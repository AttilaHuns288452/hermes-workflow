---
name: static-web-debugging
description: Debug deployed static web apps that fail to load, show stuck spinners, or can't connect to their backend (Supabase, API, etc.). Covers CONFIGURED-guard bugs, initialization flow analysis, and direct backend verification.
---

# Static Web App Debugging

## When to Use

- A static site (plain HTML/JS, no build step) deployed to Vercel, Netlify, or GitHub Pages shows an endless spinner / "Loading…" message
- The site works locally but not in production
- The Supabase-connected app shows "Loading from Supabase…" indefinitely
- The page renders whitespace with no apparent error
- A vanilla JS app fails silently without throwing console errors

## Triage by Visible State

| What you see | Likely cause | First action |
|---|---|---|
| Spinner says "Loading" forever | JS init guard blocks execution (CONFIGURED check, missing env) | Curl raw HTML, grep CONFIGURED/init |
| Spinner → red error text | Backend call failed (bad key, CORS, table missing) | Verify Supabase REST API directly |
| Blank white page | JS syntax error before first render, or CDN script failed to load | Check browser console, verify CDN URLs |
| Page renders but no data | Tables exist but empty, or query returns nothing | Seed data, check fetch logic |

## Diagnosis: Raw HTML Inspection (Primary Tool)

Curl the deployed HTML before touching any browser DevTools. The bug is often visible in the static source — no JS execution needed.

```bash
# Get the CONFIGURED/init logic
curl -sL https://site.vercel.app/ | grep -A3 'CONFIGURED\|init\|createClient\|supabase'

# Full init flow
curl -sL https://site.vercel.app/ | grep -n 'function.*init\|async.*fetch\|catch.*err\|CONFIGURED'
```

## Anti-Pattern: CONFIGURED Guard Compares Against Itself

The most common cause of "Loading forever" on Supabase-connected static sites:

```javascript
// BROKEN — always evaluates false because value === the hardcoded string
const CONFIGURED = SUPABASE_URL !== 'https://project.supabase.co'
                 && SUPABASE_KEY !== 'eyJhbG...';
// This checks: "is the URL not equal to itself?" → always false
// CONFIGURED is false → init() returns early → loading spinner never resolves

// FIXED — simple truthy check
const CONFIGURED = !!(SUPABASE_URL && SUPABASE_KEY);
```

**Why it happens:** The developer used placeholders (e.g. `%%SUPABASE_URL%%`) with a conditional-replacement build tool, then later hardcoded real values but never updated the comparison expression. The comparison is checking "is this value different from the template default?" — but when the template default and the hardcoded value are the same string, it always returns false.

**Fix:** Always use a truthy check (`!!(URL && KEY)`) for CONFIGURED guards. Never compare against the hardcoded value string.

## Verification: Supabase REST API Direct Connection

Use curl to verify Supabase connectivity independently of browser JS. This confirms the key is valid, tables exist, and RLS policies allow the operation.

```bash
# Verify the anon key + table existence + RLS read access
curl -s -H "apikey: $ANON_KEY" \
        -H "Authorization: Bearer $ANON_KEY" \
        "https://$PROJECT_ID.supabase.co/rest/v1/roles?select=count"

# Expected: [{"count":0}] when working (0 rows but table exists)
# Expected: [{"count":N}] when data exists
# Error { "message": "no such table" } — table missing, run schema.sql
# Error { "message": "permission denied" } — RLS blocks public access
```

**Key format note:** Supabase accepts both:
- Classic JWT anon key — `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
- Newer publishable key — `sb_publishable_<base64>`

Both work with `createClient()`. Do not reject a key because it doesn't look like a JWT — the `sb_publishable_` prefix is valid.

## Read-File Truncation Trap

When using `read_file` to inspect a static HTML file, long lines (especially API keys > ~80 chars) are **truncated in the display**. The content window shows `eyJhbG...bf98` but the actual file has the full key:

```
read_file display:   SUPABASE_KEY = 'eyJhbG...bf98'
actual file content: SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS...'
```

**Diagnosis:** Use `grep` in terminal to get the full line:
```bash
cat index.html | grep 'SUPABASE_KEY'
```

## Full Inspection Chain

```bash
# 1. Fetch raw HTML
curl -sL https://site.vercel.app/ > /tmp/deploy.html

# 2. Find CONFIGURED logic
grep -n 'CONFIGURED\|init\|createClient' /tmp/deploy.html

# 3. Find Supabase config values  
grep -n 'SUPABASE_URL\|SUPABASE_KEY\|ANON_KEY' /tmp/deploy.html

# 4. Check CDN scripts load
grep -n 'src="https://cdn\.\|src="https://unpkg' /tmp/deploy.html

# 5. Verify access errors in console area
grep -n 'catch.*err\|console\.error\|error.*message' /tmp/deploy.html
```

## Anti-Pattern: CDN UMD Variable Collision (Silent SyntaxError)

When a CDN script declares a global `var` and the inline script redeclares it with `let`/`const` in the same scope, the browser throws `SyntaxError: Identifier 'X' has already been declared`. The script stops — no error visible in the catch block, the loading spinner simply hangs forever.

**Example:** `@supabase/supabase-js@2` UMD bundle declares `var supabase` globally. Inline code then declares `let supabase` — collision in the non-module `<script>` scope:

```javascript
// UMD bundle (CDN, separate <script> tag, non-module)
var supabase = (function(e) { ... })(...);   // creates window.supabase

// Inline script — SyntaxError here, execution halts
let supabase = null;                    // ❌ 'supabase' already declared
supabase = window.supabase.createClient(...);
```

**Fix:** Rename the local variable:
```javascript
let sb = null;                          // ✅ no collision
sb = window.supabase.createClient(URL, KEY);
```

**Diagnosis:** Use Playwright headless to catch the SyntaxError:
```javascript
page.on('pageerror', err => console.log('PAGE_ERROR:', err.message));
// → PAGE_ERROR: Identifier 'supabase' has already been declared
```

**Prevention:** When a vanilla JS app uses a CDN library via UMD bundle, check if the library's global variable name (`window.supabase`, `window.Stripe`, etc.) matches any local `let`/`const`/`var` in the inline script. If yes, rename the local one.

## Red Flags

- Fixing a CONFIGURED check by changing the hardcoded comparison string instead of switching to a truthy check (brittle — breaks if values change)
- Deploying a site without verifying the Supabase tables exist (curl the REST API first)
- Assuming a key is invalid because it uses `sb_publishable_` prefix instead of a JWT format
- Reading a long key value via `read_file` and assuming the truncated display is the full value
- Checking browser DevTools before checking the raw HTML source (the bug is often in static markup, not runtime)
