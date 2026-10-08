---
name: ui-art-direction
description: Use when making a frontend UI feel designed, not templated, or when the type/spacing scale reads inconsistent (some sections too big, others too small).
---

# UI Art Direction Pass

Class of work: the user reviews a working frontend and says the UI is "too visually safe, flat, generic" — a CRUD app that got Tailwind polishing — or simply calls it ugly and says to use every UI/UX skill to improve it (same job: a full pass, not tweaks). The goal: a product **designed intentionally by a UI designer**. Covers "visual identity pass", "art direction pass", "premium but restrained" requests. The pass is art DIRECTION, not random CSS: inspect first, define the system, then implement and prove it visually.

**Opposite polarity, same class.** A "modernize this: professional, minimal, premium, avoid AI slop" brief is subtraction-first, not personality-add. The win there is removing slop (excess gradients, glassmorphism, pill-everything, giant headings, emoji-as-chrome, decorative shadows/floats, generic AI-purple branding, inconsistent spacing) and tightening the system, then adding only missing product states. Use the brief's priorities as tie-breakers: working prototype over unnecessary sophistication, functional/educational value over decoration, correctness over flashy behavior, clear hierarchy over animation. Never invent new product features in a polish pass.

Standing taste bar (user's words, condensed): memorable but restrained · premium but approachable · modern, not trendy for its own sake · simple to use, not visually bland. Must stay professional enough for a school panel / client presentation.

## Procedure

### 1. Inspect before any edit
- Map the app: routes, shared chrome (navbar/bottom tabs), component system, tailwind tokens/config, global CSS layers, assets.
- **Check the repo's own design references first** — exported proposal boards / reference HTML (e.g. `DAR-DENTAL-*.html` style files) are the already-approved visual contract. Read them for the design language (surface shapes, hierarchy, signature moves) and bring the app up to that language. Don't invent a direction the user hasn't seen.
- Diagnose what became repetitive (card monoculture, one surface type, uniform label styles) and where personality is missing. Say this in the report — it's the rationale for the system.

### 2. Define the system before touching CSS
Write the direction down (even briefly), then encode it ONCE in tokens/config/shared classes and reuse:
- **Surface rhythm**: 3-5 intentional surface types instead of uniform white cards — e.g. one strong anchor per screen (teal hero), content cards (borderless + soft diffuse shadow), one warm editorial surface for promo moments, flat list rows, semantic chips. Surface type = content role.
- **Palette discipline**: keep the existing primary; extend with ONE secondary warm accent given a named semantic role (editorial/coral = promotion only), semantic colors only for status. No rainbow, no random gradients/glassmorphism/neon blobs. A restrained secondary palette + one new component type beats a themed widget festival.
- Typography scale + one label system (tiny uppercase eyebrow, tabular numbers for money) defined in one CSS place.
- Motion tokens: 200-260ms staggered entrance on key cards, press/hover lift states, all `prefers-reduced-motion`-safe.
- One signature per screen (raised action FAB in the tab bar, composed hero art), not five.
- **Dense lists & leaderboards**: long rows in a wide container read as two disconnected islands (identity left, numbers right) with a dead middle. Fix with a real column grid + column headers stated ONCE — identical per-row label text (the same badge on every row) is label spam; move it to headers and let rows carry data only. Fill surplus width with a genuinely useful side panel (methodology/education), not stretched rows.
- Data-encoding honesty: bar length must encode the dimension the list ranks by (a "cheapest wins" list must not draw the biggest bar on the most expensive item — invert or drop the bar); ratings must not overstate (partial-fill stars so 4.5 renders 4.5); "est." values state the assumption in plain language ("est. monthly over 36 months"), never as decorative labels.
- One hero number per row (the ranking key) with `tabular-nums` on all figures; demote identifiers to quiet size. A separate header row must share the cards' exact horizontal insets (including a transparent border matching rows' accent bars) or the columns visibly float off their headers.#### When the complaint is scale inconsistency ("some sections feel too big, others too small")

