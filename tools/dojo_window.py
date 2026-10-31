#!/usr/bin/env python3
"""The window at the top left, above the dojo: its glass clean again, its frame whole.

    python3 tools/dojo_window.py      (after tools/tree_bc.py; it takes its zone back from commit BEFORE each time, so it
                                       can be run again)

Over the tree in front of the dojo the house's upper window shows (x 0..40, y 0..37): its glass carried diagonal red
planks from x 19 on (the wall's boards running into it), and the wall's planks, redrawn toward their vanishing point
when the old foliage's shadows were taken off, ran over its frame (x 40..52). Its glass is now the painter's own clean
glass of its left part (x 0..18) carried on to its frame, column for column, row for row (two panes, the painter's
mullion between them); its frame (the dark mullion,
its lit strip) the painter's again, from FRAME_AT, where the boards stop at it. Over the tree only (each row down to the
tree's top there). In layer_city_off, street_unlit, night_far and street_sun. Needs git, Pillow, numpy.
"""
import io
import os
import subprocess
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = lambda p: os.path.join(ROOT, 'assets', p)
BEFORE = '45c5cb5'                   # (the layers as they were: the glass striped, the frame overrun)
FRAME_AT = '8d4ca3c'                 # (the frame whole: before the wall's boards were redrawn)
ZONE = (0, 0, 53, 38)                # x0, y0, x1, y1: the window over the tree
GLASS = (0, 19, 40)                  # the clean glass's columns (x0 .. x1 - 1), the striped glass's (x1 .. x2 - 1)
FRAME = (40, 53)                     # the frame's columns (the mullion, its lit strip, the boards' end)
TOP = 37                             # the last row over the tree (the tree's top at these columns: y 38..42)


def load(p, mode='RGBA', at=None):
    data = subprocess.run(['git', 'show', f'{at}:assets/{p}'], cwd=ROOT, capture_output=True, check=True).stdout if at else open(A(p), 'rb').read()
    return np.asarray(Image.open(io.BytesIO(data)).convert(mode)).astype(float)


def save(arr, p, mode):
    Image.fromarray(np.clip(np.round(arr), 0, 255).astype(np.uint8), mode).save(A(p), 'WEBP', lossless=True, quality=100, method=6, exact=True)


def main():
    names = (('layer_city_off.webp', 'RGBA'), ('street_unlit.webp', 'RGBA'), ('night_far.webp', 'RGB'), ('street_sun.webp', 'RGB'))
    for n, m in names:
        l, b, f = load(n, m), load(n, m, BEFORE), load(n, m, FRAME_AT)
        x0, y0, x1, y1 = ZONE
        l[y0:y1, x0:x1] = b[y0:y1, x0:x1]
        g0, g1, g2 = GLASS
        for x in range(g1, g2): l[:TOP + 1, x] = b[:TOP + 1, g0 + (x - g1) % (g1 - g0)]   # (the clean glass carried on)
        l[:TOP + 1, FRAME[0]:FRAME[1]] = f[:TOP + 1, FRAME[0]:FRAME[1]]                    # (the frame as the painter left it)
        save(l, n, m)
    print('window: glass x', GLASS[1], '..', GLASS[2] - 1, 'from x', GLASS[0], '..', GLASS[1] - 1, '| frame x', FRAME, 'from', FRAME_AT)


if __name__ == '__main__':
    main()
