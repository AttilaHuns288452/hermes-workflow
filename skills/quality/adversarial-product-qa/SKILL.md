---
name: adversarial-product-qa
description: Use when stress testing or adversarially QA-ing an app.
---

# Adversarial Product QA

Break the app on purpose, across every role, before a real user does. The goal
is discovering failures, not collecting PASS results. Works for pre-release
stress tests, "try to break it" prompts, and multi-role release audits.

## Always-on rules

- **Document before fixing.** During the audit phase, change nothing. Findings
  come first in the mandated report; fixes come only when the user says fix.
- **Prove, don't assume.** A screen looking right is not a PASS. Trace: actor →
  UI action → frontend state → query → DB mutation → resulting state → other
  roles → refresh → persistence.
- **Test-harness mutations are test damage.** Every write-probe must be undone:
  restore touched fields to their prior values and delete only rows the probe
  created (match by created IDs, never by entity name — seed data shares names
  with test fixtures). Disclose any damage you caused and its restoration in
  the report.
- **Your probes can lie.** Before trusting a BREAK verdict, re-read the probe's
  assertion polarity and what it actually measured (see
  `references/backend-attack-probes.md`). A bug found in the harness is not a
  bug in the app.
- **After fixes, the battery is the regression suite.** Re-run it plus the
  project's existing suites; "fixed" without a re-run is a claim, not a result.

## Procedure

### 1. Test inventory

Enumerate roles, every action per role, shared vs role-specific pages,
protected routes, and features that visually appear but may not be functional.
This inventory is the coverage contract for the report matrix.

### 2. Adversarial battery (document-only)

Run all layers; each finding gets evidence, not suspicion:

1. **API abuse matrix** with throwaway attacker accounts: forged state on
   inserts (self-confirmed records, money fields, status fields), field tamper
   on updates, cross-user reads/writes, destructive ops, double-submit and
   parallel races, oversized/empty payloads on privileged RPCs.
2. **Data-integrity sweep**: orphans, duplicates vs unique constraints,
   impossible status combinations, unlinked ledgers, dead/junk rows.
3. **UI battery** per role: auth edges (bad creds, empty, session persistence,
   post-logout back button, deep links into other roles), negative form input
   (long strings, HTML, wrong types), double-click submits, search/filter/sort
   cases, every-button sweep for dead controls.
4. **Cross-role sync scenarios** in separate browser contexts: one role acts,
   the other refreshes and must see it. Test cancel/complete paths and who is
   allowed to run them.
5. **Independent recompute** of any displayed totals from raw rows — never
   trust an analytics number you did not recalculate.
6. **Fake-functionality sweep**: grep for hardcoded numbers/labels, verify
   each claimed feature has a backend path (`UI action → query → table →
   mutation → UI`), mark gaps FAKE / FRONTEND-ONLY.
7. **Responsive** at small-mobile / tablet / desktop for every major route
   (horizontal overflow is the cheap signal).

### 3. Bug report (mandated shape)

Use `templates/bug-report.md`. Every finding: `[BUG-NNN]` + role, screen,
severity, precondition, numbered repro steps, expected, actual, Figma/design
expectation, DB behavior, cross-role impact, likely root cause, recommended
fix. Severity: **P0** security/data corruption/impossible workflow/role
bypass · **P1** major feature or cross-role inconsistency missing · **P2**
meaningful UX/data issue that doesn't block · **P3** copy/visual/polish.
Close with the system matrix and the acceptance gate checklist. Report
anything untestable as NOT TESTABLE — never fabricate coverage.

### 4. Fix pass (only after the user approves)

Fix root cause where all callers route (one guard in a shared trigger/function
beats a guard per screen). Money and security paths get a runnable check —
keep the attack battery as a committed script (`verify_fixes.mjs`-style) and
leave it green.

### 5. Multi-auditor cycles ("fix, then repeat until clean" mandates)

- Audit wave: parallel document-only auditors over the same surface with
  disjoint lenses (visual design / UX + accessibility / responsive +
  interaction). Each emits lane-numbered findings (`[V-NNN]`/`[A-NNN]`/
  `[R-NNN]`) carrying severity, route + repro, measured evidence (rects,
  contrast values, hit tests — not impressions), proposed fix, and how to
  verify. Auditors change nothing.
- Fix wave: one worker per finding-ID group with disjoint FILE ownership;
  briefs name exact routes, strings, and behavior contracts. Verify claimed
  edits with a diff before trusting a completion message. The orchestrator
  owns shared runtime (dev server, DB): a server spawned inside a subagent
  dies with its session, so start and health-check it centrally before
  verification.
- Suites are shared code: apply the same-change harness sweep from Pitfalls
  to the whole wave (copy/contract changes kill locators and asserts), and
  classify each failure — stale expectation = harness debt, spec-mandated
  content the change dropped = product bug.
- Next cycle: fresh auditors regression-verify the previous fixes BY ID
  (VERIFIED/REGRESSED per finding) and re-cover areas that were excluded
  while fixes were in flight. Stop only when a cycle finds no real defects;
  per-cycle rubric scores (/10 with reasons) and counts come from harness
  output, not from worker claims.

## Reference reconciliation (when design docs exist)

Establish the source hierarchy before judging mismatches:
**latest intended state > newest reference set > older artifacts**. Demo
videos = behavior/flow truth; design frames = visual/layout truth;
accumulated user feedback = regression tests — flows the user previously
rejected must NOT reappear just because an older reference contains them.
Never grade the app against superseded artifacts. Detail:
`references/reference-hierarchy.md`.

## Pitfalls

- RLS-blocked UPDATE/DELETE often returns `error: null` with 0 rows — judge by
  rows affected + read-back, or you will report "accepted" for a blocked call.
- An assertion helper given a Promise prints the same verdict every run —
  never pass an async IIFE straight into a boolean parameter.
- Ad-hoc `t(name, bad)` flag helpers invert polarity under pressure; have the
  helper print expected vs actual, or re-verify every BREAK line before
  reporting it.
- Fixtures that collide with DB unique constraints (same slot/date/row) make
  reruns fail for harness reasons — use dynamic per-run values.
- After a deliberate UI or behavior change, sweep the harness in the same
  change (a replaced component kills every locator for it) and classify each
  resulting failure before touching either side: a dead locator or stale
  expectation is harness debt — update the assert to the NEW contract; content
  or behavior the spec mandates but the refactor dropped is a product bug — fix
  the code. Keep asserts on the spec's literal content lines through refactors.

## See also

- `references/backend-attack-probes.md` — Supabase/PostgREST probe semantics
  and the attack checklist.
- `references/web-harness-pitfalls.md` — Playwright locator/harness traps.
- External (read-only) overlaps: `production-audit` (readiness scoring),
  `audit-verify-explain-grade-5` (evidence discipline), `e2e-testing` (POM
  patterns), `silent-failure-audit` (hunting swallowed errors).
