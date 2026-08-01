---
name: orchestrator-profile-factory
description: Profile creation playbook for the kanban orchestrator. Create specialized worker profiles on demand from the golden `learning` template.
triggers:
  - "create profile"
  - "new worker"
  - "spawn worker profile"
  - "profile factory"
---

# Orchestrator Profile Factory

When no existing profile fits a task's needs, create one.

## Decision flow (run BEFORE kanban_create)

```
1. hermes profile list                          # see available profiles
2. Match by role needed → exists? → reuse       # researcher, reviewer, writer, etc.
3. No match → hermes profile create <role> --clone-from learning --description "<what>"
4. hermes profile describe <role> --text "<one-line>"
5. kanban_create(assignee="<role>", ...)        # now the dispatcher can spawn it
```

**Rule:** check `hermes profile list` before every `kanban_create`. Unknown assignee = dispatcher silently fails (`skipped_nonspawnable`).

## Create a worker profile

```bash
hermes profile create <name> --clone-from learning \
  --description "<one-line role>"
```

## Describe it (for decomposer routing)

```bash
hermes profile describe <name> --text "<what this profile does best>"
```

## Pin its model (optional, inherits learning's otherwise)

```bash
hermes -p <name> config set model deepseek-v4-flash-free
hermes -p <name> config set provider opencode
```

## Then use it in kanban

```
kanban_create(title="...", assignee="<name>", body="...")
```

## Ponytail rules

- One profile per role. Don't create 5 researchers — one `researcher` with parallel tasks.
- Reuse before creating. Check `hermes profile list` first.
- Name = role. `researcher`, `reviewer`, `writer`, `translator`, not `worker-1`.
- Delete stale ones. `hermes profile delete <name>` when a role is no longer needed.
