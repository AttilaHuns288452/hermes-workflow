---
name: template-fidelity
description: Fill docx templates with exact formatting fidelity.
triggers:
  - fill template
  - user stories document
  - sprint documentation
  - follow the template
  - template formatting
---

# Template Fidelity

Use when a deliverable must look exactly like the user's blank template
(school docs, sprint/user-story docs, reports) while carrying real content
sourced from evidence. The blank template's formatting is a contract:
reproduce it run-for-run and paragraph-for-paragraph; fold the data into the
template's own slots; verify the rendered output, not just the text.

## User conventions (standing)

- Filled deliverables are ALL BLACK text. The blank template's placeholder
  accent colors (often red) are for the template's look, not the deliverable.
- Em dashes are banned in deliverables ("ai slop"). Rewrite with commas,
  colons, parentheses. En dashes in date ranges are fine.
- Page-number footer: "Page X of Y", SMALL (9pt), RIGHT-aligned.
- Deliverables go to BOTH `~/Downloads` and the repo/project root, with a
  README pointer saying what the file is and how to open it.
- Multi-doc sets must be coherent and cross-referencing (same IDs, titles,
  headers everywhere), and defensible: every claim traceable to a source.
- Financial/analysis tables show their arithmetic inline: the difference or
  delta cell carries the calculation ("= 58,600 one-time + 8,100 maintenance"),
  not just the result. Size that column wide enough that the arithmetic wraps
  between tokens, never mid-token.

## Procedure

1. **Inspect the template before writing anything.** Dump per-paragraph: style
   name, `space_before`/`space_after`, line spacing, run signatures
   `(bold, font, size, color)` per run, and `pPr.numPr` (numId + ilvl).
   Templates routinely style body lines as Word list items on `Normal`
   paragraphs with several indent levels; that structure is invisible in a
   text dump and flattening it is the most common fidelity failure (the doc
   reads as "one whole block").
2. **Map content to template slots first** (Template purity, below).
3. **Build from the template file itself.** `Document(template_path)`, capture
   `copy.deepcopy(p._p.pPr)` from one prototype paragraph per line kind, clear
   the body, then add every new paragraph carrying a cloned pPr. This
   reproduces numbering, indents, hanging indents, and spacing exactly; then
   set `numPr/numId`/`ilvl` on the clone for the target list level.
4. **Runs: match the template's bold convention.** Template body runs carry
   `bold=None` (inherited). Only set `r.bold = True` on labels; never set
   `bold=False` — an explicit False is a run-format signature the template
   does not have and overrides inherited formatting.
5. **Pagination polish before save.** `keep_together=True` on every paragraph;
   `keep_with_next=True` on all but the last paragraph of each contiguous
   non-blank block (chains MUST break at blank paragraphs, else Word chains
   whole sections and silently ignores it); `page_break_before=True` on
   section headings when each section should start on a fresh page.
6. **"Page X of Y" footer** (user convention: 9pt, right-aligned):
   `w:fldSimple` with ` PAGE ` / ` NUMPAGES `; put an `rPr` (rFonts + `w:sz`
   half-points) INSIDE the field's run or the number renders at default size
   while surrounding text is small.
7. **Purge placeholder colors across ALL XML parts.** Run-level color settings
   are not enough — numbering-level glyph colors and styles survive; rewrite
   every `<w:color w:val="RRGGBB">` to `000000` via zip rewrite after save.
8. **Never commit to inferred facts silently** (names, undefined terms): state
   the assumption and ask; the user answers and it goes in verbatim.

## Reformatting an existing document to match a template's look

When the user hands a FINISHED document plus a separate template and says "use
the template's formatting — the font, line spacing, line dividers etc": the
template is the formatting spec; the document keeps ALL its content and
figures untouched.

