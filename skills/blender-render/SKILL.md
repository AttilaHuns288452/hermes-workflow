---
name: blender-render
description: "Render existing Blender scenes to still images or frame sequences with preview checks and verified outputs."
---

> Source: SamuelAsherRivello/ai-skills-blender @ 54b4f26 (shared skills/)

# blender-render

## Inputs and scope

Accept existing scene, camera, output path/format/resolution; default to existing usable settings and bounded preview. Also accept optional setting, action/pose, composition, camera, lighting/mood, palette, user references, output specifications and technical constraints when relevant. State assumptions; ask only when a missing answer materially changes the work. A textual style works without reference images. The shared render-style gallery is optional: use an explicitly supplied path or known checkout, inspect a chosen PNG before drawing conclusions, and never fetch missing images automatically.

Use the separately configured official Blender Lab MCP connection. Discover its tools and confirm read-only scene access before mutations; report a connection blocker instead of switching servers. Preserve unrelated objects and settings, scope new content by named collection/run, and checkpoint before destructive edits. Repeated scripts must replace only owned output or create a separate named run. Do not start paid services without authorization.

Use the existing MCP connection whenever it can perform the operation. On Windows, auxiliary execution MUST remain windowless, including brief flashes, during setup, diagnostics, rendering, export, and verification. Before launching, establish suppression for the complete process chain, including client-owned and dependency-owned startup. Use explicit no-console creation (such as subprocess.CREATE_NO_WINDOW) and captured output for reviewed console-only commands. If any required boundary is unknown or unsupported, do not launch: report BLOCKED with the reason and next action, and continue independent safe work. Never retry through a visible terminal, toggle Blender's system console, or weaken suppression. An absolute executable path, cmd /c, Blender --background, or Start-Process -WindowStyle Hidden alone is not proof of no flashes. Keep exit status, bounded timeouts, useful diagnostics without secrets, and cleanup of owned descendants. Do not hide, minimize, restore, focus, or close the existing Blender editor to suppress auxiliary windows. Preserve fresh editor-readiness checks before screenshots.

## Parallel visual target and feedback

At the start of a new top-level 3D task, launch one subagent using `blender-create-visual-target-2d` with the exact prompt, constraints, supplied references/current-scene preview, unchanged features, task ID and an exclusive target directory. Continue Blender inspection and construction immediately while it prepares the prompt-specific target. Nested skills reuse the same pending/completed worker; do not launch one per skill. The target worker must not mutate Blender or recursively delegate.

When it returns, inspect the target and compare a genuine current preview, prioritize visible gaps, apply in-scope corrections and inspect again against the same target version. Use the requested iteration budget, otherwise up to two focused correction passes; report remaining gaps. Preserve render/export/audit-only scope and existing-asset identity. Follow the target skill's parallel-feedback reference when available. If delegation or image generation is unavailable, use parent-side preparation or a supplied target, disclose any prompt-only fallback, and never claim an unperformed comparison. Pure setup checks and explicit user opt-outs bypass this default.

## Workflow

1. Verify readiness and identify still/sequence output requirements and source scene.
2. Preflight camera, visibility, missing assets, frame range and output destination.
3. Select a supported render engine/device and report any fallback.
4. Set a modest preview resolution/sample budget; cap requested frame batches.
5. Render the preview without overwriting unrelated outputs.
6. Inspect composition, noise, materials, transparency and exposure against the requested style and any supplied references. Identify the largest visible mismatch and route it to modeling, materials, or lighting before increasing render quality. Samples cannot repair missing construction depth, poor framing, or a mismatched visual treatment.
7. Record final settings, version, source path and expected files in a run manifest.
8. Render final output; resume only verified frames from the same source/settings and use a fresh run if settings changed.
9. Verify dimensions, format, alpha and complete frame coverage; inspect representative final images.
10. Deliver source, output paths, settings, evidence and any unverified quality/engine assumptions. For requested iteration studies, retain each attempt, select by inspected brief compliance rather than recency, and distinguish visual shortcomings from file-validation failures. Record build time separately from render time; treat a stated soft timing target as a trade-off, not permission to weaken the brief silently.

## Artifact triage

When a rendered frame shows an unexplained artifact (dark slab, smear, haze, "floating" element), identify the responsible object before changing lighting, materials, or composition. Cast a ray from the active camera through the suspect pixel (`scene.ray_cast` with a direction built from the camera matrix and angle_x/angle_y) and read the hit object's name; then cast rays from the hit surface toward each light to separate interposed geometry from shading. Vision analysis alone misattributes artifacts — translucent overlay planes read as "composited bars", shadows read as floating geometry — while the ray hit names the object definitively.

Before blaming the scene for streak bars, haze bands, or translucent slabs, check the compositor: in Blender 5.x compositor node options (Glare `Type`/`Threshold`/`Size`/`Strength` and similar) are input **sockets**, and assigning the old property names silently no-ops while the node keeps its default (Glare defaults to `Streaks`, painting streak bars across every frame). Set `node.inputs['Name'].default_value = ...` and read the value back to confirm it took; never wrap the assignment in try/except and move on — the swallowed failure ships a corrupted film.

