#!/usr/bin/env python3
"""The R6 block's sprites: the scout drone (every size it takes on the street, from every side, its wheels turning) and the
small wall camera, drawn whole-pixel from a model of each, built on real ones.

    python3 tools/r6_sprites.py        (writes assets/r6_drone.webp, r6_drone_n.webp, r6_cam.webp, the screen's r6_panel, r6_bezel,
                                        r6_key, r6_key_on, r6_ant .webp; prints the camera's cell, then
                                        the drone's layout: street.js's R6C and R6D)

The drone is a two-wheeled throwable reconnaissance robot of the kind police and soldiers roll into a room before them
(ReconRobotics' Throwbot 2 and its Recon Scout forebears, measured on their maker's front and back views and on public
domain photos of them on asphalt): 20 cm across, two wheels 10.8 cm high and 3.2 cm thick, between them a tube 4 cm
thick on the axle (14 cm long) with the camera in the middle of its front (a small round lens in a bezel), a green status
light over it and one at the back, a flat tail trailing back and down to the ground from the middle of its back (what keeps
the tube from spinning), two whip antennas rising from the tube's ends, raked backwards. Its wheels are rubber tyres with a
staggered tread of lugs (10 round, two rows across the tread, half a lug apart; the maker's larger rubber tyres), their
faces a plain hub and its cap, a light marker dot by the rim. Matte black: rubber, black anodized aluminium, a lighter
bezel. An original design (no maker's marking, no game's shapes). (R6_DESIGN=claw: the Throwbot 2's own clawed wheels,
compared.)

It is drawn by casting rays through the model (orthographic: at the street's scale a 20 cm robot has no perspective of
its own), SS x SS samples a pixel: a pixel is the robot's where most of its samples are, it takes the material most of
them hit (the lens, its bezel, the light win a tie); thin parts (the antenna, the tail when thinner than a pixel) are
whole-pixel lines behind what is nearer (a whip seen near end on: one straight column); lone pixels go, one-pixel notches
fill, a stray piece is tied back (one shape a cell); the lens and the lights last, by one rule for every size and turn
(where they face the eye past the tyres: the lens 1 px, 2 x 2 from 24 px wide; each light 1 px). Each pixel keeps its normal (snapped to
a few directions, so a round thing takes the few flat tones a painter gives it, not a smooth gradient), and a class:
matte, satin, glass, metal, its own light. The page lights it with the street's own picture round it (street.js, R6).

Its layout: one block per width (WIDTHS: the robot's width in whole px, from the far end of its routes to their near end;
px per m = width / 0.201, its view from above at that distance: the eye 1.41 m up), each block NROLL columns (its wheels
turned by ROLL_STEP each: the tread moves on a quarter lug a turn, so it reads as rolling, the marker goes round) by NPSI rows (the eye's
side of it, every 22.5 degrees from its lens (0) round its left side to its back (8); the other side is the same robot
mirrored, which the page does). Two atlases of the same layout: r6_drone.webp its colours (albedo, sRGB), r6_drone_n.webp
each pixel's normal (R x right, G y up, 0..255 for -1..1) and class (B: 0 matte, 40 satin, 80 glass, 120 metal, 160 its
own light).

The wall camera is a small vandal-proof dome camera (as on public domain and free photos of them: domes screwed flat on a wall at
a corner under a cornice, small white domes on shop walls, one at night): an ivory base 9.2 cm across flat on the wall, a smoked
half-sphere 6.6 cm across bulging from it, the lens and its infrared LEDs inside, a status light on the base's rim; on the wall of
the tall building on the right (the right facades' plane, X 5.0 m) under its tiled eave, at the corner over the arcade's opening,
2 px under the eave's lit lower edge, looking down the street (CAM_P). It is cast as the eye sees it from 1.41 m up across the
street, its small parts stamped on their pixel; its cell is placed round it (printed: x, y, w, h). r6_cam.webp: six cells, its
pixels as the eave's shadow lights them (CAM_DN from below, CAM_UP from above; graded by the page as the street's sprites); the
arcade's light on what of it faces the opening (the housing's rim toward it its palest pixels); its status light; its infrared
LEDs' dull red (one dot at this size: a ring, with the highlight and the light, read as a face); the dome's one highlight; the
status light's glow. The page adds the last five on the screen's own values, so each is baked as what its light adds over that
pixel. (R6_CAM, R6_TONE: the mounts and housings compared.)
Needs Pillow, numpy.
"""
import json
import math
import os
import sys
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = lambda p: os.path.join(os.environ.get('R6_OUT') or os.path.join(ROOT, 'assets'), p)   # (R6_OUT: elsewhere, for comparing)
SV = dict(lossless=True, quality=100, method=6, exact=True)
SS = 6                                   # samples per pixel side

# ---- the drone (metres; its frame: x across to its right, y up, z forward, the ground at y 0) ----
WIDTH = 0.201                            # wheel face to wheel face
R = 0.054                                # the wheels' radius (to the lugs' tops)
WHW = 0.016                              # a wheel's half thickness
WX = WIDTH / 2 - WHW                     # a wheel's centre plane
LUG = 0.004                              # the lugs' height over the tread
NLUG = 10                                # lugs round a row (two rows, staggered): chunky, a lug every 36 degrees
HUB = 0.03                               # the hub's radius (the tyre's sidewall outside it)
BODY = 0.02                              # the tube's radius
BODYX = WX - WHW + 0.002                 # the tube's half length (into the wheels' inner faces)
TAIL0 = (0.0, R - 0.008, -0.017)         # the tail: from the back of the tube ...
TAIL1 = (0.0, 0.006, -0.112)             # ... to its foot on the ground
WHIP0 = (BODYX - 0.008, R + BODY - 0.003, -0.004)   # the two whips: their roots on the tube's ends (x mirrored) ...
WHIP1 = (BODYX - 0.004, R + BODY + 0.122, -0.048)   # ... their tips, raked back (13 cm: 1.2 wheel heights)
DESIGN = os.environ.get('R6_DESIGN', 'tyre')   # (the alternatives compared: 'tyre', 'claw')
WIDTHS = list(range(10, 37))             # its widths on the street (px): Z 19.3 m .. 5.4 m
NPSI, NROLL = 9, 8
ROLL_STEP = math.radians(45)             # (a turn of 45 moves the tread on by a quarter lug (45 = 36 + 9): it reads as rolling forward, never
                                         # as a back-and-forth swap; the hub is plain (holes 90 apart would swap each turn); the marker goes round)

