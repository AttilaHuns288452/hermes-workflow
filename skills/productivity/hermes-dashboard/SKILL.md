---
name: hermes-dashboard
description: >-
  Serve and interact with the Hermes Agent Dashboard — both the built-in `hermes dashboard` (port 9119,
  sessions/skills/config/cron/jobs) and the static ecosystem visualization (port 8080,
  project graph, model tiers, API list, ECC agents). Primary: the official 9119 dashboard.
---

# Hermes Dashboard

## Overview

There are **two** Hermes dashboards — the **official Hermes Agent Dashboard** (port 9119, built-in) and the **static ecosystem dashboard** (port 8080, community-skills page):

| Dashboard | Command / URL | Purpose |
|-----------|--------------|---------|
| 🏛️ **Official Dashboard** | `http://127.0.0.1:9119` via `hermes dashboard` | Session browser, skills manager, config editor, cron jobs, auth, health |
| 🕸️ **Static Ecosystem Viz** | `http://127.0.0.1:8080` via Python | Ecosystem graph, project grid, model tiers, API list, ECC agents |

When prompted for "dashboard" / "ecosystem" / "show me everything" — **prefer the official Hermes dashboard (9119)** as the primary answer. It is the authoritative web UI.

### Official Dashboard (9119 — Built-in `hermes dashboard`)

The official Hermes Agent web dashboard provides:
- **Sessions** — browse, search, and inspect all past conversations (FTS5-backed)
- **Skills** — browse and manage installed skills
- **Config** — view and edit `config.yaml` live
- **Cron Jobs** — create, edit, pause, remove scheduled tasks
- **Auth / Credentials** — manage provider credentials
- **Status & Health** — component status at a glance

Launch:
```bash
hermes dashboard --port 9119 --host 127.0.0.1 --no-open
```

The dashboard URL is auto-detected at session start: the `decide` skill, `/session-memory`, and ecosystem links all resolve to `HERMES_DASHBOARD_URL` (default `http://127.0.0.1:9119`).

Configuration via `.env`:
```bash
HERMES_DASHBOARD_URL=http://127.0.0.1:9119
```

### Static Ecosystem Dashboard (8080 — hermes-dashboard/index.html)

The static dashboard at `~/Documents/Projects/hermes-dashboard/index.html` (755 lines) visualizes the Hermes Agent ecosystem with:

- **16 projects** with git/obsidian/graph status indicators
- **Graphify + CodeGraph node map** (vis-network force-directed graph)
- **Free AI model ecosystem** across 4 layers (OpenCode, Freebuff, FreeLLMAPI, OpenRouter)
- **API Mega List Explorer** (26,005 APIs / 18 categories)
- **MCP Servers wired** (6 total)
- **ECC Agents** (64 total, 57 free-compatible)
- **Skills by category** breakdown
- **Observability & memory** stats
- **Power stats** (token savings, obsidian notes, vault KG nodes)

No backend server required — it's fully client-side with hardcoded static data.

## Serving

### Official Dashboard (9119 — Priority)
```bash
hermes dashboard --port 9119 --host 127.0.0.1 --no-open
```
Opens at `http://127.0.0.1:9119`. This is the primary dashboard — always try this first when asked for the dashboard.

Check if already running:
```bash
hermes dashboard --status
```

Stop stale instances:
```bash
hermes dashboard --stop
```

### Static Ecosystem Dashboard (8080 — Fallback)
```bash
cd ~/Documents/Projects/hermes-dashboard
python -m http.server 8080 --bind 127.0.0.1
# Opens at http://localhost:8080
```

### Background (recommended for persistent static access)
```bash
terminal(background=true, command="cd ~/Documents/Projects/hermes-dashboard && python -m http.server 8080 --bind 127.0.0.1")
```

### Direct Open (no server)
```bash
start ~/Documents/Projects/hermes-dashboard/index.html
```

## Sections

| Section | Content | Source |
|---------|---------|--------|
| 🕸️ **Graph Node Map** | Force-directed graph of projects, MCP servers, APIs, free models, ECC agents, skills | vis-network, hardcoded DATA object |
| 📁 **Projects** | 16 projects with git/obsidian/graph badges | STATIC: data/js embedded in HTML |
| 🤖 **Free Model Ecosystem** | Models across layers with availability counts | STATIC: tier/count data embedded |
| 🔌 **API Mega List Explorer** | 26K APIs by category with search filter | STATIC: category/count data |
| 🔗 **MCP Servers** | 6 wired servers | STATIC |
| 🧠 **ECC Agents** | 64 total, free/paid split | STATIC |
| 📦 **Skills by Category** | Category breakdown with counts | STATIC |
| 👁️ **Observability** | Session DB files, memory, config | STATIC |
| ⚡ **Power Stats** | Token savings, notes, graph stats | STATIC |

