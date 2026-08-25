---
name: design-delivery-ops
description: Rebuild and verify HTML-to-Figma boards.
---

# Design Delivery Ops — HTML → Figma Boards

Class-level ops for the `gen_frames.py → merge_frames.py → wireframe` pipeline. Prevents the #1 Figma import failure: a stale merged board.

## When to use

- A module (e.g. Staff) "is missing in Figma" but its `frames/NN_*.html` files exist and are import-safe.
- `frames/order.txt` and `DAR_Dental_All_*.html` label counts diverge.
- Any edit to `gen_frames.py` without re-running the merge step.

## The invariant

- `frames/*.html` = source of truth (per-screen, own `<style>` + sprite).
- `DAR_Dental_All_75.html` / `DAR_Dental_Flow.html` = **derived** artifacts — never hand-edit.
- `DAR_Dental_Wireframe.html` / `DAR_Dental_Flow_Wireframe.html` = derived + appended gray `!important` `:root` override (zero body changes).

## Rebuild sequence (canonical)

```bash
cd design
python -E gen_frames.py
python -E merge_frames.py frames DAR_Dental_All_75.html
python -E merge_frames.py frames DAR_Dental_Flow.html
# regenerate wireframes — append gray var override after </head> (no body changes)
python -E - << 'PY'
import pathlib
src=pathlib.Path("DAR_Dental_All_75.html").read_text(encoding="utf-8")
extra='<style>\n:root{ --accent:#8a8f98 !important; --accent-dark:#5a5e66 !important; --accent-soft:#e9eaee !important; --ink:#2a2e35 !important; --ink-2:#6b7280 !important; --muted:#9ca3af !important; --bg:#f3f4f6 !important; --surface:#ffffff !important; --line:#d1d5db !important; --st-pending:#6b7280 !important; --st-pending-bg:#f3f4f6 !important; --st-approved:#6b7280 !important; --st-approved-bg:#e9eaee !important; --st-completed:#6b7280 !important; --st-completed-bg:#e9eaee !important; --st-cancelled:#6b7280 !important; --st-cancelled-bg:#e9eaee !important; }\n.banner,.notif,.tag,.chip,.pill,.datebox,.kpi,.banner.warn,.banner.err{ background:#fff !important; border-color:#d1d5db !important; color:#6b7280 !important; }\n.tag.owner,.tag.staff,.chip,.pill{ background:#e9eaee !important; color:#6b7280 !important; }\n</style>'
out=src.replace("</head>", extra+"\n</head>").replace("<title>Merged frames</title>","<title>DAR Dental Wireframe</title>")
pathlib.Path("DAR_Dental_Wireframe.html").write_text(out, encoding="utf-8")
flow=pathlib.Path("DAR_Dental_Flow.html").read_text(encoding="utf-8")
flow=flow.replace("</head>", extra+"\n</head>").replace("Navigation Flow Map","Navigation Flow Map — Wireframe")
pathlib.Path("DAR_Dental_Flow_Wireframe.html").write_text(flow, encoding="utf-8")
PY
```

## Diagnosis (fast)

```bash
# label/frame drift?
grep -c 'frame-label' DAR_Dental_All_75.html; grep -c 'class="frame"' DAR_Dental_All_75.html
# order.txt vs board
grep 'class="frame-label"' DAR_Dental_All_75.html | head
cat frames/order.txt | grep -v '^#' 
# import-safety
grep -q 'rgba(' DAR_Dental_All_75.html && echo "rgba leak"
grep -q '<use' DAR_Dental_All_75.html && echo "use leak"
grep -q 'var(' DAR_Dental_All_75.html && echo "var unresolved"
```

## Verification (always after rebuild)

1. `python -E audit.py` → `AUDIT CLEAN — zero findings` (no `transform`/`rgba`/`position:absolute`, no tag mismatches).
2. Geometry via Playwright (`C:/Users/Attila/AppData/Local/Programs/Python/Python311/python.exe` — hermes venv has no playwright):
   ```python
   from playwright.sync_api import sync_playwright
   # frame 390×844 @ y=0, scrollHeight==844 (clip==0), no h-overflow (right > frame.right)
   ```
3. Visual spot-check of the affected module (e.g. Staff `47–54, 63`) — no clipping, no double icons, nav highlight correct.

## Pitfalls

- **Never import `DAR_Dental_All_71.html`** — legacy; use `DAR_Dental_All_75.html` (or `Flow`).
- `76 labels / 75 frames` is expected — one `.sec-title` shares the label count pattern; assert `frames==len(order entries without #)` not `labels==frames`.
- `fit-content` boards report viewport-width rects — not overflow.
- Sprite `<svg>` must be `display:none`, never inline 0×0 (phantom line box).

## References

- `references/staff-import-stale-board-2026-08-19.md` — session transcript: Staff module "not correctly imported" → stale board diagnosis, rebuild, and QA evidence (Playwright geometry + MiMo vision).
