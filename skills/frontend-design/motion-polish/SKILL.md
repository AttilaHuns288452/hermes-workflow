---
name: motion-polish
description: Use when adding or auditing motion or polish in a web app.
---

# Motion polish

Purpose-driven pass over an existing web app: inventory the motion language, remove forced motion, implement state-change motion with proper exits, and verify every surface. This user's bar: the app must feel responsive, alive, polished, and intentional without being slower, distracting, childish, or artificially animated.

Purpose contract (applies to every animation, always):
- Each animation must answer at least one: does it help the user understand what changed, establish continuity between two states, show where something came from or went, give feedback for an interaction, make navigation smoother, communicate hierarchy, make an important action feel satisfying, reduce perceived waiting, or add polish without slowing anything down. If none apply, do not add it. Never animate because the page looks empty.
- The app must feel like a professional product, not a landing page. Forbidden: random fade-ins on load, card bounce-in staggers, exaggerated springs, constant floating elements, unnecessary parallax, giant zooms, auto-playing decoration, and any animation the user must wait for before content is usable.
- Exactly four motion categories, matched to the magnitude of the change: (1) micro-interaction feedback (press, hover, focus, success), (2) surface transition (modal, sheet, dropdown in/out), (3) context transition (page, tab, accordion state change), (4) gesture transition (drag-follow carousel). Never zoom a small element like a modal.
- Speed: 100-200ms state changes, 200-300ms page transitions, 300-400ms rare large context shifts. Mobile shorter than desktop. Animate transform/opacity only; layout properties cause reflow jank.
- Honor prefers-reduced-motion in CSS and in JS timing (see templates/useClosable.js) — with one user-stated exception: ambient/decorative surfaces the user explicitly asked to animate (hero canvas, live demo previews) animate anyway, because their browser may report `reduce` and a frozen hero gets reported as broken/dead. Content entrances, exits, and transitions still honor it, and every animated surface keeps manual controls.
- Two self-tests on every animation: the boring test (would the interface feel stale, broken, or slower without it? if nothing feels missing, it is decoration) and the too-much test (would removing it improve the experience? then remove it).

## Two surface classes (the contract changes with the surface)
- **Product UI** (app screens, workspaces, settings): the contract above, strict. Professional product feel; no entrance choreography, no scroll theater.
- **Marketing surface** (landing page, hero, promo sections) is the one place landing-page motion IS the purpose. When the user asks for "cool" / "epic" motion, deliver: staged hero entrance choreography, a scroll progress bar, parallax depth on decorative art, directional heading reveals with self-drawing rules, staggered card grids, count-up stats. Same discipline underneath: one motion language, transform/opacity only, reveals fade content in place (never make the user wait for usability), and the same boring/too-much tests.
- **Explicit commission raises the visibility bar.** When the user explicitly
  commissions motion design, the choreography IS the purpose: staged grid
  entrances, chart-point pop-in, and hover scale are legitimate deliverables
  even on product screens, and the "no entrance choreography" default governs
  only unrequested motion. The fixed rules never move: content-in-place
  reveals (usability never waits), transform/opacity only, tight durations,
  reduced-motion honored.

## Procedure

1. **Inventory the existing motion language first.** grep the stylesheets for @keyframes/animation/transition and the components for animate-*/transition-* classes. Extend the existing vocabulary family; launching a second parallel animation system is worse than adding nothing.
2. **Remove forced motion before adding anything.** Targets: entrance staggers that replay on every page load (dashboard cards), two stacked entrance systems (page fade plus element staggers), decorative loops on non-status elements. One 100-200ms opacity fade per route change is the ceiling for navigation continuity.
3. **Implement state-change motion in priority order**, each item passing the purpose contract: global press/hover/focus feedback, then modal and sheet entrance AND exit, then save-to-confirm, then tab and selected-state transitions, then accordion/expansion reveals, then carousel gestures, then a short page continuity fade (opacity only).
   - Entrance = CSS animation on mount. Exit = delayed unmount: the node is gone the instant state flips unless unmount is delayed. Use one closer hook per dialog group (templates/useClosable.js): it adds the out-class, waits ~150-200ms, runs the real close, and closes immediately under reduced motion. Route save and cancel both through it so a dismissed form slides away and the updated view sits underneath.
   - Surface motion pairing: bottom sheets rise (translateY + fade) and exit reversed; centered dialogs fade + subtle scale (~0.97). Never mix the motions across surface types.
   - If any save ever shows waiting, the success state must outlast the loading state.
4. **Test every surface at mobile and desktop widths**: every role, home, navigation, modals, forms, loading, success/error, list changes. Assert behavior, not just looks: the out-class must appear before unmount and the dialog must be gone after; an emulated prefers-reduced-motion: reduce context must report animationName none.
5. **Second pass is mandatory.** Re-audit every animation against the purpose contract and consistency. Delete whatever is forced. The interface is calmer and loses nothing when forced motion goes.
6. Walk home, major flows, modals, lists, and transitions at both widths before claiming done, and report only what is visibly better.

