# Responsive Layout Mechanics — traps that silently inflate or shift mobile layouts

Stack-agnostic CSS truths. Each rule is a failure mode that renders *plausibly*
(wrong size, wrong position) rather than obviously broken, so it survives a
casual look and gets caught only by measuring rects.

## Grid track sizing

- **`auto-rows-fr` / `grid-auto-rows: 1fr` inflates every row to its tallest
  cell.** One multi-line child stretches the whole grid: a 7-column calendar
  whose cells should be ~48px square renders as ~48×113 portrait tiles because
  a single 2–3-line chip set the row height. Fix: clamp cell content to one or
  two lines (`line-clamp`), use compact single-line chips in narrow columns, or
  size tracks explicitly (`auto-rows-min`, `minmax(min-content, …)`) — never
  `fr` when cells are meant to be uniform-and-small.
- **A min-content child wider than its column forces overflow at the smallest
  width.** An icon + "N booked" row inside a 3-column cell can exceed the cell
  at 320px and push `scrollWidth` past the viewport. Let such rows wrap
  (`flex-wrap`) or drop the icon under the smallest breakpoint. Always probe
  `documentElement.scrollWidth` vs `window.innerWidth` at 320px.

## Control strips / segmented controls

- **`inline-flex` on a tab or segmented strip shrink-wraps to content width and
  floats left** instead of filling its column. For a mobile segmented control
  use `flex w-full` with equal-width children (`flex-1`) so it reads as
  full-width thirds. Keep the desktop toolbar `inline-flex`, but switch to
  `flex w-full` under the mobile breakpoint.

## View/tab-switch chrome stability

- **Render shared toolbar chrome (legend, heading, controls) in ONE stable DOM
  slot across every view.** When a page has Month/Week/Day-style views, chrome
  duplicated into two slots (e.g. a legend before the controls in one view and
  after the heading in another) makes the toolbar JUMP position on every switch.
  Pin each shared element to a fixed slot (e.g. legend always last and
  right-aligned) so variable heading length cannot shift it. Verify by reading
  the control's `getBoundingClientRect` before and after each switch — it must
  not move.
