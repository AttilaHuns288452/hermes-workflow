---
name: ui-navigation-flow-board
description: Use when building a 2D user-flow graph from UI frames.
---

# UI navigation flow board (frames as graph nodes)

Build a FigJam/Miro-style navigation map where every node is a real 390×844
UI frame, edges are orthogonal connectors with arrowheads, and clusters
group application areas. Used for capstone design decks: a separate
"presentation/understanding" artifact alongside the linear import board.

## Layout: hand-placed (col, row) grid, not a vertical stack

- `POS = {name: (col, row)}` in a `flow_layout.py`; x = X0 + col*COL_W
  (520), y = Y0 + row*ROW_H (1000). Branches spread HORIZONTALLY; chains
  continue downward; error/state frames sit directly under the action that
  causes them (dashed edge); destinations sit below their parent (solid).
- Two role-branches side by side: patient zone left, doctor zone right —
  this is what makes it read as a 2D map instead of a poster.
- Deep zones get extra row pitch (`if row >= 6: y += (row-5)*220`) when a
  "density wall" forms.
- Cluster boxes: dashed rounded rects from (col,row) bounds + high-contrast
  title chips (white text on dark fill, 17px — small gray labels fail vision
  audits). Non-overlapping boxes only.

## Edges + routing (import-safe, behind frames)

- Edges: (src, dst, style) with style in solid (forward nav, #334155),
  dash (error/alternate state, #7c8ea0), back (back/cancel, #8b9cb1).
  Short-name edges ("00→01") resolve to full names by prefix.
- Routing rules that avoid crossing frames:
  1. Directly below (same col, adjacent row): vertical + down arrow.
  2. Descending, different col: vertical stub from parent bottom to a
     horizontal BUS (staggered `bus_y = bottom + 34 + (col*13)%40` to avoid
     overlapping buses), horizontal to child x, drop into child top.
  3. Descending, same col multi-row: right-side LANE (frame edge + 30), enter
     from the right — a center drop crosses the frames in between.
  4. Same-row back edge across other frames: route BELOW the row
     (`bottom + 20`), arrow up into the destination.
  5. Upward back edges: left lane (src.left - 45) up to dst.bottom + 10,
     horizontal to dst.left + 40, up arrow.
  6. Spans > 1500px get mid-span arrowheads (1/3 and 2/3) so direction
     survives zoom-out.
- Import-safe connector primitives (same rules as html-to-figma-import-safety):
  lines = 4px solid divs; dashes = 12px rects (NOT repeating gradients);
  arrows = 14×14 inline `<svg><polygon>` (NOT zero-size border triangles);
  z-index: connectors 0, cluster boxes 0, captions 1-2, frames 2.

## Captions

Two-line caption under every frame: bold title ("NN · Screen Name") + one
context line ("Shown when the password is wrong"). Solid background chip so
connectors pass behind legibly. Titles overridable via a notes dict
(("Custom Title", ctx) tuples).

## Verification loop (until CLEAN)

1. Regenerate; assert import-safety (no var(, rgba(, gradients, use-refs).
2. Playwright: frames count/size (390×844), zero pairwise frame overlaps,
   zero segment-through-frame crossings (filter out cluster boxes + captions
   by class/text; skip arrows). Each crossing gets named + fixed by rerouting
   (usually a lane/bus choice), not ignored.
3. Vision audit: full-page screenshot scaled to ~2200-2400px wide
   (`flow_shot.py` pattern with `Image.MAX_IMAGE_PIXELS = None`), then
   `hermes -z "... load <shot> with vision_analyze ..." -m mimo-v2.5-pro
   --provider opencode-go`. Fix findings, repeat. Common findings: labels too
   small/faint (white-on-dark chips fix), lines too thin (4px + 12px arrows
   fix), bottom-right density (extra row pitch fix), long spans losing
   direction (mid-span arrows fix). When providers rate-limit, the
   playwright geometry checks ARE the pass/fail.

## Pitfalls

- Filename-sorted merging destroys deck order — the merge must follow
  `order.txt` (see html-to-figma-import-safety).
- `margin-top:auto` nav pinning fails silently when the nav sits INSIDE the
  content wrapper — extract it as a direct frame child first.
- CSS fix rules appended after `</style>` are dead text — insert inside.
- Browser rects include body margin (~30px); subtract it when matching
  computed segment coordinates to find the offending edge.
