#!/usr/bin/env python3
"""The wall at the top left, above the dojo: all boards, and a window as the painter draws them on these walls, its room lit.

    python3 tools/dojo_window.py      (after tools/tree_bc.py; it takes its zone back from commit BEFORE each time, so it
                                       can be run again)

Over the tree in front of the dojo the house's upper wall shows (x 0..111): all of it but the tree's crown (its leaves,
the dark pixels the tree's change put there, joined to the crown's mass below through runs of three dark pixels: a thin
dark line the change also put there is no leaf; and what the leaves enclose). Its old window had become a smear (the
wall's boards, redrawn toward their vanishing point, ran over it).

The wall is now all boards, without a seam: its boards run on the rays to the street's vanishing point VP, each the same
board all along its ray, so each pixel takes the board of its own ray where that ray crosses the wall's clean boards
(CLEAN), or, where it does not, the board a whole number of boards over (the boards' spacing as seen from VP: DTHETA).

Set into it, a window as the painter drew the one on the left house's wall (x 247..273): its head, its sill and its
meeting rail on the rays to VP as his are (so they run with the boards, and with his window's), its stiles plumb; its
outline on the wall a pixel of his transition, his dark frame, his sash's inner line, his curtain's band and his glass,
band by band across and down (BANDS: his rows and columns of each, then this window's; a third larger, being nearer),
each pixel his pixel at the same place in its band, in each layer that same pixel (so his window's light off, his power
cut). Its light, a sprite of its own (assets/win_dojo.webp, a home's window in assets/street.js: on and off a long while,
out in the power cut, red in the red night): over its glass, the panes and the curtain of the owner's reference
(tools/src/dojo_window_ref.png, from ref_house_trad_2), their colours brought to his window's light (each channel's mean
and spread). The tree stays in front of both. In layer_city_off, street_unlit, night_far (0, the street's), street_sun
and its sprite. Needs git, Pillow, numpy.
"""
import io
import json
import os
import subprocess
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = lambda p: os.path.join(ROOT, 'assets', p)
BEFORE = '45c5cb5'                   # (the layers as they were: the boards over the old window)
OLD, TREE = '8d4ca3c^', '8d4ca3c'    # (before the tree was changed; the tree's change)
REF = os.path.join(ROOT, 'tools', 'src', 'dojo_window_ref.png')
REF_GLASS = (245, 40, 457, 220)      # (in the reference: its panes' box, x0, y0, x1, y1, inside its frame)
ZONE = (0, 0, 112, 80)               # x0, y0, x1, y1: the wall over the tree (the sprite's box too)
LEAF = 45                            # (a leaf: darker than this, where the tree's change put a pixel)
VP = (725.0, 625.0)                  # the street's vanishing point (the boards, the windows' heads and sills run to it)
CLEAN, DTHETA = (82, 108, 2, 48), 0.01175   # the wall's clean boards (x0, x1, y0, y1); the boards' spacing seen from VP (rad)
HIS = (247, 260)                     # his window: its left column (its transition), the column his rows below are read on
XL, Y0 = 70, 2                       # this window: its left column (its transition), its top row there (on the ray to VP)
# bands: (name, his first, his last, this window's count); across from his left column, down from his top on his column
COLS = (('edge', 0, 0, 1), ('frame', 1, 3, 4), ('sash', 4, 4, 1), ('curtain', 5, 9, 6), ('glass', 10, 23, 20),
        ('glass_edge', 24, 24, 1), ('frame_r', 25, 25, 2), ('edge_r', 26, 26, 1))
ROWS = (('edge', 260, 260, 1), ('head', 261, 264, 5), ('lit', 265, 265, 1), ('shade', 266, 270, 6), ('glass', 271, 289, 25),
        ('rail', 290, 294, 6), ('rail_lit', 295, 296, 2), ('glass', 297, 344, 62), ('sill', 345, 350, 8), ('edge', 351, 351, 1))
UP = 'win_z7_up'                     # his window's light (its sprite)
LUM = np.array([0.299, 0.587, 0.114])


def load(p, mode='RGBA', at=None):
    data = subprocess.run(['git', 'show', f'{at}:assets/{p}'], cwd=ROOT, capture_output=True, check=True).stdout if at else open(A(p), 'rb').read()
    return np.asarray(Image.open(io.BytesIO(data)).convert(mode)).astype(float)


def save(arr, p, mode):
    Image.fromarray(np.clip(np.round(arr), 0, 255).astype(np.uint8), mode).save(A(p), 'WEBP', lossless=True, quality=100, method=6, exact=True)


def ray(y, x_from, x_to):                                                    # (the row at x_to of the ray to VP through (x_from, y))
    return VP[1] + (y - VP[1]) * (VP[0] - x_to) / (VP[0] - x_from)


def bands(spec):                                                             # (this window's index -> his index, and its band's name)
    out = []
    for name, a, b, n in spec:
        for k in range(n): out.append((a + min(b - a, int((k + 0.5) * (b - a + 1) / n)), name))
    return out


