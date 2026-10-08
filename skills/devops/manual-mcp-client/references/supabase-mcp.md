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

Semantics worth knowing:

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
