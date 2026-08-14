# OpenDesign daemon failure modes — diagnosis sequence (2026-08-09)

Full chain observed while generating a mobile prototype through OD's MCP daemon.

## Symptom → cause → fix table

| Symptom | Cause | Fix |
|---|---|---|
| `start_run` accepted, run dies ~15 s later: `status=failed`, `errorCode=AGENT_EXECUTION_FAILED`, `failureCategory=upstream_unavailable`, `failureDetail=upstream_5xx`, `failureStage=first_token_wait` | OD's spawn of the agent carries a **tool token** (`toolTokenExpiresAt` in the run start event) that expired minutes earlier. The provider returns `UnknownError { data: { message: "Unexpected server error...", ref: "err_xxxx" } }` — visible in the run's `data/runs/<runId>/events.jsonl` raw stream | Restart the Open Design app (mints fresh tokens), then immediately `start_run`. Manual `opencode run -m <same-model>` succeeding while OD's runs 5xx is the tell |
| `list_projects` → `{"projects": []}` while `app.sqlite` `projects` table has all projects (check with sqlite3) | Daemon's project store is **workspace-gated**. GUI frontend never attached: desktop log shows repeated `main window did-start-loading` for `od://app/` + `net::ERR_FAILED`; daemon log shows `[langfuse-trace] Vela telemetry failed status=502`, `hub events channel connected` but `no-active-team` | App restart sometimes recovers (restart #1 worked, #2/#3 didn't). If ~2 restarts fail → use the project-dir fallback (see SKILL.md). Don't fight it |
| `get_project <exact id>` also returns `no projects on this daemon` | Same workspace gate — explicit ids don't bypass it | Fallback |
| `tools/call` returns the initialize response (instructions text) instead of the tool result | JSON-RPC id collision: both initialize and tools/call sent with `id` 1; matcher grabbed the first response | initialize `"id":1`, tools/call `"id":2`, match on parsed top-level `"id"` field |
| CLI reports `cannot reach the Open Design daemon at http://127.0.0.1:7456` | Hardcoded default port; real daemon binds a **random port per launch** | Read `"url": "http://127.0.0.1:XXXXX"` from `logs/daemon/latest.log` and set `OD_DAEMON_URL` |
| `Cannot find module ...\@open-design\daemon\dist\cli.js` (MODULE_NOT_FOUND) | App update moved the daemon CLI | Use `resources/app/prebundled/daemon/daemon-cli.mjs` (check `find resources/app -name "daemon-cli.mjs"`) |
| App restart via `taskkill //F` in git-bash | MSYS mangles `//F` | `powershell -NoProfile -Command "Stop-Process -Name 'Open Design' -Force; Start-Sleep 2; Start-Process '<exe>'"` — also kills ALL instances cleanly |

## State inspection points

- Runs: `%APPDATA%\Open Design\namespaces\release-stable-win\data\runs\<runId>\events.jsonl` — start/error/retry events with the child stream's raw error.
- Projects DB: `data/app.sqlite` → `projects`, `agent_sessions` (shows per-run agent+model), `routine_runs`, `run_devloop_iterations`.
- Daemon state: `logs/daemon/latest.log` — `"url"`, `desktopAuthGateActive`, `hub events`, `no-active-team`.
- Desktop state: `logs/desktop/latest.log` — frontend load failures (`od://app/` + `net::ERR_FAILED`), `session-state.json` (`reachedRunning`, `clean`).
- Sidecar env names (for standalone sidecar attempts): `OD_PORT` is the daemon port env (`SIDECAR_ENV.DAEMON_PORT`), `OD_SIDECAR_BASE`, `OD_SIDECAR_IPC_PATH`, `OD_PACKAGED_NAMESPACE_BASE_ROOT = dirname(dirname(runtimeRoot))`. Standalone sidecar also needs launcher handoff state — not worth it; restart the app instead.

## Effort rule

After one failed run + one empty `list_projects`, restart the app once (fresh token). If the second instance still shows `projects: []`, go straight to the project-dir fallback — the GUI workspace is backend-gated and out of our control. Two restarts max.
