---
name: ak-subagent-board
description: |
  Track subagent-delegated work on the Agent Kanban board (agent-kanban.dev,
  board u7j2gicp "My Board"). Before delegating via delegate_task, create an
  AK task row for the work; after the subagent's result is verified, the board
  stays as the ledger. Use when agent-kanban is configured and the user asks
  for subagent delegation or board utilization. Not for ordinary single-agent
  work.
---

# ak-subagent-board — Kanban-tracked subagent delegation

Every delegated unit of work gets an AK task row on board `u7j2gicp`. The
board is the work ledger; the chat is not.

> Debugging the board's API/auth internals? See
> `references/agent-kanban-api-notes.md` (endpoint table, session-JWT
> reconstruction, PATCH-status trap, worker-gate proof).

## Environment (this machine)

- The bare `ak` command is BROKEN in this shell (npm shim breaks
  process-ancestry detection). Always invoke via node directly, with a
  Windows-style path (MSYS mangles `$HOME`-expanded paths):

```bash
export AK="C:/Users/Attila/AppData/Roaming/npm/node_modules/agent-kanban/dist/index.js"
node "$AK" <command>            # e.g. node "$AK" get board u7j2gicp
```

- Board: `u7j2gicp` ("My Board"). Leader identity: `attila` /
  `c766796c27aa2c36` (runtime hermes) — session persisted locally.
- If `node "$AK" auth whoami` says no session: re-login:
  `node "$AK" auth login --leader-agent --username attila --name "Attila"`.

## Workflow

1. **Create the task before delegating:**

```bash
node "$AK" create task --board u7j2gicp --title "<what the subagent does>" \
  --description "<context summary, acceptance criteria>" -o json
```

   Capture the returned task `id`.

2. **Pass the task id to the subagent** in the `delegate_task` context:
   "This work is tracked as AK task <id> on board u7j2gicp."

3. **Subagent executes.** Subagents do NOT move board status — status
   mutation endpoints are worker-gated server-side (see below). The subagent
   returns its result in the chat, as usual.

4. **Orchestrator closes the loop** — verify the subagent's result (never
   trust a bare self-report), then record the outcome on the board where
   possible: re-list to confirm the row, or update its description with the
   outcome:

```bash
node "$AK" get task <id> -o json         # confirm row + current state
node "$AK" get board u7j2gicp            # board-level rollup
```

## Status lifecycle — current limitation (verified 2026-07-31)

The board's full lifecycle is `todo → claim → in_progress → review →
in_review → complete → done`, but on the HOSTED agent-kanban.dev this account
can only ever reach `todo`:

- `task claim/review/complete/reject/cancel` → server rejects with
  `agent:worker required` (worker-kind session only; verified server-side).
- Worker agents cannot be created: `ak create agent` → "Connect AMA to enable
  cloud scheduling"; the hosted API returns `runner: null` (no AMA runner
  provisioned for this account) and the machine API key was revoked by the
  server (401 on all machine endpoints).
- The machine daemon (`ak start`) cannot run for the same reason.

**Unlock options** (ask the user before doing either):
1. **Self-host agent-kanban** (github.com/saltbo/agent-kanban, docker-compose)
   — full machine runner, worker agents, and complete lifecycle locally.
2. **Get AMA enabled** on the hosted account (agent-kanban.dev dashboard) —
   then workers become creatable and the daemon can run.

Until then: use the board as a **creation + visibility ledger** (every
delegation gets a row; the board shows what's in flight). Do not tell the
user a task was "completed" on the board — it cannot be.

## Pitfalls

- Never run bare `ak` — shim ancestry bug. `node "$AK"` only.
- Use `C:/Users/...` paths, not `$HOME/...`, when passing paths to node.
- `create task --assign-to <id>` only when the agent exists — none do today
  (AMA-gated).
- PATCH `/api/tasks/<id>` with `status` echoes 200 but does NOT persist —
  status only moves via the action endpoints (worker-only).
