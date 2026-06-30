# Worked Example: freelancecalculator.xyz AdSense Recovery

This is a real AdSense "low quality content" recovery for a freelance rate calculator site. The full content deliverables and implementation guide are at `~/Documents/Projects/freelancecalculator-content/`.

## Pre-Recovery State (What Was Flagged)

| Dimension | Status |
|-----------|--------|
| Editorial words on site | ~4,000 |
| Blog posts | 3 (all January 2024 — 2.5 years stale) |
| About page | None |
| Contact page | None |
| Affiliate placement | Footer of every page (6 links, "Sponsored" H2 heading) |
| Author attribution | None on any page |
| FAQ schema | None |
| Article schema | None |
| Last content update | January 2024 |

## The Transformation

| File Created | Words | Impact |
|-------------|-------|--------|
| `about-page.md` | ~1,200 | E-E-A-T foundation (author, mission, methodology) |
| `contact-page.md` | ~500 | Trust signal (email, response time) |
| `resources-page.md` | ~2,000 | Affiliate pages with proper disclosure |
| `homepage-how-it-works-section.md` | ~2,500 | Homepage content (methodology + FAQ) |
| `blog-freelancer-vs-employee-2026.md` | ~2,800 | New post (fresh, linkable) |
| `blog-retainer-rate-templates.md` | ~2,500 | New post (practical, template-focused) |
| `blog-self-employment-tax-2026.md` | ~3,200 | New post (seasonal, authoritative) |
| `blog-pricing-strategies.md` | ~3,100 | New post (comprehensive guide) |
| 3x existing post update guides | ~1,100 | Date freshness + author attribution |
| `content-plan.md` | ~800 | Master plan and audit findings |
| `implementation-guide.md` | ~2,500 | Exact file paths and deploy instructions |

## Post-Recovery State (Target)

| Dimension | Target |
|-----------|--------|
| Editorial words on site | ~22,000+ |
| Blog posts | 7 (all with current dates) |
| About page | Present (author, mission, methodology) |
| Contact page | Present (email, response time) |
| Affiliate placement | Single Resources page with disclosure |
| Author attribution | Every post has byline + link to About |
| FAQ schema | On homepage |
| Article schema | On every blog post |
| Most recent update | June 2026 (current) |

## Key Decisions Made

1. **Affiliates**: Moved from global footer to dedicated `/resources/` page. Footer now has a single "Resources →" link.
2. **Blog structure**: All posts link back to the calculator at least twice. Posts cross-link to each other.
3. **Dates**: Original dates preserved with "Updated June 2026" appended, rather than replacing dates entirely.
4. **Author byline**: Consistent persona across all posts with link to About page.
5. **Schema**: FAQPage on homepage (even though FAQ rich results were deprecated — still aids AI parsing).
6. **Methodology**: Expanded by default (not hidden behind a click), with full transparency about assumptions.

## Topics That Worked for This Calculator Niche

- "Freelancer vs Employee Cost Comparison (2026)" — comparison format, high shareability
- "Self-Employment Tax Guide (2026)" — seasonal/evergreen, solves real pain point
- "Retainer Rate Calculation + Templates" — practical tool-adjacent content
- "Pricing Strategies Comparison" — comprehensive guide, links well to calculator

## Lessons

- Calculator sites need 7+ editorial posts minimum for AdSense, not 3
- Affiliate links in the footer are a red flag — move to a dedicated page
- About + Contact pages are non-negotiable for YMYL-adjacent sites
- Blog posts all dated the same month = content dump signal. Stagger or backdate.
- FAQPage schema matters even though rich results were deprecated — AI citation still uses it
- Author bylines on every post are the cheapest E-E-A-T win available