# materials: albedo (sRGB), class (0 matte, 1 satin, 2 glass, 3 metal, 4 own light)
MAT = {1: ((26, 26, 29), 0),     # tyre: the groove floor
       2: ((33, 33, 36), 0),     # tyre: the lugs
       3: ((24, 24, 27), 0),     # the tyre's sidewall
       4: ((33, 34, 38), 1),     # the hub (dark)
       5: ((10, 10, 11), 0),     # the hub's holes
       6: ((48, 50, 56), 3),     # the hub's cap (an axle's glint)
       7: ((34, 35, 40), 1),     # the tube (black anodized)
       8: ((28, 29, 33), 1),     # the tube's lower half, the tail
       9: ((40, 41, 46), 1),     # the camera's housing
       10: ((82, 84, 92), 3),    # the lens's bezel
       11: ((8, 10, 14), 2),     # the lens
       12: ((24, 24, 27), 0),    # the whips (rubber-coated, matte: a dark line; their tip caps glint)
       13: ((120, 255, 150), 4), # the status lights (green)
       14: ((22, 22, 25), 0),    # the tail's foot (rubber)
       15: ((92, 94, 100), 3),   # a marker on each tyre (a light dot near its rim: its turning shows)
       16: ((46, 46, 52), 3)}    # the whips' tip caps (their last 1.2 cm: a glint)
PRIO = {11: 6, 13: 6, 15: 4, 10: 3, 6: 2, 5: 1}
TAU = 2 * math.pi


class Hit:
    """the nearest hit per ray: its distance, normal, material"""
    def __init__(self, n):
        self.t = np.full(n, np.inf); self.n = np.zeros((n, 3)); self.m = np.zeros(n, int)

    def take(self, t, n, m, i):
        ok = np.isfinite(t) & (t > 1e-7) & (t < self.t[i]) & (m > 0)
        j = i[ok]; self.t[j] = t[ok]; self.n[j] = n[ok]; self.m[j] = m[ok]


def near(O, D, c, rb):
    """the rays passing within rb of c (each primitive is cast only for them)"""
    w = np.array(c, float) - O; d = w - (w * D).sum(1)[:, None] * D
    return np.nonzero((d * d).sum(1) < rb * rb)[0]


def frame(O, D, c, ax):
    """rays into a frame whose z is the axis ax (through c): local O, D and the matrix back"""
    z = np.array(ax, float); z /= np.linalg.norm(z)
    x = np.cross([0, 1, 0], z) if abs(z[1]) < 0.9 else np.cross([1, 0, 0], z); x /= np.linalg.norm(x); y = np.cross(z, x)
    M = np.stack([x, y, z], 1)
    return (O - np.array(c, float)) @ M, D @ M, M


def cyl(H, O, D, c, ax, r, z0, z1, side, cap0=None, cap1=None):
    """a finite cylinder along ax through c, local z from z0 to z1; side(P) / cap(P) -> material (0: no hit there)"""
    zz = np.array(ax, float) / np.linalg.norm(ax); i = near(O, D, np.array(c, float) + zz * (z0 + z1) / 2, math.hypot(r, (z1 - z0) / 2) + 1e-4)
    if not len(i): return
    o, d, M = frame(O[i], D[i], c, ax)
    a = d[:, 0] ** 2 + d[:, 1] ** 2; b = 2 * (o[:, 0] * d[:, 0] + o[:, 1] * d[:, 1]); cc = o[:, 0] ** 2 + o[:, 1] ** 2 - r * r
    disc = b * b - 4 * a * cc; ok = (disc >= 0) & (a > 1e-12); sq = np.sqrt(np.where(ok, disc, 0)); a2 = np.where(ok, 2 * a, 1)
    for t in ((-b + sq) / a2, (-b - sq) / a2):           # (the far one first: the near one wins the take)
        P = o + d * t[:, None]; inside = ok & (P[:, 2] >= z0) & (P[:, 2] <= z1)
        n = np.zeros_like(P); n[:, 0] = P[:, 0] / r; n[:, 1] = P[:, 1] / r
        m = side(P) * inside
        H.take(np.where(inside, t, np.inf), n @ M.T, m, i)
    for z, s, f in ((z0, -1.0, cap0), (z1, 1.0, cap1)):
        if f is None: continue
        dz = np.where(np.abs(d[:, 2]) > 1e-12, d[:, 2], 1e-12); t = (z - o[:, 2]) / dz
        P = o + d * t[:, None]; inside = P[:, 0] ** 2 + P[:, 1] ** 2 <= r * r
        n = np.zeros_like(P); n[:, 2] = s
        H.take(np.where(inside, t, np.inf), n @ M.T, f(P) * inside, i)


def obox(H, O, D, c, ax, up, half, mat):
    """an oriented box: centre c, its local z along ax (its y toward up), half sizes (x, y, z); mat(P, n) or an int"""
    z = np.array(ax, float); z /= np.linalg.norm(z); x = np.cross(up, z); x /= np.linalg.norm(x); y = np.cross(z, x)
    i = near(O, D, c, np.linalg.norm(half) + 1e-4)
    if not len(i): return
    M = np.stack([x, y, z], 1); o = (O[i] - np.array(c, float)) @ M; d = D[i] @ M
    hw = np.array(half, float); dd = np.where(np.abs(d) > 1e-12, d, 1e-12)
    t1 = (-hw - o) / dd; t2 = (hw - o) / dd; tn = np.minimum(t1, t2).max(1); tf = np.maximum(t1, t2).min(1)
    ok = (tn <= tf) & (tf > 0); k = np.minimum(t1, t2).argmax(1)
    n = np.zeros_like(o); n[np.arange(len(o)), k] = -np.sign(dd[np.arange(len(o)), k])
    P = o + d * tn[:, None]
    m = mat(P, n) if callable(mat) else np.full(len(o), mat)
    H.take(np.where(ok, tn, np.inf), n @ M.T, m, i)


