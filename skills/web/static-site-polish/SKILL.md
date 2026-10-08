---
name: static-site-polish
description: Use when polishing or iterating a deployed static HTML site.
---

# Static site polish & iteration

For promoted HTML/CSS sites (GitHub Pages / static hosts) that are already live and
in an approved visual direction: audit the RENDER, make targeted fixes, verify at
three viewports, rebuild the Figma import board, push, verify the deploy.

## Standing preferences (Attila)

- "Improve / impro" means significant visible upgrades, not an audit plus spacing
  tweaks. Verify everything, then commit and push without asking.
- "Tighten / compress" a section means recompose it (root-cause its height), never
  shrink padding globally: measure the section height vs viewport at 1280/768/390,
  find what actually inflates it (an image at natural size, a one-off max-width,
  stacked margins), fix that, and confirm the next section peeks into the first
  viewport without the section feeling cramped.
- Preserve decisions the user already approved. A newer directive wins, but never
  silently revert an approved decision; if leftover working-tree changes contradict
  it, `git checkout -- <files>` back to HEAD before starting.
- Placeholders are documented in-code and swap in one place; never fabricate store
  URLs, metrics provenance, or capabilities. Honest footer disclaimers stay.
- Copy rules: no em dashes in visible copy, no kickers/eyebrows above headings,
  mono type only for measurements and index numbers, no fake telemetry (timestamps,
  unit IDs, status pills). Severity/status via typography and contrast, never
  color-coded lamps, and never colors outside the pinned palette. Bulk em-dash
  sweep: enumerate unique UI sentences containing the dash OUTSIDE data blocks and
  comments, rewrite each to comma/semicolon/period; never touch data values or code
  comments. Also fix copy bugs found by review passes at the source rule, not just
  the wording: a no-op filter option gets deleted, a recovery button gets pointed
  at the editable step, and duplicated words ('priorities, priorities') get one
  canonical sentence — these are review-credibility bugs, not typos.
- When the user pins a palette, record it in the repo's DESIGN.md as tokens and
  treat retired colors as gone (delete dead token defs once unreferenced).
- Reply in plain English; be decisive — pick the path and ship it.

## Procedure

0. **Freshness-check any external review prompt.** When the user pastes a 'master polish prompt' with an attached live-site extract, grep the repo for the extract's distinctive markers (old headline, removed feature names) before acting — the attachment is often a stale CDN crawl from several passes ago. Execute only the deltas; re-doing already-shipped items churns approved work.
1. **Render first.** `python3 -m http.server <port>` in the repo root; Playwright
   full-page screenshots at 1280 / 768 / 390 plus a DOM geometry probe. Judge the
   rendered result, never the source — the source lies about cascade and overlap.
   Include section heights, container left/right edges, and image rendered size in
   the probe — tall sections and misaligned edges never show up as overflow.
2. **Root-cause user-reported interaction bugs with hit-testing.** See
   `references/qa-recipes.md` (elementFromPoint after scrollIntoView on every CTA
   and image-CTA). Bare `<img>` badges/QRs with no wrapping `<a>` are the classic
   "button does nothing" bug. Wrap them in real anchors with documented placeholder
   hrefs until real destinations exist.
3. **Delegate implementation with disjoint file ownership.** One agent per file
   set, stated as "you own exactly X; do not touch Y"; page-specific CSS goes in a
   page `<style>` block or stays index-scoped in the shared sheet. Steer running
   agents for new directives mid-flight. Commit with scoped paths
   (`git add <files>`) so a sibling agent's WIP never lands in your commit.
   READ-ONLY audit subagents (copy/UX-writing, accessibility) can run in parallel
   with your hands-on writing — they surface real logic bugs visual passes miss
   (no-op filter options, buttons targeting the wrong step, duplicated words).
4. **Fix loop.** Smallest diff at the root cause. After any CSS surgery or markup
   restructuring, re-verify computed styles and tag balance (see pitfalls).
5. **Vision QA, then adjudicate.** One batched pass; every non-CLEAN flag gets a
   DOM check before you edit. Vision models hallucinate elements (buttons, gauges
   that do not exist) and misread artifacts (see pitfalls). Discard false flags
   explicitly in the report.
6. **Figma board.** Regenerate the import-safe board (flattened vars, base64
   images, no animation/sticky) — see the `figma-board-ops` skill (channel profile,
   read-only) and the repo's board builder script if present.
