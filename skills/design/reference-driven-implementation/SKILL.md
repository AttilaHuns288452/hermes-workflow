---
name: reference-driven-implementation
description: Use when building apps from Figma, video, and feedback refs.
---

# Reference-Driven Implementation

Build/reconcile a shippable app from reference artifacts (Figma frames/PDF exports, demo videos, prior user feedback) instead of a fresh spec. Build the product the references collectively describe — not a screenshot copy of any single one. References split authority:

- **Video / demo recordings = behavior**: flows, state transitions, what happens after each action, which features exist at all.
- **Figma frames = visuals**: layout, hierarchy, spacing, components, colors, terminology.
- **Past user feedback = regression tests**: every previously reported problem is a permanent acceptance check.
- **Latest reference wins** over older ones. Old artifacts contain exploratory screens, removed flows, and superseded states — never reintroduce a feature just because an older reference still shows it.

## Procedure

1. **Inventory every reference** (video files, Figma exports, scripts, timeline/production JSONs, prior app versions). If a video was produced by a scripted pipeline, its timeline JSON + narration cues ARE the behavior spec text — read them instead of OCR-ing frames.
2. **Extract the behavior spec from video**: goal → screen → action → system response → state change → next screen. Narration assertions ("confirmed instantly", "every paid appointment becomes income") are functional requirements. Words banned from narration (look for banned-word asserts in the video pipeline) mark features the product must not have.
3. **Extract the UI spec from Figma** — see `references/figma-pdf-extraction.md`. Build page inventory with role/nav taxonomy and flow chains; flag duplicate/outdated/modal-state pages.
4. **Recover regression history** with `session_search` for past complaints about earlier versions. Distill each to a rule; each becomes an automated check asserting the correction SURVIVES (usually: the banned thing is ABSENT).
5. **Write the reconciliation delta** before coding: requirement (source) → expected behavior → current implementation → status. Conflicts resolve by: newest reference > accumulated corrections > older references.

   Before writing a status for a "missing" feature, diagnose which kind of missing it is: `git log --follow` on the implementation file plus a grep of the original prototype/source distinguishes **never ported** (rebuild it from the prototype) from **regressed** (revert or reapply the fix). The two look identical in the UI but take different fixes.
6. **Implement the minimal delta** in the existing app (behavior from video where flow conflicts, visuals from Figma). Keep corrections that already shipped; don't rebuild what's right. For a multi-page rebuild: shared keystone components (shell/navbar, cards, state hooks) first, then parallel page rewrites on disjoint files against per-page frame-copy extracts. The first integration pass must check cross-file shell conflicts — a page rendering its own navbar/footer while the router shell renders one too — before building.
7. **Cross-reference QA before declaring done:**
   - A. vs final video: same workflows possible, same state transitions?
   - B. vs Figma: layout/terminology/hierarchy consistent? Treat vision-diff findings as hypotheses: verify every claimed deviation against the live DOM (innerText probes, computed styles, element counts) before fixing — downscaled side-by-side stitches systematically misread small currency glyphs, counts, and colors.
   - C. vs previous versions: every earlier fix still fixed?
   - D. vs user feedback: nothing rejected reintroduced?
   - Banned-feature sweep: grep the SHIPPED artifact (built bundle / rendered file) for banned strings and dead routes — absence verified in the built output, not just source.
   - Responsive sweep for web UIs: assert no horizontal overflow (scrollWidth vs clientWidth) at 320/390/768/1280/1366/1440/1920 on every route. Unbreakable tokens (large mono numbers, long ids) overflow via min-content inside narrow grid cells even when every element's rect fits the viewport — stack them on mobile (`block md:inline`) rather than shrinking type.
   - Run the full test suites; update suite assertions in the same commit when behavior intentionally changed.

## Pitfalls

- A failing test that asserts a REMOVED feature is the test bug — invert it into a regression guard asserting absence.
- Reference priority is per-DECISION (behavior vs visual), not per-file — a single PDF can be authoritative for layout and stale for flows.
- The same UI page often exists in multiple role variants; role identity comes from the visible navbar, and the variant is part of the screen's identity (see `product-demo-film` role-context rule).
- Suites encode the old behavior long after the app changes: grep them for the removed feature's strings when a feature is deleted, not just the source tree.
- Report the QA as a matrix against each reference, not a vibes statement — this user checks claims against the artifacts themselves.
- A fuzzy patch matcher can "succeed" against near-duplicate code blocks (two JSX closures differing by one token) and silently corrupt the survivor. In any session with parallel file writers, run a syntax transform check (`esbuild transformSync`, loader `jsx`) after EVERY patch, and inspect the diff whenever your anchor predates someone else's edit.
- A probe that guesses a route slug hits the not-found fallback and looks exactly like a missing feature. Resolve ids from the data file before concluding anything is broken.
- Copy inside a design mock is literal ground truth, including the mock's own quirks (duplicated words, contradictory footnotes). Reproduce verbatim and flag quirks in the report — silently "fixing" frame copy breaks the fidelity review.

## References

- `references/figma-pdf-extraction.md` — reading a Figma PDF export as a product spec (inventory, role taxonomy, flow chains).
- `references/test-harness-pitfalls.md` — engineering agent-run Playwright suites that survive reruns and UI redesigns.