---
name: product-3d-prototype
description: "Use when building 3D product prototypes or part renders."
---

# Product 3D Prototype

Build labeled 3D product-prototype models from reference images: hybrid AI-generated detail (Tripo/scan GLBs) plus handcrafted Blender geometry, studio renders, labeled part diagrams. Trigger territory: user provides product sketches/renders and wants a 3D model, hardware prototype, part views with labels, or AI-generation + hand-modeling combined.

## Workflow

1. **Read every reference image with vision first.** Extract parts, proportions, colors, callouts. Where images conflict, pick values explicitly and say which source won.
2. **Define FRONT/BACK as a comment constant at script top** (`# front is -Y`); every placement derives from it. Sign flips put features on the wrong side.
3. **Handcraft the shell as ONE box** (user silhouette taste): single bevel, then cut pockets (vent recess, service bay, drawer cavity) with boolean cutters that overshoot the surface by ~1mm. Proof the shell with geometry (base cube = 8 verts), not vibes.
4. **Generate AI detail for dense interiors/organic parts only** (Tripo/scan GLBs); handcraft shells, silhouette, exact feature placement, and all labeled views. API + ingest cleanup: `references/tripo-api.md`.
5. **Install generated guts into the handcrafted cavity** with a scaled pivot rig (see pitfalls), then add handcrafted mounting hardware and a wire harness on top — the harness is what sells "installed" once generated detail is scaled down.
6. **Render clean frames per view** — front / inside-bay / back, optional drawer detail — then annotate in 2D: project 3D anchors to pixels with `bpy_extras.object_utils.world_to_camera_view`, draw navy chips + leader lines + ring dots in PIL. Never build 3D text labels.
7. **Verify:** ray_cast probes prove placement, a render from the actual viewing angle proves visibility, vision confirms the read (serialize vision calls), pixel checks confirm dots landed.

## User Preferences (standing)

- **Accumulate, never remove** ("do not remove what you created"): every model, variant, and deliverable stays in the .blend and on disk. Fix looks with per-view `hide_render` swaps (cover on/off, drawer open/flush, primitive stand-ins vs generated guts) so one file serves every shot.
- **Silhouette taste: exactly ONE box** — flush panels, no stepped modules, no proud lids. Flush inset panels read as features; proud ones read as second blocks. Shrink square plates to fit inside a rounded silhouette. Never name a region as a separate module in a callout — labels teach viewers to see blocks that are not there.
- **Hybrid division of labor:** AI generation = dense interior/organic detail; handcrafted Blender = shell, exact placement, labels. User explicitly directs this split.
- **Labeled set convention:** front / inside-bay / back views plus optional drawer-detail view; navy rounded chips, thin leader lines, ring-dot anchors.
- Deliverables as MEDIA files with the labeled set first, generated/raw renders second.

## Modeling Pitfalls (construction, placement, rendering)

