---
name: blender-product-modeling
description: Use when building a Blender model from a sketch or spec.
---

# Blender Product Modeling

Class of task: user supplies a hand-drawn product sketch or asks for revisions to an existing model; agent builds/updates geometry, verifies it numerically, renders labeled multi-view images (outside / inside cutaway / back / service view), and delivers PNGs + native .blend (+ optional GLB).

## Driving Blender

- Primary channel: the Blender MCP addon socket on port 9876 with raw JSON — `{"type":"execute_code","params":{"code":...}}`; also `get_scene_info` and `get_viewport_screenshot` (there is no plain `screenshot` command). If the socket refuses, relaunch Blender GUI with the server auto-started (command in references/blender5x-errors.md), wrapped in a background script — the terminal tool refuses inline `&`.
- Save the .blend after every successful stage. GUI sessions crash mid-task; relaunching from the last save costs nothing.
- Batch renders and final exports go through headless `blender --background file.blend --python-expr` — one render per launch.
- Before trusting any object state from a previous step, re-open or re-query it: states, `hide_render` flags, and object positions drift across save/reload cycles. Re-set annotation-layer `hide_render` before every save.

## Build → verify → render → audit loop

1. Read the sketch with vision exhaustively BEFORE building: every view, every label verbatim (normalize misspellings), every relative position ("below X", "top-center facing down"), the single written dimension if any. Turn it into a part checklist — that checklist is the final acceptance audit.
2. Build geometry as separate named objects, one per real part. Labels, exploded states, and per-part render toggles all depend on this.
3. Verify numerically before rendering: bmesh face counts at known planes (e.g. hole faces at the front plane), world-space bounding boxes to confirm parts sit inside the device, and `scene.ray_cast` to prove cavities are open and lines of sight are clear. Call `bpy.context.view_layer.update()` + fresh `evaluated_depsgraph_get()` after any transform — stale depsgraphs report pre-move positions. Prefer doing transforms and ray-tests in separate socket calls.
4. Render, then vision-audit against the sketch checklist part-by-part (present / position / scale / orientation). Every audit finding gets fixed from root cause — wrong camera, occluded part, stray light, misplaced object — then re-render and re-audit. Iterate until no mismatch remains.
5. If vision is unavailable (402/timeout), pixel-stat scans of the saved render are the sanctioned fallback: count saturated color clusters in the cavity region, blown-white fraction, dark-dot fraction on a face, and sample pixels at `world_to_camera_view`-projected part coordinates.

## Annotate in 2D, never in 3D

3D text labels (billboarded text + curve leaders) cost hours: chips drift from text after camera changes, glyphs z-fight, leader ends notch text, labels occlude each other and the device. The fast path:

1. Render a CLEAN frame (all annotation objects hidden).
2. Project 3D anchor points to pixels with `bpy_extras.object_utils.world_to_camera_view` and print them as JSON. Anchor on the part's world-space bbox center read AFTER the final move — hardcoded coordinates drift on every recomposition.
3. Draw chips, leader lines, and ring dots in PIL on the host (Blender's Python has no PIL). Sort callout columns by anchor Y so leaders never cross; compute chip rectangles and assert none clip the frame; offset endpoints from chip edges so lines don't notch text.
4. Keep the clean render too — the label layer is a separate artifact you can re-lay out for free.

## Occlusion — the top cause of "the parts don't show"

White-on-white interiors hide components behind shelves and mid-walls from most angles. Before blaming materials or lighting, ray-cast from the camera to each part center: if the first hit is not the part, it's occluded. Fixes in order: lower the camera pitch / move closer so the view clears the occluding lip; move parts to their true sketch positions (parts below a shelf line are invisible from above — raise sensors above the shelf line if the sketch says they face down over the tank rim); slide the occluder aside for service views. Watch the extremes: too-steep angles hide the entire back wall, too-close angles land the camera inside the shell (frame goes all-white). Also check for a leftover dark cavity liner or stray annotation objects rendering in the shot.

## Exposure and contrast for white-on-white interiors

Blown-out cavities are almost always a stray light: inventory ALL lights (`type=='LIGHT'`, include Blender's default 1000 W point lamp) and world background strength first. Then: one interior area light aimed at the back wall (not the ceiling), world strength 0.10–0.20, exposure −0.9 to −1.2, and part colors saturated at the material level (deep PCB green, strong relay blue, saturated wire colors) so they survive the AgX view transform. Emission stays moderate (strength ~25, not 100) or AgX clips it to white. Verify per color with pixel-cluster counts in the cavity region; iterate.

## Service / exploded views

To show a removable part (tank slides out the back, cover lifts off): move the part together with its children (a water fill inside a tank moves with it); place secondary parts beside the sightline, never between camera and subject; set `dof.use_dof=False` (DOF blurs the moved part into a blob); pull the camera back until every moved part is fully in frame; then read label anchors from the objects' post-move world bboxes. The staged position must match the label text — "SLIDES OUT BACK" requires the tank visibly behind the device from that camera. Pick the camera side so the moved part reads behind the device, not in front of it.

## Delivery set

- Labeled PNGs per view (outside front, outside back, inside cutaway, service view) at 1600x1200 Cycles.
- One native .blend per state (outside vs inside), each with its per-view cameras saved — the user opens these by double-click; GLB only imports via File → Import → glTF, so never hand a user a .glb when they asked for "the Blender file".
- Optional: GLB exports (see blender-mcp's export rules; convert text/curves to mesh first) plus a Three.js viewer page for interactive labeled models.

## Blender 4.x/5.x API pitfalls

Full table in [references/blender5x-errors.md](references/blender5x-errors.md). The frequent ones: primitive operators reject `name=` (assign `bpy.context.object.name` after); `object.convert` takes `target=` in 5.x; `bmesh.ops.extrude_face_region` takes `geom=` and keeps source faces; it's `bpy.context.view_layer.update()`, not `scene.view_layer`; to open a box reliably, bmesh-delete the face then SOLIDIFY + BEVEL modifiers instead of inset/extrude bookkeeping; Boolean cutters must pierce a face and sit before Solidify/Bevel in the stack; verify openings by ray-cast, not by modifier count.