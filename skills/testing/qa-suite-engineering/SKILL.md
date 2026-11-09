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
- **Never wrap the operation under assertion in a bare `try/catch` that
  swallows.** The suite then reports green on the exact failure path it exists
  to detect (a settle call that aborts every run, a mutation that always
  throws). Wrap only to CAPTURE the error and assert its expected shape
  explicitly: the call must succeed, or raise the one documented semantic
  error — anything else is a FAIL.
- **A catch-and-log inside the UNIT under test defeats "does not throw /
  degrades safely" assertions.** Code that swallows its own crash and returns
  a fallback passes the suite while the thing it was supposed to produce is
  silently missing. Assert the rendered output's shape/content too (non-empty
  nodes, expected labels), and scan even a GREEN run's stdout for `failed`/
  `error` lines before trusting the pass count — the swallowed crash prints
  there while every assertion goes green. Pair with the fix rule: optional
  fields in declarative specs legitimately arrive absent (tests, generated
  data), so coerce at the use site (`String(x || '')` before `.slice()`)
  instead of trusting the spec to carry a value.
- **Intervals started by UI code hang `node --test` silently** — the runner
  waits for the event loop, so a leaked `setInterval` (autoplay beats, preview
  restart loops) reads as a suite stuck at its timeout cap with NO fail line,
  not as a failure. Dual-environment timers must `unref()` when the handle
  supports it (browsers return a number — guard the call) or expose a teardown
  the fixture calls; treat a no-output timeout as a timer-leak hunt before a
  logic hunt.
- **A missing/undefined row must fail the check, not pass it vacuously.**
  Negation assertions (`!(a && b && sameDentist)`, `a?.status !== 'approved'`)
  and count checks compared as `0 === 0` pass when every read returned nothing.
  Pre-assert the rows exist (`rows.length === N` / non-null) and FAIL on empty
  reads before evaluating any invariant over them.
- **A state-gated action's absence is a fixture error until proven otherwise.**
  Before reporting a control missing, check the fixture's row state against the
  feature's gate (a receipt action that renders only on paid/completed rows,
  an edit affordance only in edit mode) — pointing the check at the wrong
  state false-fails correct behavior and sends you hunting a phantom bug.
- Assertions pinned to UI copy must change in the SAME commit as the copy — grep the suite tree for the old name and update every driver that clicks by accessible name in the same pass. When sweeping for old labels or class names, a `search_files`/rg pattern starting with a dash is parsed as a CLI flag (`error parsing flag`) — drop the leading dash and match the stem (`mb-28`, not `-mb-28`).
- Every UI-driving click in a long matrix suite goes through the same capture
  wrapper as the asserts: an unguarded `.click()` on a locator a rename
  killed raises an uncaught TimeoutError that kills the process mid-run and
  discards every remaining verdict. One stale locator must degrade to one
  FAIL line, not a dead run.
- **A passing existence check does not make the element actionable.** `count() === 1` is satisfied by a hidden node (a panel that must be opened, a sub-view inside a container), so the next bare click times out — assert `isVisible()` for any affordance claim, not `count()`. In exclusive-workspace layouts (one full-area view visible at a time) every flow step must switch to the owning workspace first, exactly as a user would; a flow that outlives a workspace switch will time out on the first control of the previous workspace.
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
- **Capture-after-sleep loses to full-page loading states.** When a screen renders a page-level skeleton until its fetch resolves (not just inline spinners), a text assertion captured after a fixed `waitForTimeout` reads empty content under load and fails checks whose deeper click-based siblings pass (clicks wait for their target). Capture assertions must waitFor the TARGET CONTENT being asserted — blind sleeps race the fetch. The subtler form: the wait selector matches a placeholder node that exists BEFORE content (an empty pending bubble that later becomes the answer container) — with any post-render enrichment stage (LLM polish, async rewrite), wait on the content-bearing child (`.answer` / non-empty text), not the message wrapper. Getting this wrong has a diagnostic fingerprint: within ONE run a locator fails its count/visibility check while a sibling text check on the same element family passes moments later — content landed mid-run and the wait anchored pre-content.
- `textContent` misses input VALUES (edit-mode fields render as inputs, not text) — assert via `input.value` or a server-side read; and `button[type="submit"]` misses default-type submit buttons (a bare button has no type attribute) — select `button:not([type="button"])`.
- State attributes beat text for toggles and counters. A composite control
  (icon + label + live count) gives `innerText` ad-hoc separators, so a regex
  over its rendered text false-fails against correct behavior — assert
  `aria-pressed` / `aria-checked`, or read the count node's own text. When a
  text check does fail, put the RENDERED text in the FAIL detail so adjudicating
  check-vs-product is one look instead of a debugging round.
