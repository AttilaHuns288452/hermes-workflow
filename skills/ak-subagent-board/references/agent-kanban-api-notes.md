# agent-kanban API & auth notes (verified 2026-07-31, CLI v1.15.0, hosted agent-kanban.dev)

## Auth model (three layers)

1. **Machine key** (`api-key` in `~/.config/agent-kanban/config.json`) — authenticates
   machine endpoints: `POST /api/machines`, `POST /api/agents/{id}/sessions`,
   `GET /api/agents` (worked early, then server revoked it mid-session → 401
   everywhere; machine keys are server-issued, rotation is not client-controllable).
2. **Agent session JWT** — per-agent Ed25519-signed short-lived JWT
   (`alg: EdDSA`, `typ: agent+jwt`, claims `sub=sessionId`, `aid=agentId`,
   `aud=apiUrl`, exp ~60s). Private key lives in the session file:
   `~/.local/state/agent-kanban/sessions/<sessionId>.json` (contains `agentId`,
   `sessionId`, `privateKeyJwk`, `apiUrl`, `type`).
   Reconstruct a session client-side: import `privateKeyJwk` via
   `crypto.subtle.importKey('jwk', ..., {name:'Ed25519'})` + `SignJWT` from
   `jose` (resolve via `createRequire('.../agent-kanban/dist/index.js')`).
3. **Leader vs worker kind** — the session's agent `kind` decides permissions.

## Endpoints that matter

| Action | Endpoint | Who |
|---|---|---|
| Create task | `POST /api/tasks` (body incl. `board_id`, `title`, ...) | leader ✅ |
| List/get task | `GET /api/tasks`, `/api/tasks/{id}` | leader ✅ |
| Update fields | `PATCH /api/tasks/{id}` (title/description/labels/...) | leader (field updates OK) |
| **Status moves** | `POST /api/tasks/{id}/claim` \| `/review` \| `/complete` \| `/reject` \| `/cancel` \| `/release` | **worker only** — server rejects leader sessions with `agent:worker required` (the string is NOT in the client bundle; it is server-side) |
| Create agent | `POST /api/agents` | needs AMA cloud scheduling → `Connect AMA to enable cloud scheduling` |
| Register machine | `POST /api/machines` | machine key; hosted API returns `runner: null` → `ak start` aborts (`startAmaRunner` hard-requires `onboarding.origin/projectId/environmentId`) |

## Pitfalls discovered

- **`PATCH /api/tasks/{id}` with `status` in the body returns 200 and echoes
  the requested status but does NOT persist it.** Status only moves via the
  action endpoints above. Don't build client workarounds on PATCH-status.
- **Bare `ak` fails inside Hermes/git-bash** with "Could not locate hermes
  process in ancestry": the npm shim (`#!/bin/sh` script) breaks the native
  process-tree walk — the walk stops at the interpreter (`sh.exe`/`env.exe`),
  never reaching `hermes_cli.main serve`. Direct `node dist/index.js`
  invocations walk fine (node's parent is the runner bash).
- **MSYS path mangling**: `node $HOME/...` mangles to `C:\c\Users\...` — always
  pass Windows-style `C:/Users/...` paths to node on this box.
- **Machine registration order**: `ak start` (POST /api/machines) must precede
  `ak auth login`; login-first fails with "Machine not registered".
- Session files are picked by newest mtime in the sessions dir; multiple
  machines/sessions can pile up there.

## Hosted-service ceiling (this account)

Leader-only setup on hosted agent-kanban.dev: can create/list/update tasks but
can NEVER move status past `todo` (no workers creatable without AMA, machine
key revoked, no runner). Unlock = self-host (docker-compose, full runner) or
get AMA enabled on the hosted account.
