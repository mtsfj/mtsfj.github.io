#!/usr/bin/env python3
"""The utility pole on the right sidewalk: cut shorter, just under its transformer (which goes), its top capped.

    python3 tools/pole_cut.py      (it takes its zone back from commit BEFORE each time, so it can be run again)

The pole ran out of the frame at the top, its transformer hung on its left (x 988-1027, y 0-57, its brackets to 64),
its top a dark block of hardware down to y 95. It now ends well under where the transformer hung, a little under the
roof line of the house on its right (y 66) and well clear of the page's menu over the sky (it sat right under "Blog"
higher up): only sky above it and on its left, the house on its right beginning at its own lit edge (x 1064), nothing
to invent behind it. Its top is
the cap the concrete poles wear: a short sleeve one pixel wider than the pole each side (LIP rows), a low dome over it
(DOME rows), a line of shadow under the sleeve. Each pixel of the cap is shaded from its normal: round its axis as the
pole is (its lit left edge, its dark body, its rim from the shops' red), from above by the sky (blue, lighter on the left
where the pole's light comes from), in a few stepped bands with the pole's own grain on them, its outline on the sky by
coverage. Under it, the pole's own cylinder: its clean rows from under the old hardware (SRC) copied up, their fine grain
kept and their slow change down the pole levelled at what it is there (in the street and in the power cut alike: the
red night reads the two), so it is one pole from the cap down; the rim's red, which grows toward the street, fading a
little upward as it does down the pole. A band round it under the cap, the two thin conduits on its face running under
it to the cap. In
layer_city_off, street_unlit (each from its own pixels), night_far (0, the street's) and street_sun (the sun on the rim,
carried up; not on the dome's top); what goes is the sky in all four (transparent, 0). The pole's occlusion for what
moves behind it (COCC in assets/street.js) starts at its top. Needs git, Pillow, numpy.
"""
import io
import json
import os
import re
import subprocess
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = lambda p: os.path.join(ROOT, 'assets', p)
BEFORE = '6c8530a'                   # (the layers as they were, the pole whole)
ZONE = (985, 0, 1071, 100)           # x0, y0, x1, y1: taken back from BEFORE first
X0, X1 = 1025, 1063                  # the pole's columns (its lit left edge .. its rim)
APEX, DOME, LIP = 74, 7, 4           # the cap: its top, its dome's rows, its sleeve's rows
SRC = 106                            # the pole's clean rows, copied up from here (under the old hardware's two bands, 92-93 and 102-104)
JOIN = 96                            # the first row of the pole left as it is
TREND = 40                           # (the rows under it that give each column its slow change: above the lamp's arm)
RIM, RIM_TOP = (1060, 1063), 0.75    # its rim's columns; how much of its red is left at the top
BAND = 4                             # a band round the pole, this many rows under the cap
SKY = np.array([27., 36., 69.])      # (what faces the sky here: the house's coping, y 66-68)
LIT = np.array([64., 61., 105.])     # (the pole's lit left edge)
CREST = np.array([35., 44., 82.])    # (the sky's light on a crest: the house's coping's top)
TRANSFO = (988, 0, 1064, 66)         # the transformer, its brackets, the hardware above the house's roof (x0, y0, x1, y1)


def load(p, mode='RGBA', at=None):
    data = subprocess.run(['git', 'show', f'{at}:assets/{p}'], cwd=ROOT, capture_output=True, check=True).stdout if at else open(A(p), 'rb').read()
    return np.asarray(Image.open(io.BytesIO(data)).convert(mode)).astype(float)


def save(arr, p, mode):
    Image.fromarray(np.clip(np.round(arr), 0, 255).astype(np.uint8), mode).save(A(p), 'WEBP', lossless=True, quality=100, method=6, exact=True)


