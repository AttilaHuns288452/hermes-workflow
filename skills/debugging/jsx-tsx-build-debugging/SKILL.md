---
name: jsx-tsx-build-debugging
description: Systematically debug JSX/TSX build failures. Use when Next.js/Turbopack gives confusing parse errors ('Expected </', got 'jsx text'), when a build fails after template changes, or when tag-mismatch errors cascade in JSX files.
---

# JSX/TSX Build Debugging

## Overview

Next.js Turbopack error messages for JSX parsing failures can be misleading. "Expected '</', got 'jsx text'" often points at the **first tag AFTER the real problem**, not at the root cause. The real issue is usually an unclosed tag earlier in the file that cascades forward.

Use the TypeScript compiler directly to get precise tag-mismatch locations, then fix systematically.

## When to Use

- Turbopack says "Expected '</', got 'jsx text'" or "Expression expected"
- A build fails after template/JSX changes with confusing line references
- Tag-mismatch errors cascade across multiple files
- You patched a JSX file and the build broke in unexpected places

## Step-by-Step

### 1. Get Precise Error Locations

Turbopack errors often point downstream. Use TypeScript directly:

```bash
npx tsc --noEmit --jsx react-jsx --esModuleInterop --moduleResolution node app/path/to/file.tsx 2>&1 | grep -E "TS17008|TS17002|TS17014"
```

This filters to the actionable errors:
- **TS17008** — 'X element has no corresponding closing tag' (missing close)
- **TS17002** — 'Expected corresponding JSX closing tag for X' (nested inside unclosed tag)
- **TS17014** — 'JSX fragment has no corresponding closing tag' (missing `</>`)
- **TS1381** — Unexpected token (usually a stray brace from tag corruption)

### 2. Interpret the Cascading Error Chain

Errors cascade from the first real problem. Typical pattern:

```
1. TS17014: JSX fragment has no corresponding closing tag      → missing </>
2. TS17008: JSX element 'main' has no corresponding closing tag → cascading
3. TS17008: JSX element 'div' has no corresponding closing tag  → cascading
4. TS17008: JSX element 'article'...                            → cascading
...
N. TS17002: Expected corresponding JSX closing tag for 'p'      ← ROOT
```

The **last TS17008 error** in the list is usually the first real unclosed tag. The **first TS17002 error** is often the earliest root cause.

### 3. Check Tag Balance

For a quick audit of which element types are unbalanced:

```bash
node -e "
const fs = require('fs');
const content = fs.readFileSync('path/to/file.tsx', 'utf-8');
for (const t of ['p','ol','ul','div','span','table','h1','h2','h3','section','header','footer','article']) {
  const opens = (content.match(new RegExp('<' + t + '\\\\b','g')) || []).length;
  const closes = (content.match(new RegExp('</' + t + '>','g')) || []).length;
  const selfClose = (content.match(new RegExp('<' + t + '[^>]*/>','g')) || []).length;
  console.log(t + ': ' + (opens - closes - selfClose));
}
"
```

Any non-zero result indicates unbalanced tags.

### 4. Fix Root Cause, Not Symptoms

Once you identify the first unclosed tag, fix it with targeted patches. Then rebuild. Do NOT fix all the cascading errors individually — fixing the root cause resolves the cascade.

## Common Patterns & Fixes

### Unclosed `<p>` Before Block Elements

**Pattern:** `<p>` opens, then `<div>`, `<ul>`, or `<h2>` starts before `</p>` closes.

**Fix:** Add `</p>` before the block element:

```
old: ...text content</p>\n\n<h2>Section Title
new: ...text content</p>\n\n<h2>Section Title       # needs </p> before the blank line
```

### Unclosed `<ol>`/`<ul>` After List Items

**Pattern:** List items end, then a heading or div starts without closing the list.

**Fix:** Add `</ol>` or `</ul>` before the next heading:

```
old: <li>last item</li>\n\n<h2>Next Section
new: <li>last item</li>\n</ol>\n\n<h2>Next Section
```

### Missing `<div>` Close for Alert/Tip Boxes

**Pattern:** `<div className="bg-blue-50...">` (info box) opened but never closed before `<hr>` or next heading.

**Fix:** Add `</div>` before the next element after the box content.

### Missing `</>` Fragment Close

**Pattern:** `<>` opens in `return (<>` but `</>` is missing before `);`.

**Fix:** Add `</>` between `</main>` and `);`.

### Missing `}` Function Close

**Pattern:** `export default function X() {` opens but no final `}` at EOF. Turbopack says "Expected '}', got '<eof>'".

**Fix:** Add `}` at the end of the file.

### Premature `}` Before `return` (white screen)

**Pattern:** the function closes EARLY — `}` right after a helper/const, with the `return (` JSX block sitting AFTER it at module top level. Vite dev shows a white page (compile error); `npm run build` fails on the stray top-level `return`.

```
export default function AuthModal() {
  const [mode, setMode] = useState('login')
  const tabClass = ...          // ← premature }
}
  return (<div>...</div>)       // ← return is OUTSIDE the function
}
```

**Fix:** move the closing `}` to after the `return` block. This is the mirror of the missing-brace case — always check brace/return ORDER, not just presence.

