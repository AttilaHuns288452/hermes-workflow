# Supabase MCP — specifics

Endpoint `https://mcp.supabase.com/mcp` (OAuth; token files `supabase.json` /
`supabase.meta.json` / `supabase.client.json`). Cloudflare-fronted: browser UA
mandatory.

Tools relevant to DB work (names as returned by `tools/list`):

| Tool | Behavior |
|---|---|
| `execute_sql(project_id, query)` | READ-ONLY transaction. Any write raises `25006 cannot execute INSERT in a read-only transaction`. Multi-statement strings fail at the seam — one statement or one DO block. |
| `apply_migration(project_id, name, query)` | Runs arbitrary SQL (DDL+DML) as a migration entry; returns `{'success': true}` in content text. Use for migrations AND one-off data fixes (name them `zz_<purpose>`). |
| `list_migrations(project_id)` | Migration history as recorded server-side. |
| `query_logs(project_id, ...)` | Intermittently unavailable; retry once, then fall back to evidence from tests. |
| `deploy_edge_function(project_id, name, entrypoint_path, verify_jwt, files[])` | Creates/updates a function. `files` = `[{name, content}]`, `entrypoint_path` like `index.ts`; a shared module ships as a second file (`_shared/x.ts`) and the deploy must carry EVERY imported file. Source file content from disk (display redaction corrupts payloads built from printed text). |
| `get_edge_function(project_id, name)` | Returns the deployed source UNMASKED inside the JSON — the reliable way to read code containing env-key references back. |

## Edge function deploys: the deploy call is not the proof

Verify the deployed function itself, in this order:

1. **Read back** with `get_edge_function` and confirm the new marker strings are present.
2. **Unauthenticated request**: `401` proves it is deployed AND auth-gated; `500` usually means an import crash (missing shared file, wrong relative path); `404` means routing or a `verify_jwt` mismatch.
3. **`OPTIONS` preflight** returns `200` with CORS headers — proves the browser client can reach it.
4. **One real authenticated flow** whose DB effect is read back.

Preserve each function's `verify_jwt` flag on redeploy (webhook handlers are `false`); letting it default to `true` turns a working webhook into 401s.

## Semantics worth knowing

- Errors return HTTP 200 with a JSON error INSIDE the content text (`{"error":
  {"name": "HttpException", "message": "Failed to run sql query: ERROR: ..."}}`)
  — always parse content for `"error"` before claiming a query worked.
- A `DO` block that only raises `NOTICE` produces EMPTY content — empty is
  ambiguous with the framing bug; make verdicts explicit (raise exception or a
  result row).
- PostgREST RLS failures surface differently by cause: no policy on a granted
  verb = silent 0 rows / `error: null`; missing table GRANT = hard
  `permission denied for table <t>`. Legacy client code may silently depend on
  the no-op shape.
- Query `pg_policies`, `information_schema`, `pg_get_function_arguments()` for
  ground truth on policies/defaults/signatures — never infer them from the
  migration files alone (applied state can drift from disk history).
