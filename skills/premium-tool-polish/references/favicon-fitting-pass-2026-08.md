# Favicon Fitting Pass 2026-08 — both sites get *fitting* icons

Follow-up to `favicon-brand-fix-2026-08.md`. User feedback: "why its jsut a boring fc" — bare `FC` initials are not fitting at 16px.

## What shipped

**freelance-rate-calculator** (`3140ec3`):
- `app/icon.svg` 32px — periwinkle gradient `#5e6ad2→#312e81` rounded `rx 8`, white calculator silhouette (outline + `$` screen + 3×3 dot grid), not plain `FC` text. Readable at 16px tab, matches `from-[#5e6ad2] via-[#4f46e5]` hero.
- `app/apple-icon.svg` 180px — same gradient + larger calculator, thicker stroke.
- `app/favicon.ico` + `public/favicon.ico` — 1510B PNG-ICO via `sharp` (regenerated from new `icon.svg`). Verified `curl /icon.svg` returns calculator SVG, `/favicon.ico` 200 1510B.

**anime-waifu-quiz** (`e77c6f5`):
- `app/icon.svg` 32px — dark `#0f0f1a` `rx 8` with gradient heart `M16 22.5 ...` (`#7c3aed 0% → #ec4899 50% → #3b82f6 100%`) + white sparkle `M24 7 ...` — fitting anime/playful brand, not generic `logo.png` fuzzy crop.
- `app/apple-icon.svg` 180px — same heart + 2 sparkles (main + subtle `opacity 0.7`).
- `app/favicon.ico` + `public/favicon.ico` — 904B PNG-ICO via `sharp`. Removed legacy `app/layout.tsx:75` manual `<link rel="icon" href="/logo.png">` so Next.js auto-discovery (`app/icon.*` / `app/apple-icon.*` / `app/favicon.ico`) wins; that tag was causing stale 628K PNG in `public/logo.png` to be used instead.
- Pitfall fixed: 2026-08-19 commit `e77c6f5` initially staged unrelated changes (`app/character/[slug]/page.tsx`, services, `Marquee.tsx`, `lib/characters.ts`); reverted with `git checkout --` before push — always `git status --short` before `git add .`.

## Pattern: boring initials → fitting silhouette

- Finance/tool sites → tool silhouette (calculator, chart, coin) + accent gradient + `$`/symbol hint
- Anime/playful → heart/star/sparkle + multi-stop vibrant gradient on dark, not flat color + initials
- Keep `system-ui` only if text is unavoidable; silhouette beats letters at 16px every time

## Verification

- `npm run build` both — freelance 19 routes (`○ /icon.svg`), anime 427 char pages + `/icon.svg`
- Live: `curl /icon.svg` on both returns fitting SVG (not FC text-only / logo.png)
- Live: `curl -I /favicon.ico` both 200 `image/vnd.microsoft.icon`
- Client: `Ctrl+Shift+R` — ICO cache is sticky

Skipped: custom hand-drawn illustration, multi-size ICO — silhouette scales to 16px with zero deps; add mascot art when brand has one.
