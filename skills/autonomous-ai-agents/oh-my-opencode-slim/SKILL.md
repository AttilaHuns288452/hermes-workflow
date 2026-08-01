---
name: oh-my-opencode-slim
description: "Pantheon agent swarm for OpenCode — multi-agent coding orchestration with 7 specialized agents (Orchestrator, Oracle, Explorer, Librarian, Designer, Fixer, Council, Observer)."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [OpenCode, Agent-Swarm, Multi-Agent, Orchestration, Coding]
    related_skills: [opencode, autonomous-ai-agents/opencode]
---

# oh-my-opencode-slim

Pantheon agent swarm plugin for OpenCode. Orchestrates multi-agent coding workflows with role-specialized agents.

## Agent Roles

| Agent | Model | Role |
|-------|-------|------|
| **Orchestrator** | **Hermes chat model** (currently `opencode-go/deepseek-v4-pro`) | Master delegator, plans work graph, dispatches specialists |
| **Oracle** | `opencode/deepseek-v4-flash-free` | Strategic advisor, code review, hard debugging |
| **Explorer** | `opencode/deepseek-v4-flash-free` | Codebase reconnaissance, file discovery |
| **Librarian** | `opencode/deepseek-v4-flash-free` | External knowledge retrieval, API docs research |
| **Designer** | `opencode/deepseek-v4-flash-free` | UI/UX implementation, visual polish |
| **Fixer** | `opencode/deepseek-v4-flash-free` | Fast implementation, scoped patches |
| **Observer** | `opencode/mimo-v2.5-free` | Vision tasks — screenshots, images, PDFs (multimodal) |
| **Council** | Config-driven | Multi-model consensus, parallel synthesis |

## When to Use

- 3+ subtasks / features / PRs need parallel work
- Complex multi-file refactors requiring orchestration
- Tasks needing code review + implementation + research simultaneously
- Vision tasks (screenshots, images, PDF analysis) → route to Observer agent

## When NOT to Use

- 1-2 simple edits → do directly or use plain `opencode run`
- Research-only tasks → use browser agents
- Single-file changes → too small for agent swarm overhead

## Invocation

```bash
# Bounded task — auto-delegates to Pantheon agents
opencode run 'implement multi-step feature X'

# Interactive swarm session
opencode  # TUI starts, Orchestrator auto-delegates

# Force specific model
opencode run '...' --model opencode/deepseek-v4-flash
```

## Prerequisites

- OpenCode installed (v1.16+)
- Plugin installed at `~/Documents/Projects/oh-my-opencode-slim/`
- Plugin configured in `~/.config/opencode/opencode.jsonc` under plugins
- Per-agent model overrides in `oh-my-opencode-slim.json` at plugin root (Orchestrator→GLM, agents→DeepSeek, Observer→MiMo)

## Model Configuration

All free-tier models for cost efficiency:
- Coding/reasoning: `opencode/deepseek-v4-flash-free` or `opencode-go/deepseek-v4-flash`
- Vision: `opencode/mimo-v2.5-free` or `opencode-go/mimo-v2.5`
- Orchestration: Hermes chat model (currently `opencode-go/deepseek-v4-pro`)
