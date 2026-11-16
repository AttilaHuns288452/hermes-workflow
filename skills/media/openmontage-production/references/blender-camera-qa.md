# Blender camera QA and render iteration (source-model product films)

Use when a film is rendered from a source model (SketchUp import or prepared blend) with scripted per-shot cameras and a full-sequence render is expensive (hours).

## Loop order (cost discipline)

1. Build/repair scene + shot table first, then render start/mid/end stills per shot (~2-3s/frame EEVEE 1080p on NVIDIA offload; 33 stills ≈ 90s) BEFORE any full-length render.
2. Vision-check the stills against each shot's intended narration; fix cameras; repeat.
3. Full render only after every shot passes. Patching one shot later = re-render ONLY its frame range (`-s`/`-e`), never the film.

Pitfall: launching the full render before camera QA burns hours on frames that must be re-rendered anyway — the preview pass is 1% of the cost and catches everything the full render would.

## Camera visibility verification (never bounding boxes alone)

- A bbox-in-frame check PASSES for a blank wall close-up: the camera can sit centimeters from shell skin with the subject bbox technically inside the frustum. Verify actual pixels: unique RGB count (>200) and std dev (>5) per preview frame.
- Ray-cast grid (5x5) from the camera through points on the subject bbox with the evaluated depsgraph (`scene.ray_cast(dg, origin, dir, distance=...)`). Classify first hits as SUBJECT / OCCLUDER / CLEAR. `None` = the ray reached the point unobstructed = CLEAR sight INTO a hollow object (open tray interior) — not a failure; misclassifying clear rays as hits hides the best viewing angles.
- Blank-frame root-cause bisect: re-render the same pose with DOF off (unchanged = not DOF), then shift the camera ~10cm along the suspect axis. If content appears, the path grazes geometry — re-key the whole shot outside the shell.

## Enclosed subjects: reframe and re-narrate

If raycast probing and candidate renders agree the subject is visible from no pose (every ray hits shell), the subject is enclosed. Do not fight geometry or fake it: reframe to the nearest honest visible story (e.g. the drain spout feeding the hidden collector) and regenerate that shot's narration line to describe exactly what the frame shows. Per-shot narration-vs-frame agreement is the acceptance test.

## Blender 5.2 API gotchas

- `action.fcurves` is REMOVED. Update keys in place with `obj.keyframe_insert('location', frame=f)` (inserting at an existing frame replaces that key), or reach fcurves via `action.layers[].strips[].channelbags[].fcurves`.
- When rendering candidate poses from a script, `cam.animation_data_clear()` first — otherwise keyed values override your probe locations at frame evaluation.
- Check the render entry point before trusting scene fixes: a `build`-style mode REBUILDS cameras/markers from its constants and clobbers manual re-keys; a `render` mode that only does `scene.frame_set` uses the blend's stored animation. Most render scripts also resolve their output directory from the OPENED blend's location and skip existing frames — know where frames land before launching, and treat a missing frame directory as a silent full re-render trigger.

## Vision prompts that drive fixes

- Ask: "does the frame support narration X", "is the subject chain clipped by frame edges", "rate composition 1-10". The numeric rating plus one specific defect (clipped top edge, subject too small) gives a concrete fix.
- Standard framing fix after "clipped / too small": raise the aim target toward the subject cluster and pull the camera back ~12%; re-render 3 stills and re-ask. Two iterations typically reach 8/10.
- Still frames exaggerate render grain and flat-shaded materials; don't chase source-model fidelity limits in stills. Judge motion in the assembled video.
