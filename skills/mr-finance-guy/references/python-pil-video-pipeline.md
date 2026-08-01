# Python PIL + FFmpeg Video Pipeline

Alternative to the Remotion pipeline. Faster for prototyping. Same visual output.
Used in `replicate_video_v7.py` for Saving vs Investing.

## Architecture

```
PIL scene generation           FFmpeg composition
┌────────────────────┐         ┌──────────────────┐
│ Scene 1 (PNG)      │ ──────▸│ Per-scene clip   │
│ Scene 2 (PNG)      │ ──────▸│ Per-scene clip   │
│ ...                │         │ Concat clips     │
│ Scene N (PNG)      │ ──────▸│ + audio merge    │
└────────────────────┘         └──────────────────┘
         ▲
   ElevenLabs TTS (determines scene durations)
```

## Stage 1 — ElevenLabs TTS → Scene Timings

Generate each narration segment as a separate MP3:

```python
import requests, base64

VOICE_ID = "21m00Tcm4TlvDq8ikWAM"
API_KEY = open(MONEY_PRINTER_KEY).read().strip()
URL = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

scenes = [
    "Narration text for scene 1...",
    "Narration text for scene 2...",
    # ...
]

for i, text in enumerate(scenes):
    resp = requests.post(URL, headers={"xi-api-key": API_KEY}, json={
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
    })
    with open(f"audio_v3/segment_{i+1:02d}.mp3", "wb") as f:
        f.write(resp.content)
```

Scene duration = MP3 file duration (use ffprobe to get each).

## Stage 2 — PIL Scene Generation

Use Pillow to render each scene matching the reference layout.

### Key imports

```python
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1920  # 9:16 vertical
```

### Drawing helpers (v7 defaults)

```python
def draw_card(draw, x, y, w, h, bg_color, text, text_color="#000000", font_size=105, font_path="impact.ttf"):
    """Draw a card with rounded corners and centered text."""
    draw.rounded_rectangle([x, y, x+w, y+h], radius=8, fill=bg_color)
    font = ImageFont.truetype(font_path, font_size)
    bbox = draw.textbbox((0, 0), text, font=font)
    tx = x + (w - (bbox[2] - bbox[0])) // 2
    ty = y + (h - (bbox[3] - bbox[1])) // 2
    draw.text((tx, ty), text, fill=text_color, font=font)

def draw_narration(draw, text, y=1402, color="#000000", max_width=920, font_size=44, font_path="impact.ttf"):
    """Draw word-wrapped narration text at the lower third."""
    font = ImageFont.truetype(font_path, font_size)
    words = text.split()
    lines, line = [], []
    for w in words:
        test = " ".join(line + [w])
        if draw.textbbox((0, 0), test, font=font)[2] <= max_width:
            line.append(w)
        else:
            lines.append(" ".join(line))
            line = [w]
    if line:
        lines.append(" ".join(line))
    line_h = font_size + 14
    start_y = y - (len(lines) * line_h) // 2
    for i, l in enumerate(lines):
        bbox = draw.textbbox((0, 0), l, font=font)
        tx = (W - (bbox[2] - bbox[0])) // 2
        draw.text((tx, start_y + i * line_h), l, fill=color, font=font)
```

### Proportions grid (1080×1920) — v8 Verified by Twelve Labs

| Element | Position | Size |
|---------|----------|------|
| Left card (SAVING side) | x=65, y=192 | w=454, h=250 (42% × 13%) |
| Right card (INVESTING side) | x=562, y=192 | w=454, h=250 (42% × 13%) |
| Character | LEFT: x=32, y=1718 (bottom-aligned, 8% margin) | **55% of H (1056px)** — outline dilation recommended for pure black sprites |
| Speech bubble (hook) | center x=540, y=538 (28% from top) | ~200×120 |
| Narration text | center y=1402 (73% from bottom) | max_width=920 |

### Card Styling (v7)