A complaint naming several symptoms ("page breaks and alignment and line
spacing... the entire file") is a request for a whole-document normalization
pass — sweep every paragraph and table to canon; spot-fixing the named
symptoms reads as incomplete.

1. **Render the template first** (`soffice --headless --convert-to pdf` →
   `pdftoppm -png -r 85`) and vision-check it BEFORE writing code. Vague
   format words need disambiguation: "line dividers" is usually full-width
   thin paragraph bottom rules (`w:pPr/w:pBdr/w:bottom`, sz 6), but could be
   table borders or spacer paragraphs. Record the spec per role: body/heading/
   title font+size+bold+color, margins, section rules, table grid color and
   header fill.
2. **Get ground truth from the template's XML**, not the render: count fonts,
   sizes, and `w:color` values across runs. Low-dpi vision cannot tell serif
   from sans or 10pt from 12pt, and flips between reports.
3. **Apply as ONE normalization pass at the end of the build** (a
   `apply_template_format(doc)` block right before `doc.save()`): body font/
   size, heading overrides, blank-paragraph spacing, section rules, table
   grids + header fills. Never scatter per-element patches — the next content
   edit forgets them.
4. **Sweep runs at XML level**: `doc.element.body.iter(qn("w:r"))`.
   `Paragraph.runs` misses hyperlink runs AND the paragraph-mark run
   properties (`w:pPr/w:rPr`), which carry stale colors. Auto-create `rPr`,
   set `w:ascii/hAnsi/eastAsia/cs`, and keep rPr child order (rFonts AFTER
   rStyle, sz BEFORE szCs) or Word offers to "repair" the file. Any `w:color`
   rewrite must target only children of `w:rPr` — table borders and shading
   elements also carry `w:color`.
5. **Blank spacer paragraphs inherit large before/after spacing** — that is
   the "blocky" look users complain about. Normalize every empty paragraph to
   zero before/after and single line spacing.
   6. **Repair flow (page breaks + orphans).** Remove stray `pageBreakBefore`. A
   `w:sectPr` with NO `w:type` child IS a `nextPage` break: demoting it to
   continuous means INSERTING `<w:type w:val="continuous"/>` — renaming a val
   on an absent element no-ops silently (a patch that "worked" without
   changing the page count is this). Place `w:type` after header/footer refs
   inside `sectPr` (child order is schema-enforced; wrong order makes Word
   offer to "repair" the file). Bind every table to its full lead-in chain:
   walk back from the table through consecutive non-empty paragraphs setting
   `keepNext`, covering heading + basis note + spacers — binding only the
   nearest paragraph strands the heading on one page while the table starts
   on the next.
   7. **Upsizing fonts re-wraps every table cell.** Regex-scan extracted text for
   money values split mid-token (`Php\d[\d,.]*$` line followed by bare digits),
   widen the offending columns at the TARGET font size, and add `w:tblHeader`
   to header rows so tables that now span pages repeat their header.

## Authoring a NEW deliverable to match a reference document's look (pandoc route)

When the deliverable is authored as markdown (long analytical document, many computed
tables) and the user hands a finished reference DOCX for the LOOK ("make it look like
this"), the reference is a style contract only, never a content or figure source.

1. Extract the reference identity BEFORE writing code: render 4-6 representative pages
   (title, TOC, a table page, a heading page) AND dump its XML facts — heading
   font/size/bold/color per level (styles.xml plus run-level overrides), body font and
   alignment, title-page treatment (capitalization, what follows it), sectPr margins and
   page size, table identity (grid presence/color, header fill, label-column bold,
   number alignment), caption format ("Table N. Title" vs "Table N:"), footer format
   ("Page X of Y" vs bare "Page N", size, alignment), reference-list styling (hanging
   indents, URL runs). Vision gives the character (sans vs serif, compact vs airy); the
   XML counts settle fonts, sizes, colors.
2. Build a pandoc `--reference-doc` carrying that identity (styles including theme-font
   overrides, heading colors/spacing, Normal alignment, sectPr, footer with PAGE /
   NUMPAGES fields), generate the document from markdown with pandoc, then post-process
   with python-docx for what pandoc cannot do: title page, static TOC, numbered captions.
3. Post-processing order: content fixes -> ONE style/normalization pass -> pagination-
   sensitive additions (title page + TOC placeholders) -> caption injection -> save.
   Render to PDF, map real pagination, patch the TOC's page numbers, re-render, and
   assert the page map is stable before any page-number check counts.
4. Verify as the Verification section says: side-by-side rendered-page vision against
   the reference's pages, XML ground truth whenever the render reading is doubtful.

Command-level recipe: `references/pandoc-reference-docx-pipeline.md`.

Pandoc-route pitfalls:

- Pandoc writes TOC field codes that LibreOffice never populates, so the PDF renders an
  empty TOC (and a leftover field can print a raw "TOC" heading). Build a static TOC
  (entry paragraph + right-aligned tab + literal page number) from a two-pass pagination
  map; TOC pages shadow body matches when locating headings, so search past them.
- Heading styles inherit Normal's justify alignment: every wrapped line except the last
  stretches word-by-word and reads as scattered single words. Set heading alignment
  explicitly in the normalization pass.
- A rendered font that contradicts the style definitions is run-level `w:rFonts` or a
  theme override beating the style (pandoc emits both). Sweep run-level rFonts and settle
  fonts by counting XML, never by the render.
- Any preprocessing pass that changes line counts (blank-line insertion, list
  restructuring) silently shifts the stored line indices of every later insertion.
  Locate blocks to modify by content with a moving cursor in document order — never by
  saved line numbers.
- A regex trimming trailing whitespace (`\s*$`) also eats the newline and merges the
  next line into the match, shifting every index after it. Anchor to `[ \t]*$`.
- Pandoc only recognizes a `Table: caption` paragraph as a caption when it is blank-line
  separated above and the pipe table follows within a few lines; a horizontal rule
  (`---`) between them defeats recognition and the literal "Table: " text lands in the
  body.
- Normalize non-breaking hyphens, curly vs straight quotes, and NBSP to plain characters
  before any exact-match assertion between expected strings and extracted text —
  typographic variants look identical and fail equality.
- A multi-pass markdown rewrite runs in dependency order: structural section
  splices first (their anchors may contain the tokens a later pass strips),
  reference renumbering before token removal, pure surface substitutions last.
  A reversed pair silently no-ops on stale anchors. Body-content conventions
  for deliverable prose (no traceability codes in body, tables over blocks)
  live in the docx skill's "Deliverable reports".
- When a rewrite script splits the document into regions and transforms one,
  the transform must read AND write the region variable: renaming only the
  assignment target (`x = re.sub(..., whole_doc)` → `y = re.sub(...,
  whole_doc)`) leaves the regex argument pointing at the full document, and
  the region join then silently duplicates that content (two References
  sections ship). Post-condition before any conversion: every top-level
  heading matches exactly once, and each appended section occurs once.
- Patch generated pipeline scripts by position, not by a spanning regex:
  slice from `rindex(anchor_before)` to `index(anchor_end)`. A non-greedy
  regex from one `check(...)`/dict line to another swallows every similar
  line between them (neighboring check and figure blocks live exactly
  there), and one mismatched anchor eats real code silently.
- Reference-list entries are one paragraph each: bare one-per-line entries
  with their markers stripped collapse into a single markdown paragraph
  (consecutive non-blank lines join). Keep blank lines or list markers
  between entries, apply a hanging indent, and left-align the list —
  justify stretches short entries into word rivers.

## Template purity (user correction, enforced)

Never invent structural elements the blank template lacks (owner / "Assigned
to" lines, assignment blocks, extra columns). Fold source data into the slots
the template already has (e.g. more `Task:` lines under existing headings).
New ENTRIES within existing element types are fine (more user stories when the
data needs a home); new ELEMENT TYPES get rejected.

## Review-round responses

When the user relays numbered panel or correction comments: verify every item
against the artifact BEFORE editing — a share of review comments are already
satisfied. Answer with a per-item status table (comment → fixed now / already
met, each with its evidence), and fix only what fails verification.

When the user asks to "compare with the old one": answer with an old-vs-new
figure table, a why-the-numbers-differ list (the assumption changes the user
directed), what style was deliberately preserved from the old document, and
an honest bottom line. Never report revised figures without explaining the
delta against the previous version.

## Structure parity vs a user-supplied reference

When the user hands a reference document (or pastes its text) saying "make sure
it has the same sections as these": parity applies to STRUCTURE ONLY (headings,
sub-sections, table slots). Never copy the reference's numbers or claims — the
reference is routinely a stale draft whose figures the current model has
already corrected. Check parity programmatically: extract rendered text
(`pdftotext`), collapse whitespace, assert every section heading, named table,
and signatory row is present, and report a mapping table (reference section →
present / intentionally changed) rather than eyeballing it.

## Multi-document consistency

Generate all docs from ONE shared dataset in one script. Assert
id/title/membership/section equality at build time (selfcheck), then diff the
OUTPUT files with an independent extractor (parse IDs, titles, headers back
out of each .docx and compare) — build-time data equality does not prove the
rendered output matches. Cross-reference lines in each doc must state the
shared ID range correctly.

## Source-backed deliverables (defensibility)

- Trace every task/claim line to its source corpus (standup logs, tasking
  posts): a keyword-overlap pass flags untraceable lines for manual review;
  trim invented detail rather than shipping it.
- Every number in a generated table comes from the calculation model, which must be
  extended to compute each presented series (sensitivity, reserve, scenario variants).
  Hand-computed cells in prose tables drift from the model and are the first defect an
  adversarial review finds; one correction then has to propagate by hand.
- Before delivery run an independent second-path verification: fresh code that recomputes
  the money math from raw inputs and reconciles the document's extracted table numbers
  against the model output. Validate external/adversarial review findings the same way —
  each against the model before fixing — since a reviewer's own recomputed figures can
  carry arithmetic slips.
- Prefer structure that cannot contradict sources (one overall date range in
  the header instead of per-section dates when real activity overlaps).
- When the user supplies the real sequence/ordering of events, that OVERRIDES
  orderings inferred from timestamps; restructure the content to match it.

## Uniform generated tables (standing preference)

"The tables look inconsistent, make everything consistent" = ONE normalization
pass at the END of the build looping `doc.tables` — never per-table patches
(the next table added forgets them). Enforce on every table:

- Uniform borders on every table; a table can silently carry none and only
  look "borderless" next to its neighbors.
- Light header shading on row 0 of EVERY table — tables filled via different
  helpers end up unshaded; check each one's `tcPr/w:shd`, don't trust the
  render.
- One font size in all cell runs (10pt for deliverables), no stray italics.
- Uniform cell margins (`w:tblCellMar` on tblPr, ~115 twips) and even 2pt
  paragraph spacing in cells.
- Numeric/money columns right-aligned, text columns left. Decide per column
  data-driven (every body cell matches a money/number regex) so header and
  body alignment agree — keyword lists on header names miss cases like
  "Project Benefits".
- Column widths: set BOTH `tcW` per cell and the `w:tblGrid` gridCol values
  (LibreOffice honors the grid), and size numeric columns so headers wrap
  between words, never mid-word, and size money columns so VALUES never wrap
  mid-token at the FINAL font size (a font upsize late in the build silently
  breaks columns that fit before; re-run the extracted-text wrap scan after
  any type change). Keep headers and row labels on ONE line:
  widen the column or rename slash labels ("Database/integration" →
  "Database & integration") — slashes invite ugly wraps. Verify one-lineness
  from the extracted text, not the render.
- When you rename a display label (to fix wrapping or style), rename every
  lookup keyed on the old label in the SAME edit: detail maps, keep-together
  matchers, build asserts. A stale key fails silently to its fallback text and
  the render still looks plausible.

Table body cells stay plain (header row bold only) — enforce that at the
cell-fill helpers, NOT by mass-overriding bold in the normalization pass when
template-derived content is present (that destroys the template's run
signatures). Body paragraphs: bold line-start labels only.

Choke-point snippet (borders, shading, margins, widths, numeric align):
`references/docx-table-styling.md`.

## Targeted section replacement in a finished document

When the user says "rewrite only these sections / fill these placeholders, do
not touch anything else" in a FINISHED document:

1. **Back up the original to a sibling file first, and treat the backup as the
   rebuild source.** Re-running an edit script over an already-edited file
   double-applies or silently no-ops; regenerate deterministically by copying
   the backup over the target, then running the edit script.
2. **Script the edit as a repeatable generator**, not one-off surgery: every
   figure in the new prose must come from the same calculation output the
   verifier reads, so a rebuild cannot silently diverge from its numbers.
3. **Replace content in place**, cloning the replaced paragraph's pPr onto each
   new paragraph so the section keeps the document's styles, spacing, and list
   structure; keep the document's run conventions (bold=None inherited, label
   runs bold).
4. **Do not restructure outside the target range**: no renumbering, no table
   restyling, no footer changes.

Verification deltas for targeted edits (on top of the standard checks):

- **Untouched-range identity:** compare original vs output paragraph-text
  lists restricted to everything outside the edited range and assert zero
  paragraphs lost; assert the section headings appear in order.
- **Figure anchors:** `pdftotext` the rendered PDF and count every new key
  figure and heading. A value computed by the script but absent from the
  extracted text means the edit did not land — fix before reporting.
- **Rendered layout:** vision-check ONLY the pages containing the edited
  sections (locate them via form-feed split of the extracted text) for
  clipping, overlap, and table integrity.
- **Inherited-vs-induced warnings:** run the same package validator on the
  pre-edit backup; warnings identical in both are inherited false positives
  (report them as such, do not chase them), warnings present only in the
  output are regressions to fix.

## Verification

1. **Run-format signature diff:** sets of
   `(style, space_before, space_after, bold, font, size, color)` for template
   vs output; assert `output - template == empty`; page setup equal.
2. **Render:** `soffice --headless --convert-to pdf` → `pdftoppm -png` →
   vision check (structure, colors, blocks intact, section-per-page starts).
   Locate the target pages first: split `pdftotext` output on form feeds, find
   which page a section landed on, then render ONLY those pages — pagination
   shifts whenever rows or paragraphs are added, so page numbers from a
   previous build are stale.
   Vision models over-report faint color on bullet glyphs and misread table
   borders/shading (a bordered shaded table can read as "borderless"), and at
   low dpi they also claim right-aligned number columns are left-aligned and
   call bold headers unbolded — settle table-format questions with an XML dump
   of `tblPr`/`tcPr` (borders, w:shd) and run bold / `w:jc` per column via
   python-docx, font-family/size questions with a counter over run `w:rFonts`
   / `w:sz`, and color questions by scanning the XML parts, not the render.
   Fix only defects the file actually contains.
3. **Fields:** `pdftotext` + grep for rendered values (`Page N of M` on every
   page). Field codes alone prove nothing; field results compute at render.
4. **Content asserts** in the generator for every grammar/accuracy fix already
   made, so a rebuild cannot regress them.
5. **Computed-table arithmetic:** parse the numbers back out of the RENDERED
   table text and assert row values sum exactly to the total rows and match the
   model's computed values. A total its rows do not sum to is the first thing a reviewer attacks. A
   table SPLIT across pages with a repeated header reads as a standalone
   shorter table to a vision model — it sums only the visible page's rows and
   reports a false "rows do not sum to total". Count rows and sum across ALL
   pages of extracted text before touching any numbers.
6. **Table-cell content checks match tokens, not phrases.** PDF text extraction
   interleaves table columns across wrapped lines, so a multi-word cell value
   (a signatory's full name) never appears contiguously — a full-phrase grep
   reports a false miss. Assert individual tokens per cell. The same wrap
   breaks short strings across extracted lines ("58,600 one-time" split at a
   line end), so collapse ALL whitespace to single spaces before any substring
   assert on extracted text.
7. **Formatting-only passes are gated on content identity.** Hash the extracted
text before and after a rebuild and assert byte-identical: a
flow/alignment/spacing pass that moves a number is a bug, and the hash is the
only cheap proof. For page-flow audits, split `pdftotext` output on form feeds
and count tokens per page — flag blank/sparse pages, pages ending on a
heading, and a table whose lead-in paragraph sits on the previous page.
`pdftoppm` pads output page numbers to the page-count digit width
(`qa5-05.png`, not `qa5-5.png`): a stale-name miss is your naming, not a
failed render.