## Data Freshness

⚠️ **Dashboard is purely static** — all data is hardcoded in the HTML's `DATA` JavaScript object. It does NOT auto-sync with the live file system or any backend.

To update stats, edit the `DATA` constant in `index.html` directly:
```javascript
const DATA = {
  projects: [...],        // 16 project entries
  graphify: {...},        // node/community counts
  codegraph: {...},       // file/node/edge counts
  obsidian: {...},        // note/vault graph stats
  models: [...],          // 5+ model tier entries
  apis: [...],            // 18 category entries
  mcps: [...],            // 6 server entries
  ecc: {...},             // agent counts + top agents
  skills: {...},          // category:count pairs
};
```

## Troubleshooting

### Desktop GUI vs CLI Dashboard

There are **two ways** to serve the Hermes web UI at port 9119:

| Mode | When | Command |
|------|------|---------|
| **CLI (preferred)** | Agent-invoked, headless server | `hermes dashboard --port 9119 --no-open --skip-build` |
| **Desktop GUI app** | User-launched Electron app | Launched via Start menu / desktop shortcut |

**The Desktop GUI app is NOT the same as `hermes dashboard`.** The desktop app spawns a child Hermes backend process internally; if that backend crashes (e.g. OpenRouter 402), the entire UI shows "Desktop boot failed: Desktop IPC bridge is unavailable" and the dashboard never loads. The CLI dashboard is a standalone server that does NOT need IPC and is far more reliable.

### Standalone HTML Dashboard for Electron SPA Features

When the Electron SPA cannot boot (even after fixing the Desktop IPC bridge), specific backend features can still be accessed via a **standalone HTML page** that talks to the backend API directly.

**When to use this approach:**
- The Electron SPA's boot failure is recurring despite fixes
- Only specific features are needed (e.g. session memory, settings, stats)
- The backend API already exists on a separate port (e.g. FreeLLM API on 3001)

**How it works:**
1. Create a self-contained `.html` file in the dashboard's `dist/` directory
2. The page uses `fetch()` calls directly to the backend API (no Electron dependency)
3. Includes inline CSS for a dark-themed UI matching the Hermes aesthetic
4. Handles auth (login) transparently
5. Served as a static file from the dashboard's HTTP server

**Template location:** The file lives alongside the SPA's `index.html` in the dist folder:
```
<web-dist>/session-memory.html
```
📎 See `references/standalone-dashboard-electron-spa.md` for the full implementation reference, including CORS configuration, auth patterns, tab data loading, and debounced search.

**Key implementation details:**
- Login via `POST /api/auth/login` with stored credentials
- Store token in a module-level variable (not localStorage)
- Fetch session data from `GET /api/session-memory/sessions`
- Search with debounce (300ms) to avoid API spam
- Tab switching loads data on-demand via explicit `loadMemory()` / `loadStats()` calls

**CORS between dashboard (9119) and backend API (3001):**
```
Browsers treat http://localhost:<port> and http://127.0.0.1:<port>
as different origins. When the HTML page is served from port 9119
and fetches from port 3001, BOTH origins must be in the backend's
CORS allowlist:
  DASHBOARD_ORIGINS=http://localhost:9119,http://127.0.0.1:9119
```
Without this, the fetch login call fails silently with a CORS error and the page shows "Error: Login failed".

**Limitations of standalone HTML:**
- Static — no live WebSocket updates
- Requires manual refresh for new data
- No drag-and-drop, file uploads, or native features
- Must keep credentials in the page source (ok for local/dev use)

### Dashboard shows "Desktop boot failed" or "IPC bridge is unavailable"

**Symptoms**: Port 9119 responds with a blank error screen, desktop.log shows "Hermes backend exited (1)" then "reset requested by renderer" in a loop.

**Root cause**: The desktop Electron app launches a Hermes backend process that makes an API call during boot. If the default model provider returns HTTP 402 (insufficient credits), the backend exits immediately with code 1, before the IPC handshake completes. The desktop renderer retries indefinitely, failing every time.

