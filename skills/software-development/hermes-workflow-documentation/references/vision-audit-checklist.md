# Vision Audit Checklist for Premium Website Overhaul

When MiMo (or any vision model) audits a site screenshot, ask for these specific
areas scored 1-10. This checklist produced a 5/10 → 8.5/10 improvement in one pass.

## Audit Questions

1. **Visual quality** — does it feel premium or cheap? What undermines it?
2. **Layout/spacing** — any cramped sections, missing whitespace, sections blurring together?
3. **Hierarchy** — can you distinguish section headings from subsection headings from content?
4. **Color usage** — is the palette consistent? Any clashing accent colors on interactive elements?
5. **Typography** — font sizes, weights, readability against the background?
6. **Section-by-section quality** — which sections are strongest? Which are weakest?
7. **What needs the most improvement** — the top 3-5 specific changes to reach premium feel?

## Fixes That Worked (session 2026-07-27)

| Problem | Fix | Impact |
|---------|-----|--------|
| All cards dumped at once | Show 8 per category + "Show more" button | Biggest single win — reduced overwhelm |
| Sections blur together | `section-pad: py-32 md:py-40` + section dividers | Clear visual separation |
| Weak heading hierarchy | h2 `clamp(2rem, 4vw, 3.5rem)`, card titles `text-base font-bold` | Scannable structure |
| Cramped SVG pipeline diagram | viewBox 172→220, rect h 44→56, font 9.5→11/12→14, max-w 620→720px | Readable diagram |
| Purple CTA clashing | CTA gradient `#4a8cf4 → #6bc5e8` (blue→cyan, no purple in interactive) | Cohesive palette |
| Low contrast card text | `#8895b8` → `#a0aec8` (brighter), `text-xs` → `text-sm` (larger) | Readable descriptions |
| No closing CTA | "Ready to build?" section before footer | Premium landing-page close |
| Cramped hero stats | min-w 88→110px, gap-2→gap-3, label text-[9px]→text-[10px] | Breathing room |
| Nav covers section tops | `scroll-mt-24` on all section ids | Clean anchor navigation |
| No nav hover feedback | Underline slide-in animation on hover | Polish |

## Post-Improvement Audit (MiMo scores)

| Area | Before | After |
|------|--------|-------|
| Visual quality | 6 | 8 |
| Spacing | 4 | 9 |
| Hierarchy | 5 | 9 |
| Color consistency | 5 | 8 |
| Text readability | 5 | 9 |
| Premium feel | 5 | 8 |

**Average: 5/10 → 8.5/10** (+70%)

## Firecrawl Screenshot URL Pitfall

**Problem:** Firecrawl returns signed GCS URLs that expire in ~5 minutes. Passing the raw signed URL to `vision_analyze` fails with 400/403 errors.

**Fix:** Download the screenshot locally first, then pass the local file path:
```python
import subprocess, os
url = "<firecrawl signed screenshot URL>"
path = os.path.expanduser("~/Documents/screenshot.png")
subprocess.run(["curl", "-sL", "-o", path, url], timeout=30)
# Then: vision_analyze(image_url=path, question="...")
```

The signed URL includes query params (GoogleAccessId, Expires, Signature) — without them the bare GCS URL returns 403.

## Second-Pass Improvements (session 2026-07-27, round 2)

| Problem | Fix | Status |
|---------|-----|--------|
| No copy button on install commands | `navigator.clipboard.writeText()` + "Copied!" green feedback 2s | ✅ Shipped |
| Long hero paragraph | 4 scannable ✓ bullet points with green checkmarks | ✅ Shipped |
| No trust signals | Truthful badges: "Open Source", "MIT License", "Free Models", "No API Key Required" | ✅ Shipped |
| Tool demo screenshot | **Skipped (YAGNI)** — the site IS the demo | Not doing |
| "10k+ Users" badge | **Rejected** — not factually true, would be a lie | Not doing |

## Second-Pass Audit (MiMo scores after round 2)

| Area | After R1 | After R2 |
|------|----------|----------|
| Visual quality | 8 | 8 |
| Spacing | 9 | 9 |
| Hierarchy | 9 | 9 |
| Color consistency | 8 | 8 |
| Text readability | 9 | 9 |
| Premium feel | 8 | 8 |

Scores held steady — R2 was polish (copy buttons, bullets, trust badges), not structural.

## Remaining Suggestions (not yet implemented)

1. Add tool demo screenshot/video in hero (skipped — YAGNI, the site IS the demo)
2. Mobile responsiveness audit (not yet tested via MiMo)

## Trust Badge Audit Rule

When adding trust badges, verify each claim is factually true:
- ✅ "Open Source" — repo is public with a LICENSE file
- ✅ "MIT License" — verify LICENSE file exists before claiming
- ✅ "Free Models" — true if the project uses free-tier models
- ✅ "No API Key Required" — true if free tier needs no key
- ❌ "10k+ Users" — do NOT fabricate user counts or social proof
- ❌ Any claim you cannot verify from the repo itself
