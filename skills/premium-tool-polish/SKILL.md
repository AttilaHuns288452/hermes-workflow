---
name: premium-tool-polish
description: Use when polishing calculators to premium feel.
---

# Premium Tool Polish

Use when the task is `make it feel like a $10k premium product` for calculators, generators, and tool landing pages (Next.js + Tailwind, no heavy deps).

## When to Use

- Calculator / estimator / generator overhaul
- Landing that wraps an interactive tool (hero + calculator + guides + methodology + FAQ)
- Prompt contains keywords: premium, $10k, sticky results, lifestyle preview, mesh hero, CLS-safe ads

## Stack Constraints

- Tailwind only; no chart lib, no framer-motion unless already installed
- `lib/calculations.ts` (or equivalent math) is untouched — UI only
- Next.js `output: export` static build must stay green (18 pages in reference project)
- Verify with `npm run build` — must pass

## Calculator Layout

- Two-column desktop: `lg:grid [1.1fr_0.9fr]` (or `1.15fr 0.85fr`), right column `lg:sticky lg:top-[4.5rem]`
- Inputs grouped as elevated cards (icon + label + help tooltip + number input + inline preview + optional slider)
- Lifestyle preview sentence above presets, live: `Work {h}h/wk · {off} wks off → {billable} hrs/yr` (pulse dot)
- Inline previews under money fields: `$100K/yr · $46/hr → $370/day`, `$300/mo · $3,600/yr` — prevents user mental math
- Presets: flags/icons in label, active `ring-2 ring-[#c7d2fe]` + `bg-[#5e6ad2] text-white`, `border-[#a5b4fc]`/`bg-[#eef2ff]` on hover, persist preset key + full inputs to `localStorage` (`frc-preset` / `frc-inputs`), sync to URL via `replaceState`, add subtle `Reset to defaults` link

## Inputs & Validation

- Field meta pattern: `FieldMeta { key, label, suffix, step, min, max, isPercent, help, tip, group, slider, icon }`
- Slider gradient fill: inline `linear-gradient(to right, #5e6ad2 0%, #818cf8 {pct}%, #eef2ff {pct}%, #eef2ff 100%)` where `pct = (value-min)/(max-min)*100`; recompute on every `onChange` (was `#2563eb`/`#e5e7eb` before 2026-08 periwinkle pass)
- Custom thumb: `18-20px` + `border 3px white` + `box-shadow 0 2px 10px rgba(94,106,210,0.45)` + `scale(1.12)` on hover
- Clamps: `weeksWorked` 1–51 (max 51), `billableHours` 1–40, `annualTaxRate` 0–0.5; shake (`@keyframes shake` + `.animate-shake 0.35s`) on 0 billable hours then reset to 1; `aria-invalid` + `focus:ring-2`

## ResultCard

- Hero: `bg-gradient-to-br from-[#5e6ad2] via-[#4f46e5] to-[#3730a3]` + 3 periwinkle mesh blobs (`#5e6ad2/35`, `#818cf8/20`, `#4338ca/30` blur-90) + grain (SVG turbulence `0.04`) + grid `opacity-[0.06]` (`36px`), animated number `useCountUp` (simple `setInterval` eased 650ms, 12–30 steps, `1 - (1-p)^3`), 3 pill chips (`bg-white/15 backdrop-blur border-white/15`)
- Delta badge: `You need +{pct}% over salary` (`bg-white/15 border-white/20`)
- Billable bar: `h-3 bg-[#eef2ff] rounded-full` + gradient fill `from-[#5e6ad2] to-[#4338ca]` + `%` badge `bg-[#eef2ff] border-[#c7d2fe]`, legend pills for `h/yr`, `wks off`, `h/wk non-billable`
- Employee vs Freelancer: side-by-side `md:grid-cols-2`, right card `from-[#eef2ff] to-[#e0e7ff] border-[#c7d2fe]` with taxes/benefits/expenses list
- Proposal preview: copy + share (Web Share API → clipboard fallback with URL), `bg-gray-50 rounded-xl border`
- Cost breakdown: stacked flex bar (pure CSS, no chart lib) — segments `flex` with `width: value/total*100%`, legend with colored dots + `%`, open `details` by default
- Empty state for 0 income: `👋 Set your target income…`
- Print: `print:hidden` on blobs/grid, `print:bg-white print:text-gray-900 print:border`

## Page Layout

