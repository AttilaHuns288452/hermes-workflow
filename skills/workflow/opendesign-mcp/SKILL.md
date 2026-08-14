---
name: opendesign-mcp
description: Drive OpenDesign headlessly via its MCP daemon.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [OpenDesign, MCP, Design, Automation]
    related_skills: [opendesign-sync, oh-my-opencode-slim]
---

# OpenDesign headless (MCP daemon)

OpenDesign's GUI is an Electron app whose **sidecar daemon** exposes the full MCP toolset over stdio. You can commission design generations, read/write project files, and poll runs without touching the window.

## Wiring (Windows)

- App: `C:\Users\YOUR_USERNAME\AppData\Local\Programs\Open Design release-stable-win\Open Design.exe`
- Daemon CLI: `<app>\resources\app\prebundled\daemon\daemon-cli.mjs` — **NOT** `node_modules\@open-design\daemon\dist\cli.js` (moved after an app update; check `find <app>\resources\app -iname "*daemon*"` if it moves again)
- Spawn: `Open Design.exe daemon-cli.mjs mcp` with env:
  - `ELECTRON_RUN_AS_NODE=1`
  - `OD_DATA_DIR=<...>\Open Design\namespaces\release-stable-win\data`
  - `OD_SIDECAR_NAMESPACE=release-stable-win`
  - `OD_DAEMON_URL=http://127.0.0.1:<PORT>` — **port is random per app launch**; read it from `%APPDATA%\Open Design\namespaces\release-stable-win\logs\daemon\latest.log` (line containing `"url": "http://127.0.0.1:`).
- Talk JSON-RPC over stdin/stdout: initialize (id 1) → tools/call (id 2). **Pitfall: JSON-RPC ids must be distinct** — reusing id 1 for tools/call makes the client match the initialize response (looks like list_projects returning the instructions blob).
- Ready-made client: `scripts/od-gen.py` (modes: `agents | plugins | projects | create <name> | run "<prompt>" [project] [model]`).

## Key tools

- `list_projects` / `get_project(project)` — note: resolution can fail even when the project exists in `data/app.sqlite` (see failures).
- `create_project(name)` then `start_run({prompt, agent, model, project})` → returns runId immediately.
- `get_run(runId)` → poll every 30-60s; runs take **5-30 min**; terminal = succeeded/failed/canceled. On success: previewUrl + pull files via `get_artifact`.
- `list_agents` — real agent ids + per-agent model lists (e.g. agent `amr` has `deepseek-v4-flash` as default). Don't guess agent ids.
- `list_plugins` / `list_skills` — installed design systems (the exported `design-*` plugins) and recipes for `start_run`.

## Model pinning

Pass `agent` + `model` to `start_run`. But note OD's opencode agent loads the oh-my-opencode-slim swarm plugin, whose active preset routes roles to other models (designer → kimi-k2.7-code!). See `references/opencode-swarm-interaction.md` for the flash-only preset pattern that guarantees a model whitelist.

## Failure modes (all seen 2026-08-09)

1. **`AGENT_EXECUTION_FAILED` / `upstream_5xx` at `first_token_wait`** — the spawned opencode's provider call died before the first token. Check `runs/<runId>/events.jsonl` for the CLI stream error (`UnknownError` + `ref`). If a manual `opencode run -m <same model>` works, the issue is OD-side: **stale tool token** (events show `toolTokenExpiresAt` earlier than run start after an app restart) → **restart the app** to mint fresh tokens, then retry.
2. **`list_projects` returns `[]` while `data/app.sqlite` has rows** — the GUI's workspace never attached (app frontend fails: `od://app/` + `net::ERR_FAILED` in `logs/desktop/latest.log`; daemon log shows Vela/langfuse 502s). Restarting may or may not recover; this is upstream-network-dependent. Fallback: generate via opencode directly into the OD project dir (`data/projects/<project-id>/index.html`), so the artifact is already an OD project when the GUI recovers.
3. **App restart on git-bash**: `taskkill //F //IM` mangles flags; use `powershell -NoProfile -Command "Stop-Process -Name 'Open Design' -Force; Start-Sleep 2; Start-Process '<exe>'"`, wait ~20-25s, re-read the daemon URL (changes every launch).

## Related

- Skill export/import (plugins, `design-*`) → `opendesign-sync`; export script: `%LOCALAPPDATA%\hermes\scripts\export-design-skills-to-opendesign.py` (idempotent, includes `HERMES_EXTRA` list of Hermes-local UI/UX skills).
