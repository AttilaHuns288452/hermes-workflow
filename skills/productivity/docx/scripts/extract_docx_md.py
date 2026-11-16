#!/usr/bin/env python3
"""Convert a .docx to markdown: headings, paragraphs, lists, tables.

Fallback for the docx skill when markitdown/pandoc are unavailable and
python-docx is only available ephemerally:
    uv run --with python-docx python3 extract_docx_md.py in.docx out.md

Text-only: images stay in the source docx. Tables become pipe markdown.
Iterates document.element.body so paragraphs and tables keep document order.
"""
import sys
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph

def cell_md(c):
    return " ".join(p.text.strip() for p in c.paragraphs if p.text.strip()).replace("|", "\\|") or " "

def main(path, out):
    doc = Document(path)
    body = doc.element.body
    lines = []
    for child in body.iterchildren():
        tag = child.tag.split('}')[-1]
        if tag == 'p':
            p = Paragraph(child, doc)
            t = p.text.strip()
            if not t:
                continue
            style = (p.style.name or "").lower()
            if style.startswith('heading'):
                try:
                    lvl = int(''.join(ch for ch in style if ch.isdigit()) or 1)
                except ValueError:
                    lvl = 1
                lines.append("#" * min(max(lvl, 1), 6) + " " + t)
            elif style.startswith('list'):
                lines.append("- " + t)
            elif t.startswith(('•', '-', '*')) and len(t) > 1:
                lines.append("- " + t.lstrip("•-* "))
            else:
                lines.append(t)
            lines.append("")
        elif tag == 'tbl':
            tbl = Table(child, doc)
            rows = []
            for r in tbl.rows:
                rows.append([cell_md(c) for c in r.cells])
            if not rows:
                continue
            width = max(len(r) for r in rows)
            rows = [r + [""] * (width - len(r)) for r in rows]
            lines.append("| " + " | ".join(rows[0]) + " |")
            lines.append("|" + "---|" * width)
            for r in rows[1:]:
                lines.append("| " + " | ".join(r) + " |")
            lines.append("")
    text = "\n".join(lines).strip() + "\n"
    with open(out, "w") as f:
        f.write(text)
    print(f"OK {out}: {len(text)} chars, {text.count(chr(10))} lines")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: extract_docx_md.py in.docx out.md")
        sys.exit(2)
    main(sys.argv[1], sys.argv[2])
