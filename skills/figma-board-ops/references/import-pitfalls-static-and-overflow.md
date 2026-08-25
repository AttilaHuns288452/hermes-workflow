# Import pitfalls: overflow clip + static-only frames

Two real causes of "components missing / model didn't load" on html.to.design
imports, found while fixing the DAR Dental income boards (Aug 2026).

## 1. `.body{overflow:hidden}` clips the ENTIRE frame

The importer renders each frame at a fixed 390×844. Any frame body with
`overflow:hidden` crops everything below the fold — so bottom cards (e.g.
**Revenue by procedure** on Analytics page 2) AND interactive controls
(range toggles Monthly/Yearly/All time, Save buttons) import missing or
"dead". This reads to the user as "model didn't load correctly" even though
the HTML/JS is fine in a browser.

It is the **#2 cause after `var()`**.

Fix (one-line per frame, or baked into the merge script's shared CSS):
```css
.body{flex:1;overflow-y:auto;overflow-x:hidden;padding:16px;display:flex;
  flex-direction:column;gap:16px;scrollbar-width:none}
.body::-webkit-scrollbar{display:none}
```
Assert: `\.body\{` rule must contain `overflow-y:auto`, never `overflow:hidden`.

## 2. Figma frames must be 100% STATIC — no JS

User standing rule for any frame handed to Figma: *"no special shenanigans
only static"*. When asked for a modal/frame to import:
- Strip every `<script>` block.
- Strip inline handlers: `onclick`, `oninput`, `onchange`, `addEventListener`.
- Bake the selected state into markup with `class="on"` (segmented control,
  category slot, toggle).
- Pre-fill inputs with `value="..."`.

Dummy JS only proves behavior the import can't show and feeds the
"model didn't load" misread. Static file = safe import.

Verify: `grep -ci '<script\|onclick\|oninput\|onchange\|addEventListener' frame.html`
must print `0`.

## Note on the income board fix (Aug 2026)

- `Income_Figma_7.html`: body overflow fixed; revenue-by-procedure already on
  page 1 — it was page 2 that was expenses-only by design; restored the card
  on page 2 of the Monthly view (`DAR_Dental_Income_Grouped.html`).
- `frames/66_Income_Add_Expense.html` = static Income variant (no JS).
- `frames/66b_Income_Add_Expense_Expense.html` = static Expense twin (Type=
  Expense pre-selected, Category=Expense list, Description field instead of
  Patient, hint flipped).
