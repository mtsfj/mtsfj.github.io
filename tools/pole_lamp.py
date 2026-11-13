#!/usr/bin/env python3
"""The street lamp on the right pole, redrawn: its arm a clean steel tube, its bracket, its head a believable Japanese
street light, lit (its comp) and off (in the layers) alike (the owner: "luminaire du poteau").

    (a module: tools/redraw_zones.py's zone 'polelamp' calls draw() after 'poletex' (tools/pole_texture.py); it also
     writes assets/lamp.webp, the lamp's lit comp, and assets/night_far.webp over its box, from before copies: the same
     bytes each time)
    python3 tools/pole_lamp.py --preview DIR   (only shows it: the zone drawn on the layers as they are, written to
                                                DIR with its comp; run it on layers without the zone (the commit
                                                before it); nothing in the repository changes)

What was there: a head of soft smears (a dark top, a mauve glass, lit as a blurred white wedge in the comp), an arm of
uneven width with a pale blob where it met the head, and where it met the pole a dark mass with pink flecks (its
"plate", its clamp) over the apartment building's wall.
Now, in the street's own camera (tools/zone5_facades.py's: the vanishing point 700, 615, f 960 px, the eye 1.41 m up),
the lamp at the pole's depth (8.89 m, the foot's: tools/pole_foot.py), its glass where the painter's was (x 860..902,
under the cone of lit air street.js starts at row 165, LC):
- the head, a model cast pixel by pixel (4 x 4 rays a pixel; each pixel one surface, the most of its rays, its colour
  the ray's nearest its middle, its tones stepped as the painter shades: crisp, no gradient): a pressed-steel hood
  0.54 m long and 0.23 wide, a stadium in plan (its nose rounded toward the street), its crown from 6.5 cm at the nose
  to 10.5 at the back; under it a milky lens, a shallow bowl 0.43 by 0.21 m (4 cm deep) inset in the hood's rim, seen from below
  at the eye's angle (its near edge high, its far edge low, as the painter's glass); a collar at its back where the arm
  goes in. The hood lit as the painter lit it, from the open sky beyond the street (its nose, its shoulder along the
  top), darker by its back; the lens off in the street the painter's milky mauve (redder at its rim), in the power cut
  his dark glass (lighter toward the nose, the sky in it); lit (the comp), the painter's own lit colours laid by
  brightness, white at its middle, warm toward its rim, the hood's thin rim round it lit by it;
- the arm, one steel tube (4.6 px, 4.3 cm), the hood's steel: up from its bracket by the pole, a bend, then rising
  gently (12 degrees) to the head, as the painter's; its top lit by the sky, its lower edge darker with a shade of the
  street's warm light; the part by the pole lit on its left by the lamp (in the street, not in the power cut); its
  foot capped;
- its bracket: two flat straps from the pipe to the pole's two bands (tools/pole_texture.py, rows 183 and 215), a
  collar round the pipe at each; between them the wall;
- what the old head and arm covered: over the sky, nothing (transparent: the tree and the sky of the far layers show,
  night_far 0 there); over the building's wall, the wall carried along its own rays (the facade's lines to the vanishing
  point: its plaster, its parapet's edge) from beside, in each layer from its own pixels.
The lamp's other lights stay as street.js lays them (its cone, its rain, its pool, gl_lamp.webp). Needs Pillow, numpy,
scipy.
"""
import os
import sys
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDITS = os.path.join(ROOT, 'tools', 'src', 'edits')
VPX, VPY, FOC, EYE = 700.0, 615.0, 960.0, 1.41
BOX = (845, 128, 1023, 230)                     # the zone (redraw_zones.py 'polelamp')
COMP = ('lamp', (843, 134), (78, 54))           # the lit comp: street.js ASSETS.comps.lamp
SS = 4                                          # rays a pixel, each way
# the head (m): its hood, its lens, its collar
ZC, XH, AH, BH = 8.885, 1.705, 0.27, 0.115      # depth; the hood's middle, half its length, half its width
YB = 5.63                                       # the hood's rim (its underside)
HN, HB = 0.065, 0.105                           # its crown's height at the nose, at the back
XL, AL, BL, BULGE = 1.695, 0.215, 0.104, 0.042  # the lens: its middle, half length, half width, how far it bulges
COLLAR = (1.95, 2.02, 0.032, 0.05)              # X from, to, radius, its axis over the rim (m)
# the arm on the screen (it lies in the plane of the pole's axis, square to the view: drawn there)
ARM_R = 2.3                                     # its radius (px)
ARM_FOOT = (1010.5, 227.0)
ARM_BEND = [(1010.5, 192.0), (1010.5, 173.0), (994.0, 169.98), (976.0, 166.2)]   # a cubic: up, then over
ARM_END = (918.3, 153.6)                        # the collar's end
STRAPS = [(183, 3), (215, 3)]                   # the bracket's straps: their top row, rows (the pole's bands)
STRAP_X = (1011, 1022)
# what the old lamp covered
OLD_AXIS = [(918, 155), (935, 158), (950, 161.5), (962, 164.5), (974, 168.5), (984, 169.0), (990, 169.8), (995, 171.0),
            (1000, 172.6), (1004, 175.0), (1007.5, 178.5), (1010.0, 183.5), (1010.5, 226.0)]   # (zone5_facades.ARM_AXIS, on to the head)
