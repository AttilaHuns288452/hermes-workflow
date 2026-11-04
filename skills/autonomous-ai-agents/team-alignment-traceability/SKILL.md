---
name: team-alignment-traceability
description: Use when aligning shared requirements across specialists.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [team, alignment, requirements, traceability, handoff]
    related_skills: [hermes-multiagent-team, team-agent-orchestration, intent-driven-development]
---

# Team Alignment and Traceability

Use this skill when a Hermes specialist task affects another role, a shared project requirement, or a
final deliverable. It keeps the PM brief authoritative and makes cross-functional dependencies explicit.

## When to Use

- A specialist receives a task that affects another department.
- A requirement, design, architecture, market claim, or deliverable changes.
- The PM is preparing a cross-functional Kanban graph or Group Chat discussion.
- Outputs from multiple profiles must become one coherent result.

## Procedure

1. Read `~/.hermes/team/CHARTER.md` and the project's authoritative `BRIEF.md`, `DECISIONS.md`, and `STATUS.md` if present.
2. Classify the request as independent, cross-functional, or major decision. Do not convene every role for an independent task.
3. For cross-functional work, name affected specialists, dependencies, one owner, deliverables, and acceptance criteria before execution. Use Kanban for durable work and Group Chat only for discussion that benefits from interaction.
4. Preserve the traceability chain: owner concept → PM brief → evidence/UX/business or research input → technical decision → implementation → QA evidence → final document.
5. Reject silent scope drift. If a recommendation contradicts the authoritative brief, state the conflict and route it to the PM.
6. After execution, verify the artifact and update `STATUS.md` / `DECISIONS.md` when the user has requested project documentation or the workflow requires it.

## Handoff Contract

Return objective, output, evidence/verification, acceptance status, open risks, next action/owner, and any
conflict with the authoritative project brief. Facts, assumptions, estimates, and opinions must remain
separate.

## Skill Gap Rule

Before proposing a new skill, search the live catalog and reference index. Add a skill only for a proven
recurring capability gap. For an external candidate, record source, version, license, dependencies,
security verdict, assigned profiles, and an actual invocation check. Never install a candidate merely
because it sounds relevant.

## Verification

A cross-functional handoff passes only when:

- one owner is named;
- affected specialists and dependencies are named;
- acceptance criteria are observable;
- the result is stored in the correct project artifact or Kanban card;
- the PM can compare it against the authoritative brief;
- open conflicts are surfaced rather than silently averaged away.
