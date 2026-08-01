# ECC Agent Dispatch Protocol — Proven Pattern (CashFlow OS session)

## The Pattern

For ANY codebase change, dispatch at least 2 ECC agents in parallel via `delegate_task`. Agents complete independently and results arrive as new messages.

```ts
// Pseudocode — orchestrator dispatches
delegate_task(tasks=[
  { goal: "Review schema for RLS correctness, missing indexes, constraint gaps" },
  { goal: "Scan codebase for silent failures, swallowed exceptions, missing error states" },
  { goal: "Full code quality review — DRY, TypeScript safety, React patterns, imports" },
])
```

## Which Agents When

| Change Type | Agents to Dispatch | Rationale |
|-------------|-------------------|-----------|
| Schema change / migration | `database-reviewer` + `silent-failure-hunter` | Schema correctness + error paths |
| Feature code (UI + actions) | `code-reviewer` + `silent-failure-hunter` | Code quality + error handling |
| Build/TS issues | `build-error-resolver` + `code-reviewer` | Fix errors + prevent regressions |
| Full PR / deploy | All 3: `database-reviewer` + `code-reviewer` + `silent-failure-hunter` | Defense in depth |
| Pure UI (no server actions) | `code-reviewer` | Lighter touch |

## Results (CashFlow OS — real findings)

3 agents dispatched in parallel found:
- **database-reviewer**: 0 high, 2 medium (missing CHECK constraints on debts/assets, duplicate category names possible)
- **silent-failure-hunter**: 38 issues (empty catch blocks, uncaught throws from server actions, no try/catch in 15+ component handlers, signup silently failing)
- **code-reviewer**: 14 issues (5 copies of `getEntity()` duplicated, unused imports, N+1 query pattern, `as any` casts)

**All fixed in <30 minutes.** Without ECC, most of these would have shipped.

## Pitfalls

- Don't wait for agents synchronously — dispatch and continue working
- Agent results arrive as new messages, not direct returns
- Subagents have no memory of the conversation — pass full context
- 600s timeout per agent — break large reviews into focused scopes
- Agents may revert each other's fixes if dispatched concurrently on the same files — use sequential dispatch for overlapping file sets
