# DAR Walkthrough 2026-08-24 — Patient Home Sample

## Session
- Prompt: 15s Patient Home walkthrough from Figma PDF, spotlight sequence FULL→DARKEN→HIGHLIGHT→ZOOM→RETURN
- Source PDF: `C:/Users/Attila/Downloads/SF Dental (Copy).pdf` 78MB 175 pages, rect 390×844 for phone frames
- Identified Patient Home: page 18 `Good morning, Maria | Welcome back | Appointment Approved | Upcoming appointment | Oral Prophylaxis | AUG 20`
- HTML mirror: `design/frames/03_Patient_Home.html` (29K) validated layout

## Extraction
- `pymupdf.Matrix(3,3)` → 1170×2532 PNG `videos/patient_home_from_pdf.png` 202K sharp, vector text retained
- 2× also saved for preview
- Vision confirmed: notif y142-238, upcoming y275-390, quick grid y430-660, recent y705-800

## Narration
- Text exact: "From the patient side, after you have signed in, the Home screen appears and provides a quick overview of upcoming appointments, recent activity, and quick actions. It also has a notification bar to keep the patient informed about important updates."
- `en-US-AriaNeural` rate `-2%` → 16.25s too long, `+12%` → 14.23s, `+8%` 14.73s, `+5%` 15.16s. Chose `+12%` for 15.2s video (0.4s lead, 0.8s tail)
- Generated via `edge_tts edge_tts.Communicate(text, voice, rate='+12%')`
- BGM: `ffmpeg -f lavfi -i sine=frequency=110:duration=16 -filter:a volume=0.04,lowpass=f=800` → 16s (must exceed video 15.2s or MoviePy OSError at 15.02)

## Video builder
- `videos/build_patient_home_sample.py` 348 lines, PIL per-frame compositing, MoviePy VideoClip(make_frame, duration=15.2) @30fps
- Keyframes with cubic ease: 0-1.6 FULL, 1.6-3.2→UPCOMING 1.55, 5.6-7.0→QUICK_RECENT 1.42, 9-10.6→NOTIF 1.65, 14.2→RETURN
- Darken: rgba 15,23,42 alpha 77 (140*0.55), hole rounded 12*scale + blur 1, teal ring 6,182,214
- Phone math: factor=disp_w/1170, x0=960 - cx*3*factor
- Previews rendered at 0.5,3.5,7.2,10.8,14.5s for verification
- Encode: libx264 8000k, aac 128k, yuv420p, +faststart, threads 4 — 80s render for 456 frames

## Verification
- Extracted frames at 1s (full), 4s (upcoming), 7.5s (quick), 11s (notif), 14.5s (return)
- vision_analyze on 4s upcoming: "darkened background + teal glow readable premium" passed
- ffprobe: 1920×1080 h264 30/1 15.2s, aac 44100 2ch, 5.37 Mbps, 10.2 MB
- Checklist: frame correct, readable, darken OK, zooms smooth, highlights subtle, narration sync, premium

## Pitfalls captured
- BGM shorter than video → OSError; always BGM duration > video
- Rate too slow → exceeds 15s limit

## Reuse
For next screens (04 Book, 06 Appointments): swap RECTS logical coords, keep keyframe structure, change PDF page index (19,20,21,22)
