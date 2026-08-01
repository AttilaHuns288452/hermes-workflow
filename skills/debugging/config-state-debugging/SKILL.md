---
name: config-state-debugging
description: "Debug state flow through config-file-driven applications where runtime changes don't persist across reads. Covers flag-gated persistence, read/write asymmetry, and transient-state-revert patterns."
---

# Config-Driven State Persistence Debugging

## When to Use

Use when a user-facing change (model switch, settings toggle, config update) works momentarily but reverts after a polling interval, page refresh, or new session. The user reports "it works for a few seconds, then snaps back."

## Core Symptom

The in-memory runtime updated correctly, but the config/database layer was never written to. On the next read cycle the reader sees the old persistent value.

## Diagnostic Protocol

### 1. Isolate the Persistence Layer

Test the write and read paths independently:

```python
# Read what's currently in config
cfg = load_config()
print(cfg.get("model", {}).get("default", "NOT SET"))

# Simulate the write
save_config_value("model.default", "picked-model")
save_config_value("model.provider", "picked-provider")

# Re-read to verify write stuck
cfg2 = load_config()
print(cfg2.get("model", {}).get("default", "NOT SET"))
```

If the value didn't change: the persistence function is broken or never called.
If the value persisted: the write path is fine, but the UI is calling a different function.

### 2. Trace What the UI Actually Sends

Find the exact value the UI passes to the server:

```bash
# Search minified JS for the function name
grep -oP 'selectModel[^;]+' dist/assets/index-*.js

# Look for the value template in the RPC call
# e.g., value: `${r.model} --provider ${r.provider} --session`
```

Reproduce locally with the exact same format:

```python
from model_switch import parse_model_flags, resolve_persist_behavior
value = "picked-model --provider picked-provider --session"  # exact UI format
model_input, provider, is_global, force_refresh, is_session = parse_model_flags(value)
persist = resolve_persist_behavior(is_global, is_session)
print(f"persist_global={persist}")  # if False → flag-gated persistence bug
```

### 3. Trace the Full Code Path

```bash
# Where is config READ?
grep -rn "get_config\|model.default\|load_config" src/

# Where is config WRITTEN?
grep -rn "save_config\|persist\|write_config" src/

# Where is the UI's RPC handler?
grep -rn "config.set\|model.set" src/server/
```

## Root Cause Categories

| # | Pattern | Detection | Fix |
|---|---------|-----------|-----|
| 1 | **Flag-gated persistence** — UI sends `--session`/`--no-save` flag that prevents writing | `parse_model_flags(value)` shows `is_session=True` | Strip the flag at the handler |
| 2 | **Persistence bypass** — In-memory update happens in function A, but persistence call is in function B, and function B is never called | Trace the full call chain from UI → handler | Move persistence into function A |
| 3 | **Read/write asymmetry** — Read path and write path use different sources | Check: write→`config.yaml`, read→`env var` or vice versa | Unify the read/write source |
| 4 | **Mid-write crash** — Exception in persistence is silently caught | Add a try/except with logging around the save call | Fix the exception or propagate it |
| 5 | **Config file conflict** — Two processes modify the same config, one overwrites the other | Check for parallel process instances modifying config | Lock the config file or use atomic writes |
| 6 | **Stale deployment** — Source patched but `.pyc` compiled before the patch; Python loads old bytecode | `stat server.py` mtime vs `stat server.cpython-*.pyc` mtime. If `.pyc` is newer, runtime ignores source changes | Find + delete stale `.pyc` files, kill processes, verify they restart with fresh bytecode |
| 7 | **Re-emission rollback** — Persistence works, but a second event (from another code path) overwrites the value back after the first change | Grep for all _emit("session.info") call sites — any one can revert the model on the UI | Add trace logging to every emit site, identify which fires the rollback, then guard that path |
| 8 | **yaml.dump line-width truncation** — yaml.dump defaults to 80-char line width; strings >80 chars are wrapped and ... inserted at the break. Since ... is YAML's document-end marker, subsequent reads silently truncate to the prefix. | Check raw YAML for ... mid-value; print(repr(read_value)) reveals truncation at exactly 80-char boundary | Always set width=999 in yaml.dump() calls that write config: yaml.dump(data, f, width=999) |

## Fix Patterns

**Priority order (least changes to most):**

1. **Strip the flag at the handler** — Modify the RPC handler to remove `--session` before parsing. One-line change, no UI changes needed, server stays compatible with both CLI (which legitimately uses `--session`) and desktop.

2. **Make the reader session-aware** — Modify the read path to check for in-memory overrides before falling back to config. Larger change but more correct (respects per-session overrides).

3. **Make the writer always persist** — Remove the flag from the UI side. Requires UI rebuild. Simplest long-term but most effort to ship.

## Concrete Example

See `references/hermes-model-switch-revert.md` for a full reproduction of the Hermes desktop model switch bug: the JS→Python→config flow, the minified JS template extraction, the `parse_model_flags` trace, and the one-line handler fix.
