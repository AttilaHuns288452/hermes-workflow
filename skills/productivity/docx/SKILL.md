---
name: docx
description: Create, read, edit, template, and review Word .docx files.
version: 1.1.0
author: Nous Research
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [word, docx, documents, office, templates, revisions, comments]
    category: productivity
    related_skills: [pdf, xlsx, powerpoint]
---

# Docx Skill

Create, read, edit, and template Microsoft Word `.docx` files with
python-docx via small CLIs. It handles text, styles, lists, tables,
images, headers/footers, `{{token}}` templating, tracked changes
(list/accept/reject), comments (list/add/delete), TOC and page-number
fields, and package health checks. It does not render documents itself
(PDF needs LibreOffice — see Converting to PDF) or edit legacy `.doc`.

## When to Use

- The user asks to generate a Word document (report, letter, contract).
- You need the text, outline, styles, or embedded images of a `.docx`.
- You must change an existing `.docx`: replace text, edit table cells,
  insert/delete paragraphs, apply styles, merge fragmented runs.
- You have a `.docx` template with `{{placeholders}}` to fill from data.
- The document has tracked changes to review, accept, or reject.
- You need to read reviewers' comments, or add/delete comments.
- A `.docx` won't open or behaves oddly and you need corruption triage.
- The document needs a table of contents or "Page X of Y" footers.
- Not for: `.doc` (legacy), `.odt`, or WYSIWYG layout work.

## Preferred: markitdown for Reading

For **reading/converting DOCX to markdown** (when you need the content for LLM analysis), use `markitdown` first — it preserves structure as markdown, which LLMs understand natively:

```bash
markitdown document.docx -o output.md   # Convert to markdown
markitdown document.docx                 # Print to stdout
```

A `markitdown` binary that exists is not proof it can read DOCX: the DOCX
converter is an optional `[docx]`/`[all]` extra, and `uv tool`/`pipx` installs
often ship without it (conversion then raises
`MissingDependencyException`/`FileConversionException`). Probe with one real
conversion; on that failure fall straight to `scripts/extract_docx_md.py`
ephemerally — no permanent install needed (do not retry markitdown):

```bash
uv run --with python-docx python3 scripts/extract_docx_md.py in.docx out.md
```

It walks `document.element.body` in document order so paragraphs and tables
stay interleaved (tables become pipe markdown; images are skipped and remain
in the source docx). Prefer it over hand-rolled docx parsing whenever the
deliverable is a markdown copy for context or analysis. Tables missing from extraction?
Check `references/table-extraction-pitfalls.md`: verify completeness by counting
`<w:tbl>` in `word/document.xml` first — body-level walks miss tables inside
`w:sdt`/`w:customXml` content controls (recursive-walk fix and the user-export fallback
live there).

Use the existing `docx_read.py` scripts only when you need structured JSON output (heading outline, styles, revisions, comments) or for editing operations (replace, insert, delete, template fill).

## Prerequisites

- Python 3.10+ with `python-docx` installed:
  `pip install python-docx` (import name is `docx`; lxml comes with it).
  Not installed and you don't want a permanent install? Every script here
  also runs ephemerally: `uv run --with python-docx python3 scripts/<script>`.
- Comments `add` uses the native API on python-docx >= 1.2 and an XML
  fallback on older versions — both are automatic.
- For image blocks: the image files must exist locally (PNG/JPEG).

## How to Run

All helpers live in `scripts/` next to this file. Run them with the
`terminal` tool; each supports `--help` and prints JSON to stdout.

```bash
python scripts/docx_create.py spec.json out.docx
python scripts/docx_read.py out.docx --text
python scripts/docx_edit.py replace out.docx --find old --replace new
python scripts/docx_template.py tpl.docx values.json filled.docx
python scripts/docx_revisions.py list out.docx
python scripts/docx_comments.py list out.docx
python scripts/docx_validate.py out.docx
```

## Quick Reference

