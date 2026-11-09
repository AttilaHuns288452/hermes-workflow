---
name: cinematic-pipeline
description: "Code-driven 3D cinematic video production using Blender via the cinematic-pipeline Python package. Use when the user wants to generate Blender scenes programmatically (dataclass scene description -> generated Blender Python script -> rendered MP4), build cinematic 3D camera/lighting shots, or render Blender animations from code without manual Blender UI work."
---

# cinematic-pipeline (code-driven Blender cinematics)

Author 3D cinematic shots in Python dataclasses; the package generates a self-contained
Blender Python script, then Blender renders it. No manual Blender UI.

> Source: Kitolochi/cinematic-pipeline @ 13c74a7 (MIT). Installed editable at
> `~/Documents/Projects/cinematic-pipeline`. This wrapper records the local install
> contract and Blender 5.x gotchas proven on this machine.

## Install (already done here)

```
python3 -m pip install -e ~/Documents/Projects/cinematic-pipeline
```

Pure-Python, zero deps. The examples also run standalone (they `sys.path.insert` the
`src/`), so the package works even before install.

## Run contract (important)

Generate the scene, then run Blender **from the parent dir that contains the output/ folder**
(the generated script uses `./output/...` relative paths):

```
cd ~/Documents/Projects/cinematic-pipeline
python3 examples/hello_cube.py          # writes output/hello_cube/_render_script.py
blender --background -E CYCLES --python output/hello_cube/_render_script.py
```

Running Blender from inside `output/hello_cube/` writes artifacts to a nested
`output/hello_cube/output/` — always run from the project root.

## Blender 5.x gotcha (fixed in our install)

Blender 5.x headless builds reject `image_settings.file_format = 'FFMPEG'` (movie output
is NOT in the assignable enum — `OPEN_EXR_MULTILAYER` is also gated). Upstream's
`render_animation_script` emitted `FFMPEG` and crashed. Our installed copy is patched:
it renders a **PNG frame sequence** then muxes to MP4 with `ffmpeg` (`-c:v libx264
-pix_fmt yuv420p`). Do not revert to `FFMPEG`. Renders stills/frames via
`image_format='PNG'` which is valid.

## NVIDIA offload (this Optimus box)

Rendering is ~10x faster on the dGPU. Always prefix the blender command:

```
__NV_PRIME_RENDER_OFFLOAD=1 __GLX_VENDOR_LIBRARY_NAME=nvidia blender --background -E CYCLES ...
```

## API surface

- `Scene(name, fps, frame_end, render_engine, render_samples, world_color, ...)`
- `Mesh(name, primitive=PrimitiveType.*, size, location, material_name)`
- `Camera(name, preset=CameraPreset.*, location)`, `Light(name, light_type=LightType.*, location)`, `three_point_rig`
- `Material`, `metallic_dark`
- `RenderConfig(output_dir, filename_prefix, image_format, ...)`
- `write_and_render(scene, config, mode="animation"|"still"|"frames") -> blender cmd`

See `examples/hello_cube.py` (smoke test), `examples/cinematic_cube.py`,
`examples/asset_showcase.py` in the install dir.

## Verified

2-frame CYCLES scene -> PNG frames -> ffmpeg mux -> real MP4 (h264 1920x1080) on
Blender 5.2.1 LTS. `python3 examples/hello_cube.py` generates the render script clean.
