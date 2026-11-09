---
name: pdf-reports
description: Use when exporting professional PDF reports from a web app.
metadata:
  author: attila
  version: "0.1.0"
  license: MIT
  hermes:
    tags: [pdf, reports, print, finance, documents]
    related_skills: [dataviz, investor-materials]
---
# PDF Reports (web-app print exports)

Produce the printable documents a web app hands to a client or accountant:
financial summaries, income reports, plan documents, audit exports. The
deliverable is a PDF a professional would sign — reconciled numbers, corporate
layout, no raw uuids, no UI chrome. Triggers: "monthly/annual report PDF",
"export the income report", "make the PDFs look professional", any print-style
document export. Chrome-print mechanics and the render/inspect commands live in
`references/print-css-and-render.md`.

## When to Use

- A web app needs a printable PDF report: "monthly/annual report PDF", "export
  the income report", "make the PDFs look professional".
- Any print-style document export (financial summary, plan document, audit)
  that must carry reconciled numbers and a corporate layout.
- Not for editing existing PDFs (nano-pdf) or spreadsheet models (finance/*).

## Standing preferences (every report in this class)

- **One letterhead family.** Every exported document shares the org header
  (logo + org name + document title + exact period + generated-on date) and the
  same footer. If the app has an EHR/document header, ALL exports use it.
- **Reuse the app's existing date filters.** Day/Month/Year/Range/All-time
  selection comes from the app's ONE shared period picker + ONE shared period
  predicate. Never build a parallel reporting-period system — dashboards and
  exports must filter identically or the numbers diverge.
- **The visual verdict is the finish line.** Render the real PDF and inspect
  the pages; iterate until no real defects remain. A green test is not done.
- **Deliverable copies** go to BOTH `~/Downloads` and the repo/project root,
  with a README pointer.

## Procedure

### 1. Pin the numbers' single source of truth

Identify the metrics helper the dashboard renders from and make the report
consume the SAME helper — never recompute totals inside the template. Record
its contract first (what counts as income/expense, how voids are treated,
whether gross is cash or gross treatment value) and build to it. A report that
re-derives numbers is a second authority that will drift.

### 2. Pure builder module + self-check

One module `build<Name>Report(data, period, meta) -> HTML string`, pure and
importable, with a `demo()` self-check that runs on a tiny fixture and asserts
structure AND arithmetic reconciliation (chart shares sum to the total, ledger
totals row equals the statement). Run `demo()` in CI/verification before any
UI work — a builder that fails its own fixture must never reach a page.

### 3. Report anatomy (the benchmark for "corporate")

1. Letterhead (standing preference above) + the exact resolved date range.
2. KPI summary strip: period totals with one prominent net figure.
3. Previous-period comparison: both periods' values plus delta, colored by
   FAVORABILITY (income/net up = green, expenses up = red — sign-based coloring
   marks an expense increase as good).
4. Statement table(s) (inflows/outflows by category).
5. Charts (below).
6. Detailed ledger with grand-total row (below).
7. Insights bullets (below).
8. Confidential footer repeated on every printed page.

### 4. Charts: print-safe inline SVG only

Doughnuts for composition (center total; legend with % AND absolute amounts;
segments under ~3% grouped into "Other" with a reconciliation caption), grouped
bars for inflow-vs-outflow, single series for net trend. Zero-fill month axes
so interior gaps stay visible (an annual chart must show every month); keep day
axes sparse with a caption stating the convention. Captions state the
reconciliation truthfully ("shares reconcile exactly with the total").

### 5. Ledger discipline

Fixed `colgroup` widths with `white-space:nowrap` on date/ref/amount/status —
hard-wrapped dates and flags are the top visual complaint. Show provider
references (payment-intent ids) instead of raw row uuids. Voided rows stay in
the ledger with visible status flags but are excluded from totals; corrections
stay flagged for traceability. Grand totals under the table: put the NET in the
label cell so it does not land under the last (Status) column.

### 6. Insights say only what the data supports

State baselines alongside every delta ("X -> Y: down Z"). Never echo raw
ledger description text into prose — user typos get amplified into
"findings". Word void/correction counts precisely ("N voided, excluded from
totals; M carrying corrections, kept for traceability").

### 7. Verification ladder (all rungs, in order)

1. Builder `demo()` green.
2. Reconciliation E2E: for EACH period mode, drive the real app to the report,
   capture the dashboard's own displayed numbers, export, and assert the PDF's
   numbers equal the captured values. Also assert per-mode APPROPRIATENESS: the
   chart aggregation matches the period (daily vs monthly buckets), the exact
   boundary dates are printed, a fixture on each edge proves inclusive
   boundaries, nothing outside the period leaks into the ledger, and switching
   modes leaks no stale range/title into the next export. Never assert
   hardcoded amounts against a shared database — other rows exist and a failed
   fixture insert leaves the test reading production data.
3. Render REAL PDFs of representative periods, rasterize every page, and
   inspect each page with targeted "check ONLY X" vision questions (see the
   reference for the commands and DPI guidance).
4. Classify vision findings: code defects (layout, labels, wrapping, colors)
   get fixed; data-hygiene defects (test rows, typos in user-entered data,
   implausible amounts) are REPORTED, never silently "fixed" — the report
   faithfully shows recorded data.
5. Battery of the app's static suites, then ship and re-run the reconciliation
   E2E against production.

## Pitfalls

- **Never conclude "content is missing" from a truncated file listing.** A
  `ls | head`-style cap hides later pages/sections and turns your own sampling
  error into a false defect report against the report builder. Inventory the
  full page set first.
- **Open-ended vision reviews of rendered pages flood with noise.** Ask focused
  "check ONLY: 1..3" questions per page, and verify any claimed text defect
  (typos, ghosting, garbled names) against the source before "fixing" — OCR
  misreads glyphs and invents typos that are not in the document.
- **Crop at real resolution.** A downscaled full-page screenshot makes small
  decorations/charts invisible to the vision model; crop the region at 150+
  DPI and re-ask instead of accepting "not visible".
- **Chrome's native print cannot inject page numbers.** Repeat the
  confidential footer on every page and state the limitation in the delivery
  summary — do not build custom pagination machinery for a browser-print PDF.
- **The print window's URL is what the browser prints in its footer.** A bare
  `window.open('', ...)` yields `about:blank` there. Open the window at a real
  static surface (a tiny `/report.html` shipped in `public/` with the brand as
  `<title>`), `document.write` the report over it, then `history.replaceState`
  to a clean path (e.g. `/report`) as an upgrade — replaceState alone can be
  blocked and leaves the bare window. Browser headers/footers cannot be
  disabled from page code; the document's own footer must carry everything
  that matters.
- **Multi-page tables need `thead { display: table-header-group }`** and
  `tr { break-inside: avoid }`; keep whole sections `break-inside: avoid` so a
  heading never ends a page alone.
- **Stale export popups poison test reads.** A DOM text read that scans the
  whole document concatenates every export the run produced; scope the read to
  the newest popup (or close previous ones) before comparing numbers.
- **Print only after images settle.** `window.print()` fired right after
  `document.close()` captures before an async logo finishes loading — the PDF
  prints with a blank letterhead. Wait on `document.images` (resolve on
  `complete`/`onload`/`onerror`) with a ~2s cap so a hung fetch cannot block
  the dialog, then print. One guard in the shared print helper covers every
  export.
- **Playwright popup events race with `document.write`.** `waitForEvent('popup')`
  / `ctx.on('page')` can miss an export window that `window.open` demonstrably
  returned (the write replaces the document mid-attach). Intercept
  `window.open` via `addInitScript` (push every handle into `window.__opened`)
  and read `__opened[last].document` for the exported text; override
  `window.print` the same way to record `document.images` state at print-time
  and prove the logo loaded before the capture.
- **One popup, one print.** `window.print()` is async to the user's dialog;
  drive headless verification through the popup's rendered DOM or `page.pdf()`,
  not by hooking the print dialog.
