# Next.js SEO Fix Patterns (Vercel Static Export)

Fix patterns discovered during hands-on SEO remediation of two Next.js sites. These complement the `seo-audit-with-hermes-tools.md` audit recipe.

## Pattern 1: Client-Component H1 Trap

**Symptom:** SEO audit shows multiple `<h1>` elements, but you only see one in `page.tsx`.

**Root cause:** Client components (in `app/services/`, `components/`, or `lib/`) can render their own `<h1>` tags. These aren't visible in the route metadata or server-component inspection. The `<QuizLoader>` wraps `<AnimeQuiz>` which has its own `<h1>` that search engines see.

**Fix:** Search ALL `.tsx` files in the project, not just routes:
```bash
grep -r '<h1' app/ components/ services/ lib/
```
Change any non-route `<h1>` to `<h2>` or lower, preserving the className.

```diff
- <h1 className="text-3xl font-bold">Which Anime Match Are You?</h1>
+ <h2 className="text-3xl font-bold">Which Anime Match Are You?</h2>
```

**Verification:** After deploying, use `document.querySelectorAll('h1')` in browser_console to confirm count = 1.

---

## Pattern 2: OG Tags Per Page — Override Layout Defaults

**Symptom:** OG tags on subpages show the homepage title/URL.

**Root cause:** Layout.tsx sets global `openGraph` defaults. Pages that export their own `title` and `description` get those overridden in `<title>`, but the `openGraph` object from layout is NOT auto-overridden by page-level `title`. You must explicitly include `openGraph` and `twitter` in each page's metadata export.

**Fix — each subpage's `metadata` export:**

```typescript
export const metadata: Metadata = {
  title: "Subpage Title",
  description: "Subpage description.",
  alternates: {
    canonical: "https://example.com/subpage",
  },
  openGraph: {
    url: "https://example.com/subpage",
    title: "Subpage Title — Site Name",
    description: "Subpage description for social shares.",
    images: [{ url: "/og-image.png", width: 1200, height: 630, alt: "Subpage OG alt text" }],
  },
  twitter: {
    card: "summary_large_image",
    title: "Subpage Title — Site Name",
    description: "Shorter version for Twitter.",
    images: ["/og-image.png"],
  },
};
```

Fields that MUST be per-page:
- `openGraph.url` — correct canonical for the page
- `openGraph.title` — page-specific, not just `title` (Next.js does NOT auto-inherit)
- `twitter.title` — same reason
- `alternates.canonical` — correct per page

Fields that can stay in layout default:
- `openGraph.siteName`
- `openGraph.locale`
- `twitter.card`
- `openGraph.images[].width/height`
- `metadataBase`

---

## Pattern 3: Sitemap Generation for Static Export

**Symptom:** Sitemap only lists 7 top-level pages, missing all dynamic content.

**Root cause:** Next.js static export (`output: "export"`) doesn't auto-generate a sitemap for non-dynamic routes. You need a build-time script.

**Script pattern — `scripts/generate-sitemap.js`:**

```javascript
const fs = require("fs");
const path = require("path");

const BASE_URL = "https://www.example.com";
const PAGES = [
  { url: "", changefreq: "weekly", priority: 1.0 },
  { url: "/page2", changefreq: "weekly", priority: 0.8 },
  // ... all pages
];

function generateSitemap() {
  const today = new Date().toISOString().split("T")[0];
  const urls = PAGES.map(p => `  <url>
    <loc>${BASE_URL}${p.url}</loc>
    <lastmod>${today}</lastmod>
    <changefreq>${p.changefreq}</changefreq>
    <priority>${p.priority}</priority>
  </url>`).join("\n");
  const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls}\n</urlset>`;

  // Write to BOTH locations:
  fs.writeFileSync(path.join(__dirname, "..", "public", "sitemap.xml"), sitemap);
  try {
    fs.writeFileSync(path.join(__dirname, "..", "out", "sitemap.xml"), sitemap);
  } catch (_) { /* out/ may not exist yet */ }
  console.log(`✅ Sitemap: ${PAGES.length} pages`);
}
generateSitemap();
```

**Wire into `package.json`:**
```json
"build": "next build && node scripts/generate-sitemap.js"
```

**Why both locations:** `public/` is copied to `out/` during `next build`. But writing to `out/` explicitly covers edge cases where the sitemap needs updating post-build (e.g., from dynamic data that changed during build).

---

## Pattern 4: Stale Character/Content Count — Update Everywhere

**Symptom:** Site grew from 70 to 427+ characters, but metadata, body text, and structured data still say "70+".

**Fix — search for ALL occurrences and update every one:**

| Where to search | Example fix |
|----------------|-------------|
| `app/layout.tsx` metadata.description | `"Featuring 70+ characters" → "Featuring 427+ characters"` |
| `app/layout.tsx` openGraph.description | Same |
| `app/layout.tsx` LD+JSON featureList | `"70+ anime characters" → "427+ anime characters"` |
| `app/page.tsx` metadata.description | Same |
| `app/page.tsx` body text | Same |
| `app/library/page.tsx` title/description | Same |
| `app/quiz/page.tsx` description | Same |

Use `grep -r "70+" app/ --include="*.tsx"` to find every stale reference.

When updating structured data (LD+JSON), also update the `description` field inside the JSON, not just the React metadata.

---

## Pattern 5: Deploy and Verify

After pushing to GitHub (Vercel auto-deploy):

1. Wait ~30–60s for deploy
2. Verify with browser_console:
   ```javascript
   // Heading count
   document.querySelectorAll('h1').length
   // OG tags
   document.querySelector('meta[property="og:title"]')?.content
   // Canonical
   document.querySelector('link[rel="canonical"]')?.href
   // Structured data
   JSON.parse(document.querySelector('script[type="application/ld+json"]')?.innerHTML || '{}').featureList
   ```
3. Check subpage OG tags by navigating to each subpage
4. Verify sitemap: `web_extract(["https://example.com/sitemap.xml"])`

---

## Pattern 6: Next.js 15+ themeColor Migration (Viewport Export)

**Symptom:** Build shows warnings per route:
```
⚠ Unsupported metadata themeColor is configured in metadata export in /page.
Please move it to viewport export instead.
```
Build still succeeds, but warnings clutter output and may confuse structured-data validators.

**Root cause:** Next.js 15+ moved `themeColor` out of the `Metadata` type into a separate `Viewport` type. The old metadata field still works but emits deprecation warnings.

**Fix — add a `viewport` export to root layout:**

```typescript
import type { Metadata, Viewport } from "next";

export const viewport: Viewport = {
  themeColor: "#1d4ed8",
};

export const metadata: Metadata = {
  // ...existing fields, but DELETE themeColor from here
};
```

**Verification:** Rebuild and confirm zero warnings:
```bash
npm run build 2>&1 | grep -c "themeColor"
# should return 0
```

**Per-page override:** Export `viewport` in individual pages for route-specific colors.
