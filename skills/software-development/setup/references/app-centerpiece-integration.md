# App Centerpiece Integration

This project has an **Electron launcher** ("App Centerpiece") at `~/Documents/Playground/src/launcher-centerpiece/` that manages Start/Stop/Open for local developer tools. After setting up a new project, it should be registered here so the user can launch it from a single desktop bubble.

## Location

```
~/Documents/Playground/
├── src/launcher-centerpiece/
│   ├── apps.registry.json      ← Add new app entries here
│   ├── main.ts                 ← Electron main process (IPC handlers)
│   ├── renderer.ts             ← Card UI renderer
│   ├── process-manager.ts      ← PowerShell spawn/kill logic
│   ├── types.ts                ← AppRegistryEntry schema
│   └── renderer/
│       ├── index.html          ← Popup panel
│       ├── bubble.html         ← Minimised bubble
│       └── styles.css          ← Dark theme
├── package.json                ← Scripts: centerpiece:dev, centerpiece:start
└── tsconfig.json
```

The registry path is auto-resolved from `createAppPaths()` which goes up two directories from the compiled `dist/launcher-centerpiece/` to find the project root, then down to `src/launcher-centerpiece/apps.registry.json`. You can override with the `CENTERPIECE_REGISTRY_PATH` env var, but the default is correct for normal use.

## Registry Entry Schema (`apps.registry.json`)

```typescript
interface AppRegistryEntry {
  id: string;                    // unique kebab-case identifier
  name: string;                  // display name
  description: string;           // one-line description
  cwd: string;                   // working directory (Windows backslashes)
  launch: {
    shell: "powershell";         // only "powershell" supported
    script?: string;             // inline PowerShell script (preferred)
    command?: string;            // alternative: single executable path
    args?: string[];             // alternative: args for command
    env?: Record<string, string>;
    windowStyle: "normal" | "hidden";
    startupProbe: {
      mode: "processMatch";
      match: {
        field: "name" | "commandLine";
        value: string;           // substring match (case-insensitive, normalised)
      };
    };
  };
  openTarget:
    | { type: "url"; value: string }
    | { type: "launch" }               // same as Start button
    | { type: "directory"; value: string }
    | { type: "file"; value: string };
  stop: {
    mode: "processTreeMatch";
    match: {
      field: "name" | "commandLine";
      value: string;             // substring match for kill target
    };
  };
  notes?: string;
}
```

## Key Constraints

### Launch script (PowerShell)
- Always use `Set-Location` to set the working directory (not `cd`).
- For Python apps, call the venv Python directly: `& '.venv\\Scripts\\python.exe' -m module.name start`
- Set `$env:PYTHONUTF8='1'` and any other env vars before the command.
- The script must `Write-Output` the PID at the end — the process manager captures this.
- `windowStyle: "normal"` makes the console window visible; `"hidden"` for services.

### Startup probe
- Matches by `field` (`name` = process name, `commandLine` = full cmdline) with case-insensitive substring matching.
- Use `"commandLine"` with a unique part of the Python module path (e.g. `deeptutor_cli.main`).
- The probe runs every 3 seconds; stale "starting" entries time out after 10 seconds.

### Stop
- Uses `processTreeMatch` mode which runs `taskkill /PID /T /F` on all matching PIDs.
- **Match key must be same as (or superset of) startup probe** so the process manager can find what it launched.
- If the app leaves child processes (uvicorn, next dev), the `/T` flag cleans them all.

### Open target for web apps
- Always use `{ "type": "url", "value": "http://127.0.0.1:<port>" }` for web UIs.
- The Electron main process calls `shell.openExternal()` which opens the user's default browser.

## Multi-Service Apps (Python Backend + Node.js Frontend)

Some projects (like DeepTutor) have a Python backend and a Next.js/React frontend. The `deeptutor start` wrapper launches both, but in certain scenarios the interactive prompt blocks automated launch.

### Option A — Delegate to the `start` wrapper (preferred)

Let `deeptutor start` handle both backend and frontend. The registry script just calls the CLI:

```powershell
Set-Location 'C:\\Users\\Attila\\Documents\\Projects\\DeepTutor'
$env:PYTHONUTF8='1'
& '.venv2\\Scripts\\python.exe' -m deeptutor_cli.main start
```

The startup probe looks for any process with `deeptutor_cli.main` in its command line.

**Pitfall:** If default ports (8001/3782) are already occupied, `deeptutor start` shows an interactive prompt:
```
[1] Change ports (saved to data/user/settings/system.json)
[2] Stop the occupying process(es) and continue
Choice [1/2]:
```
This prompt hangs in headless/background sessions. Pre-create `data/user/settings/system.json` with custom ports to bypass it (see below).

### Option B — Start components separately

When the combined `start` command doesn't work (e.g. it hangs on Windows without TTY), start the backend via the registry and document the frontend separately:

