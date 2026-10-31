#!/usr/bin/env python3
"""The wall at the top left, above the dojo: all boards, and behind the tree a big window of the owner's reference, its room lit.

    python3 tools/dojo_window.py      (after tools/tree_bc.py; it takes its zone back from commit BEFORE each time, so it
                                       can be run again)

Over the tree in front of the dojo the house's upper wall shows (x 0..131, its corner post past it). The old window up
there had become a smear (the wall's boards, redrawn toward their vanishing point, ran over it): that part of the wall
(REFILL) is all boards now, without a seam: its boards run on the rays to the street's vanishing point VP, each the same
board all along its ray, so each pixel takes the board of its own ray where that ray crosses the wall's clean boards
(CLEAN), or, where it does not, the board a whole number of boards over (the boards' spacing as seen from VP: DTHETA);
along it a different pixel of that board for each column, back and forth, so that its grain stays.

Lower on that wall, behind the tree, a big window: the owner's reference (tools/src/dojo_window_ref.png, ref_house_trad_7:
its frame, its two panes and their curtains, its balcony rail), set into the wall in perspective: its head and its sill
on the rays to VP (as the boards and the other houses' windows), its stiles plumb, its columns closer together toward VP
(as a wall going away has them). Its picture is the reference's own colours (a palette of its own pixels, no dither), its
outline a pixel of its frame's dark all round. Off, as it is in the layers, its glass is the painter's glass on the left
house (x 247..273: his window's dark glass, his frame's navy), the curtains' folds still in it; its light is a sprite of
its own (assets/win_dojo.webp, a home's window in assets/street.js: on and off a long while, out in the power cut, red in
the red night): its panes and curtains as the reference has them, brought to the street's lit home window (each
channel's mean and spread, as win_z7_up). The tree stays in front of all of it: its leaves (the dark pixels the tree's
change put there, joined to the crown's mass through runs of three dark pixels, and the dark ones close to them); where
the leaves part, the window shows. In layer_city_off, street_unlit, night_far (0, the street's), street_sun (the frame
takes the wall's sunset, the glass none) and its sprite. Needs git, Pillow, numpy.
"""
import io
import os
import re
import subprocess
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = lambda p: os.path.join(ROOT, 'assets', p)
BEFORE = '45c5cb5'                   # (the layers as they were: the boards over the old window)
OLD, TREE = '8d4ca3c^', '8d4ca3c'    # (before the tree was changed; the tree's change)
REF = os.path.join(ROOT, 'tools', 'src', 'dojo_window_ref.png')
ZONE = (0, 0, 140, 200)              # x0, y0, x1, y1: taken back from BEFORE; where the crown is found
WALL_X1 = 131                        # the wall's last column (its corner post past it)
REFILL = (0, 0, 82, 80)              # the old window's part of the wall and its smudged edge, all boards again
LEAF = 45                            # (a leaf: darker than this, where the tree's change put a pixel)
VP = (700.0, 615.0)                  # the painter's vanishing point for the houses on the left (his boards, his small window's
                                     # head and sill, the far house's ledges all run to it): the boards, the window's head and sill
CLEAN, DTHETA = (82, 108, 2, 66), 0.0123    # the wall's clean boards (x0, x1, y0, y1); the boards' spacing seen from VP (rad)
XL, XR, Y0, H = 8, 122, 0, 100       # the whole window: its first and last columns, its top's row at XL, its height there
UNIT = ((10, 0, 522, 12), (0, 12, 531, 99), (70, 97, 471, 371), (42, 242, 496, 426))   # in the reference (x0, y0, x1, y1): its
                                     # hood's ridge, its hood (tiles, eaves, the shadow under them), its frame and panes, its balcony
GLASS = (82, 110, 460, 362)          # its panes (the light's), in the reference
HOOD_FOOT, HOOD_V, HOOD_END = 99, 0.12, 3   # the hood's foot (reference row); its share of the height here (thinner than
                                     # the reference's); its end, square to us, this many columns out from its first
SHADE = (0.5, 0.22, 3)               # its shadow on the wall: darkest under it, gone
                                     # this far down (of its height), and over this many columns at its ends
