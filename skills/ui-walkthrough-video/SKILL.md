---
name: ui-walkthrough-video
description: Generate Figma walkthrough videos with spotlight zoom.
---

# UI Walkthrough Video

Class-level umbrella for turning **actual Figma frames** (PDF or 390×844 HTML) into premium enterprise presentation videos with synchronized narration. Established 2026-08-24 from DAR Dental Clinic Patient Home sample.

## When to use
- Canva presentation needs `FULL → DARKEN → HIGHLIGHT → ZOOM → RETURN` per feature
- Figma PDF exported (e.g. `SF Dental (Copy).pdf` 175p, 78MB) is primary source — do NOT redesign UI
- Need 1920×1080, 16:9, H.264, 10-15s style prototype that previews before building full deck
- Voiceover must sync to spotlighted areas

## Ladder (ponytail)
1. Is video needed? Style prototype only — single screen first, not full deck (YAGNI)
2. PDF already has frame? Extract via `pymupdf` — don't screenshot HTML
3. Stdlib PIL for compositing, MoviePy for encoding — no new deps beyond `pymupdf + moviepy + edge_tts`
4. Native `edge_tts` rate tuning over external TTS APIs

## Workflow

### 1. Locate & identify frame
```bash
ls -1 "C:/Users/Attila/Downloads" | grep -i pdf
python -c "import pymupdf; doc=pymupdf.open('SF Dental (Copy).pdf'); print(len(doc)); [print(i, doc[i].rect, doc[i].get_text()[:120]) for i in range(20)]"
# Patient Home = page 18: rect 390×844, text 'Good morning, Maria | Welcome back | Appointment Approved'
```

### 2. Extract at 3× for zoom headroom
```python
import pymupdf
pix = pymupdf.open(pdf)[18].get_pixmap(matrix=pymupdf.Matrix(3,3))
pix.save("patient_home_from_pdf.png")  # 1170×2532 = 3× logical
```

### 3. Narrate with duration control
- Voice: `en-US-AriaNeural` calm professional
- Rate `+12%` → 16.25s → 14.23s (fits 15.2s video with 0.4s lead + 0.8s tail)
- Generate: `edge_tts --rate +12%` → `narration_final.mp3`
- Measure: `ffprobe -show_entries format=duration`
- Rule: total video 10-15s; tune rate ±5-12% until narration ≤14.5s

### 4. Build cinematic composite (PIL + MoviePy)
- Canvas 1920×1080, subtle gradient bg, phone base height 860 (scale 860/2532)
- Keyframes (t, scaleMult, cx, cy, darken, hl):
  `0 FULL 1.0, 3.2 UPCOMING 1.55@(195,328), 7.0 QUICK_RECENT 1.42@(195,600), 10.6 NOTIF 1.65@(195,190), 14.2 RETURN`
- Easing: cubic `ease_in_out`
- Highlight rects in **logical** 390×844 (vision-verified):
  - `notif (10,142,370,96)` green bar
  - `upcoming (10,265,370,125)` card
  - `quick_recent (10,400,370,400)` grid+recent
- Darken: `rgba(15,23,42,140*alpha)` rounded hole + GaussianBlur(1) + teal ring `rgba(6,182,214,180)` + outer glow + inner white hairline
- Shadow: GaussianBlur 16, offset 8, rounded 18×scale
- Phone centering: `x0=960 - cx*3*factor`, `y0=540 - cy*3*factor` where `factor=disp_w/1170`
- Progress bar `W*prog` at bottom, pill `D.A.R. Dental Clinic • Patient Home`

### 5. Audio mix
- BGM: `sine 110Hz` volume 0.04 lowpass 800Hz duration **> video** (16s for 15.2s video) to avoid `OSError t>duration`
- Mix: BGM vol 0.09 (~-21dB), narration vol 1.0 at start 0.4s via `CompositeAudioClip`
- Verify narration dominates

### 6. Encode & verify
```bash
python build_patient_home_sample.py  # writes DAR-Dental-Clinic-Patient-Home-Sample.mp4 30fps libx264 yuv420p +faststart
ffprobe -select_streams v:0 -show_entries stream=width,height,codec_name,duration -of default=nw=1
ffmpeg -ss 4 -i mp4 -vframes 1 check.jpg  # upcoming
# vision_analyze each checkpoint: full, upcoming, quick, notif, return
```
Checklist: correct Figma frame, readable, darken correct, zooms smooth, highlights subtle, narration↔focus aligned, premium look.

## Pitfalls
- `bgm_subtle.m4a` 15.0s + video 15.2s → OSError at 15.02s — always generate BGM **longer** than total (16s)
- `rate='-2%'` too slow (16.25s >15s limit) — use `+12%`
- Highlight misalignment: use logical coords ×3×factor, add 6*scale pad, blur hole edge
- Inventing UI: extract PDF, don't rebuild from HTML template

## Files
- `videos/patient_home_from_pdf.png` — 3× source
- `videos/narration_final.mp3` — AriaNeural +12%
- `videos/bgm_subtle.m4a` — 16s sine
- `videos/build_patient_home_sample.py` — full builder (reference for reuse)

References:
- `references/dar-walkthrough-2026-08-24.md` — session transcript, timings, verification images

See also: `figma-board-ops` (HTML board import safety) — this skill covers video spotlight pipeline.
