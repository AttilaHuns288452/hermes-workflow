# Purging demo/QA accounts and their data from a live project

Turning a QA-polluted database back into a clean production seed: keep one account per role, delete everything else, and leave no orphaned rows behind. This is a DESTRUCTIVE operation — snapshot, dry-run, then mutate.

## 1. Establish the keep set explicitly, in the user's terms

List every auth user with their role and activity before asking anything:

```bash
curl -s "$URL/auth/v1/admin/users?per_page=200" -H "apikey: $SECRET" -H "Authorization: Bearer $SECRET"
```

Print one line per account: email, profile role, created_at, last_sign_in_at, and counts of appointments / chats / transactions. The user then answers in ROLES ("1 patient 1 doctor 1 owner"), not emails — map roles back to concrete accounts through the profiles/roster table and echo the mapping. Never assume "the demo trio": the platform superadmin, the owner's personal login, and teammate logins are separate decisions that the user will correct you on. Ask before deleting, and re-confirm when they amend the keep set mid-task.

## 2. Snapshot before touching anything

Write every table plus the auth user list to `backups/pre-cleanup-<ts>/` in one script:

- **Enumerate the schema from the Data API root** — `GET /rest/v1/` returns a `definitions` object whose keys are every exposed table. One call, no guessing, no need to parse migrations.
- Page each table with a `Range: <off>-<off+999>` header; stop when a page returns fewer rows than the page size.
- Auth users from `/auth/v1/admin/users?per_page=200&page=N` — store `id`, `email`, `created_at`, `last_sign_in_at` only. Never dump password hashes or tokens.
- Record a `_manifest.json` of table → row count so the dry-run numbers can be checked against reality later.

A 36-table / 59-user project lands around 8 MB. Trivially cheap insurance; do not skip it to save a call.

## 3. Dry-run the counts, then the FK graph

Run one read-only `SELECT` of CTEs that reports keepers vs doomed users / patients / appointments / payments / ledger rows and the counts of rows that will cascade. Approve the mutation against those numbers, not against a mental model.

Then read the constraint graph — the deletion ORDER depends on it, and guessing the order is what produces `23503 foreign key violation` halfway through a transaction:

```sql
select conrelid::regclass as tbl, conname, confdeltype, pg_get_constraintdef(oid) as def
from pg_constraint
where confrelid in ('auth.users'::regclass, 'public.profiles'::regclass, 'public.patients'::regclass)
  and contype = 'f'
order by 1, 2;
```

`confdeltype`: `c` = CASCADE (free), `n` = SET NULL (tolerated), `r` = RESTRICT and `a` = NO ACTION (**these block the delete**). Typical findings: `profiles`, `notifications`, `push_subscriptions`, `superadmins` cascade from `auth.users`; `transactions.created_by` and `schedule_blocks.created_by` do NOT and must be removed or nulled first.

## 4. Delete in dependency order, auth users last

One transaction for the SQL half, carrying the keeper identity in a single temp table so every step agrees:

```sql
begin;
create temp table k_user on commit drop as
  select u.id from auth.users u
  where lower(u.email) in ('patient@x','doctor@x','owner@x','superadmin@x');

-- a patients row survives only for a keeper whose ROLE is actually patient
create temp table k_pat on commit drop as
  select p.id from patients p join profiles pr on pr.id = p.user_id
  where p.user_id in (select id from k_user) and pr.role = 'patient';

-- 1. blocking / soon-to-be-orphaned child rows
-- 2. patients      (cascades chat/plans/ehr/service_prices)
-- 3. appointments  (cascades payments; provider_events.payment_id -> null)
-- 4. dentists with no remaining login
commit;
```

Then delete the auth users through GoTrue, never with `delete from auth.users`:

```
DELETE /auth/v1/admin/users/{id}   apikey + Authorization: Bearer <secret>
```

Loop the dry-run list, count successes and failures, then re-list and print the survivors. **Restrict the patients survival rule to keepers whose profile role is `patient`** — a superadmin often carries role `doctor` plus a stray patients row, and a naive `user_id in (keepers)` keeps that dead patient record (and its appointments) in the roster.

**Cleanup is not a business edit — delete the row, do not update it.** Domain guard triggers written to protect money (`price` / `payment_status` / `final_fee` "change only through the payment or completion workflow") correctly raise for a cleanup script holding a service key, because the guard checks the caller's role and not the intent. The temptation is to add an owner-role bypass or flip a `bypass` GUC for the cleanup. Do not. Delete the offending appointment/payment row (its ledger rows cascade) and move on — the guard is doing exactly its job. Applies to any placeholder row that only exists because a QA script wrote it; free-text content worth keeping for the demo is renamed instead (see the plausibility step).

