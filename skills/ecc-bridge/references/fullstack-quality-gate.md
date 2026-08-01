# Parallel ECC Quality Gate — Proven Pattern

Proven in CashFlow OS session (2026-07-30). After building a full-stack Next.js + Supabase app, dispatched 3 ECC agents in parallel for review before shipping. Caught 38+ issues the primary builder missed, all fixed within ~15 minutes.

## Results

| Agent | Time | Issues | Key Finding |
|-------|------|--------|-------------|
| `database-reviewer` | 2m13s | 7 (0 critical) | Missing CHECK constraints on assets/debts, no UNIQUE on category names |
| `silent-failure-hunter` | 2m41s | 38 | Empty catch blocks, 17+ uncaught server action throws, missing try/catch in every component handler |
| `code-reviewer` | 2m49s | 14 | `getEntity()` duplicated identically in 4 files, unused imports, `as any` casts |

## Dispatch Pattern

```ts
delegate_task(tasks=[
  {
    goal: "Review the database schema for RLS correctness, missing indexes, constraints",
    context: "Project: <path>. Check supabase/migrations/*.sql. Focus on RLS, cascades, CHECK constraints."
  },
  {
    goal: "Scan the codebase for silent failures, unhandled errors, swallowed exceptions",
    context: "Project: <path>. Check all .ts/.tsx files. Focus on empty catch blocks, unhandled promises, missing error states, server action throws."
  },
  {
    goal: "Full code quality review — DRYness, TypeScript safety, React patterns, import hygiene",
    context: "Project: <path>. Check all source files. Focus on duplicated code, any casts, unused imports, naming, feature boundary violations."
  },
])
```

## Root-Cause Cascade (Key Insight)

Both `silent-failure-hunter` and `code-reviewer` independently flagged the same root cause: `getEntity()` duplicated identically in 4 action files, each throwing raw errors instead of returning structured `{ error: string }` objects. Extracting to a shared `src/lib/entity.ts` with structured returns resolved 20+ issues in one change — the silent-failure-hunter's top cluster (17 uncaught throws) evaporated.

**Fix root causes first.** One shared function extraction cascades to resolve dozens of reported issues.

## Agent → Quality Dimension Mapping

| Agent | What it catches best | Skip if... |
|-------|---------------------|------------|
| `database-reviewer` | RLS gaps, missing CHECK/UNIQUE, FK cascade issues, missing indexes | No database changes |
| `silent-failure-hunter` | Empty catches, unhandled promises, missing error states, unsafe type casts | Purely read-only code |
| `code-reviewer` | DRY violations, import hygiene, React anti-patterns, naming inconsistency | Single-file changes |
| `build-error-resolver` | Unused imports, deprecation warnings, missing keys, strict type errors | Build already passes cleanly |

## What we skipped (deliberate, not oversight)

- Recurring transaction cron engine — add when 10+ entries/week
- Stock market API — add when user provides Finnhub/Alpha Vantage key
- Business mode UI — entities table exists, UI deferred to v2
- AI assistant — add when data model is stable with 6+ months of real data
- Financial calendar — date picker on transactions covers 80% of need
- Document vault — Supabase storage exists, no user has asked for it

The `build-error-resolver` is lowest priority. If `npm run build` exits 0, skip it. The other three always run for non-trivial builds.