Alternatively, when running `hermes dashboard` CLI mode, the SPA shows "Desktop IPC bridge is unavailable" because it expects `window.hermesDesktop` (the Electron IPC bridge) which doesn't exist in a browser context. This is the *same* error screen as the backend crash but has a different root cause.

**Detect which cause:**
```
Check browser console:
├── "Desktop IPC bridge is unavailable" + no network errors
│   → SPA is missing the Electron IPC bridge (CLI mode)
├── "Desktop boot failed" + network tab shows failed API calls
│   → Backend process exited (e.g. OpenRouter 402)
├── Check server logs for process exit code
└── If port 9119 responds with HTML but SPA shows boot error:
    curl -s http://127.0.0.1:9119 | grep -o '<title>[^<]*</title>'
    → "Hermes" = SPA loaded but IPC bridge missing
```

**Fix sequence**:
1. Kill the broken desktop process:
   ```bash
   # On Windows (git-bash/MSYS):
   netstat -ano | grep 9119                # find PID
   taskkill //F //PID <PID>                # kill it
   # On Linux/macOS:
   kill $(lsof -ti:9119)
   ```
2. Switch the default model to a working free provider:
   ```bash
   hermes config set model.default deepseek-v4-flash-free
   hermes config set model.provider opencode-zen
   hermes config set model.base_url https://opencode.ai/zen/v1
   ```
3. Fix any YAML null-value warnings (caused by `context_file_max_chars: null` or `max_concurrent_sessions: null` in config.yaml):
   ```bash
   hermes config set context_file_max_chars 100000
   hermes config set max_concurrent_sessions 1
   ```
   **Never edit config.yaml directly** — the agent is blocked from writing it; always use `hermes config set`.
4. Start the CLI dashboard instead (does not need IPC):
   ```bash
   hermes dashboard --port 9119 --no-open --skip-build
   ```

**Verification**: The dashboard should serve the Hermes SPA HTML when you curl `http://127.0.0.1:9119` and return a `<title>Hermes</title>` page.

### Dashboard is running but shows "Gateway offline"

The CLI dashboard connects to the gateway API (typically on port 8642). If the gateway isn't running or the API key used by the dashboard is wrong, the status reads offline.

Check gateway status:
```bash
hermes gateway status
```

If the gateway is running but the dashboard still shows offline, restart it:
```bash
hermes gateway restart
```

### Port 9119 already in use

```bash
# Check what's listening
hermes dashboard --status

# Kill stale instances
hermes dashboard --stop

# Or kill manually (Windows git-bash)
netstat -ano | grep 9119
taskkill //F //PID <PID>
```

Then retry:
```bash
hermes dashboard --port 9119 --no-open --skip-build
```

### Config changes not reflected in dashboard

The 9119 dashboard reads from Hermes state DB and config.yaml at page load. After changing config via `hermes config set`, refresh the dashboard page (Ctrl+R / Cmd+R). No need to restart the dashboard server — it serves the latest state on each request.

### Companion API: FreeLLMAPI Session Memory

FreeLLMAPI (`http://localhost:3001`) has its own **session-memory API** at `/api/session-memory` that provides a richer browsing experience for Hermes conversation history:

| Endpoint | Description |
|----------|-------------|
| `GET /api/session-memory` | List all memory files (MEMORY.md, USER.md, per-profile) |
| `GET /api/session-memory/stats` | Session statistics (session count, message count, token counts, top models) |
| `GET /api/session-memory/sessions` | Paginated session list with search/filter by source |
| `GET /api/session-memory/sessions/:id` | Session detail + message previews (capped at 2K chars each) |
| `GET /api/session-memory/file?name=MEMORY.md` | Read a specific memory file (path-traversal guarded) |

**Auth**: All session-memory endpoints require a dashboard session token (`requireAuth` middleware). Use the same login as the FreeLLMAPI dashboard.

**Access**:
```bash
# Login
TOKEN=$(curl -s -X POST http://localhost:3001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@freellmapi.local","password":"admin12345"}' \
  | python -c "import sys,json; print(json.load(sys.stdin)['token'])")

# Query session memory
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:3001/api/session-memory/stats
```

**The two dashboards complement each other**: Hermes Dashboard (9119) provides live chat, skills management, and config editing. FreeLLMAPI session-memory (3001) provides searchable session history with aggregate stats, memory files, and per-profile support. Use both when the user asks for comprehensive session history views.

