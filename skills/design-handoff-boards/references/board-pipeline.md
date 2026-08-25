# Board Pipeline — Session Detail (2026-08-20)

## Context
D.A.R. Dental Clinic — 75 frames (`00_Welcome` → `63_Staff_Settings`), deck order `A-K` via `frames/order.txt`. Merged boards: `DAR_Dental_All_75.html` (deck), `DAR_Dental_Flow.html` (2D graph), plus wireframe variants.

## Fix 1: Border-triangle connectors dropped by html.to.design
- **Symptom:** 65 inter-frame connectors on `DAR_Dental_All_75.html` imported stem-only — no arrowheads. User report: "components still missing" on import.
- **Root cause:** `merge_frames.py` used `.conn .arr { width:0; height:0; border-left:5px solid transparent; border-right:5px transparent; border-top:6px solid #94a3b8; }`. The importer drops zero-size elements regardless of borders.
- **Fix:** Replace with real SVG:
  ```css
  .conn { display:flex; flex-direction:column; align-items:center; gap:0; margin:0 auto; }
  .conn-stem { width:2px; height:14px; background:#94a3b8; border-radius:1px; }
  ```
  ```html
  <div class="conn"><div class="conn-stem"></div><svg width="10" height="6" viewBox="0 0 10 6" style="display:block"><polygon points="0,0 10,0 5,6" fill="#94a3b8"/></svg></div>
  ```
  Flow graph uses `14×14` polygons (`points="0,0 14,7 0,14"` etc). Verified: deck `65 polygons`, flow `169 polygons`.
- **Assert added:** `assert doc.count("<polygon") > 20` (deck ~65, flow 169).

## Fix 2: Stale board lingering
- `DAR_Dental_All_71.html` (238K, 71 frames, Aug 16) remained after staff sections J/K were added (47-54) and `order.txt` grew to 75. Importing stale file = missing Staff column.
- **Fix:** Deleted `All_71`; rebuilt `All_75` (361K→369K) and `Flow` (494K→505K). Assert `n_labels == n_frames == len(order_entries)` catches this.
- **Wireframe staleness:** `DAR_Dental_Wireframe.html` was Aug 19 354K with 0 polygons. Rebuilt via appended `!important` gray `:root` override (361K/495K, polygons preserved).

## Verification (this session)
```
audit.py:           AUDIT CLEAN — zero findings
qa_shot.py:         75/75 frames OK -> ALL PASS (390×844, scrollHeight<=844, fill>0.75)
qa_deep.py:         checked 75 frames, 0 with issues
merged checks:      var 0, <use 0, <symbol 0, rgba 0, repeating-linear-gradient 0
DAR_Dental_All:     65 polygons, 65 conn
DAR_Dental_Flow:    169 polygons
```

## Repro
```bash
python -E merge_frames.py frames DAR_Dental_All_75.html
python -E flow_board.py
# wireframes: append !important gray :root to each merged board
python -E audit.py && python qa_shot.py && python qa_deep.py
```