- Hero mesh: 2–3 `blur-[80-90px]` periwinkle blobs (`#5e6ad2/35`, `#818cf8/20`, `#4338ca/30`) + `linear-gradient` 32-36px grid at `opacity-[0.06]` + vignette + grain `0.04` mix-blend, proof badges (`10k+ freelancers`, `2026 tax tables`, `No signup`) as `bg-white/[0.08] backdrop-blur border-white/10` (dark) + periwinkle pill `bg-[#5e6ad2]` for `No signup • Free forever`, peek rate card desktop `rotate-[1.5deg]` (`hidden lg:block` 360px), CTA pair (`bg-white text-[#0f1229]` + `bg-white/10 border-white/15`), editorial headline `Design your ideal freelance / life — not just a rate.` with `from-[#a5b4fc] via-white to-[#c7d2fe]` clip
- Guides: `hover:-translate-y-1 hover:shadow-[0_12px_32px_rgba(15,18,41,0.08)] hover:border-[#c7d2fe]` + periwinkle wash `opacity-[0.05]` + category pill `bg-[#f8f9ff] border-[#eef2ff]`, icon `w-10 h-10 rounded-xl bg-[#f8f9ff] border-[#eef2ff]` → `#eef2ff` on hover, arrow `bg-[#0f1229]` ring on hover
- How It Works timeline: vertical stack mobile, `md:grid-cols-2` desktop with center `w-px bg-gradient-to-b from-[#c7d2fe] via-[#e0e7ff] to-amber-200` connector + dot `w-2.5 h-2.5 bg-white border-2 border-[#a5b4fc]` at `-28px`, alternate `md:mt-6` on odd, card `p-5 bg-[#f8f9ff] rounded-[20px] border-[#eef2ff] hover:bg-white hover:shadow-[0_8px_24px_rgba(15,18,41,0.06)]`, numbered `w-11 h-11` periwinkle badge (`#5e6ad2`), formula `bg-[#eef2ff] border-[#c7d2fe] rounded-[20px]` + mono `#4338ca`
- Why Undercharge: dark `from-[#0f1229] via-[#1a1d3d] to-[#0f1229] rounded-[28px] shadow-[0_20px_60px_rgba(15,18,41,0.25)] border-white/5` + `bg-white/[0.06] border-white/10 rounded-2xl backdrop-blur` ✕ rows + `bg-[#5e6ad2]/25 blur-3xl` glow
- FAQ: `details/summary` accordion `bg-white rounded-[20px] border-[#eef2ff] open:shadow-[0_8px_24px_rgba(15,18,41,0.06)] open:border-[#c7d2fe]` + chevron `w-8 h-8 bg-[#f8f9ff] border-[#eef2ff] group-open:bg-[#eef2ff] group-open:border-[#c7d2fe] group-open:rotate-180 text-[#5e6ad2]`
- Final CTA: `from-[#5e6ad2] via-[#4f46e5] to-[#3730a3] rounded-[28px] shadow-[#5e6ad2]/20 border-white/10` + dot grid `0.04` + `↑ Back to Calculator` `bg-white text-[#4338ca]` pill
- Nav: `glass-nav` (`rgba(255,255,255,0.78)` + `blur(16px) saturate(1.2)`) + `h-[60px] max-w-6xl`, `FC` `w-8 h-8 rounded-xl bg-[#5e6ad2] shadow-[#5e6ad2]/20`, links `rounded-full hover:bg-[#eef2ff] hover:text-[#5e6ad2]` + `Try it →` `bg-[#0f1229]` pill `hidden md:inline-flex`
- Ads (Adsterra): wrap every `AdBanner` in `min-h-[110-130px]` (`below-results` 110, `between-guides-and-faq` 130, banner 72) + `Sponsored` label + dashed placeholder `bg-gray-50 border-dashed`; scripts 1 & 2 stay `strategy="afterInteractive"` in `layout.tsx`
- Footer: affiliate disclosure + sponsored gradient pill `from-amber-500 to-orange-500 rounded-full shadow-md`, `max-w-6xl` + `tracking-[0.14em]` sponsored label

## Global Tokens (periwinkle system 2026-08 — `#2563eb` retired)

