#!/usr/bin/env python3
"""The eave under Kirua (the left house's roof edge, right end): its gutter's downpipe.

    python3 tools/kirua_gutter.py      (after tools/tree_a.py and tools/tree_bc.py; it takes its zone back from
                                        commit BEFORE each time, so it can be run again)

The eave runs on past the house's corner (x 325) into the sky, its gutter closed by the painter's own end cap at x 357.
Kirua sits on that eave, his feet swinging over it: his two legs, in every frame, cover x 326..353 down to y 226, so a
downpipe from anywhere along it would stand under a boot and read as a third shin. The gutter drains at its very end,
past where his boots reach in all but his farthest kicks: a small collecting box under the end cap (as on the houses of
the references), a short drop, a swan neck back toward the house along the street's line (45 degrees here, a clean
one-for-one stair), and the pipe down the house's end wall, one pixel clear of the corner (its lit arris kept), held by
three clamps whose arms reach back across that gap to the wall; it goes on down behind the low roof in front of it (that
roof's upper edge: y = 454 + 1.22 (x - 326)). Its metal is the gutter's own: each pixel takes the colour of a pixel of
the gutter (in each layer the same pixel, so the power cut and the red night read it as they read the gutter), chosen by
where it lies across the pipe (the side toward the house dark, toward the open sky lit, the gutter's lit rim on that
edge, a tube's two lit edges on the swan neck), in short vertical runs, with a few of the gutter's specular dashes; a
collar at each bend. Where the street's lights reach the wall beside it (the red night's patch, x 299..324, y 340..422),
its side toward the wall takes half of that light, and the clamps with it. In layer_city_off, street_unlit, night_far
(0, the street's) and street_sun (the corner's own sun on its side toward the sky). Needs git, Pillow, numpy.
"""
import io
import os
import subprocess
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = lambda p: os.path.join(ROOT, 'assets', p)
BEFORE = '6c8530a'                   # (the layers as they were, the eave untouched)
ZONE = (296, 196, 372, 470)          # x0, y0, x1, y1: taken back from BEFORE before anything is drawn
GUTTER = (330, 356)                  # the gutter's columns past the corner, where its colours are taken
BOX = (350, 356, 5)                  # the collecting box: its columns, its height (hung under the gutter's underside)
DROP = (353, 252)                    # the drop's foot, where the swan neck starts (its axis)
RUN_X = 329                          # the pipe's axis down the wall (its columns 327..331; the corner arris is x 322..325)
NECK = (275, 330)                    # where the swan neck meets it: its last row, its axis there (clear of the corner)
CLAMPS = (322, 372, 422)             # the clamps (first of their two rows)
ROOF = lambda x: 454 + 1.22 * (x - 326)   # the low roof's upper edge, in front of the pipe
SEED = 33


def load(p, mode='RGBA', at=None):
    data = subprocess.run(['git', 'show', f'{at}:assets/{p}'], cwd=ROOT, capture_output=True, check=True).stdout if at else open(A(p), 'rb').read()
    return np.asarray(Image.open(io.BytesIO(data)).convert(mode)).astype(float)


def save(arr, p, mode):
    Image.fromarray(np.clip(np.round(arr), 0, 255).astype(np.uint8), mode).save(A(p), 'WEBP', lossless=True, quality=100, method=6, exact=True)


