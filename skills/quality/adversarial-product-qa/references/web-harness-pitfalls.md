# Web Harness Pitfalls (Playwright + suite coupling)

## Locator traps

- `has-text("Male")` matches "Female" (substring, case-insensitive) → use
  `text-is` / `getByRole('button', { name: 'Male', exact: true })`.
- `locator('form button').last()` often hits a helper button inside the form
  (e.g. a "Log in" switch link placed after the submit) → target the submit by
  exact role+name.
- `getByText('Person Name').first()` can hit a header/summary echo of the name
  above the real row → prefer `getByRole('button', { name: /Name/ })`.
- Strict-mode multi-match violations are ambiguity bugs in the harness — fix
  the locator, don't click through them.
- `textContent` never contains input VALUES or placeholders → assert
  `inputValue()` / placeholder attributes for field state.
- `fill()` refuses `input[type=number]` → scope text fills with
  `input:not([type="number"])`.
- A regex over full page text can match a permanent subtitle that happens to
  equal the validation message → assert on the error element's own locator.

## Suite ↔ UI coupling

- Replacing a component (native date input → month grid) kills every suite
  locator for it — sweep and patch the harness in the same change, and add a
  `pickDate(pg, daysAhead)`-style helper instead of repeating raw clicks
  (helper must navigate month headers when the target is out of view).
- Asserting output strings couples suites to copy; prefer role/aria locators
  and data semantics.
- Build pipeline trace: `npm run build | grep "✓ built"` hides the failure
  reason — when the grep comes back empty, re-run unfiltered before debugging
  the wrong layer.

## Repeatable-run hygiene

- Fixed fixture dates collide with DB unique constraints on reruns (same
  patient+date, same slot) → compute dates from `Date.now()` with different
  per-suite offsets and vary time-slot picks.
- One suite's leftover rows poison later runs (a stale row matching a "gone
  from list" assertion) → clean fixture rows before EVERY run, not just after.
- Regression assertions for removed features must assert ABSENCE (negative
  regex over page text), not presence — suites written for the old feature
  will otherwise "fail" in the correct new world.
- Screenshot/demo-capture scripts carry component locators too — they break
  silently and deliver dead screens; update them with the same component
  change and re-shoot.

## Interaction probes

- Backdrop/dismissal clicks: derive click points from the dialog's bounding box
  (a real gutter inside the viewport), never hardcoded corner pixels — corners
  land on sticky headers or edge decorations and false-fail the close handler.
  Confirm the hit target with `document.elementFromPoint`; if app chrome
  (header/nav) is still topmost while a modal is open, that is a real stacking
  bug (scrim must portal above fixed chrome), not a test artifact to route
  around.
- A click timeout on a visible, enabled, in-viewport element is interception
  until proven otherwise: hit-test `elementFromPoint` at the target's center
  to name the interceptor. Toast/badge overlays are harness artifacts — dodge
  in the helper by re-targeting at top level (a dodge inside a scroll
  container can defeat itself). But when the window is at MAX SCROLL and
  fixed chrome covers the target's band, no dodge exists for a real finger
  either — that is a real UI trap, and the fix belongs to the app: deepen the
  page's bottom clearance so content never rests inside the fixed band, and
  make any negative margin that cancels that clearance share its exact
  `calc()` expression — a hardcoded rem detaches silently when the formula
  changes (pinned panels drift, pages start scrolling).
- A control that mutates its own attributes (password visibility toggle swaps
  `type`, can clear placeholder) kills selectors keyed to those attributes
  mid-assert — hold element handles before the toggle and compare
  `boundingBox()`/value through the handles instead of re-querying.
- Form-walker scripts that assume a `<form>` wrapper silently match nothing on
  component-built forms (inputs in divs, submit outside any form) — query
  visible inputs and buttons document-wide, scoped to the open dialog when one
  exists.

## Cross-role sync tests

Use separate browser contexts (one per role) so sessions can't bleed. Pattern:
close popup expectations early (`Promise.all([waitForEvent('popup'), click])`)
and treat a missing popup as either a real dead button or popup blocking —
verify with a headless run where no blocker exists, then add an in-app
fallback for blocked environments.
