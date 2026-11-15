#!/usr/bin/env python3
"""止まれ on the road redrawn as a real road marking: the three characters from the font, each long on the ground as the
real ones are, with a clear space between them, in the road's perspective.

    (a module: tools/redraw_zones.py's zone 'tomare' calls draw() on the street as the zones before it leave it, last;
     it also writes the ground lights that carry the paint, assets/gl_*.webp, from their before crops)
    python3 tools/tomare_marking.py --befores   the ground lights' before crops (tools/src/edits/tomare_before_<gl>.webp),
                                                once, from the assets as they are, before the zone is first run

What was there (tools/tomare.py, kept for its history): 止 carried far by the crosswalk, the painter's ま under it, れ from
the font near; 止 sat on ま with no space, the two read as one character ("集れ"), above all on a phone, where the
marking is right under the name. Now the three are drawn alike: each character of IPAGothic (tools/src/tomare_re.png's
way: 1000 px, thickened THICK px) stretched over its own rectangle of the road, LEN m long and the painter's width
(X from XL to XR, measured on his letters), with GAP m of asphalt between them, from ZFAR (just past the crosswalk's
line) to ZNEAR (short of the puddle): 止 farthest, ま, れ nearest. Seen from the eye, the far one is short and the near
one long, as on a real street; the spaces keep them apart.

The paint is the painter's, layer by layer (the street, the power cut, and each ground light whose box touches it: the
paint gives back more of a light than the asphalt): where a letter was and is no more, the asphalt (smoothed along its
row from the asphalt round it) and the grain of an asphalt pixel of the same row; where a letter is, the asphalt times
the paint's own ratio to it (its median over the old letters, channel by channel, in that layer) and the grain of a
pixel of the old paint from the nearest painted rows; the edges in between by coverage (SUB x SUB points a pixel).
The draws are seeded: the same bytes each time. The water's sheen and the rain lie on it as on the rest of the road.
Needs numpy, scipy, Pillow.
"""
import os
import re
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as nd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDITS = os.path.join(ROOT, 'tools', 'src', 'edits')
BOX = (600, 682, 800, 790)                       # the zone: below the crosswalk's line (680-681), short of the puddle
VP, F, EYE = (700.0, 615.0), 1400.0, 1.5         # (tools/tomare.py's camera of the road)
GLYPHS = '止まれ'                                 # far to near
ZFAR, ZNEAR, GAP = 31.0, 12.6, 1.8               # m: the far end of 止, the near end of れ, the asphalt between two
XL, XR = -0.71, 0.65                             # m: the letters' width, the painter's
THICK = 44                                       # px of the 1000 px glyph added round its strokes
FONT = '/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf'
SUB = 6
SEED = 33
COLS = (630, 770)                                # (where the old letters are)

Zof = lambda y: F * EYE / (y - VP[1])
Yof = lambda Z: VP[1] + F * EYE / Z
Xof = lambda x, Z: (x - VP[0]) * Z / F


