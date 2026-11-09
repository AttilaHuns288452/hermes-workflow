---
name: executing-plans
description: Use when you have a written implementation plan to execute in a separate session with review checkpoints
---

# Executing Plans

## Overview

Load plan, review critically, execute all tasks, report when complete.

**Announce at start:** "I'm using the executing-plans skill to implement this plan."

**Note:** Tell your human partner that Superpowers works much better with access to subagents (Claude Code, Codex CLI, Codex App, Copilot CLI, and Gemini CLI all qualify; see the per-platform tool refs in `../using-superpowers/references/`). If subagents are available, use superpowers:subagent-driven-development instead of this skill.

## The Process

### Step 1: Load and Review Plan
1. Ensure an isolated workspace: use superpowers:using-git-worktrees to create one or verify the existing one
2. Read plan file
3. Review critically - identify any questions or concerns about the plan
4. If concerns: Raise them with your human partner before starting
5. If no concerns: Create todos for the plan items and proceed

### Step 2: Execute Tasks

For each task:
1. Mark as in_progress
2. Follow each step exactly (plan has bite-sized steps)
3. Run verifications as specified
4. Mark as completed

### Step 3: Complete Development

After all tasks complete and verified:
- Announce: "I'm using the finishing-a-development-branch skill to complete this work."
- **REQUIRED SUB-SKILL:** Use superpowers:finishing-a-development-branch
- Follow that skill to verify tests, present options, execute choice

## Continuous execution for pasted briefs

When the plan arrives as a pasted brief (a spec handed over for immediate work),
this user wants it carried to completion in one pass — do not stop after each
phase to report and wait for a go-ahead. Report once, at the end, covering what
was done and what was verified.

- **Handwritten line beats the brief.** When a message carries both a short
  handwritten instruction and an attached spec, the handwritten line is the
  immediate priority and the brief is still expected to be executed. Do both,
  handwritten first.
- **Unanswered questions get a sensible default, not a pause.** Choose the
  reasonable option, proceed, and surface the choice in the final report. Reserve
  stopping for genuine blockers (missing access, a destructive action, a decision
  that changes what gets built and cannot be defaulted).
- **The brief's own deliverable requirements are acceptance criteria.** If it asks
  for a report with named sections, before/after evidence, or specific
  verification, produce exactly that — not a summary of effort.
- Later direct instructions override earlier pasted briefs. When they conflict,
  follow the direct instruction and say so.

## When to Stop and Ask for Help

**STOP executing immediately when:**
- Hit a blocker (missing dependency, test fails, instruction unclear)
- Plan has critical gaps preventing starting
- You don't understand an instruction
- Verification fails repeatedly

**Ask for clarification rather than guessing.**

## When to Revisit Earlier Steps

**Return to Review (Step 1) when:**
- Partner updates the plan based on your feedback
- Fundamental approach needs rethinking

**Don't force through blockers** - stop and ask.

## Remember
- Review plan critically first
- Follow plan steps exactly
- Don't skip verifications
- Reference skills when plan says to
- Stop when blocked, don't guess
- Never start implementation on main/master branch without explicit user consent
