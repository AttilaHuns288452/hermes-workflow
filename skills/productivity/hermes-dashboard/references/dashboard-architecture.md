# Hermes Dashboard Architecture

## How `hermes dashboard` works internally

Source: `hermes_cli/subcommands/dashboard.py` and `web_server.start_server`

```
hermes dashboard --port N
  └── start_server(port=N)
        ├── Serves SPA from web dist (apps/desktop/release/.../dist/)
        ├── Starts gateway (JSON-RPC + WebSocket)
        ├── Proxies /api/* to gateway API server
        └── WebSocket /api/ws → gateway for real-time chat
```

**Key insight:** `dashboard` and `serve` share the same `start_server` handler.
The only difference is `headless_backend=True` for `serve` (skips SPA build).

## Port allocation

| Component | Port | Notes |
|-----------|------|-------|
| Dashboard (SPA + API proxy) | N (user-specified, default 9119) | Single entry point |
| Gateway API server | 8642 (internal) | Proxied through dashboard |
| Gateway WebSocket | 8642 (internal) | `/api/ws` endpoint |

## SPA connection flow

1. Browser loads SPA from `http://127.0.0.1:N/`
2. SPA JavaScript initializes
3. SPA connects to `ws://127.0.0.1:N/api/ws` (or detects `window.hermesDesktop` in Electron)
4. WebSocket handshake with gateway
5. Real-time chat/sessions/skills via WebSocket

## Browser vs Electron

| Mode | IPC bridge | WebSocket | Notes |
|------|-----------|-----------|-------|
| Electron | ✅ `window.hermesDesktop` | Also available | Full features |
| Browser | ❌ Missing | ✅ Primary transport | SPA works, just uses WebSocket |

The "Desktop IPC bridge is unavailable" error in browser is a JavaScript-level
warning from the SPA code. It falls back to WebSocket automatically. The error
is cosmetic — the dashboard should still function.

## Verification script

```bash
#!/bin/bash
PORT=${1:-9119}
echo "=== Dashboard on port $PORT ==="

# SPA check
SPA=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:$PORT/)
echo "SPA: HTTP $SPA"

# API check
API=$(curl -s http://127.0.0.1:$PORT/api/status 2>/dev/null)
if echo "$API" | python -c "import sys,json; d=json.load(sys.stdin); assert d['gateway_running']" 2>/dev/null; then
    echo "Gateway: RUNNING"
    echo "$API" | python -c "import sys,json; d=json.load(sys.stdin); print(f'  Sessions: {d[\"active_sessions\"]} | Auth: {d[\"auth_required\"]} | Profiles: {len(d[\"profiles\"])}')"
else
    echo "Gateway: NOT RUNNING"
fi

# WebSocket check
WS=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:$PORT/api/ws)
echo "WebSocket: HTTP $WS (401 = auth handshake needed, 200 = open)"
```