```powershell
Set-Location 'C:\\Users\\Attila\\Documents\\Projects\\DeepTutor'
$env:PYTHONUTF8='1'
$env:DEEPTUTOR_HOME='C:\\Users\\Attila\\Documents\\Projects\\DeepTutor\\data'
& '.venv2\\Scripts\\python.exe' -m deeptutor_cli.main serve --host 127.0.0.1 --port 8005
```

The frontend must be started manually alongside:
```bash
cd ~/Documents/Projects/DeepTutor/web
export NEXT_PUBLIC_API_BASE="http://127.0.0.1:8005"
export BACKEND_PORT="8005"
node --max-old-space-size=4096 ./node_modules/next/dist/bin/next dev -p 3785
```

In the registry, set `openTarget` to the frontend URL (`http://127.0.0.1:3785`).

## Custom Port Configuration (avoiding conflicts)

DeepTutor reads port settings from `data/user/settings/system.json`. To avoid port conflicts with other projects, pre-create this file with custom ports:

```json
{
  "backend": {
    "host": "127.0.0.1",
    "port": 8005
  },
  "frontend": {
    "host": "127.0.0.1",
    "port": 3785
  }
}
```

This file is consumed by `deeptutor start` automatically — the port conflict prompt won't appear because the custom ports are unlikely to conflict with default 8001/3782.

If you change ports, also update the registry's `openTarget` URL to match.

## Build & Launch

After editing the registry, rebuild and launch:

```bash
cd ~/Documents/Playground
npm run build                           # tsc compile
npm run centerpiece:dev                 # build + electron launch
# or for a faster restart (build already done):
npx electron dist/launcher-centerpiece/main.js
```

The app opens as a dark popup panel with Start/Stop/Open buttons per registered app. It also creates a system tray icon and a small desktop "bubble" for minimise/restore.

## Port Conflict Detection

Windows leaves orphan processes holding ports. Before starting a new instance:

```bash
netstat -ano | grep ":PORT " | grep LISTEN
taskkill //F //PID <pid>      # note: //F not /F in git-bash
```

Common DeepTutor ports: backend `8001`/`8005`, frontend `3782`/`3785`.

## Existing Apps

As of July 2026, the registry contains:

| App | ID | Type | Port/Mode |
|-----|----|------|-----------|
| Crypto Watcher | `crypto-radar` | Electron app | — |
| LDS Clerk Bot | `lds-clerk-bot` | npm dev server | — |
| Open WebUI | `open-webui` | Python executable | :8080 |
| LLMFit | `llmfit` | Native binary | — |
| FreeDev Tools | `free-dev-tools` | TSX dev server | — |
| OpenCharts | `opencharts` | Vite React app | :5173 |
| AutoGPT | `autogpt` | Python FastAPI (serve mode) | :8000 |
| DeepTutor | `deeptutor` | Python + Next.js | backend :8005, UI :3785 |
| TradingAgents | `tradingagents` | pip-installed Python CLI | CLI (interactive) |

## Python App Launch Patterns

### Poetry-managed apps (AutoGPT)

The Poetry venv path is resolved via `poetry env info --path` at launch time. The Hermes venv's Python may be on `PATH` and conflict — always call the Poetry venv Python directly:

```powershell
Set-Location 'C:\\Users\\Attila\\Documents\\Projects\\AutoGPT\\classic'
$env:PYTHONUTF8='1'
& (poetry env info --path)\\Scripts\\python.exe -m autogpt.app.cli serve
& $(poetry env info --path)\\Scripts\\python.exe -m autogpt.app.cli serve

**Pitfall:** `poetry run autogpt serve` inherits `$env:PYTHONPATH` from the Hermes process, which can cause import conflicts (`ModuleNotFoundError` for `httpx._transports`, wrong `openai` version, etc.). Calling the venv Python directly avoids this.  

**PowerShell syntax:** use `$(cmd)` not `(cmd)` — parentheses alone is bash syntax and silently fails in PowerShell (the command runs but returns the wrong object).

### Pip-installed CLI apps (TradingAgents)

Apps installed into the Hermes venv (e.g. via `pip install -e .` in the Hermes env) can use `python -m <module>` directly without venv path resolution:

```powershell
Set-Location 'C:\\Users\\Attila\\Documents\\Projects\\TradingAgents'
$env:PYTHONUTF8='1'
python -m cli.main
```

Open target for CLI apps: `{ "type": "launch" }` (re-launches the terminal). No URL, no directory — the window IS the app.

### Startup probe for Python apps

- Poetry venv: probe on `commandLine` with the Python module name (e.g. `autogpt.app.cli serve`)
- Pip-installed: probe on `commandLine` with the module name (e.g. `cli.main`)
- The module name string must be unique enough to match the launched command and nothing else

### `.env` for CLI Python apps

Some apps (TradingAgents) read `.env` from their project root. Follow the app's `.env.example` structure. For TradingAgents specifically, `TRADINGAGENTS_*` env vars override the default config and also skip CLI interactive selections — useful for unattended runs.
