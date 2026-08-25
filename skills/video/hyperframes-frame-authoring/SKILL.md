---
name: hyperframes-frame-authoring
description: >-
  Use when writing HyperFrames frames that must pass lint.
---

# HyperFrames Frame Authoring (worker-side)

Practical, lint-verified rules for writing `compositions/frames/<id>.html`
sub-compositions in a HyperFrames project (product-launch / promo pipeline).
The orchestrator dispatches: `.hyperframes/frame-packets/_role.md` (worker
contract), `.hyperframes/frame-packets/<id>.md` (frame block + shot sequence),
and `frame.md` (design tokens) — READ all three fully before writing. These
findings were verified against the actual linter in an 8-frame promo build and
are the fixes the lint gate enforces.

## File shape (must pass lint)

- Exactly one bare `<template>…</template>` fragment — first bytes `<template`,
  last `</template>`. No doctype/head/body.
- Root: `<div id="root" data-composition-id="<frame_id>" data-start="0"
  data-duration="<dur>" data-width="1920" data-height="1080">`.
- Style the root via the `#root` selector — NEVER a class on the root
  (assembly scopes classes to a descendant selector that can't match it, so
  the whole scene renders unstyled; Studio preview still looks right).
- Full-bleed background (color field / grid / glow) = a full-duration
  `class="clip"` layer with `data-start` / `data-duration` / `data-track-index`,
  never a `background` on `#root`.
- Every `<style>` and `<script>` block, including the GSAP CDN `<script src>`,
  goes INSIDE the template.
- One paused timeline: `window.__timelines = window.__timelines || {};`
  `const tl = gsap.timeline({ paused: true });` … `window.__timelines["<frame_id>"] = tl;`
- No CSS `transition`, no `repeat`/`yoyo`, no `Math.random()`, no `Date.now()`,
  no runtime fetch (GSAP CDN at authoring is fine — the project's own
  `index.html` does it).

## Lint codes that bite (and exact fixes)

- `overlapping_clips_same_track`: clips on the same `data-track-index` must not
  overlap in time — the linter allows one clip per track at a time. Fix: give
  EVERY simultaneous layer its own track index (bg=0, glow=1, kicker=2,
  wordmark=3, tagline=4, …). Do not share one foreground track across all text
  elements even if they're "one layer" conceptually.
- `gsap_timeline_set_initial_hide`: `tl.set(target, {opacity:0}, 0)` inside the
  paused timeline does NOT render at frame 0 (playhead sits exactly at 0).
  Fix: call immediate `gsap.set(...)` OUTSIDE the timeline before building it.
  This still satisfies the "pre-animation state set with gsap.set" determinism
  rule and frame 0 shows the hidden state.
- `overlapping_gsap_tweens`: sequential tweens on the same target are flagged
  when the next tween's start time EQUALS the previous tween's end time
  (boundary-touch counts as overlap). Fix: small explicit gaps between
  segments (e.g. 0.05s) or pad/trim durations so windows never touch. For a
  "hold + subtle pulse" section, hand-sequence each pulse segment with gaps —
  no `repeat` needed (repeat is banned anyway).
- `gsap_css_transform_conflict`: never put a CSS `transform` (e.g. translateY
  centering) on an element GSAP animates a transform prop on — GSAP overwrites
  the whole transform. Center with flex/inset/margins, or use `fromTo`.
- `font_family_without_font_face`: fires only for families NOT in the
  renderer's bundled alias set (`FONT_ALIAS_MAP2`) and not declared/imported.
  Bundled families — Inter, Montserrat, Outfit, Nunito, Oswald, Roboto,
  Open Sans, Lato, Poppins, JetBrains Mono, IBM Plex Mono, Space Mono,
  EB Garamond, Playfair Display, Source Code Pro, Noto Sans JP — pass with NO
  `@font-face` at all: the renderer auto-resolves them. Family names are
  lowercased before the check, so `font-family: "Inter"` (no @font-face) lints
  clean — the toolchain's own `index.html` uses bare `Inter`; mirror it.
  Never invent a woff2 path when a project ships no font files (a bogus
  `@font-face` 404s at render). System fonts with no downloadable file
  (Hiragino Sans, Microsoft YaHei): `@font-face { font-family: '…';
  src: local('Exact Name'); }` alone satisfies the check. Do not name any font
  that is neither bundled nor shipped — clean render machines lack system
  CJK fonts and the text silently falls back to generic.
- `missing_template_wrapper` / `missing_composition_id`: file must be exactly
  one template with the frame id on the root.

