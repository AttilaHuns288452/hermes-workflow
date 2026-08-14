# MCP Endpoint — Verified E2E Recipe (cashflow-os, 2026-08-05)

Live-tested against the MCP Streamable HTTP endpoint (`/api/mcp`, protocol 2025-06-18)
that wraps Supabase cookie-based server actions with bearer-token auth. The whole
external-agent path was proven end-to-end; use this recipe instead of re-deriving it.

## The E2E proof (playwright script that passed)

1. Login as a real user in a browser context.
2. Read the Supabase session cookies — they are httpOnly, so use
   `context.cookies()` (playwright sees httpOnly), NOT `document.cookie`.
   The session cookie is chunked: `sb-<project-ref>-auth-token` plus
   `.0`, `.1`, … when long. Sort by name, join values.
3. Decode: `JSON.parse(Buffer.from(value.replace(/^base64-/, ""), "base64url").toString("utf8"))`
   → `access_token` (the JWT). This is the exact wire format @supabase/ssr uses.
4. Call the endpoint with `Authorization: Bearer <jwt>`:

```js
const call = (body) => page.evaluate(async (b) => {
  const res = await fetch("/api/mcp", {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: "Bearer " + b.token },
    body: JSON.stringify(b.body),
  });
  return { status: res.status, body: await res.json() };
}, { token, body });
```

5. Expected results (all verified):
   - `initialize` → 200 `{ protocolVersion: "2025-06-18", capabilities: {tools:{}}, serverInfo }`
   - `tools/list` → 200 with the full tool list
   - `tools/call dashboard_summary` → 200 with the REAL user's data, RLS-scoped
     (matched live DB numbers: entity currency, net worth, month totals)
   - no auth / garbage bearer → 401 JSON-RPC `{ code: -32001 }`
   - `OPTIONS` preflight → 204 with CORS headers

## Two traps found while making this work (both fixed)

### 1. Auth middleware 307s the MCP route before it can answer
The app's `proxy.ts` (Next 16 middleware) redirects unauthenticated requests to
`/login` — so an external agent's first POST got a 307 and the OPTIONS preflight
never reached the route (CORS broken entirely). The MCP route does its own auth
(cookie OR bearer), so it must be exempted from the middleware gate:

```ts
// proxy.ts isPublicPage:
request.nextUrl.pathname.startsWith("/api/mcp")  // route self-authenticates
```

Symptoms if you skip this: GET discovery 307s, POST 307s, preflight 307s — every
MCP client fails with redirect errors instead of clean 401s.

### 2. Playwright login races React hydration
Clicking the login submit before React hydrates submits the FORM natively
(GET with `?email=…&password=…` in the URL, no navigation). Always
`waitForTimeout(~1500-2000ms)` after `domcontentloaded` on auth pages before
filling/interacting in screenshot or E2E scripts.

## Hardening applied after the ECC security pass (do the same)

- Cookie `maxAge` = the JWT's actual remaining life (`Math.max(60, expiresAt - now)`),
  never a flat 3600 — the injected session cookie must not outlive the token.
- Per-user in-memory rate limit (same Map pattern as `/api/ai/chat`, 20/min) keyed
  by the resolved user id — `tools/call` runs multiple Supabase queries per hit.
- JSON-RPC §2.3: never respond to notifications (id-less requests) — return 202/no
  body; only respond to id-carrying requests.
- `clampInt`-style helpers: guard with `Number.isFinite(Number(v))` before
  `Math.floor` — `|| dflt` silently swallows a legitimate `0`.
- Read the `nextjs-supabase-stack` SKILL.md "External bearer tokens" section for
  the injection mechanics + remaining caveats (response Set-Cookie, exp margin).
