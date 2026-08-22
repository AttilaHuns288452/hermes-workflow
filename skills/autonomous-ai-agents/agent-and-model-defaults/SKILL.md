---
name: agent-and-model-defaults
description: "Workflow defaults: Hermes chat model orchestrates, Muse Spark codes @ opencode-go, MiMo handles vision. OpenCode config + AGENTS.md setup."
version: 1.2.0
author: Hermes Agent
tags: [workflow, defaults, opencode, ecc, model, vision, mimo, glm, muse-spark, mimo-v2.5]
---

# Agent & Model Defaults

## Role Assignments

| Role | Tool | What it does |
|------|------|-------------|
| **Orchestrator** | Hermes (this session) | Understands the task, breaks it down, decides which agent to invoke, verifies results |
| **Coder** | OpenCode (`opencode run`) | Writes, edits, and reviews files. Executes coding tasks |
| **Specialists** | ECC agents (via ecc-bridge + OpenCode) | Domain-specific reviews: a11y-architect (UI/UX), code-architect (architecture), code-reviewer (quality) |

## Model Default

**Always** use `opencode/meta/muse-spark-1.2-contributor` (config.yaml `opencode-go` — provider is truth, not this file):

```
opencode run '...' --model opencode-go/meta/muse-spark-1.2-contributor
```

### Full Model Role Split (User Preference)

| Role | Model | Provider | When |
|------|-------|----------|------|
| **Orchestrator / Planning / Architecture / Reasoning** | **Hermes chat model** (= `config.yaml` `model.default`) | opencode-go (source of truth) | Understanding tasks, delegation decisions, architecture design, planning. NEVER for terminal/git/patch/coding. |
| **Main coding agent — implementation, edits, coding, execution** | `meta/muse-spark-1.2-contributor` | `opencode-go` (config truth `delegation.model`) | ALL coding+git+deploy+build+patches+merge conflicts |
| **Multimodal (images, video, audio, PDFs, charts)** | `mimo-v2.5` | `opencode-go` (config truth `auxiliary.vision`) | Visual understanding, screenshots, UI audits, design review |
| **Difficult multimodal reasoning** | `mimo-v2.5-pro` | `opencode-go` | Complex, long-running multimodal tasks |

### Delegation Config (Critical — Prevents Model Leakage)

Hermes `delegate_task` subagents inherit the **parent session model** unless pinned in config.yaml. When the orchestrator is a reasoning model (e.g. `muse-spark-1.2-contributor`), empty delegation config leaks it into every subagent task:

```yaml
# ~/AppData/Local/hermes/config.yaml
delegation:
  model: muse-spark-1.2-contributor   # truth: config.yaml delegation.model
  provider: opencode-go              # truth: config.yaml delegation.provider
```

Empty `model`/`provider` = children inherit parent model. Set both to pin ALL subagents to the coding agent (Muse Spark @ opencode-go) regardless of parent session.

### Pantheon Swarm Agent Models

oh-my-opencode-slim needs per-agent overrides so Orchestrator follows the chat model while agents use Muse Spark / MiMo:

```json
{
  "agents": {
    "orchestrator": {
      "model": "opencode-go/muse-spark-1.2-contributor"
    },
    "observer": {
      "model": ["opencode-go/mimo-v2.5"]
    }
  }
}
```

Other agents (oracle, explorer, librarian, designer, fixer) inherit the global default — `opencode-go/meta/muse-spark-1.2-contributor` (config truth).

Set Muse Spark as OpenCode's default in the VS Code extension config (`~/.vscode/extensions/tanishqkancharla.opencode-vscode-<version>/opencode.json`):

```json
{
  "agent": {
    "main": {
      "description": "Primary coding agent — Muse Spark 1.2 Contributor @ opencode-go",
      "model": "opencode-go/meta/muse-spark-1.2-contributor"
    }
  }
}
```

Create `~/AGENTS.md` so OpenCode knows the role split:

```markdown
## Model Roles
| Role | Model |
|------|-------|
| Orchestrator / planning / architecture | Hermes chat model (currently `opencode-go/muse-spark-1.2-contributor`) |
| Implementation / coding / execution | `opencode-go/meta/muse-spark-1.2-contributor` |
| Multimodal (images, video, audio) | `opencode-go/mimo-v2.5` |
| Difficult multimodal | `opencode-go/mimo-v2.5-pro` |
```

OpenCode reads `AGENTS.md` from the working directory or home. This is the equivalent of Hermes's `/decide` model role split.

### Hermes Vision Model

Hermes config (`~\AppData\Local\hermes\config.yaml`) should have:

```yaml
ai:
  vision:
    model: mimo-v2.5
    provider: opencode-go
```

### Skill Access

