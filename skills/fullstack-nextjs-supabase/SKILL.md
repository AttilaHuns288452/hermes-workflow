---
name: fullstack-nextjs-supabase
description: Patterns for building fullstack Next.js + Supabase apps — entity-based ownership, shared getEntity(), structured errors, RLS subquery pattern, DB triggers vs app code, shadcn manual components, loading skeletons, audit trail triggers, ECC parallel dispatch.
category: software-development
triggers:
  - "build a supabase app"
  - "nextjs supabase fullstack"
  - "create a supabase project"
  - "RLS policies"
  - "supabase schema migration"
  - "server actions supabase"
  - "shadcn supabase"
---

# Fullstack Next.js + Supabase Patterns

Proven patterns from shipping a complete personal finance app (CashFlow OS) with Supabase + Next.js 16 + Tailwind + shadcn/ui.

## Entity-based ownership

When the app may need multiple tenants/businesses per user in the future, scope all data to an `entity_id`, never `user_id` directly. Every user gets a `personal` entity auto-created on signup. Child tables (categories, transactions, assets, debts) reference `entity_id` with `ON DELETE CASCADE`. Cost in v1: one extra JOIN per query. Benefit: no destructive migration when business mode ships.

## Shared getEntity() — extract, don't duplicate

If 3+ feature action files duplicate the same `auth.getUser()` + `entities.select()` pattern, extract ONE shared `getEntity()` to `src/lib/entity.ts`. Return `{ supabase, entityId } | { error: string }` — structured, never throws. This one function eliminates 17+ uncaught error sites across the codebase.

```ts
export async function getEntity(): Promise<EntityResult> {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return { error: "Not authenticated" };
  const { data: entity } = await supabase.from("entities").select("id").eq("user_id", user.id).eq("type", "personal").single();
  if (!entity) return { error: "No personal entity found" };
  return { supabase, entityId: entity.id };
}
```

## Structured errors — never raw throws

Every server action returns `{ error: string } | { success: true } | data[]`. Never `throw new Error()` — client handlers don't catch it. Avoid `redirect()` in server actions called imperatively — it throws NEXT_REDIRECT. Return success and let client `router.push`.

## RLS: entity subquery pattern

Foreign-key tables don't have `user_id`. RLS policies use a consistent subquery:
```sql
EXISTS (SELECT 1 FROM entities WHERE entities.id = <table>.entity_id AND entities.user_id = auth.uid())
```
Add `CREATE INDEX idx_entities_user ON entities(user_id)` for performance.

## DB triggers vs app code

Postgres triggers on `auth.users` are fragile on Supabase (SECURITY DEFINER, auth schema permissions, migration splitting). Ponytail: handle entity + category creation in the `signUp` server action. One extra insert, zero trigger maintenance. Drop the trigger if it exists — it causes 500 errors on signup.

## shadcn/ui on Windows

`npx shadcn@latest add` frequently fails with npm cache errors (`ENOTEMPTY`). Write shadcn components manually: `forwardRef` + `cn()` + Tailwind classes. Each component is 10-50 lines. Copy from shadcn's source or write from memory. Never block a build on the CLI.

## Loading skeletons

One `loading.tsx` per route with `animate-pulse` divs. Next.js auto-shows during navigation. No dependencies. Immediate UX upgrade for slow Supabase queries. Cost: 10 lines per route.

## Postgres triggers for audit trail

```sql
CREATE FUNCTION log_transaction_change() RETURNS TRIGGER AS $$
BEGIN
  IF TG_OP = 'UPDATE' THEN INSERT INTO transactions_history (...) VALUES (OLD.*); RETURN NEW;
  ELSIF TG_OP = 'DELETE' THEN INSERT INTO transactions_history (...) VALUES (OLD.*); RETURN OLD;
  END IF; RETURN NULL;
END; $$ LANGUAGE plpgsql;

CREATE TRIGGER trg_transactions_history BEFORE UPDATE OR DELETE ON transactions FOR EACH ROW EXECUTE FUNCTION log_transaction_change();
```
Zero app-code impact. Add early — backfilling audit data is impossible.

