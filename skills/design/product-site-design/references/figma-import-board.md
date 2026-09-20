# HTML -> Figma import-safe board (html.to.design)

When the user will import a static site into Figma, ship a single self-contained board file: one page per site page, labeled 1280px frames stacked vertically.

## Import-safe transforms (assert each in the build script so a violation fails the build)
| Breaks import | Fix |
|---|---|
| `var(--x)` custom properties | parse `:root` vars, substitute literals in CSS AND inline styles; assert no `var(` remains |
| `position: sticky/fixed` | convert to static (navs render once at top of frame) |
| `@keyframes`/`animation`/`transition`/`backdrop-filter` | strip rules entirely (Figma is static) |
| `<img src="local">` | base64-inline every local image (jpg/png/svg with correct MIME); assert 0 remaining relative srcs |
| `<body class="page-x">` scoped page overrides | extract with `<body[^>]*>` and CARRY the class onto that page's frame wrapper div, or scoped rules silently vanish for that page |
| inter-page links | rewrite `href="*.html"` to `#` |
| HTML comments | strip (direction contracts, review notes) |

## Generator pattern
A single python script (`build-figma-board.py`) in the repo: read pages -> extract `<body>` inner -> transforms -> wrap each in `<div class="frame-label">NN · Name</div><div class="frame">...</div>` -> inline the flattened CSS -> assert-based self-checks (no var(), no banned props, frame count, brace balance) -> write one HTML file. Include the Google Fonts `<link>` in the board head.

## Verify the board, not just the source pages
Serve locally and check with Playwright: frame count, all `<img>` load (scroll the full board first — below-fold images false-report broken), 0 console errors, one scoped-override spot check per page. Kill the server after.

Fix invalid source markup (e.g. `height="auto"` on an `<svg>`, a self-closed tag missing its `>`) in the PAGES before generating — the board copies the DOM, so source console errors and clipped elements import straight into Figma.

## Related
An `html-to-figma-import-safety` / `figma-board-ops` skill exists in another profile with extra transforms (sprite inlining, anchor-to-div conversion, border-triangle arrows); adopt via curator if a board needs them.