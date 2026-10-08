# Docx Run-Level Formatting Preservation

Depth for template-filling step 2/4 with python-docx. The `docx` skill's
scripts do not expose run-level formatting — use a small python-docx
snippet for the dump and for verification.

## Formatting dump (the contract)

Collect for every paragraph: style name, `space_before`, `space_after`;
for every run: text, `bold`, `font.name`, `font.size.pt`, explicit
`font.color.rgb`. Normalize every field to `str(...)` in the comparison
tuples — mixed None/bool values break set sorting otherwise.

## Generation pattern

- Open the template with `Document(template_path)`, delete each
  `paragraph._p` from `element.body` (keep `sectPr`), then add fresh
  paragraphs with the dump's style and spacing and runs with explicit
  font name / bold / size / color.
- Group content lines into builder helpers per template flavor (title,
  label+value field, heading with two-color parts, checklist line,
  task line) so run splits stay consistent across the document.
- Only set `r.bold` when the dump says bold=True. Template body runs
  carry bold=None (inherit); writing explicit False produces a foreign
  run signature and can override style-level bold.
- Match run boundaries exactly: if the template has punctuation in its
  own run after a content run, split your strings the same way.
- Watch for runs with explicit values the style already implies (title
  run with explicit black color, mixed 10/11pt sizes). Where the
  template is internally inconsistent, follow its dominant pattern.

## Verification snippet shape

Run-format signature = the set of tuples
`(style, space_before, space_after, bold, font, size, color)` over all
runs. Assert `filled - template == set()`. Also assert page setup equal:
`(page_width, page_height, left_margin, right_margin, top_margin,
bottom_margin)` of `sections[0]`.

## Nested-heredoc escaping

When a verify script is emitted through python-inside-python terminal
calls, `"\n"` inside a string literal is expanded by the OUTER
interpreter and the inner script dies with "unterminated string
literal". Build multi-line text with `chr(10).join(...)` instead.

## Render check

`soffice --headless --convert-to pdf --outdir <dir> <file.docx>` then
`pdftoppm -png -r 60 <pdf> <prefix>`. Vision-check page 1 and one
mid-document page. Low-DPI vision may misread names — trust the text
extraction over OCR when they disagree.
