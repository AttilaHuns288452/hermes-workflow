# Role Board Supabase — Stuck-at-Loading Debug Session

## Symptom

Deployed site at `https://role-board-supabase.vercel.app` showed "Loading from Supabase…" spinner indefinitely. No error message shown.

## Root Cause

The `CONFIGURED` guard compared SUPABASE_URL and SUPABASE_KEY against their own hardcoded values:

```javascript
// Line 261 in index.html — always false
const CONFIGURED = SUPABASE_URL !== 'https://qjtzednadniskhtpjzyw.supabase.co' 
                && SUPABASE_KEY !== 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...';
```

Since the URL and key matched their own string exactly on both sides of `!==`, `CONFIGURED` was always `false`. The `if (CONFIGURED)` block never created the Supabase client, and `init()` returned immediately at `if (!CONFIGURED) return;`. The loading spinner text was never replaced.

## Fix Applied

1. **CONFIGURED check** — changed from self-comparison to truthy check:
   ```javascript
   const CONFIGURED = !!(SUPABASE_URL && SUPABASE_KEY);
   ```

2. **SUPABASE_KEY** — kept the existing full JWT key (the `read_file` tool had truncated its display, making it look like a placeholder `eyJhbG...bf98` when the actual file contained the full JWT).

## Supabase Project Info

| Field | Value |
|-------|-------|
| Project URL | `https://qjtzednadniskhtpjzyw.supabase.co` |
| Project ID | `qjtzednadniskhtpjzyw` |
| Key format | `sb_publishable_<base64>` (newer Supabase format) |
| Key value | `sb_publishable_fA2-vEEktnLWTLv0o-Kukw_K3dXTzzI` |
| Tables | `roles`, `members` (created via schema.sql) |
| RLS | Public read/write on both tables |

## Verification

```bash
# Both tables exist and accept public SELECT
curl -s -H "apikey: sb_publishable_fA2-vEEktnLWTLv0o-Kukw_K3dXTzzI" \
        -H "Authorization: Bearer sb_publishable_fA2-vEEktnLWTLv0o-Kukw_K3dXTzzI" \
        "https://qjtzednadniskhtpjzyw.supabase.co/rest/v1/roles?select=count"
# → [{"count":0}]
```

## Second Bug (2026-07-27) — CDN UMD Variable Collision

After fixing CONFIGURED, the page still showed "Loading from Supabase…" forever. No error in the catch block.

**Root cause:** `@supabase/supabase-js@2` UMD bundle declares `var supabase` globally. The inline script's `let supabase = null;` collided with it — `SyntaxError: Identifier 'supabase' has already been declared`. The SyntaxError is a compile-time error in the script scope; it prevents ANY code in that script from running, including the try/catch. The page freezes before `init()` even runs.

**Fix:** Renamed local variable `supabase` → `sb` everywhere, keeping `window.supabase` as the UMD reference:
```javascript
let sb = null;                          // was: let supabase = null;
sb = window.supabase.createClient(URL, KEY);
await sb.from('roles').select('*');
```

**Verification with Playwright:**
```
node test_page.mjs
=== PAGE TEXT ===
TEAM ROLE BOARD
Drag items between roles · Click the dot to cycle confidence · All data persisted in Supabase
+ Add Item (to Unassigned)
+ Add Role
Seed Default Data
Unassigned

=== CONSOLE LOGS ===
(no errors)
```

**Lesson:** When a vanilla JS app uses a CDN library's UMD bundle that exports a global with `var`, never reuse that global's name as a local `let`/`const`/`var` in the same non-module `<script>`. The `var` in the UMD and the `let` in the inline script conflict because both run in the same function scope (the global scope of the non-module script).

## Deployment Info

GitHub repo: `AttilaHuns288452/role-board-supabase`
Vercel auto-deploys from `main` branch.
Live URL: https://role-board-supabase.vercel.app
