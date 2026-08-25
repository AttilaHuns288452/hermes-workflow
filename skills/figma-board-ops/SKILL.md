---
name: figma-board-ops
description: Use when delivering HTML boards to Figma.
---

# Figma Board Ops

Curator-managed umbrella for HTML boards that survive html.to.design import and read consistently across roles. Use when building, merging, or QAing any `frames/ → DAR_Dental_All_*.html / Flow` style board set, or auditing cross-role user flows before defense/import.

## When to use
- Merging 70+ `390×844` frames into `All_*.html` + `Flow.html` via `order.txt`
- Fixing "components missing after import" (vars, icons, arrows, navs)
- Auditing role-based flow consistency (patient/dentist/owner, staff, income)
- Rebuilding wireframe variants

## Import-safe transforms (bake into generator + merge, assert build fails if violated)

| Breaks import | Fix | Assert |
|---|---|---|
| `var(--x)` — importer does not resolve custom properties | Parse `--x: value;` from shared CSS, regex `var\(--[a-z0-9-]+(?:,\s*[^)]*)?\)` → literal in CSS AND inline styles. Class must include digits (`[a-z0-9-]`) — `--ink-2` survives `[a-z-]` and leaves hundreds of unresolved vars. | `assert "var(" not in doc` |
| `<use href="#i-*">` sprite refs — defs land outside frame | Inline each symbol's inner paths per frame, drop shared sprite. Extract without requiring `<defs>` wrapper; match `ic` and `icon` classes; inject `viewBox="0 0 24 24" fill="none" stroke="currentColor"...` when missing. Count `path,rect,circle,line,polyline,polygon`. | `assert "<use" not in doc and "<symbol" not in doc` |
| `<a>` anchors — importer drops contents | Convert to `<div>` keep classes drop href. | `assert "<a " not in doc` |
| Zero-size border-triangle arrows (`width:0;height:0;border-left/right:5px transparent;border-top:6px solid #94a3b8` — e.g. `.conn .arr` 65 conn divs on All_75) | Real SVG: `<div class="conn"><div class="conn-stem"></div><svg width="10" height="6" viewBox="0 0 10 6"><polygon points="0,0 10,0 5,6" fill="#94a3b8"/></svg></div>` with `.conn{display:flex;flex-direction:column;align-items:center}` + `.conn-stem{width:2px;height:14px;background:#94a3b8}` | `assert doc.count("<polygon") > 20` (All_75 65, Flow 169) |
| `repeating-linear-gradient` dashes | Real 12px rects with 12px gaps, plain `background:` | `assert "repeating-linear-gradient" not in doc` |
| `rgba(` overlays / gradients | Opaque hex only | `assert "rgba(" not in doc` |
| Bottom nav `position:absolute;bottom:0` | Flex pin: `.frame{display:flex;flex-direction:column}` + `.body{flex:1 1 auto;min-height:0;overflow:hidden}` + `.nav{flex-shrink:0}` direct child of frame | Visual + geometry: `scrollHeight <= 844` |
| Fix CSS after `</style>` | Insert before `</style>` or in extra style block | — |
| `transform:translateX(-50%)` | `margin:0 auto` in flex header | — |

## Flow integrity checks (cross-role)

Audit before every board rebuild; fix in `gen_frames.py` (smallest diff, reuse helpers):

1. **Auth symmetry** — both `01_Patient_Login` and `09_Dentist_Login` need back to `00_Welcome` role picker if either has it.
2. **KPI naming** — empty vs filled dashboard must share metric names (`Income Today` not `Revenue` vs `Income Today`).
3. **Control parity** — same action (time assignment) must use same widget (`seg AM/PM` not `slot on` vs `seg`) across `f32 Approve` and `f75 Time Conflict` — enables Figma component reuse.
4. **Selection states** — `svc-row on` must include `<div class="rdot"></div>` inside `.radio`; highlight without dot reads as unselected.
5. **Orphaned nodes** — every node in `flow_layout.POS` + `flow_notes` must be reachable: if `f74 Change Password` exists in graph (`72→74`, `74→72`), `f72 Profile Edit` needs a `Change Password` button to reach it.
6. **Duplicate CSS** — single `.divider` rule (last wins silently); remove dup, keep `gap:12px;color:var(--ink-2)`.
7. **Archived screens** — functions not in 75-frame deck (`f36 Verify Payment`, `f60 Outstanding`) mark `ponytail: archived — …; not in 75-frame deck` so deck count 75 == function count is explainable.

## Verification (playbook)

```bash
python -E gen_frames.py                          # writes 75 frames + order.txt
python -E merge_frames.py frames DAR_Dental_All_75.html
python -E flow_board.py                          # Flow 109 edges, 169 polygons
# wireframes = appended !important gray override on fresh boards (not stale copy)
python -E audit.py                               # AUDIT CLEAN — zero findings
python qa_shot.py                                # 75/75 frames OK — 390×844, no overflow, fill>0.75
python qa_deep.py                                # checked 75 frames, 0 with issues
python -c "assert 'var(' not in open('DAR_Dental_All_75.html').read() ..."
# counts: All_75 65 polygon, Flow 169 polygon
```

- Geometry via Playwright is authoritative; vision is flaky.
- Wireframes must be rebuilt from fresh boards each time (stale Aug 19 354K → fresh 361K/495K).

## Files
- `references/dental-session-2026-08-20.md` — this session's transcripts, counts, and before/after diffs
- `templates/import_safe_transforms.py` — canonical `parse_vars/resolve_vars/inline_icons/frame_div` to copy into merge scripts

See also: `html-to-figma-import-safety` (external, read-only — adopt via `hermes curator adopt html-to-figma-import-safety` to make writable, or use this umbrella).
