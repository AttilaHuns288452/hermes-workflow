# Pandoc reference-docx pipeline

Recipe for authoring a long analytical deliverable in markdown and rendering it as a
DOCX that matches a user-supplied reference document's formatting identity. Procedure
overview and pitfalls live in SKILL.md ("Authoring a NEW deliverable to match a
reference document's look"). The blank-template fill route is a different workflow
(see SKILL.md "Procedure"); use this route when the deliverable is generated from
markdown and the reference supplies LOOK only.

## 1. Fingerprint the reference

```bash
soffice --headless --convert-to pdf --outdir ref_render/ "Reference.docx"
pdftoppm -png -r 85 ref_render/Reference.pdf ref_render/page   # vision: style character
```

XML facts to collect (python-docx / lxml on the reference package):

- `word/styles.xml`: Heading 1/2/3 + Title + Normal — font (`w:rFonts w:ascii`), size
  (`w:sz`, half-points), bold, `w:color`, spacing (`w:spacing` before/after, line).
- `word/document.xml` sectPr: `w:pgSz` (twips) + `w:pgMar` (1440 twips = 1 inch).
- footer XML: field codes (PAGE vs PAGE+NUMPAGES), `w:jc` alignment, run size.
- tables: tblBorders color, header row `w:shd` fill, label-column run bold, per-column
  `w:jc` on body cells, `w:tblLayout` (fixed vs autofit), `w:tblGrid` widths.
- reference list: hanging indent (`w:ind w:hanging`), URL run styling (color/underline).

Record as a small identity dict; later asserts compare generated output against it.

## 2. Build the pandoc reference doc

```bash
pandoc -o ref.docx --print-default-data-file reference.docx > ref.docx   # pandoc 3.x
```

Edit `ref.docx` with python-docx: apply the identity to the styles AND to
docDefaults/theme fonts (pandoc emits run-level `w:rFonts` that beat style fonts
otherwise), heading colors/spacing/alignment, Normal font/alignment, sectPr margins,
footer with PAGE/NUMPAGES `w:fldSimple` (put an `rPr` INSIDE the field's run or the
number renders at default size while surrounding text is small).

## 3. Generate

```bash
uv run --with pypandoc-binary python - <<'PY'
import pypandoc
pypandoc.convert_file('input.md', 'docx', outputfile='out.docx',
                      extra_args=['--reference-doc=ref.docx', '--standalone'])
PY
```

Generate WITHOUT `--toc` when a static page-numbered TOC is required. Pandoc caption
syntax: `Table: Title` as its own paragraph immediately before the pipe table (blank
line above the caption line, no `---` rule between caption and table).

## 4. Post-process (python-docx), in this order

1. Content-level fixes (label splits, table structure corrections).
2. ONE normalization pass: run-level `w:rFonts` sweep
   (`doc.element.body.iter(qn('w:r'))`), heading alignment left, table grid widths +
   header fills + label-column bold + data-driven numeric right-align.
3. Pagination-sensitive inserts: title page at document start + explicit page break;
   static TOC placeholder paragraphs (entry text + right tab stop + placeholder number).
4. Caption injection: walk table blocks by content with a moving cursor (stored line
   indices desync whenever an earlier pass changes line counts), insert numbered caption
   paragraphs in the reference's caption format.
5. Footer fields; save.

## 5. Two-pass pagination for the TOC

```bash
soffice --headless --convert-to pdf --outdir out/ out.docx
pdftotext -layout out/out.pdf out/out.txt   # split on '\f' for per-page text
```

Locate each heading's page by normalized matching (collapse whitespace, unify
curly/straight quotes and hyphen variants), searching PAST the TOC pages (TOC entries
shadow body matches, and headings may wrap or split across a page boundary — match
substrings, not whole lines). Patch literal page numbers into the TOC paragraphs, save,
re-render, re-run the map, and assert the map is unchanged. If pagination moved, repeat
once; it converges as long as the entry count (and thus TOC page count) is stable.

## 6. Verification chain

- Structural asserts on the docx: page-count floor, caption count vs table count,
  PAGE fields in every section footer, no pandoc TOC field leftovers, all citation/ID
  tokens resolvable.
- Extracted-text asserts (pdftotext): every key figure present, stale figures absent,
  TOC printed numbers == final page map.
- Vision on key pages vs the reference's rendered pages (title, TOC, longest table,
  heading-heavy page).
- XML ground truth whenever vision disagrees: fonts = count `w:rFonts` at run vs style
  level; alignment = `w:jc`; colors = scan `w:color` inside run rPr only; numeric
  alignment = per-column `w:jc` on body cells.
