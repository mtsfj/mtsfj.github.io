#!/usr/bin/env python3
"""The roof garden over Naruto's window in the wind: what the street's script needs to move its plants (assets/roof_sway.webp).

    python3 tools/roof_sway.py      (after tools/naruto_roof.py; it replays that tool on the layers as they were before it)

(Superseded: the garden now stands on the parapet redrawn by tools/naruto_floor.py, which writes assets/roof_sway.webp
the same way, with foliage_own() and the rules below; this replay no longer matches the layers and stops.)

The garden (tools/naruto_roof.py: the maple's crown in tiers, the shrubs' cushions, the low hedge) is painted into the
street's layers. To move it the script needs what is behind each plant and which plant each pixel is. This replays
naruto_roof.py on the layers of commit BEFORE (in memory: nothing is written but the data file), checks that it gives the
layers as they are now in the garden's box, pixel for pixel, and keeps, in the box (BOX: x, y, w, h), three blocks one
under the other:
  - rows 0..h-1: what each plant covers in layer_city_off (the wall of building C, its coping, the maple's trunk and
    limbs; transparent where the sky is behind), the layer elsewhere;
  - rows h..2h-1: the same in street_unlit (the power cut, the finale's dark street);
  - rows 2h..3h-1: R the plant (16 + its clump: the maple's crown 16..26; 32 + a shrub's cushion; 48 + a clump of the
    hedge; 0 what never moves: the wall, the sky, the trunk, and the few leaves the street lamp lights, which the red night
    paints from the lit layer); G how free the pixel is (0..255: the maple's crown more toward its top and its tiers' ends,
    a cushion's or the hedge's top rows only, the hedge still under the menu's text); B 255 where a leaf may show (over the street's parapet, right of C's corner:
    the clip naruto_roof.py painted them with); A 255.
The script (assets/street.js, its ROOF block) moves them on the scene's gusts as the cherry's rustle does.
Needs git, Pillow, numpy.
"""
import io
import os
import subprocess
import sys
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import naruto_roof as NR   # noqa: E402

BEFORE = '1a17325^'          # (the layers before naruto_roof.py: the old floor still there)
OUT = os.path.join(ROOT, 'assets', 'roof_sway.webp')
MASSES = ('maple', 'shrubs', 'hedge')
HEDGE_CALM = 44             # (naruto_roof.py keeps the hedge dark above this row: the menu's text is over it on a 16:9 window)
LAMP_LIT = 0.04              # a leaf lit by the street lamp more than this (luminance, lit over unlit) never moves
LUM = np.array([0.299, 0.587, 0.114])


def gload(p, mode='RGBA'):
    data = subprocess.run(['git', 'show', f'{BEFORE}:assets/{p}'], cwd=ROOT, capture_output=True, check=True).stdout
    return np.asarray(Image.open(io.BytesIO(data)).convert(mode)).astype(float)


def foliage_own(clumps, rank, seed, clip, lift=0.0, rim=1.6, spots=0.0):
    """naruto_roof.foliage, keeping each leaf's clump (the clump that painted it last): {(x, y): k}"""
    rng = np.random.default_rng(seed); th, tw = rank.shape
    own = {}
    for k, (cx, cy, rx, ry) in enumerate(clumps):
        nb = 24; bump = np.convolve(rng.random(nb + 4), np.ones(3) / 3, 'valid')[:nb]
        for y in range(int(cy - ry - 3), int(cy + ry + 3)):
            for x in range(int(cx - rx - 3), int(cx + rx + 4)):
                nx, ny = (x - cx) / rx, (y - cy) / ry; d = np.hypot(nx, ny)
                a = (np.arctan2(ny, nx) / (2 * np.pi) + 0.5) * nb; e = bump[int(a) % nb] * (1 - a % 1) + bump[int(a + 1) % nb] * (a % 1)
                g = rank[(y + 13 * seed) % th, (x + 7 * seed) % tw]
                lim = 1.0 + 0.32 * (e - 0.5) / max(rx, ry) * 6 + (0.12 if g < 0.12 else -0.1 if g > 0.85 else 0.0)
                if d <= lim and clip(x, y): own[(x, y)] = k
    return own


