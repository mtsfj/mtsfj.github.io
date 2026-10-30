#!/usr/bin/env python3
"""The tree between the drinks shop and the oden (A), replaced: a new tree behind the shop, in front of the oden's roof.

    python3 tools/tree_a.py      (reads the layers as they were before any change to that tree, at commit aa383bc;
                                  then tools/fuji_aux.py)

The old tree rose 170 px over the roofs. The new one (tools/src/tree_a.jpg, a pixel-art tree drawn on white) stands where
the old one stood, in the depth the painting gives it: behind the drinks shop's roof and the lantern, in front of the oden's
blue roof, whose upper left corner it hides as the old one did (that corner was never painted). Its crown: 136 px wide, its
top at y 452 (the oden's roof: 450), from x 330 to 466; the shop's roof cuts its lower left (it goes on behind it), its foot
is in the alley between the two shops, among the old tree's dark leaves there (kept below y 515, behind the lantern).
Its colours: the old tree's own (its leaves by lightness, its blossoms by lightness), so every hour grades it as it graded
the old one; the power cut: the old tree's own change there, position by position (the lantern's and the sign's light on
its leaves). Everything of the old tree above that is gone: the sky, the pagoda's foot, Fuji's flank (carried on in the
street's layer left of x 378, as the mountain: night_far 160), and the oden's roof edge where the old sprigs stood on it.
In layer_city_off, street_unlit, night_far (the tree: 0) and street_sun (0). Needs git, Pillow, numpy and scipy.
"""
import io
import os
import subprocess
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = lambda p: os.path.join(ROOT, 'assets', p)
BEFORE = 'aa383bc'
SRC = os.path.join(ROOT, 'tools', 'src', 'tree_a.jpg')
GRID, PHASE = 5.12, (4.25, 4.25)                  # the source's pixel grid (200 pixels across) and its offset
MIRROR = False                                    # (its trunk on the left: in the little alley behind the drinks shop, out of sight)
TREE_X, TREE_Y = 284, 400                         # its tree's top left in the scene, one source pixel to one
CUT_BELOW = 860                                   # (the source's rows under this, the trunk's foot and its rock: hidden anyway)
KEEP_Y = 556                                      # the old tree's dark leaves kept low in the alley, round the lantern, below this
DEEP_DX, DEEP_DY, DEEP_SHADE = -26, 40, 0.62      # its leaves further in: the drawing again, lower, in shade (its right edge over the
                                                  # oden's roof end, leafy, as the old tree's was)
SHADOW = (470, 545, 0.45)                         # the buildings' shade on its lower part: from y, to y, how much darker at the foot
M0 = 378                                          # (left of this the mountain is carried on in the street's layer, down to the roof)
ROOF = lambda x: 454 + 1.22 * (x - 326)           # the drinks shop's roof, in front: its upper edge
EDGE = lambda x: 465 + 0.62 * (x - 437)           # the oden's blue roof, its upper edge (as painted from x 437 to 474)
ROOF_X0 = lambda y: 431 - 0.22 * (y - 470)        # its left end, slanting out to its eave's foot (ROOF_Y1), as painted
ROOF_Y1 = 524
FX, SLOPE = 376, 0.43                             # fuji_night's left edge; its flank's slope there
OUT = os.environ.get('OUT')                       # (a folder: write the layers there instead of assets/)


def load(p, mode='RGBA', at=None):
    data = subprocess.run(['git', 'show', f'{at}:assets/{p}'], cwd=ROOT, capture_output=True, check=True).stdout if at else open(A(p), 'rb').read()
    return np.asarray(Image.open(io.BytesIO(data)).convert(mode)).copy()


def save(arr, p, mode):
    path = os.path.join(OUT, p) if OUT else A(p)
    Image.fromarray(np.clip(np.round(arr), 0, 255).astype(np.uint8), mode).save(path, 'WEBP', lossless=True, quality=100, method=6, exact=True)


