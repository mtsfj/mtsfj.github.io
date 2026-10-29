#!/usr/bin/env python3
"""PNG -> WebP lossless, pixel for pixel (the colours under the transparent pixels kept too: exact).

    python3 tools/png2webp.py                    every PNG of assets/ that the site uses
    python3 tools/png2webp.py assets/x.png ...   only these (a sprite just made by a generator)

Each image is encoded at the format's highest effort, decoded again and compared with the PNG; only an identical and
smaller WebP replaces it: its references in the site's files go from x.png to x.webp (their ?v= kept), the PNG is removed.
16-bit PNGs and those carrying a colour profile or a gamma are left alone (the browser may not show them the same), and so
are the images the page draws into a 2D canvas (KEEP_PNG below): there Chrome premultiplies a WebP's half-transparent pixels
with another rounding than a PNG's (in WebGL, the street's own path, both are read the same, pixel for pixel).
Needs Pillow (pip install pillow). The site's icons and sharing image (favicon.png, apple-touch-icon.png, og.png) stay PNG.
"""
import os, re, struct, sys
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_JS = {'three.min.js', 'OrbitControls.js'}
KEEP_PNG = {'arcade_sill', 'battlebus_36', 'battlebus_42', 'battlebus_48', 'jugg_drink', 'speed_drink', 'tap_drink', 'mars_disc'}


def site_files():
    for d, _, fs in os.walk(ROOT):
        if '/.git' in d or d.endswith('/tools'):
            continue
        for f in fs:
            if f in SKIP_JS:
                continue
            if f.endswith(('.html', '.js', '.css', '.md', '.xml', '.webmanifest', '.json')):
                yield os.path.join(d, f)


def plain(path):                                   # 8 bits a channel, no colour profile, no gamma
    b = open(path, 'rb').read()
    if b[:8] != b'\x89PNG\r\n\x1a\n' or b[24] > 8:
        return False
    i = 8
    while i < len(b):
        n, = struct.unpack('>I', b[i:i + 4]); t = b[i + 4:i + 8]
        if t in (b'iCCP', b'gAMA', b'cHRM', b'sRGB', b'cICP'):
            return False
        i += 12 + n
    return True


def convert(png):
    im = Image.open(png); im.load()
    rgba = np.asarray(im.convert('RGBA'))
    out = png[:-4] + '.webp'
    im.save(out, 'WEBP', lossless=True, quality=100, method=6, exact=True)
    back = Image.open(out); back.load()
    if back.size != im.size or not np.array_equal(np.asarray(back.convert('RGBA')), rgba) or os.path.getsize(out) >= os.path.getsize(png):
        os.remove(out)
        return None
    return out


def main():
    files = list(site_files())
    texts = {f: open(f, encoding='utf-8').read() for f in files}
    pngs = sys.argv[1:] or sorted(os.path.join('assets', f) for f in os.listdir(os.path.join(ROOT, 'assets')) if f.endswith('.png'))
    saved = 0
    for rel in pngs:
        png = os.path.join(ROOT, rel); name = os.path.basename(png)[:-4]
        pat = re.compile(r'(?<![A-Za-z0-9_.-])' + re.escape(name) + r'\.png\b')
        users = [f for f, t in texts.items() if pat.search(t)]
        if not users:
            print('  unused, left  ', rel); continue
        if name in KEEP_PNG:
            print('  2D canvas, left', rel); continue
        if not plain(png):
            print('  not plain, left', rel); continue
        out = convert(png)
        if not out:
            print('  no gain, left ', rel); continue
        a, b = os.path.getsize(png), os.path.getsize(out); saved += a - b
        for f in users:
            texts[f] = pat.sub(name + '.webp', texts[f])
            open(f, 'w', encoding='utf-8').write(texts[f])
        os.remove(png)
        print(f'{a // 1024:6d} K -> {b // 1024:5d} K  {rel}  ({len(users)} file{"s" if len(users) > 1 else ""})')
    print(f'saved {saved // 1024} K')


if __name__ == '__main__':
    main()
