---
name: frontend-patterns
description: Reusable frontend implementation patterns for production React/Tailwind apps. Use for card grids, hover effects, animations, icon systems, and other UI patterns that come up repeatedly across projects.
---

# Frontend Patterns

## When to use

- Redesigning card grids, catalogs, rosters, or dashboards.
- Adding premium hover/interaction effects without new dependencies.
- Replacing Framer Motion with CSS-only animations.
- Building a lightweight inline SVG icon system.
- Adding a draggable floating button / chat widget FAB (pointer events, position persistence).

## 21st-Inspired Premium Cards (No Framer Motion)

### Spotlight hover effect

Track mouse position relative to each card via a container listener and expose CSS custom properties.

```jsx
function SpotlightGrid({ children, className = '' }) {
  const containerRef = useRef(null)
  useEffect(() => {
    const container = containerRef.current
    if (!container) return
    const onMouseMove = (e) => {
      container.querySelectorAll('.spotlight-card').forEach(card => {
        const rect = card.getBoundingClientRect()
        card.style.setProperty('--mouse-x', `${e.clientX - rect.left}px`)
        card.style.setProperty('--mouse-y', `${e.clientY - rect.top}px`)
      })
    }
    container.addEventListener('mousemove', onMouseMove)
    return () => container.removeEventListener('mousemove', onMouseMove)
  }, [])
  return <div ref={containerRef} className={className}>{children}</div>
}
```

```css
.spotlight-card {
  position: relative;
  overflow: hidden;
  border-radius: 1rem;
  background: rgba(12, 20, 40, 0.55);
  border: 1px solid rgba(255, 255, 255, 0.05);
  transition: all 0.35s cubic-bezier(0.22, 1, 0.36, 1);
}
.spotlight-card::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  padding: 1px;
  background: radial-gradient(
    600px circle at var(--mouse-x, 50%) var(--mouse-y, 50%),
    rgba(74, 140, 244, 0.35),
    transparent 40%
  );
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  opacity: 0;
  transition: opacity 0.3s;
  pointer-events: none;
}
.spotlight-card:hover::before { opacity: 1; }
```

### Category color + icon

Pass category-specific color as a CSS variable. Use inline SVG for icons instead of adding an icon library.

```jsx
<div className="spotlight-card premium-card p-4" style={{ '--cat-color': color }}>
  <span className="category-icon-bg"><InlineIcon name={icon} /></span>
  <span className="category-label">{category}</span>
</div>
```

```css
.premium-card {
  background:
    radial-gradient(400px circle at var(--mouse-x, 50%) var(--mouse-y, 50%),
      rgba(74, 140, 244, 0.06), transparent 40%),
    rgba(12, 20, 40, 0.55);
}
.premium-card:hover {
  transform: translateY(-4px);
  border-color: rgba(255, 255, 255, 0.12);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.25), 0 0 0 1px rgba(74, 140, 244, 0.1);
}
.premium-card .category-icon-bg { color: var(--cat-color, #7aa9f7); }
.premium-card .category-label { color: var(--cat-color, #7aa9f7); }
```

