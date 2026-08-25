# Next.js Static Export SEO Hygiene — 2026-08 (both sites)

Dual-site pass: `freelance-rate-calculator` (periwinkle, 15 pages) + `anime-waifu-quiz` (427 char pages). Both `output: "export"` static on Vercel.

## Fixes shipped as `b7e3fba` + `6611b55`

**1. robots.txt Crawl-delay removal**
- Found: freelance `scripts/generate-sitemap.js` wrote `Crawl-delay: 10` into `public/robots.txt` + `out/robots.txt`.
- Harm: throttles crawl budget; Bing obeys, Google nominally ignores but signal is negative. No benefit for static sites.
- Fix: removed `Crawl-delay` lines from `scripts/generate-sitemap.js` template + overwrote `public/robots.txt` to `Allow: /` + `Sitemap:` only. Regens on every `npm run build` via script, so script fix is the durable one.
- Verify: `curl /robots.txt` — no `Crawl-delay`, only `Allow` + `Sitemap`.

**2. Canonical ↔ sitemap ↔ trailingSlash alignment**
- freelance has `next.config.ts: trailingSlash: true` + `output: "export"` → sitemap uses `/blog/.../` with slash, pages emit `/blog/.../index.html`. Canonicals must match or Google sees duplicates.
- Found: 7 blog `page.tsx` canonicals were `https://freelancecalculator.xyz/blog/slug` (no slash) while sitemap + file path had trailing slash.
- Fix: one-liner loop (node) to add trailing slash to all `canonical:` strings in `app/blog/*/*.tsx`. Keep `layout.tsx` root canonical as `https://freelancecalculator.xyz/` (with slash) to match `PAGES[0] url: ""` → sitemap `<loc>https://...` (root sitemap omits slash; Next metadata adds consistency).
- anime has *no* `trailingSlash` → canonical stays `https://www.animewaifucompatibility.xyz` (no slash) and sitemap `/quiz` (no slash) — do not add slashes there. Rule: sitemap.url === canonical exactly.
- Verify: `curl /` → `rel="canonical" href=".../"` matches sitemap `<loc>`, same for `/blog/.../` pages.

**3. Title template + robots googleBot**
- Both layouts had `title: string` + `robots: "index, follow"` (string).
- Fix: `title: { default: "...", template: "%s | Freelance Calculator" }` (and `"%s | Anime Waifu Quiz"`) so every subpage (blog, character) gets branded suffix automatically. `robots: { index: true, follow: true, googleBot: { index: true, follow: true, "max-image-preview": "large", "max-snippet": -1, "max-video-preview": -1 } }` unlocks large image previews, unlimited snippets.
- Verify: view source on `/blog/.../` — `<title>Post Title | Freelance Calculator</title>`; meta robots includes `max-image-preview:large`.

**4. What was *not* changed (and when to)**
- No new package (`next-sitemap`, `seo-*` skill) — `scripts/generate-sitemap.js` already covers 15 + 434 URLs and runs in `build` (`next build && node scripts/...`). Add a package only for image/news sitemap or i18n.
- No `app/sitemap.ts` — would duplicate the script; keep one source of truth.
- No manual `<link rel="icon">` — Next auto-discovers `app/icon.*` (see favicon refs).

## Checklist for next static export SEO pass

1. `cat public/robots.txt` — no `Crawl-delay`, has `Sitemap: https://<domain>/sitemap.xml`.
2. `grep -r "canonical" app/` — every canonical ends with `/` iff `trailingSlash: true`, else without. Compare to `grep -o "<loc>[^<]*" public/sitemap.xml`.
3. `grep -n "title" app/layout.tsx` — object with `default` + `template`, not plain string.
4. `grep -n "robots" app/layout.tsx` — object with `googleBot`, not string.
5. `npm run build` both — freelance `18/18` + `Sitemap, robots.txt, and ads.txt generated`, anime `427 characters` sitemap.

Skipped: hreflang (single locale), HowTo schema (deprecated Sept 2023), FAQ rich results (retired 2026-05) — not applicable to these tool/quiz sites. Add when i18n or real Q&A pages exist.
