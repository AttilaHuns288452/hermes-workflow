# JSX Parse Error Diagnosis After Patch Edits

Captured from a production Next.js build session (June 2026) where fuzzy-patching 7 blog posts caused cascading build errors.

## Error Signatures and Root Causes

### "Expected '</', got 'jsx text'" at a closing tag

The most common pattern. The error points at `</h1>`, `</div>`, or `</header>`.

**Root cause:** A parent element opened earlier was never closed — its closing tag was consumed by a prior fuzzy patch. The parser now sees the `</h1>` / `</div>` as invalid because the JSX is nested inside the still-open `<p>`, `<time>`, or `<header>`.

**Quick check:** Read 10-15 lines ABOVE the error line. Look for:
- `<p>Some text` without `</p>` — the `<div>` coming next makes `<p>` illegal in JSX
- `<time class="...">` without a following `</time>` — the time text + close tag was consumed
- `</div></header>\n` appearing merged — should be separate lines

**Fix:** Add the missing closing tag. If a `<p>` is missing `</p>`, insert it before any `<div>` sibling.

### "Unexpected token 'default'" at `export default function`

**Root cause:** The preceding `export const metadata = { ... };` block lost its closing `};` (consumed by a fuzzy match targeting the `import Script from "next/script"` line directly above it).

**Fix:** Read the metadata object, count `{` and `}`, add `};` after the last property.

### Missing `<` on a JSX element line

`div className="max-w-4xl ...">` (no `<` at line start)

**Root cause:** A fuzzy patch with `replace_all=True` consumed the `<div` or `\n<div` sequence.

**Fix:** Prepend `<` to restore the JSX element.

### Missing function name in component declaration

`export default function\n  return (`

**Root cause:** The function name was consumed by `replace_all=True` matching on a nearby `<time className="...">` pattern whose fuzzy match swept into the function signature.

**Fix:** Add the function name: `export default function ComponentName() {`

## Session Narrative (What Happened)

The session applied 4 different patch operations to each of 7 blog posts:

1. **opener** — replaced the outer wrapper structure
2. **after-h1** — closed the hero wrapper and opened the content div
3. **remove-time** — deleted orphaned `<time>` tags (with `replace_all=True`)
4. **close** — replaced the old footer with new structure

Each patch succeeded (returned True), but the fuzzy matcher consumed adjacent content in 3 of 7 files — eating `</p>`, `<h1`, export metadata `};`, and function names silently.

## Lessons Applied Mid-Session

- After 6 failed builds, switched to single targeted patches instead of batch scripts
- Read the FULL file at the error location (not just error context window) to trace nesting
- Final fix was adding `</p>` before a `<div>` sibling — the most common single cause
