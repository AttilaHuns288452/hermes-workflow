# UI Polish Playbook — React + Tailwind

Refine existing UI without adding sections, components, or content. Every change is a shade/shift/space tweak only.

## Principles

- **No additions.** No new sections, buttons, icons, images, animations, or layout changes.
- **No redesign.** Same structure, same elements. Make each element look 20–30% more polished using spacing, typography, shadows, borders, alignment.
- **8-point spacing.** Use `gap-2` `gap-4` `gap-5` `gap-6` `gap-8` consistently. Avoid arbitrary values.

## Navbar

- Height: `h-20` (80px) or `h-18` (72px)
- Horizontal padding: `px-10`
- Shadow: `shadow-sm` (subtle separation)
- Link spacing: `gap-8` with `ml-auto` (no manual margins)
- Transitions: `transition-all duration-200 ease-out`
- Active link: `font-semibold text-white border-b-2 border-blue-400 pb-0.5`
- Sign In button: glass style `bg-white/10 backdrop-blur-sm border border-white/20 hover:bg-white/20`

## Page Layout

- Background: `bg-slate-50` (never pure white)
- Card centering: `min-h-[calc(100vh-12rem)]` (shifts card ~40-80px higher than default)
- Avoid excessive vertical whitespace

## Profile / Content Card

- Corners: `rounded-3xl`
- Shadow: `shadow-xl`
- Border: `ring-1 ring-slate-200` (no visible border)
- Internal padding: `p-10`
- Internal spacing: `gap-5` on `flex flex-col` (photo → name → detail → button)
- Avatar: `w-40 h-40 rounded-full ring-4 ring-blue-100`
- Name: `text-2xl font-bold text-slate-800 tracking-tight`
- Supporting text: `text-slate-600` with values in `font-semibold text-slate-800`
- Avoid blue text for body content. Blue = accent only.

## Button

- Corners: `rounded-xl`
- Shadow: `shadow-md` → `hover:shadow-lg`
- Transitions: `transition-all duration-200 ease-out`
- Hover: `hover:-translate-y-0.5` (lifts 2px)
- Active: `active:scale-95` (press feedback)
- Padding: `px-8 py-2.5`

## Colors

- Brand blue: blue-950 (darkest, navbar), blue-600 (primary button), blue-100 (avatar ring)
- Support text: slate-600, slate-800
- Background: slate-50
- No new colors. Only refine shades.
