# Mobile horizontal overflow: diagnosis recipe

Suite signal: `document.documentElement.scrollWidth - document.documentElement.clientWidth > 1` at a narrow viewport (the fit matrix runs 320/390/430 and up).

## Order

1. **Reproduce at the failing width in the exact UI state the suite used** (same role, same clicks, same added row or open form). Overflow often exists only in that state.
2. **Find overshooting leaves:** evaluate over all elements, collect `getBoundingClientRect().right > viewportWidth + 2` where `children.length === 0`, sort by width descending. Filtering on parents shows only victim wrappers stretched to the column width; the forcing node is deeper.
3. **If offenders are only slightly wide or none appear, the container has a min-content floor.** Measure with the min-content probe below and recurse until the deepest node whose min-content exceeds the viewport is named.
4. Fix at the owning layer (table), re-run the suite check at every width.

## Min-content probe

Clone subtrees into a hidden `width: min-content` div and measure; recurse into any child whose min-content exceeds the viewport:

```js
const probe = document.createElement('div')
probe.style.cssText = 'position:absolute;left:-9999px;top:0;width:min-content'
document.body.appendChild(probe)
const minc = (el) => {
  const c = el.cloneNode(true)
  probe.innerHTML = ''
  probe.appendChild(c)
  return Math.round(probe.getBoundingClientRect().width)
}
// walk: if minc(el) > viewportWidth, record {tag, cls, minc} and recurse into children
```

## Root causes and the fix at the owning layer

| Mechanism | Fix |
|---|---|
| Bare `grid`/`flex` container with no explicit base columns: implicit `auto` track sizes to max-content of its content | `grid grid-cols-1` at base plus `md:grid-cols-N` variants (`grid-cols-N` = `minmax(0,1fr)`, so tracks shrink) |
| `overflow-x-auto` / `overflow-hidden` scrollers inside a grid or flex item (carousel tracks, chip rows): they clip visually but still contribute full content width as min-content | The scroller is not the bug — the un-capped track around it is. Fix the track (row 1). Never mask with `overflow-x-hidden` on the page. |
| `1fr` track or flex row with `shrink-0`/fixed-width items (badges, price, CTA) | `minmax(0, 1fr)` tracks; `flex-wrap` on rows; `flex-1 min-w-0` on shareable items |
| `<input>` intrinsic width inside a flex row | `flex-1 min-w-0` on the input |
| Row of fixed-width buttons that must fit one narrow line (e.g. 7 day toggles) | `flex-1 min-w-0` at base, fixed `md:w-11 md:flex-none` at md+ |
| Longest unbreakable text (`whitespace-nowrap` spans in a row) | let it wrap at base or give the row `flex-wrap` |

Every listed mechanism is a layout bug at the owning layer. Do not mask overflow with `overflow-x-hidden`; the next content change re-breaks it silently.
