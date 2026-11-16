# Mobile horizontal-overflow debugging

When `document.documentElement.scrollWidth > window.innerWidth` at a narrow viewport (test 320px, not just 390), find the FORCING node — the overflow list shows victims first.

## Probe method

1. Replicate the exact UI state the failing check used (rows added, dialogs open) — overflow often exists only there.
2. List candidates: elements whose `getBoundingClientRect().right > innerWidth + 1` or `scrollWidth > clientWidth + 1`. Outermost wrappers appear first and are usually victims.
3. Walk up from the worst offender measuring min-content: for each ancestor set `width: min-content` temporarily and measure, or inspect which descendant's `getBoundingClientRect().width` cannot shrink. The forcing node is the deepest element whose min-content width exceeds its container.
4. Check `getComputedStyle(el).minWidth` — a resolved `auto` on a grid/flex item means min-content floor (`min-width: auto`), the classic silent floor.

## Bug-class table (forcing node → fix)

| Symptom | Cause | Fix |
|---|---|---|
| Grid column resolves to a wide fixed px (e.g. 519px) at narrow width | Bare `grid gap-*` without explicit columns creates an implicit `auto` track sized to MAX-CONTENT of its children — an `overflow-x-auto` scroller inside contributes its full scroll width as max-content | Add `grid-cols-1` (i.e. `minmax(0,1fr)`) or `minmax(0,1fr)` on the track; then children shrink properly |
| Row of fixed-size buttons won't shrink | `flex-none` (or `w-N`) children total wider than the viewport | Fluid at base (`flex-1` or `flex-wrap`), compact fixed sizes only at `md:` and up |
| Grid/flex child won't shrink despite `overflow-hidden` | `min-width: auto` min-content floor | `min-w-0` on the child |
| Long unbroken token (URL, filename, email) | No wrap opportunity | `break-words` / `min-w-0` on the containing flex/grid item |

## After fixing

- Re-probe in the SAME state the check uses, at 320px and 390px; a fix that clears the default view may leave the post-interaction state broken.
- Sweep all files touched in the same batch for the same bug class (e.g. grep for `className="grid` without `grid-cols` / `grid-template`) — one visual pass that introduced the pattern usually introduced it more than once.
- A partially-visible horizontally scrolling row needs a scroll AFFORDANCE (edge fade via `mask-image:linear-gradient(...)`), or a clipped card reads as broken rather than scrollable.
- Full-page screenshots cannot verify fixed-nav clearance (stitching artifact) — use viewport-only screenshot scrolled to the bottom plus bounding-box math.