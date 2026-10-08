# Reference Hierarchy for Fidelity QA

When a build is judged against design docs, demos, and feedback history, decide
the source of truth BEFORE cataloguing mismatches.

## Hierarchy

1. **Latest intended state** — the newest feedback and corrections.
2. **Demo videos / live walkthroughs** — behavior, flow, transitions, what
   happens after each action.
3. **Design frames (Figma/PDF)** — layout, spacing, typography, components,
   states, terminology.
4. **Older artifacts** — superseded frames, earlier video cuts, exploratory
   screens. Evidence of history, NOT requirements.

## Rules

- **Videos = how it should work. Frames = how it should look.** A behavior
  visible only in video still gets implemented; a visual detail with unclear
  behavior gets its behavior from the surrounding video flow.
- **Accumulated user feedback = regression tests.** Flows the user previously
  rejected (removed tabs, banned terminology, dropped approval steps) must
  stay removed even when an older reference still shows them. Before building
  from a reference set, search session history for prior complaints about the
  earlier versions of that reference — that list is the regression suite.
- **Frames can be stale states**: duplicated flows, dead-end explorations,
  role-variant copies of the same screen. A screen's visible chrome (navbar,
  role context) is part of its identity — don't mix role variants mid-flow.
- **When sources conflict and it changes the product story, flag it; don't
  silently pick.** Priority: prototype UI → narration/script → deck → old
  timing plans.
- Terminology bans flow downstream everywhere: narration, UI copy, test
  assertions, fixture states. A banned word in a test assertion means the test
  encodes the rejected feature — invert it to an absence assertion.

## Cross-reference QA gate (before declaring done)

| Source | Question |
| --- | --- |
| Final video | Does the app behave the same way? Same workflows, same state transitions? |
| Design frames | Does the UI match: layout, hierarchy, components, terminology? |
| Previous versions | Were previously fixed problems kept fixed? |
| User feedback | Was anything explicitly rejected reintroduced? |

Any "no" is a defect against the build, not a style opinion.
