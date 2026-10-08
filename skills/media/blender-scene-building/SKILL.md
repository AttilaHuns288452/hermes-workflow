---
name: blender-scene-building
description: "Use when building a Blender model from a sketch over MCP."
---

# Blender Scene Building

Build models through the Blender MCP socket (`localhost:9876`), verify every claim numerically, deliver .blend + .glb + labeled PNGs. Export mechanics (gltf-transform pipeline, material loss, name mapping) live in the `blender-mcp` skill — this skill covers the BUILD side.

## Procedure

1. **Confirm the socket.** `get_scene_info` + `execute_code: print("ok")` + `get_viewport_screenshot` (there is no `screenshot` command). If port 9876 is dead, relaunch Blender with the addon auto-start (enable addon, instantiate `BlenderMCPServer`, start it) and re-check. Save the .blend before risky operations — booleans, bulk deletes, scene splits.

2. **Read the brief into a part list.** From a sketch: extract every labeled part, its location, and any dimension (vision_analyze the sketch with a modeling-specific prompt). State the derived dimensions before building — the user's "3 inch extension" callout sets the scale of everything else.

3. **Build by part, verify per stage.** Batch geometry creation into `execute_code` scripts. After each stage, verify numerically (see Verification below) — never batch the whole build then debug from one render.

4. **Verify geometry numerically.** Render-reading alone lies (see Pitfalls). Minimum checks:
   - Openings: `scene.ray_cast` from outside toward the interior — expect a named interior-part hit, not the shell.
   - Hole grids: count bmesh faces within a size/position band.
   - Occlusion: ray_cast camera→part-center and read the first hit's name before rendering a "clear view" — a mid-height shelf or misplaced panel silently hides labeled parts.
   - Placement disputes: `world_to_camera_view` projects a part into the frame; settle "where is it on screen" arguments with projected coordinates, not guesses.

5. **Light and expose by bracketing.** Kill the startup scene's default 1000 W point light. Emission under AgX clips to white near strength 100; ~25 keeps hue. Bracket exposure (render → pixel-scan blown-white fraction and saturated-color counts → adjust ±0.5 EV). White-on-white interiors: dedicated area light aimed INTO the cavity at the far wall, and confirm via occlusion ray-cast that a shelf doesn't shadow the parts behind it — fix part placement or camera angle, don't overexpose.

6. **Label in 2D, not 3D.** Render a clean frame, project anchors with `bpy_extras.object_utils.world_to_camera_view`, then run `scripts/annotate_render.py` to draw chips, leader lines, anchor dots, and a wiring color legend. Sort callout rows by anchor Y so leaders never cross; re-project after ANY camera/exposure change; inset column x by the longest chip width so nothing clips.

7. **Deliver all three artifacts.** `.blend` (per state/variant — users double-click it in Blender; .glb needs File → Import), `.glb` (convert FONT/CURVE objects to mesh first; `convert(target="MESH")` on 5.2, `type=` older), and rendered PNGs of each view. Set `hide_render` explicitly for every object before each save — visibility flags are the first thing lost when a scene splits into variants.

## Pitfalls (Blender 5.x scripting)

- Primitive operators reject `name=`: create, then `bpy.context.object.name = "X"`.
- `bpy.ops.object.convert` takes `target=` in 5.2, `type=` in older — try/except both.
- `bmesh.ops.extrude_face_region` takes `geom=` and KEEPS the source faces — delete them or the surface stays capped. To open a box: bmesh-delete the front face → SOLIDIFY modifier → BEVEL. Boolean cutters fail silently when mis-positioned; always prove the opening with ray_cast.
- Perforation grids: one cylinder + two ARRAY modifiers + BOOLEAN DIFFERENCE. `use_constant_offset=True` always — `relative_offset_displace` on a rotated cylinder displaces along LOCAL axes and drills holes through air.
- `bpy.context.view_layer.update()` + fresh `evaluated_depsgraph_get()` before any `ray_cast` after transforms; `scene.view_layer` does not exist.
- Bezier wires: object at origin, world coords in the points; converted to mesh they may still occlude ray tests — name them consistently (`Wire_*`) so verification can ignore or include them deliberately.

## Verification discipline

Vision audits of renders misread in repeatable ways: shaded holes look like raised bumps; an assembled proud panel reads as "detached"; white parts vanish into white walls. When vision and geometry disagree, re-verify geometry first, then re-render from another angle, then settle with pixel-stat scans (dark-pixel fraction in the face region for holes, saturated-color pixel counts per wire color, blown-white fraction for exposure). Ray-cast plus face-count plus pixel-scan settles every "is it there" question without a human.

When a user says parts "don't show", suspect occlusion first: ray_cast from the camera to each part center and read the first hit. Fix placement or camera before touching lights.