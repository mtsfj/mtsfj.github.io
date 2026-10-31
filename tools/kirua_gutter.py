#!/usr/bin/env python3
"""The eave under Kirua (the left house's roof edge, right end): shortened, and its gutter's downpipe.

    python3 tools/kirua_gutter.py      (after tools/tree_a.py and tools/tree_bc.py; it takes its zone back from
                                        commit BEFORE each time, so it can be run again)

The eave ran on past the house's corner (x 325) into the sky as far as x 357. It now stops a short overhang past the
corner (EAVE_END), closed by the painter's own end (its last columns, the gutter's cap: END, carried back along the eave's
line, each column on the eave's rows there); what it covered is sky again (transparent; 0 in night_far and street_sun,
as round it). The gutter drains at that end, straight down: a collecting box under its last stretch, wider than the
pipe, and the pipe down the house's end wall against its corner (the corner's lit arris kept), held by two clamps about
a metre apart; at the low roof in front of it a shoe kicks it toward the street and pours on that roof (a splash plate
and a wet mark down its corrugations). Kirua sits on that corner, his boots over the end, in front of the pipe's top.
Its metal is the gutter's own: each pixel takes the colour of a pixel of the gutter, in each layer the same pixel and
its mark in street_sun too (so the power cut, the red night and the hours read it as they read the gutter: a sunset rim
stays a sunset rim and fades with the evening like the gutter's own), chosen by where it lies across the pipe (the side
toward the house dark, toward the open sky lit, the gutter's sunset rim on that edge), each band of it one colour all
down (the gutter's pixel nearest its band's mean: no mottle); a collar at each joint, the clamps dark rings. Where the street's lights reach the wall beside it (the red night's
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
GUTTER = (330, 356)                  # the gutter's columns past the corner (as painted), where its colours are taken
EAVE_END = 346                       # the eave's last column now (it ran on to x 357): a short overhang past the corner
END = (352, 357)                     # the painter's own end of the eave (its last columns, the gutter's cap), moved back to it
BOX = (325, 331, 5)                  # the collecting box (shuusuiki): its columns (a pixel wider than the pipe each side), its rows under the gutter
RUN_X = 328                          # the pipe's axis down the wall (its columns 326..330, against the corner; its arris x 322..325)
FOOT = 455                           # the run's last row, at the low roof's corner; then a shoe turns in over that roof and pours on it
CLAMPS = (318, 393)                  # the clamps (first of their two rows), about a metre apart
EDGE = lambda x: 452 + 1.46 * (x - 326)   # the low roof's far edge right of the corner (the cherry behind it, above)
PLATE = ((300, 446), (306, 448), (312, 450))   # the low roof's lit top edge: where the splash plate's colours are taken


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

    # the gutter's own pixels, past the corner (as painted): binned by their light (dark body, mid, lit, specular)
    gy, gx = np.where(B[0][:, GUTTER[0]:GUTTER[1] + 1, 3] == 255); gx = gx + GUTTER[0]
    keep = (gy >= 200) & (gy <= 250); gy, gx = gy[keep], gx[keep]
    lum = B[0][gy, gx, :3] @ [0.299, 0.587, 0.114]
    q = np.quantile(lum, [0.4, 0.75, 0.93])
    BIN = {'dark': lum < q[0], 'mid': (lum >= q[0]) & (lum < q[1]), 'lit': (lum >= q[1]) & (lum < q[2]), 'spec': lum >= q[2]}
    REP = {}                                                                     # (each band's one colour: the pixel nearest its mean)
    for k, v in BIN.items():
        i = np.flatnonzero(v); c = B[0][gy[i], gx[i], :3]; REP[k] = int(i[np.argmin(((c - c.mean(0)) ** 2).sum(1))])

    # the eave, shortened: past EAVE_END sky again; its last columns the painter's end, each moved back along the eave's line
    # (its rows there: the eave's top edge falls a pixel a column, its band 13 rows deep)
    top = {x: int(np.where(B[0][190:260, x, 3] > 0)[0].min()) + 190 for x in range(326, END[1] + 1)}
    for l in L: l[top[EAVE_END] - 4:top[END[1]] + 16, EAVE_END + 1:END[1] + 2] = 0
    for x in range(EAVE_END - (END[1] - END[0]), EAVE_END + 1):
        xs, d = x + END[1] - EAVE_END, top[x + END[1] - EAVE_END] - top[x]
        for l, b in zip(L, B): l[top[x] - 3:top[x] + 16, x] = b[top[x] - 3 + d:top[x] + 16 + d, xs]
    under = {x: (top[x] + 12 if x >= 326 else round(top[326] + 12 - 1.03 * (326 - x))) for x in range(BOX[0], BOX[1] + 1)}   # (its underside)

    # the pipe, row by row: (y, x, role, lane); roles across the pipe from the house side; a lane is what keeps its tone
    # (a column of the pipe, a row of the box)
    px = []
    VERT = ('dark', 'dark', 'mid', 'lit', 'rim')
    ybox = {}
    for x in range(BOX[0], BOX[1] + 1):                                         # the box under the gutter: its lit lip, its face, its
        for k in range(BOX[2]):                                                  # dark sides and underside, wider than the pipe
            role = 'rim' if k == 0 else 'dark' if k == BOX[2] - 1 or x in (BOX[0], BOX[1]) else 'lit' if k == 1 else 'mid'
            px.append((under[x] + 1 + k, x, role, ('b', x, k)))
        ybox[x] = under[x] + BOX[2]
    y0p = ybox[RUN_X] + 1                                                        # (the pipe's first row, under the box's middle)
    for i, x in enumerate(range(RUN_X - 2, RUN_X + 3)):                          # down the wall from the box: its rim only against the sky
        for y in range(ybox[x] + 1, FOOT + 1):
            role = VERT[i] if VERT[i] != 'rim' else ('sun' if B[0][y, RUN_X + 3, 3] == 0 else 'mid')
            px.append((y, x, role, ('v', x)))
    for y in range(FOOT + 1, FOOT + 4):                                          # the shoe, turned in over the low roof
        a = RUN_X - (y - FOOT)
        for i, x in enumerate(range(a - 2, a + 3)): px.append((y, x, 'mid' if VERT[i] == 'rim' else VERT[i], ('s', i)))
    collars = (y0p + 1, FOOT + 1)                                                # (a lit ring at each joint)

    # each pixel its band's one gutter pixel (the rim against the sky the gutter's sunset rim, its specular band)
    BAND = {'dark': 'dark', 'mid': 'mid', 'lit': 'lit', 'rim': 'lit', 'sun': 'spec'}
    for y, x, role, lane in px:
        s = REP['lit'] if y in collars and role != 'dark' else REP[BAND[role]]
        for l, b in ((city, B[0]), (unlit, B[1])): l[y, x, :3] = b[gy[s], gx[s], :3]; l[y, x, 3] = 255
        nf[y, x] = 0
        sun[y, x] = B[3][gy[s], gx[s]]                                          # (its source's: a sunset rim stays a sunset rim at every hour)

    # the clamps: a dark ring across the pipe a pixel wider each side (its top a shade lighter), its arm into the wall's corner
    for c in CLAMPS:
        for y, b in ((c, 'mid'), (c + 1, 'dark')):
            for x in list(range(RUN_X - 3, RUN_X + 4)) + ([RUN_X - 4, RUN_X - 5] if b == 'dark' else []):
                s = REP[b]
                for l, bb in ((city, B[0]), (unlit, B[1])): l[y, x, :3] = bb[gy[s], gx[s], :3]; l[y, x, 3] = 255
                nf[y, x] = 0; sun[y, x] = B[3][gy[s], gx[s]]

    # the warm light on the wall beside it (the sunset's, marked in street_sun: gone at night, red in the red night, unlit
    # in the cut) on the pipe's side toward the wall, marked as the wall is
    e = np.maximum(0, B[0][:, 318:325, :3] - B[1][:, 318:325, :3]).mean(1)       # (its share: lit minus unlit beside the corner)
    lit = B[3][:, 321:325, 0].max(1) > 0
    for y, x, role, lane in px:
        if x <= RUN_X - 1 and y0p < y <= FOOT and lit[y]:
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
    print('downpipe', len(px), 'px | gutter bins', {k: int(v.sum()) for k, v in BIN.items()})


if __name__ == '__main__':
    main()
