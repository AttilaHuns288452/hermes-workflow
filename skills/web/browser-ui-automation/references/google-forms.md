# Google Forms editor (browser path)

Use when Forms API/`gws` auth is absent but the user's browser is logged in. Create a form at `https://docs.google.com/forms/u/0/create`. Follow the parent skill's procedure (single tab, `Page.bringToFront`, hit-tested trusted clicks) throughout.

## Selectors

- Form title: `[aria-label="Form title"]`; description field sits directly below it (contenteditable).
- Question cards: `[aria-label="Question"]` — DOM order = visual order. Question title: `[aria-label="Question title"]` inside the card.
- Add: `[aria-label="Add question"]`; per-card `[aria-label="Duplicate question"]` / `[aria-label="Delete question"]` — only the ACTIVE card's toolbar buttons are visible, and they are hoisted first in the DOM (see parent skill step 8).
- Type picker: the card's own `[aria-label="Question types"]` listbox; options are `[role="option"]` matched by text ("Short answer", "Paragraph", "Multiple choice", ...). Assert option height > 0 before clicking.
- Per-question Required toggle: a Material switch that resists synthetic events — trusted clicks only, and treat the responder view as ground truth.

## Order of operations

1. Set the title/description via execCommand (parent skill step 6).
2. **Before adding questions**, fix the defaults: Settings → Question defaults → turn "Make questions required by default" OFF when the spec wants optional fields (every new question is otherwise born required); Settings → Responses → "Collect email addresses" = Do not collect unless the spec wants it (collected email becomes a required field on the responder form).
3. Per question: Add → retitle → set type. Activate the anchor card before Add ("Add question" inserts after the ACTIVE card — to place a question last, activate the current last one first).
4. Publish when a shareable link is wanted: Publish button (top right) → dialog ("Anyone with the link") → Publish.
5. URLs: edit = `/forms/d/<id>/edit`, authenticated preview = `/forms/d/<id>/preview`, public responder = `/forms/d/e/<FAIpQLS...>/viewform` — the responder URL exists only after publishing and appears in an input value, not as a link.

## Verification checklist (responder page, fresh load)

- Item count and order match the spec exactly.
- Every item is Short answer (`input[type="text"]`) unless the spec says otherwise.
- Zero `[aria-label="Required question"]` markers when items must be optional.
- No email/sign-in field unless requested.

## Failure modes

- A retitled or deleted the WRONG card: Add/"last" targeting assumed append-at-end, but insertion is relative to the active card — see parent skill step 8.
- All questions required in the live form: the required-by-default setting was left ON; flip it, then re-add or toggle per card with trusted clicks.
- Question stuck on Multiple choice: the type dropdown never opened (option rect height 0, usually a backgrounded tab) — see parent skill steps 3 and 7.
