---
name: website-improvement-pass
description: Use when improving or redesigning an existing site.
---

# Website improvement pass

Class: the user says "improve" / "polish" / "redesign" an existing site or landing page and hands a goal or spec. Expected outcome for this user: significant visible upgrades (not an audit plus small patches), everything verified, committed and pushed without being asked twice.

## Standing rules

- Significant visible upgrades: fix real bugs found, improve hierarchy and storytelling, add polish — never only spacing tweaks.
- Verify everything (serve locally, DOM checks, screenshots) and commit+push without asking twice; report what real execution returned.
- When asked to "use all design skills": state coverage explicitly — which were loaded, which applied, which skipped and why (pinned identity overrides style kits; the brief wins).
- Reply in plain English; keep status lines to one while background work runs.

## Procedure

1. **Recon before reading pages.** Locate the repo under `~/Documents/Projects/`, run `git status --short && git log --oneline -5`, list assets and build scripts. Probe `mcp__codegraph__codegraph_explore` before any `read_file` (token saver). Read identity docs FIRST (`DESIGN.md`, `PRODUCT.md`, claims/messaging register) — they outrank assumptions; pages come second. The claims register governs copy: nothing new factually, demo numbers on mocks must be labeled illustrative. **If identity docs are missing, create them before any visual work** — the user's standing pattern (moldguard) is the template: `README.md` (purpose, page inventory, architecture map, design system summary, run/verify commands, known gaps), `PRODUCT.md` (platform, stack, users, purpose, positioning, honesty rules, constraints, status), `messaging.md` (claim register with source + status, honest omissions list, visual-only claims, fact-check method, open questions). This is non-negotiable for this user — a build without the docs layer is unfinished.

2. **Load the design stack.** Load the design-director skill by its FULL categorized path (bare names collide in this environment, e.g. `impeccable` matches several installs). Run its `context.mjs` setup script once per session with cwd at the project, and load its craft-floor reference immediately before UI edits. Craft-floor rules that bite here: kicker/eyebrow labels above headings are banned (remove them on pages touched), no colored border-left/right above 1px, no hard offset shadows, body measure 65–75ch, monospace only for data readouts, contrast ≥4.5:1 body / ≥3:1 large. Fetch the web-interface-guidelines rules file fresh with `curl -sL` from its raw GitHub URL (extract tools can fail billing walls on raw fetches; curl works) and review the built page: `…` not `...`, curly quotes, alt/aria on new SVGs, heading hierarchy, focus-visible, tabular-nums on data grids, scroll-margin-top on anchor targets, explicit width/height on images.

3. **Classify constraints, then write the build spec.** If the result will be imported into Figma: static only — no new animation/transition/hover reveals/JS/video; flow layout (flex/grid), absolute positioning only for small overlay status cards; reuse existing design tokens; never rename CSS classes shared by other pages. Convert every spec point into numbered section instructions with concrete copy, labels, values, and section order, plus mandatory self-verification for the builder (serve on localhost, screenshot desktop/hero/mobile, check overflow + anchors + console, grep the diff for banned CSS additions).

4. **Delegate the build** to one background subagent with the full spec in a single dispatch. Front-load ALL hard constraints (identity contract, palette, banned patterns, claims discipline) so later directives stay additive. Require evidence in the report: screenshot paths, check outputs, diff greps.

5. **Mid-flight user directives.** When the user sends a new binding directive while the child runs, immediately steer the subagent — translated into implementation terms (exact hex tokens, which sections change, what is removed), never forwarded as prose. Steer text queues until the child's next tool result; if the child finished first it returns as missed_steer — then apply and verify the directive yourself during QA.

6. **QA and ship.** Independent pass over the diff: desktop full-page + hero-viewport + 390px mobile screenshots, no horizontal overflow at either width, all anchors resolve, console clean, palette-compliance grep (no hex outside the pinned tokens), banned-CSS grep (`transition|animation|@keyframes` additions empty). Run `scripts/svg-page-audit.py` (serves the repo, then checks every SVG `<text>` bbox against its viewBox at both viewports, plus broken images, horizontal overflow, console errors) — hand-centered SVG labels near viewBox edges overflow silently because font metrics beat hand estimates. Regenerate the Figma import board if the repo has a board builder; keep it import-safe (no `var()`, no absolute/fixed/transform, inline CSS, base64-inline images). Push, then verify the live URL reflects the change before reporting done.

