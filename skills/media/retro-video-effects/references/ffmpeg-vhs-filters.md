# ffmpeg VHS Filter Chains — Complete Reference

> Concrete ffmpeg filter commands and Python wrappers for applying retro/VHS/90s effects to short-form video. **10-30x faster than MoviePy/numpy per-frame processing.**

## Quick Reference: Single-Filter Effects

### Sepia Tone
```bash
ffmpeg -i input.mp4 -vf "colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131:0" output.mp4
```

### Vintage Curves (vs eq=)
Two approaches achieve the old-photo look — **vintage curves** often look better than manual `eq`:

| Method | When to use |
|--------|-------------|
| `curves=preset=vintage` | **Prefer this** — warmer, more organic \"old TV\" feel |
| `eq=saturation=0.3:contrast=1.1` | Only when numerical precision is needed |

### Film Grain (Light)
```bash
ffmpeg -i input.mp4 -vf "noise=alls=4" output.mp4
# alls=1-4 = light (fast), alls=6 = moderate (acceptable at ~8min for 80s), alls=8-12 = heavy (SLOW - avoid for production, 15+ min for 80s risks timeout)
```

### Film Grain (Heavy, Static Overlay Approach)
```bash
# Generate grain PNG once, then overlay (much faster than per-frame noise filter)
# Requires ImageMagick installed:
convert -size 1080x1920 plasma: -channel R -evaluate sin 40% grain.png
ffmpeg -i input.mp4 -i grain.png -filter_complex "[0:v][1:v]overlay=format=auto:mode=softlight" output.mp4
```

### Vignette
```bash
ffmpeg -i input.mp4 -vf "vignette=PI/5" output.mp4
# PI/5 = subtle, PI/3 = moderate, PI/2 = heavy
# Note: max_eval option was REMOVED in recent ffmpeg versions - omit it
```

### Desaturate + Contrast
```bash
ffmpeg -i input.mp4 -vf "eq=saturation=0.3:contrast=1.1:brightness=-0.03" output.mp4
# saturation=0.0 = grayscale, 0.3 = faded vintage, 1.0 = normal
# contrast=0.8 = washed out, 1.1 = punchy, 1.3 = harsh
```

### Scanlines (CRT Effect)
```bash
ffmpeg -i input.mp4 -vf "drawgrid=w=1080:h=3:t=fill:color=black@0.15:y0=0" output.mp4
# h=3 = 3px rows, color=black@0.15 = 15% dimming
# For horizontal videos, use w instead of h: w=3:h=ih
```

### Composite: 90s Radio Style (All Effects)
```bash
ffmpeg -i input.mp4 -i audio.mp3 \
  -filter_complex "
    [0:v]
    colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131:0,
    eq=saturation=0.3:contrast=1.1:brightness=-0.03,
    vignette=PI/5,
    scale=1080:1920:force_original_aspect_ratio=decrease,
    pad=1080:1920:(ow-iw)/2:(oh-ih)/2
  [vout]
  " \
  -map '[vout]' -map '1:a' \
  -c:v libx264 -preset veryfast -b:v 4000k -pix_fmt yuv420p \
  -shortest output.mp4
```

---

## Complete Python Script: Multi-Clip VHS Builder

This script takes N cached Pexels clips, concatenates them with proportional timing, applies VHS effects, and overlays ElevenLabs audio.

```python
"""build_vhs_ffmpeg.py — Production VHS video builder."""

import os, subprocess

ROOT = r"C:\path\to\project"
CACHE = r"C:\path\to\cache_videos"
AUDIO = r"C:\path\to\elevenlabs_audio.mp3"
OUTPUT = os.path.join(ROOT, "vhs_output.mp4")

# Pick N freshest clips (adjust N as needed)
all_vids = sorted(
    [os.path.join(CACHE, f) for f in os.listdir(CACHE) if f.endswith('.mp4')],
    key=lambda p: os.path.getmtime(p), reverse=True
)[:17]
all_vids.reverse()

# Get audio duration for -shortest flag
dur = float(subprocess.check_output(
    ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
     '-of', 'default=noprint_wrappers=1:nokey=1', AUDIO], text=True).strip())
print(f"Audio: {dur:.1f}s | Clips: {len(all_vids)}")

# Method 1: Concat demuxer + single filter pass (fastest)
with open('_concat.txt', 'w') as f:
    f.write("ffconcat version 1.0\n")
    for v in all_vids:
        f.write(f"file '{v}'\n")

cmd = [
    'ffmpeg', '-y',
    '-f', 'concat', '-safe', '0', '-i', '_concat.txt',
    '-i', AUDIO,
    '-filter_complex',
    '[0:v] '
    'colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131:0,'
    'eq=saturation=0.3:contrast=1.1:brightness=-0.03,'
    'vignette=PI/5,'
    'scale=1080:1920:force_original_aspect_ratio=decrease,'
    'pad=1080:1920:(ow-iw)/2:(oh-ih)/2'
    '[vout]',
    '-map', '[vout]',
    '-map', '1:a',
    '-c:v', 'libx264', '-c:a', 'aac',
    '-pix_fmt', 'yuv420p', '-r', '30',
    '-preset', 'veryfast', '-b:v', '4000k',
    '-shortest', OUTPUT
]

print("Encoding...")
subprocess.run(cmd, check=True)
size = os.path.getsize(OUTPUT) / 1024 / 1024
print(f"DONE: {size:.1f} MB — {OUTPUT}")
```

