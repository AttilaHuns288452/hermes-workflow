---
name: retro-video-effects
description: "Apply vintage/retro aesthetic effects (VHS, 90s, CRT, radio-style) to AI-generated or stock footage videos using MoviePy v2 and ffmpeg. Post-process any video pipeline output for a period-correct look."
version: 1.2.0
tags:
  - vhs
  - retro
  - 90s
  - crt
  - vintage
  - video effects
  - moviepy
triggers:
  - "make this look like the 90s"
  - "vhs aesthetic"
  - "retro video effect"
  - "vintage look"
  - "old tv style"
  - "radio style video"
  - "crt effect"
  - "apply film grain"
  - "sepia tone video"
---

# Retro Video Effects — VHS / 90s / CRT Aesthetic

## Role
Apply vintage period-correct visual effects to any short-form video content (AI-generated, stock footage, or recorded). The pipeline: **source video → sepia/color grade → film grain → vignette → scanlines → CRT artifacts → output**. Works as a post-processing layer on top of any video generation pipeline (MoneyPrinterTurbo, Runway, Pika, or raw Pexels clips).

> ⚠️ **PERFORMANCE WARNING**: The MoviePy/numpy per-frame approach below is **CPU-bound and slow** (~30 min for 80s video at 30fps for sepia+grain+vignette). For production use, prefer the **ffmpeg Fast Path** which runs in ~3 min for the same output using native filters. See the [Performance Guide](#performance-guide) for when to choose each.

## Class Scope
This skill covers the **visual post-processing** of short-form videos (15s–120s, vertical or horizontal). It does NOT cover:
- **Video generation** (see `media/money-printer-turbo` for AI short video generation)
- **Animation** (see `creative/manim-video` for math/animation)
- **ComfyUI workflows** (see `creative/comfyui` for node-based image/video gen)

## Prerequisites
- **MoviePy v2** (2.x — API differs significantly from v1): `pip install moviepy`
- **NumPy**: `pip install numpy`
- **ffmpeg**: Must be in PATH
- **Python**: 3.10+
- **Windows note**: Git-bash terminal, Python venv at `.venv/Scripts/activate`

## MoviePy v2 API Reference (Critical — Differs from v1)

| Operation | MoviePy v1 | MoviePy v2 |
|-----------|-----------|-----------|
| Import | `from moviepy.editor import *` | `from moviepy import *` |
| Resize | `.resize((w, h))` | `.resized((w, h))` |
| Subclip | `.subclip(t1, t2)` | `.subclipped(t1, t2)` |
| Duration | `.set_duration(t)` | `.with_duration(t)` |
| Audio | `.set_audio(clip)` | `.with_audio(clip)` |
| Frame func | `.fl_image(func)` | `.transform(lambda gf, t: func(gf(t)))` |
| Concat clips | `concatenate_videoclips([...])` | `concatenate_videoclips([...])` |
| Composite | `CompositeVideoClip([...])` | `CompositeVideoClip([...])` |
| Position | `.set_position(...)` | `.with_position(...)` |

**Key API changes:**
- `.fl_image(func)` does NOT exist in v2 — use `.transform(lambda gf, t: func(gf(t)))`
- `ColorClip(size, color, duration)` works, but `.fl_image()` is also gone on ColorClip — use `.transform()` with a lambda that ignores time
- `write_videofile` signature is the same

## Core Effects Library

### 1. Sepia Tone
Classic vintage photograph look via weighted RGB transformation:
```python
def sepia_frame(frame):
    r = frame[:,:,0].astype(np.float64)
    g = frame[:,:,1].astype(np.float64)
    b = frame[:,:,2].astype(np.float64)
    tr = np.clip(0.393 * r + 0.769 * g + 0.189 * b, 0, 255)
    tg = np.clip(0.349 * r + 0.686 * g + 0.168 * b, 0, 255)
    tb = np.clip(0.272 * r + 0.534 * g + 0.131 * b, 0, 255)
    return np.stack([tr, tg, tb], axis=2).astype(np.uint8)
```

**Variation:** Colder sepia (desaturated, blue-tinted shadows) for a bleach bypass / documentary look — reduce `tb` weight.

### 2. Film Grain (Analog Noise)
Random noise + occasional scratch lines:
```python
def grain_frame(frame, intensity=8, scratch_chance=0.015):
    noise = np.random.randint(-intensity, intensity, frame.shape, dtype=np.int16)
    grainy = frame.astype(np.int16) + noise * 2
    # Random scratch line across image
    if np.random.random() < scratch_chance:
        row = np.random.randint(0, frame.shape[0])
        col = np.random.randint(0, max(1, frame.shape[1] - 50))
        grainy[row, col:col+50] = 255
    return np.clip(grainy, 0, 255).astype(np.uint8)
```

**Adjust:**
- `intensity=4` (light grain, 90s TV) to `intensity=15` (heavy grain, 70s film)
- `scratch_chance=0.005` (subtle) to `scratch_chance=0.05` (damaged reel)

### 3. Vignette (Darkened Edges)
Simulates lens falloff or CRT burn-in:
```python
def vignette_frame(frame, strength=0.4, falloff=0.7):
    h, w = frame.shape[:2]
    X, Y = np.meshgrid(np.linspace(-1, 1, w), np.linspace(-1, 1, h))
    mask = 1.0 - strength * (X**2 + Y**2) ** falloff
    mask = np.clip(mask, 0.2, 1.0)[:, :, np.newaxis]
    return (frame * mask).astype(np.uint8)
```

**Adjust:**
- `strength=0.3` (subtle) to `strength=0.6` (heavy vignette, fisheye)
- `falloff=0.5` (sharp circle) to `falloff=1.0` (smooth gradient)

### 4. Scanlines (CRT Display)
Every Nth row dimmed:
```python
def scanlines_frame(frame, interval=3, dim_factor=0.80):
    frame[0::interval] = (frame[0::interval] * dim_factor).astype(np.uint8)
    return frame
```

**Adjust:**
- `interval=2` (thick scanlines, obvious CRT) to `interval=4` (subtle)
- `dim_factor=0.70` (heavy) to `dim_factor=0.90` (light)

**Note:** Must be applied as a separate overlay ColorClip in a CompositeVideoClip to avoid compounding across transform chains.

### 5. Color Flicker (CRT Power Fluctuation)
Simulates unstable analog signal:
```python
def flicker_frame(frame, flicker_strength=0.03):
    # Random brightness fluctuation
    flicker = 1.0 + flicker_strength * (np.random.random() - 0.5) * 2
    return np.clip(frame * flicker, 0, 255).astype(np.uint8)
```

**Adjust:**
- `flicker_strength=0.02` (subtle) to `flicker_strength=0.08` (obvious power sag)

### 6. VHS Tracking Error
Horizontal offset bands:
```python
def tracking_error_frame(frame, chance=0.008, max_shift=20):
    if np.random.random() < chance:
        shift = np.random.randint(5, max_shift)
        band_start = np.random.randint(0, frame.shape[0] - 20)
        band_end = band_start + np.random.randint(10, 40)
        shifted = np.roll(frame[band_start:band_end], shift, axis=1)
        frame[band_start:band_end] = shifted[:band_end - band_start]
    return frame
```

## Applying Effects (MoviePy v2)

### Per-Clip (Every frame processed)
```python
from moviepy import *
import numpy as np

clip = VideoFileClip("input.mp4").resized((1080, 1920))

# Chain multiple effects as .transform() calls
clip = clip.transform(lambda gf, t: sepia_frame(gf(t)))
clip = clip.transform(lambda gf, t: grain_frame(gf(t), intensity=8))
clip = clip.transform(lambda gf, t: vignette_frame(gf(t), strength=0.4))
```

### Scanline Overlay (Separate layer — avoids compounding)
```python
def scanline_fn(frame):
    frame[0::3] = (frame[0::3] * 0.80).astype(np.uint8)
    return frame

scanline_overlay = ColorClip((1080, 1920), color=(0, 0, 0), duration=clip.duration)
scanline_overlay = scanline_overlay.transform(lambda gf, t: scanline_fn(gf(t)))

final = CompositeVideoClip([clip, scanline_overlay])
final = final.with_duration(clip.duration).with_audio(clip.audio)
```

## ffmpeg Fast Path (Recommended for Production)

**10-30x faster than MoviePy/numpy for the same effects.** Use ffmpeg native filters when:
- You have 3+ clips to concatenate (common for AI-generated videos)
- Your video is 60s+ at 30fps
- You need reliable encoding (no BrokenPipeError)
- You want single-pass encode (no intermediate files)

**MoviePy/numpy is only better when:**
- You need frame-dependent randomness per effect (e.g. per-frame grain seed variation)
- You're doing a proof-of-concept on a very short clip (<15s)
- You need custom effects not expressible in ffmpeg filter chains

### How It Works

Two strategies for joining multiple clips before applying VHS filters:

| Strategy | Speed | Use Case |
|----------|-------|----------|
| **Single filter pass** (concat demuxer) | Fastest (~3 min for 80s) | All clips in a single directory, same resolution |
| **Per-clip filter_complex** (17× filter chains + concat) | Slower (~5-6 min) | Clips need per-clip trimming or different resolutions |

### Strategy A: Concat Demuxer + Single Filter Pass (Fastest)

```bash
# 1. Create concat file
echo "ffconcat version 1.0" > clips.txt
echo "file 'clip1.mp4'" >> clips.txt
echo "file 'clip2.mp4'" >> clips.txt
# ... all clips

# 2. Single filter pass - VHS effects applied ONCE to concatenated video
ffmpeg -y -f concat -safe 0 -i clips.txt -i audio.mp3 \
  -filter_complex '
    [0:v]
    colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131:0,  # sepia
    eq=saturation=0.3:contrast=1.1:brightness=-0.03,                     # desaturate + contrast
    vignette=PI/5,                                                       # dark corners
    scale=1080:1920:force_original_aspect_ratio=decrease,                # fit vertical
    pad=1080:1920:(ow-iw)/2:(oh-ih)/2                                    # letterbox
    [vout]
  ' \
  -map '[vout]' -map '1:a' \
  -c:v libx264 -c:a aac -pix_fmt yuv420p -r 30 \
  -preset veryfast -b:v 4000k -shortest \
  output.mp4
```

**Critical notes on concat demuxer:**
- All clips must have the **same resolution and codec** (Pexels clips from the same source usually do)
- The `-f concat` demuxer reads files sequentially — no per-clip trimming possible here
- High `dup` counts in ffmpeg output are normal (PTS smoothing between clips)
- File paths in the concat list must not contain `:` characters or use absolute paths in quotes

### Strategy B: Per-Clip filter_complex + Concat (More Control)

For per-clip trimming, use individual `-i` inputs and per-clip filter chains:

```bash
ffmpeg -y \
  -i clip1.mp4 -i clip2.mp4 ... -i clip17.mp4 -i audio.mp3 \
  -filter_complex '
    [0:v] colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131:0,
          eq=saturation=0.3:contrast=1.1:brightness=-0.03,
          vignette=PI/5,
          setpts=PTS-STARTPTS,
          scale=1080:1920:force_original_aspect_ratio=decrease,
          pad=1080:1920:(ow-iw)/2:(oh-ih)/2 [v0];
    [1:v] ...same chain... [v1];
    ...
    [v0][v1]...[v16] concat=n=17:v=1:a=0 [vout]
  ' \
  -map '[vout]' -map '17:a' \
  -c:v libx264 -preset veryfast -b:v 4000k -shortest \
  output.mp4
```

Proportional timing (word-count based):
```python
total_words = sum(len(s.split()) for s in text_segments)
durations = [(len(s.split()) / total_words) * audio_dur for s in text_segments]
# Trim each clip to its duration before feeding into ffmpeg
```

## Two-Pass Production Pipeline (Discovered in 2026-06-16 Session)

When applying heavy VHS effects to many clips, the **two-pass approach** is more reliable and debuggable than a single filter_complex:

```
PASS 1: Raw concat (no effects)
  - Trim each clip to segment duration (word-count proportional)
  - Scale + pad to 1080×1920
  - Concat all clips + overlay audio
  - Output: raw_concat.mp4 (~70MB for 80s)
  - Time: ~15-20 seconds

PASS 2: VHS effects on one file
  - Apply sepia, vintage curves, noise, vignette, scanlines
  - Single file input = simpler filter graph
  - Time: ~3-5 minutes
```

**Why two-pass is better than single-pass filter_complex:**
| Factor | Single Pass (17 clips) | Two-Pass |
|--------|----------------------|----------|
| Filter graph size | 17× filter chains + concat + overlay | 1 chain |
| Failure mode | Hard to debug which clip caused it | Always clear |
| Retry speed | Must re-concat all clips | Re-apply effects only |
| Memory | All 17 clips decoded simultaneously | 1 clip at a time |

**Working fallback chain (when heavy geq noise is too slow):**
```
PASS 2 tries heavy → if timeout/heavy, fallback to:
colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131,
curves=preset=vintage,
noise=alls=6:allf=t+u,
vignette,
drawbox=x=0:y=0:w=iw:h=1:color=white@0.08:t=fill,
drawbox=x=0:y=ih-1:w=iw:h=1:color=white@0.08:t=fill
```
This light chain works in ~3-4 min for 80s footage vs the heavy `geq` chain which can timeout at 5+ min.

### ffmpeg Filter Chains Reference

| Effect | ffmpeg Filter | Parameters |
|--------|--------------|------------|
| **Sepia** | `colorchannelmixer` | `.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131:0` |
| **Desaturate** | `eq=saturation=0.3` | 0.0=grayscale, 0.3=vintage faded, 1.0=full color |
| **Contrast** | `eq=contrast=1.1` | 1.0=normal, 1.1-1.3=increased, 0.8-0.9=faded |
| **Vignette** | `vignette=PI/5` | `PI/5`=subtle, `PI/3`=moderate, `PI/2`=heavy (do NOT use `max_eval` — removed in recent ffmpeg) |
| **Film Grain** | `noise=alls=N:allf=t+u` | `alls=2-4`=light (recommended, fast), `alls=6`=moderate (production-reliable, ~4 min for 80s), `alls=8-12`=heavy (SLOW — test before production) |
| **Scanlines** | `drawgrid` | `drawgrid=w=1080:h=3:t=fill:color=black@0.15:y0=1` |
| **Color Flicker** | No native ffmpeg — use MoviePy for this | — |
| **Tracking Errors** | No native ffmpeg — use MoviePy for this | — |

### ⚡ Performance: noise Filter is the Bottleneck

The `noise=alls=N:allf=t+u` filter with `alls>=8` makes ffmpeg **3-5x slower**. On 80s 30fps:
| noise level | Speed | Render time |
|-------------|-------|-------------|
| None | ~0.5x | ~3 min |
| `alls=3` | ~0.3x | ~4.5 min |
| `alls=12:allf=t+u` | ~0.1x | ~15-30 min |

**Recommendation:** Apply noise as a **static overlay** (pre-generated grainy PNG via ImageMagick or Python) rather than per-frame filter. Or accept the grain-free look with just sepia + vignette + scanlines.

### Python Wrapper for ffmpeg Approach

See `references/ffmpeg-vhs-filters.md` for a complete Python script template that:
1. Picks the N freshest clips from a cache directory
2. Measures audio duration
3. Builds concat file or per-clip filter_complex
4. Applies VHS filter chain
5. Overlays audio
6. Outputs 1080×1920 @ 30fps mp4

## Performance Guide

| Method | 60s video | 80s video | Pros | Cons |
|--------|-----------|-----------|------|------|
| **ffmpeg concat + single filter** | ~2 min | ~3 min | Fastest, reliable | No per-frame randomness |
| **ffmpeg per-clip filter_complex** | ~4 min | ~5-6 min | Per-clip trimming | More complex filter graph |
| **MoviePy numpy (sepia+grain+vignette)** | ~15-25 min | ~30 min | Any effect possible | CPU-bound, videos must fit in RAM |
| **MoviePy (effects disabled, trim+concat only)** | ~2 min | ~3 min | Good for proof-of-concept | — |

## Integration with MoneyPrinterTurbo Pipeline

The typical workflow: **generate video → apply retro effects.**

### TTS Options for VHS/Retro Videos

| TTS Source | Where | Quality | Speed | Best For |
|------------|-------|---------|-------|----------|
| **Edge TTS** (Turbo) | Built-in | Good, detectable AI | Instant | Quick drafts |
| **ElevenLabs Adam** | HTTP API | Gold standard | ~3s per story | Production monetized content |
| **KittenTTS** (V2) | MoneyPrinterV2 venv | Very good, natural | ~10-20s per story | Free, offline, solo creator |

KittenTTS lives in MoneyPrinterV2's venv (`~/Documents/Projects/MoneyPrinterV2/venv`), model `KittenML/kitten-tts-mini-0.8`, voice `"Jasper"`. First call downloads ~1.5 GB model from HuggingFace.

```python
from kittentts import KittenTTS as KittenModel
import soundfile as sf
model = KittenModel("KittenML/kitten-tts-mini-0.8")
audio = model.generate("script text", voice="Jasper")
sf.write("output.wav", audio, 24000)
# Convert to MP3 for ffmpeg: ffmpeg -i output.wav -codec:a libmp3lame -b:a 192k output.mp3
```

### Step 1: Generate Source Video (MoneyPrinterTurbo)
```bash
# Generate 90s-themed Pexels clips and ElevenLabs audio
# (See media/money-printer-turbo skill for full pipeline)
python run_pipeline.py   # → downloads fresh Pexels clips per script term
```

### Step 2: Compose with VHS Effects
```python
# 17 clips + ElevenLabs audio → MoviePy composite with all effects
for fpath in clip_paths:
    clip = (VideoFileClip(fpath)
            .resized((1080, 1920))
            .subclipped(0, segment_duration))
    clip = apply_vhs(clip)  # sepia + grain + vignette
    clips.append(clip)

# Overlay scanlines
scan = ColorClip((1080, 1920), color=(0, 0, 0), duration=audio_dur)
scan = scan.transform(lambda gf, t: scanline_fn(gf(t)))

final = CompositeVideoClip([concatenate_videoclips(clips, method="compose"), scan])
final = final.with_duration(audio_dur).with_audio(audio_clip)
final.write_videofile("output.mp4", codec="libx264", fps=30, bitrate="5000k")
```

### Step 3: Output Specs
- **Resolution**: 1080×1920 (vertical 9:16 for TikTok/Shorts/Reels)
- **FPS**: 30
- **Codec**: libx264
- **Audio**: aac
- **Bitrate**: 4000-6000k

## Full VHS Effect Pipeline (Copy-Paste Template)

### Option A: ffmpeg (Production — Fast, Recommended)

```python
import os, subprocess

AUDIO = "voice.mp3"
OUTPUT = "vhs_output.mp4"
CACHE = "cache_videos/"

# Pick 17 freshest clips
all_vids = sorted(
    [os.path.join(CACHE, f) for f in os.listdir(CACHE) if f.endswith('.mp4')],
    key=lambda p: os.path.getmtime(p), reverse=True
)[:17]
all_vids.reverse()

# Get audio duration
dur = float(subprocess.check_output(
    ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
     '-of', 'default=noprint_wrappers=1:nokey=1', AUDIO], text=True).strip())

# Concat file
with open('_concat.txt', 'w') as f:
    f.write("ffconcat version 1.0\n")
    for v in all_vids:
        f.write(f"file '{v}'\n")

# One-pass VHS filter
vhs = (
    "colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131:0,"
    "eq=saturation=0.3:contrast=1.1:brightness=-0.03,"
    "vignette=PI/5,"
    "scale=1080:1920:force_original_aspect_ratio=decrease,"
    "pad=1080:1920:(ow-iw)/2:(oh-ih)/2"
)

subprocess.run([
    'ffmpeg', '-y',
    '-f', 'concat', '-safe', '0', '-i', '_concat.txt',
    '-i', AUDIO,
    '-filter_complex', f'[0:v]{vhs}[vout]',
    '-map', '[vout]', '-map', '1:a',
    '-c:v', 'libx264', '-c:a', 'aac', '-pix_fmt', 'yuv420p',
    '-r', '30', '-preset', 'veryfast', '-b:v', '4000k',
    '-shortest', OUTPUT
], check=True)
```

### Option B: MoviePy (Development / Custom Effects)

```python
from moviepy import *
import numpy as np

def apply_vhs(clip):
    clip = clip.transform(lambda gf, t: sepia_frame(gf(t)))
    clip = clip.transform(lambda gf, t: grain_frame(gf(t)))
    clip = clip.transform(lambda gf, t: vignette_frame(gf(t)))
    clip = clip.transform(lambda gf, t: flicker_frame(gf(t)))
    return clip

def sepia_frame(frame):
    r, g, b = frame[:,:,0].astype(np.float64), frame[:,:,1].astype(np.float64), frame[:,:,2].astype(np.float64)
    tr = np.clip(0.393*r + 0.769*g + 0.189*b, 0, 255)
    tg = np.clip(0.349*r + 0.686*g + 0.168*b, 0, 255)
    tb = np.clip(0.272*r + 0.534*g + 0.131*b, 0, 255)
    return np.stack([tr, tg, tb], axis=2).astype(np.uint8)

def grain_frame(frame):
    noise = np.random.randint(-8, 8, frame.shape, dtype=np.int16)
    grainy = frame.astype(np.int16) + noise * 2
    if np.random.random() < 0.015:
        row, col = np.random.randint(0, frame.shape[0]), np.random.randint(0, max(1, frame.shape[1]-50))
        grainy[row, col:col+50] = 255
    return np.clip(grainy, 0, 255).astype(np.uint8)

def vignette_frame(frame):
    h, w = frame.shape[:2]
    X, Y = np.meshgrid(np.linspace(-1, 1, w), np.linspace(-1, 1, h))
    mask = np.clip(1.0 - 0.4 * (X**2 + Y**2)**0.7, 0.2, 1.0)[:, :, np.newaxis]
    return (frame * mask).astype(np.uint8)

def flicker_frame(frame):
    flicker = 1.0 + 0.03 * (np.random.random() - 0.5) * 2
    return np.clip(frame * flicker, 0, 255).astype(np.uint8)

def scanline_fn(frame):
    frame[0::3] = (frame[0::3] * 0.80).astype(np.uint8)
    return frame
```

## Retro Aesthetic Styles Reference

| Style | Effects | Best For |
|-------|---------|----------|
| **90s Radio / Documentary** | Sepia + Light grain + Vignette + Subtle scanlines | Financial storytelling, educational |
| **VHS Camcorder** | Slight blue shift + Grain + Tracking errors + Heavy scanlines | Nostalgia, personal storytelling |
| **CRT Broadcast** | Color flicker + Scanlines + Vignette | Gaming, retro-tech content |
| **Bleach Bypass / Film** | Desaturated + Heavy grain + No scanlines | Cinematic drama, high-production feel |
| **Damaged VHS** | Tracking errors + Heavy grain + Color flicker + Random static lines | Forgotten tapes aesthetic, eerie narratives |

## Windows Pitfalls

### MoviePy v2 Import
Use `from moviepy import *` — the old `from moviepy.editor import *` does NOT exist in v2.

### Transform API
`.fl_image(func)` is gone. Use `.transform(lambda gf, t: func(gf(t)))` where `gf` is a `get_frame` callable and `t` is time in seconds.

### Seed for Reproducibility
`np.random.seed(0)` before rendering if you need deterministic grain patterns. Omit for true random.

### Performance: MoviePy Per-Frame is CPU-Bound

Frame-by-frame numpy ops are CPU-bound. For a 60s video at 30fps:
- 4 effects (sepia + grain + vignette + flicker) × 1800 frames = ~15-25 min render time
- Reduce scope: skip flicker and grain for <10 min
- Use ffmpeg Fast Path (see above) for <5 min production renders
- Use `bitrate="5000k"`, `preset="fast"`, `threads=2` in `write_videofile`

### ffmpeg Concat Demuxer Dup Counts

High `dup` counts (e.g. `dup=498338`) in ffmpeg output are **normal** when using the concat demuxer with variable-duration clips. The concat protocol reads clips sequentially and reports duplicate PTS values during transitions. These dups are **dropped during encoding** and do NOT affect the output video quality. They just make the progress output look alarming.

### ffmpeg Concat Demuxer Path Restrictions

On Windows, `-f concat` with `ffconcat version 1.0` files:
- File paths must not contain Windows drive letters at the start when inside quotes — use POSIX-style paths or escape properly
- The `-safe 0` flag is REQUIRED for absolute paths
- If paths contain `:` characters (like `C:\...`), wrap the entire path in single quotes in the concat file

## Related Skills
- `media/money-printer-turbo` — AI short video generation (source footage for this skill)
- `creative/manim-video` — Math animations (different visual direction)
- `creative/comfyui` — Node-based image/video generation (can generate retro-styled image sequences)
