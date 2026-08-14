---
name: html-prototype-flow-audit
description: Audit HTML design-frame sets for navigation flow gaps.
---

# HTML Prototype Flow Audit

Audit a directory of `NN_Name.html` design frames (mobile prototypes, usually Figma-importable, 390x844) for cross-frame navigation and flow completeness. Produces a terse per-frame issue list.

## How these prototypes are structured (critical)

- Navigation is **purely visual** — no `<a href>`, no `<button>`, no onclick. A first pass with link/button regexes returns NOTHING.
- Tabs: `<div class="nav-item">` … `<div class="nav-ic">svg</div><div>Label</div>`, active = `class="nav-item active"`.
- Buttons: `<div class="btn btn-primary">Label</div>`. Icon buttons: `<div class="icon-btn">`.
- Destinations are inferred from button **labels** — check each label maps to an existing frame (e.g. "Review" → Requests frame, "Back to Staff" → Staff List).
- Price entity is `&#8369;` (PHP peso) — normalize to `PHP` before reading text.

## Extraction (one Python pass over all frames)

```python
# nav labels: inner <div>Label</div> after .nav-ic — plain `.*?` regex gets eaten by nested divs
re.finditer(r'<div class="nav-item( active)?"[^>]*>\s*<div class="nav-ic">.*?</div>\s*<div>([^<]*)</div>', body, re.S)
# buttons
re.finditer(r'<div class="btn[^"]*"[^>]*>(.*?)</div>', body, re.S)
# visible text: strip_tags(body).replace('&#8369;','PHP'), then drop the <symbol> svg-defs block
```

Per frame record: title, nav items + active flag, btn labels, icon buttons, marker hits (`GCash|Maya|balance|outstanding|slot|&#8369;|price`). Batch-dump text of frames that hit markers to check context before flagging.

## Audit checklist

1. **Tab set per role** — verify against the product spec (e.g. owner 6 tabs, staff dentist 4, patient 5). Count `.nav-item`s per frame.
2. **Active tab matches screen** — dialogs/overlays inherit the PARENT screen's active tab; a dialog showing Home over a Patients-context screen is a bug.
3. **Every button → plausible destination** — search the frame set for a matching screen; unbuildable actions (Print, PDF export, Email) are fine, missing form/detail screens are dead ends.
4. **Lifecycle flows** — trace end-to-end against product rules (registration: role select → register → pending → approve/reject → activated; booking: patient picks service+date only → dentist assigns time on approve → completion records amount paid). Inconsistencies are usually *leftover copy/UI from an older flow* (times shown on pending requests, "locks the slot" copy, payment-proof uploads, GCash, outstanding-balance columns).
5. **Leftover-UI markers** — scan for payment methods (GCash/Maya), balances, slot-based copy on date-based flows, proof-upload flows. Verify context: dentist-side calendar slots and paid-history amounts are usually CORRECT and must not be flagged; patient-side prices/slot pickers are the leftovers.

## Output format

Terse `FRAME NN: issue → fix` lines, hard cap (e.g. 30 lines). Group: structure-OK summary (tab sets, lifecycle, core flow) in 3–4 bullets, then issues ordered by severity (wrong active tab, dead ends, whole outdated frames, copy). End with a "verified fine" list to preempt false-positive fixes.

## Pitfalls

- Don't conclude "no navigation" — you parsed the wrong element type. Divs, not buttons/links.
- `slot` matches inside unrelated words; always check the matched context.
- A frame with no bottom nav (login, settings, dialogs) is normal — don't flag missing tabs there.
- Output must stay a findings report; never edit frames unless asked (read-only audit).
