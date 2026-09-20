---
name: site-to-figma-board
description: Use when a JS-rendered site needs a single-file Figma board
---

# Site → Single-File Figma Import Board

Builds a `<Project>_All_<N>.html` board (labeled stacked frames) that imports cleanly via html.to.design. Two capture modes — pick by how the site renders:

- **Source-parse** (static pages): strip `<body>` inner per page, sanitize. See `figma-board-ops` (external, read-only) for the 390×844 frames-deck transforms table.
- **Rendered-DOM capture** (JS-rendered sites): parsing source yields empty shells — all content is built client-side. Capture the rendered DOM in a real browser, then sanitize. This skill is that pipeline.

## Procedure

1. **Serve**: `python3 -m http.server 8765` in the project root (static server dies between sessions — restart and curl-check 200 before assuming).
2. **Choose frames**: every real screen, including query-param states (`category.html?cat=…`, `compare.html?ids=…`, `…html?id=…`) and the logged-in/admin views. Seed `localStorage` via `context.add_init_script` for states that read it (wishlist, compare history); use a fresh context per page when seeding so state never leaks between frames.
3. **Capture**: Python playwright (sync API) ships in the Hermes venv: `/home/attila/.hermes/hermes-agent/venv/bin/python`. Viewport 1280×900, `wait_until="networkidle"` + ~400ms settle, then evaluate an in-page cleanup that returns `document.body.innerHTML`:
   - remove `script, style, template, noscript, link`
   - remove `.skip-link` — it parks at `top:-48px` and imports as phantom space above the frame
   - remove every element whose computed style is `display:none` / `visibility:hidden` / `opacity:0` — hidden nodes import as stray boxes
   - rewrite `a[href]` → `#`
4. **Sanitize CSS** — concatenate ALL stylesheets FIRST, then flatten once. Flattening per-file fails when one file's rules reference tokens defined in another's `:root` (leaves unresolved `var(` strays). Parse `:root` tokens, then resolve alias chains (`--accent: var(--primary)`) iteratively **and substitute resolved values back into the token map** — captured markup carries `var()` in inline styles, so the map must hold final literals, not alias pointers.
5. **rgba()**: never ship it. Blend over the ACTUAL painted background — white is right for overlays on light surfaces, but white text/borders on a dark band blend over the band's hex (e.g. hero navy), not white.
6. Strip `@keyframes`/`animation`/`transition`/`backdrop-filter`; `position: sticky|fixed` → `static`.
7. **Assemble**: `.board` (gray page bg, centered column, ~48px gaps) → `.frame-label` (`NN · Name`, uppercase, gray) → `.frame` (fixed width = design width, `overflow:hidden`, white bg). Shared `<head>`: Google-fonts link + flattened CSS once. Frame height is natural (full page), width fixed.
8. **Build-time asserts**: scan the BODY only — the board's own `<style>` tag literally contains `<style`, so whole-doc bans always false-trip. Assert in body: no `<script`, `<style`, `var(`, `rgba(`, `position:fixed|sticky`, `@keyframes`, `<use`, `<symbol`; brace balance; frame count == page list length.
9. **QA geometry** (playwright, node side: `/home/attila/.hermes/hermes-agent/node_modules/playwright`): per frame — width == design width, `innerText` length (blank < ~40 chars), element count, horizontal overflow (`child right > frame right + 2`). Zero blank, zero overflow, then deliver.

## Pitfalls

- Don't hand-write frames for a JS-rendered site — the DOM after render includes generated SVG attributes, seeded defaults, and hidden scaffolding you can't reconstruct from source. Capture, don't reconstruct.
- Remote image URLs stay remote (import machine needs internet); base64-inlining a whole catalog balloons the file for no gain.
- If charts/visualizations compute size from viewport, give the frame content a settle delay before capture — capturing too early imports collapsed panels.

## Standing user preferences

- The generator lives OUTSIDE the product repo (sibling dir like `Projects/<name>-figma/`) — product repos stay untouched unless explicitly asked; verify with `git status` that the repo is clean after the build.
- Naming: `<Project>_All_<N>.html`; labels `NN · Name` in page order; deliver by writing `MEDIA:/abs/path` in chat.
- Keep the generator script alongside the board so the next site change is a rerun, not a rebuild.