- Typography: Geist (`--font-geist-sans` / `--font-geist-mono`), antialiased, `::selection` periwinkle
- Palette: primary `#5e6ad2` (retired `#2563eb`), `#4f46e5` / `#4338ca` / `#3730a3`, soft `#eef2ff` / `#e0e7ff` / `#c7d2fe` / `#a5b4fc`, dark `#0f1229` / `#1a1d3d` vignette, bg `#f8f9ff` (not `gray-50`), grain `0.035` SVG turbulence, `glass-nav` (`rgba(255,255,255,0.78)` + `blur(16px) saturate(1.2)` + `border rgba(15,18,41,0.06)`)
- Card: `bg-white border border-[rgba(15,18,41,0.06)] rounded-[20px] shadow-[0_1px_2px_rgba(15,18,41,0.04),0_8px_24px_rgba(15,18,41,0.06)]`, hover `shadow-[0_8px_28px_rgba(15,18,41,0.10)]` + `translateY(-2px)` (was `border-gray-200 rounded-2xl`)
- Print stylesheet: `@media print { header, footer, .no-print { display:none } body { background:white } .card { box-shadow:none } }`
- Focus: `*:focus-visible { outline 2px solid #5e6ad2; outline-offset 2px }` + `.premium-input:focus` ring `#5e6ad2/14` (`bg-white`)

## Pitfalls

- Next.js `output: export` prerender fails if a Server Component passes `onSubmit`/`onClick` to a Client Component — extract the interactive form to its own `"use client"` file (e.g., `components/EmailCapture.tsx`) and import it into `app/page.tsx`
- Tailwind v4 uses `@import "tailwindcss"` + `@theme { --color-* }` — there is no `tailwind.config.ts`; editing it does nothing
- Do not break `metadataBase`, `openGraph`, `GA/AdSense/Adsterra` scripts, or `scripts/generate-sitemap.js` (still runs post-build for `sitemap.xml`/`robots.txt`/`ads.txt`)
- Static-export SEO: `robots.txt` must not contain `Crawl-delay` (throttles crawlers); canonicals must match sitemap *exactly* (trailing slash iff `next.config.trailingSlash: true` — freelance `true` → `/.../` canonicals, anime-waifu `false` → no slash); `title` should be `{ default, template: "%s | ..."}`, `robots` object with `googleBot` — not strings. See `references/nextjs-static-seo-hygiene-2026-08.md` (b7e3fba/6611b55)
- Default `app/favicon.ico` is the Vercel triangle (26K) — survives any redesign. Replace with *fitting* brand mark via `app/icon.svg` (32px) + `app/apple-icon.svg` (180px) + `app/favicon.ico`/`public/favicon.ico` (PNG-ICO via `sharp`); Next.js auto-discovers `app/icon.*` so no `metadata.icons` needed. Bare initials (`FC`) are boring at 16px — use a thematic silhouette: freelance = periwinkle gradient calculator (`#5e6ad2→#312e81` + white `$` screen + 9-dot grid, 1510B ICO), anime-waifu = dark `#0f0f1a` heart with purple→pink→blue gradient (`#7c3aed/#ec4899/#3b82f6`) + sparkle (904B ICO). Remove legacy manual `<link rel="icon" href="/logo.png">` (anime had it) so auto-discovery wins. Browsers cache hard — verify live `curl /icon.svg` + `curl -I /favicon.ico`, tell user `Ctrl+Shift+R`. See `references/favicon-brand-fix-2026-08.md` + `references/favicon-fitting-pass-2026-08.md`

## Verification

- `npm run build` → `✓ Compiled` + `Generating static pages (18/18)` + `Sitemap, robots.txt, and ads.txt generated`
- Refresh with `?income=100000&hrs=25&wks=46…` keeps values (URL round-trip)
- `localStorage` round-trip: reload without query restores last preset/inputs

## References

- `references/premium-calculator-overhaul.md` — session transcript, field meta, build output (18 pages), and checklist
- `references/periwinkle-pass-2026-08.md` — periwinkle system (`#5e6ad2` over `#2563eb`), windows node-replace trick, 0a7f31b diff
- `references/favicon-brand-fix-2026-08.md` — Vercel triangle → periwinkle FC favicon (app/icon.svg + apple-icon.svg + sharp PNG-ICO), 0b24f17
- `references/favicon-fitting-pass-2026-08.md` — boring FC → fitting silhouettes (calculator vs gradient heart + sparkle), both sites 3140ec3/e77c6f5
- `references/nextjs-static-seo-hygiene-2026-08.md` — crawl-delay yank, trailingSlash ↔ canonical alignment, title template + googleBot, dual static-export checklist (b7e3fba/6611b55)
