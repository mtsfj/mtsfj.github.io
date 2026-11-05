#!/usr/bin/env python3
"""The passer-by of the Gommage (Clair Obscur: Expedition 33): someone walking the far sidewalk along the railing in the rain.

    python3 tools/e33_walker.py      (writes assets/e33_walker.webp; reads nothing)

An original figure, no game's: an older person (grey hair) in a long dark coat and a red scarf, a white umbrella held
over the head, seen from the side, walking right (street.js mirrors the cells to walk left). Rigged in metres and drawn
at the far sidewalk's scale (PPM: 21 px a metre there, the doors behind it being 2 m for 44 px): 1.65 m tall, the
umbrella 0.9 m across. The legs on two bones each, set by where the foot is (IK): a foot is planted half the stride and
moves back under the body at its walking speed, swings forward the other half, lifted; a stride of two steps is 30 px
(STEP 15 px), cut in sixteen cells, each drawn at its own fraction of a pixel along the stride (the hip there), so that
street.js, moving the figure with the cells, keeps a planted foot on the same pixel. The far arm swings; the near one
holds the umbrella. Each shape drawn at 8x (SS), then each scene pixel takes the material covering most of it (opaque
when most of it is: no blended edge, no colour made up), then its colour by material: shade, base, lit (COL), as the far
sidewalk's dusk light shows them (street.js scales them by the light there now); lit along the tops (the sky's light),
the coat's back edge in shade, the sleeve's upper edge catching the light over the coat. Then the stand; then the back
(at the railing, turned to the Monolith: the umbrella's dome over the head, the scarf's end down the back, the near arm
up to the shaft; never mirrored) and the half turn between the two (the same figure narrower, its head and umbrella
still leaning where it faced; mirrored as it walked). Its 19 cells (16 walking, the stand, the back, the half turn) side
by side, 32 x 46 each, the hip over column 14, the shoes' last row 43. The alpha holds each pixel's turn in the Gommage,
128 (first) .. 255 (last): the edges first, in a scatter (a seeded draw): street.js lets a pixel go when the Gommage
passes its turn (its back is what comes apart).
Needs Pillow, numpy.
"""
import os
import math, numpy as np
from PIL import Image, ImageDraw
SS, PPM, CW, CH, AX, AY = 8, 21.0, 32, 46, 14, 44     # supersampling, px per metre (the far sidewalk), the cell, the hip's column and the ground's row in it
E, UMB_T, UMB_B, SHAFT, HAIR, SKIN, SCARF, COAT, COATF, TROU, TROUF, SHOE, SHOEF, HAND, SLEEVE = range(15)

OFF = [0.0]                                      # the cell's sub-pixel offset (the hip's place between whole pixels)
TURN = [1.0, 0.0]                                # (a turning figure: its width's share, its head's lean toward where it faced)
def P(x, y):                                     # metres (x forward, y up, feet at 0) -> supersampled px
    x = x * TURN[0] + TURN[1] * (1 if y > 1.45 else 0.4)
    return ((AX + 0.5 + OFF[0] + x * PPM) * SS, (AY - y * PPM) * SS)

def cap(d, a, b, w, m):                          # a limb: a capsule from a to b, w metres thick
    (x0, y0), (x1, y1) = P(*a), P(*b); r = w * PPM * SS / 2
    d.line([(x0, y0), (x1, y1)], fill=m, width=int(round(2 * r)))
    for (x, y) in ((x0, y0), (x1, y1)): d.ellipse([x - r, y - r, x + r, y + r], fill=m)

def poly(d, pts, m): d.polygon([P(*p) for p in pts], fill=m)

TH, SH = 0.44, 0.42                              # thigh, shin (m); the ankle 0.07 over the ground
STEP = 15 / PPM                                  # a step: 15 px (0.71 m); a stride of two, 30 px, sixteen cells of 1.875 px

def foot_at(p):                                  # the near foot's ankle relative to the hip's x, and its lift: planted in [0, .5), swinging after
    if p < 0.5: return STEP / 2 - STEP * (p / 0.5), 0.0
    u = (p - 0.5) / 0.5; s = u * u * (3 - 2 * u)
    return -STEP / 2 + STEP * s, 0.07 * math.sin(math.pi * u)

