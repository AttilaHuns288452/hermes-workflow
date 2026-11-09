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

## Audit-and-fix missions (protected areas)

When the mission is "audit this app and fix what you find" — especially with
protected areas (files another dev owns) or a co-dev pushing in parallel — the
plan-approval gate is mandatory and the plan has a specific shape:

1. **Finish the evidence phase first.** Dispatch the audits, wait for ALL
   subagent batches to land, then compile. A plan written on partial findings
   gets revised twice and wastes the approval.
2. **Record protected boundaries in a committed scope file** (e.g.
   `docs/audit-<date>/PROTECTED-SCOPE.md`) before touching anything. When the
   user revises the boundaries mid-mission, update the file and commit before
   continuing — the scope file is the durable record of what was authorized
   when.
3. **Present the plan as a fix table, not prose:** every finding with root
   cause, the exact files to touch, the reasoning for the fix chosen, the
   verification method, and an explicit "leave alone + why" list. The user
   approves the *thought process*, not just the file list.
4. **No edits until approval.** The user is otherwise action-oriented; this
   gate applies to audit-and-fix missions, not to routine tasks — do not
   generalize it into plan-first-everything.

## Output

A clear plan presented to the user, followed by execution after approval.