def sphere(H, O, D, c, r, mat, cut=None):
    """a sphere (cut(P) False: no hit there, the far side seen through)"""
    i = near(O, D, c, r + 1e-4)
    if not len(i): return
    oc = O[i] - np.array(c, float); D = D[i]; b = 2 * (oc * D).sum(1); cc = (oc * oc).sum(1) - r * r; a = (D * D).sum(1)
    disc = b * b - 4 * a * cc; ok = disc >= 0; sq = np.sqrt(np.where(ok, disc, 0))
    for t in ((-b + sq) / (2 * a), (-b - sq) / (2 * a)):
        P = oc + D * t[:, None]; keep = ok & (cut(P) if cut else True)
        H.take(np.where(keep, t, np.inf), P / r, mat(P) * keep if callable(mat) else np.full(len(i), mat) * keep, i)


def wheel(H, O, D, s, roll):
    """one wheel (s: -1 its left, +1 its right): the tyre (its tread of lugs, its sidewalls), the hub, its holes, its cap"""
    cx = s * WX

    def lug(P):                                            # (local: z across the wheel, outward on both sides by the frame)
        a = np.mod(np.arctan2(P[:, 1], P[:, 0]) - roll, TAU)
        row = (P[:, 2] * s > 0).astype(float)              # the outer row half a lug round from the inner one
        ph = np.mod(a / (TAU / NLUG) + 0.5 * row, 1.0)
        on = (ph < 0.56) & (np.abs(np.abs(P[:, 2]) - WHW * 0.5) < WHW * 0.42)
        return np.where(on, 2, 0)
    # (the frame's z along the axle; its x, y round it: the angle and the roll in the wheel's own plane)
    cyl(H, O, D, (cx, R, 0), (1, 0, 0), R, -WHW + 0.003, WHW - 0.003, lug)

    def face(P):                                           # the sidewall, and its marker (one light dot by the rim)
        rr = np.hypot(P[:, 0], P[:, 1]); a = np.arctan2(P[:, 1], P[:, 0]) - roll
        mk = (np.abs(np.mod(a + math.pi, TAU) - math.pi) < 0.32) & (rr > 0.72 * R) & (rr < 0.9 * R)
        return np.where(rr > HUB, np.where(mk, 15, 3), 0)
    cyl(H, O, D, (cx, R, 0), (1, 0, 0), R - LUG, -WHW, WHW, lambda P: np.full(len(P), 1), face, face)

    def hub(P):                                            # a plain dark hub, its cap (the turning shows on the marker and the tread)
        rr = np.hypot(P[:, 0], P[:, 1])
        return np.where(rr < 0.3 * HUB, 6, 4)
    cyl(H, O, D, (cx, R, 0), (1, 0, 0), HUB, -WHW + 0.0025, WHW - 0.0025, lambda P: np.full(len(P), 4), hub, hub)


def claw_wheel(H, O, D, s, roll):
    """(the alternative compared: the Throwbot 2's own wheel, a holed disc with eight curved claws round it)"""
    cx = s * WX
    def disc(P):
        rr = np.hypot(P[:, 0], P[:, 1]); a = np.arctan2(P[:, 1], P[:, 0]) - roll
        hole = np.zeros(len(P), bool)
        for k in range(8):
            b = (k + 0.5) * TAU / 8; dx = rr * np.cos(a - b) - 0.62 * 0.68 * R; dy = rr * np.sin(a - b)
            hole |= dx * dx + dy * dy < (0.16 * R) ** 2
        return np.where(rr < 0.2 * R, 6, np.where(hole, 5, 4))
    cyl(H, O, D, (cx, R, 0), (1, 0, 0), 0.68 * R, -WHW * 0.5, WHW * 0.5, lambda P: np.full(len(P), 4), disc, disc)
    for k in range(8):                                      # each claw: three short blades along a hook, the wheel's thickness
        a0 = k * TAU / 8 + roll
        for j in range(3):
            r0 = 0.62 * R + j * 0.13 * R; r1 = r0 + 0.15 * R; b0 = a0 - 0.22 * j; b1 = a0 - 0.22 * (j + 1) - 0.05
            p0 = np.array([cx, R + r0 * math.sin(b0), -r0 * math.cos(b0)]); p1 = np.array([cx, R + r1 * math.sin(b1), -r1 * math.cos(b1)])
            ax = p1 - p0; L = np.linalg.norm(ax)
            obox(H, O, D, (p0 + p1) / 2, ax, (1, 0, 0), (0.0018, WHW * 0.95, L / 2 + 0.001), 2)


def drone(H, O, D, roll):
    for s in (-1, 1): (claw_wheel if DESIGN == 'claw' else wheel)(H, O, D, s, roll)
    cyl(H, O, D, (0, R, 0), (1, 0, 0), BODY, -BODYX, BODYX, lambda P: np.where(P[:, 1] < -0.35 * BODY, 8, 7))
    # the camera: a short round housing out of the tube's front, the bezel, the lens; the infrared emitters a strip over it
    face = lambda P: np.where(P[:, 0] ** 2 + P[:, 1] ** 2 < 0.0085 ** 2, 10, 9)   # (the lens itself: stamped, see render)
    cyl(H, O, D, (0, R + 0.001, 0), (0, 0, 1), 0.0115, 0.0, BODY + 0.006, lambda P: np.full(len(P), 9), None, face)
    # the tail: a flat bar from the tube's back to the ground (and a line under it, below), its foot a rubber pad
    t0, t1 = np.array(TAIL0), np.array(TAIL1); ax = t1 - t0; L = np.linalg.norm(ax)
    obox(H, O, D, (t0 + t1) / 2, ax, (0, 1, 0), (0.007, 0.003, L / 2), 8)
    obox(H, O, D, (0, 0.0055, t1[2] - 0.003), (0, 0, 1), (0, 1, 0), (0.012, 0.0055, 0.011), 14)
    for sx in (-1, 1):                                     # the whips' roots: short posts on the tube's ends
        cyl(H, O, D, (sx * WHIP0[0], WHIP0[1], WHIP0[2]), (0, 1, 0), 0.004, -0.004, 0.007, lambda P: np.full(len(P), 7), None, lambda P: np.full(len(P), 7))


