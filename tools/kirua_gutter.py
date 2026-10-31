#!/usr/bin/env python3
"""The eave under Kirua (the left house's roof edge, right end): its gutter's downpipe.

    python3 tools/kirua_gutter.py      (after tools/tree_a.py and tools/tree_bc.py; it takes its zone back from
                                        commit BEFORE each time, so it can be run again)

The eave runs on past the house's corner (x 325) into the sky, its gutter closed by the painter's own end cap at x 357.
Kirua sits on that eave, his feet swinging over it: his two legs, in every frame, cover x 326..353 down to y 226, so a
downpipe from anywhere along it would stand under a boot and read as a third shin. The gutter drains near its very end,
just inboard of its cap and past where his boots reach at rest: a short outlet with a lit collar, a drop, a swan neck
back toward the house along the street's line (45 degrees here, a clean one-for-one stair, lit from the sky above on its
upper side), and the pipe down the house's end wall against its corner (the corner's lit arris kept), held by three
clamps; at the low roof in front of it a shoe kicks it toward the street and pours on that roof (a wet mark there). Its
metal is the gutter's own: each pixel takes the colour of a pixel of the gutter, in each layer the same pixel and its
mark in street_sun too (so the power cut, the red night and the hours read it as they read the gutter: a sunset rim
stays a sunset rim and fades with the evening like the gutter's own), chosen by where it lies across the pipe (the side
toward the house dark, toward the open sky lit, the gutter's rim on that edge), in steady runs, with a few of the
gutter's specular dashes; a collar at each bend. Where the street's lights reach the wall beside it (the red night's
patch, x 299..324, y 340..422), its side toward the wall takes most of that light. In layer_city_off, street_unlit,
night_far (0, the street's) and street_sun. Needs git, Pillow, numpy.
"""
import io
import os
import subprocess
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = lambda p: os.path.join(ROOT, 'assets', p)
BEFORE = '6c8530a'                   # (the layers as they were, the eave untouched)
ZONE = (296, 196, 372, 492)          # x0, y0, x1, y1: taken back from BEFORE before anything is drawn
GUTTER = (330, 356)                  # the gutter's columns past the corner, where its colours are taken
BOX = (348, 355, 6)                  # the collecting box (shuusuiki): its columns, its rows under the gutter's underside
DROP = (352, 252)                    # the drop's foot, where the swan neck starts (its axis)
RUN_X = 328                          # the pipe's axis down the wall (its columns 326..330, against the corner; its arris x 322..325)
NECK = (275, 329)                    # where the swan neck meets it: its last row, its axis there
FOOT = 455                           # the run's last row, at the low roof's corner; then a shoe turns in over that roof and pours on it
CLAMPS = (318, 393)                  # the clamps (first of their two rows), about a metre apart
EDGE = lambda x: 452 + 1.46 * (x - 326)   # the low roof's far edge right of the corner (the cherry behind it, above)
PLATE = ((300, 446), (306, 448), (312, 450))   # the low roof's lit top edge: where the splash plate's colours are taken
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

    # the pipe, row by row: (y, x, role, lane); roles across the pipe from the house side; a lane is what keeps its tone
    # (a column of the upright parts, a strip along the swan neck)
    px = []
    VERT, DIAG = ('dark', 'dark', 'mid', 'lit', 'rim'), ('rim', 'lit', 'mid', 'dark', 'dark', 'dark', 'mid')   # (lit from the sky above)
    ybox = {}
    for x in range(BOX[0], BOX[1] + 1):                                         # the box under the gutter: its lit lip, its face, its
        for k in range(BOX[2]):                                                  # dark sides and underside, wider than the pipe
            role = 'rim' if k == 0 else 'dark' if k == BOX[2] - 1 or x in (BOX[0], BOX[1]) else 'lit' if k == 1 else 'mid'
            px.append((under[x] + 1 + k, x, role, ('b', x, k)))
        ybox[x] = under[x] + BOX[2]
    for i, x in enumerate(range(DROP[0] - 2, DROP[0] + 3)):                     # the drop, from the box's underside
        for y in range(ybox[x] + 1, DROP[1]): px.append((y, x, VERT[i], ('v', x)))
    for y in range(DROP[1], NECK[0] + 1):                                        # the swan neck, one for one
        a = DROP[0] - (y - DROP[1])
        for i, x in enumerate(range(a - 3, a + 4)): px.append((y, x, DIAG[i], ('d', i)))
    for y in range(NECK[0] + 1, FOOT + 1):                                       # down the wall: its rim only against the sky
        for i, x in enumerate(range(RUN_X - 2, RUN_X + 3)):
            role = VERT[i] if VERT[i] != 'rim' else ('sun' if B[0][y, RUN_X + 3, 3] == 0 else 'mid')
            px.append((y, x, role, ('v', x)))
    for y in range(FOOT + 1, FOOT + 4):                                          # the shoe, turned in over the low roof
        a = RUN_X - (y - FOOT)
        for i, x in enumerate(range(a - 2, a + 3)): px.append((y, x, 'mid' if VERT[i] == 'rim' else VERT[i], ('s', i)))
    collars = (DROP[1], NECK[0] + 1, FOOT + 1)                                    # (a lit ring at each bend)

    # each pixel a gutter pixel, its lane in steady runs; a rare specular dash on the rim where it is against the sky
    run = {}
    for y, x, role, lane in sorted(px, key=lambda p: p[0]):
        r = run.get(lane)
        if r is None or r[1] <= 0 or r[2] != y - 1 or r[3] != role:
            if role == 'sun':                                                    # (the sunset's rim against the sky, warmer up high)
                b = 'spec' if rng.random() < 0.85 - 0.6 * (y - NECK[0]) / (FOOT - NECK[0]) else 'lit'
            else: b = ('spec' if rng.random() < 0.1 else 'lit') if role == 'rim' else role
            r = [PICK[b][rng.integers(len(PICK[b]))], int(rng.integers(8, 21) if role == 'rim' else rng.integers(3, 9)), y, role]
        s = PICK['lit'][rng.integers(len(PICK['lit']))] if y in collars and role != 'dark' else r[0]
        run[lane] = [r[0], r[1] - 1, y, role]
        for l, b in ((city, B[0]), (unlit, B[1])): l[y, x, :3] = b[gy[s], gx[s], :3]; l[y, x, 3] = 255
        nf[y, x] = 0
        sun[y, x] = B[3][gy[s], gx[s]]                                          # (its source's: a sunset rim stays a sunset rim at every hour)

    # the clamps: a ring across the pipe a pixel wider each side (lit over dark), its arm into the wall's corner
    for c in CLAMPS:
        for y, b in ((c, 'lit'), (c + 1, 'dark')):
            for x in list(range(RUN_X - 3, RUN_X + 4)) + ([RUN_X - 4, RUN_X - 5] if b == 'dark' else []):
                s = PICK[b][rng.integers(len(PICK[b]))]
                for l, bb in ((city, B[0]), (unlit, B[1])): l[y, x, :3] = bb[gy[s], gx[s], :3]; l[y, x, 3] = 255
                nf[y, x] = 0; sun[y, x] = B[3][gy[s], gx[s]]

    # the warm light on the wall beside it (the sunset's, marked in street_sun: gone at night, red in the red night, unlit
    # in the cut) on the pipe's side toward the wall, marked as the wall is
    e = np.maximum(0, B[0][:, 318:325, :3] - B[1][:, 318:325, :3]).mean(1)       # (its share: lit minus unlit beside the corner)
    lit = B[3][:, 321:325, 0].max(1) > 0
    for y, x, role, lane in px:
        if x <= RUN_X - 1 and NECK[0] < y <= FOOT and lit[y]:
            city[y, x, :3] = np.minimum(255, city[y, x, :3] + (1.0 if x == RUN_X - 2 else 0.6) * e[y]); sun[y, x] = 255

    # under the shoe's mouth, on the low roof: a small splash plate (the roof's lit edge's colours), and a wet streak
    # running down the roof's corrugations from it
    mx, my = RUN_X - 3, FOOT + 3                                                 # (its mouth, over the roof inside its far edge)
    for k, x in enumerate(range(mx - 2, mx + 2)):
        for dy in (0, 1):
            y = my + 2 + dy
            sx, sy = PLATE[k % len(PLATE)]
            for l, b in ((city, B[0]), (unlit, B[1])): l[y, x, :3] = b[sy, sx, :3] * (1.0 if dy == 0 else 0.7)
            sun[y, x] = B[3][sy, sx]
    for k in range(1, 9):                                                        # (down the corrugations)
        x, y = mx + 1 + k // 2, my + 4 + k
        if (x >= 326 and y <= EDGE(x)) or y >= H: break                          # (stays on the roof)
        for l in (city, unlit): l[y, x, :3] *= 0.72

    for (n, m), l in zip(names, L): save(l, n, m)
    print('downpipe', len(px), 'px | gutter bins', {k: len(v) for k, v in PICK.items()})


if __name__ == '__main__':
    main()
