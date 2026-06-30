# Remotion Windows Asset Path Troubleshooting

## Error Signature

When rendering via Remotion on Windows, assets fail to load with:

```
Not allowed to load local resource: file:///C:/path/to/assets/image.png
Browser failed to load file:///C:/path/to/assets/image.png (Image):
  EncodingError: The source image cannot be decoded.

Could not play audio with src file:///C:/path/to/assets/music/file.mp3:
  [object MediaError]
```

## Root Cause

The `video_compose._remotion_render()` method (line 1327-1333 in `tools/video/video_compose.py`) automatically converts non-URL paths to `file:///` URIs:

```python
for cut in props.get("cuts", []):
    source = cut.get("source", "")
    if source and not source.startswith(("http://", "https://", "file://")):
        resolved = Path(source).resolve()
        if resolved.exists():
            posix = resolved.as_posix()
            cut["source"] = f"file:///{posix}" if not posix.startswith("/") else f"file://{posix}"
```

However, Remotion's headless Chrome instance blocks `file:///` URIs for local resources. This affects:
- `backgroundImage` on cuts
- `audio.narration.src`
- `audio.music.src`
- Any `source` field on cuts

## The Path Through `resolveAsset()` in Explainer.tsx

```typescript
function resolveAsset(src: string): string {
  if (src.startsWith("http://") || src.startsWith("https://") || src.startsWith("data:"))
    return src;
  const clean = src.replace(/^file:\/\/\/?/, "");
  if (clean.startsWith("/") || /^[A-Za-z]:[\\/]/.test(clean))
    return `file:///${clean.replace(/\\/g, "/")}`;  // ← blocked!
  return staticFile(clean);  // ← works!
}
```

Key insight: paths starting with `/` are treated as absolute filesystem paths and converted to `file:///` URIs. Only relative paths (no leading `/`, no drive letter) route through `staticFile()`.

## Fix Steps

1. Copy assets into `remotion-composer/public/`:
   ```bash
   mkdir -p remotion-composer/public/assets/images
   mkdir -p remotion-composer/public/assets/audio
   mkdir -p remotion-composer/public/assets/music
   cp projects/<name>/assets/images/*.png remotion-composer/public/assets/images/
   cp projects/<name>/assets/audio/*.mp3  remotion-composer/public/assets/audio/
   cp projects/<name>/assets/music/*.mp3  remotion-composer/public/assets/music/
   ```

2. Write props JSON with relative paths (no leading `/`):
   ```python
   import json
   prop = {
       "cuts": [{
           "backgroundImage": "assets/images/hero_bg.png",  # NOT /assets/...
       }],
       "audio": {
           "narration": {"src": "assets/audio/narration.mp3"},
           "music": {"src": "assets/music/background.mp3"},
       }
   }
   ```

3. Run Remotion render:
   ```bash
   cd remotion-composer
   npx remotion render src/index.tsx Explainer output.mp4 \
     --props=props.json --width=1080 --height=1920
   ```

## Verification

After fix, Remotion logs show no asset errors:
```
Rendered 0/3180
Rendered 1/3180, time remaining: ...
```
No `Not allowed to load local resource` messages = success.

## Debugging: The "from prop NaN" Red Herring

When image assets fail to load, Remotion sometimes reports a misdirecting error:

```
TypeError: The "from" prop of a sequence must be finite, but got NaN.
```

This error fires on **every** parallel render tab under the hood, even though the actual root cause is the image loading failure. Do not chase timing values in your props — the `calculateMetadata` function and Sequence timings are fine. Instead:

1. First test with **text-only cuts** (no `source`, no `backgroundImage`, no audio). If it renders, the timing/cuts are valid.
2. Add images one at a time. When the error changes from "from prop NaN" to "Error loading image with src: file:///...", you've confirmed it's a file:/// path issue.
3. Apply the public/ directory fix above.

## Incremental Remotion Testing Pattern

Use this methodical approach to isolate Explainer composition issues:

| Step | Props | Expected |
|------|-------|----------|
| 1 | Text card only, no audio | Renders instantly |
| 2 | Multiple text cards | Sequences/time-slicing work |
| 3 | Text cards + captions | Overlay layer works |
| 4 | Text cards + audio narration | Audio layer works |
| 5 | Single image via public/ relative path | ImageScene renders |
| 6 | Multiple images + all layers | Full composition works |

Test with `--concurrency 1` to avoid confusing parallel error spam across tabs.

## Remotion Render on Windows: subprocess Resolution

When invoking Remotion from Python (not the terminal tool), `subprocess.run(["npx", ...])` **fails** on Windows because `npx` is a Unix shell script, not a Windows executable. The actual entry point is `npx.cmd`:

```python
import subprocess, sys, os

def run_remotion(args: list[str], cwd: str):
    """Run npx.cmd on Windows, npx elsewhere."""
    npx = "npx.cmd" if sys.platform == "win32" else "npx"
    subprocess.run([npx, *args], cwd=cwd, check=True)
```

Alternatively, the Hermes `terminal()` tool (bash/MSYS) resolves `npx` correctly — use it instead of `subprocess.run` when running Remotion from an agent context.

Error signature of incorrect subprocess resolution:
```
%1 is not a valid Win32 application.
```

## Alternative: `file://` Chrome Flag

If for some reason you MUST use absolute paths, Remotion supports the `--disable-web-security` flag via the `CHROMIUM_FLAGS` env var:
```bash
set CHROMIUM_FLAGS=--disable-web-security
```
But this is insecure for production use and not recommended.
