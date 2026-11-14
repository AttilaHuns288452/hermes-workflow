---
name: supabase
description: "Use when doing ANY task involving Supabase. Triggers: Supabase products (Database, Auth, Edge Functions, Realtime, Storage, Vectors, Cron, Queues); client libraries and SSR integrations (supabase-js, @supabase/ssr) in Next.js, React, SvelteKit, Astro, Remix; auth issues (login, logout, sessions, JWT, cookies, getSession, getUser, getClaims, RLS); Supabase CLI or MCP server; schema changes, migrations, security audits, Postgres extensions (pg_graphql, pg_cron, pg_vector)."
metadata:
  author: supabase
  version: "0.1.2"
---

# Supabase

## Core Principles

**1. Supabase changes frequently — verify against changelog and current docs before implementing.**
Do not rely on training data for Supabase features. Function signatures, config.toml settings, and API conventions change between versions.

First, fetch `https://supabase.com/changelog.md` (a lightweight summary index — not a heavy pull), scan for `breaking-change` tags relevant to your task, and follow the linked page for any that apply. Then look up the relevant topic using the documentation access methods below.

**2. Verify your work.**
After implementing any fix, run a test query to confirm the change works. A fix without verification is incomplete.

**3. Recover from errors, don't loop.**
If an approach fails after 2-3 attempts, stop and reconsider. Try a different method, check documentation, inspect the error more carefully, and review relevant logs when available. Supabase issues are not always solved by retrying the same command, and the answer is not always in the logs, but logs are often worth checking before proceeding.

**4. Exposing tables to the Data API:** Depending on the user's [Data API settings](https://supabase.com/dashboard/project/<ref>/integrations/data_api/settings), newly created tables may not be automatically exposed via the Data (REST) API. If this is the case, `anon` and `authenticated` roles will need to be explicitly granted access.

> Note that this is separate from RLS, which controls which _rows_ are visible once a table is accessible, not whether the table is accessible at all.

