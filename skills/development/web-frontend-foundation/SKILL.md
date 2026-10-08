---
name: web-frontend-foundation
description: Use when building or reorganizing a web repo's frontend.
---

# Web Frontend Foundation

Standing up or reorganizing the frontend of an existing web repo (React/Vite/Tailwind class) for this user. The deliverable is a committed, pushed, runtime-verified foundation — not a visual mockup.

## Procedure

1. **Inspect before changing.** Clone/find the repo, read package.json, entry files, README, and list the source tree first. Reuse the existing stack and libraries — never introduce a framework the repo doesn't have. The user demands this explicitly.
2. **Placeholder-first.** In an early-stage team project, every route renders the SAME placeholder (icon + screen name + role + route path). Do NOT pre-build sample screens with mock dashboards — the user has twice had them deleted in favor of placeholders. Nav/routing/chrome are the deliverable; screens come later, one by one, replacing placeholders.
3. **Role switching = context, not conditionals.** One provider exposing `{ role, user, setRole }` with roles as an exported const map. Persist to localStorage. One nav config file maps role → menu items (label, path, icon). Keep the provider auth-shaped so real Supabase auth later only changes the provider's internals — no consumer edits.
4. **Dev role switcher is a separate component** ("Login as User/Doctor/Owner" buttons in a visually distinct dev bar), documented as delete-when-real-auth-lands. No auth validation — clicking just sets the role.
5. **Routing without new deps:** hash routing (`useHashPath` hook reading `location.hash`). On role switch, if the current route isn't in the new role's nav config, snap to that role's home — never strand the user on a dead route. Active-tab highlighting must use longest-prefix match, else `/owner/manage` highlights `Home` too.
6. **Connect Supabase via MCP, not guesses.** `list_projects` to find the project → `get_publishable_keys` for the publishable key. Keys are gitignored on this user's repos: write `.env.local` locally, commit a `.env.example` documenting the variable contract. Verify with a small node script importing the REPO'S OWN client (`supabaseClient.js`) and doing one real query. Run `list_tables` before assuming schema, and surface any RLS-disabled advisory to the user verbatim — never auto-apply remediation SQL, and never touch tables belonging to a different app that shares the project.
7. **Mock data pattern:** seed state with mocks in `useState(MOCK_DATA)` and replace only when a real query returns rows. Never render "Loading…" from an empty fetch — with placeholder/unreachable credentials the fetch hangs or errors and the screen looks broken forever. Mock modules live in `src/data/mock.js` (or equivalent), named so later real queries swap cleanly.
8. **Verify, then ship:** `npm run build` → headless smoke test → commit with a clear message → push → confirm remote HEAD via the GitHub API. See pitfalls for why the build alone is not verification.
9. **Building the real screens (when the user asks to "make it shippable"):** follow `references/figma-to-shipped-app.md` — vision-audit the design PDF frames first, implement screens role by role, write the committed QA suite, seed realistic demo data, then deploy. Ask the user before building all screens at once vs. placeholders if the project is a team capstone; once they say "build it", go full screens.
10. **Cloning into a NEW renamed repo (independent-project tests):** `gh repo create <name> --source=. --push` defaults the branch to `master` — rename locally (`git branch -m master main`), push, then `gh api -X PATCH repos/<owner>/<name> -f default_branch=main` BEFORE deleting the remote master. Deploy platforms and collaborators assume `main`.

## Pitfalls

