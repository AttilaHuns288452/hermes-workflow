---
name: offline-docs-handbook
description: Use when building a self-contained offline HTML handbook.
---

# Offline Docs Handbook

Deliverable: ONE self-contained `.html` file a teammate downloads and double-clicks.
No server, no npm, no CDN, no fetch, no build step at read time. `file:///…/HANDBOOK.html`
must be fully useful with the network down; only optional `View source on GitHub` links may
need internet. Engineering knowledge base (architecture, modules, real code, QA), not a
marketing site.

## Always-on rules

- **One artifact, one source of truth.** The HTML is the documentation. When the deliverable
  is redirected (hosted site → portable file), remove the old mechanism in the same change
  (deploy workflows, site config, README links) — never maintain two documentation surfaces.
- **Zero external resources** in the output: no `<script src>`, `<link href>`, `<img src>`,
  fonts, or `fetch()`. Everything embedded. Only `<a href="https://…">` links are allowed.
- **Real code, extracted at build time.** Snippets are sliced from the live repo by path + line
  range in the generator — never hand-typed, never from memory. Each card shows: what it does,
  concept used, why, what depends on it, tested-by (real QA suite names), source link.
- **Verify every documentation claim against source before writing it.** Grep the actual files
  for each function/file/column name the docs assert (exports, table names, RPC signatures).
  Docs that contradict the implementation document the implementation and flag the stale claim.
- **No secrets.** Env vars appear as names + `<configured in deployment>` / `...` placeholders.
  Run a regex secret scan (`sk_`, `whsk_`, `eyJ`, key names) over the final HTML before delivery.
- **Source text is shown, not summarized away.** When the handbook reproduces source material
  (user prompts, transcripts, quotes), show EVERY real item, exact wording preserved (typos
  included), visible inline. Collapsible `<details>` is for optional depth only — never for the
  content the section exists to carry; hidden-by-default source text reads as hiding. One
  verbatim home: a long source appears once (full transcript); other sections reference it by
  anchor/timestamp instead of duplicating giant blocks.
- **Honest limitations stay in.** Unverified device tests, missing AV scanning, known flakes —
  documented, not hidden.
- **Final report = the brief's checklist form** (PASS/FAIL per criterion) + files changed +
  explicit "Application behavior changes: NONE" when docs-only.

## Procedure

1. **Audit the repo at HEAD.** package manifests, src tree, migrations, edge functions, QA
   scripts, deploy config. Fix any stale doc claims found (see always-on rule 4).
2. **Write content as structured markdown** (one file per section), then compile with the
   generator. Keep the md as regenerable source; state which of md vs HTML is authoritative.
3. **Generate the single file** from `templates/guide_builder.py` skeleton: embed all CSS/JS,
   sections as `<section id>` + hash nav, sidebar grouped nav, runtime DOM-based search index
   (no build-time JSON), copy buttons on code blocks, single-pass syntax highlighting,
   offline diagrams (ASCII in `<pre>` or inline SVG — mermaid needs a CDN, so it is out),
   dark/light theme via `localStorage`, prev/next nav, mobile drawer, skip link + focus states.
4. **Validate with `scripts/guide_qa.mjs`** (adapt playwright path): `file://` URL, all non-file
   requests aborted, viewports 390/768/1024/1440, overflow check, drawer, search queries,
   copy button, deep link, theme toggle, console/page errors.
5. **Vision QA 2-3 passes** on screenshots (desktop + a code section + mobile). Fix real
   defects, re-run step 4.
6. **Retire any hosted mechanism** being replaced: delete deploy workflows + site config;
   if the repo must go private: `gh repo edit <owner>/<repo> --visibility private` (older gh
   has no `--accept-visibility-change-consequences` flag — it errors; omit it).
7. **Report** (checklist form) + commit + push.

## Pitfalls

- Consecutive `> ` markdown lines become separate blockquotes in a naive converter — merge
  consecutive quote lines into one `<blockquote>` or the callout renders as split cards.
- Long unbroken inline `<code>` tokens (paths, identifiers) force mobile horizontal overflow —
  `code { overflow-wrap:anywhere }` but keep `pre code` at `normal` so code blocks scroll instead.
- A flex header (brand + version + search + buttons) overflows at 390px — hide the version
  badge below 640px and make the search input `flex:1; min-width:0`.
- Python f-strings cannot contain backslashes inside expressions (3.11) — hoist any `re.sub`
  with regex escapes to a variable before the f-string.
- Anchor screenshots capture smooth-scroll mid-flight (blank top half, stale nav highlight) —
  playwright context `reducedMotion: 'reduce'` before screenshotting `#anchor` landings.
- Vision models report below-the-fold content as "missing" and clipped scrollable code as a
  defect — confirm with DOM queries (element counts) before changing anything; horizontal
  scroll on code blocks is a requirement, not a bug.
- `navigator.clipboard` may be unavailable on `file://` — copy buttons need a textarea +
  `document.execCommand('copy')` fallback.
- Syntax highlighting: one single-pass alternation regex (comments | strings | keywords |
  numbers). Cascaded replaces color keywords inside strings and comments.
- Two workflows both claiming Pages deploy fight each other; a job that fails with zero steps
  is environment-level (Pages source / workflow permissions), not the YAML — don't rewrite
  working YAML chasing it.
- Deletion safety: determine what a `docs/` folder contains before removing it (site assets vs
  content source); build inputs stay, hosting machinery goes.
- A naive md→HTML converter escapes raw HTML lines — teach it to pass lines starting with
  `<details>`/`<summary>`/`<div>` through untouched when source md uses HTML blocks, or the
  tags render as literal text on the page.
- Generator-appended blocks land wherever the append happens — after hand-written closing
  prose if that's what precedes the append, separating a section's body from its intro.
  Verify heading order by string-index positions in the assembled md before building.
- `documentElement.scrollWidth` over-reports when inner `pre`/table wrappers hold wide scroll
  content even though the page cannot actually scroll horizontally — assert behavior
  (`window.scrollTo(400,0)` then `window.scrollX === 0`), not the metric, in mobile QA.
- Playwright screenshots taken right after `setViewportSize` or mid-scroll capture
  paint-incomplete blank frames while the DOM is fine — settle ~1-2s before screenshotting,
  and re-capture once before treating a blank frame as a rendering defect.

## Support files

- `templates/guide_builder.py` — proven generator skeleton (converter + snippet extraction).
  Fill SECTIONS / SNIPPETS / diagrams; wrap output in the UI shell described in step 3
  (the full working implementation lives in the DentalVibe repo's `build_guide.py`).
- `scripts/guide_qa.mjs` — the offline/widths/interactions validator for the generated file.
