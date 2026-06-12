---
name: decide
description: "Master orchestrator — 5-step reasoning protocol for every request. Decompose prompt, score confidence, select skills, resolve conflicts, execute pipeline. Enforces execution order across all downstream skills."
version: 1.0.0
author: Hermes Workflow
license: CC BY-NC 4.0
triggers:
  - always
---

# /decide — Routing Brain

## Role

The routing brain for every session. Parses every incoming prompt, maps it to the correct skill set, resolves conflicts, injects context, and hands off with a structured execution plan. Does not execute the task itself — it owns the decision of what runs, in what order, and with what inputs.

## 5-Step Reasoning Protocol

Every request goes through this protocol before any tool is called. No shortcuts.

### Step 1 — Decompose the Prompt

Break the request into its actual components. A single prompt can contain multiple distinct tasks, hidden dependencies, or implicit deliverables. Name them explicitly before routing anything.

Check for:
- Setup + documentation (requires two skills)
- Research + code + obsidian (three-phase task)
- Review + fix + verify (feedback loop)

### Step 2 — Challenge the Obvious Interpretation

Ask: is the surface reading of this prompt actually what's being asked?

Check for:
- Implicit context that changes the domain
- User shortcuts or shorthand
- Prior session patterns that reframe the request
- Domain-specific terminology (e.g. "fix this" on a finance formula is a domain task, not a coding task)

### Step 3 — Score Routing Confidence

For each candidate skill, assign a confidence level:
- **High** — intent is unambiguous, skill maps cleanly
- **Medium** — plausible match but at least one alternative exists
- **Low** — best guess; flag assumption in output

If any selected skill scores Low, state the assumption explicitly. If the entire routing is Low confidence, ask one clarifying question before proceeding.

### Step 4 — Second-Order Thinking

Ask: what will this task likely produce or require next? If the current request is step 1 of a multi-step workflow, pre-load the skills that step 2 will need.

Examples:
- A new feature implementation → needs code review + Obsidian doc
- A setup task → needs complementary integration check + KG refresh
- A one-shot query → probably just needs answer, no post-execution

### Step 5 — Self-Challenge

Before finalizing the routing decision, ask: is there a simpler path? Could one skill handle this instead of three? Avoid over-routing. The right answer is the minimum viable skill set that fully satisfies the task.

## Execution Order (Mandatory)

Every request executes in this exact order. Never skip a step.

```
session_memory → guardrail → /decide → token-saver → domain skills → model routing → obsidian docs → KG refresh
```

1. **session_memory** — Pull prior context from past sessions. Never route blind.
2. **🛡️ Core Identity Guardrail** — Safety check before anything else. Never skipped.
3. **/decide** — Run the 5-step reasoning protocol above. Select skills, resolve conflicts.
4. **⚡ Token Saver** — Probe Graphify + CodeGraph before any `read_file()`. Target: 56× reduction.
5. **🎯 Domain Skills** — Execute the selected skills in order. ECC agents, LLMQuant, coding, creative, research, GitHub, media, etc.
6. **🤖 Model Routing** — Try OpenCode → Freebuff → FreeLLMAPI → OpenRouter → paid. Always default to free.
7. **📝 Obsidian Docs** — ATM-Machine quality: Overview, Architecture, Code Patterns, Mermaid graph, wikilinks.
8. **🕸️ KG Refresh** — Re-scan vault, regenerate galaxy graph.

## Skill Discovery

At the start of every session, before routing:

1. Scan the skills directory for all available `.md` skill files.
2. Read each file's frontmatter: `name`, `description`, `triggers`.
3. Build the routing table dynamically from what's found.
4. If a new skill is found with no existing routing rule, infer its trigger conditions from its `description` and `triggers` frontmatter.

## Routing Rules

| Trigger | Route To |
|---------|----------|
| Setup / install / configure | `setup` skill |
| Coding / implementation | Domain coding skill |
| Design / UI / visual | `creative` skills |
| Research / papers / monitoring | `research` skills |
| GitHub / PR / issues | `github` skills |
| Obsidian / docs / vault | `obsidian` skills |
| Model selection / model question | `model-router` skill |
| Knowledge graph / Graphify / CodeGraph | `graphify` / `codegraph` skills |
| ECC agent invocation | `ecc-bridge` skill |
| Finance / quant | `llmquant` domain skills |
| Documentation writing | `obsidian-docs` skill |

## Conflict Resolution

- Two domain skills overlap → activate both; primary domain governs.
- No skill matches → fall back to closest matching skill, proceed on own judgment, flag the gap in output.
- Ambiguous intent → do not ask for clarification unless Step 3 scores the entire routing as Low confidence.

## Self-Correction

If the routing produces a wrong or suboptimal result:

1. Record what went wrong: which skill was selected incorrectly?
2. Record what should have been selected: what was the correct routing?
3. Patch the routing rules to capture the correction.
4. Notify the user: briefly mention the correction was captured.

The system evolves. Every mistake improves future routing.

## Complementary Setup Routing

When a setup/install task is detected, also check for complementary integration:

- **Graphify (code knowledge graph)** → Route to BOTH `setup` AND `graphify-integrate` AND the Obsidian bundle. Graphify provides AST-level code understanding.
- **Agent framework** (ECC, devfleet) → Route to BOTH `setup` AND `external-agent-ecosystem-adapter`. Check for model default conflicts.
- **Model/provider resource** → Route to `setup`, then cross-reference with `model-router` for integration. Run model-recommender to test.
- **Tool/utility** → Set up normally, check for shared dependency conflicts. Add Obsidian wikilinks.
- **Coding agent** (Freebuff, Codebuff) → Route to `setup`, cross-reference with `model-router` for combined model selection.
