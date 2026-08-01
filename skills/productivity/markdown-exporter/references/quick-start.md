# Markdown Exporter — Quick-Start Reference

## One-liner Export Patterns

```bash
# Report formats
markdown-exporter md_to_docx report.md report.docx
markdown-exporter md_to_pdf  report.md report.pdf
markdown-exporter md_to_html report.md report.html

# Table data
markdown-exporter md_to_xlsx table.md table.xlsx
markdown-exporter md_to_csv  table.md table.csv
markdown-exporter md_to_json table.md table.json --style json_array

# Presentations (Pandoc slide syntax)
markdown-exporter md_to_pptx slides.md slides.pptx

# Notebooks
markdown-exporter md_to_ipynb notebook.md notebook.ipynb

# Code extraction
markdown-exporter md_to_codeblock tutorial.md extracted/          # individual files
markdown-exporter md_to_codeblock tutorial.md extracted.zip --compress  # single ZIP

# Corpora / structured data
markdown-exporter md_to_xml   data.md data.xml
markdown-exporter md_to_latex data.md data.tex
```

## With Custom Templates
```bash
markdown-exporter md_to_docx report.md branded.docx --template company-template.docx
markdown-exporter md_to_pptx slides.md branded.pptx --template company-theme.pptx
```

## Common Workflow: Markdown → PDF for sharing
```bash
# 1. Write content.md with proper markdown
# 2. Convert
markdown-exporter md_to_pdf content.md content.pdf
# 3. Share or email content.pdf
```

## Common Workflow: Extract code blocks from a tutorial
```bash
markdown-exporter md_to_codeblock tutorial.md code/ --compress
# Output: code/ (directory) or code.zip (if --compress)
```
