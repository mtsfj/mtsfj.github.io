#!/usr/bin/env python3
"""The far crossing: now and then a passer-by under an umbrella crosses the street's end on its zebra crossing.

    python3 tools/crossing_walker.py                 (writes assets/crossing_walker.webp and, in assets/street.js, the line
                                                      XWS: it can be run again, it writes the same bytes)
    python3 tools/crossing_walker.py --preview DIR   (only shows it: the atlas x6, the walk on the crossing, XWS in json)
    python3 tools/crossing_walker.py --input         (writes the image model's inputs: tools/src/edits/xwalk_in.webp, the
                                                      pose guide, xwalk_ctx.webp, the street round the crossing, and
                                                      xwalk2_in.webp, the second guide, from the first answer)
    python3 tools/crossing_walker.py --ask           (asks the image model: xwalk_prompt.txt with xwalk_in.webp, xwalk_ctx.webp
                                                      and study_walk_model.webp; its answer xwalk_model.webp; about 0.27 $)
    python3 tools/crossing_walker.py --ask2          (the second: xwalk2_prompt.txt with xwalk2_in.webp and xwalk_model.webp;
                                                      its answer xwalk2_model.webp, the frames used; about 0.25 $)

Who: an ordinary man of the street on his way home in the rain, a salaryman in a belted beige trench coat over a dark suit,
a black umbrella over his head, a black briefcase in his near hand, black leather shoes. His first sheet (xwalk_model.webp,
R28): eight frames of a walk seen from the side, walking to the right, painted over the eight grey mannequins of a pose
guide (xwalk_in.webp, drawn here) in the street's style (xwalk_ctx.webp, the street round the crossing at 22 h; the walk of
the owner's study, its style only): the man right, his steps not (its passing pose twice, its "up" a second contact: the
planted foot would have stood still a frame, then leapt 13 px). His second sheet (xwalk2_model.webp): the first's man kept
above his coat's hem, his legs repainted over mannequin legs drawn from a walk's kinematics (xwalk2_in.webp: guide2), each
frame a step on; its steps measured (steps: 2 to 8 px a frame, 37 px the cycle).

Where (the street's camera, model B: tools/zombie_sol.py, F 959.5 px, the eye 1.41 m over the road, the horizon at 615, the
sidewalks 0.15 m up): the zebra crossing at the street's end, past the 止まれ marking, its stripes 45 cm wide every 90 cm
(measured: 35.5 px a period on their middle row 669.5, B's 38.4 px a metre there: the stripes are B exactly, as
zombie_sol.py found; the railing behind, 0.86 of B, is the painting's own and no measure). He walks from the cross street's
near sidewalk on one side, behind the corner of the oden's block (x 504) or the Pokemon Center's (x 866-870: BUS.occ, the
TranZit's), across on the stripes (their middle at the near kerb, their far half at the other), to the other side and
behind the other corner: a straight line on the ground (PATH, X across and D deep in metres, 17 degrees off the cross
street: from 24 m behind the oden's corner (X -5, D 23.7) to 27.1 m as he passes behind the Center's (X 4.62, D 26.9):
never inside a building, never off the stripes' far edge (27.06 m) in the middle). His height in px is the street's
figures': K x B (SOL.k 1.1, the bus, the machines and the doors), 1.72 m where he crosses the street's middle (D 25.6):
70.9 px; one scale for every frame (from the first corner to the second he would go from 74 to 67 px: four pixels at most
off). Down the kerb (X -2.8 m) and up the other (X 2.8): his soles from the sidewalk's row to the road's and back, over
half a step (street.js).

His light: as graded as the far end round him at 22 h (VALUES: the city behind him L* 22, the walls 8-20, the road 13; he is
a little darker than the city's glow, his face under the umbrella darker still), a soft night light from above (the sky,
the umbrella's shade on his face and shoulders), his tones in FAMILIES families with a fine grain, no outline; on each pixel
the share of three lights that street.js weighs by their sources (the masks, the atlas's second layer): R, the edges facing
the Center (right, a little up: its shop's warm white and its awning's red), G, the edges facing the oden (left: its warm
orange), B, the edges facing up (the umbrella's top, his shoulders: the lamp and the sky); his cell mirrored, R and G swap.

Needs Pillow, numpy, scipy (and tools/ichiraku_figures.py, tools/ichiraku_interior.py, tools/owner_study.py).
"""
import base64
import io
import json
import math
import os
import re
import sys
import urllib.request
import numpy as np
from PIL import Image, ImageDraw

sys.dont_write_bytecode = True
ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
ROOT = os.path.dirname(ICI)
EDITS = os.path.join(ICI, 'src', 'edits')
OUT = os.path.join(ROOT, 'assets', 'crossing_walker.webp')
JS = os.path.join(ROOT, 'assets', 'street.js')
MODEL = 'openai/gpt-5.4-image-2'

