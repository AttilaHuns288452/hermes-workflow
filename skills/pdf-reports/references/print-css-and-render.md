# Chrome print mechanics + PDF render/inspect

Concrete mechanics for `pdf-reports`. The print path is a popup window the app
writes its report HTML into, then `window.print()` (Save as PDF). Everything
below is what makes that output professional and verifiable.

## Print CSS that actually holds

```css
@page { size: A4; margin: 12mm 12mm 14mm 12mm; }  /* bottom margin holds the footer */
thead { display: table-header-group; }              /* table headers repeat on every page */
tr    { break-inside: avoid; }
.section { break-inside: avoid; }                   /* heading never ends a page alone */
.footer  { position: fixed; bottom: 0; }            /* repeats on every printed page */
```

- Chrome's native print dialog cannot inject page numbers into a page-rendered
  document. A repeated footer ("Confidential — <doc name> — <period>") is the
  honest substitute; state the limitation in delivery notes.
- The popup's URL is `about:blank` and Chrome prints it in the footer. Fix:
  after `document.write` and before `print()`, run
  `history.replaceState(null, '', '/report')` — same-origin blank windows allow
  it, and the footer then prints the real origin/path.
- Currency/number alignment: right-align numeric table columns and keep
  label+value groups in the label cell (a net total in the last data column
  reads as belonging to that column).

## Headless render of the real PDF

The app's own popup + `window.print()` cannot be driven headlessly; for QA,
write the same report HTML into a Playwright page and call `page.pdf()`:

```js
const pg = await browser.newPage()
await pg.setContent(reportHtml)          // the builder's exact output
await pg.pdf({ path: outPath, format: 'A4', printBackground: true,
               margin: { top: '12mm', bottom: '14mm', left: '12mm', right: '12mm' } })
```

Keep the margins identical to the CSS `@page` rule or the rendered PDF will
paginate differently from what users get.

## Rasterize + inspect every page

```bash
pdftoppm -png -r 80  file.pdf prefix     # layout overview per page
pdftoppm -png -r 200 file.pdf prefix     # text/notation checks (80 DPI misreads glyphs)
ls prefix-*.png | wc -l                  # inventory FIRST — never head-truncate
```

Then `vision_analyze` each page with targeted questions:

> "Check ONLY: 1) does the date column fit on one line 2) is there a totals row
> under the table 3) is the footer present. Verdict: pass/fail + defects."

Rules that make vision output trustworthy:

- One page per call; crop to the region at 150+ DPI for small text or chart
  legends (full-page downscales make them invisible → "missing" verdicts).
- Ask "check ONLY <specific items>" — open-ended reviews return long lists
  mixing real layout defects with data-hygiene complaints and OCR noise.
- Verify any claimed TEXT defect against the source string before editing;
  vision invents typos and "strikethrough ghosting" that are not in the HTML.
- Numbers: ask the vision to recompute sums from what it sees ("do the legend
  amounts sum to the center total?") — this is a free reconciliation check.

## Reconciliation test shape

For each period mode (Day/Month/Year/Range/All): navigate to the dashboard,
capture the KPI values it displays, export the PDF, extract its text, and
assert PDF == captured values. Fixture rows for shared databases must be
seeded with uniform key shapes (PostgREST bulk insert requires identical keys
across rows) and cleaned up by id — see `productivity/supabase` — and never
assert absolute totals; reconcile against what the dashboard shows for the
same filter.
