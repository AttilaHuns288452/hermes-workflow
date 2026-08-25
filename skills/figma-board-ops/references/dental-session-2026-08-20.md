# Dental session 2026-08-20 — Figma board fixes

## Boards (final verified)
- `DAR_Dental_All_75.html` 361K — 75 frames, 75 labels, 65 `<polygon>` (real SVG arrows), `var 0, <use 0, <symbol 0, rgba 0`
- `DAR_Dental_Wireframe.html` 362K — same + `!important` gray override (22 overrides), 65 polygons
- `DAR_Dental_Flow.html` 494K — 109 edges, 169 polygons, canvas 17130×10994
- `DAR_Dental_Flow_Wireframe.html` 495K — flow wireframe
- `frames/ 75× 390×844` — `audit.py AUDIT CLEAN`, `qa_shot 75/75 ALL PASS`, `qa_deep 0 issues`
- Stale `DAR_Dental_All_71.html` (238K, 71 frames) removed — was missing J/K staff sections.

## Real import blocker (html.to.design)
`merge_frames.py` `.conn .arr{width:0;height:0;border-left/right:5px transparent;border-top:6px solid #94a3b8}` — zero-size border triangles are dropped by importer. 65 connectors had no arrowheads.
Fix: `.conn{display:flex;flex-direction:column;align-items:center}` + `.conn-stem{width:2px;height:14px;background:#94a3b8}` + `<svg width="10" height="6"><polygon points="0,0 10,0 5,6" fill="#94a3b8"/></svg>`. Assert `polygon >20`.

## Flow inconsistencies fixed in gen_frames.py (6 patches)
1. `.divider` dup — `gap:10px;color:var(--muted)` + `gap:12px;color:var(--ink-2)` — removed first, kept second.
2. `f28 Dashboard Empty` KPI `Revenue ₱0` → `Income Today ₱0` (matches f10 `Income Today ₱1,500`; DESIGN.md says Income Analytics).
3. `f75 Time Conflict` AM pill `slot on` → `seg AM/PM` (`<div class="seg" style="height:44px;padding:0"><div class="on" style="height:40px">AM</div><div style="height:40px">PM</div></div>`) — parity with f32 Approve.
4. `f48 Invite Dentist` selected row missing rdot → `<div class="radio"><div class="rdot"></div></div>` (was empty radio).
5. `f72 Profile Edit` orphaned — `f74 Change Password` existed in POS/NOTES/graph (72→74,74→72) but no button to reach it — added `<div class="btn btn-ghost">{ic("lock",16)} Change Password</div>` below Save/Cancel.
6. `f36` / `f60` archived — added `ponytail: archived — not in 75-frame deck` comments; f01/f09 back already symmetric.

## Sweep (no fix needed)
Auth `f01/f09` back both True; patient B empty→filled per module; `nav_patient` 5-tab; `f54 Staff View` hides Income/Staff via `nav(staff=False,income=False)`; staff 47 pending CC + MR 3/5 perms.

## Replay
```
python -E gen_frames.py && python -E merge_frames.py frames DAR_Dental_All_75.html && python -E flow_board.py
# rebuild wireframes as !important override on fresh boards, not stale copy
python -E audit.py && python qa_shot.py && python qa_deep.py
```
