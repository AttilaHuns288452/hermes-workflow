# Raw Socket Protocol (driving the addon without the MCP client)

The addon serves JSON over TCP `localhost:9876`. One request per connection: send a JSON object, read until the accumulated bytes parse as JSON, then close.

## Command names (verified against the addon source)

`get_scene_info`, `execute_code`, `get_viewport_screenshot`, `get_object_info`, `get_world_state_snapshot`, `get_polyhaven_*`, `get_sketchfab_*`.

There is NO `screenshot` and NO `execute_python` — those names return `Unknown command type`. When in doubt, grep the addon source for the dispatch table.

## Helper

```python
import socket, json

def mcp_call(payload, timeout=30):
    s = socket.create_connection(("localhost", 9876), timeout=timeout)
    s.sendall(json.dumps(payload).encode())
    data = b""
    while True:
        chunk = s.recv(65536)
        if not chunk:
            break
        data += chunk
        try:
            json.loads(data.decode())
            break
        except Exception:
            pass
    s.close()
    return json.loads(data.decode())
```

## Calls

```python
mcp_call({"type": "get_scene_info", "params": {}})
mcp_call({"type": "execute_code", "params": {"code": "import bpy; print(bpy.app.version_string)"}})
mcp_call({"type": "get_viewport_screenshot", "params": {"max_size": 800, "filepath": "/tmp/shot.png", "format": "png"}})
```

## Response shapes

- Success: `{"status": "success", "result": {...}}`. `execute_code` returns captured stdout under `result.result` — print JSON from the script for structured data.
- Error: `{"status": "error", "message": "<JSON string>"}` where the inner JSON has `exception_type`, `message`, and a full `traceback`. Parse `message` before retrying.
- `get_viewport_screenshot` writes the PNG to `filepath` itself; the response carries `width/height/filepath` (no base64 payload).

## Blender 5.x scripting notes

- **Primitive operators no longer accept `name=`** (`TypeError: keyword "name" unrecognized`). Create, then rename: `bpy.context.object.name = "X"`.
- Principled BSDF transmission input is `Transmission Weight` on 4.x+/5.x; use `bsdf.inputs.get("Transmission Weight")` and guard for None to stay version-safe.
- After `bpy.ops.object.join()`, run `bpy.ops.object.shade_flat()` — joined meshes keep smooth shading and facet structure reads as domed/rounded instead of faceted.
- Two cones make a diamond: crown = `radius1=girdle, radius2=table` above z-girdle; pavilion = `radius1=0` (apex DOWN at the BOTTOM), `radius2=girdle`. Getting `radius1`/`radius2` backwards inverts the pavilion apex upward into an hourglass.
- `bmesh.ops.extrude_face_region` takes `geom=`, NOT `faces=` (`TypeError` on `faces=`).
- To open a box (front face removed, walls kept): do NOT use bmesh `inset_region` + `extrude_face_region` — the original face survives as a rim cap and the front stays closed. Deterministic recipe: `bmesh.ops.delete(front_face, context="FACES")` → SOLIDIFY modifier (wall thickness) → BEVEL modifier (rounding). Deterministic beats clever here; selection-flag-based edit-mode ops also silently lose selection by the time the op runs.
- `scene.ray_cast` hits a cached BVH. After geometry changes: `bpy.context.view_layer.update()` + fresh `bpy.context.evaluated_depsgraph_get()`, and run verification rays in a SEPARATE execute_code call from the mutation call.
- ARRAY modifier offsets follow the cutter's LOCAL axes. For hole grids through a face: create the cutter already rotated, set `use_constant_offset=True` (not relative), and verify the grid's world extent via `obj.matrix_world @ Vector(c)` over `bound_box` before booleaning — local/world axis confusion silently drills the grid through empty space (e.g. below the floor).
- Blender's bundled Python has no PIL/numpy: save renders/screenshots to disk from Blender, then analyze the files in the agent's own Python.
- `bpy.ops.wm.save_as_mainfile` fails on a missing directory — `mkdir -p` the output path first.

## Server not listening (9876)

The addon auto-starts the server when enabled persistently. If the port is dead, relaunch Blender with:

```bash
blender --python-expr "import addon_utils; addon_utils.enable('blender_mcp_addon', default_set=True, persistent=True); import blender_mcp_addon as m; srv=m.BlenderMCPServer(host='localhost', port=9876); srv.start(); import bpy; bpy.types.blendermcp_server=srv"
```

Poll `ss -tlnp | grep 9876` before calling. Launching via a script file written to /tmp avoids shell-quoting bugs with the nested quotes.
