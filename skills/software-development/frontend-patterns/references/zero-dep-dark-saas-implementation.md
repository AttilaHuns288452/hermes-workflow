# Zero-dependency dark SaaS landing — Next.js + Tailwind v4 implementation playbook

Verified end-to-end on CashFlow OS (Next 16 App Router, Tailwind v4, `npx tsc --noEmit` clean, dev-server 200). Use when a brief demands Stripe/Linear/Vercel-caliber dark landing with **no new npm deps** (no framer-motion, no radix accordion).

## Architecture split (server shell + client islands)

- `page.tsx` = server component: metadata, composes sections, renders ONE scoped `<style>` block with all keyframes/helper classes. Do not touch `globals.css` (often frozen) — a `<style>` tag in the page shell is the escape hatch.
- `'use client'` ONLY for: `Reveal.tsx` (IntersectionObserver), tab switcher, FAQ accordion. Everything else stays a server component.

## Reveal-on-scroll (the one shared client util)

```tsx
'use client'
export function Reveal({ children, delay = 0, className = '' }) {
  const ref = useRef<HTMLDivElement>(null)
  const [inView, setInView] = useState(false)
  useEffect(() => {
    const el = ref.current
    if (!el) return
    const io = new IntersectionObserver(
      ([e]) => { if (e.isIntersecting) { setInView(true); io.disconnect() } },
      { threshold: 0.15 }
    )
    io.observe(el)
    return () => io.disconnect()
  }, [])
  return (
    <div ref={ref} className={`reveal ${inView ? 'is-in' : ''} ${className}`}
      style={{ transitionDelay: `${delay}ms` }}>
      {children}
    </div>
  )
}
```
CSS: `.reveal { opacity:0; transform:translateY(16px); transition:opacity .6s ease-out, transform .6s ease-out }` / `.reveal.is-in { opacity:1; transform:none }`. Stagger grids with `delay={i*60}` or `(i%3)*60` per row.

## Motion recipes (CSS only)

- **Hero load**: fade-up keyframe (`fade-up .7s cubic-bezier(.16,1,.3,1) both`) + inline `animationDelay` 80ms steps on eyebrow→headline→sub→CTAs→mock.
- **Tab crossfade**: `<div key={activeTab}>{views[activeTab]}</div>` — keyed re-mount retriggers a 300ms fadeUp animation. No transition lib needed.
- **Accordion**: parent `grid transition-[grid-template-rows,opacity] duration-300` + `grid-rows-[0fr]`/`grid-rows-[1fr]`, inner wrapper `min-h-0 overflow-hidden`. Chevron: `rotate-180` on open.
- **Animated AI orb**: 64px circle, `bg-[conic-gradient(from_180deg,#0a1128,#4158d0,#00d9ff,#0a1128)] p-[2px]` ring over a dark `#0a1128` face with an SVG face (glowing eyes/smile via `drop-shadow`). Animate with keyframes: box-shadow pulse (2.5s), gentle float translateY (6s), eye blink scaleY (4.5s). Speech bubble above with caret (rotated 2.5×2.5 div).
- **Always ship**: `@media (prefers-reduced-motion: reduce)` killing reveals/animations, and `@media (scripting: none)` forcing `.reveal` visible (SSR/SEO-safe).

## Frozen globals.css traps (app-repo class)

- `h1,h2,h3 { font-family: var(--font-display) }` (serif) globally → override per-page with a scoped rule: `.lp-root h1, .lp-root h2, .lp-root h3 { font-family: var(--font-sans) }` (class-scoped selector beats element selector regardless of source order).
- `* { @apply border-border }` sets border-color globally → always pass an explicit border-color class (`border-white/[0.06]`) or the app's light border leaks in.
- `body` bg is the app theme → page shell div must carry `min-h-screen bg-[#08090a]` to cover wrapper gradients (e.g. an AuthShell wrapper's light gradient).

## Dark premium token system (Linear-style, reuse as-is)

- Page `#08090a`; panels `#0f1011`; elevated `#191a1b`. Text `#f7f8f8` / `#d0d6e0` / `#8a8f98` / `#62666d` — never pure white body text.
- Accent `#5e6ad2` (CTA), `#7170ff` (links/icons), hover `#828fff`; success `#27a644`. SPARING — CTAs/interactive only.
- Borders `rgba(255,255,255,0.05–0.08)`, hover 0.14; card bg `rgba(255,255,255,0.02–0.04)`; radius 8px cards / 12px panels / 6px buttons. Elevation = luminance stepping, not shadows.
- Headlines: sans, weight 500 (never 700), negative tracking (`tracking-[-0.03em]` at 72px scale), clamp() responsive. Eyebrows: mono 11px uppercase `tracking-[0.18em]` muted.
- ONE decorative flourish max: radial glow `bg-[radial-gradient(ellipse_at_center,rgba(94,106,210,0.12),transparent_62%)] blur-2xl` + faint 1px grid via two linear-gradients (56px cells) masked with `[mask-image:radial-gradient(...)]`.
- Shared CSS classes in the scoped style block (`.lp-container`, `.lp-eyebrow`, `.lp-card`, `.lp-btn-primary/ghost`) beat repeating 8-class Tailwind strings on 20 cards.

## Tailwind v4 arbitrary-value syntax (verified)

- Opacity modifiers: `bg-white/[0.02]`, `border-white/[0.06]` (bracket form safest across v3/v4).
- Gradients: spaces → underscores: `bg-[radial-gradient(ellipse_at_center,rgba(94,106,210,0.12),transparent_62%)]`, `bg-[conic-gradient(from_180deg,#0a1128,#4158d0,#00d9ff,#0a1128)]`.
- `grid-rows-[0fr]` / `grid-rows-[1fr]`, `transition-[grid-template-rows,opacity]` all valid.
- Reuse the app's frozen radius tokens: `rounded-lg`=8px, `rounded-xl`=12px, `rounded-md`=6px when `--radius: 0.5rem`.

## Verification when `npm run build` is forbidden (concurrency rule)

1. `npx tsc --noEmit` → exit 0 (catches bad lucide icon names, unused imports, type errors).
2. Dev-server smoke test: `npm run dev` in background, curl `http://localhost:3000/`, assert HTTP 200 + grep for headline markers (`grep -oE "One dashboard[^<]*"`). Pipe curl straight into grep — on git-bash, `curl -o /tmp/x.html` followed by grep can silently miss the file; direct piping avoids it.
3. Note: `grep -c` on minified HTML counts LINES not matches — expect small numbers.
4. Commit locally, never push, unless told otherwise.
