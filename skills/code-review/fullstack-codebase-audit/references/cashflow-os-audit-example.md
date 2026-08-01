# CashFlow OS Audit — Real-World Example

Full audit of a Next.js 16 / Supabase / Tailwind v4 / shadcn finance app.

## Findings Summary

| Severity | Count | Root cause |
|----------|-------|------------|
| Bug | 10 | Layer drift, silent errors, framework-version pitfalls |
| Quality | 6 | Stale types, disconnected state, UX shortcuts |
| Minor | 2 | Harmless `cache()`, zero unused imports |

## Top Bugs Found Per Methodology Step

### Step 1: Migrations → Types

009_schema.sql (migration 1) defined 5 tables. 3 more migrations added 6 more tables (investments, budgets, goals, accounts, transfers, ious, inventory, staff, stock_movements, net_worth_snapshots) + 3 ALTER TABLE ADD COLUMN. The types file at `types/database.ts` only covered the original 5 tables — zero awareness of the 6 newer tables.

### Step 2: Schema → Server Actions

Every server action called `getEntity()` which hardcodes `.eq("type", "personal")`. Migration 007 added `is_active BOOLEAN DEFAULT true` to entities — but `getEntity()` doesn't use it. Migration 006 added `currency` to entities — only `settings/actions.ts` and `dashboard/actions.ts` read it.

### Step 3: UI State → Server Handoff

The sidebar has an `EntitySwitcher` component that writes `selectedEntity` to `localStorage`. The Staff page reads from localStorage... but then calls `createStaffMember()` which internally calls `getEntity()` → personal entity only. Zero server actions ever read the localStorage value.

### Step 4: Silent Errors (the biggest pattern)

6 delete/update/toggle functions return `{ success: true }` without checking the Supabase error response. Example:
```ts
await supabase.from("accounts").delete().eq("id", id);
return { success: true };  // Supabase error? Doesn't matter.
```

### Step 5: Framework Pitfalls

- **Tailwind v4**: `text-${color}-600` in stat cards — silent no-op, classes never generated
- **Middleware**: auth guard lives at `src/proxy.ts` instead of `src/middleware.ts` — never executes
- **localStorage entity selector**: lost on browser clear, invisible to server actions

## What Wasn't Broken

- RLS policies are correct and consistent across all 8 migrations
- `use server` / `use client` boundaries are clean
- `getEntity()` shared abstraction pattern is good (just needs entityId param support)
- Client-side data fetching pattern (fetch in useEffect) is consistent
- Budget manager prevents duplicate budgets per category
- `Awaited<ReturnType<>>` for derived component types — clean
