# Composio Connect MCP — OAuth, keys, and config repair (verified 2026-08)

Composio's federated MCP endpoint is `https://connect.composio.dev/mcp` (1000+ integrations via one server). Auth facts verified against the live endpoint + [GitHub issue #3485](https://github.com/ComposioHQ/composio/issues/3485).

## Key facts

- **`ak_` keys NEVER work on this endpoint.** They are developer Platform keys (dashboard → API Keys page). Response: `401 {"error":"Authorization required","reason":"Bearer token rejected: not a valid AuthKit JWT for this resource, or no matching Composio account"}`. Expected behavior per Composio maintainers.
- **`ck_` consumer keys** (Composio "For You" / Connect dashboard → **Install** section, older name "AI Clients") work as `x-consumer-api-key` header. But the official Hermes route (composio.dev/hermes) is: **no headers at all → OAuth automatically**.
- OAuth discovery (RFC 8414):
  - Protected-resource metadata: `https://connect.composio.dev/.well-known/oauth-protected-resource` → `{"resource":".../mcp","authorization_servers":["https://login.composio.dev"],"bearer_methods_supported":["header"]}`
  - Auth server: `https://login.composio.dev/.well-known/oauth-authorization-server` → authorize `/oauth2/authorize`, token `/oauth2/token`, **dynamic client registration** `/oauth2/register`, PKCE `S256` only, `token_endpoint_auth_methods: ["none"]` (public client), scopes `openid profile email offline_access`.
  - Headerless request gets `WWW-Authenticate: Bearer error="unauthorized" ... resource_metadata="https://connect.composio.dev/.well-known/oauth-protected-resource"`.
- **Hermes' built-in MCP OAuth client can fail on this server** (gateway log: `MCP server '<name>' failed initial OAuth authentication, not retrying automatically: ... 401`). Working fallback: manual PKCE OAuth — `scripts/composio_oauth.py` (registers a dynamic client, opens `http://127.0.0.1:8345/callback` listener, saves token to `~/AppData/Local/hermes/composio_token.json`). Then drive the endpoint directly over JSON-RPC with `Authorization: Bearer <access_token>` (initialize → tools/list → tools/call via curl). Access token ~1h; refresh token saved alongside; token_endpoint_auth_method none + PKCE verifier are stored for refresh.
- Session tool catalogs are fixed at session start: tools connected via a mid-session gateway restart are NOT visible to the running session. Either start a new session or call the endpoint directly over JSON-RPC.

## Config.yaml repair after sed mistakes

Removing nested keys with sed is dangerous:
- `sed -i '/^    headers:$/d' config.yaml` deletes the `headers:` line for EVERY server at that indentation (e.g. both `figma` AND `21st`), orphaning their child keys (`x-api-key` at wrong indent) and breaking the whole file: gateway logs `Failed to process config.yaml — falling back to .env / gateway.json values. Error: while parsing a block mapping` and NO MCP servers load.
- `hermes config set` refuses to modify a config it cannot parse, so the file must be fixed with a direct scripted edit first (line-based rewrite, CRLF-safe — `\n`-only patterns fail on Windows files).
- Always validate after any direct config edit: `python -c "import yaml; yaml.safe_load(open(r'C:\Users\YOUR_USERNAME\AppData\Local\hermes\config.yaml', encoding='utf-8'))"` BEFORE restarting the gateway.
- If `hermes config set mcp_servers.X.headers.y "v"` writes a value that later displays masked (e.g. `ak_wXE...I_7t`) in grep/read_file output, the raw file may still hold the real value — tool output masks secret-shaped strings. Verify via a parser, not displayed output.

## Gateway restart sequence (this session's working order)

1. Fix/validate config.yaml (yaml.safe_load).
2. `hermes gateway restart`; wait ~10s; check `~/AppData/Local/hermes/logs/gateway-stdio.log` for the server's connect result.
3. Confirm tools via `hermes tools list` (config-level status only — does not prove live connection; the log does).
