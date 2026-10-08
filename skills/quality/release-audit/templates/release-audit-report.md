# <Project> Final Release Audit

Audited at <commit> on <date>. Prior claims: <report/numbers — and whether they
still matched HEAD>.

## 1. Build
PASS/FAIL — build result + reference/doc verifiers.

## 2. Automated QA
X/X checks · N suites — full matrix at HEAD. Any first-pass failures get a
root-cause table here (failure → cause → fix → re-run), harness vs product
stated explicitly.

## 3. Security
PASS/FAIL + findings (adversarial suites, secret scan).

## 4. Role Isolation
PASS/FAIL — cross-role + navigation suites; DB-layer enforcement named.

## 5. Appointment/Scheduling
PASS/FAIL

## 6. Payments
PASS/FAIL

## 7. Finance/Audit
PASS/FAIL

## 8. EHR/Storage
PASS/FAIL

## 9. Notifications
PASS/FAIL

## 10. Navigation/UX
PASS/FAIL — routes, back/forward, refresh, loading/error states, console errors.

## 11. Data Hygiene
PASS/FAIL + KEEP vs JUNK table (record · why test · dependencies · safe plan) +
remaining test records. Nothing deleted without user approval.

## 12. Documentation
PASS/FAIL — docs-vs-code drift found and fixed; design gaps classified A/B/C.

## 13. Manual QA Required
Only what automation cannot physically do (devices, real payment scan,
multi-device races, projector walkthrough).

## 14. Remaining Known Limitations
Genuine limitations only.

## 15. Release Recommendation
READY / NOT READY — tied to the evidence above, one paragraph.