OLD_R = 4.3
OLD_PLATE = (1011, 1022, 172, 227)              # its plate, its clamp's flecks (x0, x1, y0, y1)
SKY_CLEAR_TO = 177                              # (above this row, left of the building: the sky, cleared)
# colours (the painter's, from his hood, glass and arm)
HOOD = dict(dark=(20, 25, 52), mid=(50, 54, 90), lit=(96, 78, 110), top=(26, 22, 32), under=(34, 33, 60))
LENS_OFF = dict(mid=(123, 77, 130), rim=(108, 40, 76))           # the street: his milky mauve
LENS_CUT = dict(nose=(93, 75, 126), back=(36, 40, 72))            # the power cut: his dark glass
RIM_LIT = (243, 120, 112)                                         # the hood's rim lit by the lens (his warm edge)
ARM = dict(dark=(22, 26, 52), mid=(50, 54, 90), top=(98, 92, 130), under=(46, 34, 58), lamp=(116, 82, 92))   # (the hood's steel)
KEY = np.array([-0.8, 0.45, -0.4]); KEY = KEY / np.linalg.norm(KEY)   # the hood's light: the open sky beyond the street
LUMA = np.array([0.299, 0.587, 0.114])


def smooth(t):
    t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)


def steps(t, n):
    """t (0..1) in n even steps: the painter's stepped shading, no gradient."""
    return np.round(np.clip(t, 0, 1) * n) / n


# ---- the head, ray by ray
def plan(X, Z, xc, a, b):
    """A stadium in plan: 0 on its middle line, 1 on its edge."""
    return np.hypot(np.maximum(np.abs(X - xc) - (a - b), 0), Z - ZC) / b


def crown(X):
    return HN + (HB - HN) * smooth((X - (XH - AH)) / (2 * AH))


def top_of(X, Z):
    p = plan(X, Z, XH, AH, BH)
    return YB + crown(X) * np.clip(1 - p ** 6, 0, 1) ** (1 / 6.0), p


def bottom_of(X, Z):
    pl = plan(X, Z, XL, AL, BL)
    return np.where(pl < 1, YB - BULGE * np.sqrt(np.clip(1 - pl * pl, 0, 1)), YB), pl


def collar_in(X, Y, Z):
    x0, x1, r, h = COLLAR
    return (X >= x0) & (X <= x1) & (np.hypot(Y - (YB + h), Z - ZC) <= r)


