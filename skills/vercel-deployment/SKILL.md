---
name: vercel-deployment
description: Diagnose and fix production deployment issues for Next.js apps on Vercel — build failures, hydration errors, and config mismatches
category: vercel
---

# Vercel Deployment

Diagnose and fix production deployment issues for Next.js applications on Vercel — build failures, hydration errors, and configuration mismatches.

## When to use
- A Next.js app fails to build or deploy on Vercel
- Users report "this page couldn't load" or blank screen in production
- Quiz/button/interactive components don't respond to clicks on Vercel but work locally
- Debug Vercel build logs errors about missing artifacts

## Step-by-step diagnostic

### 1. Check build output first
```bash
cd /path/to/project
npm run build 2>&1
```
Note: Build passing locally does NOT guarantee Vercel will build — their environment differs.

### 2. Diagnose via curl (fastest)
```bash
# Check HTTP status and headers
curl -sI https://your-domain.com/ | grep -E "HTTP|X-Vercel|Vercel|Age"

# Check raw HTML for hydration markers
curl -s https://your-domain.com/ | grep -o "BAILOUT_TO_CLIENT_SIDE_RENDERING\|data-dgst\|out/routes-manifest\|_not-found"

# Check all pages return 200 (no redirects)
for page in "" "/quiz" "/library" "/feedback"; do
  echo -n "$page → "
  curl -s -o /dev/null -w "%{http_code} %{redirect_url}" "https://your-domain.com${page}"
  echo
done

# DIAGNOSE SITEMAP ISSUES (Google "couldn't fetch" errors):
# 1. Check sitemap XML is accessible
curl -sI https://your-domain.com/sitemap.xml | grep -E "HTTP/|Content-Type"
# 2. Check every URL in sitemap for redirects — 308 = trailing slash mismatch
for url in "" "/privacy" "/blog"; do
  echo -n "$url → "
  curl -s -o /dev/null -w "%{http_code} %{redirect_url}" "https://your-domain.com${url}"
  echo
done
# 3. If trailingSlash:true in next.config.ts, all sitemap URLs must have trailing slashes
```

### 3. Check browser console (via Hermes browser tools)
```js
// Look for js_errors and console_messages
browser_console()
// If body.innerHTML becomes 0 after interaction, hydration is failing
document.body.innerHTML.length  // 0 = catastrophic render crash
```

**Key markers to look for in raw HTML:**
| Marker | Meaning |
|--------|---------|
| `BAILOUT_TO_CLIENT_SIDE_RENDERING` | Component can't SSR — needs client hydration. If buttons don"t work, hydration is failing |
| `Loading quiz...` / spinner visible | SSRed fallback never replaced → hydration error |
| `out/routes-manifest.json` error | `outputDirectory` is wrong in vercel.json |

## Critical configuration rules

### `vercel.json` — `outputDirectory` (CRITICAL — get this right)
```json
{
  "framework": "nextjs",
  "outputDirectory": ".next"  // MUST be ".next" — see below
}
```
- **`outputDirectory` MUST ALWAYS be `".next"`** when using `"framework": "nextjs"`. This is NOT optional. Vercel's Next.js builder reads `.next/routes-manifest.json` for routing metadata, and that file only exists in `.next/` — regardless of whether `output: "export"` is set.
- **Setting `outputDirectory: "out"` WILL break the build.** Vercel will fail immediately with `The file "/vercel/path0/out/routes-manifest.json" couldn't be found` because `routes-manifest.json` lives in `.next/`, not `out/`. There is no scenario where `"out"` succeeds with `"framework": "nextjs"`.
- **If Vercel reports routes-manifest.json not found**: Check your `vercel.json` — it probably has `"outputDirectory": "out"`. Change it back to `".next"`.
- **Static export (`output: "export"`) + framework: "nextjs":** Works correctly when outputDirectory stays at `.next`. Vercel's builder detects the export mode, generates both `.next/` (for routing metadata) and `out/` (for static files), and serves from the correct directory. Changing `outputDirectory` to `"out"` breaks this — revert to `.next`.
- **No `vercel.json` at all** is the safest option for `framework: "nextjs"` — Vercel auto-detects Next.js and uses `.next` as the default.
- **Drag-drop method** (manual deployment via `vercel.com/new` with the `out/` folder) is a different deployment path entirely — it bypasses the framework builder and serves static files directly. This does NOT use `vercel.json` settings.

### `next.config.ts` — `output: "export"`
- **REMOVE IT IF**: Standard Next.js app with proper SSR patterns, API routes, or middleware. Vercel handles SSR/ISR natively.
- **KEEP IT IF**: App has complex `"use client"` mount patterns (nested `useEffect` + `mounted` guard chain, e.g. QuizLoader→AnimeQuiz), heavy Math.random() decoration (sakura petals, confetti), or uses localStorage on initial render. Static export eliminates ALL SSR/hydration mismatches at once.
- **GitHub import + `output: "export"` works fine** — as long as `outputDirectory` stays `.next`, Vercel's builder handles the static export correctly.

