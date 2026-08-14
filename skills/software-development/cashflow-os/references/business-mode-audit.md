# Business-mode audit (2026-08-06) — RLS-layer + ERP cluster findings

AUDIT-ONLY wave over `src/features/{business,staff,customers,suppliers,employees,sales,purchasing,inventory,automation,notifications}` + `src/app/<same>` + all migrations. Verdict: **approve with fixes** — entity scoping, server-side money math, transition maps, status-filtered aggregates all solid; the failures concentrate in RLS write-lanes and payroll/notification idempotency.

## New audit checks this wave proved out (add to every repeat)

1. **UPDATE policies: check `WITH CHECK`, not just `USING`.** `USING` gates WHICH rows; `WITH CHECK` gates the NEW row. Missing WITH CHECK on an approval lane = direct-API self-approval. 011 "txn edit own pending for staff" (`submitted_by = mine AND status='pending'` USING only) → submitter flips own row to `approved`. Fix: `WITH CHECK (status = 'pending')` (or restrict to `pending|rejected`).
2. **INSERT lanes must force workflow status themselves.** 011 "txn insert for staff" (`current_staff_role IS NOT NULL`) lets staff insert `status='approved'` rows. A migration comment "the app layer forces status='pending'" is NOT a guard — RLS is the stated backstop and must stand alone. Fix: `WITH CHECK (status = 'pending' OR current_staff_role(entity_id) = 'owner')`.
3. **SECURITY DEFINER RPCs verify auth INSIDE the body.** `notify_user` (017) — definer, default PUBLIC EXECUTE, zero auth check — any logged-in user inserts notifications into ANY user's inbox (spam/phishing vector). App wrapper `sendNotification` forcing `user.id` (notifications/actions.ts:77) protects only the wrapper, not the RPC. Fix: `IF p_user_id <> auth.uid() AND NOT EXISTS (SELECT 1 FROM entities WHERE id = p_entity_id AND user_id = auth.uid()) THEN RAISE EXCEPTION; END IF`.
4. **Deletes must respect the same transition map as status updates.** `deleteInvoice` (sales/actions.ts:186) / `deletePO` (purchasing/actions.ts:237) have no status guard → paid/received records erased. Fix: reject unless `status = 'draft'`.
5. **Payroll run creation idempotency.** `createPayrollRun` (employees/actions.ts:153) has no duplicate-period check AND `payroll_runs` has no `UNIQUE(entity_id, period_start, period_end)` (013) → retry/double-click = two pending runs = double pay. The markPayrollPaid conditional flip only protects the PAID transition, not run creation. Fix: unique constraint + 23505 catch, or pre-check.
6. **Rollback-by-description is a race.** markPayrollPaid (employees/actions.ts:255-287) books expenses then flips status conditionally; the LOSER deletes `transactions WHERE description = ...` — which also deletes the WINNER's freshly booked expenses (run stays paid, no expense). Fix: delete by run linkage (add run_id to the expense) or scope cleanup to rows from this attempt.
7. **Duplicate CRUD paths drift.** `business/actions.ts:48 createStaffMember` spreads client `role` with NO whitelist while `employees/actions.ts` has `ROLES = ['manager','accountant','staff']` → owner-escalation via `role='owner'` staff row (018 normalizes legacy rows only). Fix: whitelist in the business copy too (or delete it — no UI caller). Also EmployeesPage.tsx:375 offers "Owner" in the role Select, which always fails server-side — a UX trap.
8. **Policy-pair completeness on child tables.** Every 012/013 parent has owner-full + staff-read; `payments` (012:180-184) has ONLY the owner policy — latent staff-blind spot. Grep each table for its pair.
9. **Write-on-read sweeps.** The overdue flip inside `getInvoices` (sales/actions.ts:44-49) runs on every list load; staff's RLS blocks the UPDATE and the error is ignored → stale data, silent. Check the error or gate by role.

## Findings table (condensed)

