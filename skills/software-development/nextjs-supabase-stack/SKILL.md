---
name: nextjs-supabase-stack
description: Patterns, pitfalls, and workflows for building Next.js (App Router) + Supabase (Postgres + Auth + RLS) full-stack apps. Use when scaffolding, debugging, or adding features to any Next.js + Supabase project.
triggers:
  - Next.js + Supabase
  - nextjs supabase
  - Supabase auth Next.js
  - server actions Supabase
  - RLS Next.js
  - createBrowserClient createServerClient
---

# Next.js + Supabase Stack

Production patterns and pitfalls from building full-stack apps with Next.js 15+ (App Router) and Supabase.

## Supabase Project Setup

### CLI auth (token required)
```bash
npx supabase login                    # interactive (PTY needed)
npx supabase login --token <sbp_...>  # CI/non-interactive
```
Get tokens at: https://supabase.com/dashboard/account/tokens

### Create project
```bash
npx supabase orgs list  # get org ID
npx supabase projects create <name> --org-id <id> --region ap-southeast-1 --db-password <pw>
```

### Get API keys
```bash
npx supabase projects api-keys --project-ref <ref>
```
Or via Management API:
```bash
curl -s "https://api.supabase.com/v1/projects/<ref>/api-keys" -H "Authorization: Bearer $SUPABASE_ACCESS_TOKEN"
```

### Auth config for MVP (no email confirmation)
Patch auth config to skip email verification for v1:
```bash
curl -X PATCH "https://api.supabase.com/v1/projects/<ref>/config/auth" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"mailer_autoconfirm": true, "disable_signup": false}'
```
Also set `site_url` to the Vercel production URL for correct redirects.

## SQL Migrations

### 🚨 PITFALL: Splitting multi-statement SQL breaks PL/pgSQL
When running migrations via the Management API's `/database/query` endpoint, it executes ONE statement per call. Splitting on semicolons destroys multi-statement bodies (functions, triggers with `$$` blocks, `BEGIN...END`).

**✅ Do:** Run the entire migration as a single statement in Supabase SQL Editor (Dashboard → SQL Editor → paste full SQL).

**❌ Don't:** Split the SQL file by semicolons and run each fragment separately. The function body `$$...$$` will be torn apart.

### Entity creation: App code > DB triggers
Postgres triggers on `auth.users` are fragile (schema permissions, SECURITY DEFINER context, function truncation from split migrations). For auto-creating data on signup (e.g., personal entity, default categories):

**✅ Do:** Handle in the `signUp` server action:
```ts
const { data } = await supabase.auth.signUp({ email, password })
if (data.user) {
  await supabase.from("entities").insert({ user_id: data.user.id, type: "personal", name: "Personal" })
  // seed categories, etc.
}
```

**❌ Don't:** Use `CREATE TRIGGER ... ON auth.users`. Works in SQL Editor, breaks when splitting migrations, and introduces auth-schema permission issues.

## Server Actions

### 🚨 PITFALL: `redirect()` in server actions called imperatively
When a server action uses `redirect("/path")` and is called from an `onSubmit` handler (not a form `action` prop), the NEXT_REDIRECT throw goes uncaught. The form silently fails.

**✅ Do:** Return `{ success: true }` from the server action and let the client navigate:
```ts
// server action
export async function signIn(formData: FormData) {
  const { error } = await supabase.auth.signInWithPassword(...)
  if (error) return { error: error.message }
  return { success: true }  // client does router.push()
}

// client form
const result = await signIn(formData)
if (result?.error) setError(result.error)
else router.push("/dashboard")
```

**❌ Don't:** `redirect("/dashboard")` in the server action when called from `onSubmit`. Only works when the server action is the form's `action` prop.

### 🚨 PITFALL: Unchecked Supabase mutations always return `{ success: true }`

When calling `supabase.from(...).delete().eq(...)`, `supabase.from(...).update(...).eq(...)`, or similar mutations, the response `.error` is never checked by default. If the DB write fails (RLS, constraint violation, network issue), the caller gets `{ success: true }` — data silently lost.

```ts
// ❌ BAD — always reports success
await supabase.from("accounts").delete().eq("id", id);
revalidatePath("/accounts");
return { success: true };

// ✅ GOOD — check error before reporting success
const { error } = await supabase.from("accounts").delete().eq("id", id);
if (error) return { error: error.message };
revalidatePath("/accounts");
return { success: true };
```

Same for `.single()` queries — always destructure both `data` and `error`:
```ts
const { data, error } = await supabase.from("entities").select("currency").eq("id", entityId).single();
if (error) return "USD";
return data?.currency || "USD";
```

This pattern cost 8 silent data-loss bugs in a single CashFlow OS session. Check every mutation.

### Entity resolution pattern
Every server action that touches entity-scoped data must resolve the user's entity first:
```ts
async function getEntity() {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) throw new Error("Not authenticated")
  const { data: entity } = await supabase
    .from("entities").select("id")
    .eq("user_id", user.id).eq("type", "personal").single()
  if (!entity) throw new Error("No personal entity")
  return { supabase, entityId: entity.id }
}
```
Use this helper at the top of every data-access server action.

## RLS Policies

