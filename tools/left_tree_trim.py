#!/usr/bin/env python3
"""The left tree (by Killua's house) brought down below the roofs beside it, the mountain carried on behind it.

    python3 tools/left_tree_trim.py      (reads the layers as they were before it, at commit aa383bc; then tools/fuji_aux.py)

Its crown rose 170 px over the oden's roof next to it (y 450): it now stays under it (447 at the highest). Not cut
across: its own painted top (the leafy edge from x 334 to 426, its clumps, its sprigs and gaps, 8 to 22 px deep) is
brought down onto the new line, mirrored (it rose to the wall; it now rises to the right, to the tree's right flank,
which starts at that height). It comes as five pieces, each moved whole (the clumps keep their shape), cut where the
painted top steps down from one clump to the next; those steps are kept, a quarter as tall, each still showing the
higher clump's own edge. Under the edge, the foliage in place, joined along the seam where the two match best (one
row's step at most per column). The right flank (x 427..449) is lowered 5 px the same way, its edge with it. Near the
wall the crown sinks behind the low roof in front of it (its edge: y = 454 + 1.22 (x - 326)), which is left as it is,
as is the oden's blue roof. The dark top of the tree in the eave's shadow (x 326..333, down from the roof's underside)
goes too. What shows over the crown: the sky, the pagoda's foot and Fuji's left flank.
In the street's layers (layer_city_off, street_unlit, street_sun, night_far), with nothing left floating. The mountain's
layer (fuji_night.webp) starts at x 376; left of it, between its flank carried on (its slope, 0.43) and the tree, the
street's layer takes the mountain (over 376-377 too, whose two columns fade out there, where the tree hid them):
fuji_night's own pixels right of 378, mirrored, sat on the carried-on slope (their alpha with them: the same soft edge on
the sky), behind the leaves' soft edges, marked in night_far as the mountain's (160), so they take its hours.
Needs git, Pillow, numpy and scipy.
"""
import io
import os
import subprocess
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = lambda p: os.path.join(ROOT, 'assets', p)
BEFORE = 'c8de52b'                     # (the layers as they were, the tree whole)
TREE_BOX = (326, 270, 492, 572)        # x0, y0, x1, y1: the tree, right of the house's wall (x 325)
TOP = 450                              # the crown's highest point: the oden's roof
MIRROR = 334 + 426                     # the painted top (x 334..426) mirrored: x -> MIRROR - x
PIECES = [(334, 352), (353, 374), (375, 397), (398, 418), (419, 423), (424, 426)]   # its clumps, as painted (from the wall)
STEP = 0.25                            # how much of each step down between them is kept
FLANK, FLANK_DROP = (427, 449), 8      # the right flank, lowered (its top to the same height)
SEAM = (8, 22)                         # how deep the brought-down edge goes before the foliage in place
FLANK_SEAM = (5, 10)                   # (shallower over the flank: the blue roof is close under it)
ROOF = lambda x: 454 + 1.22 * (x - 326)   # the low roof in front of the tree, its upper edge
FX, SLOPE = 376, 0.43                  # fuji_night's left edge; its flank's slope there (px down per px left)


def load(p, mode='RGBA', at=None):
    data = subprocess.run(['git', 'show', f'{at}:assets/{p}'], cwd=ROOT, capture_output=True, check=True).stdout if at else open(A(p), 'rb').read()
    return np.asarray(Image.open(io.BytesIO(data)).convert(mode)).copy()


def save(arr, p, mode):
    Image.fromarray(arr.astype(np.uint8), mode).save(A(p), 'WEBP', lossless=True, quality=100, method=6, exact=True)


