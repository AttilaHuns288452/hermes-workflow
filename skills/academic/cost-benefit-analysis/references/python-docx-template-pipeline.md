# python-docx template fill + vision QA pipeline

Session-proven recipe for filling a Google Docs template (.docx export) in place, preserving
the template's formatting, fonts, and divider images, then QA-ing the result with vision models.
All code runs with SYSTEM Python (`C:/Users/YOUR_USERNAME/AppData/Local/Programs/Python/Python311/python.exe`
— has pip; the Hermes venv python does not). `python-docx` and `pymupdf` must be installed there.

## 1. Get the template
Public Google Doc export works WITHOUT auth:
`https://docs.google.com/document/d/<DOC_ID>/export?format=docx` (curl or web_extract download).
Templates from this user often come PRE-FILLED with header block (project name, "Prepared By",
date) — read the download before writing anything.

## 2. Fill in place (never re-export from markdown)
markdown-exporter output loses the template's layout/dividers. Instead edit the .docx with
python-docx, keeping the XML structure. Build the fill as a re-runnable script; make inserts
IDEMPOTENT or never run the script twice (it duplicates bullets/refs).

### Core helpers (session-verified)
```python
def set_text(p, text):            # REPLACES whole paragraph safely
    if p.runs:
        p.runs[0].text = text
        for r in p.runs[1:]: r.text = ""   # ← clearing runs[1:] is mandatory
    else: p.add_run(text)

def set_bullet(p, bold_part, rest):   # keep run structure: run0=bold label, run1=rest
    if len(p.runs) >= 2:
        p.runs[0].text = bold_part; p.runs[1].text = rest
        for r in p.runs[2:]: r.text = ""
    elif len(p.runs) == 1: p.runs[0].text = bold_part; p.add_run(rest)
    else: p.add_run(bold_part); p.add_run(rest)

def find_table(fragment):         # tables by HEADER TEXT, never by index (inserts shift indices)
    for t in doc.tables:
        if fragment in " ".join(c.text for c in t.rows[0].cells): return t

def insert_after(p, text):        # new paragraph after an existing one (deepcopy keeps style)
    import copy
    from docx.text.paragraph import Paragraph
    np = copy.deepcopy(p._p); p._p.addnext(np)
    return Paragraph(np, p._parent)
```

### Pitfalls that actually bit
- **Multi-run paragraphs**: template header lines contain soft line breaks split across 4-6 runs.
  Editing only `runs[0].text` leaves the rest → duplicated text ("Software BuildersDental...",
  double dates). Always use set_text (clears runs[1:]).
- **Red text**: Google Docs templates color example/placeholder text red; replaced text INHERITS
  it. After filling, force `r.font.color.rgb = RGBColor(0,0,0)` on every run (or document-wide pass).
- **Containment matching with bracketed refs**: matching paragraphs by substring "[6]" also hits
  paragraphs containing "[6]–[11]" or "[6][7][10]" — replacing the wrong paragraph and destroying
  content. Match refs by POSITION (the 11 paragraphs after the "References" heading), never by
  "[n]" substring; restore bracketed in-text paragraphs AFTER the refs pass.
- **Bullet markers vanish**: rewrites that replace run0 with the label text drop the "•" prefix —
  re-add "• " when rewriting bullets, or preserve run0 as-is.
- **Non-idempotent scripts**: an insert script run twice duplicates every inserted paragraph/ref.
  Delete intermediates before a rebuild, or structure scripts as idempotent replacements.
- **Split paragraphs defeat match-and-replace**: after a paragraph was split into several (exec
  summary P1/P2/P3), substring matching updates only the fragment containing the anchor text —
  old numbers survive in siblings. Fix each fragment, then sweep for OLD values ("Php71,400" not
  in full doc text), not just the new value present.
- **Citation/reference drift**: a later script rewriting a bullet can silently drop an in-text
  citation (reference stays in the list, uncited → APA violation) or leave ";" before ")"
  ("(A, 2021; B, n.d.;)"). After any citation edit, verify every ref entry appears in-text and
  no malformed multi-source parens remain.

