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

### Migration × App Contract (combined-diff review)

When one diff ships a migration that tightens RLS together with app changes, the mismatch lives BETWEEN them — neither file shows it alone. For every column a new/changed policy constrains (e.g. INSERT `WITH CHECK status='pending' OR role='owner'`), grep the server actions for the values they actually insert/update. App-derived values (`status: canApprove(role) ? "approved" : "pending"`) can violate the new policy for a middle role (managers) the policy author forgot — the write is rejected at runtime with a raw RLS error and no test catches it. Same for UPDATE policies: a new `WITH CHECK` on a column the app's update path legitimately flips breaks that flow if no other policy covers it. This is the app-side sanity check owed when a DB migration ships in the same sprint.

### Design-Sweep Regressions (theming)

A sweep that swaps hardcoded colors for `var(--*)` tokens can break the OTHER theme mode:

- Background switched to `var(--card)` (white in light mode) while inner text/bubbles stay hardcoded `text-white` / `bg-white/10` → white-on-white in light mode. A panel that was pinned dark with hardcoded white text needs a pinned dark surface or var-driven text. Check both theme modes, not just the one the screenshots show.
- Verify swept classes resolve: `text-red`, `bg-green-soft`, `border-green/30` only exist if `globals.css` maps `--color-*` in Tailwind v4 `@theme`. Grep the token file instead of trusting class names.

### Failure-Path Guard Consistency & Stale Guards

- All failure branches of one load path must use the SAME guard: a `catch` that only sets error when `!initialData` while the sibling `if (!data)` branch sets it unconditionally means a transient background refetch replaces valid SSR data with the error screen.
- Stale-response guard key: the request-id should BE the query parameter (date/filter) so same-key responses are interchangeable and a newer key supersedes. Verify the guard is checked on success, error, AND finally paths (skipping it on one path leaves `setLoading(false)` clobbering a newer load).

### Efficient Large-Diff Review

- Kick off `npx tsc --noEmit` in the background FIRST; dump `git diff HEAD > /tmp/x.diff` and page it in chunks while tsc runs.
- After reading the diff, grep every caller of each function whose shape changed (`grep -rn "fnName" src`, excluding the definition). Union-return changes (`{ error } | data`) only break callers the type system can't see — `as any`, `Extract<Awaited<...>>` gymnastics, callers treating `[]`/null as the only failure shape. Verify each caller handles both branches.
- Output contract for gate reviews: VERDICT (APPROVE / REQUEST_CHANGES) + numbered findings `severity | file:line | issue | one-line fix`, then a "verified clean" list of what was checked and passed.

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
4. **Dead error state** — `.then(...).catch(() => setErr(true))` wired around a function that can never reject (server actions that swallow errors and return `[]`/null). The error UI is unreachable — failures surface as an empty state instead. Before trusting any `.catch(() => setError())`, confirm the called function actually throws on failure.

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

### Conditional Hooks After Early Returns

The crash the typechecker can't see. Grep each component body for early returns (`if (loading) return`, `if (error) return`) and count hooks on each side:

```tsx
if (loading) return <Skeleton />      // 23 hooks called
if (error) return <ErrorCard />       // still 23
const stats = useMemo(...)            // 27th hook — only runs on happy-path renders
```

Hook count/order must be identical on every render. Early returns before later hooks make the count vary → React throws **"Rendered more hooks than during the previous render"** the moment the loading/error branch renders (mount with `initialData=null`, or an error → "Try again" retry path that sets `loading=true` then completes). Verified in practice: `tsc --noEmit` AND eslint-config-next's react-hooks v6 rules BOTH miss this pattern — only manual hook counting catches it. Fix: hoist the `useMemo`/`useState` calls above the early returns, or move the early-return branches into a child render helper.

### React 19 Lint Rules (eslint-config-next, react-hooks v6)

`npx eslint <changed files>` now surfaces rules tsc never sees — triage them:

- `react-hooks/refs` — `ref.current = x` during render ("latest ref" pattern). Real lint error; in most cases the simpler fix is folding the value into `useCallback` deps (`useCallback(fn, [currency])`) — the ref exists to stabilize identity that the deps array already provides.
- `react-hooks/set-state-in-effect` — flags mount-sync patterns (localStorage restore, `setLoading(false)` after initializing from props). Usually benign/correct; the canonical fix is `useSyncExternalStore` or dropping the redundant line.
- `react-hooks/purity` — flags `Date.now()`/`Math.random()` in any function defined in render scope, including **event handlers** (false positive — handlers are not render). Suppress with a comment rather than "fixing" it.
- `@typescript-eslint/no-explicit-any` on joined data (`.categories?.name`) — real error; fix with a one-interface join type, not a lint disable.

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

### MCP Streamable HTTP Routes (Next.js route handlers)

Checklist for `/api/mcp` JSON-RPC 2.0 endpoints:

- **Auth before body parse** — 401 with a JSON-RPC error (`{code:-32001}`), never HTML.
- **Notifications** (no `id`, or `id: null`) must get NO response — in both the single-message path and the batch path (drop from array; empty batch → 202/204 with empty body). A `case "tools/call": return handleToolCall(m.id, ...)` that ignores the notification flag replies to notifications — spec violation.
- **Error codes** — -32700 parse, -32600 invalid request, -32601 method not found, -32602 invalid params; invalid-request responses use `id: null`. `id ?? null` must be nullish coalescing, not `||` (id `0` is legal).
- **Tool failure signaling** — `isError: true` + `content:[{type:"text", text: JSON.stringify(...)}]` for null/undefined/`{error}` results and thrown errors. A `typeof result === "object" && "error" in result` check is safe only because null is excluded first — `in` on a non-object throws.
- **Bearer→cookie injection** — injecting a session cookie so downstream server actions run authenticated relies on Next's `RequestCookies.set()` mutating the per-request store AND @supabase/ssr reading cookies lazily via `getAll()` (clients created before injection still see it). Works today, silently fragile on Next upgrades — flag for a comment pinning both invariants.
- **CORS** — `Access-Control-Allow-Origin: *` + bearer token is fine (no credentials mode); cookie auth stays CSRF-safe only with `SameSite=Lax` and no `Access-Control-Allow-Credentials`.
- **Rate limit `tools/call`** — it's an authenticated DB-query surface; if sibling routes (e.g. `/api/ai/chat`) have a sliding-window limiter and MCP doesn't, that's a finding.
- **Arg clamping** — `Math.floor(Number(v)) || dflt` swallows valid `0` (limit=0 becomes the default). Use `Number.isFinite(Number(v)) ? clamped : dflt`.

## Stale Type Detection

If the migrations end at `008_*.sql` and the types file covers only the first 2 tables (entities, categories, transactions, assets, debts), the type system is lying. Every migration that adds a table or column without updating the types file creates a blind spot.

## Git Diff Review

For focused review of a git diff (not a whole codebase), see `references/git-diff-review-checklist.md`. It covers the 6-axis checklist, severity-ranked reporting format, and concrete example output.

For a worked React/TS + MCP route review pass (hook-counting, lint triage, severity table), see `references/react-ts-hooks-mcp-review.md`.

## Verification

After the audit, run `tsc --noEmit` AND `npx eslint <changed files>` (lint catches `no-explicit-any` and the react-hooks v6 rules tsc misses — but triage its false positives, see "React 19 Lint Rules" above). `npm run build` or `tsc --noEmit` catches type-level issues. It will NOT catch:
- Dynamic class name generation (Tailwind v4)
- Dead middleware files
- localStorage/server-action state disconnect
- Silent error return values
- `as any` casts on joined data (TypeScript allows them)
- Empty catch blocks
- `.then()` without `.catch()` in effects
- Conditional hooks after early returns (verified: both tsc and eslint miss it — count hooks manually)
- Naming convention issues
- One-letter state variables

Host quirk: on this Windows host, `search_files`/ripgrep can fail on project paths with "IO error ... cannot find the path" — fall back to terminal `grep -n` (works; the read/search tools and shell disagree on path translation).
