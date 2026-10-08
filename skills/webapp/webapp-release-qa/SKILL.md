---
name: webapp-release-qa
description: Use when auditing, stress-testing, or fixing a web app.
---

# Web App Release QA

Full-product audits, adversarial/multi-role QA, design-fidelity verification, and iterative test-find-fix-regress loops until the app is release-grade. Trigger words: audit, stress test, break it, production-ready, shippable, fidelity, "fix all" / "apply the fixes" after a report.

## Always-on rules

1. **Audit means document, not fix.** In an audit phase, record current state first; never silently patch while auditing. Fixing starts only when the user says to apply the fixes.
2. **Never fabricate test results.** Everything reported as PASS was actually executed. Unverified items are `NOT TESTABLE` (with reason) or `BLOCKED`. An inconclusive probe is not a PASS and not a FAIL.
3. **Frontend behavior is not evidence.** A button works only when the database changed and persists across refresh and re-login. Authorization is only what the server enforces. Optimistic UI state (a handler that updates local state after a silent or failed write) fakes this — the verdict is the database read-back; a green UI check over a failed write means the handler swallowed an error.
4. **Every fix passes regression before being called fixed:** original repro → surrounding workflow → related cross-role flows → DB state → UI state → refresh → re-login.
5. **Preserve the stable version first** (git tag / commit) before a fix pass.
6. **Test-infrastructure hygiene:** delete only rows belonging to the suite's own test identities (patients/users the suite itself creates) — identity scope first, date-bounding second; never date-only or pattern-only deletion, it eats seed data. Self-clean at BOTH start and end: crashed runs leave residue that collides with the exact guards under test. Keep a canonical seed row map (shared by seed + cleanup scripts); when a cleanup eats seed rows anyway, restore via the seed script and disclose it — do not chase the row count by deleting more. If a probe mutates real rows, restore them to their exact prior values and disclose it in the report.
7. **Dev/QA tooling hides behind a flag** (`?dev=1` + localStorage), including one-tap role logins and mock payments. Mocks must travel the REAL backend path (real RPC/endpoint) so downstream analytics reflect them. Default state must contain no dev UI.
8. **A failing check is a hypothesis.** Triage every FAIL to harness-defect vs product-defect with a minimal probe (DOM dump, API read-back, single-flow replay) BEFORE editing product code; when a product fix results, that probe becomes its runnable check. Suite asserts track presentation copy: only a USER-DIRECTED design change may update a failing assert (and then log the deviation) — never revert a directed design to satisfy a stale assert. Conversely, a committed gate that was green and flips red after your own unrequested behavior change is the spec: restore the behavior or ask the user; do not weaken the assert to bless your change.

## The loop

> Inspect → Compare → Implement → Test → Find failures → Fix → Retest → Regress → Repeat

Do not stop after the first passing cycle or because the happy path works. Continue until the acceptance gate (below) is met.

### 1. Inventory + requirements matrix

Enumerate roles, shared vs role-specific pages, protected routes, and every button/form/list. Track as `requirement | reference | expected behavior | implementation | backend support | PASS/PARTIAL/FAIL/MISSING/BLOCKED/NOT TESTABLE`. Keep it current as fixes land.

### 2. Compare against the reference set (reconcile, do not blind-copy)

Source priority when references disagree: **latest product video = behavior/flows; latest Figma = visuals/layout; accumulated user feedback = regression tests.** For responsive/visual passes (route × viewport × role screenshot matrices with programmatic overflow/target/nav-chrome checks plus batched vision review), see `references/visual-qa-matrix.md`. For the fast vision-free responsive gate (every route × extreme widths × engines: overflow + clipped-text + page-error scan), run `scripts/responsive-sweep.cjs` (method in the same reference). Never reintroduce a flow the user previously rejected just because an older frame contains it (removed tabs, approval queues). Figma sets carry exploratory, outdated, and duplicated states — and the visible navbar is part of a frame's identity (the same page exists in per-role variants). When pixel comparison is impossible, compare `pdftotext -layout` structure against the app DOM and hand the user both screenshots.

### 3. Per-role live walkthroughs

One session per role, natural user sequence (login → core journey → edit → logout → re-login), verifying at each step: correct screen, validation, DB mutation, resulting state, persistence after refresh. Then stress each role: empty submits, double-clicks, stale pages, back button, wrong routes, manipulated IDs, cross-user access attempts.

Role-scoped information requirements ("a doctor must never see clinic
revenue", "financials are owner-only") get their own audit in both
directions:

- Grep the frontend for the information's markers (currency symbols,
  income/revenue/billing keywords) and enumerate every surface that can render
  them: pages, shared card/tile components, nav/tab configs, and shared
  branches that serve more than one role.
- Prove each role's view from RENDERED text: inject that role's session before
  `goto`, dump the region's `innerText`, and assert presence for the owning
  role AND absence for the others. Match case-insensitively — CSS
  `text-transform` makes a case-pinned absence check pass vacuously.
- Fix by whitelist, not by omission: gate the shared branch on the privileged
  role (`role === 'owner'`), so future roles inherit the hidden default.
  Removing the card from one role's branch leaves the next shared branch
  leaking the same data.
- Keep the owning role's access intact in the same change; a leak fix that
  also breaks the owner's dashboard fails the same brief.

### 4. Cross-role live simulation (the centerpiece)

Run all roles together as one business scenario with separate sessions: actor acts → every role sees the effect → DB readback as that role (their own client, not the service key) → a second role mutates → all see it → refresh everything → re-login everything → states hold. No contradictory states across roles.

