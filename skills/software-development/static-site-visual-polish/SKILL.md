---
name: static-site-visual-polish
description: Use when polishing or finishing a static promo site.
---
# Static Site Visual Polish

Final-polish and de-theme passes on existing static HTML/CSS product sites, typically Figma-bound. Companion to `redesign-existing-projects` (the generic design audit lives there); this skill carries the rendered-verification protocol, AI-de-theming checklist, and deployment workflow that session after session keeps proving out.

## Standing constraints

- Static and Figma-safe: no animation-dependent content, minimal absolute positioning, layouts reproducible from a screenshot. Regenerate the import board after the last visual change.
- Never fake external brand assets: official store badges unmodified with exact wording ('Get it on Google Play' / 'Download on the App Store'), real scannable QR only (generate with `qrcode`, self-check by decoding the PNG with `zxing-cpp` inside the generator), destination = one documented constant; the page's own URL is an honest placeholder until real listings exist. Text fallback link beside any QR.
- Claim register discipline: if the project has a claims/messaging doc, every visible claim traces to it. Omit client-suggested features the register doesn't cover, and say so in the report.
- Latest directive wins: a mid-task palette/scope directive supersedes earlier ones. Re-check built work against it; forward it to a running build subagent via steer rather than restarting.
- One-pass autonomy: when the user grants it ('do not wait for approval', 'execute in one pass'), run audit → fix → QA → deploy without pausing; in interactive sessions, present the plan first.

## Procedure

1. **Recon before touching anything:** git state (revert or commit stray work first), design docs, claims register, then render every page at 1280/768/390 and capture full-page screenshots (scroll through first so lazy images load).
2. **Audit in two tracks, in parallel:** (a) delegated vision/geometry audit with per-viewport screenshots — instruct auditors to measurement-verify every flag and rank BLOCKING/polish/nit; (b) automated DOM audit: overflow per viewport, computed grid column counts, console errors, broken images after scroll, heading outline, CTA-label consistency, form labels, em-dash and mono scan on visible copy (strip `<head>` and comments — meta tags legitimately keep em dashes).
3. **Fix**, smallest diff first, respecting the pinned palette/type contract; purge dead CSS in the same pass (see pitfalls).
4. **Verify rendered, not source:** re-run the full matrix (pages × viewports) with console/link/image checks; adjudicate remaining vision findings against DOM geometry.
5. **Deploy and confirm live:** push, then curl the live URL for a marker of the new build (a new class, a changed string); GH Pages takes 1–3 min.
6. **Report:** what changed, what was flagged and rejected as hallucination (with the DOM evidence), what remains placeholder.

## Palette re-theme pass (proven across four full identity swaps)

When the directive is a new palette identity, not a tweak:
1. **Contrast-check the palette before writing CSS.** A node WCAG-ratio one-liner over every text/background pair (button fill, badge ink on soft background, hero text) — tune ink-on-soft tones until text pairs clear 4.5:1. Getting the numbers first kills a whole round of audit flags.
2. **Keep the theme swappable:** palette tokens in the main stylesheet + identity rules in one overlay file. A re-theme is then a token swap + literal sweep, not a hunt through 20 pages.
3. **Sweep non-token literals.** `var()` never reaches inline SVG `fill=`/`stroke=`, favicon `data:` URIs, JS chart palettes, per-category tint maps, rgba() glow values. After the swap, grep every old hex across css/js/html — residuals hide in all of these.
4. **Copy names colors.** Fix captions like "coral dots" when the accent changes; re-shoot the screenshot matrix and run one vision pass asking specifically for off-palette leftovers.

## Verification pitfalls (each has cost a session)

