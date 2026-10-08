#!/usr/bin/env python3
"""Draw callout labels + leader lines + wiring legend onto a Blender render.

Usage:
  python3 annotate_render.py render.png out.png anchors.json \
      [--crop x0,y0,x1,y1] [--scale 1.5] [--legend legend.json]

anchors.json: {"LABEL TEXT": [x_px, y_px], ...}  (pixels in the ORIGINAL image)
legend.json:  {"Legend entry": [r, g, b], ...}   (optional, drawn as a bottom bar)

Anchor pixels come from Blender:
  from bpy_extras.object_utils import world_to_camera_view as w2c
  co = w2c(scene, camera, Vector((x, y, z)))
  px, py = round(co.x * W), round((1 - co.y) * H)
Re-project after ANY camera or exposure change.
"""
import json
import sys
from PIL import Image, ImageDraw, ImageFont


def load_font(size, bold=True):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    try:
        return ImageFont.truetype(f"/usr/share/fonts/truetype/dejavu/{name}", size)
    except Exception:
        return ImageFont.load_default()


def main():
    args = sys.argv[1:]
    src, dst, anchors_path = args[0], args[1], args[2]
    crop, scale, legend_path = None, 1.5, None
    i = 3
    while i < len(args):
        if args[i] == "--crop":
            crop = tuple(int(v) for v in args[i + 1].split(","))
            i += 2
        elif args[i] == "--scale":
            scale = float(args[i + 1])
            i += 2
        elif args[i] == "--legend":
            legend_path = args[i + 1]
            i += 2
        else:
            i += 1

    im = Image.open(src).convert("RGB")
    pts = {k: list(map(int, v)) for k, v in json.load(open(anchors_path)).items()}
    if crop:
        im = im.crop(crop)
        pts = {k: [round((v[0] - crop[0]) * scale), round((v[1] - crop[1]) * scale)]
               for k, v in pts.items()}
    if scale != 1.0:
        im = im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)

    W, H = im.size
    d = ImageDraw.Draw(im)
    font = load_font(24)
    LINE, CHIP, TXT = (50, 50, 58), (15, 15, 19), (255, 255, 255)
    mid = W / 2

    def chip_box(text, cx, cy):
        bb = d.textbbox((0, 0), text, font=font)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        return cx - (tw + 26) // 2, cy - (th + 18) // 2, cx + (tw + 26) // 2, cy + (th + 18) // 2

    left = sorted([(k, 250) for k, p in pts.items() if p[0] <= mid], key=lambda t: pts[t[0]][1])
    right = sorted([(k, W - 250) for k, p in pts.items() if p[0] > mid], key=lambda t: pts[t[0]][1])
    rows = {"left": [90 + 140 * n for n in range(len(left))],
            "right": [90 + 140 * n for n in range(len(right))]}
    layout = []
    for col, key in ((left, "left"), (right, "right")):
        for (text, cx), cy in zip(col, rows[key]):
            layout.append((text, cx, cy))

    for text, cx, cy in layout:
        ax, ay = pts[text]
        x0, y0, x1, y1 = chip_box(text, cx, cy)
        sx = x1 if cx < mid else x0  # start line past the chip edge, not through the text
        d.line([(sx, cy), (ax, ay)], fill=LINE, width=3)
    for text, cx, cy in layout:
        ax, ay = pts[text]
        d.ellipse([ax - 7, ay - 7, ax + 7, ay + 7], outline=(28, 28, 33), width=3)
    for text, cx, cy in layout:
        x0, y0, x1, y1 = chip_box(text, cx, cy)
        d.rounded_rectangle([x0, y0, x1, y1], radius=9, fill=CHIP, outline=(140, 140, 148), width=1)
        bb = d.textbbox((0, 0), text, font=font)
        d.text((cx - (bb[2] - bb[0]) // 2 - bb[0], cy - (bb[3] - bb[1]) // 2 - bb[1]),
               text, font=font, fill=TXT)

    if legend_path:
        legend = json.load(open(legend_path))
        lf = load_font(17, bold=False)
        ly = H - 34
        lx = 24
        d.rounded_rectangle([10, ly - 26, W - 10, ly + 18], radius=8, fill=(14, 14, 18))
        for name, col in legend.items():
            d.ellipse([lx, ly - 10, lx + 17, ly + 7], fill=tuple(col), outline=(100, 100, 105))
            d.text((lx + 23, ly - 12), name, font=lf, fill=(240, 240, 245))
            lx += 232

    im.save(dst)
    print(f"saved {dst} ({im.size[0]}x{im.size[1]}, {len(layout)} labels)")


if __name__ == "__main__":
    main()
