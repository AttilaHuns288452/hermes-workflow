#!/usr/bin/env python3
"""Merge a folder of standalone mobile-UI frames (NN_*.html) into ONE importable HTML.

Safe ONLY when every frame is pure static flow (no position:absolute/transform
overlays, no rgba scrims) — see mobile-ui-figma-handoff SKILL.md.

Usage: python merge_frames.py <src_dir> <out.html>

Verifies (exits non-zero on failure):
  - frame count == label count
  - every frame exactly 390x844 and y-sequential
  - zero x-overflow inside any frame
  - every <use href="#..."> resolves to a unique <symbol id>
"""
import re, sys, os

def css_blocks(html):
    return re.findall(r"<style>.*?</style>", html, re.S)

def sprite(html):
    m = re.search(r"<svg[^>]*>\s*<defs>.*?</defs>\s*</svg>", html, re.S)
    return m.group(0) if m else ""

def frame_div(html):
    m = re.search(r'<div class="frame".*?</div>\s*</body>', html, re.S)
    if not m:
        sys.exit(f"no .frame div found in {html[:60]!r}")
    return m.group(0)

def label_for(fname):
    stem = fname[:-5]
    num, _, rest = stem.partition("_")
    return f"{num} · {rest.replace('_', ' ')}"

def main():
    if len(sys.argv) != 3:
        sys.exit("usage: merge_frames.py <src_dir> <out.html>")
    src, out = sys.argv[1], sys.argv[2]
    files = sorted(f for f in os.listdir(src)
                   if re.match(r"^\d{2}_", f) and f.endswith(".html"))
    if not files:
        sys.exit(f"no NN_*.html files in {src}")

    first = open(os.path.join(src, files[0]), encoding="utf-8").read()
    css = "\n".join(css_blocks(first))
    sp = sprite(first)

    extra = """
<style>
    .board { width: fit-content; margin: 24px auto 48px; display: flex; flex-direction: column; align-items: flex-start; }
    .frame-label { font-family: -apple-system, 'Segoe UI', Roboto, Arial, sans-serif; font-size: 12px; font-weight: 600; color: #64748b; margin: 20px 0 6px; }
</style>
"""

    parts = []
    for f in files:
        html = open(os.path.join(src, f), encoding="utf-8").read()
        parts.append(f'<div class="frame-label">{label_for(f)}</div>')
        parts.append(frame_div(html))

    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Merged frames</title>
{css}
{extra}
</head>
<body>
{sp}
<div class="board">
{chr(10).join(parts)}
</div>
</body>
</html>"""

    with open(out, "w", encoding="utf-8") as fh:
        fh.write(doc)

    # ---- static verification (no browser needed) ----
    n_labels = doc.count('class="frame-label"')
    n_frames = len(re.findall(r'<div class="frame[ >"]', doc.replace('class="frame-label"', '')))
    ids = set(re.findall(r'<symbol id="([^"]+)"', doc))
    uses = set(re.findall(r'<use href="#([^"]+)"', doc))
    missing = sorted(u for u in uses if u not in ids)
    assert n_labels == len(files) == n_frames, f"count mismatch: labels={n_labels} frames={n_frames} files={len(files)}"
    assert not missing, f"unresolved use refs: {missing}"
    print(f"merged {n_frames} frames -> {out} ({os.path.getsize(out)} bytes); "
          f"labels {n_labels}, symbols {len(ids)}, use refs OK")

    # Browser-side checks (frame size/sequence/x-overflow) are done by
    # scripts/fitcheck.js + verify_merged.js in this skill's scripts dir.

if __name__ == "__main__":
    main()
