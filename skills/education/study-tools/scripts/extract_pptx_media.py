#!/usr/bin/env python3
"""Extract slide images from a PPTX in slide order — stdlib only.

Built for image-only decks (slides exported as screenshots) where text
extraction yields nothing: read the slide rels, pull each slide's image,
write slideNN.<ext> into outdir in slide order.

Usage: python3 extract_pptx_media.py deck.pptx outdir/
"""
import zipfile, re, os, sys
from xml.etree import ElementTree as ET


def extract(pptx_path, outdir):
    os.makedirs(outdir, exist_ok=True)
    z = zipfile.ZipFile(pptx_path)
    n = 0
    for name in sorted(z.namelist()):
        m = re.match(r'ppt/slides/slide(\d+)\.xml$', name)
        if not m:
            continue
        idx = int(m.group(1))
        rel = f'ppt/slides/_rels/slide{idx}.xml.rels'
        img = None
        if rel in z.namelist():
            for rel_el in ET.fromstring(z.read(rel)):
                if rel_el.get('Type', '').endswith('/image'):
                    target = rel_el.get('Target', '').replace('../media/', 'ppt/media/')
                    if target in z.namelist():
                        img = target
                        break
        if img:
            n += 1
            ext = os.path.splitext(img)[1]
            with z.open(img) as src, open(os.path.join(outdir, f'slide{idx:02d}{ext}'), 'wb') as dst:
                dst.write(src.read())
    print(f'{n} slide images -> {outdir}')
    return n


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    extract(sys.argv[1], sys.argv[2])
