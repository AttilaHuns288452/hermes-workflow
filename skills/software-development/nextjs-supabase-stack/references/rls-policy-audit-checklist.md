# RLS policy audit checklist (approval/workflow schemas)

Run on every Supabase audit where migrations define staff roles, pending/approved statuses, or SECURITY DEFINER helpers. Ground truth order: read `supabase/migrations/*.sql` FIRST, then app code — severity ratings depend on what RLS actually enforces (an entity-scoped policy turns a missing `.eq('entity_id')` into a silent no-op, not a leak).

## The six checks

1. **UPDATE lanes: audit `WITH CHECK`, not just `USING`.**
   `USING` gates WHICH rows; `WITH CHECK` gates the NEW row. A policy like `FOR UPDATE USING (submitted_by = mine AND status='pending')` with no WITH CHECK lets the submitter flip their own row to `approved` via direct API — the RLS-level self-approval bypass. Every approval/submitter lane needs its new-row status constrained: `WITH CHECK (status = 'pending')` or `NEW.status IN ('pending','rejected')`.

2. **INSERT lanes must pin workflow status themselves.**
   `FOR INSERT WITH CHECK (member_of_entity)` lets staff insert `status='approved'` rows. A migration comment "the app layer forces status='pending'" is NOT a guard — RLS is the backstop and must stand alone. Fix: `WITH CHECK (status = 'pending' OR current_staff_role(entity_id) = 'owner')`.

3. **SECURITY DEFINER functions = RLS bypasses; verify auth inside the body.**
   Default `EXECUTE` is granted to PUBLIC, so any authenticated user can call the RPC directly — an app wrapper that forces `p_user_id: user.id` protects only that wrapper. Classic finding: `notify_user(p_user_id, ...)` inserting into any user's inbox (spam/phishing). 🚨 **THE NULL TRAP: `auth.uid()` is NULL for anonymous callers, and `NULL AND x` is NULL, which `IF` treats as FALSE — so a guard like `IF p_user_id <> auth.uid() AND NOT EXISTS(...) THEN RAISE` fails OPEN for anon callers** (the raise is skipped, the SECURITY DEFINER insert proceeds into any inbox). Every auth.uid() boolean guard must fail closed on NULL:
   ```sql
   IF auth.uid() IS NULL OR (p_user_id <> auth.uid() AND NOT EXISTS (
     SELECT 1 FROM entities WHERE id = p_entity_id AND user_id = auth.uid()
   )) THEN RAISE EXCEPTION 'not allowed'; END IF;
   ```
   Also check the guard's SCOPE: entity-ownership (`caller owns p_entity_id`) still lets any user who owns ANY entity notify ANY user in the system — if that matters, require the recipient to be the entity owner or a staff member of `p_entity_id`.
   (Contrast: audit TRIGGER functions are fixed by REVOKE + TG_TABLE guard + SET search_path — see nextjs-supabase-stack SKILL.md.)

4. **Deletes must respect the same transition map as status updates.**
   `deleteInvoice`/`deletePO` with no status guard erase `paid`/`received` records. A transition map enforced only on the status-update action is bypassed via delete. Guard: reject unless `status = 'draft'` (or whatever the map allows).

5. **Idempotency = UNIQUE natural key, not a pre-check.**
   Read-then-insert "already exists?" checks race. Add `UNIQUE(entity_id, period_start, period_end)`-style keys and catch 23505 in the action (retry or friendly error). Also audit rollback/cleanup paths: deleting side-effect rows "by description" can wipe a CONCURRENT winner's rows — payroll loser of a conditional status flip deletes the winner's booked expenses, leaving a `paid` run with no expense. Clean up by run/row linkage instead. **Dedupe direction matters:** `DELETE ... WHERE a.id > b.id` keeps the OLDEST row per natural key — if the oldest is a stale `pending` retry and a newer run was already approved/paid, the delete removes paid history (and cascades its child lines). Prefer keeping an approved/paid row over a pending stray.

6. **Policy-pair completeness + write-on-read sweeps.**
   - Every owner-full/staff-read pair on a parent table needs the staff-read policy on its children (lines join through the parent), and flag tables that only got the owner policy (e.g. `payments`). Grep each table for its policy pair.
   - Lazy sweeps inside GETs (mark past-due invoices `overdue` on list load) hit RLS-blocked UPDATEs for restricted roles; the ignored error = stale data. Check the error or gate by role.

7. **After tightening an INSERT/UPDATE policy, re-check the APP's status derivation.**
   A migration that restricts statuses (e.g. `INSERT ... status='pending'` unless owner) can contradict app logic that still derives `'approved'` for managers (`canApprove(role) ? 'approved' : 'pending'`) → every manager create fails at runtime with an RLS violation, not a leak. Grep the actions for the status derivation (search `canApprove`/`status:` in the file the migration's table feeds) and align it with the policy (`role === 'owner'`), or extend the policy deliberately. Stricter-than-app is safe but broken — it must be one of the review's numbered findings either way.

## Supporting app-code checks (same pass)

- Duplicate CRUD paths drift: two actions for the same entity, one with a role/status whitelist and one without (spread-insert of client `role` → `'owner'` staff row → manager lane via `current_staff_role`). Grep for sibling creators before trusting one action's guard.
- Money sums need status filters on FK embeds AND aggregates (billed/outstanding exclude draft/void; totals exclude cancelled; revenue = paid only).
- Server-derived workflow fields (status/submitted_by computed from resolved role, never client-passed) — verify even when the client UI looks safe.
- Stub actions returning `{ ok: true }` with no side effect make UIs lie (e.g. "Reminded" button) — flag as LOW.

## Verified-clean patterns (don't re-flag)

Conditional writes with `.eq('status','pending').select('id')` count-probes · explicit enum-validated transition maps · cross-entity FK pre-checks (`select().eq('id', x).eq('entity_id', entityId)`) · orphan rollback on parent+children inserts · round2 on every money line + DB CHECK backstop · status-filtered summary queries.
