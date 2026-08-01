# ECC Parallel Dispatch Workflow (from CashFlow OS session)

When a project reaches a checkpoint (pre-merge, post-feature-batch, pre-deploy), dispatch 2-3 ECC agents in parallel via `delegate_task`. Each gets the project context and a specific review goal.

## Proven dispatch combo

```ts
delegate_task(tasks=[
  { goal: "Review schema for RLS, indexes, constraints", context: "Project at ~/Documents/Projects/$PROJECT. Check migrations." },
  { goal: "Scan all .ts/.tsx for silent failures", context: "Project at ~/Documents/Projects/$PROJECT. Find empty catches, unhandled throws." },
  { goal: "Full code quality review", context: "Project at ~/Documents/Projects/$PROJECT. Check DRY, imports, patterns." },
])
```

## Agent-to-task mapping

| Agent | Use when | Typical findings |
|-------|---------|-----------------|
| `database-reviewer` | Migration ran, schema changed | Missing CHECK constraints, duplicate categories allowed, missing UNIQUE |
| `silent-failure-hunter` | New server actions, new components | Empty catch blocks, no try/catch in handlers, stuck loading states |
| `code-reviewer` | 3+ files changed | Duplicated getEntity(), unused imports, feature boundary violations |
| `build-error-resolver` | Build fails with TS error | Auto-fixes deprecation warnings, missing imports |

## Results handling

Each agent returns findings as a new message in the conversation. Apply fixes in priority order:
1. Schema issues (have migration risk if deferred)
2. Error handling gaps (can silently break UX)
3. Code quality (imports, DRY, patterns)

The dispatch itself costs nothing — they run in parallel background. The findings save hours of manual review.
