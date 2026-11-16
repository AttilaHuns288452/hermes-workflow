# Reviewer Routing (Hermes adaptation)

Adapted replacement for the upstream reviewer-routing matrix (which mapped
platform hosts to MCP bridges). Here routing is one decision:

**Who reviews?** An independent subagent (`delegate_task`) that has not seen the
executor's conversation.

| Situation | Route |
|---|---|
| Default | `delegate_task` subagent, configured delegation model |
| User names a reviewer model | `delegate_task` with explicit `model` + `provider` |
| Executor and delegation model are the same family | Record `same-family / provisional`; say so in the report |
| Delegation unavailable (provider error, no credit) | `REVIEW_UNAVAILABLE`; run the deterministic gates only and label the review incomplete |

Fallback rules upstream kept for legacy routes (`oracle-pro`, `manual`,
`copilot`) do not apply here. There is no silent provider switching: if the
selected reviewer cannot run, the review step is unavailable, not waived.

Effort/tier knobs (upstream `reviewer effort`) map to `goal_mode` /
`goal_max_turns` on the subagent when a longer adversarial pass is wanted;
otherwise leave defaults and do not label any effort as observed evidence.

For adversarial pairs (see `references/fan-out-pattern.md`): dispatch the attack
and defense children as two separate `delegate_task` calls in one batch — they
must not share context with each other or with the executor.
