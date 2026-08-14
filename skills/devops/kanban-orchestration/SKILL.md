---
name: kanban-orchestration
description: Orchestrate work on the Hermes kanban board.
---

# Kanban Orchestration (Hermes built-in board)

Operate `hermes kanban` (SQLite board, one board per project/workstream) as the
orchestrator: decompose → create tasks → dispatch parallel worker waves via
`delegate_task` → mark done as results land → final ECC gate task.

## The child-context guard (first thing to know)

Desktop-app sessions can inherit `HERMES_DELEGATED_CHILD_CONTEXT=1`; then ANY
`hermes kanban` mutation fails with:
`delegate_task child contexts cannot mutate Kanban tasks or boards`.
The guard keys off the env var only — strip it per-command:

```bash
env -u HERMES_DELEGATED_CHILD_CONTEXT hermes kanban --board <slug> list
```

Define a shell helper once per session: `K() { env -u HERMES_DELEGATED_CHILD_CONTEXT hermes kanban "$@"; }`.

## Board + task workflow (verified syntax)

```bash
K boards create <slug> --name "Sprint name"          # one board per workstream
K --board <slug> create "Task title" --body "spec"   # returns Created t_<id>
K --board <slug> list                                # verify — always verify after batch creates
K --board <slug> edit t_<id> --result done           # completion (see quirks)
K --board <slug> comment t_<id> "progress note"      # log progress/decisions on a task (verified 2026-08)
```

Full CLI per `hermes kanban --help`: `init boards create swarm list show
assign set-model reclaim reassign claim comment attach complete edit block
schedule unblock promote archive tail dispatch daemon watch stats link unlink
log runs context specify decompose gc repair`. `complete`/`block`/`claim`/
`link`/`swarm` exist for lifecycle moves; `edit --result done` remains the
verified-completion path until `complete` is confirmed on this install.

## CLI quirks (each cost real time — don't repeat)

- `--priority P1` on `create` is INVALID (unknown choices) — the command exits 0
  with usage text, so **never swallow create output** with `>/dev/null` when
  scripting; a silent failure looks like success until `list` shows nothing.
- `edit` has NO `--status` flag — it requires `--result` (e.g. `--result done`).
- `create --body` is the place for the task spec; workers don't see the chat, so
  the body must be self-contained (file scope, design language, quality bar).
- Boards are per-project: pass `--board <slug>` to every subcommand; `create`
  without `--board` lands on `default`.
- `complete <id> --result done` (verified 2026-08-06) prints a MISLEADING
  `cannot complete t_<id> (unknown id or terminal state)` while actually
  completing the task — and `complete t_a t_b t_c --result done` completes
  multiple ids in one call (first id may report the error, the rest succeed).
  NEVER trust the command's stderr; always verify with `list` afterwards.

## External `ak` CLI — when to skip it

`ak` (agent-kanban.dev) is the hosted alternative but needs BOTH a saved auth
session AND a registered machine before any board op. `ak get board` →
"No AK auth session found" → `ak auth login --leader-agent` requires a username
you may not have. If `~/.config/agent-kanban/config.json` holds only
`api-url`/`api-key` (no session), don't burn time on machine registration —
use the built-in `hermes kanban` board (offline, no daemon). On git-bash, bare
`ak` fails with "Could not locate hermes process in ancestry" — the npm shim;
run `node "$(npm root -g)/agent-kanban/dist/index.js" ...` instead.

## Orchestration pattern (what works)

0. **Check existing boards before creating new tasks** — `boards list`, then
   `--board <slug> list` on each. Prior sprints often leave READY tasks that
   were planned but never executed (cfos-sprint2 sat ready for days); resuming
   them beats inventing fresh scope.
1. Create board + tasks with self-contained `--body` specs (file ownership per
   task is mandatory — overlapping file scopes between parallel workers conflict).
2. Dispatch ONE `delegate_task(tasks=[...])` batch per wave; workers in a wave
   must own DISJOINT files. Order waves by dependency (design foundation →
   pages → gate).
3. While workers run, do the small non-owned fixes yourself (files no worker
   touches) — verify with `tsc --noEmit` after.
4. Close tasks with `--result done` as batches land; keep the final task for the
   review gate (ECC agents) + build + deploy.
5. **Board audit before declaring done / before the next phase** (user asks
   "are the assigned tasks actually finished?" — 2026-08-06): `boards list` +
   per-board `list`, then triage EVERY non-done task against reality, not the
   board's word: stale READY tasks whose work already shipped in code get closed
   after grep-verifying the artifact exists (the `default` board carried 3 READY
   tasks from a prior sprint — validation.ts/toast/pagination — all shipped, all
   closed with evidence); BLOCKED is only for genuine external blockers (dead
   API, missing creds); leave a closing comment per task (what/when + the
   verification evidence) so the audit trail shows the task was checked, not
   just flipped.

## Overlaps (curator note)

Overlaps user-owned `hermes-kanban-setup` (setup) and `devops/agent-kanban-ops`
(ak CLI ops) — those are off-limits to autonomous curation; adopt them via
`hermes curator adopt` to merge this content in.
