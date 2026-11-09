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
8. **Schema and the code that reads it ship in one order: migration live and verified first, then the frontend.** A build succeeds and the deploy reports READY while every request touching the new column fails — deploy success proves the bundle served, not the schema beneath it. Object-by-object live probes are in `supabase-mcp-workflows` → "Verifying an applied migration".
9. **Secret-shaped literals are masked/truncated at `write_file` and echoed tool output, but a secret the user already provided CAN be placed where it is needed via `execute_code`.** `write_file`, `read_file`, and `terminal` echo render `sb_secret_…`, `sb_publishable_…`, `Bearer …`, `apikey: X` as truncated or `***` — a probe file written to hold a key silently contains a truncated value and fails with a misleading `401 Invalid API key`, which reads as a bad credential rather than a self-inflicted one. To USE a secret the user already gave you, build it at runtime INSIDE `execute_code` (string concat like `"sb_secret_" + rest`, or base64-decode of an innocuous literal) — `execute_code` does not mask it, and you can confirm integrity with `len()` + last-6 chars, never the full value. Do not trust a first read of a pasted key's length: a value copied from chat or a dashboard can carry extra trailing characters and fail `Invalid API key` even though it looks right — validate it against the provider's own key-listing endpoint before wiring it in (see `supabase` → key model). When the user has NOT provided the value, ship code that reads `process.env.X` / `import.meta.env.VITE_X`, write a placeholder-only `.env.example` naming each var and its host type (Secret vs Config), and hand the user the exact key names to paste. Verify wiring by app behavior (length, status codes), never by echoing a value.
10. **Moving a GitHub Pages site to Vercel: branch the bundler config on `process.env.VERCEL`.** A Vite config pinned to Pages (`base: "/<repo>/"`, `outDir: "docs"`) makes every Vercel deploy build to the wrong directory with the wrong asset paths, so the deploy fails or serves unstyled HTML. Keep one config serving both targets: `base: "/"` + `outDir: "dist"` when `VERCEL` is set, Pages values otherwise. Add `vercel.json` SPA rewrites (`/(.*) -> /index.html`) for clean deep links, then confirm assets still serve as JS/CSS and are NOT rewritten.
11. **A serverless proxy owns the trust boundary for a paid third-party API.** Validate query/marketplace/id and return 4xx before spending upstream quota; bound pagination and cache identical requests. Never accept a 2xx blindly — external APIs return `200` with `{message}` or an empty object, so gate on the expected shape (a real id/title, a products array) and return 404/502 otherwise; a fake-empty payload rendered as success is a silent failure. Separate "bad key" from "provider outage" with a free, non-consuming endpoint on the same host (e.g. `/account/usage`): if it succeeds with the same key and header, the key and host are fine and the failure is upstream. Contract discovery, the pure-layer split, and the full recipe: [references/third-party-api-proxy.md](references/third-party-api-proxy.md).
12. **A brief that presumes prior work is a hypothesis, not a starting state.** Before planning or implementing, verify every "already integrated / already works" claim against the real repo — dependency in `package.json`, config file present, a real code path (not a mock with a `// mock` comment), a migration that was actually applied. A prior report asserting an integration exists will otherwise compound into a plan built on nothing. Report the measured state first when it contradicts the brief; do not quietly re-implement around a false premise. **This includes a report produced earlier in this same conversation by you or another agent.** A fabricated "everything works" summary is indistinguishable from a real one without a repo probe; when a pasted or prior-turn report lists features (auth wired, DB integrated, scraper live), grep the real code path for each before building on it, and when the probe contradicts the report, say so plainly and correct the record before continuing.

## Procedure

1. **Discover** — existing projects on both sides; repo stack (which subdirectory builds, what the backend stub does). An empty backend stub + frontend app means Supabase replaces the backend; say so, ship the frontend wiring, skip the stub.
2. **Decide reuse vs create** per side (org visibility, free slots, what already lives in the target DB).
3. **Database** — select/create project, apply schema as one migration (tables, indexes, RLS on every exposed table, minimal policies, seed rows), fetch project URL + publishable key via MCP.
4. **Host** — create project linked to the repo with env vars inline (or create then set env), `rootDirectory` for monorepo subdirs, framework pinned to the actual bundler. Apps that run as a persistent Node server (`http`/express) must be wrapped into a serverless handler — the recipe, the handler-export and `includeFiles` pitfalls, the manual-deploy REST call, and the no-token / session-cookie auth fallbacks are in `references/vercel-supabase-wiring.md`.
5. **Build** — trigger via empty commit (`git commit --allow-empty && git push`), poll deployments until READY/ERROR.
6. **Verify** — REST smoke of the DB (anon key read), HTTP status + alias + bundle-content check of the site, headless-browser render of the real data path. Bundle-content checks grep for identifier-level markers (field/RPC names, module strings), not UI label copy: minification and JSX text splitting drop label strings, so absent copy proves nothing about whether the change shipped.
7. **Wire the app** — minimal client module + first real query, build locally with the env vars set, push (auto-deploy), re-verify in browser.

Vendor-specific endpoints, payloads, and failure modes: [references/vercel-supabase-wiring.md](references/vercel-supabase-wiring.md)

Renaming a product or moving to a new domain: [references/domain-migration.md](references/domain-migration.md)
