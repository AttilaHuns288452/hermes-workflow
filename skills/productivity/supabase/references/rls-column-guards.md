# Column-level guard: protecting specific columns when RLS can't

RLS is row-level. It can decide WHICH rows a role may update, but it cannot say
"this role may update this row but not THIS column." When a role is allowed to
touch a row yet must not change sensitive columns outside a sanctioned workflow
(financial fields like `payment_status` / `final_fee` / `price`, or a status /
ownership column), a row policy is the wrong tool. Use a BEFORE UPDATE trigger
that whitelists the change path.

## Recipe

The SECURITY DEFINER RPC that legitimately mutates those columns sets a
transaction-local bypass flag right before its UPDATE; the trigger allows the
change only when the actor is the privileged role OR a flag is set.

```sql
create or replace function fn_t_financial_guard() returns trigger
language plpgsql security definer set search_path to public as $$
begin
  -- inspect ONLY the protected columns so unrelated updates are untouched
  if (new.payment_status is distinct from old.payment_status)
     or (new.final_fee is distinct from old.final_fee)
     or (new.price is distinct from old.price) then
    if fn_my_role() is distinct from 'owner'
       and coalesce(current_setting('app.completion_rpc', true), '') is distinct from 'on'
       and coalesce(current_setting('app.bypass_guard', true), '') is distinct from 'on' then
      raise exception 'payment and fee fields change only through the payment or completion workflow';
    end if;
  end if;
  return new;
end $$;
drop trigger if exists trg_t_financial_guard on t;
create trigger trg_t_financial_guard before update on t
  for each row execute function fn_t_financial_guard();
revoke all on function fn_t_financial_guard() from public, anon;
```

## Rules

- The owning RPC must `set_config('app.<flag>','on', true)` (transaction-local)
  immediately before its own UPDATE; the trigger reads it via
  `current_setting(..., true)`. Every legitimate write path (completion RPC,
  payment-settle RPC, owner direct edit) must be covered — a path that updates the
  column WITHOUT setting a flag will start failing the moment the guard lands, so
  enumerate the writers before deploying.
- Compare the protected columns with `IS DISTINCT FROM` and touch ONLY those, so
  reschedules / notes / status transitions through RPCs keep working.
- Fail closed: deny when the role is not the privileged one AND no flag is set.
- Keep the trigger additive + reversible (`drop trigger if exists`); it is the
column-level layer that RLS cannot provide, and it composes with (does not replace)
row policies.
- Verify it with the behavioral guard test in `live-database-access.md` (attempt the
change as the restricted role and expect a reject; confirm the sanctioned RPC still
succeeds) — the trigger is only as good as the live behavioral check.