def leg(d, hip, p, mt, ms):                      # two bones on the foot's place (the knee forward)
    fx, lift = foot_at(p); ax_, ay_ = hip[0] + fx, 0.07 + lift
    dx, dy = ax_ - hip[0], ay_ - hip[1]; D = min(TH + SH - 1e-4, math.hypot(dx, dy))
    a0 = math.atan2(dy, dx); c = (TH * TH + D * D - SH * SH) / (2 * TH * D); ang = a0 + math.acos(max(-1, min(1, c)))   # (the knee on the forward side)
    kx, ky = hip[0] + TH * math.cos(ang), hip[1] + TH * math.sin(ang)
    cap(d, hip, (kx, ky), 0.15, mt); cap(d, (kx, ky), (ax_, ay_), 0.11, mt)
    toe_up = 0.05 * lift / 0.07 if p >= 0.5 else 0.0
    poly(d, [(ax_ - 0.07, ay_ + 0.03), (ax_ + 0.04, ay_ + 0.05), (ax_ + 0.2, ay_ - 0.04 + toe_up), (ax_ + 0.19, ay_ - 0.07 + toe_up), (ax_ - 0.07, ay_ - 0.07)], ms)
    return (kx, ky)

def frame(p, stand=False):
    im = Image.new('L', (CW * SS, CH * SS), E); d = ImageDraw.Draw(im)
    s2 = math.sin(2 * math.pi * p); c2 = math.cos(2 * math.pi * p)
    A = 0 if stand else 24 * s2                                   # (the arms' swing, as the legs')
    bob = 0 if stand else -0.016 * math.cos(4 * math.pi * p)     # (lowest as both feet are down, highest over the planted one)
    hip = (0.0, 0.86 + bob)
    leg(d, hip, 0.25 if stand else (p + 0.5) % 1, TROUF, SHOEF)   # the far leg (behind)
    # the far arm, swinging a little behind the coat
    sw = math.radians(-14 * s2 if not stand else 0)
    cap(d, (-0.02, 1.36 + bob), (-0.02 + 0.5 * math.sin(sw), 1.36 + bob - 0.5 * math.cos(sw)), 0.08, COATF)
    leg(d, hip, 0.25 if stand else p, TROU, SHOE)                 # the near leg
    # the coat: shoulders to the knee, A-line, its hem following the legs
    hf = 0.02 * A / 24
    poly(d, [(-0.13, 1.40 + bob), (0.10, 1.41 + bob), (0.15, 1.28 + bob), (0.15, 1.05 + bob), (0.19 + hf, 0.55 + bob), (-0.20 + hf, 0.55 + bob),
             (-0.16, 0.95 + bob), (-0.15, 1.25 + bob)], COAT)
    # the scarf: a band round the neck and its end down the back
    poly(d, [(-0.10, 1.37 + bob), (0.09, 1.38 + bob), (0.08, 1.45 + bob), (-0.08, 1.45 + bob)], SCARF)
    poly(d, [(-0.12, 1.42 + bob), (-0.05, 1.40 + bob), (-0.11, 1.18 + bob), (-0.17, 1.2 + bob)], SCARF)
    # the head: grey hair over the back and top, the face in front
    hx, hy, r = 0.03, 1.54 + bob, 0.105
    (cx, cy) = P(hx, hy); R = r * PPM * SS
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=SKIN)
    d.pieslice([cx - R, cy - R, cx + R, cy + R], 120, 330, fill=HAIR)
    # the near arm up to the umbrella's shaft, the hand on it
    hand = (0.2, 1.12 + bob)
    cap(d, (0.0, 1.36 + bob), (0.06, 1.13 + bob), 0.085, SLEEVE); cap(d, (0.06, 1.13 + bob), hand, 0.08, SLEEVE)
    # the umbrella: the shaft from the hand, its canopy tipped a little forward into the rain
    tilt = math.radians(7); top = (0.08, 1.98 + bob)
    cap(d, (hand[0] + 0.01, hand[1] - 0.06), top, 0.035, SHAFT)
    def rot(x, y): return (top[0] + x * math.cos(tilt) + y * math.sin(tilt), top[1] - x * math.sin(tilt) + y * math.cos(tilt))
    # the canopy: a dome 0.9 m across, its rim scalloped between eight ribs (in profile: five tips), the tips a little down
    R_, Hd = 0.45, 0.3
    dome = [rot(R_ * math.cos(a), -Hd + Hd * math.sin(a) ** 0.7) for a in np.linspace(0, math.pi, 31)]
    rim = []
    for k in range(5):                                            # the rim from the back tip to the front tip, sagging between ribs
        x0_, x1_ = -R_ + 2 * R_ * k / 5, -R_ + 2 * R_ * (k + 1) / 5
        for u in np.linspace(0, 1, 7)[:-1]:
            rim.append(rot(x0_ + (x1_ - x0_) * u, -Hd - 0.035 + 0.05 * math.sin(math.pi * u)))
    rim.append(rot(R_, -Hd - 0.035))
    poly(d, dome + rim[::-1], UMB_T)
    cap(d, rot(0, 0), rot(0, 0.03), 0.03, SHAFT)                  # the ferrule
    cap(d, (hand[0] - 0.02, hand[1]), (hand[0] + 0.03, hand[1]), 0.06, HAND)
    return np.array(im)