def main():
    names = (('layer_city_off.webp', 'RGBA'), ('street_unlit.webp', 'RGBA'), ('night_far.webp', 'RGB'), ('street_sun.webp', 'RGB'))
    L = [load(n, m) for n, m in names]
    B = [load(n, m, BEFORE) for n, m in names]
    x0, y0, x1, y1 = ZONE
    for l, b in zip(L, B): l[y0:y1, x0:x1] = b[y0:y1, x0:x1]
    city, unlit, nf, sun = L
    H, W = city.shape[:2]
    rng = np.random.default_rng(SEED)

    # the gutter's own pixels, past the corner: binned by their light (dark body, mid, lit, specular)
    gy, gx = np.where(city[:, GUTTER[0]:GUTTER[1] + 1, 3] == 255); gx = gx + GUTTER[0]
    keep = (gy >= 200) & (gy <= 250); gy, gx = gy[keep], gx[keep]
    lum = city[gy, gx, :3] @ [0.299, 0.587, 0.114]
    q = np.quantile(lum, [0.4, 0.75, 0.93])
    BIN = {'dark': lum < q[0], 'mid': (lum >= q[0]) & (lum < q[1]), 'lit': (lum >= q[1]) & (lum < q[2]), 'spec': lum >= q[2]}
    PICK = {k: np.flatnonzero(v) for k, v in BIN.items()}
    under = {x: int(np.where(city[200:260, x, 3] == 255)[0].max()) + 200 for x in range(BOX[0], BOX[1] + 1)}   # (the gutter's underside)

    # the pipe, row by row: (y, x, role); roles across the pipe, from the house side
    px = []
    VERT, DIAG = ('dark', 'dark', 'mid', 'lit', 'rim'), ('lit', 'mid', 'dark', 'dark', 'mid', 'lit', 'rim')
    for x in range(BOX[0], BOX[1] + 1):                                         # the box, hung under the gutter
        top = under[x] + 1
        for k in range(BOX[2]):
            role = 'dark' if k == 0 or x == BOX[0] else 'rim' if x == BOX[1] else 'lit' if k == 1 else 'mid'
            px.append((top + k, x, role))
    ybox = max(under[x] for x in range(BOX[0], BOX[1] + 1)) + BOX[2]
    for y in range(ybox - 1, DROP[1]):                                           # the drop
        for i, x in enumerate(range(DROP[0] - 2, DROP[0] + 3)): px.append((y, x, VERT[i]))
    for y in range(DROP[1], NECK[0] + 1):                                        # the swan neck, one for one
        a = DROP[0] - (y - DROP[1])
        for i, x in enumerate(range(int(round(a)) - 3, int(round(a)) + 4)): px.append((y, x, DIAG[i]))
    for y in range(NECK[0] + 1, int(ROOF(RUN_X + 3)) + 1):                      # down the wall, behind the low roof
        for i, x in enumerate(range(RUN_X - 2, RUN_X + 3)):
            if y < ROOF(x + 0.5): px.append((y, x, VERT[i]))
    collars = (DROP[1], NECK[0] + 1)                                             # (a lit ring at each bend)

    # each pixel a gutter pixel, in short vertical runs; the lit edge's specular dashes
    run = {}
    for y, x, role in sorted(px, key=lambda p: (p[1], p[0])):
        r = run.get((x, role))
        if r is None or r[1] <= 0 or r[2] != y - 1:
            b = 'spec' if role == 'rim' and rng.random() < 0.18 else 'lit' if role == 'rim' else role
            r = [PICK[b][rng.integers(len(PICK[b]))], int(rng.integers(1, 4)), y]
        s = PICK['lit'][rng.integers(len(PICK['lit']))] if y in collars and role != 'dark' else r[0]
        run[(x, role)] = [r[0], r[1] - 1, y]
        for l, b in ((city, B[0]), (unlit, B[1])): l[y, x, :3] = b[gy[s], gx[s], :3]; l[y, x, 3] = 255
        nf[y, x] = 0
        sun[y, x] = B[3][y, 323] if role in ('lit', 'rim') and x >= RUN_X else 0

    # the clamps: a band one pixel wider, an arm back across the gap to the wall
    for c in CLAMPS:
        for y in (c, c + 1):
            for x, b in ((RUN_X - 3, 'dark'), (RUN_X + 3, 'lit' if y == c else 'mid')):
                s = PICK[b][rng.integers(len(PICK[b]))]
                for l, bb in ((city, B[0]), (unlit, B[1])): l[y, x, :3] = bb[gy[s], gx[s], :3]; l[y, x, 3] = 255
                nf[y, x] = 0; sun[y, x] = 0
            for l in (city, unlit): l[y, RUN_X - 4, :3] *= 0.7                     # (its foot on the wall's dark edge)

    # the street's light on the wall beside it: half of it on the pipe's side toward the wall, and on the clamps' arms
    e = np.maximum(0, B[0][:, 322:325, :3] - B[1][:, 322:325, :3]).mean(1)       # (lit minus unlit, the corner's arris)
    for y, x, role in px:
        if x <= RUN_X - 1 and y > NECK[0]: city[y, x, :3] = np.minimum(255, city[y, x, :3] + 0.5 * e[y])
    for c in CLAMPS:
        for y in (c, c + 1): city[y, RUN_X - 3, :3] = np.minimum(255, city[y, RUN_X - 3, :3] + 0.5 * e[y])

    for (n, m), l in zip(names, L): save(l, n, m)
    print('downpipe', len(px), 'px | gutter bins', {k: len(v) for k, v in PICK.items()})


if __name__ == '__main__':
    main()
