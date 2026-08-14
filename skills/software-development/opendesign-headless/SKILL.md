---
name: opendesign-headless
description: "OpenDesign headless via MCP: runs, artifacts, fallback."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
tags: [opendesign, mcp, prototype, generation, headless]
related_skills: [opendesign-skill-sync, oh-my-opencode-slim]
---

# OpenDesign Headless

Open Design exposes a full MCP server (name `open-design`, v0.2.x) over stdio. The daemon CLI is spawned with the app's own Electron binary in node mode; tools talk JSON-RPC. This lets you create projects, start generation runs, poll them, and pull artifacts without touching the GUI.

## Working client scripts (already on disk)

- `~/AppData/Local/hermes/scripts/od-gen.py` — modes: `agents` | `plugins` | `projects` | `create <name>` | `run "<prompt>" <project> <model> [design-system]`. `run` starts and polls to completion (5–30 min typical).
- `~/AppData/Local/hermes/scripts/opendesign-direct-call.py` — minimal list_projects probe.
- `~/AppData/Local/hermes/scripts/od-prompt.txt`, `od-prompt-dental.txt` — proven prototype briefs (mobile-first, Customer⇄Admin modes, single self-contained index.html, no CDN, localStorage, #5e6ad2 accent).

## Spawn recipe (critical details)

```python
cli = os.path.join(BASE, r"resources\app\prebundled\daemon\daemon-cli.mjs")  # NOT node_modules/@open-design/daemon/dist/cli.js — app updates move it; if missing, `find <install>/resources/app -name "daemon-cli.mjs"`
cmd = [os.path.join(BASE, "Open Design.exe"), cli, "mcp"]
env: ELECTRON_RUN_AS_NODE=1, OD_DATA_DIR=<namespace data dir>, OD_SIDECAR_NAMESPACE=release-stable-win, OD_DAEMON_URL=<sidecar url>
```

- **Daemon URL is a random port per app launch.** Read it from `%APPDATA%/Open Design/namespaces/release-stable-win/logs/daemon/latest.log` — last `"url": "http://127.0.0.1:XXXXX"` line. Never hardcode (7456 is only the dev default).
- **JSON-RPC ids must be distinct**: initialize with `"id":1`, then tools/call with `"id":2`. Sending both with the same id makes the client match the initialize response and silently return wrong data.
- First call after spawning needs ~1–2 s settle before sending tools/call.

## Generation flow

1. `list_agents` → agents available (e.g. `amr` = OD's router with model list incl. deepseek-v4-flash default; `opencode`; `codex`). Do NOT guess agent ids.
2. `create_project {"name": ...}` or reuse existing (id or name substring).
3. `start_run {"prompt", "agent", "model", "project"}` → runId immediately. OD spawns its own agent. **Model id MUST be provider-qualified: `opencode-go/deepseek-v4-flash`, never bare `deepseek-v4-flash`** — bare ids resolve to a broken/exhausted route (opencode-zen, logged `429 FreeUsageLimitError`) and the run dies with the SAME `AGENT_EXECUTION_FAILED`/`upstream_5xx` as an expired token, even on a fresh app (verified 2026-08-12: bare id failed twice, qualified id ran fine). Before restarting the app for "expired token", probe: `opencode run -m opencode-go/deepseek-v4-flash "Reply with exactly: PONG"` — `PONG` means the backend is fine and the model id (or project store) is the real problem. od-gen.py's `run` default is already `opencode-go/deepseek-v4-flash`; only an explicit bare id overrides it.
4. `get_run runId` every 30–60 s. 5–30 min is normal; `status:running` with unchanged file mtimes = inner agent thinking, NOT a hang.
5. On success: `previewUrl` + `get_artifact` to pull files.

## Model pinning (only-X-models constraints)

OD's opencode agent loads the oh-my-opencode-slim swarm plugin → the run's ACTUAL model usage follows the swarm preset, not just `model`. See `oh-my-opencode-slim` skill for the `OPENCODE_SLIM_PRESET` temp-preset recipe (e.g. all roles → deepseek-v4-flash, observer → mimo, then restore the config).

## Failure modes (all seen 2026-08-09)

- **Install path probe gotcha (false "not installed")** — the app lives at `C:\Users\YOUR_USERNAME\AppData\Local\Programs\Open Design release-stable-win\Open Design.exe` (note the `release-stable-win` suffix). Probing `Programs\Open Design\` (without suffix) returns nothing → do NOT conclude "not installed"; run `find ~/AppData/Local/Programs -maxdepth 2 -iname "Open Design.exe"`. If truly absent, author the design system directly (DESIGN.md tokens/specs) and produce the deliverable as a **single-file HTML with fixed 390×844 phone frames for Figma import** — that is often the user's actual target ("so i can put it on figma"), not a generated prototype. Full workflow in the `mobile-ui-figma-handoff` skill.

- **`upstream_5xx` / `AGENT_EXECUTION_FAILED` at first_token_wait, exit 1** — OD's spawn carries a tool token that expires ~5 min after the app launches; runs started after that fail with `UnknownError` + `err_<ref>` in the run's events.jsonl (`data/runs/<runId>/events.jsonl`) while manual `opencode run` with the same model works. Fix: restart the app (fresh token, new random port), then immediately start the run.
- **`list_projects` → `[]` though app.sqlite has all projects** — the daemon's project store is workspace-gated; the GUI frontend failed to attach (`od://app/` + `net::ERR_FAILED`, hub/Vela 502s = OD backend flaky). App restarts may or may not recover it; explicit `get_project` by id also fails. **After an app restart, `start_run` can also fail with `no projects on this daemon`** — the store did not survive the restart. Recovery: `create <name>` again on the CURRENT daemon (returns a NEW slug, e.g. `guardian-alert-8446`), then `run` against the new id. See `references/daemon-failure-modes.md` for the full diagnosis path.
- **Windows restart recipe (proven 2026-08-12)** — when the token expired or the sidecar died: kill ALL instances with `powershell -Command "Stop-Process -Name 'Open Design' -Force"` (git-bash `taskkill //F //IM` and `cmd //c start` are unreliable through the bash wrapper — verify with `tasklist` that PIDs actually changed), relaunch via `powershell -Command "Start-Process -FilePath '<install>\Open Design.exe'"`. Then WAIT: the old port URL lingers in `latest.log` and the log can even truncate empty while the daemon restarts; the sidecar binds lazily (up to ~1-2 min). **A URL line in the log ≠ a listening port** — confirm with `netstat -ano | grep LISTENING | grep 127.0.0.1:<port>` before running. `od-gen.py` printing `START: fetch failed` means the spawned daemon couldn't reach the sidecar (stale URL / not bound yet) — wait for the listening port, retry, don't debug the script. The sidecar can die again after a relaunch (seen once); probe-loop for a fresh URL+listening pair. Cap restarts at ~2 per the pitfall below, then use the fallback.
- **`hard_quota` / `rate_limit` after several minutes, child exit 0, empty output** — distinct from upstream_5xx: the run lives 3–10 min, then the `end` event shows `status: failed`, `failureCategory: rate_limit`, `failureDetail: hard_quota` ("Agent completed without producing any output"). The provider's free quota is exhausted; retrying immediately fails the same way. BUT the run may still have delivered: check the `end` event's `artifactPaths` and `<data>/projects/<slug>/` before re-running — a failed run CAN capture the artifact (seen 2026-08-12: GUI run died on hard_quota after the designer wrote 9 screens; artifact registered and usable).
- **Pitfall: don't spend 4+ app restarts fighting the workspace.** If the daemon won't attach after ~2 restarts, switch to the fallback below.

## Monitoring runs (incl. the GUI's own runs)

Runs land in `<data>/runs/<runId>/`. `events.jsonl` lines are `{"id","event","data","timestamp"}` with event types: `start` (model, projectId, cwd, toolTokenExpiresAt), `agent` (`text_delta` / `status` / `usage`), `diagnostic`, `end` (status, artifactPaths, failureDetail). `state.json` mirrors status/model/projectId. GUI-initiated runs are in the SAME store — you can watch the user's in-app run headlessly.

- Swarm flow: the orchestrator's `text_delta` "Dispatching the build to @designer" means planning is done; then events go quiet 5–20 min while the designer child works (its output returns on completion). Silence ≠ hang — check for a heavy `node.exe` (300–500 MB) via `tasklist`.
- A first @designer dispatch can die without writing ("The interrupted dispatch never wrote the file (directory is empty). Re-dispatching the designer build.") — the orchestrator retries automatically; not a failure signal.
- The project dir can be deleted/recreated by the app mid-run (od-owned workspace) — re-stat `<data>/projects/<slug>/` instead of caching its existence.

## Fallback: generate straight into the project dir (works even when the daemon is dead)

1. `mkdir -p <data>/projects/<slug>` (slug like `mobile-admin-customer-prototype-89ec`).
2. From inside that dir, run the swarm with a pinned preset (see oh-my-opencode-slim) or plain `opencode run -m <model> "$(cat prompt.txt)"`. If the opencode CLI's remote routes error out but Hermes works (probe: `hermes -z "Reply with exactly: PONG"`), run the generation via `hermes -z "$(cat prompt.txt) … write index.html in cwd; reply with the path"` from inside the dir — same artifact, working route. Do NOT run it concurrently with an OD GUI run in the same project dir (both write index.html; kill the redundant one).
3. Verify: file exists, `node --check` on the extracted inline `<script>`, grep for `http`/`cdn`/`<link>` (must be none), then playwright mobile screenshots + vision QA (see visual-qa skill).
4. When OD recovers, the folder is picked up as a project automatically.

## Verification chain for generated prototypes

Extract + syntax-check the inline JS, confirm zero external URLs, screenshot at 390×844 via playwright (`NODE_PATH=$(npm root -g) node shot.js` — see visual-qa), vision-QA each mode, fix `main { padding-bottom }` ≥110px when a fixed bottom nav exists (content otherwise scrolls under it), re-shoot.

- **OD artifacts can be incomplete** (designer dies mid-spec): supplement missing screens by hand IN THE ARTIFACT'S OWN SYSTEM — reuse its CSS classes, design tokens, and internal SVG sprite (`<use href="#icon-...">`), add `data-od-id` to new elements. Verified 2026-08-12: added 4 screens (change-account sheet, delete/logout dialogs, success toast) to a 9-screen OD artifact; re-shot 13 frames clean.
- **Vision-QA flags are often noise on generated screens** — verify geometrically before editing (playwright `getBoundingClientRect` on flagged elements: gaps, button widths, gutters). 5 of 5 flags across two rounds were disproven by measurement; only one real bug (a stray `</span>` nesting an avatar) ever survived measurement.

See `references/daemon-failure-modes.md` for error refs and the app-state diagnosis sequence.