### 5. Adversarial + integrity passes

Attack at the API with throwaway accounts; sweep for orphans/dupes/invalid status combos; recompute displayed totals from source rows and compare. `references/adversarial-testing.md` has the attack checklist and bug report format.

### 6. Fix + regress

On "fix all": apply root-cause fixes P0→P2 (one shared guard beats per-caller patches), then re-run the ENTIRE battery. A fix that breaks a sibling flow is not done. Backend trust-boundary fixes: `references/backend-trust-boundaries.md`.

## Harness pitfalls (a broken harness produces false verdicts)

- **Check helpers must take awaited booleans.** An async IIFE passed as the verdict is a Promise — always truthy, so every such check mis-reports. Await inside the helper or at the call site.
- **Write verdict semantics once and name the expected side** (`blocked` vs `accepted`); a flag whose happy value prints as BREAK will be misread every time.
- **RLS denials return `error: null` + 0 rows** — assert on rows affected (`.select()` and count), not error presence.
- **Short-label `has-text` is substring**: `has-text('Male')` matches "Female". Use exact text (`button:text-is(...)`) for short labels. `form button.last()` lands on in-form nav links — click the named submit button.
- **`textContent` never contains input VALUES** — assert on `inputValue()` for form state.
- **Replacing a form control breaks every suite at once** (native date input → custom grid). Immediately grep all suites for the old selector; for date grids use one shared `pickDate(page, daysAhead)` helper that navigates months then clicks the day.
- **Rolling fixture dates/slots** (`Date.now() + N days`, varied slot) keep re-runs from colliding with the unique constraints they are meant to exercise.
- **Long scripts go to files** and run with `node file.mjs`; giant inline one-liners/heredocs trip the command parser's blocklist.
- **Preview/dev servers die between sessions, and `nohup ... &` launched inside a foreground tool call dies when that call returns** — start long-lived servers through terminal background mode instead, and health-check (`curl -o /dev/null -w %{http_code}`) before any test run instead of assuming the port is live.
- **Landmark collisions break legacy selectors**: a second `<nav>`/`<main>` landmark makes old `locator('nav')` calls strict-mode ambiguous (silent timeout, not an error). Keep one landmark per role or scope selectors to the known container before adding page chrome.
- **`fullPage` screenshots composite fixed/sticky chrome at the capture edge** — "content clipped under the tab bar" findings are usually capture artifacts. Confirm with viewport-scoped bounding boxes before touching layout.
- **A blank page with zero `innerText` is a crash until proven otherwise** — check the console for render/hook errors ("Rendered fewer hooks...") before hunting data bugs; a React root crash blanks the entire app while navigation still 'works'.
- **A blank SPA shell is a URL-shape mismatch until proven otherwise** — serving a subpath-based build (Vite `base: '/repo/'`) from a different mount 404s its assets, and a hash route absent from the router (e.g. `#/g/:id` vs `#/gadgets/:id`) renders an empty page indistinguishable from a crash. Read the router's route table and the build's `base` first, mount local copies at the production base path, and count root children / check network 200s before touching app code.
- **Vision-model audits return plausible wrong findings** (placeholder text read as page content, `closest()` matching the element itself, mid-animation frames read as misplaced elements). Verify each finding with a DOM/pixel-extent check before editing anything.
- **Supabase RETURNING quirk**: `update(...).select()` can fail with a table permission error while the same plain `update()` succeeds (column-allowlist SELECT grants). Probe writes without `.select()`, then read back separately.
- **Reads through RLS/security-definer views with a service or anon key return zero rows silently** (`auth.uid()` is null) — read the base table from tests, or use the acting role's own client.
- **Automation silently blocked by required chip/select controls** (category/type pickers no text input fills) and exact-text selectors missing real labels (`Save` vs a longer label). Drive every required control; give flaky inline panels one retry on the DRIVE, never on the assertion.
- **An overlay whose pinned footer is unreachable, or whose click hits the element behind it, is usually anchored to an ancestor instead of the viewport.** An entrance animation with fill mode `both`/`forwards` on a page/root element freezes its end-of-animation transform (even identity), which makes that element the containing block for every `fixed` descendant — the sheet then sizes against the page and grows past the screen. Measure before resizing anything: compare the wrapper's `getBoundingClientRect()` to the viewport, run `elementsFromPoint()` at the unreachable control, and walk the ancestor chain for computed `animation-fill-mode`/`transform`. Fix at the source: page entrances animate opacity only, or use fill `backwards`.
- **A `flex-1 overflow-y-auto` body only scrolls when it can shrink below its content size** — give it `min-h-0` (and the sheet container `overflow-hidden`), or the pinned footer is pushed past the container's max-height and clipped.

## Acceptance gate + report

When the user asks to review before deploy: commit locally and stop — no push. Evidence-only reports throughout: every "done" carries executed test output and, for UI changes, before/after screenshots; "looks good" without a run is not a report.

Report shape: what was tested (per role / cross-role / backend / design) · what was fixed (each with its regression evidence) · remaining blockers (genuine only) · final results table (PASS/PARTIAL/BLOCKED/NOT TESTABLE) · the executed live-demo scenario · known limitations (state them, never hide). Severity: **P0** security/data corruption/impossible workflow · **P1** major feature or cross-role breakage · **P2** meaningful UX/data issue · **P3** polish. Bug entries: role, screen, severity, precondition, repro steps, expected, actual, reference expectation, DB behavior, cross-role impact, root cause, recommended fix.