7. **Push and verify the deploy.** `git push`, wait, then `curl` the live URL and
   grep for the changed markup (new selector present AND old selector absent).
   Cache-bust the stylesheet link (`site.css?v=N`) so the user's browser shows the
   new state without a hard refresh. GitHub Pages serves stale builds for 1-3 min
   after push — a production check that false-fails right after push needs a
   cache-busted URL (`?cb=<timestamp>`) before you conclude the fix did not deploy.

## Pitfalls

- **An `<img height="N">` attribute overrides CSS aspect-ratio.** Aspect-ratio only
  applies when height is auto, so a stale HTML height attribute pins the rendered
  height (e.g. 1024px for a 500px slot) and balloons the section; nothing
  overflows, so overflow checks stay green. Give CSS `height: auto` (or drop the
  attribute) and assert the rendered box matches width × declared ratio.
- **Page-scoped layout modifiers drift off the shared grid.** A section wrapper
  carrying its own max-width (e.g. 1240px inside a 1120px page grid) misaligns its
  edges from the nav and every other section — invisible per-section, obvious in
  the full page. When alignment is questioned, compare `getBoundingClientRect().left/right`
  of the header nav vs the section container instead of eyeballing screenshots.
- **Scripted multi-replace batches are all-or-nothing AND conditionally silent.**
  A batch that accumulates replacements in memory and writes at the end drops the
  ENTIRE batch when any assert fails mid-way — later runs then re-apply stale
  patches or skip them via `if x in h:` conditionals that silently no-op. After
  every write, assert each new string is PRESENT and each old string ABSENT in the
  file, and make every conditional patch print a message when it skips. When a
  browser check contradicts a supposedly-applied fix, suspect the lost write
  before debugging app logic.
- **After scripted multi-replace, verify every replacement landed.** A read-modify
  cycle that re-reads the file between steps (or a substring that no longer matches)
  drops edits silently while later steps keep succeeding. `grep -c` each intended
  replacement in the written file before building/committing.
- **Overflow checks pass on squeezed grids.** A page-scoped grid modifier defined
  after a media query wins the cascade at equal specificity and silently breaks
  stacking — the layout just compresses, nothing overflows. Assert computed
  `grid-template-columns` count per viewport instead of only scrollWidth.
- **Full-page screenshots displace sticky headers.** They render at the capture
  scroll offset and look like a mid-page collision. It is a screenshot artifact:
  adjudicate with getBoundingClientRect at rest, never from the capture.
- **Adjudicate vision flags via DOM before editing.** Expect hallucinated elements
  (nonexistent buttons, gauge rows) and false broken-image reports. Scroll through
  the page before `naturalWidth` checks — below-fold lazy images report 0/0 and
  false-fail.
- **CSS purge regexes match substrings.** A pattern written for `.p-num` also eats
  the block defining `.p-num .p-scale`. Do removals line-anchored
  (`(?m)^[ \t]*selector[^{}]*\{` plus brace-depth matching for multiline), then
  assert brace balance AND spot-check computed styles of the survivors.
- **Removing a wrapper div requires removing exactly one close-div.** Assert
  open/close `<div>` balance inside the edited section before writing.
- **Nested SVG extraction needs a greedy match.** A diagram `<svg>` containing a
  nested `<svg>` (e.g. a product icon inside a flow diagram) defeats a non-greedy
  `.*?</svg>` — it stops at the inner close and splices a truncated diagram. Anchor
  the regex on the trailing sibling (caption/footnote) or `rfind('</svg>')`, then
  assert the extracted block contains the expected number of `</svg>` closes.
- **CSS `var(--x, fallback)` breaks exact-match token flattening.** Board builders
  that replace `var(--name)` by exact string never match the fallback form, and an
  assert on residual `var(` fails the build. Use bare `var(--name)` referencing
  defined tokens (or literal values) in stylesheets a flattening script consumes.
- **Other brands' reference screenshots never go on the site.** An app-spec doc
  whose embedded images are Tapo/ThinQ shots contributes its TEXT spec only;
  extract images to an assets/app-reference folder for the team, keep mocks
  branded to the product.
- **Screen-spec text is the canonical mock source.** When a real app's IA doc
  exists (nav tabs, card variants, telemetry tiles, exact alert copy), build site
  mocks to it with marketing density — do not invent numbers or alert wording.
- **Image generation and Firecrawl share the Nous gateway credits.** When the
  gateway returns 402 BILLING_ERROR, do not fake the asset or pretend the step ran:
  route image generation through the `sensenova-image-gen` skill (xKiro, free)
  instead of reporting a dead end, and say plainly in the report that the paid
  gateway was skipped.
