# Vercel Deploy Gotchas

Hit on this user's monorepo Vite/Express setups. Read before creating or redeploying a Vercel project.

## The agent usually cannot drive Vercel directly

The Vercel MCP token on this box is not authorized for the user's actual project scope (`attilasabiniano-5370s-projects`) — `list_teams` returns empty, project reads/creates 403. When a step needs the dashboard (create project, env vars, deployment protection), hand the user exact click-by-click instructions and the exact env values, then verify the result from the deployed URL with Playwright. Do not burn turns retrying the API.

## Creating a project from a monorepo

- Root Directory must be set to the frontend folder (`frontend`) at project creation, OR the repo needs a `vercel.json`. Dashboard-created projects often leave it empty → build "completes" but fails with `No Output Directory named "build" found`.
- The deterministic fix is a committed `vercel.json` in the frontend dir:

```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "outputDirectory": "dist",
  "buildCommand": "npm run build",
  "installCommand": "npm install",
  "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }]
}
```

- The `rewrites` entry is required for SPA routers (react-router BrowserRouter) or deep links 404 on refresh.
- Pushing the `vercel.json` fix triggers a fresh deploy automatically — no manual redeploy needed for file changes.

## Deployment Protection (SSO wall)

New projects under this team default to Deployment Protection ON: every visit redirects to a Vercel login (`vercel.com/login?next=...sso-api...`) even though the deployment itself succeeded. Diagnosis: `curl -sL <url>` follows to a vercel.com login page with a `dpl-` id in the HTML. Fix (user, dashboard): Settings → Deployment Protection → Production Deployments → Disabled.

## Environment variables

- The agent can rarely write them (same MCP scope wall) — give the user an exact two-row table (KEY / VALUE / environments=all) and have them paste it.
- VITE_ vars are baked at BUILD time: adding them in Settings does nothing until a NEW build runs.
- **"Redeploy" from an existing deployment reuses the build cache and does NOT re-inject newly added env vars.** After adding env vars, trigger a fresh build — push a new commit (even empty: `git commit --allow-empty -m "chore: pick up env vars" && git push`) — then verify the served bundle hash changed (`curl -s <url> | grep -oE 'assets/index-[^" ]*\.js'`) and the bundle contains the new value (grep for the supabase ref).
- Symptom of missing env vars in the served bundle: page renders an empty body, console shows `Error: supabaseUrl is required.`

## Verifying a deploy

1. `curl -s <prod-url> | grep -o '<title>[^<]*</title>'` — right app, right title.
2. Playwright pass against the PRODUCTION URL: real login, one write action per role, zero `pageerror`.
3. Confirm the GitHub commit status (`gh api repos/<o>/<r>/commits/main/status --jq .state`) says `success` — this catches failed builds that still serve the previous bundle.