def main():
    city, unlit = load('layer_city_off.webp', at=BEFORE), load('street_unlit.webp', at=BEFORE)
    nf, sun = load('night_far.webp', 'RGB', at=BEFORE), load('street_sun.webp', 'RGB', at=BEFORE)
    fn = load('fuji_night.webp')
    H, W = city.shape[:2]; yy, xx = np.mgrid[0:H, 0:W]
    x0, y0, x1, y1 = TREE_BOX
    op = city[:, :, 3] > 128
    box = (xx >= x0) & (xx < x1) & (yy >= y0) & (yy < y1)
    lab, n = ndi.label(op & box, structure=np.ones((3, 3)))
    sizes = ndi.sum(op & box, lab, range(1, n + 1)); tree = lab == 1 + np.argmax(sizes)
    tree &= yy < np.ceil(ROOF(xx))                                            # (not the low roof)
    top0 = np.array([np.argmax(tree[:, x]) if tree[:, x].any() else H for x in range(W)])

    # each column: where its edge comes from (src) and how far down it is brought (shift)
    src = np.arange(W); shift = np.zeros(W, int); band = {}
    shift[PIECES[0][0]:PIECES[0][1] + 1] = TOP - top0[PIECES[0][0]]           # (the painted top's highest, by the wall, at TOP)
    for (a0, a1), (b0, b1) in zip(PIECES, PIECES[1:]):
        step = top0[b0] - top0[a1]                                            # (down, from one clump to the next, as painted)
        d = shift[a1] if step <= 0 else shift[a1] - int(round(step * (1 - STEP)))
        shift[b0:b1 + 1] = d
    for a, b in PIECES:
        for s in range(a, b + 1):
            src[MIRROR - s] = s; shift_s = shift[s]; band[MIRROR - s] = (shift_s, SEAM)
    for x in range(FLANK[0], FLANK[1] + 1): band[x] = (FLANK_DROP, FLANK_SEAM)
    ynew = top0.copy()
    for x, (d, _) in band.items(): ynew[x] = top0[src[x]] + d
    for x in range(x0, 334): ynew[x] = int(np.ceil(ROOF(x)))                 # (by the wall: behind the low roof)

    # the seam: per column, the depth under the new edge where the brought-down edge meets the foliage in place
    cols = sorted(band); D = SEAM[1] + 1
    cost = np.full((len(cols), D), 1e9)
    for i, x in enumerate(cols):
        lo, hi = band[x][1]
        for d in range(lo, hi + 1):
            c = 0.0
            for k in (-1, 0, 1):
                ys, yt = top0[src[x]] + d + k, ynew[x] + d + k
                if yt >= ROOF(x): continue                                    # (under the low roof: nothing shows)
                a, b = city[ys, src[x]], city[yt, x]
                if a[3] < 129 or b[3] < 129: c += 300; continue
                c += np.abs(a[:3].astype(float) - b[:3]).sum()
            cost[i, d] = c
    acc = cost.copy(); back = np.zeros_like(cost, int)
    for i in range(1, len(acc)):
        for j in range(D):
            lo, hi = max(0, j - 1), min(D, j + 2)
            k = lo + int(np.argmin(acc[i - 1, lo:hi])); acc[i, j] += acc[i - 1, k]; back[i, j] = k
    seam = np.zeros(len(cols), int); seam[-1] = int(np.argmin(acc[-1]))
    for i in range(len(acc) - 1, 0, -1): seam[i - 1] = back[i, seam[i]]

    out = [L.copy() for L in (city, unlit, nf, sun)]
    cut = np.zeros((H, W), bool); moved = np.zeros((H, W), bool)
    for x in range(x0, x1): cut[y0:ynew[x], x] = tree[y0:ynew[x], x]          # (over the new edge: nothing of the tree)
    for i, x in enumerate(cols):
        for d in range(seam[i]):
            ys, yt = top0[src[x]] + d, ynew[x] + d
            if yt >= ROOF(x) or not (tree[yt, x] or city[yt, x, 3] == 0): continue
            for o, L in zip(out, (city, unlit, nf, sun)): o[yt, x] = L[ys, src[x]]
            moved[yt, x] = True
    cut &= ~moved
    # the tree's dark top in the eave's shadow, by the wall: down from the roof's underside (13 px under its upper edge)
    for x in range(x0, 334):
        eave = int(np.argmax(city[180:, x, 3] > 128)) + 180
        cut[eave + 13:ynew[x], x] = True
    for o in out[:2]: o[cut] = 0
    out[2][cut] = 0; out[3][cut] = 0
    city, unlit, nf, sun = out
    # nothing left floating, nor faint: what of the tree the cut or the move parted from its body goes too (twice), and
    # any faint pixel of its edge over it
    body = (city[:, :, 3] > 128) & box
    for _ in range(2):
        lab, n = ndi.label(body, structure=np.ones((3, 3)))
        sizes = ndi.sum(body, lab, range(1, n + 1)); main = 1 + np.argmax(sizes)
        near = ndi.binary_dilation(cut | moved, iterations=2)
        parted = np.unique(lab[near & body]); parted = parted[(parted > 0) & (parted != main)]
        bits = np.isin(lab, parted)
        for L in (city, unlit): L[bits] = 0
        nf[bits] = 0; sun[bits] = 0; body &= ~bits; cut |= bits
    faint = box & (city[:, :, 3] > 0) & (city[:, :, 3] <= 128) & (yy < ynew[None, :] + 2) & ~ndi.binary_dilation(body) \
        & ndi.binary_dilation(tree, iterations=2)                            # (the tree's own soft edge: not the rain painted in the sky)
    for L in (city, unlit): L[faint] = 0
    nf[faint] = 0; sun[faint] = 0

    # the mountain carried on left of fuji_night, under its flank's line, behind what of the street is there
    ftop = np.array([np.argmax(fn[:, c, 3] > 30) for c in range(fn.shape[1])]) + 66
    M = FX + 2                                                                # (its first two columns fade out where the tree hid them)
    y_edge = lambda x: ftop[M - FX] + (M - x) * SLOPE                         # (its line from its first full column)
    ext = 0
    for x in range(x0, M):
        sx = 2 * M - x - FX                                                   # (mirrored about its first full column, over the faded ones)
        dy = int(round(y_edge(x) - ftop[sx]))
        for y in range(int(np.floor(y_edge(x))) - 3, min(ynew[x] + SEAM[1] + 2, int(np.ceil(ROOF(x))) + 1)):
            sy = y - dy - 66
            if not (0 <= sy < fn.shape[0]) or fn[sy, sx, 3] == 0 or city[y, x, 3] == 255: continue
            am, ac = fn[sy, sx, 3] / 255.0, city[y, x, 3] / 255.0
            ao = ac + am * (1 - ac)
            for L in (city, unlit):
                L[y, x, :3] = np.round((L[y, x, :3] * ac + fn[sy, sx, :3] * am * (1 - ac)) / ao); L[y, x, 3] = round(ao * 255)
            if ac == 0: nf[y, x] = 160; sun[y, x] = 0
            ext += 1
    save(city, 'layer_city_off.webp', 'RGBA'); save(unlit, 'street_unlit.webp', 'RGBA')
    save(nf, 'night_far.webp', 'RGB'); save(sun, 'street_sun.webp', 'RGB')
    print('crown', min(ynew[x] for x in cols), '..', max(ynew[x] for x in cols), '| pieces moved', sorted(set(shift[a] for a, _ in PIECES)),
          '| seam depth', seam.min(), '..', seam.max(), '| cut', int(cut.sum()), 'px | mountain carried on', ext, 'px')


if __name__ == '__main__':
    main()
