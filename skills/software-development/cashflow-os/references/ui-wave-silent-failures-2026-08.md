# Sprint-4 UI-Elevation Wave — Silent-Failure-Hunter Gate (2026-08-06)

Gate contract: `npx tsc --noEmit` + full diff read + grep for `.then(`/`await ` without `.catch`, `window.confirm/prompt` leftovers, `onCta={fetch}` retry wiring. Verdict: **REQUEST_CHANGES** (tsc errors + 2 HIGH).

## Findings (severity | file:line | issue | one-line fix)

1. **HIGH (pre-existing, gate-blocking)** | `src/features/dashboard/components/DashboardPage.tsx:172,342` | `getDashboardData` (actions.ts:107) never returns `monthNoSpend` → `setMonthNoSpend(undefined)` → `{monthNoSpend.length > 0 && <NoSpendCalendar/>}` throws TypeError → **dashboard crashes after every successful load**. tsc TS2339 ×2 on the inferred type. | Drop the dead field or add it to the action return; guard render `(monthNoSpend?.length ?? 0) > 0`.
2. **HIGH** | `src/components/layout/AppShell.tsx` NewEntityDialog.submit (~171-176) | `await m.createBusinessEntity(trimmed)` — no try/catch → rejection = unhandled + `busy` stuck TRUE ("Creating…" disabled forever, dialog unusable till reload). | `.catch(() => ({ error: "Network error" }))` + reset busy in finally (house pattern).
3. **MEDIUM** | `src/features/passive-income/components/PassiveIncomePage.tsx:52-63` | `fetchData` no try/catch → rejection = unhandled + `setLoading(false)` never runs → skeleton stuck forever; the new EmptyState Retry (`onCta={fetchData}`) can't recover this path. | try/catch/finally.
4. **MEDIUM** | `src/features/investments/components/PortfolioView.tsx:492-504` (+ `doDelete` 108-120) | Inline confirm delete: `await deleteInvestment(id)` no `.catch` → unhandled rejection, delete fails SILENTLY (no rowErr, no refetch). `doDelete` is dead code (zero callers). | Add `.catch(...)`; delete `doDelete`.
5. **MEDIUM** | `src/features/assets/components/AssetManager.tsx:107,111` | New confirm-delete wiring: `await deleteAsset/deleteDebt(id)` no `.catch` → rejection = unhandled + silent (no err, no fetch). | `.catch(() => ({ error: "Network error" }))`.
6. **MEDIUM** | `src/features/transactions/components/TransactionList.tsx:325-332` | fetchData error → full-page error view whose Retry calls `loadPage()` (**unfiltered**) — after a failed FILTER refetch, Retry silently drops active filters while badge/popover still show them applied. | Retry should call `fetchData()` (re-run failing fetch with current params) or clear filters.
7. **LOW** | `TransactionList.tsx:586-644,391-423` | Filter + More menus: no Escape-to-close (backdrop click ✓); during `updating`, CardContent `opacity-40` creates a stacking context that demotes the `fixed inset-0 z-40` backdrop below root-level elements (header) → some outside clicks won't dismiss. | Escape keydown listener; don't dim while a popover is open.
8. **LOW** | `TransactionList.tsx:103-126` | `loadedOnce` set only in `fetchData`, not `loadPage` → first filter change after mount shows the full skeleton instead of dim-update. Chained filter changes: older fetch's `finally` clears `updating` while newer is in flight (indicator cuts short — **cannot stick true**: finally always runs, error path included). | Set `loadedOnce` in loadPage; seq-id guard on `updating`.
9. **LOW** | `DashboardPage.tsx:347-350` | "Updated just now" computed at render with no timer → label freezes until next state change; `updatedAt` also null on initialData first paint (set only in applyData). | 60s interval, or always render HH:mm.
10. **INFO (pre-existing)** | `src/features/budgets/components/BudgetManager.tsx:30` | `shareTTL(getBudgetVsActual)().then(...)` no catch → widget silently never renders on rejection. | `.catch(() => setLoading(false))`.

## Verified clean (answers to the standard gate questions)

- `updating` (TransactionList): reset in `finally` on error AND success — cannot stick true. ⚠ race nuance in #8.
- Filter badge: `activeFilterCount` counts exactly the 6 FilterState fields. ✓
- `confirmId`: not reset on row unmount/refetch but harmless (matched by `t.id`); reset on success/cancel. ✓
- EmptyState error/Retry correctly wired: calendar (retry = `setMonth(new Date(month))` → new identity refires effect), inventory, loans, CashFlowChart, IncomeStatement, PortfolioView. ⚠ PassiveIncome (#3).
- Count-up keyed animation: `key={card.val}` remount = text-only 300ms CSS anim — no layout thrash. ✓
- `window.prompt` fully removed from src/ (old createEntity callers gone). ✓
- All TransactionList mutations (`handleAdd/handleReview/handleDelete`) use `.catch(() => ({error}))`. ✓
- Calendar page: full try/catch/finally + cancelled flag. ✓ (reference implementation)

## Mechanics learned

- **tsc-as-crash-finder**: TS2339 on a property of an INFERRED type (type derived from action's return literal) = the property is genuinely ABSENT from the runtime object. setState(undefined) → `.length`/`.map` in render throws. Trace inferred types to the server-action return literal before rating; pre-existing tsc errors in a wave's OWN files are gate-blocking anyway (wave touched `applyData` right next to the dead field).
- Grep the DIFF (not just the files) for `await ` lines without `.catch(` — the house pattern is `.catch(() => ({ error: "Network error" }))` on every server-action await; new async handlers must also reset busy/loading in `finally`.
- Check every `onCta={fetch}` retry target: does it (a) clear its error state first, (b) have try/catch, (c) re-run the SAME query that failed (not a different loader)?
