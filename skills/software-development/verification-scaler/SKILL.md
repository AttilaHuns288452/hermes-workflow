---
name: verification-scaler
description: Risk-based verification selection for code changes.
triggers:
  - verify
  - test
  - validate
  - check
  - ensure
---

# Verification Scaler Skill

> **Source:** Extracted from amp-code risk-based verification.

## When to Use

After any code change before declaring done.

## Verification Levels

### Level 0: No Verification
- Typo fixes
- Comment changes
- Formatting changes

### Level 1: Targeted Check
- Run affected file(s)
- Check behavior manually
- Run focused test if available

### Level 2: Full Test Suite
- Run all tests
- Typecheck
- Lint
- Build

### Level 3: Comprehensive
- Level 2 + integration tests
- Browser QA if UI
- Regression check

## Decision Rules

- Typo fix → Level 0
- Single function change → Level 1
- Cross-module change → Level 2
- Architecture change → Level 3
- Shared/global code → Level 2-3

## Output

Verification result with evidence.