7. **Product hero render.** When the page needs a photoreal product/device image and the default image tool is billed/dead, use the `sensenova-image-gen` skill (free xKiro async job API: POST → poll → CDN URL → download into `assets/`). Vision-approve the render before committing; check AI artifacts at full zoom even if invisible at display size.

## Merging two versions of one project

When the user asks to "combine the strengths" of a past version and the current one (an old commit or another repo copy of the same product), do not rebuild — port selectively:

1. **Inventory both sides before deciding.** `git log --oneline` for the old commit; `git show <commit>:<file>` to read old code without checking it out. List what the old version has that the new lacks (richer data, extra views, auth gating) and what the new has that must survive (architecture, design system, honesty fixes). The merge spec is that two-column inventory.
2. **Port data model first, UI second.** Old rich fields (`goodFor`, `notIdeal`, `uses`, `strengths/weaknesses`, review objects with year/context) merge INTO the new data structure — keep the new shape, add the old fields. UI features (scatter plot, verdict copy, card callouts) then consume them.
3. **Delegation brief lists the old source explicitly** — the child has no conversation history; tell it the commit SHA and `git show <sha>:index.html` as the extraction route, plus the exact formulas (e.g. an index/score computation) so nothing gets paraphrased.
4. **Name the non-negotiables as constraints** — the new architecture, design system, and honesty fixes stay; the old version's regressions (fake stats, admin-in-nav) do not come along.

## Version ping-pong: keep every round reversible

This user may flip direction repeatedly on the same project (revert the overhaul → then want the overhaul back → then want pieces of it again). Structure work so each flip is one command, not a rebuild:

1. **Commit every version state separately with a descriptive message** — never pile "revert + feature + fix" into one commit; the revert target must be a single clean SHA to `git checkout <sha> -- .` from.
2. **A revert means `git checkout <target-sha> -- .` plus deleting files the target lacks** — checkout alone only overwrites, it does not remove files added after the target (new pages, `css/`, `js/` dirs); `git rm -r` them explicitly and commit.
3. **Before reverting, extract the upgrades the current state added** (one-line list per feature) and re-port the cheap ones on top of the restored base — the user's revert almost never means "delete every improvement", it means "go back to that shell".
4. **When restoring old code wholesale, scrub mock/orphan IDs everywhere**: grep the whole tree for the deleted dataset's id prefixes; remap `adminMetrics`, seeded history, pending-review queues, default detail-page ids, and label maps to the surviving catalog — a `GW.getGadget(id)` returning null renders empty rows silently.
5. **Keep docs honest through flips**: after each revert/port, update README/PRODUCT/messaging to describe the version that now EXISTS, and mark superseded docs as describing an older state rather than deleting them (the user may flip back).
6. **Delegate large multi-file ports** (whole dataset rewrites, feature sets spanning 5+ files) to a background subagent with the full spec; hand-verify with `node -c` on all JS, page curl checks, and a vm-based smoke test that loads data.js and asserts the invariants (catalog size, formula parity, no orphan ids). See the jsdom/vm smoke-test pattern below.

## Palette swap from a full token spec

When the user supplies a complete color-identity replacement (exact hex per role: bg/surface/ink/primary/accent/semantic/hero + radii + shadows), it is a mechanical swap with traps:

1. **Verify every spec contrast pair before writing CSS** (primary/white, tag-ink/tag-soft, hero/white, accent-ink/accent-soft). Nudge the INK value, not the accent, when a pair falls under 4.5 — the accent is the brand, the ink is negotiable. Report the numbers.
2. **Swap the token block, then alias-check.** Stylesheets carrying legacy alias vars (`--accent: var(--primary)`, `--gold: …`) keep an old identity alive through 30+ call sites; confirm each alias maps to the right NEW role, and delete duplicate alias overrides (a second `--ink-2:` in the alias block silently beats the token).
3. **Purge literals, not just variables.** JS-injected SVG (logo marks, chart slice colors) and per-page favicons carry old hex the tokens never touch; favicons are URL-encoded (`fill='%23…'`) — sed that form too. Grep the repo for every old hex until zero hits.
4. **Re-tint per-category systems into ONE family.** Derive category tints from the new core ramp (e.g. lavender↔coral) instead of rainbow hues; the spec's distribution rule (70-80% neutral / 15-20% primary / 5% accent) applies to tints.
5. **Diff var() usage against definitions after the identity rules land** — a rule referencing a token the spec names but the token block omits (e.g. `--warm-dark`) surfaces only here. Ship with zero unresolved vars.
6. **Overlay layout:** identity rules can live in a separate CSS file that must load AFTER the base stylesheet on every page — sed the `<link>` into all HTML files and verify with `grep -l <file> *.html | wc -l`.
7. **Visual-only specs still lock copy.** Apply hero heading/CTA copy verbatim; when replacing a wired element (e.g. a hero search form), grep its attribute (`data-search-form`) first to know whether listeners become dead or must move.
8. **Featured panels show REAL products.** When the design calls for a featured-product card, render the catalog's actual top item (real photo, price, score, a real review quote) — a fictional placeholder or half-empty card reads as broken, and 'PROTOTYPE DATA' style labels get ordered removed on sight.

