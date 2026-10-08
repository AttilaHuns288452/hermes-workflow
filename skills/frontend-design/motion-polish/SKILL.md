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
- Honor prefers-reduced-motion in CSS and in JS timing (see templates/useClosable.js).
- Two self-tests on every animation: the boring test (would the interface feel stale, broken, or slower without it? if nothing feels missing, it is decoration) and the too-much test (would removing it improve the experience? then remove it).

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

## Templates

- templates/useClosable.js: known-good React delayed-unmount closer (exit motion, reduced-motion aware). Reproduce with modifications for other stacks.
- templates/motion-vocabulary.css: keyframe family for overlay fade, sheet rise, dialog fade+scale, success pop, global press feedback, and the reduced-motion kill block. Copy into a project without a motion vocabulary and rename to its token family.