# Security trap checklist (Postgres/RLS/auth) — from Supabase's official skill

Source: https://github.com/supabase/agent-skills (MIT), distilled 2026-11-16. These are
the traps that silently create vulnerabilities rather than errors. Load this before
writing any policy, view, function, or auth check.

## Auth and session

- **Never authorize on `user_metadata`.** `raw_user_meta_data` is user-editable and shows
  up in `auth.jwt()`. Put authorization data in `raw_app_meta_data` / `app_metadata`.
- **Deleting an auth user does not invalidate live tokens.** Sign out / revoke sessions
  first, keep JWT expiry short for sensitive apps, and check `session_id` against
  `auth.sessions` for strict guarantees.
- **JWT claims are stale until refresh.** `app_metadata` claims do not update on their own.

## RLS and views

- **Views bypass RLS by default.** Postgres 15+: `create view ... with (security_invoker = true)`.
  Older versions: revoke from `anon`/`authenticated`, or keep the view in an unexposed schema.
- **UPDATE requires a SELECT policy.** Without one, updates return 0 rows silently. No error.
- **`WITH CHECK` is mandatory on UPDATE policies.** Without it a user can reassign
  `user_id` to someone else.
- **`TO authenticated` alone is authentication, not authorization (BOLA/IDOR).** Pair it
  with an ownership predicate in `USING`.
- **`auth.role()` is deprecated.** Use the `TO authenticated` / `TO anon` clause. Worse,
  `auth.role() = 'authenticated'` breaks when anonymous sign-ins are on: anonymous users
  carry the `authenticated` Postgres role and pass the check.

## Functions

- **`SECURITY DEFINER` bypasses RLS.** Never add it to fix a permission error; prefer
  `SECURITY INVOKER`.
- **Every new function is granted EXECUTE to `PUBLIC` by default.** A `SECURITY DEFINER`
  function in `public` is therefore a public API endpoint for `anon` and `authenticated`.
  When it is genuinely needed: keep it in an unexposed schema, include an `auth.uid()`
  check in the body, and always `revoke execute ... from public, anon`.
- **Data API exposure is separate from RLS.** New tables may not be reachable at all until
  `anon`/`authenticated` are explicitly granted; granting without RLS is worse than not
  granting.

## Storage and supply chain

- **Storage upsert needs INSERT + SELECT + UPDATE.** With only INSERT, replacement fails
  silently.
- **Pin versions and commit lockfiles** for `supabase-js`, `@supabase/ssr`, and friends.

## Verify, do not assume

These traps fail closed only if you test them: attempt the forbidden write as the
restricted role and confirm a reject, then confirm the sanctioned RPC still succeeds
(see `authorization-and-integrity-testing.md`). `supabase db advisors` after schema work.
For anything not listed here, fetch `https://supabase.com/docs/guides/security/product-security.md`.
