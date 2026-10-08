# Backend Attack Probes (Supabase / PostgREST)

Probe semantics first — a wrong verdict wastes more time than a missed bug.

## Verdict semantics

- **Judge writes by rows affected + read-back, never `error` alone.** RLS-denied
  UPDATE/DELETE returns `error: null` with `data: []`; only triggers and
  constraints raise. Always follow a probe with a select-back of the row.
- **`.single()` returns `data: null` on 0 OR 2+ rows.** Signup triggers + manual
  fixture inserts both create rows → fixture lookups silently null. Use
  `.limit(1)` and assert the length.
- **A trigger can mutate the row between your statements inside one function/
  transaction.** A later `WHERE payment_status = 'unpaid'` then matches 0 rows
  even though the row existed moments earlier. Diagnose with
  `GET DIAGNOSTICS` + `raise exception` carrying the row's current state.
- **Multi-statement SQL via a management API returns only the LAST result.**
  Run integrity queries one statement per call.
- `pg_get_functionidentityarguments()` doesn't exist on older PG — use
  `proargtypes::regtype[]` from `pg_proc` for signature checks.
- PostgREST filters don't accept subqueries in `not-in` — do the set-diff
  client-side.

## Column privacy

- `REVOKE SELECT (col) ON t FROM role` is a **no-op while a table-level SELECT
  grant exists** (Supabase grants table-level to `authenticated` by default).
  Correct shape: `REVOKE SELECT ON t FROM authenticated, anon;` then
  `GRANT SELECT (allowlist...) ON t TO authenticated;`.
- After an allowlist, `select('*')` errors for EVERY role lacking the columns
  (including staff) — audit every `select('*')` caller: patient-facing queries
  list safe columns explicitly; staff read a `security definer`/owner view
  filtered by `fn_my_role()`-style check.
- Security-definer role helpers (e.g. `fn_my_role()`) avoid RLS recursion when
  policies must consult the user's own profile.

## Attack checklist (run against throwaway accounts, one per hostile role)

1. INSERT with forged privileged fields: pre-confirmed status, verified
   payment, arbitrary price (0 / negative / inflated), foreign ownership.
   Trust-boundary fix shape: a BEFORE INSERT trigger pinning
   `status/payment/price` (price must equal the catalog or per-customer
   exception value).
2. UPDATE tamper on owned rows: money fields, internal/clinical fields, status
   escalation. Fix shape: one BEFORE UPDATE trigger allowing only whitelisted
   columns per role (customer: own notes + cancel; staff: business fields;
   owner: identity + ledger).
3. Cross-user reads on every PII table and every staff-only table.
4. Destructive ops: self-delete (orphans via FK ON DELETE SET NULL), staff
   delete/rename of core entities. Fix shape: no DELETE policy at all (service
   role bypasses RLS for admin tooling) + identity fields owner-only via
   trigger.
5. Direct inserts into evidence/ledger tables that should only be written by
   a security-definer RPC (fix: drop the INSERT policy entirely — the RPC runs
   as owner and bypasses RLS).
6. RPC abuse: oversized payload, empty payload, double-submit, foreign-target.
   Check rollback semantics: an exception aborts the whole transaction
   including earlier statements in the RPC.
7. Parallel duplicate inserts (race) against each unique constraint — exactly
   one must win.
8. Privilege escalation: role column self-update. Beware WITH CHECK subqueries
   that compare the new row to itself (always true) — enforce old-vs-new
   equality in a trigger instead.

## Integrity sweep template

One query per call; every row must be 0 on a healthy DB:
orphans · duplicate unique-key values · status/payment combinations that
shouldn't exist · rows referencing deleted auth users · duplicate business
keys · negative/zero money rows · role rows missing their dependent profile.

## Cleanup discipline

Delete by the IDs your probe created; restore fields to recorded prior values.
Never `delete where name in (...)` — production seed data reuses test names.
Re-run the sweep after cleanup to prove the DB is back to its pre-test state.
