---
name: figma-board-capture
description: Use when handing a live JS site to Figma as an import board.
---

# Figma Board Capture — live JS-rendered sites → html.to.design import

Build a single-file Figma import board from a running website whose pages render entirely in JS
(no hand-built frames exist). Complements the external hand-built pipelines (`figma-board-ops`,
`design-handoff-boards`, `figma-html-import` — all external_dirs, read-only; their transform tables
carry the full hand-built-frame rules).

## Pipeline (generator script, one Python file per project)

1. **Recon** — inventory every reachable state: grep the site JS for tabs (`data-tab`), wizard steps,
   modals (`openModal`), filtered views, localStorage keys. Verify each trigger opens its state
   (`click` → `is_visible` assert) BEFORE writing the generator. Skip states unreachable in the UI;
   report them, never fake them.
2. **List states** in the generator as `PAGES = [("NN · Label", "/path?query", seed), ...]` —
   labels numbered by deck position. Seeds: `dict` = localStorage values (wishlist etc., applied via
   `context.add_init_script` BEFORE `goto`), `str` = interaction script, `{"tab": id}` / `{"modal": actions}`
   for tab/modal states.
3. **Capture** with Playwright Python sync API per state: fresh context (1280w, device_scale_factor 2),
   `goto(url, wait_until="networkidle")`, settle wait, drive the interaction, assert the state landed
   (`is_visible` on the pane/dialog — never trust the click), then `page.evaluate` the body HTML.
   Wizard `goto N` = advance to ABSOLUTE step N by clicking each pane's Continue; answers must be
   selected BEFORE advancing (validation blocks empty Continue). Modal triggers hidden behind tabs
   need the tab clicked first.
4. **Sanitize** the captured markup (see transform table below) — assert the negatives, build fails if
   violated.
5. **Emit** one merged file `Name_All_N.html`: shared `<head>` (flattened CSS + Google Fonts link),
   frames as labeled blocks (`NN · Label` div + `.frame` div) on a `.board` flex column.
6. **QA**: node/Playwright geometry pass — per-frame rect, non-blank innerText, no element extending
   past the frame's right edge, zero blanks. Vision-check 1–2 representative frames LAST; vision flags
   are hypotheses (watch for off-by-one frame index in the screenshot script — verify which frame you
   actually captured before believing a 'wrong content' flag).

## Import-safe transform table (bake into the generator, assert each)

| Breaks import | Fix | Assert |
|---|---|---|
| `var(--x)` in CSS + inline styles | Flatten from `:root` tokens; resolve alias chains TRANSITIVELY into the token map (`--accent: var(--primary)` must land on final hex) and subst into captured markup. Flatten all stylesheets in ONE pass (a second stylesheet references the first's tokens). | `"var(" not in output body` |
| `rgba(r,g,b,a)` scrims/borders — import as solid black | Blend over the ACTUAL backdrop to opaque hex. White-on-navy alpha (hero outlines) blends over the navy, not white — a single global white-blend corrupts colors. | `"rgba(" not in output body` |
| `<svg>` sized only via CSS (`width:100%;height:auto`) | Importer collapses it to an empty frame — charts silently vanish. Add explicit `width=`/`height=` from the viewBox; keep the style attr. | every `<svg` tag has `width=` |
| `position:fixed/sticky` (headers, trays, overlays) | Flatten to `position:static`, normal flow. | `"position:fixed" not in doc` |
| `@keyframes/animation/transition/backdrop-filter` | Strip entirely (importer drops or misrenders). | negatives assert |
| `<script>/<style>/<link>` nodes, skip-links, `display:none`/zero-opacity elements | Strip — skip-links live at `top:-48px` and import as phantom space; hidden elements import as stray boxes. | no `<script` in body |
| `<a href>` navigation | Rewrite to `href="#"`. | — |
| Overlay modals (fixed scrim + centered dialog) — drop or black-screen on import | The dialog card IS the frame content: open live, then JS-flatten the overlay to `position:static` on a flat light-gray band and hide the page behind it (main/shell/header/footer — admin pages often use a shell div, not `main`; hide both). | per-frame `.modal` visible + page hidden |
| Degenerate default chart view (e.g. one-point frontier, no line) looks like a capture bug | Capture the segmented view (category tab / filtered series) as its OWN frame alongside the default — both are real states. | — |

## Deliverable variants

- **Full deck**: `Name_All_N.html` — one import, every state labeled.
- **Partial deck** ("only the missing parts"): a sliced generator variant reusing the same sanitizer
  over a reduced PAGES list, output named for the subset (`Name_Subset_M.html`). Keep both generators;
  the full one is the source of truth.
- Never modify the source site/repo when the user says it's hands-off — generators live in their own
  project directory reading the site via local HTTP or the deployed URL.

## Verification commands

```bash
python3 build_board.py                      # asserts fire inside
node qa.js                                  # geometry: per-frame rect + text + overflow + blank count
git -C <source-repo> status -sb             # source untouched (clean vs origin)
```

Verify against the LOCAL file only; there is no deploy step.

## Pitfalls

- Auth-gated states: if a modal exists in code but no UI path calls it (e.g. `requireLogin` defined
  but never invoked), it has no real state to capture — tell the user, offer the one-line site fix,
  don't synthesize the screen.
- Label numbering must be sequential and match `len(frames)`; assert it. Renumber by editing the
  PAGES list, never by string-replacing labels (produces duplicates).
- Playwright module paths vary by install (node: `~/.hermes/hermes-agent/node_modules/playwright`;
  Python sync API: hermes venv) — probe with a one-line require/import before writing the script.
- Vision QA sees the frame you screenshotted, not the one you meant — index off-by-ones in the
  screenshot script produce confident 'wrong modal' readings; cross-check the frame label in-image.