# thin parts, drawn as whole-pixel lines (even steps, joined to the body): from, to, material; and the stamped lights: where, facing
LINES = [((sx * WHIP0[0], WHIP0[1] + 0.006, WHIP0[2]), (sx * WHIP1[0], WHIP1[1], WHIP1[2]), 12) for sx in (-1, 1)] + [(TAIL0, TAIL1, 8)]
STAMPS = [((0.0, R + 0.0125, BODY + 0.004), (0, 0.6, 0.8), 13), ((0.0, R + 0.012, -BODY + 0.001), (0, 0.5, -0.87), 13)]
LENS = ((0.0, R + 0.001, BODY + 0.006), (0, 0, 1))   # the lens: its centre, its axis
BOUND = ((-0.105, 0.0, -0.135), (0.105, R + BODY + 0.126, 0.03))
LENS2 = 24                               # (the lens two pixels by two from this width: 1.25 px across there)
W_OF = [0]                               # (the width being drawn)


def basis(psi, phi):
    """the eye's side psi (0: in front of the lens, +: round to its left), from phi above: view dir, screen right, up"""
    c = np.array([-math.sin(psi) * math.cos(phi), math.sin(phi), math.cos(psi) * math.cos(phi)])
    v = -c; r = np.cross([0, 1, 0], v); r /= np.linalg.norm(r); u = np.cross(v, r)   # (the street's axes are left-handed: x right, y up, z away)
    return v, r, u


def cell_box(s, phi):
    """a level's cell (w, h) and the ground point's px in it (ax, ay): every side's bound fits"""
    lo, hi = np.array(BOUND[0]), np.array(BOUND[1])
    pts = np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])
    X0 = Y0 = 1e9; X1 = Y1 = -1e9
    for k in range(64):
        v, r, u = basis(k * TAU / 64, phi)
        sx, sy = pts @ r * s, pts @ u * s
        X0, X1, Y0, Y1 = min(X0, sx.min()), max(X1, sx.max()), min(Y0, sy.min()), max(Y1, sy.max())
    ax = int(math.ceil(-X0)) + 1; ay = int(math.ceil(Y1)) + 1
    return ax + int(math.ceil(X1)) + 2, ay + int(math.ceil(-Y0)) + 2, ax, ay


def snap(n):
    """a normal (screen: x right, y up, z to the eye) to the nearest of a few: a painter's few tones on a round thing"""
    out = n.copy()
    q = np.round(n[..., :2] * 2.4) / 2.4
    l2 = (q ** 2).sum(-1)
    big = l2 > 1
    q[big] /= np.sqrt(l2[big])[:, None]
    out[..., :2] = q; out[..., 2] = np.sqrt(np.clip(1 - (q ** 2).sum(-1), 0, 1))
    return out


def render(s, psi, phi, roll, W, Hh, ax, ay):
    """one cell: each pixel's material (0: none) and its screen normal"""
    v, r, u = basis(psi, phi)
    jj, ii = np.mgrid[0:Hh * SS, 0:W * SS]
    px = (ii + 0.5) / SS; py = (jj + 0.5) / SS
    P0 = np.outer((px - ax).ravel() / s, r) + np.outer((ay - py).ravel() / s, u)
    O = P0 - v * 1.0; D = np.tile(v, (len(P0), 1))
    H = Hit(len(P0)); drone(H, O, D, roll)
    k = SS * SS
    mat = H.m.reshape(Hh, SS, W, SS).transpose(0, 2, 1, 3).reshape(Hh, W, k)
    nrm = H.n.reshape(Hh, SS, W, SS, 3).transpose(0, 2, 1, 3, 4).reshape(Hh, W, k, 3)
    dep = np.where(np.isfinite(H.t), H.t, np.nan).reshape(Hh, SS, W, SS).transpose(0, 2, 1, 3).reshape(Hh, W, k)
    nm = max(MAT) + 1
    cnt = np.stack([(mat == i).sum(2) for i in range(nm)], -1).astype(float); cnt[..., 0] = 0
    pr = np.array([PRIO.get(i, 0) for i in range(nm)], float)
    score = cnt + pr * k * 0.08 * (cnt >= k * 0.12)
    om = score.argmax(-1); best = np.take_along_axis(cnt, om[..., None], -1)[..., 0]
    cov = (mat > 0).mean(2)
    keep = (best > 0) & ((cov >= 0.5) | ((pr[om] >= 6) & (best >= k * 0.2)))
    om = np.where(keep, om, 0)
    sel = mat == om[..., None]
    on = (nrm * sel[..., None]).sum(2); on /= np.maximum(1e-9, np.linalg.norm(on, axis=-1, keepdims=True))
    od = np.where(keep, np.nansum(np.where(sel, dep, 0), 2) / np.maximum(1, sel.sum(2)), np.inf)
    sn = np.stack([on @ r, on @ u, on @ -v], -1)
    # thin parts: whole-pixel lines (one pixel thick, even steps), behind what is nearer
    proj = lambda p: (ax + np.dot(p, r) * s, ay - np.dot(p, u) * s, 1.0 + np.dot(np.array(p, float), v))
    for a, b, m in LINES:
        (xa, ya, ta), (xb, yb, tb) = proj(a), proj(b)
        if m == 12 and abs(xb - xa) < 1.5: xb = xa       # (a whip seen near end on: one straight column, never a one-pixel kink)
        dvec = np.array(b, float) - np.array(a, float); dvec /= np.linalg.norm(dvec)
        nl = np.cross(dvec, np.cross(-v, dvec)); nl = nl / np.linalg.norm(nl) if np.linalg.norm(nl) > 1e-9 else -v
        cap = 0.012 / np.linalg.norm(np.array(b, float) - np.array(a, float)) if m == 12 else 0   # (a whip's tip cap: its last 1.2 cm)
        for x, y, f in line_px(xa, ya, xb, yb):
            t = ta + (tb - ta) * f
            if 0 <= x < W and 0 <= y < Hh and (om[y, x] == 0 or t < od[y, x]):
                om[y, x] = 16 if f >= 1 - cap - 1e-9 and cap else m; od[y, x] = t; sn[y, x] = [nl @ r, nl @ u, max(0.0, nl @ -v)]
    om = clean(om)
    om, sn = join(om, sn)
    sn = snap(sn)
    # the lens and the status lights, last, by one rule for every size and wheel turn: where each faces the eye and the tyres
    # (whole cylinders: never their lugs) leave it in sight; the lens one pixel, two by two from LENS2 px wide; each light one pixel
    def put(p, fc, m, n):
        fv = np.array(fc, float); fv /= np.linalg.norm(fv)
        if fv @ -v < 0.2 or not seen(p, v): return
        x, y, t = proj(p); xi, yi = int(math.floor(x - (n - 1) / 2)), int(math.floor(y - (n - 1) / 2))
        if n == 1 and not (0 <= xi < W and 0 <= yi < Hh and om[yi, xi]):   # (off the body's edge by a sample: onto its nearest pixel)
            c = [(abs(xx + 0.5 - x) + abs(yy + 0.5 - y), xx, yy) for yy in range(yi - 1, yi + 2) for xx in range(xi - 1, xi + 2) if 0 <= xx < W and 0 <= yy < Hh and om[yy, xx]]
            if c: _, xi, yi = min(c)
        for yy in range(yi, yi + n):
            for xx in range(xi, xi + n):
                if 0 <= xx < W and 0 <= yy < Hh and om[yy, xx]:
                    om[yy, xx] = m; sn[yy, xx] = snap(np.array([[fv @ r, fv @ u, fv @ -v]]))[0]
    put(LENS[0], LENS[1], 11, 2 if W_OF[0] >= LENS2 else 1)
    for p, fc, m in STAMPS: put(p, fc, m, 1)
    return om, sn


