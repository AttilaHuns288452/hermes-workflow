# Studio Render Recipe (Cycles, GPU)

Product-shot rendering from a scripted scene. All snippets run via `execute_code`.

## Engine + GPU setup

```python
sc = bpy.context.scene
sc.render.engine = "CYCLES"
prefs = bpy.context.preferences.addons["cycles"].preferences
prefs.compute_device_type = "OPTIX"   # NVIDIA; "CUDA" fallback
prefs.get_devices()
for d in prefs.devices: d.use = (d.type != "CPU")
sc.cycles.device = "GPU"
sc.cycles.samples = 192               # 128 draft, 256 final
sc.cycles.use_denoising = True
sc.view_settings.view_transform = "AgX"
sc.render.resolution_x, sc.render.resolution_y = 1600, 1200
sc.render.filepath = "/tmp/render.png"
bpy.ops.render.render(write_still=True)
```

A 1600x1200 192-sample render takes ~1–2 min on a mid RTX GPU — well within the socket timeout.

## Scene staging

- **Floor plane is mandatory.** No floor = no contact shadow = everything reads as floating. Big plane (size 8), matte gray (roughness ~0.75–0.85).
- Skip a separate backdrop plane unless the camera needs it — world background at strength ~0.2–0.35 gives the gray-sweep gradient for free.
- **Camera**: 50mm, Track-To constraint to an empty at the subject's center. DOF on, f/8–f/11 — f/4 melts product shots.

## Lighting

- Key: AREA light, ~90–130W, upper front-side, size ~0.7.
- Fill: ~20–25W opposite side, size ~1.0.
- Rim: ~40–55W behind/above for edge separation.
- First render of a new setup will be over- or under-exposed — drop light energy, don't fight it in post.

## AgX emission gotcha

AgX clips emissives hard: emission strength >50 renders WHITE and kills the hue. Strength 20–30 keeps color visible while still glowing. Verify emission with a pixel scan for the target hue (e.g. blue-dominant pixels), not by eye against a clipped render.

## Making perforations read as holes

Through-holes only read as holes if something DARK is behind them: put a dark cavity liner surface (roughness ~0.95, near-black) ~0.5–2mm behind the perforated panel. Without it, bright interior walls show through and holes read as raised bumps. Bore size matters too: under ~3mm at 3/4 camera angles dots optically flip to bumps; 4mm+ bores read correctly.

## Material starting points

Tune and NAME materials early — they survive across re-renders and iterations build on them.

| Material | Setup |
|---|---|
| Ivory plastic body | Base (0.90, 0.89, 0.85), rough ~0.4, coat weight ~0.15 |
| Frosted/translucent | Transmission Weight ~0.3–0.6, rough ~0.25–0.35 |
| Water | Transmission 1.0, IOR 1.33, rough 0.02, base (0.35, 0.62, 0.78) |
| Cavity dark | Base (0.02, 0.02, 0.025), rough 0.95 |
| Metal can/shield | Metallic 1.0, rough 0.3–0.35 |

## Presentation state

For the final render, assemble exploded parts back to their mounted positions (a floating panel casts no shadow and reads as a bug), delete scratch/cutter objects and stray duplicates, then save the .blend into the project dir (mkdir -p first) and copy renders there — not /tmp.