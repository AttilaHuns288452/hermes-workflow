# CDN UMD Variable Collision — `let` vs `var` in Non-Module Scripts

## The Bug

Loading a library via CDN `<script>` (UMD bundle) that declares a global with `var`, then declaring the same name with `let`/`const` in your inline script causes:

```
SyntaxError: Identifier 'supabase' has already been declared
```

## Why

In non-module `<script>` tags, `var X = ...` creates `window.X` as an own property.
`let X` / `const X` creates a lexical binding in the same global scope — and that **conflicts** with the existing `var` binding from the UMD bundle.

The SyntaxError prevents **all** code in that script block from running — try/catch, Promise constructors, and all subsequent logic are dead.

## Symptom

- Infinite "Loading…" spinner (the init function's API call never fires)
- No error message rendered (the SyntaxError happens before `try` is entered, during script parsing)
- Browser console: `PAGE_ERROR: Identifier 'supabase' has already been declared`

## Fix

Rename the local variable to avoid the collision:

```javascript
// ❌ Collides with window.supabase from CDN
let supabase = null;
supabase = window.supabase.createClient(URL, KEY);

// ✅ No collision
let sb = null;
sb = window.supabase.createClient(URL, KEY);
```

Key rule: keep the `window.` prefix when referencing the UMD global (`window.supabase.createClient`), but use a different local variable name (`sb`, `supa`, `client`, etc.).

## Prevention

When consuming a CDN-loaded UMD library in a non-module `<script>`:

1. Check what global variable the UMD bundle exports (`var X = ...` near the end of the minified bundle)
2. Avoid using that same name in `let`/`const` declarations in your inline scripts
3. Use a distinct alias (`supabase → sb`, `React → R`, `$ → jq`) 

## Detection

- Open browser DevTools → Console **before** or **immediately after** page load
- Filter for `SyntaxError: Identifier`
- The error fires during parsing, before any application code runs, so `window.onerror` or React Error Boundaries may not catch it

## Real-World Case: Supabase JS Client

- CDN: `https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2`
- UMD export: `var supabase = (function(e){ ... })(...)` → `window.supabase`
- Inline script: `let supabase = null;`
- Result: SyntaxError at parse time → "Loading from Supabase…" forever

Fix in 4 lines: rename `let supabase` → `let sb`, update all references. Deployed in under 30s.
