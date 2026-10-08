# Dental-Clinic repo notes

Active project for the frontend-prototype-shipping class. All facts below are repo conventions, not brief-specific.

## Layout

- Repo: `~/Documents/Projects/dental-clinic` (GitHub `AttilaHuns288452/Dental-Clinic`, private, `gh` authenticated). App: `frontend/` (Vite + React).
- Roles: patient / doctor / owner. One `Home.jsx` renders all home/dashboard variants via role conditionals (`isStaff` + role checks); the nav is a shared component rendering BUTTONS, not anchors. A feature meant "on Home" must land in every role branch.
- Mock layer (standing: frontend-only repo): `frontend/src/supabaseClient.js` (in-memory store, `dar_demo_session`) + `frontend/src/lib/api.js` helpers. Feature data extends the mock store; full reload resets it by design.
- Visual system: teal palette (#0D9488 / #134E4A), mobile-first app shell with per-role bottom tab nav. Density judged at 1920 width.

## Build and QA

- Build: `cd frontend && npm run build`.
- QA: `scripts/panel-qa.cjs` (Playwright, run from repo root, expects `PASS blocks: N` / `FAIL blocks: 0`). Extend by appending a numbered block per feature (add its counter to the expected-blocks list).
- Scratch Playwright scripts cannot `require('playwright')` outside the repo: use the absolute path `/home/attila/.hermes/hermes-agent/node_modules/playwright` (as `panel-qa.cjs` does) or place scripts in `scripts/`.
- SPA navigation in tests: click nav `getByRole('button', { name: 'Label' })`. `page.goto` resets the demo store — only use it for fresh-baseline entry (`window.location.hash` also works for deep entry).

## Deploy and live verify

- Live: `https://dental-clinic-nine-iota.vercel.app/`.
- Chain: push `master` with real commit → `git commit --allow-empty -m "Trigger deploy"` + push (pushes with file changes often get "Deployment was blocked"; empty commits deploy fine) → poll `gh api repos/AttilaHuns288452/Dental-Clinic/deployments/<id>/statuses` until `success`.
- Verify live: cache-bust fetch `/assets/index-*.js` and the lazy chunks; entry hash must match local `dist/assets` entry; grep all `shells-*.js` chunks for new UI strings (feature code lands in lazy chunks; there can be 3+).
