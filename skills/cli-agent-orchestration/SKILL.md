---
name: cli-agent-orchestration
description: "Route CLI coding agents with model fallback."
triggers:
  - coding agent
  - commandcode
  - opencode
  - fallback routing
  - model orchestration
  - cli agent
---

# CLI Agent Orchestration

Use CLI coding agents as execution layers with intelligent model routing and automatic fallback. Hermes remains the orchestrator; the CLI agent is the executor.

## When to Use This Skill

- User asks to implement, fix, or modify code via a CLI coding agent
- Task requires invoking `commandcode`, `opencode`, `claude`, `codex`, or similar CLIs
- Need automatic model fallback when primary model is unavailable
- Routing must consider model capabilities, cost, and credit availability

## Core Pattern

1. **Classify the task** (simple edit, architecture, large engineering, local-only)
2. **Select ordered model ladder** based on task class and current health
3. **Health check** each model before routing (lightweight `-p "ping"` probe)
4. **Invoke** with the first healthy model
5. **Fallback** on failure: retry transient errors once, immediately failover on auth/credit errors
6. **Log** every attempt: model, reason, duration, fallback path

## Invocation Pattern (CommandCode CLI)

```bash
# Non-interactive invocation (primary method)
commandcode -p "Task description" --model <model-id>

# With session continuity
commandcode -p "Task" --model <model-id> --name "session-name"

# Health check
commandcode -p "Say 'ok' if you can respond." --model <model-id>
```

### Exit Codes

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Success | Done |
| 10 | Credit exhausted | Immediate fallback, no retry |
| 1 | Unknown model / config error | Fallback |
| 124 | Timeout | Retry once, then fallback |
| other | Provider error | Retry once if transient, then fallback |

### Model Identifiers (CommandCode)

Use full IDs, not short names:
- `deepseek/deepseek-v4-flash` (NOT `deepseek-v4-flash`)
- `meituan/longcat-2.0:free`
- `poolside/laguna-s-2.1-free` (NOT `laguna-s21-free`)
- `meta/muse-spark-1.2-contributor`

See `references/commandcode-model-ids.md` for full catalog.

## Routing Logic

### Task-Aware Model Selection

| Task Class | Primary | Fallback 1 | Fallback 2 | Final |
|------------|---------|------------|------------|-------|
| Large engineering | deepseek-v4-flash | longcat-2.0 | laguna-s21 | ollama-local |
| Architecture/reasoning | deepseek-v4-flash | longcat-2.0 | laguna-s21 | ollama-local |
| Simple edit | deepseek-v4-flash | laguna-s21 | longcat-2.0 | ollama-local |
| Long context | deepseek-v4-flash | longcat-2.0 | — | ollama-local |
| Local-only/private | ollama-local | — | — | — |

### Fallback Triggers

**Immediate fallback (no retry):**
- Credit exhaustion (exit 10, "insufficient credits")
- Authentication failure
- Unknown model (exit 1)

**Retry once, then fallback:**
- Timeout
- Rate limit (429)
- Transient network errors (502, 503, 504, ECONNRESET)

**Do NOT downgrade for speed alone.** Downgrade only on actual failure.

## Health Checks

Before routing to a model, run a lightweight probe:

```bash
commandcode -p "Say 'ok' if you can respond." --model <model-id>
```

Cache results for 60 seconds to avoid redundant probes. A model is "healthy" only if exit code is 0 AND response contains "ok".

### Credit Exhaustion Detection

Check combined stdout/stderr for:
- "insufficient credits"
- "purchase more"

These indicate the model exists but the account lacks credits. Do NOT retry — go straight to fallback.

## Session Continuity

Preserve context across fallbacks by using the `--name` flag:

```bash
commandcode -p "Remember: my favorite color is blue" --model <m1> --name "task-session"
commandcode -p "What is my favorite color?" --model <m2> --name "task-session"
```

Each CLI handles sessions differently — consult the specific agent's skill for details.

## Logging

Every orchestration run should produce an execution log:

```json
{
  "execution_id": "...",
  "task": "...",
  "profile": "...",
  "selected_models": [...],
  "successful_model": "...",
  "fallback_reason": "...",
  "attempts": [...],
  "duration_seconds": ...
}
```

**NEVER log API keys, tokens, or credentials.** Redact before writing to disk.

## Configuration

### Hermes config.yaml

```yaml
delegation:
  provider: commandcode
  model: deepseek/deepseek-v4-flash

fallback_providers:
  - provider: commandcode
    model: deepseek/deepseek-v4-flash
  - provider: commandcode
    model: meituan/longcat-2.0:free
  - provider: commandcode
    model: poolside/laguna-s-2.1-free
  - provider: local-ollama
    model: qwen2.5-coder:3b
```

### Adding Models to a Provider

Use `hermes config set` or edit config.yaml directly. Verify the model exists in the provider's catalog before adding:

```bash
commandcode --list-models | grep <model-name>
```

## Script Reference

`scripts/cc_orchestrate.py` provides a complete implementation of this pattern:
- Task classification
- Health-checked model selection
- Automatic fallback with retry logic
- JSON execution logs
- Session continuity via `--name` flag

Run it directly:
```bash
python3 ~/.hermes/skills/cli-agent-orchestration/scripts/cc_orchestrate.py "Your task"
```

## Pitfalls

1. **Piping passwords to sudo** — `echo "1" | sudo -S ./setup.sh` sends "1" as the password. Use `sudo ./setup.sh` alone.
2. **Wrong model short names** — `laguna-s21-free` fails; use `poolside/laguna-s-2.1-free`.
3. **Ignoring exit code 10** — Credit exhaustion is not a transient error. Do not retry.
4. **Health check without cache** — Probing every request adds latency. Cache for 60s.
5. **Using bare model IDs** — Always qualify with provider prefix.

## Related Skills

- `autonomous-ai-agents/opencode` — OpenCode CLI delegation
- `autonomous-ai-agents/claude-code` — Claude Code CLI delegation
- `autonomous-ai-agents/codex` — Codex CLI delegation
- `subagent-delegation` — Hermes delegate_task patterns
