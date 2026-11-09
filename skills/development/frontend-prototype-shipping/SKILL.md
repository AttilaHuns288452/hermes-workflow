---
name: frontend-prototype-shipping
description: Use when shipping a frontend-only brief on a UI prototype.
---

# Frontend Prototype Shipping

Recurring class: the user sends a UI brief for a prototype app (Dental-Clinic, GadgetWise, static UI prototypes) with a hard frontend-only boundary, and expects a working, QA'd, deployed feature plus a short evidence-backed report. Standalone artifact deliverables (boards, videos, guides) get a copy in the repo root AND ~/Downloads, with a README pointer.

## Standing constraints (every brief of this class)

- Frontend only. No database or migrations, no Supabase table/RLS changes, no API endpoints, no auth changes, no new dependencies. If the feature would need backend support, implement the prototype behavior in the existing mock layer and say so in the report.
- Reuse the repo's visual system (accent palette, card/button/chip classes, image placeholders). Variety comes from layout, never new palettes. Semantic state colors (status, availability, payment states) live in ONE shared map module every page imports — per-page hardcoded status colors drift the same state into different shades across screens.
- Match the brief's stated scope exactly. Adding unrequested screens, panels, or features is a defect, not a bonus — "only these screens" means only these.
- Responsive bar: the user judges dashboards at 1920 width; verify 320/390 mobile plus 1366/1440/1920 before calling responsive done.

## Scope & simplification

- Prefer the simplest interaction that satisfies the requirement: direct manipulation (click a date to toggle it, inline edit) over workflow machinery (requests, approvals, statuses). Workflow state is justified only by genuine multi-actor requirements — when a generated brief layers request/approval flows onto a single-actor domain, ship the simple version and note the simplification in the report.
- An override ("ignore the previous X, just do Y") deletes the superseded machinery at every layer — component, data model, helpers, tests, docs — and re-points the tests to the new behavior. Hiding the UI while leaving the model, helpers and stale tests behind is not the override; the next brief inherits the dead machinery.
- Moving a feature to a new home removes it from EVERY old mount site: grep the component name AND its heading text across all pages before declaring the move done — sibling pages often mount the widget inline instead of through the relocated component, and that surviving mount is what the user finds and re-reports.
- A user-reported defect defines the scope: fix and verify exactly the named defect. Do not turn "fix the X overlap" into a full-page audit, unrelated fixes, or speculative polish — over-scoping a one-defect fix is the recurring complaint on this class of work.

## Data seam (real data drops in later)

- One seam only: all fake data lives in the mock client behind the single API-style module the UI reads (Procedure step 2). Grep for stray seed arrays in components before adding more data.
- Full coverage: every table/collection the UI queries has demo rows. Audit queried-vs-defined as a script (`npm run check:data`), not by eye.
- Leave the seam verifiable: a runnable drift guard that fails when the UI queries a table with no demo data, plus a short README swap note naming the one file to replace with the real client and any call shapes or behaviors the mock hides (auth flows especially: fake clients that accept looser signatures than the real one fail only after the swap). The guard is what keeps the seam honest while the UI grows.

## Procedure

1. Turn the brief into a checklist. Keep the brief's own section headings for the final report.
2. Extend the mock/seed layer first (the single source the UI reads), then the API-style helpers, then the component. Seed realistic data matching the brief's examples.
3. Cross-screen state (configure on one screen, reflect on another) lives in the shared mock store with subscriber updates — never component-local state. Component state resets on unmount or route change and the brief's flow check fails.
4. Build the component in the repo's components/ dir reusing existing classes. Clamp long titles/descriptions (2 lines) so seeded or user-entered strings cannot break layout.
5. Place it on EVERY relevant surface: grep the target page for role conditionals first — one page file often renders several role dashboards, and one placement ships the feature for one role only.
6. QA: extend the repo's Playwright suite with a numbered block covering the brief's flows (create → surface reflects → control works → deactivate/undo → gone), then run the full suite plus the responsive/console sweep. Expect zero FAIL and zero page errors. A failure in behavior the brief deliberately changed is a stale expectation — update the assertion to the new spec; never bend the product back to satisfy an old test. Conversely, the brief's literal content lines (example copy, mandated status labels) are test content: assert every one before restructuring the component, because a restructure silently drops a required line and only that assertion catches it.
7. Build and ship through the repo's deploy chain, verify live (below), then report: what shipped, what was skipped as out of scope, and the evidence (QA counts, commit SHA, deployment ID, live-bundle grep result). The user checks claims himself.

