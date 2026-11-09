---
name: self-healing-automation
description: "Use when writing repair scripts, watchdogs, or health jobs."
triggers:
  - repair script
  - re-apply patches
  - self-healing
  - watchdog
  - health check job
  - silent failure
  - incident not delivered
---

# Self-Healing Automation

Author and audit self-healing automation (repair scripts, watchdogs,
health-check jobs) for the Hermes install.

Reliability chain every automated mechanism must complete:

```
DETECT -> RECORD -> NOTIFY -> DIAGNOSE -> REPAIR -> VERIFY -> ESCALATE
```

A chain that stops at RECORD is monitoring without notification: the detector
stays perfectly healthy while the failure runs for weeks. Never "fix" a
detector that is correctly reporting a real outage — classify first:
detector / application / infrastructure / dependency / configuration /
operational / observability / recovery / verification failure.

## Repair / re-apply scripts

A repair script is not successful because it changed files. Contract:

1. **Each patch's guard tests its OWN definer** (`def _load_x`, `async def _y`,
   the marker it inserts) — never text another patch inserts. A call site
   added by patch 1 disables the guard of patch 2 that must install the method:
   the file ends up half-patched and dies at the first call.
2. **The health check demands exactly what the repair can install.** A check
   for an artifact no patch creates is a permanent failure loop
   ("repairing... failed" on every run, forever).
3. **Success = end state verified.** Re-run the check after applying.
   "Something changed" is not "repaired" — a half-patched file changed too.
4. **Idempotent.** Re-running on a healthy file changes nothing and reports healthy.
5. **Script and docs stay in sync.** If the owning doc lists N patches, the
   script installs and checks N patches; extend both in the same change.
6. Substring guards are acceptable only on the patch's own inserted text;
   prefer structural checks (definition exists, dependent call sites consistent)
   where cheap.
7. Fail loudly and specifically ("end state incomplete: missing X") so the
   incident is actionable.
8. Prefer upstream over obsolete patches: if upstream implemented the fix (often
   better), delete the patch from the docs and mark its backup file
   do-not-apply instead of preserving it.

## Notification semantics

- Scheduled-job failure notices are suppressed when delivery is `local`. Set a
  real `--failure-deliver` target on every job whose failure matters, and
  verify via the jobs store (`~/.hermes/cron/jobs.json` — the list output does
  not show the field).
- A watchdog's schedule is its worst-case detection latency. Failures that
  matter within the hour cannot live behind a daily check.
- A watchdog that prints only when sick is safe to point at a live chat; one
  that prints status every run is noise and gets ignored.

## Threshold sizing

- A tolerance must separate the noise floor from the bug class it targets. Bookkeeping skew of
  cents on a dollar-valued sum is normal; a unit bug is orders of magnitude. Use
  `max(abs_floor, pct * value)`, not a fixed epsilon.
- Size absolute thresholds to the host, not to generic percentages: a "disk < 15%" rule on a
  large disk is a permanent alarm, i.e. a disabled check. Pair absolute caps (db size, cost)
  with the known post-maintenance baseline so drift is measurable.
- A check that fires on every run is ignored within a week. Tune until healthy runs are silent,
  and keep one `# why this number` comment beside each threshold so the next tuning pass knows
  what it was sized against.

## Verification standard

"Fixed" means the expected invariant is now true. A compile pass is not
runtime capability; a successful repair command is not a successful repair.
State explicitly what was runtime-verified and what was not. Exit code 241
from a script job = SIGTERM (scheduler restart collateral), not a script bug.
