---
name: silent-failure-audit
description: Systematically hunt silent failures — unhandled errors, unchecked query/mutation responses, empty catch blocks, promise swallows, missing UI error states. Scan any codebase for bugs that don't crash but produce wrong state, infinite loaders, or silent data loss.
---

# Silent Failure Audit

## Overview

Silent failures are bugs that don't crash the app but silently produce wrong results, incomplete state, or infinite loading spinners. They're the most insidious class of bug — no crash, no error log, just wrong behavior. This skill provides a systematic methodology and pattern catalog for hunting them.

**The key insight:** Silent failures fall into a small set of repeatable patterns. Once you know what to grep for, you can scan a whole codebase in minutes.

## When to Use

- Before shipping a feature (especially one with async data flows)
- After adding new server actions or API routes
- When investigating reported "data doesn't save" or "page hangs" bugs
- Any codebase with async database/API mutations
- Code review of data-heavy CRUD features
- When onboarding to a new codebase (establish a baseline)

## Not for

- Logic bugs (wrong algorithm, off-by-one) — use `code-review-and-quality`
- Performance issues — use `performance-optimization`
- Security vulnerabilities — use `security-and-hardening`

## The Hunting Method

### Step 1: Map the data flow

Identify every server action, API route, and mutation handler in the codebase:

```
grep -rn "\"use server\"" src/ --include="*.ts" --include="*.tsx"
grep -rn "export async function.*\(.*\)" src/features/*/actions.ts
```

### Step 2: Find unchecked mutations

Search for DB/API writes that never check the response `error` field:

```bash
# Find ALL supabase mutations (regardless of error handling)
grep -rn "await supabase" src/ --include="*.ts" --include="*.tsx"

# Find mutations that DO check errors
grep -rn "await supabase" src/ --include="*.ts" --include="*.tsx" | grep "const.*error"

# Find the unchecked ones (no error destructuring near the mutation)
grep -rn "await supabase" src/ --include="*.ts" --include="*.tsx" | grep -v "const.*error" | grep -v "// ponytail"
```

### Step 3: Find `.single()` calls without error handling

Supabase `.single()` returns `{ data, error }` — it doesn't throw. Code that only destructures `data` silently discards query errors:

```bash
grep -rn "\.single()" src/ --include="*.ts" --include="*.tsx"
```

Check each occurrence: is the `error` field destructured and handled? If only `data` is used, the caller gets `null` data on any error (no rows, multiple rows, DB failure) with no feedback.

### Step 4: Find `.then()` chains without `.catch()`

Async promise chains in React `useEffect` that use `.then()` but no `.catch()` will silently swallow rejections, leaving the component in an infinite loading state:

```bash
grep -rn "\.then(" src/ --include="*.tsx" --include="*.ts"
```

Check each: does it have a `.catch()`? If not, what happens on rejection? If the `.then()` sets `loading(false)`, a rejection means the spinner never goes away.

### Step 5: Find client-side handlers that ignore server action return values

Server actions often return `{ error: "..." }` or `{ success: true }`. Client handlers that `await` the action but never check the return value silently confirm failed operations:

```bash
grep -rn "await.*Action\|await create\|await delete\|await update" src/features/*/components/ --include="*.tsx"
```

For each: is the return value checked for an `error` property? Or does the handler close the dialog / clear the form / refresh the list unconditionally?

### Step 6: Find missing UI error states

Components with async data fetches need three states: loading, empty, and error. Search for components that only have loading + empty:

```bash
grep -rn "loading\|Loading" src/features/*/components/ --include="*.tsx" | grep -v "error\|Error"
```

A component with `loading` state but no `error` state will hang forever if the async fetch rejects.

### Step 7: Verify build!

```bash
npm run build 2>&1 | tail -10
# or: npx tsc --noEmit
```

A build failure on top of silent failures means you're fixing in the dark.

## Silent Failure Patterns

See `references/silent-failure-patterns.md` for a detailed pattern catalog with concrete code examples and grep queries per pattern.

## Severity Classification

| Severity | Description | Example |
|----------|-------------|---------|
| 🔴 **High** | Data loss or corruption risk | Unchecked DB mutation always returns `{ success: true }` even on failure |
| 🔴 **High** | Promise rejection kills component | `.then()` without `.catch()` leaves infinite loading spinner |
| 🟡 **Medium** | Silent UX failure | Dialog closes but server action failed — user sees no error |
| 🟢 **Low** | Data degradation | Bad query returns fallback value (e.g. "USD" currency) when real data available |

## Verification

After fixing silent failures:

- [ ] Each unchecked mutation now reads and propagates the `error` field
- [ ] Each `.single()` call checks `error` before using `data`
- [ ] Each `.then()` chain has a `.catch()` handler
- [ ] Each client handler inspects server action return values
- [ ] Each async view has loading, empty, and error states
- [ ] Build passes cleanly (`npm run build` or equivalent)
