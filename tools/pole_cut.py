#!/usr/bin/env python3
"""The utility pole on the right sidewalk: cut shorter, just under its transformer (which goes), its top finished.

    python3 tools/pole_cut.py      (once; it reads and writes the street's layers as they are)

The pole ran out of the frame at the top, its transformer hung on its left (x 988-1027, y 0-57, its brackets to 64),
its top a dark block of hardware down to y 88. It now ends at TOP, where the transformer hung, 8 px over the roof line of
the house on its right (y 66): only sky above it and beside it there, nothing to invent behind it. Its top: a cap, one
pixel wider than the pole on each side, 4 rows, shaded as the pole is (its lit left edge, its red rim) but a shade flatter,
its upper corners rounded, a dark line of shadow under its lip; under that, the pole's own cylinder, its rows further down
(100..) copied up, so its edges, its lit left side and its rim from the shops run on unbroken to the cap. In
layer_city_off, street_unlit, night_far and street_sun, each from the same source pixel (the morning sun on its rim
with it); what goes is the sky in all four (transparent, 0). The pole's occlusion for what moves behind it (COCC in
assets/street.js) starts at TOP too. Needs Pillow, numpy.
"""
import json
import os
import re
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = lambda p: os.path.join(ROOT, 'assets', p)
X0, X1 = 1025, 1063                  # the pole's columns (its lit left edge .. its rim)
TOP = 58                             # its new top (the transformer's foot)
CAP = 4                              # the cap's rows
SRC = 100                            # the pole's clean rows, copied up from here
JOIN = 92                            # the first row of the pole left as it is
TRANSFO = (988, 0, 1064, 66)         # the transformer, its brackets, the hardware above the house's roof (x0, y0, x1, y1)


def load(p, mode='RGBA'):
    return np.asarray(Image.open(A(p)).convert(mode)).astype(float)


def save(arr, p, mode):
    Image.fromarray(np.clip(np.round(arr), 0, 255).astype(np.uint8), mode).save(A(p), 'WEBP', lossless=True, quality=100, method=6, exact=True)


def main():
    L = [load('layer_city_off.webp'), load('street_unlit.webp'), load('night_far.webp', 'RGB'), load('street_sun.webp', 'RGB')]
    src = [l.copy() for l in L]
    # the transformer, its brackets, the pole's hardware down to the new top, its old block down to JOIN: the sky
    x0, y0, x1, y1 = TRANSFO
    for l in L:
        l[y0:y1, x0:x1 + 1] = 0; l[:JOIN, X0 - 1:X1 + 1] = 0                       # (not the house's lit edge, x 1064)
    # the cylinder, from the cap down to where the pole is left as it is: its own clean rows copied up
    for y in range(TOP + CAP, JOIN):
        for l, s in zip(L, src): l[y, X0:X1 + 1] = s[SRC + y - (TOP + CAP), X0:X1 + 1]
    # the cap: the cylinder's profile a shade flatter, one pixel wider each side, its upper corners rounded
    for l, s in zip(L[:2], src[:2]):
        prof = s[SRC, X0:X1 + 1, :3]
        flat = prof * 0.8 + prof.mean(0) * 0.2
        flat = np.vstack([flat[:1] * 0.85, flat, flat[-1:] * 0.85])                  # (its lip, each side)
        for k in range(CAP):
            row = flat * (0.9 if k == 0 else 1.0)                                   # (its top edge, against the sky)
            l[TOP + k, X0 - 1:X1 + 2, :3] = row; l[TOP + k, X0 - 1:X1 + 2, 3] = 255
        for x in (X0 - 1, X1 + 1): l[TOP, x] = 0                                     # (its corners, rounded)
        for x in (X0, X1): l[TOP, x, 3] = 150
        y = TOP + CAP                                                                # (the shadow under its lip)
        l[y, X0:X1 + 1, :3] = l[y, X0:X1 + 1, :3] * 0.45
    for l, s in zip(L[2:], src[2:]):                                                 # (the cap's lips take the pole's edges')
        row = np.vstack([s[SRC, X0:X0 + 1], s[SRC, X0:X1 + 1], s[SRC, X1:X1 + 1]])
        for k in range(1, CAP): l[TOP + k, X0 - 1:X1 + 2] = row
        l[TOP, X0:X1 + 1] = row[1:-1]
    save(L[0], 'layer_city_off.webp', 'RGBA'); save(L[1], 'street_unlit.webp', 'RGBA')
    save(L[2], 'night_far.webp', 'RGB'); save(L[3], 'street_sun.webp', 'RGB')
    # the pole's occlusion: from its new top only
    p = A('street.js'); s = open(p, encoding='utf-8').read()
    m = re.search(r'const COCC = (\{.*?\});', s); C = json.loads(m.group(1))
    runs = [[max(a, TOP), b, c, d] for a, b, c, d in C['pole']['runs'] if b >= TOP]
    C['pole']['runs'] = runs
    s = s[:m.start(1)] + json.dumps(C, separators=(',', ':')) + s[m.end(1):]
    open(p, 'w', encoding='utf-8').write(s)
    print('pole top at', TOP, '| occlusion runs', len(runs))


if __name__ == '__main__':
    main()
