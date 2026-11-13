#!/usr/bin/env python3
"""Luffy (One Piece) on the oden's roof sign: the fourth of the four heroes, sat cross-legged on the box sign おでん over the
shop (a nod to Wano's Kozuki Oden), a meat on the bone in his hands, in the rain, under the dusk and the sign's red light.

    python3 tools/luffy_oden.py                 (reads tools/src/luffy_oden_sheet.webp; writes assets/luffy_oden.webp and,
                                                 in assets/street.js, the line LFO; again: the same bytes)
    python3 tools/luffy_oden.py --preview DIR   (previews only: the atlas x8, each frame on the street x6)

The sheet (a draft drawn for this, on white, eight frames of the same seated figure: at rest, the meat lifted to his mouth,
a bite, chewing, a hand on his hat, a grin, waving, asleep with a bubble at his nose) is cut from the white, each frame
whole (its small white holes, the teeth and the eyes, filled; the gaps between an arm and the body left open), and the
frames registered on their crossed legs: the soles' lowest row and the middle of the legs. The sheet draws the legs a
little differently each time; reduced, the rest frame's legs are laid in all the others (LEGS: under his lap), so nothing
flickers there from one frame to the next (and the grain's families are kept from a frame to the next: TEMPO).

His size, the street's (tools/figures_audit.py, the camera B): the sign stands on the oden's eave about 25 m from the eye,
its box 44 px tall for a metre: 44 px a metre. Luffy is 1.74 m; cross-legged, from the top of his hat to his soles, 0.98 m:
H px. Each frame is boxed down to that scale with one factor for all (the rest frame's height), each pixel the part of the
sheet it covers (an exact box), full from half covered, its colour the mean of the sheet's pixels nearest their median
inside the figure (two pixels in from its edge: the sheet's dark outline does not come down with it).

His light, the street's at that place (R2, R12): his picture is the dusk alone, as the power cut leaves it (the base row):
the night's ambient on what faces us (AMB, cool and dim), the sunset's terracotta on what faces the far end of the street
(on his right: RIM, the silhouette's pixels whose outside is up or to the right, and a little on the next one in), the
zenith's violet on what faces up (TOP); no outline (a pixel at the edge is never darker than the one it covers, by
OUTLINE_DL). Then the painter's grain (tools/regrain.py: FAMILIES families of tones for all his frames together, a fine
grain baked in, anchored at his seat). The sign's light (the second row, added by street.js with the sign's level, the
shop's hours and its power, red in the red night): the box glows just under his feet, so its red reaches his soles, his
shins and the fur of his cuffs, the meat in his lap, fading up to his waist (SIGN, GLOW_H).

His face, drawn by hand (tools/visages.py: at 9 px of head a reduced face is a smudge): per frame a small template on the
face's place (FACES: the eyes a pixel each, of his hair's darkest, never black; a smile, an open mouth, the teeth, shut
eyes, each a pixel or two of his own skin's colours), laid after the light and the grain. Made from the frames: rest_b
(his breath: all above his sash a pixel higher), chew_b (his jaw), asleep without the sheet's bubble (doze) and with
one blown at his nose in three sizes (doze_1..3: thin water, the dusk through it, a glint), and the wave stretched: his
raised arm drawn longer, rubber (wave_2: STRETCH[0] px more, wave_3: STRETCH[1]), its hand a pixel aside (wave_3b: the
wave). The atlas: a column a frame (ORDER), the base row over the light's. Needs Pillow, numpy, scipy.
"""
import json
import os
import re
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as nd

ICI = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(ICI)
sys.path.insert(0, ICI)
import regrain as RG                                             # noqa: E402

