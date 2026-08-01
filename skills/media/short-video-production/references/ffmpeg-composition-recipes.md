# FFmpeg Composition Recipes

Reference patterns for composing short-form videos from images + audio + captions.

## Standard Slidehow (Image + Narration + Captions)

Used for: 7-facts psychology video, TikTos, any numbered-list explainer.

```python
import subprocess

# images: list of (path, segment_duration)
# narration: path to TTS mp3

cmd = ["ffmpeg", "-y"]
for img_path, dur in segments:
    cmd.extend(["-loop", "1", "-i", str(img_path)])
cmd.extend(["-i", str(narration_path)])

filters, labels = [], []
for i, (_, dur) in enumerate(segments):
    filters.append(
        f"[{i}:v]"
        f"scale=1080:1920:force_original_aspect_ratio=increase,"
        f"crop=1080:1920,"
        f"setsar=1,fps=30,format=yuv420p,"
        f"trim=duration={dur},setpts=PTS-STARTPTS[v{i}]"
    )
    labels.append(f"[v{i}]")

filters.append(f"{''.join(labels)}concat=n={len(labels)}:v=1:a=0[base]")"

# Subtitles filter — CRITICAL: use relative SRT path on Windows
filters.append(
    f"[base]subtitles=captions.srt"
    f":force_style="
    f"'FontName=Arial,FontSize=28,"
    f"PrimaryCol=&H00FFFFFF,OutlineCol=&H00000000,"
    f"BorderStyle=3,Outline=2,Shadow=1,"
    f"Alignment=2,MarginV=120'[vid]"
)

cmd.extend(["-filter_complex", ";".join(filters)])
cmd.extend(["-map", "[vid]", "-map", f"{len(segments)}:a"])
cmd.extend(["-c:v", "libx264", "-preset", "medium", "-crf", "23"])
cmd.extend(["-c:a", "aac", "-b:a", "192k"])
cmd.extend(["-pix_fmt", "yuv420p", "-shortest"])
cmd.append("output.mp4")

subprocess.run(cmd, capture_output=True, text=True, timeout=600"
```

## Quick Composition Script (shell)

```bash
cd /c/Users/Attila/OpenMontage/projects/tiktok-viral && \
ffmpeg -y \
  -loop 1 -t 21.5 -i images/01_spotlight.png \
  -loop 1 -t 10 -i images/02_peak_end.png \
  -i audio/narration.mp3 \
  -filter_complex "\
    [0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,\
          setsar=1,fps=30,format=yuv420p,trim=duration=21.5,setpts=PTS-STARTPTS[v0];\
    [1:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,\
          setsar=1,fps=30,format=yuv420p,trim=duration=10,setpts=PTS-STARTPTS[v1];\
    [v0][v1]concat=n=2:v=1:a=0[base];\
    [base]subtitles=captions.srt:force_style='FontName=Arial,FontSize=28,\
          PrimaryCol=&H00FFFFFF,OutlineCol=&H00000000,BorderStyle=3,\
          Outline=2,Shadow=1,Alignment=2,MarginV=120'[vid]" \
  -map "[vid]" -map "2:a" \
  -c:v libx264 -preset medium -crf 23 -c:a aac -b:a 192k \
  -pix_fmt yuv420p -shortest output.mp4
```

## SRT Timing Calculator

Given a narration of length `total_dur` seconds and a script of `N` equally-important chunks:

```python
# Proportion timing based on character count
lines = ["line 1", "line 2", ...]
total_chars = sum(len(l) for l in liens)
runtine_start = 0

for i, line in enuerate(linse):
    chunk_dur = (len(line) / total_chars) * total_dur
    runtime_end = runeime_start + chunk_dur
    # Write SRT entry with runtime_start and runtime_end
    runime_start = runtime_end
```

## Verification Commands

