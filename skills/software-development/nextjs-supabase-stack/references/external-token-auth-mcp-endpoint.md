# External token auth through cookie-based server actions + MCP Streamable HTTP endpoint

Context: Next.js 16 route handler that must expose cookie-auth-only server actions
(`getEntity()` → `createClient()` → `createServerClient`) to external agents that present
`Authorization: Bearer <supabase access token>`. You cannot modify the actions.

## Why cookie injection works (verified from Next + supabase source)

- Route-handler `cookies()` returns the request's shared `RequestCookies`; `set()` mutates
  the internal `_parsed` Map (`next/dist/compiled/@edge-runtime/cookies/index.js`), so every
  later `cookies().getAll()` in the SAME request sees the write. `cookies()` always returns
  the same instance from the per-request store.
- TS note: `ReadonlyRequestCookies` (the `next/headers` return type) still includes `set`/
  `delete` via `Pick<ResponseCookies, 'set' | 'delete'>` — no cast needed in route handlers.
- supabase-js session recovery (`_recoverAndRefresh` / `__loadSession`): `_isValidSession`
  only checks the PRESENCE of `access_token` / `refresh_token` / `expires_at` keys. An
  unexpired stored session is trusted without re-validation — the JWT drives RLS on every
  PostgREST call via the auth header. So a hand-crafted session cookie is sufficient; no
  token round-trip is needed by the downstream client.

## @supabase/ssr cookie wire format (v0.12.x, read from dist source)

- Name: `sb-<project-ref>-auth-token` (ref = first label of the Supabase URL host, e.g.
  `kjsvupescrlywsdyywyu` from `https://kjsvupescrlywsdyywyu.supabase.co`).
- Value: `base64-` + base64url(UTF-8 JSON) of
  `{access_token, refresh_token, expires_in, expires_at, token_type, user}` (no padding).
- Chunking: values over 3180 chars split into `<name>.0`, `<name>.1`, … — there is NO plain
  `<name>` chunk when long; the reader (`combineChunks`) tries the plain name first, then
  joins `.N` chunks in order.
- `supabase.auth.setSession({access_token, refresh_token: ""})` THROWS
  `AuthSessionMissingError` — hand-encode the cookie instead.
- Expiry margin: supabase-js treats a session as needing refresh when
  `expires_at*1000 - now < EXPIRY_MARGIN_MS` (~90s); with an empty refresh token that
  refresh throws. Floor `expires_at` at `now + 300`s (the access JWT itself is still valid
  for the duration of the request — getUser(token) already proved it).

```ts
const session = {
  access_token: token,
  refresh_token: "",
  expires_in: Math.max(1, expiresAt - Math.floor(Date.now() / 1000)),
  expires_at: expiresAt,                       // Math.max(jwtExp, now + 300)
  token_type: "bearer",
  user,                                        // from getUser(token)
};
const value = "base64-" + Buffer.from(JSON.stringify(session), "utf8").toString("base64url");
const name = `sb-${supabaseUrlHost.split(".")[0]}-auth-token`;
const opts = { httpOnly: true, sameSite: "lax" as const, path: "/", maxAge: 3600,
               secure: process.env.NODE_ENV === "production" };
if (value.length <= 3180) cookieStore.set(name, value, opts);
else for (let i = 0, off = 0; off < value.length; i++, off += 3180)
  cookieStore.set(`${name}.${i}`, value.slice(off, off + 3180), opts);
```

Auth resolution order: cookie session first (`supabase.auth.getUser()` → user?), else
bearer token (`getUser(token)`), else 401. Actions called after injection pick the session
up via their own `createClient()`; `getEntity`'s React `cache()` is per-request so the
entity resolution is shared.

## Next 16 proxy.ts pitfall

