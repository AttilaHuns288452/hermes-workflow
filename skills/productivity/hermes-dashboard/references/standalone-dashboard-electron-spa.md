# Standalone HTML Dashboard for Electron SPAs

## Problem

An Electron SPA shows "Desktop boot failed: Desktop IPC bridge is unavailable" when served from a CLI web server (e.g. `hermes dashboard`). The SPA was built for Electron and requires `window.hermesDesktop` which doesn't exist in a browser.

## Solution: Standalone HTML Page

Create a self-contained HTML file in the dashboard's web dist directory that talks to the backend API directly via `fetch()`.

## Architecture

```
Browser ──HTTP──→ hermes dashboard (port 9119) ──fetch──→ FreeLLM API (port 3001)
                   serves session-memory.html           provides REST endpoints
```

## Key Implementation Patterns

### 1. CORS: Both localhost and 127.0.0.1

When the HTML page is served from `http://127.0.0.1:9119` and fetches from `http://127.0.0.1:3001`:

```bash
# FreeLLM API needs BOTH origins:
DASHBOARD_ORIGINS=http://localhost:9119,http://127.0.0.1:9119
```

The browser treats `localhost` and `127.0.0.1` as different origins. If the user navigates to `http://127.0.0.1:9119/`, the `Origin` header is `http://127.0.0.1:9119`, not `http://localhost:9119`.

### 2. Auth: Transparent login on first API call

```js
let token = null;

async function login() {
  const r = await fetch(API_URL + '/api/auth/login', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({email: 'admin@...', password: '...'})
  });
  const data = await r.json();
  token = data.token;
}

async function api(path) {
  if (!token && !(await login())) throw new Error('Login failed');
  const r = await fetch(API_URL + path, {
    headers: {'Authorization': 'Bearer ' + token}
  });
  if (!r.ok) throw new Error(r.status + ': ' + await r.text());
  return r.json();
}
```

### 3. Tab switching with data loading

The tab click handler must explicitly call the data-loading function:

```js
document.querySelectorAll('.nav button').forEach(btn => {
  btn.addEventListener('click', () => {
    // ... tab visibility logic ...
    if (btn.dataset.tab === 'memory') loadMemory();
    else if (btn.dataset.tab === 'stats') loadStats();
  });
});
```

Without this, clicking a tab switches the view but doesn't trigger data loading.

### 4. Debounced search

```js
let searchTimer;
document.getElementById('search').addEventListener('input', () => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => loadSessions(input.value), 300);
});
```

## When to Use vs Fix the SPA

| Approach | When | Trade-off |
|----------|------|-----------|
| **Mock IPC bridge** (inject `window.hermesDesktop` in HTML) | SPA only needs bypass boot check | Deeper WS gateway deps may still fail |
| **Standalone HTML page** | Need specific backend features | Static, no live updates, credentials in source |
| **Fix Electron SPA** | Full app needed | Requires modifying source or running actual Electron |

## Known Working Endpoints (FreeLLM API)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/auth/login` | POST | Auth (returns token) |
| `/api/session-memory/sessions` | GET | List sessions (optional `?search=` param) |
| `/api/session-memory/sessions/:id` | GET | Session detail |
| `/api/session-memory/stats` | GET | Aggregate stats |
| `/api/session-memory/memory` | GET | Memory files (may 404 if not implemented) |
