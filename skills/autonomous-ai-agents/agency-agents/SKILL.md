---
name: agency-agents
description: >-
  Use The Agency agent roster (agency-agents) — 254+ specialized AI specialists
  for engineering, design, marketing, finance, etc. Plugin exposes 4 tools.
  Load only what you need per task.
---

# The Agency — Lazy Agent Router

**Repo:** `https://github.com/msitarzewski/agency-agents`
**Plugin:** `agency-agents-router` (installed in Hermes plugins)
**Roster:** 254 specialists across 18 divisions.

## Tools provided by the plugin

| Tool | What it does |
|------|-------------|
| `agency_agents_search(query, division, limit)` | Find specialists matching query/division |
| `agency_agents_inspect(agent)` | Full details for one specialist |
| `agency_agents_load(agent)` | Compose that specialist's prompt |
| `agency_agents_delegate(agent, task)` | Delegate via Hermes `delegate_task` |

## How to use

1. **Search** first: `agency_agents_search(query="React component library", division="engineering")`
2. **Inspect** a promising specialist: `agency_agents_inspect(agent="frontend-developer")`
3. **Load or delegate**: `agency_agents_load(agent="frontend-developer")` or `agency_agents_delegate(agent="frontend-developer", task="Build button component")`

Never preload the full roster. Load/delegate only what the current phase needs.

## OpenCode

254 agent `.md` files are installed at:
- `~/.config/opencode/agents/` (global)
- `./.opencode/agents/` (per-project in the repo)

Use `opencode --agent <slug>` to invoke a specialist.

## Update

To regenerate integration files after pulling new agents:
```bash
cd ~/Documents/Projects/agency-agents
bash scripts/convert.sh --tool hermes
bash scripts/convert.sh --tool opencode
cp -r integrations/hermes/agency-agents-router ~/.hermes/plugins/
cp    integrations/opencode/agents/* ~/.config/opencode/agents/
```
