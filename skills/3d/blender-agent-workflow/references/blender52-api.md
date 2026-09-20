# Blender 5.2 API Renames & Behavior (vs 4.x-era examples)

Check this table before running any bpy script copied from 4.x examples, MCP addon snippets, or older sessions.

| Old pattern | 5.2 reality | Fix |
|-------------|-------------|-----|
| `primitive_cube_add(name="X")` (and other `primitive_*_add` name kwargs) | `TypeError: keyword "name" unrecognized` | Create, then `bpy.context.object.name = "X"` |
| `bmesh.ops.extrude_face_region(faces=[...])` | `TypeError: keyword "faces" is invalid` | Use `geom=`; returns `{'geom': [...]}` — filter BMVert entries to translate |
| bmesh inset + extrude_face_region to 'open a box' | Original faces survive as a rim capping the opening — box stays closed, silently | bmesh-delete the face, then SOLIDIFY + BEVEL modifiers |
| `bpy.ops.object.convert(type="MESH")` | `TypeError: keyword "type" unrecognized` | `convert(target="MESH")` (try/except both across versions) |
| `sc.view_layer.update()` | `AttributeError: 'Scene' object has no attribute 'view_layer'` | `bpy.context.view_layer.update()` |
| `shade_smooth()` on a faceted primitive (gem, frustum) | Smooth normals make facets read as a dome | `shade_flat()` on faceted geometry; smooth only for organic curved parts |
| Emission Strength > 50 with AgX | Clips to white — colored LED renders white | Keep ~20–30 under AgX; pixel-verify hue (`B > R+15`), not brightness |
| ARRAY modifier on a rotated cylinder with relative offsets | Offsets apply in LOCAL axes — rows go sideways / below the floor | `use_relative_offset=False; use_constant_offset=True` with local-axis displace, or compute world steps manually |
| GLTF export with font/curve objects selected | They silently drop from the GLB | `convert(target="MESH")` all text/curve objects first |
| `scene.ray_cast` right after an edit in the same script | Stale depsgraph — hits the old mesh | `view_layer.update()` + fresh `evaluated_depsgraph_get()`, ideally in a separate execution |

## Socket-server relaunch (MCP addon, port 9876)

When the socket dies (Blender quit/crashed), relaunch with the file preloaded:

```bash
DISPLAY=:0 blender /path/to/file.blend --python-expr "import addon_utils; addon_utils.enable('blender_mcp_addon',default_set=True,persistent=True); import blender_mcp_addon as m; srv=m.BlenderMCPServer(host='localhost', port=9876); srv.start(); import bpy; bpy.types.blendermcp_server=srv" &
```

Then confirm with `ss -tlnp | grep 9876` before the next MCP call. Raw protocol through the socket (when MCP tools aren't loaded in-session): `json.dumps({"type":"execute_code","params":{"code":...}})` — command types include `get_scene_info`, `execute_code`, `get_viewport_screenshot` (there is no `screenshot` command).