QA gate: `node -c` all JS, existing tests, curl every page for 200, push, then re-fetch production with a cache-buster and grep for the new tokens before reporting done.

## Prototypes: no auth, ever

When the artifact is a prototype/demo, ship it with ZERO authentication or gating UI — no login modals, no "any credentials work" forms, no `data-reqlogin` nav attributes, no `S.user` state checks before wishlist/review/account views. This user treats any auth surface in a prototype as noise to be deleted on sight; a future feature request of "add login" will be explicit. When porting old code that contains auth gates, strip them as part of the port and note the removal in the commit message.

## Pitfalls

- When a directive arrives mid-build, steering once with the FULL translation beats several partial steers — the child applies steers between tool calls, not retroactively.
- A user-reported clipped or overlapping text is one instance of a class: audit every SVG text bbox on every page at both viewports before shipping — sibling overflows are almost always present.
- After surgical CSS edits (find/replace on rules), verify the target's computed style in the browser, not just the source text — one corrupted line lets a later equal-specificity rule silently override the fix.
- **Documentation layer is mandatory, not optional.** For this user, a build is not complete without `README.md`, `PRODUCT.md`, and `messaging.md` (or equivalent identity docs). The moldguard project is the template. If they ask to "improve" a site and the docs are missing, create them FIRST — before any visual work. A future session will thank you.
- **When merging an old version in, the docs layer needs a data-status note.** If the old version's data replaces mock placeholders (real brand names, Wikimedia product photos), update `messaging.md`'s claim register to reflect which entries changed from "fictional brand" to "real product, illustrative figures" — the register must match what shipped, not what shipped last round.
- **Multi-page sites: one shell, many init calls.** Shared header/footer/nav rendered by JS (`initShell`) means every page must call the same init with the right active-nav key — audit all pages' init arguments when touching the shell, not just the page in focus. Old screenshots and stale commit copies of the same project in sibling directories are reference material only; never copy them over the live tree wholesale.
- **Shared-header injections ship site-wide.** Anything the JS shell injects into every page (skip links, badges, banners) must be checked on every page when removing or changing it — delete the injection in the shell's template function, not per-page markup, and verify with a tree-wide grep that no copy remains.
- **Aliasing a not-yet-assigned property silently breaks.** `GW.gadgets = GW.realGadgetEntries` placed BEFORE `GW.realGadgetEntries = [...]` copies `undefined`; the alias must come after the array literal (or reference the same literal). Run the data file in a vm after any reordering — the page still renders (empty grids read as "just fewer items") and only the smoke test catches it.
- **After a revert or data swap, grep the tree for orphan id prefixes** (the deleted dataset's naming scheme) across data, admin panels, seeded history, and default-detail fallbacks — orphan ids render as blank names/empty rows with no console error.
- **Smoke-test via `vm.runInContext` with stubbed globals** (document, localStorage, location, CustomEvent, URLSearchParams) to run data/app modules in Node without a browser; assert business invariants (catalog size, formula parity, Pareto-frontier sanity, per-category non-empty results). Browser-based QA on this machine is often unavailable (no launched Chrome for the harness) — vm tests + `node -c` + curl are the dependable verification trio.
- **Porting a feature between architectures means re-wiring, not copying.** A scatter/quiz/filter ported from an SPA into multi-page JS modules needs: the render function exported from the module, the container div added to the target page, the init call added to the page's script block, and the URL/params wiring re-checked — the old code's DOM hooks don't transfer by existing in the repo.

See `references/static-figma-build.md` for static/Figma-safe rules, the severity-within-palette token table, and the section-rhythm ladder. `references/documentation-layer-template.md` is the mandatory docs-layer template (README/PRODUCT/messaging) — use it whenever identity docs are missing or the user asks for "same docs as moldguard". `references/verifier-trio.md` is the vm-based smoke-test pattern with the stubbed-globals recipe. `scripts/svg-page-audit.py` is the runnable step-6 page/SVG integrity check.