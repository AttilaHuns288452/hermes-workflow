---
name: money-printer-turbo
description: "AI short video generation using MoneyPrinterTurbo — script generation from LLM + stock footage assembly + TTS voiceover + subtitle rendering + background music. Full MVC app with Streamlit WebUI, FastAPI, and CLI."
version: 1.2.0
triggers:
  - "generate a short video"
  - "money printer"
  - "AI video generation"
  - "short video from prompt"
---

# MoneyPrinterTurbo — AI Short Video Generation

## Role
Generate short-form videos (vertical 9:16 or horizontal 16:9) from a text prompt or keyword. The pipeline: **LLM script generation → stock footage search → TTS voiceover → subtitle rendering → background music → final video assembly**. Full MVC app with Streamlit Web UI, FastAPI, and Python CLI.

**Repo**: [harry0703/MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo) (MIT, 86.1k ⭐, Python 97.8%)

## Prerequisites
- **Repo cloned**: `~/Documents/Projects/MoneyPrinterTurbo/`
- **Deps installed**: `uv sync --frozen` (already done)
- **Config**: Copy `config.example.toml` → `config.toml` with API keys (**MANDATORY** — nothing works without it)
- **Python**: >=3.11, <3.13
- **Windows activation**: On Windows (git-bash), activate via `source .venv/Scripts/activate` before running. (The `uv run` examples below also work.)

## Required API Keys
| Service | Purpose | Sign Up |
|---------|---------|---------|
| **Pexels** | Stock video footage | https://www.pexels.com/api/ (free, required for stock clips) |
| **LLM Provider** | Script generation | Pick from 15+ supported providers (openai, aihubmix, deepseek, gemini, ollama, etc.) |

See `config.example.toml` for the full provider list.

