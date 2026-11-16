# Bottom-chrome overlap (mobile shell)

Bottom-anchored controls (chat composers, sticky submit bars) get covered by fixed chrome. Four causes and their fixes:

1. **Guessed chrome height.** A page reserves `calc(100dvh - <hard-coded chrome height>)`. Real chrome height varies — font scaling wraps its labels taller, safe-area padding adds to it, root font scaling rem-scales parts of it — so the guess always loses eventually and the control slides under the chrome. Fix at the owning component: the fixed chrome measures itself (ResizeObserver on the element → `document.documentElement.style.setProperty('--nav-h', h + overhang)`) and every consumer reserves `calc(... var(--nav-h, fallback))`. The measured rect already includes the element's own safe-area padding; add the overhang of negative-margin children (raised `+`/Book buttons draw outside the box) to the published value.
2. **Fixed pill/FAB anchored in the control's band.** `bottom: <nav height> + small gap` lands exactly on a composer that hugs the nav. Anchor such floaters ABOVE the composer band: `bottom: calc(var(--nav-h) + <composer height>)`. When the hidden-by-breakpoint chrome publishes ~0, one formula covers mobile and desktop.
3. **FAB over its own destination.** A floating button that navigates to page X covers X's primary action while on X. Hide it on its own route (`!path.endsWith('/x')`).
4. **Keyboard.** Without `interactive-widget=resizes-content` in the viewport meta, the layout viewport does not resize when the keyboard opens and any `100dvh`-sized layout leaves the input behind the keyboard. Add the token to the meta viewport; it also makes `100dvh` track the keyboard on supporting browsers.

Tailwind note: `h-[calc(100dvh-3.5rem-var(--nav-h,4.75rem))]` works as-is — arbitrary values normalize math spacing and accept a `var()` with a comma fallback.

## Reproduce (stock viewports often pass)

Headless device descriptors do not reproduce system font scaling. Grow the fixed chrome with injected CSS — its labels wrap and the chrome outgrows any hard-coded reserve:

```js
await page.addStyleTag({ content: 'nav.fixed * { font-size: 15px !important }' })
```

Sweep 320/390/412 px widths at 13px/15px; the overlap shows as `formBottom > navTop` by a few px.

## Verify with one generic check (targeted checks miss occluders)

Per-element asserts ("nav doesn't cover the form") miss the dev pill and the FAB. Scan EVERY visible fixed/absolute element for >2px two-dimensional rect intersection with the input box — that one check catches all occluders at once. Then vision-check a viewport screenshot for collisions; vision over-reports (divider lines through a raised FAB read as overlap), so confirm each finding with the same DOM scan before editing.

Harness with the full pattern (geometry + overlap scan + send/Enter behavior + font-scale sweep): `templates/composer-qa.cjs`.
