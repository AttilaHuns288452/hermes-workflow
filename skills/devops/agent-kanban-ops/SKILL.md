---
name: agent-kanban-ops
description: Operate the agent-kanban (ak) CLI from Hermes — install, credential setup, machine registration, leader auth, daemon limits, and Windows/git-bash quirks. Use when setting up, configuring, or troubleshooting the ak CLI against agent-kanban.dev or a self-hosted server.
---

# Agent-Kanban Ops (ak CLI)

Operator-side setup and troubleshooting for the `ak` CLI (npm package `agent-kanban`,
binary `ak`). Complements the worker-facing `agent-kanban` skill (task lifecycle)
and `ak-plan`/`ak-task`/`ak-maintainer` skills (board workflows).

## Setup sequence (order matters)

1. `npm install -g agent-kanban` → verify `ak --version` (1.15.0 at time of writing).
2. `ak config set --api-url https://agent-kanban.dev --api-key <key>` — persists to
   `~/.config/agent-kanban/config.json`. Never echo the key in output; mask it
   (`sed 's/ak_[A-Za-z0-9]*/ak_***/'`) when displaying config.
3. **Register a machine BEFORE leader login.** `ak auth login --leader-agent` fails
   with `Machine not registered` until a machine exists for the account — the server
   binds agent sessions to a registered machine. `ak start` registers one on boot;
   if the daemon can't start, register manually via
   `POST /api/machines` (server upserts by `device_id`; see
   `references/setup-windows-git-bash.md` for the exact curl).
4. `ak auth login --leader-agent --username <u> --name <n>` → prints identity +
   session. Verify with `ak auth whoami` (Type: leader, Runtime: hermes).

## Known limitations (hosted agent-kanban.dev)

- `ak start` (machine daemon) exits with `Machine registration did not return runner
  onboarding details`: the hosted API returns `"runner": null` for local machines —
  no AMA runner onboarding (origin/projectId/environmentId). Server-side, no CLI
  flag/env bypass in 1.15.0. Leader/board/task CRUD works without the daemon; only
  local worker spawning is gated.

## Windows / git-bash pitfalls

- Bare `ak` breaks with `Could not locate hermes process in ancestry` — the npm
  `#!/bin/sh` shim truncates the native process-tree ancestry walk. Fix: wrapper
  that delegates through `cmd.exe` (chain stays intact). Deleting the shim does NOT
  make bash fall back to `ak.cmd` — the command becomes "not found". Workaround:
  `node "$(npm root -g)/agent-kanban/dist/index.js" ...`. Full detail + probe script
  in `references/setup-windows-git-bash.md`.

## Useful diagnostics

- `ak get board` / `ak get agent -o json` — board and agent state (includes
  `status.schedulable`, task counts).
- `ak get repo` — registered repos (none until you register one).
- Server responses: `429` retry-after, `401` bad session, `409` state conflict.
  Errors like `Machine not registered` and `Leader agents cannot be modified` come
  from the server, not the CLI — curl the endpoint directly with the machine key to
  distinguish server-side conditions from local setup problems.