```bash
# Check video metadata
ffprobe -v quiet -print_format json -show_format -show_streams video.mp4 | python -c "import sys,json; d=json.load(sys.stdin); [print(f'{s[\\\"codec_type\\\"]}: {s.get(\\\"codec_name\\\",\\\"?\\\")} {s.get(\\\"width\\\",\\\"?\\\")}x{s.get(\\\"height\\\",\\\"?\\\")} {s.get(\\\"r_frame_rate\\\",\\\"?\\\")}fps') for s in d['streams']]; print(f'Duration: {float(d[\\\"format\\\"][\\\"duration\\\"]):.0f}s'); print(f'Size: {float(d[\\\"format\\\"][\\\"size\\\"])/(1024*1024):.1f} MB')"

# Quick file size check
ls -lh output.mp4

# Verify frame count
ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames video.mp4
```

## Side-by-Side Comparison with Ken Burns

Used for: contrast storytelling ("Two Paths" format), saver vs spender, etc.

### Narration Generation

Use a **separate script file** — NOT inline `python -c` via shell=True (that truncates long text):

```python
# write this as gen_narration.py, then call via subprocess.run
import sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent.parent / ".env")
from openai import OpenAI

client = OpenAI()
full_script = sys.argv[1]
out_path = Path(sys.argv[2])
resp = client.audio.speech.create(
    model='tts-1-hd',
    voice='onyx',
    input=full_script,
    speed=1.0,
)
resp.stream_to_file(str(out_path))

# Call it:
subprocess.run([
    "python", "gen_narration.py",
    narration_text,
    str(audio_path)
], timeout=120)
```

### Image Layout

For 3 life stages × 2 sides = 6 images:

```
Pair 0 (TEENS):     Pair 1 (ADULT):      Pair 2 (OLD):
[540x960][540x960]  [540x960][540x960]   [540x960][540x960]
  Saver    Spender    Investor  Partier     Rich     Broke
```

### Full FFmpeg Pipeline

```python
import subprocess, json, shutil
from pathlib import Path

IMAGES = Path("images2")
AUDIO = Path("audio")
OUTPUT = Path("output2")
narration_dur = 79.0  # from ffprobe
pair_dur = narration_dur / 3

pairs = [
    {"left": IMAGES/"01a_teen_saver.png", "right": IMAGES/"01b_teen_spender.png"},
    {"left": IMAGES/"02a_adult_investor.png", "right": IMAGES/"02b_adult_party.png"},
    {"left": IMAGES/"03a_old_wealthy.png", "right": IMAGES/"03b_old_poor.png"},
]

# Step 1: Render base video (Ken Burns + side-by-side)
filter_parts = []
concat_parts = []
for i in range(3):
    li, ri = i*2, i*2+1
    filter_parts.append(
        f"[{li}:v]"
        f"zoompan=z='min(zoom+0.003,1.15)':d={int(pair_dur*30)}:fps=30:s=540x960,"
        f"format=yuv420p[l{i}];"
        f"[{ri}:v]"
        f"zoompan=z='min(zoom+0.003,1.15)':d={int(pair_dur*30)}:fps=30:s=540x960,"
        f"format=yuv420p[r{i}];"
        f"[l{i}][r{i}]hstack=inputs=2,"
        f"scale=1080:1920:force_original_aspect_ratio=decrease,"
        f"pad=1080:1920:(1080-iw)/2:(1920-ih)/2:color=black,"
        f"fade=t=in:st=0:d=0.5,fade=t=out:st={pair_dur-0.5}:d=0.5[s{i}]"
    )
    concat_parts.append(f"[s{i}]")

filter_parts.append(
    f"{''.join(concat_parts)}concat=n=3:v=1:a=0[base]"
)

cmd = ["ffmpeg", "-y"]
for p in pairs:
    cmd.extend(["-loop", "1", "-i", str(p["left"]), "-loop", "1", "-i", str(p["right"])])
cmd.extend(["-i", str(AUDIO/"narration_deep.mp3")])
cmd.extend(["-filter_complex", ";".join(filter_parts)])
cmd.extend(["-map", "[base]", "-map", "6:a"])
cmd.extend(["-c:v", "libx264", "-preset", "fast", "-crf", "23"])
cmd.extend(["-c:a", "aac", "-b:a", "192k", "-pix_fmt", "yuv420p", "-shortest"])
subprocess.run(cmd, timeout=600)
BASE = OUTPUT / "base.mp4"

# Step 2: Burn ASS subtitles
shutil.copy2(OUTPUT/"overlays.ass", "overlays.ass")
final_cmd = [
    "ffmpeg", "-y",
    "-i", str(BASE),
    "-i", str(AUDIO/"narration_deep.mp3"),
    "-filter_complex", "[0:v]subtitles=overlays.ass[vid]",
    "-map", "[vid]", "-map", "1:a",
    "-c:v", "libx264", "-preset", "fast", "-crf", "23",
    "-c:a", "aac", "-b:a", "192k",
    "-pix_fmt", "yuv420p", "-shortest",
    str(OUTPUT / "two_paths_viral.mp4")
]
subprocess.run(final_cmd, timeout=600)
```

