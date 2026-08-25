# Skill collision + commandcode Muse Spark — 2026-08-20

## Skill collision: `skill_view('decide')` → Ambiguous

**Symptom**
```
skill_view(name='decide') → {success:false, error:"Ambiguous skill name 'decide': 2 skills match..."}
matches: [".../hermes/skills/decide/SKILL.md", ".../.agents/skills/decide/SKILL.md"]
```

**Root** — `config.yaml: skills.external_dirs` includes `C:/Users/Attila/.agents/skills`. Loader at `hermes-agent/tools/skills_tool.py:1183` scans ALL dirs via direct-path + recursive `SKILL.md` + frontmatter `name:` match. `len>1` → refuse.

**Fix (verified)**
```bash
mv "C:/Users/Attila/.agents/skills/decide" "C:/Users/Attila/.agents/decide.bak-20260820"
# .bak inside .agents/skills still matches via rglob+frontmatter — must leave indexed dir
skill_view(name='decide') → success:true
```
Backup: `C:/Users/Attila/.agents/decide.bak-20260820`. Herm vs .agents diff: only provider strings (`opencode-go/*` vs `commandcode/*`).

**Scope** — `comm -12 <(ls hermes/skills) <(ls .agents/skills)` → 211 dupes (e.g. `ecc-bridge`, `silent-failure-audit`). Fix on demand.

## commandcode / Muse Spark

### 1. `reasoning_effort: ultra` → 400

Gateway `commandcode → meta` only accepts `low|medium|high|xhigh|max`. Hermes allows `ultra` (=max) in `hermes_constants.VALID_REASONING_EFFORTS`.

- Before: `config.yaml` had `agent.reasoning_effort: ultra`, `delegation: max`, plus stray top-level `reasoning_effort: none` at EOF (outside `agent:` — ignored by `resolve_reasoning_config` but confusing).
- Fixes:
  - `hermes config set agent.reasoning_effort max` → `agent:max`, removed stray EOF key.
  - `agent/transports/chat_completions.py:21 _reasoning_config_for_model`: was `ultra→max` only for `gpt-5.6`; patched to clamp for any model.

### 2. `input[56] missing required field arguments`

One hit in `logs/agent.log` on `bg-review` (56 inputs, long replay). Meta requires `arguments` string on every `tool_calls[].function`. Already handled by `agent/agent_runtime_helpers.py:286 sanitize_tool_call_arguments` ("" / None / non-string → "{}" + JSON repair + stub tool result). The hit bypassed sanitize on that thread — not a model bug, isolated.

**When debugging**: `input[N]` = index in sanitized message list; check sanitize cursor logic.

## Verification

```bash
skill_view(name='decide')
hermes -z "terminal echo hello"  # single toolcall
hermes -z "read_file + terminal + search_files (3 parallel)"
grep -n reasoning_effort C:/Users/Attila/AppData/Local/hermes/config.yaml  # agent:max, delegation:max
```
