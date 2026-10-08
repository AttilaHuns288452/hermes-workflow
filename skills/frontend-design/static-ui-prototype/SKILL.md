---
name: static-ui-prototype
description: Use when a repo must stay a static UI-only prototype.
---

# Static UI/UX Prototype

A prototype repo whose only job is to SHOW the UI/UX: no backend, no
serverless functions, no real network calls, no real auth. Everything runs
from an in-memory demo layer. This is a standing scope, not a one-time
cleanup - one page quietly reaching a real service breaks the promise.

## Scope rules (always on)

- Zero real integration: no SDK clients, no env-var credential reads, no
  `fetch` to external services, no `backend/` or `supabase/functions/`
  scaffolds, no backend dependencies. Delete what exists - do not comment it
  out (git history preserves it).
- The mock layer is the ONLY data surface; every page imports it.
- The mock imitates the REAL API surface (the same call shapes AND error
  semantics a future integration will use) so swapping later is a one-file
  change. When the real API accepts multiple call shapes (object arg vs
  positional args), normalize BOTH in the mock - never patch callers one by one.
  Error shapes count: return the real API's error codes/messages, never
  friendlier ones - callers write handling against the real contract (e.g.
  PostgREST `.single()` with 0 rows must return PGRST116; a made-up message
  misses the caller's not-found branch and stale deep links dead-end).
- Flows stay demonstrable end-to-end: a form whose real counterpart provisions
  accounts becomes simulated signup + a local roster insert, with one plain
  comment noting where the real integration will plug in.
- Every navigable destination is a real page. Every `navigate()` target, nav/tab
  config path, and deep link must resolve to a rendered page - a fallback
  "coming soon" stub reachable from navigation is a broken link, not a page.
- Demo auth gates by identity (email match), never a password wall; the session
  is a localStorage key, so QA injects it before `goto` and skips the login UI.
- Demo data must be provenance-honest: every displayed value either comes from data a write path can change, or is DERIVED from such data. A hard-coded seed value no module writes reads as fake functionality the moment someone asks "how does this happen in the system". Fix = derive it (e.g. sessions-done = pre-tracking baseline field + completed-appointment count, capped at total — the baseline stays its own seed field so the derivation has one source of truth).
- Leave one runnable check behind every flow you rewired. For derived values the check asserts an independently computed expected number (baseline + fixture count), not a copy of the current output.
- Code must read human-written. Teammates, graders, and clients read this
  repo, so comments stay in plain developer voice: no tool or mode tags
  (`ponytail:`, `claude:`, similar), no generated-style shorthand
  (`upgrade path =`, `ceiling =`), no meta-notes about how the code was
  produced. Same information, the way a person would write it. Gate before
  commit: grep the diff for tag words and mode markers - one surviving
  marker fingerprints the entire repo as machine-written.

## Procedure (convert or audit a repo to this scope)

1. Sweep for backend leakage PER FILE, not just the central client:
   `createClient` / SDK imports / `import.meta.env` reads / `fetch(` /
   external URLs / backend or function dirs / server packages in
   package.json. A single page constructing its own real client from env vars
   survives a central-client audit.
2. Fix at the shared layer: make the mock accept every call shape its callers
   use (root cause) instead of editing each caller.
3. Delete dead scaffolds and unused backend deps.
4. Docs sweep: after ANY removal, grep the README for the removed thing -
   stack list, run instructions, key-setup sections, and file-tree comments
   all teach the deleted setup and rot silently. Strip real-key instructions.
5. README states the prototype scope up front ("no backend, no functions;
   integration comes later") so teammates don't re-add machinery.
6. Route integrity gate (`templates/route-crawl.cjs`, copy into `scripts/`):
   statically map every `navigate()` target and nav-config path to a router
   case, then live-crawl every route x role asserting real content renders
   (non-blank body, no fallback stub). The matrix doubles as a drift guard:
   every nav-config path must appear in it. Crawling beats reading the router -
   it catches render crashes static mapping cannot see.
7. Verify: leakage greps come back clean, build passes, the route crawl is
   green, and the runnable flow check passes.

## Pitfalls

- A full-page screenshot stitches fixed overlays (bottom nav, sticky CTA bars, floating buttons) into mid-image positions, so an "overlap" visible only in a full-page capture is usually a capture artifact. Verify suspected overlaps against live DOM bounding boxes (`getBoundingClientRect` on both elements) and use scrolled viewport screenshots as layout evidence.
- A vision report is a claim, not ground truth — small text gets misread. When exact wording matters (captions, labels, counters), capture the elements' `textContent` alongside the screenshot and check the report against it.
- Playwright role/name locators match substrings: `{ name: 'Next' }` also matches "Next month" and silently clicks the wrong element, which then looks like an app bug. Use `exact: true` or scope the locator to a container.
- A frozen displayed value was probably seeded in more than one row: grep the seed for the FIELD NAME across every record and fix all carriers, not just the row the user named. Half-fixing leaves the identical fabricated value visible on another screen.
- Mock DB state lives per page load, so cross-role E2E (log in as A, mutate, log in as B) resets the in-memory DB at every reload and cannot demonstrate mutation effects. Verify state-changing logic in ONE page load by driving the modules directly against the dev server: `page.evaluate(async () => { const api = await import('/src/lib/api.js'); /* call, mutate, re-read */ })` — dynamic imports share the app's module registry, so calls hit the same DB instance the UI renders from. Capture before → act → after numbers as proof. When the proof must go through the UI itself (button states, slot captions, disabled controls), stay in one page load and move between screens SPA-style: `history.pushState({}, '', path)` plus a synthetic `popstate` dispatch. `page.goto` between steps reloads and resets the mock; `page.goBack()` re-enters earlier screens carrying sticky draft state (selected date, service, wizard step) that silently changes the flow under test.
- Never render "Loading" from an empty fetch - a mock left with placeholder
  credentials can hang a page forever; seed demo data and render it
  immediately.
- "Static prototype" scope drifts through one helpful page at a time. Re-run
  the step-1 leakage sweep as a gate whenever the repo is touched for new
  work.
- Deleting a backend while its dependency and docs survive is a half fix -
  the dep invites reintroduction and the docs teach teammates to run the
  deleted folder. Removals go in one pass: code, dep, docs.
- A route rendering blank (zero body text) with no thrown error is a crashed
  React root until proven otherwise: an early `return` above any hook call
  ("Rendered fewer hooks") unmounts the ENTIRE app, not one route. Triage the
  console first; keep every hook above every early return.
- A QA script must run on a bare checkout: resolve its browser driver with a fallback (require from the repo's node_modules if present, else an absolute known install) instead of assuming dev deps were installed - the teammate or reviewer who runs the check will not npm i first.
- If a build command is refused or killed as a suspected long-running server, run it as the package script (`npm run build`) instead of the npx binary form - same build, no daemon heuristic trigger.
- Before adding motion/interaction CSS in a polish pass, grep the global
  stylesheet for an existing craft layer (entrance/press/transition classes) -
  earlier passes leave reusable blocks; wire elements to them. A global mount
  animation on `main > *` already covers per-route entrance, so `key={path}`
  remounts add nothing and replay animations on every state change.