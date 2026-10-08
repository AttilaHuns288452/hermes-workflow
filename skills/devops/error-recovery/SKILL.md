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

## Output

Recovered state or escalation.