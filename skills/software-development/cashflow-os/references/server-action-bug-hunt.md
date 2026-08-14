# Server-action bug hunt (2026-08-05, full src/features + src/lib + src/app/api sweep)

Code-level audit of every `actions.ts`, complementing `schema-drift-audit.md` (that one checks queries vs migrations; this one checks the action logic itself). Do NOT edit during the hunt — return numbered findings with file:line + severity + one-line fix.

## Method (repeat this)

1. Enumerate tables touched: `grep -rhoE "\.from\('[a-z_]+'\)" src --include=*.ts --include=*.tsx | sort | uniq -c | sort -rn` (use terminal grep — `search_files` mangles backslashes on this host).
2. Grep money paths: `toFixed|Math.round|Number(` and `/ 100|/ 12|reduce` in features.
3. Read every `actions.ts` fully (23 files, ~3500 lines — cheap), then the 8 hottest: transactions, sales, purchasing, employees, dashboard, assets, investments, reports.
4. **Verify RLS claims against `supabase/migrations/*.sql` BEFORE rating severity.** Entity-scoped policies (`EXISTS (SELECT 1 FROM entities WHERE ... user_id = auth.uid())`) mean a missing `.eq('entity_id')` on an id-only write is a SILENT 0-ROW NO-OP (returns success, nothing changed) — a MAJOR bug, not a CRITICAL leak. DB CHECKs (e.g. `invoices CHECK (total >= 0)`) backstop app math — check before calling an app-level negative-total a bug.
5. Check status transitions + filters: which queries omit `.neq('status','rejected')` while siblings have it; whether `pending` counts as real money (design decision, but must be consistent page-to-page).
6. Look for the recurring classes below — each was found in the wild in this repo.

## Recurring bug classes (all confirmed in this repo)

- **Status flip BEFORE side-effect booking, revert-on-failure → duplicates on retry.** `markPayrollPaid` (employees/actions.ts:223-262) marks the run `paid` first, then inserts one expense per line; a mid-loop failure reverts to `pending` but earlier expenses persist → retry books them twice. Fix: book side effects first, then the conditional status update.
- **Two actions implementing the same transition, one guarded one not.** `reviewTransaction` (transactions) has role+self-approval+status-pending checks; `approveTransaction`/`rejectTransaction` (business/actions.ts:68-82) have none → manager self-approval bypass. Any new approval path must reuse the guarded action.
- **Staff role `'owner'` escalation.** `current_staff_role` returns `staff.role` verbatim; `ROLES` includes `'owner'`, so a staff row with `role='owner'` gets the RLS manager lane + `canApprove`. Fix: exclude `'owner'` from the staff ROLES allowlist.
- **Status-filter drift on money sums.** Income statement (reports/actions.ts:138), health score (accounts:88), budget-vs-actual (budgets:79), TransactionList stats (allTxns, TransactionList.tsx:244) omit `.neq('status','rejected')` while dashboard/business queries have it → rejected money counts as real, and pages disagree with each other.
- **`toISOString()` month-bound drift.** `startOfMonth/endOfMonth(...).toISOString().split('T')[0]` shifts bounds a day EARLY in UTC+X (east) timezones (dashboard:21-25,60-61; purchasing:25; reports:35,157; accounts:84-85; budgets:74-75; passive-income:49). Use `format(d,'yyyy-MM-dd')`.
- **One fetch serving two windows with the narrower bound.** `monthNoSpend` (dashboard/actions.ts:41,85-93) uses `gte(weekStart)` so days 1..(Mon-1) of the month show $0. A query feeding two derived windows needs the union's min bound.
- **Unvalidated spread-inserts.** `createInvestment` (investments:35), `createAccount`/`createTransfer`/`createIOU` (accounts:17,39,54), `createGoal`/`updateGoal` (goals:27,37) spread raw client numbers — negative qty/price/balance accepted, negative portfolio value flows into assets. Use `validateAmount` everywhere money lands.
- **TOCTOU quantity updates.** `updateStock` (reports:69-73) read-then-write without `gte('quantity', qty)` → concurrent sales oversell. Same family: `recordReceipt` (purchasing:186-191) read-then-write `received_qty` without a conditional → concurrent receipts under-count.
- **Copy-into-month without idempotency or day clamping.** `copyRecurring` (reports:8-24): double-click duplicates; 31st-of-month recurring copied into a 30-day month inserts an invalid date. Guard with an already-copied check + `min(day, daysInMonth)`.
- **Money totals over FK embeds without status filter.** `getSuppliers` (suppliers:13-19) sums ALL `purchase_orders(total)` incl. cancelled/draft. Filter the embed by status.
- **Module TTL caches never invalidated on writes.** debtsCache/healthCache/entityCache/budgetCache/goalsCache/currencyCache serve stale money up to 20s after a write (revalidatePath doesn't clear them) and grow unbounded. Invalidate on the mutating action.
- **Raw DB errors to clients.** `return { error: error.message }` after insert/update leaks PostgREST detail; map to generic messages.
- **`createInvoice` discount > subtotal** → DB `CHECK (total >= 0)` rejects with a raw error message — validate `discount <= subtotal` app-side for a friendly error.
- **Cross-entity FK refs without ownership check.** `createTransaction`/`updateTransaction`/`createBudget` accept any `category_id` (sales/purchasing guard customers/suppliers) → row renders "Uncategorized", budget grouping wrong.
- **Legacy unbounded list path.** `getTransactions({})` (no cursor) returns the whole table; `getTxPage` slices client-side. Fine for stats, but it's a full-table fetch per page load.
- **Hydration:** `format(new Date(), "MMMM yyyy")` rendered in SSR'd client components (TransactionList.tsx:275, DashboardPage:84) — UTC vs local mismatch; compute post-mount.
- **`sendNotification`** lets any authed user notify arbitrary userId — restrict to own id.
- **Dead legacy helpers** with unvalidated `entityId` params (dashboard:110-225: getMonthlyStats/getNetWorth/getMonthlyTrend/...) — RLS-only gate, no current callers; delete or route through getEntity().

## Verified-clean patterns (don't re-flag)

Keyset pagination on `(date,id)` with `limit+1` lookahead + filters-ref race guard; sales/purchasing money math (round2 per line + header, DB CHECK backstop); conditional writes with `.select('id')` count probe; orphan rollback on parent+children inserts; AI route (auth + rate limit + no key leak); `validateAmount` round-trip 2dp check; forecast div guards.
