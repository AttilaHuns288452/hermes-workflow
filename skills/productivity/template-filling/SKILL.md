---
name: template-filling
description: Use when filling document templates with real content.
triggers:
  - fill up / fill in this template
  - complete this .docx / .xlsx / .pptx template
  - write this up from our standups / meetings / chat logs
---

# Template Filling

Rewrite a template's example/placeholder content with real content drawn
from source material (chat logs, transcripts, repos), producing a
deliverable indistinguishable from the template's own formatting. For
`{{token}}` templates use the `docx` skill's `docx_template.py` instead;
this skill is for templates whose content is example prose to replace.

## Always-On Rules

- **Exact formatting fidelity is the contract.** The filled doc must
  reproduce the template's run-level formatting (font, size, bold,
  color, run splits) and paragraph spacing — not merely look similar.
- **All-black text in deliverables.** Flatten the template's accent
  colors (e.g. red variable text) to normal black; user preference for
  submission documents. Note the flattening in the delivery message.
- **Source-accuracy gate.** Every claim traces to the source material.
  Trim invented details (they read as fact); status-adjacent claims
  (DoD, progress) assert only what the source shows. Flag remaining
  assumptions (e.g. a real name inferred from a chat handle) in the
  delivery message.
- **Read back and assert.** Regenerated content is verified by text
  extraction with grammar/content asserts, never by trusting the
  generator.
- **Deliver in both homes:** final files go to `~/Downloads` AND the
  project/repo root, with a README pointer (what it is, how to open it).
- **Clean-professional look bar** (user standard: "clean as hell and
  professional, not messy"): bold only headings and short bold-label
  leads (text up to the colon) — never whole sentences, table data
  rows, notes, footers, or page numbers; no text walls (split prose
  into short paragraphs or bold-label bullets; shorten where possible);
  every table row label and header fits one line (rename slash
  abbreviations to "&" form, size columns to fit); numeric columns
  right-aligned; math uses × not x; no orphaned headings or single-line
  page-top spills (keep_together + widow_control).

## Procedure

1. **Harvest the source first.** Pull the full raw material (all
   messages/threads, not just recent) into a workspace dump file and
   read it completely before writing content. For Discord forum
   channels see `references/discord-history-harvesting.md`.
2. **Dump the template's formatting spec** (per paragraph: style,
   spacing; per run: text, bold, font, size, color). This is the output
   contract. Details in `references/docx-run-formatting.md`.
3. **Map content to the template's slot structure.** Keep the
   template's section/story shape; make IDs cross-consistent if the
   user supplies more than one document (same story set everywhere).
4. **Generate from the template file itself**, clearing only body
   paragraphs (styles, theme, page setup survive). Rebuild runs as
   explicit specs matching the dump. For docx specifics and pitfalls:
   `references/docx-run-formatting.md`.
5. **Polish pass** — apply the look bar as ONE uniform pass over the
   whole document: per-paragraph spacing/line-spacing + bold policy,
   then a single loop over all tables (identified by header content)
   for widths, numeric alignment, cell margins, borders, and
   keep-together rows. A uniform choke point beats per-table tweaks
   and keeps every table consistent with the others.
6. **Verify, in order:** (a) run-format signature diff — filled −
   template = ∅; (b) page setup equality; (c) text read-back with
   content + grammar asserts; (d) render to PDF (LibreOffice) → PNG →
   vision check, asking specifically about bold misuse, mid-label
   wraps, misaligned numbers, and orphaned lines. Then deliver per the
   both-homes rule and commit if the repo is the user's.

## Pitfalls

- Explicit `bold=False` on an inheriting run breaks format fidelity
  even though it renders the same — leave bold unset unless required.
- Trailing punctuation belongs in its own run when the template does it
  that way; glued into a content run it fails the format diff.
- Paragraph spacing differs per template (both-sides vs after-only) —
  never guess it.
- Assembled-sentence grammar bugs ("I want to to …") are invisible to
  every formatting check; only text read-back catches them.
- Renaming table labels or headers for display breaks anything keyed
  on the old text — per-row detail maps matched by `startswith`,
  width/keep-together blocks matched by header text. The fallback or
  dead block ships silently. Rename keys and matcher strings in the
  same edit, then re-dump the final table and read every cell.
- Bold-lead helpers with a minimum-length threshold skip label-only
  lines ("Return on Investment (ROI):"), leaving the whole line bold;
  label-only bold needs a post-pass: bold exactly the lead ending at
  the colon, remainder plain.
- Verify alignment and glyph claims from the docx XML (paragraph
  alignment, run text), not the rendered PNG — low-DPI vision misreads
  right-aligned short numbers as left-aligned and renders × as "x".
  Use vision for layout only: wraps, breaks, text walls, orphaned rows.
- Text-cleanup replacements (× math signs, spacing) must also run on
  table cell paragraphs — `doc.paragraphs` excludes tables — and must
  not be skipped for heading/keep-with-next paragraphs.