## Pitfalls

- Never leave a persistent transform (animation-fill-mode both/forwards on a transform) on a page-level wrapper: it becomes the containing block and every fixed-position overlay inside it breaks. Entrance fills use backwards.
- Do not make reduced-motion users eat the exit delay: the closer must check matchMedia and close immediately, or closing feels laggy exactly for the users who opted out.
- When an automated test cannot click a control, check responsive label changes before blaming the app: the same action can have different accessible names per breakpoint ("Edit plan" on mobile, "Edit" on desktop). Scope locators to the container (e.g. [role="dialog"]) or match a regex.
- Do not add an animation library for what CSS keyframes and transitions already cover in this vocabulary; a dependency for this is dead weight.
- Do not animate presence (wiggling buttons, pulsing text). Motion belongs to change.
- Directional reveal transforms (translateX ±28px before triggering) create transient horizontal overflow at phone widths. Decorative motion must never create a scrollbar: clip at the root (`overflowX: 'clip'`) and re-run the 360 overflow probe after adding any transform-based reveal.
- Scroll-reveal observers must watch every reveal class you introduce — an orphaned variant (directional/stagger classes added after the observer's selector) stays invisible forever — and carry a forced-reveal failsafe (~2.5s) so no content can remain hidden if the observer misses.
- Assert reveal state only after settling past the failsafe window AND having scrolled the whole page: a fast scroll with a short wait catches pre-trigger and mid-animation states (`fill: both` starts at opacity 0) and reports them as hidden content — a false defect hunt that burns whole rounds.
- A CSS animation on a persistent element runs ONCE, ever — it does not replay
  on navigation. Route-level transition motion therefore does nothing after the
  first load unless the element is keyed to the route (`key={location.pathname}`
  on the page wrapper) or the enter class is re-applied per navigation. This
  silently ships a whole transition system that only fires once; verify it by
  navigating twice, not by reading the CSS.
- A stagger implemented as fixed nth-child/delay entries stops at its last
  entry (often six), so the tail of a grid enters all at once and the cascade
  dies mid-row. Drive the delay from the item index (per-item custom property)
  so it covers the whole collection, then count the distinct delays in a real
  render.
- "I don't see any difference" is a perception verdict, not something to
  re-verify code against. First rule out a stale bundle (cache-busted grep of
  the built CSS/JS, hard refresh), then treat the motion as below threshold:
  150ms fades and hover lifts read as nothing to this user — deliver motion
  noticeable at a glance on the surfaces carrying data (grids, charts) and
  verify with a before/after capture. Code existence is never proof of a
  visible difference.
- Prove motion RAN, not just that it exists: sample computed styles over time
  during load (`getComputedStyle(el).opacity` and the translate component of
  `transform` at ~100-150ms intervals) and show the values progressing. This
  settles both amplitude and ordering in one shot — a cascade is proven when
  later elements are still translating while earlier ones have arrived, and a
  dead animation shows flat values. Perceptible floors for a user who calls
  motion invisible: ~25px+ travel, 350-450ms for entrances, and ~50-60ms beat
  spacing between staggered items.
- Force a paint on every sample or the measurement is fiction. A headless
  browser does not advance the document timeline while nothing paints
  (`document.timeline.currentTime` stays 0), so `getComputedStyle` returns the
  declared `from`/base values and a live animation reads frozen or instantly
  finished — a false verdict in BOTH directions. Take a `page.screenshot()`
  per sample to force the frame, or run the probe as an in-page
  `requestAnimationFrame` loop. Two tells that the timeline is starved: the
  sampling loop returns only one or two rows, and the probe window ends before
  a multi-card cascade finishes and reports healthy motion as "never settles".
- Read the `@keyframes` body for the property you expect — not the class name,
  not the animation config. A class named `anim-fade-up` carrying the right
  `animation-name`, duration, delay and fill can still animate only
  `transform`, so every card slides in at full opacity and the effect reads as
  an insta-pop while every config inspection passes. Grep the keyframe's
  `from`/`to` blocks for `opacity` before concluding anything about a fade;
  the keyframe is where an entrance effect is actually defined.
- A reduced-motion kill block must zero `animation-delay` as well as
  `animation-duration`. Duration 0 alone leaves `fill: backwards` holding the
  element at its invisible `from` state for the whole remaining delay, so the
  users who opted out of motion get the blank/invisible window instead of the
  content.

## Templates

- templates/useClosable.js: known-good React delayed-unmount closer (exit motion, reduced-motion aware). Reproduce with modifications for other stacks.
- templates/motion-vocabulary.css: keyframe family for overlay fade, sheet rise, dialog fade+scale, success pop, global press feedback, and the reduced-motion kill block. Copy into a project without a motion vocabulary and rename to its token family.