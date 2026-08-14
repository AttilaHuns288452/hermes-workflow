---
name: figma-html-import
description: Build import-safe HTML screens for Figma import.
---

# Import-safe HTML for Figma (html.to.design)

User workflow: design deliverables are **HTML files imported into Figma via html.to.design** — never Figma-native drawing. Deliver all three variants, keep old deliverables, always visual-QA.

## Import-safe markup rules (proven failures)

- **NO `position:absolute`/`fixed`, NO `transform`** on overlays — html.to.design drops or misplaces them (dialogs vanished; boards imported byte-identical base pages).
- **NO rgba/alpha scrims** — semi-transparent overlays import as solid **black screens**. Dialogs/sheets/toasts must be **flat static cards in normal flow** on the light page background.
- **NO overlays at all** in single-file merges: if a frame needs a modal, the modal IS the frame content (page content above, dialog card below).
- Everything else in normal block/flex flow. Frames exactly `390×844`, `overflow:hidden` on the frame is fine.

## Deliverable pattern

1. **Separate files** per screen (`NN_Name.html`), each fully self-contained (own CSS + own SVG sprite). Splitting avoids import dropping frames when one file holds many.
2. **Merged single file** (`Name_All_NN.html`) — user imports this for convenience: one shared `<head>` (CSS once + sprite once), frames stacked in a `.board`, small gray `.frame-label` ("01 · Login") above each frame. Merged imports keep dialogs now that overlays are static-flow.
3. **Wireframe variant** (`Name_Wireframe.html`) — same merged file + appended `<style>` that redefines `:root` CSS variables to grays (`--accent:#8a8f98`, `--text:#4b5057`, etc.) plus `!important` overrides for hardcoded classes (banners, `.text-red`, inline-styled avatars). Zero body changes.

## Generator pattern

One Python generator script emitting all files from shared CSS/EXTRA/sprite + per-screen body strings. Reuse proven frames verbatim; only rebuild broken ones.

## Verification (always)

- **Geometry via Playwright**, never trust vision alone: frame `getBoundingClientRect()` must be 390×844 at y=0 (no phantom space above), `scrollHeight <= 844` (no vertical clip), no element `right > frame.right` (no h-overflow). Script pattern: iterate `.frame` children, record deepest bottom / widest right.
- **Vision QA** (qwen-vl via OpenRouter — route now 402, verify key/credit first; fall back to geometry when down). Vision flags are hypotheses: every flag gets a geometric check before fixing. Vision cannot count `•` glyphs reliably.

## Pitfalls

- **Raw CSS outside `<style>`** (e.g. f-string concatenation bug) = dead styles AND phantom layout space above the frame (whole page shifted down ~650px). Always brace-check and verify frame y=0.
- Sprite `<svg>` must be `display:none` (or absolute+hidden), never plain inline 0×0 — inline svg creates a phantom line box.
- Duplicate sprite ids across merged files are harmless (first wins) — dedupe anyway.
- `fit-content` boards: block-level body elements will report viewport-width rects — that's expected, not overflow.
