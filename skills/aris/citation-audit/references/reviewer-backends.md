# Selectable Reviewers (Hermes adaptation)

This is the adapted replacement for the upstream reviewer-transport contract.
Upstream routed reviews through Codex/Antigravity/Grok/claude-review MCP bridges.
In this system the reviewer is an **independent subagent** dispatched with
`delegate_task` (see the `subagent-delegation` skill). Everything else in the
review step — prompt, evidence, fresh-context requirement, rebuttal, verdict
schema — is preserved exactly as the workflow skill demands.

## Selection

Selection order is **this invocation → project preference → default**.

- Default: one `delegate_task` subagent per review round, given only the review
  task and the primary input paths (no executor conversation history — the
  child starts clean, which satisfies the fresh-context requirement).
- The reviewer model comes from the configured delegation model When the user
  pins a reviewer ("have X review it"), pass `model`/`provider` on the
  `delegate_task` call instead of the default.
- Reviewer identity: record the model the child reports running on. If the
  executor cannot establish that the reviewer is a different model family, the
  review is `same-family / provisional`, exactly as upstream requires. Never
  record a family you did not observe.

## First call and continuation

- First call: `delegate_task` with the review prompt, explicit input file paths,
  and the required verdict schema in `output_schema` when the skill specifies one.
- Continuation (multi-round loops): a NEW subagent per round, passing the prior
  round's findings in `context` plus the fix summary to verify ("did round N's
  gaps get resolved"). Subagents have no persistent thread, so the accumulated
  reviewer memory travels in the context payload — do not assume thread state.

## Completion, identity and acceptance

- A child summary is a self-report: treat "review passed" as a claim until the
  verdict artifact (the child's returned verdict text or written file) exists.
- Timeout, interruption, or an empty/partial child return is `REVIEW_UNAVAILABLE`
  — never a fabricated PASS. Do not silently re-dispatch after an ambiguous
  failure without saying so.
- Deterministic gates (the bundled `tools/review_gate.py`, `tools/verify_papers.py`,
  `tools/verify_paper_audits.sh`) stay deterministic: run them with `terminal` and
  record their exit codes as evidence. A reviewer opinion never substitutes for
  a mandatory deterministic check, and a deterministic check never substitutes
  for the reviewer verdict.
- Trace every review round as the workflow skill requires (`references/review-tracing.md`),
  recording: round, reviewer model, verdict, and gate exit codes.
