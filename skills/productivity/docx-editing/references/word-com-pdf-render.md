# Word COM PDF export + page rendering (Windows)

Render a .docx to PDF/PNG for visual QA without LibreOffice. Verified on Attila's PC (Word installed, system Python `C:/Users/YOUR_USERNAME/AppData/Local/Programs/Python/Python311/python.exe`).

## Export docx → PDF via the RUNNING Word instance

`New-Object -ComObject Word.Application` fails here with:
`Unable to cast COM object ... TYPE_E_CANTLOADLIBRARY (0x80029C4A)` (type library load error — happens when Word is already running / registration is broken). The working path attaches to the user's already-running Word:

```bash
powershell.exe -NoProfile -Command 'try { $w = [System.Runtime.InteropServices.Marshal]::GetActiveObject("Word.Application"); $d = $w.Documents.Open("C:\path\in.docx", $false, $true); $d.ExportAsFixedFormat("C:\path\out.pdf", 17); $d.Close($false); Write-Output "EXPORT_OK" } catch { Write-Output ("ERR: " + $_.Exception.Message) }'
```

- `17` = `wdExportFormatPDF`.
- `$false, $true` = ConfirmConversions=false, ReadOnly=true (never touch the user's open doc).
- Open(ReadOnly) is safe even while the doc is open in the user's Word — but if the target file is locked (user has it open), export a different copy.
- **bash quoting**: wrap the whole PowerShell command in SINGLE quotes in bash or `$w`/`$d` get expanded by bash to empty strings (symptom: `ExpectedExpression` parse errors).
- Do NOT call `$w.Quit()` when attached to the user's instance — it would close their Word.
- Alternative if Word is NOT running: `SaveAs2(path, 17)` may work in a fresh instance; if the COM cast error appears, check whether Word is running and use GetActiveObject.

## PDF → PNG pages

```python
import pymupdf  # pip install pymupdf  (import "fitz" is deprecated but still works)
doc = pymupdf.open(r"out.pdf")
for i, page in enumerate(doc):
    page.get_pixmap(dpi=130).save(f"page{i+1}.png")
```

## Vision QA loop

1. `vision_analyze` each PNG: "Describe the readability problems you see: paragraph lengths, spacing, alignment, text density, table readability, awkward gaps. Be specific about location."
2. Fix in python-docx, re-export, re-render, re-check.
3. Also cross-check at text level (`page.get_text()` per page) — vision reliably reports "table cut off" but text-level probes confirm exactly which page each element landed on.

## What vision catches that extraction misses
- Duplicated header lines from partial run edits ("Software BuildersDental Practice Management System", double dates)
- Table header row orphaned at a page bottom (data rows on next page)
- Single orphaned reference line alone on the final page
- Walls of text that should be split/bulleted
- "• -" double markers from template hyphens (note: vision can also HALLUCINATE these — verify at text level with `"\u2022 -" not in text` before fixing)

## Page-layout fixes (python-docx)
- Keep rows from splitting: `w:cantSplit` on each row's trPr; repeat header on split: `w:tblHeader` on row 0.
- Word ignores `w:keepNext` on table rows — to keep a small table whole, use `page_break_before = True` on the section heading paragraph instead.
- Blank trailing page: delete trailing empty paragraphs, but stop if the last one contains `w:sectPr`.
- Column widths: `table.autofit = False` then set `cell.width` on every row; usable width = page width − margins (8.5" − 2×1" = 6.5").
- Cell padding: `w:tblCellMar` on tblPr (top/bottom ~20-60 twips, start/end ~108 twips; dxa units).