def main():
    NR.load = gload
    rec = {'calls': [], 'clumps': [], 'clip': None}

    class Layers(NR.Layers):
        def save(s): rec['final'] = (s.city.copy(), s.unlit.copy())
    NR.Layers = Layers
    plain = NR.foliage

    def foliage(clumps, rank, seed, clip, *a, **k):
        if not rec['calls']: rec['under'] = (rec['Ls'].city.copy(), rec['Ls'].unlit.copy())   # (the trunk and limbs in, no leaf yet)
        px = plain(clumps, rank, seed, clip, *a, **k)
        own = foliage_own(clumps, rank, seed, clip, *a, **k)
        rec['calls'].append((px, own)); rec['clumps'].append(list(clumps)); rec['clip'] = clip
        return px
    NR.foliage = foliage
    garden = NR.garden

    def garden_rec(Ls):
        rec['Ls'] = Ls; garden(Ls)
    NR.garden = garden_rec
    NR.main()

    # the replay is the layers as they are now, in the garden's box
    cur = [np.asarray(Image.open(os.path.join(ROOT, 'assets', n)).convert('RGBA')).astype(float) for n in ('layer_city_off.webp', 'street_unlit.webp')]
    fin = [np.clip(np.round(a), 0, 255) for a in rec['final']]
    under = [np.clip(np.round(a), 0, 255) for a in rec['under']]

    mass = {}; clump = {}
    for m, (px, own) in enumerate(rec['calls']):
        for q in px: mass[q] = m + 1; clump[q] = own[q]
    xs = [q[0] for q in mass]; ys = [q[1] for q in mass]
    x0, y0 = min(xs) - 3, max(0, min(ys) - 3); x1, y1 = max(xs) + 4, max(ys) + 4
    W, H = x1 - x0, y1 - y0
    for a, b, n in zip(fin, cur, ('layer_city_off', 'street_unlit')):
        d = np.abs(a[y0:y1, x0:x1] - b[y0:y1, x0:x1]).max()
        if d > 0: sys.exit(f'roof_sway: {n} differs from the replay in the box ({d}): run it on the layers naruto_roof.py made')

    out = np.zeros((3 * H, W, 4), np.uint8)
    out[0:H] = under[0][y0:y1, x0:x1]
    out[H:2 * H] = under[1][y0:y1, x0:x1]
    clip = rec['clip']
    L = fin[0][:, :, :3] @ LUM / 255.0; Lu = fin[1][:, :, :3] @ LUM / 255.0
    # each plant's own extent, for how free each of its pixels is
    ext = {}
    for q, m in mass.items():
        e = ext.setdefault(m, [1e9, -1e9, 1e9, -1e9]); e[0] = min(e[0], q[0]); e[1] = max(e[1], q[0]); e[2] = min(e[2], q[1]); e[3] = max(e[3], q[1])
    ctop = {}                                                 # (a cushion's or a hedge clump's top row at each column)
    for q, m in mass.items():
        if m > 1: key = (m, clump[q], q[0]); ctop[key] = min(ctop.get(key, 1e9), q[1])
    fixed = 0
    for y in range(y0, y1):
        for x in range(x0, x1):
            o = out[2 * H + y - y0, x - x0]
            o[3] = 255; o[2] = 255 if clip(x, y) else 0
            m = mass.get((x, y))
            if not m: continue
            if L[y, x] - Lu[y, x] > LAMP_LIT: fixed += 1; continue
            k = clump[(x, y)]
            if m == 1:                                        # the maple: its crown from the fork up (y 100) to its top, its tiers' ends
                cx, cy, rx, ry = rec['clumps'][0][k]
                up = np.clip((100 - y) / (100 - ext[1][2]), 0, 1); out_ = np.clip(abs(x - cx) / rx, 0, 1)
                f = (0.35 + 0.65 * up) * (0.75 + 0.25 * out_)
            else:                                             # a cushion, the hedge: its top rows only (clipped: stiff); the
                d = y - ctop[(m, k, x)]                       # hedge still under the menu's text on a 16:9 window (y < HEDGE_CALM)
                f = max(0.0, 1.0 - d / 4.0) * (0.8 if m == 2 else 0.6 * float(np.clip((y - HEDGE_CALM) / 4.0, 0, 1)))
            o[0] = 16 * m + k; o[1] = int(round(255 * f))
    Image.fromarray(out, 'RGBA').save(OUT, 'WEBP', lossless=True, quality=100, method=6, exact=True)
    back = np.asarray(Image.open(OUT).convert('RGBA'))
    assert (back == out).all(), 'roof_sway: the WebP is not the data'
    print(f'roof_sway: box x {x0} y {y0} w {W} h {H}; leaves', {n: sum(1 for v in mass.values() if v == i + 1) for i, n in enumerate(MASSES)}, '; lamp-lit, kept still:', fixed)


if __name__ == '__main__':
    main()
