# App UI polish rules (functional prototypes / panel-compliance passes)

Use this set when the deliverable is a FUNCTIONAL web app or prototype (React/Tailwind or similar, interactive flows, committed QA gates) receiving a polish / modernize / panel-compliance pass. The Figma-import rules in `static-figma-build.md` (no animation, no transitions) do NOT apply here — this class has a deliberate, restrained animation policy.

Panel meaning of "simple" = **easy to understand and navigate**, not visually plain. Target: modern, polished, professional, mobile-first, clean, restrained, intuitive, visually hierarchical. Avoid: excessive gradients/glassmorphism, giant decorative elements, too many buttons, redundant nav, excessive animation, visual noise, dashboard-widget stuffing.

## Design rules

- **Solid chrome beats glass.** Header/bottom-nav = `bg-white` + border + subtle shadow. Reserve `backdrop-blur` for truly floating overlays. A full-page primary-color background becomes a neutral surface (`bg-gray-50`) + white cards + primary accents.
- **Restrained active states.** Nav active = color + font-weight + `aria-current`, with ~150ms transitions. No colored capsules, dots, or icon plates — vision QA reads them as noise. Icon "chips" lose their decorative backgrounds; role pills go subtle-tint instead of solid.
- **One primary action per screen.** Two stacked primaries = pick one, demote the other. Filter is the primary control of its screen; secondary actions become ghost/text buttons.
- **Money honesty.** Never hardcode a fee/price as authoritative — load it from settings with loading ("…") and unavailable ("—") states. Payment summary shows the trio: estimated total / fee due now / amount due later, plus what happens at the clinic.
- **Honest empty states, factual rows.** "No active treatment plan" beats fabricated data. List rows show only fields the data model actually has (name / price / duration); never invent descriptions. Preserve required disclosures (e.g. demo-data notices) — restyle, don't remove.
- **Dev/QA affordances that ARE the prototype's feature** (a role-switcher standing in for login) get restyled, not deleted: a subtle "Demo" pill, layered BELOW modal z so overlays cover it.
- **Animation policy:** purposeful only (nav active state, card hover/press, modal/sheet entrance AND exit, expand/collapse + chevron rotation, selection feedback, one restrained success moment). 150–300ms; transform/opacity/shadow only; `prefers-reduced-motion` honored. **Page entrances animate opacity only** (see pitfall below).

## Verification battery (run before the commit)

1. Build clean (bundler build, no warnings that matter).
2. Committed QA gates + a route crawl: every route × role renders a real page (not a placeholder).
3. Responsive sweep: N viewports × routes with programmatic zero-horizontal-overflow assertion.
4. Vision QA on rendered screenshots (mobile + desktop) for hierarchy/polish — but **adjudicate every vision claim with a DOM/measurement probe before acting** (vision misreads scrims, mid-animation states, and floating controls).
5. Ship screenshots to `~/Downloads/<project>-<pass>/` per the deliverable convention.

Report shape: changes made (grouped by area) · files changed · QA results with real tool output · remaining limitations (genuine only) · short honest assessment (including self-corrections).

## Pitfalls

- **Page-entrance `animation … both` on a route/page root freezes a containing block for every `fixed` overlay** (sheet footer unreachable, clicks land on the nav behind). Opacity-only page entrances, or fill `backwards`. Diagnosis recipe in `webapp-release-qa` pitfalls.
- **`flex-1 overflow-y-auto` sheet bodies need `min-h-0`** (container `overflow-hidden`) or the pinned footer is clipped below max-height.
- **Fuzzy patching structural JSX silently eats adjacent tags.** Build immediately after each structural patch batch; if the build error moves after each fix, stop patching and rewrite the file (`safe-file-patching`).
- **A committed QA gate that flips red after your change is the spec** unless the user directed that behavior change — restore or ask, never weaken the assert to bless it.
- **grep alternation through the terminal tool needs `grep -E 'a|b'`** — `\|` gets mangled by the shell layer and silently returns nothing.
- Keep the audit/QA battery discipline (evidence-only results, gate semantics, adversarial passes) in `webapp-release-qa`; this file covers the polish-pass design and verification loop only.
