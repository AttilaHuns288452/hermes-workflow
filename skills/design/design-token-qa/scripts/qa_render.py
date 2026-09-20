#!/usr/bin/env python3
"""Render sanity: screenshot each 390x844 frame, assert non-blank (ink + variance),
and save COLOR copies for pixel-token verification. Grayscale is computed on a
separate convert — saving the L-copy strips color from the file.
Run: python3 qa_render.py (writes qa_shots/NN_Name.png next to frames/)"""
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image
import io

DESIGN = Path(__file__).parent
order = [l.strip() for l in (DESIGN / "frames/order.txt").read_text().splitlines()
         if l.strip() and not l.strip().startswith("#")]
shots = DESIGN / "qa_shots"
shots.mkdir(exist_ok=True)

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 420, "height": 900})
    bad = []
    for name in order:
        pg.goto(f"file://{DESIGN}/frames/{name}.html")
        pg.wait_for_timeout(50)
        png = pg.screenshot(clip={"x": 0, "y": 0, "width": 390, "height": 844})
        rgb = Image.open(io.BytesIO(png)).convert("RGB")  # save THIS
        im = rgb.convert("L")                             # metric on a copy
        hist = im.histogram()
        total = sum(hist)
        ink = sum(hist[:200]) / total
        var = (sum((i - 128) ** 2 * c for i, c in enumerate(hist)) / total) ** 0.5
        if ink < 0.02 or var < 10:
            bad.append((name, round(ink, 3), round(var, 1)))
        rgb.save(shots / f"{name}.png")
    b.close()

print(f"render: {len(order) - len(bad)}/{len(order)} frames non-blank")
for n, i, v in bad:
    print(f"BLANK? {n} ink={i} var={v}")
