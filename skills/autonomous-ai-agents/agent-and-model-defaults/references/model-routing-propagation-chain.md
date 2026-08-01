# Model Routing Propagation Chain

When the user changes model routing preferences, update ALL of these. Missing any
creates a stale reference that silently contradicts the active config.

## Touchpoints (in priority order)

| # | What | Path | Notes |
|---|------|------|-------|
| 1 | **Memory** | agentmemory `memory` store | The authoritative routing fact injected into every turn. Update with `memory(action='replace', ...)` |
| 2 | **`~/AGENTS.md`** | `C:\Users\Attila\AGENTS.md` | OpenCode reads this. Keep in sync with memory. |
| 3 | **`decide/SKILL.md`** | `skills/decide/SKILL.md` | Section `## 🤖 Model Roles & Delegation` — the quick-reference table + delegation rule paragraph. Also check the routing table entry for Pantheon swarm. |
| 4 | **`agent-and-model-defaults/SKILL.md`** | `skills/autonomous-ai-agents/agent-and-model-defaults/SKILL.md` | The canonical "Full Model Role Split" table, delegation config warning, Pantheon swarm config JSON, and AGENTS.md template block. |
| 5 | **`subagent-delegation/SKILL.md`** | `skills/subagent-delegation/SKILL.md` | Model Roles table, forbidden-actions section, rate-limit fallback section. |
| 6 | **`oh-my-opencode-slim/SKILL.md`** | `skills/autonomous-ai-agents/oh-my-opencode-slim/SKILL.md` | Agent Roles table, Model Configuration section. Also check `references/pantheon-config.md` if it exists. |

## Merge, don't replace

User directive: "configure it so that it doesnt reduce their task of my current
configuraiton only merged them with my current instructions." When updating, add
new roles/models without removing unrelated configuration (delegation settings,
provider preferences, free/paid fallback tiers).

## Verification

After updating, grep the skills directory for any remaining references to the
old model name. Stale references in error messages, examples, or inline comments
count:

```bash
grep -r "old-model-name" ~/AppData/Local/hermes/skills/ --include="*.md" -l
```