### White screen in Vite dev: unimported component + undefined handler

A blank white page (no error overlay) in a Vite+React app usually means a **runtime ReferenceError**, not a build failure:

- **Component used but never imported** — `<LandingPage />` in JSX with no `import LandingPage` → ReferenceError → React unmounts everything → white page. Grep the imports vs every `<Component` used.
- **Stray `(` expression inside JSX** — a bare `(<Component ... />)` pasted into the return tree with no preceding `{` renders nothing and looks like a deleted chunk of code.
- **Handler case typos** — `onCLick` (capital L) silently never fires; no error, button just does nothing. `onClick` is the only correct casing in React.

When the user reports "page is white" and the build passes, read the whole component file top-to-bottom first — mid-edit files routinely have early `}`, unimported references, and stray expressions.

## Workflow pitfall: sibling " - Copy" folders

This user keeps `project`, `project - Copy`, `project - Copy (2)` side by side. A working version often exists in a Copy folder while the main folder is mid-rebuild. **Do NOT silently copy working files from a Copy folder to fix the main folder** — the user may be intentionally rebuilding those components from scratch. Fix the root cause in place; ask (or state plainly) before copying anything in.

## Pitfalls

### Flaky `tsc --noEmit` on Next.js: missing `.next/dev/types` + incremental cache

On Next.js projects, `tsc --noEmit` can give **different results run to run**:

- **TS6053 `.next/dev/types/*.d.ts not found`** — those files are generated by Next (`next dev` / `next typegen`), NOT by tsc. If they don't exist, tsc errors out.
- **Phantom TS2345/other errors in files you didn't touch** — with `"incremental": true` in tsconfig, a stale `tsconfig.tsbuildinfo` (or types generated against an older file set) surfaces errors from untracked WIP files or old route types.

**Fix sequence:**

```bash
npx next typegen                 # regenerate .next/types + .next/dev/types
npx tsc --noEmit --incremental false   # force a fresh full check
```

Run it twice — the first run may still be polluted by the stale tsbuildinfo; the second confirms stability. To attribute an error to the right file before debugging it: `git status --porcelain <file>` — an untracked (`??`) file is not yours; verify against a fresh check before treating it as a regression.

### On Windows hosts: `search_files` may fail with MSYS path errors

`search_files` (rg-backed) can fail with `IO error ... /c/Users/... The system cannot find the path specified` even when `read_file` works fine with the same `C:/...` path. Fallback: use terminal `cd "/c/Users/..." && grep -rn ...` (git-bash) — that works reliably.

### lucide-react icon aliases break `declare const` greps

Older icon names like `AlertTriangle` are exported as **aliases** (`TriangleAlert as AlertTriangle`), so `grep "declare const AlertTriangle:"` finds nothing even though the import compiles. Verify icon availability against the export list (`grep "export { ..."`) or just try importing — a missing alias is a build error, a missing `declare const` match is not evidence of absence.

### Vite Build Fails: "Failed to resolve ... from index.html"

**Distinct from JSX parse errors.** This is a Vite config issue, not a tag-mismatch issue. If the build error looks like:

```
Error: Failed to resolve /repo-name/assets/index-XXXXXXX.js from index.html
```

The root `index.html` has been overwritten with **built output** (hardcoded hashed asset references) instead of referencing the Vite source entry (`/src/main.jsx`). This happens when someone copies `docs/index.html` or `dist/index.html` to the repo root.

**Fix:** Restore root `index.html` to reference `/src/main.jsx`:
```html
<script type="module" src="/src/main.jsx"></script>
```

Then `npm run build` to regenerate the `docs/` or `dist/` output. See `hermes-workflow-documentation` skill → `references/vite-github-pages-deploy.md` for full context.

### Fuzzy Patch Tool Can Consume More Than Intended

When using `patch()` with `replace_all=True` on JSX files, the fuzzy matcher may match beyond the intended boundary. Warning signs:

- A tag line changed from `<div className="...">` to just `<div` (attributes eaten)
- Two `</div>` tags where there should be one
- A function name or closing brace disappeared
- The build fails after the patch with new errors far from the patched area

**Safer alternatives when patch is too aggressive:**

1. Use `sed -i` for simple one-line text replacements (works in git-bash on Windows)
2. Use `write_file` to rewrite the file from scratch using a known-good template
3. Use `patch()` with more surrounding context and WITHOUT `replace_all=True`

### Indentation Doesn't Matter for Nesting

JSX nesting is determined by tag open/close order, NOT by indentation whitespace. A `<footer>` with LESS indentation than the `<div>` containing it is still INSIDE that `<div>` until `</div>` is encountered. This means you can't rely on visual indentation to verify nesting — check the actual tag order.

### Line-Ending Warnings Are Safe

Git warning "LF will be replaced by CRLF the next time Git touches it" for modified files is harmless on Windows. It does not affect the build.

## Verification

- [ ] `npm run build` passes (Turbopack + TypeScript)
- [ ] All TS17008 errors resolved (no unclosed elements)
- [ ] No cascading TS17002 errors remain
- [ ] Build output shows expected number of static pages