# ---- the street's camera (model B) and the walk's place ----
CF, CEYE, CHZ, TR, SOLK = 959.5, 1.41, 615.0, 0.15, 1.1
H_M = 1.72                                       # his height (m, soles to the top of his head)
D_MID = 25.6                                     # his size's depth (m): where he crosses the street's middle
PATH = ((-5.6, 23.93), (8.0, 28.01))             # his line on the ground: (X, D) behind the oden's corner, past the Center's
KERB = 2.8                                       # the kerbs' faces (|X|, m)


def row(D, G=0.0):
    return CHZ + CF * (CEYE - G) / D


def col(X, D):
    return 700.0 + CF * X / D


# ---- the pose guide: eight grey mannequins on a flat green, a walk cycle seen from the side to the right, his near limbs
# light grey, his far ones dark grey; the umbrella in his near hand over his head, the briefcase in his far hand. Its angles
# (degrees: the thigh from the vertical, forward +; the knee's bend; the foot from the level, toes up +) for the near leg in
# the cycle's eight frames (contact, down, passing, up, then the far leg's four): the far leg is the near one four frames on ----
GW, GH, GC, GR = 1024, 1024, 4, 2                # the guide (the model answers 1024 x 1024): 4 x 2 cells of 256 x 512
GPX = 192.0                                      # guide px a metre: 1.72 m is 330 px
GBASE = 470                                      # the soles' row in each cell
LEG = [(24, 2, 14), (14, 18, 0), (2, 5, 0), (-13, 4, -4), (-21, 8, -26), (-16, 40, -38), (8, 62, -12), (22, 34, 4)]
ARM_SWING = [-10, -6, 0, 6, 10, 6, 0, -6]       # the far arm (with the briefcase): against the far leg (degrees, forward +)
BOB = 0.0                                        # (the pelvis's height comes from the legs: the lower sole on the baseline)
G_GREEN, G_NEAR, G_FAR, G_BODY = (0, 177, 64), (200, 200, 206), (78, 78, 86), (150, 150, 158)
G_SKIN, G_HAIR, G_UMB, G_SHAFT, G_BAG = (226, 186, 160), (40, 34, 30), (34, 36, 44), (150, 150, 150), (70, 46, 34)
THIGH, SHIN, ANKLE, HEEL, TOE = 0.45, 0.44, 0.075, 0.06, 0.20


def leg_points(hip, th, kn, ft):
    a = math.radians(th); s = math.radians(th - kn)
    knee = (hip[0] + THIGH * math.sin(a), hip[1] - THIGH * math.cos(a))
    ank = (knee[0] + SHIN * math.sin(s), knee[1] - SHIN * math.cos(s))
    f = math.radians(ft)
    heel = (ank[0] - HEEL * math.cos(f), ank[1] - ANKLE - HEEL * math.sin(f))
    toe = (ank[0] + TOE * math.cos(f), ank[1] - ANKLE + TOE * math.sin(f))
    return knee, ank, heel, toe


