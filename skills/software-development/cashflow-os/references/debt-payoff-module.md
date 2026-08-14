# Debt payoff module

Built 2026-08-04 (commit 36ee863). Spreadsheet "Debt Tracker" tab tracks STARTING DEBT / DEBT PAID SO FAR / DEBT REMAINING — the product answers "when am I free?" via a payoff projection.

## Schema reality

`debts` = `id, entity_id, name, amount DECIMAL(12,2), updated_at` — **NO apr, NO min_payment, NO interest columns** (verified in `supabase/migrations/001_schema.sql`). UI only ever had name + amount (`AddDebtDialog` posts `{name, amount}`).

## Server action: getDebtPayoff() — src/features/assets/actions.ts

- Returns `{ debts: PayoffDebt[], projection: PayoffProjection | null } | { error }`; entity-scoped via `getEntity()`, direct supabase query (does NOT reuse the getDebts TTL cache).
- `PayoffDebt`: `{ name, balance, apr: null, minPayment: null, monthsToFree, payoffDate, interestPaid }` — payoffDate formatted server-side "Mar 2027" (`Intl.DateTimeFormat` month+year).
- Projection = LAST debt paid: `monthsToFree = max(...)`, `payoffDate` = that debt's date, `totalInterest` = sum of interestPaid. Any debt hitting the 600-month cap → whole projection null (component shows "Over 50 years").
- No debts → `{ debts: [], projection: null }` (component renders "No debts — nothing to simulate 🎉").

## Amortization (per debt, server-side loop)

- `apr`/`minPayment` columns don't exist → defaults: 0% APR, min payment = `balance/24` monthly; `payment = min(balance+interest, max(balance/24, interest+100))`.
- The $100 payment floor dominates at low balances: $10k @ 0% → 58 months, NOT 24 (floor kicks in once balance < $2.4k). This is per spec, not a bug.
- Loop cap 600 months (50y) → `monthsToFree: null`. Always terminates (payment ≥ balance/24 > 0).
- Sanity check pattern: `node -e` one-liner replicating the loop (10k→58, 500→5, 1e9→329). Re-run when the formula changes.

## Component: DebtPayoffSimulator.tsx (src/features/assets/components/)

- `'use client'`; fetches `getDebtPayoff()` + `getCurrencySetting()`; states data/currency/loading/error.
- Card: mono eyebrow "Forecast · Debt payoff", `font-display` title, per-debt row (name, balance, "Free by <date>" / "Over 50 years", interest contribution), totals row (debt-free date, "N months to go", total interest) — amounts in `font-mono tabular-nums`.
- Loading skeleton / error+Retry / empty state all present (app quality bar).
- Mounted in `AssetManager.tsx` debts `TabsContent` below `DebtTable`, wrapped in `space-y-4`, with `key={debts.length}` so the projection remounts/refetches on add/delete.

## TS pitfall

`projection?.totalInterest ?? null` — the optional chain yields `number | null | undefined`; without `?? null`, the `=== null` ternary does NOT narrow away `undefined` → tsc TS2345. Apply `?? null` to every optional-chained numeric before null-checking.
