---
name: design-demo-video
description: Turn design screens into a narrated demo video.
---

# Design → Demo Video

Portrait 1080×1920 app demo video from static design screens (Figma PDF export, screenshots, HTML mockups). Stack: pdftoppm/PIL (screen extraction) → TTS (voiceover) → HyperFrames (composition, check, render). Known-good end-to-end generator: `templates/build.py`.

## Procedure

1. **Identify screens before rendering anything.** `pdftotext file.pdf -` and split on `\f` — the per-page text map tells you which pages hold which screens (Figma PDF exports are one frame per page). Render only the chosen pages: `pdftoppm -f N -l N -r 300 -png`. Then crop each page to its content bbox (PIL: diff against pure white, pad ~12px) — exports sit on white pages with margins that poison framing.

2. **Probe the TTS provider before scripting the VO around it.** If the user names a provider (e.g. Fish Audio with a reference voice), test it FIRST with a one-line request — Fish Audio HTTP 402 means valid key but zero API credit (billed separately from platform credit; no balance endpoint on api.fish.audio). Fallback chain: `edge-tts` (installed) with a Filipino-English voice for PH projects. Test the chosen voice ID with a 3-word line before batch synthesis — some neural voice IDs die upstream with `NoAudioReceived`; try a sibling voice (`en-PH-RosaNeural` is a known-working fallback). Make the voice an env override in the generator (`VO_VOICE=`).

3. **Generate VO first, measure, then lay scenes.** Synthesize all segments, ffprobe each mp3, scene length = lead-in + VO duration + pads. Never hand-time scenes to guessed VO lengths — narration and scene cuts drift apart.

4. **Build the composition from the generator, never by hand.** `python3 build.py` writes `index.html` from a SCENES table (screen png, label, kicker, VO line) plus measured durations. The generator is the source of truth — hand edits get overwritten on the next run.

5. **Gate loop, in order:** `npx hyperframes lint` → `npx hyperframes check` (must reach `Check passed`, 0 errors) → `npx hyperframes snapshot --at <scene midpoints>` → vision-check the contact sheet (phone framing, caption legibility, icon glyphs) → only then `npx hyperframes render --quality high --output out/<name>.mp4`.

6. **Verify the MP4 itself, not the render log.** ffprobe: h264+aac streams, 1080×1920, duration ≈ timeline total. Extract 2 frames from the file (`ffmpeg -ss T -i out.mp4 -frames:v 1 f.jpg` — one intro-card timestamp, one phone-scene timestamp) and vision-check them. Also confirm a non-silent audio track (extract 20s of audio, check duration > 0).

## Pitfalls

- `npx hyperframes` can fail with a silent exit 1 and zero output on this machine — install locally (`npm i hyperframes`) and use the project-local binary.
- Every timed element needs a unique `id`; an `<audio>` without one renders **silent** in the final video (the renderer discovers media by id) — lint catches it only as `media_missing_id`.
- pdftoppm names output `p031-031.png`. Reference exact filenames or rename to `p031.png`; a naive glob rename (`${f/-*-/_.png}`) produces `p031-031.png.png`.
- Emoji in hero/title cards: verify the codepoint renders as the intended glyph via snapshot vision check — one digit off turns a tooth 🦷 into a screwdriver, and static audit can't see it.
- `container_overflow` lint infos on screen-image pan tweens are expected (Ken Burns inside the `overflow:hidden` phone screen) — not defects, don't chase them.
- Source-design quirks (placeholder service names, odd labels) are kept as-is: the video is a faithful demo of the design, and silently "fixing" the design misrepresents it.
- The HyperFrames skills live in the read-only external skill source — workflow lessons from video sessions belong HERE, not in `hyperframes-*` skills.
