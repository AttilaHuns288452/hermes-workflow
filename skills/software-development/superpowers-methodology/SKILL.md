---
name: superpowers-methodology
description: Complete software development methodology from obra/superpowers — structured design → plan → TDD → review → finish pipeline. Use when starting a feature, fixing a bug, or building anything non-trivial.
version: 1.0.0
author: Prime Radiant / obra — adapted for Hermes Agent
license: MIT
tags: [methodology, workflow, pipeline, tdd, design, planning, review]
related_skills:
  - brainstorming
  - writing-plans
  - executing-plans
  - subagent-driven-development
  - test-driven-development
  - systematic-debugging
  - requesting-code-review
  - finishing-a-development-branch
  - using-git-worktrees
  - verification-before-completion
triggers:
  - superpowers methodology
  - structured development workflow
  - design-first development
  - start new feature
  - implement a spec
  - build from requirements
  - obra superpowers
platforms: [linux, macos, windows]
---

# Superpowers Methodology

> **Upstream:** https://github.com/obra/superpowers — MIT License

A complete software development methodology for coding agents. The pipeline transforms rough ideas into shipped features through a structured, composable skill workflow.

## The Pipeline

```
IDEA → BRAINSTORM → DESIGN DOC → PLAN → IMPLEMENT → REVIEW → FINISH
```

Each phase is enforced by a dedicated skill. The agent CANNOT skip phases — the methodology gate blocks any attempt to jump ahead.

## Phase 1: Brainstorming

**Skill:** `brainstorming` (from Superpowers)

Before writing ANY code, the agent MUST:
- Explore project context (files, docs, commits)
- Ask clarifying questions one at a time
- Propose 2-3 approaches with trade-offs
- Present design sections for incremental approval
- Write a spec doc to `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`
- Run spec self-review (no placeholders, contradictions, ambiguity)
- Get user approval on the written spec

**Gate:** HARD — no implementation skill, no code, no scaffolding until design is approved.

## Phase 2: Implementation Plan

**Skill:** `writing-plans` (from Superpowers / Hermes)

With approved design, the agent:
- Breaks work into bite-sized tasks (2-5 minutes each)
- Every task has exact file paths, complete code, verification steps
- Emphasizes true red/green TDD, YAGNI, DRY

## Phase 3: Execution

**Two paths depending on scope:**

### Subagent-Driven (complex, multi-step)
**Skill:** `subagent-driven-development`

Dispatches fresh subagent per task with two-stage review:
1. **Spec compliance** — does it match the design?
2. **Code quality** — is it clean, tested, maintainable?

### Batch Execution (simpler, fewer tasks)
**Skill:** `executing-plans`

Execute tasks in batches with human checkpoints between batches.

## Phase 4: Test-Driven Development

**Skill:** `test-driven-development` (RED-GREEN-REFACTOR)

Cross-cutting — applies to every task in every phase:
1. **RED** — Write a failing test first
2. **GREEN** — Write minimal code to make it pass
3. **REFACTOR** — Clean up while keeping tests green

**Exception:** Throwaway prototypes, generated code, config files (ask human partner first).

## Phase 5: Code Review

**Skills:** `requesting-code-review` → `receiving-code-review`

After each task, the agent reviews against the plan:
- Reports issues by severity (critical blocks progress)
- Addresses feedback structurally (not defensively)

## Phase 6: Finishing

**Skill:** `finishing-a-development-branch`

When all tasks are complete:
- Verify all tests pass
- Present options: merge / PR / keep worktree / discard
- Clean up worktree and sync

## Infrastructure

### Git Worktrees
**Skill:** `using-git-worktrees`

After design approval (Phase 1 done), create an isolated workspace:
```
git worktree add ../project-feature feature-branch
```
Keeps the main branch clean. Verifies clean test baseline before starting.

### Verification Before Completion
**Skill:** `verification-before-completion`

Before claiming any task is done:
- Does the code actually run?
- Do tests pass?
- Does the behavior match the spec?

## Debugging

**Skill:** `systematic-debugging` (4-phase: Root Cause → Pattern → Hypothesis → Fix)

For bugs and test failures. The Iron Law:
```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

## Cross-Cutting Guardrails

### Karpathy Guidelines (`karpathy-guidelines`)
- **Think Before Coding** — surface assumptions, don't hide confusion
- **Simplicity First** — no overengineering, no speculative features
- **Surgical Changes** — touch only what the task requires
- **Goal-Driven Execution** — define success criteria, loop until verified

### Dispatching Parallel Agents
**Skill:** `dispatching-parallel-agents`

For independent workstreams within a phase — multiple subagents working concurrently on independent tasks.

## When to Use

Use the full pipeline for:
- New features
- Bug fixes with design implications
- Refactoring that changes behavior
- Anything that would benefit from a written spec

**Use judgment for:**
- Trivial typo fixes (skip to Phase 5/6)
- Configuration-only changes
- Throwaway prototypes

## Post-Build Review (Multi-Perspective Protocol)

After any milestone ships, run a 5-persona critique: everyday user, power user, business owner, staff, accountant. Produces prioritized fix list. See `references/multi-perspective-review.md` for the full protocol.

Proven: CashFlow OS v1 review caught 10 issues (missing audit trail, currency hardcoded, quick-add bloated). All fixable within session.

## References

- **Superpowers repo:** https://github.com/obra/superpowers — original source of this methodology
- **Superpowers skills (external_dirs):** `C:/Users/YOUR_USERNAME/Documents/Repos/external-skills/superpowers/skills/`
- **Release announcement:** https://blog.fsck.com/2025/10/09/superpowers/
- **Superpowers evals:** https://github.com/prime-radiant-inc/superpowers-evals/
