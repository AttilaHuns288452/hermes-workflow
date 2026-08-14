#!/usr/bin/env python3
# Normalize every standalone frame: keep head + balanced frame div ONLY,
# dropping trailing wrapper closers that corrupt the merged board DOM.
# Run BEFORE merge_frames.py on any externally-exported frame set (OpenDesign
# files end "</div></div></div></body>"; the lazy frame_div regex slurps the
# strays and one frame swallows the rest of the board).
#
# Usage: python normalize_frames.py <frames_dir>
import glob, os, re, sys

d = sys.argv[1] if len(sys.argv) > 1 else "."
for path in sorted(glob.glob(os.path.join(d, "*.html"))):
    html = open(path, encoding="utf-8").read()
    head, _, rest = html.partition('<div class="frame"')
    if not rest:
        print("skip", os.path.basename(path)); continue
    depth = 1
    i = 0
    for m in re.finditer(r"<div|</div>", rest):
        if m.group() == "<div":
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                i = m.end()
                break
    if depth != 0:
        print("UNBALANCED", os.path.basename(path), "depth", depth)
        print("  -> append the missing </div> before </body>, then re-run")
        continue
    doc = head + '<div class="frame"' + rest[:i] + "\n</body>\n</html>\n"
    open(path, "w", encoding="utf-8").write(doc)
    print("normalized", os.path.basename(path))
print("done")
