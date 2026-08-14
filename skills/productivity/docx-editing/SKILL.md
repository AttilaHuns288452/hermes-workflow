---
name: docx-editing
description: Edit .docx files in place with python-docx preserving formatting — structure dump, paragraph/table replacement, TOC field fixes, verification. Use when the user asks to modify text/structure of an existing Word document (proposals, reports, papers) rather than regenerate it.
---

# Docx Editing (python-docx, in-place)

## When to use
User says "modify the text on my proposal/document" and points at an existing .docx. Read it first with `read_file` (auto-extracts). Then edit **in place** with python-docx — a from-scratch rebuild loses styles, tables, and page structure. Save as a new version or overwrite with a `.bak` copy first.

## Setup — Windows + Hermes venv pitfall
python-docx is not installed in the session venv, and the hermes venv's lxml **shadows** uv's isolated env, breaking python-docx's import (`ImportError: cannot import name 'etree' from 'lxml'`). The fix is clearing PYTHONPATH so uv's env wins:

```bash
PYTHONPATH= uv run --with python-docx python script.py
```

## Workflow
1. `read_file` the .docx to see the full text (what the user sees).
2. Dump structure first — `scripts/dump_docx.py`: every non-empty paragraph (index, style, preview) + every table row/col. Anchor edits by **unique substrings**, never paragraph indices (indices shift after inserts/deletes).
3. Copy to `.bak` before overwriting (`shutil.copy2`).
4. Apply edits with the helpers in `scripts/edit_docx.py`:
   - **Whole-paragraph replace**: `set_para_text(p, text)` — keeps paragraph style, copies first run's rPr (font) to new runs, splits `\n` into real line breaks (`w:br`). Critical for ASCII diagrams and multi-line blocks.
   - **Delete**: `p._element.getparent().remove(p._element)`.
   - **Table cell**: clear runs of first paragraph, add one run, drop extra paragraphs (`set_cell`).
   - **Insert table row mid-table**: `deepcopy` an existing row's `_tr`, `addprevious`, then fill cells via the table API.
   - **TOC / field cached text**: python-docx's `doc.paragraphs` may not see TOC entries (fields/textboxes). Fix at XML level: `for t in doc.element.iter(qn('w:t')): t.text = t.text.replace(old, new)`.
   - **Fragment replace** only works if the fragment sits in a single run; otherwise rewrite the whole paragraph.
5. **Verify**: re-extract all text (paragraphs + every table cell) and grep for stale terms — old module names, removed features, renamed sections. Intentional mentions in "what was removed" phrasing are OK; everything else is a leftover.

## Pitfalls
- `read_file` extraction renders em dashes / curly quotes as spaces or mojibake — **never match on long original strings containing them**. Match short ASCII fragments, then replace the whole paragraph with clean new text.
- Diagrams/pasted sections are often ONE paragraph with `w:br` line breaks, not many paragraphs — handle with `\n`-splitting, don't assume paragraph boundaries.
- List numbering may be literal text ("Module 1 — …") or auto (`numPr`). Renumber via text only when literal; text replacement preserves auto numbering.
- Empty paragraphs are skipped by `.strip()` filters — a "missing" section may live in a textbox/field; the XML `w:t` pass covers those.
- Recompute totals when editing cost/quantity tables — verify the arithmetic by hand.
- Long documents: batch replacements as a list of `(unique_substring, new_text)` pairs; log a WARN for any substring with 0 or 2+ matches instead of silently skipping.

## Filling template .docx files (Google Docs templates, forms with placeholders)

Template-fill jobs (professor/agency templates with `[Insert X]` placeholders + "Example:" scaffolding) have their own recipe:

1. **Download public Google Docs without auth**: `curl -L "https://docs.google.com/document/d/<ID>/export?format=docx" -o template.docx`. If the doc was viewable in a browser (or its content was attached), the export URL works with no credentials — skip OAuth entirely.
2. Dump the template with `scripts/dump_docx.py` first. Note the header block may already be filled by the user (project name, prepared-by, date) — do NOT touch those.
3. Replace `[Insert ...]` cells and rewrite "Example:" paragraphs; **delete the template instruction lines** ("Provide a brief overview…", "Clearly define…") — a submitted doc carries no scaffolding. Leave genuinely unknown placeholders (decision-maker names, titles) untouched per user instruction.
4. Verify: re-extract text and assert (a) every `[Insert` is gone EXCEPT the intentionally-kept ones, (b) no "Example:" remains, (c) totals recomputed correctly.

