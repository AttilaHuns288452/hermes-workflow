---
name: coderabbit-code-review
description: "AI-powered code review using CodeRabbit. Finds bugs, security issues, and quality risks. Use for explicit review requests and autonomous review when needed."
---

# CodeRabbit Code Review

AI-powered code review using CodeRabbit. Groups findings by severity (Critical, Warning, Info).

## When to Use

- Review code changes / Review my code
- Check code quality / Find bugs or security issues
- Get PR feedback / Pull request review

## How to Review

### 1. Check Prerequisites

```bash
coderabbit --version 2>/dev/null || echo "NOT_INSTALLED"
coderabbit auth status 2>&1
```

If not installed: install from https://www.coderabbit.ai/cli
If not authenticated: `coderabbit auth login`

### 2. Run Review

```bash
coderabbit review --agent
```

**Options:**

| Flag | Description |
|------|-------------|
| `-t all` | All changes (default) |
| `-t committed` | Committed changes only |
| `-t uncommitted` | Uncommitted changes only |
| `--base main` | Compare against specific branch |
| `--base-commit <hash>` | Compare against specific commit |
| `--dir <path>` | Review specific directory |
| `--agent` | Agent-readable output + fix guidance |

### 3. Present Results

Group by severity and provide actionable fixes.
