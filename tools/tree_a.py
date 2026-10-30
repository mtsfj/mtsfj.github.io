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
CROWN_X, CROWN_TOP, CROWN_W = 330, 452, 136       # its crown: left, top, width (the source drawn on a 5.12 px grid)
TRUNK_FROM = 0.80                                 # (the source's rows below this share of its height: the trunk, left out)
BUSH_Y = 515                                      # the old tree's dark leaves kept in the alley below this
ROOF = lambda x: 454 + 1.22 * (x - 326)           # the drinks shop's roof, in front: its upper edge
EDGE = lambda x: 484 + 0.5 * (x - 464)            # the oden's blue roof, its upper edge (painted from x 464)
FX, SLOPE = 376, 0.43                             # fuji_night's left edge; its flank's slope there
OUT = os.environ.get('OUT')                       # (a folder: write the layers there instead of assets/)


def load(p, mode='RGBA', at=None):
    data = subprocess.run(['git', 'show', f'{at}:assets/{p}'], cwd=ROOT, capture_output=True, check=True).stdout if at else open(A(p), 'rb').read()
    return np.asarray(Image.open(io.BytesIO(data)).convert(mode)).copy()


def save(arr, p, mode):
    path = os.path.join(OUT, p) if OUT else A(p)
    Image.fromarray(np.clip(np.round(arr), 0, 255).astype(np.uint8), mode).save(path, 'WEBP', lossless=True, quality=100, method=6, exact=True)


def crown():
    """The source's tree, cut out of its white ground, its trunk left out, at CROWN_W wide: (rgb, alpha)."""
    src = Image.open(SRC).convert('RGB'); a = np.asarray(src).astype(float)
    fg = a @ [0.299, 0.587, 0.114] < 225
    lab, n = ndi.label(fg); fg = lab == 1 + np.argmax(ndi.sum(fg, lab, range(1, n + 1)))
    ys, xs = np.where(fg); x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    y1 = y0 + int((y1 - y0) * TRUNK_FROM)
    w = CROWN_W; h = round((y1 - y0) * w / (x1 - x0))
    rgb = np.asarray(src.crop((x0, y0, x1, y1)).resize((w, h), Image.LANCZOS)).astype(float)
    al = np.asarray(Image.fromarray((fg[y0:y1, x0:x1] * 255).astype(np.uint8)).resize((w, h), Image.BOX)).astype(float) / 255 > 0.5
    lab, n = ndi.label(al); al = lab == 1 + np.argmax(ndi.sum(al, lab, range(1, n + 1)))   # (nothing floating)
    return rgb, al


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
    # the oden's blue roof under its upper edge: behind the tree, kept as painted (the old tree's leaves on it with it)
    roof = (xx >= 420) & (xx < 478) & (yy >= EDGE(xx)) & (yy < 525)
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
    rim = al & ~ndi.binary_erosion(al, iterations=2)                          # (the drawing's pink outline along its edge: leaves)
    sp = pink(rgb) & al & ~rim; sf = al & ~sp
    out = rgb.copy()
    for m, ref in ((sf, px[~pink(px)]), (sp, px[pink(px)])):
        if not m.any(): continue
        qs = np.linspace(0, 100, 101); RL = ref @ [0.299, 0.587, 0.114]
        L2 = np.interp(Ls[m], np.percentile(Ls[m], qs), np.percentile(RL, qs))
        out[m] = by_lightness(ref, L2)[0]
    cm = np.zeros((H, W), bool); cc = np.zeros((H, W, 3))
    cm[CROWN_TOP:CROWN_TOP + h, CROWN_X:CROWN_X + w] = al; cc[CROWN_TOP:CROWN_TOP + h, CROWN_X:CROWN_X + w] = out
    cm &= ~front

    # the power cut: the old tree's own change, by place (each channel's ratio, smoothed over its pixels)
    wt = ndi.gaussian_filter(old.astype(float), 6)
    ratio = np.stack([ndi.gaussian_filter(np.where(old, (unlit[:, :, ch] + 1) / (city[:, :, ch] + 1), 0), 6) for ch in range(3)], -1) / np.maximum(wt, 1e-6)[..., None]
    ratio = np.where(wt[..., None] > 0.02, np.clip(ratio, 0.3, 1.0), 1.0)

    # out: the old tree over the crown's outline and above the alley's leaves; what of it stood on the blue roof
    gone = old & ~cm & ~((xx >= 376) & (xx <= 425) & (yy >= BUSH_Y))
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

    # the crown, in front of what stays behind it
    city[cm, :3] = cc[cm]; city[cm, 3] = 255
    unlit[cm, :3] = cc[cm] * ratio[cm]; unlit[cm, 3] = 255
    nf[cm] = 0; sun[cm] = 0
    save(city, 'layer_city_off.webp', 'RGBA'); save(unlit, 'street_unlit.webp', 'RGBA')
    save(nf, 'night_far.webp', 'RGB'); save(sun, 'street_sun.webp', 'RGB')
    print('crown', w, 'x', h, 'px at', (CROWN_X, CROWN_TOP), '| old tree out', int(gone.sum()), 'px | mountain carried on', ext, 'px')


if __name__ == '__main__':
    main()
