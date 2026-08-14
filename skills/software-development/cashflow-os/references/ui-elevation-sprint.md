# UI Elevation Sprint (2026-08-06) — research-first workflow + decisions

The owner said: "I like the landing page but the core app is meh and generic."
Both the frozen design language AND the premium bar (Tarsi/Stripe/Linear) apply —
the fix is evidence-led, not vibes.

## The workflow that worked (reuse for any "make X feel premium" request)

1. **Research wave FIRST, zero code.** Two parallel audit-only agents:
   - **Psychology agent**: loads the designer-skills (aesthetic-usability,
     doherty-threshold, hicks-law, fitts-law, millers-law, von-restorff-effect,
     law-of-common-region, law-of-proximity, interfaces-that-feel, loading-states,
     feedback-patterns, form-design, error-handling-ux, onboarding-design) →
     delivers psych-backed findings (principle + problem + fix), the light-vs-dark
     verdict for the domain, what transfers from the admired reference vs what
     doesn't, and top-5 zero-risk quick wins.
   - **Design direction agent**: loads impeccable + design-taste-frontend →
     diagnosis table (canvas/depth, type scale, tracking, motion, surface
     hierarchy, composition, color discipline, number voice, density, empty
     states, interaction states, errors), a class-level elevation spec with
     **[FROZEN-CHANGE]** flags on anything touching the frozen rules, and a
     ranked top-10 (impact ÷ effort).
2. **One conscious fork → clarify tool.** The pivotal decision (accent/brand
   identity, light-vs-dark) goes to the user as a clarify with 3-4 options.
   If they dismiss it: default to the strongest recommendation and SURFACE the
   default prominently in the final report (owner's standing rule: unanswered
   clarifications → default + surface).
3. **Foundation before parallel wave.** Tokens + shared components land first
   (one turn, verified), so surface agents have no cross-file dependency:
   globals.css tokens + `.num` + `EmptyState` component. THEN dispatch the
   surface wave (5 agents, disjoint file ownership, per-audit task lists).
4. Same gate as any sprint: parent merge → tsc → ECC → build → deploy → visual
   re-check.

## Decisions made (2026-08-06) — keep these

- **Accent: `#5e6ad2` periwinkle, light AND dark, unified with the landing.**
  Was `#2563eb` (AI-template blue). Psychology rationale: the "premium" the
  owner admires is the accent/type/restraint, not the darkness; a split accent
  = two brands = the "meh". The accent change was a frozen-rule override —
  shipped on the dismissed-clarify default, flagged in the report.
- **Light stays the default shell.** Psych: dense ledger scanning, trust
  convention (banks are light), long sessions. Dark = perception, not
  performance. Dark MODE stays, rebased onto the landing palette.
- **Number voice = mono ledger.** `.num` utility (font-mono, tabular-nums,
  -0.02em) on every financial figure — the landing already advertises mono
  ledger numbers; the app now delivers them.
- **Elevation over flatness.** Visible shadow scale (old shadows were below
  perception threshold). No gradients — elevation only.
- **EmptyState component** for all empty/error states; 👋 emoji banned.

## Psychology findings worth keeping (finance-app specifics)

- `window.confirm()` / `prompt()` / bare "Loading..." = the strongest
  "this is a prototype" signal when handling money → inline confirms / dialogs /
  skeletons.
- No freshness indicator ("Updated just now") → users can't tell stale money
  from fresh.
- Filter changes must NOT blank the page into skeletons (keep rows dimmed +
  inline "Updating…") — biggest perceived-performance win.
- Loss aversion: frame net ≥ 0 as "You kept ₱X" (gain frame); budget 75-100%
  pre-warning "₱X left" before the red bar.
- Goal-gradient: "Just ₱500 to go!" near completion; completion moment.
- Never let decorative motion compete with numbers (Von Restorff): money
  moving (count-up) is the one place animation belongs.
- Eyebrow overload: tracking-[0.06em] caps everywhere hurt legibility — bump
  to 0.12em and ration to section labels (form fields get plain text-xs labels).

## Deferred (queued, not lost)

Optimistic quick-add + undo toast (needs approval-flow care — undo re-inserts
as pending for staff entities), goal-gradient + logging-streak widgets (new
data needs), full motion stagger cascade, dark-mode deep polish pass, page
padding standardization (`px-4 md:px-6 lg:px-8` + `space-y-6`).
