---
name: model-recommender-workflow
description: >-
  Use the Model Recommender CLI to select free models for any task type. Integrates
  free-ai-tools provider data, ECC domain skills, and free-ai-model-router priority
  chains. Trigger on: model selection, task routing, free model queries.
triggers:
  - model selection
  - free model
  - model recommender
  - best model for
  - task routing
---

# Model Recommender Workflow

Use when the user asks "which free model should I use for X" or when you need
to select the best free model for a coding, reasoning, creative, fast, agentic,
or security task.

## Quick Start

```bash
# All task types (pretty-print)
python ~/Documents/Projects/free-ai-tools/scripts/model-recommender.py

# Single task with ECC skills
python ~/Documents/Projects/free-ai-tools/scripts/model-recommender.py coding --ecc

# Machine-readable JSON
python ~/Documents/Projects/free-ai-tools/scripts/model-recommender.py --json

# Explore data sources
python ~/Documents/Projects/free-ai-tools/scripts/model-recommender.py --list-models
python ~/Documents/Projects/free-ai-tools/scripts/model-recommender.py --list-providers

# Probe live model availability
python ~/Documents/Projects/free-ai-tools/scripts/model-recommender.py coding --probe
```

## Task Type → Model Mapping

| Task Type | Primary Model | Fallbacks | ECC Skills to Load | Freebuff Option |
|-----------|--------------|-----------|-------------------|-----------------|
| coding | opencode/deepseek-v4-flash-free | mimo-v2.5 → nemotron-3 → gpt-oss-120b → nex-n2-pro | backend-patterns, python-patterns, api-design, tdd-workflow | `freebuff` → DeepSeek V4 Pro or Kimi K2.6 |
| fast | opencode/north-mini-code-free | big-pickle | frontend-patterns, react-patterns, vite-patterns | `freebuff` → DeepSeek V4 Flash |
| reasoning | opencode/nemotron-3-ultra-free | mimo-v2.5 → nex-n2-pro | agent-architecture-audit, blueprint, security-review | `freebuff` → DeepSeek V4 Pro |
| creative | opencode/mimo-v2.5-free | nemotron-3 → big-pickle | brand-voice, article-writing, frontend-design-direction | `freebuff` → MiMo 2.5 Pro or MiniMax M3 |
| agentic | opencode/mimo-v2.5-free | deepseek-v4 → nemotron-3 | agentic-engineering, autonomous-agent-harness, autonomous-loops | `freebuff` → Multi-agent workflow (9 sub-agents) |
| security | opencode/nemotron-3-ultra-free | deepseek-v4 → nex-n2-pro | security-review, django-security, security-scan, and 6 more | — |

## Three-Layer Pipeline

```
📊 Model Data (free-ai-tools)     → 45 providers, 550+ tools, free-coding-models CLI
🎯 Domain Skills (ECC)            → 261 skills, 64 agents, per-task skill loadouts
🔍 Code Graph (Graphify)          → AST code symbols, imports, calls, communities
🧠 Model Routing (free-ai-model-router) → Priority chains, verified fallbacks, live probing
├─ Hermes decide skill            → Routes to correct task type
├─ FreeLLMAPI (local)             → 110+ models, 16 providers at localhost:3001/v1
└─ Obsidian                       → Documentation + Knowledge Graph
```

**Graphify as brain input:** The code graph (built by `graphify-integrate` on every project) provides structural context that feeds model selection — e.g., if the project has existing agent patterns, prefer agentic models; if it's pure C# console, prefer DeepSeek V4 Flash; if it has complex async, prefer Nemotron 3 Ultra.

## Data Sources

- **free-ai-tools README**: `~/Documents/Projects/free-ai-tools/README.md` (81KB, 1914 lines, 45 providers)
- **ECC skills dir**: `~/Documents/Projects/ECC/skills/` (261 .md files)
- **free-coding-models CLI**: Installed globally, `--opencode --json` for real-time checks
- **Model Registry**: 7 confirmed working free models (5 OpenCode bundled + 2 OpenRouter)

## Related Files

- `~/Documents/Projects/free-ai-tools/scripts/model-recommender.py` — The CLI tool (source of truth)
- `workflow/free-ai-model-router` — Hermes skill with priority chains and probing methodology
- `references/full-ecosystem-test.md` — End-to-end verification recipe for the entire free model ecosystem (model selection → code generation → build/run → complementary tool → Obsidian → KG refresh)
- `references/live-ecosystem-test-2026-06-11.md` — **Live test results** from June 11, 2026: complete ecosystem test with OpenCode, Freebuff, Graphify, FreeLLMAPI, Obsidian all validated end-to-end
- Obsidian: `Projects/github-repos/Model Recommender CLI.md`

## Full Ecosystem Verification

After adding a new tool or model source to the ecosystem, run the full test recipe
in `references/full-ecosystem-test.md`. This validates:

1. **Model selection** — recommender picks the correct model for the task type
2. **Direct probe** — model responds via `opencode run`
3. **Code generation** — model creates a real, buildable project (C#, Node, Python)
4. **Build & run** — project compiles with 0 errors and produces correct output
5. **Complementary tool test** — Freebuff (or other coding agent) adds a feature
6. **Skill updates** — all 4 ecosystem skills patched with new tool info
7. **Obsidian documentation** — ATM-quality notes + cross-links + wikilinks
8. **Knowledge graph refresh** — `render_kg.py` regenerates the vault graph

### Fallback chain test order (after ecosystem grows):

```
OpenCode → Freebuff → FreeLLMAPI → OpenRouter :free → Paid safety net
```

Each layer should be tested independently before claiming the chain is healthy.

## Pitfalls

- Free-ai-tools README parsers use regex and may miss some provider metadata
- OpenRouter :free models change frequently — always probe before committing
- Model probe via subprocess requires opencode CLI in PATH