- **Squeeze is not overflow.** A grid that fails to stack passes `scrollWidth <= clientWidth` while rendering broken. Also assert computed `grid-template-columns` count per viewport on hero/section grids (2 desktop, 1 mobile).
- **Cascade order kills responsive rules:** a page-scoped class setting `grid-template-columns` defined AFTER a `@media` block beats it at equal specificity and the layout silently never stacks. Put page-scoped layout classes before responsive blocks or give them their own override.
- **Full-page screenshots displace sticky headers** mid-capture; 'header collides with content' from a screenshot is an artifact until DOM boxes at rest prove otherwise.
- **Vision findings are hypotheses, not defects.** Models invent specific content (footer buttons, data rows that don't exist) and misread captures. Adjudicate every flag with `getBoundingClientRect`/computed styles; discard hallucinations explicitly instead of 'fixing' them.
- **Lazy images report broken without scroll.** Scroll through the page before asserting `naturalWidth > 0`.
- **Heading demotion needs sibling check:** fixing an h1→h3 skip by promoting one heading can leave it visually louder than its h3 peers — match the peer level instead.
- **Label-with-nested-span forms:** `<label>Phone <span>(optional)</span></label>` still labels the input; regex that reads only direct label text false-positives.
- **Cache-bust the stylesheet** (`site.css?v=final`) once the user has seen the old render, or stale cache gets reported as your bug.
- **Dead-CSS removal:** selector regex fails on descendant/compound selectors and multi-line rules. Use brace-depth-matched block removal or exact line surgery; assert `{` == `}` and zero remaining references before writing; check class liveness across ALL pages first.
- **Fixed-position elements phantom into full-page captures.** A fixed bar hidden with `translateY(110%)` still paints a sliver of its own height at the capture's final scroll position — every full-page screenshot then shows a mysterious off-palette band mid-page that real browsers never show. Display-gate (`display:none` until `.show`) instead of transform-hiding; probe suspects with a script scanning `body *` for wide dark `backgroundColor` values before hunting CSS.
- **Playwright without a local install:** `require('~/.hermes/hermes-agent/node_modules/playwright')` — do not npm-install into the site repo. One DOM-probe script (computed colors, bounding boxes, naturalWidth) settles vision disagreements faster than another screenshot round.
- **Vision analyzers may answer in another language**; rewrite findings into English in the report — never paste analyzer prose verbatim.

## AI-de-theme checklist

The recurring client complaint about AI-built sites: a metaphor became the whole personality. Audit for:
- Fake telemetry: unit IDs, timestamps, AUTO·ON pills, LIVE lamps, window dots, floating status cards. One real measurement in a hero mock is the ceiling.
- Mono as decoration: allowed only for measurements and compact index numbers, never kickers/labels/tags.
- Status-pill confetti: every chip/pill/lamp must carry needed data; severity via typography weight, contrast, border intensity — never color-coded lamps (amber/coral/green are AI defaults; retire wholesale).
- Metaphor-as-theme: 'station log', 'threshold ruler', 'loop nodes' everywhere = vocabulary overload; borrow 2–3 traits of a metaphor, keep one signature concept.
- Em-dash chains in copy ('clause — consequence'); rewrite as sentences.
- Instrumented section chain (hero → dashboard → loop → more dashboards); replace with editorial numbered lists and large single product visuals.
- Hero = impact, detail page = depth: one large product image, name + price, ONE metric. Spec rows, quotes, formulas, and methodology move to the detail page — a hero that explains is a report.
- Duplicate sections: the same content rendered twice (top products as full cards AND as mini rows) reads as filler; keep one.
- De-slop greps hit repeatedly: 'Why it stands out' (drop the label, the text is the strength), 'BEST MATCH FOR YOU' → 'BEST MATCH', '(mock)' → plain noun, 'Placeholder artwork' in alt text → real product name, 'scoring engine'/'black box'/'personalized' → plain words, 'Inspect gadget' → 'Details', fake-precision footlines under breakdowns → deleted.
- Card-in-card: three feature boxes → editorial columns (large display word + small copy, no boxes); boxed list rows → borderless rows sitting on the page.
- Composition pass, not component pass: kill per-category rainbow tints to one brand family, de-emphasize secondary charts (smaller heading, plain section, moved below product proof), strip flow-step copy to number + word.

## Deterministic scoring honesty pass

When the task is making a scoring/recommendation engine data-feasible ("no AI, deterministic"):
1. **Classify every data field by provenance** and write the table into the data-file header + README: RAW (marketplace/source) / GW-EDITORIAL (manually maintained) / GW-CALCULATED (documented formula) / USER-GENERATED.
2. **Remove non-defensible metrics from the engine first, then grep every sibling surface:** weights-panel chips, reason lines, comparison verdict switches, catalog filters, admin forms, docs. A metric removed only from the engine keeps rendering in six other places.
3. **Replace lifespan-derived calcs with one fixed documented window** (monthly cost = price ÷ 36) applied identically to all products — comparable and defensible, no per-product invention.
4. **Missing-data policy in writing:** a missing spec renders "Not specified" and contributes nothing to scores; never impute.
5. **Verify determinism with a vm-harness double-run:** same inputs twice → identical ranking JSON across every category×use-case combination; assert priority weights still sum to their fixed total after any redistribution.

## Figma import board

Regenerate from final pages, not from an old board: inline the shared CSS, flatten every `var()` token to literal values, base64-inline images (jpg/png AND svg — qr codes and badges live in different extensions), strip sticky/animation/keyframes/backdrop-filter, point inter-page hrefs at `#`. Assert the output contains no `var(`, no `position:sticky`, no `@keyframes`, balanced braces, and the expected frame count. Carry `<body class="...">` page-scoped classes onto the page's frame wrapper — a plain `<body>` regex extraction silently drops those overrides.

## Know when to stop

The site is finished when it is disciplined, not busy. After the audit findings are resolved and QA is green, stop: no new sections, no new effects, no redesign of what the user already approved. Whitespace is intentional; do not fill it. Keep honest disclaimers (prototype, placeholder photography, not-a-diagnostic) — they are credibility features, not defects.
