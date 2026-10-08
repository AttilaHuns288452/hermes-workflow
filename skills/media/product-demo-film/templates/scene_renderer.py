#!/usr/bin/env python3
"""Render ONE scene of a self-contained GSAP sub-composition to PNG frames.

Core of the product-demo-film "scene-level splice" revision flow: when one
card's copy changed after a full render, render ONLY that scene here and
frame-exact splice the frames into the delivered master (see SKILL.md).

Usage: scene_renderer.py <scene_id> <duration_s> [fps=30]
Expected layout (adapt paths):
  compositions/<scene_id>.html  self-contained scene: own <style>, own script
                                that saves its GSAP timeline to window.__tl
  gsap.min.js                   local GSAP copy beside this script
  frames/seg_<scene_id>/f%05d.png  output

Three validated traps are encoded below - do not simplify them away:
1. fetch() of local files under file:// is CORS-blocked in Chromium, so the
   scene source and gsap are INLINED into the harness HTML as JSON strings.
2. A literal </script> in an inlined payload terminates the harness script
   block: escape "</" -> "<\\/" in every payload, computed OUTSIDE the
   f-string (Python 3.11 f-strings cannot contain backslashes in expressions).
3. wait_for_function must assert a BOOLEAN (!!window.__tl): asserting the GSAP
   timeline object itself hangs forever - it cannot serialize to the driver.
"""
import json
import os
import shutil
import sys

from playwright.sync_api import sync_playwright


def js_payload(text):
    return json.dumps(text).replace("</", "<\\/")


def main():
    scene_id = sys.argv[1]
    dur_s = float(sys.argv[2])
    fps = int(sys.argv[3]) if len(sys.argv) > 3 else 30
    here = os.path.dirname(os.path.abspath(__file__))

    with open(os.path.join(here, "compositions", scene_id + ".html"), encoding="utf-8") as fh:
        scene_src = fh.read()
    with open(os.path.join(here, "gsap.min.js"), encoding="utf-8") as fh:
        gsap_src = fh.read()

    out = os.path.join(here, "frames", "seg_" + scene_id)
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)

    scene_js = js_payload(scene_src)   # outside the f-string (trap 2)
    gsap_js = js_payload(gsap_src)
    harness = f"""<!doctype html><html><head><meta charset="utf-8"><style>
html,body{{margin:0;padding:0;background:#06090e;overflow:hidden}}
#scene{{width:1920px;height:1080px;position:relative;overflow:hidden}}
</style></head><body>
<div id="scene"></div>
<script>{gsap_js}</script>
<script>
const SCENE_SRC = {scene_js};
const host = document.getElementById('scene');
host.innerHTML = SCENE_SRC.replace(/<script\\b[^>]*>[\\s\\S]*?<\\/script>/gi, '');
for (const tag of (SCENE_SRC.match(/<script\\b[^>]*>[\\s\\S]*?<\\/script>/gi) || [])) {{
  window.eval(tag.replace(/^<script\\b[^>]*>/i, '').replace(/<\\/script>$/i, ''));
}}
</script></body></html>"""
    hp = os.path.join(here, "_harness_" + scene_id + ".html")
    with open(hp, "w", encoding="utf-8") as fh:
        fh.write(harness)

    n = round(dur_s * fps)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        page.goto("file://" + hp)
        page.wait_for_function("!!window.__tl", timeout=30000)  # trap 3
        for i in range(n):
            page.evaluate("t => window.__tl.pause(t)", i / fps)
            page.screenshot(path=os.path.join(out, "f%05d.png" % i))
        browser.close()
    os.remove(hp)
    print("frames:", n, "->", out)


if __name__ == "__main__":
    main()