GLOW_MIN = 4                         # (its light where the leaves part over this many pixels together, at least)
HIS_GLASS, HIS_FRAME = (257, 271, 280, 336), (248, 251, 280, 336)   # the painter's window (x0, x1, y0, y1): its glass, its frame
UP = 'win_z7_up'                     # the street's lit home window (its sprite)
HIS_AT = '119e468'                   # (the painter's small window and its light read as they were there: since then
                                     # tools/kirua_bay_window.py has put a bay window in their place)
LUM = np.array([0.299, 0.587, 0.114])


def load(p, mode='RGBA', at=None):
    data = subprocess.run(['git', 'show', f'{at}:assets/{p}'], cwd=ROOT, capture_output=True, check=True).stdout if at else open(A(p), 'rb').read()
    return np.asarray(Image.open(io.BytesIO(data)).convert(mode)).astype(float)


def save(arr, p, mode):
    Image.fromarray(np.clip(np.round(arr), 0, 255).astype(np.uint8), mode).save(A(p), 'WEBP', lossless=True, quality=100, method=6, exact=True)


def ray(y, x_from, x_to):                                                    # (the row at x_to of the ray to VP through (x_from, y))
    return VP[1] + (y - VP[1]) * (VP[0] - x_to) / (VP[0] - x_from)


def grow(m, n=1):
    for _ in range(n):
        g = m.copy(); g[1:] |= m[:-1]; g[:-1] |= m[1:]; g[:, 1:] |= m[:, :-1]; g[:, :-1] |= m[:, 1:]; m = g
    return m


def flood(ok, seeds):
    hit = np.zeros_like(ok); todo = list(seeds); h, w = ok.shape
    while todo:
        y, x = todo.pop()
        if 0 <= y < h and 0 <= x < w and ok[y, x] and not hit[y, x]:
            hit[y, x] = True; todo += [(y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)]
    return hit


def regrade(px, m1, s1):                                                     # (each channel's mean and spread brought to m1, s1)
    return np.clip(m1 + (px - px.mean(0)) / (px.std(0) + 1e-6) * s1, 0, 255)


