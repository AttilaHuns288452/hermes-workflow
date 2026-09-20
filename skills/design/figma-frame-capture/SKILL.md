---
name: figma-frame-capture
description: Use when a JS-rendered app needs Figma-importable frames.
---

# Figma Frame Capture (JS-rendered apps)

html.to.design imports static HTML. When the source app renders all content client-side (prototype with `js/*.js` builders, wizard steps, localStorage state), extracting `<body>` from source produces empty or step-1-only frames. Capture the RENDERED DOM with Playwright instead, then sanitize. This complements `figma-board-ops` (static-template merge pipeline, external/read-only — its transform table still applies to captured output).

## Pipeline

1. **Serve locally** — `python3 -m http.server 8765` in the app root. Dies between sessions; restart and `curl -s -o /dev/null -w "%{http_code}"` before assuming otherwise.
2. **Capture per page** — Playwright: `viewport 1280×900`, `device_scale_factor 2`, `goto(..., wait_until="networkidle")` + 400ms settle. Fresh `browser.new_context()` PER frame — contexts share nothing, so seeded state can't leak across frames.
3. **Seed state** — `context.add_init_script("localStorage.setItem('key', JSON.stringify([...]))")` before navigation (wishlist items, compare selections) so account pages show populated UI instead of empty states.
4. **Drive wizards by clicking, answer-before-advance** — pick the answer on the currently visible pane, THEN click Continue; validation blocks advancing on an unanswered pane. Model `goto N` as "advance to absolute step N": track the current step counter and click `[data-step=cur] [data-next=cur+1]` until `cur == N`. Never re-click earlier Continue buttons — they are hidden by then and the click times out.
5. **Assert landing truthfully** — `page.is_visible('[data-step="N"]')` (or equivalent pane check). Stepper sub-labels update on selection even when the pane never switched; indicator text alone lies.
6. **Clean in-page BEFORE extracting** — one `page.evaluate` pass: remove `script,style,template,noscript,link`; remove any element with `display:none` / `visibility:hidden` / `opacity:0` (hidden elements import as stray boxes); rewrite `a[href]` → `#`; drop accessibility skip-links (they sit at negative offsets and import as phantom space).
7. **Sanitize the extracted HTML** — same transforms as any board: flatten `var()` in markup AND inline styles (JS-rendered DOM carries vars in `fill="var(--x)"`, `style=` attrs, SVG text), flatten `rgba()` to opaque hex blended over the element's actual background, strip keyframes/transitions, `position:sticky/fixed` → `static`.
8. **Assemble board** — `.board` flex column, `.frame-label` above each frame, `.frame{width:1280px; overflow:hidden}`. Desktop-web frames use full-page height — the 390×844 phone grid is a mobile convention.

## Sanitizer pitfalls

- **Flatten alias chains into the var MAP, not just the CSS** — tokens like `--accent: var(--primary)` must resolve inside the map too, or every later `body.replace("var(--accent)", ...)` substitutes an unresolved value and inline/SVG vars survive the assert by hiding inside captured markup.
- **Flatten ALL stylesheets in one pass** — theme/identity CSS layers reference the base `:root`; flattening per-file strands cross-file references.
- **Blend rgba over the real background** — white scrims sit on dark hero bands; blending everything over white shifts them invisible. Two blend helpers: over-white and over-band, applied by where the color occurs.
- **Scan for banned tokens in the BODY only** (`doc.split("</head>")[1]`) — the board's own `<style>` block trips naive whole-doc asserts.
- **Selector quoting**: keep `[data-budget="10-20k"]` double-quoted inside single-quoted Python strings; alternating quote styles across `str.replace` patches is how seed strings get mangled — after any scripted edit, print the seed lines and `ast.parse` before running.

## Verification (deterministic, then vision)

- Playwright geometry pass over the merged board: per frame — expected width, no descendant `right > frame.right`, non-trivial `innerText` (short = empty/blank frame), element count sane.
- Content spot-checks per frame class: wizard frames contain their pane's content markers (budget band labels, priority rows); results frames contain rank badges; seeded frames show the seeded items.
- Vision spot-checks: styling, selected states, score rings. Index screenshots by board position (nth `.frame`), never by assumed filename — wrong-index grabs analyze the neighboring frame.

## Session layout

Generator lives OUTSIDE the app repo (user forbids touching some repos): `~/Documents/Projects/<app>-figma/build_figma_board.py` reading the app as a sibling directory. Rerunnable anytime the app changes; deliver the single merged HTML as a MEDIA: file.

Reference implementation of every snippet in this skill: `scripts/gadgetwise_build_reference.py`.