| Task | Command |
| --- | --- |
| Create from JSON spec | `docx_create.py spec.json out.docx` |
| Full text (body+tables+headers/footers) | `docx_read.py f.docx --text` |
| Heading outline + table shapes | `docx_read.py f.docx --structure` |
| Styles actually used | `docx_read.py f.docx --styles` |
| Extract embedded images | `docx_read.py f.docx --images outdir/` |
| Detect tracked changes/comments | `docx_read.py f.docx --revisions` |
| Find/replace (formatting kept) | `docx_edit.py replace f.docx --find A --replace B -o out.docx` |
| Set a table cell | `docx_edit.py set-cell f.docx --table 0 --row 1 --col 2 --text X` |
| Insert paragraph before index N | `docx_edit.py insert f.docx --index N --text X --style Normal` |
| Delete paragraph N | `docx_edit.py delete f.docx --index N` |
| Apply style to paragraph N | `docx_edit.py style f.docx --index N --style "Heading 1"` |
| Merge equal-format adjacent runs | `docx_edit.py normalize f.docx -o out.docx` |
| Insert TOC field before para N | `docx_edit.py toc f.docx --index N -o out.docx` |
| "Page X of Y" footer fields | `docx_edit.py page-numbers f.docx` |
| Fill `{{tokens}}` | `docx_template.py tpl.docx values.json out.docx --strict` |
| List revisions (id/author/date/text) | `docx_revisions.py list f.docx` |
| Accept / reject all revisions | `docx_revisions.py accept-all f.docx -o out.docx` (or `reject-all`) |
| Accept / reject one revision | `docx_revisions.py accept f.docx --id 3 -o out.docx` |
| List comments (+anchored text) | `docx_comments.py list f.docx` |
| Add comment anchored to text | `docx_comments.py add f.docx --target "phrase" --text "note" --author You` |
| Delete comment by id | `docx_comments.py delete f.docx --id 0` |
| Health-check the package | `docx_validate.py f.docx` (exit 1 on errors) |

## Procedure

1. **Create.** Write a JSON spec with `write_file`, then run
   `scripts/docx_create.py`. The spec supports: `page` (size + margins in
   mm), `header`/`footer` strings, `footer_page_numbers` (adds a
   "Page X of Y" field footer), `styles` (custom paragraph styles with
   font, size, bold/italic, hex `color`), and `blocks` — `heading`
   (level 1-9), `paragraph` (either `text` or a `runs` list where each run
   may set `bold`/`italic`/`underline`), `bullet_list`, `numbered_list`,
   `table` (`header` row rendered bold, `rows`, optional built-in table
   `style` such as `Table Grid`), `image` (`path`, optional `width_mm`),
   `toc` (Table of Contents field), and `page_break`. The full spec
   format is documented at the top of `scripts/docx_create.py`.
2. **Read.** Use `scripts/docx_read.py` with exactly one mode flag.
   `--text` returns body paragraphs, all table cell text, and
   header/footer text as JSON. `--structure` returns the heading outline
   plus paragraph/table/section counts. `--images DIR` copies every file
   under `word/media/` out of the package.
3. **Edit.** Use `scripts/docx_edit.py`. `replace` walks body, tables
   (nested included), headers and footers, and preserves run formatting;
   add `--body-only` to skip headers/footers. Pass `-o out.docx` to keep
   the original; omit it to edit in place. Paragraph indices for
   `insert`/`delete`/`style`/`toc` refer to `--structure`/`--text` body
   order. Run `normalize` first on documents that came out of heavy Word
   editing — it merges adjacent runs with identical formatting so later
   find-replace matches reliably.
4. **Review revisions.** `docx_revisions.py list` reports every `w:ins`
   and `w:del` (id, author, date, affected text) anywhere in body,
   tables, headers, or footers. `accept-all` / `reject-all` resolve them
   in bulk; `accept`/`reject --id N` handles a single revision. Accept
   keeps insertions and drops deleted text; reject does the reverse.
5. **Comments.** `docx_comments.py list` returns each comment's id,
   author, date, body text, and the document text it is anchored to.
   `add --target "some phrase"` anchors a new comment to the first
   occurrence of that phrase (runs are split as needed; formatting is
   preserved). `delete --id N` removes the comment and its markers
   without touching document text.
