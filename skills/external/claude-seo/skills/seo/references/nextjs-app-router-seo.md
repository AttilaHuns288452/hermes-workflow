# Next.js App Router SEO Patterns

Common SEO fixes and optimizations for Next.js App Router sites with static export on Vercel.

## Canonical Tags

Every page needs a `<link rel="canonical">`. In App Router, add it via the `alternates` field in the `Metadata` export:

```tsx
export const metadata: Metadata = {
  title: "Page Title",
  description: "Page description",
  alternates: {
    canonical: "https://yoursite.com/page-path",
  },
};
```

**Root layout:** all pages inherit the layout's metadata. Set the site-wide canonical on the root layout:

```tsx
// app/layout.tsx
export const metadata: Metadata = {
  metadataBase: new URL("https://yoursite.com"),
  alternates: {
    canonical: "https://yoursite.com",
  },
  // ... OG, twitter, robots
};
```

**Sub-pages:** override `alternates.canonical` with the page's own URL. This prevents the root canonical from leaking.

**Why it matters:** missing canonical tags are a **critical** SEO issue — Google may treat duplicate content (www vs non-www, trailing slash variants) as separate pages, diluting ranking signals.

## metadataBase

Set `metadataBase` to the production URL. This makes all relative URLs in metadata resolve correctly for OG images, canonical tags, and sitemap references:

```tsx
metadataBase: new URL("https://yoursite.com"),
```

Without it, Next.js logs a build warning and OG image URLs may break on social shares.

## Structured Data (JSON-LD)

Inject structured data in the root layout via a `<script type="application/ld+json">` tag. The App Router approach:

```tsx
export default function RootLayout({ children }) {
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "WebApplication",
    name: "Your App Name",
    description: "A short description",
    url: "https://yoursite.com",
    applicationCategory: "QuizApplication",  // or "WebApplication", "Game", etc.
    operatingSystem: "Web",
    offers: { "@type": "Offer", price: "0", priceCurrency: "USD" },
  };

  return (
    <html lang="en">
      <head>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
```

Common schema types for static sites:
- `WebApplication` — interactive tools, calculators, quizzes
- `WebSite` — general site identity
- `Article` / `BlogPosting` — for blog content pages

## Twitter Cards

Add Twitter card metadata alongside OG tags in the root layout metadata:

```tsx
twitter: {
  card: "summary_large_image",
  title: "Page Title for Twitter",
  description: "Description for Twitter",
  images: ["https://yoursite.com/og-image.png"],
},
```

## Affiliate Link Best Practices

External recommendation links in footers or affiliate disclosures should use:

```html
rel="noopener noreferrer nofollow"
```

The `nofollow` attribute tells Google not to pass PageRank to affiliate/paid destinations. Skipping it is a **medium** SEO risk — Google may interpret it as unnatural link patterns.

## Avoid Sponsored/H2 Headings for Paid Content

A heading like `<h2>Sponsored</h2>` on the homepage signals thin/spammy content to Google. Use a semantic but low-impact element (`<p>`, `<div>`) for sponsored sections instead of headings.

## Verification Checklist

After deploying SEO fixes:

- [ ] Every HTML page has `<link rel="canonical" href="https://...">` in `<head>`
- [ ] `metadataBase` resolves to production URL (no build warning)
- [ ] OG image URLs are absolute (include `https://`)
- [ ] Structured data renders in the page source
- [ ] Twitter card meta tags present
- [ ] robots meta is `index, follow` for public pages
- [ ] robots.txt and sitemap.xml exist and are valid
- [ ] Affiliate/external links have `rel="noopener noreferrer nofollow"`
