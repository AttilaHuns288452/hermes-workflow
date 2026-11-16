# FFmpeg assembly fallback (rendered frames -> final MP4)

Use when the sanctioned fallback path applies: a source-led 3D render (e.g. Blender PNG sequence) assembled by script, because the full pipelines are unavailable. Pattern: gapless PNG sequence + mixed audio + ASS subtitles -> H.264/AAC MP4.

## Command shape

```bash
ffmpeg -y -framerate 30 -start_number 1 -i frames/f%04d.png -i audio_mix.wav \
  -map 0:v:0 -map 1:a:0 \
  -vf "subtitles=captions.ass:fontsdir=/usr/share/fonts/truetype/dejavu,fade=t=in:st=0:d=1.2,fade=t=out:st=END:d=1.5" \
  -frames:v N -t DURATION -r 30 -c:v libx264 -preset fast -crf 18 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -ar 48000 -movflags +faststart out.mp4
```

Then verify: ffprobe assertions (width/height/r_frame_rate/nb_frames/codecs/duration) + full decode (`-v error -xerror -i out.mp4 -map 0 -f null -`). A short review proxy can be derived from the final export with `-vf scale=1280:-2`.

## Pitfalls

- **Map filter-graph outputs explicitly.** When `-filter_complex` produces a labeled output (e.g. `amix ... [a]`), `-map` must reference the label (`-map "[a]"`). Omitting it fails with `Filter 'amix:default' has output 0 (a) unconnected` / `Error binding filtergraph inputs/outputs` — the label mapping IS the connection; the same command shape works with plain `-i` audio only because those map by index.
- **Gapless-frame gate before assembling.** Assert the PNG sequence is contiguous (f0001..fN with no gaps) and every Nth frame decodes at the expected size. One missing frame silently shifts every later cut against the audio.
- **Fades only at the ends.** Interior transitions belong to the edit/camera cuts; a fade per clip welds the film together into mush.

## Audio for assembled renders

- **Narration is built per shot, not as one monolith.** Generate one TTS segment per shot, ffprobe each real duration, and place segments with explicit `adelay` at their shot start times. A single narration file "close to" the runtime desyncs from shot changes and overflows the tail shot. Budget VO to fit each shot window (0-6s typical); shorten the line rather than speeding the voice past ~1.1x.
- **Measure the mix; never trust a volume filter.** Target integrated loudness -16 to -18 LUFS, true peak <= -1 dB (ffmpeg `ebur128`/`astats`). A bed measuring ~-50 dB mean is silence no matter how it was generated; scaling silence by `volume=0.2` stays silence. Bring a procedural bed to roughly -25 to -30 LUFS under speech, with ducking, and smooth ~1s fades at head/tail.
- **Proven local TTS on this box:** `tools/venv/bin/python` + `edge-tts` (en-US-AndrewNeural) produces per-segment WAVs; probe provider availability per the voice-selection rule in the parent skill before committing.

## Proven mix chain (shot-synced narration + ducked bed)

- Narration track: per-segment `adelay=<shot_start_ms>:all=1` → `amix=inputs=N:duration=longest:normalize=0` → `apad,atrim=0:<TOTAL>` for an exact-length track.
- Mix: bed through `sidechaincompress=threshold=0.02:ratio=12:attack=25:release=400` keyed by the narration track (NOT self-keyed), then 2-pass `loudnorm=I=-17:TP=-2:LRA=11` — pass 1 with `print_format=json` on `-f null`, feed `measured_*` + `target_offset` into pass 2 with `linear=true` — plus ~1s fades at head/tail.
- Assert per segment: duration ≤ shot window (with ~0.3s margin) and ≤ the VO cap; assert total = film length exactly; assert LUFS/peak after the final encode, not before.
- Parameterize the pipeline by a narration text file (one `SHOT | line` entry per shot): a wording fix = edit one line, regenerate that segment, rebuild the mix. Never hand-edit generated audio.