---

## Method 2: Per-Clip filter_complex (With Trimming)

Use when each clip needs different trim times (e.g. word-count proportional timing).

```python
import os, subprocess

# Text segments and word-count proportions
text_segments = [
    "What if the wealthiest person you know...",
    "There is a quiet pattern among people who build generational wealth.",
    # ... 18 total segments
]

total_words = sum(len(s.split()) for s in text_segments)
durations = [(len(s.split()) / total_words) * audio_dur for s in text_segments]

# Build per-clip filter chain
parts = []
for i in range(len(clips)):
    parts.append(
        f"[{i}:v] "
        f"trim=0:{durations[i]},setpts=PTS-STARTPTS,"
        f"colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131:0,"
        f"eq=saturation=0.3:contrast=1.1:brightness=-0.03,"
        f"vignette=PI/5,"
        f"scale=1080:1920:force_original_aspect_ratio=decrease,"
        f"pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1 "
        f"[v{i}];"
    )

parts.append(''.join(f'[v{i}]' for i in range(len(clips))) +
             f' concat=n={len(clips)}:v=1:a=0 [vout]')

inputs = []
for vp in clips:
    inputs.extend(['-i', vp])
inputs.extend(['-i', AUDIO])

cmd = ['ffmpeg', '-y'] + inputs + [
    '-filter_complex', ''.join(parts),
    '-map', '[vout]', '-map', f'{len(clips)}:a',
    '-c:v', 'libx264', '-c:a', 'aac',
    '-pix_fmt', 'yuv420p', '-r', '30',
    '-preset', 'veryfast', '-b:v', '4000k',
    '-shortest', OUTPUT
]
subprocess.run(cmd, check=True)
```

---

## VHS Effects Style Matrix

| Style | ffmpeg filter chain | Best for |
|-------|---------------------|----------|
| **90s Radio / Documentary (curves)** | `colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131:0,curves=preset=vintage,vignette=PI/5` | **Prefer this** — warmer organic vintage feel |
| **90s Radio / Documentary (eq)** | `colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131:0,eq=saturation=0.3:contrast=1.1:brightness=-0.03,vignette=PI/5` | When numerical control needed |
| **VHS Camcorder** | `eq=saturation=1.2:hue=-0.1:contrast=0.9,noise=alls=6,eq=brightness=0.05` | Nostalgia, home video aesthetic |
| **Bleach Bypass** | `colorchannelmixer=.299:.587:.114:0:.299:.587:.114:0:.299:.587:.114:0,eq=contrast=1.3` | High-contrast filmic look |
| **1970s Film** | `colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131:0,noise=alls=4,vignette=PI/4` | Retro documentary |
| **Old TV Broadcast** | `eq=saturation=0.0:contrast=1.2,brightness=-0.05,vignette=PI/3` | Found footage / archival aesthetic |

---

## Speed Benchmarks (80s video, 30fps, 17 clips, Windows 10 i7-12700H)

| Approach | Effects | Time |
|----------|---------|------|
| ffmpeg concat demuxer single pass | Sepia + desaturate + vignette | **~3 min** |
| ffmpeg concat demuxer single pass | Same + noise=alls=3 | ~4.5 min |
| ffmpeg concat demuxer single pass | Same + noise=alls=6 | ~8 min |
| ffmpeg per-clip filter_complex (17×) | Sepia + desaturate + vignette | ~5-6 min |
| ffmpeg two-pass (raw concat → VHS) | curves=vintage + noise=alls=6 + vignette | **~4 min** (15s concat + 3:45 VHS) |
| ffmpeg two-pass (raw concat → VHS) | curves=vintage + vignette (no noise) | **~3.5 min** |
| MoviePy numpy per-frame | Sepia + grain + vignette + flicker | ~30 min |
| MoviePy numpy per-frame | Sepia + vignette only | ~15 min |

**Two-pass is the most reliable production approach:** it avoids filter graph failures, lets you re-apply VHS settings without re-downloading clips, and the raw concat can be re-used for different effect styles.
