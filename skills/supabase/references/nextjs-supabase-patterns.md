# Next.js + Supabase Patterns: Pitfalls & Techniques

## Server Actions

### Don't use `redirect()` in imperatively-called actions
`redirect()` throws `NEXT_REDIRECT`. When called from an `onSubmit` handler (not form `action` prop), the throw is unhandled → silent failure.
**Fix**: Return `{success: true}` and let the client `router.push("/dashboard")`.

### Merge parallel actions to reduce round trips
Dashboard calling 8 server actions in `Promise.all` = 8 round trips. Merge into one `getDashboardData()` that does internal `Promise.all` for DB queries. One HTTP call, not eight.

### React.cache() for entity/context resolution
When every server action independently calls `getEntity()` (auth + entity lookup), wrap with `React.cache()`. One auth call per request shared across all server actions on the page:
```ts
import { cache } from "react";
export const getEntity = cache(async (): Promise<EntityResult> => { ... });
```

### Return structured errors, never throw
Server actions should return `{error: string}` or `{success: true}`, never throw. Thrown errors propagate as unhandled rejections in client components. Makes error handling predictable.

## Supabase

### Trigger fragility in auth schema
Postgres triggers on `auth.users` can fail silently (500 "Database error saving new user") due to schema permissions. Move entity/category creation to the `signUp` server action in app code — more reliable, better error surfacing.

### Migration deployment via Management API
The Management API `/database/query` endpoint only runs ONE statement per call. For multi-statement migrations:
- Split on semicolons
- Run each separately
- Use `DO $$ BEGIN ... EXCEPTION WHEN duplicate_object THEN NULL; END $$` for idempotent policies/triggers
- `CREATE POLICY IF NOT EXISTS` is NOT valid PostgreSQL syntax

### Data seed pattern
Use service role key to bypass RLS. Batch insert arrays, not per-row loops. For signup-triggered seed data, do it in the app's `signUp` action alongside entity creation.

## TypeScript

### @ts-expect-error vs as any
When you use `as any` to cast a joined Supabase result, the `@ts-expect-error` directive is unused (the cast already suppresses the error) and the build fails. Just use `(t as any).categories?.name` — the cast is self-documenting.

### Recharts type safety
Recharts callbacks (`label`, `formatter`, `Tooltip`) use broad union types that conflict with explicit parameter types. Use `(p: any)` or `(v: any)` — this is a known Recharts TS limitation, not a code smell.

## SSR / Client Components

### localStorage SSR guard
Client components using `localStorage` crash during SSR (`ReferenceError: localStorage is not defined`). Always guard:
```ts
// In useState initializer (lazy init):
useState(() => typeof window !== "undefined" ? localStorage.getItem("key") : "")

// In handler/effect:
const val = typeof window !== "undefined" ? localStorage.getItem("key") : "";
```

## Performance

### Loading skeletons beat blank screens
Add `loading.tsx` to every route. Animated pulse skeletons make data loading feel instant even if the API takes 500ms. One file per route.

### Client components skip loading.tsx
Pages that are `"use client"` render a blank screen, THEN fetch data, THEN update. The `loading.tsx` never shows because the page renders immediately (no SSR data fetch). Consider wrapping in a Suspense boundary or using a server component wrapper.
