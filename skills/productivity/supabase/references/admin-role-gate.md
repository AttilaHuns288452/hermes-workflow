# Database-enforced admin / role gate

A client-side admin check — a hidden route, a `sessionStorage` flag, or a role string in
`user_metadata` — is not authorization. It is UI decoration: anyone can flip it from the
browser. Enforce privileged access in the DATABASE, which the client cannot reach. The
client decides what to SHOW; the database decides what a caller may DO.

## When to use
Any admin / moderator / staff-only surface: an admin console, review moderation, content
management, feature flags, financial approval. The recipe is role-based authorization
enforced entirely in Postgres, verified behaviorally before you call it done.

## Recipe

### 1. Membership table with NO user-writable policy
```sql
create table public.admin_users (
  user_id uuid primary key references auth.users(id) on delete cascade,
  granted_at timestamptz not null default now()
);
alter table public.admin_users enable row level security;
-- READ-ONLY self view: a user may see their own membership, never write it
create policy admin_users_self_read on public.admin_users
  for select using (user_id = auth.uid());
-- Deliberately NO insert/update/delete policy.
```
The ABSENCE of a write policy is the security boundary. With RLS on and no policy
matching, Postgres default-denies: no client role can grant itself admin. Do not add a
`with check (auth.uid() = user_id)` insert policy here — that would let any user insert
their own row and self-elevate.

### 2. `is_admin()` security-definer check (fail-closed)
```sql
create or replace function public.is_admin() returns boolean
language sql security definer stable set search_path to public as $$
  select exists (select 1 from public.admin_users where user_id = auth.uid());
$$;
revoke execute on function public.is_admin() from public, anon;
grant execute on function public.is_admin() to authenticated;
```
`security definer` so it reads `admin_users` past the read policy; `stable`; safe
`search_path`. REVOKE from `public`/`anon` and grant to `authenticated` (the SKILL.md
function-privilege rules apply — a default PUBLIC execute grant is an availability oracle).

### 3. Gate privileged writes on `is_admin()`
Moderation / financial / status columns get an admin-only policy, or live inside a
SECURITY DEFINER RPC that raises unless `is_admin()`:
```sql
create policy reviews_admin_moderate on public.reviews
  for update using (public.is_admin()) with check (public.is_admin());
```
When one row has BOTH self-editable and admin-only columns, the self-write policy must
not touch the privileged columns — pair with `rls-column-guards.md` (BEFORE UPDATE trigger)
for the column split.

### 4. Wire the frontend to the DB check, not a local flag
After sign-in, call `is_admin()` (RPC) and gate the UI on its result. Gate the ROUTE too
(redirect non-admins), but treat the route gate as cosmetic — step 3 is the real boundary.
Never derive admin from `user_metadata` (user-editable, per SKILL.md) or a client-held flag.

### 5. Designate admins out-of-band
Insert into `admin_users` via the SQL editor / service key, never through a client path.
Do not auto-promote any account — ask the owner WHICH account should be admin first.

### 6. End-to-end UI verification without a real admin session
When the admin surface must be driven in a browser and no admin credentials exist:
temporarily promote a CONTROLLED test account (its own marker in `granted_by`, e.g.
`temp-ui-test`), sign in as it, run the UI journey, then delete exactly that row and
re-query to prove zero leftovers (`where granted_by = '<marker>'`). Row-level cleanup
proof beats hoping the delete matched. Never promote a real member's account, and never
end a session with the temporary grant still present.

## Verify (behavioral, before claiming it holds)
Using a NON-admin user JWT (never the service key — it bypasses RLS and proves nothing):
- self-insert into `admin_users` → REJECTED (403 / 42501)
- read `admin_users` → 0 rows (or only own membership)
- `is_admin()` → `false`
- touch the admin-only column / call the admin RPC → REJECTED
Then as the admin JWT: `is_admin()` → `true` and the same write succeeds. Both directions
must be asserted; a guard present in source is not proof it fires. Full probe loop in
`authorization-and-integrity-testing.md`.
