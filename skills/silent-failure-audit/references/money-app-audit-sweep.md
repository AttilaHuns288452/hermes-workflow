# Money/security app audit sweep — proven checklists (CashFlow OS sprint, Aug 2026)

Two read-only agents, run in parallel, on `git diff <base>..HEAD` or the whole feature tree. 27 findings → 27 fixes across ~20 build/deploy cycles.

## Agent 1 — code-level (money/security/state)
- Money math: round2 every line AND header total (1.335×2 ≠ 2.67); div-by-zero on percentages/ratios/runways; unvalidated client numbers spread into inserts (validateAmount before write).
- Write scoping: every update/delete needs `.eq('entity_id', entityId)` + `.select('id')` row-count check. A foreign id with RLS = silent 0-row "success". ~20 actions had this gap.
- TOCTOU races: read-then-write without conditional. Fix pattern: conditional WHERE evaluated at update time — sale: `.gte('quantity', qty)`, purchase: `.eq('quantity', readValue)`, receipt: `.eq('received_qty', readValue)`; check row count, return "changed — try again" on 0.
- Status filters on money sums: `.neq('status','rejected')` on EVERY query that sums money (P&L, health score, budget-vs-actual, trends, page stats). Rejected txns counted as real money in 5+ places.
- Hydration: server-UTC `new Date()` vs client-local "today" — pass client date into server actions (`getDashboardData(today?: string)`, anchor all date math on it).
- Privilege escalation: staff role 'owner' un-creatable (real owners detected via entities.user_id); normalize legacy rows (migration).
- Dead code: grep callers before deleting; keep what forecast/other actions import.

## Agent 2 — data/schema-level
- Every `.from('table')` vs migration columns — schema reality beats code comments (a stale comment saying "no yield column" shipped pre-015 logic that zeroed real data; the enriched action already returned the field).
- Embed/join columns vs declared FKs; RPC arg names vs function signature (mismatch = 42883).
- Status-enum CHECK drift: nothing ever writes 'overdue' → lazy sweep on read (one UPDATE flipping past-due rows, self-healing, no cron).
- TTL caches never invalidated on writes → stale money displays up to 20-60s; `cache.delete(key)` after mutating actions.
- copyRecurring-style duplication: idempotency guard (skip rows already booked this month) + clamp day to days-in-month (no Feb 31 invalid DATE).

## Fix patterns that stuck
- **Book-then-flip**: create ALL child rows first, flip parent status LAST with conditional update; on any failure delete the children you created. Flip-first-then-create double-books on retry (payroll CRITICAL).
- **Delegate to the guarded function**: a bypass copy (approve/reject) → delete it, route callers through the shared guarded action. One guard, all callers.
- **Patch-tool redaction false positive**: display layer shows `apiKey: ***` for valid `apiKey: aiRow.api_key` lines — tsc exit 0 proves the file is fine. Verify with char-code decode, not visual read. This fooled BOTH a reviewer and the parent once.
