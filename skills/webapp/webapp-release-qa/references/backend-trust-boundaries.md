# Backend Trust-Boundary Hardening (Postgres / Supabase)

Root-cause fix recipes for the P0/P1 classes found by `references/adversarial-testing.md`.

## One guard trigger for INSERT + UPDATE

All mutation rules for a trust-boundary table live in one function, attached `BEFORE INSERT OR UPDATE`. A GUC escape hatch lets security-definer RPCs (payment confirm, seeding as service role) bypass without weakening the rules:

```sql
create function fn_order_guard() returns trigger language plpgsql
security definer set search_path to 'public' as $$
declare v_role text; v_expected numeric;
begin
  if auth.uid() is null then return new; end if;                       -- service role
  if current_setting('app.bypass_guard', true) = 'on' then return new; end if; -- system RPC
  select role into v_role from profiles where id = auth.uid();

  if tg_op = 'INSERT' then
    if v_role in ('staff','owner') then return new; end if;
    if new.status <> 'pending' or new.payment_status <> 'unpaid' then
      raise exception 'rows start as pending and unpaid';
    end if;
    select coalesce((select sp.price from price_exceptions sp
                      where sp.customer_id = new.customer_id and sp.item_id = new.item_id),
                    (select i.price from items i where i.id = new.item_id)) into v_expected;
    if new.price is distinct from v_expected then
      raise exception 'price does not match the catalog price';
    end if;
    return new;
  end if;

  if v_role = 'owner' then return new; end if;
  if v_role = 'staff' then
    if new.payment_status is distinct from old.payment_status then
      raise exception 'payment status changes through payment only';
    end if;
    return new;
  end if;
  if new.status = old.status and new.payment_status = old.payment_status
     and new.price = old.price and new.customer_id = old.customer_id then
    return new;                                                        -- notes edit
  end if;
  if new.status = 'cancelled' and old.status = 'pending'
     and new.payment_status = old.payment_status and new.price = old.price then
    return new;                                                        -- own cancel
  end if;
  raise exception 'customers may only edit notes or cancel a pending row';
end $$;

create trigger trg_order_guard before insert or update on orders
  for each row execute function fn_order_guard();
```

Shape rules: immutability + transitions are OLD-vs-NEW — never policy `WITH CHECK` subqueries (they see only the NEW row; `col = (select p2.col from t p2 where p2.id = t.id)` self-compares to always-true). Payment flips are RPC-only (the RPC sets the bypass GUC in its own transaction, flips state atomically, notifies). One place to audit; every caller routes through it.

## Policy / privilege traps

- **Denied writes are silent**: RLS-blocked UPDATE/DELETE matching 0 rows returns `error: null` + empty result. Verify with `.select()` + row count.
- **Column `REVOKE SELECT` is a no-op under a table-level `GRANT SELECT`.** To hide columns: `REVOKE SELECT ON t FROM role;` then `GRANT SELECT (safe_cols) ON t TO role;`. `select('*')` then errors for that role → client must list safe columns explicitly; staff read a privileged view for full rows:

```sql
create view public.staff_patients as
  select * from public.patients where public.fn_my_role() in ('doctor','owner');
grant select on public.staff_patients to authenticated;
```

(Owner-rights view sees full rows; non-staff filtered to zero. Writes still hit the base table.)
- **Child-table triggers mutate parent state inside the calling transaction** — a later UPDATE's WHERE re-evaluates against the trigger's change and matches nothing. Fix statement order; instrument `not found` raises with row_count / uid / current state to see it instantly.

## Paid holds the resource

```sql
create unique index ux_order_paid_slot on orders(slot_at)
  where payment_status = 'verified' and slot_at is not null;
```

Unprovisioned rows hold nothing; payment claims the slot and a concurrent claimant gets a unique violation. Map that constraint name to friendly copy in EVERY submit path (booking AND payment screens) — never render raw Postgres text to users.
