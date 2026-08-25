# Premium Calculator Overhaul — Reference

Source session: freelance-rate-calculator premium UI/UX overhaul (Aug 2026).
Repo: `C:\Users\Attila\Documents\Projects\freelance-rate-calculator` — Next.js App Router + Tailwind v4, `output: export`.

## Scope

A) RateCalculator + ResultCard, B) page.tsx + layout.tsx, C) global polish. Math untouched in `lib/calculations.ts` (6 presets, `calculateFreelanceRate`).

## Files Changed

- `app/globals.css` — `@import "tailwindcss"` + `@theme`, slider thumb 18px + shadow + scale, `@keyframes shake`, `.card`, `@media print`
- `components/RateCalculator.tsx` — 356→~400 lines. Added `icon` to FieldMeta, `sliderFill()`, lifestyle preview, `localStorage` (frc-preset/frc-inputs), clamps + shake, `fieldCard()` pattern, `[1.1fr_0.9fr]` sticky
- `components/ResultCard.tsx` — 101→~220 lines. Added `useCountUp`, delta badge, stacked bar, share, empty state
- `app/page.tsx` — hero mesh (3 blobs + 32px grid), guides hover lift, How It Works timeline (center w-px + dots), Why Undercharge dark card, FAQ pill chevron, final CTA, CLS wrappers
- `app/layout.tsx` — footer `max-w-6xl` + pill CTA polish
- `components/AdBannerFreelance.tsx` — `rounded-2xl` + dashed placeholder
- `components/EmailCapture.tsx` — NEW `"use client"` extracted form (fixes prerender)

## FieldMeta Pattern

```ts
interface FieldMeta {
  key: FieldKey; label: string; suffix: string; step: number; min: number; max?: number;
  isPercent?: boolean; help: string; tip?: string; group: "lifestyle"|"costs"; slider?: boolean; icon: string;
}
const FIELDS: FieldMeta[] = [ /* 8 fields */ ];
function sliderFill(f: FieldMeta, disp: number) {
  const pct = ((disp - f.min)/(f.max! - f.min))*100;
  return `linear-gradient(to right, #2563eb 0%, #3b82f6 ${pct}%, #e5e7eb ${pct}%, #e5e7eb 100%)`;
}
```

## Build Transcript

Failure on first `npm run build`:

```
Error occurred prerendering page "/"
Error: Event handlers cannot be passed to Client Component props.
  {onSubmit: function onSubmit, ...}
```

Fix: extracted `onSubmit` form to `components/EmailCapture.tsx` (`"use client"`), imported into `app/page.tsx` (Server Component).

Success on second build:

```
✓ Compiled successfully in 7.5s
✓ Generating static pages (18/18) in 2.0s
Route (app)
┌ ○ /
├ ○ /_not-found
├ ○ /about
├ ○ /affiliate-disclosure
├ ○ /blog
├ ○ /blog/freelance-hourly-rate-calculator-guide
├ ○ /blog/freelance-pricing-strategies-value-based
├ ○ /blog/freelance-retainer-rate-calculator-templates
├ ○ /blog/freelance-tax-deductions-calculator-write-offs
├ ○ /blog/freelancer-vs-employee-cost-comparison-2026
├ ○ /blog/how-much-to-charge-freelancer-day-rate-vs-hourly
├ ○ /blog/self-employment-tax-guide-2026
├ ○ /contact
├ ○ /privacy
├ ○ /resources
└ ○ /terms
○  (Static)  prerendered as static content
✅ Sitemap, robots.txt, and ads.txt generated
```

## Checklist

- [ ] Presets: flags, active ring, localStorage + URL sync, Reset link
- [ ] Lifestyle preview live
- [ ] Slider gradient fill + thumb 18px
- [ ] Clamps 51/40/0.5 + shake on 0 billable
- [ ] ResultCard: count-up, pills, bar %, delta, share, stacked bar, empty state
- [ ] Hero mesh + badges + CTAs
- [ ] Guides hover lift + category pills
- [ ] Timeline connector + dots
- [ ] Ads min-h wrappers + Sponsored labels
- [ ] Print stylesheet
- [ ] `npm run build` 18/18 + sitemap
