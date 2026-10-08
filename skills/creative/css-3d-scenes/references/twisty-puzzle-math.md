# Twisty-puzzle construction math (CSS 3D)

Numbers below use a 3x3 cube with `pitch = 88` (cubie spacing), `gap = 8`, `face = 80` (cubie box size). Generalize symbolically.

## Box construction

- Cubie box: `width/height = face`, positioned `left/top = −face/2`, 6 faces at `translateZ(face/2)` and `rotateX/Y(90deg) translateZ(face/2)`.
- Sticker: child of the face, `position:absolute; inset: 7px` (~9% of face), `border-radius: 8px` on `11px` face.
- Stubborn `left/top` plus `translate3d` centering pulls its own trick (layout position adds to the 3D translate): use only `left/top = −face/2` and put the position in the translate.

## Cubie transforms

- State per cubie: `pos` (integer grid coords) + `rot` (accumulated 3x3 orientation matrix).
- Composed transform: `translate3d(x·pitch, y·pitch, z·pitch) matrix3d(rot)` — translate first, then the orientation matrix (rotation about the cubie's own center).
- A layer turn multiplies the orientation of every cubie on the layer by the 90° rotation R about the turn axis and translates its position by R as well. Update the FULL stored matrix (position and orientation) on every turn: recomputing orientation from positions is impossible, and positions stay derivable from the matrix.

## Snap rule

After each turn, for every matrix coefficient: multiply by 4, `Math.round`, divide by 4. Safe because orientations are 90° multiples (coefficients in {0, ±1}) and positions are integer multiples of pitch. Float drift is invisible until it is a wrong snap; snap every turn, not just at reset.

## Gesture turn: scrub + release snap

Motion model for drag-driven turns — distinct from the matrix snap rule above (which quantizes coefficients after baking).

- **Commit**: after the drag passes a small dead zone (~10px), derive axis/sign via the camera-space method and freeze it; from then on the gesture contributes only a scalar.
- **Scrub**: `angle = clamp(projected_drag_px · DEG_PER_PX, 0, 90)`, `DEG_PER_PX ≈ 0.55` (90° ≈ 165px). Projected drag = pointer travel along the unit direction frozen at commit (dot product). Straight-line projection is enough for a single-axis turn — skip arc physics.
- **Release snap**: `deg1 = angle > 45 ? 90 : 0`; tween `deg0 → deg1` over `SNAP_MS ≈ 320` with `cubic-bezier(.2, 1.4, .4, 1)` (back-out overshoot; reduce to 0 duration under reduced motion). Bake the state at `deg1` only: `deg1 = 0` bakes an identity and must leave the state byte-identical.
- **Tween shape**: interpolate `deg0 → deg1` (not `0 → 90`) so the snap can start from the scrubbed angle; `paint(t, deg)` applies the live transform each frame, `bake(deg)` commits with deg=0 = identity repaint. The commit-then-autoplay queue path can be deleted outright.

## 90° rotation matrices

```
Rx(90): [1,0,0; 0,0,-1; 0,1,0]   Ry(90): [0,0,1; 0,1,0; -1,0,0]   Rz(90): [0,-1,0; 1,0,0; 0,0,1]
```

CSS `matrix3d` is COLUMN-major: `m(a,b,c,d,e,f,g,h,i,j,k,l,...)` rows are (a,e,i), (b,f,j), (c,g,k).

## Camera math

- Math space: `M = Ry(yaw)·Rx(pitch)`. CSS application is the y-flip conjugation `T = S·M·S`, `S = diag(1,-1,1)`, because CSS y points down. Computed `matrix3d` must equal `T` element-for-element.
- Screen drag -> turn axis: convert the drag vector into math space via the inverse camera matrix; the dominant world-axis component is the turn axis. The drag direction sign combined with the grabbed sticker's normal determines the turn sign.
- Projected face-rect sanity at yaw −28°, pitch 22°, cube half-size 132: top ≈ 95×28, right ≈ 43×95, front ≈ 77×68. A near-square projected rect means the camera is near face-on.

## Inner core (gap-tunnel seal)

- A core of one `.cubie`-shaped box with 6 solid `.face` planes (no stickers) scaled uniformly about the scene origin. Keep it OUT of the cubie array — the scene DOM is wiped and rebuilt on every reset/scramble, so the core must be re-created inside the same build function.
- Scale factor: wall planes land at `scale · face / 2`. `scale = 2` puts them at exactly `±face` — too deep: an oblique ray entering a top-surface crossing (half-pitch, 3·half-pitch, half-pitch) threads past the corner between the top and side walls. `scale = 3` puts walls at `±3·face/2` (±120 here): 8px behind the outer surface (`3·pitch/2 + face/2`), well clear of the inner plane (`3·pitch/2 − face/2`), and no crossing ray survives.
- Rules: wall planes must sit between the inner shell and the outer surface (closer to the surface is safer), and must not coincide with any face plane (z-fighting). Validate with the solved-state pixel scan, not by eye.

## Leak-color pixel scan

```python
# solved cube: only white/green/red visible -> any blue-dominant pixel in the cube box is a leak
from PIL import Image
im = Image.open('shot.png').convert('RGB').crop(box)
pix = im.load()
for y in range(h):
    for x in range(w):
        r,g,b = pix[x,y]
        if b > r + 40 and b > g + 40 and b > 90:  # hue threshold, tune per palette
            hits.append((x,y,(r,g,b)))
```

Compare hit counts before/after a fix; ~57 hits at 4x sampling was a real cross-seam leak, 0 is the pass bar.
