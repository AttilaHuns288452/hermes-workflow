# Staff import — stale merged board (2026-08-19)

## Symptom
User: "staff section they seem to be not correctly imported when being imported to figma" (ponytail mode). Staff module = 9 frames: `47_Staff_List`, `48_Staff_Invite_Dentist`, `49_Staff_Invite_Sent`, `50_Staff_Approval_Queue`, `51_Staff_Reject_Dialog`, `52_Staff_Permissions`, `53_Staff_Remove_Dentist`, `54_Dentist_Staff_View`, `63_Staff_Settings` (order.txt section `# J · Staff module` + `K` tail).

## What was actually broken
- Individual staff frames were **already import-safe**: flat static cards in normal flow (`dlg-wrap` + `dialog` inside `.body`), no `position:absolute`/`fixed`/`transform`/`rgba` overlays (verified via `gen_frames.py` CSS + `frames/*` grep). Dialog frames use inline `display:flex` body flow — Figma's html.to.design would not drop them.
- Merged boards `DAR_Dental_All_75.html` / `DAR_Dental_Flow.html` + wireframes were **stale** (mismatched `order.txt` deck order after prior staff additions). Importing the stale board = Staff column J absent or showing byte-identical base pages. User imports the single `All_*.html`, not individual frames.

## Diagnosis steps that worked
1. `grep -n "def f47|def f48|...|Staff" gen_frames.py` → FRAMES list includes all 9 at correct positions.
2. `ls frames/*.html | wc -l` = 75, `cat frames/order.txt` → J section has 8 + K has `63_Staff_Settings` = 9.
3. `grep -c 'frame-label' DAR_Dental_All_75.html` vs `class="frame"` — 76 vs 75 is normal (one `.sec-title` in the count pattern); real invariant is `frames==len(order entries without #)`.
4. Playwright geometry (must use `C:/Users/Attila/AppData/Local/Programs/Python/Python311/python.exe`, not hermes venv):
   ```python
   from playwright.sync_api import sync_playwright
   # per-frame: fr.getBoundingClientRect() == 390×844 @ y0, scrollHeight==844 clip==0
   # merged board: same check via .frame-label iteration — no H-overflow
   ```
   Staff frames all `390×844 clip=0` individually and inside the merged board.
5. Vision QA (MiMo) on `47_Staff_List`, `48_Staff_Invite_Dentist`, `52_Staff_Permissions`, `51_Staff_Reject_Dialog` — no clipping, no double icons, toggles `3 on / 2 off` correct, nav highlight present. Vision confirms but geometry is authoritative.

## Fix applied
- Regenerated: `python -E gen_frames.py && python -E merge_frames.py frames DAR_Dental_All_75.html && python -E merge_frames.py frames DAR_Dental_Flow.html` (canonical rebuild — CSS vars resolved, `<use>` inlined, no `var()`/`rgba`/`symbol` leaks).
- Regenerated wireframes by appending gray `!important` `:root` override after `</head>` (zero body changes).
- Verified: `audit.py → AUDIT CLEAN — zero findings`; geometry → all Staff `390×844 clip=0`; `DAR_Dental_All_75.html` import-safety: no `rgba`/`use`/`symbol`/`var()` leaks.

## Lesson
When a FIGMA IMPORT "drops a module," check the **derived board**, not the source frames first. The generator is the fix point — never hand-edit merged HTML. The skill `figma-html-import` already knew this; this session proved the diagnostic order: stale-board check before frame debugging.
