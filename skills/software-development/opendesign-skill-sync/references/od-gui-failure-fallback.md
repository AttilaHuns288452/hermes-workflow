# OD GUI failure modes + validated fallback (session 2026-08-09)

Context: driving OpenDesign headlessly to generate a mobile prototype pinned to
deepseek-v4-flash + mimo-v2.5 only. The GUI pipeline failed; the fallback delivered.

## Symptom → check → action ladder

| Symptom | Check | Action |
|---|---|---|
| CLI says "cannot reach the Open Design daemon at http://127.0.0.1:7456" | Port is random per launch; 7456 is the CLI default | Read `"url"` from `%APPDATA%\Open Design\namespaces\release-stable-win\logs\daemon\latest.log`, set `OD_DAEMON_URL` |
| CLI says "cannot reach ... at http://127.0.0.1:<logged-port>" | `netstat -ano \| grep <pid>` for LISTENING; `curl -m 3` the port | 000 = sidecar dead → restart app via `powershell Stop-Process -Name 'Open Design' -Force; Start-Process <install>\Open Design.exe`, wait ~20s, re-read port |
| `list_projects` → `{"projects": []}` but `SELECT id,name FROM projects` in `data/app.sqlite` has rows | `curl` the daemon port (404 = healthy API root) | Workspace attach failed — GUI frontend won't load (`od://app/` ERR_FAILED; backend 502s). Retry once; then use the opencode-into-project-dir fallback |
| `start_run` → `status: failed, failureDetail: upstream_5xx, failureStage: first_token_wait`, `failureAction: retry` | Read `data/runs/<runId>/events.jsonl` — the CLI stream error carries a server ref like `err_1eec9e84` | Transient provider blip. Health check: `opencode run -m opencode-go/deepseek-v4-flash "ping"` from the project dir (exit 0 = provider fine). Retry the run |

## Validated fallback: generate into the OD project folder

Works when the GUI/daemon pipeline is down but the user needs the artifact:

```bash
# 1. create a temp swarm preset pinning every role to the allowed model
python - <<'EOF'
import json
p = r'C:\Users\YOUR_USERNAME\.config\opencode\oh-my-opencode-slim.json'
cfg = json.load(open(p, encoding='utf-8'))
og = cfg['presets'][cfg['preset']]          # clone the ACTIVE preset
flash = {}
for role, spec in og.items():
    if isinstance(spec, dict) and 'model' in spec:
        s = dict(spec)
        s['model'] = 'opencode-go/deepseek-v4-flash'   # observer -> vision model (mimo-v2.5)
        flash[role] = s
cfg['presets']['flash-only'] = flash
json.dump(cfg, open(p, 'w', encoding='utf-8'), indent=2)
EOF

# 2. generate in the OD project dir (artifact lands where OD expects it)
cd "$APPDATA/Open Design/namespaces/release-stable-win/data/projects/<project-id>"
OPENCODE_SLIM_PRESET=flash-only opencode run -m opencode-go/deepseek-v4-flash "$(cat prompt.txt)"

# 3. restore the config (safe right after launch — config is read at plugin init)
python -c "import json; p=r'C:\Users\YOUR_USERNAME\.config\opencode\oh-my-opencode-slim.json'; c=json.load(open(p)); c['presets'].pop('flash-only',None); json.dump(c,open(p,'w'),indent=2)"
```

Why this works: OpenDesign projects are plain folders under
`data/projects/<slug>/`; a single-file `index.html` there is a valid artifact
(OD infers manifests for HTML entries). The swarm reads its preset at plugin
init, so the temp preset only affects this run.

## JSON-RPC client traps (MCP over stdio)

- initialize id=1, then tools/call with a DIFFERENT id (2). Reusing id 1 makes
  the response matcher return the initialize message.
- Never substring-match `"id":2` — the initialize response's instructions text
  contains it. Parse each line's JSON and compare the top-level `id`.
- Wait ~1.2s after initialize before sending tools/call; a fresh app needs
  longer (bump client timeout to 90s after a restart).

## Model pinning facts

- `list_agents` shows agent IDs (`amr`, `opencode`, `codex`) + per-agent model
  lists with `default` flags. `start_run` accepts `agent` + `model` (bare ids
  like `deepseek-v4-flash` work).
- The executed agent is still `opencode`; the oh-my-opencode-slim plugin then
  hijacks the run and routes by ROLE (designer → kimi-k2.7-code unless pinned).
  Pin via OPENCODE_SLIM_PRESET temp preset; `-m` alone only pins the orchestrator.

## Verification that worked

- JS syntax: extract `<script>` body to temp file, `node --check` it.
- Offline check: grep for `http://`/`https://` external URLs in the HTML.
- Visual QA: playwright headless Chromium at 390×844 viewport, screenshot
  customer + admin (click the mode toggle via JS), then vision model review.
  Chart "empty" in a fast screenshot is often an animation/timing artifact —
  re-check the DOM for bar heights before calling it a bug.
- playwright module not resolvable from arbitrary dirs: run with
  `NODE_PATH=$(npm root -g) node script.js` (global install).
