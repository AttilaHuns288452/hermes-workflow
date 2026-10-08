# Visual / responsive QA matrix

Method for screenshot-matrix passes: every route × viewport × role, programmatic audit, then vision review. Produces the audit table and the before/after evidence set.

## Capture

- Viewports: `360x800, 390x844, 412x915, 768x1024, 1024x768, 1440x900` (narrow phone → phone → tall phone → tablet → laptop → desktop).
- Every route per role (patient/doctor/owner route lists live in the router); one logged-in context per role, one page per viewport.
- Save RGB PNGs only (never a grayscale copy), full-page, into a `screenshots/<pass>/` dir named `route__WxH.png`.
- Capture the BEFORE set from the current build in the same script run as the audit; re-shoot the AFTER set after fixes with the same script.
- When the user names a judging size (their display, e.g. 1920x1080), capture and critique at exactly that viewport as the PRIMARY pass: full-page shots and per-page vision review there first; the responsive matrix is the secondary gate. Judgement happens at one size, so that size gets the polish budget.
- QA widgets behind a dev flag render in every shot — either position them clear of CTAs/chrome or accept them as known fixtures in the report.

## Programmatic audit per shot (runs in-page)

1. Horizontal scroll: `documentElement.scrollWidth - innerWidth <= 1`.
2. Nav chrome per breakpoint: mobile = bottom tab bar visible + sidebar hidden, and tab labels equal the ROLE's tab set (never another role's); ≥768 = rail visible + bottom bar hidden.
3. Tap targets: visible buttons/links ≥ ~44px tall (report offenders with name + `WxH`; icon-only header chrome may stay ~36px by design).
4. Fixed/sticky elements: flag any fixed element extending past the viewport bottom.
5. Zero page errors for the whole sweep.

Record findings as `route @ viewport :: issue :: SEVERITY`; the run's finding count before vs after is the pass metric. `fullPage` captures composite fixed chrome at the edge — verify "clipped" findings with viewport-scoped bounding boxes first.

## Responsive correctness sweep (routes × widths × engines, no vision)

Fast deploy gate for "make sure it's responsive": every route × extreme widths × engines, two detectors, zero screenshots. `scripts/responsive-sweep.cjs <base-url> [routes...] [--engines=chromium,firefox,webkit] [--widths=...]` runs it and exits 1 on any finding.

- Widths: `320 360 390 412 480 640 768 834 1024 1280 1366 1440 1920 2560`, plus one phone-landscape (844x390) and 1366x768. Chromium always; Firefox + WebKit for anything shipping cross-browser (install engines with the bundled Playwright's own `cli.js` — a differently-installed Playwright is a different version and fails to launch them).
- Detectors: the same horizontal-overflow rule as above, plus a clipped-text leaf scan: text elements with `scrollWidth > clientWidth` while computed `overflow-x` is `visible`. Skip `auto`/`scroll`/`ellipsis` (intentional rails or truncation) and record those as known-intentional.
- Zero page errors across the whole run. Run the sweep after every layout-affecting change AND after any source restructure: a clean compile says nothing about crashed routes.

## Vision review

- Batch independent `vision_analyze` calls (several per turn); ask for concrete defects with severity, and separately for fidelity vs the matching design frame when one exists.
- Treat vision findings as hypotheses: placeholders/attributes are not page text, `closest()` matches self, and mid-animation frames misplace elements. Confirm each with a DOM query or pixel extents before "fixing".
- Cap annotated-crop zoom at ~1.08 — heavy zoom crops bottom overlays and manufactures cut-off findings.
- After fixes, re-verify with numbered check questions naming each intended change, then request a short PASS/FAIL verdict; open-ended re-reviews tend to confirm what they expect to see.

## Common desktop-target findings and their fixes

- Card grid rows lose alignment when names wrap 1 vs 2 lines: give the title block a 2-line `min-height`, or move badges off the title row onto a photo-corner overlay (the overlay also frees title width and kills forced name wraps).
- A wide table over few columns leaves a dead slab at desktop: cap `max-width` proportional to column count (e.g. `240 + n*380` px), keeping `min-width` + `overflow-x-auto` for phones.
- A `self-stretch` rail/sidebar beside short content shows large dead space: `self-start` so it hugs its content.
- An odd last grid child forced to `col-span-2` reads as broken at desktop: leave the orphan in one column.
- `marker:text-<name>` silently keeps the default bullet color when `<name>` is not a build-tool color token (the color lives only in custom CSS): use the real token name or arbitrary hex, and replace literal `•` glyphs with `list-disc` + `pl-*` to get a free hanging indent.
- Adjacent text blocks with different measures (paragraph `max-w-2xl`, bullet list wider) look broken: match their `max-w-*`.
- Content that looked balanced on mobile sits left-heavy inside a wide desktop container: cap the content block's width rather than the section container.

## Layout expectations to check explicitly

- Sticky CTAs clear fixed nav: `bottom-[calc(4.25rem+env(safe-area-inset-bottom))]` on mobile, plain offset at desktop where the tab bar is gone.
- Desktop replaces mobile chrome with a sidebar rail (same design system); content widens past the phone shell only at desktop breakpoints.
- Safe-area insets honored on header and bottom bars; no horizontal scroll at 360px.
