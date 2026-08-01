# Hermes Desktop Model Switch Revert Bug

## Symptom

User picks a different model from the desktop picker. It shows the new model for 2-5 seconds, then snaps back to `deepseek-v4-flash-free`.

## Root Cause (Original)

The desktop picker calls `config.set` with the `--session` flag:

```javascript
// value: `${r.model} --provider ${r.provider} --session`
```

This causes `parse_model_flags()` to set `is_session=True`, which makes `resolve_persist_behavior()` return `persist_global=False`. The `_persist_model_switch()` function is never called, so `config.yaml` is NOT updated.

When the desktop re-reads model state, it reads the default from unchanged config.yaml → the picker reverts.

## Root Cause (Deployment Blocker: Stale Bytecode)

Even after the source fix, if the serve process was running with stale `.pyc` compiled BEFORE the patch, the fix never executes. Python uses the cached bytecode mtime trust:

```
source mtime < .pyc mtime  →  Python trusts old bytecode  →  patch ignored
```

**Check:** `stat tui_gateway/server.py` vs `stat tui_gateway/__pycache__/server.cpython-311.pyc`

**Fix:** Delete `__pycache__/*.pyc` + `find ... -delete`, kill serve PIDs, verify new `.pyc` generated after restart.

## Root Cause (Unfixed: Re-emission Rollback)

After the persistence fix is deployed, the model can still revert if a SECOND `session.info` event fires with the old model. There are 15+ `_emit("session.info", ...)` call sites in `tui_gateway/server.py`. Any one of them can fire after the model switch and overwrite `$currentModel` back to the default.

**Evidence:** Config.yaml mtime unchanged even after model switch attempts, confirming `_persist_model_switch` is unreachable OR `save_config_value` silently fails.

## Code Path (Full)

```
Desktop JS → config.set({key:"model", value:"model --provider provider --session"})
  → tui_gateway/server.py @method("config.set")
    → parse_model_flags(value_without_--session)
      → model_input="model", explicit_provider="provider", is_session=False
    → resolve_persist_behavior(False, False) → True (with patch)
    → _apply_model_switch(...)
      → switch_model() ✓ (agent.model updated)
      → _emit("session.info", ...)  ✓ (new model broadcast)
      → session["model_override"] = {...}  ✓ (session override set)
      → _persist_model_switch(result)  ✓ NOW CALLED (writes config.yaml)
  → config.yaml UPDATED ✓
```

## Fixes Applied

1. `tui_gateway/server.py` — Strip `--session` before parsing flags:
   ```python
   fixed_value = value.replace("--session", "").strip()
   parsed_flags = parse_model_flags(fixed_value)
   ```

2. `hermes_cli/model_switch.py` — `resolve_persist_behavior` always returns True:
   ```python
   def resolve_persist_behavior(is_global, is_session):
       return True  # ponytail: always persist config
   ```

3. Stale `.pyc` cleared, serve PIDs restarted, fresh bytecode confirmed.

## Verification

```python
from cli import save_config_value
rc = save_config_value("model.default", "any-model-here")
print(f"WRITE OK: {rc}")  # must be True
# Check mtime changed:
import os, time
p = os.path.expanduser("~/AppData/Local/hermes/config.yaml")
print(f"mtime: {os.path.getmtime(p)}")
```

## Still Open

Even with all 3 fixes deployed, the model COULD still revert if any of the 15+ `_emit("session.info", ...)` call sites fires after the switch. To diagnose: add `log.info` to every emit site, restart, observe which handler fires the old model.