6. **Template.** Put `{{name}}`-style tokens in the document. Run
   `scripts/docx_template.py` with a JSON object of values. Use
   `--strict` to fail when tokens remain unfilled; the JSON output lists
   `filled` counts and `unfilled_tokens` either way.
7. **Verify** (always): re-read the output with `--text` or
   `--structure`, and run `docx_validate.py` on anything you produced
   via revision/comment surgery. For a layout-sensitive deliverable,
   also render to PDF (`soffice`), run `pdftotext` to assert the new
   figures are present and stale figures are gone, render the affected
   pages to PNG, and inspect them (vision) for clipped or overlapping
   tables before claiming done. Glob the PNG output instead of constructing
   filenames: `pdftoppm` pads the page number to the page count's digit width
   (`page-01.png` in a 27-page document), so a hand-built path fails as
   file-not-found immediately after a successful render. Sequence the two: finish the render first,
   then analyze in a later call; a vision read of an image another process is
   still rewriting returns stale content that looks like a fresh bug report. Check glyph-level content (math,
   superscripts, non-Latin) at ≥ 200 DPI — low-res renders misread glyph
   shapes, and "fixing" correct output to match a misread is real damage.

## Whole-section replacement in an existing document

When one section must gain new paragraphs and tables while every other
section stays untouched (feasibility studies, reports with a fixed
letterhead): snapshot the original to a dated backup, then write a
one-shot python-docx script keyed to the backup's paragraph indexes.
Rewrite existing paragraphs in place (clear children except `pPr`,
re-add runs), build new blocks with `add_paragraph` +
`addnext`/`addprevious` against an anchor element, and edit the cells of
tables that already exist instead of recreating them. Regeneration rule:
the script must always start from the backup (`cp backup target &&
python edit.py`) so it is idempotent and paragraph indexes stay stable
across re-runs. Verify afterwards that content outside the edited range
is byte-for-byte unchanged (compare paragraph and table-cell text
against the backup).

## Transplanting a formatted header block from another document

When the deliverable must carry another document's header (school block with
seal images, letterhead), python-docx cannot move drawings between packages.
Structured package surgery is the sanctioned exception to "don't unzip the
xml": edit the docx as a zip of parts with a zipfile round-trip — copy parts
and register them; never text-substitute into xml.

1. Copy the source header part (`word/headerN.xml`) and the media files its
   drawings reference (`word/media/...`) into the target package.
2. Register the part in `[Content_Types].xml`; add its relationship in
   `word/_rels/document.xml.rels` under a fresh rId that collides with nothing,
   and write `word/_rels/headerN.xml.rels` so the drawing targets point at the
   copied media.
3. Point the target section's header reference at the new rId and copy the
   source's page geometry (margins, header distance) — a verbatim header on
   different margins renders clipped or floating.
4. Self-check before delivering: header part present, media bytes copied,
   reference id resolves, content types registered, geometry copied.
5. Verify by rendering page 1 of BOTH the target and the source and comparing.
   A "missing" border or shading is often not a transplant defect — render the
   source first and match what it actually shows, not what the block is assumed
   to look like.

## Table surgery in place (preserve existing formatting)

When editing tables inside a document someone else formatted (or a pipeline-styled deliverable the user has since edited), edit cells/rows/tables surgically instead of rebuilding the table — rebuilding drops the document's styling. Primitives (python-docx):

```python
def setcell(cell, text, size, bold=False):   # size read from a peer cell in the same column
    cell.text = ''
    r = cell.paragraphs[0].add_run(text)
    r.font.name = 'Arial'; r.font.size = size; r.font.bold = bold

def del_row(t, i):            t._tbl.remove(t.rows[i]._tr)
def del_table(t):             t._element.getparent().remove(t._element)
def del_paragraph(p):         p._element.getparent().remove(p._element)
new = t.add_row()             # appends; position it with:
t.rows[n]._tr.addprevious(new._tr)
```

