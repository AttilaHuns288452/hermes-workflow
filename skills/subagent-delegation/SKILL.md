---
name: subagent-delegation
description: "When and how to delegate to subagents. Models come from config.yaml — orchestrator = model.default, delegate = delegation.model, vision = auxiliary.vision. Never hardcode model IDs here."
version: 2.0.0
author: Hermes Agent
triggers:
  - delegate
  - subagent
  - coding agent
  - delegation
  - vision
---

# Subagent Delegation & Model Roles

## Model Roles (config-derived — never name IDs here)

| Role | Source of truth | When |
|------|-----------------|------|
| **Orchestrator / Planning / Architecture** | `config.yaml` → `model.default` | Understanding tasks, delegation, architecture decisions, reviewing output. Does not implement product code. |
| **Delegate / Implementation** | `config.yaml` → `delegation.model` | ALL substantial coding, git, deploy, build, patches, multi-file edits — via `delegate_task`. |
| **Vision** | `config.yaml` → `auxiliary.vision` | Image/screen analysis. Simple inline checks may use `vision_analyze` directly; heavy multi-image visual audits go to a delegate with the image attached. |
| **Fallback** | `config.yaml` → `fallback_providers` | Automatic on provider failure; do not hand-route unless the ladder demands it. |

If this table and config disagree, config wins — and patch this file.

## When to Delegate vs Go Direct

**Delegate:** features, refactors, multi-file edits, builds, anything touching `~/Documents/Projects/` product code, parallelizable independent work (batch `delegate_task(tasks=[...])` — one entry per agent, agents don't share files).

**Direct is fine:** ≤3-line diffs, bounded one-off ops, Hermes-internal maintenance (skills/config/cron/scripts), when delegation overhead exceeds the work.

**Known constraint:** delegate children can time out writing one huge file in a single go. For big single-file builds, instruct sectioned writes (write the skeleton, then append sections).

## Brief Discipline

A delegation brief is decision-complete: goal, success criteria, interfaces, expected files, edge cases, test criteria, assumptions. Every unknown either resolved by exploring before delegating, or asked as one batched question with a recommended default.

Read-only subagents (exploration/planning/review) get read-only instructions verbatim. A planning subagent that edits has escaped its contract.

## Post-Delegation Verification (mandatory)

Never relay a child's "done" as success:
1. Read back actual output — files exist, state changed
2. Run the relevant test/build/check from the brief
3. For substantial Tier-3 work: `hermes verify <project>` records evidence
4. Only then report, with evidence

## Visual QA Pattern (when interfaces are involved)

1. Orchestrator plans (minimal spec, single-file when sensible)
2. Delegate implements
3. Render the result (browser/screenshot) → `vision_analyze` or delegate-with-image for the audit
4. Orchestrator reports: code-path trace + visual findings together

Full recipes in `references/` of this skill.

## Model-Switch Rule

Don't switch models per-task unless the current one demonstrably fails (timeout on large writes, repeated malformed output). First remedy: smaller briefs / sectioned writes, not a different model. Provider fallback is config-automatic.
