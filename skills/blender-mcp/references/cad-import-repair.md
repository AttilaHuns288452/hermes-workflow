# Client CAD / SketchUp → Blender import audit & repair

Use when a client's SketchUp model (or other CAD assembly export) must become a clean, animatable Blender scene. The semantic ground truth is lost in the binary CAD file's converter output — recover it from the conversion metadata before doing look-dev.

## Pipeline

1. Extract the source file's own ground truth FIRST. A `.skp` is a zip container: unzip it — inside are the raw geometry JSON (world-space vertices in mm + per-instance placement transforms), the original texture images (often the 'lost' ones — PCB silkscreens, board photos, brushed-metal maps), and preview thumbnails. This data is the exact source frame: the GLB/JSON from any converter can be checked against it mesh-by-mesh. If only a GLB exists, convert SKP → GLB **plus a metadata JSON** (mesh index, SKP material table with colors/alpha, layer names, component names) with a dedicated converter (e.g. OpenSKP CLI). Keep BOTH artifacts: the GLB is geometry + vertex-color-encoded names; the JSON is the only record of semantic names, exact colors, and transparency.
2. Import the GLB into Blender and audit BEFORE editing: mesh/vert counts, material count, named components (real part names like `DHT11`, `1 Channel - Relay Module` are ground truth for scale AND for later callout labels), 3D text labels (they survive as mesh geometry; confirm via mesh names containing label words like `VIN`, `GND`), and layer names.
3. Repair ladder in this order (each step assumes the previous): axis/units → stray parking → material names → transparency → hierarchy → PBR baseline → save.
4. Verify deterministically, render 2–3 test frames, write the conversion report.

## Axis and units (do first — everything else assumes them)

- CAD imports may be Y-up while Blender is Z-up. A camera with `to_track_quat('-Z','Y')` renders Y-up data looking upright, which MASKS the error — bbox math (tallest extent on Y, thin Z) contradicts what renders show. Settle the axis from bbox extents of named assemblies, then rotate every mesh `Matrix.Rotation(radians(90),4,'X') @ matrix_world` and re-base: device bbox min z → 0, x/y centered at origin.
- Scale: never trust the unit setting. Measure real named components against their real-world specs (80mm fan ≈ 0.08m, 40mm Peltier, DHT11 ≈ 1.2cm) and apply a uniform factor if off.

## Material name restore (color-match)

Converter material names are generic (`Material_N`), but mesh names encode each part's face color as trailing `_R_G_B` tokens. Match those RGB triples against the source material table in the metadata JSON to restore semantic names — colors match nearly 1:1 and the recovery rate is high (188/190 on one real model). Semantic names drive the PBR baseline and later callouts. Watch the Blender-side suffix trap: GLB import creates suffixed copies for duplicate material names (`Material_79.001`), so a texture wire-up against the bare name attaches to an unused copy and renders flat — re-link by name prefix and verify the textured meshes actually reference the material.

## Transparency

Alpha survives only in `baseColorFactor[3]`; `alphaMode` is never set, so every material imports opaque. Restore from the source material table: set Principled `Alpha` and the blend mode (`BLEND` for glass, `HASHED`/blend for frosted). Split shared materials first if only one of the sharing meshes should be transparent.

## Hierarchy

Import flattens everything to root meshes named `mesh_N_ROOT__ComponentName__Sub_Layer0_R_G_B`. Rebuild per-component collections by parsing the component-name segment, so parts stay separately animatable.

## Strays and parked parts

CAD assemblies carry parked or duplicated subassemblies (spare fan/Peltier/heatsink sets floating meters away from the device). Detect via bbox centers far outside the device bbox; set `hide_render` for hero shots but SHOW them once in an overview audit render, and ask the user before deleting — deletion is theirs to approve.

## PBR baseline rebuild

Assign by name/color category: casing → plastic (rough ~0.38, light coat); extrusions/heatsinks/screws → metal (metallic ~0.32); screens/glass covers → glass (rough 0.05 + transmission); status LEDs → emissive (raise emission strength until dots visibly glow at render exposure). Flat Principled defaults are enough at the report stage; hero-grade shading comes later.

## Deterministic verification

- **Source-parity gate** (when the converted model must be a faithful 1:1): mesh-count parity source vs converted (every source mesh present — count them), per-mesh bbox-center agreement against the source instance placements, and real-part scale checks. Report the numbers; an eyeball render is not the answer.
- Embedded preview thumbnails inside the SKP can be stale (an earlier design iteration). The file's geometry is authoritative: render the file, and report the thumbnail discrepancy instead of conforming the model to a thumbnail.
- Project the device bbox corners through `bpy_extras.object_utils.world_to_camera_view` per render; assert all UVs inside [0.02, 0.98] and report the fill fraction.
- PIL ink% + bbox fraction on the saved PNG proves content actually painted.
- When aiming a close-up by bbox-center filters, PRINT the matched object names before rendering — interior parts (Peltier plates, fan frames) share coordinate bands with the intended face; filter on the face-plane coordinate (the display sits at the housing's front-face x) and verify the matched set is the expected component band.
- Vision analysis is a smoke test only: settle orientation/part-presence questions with bbox math and matched-name prints.

## Conversion-stage deliverable

The client gets: a short conversion report (**what survived / what broke / what was fixed / what was rebuilt or approximated / known gaps with exactly what input is needed**), 2–3 test renders (full-frame hero showing the whole device on ground contact, one component close-up, one scene overview showing any strays), and the kept .blend + re-runnable scripts. Never silently guess a lost texture, logo, or label — ask for the source asset and say what was substituted meanwhile. Wait for the client's OK before building the full production.