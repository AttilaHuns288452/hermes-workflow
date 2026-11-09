---
name: motion-verification
description: Use when proving UI animations run visibly in a browser.
---

# Motion verification

A screenshot after an animation finished proves nothing. The mission is evidence that motion happened WHERE THE USER LOOKS, at the time they look. Covers entrance animations, stagger waves, skeleton handoffs, scroll reveals.

## Instrument first, look second

1. `addInitScript` before navigation logging `animationstart` / `animationend` / `transitionrun` with `performance.now()`, `e.animationName`, truncated `target.className`, and `effect.getTiming().delay/duration` into `window.__anims`.
2. `animationstart` fires AFTER the delay phase: `event_t - delay = element mount time`. This distinguishes 'mounted late' from 'delayed' from 'never animated'.
3. Dump the full event array to JSON per route; aggregate by name and by delay sequence in Python, never by eyeballing logs.
4. Record video (`recordVideo`) alongside; extract frames with ffmpeg seek AFTER `-i` (accurate), never fast-seek on VP8.

## Assert wave state, not just events

For viewport-driven systems (items marked `.is-live` / similar), report at end of run: `total`, `played`, `still-pending` counts. The signature of a healthy system on a 240-card grid is `played == number the reader actually scrolled past`, `pending == rest`. A run where all 240 'played' at mount means the animations fired off-screen.

Use step-scrolling (viewport-sized jumps with MARK log entries) so waves can be attributed to the scroll step that caused them; each step should produce one wave with delays 0, d, 2d, ... (the piano-key signature).

## Capture mid-wave frames deliberately

Fixed-offset screenshots (e.g. +800ms) almost always miss a 560ms wave. Trigger the wave (scroll into pending items), then shoot at +110 / +230 / +360ms. Growth in PNG file sizes across the burst is a cheap pre-sign of progressive appearance. Vision-check ONE mid-wave frame for mixed states (some cards 100%, some ~50% opacity with residual translate).

## Interacting with elements under motion

- Coordinate clicks on elements riding entrance waves fail actionability ("element is not stable", then "detached" once the wave re-keys), and a fixed tray/toast can sit over the target mid-test. For deterministic interaction, dispatch the DOM event: `locator.evaluate((el) => el.click())` — framework delegated handlers still receive it. Reserve coordinate clicks for hover-state tests.
- Match controls EXACTLY: `getByLabel("Compare")` is a substring match, so it also matches a nav icon's `aria-label="Compare gadgets"` — clicking it silently navigates away and the probe reports an app bug. Use `getByLabel(name, { exact: true })`; when a click "did something impossible", print the matched `outerHTML` before suspecting app behavior.
- Parse prices/money with the decimal separator kept (`[^\d.]`, never `[^\d]`): "₱2,856.36" becomes 285636 under digit-stripping and every filter-cap assertion false-fails on decimals.

## Common false diagnoses (verify before 'fixing')

- 'Cards never animate' in a local dev that lacks the serverless /api = catalog error state, zero cards rendered. Stand up a static server + /api proxy to production before concluding anything about card animation.
- Empty container at t=250ms = entrance sequence not started yet (delays), not 'content missing'. Check the t=800-1200 frame.
- The reveal/hidden-state gate (e.g. `html.reveal-ready`) may be set by ONE page's hook only — if the gate is page-scoped, other routes silently run the old behavior. Move the driver to the app shell.
- Changing `animation-delay` REPLAYS a CSS animation. If a React re-render can rewrite the delay var, keep the wave index in a separate var the framework never touches.
- `prefers-reduced-motion` blocks that zero durations but not `animation-play-state` strand paused items invisible.
- Re-analyzing a screenshot while another process rewrites it returns stale vision results; shoot, wait, analyze in a later call.
- Very tall full-page screenshots (mobile at 2x) can fail vision ingest as "not a recognized image"; capture viewport-sized scrolled segments instead.

## When the user reports "I can't see the animations"

Walk the elimination ladder in order; each rung is a cheap probe, and the last one is a question, not a guess:

1. Fresh cache-busted URL in a NEW tab (a SPA tab keeps running its old bundle forever; a phone with a cold cache sees the new build first).
2. Ask that exact browser what it reports: a trivial page evaluating `matchMedia('(prefers-reduced-motion: reduce)').matches` is the ground truth for that engine/profile, regardless of OS settings. Get the answer from the user's ACTUAL long-lived browser, not a headless or freshly launched one — the engine caches this state, and a stale desktop broadcast (XSETTINGS sending `gtk-enable-animations=false` while gsettings/settings.ini all read "enabled") sticks to running browsers until they restart. Probe the open browser itself (drive its DevTools console with xdotool + clipboard paste — pasted text survives autocomplete where typed text does not — and read the answer back through `copy(...)` or `document.title`, which `getwindowname` can read), and compare against a fresh headed browser on the same desktop: fresh `false` + user's `true` means restart their browser and the app is fine. OS config files claiming animations are enabled are NOT evidence; the browser's `matchMedia` is the only ground truth.
3. Extensions and per-browser prefs can zero animations globally; check the profile's extension list and reduced-motion pref — and the DevTools "Rendering → Emulate CSS media feature prefers-reduced-motion" toggle, which persists per profile and silently applies to every page until set back to "No emulation".
4. Prove the ENGINE renders the entrance: capture the live page in that engine at controlled times. `firefox --headless --screenshot` fires at load, which can be before the first delay elapses (looks "empty"), so wrap the page in an iframe plus a slow subresource (`/delay/5`) to force a late capture, and compare early-vs-late frames: late-rendered content means the engine is fine, late-EMPTY means content is stranded.
5. Entrances that finish in ~1s are invisible to anyone who looks after load (slow devices make users watch the same entrance). The distinguisher is scroll behavior: ask whether new rows fade in as they enter the screen.

The file-size delta of sequential captures is a cheap content-presence signal before spending a vision call.

## Done criteria

- Event log proves each entrance started (and with what delay sequence).
- Wave-state counts prove off-screen items did NOT play early.
- One mid-wave frame visually shows mixed animation states.
- Hover/interaction still works after entrance (fill `backwards`, not `both` — `both` pins transform and kills hover-lift).
- Re-run every check against the DEPLOYED URL, not only localhost.