def cast(xs, ys):
    """The rays through screen points (xs, ys): what each meets first (0 none, 1 hood, 2 lens, 3 rim, 4 collar), where
    (X, Y, Z) and the normal there."""
    n = len(xs); kind = np.zeros(n, int); P = np.zeros((n, 3)); N = np.zeros((n, 3))
    tx, ty = (xs - VPX) / FOC, (VPY - ys) / FOC
    alive = np.ones(n, bool)
    for Z in np.arange(ZC - BH - 0.01, ZC + BH + 0.01, 0.0012):
        if not alive.any(): break
        X, Y = tx * Z, EYE + ty * Z
        top, p = top_of(X, Z); bot, pl = bottom_of(X, Z)
        hit = alive & (p < 1) & (Y <= top) & (Y >= bot)
        col = alive & ~hit & collar_in(X, Y, Z)
        for m, k in ((hit, None), (col, 4)):
            if not m.any(): continue
            P[m] = np.stack([X[m], Y[m], np.full(m.sum(), Z)], -1)
            if k is None:
                kk = np.where(Y[m] <= YB + 0.0015, np.where(pl[m] < 1, 2, 3), 1)
                kind[m] = kk
            else: kind[m] = 4
            alive &= ~m
    # normals (from the surfaces' height fields, by differences; the collar's from its axis)
    e = 1e-3
    for k in (1, 2, 3, 4):
        m = kind == k
        if not m.any(): continue
        X, Y, Z = P[m, 0], P[m, 1], P[m, 2]
        if k == 4:
            v = np.stack([np.zeros_like(X), Y - (YB + COLLAR[3]), Z - ZC], -1)
        elif k == 1:
            f = lambda X, Z: top_of(X, Z)[0]
            gx = (f(X + e, Z) - f(X - e, Z)) / (2 * e); gz = (f(X, Z + e) - f(X, Z - e)) / (2 * e)
            v = np.stack([-gx, np.ones_like(X), -gz], -1)
            side = top_of(X, Z)[1] > 0.995                # (its wall: the plan's outward normal)
            if side.any():
                dx = np.maximum(np.abs(X - XH) - (AH - BH), 0) * np.sign(X - XH)
                v[side] = np.stack([dx[side], np.zeros(side.sum()), (Z - ZC)[side]], -1)
        elif k == 2:
            f = lambda X, Z: bottom_of(X, Z)[0]
            gx = (f(X + e, Z) - f(X - e, Z)) / (2 * e); gz = (f(X, Z + e) - f(X, Z - e)) / (2 * e)
            v = np.stack([gx, -np.ones_like(X), gz], -1)
        else:
            v = np.tile([0.0, -1.0, 0.0], (m.sum(), 1))
        N[m] = v / np.maximum(np.linalg.norm(v, axis=1, keepdims=True), 1e-9)
    return kind, P, N


def lit_palette():
    """The painter's lit glass (the comp as it was), its colours by brightness."""
    a = np.asarray(Image.open(os.path.join(EDITS, 'polelamp_comp_before.webp')).convert('RGBA')).astype(float)
    c = a[a[..., 3] > 0][:, :3]
    return c[np.argsort(c @ LUMA, kind='stable')]


