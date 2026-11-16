# Review Tracing (Hermes adaptation)

Adapted replacement for the upstream trace-flag reference. Every review round
produces a trace record so acceptance is auditable after the fact.

## What to record per round

Use the bundled `tools/save_trace.sh` (or an equivalent JSONL append) with:

- run id, round number, skill name
- reviewer transport: `delegate_task` (the only route in this adaptation)
- requested reviewer model vs the model the child reported; if they differ,
  record the reported one and note the mismatch
- verdict + score exactly as returned (do not normalize)
- `--review-completed` / `--review-scope-complete` ONLY after those facts were
  checked; `--review-positive` only after the skill's own positive gate passes
- gate exit codes from `tools/review_gate.py` runs
- `--status error` for failed calls (timeout, provider error, empty return)

## Trace location

`.aris/traces/<skill>/<date>_runNN/` under the working directory: one state
file per run, one JSONL line per round. A verdict word alone is not positivity;
an incomplete or unavailable review never becomes a PASS record. Acceptance in
a trace does not replace a skill's submission, proof, citation, or experiment
gate — it records that the gate ran.