def seen(p, v):
    """is the point p in sight from the eye (along -v): not behind either tyre (a whole cylinder, its lugs aside)"""
    O = np.array([p], float) - v * 0.0005; D = np.array([-v], float); H = Hit(1)
    for s in (-1, 1): cyl(H, O, D, (s * WX, R, 0), (1, 0, 0), R, -WHW, WHW, lambda P: np.full(len(P), 1), lambda P: np.full(len(P), 1), lambda P: np.full(len(P), 1))
    return not np.isfinite(H.t[0])


def line_px(xa, ya, xb, yb):
    """the pixels of a line from point a to point b (Bresenham between their pixels: even steps), with each one's place along it"""
    x0, y0, x1, y1 = int(math.floor(xa)), int(math.floor(ya)), int(math.floor(xb)), int(math.floor(yb))
    dx, dy = abs(x1 - x0), -abs(y1 - y0); sx, sy = (1 if x1 > x0 else -1), (1 if y1 > y0 else -1); e = dx + dy; n = max(dx, -dy, 1); out = []
    x, y = x0, y0
    while True:
        out.append((x, y, len(out) / n))
        if x == x1 and y == y1: break
        e2 = 2 * e
        if e2 >= dy: e += dy; x += sx
        if e2 <= dx: e += dx; y += sy
    return out


def parts(m):
    """the 8-connected pieces of a cell: a label per pixel, each piece's size"""
    H, W = m.shape; lab = np.zeros((H, W), int); sizes = []
    for y0 in range(H):
        for x0 in range(W):
            if not m[y0, x0] or lab[y0, x0]: continue
            n = len(sizes) + 1; st = [(y0, x0)]; lab[y0, x0] = n; c = 0
            while st:
                y, x = st.pop(); c += 1
                for yy in (y - 1, y, y + 1):
                    for xx in (x - 1, x, x + 1):
                        if 0 <= yy < H and 0 <= xx < W and m[yy, xx] and not lab[yy, xx]: lab[yy, xx] = n; st.append((yy, xx))
            sizes.append(c)
    return lab, sizes


def join(m, sn):
    """one shape: a stray piece (a whip's tip, a tail's end the cast lost a sample of) tied back to the body by a line of its own
    material, a single stray pixel dropped"""
    lab, sizes = parts(m)
    if len(sizes) <= 1: return m, sn
    main = int(np.argmax(sizes)) + 1; mp = np.argwhere(lab == main)
    for k in range(1, len(sizes) + 1):
        if k == main: continue
        pts = np.argwhere(lab == k)
        if len(pts) <= 1: m[lab == k] = 0; continue
        d = ((pts[:, None, :] - mp[None, :, :]) ** 2).sum(-1); i, j = np.unravel_index(d.argmin(), d.shape)
        (y0, x0), (y1, x1) = pts[i], mp[j]
        for x, y, f in line_px(x0 + 0.5, y0 + 0.5, x1 + 0.5, y1 + 0.5):
            if not m[y, x]: m[y, x] = m[y0, x0]; sn[y, x] = sn[y0, x0]
    assert len(parts(m)[1]) == 1
    return m, sn


def clean(m):
    """lone pixels off (a thin line's pixels keep their diagonal neighbours), one-pixel notches filled"""
    H, W = m.shape; o = m.copy()
    for y in range(H):
        for x in range(W):
            n8 = [(m[yy, xx]) for yy in (y - 1, y, y + 1) for xx in (x - 1, x, x + 1) if (yy, xx) != (y, x) and 0 <= yy < H and 0 <= xx < W]
            n4 = [m[yy, xx] for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)) if 0 <= yy < H and 0 <= xx < W]
            if m[y, x] and not any(n8): o[y, x] = 0
            if not m[y, x] and len(n4) == 4 and all(n4): o[y, x] = max(set(n4), key=n4.count)
    return o


def build_drone():
    blocks, levels = [], []
    for w in WIDTHS:
        s = w / WIDTH; Z = 959.5 / s; phi = math.atan(1.38 / Z); W_OF[0] = w
        cw, ch, ax, ay = cell_box(s, phi)
        Aa = np.zeros((ch * NPSI, cw * NROLL, 4), np.uint8); Na = np.zeros_like(Aa)
        for k in range(NPSI):
            for f in range(NROLL):
                m, sn = render(s, k * TAU / 16, phi, f * ROLL_STEP, cw, ch, ax, ay)
                r0, c0 = k * ch, f * cw
                for y, x in zip(*np.nonzero(m)):
                    alb, cls = MAT[int(m[y, x])]
                    Aa[r0 + y, c0 + x] = (*alb, 255)
                    Na[r0 + y, c0 + x] = (round(127.5 + 127.5 * sn[y, x, 0]), round(127.5 + 127.5 * sn[y, x, 1]), cls * 40, 255)
        blocks.append((Aa, Na)); levels.append([w, round(s, 3), cw, ch, ax, ay])
    AW = 1024; x = y = sh = 0; pos = []                     # (shelves)
    for Aa, _ in blocks:
        h, wd = Aa.shape[:2]
        if x + wd > AW: x = 0; y += sh; sh = 0
        pos.append((x, y)); x += wd; sh = max(sh, h)
    AH = y + sh
    AT = np.zeros((AH, AW, 4), np.uint8); NT = np.zeros_like(AT)
    for (Aa, Na), (px, py), L in zip(blocks, pos, levels):
        AT[py:py + Aa.shape[0], px:px + Aa.shape[1]] = Aa; NT[py:py + Na.shape[0], px:px + Na.shape[1]] = Na; L += [px, py]
    return AT, NT, {'size': [AW, AH], 'L': levels}


