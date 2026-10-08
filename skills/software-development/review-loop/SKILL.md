---
name: review-loop
description: Self-review with correction cycles after implementation.
triggers:
  - review
  - verify
  - check
  - audit
  - inspect
---

# Review Loop Skill

> **Source:** Extracted from Anthropic and amp-code self-review patterns.

## When to Use

After any non-trivial code change, before declaring completion.

## Workflow

### Step 1: Self-Review Checklist
- Correctness: Does it do what it should?
- Safety: Any side effects or data loss?
- Completeness: Are all cases handled?
- Style: Does it match project conventions?
- Tests: Are there tests? Do they pass?

### Step 2: Identify Issues
If issues found, create a fix plan.

### Step 3: Execute Fix
Apply the fix.

### Step 4: Re-Review
Run the checklist again.

### Step 5: Repeat
Up to 3 cycles. If issues persist after 3 cycles, escalate to user.

### Step 6: Declare Verified
All clear → mark complete.

## Output

Verified result or escalation with specific unresolved issues.