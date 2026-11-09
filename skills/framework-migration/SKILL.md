---
name: framework-migration
description: Migrate a live app to a new frontend framework, or port screens between sibling apps sharing a stack.
version: 0.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [migration, react, vite, tailwind, frontend]
    related_skills: [react-patterns, webapp-testing, vercel-deployment]
---

## When to Use

- The user asks to migrate/rewrite a working app into React, Vite, Tailwind, Svelte, or another frontend framework.
- A brief demands a "full transformation" of an existing product and includes tests/QA/deploy requirements.
- Two sibling apps share a stack and one is the reference: port its screens/features into the other while the target keeps its own data layer (see "Porting between sibling apps").
- Skip for greenfield apps (nothing to preserve) or backend-only refactors.

# Framework Migration

Migrate a LIVE, working application to a different frontend framework (React/Vite/Tailwind, Svelte, etc.) without losing behavior. The failure mode this skill exists to prevent: a rewrite that looks modern, passes a build, and silently drops half the product's interactions, then ships on the strength of `npm run build`. Applies to "move to React", "rewrite in X", "full framework transformation" briefs.

**Always-on rules:**
- The existing QA suites and tests are the behavior contract. Inventory them BEFORE writing any new code; a migration is done when those checks pass against the NEW UI, not when the build is green.
- Keep a verified rollback: timestamped backup branch AND a reachable legacy route in the deployed app until the user signs off.
- Never claim parity from a successful build. Every claim pairs with an executed check (suite result, browser flow, geometry probe).
- Preserve user data and API contracts untouched; migrate the UI layer, not the schema.

## Procedure

### 1. Pre-flight (before any edit)
- `git status` + `git log --oneline -3`; record the starting commit. Create and VERIFY a backup branch:
  ```bash
  BR="backup/pre-$(date +%Y%m%d-%H%M)" && git branch "$BR" && git rev-parse HEAD && git rev-parse --verify "$BR"
  ```
- Inventory the behavior contract: every test file, QA script, and the DOM selectors/labels they bind to (grep the test tree for `data-`, ids, `has-text`, accessible names). Those selectors are the migration's acceptance list.
- Classify every existing module into (a) UI layer → migrate, (b) behavior library (engines, stores, renderers, parsers) → keep as-is and integrate, (c) backend/API → untouched. Most "rewrite the app" work is (a) only; modules in (b) are usually imperative DOM writers by design.

### 2. Architecture: integrate, don't reimplement
- Load behavior libraries as plain scripts and expose them to the new UI. **Bridge lexical globals explicitly**: a classic script's top-level `const X = …` is NOT a `window.X` property, so `window.X` reads `undefined` in modules. One inline `<script>window.X = X;</script>` after the library tag (or use the bare identifier) — the crash looks like "store is undefined" inside an otherwise working screen. Also enumerate every library the reused modules read and give each its own script tag in the new host page: a library the old page loaded but the new page forgets leaves its renderers silently unreachable.
- Wrap imperative engines with ref-mount adapters (mount into a container ref on effect, unmount/pause on cleanup). This is the standard integration for canvas/SVG renderers; reimplementing a proven visualization engine inside the new framework is where correctness dies. When the legacy tree already owns the REAL interactive renderer (answer checking, scoring, zoom/reset, drill loops), mount that — a freshly written static shell passes a screenshot review and fails the user the moment they click.
- Preserve the QA DOM contract in the new components: same ids/classes/roles/text hooks the suites bind to. The suites then validate the NEW UI with zero rewrites. When a deliberate copy change breaks an assert, update the assert in the same change (assert the invariant, not the old string).

### 3. Styles: the legacy sheet will fight the new app
- If the old app's global stylesheet styled `body`/`html` as its own shell (grid/flex app frame, `overflow: hidden`), it will hijack the new root — the whole new UI collapses into one grid cell and every child measures fine in isolation. Neutralize page-level shell rules in the new app's stylesheet and say so in a comment.
- Cascade truth: Tailwind utilities live in `@layer` and LOSE to the legacy sheet's unlayered rules no matter where the link sits. Responsive/column overrides for legacy-shared components must be plain (unlayered) CSS in the new stylesheet, matched by media query — not utilities. Verify at the failing viewport, not at desktop.
- Arbitrary-value utilities must be syntactically valid or they silently drop: in Tailwind, spaces are underscores (`w-[calc(100%_-_64px)]` — bare `calc(100%-64px)` is invalid CSS and the width falls back to auto/shrink-wrap). Prefer flex/grid growth (`flex-1 min-w-0`) over computed widths.
- Give every responsive grid explicit columns (`grid-cols-1 lg:grid-cols-[…]`) and cap fixed minimums: `minmax(min(300px, 100%), 1fr)` — a bare `minmax(300px, 1fr)` overflows a narrower content column (nav rail + padding shrink it below the minimum) and shows up as page-level horizontal scroll on phones only.

### 4. Routing + rollback
- New app owns the primary routes; keep the old app reachable at a stable prefix (`/legacy`) served by the same server. The server prefers the new build when its output exists and falls back to the old static tree — that makes deployment atomic and rollback a URL.
- Wire the build into the existing deploy workflow (`"build"` in package.json so a `framework: node` project builds the frontend; dev tooling in devDependencies is installed at build time).
- Repoint QA scripts' navigation to the new entry in the same change; a suite still loading the old URL keeps passing against the legacy app and proves nothing.