def guide():
    im = Image.new('RGB', (GW, GH), G_GREEN); g = ImageDraw.Draw(im)
    cw, ch = GW // GC, GH // GR
    for i in range(8):
        cx0, cy0 = (i % GC) * cw, (i // GC) * ch
        near, far = LEG[i], LEG[(i + 4) % 8]
        # the pelvis's height: the lower sole of the two on the ground (y = 0)
        lows = []
        for th, kn, ft in (near, far):
            _, _, heel, toe = leg_points((0.0, 0.0), th, kn, ft); lows.append(min(heel[1], toe[1]))
        hip = (0.0, -min(lows))
        P = lambda p: (cx0 + cw * 0.42 + p[0] * GPX, cy0 + GBASE - p[1] * GPX)

        def limb(a, b, w, col_):
            g.line([P(a), P(b)], fill=col_, width=int(w * GPX))
            for q in (a, b):
                x, y = P(q); r = w * GPX / 2; g.ellipse([x - r, y - r, x + r, y + r], fill=col_)

        def leg(L, col_):
            knee, ank, heel, toe = leg_points(hip, *L)
            limb(hip, knee, 0.15, col_); limb(knee, ank, 0.115, col_)
            g.polygon([P((ank[0] - 0.04, ank[1] + 0.02)), P(heel), P(toe), P((ank[0] + 0.07, ank[1] - 0.02))], fill=col_)
        sh = (hip[0] + 0.05, hip[1] + 0.50)       # the shoulder (the torso leans forward a little: the rain)
        # the far arm and the briefcase, behind him
        a = math.radians(ARM_SWING[i]); elb = (sh[0] + 0.30 * math.sin(a), sh[1] - 0.30 * math.cos(a))
        hand = (elb[0] + 0.27 * math.sin(a + 0.15), elb[1] - 0.27 * math.cos(a + 0.15))
        limb(sh, elb, 0.085, G_FAR); limb(elb, hand, 0.075, G_FAR)
        bx, by = hand[0], hand[1] - 0.04
        g.rectangle([P((bx - 0.21, by)), P((bx + 0.21, by - 0.30))], fill=G_BAG)
        limb((bx - 0.05, by + 0.03), (bx + 0.05, by + 0.03), 0.03, G_BAG)
        leg(far, G_FAR)
        # the torso, the neck, the head (his face to the right), lit grey
        t0, t1 = (hip[0] - 0.12, hip[1] + 0.04), (hip[0] + 0.12, hip[1] + 0.04)
        g.polygon([P(t0), P(t1), P((sh[0] + 0.13, sh[1] - 0.02)), P((sh[0] + 0.06, sh[1] + 0.05)), P((sh[0] - 0.10, sh[1] + 0.05)), P((sh[0] - 0.14, sh[1] - 0.04))], fill=G_BODY)
        nk = (sh[0] + 0.03, sh[1] + 0.06); limb(nk, (nk[0] + 0.01, nk[1] + 0.09), 0.10, G_SKIN)
        hc = (sh[0] + 0.05, sh[1] + 0.25); r = 0.105 * GPX; x, y = P(hc)
        g.ellipse([x - r, y - r * 1.1, x + r, y + r * 1.1], fill=G_SKIN)
        g.chord([x - r, y - r * 1.1, x + r, y + r * 1.1], 160, 360, fill=G_HAIR)
        g.pieslice([x - r, y - r * 1.1, x + r, y + r * 1.1], 90, 200, fill=G_HAIR)
        leg(near, G_NEAR)
        # the near arm holding the umbrella: the upper arm down, the forearm forward and up, the hand before his chest
        elb = (sh[0] + 0.05, sh[1] - 0.27); hand = (sh[0] + 0.24, sh[1] - 0.17)
        top = (hand[0] - 0.05, hip[1] + 1.22)     # the shaft's top (the canopy's apex), leaning back over his head
        limb(hand, (hand[0] + 0.012, hand[1] - 0.12), 0.022, G_SHAFT)
        limb(hand, top, 0.018, G_SHAFT)
        R_ = 0.50; rim_y = top[1] - 0.24          # the canopy: a dome, its scalloped rim, a little tilted forward
        pts = []
        for k in range(41):
            u = -1 + 2 * k / 40; xx = top[0] + R_ * u; yy = rim_y + 0.24 * math.sqrt(max(0, 1 - u * u)) ** 0.8
            pts.append(P((xx, yy)))
        for k in range(8, -1, -1):
            u = -1 + 2 * k / 8; xx = top[0] + R_ * u
            pts.append(P((xx, rim_y + (0.0 if k % 2 == 0 else 0.03))))
        g.polygon(pts, fill=G_UMB)
        limb(top, (top[0], top[1] + 0.05), 0.02, G_SHAFT)
        limb(sh, elb, 0.09, G_NEAR); limb(elb, hand, 0.08, G_NEAR)
        x, y = P(hand); r = 0.045 * GPX; g.ellipse([x - r, y - r, x + r, y + r], fill=G_SKIN)
    return im


# ---- the second guide (xwalk2_in.webp): the first answer's man kept above his coat's hem (each frame's upper body, set on one
# column and raised or lowered by his step's bob) and the briefcase in his near hand, his legs below as grey mannequin legs
# from a walk's kinematics: the hips at an even pace, each foot on the ground 60 % of the cycle (moving back under him by the
# stride's eighth each frame: every frame a step on, no two alike, the planted foot on its place), lifted and swung forward
# the other 40 %; the hips as high as the bearing leg lets them (nearly straight: the bob); his near leg light, his far one
# dark. The first answer's poses came in uneven steps (its passing frame twice, its "up" a contact): the body would have
# stood, then leapt 13 px ----
S2 = 171.0                                       # (the first answer's px a metre: 294 px for 1.72 m)
STRIDE2 = 1.2                                    # the stride (m): two steps of 0.6 m
L_TH, L_SH, L_AN, L_HE, L_TO = 0.42, 0.415, 0.075, 0.06, 0.19
ANCH2 = 118                                      # (his torso's column in each cell)
SOLE2 = 398                                      # (his soles' row in each cell)


def alpha_key(a):
    """a cell off its green: each pixel's share of the figure from its green's excess over the background's (the green's
    channel over the larger of the other two: the background's excess is 0, the figure's own colours have none), the figure's
    colour unmixed from the green; the pieces cut off the figure (specks of the green's noise) left out"""
    from scipy import ndimage as ndi
    bg = np.median(np.concatenate([a[:8, :8].reshape(-1, 3), a[:8, -8:].reshape(-1, 3), a[-8:, :8].reshape(-1, 3)]), 0)
    e = a[..., 1] - np.maximum(a[..., 0], a[..., 2]); e0 = bg[1] - max(bg[0], bg[2])
    al = np.clip(1.0 - (e - 4.0) / (e0 - 16.0), 0, 1)
    lab_, n = ndi.label(al > 0.3); sz = ndi.sum(np.ones_like(al), lab_, range(1, n + 1))
    main_ = np.isin(lab_, 1 + np.nonzero(sz >= 0.02 * sz.max())[0])
    al = np.where(ndi.binary_dilation(main_, iterations=2), al, 0.0)
    c = (a - (1 - al[..., None]) * bg) / np.maximum(al[..., None], 1e-3)
    c[..., 1] = np.minimum(c[..., 1], np.maximum(c[..., 0], c[..., 2]) + 12)   # (no green left in an edge)
    return np.clip(c, 0, 255), al


def foot2(q):
    """a foot at the cycle's phase q (0: its heel strikes): its ankle (x forward of the hips, y up, m), its angle (degrees)"""
    S = STRIDE2; q %= 1.0
    if q < 0.6:
        ax = 0.3 * S - q * S
        ph = 15.0 * (1 - q / 0.08) if q < 0.08 else (-35.0 * (q - 0.42) / 0.18 if q > 0.42 else 0.0)
        ay = L_AN + L_HE * math.sin(math.radians(ph)) if ph >= 0 else L_AN - L_TO * math.sin(math.radians(ph))
        return ax, ay, ph, True
    p = (q - 0.6) / 0.4
    ax = -0.3 * S + S * (3 * p * p - 2 * p ** 3) - 0.4 * S * p
    ph = -35.0 + 25.0 * min(1, p / 0.4) if p < 0.4 else (-10.0 + 25.0 * (p - 0.4) / 0.6)
    floor = L_AN - L_TO * math.sin(math.radians(ph)) if ph < 0 else L_AN + L_HE * math.sin(math.radians(ph))
    ay = max(floor, L_AN + 0.09 * math.sin(math.pi * p) ** 0.9)
    return ax, ay, ph, False


def hips2(q):
    """the hips' height at phase q: the bearing legs nearly straight (a knee bend of 6 degrees)"""
    dmax = math.sqrt(L_TH ** 2 + L_SH ** 2 + 2 * L_TH * L_SH * math.cos(math.radians(6)))
    H = 9.0
    for f in (foot2(q), foot2(q + 0.5)):
        if f[3]: H = min(H, f[1] + math.sqrt(max(0.0, dmax ** 2 - f[0] ** 2)))
    return H


def ik2(hip, ank):
    """the knee (forward) between the hip and the ankle"""
    dx, dy = ank[0] - hip[0], ank[1] - hip[1]; d = min(math.hypot(dx, dy), L_TH + L_SH - 1e-4)
    a = math.atan2(dy, dx); c = (L_TH ** 2 + d * d - L_SH ** 2) / (2 * L_TH * d); b = math.acos(max(-1, min(1, c)))
    k1 = (hip[0] + L_TH * math.cos(a + b), hip[1] + L_TH * math.sin(a + b))
    k2 = (hip[0] + L_TH * math.cos(a - b), hip[1] + L_TH * math.sin(a - b))
    return k1 if k1[0] > k2[0] else k2


def body2(a, k):
    """the first answer's frame k: its colours off the green, its share, its torso's column, its soles' row, its coat's hem
    and the briefcase's box (the dark box under his near hand, 0.31 m tall)"""
    from scipy import ndimage as ndi
    cx0, cy0 = (k % 4) * CELL[0], (k // 4) * CELL[1]
    raw = a[cy0:cy0 + CELL[1], cx0:cx0 + CELL[0]]; c, al = alpha_key(raw); m = al > 0.5
    ys, xs = np.nonzero(m); bot = ys.max() + 1
    band = m[bot - 228:bot - 148]; prof = band.sum(0); body = np.nonzero(prof > 0.5 * prof.max())[0]
    ax = (body.min() + body.max() + 1) / 2.0
    beige = m & (c[..., 0] > 90) & (c[..., 0] > c[..., 2] + 20); wid = beige.sum(1)
    belt = int(bot - 0.6 * S2); hem = belt
    while hem < bot and wid[hem] >= 3: hem += 1   # (the coat's hem: the first row under the belt with no coat)
    dark = m & (np.max(c, 2) < 85)
    top = next(y for y in range(belt - 30, hem) if dark[y].sum() >= 25)
    cols = np.nonzero(dark[top + 4:top + 10].sum(0) >= 4)[0]
    lab_, n = ndi.label(np.isin(np.arange(CELL[0]), cols)); big = np.argmax(ndi.sum(np.ones(CELL[0]), lab_, range(1, n + 1))) + 1
    cols = np.nonzero(lab_ == big)[0]
    return dict(raw=raw, c=c, al=al, m=m, ax=ax, bot=bot, hem=hem, bag=(top, int(top + 0.31 * S2), cols.min(), cols.max() + 1),
                dark=dark)


BOB2 = 0.7                                       # (the bob's share kept: 4.5 cm, the knees taking the rest)


def guide2():
    a = np.asarray(Image.open(SHEET1).convert('RGB')).astype(float)
    Hs = [hips2(k / 8) for k in range(8)]; Hm = sum(Hs) / 8; Hs = [Hm + BOB2 * (h - Hm) for h in Hs]
    A = np.zeros((GH, GW, 3)); A[:] = G_GREEN
    for k in range(8):
        cx0, cy0 = (k % 4) * CELL[0], (k // 4) * CELL[1]
        im = Image.fromarray(A.astype(np.uint8)); g = ImageDraw.Draw(im)
        P = lambda p: (cx0 + ANCH2 - 0.02 * S2 + p[0] * S2, cy0 + SOLE2 - p[1] * S2)

        def limb(p0, p1, w, col_):
            g.line([P(p0), P(p1)], fill=col_, width=int(w * S2))
            for q_ in (p0, p1):
                x, y = P(q_); rr = w * S2 / 2; g.ellipse([x - rr, y - rr, x + rr, y + rr], fill=col_)

        hip = (0.0, Hs[k])
        for q, col_ in ((k / 8 + 0.5, G_FAR), (k / 8, G_NEAR)):   # (the far leg first, the near one over it)
            fx, fy, ph, _ = foot2(q); ank = (fx, fy); kn = ik2(hip, ank); f = math.radians(ph)
            heel = (fx - L_HE * math.cos(f), fy - L_AN - L_HE * math.sin(f)); toe = (fx + L_TO * math.cos(f), fy - L_AN + L_TO * math.sin(f))
            limb(hip, kn, 0.15, col_); limb(kn, ank, 0.115, col_)
            g.polygon([P((fx - 0.045, fy + 0.025)), P(heel), P(toe), P((fx + 0.075, fy - 0.02))], fill=col_)
        A = np.asarray(im).astype(float)
        # his upper body over the legs (down to the hem), the briefcase over all, blended by their share
        B = body2(a, k); bob = int(round((Hs[k] - Hm) * S2))
        dx, dy = int(round(ANCH2 - B['ax'])), SOLE2 - B['bot'] - bob
        al = B['al'].copy(); al[B['hem']:] = 0
        t, b_, x0, x1 = B['bag']; bag = np.zeros_like(B['m']); bag[t:b_, x0:x1] = True
        al[bag] = np.maximum(al[bag], B['al'][bag])
        yy, xx = np.nonzero(al > 0.01); ty, tx = yy + dy + cy0, xx + dx + cx0
        ok = (ty >= cy0) & (ty < cy0 + CELL[1]) & (tx >= cx0) & (tx < cx0 + CELL[0])
        w = al[yy[ok], xx[ok]][:, None]
        A[ty[ok], tx[ok]] = A[ty[ok], tx[ok]] * (1 - w) + B['c'][yy[ok], xx[ok]] * w
        bm = bag & (B['al'] < 0.5); yy, xx = np.nonzero(bm)   # (the box's corners the old leg hid: the bag's colour)
        A[yy + dy + cy0, xx + dx + cx0] = np.median(B['c'][bag & B['dark']], 0)
    return Image.fromarray(np.clip(np.round(A), 0, 255).astype(np.uint8)), Hs


CTX_BOX = (470, 470, 910, 750)                   # the street round the crossing (scene px), at 22 h


def context():
    """the street round the crossing at 22 h (a render of the street, tools/dev/shot.cjs 22, kept as the input it was):
    enlarged with nearest pixels"""
    src = os.path.join(EDITS, 'xwalk_ctx_src.webp')
    a = Image.open(src).convert('RGB')
    return a.resize((a.width * 2, a.height * 2), Image.NEAREST)


def api_key():
    k = os.environ.get('OPENROUTER_API_KEY')
    if k: return k
    p = os.path.expanduser('~/.config/openrouter/key')
    return open(p).read().strip() if os.path.exists(p) else 'proxy-injected'


def ask(name='xwalk', refs=('xwalk_ctx.webp', 'study_walk_model.webp')):
    """asks the image model: NAME_prompt.txt, NAME_in.webp and the references; its answer NAME_model.webp"""
    imgs = [os.path.join(EDITS, f'{name}_in.webp')] + [os.path.join(EDITS, r) for r in refs]
    content = [{"type": "text", "text": open(os.path.join(EDITS, f'{name}_prompt.txt')).read().strip()}]
    for p in imgs:
        buf = io.BytesIO(); Image.open(p).convert('RGB').save(buf, 'PNG')
        content.append({"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()}})
    body = {"model": MODEL, "modalities": ["image", "text"], "usage": {"include": True}, "messages": [{"role": "user", "content": content}]}
    req = urllib.request.Request('https://openrouter.ai/api/v1/chat/completions', data=json.dumps(body).encode(),
                                 headers={'Authorization': 'Bearer ' + api_key(), 'Content-Type': 'application/json'})
    d = json.loads(urllib.request.urlopen(req, timeout=900).read())
    url = d['choices'][0]['message']['images'][0]['image_url']['url']
    im = Image.open(io.BytesIO(base64.b64decode(url.split(',', 1)[1])))
    im.save(os.path.join(EDITS, f'{name}_model.webp'), 'WEBP', lossless=True, quality=100, method=6)
    print(name, 'answer', im.size, 'saved; cost', d.get('usage', {}).get('cost'), '$')


# ---- his frames: the second answer's eight cells off their green (alpha_key: each pixel's share of him, his colours unmixed
# from the green), brought to his size by one scale (its man, 288 px from his soles to the top of his hair under the canopy on
# its first frame, is 70.9 scene px: PERSON), each scene pixel SS x SS points of the sheet (his colours weighed by their share,
# his dark strokes kept where they cover INK[1] of it: his eye; solid from half covered, and a thin line kept whole: the
# umbrella's shaft, 2 to 3 sheet px, a pixel's half or less, would break into dashes), set by his torso (the middle of his
# coat at his chest: his upper body on the same pixels in every frame) and his soles ----
SHEET1 = os.path.join(EDITS, 'xwalk_model.webp')   # (the first answer: the second guide's upper body)
SHEET = os.path.join(EDITS, 'xwalk2_model.webp')
CELL = (256, 512)                                # the sheet's cells (4 x 2, the guide's)
PERSON_SHEET = 288.0                             # (his height on the sheet: soles at 393, the top of his hair at 105)
PERSON = H_M * SOLK * CF / D_MID                 # his height in the street (scene px)
TORSO = (224, 148)                               # (his chest's rows over his soles on the sheet: between his collar and his belt)
WALK_T = 0.95                                    # the cycle's time (s): two short steps (0.46 m each), a man hurrying home in the rain
FRAME_T = (0.06, 0.26)
SS, INK, THIN = 8, (0.62, 0.3), 0.22


def reduce2(c, al, ax, ay, s):
    """the frame at the scene's pixels, its anchor on a pixel's corner (owner_study.reduce_cell, with each point's share)"""
    m = al > 0.02; ys, xs = np.nonzero(m)
    X0 = int(np.floor((xs.min() - ax) / s)) - 1; X1 = int(np.ceil((xs.max() + 1 - ax) / s)) + 1
    Y0 = int(np.floor((ys.min() - ay) / s)) - 1; Y1 = int(np.ceil((ys.max() + 1 - ay) / s)) + 1
    w, h = X1 - X0, Y1 - Y0
    u = ax + (X0 + (np.arange(w * SS) + 0.5) / SS) * s; v = ay + (Y0 + (np.arange(h * SS) + 0.5) / SS) * s
    xi = np.clip(np.floor(u).astype(int), 0, al.shape[1] - 1); yi = np.clip(np.floor(v).astype(int), 0, al.shape[0] - 1)
    inb = ((u >= 0) & (u < al.shape[1]))[None, :] & ((v >= 0) & (v < al.shape[0]))[:, None]
    C = c[yi][:, xi].reshape(h, SS, w, SS, 3).transpose(0, 2, 1, 3, 4).reshape(h, w, SS * SS, 3)
    A = (al[yi][:, xi] * inb).reshape(h, SS, w, SS).transpose(0, 2, 1, 3).reshape(h, w, SS * SS)
    lum = C @ np.array([0.299, 0.587, 0.114]); on = A > 0.5
    ref = np.array([[np.percentile(lum[y, x][on[y, x]], 80) if on[y, x].any() else 0 for x in range(w)] for y in range(h)])
    dark = on & (lum < INK[0] * ref[..., None])
    W_ = np.where((dark.sum(2) >= INK[1] * np.maximum(on.sum(2), 1))[..., None], dark * A, A * ~dark)
    W_ = np.where((W_.sum(2) == 0)[..., None], A, W_)
    rgb = (C * W_[..., None]).sum(2) / np.maximum(W_.sum(2), 1e-6)[..., None]
    cov = A.mean(2); sol = cov >= 0.5
    p = np.pad(cov, 1)
    thin = (cov >= THIN) & ((p[:-2, 1:-1] >= THIN) | (p[2:, 1:-1] >= THIN)) & (p[1:-1, :-2] < 0.5) & (p[1:-1, 2:] < 0.5)
    return rgb, sol | thin, -X0, -Y0


def cut():
    a = np.asarray(Image.open(SHEET).convert('RGB')).astype(float)
    s = PERSON_SHEET / PERSON; out = []
    for i in range(8):
        x0, y0 = (i % 4) * CELL[0], (i // 4) * CELL[1]
        c, al = alpha_key(a[y0:y0 + CELL[1], x0:x0 + CELL[0]]); m = al > 0.5
        ys, xs = np.nonzero(m); bot = ys.max() + 1
        band = m[bot - TORSO[0]:bot - TORSO[1]]; prof = band.sum(0)   # (the coat's widest run at his chest: not the hand nor the shaft)
        body = np.nonzero(prof > 0.5 * prof.max())[0]; ax = (body.min() + body.max() + 1) / 2.0
        rgb, mm, cx, cy = reduce2(c, al, ax, float(bot), s)
        out.append(dict(rgb=rgb, m=mm, ax=cx, ay=cy, s=s, mask=m, sax=ax, say=float(bot)))
    return out


def feet(c):
    """his feet in a frame: each shoe's sole (its column from his torso, its height over the baseline, scene px)"""
    from scipy import ndimage as ndi
    m = c['mask']; s = c['s']; ys, xs = np.nonzero(m); top, bot = ys.min(), ys.max(); y0 = int(bot - 0.085 * (bot - top))
    low = np.zeros_like(m); low[y0:] = m[y0:]; lab_, n = ndi.label(low); out = []
    for j in range(1, n + 1):
        yy, xx = np.nonzero(lab_ == j)
        if len(yy) < 30: continue
        yl = yy.max(); out.append(((xx[yy >= yl - 4].mean() - c['sax']) / s, (c['say'] - yl - 1) / s))
    return out


def steps(C):
    """[frame, its time (s), the step to the next (scene px)]: between two frames the foot that bears in both (on the ground in
    both, moved back the least) stays on its pixel: the body moves on by what it moved back. Each frame lasts its share of the
    cycle by its step"""
    adv = []
    for k in range(8):
        a, b = feet(C[k]), feet(C[(k + 1) % 8])
        cand = [fa[0] - fb[0] for fa in a for fb in b if fa[1] < 0.8 and fb[1] < 0.8 and fa[0] >= fb[0] - 0.3]
        adv.append(max(0.0, min(cand)) if cand else None)
    known = [v for v in adv if v is not None]; mean = sum(known) / len(known)
    adv = [mean if v is None else v for v in adv]
    stride = sum(adv); ints = []; acc = 0.0                                  # (whole pixels: their sum the stride, rounded)
    for v in adv:
        acc += v; ints.append(int(round(acc)) - sum(ints))
    return [[k, round(float(np.clip(WALK_T * v / stride, *FRAME_T)), 3), ints[k]] for k, v in enumerate(adv)], sum(ints)


# ---- his light: the far end's night on him (AMB, in linear light: the dusk's violet blue, a little of the city's mauve glow),
# his colours as dark as what is round him (VALUES); the sky's faint light on the umbrella's top (SKY); his tones in FAMILIES
# families, no dark outline, few lone pixels, a fine grain. The lights street.js adds by their sources, each pixel's share
# (an edge's facing, its first ring 1, its second LIGHT_2): R right (the Center), G left (the oden), B up (the lamp) ----
AMB = (0.105, 0.095, 0.15)                       # (linear: his daylight colours to the far end's night: the coat L* ~24)
VALUES = (10.0, 26.0)
SKY = ((104, 84, 128), 0.32)                      # (the dusk sky's violet on the umbrella's top)
FAMILIES = 18
GRAIN, GRAIN_T = 2, 8
LIGHT_DIRS = {'R': (1.0, -0.15), 'G': (-1.0, -0.15), 'B': (0.25, -1.0)}
LIGHT_2 = 0.45


def lin(c):
    c = np.clip(np.asarray(c, float), 0, 255) / 255.0
    return np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)


def srgb(l):
    l = np.clip(l, 0, 1)
    return 255 * np.where(l > 0.0031308, 1.055 * l ** (1 / 2.4) - 0.055, 12.92 * l)


def facing(m, d):
    import ichiraku_figures as FG
    dep = FG.ring_depth(m); nx, ny = FG.normals(m); l = np.array(d, float); l /= np.hypot(*l); c = nx * l[0] + ny * l[1]
    return np.clip(np.where(dep == 1, np.clip((c - 0.15) / 0.75, 0, 1), np.where(dep == 2, LIGHT_2 * np.clip((c - 0.45) / 0.55, 0, 1), 0)) * m, 0, 1)


def graded(C):
    import ichiraku_figures as FG
    import ichiraku_interior as RI
    base = {}
    for k, c in enumerate(C):
        b = srgb(lin(c['rgb']) * np.array(AMB))
        b = FG.rim(b, c['m'], (0.1, -1.0), SKY[0], SKY[1], cos=0.55)
        base[k] = b
    allc = np.concatenate([base[k][c['m']] for k, c in enumerate(C)])
    fam = FG.palette(np.clip(allc, 0, 255), FAMILIES)
    lab_ = RI.lab(fam); L = lab_[:, 0]; top = max(L.max(), VALUES[1] + 1e-6)
    lab_[:, 0] = np.where(L > VALUES[0], VALUES[0] + (L - VALUES[0]) * (VALUES[1] - VALUES[0]) / (top - VALUES[0]), L)
    famB = FG.lab2rgb(lab_); Lf = RI.lab(famB)[:, 0]
    tile = np.random.default_rng(31).integers(-GRAIN, GRAIN + 1, (GRAIN_T, GRAIN_T))
    for k, c in enumerate(C):
        m = c['m']; h, w = m.shape
        idx = np.where(m, RI.nearest(np.clip(base[k].reshape(-1, 3), 0, 255), fam).reshape(m.shape), -1)
        idx = FG.no_outline(idx, m, Lf, (0.0, -1.0))
        idx = FG.unspeckle(idx, m, np.zeros_like(m))
        gr = np.tile(tile, (h // GRAIN_T + 1, w // GRAIN_T + 1))[:h, :w]
        night = np.zeros((h, w, 4)); night[..., 3] = m * 255
        night[..., :3] = np.clip(np.round(famB[np.maximum(idx, 0)] + gr[..., None]), 0, 255) * m[..., None]
        lt = np.zeros((h, w, 4)); lt[..., 3] = m * 255
        for j, key in enumerate('RGB'):
            lt[..., j] = np.round(255 * facing(m, LIGHT_DIRS[key]))
        c['night'], c['light'] = night, lt


def build():
    C = cut(); graded(C)
    st, stride = steps(C)
    # the cells: each frame trimmed to the box of all frames round the anchor (one size: the mesh never changes)
    L = max(c['ax'] for c in C); R_ = max(c['m'].shape[1] - c['ax'] for c in C)
    T = max(c['ay'] for c in C); B = max(c['m'].shape[0] - c['ay'] for c in C)
    w, h = int(L + R_), int(T + B)
    U = []
    for c in C:
        ox, oy = int(L - c['ax']), int(T - c['ay'])
        n = np.zeros((h, w, 4)); g = np.zeros((h, w, 4)); hh, ww = c['m'].shape
        n[oy:oy + hh, ox:ox + ww] = c['night']; g[oy:oy + hh, ox:ox + ww] = c['light']
        U.append((n, g))
    img = np.zeros((2 * h, 8 * w, 4), np.uint8)
    for k, (n, g) in enumerate(U):
        img[:h, k * w:(k + 1) * w] = np.round(n).astype(np.uint8); img[h:, k * w:(k + 1) * w] = np.round(g).astype(np.uint8)
    XWS = {'cw': w, 'ch': h, 'ax': int(L), 'ay': int(T), 'n': 8, 'steps': st, 'stride': stride, 'amb': [round(v, 4) for v in AMB],
           'path': [list(p) for p in PATH], 'kerb': KERB, 'h': round(PERSON, 1), 'dm': D_MID}
    return img, XWS, C


def preview(dirn, img, XWS, C):
    os.makedirs(dirn, exist_ok=True)
    h = XWS['ch']; bg = np.full((h, img.shape[1], 3), (44, 45, 73), float)
    al = img[:h, :, 3:] / 255.0
    a = bg * (1 - al) + img[:h, :, :3] * al
    lt = img[h:, :, :3].astype(float)
    both = np.concatenate([a, lt], 0)
    Image.fromarray(np.clip(both, 0, 255).astype(np.uint8)).resize((both.shape[1] * 6, both.shape[0] * 6), Image.NEAREST).save(os.path.join(dirn, 'atlas_x6.png'))
    json.dump(XWS, open(os.path.join(dirn, 'xws.json'), 'w'))


def main():
    if '--preview' in sys.argv or len(sys.argv) == 1:
        img, XWS, C = build()
        print('the walker: %.2f sheet px a scene px, %.1f px tall; cells %d x %d; stride %d px; steps %s' % (
            C[0]['s'], PERSON, XWS['cw'], XWS['ch'], XWS['stride'], XWS['steps']))
        if '--preview' in sys.argv:
            preview(sys.argv[sys.argv.index('--preview') + 1], img, XWS, C); return
        Image.fromarray(img, 'RGBA').save(OUT, 'WEBP', lossless=True, quality=100, method=6, exact=True)
        js = open(JS, encoding='utf-8').read()
        line = 'const XWS = ' + json.dumps(XWS, separators=(',', ':')) + ';'
        js2, k = re.subn(r'const XWS = \{.*?\};', lambda m_: line, js, count=1)
        if k and js2 != js: open(JS, 'w', encoding='utf-8').write(js2)
        print('wrote', OUT, '| street.js XWS', 'updated' if k else 'NOT FOUND'); return
    if '--input' in sys.argv:
        guide().save(os.path.join(EDITS, 'xwalk_in.webp'), 'WEBP', lossless=True, quality=100, method=6)
        context().save(os.path.join(EDITS, 'xwalk_ctx.webp'), 'WEBP', lossless=True, quality=100, method=6)
        if os.path.exists(SHEET): guide2()[0].save(os.path.join(EDITS, 'xwalk2_in.webp'), 'WEBP', lossless=True, quality=100, method=6)
        print('wrote xwalk_in.webp, xwalk_ctx.webp, xwalk2_in.webp'); return
    if '--ask' in sys.argv:
        ask(); return
    if '--ask2' in sys.argv:
        ask('xwalk2', ('xwalk_model.webp',)); return


if __name__ == '__main__':
    main()
