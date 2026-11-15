#!/usr/bin/env python3
"""The belvedere's railing at the street's end, dimmed as the far city goes out: its dark picture (assets/rail_dark.webp).

    python3 tools/belvedere_rail.py      (from the street's layer as it is; again after a change there: the same bytes)

The railing (x 604..768, y 618..640) is painted lit by the city's glow behind and below it, as the dusk shows it; at 3 h
the far windows are out (NIGHT.home, the share of homes lit) and the railing still glowed pink-white over a dark city.
This keeps its rails and posts (in each rail's band of rows, each column's brightest pixel where it stands out of the
band's edges; a post a column brighter than either side over most of the railing's height; neither coloured: the far
windows' lights are) and writes them as they look once the glow behind them is gone: a
dark silhouette in the night's blue (RAIL_DARK of their own value), transparent elsewhere. street.js lays it over the
railing (z 0.59, over the far city's quad) graded as the street, at 1 - NIGHT.home, eased: none through the evening,
most of it after 2 h, as the far windows go out. Needs numpy, Pillow.
"""
import os
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOX = (604, 618, 768, 640)
RAIL_DARK = np.array([0.36, 0.37, 0.5])
RAILS = [(621, 624), (626, 629), (630, 633)]     # the three rails' bands of rows
POST_ROWS = (622, 637)
LUMA = np.array([0.299, 0.587, 0.114])


def main():
    x0, y0, x1, y1 = BOX
    c = np.asarray(Image.open(os.path.join(ROOT, 'assets', 'layer_city_off.webp')).convert('RGBA')).astype(float)
    s = c[y0 - 2:y1 + 2, x0 - 2:x1 + 2, :3]
    L = s @ LUMA
    mx, mn = s.max(-1), s.min(-1); sat = (mx - mn) / np.maximum(mx, 1)
    Lc, satc = L[2:-2, 2:-2], sat[2:-2, 2:-2]
    m = np.zeros(Lc.shape, bool)
    for a, b in RAILS:                                            # the rails: each column's brightest row in the band
        band = Lc[a - y0:b - y0 + 1]
        r = band.argmax(0); top = band.max(0)
        edge = np.minimum(Lc[a - y0 - 1], Lc[min(b - y0 + 1, Lc.shape[0] - 1)])
        ok = (top - edge > 10) & (top > 60)
        near = (band > top[None] - 18) & ok[None]                 # (a rail two rows thick where it is)
        m[a - y0:b - y0 + 1] |= near
    hori = Lc - 0.5 * (L[2:-2, :-4] + L[2:-2, 4:])               # the posts: a column brighter than either side
    post = (hori > 15) & (satc < 0.4)
    pc = np.where(post[POST_ROWS[0] - y0:POST_ROWS[1] - y0].sum(0) >= 6)[0]
    m[POST_ROWS[0] - y0:POST_ROWS[1] - y0, pc] |= post[POST_ROWS[0] - y0:POST_ROWS[1] - y0, pc] | (Lc[POST_ROWS[0] - y0:POST_ROWS[1] - y0, pc] > 70)
    m &= satc < 0.45
    out = np.zeros((y1 - y0, x1 - x0, 4))
    out[m, :3] = s[2:-2, 2:-2][m] * RAIL_DARK; out[m, 3] = 255
    Image.fromarray(np.round(out).astype(np.uint8), 'RGBA').save(os.path.join(ROOT, 'assets', 'rail_dark.webp'), 'WEBP',
                                                                   lossless=True, quality=100, method=6, exact=True)
    print('rail_dark:', int(m.sum()), 'px at', (x0, y0), (x1 - x0, y1 - y0))


if __name__ == '__main__':
    main()