Text and printed ink washing pale is a lighting/view-transform interaction, not a broken texture: under a bright scene an AgX view transform compresses even 0.1-albedo ink to mid-gray, and semi-gloss type (roughness below ~0.5) mirrors nearby lights as a sheen across the glyphs. Render printed ink as near-black matte albedo (or emission-driven flat color when the ink must hold exact contrast), and verify legibility with per-pixel MINIMUMS over the glyph band — region means hide thin dark strokes between sampling cells, and vision prose under-reads low-contrast type.

When stray lines, specks, or slabs appear that no lighting or material change explains, scan every mesh object's world-space bounding box first: one degenerate conversion mesh (a spike spanning meters) accounts for many unrelated-looking artifacts at once, and a single bbox pass names every offender before any render is spent.

A vision model's frame description is a hypothesis: it can carry content over from earlier images in the conversation (labels, text, prior frames) that is not in the frame being judged. Before redesigning around a vision claim, verify it with a deterministic probe — pixel-color counts, the exact frame pulled from the PNG sequence (no seek ambiguity), or ray_cast geometry. Vision calls can contradict each other on the same frame, and single vision grounding claims ("the object floats") are unreliable for light subjects on light surfaces — settle contact with world_to_camera_view projections of the contact points. But projections prove only what they measure: contact can be perfect while the model itself lacks its outer body and reads floating and wrongly shaped from every camera. When the USER (not just a vision pass) reports floating or a wrong angle, probe model completeness first (does the subject have a closed body, or is it an assembly shell over internal supports?) and compare against a known-good reference render before defending the geometry; the user's repeated visual verdict outranks passing contact numbers. Once the owning fix is in, re-render only the affected frame range (`blender -s N -e M -a`) and confirm with test frames before the batch.

A delegated reviewer's verdict is a hypothesis the same way: it grades against whatever spec it was handed, so extract the review brief from the current build source (script values, storyboard as written) rather than remembered figures, and triage every finding against a deterministic probe before fixing anything.

Before launching a long batch render, confirm no other render of the same scene is alive (`ps aux | grep '[b]lender'`): killing a background shell/wrapper pid does not kill the render child it spawned, and several orphaned renders sharing one GPU look exactly like a per-frame performance regression. Kill strays by explicit PIDs from the process listing, never by a name-pattern pkill whose pattern also appears in your own command line — the launching shell contains that text and kills itself.

## Execution notes

Use [scripts/verify_outputs.py](scripts/verify_outputs.py) for PNG output manifests. It verifies structure and requested dimensions/channels, not artistic quality or alpha coverage. Run with --help. Actual image inspection remains required. Save the source before recording its path.

Before a long batch render with camera moves, run a layout gate: sample each text/label object across its full visibility window (respect hide_render keyframes — in Blender 5.x read curves through action.layers[].strips[].channelbags[].fcurves, the legacy action.fcurves is removed), project its bounding-box corners with `bpy_extras.object_utils.world_to_camera_view`, and assert every projection stays inside a safe margin. Checked endpoints miss mid-move drift — a label that clips during a push-in looks fine at the one keyframe you inspected. Give every overlay label an explicit staggered visibility window; a default end-of-sequence window accumulates every label on screen at once.

## Delivery and evidence

Provide editable source and requested outputs, relevant settings/seed/version, observed checks and remaining limitations. Inspect actual images for visual claims. File existence alone is not proof of quality. Prefer previews before expensive batches; do not overwrite unrelated files. Report unavailable downstream checks as unverified. QA the exact file just produced: checksum or mtime-check the artifact under review before auditing it, and keep the deliverable-copy step inside the compose script — stale copies in delivery directories lead audits to report defects that are already fixed. The finish bar for delivered films is visual, not procedural: professional and clean, no blur or artifacts, correct angles with coherent motion direction, cinematic pacing; when asked to loop until it looks good, iterate full-res frame passes on the delivered file — each finding triaged by a deterministic probe — until a complete pass shows no real defects.

## Editor screenshot readiness

Before capturing genuine editor evidence, verify Blender has an open, visible, non-minimized editor window; maximization is unnecessary. Minimized full-window and area captures have returned black on the tested workstation. If minimized, report the solution: restore Blender from the taskbar. Capture permission is already included in requested Blender work; this is a technical readiness issue. Inspect captured pixels and never label a failed capture, prior screenshot, or clean render as fresh editor evidence. Do not change the user's window state without authorization.

Before **every** Blender editor/window/area screenshot call, freshly check that the relevant Blender process has a visible, non-minimized editor window; do not reuse an earlier setup result. If Blender is closed, prompt the user to open it. If minimized or hidden, prompt the user to restore/show it (maximization is unnecessary). If inspection is unavailable, report the unknown state and ask the user to make the editor visible. Pause screenshot attempts until the issue is resolved, then repeat the window-state check before capturing. Do not automatically restore/focus the window. This prerequisite applies to editor screenshots, not saved render output. A passing check still requires inspection of the captured pixels; if the image is black or stale, report the failure and prompt the user to restore/show the editor before a fresh check and retry.
