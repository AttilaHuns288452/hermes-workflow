---
name: static-site-github-pages-deploy
description: "Deploy Vite/Astro/static sites to GitHub Pages by building, copying output to repo root, and pushing. Covers the stale-index.html pitfall and the build→copy→push workflow."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [github-pages, vite, deploy, static-site, frontend]
---

# Static Site GitHub Pages Deploy

Deploy Vite, Astro, or other static site builds to GitHub Pages using the "copy build output to repo root" pattern.

## When to Use

- Deploying a Vite/Astro/webpack static site to GitHub Pages
- The project builds to a subdirectory (e.g. `docs/`) and copies output to repo root for Pages serving
- You need to build, copy assets, commit, and push in one workflow

## The Deploy Workflow

```bash
# 1. Build the site (Vite example — outDir: 'docs', base: '/repo-name/')
npm run build

# 2. Copy build output to repo root for GitHub Pages
cp docs/index.html index.html
mkdir -p assets && cp docs/assets/* assets/

# 3. Commit and push
git add -A && git commit -m "feat: description" && git push origin master
```

## Vite Config Requirements

```js
// vite.config.js
export default defineConfig({
  base: '/repo-name/',           // GitHub Pages subpath
  build: { outDir: 'docs' },     // build output directory
})
```

GitHub Pages repo settings: Source = "Deploy from a branch", Branch = `master` / root, OR Branch = `master` / `/docs`.

## CRITICAL PITFALL: Stale root index.html breaks Vite build

**Symptom:** `npm run build` fails with:
```
Error: Failed to resolve /repo-name/assets/index-XXXXXX.js from index.html
```

**Root cause:** A previous deploy copied `docs/index.html` (the built version with hashed asset refs like `<script src="/repo-name/assets/index-jmGgDArs.js">`) over the root `index.html`. Vite uses root `index.html` as its entry point. When it contains hashed refs to assets that don't exist yet (they're about to be built), the build fails.

**Fix:** Restore the source `index.html` before building. The source version must contain:
```html
<script type="module" src="/src/main.jsx"></script>
```
NOT hashed asset references.

**Detection:** Check if root `index.html` has `/src/main.jsx` or hashed asset refs:
```bash
grep -q 'src/main.jsx' index.html && echo "source OK" || echo "STALE — needs restore"
```

**Prevention options:**
1. Don't copy `docs/index.html` to root — use GitHub Pages `/docs` folder setting instead (Settings → Pages → Source → master / `/docs`)
2. If you must copy to root, keep a backup of source `index.html` and restore before each build
3. Add a prebuild script: `"prebuild": "git show HEAD:index.html > index.html"` (if the committed version is the source)

See `references/vite-index-html-pitfall.md` for the full debugging trace.

## Build Verification

After building, verify the output:
```bash
# Check build succeeded
ls docs/index.html docs/assets/

# Verify no stale refs in built output
grep -c 'src/main.jsx' docs/index.html  # should be 0 — built output has hashed refs
```

## Windows / git-bash Notes

- Use forward slashes in all paths (`C:/Users/...` or `/c/Users/...`)
- `cp` and `mkdir -p` work in git-bash
- Git may warn about LF→CRLF — cosmetic, `.gitattributes` normalizes
- `npm run build` works the same as on POSIX
