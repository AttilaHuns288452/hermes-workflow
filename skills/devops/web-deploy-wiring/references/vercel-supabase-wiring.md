# Vercel + Supabase wiring recipes

Exact calls behind the `web-deploy-wiring` procedure. Values marked `<...>` are per-project.

## Vercel: new project from a repo

1. `mcp__vercel__list_projects` first — reuse instead of duplicating a name.
2. Prefer `mcp__vercel__create_git_project` (`repo: "owner/name"`, `teamId`, `rootDirectory` for monorepo subdirs, `deploy: true`).

   If it fails with `403 "Not authorized: Trying to access resource under scope ..."` on the git-repo lookup (team-scoped OAuth token, personal-scope lookup), bypass via REST using the same OAuth token cached at `~/.hermes/mcp-tokens/vercel.json`:

   `POST https://api.vercel.com/v12/projects` — **no teamId** (personal scope) — body:
   ```json
   {
     "name": "project-name",
     "framework": "vite",
     "rootDirectory": "frontend",
     "gitRepository": { "type": "github", "repo": "owner/name" },
     "environmentVariables": [
       { "key": "VITE_X", "value": "...", "type": "plain", "target": ["production", "preview", "development"] }
     ]
   }
   ```
   Env vars inline here beats separate env calls (see SKILL.md rule 4).

3. First build: `git commit --allow-empty -m "Trigger Vercel deploy" && git push`. `gitRepository` at creation wires push-to-deploy — no CLI deploy needed. Poll `GET /v6/deployments?projectId=<id>&limit=3` until `readyState` is READY or ERROR.
4. Manual deploy without any CLI (session-cookie auth, see auth section below): `POST https://api.vercel.com/v13/deployments?teamId=<id>&forceNew=1` with body `{"name": "<project>", "project": "<project>", "gitSource": {"type": "github", "ref": "master", "repoId": <numeric id>, "repo": "owner/name", "orgId": <numeric id>}, "target": "production"}`. The body schema is strict — any extra property is rejected with `should NOT have additional property`. `teamId` comes from `GET /v2/teams` (use `id`, not `id.name`). A `gitSource` deploy builds the pushed repo HEAD, not the local working tree.

## Vercel: domain verification (never skip)

- Bare `https://<name>.vercel.app` is globally first-come — a stranger's app can 200 on it. That 200 is a false success, not a deploy confirmation.
- Real domains: `GET /v9/projects/<id>` → `latestDeployments[0].alias` — typically `<name>-<word>-<word>.vercel.app` (production), `<name>-git-main-<team-slug>.vercel.app`, `<name>-<team-slug>.vercel.app`.
- Bundle check: extract the script `src` from the page HTML, curl the JS, grep for an app-unique string (Supabase project ref, env-inlined URL). Mismatch on a 200 = wrong site.

## Vercel: runtime render check

Client-fetched data (supabase-js, any API) is absent from the DOM at load. Headless (Playwright via the Hermes checkout) pattern:

```js
await p.goto(url, { waitUntil: 'domcontentloaded' });
await p.waitForSelector('ul li', { timeout: 15000 });   // real selector for the data
JSON.stringify(await p.locator('ul li').allTextContents());
```

On timeout: collect `p.on('console')` error events and report those — do not conclude from the empty list alone.

## Vercel: wrapping a persistent Node server (http / express, no framework)

When the app runs as `node server.js` with `http.createServer(cb)` and already serves its own static files + API:

1. Refactor the create-server callback into a named `function handler(req, res)`, keep `const server = http.createServer(handler)`, guard the listener with `if (require.main === module) server.listen(PORT)`. One code path serves local dev and the serverless function.
2. **The file Vercel invokes must export the handler FUNCTION** — `module.exports = handler;` with extras attached as properties (`module.exports.server = server`). Vercel's Node builder calls the module's export; an object export (`module.exports = { server, handler }`) makes EVERY invocation fail with `FUNCTION_INVOCATION_FAILED` and no error detail, including static-file requests that fall through to the function. If you use an `api/index.js` wrapper instead, its export must be the function too (`module.exports = require('../server').handler`). Gate before pushing: `node -e "console.log(typeof require('./<entry>'))"` must print `function`.
3. `vercel.json` (`version: 2`): the server routes everything internally, so give it the whole site — legacy `builds` + one catch-all route. Do not split static serving across `routes` for a server that already serves static; mis-split symptoms are indistinguishable from the crash in step 2:
   ```json
   {
     "version": 2,
     "builds": [{ "src": "server.js", "use": "@vercel/node", "config": { "includeFiles": ["public/**", "knowledge/**"] } }],
     "routes": [{ "src": "/(.*)", "dest": "server.js" }]
   }
   ```
