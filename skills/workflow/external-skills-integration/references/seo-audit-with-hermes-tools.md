# Live SEO Audit with Hermes Browser & Web Tools

The claude-seo skills assume Claude Code tooling (`Read`, `Write`, `Edit`, `Bash`, web-extraction). This reference maps each audit task to Hermes equivalents so you can run full SEO audits without Claude Code.

## Canonical SEO Audit Recipe

### Step 1 — Check Live Page Metadata

```javascript
// Run in browser_console(expression=...)
JSON.stringify({
  title: document.title,
  metaDesc: document.querySelector('meta[name="description"]')?.content,
  canonical: document.querySelector('link[rel="canonical"]')?.href,
  h1: document.querySelector('h1')?.innerText,
  h2s: [...document.querySelectorAll('h2')].map(h => h.innerText),
  ogTitle: document.querySelector('meta[property="og:title"]')?.content,
  ogImage: document.querySelector('meta[property="og:image"]')?.content,
  robots: document.querySelector('meta[name="robots"]')?.content,
  structuredData: document.querySelector('script[type="application/ld+json"]')?.innerHTML?.slice(0,120),
  twitterCard: document.querySelector('meta[name="twitter:card"]')?.content,
  links: [...document.querySelectorAll('link[rel]')].map(l => l.rel + ': ' + l.href),
  imgsMissingAlt: [...document.querySelectorAll('img:not([alt])')].length,
})
```

### Step 2 — Check Robots & Sitemap

```python
# web_extract for remote files
web_extract(urls=[
  "https://example.com/robots.txt",
  "https://example.com/sitemap.xml"
])
```

### Step 3 — Check Google Indexing

```python
web_search(query="site:example.com", limit=10)
```

### Step 4 — Check Page Speed (Visual)

Use `browser_navigate` to PageSpeed Insights, or check TTFB in console:

```javascript
performance.timing.responseStart - performance.timing.navigationStart
```

For static exports on Vercel, TTFB < 100ms is common.

### Step 5 — Check All Subpages by Inspecting Built Output

```bash
# For Next.js static export
grep 'rel="canonical"' out/index.html         # homepage canonical
grep 'rel="canonical"' out/blog/index.html    # blog canonical
# Count all pages with canonicals
grep -r 'rel="canonical"' out/ | wc -l
# Check for structured data
grep -r 'ld+json' out/ | head -5
```

## Fixing Issues in Next.js App Router

### Canonical Tags

Add to the `metadata` export in any page/layout:

```typescript
export const metadata: Metadata = {
  title: "...",
  description: "...",
  alternates: {
    canonical: "https://example.com/page-path",
  },
  // ...
};
```

Add `metadataBase` in root layout for correct OG image resolution:

```typescript
metadataBase: new URL("https://example.com"),
```

### Structured Data (JSON-LD)

Add in the `<head>` of your root layout:

```tsx
<script
  type="application/ld+json"
  dangerouslySetInnerHTML={{
    __html: JSON.stringify({
      "@context": "https://schema.org",
      "@type": "WebApplication",  // or QuizApplication, Article, etc.
      name: "...",
      description: "...",
      url: "https://example.com",
      applicationCategory: "BusinessApplication",
      operatingSystem: "Web",
      offers: { "@type": "Offer", price: "0", priceCurrency: "USD" },
      featureList: ["Feature 1", "Feature 2"],
    }),
  }}
/>
```

### Nofollow on Affiliate Links

```tsx
<a href="https://partner.com" target="_blank" rel="noopener noreferrer nofollow">Link</a>
```

## Deployment (Vercel + GitHub)

Both sites auto-deploy from GitHub master. The push pattern:

```bash
npm run build                           # verify no errors
git add -A && git commit -m "SEO: ..."  # commit
git push origin master                   # triggers Vercel deploy
```

## Tool Mapping (Claude Code → Hermes)

| Claude Code | Hermes Equivalent | Notes |
|-------------|------------------|-------|
| `Read` file | `read_file()` | Same function |
| `Edit` file | `patch()` | Fuzzy matching handles whitespace |
| `Write` file | `write_file()` | Same function |
| `Bash` command | `terminal()` | Same function |
| Web content | `web_extract(urls=[])` | Use for robots.txt, sitemap.xml, plain URLs |
| Browser/JS page | `browser_navigate()` + `browser_console()` | Use for JS-rendered pages, DOM inspection |
| Search results | `web_search()` | Use for `site:` queries, keyword research |
| Python script | `termin...(continued) 