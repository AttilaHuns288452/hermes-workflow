# Reading a Figma PDF export as a product spec

The PDF export is a design prototype dump — pages include junk, duplicates, and state captures. Extract the SPEC, not a page-by-page copy.

## Extraction

- Text layer first: `pdftotext -layout "<file>.pdf" out.txt`, then split on `\f` into per-page text files. Cheap page thumbnails: `pdftoppm -r 50 -png pdf pg`. Detail crops/measurement: `-r 300`. (Screen-asset extraction and callout-rect measurement → `product-demo-film` skill — do not duplicate that machinery here.)
- Skip leading pages that are Figma canvas junk (boards, cover art, wide multi-panel boards); phone screens start where consistent device widths appear.

## Proportional measurements

When the task is type/spacing calibration (not flows), extract the frame's proportions from the same PDF with pymupdf: `page.rect` = artboard width, text-span `size` = body/heading font px, span `bbox` x-offsets = gutters. These three numbers bracket the type-multiplier and gutter candidates for the target viewport (workflow: `product-site-design` → 'Proportional type system'). The artboard width is often NOT the assumed 1440 (e.g. 1280pt) — measure before deriving ratios.

## Page inventory

One row per page: `page → role → screen → state`. Classify ROLE by the visible bottom-navbar item set (e.g. patient 5-tab / doctor 4-tab / owner 6-tab) — content alone misleads: the same screen (calendar, patients list, messages) is usually exported in several role variants, and the navbar is part of the screen's identity.

Flag unusable pages:

- **Modal/scrim states** (>50% mid-gray pixels: logout confirmations, edit dialogs with overlay) are ONE interaction state, not a screen — find the clean sibling state instead.
- **Outdated/superseded flows** — a page family present in the export but removed from later flows (and absent from the newest video/exports) is a rejected design; record it as banned, don't implement it.
- **Multi-screen boards** (one wide page holding several phones): treat each panel as its own screen.

## Flow chains

Map each major workflow as an ordered page chain (e.g. book: service list → date → time → payment summary → QR → success). The chain IS the behavioral contract for that feature: implement the transitions, not just the pages. Note entry points (which tab/button leads in) and terminal states (success, empty, error) per chain.

Cross-check chains against the demo video when both exist — video behavior wins on transitions; Figma wins on the pixels of each step.