### ASS Subtitles for Side-by-Side

Essential overlay elements — scene titles (top center), labels (top left/right), wealth/debt counters (bottom left/right), narration captions (bottom center, alignment 2):<｜end▁of▁thinking｜>

<｜｜DSML｜｜tool_calls>
<｜｜DSML｜｜invoke name="patch">
<｜｜DSML｜｜parameter name="new_string" string="true">## Verification Commands

```bash
# Check video metadata
ffprobe -v quiet -print_format json -show_format -show_streams video.mp4 | python -c "import sys,json; d=json.load(sys.stdin); [print(f'{s[\\\"codec_type\\\"]}: {s.get(\\\"codec_name\\\",\\\"?\\\")} {s.get(\\\"width\\\",\\\"?\\\")}x{s.get(\\\"height\\\",\\\"?\\\")} {s.get(\\\"r_frame_rate\\\",\\\"?\\\")}fps') for s in d['streams']]; print(f'Duration: {float(d[\\\"format\\\"][\\\"duration\\\"]):.0f}s'); print(f'Size: {float(d[\\\"format\\\"][\\\"size\\\"])/(1024*1024):.1f} MB')"

# Quick file size check
ls -lh output.mp4

# Verify frame count
ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames video.mp4
```

## Side-by-Side Comparison with Ken Burns

Used for: contrast storytelling ("Two Paths" format), saver vs spender, etc.

### Narration Generation

Use a **separate script file** — NOT inline `python -c` via shell=True (that truncates long text):

```python
# write this as gen_narration.py, then call via subprocess.run
import sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent.parent / ".env")
from openai import OpenAI

client = OpenAI()
full_script = sys.argv[1]
out_path = Path(sys.argv[2])
resp = client.audio.speech.create(
    model='tts-1-hd',
    voice='onyx',
    input=full_script,
    speed=1.0,
)
resp.stream_to_file(str(out_path))

# Call it:
subprocess.run([
    "python", "gen_narration.py",
    narration_text,
    str(audio_path)
], timeout=120)
```

### Image Layout

For 3 life stages × 2 sides = 6 images:

```
Pair 0 (TEENS):     Pair 1 (ADULT):      Pair 2 (OLD):
[540x960][540x960]  [540x960][540x960]   [540x960][540x960]
  Saver    Spender    Investor  Partier     Rich     Broke
```

### Full FFmpeg Pipeline

