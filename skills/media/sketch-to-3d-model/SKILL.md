---
name: sketch-to-3d-model
description: Use when a user sketch must become a labeled Blender model.
---

# Sketch to 3D Model (Blender)

Workflow for: user hands over a hand-drawn product sketch (or photo) → extract part list + positions → build in Blender via the blender-mcp socket → deliver labeled renders of every view. The deliverable is judged on part accuracy to the sketch and label legibility, not on artistic merit.

## Standing user expectations (every instance)

- Every part named in the sketch gets a label in the delivered renders, using the sketch's own wording (normalize its spelling: "MANETIC REED" → "MAGNETIC REED SWITCH"). Do not invent extra names, and do not add features the sketch doesn't show (a logo flourish was rejected once already).
- EVERY delivered view gets a labeled version. An unlabeled render will be asked for again. Front, inside/cutaway, and back are the default view set.
- Give the user .blend files (double-click openable), not just .glb — .glb must go through File → Import → glTF 2.0 and the user will ask why it doesn't open.
- Distill the sketch with vision first: every view, every label verbatim, proportions, the one dimension if any. Re-read it during accuracy passes.

## Procedure

1. **Distill the sketch** with vision_analyze: part list with exact label text + arrow-target positions, proportions, dimensions. This is the acceptance checklist for the whole job.

2. **Build in stages, verify each** — shell/housing first, then interior parts per sketch positions, then details. Compute positions in meters from the sketch's proportions (IN = 0.0254). Convert label text via text objects ONLY if exporting GLB; see the 2D-label rule below.

3. **Geometry verification** — after each build stage, re-read state in a SEPARATE socket call:
   - `scene.ray_cast` through openings (expect to hit the part BEHIND the opening) to prove shells are open.
   - Count boolean-hole faces via bmesh (faces on the cut plane with tiny `calc_area()`).
   - Never trust ray_casts or counts run in the SAME script that edited the mesh — stale depsgraph lies. Same-script `bmesh` reads are local-space; world-space comparisons need `matrix_world @`.

4. **Cutaway camera occlusion test** — before rendering a cutaway, ray-cast from the candidate camera to each labeled part center; first hit must be the part itself. Iterate camera position (seconds) until the report is clean; render only then. A mid-height shelf occludes the back wall both from low cameras and from steep look-downs — the working angle is slightly above the shelf, aimed along it at the back wall.

5. **Lighting/exposure for white-enclosure interiors**: kill the default 1000 W scene lamp (it blows every interior to white regardless of your lights); saturate part base colors hard instead of fighting exposure alone; exposure ≈ -0.9 with a 30-60 W cavity area light is the working window (darker reads as void, lighter clips). AgX clips strong emission to white — LEDs at emission ~25 keep their hue, 100 becomes a white blob. Verify each render with pixel stats: color-predicate counts per part + blown-white fraction in the cavity crop. When vision and pixel data contradict, crop the disputed region, upscale 2x, re-ask vision on the crop — full-frame audits misread small geometry.

6. **Labels as 2D overlay, not 3D text** — 3D text labels cost 6+ fix rounds (billboard drift, glyph z-fighting, lines notching text, occlusion): render a CLEAN frame, project anchor points with `bpy_extras.object_utils.world_to_camera_view`, draw chips/leaders/dots in PIL. Sort callout rows by anchor Y so leaders don't cross. Projected part centers land inside the part — for exterior surface callouts, correct the endpoint to the device silhouette (scan rows for the outermost non-background pixel); a leader ending in open background is the most common defect, audit every endpoint.

7. **Deliver** — labeled PNG per view (1600×1200 Cycles, named cameras), .blend per state variant, GLB only if asked. Per-view audit with vision, iterating until endpoints all land on parts.

## Variant .blend files (outside/inside/exploded)

- Explicitly set hide_render for EVERY state-dependent object (annotation layer, covers, inside light) in EACH save — file-splits lose hide state and 3D annotation text (mirrored, from behind) leaks into clean renders.
- Verify each saved variant headless: `blender --background file.blend --python-expr "<inventory: name/location/hide_render>" | grep DATA`. A save without a readback is an unverified save.
- Name cameras per view (OutFrontCam, OutBackCam, ICam...) and select by name when rendering; grabbing 'the first camera' silently renders the wrong view.

## Blender 5.x API breaks (verified on 5.2)

- Primitive operators reject `name=` — create, then `bpy.context.object.name = "X"`.
- `bmesh.ops.extrude_face_region` takes `geom=`, not `faces=`.
- `bpy.ops.object.convert(target="MESH")` — not `type=`.
- `bpy.context.view_layer.update()` — not `sc.view_layer`.
- Principled BSDF: `"Emission Color"` + `"Emission Strength"`, `"Transmission Weight"` — guard with `inputs.get()` for cross-version safety.
- Open-hollow-box: bmesh inset+extrude leaves a rim capping the face, and bmesh face-deletion alone re-caps it — delete the front face (`bmesh.ops.delete(context="FACES")`), then SOLIDIFY + BEVEL modifiers, then verify by fresh-call ray-cast.

## Curated references

- `~/.hermes/skills/blender-mcp/` (hub skill, read-only): export pipeline, GLTF gotchas, material survival matrix, error tables.
- Socket fallback when the MCP server is down: raw JSON `{"type":"get_scene_info"|"execute_code"|"get_viewport_screenshot"}` on port 9876; relaunch with `blender file.blend --python-expr "...addon_utils.enable...BlenderMCPServer...start()"`.
