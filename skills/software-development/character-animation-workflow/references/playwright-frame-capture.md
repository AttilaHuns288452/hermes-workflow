# Playwright Frame Capture for Character Animation

## Overview

Two approaches for capturing character-animation HTML to video:

- **Option A: Record video** — Playwright's built-in `record_video_dir` context option. Simpler but real-time only.
- **Option B: Frame-by-frame capture** — Deterministic frame scrubbing via `goToFrame(N)` + screenshots + ffmpeg stitch.

## Option A: Record Video (Simpler)

Use when you have a standalone HTML with GSAP animation and just want it recorded at real-time speed.

```python
from playwright.sync_api import sync_playwright
import subprocess, shutil, os

def record_video(html_path, output_mp4, duration_s=12, w=1280, h=720):
    video_dir = os.path.dirname(output_mp4) + "/_capture"
    os.makedirs(video_dir, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(
            viewport={"width": w, "height": h},
            record_video_dir=video_dir,
            record_video_size={"width": w, "height": h}
        )
        page = context.new_page()
        page.goto(html_path.resolve().as_uri(), wait_until="networkidle")
        page.wait_for_timeout(duration_s * 1000)
        context.close()  # MUST close before accessing page.video
        browser.close()

    # Find the .webm file
    import glob
    webm_files = glob.glob(os.path.join(video_dir, "*.webm"))
    if not webm_files:
        raise RuntimeError("No webm produced")

    # Convert webm to mp4
    subprocess.run([
        "ffmpeg", "-y", "-i", webm_files[0],
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
        output_mp4
    ], check=True, capture_output=True, timeout=120)

    shutil.rmtree(video_dir, ignore_errors=True)
    return output_mp4
```

**Caveats:**
- Real-time capture — 12s animation requires 12s+ of capture overhead
- Output framerate depends on browser compositor (typically ~25fps, not configurable)
- `page.video.path()` returns `None` until `context.close()` — do not try to access it before
- The webm-to-mp4 conversion is required for broad compatibility
- If CDN resources are unavailable, `wait_until="networkidle"` hangs — use `wait_until="domcontentloaded"` instead

## Option B: Frame-by-Frame Capture (Deterministic)

Use when you need exact framerate control and can expose a `goToFrame(N)` function on the page.

### The Animation HTML Pattern

The HTML must expose a `goToFrame(frameNum)` function on `window`:

```javascript
function goToFrame(frame) {
    const currentTime = frame / FPS;
    // Find active scene by time
    // Set character poses (call gsap.set or direct DOM)
    // Show/hide overlays
    // Update health bars, stat displays
}
```

For GSAP-based scenes, use `gsap.set()` instead of `gsap.to()` when scrubbing — `set()` is instant and does not interpolate. Store the active timeline actions in an array keyed by frame range, and apply the correct state at each frame.

### Playwright Capture Script

```python
from playwright.sync_api import sync_playwright

def render(html_path, output_mp4, total_frames=2430, fps=30, w=1080, h=1920):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": w, "height": h})
        # Use domcontentloaded, NOT networkidle (CDN may hang)
        page.goto(html_path.resolve().as_uri(), wait_until="domcontentloaded")
        page.wait_for_timeout(2000)  # Let JS initialize
        for frame in range(total_frames):
            page.evaluate(f"goToFrame({frame})")
            page.wait_for_timeout(5)
            page.screenshot(path=f"frame_{frame:06d}.png",
                          clip={"x": 0, "y": 0, "width": w, "height": h})
        browser.close()
    subprocess.run([
        "ffmpeg", "-y", "-framerate", str(fps),
        "-i", "frame_%06d.png",
        "-c:v", "libx264", "-preset", "slow", "-crf", 18,
        "-pix_fmt", "yuv420p", str(output_mp4)
    ], check=True)
```

### Performance

- ~5 frames/second capture speed (1080x1920 PNGs)
- 2430 frames -> ~8 minutes capture + ~2 minutes ffmpeg
- ~1.5-2MB per frame -> ~3.5GB temporary storage
- Final MP4 ~30-50MB at CRF 18

## HyperFrames Template Warning

The `character_rig_renderer` outputs HyperFrames-style HTML using `<template>` tags:

```html
<template id="character-scene-template">
  <div data-composition-id="character-scene" ...>
```

This format ONLY renders when consumed by the HyperFrames runtime. In a plain browser or Playwright capture, `<template>` elements are NOT rendered visually — the page appears to show source code.

**Fix**: Create a standalone HTML page that:
1. Inlines the SVG directly in the `<body>` (not inside `<template>`)
2. Removes the `<template>` wrapper entirely
3. Writes GSAP animation calls targeting the in-SVG selectors
4. Embeds GSAP inline (to avoid CDN dependency)

## Verifying Output

```bash
ffprobe -v quiet -print_format json -show_format -show_streams output.mp4
```

Check: duration matches expected, resolution is correct, codec is h264.