- `cell.text = ...` (and the `set-cell` helper) resets the cell's runs to plain formatting — match the row peers' font name/size explicitly on every run you write.
- Rewrite a paragraph's text without losing formatting by setting `runs[0].text = new` and blanking `runs[1:]` — but only when `p.runs` is non-empty; paragraphs created by `add_row()` or `add_paragraph()` have NO runs, so a runs[0]-keyed helper silently writes nothing. Fall back to `p.add_run(text)` when `p.runs` is empty.
- Row edits match per CELL, never across the row: each cell is its own paragraph, so an anchor written as `"Label | Value"` or `"Label ... Value"` can never match anything. Match `row.cells[0].text.strip()` to identify the row, then write the value cell (`row.cells[-1]` or the index you dumped) separately.
- After surgery, walk `document.element.body` in order pairing every "Table N." caption paragraph with the next table's first cell and assert: each table has its caption, numbering is sequential, and prose has no cross-reference to deleted/renumbered tables (grep `Table \d+` in paragraphs).

## Converting to PDF

No script needed. When LibreOffice is installed, convert headlessly:

```bash
soffice --headless --convert-to pdf --outdir outdir/ file.docx
```

When converting several Office files in one run, give each its own
`--outdir`: same-basename inputs (`a.docx` + `a.pptx`) both emit `a.pdf` and
the second silently overwrites the first.

Check availability first (`command -v soffice || command -v
libreoffice`). If neither exists, tell the user PDF conversion is
unavailable in this environment rather than improvising — python-docx
cannot render PDFs, and layout fidelity requires a real renderer.

## Deliverable reports (standing user preferences)

- **The polished document file is THE deliverable.** When the mission names a
  document (CBA, proposal, report), the formatted DOCX + PDF is the artifact
  the user opens: lead the completion reply with its MEDIA: links and its
  one-paragraph what's-inside summary. Registers, markdown sources, and
  calculation models are supporting material for the package folder with a
  README pointer. A reply that reports the package work without the file
  front-and-center reads to the user as "no deliverable" ("where is it").
- **"I cannot see it" after a verified edit means stale viewing, not a failed
  edit.** When probes prove the content is present but the user reports it
  missing: render the changed pages to PNG (`pdftoppm`), show them inline via
  MEDIA:, and name the exact page/table location plus the mechanism (the
  viewer holds a pre-edit buffer, or the backup copy is open). Re-editing
  blind to "make it appear" corrupts a correct document.
- **Tables over prose.** Any block of text that can be a table must be one. Prose is limited to one-line lead-ins before each table; the only acceptable long paragraph is a citation/source list.
- **Every numeric cell shows its derivation** in a "How computed"/"Computation" column with explicit arithmetic (`₱4,654 + ₱300 + ₱500 = ₱5,454`). A figure without a visible trace is a defect.
- **Label each figure's nature**: verified price, supplier listing, official plan limit, internal project figure, planning assumption, or calculated estimate. Assumptions must read as assumptions; never present an estimate as a measurement.
- **Source-of-record**: when the project's own documents (CBA, proposal, plan) contain a figure — an electricity rate, a BOM, a quota — cite that document as the source of record and put external sources alongside as cross-checks. The user prefers this over external-only sourcing.
- **User values override the brief**, and one change propagates everywhere: figure changes go through the calculation pipeline (script → machine-readable output → document → reports) in one run. Never hand-patch a single artifact — stale figures in sibling deliverables erode trust faster than wrong ones.
- **Cost deliverables are cash cost to the payer.** Unpaid student labor is not a line item unless the user asks for imputed labor; funding comes from whatever model the user states (e.g. team contributions), and missing facts get labeled "to confirm", never invented.
- **No internal traceability codes in body prose** (user correction). Source/calculation/gap/risk IDs (S-001, CAL-403, GAP-011, CF-07 ...) live only as row labels inside register tables (assumptions, gaps, risks, sources); prose and summary tables say the plain thing ("the Feasibility Study", "not yet measured", "the room-size conflict"). A complaint about "special codes/characters" or "word blocks" triggers a scripted readability pass: token map code→plain words, references renumbered to plain [n], word-heavy sections converted to tables. Registers keep the IDs so traceability survives without the clutter.
- **Money-table layout (user-judged).** Note/footnote rows merge across all columns
  (long note text in the first column of a wide numeric table explodes into a tall
  slab beside empty bordered cells). Label column ~30% of table width, numeric
  columns right-aligned so decimals line up and sized to their values, data cells
  uniform weight (no mixed bold). Judge the result from the rendered page, not the
  text extraction.
