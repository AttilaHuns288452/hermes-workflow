---
name: tool-site-content
description: >-
  Content improvement strategy for tool, calculator, and interactive SaaS sites
  that get flagged as "low quality content" by Google/AdSense. Covers the full
  expansion pattern: E-E-A-T foundation pages, homepage content, blog/library
  build-out, affiliate disclosure cleanup, and structured data.
triggers:
  - "AdSense rejected"
  - "low quality content"
  - "calculator site content"
  - "tool site SEO"
  - "thin content site"
  - "SaaS site needs content"
  - "not enough text on site"
  - "affiliate site content"
---

# Tool & Calculator Site Content Strategy

## When to Use This Skill

This skill is for sites where the primary value is a tool, calculator, interactive app, or database — but Google/AdSense flags the site for "low quality content" because the editorial text around the tool is minimal.

**Classic symptoms:**
- AdSense rejection says "low quality content" or "insufficient content"
- Site has 2-3 blog posts, all from the same date 2+ years ago
- No About page, no Contact page
- Affiliate links in footer/sidebar on every page
- Homepage is just the tool UI + a paragraph
- No author attribution anywhere

## The 5-Phase Overhaul Pattern

### Phase 1 — E-E-A-T Foundation Pages (build identity)

Create these BEFORE touching the tool page. They establish the site as a real entity, not a thin affiliate/tool page.

| Page | Purpose | Min Words | Key Elements |
|------|---------|-----------|--------------|
| **About** | Who built this, why it exists, methodology, credentials | 800+ | Author bio, site mission, methodology transparency, disclaimer, real credentials or "why we built this" story |
| **Contact** | How to reach the operator | 400+ | Email, response time promise, bug report template, partnership inquiry info |
| **Resources** | Dedicated affiliate/tool recommendations page | 1,500+ | Above-the-fold affiliate disclosure, honest reviews, pro/con per tool, direct links |

**⚠️ Critical pitfall:** Remove ALL affiliate links from page footers and global navigation. Replace them with a single "Resources →" nav link pointing to the dedicated resources page. Footer affiliate links on every page is a strong "low quality" signal for AdSense.

### Phase 2 — Expand the Homepage / Tool Page

The tool page itself needs substantial editorial content:

1. **Expanded Methodology Section** (1,500-3,000 words)
   - Step-by-step explanation of how the tool works
   - What each input/parameter means
   - Where assumptions come from
   - Data sources and update frequency
   - Make this expanded by default (not hidden behind a click)

2. **FAQ Section** (5-10 questions)
   - Answer genuine user questions about the tool's use case
   - Implement as FAQPage structured data (yes, even though FAQ rich results were deprecated — the markup still helps AI parsing)

3. **Social Proof / "Who This Is For"** callout
   - Brief use-case descriptions, user counts, or testimonials

4. **⚠️ Fix Content Visibility — Diagnose What Users Actually See**
   Tool sites often bury blog posts, guides, and CTAs below the fold behind collapsed details, feedback forms, or affiliate link sections. Use `browser_navigate` to check DOM order — if blog cards appear after `DisclosureTriangle` or `details` elements, users never see them.

   **Restructuring pattern:**
   - **Verify section order** via browser snapshot — blog/content should appear BEFORE methodology and FAQ sections, not at the very bottom
   - **Replace `<details>`** with permanently visible sections (card grids, numbered steps) — collapsed elements hide SEO content from both users and crawlers
   - **Remove distractions from tool output** — feedback forms, affiliate links, and upsells inside calculator/form results destroy trust and push content down the page. Move them to dedicated pages (Contact, Resources)
   - **Add scroll-to-section anchors** — every major section needs an `id` so bottom-of-page CTAs can scroll back up: `#calculator`, `#guides`, `#how-it-works`, `#faq`
   - **Sticky nav header** — on pages over 1 viewport, add `sticky top-0 z-50 bg-white/80 backdrop-blur-md` header with links to calculator, blog, resources, about
   - **Hero with trust badges** — gradient hero with "100% free", "No signup needed", "Updated [year]" badges above the tool for immediate credibility

   **Layout priority (good):**
   ```
   Hero → Calculator → Blog cards (visible!) → Methodology → Undercharge explainer → FAQ → CTA
   ```

   **Layout priority (bad — content buried):**
   ```
   Hero → Calculator → [collapsed <details> methodology] → [collapsed FAQ] → Feedback form → Blog cards
   ```

   See `references/content-visibility-ux.md` for the full diagnosis + fix pattern with code examples.

