# Studio on Linux (Vinegar) + Studio MCP bridge

## Install state probe

- Vinegar: `flatpak list | grep -i vinegar` (also check Sober for the player client).
- Vinegar 1.9.x layout (verified): Studio installs to `~/.var/app/org.vinegarhq.Vinegar/data/vinegar/versions/version-<guid>/`` (StudioMCP.exe sits NEXT TO RobloxStudioBeta.exe there). The wine prefix is `data/vinegar/prefixes/studio`, and Vinegar's bundled Wine is `data/vinegar/kombucha/bin/wine` (NOT on the flatpak sandbox PATH — `flatpak run --command=wine` fails; use `--command=<abs path to kombucha/bin/wine>`). An empty `data/vinegar/` dir means Studio was NEVER installed (the flatpak alone is not an install).
- Install: `flatpak run org.vinegarhq.Vinegar install` — this downloads AND launches Studio on first run. NEVER pipe this through `head`/`less`: the SIGPIPE kills the installer mid-download. `flatpak run` also ignores plain SIGTERM from `timeout` — drive smoke tests with a subprocess + explicit process-group SIGKILL.
- Studio install is agent-doable; only the login click is the HUMAN step (never type Roblox credentials): first launch opens an "Authorize access - Roblox" OAuth page in the browser, the user clicks Authorize, and the `roblox-studio-auth://` callback deep-links back through Vinegar to sign Studio in.
- After login, the Studio side must be enabled (GUI recipe below). `StudioMCP.exe` is an rmcp (Rust) stdio↔WebSocket BRIDGE — Studio connects INTO it on the FIXED WS port **127.0.0.1:13469** (hardcoded in RobloxStudioBeta.exe; Studio dials `http://localhost:13469/studio` every 3s). With no Studio session linked it answers `initialize` and returns `tools: []` ("Timed out waiting for tools to become available").
- **Run the bridge under SYSTEM wine (`/usr/bin/wine`), NOT Vinegar's bundled kombucha wine**: kombucha's wine leaves Studio's WS upgrade request unread in Send-Q forever (tokio/IOCP breakage; wine-staging 11.19 completes the same handshake). Invoke the exe directly with `WINEPREFIX=<prefixes/studio>` — `flatpak run --command=/usr/bin/wine` fails (host binary outside the sandbox).
- Auth token (`appdata/Roblox/StudioMCP/auth.token`, 64 bytes, stable): if Studio's handshake gets RST, copy the token to the prefix-local path too: `<prefix>/drive_c/users/<user>/AppData/Local/Roblox/StudioMCP/auth.token`.
- Launch Studio ONLY via `flatpak run org.vinegarhq.Vinegar` — Vinegar's launch carries the stored Roblox session. A direct `wine RobloxStudioBeta.exe <place>` spawn opens a SECOND instance that bypasses the auth delivery and dead-ends at "Launch failed — Login is required", and a place path passed to plain `wine` (not the exe) fails with `ShellExecuteEx failed`. Stale "Authorize access - Roblox" browser tabs from earlier auth flows linger and mean nothing — judge by the Studio window state itself.
- Port 13469 is single-occupancy: zombie bridge processes hijack it and Studio lands in a dead socket (bytes stuck in Send-Q, "Recv failure: Connection reset by peer"). `pkill -9 -f 'Studio[M]CP'` before testing.
- Race: Studio pushes tools via an unsolicited `init-tools-<uuid>`; if no stdio `tools/list` is waiting, the bridge logs `No proxy found waiting for response init-tools-...` and drops the manifest. Clients calling `tools/list` right after `initialize` win naturally. Verified end-to-end: 34 tools (execute_luau, script_read, multi_edit, start_stop_play, screen_capture, search_game_tree, …) via `hermes mcp test roblox_studio`.
- **UNFIXED PAIRING BUG (2026-11-04, Vinegar + Studio 0.745)**: `list_roblox_studios` stays empty and every instance-targeted tool returns "No Roblox Studio instances are connected" because the `init-tools-<uuid>` session pairing never matches (`ws_server::server: No proxy found waiting for response init-tools-...`). The 34-tool manifest is STATIC in the proxy — tools/list succeeding does NOT prove a Studio link. Ruled out: wine flavor (system/kombucha), token paths, token-enforcement flags, place open/closed, request timing. `DFFlagEnableExternalWebSockets` is already True server-side; `ClientAppSettings.json` FFlag overrides land in `appdata/Roblox/ClientSettings/`.
- **WORKING BRIDGE (verified end-to-end 2026-11-04)**: the plugin-based HTTP bridge (eyedautumn/python_roblox_studio_mcp v0.1.102) fully works. Setup: `RobloxMcpBridge.rbxm` in `<prefix>/drive_c/users/<user>/AppData/Local/Roblox/Plugins/`; bridge daemon `roblox_bridge_server.py` on :28650 (POST /job {job_id,client_id,action,params} + GET /result/<id>); job actions = `run_code`, `run_script_in_play_mode`, `start_stop_play` `{"mode": "start_play"|"stop"|"run_server"}`, `get_studio_mode`, `get_console_output`, `get_playtest_output` (schemas: src/plugin/Tools). CRITICAL ENABLERS: (1) the plugin's `startPolling` gate needs `HttpService.HttpEnabled=true` — set it in the PLACE FILE (`default.project.json`: `"HttpService": {"$properties": {"HttpEnabled": true}}` in the Rojo tree); (2) GUI buttons are unclickable when wine's mouse pump stalls — PATCH the plugin source (repo src/plugin/init.plugin.luau) appending `task.delay(2, startPolling)` at file end and rebuild with `rojo build repo/default.project.json` = auto-start, zero clicks; (3) place-file opens via GUI: Ctrl+O works when modifier keys flow (character typing into the file dialog works even when the command bar doesn't accept typed characters).
- **Playtest probe patterns**: `run_script_in_play_mode` starts its own session (stops on script end; one at a time — a timed-out job leaves the session running and blocks the next with 'previous test still in progress'; stop via `start_stop_play {action:stop}` and wait). Its sessions are SERVER-side probes (player may not have joined at script start — `Players.PlayerAdded:Wait()` first). Real play = `start_stop_play {action:'start_play'}` and judge the UI VISUALLY (screenshots). Client-side errors are invisible to all server channels — install an error-display LocalScript into StarterGui that reads `LogService:GetLogHistory()` and renders errors on screen, then screenshot it.

## Official Studio MCP (preferred)

Built into Studio, stdio transport. Enable: Assistant → ⋯ → Manage MCP Servers → "Enable Studio as MCP server". Documented tools include `list_roblox_studios` (returns studio_id used on later calls), `script_read`, `multi_edit` (creates the script if the path doesn't exist), `script_search` (fuzzy), plus Luau execution / playtest / output inspection per https://create.roblox.com/docs/studio/mcp. Official configs target Windows (`cmd.exe /c %LOCALAPPDATA%\Roblox\mcp.bat`) and macOS only.

## Linux wrapper (selected bridge pattern)

A small shell wrapper locates `StudioMCP.exe` and pipes stdio through SYSTEM wine (see the wine bullet above — kombucha's wine breaks the handshake). Note the `Z:\` ABSOLUTE path mapping (`Z:` + relative path silently resolves against Z:'s cwd — worked by luck once, don't rely on it):

```bash
#!/bin/bash
set -u
VG="$HOME/.var/app/org.vinegarhq.Vinegar/data/vinegar"
MCP=$(find "$VG/versions" -name "StudioMCP.exe" -print -quit 2>/dev/null)
[ -z "$MCP" ] && MCP=$(find "$VG/prefixes" -name "StudioMCP.exe" -print -quit 2>/dev/null)
[ -z "$MCP" ] && { echo "StudioMCP.exe not found" >&2; exit 1; }
WIN_PATH=$(echo "$MCP" | sed 's|^/|Z:\\|' | tr '/' '\\')
exec env WINEPREFIX="$VG/prefixes/studio" /usr/bin/wine "$WIN_PATH" --stdio "$@"
```

Register with Hermes in `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  roblox_studio:
    command: /home/attila/.local/bin/roblox-studio-mcp.sh
    enabled: true
```

Community confirmation this pattern works (AdilZhalgasbay/roblox-studio-mcp-linux, MIT; devforum Vinegar/Codex guides use the same shape with a registry-query fallback for the ContentFolder).

## Verification checklist (run before trusting the bridge)

1. `list_roblox_studios` returns the open instance.
2. `script_read` on an existing script.
3. `multi_edit` creates a test script, then delete it.
4. Execute harmless Luau (spawn + remove a part).
5. Start and stop a playtest.
6. Retrieve output/errors from the playtest.

All six must pass before ANY workflow assumes Studio automation. Until then the game stays source-driven (Rojo build + static verification) and the docs say "not playtested".

## StudioMCP proxy architecture (verified)

`StudioMCP.exe` (Rust, rmcp) speaks MCP to the client over stdio and hosts a WebSocket endpoint that ROBLOX STUDIO connects into as a client — Studio polls `http://localhost:13469/studio` every ~3s (its log shows `WebSocketTraceError ... /studio ConnectFail` while nothing is listening). Same data dir: `appdata/Roblox/mcp.bat` = plain `StudioMCP.exe %*` (a wrapper exec'ing the exe with `--stdio` is equivalent to the official launcher) and `appdata/Roblox/StudioMCP/auth.token` = shared auth token (64 chars; `FFlagStudioMCPProxyToken*` gates enforcement). `StudioMCP.exe --print-flags` dumps its fast-flag state.

- **Exactly one bridge process may exist at a time.** The WS host port is fixed, so a leftover bridge (e.g. from a killed smoke test) silently steals it: Studio keeps talking to the zombie while every fresh bridge answers `tools/list` with `[]` after "Timed out waiting for tools". Before any bridge probe: `pkill -9 -f 'Studio[M]CP'` (bracket-guard the pattern — a plain pattern matches the pkill's own shell and self-kills the command), start ONE bridge, then wait for Studio's reconnect loop to establish the loopback pair (`ss -tn` / `/proc/net/tcp` ESTAB on the WS port) BEFORE requesting tools.
- `flatpak run` wrappers survive `timeout`'s SIGTERM — drive bridge probes with a subprocess and `os.killpg(SIGKILL)`, and drain both stdout and stderr with `select` (a blocked stderr pipe stalls the whole probe).

## Enabling the Studio-side toggle (GUI recipe)

The Assistant button does not exist on the Studio landing page — open a place first (Ctrl+O, type the Windows path form `Z:\home\...` in the File name box; unix paths are rejected). Two modals silently EAT Ctrl+O (the shortcut "does nothing" while one is up — screenshot and look before blaming input focus): a "Lighting Technology Migration" dialog on opening older places (Continue dismisses it) and an "Auto Recovery File Found" prompt after an unclean exit (Review/Ignore — choose Ignore whenever the on-disk file is the authoritative build; the recovery copy is a stale autosave). Then drive vision-guided clicks (`gnome-screenshot -f` to capture; ask vision for coordinates in ORIGINAL pixel space; re-screenshot and verify after every click — vision coordinates drift and menus move):

1. Ribbon top-right icon cluster: Assistant sits left of the notification bell.
2. Assistant panel → "…" kebab on the session row — it EXPANDS panel sections in place ("Settings", "Usage"), it is not a popup menu.
3. "Assistant Settings" dialog → sidebar "MCP Servers" → toggle "Enable Studio as MCP server" (top-right of the pane).
4. Cheap state check without screenshots: the Studio status bar chip reads "● MCP off" / "● MCP Ready".

## Studio startup hangs and "not responding" under Vinegar

Symptom: Studio processes at 0% CPU, no window, no new lines in `appdata/Roblox/logs/`. Fixes in order:

1. Kill the session INCLUDING the wineserver: `WINEPREFIX=<prefix> <kombucha>/bin/wineserver -k`, then `kill -9` any surviving `winedevice.exe`/wineserver pids — a stale wineserver from a hung session wedges every later launch until removed.
2. Check the Vinegar log for DXVK: first installs can skip it and Studio hangs before rendering; a relaunch that logs "Downloading DXVK" / "Using the Vulkan renderer" fixes it.
3. Do NOT pin `forced_version` to an older build to dodge a hang — Roblox's backend rejects old Studio versions at startup ("The version of Roblox Studio is out of date") and the app is unusable; unpin immediately.

Intermittent "Vinegar/Roblox Studio is not responding" banners (transient, self-recovering) are Wine message-loop stalls: WebView2/auth waits, DXVK shader compilation bursts (worst on the first run after a GPU change), and general Wine message-pump overhead. On Optimus laptops the durable mitigation is to pin Studio to the dGPU PERMANENTLY via the flatpak (survives menu launches, unlike wrapper scripts):

```bash
flatpak override --user --env=__NV_PRIME_RENDER_OFFLOAD=1 \
  --env=__VK_LAYER_NV_optimus=NVIDIA_only \
  --env=__GLX_VENDOR_LIBRARY_NAME=nvidia org.vinegarhq.Vinegar
```

Verify with `flatpak run --command=sh org.vinegarhq.Vinegar -c 'echo $__VK_LAYER_NV_optimus'`. The first launch after this change does a one-time shader compile (extra stalling) — warn the user. If the "not responding" dialog's Wait/Force Quit buttons are unclickable (the WM overlay itself stalls), end the session from a terminal instead of fighting the dialog.

## Fallback: plugin-based HTTP bridge (eyedautumn/python_roblox_studio_mcp)

For when the official WS pairing fails entirely. A Studio plugin polls an HTTP daemon; tool calls travel as plain HTTP jobs — no WS pairing, no tokens. Status: daemon + HTTP API VERIFIED working; end-to-end NOT yet verified (needs the GUI click below).

- Get `RobloxMcpBridge.rbxm` from the GitHub releases into `~/.var/app/org.vinegarhq.Vinegar/data/prefixes/studio/drive_c/users/<user>/AppData/Local/Roblox/Plugins/` (plugins are scanned at Studio START — install before launching). The daemon is `src/server/roblox_bridge_server.py` (stdlib-only, no deps).
- Run `python3 roblox_bridge_server.py` once (port 28650); agents talk to it DIRECTLY over HTTP, no stdio adapter needed: `POST /job {job_id, client_id, action, params}` then poll `GET /result/<job_id>` → `{ok, ready, result}`; `GET /status` lists Studio clients (the plugin's poll marks presence, 15s staleness window); `GET /health` for the daemon alone. Plugin actions are the `roblox_*` tool names (run_code, start_stop_play, get_console_output, get_studio_mode, bulk_create_instances, ...).
- GUI steps after a place opens: the "Roblox MCP" toolbar button appears → **Start Bridge Polling** (one click; the widget's client_id defaults to the PlaceId — use that id in `/job` calls). HTTP Requests in Game Settings → Security may need enabling (the plugin attempts it).
- **The plugin panel is the control surface, and polling is manual.** It reads `Status: stopped|running`, `Client ID`, `Jobs completed`, with Start/Stop Bridge Polling buttons. A healthy daemon plus an empty `GET /clients` means nobody is polling — click Start in the Studio window, then re-check `/clients` before concluding the bridge is broken. Patching the plugin with a `task.delay(2, startPolling)` tail removes the click.
- **Entering Play mode ends that plugin session, and the panel keeps lying about it.** `start_stop_play {"mode":"start_play"}` takes the place into a test datamodel, after which `/clients` reports the id as `connected: false` while the panel still renders `Status: running (connected)` with a stale job count. The key is `mode`: `{"is_start": true}` answers `Unknown Studio mode (supported: start_play, stop, run_server)`. A real Stop→Start in the panel DOES revive polling (verified — the id returns `connected: true`), so two human clicks are cheaper than losing the window; what does not work is blind coordinate clicking at the panel while the window has no focus, which reads as "unrecoverable" when it is only an input miss. Order the work so it cannot bite at all: **inject `write_script` fixes and publish BEFORE the first playtest**, and treat `/clients` — never the panel label — as the readiness signal.
- **`run_code` runs in the EDIT datamodel even while a playtest is live**, so a playtest character is not reachable from it (you get `no character` / an empty Players query that looks like a spawn bug). Character-level assertions belong to `run_script_in_play_mode` or the real client, not to cross-datamodel `run_code` calls.
- **`client_id` defaults to the PlaceId, so `0` means you are driving a LOCAL file.** Any Studio window that opened a `.rbxlx` from disk registers as `0`, the daemon keeps one entry per id, and only the latest poller is served — two Studio windows therefore send jobs to whichever polled last. A `run_code` that reports the wrong place/contents is a two-instance symptom first: run exactly one Studio, or give each a distinct Client ID in the panel before starting polling.
- **Assert the session before acting on it:** `run_code 'return tostring(game.PlaceId)'`. `0` = local file. Pair it with a cheap content probe (`#ServerScriptService:GetChildren()`) so an almost-empty result reads as "wrong session" rather than "map did not build".
- **A local `.rbxlx` cannot be published over the live place.** With PlaceId `0`, File → Publish opens the *Publish Experience → Basic Info* new-experience flow, and its "Update existing experience..." link does nothing under Wine (clicked repeatedly, no state change). There is no post-hoc way to point a file at an existing place, so to update a shipped game drive the session that ALREADY has the cloud place open (its Client ID is that place's id) and push the changed scripts into it.
- **Pushing a fix into the live place: `write_script` → read back → Publish.** `write_script {path: "ReplicatedStorage.Shared.Config", source: "<file contents>"}` takes DOT-notation from the service (`StarterGui.UiScaler`, `ServerScriptService.Server.MapBuilder`) and the source read straight off disk — never hand-retyped — so the place matches a commit instead of a drifted variant. A `{ok:true}` only means the job queue accepted it: assert the text arrived by reading `Source` back for a marker unique to that edit (`string.find(script.Source, "<new id or symbol>")`) for every file you wrote. Then File → Publish in that same window; success is the Studio toast *"Published. Eligible players can play now"*, and the independent proof is `games.roblox.com/v1/games?universeIds=<id>` returning an `updated` timestamp newer than the edit.
- **Publish with `Alt+P`, not by clicking the File menu.** The File menu is not a stable target: once a place has been published it gains a "Save to Roblox with Notes" row that shifts every item below it, so a coordinate that hit Publish on one attempt lands on **Manage Audience** the next and opens a modal — which then swallows `Alt+P` until dismissed. `Alt+P` is idempotent and layout-independent; if it appears to do nothing, look for a modal over the window (Escape) before concluding the publish failed. Confirm by the `updated` timestamp, never by the toast alone.
- **Injecting files leaves the rest of the place at its last published state.** Only the scripts you wrote are at HEAD; everything else is whatever the previous publish contained, so the live game is a hybrid and the repo is no longer what is running. Diff against the last published commit before injecting, name the gap, and treat the next publish from a file-backed session as the reconciliation step.
- **Call the daemon directly; don't wait on an MCP stdio round-trip.** `POST /job {job_id, client_id, action, params}` then poll `GET /result/<job_id>`, or use `tools/rbxjob.py <action> '<json>' <timeout>` — sub-second, and it surfaces the plugin's own error strings (`Unknown job type: ...`) that identify the action name. Result shape: `{ok, job_id, result: {result: "[RETURNED RESULTS] <value>\n"}}` — the payload is a STRING inside a nested `result`; strip the prefix before comparing.
- Job actions verified working this way: `run_code` (arbitrary Luau in the Edit datamodel), `start_stop_play`, `get_studio_mode`, `get_console_output`, `script_read`/`write_script`. Full action list is the handler table in `src/plugin/init.plugin.luau`.

## Other fallbacks + risks

- Live sync alternative: `rojo serve` + the Rojo Studio plugin keeps the source tree authoritative and reduces how much the MCP must do.