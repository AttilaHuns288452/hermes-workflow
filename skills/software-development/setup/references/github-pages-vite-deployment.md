# GitHub Pages + Vite Deployment Notes

Common failure modes when deploying a Vite React app to a GitHub Pages project site (`https://<user>.github.io/<repo>/`).

## Root cause of "only hero renders"

The live site showed the hero + footer but a huge blank middle section. The DOM contained all sections; the missing sections were wrapped in `.reveal { opacity: 0; transform: translateY(30px) }` and the IntersectionObserver never added `.visible` to most of them. The deployment itself was also stale: the repo root `index.html` pointed to `/src/main.jsx` (Vite source), which 404s on Pages.

## Build pitfall: root `index.html` must be source, not built output

If you copy `docs/index.html` to repo root and then run `npm run build`, Vite sees the hashed asset paths (`/hermes-workflow/assets/index-XXXXXX.js`) in `index.html` and tries to resolve them as entry points, failing with:

```
Failed to resolve /hermes-workflow/assets/index-XXXXXX.js from .../index.html
```

**Fix:** keep `index.html` as the Vite source (`<script type="module" src="/src/main.jsx"></script>`) during build. Only copy the built `docs/` output to root *after* the build succeeds.

## Correct workflow

```bash
# 1. Ensure root index.html is the Vite source
#    (points to /src/main.jsx, not a hashed asset)

# 2. Build
npm run build

# 3. Copy built output to repo root for Pages root-source deployment
cp docs/index.html index.html
mkdir -p assets
cp docs/assets/* assets/
touch .nojekyll

# 4. Commit both root and docs copies so Pages works whether source is root or /docs
git add index.html assets/ docs/ .nojekyll docs/.nojekyll
git commit -m "deploy: rebuild docs/ and sync to root"
git push
```

Vite config for GitHub Pages project site:

```js
export default defineConfig({
  base: '/<repo-name>/',
  build: { outDir: 'docs' },
})
```

## Fix hidden-by-default scroll-reveal CSS

If sections use `opacity: 0` with scroll-triggered `.visible`, make content visible by default so a broken observer doesn't hide everything:

```css
.reveal {
  opacity: 1;
  transform: translateY(0);
}

@media (prefers-reduced-motion: no-preference) {
  .reveal {
    opacity: 0;
    transform: translateY(30px);
    transition: opacity .7s, transform .7s;
  }
  .reveal.visible {
    opacity: 1;
    transform: translateY(0);
  }
}
```

See `references/scroll-reveal-fallback.md` for the full pattern and Playwright verification script.

## Verification commands

```bash
# What index.html points to
curl -s https://<user>.github.io/<repo>/index.html | grep -o 'src="[^"]*"'

# Asset 200 (cache-bust with random query string)
curl -sI "https://<user>.github.io/<repo>/assets/index-XXXX.js?_$RANDOM"

# CSS contains visible-by-default reveal rule
curl -s https://<user>.github.io/<repo>/assets/index-XXXX.css | grep -o '\.reveal{[^}]*}'
```
