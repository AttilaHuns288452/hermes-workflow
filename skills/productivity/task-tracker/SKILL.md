---
name: task-tracker
description: Per-task todo tracking with priorities and blockers.
triggers:
  - task
  - todo
  - subtask
  - priority
  - block
---

# Task Tracker Skill

> **Source:** Extracted from Microsoft Copilot CLI and Kimi task management.

## When to Use

Any task with 3+ subtasks or non-trivial complexity.

## Workflow

### Step 1: Decompose
Break the task into subtasks.

### Step 2: Prioritize
Mark high/medium/low priority.

### Step 3: Track Status
- pending → in_progress → completed

### Step 4: Blockers
If blocked, mark block reason and escalate.

### Step 5: Update
Update status after each subtask completion.

## Output

Task list with status and progress.