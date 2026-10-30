#!/usr/bin/env python3
"""assets/fuji_aux.webp: what the hours' shader must know of the far layers' box (376, 66, 640 x 640), pixel for pixel.

    python3 tools/fuji_aux.py        (again after any change to fuji_night.webp or fuji_tree.webp)

R: the cherry's (255) or not (0): what shows there of the far layers is the tree (fuji_tree.webp's opaque pixels, or the
   lower canopy painted into fuji_night.webp since the split). The tree keeps its own colours at every hour; the mountain
   takes the hours (skHours). It replaces a guess by a line along the flank and a pink test, which lit a band of the tree
   along the flank (a light streak through it at dawn), greyed its less pink blossoms and left a strip of the flank unlit.
   In fuji_night the canopy is told from the rock by its grain: the painted rock is smooth, the blossoms and branches are
   not; it starts from the pink blossoms and keeps what touches them, above the mountain's foot and its pines, off the
   slope's rim and the snow streaks under it; the rock's painted violet by the canopy and the canopy's blended edge go
   back to the rock (kept in the dusk's colours by a lit mountain, they read as blue foliage that is not there).
G: the slope's rim (in the 4 rows under the sky, the pixels lighter than the rock 4..8 px further in): the lightness of
   that rock (1..255), else 0. At dusk those rows are the sky's light on the edge; read as their own lightness at dawn
   they turned to snow, a white line down both flanks.
Needs Pillow, numpy and scipy.
"""
import os
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOX = (376, 66)


def main():
    fn = np.asarray(Image.open(os.path.join(ROOT, 'assets/fuji_night.webp')).convert('RGBA')).astype(float)
    ft = np.asarray(Image.open(os.path.join(ROOT, 'assets/fuji_tree.webp')).convert('RGBA')).astype(float)
    rgb, a = fn[:, :, :3], fn[:, :, 3]; H, W = a.shape
    L = rgb @ [0.299, 0.587, 0.114] / 255
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    yy, xx = np.mgrid[0:H, 0:W]; X, Y = xx + BOX[0], yy + BOX[1]
    op = a > 128
    mean = ndi.uniform_filter(L, 3); sq = ndi.uniform_filter(L * L, 3); std = np.sqrt(np.maximum(sq - mean * mean, 0))
    pink = (r - b > 12) & (r - g > 22) & op
    smooth = std < 0.012

    top = np.full(W, H); rim = np.zeros_like(op); inner = np.zeros(W)
    for x in range(W):
        ys = np.where(a[:, x] > 30)[0]
        if not len(ys) or ys[0] >= H - 10:
            continue
        top[x] = y0 = ys[0]
        inner[x] = np.median(L[y0 + 4:y0 + 9, x])
        for y in range(y0, y0 + 4):
            if L[y, x] > inner[x] + 0.05:
                rim[y, x] = True

    room = (X >= 740) & (Y <= np.where(X <= 860, 478, 467)) & ~((X < 826) & (yy < top[None, :] + 22))
    blossom = ndi.binary_opening(pink & (L > 0.25) & room, structure=np.ones((2, 2)))
    lab, n = ndi.label(blossom, structure=np.ones((3, 3))); sizes = ndi.sum(blossom, lab, range(1, n + 1))
    seeds = np.isin(lab, 1 + np.where(sizes >= 20)[0])
    cand = op & room & (~smooth | pink)
    lab, n = ndi.label(cand, structure=np.ones((3, 3)))
    keep = np.zeros(n + 1, bool); keep[np.unique(lab[seeds])] = True; keep[0] = False
    tree = keep[lab]
    holes = ndi.binary_fill_holes(tree) & ~tree
    hl, hn = ndi.label(holes); hs = ndi.sum(holes, hl, range(1, hn + 1))
    tree = (tree | np.isin(hl, 1 + np.where(hs <= 8)[0])) & op
    # not the rock's painted violet by the canopy: away from the blossoms (over 3 px) and reached by the rock, it is the rock;
    # then the canopy's edge peeled twice (a pixel neither pink nor a branch against the rock: the dusk's blend of the two)
    pinkish = (r - b > 8) & (r - g > 18) & op; branch = L < 0.16
    far = tree & ~pinkish & ~branch & (ndi.distance_transform_edt(~pinkish) > 3)
    lab, n = ndi.label(far, structure=np.ones((3, 3)))
    reach = np.unique(lab[ndi.binary_dilation(op & ~tree) & far]); reach = reach[reach > 0]
    tree &= ~np.isin(lab, reach)
    for _ in range(2):
        rock = op & ~tree
        tree &= ~(~pinkish & ~branch & ndi.binary_dilation(rock, structure=ndi.generate_binary_structure(2, 1)))

    out = np.zeros((H, W, 4), np.uint8); out[:, :, 3] = 255
    out[:, :, 0] = np.where(tree | (ft[:, :, 3] > 128), 255, 0)
    out[:, :, 1] = np.where(rim & ~tree, np.clip(np.round(inner[None, :] * 255), 1, 255), 0)
    Image.fromarray(out).save(os.path.join(ROOT, 'assets/fuji_aux.webp'), 'WEBP', lossless=True, quality=100, method=6, exact=True)
    print('cherry px', int((out[:, :, 0] > 0).sum()), '| rim px', int((out[:, :, 1] > 0).sum()))


if __name__ == '__main__':
    main()
