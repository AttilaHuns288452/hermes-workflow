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

## Harness interaction vs app bug

A content area that renders fine standalone — including after replaying the preceding test section — but blanks only under a full stress run is a harness interaction, not an app bug. Capture it as a known limitation with its reproduction context (in the report's Remaining section); do not patch the app against a state only the harness produces.
