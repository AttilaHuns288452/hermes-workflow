# Clickable prototype + wireframe from the static frame set

Both derivatives are pure additions to the merged static file — the original
files stay untouched. Verified 2026-08-13 on the 24-screen Guardian Alert set.

## 1. Clickable prototype (click element → show another frame)

Two parts: (a) annotate hotspot elements with `data-nav="NN"`, (b) a runtime
that hides all `.frame`s and shows the target.

### Annotation — Python stdlib only (no bs4/lxml needed)

- Parse with `html.parser.HTMLParser`; keep each element's ORIGINAL start-tag
  string and inject attributes by string surgery (`start[:-1] + ' data-nav=...'`)
  so the output stays byte-identical except the added attribute.
- Identify frames by exact class token `frame` (exclude `frame-label`/
  `frame-wrap`/`frame-item` — the label prefix match WILL trip naive filters).
- Rules per screen: `BACK = {frame: target}` for `.header-back` elements, and
  a text map `{frame: [(text, target), ...]}`.
- **Text matching: exact for `<button>`/`<a>`, CONTAINS for rows/cards**
  (`.list-row`, `.account-row`, `.radio-card`, `.device-card`). Row subtitles
  make exact matching fail; but a device card contains its own "Test alarm"
  button text, so rule ORDER matters — put the card-specific key first
  (`("Wearable wristband", "05")` before `("Test alarm", "13")`).
- **`Node.text` from a naive parser holds only DIRECT text nodes** — a
  `<div class="account-row"><p>Change account</p><p>Switch…</p></div>` shows
  empty direct text. Collect full text recursively and normalize whitespace.
- Bottom nav tabs: match the `.nav-label` text (Home/About/Account →
  universal targets).
- Report per-frame matched rules; a rule that never matches is a typo or
  wrong class-name assumption (e.g. OD's card class is `device-card`, not
  `list-row`; "Delivery driver" vs "Delivery Driver").

### Runtime

- CSS: `.frame { display:none }` and `#frame-01 { display:flex }` — **NO
  `!important`**. With `!important`, inline `style.display` set by JS can
  never win: frame-01 stays pinned visible, targets never appear, every click
  "fails" while the DOM is correct. This is the #1 prototype bug.
- JS: one delegated `document.addEventListener('click', …)` on
  `e.target.closest('[data-nav]')`; hide all frames, show target, update a
  fixed badge with the frame's label, `scrollTo(0,0)`.
- `[data-nav] { cursor:pointer }` for affordance.

### Verification — Playwright click-through, not screenshots

Assert `visible frame id` after each programmatic `.click()`: initial →
Sign in → Home → device card → detail → nav Home → … A sheet-style screen
may have NO `.header-back` (its back is the bottom nav) — check the design
before assuming navigation chrome exists.

## 2. Wireframe (low-fi gray) — CSS variable override, zero body changes

If every color flows through `:root` CSS variables, a wireframe pass is one
extra `<style>` block:

- Redefine the palette to grays: `--accent:#8a8f98; --text:#4b5057;
  --secondary:#8a8f98; --page-bg:#f4f5f7; --card-bg:#fff; --border:#d8dbe0;
  --green/--red/--amber:#8a8f98; --*-tint:#e8eaee` etc.
- Hardcoded colors still leak: banner classes (`#fef3c7`, `#991b1b`, …) and
  inline-styled avatars (`style="background:#ede9fe;color:#7c3aed"`). Override
  the classes, and for inline styles use `!important` (here it is CORRECT —
  it must beat inline styles).
- Verify by computed style: `getComputedStyle(.btn-primary).backgroundColor`
  must be the gray, `--accent` var must resolve to the gray, 24 frames still
  390×844.

## Pitfalls

- `!important` display rules break the prototype's JS visibility toggling.
- Exact-vs-contains text matching and rule ordering on nested rows.
- Frames without header-back (sheet screens) break naive back-button tests.
- Vision QA (OpenRouter qwen-vl) can hit HTTP 402 when the key is exhausted —
  geometry checks (frame count, dims, computed colors) still verify layout
  structure without it.
