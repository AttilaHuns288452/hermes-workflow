---
name: "auto-review-loop"
description: "Autonomous multi-round research review loop: an independent reviewer subagent scores a research artifact each round, the executor fixes, and the loop stops only on the acceptance gate. Use when the user says \"auto review\", \"review loop\", \"keep reviewing until ready\", or wants adversarial multi-round review of research, a paper, or a defense document."
---
# auto-review-loop — multi-round independent review

Adapted from ARIS's auto-review-loop for Hermes. The upstream skill routed
reviews through platform MCP bridges; here the reviewer is an **independent
subagent** (`delegate_task`, see `references/reviewer-backends.md`). The loop semantics —
rounds, scoring, verdict schema, deterministic gates, stop rules — are
preserved exactly.

## When to use

- A research artifact (paper, proposal, defense document, CBA, report) must be
  driven to "submission-ready" through repeated independent critique.
- The user wants adversarial review that does not stop at one pass.

Do NOT wrap this loop in an external timer (see `references/external-cadence.md`): cadence
can drive, it cannot acquit. Re-running a verdict on a wall-clock schedule with
no artifact change produces zero new signal at full cost.

## Roles

- **Executor** (this agent): produces/fixes the artifact and threads the loop.
  It never writes its own acceptance verdict.
- **Reviewer** (fresh subagent per round): scores and critiques. Round-to-round
  memory travels in the subagent context payload: each round's `context`
  carries the accumulated REVIEWER_MEMORY (prior findings + fix summaries) so
  the reviewer can check resolution against its own prior critique. A subagent
  has no persistent thread; do not assume one.
- **Deterministic gates** (`tools/review_gate.py` in this skill's bundle):
  record transport/completion/scope facts as evidence. A reviewer opinion never
  substitutes for a mandatory deterministic check and vice versa.

## Effort tiers

- `regular`: one review round at default depth.
- `hard`: reviewer reads the primary inputs itself (give it file paths, not
  conclusions) and returns per-claim findings.
- `nightmare`: `hard` + the reviewer reads the repo directly (read-only),
  the executor cannot filter what the reviewer sees.

Pick the lowest tier that matches the stakes; the user can raise it explicitly.

## The loop

**Step 0 — Snapshot state.** Create/extend the run state file
(`.aris/traces/auto-review-loop/<date>_runNN/state.json`): run_id, round,
effort, REVIEWER_MEMORY so far.

**Step 1 — Dispatch the review round.** `delegate_task` with:
- `goal`: the round's review prompt (the workflow's canonical prompt: what to
  evaluate, the verdict schema, the claim-vs-evidence obligations).
- `context`: primary artifact paths (+ raw evidence paths at `hard`/`nightmare`),
  plus accumulated REVIEWER_MEMORY and the fix summary since last round.
  Claims by the author must be clearly marked as claims, never as evidence.
- `output_schema`: {score: number, verdict: "ready"|"almost"|"needs-work",
  findings: [{severity, location, claim, problem, fix}]}.

**Step 2 — Record evidence.** Save the child's raw verdict text before
interpreting it. A timeout, interruption, or empty/partial return is
`REVIEW_UNAVAILABLE` — never a fabricated PASS, never a silent re-dispatch.
Then run the gate:

```bash
python3 <this-skill>/tools/review_gate.py --run-id <run_id> --round <N> \
  --verdict <verdict> --score <score> \
  --review-status ok --review-completed --review-scope-complete
```

Only pass `--review-completed` / `--review-scope-complete` after checking those
facts. Missing identity/completion/scope yields `review_unavailable`. Trace
every round per `references/review-tracing.md` (backend, reviewer model, verdict, gate
exit codes).

**Step 3 — Stop or fix.**
- **Positive stop:** score >= 6 AND verdict in {ready, almost} AND the round's
  mandatory deterministic checks passed. Record the external-finalizer line in
  the trace JSONL: run_id, round, verdict, score, executor model, reviewer
  model (as reported by the child), timestamp.
- **Otherwise:** executor fixes every finding (or documents why a finding is
  rejected with evidence), appends a fix summary to REVIEWER_MEMORY, increments
  round, returns to Step 1.
- **Hard ceiling:** stop after the configured max rounds (default 5) with a
  needs-work verdict rather than looping forever; surface the unresolved
  findings to the user.

## Rules

- Fresh subagent every round and every adversarial slot; the attack and defense
  slots never share context with each other or the executor
  (`references/fan-out-pattern.md`).
- Reviewer model identity: record what the child reports. Same model family as
  the executor = `same-family / provisional`, and the report must say so.
- The verdict schema is fixed; do not grade your own work.
- Integration obligations follow `references/integration-contract.md`; independence rules
  follow `references/reviewer-independence.md`; output artifacts follow
  `references/output-manifest.md` / `references/output-versioning.md`.
