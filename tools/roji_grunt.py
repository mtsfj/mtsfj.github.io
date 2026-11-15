#!/usr/bin/env python3
"""The roji's emergency exit (tools/roji_alley.py): now and then a Team Rocket grunt sneaks out of it for a smoke, and Pikachu,
on the Center's roof right above him with Red (tools/center_red.py), zaps him.

    python3 tools/roji_grunt.py                     (writes assets/roji_grunt.webp and, in assets/street.js, the line RJS:
                                                     it can be run again, it writes the same bytes)
    python3 tools/roji_grunt.py --preview DIR       (only shows it: the atlas x6 on the alley's wall, RJS in json)

His sheet (tools/src/roji_grunt_sheet.webp: the image model's answer to tools/src/edits/roji_grunt_in.webp and _prompt.txt,
the style taken from roji_grunt_in_style.webp, R28): a grunt in the black uniform, the red R on his chest, a black cap, white
gloves and boots, painted, no outline, on white, eight frames: sneaking out toward the left (step), glancing left (look_l)
and right (look_r), lighting a cigarette in his cupped hands (light), smoking at ease (hold), electrocuted, stiff, his cap
off (zap1), blackened with soot (zap2), fleeing to the right (flee). Each cut off its white (tools/ichiraku_figures.py: cut),
the sheet's painted smoke and the lighter's flame taken out (CLEAR: street.js draws the flame, the ember and the smoke,
alive), brought down to his size at his place by one scale (each scene pixel the mean of the sheet's pixels it covers,
solid from half covered), set by his feet.

His place: in the alley, in front of its far wall (the Center's side, 23.08 m: tools/roji_alley.py), 0.6 m out from it,
between the Center's corner and the door (X 5.15 m, Z 22.48 m: 42.7 px a metre), on its floor (the sidewalk's level): his
feet at FOOT, 1.75 m tall. Light: the alley's night (AMB, cold and low: as dark as what is round him, VALUES), the exit
sign's green over him from above and to his right (RIM_SIGN, on his top edges); and a second layer, the door's light on his
right edge (WARM: laid by street.js, added, while the door is open). In its families of tones (FAMILIES), no dark line at
the edge on the lit side, few lone pixels, a fine grain. Where the cigarette's tip is in each image (EMBER: the lighter's
flame in 'light'), for street.js. Needs Pillow, numpy (and what tools/ichiraku_figures.py needs).
"""
import json
import os
import re
import sys
import numpy as np
from PIL import Image

sys.dont_write_bytecode = True
ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import ichiraku_figures as FG                                    # noqa: E402
import ichiraku_interior as R                                    # noqa: E402

ROOT = os.path.dirname(ICI)
SHEET = os.path.join(ICI, 'src', 'roji_grunt_sheet.webp')
OUT = os.path.join(ROOT, 'assets', 'roji_grunt.webp')
JS = os.path.join(ROOT, 'assets', 'street.js')
F, VPX, VPY, EYE, HS = 960.0, 700.0, 615.0, 1.41, 1.41 - 0.2555 * 5.0   # (the street's camera; the alley's floor, m)
X_M, Z_M, H_M = 5.15, 22.48, 1.75                # his place (m across, m deep) and his height
FOOT = (int(round(VPX + F * X_M / Z_M)), int(round(VPY - F * (HS - EYE) / Z_M)))   # his feet in the street (920, 670)
CELLS = {'step': (5, 4, 287, 452), 'look_l': (297, 4, 579, 452), 'look_r': (589, 4, 871, 452), 'light': (881, 4, 1163, 452),
         'hold': (5, 462, 287, 908), 'zap1': (297, 462, 579, 908), 'zap2': (589, 462, 871, 908), 'flee': (881, 462, 1163, 908)}
