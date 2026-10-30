#!/usr/bin/env python3
"""The utility pole on the right sidewalk: cut shorter, just under its transformer (which goes), its top capped.

    python3 tools/pole_cut.py      (once; it reads and writes the street's layers as they are)

The pole ran out of the frame at the top, its transformer hung on its left (x 988-1027, y 0-57, its brackets to 64),
its top a dark block of hardware down to y 88. It now ends under where the transformer hung, a little over the roof of
the house on its right (y 66): only sky above and beside it there, nothing to invent behind it. Its top is the cap the
concrete poles wear: a short sleeve one pixel wider than the pole each side (LIP rows), a low dome over it (DOME rows),
a line of shadow under the sleeve. Each pixel of the cap is shaded from its normal: round its axis as the pole is (its
lit left edge, its dark body, its rim from the shops' red), from above by the sky (blue, lighter on the left where the
pole's light comes from), its outline on the sky by coverage. Under it, the pole's own cylinder: its clean rows from just
under the band at JOIN (rows 92-94, left as they are) copied up, so the band reads as a band, the same pole on both
sides; the rim's red, which grows toward the street, fading upward as it does down the pole. In layer_city_off,
street_unlit (each from its own pixels), night_far (0, the street's) and street_sun (the sun on the rim, carried up; not
on the dome's top); what goes is the sky in all four (transparent, 0). The pole's occlusion for what moves behind it
(COCC in assets/street.js) starts at its top. Needs Pillow, numpy.
"""
import json
import os
import re
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = lambda p: os.path.join(ROOT, 'assets', p)
X0, X1 = 1025, 1063                  # the pole's columns (its lit left edge .. its rim)
APEX, DOME, LIP = 50, 7, 4           # the cap: its top, its dome's rows, its sleeve's rows (it ends at y 61)
SRC = 96                             # the pole's clean rows, copied up from here (just under the band at JOIN)
JOIN = 92                            # the first row of the pole left as it is: a band round it (rows 92-94)
RIM, RIM_TOP = (1060, 1063), 0.55    # its rim's columns; how much of its red is left at the top
SKY = np.array([27., 36., 69.])      # (what faces the sky here: the house's coping, y 66-68)
LIT = np.array([64., 61., 105.])     # (the pole's lit left edge)
TRANSFO = (988, 0, 1064, 66)         # the transformer, its brackets, the hardware above the house's roof (x0, y0, x1, y1)


def load(p, mode='RGBA'):
    return np.asarray(Image.open(A(p)).convert(mode)).astype(float)


def save(arr, p, mode):
    Image.fromarray(np.clip(np.round(arr), 0, 255).astype(np.uint8), mode).save(A(p), 'WEBP', lossless=True, quality=100, method=6, exact=True)


def main():
    L = [load('layer_city_off.webp'), load('street_unlit.webp'), load('night_far.webp', 'RGB'), load('street_sun.webp', 'RGB')]
    src = [l.copy() for l in L]
    x0, y0, x1, y1 = TRANSFO
    for l in L:
        l[y0:y1, x0:x1 + 1] = 0; l[:JOIN, X0 - 1:X1 + 1] = 0                       # (not the house's lit edge, x 1064)
    # the cylinder, from the cap down to the band
    top = APEX + DOME + LIP
    for y in range(top, JOIN):
        for l, s in zip(L, src): l[y, X0:X1 + 1] = s[SRC + y - top, X0:X1 + 1]
    for l, s in zip(L[:2], src[:2]):
        floor = s[SRC:SRC + JOIN - top, RIM[0]:RIM[1] + 1, :3].min(0)
        for y in range(top, JOIN):
            k = RIM_TOP + (1 - RIM_TOP) * (y - top) / (JOIN - 1 - top)
            v = l[y, RIM[0]:RIM[1] + 1, :3]; l[y, RIM[0]:RIM[1] + 1, :3] = floor + (v - floor) * k
    # the cap
    prof = [l[top, X0:X1 + 1, :3].copy() for l in L[:2]]; sunp = L[3][top, X0:X1 + 1].copy()
    cx, r = (X0 + X1 + 1) / 2.0, (X1 - X0 + 1) / 2.0 + 1                         # (its axis; its radius, the sleeve's)
    ylip = APEX + DOME

    def inside(x, y):
        if ylip <= y < top: return abs(x - cx) <= r
        v = (ylip - y) / DOME
        return APEX <= y < ylip and abs(x - cx) <= r * np.sqrt(max(0.0, 1 - v * v))

    def round_it(i, az):                                                         # (the pole's shading at azimuth az, -1 .. 1)
        t = np.clip((az + 1) / 2 * (X1 - X0), 0, X1 - X0); a = int(t); b = min(a + 1, X1 - X0); f = t - a
        return prof[i][a] * (1 - f) + prof[i][b] * f

    for y in range(APEX - 1, top):
        for x in range(int(cx - r) - 1, int(cx + r) + 2):
            cov = np.mean([inside(x + (i + .5) / 4, y + (j + .5) / 4) for i in range(4) for j in range(4)])
            if cov == 0: continue
            u = np.clip((x + .5 - cx) / r, -1, 1)
            if y + .5 >= ylip: nx, ny, nz, k = u, 0.0, np.sqrt(1 - u * u), (0.92 if y == top - 1 else 1.0)
            else:
                v = min(1.0, (ylip - y - .5) / DOME); w = np.sqrt(max(1e-6, 1 - v * v)); uu = np.clip(u / w, -1, 1)
                nx, ny, nz = uu * w / r, v / DOME, np.sqrt(1 - uu * uu) * w / r; n = np.sqrt(nx * nx + ny * ny + nz * nz)
                nx, ny, nz, k = nx / n, ny / n, nz / n, 1.0
            h = np.sqrt(nx * nx + nz * nz); az = nx / h if h > 1e-6 else 0.0; up = max(0.0, ny)
            for i in range(2):
                L[i][y, x, :3] = round_it(i, az) * (1 - up) * k + (SKY + (LIT - SKY) * max(0.0, -az) * 0.6) * up
                L[i][y, x, 3] = round(255 * min(1.0, cov))
            L[2][y, x] = 0; L[3][y, x] = sunp[int(round(np.clip((az + 1) / 2 * (X1 - X0), 0, X1 - X0)))] if up < 0.6 else 0
    for l in L[:2]: l[top, X0:X1 + 1, :3] *= 0.5                                 # (the shadow under the sleeve)
    save(L[0], 'layer_city_off.webp', 'RGBA'); save(L[1], 'street_unlit.webp', 'RGBA')
    save(L[2], 'night_far.webp', 'RGB'); save(L[3], 'street_sun.webp', 'RGB')
    # the pole's occlusion: from its top only
    p = A('street.js'); s = open(p, encoding='utf-8').read()
    m = re.search(r'const COCC = (\{.*?\});', s); C = json.loads(m.group(1))
    C['pole']['runs'] = [[max(a, APEX), b, c, d] for a, b, c, d in C['pole']['runs'] if b >= APEX]
    s = s[:m.start(1)] + json.dumps(C, separators=(',', ':')) + s[m.end(1):]
    open(p, 'w', encoding='utf-8').write(s)
    print('cap', APEX, '..', top - 1, '| occlusion runs', len(C['pole']['runs']))


if __name__ == '__main__':
    main()