## 5. Sweep what cascades miss

- **Storage does not cascade from `auth.users`.** List each bucket with `POST /storage/v1/object/list/<bucket>` body `{prefix:'', limit:1000, offset:0}`, split the owner id off each name (avatars are `<uid>-<ts>-avatar.jpg`, EHR files are `<patient_id>/<ts>-file`), and delete the orphans with `DELETE /storage/v1/object/<bucket>` body `{prefixes:[...]}`.
- Listing a folder-style prefix returns entries with `id: null` that are folders, not files — filter on `o.get('id')` before building the delete body, or you send a folder name and the request fails.
- **Notification rows hold denormalised deep-link keys (`appt:<uuid>:...`, `msg:<uuid>:...`) with no FK.** Deleting the appointment leaves dead links that the UI still renders and the user still clicks. Extract the uuid from `dedupe_key` and delete rows whose target no longer exists — this typically takes the table from thousands of rows down to tens.
- Audit logs usually have no FK to the actor. Decide explicitly (the default that satisfies this user: leave them, harmless history) and say so in the report rather than leaving it ambiguous.

## 6. Make the surviving demo data plausible

Correct row counts are not the same as an app that looks clean. A QA run leaves junk in
free-text columns that no FK or cascade touches: a treatment plan named `dfsdfsf`, a chat thread
of `musta par` / `ywww`, a service price nudged to `501` by a price-editing suite, an
announcement with a typo plus a seasonal sale two months stale, an adult patient whose birthdate
is the current year so the chart renders `0 y/o`. Query the keeper-visible content tables
(services, announcements, treatment plans, chat messages, patient demographic fields), fix the
strings, then render each role's landing page and read the visible text back. This data gets
demoed to a panel — "it's only seed data" is not a defense, and a checkerboard of test strings is
the first thing a reviewer notices.

## 7. Verify with invariants, not eyeballs

One anti-join query, every count must be 0: appointments with no patient · chat/plans with no patient · payments with no appointment · patients with no user · notifications with no user · dentists with no work schedule. Then:

1. Password-grant one real session per surviving role against the anon key; expect HTTP 200 for each.
2. Drive the UI per role (Playwright) and read back the owner's roster/ledger pages — a count badge that still shows the old total means a step was skipped.

## Pitfalls

- **A documented demo password is not proof the keeper knows it.** If one account rejects `password123` while its siblings accept it, stop guessing (GoTrue rate-limits and eventually locks): set it deliberately with `PUT /auth/v1/admin/users/{id}` body `{"password":"..."}` and confirm with a single password grant returning 200.
- **Do not assume a raw-SQL helper RPC exists.** `POST /rest/v1/rpc/exec_sql` 404s unless someone created that function; the failure reads like a permissions problem. Use the platform MCP `execute_sql`, the CLI, or the dashboard SQL editor for raw SQL — PostgREST only calls functions that actually exist.
- **Roles can collide with emails.** Keepers are identified by email in the delete predicate and by profile role in the survival predicate; use `lower()` on both sides or a case-variant duplicate slips through.
- An email that LOOKS like test data (`+1`, `regtest`, `qa…`) is still a user's account until they say otherwise — the dry-run count is what they approve, so make it legible.
- **Deleting fixture accounts invalidates every suite that logs in as them — report the split, do not paper over it.** Runtime suites that hardcode a shared demo identity (`maria@…`, `owner@…`) die at login once those accounts are gone; source-level/static suites keep passing. Grep the QA tree for the deleted addresses before declaring the project handover-ready, name the affected suites as a known blocker, and state that the static subset is still green. Repointing those suites or re-creating fixtures is separate work — do not silently re-create the accounts you were just asked to delete.
- **A runtime suite killed by a timeout leaves its fixtures behind.** Cleanup lives after the assertions, so a thrown `TimeoutError` skips it and the run's own `journey<ts>@…` user plus its patient/appointment rows survive — invisible until the next roster read. After ANY suite run against the cleaned database, re-list `auth.users` / `patients` / `profiles` for the run's marker or timestamp prefix, delete the stragglers, and re-run the invariant counts. Verify by count, not by the suite's exit line.
- **Orphan patient rows are not created by your purge — they were already there.** The patients→profiles FK is `ON DELETE SET NULL`, so an earlier account deletion leaves a full patient record with `user_id = null`: no login, still listed in the owner's roster, still carrying appointments. Probe `user_id is null or user_id not in (select id from profiles)` and delete them; they are the difference between "30 patients" and "25 patients that can log in".
- **Check the payment provider mode before demoing a purged project.** A project carrying live provider keys charges real money on the first booking demo. Read the mode flag out of the provider-config table and state live-vs-mock in the handover report instead of letting someone discover it at the payment step.
