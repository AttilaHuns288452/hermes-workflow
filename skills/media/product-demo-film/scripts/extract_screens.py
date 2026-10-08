#!/usr/bin/env python3
"""Screen extractor for design-export PDFs (Figma exports, decks).
Usage: python3 extract_screens.py <file.pdf> <out_dir> <page> [<page> ...]
Renders each page at 300 dpi, crops to non-white content (+12px margin),
normalizes names to pNNN.png. Requires: pdftoppm, Pillow."""
import subprocess, sys, os, glob
from PIL import Image, ImageChops

pdf, outdir = sys.argv[1], sys.argv[2]
pages = [int(p) for p in sys.argv[3:]]
os.makedirs(outdir, exist_ok=True)
tmp = '/tmp/extract_screens'
os.makedirs(tmp, exist_ok=True)
for p in pages:
    subprocess.run(['pdftoppm', '-f', str(p), '-l', str(p), '-r', '300', '-png',
                    pdf, f'{tmp}/p{p:03d}'], check=True)
    f = glob.glob(f'{tmp}/p{p:03d}-*.png')[0]
    im = Image.open(f).convert('RGB')
    bg = Image.new('RGB', im.size, (255, 255, 255))
    b = ImageChops.difference(im, bg).getbbox()
    if b:
        m = 12
        b = (max(0, b[0]-m), max(0, b[1]-m), min(im.width, b[2]+m), min(im.height, b[3]+m))
        im = im.crop(b)
    out = os.path.join(outdir, f'p{p:03d}.png')
    im.save(out)
    print(out, im.size)