# ---- the wall camera (metres; world axes: X right, Y up, Z away from the eye; its origin the wall point it is screwed to) ----
CAM_KIND = os.environ.get('R6_CAM', 'wall')      # (the alternatives compared: 'wall' (flat on the wall), 'bracket' (on a short arm), 'ceiling' (under the soffit))
CAM_TONE = os.environ.get('R6_TONE', 'white')    # (its housing: 'white' or 'dark')
CAM_PAD = 24                                     # (it is cast in a square this far round its wall point, then cropped to it, 1 px round)
CAM_P = (5.0, 3.32, 7.84)                        # the wall point: the bracket's top, 2 px under the eave's lit lower edge (the right facades' plane X 5.0 m)
CAM_K = 1.35                                     # (its size: a 12.4 cm base, a 9 cm dome: an outdoor mini dome; 15 px tall there)
CAMMAT = {1: ((206, 208, 214) if CAM_TONE == 'white' else (58, 60, 66), 1),   # the housing
          2: ((176, 178, 184) if CAM_TONE == 'white' else (46, 48, 54), 1),   # the bracket, the base's lip
          3: ((20, 22, 30), 2),                                               # the smoked dome
          4: ((6, 7, 10), 2),                                                 # the lens behind it
          5: ((40, 12, 14), 2),                                               # the infrared ring behind it (dull red when lit)
          6: ((255, 60, 50), 4),                                              # the status light
          7: ((8, 10, 14), 2),                                                # the lens's glint (its light: a layer of its own)
          8: ((20, 22, 30), 2)}                                               # the dome's highlight (the same)


def cam_model(H, O, D):
    ld = np.array([-0.62, -0.42, -0.66]); ld /= np.linalg.norm(ld)   # where its lens looks: down the street, toward the eye's side
    if CAM_KIND == 'wall':                                                # (its base flat on the wall, the dome out toward the street: d03, d08-d10)
        k = CAM_K
        cyl(H, O, D, (0, -0.045 * k, 0), (1, 0, 0), 0.046 * k, -0.022 * k, 0.0, lambda P: np.full(len(P), 1), lambda P: np.full(len(P), 2), lambda P: np.full(len(P), 1))
        dc = np.array([-0.022, -0.045, 0.0]) * k
        sphere(H, O, D, dc, 0.033 * k, 3, cut=lambda P: P[:, 0] < 0.0005)
        return dc, ld
    if CAM_KIND == 'ceiling':
        c = np.array([-0.07, -0.0, 0.0])                               # (a base on the soffit, 7 cm out from the wall)
        cyl(H, O, D, c - [0, 0.018, 0], (0, 1, 0), 0.046, 0.0, 0.018, lambda P: np.full(len(P), 1), lambda P: np.full(len(P), 2), lambda P: np.full(len(P), 1))
        dc = c - np.array([0, 0.018, 0])
    else:
        obox(H, O, D, (-0.006, -0.03, 0.0), (1, 0, 0), (0, 1, 0), (0.006, 0.036, 0.022), 2)          # the wall plate
        obox(H, O, D, (-0.05, 0.0, 0.0), (1, 0, 0), (0, 1, 0), (0.045, 0.007, 0.02), 2)             # the arm out
        c = np.array([-0.085, -0.007, 0.0])
        cyl(H, O, D, c - [0, 0.026, 0], (0, 1, 0), 0.045, 0.0, 0.026, lambda P: np.full(len(P), 1), lambda P: np.full(len(P), 2), lambda P: np.full(len(P), 1))
        dc = c - np.array([0, 0.026, 0])
    sphere(H, O, D, dc, 0.033, 3, cut=lambda P: P[:, 1] < 0.0005)
    return dc, ld


def cam_parts():
    """the small parts, stamped on their pixel after the cast: the lens (behind the glass, on its axis), three infrared LEDs round
    it, the status light on the housing's side toward the street"""
    k = CAM_K if CAM_KIND == 'wall' else 1.0
    dc = np.array([-0.07, -0.018, 0.0]) if CAM_KIND == 'ceiling' else np.array([-0.022, -0.045, 0.0]) * k if CAM_KIND == 'wall' else np.array([-0.085, -0.033, 0.0])
    ld = np.array([-0.62, -0.42, -0.66]); ld /= np.linalg.norm(ld)
    lens = dc + ld * 0.024 * k
    e1 = np.cross(ld, [0, 1, 0]); e1 /= np.linalg.norm(e1); e2 = np.cross(ld, e1)
    ir = [dc + ld * 0.02 * k + 0.016 * k * (math.cos(a) * e1 + math.sin(a) * e2) for a in (0.0, 2.1, 4.2)]
    eye = np.array([-0.54, 0.0, -0.84])
    led = dc + np.array([0.012, 0.03, -0.03]) * k if CAM_KIND == 'wall' else dc + np.array([0, 0.012 if CAM_KIND == 'ceiling' else 0.02, 0]) + eye * 0.046
    return lens, ir, led