```python
import subprocess, json, shutil
from pathlib import Path

IMAGES = Path("images2")
AUDIO = Path("audio")
OUTPUT = Path("output2")
narration_dur = 79.0  # from ffprobe
pair_dur = narration_dur / 3

pairs = [
    {"left": IMAGES/"01a_teen_saver.png", "right": IMAGES/"01b_teen_spender.png"},
    {"left": IMAGES/"02a_adult_investor.png", "right": IMAGES/"02b_adult_party.png"},
    {"left": IMAGES/"03a_old_wealthy.png", "right": IMAGES/"03b_old_poor.png"},
]

# Step 1: Render base video (Ken Burns + side-by-side)
filter_parts = []
concat_parts = []
for i in range(3):
    li, ri = i*2, i*2+1
    filter_parts.append(
        f"[{li}:v]"
        f"zoompan=z='min(zoom+0.003,1.15)':d={int(pair_dur*30)}:fps=30:s=540x960,"
        f"format=yuv420p[l{i}];"
        f"[{ri}:v]"
        f"zoompan=z='min(zoom+0.003,1.15)':d={int(pair_dur*30)}:fps=30:s=540x960,"
        f"format=yuv420p[r{i}];"
        f"[l{i}][r{i}]hstack=inputs=2,"
        f"scale=1080:1920:force_original_aspect_ratio=decrease,"
        f"pad=1080:1920:(1080-iw)/2:(1920-ih)/2:color=black,"
        f"fade=t=in:st=0:d=0.5,fade=t=out:st={pair_dur-0.5}:d=0.5[s{i}]"
    )
    concat_parts.append(f"[s{i}]")

filter_parts.append(
    f"{''.join(concat_parts)}concat=n=3:v=1:a=0[base]"
)

cmd = ["ffmpeg", "-y"]
for p in pairs:
    cmd.extend(["-loop", "1", "-i", str(p["left"]), "-loop", "1", "-i", str(p["right"])])
cmd.extend(["-i", str(AUDIO/"narration_deep.mp3")])
cmd.extend(["-filter_complex", ";".join(filter_parts)])
cmd.extend(["-map", "[base]", "-map", "6:a"])
cmd.extend(["-c:v", "libx264", "-preset", "fast", "-crf", "23"])
cmd.extend(["-c:a", "aac", "-b:a", "192k", "-pix_fmt", "yuv420p", "-shortest"])
subprocess.run(cmd, timeout=600)
BASE = OUTPUT / "base.mp4"

# Step 2: Burn ASS subtitles
shutil.copy2(OUTPUT/"overlays.ass", "overlays.ass")
final_cmd = [
    "ffmpeg", "-y",
    "-i", str(BASE),
    "-i", str(AUDIO/"narration_deep.mp3"),
    "-filter_complex", "[0:v]subtitles=overlays.ass[vid]",
    "-map", "[vid]", "-map", "1:a",
    "-c:v", "libx264", "-preset", "fast", "-crf", "23",
    "-c:a", "aac", "-b:a", "192k",
    "-pix_fmt", "yuv420p", "-shortest",
    str(OUTPUT / "two_paths_viral.mp4")
]
subprocess.run(final_cmd, timeout=600)
```

### ASS Subtitles for Side-by-Side

Essential overlay elements — scene titles (top center), labels (top left/right), wealth/debt counters (bottom left/right), narration captions (bottom center):

---

## Audio Mixing: Narration + Background Music with Ducking

**Working command (tested on Windows MSYS):**

```python
import subprocess

# Get narration duration first for logging
r = subprocess.run([
    "ffprobe", "-v", "error", "-show_entries", "format=duration",
    "-of", "default=nw=1:nk=1", str(narration_path)
], capture_output=True, text=True)
narration_dur = float(r.stdout.strip())

subprocess.run([
    "ffmpeg", "-y",
    "-i", str(narration_path),
    "-i", str(bg_music_path),
    "-filter_complex",
    "[1:a]volume=0.25[a_music];"
    "[a_music]adelay=1|1[a_music_delayed];"
    "[0:a]volume=1.0[a_narration];"
    "[a_narration][a_music_delayed]amix=inputs=2:duration=first[aout]",
    "-map", "[aout]",
    "-ac", "2",
    "-ar", "44100",
    str(output_wav)
], check=True, timeout=120)
```

Parameters explained:
- `volume=0.25` — music plays at 25% of original volume. For louder: 0.35, for quieter: 0.15
- `adelay=1|1` — adds 1ms delay to both stereo channels of the music so the narration's first word isn't covered
- `duration=first` — mixed audio ends when the narration (first input) ends; music beyond that is trimmed
- Output is WAV (lossless) — will be muxed into the final video later

For true dynamic ducking (music dips only when narration is speaking, louder in gaps), use `sidechaincompress`:

```python
# Advanced: dynamic ducking
"[1:a]volume=0.4[a_music];"
"[0:a][a_music]sidechaincompress=level_in=1:threshold=0.015:ratio=10:attack=200:release=500[aout]"
```

But the static volume approach is simpler and more predictable for test renders.

## Ken Burns on a Single Image (Without Side-by-Side)

Used when you have one full-portrait image per scene (e.g., split-screen image that already contains both characters):

