#!/usr/bin/env python3
"""Kirua seated on his roof's tiles: his body's frames cut where the eave's tiles stand in front of his seat.

    python3 tools/killua_seat.py      (reads tools/src/killua_body_before.webp, the body's sheet as baked by
                                       build_zzzchar_killua.py, and tools/left_eaves.py's model of the roof (not the
                                       layers: any time in the chain); writes assets/killua_body.webp, the same bytes)

The roof under him was redrawn (tools/left_eaves.py: the barrels' ends a slight bump over the flat tiles, the band in the
street's perspective) and he sat on its very edge, his seat on the tiles' tops: from the street he seemed to perch on
it, a hair of sky under him between the bumps (the owner: "faudrait le reculer un poil, il flotte un poil"). He sits
now a little further up the slope, KOFF (assets/street.js moves his whole rig by it: body, legs, head, the yo-yo and
his seat): from below the roof's edge is then in front of his seat, so each frame of his body (KM.body, the 3 x 3 sheet:
his breath, his shirt's hem in the gust) loses, left of where his thighs leave the seat (THIGH), the pixels the eave
covers there, as tools/left_eaves.py draws it (its tiles, their lip and the gutter, where they cover half a pixel or
more), and the tiles show in front of him; between
two barrels' ends his body shows (the roof itself is behind the edge, out of sight from below). His thighs (the legs'
sheet) pass over the edge and his shins hang in front of the gutter as before; his head, his hair's rim, his far leg
are not touched. His lightning's silhouette and his sparks' outline are read from these frames at run time, so they
follow. The soft shadow he casts on the tiles round his seat is tools/left_eaves.py's (K_SEAT). Needs numpy, Pillow.
"""
import os
import sys
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import left_eaves as L

SRC = os.path.join(ROOT, 'tools', 'src', 'killua_body_before.webp')
OUT = os.path.join(ROOT, 'assets', 'killua_body.webp')
BODY = (294, 160, 49, 51, 3, 3)                  # KM.body in assets/street.js before KOFF: x, y, w, h, columns, rows
KOFF = L.K_SEAT['off']                           # (his move up the slope, in scene px: street.js's KOFF)
ROOF = (L.TILE, L.DISC, L.LIP, L.GUT, L.HANGER)
THIGH = -1                                       # (the cut stops this far right of his seat: there his thighs go over the edge)


def main():
    S = np.array(Image.open(SRC).convert('RGBA'))
    x, y, w, h, cols, rows = BODY
    bx, by = x + KOFF[0], y + KOFF[1]
    R = L.render(bx, by, bx + w, by + h, 'K')
    front = (R['cov'] >= 0.5) & np.isin(R['kind'], ROOF)
    front &= (np.arange(bx, bx + w) < L.K_SEAT['seat'][0] + KOFF[0] + THIGH)[None, :]   # (his seat only: his thighs pass
                                                                                        # over the edge, in front of it)
    n = 0
    for r in range(rows):
        for c in range(cols):
            f = S[r * h:(r + 1) * h, c * w:(c + 1) * w]
            m = front & (f[..., 3] > 0); n += int(m.sum())
            f[m] = 0
    Image.fromarray(S, 'RGBA').save(OUT, 'WEBP', lossless=True, quality=100, method=6, exact=True)
    print('killua_body: %d pixels behind the tiles over the 9 frames (offset %s)' % (n, KOFF))


if __name__ == '__main__':
    main()
