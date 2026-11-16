# Web Vitals measurement protocol

How to produce Lighthouse/Core Web Vitals numbers that mean something, and the two fixes that move the scores most on a Vite + React SPA. Read before reporting any performance score.

## Measure the build you ship

A dev server is not a measurement target: it serves un-minified, un-split modules with no production tree-shaking and long-poll HMR sockets, so every score is fiction in both directions (bundle weight overstated, runtime behaviour unrepresentative). Always:

1. `npm run build`, then serve the built output.
2. Serve it at the SAME base path the build uses. Vite `base: '/repo/'` means a flat server at `/` returns 200 for `index.html` while every asset 404s — the page "paints nothing" and looks like an app crash. Mount the output at the configured base and check the network tab for 200s on the JS/CSS chunks before trusting any number.
3. Point Lighthouse at a browser you control:

```bash
export CHROME_PATH=$(ls -d ~/.cache/ms-playwright/chromium-*/chrome-linux64/chrome | head -1)
lighthouse <url> --output=json --output-path=/tmp/lh.json \
  --only-categories=performance,accessibility,best-practices,seo \
  --form-factor=mobile --screenEmulation.mobile --quiet \
  --chrome-flags="--headless=new --no-sandbox"
lighthouse <url> --output=json --output-path=/tmp/lh-desk.json --preset=desktop \
  --chrome-flags="--headless=new --no-sandbox"
```

Report both form factors. Mobile throttles CPU 4x and reveals defects (layout shift, blocking work) that desktop never shows.

## CLS from webfont swap reflow

A remote webfont arriving after first paint reflows every text run: the fallback and the face have different ascent/descent/line-gap, so line boxes change height and the whole page shifts. Under Lighthouse's 4x CPU throttle this is the dominant CLS term; unthrottled it can read 0.0000 and hide entirely — reproduce under throttle before declaring CLS clean.

Fix by self-hosting the faces and giving each fallback an **explicit metric override** so the fallback occupies the same box as the real face:

```css
@font-face {
  font-family: 'Inter';
  src: url('/fonts/Inter-Variable.woff2') format('woff2');
  font-display: swap;
}
/* metric-matched fallback: measure the face's hhea/OS2 metrics with fontTools
   and set them as ratios against the fallback's own metrics */
@font-face {
  font-family: 'Inter-fallback';
  src: local('Arial');
  ascent-override: 100%;
  descent-override: 30.3%;
  line-gap-override: 0%;
  size-adjust: 105.8%;      /* matches advance width, so line breaks land equal */
}
```

Then declare the stack as `font-family: 'Inter', 'Inter-fallback', system-ui, sans-serif` so the overridden fallback is actually used. Derive the values rather than guessing:

```python
from fontTools.ttLib import TTFont
f = TTFont('Inter.ttf'); hhea = f['hhea']; head = f['head']
upem = head.unitsPerEm
print('ascent%', hhea.ascent / upem * 100)
print('descent%', abs(hhea.descent) / upem * 100)
# size-adjust = measured advance width of the real face / fallback's, in %
```

Self-hosting also removes a render-blocking third-party round-trip (Google Fonts), so it pays twice: CLS 0 and a faster FCP. Verify the font URLs survive the build — Vite rewrites `url()` in CSS for the configured `base`, and a font 404 silently reintroduces the swap shift.

## First-load JS: split by route

When Lighthouse reports a single large chunk of unused JS, statically imported pages are the cause. Make every route except the landing page lazy and keep one Suspense boundary so route transitions stay intact:

```tsx
const Admin = lazy(() => import('./pages/Admin'));   // landing stays eager
<Routes>
  <Route path="/" element={<Home />} />
  <Route path="/admin" element={<Suspense fallback={null}><Admin /></Suspense>} />
</Routes>
```

Measure the split before and after (chunk sizes in the build output). Leave the remaining vendor weight alone when it is auth/runtime code (react-dom, auth client, router) — splitting those means an async auth refactor, which is a product change, not a perf win; say so instead of claiming a score you did not earn.

## Verdict discipline

- A perf score is a before/after pair against the same build type. Never compare a dev-server number to a production number.
- A passing metric under default throttling is not "clean": re-run CLS under CPU throttle, and re-run any motion-dependent audit with paints forced (see `motion-polish` — the document timeline does not advance unpainted).
- Report the metric values (FCP, LCP, TBT, CLS) alongside the category scores. A score can move on unrelated audits while the metric you were asked to fix stays broken.
