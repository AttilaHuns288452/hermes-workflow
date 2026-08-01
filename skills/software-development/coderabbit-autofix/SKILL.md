---
name: coderabbit-autofix
description: "Fetch unresolved CodeRabbit review-thread feedback for current PR branch and apply validated fixes with explicit approval."
---

# CodeRabbit Autofix

Fetch unresolved CodeRabbit review-thread feedback for your current branch's PR and apply validated fixes with explicit approval.

## Prerequisites

- `gh` (GitHub CLI) — `gh auth status`
- `git`
- Git repo on GitHub, current branch has open PR
- PR reviewed by CodeRabbit bot

## Workflow

### Step 1: Check Git State

```bash
git status
```

If uncommitted changes: warn and ask to commit first.
If unpushed commits: warn and ask to push first, then exit (CodeRabbit needs ~5 min).

### Step 2: Resolve PR

```bash
pr_number=$(gh pr list --head "$(git branch --show-current)" --state open --json number --jq '.[0].number')
```

If no PR: ask to create one, then exit.

### Step 3: Fetch CodeRabbit Feedback

```bash
pr_number=$(gh pr view --json number --jq '.number')
owner=$(gh repo view --json owner --jq '.owner.login')
repo=$(gh repo view --json name --jq '.name')
```

Fetch review threads via GitHub GraphQL, filter for CodeRabbit comments with suggestions.

### Step 4: Apply Fixes Per-Thread

For each unresolved thread:
1. Present the issue and proposed fix
2. Ask for approval
3. Apply the fix
4. Track in a session task list

### Step 5: Finalize

Commit applied changes with descriptive message per fix.
