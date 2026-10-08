---
name: css-3d-scenes
description: Use when building interactive 3D scenes in pure CSS 3D.
category: creative
version: 1.0.0
---

# CSS 3D Scenes

Single-file interactive 3D objects (twisty puzzles, dice, card flips, product viewers) with `transform-style: preserve-3d` + vanilla JS. Choose this over Three.js/WebGL when the object is boxes and planes and a dependency-free one-pager is the deliverable. Construction math lives in [`references/twisty-puzzle-math.md`](references/twisty-puzzle-math.md).

## Procedure

1. **Scene skeleton**: `.stage` (perspective) -> `.scene` (width/height 0 at center so children position around the origin; carries the camera rotation) -> positioned boxes. Scale tokens: `--pitch` = box spacing, `--face` = box size (= pitch − gap).
2. **Box = element + 6 `.face` planes** at `translateZ(±face/2)` + `rotateX/Y(90deg)`. `transform-style: preserve-3d` on every ancestor of a transformed child.
3. **Paint layering**: outward faces get a plastic body (`.face`, dark, rounded) + a colored sticker child (inset margin, rounded). Inner faces get a dark sticker too, so gaps never show raw background.
4. **Seal the interior** before rendering (pitfall 2): one `.core` box of 6 solid planes scaled so its walls sit just inside the visible shell; `pointer-events: none`; rebuilt whenever the scene DOM is rebuilt.
5. **Camera**: `M = Ry(yaw)·Rx(pitch)` in math space, applied as the CSS `matrix3d` of the conjugation `S·M·S` (y-axis flip). Keep camera state separate from object rotations: orbiting must never look like a move.
6. **Interaction**: pointer events with `touch-action: none` on the stage. Drag on a sticker = layer turn (project the drag vector through the inverse camera matrix to pick the turn axis and sign); drag on empty stage = orbit; wheel = zoom.
7. **Turn motion = scrub, then snap** (recipe in the reference): while the pointer is down, rotate the grabbed layer live with the drag as a scalar along the committed turn direction; on release, past half the turn complete the 90°, below it unwind to rest with the state unchanged. Never commit on gesture end and autoplay a fixed tween (pitfall 5). Axis/sign derivation stays in one tested pure function; the scrub only moves a scalar along it, so drag physics never touch the sign convention.
8. **Turn math, motion-model numbers, core numbers**: see the reference.
8. **Verify headlessly** (mandatory) before shipping.

## Pitfalls

1. **`backface-visibility` is not inherited — put it on the painted leaf.** A wrapper element paints no pixels, so hiding its backface does nothing and far-wall stickers bleed through gaps. Set it on the sticker leaf; keep the body two-sided so gap tunnels read dark.
2. **Gap channels between boxes are see-through tunnels**, and rounded tile corners leave diamond holes at every 4-tile crossing, so far-side colors or the page background leak through seams. Fix: a sealed dark inner core (6-plane shell) whose walls sit between the inner shell and the outer surface (~one gap behind the surface). A core whose walls sit deeper gets threaded by oblique rays at the crossings — compute one worst-case crossing ray before trusting any scale. Wall planes must also clear every box face plane or they z-fight.
3. **"It renders flat" is usually the camera angle, not the renderer.** A near-face-on still of a correctly rotated object looks 2D. Before touching render code, assert the computed `matrix3d` against the expected conjugated rotation and check projected face-rect aspect ratios (a square face at 3/4 view must have a non-square bounding rect).
4. **Vision models over-report tiny artifacts and reuse identical vague wording across fixes.** Never chase pixels on a vision verdict alone. Measure: scan the screenshot for leak colors in a discriminating frame state (a solved cube shows only 3 hues, so any 4th dominant-hue pixel is a leak) and compare counts before/after the fix.

5. **Commit-then-autoplay reads as "instant rotation, no motion"** even with a smooth tween: the drag itself produces no visual change (the gesture only decides the turn), and ease-out front-loads the motion (a 220ms ease-out cubic moves ~2/3 of the rotation in its first 60ms). Scrub the layer with the drag and animate only the remaining snap; gate both release branches — past the snap threshold the state changes, below it the state is identical after the unwind.

## Headless verification (mandatory)

Playwright (Chromium headless; see environment notes for the module path). Expose a small self-test API on the page (matrix invariants, move bookkeeping) and run it both in-page on load and from the harness.

- **Real pointer drags, never synthetic events**: hit-test the target sticker with `elementFromPoint` and assert the hit element IS the sticker (anything else means it is occluded), then mouse down/move/up. Assert a sticker drag changes exactly one layer (9 of 26 boxes for a 3x3), and an orbit drag changes the scene matrix without incrementing the move count.
- **Motion is measured, not eyeballed** — screenshots cannot prove motion. When the complaint is "instant"/"no motion", sample distinct per-frame transform strings during the drag (rAF loop, `Set` of signatures) plus the span while the tween runs; gate on >2 distinct paints during the drag and a nonzero animating span. Triage before rewriting interaction code: `prefers-reduced-motion` first (zeroing turn durations converts drag motion into state jumps — only zero auto-played animations), then a stray CSS `transition` on the animated element. Playwright `mouse.move` steps can land inside one frame and collapse to one paint — wait ~35ms between steps or the motion sampler undercounts.
- Screenshots at desktop and mobile viewports; one scroll-zoom probe.
- Pixel-scan screenshots per pitfall 4. In the scrambled state legit stickers can share the leak hue, so use a solved-state shot as the discriminator.
- Only ship after the harness passes with zero page errors at both viewports.

## Deliverable

One self-contained HTML file, zero dependencies. Deliver per the user's convention: copy to the repo/project root AND `~/Downloads`, with a README pointer saying what it is and how to open it.
