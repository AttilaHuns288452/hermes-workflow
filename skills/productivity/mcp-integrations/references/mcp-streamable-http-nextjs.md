# Exposing a Next.js + Supabase app as an MCP server (Streamable HTTP)

Verified end-to-end 2026-08-05 on CashFlow OS (`/api/mcp`). Covers the SERVER side —
the inverse of this skill's usual Hermes-as-client focus. Real MCP clients (Claude
Desktop, Cursor, OpenCode, Cline) connect to a Streamable HTTP endpoint.

## Architecture

Single Next.js route handler (`src/app/api/mcp/route.ts`), POST = JSON-RPC 2.0,
`Content-Type: application/json` responses (SSE only needed for server-initiated
messages — skip it, JSON responses are spec-compliant). `export const dynamic = "force-dynamic"`.

Method set that makes clients happy:
- `initialize` → `{ protocolVersion: "2025-06-18", capabilities: { tools: {} }, serverInfo: { name, version } }`
- `notifications/initialized` → HTTP 202, no body
- `ping` → `{}`
- `tools/list` → `{ tools: [{ name, description, inputSchema }] }`
- `tools/call` → `{ content: [{ type: "text", text: JSON.stringify(result) }], isError: true? }`
- Unknown method → `-32601`; parse error → `-32700`; bad params → `-32602`; unauthenticated → `-32001` + HTTP 401
- Notifications (id null/undefined) → 202 with no body; JSON-RPC batches → array of responses

Tool implementations wrap existing server actions (they already do `getEntity()` +
RLS scoping) — never re-implement queries in the route.

## Auth: cookie OR bearer, without forking the data path

The app's server actions read the Supabase session from cookies. For external agents
(bearer token), INJECT the validated session into the request's cookie store so the
same cookie-based actions stay RLS-scoped:

1. `supabase.auth.getUser(token)` validates the bearer JWT.
2. Mirror @supabase/ssr's cookie format: `"base64-" + base64url(JSON(session))`,
   chunked at 3180 chars into `sb-<ref>-auth-token.0/.1/...` (ref = first subdomain
   label of the Supabase URL). Session JSON: `{ access_token, refresh_token: "", expires_in, expires_at, token_type: "bearer", user }`.
   Floor `expires_at` at `now + 300` so supabase-js's expiry margin never rejects a valid token.
3. `cookies().set(...)` per chunk — Next's RequestCookies mutates the per-request
   map, so later reads in the same request (getEntity → createClient) see the session.

Accept `Authorization: Bearer <supabase access token>` AND a custom header
(`x-cashy-token`) — some clients let you set headers, some only auth.

## CORS

`Access-Control-Allow-Origin: *`, `Access-Control-Allow-Methods: GET, POST, OPTIONS`,
`Access-Control-Allow-Headers: Authorization, Content-Type, x-cashy-token`,
OPTIONS preflight → 204. External desktop agents connect cross-origin.

## ⚠️ The middleware 307 trap (broke everything first)

If the app has a Supabase proxy/middleware (`src/proxy.ts`) that redirects
unauthenticated requests to `/login`, it 307s `/api/mcp` BEFORE the route runs —
killing BOTH the 401 JSON-RPC semantics AND the OPTIONS preflight. External agents
just fail to connect. Fix: exempt the path in the proxy's public allowlist
(`request.nextUrl.pathname.startsWith("/api/mcp")`) — the route is its own gate.
Test: unauthenticated POST must return 401 JSON, not 307.

## E2E verification (playwright, proves the external-agent path)

```js
// login → pull session JWT from httpOnly cookies → Bearer tools/list + tools/call
const ctx = await browser.newContext();
await page.goto(APP + "/login"); await page.fill(...); await page.click('button[type="submit"]');
await page.waitForURL("**/dashboard");
const sb = (await ctx.cookies()).filter(c => c.name.startsWith("sb-") && c.name.includes("auth-token"))
  .sort((a,b) => a.name < b.name ? -1 : 1).map(c => c.value).join("");
const token = JSON.parse(Buffer.from(sb.replace(/^base64-/, ""), "base64url").toString("utf8")).access_token;
// then fetch POST /api/mcp with Authorization: Bearer token → initialize, tools/list, tools/call
```

Assert `tools/call` returns the REAL user's scoped data (matches a known dashboard
value) — proves RLS + entity scoping hold on the bearer path. Delete the test script
after; it contains the test password.

## GET discovery (nice-to-have)

`GET /api/mcp` → `{ name, version, protocol: "MCP Streamable HTTP", auth: ["cookie","bearer"], tools: [...] }` — cheap health/discovery for humans and clients.

## Hardening (ECC review round, same session)

- **Rate limit per user:** copy the in-memory Map sliding-window limiter (20 req/min) from the app's AI chat route; key by the RESOLVED user id (make `resolveAuth` return the id, not a boolean). 429 body: JSON-RPC error `-32029` + HTTP 429.
- **Cookie lifetime = JWT lifetime:** set `maxAge: Math.max(60, expiresAt - now)` — the injected session cookie must never outlive the bearer token it materializes (defense-in-depth; a stolen-token → persistent-cookie escalation stays bounded by the JWT expiry).
- **Notifications: never respond.** JSON-RPC 2.0 §2.3 — return `null` (→ HTTP 202) for ANY method whose `id` is null/undefined, not just unknown methods. A response to a notification is a protocol violation some clients reject.
- **Arg validation:** sanitize tool args with a `Number.isFinite` guard (naive `Math.floor(v) || dflt` swallows legitimate `0`).
- Deferred (accepted tradeoff): full per-request in-memory storage adapter instead of cookie materialization — the cookie path is bounded by JWT expiry + httpOnly + SameSite=Lax; re-evaluate on the next Next.js upgrade (invariant pinned in a comment).
