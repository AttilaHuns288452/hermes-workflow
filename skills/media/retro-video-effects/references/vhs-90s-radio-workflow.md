# VHS 90s Radio-Style Video Workflow

## Session Context (2026-06-16)
Created a 90s radio/documentary style video from MoneyPrinterTurbo pipeline output + ElevenLabs "Adam" voice.

## Full Workflow

### 1. Generate 90s-Themed Clips (MoneyPrinterTurbo Pipeline)
```bash
# Use run_pipeline.py with 90s search terms
# Terms used:
90s wealthy businessman office
90s generational wealth family
90s business owner keys office
90s luxury car parking lot
90s plumber van work
90s grandfather giving keys family
90s overdue bills family
90s decision crossroads
90s Robert Kiyosaki book
90s savings account passbook
90s house mortgage papers
90s rental property keys
90s voting ballot metaphor
90s bank card shopping
90s fork in road decision
90s alarm clock morning
90s mirror reflection morning
```

### 2. Generate ElevenLabs Audio
```python
# Model: eleven_flash_v2_5 (only free-tier-compatible model)
# Voice: Adam (pNInz6obpgDQGcFmaJgB)
# Script: Sophisticated wealth psychology (18 segments)
```

### 3. Compose with VHS Effects (Two Options)

**Option A: MoviePy (Slow, Custom Effects)**
```bash
# located at: MoneyPrinterV2/build_vhs_radio.py
# applies: sepia + grain + vignette + scanlines
# 17 Pexels clips → effects → concat → ElevenLabs audio
# Output: MoneyPrinterV2/vhs_90s_radio_final.mp4
# Time: ~30 min for 80s video
```

**Option B: ffmpeg Two-Pass (Fast, Production)**
```bash
# located at: MoneyPrinterV2/build_vhs_fast.py
# PASS 1: Raw concat with trim + scale (no effects) — ~15s
# PASS 2: VHS effects (curves=vintage + noise=alls=6 + vignette + drawbox scanlines) — ~4 min
# Uses lighter filter chain that avoids timeout:
#   colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131,
#   curves=preset=vintage,
#   noise=alls=6:allf=t+u,
#   vignette,
#   drawbox=x=0:y=0:w=iw:h=1:color=white@0.08:t=fill
#   drawbox=x=0:y=ih-1:w=iw:h=1:color=white@0.08:t=fill
# Audio: ElevenLabs Adam (eleven_flash_v2_5)
# Output: MoneyPrinterV2/vhs_90s_radio_final.mp4
# Time: ~4-5 min total
```

## Key Decisions
- **Python env**: MoneyPrinterV2's venv (Python 3.11.9, MoviePy 2.2.1)
- **MoviePy v2 API**: `.transform()` not `.fl_image()`, `.resized()` not `.resize()`
- **Scanlines as overlay**: Separate ColorClip in CompositeVideoClip (not apply_vhs chain) to avoid compounded dim effect
- **Frame rate**: 30fps — no benefit to 60fps for retro look
- **Bitrate**: 5000k (enough for 1080×1920 with grain; too low makes grain blocky)
