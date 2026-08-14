# Polish pass — readability + template color cleanup (python-docx)

After filling a template docx, users often ask for a "more readable / easy on the eyes" version — and Google Docs templates frequently mark example/placeholder text in **red** (`FF0000`). Your replaced text INHERITS that red because `set_para_text` keeps the first run's rPr. Verified on the CBA template fill (Aug 2026).

## Steps
1. **Kill all explicit run colors**: for every run in paragraphs + table cells, if `r.font.color.rgb is not None` → `r.font.color.rgb = RGBColor(0,0,0)`. Leave inherit alone.
2. **Normalize body font**: Arial 11pt on every run; set `w:ascii`, `w:hAnsi`, `w:cs` on the `w:rFonts` element (`r._element.get_or_add_rPr()`) — name-only assignment is ignored by Word on some runs.
3. **Headings** — regex `^\d+\.\s` (sections) / `^\d+\.\d+\s` (subsections): bold, dark navy `RGBColor(0x1F,0x2A,0x44)`, 13pt sections / 12pt subsections. Title paragraph → 20–22pt bold black.
4. **Table header rows** (row 0 of every table): bold runs + light fill:
   ```python
   from docx.oxml.ns import qn
   from docx.oxml import OxmlElement
   tcPr = cell._tc.get_or_add_tcPr()
   shd = OxmlElement("w:shd")
   shd.set(qn("w:val"), "clear"); shd.set(qn("w:fill"), "D9E2F3")
   tcPr.append(shd)
   ```
5. **Header block** (Project Name / Prepared By / Date lines): leave structure, just normalize to body style + black.

## Pitfalls
- **Locked file**: if the user has the docx open in Word, `doc.save()` raises `PermissionError: [Errno 13]` — save to a NEW filename (e.g. `*-Final.docx`) instead of asking them to close Word.
- **Verify**: re-extract and assert 0 runs with `str(c.rgb) == "FF0000"`; check every heading's runs are bold.
- **Do not deepcopy the title paragraph** for new body/caption paragraphs — the title font bleeds in. Use `doc.add_paragraph()` then move the XML element (`ref._p.addnext(new._p)`).
- `~` in bash + python args on MSYS mangles to `C:\c\Users\...` — pass `C:/Users/...` paths explicitly.
- Plain `python` may resolve to the Hermes venv (no pip). Use `C:/Users/YOUR_USERNAME/AppData/Local/Programs/Python/Python311/python.exe` for pip + python-docx work.

## Working example
`C:\Users\YOUR_USERNAME\AppData\Local\hermes\scripts\polish_cba.py` (full polish pass on the CBA docx: red cleanup → fonts → headings → table shading → verify).
