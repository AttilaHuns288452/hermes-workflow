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

## Pitfalls

- Sass `@for` loops fail in Tailwind v4 / LightningCSS. Write explicit nth-child rules.
- `color-mix()` is fine for modern browsers; provide a solid fallback if needed.
- One container-level `mousemove` listener is more efficient than one per card.
- Respect `prefers-reduced-motion` for reveal animations.
- CDN UMD bundle variable collision: `var X` from a UMD bundle and `let X` in your inline script → `SyntaxError: Identifier 'X' has already been declared`. See `references/cdn-umd-variable-collision.md`.
