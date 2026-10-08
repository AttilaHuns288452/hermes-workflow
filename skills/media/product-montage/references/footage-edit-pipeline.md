# Real-footage edit pipeline (default capture → cut path)

Default material: real recorded interaction footage (ui-demo workflow: Playwright `recordVideo` + injected cursor + rehearsal), cut EDL-style with ffmpeg. The generative composition stack (`render-pipeline.md`) is the fallback when interaction capture is impossible.

## 1. Capture geometry (verify before any crop work)
- Playwright `recordVideo.size` sets the canvas, not the content scale. When canvas ≠ viewport, the page renders 1:1 top-left and the remainder is padding.
- Immediately after recording: extract one frame, measure the content extents (where the app actually ends), and write the content rect into the capture manifest. All crops are measured against real video frames from then on.

## 2. Trimming recorded clips
- Accurate seek only: `ffmpeg -ss <t> -i in.webm ...` is FAST seek and snaps VP8 to keyframes — it silently returns footage from the wrong time. Put `-ss` AFTER `-i` for frame-accurate trims.
- Trim to the interaction beat: state visible before the click → consequence visible, with ~0.2-0.4s lead-in so the shot doesn't open on the click itself.

## 3. EDL-driven render
- One Python EDL table: shot id, clip, in/out, crop or "full", composition mode, audio role. The renderer walks it and supports per-shot re-render (`--shot ID`).
- Importable EDL = computed QA timestamps: sample at each shot's MIDPOINT. Hand math drifts onto neighboring shots and manufactures false defects.
- Output contract: 1920x1080@30, h264+aac; `ffprobe` duration must match the EDL sum exactly.

## 4. Cropping and panels
- Crop boxes: measured on grid-overlay frames (vision reads pixel bboxes at 100-200px grid), content fully inside with margin, even pixel values; verify each by extracting the shot's midpoint frame from the render.
- Anything scaled to 1920x1080 must be 16:9. "full" mode = crop the content rect → scale to 1920x1080.
- Non-16:9 content (before/after splits, role comparisons): PIL composite panel at a deliberate panel height, even letterbox bands, cards with margin. Never accept accidental padding.
- Close-up crops keep enough chrome (sidebar/header) for the viewer to know where in the app they are.
- Brand end card: tight crop of the product's own logo asset (mask to shape), hold 2-2.5s.

## 5. Composition grammar (anti-formula)
- The product's own UI motion is the animation: no camera moves, no fake pans, no decorative transitions.
- Transitions = real navigation / selection / state change. Sound accents (whooshes, one impact) only at act boundaries; BGM energy stepped per act.
- Variety comes from shot PURPOSE — full app / interaction close-up / before-after panel / rapid states / result hold — not from effects. A weak shot is cut, not decorated.

## 6. QA + delivery
- Extract QA frames at computed midpoints; full-res single-frame reads are reliable, contact sheets are inventory only (vision hallucinates content at thumbnail scale).
- Disposition every defect claim against the full-res crop before editing — vision over-flags on video.
- Final gate: clean per-scene sheet (no broken/blank frames, intended flow, holds tight except deliberate cards) + the SKILL.md self-critique table.
- Deliver to project root + `~/Downloads` (+ `_preserved/` when kept), identical checksums, README pointer.
