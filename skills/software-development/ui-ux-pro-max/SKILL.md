---
name: ui-ux-pro-max
description: "UI/UX design intelligence for web and mobile. Searchable local database with 84 styles, 192 color palettes, 74 font pairings, 192 product types, 98 UX guidelines, 104 icon entries, 16 GSAP motion presets, 25 chart types, 22 stacks. Use when designing, building, or reviewing UI."
---

# UI/UX Pro Max - Design Intelligence

Searchable database of UI/UX design rules with priority-based recommendations.

## When to Apply

Use this Skill when the task involves **UI structure, visual design decisions, interaction patterns, or user experience quality control**.

## Rule Categories by Priority

| Priority | Category | Impact | Domain | Key Checks |
|----------|----------|--------|--------|------------|
| 1 | Accessibility | CRITICAL | `ux` | Contrast 4.5:1, Alt text, Keyboard nav, Aria-labels |
| 2 | Touch & Interaction | CRITICAL | `ux` | Min size 44×44px, 8px+ spacing, Loading feedback |
| 3 | Performance | HIGH | `ux` | WebP/AVIF, Lazy loading, CLS < 0.1 |
| 4 | Style Selection | HIGH | `style`, `product` | Match product type, SVG icons (no emoji) |
| 5 | Layout & Responsive | HIGH | `ux` | Mobile-first breakpoints, No horizontal scroll |
| 6 | Typography & Color | MEDIUM | `typography`, `color` | Base 16px, Line-height 1.5, Semantic color tokens |
| 7 | Animation | MEDIUM | `ux`, `gsap` | Duration 150–300ms, reduced-motion support |
| 8 | Forms & Feedback | MEDIUM | `ux` | Visible labels, Error near field, Progressive disclosure |
| 9 | Navigation | HIGH | `ux` | Predictable back, Bottom nav ≤5, Deep linking |
| 10 | Charts & Data | LOW | `chart` | Legends, Tooltips, Accessible colors |

## Search

```bash
python "$SKILL_DIR/scripts/search.py" "<query>" --domain <domain>
python "$SKILL_DIR/scripts/search.py" "<query>" --design-system -p "Project Name"
python "$SKILL_DIR/scripts/search.py" "<query>" --stack <stack>
```

**Domains:** `product`, `style`, `typography`, `color`, `landing`, `chart`, `ux`, `icons`, `react`, `web`, `google-fonts`, `gsap`

**Stacks:** `react`, `nextjs`, `vue`, `svelte`, `astro`, `nuxtjs`, `angular`, `swiftui`, `react-native`, `flutter`, `html-tailwind`, `shadcn`, and 11 more.

**Design dials (with `--design-system`):** `--variance <1-10>`, `--motion <1-10>`, `--density <1-10>`

For full rule details: read `references/quick-reference.md` on demand.
For pre-delivery checklist: read `references/pro-rules.md`.