CLEAR = {'hold': [(80, 494, 103, 548)], 'light': [(1056, 123, 1070, 145)]}   # (the painted smoke, the flame)
EMBER = {'hold': (105, 551), 'light': (1062, 136)}   # (the cigarette's tip, the flame: in the sheet)
REF = 'hold'                                     # (his height measured on this image: standing)
AMB = (0.40, 0.40, 0.52)                         # the alley's night on him (cold, low)
VALUES = (10.0, 24.0)                            # (L*: the plaster round him is 22-25 at 22 h; he is a little darker)
RIM_SIGN = ((92, 196, 142), 0.30)                # the exit sign's green on his top edges (from above, a little to his right)
WARM = (255, 214, 162)                           # the door's light on his right edge (its own layer)
FAMILIES = 12
GRAIN, GRAIN_T = 2, 8
LIGHT = (0.4, -1.0)


def values(P):
    lab_ = R.lab(P); L = lab_[:, 0]; top = max(L.max(), VALUES[1] + 1e-6)
    lab_[:, 0] = np.where(L > VALUES[0], VALUES[0] + (L - VALUES[0]) * (VALUES[1] - VALUES[0]) / (top - VALUES[0]), L)
    return FG.lab2rgb(lab_)


def cut_all():
    sheet = {'s': np.asarray(Image.open(SHEET).convert('RGB')).astype(float)}
    out = {}
    for n, box in CELLS.items():
        Q, a, _ = FG.cut(sheet, 's', box, 'free', {})
        a = a.astype(float).copy()
        for x0, y0, x1, y1 in CLEAR.get(n, ()):
            a[y0 - box[1]:y1 - box[1], x0 - box[0]:x1 - box[0]] = 0
        out[n] = (Q, a, box)
    return out


def shrink(Q, a, box, s, n):
    """the image at s scene px a sheet px, set by its feet (the bottom row of its solid, the middle of its lowest tenth): each
    scene pixel the mean of the sheet's pixels it covers (6 x 6 samples), solid from half covered; (ax, ay) its feet in it"""
    m = a > 0.5; ys, xs = np.nonzero(m); bot = ys.max() + 1
    low = ys >= bot - 0.1 * (bot - ys.min()); fx = (xs[low].min() + xs[low].max() + 1) / 2
    H, W = m.shape
    x0 = int(np.floor(-fx * s)) - 1; x1 = int(np.ceil((W - fx) * s)) + 1; y0 = int(np.floor(-bot * s)) - 1
    w, h = x1 - x0, -y0 + 1
    S = 6; off = (np.arange(S) + 0.5) / S
    acc = np.zeros((h, w, 3)); cov = np.zeros((h, w))
    for oy in off:
        for ox in off:
            sx = fx + (np.arange(w)[None, :] + x0 + ox) / s; sy = bot + (np.arange(h)[:, None] + y0 + oy) / s
            ix = np.clip(np.floor(sx).astype(int), 0, W - 1); iy = np.clip(np.floor(sy).astype(int), 0, H - 1)
            ok = (sx >= 0) & (sx < W) & (sy >= 0) & (sy < H)
            al = np.where(ok, a[iy, ix], 0.0); acc += Q[iy, ix] * al[..., None]; cov += al
    cov /= S * S; rgb = acc / np.maximum(cov[..., None] * S * S, 1e-6)
    sol = cov >= 0.5
    ex, ey = EMBER.get(n, (None, None))
    em = None if ex is None else [int(np.floor((ex - box[0] - fx) * s)), int(np.floor((ey - box[1] - bot) * s))]   # (from his feet)
    ys, xs = np.nonzero(sol); t, b_, l, r_ = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1   # (the cell: his solid's box)
    return dict(rgb=rgb[t:b_, l:r_], m=sol[t:b_, l:r_], ax=-x0 - l, ay=-y0 - t, em=em)


