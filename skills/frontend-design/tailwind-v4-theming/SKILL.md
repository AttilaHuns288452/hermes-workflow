---
name: tailwind-v4-theming
description: Tailwind v4 tokens, animations, shadcn/ui polish.
---

# Tailwind v4 Theming & shadcn/ui Customization

Tailwind v4 is CSS-first: no `tailwind.config.js`; `@theme` in globals.css is the config. This skill covers making a shadcn/ui + Tailwind v4 app's core feel premium without adding dependencies or breaking existing classes.

## When to use
- Refining design tokens (globals.css `@theme` / `:root`) for a v4 app
- Customizing shadcn/ui components (Button/Card/Input/Dialog/Select…) for consistency
- "Dialog/select doesn't animate" — silent no-op, nothing broken
- Any polish pass on a v4 + shadcn codebase (additive changes only)

## Core: `@theme` tokens generate utilities
```css
@theme {
  --shadow-card: 0 1px 2px rgb(15 23 42 / 0.04), 0 1px 3px rgb(15 23 42 / 0.06);
  --shadow-card-hover: 0 6px 16px rgb(15 23 42 / 0.08), 0 2px 4px rgb(15 23 42 / 0.05);
  --shadow-popover: 0 12px 32px rgb(15 23 42 / 0.12), 0 4px 8px rgb(15 23 42 / 0.06);
}
```
→ `shadow-card`, `shadow-card-hover`, `shadow-popover` utilities. Same mechanism for `--color-*`, `--radius-*`, `--animate-*`.

## Animations: `--animate-*` + keyframes INSIDE `@theme`
```css
@theme {
  --animate-dialog-in: dialog-in 200ms cubic-bezier(0.16, 1, 0.3, 1);
  @keyframes dialog-in { from { opacity: 0; transform: translate(-50%, -48%) scale(0.96); } }
}
```
Keyframes inside `@theme` are emitted only when the matching utility is used.

## Pitfalls
- **Dead `data-[state=open]:animate-in` classes (shadcn + v4).** shadcn dialog/select templates ship `animate-in`/`fade-in-0`/`zoom-in-95` classes that need the `tw-animate-css` plugin. Missing plugin = silent no-op (no build error). Fix: install `tw-animate-css`, or define real `--animate-*` + keyframes in `@theme` and swap the class names — zero new deps.
- **Dialog keyframes must bake in centering.** DialogContent uses `translate-x/y-[-50%]` utilities; an animation whose keyframes only animate opacity/scale works, but any `transform` in keyframes must start at `translate(-50%, -48%)` (and implicitly end at the computed `translate(-50%, -50%)`) or the element jumps during the animation.
- **v4 emits only used utilities.** After adding tokens, confirm they compiled: `grep -l "shadow-card" $(find .next -name "*.css")`. If absent, the class isn't being used or the token name/namespace is wrong.
- **Global `:focus-visible` fallback must live in `@layer base`.** Unlayered CSS beats layered utilities, so a bare `:focus-visible { outline: … }` overrides components' `focus-visible:outline-none` and doubles up with their ring utilities. `@layer base` keeps it a fallback for elements with no explicit ring.
- **Adaptive light/dark without `dark:` variants:** `color-mix(in oklch, var(--fg) 16%, transparent)` for scrollbar thumbs, `::selection`, hover fills — derives from theme vars so both themes work from one rule. Wire native controls: `:root { color-scheme: light }` + `.dark { color-scheme: dark }`.
- **Windows CRLF files + the patch tool:** patch inserts LF lines into CRLF files → mixed endings → noisy git diff. Normalize after editing: `python -c "p='f';d=open(p,'rb').read();open(p,'wb').write(d.replace(b'\r\n',b'\n').replace(b'\n',b'\r\n'))"`.
- **`prefers-reduced-motion` kill-switch** (a11y): `*, ::before, ::after { animation-duration: 0.01ms !important; animation-iteration-count: 1 !important; transition-duration: 0.01ms !important; }` inside the media query.

## Workflow for a polish pass
1. Read the full globals.css + target components first; note which classes are actually used (`grep -rn "classname" src/`).
2. Additive/substitute only — every existing class name keeps working.
3. After edits: `npx tsc --noEmit`, then `npm run build`, then grep the built CSS for new utilities.
4. Check `git status` — confirm you didn't touch protected files; normalize line endings.

## References
- `references/worked-recipe.md` — full worked recipe from a real polish pass (shadow scale, dialog/select animations, scrollbar/selection, focus rings, verify commands).
