---
name: short-video-production
version: "1.0.0"
description: >-
  Produce 9:16 vertical short-form videos (>60s for TikTok monetization) using
  AI image generation + TTS narration + FFmpeg composition. Provider-agnostic —
  works with GPT-Image, FLUX, Pexels stock, and any TTS (OpenAI, ElevenLabs,
  Google). Covers the full pipeline: script → image assets → narration audio →
  FFmpeg composition with SRT captions.
category: media
triggers:
  - "create a TikTok/Reel/Shorts video"
  - "viral video"
  - "slideshow with narration"
  - "video from images and voiceover"
  - "short-form video production"
---

# Short-Form AI Video Production

## 🚨 FIRST CHECK: OpenMontage is Installed

Before using this skill, check if **OpenMontage** is available at `~/OpenMontage/`. 
OpenMontage is the user's **primary video production system** — fully configured with 
all 12 API keys and 13 production pipelines. It produces higher quality videos with 
Remotion/HyperFrames composition, proper stage management, and multi-provider routing.

**Route to `media/openmontage-production` first.** Only use this skill as a fallback if:
1. OpenMontage preflight shows blockers (missing keys, broken tool registry)
2. The user explicitly asks for a simpler FFmpeg-only approach
3. OpenMontage isn't installed on this machine

## ⚠️ User Preferences (This User)

NEVER produce a video that's just **static images + narration + captions centered on screen**. The user explicitly rejected that format as "literally bad — the caption blocks the entire thing." Every video MUST have:\n- **Motion/animation** on ALL images (Ken Burns slow zoom at minimum)\n- **Side-by-side or split-screen** layout when comparing two concepts\n- **Captions at the very bottom** (y=1920-140 or lower), never covering the subject\n- **Styled labels** (ASS subtitles, not plain SRT) for scene titles and side labels\n- **ElevenLabs TTS for all voiceovers** — mandatory. Never use OpenAI TTS, edge-tts, or any other provider. Always use ElevenLabs Rachel (UUID `21m00Tcm4TlvDq8ikWAM`). API key at `~/Documents/Projects/MoneyPrinterTurbo/.elevenlabs_key`.

---

## When to Use

- User asks to "create a TikTok/Reel/Shorts video"
- User wants a "viral video" with images + narration + captions
- Building a slideshow/explainer video between 30–120s
- Any task that ends with a `.mp4` export for social media

## Workflow (4 Phases)

### Phase 1 — Script & Concept

1. Pick a viral-worthy format: **numbered lists** (7 facts, 5 tips, 3 mistakes), **contrast hooks** ("everything you know about X is wrong"), or **storytelling** (before/after, personal journey)
2. Hook in first 3 seconds — a shocking statement or question
3. Each numbered item = ~10s of runtime. Target 60-90s total
4. Save script as `script.md` in a project directory

### Bonus Format: Side-by-Side Comparison ("Two Paths")

This format tells a contrast story with two characters at multiple life stages. Best for: financial lessons, lifestyle comparisons, life-path narratives.

**Two framing approaches:**

**Approach A — Classic "Saver vs Spender"** (simpler, good for beginners):
- 3 life stages (young → middle → old) × 2 characters = 6 images
- Each stage gets ~1/3 of total runtime
- Side-by-side layout: left = character A (positive/green), right = character B (negative/red)
- Ken Burns slow zoom on both images simultaneously
- Labels at top left/right identifying each character
- Wealth/debt counters at bottom per side
- Captions at very bottom center
- Deep calm male voice (Onyx) narrating the contrast

**Approach B — Authentic "Both Risk, Different Target"** (preferred by this user — shows failure as part of the journey):
- Same structure (3 life stages × 2 characters, side-by-side), but the framing is:
  - **Both characters spend/lose their money** — one spends on GROWTH (side hustles, businesses, trading, education) that sometimes fails, the other spends on CONSUMPTION (stuff, entertainment, lifestyle) that always vanishes
  - **Visible failures on the growth path** — small setback icons, dips in the chart, "FAIL" badges that are part of the visual story (not hidden)
  - **The lesson is NOT "save vs spend"** — it's "BUY ASSETS vs BUY LIABILITIES" or "RISK ON GROWTH vs RISK ON STUFF"
  - The spender also "loses money" — but loses it on things that don't last
  - The saver also "loses money" — on failed experiments and early business attempts — but those losses teach lessons that compound
