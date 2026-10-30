#!/usr/bin/env python3
"""assets/fuji_aux.webp: what the hours' shader must know of the far layers' box (376, 66, 640 x 640), pixel for pixel.

    python3 tools/fuji_aux.py        (again after any change to fuji_night.webp or fuji_tree.webp)

R: the cherry's (255) or not (0): what shows there of the far layers is the tree (fuji_tree.webp's opaque pixels, or the
   lower canopy painted into fuji_night.webp since the split). The tree keeps its own colours at every hour; the mountain
   takes the hours (skHours). It replaces a guess by a line along the flank and a pink test, which lit a band of the tree
   along the flank (a light streak through it at dawn), greyed its less pink blossoms and left a strip of the flank unlit.
   In fuji_night the canopy is told from the rock by its grain: the painted rock is smooth, the blossoms and branches are
   not; it starts from the pink blossoms and keeps what touches them, above the mountain's foot and its pines, off the
   slope's rim and the snow streaks under it; the rock's painted violet by the canopy and the canopy's soft violet edge
   (up to 5 px) go back to the rock (kept in the dusk's colours by a lit mountain, they read as blue foliage, a dark rim).
G: the slope's rim (in the 4 rows under the sky, the pixels lighter than the rock 4..8 px further in): the lightness of
   that rock (1..255), else 0. At dusk those rows are the sky's light on the edge; read as their own lightness at dawn
   they turned to snow, a white line down both flanks.
B: what shows there is the rock though the tree's own layer is on top (its pixels painted as the rock): graded as the
   mountain all the same (255), else 0.
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
    # the canopy's edge on the rock: its soft pixels (neither pink nor a branch: the dusk's violet shade on it, 1 to 5 px wide
    # by places) reached from the rock through soft pixels only, up to 5 px in, go back to the rock, and the soft crumbs they
    # leave alone with them: the edge is the blossoms' all along (kept violet by a lit mountain, they read as a dark rim)
    cross = ndi.generate_binary_structure(2, 1)
    soft = tree & ~pinkish & ~branch & ~(ft[:, :, 3] > 128)
    front = op & ~tree; peel = np.zeros_like(soft)
    for _ in range(5):
        front = ndi.binary_dilation(front, structure=cross) & soft & ~peel; peel |= front
    left = soft & ~peel; lab, n = ndi.label(left, structure=cross); sz = ndi.sum(left, lab, range(1, n + 1))
    peel |= np.isin(lab, 1 + np.where(sz <= 3)[0]) & ndi.binary_dilation(peel)
    tree &= ~peel
    # what shows there as the rock does (the dusk's colour of the rock round it, within 16 a channel, and joined to it): the
    # rock's, whatever its layer (its dusk purple passes the pink test). Under the tree's own layers (fuji_tree, fuji_front)
    # it is told to the shader by B: graded as the mountain all the same
    ff = np.asarray(Image.open(os.path.join(ROOT, 'assets/fuji_front.webp')).convert('RGBA')).astype(float)
    top = rgb.copy(); ta = a / 255
    for Ly in (ft, ff):
        al = Ly[:, :, 3:4] / 255; top = top * (1 - al) + Ly[:, :, :3] * al; ta = np.maximum(ta, Ly[:, :, 3] / 255)
    rock = op & ~tree & smooth & ~(ft[:, :, 3] > 128)
    wgt = ndi.gaussian_filter(rock.astype(float), 5)
    field = np.stack([ndi.gaussian_filter(rgb[:, :, c] * rock, 5) for c in range(3)], -1) / np.maximum(wgt, 1e-6)[..., None]
    cher = tree | (ft[:, :, 3] > 128)
    like = cher & ndi.binary_dilation(rock, iterations=10) & (wgt > 0.02) & (np.abs(top - field).max(-1) < 16) & (ta > 0.5)
    lab, n = ndi.label(like | rock, structure=cross); keep = np.unique(lab[rock]); like &= np.isin(lab, keep[keep > 0])
    tree &= ~like
    under = like & ((ft[:, :, 3] > 128) | (ff[:, :, 3] > 128))
    # the rock's pockets inside the canopy (its gaps onto the mountain's foot, dark at dusk like its shade): the tree's, as
    # the night shows them, not light grey spots in the blossoms at dawn; the rock along the canopy's outer edge stays rock
    canopy = tree | (ft[:, :, 3] > 128)
    disk = ndi.generate_binary_structure(2, 1); disk = ndi.iterate_structure(disk, 3)
    closed = ndi.binary_fill_holes(ndi.binary_closing(canopy, structure=disk))
    pockets = op & ~canopy & ~like & closed & ~ndi.binary_dilation(~closed, iterations=2)
    tree |= pockets

    out = np.zeros((H, W, 4), np.uint8); out[:, :, 3] = 255
    out[:, :, 0] = np.where((tree | (ft[:, :, 3] > 128)) & ~like, 255, 0)
    out[:, :, 2] = np.where(under, 255, 0)
    out[:, :, 1] = np.where(rim & ~tree, np.clip(np.round(inner[None, :] * 255), 1, 255), 0)
    Image.fromarray(out).save(os.path.join(ROOT, 'assets/fuji_aux.webp'), 'WEBP', lossless=True, quality=100, method=6, exact=True)
    print('cherry px', int((out[:, :, 0] > 0).sum()), '| rim px', int((out[:, :, 1] > 0).sum()), '| rock-like', int(like.sum()), 'of which under the tree layers', int(under.sum()), '| pockets', int(pockets.sum()))


if __name__ == '__main__':
    main()
