# Animated demo previews (gallery cards over interactive engines)

Recipe for cards whose preview is a live mini-run of a real demo engine — the
preview must derive from the same implementation the full workspace mounts, so
what the card animates is the product's actual behavior, not decoration.

## Mount contract

One registry maps card → engine mount + pinned options (algorithm, dataset,
policy…). The preview box mounts the engine with `preview: true`; CSS scoped to
`.preview-box` hides the engine's chrome (`.lab-controls`, selects, buttons,
prose, secondary logs) so the card shows visualization + key stats only. The
workspace keeps everything.

## Lifecycle (IntersectionObserver)

- Mount lazily when the card enters the viewport (rootMargin ~80px); pause on
  exit. No observer → mount all paused (static frames).
- Reduced-motion gates DECORATION, not the demo itself: this motion is the product's actual behavior and animates on demand even under `prefers-reduced-motion` (general policy in `make-interfaces-feel-better`). Mount paused at the first frame only when the brief prioritizes calm over motion — when the user explicitly demands visible animation, autoplay wins.
- Teardown clears every interval and disconnects the observer on gallery close.

## Driver (the trap set)

Engine handles are inconsistent: `run()` may be a play/pause TOGGLE (calling it
twice flips a running demo off) or may complete the whole simulation
synchronously (zero motion). Do not trust it:

1. Start sequence = `pause()` → `reset()` → drive `step()` on a fixed interval
   (~450ms). `step()` advances exactly one visible state in every engine.
2. Engines without `step()` fall back to `run()` (after `pause()`).
3. Pin a deterministic scenario in preview mode. Random short scenarios render
   an already-finished, frozen card (a random 1-day trip ends before the first
   frame). The workspace keeps randomness for exploration.
4. Restart completed runs on a slow loop (~5s: pause → reset → step beat) so
   the card stays alive. Cleared intervals guard against re-mount races.
5. Repeated observer events must call the same start sequence — never bare
   `run()` — or the toggle semantics silently stop a running preview.

6. `run()` may also silently no-op while the engine's data is still loading (fetch-backed traces): a call during the load window is lost and nothing replays it. Drive the OPENED workspace with the same shared step-beat instead of the engine's `run()` — toolbar Run toggles the beat with a live Pause/Run label, Step/Back/Reset stop it first, and the speed control re-times the interval. One driver, both surfaces.

## Test harness
- VM/unit sandboxes often clamp `setTimeout`/`setInterval` to a few ms: a slow beat becomes a machine gun that outruns assertions. Pause the autoplay before any `await` in tests and assert stepping explicitly.
- `unref()` Node-side beat/loop intervals (guarded — browser intervals return numbers) or a leaked interval hangs `node --test` forever.
- Stub DOMs lack `querySelectorAll`, `style.setProperty`, and an `input.value` default: feature-detect around cosmetic UI seams (duplicate-control hiding, per-category hues, search filtering) so they can never throw.

## Honest visualization

If the scenario hides information from the algorithm (unknown trip length,
unseen stream tail), the preview must not leak it: draw unknown tiles as `?`
and grow the board as steps happen. A pre-rendered full board contradicts the
lesson the demo teaches.

## Verification (mandatory)

Pixel-diff two screenshots of the SAME preview box ~1.4s apart
(`PIL.ImageChops.difference`, count changed pixels). Expect >0 for every card
that should be alive; 0 = frozen regardless of what counters say. Then a
per-card behavioral check: scroll card N into view and assert ITS preview
mounted. Report changed-pixel counts as the evidence.
