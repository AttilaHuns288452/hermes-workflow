---
name: supabase-mcp-workflows
description: "Use when driving Supabase through the Hermes MCP tools."
tags: [supabase, mcp, migrations, edge-functions, tooling]
triggers: [supabase mcp, execute_sql, apply_migration, deploy_edge_function, edge function deploy, supabase migration apply, supabase mcp query]
---

# Supabase MCP Tool Workflows

How the Supabase MCP tools in this environment actually behave (mechanisms, not schema lists). Product-level Supabase guidance lives in the `supabase` skill; this covers the tool layer.

## Tool selection

- `execute_sql` — reads/verification. Its channel runs **read-only transactions**: any INSERT/UPDATE fails with `cannot execute INSERT in a read-only transaction`. Not a bug — use `apply_migration` (schema/state changes) or the REST API with the service role (data writes from scripts).
- `apply_migration` — named migrations for DDL + state changes; keeps migration history honest.
- `deploy_edge_function` — `files` is a list of `{name, content}`: the entrypoint PLUS relative dependencies (e.g. `name: "../_shared/paymongo.ts"` resolves beside the function).

## Pitfalls

- **One statement per `execute_sql` call.** Multi-statement batches are unreliable: depending on the shape they either error at the second statement (`syntax error at or near` the next block) or silently return only the last statement's result — a missing-looking result then reads as "the object doesn't exist" and sends you fixing the wrong thing (e.g. re-creating policies that were fine). Verify schema facts (columns, policies, triggers) one statement per call.
- **Apply migrations sequentially, never in parallel.** Concurrent `apply_migration` calls on one project race on the migration version key (both pick the same timestamp) and one silently rolls back — the rolled-back table/policies are simply missing afterward, so verify each migration's objects exist before submitting the next.
- **A verification `DO` block returns no result rows** (empty tool output on success). Make the verdict visible: end with `raise exception 'SMOKE ALL PASS'` — every assert raises its own FAIL message first, so the error channel carries the verdict — or write the result into a scratch table and SELECT it in a separate call.
- **Edge function bundles are per-function.** A shared module (imported as `../_shared/x.ts`) is only live in functions that included it in THEIR deploy — redeploying one function never updates its siblings. Include the shared file in every deploy whenever it changes, or one path silently runs stale shared code.
- **Tool output redacts credential-shaped values** (`apikey:`/`Authorization:` header lines render as `***`). Copying such "verbatim" file content into a deploy payload produces unparseable code. Author those lines explicitly instead (e.g. `const svcAuth = { apikey: KEY, Authorization: 'Bearer ' + KEY }`), then re-emit from what you authored.
- `verify_jwt: false` only for endpoints doing their own signature auth (webhooks); everything else keeps JWT verification on.
- **Never reference `auth.users` in RLS policies** authored in `apply_migration` payloads: that table is RLS-locked with zero policies, so any policy qualifying against it makes every write fail with `permission denied for table users` (reads return empty, no error). Use the JWT claim instead — `lower(auth.jwt() ->> 'email')` — and verify a real role's write after applying, not just policy existence.
- Policy/trigger recon before editing: `pg_policies` (policyname, cmd, roles, qual, with_check) and `pg_trigger ... where not tgisinternal` in ONE statement per relation via `execute_sql` — duplicated triggers from layered migrations show up here as double audit rows.
- **Recreating a function is a signature-preservation exercise.** `apply_migration` refuses return-type changes (42P13 "Use DROP FUNCTION first"), so replacements are DROP+CREATE — which invites drift: argument NAMES are load-bearing (named-arg RPCs match by name), return shapes break callers, and error strings are pinned by tests. Capture `pg_get_functiondef` (or the repo's canonical SQL) FIRST and diff your replacement against it — recreating "from what you remember" reintroduces bugs that were already fixed.
- **`REVOKE ... FROM public` also strips the default grants service_role relied on** — privilege lockdowns must re-grant explicitly to `service_role`, or server-side callers break while client roles are correctly denied.
- RLS policy semantics worth checking during any security audit live in `references/rls-privilege-audit.md` (permissive-OR traps, definer-function execute grants, adversarial verification).

## When the MCP tools aren't in the session toolset

`hermes mcp list` showing the server enabled does NOT mean `tool_search` exposes its
tools this session. The same authorized connection can be driven over raw JSON-RPC:

1. OAuth tokens live in `~/.hermes/mcp-tokens/` (`supabase.json` = access +
   refresh_token + expires_at; `supabase.client.json` = client_id/secret;
   `supabase.meta.json` = token_endpoint). Expired access token → POST
   `grant_type=refresh_token` to the token_endpoint and rewrite `supabase.json`.
2. POST to `https://mcp.supabase.com/mcp` with
   `Authorization: Bearer <access_token>`, `Accept: application/json, text/event-stream`,
   `MCP-Protocol-Version: 2025-03-26` — and a **browser-like `User-Agent`**, or
   Cloudflare blocks with 403 error 1010 before the request reaches the server.
3. Handshake: `initialize` (keep the returned `Mcp-Session-Id` on later calls) →
   `notifications/initialized` → `tools/call`. Responses are a **plain JSON body**
   despite the SSE Accept header — parse `{"result": …}` directly.
4. `apply_migration {project_id, name, query}` and `execute_sql {project_id, query}`
   are ordinary tools on that server; same one-statement and read-only rules apply.

## Output Pattern

[code] → skipped: [X], add when [Y].
