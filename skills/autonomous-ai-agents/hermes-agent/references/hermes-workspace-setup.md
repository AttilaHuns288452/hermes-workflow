# Hermes Workspace Setup

**Hermes Workspace** (`ghcr.io/outsourc-e/hermes-workspace`) is a companion web UI for Hermes Agent — chat, sessions, memory, skills, MCP, terminal, dashboard, and multi-agent operations in one browser interface.

## Architecture

Three services must be running for full functionality:

| Service | Port | Purpose |
|---------|------|---------|
| **Gateway** (API Server) | `:8642` | Chat, streaming, models, jobs — Hermes Agent core |
| **Dashboard** | `:9119` | Sessions, skills, config, MCP, memories — admin APIs |
| **Workspace UI** | `:3000` | The browser frontend |

```
┌───────────────┐         :8642 gateway          ┌────────────────┐
│   Workspace    │ ─────────────────────▶ │  Hermes Agent  │
│   :3000 (UI)   │ ◀───────────────────── │  CLI / brain   │
└───────────────┘         :9119 dashboard        └────────────────┘
```

## Prerequisites

- Hermes Agent installed (via Nous official installer)
- Node.js 22+ (`node --version`)
- pnpm (`pnpm --version`)

## Step-by-Step Setup

### 1. Clone the Repo

```bash
git clone https://github.com/outsourc-e/hermes-workspace.git
cd hermes-workspace
pnpm install
cp .env.example .env
```

### 2. Configure the Gateway API Server

Hermes Workspace needs the gateway's HTTP API server to be enabled. Add these to **the gateway's `.env`** (NOT the workspace `.env`):

```bash
# ~/AppData/Local/hermes/.env  (Windows)
# or ~/.hermes/.env            (Linux/macOS)
API_SERVER_ENABLED=true
API_SERVER_KEY=<your-secret-key>
```

- `API_SERVER_ENABLED=true` exposes the REST API on `:8642`
- `API_SERVER_KEY` is an arbitrary secret; set it to anything secure
- Without `API_SERVER_KEY`, the API server starts with no authentication — still functional but unsecured

### 3. Configure the Workspace `.env`

Edit `~/hermes-workspace/.env`:

```env
# Required: point at the gateway
HERMES_API_URL=http://127.0.0.1:8642

# Recommended: unlocks sessions, skills, config, MCP, jobs
HERMES_DASHBOARD_URL=http://127.0.0.1:9119

# Must match API_SERVER_KEY if set on the gateway
HERMES_API_TOKEN=<same-secret-key>
```

- `HERMES_API_TOKEN` must match `API_SERVER_KEY` — if the gateway has no key, leave this unset/uncommented.

### 4. Restart the Gateway

```bash
# From a separate terminal (NOT inside the running gateway process):
hermes gateway run --replace
```

**Pitfall:** `hermes gateway restart` blocks when called from inside the gateway process itself — SIGTERM propagates to the caller. Use `--replace` from a background terminal or a separate shell:

```bash
# From inside Hermes (e.g. via terminal tool with background=true):
terminal(command="hermes gateway run --replace", background=true)
```

### 5. Start the Dashboard

```bash
hermes dashboard
```

Runs on `http://127.0.0.1:9119`. Provides config, sessions, skills, and jobs APIs that the workspace reads.

### 6. Start the Workspace UI

```bash
cd ~/hermes-workspace
pnpm dev
```

Opens `http://localhost:3000`.

### 7. One-command startup (all three)

If installed via the one-liner installer:

```bash
# From hermes-workspace repo root:
pnpm start:all
```

This runs `concurrently "hermes gateway run" "pnpm dev"` — note that dashboard still needs a separate terminal.

## Verification

Before opening the UI, verify all three services:

```bash
# 1. Gateway health
curl http://127.0.0.1:8642/health
# → {"status": "ok", "platform": "hermes-agent"}

# 2. Dashboard status
curl http://127.0.0.1:9119/api/status
# → {"version": "0.17.0", "gateway_running": true, ...}

# 3. Workspace UI
curl -o /dev/null -w "%{http_code}" http://127.0.0.1:3000
# → 200
```

## Debugging

### Gateway not listening on :8642

```bash
# Check gateway logs for "Connecting to api_server..."
tail -20 ~/AppData/Local/hermes/logs/gateway.log
```

Expected log line when API server is active:
```
INFO gateway.platforms.api_server: [Api_Server] API server listening on http://127.0.0.1:8642
```

If missing:
1. Verify `API_SERVER_ENABLED=true` is in **the gateway's** `.env` (not the workspace's)
2. Restart with `hermes gateway run --replace`
3. Check `netstat -ano | grep 8642` (Linux) / `netstat -ano | findstr :8642` (Windows)

### "Another gateway instance is already running"

The PID file from a previous gateway instance still exists but the process is dead. Use:

```bash
hermes gateway run --replace
```

This auto-replaces the stale PID registration.

### Dashboard says gateway running but :8642 unreachable

The dashboard shows the gateway process status — not the API server's health. The gateway may be running without `API_SERVER_ENABLED=true`. Check the gateway `.env` and restart.

### Workspace shows "portable mode" / extended APIs missing

The dashboard at `:9119` is not running. Start `hermes dashboard` and refresh the workspace UI.

### Logs location

| Log | Path (Windows) | Path (Linux/macOS) |
|-----|---------------|-------------------|
| Gateway | `~/AppData/Local/hermes/logs/gateway.log` | `~/.hermes/logs/gateway.log` |
| Gateway exit diag | `~/AppData/Local/hermes/logs/gateway-exit-diag.log` | `~/.hermes/logs/gateway-exit-diag.log` |
| Dashboard | `~/AppData/Local/hermes/logs/dashboard.log` | `~/.hermes/logs/dashboard.log` |

## Windows-Specific Notes

- **Two `.env` files matter.** Gateway reads `~/AppData/Local/hermes/.env`; Workspace reads `~/hermes-workspace/.env`. Keep `API_SERVER_KEY` / `HERMES_API_TOKEN` in sync.
- **`hermes gateway run --replace`** works from a background terminal tool call.
- **Gateway paths on Windows:** Gateway `.env` is at `~/AppData/Local/hermes/.env`, NOT `~/.hermes/.env`.
- **Port checking:** Use `netstat -ano | findstr :8642` — `lsof` is not available in Git Bash.
