# Next.js Server Action Pitfalls

## `redirect()` silently breaks form submissions

**Symptom:** Login/signup forms submit but nothing happens — no error, no navigation, no loading state. User clicks submit and stays on the form.

**Root cause:** `redirect()` in a Next.js server action throws a `NEXT_REDIRECT` error. When the server action is called **imperatively** (via `onSubmit` + `e.preventDefault()` + manual call), this throw is an unhandled promise rejection — not caught by Next.js's form submission handling.

**Wrong (silent failure):**
```ts
// actions.ts
"use server"
export async function signIn(formData: FormData) {
  // ... auth ...
  redirect("/dashboard")  // ❌ throws, form handler never sees the result
}

// LoginForm.tsx
async function handleSubmit(e) {
  e.preventDefault()
  const result = await signIn(new FormData(e.target))  // never resolves; redirect throws
  // unreachable code below
}
```

**Right (return structured result):**
```ts
// actions.ts
"use server"
export async function signIn(formData: FormData) {
  // ... auth ...
  return { success: true }  // ✅ client receives result, can navigate
}

// LoginForm.tsx
async function handleSubmit(e) {
  e.preventDefault()
  const result = await signIn(new FormData(e.target))
  if (result?.error) { setError(result.error); return }
  router.push("/dashboard")  // ✅ client handles navigation
}
```

**When `redirect()` IS safe:** Only when the server action is used as the form's `action` prop directly (not called imperatively). Next.js intercepts the form submission response and handles the redirect.

**Also applies to:** `revalidatePath()`, `revalidateTag()` — these are safe (synchronous), but `redirect()` and other navigation functions (`notFound()`, `permanentRedirect()`) throw. Return structured `{ error, success }` instead.

## Entity creation in app code vs DB triggers

**Problem:** Postgres triggers on `auth.users` need `SECURITY DEFINER` and fail silently when SQL migrations are split by semicolons (function body gets truncated).

**Fix:** Move entity/category creation to the `signUp` server action. More reliable, easier to debug, and allows error surfacing to the user:

```ts
export async function signUp(formData: FormData) {
  const { data, error } = await supabase.auth.signUp({ email, password })
  if (error) return { error: error.message }

  // Create entity in app code, not DB trigger
  const { data: entity, error: entityErr } = await supabase
    .from("entities")
    .insert({ user_id: data.user.id, type: "personal", name: "Personal" })
    .select("id").single()

  if (entityErr || !entity) {
    return { error: "Account created but setup failed. Please try signing in." }
  }

  // Seed default categories
  const { error: catErr } = await supabase.from("categories").insert(...)
  if (catErr) {
    return { error: "Account created but category setup failed." }
  }

  return { success: true }
}
```

**Key:** Always check errors on entity + category creation. Silent failures here mean the user signs up with no data — downstream crashes on every page.

## Supabase Migration via REST API

When running migrations through Supabase Management API (`/v1/projects/:ref/database/query`):

1. **One statement per call** — the API only runs the first SQL statement
2. **Split on `;` carefully** — PL/pgSQL `$$...$$` blocks contain semicolons. Use regex to avoid splitting inside dollar-quoted strings
3. **`CREATE POLICY IF NOT EXISTS` is invalid** — PostgreSQL doesn't support it. Use `DO $$ BEGIN CREATE POLICY ... EXCEPTION WHEN duplicate_object THEN NULL; END $$`
4. **`ALTER TABLE ... ADD COLUMN IF NOT EXISTS` IS valid** — use `IF NOT EXISTS` on ALTER/ADD operations
