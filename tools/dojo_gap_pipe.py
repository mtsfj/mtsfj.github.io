#!/usr/bin/env python3
"""The downpipe in the dark gap between the dojo and the sweet shop (だがし): one plumb pipe from the gutter to the ground.

    python3 tools/dojo_gap_pipe.py      (after tools/kirua_house_side.py; it takes its zone back from commit BEFORE each
                                         time, so it can be run again)

The painter's downpipe both roofs drain into comes down from under the upper eave at the houses' corner (x 132..139:
its dark body, its lit rim on the right) into the dojo's tree. Under the tree, in the gap between the two shops, a lit
strip of the same width ran down to the pavement, but 7 px to the left (x 125..131): the two did not read as one pipe.
The strip moves under the downpipe (DX), as it is (its colours, its edges, its foot on the pavement), so the pipe runs
plumb from the gutter to the ground, the tree hiding its middle. Where it was, the gap as it is on its left (mirrored
from there, row by row: its black, and at its foot the dojo's light on the ground). Where it goes up into the leaves (rows above LEAVES) the painter had it showing between them, darker
in their shade: those pixels of it move with it, as they are (the leaves there keep the gaps he left), and where they
were, the gap's black shows between the leaves. A pixel of the strip is one of the painter's blue (the leaves are
greyer: STRIP_BLUE). In layer_city_off and street_unlit, each
from its own pixels (night_far and street_sun are 0 there, the street's); the wet ground mirrors the street live, so its
reflection follows. Needs git, Pillow, numpy.
"""
import io
import os
import subprocess
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = lambda p: os.path.join(ROOT, 'assets', p)
BEFORE = '5827dd8'                   # (the layers as they were, the strip on the left)
ZONE = (118, 440, 146, 760)          # x0, y0, x1, y1: taken back from BEFORE first
X0, X1 = 124, 132                    # the strip's columns, its two dark edges included
DX = 7                               # onto the downpipe's columns (132..139)
TOP, FOOT = 446, 752                 # its rows: from among the leaves' lower edge to its foot's glint on the pavement
LEAVES = 472                         # (below this row, no leaf over it: the whole strip moves)
STRIP_BLUE = lambda r, g, b: (b >= 30) & (b >= 2.3 * np.maximum(r, 1)) & (b >= g + 12)
BLACK = 9                            # (a pixel of the gap seen between the leaves: r + g + b at most this)


def load(p, mode='RGBA', at=None):
    data = subprocess.run(['git', 'show', f'{at}:assets/{p}'], cwd=ROOT, capture_output=True, check=True).stdout if at else open(A(p), 'rb').read()
    return np.asarray(Image.open(io.BytesIO(data)).convert(mode)).astype(float)


def save(arr, p, mode):
    Image.fromarray(np.clip(np.round(arr), 0, 255).astype(np.uint8), mode).save(A(p), 'WEBP', lossless=True, quality=100, method=6, exact=True)


def main():
    names = (('layer_city_off.webp', 'RGBA'), ('street_unlit.webp', 'RGBA'))
    src = [load(n, m, BEFORE) for n, m in names]
    zx0, zy0, zx1, zy1 = ZONE
    ref = src[0][..., :3]
    strip = np.zeros(ref.shape[:2], bool)
    strip[TOP:LEAVES, X0 + 1:X1] = STRIP_BLUE(*(ref[TOP:LEAVES, X0 + 1:X1, c] for c in range(3)))
    strip[LEAVES:FOOT, X0:X1 + 1] = True
    gap = ref.sum(2) <= BLACK                                                    # (the gap's black between the leaves)
    for (n, m), s in zip(names, src):
        l = load(n, m)
        l[zy0:zy1, zx0:zx1] = s[zy0:zy1, zx0:zx1]
        dark = np.median(s[TOP:LEAVES, X0:X1 + DX + 1][gap[TOP:LEAVES, X0:X1 + DX + 1]], 0)   # (that black, in this layer)
        for y in range(TOP, FOOT):                                               # where it was: the gap
            for x in range(X0, X1 + 1):
                if strip[y, x]: l[y, x] = s[y, 2 * X0 - 1 - x] if y >= LEAVES else dark
        for y in range(TOP, FOOT):                                               # where it goes, as it is
            for x in range(X0, X1 + 1):
                if strip[y, x]: l[y, x + DX] = s[y, x]
        save(l, n, m)
    print('strip moved', DX, 'px right, rows', TOP, '..', FOOT - 1, '| between the leaves', int(strip[TOP:LEAVES].sum()), 'px')


if __name__ == '__main__':
    main()
