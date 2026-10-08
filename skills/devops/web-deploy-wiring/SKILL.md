---
name: web-deploy-wiring
description: Use when wiring a GitHub repo to Vercel and/or Supabase.
---

# Web Deploy Wiring

Zero-to-live wiring: repo → host (Vercel) + database (Supabase) + verified production deploy.

Boundaries — do not duplicate these:
- Existing deploy broken (build fail, hydration, sitemap) → `vercel-deployment`
- Supabase auth/RLS/product depth, CLI gotchas → `supabase`
- Netlify → `netlify-deploy`
- Docker, CI pipelines, rollout strategies → `deployment-patterns`

## Always-on rules

1. **Probe both accounts before creating anything** — Supabase `list_projects` + `list_organizations`, Vercel `list_projects`. Reuse beats create. Supabase free tier caps at 2 active projects per user; the third `create_project` fails with a limit error and deleting an existing project is the only in-token fix.
2. **If the user's stated org/account is not visible to your tokens, surface it — never silently create elsewhere.** Offer the real options (invite the account, owner runs the schema SQL from a repo migration, reuse a visible project) in one batched question.
3. **Freeing a slot by deleting a project is the user's call** — present the exact data-loss tradeoff, and run the independent half of the work (host side, schema SQL draft) while waiting.
4. **Env vars exist before the first build.** A Vite/Next build without them bakes empty values into the bundle; setting them after means a wasted deploy. Set inline at project creation when the API allows.
5. **Never report `https://<project>.vercel.app` as the live URL without domain verification.** The bare name is globally first-come: a stranger's project can serve HTTP 200 on it. Read the project's aliases from the API and confirm the served bundle contains an app-unique string (a Supabase ref, an env-inlined URL).
6. **Client-fetched data needs a wait before DOM assertions.** An immediate check of rendered rows returns empty; `waitForSelector` on a real selector, and on timeout dump browser console errors instead of declaring the deploy broken.
7. **Commit the schema to the repo** (migration SQL in-repo or applied via MCP with the name recorded) so the DB state is reproducible by anyone who clones.

## Procedure

1. **Discover** — existing projects on both sides; repo stack (which subdirectory builds, what the backend stub does). An empty backend stub + frontend app means Supabase replaces the backend; say so, ship the frontend wiring, skip the stub.
2. **Decide reuse vs create** per side (org visibility, free slots, what already lives in the target DB).
3. **Database** — select/create project, apply schema as one migration (tables, indexes, RLS on every exposed table, minimal policies, seed rows), fetch project URL + publishable key via MCP.
4. **Host** — create project linked to the repo with env vars inline (or create then set env), `rootDirectory` for monorepo subdirs, framework pinned to the actual bundler. Apps that run as a persistent Node server (`http`/express) must be wrapped into a serverless handler — the recipe, the handler-export and `includeFiles` pitfalls, the manual-deploy REST call, and the no-token / session-cookie auth fallbacks are in `references/vercel-supabase-wiring.md`.
5. **Build** — trigger via empty commit (`git commit --allow-empty && git push`), poll deployments until READY/ERROR.
6. **Verify** — REST smoke of the DB (anon key read), HTTP status + alias + bundle-content check of the site, headless-browser render of the real data path.
7. **Wire the app** — minimal client module + first real query, build locally with the env vars set, push (auto-deploy), re-verify in browser.

Vendor-specific endpoints, payloads, and failure modes: [references/vercel-supabase-wiring.md](references/vercel-supabase-wiring.md)
