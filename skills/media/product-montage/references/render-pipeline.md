# Render pipeline: generative HTML-composition stack

The proven stack for montage/`product-demo-film` scenes (one project instance: `dar-demo-video`):

```
capture walker (Playwright) → _screens/*.png + callout candidates
→ callouts JSON (page-prefixed region map, e.g. "pay:fee_row")
→ EDL generator (.py: scene dicts + budgets + energy() + sfx derivation)
→ composition library (phone_scene / section_scene / brand / close helpers; hl/focus/cam/toast ops; fx_script)
→ build wrapper (.sh: swaps the project callouts JSON into place, then runs the generator)
→ scene renderer (per-cid frames → mp4 segs; caches segs/<cid>.mp4)
→ render driver (render_all.py: per-seg frame-count assert, concat, mux BGM+sfx, TOTAL assert, -t trim, output name per version)
→ deliver (copies + checksums)
```

## Composition op semantics (the timing traps)

- **`hl(key, at, dur)`**: `dur` is the VISIBLE WINDOW, not a draw time — the box auto-fades at `min(at+dur, scene_end-0.35)`. Set `dur` to reach the scene's fade cap (e.g. 3.0) so the box is still visible at any sample point; short durations make boxes "disappear" before the frame you are checking and look like a generator bug.
- **`focus` / `cam` dur args are camera TRAVEL times.** The move must land early in the scene (under ~55% of its duration) or the cut kills the punch mid-move. A "camera never settles" complaint is a travel-duration bug, not footage. The inverse is a dead tail: a move that lands with >0.75s of scene left reads as a frozen hold — on punch shots run the travel to the cut.
- **Transient overlays (toast, tooltip) auto-fade at `scene_end-0.35`.** Schedule them early enough to finish appearing before that point or they fade mid-appear and read as noise.
- **Derived effects are positional** (e.g. alternating per-phone-scene motion drift): inserting/removing scenes shifts derived values for everything after. Prefer stable scene ids across versions.

## Generator surgery (patching the EDL/composition code)

- **Re-read the target file from disk before every patch batch.** A fuzzy-match miss on an anchor you "know" is present means the content diverged from your memory of it — verify the anchor with a file search first, then re-patch against what is actually on disk. Never rewrite generator files blind from summarized context.
- **Table-row surgery moves WHOLE rows.** Timeline tables split label/caption tuple, image spec, and fx spec across one line each. Reordering or relabeling rows must carry the entire line; swapping only the label head silently decouples captions from their screens, and the QA sheet then reports "wrong caption on screen X" as a phantom defect.
- **After a forced per-id re-render, verify the seg actually changed** (extract a frame and diff before/after). A wrong or misspelled cid no-ops silently, and the "still broken" QA sheet is then a cache artifact.
- **Project generators are mixins**: a project generator execs the shared composition library above its build marker, so helper names, op semantics, and callout-key conventions (screen-prefixed, e.g. `dpat:row1`) come from the LIBRARY, not the project file. A NameError after an edit usually means the helper was renamed upstream.

## Callout JSON swap

The generator reads ONE region map (default `callouts3.json`) and asserts keys like `page:region`. The build wrapper swaps the project's map (`analysis/callouts_rj.json`-style) into place before generation. Running the generator directly trips the key assert and looks broken when the wrapper path is fine — always build via the wrapper.

## Segment-cache recipe (20x speedup)

The build intentionally `rmtree`s the render dir, which wipes cached segs. To re-render only changed scenes:

1. `cp -r <render_dir>/segs /tmp/segs_bak`
2. run the build wrapper (regenerates compositions + audio; identical specs regenerate identical compositions)
3. `cp -r /tmp/segs_bak/. <render_dir>/segs/`
4. `python3 render_all.py <changed_cid…>` — per-id args force just those segs, then re-concat and re-mux everything

Cached segs stay valid iff each scene's spec + duration is unchanged (retiming starts alone does NOT invalidate them). The driver's per-seg frame-count assert catches stale segs if a duration did change.

## Region measurement

- Detect card/tile bands by scanning pixel extents on the capture (PIL); then expand the rect to fully enclose label AND value with padding.
- Never accept an auto-detected region unchecked — detectors return slivers (e.g. a 16%-wide fragment of a 90%-wide card).
- Sanity rule: callout boxes + captions must not intersect phone tab bars / nav chrome.

## Audio derivation

One change point: budgets define the cut list; whooshes derive at `cut-0.45` (swell into the cut), the impact boom sits ON the biggest transition, close bells on the last. Regenerate stems after any retime and verify by scanning the isolated sfx stem for peaks at the expected cut times (mixed-audio scans drown sfx under BGM).
