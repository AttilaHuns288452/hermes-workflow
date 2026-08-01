# Parallel Bug-Fix Dispatch Pattern

When fixing 10+ bugs across 80 files in an existing app, dispatch DeepSeek V4
Flash agents **in parallel with non-overlapping file ownership**.

## When to Use

- 3+ independent bug clusters across different files
- None of the bugs require reading each other's changes
- Build passes before dispatch (you want it to pass after too)

This is distinct from [greenfield builds](greenfield-app-spec-template.md)
(one big spec → one agent) and [ECC review](#ecc-agent-dispatch) (read-only
N agents on the same diff). Here you are **writing** in parallel.

## File-Ownership Partitioning

The #1 risk with parallel write-agents is **edit conflict** — two agents
editing the same file, the second clobbering the first. Prevent it by
assigning **exclusive file sets** in the `context` field:

```
Agent 1 owns:  src/lib/currency.ts
               src/features/dashboard/actions.ts
               src/features/dashboard/components/DashboardPage.tsx
               src/app/layout.tsx
               src/app/globals.css
               src/features/business/actions.ts
               src/features/accounts/actions.ts
               src/app/staff/page.tsx

Agent 2 owns:  src/features/transactions/components/TransactionList.tsx
               src/features/budgets/components/BudgetManager.tsx
               src/features/goals/components/GoalsPage.tsx
               ...9 feature component files

Agent 3 owns:  src/components/layout/AppShell.tsx
               src/components/layout/AuthShell.tsx
               src/features/auth/components/LoginForm.tsx
               src/features/auth/components/SignUpForm.tsx
               src/features/accounts/components/AccountsPage.tsx
```

**Rule: every file an agent edits must appear in its "YOU OWN THESE FILES"
list, and no file appears in two agents' lists.**

If a shared dependency changes (e.g. `src/lib/currency.ts` adds a new
function that all feature components need to import), assign the dependency
file to ONE agent and tell the other agents to **import from** it — do not
let two agents edit the same lib file.

## Context Block Anatomy

Each agent's `context` field contains:

1. **"YOU OWN THESE FILES"** block — the explicit list, every file path
2. **"DO NOT EDIT any other files"** — one line, make it loud
3. **What other agents are doing** — one line so the agent knows not to
   touch their work ("Another agent is editing AppShell, AuthShell, …")
4. **Bug descriptions** — numbered, one per bug, with the root cause and the
   fix approach in 2-3 lines each
5. **Code patterns** — the shared pattern the agent should follow (e.g.
   "Server actions use `getEntity()` from `@/lib/entity.ts` which returns
   `{ supabase, entityId } | { error }`. Check `if ('error' in entity)`.")
6. **Build command** — `cd <path> && npm run build` as the last instruction

## Read-Before-Dispatch Discipline

The orchestrator must read **every file** before partitioning. If you skip
a file, you risk assigning it to two agents or leaving a bug unassigned.
The read pass is not optional — it is where you discover the cross-file
relationships that decide the partition.

Flow:
1. `find src -type f | sort` → file inventory
2. Read all server actions → understand the data layer
3. Read all feature components → understand the UI layer
4. Map bugs → files
5. Map files → agents (no overlaps)
6. Dispatch `delegate_task(tasks=[{goal, context}, …])`

## Post-Return Recovery

All three agents return as a single consolidated message. After that:

1. `npm run build` — if it fails, the error names the file, and you know
   which agent's work to inspect
2. Fix TypeScript errors inline (the orchestrator CAN fix minor TS issues —
   you are not writing feature code, just adjusting imports/types)
3. Files no agent owned (gaps in partitioning) → orchestrator patches
   using the same pattern the agents used (e.g. formatCurrency)
4. Dispatch MiMo for visual QA, ECC for code review — both in parallel
5. Deploy

## Signal: When NOT to Use This Pattern

- 1-2 patches → single `delegate_task`, no partitioning needed
- Bugs are causally linked (fixing A changes the interface B depends on) →
  serialize: fix A → build → fix B
-纯粹 visual polish with no logic changes → delegate to one agent or
  use MiMo for the audit and one DeepSeek for the fixes