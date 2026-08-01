# Model Switch Revert Debugging

## Scenario
Desktop model picker lets you click another model, it switches for ~3 seconds, then reverts to `deepseek-v4-flash-free`.

---

## Round 1 (June 2026): Dead API Server Gateway

### Evidence Chain

### 1. Python `model.options` Works Fine
```python
from hermes_cli.inventory import build_models_payload, load_picker_context
ctx = load_picker_context()
payload = build_models_payload(ctx, picker_hints=True, canonical_order=True, capabilities=True)
# Returns 8 providers, 56 opencode-zen models
```

### 2. Desktop Uses BOTH Gateway Layers
- Chat/model switching goes through JSON-RPC on TUI gateway (port 57964)
- Model listing/info goes through REST on API server gateway (port 8642)

### 3. API Server Gateway Was Dead
- Routes registered: `grep 'api/model/options' api_server.py` → line 1325
- But: `grep 'def _handle_model_options' api_server.py` → NOT FOUND
- `_handle_model_info` and `_handle_model_set` also missing

### 4. Why: Broken Patch Script
`patch_gateway_models.py` had:
```python
if route_tuple not in src:
    src = src.replace(route_anchor, new_routes, 1)
if "_handle_model_options" not in src:
    src = src.replace(cap_anchor, handlers + cap_anchor, 1)
```
Routes added in step 2 contain `self._handle_model_options`, so step 3's idempotence guard was always satisfied — handler methods never inserted.

### Fix Applied (June)
1. Removed duplicate routes
2. Inserted handler methods before `_handle_capabilities` using a unique anchor

---

## Round 2 (July 21 2026): `--session` Flag Prevents Config Persistence

Despite API server fix, model switch still reverted. Real root cause was the TUI gateway's `config.set` handler.

### Root Cause 1: `--session` Flag

Desktop sends `config.set` with value format (from `use-model-controls.ts:99`):
```
modelname --provider providername --session
```

`--session` → `parse_model_flags` sets `is_session=True` → `resolve_persist_behavior` returns `False` → `_persist_model_switch()` never called → config.yaml NOT updated → next read picks old default.

**Fix in `tui_gateway/server.py` (config.set handler, ~line 10347):**
```python
fixed_value = value.replace("--session", "").strip()
parsed_flags = parse_model_flags(fixed_value)
```

Also, `_apply_model_switch` defaults `pin_session_override=True`, which sets `session["model_override"]` even after global persist. This session-level override shadows the global config on subsequent reads. Pass `pin_session_override=False` from the config.set handler.

### Root Cause 2: `resolve_persist_behavior` Always Returns False for `--session`

Nuclear option: replace function body in `hermes_cli/model_switch.py` with:
```python
def resolve_persist_behavior(is_global, is_session) -> bool:
    return True
```
Guarantees ANY model switch persists regardless of flags.

### Root Cause 3: Python `.pyc` Staleness

After patching source, running serve processes may still use old `.pyc` bytecode if pyc mtime > source mtime. Python considers pyc authoritative when newer.

**Diagnosis:**
```bash
stat --format="%Y" server.py
stat --format="%Y" __pycache__/server.cpython-311.pyc
```

**Fix:**
```bash
touch server.py
rm -f __pycache__/server.cpython-311.pyc
# Kill and restart serve processes so they recompile from patched source
```

### Desktop Client Model-Read Priority

`currentPickerSelection` in `model-status-label.ts`:
```typescript
(hasSession && options?.model) || store.model || options?.model
```
Priority: session model from `model.options` API → `$currentModel` atom → API fallback.

### model.options Endpoint
Returns `getattr(agent, "model", "")` — the session agent's current model, NOT the config default. After a successful switch, agent.model is updated so `model.options` returns the new model.

### session.info Application
Desktop only applies model from `session.info` when event targets the ACTIVE session (`apply = explicitSid ? isActiveEvent : !activeSessionIdRef.current` in `gateway-event.ts:148`).

### Verification
```bash
grep -n "fixed_value = value.replace" server.py  # --session fix present
grep -A2 "def resolve_persist_behavior" model_switch.py  # should return True
stat server.py  # mtime should be ~current time
# config.yaml mtime should update after desktop model switch attempt
```