When a user reports a SQL-created table is unexpectedly inaccessible, check their Data API settings and whether the roles have been granted access via explicit `GRANT` SQL. When granting public (`anon`/`authenticated`) access, always enable RLS too. See [Exposing a Table to the Data API](https://supabase.com/docs/guides/api/securing-your-api.md) for the full setup workflow.

**5. RLS in exposed schemas.**
Enable RLS on every table in any exposed schema, which includes `public` by default. This is critical in Supabase because tables in exposed schemas can be reachable through the Data API when the `anon`/`authenticated` roles have access (see [Exposing a Table to the Data API](https://supabase.com/docs/guides/api/securing-your-api.md)). For private schemas, prefer RLS as defense in depth. After enabling RLS, create policies that match the actual access model rather than defaulting every table to the same `auth.uid()` pattern.

**6. Security checklist.**
When working on any Supabase task that touches auth, RLS, views, storage, or user data, run through this checklist. These are Supabase-specific security traps that silently create vulnerabilities:

- **Auth and session security**
  - **Never use `user_metadata` claims in JWT-based authorization decisions.** In Supabase, `raw_user_meta_data` is user-editable and can appear in `auth.jwt()`, so it is unsafe for RLS policies or any other authorization logic. Store authorization data in `raw_app_meta_data` / `app_metadata` instead.
  - **Deleting a user does not invalidate existing access tokens.** Sign out or revoke sessions first, keep JWT expiry short for sensitive apps, and for strict guarantees validate `session_id` against `auth.sessions` on sensitive operations.
  - **A revoked session leaves "phantom" tabs whose JWT still passes data reads.** `signOut()` defaults to `scope: 'global'` (revokes ALL of the user's server sessions); with per-tab session storage the other tabs keep an unexpired JWT that PostgREST/RLS still honors while `auth/v1/user` rejects it (`403 session_not_found`). Shape: same token, data reads work, identity-checked calls fail with "invalid session" — which looks like a broken function, not a dead session. Diagnose by probing `auth/v1/user` vs a PostgREST read with the same token; prefer `signOut({ scope: 'local' })` for per-tab sign-out and drop client state on the `SIGNED_OUT` auth event. Make the API layer self-heal: when a getUser()-gated call (edge function, auth-checked RPC) returns "invalid session"/`session_expired`, clear the local session and surface a re-auth action instead of a dead-end error — the revocation always detonates on the step the user cares about (booking worked, payment says invalid session). See `references/auth-flow-verification.md`.
  - **If you use `app_metadata` or `auth.jwt()` for authorization, remember JWT claims are not always fresh until the user's token is refreshed.**
  - **A role/permission check that runs before the auth client commits the session answers negative** (the server sees no `auth.uid()`), and caching that negative locks the legitimate user out until a reload — the UI bounces them from their own admin surface while the database says they are authorized. Await `getSession()` before the first check, and cache only confirmed positives: a `false` is retried on the next mount, a `true` is remembered.
  - **Renaming account emails in code is not renaming the accounts.** `auth.users.email`, `profiles.email`, `dentists.email`, and any lookup keyed on email are the authoritative identity rows; a repo-wide string replace leaves them behind and silently breaks every scripted login and email-based join. Rename the rows in the same change set (or ship a data migration alongside), then run one real sign-in per renamed account before claiming the rename is done.
  - **`auth.signUp()` always sends the confirmation email** (even when confirmation is unenforced — `confirmed_at` stays null, login works immediately). A welcome/onboarding email cannot be delivered through the signup path; account provisioning that must send specific copy needs `inviteUserByEmail` / `generateLink`, and `type: 'recovery'` sends "reset your password" copy — the wrong template reads to the user as "the app emailed me a password reset". See [references/live-deployment-parity.md](references/live-deployment-parity.md).

- **API key and client exposure**
  - **Never expose the `service_role` or secret key in public clients.** Prefer publishable keys for frontend code. Legacy `anon` keys are only for compatibility. In Next.js, any `NEXT_PUBLIC_` env var is sent to the browser.

- **RLS, views, and privileged database code**
  - **Views bypass RLS by default.** In Postgres 15 and above, use `CREATE VIEW ... WITH (security_invoker = true)`. In older versions of Postgres, protect your views by revoking access from the `anon` and `authenticated` roles, or by putting them in an unexposed schema.
  - **UPDATE requires a SELECT policy.** In Postgres RLS, an UPDATE needs to first SELECT the row. Without a SELECT policy, updates silently return 0 rows — no error, just no change. A self-update policy must also pin the ownership column in `WITH CHECK` (e.g. `user_id = auth.uid()`), not just `USING` — without it the row can be re-linked to another account.
  - **Do not put `security definer` functions in an exposed schema.** Keep them in a private or otherwise unexposed schema.
  - **Role checks are not row authorization — that gap is the classic IDOR.** A SECURITY DEFINER function that gates on `role in ('doctor','owner')` (or any role) and then reads/writes a caller-supplied row id WITHOUT also checking the caller's relationship to that specific row lets any holder of the role act on ANY object — e.g. a doctor completing another doctor's patient appointment by passing its id. Derive the actor's identity server-side (`auth.uid()` / `auth.email()`, never a client-passed user/role arg) and match it to the row's owner/assignee/`<entity>_id` before any write; reserve the "act on any row" path for the top role (owner) only. Corollary (segregation of duties): gate privileged side-effects — financial writes, status changes on others' records — to the specific role that owns that authority, not broadly to every authenticated staff role.
  - **Verify live function privileges after every change to SECURITY DEFINER code; migration history is not proof of the current ACL.** Client-role EXECUTE grants reappear through schema pushes, database resets, or later migrations, silently re-exposing a function an earlier REVOKE locked down. Probe the live catalog (`has_function_privilege('authenticated', 'schema.fn', 'EXECUTE')` for each client role) and ALSO gate inside the function body (`if auth.role() not in ('service_role') then raise ...`) — the body gate holds even when grants drift, so the two layers must both exist. When verifying a rewritten body with `pg_proc.prosrc` token greps (stale marker absent, new path present), remember `SECURITY DEFINER` is a DDL attribute in `pg_proc.prosecdef`, never in prosrc — a prosrc probe for it always returns zero (false negative). Gate the attribute on `prosecdef` / `pg_get_functiondef`, and probe `count(*)` overloads alongside so a stale sibling signature cannot hide.
  - **A function's overloads are independent code paths — a guard added to one does not protect the others.** After rewriting a SECURITY DEFINER function to add an authorization check, query `pg_proc where proname = '<fn>'` for EVERY overload. A stale overload (e.g. one from before a parameter was added) may lack the new guard, leaving an unguarded path a caller can still reach; and when both overloads have defaulted parameters, even legitimate single-argument calls fail with `42725: function is not unique`. Drop the dead overloads (the `drop function if exists <fn>(argtypes)` pattern) so the guarded version is the only entry point, then re-run the authorization test against the surviving signature.
  - **Write the authorization comparison fail-closed.** When the guard compares the caller's identity to the row's owner/assignee (often a nullable FK or an email), a NULL on either side must DENY, not pass: use `IS DISTINCT FROM` / `IS NOT DISTINCT FROM`, never `<>`/`=` on nullable lookups (which are NULL-false and can let a row through a `not (a <> b)` guard, or wrongly deny on the legitimate path). Match emails case-insensitively on BOTH sides (`lower(a) = lower(b)`) — a case-sensitive comparison silently drops the legitimate actor or lets a near-miss through. Fail-closed plus case-insensitive is the correct default for every row-ownership check.
  - **A trigger enforcing a cross-table invariant must be `security definer`** (with a pinned `search_path`): a plain trigger runs with the INVOKER's RLS visibility, so its `exists (select 1 from other_table ...)` sees zero rows whenever the invoker cannot read that table — the guard silently passes every collision (fail-open). Scope it to the relevant columns (`before insert or update of email`) and early-return on an unchanged value so unrelated edits never trip it. This is the right shape for a shared email namespace across two role tables (staff vs patient): the collision check belongs in the DB, not in an app-layer pre-check.
  - **A trigger that `RAISE`s rolls back its own side effects.** Any audit row written just before `raise exception` dies with the aborted transaction, so "log the rejection, then reject" silently loses the log. To enforce AND record, validate in a SECURITY DEFINER RPC that RETURNS `{ok:false, error}` (the transaction commits, so the audit row survives) while the raising trigger stays behind it as the fail-closed backstop for writes that bypass the RPC. Enforcement must fail closed; audit logging must never break the action it describes.
  - **`current_user` / `session_user` inside a SECURITY DEFINER function are the function OWNER (usually `postgres`), never the caller** — so any role or service discrimination built on them is a compile-time constant: `current_user = 'service_role'` is never true, `current_user <> 'authenticated'` is always true. Guards silently take one branch forever and audit triggers never fire (or always fire) — and the hole this opens is exactly the privileged path the guard was meant to close. Discriminate service/admin calls by JWT presence (`auth.uid() is null` = no user JWT = service/admin path) and roles from `auth.jwt()` claims or an `auth.uid()`-looked-up profile row; use that ONE convention in every function AND trigger in the codebase so a caller cannot slip between two vocabularies.

- **Storage access control**
  - **Storage upsert requires INSERT + SELECT + UPDATE.** Granting only INSERT allows new uploads but file replacement (upsert) silently fails. You need all three. For user-owned upload buckets, a uid-prefixed object name plus `with check (bucket_id = '...' and name like auth.uid()::text || '-%')` on INSERT enforces own-files-only writes without per-user folders; pair with a public-read policy when the files are avatars or other shared assets.

For any security concern not covered above, fetch the Supabase product security index: `https://supabase.com/docs/guides/security/product-security.md`

## Querying: timestamps

**A naive timestamp string is read as UTC.** `timestamptz` input without an offset (`2026-10-27T10:00:00`) is interpreted by Postgres as UTC — in a UTC+8 clinic every scheduling write lands 8 hours off and availability checks answer "no dentist available" for slots that are visibly free. When the domain stores wall-clock local time (clinic schedules, opening hours), send an explicit offset (`+08:00`) or normalize at a single shared service-layer helper (naive → clinic offset; already-instant strings pass through untouched). Prove each write path once with both shapes and read back the stored instant equals the intended wall-clock.

## Querying: bulk inserts and seeding

**PostgREST requires identical key sets across every row of a bulk insert.** A mixed-shape array (row A carries `foo`, row B omits it because the value is null/default) fails with `All object keys must match` even when the omitted value would have defaulted anyway. Pad every row to the same shape with explicit nulls/defaults before posting. This bites fixture and seeding scripts that build rows conditionally — and a silently failed seed leaves the downstream test reading real data, which then "fails" on values the test assumed it had created.

## Querying: FK arrays and embedding

**A `uuid[]` (or any array) column holding foreign keys is NOT embeddable through PostgREST's `select=<table>(<col>)` syntax.** PostgREST embeds only across real single-column FK relationships; an array of ids declares none, so `appointments.select('service_id, services(name)')` resolves only the scalar `service_id`'s name (or nothing) and silently drops every other id in `service_ids[]`. A row storing several linked items then renders just the first — a data-trust bug that looks like missing data, not a query error. Resolve the array's names client-side: fetch the referenced rows into an id→name map and look up each id at render time (or expose a thin RPC that unnests the array and joins). Wire the same resolver into EVERY display surface for that field (list cards, detail/receipt, calendar) — fixing one screen leaves the others still showing the single-name fallback.

**PostgREST rejects an unfiltered `DELETE` with `400`** — a WHERE clause is mandatory. A cleanup step that swallows that error therefore leaves every test row behind, which skews exactly the uniqueness and duplicate guards under test. Delete by identity: read the row ids first and issue `DELETE ...?id=eq.<id>` per row, or filter by the run's own marker (`?marker=like.*<run-id>*`) so only the rows the run created are matched.

## Debugging auth signup/signin failures

**GoTrue flattens a trigger's `RAISE` into a generic client error.** A signup blocked by a database guard (email-namespace collision, uniqueness trigger) returns `Database error saving new user` with `error_code: unexpected_failure` — the real `SQLSTATE` + trigger message exists only in the auth logs. When a signup/sign-in fails with a generic DB error, do not debug the client: query `source='auth_logs'` for the request (recipe in [references/live-database-access.md](references/live-database-access.md)) and read the flattened error there — the trigger message names the exact invariant that fired.

- **Diagnose the collision on the identity rows, not in auth code.** The invariant almost always references other tables (e.g. a shared staff/patient email namespace): probe those tables for the input value before blaming the auth client. A targeted PostgREST filter that returns empty is NOT proof the row is absent — confirm with an unfiltered listing before concluding.
- **Keep the guard; fix the message and the data.** A guard that rejects the input is usually correct product behavior — the defect is either stale data holding the identity (a leftover test/staff row on the email: free or delete the row per the user's deletion preference, do not weaken the guard) or the UX (map the generic client error at the catch to actionable copy: which login to use instead / use a different email). Never answer a guard rejection by removing the guard.

## Supabase CLI

Always discover commands via `--help` — never guess. The CLI structure changes between versions.

```bash
supabase --help                    # All top-level commands
supabase <group> --help            # Subcommands (e.g., supabase db --help)
supabase <group> <command> --help  # Flags for a specific command
```

**Supabase CLI Known gotchas:**

- `supabase db query` requires **CLI v2.79.0+** → use MCP `execute_sql` or `psql` as fallback
- `supabase db advisors` requires **CLI v2.81.3+** → use MCP `get_advisors` as fallback
- When you need a new migration SQL file, **always** create it with `supabase migration new <name>` first. Never invent a migration filename or rely on memory for the expected format.

**Version check and upgrade:** Run `supabase --version` to check. For CLI changelogs and version-specific features, consult the [CLI documentation](https://supabase.com/docs/reference/cli/introduction) or [GitHub releases](https://github.com/supabase/cli/releases).

## Supabase MCP Server

For setup instructions, server URL, and configuration, see the [MCP setup guide](https://supabase.com/docs/guides/getting-started/mcp).

**Troubleshooting connection issues** — follow these steps in order:

1. **Check if the server is reachable:**
   `curl -so /dev/null -w "%{http_code}" https://mcp.supabase.com/mcp`
   A `401` is expected (no token) and means the server is up. Timeout or "connection refused" means it may be down.

2. **Check `.mcp.json` configuration:**
   Verify the project root has a valid `.mcp.json` with the correct server URL. If missing, create one pointing to `https://mcp.supabase.com/mcp`.

3. **Authenticate the MCP server:**
   If the server is reachable and `.mcp.json` is correct but tools aren't visible, the user needs to authenticate. The Supabase MCP server uses OAuth 2.1 — tell the user to trigger the auth flow in their agent, complete it in the browser, and reload the session.

## Supabase Documentation

Before implementing any Supabase feature, find the relevant documentation. Use these methods in priority order:

1. **MCP `search_docs` tool** (preferred — returns relevant snippets directly)
2. **Fetch docs pages as markdown** — any docs page can be fetched by appending `.md` to the URL path.
3. **Web search** for Supabase-specific topics when you don't know which page to look at.

## Making and Committing Schema Changes

**To make schema changes, use `execute_sql` (MCP) or `supabase db query` (CLI).** These run SQL directly on the database without creating migration history entries, so you can iterate freely and generate a clean migration when ready.

Do NOT use `apply_migration` to change a local database schema — it writes a migration history entry on every call, which means you can't iterate, and `supabase db diff` / `supabase db pull` will produce empty or conflicting diffs. If you use it, you'll be stuck with whatever SQL you passed on the first try.

**Rapid-fire `apply_migration` calls collide on version keys.** Each call stamps `schema_migrations` with a timestamp version; two calls in the same second produce `duplicate key value violates unique constraint "schema_migrations_pkey"` — a version collision, not a SQL error. Retry the second call under a fresh name instead of rewriting its SQL.

**When ready to commit** your changes to a migration file:

1. **Run advisors** → `supabase db advisors` (CLI v2.81.3+) or MCP `get_advisors`. Fix any issues.
2. **Review the Security Checklist above** if your changes involve views, functions, triggers, or storage.
3. **Generate the migration** → `supabase db pull <descriptive-name> --local --yes`
4. **Verify** → `supabase migration list --local`

## Reference Guides

- **Live DB access when MCP is permission-denied** → [references/live-database-access.md](references/live-database-access.md)
  **Read when** project-scoped MCP calls return permission errors, a migration fails against a live database whose schema drifted from the repo, or an auth signup/sign-in fails with a generic "database error" (the auth-logs query recipe that reveals the real trigger message lives there). First settle the account identity (`list_projects` + re-auth) — a permission error on an account with zero visible projects is an auth problem, not an ACL — and never report the live database as blocked or unverifiable before both paths in that reference have been attempted: the user holds dashboard access and expects migrations and data fixes to be made through the SQL Editor when the MCP is permission-denied.

- **Live deployment parity (repo vs deployed)** → [references/live-deployment-parity.md](references/live-deployment-parity.md)
  (or an edge function 404s, a frontend call hits a missing column/function/policy, or you must prove that migrations and edge functions in the repo are actually live. Probe recipes: 404-vs-401 for functions, the MCP `deploy_edge_function` payload + `verify_jwt` rule (a function that authenticates itself must deploy `verify_jwt: false` or CORS preflights fail), a 5-step behavioral verification ladder for deployed functions, live-catalog reconciliation for migrations, invite/recovery template semantics for provisioning emails.

- **Auth flow verification** → [references/auth-flow-verification.md](references/auth-flow-verification.md)
  **Read when** verifying OAuth redirects, PKCE, or auth flows after an origin change, or when an OAuth login lands on the wrong host (e.g. redirects to localhost) — that is a URL Configuration allow-list fix (Site URL + Redirect URLs), not a client-code bug.
- **Authorization & data-integrity verification** → [references/authorization-and-integrity-testing.md](references/authorization-and-integrity-testing.md)
  **Read when** you must PROVE a Supabase app works before reporting it verified: behavioral per-role RPC/RLS tests, independent DB reads after UI mutations, idempotency and conflict rejection. The checklist above says what to fix; this is how to gather the runtime evidence.
- **Database-enforced admin / role gate** → [references/admin-role-gate.md](references/admin-role-gate.md)
  **Read when** building any admin/moderator/staff-only surface (admin console, review moderation, privileged writes). A client-side admin flag is not authorization — this is the schema + `is_admin()` + policy recipe that keeps privilege in the DB where the client cannot flip it, with the behavioral proof.
- **Encrypted secret storage & admin-configurable integrations** → [references/secrets-config-storage.md](references/secrets-config-storage.md)
  **Read when** an admin must set/rotate a third-party API key or credential through the app UI: AES-256-GCM at rest in `app_settings`, admin-only `is_admin()` RLS, and a runtime DB-first/env-fallback lookup so a saved key applies without a redeploy.
- **Migration execution pitfalls** → [references/migration-execution-pitfalls.md](references/migration-execution-pitfalls.md)
  **Read when** writing or applying SQL/migrations through the MCP or CLI: what `apply_migration` actually executes, verification-query semantics, trigger shape across tables of different row types, and how to tell a real delete from an RLS-filtered no-op.
- **Skill Feedback** → [references/skill-feedback.md](references/skill-feedback.md)
  **MUST read when** the user reports that this skill gave incorrect guidance or is missing information.