def head_colours(kind, P, N, pal):
    """Each ray's colour: in the street (the lamp off), in the power cut, lit (the comp); and whether it is lit there."""
    n = len(kind); off, cut, lit = np.zeros((n, 3)), np.zeros((n, 3)), np.zeros((n, 3)); glow = np.zeros(n, bool)
    H = {k: np.array(v, float) for k, v in HOOD.items()}
    # the hood and the collar: steel, lit from the open sky beyond the street, its top edge by the sky above
    m = (kind == 1) | (kind == 4)
    Nm = N[m]
    key = steps(np.clip(Nm @ KEY, 0, 1) ** 1.3, 3)
    amb = steps(0.5 + 0.5 * np.clip(Nm @ np.array([0.0, 0.3, -1.0]) / np.hypot(0.3, 1.0), 0, 1), 2)
    up = steps(np.clip(Nm[:, 1] * 1.6, 0, 1) ** 2, 2)       # (its shoulder: the sky's light along its top)
    back = steps(smooth((P[m, 0] - XH - 0.5 * AH) / (0.5 * AH)), 1)[:, None]   # (its back, by the collar, darker)
    c = H['dark'] + (H['mid'] - H['dark']) * amb[:, None] + (H['lit'] - H['mid']) * key[:, None] + H['top'] * up[:, None]
    c = c * (1 - 0.3 * back)
    off[m] = cut[m] = lit[m] = c
    # the lens
    m = kind == 2
    pl = plan(P[m, 0], P[m, 2], XL, AL, BL)
    t = steps(smooth((pl - 0.55) / 0.45), 2)[:, None]
    off[m] = np.array(LENS_OFF['mid']) * (1 - t) + np.array(LENS_OFF['rim']) * t
    s = steps(smooth((P[m, 0] - (XL - AL)) / (2 * AL)), 4)[:, None]
    cut[m] = (np.array(LENS_CUT['nose']) * (1 - s) + np.array(LENS_CUT['back']) * s) * (1 - 0.15 * t)
    I = steps(np.clip(1 - pl * pl, 0, 1) ** 0.7, 5)
    q = np.clip(0.1 + 0.88 * I, 0, 1)
    lit[m] = pal[np.round(q * (len(pal) - 1)).astype(int)]
    glow[m] = True
    # the hood's rim under it, round the lens: dark, lit by the lens in the comp
    m = kind == 3
    off[m] = cut[m] = H['under']
    lit[m] = np.array(RIM_LIT); glow[m] = True
    return off, cut, lit, glow


HEAD_BOX = (848, 136, 922, 172)                 # (where the head can be: its rays are cast there only)