- This framing is more honest and resonates better because viewers know failure is real

**Narrative arc for comparison videos:**

Hook (0-6s) → Setup: The Single Number (6-17s) → Teen: First Fork (17-36s) → Adult: Divergence (36-58s) → Old: The Result (58-74s) → Climax: The Stat That Hurts (74-88s) → Landing: CTA (88-93s)

- ~190-230 words for a 75-93s video at 150 WPM
- Each section maps to 1-2 visual scenes
- Core message lands in the climax, not the hook

**Image pair prompts (Approach A — saver vs spender):**
```
Pair 1: "focused teenage boy saving money, warm lighting" / "teenager surrounded by toys and games, messy room"
Pair 2: "young man studying financial charts" / "young man partying at nightclub"  
Pair 3: "elderly man on luxury balcony, ocean view" / "elderly man alone in empty apartment, worried"
```

**Image pair prompts (Approach B — both risk, one on growth):**
```
Pair 1: "teenage boy mowing a lawn, small business attempt, suburban driveway" / "teenage boy gaming on couch with snacks, same age"
Pair 2: "adult man working on laptop, small service business, busy office" / "adult man shopping, buying things, same age"
Pair 3: "elderly successful man, owns businesses, content" / "elderly man in storage unit, worried expression, things bought on credit"
```

**Narration pacing:** 950-1300 chars with tts-1-hd Onyx @ speed 1.0 → ~60-79s (TikTok monetization)

