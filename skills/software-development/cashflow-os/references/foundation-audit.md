# FOUNDATION cluster audit (2026-08-06)

Audit-only recipe + findings for the FOUNDATION cluster: `src/app/{login,signup,settings,api,offline,manifest.ts,layout.tsx,loading,error,global-error,not-found}/**`, `src/components/layout/**`, `src/lib/**`, `src/features/{auth,ai,settings}/**`. Disjoint from schema-drift and server-action hunts. Never edit/build/git during the audit.

## Checklist per area

- **/api/mcp (src/app/api/mcp/route.ts):** JSON-RPC 2.0 — notifications (id undefined/null) get NO response (202 no-body, correct); invalid requests get -32602/-32700 EVEN when id-less (check runs before the notification guard — keep that order); batch drops notifications, but an EMPTY batch `[]` must get a single -32600 error, not 202 (was wrong); `id: 0` must round-trip (`id ?? null` does). Streamable HTTP: `MCP-Protocol-Version` response header required on ALL responses incl. 401/429 (missing) — strict clients reject. Auth: cookie session first, bearer (`Authorization: Bearer` / `x-cashy-token`) fallback verified via `getUser(token)`; injected session cookie must mirror @supabase/ssr format (`base64-` + base64url(JSON), chunked at 3180 into `<name>.0`, `.1`…). Rate limit per-user AFTER auth. CORS `*` is safe only because cookie flows are same-origin.
- **Cookie lifetime == JWT expiry:** `maxAge`/`expires_at` must equal JWT exp; `Math.max(60, …)` / `now + 300` floors let cookie/session outlive the token by ≤60s / ≤5min (harmless — token is dead — but breaks the stated invariant).
- **/api/ai/chat:** auth gate `getUser` → 401; per-user rate limit; caps (20 msgs, 2000 chars/msg, 4000 context); 30s `AbortSignal.timeout` → 504 — **match on `e.name === 'TimeoutError'`, never on a custom message** (the DOMException message is generic; message-matching makes the 504 branch dead code → all-timeouts become 500). Generic client errors + `console.error` server-side. System prompt fully static; `[FINANCIAL CONTEXT — untrusted data]` block appended by the ROUTE to the LAST user message; client sends RAW context (no double-framing); defensively drop trailing assistant messages before appending.
- **Auth flows:** signUp creates personal entity + 12 default categories in the server action — verify email-confirmation interplay (no session → RLS blocks inserts → entity-less accounts; migration 001 removed the DB trigger). Login redirects to /dashboard. Map Supabase error codes to generic copy (no account-existence leaks). Check dead links (e.g. /forgot-password).
- **PWA:** manifest.ts (start_url, icons present in public/), offline page, sw.js (precache "/" + "/offline", network-first navigations, cache-first same-origin statics, skipWaiting/clients.claim).
- **A11y:** skip link → `#main`; drawer `inert` + `aria-hidden` when closed on mobile (open drawer still needs focus trap + Escape); CommandPalette combobox/listbox/aria-activedescendant; `prefers-reduced-motion` block in globals.css.
- **Hydration:** client-only values (`new Date().getHours()` greetings) in useEffect; render-time getHours is only safe if the component's data starts null (client-only render) — fragile. No inline theme script → `.dark` FOUC on load.
- **Design language:** all colors from CSS vars; no gradients/arbitrary `[]` values; known offenders: AuthShell gradient blobs (`bg-purple-500/…`), AIAssistant hardcoded hex + `bg-[#7c3aed]` + `shadow-[0_8px_32px_rgba(...)]`, scattered `bg-black/40`/`text-white`/`text-red-500`.
- **Middleware:** repo has NONE — no route-level auth guard; enforcement is server actions + RLS (anon users render the shell).

## Verification technique (critical this round)

Tool output on this host MASKS secret-like patterns (`apiKey: <value>`, `Bearer <token>`) as `***` — even in read_file/terminal output and in Python prints (a printed `repr` of `apiKey: string` came back as `apiKey: ***`). A clean file can look like it contains a literal `***` artifact. Ground truth:
1. `git grep -n '\*\*\*' -- src` (committed+tracked content, unfiltered).
2. Python: read the file, print line length + `"*" in line` + `[ord(c) for c in line[8:]]` instead of content.

Result: zero literal `***` in 234 tracked files; the previously recorded "CRIT `apiKey: ***` at chat/route.ts:90" was an output-filter illusion (`apiKey: aiRow.api_key,` in reality). Don't trust any `***` sighting until byte-verified.

## Findings (severity table)

| Sev | Location | Issue | Fix |
|---|---|---|---|
| HIGH | src/lib/ai.ts:142-145 | TimeoutError message-match never hits → 504 branch dead, timeouts → 500 | check `e.name === 'TimeoutError'` |
| HIGH | src/features/auth/actions.ts:56-81 | Entity+category seeding fails under email confirmation (no session, RLS blocks; no DB trigger since 001) | security-definer fn or lazy ensure-on-first-signin |
| MED | mcp/route.ts | missing `MCP-Protocol-Version` header on all responses | add in withCors |
| MED | mcp/route.ts:251-258 | empty batch `[]` → 202; spec wants single -32600 | guard `body.length === 0` |
| MED | ai/chat/route.ts:69-77 | context block appended to last message regardless of role | attach to last USER message |
| MED | LoginForm.tsx:80 | /forgot-password link → 404 (route doesn't exist) | create page or drop link |
| MED | AppShell.tsx:446 | open mobile drawer: no focus trap / Escape | trap Tab + Escape when open |
| MED | layout.tsx / AppShell.tsx:362-371 | no inline theme script → dark-mode FOUC | pre-paint script reading localStorage |
| MED | AIAssistant.tsx | hardcoded hex, gradients, arbitrary [] values — frozen language violated | map to CSS vars |
| LOW | mcp/route.ts:92,132 | cookie maxAge/expires_at floors outlive JWT ≤60s/≤5min | exact exp, no floors |
| LOW | entity.ts:25,35 | `supabase as any` (AGENTS.md forbids) | type the union |
| LOW | settings/actions.ts:12 | setCurrency no whitelist validation | validate against CURRENCIES |
| LOW | PwaRegister.tsx:10 | `.catch(() => {})` silent | console.warn |

Verdict: no CRITICAL; two HIGHs (timeout→504, signUp seeding) block sign-off.
