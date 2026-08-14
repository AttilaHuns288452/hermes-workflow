# Driving Open Design headlessly via its MCP daemon

Verified 2026-08-09. Full pipeline works: list projects, read/write files,
commission generation runs (`start_run`), poll (`get_run`), pull artifacts —
no GUI clicking needed. The desktop app must be RUNNING (it hosts the daemon),
but it never needs to be visible or interacted with.

## Spawn recipe

```python
import subprocess, json, os, threading, time

base = r"C:\Users\YOUR_USERNAME\AppData\Local\Programs\Open Design release-stable-win"
cli = os.path.join(base, r"resources\app\prebundled\daemon\daemon-cli.mjs")  # NOT node_modules/@open-design/daemon/dist/cli.js (stale after app update)
env = os.environ.copy()
env["OD_DATA_DIR"] = r"C:\Users\YOUR_USERNAME\AppData\Roaming\Open Design\namespaces\release-stable-win\data"
env["OD_SIDECAR_NAMESPACE"] = "release-stable-win"
env["ELECTRON_RUN_AS_NODE"] = "1"

# CLI defaults to http://127.0.0.1:7456 but the real daemon listens on a
# RANDOM port per launch. Read it from the daemon log:
log = os.path.expandvars(r"%APPDATA%\Open Design\namespaces\release-stable-win\logs\daemon\latest.log")
url = None
if os.path.isfile(log):
    for line in open(log, encoding="utf-8", errors="replace"):
        if '"url"' in line and "127.0.0.1" in line:
            url = line.split('"url": "')[1].split('"')[0]
env["OD_DAEMON_URL"] = url or "http://127.0.0.1:7456"

proc = subprocess.Popen([os.path.join(base, "Open Design.exe"), cli, "mcp"],
                        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE, text=True, bufsize=1, env=env)
# talk JSON-RPC 2.0 (MCP protocol) over stdin/stdout:
# {"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{...},"initializationOptions":{"bloom":False}}}
# then {"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"list_projects","arguments":{}}}
```

Working script: `~/AppData/Local/hermes/scripts/opendesign-direct-call.py` (already fixed with port auto-discovery).

## Tool surface (MCP tools/list)

| Tool | Use |
|---|---|
| `list_projects` | discover projects; each has id, name, status{value, runId} |
| `get_active_context` | project+file the user has open in the GUI (expires ~5 min after last interaction) |
| `get_artifact` | entry file + all referenced siblings (prefer over get_file for design bundles) |
| `get_file` / `search_files` / `list_files` | read/search file metadata; `since=<unix-ms>` cheap-poll |
| `create_artifact` / `write_file` / `delete_file` | write project files (create_artifact rejects existing; write_file overwrites) |
| `create_project(name, [designSystem], [skill])` | new project; start_run requires an existing project |
| `list_skills` / `list_plugins` | what OD can generate with (plugins = our design-* exports) |
| `list_agents` | ONLY agents returned here will actually spawn — don't guess 'claude'/'codex' |
| `start_run(prompt, [skill], [plugin], [inputs], [agent], [model])` | commission generation; returns runId immediately; **agent/model overrides per run** |
| `get_run(runId)` | poll → queued/running/succeeded/failed/canceled; on success gives previewUrl + agentMessage |
| `cancel_run(runId)` | abort (only if user asks) |

## Workflow + patience rules

- Generation runs take **5–30 min**. `status:running` with unchanged file mtimes = inner agent thinking, not a hang. Poll every 30–60 s; do NOT cancel and hand-write files as a "faster" workaround — the daemon's instructions explicitly warn this throws away pipeline design quality.
- On success: `get_artifact` to pull files; `previewUrl` opens in a browser.
- Project args accept UUID or name substring (server resolves; response carries `resolvedProject`).
- Ambiguous deliverables (PPT/deck/PDF): OD only produces browser-viewable HTML/SVG — ask the user which they want before starting a run.

## Model slots (app-config.json → agentModels)

`%APPDATA%\Open Design\namespaces\release-stable-win\data\app-config.json`:
- `hermes` slot: model `"default"` (= Hermes config default, deepseek-v4-flash)
- `opencode` slot: `opencode/mimo-v2.5-free`

For design generation the best pick in Attila's stack is `opencode/mimo-v2.5-pro` (multimodal — can see/self-correct visuals). Edit this file only while the app is closed (it rewrites it).

## Pitfalls

- Daemon CLI path moved on app update: `node_modules/@open-design/daemon/dist/cli.js` → `resources/app/prebundled/daemon/daemon-cli.mjs`. If MODULE_NOT_FOUND, re-find with `find resources/app -name "daemon-cli.mjs"` or `grep -rl "tools/call" resources/app/prebundled/daemon`.
- Port 7456 is a default, not the truth. No listener on 7456 + "cannot reach the Open Design daemon" = wrong/missing OD_DAEMON_URL, not a dead app. Check `logs/daemon/latest.log` for `"url"`.
- App not running → daemon unreachable (list_projects errors). Verify with `tasklist | grep -i "open design"`.
