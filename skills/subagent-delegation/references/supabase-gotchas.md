# Supabase Gotchas & Ponytail Fixes

Accumulated from CashFlow OS session (2026-07-30) and prior sessions.

## DB Triggers on auth.users Are Unreliable

**Problem:** Creating triggers on `auth.users` for auto-creating entities fails with
"Database error saving new user" (500). The trigger function exists and is correct,
but auth schema permissions prevent it from running during signup.

**Ponytail fix:** Handle entity creation in app code (server action on signup).
Drop the trigger entirely. One extra query, zero fragility.

```ts
// In signUp server action:
const { data: { user } } = await supabase.auth.signUp({ email, password })
if (user) {
  await supabase.from("entities").insert({ user_id: user.id, type: "personal", name: "Personal" })
  // seed default categories...
}
```

## redirect() in Server Actions Called Imperatively

**Problem:** `redirect("/dashboard")` in a server action throws NEXT_REDIRECT. When the
server action is called imperatively (via `onSubmit` + `preventDefault()`, not as a form
`action` prop), the redirect error is unhandled — the form submission silently fails.

**Ponytail fix:** Return `{ success: true }` instead of calling `redirect()`. Let the
client component do `router.push()` on success.

```ts
// DON'T:
export async function signIn(formData: FormData) {
  const { error } = await supabase.auth.signInWithPassword(...)
  if (error) return { error: error.message }
  redirect("/dashboard") // BUG: unhandled in imperative calls
}

// DO:
export async function signIn(formData: FormData) {
  const { error } = await supabase.auth.signInWithPassword(...)
  if (error) return { error: error.message }
  return { success: true } // client does router.push()
}
```

## Management API /database/query Runs One Statement

**Problem:** `POST /v1/projects/:ref/database/query` only executes the first SQL
statement. Multi-statement migrations must be split and run individually.

**Ponytail fix:** Split on semicolons, run each statement separately. Skip empty
statements and pure comment blocks. PL/pgSQL function bodies ($$...$$) break regex
splitting — run functions as single statements.

```python
statements = re.split(r';(?=\s*(?:--.*)?$)', sql, re.MULTILINE)
for stmt in statements:
    if stmt.strip():
        requests.post(f"{base}/query", json={"query": stmt})
```

## Idempotent Policies: DO $$ Not IF NOT EXISTS

`CREATE POLICY IF NOT EXISTS` is not valid PostgreSQL. Use `DO $$` blocks:

```sql
DO $$ BEGIN
  CREATE POLICY "policy_name" ON table_name
    FOR SELECT USING (condition);
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;
```

For INSERT policies, replace `FOR SELECT USING` with `FOR INSERT WITH CHECK`.

## mailer_autoconfirm for MVP

**Problem:** By default, Supabase requires email confirmation. For MVP, this adds
friction (user must check email before logging in).

**Fix:** `PATCH /v1/projects/:ref/config/auth` with `{"mailer_autoconfirm": true}`.
Users get a session immediately on signup. Also set `"disable_signup": false`.

## CHECK Constraints on Financial Columns

Always add CHECK constraints — Supabase doesn't auto-add them:

```sql
ALTER TABLE debts ADD CONSTRAINT debts_amount_nonnegative CHECK (amount >= 0);
ALTER TABLE assets ADD CONSTRAINT assets_value_nonnegative CHECK (value >= 0);
```

## UNIQUE on (entity_id, name) for Categories

Prevent duplicate category names within an entity:

```sql
ALTER TABLE categories ADD CONSTRAINT unique_category_per_entity UNIQUE (entity_id, name);
```

## Site URL for Production Deploy

Set `site_url` and `additional_redirect_urls` so Supabase auth redirects work
on both localhost and the deployed domain:

```python
requests.patch(f"{base}/projects/{ref}/config/auth", json={
    "site_url": "https://app-name.vercel.app",
    "additional_redirect_urls": "http://localhost:3000,https://app-name.vercel.app",
})
```

## Vercel Env Var Deployment

Next.js `NEXT_PUBLIC_*` vars must be set on Vercel separately from `.env.local`:

```bash
npx vercel env add NEXT_PUBLIC_SUPABASE_URL production
npx vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY production
npx vercel --yes --prod   # redeploy to pick up new vars
```
