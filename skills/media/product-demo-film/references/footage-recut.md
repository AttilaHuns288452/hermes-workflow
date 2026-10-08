# Real-footage recut: Playwright screen recordings → short montage

Use when the montage must show the app in MOTION (animations, transitions, real cursors) that frame compositions cannot author. Same downstream contract as the sizzle re-edit (captions + role pills, no narration), different material.

## Pipeline

1. **Record.** Playwright `record_video` against the local dev server at the pinned HEAD. Drive flows with real clicks (booking → confirm, form → save, chart hover). One flow per continuous take; keep takes ≥ the shots you expect to cut from them.
2. **Cut list (EDL) as data.** One script holds rows `(name, src, start, end, crop, caption, role)`; every later stage (shots, sections, xfade offsets, audio) derives from it — never a second hardcoded copy (same rule as timeline-derived audio). Windows: content shots 1.6–2.6s, heroes 2–3s, deliberate rapid blocks 1.0–1.5s.
3. **Verify before cutting.** Extract the first frame of every candidate window: confirm ROLE from the frame itself (portal subtitle/sidebar) and that the interaction's result is inside the window. Filenames and recording-session notes are hypotheses.
4. **Per-shot encode.** Accurate seek (`-i src -ss t -t d`, seek AFTER `-i`), `crop` to the content region + `scale` to the render size (crop box must match output aspect or the scale squishes the UI), uniform `yuv420p`/30fps, CRF 18–20. `--shot NAME` single-shot mode for diagnosis loops.
5. **Sections + transitions.** Concat per role/act with the concat demuxer (`-f concat`, no fades inside an act), then one xfade chain across sections: `offset = section_start − fade_dur × (number of earlier fades)`. Crossfades at act boundaries only; hard cuts inside acts.
6. **Audio from the EDL.** Whoosh/impact times = act boundaries computed from the cut list (budgets), then bed + mix. Any retime → recompute from the EDL and verify peaks against the new cut points.
7. **QC.** Full-res frame per shot at its midpoint (see sampling rule below) → identity/label/proportion check; boundary luminance scan for black flashes (distinguish deliberate fade-ins on cards — a fade-up from black on an identity card is a design choice, not a defect); `ffprobe` duration/streams + `volumedetect`; md5 + spot frames on the delivered copy.

## Pitfalls

- **Sample grids drift in overlapping chains.** In a render with xfades, a shot's content appears `fade_dur × (earlier fades crossed)` later than the flat sum of durations suggests; sample at corrected midpoints (or per-shot files) — a drifted grid reads correct shots as wrong-screen defects and sends fixes at phantom bugs.
- **Fast seek lies at boundaries.** `-ss` before `-i` snaps to keyframes and returns a neighboring scene — the source of phantom "wrong screen / dark frame" findings. Accurate seek only when verifying.
- **`record_video` canvas ≠ viewport.** The recorded canvas can be larger than the viewport with the content parked top-left and padding elsewhere. Measure crop boxes on frames extracted FROM THE VIDEO, never on screenshots taken at other scroll states.
- **Hook shots must be true variety.** If several recordings all open on the same landing screen, a multi-world hook built from their openings shows the same screen three times — pick windows from inside the flows instead.
- **Contact-sheet verdicts are candidates only.** Multi-tile vision passes misattribute labels to neighboring tiles; confirm anything you will edit from a single full-res frame.
- **Keep scratch output version-suffixed and outside the deliverable path**; verify prior deliverable checksums unchanged after a run.