| Element | Left Card | Right Card |
|---------|-----------|------------|
| Fill | `#F5F5F5` (off-white — visible against white bg!) | `#33BB77` (lighter green) |
| Border | `#DCDCDC` 2px | `#28A064` 2px |
| Accent | 4px `#1E90FF` bar at top | none |
| Text | `#000000` Impact Bold 105px | `#FFFFFF` Impact Bold 105px |

### Character loading with outline thickening

When character sprites are pure black outlines on transparent (no skin-tones), thin lines become invisible at mobile scale. Apply dilation to thicken outlines:

```python
from PIL import Image, ImageFilter, ImageFont, ImageDraw

char_img = Image.open(f"{CHAR_DIR}/pose_01.png").convert("RGBA")
# Scale to 55% of frame height for visible details
target_h = int(H * 0.55)
ratio = target_h / char_img.height
char_w = int(char_img.width * ratio)
char_img = char_img.resize((char_w, target_h), Image.LANCZOS)

# --- Outline thickening via MaxFilter dilation ---
_, _, _, a = char_img.split()
outline_mask = a.point(lambda x: 255 if x > 30 else 0)
thicken_px = 4
dilated = outline_mask.filter(ImageFilter.MaxFilter(thicken_px * 2 + 1))

# Create thickened shadow layer
thick_shadow = Image.composite(
    Image.new('RGBA', char_img.size, (0, 0, 0, 200)),
    Image.new('RGBA', char_img.size, (0, 0, 0, 0)),
    dilated
)

# Position: left side, bottom-aligned
char_x = int(W * 0.03)
char_y = H - target_h - int(H * 0.08)  # 8% margin from bottom

# Paste shadow first, then original on top
img.paste(thick_shadow, (char_x, char_y), thick_shadow)
img.paste(char_img, (char_x, char_y), char_img)
```

TwelveLabs Pegasus 1.2 describes this output as: "thick outline ensures high contrast and clarity against the white background, making it easily distinguishable and memorable."

### Complete scene example (v7 — Twelve Labs verified)

```python
def render_scene_1():
    img = Image.new("RGB", (W, H), "#FFFFFF")
    draw = ImageDraw.Draw(img)

    # FONT — Impact Bold for card headings
    font_card = ImageFont.truetype("impact.ttf", 105)

    # Left card — off-white fill + border + blue accent bar
    draw.rounded_rectangle([65, 192, 65+454, 192+250], radius=8,
                           fill="#F5F5F5", outline="#DCDCDC", width=2)
    draw.rectangle([75, 197, 65+454-10, 201], fill="#1E90FF")

    bbox = draw.textbbox((0, 0), "SAVING", font=font_card)
    draw.text((65 + (454-(bbox[2]-bbox[0]))//2,
               192 + (250-(bbox[3]-bbox[1]))//2 - 2),
              "SAVING", fill="#000000", font=font_card)

    # Right card — green fill + border
    draw.rounded_rectangle([562, 192, 562+454, 192+250], radius=8,
                           fill="#33BB77", outline="#28A064", width=2)

    bbox = draw.textbbox((0, 0), "INVESTING", font=font_card)
    draw.text((562 + (454-(bbox[2]-bbox[0]))//2,
               192 + (250-(bbox[3]-bbox[1]))//2 - 2),
              "INVESTING", fill="#FFFFFF", font=font_card)

    # Character
    char = Image.open(f"{CHAR_DIR}/pose_neutral.png").convert("RGBA")
    target_h = int(H * 0.40)
    ratio = target_h / char.height
    char = char.resize((int(char.width * ratio), target_h), Image.LANCZOS)
    img.paste(char, (65, int(H * 0.30)), char)

    # Narration
    font_narr = ImageFont.truetype("impact.ttf", 44)
    text = "This is saving. This is investing. What's the difference?"
    max_w = 920
    words = text.split()
    lines, line = [], []
    for w in words:
        test = " ".join(line + [w])
        if draw.textbbox((0, 0), test, font=font_narr)[2] <= max_w:
            line.append(w)
        else:
            lines.append(" ".join(line))
            line = [w]
    if line: lines.append(" ".join(line))

    start_y = 1402
    for i, l in enumerate(lines):
        bbox = draw.textbbox((0, 0), l, font=font_narr)
        draw.text(((1080-(bbox[2]-bbox[0]))//2, start_y + i * 58),
                  l, fill="#000000", font=font_narr)
    return img
```

