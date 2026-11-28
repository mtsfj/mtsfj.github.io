#!/usr/bin/env python3
"""The oden's bench lamp switched off with the oden: its light as the unlit street has it, across the oden zone's edge.

    python3 tools/oden_bench_lamp.py       writes assets/oden_bench_off.webp (the same bytes each time)

The small lamp under its green shade over the oden's bench (between the drinks machines' canopy and the oden's front, its
warm pool on the wall, the bench, the flower pot and the step) is painted lit in the street's layer. When the oden shuts
(1 h) street.js lays the unlit street over the oden's zone (x 378-524): the right third of the pool went dark with it and
the rest stayed lit, cut along x 378, the lamp on all night. This picture is the lamp's light gone out: every pixel of
x 352-400, y 576-700 (across the zone's soft edge, 6 px each way, where the zone's unlit picture is only partly laid) that
the lamp lights (the lit and the unlit layers more than 3 apart, their sum), the unlit layer's there (alpha 255), nothing
elsewhere (the machines' own light, left of x 352, is not the lamp's). street.js shows it as the oden's zone shuts, at
the same level, so the whole lamp and its pool go out together. Needs numpy and Pillow.
"""
import os
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOX = (352, 576, 400, 700)                    # x0, y0, x1, y1: the lamp's light, to past the oden zone's soft edges (x 378, y 692, 6 px)
OUT = os.path.join(ROOT, 'assets', 'oden_bench_off.webp')


def main():
    city = np.array(Image.open(os.path.join(ROOT, 'assets', 'layer_city_off.webp')).convert('RGB')).astype(int)
    unlit = np.array(Image.open(os.path.join(ROOT, 'assets', 'street_unlit.webp')).convert('RGB')).astype(int)
    x0, y0, x1, y1 = BOX
    c, u = city[y0:y1, x0:x1], unlit[y0:y1, x0:x1]
    lit = np.abs(c - u).sum(2) > 3
    rgba = np.zeros((y1 - y0, x1 - x0, 4), np.uint8)
    rgba[..., :3] = u.astype(np.uint8); rgba[..., 3] = np.where(lit, 255, 0)
    Image.fromarray(rgba).save(OUT, lossless=True, quality=100, method=6, exact=True)
    print('wrote', OUT, int(lit.sum()), 'px')


if __name__ == '__main__':
    main()
