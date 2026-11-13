#!/usr/bin/env python3
"""Luffy (One Piece) on the oden's roof sign: the fourth of the four heroes, sat cross-legged on the box sign おでん over the
shop (a nod to Wano's Kozuki Oden), a meat on the bone in his hands, in the rain, under the dusk and the sign's red light.

    python3 tools/luffy_oden.py                 (reads tools/src/luffy_oden_sheet.webp; writes assets/luffy_oden.webp and,
                                                 in assets/street.js, the line LFO; again: the same bytes)
    python3 tools/luffy_oden.py --preview DIR   (previews only: the atlas x8, frames on the street x6)

The sheet (a draft drawn for this, on white, eight frames of the same seated figure: at rest, the meat lifted to his mouth,
a bite, chewing, a hand on his hat, a grin, waving, asleep with a bubble at his nose) is cut from the white, each frame
whole (its small white holes, the teeth and the eyes, filled; the gaps between an arm and the body left open), and the
frames registered on their crossed legs: the soles' lowest row and the middle of the legs. The sheet draws the legs a
little differently each time; reduced, the rest frame's legs are laid in all the others (LEGS: under his lap), so nothing
flickers there from one frame to the next (and the grain's families are kept from a frame to the next: TEMPO).

His size, the street's: the sign stands on the oden's eave, its three kana about 0.28 m each (14 px): 51 px a metre.
Luffy is 1.74 m; cross-legged, from the top of his hat to his soles, 0.98 m: H px. Each frame is boxed down to that scale
with one factor for all (the rest frame's height), each pixel the part of the sheet it covers (an exact box), full from
half covered, its colour the mean of the sheet's pixels nearest their median inside the figure (three pixels in from its
edge: the sheet's dark outline does not come down with it).

Sat ON the sign (SEAT, EDGE): seen from below, the box's near top edge hides what rests on its top: his seat and the backs
of his crossed legs go down behind that edge (his pixels under it, over the sign's span, are the sign's), pressed on it;
the edge runs down to the right (it recedes), so his lap and legs lean with it (SHEAR: a part of its slope, nothing at his
waist, all of it at his soles); his right sandal hangs over the front of the box (in front of it: HANG); his shadow on the
box's lit rim under him (CONTACT).

His stuff, read on his own colours (stuff): the hat's straw, its band, his hair, skin, the vest, the sash, the shorts,
the fur of their cuffs, the sandals, the meat, its bone. What the reduction cannot carry is drawn on them (detail): the
straw's weave (a lighter and a darker step in a diagonal), the band one clean red line round the crown, the vest's two
buttons, the meat's sheen on its top.

His light, the street's at that place (R2, R12): his picture is the dusk alone, as the power cut leaves it (the base row).
A surface's facing from his silhouette (normals: his outline's smoothed slope at the edge, square to us inside): the
night's ambient on what faces us (AMB), the zenith's violet on what faces up (TOP), the sunset's terracotta on what faces
the far end of the street, his right, a thin rim (RIM), his undersides a step darker (UNDER); no outline (an edge pixel
never darker than the one it covers by OUTLINE_DL). The sign's light (the second row, added by street.js with the sign's
level, the shop's hours and its power, red in the red night): what faces down and toward the street from his soles up, the
most at his knees, the sandal over the box, the meat in his lap, a little under his chin (SIGN, GLOW). Then the
painter's grain (tools/regrain.py: FAMILIES families of tones for all his frames together, a fine grain baked in).

His face, drawn by hand (tools/visages.py's way: at 9 px of head a reduced face is a smudge), after the light and the
grain, on the face that each frame shows (face_box: his skin under his hair), per frame (FACES): the eyes a pixel each of
his hair's darkest, never black, the scar under his left eye, the grin's teeth and its dark, a smile, shut eyes. Made from
the frames: rest_b (his breath), chew_b (his jaw), asleep with a bubble at his nose in three sizes (doze_1..3), the wave
stretched, rubber (wave_2, wave_3: STRETCH px more of his forearm; wave_3b: the hand a pixel aside). The atlas: a column a
frame (ORDER), the base row over the light's. Needs Pillow, numpy, scipy.
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
H = 50                          # cross-legged, the top of his hat to his soles (0.98 m at 51 px a metre)
CW, CH = 56, 92                 # a cell; his anchor at (AX, AY): the middle of his crossed legs, the soles' lowest row
AX, AY = 28, 85
INK = 40                        # (what is the figure: this far from white, 0..765)
HOLE = 900                      # (white holes inside him smaller than this, px of the sheet: teeth, eyes, filled)
SEAT = (490, 492)               # in the street: his anchor, pressed on the sign's top edge
EDGE = ((475, 484), (506, 498))  # the sign's near top edge (its two ends, measured on the layers: the same lit, off, unlit)
SHEAR = 0.8                     # (the part of the edge's slope his lap and legs lean with)
WAIST = 66                      # (the sash's top row: above it nothing leans; his breath lifts what is above it a pixel)
LEGS = (70, 76, (17, 41))       # (his legs, the rest frame's in all: from row 76 down, and rows 70-75 outside these columns)
HANG = (34, 45, 79)             # (his right sandal hanging over the box's front: its columns, from this row down, before the lean)
HANG_D = 1                      # (how far it hangs)
CONTACT = 0.5                   # (his shadow on the box's rim under him: the rim's light kept)
AMB = np.array([0.44, 0.38, 0.52])        # the night's ambient on what faces us
TOP = np.array([34.0, 28.0, 52.0])        # the zenith's violet on what faces up (added, times his own colour + 60, / 255)
RIM = np.array([88.0, 46.0, 34.0])        # the sunset's terracotta on what faces his right (the same, a thin rim)
UNDER = 0.72                              # his undersides: this much of their light
OUTLINE_DL = 6
SIGN = np.array([0.55, 0.14, 0.07])       # the sign's light on him (its red), times his own colour
GLOW = (3, 22, 0.12)                      # full up to this many rows over his soles, down to its last share at the second
FAMILIES = 26
STRETCH = (10, 20)
STRAY = 6
TEMPO_GRAIN = dict(grain_k=0.12, dither=0.9)


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
        F[name] = dict(m=mm, rgb=rgb[y0:y1, x0:x1], bot=ys.max() + int(hh * 0.8), cx=(xs.min() + xs.max()) / 2)
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
    """a frame at scale k in its cell: RGBA, his anchor at (AX, AY)"""
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


# ---- his stuff, read on his own colours
def stuff(c):
    """each pixel's stuff: H hat (straw), B its band, K hair (and dark lines), S skin, V vest, Y sash, P shorts, F fur
    (the cuffs, and the bone), D sandals, M meat, W white (eyes, teeth, the sheet's bubble), ' ' nothing, '.' else"""
    r, g, b = c[..., 0], c[..., 1], c[..., 2]; mx, mn = c[..., :3].max(-1), c[..., :3].min(-1)
    a = c[..., 3] > 0
    ys = np.nonzero(a.any(1))[0]; top = ys.min() if len(ys) else 0
    head = (np.arange(CH) < top + 16)[:, None]
    out = np.full(c.shape[:2], '.', '<U1')
    red = (r > 140) & (g < 90) & (b < 100) & (r - g > 70)
    out[(r > 150) & (g > 105) & (b < 125) & (r - b > 55) & ~red] = 'H'
    out[red & head] = 'B'; out[red & ~head] = 'V'
    out[(r > 200) & (g > 160) & (b < 110) & ~head] = 'Y'
    out[(b > 100) & (b > r + 20) & (mx > 80)] = 'P'
    out[(mn > 150) & (mx - mn < 60)] = 'F'
    out[(r > 180) & (g > 120) & (g < 215) & (b > 80) & (b < 185) & (r - b > 45)] = 'S'
    out[(r > 110) & (g > 45) & (g < 125) & (b < 95) & (r - g > 45) & (r - b > 60) & ~head] = 'M'
    out[(mn > 185) & (mx - mn < 40) & head] = 'W'
    out[(mx < 72)] = 'K'
    out[(mx >= 72) & (mx < 130) & (r > b) & (g > b) & ~head & (np.arange(CH)[:, None] > AY - 8)] = 'D'
    out[~a] = ' '
    return out


def face_box(c):
    """the face it shows: its skin under his hair, in the head's rows (x0, y0, x1, y1, edges included), or None"""
    st = stuff(c); a = c[..., 3] > 0
    ys = np.nonzero(a.any(1))[0]; top = ys.min()
    reg = np.zeros_like(a); reg[top + 4:top + 17] = True
    sk = (st == 'S') & reg
    lab, n = nd.label(sk)
    if not n: return None
    sizes = nd.sum(sk, lab, range(1, n + 1)); big = lab == (np.argmax(sizes) + 1)
    yy, xx = np.nonzero(big)
    return int(xx.min()), int(yy.min()), int(xx.max()), int(yy.max())


# ---- what is made from the frames (in his own colours, before the light)
def derive(cells):
    """rest_b (his breath), the wave stretched (wave_2, wave_3) and waving (wave_3b), doze without the sheet's bubble
    (street.js blows it: doze_1..3), chew_b (his jaw); the rest frame's legs in all"""
    r = cells['rest']; b = r.copy(); b[:WAIST - 1] = r[1:WAIST]; cells['rest_b'] = b
    w = cells['wave']; a = w[..., 3] > 0
    top = np.nonzero(a.any(1))[0].min()
    c0 = AX + 8                                  # (his raised forearm: right of his head, between the hand and the shoulder)
    widths = [(y, np.count_nonzero(a[y, c0:])) for y in range(top + 6, top + 16)]
    cut = min(widths, key=lambda t: (t[1] if t[1] else 99, -t[0]))[0]
    for name, d in (('wave_2', STRETCH[0]), ('wave_3', STRETCH[1])):
        n = w.copy(); n[:cut, c0:] = 0
        n[:cut - d, c0:] = w[d:cut, c0:]
        n[cut - d:cut, c0:] = w[cut:cut + 1, c0:]              # (the forearm, drawn out)
        cells[name] = n
    n = cells['wave_3'].copy(); ht = cut - STRETCH[1] - 1
    hand = n[:ht, c0:CW - 1].copy(); n[:ht, c0:] = 0; n[:ht, c0 + 1:] = hand; cells['wave_3b'] = n
    d = cells['doze'].copy(); st = stuff(d); fb = face_box(d)
    if fb:
        for y, x in zip(*np.nonzero(st == 'W')):
            if x > fb[2] - 1:
                left = [d[y, xx].copy() for xx in range(x - 1, x - 4, -1) if st[y, xx] == 'S']
                d[y, x] = left[0] if (left and x <= fb[2] + 1) else 0
    cells['doze'] = d
    cells['chew_b'] = cells['chew'].copy()
    for i in range(1, 4): cells['doze_%d' % i] = d.copy()
    y0, y1, (xa, xb) = LEGS                      # (his crossed legs, the same in every frame: the sheet draws them a
    for n, c in cells.items():                   # little differently each time, and a pixel that changes there flickers)
        if n == 'rest': continue
        c[y1:] = r[y1:]; c[y0:y1, :xa] = r[y0:y1, :xa]; c[y0:y1, xb:] = r[y0:y1, xb:]


def detail(c):
    """what the reduction cannot carry, drawn on his stuff: the straw's weave, the band's line, the vest's buttons, the
    meat's sheen"""
    st = stuff(c); out = c.copy(); h, w = st.shape
    for y, x in zip(*np.nonzero(st == 'H')):                    # the straw: a lighter and a darker step, in a diagonal weave
        k = (1.1, 1.0, 0.9, 1.0)[(x + 2 * y) % 4]
        out[y, x, :3] = np.clip(c[y, x, :3] * k, 0, 255)
    band = st == 'B'                                            # the band: one clean red line round the crown
    for y in np.unique(np.nonzero(band)[0]):
        xs = np.nonzero(band[y])[0]
        for x in range(xs.min(), xs.max() + 1):
            if st[y, x] in 'HB': out[y, x, :3] = (196.0, 32.0, 36.0)
    vest = st == 'V'                                            # the buttons: on the vest's opening, a third and two thirds down
    rows = np.nonzero(vest.any(1))[0]
    if len(rows) > 8:
        for f in (0.3, 0.6):
            y = int(rows.min() + f * (rows.max() - rows.min()))
            xs = np.nonzero(vest[y])[0]
            if len(xs) < 2: continue
            mid = (xs.min() + xs.max()) / 2
            for x in (xs[xs < mid].max() if (xs < mid).any() else None, xs[xs > mid].min() if (xs > mid).any() else None):
                if x is not None and st[y, x] == 'V' and ((x - 1 >= 0 and st[y, x - 1] == 'S') or (x + 1 < w and st[y, x + 1] == 'S')):
                    out[y, x, :3] = (236.0, 196.0, 70.0)
    meat = st == 'M'                                            # the meat's sheen: its top edge and the pixel under it
    up = meat & ~np.vstack([np.zeros((1, w), bool), meat[:-1]])
    out[up, :3] = np.clip(c[up, :3] * 1.28 + 10, 0, 255)
    up2 = meat & ~up & np.vstack([np.zeros((1, w), bool), up[:-1]])
    out[up2, :3] = np.clip(c[up2, :3] * 1.1, 0, 255)
    return out


def clean_face(c):
    """before the light: in the face's box (and a pixel round it), the sheet's white (its eyes, its teeth) made skin"""
    fb = face_box(c)
    if not fb: return
    x0, y0, x1, y1 = fb; st = stuff(c)
    reg = (slice(max(0, y0 - 1), y1 + 2), slice(max(0, x0 - 1), x1 + 2))
    skin = c[reg][st[reg] == 'S']
    tone = np.median(skin, 0)
    for y in range(y0 - 1, y1 + 2):
        for x in range(x0 - 1, x1 + 2):
            if st[y, x] == 'W': c[y, x, :3] = tone[:3]


# ---- the light
def normals(a):
    """a surface's facing from his silhouette: near his outline its smoothed slope (outward), inside square to us"""
    s = nd.gaussian_filter(a.astype(float), 1.4)
    gy, gx = np.gradient(s)
    g = np.hypot(gx, gy) + 1e-6
    m = np.clip(g * 3.2, 0, 0.96)
    nx, ny = -gx / g * m, -gy / g * m
    return nx, ny, np.sqrt(1 - m * m)


def light(c):
    """the dusk on him (the base row)"""
    a = c[..., 3] > 0
    nx, ny, nz = normals(a)
    alb = c[..., :3]
    col = alb * AMB
    top = np.clip(-ny, 0, 1)[..., None] * TOP / 255.0 * (alb + 60)
    rim = (np.clip(nx, 0, 1) ** 1.5 * (1 - nz) ** 0.7)[..., None] * RIM / 255.0 * (alb + 60)
    under = 1 - (1 - UNDER) * np.clip(ny, 0, 1)[..., None]
    out = c.copy()
    out[..., :3] = np.where(a[..., None], np.clip((col + top + rim) * under, 0, 255), 0)
    L = out[..., :3] @ LUM                                      # no dark line round him
    edge = a & ~nd.binary_erosion(a)
    for y, x in zip(*np.nonzero(edge)):
        best = None
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            yy, xx = y + dy, x + dx
            if 0 <= yy < a.shape[0] and 0 <= xx < a.shape[1] and a[yy, xx] and not edge[yy, xx]:
                if best is None or L[yy, xx] > L[best]: best = (yy, xx)
        if best and L[y, x] < L[best] - OUTLINE_DL: out[y, x, :3] = out[best][:3] * 0.94
    return out


def sign_glow(c, albedo):
    """the sign's red on him (the second row): what faces down and toward the street, the most low, a little higher up"""
    a = c[..., 3] > 0
    nx, ny, nz = normals(a)
    r = (AY - np.arange(CH))[:, None].astype(float)
    hk = np.where(r <= GLOW[0], 1.0, np.clip(1 - (r - GLOW[0]) / (GLOW[1] - GLOW[0]), GLOW[2], 1))
    face = np.clip(0.18 * nz + 0.95 * np.clip(ny, 0, 1), 0, 1)
    g = np.zeros_like(c)
    g[..., :3] = albedo[..., :3] * SIGN * (hk * face)[..., None] * a[..., None]
    g[..., 3] = (a & (g[..., :3].max(-1) > 1.5)) * 255
    return g


# ---- his seat on the sign
def edge_y(x):
    (xa, ya), (xb, yb) = EDGE
    return ya + (x - xa) * (yb - ya) / (xb - xa)


def lean(c):
    """his lap and legs leaning with the edge: each column's rows under his waist moved down by a part of the edge's slope
    at that column, nothing at the waist, all of it at his soles (nearest pixel, from the column itself)"""
    out = np.zeros_like(c); s = SHEAR * (EDGE[1][1] - EDGE[0][1]) / (EDGE[1][0] - EDGE[0][0])
    out[:WAIST] = c[:WAIST]
    for x in range(CW):
        dmax = s * (x - AX)
        for y in range(WAIST, CH):
            t = (y - WAIST) / (AY - WAIST)
            ys = int(round(y - dmax * min(1.0, max(0.0, t))))
            if WAIST <= ys < CH: out[y, x] = c[ys, x]
    return out


def seat(c, glow, hang):
    """on the sign: what of him is under its near top edge, over its span, is the sign's (cut), but the sandal that hangs
    over its front; his shadow on the box's rim under him"""
    x0, y0 = SEAT[0] - AX, SEAT[1] - AY
    a = c[..., 3] > 0
    for x in range(CW):
        sx = x0 + x + 0.5
        if not EDGE[0][0] <= sx <= EDGE[1][0] + 1: continue
        e = edge_y(sx) - y0                                     # (the edge's row in the cell)
        for y in range(CH):
            if y + 0.5 > e and not hang[y, x]: c[y, x] = 0; glow[y, x] = 0
        if a[:int(e) + 1, x].any():                             # his shadow on the rim, right under where he sits
            ye = int(np.floor(e)) + 1
            for k, f in ((0, CONTACT), (1, CONTACT + (1 - CONTACT) * 0.5)):
                if ye + k < CH and not hang[ye + k, x]: c[ye + k, x] = (0.0, 0.0, 0.0, 255 * (1 - f))


def hang(c, g):
    """his right sandal over the box's front: its pixels (HANG: columns, from a row down) HANG_D rows lower, his ankle drawn
    longer above it, in both rows (before the lean); gives its mask in the cell"""
    xa, xb, y0 = HANG; d = HANG_D
    part = (stuff(c)[y0:, xa:xb] != ' ')
    m = np.zeros(c.shape[:2], bool)
    for L in (c, g):
        old = L[y0:, xa:xb].copy(); new = L[y0:, xa:xb]
        new[part] = 0
        mv = np.zeros_like(old); mv[d:] = old[:-d]; mv[:d] = old[:1]
        pm = np.zeros_like(part); pm[d:] = part[:-d]; pm[:d] = part[:1]
        new[pm] = mv[pm]
    pm = np.zeros_like(part); pm[d:] = part[:-d]; pm[:d] = part[:1]
    m[y0:, xa:xb] = pm
    return m


# the faces: per frame what it shows (in the face's box, edges included: x0..x1, y0..y1), in its rows' fractions:
#   eyes: 'open' | 'shut' | None (under his hat's brim, or the meat), the row's fraction; mouth: 'smile' | 'grin' | 'laugh' |
#   'bite' | 'puff' | None; scar: under his left eye (our right) when his eyes show
FACES = {'rest': ('open', 0.38, 'smile'), 'rest_b': ('open', 0.38, 'smile'), 'lift': ('open', 0.38, None),
         'bite': ('open', 0.38, 'bite'), 'chew': ('shut', 0.4, 'puff'), 'chew_b': ('shut', 0.4, 'smile'),
         'hat': (None, 0.4, 'smile'), 'grin': ('open', 0.32, 'grin'), 'wave': ('shut', 0.34, 'laugh'),
         'doze': ('shut', 0.45, None)}
for _n in ('wave_2', 'wave_3', 'wave_3b'): FACES[_n] = FACES['wave']
for _i in range(1, 4): FACES['doze_%d' % _i] = FACES['doze']
ORDER = ['rest', 'rest_b', 'lift', 'bite', 'chew', 'chew_b', 'hat', 'grin', 'wave', 'wave_2', 'wave_3', 'wave_3b',
         'doze', 'doze_1', 'doze_2', 'doze_3']


def marks(c, name, fb):
    """after the light and the grain: his face, in his own colours (the face's skin, his hair's darkest)"""
    if not fb: return
    x0, y0, x1, y1 = fb; eyes, fy, mouth = FACES[name]
    a = c[..., 3] > 0
    reg = c[y0:y1 + 1, x0:x1 + 1, :3][a[y0:y1 + 1, x0:x1 + 1]]
    L = reg @ LUM; mid = reg[np.argsort(L)[len(L) // 2]]
    dark = c[max(0, y0 - 8):y0 + 2, x0 - 2:x1 + 3, :3].reshape(-1, 3)
    dark = dark[(dark @ LUM) > 1]
    eye = np.maximum(dark[np.argmin(dark @ LUM)], mid * 0.2) if len(dark) else mid * 0.3
    col = dict(E=eye, e=mid * np.array([0.6, 0.52, 0.6]), u=mid * np.array([0.74, 0.58, 0.6]),
               M=mid * np.array([0.38, 0.17, 0.2]), T=mid * np.array([1.12, 1.1, 1.14]), O=mid * np.array([0.82, 0.36, 0.36]),
               c=mid * np.array([0.84, 0.66, 0.66]))
    w = x1 - x0 + 1; hh = y1 - y0 + 1
    cx = (x0 + x1) / 2
    ey = y0 + int(round(fy * (hh - 1)))
    ex = (int(round(cx - w * 0.24)), int(round(cx + w * 0.24)))
    put = lambda x, y, k: a[y, x] and c.__setitem__((y, x, slice(0, 3)), np.clip(col[k], 0, 255))
    if eyes == 'open':
        for x in ex: put(x, ey, 'E')
        put(ex[1] + 1, ey + 1, 'c'); put(ex[1], ey + 2, 'c')               # (the scar under his left eye)
    elif eyes == 'shut':
        for x in ex: put(x, ey, 'e'); put(x - 1, ey, 'e')
    my = min(y1, ey + max(3, int(round(hh * 0.42))))
    mx = int(round(cx))
    if mouth == 'smile': put(mx - 1, my, 'u'); put(mx, my, 'u')
    elif mouth == 'puff': put(mx, my, 'u'); put(x0, my - 1, 'c'); put(x1, my - 1, 'c')
    elif mouth == 'bite': put(mx - 1, my, 'M'); put(mx, my, 'M'); put(mx - 1, my - 1, 'T')
    elif mouth in ('grin', 'laugh'):
        for x in range(mx - 2, mx + 2): put(x, my - 1, 'T'); put(x, my, 'M')
        put(mx - 1, my + 1, 'O') if my + 1 <= y1 + 1 else None


def bubble(c, glow, size, fb):
    """asleep: the bubble at his nose, size 1..3 (thin water, the dusk through it, its rim a little lighter, a glint)"""
    x0, y0, x1, y1 = fb
    bx, by = x1 + 1, y0 + int(round(0.62 * (y1 - y0)))
    shapes = {1: ['##'], 2: ['.#.', '###', '.#.'], 3: ['.##.', '####', '####', '.##.']}
    sh = shapes[size]; h = len(sh)
    base = np.array([108.0, 110.0, 146.0])
    for i, row in enumerate(sh):
        for j, ch in enumerate(row):
            if ch != '#': continue
            y, x = by - h // 2 + i, bx + j
            edge = i in (0, h - 1) or j in (0, len(row) - 1) or row[j - 1] != '#' or (j + 1 < len(row) and row[j + 1] != '#')
            c[y, x, :3] = base * (1.22 if edge else 1.0); c[y, x, 3] = 255 if edge else 165
            glow[y, x] = (14.0, 4.0, 3.0, 255.0)                     # (the sign's red in it)
    if size >= 2:
        y, x = by - h // 2 + (1 if size == 3 else 0), bx + 1; c[y, x, :3] = (186.0, 188.0, 214.0); c[y, x, 3] = 255


def build():
    F = frames()
    k = H / (F['rest']['bot'] + 1 - np.nonzero(F['rest']['m'].any(1))[0][0])
    cells = {n: reduce(F[n], k) for n in NAMES}
    derive(cells)
    alb, fbs = {}, {}
    for n in ORDER:
        fbs[n] = face_box(cells[n]); clean_face(cells[n]); cells[n] = detail(cells[n]); alb[n] = cells[n].copy()
    N = len(ORDER)
    atlas = np.zeros((CH, CW * N, 4)); glow = np.zeros((CH, CW * N, 4))
    for i, n in enumerate(ORDER):
        atlas[:, i * CW:(i + 1) * CW] = light(cells[n]); glow[:, i * CW:(i + 1) * CW] = sign_glow(cells[n], alb[n])
    items = [dict(a=atlas, box=(i * CW, 0, CW, CH), anchor=(AX, AY), seq=('luffy', i), **{'with': [glow]}) for i in range(N)]
    P = dict(RG.DEF); P.update(families=FAMILIES, stray=STRAY, **TEMPO_GRAIN)
    info = RG.regrain_group(items, P, 'luffy')
    for i, n in enumerate(ORDER):
        sl = slice(i * CW, (i + 1) * CW)
        c, g = atlas[:, sl].copy(), glow[:, sl].copy()
        marks(c, n, fbs[n])
        if n.startswith('doze_') and fbs[n]: bubble(c, g, int(n[-1]), fbs[n])
        hm = hang(c, g)
        c, g, hm = lean(c), lean(g), lean(np.repeat(hm[..., None].astype(float), 4, -1))[..., 0] > 0.5
        seat(c, g, hm)
        atlas[:, sl], glow[:, sl] = c, g
    out = np.concatenate([atlas, glow], 0)
    out[..., :3][out[..., 3] == 0] = 0
    print('scale', round(k, 4), 'families', info['families'], 'frames', N)
    return out


def main():
    prev = sys.argv[sys.argv.index('--preview') + 1] if '--preview' in sys.argv else None
    out = build()
    if prev:
        os.makedirs(prev, exist_ok=True)
        bg = np.array([40.0, 32.0, 56.0]); al = out[..., 3:4] / 255
        Image.fromarray(np.uint8(out[..., :3] * al + bg * (1 - al))).resize((out.shape[1] * 8, out.shape[0] * 8), Image.NEAREST).save(os.path.join(prev, 'atlas_x8.png'))
        return
    Image.fromarray(np.round(out).astype(np.uint8), 'RGBA').save(OUT, 'WEBP', lossless=True, quality=100, method=6, exact=True)
    js = open(JS, encoding='utf-8').read()
    line = 'const LFO = ' + json.dumps(dict(cell=[CW, CH], seat=list(SEAT), anchor=[AX, AY], names=ORDER), separators=(',', ':')) + ';'
    js2, n = re.subn(r'const LFO = \{.*?\};', lambda m: line, js, count=1)
    if n: open(JS, 'w', encoding='utf-8').write(js2)
    print('wrote', OUT, '| street.js LFO', 'updated' if n else 'NOT FOUND')


if __name__ == '__main__':
    main()
