# Blender 4.x/5.x API Pitfalls & Errors (encountered in practice)

## Operator signature changes (4.x → 5.x)

| Error | Cause | Fix |
|-------|-------|-----|
| `TypeError: keyword "name" unrecognized` on `primitive_*_add` | Primitive operators no longer take `name=` | Set it after creation: `bpy.context.object.name = "Foo"` |
| `TypeError: keyword "type" unrecognized` on `bpy.ops.object.convert` | Kwarg renamed in 5.x | `bpy.ops.object.convert(target="MESH")` (try `type=` as fallback on older builds) |
| `extrude_face_region: keyword "faces" is invalid` | bmesh op signature | `bmesh.ops.extrude_face_region(bm, geom=inner)` — and it KEEPS the source faces |
| `AttributeError: 'Scene' object has no attribute 'view_layer'` | Wrong namespace | `bpy.context.view_layer.update()` |
| `ModuleNotFoundError: PIL` inside Blender | Blender's bundled Python lacks PIL | Do projection inside Blender (`world_to_camera_view`), image work in host Python; pass JSON between the two |

## bmesh open-a-box trap

`bmesh.ops.inset_region` + `bmesh.ops.extrude_face_region` + deleting the inset faces leaves a rim face capping the plane — the box stays visually closed while face counts look plausible. The deterministic way to make an open enclosure:

1. bmesh-delete the front face (`bmesh.ops.delete(..., context="FACES")`).
2. SOLIDIFY modifier for wall thickness.
3. BEVEL modifier for rounded edges (after solidify).
4. Prove it: bmesh face count at the front plane in WORLD coordinates (local-space comparisons silently fail on located objects) + `scene.ray_cast` through the opening.

Also: `mesh.inset`/`mesh.extrude_region_move` operators depend on edit-mode selection state that silently resets — prefer bmesh delete + modifiers, which have no selection dependency.

## Boolean gotchas

| Symptom | Cause | Fix |
|---------|-------|-----|
| Boolean has no visible effect | Cutter sits entirely inside the solid — it carves a hidden void | Cutter must pierce fully through one face |
| `Info: Applied modifier was not first` | Bevel/Solidify before the Boolean in the stack | Boolean first, then Solidify, then Bevel; apply in order |
| Perforation holes land outside the face | Array offsets on a rotated object are in LOCAL axes | `use_constant_offset=True` with offsets in the object's local frame, or create the cutter un-rotated |

## Depsgraph / ray-cast staleness

`scene.ray_cast` and `world_to_camera_view` evaluate the last-updated depsgraph. After ANY transform, call `bpy.context.view_layer.update()` and grab a fresh `bpy.context.evaluated_depsgraph_get()` — ideally do transforms in one socket call and ray-tests/projections in the next. A ray test that hits a just-deleted object or reports a pre-move position is always stale-state, not a geometry bug. For label anchors, read `object.matrix_world @ bound_box` centers after the move; hardcoded pixel/anchor numbers break on every recomposition.

## Lights & color management

| Symptom | Cause | Fix |
|---------|-------|-----|
| Cavity renders pure white | Stray default 1000 W point lamp or interior light aimed at the ceiling | Inventory `type=='LIGHT'` objects + world Background strength first; one area light aimed at the back wall; world 0.10–0.20; exposure −0.9 to −1.2 |
| LED renders white instead of colored | Emission strength 100+ clips under AgX | Emission strength ~25 with saturated emission color |
| Parts washed out in white-on-white interior | Low material saturation + AgX desaturation | Saturate base colors at the material level (deep green PCB, strong blue relay, saturated wire colors) |

## Rendering / state management

| Symptom | Cause | Fix |
|-------|-------|-----|
| Annotation dots/lines appear in a "clean" render | hide_render flags lost across save/reload of state variants | Re-set hide_render on every annotation object before each save and before each render |
| Part "missing" from render but present in file | hide_render or hide_viewport left True from another view's state | Dump `{name: hide_render}` for all objects before rendering |
| DOF blurs the moved part in a service view | Camera DOF left on from the hero shot | `camera.data.dof.use_dof = False` for service/exploded views |
| GPU render fails / falls back to CPU | OPTIX/CUDA device not enabled in preferences | `prefs.compute_device_type = "OPTIX"; prefs.get_devices(); [setattr(d,'use',d.type!='CPU') for d in prefs.devices]`; `scene.cycles.device = "GPU"` |
| Save fails `Cannot open file ... for writing` | Target directory missing | `mkdir -p` from the host before `save_as_mainfile` |

## Verification patterns (use before claiming any render)

- Open-cavity proof: ray-cast from outside through the expected opening; the first hit must be an interior part, not the shell.
- Hole-grid proof: bmesh count of small-area faces at the panel plane (world space), then project hole centers with `world_to_camera_view` and sample those pixels in the saved PNG.
- Part-visibility proof: ray-cast camera → part-center per part; first hit must be the part itself (else occluded).
- Exposure proof: blown-white fraction + per-color pixel-cluster counts in the cavity region of the saved PNG.
- When vision contradicts geometry data, sample the projected coordinates — projection errors are usually the label overlay, not the model.
