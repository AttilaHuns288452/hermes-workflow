# Tailwind CSS v4 Setup (Vite + React)

Quick reference for setting up Tailwind CSS v4 in a Vite/React project.

## Installation

```bash
npm create vite@latest my-app -- --template react
cd my-app
npm install tailwindcss @tailwindcss/vite
```

## Configuration

### `vite.config.js`

```js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
})
```

### `src/index.css`

```css
@import "tailwindcss";
```

That's it — no `tailwind.config.js`, no `postcss.config.js`, no `@tailwind` directives.

## Custom Theme (`@theme` directive)

Replace `tailwind.config.js` `theme.extend` with CSS:

```css
@import "tailwindcss";

@theme {
  --color-brand: oklch(55% 0.2 260);
  --color-brand-light: oklch(65% 0.2 260);
  --font-heading: "Inter", sans-serif;
  --spacing-page: 1.5rem;
}
```

## Key Differences from v3

| Concern | v3 | v4 |
|---|---|---|
| Config | `tailwind.config.js` (JS/ESM) | `@theme` in CSS (no JS config) |
| Build integration | PostCSS plugin (`postcss.config.js`) | Vite plugin (`@tailwindcss/vite`) |
| CSS entrypoint | `@tailwind base; @tailwind components; @tailwind utilities;` | `@import "tailwindcss"` |
| Custom values | `theme.extend.colors.brand: '...'` in JS config | `--color-brand: ...` in `@theme` |
| Dark mode | `darkMode: 'class'` in config | `@variant dark (&:where(.dark, .dark *))` |
| Arbitrary values | `bg-[#123]` syntax | Same, but `@theme` custom properties preferred |
| Rounding | Tailwind defaults (twice the config size) | Smaller defaults, more deterministic |
| Layers | `base`, `components`, `utilities` explicit | Auto-managed, `@layer` for custom |

## Migration from v3

1. Remove `tailwind.config.js`
2. Remove `postcss.config.js` (and its `tailwindcss` + `autoprefixer` deps from package.json)
3. Replace `@tailwind base/components/utilities` with `@import "tailwindcss"`
4. Move `theme.extend` values into `@theme` in CSS
5. Move `plugins` to CSS `@plugin` directive
6. Update `vite.config.js` to use `@tailwindcss/vite` plugin
7. Run `npm uninstall tailwindcss postcss autoprefixer && npm install tailwindcss @tailwindcss/vite`
8. Run `npx @tailwindcss/upgrade` for automatic migration (optional)

## Windows Notes

- Paths in `skills.paths` for OpenCode use forward slashes even on Windows
- `npm install` may be flagged as long-running by Hermes tool guard — use `background=true` with `notify_on_complete=true`
- Vite dev server outputs may be buffered silently (MSYS/Cygwin quirk) — verify with `curl http://localhost:5173` instead of checking process logs

## Verification

```bash
npm run build
# Expect: ✓ built in <time>ms, no errors

# Or dev server:
npm run dev
curl http://localhost:5173 | head -5
# Expect: DOCTYPE html with React root div
```
