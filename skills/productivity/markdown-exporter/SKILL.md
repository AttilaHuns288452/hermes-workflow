---
name: markdown-exporter
description: Convert Markdown text to professional document formats (DOCX, PPTX, XLSX, PDF, HTML, CSV, JSON, XML, LaTeX, IPYNB, code files). CLI tool by bowenliang123.
platforms: [windows, macos, linux]
related_skills: [beautiful-article]
triggers:
  - convert markdown to docx
  - convert markdown to pptx
  - convert markdown to xlsx
  - convert markdown to pdf
  - convert markdown to html
  - convert markdown to csv
  - convert markdown to json
  - convert markdown to xml
  - convert markdown to latex
  - convert markdown to ipynb
  - extract code blocks from markdown
  - export markdown table
  - generate document from markdown
  - export report
  - markdown exporter
---

# Markdown Exporter

Turn Markdown text into professional documents — Word, PowerPoint, Excel, PDF, HTML, CSV, JSON, XML, LaTeX, Jupyter Notebooks, and code files.

**GitHub:** [bowenliang123/markdown-exporter](https://github.com/bowenliang123/markdown-exporter)
**PyPI:** `md-exporter`
**License:** Apache 2.0

## Installation

```bash
# With uv (preferred)
uv tool install md-exporter

# With pip
pip install md-exporter
```

## Available Tools

| Tool | Input | Output | 
|------|-------|--------|
| `md_to_docx` | Markdown text | Word document (.docx) |
| `md_to_html` | Markdown text | HTML file (.html) |
| `md_to_html_text` | Markdown text | HTML text string |
| `md_to_pdf` | Markdown text | PDF file (.pdf) |
| `md_to_md` | Markdown text | Markdown file (.md) |
| `md_to_ipynb` | Markdown text | Jupyter Notebook (.ipynb) |
| `md_to_pptx` | Markdown slides | PowerPoint (.pptx) |
| `md_to_xlsx` | Markdown tables | Excel spreadsheet (.xlsx) |
| `md_to_csv` | Markdown tables | CSV file (.csv) |
| `md_to_json` | Markdown tables | JSON/JSONL file (.json) |
| `md_to_xml` | Markdown text | XML file (.xml) |
| `md_to_latex` | Markdown text | LaTeX file (.tex) |
| `md_to_codeblock` | Code blocks | Code files by language (.py, .js, etc.) |

## Usage

```bash
# Convert markdown file to DOCX
markdown-exporter md_to_docx input.md output.docx

# Convert to PDF
markdown-exporter md_to_pdf input.md output.pdf

# Convert table markdown to Excel
markdown-exporter md_to_xlsx input.md output.xlsx

# Convert markdown slides to PowerPoint (Pandoc slide syntax)
markdown-exporter md_to_pptx input.md output.pptx

# Extract code blocks to individual files
markdown-exporter md_to_codeblock input.md output_dir/

# Extract code blocks as ZIP
markdown-exporter md_to_codeblock input.md output.zip --compress

# Custom DOCX/PPTX templates
markdown-exporter md_to_docx input.md output.docx --template custom.docx
```

### PPTX Slide Syntax

PPTX conversion uses [Pandoc slide shows](https://pandoc.org/MANUAL.html#slide-shows) syntax:
- `---` separates slides
- `:::` for column layouts (::::: columns / ::: column / ::)
- `::: incremental` for incremental lists
- `{background-image="url"}` for background images
- `::: notes` for speaker notes

### JSON Output Styles

- `jsonl` (default) — one JSON object per line
- `json_array` — all objects in a single array

```bash
markdown-exporter md_to_json input.md output.json --style json_array
```

## Templates

Custom DOCX and PPTX templates are supported:
- **DOCX:** Use any `.docx` file with custom heading/paragraph/table styles as template
  - [Default DOCX template](https://github.com/bowenliang123/markdown-exporter/blob/main/md_exporter/assets/template/docx_template.docx)
  - [Customize styles in Word](https://support.microsoft.com/en-us/office/customize-or-create-new-styles-d38d6e47-f6fc-48eb-a607-1eb120dec563)
- **PPTX:** Use any `.pptx` file with custom slide masters as template
  - [Default PPTX template](https://github.com/bowenliang123/markdown-exporter/blob/main/md_exporter/assets/template/pptx_template.pptx)
  - [Customize slide masters](https://support.microsoft.com/en-us/office/customize-a-slide-master-036d317b-3251-4237-8ddc-22f4668e2b56)

## Common Workflows

### Export a report to multiple formats
```bash
# Write your report in markdown, then batch export
markdown-exporter md_to_docx report.md report.docx
markdown-exporter md_to_pdf report.md report.pdf
markdown-exporter md_to_html report.md report.html
```

### Table to spreadsheet
```markdown
| Name    | Age | City        |
|---------|-----|-------------|
| Alice   | 30  | New York    |
| Bob     | 25  | London      |
```
```bash
markdown-exporter md_to_xlsx table.md table.xlsx
markdown-exporter md_to_csv table.md table.csv
```

### Extract code from tutorial markdown
```bash
markdown-exporter md_to_codeblock tutorial.md extracted/ --compress
# Produces extracted.zip with all code files
```

## Notes
- All conversion happens **locally** — no data leaves your machine
- Heavy dependencies on first call (pandoc, pymupdf) — first run may be slow
- The `md_to_png` tool is removed in v3.6.8+
- The `md_to_mermaid` tool is removed in v3.3.0 (required Node.js)
