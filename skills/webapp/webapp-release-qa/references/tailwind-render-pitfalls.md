# Tailwind / CSS render pitfalls in React apps

Cascade and interaction failures that make correctly-rendered React look broken. Each entry: the mechanism, the diagnostic, the fix shape. Grid-track/span rules live in the `frontend-design` skill.

## 1. Side-specific borders killed by color utilities

`divide-y divide-gray-100` emits `> :not([hidden]) ~ :not([hidden]) { border-color: … }` — specificity (0,3,0) — which beats a row's `border-l-primary-600` (0,1,0). Same collision: an all-sides `border-gray-100` on a row overrides its own `border-l-*` depending on stylesheet order. Symptom: the FIRST row shows its accent, all later rows don't.

Diagnose with computed styles on several rows:
```js
[...document.querySelectorAll('.row')].map(r => getComputedStyle(r).borderLeftColor)
```

Fix shape — side-specific colors, no divide layer:
```jsx
<div className="rounded-2xl">                        {/* no divide-* */}
  <div className="border-b border-b-gray-100 last:border-0 border-l-4 border-l-primary-600">…</div>
</div>
```

## 2. Global reduced-motion layer freezes all CSS animation

Apps ship `@media (prefers-reduced-motion: reduce) { *,*::before,*::after { animation: none !important } }` as an a11y layer. Brave's fingerprinting protection reports reduced-motion ALWAYS, so in that browser every keyframe animation is dead while JS-driven motion works — the split (JS advances, CSS strips don't move) is the tell.

Diagnose: read `getComputedStyle(el).animationName` in a `reducedMotion: 'reduce'` Playwright context. `'none'` while a class rule declares an animation = a competing `!important` layer.

Fix shape — out-rank the layer per-animation without touching it:
```css
.marquee-track {
  animation-name: marquee !important;
  animation-timing-function: linear !important;
  animation-iteration-count: infinite !important;
  animation-duration: var(--marquee-duration, 28s) !important; /* shorthand !important would pin duration to 0s */
}
```
```jsx
<div className="marquee-track" style={{ '--marquee-duration': (n * 7) + 's' }}>
```
Inline custom property feeds the duration; an inline `animation-duration` loses to the layer's `0s !important`.

## 3. Pointer stranding on custom sliders/carousels

Element-scoped `onPointerUp` never fires when the release happens outside the element (fast drag, mouse-up elsewhere) — `dragX`/`paused` stay stranded: the strip renders translated fully out of the clip window (blank area with the strip's normal height, dots still fine) and autoplay stays paused. A bfcache restore can resurrect the exact stranded state, so "it survives reload" is not evidence against this cause.

Diagnose: read the strip's computed `transform` and compare against `idx × slideWidth`; an offset that is not a clean slide multiple with no active pointer = stranded.

Fix shape — capture + global safety + self-heal:
```jsx
onPointerDown={(e) => { drag.current = { x0: e.clientX }; try { e.currentTarget.setPointerCapture(e.pointerId) } catch {} }}
// + window-level pointerup/pointercancel that resets drag + pause
// + a 1.5s interval: if (!drag.current) setDragX(v => v ? 0 : v)
```
Keep a runnable check: simulate press → drag → release OUTSIDE, assert the strip returns to a slide boundary and at least one card is visible within ~2.5s.

## 4. Diagnosis order when "cards don't render"

1. Fresh headless page at the target viewport — if it renders, the defect is in the user's session (stale HMR tab, stranded state, browser policy), not the code.
2. Raw pixels of the user's screenshot (PIL row scans for surface colors) — vision models misread empty regions and phantom pills.
3. DOM: does the node exist? computed transform / width / opacity? `innerWidth` overflow?
4. Only then change code; when the cause is confirmed, patch + one runnable check, and tell the user exactly which artifact to refresh (dev tabs need closing, not F5, when HMR is dead).

## 5. Clamped text colliding with the row beneath

A title/meta block reserved for N lines with `min-h` collides with the next row after any type change, and looks like a broken clamp rather than a sizing bug: the ellipsis renders at the end of line N, then line N+1 paints inside the reserved height and is sliced mid-glyph by the row under it.

Mechanism: `min-h` is an absolute height and does not track line-height. Drop the font or leading and the box is suddenly taller than N lines, so `line-clamp`'s own N-line height no longer matches the reserved height — the taller one wins and the overflow is clipped by the card, not by the clamp.

Diagnose both signals before touching CSS (the rects alone read as "no overlap"):
```js
const a = card.querySelector('a[title]');
({ h: a.clientHeight, scrollH: a.scrollHeight,          // scrollH > clientH => lines are being cut
  clamp: getComputedStyle(a).webkitLineClamp,
  display: getComputedStyle(a).display })               // must be -webkit-box, not flow-root/block
```

Fix shape — reservation and clamp derived from the same line count:
```jsx
{/* 18px text at leading-snug (1.375) = 24.75px/line => 2 lines = 49.5px */}
<a className="line-clamp-2 h-[3.1rem] overflow-hidden text-lg font-semibold leading-snug [overflow-wrap:anywhere]">
```
Keep `h` and the clamp in the same commit as any font-size/line-height change, and leave the `h` as the hard clip so a clamp regression still cannot paint over the next row.
