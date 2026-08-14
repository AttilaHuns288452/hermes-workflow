#!/usr/bin/env python3
"""Split an OpenDesign-style single-file board (all frames in ONE html) into
standalone NN_Name.html frames, ready for scripts/merge_frames.py.

Usage: python split_board.py <board.html> <out_dir>

Splits on `<!-- NN · name -->` frame-marker comments, extracts each frame div
with a balanced-div scan, derives file names from the comment text, and writes
full standalone pages (shared <style> blocks + one frame each).
"""
import re, os, sys


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: split_board.py <board.html> <out_dir>")
    src, out_dir = sys.argv[1], sys.argv[2]
    html = open(src, encoding="utf-8").read()
    css = "".join(re.findall(r"<style>.*?</style>", html, re.S))
    body = html.split("<body>", 1)[1].rsplit("</body>", 1)[0]

    # chunks = [pre, num1, name1, body1, num2, name2, body2, ...]
    chunks = re.split(r"\n\s*<!--\s*(\d+)\s*·\s*([^\n]*?)\s*-->", body)
    frames = []
    for i in range(1, len(chunks), 3):
        num, name, chunk = chunks[i], chunks[i + 1], chunks[i + 2]
        start = chunk.find('<div class="frame"')
        if start < 0:
            sys.exit(f"frame {num}: no <div class=\"frame\"> after marker comment")
        depth, j = 0, start
        while j < len(chunk):
            if chunk.startswith("<div", j):
                depth += 1
            elif chunk.startswith("</div>", j):
                depth -= 1
                if depth == 0:
                    break
            j += 1
        frames.append((num, name, chunk[start:j + 6]))

    os.makedirs(out_dir, exist_ok=True)
    safe = lambda s: re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_")
    for num, name, frame in frames:
        fname = f"{int(num):02d}_{safe(name)}.html"
        doc = (f'<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="UTF-8">\n'
               f'<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
               f'<title>{name}</title>\n{css}\n</head>\n<body>\n{frame}\n</body>\n</html>')
        open(os.path.join(out_dir, fname), "w", encoding="utf-8").write(doc)
    print(f"split {len(frames)} frames -> {out_dir}")


if __name__ == "__main__":
    main()