### Phase 3 — Content Library Build-Out

A tool site needs enough written content that the "blog" or "guides" section reads as an active resource. Target 7+ posts minimum.

**Content strategy for tool adjacency:**
- Each post should cover an adjacent topic that links back to the tool
- For a rate calculator: "Freelancer vs Employee", "Tax Guide 2026", "Pricing Strategies"
- For a health calculator: "How X affects Y", "Common misconceptions about X"
- For a finance tool: "Tax guide", "Saving strategies", "Comparison articles"

**Post structure:**
- 2,000-3,500 words each
- Author byline with link to About page
- `datePublished` + `dateModified` in metadata
- 2-3 internal links to tool page and other posts
- Article structured data

**Existing post updates:**
- Change stale dates (e.g., "2024" → "Updated June 2026")
- Refresh outdated numbers (tax brackets, limits, prices)
- Add "Published [date] · Updated [date]" header
- Add author byline at both top and bottom

### Phase 4 — Structured Data

Every page needs appropriate schema markup:

| Page Type | Schema | Required Fields |
|-----------|--------|-----------------|
| Homepage / Tool | FAQPage (for the FAQ section) | `@type: Question`, `name`, `acceptedAnswer` |
| Blog posts | Article | `headline`, `description`, `author` (Person), `datePublished`, `dateModified`, `publisher` (Organization) |
| About | Person or Organization | `name`, `description`, `url` |
| Site-wide | WebSite + Organization | `name`, `url`, `description`, `potentialAction` (SearchAction) |

### Phase 5 — Site-Wide Polish

- Active navigation with Blog, About, Resources links
- Privacy policy + Terms of Service in footer
- Cookie consent if using analytics
- Fast page load (<2s for the tool page)
- Consistent design and visual polish
- No broken internal links

## Content Volume Targets

| Metric | Before (Flagged) | After (Re-review Ready) |
|--------|-----------------|------------------------|
| Total editorial words | ~4,000 | 20,000-30,000+ |
| Number of pages | ~5 | 10+ |
| Blog posts | 2-3 | 7+ |
| About/Contact pages | None | 2 |
| E-E-A-T signals | None | Author, credentials, contact, methodology |
| Most recent update | 2+ years ago | Current month |
| Affiliate placement | Global footer | Dedicated page + disclosure |
| Schema markup | None | FAQPage + Article + Organization |

## AdSense Rejection Response Flow

When user says "AdSense rejected my site for low quality content":

1. **Audit** — Check homepage content volume, number of posts, About/Contact existence, affiliate placement, date freshness, author attribution
2. **Identify phase gaps** — Which of the 5 phases is weakest? (Usually phases 1 and 3)
3. **Create E-E-A-T pages first** — About, Contact, Resources (fastest win)
4. **Expand homepage content** — Methodolody + FAQ (biggest impact single change)
5. **Add blog posts** — 3-4 minimum to show active publishing (volume signal)
6. **Update existing content** — Fresh dates, accurate numbers (freshness signal)
7. **Add structured data** — FAQPage + Article + Organization (machine-readable E-E-A-T)
8. **Clean up affiliates** — Move to dedicated page, add disclosure (trust signal)
9. **Resubmit to AdSense** — Only after all 5 phases are deployed

## Common Pitfalls

