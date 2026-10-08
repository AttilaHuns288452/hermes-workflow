---
name: frontend-prototype-shipping
description: Use when shipping a frontend-only brief on a UI prototype.
---

# Frontend Prototype Shipping

Recurring class: the user sends a UI brief for a prototype app (Dental-Clinic, GadgetWise, static UI prototypes) with a hard frontend-only boundary, and expects a working, QA'd, deployed feature plus a short evidence-backed report. Standalone artifact deliverables (boards, videos, guides) get a copy in the repo root AND ~/Downloads, with a README pointer.

## Standing constraints (every brief of this class)

- Frontend only. No database or migrations, no Supabase table/RLS changes, no API endpoints, no auth changes, no new dependencies. If the feature would need backend support, implement the prototype behavior in the existing mock layer and say so in the report.
- Reuse the repo's visual system (accent palette, card/button/chip classes, image placeholders). Variety comes from layout, never new palettes.
- Match the brief's stated scope exactly. Adding unrequested screens, panels, or features is a defect, not a bonus — "only these screens" means only these.
- Responsive bar: the user judges dashboards at 1920 width; verify 320/390 mobile plus 1366/1440/1920 before calling responsive done.

## Procedure

1. Turn the brief into a checklist. Keep the brief's own section headings for the final report.
2. Extend the mock/seed layer first (the single source the UI reads), then the API-style helpers, then the component. Seed realistic data matching the brief's examples.
3. Cross-screen state (configure on one screen, reflect on another) lives in the shared mock store with subscriber updates — never component-local state. Component state resets on unmount or route change and the brief's flow check fails.
4. Build the component in the repo's components/ dir reusing existing classes. Clamp long titles/descriptions (2 lines) so seeded or user-entered strings cannot break layout.
5. Place it on EVERY relevant surface: grep the target page for role conditionals first — one page file often renders several role dashboards, and one placement ships the feature for one role only.
6. QA: extend the repo's Playwright suite with a numbered block covering the brief's flows (create → surface reflects → control works → deactivate/undo → gone), then run the full suite plus the responsive/console sweep. Expect zero FAIL and zero page errors.
7. Build and ship through the repo's deploy chain, verify live (below), then report: what shipped, what was skipped as out of scope, and the evidence (QA counts, commit SHA, deployment ID, live-bundle grep result). The user checks claims himself.

## Form UI rules

- An "(optional)" field label obligates a none affordance: selects get an explicit `None` option (default for new records), native date inputs get a `None` clear button (disabled when already empty), and edit prefill must show none for absent values instead of resurrecting a default. Save and preview must use the same null semantics (`value.trim() || null`) or the preview lies about what saves. Empty free-text already means none.
- Never `w-full` on a flex child that has siblings: width:100% resolves against the flex container, so the item overflows its column and lands on top of the neighbor — which then intercepts pointer events. Use `flex-1 min-w-0`. A native date input needs ~120px to show the full year; give rows pairing a date with an adjacent control the full row on phones (`col-span-2 sm:col-span-1`).

## Mock-state QA rules (Playwright)

- A full page reload resets the in-memory demo store. After creating state through the UI, navigate via the app's own nav (SPA clicks); `page.goto` silently wipes the state the reflect-checks depend on.
- Probe the nav's DOM before writing locators: it may render buttons, not anchors, so `a[href=...]` selectors match nothing. `getByRole('button', { name: 'Label' })` works regardless. If routes are real URLs, `window.location.hash` is a valid deep entry when nothing is created yet.
- Carousels, tabs, and one-card views expose only the visible item in innerText. Assert the indicator count, advance the control, or assert on the manage list instead of the surface text.
- Locate a section with `locator('section', { has: getByRole('heading', { name }) })` — page innerText includes every role branch, so page-level text assertions false-fail.
- Clicks on low page elements fail against fixed bottom navs/FABs even when visible: `scrollIntoViewIfNeeded` does not clear viewport-fixed overlays. Park the target mid-viewport first (`window.scrollBy(0, rect.top - 260)`), then click; never `force: true`, which lands the pointer on the overlay.
- A click timeout's first error line hides the culprit. Print the FULL Playwright error (the call log names the intercepting element) and probe `document.elementFromPoint` at the element's center before touching product code: interceptor = a neighboring control means a layout overflow bug to fix; interceptor = a fixed overlay means the harness must scroll.

## Visual QA rules

- Fixed-position UI (demo chips, FABs, bottom navs) composites into element screenshots at its viewport-fixed spot and reads as overlap INSIDE the element. Confirm every flagged overlap in the DOM (getBoundingClientRect, scrollWidth vs clientWidth) before touching layout; treat composite collisions as artifacts.
- Fix measurable defects only: real overlap/clipping, horizontal overflow, wrapped or truncated labels, adjacent text touching with zero gap. When vision calls spacing or type "too small" but nothing overflows or clips, it is subjective styling — leave it unless the brief specified it.

## Deploy and live verification

- Some hosts block deployments of pushes with file changes while empty commits deploy fine: after every real push, add `git commit --allow-empty -m "Trigger deploy"` and push, then poll the deployment status by ID until `success`.
- Proof it shipped: cache-bust fetch the live entry bundle and grep for new UI strings; the entry hash must match the local dist entry hash. Then grep EVERY lazy chunk too — several same-prefixed chunks can exist and the feature often lands in one of them; checking only the entry false-fails.
- Local build success is not deployment; a deployment record is not live code; the live grep is the last link.

## Report

The final message uses the brief's own headings, states what shipped and what was skipped as out of scope, and carries verification evidence. Unbacked "done" erodes trust faster than an honest blocker.

Project-specific commands and repo maps: references/dental-clinic.md.