---
name: money-printer-v2
description: "AI short video generation using MoneyPrinterV2 — KittenTTS local neural TTS, custom scripts, Pexels stock footage, ffmpeg assembly. Post-production via retro-video-effects for VHS/retro aesthetic."
version: 1.0.0
tags:
  - money-printer-v2
  - kittentts
  - short-form-video
  - tiktok
  - youtube-shorts
  - financial-education
triggers:
  - "use money printer v2"
  - "create a video with money printer v2"
  - "money printer v2 pipeline"
  - "kittentts voice generation"
  - "generate video from my script"
  - "tiktok video generation"
---

# MoneyPrinterV2 — AI Short Video Generation

## Role
Generate AI-powered short-form vertical videos (TikTok / YouTube Shorts) using the MoneyPrinterV2 project as a local base. Uses **KittenTTS** (local neural TTS, no API key needed), Pexels stock footage, and ffmpeg for assembly. The user provides their **own scripts** — not LLM-generated. Post-process with `media/retro-video-effects` for VHS/90s aesthetic.

> **This is NOT MoneyPrinterTurbo.** MoneyPrinterV2 is a separate project at `~/Documents/Projects/MoneyPrinterV2/` with its own venv, KittenTTS, and YouTube automation features. This skill covers using it as a **local video generation base** — not its full YouTube/Ollama automation pipeline.

## Project Structure

```
~/Documents/Projects/MoneyPrinterV2/
├── venv/                     # Python venv (KittenTTS, MoviePy, etc.)
├── .mp/                      # Generated audio, temp files
├── src/                      # Original source (YouTube, Twitter, etc. — not used here)
├── build_vhs_*.py            # Custom build scripts (created per-session)
├── mpv2_gen.py               # Pipeline script (written per-video)
├── mpv2_original_*.mp4       # Generated video output
└── config.json               # Project config (not needed for our pipeline)
```

**Pexels video cache:** shared with MoneyPrinterTurbo at `~/Documents/Projects/MoneyPrinterTurbo/storage/cache_videos/`

## Pipeline Steps

### 1. Write the User's Script
The user provides their own story. Format it as a plain string with natural sentence breaks. The script becomes the narration.

```python
STORY = """Two kids grow up in the same neighborhood. One saves. The other spends. ..."""
```

### 2. Generate Audio with KittenTTS
KittenTTS is a local neural TTS model from HuggingFace. First call downloads the model (~600MB). No API key needed.

```python
from kittentts import KittenTTS as KittenModel
import soundfile as sf
import os

# Must be in MoneyPrinterV2 venv (it has kittentts installed)
ROOT = r"C:\Users\Attila\Documents\Projects\MoneyPrinterV2"
os.chdir(ROOT)

model = KittenModel("KittenML/kitten-tts-mini-0.8")
audio = model.generate(STORY, voice="Jasper")  # "Jasper" is the only local voice

# Save as WAV for editing, MP3 for ffmpeg
wav_path = os.path.join(ROOT, ".mp", "story.wav")
sf.write(wav_path, audio, 24000)

# Convert to MP3 (ffmpeg handles MP3 better than WAV)
subprocess.run(['ffmpeg','-y','-i',wav_path,'-codec:a','libmp3lame','-b:a','256k',mp3_path])
```

**Settings:**
- Sample rate: 24000 Hz (fixed by KittenTTS)
- Model: `KittenML/kitten-tts-mini-0.8`
- Voice: `"Jasper"` (only option)
- Quality: local neural TTS, no artifacts, natural delivery

**Alternative TTS:**
- **ElevenLabs** for premium quality (free tier: `eleven_flash_v2_5`, voice `"Adam"` ID `pNInz6obpgDQGcFmaJgB`). Use `media/money-printer-turbo` skill for ElevenLabs integration.

### 3. Download Pexels Clips
Search Pexels for stock footage matching each story beat. **Simple search terms** outperform complex phrases:

| ✅ Good | ❌ Bad |
|---------|-------|
| "wealthy person walking" | "elderly man same old job tired financial struggle" |
| "lawyer luxury car" | "mirror reflection two different lives" |
| "grandfather handing keys" | "clock time money metaphor" |

Use the Pexels API key from MoneyPrinterTurbo's `config.toml`:

```python
PEXELS_KEY = "..."  # from ~/Documents/Projects/MoneyPrinterTurbo/config.toml
PEXELS_URL = "https://api.pexels.com/videos/search"

def search_pexels(term):
    r = requests.get(PEXELS_URL, params={"query": term, "per_page": 1, "orientation": "portrait"},
                     headers={"Authorization": PEXELS_KEY}, timeout=15)
    if r.status_code == 200:
        return r.json().get("videos", [])
    return []
```

Download to the shared cache at MoneyPrinterTurbo's `storage/cache_videos/`.

### 4. Build the Video (ffmpeg Two-Pass)

**Two-pass approach** (faster than per-clip effects):

#### Pass 1: Raw Concat
Trim each clip to its segment duration (word-count proportional timing), scale+pad to 1080×1920, concat with audio.

```python
total_words = sum(len(s.split()) for s in sentences)
time_alloc = [(len(s.split()) / total_words) * audio_dur for s in sentences]
```

#### Pass 2: Apply VHS Effects
See `media/retro-video-effects` for the full ffmpeg filter chain. Standard sepia+vignette+scanlines:

```python
colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131,vignette
```

Add `noise=alls=6:allf=t+u` for film grain (adds ~2-3 min render time).

#### Quality Render Settings

| Setting | Value |
|---------|-------|
| Codec | libx264 |
| Preset | slow |
| CRF | 16 |
| Min bitrate | 6000k |
| Pix format | yuv420p |
| FPS | 30 |
| Audio | AAC 256-320k |
| Resolution | 1080×1920 (portrait 9:16) |

```bash
ffmpeg -y -i raw_concat.mp4 -i audio.mp3 \
  -filter_complex '[0:v]colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131,vignette[outv]' \
  -map '[outv]' -map '1:a' \
  -c:v libx264 -preset slow -crf 16 -b:v 6000k \
  -pix_fmt yuv420p -r 30 \
  -c:a aac -b:a 320k \
  output.mp4
```

## TikTok Upload Pack

```python
caption = f"""{STORY[:200]}

{', '.join(hashtags[:5])}"""

hashtags = [
    "#financialliteracy", "#wealthbuilding", "#moneymindset",
    "#generationalwealth", "#personalfinance", "#investing",
    "#AIgenerated", "#moneytips", "#financialfreedom"
]
```

Label as `#AIgenerated` on upload per platform policy.

## Advanced: Using User's Original Script (Not LLM-Generated)

Unlike MoneyPrinterTurbo's built-in pipeline which generates scripts from a niche + topic, MoneyPrinterV2 can use **any text the user provides**. The pipeline is:

```
User story → KittenTTS neural TTS → Search terms (1 per sentence) → 
Pexels download → Proportional timing → ffmpeg concat → 
VHS effects → Output
```

Key: Convert the story into search terms that visually represent each beat. Keep terms simple (2-5 words, concrete nouns).

## Integration with Other Skills

| Skill | When to Use |
|-------|-------------|
| `media/retro-video-effects` | Apply VHS/90s/radio aesthetic to the output |
| `media/money-printer-turbo` | ElevenLabs TTS integration, Pexels cache access, alternative pipeline |
| `media/youtube-content` | Repurpose existing YouTube content into scripts |

## Related Skills
- `media/money-printer-turbo` — Alternative tool for video generation (different TTS, no KittenTTS)
- `media/retro-video-effects` — VHS/retro post-processing for any video output
