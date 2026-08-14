# MCP Streamable HTTP server inside a Next.js app (`/api/mcp`)

Verified pattern (cashflow-os, Aug 2026): expose an authenticated Next.js app as a real MCP server so external agents (Claude Desktop, Cursor, OpenCode) can query the user's data. Auth stays RLS-scoped because the tools reuse the app's own server actions.

## Route skeleton (`src/app/api/mcp/route.ts`, `export const dynamic = "force-dynamic"`)

Single POST endpoint, JSON-RPC 2.0:
- `initialize` → `{protocolVersion: "2025-06-18", capabilities: {tools: {}}, serverInfo: {name, version}}`
- `notifications/initialized` (no id) → HTTP 202, **no body**
- `ping` → `{}`
- `tools/list` → full schemas (`{name, description, inputSchema}`)
- `tools/call` → `{content: [{type: "text", text: JSON.stringify(result)}]}` + `isError: true` when result is null/`{error}`/throw
- Errors: `-32700` parse, `-32600` invalid request, `-32601` method not found, `-32602` invalid params, `-32001` unauthorized
- **Never respond to notifications** (id null/undefined) — return null → 202
- JSON responses are spec-compliant; SSE only needed for server-initiated messages (skip)

## Auth: cookie OR bearer (the tricky part)

1. Cookie session first: `createClient()` from `@/lib/supabase/server`, `getUser()`.
2. Bearer (`Authorization: Bearer <supabase access token>` or `x-cashy-token`): validate via `supabase.auth.getUser(token)`.
3. Then **inject the session as cookies** so the existing cookie-based server actions (getEntity → createClient) run authenticated: `base64-` + base64url(JSON session `{access_token, refresh_token: "", expires_in, expires_at, token_type, user}`), chunked at 3180 chars into `sb-<ref>-auth-token`, `sb-<ref>-auth-token.0`, ... (mirror @supabase/ssr exactly).
4. Cookie flags: httpOnly, SameSite=Lax, secure in prod, `maxAge = JWT remaining life` (never longer).
5. **INVARIANT comment in code**: relies on Next.js `RequestCookies.set()` mutating the per-request cookie map that @supabase/ssr reads lazily via `getAll()` — re-verify on every Next.js upgrade.

## Middleware exemption (forgetting this breaks everything)

The app's `proxy.ts` (middleware) 307-redirects unauthenticated requests to /login. `/api/mcp` must be exempted (`pathname.startsWith("/api/mcp")` in the public list) or external agents lose BOTH the 401 semantics AND the OPTIONS preflight (CORS dead). The route is its own gate.

## CORS + rate limit

- `Access-Control-Allow-Origin: *`, allow `Authorization, Content-Type, x-cashy-token`; OPTIONS → 204.
- Per-user sliding-window rate limit (Map, 20/min, same pattern as the AI chat route).

## E2E verification (playwright)

1. Login as test user (wait 2-4s after page load — click before React hydration submits the form natively as GET).
2. Read the chunked `sb-*-auth-token*` cookies, join, strip `base64-`, base64url-decode → `access_token`.
3. POST `initialize` → `tools/list` → `tools/call` with `Authorization: Bearer <token>`; expect 200 + **real RLS-scoped data** (e.g. dashboard_summary returns the actual user's net worth).
4. Also assert: no-auth → 401 JSON-RPC, OPTIONS → 204, GET → discovery JSON.

## Tool layer

Wrap existing server actions (`getDashboardData`, `apiGetTransactions`, `apiGetNetWorth`, categories/budgets/goals/debts) — entity scoping via `getEntity()` is inherited for free. Cap list results (e.g. 100). `clampInt` guard: use `Number.isFinite` (a falsy-`||` swallows legitimate 0).