OpenCode already has permission-granted access to all Hermes skills at `~\AppData\Local\hermes\skills\`. No file copying needed — OpenCode reads them on demand via `external_directory` permissions. Verify: `opencode config` should show permission entries for the Hermes skills path.

## Delegation Pattern

### Simple coding task → OpenCode

```
opencode run 'Implement X' --model opencode-go/meta/muse-spark-1.2-contributor
```

### Code + specialist review → OpenCode + ECC agent

Extract ECC agent prompt and attach it to the OpenCode run:

```
python scripts/ecc-runner.py <agent-name> "context" > agent-prompt.md
opencode run 'Read the files and apply the attached framework' \
  --model opencode-go/meta/muse-spark-1.2-contributor \
  --file agent-prompt.md
```

### Multiple specialists in one run → attach multiple `--file` flags

```
python scripts/ecc-runner.py code-architect "..." > arch.md
python scripts/ecc-runner.py code-reviewer "..." > review.md
opencode run 'Apply both architecture and review feedback' \
  --model opencode-go/meta/muse-spark-1.2-contributor \
  --file arch.md --file review.md
```

## Common ECC Agents for Coding Tasks

| Domain | ECC Agent | Purpose |
|--------|-----------|---------|
| UI/UX / Accessibility | `a11y-architect` | WCAG 2.2, keyboard nav, ARIA, contrast |
| Code Architecture | `code-architect` | Separation of concerns, patterns, modularity |
| Code Quality | `code-reviewer` | Bugs, style, best practices |
| Refactoring | `code-simplifier` / `refactor-cleaner` | Dead code, simplify logic |

## Verification

After any agent-run:

1. Files were written/edited (check with `ls -la`)
2. Functionality unchanged (open in browser if possible)
3. No regressions introduced

## Is Model X the Latest? — Verify via the OpenCode Registry Cache

When the user asks "is this the latest/updated model", do NOT guess from memory — the local OpenCode registry cache is authoritative and queryable in seconds:

```bash
# Cache: ~/.cache/opencode/models.json (3.3 MB, refreshed on opencode use — check its mtime first)
python -c "
import json
d = json.load(open('C:/Users/YOUR_USERNAME/.cache/opencode/models.json', encoding='utf-8'))
for prov, pv in d.items():
    for mid, mv in pv.get('models', {}).items():
        if 'v4-flash' in mid.lower() or 'v4_flash' in mid.lower():
            print(f'{prov:14s} | {mid:55s} | rel={mv.get(\"release_date\",\"?\")} upd={mv.get(\"last_updated\",\"?\")}')
"
```

**How to read the output (the part that's easy to get wrong):**
- `release_date` is the model's real version. All providers serving `deepseek-v4-flash` show `release_date: 2026-04-24` → it's THE current V4 Flash; a newer variant would carry a different release date.
- `last_updated` varies per provider (e.g. fireworks 2026-06-16, hyper 2026-07-22) — that's **provider-side serving/caching updates, NOT a new model version**. Don't report "there's a newer version" from `last_updated` alone.
- If the cache mtime is old, refresh it first (run any opencode command, e.g. `opencode run 'OK'`) so the answer reflects the current registry.
- Also confirm the Hermes side: `hermes --version` + the session's provider/model from config.yaml `model:` block.
- Provider IDs: `opencode` = Zen (`https://opencode.ai/zen/v1`, has the `-free` variants), `opencode-go` = Go lane (no `-free`), `openrouter` etc. are third-party resellers of the same model.

## Pitfalls

- **File-targeting: OpenCode writes at `workdir`, not at the path you describe.** If the user says "improve `project-a/file.html`" and you run OpenCode from `project-b/`, the edits go to `project-b/`. Always set `workdir` to the project containing the target file. Verify the right file was modified after every agent run.
- **Stderr noise in `opencode run` output.** Progress lines (`→ Read file.html`, `← Edit file.html`) print to stderr. The actual result is after `Done.` in stdout. Use the last paragraph.
- **OpenCode stale DB blocks all runs.** If `opencode run` fails with "Unexpected server error" and the logs show `SQLiteError: no such column: replacement_seq`, the local SQLite schema is stale from a version upgrade. Fix: kill any opencode processes (`ps | grep opencode`), delete `~/.local/share/opencode/opencode.db`, retry. OpenCode recreates it fresh. Full recovery steps: `references/opencode-stale-db-recovery.md`.
- **Windows `/tmp` doesn't exist.** When writing temp prompt files for `--file`, use a project-relative path (e.g. `ecc-prompt.md`) or a full `C:/Users/...` path. MSYS `/tmp` fails silently — `opencode run --file /tmp/foo` reports "File not found".
- **Smoke-test before long runs.** If switching to a new or lesser-used model, always run `opencode run 'Respond with exactly: OK' --model <model>` first. Free-tier models can disappear or hit rate limits silently.
- **Empty delegation config leaks parent model into subagents.** When `delegation.model` and `delegation.provider` are empty in Hermes config.yaml, `delegate_task` subagents inherit the parent session model. Pin both to `muse-spark-1.2-contributor` / `opencode-go` to prevent this.
- **Model routing changes must propagate to 6+ touchpoints.** See `references/model-routing-propagation-chain.md` for the full list of files/skills to update when model preferences change. Missing any creates a stale reference.
