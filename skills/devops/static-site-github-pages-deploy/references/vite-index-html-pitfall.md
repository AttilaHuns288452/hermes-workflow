# Vite Stale index.html Pitfall — Debugging Trace

## The Problem

When deploying a Vite static site to GitHub Pages using the "copy build output to repo root" pattern, `npm run build` fails with:

```
[plugin vite:build-html] index.html
Error: Failed to resolve /hermes-workflow/assets/index-jmGgDArs.js from index.html
```

## Root Cause

Vite uses the root `index.html` as its **entry point** (not `src/main.jsx` directly — it discovers `src/main.jsx` via the `<script type="module" src="/src/main.jsx">` tag in `index.html`).

The deploy workflow copies `docs/index.html` (the **built** version) to root `index.html`:
```bash
cp docs/index.html index.html
```

The built `docs/index.html` contains hashed asset references:
```html
<script type="module" crossorigin src="/hermes-workflow/assets/index-jmGgDArs.js"></script>
<link rel="stylesheet" crossorigin href="/hermes-workflow/assets/index-D02L_BxW.css">
```

On the next build, Vite reads root `index.html`, finds references to assets that don't exist yet (they're about to be generated), and fails.

## The Fix

Before building, restore the source `index.html` that references `/src/main.jsx`:

```bash
# Option A: Restore from git history (find the commit that had the source version)
git show <commit-with-source-html>:index.html > index.html

# Option B: If you know the source content, write it directly
# The source index.html MUST have:
# <script type="module" src="/src/main.jsx"></script>
# and NO hashed asset references

# Option C: Prevention — add a prebuild script in package.json
# "prebuild": "git show HEAD:index.html > index.html"
# (only works if the committed index.html is the source version)
```

## Detection Command

```bash
# Quick check — does root index.html have source ref or stale hashed refs?
grep -q 'src/main.jsx' index.html && echo "source OK" || echo "STALE — needs restore"
```

## Better Architecture: Use /docs folder for Pages

The cleanest fix is to NOT copy build output to root at all:

1. Vite config: `build: { outDir: 'docs' }`
2. GitHub Pages: Settings → Pages → Source → Deploy from a branch → `master` / `/docs`
3. GitHub Pages serves from `/docs` directly — root `index.html` stays as Vite source entry
4. No copying needed, no stale file problem

The "copy to root" pattern exists for repos that want Pages served from root. If that's not a hard requirement, the `/docs` folder approach is strictly better.

## Session Trace (2026-07-27)

- Project: hermes-workflow (Vite + React + Tailwind)
- `vite.config.js`: `base: '/hermes-workflow/', build: { outDir: 'docs' }`
- Previous deploy had run `cp docs/index.html index.html`, overwriting Vite's entry point
- Build failed with `Failed to resolve /hermes-workflow/assets/index-jmGgDArs.js`
- Fix: `git show 07bb0e9:index.html > index.html` (found the source commit via `git log --all -S "src/main.jsx" -- index.html`)
- Added back OG meta tags that the source version was missing
- Build succeeded after restore
