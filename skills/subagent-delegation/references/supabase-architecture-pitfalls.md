# Supabase Architecture Pitfalls

## DB Triggers on auth.users

**Problem:** Triggers on `auth.users` are fragile. They need SECURITY DEFINER, can fail with opaque 500 errors, and migration SQL split by regex can truncate `$$...$$` blocks.

**Fix:** Handle entity creation in app code (server action on signup), not in a DB trigger.

## Server Action redirect() Pattern

**Problem:** `redirect()` in a server action called imperatively (not via form `action` prop) throws NEXT_REDIRECT which isn't caught by client-side error handlers. The redirect silently fails.

```ts
// ❌ Breaks when called from onSubmit handler
export async function signIn(formData: FormData) {
  await supabase.auth.signInWithPassword(...)
  redirect("/dashboard")  // throws, client never navigates
}

// ✅ Works
export async function signIn(formData: FormData) {
  const { error } = await supabase.auth.signInWithPassword(...)
  if (error) return { error: error.message }
  return { success: true }  // client handles navigation
}
```

## Migration via REST API

**Problem:** Splitting SQL on semicolons with regex breaks `$$...$$` blocks, functions, and triggers. Use direct execution or targeted splitting.

**Fix:** Use Supabase Management API directly with `requests` in Python, executing full statements:
```python
requests.post(
    f"https://api.supabase.com/v1/projects/{ref}/database/query",
    headers={"Authorization": f"Bearer {token}"},
    json={"query": full_sql_statement}
)
```

## Post-Migration Verification

Always verify after migration:
```sql
-- Check tables exist
SELECT table_name FROM information_schema.tables WHERE table_schema='public'
-- Check RLS policies
SELECT tablename, policyname FROM pg_policies WHERE schemaname='public'
-- Check triggers/function bodies
SELECT prosrc FROM pg_proc WHERE proname='handle_new_user'
```

## Supabase Auth Config for MVP

Email/password signup needs:
- `mailer_autoconfirm: true` (skip email verification for MVP)
- `site_url` set to deployed Vercel URL
- `additional_redirect_urls` includes localhost + deployed URL