**Remotion vs FFmpeg note:** If the project is inside a repo with Remotion support (like OpenMontage's `video_compose` with `render_engines.remotion=true`), use the repo's pipeline instead of ad-hoc FFmpeg — Remotion gives animated comparison cards, count-up stat cards, and spring transitions that are much higher quality. See `setup` skill's `references/repo-pipeline-workflow.md` for the full protocol.

### Phase 2 — Image Assets

**GPT-Image-1.5 (preferred, working):**
```python
from openai import OpenAI
client = OpenAI()
response = client.images.generate(
    model="gpt-image-1.5",
    prompt="cinematic, dark moody, 9:16 portrait, ...",
    n=1,
    size="1024x1536",         # portrait 2:3, closest to 9:16
    quality="high",
    output_format="png"       # NOT response_format (DALL-E only)
)
```
- Returns `b64_json` when `output_format="png"`
- Supported sizes: `1024x1024`, `1024x1536`, `1536x1024`, `auto`
- NO 1024x1792 (that's DALL-E 3)

**FLUX via FAL (alternative):**
- Uses `https://fal.run/fal-ai/flux-pro` — needs top-up
- Size: 576×1024 for portrait

**Pexels stock photos (free):**
```python
requests.get("https://api.pexels.com/v1/search",
    headers={"Authorization": PEXELS_API_KEY},
    params={"query": "...", "orientation": "portrait", "per_page": 5})
```
- Free, no rate limit concerns for volume work
- Better for real-human/psychology content than AI generations

**Prompt style for short-form:**
- Include aspect ratio in prompt: "cinematic, 9:16 portrait, dark moody colors"
- One clear subject per image
- Strong lighting direction for visual drama

### Phase 3 — Audio

**Narration — Female (standard):**
```python
response = client.audio.speech.create(
    model="tts-1", voice="nova",   # nova = natural female
    input=script_text,
    speed=1.5,
)
```
- Speed 1.5 with ~1800-char script → ~76s

**Narration — Deep Calm Male (for comparison/contrast videos):**
```python
response = client.audio.speech.create(
    model="tts-1-hd",
    voice="onyx",                   # onyx = deepest male voice
    input=script_text,
    speed=1.0,                      # slower = more authoritative
)
```
- Speed 1.0 with ~950-1300 chars → ~60-79s
- Use tts-1-hd (not tts-1) for higher quality and accurate speed
- Onyx = deep, calm, authoritative — perfect for contrast storytelling

**CRITICAL: Generate narration via a SEPARATE SCRIPT FILE, not inline `python -c`**
When passing long narration text through `subprocess.run(["python", "-c", f"...{text}..."])`, the shell=True mode truncates the text at certain characters. This caused a 1296-char script to generate only 39s of audio (should be 79s).

✅ **Correct approach — separate script file:**
```python
# gen_narration.py
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

❌ **Wrong approach (text gets truncated):**
```python
# DON'T do this — shell=True truncates the Python code string
subprocess.run(["python", "-c", f"""
resp = client.audio.speech.create(input={json.dumps(text)})
..."""], shell=True)
```

**Get duration:**
```bash
ffprobe -v quiet -print_format json -show_format narration.mp3 | python -c "import sys,json; d=json.load(sys.stdin); print(f'Duration: {float(d[\"format\"][\"duration\"]):.0f}s')"
```

**Background music (free):**
- Pixabay API (`/api/tracks/`) — may be broken; fallback to direct web download
- TikTok's built-in audio library when uploading
- Suno AI if credits available

### Phase 4 — FFmpeg Composition

#### Ken Burns Animation (zoompan)

Every image MUST have slow zoom motion — static images are unacceptable.

```python
# Single-image Ken Burns zoom:
f"[{i}:v]"
f"zoompan=z='min(zoom+0.003,1.15)':"  # slow zoom from 1.0 to 1.15
f"d={int(duration*30)}:"               # total frames    
f"fps=30:s={width}:{height},"          # output resolution
f"format=yuv420p[l{i}]"
```

Parameters:
- `zoom=1.0` at start, increases by `0.003` each frame
- `min(zoom+0.003,1.15)` caps the zoom at 1.15x (15% zoom)
- Adjust `0.003` for faster/slower: 0.002 = more subtle, 0.005 = faster
- For side-by-side: each half is 540×960, final is hstack at 1080×960 then pad/scale to 1080×1920

#### Side-by-Side Layout (Comparison Videos)

Two zoompan outputs → hstack → pad/scale to 1080×1920:

```python
f"[l{i}][r{i}]"
f"hstack=inputs=2,"                          # side by side
f"scale=1080:1920:force_original_aspect_ratio=decrease,"  # fit height
f"pad=1080:1920:(1080-iw)/2:(1920-ih)/2:color=black,"    # center
f"fade=t=in:st=0:d=0.5,"                     # fade in
f"fade=t=out:st={duration-0.5}:d=0.5[s{i}]"  # fade out
```

Then concat all segments:
```python
f"[s0][s1][s2]concat=n=3:v=1:a=0[base]"
```

#### Standard Slideshow (Single Image per Segment)

```python
import subprocess, json

cmd = ["ffmpeg", "-y"]
for img_path in image_paths:
    cmd.extend(["-loop", "1", "-i", str(img_path)])  # NO -t here
cmd.extend(["-i", str(narration_mp3)])

# Filter complex: scale+crop each image, trim, concat, burn captions
filters = []
labels = []
for i, (name, dur) in enumerate(segments):
    filters.append(
        f"[{i}:v]"
        f"scale=1080:1920:force_original_aspect_ratio=increase,"
        f"crop=1080:1920,"
        f"setsar=1,fps=30,format=yuv420p,"
        f"trim=duration={dur},setpts=PTS-STARTPTS[v{i}]"
    )
    labels.append(f"[v{i}]")

filters.append(f"{''.join(labels)}concat=n={len(labels)}:v=1:a=0[base]")

filters.append(
    f"[base]subtitles=captions.srt"
    f":force_style="
    f"'FontName=Arial,FontSize=28,"
    f"PrimaryCol=&H00FFFFFF,OutlineCol=&H00000000,"
    f"BorderStyle=3,Outline=2,Shadow=1,Alignment=2,MarginV=120'[vid]"
)

cmd.extend(["-filter_complex", ";".join(filters)])
cmd.extend(["-map", "[vid]", "-map", f"{len(images)}:a"])
cmd.extend(["-c:v", "libx264", "-preset", "medium", "-crf", "23"])
cmd.extend(["-c:a", "aac", "-b:a", "192k"])
cmd.extend(["-pix_fmt", "yuv420p", "-shortest"])
cmd.append("tiktok_viral.mp4")

process = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
```

#### Critical Windows Pitfalls

1. **SRT path in subtitles filter**: FFmpeg interprets colons as option separators. On Windows, `C:\Users\...` is parsed as `original_size` parameter and crashes. **Always copy SRT to the working directory and use a relative filename.**
2. **`-t` vs `trim=duration`**: `-t` on image inputs is ignored when feeding into `filter_complex`. Use `trim=duration=` inside the filter graph instead.
3. **`-loop 1 -i`**: Required for single-frame image inputs. Without `-loop 1`, FFmpeg reads only one frame and the video ends immediately.

### SRT Caption Generation

Segment the script with approximate start/end times based on total narration duration and character count proportion:

```python
script_lines = [
    ("Your brain is lying to you right now. Here's proof.", 0, 4),
    ("Number 1: The Spotlight Effect.", 11, 13.5),
    # ... time each chunk based on narration pace
]

with open("captions.srt", "w", encoding="utf-8") as f:
    for i, (text, start, end) in enumerate(script_lines, 1):
        start_ts = f"{int(start//3600):02d}:{int(start%3600//60):02d}:{start%60:06.3f}".replace(".", ",")
        end_ts = f"{int(end//3600):02d}:{int(end%3600//60):02d}:{end%60:06.3f}".replace(".", ",")
        f.write(f"{i}\n{start_ts} --> {end_ts}\n{text}\n\n")
```

Trick: generate narration FIRST, listen to it / time it, then calculate caption timings by dividing the total duration proportionally across character count.

### ASS Subtitles (Advanced — For Styled Overlays)

SRT is limited to plain text bottom-center. For **side-by-side comparison** videos with scene titles, side labels, and colored counters, use **ASS (Advanced SubStation Alpha)** instead. ASS supports:
- Per-line positioning (alignment 1-9 on a 3×3 grid)
- Different font sizes, colors, and styles per dialogue line
- Bold, italic, shadow, outline per line
- Soundtrack-quality typesetting

**ASS Style Definitions:**
```
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, Alignment, ...
Style: caption,Arial,30,&H00FFFFFF,2,10,10,120     # bottom center
Style: label_left,Arial,22,&H00FFFFFF,1,20,10,10    # left, top
Style: label_right,Arial,22,&H00FFFFFF,7,10,20,10   # right, top
Style: wealth,Arial,16,&H0000FF00,1,10,10,10        # green, bottom-left
Style: debt,Arial,16,&H006666FF,7,10,10,10          # red, bottom-right
```

**ASS Event Format:**
```
Dialogue: 0,0:00:00.00,0:00:26.00,label_left,,0,0,0,,{\an1}THE SAVER
Dialogue: 1,0:00:00.00,0:00:04.00,caption,,0,0,0,,{\an2}Two people. Same age.
```

**Python ASS Generator:**
```python
def ass_ts(t):
    h = int(t // 3600); m = int((t % 3600) // 60)
    s = int(t % 60); cs = int((t % 1) * 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

def safe(t):
    return t.replace("{","\\{").replace("}","\\}")

ass = [
    "[Script Info]", "ScriptType: v4.00+",
    "PlayResX: 1080", "PlayResY: 1920", "",
    "[V4+ Styles]",
    "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV",
    "Style: caption,Arial,30,&H00FFFFFF,&H00000000,&H00000000,&H80000000,0,0,3,2,1,2,10,10,120",
    "", "[Events]",
    "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
]

# Add scene title
ass.append(f"Dialogue: 0,{ass_ts(0)},{ass_ts(26)},scene_title,,0,0,0,,{{\\an8}}TEENAGE YEARS")

# Add labels
ass.append(f"Dialogue: 0,{ass_ts(0)},{ass_ts(26)},label_left,,0,0,0,,{{\\an1}}THE SAVER")
ass.append(f"Dialogue: 0,{ass_ts(0)},{ass_ts(26)},label_right,,0,0,0,,{{\\an7}}THE SPENDER")

# Add wealth counter
ass.append(f"Dialogue: 0,{ass_ts(0)},{ass_ts(26)},wealth,,0,0,0,,{{\\an1}}SAVED: $5K")

# Add narration caption
ass.append(f"Dialogue: 1,{ass_ts(0)},{ass_ts(4)},caption,,0,0,0,,{{\\an2}}Two people. Same age.")

with open("overlays.ass", "w", encoding="utf-8") as f:
    f.write("\n".join(ass))
```

**Burning ASS into video:**
```python
# Copy ASS to working dir (avoid Windows colon issue in path)
shutil.copy2("output/overlays.ass", "overlays.ass")
cmd = ["ffmpeg", "-y",
    "-i", "base.mp4", "-i", "narration.mp3",
    "-filter_complex", "[0:v]subtitles=overlays.ass[vid]",
    "-map", "[vid]", "-map", "1:a",
    "-c:v", "libx264", "-preset", "fast", "-crf", "23",
    "-c:a", "aac", "-b:a", "192k",
    "-pix_fmt", "yuv420p", "-shortest",
    "final_video.mp4"
]
```

**Alignment guide ({\anN}):**
| Code | Position |
|:----:|:--------:|
| \an1 | Bottom-left |
| \an2 | Bottom-center |
| \an3 | Bottom-right |
| \an4 | Mid-left |
| \an5 | Mid-center |
| \an6 | Mid-right |
| \an7 | Top-left |
| \an8 | Top-center |
| \an9 | Top-right |

## Brainrot / Game-UI HUD Aesthetic (ASS Subtitle Pattern)

The "brainrot" TikTok style features a **static character image** (marble bust, philosopher, skeleton, statue) with **game-style HUD elements** burned in via ASS subtitles. No complex animation needed — the visual impact comes from the overlay layout.

**Core HUD elements (timed via ASS):**

| Element | Position | Style | Example |
|---------|----------|-------|---------|
| LIVE badge | Top-right, {\an9} | Red dot + "LIVE" text | `{\\c&H0000FF&}●{\\c} LIVE` |
| Stat bar | Top-right, below LIVE | Label + bar fill + % | `FINANCIAL IQ ███████░░░ 72%` |
| View counter | Top-right, below bar | Dimmed grey text | `1.2M VIEWS` |
| Impact headers | Center (y=680-840) | Impact font, 64pt, colored | `DEPRECIATING` / `ASSET` |
| Bottom caption | Bottom-center, {\an2} | Arial 24pt, black box bg | Full narration text |

**ASS style definitions for brainrot:**
```
Style: h_white,Impact,64,&H00FFFFFF,..0,3,2,1,5,10,10,60,1
Style: h_gold,Impact,64,&H0000FFD7,..0,3,2,1,5,10,10,60,1
Style: h_red,Impact,64,&H004444FF,..0,3,2,1,5,10,10,60,1
Style: h_green,Impact,64,&H0044FF44,..0,3,2,1,5,10,10,60,1
Style: caption,Arial,24,&H00FFFFFF,..0,3,1,1,2,10,10,60,1
```

**Two-pass approach (reliable on Windows):**
```
PASS 1: FFmpeg scale+crop single image → base video (no overlays)
PASS 2: FFmpeg subtitles=overlays.ass + mux audio → final video
```
PASS 1 uses simple scale+crop (fast). PASS 2 burns subtitles in one go. Avoids complex filter_graph chains and zoompan which is slow on Windows.

**Single-character brainrot format** (Socrates, skeleton, philosopher, etc.):
- One hero image per video (not side-by-side)
- Scale image 15% oversize, crop to 1080x1920 for cinematic close-up feel
- All visual variety comes from ASS timed overlays, not scene cuts
- Script arc: Hook → Setup → Points → Climax → CTA (60s total for TikTok monetization)

## Hitting 60s for TikTok Monetization

TikTok's Creator Rewards Program requires videos >= 60s. When TTS narration comes in under 60s, stretch it with `atempo`:

```bash
# ratio = current_duration / target_duration, e.g. 50.4s → 60s = 0.84x
ffmpeg -y -i narration.mp3 -filter:a "atempo=0.84" -c:a libmp3lame -b:a 128k narration_stretched.mp3
```
atempo preserves pitch (phase vocoder). Ratios below 0.5 need chaining.

## Image Source Fallback Chain

When AI image generation (FAL, GPT-Image) is unavailable, fall back in this order:
1. **Pexels photos API** — free, high-res, portrait orientation. Requires only a free Pexels API key.
2. **Solid-color background with drawtext** — no image needed, just text on a dark canvas.

Pexels photo search:
```python
requests.get("https://api.pexels.com/v1/search",
    params={"query": term, "per_page": 1, "orientation": "portrait"},
    headers={"Authorization": PEXELS_KEY})
```

## Critical Windows FFmpeg Pitfalls

These apply to ALL FFmpeg composition on Windows via MSYS/bash — every session hits these eventually.

### 1. Drawtext: No Unicode / Special Characters in Filter Values

FFmpeg's drawtext filter on Windows chokes on certain characters inside `text=` values:

| Character | Effect | Fix |
|:---------:|:-------|:----|
| ✓ ✗ ♪ → | Crashes filter graph with "No such filter: 'N'" | Replace with ASCII: `[OK]` or text description |
| ' (apostrophe) | Breaks drawtext value parsing at the `'` | Remove or rephrase without apostrophes |
| `$` | May cause shell interpretation issues | Escape or use different phrasing |
| Emoji (😊🎯) | Parsing errors in filtergraph | Avoid entirely in drawtext |

**Safe approach**: Use all-ASCII alphanumeric text in drawtext values. No punctuation that FFmpeg's filter parser could misinterpret.

### 2. Font Loading: Use `font='Name'` — NOT `fontfile=`

On Windows MSYS (git-bash), FFmpeg's fontconfig supports:
```ffmpeg
drawtext=text='Hello':font='Arial':fontsize=24
```

`fontfile=` with absolute Windows paths (`C:\Windows\Fonts\arial.ttf`) requires complex escaping in Python strings and is unreliable. Just use `font='Arial'` — fontconfig resolves it.

```python
# ✅ WORKS — no fontfile needed
"drawtext=text='ALEX':fontcolor=#00ff88:font='Arial':fontsize=60"
```

### 3. Prefer `-vf` Over `-filter_complex` for Simple Drawtext Chains

Chain multiple drawtext filters with comma-separated `-vf` rather than `-filter_complex`:

```python
# ✅ WORKS — simple -vf chain
subprocess.run(["ffmpeg", "-y",
    "-f", "lavfi", "-i", "color=c=black:s=1080x1920:r=30:d=6",
    "-vf",
    "drawtext=text='Title':font='Arial':fontsize=36:x=...,"
    "drawtext=text='Left Label':fontsize=28:x=...,"
    "drawtext=text='Right Label':fontsize=28:x=...",
    "-pix_fmt", "yuv420p", "-r", "30", str(output)
], check=True, timeout=120)
```

### 4. Python subprocess.run with List Args — More Reliable Than Shell Strings

```python
subprocess.run(["ffmpeg", "-y", "-i", path, ...], check=True,
    capture_output=True, text=True, timeout=120)
```

### 5. Trailing-Colon Pitfall in Drawtext Chains

When chaining multiple drawtext filters in `-vf`, the final parameter before the comma filter-separator must NOT end with `:`:

```python
# ✅ CORRECT — comma separates independent drawtext filters
"drawtext=text='ALEX':font='Arial':fontsize=60:..."
# that's it — next filter starts after the comma

# ⚠️ WRONG — trailing colon before comma breaks filter parsing
"drawtext=text='ALEX':font='Arial':,drawtext=text='B':..."  # ❌ ':' before ',' is a parse error
```

Easy to introduce when editing Python string concatenation between two string literals. The `:` separates parameters inside one filter; `,` separates filters in the chain — they must not overlap.

### 6. ElevenLabs Music API (Alternative Premium Music)

The ElevenLabs Music API (`POST https://api.elevenlabs.io/v1/music`, model `music_v2`) can generate studio-quality background tracks from text prompts, but requires the API key to have the `music_generation` permission enabled in the ElevenLabs dashboard. Standard ElevenLabs TTS keys only cover speech synthesis.

```python
# Requires: pip install elevenlabs (minimum v2.53.0)
from elevenlabs import ElevenLabs
client = ElevenLabs(api_key="sk_...")
result = client.music.compose(
    prompt="Motivational corporate track, warm piano, gentle strings, 100 BPM",
    music_length_ms=97000,
    model_id="music_v2",
)
with open("output.mp3", "wb") as f:
    for chunk in result:
        f.write(chunk)
```

For this user: the ElevenLabs key at `~/Documents/Projects/MoneyPrinterTurbo/.elevenlabs_key` has TTS access but needs `music_generation` permission enabled in the dashboard before the Music API will work.

### 7. Render-Per-Segment Then Concat (Avoid Complex Filtergraphs)

Instead of one massive `-filter_complex`, render each segment separately, then concat:

```python
# Step 1: Each segment individually
for i, (args) in enumerate(segments):
    subprocess.run(["ffmpeg", "-y", ...] + seg_args + [f"seg_{i:04d}.mp4"], ...)

# Step 2: Concat list
with open("concat.txt", "w") as f:
    for seg in segments:
        f.write(f"file '{seg.as_posix()}'\\n")

# Step 3: Concat
subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0",
    "-i", "concat.txt", "-c:v", "libx264", "-preset", "medium", "-crf", "22",
    "video_no_audio.mp4"], ...)

# Step 4: Mux audio
subprocess.run(["ffmpeg", "-y", "-i", "video_no_audio.mp4",
    "-i", "mixed_audio.wav",
    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
    "final.mp4"], ...)
```

### 8. Audio Mixing with Ducking

```python
subprocess.run(["ffmpeg", "-y",
    "-i", "narration.mp3", "-i", "bg_music.wav",
    "-filter_complex",
    "[1:a]volume=0.25[a_music];"
    "[a_music]adelay=1|1[a_music_delayed];"
    "[0:a]volume=1.0[a_narration];"
    "[a_narration][a_music_delayed]amix=inputs=2:duration=first[aout]",
    "-map", "[aout]", "-ac", "2", "-ar", "44100",
    "mixed_audio.wav"], check=True, timeout=120)
```

### 9. zoompan + lavfi is Too Slow for Long Videos on Windows

The `zoompan` filter combined with a `lavfi color` source and `overlay` is extremely slow on Windows MSYS for videos over ~30s. A 60s 1080x1920 video with `zoompan` + `lavfi color` can take 2-3x realtime or hang.

**Fix — two-pass approach:**
- PASS 1: Scale+crop the image directly (no zoompan, no lavfi). Just `-loop 1 -i image.jpg -t 60 -filter_complex "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"` with `-preset ultrafast -crf 22`.
- PASS 2: Apply ASS subtitles + mux audio with `-preset superfast`.

For a subtle "zoom" effect, pre-scale the image 115% before cropping:
```python
f"[0:v]scale={int(1080*1.15)}:{int(1920*1.15)}:force_original_aspect_ratio=increase,crop=1080:1920[vid]"
```

### 10. Prefer Direct Scale+Crop Over lavfi + Overlay

For videos with a single static image, apply scale+crop directly on the image input instead of creating a lavfi color source and overlaying. Direct scale+crop is significantly faster.

### 11. Generate Background Music with Python (Cloudflare Bypass)

When Pixabay/Mixkit downloads are behind Cloudflare, generate a simple WAV with numpy:
```python
import numpy as np, wave, struct
SAMPLE_RATE = 44100
# Chord progression (C-G-Am-F), sine waves, add beat, write WAV
```

## Monthly Capacity (per this user)

| Service | Cost/Video | Limit Notes |
|---------|-----------|-------------|
| GPT-Image-1.5 × 7 | ~$0.29 | Unlimited (pay-as-you-go) |
| OpenAI TTS | ~$0.03 | Unlimited |
| FAL FLUX × 7 | ~$0.28 | ~35/mo with $10 top-up |
| **Total per video** | **~$0.32** (GPT-Image path) | |

## Reference Files
## Reference Files

- `references/ffmpeg-composition-recipes.md` — Ready-to-copy FFmpeg command patterns, SRT timing calculator, verification commands, side-by-side Ken Burns recipe, narration generation fix, ASS subtitle templates, audio mixing with ducking, segment-by-segment pipeline, and Python bg music generator.
- `references/brainrot-ass-patterns.md` — ASS subtitle template for brainrot/HUD aesthetic (Socrates skeleton style): styles, HUD elements, impact headers, two-pass pipeline.
- `scripts/python-bg-music-generator.py` — Standalone script to generate corporate-style background music as WAV (bypasses Cloudflare-blocked music sites).
- `templates/ass-subtitle-template.txt` — Reusable ASS subtitle boilerplate with 8 predefined styles for side-by-side comparison videos.

## Related Skills

- `money-printer-turbo` — Different toolchain (MoneyPrinterTurbo project)
- `retro-video-effects` — Post-process output with vintage aesthetic
- `gpt-image-2` — Chinese-lang GPT Image 2 prompt templates
- `tiktok-finance-video` — Two-character comparison format (complementary, not overlapping)
