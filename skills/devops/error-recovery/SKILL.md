---
name: error-recovery
description: Structured retry and fallback plans for tool failures.
triggers:
  - error
  - fail
  - retry
  - fallback
  - recover
---

# Error Recovery Skill

> **Source:** Extracted from multiple systems' error handling.

## When to Use

When a tool call or step fails.

## Workflow

### Step 1: Classify
- Transient: retry with backoff
- Missing tool: find alternative
- Data issue: fix and retry
- Permission: escalate to user

### Step 2: Retry
For transient errors, retry up to 3 times with exponential backoff.

### Step 3: Fallback
If retry fails, try alternative tool or approach.

### Step 4: Escalate
If all fail, report to user with context.

### Step 5: Resume
After recovery, continue from checkpoint.

### Stuck Loop / Guardrail Halt
A tool-loop guardrail (`identical_call_streak_halt`, `idempotent_no_progress_warning`) ends the STRATEGY, not the task. Never end the turn with "tell me how to proceed" or "send continue" — that punts unfinished work back at the user.
- Inspect the arguments that actually dispatched before any retry: loop repeats are almost always wrong/empty arguments or a call that returns a default/browse result, not a flaky tool.
- Then change something material: different tool, different query, different entry point, or a direct read of the artifact you were chasing.
- Resume the original task and finish it. Ask the user only when the task itself is genuinely blocked (access or a decision only they can make).

## Output

Recovered state or escalation.