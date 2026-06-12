---
name: money-printer-turbo
description: "AI short video generation using MoneyPrinterTurbo — script generation from LLM + stock footage assembly + TTS voiceover + subtitle rendering + background music. Full MVC app with Streamlit WebUI, FastAPI, and CLI."
version: 1.0.0
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
- **Config**: Copy `config.example.toml` → `config.toml` with API keys
- **Python**: >=3.11, <3.13

## Required API Keys
| Service | Purpose | Sign Up |
|---------|---------|---------|
| Pexels | Stock video footage | https://www.pexels.com/api/ |
| LLM Provider | Script generation | Pick from 15 supported providers (openai, aihubmix, deepseek, gemini, ollama, etc.) |

See `config.example.toml` for full provider list.

## Usage

### Web UI
```bash
cd ~/Documents/Projects/MoneyPrinterTurbo
uv run streamlit run ./webui/Main.py --browser.gatherUsageStats=False
```
Opens at `http://localhost:8501`

### API
```bash
uv run python main.py
```
API docs at `http://localhost:8080/docs`

### CLI
```bash
uv run python cli.py --video-subject "Your video topic here"
```

Local materials:
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

## Integration Notes
- No existing Hermes skill overlaps with MoneyPrinterTurbo's capability — it fills a gap in **AI video generation**
- The `video_generate` Hermes tool provides image-to-video animation; MoneyPrinterTurbo provides the full **script→assembly→render** pipeline — complementary
- Uses `Edge TTS` for voiceover (same TTS engine available via Hermes `text_to_speech` tool)

## Related Skills
- `media/video-edit` — Edit existing video
- `media/gif-search` — Search/download GIFs
- `media/songsee` — Audio spectrogram analysis
- `software-development/repo-integration-reconciliation` — Skill audit and reconciliation for new repos
