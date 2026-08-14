---
name: hermes-kanban-setup
description: Set up Hermes built-in Kanban board. The default profile handles orchestration — KANBAN_GUIDANCE auto-injects the decompose/route/complete lifecycle. No separate orchestrator profile needed. NOT agent-kanban (ak).
triggers:
  - "set up kanban"
  - "kanban board"
  - "hermes kanban"
  - "multi-agent board"
---

# Hermes Kanban Setup

Hermes Kanban is the **built-in** kanban system (SQLite DB, embedded dispatcher, profile-based workers). NOT the external `agent-kanban` (ak) CLI.

## Quick setup

```bash
# 1. Init DB (one-time)
hermes kanban init

# 2. Start gateway (hosts embedded dispatcher, ticks every 60s)
hermes gateway start

# 3. Point kanban at your default profile.
#    KANBAN_GUIDANCE auto-injects the decompose/route/complete lifecycle.
hermes config set kanban.orchestrator_profile default
hermes config set kanban.auto_decompose true

# 4. Add descriptions to worker profiles (for decomposer routing)
hermes profile describe codingprofile --text "Backend developer: writes APIs, database schemas, server logic."
hermes profile describe finance --text "Financial analyst: researches markets, writes reports, analyzes data."
hermes profile describe learning --text "General researcher: finds information, summarizes topics, creates docs."

# 5. Create a task (from triage, auto-decomposed)
hermes kanban create "your goal here" --assignee default --triage
```

## Key concepts

- **No separate orchestrator profile** — the default profile handles orchestration. KANBAN_GUIDANCE auto-injects the "don't implement, just decompose" rules.
- **Workers don't shell out** to `hermes kanban` — they use `kanban_*` tools auto-injected into their schema
- **Scratch workspaces** are deleted on completion; use `--workspace dir:<path>` or `worktree` to preserve output
- **Dashboard** at `hermes dashboard` → Kanban tab shows the visual board
- **`hermes kanban watch`** streams live events
- **`hermes kanban dispatch --max N`** nudges the dispatcher (skip the 60s wait)

## Creating worker profiles on demand

When a task needs a profile that doesn't exist yet, create one from the golden `learning` template:

```bash
hermes profile create <role> --clone-from learning --description "<one-line>"
hermes profile describe <role> --text "<what this profile does best>"
```

Reuse before creating — check `hermes profile list` first.

## Manual operations

```bash
hermes kanban specify <id>          # LLM-flesh-out a triage task → todo
hermes kanban decompose <id>        # LLM-fan-out into child tasks
hermes kanban promote <id>          # todo → ready
hermes kanban dispatch --max 5      # one-shot dispatch pass
hermes kanban show <id>             # full task details + runs
hermes kanban runs <id>             # attempt history
hermes kanban list                  # board overview
hermes kanban stats                 # per-status counts
```

## Swarm batch lifecycle (kanban + delegate_task)

Proven pattern for project batches (UI overhauls, fix rounds):

1. **One task per workstream** — `hermes kanban create "<scope>" --body "<spec>" --assignee orchestrator --project <slug>`; scope = one agent's disjoint file set (never two agents on the same file in one batch).
2. **Dispatch ≤3 agents** via `delegate_task` with `tasks: [...]`; each brief self-contained: exact file paths, design tokens, `Run 'npx tsc --noEmit' at end (NOT npm run build)`, "Report files changed + tsc result".
3. **Complete AFTER verification, never on self-report.** Subagent "tsc clean" claims are not proof — run `npx tsc --noEmit` + `npm run build` yourself, then `hermes kanban complete <id>`.

## Subagent timeout mid-edit recovery

A subagent that times out (~600s) can leave **broken WIP** in its target file. Siblings that ran tsc concurrently then report those errors as "pre-existing in a file I never touched" — they're actually the dead agent's partial edits.

- Verify: `git diff --stat <file>` + read the diff. Remaining type errors are usually **one repeated pattern** (e.g. `string | undefined` → `SetStateAction<string>`). Fix with `patch replace_all` (`setErr(r.error)` → `setErr(r.error ?? "")`), re-tsc. Fix directly instead of re-dispatching a fresh 600s agent for a handful of one-line errors.

## Auto-decompose model

The decomposer uses `auxiliary.kanban_decomposer` in config.yaml (defaults to `auto` → main chat model). Set explicitly if auto fails:

```bash
hermes config set auxiliary.kanban_decomposer.model deepseek-v4-pro
hermes config set auxiliary.kanban_decomposer.provider opencode-go
```

## Pitfalls

- **"Default profile" ambiguity:** "make orchestrator the default" has TWO meanings. In kanban: `kanban.orchestrator_profile: default` (the system profile orchestrates). System-wide: `hermes profile use default` (your main profile, not a separate orchestrator one). Correct: keep ONE profile, set `kanban.orchestrator_profile` to it, KANBAN_GUIDANCE injects the rules. Do NOT create a separate orchestrator profile — skills/MCP/config will drift.
- **Gateway must be running** for the dispatcher to pick up tasks. Check: `curl http://127.0.0.1:8642/` (404 is normal — alive)
- **`hermes kanban dispatch`** is a one-shot pass — doesn't run the decomposer unless the gateway is on
- **Decomposer PermissionDeniedError**: the auxiliary model's `auto` may resolve to a provider with auth issues. Set `auxiliary.kanban_decomposer` explicitly or use `hermes kanban specify`.
- **Two config files**: active is `AppData/Local/hermes/config.yaml`, NOT `~/.hermes/config.yaml` (legacy)
- **Skill discovery via LightRAG** — sub-second TF-IDF over 665 skills: `python C:/Users/YOUR_USERNAME/AppData/Local/hermes/lightrag_index/find.py "<query>"`
- **Stale "ready" tasks after shipped work:** tasks implemented outside the dispatcher (direct swarm, manual commits) stay `ready` forever. Before creating a new task, run `hermes kanban list` and close tasks whose work already shipped (verify via git log / deploy) with `hermes kanban complete <id>` — prevents duplicate planning on the next session.
- **`/decide` routes kanban tasks** — triggers: "kanban", "task board", "decompose", "agent pipeline", "parallel workers", "swarm"

## Profile sync (all profiles get same skills/MCP)

```bash
# New profiles — clone from learning (the golden profile):
hermes profile create <name> --clone-from learning
# Then customize model/provider:
hermes -p <name> config set model <model>
hermes -p <name> config set provider <provider>
```

## Maintenance automation (cron jobs)

```bash
# LightRAG daily rebuild — 4am
hermes cronjob create --schedule "0 4 * * *" \
  --prompt "Run: python C:/Users/YOUR_USERNAME/AppData/Local/hermes/lightrag_index/build_index.py"

# Gateway health check — every 30m
hermes cronjob create --schedule "every 30m" \
  --prompt "curl -s http://127.0.0.1:8642/ — report if not 404"

# Profile config drift — daily 6am
hermes cronjob create --schedule "0 6 * * *" \
  --prompt "Compare profile configs vs global for skills.external_dirs and mcp_servers"

# State backup — daily 3am
hermes cronjob create --schedule "0 3 * * *" \
  --prompt "hermes backup -q -l daily-$(date +%Y%m%d); cp kanban.db ~/backup/"
```

All silence=healthy. Wire to Telegram with `deliver=telegram` for push alerts.
