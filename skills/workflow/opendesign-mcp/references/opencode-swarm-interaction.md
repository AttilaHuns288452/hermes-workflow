# OpenDesign ↔ oh-my-opencode-slim swarm interaction

OpenDesign's opencode agent spawns the system `opencode` CLI, which loads the
oh-my-opencode-slim swarm plugin (registered in `opencode.jsonc` → `plugin`).
Consequences verified 2026-08-09:

## 1. The swarm reroutes models — the "mystery kimi" case

OD asks for model `deepseek-v4-flash`, but the swarm's **active preset**
(`~/.config/opencode/oh-my-opencode-slim.json` → `presets.<active>`) decides
per-role models. The `opencode-go` preset had:
- orchestrator = `opencode-go/glm-5.2`
- **designer = `opencode-go/kimi-k2.7-code`**
- observer = `opencode-go/mimo-v2.5` (vision)

A "Redesign dental customer portal" task → dispatcher routes to @designer →
kimi-k2.7-code billed on the opencode-go usage page, even though the run was
"model: deepseek-v4-flash". Session IDs in the usage page (`…2FiFHZMz`,
`…XrQBNUzw`) match child session ids in the swarm log — that's how you
attribute billing to a task:
`~/.local/share/opencode/log/oh-my-opencode-slim.<timestamp>.log` lines:
`agentType:"designer", label:"Redesign dental customer portal"` + child session id.

Diagnosis recipe: usage-page model + session-id → grep swarm log for that
session suffix → read `agentType` + `label` + parent session → map to the
project dir recorded in the plugin init line.

## 2. Preset selection: `OPENCODE_SLIM_PRESET`

```bash
OPENCODE_SLIM_PRESET=<name> opencode run -m <model> "task"
```
- `-m` overrides the orchestrator only; other roles keep preset models.
- The plugin reads the config at startup — safe to edit the JSON *before*
  launch and restore after the run finishes.

## 3. Flash-only preset (model whitelist pattern)

To guarantee "only deepseek-v4-flash + mimo-2.5" (no kimi/glm):

```python
cfg = json.load(open(p, encoding='utf-8'))          # oh-my-opencode-slim.json
og = cfg['presets']['opencode-go']
flash = {}
for role, spec in og.items():
    if isinstance(spec, dict) and 'model' in spec:
        s = dict(spec)
        s['model'] = 'opencode-go/mimo-v2.5' if role == 'observer' else 'opencode-go/deepseek-v4-flash'
        flash[role] = s
cfg['presets']['flash-only'] = flash
json.dump(cfg, open(p, 'w', encoding='utf-8'), indent=2)
```
Then `OPENCODE_SLIM_PRESET=flash-only opencode run -m opencode-go/deepseek-v4-flash "…"`.
Back up the file first; restore after the run.

## 4. Output behavior

- `opencode run` prints only `> orchestrator · <model>` — the agent reply is
  NOT echoed. Verify via files written (cwd = run directory) or the swarm log.
- Skill load count appears in `~/.local/share/opencode/log/2026-08-09T*.log`:
  `skill count=736 init`.
- `opencode.jsonc` → `skills.paths` may point live at the Hermes skills dir
  (~221 entries, 736 SKILL.md found) — keep entries as live paths; no copying.

## 5. Related quirk

Swarm log init line records the working directory — that's how you know a
swarm run was spawned by OpenDesign (dir = `Open Design\...\data\projects\<id>`).
