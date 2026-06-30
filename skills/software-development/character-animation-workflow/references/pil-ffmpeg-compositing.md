# PIL + FFmpeg Compositing (Fast Replication Path)

## When to Use

When you need to rapidly replicate a video's format using pre-rendered character PNGs and prop images — without the full SVG-rigging pipeline. This approach works for channels that already have:
- Character pose PNGs (e.g. `bg_removed/` folder with 10-20 poses)
- A library of prop/icon images
- ElevenLabs TTS setup
- Background music tracks

This is NOT a replacement for the full character-animation pipeline (SVG rigs for fluid animation). It's a **fast-track** for producing comparison-format videos when the visual style is already established.

## Pipeline Steps

### 1. Analyze the Reference Video

```bash
# Get metadata
ffprobe -v quiet -print_format json -show_format -show_streams input.mp4

# Extract audio for transcription
ffmpeg -i input.mp4 -vn -acodec pcm_s16le -ar 16000 -ac 1 -y audio.wav

# Transcribe with faster-whisper
python -c "
from faster_whisper import WhisperModel
model = WhisperModel('tiny', device='cpu', compute_type='int8')
segments, info = model.transcribe('audio.wav', language='en')
for seg in segments:
    print(f'[{seg.start:.1f}s-{seg.end:.1f}s] {seg.text.strip()}')
"

# Extract keyframes every 3s for visual reference
ffmpeg -i input.mp4 -vf "fps=1/3,scale=480:854" -q:v 2 frame_%03d.jpg
```

### 2. Create the Compositing Script

Use a Python script with PIL/Pillow:

```python
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920  # 9:16 vertical
BG_COLOR = (255, 255, 255, 255)

# Character loading
def load_pose(pose_name, char_dir, pose_map):
    fname = pose_map.get(pose_name, pose_name) + ".png"
    fpath = char_dir / fname
    if not fpath.exists():
        fpath = char_dir / fname.replace(" ", "_")
    if not fpath.exists():
        return None
    img = Image.open(fpath).convert("RGBA")
    target_h = int(H * 0.42)
    aspect = img.width / img.height
    target_w = int(target_h * aspect)
    return img.resize((target_w, target_h), Image.LANCZOS)

# Prop image loading (fuzzy match by keyword)
def load_prop(prop_dir, name_patterns, size=(120, 120)):
    for f in os.listdir(str(prop_dir)):
        f_lower = f.lower()
        for pat in name_patterns:
            if pat.lower() in f_lower:
                img = Image.open(os.path.join(str(prop_dir), f)).convert("RGBA")
                return img.resize(size, Image.LANCZOS)
    return None
```

**Scene types:**
- **Intro** — Character center, title, "VS" badge, side labels
- **Content scenes** — Character on left, 3×2 prop grid on right, color-coded label
- **Kicker/Comparison** — Side-by-side comparison columns with divider line
- **Closing** — Character center, CTA text

### 3. Generate Video from Scenes

```python
# Render each scene to a still PNG
for i, (img, duration, name) in enumerate(scenes):
    fpath = bg_dir / f"scene_{i:03d}_{name}.png"
    img.save(fpath)

# Convert each PNG to a video segment with ffmpeg
for i, (img, duration, name) in enumerate(scenes):
    seg_path = output_dir / f"seg_{i:03d}.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-loop", "1", "-i", str(bg_dir / f"scene_{i:03d}_{name}.png"),
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-pix_fmt", "yuv420p", "-r", "30", "-t", str(duration), str(seg_path)
    ])

# Concatenate all segments
concat_file = output_dir / "concat.txt"
with open(concat_file, "w") as f:
    for s in segments:
        f.write(f"file '{s}'\n")

subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file),
                "-c", "copy", str(final_no_audio)])
```

### 4. Generate TTS Narration

Use ElevenLabs API (see `elevenlabs/SKILL.md` for API details):

```python
ELEVENLABS_API_KEY = Path.home().joinpath("Documents", "Projects", "MoneyPrinterTurbo", ".elevenlabs_key").read_text().strip()
VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel

for scene_name, duration, text in SCENES:
    resp = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}",
        headers={"xi-api-key": ELEVENLABS_API_KEY},
        json={"text": text, "model_id": "eleven_multilingual_v2",
              "voice_settings": {"stability": 0.5, "similarity_boost": 0.8, "style": 0.3}}
    )
    Path(f"{scene_name}.mp3").write_bytes(resp.content)
```

### 5. Compose Final Video with Audio

```python
# Each segment: still PNG + TTS audio
for i, (name, duration) in enumerate(SCENES):
    subprocess.run([
        "ffmpeg", "-y", "-loop", "1", "-i", f"scene_{i:03d}_{name}.png",
        "-i", f"audio/{name}.mp3",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k", "-r", "30", "-t", str(duration), "-shortest",
        f"seg_{i:03d}.mp4"
    ])

# Add background music at low volume
ffmpeg -i video_final.mp4 -i bg_music.wav \
  -filter_complex "[1:a]volume=0.15[a_music];[0:a][a_music]amix=inputs=2:duration=first" \
  -c:v copy -c:a aac -shortest final_with_music.mp4
```

## Pitfalls

1. **Missing prop images** — `load_prop()` fuzzy-matches by keyword. Always verify props are found by listing loaded props during scene generation.
2. **Character pose not found** — The `POSE_MAP` must match actual filenames in the character directory (with or without spaces, underscores).
3. **Audio duration mismatch** — If TTS is shorter than the scene duration, use `-shortest` to trim the scene to match the audio.
4. **Font availability** — Windows fonts at `C:/Windows/Fonts/` differ from Linux paths. Always use a fallback chain.
5. **CRF vs quality** — CRF 20 is a good balance for these composite videos. Lower CRF (18) for higher quality, higher (23) for smaller files.
