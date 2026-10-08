---
name: release-audit
description: Use when auditing a frozen app before demo/defense/release.
triggers: [final release audit, release gate, final hardening, release readiness audit, freeze audit, pre-demo audit]
---

# Release Audit

Audit an app that is claimed release-ready. The deliverable is evidence-backed
verdicts and a freeze decision — not more code. Standing rules come from the
user; the pipeline below is the order of work.

## Standing rules (every audit)

- **If everything is green, STOP.** Do not manufacture work; do not refactor
  stable code because it could be cleaner. Fix only real defects, security
  breaks, requirement violations, reproducibility gaps, build failures.
- **Do not create another report file.** These projects accumulate REPORT_*.md;
  update the CANONICAL release document in place with the audit result.
- **Never trust the prior report.** Re-run build + the full suite matrix at the
  current HEAD; a stale report's numbers (old commit, missing suites) are a
  finding in themselves.
- **Harness-vs-product triage before any fix.** A failing check is a harness
  defect until proven otherwise: check fixture residue, stale selectors, timing
  assumptions, and env before touching product code. Root-cause the harness bug
  even when "re-run and it passes" would be faster — the flake class is the bug.
- **Data hygiene is a report first, deletion second.** Inventory what looks like
  test/demo data, classify KEEP (demo story) vs JUNK (fixtures), state
  dependencies and a safe deletion plan — destructive cleanup waits for the
  user's OK.
- **Design gaps are classified, not chased:** (A) functionally required,
  (B) presentation/demo polish, (C) intentionally out of scope. Old design
  checkpoints go stale — verify whether "NOT BUILT" items actually ship now
  before accepting them as gaps. The goal is functional correctness + demo
  reliability, not full design reproduction.

## Pipeline

1. **Verify real state** — read the release report + docs, then re-run `npm run
   build` and the full suite matrix independently (per-suite exit codes
   captured; see `qa-suite-engineering` for runner discipline).
2. **Find regressions** — routes, role leakage, back/refresh, capacity,
   payments, finance/audit, EHR/storage, notifications, deactivated-account
   behavior, mobile, prod-vs-dev, console errors. The suites cover most of
   these; targeted probes fill gaps.
3. **Human-defense checklist** — the manual flows only a human can physically
   do (devices, real payment scan, projector walkthrough, cross-device races).
   Deliver as checkboxes, minimal.
4. **Data hygiene** — inventory → classification → deletion plan (rule above).
5. **Documentation consistency** — docs vs implementation (routes, function
   names, migration numbers, counts); run the repo's reference verifier if one
   exists. Fix drift in place; do not add documentation files.
6. **Design fidelity** — classify gaps A/B/C (rule above).
7. **Freeze** — fix only real defects → affected suites → full matrix → build →
   git diff + stray-file/secret scan → write the audit into the canonical
   document → recommend ship or block.

## Report

Use `templates/release-audit-report.md` (the user's 15-section format). Every
PASS/FAIL names the evidence (suite + counts, or the manual check). Separate
VERIFIED from NOT-VERIFIED; never invent test results or device claims.

## Overlap note

External `production-audit` (ECC) covers generic production-readiness scoring;
this skill is the user's release-freeze procedure and output format. If the
curator consolidates, fold this one's standing rules into it.