- **A Vite/Rollup build passing is NOT runtime proof.** Missing imports used inside components (`useState` in a moved hook, etc.) compile fine — Rollup treats them as globals — and blow up at runtime as `ReferenceError`. After any component extraction/move/refactor, run a headless browser smoke test (vite preview + Playwright at `~/.hermes/hermes-agent/node_modules/playwright`) asserting the page actually renders, and capture `pageerror` events.
- **Duplicate function names in one module shadow silently — last definition wins, zero errors** (JS module scope and Python both). Before adding a function with a conventional name (`f79`, `Home`, `handleClick`), grep the file for the existing symbol; a numbered namespace deserves a grep for the next free number.
- **`pkill -f <pattern>` matches your own shell** when the pattern appears in the command string itself (e.g. `pkill -f "vite preview"` inside a compound command) — it kills the compound command mid-run. Kill by PID from the background-process session, or use a pattern that cannot appear in your own command line.
- **`.env` is gitignored on these repos and real keys exist only in the deploy platform (Vercel).** Never commit keys; never assume a local run has them. Placeholder keys boot the client but every query hangs/errors — hence the mock-seed rule above.
- **Mobile-first per design:** this user's app designs are phone-frame PWAs (390×844, bottom tab bar, floating chat FAB, brand accent from the design PDF/Figma). Restyle chrome to the design system, not desktop top-nav. When a design PDF exists, render its pages and vision-audit the frames before coding.
- **Vite preview serves the dist snapshot from server START, not from disk.** After `npm run build`, restart the `vite preview` background process before re-running E2E — a stale server silently re-serves the old bundle and makes fixed bugs look unfixed.
- **Mixing hash links with BrowserRouter breaks navigation silently.** `href="#/route"` sets the hash but `useLocation().pathname` never changes — links render as no-ops with zero console errors. Pick one routing mechanism; with `react-router-dom` use `<Link to>` / `navigate()` everywhere, including brand-logo and banner links, and add the `Link` import in the same pass as the conversion.
- **Navigating with `state` loses that state on direct URL entry or reload.** Any page whose prop comes from `navigate(..., { state })` needs an inline fallback picker/empty state for deep-link access (e.g. a chat thread picker when opened via a FAB).
- **`textContent` assertions miss `<input value>`** — input values are DOM properties, not text. Assert via `pg.evaluate(() => [...document.querySelectorAll('input')].map(i => i.value))` when checking prices/quantities rendered as inputs.
- **E2E suites must be idempotent.** Seed fixtures (pending requests ≥ 3, chat messages) at the top of the QA run — otherwise the second run asserts against data the first run consumed and fails confusingly. Commit the suite into the repo (`qa_all.mjs`) so teammates rerun it.
- **Vision QA can glitch** (returning reconstructed code instead of an audit, or timing out). Retry once with a rephrased/shorter prompt or a cropped region before concluding anything about the UI; prefer deterministic Playwright assertions for pass/fail and use vision only for layout/color/spacing judgment.
- **`mcp__supabase__execute_sql` may run read-only on some projects** (UPDATE/DELETE fail with `25006 read-only transaction`) even though `apply_migration` and SELECT work — for data mutations, run a Node script with the project's own client signed in as a staff user (RLS-gated), not SQL.
- **Realtime `postgres_changes` subscriptions are not guaranteed enabled** — after inserting a chat message, refetch the thread (`listChat`) instead of trusting the subscription to render it; keep the subscription for extra liveness only.
- **Supabase MCP auth tokens can be scoped/stale per project** — a 403 on a newly created project means the MCP OAuth token predates it; use the Supabase management REST API with the token from `~/.hermes/mcp-tokens/supabase.json` for project CRUD, and have the user re-auth MCP for interactive work.

## Deploying to Vercel (new/renamed projects)

See `references/vercel-deploy-gotchas.md` — deployment-protection SSO wall, monorepo `vercel.json` requirements, the Redeploy cache trap, and env-var setup the agent cannot do itself (MCP scope limits).

## References

- `references/figma-to-shipped-app.md` — procedure for the "build it shippable from our Figma" phase: design audit, screen implementation order, seed data, QA suite.
- `references/vercel-deploy-gotchas.md` — Vercel-specific pitfalls hit on this user's monorepo setups.

## Stack notes (this user's current repos)

- React 18 + Vite + Tailwind + `@supabase/supabase-js`, single repo `frontend/` + `backend/` (Express), deployed on Vercel with env vars set there.
- Tailwind palette: restyle `primary` in `tailwind.config.js` to the project's brand color (e.g. dental teal `#0d9488`) — the template default blue is never the brand.
- E2E harness: `npx vite preview --port <port> --strictPort` in background, then a Playwright script (import from `/home/attila/.hermes/hermes-agent/node_modules/playwright/index.mjs`) with a 390×844 viewport, clicking the dev role buttons and asserting nav labels + route hashes + placeholder rendering, collecting `pageerror`.