## Reading the real lint rules (versions drift)

Doc-listed rule codes in the worker contract (`clip_missing_data_attrs`,
`timeline_not_paused`, …) do NOT all exist verbatim in the pinned CLI — codes
and severities drift by version; only the installed source is truth. Read it:

```
# Windows/git-bash — the npx cache hashed dir differs per machine:
ls ~/AppData/Local/npm-cache/_npx/*/node_modules/hyperframes/dist/cli.js
# then grep for: "code: \"<rule_name>\""  or  FONT_ALIAS_MAP2 / extractUsedFontFamilies
```

Rule bodies carry the exact severity, message, and fixHint. This is how the
font-alias and track-index behavior above were verified for 0.8.1
(see `references/lint-internals.md`).

## Patterns that pass lint (session-verified)

- **Clip wrapper for N small elements**: many scattered pieces (noise chips, dots, labels) sharing one time window → ONE `class="clip"` wrapper as a direct root child (with its own data-start/duration/track-index) containing plain inner divs that GSAP animates. The wrapper is the timed clip; inner divs are ordinary positioned elements. Saves a track per element and keeps the layout audit sane (16 chips → 1 track, not 16).
- **Per-element values in a stagger**: bake targets into data attrs (`data-o="0.35"`, `data-rot="-12"`) and read them with function-based GSAP values: `opacity: (i, el) => parseFloat(el.getAttribute("data-o"))`. Deterministic, no parallel arrays to keep in sync, works with `stagger`.
- **Static transforms via `gsap.set`, never CSS**: elements GSAP transforms (rotation, x/y, scale) must carry NO CSS `transform` in the stylesheet. Set static rotation/position once with `gsap.set` at build time (function-based value per el), then only tween opacity/translate.
- **Decorative transient layers**: `data-layout-ignore` on a decor wrapper (e.g. rotating noise chips near canvas edges) excludes it from layout audits — the narrow opt-out. Avoid `data-layout-allow-overflow` for decor: it silences perception checks (text-clipping, foreground-over-panel) for EVERY descendant (blast radius).
- **Rotated decor stays on canvas**: a rotated rect's axis-aligned full width ≈ W·|cosθ| + H·|sinθ|. Keep centers ≥ half that from canvas edges; on 1920×1080 also keep rotated bottoms above the caption keep-out (≈ 0.83 × height ≈ 900).
- **Scale breath without repeat/yoyo**: two explicit tweens at separate times (`scale:1→1.02` at T, `scale:1.02→1` at T+1.7) — keep ≤ the allowed % (e.g. ≤2%).
- **Duplicate asset paths**: packet may cite `capture/assets/x.png` while `assets/x.png` also exists — verify identical with `cmp` before choosing; use project-root-relative `assets/...` in src/url().

## Verify with lint BEFORE reporting done

- `npx hyperframes lint` scans ALL project files INCLUDING
  `compositions/frames/*.html` — a not-yet-wired frame IS linted, despite the
  worker contract's claim that lint only covers the assembled project. Run it
  right after writing.
- Bar = 0 errors on YOUR file. Errors in OTHER files (e.g. `index.html`
  missing a captured asset) are pre-existing — leave them alone; the dispatch
  says do not modify other files.
- Command pattern that works: `npx hyperframes lint 2>&1 | tail -5`
  (exits 0 even with findings — read the `✗` error and `⚠` warning lines).
- Isolate YOUR file when lint reports on the assembled project: `npx hyperframes lint 2>&1 | grep "<your-id>"` — zero hits = your file is clean; findings listed for sibling frames or index.html are theirs to fix, not yours.
- `write_file` reports `lint: skipped` for HTML with no linter attached — the
  hyperframes CLI is the real gate, so run it explicitly.

## Dispatch vs design tokens

- The frame packet is authoritative where it conflicts with `frame.md` (e.g.
  packet says dark canvas `#0b0d1a` + periwinkle `#5e6ad2` while frame.md says
  cream `#ffffff` + cobalt). Use frame.md for fonts/tokens only where the
  packet doesn't override.
- Guardrails: all content above the caption keep-out (~83% of height, ≈896px
  on a 1080-tall canvas); visible text is short motion-graphics copy, never
  narration sentences; hero visible by t ≤ 0.5s — entrance tweens use `fromTo`
  starting at their cue time so frame 0 is never a blank static hide.

## References

- `references/lint-internals.md` — verified hyperframes@0.8.1 lint internals:
  bundled font alias map, rule implementations, package discovery paths.