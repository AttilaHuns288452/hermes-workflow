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

## Cross-role sync tests

Use separate browser contexts (one per role) so sessions can't bleed. Pattern:
close popup expectations early (`Promise.all([waitForEvent('popup'), click])`)
and treat a missing popup as either a real dead button or popup blocking —
verify with a headless run where no blocker exists, then add an in-app
fallback for blocked environments.
