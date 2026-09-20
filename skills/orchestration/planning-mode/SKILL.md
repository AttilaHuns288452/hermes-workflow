---
name: planning-mode
description: Plan→approve→execute workflow for complex tasks.
triggers:
  - plan
  - design
  - implement
  - build
  - feature
  - architecture
---

# Planning Mode Skill

> **Source:** Extracted from Google Antigravity, Microsoft Copilot, and Cursor planning modes.

## When to Use

For tasks that require:
- Multiple files or modules
- Architecture decisions
- User approval before execution
- Significant ambiguity
- New feature implementation

## When NOT to Use

- Single-file changes
- Trivial fixes
- Read-only tasks
- Quick lookups

## Workflow

### Step 1: Understand
Read the task, understand the goal, identify constraints.

### Step 2: Create Plan
Write a plan.md file in the session workspace with:
- Goal statement
- Proposed approach
- Files to change
- Steps in order
- Risks and trade-offs
- Open questions

### Step 3: Present to User
Show the plan and ask for approval.

### Step 4: Execute
After approval, execute each step in order.

### Step 5: Track Progress
Update task-tracker or kanban as steps complete.

### Step 6: Verify
After execution, run appropriate verification.

## Output

A clear plan presented to the user, followed by execution after approval.