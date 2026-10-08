---
name: blender-mcp
description: "Blender MCP expert for scene inspection, Python scripting, GLTF export, and material/animation extraction. Activate when: (1) using Blender MCP tools (get_scene_info, execute_python, screenshot, etc.), (2) writing Blender Python scripts for extraction or manipulation, (3) exporting scenes to GLTF/GLB for web (Three.js, R3F), (4) debugging material or texture export losses, (5) optimizing GLB files with gltf-transform, (6) using asset integrations (PolyHaven, Sketchfab, Hyper3D Rodin, Hunyuan3D). Covers critical export gotchas, material mapping survival, texture optimization pipeline, headless CLI patterns, and known failure modes."
---

# Blender MCP

## Tool Selection

Use **structured MCP tools** (`get_scene_info`, `screenshot`) for quick inspection.

Use **`execute_python`** for anything non-trivial: hierarchy traversal, material extraction, animation baking, bulk operations. It gives full `bpy` API access and avoids tool schema limitations.

Use **headless CLI** for GLTF exports — the MCP server times out on export operations.

## Health Check (Always First)

1. `get_scene_info` — verify connection (default port 9876)
2. `execute_python` with `print("ok")` — verify Python works
3. `screenshot` — verify viewport capture works

If MCP is unresponsive, check that the Blender MCP addon is enabled and the socket server is running.

## Complete Export Workflow

This is the end-to-end linear narrative. Follow these steps in order. Do not skip steps.

### Step 1: Health Check

Confirm MCP is alive before touching anything else:

```bash
# In MCP tool call:
get_scene_info
execute_python: print("ok")
screenshot
```

