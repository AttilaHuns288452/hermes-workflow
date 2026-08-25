---
name: nextjs-supabase-pro-patterns
description: Pro patterns for Next.js + Supabase finance apps.
---

# Next.js + Supabase Pro Patterns

Class-level playbook distilled from CashFlow OS 2026-08-20 pro-polish pass (5 parallel tracks + Luna audit alignment). Use when a financial app feels "technically done but not pro."

## Financial spine — transactions.account_id

- Add `transactions.account_id uuid REFERENCES accounts(id) ON DELETE SET NULL` + indexes `(account_id)` and `(entity_id, account_id)`. Nullable — existing rows stay valid.
- Create `adjust_account_balance(p_entity_id uuid, p_account_id uuid, p_delta numeric) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER` — guards `entities.user_id = auth.uid()` and `FOR UPDATE` lock, `REVOKE FROM PUBLIC,anon; GRANT TO authenticated`.
- In `createTransaction`: validate `account_id` belongs to `entity_id`, insert with `account_id`, then `rpc("adjust_account_balance", {p_entity_id, p_account_id, p_delta})` where `delta = income ? +amount : -amount`. On RPC failure delete inserted row and return error. Handle `PGRST202` as "migration pending" for graceful degrade before migration applied.
- Wire optional picker + `Unassigned · assign` badge + `accountId` filter (`__unassigned__` → `is null`). Revalidate `/accounts` too.

## Budget periods — month-scoped

- `budgets.period DATE` first day of month, `DEFAULT date_trunc('month', CURRENT_DATE)::date`, backfill `COALESCE(created_at, NOW())`, `SET NOT NULL`.
- Replace `UNIQUE(entity_id, category_id)` with `UNIQUE(entity_id, category_id, period)` + `idx_budgets_entity_period`.
- Actions read `?period=YYYY-MM-01`, cache key `entity:period`, `getBudgetVsActual(period?)` returns `pace {dailyRate, projected, daysToLimit, willHit, label}`.

## Net worth — single source of truth

- `src/lib/net-worth.ts` must be `"use server"` (see Pitfall below). `getNetWorthBreakdown()` = `liquid(accounts.balance) + investments(market via getQuotes, FX-aware, cost-basis fallback) + physicalAssets(excludes "📈 Investment Portfolio" synthetic) - (debts + loansReceived)`. Expose `drift` vs snapshot and `portfolioDup` mismatch warning. Only `BalanceSheet` consumes it — dashboard no longer duplicates.

## Dashboard — progressive disclosure

- Above fold answers 3 questions: How much? What changed? What needs attention? → stat cards + single `Needs Attention` rail (red urgent / accent info dots) + `QuickEntryBar` ("180 · food" signature).
- `WeeklySpend + 4 charts + Net Worth` behind persisted `details/summary` disclosure (closed mobile, open desktop via `matchMedia`, `localStorage` key). `QuickAddForm` demoted to `+ Add` toggle. All amounts `tabular-nums`.

## IA — PageHeader sweep

- Route owns `<PageHeader eyebrow title subtitle>` — feature is `space-y-4` content-only, no `p-4 md:p-6` duplication. 11 routes canonical.
- 4-group nav `Overview / Money / Wealth / Setup (+Business)` with 11px sub-links (`Budgets · Goals`, `Assets · Loans · Sheet`, `Statements · Analytics`, `List · Month`) visible when expanded, `aria-current="page"` on parent+sub, collapsed tooltip joins sub labels. `CommandPalette` flatMaps `item.sub`.

## Pitfalls

- **Client bundling `next/headers`**: shared `lib/entity.ts` imports `next/headers`. Any helper importing `entity.ts` that a client component imports will poison the browser bundle (`You're importing a module that depends on "next/headers"`). Fix: mark helper `"use server"` at file top — turns it into Server Action boundary. `tsc --noEmit` stays green while `next build` fails is the symptom.
- **Vercel cwd**: `npx --prefix <project> vercel deploy` prompts "You are deploying your home directory." Use `npx vercel deploy --prod --cwd . --yes` from inside the project instead.
- **Supabase without Docker/link**: `supabase status` → `Not linked` + `docker: command not found` is fine. Use Dashboard SQL Editor → paste migration file verbatim → Run. Verify via `information_schema.columns` and `pg_proc`.

## References

- `references/cashflow-pro-polish-2026-08-20.md` — full session transcript + migration SQL + deploy logs
- `references/vercel-cwd-and-next-headers-fix.md` — minimal repros for the two build pitfalls above