**Rebuilding after edits**: If you edit `server/src/routes/session-memory.ts`, you must rebuild:
```bash
cd ~/Documents/Projects/freellmapi && npm run build:server
```
Then restart the server (kill stale node processes on port 3001 first if EADDRINUSE).

**Verify the compiled output** after every rebuild — the patch tool can corrupt `finally` blocks:
```bash
# 1. Check for garbled code (duplicated/corrupted finally blocks)
grep -c "db if (db if" server/dist/routes/session-memory.js
# Expected: 0 (exit code 1 = no matches)

# 2. Count db.close calls — should be exactly 3 (one per route, inside finally)
grep -n "db.close" server/dist/routes/session-memory.js

# 3. Verify each db.close is inside a finally block with guard
grep -B5 -A2 "db.close" server/dist/routes/session-memory.js
```

**Known bug — use-after-close in stats endpoint**: The `/stats` route previously called `db.close()` *before* the `totalCost` query, then called it again in `finally`. The fix is to move all queries before `db.close()` and keep only the `finally`-block close. After editing, confirm no `db.close()` appears before `res.json()` in the compiled output.

**Corrupted `finally` block pattern**: If the source file shows `if (db if (db if (db.open) db.close();...` (duplicated/repeated content), this is a write corruption. The corruption always occurs as a repeating pattern of the guard clause. Fix by replacing the entire corrupted `finally` block with:
```typescript
  } finally {
    if (db?.open) db.close();
  }
```
Three routes have `finally` blocks: `/sessions`, `/sessions/:id`, and `/stats` — all three must be checked.

### Port Conflict Recovery

When restarting services, ports 3001 and 9119 can hold stale processes:

```bash
# Kill stale processes on ports
python -c "
import subprocess, os
for port in [3001, 9119]:
    result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
    for line in result.stdout.splitlines():
        if str(port) in line and ('LISTENING' in line or 'ESTABLISHED' in line):
            pid = line.strip().split()[-1]
            os.system(f'taskkill /F /PID {pid}')
            print(f'Killed PID {pid} on port {port}')
"

# Verify ports are free
python -c "
import socket
for port in [9119, 3001]:
    s = socket.socket()
    s.settimeout(2)
    print(f'Port {port}: {\"OPEN\" if s.connect_ex((\"127.0.0.1\", port)) == 0 else \"FREE\"}')
    s.close()
"
```

## Integration with decide skill

The `/decide` skill routes ecosystem/dashboard queries here:
- **Trigger phrases**: "show me everything", "dashboard", "ecosystem stats", "what projects exist", "graph stats", "project graph", "model ecosystem"
- **Action**: First check if the official dashboard is running on port 9119 (`hermes dashboard --status`). If yes → tell the user to open `http://127.0.0.1:9119`. If no → start it with `hermes dashboard --port 9119 --host 127.0.0.1 --no-open`.

## Pitfalls

- **Two ways to serve 9119 exist — and they differ**: The `hermes dashboard` CLI command and the Electron Desktop GUI app both bind port 9119 but work completely differently. The CLI dashboard is a standalone web server and the preferred way to serve the dashboard. The Desktop app spawns a child Hermes backend via IPC and crashes if that backend can't boot (e.g. OpenRouter 402). When fixing a broken dashboard, kill the desktop process and use `hermes dashboard --skip-build` instead.
- **Two dashboards exist**: Don't confuse the official dashboard (9119) with the static ecosystem visualization (8080). Always prefer 9119.
- **Official dashboard reads state, not live stream**: The 9119 dashboard reads from Hermes state DB on page load — it does NOT auto-refresh. Refresh the page (Ctrl+R) to see latest data.
- **Config edits must use `hermes config set`**: The agent cannot write config.yaml directly (security restriction). Always use `hermes config set <key> <value>` to fix config. This also avoids YAML parser issues with null values like `context_file_max_chars: null`.
- **Static dashboard is purely static** — don't promise live data. Clarify it reflects a snapshot.
- **File is dead unless served**: The static HTML file needs an HTTP server — opening directly in a browser (`file://`) will not load vis-network.js from CDN correctly.
- **Python HTTP server** is single-threaded and slow on concurrent requests. For reliability, use Node.js `npx serve` or a proper web server.
- **Graph force simulation** runs in browser and may be slow on low-end machines.
