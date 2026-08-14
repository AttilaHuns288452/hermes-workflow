# Open Design app ↔ Hermes ACP agent — debugging

## Architecture

- The Open Design app (v0.18.x) spawns `hermes acp` (Agent Client Protocol, JSON-RPC over stdio) per chat run: run state shows `"bin": "hermes", "streamFormat": "acp-json-rpc"`.
- Agent/model config: `%APPDATA%/Open Design/namespaces/release-stable-win/data/app-config.json` → `agentId`, `agentModels.hermes.model` (`"default"` = Hermes config.yaml `model.default` = deepseek-v4-flash via opencode-go) and `agentModels.opencode.model`.
- Run telemetry per run: `data/runs/<run-uuid>/state.json` (agentId, model, status, error, exitCode, signal, failureCategory, failureDetail, analyticsTelemetry timeline incl. firstTokenAt/finalizeStartAt) + `events.jsonl` (every event: `stderr` [Hermes' own logs], `status`, `thinking_delta`, `error`, `runtime_close`, `end`). events.jsonl gets rewritten in place on retry — re-read if results shift.

## Failure signature: "Hermes not responding" in the app

- App-side state.json: `"error": "ACP response timed out after 600000ms"`, `status: failed`, `signal: SIGTERM`, `failureCategory: "auth"`, `failureDetail: "auth_required"` — **the auth label is a red herring**; it's the app's heuristic for "no ACP response before the 600s deadline".
- Hermes-side stderr: `concurrent tool batch timed out after 420.0s; N tool(s) still running: search_files` — shell-backed tools (search_files, terminal, write_file linters) hang under the ACP child; pure-Python tools (session_search, skill_view) complete in <1s.
- Model/provider is NOT the cause: preceding stderr lines show `API call #N: model=deepseek-v4-flash provider=opencode-go ... latency=9-55s` succeeding, then thinking_deltas stream, then the tool batch hangs.
- Telling control: a successful run exists with `tool_turns=0` (agent answered chat-only, never touched shell tools) — tool execution, not the model, is the failure point.
- Suspected mechanism (observed, not fully root-caused): search_files → `_get_file_ops` → `LocalEnvironment.__init__` → `init_session()` login-shell snapshot (`bash -l` env capture; `tools/environments/local.py` + `base.py`) stalls under the ACP child; a stuck creation thread may hold the per-task creation lock so retries hang too. Raw `rg` over the same tree is fast (0.4s / 19k files), so the search target is not the problem. `bash -l -c true` is fast from a normal shell — the stall is ACP-process-specific.

## Fix ordering

1. **In the app, switch the agent to `opencode`** (configured as `opencode/mimo-v2.5-free` in app-config.json) — proven working in run history. Fastest unblock.
2. **Remove duplicate skills** causing `skill_view` ambiguity inside the agent's turn (e.g. `~/.agents/skills/decide` vs local `skills/decide`; same for `hermes-agent`, `opendesign-skill-sync`, `stop-slop`, etc.) — the failed skill_view steers the agent into the hang loop.
3. If Hermes must work in-app: temporarily disable the auto-registered MCP servers (codegraph, graphify, obsidian-kg, vscode, agentmemory, llmquant-data, 21st, firecrawl — `opendesign` + `figma` fail to connect anyway) and re-test; bisect from there. Root fix is Hermes core (shell env under the ACP child); a `hermes update` may eventually land it.

## Driving `hermes acp` manually (protocol v1 gotchas)

JSON-RPC over stdin/stdout. Sequence:

1. `initialize` `{protocolVersion: 1, clientCapabilities: {promptCapabilities: {promptTypes: ["text"]}}}`
2. `notifications/initialized` (notification, no id)
3. `session/new` `{cwd: <abs path>, mcpServers: []}` → **capture `sessionId` from the result**; a fake one yields "session ... not found"
4. `session/prompt` `{sessionId, prompt: [...]}` — **`prompt` MUST be a LIST** of items (`[{"type":"text","text":...}]`); a single object gets `-32602 Invalid params`
5. Agent events arrive as `session/update` notifications (`update.type` = status/thinking_delta/agent_message/...); completion = the session/prompt result with `stopReason`

Notes:
- A bare prompt (no Open Design charter injected) may return `stopReason: "refusal"` — expected; the app always prepends its system charter.
- Startup is slow (~40-50s: 8 MCP servers register before the first model event) — don't misread as a hang.
- The `opendesign` MCP server (command = `Open Design.exe`) fails with CancelledError when the app is already running the ACP child — expected, harmless.
- Repro driver skeleton from the 2026-08-08 session: `C:\Users\YOUR_USERNAME\AppData\Local\hermes\cache\acp_repro.py` (handshake + forced search_files prompt).