### Category Bento Grid (click-to-filter)\n\nA grid of color-coded category cards with icon, skill count, and click-to-filter coupling with the main grid below. Each card sets `--cat-color` and drives a parent filter state.\n\n```jsx\n// Category overview grid — drives filter state in parent\nfunction CategoryBentoGrid({ cats, activeCat, onSelect, icons, colors, counts }) {\n  const ref = useSpotlight()  // reuse spotlight hover\n  return (\n    <div ref={ref} className=\"grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3 mb-8\">\n      {cats.map(c => {\n        const color = colors[c] || '#7aa9f7'\n        return (\n          <div\n            key={c}\n            className={`category-bento p-4 ${activeCat === c ? 'active' : ''}`}\n            style={{ '--cat-color': color }}\n            onClick={() => onSelect(c)}\n            role=\"button\"\n            tabIndex={0}\n          >\n            <div className=\"flex items-center gap-3 mb-3\">\n              <div className=\"category-icon-bg\" style={{ color }}>\n                <CategoryIcon name={icons[c]} />\n              </div>\n              <span className=\"text-[9px] font-semibold uppercase tracking-[0.12em]\" style={{ color }}>{c}</span>\n            </div>\n            <div className=\"text-xl font-extrabold text-[#e4eaf5] mb-0.5\">{counts[c]}</div>\n            <div className=\"text-[10px] text-[#5a6a90]\">skills</div>\n          </div>\n        )\n      })}\n    </div>\n  )\n}\n```\n\n```css\n.category-bento {\n  position: relative;\n  border-radius: 1rem;\n  overflow: hidden;\n  cursor: pointer;\n  transition: all 0.35s cubic-bezier(0.22, 1, 0.36, 1);\n  border: 1px solid rgba(255,255,255,0.05);\n  background: rgba(12,20,40,0.55);\n}\n.category-bento:hover {\n  transform: translateY(-3px);\n  border-color: var(--cat-color, #7aa9f7);\n  box-shadow: 0 8px 30px rgba(0,0,0,0.25), 0 0 0 1px color-mix(in srgb, var(--cat-color, #7aa9f7) 20%, transparent);\n}\n.category-bento.active {\n  border-color: var(--cat-color, #7aa9f7);\n  background: color-mix(in srgb, var(--cat-color, #7aa9f7) 6%, rgba(12,20,40,0.55));\n}\n.category-bento .category-icon-bg {\n  width: 2.25rem;\n  height: 2.25rem;\n  border-radius: 0.625rem;\n  display: flex;\n  align-items: center;\n  justify-content: center;\n  background: radial-gradient(circle at 30% 25%,\n    color-mix(in srgb, var(--cat-color, #7aa9f7) 20%, transparent),\n    transparent 60%);\n  border: 1px solid color-mix(in srgb, var(--cat-color, #7aa9f7) 10%, transparent);\n}\n```\n\n**Parent component coupling pattern:**\n```jsx\nfunction CatalogSection({ items, categories, categoryIcons, categoryColors }) {\n  const [activeCat, setActiveCat] = useState('all')\n\n  const filtered = activeCat === 'all'\n    ? items\n    : items.filter(i => i.category === activeCat)\n\n  return (\n    <>\n      <CategoryBentoGrid\n        cats={categories}\n        activeCat={activeCat}\n        onSelect={setActiveCat}\n        icons={categoryIcons}\n        colors={categoryColors}\n        counts={Object.fromEntries(categories.map(c => [c, items.filter(i => i.category === c).length]))}\n      />\n      <SpotlightGrid className=\"grid grid-cols-3 gap-5\">\n        {filtered.map(item => <SpotlightCard key={item.id}>{/* card content */}</SpotlightCard>)}\n      </SpotlightGrid>\n    </>\n  )\n}\n```

Use explicit CSS `nth-child` animation delays. **Do not use Sass `@for`** — Tailwind v4 / LightningCSS does not support it.

```css
.stagger-reveal > * {
  opacity: 0;
  transform: translateY(16px);
  animation: fadeUp 0.5s cubic-bezier(0.22, 1, 0.36, 1) forwards;
}
.stagger-reveal > *:nth-child(1) { animation-delay: calc(var(--stagger-delay, 40ms) * 1); }
/* repeat through required count */

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}
```

## Hand-rolled toast system (no deps)

When the constraint is "no new dependencies" (no sonner/react-hot-toast): module-level
store + `useSyncExternalStore`, no context. Provider is only a renderer; `useToast()`
returns the module `toast()` fn. Two non-obvious rules:

- **Immutable array replacement is the snapshot contract** — `useSyncExternalStore`
  re-renders only on a new reference, so always `toasts = [...toasts, item]`, never mutate.
- **Never nest two providers of the same store** — each renders its own stack → duplicate
  toasts. Wire providers into mutually exclusive layout branches (bare auth branch vs
  app shell), never both around the same subtree.
- Keyframes go in an in-component `<style>` tag when shared CSS (globals.css) is outside
  your file ownership; offset the stack above fixed FABs (`bottom-24 md:bottom-4`).

Full implementation + pitfalls: `references/toast-provider-no-deps.md`.

## Zero-dependency dark SaaS landing page (Next.js + Tailwind v4)

When the brief is a premium dark landing (Stripe/Linear/Vercel caliber) with NO new npm deps and a frozen `globals.css`:

- Architecture: server-component page shell + `'use client'` islands only (Reveal, tabs, accordion); all keyframes/helper classes in one scoped `<style>` tag in the page shell.
- CSS-only motion recipes: IntersectionObserver Reveal with `transitionDelay` stagger, tab crossfade via keyed re-mount + fadeUp, accordion via `grid-rows-[0fr]→[1fr]` + `min-h-0 overflow-hidden`, animated AI orb (conic-gradient ring + SVG face + box-shadow/float/blink keyframes).
- Frozen-globals traps: override global `h1,h2,h3 { font-family: serif }` with a scoped `.root h1 { font-family: var(--font-sans) }` rule (class-scoped beats element selector); always pass explicit border-color classes past a global `* { @apply border-border }`.
- Full verified playbook (tokens, Tailwind v4 arbitrary syntax, no-build verification via `tsc --noEmit` + dev-server curl|grep smoke test): `references/zero-dep-dark-saas-implementation.md`.

## Draggable floating button (chat FAB, pointer events)

Drag-anywhere FAB with click-to-toggle, no deps. The subtle parts are click-vs-drag disambiguation and pointer capture:

