---
name: product-montage
description: Use when building a short product montage or sizzle reel.
---

# Product Montage (app sizzle reel)

Class: a short, content-driven product showcase cut from REAL recorded interaction footage of the live app (capture-composition renders are the fallback material) — varied compositions, the product's own UI motion as the animation, captions only where the screen alone underspecifies the value, BGM + sfx. Runtime is whatever the product story needs (25-60s typical). The montage must answer, from the footage itself with no narration: WHAT the system is, WHO uses it, WHAT each role can do, WHY it is useful.

NOT this class (route elsewhere): narrated demo film with VO and chapters → `product-demo-film`; 9:16 TikTok short → `media/short-video-production`; animated explainer → `media/faceless-explainer` / `hyperframes`; slideshow of static screenshots (the montage must contain real interactions).

## Creative contract (standing user specs — every instance)

1. **Runtime is content-driven.** Never pad or trim to hit a number. The 30-60s band is a guideline, not a target. If a shot communicates in 1.5s, cut it at 1.5s; if an interaction needs 4s to read, give it 4s.
2. **Build a product journey, not a screenshot reel.** Start from the strongest current product value and arrange meaningful beats as entry → interaction → result → another capability → outcome. The viewer should feel movement through the product, not a webpage being animated.
3. **Reject the inherited visual formula.** Do not default to one centered webpage, repeated zoom/pan moves, decorative transitions, uniform pacing, or a recycled scene structure. Vary composition deliberately: full app, meaningful close-up, distinct route/state, interaction result, split/comparison when useful, detail shot, and responsive view when it proves value. A transition is allowed only when it clarifies a product relationship or change of state.
4. **Not a tutorial.** No walkthrough, no feature-by-feature narration, no "next, click…". Show real user intent and the visible consequence, then move on.
5. **Hook with product meaning, not branding alone.** The first second must identify the product category through unmistakable current-app content. Do not open on a title card or generic dashboard unless that state itself is the strongest proof.
6. **Strongest moments only.** Keep the few interactions that prove the app is good. Never show the same screen or state twice unless the second appearance is a materially changed result that the story requires.
7. **Role acts are optional, not mandatory.** Label PATIENT / DOCTOR / OWNER only when role contrast improves comprehension. Do not force every role into a fixed act structure.
8. **Every camera settles before its cut.** A punch-in still travelling at the cut wastes the shot.
9. **Captions are true to the frame.** Caption text = what the screen actually shows at that moment. A "booked" toast is not a "confirmed" screen; mislabeled claims are the first thing a review panel catches.
10. **Sound shape.** Whooshes swell INTO section cuts (peak 0.1-0.5s before each cut), one impact hit on the biggest transition, close on the brand. BGM energy is stepped per act (hook → acts → finale → close).
11. **Hierarchy on any trade-off:** quality > runtime; clarity > showing everything; strong interactions > static shots; montage > tutorial; product showcase > school presentation.
12. **Delivery:** final mp4 copied to BOTH the project root and `~/Downloads` (plus a `_preserved/` copy when the project keeps one), version in the filename, README pointer saying what it is and how to open it. Verify identical checksums across copies.
13. **Footage first.** Real interaction recording (Procedure 1) is the primary material; real UI motion and visible state changes ARE the animation. Camera moves, punch-ins, and callout boxes belong to the fallback composition path only.
14. **A weak scene is CUT, never patched over with a transition.** Decorating weak content hides the problem and reads as the retired formula.

## Procedure

### 0. Establish the current application source of truth before any edit

Resolve the exact project and runtime before opening old footage or montage files. For the Dental Clinic workflow, inspect the current repository at `/home/attila/Documents/Projects/dental-clinic` and the local app at `http://localhost:5173`; never substitute DentalVibe or port 5174. Confirm the served page title, visible product identity, route/nav labels, and current commit. If the port serves another product, stop and fix the launch target instead of adapting the montage to the wrong app.