def crown():
    """The source's tree, read off its pixel grid (each pixel the median of its cell's middle), cut out of its white ground:
    (rgb, alpha), one pixel per source pixel."""
    a = np.asarray(Image.open(SRC).convert('RGB')).astype(float)
    nx, ny = int((a.shape[1] - PHASE[0]) // GRID), int((a.shape[0] - PHASE[1]) // GRID)
    rgb = np.zeros((ny, nx, 3))
    for j in range(ny):
        for i in range(nx):
            x0, y0 = int(round(PHASE[0] + i * GRID)), int(round(PHASE[1] + j * GRID))
            rgb[j, i] = np.median(a[y0 + 1:y0 + 4, x0 + 1:x0 + 4].reshape(-1, 3), 0)
    al = rgb @ [0.299, 0.587, 0.114] < 225
    al[int((CUT_BELOW - PHASE[1]) // GRID):] = False
    lab, n = ndi.label(al); al = lab == 1 + np.argmax(ndi.sum(al, lab, range(1, n + 1)))   # (the tree: nothing floating)
    ys, xs = np.where(al)
    rgb, al = rgb[ys.min():ys.max() + 1, xs.min():xs.max() + 1], al[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    return (rgb[:, ::-1], al[:, ::-1]) if MIRROR else (rgb, al)


def by_lightness(ref, L):
    """The mean colour of the reference pixels at each lightness, interpolated."""
    RL = ref @ [0.299, 0.587, 0.114]; bins = np.linspace(RL.min(), RL.max(), 24); idx = np.digitize(RL, bins); cent, cols = [], []
    for k in range(1, len(bins) + 1):
        m = idx == k
        if m.sum() >= 8: cent.append(RL[m].mean()); cols.append(ref[m].mean(0))
    cent, cols = np.array(cent), np.array(cols)
    return np.stack([np.interp(L, cent, cols[:, ch]) for ch in range(3)], -1), RL


def main():
    city, unlit = load('layer_city_off.webp', at=BEFORE).astype(float), load('street_unlit.webp', at=BEFORE).astype(float)
    nf, sun = load('night_far.webp', 'RGB', at=BEFORE), load('street_sun.webp', 'RGB', at=BEFORE)
    fn = load('fuji_night.webp')
    H, W = city.shape[:2]; yy, xx = np.mgrid[0:H, 0:W]
    r, g, b = city[:, :, 0], city[:, :, 1], city[:, :, 2]

    # what stands in front of the tree, untouched: the shop's roof, the house's wall, the lantern, the oden's sign, its upper floor,
    # its front under the blue roof
    lantern = ndi.binary_dilation((r > 150) & (r > g + 60) & (abs(xx - 409) < 14) & (abs(yy - 552) < 18), iterations=1)
    lantern = ndi.binary_fill_holes(ndi.binary_closing(lantern, iterations=2))
    front = (yy >= ROOF(xx)) & (xx <= 400) | (xx <= 325) | lantern | ((xx >= 478) & (yy >= 483)) | ((xx >= 487) & (yy >= 448)) \
        | ((xx >= 420) & (yy >= 525))
    # the oden's blue roof, in front of the tree: under its upper edge, right of its left end; the old tree's leaves painted
    # over it (its sprigs on the edge, its leaves low on its left) give way to the roof itself, each from the nearest clean
    # pixel of the roof along its own lines (they run at its edge's slope), in each layer
    roof = (xx >= np.round(ROOF_X0(yy))) & (xx < 478) & (yy >= np.ceil(EDGE(xx))) & (yy <= ROOF_Y1)
    clean = roof & (xx >= 448)
    prof = {}
    for y, x in zip(*np.where(clean)):
        prof.setdefault(int(round(y - 0.62 * x)), []).append(city[y, x, :3])
    prof = {k: np.median(np.array(v), 0) for k, v in prof.items()}
    leafy = np.zeros((H, W), bool)
    for y, x in zip(*np.where(roof & (xx < 448))):
        k = int(round(y - 0.62 * x))
        if k in prof and np.abs(city[y, x, :3] - prof[k]).sum() > 45: leafy[y, x] = True
    leafy = ndi.binary_dilation(leafy) & roof & (xx < 448)
    src0 = city.copy(), unlit.copy()
    for y, x in zip(*np.where(leafy)):
        k = int(round(y - 0.62 * x))
        for d in range(1, 90):                                                # (the roof's own pixel further along its line)
            sx, sy = x + d, int(round(y + 0.62 * d))
            if sx >= 478 or sy > ROOF_Y1: break
            if roof[sy, sx] and not leafy[sy, sx] and k in prof and np.abs(src0[0][sy, sx, :3] - prof[k]).sum() <= 30:
                city[y, x] = src0[0][sy, sx]; unlit[y, x] = src0[1][sy, sx]; break
    # the old tree: the street's opaque pixels joined to it in its box, not those in front nor the roof
    op = city[:, :, 3] > 0
    box = (xx >= 326) & (xx < 492) & (yy >= 270) & (yy < 580)
    lab, n = ndi.label(op & box & ~front & ~roof, structure=np.ones((3, 3)))
    old = lab == 1 + np.argmax(ndi.sum(op & box & ~front, lab, range(1, n + 1)))
    old |= box & ~front & ~roof & op & ndi.binary_dilation(old, iterations=2) & (city[:, :, 3] <= 128)   # (its soft edge)

    # the crown, coloured as the old tree
    rgb, al = crown(); h, w = al.shape
    px = city[old & (city[:, :, 3] > 200) & (yy < 520)][:, :3]
    pink = lambda q: (q[..., 0] > q[..., 2] + 12) & (q[..., 0] > q[..., 1] + 20) & (q[..., 0] > 60)
    Ls = rgb @ [0.299, 0.587, 0.114]
    rim = al & ~ndi.binary_erosion(al, iterations=3)                          # (the drawing's pink outline along its edge: leaves)
    r_, g_, b_ = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    wood = al & (r_ > b_ + 4) & (r_ > g_ + 4) & (r_ < 1.5 * g_) & ~pink(rgb)  # (its brown wood: not the blossoms' crimson shade)
    wood[:int(0.45 * wood.shape[0])] = False                                 # (low in the drawing: the trunk and its boughs)
    lab_, n_ = ndi.label(wood, structure=np.ones((3, 3)))
    trunk = lab_ == 1 + np.argmax(ndi.sum(wood, lab_, range(1, n_ + 1))) if n_ else wood
    sp = pink(rgb) & al & ~rim; sf = al & ~sp & ~trunk
    out = rgb.copy()
    for m, ref in ((sf, px[~pink(px)]), (sp, px[pink(px)])):
        if not m.any(): continue
        qs = np.linspace(0, 100, 101); RL = ref @ [0.299, 0.587, 0.114]
        L2 = np.interp(Ls[m], np.percentile(Ls[m], qs), np.percentile(RL, qs))
        out[m] = by_lightness(ref, L2)[0]
    if trunk.any():                                                           # (the wood: the right cherry's, as painted in the same light)
        ft = load('fuji_tree.webp').astype(float); fr, fg_, fb_, fa = ft[..., 0], ft[..., 1], ft[..., 2], ft[..., 3]
        ref = ft[(fa > 200) & (fr < 1.4 * fg_) & (fr > fb_) & (fr + fg_ + fb_ < 330)][:, :3]
        qs = np.linspace(0, 100, 101); RL = ref @ [0.299, 0.587, 0.114]
        L2 = np.interp(Ls[trunk], np.percentile(Ls[trunk], qs), np.percentile(RL, np.linspace(35, 100, 101)))
        out[trunk] = by_lightness(ref, L2)[0]                                 # (its lighter half: the bough reads on the shade)
    cm = np.zeros((H, W), bool); cc = np.zeros((H, W, 3))
    cm[TREE_Y:TREE_Y + h, TREE_X:TREE_X + w] = al; cc[TREE_Y:TREE_Y + h, TREE_X:TREE_X + w] = out
    cm &= ~front                                                              # (in front of the oden's roof end, as the old tree was)

    # the power cut: the old tree's own change, by place (each channel's ratio, smoothed over its pixels)
    wt = ndi.gaussian_filter(old.astype(float), 6)
    ratio = np.stack([ndi.gaussian_filter(np.where(old, (unlit[:, :, ch] + 1) / (city[:, :, ch] + 1), 0), 6) for ch in range(3)], -1) / np.maximum(wt, 1e-6)[..., None]
    ratio = np.where(wt[..., None] > 0.02, np.clip(ratio, 0.3, 1.0), 1.0)

    # out: the old tree over the crown's outline and above the alley's leaves; what of it stood on the blue roof
    # all of the old tree goes, but low in the alley, round the lantern (below KEEP_Y): no old leaves mixed with the new ones
    gone = old & ~cm & ~((xx >= 376) & (xx <= 425) & (yy >= KEEP_Y))
    for L in (city, unlit): L[gone] = 0
    nf[gone] = 0; sun[gone] = 0
    # the mountain carried on left of fuji_night, down to the shop's roof, where the old tree was
    ftop = np.array([np.argmax(fn[:, c, 3] > 30) for c in range(fn.shape[1])]) + 66; M = FX + 2
    y_edge = lambda x: ftop[M - FX] + (M - x) * SLOPE
    ext = 0
    for x in range(326, M):
        sx = 2 * M - x - FX; dy = int(round(y_edge(x) - ftop[sx]))
        for y in range(int(np.floor(y_edge(x))) - 3, int(np.ceil(ROOF(x))) + 1):
            if not gone[y, x] and city[y, x, 3] > 0: continue
            sy = y - dy - 66
            if not (0 <= sy < fn.shape[0]) or fn[sy, sx, 3] == 0: continue
            for L in (city, unlit): L[y, x, :3] = fn[sy, sx, :3]; L[y, x, 3] = fn[sy, sx, 3]
            nf[y, x] = 160; sun[y, x] = 0; ext += 1
    # the eave's shadow by the wall: the old tree's dark top under the house's roof (x 326..333), down to the shop's roof
    for x in range(326, 334):
        eave = int(np.argmax(city[180:, x, 3] > 128)) + 180
        for y in range(eave + 13, min(270, int(ROOF(x)))):
            for L in (city, unlit): L[y, x] = 0
            nf[y, x] = 0

    # the old tree's leaves painted over the oden's front, left of its noren (418..434, 526..546): its dark front there, from
    # its own dark pixels round them (each layer its own), the lantern and the noren's orange untouched
    fb = (xx >= 418) & (xx <= 434) & (yy >= 526) & (yy <= 546) & ~lantern
    for L in (city, unlit):
        Lr, Lg, Lb = L[:, :, 0], L[:, :, 1], L[:, :, 2]; Lum = L[:, :, :3] @ [0.299, 0.587, 0.114]
        orange = (Lr > 80) & (Lr > 2.5 * Lb)
        leaf = fb & ~orange & ((Lum > 35) | ((Lr - Lb > 15) & (Lr > 45)))
        dark = fb & ~orange & ~leaf
        for ch in range(3):
            num = ndi.gaussian_filter(np.where(dark, L[:, :, ch], 0), 2.5); den = ndi.gaussian_filter(dark.astype(float), 2.5)
            L[leaf, ch] = (num / np.maximum(den, 1e-6))[leaf]

    # under its crown, down to the shop's roof, the lantern and the oden: its own leaves further in, in the crown's shade (the
    # same drawing, lower and darker, behind it), over the blue roof's left end with their leafy edge; no sky, no old leaves
    top = np.where(cm.any(0), np.argmax(cm, 0), H)
    under = (xx >= 326) & (yy > top[None, :]) & (yy < 560) & ~cm & ~front
    dm = np.zeros((H, W), bool); dc = np.zeros((H, W, 3))
    y0, x0 = TREE_Y + DEEP_DY, TREE_X + DEEP_DX
    dm[y0:y0 + h, max(x0, 0):x0 + w] = al[:, max(0, -x0):]; dc[y0:y0 + h, max(x0, 0):x0 + w] = out[:, max(0, -x0):] * DEEP_SHADE
    deep = under & dm
    hole = under & ~dm & ~roof & (xx < 425)                                   # (what its drawing leaves open there: its darkest leaves)
    dark = np.percentile(cc[cm].reshape(-1, 3) @ [0.299, 0.587, 0.114], 5); dark_rgb = cc[cm][np.argmin(np.abs(cc[cm] @ [0.299, 0.587, 0.114] - dark))]
    dc[hole] = dark_rgb
    shade = (1 - SHADOW[2] * np.clip((yy - SHADOW[0]) / (SHADOW[1] - SHADOW[0]), 0, 1))[..., None]
    dc *= shade; cc *= shade
    for m in (deep, hole):
        city[m, :3] = dc[m]; city[m, 3] = 255
        unlit[m, :3] = dc[m] * ratio[m]; unlit[m, 3] = 255
        nf[m] = 0; sun[m] = 0

    # the crown, in front of what stays behind it
    city[cm, :3] = cc[cm]; city[cm, 3] = 255
    unlit[cm, :3] = cc[cm] * ratio[cm]; unlit[cm, 3] = 255
    nf[cm] = 0; sun[cm] = 0
    save(city, 'layer_city_off.webp', 'RGBA'); save(unlit, 'street_unlit.webp', 'RGBA')
    save(nf, 'night_far.webp', 'RGB'); save(sun, 'street_sun.webp', 'RGB')
    print('tree', w, 'x', h, 'px at', (TREE_X, TREE_Y), '| old tree out', int(gone.sum()), 'px | mountain carried on', ext, 'px')


if __name__ == '__main__':
    main()