def layers(cells):
    """the night (the alley's, the sign's green on his top edges) and the door's warm edge, each image"""
    base = {n: c['rgb'] * np.array(AMB) for n, c in cells.items()}
    for n, c in cells.items():
        base[n] = FG.rim(base[n], c['m'], (0.35, -1.0), RIM_SIGN[0], RIM_SIGN[1], cos=0.45)
    allc = np.concatenate([base[n][c['m']] for n, c in cells.items()])
    fam = FG.palette(np.clip(allc, 0, 255), FAMILIES); Lf = R.lab(fam)[:, 0]; famB = values(fam)
    tile = np.random.default_rng(23).integers(-GRAIN, GRAIN + 1, (GRAIN_T, GRAIN_T))
    for n, c in cells.items():
        m = c['m']; h, w = m.shape
        idx = np.where(m, R.nearest(np.clip(base[n].reshape(-1, 3), 0, 255), fam).reshape(m.shape), -1)
        idx = FG.no_outline(idx, m, Lf, LIGHT)
        idx = FG.unspeckle(idx, m, np.zeros_like(m))
        gr = np.tile(tile, (h // GRAIN_T + 1, w // GRAIN_T + 1))[:h, :w]
        night = np.zeros((h, w, 4)); night[..., 3] = m * 255
        night[..., :3] = np.clip(np.round(famB[np.maximum(idx, 0)] + gr[..., None]), 0, 255) * m[..., None]
        p = np.pad(m, 1); edge = m & ~(p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:])
        nx, ny = FG.normals(m); on = edge & (nx * 1.0 + ny * -0.1 >= 0.35)
        warm = np.zeros((h, w, 4)); warm[on, :3] = WARM; warm[on, 3] = 255
        c['night'], c['warm'] = night, warm


def main():
    prev = sys.argv[sys.argv.index('--preview') + 1] if '--preview' in sys.argv else None
    raw = cut_all()
    Qr, ar, _ = raw[REF]; ys = np.nonzero((ar > 0.5).any(1))[0]
    s = H_M * F / Z_M / (ys[-1] + 1 - ys[0])                          # (scene px a sheet px: his height at his place)
    cells = {n: shrink(Q, a, box, s, n) for n, (Q, a, box) in raw.items()}
    layers(cells)
    U = FG.Atlas(128); boxes = {}
    for n in CELLS:
        c = cells[n]; boxes[n] = U.add(np.round(c['night']).astype(np.uint8), np.round(c['warm']).astype(np.uint8)) + [int(c['ax']), int(c['ay'])]
    img, dy = U.image()
    RJS = {'cells': boxes, 'warm': dy, 'x': FOOT[0], 'y': FOOT[1],
           'ember': {n: [int(e) for e in cells[n]['em']] for n in CELLS if cells[n]['em'] is not None}}
    print('the grunt: %.3f scene px a sheet px, %d px tall, feet at %s | atlas %d x %d' % (
        s, boxes[REF][3], FOOT, img.shape[1], img.shape[0]))
    if prev:
        os.makedirs(prev, exist_ok=True)
        bg = np.full(img.shape[:2] + (3,), (54, 51, 85), float); al = img[..., 3:] / 255
        Image.fromarray((bg * (1 - al) + img[..., :3] * al).astype(np.uint8)).resize((img.shape[1] * 6, img.shape[0] * 6), Image.NEAREST).save(os.path.join(prev, 'grunt_x6.png'))
        json.dump(RJS, open(os.path.join(prev, 'rjs.json'), 'w'))
        return
    Image.fromarray(img, 'RGBA').save(OUT, 'WEBP', lossless=True, quality=100, method=6, exact=True)
    js = open(JS, encoding='utf-8').read()
    line = 'const RJS = ' + json.dumps(RJS, separators=(',', ':')) + ';'
    js2, k = re.subn(r'const RJS = \{.*?\};', lambda m_: line, js, count=1)
    if k and js2 != js: open(JS, 'w', encoding='utf-8').write(js2)
    print('wrote', OUT, '| street.js RJS', 'updated' if k else 'NOT FOUND')


if __name__ == '__main__':
    main()