Ask: "If I had never seen the previous videos, how would I make a compelling product montage from this current application?" Treat previous videos and screenshots only as repetition/quality evidence, never as the composition template. Inventory the current UI, navigation, pages, interactions, responsive states, animations, and meaningful result states. For each candidate ask "if I had 10 seconds, what would I show?" Keep only interactions with a visible product outcome. Save a current nav-surface fingerprint and screenshot set so later edits detect app drift; ignore dynamic date/text changes as noise. **Staleness gate:** before reusing ANY capture asset, compare its timestamp against the repo commit timeline — footage older than the newest feature commits is stale no matter how good it looks, and the finished film must show the CURRENT UI everywhere.

### 1. Verify and use the newest capture workflow

The default capture workflow is the **Playwright `recordVideo` + injected-cursor + rehearsal flow in the `ui-demo` skill** (Discover → Rehearse → Record). Probe the tool registry for anything newer first, read its usage, and use the verified path; never silently fall back to an older screenshot-walk script. Record the verified app at `http://localhost:5173`, with the viewport, navigation, input, scrolling, and responsive controls explicitly set.

- Walk the app with a discovery script (dump visible interactive elements per page) BEFORE scripting captures. Persona/user-switcher menus often trigger first-run onboarding modals after a role change — dismiss them, or the walk silently sticks on the welcome screen and records the wrong state.
- Use one capture-walker per project, logging the exact source URL, commit, viewport, role/state, and capture-tool version into the capture manifest.
- Capture INTERACTIONS, not empty screens: type real input through the app's own fields, click through flows, capture the visible result state, and include responsive/mobile states only when they reveal product value. A mostly-empty chat/list frame wastes its shot; recapture with meaningful content or omit it.
- **Recording geometry:** Playwright's `recordVideo.size` sets the canvas, NOT the content scale — when it differs from the viewport the page lands 1:1 top-left inside the recorded canvas with padding. Immediately after recording, extract a frame, measure where the app content actually ends, and record that rect in the manifest; measure every crop against real video frames, never against rehearsal screenshots at another scroll state or assumed geometry.
- If the standard workflow is unavailable, record the blocker and use the strongest verified browser capture alternative only after confirming it can capture the same real interactions. Do not claim the standard workflow was used when it was not.

### 2. EDL (single source of truth)

- One EDL file as the single source of truth. Footage path (default): shot dicts (id, clip, in/out, crop or full, composition mode, audio role) driving ffmpeg trims + concat — no camera moves needed, real UI motion is the animation. Composition path (fallback): scene dicts (id, image, duration, camera, effects).
- Make the EDL importable code so every QA frame timestamp is COMPUTED from it (shot midpoints) — hand-calculated timestamps drift onto neighboring shots and manufacture false defects.
- Beat grid: hook → acts → close. A rapid-state flash block (one ~0.8-1s punch per breadth word or role state, each a DIFFERENT crop of existing material) is cheap breadth at hook or finale — optional garnish, never a required ending.
- Derive section budgets and the audio energy curve from the same cut times — derive, never hand-copy. The sfx cut list derives from these too.
- When retiming: renumber ALL starts in one pass so every start equals the running sum (the render driver asserts it), and update budgets, energy boundaries, total-duration assert, and output filename together. Scene content depends only on a scene's own spec + duration — retiming starts without changing durations keeps cached renders valid.

### 3. Crop boxes and callout regions

- Footage path: the crop box replaces the callout. Measure it on real extracted video frames (grid overlay + vision), content fully inside with margin, even pixel values. Any crop scaled to 1920x1080 must be 16:9; non-16:9 content (before/after splits, role comparisons) goes into a PIL composite panel at a deliberate panel height with even letterbox bands — never accept whatever padding falls out. Close-ups must keep enough chrome (sidebar/header) for the viewer to know where in the app they are.
- Brand end card: crop the product's own logo asset tightly (mask to shape); a header-region screenshot snippet reads as a messy crop.
- Measure rects from the captured image (card bands, tile boxes) with pixel extents. Never trust auto-detected regions: a detector can return a 15%-wide sliver of the real card.
- A callout box must fully enclose its label AND value with padding, and stay clear of phone tab bars / nav chrome (captions likewise).
- Verify every region on a full-res crop before rendering.

### 4. Build + cheap QA loop