## Form UI rules

- An "(optional)" field label obligates a none affordance: selects get an explicit `None` option (default for new records), native date inputs get a `None` clear button (disabled when already empty), and edit prefill must show none for absent values instead of resurrecting a default. Save and preview must use the same null semantics (`value.trim() || null`) or the preview lies about what saves. Empty free-text already means none.
- Never `w-full` on a flex child that has siblings: width:100% resolves against the flex container, so the item overflows its column and lands on top of the neighbor — which then intercepts pointer events. Use `flex-1 min-w-0`. A native date input needs ~120px to show the full year; give rows pairing a date with an adjacent control the full row on phones (`col-span-2 sm:col-span-1`).
- Overlay scrims must render through a portal to `document.body`: a modal built inside the page container is z-stacked under the app's fixed chrome (sticky header, bottom nav, demo pills), which punches through the dim. Chrome rendering bright inside a modal is a missing portal, not a z-index value to tune.

## Mock-state QA rules (Playwright)

- Probe the app's real initial state before writing navigation: demo seeds may auto-login (so `/` renders the dashboard, not the landing) and role shells differ (avatar menu vs tab bar). Assert from the observed DOM, not the route map.
- A full page reload resets the in-memory demo store. After creating state through the UI, navigate via the app's own nav (SPA clicks); `page.goto` silently wipes the state the reflect-checks depend on.
- Probe the nav's DOM before writing locators: it may render buttons, not anchors, so `a[href=...]` selectors match nothing. `getByRole('button', { name: 'Label' })` works regardless. If routes are real URLs, `window.location.hash` is a valid deep entry when nothing is created yet.
- Carousels, tabs, and one-card views expose only the visible item in innerText. Assert the indicator count, advance the control, or assert on the manage list instead of the surface text.
- Locate a section with `locator('section', { has: getByRole('heading', { name }) })` — page innerText includes every role branch, so page-level text assertions false-fail.
- Clicks on low page elements fail against fixed bottom navs/FABs even when visible: `scrollIntoViewIfNeeded` does not clear viewport-fixed overlays. Park the target mid-viewport first (`window.scrollBy(0, rect.top - 260)`), then click; never `force: true`, which lands the pointer on the overlay.
- A click timeout's first error line hides the culprit. Print the FULL Playwright error (the call log names the intercepting element) and probe `document.elementFromPoint` at the element's center before touching product code: interceptor = a neighboring control means a layout overflow bug to fix; interceptor = a fixed overlay means the harness must scroll. The same interceptors surface on touch as "keyboard won't open" or "tapping X activates Y": occlusion is the first hypothesis to test, before debugging any handler.
- Assert visible text case-insensitively (`/i`): CSS `text-transform` makes `innerText` uppercase while the DOM text is not, so `.includes('Book now')` false-fails against a label that is visibly correct.

## Visual QA rules

- Fixed-position UI (demo chips, FABs, bottom navs) composites into element screenshots at its viewport-fixed spot and reads as overlap INSIDE the element. Confirm every flagged overlap in the DOM (getBoundingClientRect, scrollWidth vs clientWidth) before touching layout; treat composite collisions as artifacts. The same goes for vision-read text: verify a flagged wrong/missing label against DOM text or code before fixing copy — misread fonts produce phantom label defects.
- Fix measurable defects only: real overlap/clipping, horizontal overflow, wrapped or truncated labels, adjacent text touching with zero gap. When vision calls spacing or type "too small" but nothing overflows or clips, it is subjective styling — leave it unless the brief specified it.

## Deploy and live verification

- Some hosts block deployments of pushes with file changes while empty commits deploy fine: after every real push, add `git commit --allow-empty -m "Trigger deploy"` and push, then poll the deployment status by ID until `success`.
- Proof it shipped: cache-bust fetch the live entry bundle and grep for new UI strings; the entry hash must match the local dist entry hash. Then grep EVERY lazy chunk too — several same-prefixed chunks can exist and the feature often lands in one of them; checking only the entry false-fails.
- Local build success is not deployment; a deployment record is not live code; the live grep is the last link.
- An explicit deploy authorization ("commit push and deploy it") is standing for that project's later rounds — ship the same way without re-asking. A brief that says do-not-deploy or branch-only resets it.

## Report

The final message uses the brief's own headings, states what shipped and what was skipped as out of scope, and carries verification evidence. Unbacked "done" erodes trust faster than an honest blocker.

Project-specific commands and repo maps: references/dental-clinic.md.