### Entity-scoped RLS (not user_id)
When using an entity pattern (where records belong to entities, not users directly), RLS policies use a subquery:
```sql
CREATE POLICY "view" ON transactions FOR SELECT USING (
  EXISTS (SELECT 1 FROM entities WHERE entities.id = transactions.entity_id AND entities.user_id = auth.uid())
);
```
This avoids a `user_id` column on every table while still enforcing per-user isolation.

## UI Component Patterns

### shadcn/ui on Windows
The `npx shadcn@latest add` CLI often fails on Windows with npm cache errors. **Write components manually** — they're just React components with Tailwind classes. The standard pattern:
```tsx
import * as React from "react"
import { cn } from "@/lib/utils"

const Card = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn("rounded-lg border bg-card text-card-foreground shadow-sm", className)} {...props} />
  )
)
Card.displayName = "Card"
```
Create `components.json` for the shadcn config, but write the `.tsx` files by hand.

### Recharts type workarounds
Recharts has strict TypeScript types that often reject valid callbacks. Use `any` as a pragmatic escape:
```tsx
// Pie label
<Pie label={(p: any) => `${p.name} ${((p.percent ?? 0) * 100).toFixed(0)}%`} ...>

// Tooltip formatter
<Tooltip formatter={(v: any) => `$${Number(v).toLocaleString()}`} />
```
This is a known trade-off — the types are correct but incompatible with simple render functions.

## Deployment

### Vercel env vars
`NEXT_PUBLIC_*` vars from `.env.local` are NOT auto-uploaded. Set them explicitly:
```bash
npx vercel env add NEXT_PUBLIC_SUPABASE_URL production
npx vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY production
```
Deploy picks up vars from Vercel's env store, not from local `.env.local`.

### Vercel project linking
First deploy auto-links. For subsequent deploys from CLI:
```bash
cd project-dir && npx vercel --yes --prod
```
GitHub auto-deploy needs Vercel dashboard → Settings → Git → Configure.

## Supabase Client Patterns

### Server client (`@supabase/ssr`)
```ts
import { createServerClient } from "@supabase/ssr"
import { cookies } from "next/headers"

export async function createClient() {
  const cookieStore = await cookies()
  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    { cookies: { getAll: () => cookieStore.getAll(), setAll: (c) => c.forEach(({ name, value, options }) => cookieStore.set(name, value, options)) } }
  )
}
```

### Browser client
```ts
import { createBrowserClient } from "@supabase/ssr"
export function createClient() {
  return createBrowserClient(process.env.NEXT_PUBLIC_SUPABASE_URL!, process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!)
}
```

### Middleware (auth gate)
```ts
import { createServerClient } from "@supabase/ssr"
import { NextResponse } from "next/server"

export async function middleware(request) {
  const supabase = createServerClient(url, key, { cookies: { getAll: () => request.cookies.getAll(), setAll: (c) => { /* ... */ } } })
  const { data: { user } } = await supabase.auth.getUser()
  if (!user && !isAuthPage) return NextResponse.redirect(new URL("/login", request.url))
  if (user && isAuthPage) return NextResponse.redirect(new URL("/dashboard", request.url))
  return NextResponse.next({ request })
}
```
Note: Next.js 16 deprecates `middleware.ts` in favor of `proxy.ts` — the pattern is identical.

### 🚨 PITFALL: Public marketing pages need TWO changes, not one
Adding public routes (`/`, `/about`, `/pricing`, `/tutorial`) to an auth-gated app silently breaks in one of two ways. The gate is TWO layers:

1. **Server-side allowlist** in the proxy/middleware — add before the `!user` redirect:
```ts
const isPublicPage =
  request.nextUrl.pathname === "/" ||
  request.nextUrl.pathname.startsWith("/about") ||
  request.nextUrl.pathname.startsWith("/pricing") ||
  request.nextUrl.pathname.startsWith("/tutorial");
if (!user && !isAuthPage && !isPublicPage) return NextResponse.redirect(new URL("/login", request.url));
```

2. **Client-side shell branch** — the layout wrapper that decides bare render vs app shell (e.g. an `AuthShell`/`RootLayout` that wraps children in the sidebar `AppShell`). Routes NOT in its bare branch render inside the authenticated app shell (sidebar, entity switcher, sign-out, dark toggle) — wrong chrome for logged-out visitors. Extend the bare branch:
```ts
const isAuthPage =
  pathname === "/login" || pathname === "/signup" || pathname === "/" ||
  pathname.startsWith("/about") || pathname.startsWith("/pricing") || pathname.startsWith("/tutorial");
```
The `/` route is often already in the bare branch — check the existing condition before adding paths.

Notes:
- The shell wrapper has NO client-side auth guard (proxy handles redirects), so logged-out users get the app sidebar rendered — the failure is cosmetic, not a crash. Diagnose via "why does my public page show the sidebar" not "redirect loop".
- `AppShell` still fires auth data fetches (`getUserEntities`, currency) on public pages — harmless but noisy; keep marketing pages OUT of the shell to avoid it.
- Keep marketing pages as server components; `"use client"` only for the navbar hamburger and the pricing monthly/yearly toggle.
- `npx tsc --noEmit` can report a transient error in a file another session/IDE is mid-edit; re-run once before chasing it.