### 5. Test-sandbox compatibility (migrated code runs in old suites)
- Old suites often load UI files into a minimal DOM stub: guard cosmetic DOM work (`querySelectorAll`, `style.setProperty`, `input.value` defaults all missing there) — a crash in a render helper blanks the feature the suite is checking.
- Any `setInterval` created by code under `node --test` must be `unref()`-guarded or the runner hangs forever waiting for the event loop.
- Sandboxes that clamp timers (e.g. every `setTimeout` → 25ms) turn deliberate playback beats into machine guns; tests that assert stepped state must pause the driver before stepping.

### 6. Parity loop (the finish line)
1. Run the full legacy suite (`npm test`) — server/library tests must stay green.
2. Run every browser QA suite against the NEW UI. For each failure: reproduce, probe geometry/state before editing, fix at the owning layer, re-run.
3. Capture before/after at the judging viewports; the proof is rendered behavior, not diffs. Ported interactive tools are proven by INTERACTING through their real affordances — answer one question and see the hint/score, jump one TOC entry, zoom one graph. A screenshot proves only that the shell mounted.
4. Only then commit, deploy, and verify LIVE (production check = the same flows: enter app, run one animation, save one piece of data, download one artifact).

## Porting between sibling apps (same framework, different data layer)

When app A becomes the visual/behavioral reference for app B and B keeps its own data layer, the handed screen/file list is never complete and the two files' histories have diverged in BOTH directions (A has contract behaviors B lacks; B has fixes A lacks).

1. **Diff the routers first**: route path strings + rendered element names in each app's router file. The delta names the structurally missing screens. The logged-out entry surface (login/landing) is the most commonly missed piece because it is not a "screen" in any feature list — reproduce it and compare against the reference before declaring the port done.
2. **Classify every diff before touching it**: UI to port / data layer to keep (the target's real API calls survive; the reference's mock layer is never ported) / intentional divergence documented in code comments (e.g. a canonical model mapping the reference lacks). Never "correct" intentional divergence to match the reference — read the mapping's comment and architecture first.
3. **Merge shared components with a two-way diff**: restore the reference's contract behaviors (active navigation states, CSS-variable-driven positioning) while keeping the target's local improvements (aria-labels, truncation, badge caps). Blind overwrite loses the target's fixes; porting only the named files keeps the target's regressions.
4. **Grep the reference's copy/schema for terms the target deliberately retired** (old feature names, removed pricing models) before porting; a port must not reintroduce what the target removed. Leave a guard assert that the retired term stays absent.
5. **Completeness greps against UI headings must be case-insensitive** — CSS `text-transform` uppercases rendered labels, so source-casing greps false-fail on content that is present.

## Pitfalls
- **An empty container with zero console errors is a missing library or global bridge, not a render bug.** The usual mount seam (`if (!api) return;`) bails silently, so nothing paints and nothing throws. Probe `typeof window.X` in-page first — one evaluate call distinguishes "library never loaded" from "renderer broke" and points at the script list instead of the component.
- **Build green ≠ migrated.** The strongest predictor of silent loss is a rewrite that reimplements behavior libraries instead of integrating them; the second is QA scripts that still point at the old entry.
- **A shrink-wrapped layout after migration is almost always a page-level CSS collision or a dropped arbitrary-value width** — measure `getBoundingClientRect()` on the root chain (root → shell → content) before touching components; one width measurement localizes it to the exact link.
- **A screen that renders but every click times out** is usually an overlaying element (sticky/fixed rail, absolute panel) intercepting pointer events — the Playwright error names the interceptor; fix the placement (explicit grid tracks / spanning rows), not the button.
- **Scroll position survives view swaps**: clicking into a detail view from a scrolled list leaves the detail page scrolled thousands of px past its top (and a sticky rail appears "floating at the bottom" in stitched captures). Reset scroll on the swap.
- **Data-model field names and id semantics differ between layers** — read the canonical writer before porting a reader, and normalize on read instead of rewriting stored data. This includes API scope keys: an endpoint that filters by, say, chapter numbers will silently accept your store ids, match nothing, and answer from its fallback path instead of erroring. And treat empty values as MODES: if `[]` means "general knowledge" while `null` means "all", sending `[]` as "no filter" silently disables grounding for every answer.
- **QA flows race async content**: streamed answers and lazy renders beat fixed sleeps. Wait on a real selector (`waitForSelector`, generous timeout), and drive the UI through real affordances (click a starter prompt) instead of typed queries — a typed question the knowledge base doesn't match looks identical to a broken feature.
- When the user says the result is still wrong after a green run, re-run their exact flow in an UNCONFIGURED browser context first: harness overrides (forced reduced-motion, pinned viewport/TZ) hide exactly the experience they are reporting.
- **After a migration, "routing is broken / clicks do nothing" is usually one render crash**: an error thrown in any subtree unmounts the whole React tree, so every later click goes nowhere and the symptom reads as navigation failure. Capture `pageerror` first (it names the culprit); the classic is rendering a raw API object as a child (React error #31) — normalize object payloads to structured JSX at the renderer.
- **A QA gate whose output is piped through a summarizing filter inside a `&&` ship chain reports the FILTER's exit code** — the filter succeeds, so a failing suite sails straight into the commit/deploy. Check the gate's exit explicitly (or `set -o pipefail`) before any side effect.
- **A ported tool that underdelivers (fixed small count, single category) is capped at the source, not in the UI.** Read the generator for hard caps and ignored parameters and fix there before adding filter/picker UI — client-side filters over a capped source ship fake filtering.
