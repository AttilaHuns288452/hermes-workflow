---
name: checkpoint
description: Save and resume session state for long-running tasks.
triggers:
  - long task
  - pause
  - resume
  - state
  - progress
---

# Checkpoint Skill

> **Source:** Extracted from Microsoft Copilot CLI checkpointing.

## When to Use

- Tasks lasting more than 5 tool calls
- Tasks interrupted by context limits
- Tasks that may need to resume later

## Workflow

### Step 1: Save State
Create a checkpoint record with:
- Task description
- Current progress
- Completed steps
- Pending steps
- File changes made
- Variables/state

### Step 2: Store Checkpoint
Save to state.db or session workspace.

### Step 3: Resume
When user says "continue" or "resume", read checkpoint.

### Step 4: Restore Context
Re-load necessary files and state.

## Output

Session can be interrupted and resumed without losing progress.