def main():
    global XL, XR, Y0, H
    if os.environ.get('DOJO_WIN'): XL, XR, Y0, H = (int(v) for v in os.environ['DOJO_WIN'].split(','))   # (trying other places)
    names = (('layer_city_off.webp', 'RGBA'), ('street_unlit.webp', 'RGBA'), ('night_far.webp', 'RGB'), ('street_sun.webp', 'RGB'))
    x0, y0, x1, y1 = ZONE
    o, t = load('layer_city_off.webp', 'RGBA', OLD)[y0:y1, x0:x1], load('layer_city_off.webp', 'RGBA', TREE)[y0:y1, x0:x1]
    changed = np.abs(o - t).sum(2) > 0
    still = np.abs(load('layer_city_off.webp', 'RGBA', BEFORE)[y0:y1, x0:x1] - t).sum(2) == 0
    dark = changed & still & (t[..., :3] @ LUM < LEAF)                       # (the tree's dark pixels, as they still are)
    core = dark & np.roll(dark, 1, 1) & np.roll(dark, -1, 1)                 # (three dark in a row: leaves, not a thin line)
    leaf = flood(core, [(y1 - y0 - 1, x) for x in range(x1 - x0)])           # (the crown: from the zone's foot up)
    leaf = grow(leaf) & dark                                                 # (its edge leaves back)
    front = leaf | (grow(leaf, 2) & dark)                                    # (and the dark ones close to it: what stays in front)
    out = flood(~leaf, [(0, x) for x in range(x1 - x0)])                     # (the wall over the crown: from the top, not crossing it)

    B = [load(n, m, BEFORE) for n, m in names]; L_ = [load(n, m) for n, m in names]
    for l, b in zip(L_, B): l[y0:y1, x0:x1] = b[y0:y1, x0:x1]

    # the old window's part of the wall (REFILL; right of it the painter's boards are clean): each pixel the board of its
    # own ray where that ray crosses the wall's clean boards (CLEAN), or, where it does not, the board a whole number of
    # boards over (the boards' spacing as seen from VP: DTHETA)
    cx0, cx1, cy0, cy1 = CLEAN
    def board(x, y):                                                         # (its grain kept: along the board, a different pixel
        th = np.arctan2(y - VP[1], x - VP[0])                                # of the clean boards for each column, back and forth)
        for k in sorted(range(-12, 13), key=abs):
            tn = np.tan(th + k * DTHETA)
            pts = [(int(round(VP[1] + tn * (xs - VP[0]))), xs) for xs in range(cx0, cx1 + 1)]
            pts = [p for p in pts if cy0 <= p[0] <= cy1]
            if pts:
                n = len(pts); i = (cx0 - 1 - x) % (2 * n)                     # (mirrored from the clean boards' edge: no seam)
                return pts[i if i < n else 2 * n - 1 - i]
    rx0, ry0, rx1, ry1 = REFILL
    for x in range(rx0, rx1):
        for y in range(ry0, ry1):
            if out[y - y0, x - x0]:
                s = board(x, y)
                for l, b in zip(L_, B): l[y, x] = b[s]
    wall = [l.copy() for l in L_]

    # the reference's whole window, seen square on (its tiled hood, its frame and panes, its balcony: UNIT, in the
    # reference's pixels; round them its own wall, left out), set into the wall (its hood thinner, its end showing):
    # across it u, closer together toward VP
    # (as a wall going away has its columns), down it v, between its top and its foot on their rays (whole rows). Each
    # pixel the mean of the reference over its patch (4 x 4 samples; the window's where most of them fall on it, else the
    # wall's), then the nearest of the reference's own colours (24 of them, no dither)
    ref = Image.open(REF).convert('RGB'); R_ = np.asarray(ref).astype(float); rh, rw = R_.shape[:2]
    pal = np.asarray(ref.quantize(colors=24, method=Image.Quantize.MEDIANCUT).getpalette()[:72]).reshape(24, 3).astype(float)
    unit = np.zeros((rh, rw), bool)
    for ux0, uy0, ux1, uy1 in UNIT: unit[uy0:uy1, ux0:ux1] = True
    gx0, gy0, gx1, gy1 = GLASS
    a0, a1 = 1 / (VP[0] - XL), 1 / (VP[0] - XR - 1)
    U = lambda x: (1 / (VP[0] - x) - a0) / (a1 - a0)                         # (where a column's left side falls across it)
    pic, shade, warm, inglass = {}, {}, {}, {}
    vref = lambda v: v / HOOD_V * HOOD_FOOT if v < HOOD_V else HOOD_FOOT + (v - HOOD_V) / (1 - HOOD_V) * (rh - HOOD_FOOT)   # (its rows)
    for x in range(XL, XR + 1):
        top, bot = int(round(ray(Y0, XL, x))), int(round(ray(Y0 + H, XL, x)))
        for y in range(top, bot):
            pts = [(min(rw - 1, int((U(x) + (U(x + 1) - U(x)) * (a + 0.5) / 4) * rw)), min(rh - 1, int(vref((y - top + (b + 0.5) / 4) / (bot - top)))))
                   for a in range(4) for b in range(4)]
            on_ = [(xr, yr) for xr, yr in pts if unit[yr, xr]]
            if len(on_) >= 8:
                c = np.mean([R_[yr, xr] for xr, yr in on_], 0); q = pal[np.argmin(((pal - c) ** 2).sum(1))]
                pic[y, x] = q; warm[y, x] = q[0] > q[2] + 8
                inglass[y, x] = np.mean([gx0 <= xr < gx1 and gy0 <= yr < gy1 for xr, yr in on_]) >= 0.5
            else:                                                            # (the wall round it: in the hood's shadow under it)
                v = (y - top + 0.5) / (bot - top) - HOOD_V
                f = 1.0 if v < 0 else SHADE[0] + (1 - SHADE[0]) * min(1.0, v / SHADE[1])
                shade[y, x] = 1 - (1 - f) * min(1.0, (min(x - XL, XR - x) + 0.5) / SHADE[2])   # (softer toward the hood's ends)
    hood = [c for (y, x), c in pic.items() if (y - int(round(ray(Y0, XL, x)))) < HOOD_V * H * (VP[0] - x) / (VP[0] - XL)]
    endc = np.array(sorted(hood, key=lambda c: c @ LUM)[len(hood) // 8])     # (the hood's end, square to us: its shaded tone)
    for x in range(XL - HOOD_END, XL):
        for y in range(Y0, int(round(Y0 + HOOD_V * H))):
            pic[y, x] = endc; warm[y, x] = False; inglass[y, x] = False
    keys = list(pic); px = np.array([pic[k] for k in keys]); W_ = np.array([warm[k] for k in keys]); G_ = np.array([inglass[k] for k in keys])
    his = load('layer_city_off.webp', 'RGBA', HIS_AT)
    glass, frame = (his[b:c, a:d, :3].reshape(-1, 3) for a, d, b, c in (HIS_GLASS, HIS_FRAME))
    off = px.copy()
    off[W_ & G_] = regrade(px[W_ & G_], glass.mean(0), glass.std(0))          # (off: its panes his dark glass, the folds kept; what
    wood = ~W_                                                                # its frame and rail his navy; what their light lit
    off[wood] = regrade(px[wood], frame.mean(0), np.minimum(px[wood].std(0), 3 * frame.std(0)))   # outside them, that wood unlit)
    off[W_ & ~G_] = off[wood].mean(0) * 1.1
    s_ = open(A('street.js'), encoding='utf-8').read()
    upi = load(UP + '.webp', 'RGBA', HIS_AT)
    upl = upi[upi[..., 3] == 255][:, :3]
    on = regrade(px[W_], upl.mean(0), upl.std(0))                             # (its light: the street's lit home window)
    OFF = dict(zip(keys, off)); LITP = dict(zip([k for k, w in zip(keys, W_) if w], on))
    wz = (~front) & (np.arange(x1 - x0) < WALL_X1)[None, :]                  # (the wall in sight: each layer's light on it)
    gain = [l[y0:y1, x0:x1, :3][wz].mean(0) / wall[0][y0:y1, x0:x1, :3][wz].mean(0) for l in wall[:2]]

    # in sight: what the tree does not hide, on the wall; its light only where the leaves part over a few pixels together
    vis = lambda k: k[1] < WALL_X1 and y0 <= k[0] < y1 and not front[k[0] - y0, k[1] - x0]
    seen = {k for k in pic if vis(k)}
    glow = np.zeros((y1 - y0, x1 - x0), bool)
    for (y, x) in seen:
        if (y, x) in LITP: glow[y - y0, x - x0] = True
    lab = np.zeros(glow.shape, int); n_lab = 0
    for (y, x) in zip(*np.where(glow)):
        if lab[y, x]: continue
        n_lab += 1; comp = flood(glow & (lab == 0), [(y, x)]); lab[comp] = n_lab
    size = np.bincount(lab.ravel())
    spr = np.zeros(L_[0].shape[:2] + (4,))
    for (y, x) in seen:
        for l, g in zip(L_[:2], gain): l[y, x, :3] = OFF[y, x] * g; l[y, x, 3] = 255
        L_[2][y, x] = 0
        L_[3][y, x] = 0 if (y, x) in LITP else wall[3][y, x]
        if (y, x) in LITP and size[lab[y - y0, x - x0]] >= GLOW_MIN: spr[y, x] = [*LITP[y, x], 255]
    for (y, x), f in shade.items():                                          # (the hood's shadow on the wall, in each layer)
        if vis((y, x)) and f < 1:
            for l in L_[:2]: l[y, x, :3] *= f
            L_[3][y, x] = L_[3][y, x] * f
    n_win = len(seen)

    for (n, m), l in zip(names, L_): save(l, n, m)
    ys, xs = np.where(spr[..., 3] > 0)
    bx, by, bw, bh = int(xs.min()), int(ys.min()), int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1)
    save(spr[by:by + bh, bx:bx + bw], 'win_dojo.webp', 'RGBA')
    s_ = re.sub(r'"win_dojo": \{"src": "assets/win_dojo\.webp\?v=(\d+)", "x": \d+, "y": \d+, "w": \d+, "h": \d+\}',
                lambda m_: f'"win_dojo": {{"src": "assets/win_dojo.webp?v={m_.group(1)}", "x": {bx}, "y": {by}, "w": {bw}, "h": {bh}}}', s_)
    open(A('street.js'), 'w', encoding='utf-8').write(s_)
    print('wall: boards over', REFILL, '| window', XR - XL + 1, 'x', H, 'at', (XL, Y0), ':', n_win, 'px in sight | its light', len(xs), 'px at', (bx, by, bw, bh))


if __name__ == '__main__':
    main()
