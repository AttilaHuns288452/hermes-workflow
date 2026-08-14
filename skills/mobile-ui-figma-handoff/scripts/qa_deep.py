#!/usr/bin/env python3
"""Deep QA for generated frames: squished buttons, x-overflow, body overflow, voids.

Run: python qa_deep.py [frames_dir] [NN prefixes...]
Defaults: frames_dir = ./frames, all frames.
Exit code = number of frames with issues. Uses global Python (needs playwright):
  "C:/Users/YOUR_USERNAME/AppData/Local/Programs/Python/Python311/python.exe" qa_deep.py
(plain `python` may resolve to a venv without playwright — PYTHONPATH leak quirk.)
"""
import glob, os, sys
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
frames_dir = os.path.join(os.path.dirname(HERE), "frames")
prefixes = []
for a in sys.argv[1:]:
    if a[:2].isdigit():
        prefixes.append(a)
    else:
        frames_dir = a
files = sorted(glob.glob(os.path.join(frames_dir, "*.html")))
if prefixes:
    files = [f for f in files if os.path.basename(f)[:2] in prefixes]

issues = 0
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 500, "height": 20000})
    for f in files:
        name = os.path.basename(f)[:-5]
        pg.goto("file:///" + f.replace("\\", "/"))
        g = pg.evaluate("""() => {
            const fr = document.querySelector('.frame').getBoundingClientRect();
            let squish = [], xOver = 0;
            document.querySelectorAll('.btn, .slot, input, .icon-btn, .send, .tgl').forEach(el => {
                const r = el.getBoundingClientRect();
                if (r.height < 34 && String(el.className).includes('btn'))
                    squish.push(el.textContent.trim().slice(0,20) + ':' + Math.round(r.height));
                if (r.right > fr.right + 1) xOver = Math.max(xOver, Math.round(r.right - fr.right));
            });
            const body = document.querySelector('.body');
            const kids = [...body.children];
            const last = kids[kids.length-1].getBoundingClientRect();
            const nav = document.querySelector('.nav');
            const nb = nav ? nav.getBoundingClientRect() : null;
            return {squish, xOver,
                    bodyOver: body.scrollHeight - body.clientHeight,
                    void: Math.round((nb ? nb.top : 844) - last.bottom)};
        }""")
        bad = g["squish"] or g["xOver"] or g["bodyOver"] > 0 or g["void"] > 140
        if bad:
            issues += 1
            print(f"{name}: squish={g['squish']} xOver={g['xOver']} "
                  f"bodyOver={g['bodyOver']} void={g['void']}")
    print(f"\nchecked {len(files)} frames, {issues} with issues")
    b.close()
sys.exit(1 if issues else 0)
