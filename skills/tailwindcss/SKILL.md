---
name: tailwindcss
description: Use when designing/implementing UI with Tailwind CSS (layout, typography, responsive, theming, component patterns). Includes quick recipes and conventions for clean, consistent web design.
---

# Tailwind CSS — Utility-first Styling Skill

## When to use
- Rapid UI building with consistent spacing/typography scales
- Design systems where composition beats bespoke CSS
- Component-driven apps (React/Vue/Svelte), marketing pages, prototypes → production

## Key concepts & patterns
- Utilities compose in HTML/JSX: `class="flex gap-4 p-6 bg-zinc-950 text-white"`
- Responsive variants: `sm: md: lg: xl:` etc.
- State variants: `hover:`, `focus:`, `active:`, `disabled:`, `group-hover:`, `peer-checked:`
- Arbitrary values (use sparingly): `w-[42rem]`, `bg-[#0b1220]`, `translate-y-[3px]`
- Dark mode patterns: `dark:` with class-based strategy
- Extracting repeated patterns:
  - Prefer components (JSX/Vue components) first
  - Then `@apply` for small reusable patterns (avoid overuse)
- Build pipeline:
  - Tailwind scans “content” files for class names and generates CSS (zero-runtime)

## Common pitfalls
- **`max-w-*` without `mx-auto` in flex layouts** — A `max-w-5xl` (or any `max-w-*`) container inside a flex parent will hug the left edge, leaving uneven margins. Always pair `max-w-*` with `mx-auto` to center: `class="max-w-5xl mx-auto"`. This is the #1 layout "why is my content not centered?" bug.
- **Sticky/fixed sidebar + margin on main = double offset** — If a sidebar is `sticky` (takes normal-flow space) AND `<main>` has `ml-*` matching the sidebar width, the content gets pushed double the sidebar width from the left. The sticky sidebar already occupies space in the flow; the margin adds a second offset on top. Fix: remove `ml-*` from main (let sticky handle it), add `pl-*` to the content area for spacing from the sidebar border. Symptom: "left margin too big, right margin too small" even with `mx-auto`.
- Classes not generated in production
  - Ensure content paths include all templates/components.
  - Avoid building class names dynamically (e.g. `"text-" + color`) unless safelisted.
- Overusing `@apply` and losing the utility-first benefits
- Conflicting styles due to class order assumptions
- Huge HTML class lists with no structure
  - Use component composition; break into subcomponents; use `clsx/cva` when needed.

## Dark mode patterns

### Strategy: `darkMode: 'class'` (recommended)
Gives users manual control rather than relying on OS `prefers-color-scheme`.

**Config:**
```js
// tailwind.config.js
module.exports = {
  darkMode: 'class',
  // ...
}
```

**Toggle implementation:**
```html
<script>
  const theme = localStorage.getItem('theme') || 'dark';
  document.documentElement.classList.toggle('dark', theme === 'dark');

  function toggleTheme() {
    const next = document.documentElement.classList.contains('dark') ? 'light' : 'dark';
    document.documentElement.classList.toggle('dark', next === 'dark');
    localStorage.setItem('theme', next);
  }
</script>
```

**Usage in HTML:**
```html
<div class="bg-white dark:bg-slate-800 text-black dark:text-white">
  Adapts to theme
</div>
```

**Light-mode overrides** (for complex apps):
```css
/* In global CSS / style tag */
html:not(.dark) .light-mode-only { display: block; }
html.dark .dark-mode-only { display: block; }
```

## Tailwind built-in animation classes

| Class | CSS equivalent | Use case |
|-------|---------------|----------|
| `animate-spin` | `animation: spin 1s linear infinite` | Loading spinners |
| `animate-ping` | `animation: ping 1s cubic-bezier(0,0,0.2,1) infinite` | Notification badges, "live" indicators |
| `animate-pulse` | `animation: pulse 2s cubic-bezier(0.4,0,0.6,1) infinite` | Skeleton placeholders, loading cards |
| `animate-bounce` | `animation: bounce 1s infinite` | Scroll-down hints, playful CTAs |

**Speed control**: override `animation-duration` inline or via CSS.
```html
<div class="animate-spin" style="animation-duration: 500ms">Fast spinner</div>
```

**Custom keyframes** (in `tailwind.config.js`):
```js
module.exports = {
  theme: {
    extend: {
      keyframes: {
        shake: {
          '0%, 100%': { transform: 'translateX(0)' },
          '25%': { transform: 'translateX(-5px)' },
          '75%': { transform: 'translateX(5px)' },
        },
      },
      animation: {
        shake: 'shake 0.5s ease-in-out',
      },
    },
  },
}
```
Then use: `<button class="animate-shake">Shake me</button>`

### Tailwind v4 setup (Vite + React)

Tailwind v4 uses CSS-based config instead of `tailwind.config.js`:
```bash
npm install tailwindcss @tailwindcss/vite
```
**vite.config.js:** `plugins: [react(), tailwindcss()]`
**src/index.css:** `@import "tailwindcss";`
**Custom theme:** `@theme { --color-primary: var(--primary); }` in CSS.
**Dark mode:** `@custom-variant dark (&:where(.dark, .dark *));` in CSS.
Toggle: `document.documentElement.classList.toggle('dark')`.

Tailwind v4 vs v3: v3 uses JS config + PostCSS, v4 uses CSS `@theme` + Vite plugin.

## Quick recipes

### 1) A clean CTA button
```html
<button class="inline-flex items-center justify-center rounded-xl px-5 py-3
               bg-indigo-600 text-white font-medium
               hover:bg-indigo-500 active:bg-indigo-700
               focus:outline-none focus:ring-2 focus:ring-indigo-400/60">
  Get started
</button>
```

### 2) Responsive hero layout
```html
<section class="mx-auto max-w-6xl px-6 py-16">
  <div class="grid gap-10 lg:grid-cols-2 lg:items-center">
    <div>
      <h1 class="text-4xl font-semibold tracking-tight sm:text-5xl">
        Ship a beautiful site fast.
      </h1>
      <p class="mt-4 text-zinc-600">
        Tailwind helps you move quickly without fighting CSS.
      </p>
    </div>
    <div class="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
      <!-- media -->
    </div>
  </div>
</section>
```

### 3) Handling dynamic classnames safely
Prefer mapping:
```js
const toneClass = {
  success: "bg-emerald-600",
  danger: "bg-rose-600",
  info: "bg-sky-600",
}[tone];
```

## User preferences (this user)
- Default framework: **React + Tailwind (Vite + Tailwind v4)**. Start here unless asked otherwise.
- Professional/minimal aesthetic. Prefers blue-toned schemes. Use CSS-only improvements, no new components for polish.
- Lean toward fewer, higher-contrast blues (blue-950/blue-600) rather than stacking multiple blue shades.

### Polish reference
For detailed refinement methodology (spacing, shadows, typography, button/avatar/card polish without adding content), see `references/polish-playbook.md`.

## What to ask the user
- Framework/build tool? (Default: React + Tailwind v4 via Vite)
- Do we need a design system (tokens, component library) or a one-off page?
- Dark mode? RTL? accessibility constraints?