Treat it as a system bug, never a list of sizes — do not resize the named elements until they agree with each other ("make all the text bigger" makes it worse; the user's rule: "do not just increase or decrease random font sizes"). Diagnose the underlying typography/spacing system, then rebalance PROPORTIONS: some named elements go up, others go down.

1. **Audit rendered truth first**: script computed font-size/line-height per named element at the judging width. The signature root cause is TWO parallel type systems — a scale bumped at one breakpoint plus hardcoded px values that never followed it — and the audit shows which system each element is on (e.g. section h2s rendering near h1 size while their own explanations sit below the scale's floor).
2. **Write the target hierarchy table** (~10 named levels) before editing anything: hero h1 56 → section h2 38 → subhead 24 → card title 20 → body 18 → supporting 16 → label 14 floor is a working example. Move every named element onto it: headings shrink, small text grows.
3. **Encode ONE scale across breakpoints** and tokenize hardcoded sizes with a mechanical mapping (10-12px→xs, 13→sm, 14→xs, 15/17→base, 19→lg). Exclude subsystems that own their own scale (admin shells running px + zoom) — folding them in regresses them.
4. **Couple spacing with type**: grown text needs proportional padding/leading in the same pass. Then the standard loop: re-render full page → crop strips → vision QA (references/vision-qa-loop.md) → fix → project QA gates → ship.

### 3. Implement in batches, verify each
Order: token/config layer → global shared chrome → highest-priority screen (usually the home/dashboard) → secondary screens. After every batch: fresh build → screenshot → targeted vision critique ("check only these three items") → fix confirmed issues. Batched CSS additions especially need the class-definedness grep (see pitfalls).

Include a product-states pass in the batches: every data surface needs loading (skeleton or quiet spinner), empty (guidance, not a blank void), error (styled callout naming the failure), and a quiet done state; dev/demo-only controls never persist in the shipped UI. Mobile verification at 390 includes ≥40px touch targets and no horizontal overflow (fix at the flex/grid child with `min-width: 0`, never global clipping).

### 4. Verification loop (mandatory — see references/vision-qa-loop.md)
Capture at the user's judging width (1920×1080 desktop — density and type size are judged there) plus 390 mobile, and iterate until the vision verdict is "ship/shippable" on both. "Close" is not done.
Vision critiques the screenshots; **every color/contrast/visibility claim is arbitrated against ground truth (computed styles, pixel samples, DOM geometry) before changing the design**. Close with: fresh build, project QA gates green, settled final screenshots, visual confirmation of the last fixes, then commit + push + report with evidence (gate counts, screenshot path). Copy the hero screenshot to `~/Downloads/` per the user's deliverable convention.

## Pitfalls
- **Screenshot after animations settle** (600-1200ms post-load, or wait for the entrance class to finish). Mid-entrance screenshots show faded/offset content that vision reports as "invisible text" / "missing chip" — hunting those phantoms costs whole rounds. Re-shoot settled before believing any visibility verdict.
- **Vision is unreliable on color/contrast** (says cream blends into background, misreports hues); it is reliable on layout, copy, truncation, hierarchy. Verify color claims with `getComputedStyle`/pixel sampling; reject the critique when numbers contradict it — and say so in the report.
- **Hidden duplicate DOM nodes**: one visible string may exist twice (responsive/aria copies, one with width 0). A fix landing on the hidden copy looks done in source while the visible node still shows the bug. When fixing clipping/truncation, probe all matches of the string and filter to visible nodes (`offsetWidth > 0`); measure with `innerText` (rendered text), never `textContent` (pulls hidden nodes). Likewise, a `textContent.includes()` filter resolves to the ancestor WRAPPER first (textContent includes all descendants) — match leaf/near-leaf nodes before measuring, or you read a container's metrics and call the section "missing". The same hazard hits hook selectors: a welcome/empty-state surface can duplicate the real panel's data hooks, `querySelector` returns the hidden copy first, and a content check passes against a blank page — scope UI assertions to the owning panel's container.
- **Batch CSS edits can silently miss**: a fuzzy `patch` may report success while a whole block never lands. After adding plain CSS classes, grep the stylesheet for every new class name before building — an undefined class renders transparent and surfaces as a mystifying "color/contrast" complaint.
- **Tailwind config changes are not picked up by a running vite dev server** (JIT was configured at startup). New palette tokens render as raw fallback colors in dev while the built output is correct. Verify against fresh `vite build` output or restart the dev server before debugging "wrong color".
- **Tailwind v4 `@theme` rescales can invert tiers**: overrides layer on defaults, so redefining `--text-3xl` larger than the untouched default `--text-4xl` leaves 4xl rendering smaller than 3xl. When rescaling, redefine every tier in the chain (xs through 4xl) in one pass and verify the rendered order with a computed-size audit.
- **Fuzzy patch on JSX can eat a closing/opening tag**, leaving a hybrid fragment; the build error is the detector. Anchor JSX edits on unique single lines. (Deep detail: external `safe-file-patching` skill.)
- **QA gates asserting exact wording** break when the brief deliberately changes copy (e.g. new promo naming). Rewrite the check to assert the invariant ("promo carries the clinic's approved naming"), don't force the UI back to stale copy — but do flag genuine copy-truncation bugs the vision found.
- Adding a `border:` shorthand in a custom CSS class overrides Tailwind per-side border utilities on the same element (the custom class lands later in the cascade). Put the accent edge inside the class itself and drop the utility from the markup.
- Relocating a DOM block (footer, section) = add-new + remove-old: grep for the old copy before building — a "move" that only adds ships a visible duplicate.
- **Duplication claims need a render count, not a source grep**: when vision says a block or formula renders twice, count rendered `innerText` occurrences first. Count 2 with the string appearing once in source = a shared component mounted twice — grep the component's render sites; a source grep alone "disproves" real duplicates.
- **Composite display names go through one helper, never string concatenation**: rendering `{brand} {model}` when the data's model field already starts with the brand produces "Samsung Samsung Galaxy S23". Route every composite name (cards, tables, summaries) through one dedupe-aware display helper; grep for `brand} {`-style concatenations to find stragglers.
- Currency/special glyphs (₱ U+20B1) are absent from some display/mono webfonts and fall back to a broken, strikethrough-looking glyph. Extend the font stack with a fallback that has the glyph and confirm it in the screenshot — the string being present in the DOM proves nothing.
- **SVG text scales with its viewBox**: an axis label at fontSize 11 in a 720-wide viewBox renders ~2.5× at full-bleed desktop width. Size SVG labels for effective rendered px and cap chart `max-width` — "unreadable chart labels" are usually an oversized container, not a font-size problem.
- **SVG sprite `<symbol>` icons: stroke styles must live on the icon class (or each symbol), never on a wrapper `<g>`.** Styles on a parent/sibling `<g>` do not cascade into `<symbol>` contents pulled in by `<use>`, so every icon renders as a solid black blob while the sprite source looks correct. Put `fill: none; stroke: currentColor` (+ stroke-width, linecaps) on the `.icon` rule targeting the `<svg>`, and verify by rendering, not by reading the sprite.

## Related
- External `visual-only-restyle` (executor-side restyle under a logic freeze) and `vision-audit-deepseek-handoff` (vision audit → coder handoff) overlap on verification; this skill owns the art-direction pass itself.
- `prototype-transplant` / `design-prototype-transplant` when a full prototype folder is the source of truth.
