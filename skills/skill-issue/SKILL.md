---
name: "skill-issue"
description: "Find out why a coding-agent skill won't fire \u2014 grade each SKILL.md A\u2013F on activation, simulate which skill a prompt triggers, and flag collisions where one silently shadows another."
---
# skill-issue — skill activation audit

## Overview

A coding agent decides which skill to run from each skill's always-on `name` +
`description`. A skill can be perfectly implemented and still never fire because
its description is too vague to match how people phrase requests, or because a
more specific sibling silently wins. `skill-issue` audits exactly that surface,
grading each skill A–F, simulating which skill fires for a given prompt, and
reporting collision clusters where one skill shadows another.

## When to Use This Skill

- Use when a skill you wrote never seems to trigger and you don't know why
- Use when the user says "why isn't my skill firing", "which skill fires for X", or "audit my skills"
- Use after writing or installing a new SKILL.md, to investigate likely activation issues
- Use in CI to fail a PR that adds a skill with empty/duplicate/colliding metadata

## How It Works

Run the upstream CLI on demand (no global install) — `npx -y @misha_misha/skill-issue` — pointed at this system's skill roots:

```bash
skill-issue ~/.hermes/skills                       # grade every skill A–F (+ collisions summary)
skill-issue ~/.the reviewer subagent/skills --why "deploy to prod" # which skill fires for this prompt, and why
skill-issue <dir> --collisions                     # clusters of skills that shadow each other
skill-issue <dir> --fix                            # append a "Use when …" clause to weak descriptions
skill-issue <dir> --json                           # machine-readable; exits non-zero on errors
```

Offline heuristic by default; add `--llm` to judge with a local coding-agent CLI.

## Examples

### Example 1: Audit installed skills

```bash
skill-issue ~/.hermes/skills
# F  deploy-helper  ✗ no description — can never fire
# C  shipit         ! no "use when …" trigger clause
# A  rollback-prod  heuristic: trigger wording present; actual activation unverified
```

### Example 2: Diagnose a collision

```bash
skill-issue ~/.hermes/skills --why "deploy the app to prod"
#  1. shipit       0.74  ← would fire
#  2. land-deploy  0.69  (margin 0.05 — ambiguous, likely collision)
```

## Limitations

- Offline scoring is heuristic and should be treated as a triage signal, not a final quality verdict.
- Collision reports highlight likely shadowing, but agent-specific routers can weight metadata differently.
- The `--fix` mode can improve weak trigger wording, but generated edits still need maintainer review before committing.

## Execution boundaries

A score or simulated trigger is not proof that a native host activates a skill. Record actual client/version observations separately. Use --fix only within authorized paths after inspecting a proposed diff; preserve original metadata. --llm may send content through the configured model provider and needs the corresponding data/cost scope.