- **Operator context drifts in long GUI-MCP sessions:** `primitive_cube_add(location=X)` + `transform_apply(scale=True)` can silently leave boxes at the origin (correct dims, wrong pos). Build boxes with bmesh (`create_cube` → `scale` → `translate`) — zero operators, immune. ALWAYS probe placed parts with `scene.ray_cast` from the camera toward the expected surface before rendering; a successful script print is not proof of placement.
- **bmesh 5.2:** `create_cone` exists, `create_cylinder` does NOT; `BMVert` has no `is_visible`. `delete(context='FACES')` on a single-face mesh deletes the whole mesh — build prisms as bottom-NGON extrusions, then delete target walls by plane-distance on `face.center` (normals are inward before recalc — never filter on `f.normal`).
- **Interior parts sealed in a solid primitive are invisible from every angle** even when correctly placed — cut a cavity (boolean pocket through the housing). Live hidden cutters (hide_render + hide_viewport) suffice for renders; apply only when the mesh must be edited further.
- **Boolean cutters must overshoot ~1mm past the final surface** — a flush cutter against a solidified/skinned wall cuts depth 0 and the feature silently vanishes.
- **Modifier-apply bakes the whole stack below it** — strip leftover modifiers after applying a boolean or walls double-thicken.
- **Array-modifier instances don't ray_cast or boolean** (evaluated-only) — apply the array before using an object as a cutter. Array offsets are LOCAL × object scale: bake scale first or offsets collapse.
- **Boolean timing:** a 49×42 cutter grid (~20.5k faces) with the EXACT solver takes 35–80s and completes; fall back to procedural bump only above ~120s.
- **Perforated grille holes vanish on same-color surfaces:** put a dark backing panel ~1.5cm behind the holes so they read as cutouts.
- **High-key washout on white products:** world strength ≤0.3, key 75–90W, `view_settings.look='AgX - Medium High Contrast'`, exposure ≈ −0.3. Plain AgX stays washed out.
- **Translucent tanks need saturated tint** (Base Color ~(0.50,0.72,0.90), Alpha 0.65) — near-white frost reads as empty plastic. Alpha-blend for visibility; full transmission vanishes against light backdrops in previews.
- **Fully metallic parts render dark in preview engines without env reflections** — use Metallic 0.2–0.3 + bright base when the preview is the deliverable.
- **Flat-lying boards are invisible from horizontal cameras** — mount key boards vertically face-out toward the viewing angle, or accept they won't read.
- **Rigging imported meshes under a pivot:** compute `matrix_parent_inverse` only AFTER `view_layer.update()` — a fresh pivot's `matrix_world` is identity and children land offset-scaled. Simpler and always right: parent plainly, then translate the pivot by (target − measured children bbox center).
- **Proportion fixes on mixed-origin scenes:** remap every mesh vertex through `matrix_world` (world coord → scaled coord → back through the inverse) and every curve bezier `co` plus handles through the same map. A uniform squash preserves pockets, clearances, and part relationships; round features distort ≤25% unnoticeably at product distance. Push label anchors and per-view part positions through the same map.
- **Name-filter traps:** generated names can carry leading spaces — `startswith('Rail')` misses `' Rail1'` and the part survives every purge, silently protruding later. Purge by case-insensitive substring and print the matched list before deleting.
- **Silhouette QA via vision is stochastic:** near-identical geometry flip-flops between "1 box" and "3 boxes" across runs, and label text biases the count. Back verdicts with geometry proofs (vertex count, bbox dims); re-verify once per real geometry change and stop — never iterate against a noisy oracle.
- **Label-dot QA without the vision API:** sample pixels at projected anchors (PIL) — white center + colored ring within ±16px = dot rendered. Parallel vision calls can race (duplicate-request errors); serialize them.
- **Per-view part states beat one compromise pose:** drawer open for its detail shot and flush elsewhere; hide every shell piece on the view path for cutaways or the cavity reads closed.
- **OpenGL viewport screenshots show the viewport camera, not the render camera** — render to PNG per angle and check the file.
- **Save every checkpoint; scripts must `open_mainfile` first** — building on the default startup scene then crashing loses everything unsaved; GUI-linked Blender can crash/empty mid-session and only the disk file survives.
- **GLTF export from a UI-session blend can fail armature validation on rigless scenes** — export via headless CLI. `export_apply=False` (baked array modifiers balloon files 50×); Draco last, never `gltf-transform optimize` (it simplifies geometry away).

## Annotated Diagrams (labels/callouts)

3D text labels in Blender are a trap (billboard drift, z-fight, occlusion). Fast path: render a CLEAN frame, project anchors with `world_to_camera_view`, draw chips/leaders/dots in PIL. Sort callout rows by anchor Y so leaders never cross.

## References

- `references/tripo-api.md` — Tripo v2 openapi recipe, input-image rules, GLB ingest shape, debris-cleanup ladder, and the dead ends not to retry.