def build_cam():
    """its cell: each pixel's material and normal (the eye's view of it: from the lens 1.41 m up, across the street)"""
    eye = np.array([0.0, 1.41, 0.0]); P = np.array(CAM_P); v = P - eye; dist = np.linalg.norm(v); v /= dist
    s = 959.5 / P[2]
    r = np.cross([0, 1, 0], v); r /= np.linalg.norm(r); u = np.cross(v, r)
    # the wall point's px (perspective, as the street's), the square round it
    X0, Y0 = int(math.floor(700 + 959.5 * P[0] / P[2])) - CAM_PAD, int(math.floor(615 - 959.5 * (P[1] - 1.41) / P[2])) - CAM_PAD
    wx = 700 + 959.5 * P[0] / P[2] - X0; wy = 615 - 959.5 * (P[1] - 1.41) / P[2] - Y0
    W = Hh = 2 * CAM_PAD
    jj, ii = np.mgrid[0:Hh * SS, 0:W * SS]
    px = (ii + 0.5) / SS; py = (jj + 0.5) / SS
    P0 = np.outer((px - wx).ravel() / s, r) + np.outer((wy - py).ravel() / s, u)
    O = P0 - v * 1.0; Dd = np.tile(v, (len(P0), 1))
    Hit_ = Hit(len(P0)); cam_model(Hit_, O, Dd)
    k = SS * SS
    mat = Hit_.m.reshape(Hh, SS, W, SS).transpose(0, 2, 1, 3).reshape(Hh, W, k)
    nrm = Hit_.n.reshape(Hh, SS, W, SS, 3).transpose(0, 2, 1, 3, 4).reshape(Hh, W, k, 3)
    nm = max(CAMMAT) + 1
    cnt = np.stack([(mat == i).sum(2) for i in range(nm)], -1).astype(float); cnt[..., 0] = 0
    pr = np.array([{4: 3, 6: 6, 5: 1}.get(i, 0) for i in range(nm)], float)
    om = (cnt + pr * k * 0.08 * (cnt >= k * 0.12)).argmax(-1); best = np.take_along_axis(cnt, om[..., None], -1)[..., 0]
    keep = (best > 0) & (((mat > 0).mean(2) >= 0.5) | ((om == 6) & (best >= k * 0.15)))
    om = np.where(keep, om, 0)
    sel = mat == om[..., None]; on = (nrm * sel[..., None]).sum(2); on /= np.maximum(1e-9, np.linalg.norm(on, axis=-1, keepdims=True))
    om = clean(om)
    # the stamps: each part's pixel, where what covers it there is the part's carrier (the glass, the housing)
    proj = lambda p: (int(math.floor(wx + np.dot(np.array(p) - 0, r) * s)), int(math.floor(wy - np.dot(np.array(p), u) * s)))
    lens, ir, led = cam_parts()
    lx, ly = proj(lens); dome = lambda x, y: 0 <= x < W and 0 <= y < Hh and om[y, x] == 3
    for x, y in ((lx, ly), (lx + 1, ly)):                 # the lens: two pixels on its axis
        if dome(x, y): om[y, x] = 4
    if dome(lx - 1, ly + 1): om[ly + 1, lx - 1] = 5       # the infrared LEDs: at this size one dull dot by the lens (not a ring: with
    # the highlight and the status light a ring read as a face)
    ys, xs = np.nonzero(om == 3)                           # the dome's highlight: one pixel in from its upper-left edge
    if len(xs):
        cx, cy = xs.mean(), ys.mean(); k = np.argmin((xs - cx) + (ys - cy)); hx, hy = xs[k] + 1, ys[k] + 1
        if dome(hx, hy): om[hy, hx] = 8
    x, y = proj(led)
    if 0 <= x < W and 0 <= y < Hh and om[y, x] in (1, 2): om[y, x] = 6
    ys, xs = np.nonzero(om); y0, y1, x0, x1 = ys.min() - 1, ys.max() + 2, xs.min() - 1, xs.max() + 2
    return om[y0:y1, x0:x1], on[y0:y1, x0:x1], (r, u, -v), (X0 + x0, Y0 + y0)


lin = lambda c: (np.asarray(c, float) / 255.0) ** 2.2
srgb = lambda c: np.clip(np.power(np.clip(c, 0, None), 1 / 2.2) * 255, 0, 255)
CAM_DN = (40, 50, 78)                            # the light on it from below (the street; its faces down) as the frame's face under it takes it
CAM_UP = (6, 9, 14)                              # from above (the eave's deep shadow)
CAM_ARC = (200, 90, 170)                         # the arcade's light (its opening below and right of it), on what faces it: x 0.09
CAM_ARCD = (0.55, -0.6, 0.58)                    # (its direction, screen: right, down, toward the eye)
CAM_AMB = (30, 31, 40)                           # the street's and the sky's light on the white housing (graded by the page with the street)
CAM_SH = 0.16                                    # (the eave's shadow on the housing: about twice the wall under it, not a lamp)
CAM_RIM = (96, 92, 140)                          # its rim toward the opening: the eave's tiles and the sky (lavender), the arcade's pink only at its foot


def bake_cam():
    """its six cells: ambient (graded by the page as the street's sprites), the arcade's light (on the housing's rim toward the opening
    its lightest value), its status light, its infrared LEDs, the street's lights on its dome (one highlight, upper left), the status
    light's glow round it (for its beat on narrow views); the last five added"""
    om, on, (r, u, f), at = build_cam()
    h, w = om.shape; L = [np.zeros((h, w, 4)) for _ in range(6)]
    edge = lambda y, x: any(not (0 <= y + dy < h and 0 <= x + dx < w) or om[y + dy, x + dx] == 0 for dy, dx in ((0, 1), (1, 0), (1, 1)))
    dn, up, arc = lin(CAM_DN), lin(CAM_UP), lin(CAM_ARC) * 0.07; ad = np.array(CAM_ARCD); ad /= np.linalg.norm(ad)
    for y, x in zip(*np.nonzero(om)):
        m = int(om[y, x]); alb, cls = CAMMAT[m]; a = lin(alb); n = on[y, x]; ns = np.array([n @ r, n @ u, n @ f])
        # from below and before it (the street): what faces down and toward the street; up, and back toward the wall: the eave's dark
        E = dn * max(0, -ns[1]) * (0.35 + 0.65 * max(0, ns[2])) + dn * 0.35 * max(0, ns[2]) * (1 - max(0, ns[1])) + up * max(0, ns[1])
        col = a * E
        if m in (1, 2): col = a * (E * 2.2 + lin(CAM_AMB)) * CAM_SH                        # (a white housing: the street's light off it, the sky's; in the eave's shadow)
        if m in (3, 4, 5, 7, 8): col = a * E * 0.6 + dn * 0.4 * (1 - max(0, ns[2])) ** 3 * max(0, -ns[1] + 0.3)   # the smoked glass: dark, a thin rim below
        if m == 6: col = lin(CAMMAT[1][0]) * (E * 2.2 + lin(CAM_AMB)) * CAM_SH             # (the light, off: the housing round it)
        L[0][y, x, :3] = srgb(col); L[0][y, x, 3] = 255
        # (the page adds its light layers on the screen's own values: each is baked as what the light adds there, over this pixel)
        add = lambda k: np.clip(srgb(col + k) - srgb(col), 0, 255)
        k = (0.15 if m in (3, 4, 5) else 0) * max(0, ns @ ad) ** 2 * arc                  # (the glass's faint sheen; the housing lit on its rim only)
        if m in (1, 2) and edge(y, x) and ns @ ad > 0.05: k = k + a * lin(CAM_RIM if y < h - 3 else CAM_ARC) * 0.05   # (its rim toward the opening: one row)
        L[1][y, x, :3] = add(k); L[1][y, x, 3] = 255 if k.max() > 0 else 0
        if m == 6:
            L[2][y, x, :3] = add(lin(alb)); L[2][y, x, 3] = 255
            for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):                            # its glow, on what is round it (the wall too)
                if 0 <= y + dy < h and 0 <= x + dx < w: L[5][y + dy, x + dx, :3] = srgb(lin((150, 24, 20))); L[5][y + dy, x + dx, 3] = 255
        if m == 5: L[3][y, x, :3] = add(lin((80, 10, 14))); L[3][y, x, 3] = 255
        if m == 8: L[4][y, x, :3] = add(lin((196, 200, 222))); L[4][y, x, 3] = 255     # (the dome's highlight: near white)
    g = [(y, x) for y, x in zip(*np.nonzero(om)) if int(om[y, x]) in (3, 4, 5, 7, 8)]   # (the glass: three flat steps, as the painting's own)
    if g:
        lum = np.array([L[0][y, x, :3] @ (0.3, 0.59, 0.11) for y, x in g]); cut = np.quantile(lum, [1 / 3, 2 / 3]); k = np.searchsorted(cut, lum)
        for j in range(3):
            sel = [p for p, kk in zip(g, k) if kk == j]
            if sel: m = np.mean([L[0][y, x, :3] for y, x in sel], 0); [L[0][y, x].__setitem__(slice(0, 3), m) for y, x in sel]
    return np.concatenate([np.round(l).astype(np.uint8) for l in L], 1), at, (w, h)