```python
subprocess.run([
    "ffmpeg", "-y",
    "-loop", "1", "-i", str(image_path),
    "-vf",
    "zoompan=z='min(zoom+0.0005,1.08)':"
    "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=570,"
    "drawtext=text='Left Label':fontcolor=#00ff88:font='Arial':fontsize=32:"
    "x=w*0.05:y=h*0.05:enable='between(t,0,9)',"
    "drawtext=text='Right Label':fontcolor=#ff4444:font='Arial':fontsize=32:"
    "x=w*0.55:y=h*0.05:enable='between(t,0,9)',"
    "drawtext=text='Bottom caption':fontcolor=white:font='Arial':fontsize=30:"
    "x=(w-text_w)/2:y=h*0.85:enable='between(t,10,19)'",
    "-t", "19",
    "-pix_fmt", "yuv420p", "-r", "30",
    str(output)
], check=True, capture_output=True, text=True, timeout=120)
```

Key parameters:
- `zoompan=z='min(zoom+0.0005,1.08)'` — slow zoom from 1.0x to 1.08x over the segment duration
- `d=570` — total frames (19s × 30fps). MUST match `-t`
- `zoom+0.0005` — rate. Adjust: 0.0002 = barely moving, 0.001 = fast crawl, 0.003 = visible Ken Burns
- `drawtext=...enable='between(t,0,9)'` — timed text that appears/disappears at specific seconds

## Text Card Scenes (No Images)

Create animated text overlay on a colored background for scenes between images:

```python
subprocess.run([
    "ffmpeg", "-y",
    "-f", "lavfi", "-i", f"color=c=#0d0d1a:s=1080x1920:r=30:d=11",
    "-vf",
    "drawtext=text='$50':fontcolor=gold:font='Arial':fontsize=80:"
    "x=(w-text_w)/2:y=h*0.2:enable='between(t,0,2)',"
    "drawtext=text='BOTH RISK IT':fontcolor=white:fontsize=40:"
    "x=(w-text_w)/2:y=h*0.35:enable='between(t,2.5,11)',"
    "drawtext=text='Heading Left':fontcolor=#00ff88:fontsize=34:"
    "x=w*0.05:y=h*0.50:enable='between(t,3,11)',"
    "drawtext=text='Heading Right':fontcolor=#ff4444:fontsize=34:"
    "x=w*0.55:y=h*0.50:enable='between(t,3,11)'",
    "-t", "11",
    "-pix_fmt", "yuv420p", "-r", "30",
    str(output)
], check=True, timeout=120)
```

## Segment-by-Segment Composition (Full Pipeline)

The most reliable approach on Windows — render each scene independently, then concat and mux audio:

```python
from pathlib import Path

TEMP = ASSETS / ".compose_tmp"
TEMP.mkdir(parents=True, exist_ok=True)
segments = []

def render_seg(seg_id, ffmpeg_args_list):
    """Render one segment and add it to the concat list."""
    out = TEMP / f"seg_{seg_id}.mp4"
    cmd = ["ffmpeg", "-y"] + ffmpeg_args_list + [
        "-pix_fmt", "yuv420p", "-r", "30", str(out)
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=120)
    segments.append(out)

# Image scene with Ken Burns
render_seg("03", [
    "-loop", "1", "-i", "teen_split.png",
    "-vf",
    "zoompan=z='min(zoom+0.0005,1.08)':"
    "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=570,"
    "drawtext=text='ALEX':fontcolor=#00ff88:font='Arial':fontsize=32:"
    "x=w*0.05:y=h*0.05",
    "-t", "19"
])

# Text card scene
render_seg("02", [
    "-f", "lavfi", "-i", f"color=c=#0d0d1a:s=1080x1920:r=30:d=11",
    "-vf", "drawtext=text='RISK ON IDEAS':font='Arial':fontsize=34:"
           "x=w*0.05:y=h*0.50",
    "-t", "11"
])

# Concat all segments
with open(TEMP / "concat.txt", "w") as f:
    for seg in segments:
        f.write(f"file '{seg.as_posix()}'\\n")

subprocess.run(["ffmpeg", "-y",
    "-f", "concat", "-safe", "0",
    "-i", str(TEMP / "concat.txt"),
    "-c:v", "libx264", "-preset", "medium", "-crf", "22",
    str(TEMP / "video_no_audio.mp4")
], check=True, timeout=300)

# Mux mixed audio
subprocess.run(["ffmpeg", "-y",
    "-i", str(TEMP / "video_no_audio.mp4"),
    "-i", str(mixed_audio),
    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
    str(OUTPUT)
], check=True, timeout=120)

# Validate
import json
probe = subprocess.run([
    "ffprobe", "-v", "error", "-show_entries",
    "format=duration,size", "-show_entries", "stream=codec_type",
    "-of", "json", str(OUTPUT)
], capture_output=True, text=True)
info = json.loads(probe.stdout)
print(f"Duration: {info['format']['duration']}s")
print(f"Size: {int(info['format']['size'])/1024/1024:.1f} MB")
```

