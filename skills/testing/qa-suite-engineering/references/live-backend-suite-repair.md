# Flaky-suite triage (live backend)

When a suite fails intermittently or only in a full-matrix run, diagnose in this order before touching app code. The standing rules for this class are in the SKILL.md (Fixtures and isolation, Execution workflow).

| Symptom | Likely cause | Probe |
|---|---|---|
| Green standalone, red in the full matrix | fixture drift / run-order pollution | run the suite after each predecessor; grep suites for writes to the asserted column |
| "multiple rows" / maybeSingle error appearing intermittently | accumulating fixture rows | make the lookup newest-row; purge the extras in cleanup |
| Fail on a success banner after a long wait | guarded-submit retry poisoning | re-check the current URL before retrying the submit |
| Suite exits nonzero with no check output | crash before the summary block | tail the log — the summary prints only at the end |
| Stress-report lines read inverted (BREAK vs ok) | check-helper argument semantics | read the helper definition before parsing the report |
| Blank content only under full stress | harness interaction | verify standalone, including replaying the preceding test section |
| Structured "unavailable" refusal from a test affordance (simulate / sandbox / seed hook) | environment runs a stricter mode than the affordance allows | read the feature's mode/config setting; never flip a live mode to make tests pass |

## Harness interaction vs app bug

A content area that renders fine standalone — including after replaying the preceding test section — but blanks only under a full stress run is a harness interaction, not an app bug. Capture it as a known limitation with its reproduction context (in the report's Remaining section); do not patch the app against a state only the harness produces.

## Mode-gated test affordances

Test affordances (payment simulation, sandbox charge endpoints, fixture seed hooks) are often refused outside test mode by design. A structured refusal (e.g. 403 "unavailable") from such an endpoint is an environment-mode boundary, not an app defect: read the feature's mode/config setting to confirm, record the untestable path under Remaining with the mode as the reason, and never flip a production mode (or weaken the gate) to make the suite green — the gate is product security working correctly. The lifecycle around the gated transition can still be verified structurally (rows created on trigger, states visible to each role) while the transition itself stays NOT-VERIFIED until it runs in the mode that allows it.

## Classify before fixing (maintenance runs)

Every failure in a suite-maintenance pass is one of four things, in probe order:
1. **Harness/env** — the suite crashed before its checks (imports, cwd) or the check cannot run here (env gate). Fix or gate first.
2. **Fixture / world-state litter** — live rows contradict the check's premises (a leftover schedule row on a closed day, a missing seeded conversation). Probe the store the check asserts on; delete litter through the owning role's authenticated API when a direct delete is refused by a guard, and restore missing seed fixtures by re-running the shared idempotent seeder — never weaken the check to fit the litter.
3. **Suite drift** — the app moved ahead (locators, tab-gated panels, actor reassignment, copy). Fix the suite at the app's current surface.
4. **App defect** — the store state and the suite agree the behavior is wrong.

In a maintained codebase most failures in such a pass are 1-3; prove which side is wrong with a data probe or the design history before touching either. The report's Fixed section names the root cause per failure so the next drift cycle starts from the classification, not from scratch.

## Supabase REST probe notes

- Storage object delete: `DELETE /storage/v1/object/<bucket>` with a JSON body `{"prefixes":["folder/file.png"]}` — an empty body is rejected 400 'Body cannot be empty', unlike plain REST deletes which take no body.
- A service-key DELETE on a guarded table can be refused by the app's own guard/trigger ('availability is clinic-managed'); clean up through the owning role's authenticated API path instead of weakening the guard for test hygiene.