# ---- the screen's casing (a handheld monitor: matte black, screwed; its keys), as pixel sprites the page shows at 2 CSS px a pixel
# (9-slice: border-image): r6_panel.webp 24 x 24 (corners 8), r6_bezel.webp the screen's bezel 12 x 12 (4), r6_key.webp a key 12 x 12
# (4), r6_key_on.webp the key lit (its camera on screen), r6_ant.webp an antenna stub 4 x 16 ----
UI = {'o': (5, 5, 7), 'L': (58, 58, 66), 'l': (42, 42, 48), 'b': (29, 29, 34), 'd': (19, 19, 23), 'D': (12, 12, 15), 's': (74, 74, 82), 'S': (8, 8, 10),
      'k': (44, 44, 50), 'K': (66, 66, 74), 'p': (255, 138, 209), 'P': (255, 196, 228), 'q': (186, 84, 146), 'g': (34, 34, 39)}
UI_PANEL = ["....oooooooooooooooo....",
            "..ooLLLLLLLLLLLLLLLLoo..",
            ".oLLllllllllllllllllddo.",
            ".oLlbbbbbbbbbbbbbbbbbdo.",
            "oLlbbsSbbbbbbbbbbbbsSbdo",
            "oLlbbSSbbbbbbbbbbbbSSbdo",
            "oLlbbbbbbbbbbbbbbbbbbbdo",
            "oLlbbbbbbbbbbbbbbbbbbbdo"] + ["oLlbbbbbbbbbbbbbbbbbbbdo"] * 8 + [
            "oLlbbbbbbbbbbbbbbbbbbbdo",
            "oLlbbbbbbbbbbbbbbbbbbbdo",
            "oLlbbsSbbbbbbbbbbbbsSbdo",
            "oLlbbSSbbbbbbbbbbbbSSbdo",
            ".oldbbbbbbbbbbbbbbbbbddo",
            ".odddddddddddddddddddDo.",
            "..ooDDDDDDDDDDDDDDDDoo..",
            "....oooooooooooooooo...."]
UI_BEZEL = ["oooooooooooo", "oddddddddddo", "odSSSSSSSSdo", "odS......Sdo"] + ["odS......Sdo"] * 4 + ["odS......Sdo", "odSSSSSSSSdo", "oLLLLLLLLLLo", "oooooooooooo"]
UI_KEY = [".oooooooooo.", "oKKKKKKKKKKo", "oKkkkkkkkkko", "oKkkkkkkkkko"] + ["oKkkkkkkkkko"] * 4 + ["oKkkkkkkkkko", "oggggggggggo", "oDDDDDDDDDDo", ".oooooooooo."]
UI_LIT = [".oooooooooo.", "oPPPPPPPPPPo", "oPppppppppqo", "oPppppppppqo"] + ["oPppppppppqo"] * 4 + ["oPppppppppqo", "oqqqqqqqqqqo", "oqqqqqqqqqqo", ".oooooooooo."]
UI_ANT = [".oo.", "oLlo", "oLlo", "oLdo", ".oo.", ".oo.", "olbo", "olbo", "olbo", "olbo", "olbo", "olbo", "olbo", "oldo", "oddo", "oooo"]


def ui_img(rows):
    img = np.zeros((len(rows), len(rows[0]), 4), np.uint8)
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch != '.': img[y, x] = (*UI[ch], 255)
    return img


def main():
    for name, rows in (('r6_panel', UI_PANEL), ('r6_bezel', UI_BEZEL), ('r6_key', UI_KEY), ('r6_key_on', UI_LIT), ('r6_ant', UI_ANT)):
        Image.fromarray(ui_img(rows), 'RGBA').save(A(name + '.webp'), 'WEBP', **SV)
    CA, at, (cw, ch) = bake_cam()
    Image.fromarray(CA, 'RGBA').save(A('r6_cam.webp'), 'WEBP', **SV)
    print(json.dumps({'cam': [int(at[0]), int(at[1]), cw, ch]}))
    if os.environ.get('R6_CAM_ONLY'): return
    AT, NT, lay = build_drone()
    Image.fromarray(AT, 'RGBA').save(A('r6_drone.webp'), 'WEBP', **SV)
    Image.fromarray(NT, 'RGBA').save(A('r6_drone_n.webp'), 'WEBP', **SV)
    print(json.dumps(lay, separators=(',', ':')))


if __name__ == '__main__':
    main()
