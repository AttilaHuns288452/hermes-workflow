# Premium dark SaaS landing recipe (Stripe/Linear/Vercel caliber)

Proven on the CashFlow OS landing rebuild (12 sections, ~2.5k lines, one
subagent + visual verification). User's exact direction: "comparable to
Stripe, Linear, Vercel, Arc, Notion, Apple, Raycast"; no generic SaaS page.

## Copy (the user's own mandate)

- **Open with a transformation, not a feature list.** "One dashboard. Every
  financial decision." — value first, then what it does. The user stated this
  explicitly: sell why someone should care.
- No "revolutionary / game-changing / next-generation" buzzwords.
- **Honesty over hype**: don't claim unshipped features ("BYOK is on the
  way" + what works today instead of "bring your own key"); placeholder
  testimonials get a code comment flag (swap before launch); social-proof
  numbers stay plausible.
- Testimonial pipeline: public `/feedback` page → `feedback` table with
  insert-only RLS (public INSERT, no public SELECT; owner reads rows in SQL
  Editor, flips `approved`). No admin UI pre-launch.

## Design system (pinned, from od-linear-app)

- bg `#08090a` (marketing black), panels `#0f1011`, elevated `#191a1b`
- text: `#f7f8f8` primary, `#d0d6e0` secondary, `#8a8f98` muted, `#62666d`
  faint — BUT `#62666d` on `#08090a` is ~3.4:1 and FAILS WCAG AA for small
  text; use `#8a8f98` (~6.2:1) for eyebrows/meta. Never pure white body.
- accent indigo `#5e6ad2` (CTA bg) / `#7170ff` (links) / `#828fff` (hover) —
  CTAs and interactive only, never decorative. Success green `#27a644`.
- borders: translucent white `rgba(255,255,255,0.05–0.08)`, never solid dark
- cards: bg `rgba(255,255,255,0.02–0.04)`, radius 8px cards / 12px panels /
  6px buttons; elevation = luminance stepping, NOT shadows
- type: system sans, display weight 500–590 (no 700), NEGATIVE letter-spacing
  at display sizes (-1.5px @72px scale), mono uppercase eyebrows 11px
- ONE decorative flourish max: hero radial glow `rgba(94,106,210,0.12)` +
  faint 1px grid lines; no gradients elsewhere

## Motion (zero dependencies)

- `Reveal` client component: IntersectionObserver threshold 0.15 fires once →
  class swap → CSS `opacity 0→1 + translateY(16px)→0`, 600ms ease-out;
  stagger via `transitionDelay: i*60ms`
- Hero fade-up: CSS keyframes with `animation-delay` per element
- Tabs: keyed div + CSS fadeUp 300ms; FAQ: `grid-rows-[0fr→1fr]` trick
- Microinteractions: card hover border 0.08→0.14 + bg 0.02→0.04

## NO-JS / SSR safety (real bug found in review)

Content hidden at `opacity:0` until JS runs = invisible page for Firefox
no-JS users (`@media (scripting:none)` is Firefox-unsupported), failed
bundles, crawlers, and pre-hydration screenshots. Required:

```html
<noscript><style>.reveal{opacity:1;transform:none} .fade-up{animation:none!important}</style></noscript>
```

plus `@media (scripting:none)` and a `prefers-reduced-motion` kill switch.

## A11y gotchas that reviewers flagged

- closed FAQ answers need `aria-hidden={!open}` + `inert={!open}` (0fr rows
  stay in the a11y tree otherwise)
- tab switchers need `role=tablist/tab/tabpanel` + `aria-selected` +
  `aria-controls`; hamburger needs `aria-expanded` + `aria-controls`
- decorative SVGs (sparklines) get `aria-hidden="true"` (lucide icons
  already are)

## Section flow (the 12 that worked)

Hero (orb + CSS dashboard mock + speech bubble) → social proof stats →
Problem (4 pain cards) → Solution (vertical connected flow) → Features
(9 cards w/ tiny CSS previews) → Showcase (5 tabs, crossfade) → AI copilot +
BYOK strip → Business mode → comparison table → testimonials → FAQ →
final CTA ("Your finances deserve one home.").

## Visual verification

See `parallel-sprint-shipping` SKILL.md "Verifying animated pages" — reveals
make screenshots black unless you open → wait → scroll → capture.
