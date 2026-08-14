# Core Finance Cluster Audit — 2026-08-06

AUDIT-ONLY wave over `src/features/{dashboard,transactions,categories,accounts,assets,budgets,goals,loans}` + `src/app/{...same...,calendar}` + `transactions/export.ts`. Verdict: FAIL — no CRITICAL, 6 HIGH, ~30 MED/LOW. Dominant systemic classes: mutation-blind TTL caches and silent error swallowing in mutation handlers; cluster-wide design drift.

## HIGH findings (fix first)

| File:line | Issue | Fix |
|---|---|---|
| dashboard/actions.ts:29-40 | `getDashboardData` destructures `{ data }` with no error check → failed query = zero-filled dashboard + renders the "Welcome 👋" onboarding card (fake empty) | return `null` on query error → page shows error+Retry |
| app/calendar/page.tsx:25 | `new Date(t.date).getDate()` = UTC midnight → UTC− users see every txn in the previous day's cell; day-1 txns invisible | `parseISO(t.date).getDate()` |
| app/calendar/page.tsx:16-17 | `startOfMonth(month).toISOString().split('T')[0]` → UTC+X users get yesterday as the from-bound (Aug grid includes Jul 31) | `format(month,'yyyy-MM-01')` / `format(endOfMonth(month),'yyyy-MM-dd')` |
| goals/components/GoalsPage.tsx:40 | `current + amt` without round2 → float noise trips updateGoal's ≤2-decimals round-trip check; contribution errors silently swallowed (no `r.error` check) | `round2(current + amt)`; check `r.error` |
| budgets/actions.ts:79-107 | `budgetCache` (20s) invalidated only by budget writes — transaction writes leave budget-vs-actual stale on every page | exported `invalidateBudgetCache()` called from transactions/actions.ts writes |
| accounts/actions.ts:126-156 | `healthCache` (20s) invalidated only by account/IOU/transfer writes — Health Score stale after txn add/delete | same pattern |

## Class lessons (new this round)

- **Cross-module TTL blindness:** module-scoped `Map` caches can only be invalidated by code in the SAME module. healthCache/budgetCache live in accounts/actions.ts + budgets/actions.ts but are driven by transaction data written in transactions/actions.ts. Audit: for every TTL cache, list its writers and check each writer module can reach the cache.
- **round2 before round-trip validators:** `validateAmount` / the goals `current_amount` check reject any value where `Math.round(x*100)/100 !== x`. Client arithmetic (`a + b`, `a - b`) produces float noise → server rejects legit cent amounts. Round client-side before sending.
- **Getters returning `[]` on error produce fake-empty pages:** getTxPage/getTransactions/`getCategories` swallow query errors and return `[]`; the client can't distinguish "no data" from "fetch failed" → "No transactions yet" rendered on failure. Error must flow as `{ error }` to the page error state.
- **Never-throw contract:** grep `throw new Error` in actions.ts — getLoans was the only violator (page happens to try/catch it, but any future caller gets an unhandled rejection).
- **Design-drift greps (all found):** `text-[10px]` (13 hits — freeze allows only `text-[11px]`/`tracking-[0.06em]`); `text-red-500`/`text-green-600`/`text-emerald-500`/`dark:text-*` palette classes; raw hex `text-[#c2410c]` (var `--orange` already IS #c2410c); `bg-gradient-to-br` (emergency-fund card); `rounded-full` pills + `bg-green-soft text-green` icon chips (explicitly banned pattern); `bg-muted/30` strips (should be `border bg-card`); hardcoded `$` money instead of `formatCurrency` with fetched currency setting; CardTitle `<div>` (use h2 CardHeading like DashboardPage/charts); `Badge` components (frozen: no badges).

## Clean-verified (no findings)

Entity-scoping via getEntity on all writes · keyset `(date,id)` DESC + `.or()` + `limit(size+1)` · `.neq('status','rejected')` on all money sums · status writes inside CHECKs (loans outstanding|paid, txns approved|pending|rejected) · hooks before early returns everywhere · stale-response filtersRef guard in TransactionList · import idempotency (migration 020 unique index + 10k dedupe + batch errors) · in-flight guards + aria-live/role=alert in QuickAdd/ImportDialog/ExportCSV · migration 008 is the ground truth for transactions.status/submitted_by (grep migrations before flagging).

## Notes

- `round2` exists only in purchasing/sales actions — core cluster sums use raw reduces (display noise only; formatCurrency rounds). Grep the helper's actual home before citing it.
- `search_files` (rg) fails on Windows backslash paths (`IO error for operation on .../migrations`) — use forward-slash paths or terminal `grep -rn`.