## 3. Render for vision QA (user explicitly wants this step)
1. Export docx → PDF via Word COM:
   - **Word already running**: attach with GetActiveObject (never create a new instance — the
     `.Visible` setter throws TYPE_E_CANTLOADLIBRARY 0x80029C4A, and SaveAs2 silently no-ops).
   - **Word fully closed**: GetActiveObject fails (MK_E_UNAVAILABLE) AND `New-Object -ComObject
     Word.Application` fails at `.Visible`. Working sequence: `Start-Process winword`, sleep ~8s,
     then GetActiveObject → export → `$w.Quit()` (you started it, so quitting is fine).
   ```bash
   powershell.exe -NoProfile -Command 'try { $w = [System.Runtime.InteropServices.Marshal]::GetActiveObject("Word.Application"); $d = $w.Documents.Open("PATH.docx", $false, $true); $d.ExportAsFixedFormat("PATH.pdf", 17); $d.Close($false); Write-Output "EXPORT_OK" } catch { Write-Output ("ERR: " + $_.Exception.Message) }'
   ```
   (17 = wdExportFormatPDF; open read-only so the user's open copy is untouched; NEVER $w.Quit() a
   borrowed instance.) Export fails silently with SaveAs2 — use ExportAsFixedFormat.
2. `pip install pymupdf` (system python), then render pages: `page.get_pixmap(dpi=130).save(...)`.
3. `vision_analyze` each page: "Describe readability problems: paragraph lengths, spacing,
   alignment, table readability, text density, awkward gaps. Be specific about location."
4. Fix → re-render → re-check. Repeat until clean.

### Findings vision models reliably catch (checklist)
- Header duplication from multi-run edits; redundant dates.
- Wall-of-text paragraphs (exec summary, assumptions) → split into short paragraphs or bullets.
- Monthly math shown next to annual totals → spell out "x 12 months = ₱… per year".
- Table cut off at page break (header row alone at page bottom) → `page_break_before` on the
  section heading; `w:cantSplit`/`w:keepNext` on table ROWS is NOT reliable in Word. BUT
  `keep_with_next` on PARAGRAPHS works: References heading + refs [1]–[10] kept the whole list
  together on the last page (block the chain, not the last item).
- Orphaned reference line on its own last page → tighten: refs space_after 1-3pt, size 10-10.5,
  heading space_before, approval-table cell margins via `w:tblCellMar` (twips).
- Blank trailing page → remove trailing empty paragraphs (skip the one whose pPr carries w:sectPr).
- Double bullet markers ("• -") from template hyphens — strip template's "- " prefix.
- Table columns cramped → set per-cell widths + `table.autofit = False` (python-docx needs
  per-cell width, not just column width).

## 4. Windows case-insensitive filesystem trap (caused data loss TWICE)
NTFS + git-bash globbing is case-INsensitive: `rm -f Cost-Benefit-Analysis-Final.docx` deletes a
file literally named `Cost-Benefit-Analysis-FINAL.docx`, and `cp x FINAL.docx` silently
OVERWRITES an existing `Final.docx`. Rules:
- Never glob or exact-match a name whose case differs from a sibling you must keep.
- Keep intermediates in a `build/` subfolder; only the final file lives in the main folder.
- After any cleanup: `ls` and confirm the deliverable still exists.
- Rename across case on Windows: `mv Final.docx tmp && mv tmp FINAL.docx` (two-step).

## 5. User edits in Word are live data
The user fills approval tables, names, and dates in Word between sessions — the docx on disk is
the live artifact. Edit it IN PLACE; never rebuild the chain from an earlier version once the
user has touched the file (regenerating loses their edits; the current file is the only source
of truth). When `doc.save()` raises PermissionError the file is open in their Word:
save to a temp name, verify the temp, then two-step `mv` when the lock clears (Word closing is
detectable by the mv succeeding). Their Word re-save may bloat the file (190KB → 2MB) — harmless.

## 6. "The numbers are not updated" — stale-view diagnostic
When the user reports old numbers but the file verifies clean (run the arithmetic assertions,
assert OLD values absent), the file is NOT stale — their VIEW is. Prime suspects:
- The Google Docs original (never edited — still the blank template; the filled version exists
  only in the downloaded docx). Upload `*-FINAL.docx` back to Drive to update it.
- A PDF/docx tab in a viewer opened before the last export — close and reopen.
Diagnose with evidence (16 arithmetic checks), point at the exact path, don't re-edit blindly.

## 7. This user's document style preferences (Attila)
- NO em dashes — replace with commas/words; en dashes in numeric ranges are fine.
- In-text APA citations (Author, Year) at every sourced claim; keep the full APA list at the end.
- Assumptions as a bold intro + bulleted list with bold labels, not a run-on paragraph.
- No red/colored text; placeholders stay placeholders; ₱ currency throughout.
