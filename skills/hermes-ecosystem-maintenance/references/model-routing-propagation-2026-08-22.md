# Model Routing Propagation Chain

When `config.yaml` model/provider assignments change (e.g. provider swap, model upgrade, delegation re-pin), the following files carry hardcoded model references that must be updated. Missing any creates a stale routing claim.

## Touchpoints (checked 2026-08-22)

### Hermes-side (live runtime)
| File | What to update |
|------|---------------|
| `SOUL.md` | Delegation hard-rule line — model name + provider + "config.yaml wins" |
| `skills/decide/SKILL.md` | Model Roles table, delegation rule paragraph, OpenCode run examples |
| `skills/subagent-delegation/SKILL.md` | Model Roles table, workflow examples, pitfalls config block |
| `skills/autonomous-ai-agents/agent-and-model-defaults/SKILL.md` | Role table, delegation YAML, Pantheon overrides, vision config |
| `skills/ecc-bridge/SKILL.md` | Top-level chain description, agent mapping header, example commands |

### Workflow repo mirror (`~/Documents/Projects/hermes-workflow/`)
| File | What to update |
|------|---------------|
| `README.md` | Model badge, free-model-chain stats line |
| `SETUP.md` | Recommended model callout |
| `META_PROMPT.md` | "Model used for this session" line |
| `INTEGRATION.md` | Provider routing table, skill routing diagram |
| `skills/decide/SKILL.md` | Same as Hermes-side |
| `skills/subagent-delegation/SKILL.md` | Same as Hermes-side |
| `skills/ecc-bridge/SKILL.md` | Same as Hermes-side |
| `skills/autonomous-ai-agents/agent-and-model-defaults/SKILL.md` | Same as Hermes-side |
| `skills/hermes-kanban-setup/SKILL.md` | Config example (`kanban_decomposer.model`) |

## Verification

```bash
# Hermes-side
grep -rn "old-model" ~/AppData/Local/hermes/SOUL.md ~/AppData/Local/hermes/skills/decide/SKILL.md ~/AppData/Local/hermes/skills/subagent-delegation/SKILL.md ~/AppData/Local/hermes/skills/autonomous-ai-agents/agent-and-model-defaults/SKILL.md

# Workflow-side
grep -rn "old-model" ~/Documents/Projects/hermes-workflow/README.md ~/Documents/Projects/hermes-workflow/skills/decide/SKILL.md ~/Documents/Projects/hermes-workflow/skills/subagent-delegation/SKILL.md ~/Documents/Projects/hermes-workflow/skills/ecc-bridge/SKILL.md
```

## Pitfalls
- Provider status changes without warning (opencode-go was "retired" then became live again). Always check `config.yaml` provider block directly.
- Historical agent mapping tables (ecc-bridge rows) are DOCUMENTATION, not routing. Add a disclaimer rather than rewriting every historical row.
- Trigger aliases in YAML frontmatter (`- deepseek`) and user-phrase examples (`"use deepseek for this"`) are NOT routing — leave them as-is.
- The `hermes-workflow` repo is a PUBLIC mirror. Patches there must be committed + pushed separately from Hermes-side skill edits.