### Build layout comparison
| Config | `.next/` has | `out/` has | Vercel uses |
|--------|-------------|------------|-------------|
| With `output:"export"` | Manifests + cache + server | Static HTML+JS+CSS | `.next/routes-manifest.json` |
| Without `output:"export"` | Full Next.js build | Nothing | Everything from `.next/` |

## Common failure patterns

### Pattern A: Build fails ("routes-manifest.json not found")
**Error**: `/vercel/path0/out/routes-manifest.json` couldn't be found
**Fix**: Revert `outputDirectory` to `.next` in vercel.json

### Pattern B: Page loads but buttons/quiz don't work (hydration failure)
**Symptoms**:
- Spinner/loading text visible forever
- Clicking buttons does nothing
- `document.body.innerHTML.length` becomes 0 after clicking
- Browser console: `js_errors` with empty message
- Raw HTML contains `BAILOUT_TO_CLIENT_SIDE_RENDERING`

**Root causes**:
1. `output: "export"` was removed — add it back if app has complex client-only patterns (nested mount guards, localStorage, Math.random decorations)
2. Nested `"use client"` mount guards (QuizLoader → AnimeQuiz, both with `mounted` state) — fragile under SSR without static export
3. `Math.random()`-based styles (sakura petals, sticker GIF rotation) — causes hydration mismatch; use `suppressHydrationWarning` or static export
4. Invalid `turbopack` config in Next.js 16 — `turbopack: { root: process.cwd() }` is NOT valid and may corrupt the build. Just remove this key entirely.

**Detection** (via browser console after simulating a click):
```js
// After clicking a button that should trigger a re-render:
document.querySelector('main') !== null         // false = main element vanished → React crash
document.body.innerHTML.length                  // 0 = catastrophic crash, >0 = check content
document.body.innerHTML.includes('could not load')  // true = Next.js error boundary triggered
```
A crash during rendering causes Next.js to unmount the entire React tree and replace it with:
```html
<div><h1>This page couldn't load</h1><p>Reload to try again, or go back.</p></div>
```

**Fix hierarchy** (try in order):
1. Remove `output: "export"` AND fix hydration mismatches in component code  
2. RESTORE `output: "export"` — simplest if the site is fully static with no API routes. This eliminates all SSR/hydration issues in one shot.
3. If still broken, check for invalid `turbopack` or experimental config keys — Next.js 16 silently ignores some invalid keys but they can corrupt the build output.

### Pattern C: GitHub → Vercel auto-deploy not triggering
- Project imported via GitHub Import (no `.vercel/` directory in repo)
- Auto-deploy needs Vercel Settings → Git → "Configure Git Provider" enabled
- **Check if webhook exists:** `gh api repos/<owner>/<repo>/hooks --jq '.[].config.url'` — empty means no Vercel webhook

**Finding Vercel deployment errors via GitHub (no Vercel CLI access):**
1. Go to the commit page on GitHub — look for the check status badge (green ✓ / red ✗)
2. Click the status badge to open the dialog — it lists all checks including Vercel
3. If Vercel shows "Deployment has failed", it also displays a Vercel CLI command you can run:
   `npx vercel inspect dpl_XXXXX --logs` — but you need a valid Vercel token for this
4. The commit page also shows the error summary directly (e.g., "The file /vercel/path0/out/routes-manifest.json couldn't be found")

**Manual deploy fallback (use Vercel CLI token):**
  ```bash
  # Build and deploy in one command
  git push && npx vercel deploy --prod --yes --token <VERCEL_TOKEN>
  ```
  Get a token at https://vercel.com/account/tokens. The token starts with `vcp_` (new format). The project must be already linked to the Vercel account (first deploy or GitHub import sets this up).
- **Force redeploy:** `git commit --allow-empty -m "redeploy" && git push`
- **Check deployments:** `https://vercel.com/<username>/<project>/deployments`

### Pattern D: Sitemap URLs return 308 redirects — "couldn't fetch" in Google Search Console

**Symptoms:**
- Google Search Console reports "Couldn't fetch" for submitted sitemap
- The sitemap XML file loads fine, but URLs *inside* the sitemap redirect
- SEO tool shows redirect chains on listed URLs

**Root cause:**
- `trailingSlash: true` in `next.config.ts` — all pages 308-redirect from `/page` → `/page/`
- Sitemap lists URLs WITHOUT trailing slashes — every URL hits a 308 before reaching the real page
- Google treats redirects in sitemap URLs as fetch failures