def render_head(box):
    """The head over box: per pixel its coverage, its colours (street, power cut, lit) and its lit share."""
    bx0, by0, bx1, by1 = box
    x0, y0, x1, y1 = HEAD_BOX; h, w = y1 - y0, x1 - x0
    o = (np.arange(SS) + 0.5) / SS
    gy, gx = np.mgrid[y0:y1, x0:x1].astype(float)
    xs = (gx[..., None, None] + o[None, None, None, :]).repeat(SS, 2).reshape(-1)
    ys = (gy[..., None, None] + o[None, None, :, None]).repeat(SS, 3).reshape(-1)
    kind, P, N = cast(xs, ys)
    pal = lit_palette()
    off, cut, lit, glow = head_colours(kind, P, N, pal)
    S = SS * SS
    K = kind.reshape(h, w, S)
    cov = (K > 0).mean(-1)
    # each pixel one surface (the most of its rays: crisp, as the painter's pixels), its colour that of its ray nearest
    # the pixel's middle on that surface
    cnt = np.stack([(K == k).sum(-1) for k in range(5)], -1); cnt[..., 0] = -1
    major = cnt.argmax(-1)
    order = np.argsort([abs(i % SS + 0.5 - SS / 2) + abs(i // SS + 0.5 - SS / 2) for i in range(S)], kind='stable')
    pick = np.zeros((h, w), int)
    for i in order[::-1]:
        pick = np.where(K[..., i] == major, i, pick)
    sel = lambda c: np.take_along_axis(c.reshape(h, w, S, 3), pick[..., None, None], 2)[..., 0, :]
    cov = (cov >= 0.5).astype(float)
    out = [cov, sel(off), sel(cut), sel(lit), ((major == 2) | (major == 3)).astype(float) * cov]
    full = []
    for a in out:                                  # (onto the zone's box)
        f = np.zeros((by1 - by0, bx1 - bx0) + a.shape[2:]); f[y0 - by0:y1 - by0, x0 - bx0:x1 - bx0] = a; full.append(f)
    return full


# ---- the arm, on the screen
def arm_axis():
    """Its axis, densely: points and their tangents."""
    pts = [np.array(ARM_FOOT)]
    b = [np.array(p) for p in ARM_BEND]
    pts += [np.linspace(ARM_FOOT, b[0], 40)[1:]]
    t = np.linspace(0, 1, 120)[:, None]
    pts += [((1 - t) ** 3) * b[0] + 3 * ((1 - t) ** 2) * t * b[1] + 3 * (1 - t) * t * t * b[2] + t ** 3 * b[3]]
    pts += [np.linspace(b[3], ARM_END, 160)[1:]]
    P = np.vstack([p.reshape(-1, 2) for p in pts])
    T = np.gradient(P, axis=0); T /= np.linalg.norm(T, axis=1, keepdims=True)
    return P, T


def render_arm(box, lamp_on):
    """The tube over box: per pixel its coverage and colour (lamp_on: the lamp's light on its part by the pole)."""
    x0, y0, x1, y1 = box; h, w = y1 - y0, x1 - x0
    P, T = arm_axis()
    o = (np.arange(SS) + 0.5) / SS
    cov = np.zeros((h, w)); col = np.zeros((h, w, 3))
    A = {k: np.array(v, float) for k, v in ARM.items()}
    lo = np.array([P[:, 0].min() - 4, P[:, 1].min() - 4]); hi = np.array([P[:, 0].max() + 4, P[:, 1].max() + 4])
    for yy in range(max(y0, int(lo[1])), min(y1, int(hi[1]) + 1)):
        for xx in range(max(x0, int(lo[0])), min(x1, int(hi[0]) + 1)):
            sx, sy = np.meshgrid(xx + o, yy + o); q = np.stack([sx.ravel(), sy.ravel()], -1)
            d = q[:, None, :] - P[None, :, :]; dist = np.hypot(d[..., 0], d[..., 1]); i = dist.argmin(1)
            dm = dist[np.arange(len(q)), i]
            # (the foot: capped square, nothing below it)
            inside = (dm <= ARM_R) & (q[:, 1] <= ARM_FOOT[1] + 0.5)
            if not inside.any(): continue
            t = T[i]; nrm = np.stack([-t[:, 1], t[:, 0]], -1)            # (the axis' normal on the screen)
            sc = np.clip(((q - P[i]) * nrm).sum(1) / ARM_R, -1, 1)          # (-1 .. 1 across it)
            front = np.sqrt(np.clip(1 - sc * sc, 0, 1))
            # its surface's normal on the screen (y down): up is the sky's, left the lamp's
            nx, ny = sc * nrm[:, 0], sc * nrm[:, 1]
            sky = steps(np.clip(-ny, 0, 1) ** 1.5, 2); under = steps(np.clip(ny, 0, 1) ** 2, 1)
            front = steps(front, 2)
            c = A['dark'] + (A['mid'] - A['dark']) * front[:, None] + (A['top'] - A['mid']) * sky[:, None] + (A['under'] - A['dark']) * under[:, None] * 0.6
            if lamp_on:                                                     # (the lamp's light on its left, by the pole)
                k = steps(np.clip(-nx, 0, 1) * smooth((q[:, 1] - 168) / 10.0) * smooth((q[:, 0] - 990) / 12.0), 2)
                c = c + (A['lamp'] - A['mid']) * 0.7 * k[:, None]
            m = inside
            if m.mean() < 0.5: continue           # (crisp: a pixel is the tube's or not, its colour its middle's)
            j = np.argmin(np.hypot(q[:, 0] - xx - 0.5, q[:, 1] - yy - 0.5) + 9 * ~m)
            cov[yy - y0, xx - x0] = 1; col[yy - y0, xx - x0] = c[j]
    return cov, col


def render_straps(box, lamp_on):
    """The bracket's straps (flat steel from the pipe to the pole's bands, their top lit by the sky, their lower edge
    dark) and the collars round the pipe (a pixel proud of it, lit on their left by the lamp): coverage and colour."""
    x0, y0, x1, y1 = box; h, w = y1 - y0, x1 - x0
    cov = np.zeros((h, w)); col = np.zeros((h, w, 3))
    A = {k: np.array(v, float) for k, v in ARM.items()}
    lamp = (A['lamp'] - A['mid']) * 0.7 if lamp_on else 0
    for yb, n in STRAPS:
        for i, tone in enumerate([A['top'], A['mid'], A['dark']][:n]):
            col[yb + i - y0, STRAP_X[0] - x0:STRAP_X[1] + 1 - x0] = tone
            cov[yb + i - y0, STRAP_X[0] - x0:STRAP_X[1] + 1 - x0] = 1
        for i in range(-1, n + 1):
            for x in range(1007, 1015):
                c = A['top'] if i == -1 else A['dark'] if i == n else (A['mid'] + lamp if x <= 1008 else A['mid'] if x <= 1012 else A['dark'])
                col[yb + i - y0, x - x0] = c; cov[yb + i - y0, x - x0] = 1
    return cov, col


# ---- the old lamp out
def b_edge(alpha):
    """The building's left silhouette in the box's rows (above the old arm: its parapet's top edge, on a ray)."""
    rows, xs = [], []
    for y in range(BOX[1], SKY_CLEAR_TO):
        run = np.nonzero(alpha[y, :BOX[2]] > 0)[0]
        if not len(run): continue
        # the run that ends at the box's right edge
        e = BOX[2] - 1; s = e
        while s - 1 >= 0 and alpha[y, s - 1] > 0: s -= 1
        if s > 950 and not (150 <= y <= 172): rows.append(y); xs.append(s)
    k = np.polyfit(rows, xs, 1)
    return lambda y: k[0] * y + k[1]           # (a line: the parapet's top edge runs on a ray)


def old_mask(shape):
    H, W = shape
    yy, xx = np.mgrid[0:H, 0:W].astype(float) + 0.5
    d = np.full((H, W), 1e9); Pa = np.array(OLD_AXIS, float)
    for (ax, ay), (bx, by) in zip(Pa[:-1], Pa[1:]):
        vx, vy = bx - ax, by - ay; t = np.clip(((xx - ax) * vx + (yy - ay) * vy) / (vx * vx + vy * vy), 0, 1)
        d = np.minimum(d, np.hypot(xx - (ax + t * vx), yy - (ay + t * vy)))
    m = d <= OLD_R
    x0, x1, y0, y1 = OLD_PLATE
    m[y0:y1 + 1, x0:x1 + 1] = True
    return m


def ray_fill(arr, hole, region):
    """Each hole pixel from the wall beside it along its own ray (the facade's lines to the vanishing point), the
    nearest good pixel each side, weighed by distance (RGBA)."""
    out = arr.copy(); H, W = hole.shape
    for y, x in zip(*np.nonzero(hole)):
        v = (VPY - (y + 0.5)) / (x + 0.5 - VPX)
        acc, wsum = np.zeros(4), 0.0
        for sgn in (-1, 1):
            for dx in range(1, 24):
                xx = x + sgn * dx
                if xx < 0 or xx >= W: break
                yf = VPY - v * (xx + 0.5 - VPX) - 0.5; ya = int(np.floor(yf)); f = yf - ya
                if ya < 0 or ya + 1 >= H: break
                if not (region[ya, xx] and region[ya + 1, xx]): break
                if hole[ya, xx] or hole[ya + 1, xx]: continue
                acc += (arr[ya, xx] * (1 - f) + arr[ya + 1, xx] * f) / dx; wsum += 1 / dx
                break
        if wsum > 0: out[y, x] = acc / wsum
    return out


def draw_layers(city, unlit, box=BOX):
    """Both layers changed in place over box; returns what changed, the lit comp, and the head's coverage."""
    x0, y0, x1, y1 = box
    H, W = city.shape[:2]
    old = old_mask((H, W))
    edge = b_edge(city[..., 3])
    yy, xx = np.mgrid[0:H, 0:W]
    inbox = (xx >= x0) & (xx < x1) & (yy >= y0) & (yy < y1)
    left = inbox & (yy < SKY_CLEAR_TO) & (xx + 0.5 < edge(yy.astype(float)) - 1.0)   # left of the building: the sky
    wall = inbox & ~left & (xx >= 941)                                    # the building's wall
    sky = left & (city[..., 3] > 0)                                       # (the old head and arm there)
    hole = old & wall
    ch = np.zeros((H, W), bool)
    for arr in (city, unlit):
        arr[sky] = 0
        f = ray_fill(arr, hole, wall)
        arr[hole] = f[hole]
    ch |= sky | hole
    # the arm, its bracket, the head
    hc, hoff, hcut, hlit, hglow = render_head(box)
    for arr, on in ((city, True), (unlit, False)):
        sub = arr[y0:y1, x0:x1]
        ac, acol = render_arm(box, on)
        sc, scol = render_straps(box, on)
        hcol = hoff if on else hcut
        for c, col in ((ac, acol), (sc, scol), (hc, hcol)):
            c = np.where(c < 0.15, 0, np.where(c > 0.85, 1, c))
            m = c > 0
            a0 = sub[..., 3:] / 255.0
            # (over what is there: its colour premultiplied by its alpha, the new on top)
            prem = sub[..., :3] * a0 * (1 - c[..., None]) + col * c[..., None]
            na = c + a0[..., 0] * (1 - c)
            sub[m, :3] = (prem / np.maximum(na, 1e-6)[..., None])[m]; sub[m, 3] = 255 * na[m]
            ch[y0:y1, x0:x1] |= m
    # the lit comp: the head lit where the lens lights it
    cn, (cx, cy), (cw, chh) = COMP
    comp = np.zeros((chh, cw, 4))
    bx0, by0 = cx - x0, cy - y0
    hcv = np.where(hc < 0.15, 0, np.where(hc > 0.85, 1, hc))
    for j in range(chh):
        for i in range(cw):
            Y, X = by0 + j, bx0 + i
            if 0 <= Y < y1 - y0 and 0 <= X < x1 - x0 and hglow[Y, X] > 0 and hcv[Y, X] > 0:
                g = hglow[Y, X] / max(hc[Y, X], 1e-6)
                comp[j, i, :3] = hlit[Y, X] * min(1, g) + hoff[Y, X] * (1 - min(1, g))
                comp[j, i, 3] = 255 * hcv[Y, X]
    return ch, comp


def save(a, path, mode='RGBA'):
    Image.fromarray(np.round(np.clip(a, 0, 255)).astype(np.uint8), mode).save(path, 'WEBP', lossless=True, quality=100, method=6, exact=True)


def far_layer(ch, box=BOX):
    """assets/night_far.webp, its box from its before copy, 0 (the street's) where the lamp changed."""
    nf = np.asarray(Image.open(os.path.join(ROOT, 'assets', 'night_far.webp')).convert('RGB')).astype(float).copy()
    x0, y0, x1, y1 = box
    nf[y0:y1, x0:x1] = np.asarray(Image.open(os.path.join(EDITS, 'polelamp_before_far.webp')).convert('RGB')).astype(float)
    nf[ch] = 0
    return nf


def draw(city, unlit, box=BOX):
    """The zone (redraw_zones.py): both layers changed in place; assets/lamp.webp and assets/night_far.webp written."""
    ch, comp = draw_layers(city, unlit, box)
    save(comp, os.path.join(ROOT, 'assets', COMP[0] + '.webp'))
    save(far_layer(ch, box), os.path.join(ROOT, 'assets', 'night_far.webp'), 'RGB')
    return ch


def preview(out):
    os.makedirs(out, exist_ok=True)
    L = {t: np.asarray(Image.open(os.path.join(ROOT, 'assets', f)).convert('RGBA')).astype(float)
         for t, f in (('city', 'layer_city_off.webp'), ('unlit', 'street_unlit.webp'))}
    A = {t: a.copy() for t, a in L.items()}
    ch, comp = draw_layers(A['city'], A['unlit'])
    print('pixels changed', int(ch.sum()))
    save(A['city'], os.path.join(out, 'layer_city_off.webp')); save(A['unlit'], os.path.join(out, 'street_unlit.webp'))
    save(comp, os.path.join(out, 'lamp.webp'))


if __name__ == '__main__':
    if '--preview' in sys.argv: preview(sys.argv[sys.argv.index('--preview') + 1])
    else: print(__doc__)