- Build through the project's build wrapper, NOT the generator directly: the wrapper swaps the project's callout JSON into place before generation, and direct exec trips a misleading callout-key assert.
- Render only changed scenes by id, extract one frame per scene, vision-check FULL-RES crops. Contact sheets are inventory only: vision misreads thin callout boxes at sheet scale and hallucinates placeholder text and callouts that are not in the frame. Sheet sampling also manufactures timing phantoms: a frame caught mid caption-slide-in reads as "missing caption", whole-frame drift reads as "bouncing UI", and a zoomed macro crop reads as "separate screens" — check the generator's timing code before treating any of these as defects. Never edit footage or regions from a sheet judgment — crop-verify first.
- Fix defects at the owning layer (op semantics: highlight windows, camera travel, toast fades — see `references/render-pipeline.md`). Symptom-chasing (moving boxes/crops) hides the real cause.

### 5. Re-render cheaply after edits

- Footage path: the EDL renderer takes per-shot ids (`--shot NAME`) — re-render only the changed shots and re-extract QA frames at computed midpoints.
- Composition path: the build wipes the render cache by design (rmtree). Stash the rendered-segment dir, rebuild, restore it, then re-render ONLY the changed scene ids with the render driver's per-id args — a full re-render costs 20x more and buys nothing. ~45 min → ~2 min.

### 6. Final verify + deliver

- ffprobe: duration equals the asserted total EXACTLY; 1920x1080@30; h264+aac.
- Audio sync: scan the isolated sfx stem for peaks — every section cut gets its whoosh swell, the finale impact lands on its cut, close bells on the last transition. Mixed-audio scans drown sfx under BGM; always scan the stem.
- Panel-eye pass: assemble a labeled per-scene frame sheet + a few full-res crops and critique as the target viewer (first impression: what is it / who uses it / what can each role do / why useful). Disposition EVERY claim against a full-res crop before editing — vision over-flags; when the crop disproves a claim, keep the footage unchanged.
- Run the self-critique gate before delivery: compare the cut against every previous video of the same product and name the repetition/bias (same formula, same duration band, same pacing, recycled structure); rewrite or CUT what repeats, then re-watch the whole result once more. Ship the critique table with the film: repetition vs previous cuts? one-centered-page default? duration by accident? transitions meaningful? every scene product value? rhythm varied?
- Deliver per contract #12 and verify checksums.

### 7. Editor pass on an existing cut (diagnose → fix → re-watch → converge)

When asked to review and refine an existing montage rather than build fresh:

- **Diagnose before touching anything.** Watch the whole cut as a first-time viewer (no knowledge of the editor's intent) and log timestamped immediate reactions (awkward, too fast/slow, confusing, noisy, repetitive, boring, "AI-generated") BEFORE opening the generator. Fix defects at the owning layer per Step 4; never mask a rhythm or content problem with another effect.
- **Mechanical-tell checklist** (why a cut reads as machine-edited): metronome pacing — several identical beat durations in a row; weight durations to story importance (a key result state deserves more than a filler screen). Universal drift — sideways creep on EVERY shot, or an amplitude that travels noticeably within a short shot (that is a pan, not a drift); scale creep to shot length and let still/short shots hold. Dead tails — on fast punch/recap shots, a camera tween that lands and leaves >0.75s of frozen frame kills the punch; run the travel to the cut (story shots still settle per contract #8). Screen re-use — a recap/flash block must not show screens the closing lineup shows (the "did the video loop?" tell); repeated screens need a materially changed state per contract #6. Punchline placement — the close card is the montage's thesis; it must land EARLY and hold ~2s, never arrive in the final beat. Sticker pattern — the same decorative effect on every beat.
- **Re-render, then re-watch the WHOLE result** and repeat until the remaining notes are sheet artifacts, app-side data quirks, or style calls at diminishing returns — then stop and say so. The delivery report ships the disposition table: what was fixed, and what was deliberately KEPT (claims disproved at full-res or by the generator code stay unchanged, named as keeps).

## references/

- `references/footage-edit-pipeline.md` — the default real-footage path: Playwright recording geometry, ffmpeg accurate-seek trims, EDL-driven concat, crop/panel recipes, midpoint QA sampling.
- `references/render-pipeline.md` — the generative HTML-composition render stack (op semantics for highlight/camera/toast timing, callout-JSON swap, segment-cache recipe, region measurement, sfx derivation). Shared substrate with `product-demo-film`.