def frame_back(turn=1.0):                        # seen from behind, at the railing, facing the Monolith: the umbrella over the head, the
    im = Image.new('L', (CW * SS, CH * SS), E); d = ImageDraw.Draw(im)   # scarf's end down the back, the near arm up to the shaft;
    TURN[:] = [0.62 + 0.38 * turn, 0.05 * (1 - turn)]   # turn < 1: half way round from the side (narrower, head and umbrella still to the front)
    for sx, mt, ms in ((-0.06, TROUF, SHOEF), (0.06, TROU, SHOE)):        # the legs, a little apart (the right one nearer the light)
        cap(d, (sx, 0.86), (sx * 1.1, 0.1), 0.12, mt)
        poly(d, [(sx * 1.1 - 0.06, 0.1), (sx * 1.1 + 0.06, 0.1), (sx * 1.1 + 0.06, 0.0), (sx * 1.1 - 0.06, 0.0)], ms)
    poly(d, [(-0.1, 1.43), (0.1, 1.43), (0.19, 1.39), (0.215, 1.3), (0.22, 1.05), (0.235, 0.55), (-0.235, 0.55), (-0.22, 1.05), (-0.215, 1.3), (-0.19, 1.39)], COAT)   # the coat, its round shoulders, A-line
    cap(d, (-0.2, 1.33), (-0.235, 0.84), 0.08, COATF)                     # the far arm down along the coat
    cap(d, (0.19, 1.34), (0.21, 1.18), 0.085, SLEEVE)                     # the near arm: its shoulder, the forearm forward to the shaft
    poly(d, [(-0.11, 1.37), (0.11, 1.37), (0.1, 1.45), (-0.1, 1.45)], SCARF)                # the scarf round the neck
    poly(d, [(0.0, 1.40), (0.07, 1.40), (0.06, 1.12), (-0.01, 1.14)], SCARF)                # its end down the back
    (cx, cy) = P(0.0, 1.54); R = 0.105 * PPM * SS
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=HAIR)                                  # the back of the head
    top = (0.0, 1.98)                                                                       # the umbrella: its dome over the head, level
    R_, Hd = 0.45, 0.3
    dome = [(top[0] + R_ * math.cos(a), top[1] - Hd + Hd * math.sin(a) ** 0.7) for a in np.linspace(0, math.pi, 31)]
    rim = []
    for k in range(4):                                                                      # (from behind: four ribs' tips, the rim sagging between)
        x0_, x1_ = -R_ + 2 * R_ * k / 4, -R_ + 2 * R_ * (k + 1) / 4
        for u in np.linspace(0, 1, 7)[:-1]: rim.append((x0_ + (x1_ - x0_) * u, top[1] - Hd - 0.035 + 0.05 * math.sin(math.pi * u)))
    rim.append((R_, top[1] - Hd - 0.035))
    poly(d, dome + rim[::-1], UMB_T)
    cap(d, (0.0, top[1]), (0.0, top[1] + 0.03), 0.03, SHAFT)                                # the ferrule
    cap(d, (0.0, 1.68), (0.0, 1.6), 0.035, SHAFT)                                           # the shaft under the canopy, over the head
    TURN[:] = [1.0, 0.0]
    return np.array(im)


def down(a):                                     # whole pixels: the material covering most of each pixel (opaque when most of it is)
    H, W = a.shape[0] // SS, a.shape[1] // SS
    b = a.reshape(H, SS, W, SS).transpose(0, 2, 1, 3).reshape(H, W, SS * SS)
    out = np.zeros((H, W), np.uint8)
    for i in range(H):
        for j in range(W):
            v = b[i, j]; n = np.bincount(v, minlength=15)
            if n[E] * 2 > v.size: continue
            n[E] = 0; out[i, j] = n.argmax()
    return out

