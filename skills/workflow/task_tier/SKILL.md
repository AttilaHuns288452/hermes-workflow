---
name: task_tier
description: Classify every incoming request into Tier 1 (atomic), Tier 2 (task), or Tier 3 (project) to gate Obsidian/KG refresh and token-saver probe execution.
triggers:
  - task classification
  - tier
  - atomic
  - obsidian gate
  - project vs task
  - kg refresh gate
platforms: [windows, linux, macos]
---

# Task Tier — Request Classification Gate

## Purpose
Run before the Obsidian + KG refresh bundle in `/decide`. Classifies every incoming request into one of three tiers and produces a structured output that `/decide` uses to gate downstream steps — avoiding unnecessary Obsidian writes, KG refreshes, and token-saver probes on trivial requests.

## Tier Definitions

### TIER 1 — ATOMIC
**Criteria (ALL must be true):**
- Single-function edit, one-liner fix, or quick question
- No new files created
- No architecture or structural change
- Answer fits in <20 lines of output
- No new Obsidian nodes would be created

**Actions:**
- SKIP Obsidian bundle entirely
- SKIP KG refresh
- Skip Token Saver probe
- Answer directly, no pipeline steps

### TIER 2 — TASK
**Criteria (ANY can be true):**
- Multi-step but scoped (bug fix across 2–3 files)
- Adding a feature to an existing module
- Writing a script or small utility
- Modifies existing files but no new structural nodes

**Actions:**
- Run Token Saver probe (pre-file-read efficiency)
- SKIP Obsidian bundle
- SKIP KG refresh UNLESS files changed structurally (new classes, modules, or interfaces added to the project)
- After completion, check if structural additions occurred — if yes, add note update to the execution plan

### TIER 3 — PROJECT
**Criteria (ANY can be true):**
- New project, new architecture, new repo setup
- Multi-file scaffold or skeleton creation
- Integration wiring between systems
- Anything that creates new Obsidian nodes
- Anything that creates new skills, skills categories, or modifies skill orchestration
- Workflow changes that affect the Hermes ecosystem routing

**Actions:**
- Full pipeline: Token Saver → domain skill → Obsidian bundle (all three: obsidian + obsidian-codebase-graph + obsidian-knowledge-graph) → KG refresh
- Create or update the project's main Obsidian note with ATM-Machine quality
- Refresh KG after note updates

## What Counts as a Structural Change

A **structural change** is anything that would create, rename, or remove a node in the knowledge graph. It includes:

- **New files** that define new modules, classes, interfaces, types, API endpoints, database tables/schemas, controllers, services, or test suites
- **New relationships** (e.g., wiring two previously separate systems together, adding a dependency between existing modules)
- **New capabilities** that change the project's feature surface: new commands, new MCP tools, new CLI subcommands, new provider integrations
- **New project scaffolding** — directories, config files, package manifests, git initialization
- **Ecosystem changes** — new Hermes skills, new pipeline steps, new MCP servers, new provider configs, new cron jobs, new profile changes
- **Architecture changes** — refactoring that changes the dependency direction, splits a module, merges modules, or introduces a new architectural layer

It does NOT include:
- Bug fixes that only modify existing function bodies
- Documentation-only changes (text in existing notes, README edits)
- Counter/status/label changes in existing files
- Light refactors (renaming variables, extracting private methods within the same class)
- Dependency version bumps in isolation

When in doubt: if the change would appear as a distinct new entity in a Mermaid architecture diagram, it's structural.

## Edge Cases & Ambiguity Resolution

| Scenario | Classification | Rationale |
|----------|---------------|-----------|
| User asks a question about code but no changes | TIER 1 | No files created or modified. Quick answer. |
| User asks to fix a typo in one file | TIER 1 | Single-function, no structural change. |
| User asks to add a feature across 2 files | TIER 2 | Multi-step, scoped to existing module. Run Token Saver. |
| User asks to create a new component | TIER 2 | New file but scoped within existing structure. Run Token Saver. Skip KG unless the component is a new major architectural piece. |
| User asks to scaffold a new project | TIER 3 | New structural nodes, new Obsidian note needed. |
| User asks to wire two existing systems together | TIER 3 | Integration creates new structural relationships. |
| User asks to create or modify a skill | TIER 3 | Skill changes affect orchestration and need ecosystem documentation. |
| User asks a setup question for an existing tool | TIER 2 | Multi-step setup, may need Token Saver. Skip Obsidian unless new dirs/files are structurally significant. |
| User asks "what did we do about X" (session recall) | TIER 1 | Pure information retrieval, no changes. |
| User asks to create an Obsidian note | TIER 2 | File creation but scoped; only Obsidian skill needed, no KG refresh unless the note is structurally new. |
| Ambiguous — could be T1, T2, or T3 | Default to TIER 2 | Safer to run Token Saver and skip Obsidian than miss a structural gate. If in serious doubt, default to TIER 3 (full pipeline). |

## Mandatory Integration with /decide

`/decide` MUST call `task_tier` as step 2 of its pipeline, immediately after `session_memory` and `core-identity-guard`, and BEFORE the decompose/reasoning/skill-selection steps.

### Where task_tier sits in the pipeline

```
session_memory → core-identity-guard → task_tier → reasoning → skill selection → execution → post-execution (Obsidian + KG, if tier 3)
```

## Output Format

`task_tier` produces a structured classification that `/decide` uses to gate next steps. Output MUST follow this exact format:

```
TIER: [1|2|3]
REASON: [one-line explanation]
OBSIDIAN: [SKIP|SKIP|RUN]
KG_REFRESH: [SKIP|SKIP|RUN]
```

### Expected values by tier

| Field | TIER 1 | TIER 2 | TIER 3 |
|-------|--------|--------|--------|
| TIER | 1 | 2 | 3 |
| REASON | Single-function/quick answer | Multi-step scoped task | New project/architecture/ecosystem change |
| OBSIDIAN | SKIP | SKIP | RUN |
| KG_REFRESH | SKIP | SKIP (unless structural change) | RUN |

### How /decide consumes the output

- If OBSIDIAN is SKIP, the Obsidian bundle is NOT loaded — skip the three Obsidian skills entirely.
- If KG_REFRESH is SKIP, the knowledge-graph re-scan is NOT run (even if Obsidian was loaded for other reasons).
- If TIER is 1, all pipeline steps after answering are skipped — no Token Saver, no skills loading for file access, answer directly.
- If TIER is 2, Token Saver runs before any file operations, but Obsidian and KG are skipped (unless structural changes detected after the fact).
- If TIER is 3, the full pipeline runs: Token Saver → domain skill(s) → Obsidian bundle (obsidian + obsidian-codebase-graph + obsidian-knowledge-graph) → KG refresh.

## Self-Correction

If task_tier misclassifies a request:
1. Record what was classified incorrectly
2. Adjust the tier definitions or ambiguity table above
3. Notify the user of the correction captured

## Pitfalls

- **Don't over-classify quick questions as TIER 2.** A yes/no question or simple lookup is TIER 1. Token Saver isn't needed because there's no file read.
- **Don't under-classify ecosystem changes as TIER 2.** Creating or modifying a skill, wiring an integration, or setting up a new tool that affects routing IS TIER 3.
- **When in doubt, default up.** Ambiguous between 2 and 3? Go with 3. The full pipeline is better than missing an Obsidian update.
- **This skill runs BEFORE reasoning.** The classification is based on request surface characteristics (scope, files affected, structural change), not deep analysis. Deep analysis happens in the reasoning step after task_tier gates the pipeline.

## Tags
#workflow #classification #orchestration #tier #gate
