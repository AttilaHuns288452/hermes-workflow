# OpenDesign MCP — proxy/daemon diagnosis (verified 2026-08-02)

## Architecture

- `Open Design.exe` (Electron) is launched with `ELECTRON_RUN_AS_NODE=1` and runs
  `daemon-cli.mjs mcp` — a stdio MCP server that is a **thin proxy**.
- Real tools live in the app's internal daemon at `http://127.0.0.1:7456`
  (default port; override with `OD_PORT` env).
- The proxy answers the MCP handshake itself: `initialize` + `list_tools`
  succeed **even when the daemon is down** (20 tools listed). Every real tool
  call then returns:
  `cannot reach the Open Design daemon at http://127.0.0.1:7456. Is it running? Start it with 'pnpm tools-dev'.`
- `hermes mcp test opendesign` times out at 40s for the same reason — it
  exercises a real call, not just the handshake.
- Tools exposed (protocol level): `list_projects`, `get_active_context`,
  `get_artifact`, `get_project`, `get_file`, `search_files`, `list_files`,
  `create_artifact`, `write_file`, `delete_file`, `delete_project`,
  `create_project`, `list_skills`, `list_plugins`, `start_run`, …

## Environment facts

- Install: `C:\Users\YOUR_USERNAME\AppData\Local\Programs\Open Design release-stable-win\`
- Daemon entry (current layout): `resources/app/prebundled/daemon/daemon-cli.mjs`
  (+ `daemon-sidecar.mjs`, `chunks/`). The OLD path
  `resources/app/node_modules/@open-design/daemon/dist/cli.js` no longer exists —
  the app was updated; stale logs still reference it.
- Data dir: `%APPDATA%\Open Design\namespaces\release-stable-win\data\`
  (`app.sqlite`, `app-config.json` — the latter contains `agentModels.hermes`,
  proving the app ships Hermes integration).
- Env keys (grepped from `prebundled/daemon/chunks/`):
  `OD_BIND_HOST`, `OD_DAEMON_CLI_PATH`, `OD_JSON_IPC_TRACE`, `OD_PORT`,
  `OD_SIDECAR_BASE`, `OD_SIDECAR_IPC_BASE`, `OD_SIDECAR_IPC_PATH`,
  `OD_SIDECAR_NAMESPACE`, `OD_SIDECAR_SOURCE`, `OD_TOOLS_DEV_PARENT_PID`,
  `OD_WEB_DIST_DIR`, `OD_WEB_PORT`, `OD_WEB_TSCONFIG_PATH`.
- `debug.log` in the install dir can show stale failures
  (`Failed to initialize Node.js … RangeError: Failed to allocate memory`) —
  check timestamps before trusting it; it referenced the old daemon path.

## Diagnostic recipe

1. App running? `tasklist | grep -i "Open Design"` (9 processes = normal Electron).
2. Sidecar pipe up? `cmd //c "dir \\.\pipe" | findstr open-design`
3. Daemon listening? `netstat -ano | grep 7456`
   → was **empty even with the GUI running**: launching the app does NOT start the daemon.
4. Direct probe — separates protocol health from backend health:

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

EXE = r"C:\Users\YOUR_USERNAME\AppData\Local\Programs\Open Design release-stable-win\Open Design.exe"
CLI = r"C:\Users\YOUR_USERNAME\AppData\Local\Programs\Open Design release-stable-win\resources\app\prebundled\daemon\daemon-cli.mjs"
env = {"ELECTRON_RUN_AS_NODE": "1",
       "OD_DATA_DIR": r"C:\Users\YOUR_USERNAME\AppData\Roaming\Open Design\namespaces\release-stable-win\data",
       "OD_SIDECAR_NAMESPACE": "release-stable-win",
       "OD_BIN": CLI}

async def main():
    params = StdioServerParameters(command=EXE, args=[CLI, "mcp"], env=env)
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()                      # 1) protocol — succeeds
            tools = await s.list_tools()              # 2) protocol — succeeds
            print("tools:", [t.name for t in tools.tools][:15])
            r = await s.call_tool("list_projects", {})  # 3) backend — names the missing daemon
            print(r.content)

asyncio.run(main())
```

## Conclusion

The Hermes config is correct; the MCP bridge is healthy at protocol level. The
blocker is the app-side daemon service (dev-mode, started with `pnpm tools-dev`
per its own error). Fix lives in the app (enable agent/tools service) or by
running that dev service — not in Hermes config.

## Pitfalls

- Don't trust `hermes mcp test` pass/fail alone on proxy servers: it can time
  out while the protocol is fine (daemon down), and it can pass while tool
  calls still fail (handshake-only servers).
- Read tool-call error text before concluding "MCP broken" — it names the
  missing backend and how to start it.
- The GUI window opening on the user's screen ≠ daemon up.
