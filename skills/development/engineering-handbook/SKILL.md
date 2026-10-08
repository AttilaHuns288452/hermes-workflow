---
name: engineering-handbook
description: Use when building a repo's offline engineering handbook.
triggers: [engineering guide, offline documentation, portable docs, documentation system, knowledge base, engineering handbook, docs traceability, system logic page, defense documentation]
---

# Engineering Handbooks (verified, self-contained, offline)

Deliverable: **one HTML file at the repo root** a teammate can download and double-click —
no server, no npm, no CDN. `docs/*.md` are the sources; a generator compiles them; the HTML is
never hand-edited alone. Different class from Obsidian-vault notes (`productivity/project-documentation`).

## Standing rules

- **Repository is the source of truth.** Audit current HEAD (code, SQL migrations, edge
  functions, config) before writing; when old docs contradict the code, document the code and
  fix the stale claim. Never copy an old explanation forward unverified.
- **No invented identifiers.** Every file path, function/trigger name, table, migration, and QA
  suite named in docs must exist. If it cannot be proven, write `Not verified from repository`.
- **Engineering tone, not marketing.** Explain WHAT → WHY → HOW → DEPENDS → WHAT WOULD BREAK;
  integration pages trace user action → UI → lib/RPC/Edge Function → DB function/trigger/
  constraint → state change → notification/provider.
- **Traceability is the product.** Every section carries an Implementation table
  (Layer | exact file/object + symbol | what it does) and a master traceability table near the
  top (Feature × Frontend / Server-RPC / Database / External / QA).
- **Delivery:** HTML at repo root + copy to `~/Downloads` + README pointer (where the file is,
  "Download raw file / double-click"). Sources stay regenerable (generator reads docs/ + live
  source slices) — the HTML alone is never the only copy of the knowledge.

## Procedure

1. **Recon in batches** (tree + symbol inventory + targeted greps). Function/trigger names from
   migrations beat docs and beats memory — naming eras mix (`audit_x` vs `trg_audit_x`), and
   plausible-sounding names that don't exist fail the same way.
2. **Write docs sources** (`docs/*.md`) per the content rules above; cross-link sibling pages.
3. **Reference checker first** (`verify_*.py`): every backticked path exists, every claimed
   symbol exists in migrations/src/edge-fns, referenced migrations/QA files exist, key factual
   claims greppable. Run it BEFORE regenerating — it catches invented names while the text is
   still cheap to fix.
4. **Generator** (`build_guide.py`): markdown subset → one HTML with grouped sidebar nav,
   runtime DOM-based search, copy buttons (event delegation + `execCommand` fallback for
   file://), single-pass syntax highlighter, dark/light toggle, prev/next, mobile drawer.
   Register sections in the generator's section list — never patch only the HTML output.
5. **Validate** (checklist below), fix, regenerate, deliver.

## Generator pitfalls

- Self-contained means **0 external `<script>/<link>/<img>`, 0 `fetch()`** — grep the output.
  Only `<a href="https://github.com/...">` links may leave the machine.
- Python f-strings: no backslashes inside expressions (hoist regexes to variables) and template
  braces must be doubled in the embedded CSS/JS.
- Markdown converter: merge consecutive `> ` lines into ONE blockquote or every line becomes a
  separate card; give inline `code` `overflow-wrap:anywhere` (long tokens otherwise force
  horizontal page overflow on mobile — table/code wrappers must scroll, not the page).
- Syntax highlighting: ONE tokenizer pass with alternation (comments|strings|keywords|numbers);
  cascaded regex passes corrupt each other. Copy buttons read `textContent` so spans are safe.
- Diagrams must be offline-safe: ASCII in code blocks or inline SVG — mermaid needs a CDN.
- Code-block scrollbars are invisible by default in screenshots — style them before visual QA.

## Validation checklist (all must pass)

1. `file://` open + **all network blocked** (route-abort) at 390/768/1024/1440: no horizontal
   overflow, drawer nav on mobile
2. search finds new sections (query an identifier that lives only there), deep links resolve,
   0 broken internal anchors, 0 console/page errors
3. link checker across `docs/*.md` + README (`.md` links must resolve to real files)
4. secret scan of the HTML (keys, tokens, demo passwords) — env vars shown as names + placeholders
5. **vision QA** the screenshots (split blockquotes, contrast, overflow, "polished engineering-docs
   aesthetic?") and fix what the vision model flags
6. reference checker green (step 3) after the final edit

## Pitfalls

- A docs page that invents symbol names survives review and dies in a defense Q&A — the
  reference checker is the gate; run it after every content edit, not once at the end.
- Duplicate skill/doc names across local and external dirs resolve ambiguously — name content
  at class level and check for collisions before naming.
- A screenshot of a smooth-scrolling page taken mid-flight reads as "half blank page" — emulate
  reduced motion in visual QA before believing a rendering defect.