def main():
    names = (('layer_city_off.webp', 'RGBA'), ('street_unlit.webp', 'RGBA'), ('night_far.webp', 'RGB'), ('street_sun.webp', 'RGB'))
    L = [load(n, m) for n, m in names]
    src = [load(n, m, BEFORE) for n, m in names]
    zx0, zy0, zx1, zy1 = ZONE
    for l, s in zip(L, src): l[zy0:zy1, zx0:zx1] = s[zy0:zy1, zx0:zx1]
    x0, y0, x1, y1 = TRANSFO
    for l in L:
        l[y0:y1, x0:x1 + 1] = 0; l[:JOIN, X0 - 1:X1 + 1] = 0                       # (not the house's lit edge, x 1064)
    # the cylinder, from the cap down to JOIN
    top = APEX + DOME + LIP
    for y in range(top, JOIN):
        for l, s in zip(L, src): l[y, X0:X1 + 1] = s[SRC + y - top, X0:X1 + 1]
    res = []
    for l, s in zip(L[:2], src[:2]):
        col = s[:, X0:X1 + 1, :3]; level = col[SRC:SRC + 8].mean(0); r = np.zeros_like(col)
        for y in range(SRC, SRC + TREND):
            a, b = max(SRC, y - 4), min(SRC + TREND, y + 5); r[y] = col[y] - col[a:b].mean(0)
        res.append(r)
        for y in range(top, JOIN): l[y, X0:X1 + 1, :3] = np.clip(level + r[SRC + y - top], 0, 255)
        floor = col[SRC:SRC + JOIN - top, RIM[0] - X0:RIM[1] - X0 + 1].min(0)
        for y in range(top, JOIN):
            k = RIM_TOP + (1 - RIM_TOP) * (y - top) / (JOIN - 1 - top)
            v = l[y, RIM[0]:RIM[1] + 1, :3]; l[y, RIM[0]:RIM[1] + 1, :3] = floor + (v - floor) * k
    # a band round the pole under the cap (its lit top, its shadow): the two conduits up its face run under it to the cap
    for l in L[:2]:
        l[top + BAND, X0:X1 + 1, :3] = np.minimum(255, l[top + BAND, X0:X1 + 1, :3] * 1.25 + 5)
        l[top + BAND + 1, X0:X1 + 1, :3] *= 0.55
        for x, e in ((X0 - 1, X0), (X1 + 1, X1)):                                # (it stands a pixel proud of the pole each side)
            l[top + BAND:top + BAND + 2, x, :3] = l[top + BAND:top + BAND + 2, e, :3] * 0.8; l[top + BAND:top + BAND + 2, x, 3] = 255
    for x, e in ((X0 - 1, X0), (X1 + 1, X1)):
        for l in L[2:]: l[top + BAND:top + BAND + 2, x] = l[top + BAND:top + BAND + 2, e]
    # the cap
    prof = [l[top, X0:X1 + 1, :3].copy() for l in L[:2]]; sunp = L[3][top, X0:X1 + 1].copy()
    cx, r = (X0 + X1 + 1) / 2.0, (X1 - X0 + 1) / 2.0 + 1                         # (its axis; its radius, the sleeve's)
    ylip = APEX + DOME

    def inside(x, y):
        if ylip <= y < top: return abs(x - cx) <= r
        v = (ylip - y) / DOME
        return APEX <= y < ylip and abs(x - cx) <= r * np.sqrt(max(0.0, 1 - v * v))

    def at(az):                                                                  # (the pole's column at azimuth az, -1 .. 1)
        return np.clip((az + 1) / 2 * (X1 - X0), 0, X1 - X0)

    def round_it(i, az):                                                         # (the pole's own column there, its bands as they are)
        return prof[i][int(round(at(az)))]

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
            h = np.sqrt(nx * nx + nz * nz); az = nx / h if h > 1e-6 else 0.0
            up = round(max(0.0, ny) * 3) / 3                                     # (stepped bands, as the painter shades)
            up *= 1 - 0.5 * max(0.0, -az)                                        # (its shoulder toward the lamp lit by the lamp, as the pole under it)
            g = int(round(at(az)))
            for i in range(2):
                c = round_it(i, az) * (1 - up) * k + (SKY + (LIT - SKY) * max(0.0, -az) * 0.6) * up
                c = c + res[i][SRC + (y * 7 + x * 3) % 30, g] * (1 - 0.5 * up)   # (the pole's own grain)
                if y < ylip and not inside(x + .5, y - .5): c = np.maximum(c, CREST)   # (its crest against the sky: the coping's light)
                L[i][y, x, :3] = np.clip(c, 0, 255); L[i][y, x, 3] = round(255 * min(1.0, cov))
            L[2][y, x] = 0; L[3][y, x] = sunp[g] if az > 0.7 and up < 0.7 else 0   # (the rim's sunset light, where the rim's colour is)
    for l in L[:2]: l[top, X0:X1 + 1, :3] *= 0.5                                 # (the shadow under the sleeve)
    for (n, m), l in zip(names, L): save(l, n, m)
    # the pole's occlusion: from its top only (from the runs as they were)
    old = subprocess.run(['git', 'show', f'{BEFORE}:assets/street.js'], cwd=ROOT, capture_output=True, check=True).stdout.decode('utf-8')
    runs = json.loads(re.search(r'const COCC = (\{.*?\});', old).group(1))['pole']['runs']
    p = A('street.js'); s = open(p, encoding='utf-8').read()
    m = re.search(r'const COCC = (\{.*?\});', s); C = json.loads(m.group(1))
    C['pole']['runs'] = [[max(a, APEX), b, c, d] for a, b, c, d in runs if b >= APEX]
    s = s[:m.start(1)] + json.dumps(C, separators=(',', ':')) + s[m.end(1):]
    open(p, 'w', encoding='utf-8').write(s)
    print('cap', APEX, '..', top - 1, '| occlusion runs', len(C['pole']['runs']))


if __name__ == '__main__':
    main()
