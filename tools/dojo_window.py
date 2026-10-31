#!/usr/bin/env python3
"""The window at the top left, above the dojo: the window of the owner's reference, set into the wall, its room lit.

    python3 tools/dojo_window.py      (after tools/tree_bc.py; it takes its zone back from commit BEFORE each time, so it
                                       can be run again)

Over the tree in front of the dojo the house's upper wall shows (x 0..65): all of it but the tree's crown (its leaves,
the dark pixels the tree's change put there, joined to the crown's mass below through runs of three dark pixels: a thin
dark line the change also put there is no leaf; and what the leaves enclose). Its window had become a smear (the wall's
boards, redrawn toward their vanishing point, ran over its frame and its glass). It is now the window of the owner's
reference (tools/src/dojo_window_ref.png, from ref_house_trad_2: its frame, its mullions, its panes, the curtain at its
right) set into that wall: its columns spread between the wall's columns XL and XR, its rows along the wall's rays to
the street's vanishing point VP (its head through (XL, HEAD), as the boards run), each scene pixel one cell of it (a cell
mostly of its frame's dark is frame, else glass: the mean of its glass); its sill a rail of its frame (SILL rows).
As every window of the street it is two things. In the layers, the window with its room's light off: its frame the old
window's casing, its glass the glass of the street's upstairs window on the same side (win_z7_up's, under its light),
each cell the painter's pixel of the same rank of lightness (in each layer that same pixel). And its light, a sprite of
its own (assets/win_dojo.webp, a home's window in assets/street.js: on and off a long while, out in the power cut, red
in the red night): the reference's own panes and curtain, their colours brought to the light of that upstairs window
(each channel's mean and spread), the tree's crown left out of it (the tree is in front). Over its head the wall's
boards (and under its sill), the painter's (as redrawn) moved along the wall by BOARD columns, a whole number of
boards; right of it the boards as they are. In layer_city_off, street_unlit, night_far (0, the street's), street_sun and its sprite. Needs git,
Pillow, numpy.
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
OLD, TREE = '8d4ca3c^', '8d4ca3c'    # (the painter's old window, before the tree was changed; the tree's change)
REF = os.path.join(ROOT, 'tools', 'src', 'dojo_window_ref.png')
ZONE = (0, 0, 66, 60)                # x0, y0, x1, y1: the wall over the tree (the sprite's box too)
LEAF = 45                            # (a leaf: darker than this, where the tree's change put a pixel)
VP = (725.0, 625.0)                  # the street's vanishing point (the wall's boards run to it)
XL, XR, HEAD, TALL = 0, 55, -26, 50  # the window: its left and right columns, its head's row at XL, its height (rows at XR)
DARK = 60                            # (a cell of the reference: frame where darker than this)
SILL = 2                             # its sill's rows (the reference stops over its balcony's rail: its rail drawn here)
BOARD = 62                           # (a whole number of boards along the wall: where the boards over its head come from)
CASING = (40, 0, 47, 36)             # the old window's casing (x0, y0, x1, y1): the frame's colours
UP = 'win_z7_up'                     # the street's upstairs window on this side: its glass off (under it) and its light
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

    # the reference, one cell a scene pixel: frame (mostly dark) or glass (the mean of its glass, and its lightness)
    ref = np.asarray(Image.open(REF).convert('RGB')).astype(float); rh, rw = ref.shape[:2]; W = XR - XL + 1
    cell = np.zeros((TALL, W), int); light = np.zeros((TALL, W)); col = np.zeros((TALL, W, 3))
    for j in range(TALL):
        for i in range(W):
            blk = ref[j * rh // TALL:(j + 1) * rh // TALL, i * rw // W:(i + 1) * rw // W].reshape(-1, 3); L = blk @ LUM
            fr = (L < DARK).mean() >= 0.4; cell[j, i] = fr; part = blk[L < DARK] if fr else blk[L >= DARK]
            col[j, i] = part.mean(0); light[j, i] = col[j, i] @ LUM
    for j in range(TALL - SILL, TALL):                                       # (its sill: the frame's rail closes it under its panes)
        cell[j] = 1; light[j] = np.minimum(light[j], np.median(light[cell == 1]))

    # the painter's colours: the casing's pixels (the frame), the upstairs window's glass under its light (the glass off)
    OL = [load(n, m, OLD) for n, m in names]; B = [load(n, m, BEFORE) for n, m in names]
    s = open(A('street.js'), encoding='utf-8').read(); i0 = s.index('const ASSETS = ') + len('const ASSETS = ')
    up = json.JSONDecoder().raw_decode(s[i0:])[0]['comps'][UP]
    upi = np.asarray(Image.open(os.path.join(ROOT, up['src'].split('?')[0])).convert('RGBA')).astype(float)
    uy, ux = np.where(upi[..., 3] == 255); lit = upi[uy, ux, :3]; uy, ux = uy + up['y'], ux + up['x']

    def ranked(ys, xs, layers):
        order = np.argsort(layers[0][ys, xs, :3] @ LUM); return ys[order], xs[order], layers
    cy, cx = np.mgrid[CASING[1]:CASING[3], CASING[0]:CASING[2]]; cy, cx = cy.ravel(), cx.ravel(); k = OL[0][cy, cx, :3] @ LUM <= 45
    FRAME, GLASS = ranked(cy[k], cx[k], OL), ranked(uy, ux, B)

    def pick(j, i):                                                         # (the painter's pixel of its rank among its kind)
        q = (light[cell == cell[j, i]] < light[j, i]).mean()
        ys, xs, src = FRAME if cell[j, i] else GLASS
        k = min(len(ys) - 1, int(q * len(ys))); return [s_[ys[k], xs[k]] for s_ in src]
    g = cell == 0; m0, s0 = col[g].mean(0), col[g].std(0) + 1e-6; m1, s1 = lit.mean(0), lit.std(0)   # (its light: to the upstairs one's)

    hh = VP[1] + (HEAD - VP[1]) * (VP[0] - XR) / (VP[0] - XL)               # (its head's row at XR, on the ray through (XL, HEAD))
    L_ = [load(n, m) for n, m in names]
    for l, b in zip(L_, B): l[y0:y1, x0:x1] = b[y0:y1, x0:x1]
    spr = np.zeros((y1 - y0, x1 - x0, 4))
    for x in range(x0, x1):
        for y in range(y0, y1):
            if not out[y - y0, x - x0]: continue                             # (the crown stays in front)
            h = VP[1] + (y - VP[1]) * (VP[0] - XR) / (VP[0] - x)            # (its row at XR on its ray)
            v, u = (h - hh) / TALL, (x - XL) / (XR - XL + 1)
            if 0 <= v < 1 and 0 <= u < 1:
                j, i = int(v * TALL), int(u * W)
                for l, c in zip(L_, pick(j, i)): l[y, x] = c
                L_[2][y, x] = 0
                if not cell[j, i]: spr[y - y0, x - x0] = [*np.clip(m1 + (col[j, i] - m0) / s0 * s1, 0, 255), 255]
            elif x <= XR:                                                    # (over its head, under its sill: the boards, a whole number of them along)
                for l, b in zip(L_, B): l[y, x] = b[y, x + BOARD]
    for (n, m), l in zip(names, L_): save(l, n, m)
    save(spr, 'win_dojo.webp', 'RGBA')
    print('window: the reference', (rw, rh), '->', (W, TALL), 'cells | its light', int((spr[..., 3] > 0).sum()), 'px | crown', int((~out).sum()), 'px')


if __name__ == '__main__':
    main()
