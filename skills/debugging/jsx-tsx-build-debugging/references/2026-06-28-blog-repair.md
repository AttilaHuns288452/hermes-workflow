# Session Reference: Blog Post JSX Repair (2026-06-28)

## Problem

7 blog post TSX files had structurally valid but tag-unbalanced JSX after batch-patching with `replace_all=True`. The patch tool's fuzzy matching consumed tag attributes and tag boundaries, leaving unclosed `<p>`, `<ol>`, `<ul>`, and `<div>` elements throughout.

## Initial Error

``` 
./app/blog/freelance-hourly-rate-calculator-guide/page.tsx:54:17
Expected '</', got 'jsx text'
```

## Actual Root Causes Found via `npx tsc --noEmit`

The TS compiler listed errors in reverse-order of root cause. The *first* TS17002 was the real root:

```
TS17008: JSX element 'p' has no corresponding closing tag  ← real root (unclosed <p>)
TS17008: JSX element 'article' has no corresponding closing tag ← cascade
TS17014: JSX fragment has no corresponding closing tag       ← cascade
```

## Fix Sequence for All 3 Broken Files

1. **Close `<p>` tags before block elements** — paragraphs before `<div>`, `<ul>`, `<h2>` needed `</p>` added
2. **Close `<ol>`/`<ul>` before headings** — list elements before `<h2>` needed `</ol>` or `</ul>`
3. **Close tip-box `<div>`** — `<div className="bg-blue-50...">` without `</div>` before `<hr>` or next heading
4. **Add `</>` fragment close** — missing between `</main>` and `);`
5. **Add `}` function close** — missing at EOF
6. **Re-add `import Script from "next/script"`** — removed by patch tool

## Useful Commands

**Get precise error locations:**
```bash
npx tsc --noEmit --jsx react-jsx --esModuleInterop --moduleResolution node app/blog/file.tsx 2>&1 | grep -E "TS17008|TS17002|TS17014"
```

**Check tag balance:**
```bash
node -e "
const fs = require('fs');
const c = fs.readFileSync('file.tsx','utf-8');
for (const t of ['p','ol','ul','div','span','table']) {
  const o = (c.match(new RegExp('<' + t + '\\\\b','g')) || []).length;
  const x = (c.match(new RegExp('</' + t + '>','g')) || []).length;
  const s = (c.match(new RegExp('<' + t + '[^>]*/>','g')) || []).length;
  console.log(t + ': ' + (o - x - s));
}
"
```

**Fix simple tag additions with sed (git-bash):**
```bash
sed -i 's|old text|new text|' file.tsx
```

**Fix missing fragment/function close at EOF:**
```bash
echo "}" >> file.tsx
```

## Key Learning

When using `patch()` on JSX files with `replace_all=True`, always verify the result by running `npx tsc --noEmit` before `npm run build`. The TS compiler gives far more precise diagnostics than Turbopack for tag-mismatch errors. Protect against cascading: fix ONE root cause (the first unclosed tag), rebuild, then check if cascading errors resolve themselves.
