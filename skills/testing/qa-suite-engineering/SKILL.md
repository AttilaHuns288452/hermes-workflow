---
name: qa-suite-engineering
description: Use when building or maintaining UI/E2E test suites.
---

# QA Suite Engineering

Automated UI test suites (Playwright-style) and full-system QA passes for this
user's apps. Goal: a suite whose green run MEANS the system is correct, and
which stays green without babysitting.

## Core principle: state propagation, not buttons

A feature passes only when the resulting state is correct in EVERY affected
surface: the other roles' UI, the database, notifications, messages, finance.
Test as Role A → verify as Role B → verify as Role C → verify DB → refresh/
relogin → verify again. "All buttons work" is not a finding.

## Report format (standing preference)

Full-system QA reports use these sections, in this order:
**Passed** (what was actually verified, with evidence) · **Failed** (broken now)
· **Fixed** (corrected during QA) · **Remaining** (known limitations) ·
**Cross-role inconsistencies** · **Data-integrity issues** · **Security issues** ·
**UX issues** · **Production risks**. Never claim 100% unless the flows were
actually run; list what was not exercised. Every count in the report ('N/N
  checks', 'X tests pass') is computed from tool/harness output — an expected
  number written into a claim is a fabricated count.

## Assertion discipline (never false-pass)

- Assert the exact expected state ('Dentist Portal', a specific value), never a
  broad regex over words a wrong page also contains — a login page containing
  "Clinic" passes /Doctor|Clinic/ and hides a failed login.
- A check whose fixture is missing must FAIL loudly or create the fixture;
  silent skip manufactures green.
- Assertions pinned to UI copy must change in the SAME commit as the copy — grep the suite tree for the old name and update every driver that clicks by accessible name in the same pass.
- One runnable check behind every money/security path — a permanent adversarial
  probe suite, not a one-time audit: self-settle payment rows, edit amounts,
  flip status fields, insert privileged records, forge prices, touch another
  tenant's resource, double-settle.
- When a value becomes configurable (settings), add a propagation check that
  edits it and asserts EVERY surface that displays it — hardcoded duplicates
  rot silently.
- When registration can collide with staff-created records, assert
  one-record-per-human after signup (account claims the existing record).
- A readiness poll that checks `count >= N` returns immediately once stale rows
  accumulate and stops waiting for the row the check is about — poll for the
  SPECIFIC row (by endpoint / id / unique key) and assert its identity, not a
  threshold count.
- Identify which entity-state actually holds the resource (draft vs
  reserved/committed) and assert conflict invariants at THAT layer — asserting
  at the draft layer either false-passes (drafts don't hold the resource) or
  false-fails (an unrelated uniqueness constraint masks the real check).
- **Capture-after-sleep loses to full-page loading states.** When a screen renders a page-level skeleton until its fetch resolves (not just inline spinners), a text assertion captured after a fixed `waitForTimeout` reads empty content under load and fails checks whose deeper click-based siblings pass (clicks wait for their target). Capture assertions must waitFor the TARGET CONTENT being asserted — blind sleeps race the fetch.
- `textContent` misses input VALUES (edit-mode fields render as inputs, not text) — assert via `input.value` or a server-side read; and `button[type="submit"]` misses default-type submit buttons (a bare button has no type attribute) — select `button:not([type="button"])`.
- A `:focus-visible` styling check must drive REAL keyboard navigation (press Tab / Shift+Tab, assert the focused element's computed style) — programmatic `element.focus()` sets `:focus` only and the check false-fails against correct styling.
- A QA probe that intentionally forces a failure (bad fetch, forced error state) must clear or exclude the error log it deliberately triggers before the suite's final zero-page-errors gate — otherwise the gate fails on the harness's own fixture.

## Fixtures and isolation

- Self-contained: create the rows you need; never scavenge for pre-existing
  state (environment-dependent, fails on clean DBs).
- Unique per run: randomize dates/emails/timestamps — uniqueness constraints
  (one booking per patient per day, one payment per appointment) collide across
  runs on fixed dates. When the constraint is per-identity-per-day and seeded
  rows are shared, hand every booking a FRESH identity from a per-date pool
  (seeded rows first, throwaway fixtures after); compute the pool from the DATABASE's rows, not the suite's own used-set, or sibling suites' leftovers collide with picks the local map thinks are free.
- Clean up everything you create, including auth users, not just the visible
  rows. Probes that skip cleanup poison every later run.
- Mutating global state (settings, prices)? Save and restore within the run. This includes fixtures that UPSERT shared/real entities: the same write can be a harmless no-op on some run days and a polluting insert on others (weekday-shaped stock rows) — snapshot and restore rows on shared entities even when the upsert "changes nothing" on most runs, because on the exceptional run it breaks a LATER suite's world-state invariant ("nobody is scheduled on closed days"), not your own. When a suite's isolation check counts WORLD state and fails only in a matrix run, the polluter is an earlier suite's leftover rows — the count identifies it arithmetically (entities × affected dates).
- Drivers that TOGGLE shared state (availability flags, referrals, settings) must read current state before clicking — a blind toggle flips fixtures the next run depends on and false-fails as a product bug.
- Fixture timestamps must obey the product's enforced time windows (working
  hours, closed days): when enforcement is added, sweep the test tree for
  bookings outside it in the same pass — those failures masquerade as product
  or provider bugs ("payment could not be created" looks like a provider
  outage when the booking is simply before opening).
- **Seed data dated relative to "today" (today+N) makes hardcoded dates in
  assertions a daily-expiring time bomb.** Derive the expected value from the
  seed's own rules (read its offset/weekday/unavailable-date arrays and compute
  the expectation) instead of pasting an absolute date, and scope capacity
  expectations to the slots the UI actually shows — a check that walks slots
  the UI hides (outside working hours) false-fails on legitimate zeroes and
  points at the booking logic when the app is correct. This includes the RUN DAY
  itself: a case asserting on today's stock state ("N dentists scheduled today")
  must create that state itself — runs cross midnight into closed days and stock
  rows are weekday-shaped. RANDOMIZED fixture dates must be clamped to the
  UI's own NAVAIGABLE horizon (month-nav limits, booking windows), not merely
  to the future: a random target beyond it clicks a disabled control and the
  click timeout masquerades as a flaky product bug. Add a fail-fast assert that the picker landed on the intended
  date before continuing.
  - A failure confined to a wall-clock WINDOW (green on daytime runs, red after local midnight; a "flake" with a stable rate) is a date-identity bug until proven otherwise: 'today' derived as the UTC date (`toISOString().slice(0,10)`) silently lags the local calendar during the timezone-offset window and shifts every relative seed, default, and day filter at once. Audit the app's date-key primitive (see the `timezone-date-keys` skill) before touching assertions or blaming fixtures, and make the window reproducible by forcing TZ to the app's timezone.
- Assert deletion via the delete response + an authoritative list, never
  download-after — object GETs can be CDN-cached (max-age) and serve deleted
  bytes, producing a false "delete failed". Sensitive uploads set cacheControl
  no-store so deletes and permission changes bite immediately.
- Cleanup scoped to per-run identities leaves earlier eras' rows behind and
  they accumulate; when a count-based check starts passing vacuously, sweep the
  test users' stale rows and tighten the check to row identity. The same
  accumulation breaks identity lookups: `.maybeSingle()` on a name/tag that
  every run re-inserts errors on multiple rows and returns null, so the check
  fails only on the branch that depends on the value — a phantom "intermittent"
  failure whose rate equals how often that branch is taken. Look up newest-row
  (`order(created_at desc).limit(1)`) or a per-run-unique identity before ever
  blaming timing.
- Fixture helpers must survive a crashed previous run: a bare INSERT on a
  natural key poisons every later run with a duplicate-key crash (the crash
  that left the row also skipped cleanup). Upsert on the natural key, or
  delete-then-create at suite start.
- Provider calls inside test setups flake (~1% transient 5xx under load):
  wrap them in a bounded retry (2–3 attempts) that PRINTS the response on
  every failed attempt — a retry that swallows the error turns one flake into
  a long false-bug hunt.
- supabase-js turns non-2xx edge-function responses into a generic message and
  hides the body on `error.context.json()` — read that body before diagnosing;
  the real text ('appointment_id required', 'no dentist available') beats
  guessing at the opaque wrapper. Same family: a query result is the
  `{data, error}` wrapper — assign it WITHOUT destructuring and `.id` reads
  `undefined`, which surfaces as a baffling 'X required' several layers later.
  Check the assignment shape before chasing the downstream error.
- Compare UI text **case-insensitively** when the target element has a
  `text-transform: uppercase` style — `innerText` returns the transformed text
  ('NOT READY'), so a case-pinned assert fails against correct behavior. The
  mirror failure is worse: a case-pinned ABSENCE check (`!text.includes('Income')`)
  passes vacuously against 'INCOME TODAY' rendered right in front of it, so a
  'role X must not see Y' gate then verifies nothing. Presence and absence
  checks use the same case-insensitive match.
- Prefer structural hooks (role + accessible name, `aria-label`, `data-test` id)
  over display copy for structural claims — 'settings button is gone' is a query
  for the control, not the absence of a word. When a copy-pinned assert fails
  against UI written in the same session, dump the rendered text of the region
  FIRST and adjudicate check-vs-product before touching either: a wrong literal
  is as likely as a real defect — including a mis-specified expectation (an
  explicit "None" control asserted where absence encodes the default). When the
  product matches its own convention or the spec, fix the assertion; "fixing"
  correct behavior breaks working code.
- When the suite asserts against an interface CONTRACT, adjudicate
  check-vs-contract before check-vs-product: an assert that demands an
  implementation detail the contract never promised (a specific element tag
  for a component the contract allows as any container) is a harness bug —
  relax the check to the contract's interface and note the missing pin for the
  next contract. "Fixing" the app to satisfy an invented interface breaks
  compliant code.
- Accessible-name queries (`getByRole({ name })`) match substrings
  case-insensitively — pass `exact: true` when the name is a prefix of another
  control's label ('Next' vs 'Next month') or the query drives the wrong control.
- Ad-hoc stress suites can invert their check helper's arguments (a `t(name, bad, detail)` where the second arg means the attack SUCCEEDED) and carry permanent placeholder checks that always report ok; a process exit code can mean "ran to completion", not "passed". Read the helper definition before trusting any verdict column.

- Rows that every suite in the matrix ASSUMES exist must be owned by the
  shared seed, and shotgun cleanup must exclude them by construction (filter
  on instrumentation columns such as kind/source) — a broad delete sweeps
  seed-owned history fixtures away and later runs fail on the assumption.

## Execution workflow

- Parameterize the base URL (QA_BASE): same suites run against local preview
  AND the deployed site. Deployed runs are the real verification. Check each suite's DEFAULT base first — a suite defaulting to the production URL silently tests the deployed build instead of your working tree.
- Never pipe suite output through `tail`/`grep` to read the verdict: the
  pipeline's exit code is the LAST command's and node's failure is masked
  (`node suite | tail -1 && next` chains green over a red suite). Capture node's
  exit explicitly (write `$?` to a file, or `PIPESTATUS`) and read the suite's
  own summary line before committing.
- Long matrices get promoted to background processes; read their results before
  claiming green or committing.
- A `waitForURL` timeout does not mean a guarded submit failed (one-per-day / one-pending guards make every retry consume another allowed slot): re-check the current URL once before retrying the submit. Pin the contested resource per actor where the domain legitimately allows parallel use.
- Checks that cannot RUN on this machine (branded browser, missing tool, topology) go behind a dep-flag env and print a VISIBLE SKIP in the report — never delete the coverage to get green and never let them false-fail. (A missing FIXTURE is the opposite case: fail loudly or create it.)
- When delegating suite runs to subagents: they do NOT inherit your shell env —
  put shared credentials in the project's gitignored env file and put a load
  command in the brief (`export $(grep KEY .env.local)`); never paste secret
  values into briefs or steering text.
- Never run two suites concurrently against one shared database — nor alongside
  subagent workers mutating that same database — because cleanup helpers delete
  each other's fixtures mid-test; treat a batch-only failure as interference
  until a solo run reproduces it. A batch-only failure that reproduces SOLO in
  the same order but not alone is sequential residue: an earlier suite's
  leftover rows — bisect the order and inspect shared-entity fixtures first.
- **Deployed-claim verification: push success is not deploy success.** Before
  reporting a change as live: (1) confirm the platform built THAT exact SHA —
  read its deployment status (e.g. `gh api repos/OWNER/REPO/deployments` filtered
  to the sha, then `/statuses`); a blocked or missing deployment means the OLD
  build is still serving. (2) If the Git-integration pipeline blocks content
  commits while shipping empty ones (observed on Vercel Git integration), unblock
  with `git commit --allow-empty -m "Trigger deploy"` + push, then re-poll the
  status. (3) Verify the LIVE artifact: run the suite that asserts the new
  behavior against the deployed URL (QA_BASE) — an entry-bundle string grep is
  only a fast first signal and can mislead when strings live in lazy route
  chunks. Never report 'live' from push success or local green alone.

Selector-, timing-, and flow-level pitfalls (route-chain grounding, transient-screen freezing, conditional forms) plus probe/crash triage (evaluate hangs, mutual-recursion renderer kills, 404-script TypeErrors) live in `references/playwright-pitfalls.md`. Report-semantics, retry-poisoning, and full-matrix triage for live-backend suites live in `references/live-backend-suite-repair.md`.

## Screenshot & responsive-audit harnesses

- Multi-viewport sweeps must reuse ONE authenticated page per role and call
  `setViewportSize()` per viewport. Opening a fresh page per viewport
  (`ctx.newPage()`) starts a new tab with empty per-tab session storage — on
  apps with per-tab auth (deliberate design) every page then audits the LOGIN
  screen, and the report fills with cascading "missing nav / missing tabs /
  missing content" findings on every route. Hundreds of near-uniform findings
  across ALL routes = suspect the harness's session state before the app.
- Role logins in such a harness need a bounded retry plus a landed-check (an
  authenticated landmark like `nav`/`aside` is visible) before proceeding — the
  post-login redirect races, and a harness that continues on the login page
  silently audits the wrong screen.
- Teardown each role's page via its context (`pg.context().close()`); closing
  the page alone leaves the context and its auth state lingering.

## Vision-model UI review (when used as a verification surface)

Triage every vision finding against capture artifacts BEFORE treating it as a
defect: fixed-position chrome (sticky headers, bottom bars, sticky footers) and
dev-only badges flatten into full-page screenshots and appear to overlap
content; OCR misreads hyphenated text as clipped or stray characters; text
truncating at a card's content edge is a deliberate app-wide convention, not
clipping; text cut mid-sentence at a natural scroll fold is complete content
below the fold (ground truth: `scrollHeight` > `clientHeight` on a scrolling
container, no clip on the text itself) — never "fix" it with padding; and an
element that appears occluded only at mid-scroll (composer over cards, sticky
bar over rows) clears at the scroll end — measure both rects at the actual
scroll position before calling it overlap. Confirm suspected overlaps with a region crop or pixel-extent/rect
measurement before "fixing" anything, ground contrast claims in
`getComputedStyle` color pairs and width-alignment claims in
`getBoundingClientRect`, and judge against the app's own
conventions — a large share of vision-pass findings are capture or perception
artifacts, and patching them wastes real polish time. The converse also holds: after layout changes, run
vision as a defect-finder alongside programmatic probes — it sees styling
defects DOM assertions cannot (SVG stroke/fill hardcoded to a token equal to
the actual background renders invisible edges; adjacent chips/labels run
together at narrow widths), while DOM/computed-style probes ground-truth its
over-reports. Confirm every vision claim at full resolution AND
programmatically before patching either side.

## Release gate & freeze

For a final QA / defense / release pass: re-run the full matrix at HEAD (prior
green is not evidence at a new commit), and run ONE consolidated adversarial
probe suite that ATTEMPTS every named hostile operation with real role sessions
— including privileged RPC execute grants, the backdoor beside RLS table
policies. Fix only real defects, security-boundary breaks, requirement
violations, reproducibility gaps, or build issues; "could be cleaner" is not a
fix. Classify findings before fixing: P0 = security/data-integrity, P1 = correctness/maintainability, P2 = polish — fix all P0 and the safe P1s in one pass, defer P2s with named reasons rather than churning a green codebase. When the audited app was PORTED from a reference codebase, first classify each finding as INHERITED from the source or INTRODUCED by the port — diff the corresponding source file before touching anything. Inherited design nits (tap-target sizes, spacing, copy) are reported as risks, not "fixed": restyling them silently breaks fidelity with the read-only reference. Likewise, a file the port "lacks" must be checked in BOTH repos before calling it a gap — a designed merge or rename (a page folded into another route) looks like a missing file in one direction of the diff. Prove parity with a both-directions file diff (`comm -23`) plus feature spot-checks read from source, never from commit messages. A user-set "N fixes" budget is a CEILING, not a quota: "0 real defects found" is a valid, reportable outcome — never manufacture work to fill it. The freeze includes the documentation sync gate: docs sources + generated artifact must match HEAD (see `portable-engineering-docs`). Report exact per-suite counts with each suite counted once, separate
VERIFIED from NOT-VERIFIED (no fabricated device tests), then FREEZE: further
priorities become demo reliability → defense preparation → documentation →
presentation, not more engineering. Deliver the audit by UPDATING the project's
canonical release/audit document in place when one exists — do not add a new
report file per pass.

## Overlap note

External skills `browser-qa`, `e2e-testing`, `ai-regression-testing` cover
adjacent ground; this skill is the standing quality bar and maintenance rules
for suites we write and keep green.