- `onPointerDown`: `e.currentTarget.setPointerCapture(e.pointerId)` (move/up keep firing off-element), record start `{ px, py, ox: rect.left, oy: rect.top, moved: false }` in a ref.
- `onPointerMove`: mark `moved` only after ~4px total travel (threshold), then `setPos(clamp(ox + dx, 16, vw - size - 16))`.
- `onPointerUp`: if `moved` → persist to localStorage; **set a `suppressClick` ref — `onClick` fires AFTER `pointerup`, so an unguarded click handler toggles the panel after every drag**. onClick consumes+resets the flag. Keep `onClick` for keyboard (Enter/Space) activation.
- `style={{ touchAction: 'none' }}` or touch drags scroll the page instead of moving the FAB.
- Default position via classes (`bottom-6 right-6`) when no saved pos; inline `left/top` only when saved — avoids SSR/hydration mismatch from reading `window` in a state initializer.
- Anchor a popover/dialog to the FAB by measuring `ref.getBoundingClientRect()` in an effect on `[open, pos]` (+ window resize listener), side-align to whichever viewport half the FAB is in, clamp to viewport, and render the dialog only once its position is computed (avoids a 0,0 flash frame). Recomputing on `pos` makes the dialog follow live while the FAB is dragged.

## Async data-fetch hardening (client components)

When a component fetches on mount/filter-change AND refreshes after mutations (add/edit/delete), use one shared fetch fn with all three guards — a per-call-site guard leaves sibling callers racy:

```tsx
const fetchData = async () => {
  setLoading(true);
  const f = filters;                       // snapshot BEFORE await
  try {
    const page = await getData(f);
    if (filtersRef.current !== f) return;  // stale-response guard: drop out-of-order responses
    setItems(page.items);
  } catch {
    setErr("Failed to load");              // never leave an unhandled rejection
  } finally {
    setLoading(false);                     // ALWAYS reset loading in finally
  }
};
```

- Keep `filtersRef` in sync inside the effect that triggers the fetch — NEVER `ref.current = x` in the render body (unsafe with concurrent rendering).
- Memoize derived data (Maps, Sets, filter+reduce stats) with useMemo — building them inline re-runs on every keystroke-driven render. Format per-row derived strings (e.g. dates) once into a Map keyed by row id instead of 3× per row per render.
- Parse date-only strings (`YYYY-MM-DD`) with `parseISO` (date-fns) — `new Date(str)` parses as UTC midnight and shifts a day in negative-offset timezones.

## Pitfalls

- Sass `@for` loops fail in Tailwind v4 / LightningCSS. Write explicit nth-child rules.
- `color-mix()` is fine for modern browsers; provide a solid fallback if needed.
- One container-level `mousemove` listener is more efficient than one per card.
- Respect `prefers-reduced-motion` for reveal animations.
- CDN UMD bundle variable collision: `var X` from a UMD bundle and `let X` in your inline script → `SyntaxError: Identifier 'X' has already been declared`. See `references/cdn-umd-variable-collision.md`.
- **Mount-only URL-param effects die on same-route soft nav (Next App Router).** `useEffect(..., [])` reading `window.location.search` fires once; a Next `<Link>` navigating to `?add=1` on the SAME route does NOT remount → the feature silently never triggers from in-app taps (only cold loads). Fix: `const sp = useSearchParams()` + `useEffect(..., [sp])` reading `sp.get(...)`, and wrap the component in `<Suspense>` at the page level (Next requires it for `useSearchParams`). Keep `history.replaceState` cleanup — it doesn't re-trigger the hook (router state, not history API), so no loop. Verified 2026-08-11 (QuickFAB "Add Income" dead when already on /transactions).
- **Responsive side-switch over-constraint (Tailwind).** `bottom-6 left-6 md:right-6` leaves BOTH `left` and `right` applied at md+ → CSS keeps `left` in LTR and the element parks on the WRONG side (fixed-width elements only). When switching sides at a breakpoint, always null the base side: `bottom-6 left-6 md:left-auto md:right-6`. Same class of bug for `top`/`bottom` switches.
- **Fixed-height containers inside padded wrappers render shorter than declared.** shadcn `CardContent` is `p-6 pt-0` → 24px bottom padding eats into a child's `h-[280px]`: the chart/`ResponsiveContainer height="100%"` gets 256px. To preserve a previous pixel size when moving a fixed-height child into a padded parent, add the padding to the declared height (`md:h-[304px]`), or move the height onto an inner un-padded wrapper.
- **Focus-stealing effects:** a `useEffect(..., [pathname])` that focuses main content fires on MOUNT, dumping keyboard/SR users past the skip link and nav (unreachable via forward Tab). Guard with a first-run ref: `if (!mounted.current) { mounted.current = true; return }`.
