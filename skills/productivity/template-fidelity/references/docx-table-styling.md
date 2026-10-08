# Docx table styling choke point

One pass at the END of the build (`doc.tables`) enforces the "Uniform
generated tables" rules. Run AFTER all content is in the document.

```python
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import re

CELL_PAD = 115          # twips; uniform cell margins
HEADER_FILL = "DDEBF7"  # light blue; uniform header shading
BODY_PT = 10
MONEY_NUM = re.compile(r"^(Php[\d,.]+%?|\d[\d,.]*%?)$")

def normalize_tables(doc, header_fill=HEADER_FILL, font_pt=BODY_PT, cell_pad=CELL_PAD):
    for t in doc.tables:
        tblPr = t._tbl.tblPr
        # 1. uniform borders (add missing pieces, force consistent values)
        borders = tblPr.find(qn("w:tblBorders"))
        if borders is None:
            borders = OxmlElement("w:tblBorders"); tblPr.append(borders)
        for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
            el = borders.find(qn(f"w:{edge}"))
            if el is None:
                el = OxmlElement(f"w:{edge}"); borders.append(el)
            el.set(qn("w:val"), "single"); el.set(qn("w:sz"), "4")
            el.set(qn("w:color"), "808080")
        # 2. uniform cell margins
        mar = tblPr.find(qn("w:tblCellMar"))
        if mar is None:
            mar = OxmlElement("w:tblCellMar"); tblPr.append(mar)
        for side in ("top", "bottom", "left", "right"):
            el = mar.find(qn(f"w:{side}"))
            if el is None:
                el = OxmlElement(f"w:{side}"); mar.append(el)
            el.set(qn("w:w"), str(cell_pad)); el.set(qn("w:type"), "dxa")
        # 3. header shading on row 0 of EVERY table
        for c in t.rows[0].cells:
            tcPr = c._tc.get_or_add_tcPr()
            shd = tcPr.find(qn("w:shd"))
            if shd is None:
                shd = OxmlElement("w:shd"); tcPr.append(shd)
            shd.set(qn("w:val"), "clear"); shd.set(qn("w:fill"), header_fill)
        # 4. uniform font size, no stray italics (do NOT touch bold here)
        for r in t.rows:
            for c in r.cells:
                for p in c.paragraphs:
                    for run in p.runs:
                        run.font.size = Pt(font_pt)
                        run.font.italic = False
        # 5. numeric/money columns right-aligned (data-driven per column)
        ncols = len(t.rows[0].cells)
        for ci in range(ncols):
            vals = [t.rows[ri].cells[ci].text.strip() for ri in range(1, len(t.rows))]
            if vals and all(MONEY_NUM.match(v) for v in vals):
                for ri in range(len(t.rows)):
                    for p in t.rows[ri].cells[ci].paragraphs:
                        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
```

Column widths (per table; use its own width list summing to the usable page
width). Set BOTH the `w:tblGrid` gridCol values and every cell's `tcW` —
LibreOffice honors the grid, Word the cells:

```python
def set_widths(t, widths):  # widths: [Inches(...), ...]
    grid = t._tbl.find(qn("w:tblGrid"))
    for gc, w in zip(grid.findall(qn("w:gridCol")), widths):
        gc.set(qn("w:w"), str(int(w.twips)))
    for r in t.rows:
        for c, w in zip(r.cells, widths):
            c.width = w
```

Notes:

- Widths: leave enough for numeric column HEADERS to wrap between words
  ("Estimated\nHours" ok, "Estimat-ed" not). Widen the numeric column, shrink
  the description column, keep the sum constant.
- Bold: enforce header-bold/body-plain at the cell-fill helpers. Never
  mass-override bold in this pass on template-derived content (destroys run
  signatures the fidelity diff checks).
- Verify formatting claims from XML (`tblPr` borders, `tcPr/w:shd`), not from
  vision renders; verify numeric alignment the same way or via a fresh render.
- Tables that split across pages: mark row 0 `w:tblHeader` (header repeats);
  sum arithmetic across ALL pages of extracted text before trusting any
  "does not sum" complaint from a vision pass.
