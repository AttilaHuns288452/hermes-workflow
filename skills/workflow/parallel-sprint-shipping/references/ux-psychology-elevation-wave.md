# Psych-grounded UI elevation wave (audit-first, then paint)

Ran on cashflow-os (Aug 2026): user loved the dark marketing landing, called
the light core app "meh and generic". Fix = research wave BEFORE any paint,
then foundation-first implementation. Both audit agents completed in ~6 min
and independently converged — the convergence is the signal.

## Wave 1 — two parallel AUDIT-ONLY agents (no edits, no build)

**Agent P — psychology specialist.** Brief: load these skills via skill_view
(aesthetic-usability, doherty-threshold, hicks-law, fitts-law, millers-law,
von-restorff-effect, law-of-common-region, law-of-proximity,
interfaces-that-feel, loading-states, feedback-patterns, form-design,
error-handling-ux, onboarding-design), then vision-analyze the key
screenshots + read the shell/main surfaces. Deliver: (A) 15-20 prioritized
findings — each with the principle name, the current problem (page + felt
experience), the fix; (B) the BIG fork question answered psych-grounded
(light vs dark for the app shell — finance apps: trust convention, dense-ledger
accuracy, long sessions → light wins; dark is perception, not performance);
(C) what transfers from the premium landing (depth layering, type contrast,
motion) vs what does NOT (storytelling sections, glow orbs, full-bleed grids
in a dashboard); (D) top 5 zero-risk quick wins.

**Agent D — design direction.** Brief: load impeccable + design-taste-frontend
+ ui-skills-root; same evidence set + the landing's design system. Deliver:
(A) 8-12 concrete "why generic vs premium" gaps in a table; (B) class-level
elevation spec (type scale, spacing, surfaces/shadows, composition,
micro-interactions) that respects frozen tokens, with any frozen-rule change
flagged **[FROZEN-CHANGE]** + justification for conscious owner approval;
(C) light-vs-dark rec; (D) top 10 ranked by impact÷effort.

## Consolidation

Read BOTH full summary files (they're truncated inline). They usually agree
on the diagnosis — the app is a *different brand* than the landing (different
accent hue, type voice, shadow scale), plus prototype-grade tells
(window.confirm/prompt/bare "Loading..."). The psych agent's killer line: the
"premium" the user admires is the accent/type/restraint, not the darkness.

## The ONE question worth asking the user

The genuine fork: unify on the landing's accent (one brand) vs keep the
frozen accent vs go dark. Ask via clarify with 4 options. If unanswered →
default to the strongest recommendation (one brand: accent swap is one token
line, instantly ties app to landing, easy revert) and SURFACE the override at
the end. Never default to full-dark for a finance app.

## Implementation (foundation-first, then wave)

1. Parent ships tokens + shared components ALONE (accent swap, shadow scale,
   dark-mode rebase to landing palette, a `.num` ledger-number utility,
   EmptyState component) — every child brief references them as "already
   shipped, use it".
2. Parallel surface wave, disjoint file ownership (dashboard hero /
   transactions UX / shell identity / craft sweeps), tsc-only children.
3. ECC gate WITH a11y-architect (see SKILL.md §5) — it catches the custom
   popover + inline-confirm focus MAJORs.
4. Visual verification loop: agent-browser open/wait/screenshot +
   vision_analyze. Conditional UI (moments that hide without history) gets
   verified by seeding one REST row, screenshotting, deleting the row.

## Finance-dashboard psych placement cheat sheet (from the audit)

- **Gain framing**: when net ≥ 0, briefings should say "you kept ₱X" — never
  only "Spending ₱X". Loss framing dominates by default; reward logging.
- **Loss-aversion inversion**: spending is the one metric where ▲ = red
  (rising spending is the warning), ▼ = green (a cut is a win). Other metrics
  follow normal direction. Implement as a per-item `good`/`invert` flag.
- **One composite number** (Miller): the spreadsheet's "AVG Change" panel
  (MoM % per metric + a mean composite) ports as a single emphasized
  "Momentum" figure beside the per-metric percentages — one dominant number
  beats five.
- **Freshness cue**: "Updated just now" near money figures is a trust signal
  finance users check for.
- **Doherty/blanking**: filter refetches must NOT skeleton the whole page —
  keep rows at low opacity + inline "Updating…"; skeleton only on first load.
- **Prototype tells kill trust in money apps**: window.confirm, window.prompt,
  bare "Loading..." → inline confirms, real dialogs, skeletons/EmptyStates.
