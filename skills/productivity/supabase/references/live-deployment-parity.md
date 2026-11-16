# Live Deployment Parity — repo artifacts vs what is actually live

A migration file or edge function existing in the repo is NOT proof it is
deployed. Migrations get skipped (partial application, MCP permission walls,
hand-applied SQL), and edge functions sit in `supabase/functions/` forever
without ever being deployed. Probe the live surface before trusting either.

## Edge functions: 404 vs 401

Probe the deployed endpoint with an unauthenticated POST:

- **404** → the function is NOT deployed (the repo copy is inert). Deploy it
  (MCP `deploy_edge_function`, or `supabase functions deploy <name> --no-verify-jwt`
  when its header says so) and re-probe.
- **401 / 403** → deployed and auth-gated (normal). Compare against a sibling
  function known to be deployed to prove the 404 is not a routing/config issue.

A UI flow coded as "call function, fall back to a client path on failure" will
silently run its fallback forever when the function is missing — the fallback
path becomes production and nobody notices. Verify each function the frontend
calls at least once per handoff.

## Deploying a function through MCP `deploy_edge_function`

Payload shape: `{project_id, name, entrypoint_path: 'index.ts', verify_jwt,
files: [{name: 'index.ts', content: '<source>'}]}` (a `_shared/` import is a
second `files[]` entry named `_shared/x.ts`). **`verify_jwt` semantics decide
whether browsers can call the function at all**: `verify_jwt: true` makes the
platform reject CORS preflight `OPTIONS` (a preflight carries no JWT), so every
browser call fails before reaching the code. When the function authenticates
the caller itself (its own `auth/v1/user` check), deploy with
`verify_jwt: false` — matching the `--no-verify-jwt` its header documents.

Assemble the payload in a script that reads the source **from disk**. Tool
output display-redacts `Authorization: Bearer ...`, `apikey: X`, and env-key
names (`SUPABASE_SERVICE_ROLE_KEY`) — copy-pasting displayed source into a
deploy payload corrupts it with literal `***`. Corollary for authoring: split
key literals in function source (`Deno.env.get('SUPABASE_' + 'SERVICE_ROLE_KEY')`)
so a plain `cat` of the file survives a redacting display path.

## Verifying a deployed function: the behavioral ladder

404-vs-401 only proves existence. For a privileged function, run the full
ladder before calling it verified:

1. Unauthenticated POST → `401` (deployed AND gated, not just routed).
2. `OPTIONS` preflight from a real origin → `200` (proves the verify_jwt
   choice above is right).
3. Authorized happy path with the REAL caller shape → `200` + read the effect
   back (an invited user row, a written record) — a `200 ok:true` alone is not
   proof the side effect landed.
4. Wrong-role caller on the same body → `403` (the role gate holds; a `200`
   here is the finding).
5. Clean up any test record the happy path created (auth admin delete for
   invited test accounts), then re-read to confirm cleanup.

## Migrations: probe the live catalog, don't trust the chain

Before claiming a schema feature exists:

1. Probe `information_schema.columns` / `pg_proc` / `pg_policies` for the exact
   objects the frontend calls (a missing column or function surfaces as a
   runtime PostgREST error, not a build failure).
2. Watch for policy drift in BOTH directions — a clean replay is only safe
   when neither exists:
   - **Live-only policies** (in `pg_policies`, no migration creates them):
     hand-pushed schema; replay misses them and silently narrows or blanks
     access the app already relies on.
   - **Chain-only policies** (a migration creates them, live dropped them):
     the seed migration's `... full access for authenticated ... using (true)`
     leftovers are the classic case — safe scoped policies get added live or
     in later files while the permissive one is never dropped, so a clean
     replay re-opens the whole table to any authenticated role.
   Reconcile with ONE idempotent migration per table: `drop policy if exists`
   every name EITHER side knows (probe `select policyname, cmd, qual,
   with_check from pg_policies where tablename = '<t>'` and grep the
   migrations for `create policy`/`drop policy`), then recreate the canonical
   live set with the live quals verbatim — never rewrite a qual from memory.
   Apply it through the path that stamps migration history (`apply_migration`
   / dashboard SQL editor), not ad-hoc `execute_sql`.
   Prove it two ways: `pg_policies` afterwards returns exactly the canonical
   names, and a deliberately-failing write's error text names the guard (the
   trigger's `raise exception` message + its PL/pgSQL CONTEXT line) — a `DO`
   block that catches the exception returns `[]` and proves nothing.
3. Partial application is the norm, not the exception: a table can exist while
   a column added three migrations later does not. Probe per-object, never
   per-migration-file.
4. **Migration history can lag the schema in the other direction** — the
   objects exist live while `list_migrations` has no row for the file that
   creates them (hand-applied SQL, a squashed push, a renamed file). Replaying
   that file is then wrong: `create or replace view` looks harmless but any
   `alter table ... add column` in the same file fails on the first duplicate,
   and a guarded `if not exists` version merely no-ops. Record the file as
   applied through the path that stamps history and note the skip, rather than
   editing the migration to be re-runnable or bumping it to a new number. When
   reporting release state, say which objects are live AND which migration
   numbers the history is missing — the two facts together are the truth, and
   neither alone is.

## Account provisioning: the email template IS the product

`auth.signUp()` dispatches the **confirmation** email even when email
confirmation is unenforced (`confirmed_at` stays null and login works
immediately) — so account creation always sends *some* email. If the intended
UX is a welcome/onboarding message, the signup path cannot deliver it. Use
`admin.inviteUserByEmail` / `generateLink({ type: 'invite' })` for invites, and
remember `type: 'recovery'` sends the "reset your password" template — which
reads as a password-reset email when the intent was a welcome/setup email.
Pick the link type for its EMAIL COPY, not just its function name.
