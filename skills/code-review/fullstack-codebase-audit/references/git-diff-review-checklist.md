# Git Diff Code Review Checklist

Use this when reviewing a git diff (changed files, not a whole codebase).  
Targets 6 specific axes to produce a severity-ranked report with file+line findings.

## Workflow

1. **Scope** — `git diff --stat` to see file count and change size
2. **Read diffs in batches** — group by layer (actions, components, pages, styles)
3. **Verify against live files** — read current state of key files to cross-reference removals
4. **Grep for orphaned functions** — confirm removed exports have no remaining callers
5. **Report** — severity-ranked table with file:line for every finding

## Six-Axis Checklist

### 1. Silent Failures
- Empty `catch {}` blocks (dead code — JS Date methods never throw)
- Supabase `.delete()` / `.update()` result not checked before returning `{ success: true }`
- `revalidatePath` / `router.push` / `window.location.reload` called even when the preceding action returned an error
- Dynamic imports with `.then()` that discard the result on error

### 2. Type Issues
- `as any` on supabase client or joined query results
- `useState<any[]>([])` — loses type safety on list state
- `parseFloat(form.get("x") as string)` — empty/non-numeric input → NaN sent to DB
- `(t as any).categories?.name` — bypass of joined query types

### 3. Duplicate / Dead Code
- Same function defined in two files (e.g. `getEntities()` in both accounts/ and business/ actions)
- Imports of functions that were removed from the source module
- Exported functions that nothing imports anymore (check with grep)
- Dynamic import could be a static import (check if it's used in only one call site)

### 4. Imports
- Unused imports after a refactor (check every icon, util, and component import)
- Missing new imports for functions/types added in the diff
- Import of `CardHeader` / `CardDescription` that's no longer rendered
- `parseISO` or other date-fns functions no longer called

### 5. getEntity() / Entity Scoping Pattern
- Every server action must call `getEntity()` and handle both branches:
  ```ts
  const entity = await getEntity();
  if ("error" in entity) return null;  // or [], { error }, etc.
  const { supabase, entityId } = entity;
  ```
- All DB queries must use `entityId` (not a hardcoded value, not `localStorage`)
- `exportTransactionsCSV(entityId?)` should fall back to `getEntity()` when no id is passed

### 6. Runtime Errors
- `Number(null)` / `Number(undefined)` → 0, but `Number("")` → 0 and `Number("abc")` → NaN
- `toLocaleString()` on null/undefined throws
- `new Date(badString)` returns Invalid Date, `toLocaleDateString()` returns "Invalid Date"
- Dynamic Tailwind classes (`text-${color}-600`) — these are stripped by the Tailwind v4 JIT
- Hardcoded `$` currency symbol mixed with new `formatCurrency()` — regex replacements on hardcoded strings can miss edge cases

## Report Format

| Severity | Meaning |
|----------|---------|
| 🔴 Bug | Runtime-impacting (NaN insert, wrong data, broken user flow) |
| 🟠 Silent failure | Error swallowed, caller told "success" but data wasn't touched |
| 🟡 Type issue | `any`, unsafe cast, untyped state, dead catch |
| 🟣 Dead/dup code | Unused function, duplicate import, orphaned export |
| 🔵 Import | Missing/incorrect/removed import |
| 🟢 getEntity() | ✅ correct or ❌ incorrect usage |
| ⚠️ Minor | Style, narrow browser support, unnecessary verbosity |

End with a summary table:

```
| Severity | Count | Key issues |
|----------|-------|------------|
| 🔴 Bug   | 4     | NaN insert, threshold mismatch, … |
| 🟠 Silent | 3     | Delete result unchecked, … |
```

## Example Output

> **🔴 Bug 1: HealthScore label/color threshold mismatch**
> *File:* `src/features/accounts/components/AccountsPage.tsx`, lines 170–171
> Label uses 80/60/40 thresholds, color uses 70/40. Score 65 shows "Good" with amber.
>
> **🟠 Silent failure 2: deleteAccount ignores Supabase result**
> *File:* `src/features/accounts/actions.ts`, line 23
> `await supabase.from("accounts").delete()...` — no `const { error } =` check, always returns success.
