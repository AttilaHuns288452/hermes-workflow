# ECC + Free AI Tools Conflict Resolution

Worked example from 2026-06-11 session. Two repos were competing with Hermes:

| Repo | Source | Purpose | Conflict Risk |
|------|--------|---------|---------------|
| **ECC** | `affaan-m/ECC` | 261 skills, 64 agents, 84 commands | Orchestrator identity, paid model defaults, agent routing rules |
| **Free AI Tools** | `ShaikhWarsi/free-ai-tools` | 550+ free AI tool catalog, Next.js website + CLI | None (data reference only) |

## Conflict Vectors Found

### Vector 1: Model Defaults (ECC agent.yaml)

**Before:**
```yaml
model:
  preferred: claude-opus-4-6
  fallback:
    - claude-sonnet-4-6
```

**After:**
```yaml
model:
  # ECC is a resource/skill library for Hermes — model routing is owned by
  # Hermes' decide skill, not ECC. These are fallback defaults only.
  preferred: opencode/deepseek-v4-flash-free
  fallback:
    - opencode/minimax-m2.5-free
    - opencode/nemotron-3-ultra-free
```

### Vector 2: Orchestration Role (ECC AGENTS.md)

Added Role Clarification block at the top:
```markdown
> **Role Clarification:** ECC is a **skill/resource library** for AI coding
> agents (Hermes, Claude Code, OpenCode, etc.) — it provides 64 agents, 261
> skills, rules, and patterns that any orchestrator can draw upon. It is NOT
> a competing orchestrator.
> **Hermes' `decide` skill** is the master orchestrator that routes tasks to
> the appropriate ECC resources when needed.
```

### Vector 3: Orchestration Identity (ECCLAUDE.md)

Added role boundary:
```markdown
> **Role:** This repository (ECC) is a skill/resource library for AI coding
> agents. See the **Role Clarification** in AGENTS.md — ECC supplies tools;
> Hermes' `decide` skill orchestrates.
```

### Vector 4: MCP Config Overlap (None Found)

ECC's `mcp-configs/mcp-servers.json` has 30+ server definitions, but all use `YOUR_*_HERE` placeholders — reference only. ECC's active `.mcp.json` only registers `chrome-devtools`, which doesn't overlap with Hermes' MCP servers in `~/.hermes/config.yaml`.

**Lesson:** Check whether ecosystem MCP files auto-register (`.mcp.json`, `claude_desktop_config.json`) or are reference-only (`mcp-configs/*.json` with placeholders).

### Vector 5: Port Conflicts (None Found)

- Port 3000: confirmed free (no listener)
- ECC website: not running
- Free AI Tools website: builds on 3000, no conflict

### Vector 6: Skill Overlap (Informational)

- ECC: 261 skills across 30+ domains
- Hermes: 47 skills
- Overlap exists in coding-standards, security, and testing domains, but ECC skills are deeper/more specific. Hermes decide skill routes to ECC skills when it needs specialized depth.

## What Free AI Tools Needed (Nothing)

- `free-coding-models` CLI: already installed globally, works correctly
- Next.js website: built successfully (13 pages, 9.8s)
- No model default conflicts (it's a reference catalog, not an orchestrator)
- No MCP configs
- No port conflicts

## Tool Verification Commands Used

```bash
# Check git status on both repos
git -C ~/Documents/Projects/ECC status --short
git -C ~/Documents/Projects/free-ai-tools status --short

# Read model defaults
grep -A5 '^model:' ~/Documents/Projects/ECC/agent.yaml

# Check if ecosystem MCP is active vs reference
ls ~/Documents/Projects/ECC/mcp-configs/
cat ~/Documents/Projects/ECC/.mcp.json

# Check Hermes config for conflicts
grep -i 'ecc\|free-ai' ~/AppData/Local/hermes/config.yaml

# Check port usage
netstat -ano | grep ':3000' | grep LISTEN

# Build website
cd ~/Documents/Projects/free-ai-tools/website && npx next build

# Check CLI is installed globally
which free-coding-models

# Final verification
grep -A3 'preferred:' ~/Documents/Projects/ECC/agent.yaml
head -5 ~/Documents/Projects/ECC/AGENTS.md
head -5 ~/Documents/Projects/ECC/CLAUDE.md
```

## Obsidian Documentation (Post-Fix)

Three notes created under `~/Documents/Obsidian Vault/Projects/github-repos/`:
- `ECC & Free AI Tools.md` — main coordination note with architecture/Mermaid graph
- `ECC Resource Library.md` — detailed ECC docs (agents, skills, configs, fixes)
- `Free AI Tools Model Reference.md` — website routes, CLI usage, model data

Knowledge graph regenerated: 115 nodes, 243 edges.