### Pitfalls specific to template filling
- **"Example:" and the example text are often ONE paragraph** with `w:br` line breaks ("Example:\nThe purpose of this CBA is to…"). Exact-match on paragraph text fails — match `startswith("Example:")` + a content fragment, then `set_para_text` (which wipes the embedded breaks).
- **Inserting a table shifts `doc.tables` indices** — identify tables by header-row content (`" ".join(c.text for c in t.rows[0].cells)` contains "Estimated Cost"), never by hardcoded index.
- **New paragraphs inherit formatting from their source** — use `doc.add_paragraph(text)` + `ref._p.addnext(new._p)` for body text; deepcopying the title paragraph for a caption inherits the title font. For bullets, deepcopy an existing bullet paragraph and clear its runs (keeps List Bullet style).
- **Cell text write loses nothing but kills mixed formatting** — `cell.paragraphs[0]` first run keeps its rPr; acceptable for fill-in cells.
- **Values that display masked in read_file/grep may be real in the file** (secret-shaped strings get masked in tool output) — when round-tripping values read from config/docs, read via a parser instead of trusting displayed output.
- **Bracket fragments hijack containment matching.** Matching paragraphs with `fragment in text` using refs like `"[6]"` will also match paragraphs containing `"[6]–[11]"` or `"[6][7][10]"` ranges — a refs-rewrite pass can silently overwrite the assumptions/benefit-note paragraphs that cite those ranges. For numbered reference lists, anchor structurally: find the "References" heading, take the next N non-empty paragraphs by position. Restore any earlier-replaced text AFTER the refs pass if it contains bracket fragments.
- **Bullets are 2-run paragraphs** (bold label run + normal rest run). Rewrite as `runs[0].text = label; runs[1].text = rest; clear runs[2:]` — clearing `runs[1:]` and conditionally re-adding only when `len(runs)==1` silently deletes the rest of the sentence.
- **Multi-run paragraphs duplicate on partial edits.** `p.runs[0].text = x` alone leaves runs[1:] intact. Template header blocks are often ONE paragraph with 6+ runs carrying `w:br` breaks ("Project Name:…\nPrepared By:…"). Editing only run0 produces "Prepared By: Software BuildersDental Practice Management System" and double dates. Always use the full `set_text` (runs[0] = whole text, clear the rest), and rebuild multi-line headers as separate paragraphs (deepcopy + `addnext` + clear residual runs, then delete the leftover paragraph).
- **User style for academic deliverables (Attila)**: no em dashes (rewrite " — " as ", " or split sentences), black text only (Google Docs templates mark example text red `FF0000`; replaced text INHERITS it — run the polish pass), and references in **APA 7** format with researched authors/dates (extract PMC/journal pages for full citation data; blogs: org or named author + date, `(n.d.)` when undated). Convert bracketed `[1]` markers to in-text **(Author, Year)** citations at each cited claim so readers don't have to jump to the list; keep the numbered list as the map. Recipe: `references/polish-pass.md`.

## Render, look, fix (docx → PDF → vision QA loop)
When the user asks to "improve readability" of a filled document, don't guess from text extraction — render and LOOK:
1. Export to PDF via Word COM (see `references/word-com-pdf-render.md` — `New-Object -ComObject Word.Application` fails with `TYPE_E_CANTLOADLIBRARY` on this box; attach to the already-running Word instance with `GetActiveObject` instead).
2. `pip install pymupdf`, render pages to PNG (`page.get_pixmap(dpi=130)`), then `vision_analyze` each page asking for readability problems by location. Vision catches what extraction can't: duplicated header lines, tables cut at page breaks, orphaned reference lines, wall-of-text paragraphs.
3. Fix → re-render → re-check with vision. Typical fixes the loop drives:
   - Wall-of-text paragraphs (exec summary, assumptions) → split into 2-3 short paragraphs; assumptions become a bold intro line + bullet list with bold labels.
   - Tables cut across pages: `cantSplit` on every row stops mid-row splits, but the header row can still orphan at a page bottom; Word **ignores `keepNext` on table rows** → `page_break_before` on the section heading is the reliable fix. Add `tblHeader` to row 0 so a split table repeats its header.
   - Orphaned last reference line alone on the final page → reclaim vertical space (refs `space_after` 1-2pt, font 10.5, line spacing 1.0; slim approval-table cell margins via `tblCellMar`).
   - Blank trailing page → delete trailing empty paragraphs (stop if the last one carries `w:sectPr`).
   - Cramped tables → `table.autofit=False` + per-row `cell.width` (usable width ≈ page − margins), cell padding via `w:tblCellMar` (top/bottom 40-60 twips, left/right 108).
   - Unit-period confusion: monthly math in a description next to an annual value reads as an error — spell out the full equation ("8.8 visits/month x Php1,000 x 12 months = Php105,600 per year").

## Support files
- `scripts/dump_docx.py` — structure dump: paragraphs (index/style/preview) + all tables.
- `scripts/edit_docx.py` — proven helpers: `set_para_text`, `delete_para`, `set_cell`, `insert_row_before`, XML `w:t` replace.
- `references/polish-pass.md` — readability/red-font/APA polish pass recipe.
- `references/word-com-pdf-render.md` — Word COM PDF export (GetActiveObject), PyMuPDF page rendering, vision QA loop, page-layout fixes.
- Working example: `C:\Users\YOUR_USERNAME\AppData\Local\hermes\scripts\fill_cba_template.py` (fills a Google Docs CBA template — download → fill → verify pattern).
