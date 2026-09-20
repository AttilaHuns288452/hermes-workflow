---
name: blender-agent-workflow
category: 3d
description: Use when building a Blender 3D model from a sketch.
---

# Blender Agent Workflow

Driving Blender to turn a reference (sketch/photo) into a verified, delivered 3D model. For MCP tool basics, GLTF export flags, and material-survival tables, see the `blender-mcp` skill; this skill covers the build→verify→deliver loop around it. Blender 5.x API renames that break copy-pasted bpy scripts: see `references/blender52-api.md` — check it before running any script taken from 4.x-era examples.

## The Loop

1. **Read the reference exhaustively first.** One vision pass: every view, every labeled part with exact text, proportions, dimensions. List the checkpoints as a table BEFORE building — this table is the acceptance test for the whole session.
2. **Build in stages** (shell → major internals → details), one `execute_code` call per stage, printing a compact JSON summary (object names, dims, face counts) each time.
3. **Verify geometry with geometry**, render for evidence, deliver last. Never ship on a plausible-looking render alone.

## Verify 3D Claims (geometry is ground truth, renders are evidence)

Vision audits of renders are probabilistic: identical geometry scored 2/10 → 8/10 across iterations and verdicts flip between renders (perforations read as 'raised bumps', then 'recessed holes', with unchanged meshes). Run a vision audit every iteration — it catches real placement bugs — but when a claim contradicts known geometry, settle it with geometry:

- **Is a face open?** `scene.ray_cast(depsgraph, origin, direction)` through the opening. Requires `bpy.context.view_layer.update()` + a FRESH `evaluated_depsgraph_get()` — and run the ray test in a SEPARATE script execution from the edit; a depsgraph captured before the edit reports the old mesh.
- **Do holes exist?** Count faces at the plane: bmesh, filter by WORLD-space face center (`matrix_world @ f.calc_center_median()`) and an area threshold. bmesh coordinates are LOCAL — comparing them to world coordinates proves nothing.
- **Did pixels change?** Project known 3D points to pixels (`bpy_extras.object_utils.world_to_camera_view`) and sample the render at exactly those pixels — never eyeball a region guess.
- **Is emission colored?** Under AgX, high Emission Strength clips to white (a blue LED renders white). Keep strength ~20–30 and pixel-verify color (`B > R+15`), not brightness.
- **How many vents?** Face counts at a plane give exact counts (e.g. 794 faces ≈ 2×8 bores + rims) even when the camera angle visually flattens the pattern.

## Opening a Box (reliable recipe)

Boolean cutters and bmesh inset+extrude both fail silently or cap the face back. Deterministic path: bmesh-delete the front face → SOLIDIFY modifier for wall thickness → BEVEL modifier for rounding. No selection bookkeeping, no leftover rim faces. Verify with the ray test above.

## Perforation Grids (boolean)

One cylinder + two ARRAY modifiers + one BOOLEAN DIFFERENCE. Pitfall: ARRAY offsets apply in the object's LOCAL axes — on a rotated cylinder relative offsets send rows sideways or below the floor. Use `use_relative_offset=False; use_constant_offset=True` and displace along the local axes you actually want, or compute world-axis steps by hand. Verify with the face-count-at-plane check.

## Annotated Views (labels/callouts)

3D text labels in Blender are a trap: billboards drift from chips, glyphs z-fight, leader lines notch text, labels occlude each other and the device. Fast path:

1. Render a CLEAN frame (all annotation objects hidden).
2. Project each 3D anchor to pixels: `world_to_camera_view(scene, camera, Vector(anchor))` → `(co.x*W, (1-co.y)*H)`.
3. Draw chips, leader lines, endpoint dots in PIL. Sort callout rows by anchor Y per column so leaders never cross; start lines at the chip EDGE (center-start notches the text); clamp column X inward so the longest chip can't clip the frame — then re-check the final PNG for clipping. A half-off-canvas label is a failed deliverable.
4. Use the sketch's own label text (normalize its misspellings) — the labels are the accuracy contract with the user.

For GLBs that must carry labels in-geometry: text as curves + leaders as POLY curves + sphere dots, then `convert(target='MESH')` BEFORE export — font/curve objects silently drop from glTF. Warn the user that in-geometry labels read edge-on at some orbit angles; HTML-overlay labels are the fix if they object.

## Sketch-Accuracy Pass

When the user supplies a sketch and asks to make the model accurate to it:

1. Extract the checkpoint table (see step 1) with exact positions — 'under the shelf facing down', 'left wall at shelf height', 'bottom half of interior'. Proportions in the sketch beat earlier guesses; re-measure, don't defend.
2. Fix geometry to the table, then re-run the vision audit against the table item by item.
3. Extras added on earlier latitude (a logo, a filler panel) become liabilities — delete anything the sketch doesn't show unless structurally necessary.

## Delivery (multi-view)

- Save ONE .blend per view state (outside/inside), each with its own named cameras (OutFrontCam, OutBackCam, ...) and correct visibility baked in. Set `scene.camera` explicitly to the named camera before every render — a fallback like 'first camera object' grabs whichever sorts first and renders the wrong view; it looks plausible until a check catches it.
- Visibility is fragile: after toggling hide_render on layers (covers, wires, annotations), inventory the state with a headless `--python-expr` before rendering — a script that crashed between toggle and save leaves stale state (covers hidden in the outside file) that silently poisons every later render from that file.
- Deliver .blend (native, opens on double-click) + per-view PNGs + .glb (web/interchange — tell the user it imports via File → Import → glTF 2.0). .glb alone is not the deliverable.
- Render headless: `blender --background file.blend --python-expr "..."` (~90–190s per Cycles frame at 1600×1200, 256 samples, denoised). Batch multiple cameras inside ONE blender invocation — each launch pays ~10s startup. Background-queue long renders rather than foreground-waiting past tool timeouts.
- Save named cameras INTO the .blend so the user can hit F12 and reproduce any view.

## Vision-Endpoint Flakiness

vision_analyze throws 409 'duplicate request' and multi-minute timeouts intermittently. Retry once on 409; on repeated failure or timeout, fall back to statistics (region brightness histograms, color-cluster counts, projected-point sampling) and geometry checks — they answer 'are the holes there / is the LED lit / did the label land' deterministically. Don't burn the session re-polling a dead endpoint.