| Sev | File:line | Issue | One-line fix |
|---|---|---|---|
| CRITICAL | 011_staff_rls.sql:58-65 | submitter UPDATE lane, no WITH CHECK → self-approval via API | add `WITH CHECK (status='pending')` |
| CRITICAL | 011_staff_rls.sql:43-45 | staff INSERT lane, no status force → pre-approved rows | `WITH CHECK (status='pending' OR role='owner')` |
| HIGH | 017_notifications.sql:23-30 | notify_user SECURITY DEFINER, no auth check → cross-user spam | auth.uid()/ownership check in body |
| HIGH | business/actions.ts:48 | createStaffMember no role whitelist → 'owner' staff row → manager lane | whitelist roles like employees/actions.ts:12 |
| HIGH | employees/actions.ts:153-179 | createPayrollRun dup on retry (no unique period key) | UNIQUE(entity_id, period_start, period_end) + 23505 |
| MED | sales/actions.ts:186 / purchasing/actions.ts:237 | delete bypasses status map (paid/received erasable) | draft-only delete guard |
| MED | employees/actions.ts:255-287 | loser cleanup deletes by description → wipes winner's expenses | delete by run linkage |
| MED | EmployeesPage.tsx:375 | "Owner" role option always fails server-side | remove SelectItem |
| MED | 012_erp_modules.sql:180-184 | payments lacks staff-read policy | add staff view via current_staff_role |
| LOW | sales/actions.ts:44-49 | overdue sweep error ignored for staff | check/guard by role |
| LOW | automation/actions.ts:147 | markInvoiceReminded stub returns ok — UI lies "Reminded" | wire or remove |
| LOW | business/actions.ts:112-113 | month revenue includes status='pending' (documented drift) | exclude pending from revenue |
| LOW | automation/actions.ts:91-96 | notify dedupe read-then-write → dup on concurrent loads | UNIQUE(user_id, kind, title) upsert |
| LOW | reports/actions.ts:90-104 | updateStock + movement insert non-atomic | RPC or movement-first |

## Design-language note

Frozen-design violations (hardcoded Tailwind palette classes + `dark:` variants + badge/pill spans) found in inventory/page.tsx:16-19,117-118,140-144; SalesPage.tsx:16-18,87,152; PurchasingPage.tsx:36-38; EmployeesPage.tsx:20-23,223,235; AutomationPage.tsx:214,238-239; CustomersPage.tsx:78,97; SuppliersPage.tsx:82. BusinessDashboard + NotificationsPage are var-backed and clean. Grep gate: `text-(green|red|orange|blue|amber|violet)-[0-9]+` and `dark:` in feature components.

## Verified-clean (don't re-flag)

- getEntity() on every action; cross-entity FK guards (sales:83-89, purchasing:61-67)
- Invoice/PO transition maps explicit + enum-validated; conditional writes `.eq(status).select('id')` everywhere
- createTransaction status/submitted_by server-derived; reviewTransaction self-approval + role gates (delegated correctly from business/actions approve/reject)
- Money sums status-filtered: customers billed/outstanding (sent|paid|overdue), suppliers total_ordered (ordered|partial|received), sales revenue=paid only, purchasing monthSpend=received only
- recordReceipt conditional update with `received_qty` optimistic guard; markPOReceived idempotent; receiveIncoming idempotent (incoming_qty=0 gate)
- Loading/empty/error states on every page; no unused imports in scope

## Host quirks hit this wave

- `src/features/business/actions.ts` is CRLF — read_file flags it "Binary file" and refuses. Read with: `python -c "print('\n'.join(f'{i}|{l}' for i,l in enumerate(open('f',encoding='utf-8').read().splitlines(),1)))"`.
- Inventory feature's server actions live OUTSIDE the inventory dir: `src/features/reports/actions.ts` (getInventory/createInventoryItem/updateStock/...) — scope checklists must grep callers to find the real home of an in-scope page's actions.
- `search_files` content-grep works fine on this repo; ripgrep backslash-regex mangling only bites on `\.` patterns — use character classes.