SRC = os.path.join(ICI, 'src', 'luffy_oden_sheet.webp')
OUT = os.path.join(ROOT, 'assets', 'luffy_oden.webp')
JS = os.path.join(ROOT, 'assets', 'street.js')
LUM = np.array([0.299, 0.587, 0.114])
NAMES = ['rest', 'lift', 'bite', 'chew', 'hat', 'grin', 'wave', 'doze']   # the sheet's frames, row by row
H = 43                          # cross-legged, the top of his hat to his soles (0.98 m at 44 px a metre)
CW, CH = 40, 66                 # a cell; his seat's anchor at (AX, AY), his soles' lowest row the cell's last
AX, AY = 20, 65
INK = 40                        # (what is the figure: this far from white, 0..765)
HOLE = 900                      # (white holes inside him smaller than this, px of the sheet: teeth, eyes, filled)
SEAT = (489, 491)               # in the street: his anchor (the middle of his crossed legs, the soles' lowest row) on the sign
AMB = np.array([0.36, 0.31, 0.44])        # the night's ambient on what faces us
RIM = np.array([50.0, 26.0, 21.0])        # the sunset's terracotta on his right side (added, at full on the edge)
TOP = np.array([16.0, 13.0, 26.0])        # the zenith's violet on what faces up
OUTLINE_DL = 6
SIGN = np.array([0.50, 0.15, 0.08])       # the sign's light on him (its red), times his own colour
GLOW_H = (2, 10)                          # rows above his soles: full up to the first, nothing past the second
FAMILIES = 18
STRETCH = (9, 18)
STRAY = 6


