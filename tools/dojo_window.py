#!/usr/bin/env python3
"""The window at the top left, above the dojo: the painter's own window again.

    python3 tools/dojo_window.py      (after tools/tree_bc.py; it takes its zone back from commit BEFORE each time, so it
                                       can be run again)

Over the tree in front of the dojo the house's upper window shows: the painter's sliding window, half open (a pane of
glass at its left, the warm room seen through its opening, the second pane, its dark casing; x 0..65). When the wall's
boards were redrawn toward their vanishing point (the old foliage's shadows taken off) they ran over its casing and its
second pane, and its opening lost its room. It is the painter's again, pixel for pixel, as it was before the tree was
changed (ORIG), in each column down to the new tree's top there (its first leaf: a dark pixel the tree's change put
there, joined to the crown's mass below); the tree stays in front of it. Its casing's right edge (x 65) is where the
redrawn boards begin. In layer_city_off, street_unlit, night_far and
street_sun. Needs git, Pillow, numpy.
"""
import io
import os
import subprocess
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = lambda p: os.path.join(ROOT, 'assets', p)
BEFORE = '45c5cb5'                   # (the layers as they were: the boards over the window)
ORIG, TREE = '8d4ca3c^', '8d4ca3c'   # (the painter's window, before the tree was changed; the tree's change)
ZONE = (0, 0, 66, 60)                # x0, y0, x1, y1: the window and its casing, down into the tree's top
LEAF = 45                            # (a leaf: darker than this, where the tree's change put a pixel)


def load(p, mode='RGBA', at=None):
    data = subprocess.run(['git', 'show', f'{at}:assets/{p}'], cwd=ROOT, capture_output=True, check=True).stdout if at else open(A(p), 'rb').read()
    return np.asarray(Image.open(io.BytesIO(data)).convert(mode)).astype(float)


def save(arr, p, mode):
    Image.fromarray(np.clip(np.round(arr), 0, 255).astype(np.uint8), mode).save(A(p), 'WEBP', lossless=True, quality=100, method=6, exact=True)


def main():
    names = (('layer_city_off.webp', 'RGBA'), ('street_unlit.webp', 'RGBA'), ('night_far.webp', 'RGB'), ('street_sun.webp', 'RGB'))
    x0, y0, x1, y1 = ZONE
    o, t = load('layer_city_off.webp', 'RGBA', ORIG)[y0:y1, x0:x1], load('layer_city_off.webp', 'RGBA', TREE)[y0:y1, x0:x1]
    dark = (np.abs(o - t).sum(2) > 0) & (t[..., :3] @ [0.299, 0.587, 0.114] < LEAF)
    leaf = np.zeros_like(dark); todo = [(y1 - y0 - 1, x) for x in range(x1 - x0) if dark[-1, x]]   # (the crown: from the zone's foot up)
    while todo:
        y, x = todo.pop()
        if 0 <= y < y1 - y0 and 0 <= x < x1 - x0 and dark[y, x] and not leaf[y, x]:
            leaf[y, x] = True; todo += [(y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)]
    top = [int(np.argmax(leaf[:, x])) if leaf[:, x].any() else y1 - y0 for x in range(x1 - x0)]   # (the tree's top, each column)
    for n, m in names:
        l, b, w = load(n, m), load(n, m, BEFORE), load(n, m, ORIG)
        l[y0:y1, x0:x1] = b[y0:y1, x0:x1]
        for x in range(x1 - x0): l[y0:y0 + top[x], x0 + x] = w[y0:y0 + top[x], x0 + x]
        save(l, n, m)
    print('window: the painter\'s, down to the tree (rows', min(top), '..', max(top), ')')


if __name__ == '__main__':
    main()
