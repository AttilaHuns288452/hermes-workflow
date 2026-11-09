---
name: blender-automation
description: "Use when driving Blender from Hermes: setup and scripting."
---

# Blender Automation (Hermes)

Complements the hub skill `blender-mcp` — load it for GLTF export workflows, material-export survival tables, gltf-transform optimization, and asset integrations (PolyHaven/Sketchfab/Rodin). This skill covers the local setup, same-session scripting, and visual verification loop; it does not duplicate that depth.

## Standing Rules

- **Verify geometry with evidence before reporting done.** Scripted geometry silently comes out inverted, mis-scaled, or smooth-shaded (smooth shading makes faceted objects read domed/rounded). Gate: run `bpy.ops.object.shade_flat()` on joined/primitive meshes, then verify through the ladder below. One extra iteration is normal; shipping an hourglass instead of a diamond is not.
- **Native MCP tools load only in a NEW session.** `hermes mcp add` saves the server config, but the tool catalog is discovered at session start. Same-session work goes through the raw socket protocol (see below) — identical commands, no waiting.
- **Read errors before guessing.** The addon returns the full Python traceback in its error response; a single failed call almost always names the exact API change or typo.

## Current Setup (this machine)

- Blender 5.2.1 LTS at `~/.local/bin/blender` (symlink into `~/Downloads/blender-5.2.1-linux-x64/`).
- MCP addon installed as `~/.config/blender/5.2/scripts/addons/blender_mcp_addon.py` (legacy `scripts/addons` dir works on 5.2), enabled persistently — it auto-starts the socket server on `localhost:9876` at every Blender launch.
- Hermes MCP registered: `blender` = `~/.hermes/bin/uvx blender-mcp` (31 tools). Register with `yes Y | hermes mcp add blender --command ~/.hermes/bin/uvx --args blender-mcp` — pipe `yes Y |` or the interactive tools-enable prompt cancels the add.

## Health Check (Always First)

1. `ss -tlnp | grep 9876` — is the socket server listening?
2. Scene info call + `execute_code: print("ok")` — protocol and Python both work.
3. Viewport screenshot — capture path works.

If 9876 is dead, relaunch Blender with the server-start expression in [references/socket-protocol.md](references/socket-protocol.md).

## Same-Session Scripting (MCP tools not loaded)

Talk to the addon directly over TCP 9876 — command names, request/response shapes, a ready `mcp_call()` helper, and Blender 5.x API changes are in [references/socket-protocol.md](references/socket-protocol.md).

## Verification Ladder (cheap → expensive; stop when the question is answered)

Vision is ONE signal, not truth — it misses interiors hidden behind a detached panel, misreads small holes as raised bumps, and calls gizmos/cursors "stray geometry". Layer the evidence:

1. **Numeric** (execute_code): world-space bounding boxes, face counts, dimensions vs. spec. A face-count jump proves a boolean ran; the world bbox proves arrays/grids land where intended. Imported assemblies (SketchUp/GLB) often carry stray duplicate components thousands of units from the model — check world coordinates against the model bbox before treating a second "assembly" as a real in-frame element.
2. **Ray-cast probes**: `scene.ray_cast` from outside each face inward proves openness and what a ray actually hits. Cast AFTER `bpy.context.view_layer.update()` with a fresh `evaluated_depsgraph_get()`, in a separate call from the mutation — same-script casts return pre-mutation hits. Hit semantics: a miss (`None`) means the ray ran UNOBSTRUCTED to its full distance — when probing line of sight into an open tray or cavity, count "first hit = subject OR no hit" as visible and only "first hit = other object" as occluded; counting `None` as occlusion inverts the ranking of every candidate camera pose.
3. **Pixel-stat scans** (agent-side PIL/numpy on the saved PNG): color-fraction per named region ("blue pixels in the cavity region = tank present").
4. **Projected-pixel sampling**: `bpy_extras.object_utils.world_to_camera_view` maps 3D feature points to pixel coords; sample the render at exactly those points. This is the arbiter when vision and geometry disagree about position or shade.
5. **Vision audit**: specific YES/NO checklist questions beat open-ended ones. When it contradicts layers 1–4, re-ask with a marked-up image (draw rings at projected coordinates, ask if the rings land on the features). Render-look claims ("the holes read as holes") legitimately end here: iterate geometry until pixel evidence (e.g. dark fraction inside hole bores) confirms, then let vision confirm.

Adjudicating review feedback: compressed proxies and contact sheets misread extreme macros (a subject filling ~70% of frame reads as "background panel, subject missing") and still-vision hallucinates small specifics (droplets, accessories, mirrored labels). Before re-rendering anything a review flags, confirm the claim against FULL-RES stills plus layers 1–2 evidence; re-render only what survives that check.

## Camera/Shot Visibility Gate (before any long render)

Bbox-in-frame framing QA passes on shots that render BLANK: the subject's bbox projects into the frame while the camera sits inside or behind shell geometry and every pixel is the occluder. Blank signature: single-digit unique-color count / near-zero pixel std. Gate every shot before committing to a full animation render:

1. Render start/mid/end stills for every shot first (33 stills for an 11-shot film cost minutes; a full render costs hours).
2. Assert pixel content per still (e.g. ≥200 unique colors, std > 5). Pixel stats are the arbiter for blankness — vision and bbox checks both miss it.
3. `scene.ray_cast` from the camera position toward the shot's target: the first hit must be the intended subject. A different first hit names the occluder.
4. Detail shots of a feature on an enclosure face: approach from outside the face the feature sits on — a camera path crossing the shell renders the shell.

Iterate on stills until every shot passes, then run the full render once.

If the subject is enclosed and NO candidate pose sees it (grid-probe poses around the subject all fail), stop hunting for the impossible: pick the best-looking candidate that shows the nearest honest story element (e.g. the drain spout above a hidden collector) and align the narration/label to what is actually on screen. A visible story that matches its caption beats a perfect caption over a blank frame.

## Scripted Multi-Shot Film Pipeline (per-shot cameras, marker-bound cuts)

- **Build and render are different modes.** A `build` step constructs cameras/targets/lights from a shot table and re-keys every camera from its constants; `render` just walks frames and writes PNGs using the animation STORED in the blend. Never run build against a patched scene — it silently reverts camera fixes. Patch a camera by setting `obj.location` + `keyframe_insert('location', frame=...)` at the EXISTING key frames (updates in place), then save the blend.
- Timeline markers bind cameras per shot, so render output picks up a re-keyed camera with no render-code changes.
- **Selective re-render:** frame loops skip existing files — delete only the frame ranges to redo, run ONE pass over the enclosing range, and it fills just the gaps. A full re-render is almost never needed.
- Motion aliasing: a rotating multi-blade part needs per-frame rotation well below its blade-symmetry period (6 blades at 60°/frame reads static at 30fps; ~8°/frame reads as a clean slow spin). Set the rotation curve to LINEAR interpolation or the speed eases in and out.

For renders (Cycles GPU, lighting, AgX emission handling, making perforations read as holes), see [references/studio-render.md](references/studio-render.md).

Switch viewport shading to MATERIAL when verifying transmissive/emissive materials — solid shading shows none of it. For a final deliverable, prefer an actual Cycles render over viewport screenshots.