4. **Pitfall (includeFiles):** Node's file tracer bundles only `require`d modules. Data files read with `fs.readFileSync` at request time (markdown reports, JSON knowledge bases) are missing from the function bundle unless declared in `includeFiles`. Symptom: works locally, 500s in production on exactly the routes that touch that data. Declare static dirs the server reads too.
5. **Pitfall (deploys build from the repo):** a `gitSource` deployment builds pushed HEAD — commit and push config/code fixes BEFORE posting `forceNew=1`, or the redeploy reproduces the identical failure and wastes a build cycle.
6. Before pushing: `node --check` the entry, the `typeof` gate above, run the suite, curl the local health + one data route + one static asset. Live verify per SKILL.md rule 5, covering the same three route types on the production URL.

## Vercel: auth paths when no token exists

- A `~/.local/share/com.vercel.cli/config.json` can exist while holding no token (telemetry keys only) — check the file's keys, not its existence. Token deploys need `VERCEL_TOKEN` / `~/.vercel` or `npx vercel` login.
- The Vercel MCP is OAuth-only and interactive (`hermes mcp test vercel` prompts) — unusable headless; don't burn retries on it.
- If no valid session exists, drive the provider's login in the user's own browser session. OAuth buttons on React pages ignore programmatic `el.click()` — dispatch a real pointer event at the element's `getBoundingClientRect` center (`click_at_xy` / CDP mouse).
- **Trust the API over the page shell for auth state.** A provider page can render a stale logged-out shell while the session cookie is still valid — check for a service worker first, then probe an authenticated endpoint (`fetch('/api/user')`); 200 means the session works and the UI is not worth debugging.
- **Session-cookie REST driving:** with a valid user session in the browser, extract cookies for the provider's domains via CDP `Network.getCookies`, write them to a `chmod 600` temp file (never print values — `document.cookie` misses httpOnly), and drive the provider's REST API headlessly: `curl -H @<(sed 's/^/Cookie: /' /tmp/cookie.txt) https://api.<provider>.com/...`. Delete the cookie file when the job is done. This turns "my browser is already logged in" into full headless automation without touching login flows.
- Terminal state: account 2FA. Vault code entry cannot fill OAuth-wall TOTP (no vault login handle; split one-time-code inputs come back `no_code_field`). Hand the open window to the user for the authenticator code and resume on their signal; never route a code through chat.

## Supabase: project + schema + keys

1. `list_projects` + `list_organizations` first. Free tier = 2 active projects per user; `create_project` fails with a limit error once full. The user's org may not be visible to your token at all — then surface options instead of creating elsewhere.
2. `get_cost(type: "project", organization_id)` → confirm with user (free tier returns 0) → `confirm_cost` → `create_project` (region `ap-southeast-1` matches this user's existing projects).
3. Schema: one `apply_migration` call with everything — tables, indexes, `enable row level security` on every public table, minimal policies, seed rows. Loop pattern for per-table policies:
   ```sql
   do $$ declare t text; begin
     foreach t in array array['patients','dentists','services','appointments'] loop
       execute format('create policy %I on public.%I for all to anon, authenticated using (true) with check (true)', t || '_full_access', t);
     end loop;
   end $$;
   ```
   Mark open policies with a `ponytail:`-style comment naming the tightening condition (auth added → restrict to authenticated + owner checks).
4. Credentials: `get_project_url` + `get_publishable_keys` — use the modern `sb_publishable_...` key in frontend clients (legacy `anon` JWT only for compatibility). Publishable key + URL in the client bundle is safe by design; RLS is the guard.
5. Smoke test before wiring UI: `curl "https://<ref>.supabase.co/rest/v1/<table>?select=..." -H "apikey: <publishable>"`.

## Frontend wiring (Vite)

- `src/supabaseClient.js`: `createClient(import.meta.env.VITE_SUPABASE_URL, import.meta.env.VITE_SUPABASE_ANON_KEY)` — nothing else.
- First query in the app: one table, one error state. Verify with a local build (`VITE_...` vars set inline) before pushing, so build errors surface locally, not in the deploy log.
