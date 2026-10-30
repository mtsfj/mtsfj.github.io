#!/usr/bin/env python3
"""The left tree (by Killua's house) brought down to the roofs beside it, the mountain carried on behind it.

    python3 tools/left_tree_trim.py      (once; then tools/fuji_aux.py)

Its crown rose 170 px over the oden's roof next to it (y 450): it now stops at that height, a line of round clumps
between 448 and 458 (each clump a dome, its sides 2 to 5 px lower), cut in the street's layers (layer_city_off,
street_unlit, street_sun, night_far) with nothing left floating. What shows over it: the sky, the pagoda's foot and
Fuji's left flank. The mountain's layer (fuji_night.webp) starts at x 376; left of it, between its flank carried on
(its slope, 0.43) and the tree, the street's layer takes the mountain (over 376-377 too, whose two columns fade out
there, where the tree hid them): fuji_night's own pixels right of 378, mirrored, sat on the carried-on slope (their alpha with them: the same soft edge on the sky), marked in night_far as the
mountain's (160), so they take its hours. Needs Pillow, numpy and scipy.
"""
import os
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = lambda p: os.path.join(ROOT, 'assets', p)
TREE_BOX = (326, 270, 492, 572)        # x0, y0, x1, y1: the tree, right of the house's wall (x 325)
BASE, SEED = 452, 5
FX, SLOPE = 376, 0.43                  # fuji_night's left edge; its flank's slope there (px down per px left)


def load(p, mode='RGBA'):
    return np.asarray(Image.open(A(p)).convert(mode)).copy()


def save(arr, p, mode):
    Image.fromarray(arr.astype(np.uint8), mode).save(A(p), 'WEBP', lossless=True, quality=100, method=6, exact=True)


def main():
    city, unlit = load('layer_city_off.webp'), load('street_unlit.webp')
    nf, sun = load('night_far.webp', 'RGB'), load('street_sun.webp', 'RGB')
    fn = load('fuji_night.webp')
    H, W = city.shape[:2]; yy, xx = np.mgrid[0:H, 0:W]
    x0, y0, x1, y1 = TREE_BOX
    op = city[:, :, 3] > 128
    box = (xx >= x0) & (xx < x1) & (yy >= y0) & (yy < y1)
    lab, n = ndi.label(op & box, structure=np.ones((3, 3)))
    sizes = ndi.sum(op & box, lab, range(1, n + 1)); tree = lab == 1 + np.argmax(sizes)

    # the new crown: round clumps, their tops 448..454, their sides down to 458
    rng = np.random.default_rng(SEED); top = np.full(W, H, float); x = x0
    while x < x1:
        w = int(rng.integers(6, 13)); peak = BASE + rng.uniform(-4, 2); c = (w - 1) / 2
        for k in range(w):
            if x + k < x1: top[x + k] = peak + rng.uniform(2.0, 5.0) * ((k - c) / (c + 0.5)) ** 2
        x += w
    top = np.round(top).astype(int)
    cut = tree & (yy < top[None, :])
    # nothing left floating: tree pixels cut off from the trunk side go too (twice: a cut can free another crumb)
    for _ in range(2):
        rest = tree & ~cut & box
        lab, n = ndi.label(rest, structure=np.ones((3, 3)))
        if n > 1:
            sizes = ndi.sum(rest, lab, range(1, n + 1)); cut |= rest & (lab != 1 + np.argmax(sizes))
    # also any faint pixel of the street's layer left in the sky over the new crown (rain specks, soft edges)
    cut |= box & (city[:, :, 3] > 0) & (city[:, :, 3] <= 128) & (yy < top[None, :])

    for L in (city, unlit):
        L[cut] = 0
    nf[cut] = 0; sun[cut] = 0

    # the mountain carried on left of fuji_night, under its flank's line, where the street's layer is now clear
    ftop = np.array([np.argmax(fn[:, c, 3] > 30) for c in range(fn.shape[1])]) + 66
    M = FX + 2                                                                # (its first two columns fade out where the tree hid them)
    y_edge = lambda x: ftop[M - FX] + (M - x) * SLOPE                         # (its line from its first full column)
    ext = np.zeros((H, W), bool); src = []
    for x in range(x0, M):
        xs = 2 * M - x                                                        # (mirrored about its first full column, over the faded ones)
        dy = int(round(y_edge(x) - ftop[xs - FX]))
        for y in range(int(np.floor(y_edge(x))) - 3, H):
            if city[y, x, 3] > 128 and not cut[y, x]: break                   # (down to what of the street is still there)
            sy = y - dy - 66
            if 0 <= sy < fn.shape[0] and fn[sy, xs - FX, 3] > 0:
                ext[y, x] = True; src.append((y, x, sy, xs - FX))
    for y, x, sy, sx in src:
        a = fn[sy, sx, 3] / 255.0; under = city[y, x, :3].astype(float) * (city[y, x, 3] / 255.0)
        rgb = fn[sy, sx, :3] * a + under * (1 - a) if city[y, x, 3] else fn[sy, sx, :3]
        for L in (city, unlit):
            L[y, x, :3] = np.round(rgb); L[y, x, 3] = max(int(fn[sy, sx, 3]), int(L[y, x, 3]))
        nf[y, x] = 160; sun[y, x] = 0
    save(city, 'layer_city_off.webp', 'RGBA'); save(unlit, 'street_unlit.webp', 'RGBA')
    save(nf, 'night_far.webp', 'RGB'); save(sun, 'street_sun.webp', 'RGB')
    print('cut', int(cut.sum()), 'px | mountain carried on', int(ext.sum()), 'px | crown', top[x0:x1].min(), '..', top[x0:x1].max())


if __name__ == '__main__':
    main()