- **Conclusions and recommendations are insight lines, not prose blocks.** Short
  judgment sentences covering the section's full scope; when the user names
  examples of what to say, those are examples, not the limit.
- **Order table rows for reading**, e.g. descending value bands (20,000 -> 15,000
  -> 10,000), never raw source order. A mis-ordered scale reads as sloppy to
  reviewers even when every number is right.
- **Label:value metadata blocks align at one tab stop** (title page: Project
  Name / Prepared By / Date). Set a tab stop at a fixed position and give the
  paragraph `left_indent = tabstop, first_line_indent = -tabstop` so wrapped
  values hang under the value instead of falling to the far left; LEFT-align
  the block — a justified paragraph stretches word gaps and both readers and
  vision QA report the stretch as "double spaces".
- **Removing a concept deletes it everywhere**: its rows, tables, notes, AND
  any sentence announcing its absence ("there is no X in this analysis"). The
  finished document simply does not contain the topic.

## Pitfalls

- **Tokens split across runs.** Word often fragments text into several
  runs. The replace helpers collapse matched runs (replacement inherits
  the first run's formatting); running `docx_edit.py normalize` first
  reduces fragmentation for all later edits.
- **Revision coverage.** `docx_revisions.py` resolves run-level
  insertions and deletions (the overwhelming majority). Paragraph-mark
  and table-row revisions, format-change records, and moves are detected
  by `--revisions` but not auto-resolved — see
  `references/revisions-and-comments.md` and hand those to Word.
- **Comment threading.** Replies and "resolved" status live in
  `commentsExtended.xml`, which this skill ignores; comments it adds are
  plain top-level comments.
- **Field results are computed by Word.** `toc`, `page-numbers`, and the
  `toc`/`footer_page_numbers` spec options write *field codes*.
  Word/LibreOffice populates the actual entries and numbers when the
  file is opened (Word may prompt to update fields); python-docx never
  computes them, so placeholder text shows until then.
- **Validation is a health check, not schema validation.**
  `docx_validate.py` verifies the zip, required parts, relationship
  targets, image magic bytes, and referenced styles. It is NOT XSD
  validation — a file can pass and still contain XML Word dislikes.
  When triaging warnings on an EDITED file, run the validator on the
  pre-edit copy too: warnings identical in both are inherited false
  positives (e.g. relationship-id complaints where the relationships
  exist and LibreOffice renders fine), and only warnings present solely
  in the edited output indicate the edit broke something.
- **Style names must exist.** Applying a style that isn't defined in the
  document raises `KeyError`. Built-ins like `Heading 1`, `List Bullet`,
  `List Number`, `Table Grid` exist in the default template; custom
  styles must be declared in the create spec first.
- **Numbered lists restart.** `List Number` relies on Word's default
  numbering; separate lists in one document may continue numbering
  instead of restarting. Warn users needing precise multi-list numbering.
- **Cell writes replace formatting.** `set-cell` uses `cell.text = ...`,
  which resets runs in that cell to plain formatting.
- **Encoding.** All JSON specs/values files are read as UTF-8 explicitly;
  never rely on locale defaults when writing your own glue code.
- **Hash filename variants before converting.** Downloads commonly holds
  `revised (1)`, `revised (2)`, `final` copies of one document; `md5sum`
  them first — byte-identical copies are one document, and converting each
  produces divergent markdown you must later reconcile.
- **User-supplied filenames can carry invisible spaces.** Google Forms/Sheets
  exports and hand-renamed files may contain U+202F (narrow no-break space) or
  U+00A0 where a normal space appears, so a path copied from display text
  fails `FileNotFoundError` against a file that visibly exists. Discover input
  files with `glob` and take the path from the match, never from rendered text.
- **A user-supplied markdown export may be stale.** When both a `.docx` and
  an `.md` of the same document exist, verify the export against the docx
  with distinctive anchor strings (part numbers, names, spec figures)
  before adopting the `.md` as canonical — a stale export silently diverges
  from the real document.
- **Table column widths need tblGrid.** Setting `cell.width` (tcW) alone is not enough: LibreOffice/Word lay tables out from `w:tblGrid` gridCol values, so columns render evenly divided and text breaks mid-token. Also set gridCol widths in twentieths of a point (`int(width_inches * 1440)` via `t._tbl.find(qn('w:tblGrid'))`) whenever you set cell widths. Budget the column-width sum against the usable page width (page width minus both margins — A4 with ~0.87 in margins ≈ 6.5 in): oversized tables get silently shrunk or clipped at render. Each column must also fit its longest unbreakable word plus ~0.24 in padding — width budgets sized to average content still break short header words mid-token.
- **`add_table` on a block container needs `width`.** In current python-docx, `Document.add_table(rows, cols, width=...)` and the body-level equivalent both require a `width` argument; pass `Inches(sum(col_widths))` and set the per-column widths right after.
- **Don't unzip-and-sed the XML.** Edit through the scripts (or
  python-docx); raw text substitution in `document.xml` corrupts files
  easily. Use `patch`/`write_file` only for the JSON inputs, never on the
  `.docx` itself.
