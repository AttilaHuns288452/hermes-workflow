#!/usr/bin/env python3
"""Geometry QA for a MERGED board (one HTML, many .frame divs).

Usage: python qa_board.py [board.html] [depth_ceiling=1700]

Per frame: must be 390x844, zero x-overflow, no element extending past
the frame bottom beyond `depth_ceiling` (measured RELATIVE to the frame
rect — absolute rects shift when the page auto-scrolls). Default ceiling
1700 because scrollable screens (About, profiles) legitimately run
1000-1700px deep and are clipped by .frame overflow:hidden; tighten to
844+40 only for generator-built decks where every frame is designed to fit.

Set the ceiling from the ORIGINAL board's per-frame depths when merging an
external frame set: flag only what exceeds the original's own numbers.

Exit code = number of frames with issues. Needs playwright:
  "C:/Users/YOUR_USERNAME/AppData/Local/Programs/Python/Python311/python.exe" qa_board.py All_29.html
(bare `python` may resolve to a Hermes-venv interpreter without playwright.)
"""
import sys
from playwright.sync_api import sync_playwright

path = sys.argv[1] if len(sys.argv) > 1 else "All.html"
ceiling = int(sys.argv[2]) if len(sys.argv) > 2 else 1700
issues = 0
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 500, "height": 50000})
    pg.goto("file:///" + path.replace("\\", "/"))
    out = pg.evaluate("""() => {
        const frames = document.querySelectorAll('.frame');
        const res = [];
        frames.forEach((fr, i) => {
            const f = fr.getBoundingClientRect();
            let xOver = 0, deep = 0, what = '';
            for (const el of fr.querySelectorAll('*')) {
                const r = el.getBoundingClientRect();
                if (r.height > 0) {
                    if (r.right > f.right + 1) xOver = Math.max(xOver, Math.round(r.right - f.right));
                    if (r.bottom - f.top > deep) { deep = Math.round(r.bottom - f.top); what = el.className; }
                }
            }
            res.push({i: i + 1, w: Math.round(f.width), h: Math.round(f.height), xOver, deep, what: String(what).slice(0, 40)});
        });
        return res;
    }""")
    for g in out:
        bad = g["w"] != 390 or g["h"] != 844 or g["xOver"] or g["deep"] > ceiling
        if bad:
            issues += 1
            print(f"frame {g['i']}: {g}")
    print(f"checked {len(out)} frames, {issues} with issues")
    b.close()
sys.exit(1 if issues else 0)
