---
name: fullstack-codebase-audit
description: Audit a full-stack codebase end-to-end — read server actions, migrations, types, and components; cross-reference for drift; trace UI state to server actions; identify disconnected features and silent failures.
---

# Full-Stack Codebase Audit

When reviewing a full-stack codebase (not a single PR diff), read and cross-reference every layer. Single-PR review techniques miss drift between layers.

## Flow

Read levels in this order — each reveals what the previous one hid:

1. **Schema / Migrations** — what the DB actually enforces
2. **Types** — what the app *thinks* the DB looks like
3. **Server Actions** — what the app queries and writes
4. **UI Components** — what the user sees and triggers
5. **Routing / Config** — what runs and what doesn't

## Cross-Reference Checks

### Schema → Types mismatch
Read the latest migration and grep for each table there in the types file. Flag missing type definitions. Common pattern: 4 migrations added 6 new tables, types file has only the original 2.

### Schema → Server Actions mismatch
For every `.from("table_name")` in server actions:
- Does the migration define that table?
- Are the columns being selected/inserted present in the migration? A join column like `status` or `submitted_by` that was added in a later migration but used by an earlier-server-action pattern.
- Are CHECK constraints being enforced by the app, or will the DB reject a write? (e.g. `amount > 0` check but action uses `parseFloat` with no validation)

### Server Actions → Types mismatch
Do the action signatures reference columns or joins that the types file doesn't model? Flag `as any` casts on joined data — they're usually a type-blindness signal.

### UI State → Server Action handoff
Trace the complete flow of any "scope" or "entity" selector:
1. Where is the selected value stored? (localStorage? React state? URL param?)
2. Is that value **actually passed** to the server action?
3. Does the server action **read from the same source** the UI wrote to?

Example of disconnected: UI writes entity ID to `localStorage`, page reads it from there and passes to component, but the server action internally calls `getEntity()` which hardcodes `type='personal'` — the UI selection is cosmetic.

### Static files that don't run
Next.js: middleware must be `src/middleware.ts`. A file at `src/proxy.ts` with a `config.matcher` that's never imported is dead code. Check next.config.ts for imports/external rewrites.

## Silent Error Patterns

Look for server actions that call `supabase.from("x").delete()` or `.update()` and **immediately** return `{ success: true }` without examining the returned `error` object. These are the most common source of false-positive UX.

Specific patterns to grep:
```
supabase\.from\(\"[\w_]+\"\)\.delete\(\)\.eq\(\"id\"[\s\S]{0,50}\)\n\s+return \{ success: true \}
```

If the delete/update returns a Supabase error (RLS violation, FK constraint), the user sees "success" but the data was not touched.

## Micro-Level Code Quality Patterns

In addition to cross-layer drift, audit for surface-level quality patterns that compound into tech debt. These won't show up in a typechecker or build step.

### `as any` Casts on Joined Data

Grep for `as any` in server actions and components. Count them. Most common cause: `.select("..., categories(name)")` returns a typed result, but accessing `.categories?.name` forces a cast because the joined type isn't modeled. The number of `as any` casts is a codebase health signal — >5 in a single-feature app means a type helper is overdue.

### Empty catch blocks & silent error handlers

Three levels to audit:

1. **Empty catch** — `} catch {` with no body. Grep: `catch\s*\{` then check for empty braces in context. These suppress all errors unconditionally.
2. **Typed catch** — `catch (e: any)` — redundant annotation (TypeScript infers `unknown`). Prefer `catch (e: unknown)` with `instanceof Error` guard.
3. **Console-only catch** — `catch (e) { console.error(...) }` — silently swallows production errors. Acceptable for third-party API fallbacks (market-data, weather, etc.) where the fallback is a null return. Flag it when the function continues as if the operation succeeded.

### Unhandled Promise Rejections in Effects

Grep for `.then(` in `useEffect` blocks. Every `.then()` chain without a `.catch()` is an unhandled rejection waiting to happen. Even if the underlying async function has internal try/catch, a future refactor that removes one creates a silent failure.

Auto-fix: append `.catch(console.error)` — not perfect, but ensures rejections are visible.

### useEffect Dependency Completeness

Every `useEffect` with `[]` deps that references a component-local function or variable is technically stale. The common pattern:

```tsx
const fetch = async () => { ... };
useEffect(() => { fetch(); }, []);
// ESLint react-hooks/exhaustive-deps warns: fetch is not in deps
```

For mount-only calls, this is functionally correct but a lint-suppression comment (or wrapping with `useCallback`) clarifies intent. Flag it during audit.

### Naming Convention Red Flags

- **One-letter state variables** (`[n, setN]`, `[t, setT]`, `[b, setB]`) in component body — they're grep-hostile and fail the "readable without help" test.
- **Duplicate import with alias** (`Plus as PlusIcon`) — signals a naming collision that should be resolved at the import source or through a wrapper.
- **Unused imports** — check each file's import list against its JSX and expression references. Particularly common: UI library imports (`CardHeader`, `CardTitle`) hoisted during copy-paste but never used in the component body.

### Auth Flow Audit

In Next.js App Router apps, trace the full auth path:

1. **Root page**: Does it check auth before redirecting? A bare `redirect("/dashboard")` with no `getUser()` check means unauthenticated users see a loading flash before hitting the error state.
2. **Middleware**: Is there a `src/middleware.ts` protecting routes? Any file named `middleware.ts` at a *different* path (e.g. `src/proxy.ts`, `lib/auth-guard.ts`) is dead code — Next.js only reads middleware from the canonical location.
3. **Server-side vs client-side auth**: Are both checked? Server actions should call `getUser()`, but the UI should also handle the case where the server responds with `{ error: "Not authenticated" }`.
4. **Duplicate client instances**: Is `createBrowserClient(...)` called in multiple locations? Extract a shared helper.

## Framework-Specific Pitfalls

### Tailwind v4
Dynamic class construction (`text-${color}-600`) does NOT work. Tailwind v4 uses static analysis — every class string must be a complete literal. Grep for template literals in className attributes. The classes silently don't generate.

### Next.js Middleware
Middleware ONLY runs from `src/middleware.ts` (or project root `middleware.ts`). A file with the middleware pattern at any other path is dead code. The route protection isn't running.

### React `cache()` on Server Actions
`cache()` from React works only within a single render pass. Each server action (`"use server"`) invocation is a separate HTTP request — the cache is fresh per call. Wrapping `getEntity()` in `cache()` is harmless but does nothing.

### LocalStorage for cross-request state
Values written to `localStorage` in a client component are invisible to server actions, lost on browser clear, and absent in incognito. Flag any localStorage-based "current workspace" or "current entity" mechanism — it's disconnected by design from the backend.

## Stale Type Detection

If the migrations end at `008_*.sql` and the types file covers only the first 2 tables (entities, categories, transactions, assets, debts), the type system is lying. Every migration that adds a table or column without updating the types file creates a blind spot.

## Git Diff Review

For focused review of a git diff (not a whole codebase), see `references/git-diff-review-checklist.md`. It covers the 6-axis checklist, severity-ranked reporting format, and concrete example output.

## Verification

After the audit, `npm run build` or `tsc --noEmit` catches type-level issues. It will NOT catch:
- Dynamic class name generation (Tailwind v4)
- Dead middleware files
- localStorage/server-action state disconnect
- Silent error return values
- `as any` casts on joined data (TypeScript allows them)
- Empty catch blocks
- `.then()` without `.catch()` in effects
- Naming convention issues
- One-letter state variables
