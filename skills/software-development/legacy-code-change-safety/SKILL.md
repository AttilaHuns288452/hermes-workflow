---
name: legacy-code-change-safety
description: Use when changing poorly tested or hard-to-change code.
version: 0.1.0
author: Hermes Agent, adapted from Michael Feathers guidance
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [legacy-code, characterization-testing, seams, safe-refactoring]
    upstream_repository: "https://github.com/ciembor/agent-rules-books"
    upstream_commit: "893a88a6fce3a80c565bf39ac65021b43a8b2990"
    source_package: "working-effectively-with-legacy-code"
---

# Safe Changes in Legacy Code

## When to Use

Use this focused workflow when behavior is unclear, tests are weak, dependencies are hidden, or runtime setup blocks feedback. Treat untested code as risky legacy code.

## Workflow

1. State the requested behavior change and the current behavior that must remain.
2. Trace the change point outward through callers, values, effects, collaborators, and outputs.
3. Add a narrow characterization test or another explicit observation path before changing uncertain behavior.
4. Find the first dependency blocking feedback: time, randomness, globals, files, network, database, framework setup, or hidden construction.
5. Create the smallest useful seam for observation or substitution.
6. Make the requested change with behavior and structural edits separated where practical.
7. Run focused tests, then related regression tests.
8. Refactor locally only after behavior is protected. Leave the area easier to test or change.

## Preferred moves

- Add a sprout method or class when new behavior can avoid fragile edits.
- Wrap a hard method or class when mediation improves observation.
- Inject clocks, randomness, configuration, and external collaborators only when they block repeatable tests.
- Split construction from use and isolate policy from persistence, UI, framework, and I/O mechanisms.
- Use broader interception or integration tests first when narrow tests are not yet possible, then tighten the seam.

## Reject

Do not rewrite first, clean the whole module, expand hidden dependencies, mock around untestable structure without improving it, or check in exploratory restructuring used only to understand the code.

## Final check

- Was uncertain current behavior characterized?
- Is the seam the smallest one that unlocks the change?
- Was at least one blocking dependency reduced?
- Are behavior, refactoring, and cleanup distinguishable?
- Is the changed area more understandable, testable, or changeable?

## Provenance

Adapted from `working-effectively-with-legacy-code` in [agent-rules-books](https://github.com/ciembor/agent-rules-books), commit `893a88a6fce3a80c565bf39ac65021b43a8b2990`. The upstream repository is MIT licensed. This is a Hermes adaptation, not a bulk import; the full source remains in the pinned mirror for reference.