### FreeLLMAPI as LLM Provider (Local, Free)
If you run [FreeLLMAPI](http://localhost:3001/v1) locally, wire it as an OpenAI-compatible endpoint in `config.toml`:
```toml
llm_provider = "openai"
openai_api_key = "sk-dummy"           # FreeLLMAPI doesn't validate the key
openai_base_url = "http://localhost:3001/v1"
openai_model_name = "gpt-4o-mini"     # FreeLLMAPI routes to its own backend
```
FreeLLMAPI must be running (`node server/index.js` from its project dir) before MoneyPrinterTurbo calls the LLM. If it's offline, script generation hangs — use `--video-script` (custom script) to bypass.

## Usage

### CLI — Testing with Custom Script
Use `--stop-at` to validate each pipeline stage without needing API keys:
```bash
# Test just the script step (no LLM needed with --video-script)
uv run python cli.py \
  --video-subject "Any Topic" \
  --video-script "Your story text here." \
  --voice-name "en-US-AriaNeural" \
  --stop-at script

# Stop after audio generation
uv run python cli.py ... --stop-at audio

# Full video (default)
uv run python cli.py ... --stop-at video
```
Available stages: `script` → `terms` → `audio` → `subtitle` → `materials` → `video` (default).

### Web UI
```bash
uv run streamlit run ./webui/Main.py --browser.gatherUsageStats=False
```
Opens at `http://localhost:8501`

### API
```bash
uv run python main.py
```
API docs at `http://localhost:8080/docs`

### Full CLI
```bash
uv run python cli.py --video-subject "Your video topic here" --voice-name "en-US-AriaNeural"
```

### Local Materials (no stock footage needed)
```bash
uv run python cli.py \
  --video-subject "Your topic" \
  --video-source local \
  --video-materials "1.mp4,2.mp4" \
  --stop-at video
```

## Key Features
- **AI script generation** via 15+ LLM providers (OpenAI, DeepSeek, Gemini, Ollama, etc.)
- **Stock footage** from Pexels, Pixabay, Coverr
- **TTS** Edge TTS (free), Azure TTS V2 (premium)
- **Subtitles** edge (fast) or whisper (accurate) — whisper needs local model download
- **Background music** random or custom
- **Batch generation** — multiple videos at once
- **Vertical (9:16, 1080x1920)** and **Horizontal (16:9, 1920x1080)**
- **Chinese & English** script support

## Voice Guide for Dramatic / Cinematic Narration

Not all voices are equal for storytelling videos. The "skeleton AI" narrator style uses a **deep, calm, authoritative** male voice at a **slower pace**.

| Goal | Recommended Voice | Voice Rate |
|---|---|---|
| Skeleton AI / ominous narrator | `en-US-ChristopherNeural` | `0.80` (20% slower) |
| Inspiring / motivational | `en-US-RogerNeural` | `0.85` |
| General storytelling | `en-US-GuyNeural` | `0.90` |
| Default / all-purpose | `en-US-AriaNeural` | `1.0` |

**Important:** The CLI only exposes `--voice-name` for voice selection. To adjust **voice_rate** (speed/pacing), use the Python script approach in `references/cinematic-dramatic-narration.md` — it creates a `VideoParams` object with full control over `voice_name`, `voice_rate`, and other parameters not exposed through the CLI.

## Integration Notes
- No existing Hermes skill overlaps with MoneyPrinterTurbo's capability — it fills a gap in **AI video generation**
- The `video_generate` Hermes tool provides image-to-video animation; MoneyPrinterTurbo provides the full **script→assembly→render** pipeline — complementary
- Uses `Edge TTS` for voiceover (same TTS engine available via Hermes `text_to_speech` tool)
- See `references/tiktok-ai-storytelling.md` for the AI-generated storytelling TikTok niche (scripts, hooks, monetization pipeline)
- See `references/cinematic-dramatic-narration.md` for voice selection, voice rate adjustment, cinematic script craft, and disk-efficient direct ffmpeg assembly

## Windows Pitfalls & Workarounds

This project was built primarily for Linux/macOS. On Windows (git-bash/MSYS) the following issues recur — use the workarounds below.

### BrokenPipeError During Final Encoding

**Symptom:** `OSError: [Errno 32] Broken pipe` during `write_videofile`. MoviePy's internal FFmpeg writer often fails on Windows.

**Fix** — the temp clips and audio are fine; manually concat + merge with ffmpeg:
```bash
# After the CLI fails, the task dir has temp-clip-*.mp4 + audio.mp3
TASK_DIR="storage/tasks/<task-uuid>"
ffmpeg -y -f concat -safe 0 -i "$TASK_DIR/ffmpeg-concat-list.txt" \
  -c:v libx264 -preset fast -crf 23 -pix_fmt yuv420p -movflags +faststart \
  "$TASK_DIR/combined-manual.mp4"
ffmpeg -y -i "$TASK_DIR/combined-manual.mp4" -i "$TASK_DIR/audio.mp3" \
  -c:v copy -c:a aac -b:a 128k -shortest -movflags +faststart \
  "$TASK_DIR/tiktok-final.mp4"
```

### Subtitle / Whisper Model Delays

**Symptom:** The `edge` subtitle provider can fail on short or punctuation-heavy scripts (cues don't match text). The fallback to `whisper` downloads the **~3GB large-v3 model** on first use, which can timeout or fill your disk.

**Prevention:**
- Set `subtitle_provider = ""` in `config.toml` to skip subtitles entirely
- Or use `--no-subtitle-enabled` on the CLI
- Or pre-download a smaller Whisper model if subtitles are critical

### LLM Hangs When FreeLLMAPI/Provider Is Offline

**Symptom:** Generating script hangs indefinitely if the LLM provider can't be reached (FreeLLMAPI not running, API key missing, etc.).

**Fix** — bypass the LLM entirely by providing both `--video-script` AND `--video-terms`:
```bash
python cli.py \
  --video-subject "Topic" \
  --video-script "Your custom story text here." \
  --video-terms "keyword1, keyword2, keyword3" \
  --voice-name "en-US-AriaNeural" \
  --video-aspect "9:16" \
  --no-subtitle-enabled
```
The `--video-terms` are keywords for stock footage search (Pexels/Pixabay). Compose them manually to cover the visual arc of your story.

### Long Videos Time Out (50+ seconds)

**Symptom:** The `combine_videos` step processes each clip sequentially via FFmpeg subprocess and can take 2+ minutes for longer videos, hitting the terminal timeout.

**Workaround:** Increase timeout when calling from terminal, or let the temp clips generate and manually concat (see BrokenPipeError fix above — same manual ffmpeg concat approach works).

### Disk Space on Windows C:\

**Symptom:** `Errno 28` No space left on device during clip encoding. MoneyPrinterTurbo writes many temp files to `storage/cache_videos/` and `storage/tasks/<uuid>/`.

**Prevention:**
- Clean old task dirs: `rm -rf storage/tasks/<old-uuids>/`
- Cache videos persist — reuse them instead of re-downloading
- Monitor with `df -h /c/` — keep >20GB free

### Script: One-Shot Story Generator (Standard)

See `templates/generate-story.sh` — ready-to-use Bash script:
1. Activates the venv
2. Runs CLI: story → TTS → Pexels footage → video
3. Auto FFmpeg fallback when MoviePy crashes (BrokenPipeError)
4. Outputs to `storage/tasks/<uuid>/tiktok-final.mp4`

Usage:
```bash
bash templates/generate-story.sh "Your story here" "keyword1, keyword2, keyword3" "en-US-ChristopherNeural" 1.05
```

### Script: Sophisticated Production (Retention-Engineered)

See `templates/build_sophisticated.sh` — **production-grade builder** with precise visual-audio lock via ffmpeg filter_complex:
- 18-segment script → 18 cached videos picked by duration match
- Each clip trimmed to EXACT narration duration (no "crisps" artifacts)
- Single-pass encode, 1080x1920@30fps, ~89s output
- Requires pre-generated audio (`voice-samples/sophisticated_money.mp3`)

Usage:
```bash
# 1. Generate audio first
python gen_sophisticated.py

# 2. Build video (picks best cached clips automatically)
bash templates/build_sophisticated.sh
```

### ✅ Proper Pipeline Usage (Fresh Pexels + Frame-Perfect Sync)

**The repo's intended workflow** — use the CLI to download **fresh, relevant footage per search term**, then assemble with frame-perfect ffmpeg `filter_complex`:

```bash
# 1. Run pipeline UP TO materials (stops before broken final concat)
python run_pipeline.py
# → downloads 17 Pexels clips matching 17 search terms in script order
# → generates audio.mp3 via Edge TTS
# → saves to storage/tasks/<uuid>/
# #
# run_pipeline.py provides:
#   - Custom sophisticated script (not LLM-generated)
#   - 17 precise search terms (one per script beat, in order)
#   - VideoParams with stop_at="materials", subtitle_enabled=False
#   - voice_name="en-US-ChristopherNeural"

# 2. Frame-perfect assembly from pipeline materials
python build_from_pipeline.py
# → Reads fresh downloads (newest 17 in cache_videos/)
# → Trims each clip to match its segment's word-count proportion
# → Single-pass ffmpeg filter_complex concat + audio overlay
# → Output: storage/tasks/<uuid>/pipeline-final.mp4
```

**Key files created this session:**
- `run_pipeline.py` — runs MoneyPrinterTurbo pipeline to `stop_at="materials"` with custom script + 17 ordered search terms
- `build_from_pipeline.py` — assembles using ffmpeg `filter_complex` with proportional timing (word-count based)
- `gen_sophisticated.py` — generates retention-engineered audio (ChristopherNeural +5%)

**Why this beats manual clip picking:**
| Manual | Pipeline Proper |
|--------|-----------------|
| Random cached clips | **Fresh downloads per exact search term** |
| Guesswork timing | **Proportional** — each clip trimmed to its segment's word count |
| 13–18 clips, mismatched | **17 clips in script order** — term 1→clip 1, term 2→clip 2 |
| BrokenPipeError concat | **filter_complex** — single-pass, frame-perfect, no artifacts |

---

### 🎯 Production Workflow: ElevenLabs + Fresh Pipeline (Recommended)

**Best of both worlds:** Premium voice (ElevenLabs Adam) + fresh relevant footage + frame-perfect sync.

```bash
# 1. Generate ElevenLabs audio (Adam voice, eleven_flash_v2_5 model)
python scripts/gen_elevenlabs.py
# → voice-samples/elevenlabs_sophisticated.mp3 (~80s, ~1.3MB)

# 2. Run MoneyPrinterTurbo pipeline to materials (fresh Pexels per term)
python scripts/run_pipeline.py
# → storage/tasks/<uuid>/audio.mp3 (Edge TTS, ignored)
# → 17 fresh Pexels clips downloaded to cache_videos/ in term order

# 3. Frame-perfect assembly with ElevenLabs audio
python scripts/build_elevenlabs.py
# → Reads the 17 fresh downloads (newest 17 in cache_videos/)
# → Trims each clip to its segment's word-count proportion
# → Overlays ElevenLabs audio (not the Edge TTS audio)
# → Single-pass filter_complex: 1080x1920@30fps
# → Output: storage/tasks/<uuid>/elevenlabs-final.mp4
```

**Files in `scripts/` (ready to copy):**
| File | Purpose |
|------|---------|
| `gen_elevenlabs.py` | Generates ElevenLabs audio with Adam voice, `eleven_flash_v2_5` model |
| `run_pipeline.py` | Runs MoneyPrinterTurbo pipeline to `stop_at="materials"` with 17 ordered search terms |
| `build_elevenlabs.py` | Assembles using ffmpeg filter_complex with word-count proportional timing + ElevenLabs audio |
| `build_from_pipeline.py` | Assembles using pipeline's own Edge TTS audio (when not using ElevenLabs) |

**Why this is the production standard:**
- ✅ **Voice quality**: ElevenLabs Adam (indistinguishable from human)
- ✅ **Visual relevance**: Fresh Pexels downloads per exact script beat
- ✅ **Perfect sync**: Word-count proportional trim per segment
- ✅ **Zero artifacts**: Single-pass filter_complex (no MoviePy, no re-encode)
- ✅ **Fast**: ~3 minutes total (audio gen + pipeline download + ffmpeg)
- ✅ **Free tier compatible**: 10k chars/mo ElevenLabs + free Pexels API


## Voice Quality Reality Check

**Edge TTS is identifiably AI.** ChristopherNeural (+5% rate) is the best free option but still has the "crisp" artifacts that make AI-generated TikToks feel synthetic.

| Provider | Voices | Cost | Quality for "Skeleton Socrates" |
|----------|--------|------|--------------------------------|
| **Edge TTS** (built-in) | ChristopherNeural, RogerNeural, GuyNeural | Free | ❌ Detectable AI — "crisps" on consonants |
| **ElevenLabs** | **Adam (pNInz6obpgDQGcFmaJgB)**, Daniel, Roger | **Free tier: 10k chars/mo** (`eleven_flash_v2_5`) | ✅ Gold standard — indistinguishable from human |
| **OpenAI TTS** | Onyx (deep), Echo (authoritative) | ~$15/1M chars | ✅ Excellent — very natural pacing |
| **Azure TTS** | ChristopherNeural (premium), RyanMultilingual | Free tier → pay | ✅ Better than Edge — cleaner high-end |

**ElevenLabs Free Tier — Critical Model Note:**
- **Deprecated:** `eleven_monolingual_v1` and `eleven_multilingual_v1` — NOT available on free tier
- **Use:** `eleven_flash_v2_5` (fast, free tier compatible) or `eleven_multilingual_v2`
- **Voice ID for "Skeleton Socrates":** `pNInz6obpgDQGcFmaJgB` (Adam — deep, authoritative male)
- **Settings for narration:** `stability=0.5, similarity_boost=0.75, style=0.3, use_speaker_boost=true`

**To use ElevenLabs in MoneyPrinterTurbo (config.toml):**
```toml
tts_provider = "elevenlabs"
elevenlabs_api_key = "sk_..."  # Your API key
elevenlabs_voice_id = "pNInz6obpgDQGcFmaJgB"
elevenlabs_model_id = "eleven_flash_v2_5"  # Critical for free tier
```

**Or bypass CLI entirely — generate audio directly, then assemble (RECOMMENDED for free tier):**
```python
# see scripts/gen_elevenlabs.py and scripts/build_elevenlabs.py
# 1. Generate ElevenLabs audio (Adam, eleven_flash_v2_5)
# 2. Run MoneyPrinterTurbo pipeline to stop_at="materials" (fresh Pexels downloads)
# 3. Frame-perfect assembly via ffmpeg filter_complex (word-count proportional timing)
```

**Voice rate for cinematic narration:**
- Edge TTS: use `rate="-15%"` to `"+5%"` in python scripts (Sophisticated: +5-8%)
- VideoParams: `voice_rate=1.05` for sophisticated pacing (1.0 = normal)
- **Skeleton Socrates sweet spot:** 
  - Edge TTS: ChristopherNeural +5% (rate=1.05)
  - ElevenLabs: Adam (voice_id `pNInz6obpgDQGcFmaJgB`) at default rate (1.0) — naturally authoritative

## Sophisticated Script Psychology (Retention Engineering)

**No "STOP scrolling" cheap hooks.** Use behavioral finance psychology:

| Framework | Implementation | Script Position |
|-----------|----------------|-----------------|
| **Information Gap (Loewenstein)** | Question creates knowledge gap: *"What if the wealthiest person you know isn't the one with the highest salary?"* | Hook (0:00–0:04) |
| **Identity Signaling** | *"They don't talk about money. They talk about ownership"* — viewer self-identifies as insider | 0:04–0:08 |
| **Authority + Specificity** | Names **Kiyosaki**, cites **$500k lawyer vs $80k plumber** — concrete numbers = credibility | 0:32–0:40 |
| **Loss Aversion (Kahneman/Tversky)** | Frames house/car as *liabilities draining wealth* — loss frame > gain frame | 0:40–0:48 |
| **Agency Restoration** | *"Every dollar votes for who you're becoming"* — gives control back | 0:48–0:52 |
| **Identity Question Close** | *"Does this make me an owner... or a renter?"* + *"What did you choose today?"* — self-reflection loop, drives rewatch | 0:52–1:04 |

**Completion Loop Mechanics:**
1. Question at start → answered mid-video → final question loops to rewatch
2. Micro-cliffhangers every 4–5s: *"The difference was..."*, *"It was THIS decision..."*, *"That's not an accident..."*
3. Three open loops opened (millionaire→building, decision→result, accident→freedom) — all closed by end
4. Relatability anchors: "gas money", "school taught triangles", "grandkids", "sleepwalking"

**Visual-Audio Lock (Required for Retention):**
- 17–18 script segments, each with its own search term
- Clips downloaded in term order (Pexels returns relevant results)
- Each clip trimmed to EXACT segment duration (word-count proportion)
- Single-pass `filter_complex` encode — no generation loss, no "crisps" from re-encoding

**Script Template (Sophisticated Money Psychology):**
```
[HOOK]          Counter-intuitive question (Information Gap)
[IDENTITY]      "They don't talk X. They talk Y." (Identity)
[CONTRAST]      Specific A vs B with numbers (Authority)
[TIME JUMP]     10yr/20yr payoff (Delayed gratification)
[REVEAL]        Core principle (Kiyosaki/asset vs liability)
[PAIN POINT]    "Nobody tells you..." (Conspiracy hook)
[REFRAME]       "Not about money. About FREEDOM." (Identity shift)
[AGENCY]        "Every dollar votes..." (Control restoration)
[DECISION]      Binary choice: Owner or Renter? (Self-reflection)
[LOOP]          "What did YOU choose today?" (Rewatch trigger)
```

## Post-Processing: Retro/VHS Effects

After generating a video with MoneyPrinterTurbo, apply vintage aesthetic effects using `media/retro-video-effects`:

```bash
# 1. Generate source video (this skill)
# 2. Apply retro effects (retro-video-effects skill)
```

See `media/retro-video-effects` for the full VHS effect library: sepia tone, film grain, vignette, CRT scanlines, tracking errors, color flicker — designed specifically for short-form AI-generated video content.

**Production workflow (two-pass ffmpeg, ~4 min for 80s):**
```bash
# PASS 1: Raw concat of MoneyPrinterTurbo pipeline clips
python scripts/build_from_pipeline.py
# → storage/tasks/<uuid>/pipeline-final.mp4

# PASS 2: Apply VHS effects to the concatenated video
python media/retro-video-effects/build_vhs_fast.py  # Two-pass approach
```

**Quick integration:** The `media/retro-video-effects` skill provides numpy-based frame functions that work on any VideoFileClip output. Run from the same venv after installing `moviepy`.

## Related Skills
- `media/retro-video-effects` — Apply VHS/90s/CRT retro aesthetic to AI-generated video (post-processing layer for MoneyPrinterTurbo output)
- `media/video-edit` — Edit existing video on RunComfy
- `media/gif-search` — Search/download GIFs
- `media/songsee` — Audio spectrogram analysis
- `software-development/repo-integration-reconciliation` — Skill audit and reconciliation for new repos

## MoneyPrinterV2 — Local Neural TTS + Custom Pipeline

**Repo:** [FujiwaraChoki/MoneyPrinterV2](https://github.com/FujiwaraChoki/MoneyPrinterV2)
**Location:** `~/Documents/Projects/MoneyPrinterV2/` (Python 3.11+ venv at `venv/Scripts/activate`)

MoneyPrinterV2 is the successor project with different focus areas:
- **Youtube Shorts Automator** (with cron/scheduler)
- **Twitter/X Bot** (with scheduled posting)
- **Affiliate Marketing** (Amazon + Twitter integration)
- **Local Business Outreach** (cold email pipeline)

Not a **replacement** for MoneyPrinterTurbo's video generation — they serve different niches. MoneyPrinterTurbo focuses on the **script→stock footage→video** pipeline, while V2 focuses on **social media automation + monetization**.

**When to use V2 environment:**
- KittenTTS (local neural TTS) — generates higher-quality voiceovers than Edge TTS offline
- MoviePy v2 is available in V2's venv (not in Turbo's) for VHS/retro post-processing
- All ffmpeg operations work the same from either venv

### KittenTTS — Local Neural TTS Engine

MoneyPrinterV2 ships with KittenTTS, a HuggingFace-based local neural TTS model that runs entirely offline:

| Property | Value |
|----------|-------|
| **Model** | `KittenML/kitten-tts-mini-0.8` |
| **Voice** | `"Jasper"` (a single neutral male voice) |
| **Sample Rate** | 24000 Hz |
| **Output** | WAV file (convert to MP3 for ffmpeg: `ffmpeg -i input.wav -codec:a libmp3lame -b:a 192k input.mp3`) |
| **Size** | ~1.5 GB model download on first use |
| **First run** | Downloads model from HuggingFace (requires internet) |

**Usage from MoneyPrinterV2 venv:**
```python
from kittentts import KittenTTS as KittenModel
import soundfile as sf

model = KittenModel("KittenML/kitten-tts-mini-0.8")
audio = model.generate("Your script text here.", voice="Jasper")
sf.write("output.wav", audio, 24000)
```

**KittenTTS vs Other TTS Options:**

| Provider | Quality | Cost | Offline? | Use Case |
|----------|---------|------|----------|----------|
| Edge TTS (Turbo) | Good, detectable AI | Free | No | Quick drafts, prototyping |
| **KittenTTS** (V2) | **Very good, natural** | **Free** | **Yes** | **Solo creator, no API budget, offline-first** |
| ElevenLabs Adam | Gold standard, human-like | Free tier (10k chars/mo) | No | Production, monetized content |
| OpenAI TTS | Excellent, flexible | $15/1M chars | No | High-budget production |

### Cross-Repo Custom Pipeline (KittenTTS + Pexels + VHS)

This is the **recommended standalone pipeline** for creating a VHS/90s radio-style video using a user-provided script (no LLM script generation needed). It combines:
- **MoneyPrinterV2's venv** (KittenTTS + MoviePy v2)
- **MoneyPrinterTurbo's Pexels cache** (stock footage clips)
- **MoneyPrinterTurbo's Pexels API key** (shared via `config.toml`)
- **ffmpeg filter_complex** (frame-perfect sync + VHS effects)

**Pexels key sharing:** MoneyPrinterTurbo's key in `config.toml` can be read by scripts running from MoneyPrinterV2's venv:
```python
import tomllib
with open(r"C:\Users\YOUR_USERNAME\Documents\Projects\MoneyPrinterTurbo\config.toml", "rb") as f:
    cfg = tomllib.load(f)
pexels_key = cfg.get("pexels_api_keys", [""])[0]
```

**Standalone script:** See `scripts/mpv2_custom_video.py` — a complete, ready-to-run script that:
1. Generates KittenTTS neural audio from a user-provided story script
2. Downloads Pexels clips per custom search terms (one per story beat)
3. Applies VHS radio aesthetic (sepia + vignette + scanlines)
4. Renders 1080×1920 @ 30fps with H.264 quality preset (CRF 20, AAC 256k)
5. Outputs to MoneyPrinterV2 root as `mpv2_custom_final.mp4`

```bash
cd ~/Documents/Projects/MoneyPrinterV2
source venv/Scripts/activate
python scripts/mpv2_custom_video.py
# Wait ~5 min for high-quality render
# Output: mpv2_custom_final.mp4
```

### When to Use Each Venv

| Task | Venv | Reason |
|------|------|--------|
| MoneyPrinterTurbo native pipeline (CLI, WebUI) | Turbo `.venv` | App dependencies |
| Pexels clip download | Either | HTTP API calls only |
| KittenTTS voice generation | **V2** `venv` | Only place KittenTTS is installed |
| ffmpeg concat + effects | Either | System-level ffmpeg |
| MoviePy numpy effects (slow) | **V2** `venv` | MoviePy v2 only in V2 |
| ElevenLabs audio generation | Either | HTTP API only |
