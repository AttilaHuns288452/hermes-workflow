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
- Probe the GL device before any long render: on Optimus laptops headless Blender renders on the Intel iGPU unless launched with `__NV_PRIME_RENDER_OFFLOAD=1 __GLX_VENDOR_LIBRARY_NAME=nvidia`. Time ONE frame at target resolution first and gate the full render on that number — if per-frame time puts the job past its budget, kill it and fix the device. A silently slow render burns the session (26 s/frame on the iGPU vs 2.4 s/frame on the dGPU, same scene, same resolution).
- Before trusting any object state from a previous step, re-open or re-query it: states, `hide_render` flags, and object positions drift across save/reload cycles. Re-set annotation-layer `hide_render` before every save.

## Build → verify → render → audit loop

1. Read the sketch with vision exhaustively BEFORE building: every view, every label verbatim (normalize misspellings), every relative position ("below X", "top-center facing down"), the single written dimension if any. Turn it into a part checklist — that checklist is the final acceptance audit.
2. Build geometry as separate named objects, one per real part. Labels, exploded states, and per-part render toggles all depend on this.
3. Verify numerically before rendering: bmesh face counts at known planes (e.g. hole faces at the front plane), world-space bounding boxes to confirm parts sit inside the device, and `scene.ray_cast` to prove cavities are open and lines of sight are clear. Call `bpy.context.view_layer.update()` + fresh `evaluated_depsgraph_get()` after any transform — stale depsgraphs report pre-move positions. Prefer doing transforms and ray-tests in separate socket calls.
4. Render, then vision-audit against the sketch checklist part-by-part (present / position / scale / orientation). Every audit finding gets fixed from root cause — wrong camera, occluded part, stray light, misplaced object — then re-render and re-audit. Treat the first clean-looking render as a draft: run the strict audit (framing/crop, speckle/z-fighting, blown highlights, part identity, lighting form) and keep looping until it passes with no findings — "loop until it looks good", not first-verified-wins.
5. For any moving camera or multi-shot sequence, verify framing NUMERICALLY at each shot's start, middle and end: project the subject's full world bbox (including open doors, lids, exploded parts) through `world_to_camera_view` and assert it stays inside a ≥6% safe margin on all four edges. A still that fits can still crop mid-travel, and a bbox that omits an open panel hides exactly the part that gets cut; compute camera distance from model size and lens, never eyeball it from one preview frame.
6. If vision is unavailable (402/timeout), pixel-stat scans of the saved render are the sanctioned fallback: count saturated color clusters in the cavity region, blown-white fraction, dark-dot fraction on a face, and sample pixels at `world_to_camera_view`-projected part coordinates.

## Imported model cleanup (CAD/GLB/SKP imports)

Speckle and z-fighting in imported assemblies are material/geometry artifacts, not sampling noise — raising samples will not fix them:

- Imported materials often arrive as `blend_method='HASHED'` with `use_transparent_shadow=True` on fully opaque skins; stochastic alpha-hashed shadows speckle every render. For opaque materials (Alpha unlinked and ≥0.999) set `blend_method='OPAQUE'`, `use_transparent_shadow=False`, `use_backface_culling_shadow=True`. Leave genuinely transparent materials alone.
- Imports carry coincident shell pairs (front/back skins at identical world coordinates) that z-fight. Group meshes by world-space vertex signature, then either hide one shell per group or prove by pixel inspection that no shimmer survives. Record which choice was made — source-preservation and de-duplication are both defensible, an undeclared mix is not.
- Verify the cleanup at full resolution on the NOISIEST regions (seams, perforated strips, thin flanges seen at grazing angles), not on one wide beauty shot where artifacts hide.

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

## Frame-sequence film (optional deliverable)

When the deliverable is a motion showcase rendered from the model: render a numbered PNG frame sequence (Blender 5.x rejects `FFMPEG` as an image output format — frames first, mux with ffmpeg), keyframe camera motion across the FULL timeline so every frame is unique (a camera keyed to only part of the range renders a frozen second half), and burn captions via the ASS `subtitles` filter. Caption pitfalls: ASS timestamps are `H:MM:SS.cs` — `0:58:00.00` parses as 58 MINUTES, not 58 seconds, so a typo silently deletes the whole caption run (assert monotonic event times and zero overlaps before burning); text over bright product geometry needs `BorderStyle=3` with a fully opaque dark box or the caption disappears into the white enclosure. Subtitles must be wired at the ffmpeg stage — fixing the .ass file does nothing if the mux command never references it.

## Blender 4.x/5.x API pitfalls

Full table in [references/blender5x-errors.md](references/blender5x-errors.md). The frequent ones: primitive operators reject `name=` (assign `bpy.context.object.name` after); `object.convert` takes `target=` in 5.x; `bmesh.ops.extrude_face_region` takes `geom=` and keeps source faces; it's `bpy.context.view_layer.update()`, not `scene.view_layer`; to open a box reliably, bmesh-delete the face then SOLIDIFY + BEVEL modifiers instead of inset/extrude bookkeeping; Boolean cutters must pierce a face and sit before Solidify/Bevel in the stack; verify openings by ray-cast, not by modifier count.