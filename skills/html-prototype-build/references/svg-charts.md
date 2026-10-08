# SVG charts & data micro-viz (single-file HTML)

## Nice y-axis ticks without clipping data
- Fixed interval count over floor-rounded steps clips: `step = nice(range/4)`, `lo = floor(min/step)*step`, `hi = lo + 4*step` lands the top BELOW the data max whenever step equals range/4 exactly. Derive the interval count from the snap instead:
  ```
  function niceStep(range, n) {
    var raw = range / n, pow = Math.pow(10, Math.floor(Math.log10(raw))), k = raw / pow;
    return (k <= 1.2 ? 1 : k <= 2.4 ? 2 : k <= 3.5 ? 3 : k <= 7.5 ? 5 : 10) * pow;
  }
  // step = niceStep(range, maxIntervals - 1)   // slack vs range/maxIntervals
  // lo = Math.floor(min/step)*step; hi = Math.ceil(max/step)*step
  // grid = [lo, lo+step, ... hi]  -> interval count falls out of the snap
  ```
- Label every gridline. Format numbers per series (no $ on counts, no decimals on whole dollars). Assert tick spacing evenness (max−min interval ≤ tolerance) and that the grid covers the data without ballooning past it.

## Chart filling a stretched card
- `preserveAspectRatio="none"` on a fixed viewBox distorts circles and stroke widths. Instead: make the card a flex column (`.card:has(#chart){display:flex}`), measure the plot box at render (`getBoundingClientRect()`), set `viewBox="0 0 w h"` in code to the box's own pixels — 1:1 mapping, no distortion, no letterboxing. The static SVG width/height attrs define the CSS box; the viewBox is rebuilt inside the render function on every call.
- Re-render on window resize (debounced ~150ms) so ticks and points stay in bounds; hover geometry is rebuilt per render.
- Hover readout: fixed-size card (width/height attrs) beside the chart prevents layout shift; translate a point marker along the curve instead of swapping the SVG.

## Sparklines & mini-bars
- Normalize each series to its own min/max with ~10% pad before mapping to the box, so every sparkline shows real shape regardless of data scale; assert min amplitude (max−min of y) > 0 in the check.
- Trend direction follows the delta it illustrates (down card = falling line, down color), never the data seed.
- Keep spark geometry constant (fixed w/h attrs), park it absolutely in a card corner, reserve its width on adjacent text rows.
- Mini-bars: width from `pct.toFixed(2) + '%'` (rounding lands exact at test tolerance); assert rendered bar width ÷ track width equals its label. Legend/segment totals must reconcile with the headline KPI they visualize.
