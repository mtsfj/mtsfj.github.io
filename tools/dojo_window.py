#!/usr/bin/env python3
"""The wall at the top left, above the dojo: all boards, and a window of the owner's reference set into it, its room lit.

    python3 tools/dojo_window.py      (after tools/tree_bc.py; it takes its zone back from commit BEFORE each time, so it
                                       can be run again)

Over the tree in front of the dojo the house's upper wall shows (x 0..65): all of it but the tree's crown (its leaves,
the dark pixels the tree's change put there, joined to the crown's mass below through runs of three dark pixels: a thin
dark line the change also put there is no leaf; and what the leaves enclose). Its old window had become a smear (the
wall's boards, redrawn toward their vanishing point, ran over it). The wall is now all boards: the painter's (as
redrawn), moved along the wall by BOARD columns, a whole number of boards, up to WALL (past it they are as they were). Set into it, the window of the owner's
reference (tools/src/dojo_window_ref.png: the right half of ref_house_trad_2's upper window, its two panes across, its
curtain), as the house's other windows are drawn on this wall: narrow, upright, its every column carried down the
wall's slope by whole pixels (SLOPE), so its head, its transoms and its sill run as the boards do while its stiles and
its mullion stay plumb. Its frame is drawn true (an even outline of FRAME pixels, its mullion and its transoms one
pixel), in the tones of the frame of the window the painter drew on the left house (its body, its lit edges); its
panes are the reference's glass, one cell a scene pixel (the mean of its glass there).
As every window of the street it is two things. In the layers, the window with its room's light off: its panes that
same painted window's glass under its light (win_z7_up), each cell the painter's pixel of the same rank of lightness, in
each layer that same pixel. And its light, a sprite of its own (assets/win_dojo.webp, a home's window in
assets/street.js: on and off a long while, out in the power cut, red in the red night): the reference's own panes and
curtain, their colours brought to that window's light (each channel's mean and spread). The tree stays in front of
both. In layer_city_off, street_unlit, night_far (0, the street's), street_sun and its sprite. Needs git, Pillow, numpy.
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
ZONE = (0, 0, 66, 60)                # x0, y0, x1, y1: the wall over the tree (the sprite's box too)
LEAF = 45                            # (a leaf: darker than this, where the tree's change put a pixel)
BOARD, WALL = (62, 46), 62          # (the boards come from BOARD columns along, whole numbers of boards: the first while it
CLEAN = 108                          # stays on the clean boards, to column CLEAN, else the second; to column WALL, where the
                                     # redrawn boards begin clean)
AT, SIZE, SLOPE = (10, 3), (30, 50), 0.9   # the window: its top left corner, its width and height (px), the wall's slope
FRAME = 2                            # its outline's width (px); its mullion and its transoms one pixel
MULL_U, BARS_V = 0.5, (0.33, 0.66)   # its mullion across (share of its width), its transoms down (share of its height)
PAINTED = (246, 252, 284, 352)       # the window the painter drew on the left house (its frame's tones)
UP = 'win_z7_up'                     # that window's light (its sprite): its glass off under it, its light
LUM = np.array([0.299, 0.587, 0.114])


def load(p, mode='RGBA', at=None):
    data = subprocess.run(['git', 'show', f'{at}:assets/{p}'], cwd=ROOT, capture_output=True, check=True).stdout if at else open(A(p), 'rb').read()
    return np.asarray(Image.open(io.BytesIO(data)).convert(mode)).astype(float)


def save(arr, p, mode):
    Image.fromarray(np.clip(np.round(arr), 0, 255).astype(np.uint8), mode).save(A(p), 'WEBP', lossless=True, quality=100, method=6, exact=True)


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
    for x in range(x0, WALL + 1):                                            # the wall: all boards (the crown in front)
        for y in range(y0, y1):
            if out[y - y0, x - x0]:
                d = BOARD[0] if x + BOARD[0] <= CLEAN else BOARD[1]
                for l, b in zip(L_, B): l[y, x] = b[y, x + d]

    # the painted window's tones: its frame (dark: its body; its lightest dark: the edges the sky lights), its glass off and lit
    px0, py0, px1, py1 = PAINTED; fr = B[0][py0:py1, px0:px1, :3].reshape(-1, 3); fl = fr @ LUM; fr = fr[fl < 32]; fl = fl[fl < 32]
    BODY, EDGE = fr[np.argsort(fl)[len(fl) // 3]], fr[np.argsort(fl)[int(len(fl) * 0.95)]]
    s = open(A('street.js'), encoding='utf-8').read(); i0 = s.index('const ASSETS = ') + len('const ASSETS = ')
    up = json.JSONDecoder().raw_decode(s[i0:])[0]['comps'][UP]
    upi = np.asarray(Image.open(os.path.join(ROOT, up['src'].split('?')[0])).convert('RGBA')).astype(float)
    uy, ux = np.where(upi[..., 3] == 255); lit = upi[uy, ux, :3]; uy, ux = uy + up['y'], ux + up['x']
    order = np.argsort(B[0][uy, ux, :3] @ LUM); gy, gx = uy[order], ux[order]

    # the reference's panes, one cell a scene pixel of the window's inside
    W, H = SIZE; ref = np.asarray(Image.open(REF).convert('RGB')).astype(float)
    rx0, ry0, rx1, ry1 = REF_GLASS; iw, ih = W - 2 * FRAME, H - 2 * FRAME
    col = np.zeros((ih, iw, 3))
    for j in range(ih):
        for i in range(iw):
            blk = ref[ry0 + j * (ry1 - ry0) // ih:ry0 + (j + 1) * (ry1 - ry0) // ih, rx0 + i * (rx1 - rx0) // iw:rx0 + (i + 1) * (rx1 - rx0) // iw].reshape(-1, 3)
            g = blk[blk @ LUM >= 55]; col[j, i] = (g if len(g) else blk).mean(0)
    light = col @ LUM; m0, s0 = col.reshape(-1, 3).mean(0), col.reshape(-1, 3).std(0) + 1e-6; m1, s1 = lit.mean(0), lit.std(0)
    mull = FRAME + round(MULL_U * iw) - 1; bars = [FRAME + round(v * ih) for v in BARS_V]

    spr = np.zeros((y1 - y0, x1 - x0, 4))
    for i in range(W):
        for j in range(H):
            x, y = AT[0] + i, AT[1] + j + round(SLOPE * i)                     # (each column down the wall's slope by whole pixels)
            if not (x0 <= x < x1 and y0 <= y < y1) or not out[y - y0, x - x0]: continue
            edge = i < FRAME or i >= W - FRAME or j < FRAME or j >= H - FRAME
            bar = i == mull or j in bars
            if edge or bar:                                                  # (its frame: its top faces and its left lit by the sky)
                c = EDGE if (j == 0 or (j in bars and not edge) or (i == 0 and j < H - FRAME)) else BODY
                for l in L_[:2]: l[y, x, :3] = c; l[y, x, 3] = 255
            else:
                ci, cj = i - FRAME, j - FRAME
                k = min(len(gy) - 1, int((light < light[cj, ci]).mean() * len(gy)))   # (off: the painter's glass of its rank)
                for l, b in zip(L_[:2], B[:2]): l[y, x] = b[gy[k], gx[k]]
                spr[y - y0, x - x0] = [*np.clip(m1 + (col[cj, ci] - m0) / s0 * s1, 0, 255), 255]
            L_[2][y, x] = 0; L_[3][y, x] = 0
    for (n, m), l in zip(names, L_): save(l, n, m)
    save(spr, 'win_dojo.webp', 'RGBA')
    print('window: at', AT, 'size', SIZE, 'slope', SLOPE, '| its light', int((spr[..., 3] > 0).sum()), 'px | crown', int((~out).sum()), 'px')


if __name__ == '__main__':
    main()
