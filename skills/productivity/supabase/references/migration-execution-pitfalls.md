# Migration & SQL execution pitfalls

Mechanics of getting schema changes applied and VERIFIED correctly through the
Supabase MCP (`apply_migration`, `execute_sql`) or the CLI. For what to put IN
the SQL (RLS, triggers, grants), see the SKILL.md security checklist.

## `apply_migration` executes the `query` parameter, not a repo file

`name` is bookkeeping (it stamps `schema_migrations`); the SQL that runs is
whatever you pass in `query`. Sending a placeholder while assuming the name
points at a file records a NO-OP migration entry under that name — the schema
never changes, the history now lies, and re-running under the same name may
conflict. Always inline the full statement list in `query`, then verify the
objects exist (below). To re-apply after a bad entry, use a fresh name suffix;
the repo file stays the source of truth for what SHOULD be there.

## Multi-statement results: only the LAST statement's rows come back

`execute_sql` with several statements returns the result of the final one
only. Do not read that as "the earlier statements returned nothing" — verify
each claim with its own targeted query (object existence, row counts, ACL
probes) instead of one combined script.

## Verify what actually landed

After applying, probe the live catalog rather than trusting the apply response:

```sql
select to_regclass('public.<table>');                       -- table exists
select tgname from pg_trigger where tgrelid = 'public.<t>'::regclass and not tgisinternal;  -- triggers attached
select has_function_privilege('authenticated', 'public.<fn>', 'EXECUTE');  -- ACL
select pg_get_functiondef(oid) from pg_proc where proname = '<fn>';        -- body is the new one
```

## Verification legs must return ROWS, not NOTICEs

A verification script wrapped in `DO $$ ... RAISE NOTICE 'verdict: ...' $$`
returns nothing to the client — the tool prints an empty result and the legs
look unproven even when every one passed. Make each leg SELECT its evidence
(or `RAISE EXCEPTION` on the failure path) so the verdict comes back as data:
assert queries return rows on pass, and re-run any NOTICE-only legs as
targeted SELECTs before citing them as proof.

## Triggers must not assume a row shape

A generic logging/audit trigger referencing `new.id` aborts the whole write
when it lands on a table without an `id` column (e.g. key/value settings
tables) — and because the trigger runs inside the user's statement, the SAVE
the admin just clicked fails. Read the identifier shape-agnostically:
`coalesce(to_jsonb(new) ->> 'id', to_jsonb(old) ->> 'id', to_jsonb(new) ->> 'key',
to_jsonb(old) ->> 'key')`.

## A `RAISE` in a trigger rolls back its own audit rows

See the SKILL.md checklist: log-then-raise loses the log. The working pattern
for "validate, reject, and record" is a SECURITY DEFINER RPC returning
`{ok:false, error}` (commits, keeps the audit row) with the raising trigger as
backstop for direct writes.

## PostgREST DELETE: 204 is not proof of deletion

A `DELETE` filtered by an RLS policy that excludes the row deletes zero rows
and still answers `204 No Content` — identical to a successful delete. Never
cite the status code as evidence a row is gone: read the row back (or compare
counts) before reporting deletion, and treat 204 + "row still present" as RLS
doing its job, not a bug.

## Re-auth when MCP calls say "You do not have permission"

For OAuth-backed MCP servers (e.g. `mcp.supabase.com`), that error usually
means the token lapsed, not an ACL. Run `hermes mcp login <server>` —
**as a background job** (`background=true`): the flow keeps a localhost
callback listener alive, and a foreground invocation can exit before you open
the authorization URL, killing the handshake. Hand the printed URL to the
user, wait for the callback, then retry the tool call.
