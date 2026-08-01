---
name: premium-html-delivery
description: User-specific HTML delivery preferences - premium dark glass aesthetic, animated SVG diagrams, category-colored grids, data accuracy on stats. Load alongside claude-design or web-design-engineer when building HTML for this user.
---

# Premium HTML Delivery

User's specific visual and quality preferences for HTML sites. Apply these defaults whenever building a polished HTML page for this user — they override generic anti-cliché rules in other design skills.

## Visual System

- **Dark base**: `#05080f` background, `#0c1428` surfaces (`--bg`, `--surface`)
- **Accent**: blue `#4a8cf4` primary, gold `#f0d060` for highlights
- **Glass-morphism**: frosted cards with `backdrop-filter: blur(8-24px)`, low-opacity fills, `rgba(255,255,255,.04)` edge borders
- **Ambient background**: floating blurred orbs with slow drift animation + fractal-noise overlay at ~2.5% opacity
- **Section headings**: a 40px gradient accent bar above every `h2` (`h2::before`)
- **Alternating sections**: every other section gets a full-viewport `100vw` pseudo-element with `rgba(74,140,244,.012)` tint
- **Copy buttons**: always visible (never `opacity:0` + `:hover` — mobile has no hover)

## Skill Grid Category Colors

Cards in grids get a 3px left-border + subtle gradient tint by category:

| Category | Border Color |
|---|---|
| Software Development / Dev | `#4a8cf4` blue |
| LLMQuant / Finance | `#f0d060` gold |
| Creative & Design | `#d088b8` pink |
| Workflow & Core | `#3ddc84` green |
| Productivity & Comms | `#6bc5e8` cyan |
| Media & Content | `#e4a847` orange |
| Research & MLOps | `#9b7cf7` purple |
| GitHub & DevOps | `#7c5cf5` violet |
| OpenCode Power Pack | `#4dc9b8` teal |
| More / Other | `#8895b8` gray |

## Animated SVG Diagrams

Replace static HTML card lists for pipelines, flowcharts, and decision trees with inline SVG:

- Use `<svg viewBox="0 0 W H">` with responsive `max-width`
- Gradient-filled `<rect>` nodes with rounded corners
- CSS `@keyframes fadeNode { to { opacity:1 } }` with staggered `animation-delay` (0.2–0.4s intervals)
- Dash-array `<path>` connectors at `stroke="#2a4070"`
- Small arrowhead `<polygon>` elements between nodes
- Text uses the Inter font family at 11px (label) and 8px (sublabel)

## Data Accuracy

Verify every stat against the live system before hardcoding:
- `hermes skills list | wc -l` for active skill count
- `find path -name "SKILL.md" | wc -l` for file-level count
- `hermes --version` for version strings
- Count actual agents/files instead of estimating from memory

## Polish Layer (vanilla JS, zero deps)

Apply these to any multi-section page once the base design is in place. All are CSS + vanilla JS — no libraries.

- **Scroll progress bar**: `#scroll-progress` fixed top, `height:2px`, `background:var(--grad)`, width updated via `requestAnimationFrame`-throttled scroll listener. Gives immediate spatial feedback on long pages.
- **Active nav indicator**: `IntersectionObserver` on section IDs (`threshold:.3, rootMargin:'-20% 0px -60% 0px'`) toggles `.active` on the matching nav link. Add `.nav-links a.active::after` gradient underline pseudo-element.
- **Card hover**: elevation only — `translateY(-3px)` + `box-shadow:0 12px 40px rgba(0,0,0,.15)`. Do NOT use glow effects (radial-gradient mouse tracking, `0 0 0 1px rgba(color,.1)`) as affordances — baseline-ui flags them. Do NOT add a `mousemove` listener for card glow — it's a performance cost for a cheap visual.
- **Animated stat counters**: `IntersectionObserver` (`threshold:.5`) triggers `requestAnimationFrame` count-up from 0 to target with cubic ease-out. Parse existing textContent for the number + suffix. Apply to `.hero-stat .num`, `.kg-stat .val`, `.ts-stat .val`.
- **Back-to-top button**: fixed bottom-right, glassmorphic, `opacity:0` → `.visible` after 400px scroll. Gradient hover.
- **Keyboard search**: `/` focuses the search input (preventDefault if not already in an input), `Esc` blurs. Show a subtle `<kbd>` hint in bottom-left that fades in mid-scroll.
- **SVG connector draw animation**: `.svg-diagram .conn { stroke-dasharray:200; stroke-dashoffset:200; animation:drawLine 1.2s ease-out forwards }` — makes pipeline/flowchart SVGs feel alive on load.

All of these are progressive enhancement — the page works without JS, they just add motion and feedback.

## Premium Audit (Existing Sites)

When auditing an EXISTING site for premium feel (not building new), run the 12-point checklist in `references/premium-audit-checklist.md`. It produces a concrete punch list grouped into Quick Wins → Structural → Polish tiers, with exact CSS fixes and verification grep commands.

## Skill Search Pattern

For any card-grid with >20 items, add a live search input above the category tabs:
- `oninput` filters the rendered array by name/description/category (case-insensitive `includes`)
- Update a count label (`"N skills"`) on every filter
- Category tab clicks pass the current search value through (don't reset search on tab change)
- Stagger card re-render with `setTimeout(() => el.style.opacity='1', i*15)` for a cascade effect

## Font Stack

```
--font: 'Geist', -apple-system, sans-serif;
--mono: 'JetBrains Mono', 'Fira Code', monospace;
```

Preconnect Google Fonts with link preloads for Geist and JetBrains Mono. Geist (Vercel's font) replaces Inter — Inter is banned by high-end-visual-design as a generic default. The swap is the single highest-impact premium upgrade.