## Stage 3 — FFmpeg Composition (Working Approach)

⚠️ **CRITICAL**: The concat demuxer with still images + explicit durations creates 1fps output.
The **working approach** is: convert each PNG to a short video clip, then concat the clips.

### Approach A: Per-scene clips + concat (RECOMMENDED)

```bash
# Scene durations matching TTS length
durations=(8 7 7 7 7 8 8 8 7 7 6)

# Generate per-scene clips
for i in "${!durations[@]}"; do
    fnum=$(printf "%03d" $i)
    dur="${durations[$i]}"
    ffmpeg -y -loop 1 -i "frames/scene_${fnum}.png" \
      -c:v libx264 -preset ultrafast -crf 22 \
      -t "${dur}" -pix_fmt yuv420p -r 30 \
      "clips/scene_${fnum}.mp4"
done

# Concat clips
> clips.txt
for f in clips/scene_*.mp4; do
    echo "file '$f'" >> clips.txt
done

ffmpeg -y -f concat -safe 0 -i clips.txt \
  -c copy \
  video_no_audio.mp4
```

### Approach B: Concat demuxer with still images (NOT RECOMMENDED)

```bash
# concat.txt format:
#   file 'scene_000.png'
#   duration 8.0
#   file 'scene_001.png'
#   duration 7.0
#   ...
#   file 'scene_N.png'    # last file repeated without duration

ffmpeg -y \
  -f concat -safe 0 -i concat.txt \
  -fps_mode passthrough \
  -pix_fmt yuv420p \
  -c:v libx264 -preset medium -crf 22 \
  video_no_audio.mp4
```
This produces 1fps output in some ffmpeg builds. Test before relying on it.

### Audio merge

```bash
# Merge MP3 segments
> audio_merge.txt
for f in audio_v3/segment_*.mp3; do
    echo "file '$f'" >> audio_merge.txt
done
ffmpeg -y -f concat -safe 0 -i audio_merge.txt -c copy audio_merged.mp3

# Combine video + audio
ffmpeg -y \
  -i video_no_audio.mp4 \
  -i audio_merged.mp3 \
  -c:v copy -c:a aac -b:a 192k -shortest \
  final_output.mp4
```

### Get audio duration per segment

```bash
ffprobe -v quiet -show_entries format=duration -of csv=p=0 segment_01.mp3
```
Returns seconds, e.g. `10.52`. Use this to set the scene duration.

## Pitfalls

| Issue | Symptom | Fix |
|-------|---------|-----|
| Wrong fps | 1fps video plays each frame for 1s | Use per-scene clips (Approach A) |
| Audio too long | Video ends early | Add 1-2s to last scene duration |
| Font not found | `OSError: cannot open resource` | Use `arial.ttf` (Windows) or install via `apt install fonts-dejavu` |
| Character sprite too small | Details invisible at thumbnail scale | Scale to ~40% frame height |
| Card text overflow | Text spills out of card | Reduce font size or wrap text with `textbbox` measurement |
| Path spaces in filenames | ffmpeg "No such file" | Use absolute paths or double-quote in concat file |

## Output Specs

| Property | Value |
|----------|-------|
| Resolution | 1080×1920 (9:16 vertical) |
| Framerate | 30 fps |
| Video codec | H.264 (libx264) |
| Audio codec | AAC 192k |
| CRF | 22 |
| Preset | ultrafast (per-clip) or medium (final) |

## Scene Structure — Dynamic Card Labels

Card labels change per scene to match the narration. See `replicate_video_v8.py` for a complete working example of the dynamic label approach with active-side highlighting.
