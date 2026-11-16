---
name: ui-parity-migration
description: Use when porting a reference UI into a functional app or matching elements to a reference.
---

# UI parity migration

**When to use:** the user says "make the UI the same as <reference>", "port the screens", "restyle to match the prototype", or asks to verify an app against a reference deployment. Not for greenfield design or single-token restyling.

Make an app's UI match a reference (prototype, mock app, or another deployment) while keeping its real data layer and functionality; verify parity on deployed builds. The reference owns look-and-feel; the app owns data and domain contracts.

## Always-on rules

- The reference repo/site is READ-ONLY: never edit, fix, or commit to it, even when it is broken. Its state is the spec. Put this in writing in every subagent context — a subagent that "helpfully fixed" the reference corrupts the spec mid-migration.
- The real data layer survives: port presentation onto the app's existing API calls, helpers, and exports. Never swap live fetches for the reference's mock arrays; never rename exports other modules import. Corollary — demo conveniences must not survive as fake success: reference prototypes show session-only previews (object-URL avatars), state-only toggles that reset on reload, and stored-but-unrendered fields. Grep the ported surface for `URL.createObjectURL`, display state initialized empty with a setter but no write path, "demo"/"not saved" copy, and payload fields never read at render; wire each to real persistence or make the copy honest.
- Domain contracts beat reference copy: where the reference's text encodes a divergent contract (fee models, prices, statuses), port the layout and keep the app's contract wording.
- Visual parity means the same landmarks (headings, sections, controls, states) rendered from live data — not identical text content. Different rows, names, and counts are not divergence.

## Procedure

1. **Inventory by churn.** Diff same-path source files between reference and app, skipping files that are intentionally different (API clients, data adapters, config). Rank by diff-line count. Large churn on a page file usually means it was never ported; a file missing in the app is a gap. Check the router's route-to-component map first: identical routes rendering divergent output means a component content gap, not a routing bug. Treat any user-named screen list as a hint, not the inventory — build the queue from the churn diff of every routed component, including the logged-out landing and auth-gate screens (onboarding, profile completion), which name-based lists routinely miss; a same-named file with matching exports can still carry hundreds of divergent lines.
2. **Triage observed differences.** Capture both surfaces at the same routes/roles/viewports (see Verification) and classify every diff into exactly one bucket: **DATA** (names, dates, counts, mock-vs-real rows, demo badges — not work), **INTENTIONAL** (dev panels, demo tools, app-only features, contract wording — not work), or **UI-GAP** (headings, layout, sections, states, spacing, typography — the work). The port queue is UI-GAPs only, ordered by the step-1 churn ranking.
3. **Port in parallel.** One subagent per file cluster with disjoint file ownership ("YOU OWN ONLY these files" in each context; reference repo named read-only). Each child: read both files fully, diff, port the reference's presentation onto the app's data layer, build must pass, no commits (the parent commits with explicit paths). Verify claimed edits with a diff before accepting any child report — completion claims are self-reports.
4. **Verify.** Build plus targeted QA of the affected routes; paired capture of app vs reference with normalized text diff (starter: templates/paired-capture.cjs); deploy verification against the live bundle (grep served chunks for new markers with a cache-busting query), never deploy status alone; exercise the real flows on the deployed app (login, create, status change), not just screenshots.

## Targeted element swaps (one reference element the user prefers)

When the user points at a single element ("the X in the prototype, I like that design compared to us"), the reference's implementation IS the spec: read the reference's source for that element (markup + CSS + behavior) before writing code. The user's phrase names the element, not the pattern — building from the verbal description alone reproduces the wrong design and forces a second round ("look at it so you know what I meant").

- Selection bars/trays: one chip per selected item showing its NAME plus a per-item remove x, count as n/max, a minimum-selection hint, and the destination CTA. A bare count strip ("N/4 in compare") is a UI-gap: the user cannot see or remove what is selected without leaving the page.
- Hide a bar/stepper on the route it navigates to — an "Open compare" bar sitting on /compare is noise; gate render on pathname.
- Fixed-position bars render via `createPortal(node, document.body)` when their logical parent animates (a transformed ancestor becomes the fixed element's containing block, so the bar drifts with it) or renders conditionally (the bar vanishes with its parent). Reserve page space (`body:has(.bar) { padding-bottom: ... }`) so the bar never covers page content.
- When a per-page element becomes global, grep the routed pages for their local copies and delete them — "two bars on one screen" is reported as one bug.

## Pitfalls

- For form login, click the form's submit control (`form button:not([type="button"])`). A `button:has-text("Sign in")` selector hits the sign-in/sign-up mode toggle and silently no-ops, and Enter-key submission is racy right after `fill`. When a login "fails", probe the auth endpoint directly with the same credentials: 200 means the harness or UI is at fault, not the account.
- Capture after hydration, never at fixed timeouts: a freshly (re)loaded SPA shows "Loading…" and lazy route chunks paint empty shells for several seconds. Wait for a landmark (no loading text and the body has real content) before screenshotting or asserting. A capture of a still-hydrating page reads as "the page is empty/broken" and burns whole debugging cycles on non-bugs. Re-probe live before reporting any render bug.
- Sign-in commonly full-page redirects (e.g. `window.location.href`), which destroys the Playwright execution context mid-evaluate. Guard `evaluate` in try/catch right after login or wait for load first.
- Playwright name/role matching is substring-based and strict-singleton: renaming a label breaks `/name/i` locators and adding a second control with the same role breaks `getByRole(role)` checks. Grep test scripts for the control's name and role before renaming or adding same-role siblings.
- Text assertions do not prove paint: clipped or `overflow-hidden` content still passes `innerText` checks. Pair text asserts with a screenshot or geometry probe before claiming anything about overlap, missing content, or layout.
- Vision-model feedback on screenshots over-reports (mid-glide frames read as collisions, scroll folds read as overlaps). Confirm every visual claim with a geometry probe or full-res crop before acting on it.
- A UI lock ("already on file → read-only") and the backend fill rule must share one emptiness definition — compare with `trim()`/`btrim()` on both sides. Truthiness counts whitespace as populated: the field locks as on-file while a NULL-only fill rule can never fill it, permanently bricking the repair path.
