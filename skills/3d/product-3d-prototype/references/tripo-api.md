# Tripo API & Scan-GLB Ingest

## API recipe (v2 openapi, base `https://api.tripo3d.ai/v2/openapi`, Bearer key)

1. **Upload:** `POST /upload`, multipart `-F file=@img.jpeg` → `{"data":{"image_token":"..."}}`. (`POST /upload/staging` does not exist.)
2. **Task:** `POST /task`, JSON body:
   ```json
   {"type":"multiview_to_model",
    "files":[{"type":"jpeg","file_token":"<front>"}, {},
             {"type":"jpeg","file_token":"<back>"}, {"type":"jpeg","file_token":"<right>"}],
    "model_version":"v3.1-20260211", "geometry_quality":"detailed"}
   ```
   - `files` = exactly 4 slots in [front, left, back, right] order; skip a view with `{}`; front required; use ≥2 images.
   - `model_version`: `v3.1-20260211` (H3) or `v2.5-20250123` (H2 default). ~40 credits/task, frozen at submission; check `GET /user/balance` first.
   - Shapes that do NOT work (9404/1004/HTTP 400): `file:{multiview:[tokens]}`, `multiview_images:[...]`, bare token lists, `files` without the 4-slot form.
3. **Poll:** `GET /task/{id}` every ~15s (~1–2 min). On `success`, `data.output.pbr_model` is a signed URL with ~15 min life — download immediately.

## Input images

Strip annotation overlays (label chips, leader lines, anchor dots) BEFORE generation. The model reconstructs them as 3D debris (floating bars + tether lines); once attached to the shell, no island filter fully removes them. Root-cause fix is upstream, at the image.

## GLB shape

Parts mode: a headless `import_scene.gltf` yields hundreds of separate mesh objects (a GUI import may show one mesh with debris as inner islands). Object origins sit at zero with geometry in world coords — measure with `bound_box @ matrix_world`, never `location`.

## Debris cleanup ladder (headless Blender only)

Run in headless CLI — an island BFS over ~1M verts hangs >10 min and wedges the MCP socket. Always on an opened file (`open_mainfile`).

1. Select each mesh, `bpy.ops.mesh.separate(type='LOOSE')` (C-speed), then measure each island's bbox via `evaluated_get(depsgraph).bound_box @ matrix_world`.
2. Kill islands with bbox max/min dim ratio > 8 (tubes, flat bars, leader lines).
3. Kill islands whose bbox center is > 0.30 from the median center of the top-12 largest islands.
4. Kill islands < 40 verts (glyph fragments).

NEVER prune seeded on the single largest island: generated enclosures split into several large islands and single-seed hulls amputate the shell. Backup the GLB before any face-level cut and solo-vision-render after.

## Dead ends (do not retry)

- **Attached-rod removal by local filters:** a rod's surface verts and a shell EDGE's verts are locally identical (both thin in two neighborhood axes; a rod near a wall sees the wall too). KD-tree span tests delete shell borders; fixed-bbox face cuts amputate shells. Only interactive sculpting or upstream image cleanup removes attached debris.
- Whole-island bbox elongation misses diagonal/curved strands (ratio < 8).

## Round-trip

Headless export→import preserves object names; a root-empty exported GLB re-imports as the same named empty, so the top-level import set recovers the hierarchy.