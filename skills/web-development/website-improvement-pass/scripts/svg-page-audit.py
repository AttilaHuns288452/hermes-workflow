#!/usr/bin/env python3
"""SVG text / page-integrity audit for static promo sites.

Serves a repo dir on a throwaway local port, loads each page at desktop
and mobile widths, and fails on: any SVG <text> escaping its viewBox
(the clipped-label class of bug), horizontal overflow, broken <img>,
or console errors. Exit 1 on any finding.

Usage: python3 svg-page-audit.py [repo_dir] [page ...]
       Defaults: cwd, every top-level *.html.
"""
import functools
import http.server
import pathlib
import socketserver
import sys
import threading

from playwright.sync_api import sync_playwright

JS = """() => ({
    svgBad: [...new Set([...document.querySelectorAll('svg text')]
      .filter(tx => { const vb = tx.ownerSVGElement.viewBox.baseVal;
                      if (!vb.width) return false;
                      const bb = tx.getBBox();
                      return bb.x + bb.width > vb.width + 0.5 || bb.x < -0.5; })
      .map(t => t.textContent.trim().slice(0, 30))),
    ov: document.documentElement.scrollWidth > document.documentElement.clientWidth,
    broken: [...document.images].filter(i => !(i.complete && i.naturalWidth > 0)).length })"""


def audit(root: pathlib.Path, pages, port=8840):
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(root))
    for candidate in range(port, port + 10):
        try:
            httpd = socketserver.TCPServer(("127.0.0.1", candidate), handler)
            break
        except OSError:
            continue
    else:
        raise SystemExit("no free port in range")
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    findings = []
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            for vw, vh, label in [(1280, 800, "desktop"), (390, 844, "mobile")]:
                pg = b.new_page(viewport={"width": vw, "height": vh})
                errs = []
                pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
                for page in pages:
                    errs.clear()
                    pg.goto(f"http://127.0.0.1:{candidate}/{page}", wait_until="networkidle")
                    pg.wait_for_timeout(250)
                    d = pg.evaluate(JS)
                    if d["svgBad"]:
                        findings.append(f"{label}:{page} svg-text overflow: {d['svgBad']}")
                    if d["ov"]:
                        findings.append(f"{label}:{page} horizontal overflow")
                    if d["broken"]:
                        findings.append(f"{label}:{page} broken images: {d['broken']}")
                    if errs:
                        findings.append(f"{label}:{page} console errors: {errs[:3]}")
                pg.close()
            b.close()
    finally:
        httpd.shutdown()
    return findings


if __name__ == "__main__":
    root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    pages = sys.argv[2:] or sorted(p.name for p in root.glob("*.html"))
    f = audit(root, pages)
    print("\n".join(f) if f else f"PASS: {len(pages)} pages x 2 viewports clean")
    sys.exit(1 if f else 0)