If any step fails, stop and fix MCP connectivity first. See [Known Errors](#known-errors--workarounds).

### Step 2: Inspect Scene

Run the full hierarchy extraction to understand what you're working with:

```python
import bpy, json

def extract_hierarchy(obj, depth=0):
    data = {
        "name": obj.name,
        "type": obj.type,
        "location": list(obj.location),
        "rotation": list(obj.rotation_euler),
        "scale": list(obj.scale),
        "visible": not obj.hide_viewport,
        "children": [],
    }
    if obj.type == 'MESH' and obj.data:
        data["vertices"] = len(obj.data.vertices)
        data["faces"] = len(obj.data.polygons)
        data["materials"] = [slot.material.name for slot in obj.material_slots if slot.material]
    if obj.type == 'LIGHT':
        data["light_type"] = obj.data.type
        data["energy"] = obj.data.energy
        data["color"] = list(obj.data.color)
    for mod in obj.modifiers:
        if mod.type == 'ARRAY':
            data.setdefault("modifiers", []).append({
                "type": "ARRAY",
                "count": mod.count,
                "offset_object": mod.offset_object.name if mod.offset_object else None,
            })
    for child in obj.children:
        data["children"].append(extract_hierarchy(child, depth + 1))
    return data

scene_data = {
    "name": bpy.context.scene.name,
    "fps": bpy.context.scene.render.fps,
    "frame_start": bpy.context.scene.frame_start,
    "frame_end": bpy.context.scene.frame_end,
    "objects": [],
}
for obj in bpy.context.scene.objects:
    if obj.parent is None:
        scene_data["objects"].append(extract_hierarchy(obj))

print(json.dumps(scene_data, indent=2))
```

Look for:
- Array modifiers (will balloon file size if baked — must replicate at runtime)
- Objects with many vertices (risk of slow export or large GLB)
- Hidden objects you may or may not want to export
- Missing materials (empty `material_slots`)

### Step 3: Verify Materials

Run the material extraction to catch export-lossy setups before committing to an export:

```python
import bpy, json

def extract_materials():
    materials = []
    for mat in bpy.data.materials:
        if not mat.use_nodes:
            continue
        info = {"name": mat.name, "nodes": [], "warnings": []}
        has_principled = False
        for node in mat.node_tree.nodes:
            node_data = {"type": node.type, "name": node.name}
            if node.type == 'BSDF_PRINCIPLED':
                has_principled = True
                for inp in node.inputs:
                    if inp.is_linked:
                        node_data[inp.name] = "linked"
                    elif hasattr(inp, 'default_value'):
                        val = inp.default_value
                        try:
                            node_data[inp.name] = list(val)
                        except TypeError:
                            node_data[inp.name] = float(val)
            if node.type == 'TEX_IMAGE' and node.image:
                node_data["image"] = node.image.filepath
                node_data["size"] = [node.image.size[0], node.image.size[1]]
                if node.image.size[0] > 2048:
                    info["warnings"].append(f"Large texture: {node.image.filepath} ({node.image.size[0]}x{node.image.size[1]})")
            if node.type in ('TEX_NOISE', 'TEX_VORONOI', 'TEX_WAVE', 'TEX_MUSGRAVE'):
                info["warnings"].append(f"Procedural texture node '{node.name}' ({node.type}) will be LOST on GLTF export")
            if node.type == 'VALTORGB':  # Color Ramp
                info["warnings"].append(f"Color Ramp '{node.name}' remapping will be LOST on GLTF export")
        if not has_principled:
            info["warnings"].append("No Principled BSDF found — export result unpredictable")
        info["nodes"].append(node_data)
        materials.append(info)
    return materials

result = extract_materials()
for mat in result:
    if mat["warnings"]:
        print(f"WARN [{mat['name']}]: {'; '.join(mat['warnings'])}")
print(json.dumps(result, indent=2))
```

Review all warnings before proceeding. Decide: bake procedural textures now, or patch materials at runtime after export.

### Step 4: Export via Headless CLI

The MCP server cannot handle GLTF exports (timeout). Always use headless CLI:

```bash
# Use 'blender' if it's on PATH, otherwise use the platform-specific path:
#   macOS:   /Applications/Blender.app/Contents/MacOS/Blender
#   Windows: "C:\Program Files\Blender Foundation\Blender 4.x\blender.exe"
#   Linux:   /usr/bin/blender
blender \
  --background "/path/to/scene.blend" \
  --python-expr "
import bpy, os
export_path = '/path/to/output.glb'
os.makedirs(os.path.dirname(os.path.abspath(export_path)), exist_ok=True)
bpy.ops.export_scene.gltf(
    filepath=export_path,
    export_format='GLB',
    export_apply=False,
    export_animations=True,
    export_nla_strips=True,
    export_cameras=True,
    export_lights=False,
    export_draco_mesh_compression_enable=False,
)
size_mb = os.path.getsize(export_path) / 1024 / 1024
print(f'Export complete: {export_path} ({size_mb:.1f} MB)')
"
```

**Critical flags:**
- `export_apply=False` — do not bake modifiers (Array modifier turns 1 MB into 56 MB)
- `export_draco_mesh_compression_enable=False` — apply Draco later via gltf-transform
- Quote all paths that may contain spaces

### Step 5: Optimize with gltf-transform

Run after a successful export. Always use individual steps, never `optimize`:

```bash
# 1. Inspect raw export first
npx @gltf-transform/cli inspect output.glb

# 2. Resize textures (max 1K for web/mobile)
npx @gltf-transform/cli resize output.glb resized.glb --width 1024 --height 1024

# 3. WebP compression (quality 90 preserves detail)
npx @gltf-transform/cli webp resized.glb webp.glb --quality 90

# 4. Draco mesh compression (LAST — irreversible)
npx @gltf-transform/cli draco webp.glb final.glb

# 5. Inspect final result
npx @gltf-transform/cli inspect final.glb
```

Expected size reduction: ~22 MB raw → ~3.7 MB (WebP) → ~1 MB (Draco). See [references/texture-optimization.md](references/texture-optimization.md) for detailed metrics.

### Step 6: Validate

Run the full Post-Export Validation checklist below before shipping.

## Post-Export Validation Checklist

After every export, verify the following before handing off the GLB for integration:

- [ ] **File size is reasonable** — raw GLB under 30 MB, optimized GLB under 5 MB for typical web scenes. Flag anything above these thresholds.
- [ ] **Inspect with gltf-transform CLI** — run `npx @gltf-transform/cli inspect final.glb` and check: mesh count, texture count, texture sizes, animation count, accessor sizes. No unexpected duplication.
- [ ] **Visual test in Babylon.js Sandbox** — drag-and-drop the GLB at [sandbox.babylonjs.com](https://sandbox.babylonjs.com). Verify: mesh renders correctly, textures appear, animations play, no black/pink materials.
- [ ] **No Three.js console errors** — load in a minimal Three.js GLTFLoader test page and check browser console. Common errors: `THREE.GLTFLoader: Unknown extension`, missing texture files, unsupported Draco version.
- [ ] **Materials spot-check** — pick 3–5 materials and visually confirm roughness, metalness, and base color look correct. Compare against Blender viewport render. Flag any that look flat or overly shiny.
- [ ] **Animation spot-check** — if the scene has animations, verify at least one plays correctly in Babylon.js Sandbox or Three.js. Check frame count matches expected.
- [ ] **Name mapping verified** — if runtime code references mesh names, confirm the names match after GLTF export transformation (spaces → underscores, dots removed). See [Critical Rule 5](#5-gltf-name-mapping).
- [ ] **No missing textures** — check Babylon.js Sandbox network tab. No 404s for texture files. All textures should be packed inside the GLB.

## Examples

### Example 1: Export Character Rig with Animations

**Scenario:** You have a humanoid character with armature, 3 NLA actions (idle, walk, run), PBR texture set, and a weapon attached via parenting. You need a web-ready GLB for a Three.js scene.

**Step 1: Health check and scene inspection**

```bash
# MCP tool calls
get_scene_info
execute_python: print("ok")
```

**Step 2: Inspect the rig**

```python
import bpy, json

# Check armature and NLA strips
for obj in bpy.data.objects:
    if obj.type == 'ARMATURE':
        print(f"Armature: {obj.name}")
        if obj.animation_data:
            print(f"  Active action: {obj.animation_data.action.name if obj.animation_data.action else 'None'}")
            for track in obj.animation_data.nla_tracks:
                print(f"  NLA track: {track.name}")
                for strip in track.strips:
                    print(f"    Strip: {strip.name}, frames {strip.frame_start}-{strip.frame_end}")
```

**Step 3: Check materials for export losses**

Run the material extraction above. For a character, watch for:
- Procedural skin texture nodes (Noise → color variation) — these will be lost
- Color Ramp on roughness for fabric — will be lost, roughness will look flat
- Decision: bake procedural variations to image textures, or patch roughness values at runtime

**Step 4: Export**

```bash
blender \
  --background "/path/to/character.blend" \
  --python-expr "
import bpy, os, tempfile
export_dir = tempfile.gettempdir()
bpy.ops.export_scene.gltf(
    filepath=os.path.join(export_dir, 'character.glb'),
    export_format='GLB',
    export_apply=False,
    export_animations=True,
    export_nla_strips=True,
    export_cameras=False,
    export_lights=False,
    export_draco_mesh_compression_enable=False,
    export_skins=True,
    export_morph=True,
)
print('done:', os.path.getsize(os.path.join(export_dir, 'character.glb')) / 1024 / 1024, 'MB')
"
```

**Step 5: Verify animations exported**

```bash
npx @gltf-transform/cli inspect character.glb | grep -i anim
```

Expected output: 3 animations (Idle, Walk, Run). If 0, check that NLA strips are muted or the tracks are set to solo.

**Step 6: Optimize**

```bash
npx @gltf-transform/cli resize character.glb char_resized.glb --width 1024 --height 1024
npx @gltf-transform/cli webp char_resized.glb char_webp.glb --quality 90
npx @gltf-transform/cli draco char_webp.glb character_final.glb
```

**Step 7: Runtime animation setup (Three.js)**

```javascript
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';
import * as THREE from 'three';

const dracoLoader = new DRACOLoader();
dracoLoader.setDecoderPath('/draco/');

const loader = new GLTFLoader();
loader.setDRACOLoader(dracoLoader);

loader.load('/character_final.glb', (gltf) => {
    const mixer = new THREE.AnimationMixer(gltf.scene);
    const clips = gltf.animations; // [Idle, Walk, Run]
    const idleAction = mixer.clipAction(clips.find(c => c.name === 'Idle'));
    idleAction.play();
    // Animate mixer in render loop: mixer.update(delta)
});
```

---

### Example 2: Debug Material Export Loss (Roughness Looks Flat)

**Scenario:** After export, a metal panel material looks uniformly flat and shiny in Three.js. In Blender it had interesting roughness variation from a Noise Texture → Color Ramp → roughness input.

**Step 1: Confirm the problem in Blender**

```python
import bpy, json

mat = bpy.data.materials.get("MetalPanel")
if mat and mat.use_nodes:
    for node in mat.node_tree.nodes:
        print(f"Node: {node.type} - {node.name}")
        for inp in node.inputs:
            if inp.is_linked:
                print(f"  Input '{inp.name}': linked to something")
```

Expected output reveals:
```
Node: BSDF_PRINCIPLED - Principled BSDF
  Input 'Roughness': linked to something
Node: VALTORGB - Color Ramp         <-- this will NOT export
Node: TEX_NOISE - Noise Texture     <-- this will NOT export
```

**Step 2: Understand what GLTF received**

The export exports the Principled BSDF's roughness input. When linked to a Color Ramp, GLTF exporter takes the **default_value of the input socket** (fallback), which is typically `0.5` — perfectly flat.

**Step 3A: Fix by baking in Blender (best quality)**

```python
import bpy

# Select the object
obj = bpy.data.objects["MetalPanelMesh"]
bpy.context.view_layer.objects.active = obj
bpy.ops.object.select_all(action='DESELECT')
obj.select_set(True)

# Create a new image to bake into
bake_img = bpy.data.images.new("MetalPanel_roughness_baked", width=1024, height=1024)
bake_img.colorspace_settings.name = 'Non-Color'

# Add image texture node to material
mat = obj.active_material
nodes = mat.node_tree.nodes
img_node = nodes.new('ShaderNodeTexImage')
img_node.image = bake_img
nodes.active = img_node

# Bake roughness (use ROUGHNESS pass or EMIT trick)
bpy.context.scene.cycles.bake_type = 'ROUGHNESS'
bpy.ops.object.bake(type='ROUGHNESS', save_mode='INTERNAL')

# Save baked image
import tempfile, os
bake_path = os.path.join(tempfile.gettempdir(), 'MetalPanel_roughness_baked.png')
bake_img.filepath_raw = bake_path
bake_img.file_format = 'PNG'
bake_img.save()
print(f"Baked roughness to {bake_path}")
```

Then connect the new image texture node to the Roughness input and re-export.

**Step 3B: Fix at runtime in Three.js (quick patch)**

If you cannot bake, override the material roughness after load:

```javascript
loader.load('/metal_panel.glb', (gltf) => {
    gltf.scene.traverse((child) => {
        if (child.isMesh && child.material) {
            const mats = Array.isArray(child.material) ? child.material : [child.material];
            mats.forEach(mat => {
                if (mat.name === 'MetalPanel') {
                    // Instead of flat 0.5, set a textured roughness or varied value
                    mat.roughness = 0.3;  // adjust to match intended look
                    mat.metalness = 0.9;
                    mat.needsUpdate = true;
                }
            });
        }
    });
});
```

**Step 4: Verify fix**

Re-export and run validation checklist. In Babylon.js Sandbox, compare the metal panel material against a Blender viewport screenshot to confirm roughness variation is preserved.

## Critical Rules

### 1. MCP Server Times Out on Exports

The Blender MCP server cannot handle GLTF exports — they exceed the timeout. Always use headless CLI:

```bash
blender --background "scene.blend" --python-expr "
import bpy, os
export_path = 'output.glb'
os.makedirs(os.path.dirname(export_path), exist_ok=True)
bpy.ops.export_scene.gltf(
    filepath=export_path,
    export_format='GLB',
    export_apply=False,
    export_animations=True,
    export_nla_strips=True,
    export_cameras=True,
    export_lights=False,
    export_draco_mesh_compression_enable=False,
)
print(f'Size: {os.path.getsize(export_path)/1024/1024:.1f} MB')
"
```

### 2. Do NOT Apply Modifiers on Export

Set `export_apply=False`. Array modifiers (circular patterns, linear repeats) balloon file size when baked. Replicate them at runtime instead.

Example: 16 roller instances via Array modifier = ~1 MB GLB. Baked = ~56 MB GLB.

### 3. Export WITHOUT Draco First

If you plan to optimize with `gltf-transform`, export without Draco compression. Re-encoding existing Draco corrupts meshes. Apply Draco as the final step.

### 4. Procedural Textures Don't Export to GLTF

These Blender node setups are **lost** on export:

| Node Setup | What's Lost | Workaround |
|------------|-------------|------------|
| Noise Texture → roughness | Entire procedural chain | Bake to texture, or shader patch at runtime |
| Color Ramp on roughness texture | Value remapping range | Manual roughness values, or runtime remap |
| Procedural bump (Noise → Bump) | Bump detail | Bake normal map in Blender |
| Mix Shader with complex factor | Blend logic | Simplify to single BSDF before export |

**What DOES export:** flat roughness/metallic values, image textures (without Color Ramp remapping), baked normal maps, PBR texture sets (baseColor, metallicRoughness, normal).

### 5. GLTF Name Mapping

Blender names are transformed in GLTF:
- Spaces → underscores
- Dots → removed
- Trailing spaces → trailing underscore

| Blender | GLTF |
|---------|------|
| `RINGS ball L` | `RINGS_ball_L` |
| `Sphere.003` | `Sphere003` |
| `RINGS L.001` | `RINGS_L001` |
| `RINGS S ` (trailing space) | `RINGS_S_` |

Always check names in the exported GLB, not Blender, when referencing meshes in code.

### 6. Never Use gltf-transform `optimize`

The `optimize` command includes `simplify` which destroys mesh geometry. Use individual steps instead:

```bash
# Resize textures (max 1024x1024)
npx @gltf-transform/cli resize input.glb resized.glb --width 1024 --height 1024

# WebP texture compression
npx @gltf-transform/cli webp resized.glb webp.glb --quality 90

# Draco mesh compression (LAST step)
npx @gltf-transform/cli draco webp.glb output.glb
```

### 7. Quote Paths with Spaces

Blender project paths often contain spaces. Always double-quote:
```bash
blender --background "$HOME/Downloads/blend 3/scene.blend" ...
```

## Scene Extraction Pattern

Full hierarchy with materials, transforms, and modifiers:

```python
import bpy, json

def extract_hierarchy(obj, depth=0):
    data = {
        "name": obj.name,
        "type": obj.type,
        "location": list(obj.location),
        "rotation": list(obj.rotation_euler),
        "scale": list(obj.scale),
        "visible": not obj.hide_viewport,
        "children": [],
    }
    if obj.type == 'MESH' and obj.data:
        data["vertices"] = len(obj.data.vertices)
        data["faces"] = len(obj.data.polygons)
        data["materials"] = [slot.material.name for slot in obj.material_slots if slot.material]
    if obj.type == 'LIGHT':
        data["light_type"] = obj.data.type
        data["energy"] = obj.data.energy
        data["color"] = list(obj.data.color)
        if obj.data.type == 'AREA':
            data["size"] = obj.data.size
            data["size_y"] = obj.data.size_y
    # Array modifiers (important for runtime replication)
    for mod in obj.modifiers:
        if mod.type == 'ARRAY':
            data.setdefault("modifiers", []).append({
                "type": "ARRAY",
                "count": mod.count,
                "offset_object": mod.offset_object.name if mod.offset_object else None,
            })
    for child in obj.children:
        data["children"].append(extract_hierarchy(child, depth + 1))
    return data

scene_data = {
    "name": bpy.context.scene.name,
    "fps": bpy.context.scene.render.fps,
    "frame_start": bpy.context.scene.frame_start,
    "frame_end": bpy.context.scene.frame_end,
    "objects": [],
}

for obj in bpy.context.scene.objects:
    if obj.parent is None:
        scene_data["objects"].append(extract_hierarchy(obj))

print(json.dumps(scene_data, indent=2))
```

## Material Extraction Pattern

```python
import bpy, json

def extract_materials():
    materials = []
    for mat in bpy.data.materials:
        if not mat.use_nodes:
            continue
        info = {"name": mat.name, "nodes": []}
        for node in mat.node_tree.nodes:
            node_data = {"type": node.type, "name": node.name}
            if node.type == 'BSDF_PRINCIPLED':
                for inp in node.inputs:
                    if inp.is_linked:
                        node_data[inp.name] = "linked"
                    elif hasattr(inp, 'default_value'):
                        val = inp.default_value
                        try:
                            node_data[inp.name] = list(val)
                        except TypeError:
                            node_data[inp.name] = float(val)
            if node.type == 'TEX_IMAGE' and node.image:
                node_data["image"] = node.image.filepath
                node_data["size"] = [node.image.size[0], node.image.size[1]]
            info["nodes"].append(node_data)
        materials.append(info)
    return materials

print(json.dumps(extract_materials(), indent=2))
```

## Animation Keyframe Extraction

```python
import bpy, json

def extract_animation(obj):
    if not obj.animation_data or not obj.animation_data.action:
        return None
    tracks = []
    for fc in obj.animation_data.action.fcurves:
        keyframes = []
        for kp in fc.keyframe_points:
            keyframes.append({
                "frame": int(kp.co[0]),
                "value": float(kp.co[1]),
                "interpolation": kp.interpolation,
            })
        tracks.append({
            "data_path": fc.data_path,
            "index": fc.array_index,
            "keyframes": keyframes,
        })
    return {"object": obj.name, "tracks": tracks}

animations = []
for obj in bpy.data.objects:
    anim = extract_animation(obj)
    if anim:
        animations.append(anim)

print(json.dumps(animations, indent=2))
```

## GLTF Export Settings Reference

| Setting | Value | Why |
|---------|-------|-----|
| `export_format` | `'GLB'` | Single binary file |
| `export_apply` | `False` | Don't bake modifiers (Array, etc.) |
| `export_animations` | `True` | Include animation data |
| `export_nla_strips` | `True` | Bake NLA strips into actions |
| `export_cameras` | `True` | Include camera rigs |
| `export_lights` | `False` | Handle lights in runtime (Three.js/R3F) |
| `export_draco_mesh_compression_enable` | `False` | Apply Draco later via gltf-transform |

## Texture Optimization Pipeline

Target: smallest GLB with acceptable visual quality.

```
Blender export (no Draco) → resize (1K max) → WebP (q90) → Draco
   ~22 MB                    ~3.7 MB           ~3.7 MB      ~1 MB
```

Key insights:
- 4K textures (4096x4096) = ~89 MB GPU memory per texture. 1K = ~5.6 MB. **16x reduction**.
- PNG metallicRoughness textures compress well to WebP at quality 85-90.
- Mobile GPUs (Adreno, Mali) benefit most from texture downscaling.
- Inspect with: `npx @gltf-transform/cli inspect model.glb`

See [references/texture-optimization.md](references/texture-optimization.md) for concrete commands and quality metrics.

## Asset Integrations

Available through Blender MCP when configured:

| Integration | Capabilities |
|-------------|-------------|
| **PolyHaven** | Search, download, import free HDRIs, textures, and 3D models with auto material setup |
| **Sketchfab** | Search and download models (requires access token) |
| **Hyper3D Rodin** | Generate 3D models from text descriptions or reference images |
| **Hunyuan3D** | Create 3D assets from text prompts, images, or both |

See [references/asset-integrations.md](references/asset-integrations.md) for usage examples and workflow patterns.

## Annotated Diagrams (labels/callouts)

3D text labels in Blender are a trap: billboard to the render camera AFTER depsgraph update, chips drift from text, glyphs z-fight, lines notch text, labels occlude each other. The fast path: render a CLEAN frame, project 3D anchor points to pixels with `bpy_extras.object_utils.world_to_camera_view`, then draw chips/leader lines/dots in PIL (2D). Sort callout rows by anchor Y so leaders never cross. 15 minutes, pixel-perfect.

## Tripo API + debris-cleanup (2026-09 humidifier v3)

- **Tripo v2 openapi recipe:** POST `/upload` (multipart file=@) → `image_token`; multiview task = `POST /task {type:multiview_to_model, files:[{type,file_token}×4 in front,left,back,right order, {} for a skipped view]}` (v2.5 accepts 3 tokens; `model_version:v3.1-20260211` = H3 v3.1, detailed geometry no extra cost; both ≈40cr); poll `GET /task/{id}` (~1–2 min); `data.output.pbr_model` = signed URL (~15 min life). `POST /upload/staging` and `file:{multiview:[tokens]}` shapes DO NOT exist (9404/1004).
- **Tripo GLB = parts mode:** headless `import_scene.gltf` yields hundreds of separate mesh objects (GUI import may show ONE mesh with debris as inner islands). Reference images' annotation overlays (label chips + leader lines) get RECONSTRUCTED as 3D debris: floating navy bars + tether lines.
- **Cleanup ladder (works):** run in HEADLESS blender, never via MCP `execute_blender_code` — island BFS on ~1M verts hangs >10 min and wedges the MCP socket (kill GUI blender, file is already saved). (1) select mesh, `bpy.ops.mesh.separate(type='LOOSE')` (C-speed) → bbox per island via `evaluated_get(depsgraph).bound_box @ matrix_world` (object origins are all zero — use bbox centers). (2) kill islands with bbox max/min dim ratio >8 (tubes, flat bars). (3) kill islands whose bbox center is >0.30 from the median center of the top-12 largest islands. (4) kill islands <40 verts (glyphs). NEVER seed on the single largest island — the enclosure is split into several large islands; single-seed pruning amputates the shell.
- **Residual after all filters:** tethers/rods CONNECTED to the shell survive every island filter; only mesh surgery removes them. Expect 3–4 rod stubs (v2.5), torn edges + spikes (v3.1). Filtering iterations cost shell integrity — stop before the device stops reading as a device, ship with status.
- **Attached-rod surgery is a dead end — do not attempt local filters:** a rod's surface verts and a shell EDGE's verts are locally identical (both neighborhoods thin in 2 axes; rod emerging near a wall sees the wall too). KD-tree span tests (2-thin-axes = rod) delete shell borders; fixed-bbox face cuts amputate the shell (v3.1 lost its walls this way — always backup the GLB before any face-level cut, and verify with a solo vision render after). Root-cause fix is UPSTREAM: strip annotation overlays (chips/lines/dots) from input images BEFORE generation, or accept the stubs. Two thin-axis span test worked only for truly detached thin strands, never for attached ones.
- **GLB round-trip:** headless export→import preserves object names — a root-empty exported GLB re-imports as the same named empty, so `tops[0]` recovers the hierarchy. Always run scripts on an OPENED file (`open_mainfile`) — building on the default startup scene then crashing loses everything unsaved.
- **bmesh 5.2:** BMVert has no `is_visible`.
- **Name-filter traps:** generated names can carry LEADING SPACES (`f' Rail{ s}'` produced `' Rail-1'`) — `startswith('Rail')` misses them and the parts survive every purge, silently protruding from later assemblies. Purge by `'rail' in name.lower()` / substring, never prefix alone; print the matched name list before deleting to confirm what you actually caught.
- **"One box" silhouette rules (user-visible QA):** any proud panel (cap lid, grille plate with sharp corners on a beveled shell, 3mm-proud service covers) reads as a second block to viewers — flush panels into the face, shrink square plates inside the rounded silhouette, and drop labels that NAME a region as a separate module ("2in Extension") since labels teach viewers to see blocks that aren't there. Interior components must end ≥2mm behind flush covers or they poke through. Per-view part states (drawer open for its detail shot, flush elsewhere) beat one compromise pose.

## Modeling-Session Lessons (2026-09 humidifier v3, MCP long-session)

- **Operator context drifts in long MCP sessions:** `primitive_cube_add(location=X)` + `transform_apply(scale=True)` silently left ~50% of boxes at the ORIGIN (correct dims, wrong pos); cylinders were unaffected. Symptom: ray_cast hits the housing shell instead of the part. Root fix: build boxes with bmesh (`create_cube` → `scale` → `translate`) — zero operators, immune. Cylinders may keep ops. ALWAYS probe every placed part with `scene.ray_cast` (from camera toward expected surface, check hit object name) before rendering; a successful script print is not proof of placement.
- **Interior parts sealed in solids:** components inside a solid primitive housing are invisible from every angle even when correctly placed. Cut a cavity: boolean pocket through the housing (vent recess into Body top; open-back bay pocket through the extension wall). Live hidden cutters (hide_render+hide_viewport) are fine for renders; apply only if the mesh must be edited further.
- **Perforated grille holes vanish at high-key exposure** (white plate on white bg): put a dark Charcoal backing panel ~1.5cm behind the holes — holes instantly read as cutouts.
- **High-key washout fix:** world strength ≤0.3, key 75-90W, plus `view_settings.look='AgX - Medium High Contrast'` and exposure −0.3. Plain AgX stays washed out on white products.
- **Mist/water feedback sells function:** 2-3 alpha-0.18 white spheres above a mist vent read as vapor; translucent tanks need Base Color ~(0.50,0.72,0.90) + Alpha 0.65 — near-white frost reads as empty plastic.
- **Label-dot QA without vision API:** sample pixels at projected anchor coords (PIL): white sum>700 at center + navy sum<300 within ±16px = dot rendered; surrounding pixel colors confirm the part under it. Vision API can 409-race on parallel image calls — serialize or fall back to pixel checks.

## Modeling-Session Lessons (2026-09 humidifier v2)

- **Define FRONT/BACK before any placement.** Set a comment constant (`# front is -Y`) at script top; every feature placement derives from it. Sign-flipped coordinates put the LED, drawer, and tank on the wrong side — 3 fix cycles. Verify placement with `scene.ray_cast` probes (cast from outside toward expected surface, check hit object + y) BEFORE rendering.
- **Cutter penetration on solidified walls:** boolean cutters must extend ~1mm PAST the final thickened surface, not end flush at the original skin — SOLIDIFY offsets the outer face (0.150 → 0.1481), and a flush cutter cuts depth 0 (grille silently missing). Add 1mm overshoot to every cutter.
- **Modifier-apply during a boolean bakes the whole stack below it** (Sol+Bev went into the mesh silently at 35s). Strip the leftover modifiers after apply or walls double-thicken.
- **bmesh 5.2:** `create_cone` exists, `create_cylinder` does NOT. `delete(context='FACES')` on a single-face mesh deletes the whole mesh (verts orphan) — build prisms as bottom-NGON extruded, then delete the target wall by `abs(face.center - expected_plane) < 1e-4` (normals are inward before recalc — never filter on `f.normal`).
- **OpenGL renders need camera-facing viewports:** `get_viewport_screenshot` returns whatever angle the viewport is at, not the render camera. Render to `/tmp/*.png` via `bpy.ops.render.opengl(write_still=True)` with the camera repositioned per angle, and vision-check the PNG file, not the viewport.
- **Array-modifier instances don't ray_cast or boolean** (evaluated-only) — apply the array before using the object as a boolean cutter.
- **49×42 cutter grid (~20.5k faces) EXACT boolean: 35-80s.** Completed both times; only fall back to procedural bump if it exceeds ~120s.
- **GLTF export pitfall (bpy.ops.export_scene.gltf from a UI-session blend):** armatures fail with `validate_armature_node` ("no valid armature") on scenes with no rig — export via headless CLI or strip non-mesh data first.
- **Bmesh↔object coordinates:** `create_cone` is Z-axis; for front/back-facing features rotate verts `Y→Z` (`(x, -z, y)`) at bmesh level.

- **Save every checkpoint.** The MCP-linked Blender instance can crash/empty mid-session (scene wiped to 0 objects while idle). The disk file survives — `wm.open_mainfile` reloads it and work continues. Backgrounded UI instances also die when an unrelated foreground terminal call exits; be ready to relaunch.
- **Array modifier offset is LOCAL space multiplied by object scale.** A scaled-down object (e.g. slat scaled 0.008 in Y) turns a 19mm offset into 0.15mm — all instances stack invisible inside each other. Fix: `transform_apply(scale=True)` FIRST (bake scale into mesh), then set array offset in real units. Verify with evaluated depsgraph vert count (instances × per-instance verts).
- **Uniform object.location shifts shear staggered stacks** (drawer panel + lip + tank all shifted by same dy = tank slides out past the panel, absurd pose). A drawer slide needs per-part offsets: front panel moves further than interior contents.
- **Translucent materials (Transmission 0.7) vanish against light backdrops** in OpenGL previews — use Alpha ~0.55 + blend_method 'BLEND' for visible-but-frosted looks.
- **Fully metallic parts render TAN/dark in OpenGL** (no env reflection) — use Metallic 0.2-0.3 + bright base color when the preview is the deliverable; full metallic is fine for Cycles finals.
- **Flat-lying PCBs are invisible from horizontal cameras.** Mount key boards VERTICALLY face-out against walls (like the reference) or accept they won't read; check from the actual viewing angle, not top-down theory.
- **Ray probes + angled close-ups together.** Probes prove existence; only a render from the inspection angle proves visibility. A part can exist, ray-cast fine, and still be hidden behind its own wall from the camera side.
- **Cutaway shots:** hiding the back cover is not enough when an extension prism or wall piece sits behind the opening — hide every shell piece on the view path or the cavity still reads closed.

## Known Errors & Workarounds

See [references/errors.md](references/errors.md) for complete error tables.

## Data Output

- `print()` + `json.dumps()` for small results (scene info, single object)
- Use `tempfile.gettempdir()` for large extraction results (full hierarchy, animation data, material reports)
- Always include metadata: scene name, fps, frame range, Blender version
