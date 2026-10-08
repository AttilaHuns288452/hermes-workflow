# Generator-built docx: edit and verification mechanics

## Edit discipline
- Patch the generator script and rebuild. Never hand-edit the .docx artifact — the next build silently reverts it.
- Generator edits through a REPL/call are invisible to `read_file` views of the same file taken earlier in the session. Anchor on current source with `find`/regex first, then `assert anchor in src` for every replacement pair, and write only after all asserts pass.
- One shared `detail_text()`/helper keeps repeated values consistent across tables and prose (e.g. itemized rows and their total). Route duplicates through it.

## Text extraction pitfalls (python-docx + pdftotext)
- `p.text` excludes runs inside `w:hyperlink` elements — hyperlink URLs are invisible to paragraph-level reads AND unfixable there. Scan the full XML (`for t in p._p.iter(qn('w:t'))`) for detection, and fix by removing the extra hyperlink child; `p.text = x` leaves the old hyperlink in place.
- `find_par`-style helpers that raise on missing paragraphs hide which lookup failed — make them log-and-return-None (or assert with the anchor string in the message) so the error names the anchor.
- `pdftotext -layout` interleaves table columns at line breaks. Verify table content with whitespace-flattened text + row-anchored regex ("label.*?value" with `\s+`), never literal multi-line substrings.
- Multiplication signs and quotes: generator writes "×" but checks may type "x"; curly quotes vs straight. Normalize (NFKD + char map) before comparing.
- PDF hyphenation splits words across lines ("below-\nmarket") — use `word-\s?word` patterns in extraction checks.
- Rendering is engine- and machine-dependent (LibreOffice/Word version, fonts change pagination). Render the PDF on the machine that ships it; gate checks on text presence, not page numbers.

## Numeric verification
- Recompute headline metrics in Python Decimal from the stated inputs; assert the document's printed strings match (rounded as printed).
- Check both sums: rounded-row sum and unrounded-component total. A rounding-convention footnote ("figures in whole pesos") explains small deltas — a real delta is ground 4.
- Currency formatting in docx tables: build strings via a single format helper so thousands separators and "Php" prefix never drift between rows and prose.

## Ship gate
1. Build succeeds with generator self-checks (all asserts pass).
2. String gates on whitespace-flattened extracted text: old strings gone, new strings present.
3. Recompute matches printed values.
4. Vision QA only the changed pages (render at ~110 dpi per page).
5. Copy the artifact to BOTH `~/Downloads` and the repo/project root; commit generator + artifacts together (plus render/ extracts if the project keeps them).