`src/proxy.ts` (Next 16's middleware rename, `export function proxy`) with a catch-all
matcher redirects unauthenticated requests to `/login` BEFORE any route handler runs —
this kills external bearer agents AND CORS preflight (OPTIONS gets 307'd). Fix: exclude
the API path from the negative lookahead:
```ts
matcher: ["/((?!_next/static|_next/image|favicon.ico|api/mcp|.*\\.svg).*)"],
```

## MCP Streamable HTTP endpoint skeleton (spec 2025-06-18)

- Single POST route; JSON-RPC 2.0; responses `Content-Type: application/json` (JSON-only
  responses are spec-compliant — SSE not required). Stateless servers are fine: no
  `Mcp-Session-Id` needed.
- `initialize` → result `{protocolVersion: "2025-06-18", capabilities: {tools: {}},
  serverInfo: {name, version}}`.
- Notifications (no `id`; e.g. `notifications/initialized`) → HTTP 202 with EMPTY body;
  unknown-method notifications also 202. `id: null` counts as a notification (lenient).
- `ping` → result `{}`. `tools/list` → `{tools: [{name, description, inputSchema}]}`.
- `tools/call` → `{content: [{type: "text", text: JSON.stringify(result)}]}`; failures get
  `isError: true` with the structured `{error}` JSON in `text` (never raw throws).
- Errors: -32700 parse error (HTTP 400), -32600 invalid request (not jsonrpc 2.0 / no
  method), -32601 method not found, -32602 invalid params (incl. unknown tool name).
  Auth failure → HTTP 401 with a JSON-RPC error body (`{jsonrpc:"2.0", id:null, error:
  {code:-32001, message:"Unauthorized"}}`).
- JSON-RPC batch (array body) → array of responses, notifications dropped; all-notification
  batch → 202.
- CORS: `Access-Control-Allow-Origin: *`, `Allow-Methods: GET, POST, OPTIONS`,
  `Allow-Headers: Authorization, Content-Type, x-cashy-token`; OPTIONS → 204.
- GET on the same path → discovery JSON `{name, version, protocol: "MCP Streamable HTTP",
  auth: [...], tools: [...]}`.

## Caveat

The bearer-injection mechanics above are verified from library/dist source (Next
RequestCookies, @supabase/ssr chunking + base64url, supabase-js session recovery), but the
full flow (inject → action runs authenticated) had NOT been live-tested end-to-end when
written. Smoke-test the first real token request before declaring it production-ready.

## Security audit notes (ECC security-reviewer pass, verified against installed dist)

Source locations that pin the wire format (don't re-derive — read these):
- Chunking: `node_modules/@supabase/ssr/dist/main/utils/chunker.js` — `MAX_CHUNK_SIZE =
  3180`; chunk names `${key}.${i}` from `.0`; `combineChunks` tries the PLAIN name first,
  then joins `.N` in order. Chunk size is measured on `encodeURIComponent(value).length`
  — identical to raw length ONLY because base64url chars need no escaping; any other
  cookie payload must account for the difference.
- Decode: `.../utils/cookies.js` — `BASE64_PREFIX = "base64-"`; undecodable/JSON-invalid
  chunked values are treated as ABSENT (fail-closed, no crash).
- Storage key: `node_modules/@supabase/supabase-js/dist/index.mjs` —
  `` `sb-${new URL(url).hostname.split(".")[0]}-auth-token` ``. Route code must use the
  same derivation (`hostname`, not `split(".")[0]` on the raw string, to also handle
  ports/lowercasing).
- Expiry margin: `node_modules/@supabase/auth-js/dist/main/lib/constants.js` —
  `EXPIRY_MARGIN_MS = 90_000` (3 ticks × 30s); refresh with empty `refresh_token` throws.

Findings (all confirmed against source; fixes in the umbrella SKILL.md):
1. **Response cookie materialization** — `cookies().set()` in a route handler also emits
   `Set-Cookie` on the response: the bearer token becomes a 1h httpOnly cookie on the app
   origin (bearer holder → browser session holder). Fix: per-request in-memory storage
   adapter instead of the shared cookie store:
   ```ts
   // inject into a local Map, never the response cookie store
   const store = new Map<string, { name: string; value: string; options?: any }[]>()
   // getAll: () => [...store.get("all") ?? [], ...cookieStore.getAll()]
   // setAll: (cookies) => store.set("all", cookies)   // request-scoped only
   ```
2. **Fabricated `expires_at`** — `max(jwtExp, now+300)` can exceed the JWT's real exp
   (token with <5 min left passes `getUser(token)`, then PostgREST rejects the query).
   Use real `exp`; reject tokens with <60s remaining; `maxAge` = remaining lifetime.
   `jwtExp`'s `now+3600` fallback is dead code (GoTrue rejects unparseable JWTs).
3. **Forgery-safe** — fake cookie `user` objects are never trusted: PostgREST validates
   the cookie's `access_token` JWT on every query (RLS `auth.uid()`), and `getUser()`
   re-validates server-side. The cookie is transport; RLS is the boundary.
4. **CORS `*` + cookie** — browsers refuse credentials mode with `*`, so cookie auth is
   same-origin-only; cross-origin Set-Cookie is dropped. External browser MCP clients are
   bearer-only. `Access-Control-Max-Age` missing → preflight every call (perf only).
5. **DoS** — JSON-RPC batches are unbounded and route handlers have no default body
   limit: cap batch (~20) + body size, add per-user rate limiting.
6. **Prompt injection to external agents** — tool results (transaction notes) are
   user-controlled strings with no untrusted-data warning in tool descriptions; the
   `[FINANCIAL CONTEXT]` framing in `/api/ai/chat` does not cover MCP tool output.
7. **BYOK SSRF** — `ai_settings.base_url` fetched verbatim server-side; allowlist scheme
   and block private/link-local/loopback hosts.