def main():
    names = (('layer_city_off.webp', 'RGBA'), ('street_unlit.webp', 'RGBA'), ('night_far.webp', 'RGB'), ('street_sun.webp', 'RGB'))
    x0, y0, x1, y1 = ZONE
    o, t = load('layer_city_off.webp', 'RGBA', OLD)[y0:y1, x0:x1], load('layer_city_off.webp', 'RGBA', TREE)[y0:y1, x0:x1]
    dark = (np.abs(o - t).sum(2) > 0) & (t[..., :3] @ LUM < LEAF)
    core = dark & np.roll(dark, 1, 1) & np.roll(dark, -1, 1)                 # (three dark in a row: leaves, not a thin line)
    leaf = np.zeros_like(dark); todo = [(y1 - y0 - 1, x) for x in range(x1 - x0) if core[-1, x]]   # (the crown: from the zone's foot up)
    while todo:
        y, x = todo.pop()
        if 0 <= y < y1 - y0 and 0 <= x < x1 - x0 and core[y, x] and not leaf[y, x]:
            leaf[y, x] = True; todo += [(y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)]
    grow = leaf.copy(); grow[1:] |= leaf[:-1]; grow[:-1] |= leaf[1:]; grow[:, 1:] |= leaf[:, :-1]; grow[:, :-1] |= leaf[:, 1:]
    leaf = grow & dark                                                       # (its edge leaves back)
    out = np.zeros_like(leaf); todo = [(0, x) for x in range(x1 - x0)]       # (what is not the crown: reached from the zone's top
    while todo:                                                              # without crossing a leaf; the crown's holes are its own)
        y, x = todo.pop()
        if 0 <= y < y1 - y0 and 0 <= x < x1 - x0 and not leaf[y, x] and not out[y, x]:
            out[y, x] = True; todo += [(y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)]

    B = [load(n, m, BEFORE) for n, m in names]; L_ = [load(n, m) for n, m in names]
    for l, b in zip(L_, B): l[y0:y1, x0:x1] = b[y0:y1, x0:x1]

    # the wall: each pixel the board of its ray where it crosses the clean boards (else a whole number of boards over)
    cx0, cx1, cy0, cy1 = CLEAN
    def board(x, y):
        th = np.arctan2(y - VP[1], x - VP[0])
        for k in sorted(range(-12, 13), key=abs):
            tn = np.tan(th + k * DTHETA)
            for xs in range(cx0, cx1 + 1):
                ys = int(round(VP[1] + tn * (xs - VP[0])))
                if cy0 <= ys <= cy1: return ys, xs
    for x in range(x0, x1):
        for y in range(y0, y1):
            if out[y - y0, x - x0] and not (cx0 <= x <= cx1 and cy0 <= y <= cy1) and x < cx1:   # (the clean boards as they are)
                s = board(x, y)
                for l, b in zip(L_, B): l[y, x] = b[s]

    # the window: his pixels, band by band; its light: the reference's panes over its glass
    cols, rows = bands(COLS), bands(ROWS); W, H = len(cols), len(rows)
    s_ = open(A('street.js'), encoding='utf-8').read(); i0 = s_.index('const ASSETS = ') + len('const ASSETS = ')
    up = json.JSONDecoder().raw_decode(s_[i0:])[0]['comps'][UP]
    upi = np.asarray(Image.open(os.path.join(ROOT, up['src'].split('?')[0])).convert('RGBA')).astype(float)
    lit = upi[upi[..., 3] == 255][:, :3]; m1, s1 = lit.mean(0), lit.std(0)
    ref = np.asarray(Image.open(REF).convert('RGB')).astype(float); rx0, ry0, rx1, ry1 = REF_GLASS
    gi = [i for i, (_, n) in enumerate(cols) if n in ('curtain', 'glass', 'glass_edge')]
    gj = [j for j, (_, n) in enumerate(rows) if n == 'glass']
    cell = {}
    for jj, j in enumerate(gj):
        for ii, i in enumerate(gi):
            blk = ref[ry0 + jj * (ry1 - ry0) // len(gj):ry0 + (jj + 1) * (ry1 - ry0) // len(gj),
                      rx0 + ii * (rx1 - rx0) // len(gi):rx0 + (ii + 1) * (rx1 - rx0) // len(gi)].reshape(-1, 3)
            g = blk[blk @ LUM >= 55]; cell[j, i] = (g if len(g) else blk).mean(0)
    cv = np.array(list(cell.values())); m0, s0 = cv.mean(0), cv.std(0) + 1e-6
    spr = np.zeros((y1 - y0, x1 - x0, 4))
    for x in range(max(x0, XL), min(x1, XL + W)):
        i = x - XL; pi, cn = cols[i]; xp = HIS[0] + pi
        for y in range(y0, y1):
            if not out[y - y0, x - x0]: continue
            j = int(np.floor(ray(y, x, XL) - Y0))                            # (its row in the window, on its ray)
            if not 0 <= j < H: continue
            py_his, rn = rows[j]
            yp = int(round(ray(ray(py_his, HIS[1], HIS[0]), HIS[0], xp)))    # (his pixel: his row on his column, along his ray)
            for l, b in zip(L_, B): l[y, x] = b[yp, xp]
            L_[2][y, x] = 0
            if (j, i) in cell: spr[y - y0, x - x0] = [*np.clip(m1 + (cell[j, i] - m0) / s0 * s1, 0, 255), 255]
    for (n, m), l in zip(names, L_): save(l, n, m)
    save(spr, 'win_dojo.webp', 'RGBA')
    print('wall: boards to x', x1 - 1, '| window', W, 'x', H, 'at', (XL, Y0), '| its light', int((spr[..., 3] > 0).sum()), 'px | crown', int((~out).sum()), 'px')


if __name__ == '__main__':
    main()