- **Node `docx` library: `Paragraph` children must be `TextRun` instances.**
  Plain `{text: ...}` objects passed as children are silently dropped — the
  package builds, validates, and opens with all headings present but EMPTY
  bodies. Wrap every run in `new TextRun({...})`, and verify content by
  extracting `word/document.xml` text (or `markitdown`) and checking it
  against the source model: package health alone cannot catch missing text.
- **A `.docx` extension is not proof of a Word file.** On any import or upload,
  validate the package before trusting its content: ZIP magic `PK` at offset 0
  AND a `word/document.xml` entry. Renamed text files and damaged archives get
  one clear rejection message naming the problem — never a stack trace, and
  never a silent empty import.
- **If you parse `document.xml` with regex (no DOM in scope), the self-closing
  alternative must be exactly `<w:p[^>]*/>`.** A bare `\/` in the pattern also
  terminates paragraphs at `<w:b/>` inside `<w:pPr>`, silently swallowing the
  paragraph's text. Prefer a real XML parser when one exists; otherwise anchor
  the self-closing form tightly and prove it with a round-trip.
- **Every generator needs a round-trip test**: build the file with your own
  writer, re-import it through your own reader, and assert headings, table
  rows, and Unicode survive. Package validity cannot see text that was
  silently dropped or swallowed.
- **Section-targeting loops must be style-aware, not text-prefix-aware.** TOC entries repeat heading text ("10. Conclusion and Recommendation<TAB>22"), so a loop matching `text.startswith('10.')` or a heading phrase hits the TOC line first and injected content lands in the table of contents. Require `p.style.name.startswith('Heading')` (or exclude lines containing a tab + page number) when locating a section's body range.
- **Scripted text injection can leak literal `\uXXXX` escapes into the document.** A replacement string built with `'\\u2019'` in a generated script writes the 6 visible characters, not the apostrophe. After any scripted text write, sweep paragraphs AND cells for literal backslash-u sequences and convert them to real characters before rebuilding the PDF.
- **A merged full-width row reports one cell at every index.** `row.cells` returns
  the same merged `tc` at all positions, so a formatting sweep over `cells[1:]`
  (e.g. right-aligning numeric columns) silently formats the merged note cell too.
  Detect merged rows with `len(set(id(c._tc) for c in row.cells)) == 1` and handle
  them apart (notes read left-aligned).
