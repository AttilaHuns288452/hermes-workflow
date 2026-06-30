# Next.js Static Export + Vercel Deployment for Content Sites

This reference covers deploying AdSense-ready content overhauls on Next.js static export sites hosted via Vercel's GitHub integration. Both of the user's sites (`freelancecalculator.xyz`, `animewaifucompatibility.xyz`) follow this pattern.

## Project Structure (Next.js App Router)

```
app/
├── layout.tsx          # Root layout: metadata, scripts, footer, Google AdSense, GA4
├── page.tsx            # Homepage (tool + blog interlinking section)
├── about/page.tsx      # E-E-A-T foundation page
├── contact/page.tsx    # Contact form / email page
├── resources/page.tsx  # Dedicated affiliate tools page
├── blog/
│   ├── page.tsx        # Blog index (static array of post cards)
│   └── <post-slug>/
│       └── page.tsx    # Each blog post as a standalone page
├── terms/page.tsx
├── privacy/page.tsx
├── affiliate-disclosure/page.tsx
├── globals.css
└── tailwind-output.css
```

### Key Files

- `next.config.ts` — contains `output: "export"` for static generation
- `package.json` — build script: `"build": "next build && node scripts/generate-sitemap.js"`
- `scripts/generate-sitemap.js` — generates `public/sitemap.xml` with all 15+ URLs
- `public/sitemap.xml` — committed to git, updated at build time

## Blog Post Page Template

Every blog post follows this structure (TypeScript Next.js App Router):

```tsx
import { Metadata } from "next";
import Link from "next/link";
import Script from "next/script";

export const metadata: Metadata = {
  title: "Post Title (Updated 2026)",
  description: "Meta description for search.",
  alternates: { canonical: "https://domain.com/blog/post-slug" },
  openGraph: {
    title: "Post Title (Updated 2026)",
    description: "Meta description.",
    type: "article",
    publishedTime: "2024-01-15",           // ⚠️ Do NOT add "updatedTime" — not in Next.js TS types
  },
  twitter: { card: "summary_large_image", title: "...", description: "..." },
  authors: [{ name: "SiteName.com" }],
};

export default function BlogPost() {
  return (
    <>
      <Script id="article-schema" type="application/ld+json" dangerouslySetInnerHTML={{
        __html: JSON.stringify({
          "@context": "https://schema.org", "@type": "Article",
          headline: "Post Title (Updated 2026)",
          description: "...",
          datePublished: "2024-01-15", dateModified: "2026-06-28",
          author: { "@type": "Organization", name: "SiteName.com", url: "https://domain.com" },
          publisher: { "@type": "Organization", name: "SiteName.com", url: "https://domain.com" },
        }),
      }} />
      <article className="min-h-screen bg-gray-50 py-12 px-4">
        <div className="max-w-3xl mx-auto">
          <header>
            <Link href="/blog" className="...">← Back to Blog</Link>
            <time className="...">Published January 15, 2024 · Updated June 28, 2026 · 8 min read</time>
            <h1>Post Title (Updated 2026)</h1>
          </header>
          <div className="prose prose-lg max-w-none">{/* content */}</div>
        </div>
      </article>
      <p className="text-center text-xs text-gray-400 mt-4">
        Published January 2024 · Updated June 2026 by SiteName.com
      </p>
    </>
  );
}
```

### Critical Pitfalls

#### 1. `updatedTime` is NOT in Next.js TypeScript types

```tsx
openGraph: {
  publishedTime: "2024-01-15",
  // ❌ DO NOT add: updatedTime: "2026-06-28"
  // Type error: Object literal may only specify known properties,
  // 'updatedTime' does not exist in type 'OpenGraphMetadata | OpenGraphArticle'
}
```

**Fix:** Remove `updatedTime` from the `openGraph` object. Instead, put `dateModified` only in the JSON-LD Article schema via `<Script>`.

#### 2. Trailing slash routing on Vercel

New pages may return **308 redirect** (trailing slash enforcement) or **404** depending on how the URL is accessed:

| URL | Behavior |
|-----|----------|
| `https://domain.com/about` | 308 → `/about/` |
| `https://domain.com/about/` | 200 ✓ |
| `https://domain.com/blog/new-post` | Might 404 temporarily during deploy propagation |

**Fix:** In curl tests, use `-L` to follow redirects. In internal links, use paths WITHOUT trailing slashes (Next.js handles the redirect). Wait 1-2 minutes after git push for Vercel to propagate all routes.

## Build Pipeline

```bash
npm run build
# Runs: next build && node scripts/generate-sitemap.js
```

The build does NOT need the `generate:sitemap` step separately — the build script includes it.

### What Next.js 16.2 Static Export Produces

18 pages for the full content site (including `/`, `/about`, `/contact`, `/resources`, 7 blog posts, privacy, terms, affiliate-disclosure, blog index, _not-found).

## Deployment

### Vercel Auto-Deploy via GitHub Push (No CLI Auth Needed)

The vercel CLI is **not authenticated** on this machine. Deployment works purely via GitHub → Vercel integration:

```bash
git add -A
git commit -m "Content overhaul: new blog posts, resources page, schema updates"
git push origin master   # NOT 'main' — the default branch is 'master'
```

The push triggers Vercel's GitHub integration automatically. No `vercel deploy` or `vercel --prod` needed.

### .gitignore Must Include

```
/out/       # Next.js static export output
graphify-out/
.vercel
```

The `out/` directory from `next build` should never be committed.

## Verification After Deploy

Check new pages are live:

```bash
# Quick smoke test (follows redirects automatically)
curl -sL -o /dev/null -w "HTTP %{http_code}" https://domain.com/about/
curl -sL -o /dev/null -w "HTTP %{http_code}" https://domain.com/resources/
curl -sL -o /dev/null -w "HTTP %{http_code}" https://domain.com/blog/new-post-slug
curl -sL -o /dev/null -w "HTTP %{http_code}" https://domain.com/contact/

# All should return 200
```

If new pages return 404, wait 60 seconds and retry — Vercel deploys asynchronously after git push and routes take a moment to propagate.