## updated_at auto-trigger

```sql
CREATE FUNCTION update_updated_at() RETURNS TRIGGER AS $$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END; $$ LANGUAGE plpgsql;
```
Attach to every table with `updated_at` column. One function, reused everywhere.

## ECC parallel dispatch

Before merging, dispatch 2-3 ECC agents in parallel: `database-reviewer` for schema, `silent-failure-hunter` for errors, `code-reviewer` for quality. See `ecc-bridge` skill reference `references/parallel-ecc-dispatch.md`.

## Multi-currency: Intl.NumberFormat (stdlib)

Never hardcode currency symbols (`$`, `₱`, `€`). Use one shared function:

```ts
export function formatCurrency(amount: number, currency = "USD") {
  return new Intl.NumberFormat("en-US", { style: "currency", currency }).format(amount);
}

export function currencySymbol(currency = "USD") {
  return new Intl.NumberFormat("en-US", { style: "currency", currency, minimumFractionDigits: 0 })
    .formatToParts(0).find(p => p.type === "currency")?.value || "$";
}
```

Client components get the currency by calling `getCurrencySetting()` (server action) in a `useEffect` and storing in state:

```tsx
const [currency, setCurrency] = useState("USD");
useEffect(() => { getCurrencySetting().then(setCurrency); }, []);
// JSX: {formatCurrency(amount, currency)}
```

Server actions that return text containing amounts (e.g., activity timeline `text` field) must also resolve the entity's currency before building the string — use the entity lookup result, not a hardcoded `$`.

Grep for `\$[0-9]` in `.tsx` files after every build to catch hardcoded symbols that slipped through.

See `references/cashflow-os-audit-checklist.md` for the full grep-based regression audit (currency, Tailwind JIT, entity bypass, duplicates, localStorage, dark mode, missing form fields).

## Pitfalls

- **redirect() in server actions called imperatively**: `redirect()` throws NEXT_REDIRECT. If the form uses `onSubmit` + `preventDefault` instead of form `action`, the redirect is an unhandled rejection. Return `{ success: true }` and use `router.push` instead.
- **Multi-statement SQL via Supabase API**: The `/database/query` endpoint runs ONE statement. Split multi-statement SQL before sending. `DO $$ BEGIN ... END $$` blocks work for single logical operations.
- **Policy idempotency**: `CREATE POLICY IF NOT EXISTS` is not valid PostgreSQL. Use `DO $$ BEGIN CREATE POLICY ... EXCEPTION WHEN duplicate_object THEN NULL; END $$`.
- **Auth schema permissions**: Triggers on `auth.users` require SECURITY DEFINER and may fail silently on signup. Avoid them — handle entity creation in app code.
- **Migration splitting corrupts functions**: When splitting SQL by `;`, `$$`-quoted function bodies with internal semicolons get broken. Use `re.split(r';(?=(?:(?!\$\$).)*$)', sql, re.DOTALL)` or send functions as single statements.
- **Dynamic Tailwind class names are JIT-purged**: `text-${card.color}-600` or `text-red-${shade}-400` will NOT work in production builds. Tailwind's JIT scanner only sees complete class strings in the source. The fix is a static mapping object: `const colorClasses = { emerald: "text-emerald-600 dark:text-emerald-400", red: "text-red-600 dark:text-red-400" }` then `colorClasses[card.color]`. Always check for template-literal class names in JSX — they are the #1 cause of "styles worked in dev but broke in prod."
- **Entity switching bypass**: When you have a shared `getEntity()` that reads a cookie, new actions that manually query `entities` with `user_id` and `type:'personal'` bypass the cookie's selected entity. Dashboard always shows personal data even when a business entity is selected. Fix: every server action — including "dashboard data" and "CSV export" — must call `getEntity()` and use its `entityId`. Never manually query `entities.select().eq("user_id", user.id).eq("type", "personal")` in server actions; that hardcodes personal entity.
