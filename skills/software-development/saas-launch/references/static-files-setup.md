# Static Files Setup for Next.js Sites

## `public/robots.txt`

```txt
User-agent: *
Allow: /
Sitemap: https://www.YOURDOMAIN.com/sitemap.xml
```

Replace `YOURDOMAIN.com` with the actual domain.

## `public/sitemap.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://www.YOURDOMAIN.com/</loc>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://www.YOURDOMAIN.com/blog</loc>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://www.YOURDOMAIN.com/privacy</loc>
    <priority>0.3</priority>
  </url>
  <url>
    <loc>https://www.YOURDOMAIN.com/terms</loc>
    <priority>0.3</priority>
  </url>
</urlset>
```

Add additional pages with appropriate priority levels:
- **1.0** — Homepage
- **0.9** — Main tool/quiz page
- **0.8** — Blog index
- **0.7** — Important content pages (library, recommendations)
- **0.5** — Feedback/contact pages
- **0.3** — Legal pages (privacy, terms)

## Vercel Behavior

- Files in `public/` are served at the root URL automatically — no build script, no copy to `out/` needed.
- `robots.txt` → `https://YOURDOMAIN.com/robots.txt`
- `sitemap.xml` → `https://YOURDOMAIN.com/sitemap.xml`
- This applies regardless of whether `output: "export"` is set.

## AdSense `ads.txt`

Create `public/ads.txt` with:

```
google.com, pub-YOUR_PUBLISHER_ID, DIRECT, f08c47fec0942fa0
```

Replace `YOUR_PUBLISHER_ID` with the AdSense publisher ID.