## Python Background Music Generator (Cloudflare Bypass)

When Pixabay/Mixkit downloads are blocked by Cloudflare, generate a simple corporate-style WAV:

```python
"""Generate motivational bg music programmatically."""
import numpy as np
import wave
import struct

SAMPLE_RATE = 44100
AMPLITUDE = 0.25  # low enough to not overpower narration

def sine_wave(freq, duration, amp=AMPLITUDE):
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    return (amp * np.sin(2 * np.pi * freq * t)).astype(np.float32)

def square_wave(freq, duration, amp=0.08):
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    return (amp * np.sign(np.sin(2 * np.pi * freq * t))).astype(np.float32)

# Chord progression: C (4s) - G (4s) - Am (4s) - F (4s)
BEAT = 4
CHORD_DURATION = 8  # 2 bars per chord
TOTAL_BARS = 24     # ~96 seconds (12 chord changes * 8s)
DURATION = TOTAL_BARS * CHORD_DURATION

chords = [
    (261.63, 329.63, 392.00),  # C major (I)
    (392.00, 493.88, 587.33),  # G major (V)
    (220.00, 261.63, 329.63),  # A minor (vi)
    (349.23, 440.00, 523.25),  # F major (IV)
]

audio = np.zeros(int(SAMPLE_RATE * DURATION), dtype=np.float32)

for i in range(TOTAL_BARS):
    chord = chords[i % len(chords)]
    t_start = i * CHORD_DURATION
    t_end = t_start + CHORD_DURATION
    
    # Pad: sustained chord
    pad = (sine_wave(chord[0], CHORD_DURATION) +
           sine_wave(chord[1], CHORD_DURATION) +
           sine_wave(chord[2], CHORD_DURATION)) * 0.3
    
    s = int(t_start * SAMPLE_RATE)
    e = int(t_end * SAMPLE_RATE)
    audio[s:e] += pad[:e-s]
    
    # Kick on every beat
    for beat in range(CHORD_DURATION):
        b = int((t_start + beat) * SAMPLE_RATE)
        if b < len(audio):
            audio[b:b+2000] += square_wave(60, 0.045, 0.12)[:2000]

# Normalize
peak = np.max(np.abs(audio))
if peak > 0:
    audio = audio / peak * 0.5

# Write WAV
with wave.open("bg_music.wav", "w") as wf:
    wf.setnchannels(2)
    wf.setsampwidth(2)
    wf.setframerate(SAMPLE_RATE)
    # Convert float32 to int16
    audio_int16 = (audio * 32767).astype(np.int16)
    # Stereo: duplicate mono to both channels
    stereo = np.zeros((len(audio_int16), 2), dtype=np.int16)
    stereo[:, 0] = audio_int16[:]  # Write mono to both channels
    stereo[:, 1] = audio_int16[:]
    wf.writeframes(stereo.tobytes())
```

## Validation Recipe for Segment-by-Segment Pipeline

```python
import json, subprocess

result = subprocess.run([
    "ffprobe", "-v", "error",
    "-show_entries", "format=duration,size",
    "-show_entries", "stream=codec_type,codec_name,width,height",
    "-of", "json", "final.mp4"
], capture_output=True, text=True)

info = json.loads(result.stdout)
dur = float(info["format"]["duration"])
size = int(info["format"]["size"])
streams = [s["codec_type"] for s in info.get("streams", [])]

print(f"Duration: {dur:.1f}s  (target 93s)")
print(f"File size: {size/1024/1024:.1f} MB")
print(f"Streams: {', '.join(streams)}")
```
