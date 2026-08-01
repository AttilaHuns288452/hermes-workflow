---
name: hermes-gateway-debugging
description: Debug Hermes Gateway route registration, model switching, WebSocket connections, and silent pythonw failures. Use when the desktop app can't switch models, MCP endpoints return 404, or the gateway won't bind its port.
version: 1.0.0
---

# Hermes Gateway Debugging

## When to Use

- Desktop model picker shows empty or reverts to default "after a few seconds"
- Gateway port won't bind (silent exit, pythonw)
- API endpoint returns 404 or 405
- MCP server tools connect but the daemon-side HTTP port is down
- A Hermes patch script applied but behavior didn't change

## Architecture Overview

Hermes has **two layers** the desktop talks to:

| Layer | Protocol | Port | Purpose |
|-------|----------|------|---------|
| TUI Gateway (serve) | JSON-RPC over WebSocket | 495XX (auto) | Chat, `config.set`, `session.*`, `model.options` (picker), agent lifecycle |
| API Server Gateway | REST over HTTP | 8642 | `/v1/models`, `/api/model/options`, `/api/model/set`, `/api/model/info` |

The desktop uses **one WebSocket + one REST connection** — NOT two separate WebSocket connections:

| Desktop Code Path | Protocol | Handler Source | Port |
|---|---|---|---|
| `requestGateway('method', ...)` → `HermesGateway` WebSocket | JSON-RPC over WS | `tui_gateway/server.py` | 495XX (serve) |
| `fetch('/api/...')` → rest polling | HTTP | `gateway/platforms/api_server.py` | 8642 |

**Key distinction:** `config.set`, `session.*`, `model.options` (picker), and all chat lifecycle RPCs go through the **WebSocket** → `tui_gateway/server.py`. The REST API server (8642) is only used for model listing/info **polling**. If the REST server is dead, the model status pill reverts to the config default after each `refetchInterval` — this was the Round 1 cause (June 2026).

The `config.set` handler in `tui_gateway/server.py` is where the `--session` flag must be stripped (see `references/model-switch-revert-june2026.md`).

## Common Bug Patterns

### -1. Stale State File: gateway_state.json Says "running" But Port Is Dead

**Symptom:** `gateway_state.json` shows `"gateway_state": "running"` with a PID, but `curl http://127.0.0.1:8642/` returns `000` (connection refused) and nothing listens on the port.

**Root cause:** The state file is written at start and not cleaned up on crash/kill — it lies after the process dies (desktop restart, orphan kill, OOM).

**Diagnosis — never trust the state file alone:**
```bash
cat ~/AppData/Local/hermes/gateway_state.json   # shows claimed PID + "running"
tasklist //FI "PID eq <pid>"                    # empty = process gone → stale
curl -s -m 3 -o /dev/null -w "%{http_code}" http://127.0.0.1:8642/   # 000 = dead
```

