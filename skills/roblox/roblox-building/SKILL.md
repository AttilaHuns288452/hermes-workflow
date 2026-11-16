---
name: roblox-building
description: "Use when building or editing geometry, maps, props, or generated assets with MCP or standalone Luau"
---


# Roblox Building

## When to Load

Load for geometry, props, maps, and spatial onboarding via MCP or Luau.

## Quick Reference

### MCP Build Mode
1-2. Inspect Studio/Workspace/assets; name root, origin, dimensions, assets.
3-4. Build in phases with readback; verify tree, view, traversal.

### Asset Choice
- Search project assets and Toolbox first; check type, creator, price, scripts, fit.
- Paid/cross-owner insertion: disclose creator, ID, price, rights first. Inspect scripts/dependencies; remove unneeded code. See `roblox-security`.
- MCP: `generate_procedural_model`, `generate_mesh`, `generate_material`.
- Check mesh bounds, collision, PBR, and quality levels.
- Use permitted images; wait for jobs to finish.
- `EditableImage`/`EditableMesh`: permission + memory limits.
- Native Parts/CSG when reuse/generation is unsuitable.
- **Asset privacy:** new accounts/groups create Images/Decals/Meshes Restricted — blank texture/invisible mesh usually means a missing grant, not corruption. Read the Output error; grant the experience in Creator Dashboard. See `roblox-studio-mcp`.

### Player Scale
Player ~5 studs | Door 4w×7h | Ceiling 10-14 | Counter 3.5-4 | Seat 1.5 | Path 6+

### Spatial Rules
- Name dimensions; offset sub-parts from anchor CFrames, never guessed world coordinates.
- Snap to 0.125/0.25/0.5 studs. Build complex CSG near origin, then `PivotTo` the destination.
- Set anchoring, collision, shadows, color, material explicitly.

### Acceptance
**Prop:** named model, pivot, scale, bounds, materials, collision, anchoring, no loose parts, provenance.
**Map:** root/origin, zones, landmarks, spawns/return paths, traversal, bounds excluding Baseplate/Terrain/SpawnLocation.
**Evidence:** readback, view when supported, playtest results.

### Anti-Patterns
Guessing coordinates | unanchored/duplicate parts | hardcoded world positions | silent CSG failure | oversized batches | claims without readback

### External mesh pipeline (Blender → Studio)

When generating props in Blender and importing them as `MeshPart`s:

- **Origin at the base centre, 1 Blender unit = 1 stud.** Then placement is `CFrame.new(x, sizeY/2, z)` and props sit on the ground instead of half-buried.
- **Build the silhouette from wide low-segment chamfers, not density.** A 200-500 tri prop with a beveled profile reads better than a smooth high-poly one and stays inside mobile budgets.
- **Export OBJ and FBX from the same build.** Studio's 3D Importer file dialog filters on `*.fbx` by default, so an OBJ-only export greys out in the picker and looks like a broken importer. Scene prop meshes also download as `MeshPart`, so keep the source files in the repo for re-upload.
- **Wrap per-prop creation in `pcall` AND count the result.** A mesh helper that requires a parent folder which does not exist yet returns nil silently, and `pcall` hides the error: every prop vanishes with no log line. Assert a count (`meshParts >= N`) in a test, not just that the builder ran.
- **Baking the map into the place means the runtime builder must destroy its own previous output first**, or a playtest stacks a second map root on top of the saved one.
- **Never put `if Workspace:FindFirstChild(<root>) then return end` at the TOP of a builder.** It reads as idempotency, but it also short-circuits every configuration line below it — lighting, post-processing, materials, prop placement — the moment the place ships with a saved root. The symptom is "my changes never appear" while the file is demonstrably correct. Destroy-and-rebuild instead; if a second build in the same session must be blocked, guard on a session flag placed BELOW the configuration block.
- **Find-or-create helpers must configure the existing instance, never skip it.** An `if FindFirstChildOfClass(x) then return end` inside a helper locks in the values from the first pass forever: every later tuning edit silently does nothing while the property list still reads correctly. Assign on every call, wrapping individual assignments in `pcall` where a property is version-dependent.

### Anti-Patterns
Guessing coordinates | unanchored/duplicate parts | hardcoded world positions | silent CSG failure | oversized batches | claims without readback

**Details:** `references/full.md` (maps, validation, assets).