- Read back generated harness files after writing them: a regex authored
  through layered tool calls (a Python string inside a call that patches a
  file) arrives with backslashes double-escaped (`\s` lands as `\\s`), so the
  pattern silently stops matching and false-fails against correct behavior.
  Prefer state assertions, or verify the assertion lines landed as typed before
  trusting any FAIL.
- A `:focus-visible` styling check must drive REAL keyboard navigation (press Tab / Shift+Tab, assert the focused element's computed style) — programmatic `element.focus()` sets `:focus` only and the check false-fails against correct styling.
- Cross-user visibility/protection checks must carry the row through its
  publish gate first (approve / confirm / settle): pending rows are invisible
  to other users BY DESIGN (RLS), so an ungated row false-fails as a broken
  share, vote, or visibility feature. Drive the gate as its own asserted step
  through the approving role's real UI — it doubles as coverage of the
  moderation flow.
- A QA probe that intentionally forces a failure (bad fetch, forced error state) must clear or exclude the error log it deliberately triggers before the suite's final zero-page-errors gate — otherwise the gate fails on the harness's own fixture.

## Fixtures and isolation

- Fake-DOM/sandbox fixtures must mirror the real page's container NESTING, not
  just its ids: when a refactor moves rendering into a new container (a library
  div inside the workspace root), mount and nest it in the fixture the same way
  — descendant-scoped assertions (`children of view-X`) false-fail when the
  fixture mounts the new container as a root sibling, and the reverse nesting
  mistake false-passes. A fixture builder that runs before its DOM helpers are
  in scope crashes the whole fixture; use the builder's own local document
  shim, not test-body lookup helpers.
- Hand-rolled harnesses that load app modules from an explicit file list must
  gain EVERY new client module in the same commit that adds the file — a module
  the fixture never loads dies with an undefined-global at first call, and the
  failure lands in whichever test touches it first. Grep the harness's load
  list before concluding the new code is broken.

- Self-contained: create the rows you need; never scavenge for pre-existing
  state (environment-dependent, fails on clean DBs).
- An upstream data outage (quota exhaustion, dead feed) emptying the surface
  under test is not a reason to skip live verification: insert a clearly
  labeled temporary fixture through the app's own write path (admin UI or DB),
  exercise the feature end-to-end against it, then delete it and verify the
  deletion. The feature gets verified while the outage is still the outage.
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
- A shared helper with its own default login REPLACES the caller's actor for everything after it; under row-level security the symptom is an empty result ("nothing to settle" / "no pending rows") for data the UI just created, not an auth error. Thread the acting user's session through explicitly, and grep helper defaults for hardcoded credentials when a flow finds 'no rows' its own steps just produced.
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
  Corollary: icon buttons must carry real `aria-label`s — a bare-glyph query
  (`name: '+'`) collides with ANY visible label containing the glyph
  ('+ Add Transaction') the moment a trigger keeps its label while its modal is
  open. And a strict-mode collision can surface through a custom error
  formatter as "waiting for <locator>" — "waiting for" does NOT mean "not
  found"; check `count()`/`all()` before hunting for a missing element.
- Adding a NEW control to an existing form or section breaks the suite's singular
  role queries even when no label changed: a bare `getByRole('combobox')` scoped
  to the section, or a `count() === 1` contract, turns strict the moment a second
  select or a same-named button appears (a new "None" option chip collides with
  the existing "None" date-clear button). Before adding a control, grep the suite
  for role queries scoped to that section; then either give the new control a
  different role/shape (chips instead of a second `<select>`) or update the
  suite's locator in the same commit. Distinct labels beat `exact: true` sprinkles.
- Splitting one field into two is the same trap from the other direction: the old label becomes a prefix of both new fields and `getByLabel(old)` resolves to two elements (strict-mode violation) — update every suite locator for that field in the same commit the split lands.
- A validation-state change breaks submit flows silently: making a field REQUIRED (or adding a required consent checkbox) that flows used to submit without breaks every registration/edit driver on that form — the failure surfaces at the submit step as a timeout waiting for the success screen, far from the cause. When tightening validation, grep the suite for every flow that SUBMITS the form, not just the changed label.
- Regex label checks break when a word is inserted mid-phrase even
  case-insensitively (`/keep appointment/i` no longer matches "Keep my
  appointment"). When editing button copy, grep the suite for the label's
  multi-word phrases and regex alternations, not just the old literal.
- A pass TOTAL that changes between runs with no FAIL line means a
  dynamically-registered check (loop-, data-, or time-window-dependent) ran
  fewer times — compare which checks ran (identities or static call sites), not
  the totals, before treating the delta as a regression.
- Ad-hoc stress suites can invert their check helper's arguments (a `t(name, bad, detail)` where the second arg means the attack SUCCEEDED) and carry permanent placeholder checks that always report ok; a process exit code can mean "ran to completion", not "passed". Read the helper definition before trusting any verdict column.

- Rows that every suite in the matrix ASSUMES exist must be owned by the
  shared seed, and shotgun cleanup must exclude them by construction (filter
  on instrumentation columns such as kind/source) — a broad delete sweeps
  seed-owned history fixtures away and later runs fail on the assumption.

## Execution workflow

- Parameterize the base URL (QA_BASE): same suites run against local preview
  AND the deployed site. Deployed runs are the real verification. Check each suite's DEFAULT base first — a suite defaulting to the production URL silently tests the deployed build instead of  your working tree.
- **When a route shift moves the screen under test** (a landing page takes
  `/`, the app moves under `/app`, a legacy surface takes a prefix), re-point
  every suite's `goto` in the same commit that moves it. The stale entry URL
  then audits the wrong surface — a marketing page where the app was — and the
  report fills with cascading "missing app chrome" findings; hundreds of
  near-uniform missing-element findings across flows = suspect the entry URL
  before the app.
- Ad-hoc probes written outside the suite must reuse the suite's own auth bootstrap (read its login/session-injection helper and copy it) — guessing the storage key or session shape wastes a diagnostic cycle and false-fails the flow under test.
- Flow-terminal screens (success / receipt / detail) usually accept a `?id=`
  deep link that re-fetches by id — drive them directly with a fixture in the
  right state instead of replaying the whole upstream flow in every check.
  Confirm the deep link is authoritative (re-fetches, not just a state cache)
  before relying on it.
- Never pipe suite output through `tail`/`grep` to read the verdict: the
  pipeline's exit code is the LAST command's and node's failure is masked
  (`node suite | tail -1 && next` chains green over a red suite). Capture node's
  exit explicitly (write `$?` to a file, or `PIPESTATUS`) and read the suite's
  own summary line before committing.
Long matrices get promoted to background processes; read their results before
claiming green or committing.
- A harness that gates a product is product code: keep it in the repo (`qa/`,
  `test/`) and commit it. Scratch-dir cleanup destroys a `/tmp` harness between
  sessions, and the from-memory rebuild drifts selectors (`.cite-chip` vs
  `button.citation-chip`; a hidden input vs the styled label around it), which
  surfaces as phantom product failures. Ground-truth every selector from a live
  DOM dump before writing checks against a rebuilt harness.
- A `waitForURL` timeout does not mean a guarded submit failed (one-per-day / one-pending guards make every retry consume another allowed slot): re-check the current URL once before retrying the submit. Pin the contested resource per actor where the domain legitimately allows parallel use.
- **Confirm-gated actions need the full trigger → confirm → post-state sequence.** Destructive or irreversible controls (logout, delete, void, cancel) open a confirmation dialog; a driver that clicks only the trigger leaves the app unchanged, and every later step that assumes the action happened cascades into false failures (no login form to fill, stale rows still present). When a step times out on something an earlier step "already did", check that step for a confirm dialog before hunting app bugs.
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
- **Local stale-process trap: green tests are not the running server.** Tests
  import modules fresh per process and pass while the long-lived dev/E2E server
  still serves pre-change code or pre-change env (server modules and env are
  read at process start / require time). Restart the server after ANY
  server-side or env change BEFORE trusting browser/E2E results. When E2E
  shows behavior that green tests prove impossible, check the server's start
  time against the change before debugging the app.
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
- **Route-completeness sweep — the "nothing missed" net.** After broad UI changes
  or a port from a reference codebase, log in once per role and `goto` EVERY
  route, asserting each renders real content (body text present AND not an
  error/placeholder/empty shell) with ZERO console/page errors accumulated across
  the whole run; screenshot each route. Diff-scoped runtime checks and green
  unit/contract tests never touch the routes the change didn't name — a broken
  import, blank screen, or console error on an unrelated page surfaces only here.
  Assert the rendered body's shape (`innerText.length > N && !/coming soon|not
  found/i`), never a bare load/200 — a login page or placeholder renders fine and
  passes a load-only check. Report line is `N routes × R roles rendered, M issues`
  computed from the run; anything less means the sweep didn't complete. Pair it
  with targeted edge-case interaction tests on the changed surface (open → act →
  Esc/back-out → assert no unintended mutation) — the sweep proves nothing is
  broken, the edge tests prove the change behaves at its boundaries.

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
scroll position before calling it overlap. When the rects show REAL occlusion persisting at max scroll (nothing left to scroll to), fix it as wrapper clearance: deepen the wrapper's bottom padding AND the pinned child's matching negative margin together — a solo padding change is swallowed by the margin and silently no-ops; verify at max-scroll geometry, not at rest. Confirm suspected overlaps with a region crop or pixel-extent/rect
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