**Read the code right:**
- `404` on `http://127.0.0.1:8642/` is NORMAL for the API server (it's an API, no root route). `404` = gateway alive. `000` = dead.
- The **kanban dispatcher is embedded in the gateway** (log: `kanban dispatcher: embedded in gateway (interval=60s)`). Gateway down = no kanban dispatch, no cron delivery. Restarting the gateway is part of "kanban stopped working" triage.

**Restart + verify:**
```bash
hermes gateway run    # background: true, watch for "API server listening" / "kanban dispatcher: embedded"
```
Then confirm:
1. `curl -s -m 3 -o /dev/null -w "%{http_code}" http://127.0.0.1:8642/` → `404` (alive)
2. `tail ~/AppData/Local/hermes/logs/gateway.log` → lines `API server listening on http://127.0.0.1:8642`, `Gateway running with 1 platform(s)`, `kanban dispatcher: embedded in gateway`
3. Startup takes ~2-3 min on Windows — MCP server connect retries (`opendesign` etc.) log WARNINGs and park, but the gateway still comes up. Wait for the log lines, don't panic at the warnings.

### 0. Dashboard IPC Bridge Unavailable (CLI `hermes dashboard`)

**Symptom:** Opening `http://127.0.0.1:9119` in a browser shows "Hermes couldn't start — Desktop IPC bridge is unavailable."

**Root cause:** `hermes dashboard` serves the SPA on port 9119, but the SPA communicates with the gateway via Electron IPC (named pipes on Windows), not HTTP. The IPC bridge only works inside the Electron app context. Running the SPA in a browser has no IPC bridge to connect to.

**Why it happens:** The CLI `hermes dashboard` command is for development/embedding (e.g., embedding the SPA in another app). It is NOT a standalone browser dashboard. The gateway started via `hermes gateway run` uses IPC transport when `gateway.transport: auto` (the default), which only works within Electron.

**Fix:** Use the Hermes desktop app directly — it has the dashboard built in. The desktop app (Hermes.exe) manages both the gateway and the SPA with IPC working correctly. Do NOT try to access the dashboard via browser at port 9119 unless you've explicitly configured `gateway.transport: http`.

**If you need HTTP transport** (e.g., headless server, Docker): Set `gateway.transport: http` in `config.yaml` and restart the gateway. The SPA will then connect via HTTP instead of IPC.

### 1. Routes Registered, Handler Methods Missing

**Root cause:** A patch script adds route entries to `_http_route_table()` but the corresponding handler method (`async def _handle_xxx`) was never inserted.

**Why it happens:** The idempotence check uses `"_handle_model_options" not in src` — but the just-inserted routes contain `self._handle_model_options`, so the check passes prematurely. The handler method is never added.

**Diagnosis:**
```bash
grep 'api/model/set' api_server.py          # route entries — expect 1
grep 'def _handle_model_set' api_server.py  # handler — expect 1
# If routes exist but handler doesn't → this bug
python -c "import py_compile; py_compile.compile('api_server.py', doraise=True)"
```

**Fix:** Insert the handler methods using a unique ANCHOR string that is NOT part of the route references (e.g. the docstring of an adjacent method). Then verify compilation and restart.

### 2. Silent pythonw Failure

On Windows, `pythonw.exe` runs without a console. Any startup exception is swallowed.

**Common causes:**
- Missing methods referenced in route tables → `AttributeError`
- Missing imports → `ModuleNotFoundError`
- Config file not found → `FileNotFoundError`

**Diagnosis:** Check if process exits immediately with no output. Check exit code. Run the same command without pythonw (terminal) to surface the error.

### 3. Desktop Polling Overrides User Selection

The desktop app polls model state every few seconds via react-query. If the API server gateway is down or returns the config default, the picker reverts to that default.

**Traced flow (June 2026):**
1. User picks model via desktop → `config.set` RPC → TUI gateway → `switch_model()` → `_persist_model_switch()` → writes config.yaml
2. Desktop polls `/api/model/options` on *API server* gateway (port 8642) every few seconds
3. API server is dead (silent failure) → poll fails → desktop falls back to default model
4. Model reverts to `deepseek-v4-flash-free` after each poll interval

## Tracing Desktop → Backend Path

To find which backend endpoint a desktop feature uses:

1. Open the Electron asar in `apps/desktop/release/win-unpacked/resources/app.asar.unpacked/dist/assets/`
2. `grep -oP 'methodName|route' index-*.js`
3. If it uses `t.request("method", ...)` → JSON-RPC → TUI gateway
4. If it uses `fetch("/api/path")` → REST → API server gateway

Then grep the Python source for the handler.

### Python `.pyc` Staleness — Always Check Before Restarting

After patching Python source, confirm the running process actually loaded your changes:

```bash
# Compare source vs bytecode mtimes
stat --format="%Y %y" path/to/source.py
stat --format="%Y %y" path/to/__pycache__/source.cpython-311.pyc
```

If `.pyc` mtime **≥** source mtime, Python uses the old bytecode. Fix:
```bash
touch path/to/source.py              # bump source mtime to now
rm -f path/to/__pycache__/*.pyc       # clear bytecode cache
# Kill and restart the process
# When Python re-imports, it recompiles from patched source
```

**Why it happens:** Python's import machinery compares file mtimes. If `.pyc` exists and is newer, it skips recompilation. The `patch` tool may not update the file's mtime reliably on all systems.

**Pro tip:** After any Python patch, always do `touch source.py && rm -f __pycache__/*.pyc` before restarting the backend process. Verify fresh bytecode exists after restart:
```bash
ls -la __pycache__/source.cpython-311.pyc  # must have current timestamp
```

### `--session` Flag in Desktop `config.set`

The desktop sends `config.set` with `--session` flag (intentional — model selection is designed as per-session), which prevents writing to `config.yaml`. When `model.options` is refetched, the config default appears.

**Fix:** Strip `--session` before parsing:
```python
fixed_value = value.replace("--session", "").strip()
parsed_flags = parse_model_flags(fixed_value)
```

Also override `resolve_persist_behavior` to always return `True` (nuclear option).
Also pass `pin_session_override=False` to `_apply_model_switch` so `session["model_override"]` is NOT set, preventing the session-level override from shadowing the global config.

See `references/model-switch-revert-june2026.md` for full debugging narrative.

## Cron Job Config Pitfalls (gateway-adjacent)

Cron jobs fail in two non-obvious ways; both fixed via `cronjob action=update`:

1. **`script` must be a FILE PATH, never an inline command.** Hermes resolves `script` against `~/AppData/Local/hermes/scripts/`. A job created with `script: python3 -c "..."` fails with `Script not found: C:\...\scripts\python3 -c "` and delivers a Script Error report. Fix: write the command to a real file (e.g. `scripts/weekly-recent-files.py`) and set `script=weekly-recent-files.py`. Keep the script fast (<10s) and prune heavy dirs (`node_modules`, `.git`, `dist`, `.next`, `assets`) — a naive `rglob` over `~/Documents/Projects` times out (>60s).
2. **Model drift blocks unpinned agent jobs.** If the global config's model/provider changed since a job was created (e.g. `opencode-zen/deepseek-v4-flash-free` → `opencode-go/deepseek-v4-flash`), the runtime skips inference: `RuntimeError: Skipped to prevent unintended spend: global inference config drifted since this job was created... and this job is unpinned.` The job's `last_status` flips to `error` even though the script ran. Fix: `cronjob action=update job_id=<id> model=<model> provider=<provider>` to re-pin. After fixing, verify with `cronjob action=run` and check the output file under `~/AppData/Local/hermes/cron/output/<job_id>/`.

## Verification

After fixing:
- [ ] Route method exists: `grep 'def _handle_xxx' api_server.py`
- [ ] Route table clean (no duplicates): `grep -c 'api/xxx' api_server.py` = 1
- [ ] File compiles: `python -c "import py_compile; py_compile.compile('source.py', doraise=True)"`
- [ ] `.pyc` was regenerated with current timestamp: `ls -la __pycache__/*.pyc`
- [ ] Port is listening on expected PID: `netstat -ano | findstr :8642` (verify PID matches expected process, not a stale orphan)
- [ ] Endpoint responds: `curl http://127.0.0.1:8642/api/model/options`
- [ ] Config.yaml mtime updates after model switch: `stat config.yaml` (before → switch → after, mtime must change)
- [ ] Desktop model picker shows models and switch persists past poll interval
