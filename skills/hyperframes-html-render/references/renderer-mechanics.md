# Renderer mechanics & pitfalls (verified empirically 2026-10-02, CLI 0.8.107)

## GSAP timeline registry
- Register as `window.__timelines[compositionId] = tl` (keyed map, NOT the array+push form).
- NEVER reassign `window.__timelines` itself. The runtime pre-creates the object and keeps a reference to it; `window.__timelines = [...]` orphans that reference and silently disables ALL timeline seeking (every `from()` tween stays baked at its invisible start state → blank frames). Always `window.__timelines = window.__timelines || {};` then assign keys.

## Why your scenes render blank or pre-animated
- GSAP seeking is effectively monotonic across scenes in one file: a single timeline's tween positions get consumed by OTHER scenes' clocks before a scene becomes visible, so `from()` entrances land "already played" (scenes appear fully formed, no motion). Per-scene timelines keyed by clip id are NOT selected by the runtime (only `__timelines[compId]` is).
- CSS animations are seeked at CLIP-LOCAL time: `animation-delay` is relative to clip activation, never global. Putting scene-start values (e.g. `animation-delay:13.64s` on scene 2) doubles the delay — the scene fades in 13.64s AFTER its own activation, i.e. after its window ends → permanently blank frames. Small per-element delays (0.1–7s) give correct per-scene entrance motion.
- Rule of thumb: per-scene entrance/exit motion = CSS keyframes with small delays (renderer-native, deterministic clip-local); GSAP = only for within-scene state tweens whose timing you have verified with snapshots.

## Scene cuts vs overlaps
- With opaque scene backgrounds and increasing `data-track-index`, an overlap window is visually a hard cut (incoming clip covers outgoing). The layout pass still flags `content_overlap` text errors during overlaps — collapse durations to exact cuts (each scene ends where the next starts) to silence it with zero visual change.

## CLI gotchas
- `npx hyperframes ...` can fail silently (exit 1, no output). Use the global binary installed by `scripts/setup.sh` (`hyperframes <cmd>`).
- `hyperframes tts` needs `HYPERFRAMES_PYTHON` pointing at a venv with `kokoro-onnx soundfile` (PEP 668 blocks system pip). First run downloads the Kokoro model.
- `hyperframes validate` is deprecated → `hyperframes check` (works on the project dir).
- `hyperframes snapshot --at 1.5,4.0 --no-end` captures exact timestamps; `--frames N` is evenly spaced.

## Audio clips: `<audio src=...>` elements, NOT spans
- Root compositions mux narration/music via real `<audio id data-start data-duration data-track-index src="audio/….wav"></audio>` elements inside the composition div. `<span data-src data-audio>` is faceless-explainer's FRAME-FILE convention — spans in a root composition are silently ignored (`hasAudio:false`, "audio 0.0s" in the render trace, video renders fine but mute).
- Verify narration actually muxed: the render trace line must say `hasAudio:true`; confirm with `ffprobe -show_streams -select_streams a`. Treat a mute video as a failed render even if "Render complete" prints.
- Audio spans/clips on the same track must not overlap; keep `data-duration` ≤ the gap to the next clip.

## Cheap QC before rendering
- Snapshot key + transition-moment frames, then diff `px>60` counts on grayscale histograms: identical counts within a scene = no animation happening; ~2k = background-only (blank). Only then spend vision calls on the frames that matter. Contact sheets at small cell sizes can hallucinate text defects — verify suspected text issues with a high-res `--zoom` crop or full-frame PNG before "fixing" non-existent bugs.
