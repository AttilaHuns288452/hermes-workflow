# Manual SEO Audit (No Crawl Infrastructure)

When the full claude-seo Python-based crawl infrastructure is unavailable (missing python3, Playwright, or the required scripts), use Hermes browser/devtools tools for a manual audit. This approach covers the same categories but is hands-on rather than automated.

## What to Check

### On-Page (browser_console JavaScript)

```javascript
// Title & meta description
JSON.stringify({
  title: document.title,
  metaDesc: document.querySelector('meta[name="description"]')?.content,
  robots: document.querySelector('meta[name="robots"]')?.content,
  h1: document.querySelector('h1')?.textContent,
  h2s: [...document.querySelectorAll('h2')].map(h => h.textContent),
})

// Canonical & other link rel tags
[...document.querySelectorAll('link[rel]')].map(l => l.rel + ': ' + l.href)

// OG tags
[...document.querySelectorAll('meta[property^="og:"]')].map(m => m.getAttribute('property') + ': ' + m.content)

// Twitter cards
document.querySelector('meta[name="twitter:card"]')?.content

// Structured data
document.querySelector('script[type="application/ld+json"]')?.innerHTML?.slice(0, 100)

// Image alt check
[...document.querySelectorAll('img:not([alt])')].length + ' images missing alt text'
```

### Technical (web_extract / curl)

- `robots.txt` — present, correct `User-agent` and `Disallow` rules
- `sitemap.xml` — present, includes all pages, valid XML, recent lastmod dates
- Both accessible at the root of the domain

### Canonical URLs (Critical)

Every page MUST have a self-referencing canonical. Check via:

```javascript
document.querySelector('link[rel="canonical"]')?.href
```

**Next.js fix:** Add `alternates: { canonical: "https://..." }` to each page's `metadata` export.

### Google Index Status (web_search)

```text
site:example.com
```

Check how many pages Google has indexed vs total pages.

### Performance

Use PageSpeed Insights (manual URL check) or the `browser` tool's load speed observation.

### SEO Health Score (Simplified)

| Category | Weight | Check |
|----------|--------|-------|
| Title & Meta | 15% | browser_console |
| Canonical Tags | 15% | browser_console |
| OG/Twitter Cards | 10% | browser_console |
| Structured Data | 10% | browser_console |
| robots.txt | 5% | web_extract |
| Sitemap | 5% | web_extract |
| Alt Text | 5% | browser_console |
| Heading Structure | 5% | browser_console |
| Affiliate Links | 10% | browser_console |
| Index Status | 10% | web_search |
| Performance | 10% | PageSpeed / observation |
