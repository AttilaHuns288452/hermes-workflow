#!/usr/bin/env python3
"""Frame QA: static import-safety + Playwright geometry for 390x844 design frames.
Expects sibling dirs: frames/NN_Name.html + frames/order.txt (from design-handoff-boards pipeline).
Run: python3 qa_frames.py  — exits 1 on any static violation."""
import re, sys
from pathlib import Path

DESIGN = Path(__file__).parent

def static_asserts():
    frames = sorted(DESIGN.glob("frames/[0-9]*.html"))
    report = []
    for f in frames:
        t = f.read_text(encoding="utf-8")
        # 'transform:' intentionally omitted — text-transform false-positives
        bad = [x for x in ["var(", "<use", "<symbol", "rgba(", "position:absolute",
                           "position:fixed", "<a "] if x in t]
        ok = (not bad) and "width:390px;height:844px" in t
        report.append((f.name, ok, bad))
    return report

def main():
    rep = static_asserts()
    bad_static = [r for r in rep if not r[1]]
    for name, ok, bad in rep:
        if not ok:
            print(f"STATIC BAD {name}: {bad}")
    if bad_static:
        sys.exit(1)
    print(f"static: {len(rep)}/{len(rep)} frames import-safe")

    from playwright.sync_api import sync_playwright
    order = [l.strip() for l in (DESIGN / "frames/order.txt").read_text().splitlines()
             if l.strip() and not l.strip().startswith("#")]
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 420, "height": 900})
        for name in order:
            pg.goto(f"file://{DESIGN}/frames/{name}.html")
            pg.wait_for_timeout(60)
            r = pg.evaluate("""() => {
              const f = document.querySelector('.frame');
              if (!f) return {err: 'no .frame'};
              const fr = f.getBoundingClientRect();
              let maxR = 0, maxB = 0, minL = 9999;
              const walk = (el) => {
                for (const c of el.children) {
                  const r = c.getBoundingClientRect();
                  if (r.width > 0 && r.height > 0) {
                    maxR = Math.max(maxR, r.right); maxB = Math.max(maxB, r.bottom);
                    minL = Math.min(minL, r.left);
                  }
                  walk(c);
                }
              };
              walk(f);
              // .frame scrollHeight, NOT document.scrollHeight — the viewport
              // pollutes the document metric (false 900s on every frame)
              return {x: fr.x, w: fr.width, h: fr.height,
                      sh: f.scrollHeight,
                      maxR: Math.round(maxR), maxB: Math.round(maxB), minL: Math.round(minL),
                      fill: Math.round((maxB - fr.y) / 844 * 100) / 100};
            }""")
            issues = []
            if "err" in r: issues.append(r["err"])
            else:
                if abs(r["w"] - 390) > 1 or abs(r["h"] - 844) > 1: issues.append(f"rect {r['w']}x{r['h']}")
                if abs(r["x"]) > 1: issues.append(f"frame x={r['x']}")
                if r["sh"] > 860: issues.append(f"scrollHeight {r['sh']}")
                if r["maxR"] > 391: issues.append(f"h-overflow right={r['maxR']}")
                if r["maxB"] > 845: issues.append(f"v-overflow bottom={r['maxB']}")
                if r["fill"] < 0.80: issues.append(f"fill {r['fill']}")
            results.append((name, issues))
        b.close()
    ok = [n for n, i in results if not i]
    for n, i in results:
        if i: print(f"GEO BAD {n}: {i}")
    print(f"geometry: {len(ok)}/{len(results)} frames clean")

if __name__ == "__main__":
    main()
