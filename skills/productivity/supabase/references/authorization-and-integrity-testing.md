# Authorization & data-integrity verification (proving it works)

The SKILL.md security checklist tells you WHAT to fix. This is HOW to prove the fixes hold at runtime and that a real workflow persists correctly — the evidence you show before claiming an app is verified. All probes run against a live project; read credentials from the app's env file inside the probe and never print them.

## 1. Get a role's JWT (authenticated probing)
Sign in with the password grant to get an `access_token` for each role you need to act as:
```
POST {SUPABASE_URL}/auth/v1/token?grant_type=password
  {"email": ..., "password": ...}   (apikey = anon/publishable key)
→ access_token
```
**Never use the service-role/secret key to test authorization** — it bypasses RLS and role checks, so a call that succeeds under it proves nothing about what a real user can do. Use it only for independent post-mutation reads (step 3).

## 2. Prove authorization behaviorally, per role
Call the SECURITY DEFINER RPC (via `/rest/v1/rpc/<fn>`) or PostgREST endpoint **as the actor's JWT** and assert both directions:
- **Authorized case succeeds** (owner completes their clinic's record).
- **Unauthorized case is REJECTED** — a different actor (cross-patient), a wrong role (doctor doing an owner-only write), or a foreign row id — and the rejection is the guard's own message (e.g. `not authorized to complete this appointment`). The rejection message is the proof the guard fires.

Pitfall: a guard present in source is not proof it fires. Behavioral rejection on the live function is the only proof; a static grep or migration diff does not tell you the deployed function body. (Pair with the SKILL.md overload + live-privilege checks.)
Pitfall: **probe write-guard holes with a NOVEL value, never the row's current one.** A PATCH that rewrites the same value answers 204 whether the write landed or matched a 0-row no-op — and same-value writes are exactly what a value-change-based guard lets through, so that probe false-negatives the hole in both directions. Write a novel value, read back `updated_at`/the changed column to prove it LANDED, then restore the original value and report the mutation. A 204 without a read-back proves nothing either way.
Pitfall: resolve the actor's identity server-side (`auth.uid()`/`auth.email()`), never a client-passed role/user arg — otherwise the "unauthorized" test can pass for the wrong reason.
Pitfall: **the two PostgREST auth headers are different values.** When probing a table (not an RPC) as an authenticated user, `apikey` carries the anon/publishable key and `Authorization: Bearer <jwt>` carries the user's access_token. Passing the user JWT as `apikey` returns `401 Invalid API key` even though the JWT is perfectly valid — the gateway validates the apikey before it ever reads the bearer. Keep the service key only for independent post-mutation reads (step 3), never as the probe's `apikey` when testing what a real user can do.
Pitfall: **a user inserting their OWN row can still fail under a correct `with check (auth.uid() = user_id)`** when the table has NOT NULL columns the client does not supply. Set a DEFAULT (or make it nullable) on every column the self-insert path leaves empty — the ownership policy is not the only gate on INSERT, and the missing-default failure surfaces as a rejected insert that looks like an RLS denial. Verify the self-insert succeeds as the owner before trusting the policy is the sole boundary.
Pitfall: signing users up in a test loop hits `429 over_email_send_rate_limit` (every `POST /auth/v1/signup` triggers a confirmation email), which halts an auth/persistence run long before any real code bug and masks the behavior under test. When you only need a signed-in user to exercise session restore, wishlist/row persistence, or logout, create the user pre-confirmed via the service key (`POST /auth/v1/admin/users` with `email_confirm: true` — sends no email) and verify via LOGIN (password grant, no email) instead of signup. That drives the same session/persistence paths without consuming the email quota. Reserve real signup for the one test that must prove the registration flow itself.

## 3. Prove persistence independently of the UI
After driving a mutation through the real UI (or the RPC), read the resulting rows via PostgREST with the service key. A UI success message or a returned HTTP 200 is NOT verification — a mutation can fail and the UI still render success. Assert the row exists with the expected columns (owner, status, foreign keys) straight from the DB.

## 4. Prove idempotency / no duplicate side effects
Retry the mutation (double-click, network retry, re-run). Assert no duplicate committed rows — e.g. a financial/`income` row appears **exactly once** and the retry returns an `already_completed`-style no-op. This is the check-then-act / retry-duplicate guard.

## 5. Prove conflict / duplicate rejection at the DB
Attempt a clashing operation directly (same unique slot, double-booking, same one-per-day key) and assert the DB constraint/guard rejects it (HTTP 4xx). Frontend disabling of a button is not a boundary — the DB is.

## 6. Cross-role consistency
Read the same record as each affected role and assert every authorized view agrees on the shared state (status, performer, amount), with any differences explainable by role-specific permissions only. A value that differs without a permission reason is a bug.

Minimal evidence loop: **UI action → independent DB read → authorized RPC as each role → unauthorized RPC must be rejected → retry for idempotency → cross-role read agrees.** Capture the pass/fail per step; that set is the acceptance proof.