def glyph(ch):
    f = ImageFont.truetype(FONT, 1000)
    im = Image.new('L', (1300, 1300), 0); ImageDraw.Draw(im).text((150, 50), ch, font=f, fill=255)
    g = nd.binary_dilation(np.asarray(im) > 127, iterations=THICK // 2)
    ys, xs = np.where(g)
    return g[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def places():
    LEN = (ZFAR - ZNEAR - GAP * (len(GLYPHS) - 1)) / len(GLYPHS)
    out, zf = [], ZFAR
    for ch in GLYPHS:
        out.append((ch, zf - LEN, zf)); zf -= LEN + GAP
    return out


def coverage(box):
    """each pixel's share of paint, 0..1 (SUB x SUB points of the ground in it)"""
    x0, y0, x1, y1 = box
    cov = np.zeros((y1 - y0, x1 - x0)); xs = np.arange(x0, x1)
    for ch, zn, zf in places():
        g = glyph(ch); gh, gw = g.shape
        for y in range(max(y0, int(Yof(zf)) - 1), min(y1, int(Yof(zn)) + 2)):
            acc = np.zeros(x1 - x0)
            for i in range(SUB):
                Z = Zof(y + (i + 0.5) / SUB); v = (zf - Z) / (zf - zn)
                if not 0 <= v < 1: continue
                for j in range(SUB):
                    u = (Xof(xs + (j + 0.5) / SUB, Z) - XL) / (XR - XL)
                    ok = (u >= 0) & (u < 1)
                    acc += np.where(ok, g[min(int(v * gh), gh - 1), np.clip((u * gw).astype(int), 0, gw - 1)], 0)
            cov[y - y0] = np.maximum(cov[y - y0], acc / (SUB * SUB))
    return cov


def old_paint(V):
    """the old letters' coverage, 0..1, from the street's layer (its blue over each row's asphalt), as tools/tomare.py reads it"""
    b = V[..., 2]; c = np.zeros_like(b)
    for r in range(b.shape[0]):
        row = b[r]; a = np.median(row); m = row > a + 35
        p = np.percentile(row[m], 80) if m.sum() > 3 else a + 80
        c[r] = np.clip((row - a) / max(p - a, 1), 0, 1)
    c[:, :COLS[0] - BOX[0]] = 0; c[:, COLS[1] - BOX[0]:] = 0
    return c


def lisse(v, w, sy, sx):
    num = nd.gaussian_filter(v * w[..., None], (sy, sx, 0)); den = nd.gaussian_filter(w.astype(float), (sy, sx))[..., None]
    return num / np.maximum(den, 1e-6)


def plan(V0):
    """what goes and what comes, and the pixels each one's grain is drawn from (seeded): from the street's layer"""
    cov0 = old_paint(V0)
    new = coverage(BOX)
    old = nd.binary_dilation(cov0 > 0.12)
    touch = old | (new > 0)
    clean = ~nd.binary_dilation(cov0 > 0.05, iterations=2)
    paint = cov0 > 0.85
    H, W = cov0.shape
    rng = np.random.default_rng(SEED)
    prow = np.where(paint.any(1))[0]
    pa = np.zeros((H, W, 2), int); pp = np.zeros((H, W, 2), int)
    for r, c in zip(*np.where(touch)):
        for d in range(40, W, 10):
            cs = np.where(clean[r, max(0, c - d):c + d + 1])[0] + max(0, c - d)
            if len(cs) >= 8: break
        pa[r, c] = (r, cs[rng.integers(len(cs))])
        near = prow[np.argsort(np.abs(prow - r), kind='stable')][:3]
        cand = [(a, b) for a in near for b in np.where(paint[a])[0]]
        pp[r, c] = cand[rng.integers(len(cand))]
    return dict(new=new, old=old, touch=touch, clean=clean, paint=paint, pa=pa, pp=pp)


def repaint(V, P, have=None):
    """one layer's box (H, W, 3) with the new letters (have: where the layer has pixels, a ground light's box)"""
    have = np.ones(V.shape[:2], bool) if have is None else have
    As = lisse(V, P['clean'] & have, 1.0, 10)
    pm = P['paint'] & have
    k = np.clip(np.median(V[pm], 0) / np.maximum(np.median(As[pm], 0), 1e-3), 1.0, 6.0) if pm.sum() > 20 else np.ones(3)
    out = V.copy()
    for r, c in zip(*np.where(P['touch'])):
        a, b = P['pa'][r, c]; e, f = P['pp'][r, c]
        base = As[r, c] + (V[a, b] - As[a, b]) if P['old'][r, c] else V[r, c]
        pnt = As[r, c] * k + (V[e, f] - As[e, f] * k)
        q = P['new'][r, c]
        out[r, c] = (1 - q) * base + q * pnt
    return np.clip(out, 0, 255)


def ground_lights():
    """the ground lights whose box touches the zone: (name, (x, y)) from street.js"""
    js = open(os.path.join(ROOT, 'assets', 'street.js'), encoding='utf-8').read()
    x0, y0, x1, y1 = BOX; out = []
    for m in re.finditer(r"url: 'assets/(gl_[a-z0-9_]+)\.webp\?v=\d+', box: \[(\d+), (\d+), (\d+), (\d+)\]", js):
        n, bx, by, bw, bh = m.group(1), *map(int, m.groups()[1:])
        if bx < x1 and bx + bw > x0 and by < y1 and by + bh > y0: out.append((n, (bx, by)))
    return out


def clip_box(gx, gy, g):
    x0, y0, x1, y1 = BOX
    return max(x0, gx), max(y0, gy), min(x1, gx + g.shape[1]), min(y1, gy + g.shape[0])


def befores():
    for n, (gx, gy) in ground_lights():
        g = np.asarray(Image.open(os.path.join(ROOT, 'assets', n + '.webp')).convert('RGBA'))
        a, b, c, d = clip_box(gx, gy, g)
        Image.fromarray(g[b - gy:d - gy, a - gx:c - gx], 'RGBA').save(os.path.join(EDITS, f'tomare_before_{n}.webp'), 'WEBP',
                                                                       lossless=True, quality=100, method=6, exact=True)
        print('tomare_before_' + n, (a, b, c, d))


def draw(city, unlit, box=BOX):
    """The zone: both layers' boxes in place, the ground lights written; returns what changed (whole scene)."""
    x0, y0, x1, y1 = box
    H, W = city.shape[:2]
    P = plan(city[y0:y1, x0:x1, :3].copy())
    for L in (city, unlit):
        L[y0:y1, x0:x1, :3] = repaint(L[y0:y1, x0:x1, :3].copy(), P)
    for n, (gx, gy) in ground_lights():
        path = os.path.join(ROOT, 'assets', n + '.webp')
        g = np.asarray(Image.open(path).convert('RGBA')).astype(float).copy()
        a, b, c, d = clip_box(gx, gy, g)
        g[b - gy:d - gy, a - gx:c - gx] = np.asarray(Image.open(os.path.join(EDITS, f'tomare_before_{n}.webp')).convert('RGBA')).astype(float)
        full = np.zeros((y1 - y0, x1 - x0, 3)); full[b - y0:d - y0, a - x0:c - x0] = g[b - gy:d - gy, a - gx:c - gx, :3]
        hv = np.zeros((y1 - y0, x1 - x0), bool); hv[b - y0:d - y0, a - x0:c - x0] = True
        out = repaint(full, P, hv)
        g[b - gy:d - gy, a - gx:c - gx, :3] = out[b - y0:d - y0, a - x0:c - x0]
        Image.fromarray(np.round(g).astype(np.uint8), 'RGBA').save(path, 'WEBP', lossless=True, quality=100, method=6, exact=True)
    print('tomare:', ', '.join(f'{ch} rows {Yof(zf):.1f}-{Yof(zn):.1f}' for ch, zn, zf in places()))
    ch = np.zeros((H, W), bool); ch[y0:y1, x0:x1] = P['touch']
    return ch


if __name__ == '__main__':
    if '--befores' in sys.argv:
        befores()