- **Repeated `add_row()` + `addprevious(t.rows[1]._tr)` inserts rows in REVERSE order** (each new row lands above the previous one). After batch insertions, re-sort the row block explicitly from the cell values and assert the final order by reading the cells back — insertion order is not row order.
- **A surgical edit script that exits 0 is not proof any edit landed.** Probe and print the real row/cell labels before writing match patterns at all — label qualifiers drift (a parenthetical form assumed vs a comma form actually present) and a guessed anchor misses silently. Make every edit branch print its anchor-hit count and treat zero hits as a reported failure, never as success — silent no-matches (stale anchors after a prior pass rewrote the text, curly-vs-straight quote drift, wording drift from format conversion) are indistinguishable from success otherwise. Verify with count-probes over the FULL text (body paragraphs AND every table cell's paragraphs) asserting new strings present and superseded strings count 0 before rebuilding any derived artifact.
- Deleting tables strands their caption paragraphs and breaks caption numbering. A "Table N." caption is a separate paragraph from its table; removing the table element leaves the caption orphaned and every later caption misnumbered. Post-delete routine: reword or delete stranded captions, renumber the rest sequentially, fix prose cross-references to old numbers, and re-audit caption-to-table pairing — a caption filter matching only paragraphs that START with "Table" will silently skip captions you already reworded mid-cleanup.
- **Reference audits need whitespace-tolerant matching.** Word runs carry NBSP (U+00A0) where a plain space appears, so literal-substring searches like `'Table '` miss exactly the references they were meant to audit and return a clean-looking zero. Match with `[Tt]able\s+\d+`-style regex (`\s` covers NBSP) and treat zero matches as suspicious until one probe proves the pattern can hit known text. Zero-width characters (U+200B) are not `\s` and also vanish in `pdftotext` extraction, defeating both the docx regex and the PDF grep; when a probe returns zero and text is expected, dump `repr()` of the candidate paragraphs/cells to expose invisible characters before concluding absence.
- **Phantom numbering complaints have two known mechanisms; fix the mechanism,
  never the correct numbering.** (1) Captions render above their table grids, so a
  caption paired mentally with the NEXT table reads as "heading says N, caption
  says N+1". (2) A table split across a page break repeats its header row on the
  next page; a reader counting visible grids then sees a +1 drift per split table,
  and the identical complaint returns every review round with the same offset
  pattern. Before chasing the complaint: renumber the caption stream sequentially,
  audit every in-text and in-cell "Table N" reference (references to a cited
  source's own tables, e.g. "study Table 5.4", are legitimate and stay), and check
  the contested range for split tables. Glue a table that must not split:
  keep_with_next on its caption and every lead-in paragraph up to the grid, plus
  every cell paragraph in all rows except the last. Name target tables in
  cross-references ("Tables 27-28, the sensitivity and scenario tables") so
  navigation survives any counting method. If captions and references are
  consistent and no splits remain, report the reader artifact; never renumber
  correct captions to match a miscount.
- **A hand-built TOC (tab + literal page number, not a Word field) goes stale on every rebuild.** Sync it from the BUILT PDF (`pdftotext`, find each heading's page), with four traps: a bare `^\d+\.\s+[A-Z]` heading regex also matches table rows ("11 PHP 9,994") and patches TOC entries to junk pages — match against the known section titles instead; strip the entry's section number before comparing or matching silently returns zero patches that look like "already correct"; match FULL titles — sibling headings sharing a 15-char prefix ("What the customer pays"/"What the customer gets") steal each other's pages; and headings living on the TOC page itself fall outside measurement — keep those entries out of the fix loop rather than assuming the first two pages are heading-free.
- **Never content-check a .docx by grepping its raw bytes** — the zip is
  compressed, so grep hits and misses are both meaningless. Read parts via
  python-docx or unzip first, then assert.
- **Generated workbooks with formulas need a recalculation check.** openpyxl
  writes formulas with no cached values, so reading the file back shows
  nothing computed; convert a copy with LibreOffice (recalculates on load)
  and read the computed values back — assert check rows evaluate to zero.

## Verification

- After create/edit/template, run `docx_read.py out.docx --text` and
  check the expected strings appear (and old strings are gone).
- After accept/reject, `docx_revisions.py list` should return `[]` (or
  only the ids you intentionally left); after comment surgery,
  `docx_comments.py list` should reflect the change and `--text` output
  must be unchanged.
- `docx_validate.py out.docx` exits 0 with `"ok": true` on a healthy
  package — run it after any revision/comment/field manipulation.
- For templates run with `--strict`, or check `unfilled_tokens == []`.
- Structure checks: `--structure` should show the expected heading
  outline and table shapes; `--styles` confirms custom styles applied.