COL = {  # each material's colour at the dusk light of the far sidewalk (sRGB): shade, base, lit
    UMB_T: [(66, 68, 102), (82, 84, 122), (100, 102, 142)], UMB_B: [(40, 40, 64)] * 3, SHAFT: [(22, 20, 28)] * 3,
    HAIR: [(46, 46, 64), (58, 58, 78), (70, 70, 92)], SKIN: [(54, 40, 52), (66, 50, 62), (78, 60, 72)],
    SCARF: [(64, 18, 32), (84, 24, 40), (104, 34, 50)], COAT: [(14, 14, 26), (19, 19, 34), (27, 27, 45)], COATF: [(11, 11, 21)] * 3,
    TROU: [(12, 12, 22), (15, 15, 27), (20, 20, 34)], TROUF: [(10, 10, 18)] * 3, SHOE: [(8, 8, 15), (10, 10, 18), (16, 16, 26)], SHOEF: [(7, 7, 13)] * 3,
    HAND: [(54, 40, 52), (66, 50, 62), (78, 60, 72)], SLEEVE: [(14, 14, 26), (19, 19, 34), (30, 30, 50)]}

def shade(m):
    H, W = m.shape; out = np.zeros((H, W, 4), np.uint8)
    for i in range(H):
        for j in range(W):
            k = m[i, j]
            if k == E: continue
            up = m[i - 1, j] if i else E
            lvl = 2 if up != k and up in (E, UMB_B) or (k == UMB_T and i > 0 and m[i - 1, j] == E) else 1
            if k == UMB_T:                                       # the canopy: lit on its upper rows, the rim row in shade
                below = m[i + 1, j] if i + 1 < H else E
                lvl = 2 if up == E else (0 if below != UMB_T else 1)
            if k == SLEEVE:                                      # the sleeve over the coat: its upper edge lit, the rest the coat's
                lvl = 2 if up in (COAT, E, SCARF) else 1
            if k == COAT:                                        # the coat: its back edge in shade, its shoulders lit
                left = m[i, j - 1] if j else E
                if left in (E, COATF): lvl = 0
            out[i, j, :3] = COL[k][lvl]; out[i, j, 3] = 255
    return out

def sheet(n=16):
    cells = []
    for f in range(n):
        OFF[0] = (f * 30 / n) % 1; cells.append(shade(down(frame(f / n))))
    OFF[0] = 0.0; cells.append(shade(down(frame(0, stand=True))))
    cells.append(shade(down(frame_back())))
    cells.append(shade(down(frame_back(0.5))))
    return cells

def order(cell, seed):                           # each pixel's turn in the Gommage, 0 (first) .. 1: the edges first, in a scatter
    a = cell[..., 3] > 0; H, W = a.shape
    d = np.where(a, 99, 0).astype(float)
    for _ in range(2):                           # (a chamfer distance to the outside, both passes twice)
        for y in range(H):
            for x in range(W):
                if a[y, x]:
                    for dy, dx in ((-1, 0), (0, -1), (-1, -1), (-1, 1)):
                        yy, xx = y + dy, x + dx; v = d[yy, xx] if 0 <= yy < H and 0 <= xx < W else 0
                        d[y, x] = min(d[y, x], v + (1 if dy == 0 or dx == 0 else 1.4))
        for y in range(H - 1, -1, -1):
            for x in range(W - 1, -1, -1):
                if a[y, x]:
                    for dy, dx in ((1, 0), (0, 1), (1, 1), (1, -1)):
                        yy, xx = y + dy, x + dx; v = d[yy, xx] if 0 <= yy < H and 0 <= xx < W else 0
                        d[y, x] = min(d[y, x], v + (1 if dy == 0 or dx == 0 else 1.4))
    rng = np.random.default_rng(seed)
    o = 0.5 * np.clip((d - 1) / 3, 0, 1) + 0.5 * rng.random((H, W))
    o = (o - o[a].min()) / max(1e-6, o[a].max() - o[a].min())
    out = cell.copy(); out[..., 3] = np.where(a, 128 + np.round(127 * o), 0).astype(np.uint8)
    return out

def build_sheet(path):
    cells = [order(c, 33 + i) for i, c in enumerate(sheet())]
    W = Image.new('RGBA', (CW * len(cells), CH), (0, 0, 0, 0))
    for i, c in enumerate(cells): W.paste(Image.fromarray(c), (i * CW, 0))
    W.save(path, 'WEBP', lossless=True, quality=100, method=6, exact=True)


if __name__ == '__main__':
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    build_sheet(os.path.join(root, 'assets', 'e33_walker.webp'))
    print('assets/e33_walker.webp: %d cells of %d x %d' % (19, CW, CH))