| Mistake | Why It Fails | Correct Approach |
|---------|-------------|------------------|
| Adding more tool pages instead of editorial content | More tools = more thin pages | Add editorial content around the existing tool |
| Keeping affiliate links in the footer | Looks like an MFA (Made for AdSense) site | Move to a dedicated Resources page |
| Publishing all blog posts on the same date | Looks like a content dump | Stagger posts or backdate them, add update dates |
| Hiding methodology behind a click | Google's crawlers may not see it | Expand by default |
| No author attribution | Zero E-E-A-T signal | Author bylines on every post + About page |
| Thin privacy/terms pages | Missing trust signals | Comprehensive privacy policy + ToS |
| Skipping structured data | Missed machine-readable E-E-A-T | Always add FAQPage + Article schema |
| Feedback form inside calculator/form output | Survey fatigue before value; pushes content down the page | Move feedback to a Contact page or dedicated feedback page |
| Affiliate/Sponsored links in calculator results | Feels spammy; distracts from core value; competing CTA | Move to a dedicated Resources page with above-the-fold affiliate disclosure |

## Next.js Implementation

When the target site is a Next.js App Router project with `output: "export"` (both of this user's sites use this stack):

- **Blog posts** are standalone `app/blog/<slug>/page.tsx` files, not markdown — each needs Metadata + Script(Article schema) + article layout
- **Build command**: `npm run build` (runs `next build && node scripts/generate-sitemap.js`) — the sitemap generator is part of the build script
- **Deployment**: git push to `origin master` → Vercel auto-deploy (no Vercel CLI auth needed)
- **`.gitignore`** must exclude `/out/`, `graphify-out/`, `.vercel`

See `references/nextjs-vercel-deployment-patterns.md` for the full page template, deploy commands, and curl verification snippets.

### TypeScript Pitfall: `updatedTime` in OpenGraph

Next.js `Metadata` type does NOT include `updatedTime` in `openGraph`. Adding it causes build failure:

```
Type error: Object literal may only specify known properties,
and 'updatedTime' does not exist in type 'OpenGraphMetadata | OpenGraphArticle'
```

**Fix:** Remove `updatedTime` from the `openGraph` object. Use `dateModified` only in the JSON-LD `<Script id="article-schema">` block.

### Build Error: Raw `<script>` Tags Inside Client Components

When adding inline JavaScript (e.g., AdSense init, analytics hooks) inside a **client component** (`"use client"`), raw `<script>` tags in JSX cause a Turbopack build error:

```
Expected '</', got ';'
   <script>{(adsbygoogle = window.adsbygoogle || []).push({});}</script>
                                                        ^
```

**Root cause:** JSX parses `{...}` as expression slots. Raw `<script>` tags with curly braces break the parser.

**Fix:** Use the Next.js `Script` component from `next/script` with `dangerouslySetInnerHTML`:

```tsx
import Script from "next/script";
// ...
<Script id="adsense-init" strategy="lazyOnload" dangerouslySetInnerHTML={{
  __html: `(adsbygoogle = window.adsbygoogle || []).push({});`
}} />
```

Always use `dangerouslySetInnerHTML` or the `Script` component for JavaScript injection in JSX. This applies to both server components (via `next/script`) and client components (via `next/script` with appropriate `strategy`).

## Verification Checklist

When the work is deployed, verify before telling the user to resubmit:

- [ ] Homepage has 1,500+ words of editorial content
- [ ] About page has author bio and credentials
- [ ] Contact page has email and response time
- [ ] Resources page has proper affiliate disclosure
- [ ] 4+ new blog posts or guides published
- [ ] All existing posts updated with current dates
- [ ] Every blog post has author byline + update date
- [ ] Footer affiliate links removed (replaced with nav link)
- [ ] FAQPage schema is on homepage/tool page
- [ ] Article schema on each blog post
- [ ] Sitemap includes all new pages
- [ ] Navigation has Blog, About, Resources links
- [ ] No broken internal links
- [ ] Build succeeds with `npm run build` (zero TS errors)
- [ ] New page routes return 200 (curl -sL check)
- [ ] Trailing-slash routing works (308 → 200 with -L)
- [ ] Sitemap regenerated with all new URLs
- [ ] Git push triggered Vercel deploy (verify via site access, not CLI)