def frames():
    rgb = np.asarray(Image.open(SRC).convert('RGB')).astype(np.float32)
    ink = 765 - rgb.sum(2)
    m = ink > INK
    lab, n = nd.label(nd.binary_closing(m, iterations=2), np.ones((3, 3)))
    sz = nd.sum(m, lab, range(1, n + 1)); sl = nd.find_objects(lab)
    boxes = [(sl[i][0].start, sl[i][1].start, sl[i][0].stop, sl[i][1].stop, i + 1) for i in range(n) if sz[i] > 8000]
    boxes.sort(key=lambda b: (b[0] // 300, b[1]))
    assert len(boxes) == len(NAMES), len(boxes)
    F = {}
    for name, (y0, x0, y1, x1, l) in zip(NAMES, boxes):
        mm = (lab[y0:y1, x0:x1] == l) & m[y0:y1, x0:x1] | (lab[y0:y1, x0:x1] == l) & nd.binary_erosion(lab[y0:y1, x0:x1] == l, iterations=1)
        holes = nd.binary_fill_holes(mm) & ~mm
        hl, hn = nd.label(holes)
        hs = nd.sum(holes, hl, range(1, hn + 1))
        for i, s in enumerate(hs):
            if s < HOLE: mm |= hl == i + 1
        hh, ww = mm.shape
        ys, xs = np.nonzero(mm[int(hh * 0.8):])
        F[name] = dict(m=mm, rgb=rgb[y0:y1, x0:x1], bot=hh - 1 - (hh - 1 - (ys.max() + int(hh * 0.8))),
                       cx=(xs.min() + xs.max()) / 2)
    return F


def boite(A, f, ox, oy, W, Hh):
    """A (the sheet's pixels) at scale f, its (0, 0) at (ox, oy) of the W x Hh output: the part of each pixel covered"""
    h, w = A.shape
    S = np.zeros((h + 1, w + 1)); S[1:, 1:] = A.cumsum(0).cumsum(1)
    def integ(ys, xs):
        ys = np.clip(ys, 0, h); xs = np.clip(xs, 0, w)
        y0 = np.minimum(np.floor(ys).astype(int), h - 1); x0 = np.minimum(np.floor(xs).astype(int), w - 1)
        fy = ys - y0; fx = xs - x0
        return S[y0, x0] * (1 - fy) * (1 - fx) + S[y0 + 1, x0] * fy * (1 - fx) + S[y0, x0 + 1] * (1 - fy) * fx + S[y0 + 1, x0 + 1] * fy * fx
    gy = (np.arange(Hh + 1) - oy) / f; gx = (np.arange(W + 1) - ox) / f
    Y, X = np.meshgrid(gy, gx, indexing='ij'); Q = integ(Y, X)
    return np.clip((Q[1:, 1:] - Q[:-1, 1:] - Q[1:, :-1] + Q[:-1, :-1]) * f * f, 0, 1)


def reduce(f, k):
    """a frame at scale k in its cell: RGBA, his anchor at (AX, AY) (the soles' lowest row the cell's last)"""
    mm, rgb = f['m'], f['rgb']; hh, ww = mm.shape
    ox = AX + 0.5 - f['cx'] * k; oy = AY + 1 - (f['bot'] + 1) * k
    cov = boite(mm.astype(float), k, ox, oy, CW, CH)
    a = cov >= 0.5
    inner = nd.binary_erosion(mm, iterations=3)
    out = np.zeros((CH, CW, 4))
    for i, j in zip(*np.where(a)):
        ya, yb = (i - oy) / k, (i + 1 - oy) / k; xa, xb = (j - ox) / k, (j + 1 - ox) / k
        r0, r1 = max(0, int(np.floor(ya))), min(hh, int(np.ceil(yb))); c0, c1 = max(0, int(np.floor(xa))), min(ww, int(np.ceil(xb)))
        q = inner[r0:r1, c0:c1]
        if q.sum() < 3: q = mm[r0:r1, c0:c1]
        px = rgb[r0:r1, c0:c1][q]
        if not len(px): continue
        med = np.median(px, 0); d = np.abs(px - med).sum(1)
        sel = px[d <= np.median(d)] if len(px) > 3 else px
        out[i, j, :3] = sel.mean(0); out[i, j, 3] = 255
    return out


def light(c):
    """the dusk on him (the base row): AMB times his colour, RIM on what faces his right and up, TOP on what faces up"""
    a = c[..., 3] > 0
    P = np.pad(a, 1)
    up = a & ~P[:-2, 1:-1]; right = a & ~P[1:-1, 2:]; left = a & ~P[1:-1, :-2]
    up2 = a & ~up & np.roll(up, 1, 0); right2 = a & ~right & np.roll(right, -1, 1)
    out = c.copy()
    col = c[..., :3] * AMB
    rim = (right * 1.0 + right2 * 0.45 + up * 0.55 + up2 * 0.2)[..., None] * RIM / 255.0 * (c[..., :3] + 60) / 1.0
    top = (up * 1.0 + up2 * 0.4)[..., None] * TOP / 255.0 * (c[..., :3] + 80)
    out[..., :3] = np.where(a[..., None], np.clip(col + rim * 0.9 + top * 0.8, 0, 255), 0)
    # no dark line round him: an edge pixel never darker than the one it covers by OUTLINE_DL
    L = out[..., :3] @ LUM
    edge = a & ~nd.binary_erosion(a)
    for y, x in zip(*np.nonzero(edge)):
        best = None
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            yy, xx = y + dy, x + dx
            if 0 <= yy < a.shape[0] and 0 <= xx < a.shape[1] and a[yy, xx] and not edge[yy, xx]:
                if best is None or L[yy, xx] > L[best]: best = (yy, xx)
        if best and L[y, x] < L[best] - OUTLINE_DL: out[y, x, :3] = out[best][:3] * 0.92
    return out


def sign_glow(c, albedo):
    """the sign's red on him (the second row): his own colour times SIGN, full on his lowest GLOW_H[0] rows, none past GLOW_H[1]"""
    a = c[..., 3] > 0
    r = AY - np.arange(CH)
    w = np.clip((GLOW_H[1] - r) / (GLOW_H[1] - GLOW_H[0]), 0, 1)[:, None]
    g = np.zeros_like(c)
    g[..., :3] = albedo[..., :3] * SIGN * w[..., None] * a[..., None]
    g[..., 3] = (a & (g[..., :3].max(-1) > 1.5)) * 255
    return g


# ---- what is made from the frames (in his own colours, before the light)
WAIST = 50                      # (the sash's top row: his breath lifts what is above it a pixel)
ARM = dict(cut=33, cols=(28, 37))   # (waving, his raised forearm: cut at this row, these columns; what is above goes up)
BUBBLE = (23, 35)               # (asleep: the bubble at his nose, its left edge's middle; the sheet's own bubble taken away)
LEGS = (52, 57, (13, 31))       # (his legs, the rest frame's in all: from row 57 down, and rows 52-56 outside columns 13-30, the
                                #  knees and the cuffs; above and between, his lap, where the meat and his hands are)


def classify(c):
    """each pixel's stuff, from his own colours: s skin, w white (eyes, teeth, the sheet's bubble), h hair (and dark
    lines), ' ' nothing, '.' anything else"""
    r, g, b = c[..., 0], c[..., 1], c[..., 2]; mx, mn = c[..., :3].max(-1), c[..., :3].min(-1)
    out = np.full(c.shape[:2], '.', '<U1')
    out[(r > 180) & (g > 120) & (g < 215) & (b > 80) & (b < 185) & (r - b > 45)] = 's'
    out[(mn > 175) & (mx - mn < 45)] = 'w'
    out[mx < 70] = 'h'
    out[c[..., 3] == 0] = ' '
    return out


def derive(cells):
    """rest_b (his breath), wave_2, wave_3, wave_3b (the arm stretched, rubber; the hand waving), doze without the
    sheet's bubble (street.js blows it: doze_1..3), chew_b (his jaw)"""
    r = cells['rest']; b = r.copy(); b[:WAIST - 1] = r[1:WAIST]; cells['rest_b'] = b
    w = cells['wave']; c0, c1 = ARM['cols']; cut = ARM['cut']
    for name, d in (('wave_2', STRETCH[0]), ('wave_3', STRETCH[1])):
        n = w.copy(); n[:cut, c0:c1] = 0
        n[:cut - d, c0:c1] = w[d:cut, c0:c1]
        n[cut - d:cut, c0:c1] = w[cut:cut + 1, c0:c1]               # (the forearm, drawn out)
        cells[name] = n
    n = cells['wave_3'].copy(); top = cut - STRETCH[1]
    hand = n[:top, c0:c1].copy(); n[:top, c0:c1] = 0; n[:top, c0 + 1:c1 + 1] = hand; cells['wave_3b'] = n
    d = cells['doze'].copy(); cl = classify(d)
    bx, by = BUBBLE
    for y in range(by - 4, by + 5):
        for x in range(bx - 2, min(CW, bx + 6)):
            if cl[y, x] != 'w': continue
            left = [d[y, xx].copy() for xx in range(x - 1, x - 4, -1) if cl[y, xx] == 's']
            if left and x <= bx: d[y, x] = left[0]
            else: d[y, x] = 0
    cells['doze'] = d
    cells['chew_b'] = cells['chew'].copy()
    for i in range(1, 4): cells['doze_%d' % i] = d.copy()
    r = cells['rest']                            # (his crossed legs, the same in every frame: the sheet draws them a little
    y0, y1, (xa, xb) = LEGS                      # differently each time, and a pixel that changes there would flicker)
    for n, c in cells.items():
        if n == 'rest': continue
        c[y1:] = r[y1:]; c[y0:y1, :xa] = r[y0:y1, :xa]; c[y0:y1, xb:] = r[y0:y1, xb:]


# the faces (tools/visages.py's way, his own letters): per frame the template's top left (x0, y0) in the cell and its rows.
# Before the light, what of the sheet's face is not skin (its white eyes and teeth) is skin again (clean_face); after the
# light and the grain, the marks, in his own colours (marks):
#   E an open eye (his hair's darkest)    e a shut eye (the skin, darker)    u a smile (the skin, darker and redder)
#   M an open mouth (a dark warm red)     T the teeth (the skin, paler)      O the tongue (a warm red)   . as it is
FACES = {
    'rest':   ((17, 31), ['......', '.E..E.', '......', '..uu..']),
    'rest_b': ((17, 30), ['......', '.E..E.', '......', '..uu..']),
    'lift':   ((16, 31), ['......', '.E..E.']),
    'bite':   ((17, 31), ['......', '.E..E.', '......', '.MM...']),
    'chew':   ((17, 31), ['......', '.e..e.', '......', '...u..']),
    'chew_b': ((17, 31), ['......', '.e..e.', '......', '..uu..']),
    'hat':    ((16, 34), ['.......', '.......', '...u...']),
    'grin':   ((17, 30), ['.......', '.E...E.', '.......', '..TTT..', '..MOM..']),
    'wave':   ((16, 31), ['.......', '.e...e.', '.......', '..TTT..', '..MOM..']),
    'doze':   ((15, 33), ['........', '..e..e..', '........', '....u...']),
}
for _n in ('wave_2', 'wave_3', 'wave_3b'): FACES[_n] = FACES['wave']
for _i in range(1, 4): FACES['doze_%d' % _i] = FACES['doze']
ORDER = ['rest', 'rest_b', 'lift', 'bite', 'chew', 'chew_b', 'hat', 'grin', 'wave', 'wave_2', 'wave_3', 'wave_3b',
         'doze', 'doze_1', 'doze_2', 'doze_3']


def face_box(name):
    (x0, y0), rows = FACES[name]
    return x0, y0, x0 + len(rows[0]) - 1, y0 + len(rows) - 1


def clean_face(c, name):
    """before the light: in the face's box (and a pixel round it), the sheet's white (its eyes, its teeth) made skin"""
    x0, y0, x1, y1 = face_box(name); cl = classify(c)
    reg = (slice(max(0, y0 - 2), y1 + 3), slice(max(0, x0 - 1), x1 + 2))
    skin = c[reg][cl[reg] == 's']
    if not len(skin): return
    tone = np.median(skin, 0)
    for y in range(y0 - 1, y1 + 2):
        for x in range(x0 - 1, x1 + 2):
            if cl[y, x] == 'w': c[y, x, :3] = tone[:3]


def marks(c, name, alb):
    """after the light and the grain: the template's marks, in his own colours (the face's skin, his hair's darkest)"""
    (x0, y0), rows = FACES[name]
    x1, y1 = x0 + len(rows[0]) - 1, y0 + len(rows) - 1
    cl = classify(alb)
    reg = (slice(y0 - 1, y1 + 2), slice(x0 - 1, x1 + 2))
    sk = c[reg][cl[reg] == 's'][:, :3]
    if not len(sk): return
    L = sk @ LUM; mid = sk[np.argsort(L)[len(L) // 2]]
    hair = c[..., :3][(cl == 'h') & (np.arange(CH)[:, None] < y1 + 2)]
    eye = hair[np.argmin(hair @ LUM)] if len(hair) else mid * 0.3
    eye = np.maximum(eye, mid * 0.22)                              # (never black: the hair's own darkest)
    col = dict(E=eye, e=mid * np.array([0.62, 0.55, 0.62]), u=mid * np.array([0.78, 0.62, 0.64]),
               M=mid * np.array([0.42, 0.2, 0.24]), T=mid * np.array([1.08, 1.06, 1.1]), O=mid * np.array([0.8, 0.36, 0.36]))
    for i, row in enumerate(rows):
        for j, ch in enumerate(row):
            if ch in col and c[y0 + i, x0 + j, 3] > 0: c[y0 + i, x0 + j, :3] = np.clip(col[ch], 0, 255)


def bubble(c, size):
    """asleep: the bubble at his nose, size 1..3 (thin water, the dusk through it, its rim a little lighter, a glint)"""
    bx, by = BUBBLE
    shapes = {1: ['##'], 2: ['.#.', '###', '.#.'], 3: ['.##.', '####', '####', '.##.']}
    sh = shapes[size]; h = len(sh)
    base = np.array([96.0, 98.0, 132.0])
    for i, row in enumerate(sh):
        for j, ch in enumerate(row):
            if ch != '#': continue
            y, x = by - h // 2 + i, bx + j
            edge = i in (0, h - 1) or j in (0, len(row) - 1) or row[j - 1] != '#' or (j + 1 < len(row) and row[j + 1] != '#')
            c[y, x, :3] = base * (1.25 if edge else 1.0); c[y, x, 3] = 255 if edge else 170
    if size >= 2:
        y, x = by - h // 2 + (1 if size == 3 else 0), bx + 1; c[y, x, :3] = [168.0, 170.0, 196.0]; c[y, x, 3] = 255


def build():
    F = frames()
    k = H / (F['rest']['bot'] + 1 - np.nonzero(F['rest']['m'].any(1))[0][0])
    cells = {n: reduce(F[n], k) for n in NAMES}
    derive(cells)
    alb = {}
    for n in ORDER:
        clean_face(cells[n], n); alb[n] = cells[n].copy()
    N = len(ORDER)
    atlas = np.zeros((CH, CW * N, 4)); glow = np.zeros((CH, CW * N, 4))
    for i, n in enumerate(ORDER):
        atlas[:, i * CW:(i + 1) * CW] = light(cells[n]); glow[:, i * CW:(i + 1) * CW] = sign_glow(cells[n], alb[n])
    items = [dict(a=atlas, box=(i * CW, 0, CW, CH), anchor=(AX, AY), seq=('luffy', i), **{'with': [glow]}) for i in range(N)]
    P = dict(RG.DEF); P.update(families=FAMILIES, stray=STRAY)
    info = RG.regrain_group(items, P, 'luffy')
    for i, n in enumerate(ORDER):
        c = atlas[:, i * CW:(i + 1) * CW]; marks(c, n, alb[n])
        if n.startswith('doze_'): bubble(c, int(n[-1]))
    out = np.concatenate([atlas, glow], 0)
    out[..., :3][out[..., 3] == 0] = 0
    print('scale', round(k, 4), 'families', info['families'], 'frames', N)
    return out


def main():
    prev = sys.argv[sys.argv.index('--preview') + 1] if '--preview' in sys.argv else None
    out = build(); N = len(ORDER)
    if prev:
        os.makedirs(prev, exist_ok=True)
        bg = np.array([40.0, 32.0, 56.0]); al = out[..., 3:4] / 255
        Image.fromarray(np.uint8(out[..., :3] * al + bg * (1 - al))).resize((out.shape[1] * 8, out.shape[0] * 8), Image.NEAREST).save(os.path.join(prev, 'atlas_x8.png'))
        st = np.asarray(Image.open(os.path.join(ROOT, 'assets', 'layer_city_off.webp')).convert('RGBA')).astype(float)
        for n in ('rest', 'grin', 'wave_3', 'doze_3'):
            i = ORDER.index(n); c = out[:CH, i * CW:(i + 1) * CW]; g = out[CH:, i * CW:(i + 1) * CW]; x0, y0 = SEAT[0] - AX, SEAT[1] - AY
            crop = st[y0 - 10:y0 + CH + 30, x0 - 30:x0 + CW + 30].copy()
            sky = np.array([98.0, 72.0, 100.0]); A = crop[..., 3:4] / 255
            crop[..., :3] = crop[..., :3] * A + sky * (1 - A)
            sub = crop[10:10 + CH, 30:30 + CW]; al = c[..., 3:4] / 255
            sub[..., :3] = c[..., :3] * al + sub[..., :3] * (1 - al) + g[..., :3] * (g[..., 3:4] / 255)
            Image.fromarray(np.uint8(np.clip(crop[..., :3], 0, 255))).resize((crop.shape[1] * 6, crop.shape[0] * 6), Image.NEAREST).save(os.path.join(prev, f'street_{n}_x6.png'))
        return
    Image.fromarray(np.round(out).astype(np.uint8), 'RGBA').save(OUT, 'WEBP', lossless=True, quality=100, method=6, exact=True)
    js = open(JS, encoding='utf-8').read()
    line = 'const LFO = ' + json.dumps(dict(cell=[CW, CH], seat=list(SEAT), anchor=[AX, AY], names=ORDER), separators=(',', ':')) + ';'
    js2, n = re.subn(r'const LFO = \{.*?\};', lambda m: line, js, count=1)
    if n: open(JS, 'w', encoding='utf-8').write(js2)
    print('wrote', OUT, '| street.js LFO', 'updated' if n else 'NOT FOUND')


if __name__ == '__main__':
    main()