**Diagnosis:**
```bash
# Check if sitemap URLs redirect
for url in "" "/privacy" "/blog" "/terms"; do
  echo -n "https://your-site.com${url} → "
  curl -s -o /dev/null -w "%{http_code} %{redirect_url}" "https://your-site.com${url}"
  echo
done
# 308 in output = redirect issue
```

**Fix:**
1. **If keeping `trailingSlash: true`** — update the sitemap to use trailing slashes on every URL:
   ```xml
   <loc>https://example.com/privacy/</loc>  <!-- not /privacy -->
   ```
   Update both `public/sitemap.xml` and the generation script that builds it.

2. **If removing `trailingSlash: true`** — update the sitemap to remove all trailing slashes.

3. **Static export rule:** for `output: "export"`, the sitemap must be a static file in `public/sitemap.xml` that gets copied to `out/` during build. Ensure the build script runs after `next build` to update both locations.

**Verification after fix:**
```bash
# Check all sitemap URLs return 200 with no redirect
curl -s -o /dev/null -w "%{http_code} %{redirect_url}" "https://your-site.com/privacy/"
# Expect: "200 "  (no redirect URL)
```

### Pattern E: GSC "Couldn't fetch" persists after sitemap fix — property mismatch

**Symptom:**
- All sitemap URLs return 200 with no redirects
- robots.txt references the correct sitemap URL
- But Google Search Console still reports "Couldn't fetch"
- The stale error persists even after re-submitting the sitemap

**Root cause:**
The GSC **property itself** doesn't match the sitemap URL's host. Google does NOT follow 307/308 redirects when verifying a property:
- Property = `https://example.com` (non-www) BUT sitemap is at `https://www.example.com/sitemap.xml` → Google gets a 308 from non-www to www → "Couldn't fetch"
- Property = `https://www.example.com` (www) BUT sitemap is at `https://example.com/sitemap.xml` → same redirect issue

**Diagnosis:**
```bash
# 1. Check which version is canonical (which one doesn't redirect)
echo "Non-www: $(curl -s -o /dev/null -w '%{http_code} -> %{redirect_url}' https://your-site.com/sitemap.xml)"
echo "Www:     $(curl -s -o /dev/null -w '%{http_code} -> %{redirect_url}' https://www.your-site.com/sitemap.xml)"
# The version that returns "200 " (no redirect) is the canonical

# 2. Check what property you have in GSC
# Must match the canonical version exactly
```

**Fix:**
1. Determine the canonical URL (www or non-www) from the diagnostic above
2. Delete the existing GSC property
3. Re-add as **URL prefix** with the exact canonical URL (e.g., `https://www.your-site.com`)
4. Re-verify ownership
5. Re-submit the sitemap
6. Click "Test" → if green ✅ → "Request Indexing"

**Cached errors:** Even after fixing the property, GSC may show the OLD "Couldn't fetch" from the previous failed crawl. Always use the **"Test"** button (live fetch) to see the real status, then "Request Indexing" to force a recrawl.

For comprehensive GSC troubleshooting including the "Test" workflow, see `saas-launch` skill's `references/google-search-console-setup.md`.

### Pattern E: JS bundles load but app doesn't hydrate
- Verify all `_next/static/chunks/*.js` return 200 via curl
- Count scripts: `document.querySelectorAll('script[src]').length` (expect 10+)
- If scripts load but hydration fails → see Pattern B

### Pattern F: Missing production env vars → 500 errors
**Symptom:** Site returns 500 after deploy but builds fine locally. `NEXT_PUBLIC_*` vars from `.env.local` are NOT auto-uploaded to Vercel.
**Fix:** Set env vars explicitly via CLI BEFORE deploying:
```bash
npx vercel env add NEXT_PUBLIC_SUPABASE_URL production
npx vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY production
```
Then redeploy. The CLI deploy (`npx vercel --prod`) picks up local `.env.local` files at build time but NOT as production runtime vars — Vercel reads from its own env store.
**Verify:** `npx vercel env ls` should show both vars under `production`.

## Deploy verification
```bash
# 1. HTTP status
curl -sI https://your-domain.com/ | head -5

# 2. robots.txt / sitemap.xml served
curl -s https://your-domain.com/robots.txt

# 3. Page content renders
curl -s https://your-domain.com/ | grep -c "expected text"

# 4. No hydration failure markers
curl -s https://your-domain.com/ | grep -c "BAILOUT_TO_CLIENT_SIDE_RENDERING"

# 5. Vercel cache status
curl -sI https://your-domain.com/ | grep "X-Vercel-Cache"

# 6. Full sitemap validation (requires bash + curl + python3)
# See scripts/validate-sitemap.sh for a reusable script
```
