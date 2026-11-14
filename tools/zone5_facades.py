#!/usr/bin/env python3
"""The three houses between the right cherry tree and the ramen shop: each its own wall, and signs of life.

    python3 tools/zone5_facades.py      (once, on the layers as painted: it checks the zone and refuses to run twice)

The row of right-side buildings behind the lamp's arm and the pole (A, the narrow far one, x 908-940; B, three floors
and Red's balcony, x 941-1022; C, behind the pole, its lit curtained window, x 1066-1121) were three clones in the
same grey concrete. Each now has a wall of its own, traditional or residential, as on the owner's references: A small
glazed tiles (the owner's tex_tiles, a lavender grey in this light; on the narrow pier by the door only their joints
along the rays), B dark horizontal weatherboards (shitamiita, as on ref_house_trad 5 to 8), C dark vertical planks
with the battens behind their seams (the owner's tex_wood_planks: its ten boards' own tones). (Compared, in tools'
VARIANTS: B tiled with A in weatherboards; A in plaster; B in plaster. The dark wood on B, the largest and the most
seen, makes the block the traditional street of the references, and the light tiles on the narrow A set it apart;
plaster read as the old concrete, only paler.)
Since 2026-11-13 B is one plaster from its roof to the sidewalk (the owner): tools/redraw_zones.py, zone bwall, runs
walls() here for B alone with plaster() and lays it over these weatherboards. Since 2026-11-14 A is gone: a side alley
in its place (tools/roji_alley.py, zone alley); its mailbox, door, windows and walls with it, the plant on the sidewalk kept.

Where a building's wall was one concrete, it is one material now: every pixel of the wall, the parapet, the strips
between the openings and the floors, the lintels and the spandrels, carries the pattern; the projecting elements
(cornice, ledges between the floors, the canopies over Red's door and the second-floor window, the shop's ledge, the
plinth) carry the same material's tone, flat, with their own light (lit top, face, dark underside), as a trim board or
a tiled band would; the parapets have sheet-metal caps (C's painted cap retinted). Only what is not wall stays as
painted: the windows, their frames, reveals, sills and rails, the doors, the shop front, the downpipe and its clamps,
B's lit left arris, A's dark outline on the tree, and everything in front (the pole, the lamp's arm, its drop and its
plate, the ramen's side sign). The pattern lies on each facade's plane, on the facades' measured vanishing point
(700, 615) (B's parapet and C's ledges run within 0-2 px of it; the street's VP 669, 568 fits none of them): its rows
along the rays (v = (615 - y) / (x - 700) constant), its columns spaced as the depth along the street is
(Zd = 4800 / (x + 0.5 - 700) m, the scene's ground model: f 959.5 px, the facades 5 m from the eye's line), one
coordinate system per facade, so joints and boards run on behind the openings and the trims.

Its light is the painter's: each surface's own shading, taken from the painted concrete along its rays (a bilateral
filter that follows the rays: the lit lips and the shadows stay, the light keeps its gradient, the concrete's stains
go; what went with the old, the shutter box's lit lip, is filled from above and below first), times the material's
albedo relative to the concrete, times a tenth of the painter's own grain. In the power cut (street_unlit) each changed
pixel is darkened as the painted wall was there (the ratio of the two layers' shading, per channel); so the red night,
which reads the lights as the street over its power cut, finds the same lights. Where a lit window's overlay
(win_z1_top, win_z1_violet, win_z1_warm) covers wall beside its window (the room's light on it), the overlay's pixels
take the same change (written back to those overlays).

Signs of life, in the scene's perspective (the camera of the ground model, the eye 1.41 m up), lit by the light they
stand in (laundry dried indoors behind B's second-floor window was tried, render_laundry, LAUNDRY_ON: at this size its
tee read as a figure standing at the window, so it is left out); A's lit window a shoji behind its glass (its paper an
even warm cream at the curtained windows' value, its kumiko dark wood every 0.45 m by 0.30 m, the window's sash two
pixels heavy in front; dark in the power cut); A's rolling shutter its sliding lattice door (koshi-do: warm brown
cedar slats on the facade's rays, two thirds slat and a third gap, the slat's edge toward the lamp lit, the warm glow
of the hall through frosted glass between them (none in the power cut), a kick board, a mid rail, a lintel, the
shutter's guides its jambs); A's mailbox, a stainless box on the pier right of its door (modelled and projected: its
face, its end, its lid, a slot); left of A's door a leafy plant in a terracotta pot (sheet 3), the sprite brought to
the scene's pixel size by the commonest of its own colours over each pixel (no averaging), its contrast lowered to the
dusk; and a city bicycle (mamachari: a cream step-through frame, black tyres, a saddle, swept bars with grips, steel
fenders over the wheels' tops, a chain case, a basket of upright black wires in front) parked along B's shutter
(parallel to the wall, on the facade's rays; left of the painter's bucket), modelled in metres and projected (its
wheels ellipses on their own plane), the pink of B's lit entrance on its edge facing it (in the street's layer only).
A shade on the ground round each foot; under them wet.webp is dry (the ground around stays wet, so the wet pass
mirrors them). In the power cut what stands on the sidewalk darkens as the wall behind it does in the rendered frames
(CUT_K, CUT_ADD: the painter's layers are alike at the foot of the walls, the lit states' extra light there is the
engine's, added over all); the bicycle is muted (a 24-inch one, its lit side toward the lamp, its shadow side away),
the pot's lip lit with a darker band under it. Weathering on A and B: rain streaks under the sills, the ledges and the
canopies' ends, a darker splash band at the foot of the walls, a rust tint under the caps. B's weatherboards are drawn
as the painter draws the left house's: under each lap's dark line a lit band, a duller middle, the lip lit again; they
run the facade's whole width (no butt joints at this scale); the lap's dark line as thick across a steep ray as along
it (solid, not dotted); the wood's value drifts gently (DRIFT: B lighter by its lit arris, darker toward the pole and
under its cap; C's planks each wandering slowly up the wall); C's boards have a lit edge toward the lamp beside each
seam. night_far: 20 wall pixels that were coded as the tree's mass (160) are the street's (0) now; street_sun (0 here)
does not change.
Sources in tools/src/: zone5_sheet1.jpg, zone5_sheet2.webp, zone5_sheet3.webp (the owner's sprite sheets as given: the
pots are cut from them, the mailbox's and the bicycle's colours measured on them), zone5_tiles.jpg and
zone5_wood_planks.jpg (the owner's textures: their tones and proportions measured into tiles() and WOOD_T).
Needs Pillow, numpy, scipy.
"""
import argparse
import json
import os
import re
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A_ = lambda p: os.path.join(ROOT, 'assets', p)
H, W = 816, 1456
VPX, VPY = 700.0, 615.0              # the right facades' vanishing point (measured on B's parapet, C's ledges)
XS = 5.0                             # their distance from the eye's line (m): a height Y = XS v
KD = 4800.0                          # depth along the street: Zd = KD / (x + 0.5 - 700) m (f 959.5 px x 5 m)
ZONE = (60, 705, 905, 1123)          # the zone's box (y0, y1, x0, x1): nothing outside it changes
ZONE_SKIP = (1022, 1069)             # (its columns under the pole, which other scripts change: not in the check)
ZONE_SHA = '26a3d7bc843fb88a'        # its painted pixels before this script (so it never runs twice on them)


def zone_sha(city):
    import hashlib
    y0, y1, x0, x1 = ZONE; z = city[y0:y1, x0:x1].astype(np.uint8).copy()
    z[:, ZONE_SKIP[0] - x0:ZONE_SKIP[1] - x0] = 0
    return hashlib.sha1(np.ascontiguousarray(z).tobytes()).hexdigest()[:16]

YY, XX = np.mgrid[0:H, 0:W]
XC, YC = XX + 0.5, YY + 0.5
with np.errstate(divide='ignore', invalid='ignore'):
    V = (VPY - YC) / (XC - VPX)      # each pixel's ray (constant along a line through the VP)


def yv(x, v):                        # the row (float) of ray v at column x
    return VPY - v * (np.asarray(x, float) + 0.5 - VPX) - 0.5


# ---- the facades, in (x, v): R a box of columns x0..x1 and rays v0..v1, S a box on screen, PS a polygon on screen
def R(x0, x1, v0, v1): return ('r', x0, x1, v0, v1)
def S(x0, x1, y0, y1): return ('s', x0, x1, y0, y1)
def PS(*pts): return ('ps', list(pts))
def P(*pts): return ('p', list(pts))


BLD = {   # out: the facade; keep: not wall (as painted); cap: the parapet's metal cap; trim: projecting ledges and hoods
          # (their lit tops, faces and undersides: the material's own tone, flat); tint: retinted as painted
  'A': dict(out=[R(908, 940, -0.2555, 1.2335)], cap=[R(908, 940, 1.190, 1.2335)],
            trim=[R(908, 940, 0.771, 0.832), R(908, 940, 0.347, 0.402)],              # the two ledges
            erase=[R(912, 936, 0.314, 0.325)],                                         # the old shutter box's lit lip
            keep=[R(908, 908, -0.2555, 1.19),                                          # its dark outline on the tree
                  R(912, 935, 0.884, 1.153), R(911, 935, 0.884, 0.907),      # the top window, its reveal, frame, sill
                  R(912, 935, 0.459, 0.737),                                 # the lit window, its lit reveal, frame, sill
                  R(912, 935, -0.2295, 0.2515), R(935, 935, -0.2295, 0.260)]),   # the shutter and its guides
  'B': dict(out=[R(941, 1022, -0.283, 1.6085)], cap=[R(941, 1022, 1.5765, 1.6085)],
            trim=[R(941, 1022, 1.372, 1.414),                                          # the cornice under the parapet
                  P((950, 1.361), (1022, 1.361), (1022, 1.284), (962, 1.284), (950.5, 1.334)),   # the door's canopy
                  R(941, 1022, 0.8715, 0.9075),                                        # the floor ledge
                  P((951, 0.861), (1022, 0.861), (1022, 0.801), (964, 0.801), (952, 0.836)),     # the window's canopy
                  R(941, 1022, 0.390, 0.4245), R(941, 957, -0.283, -0.258)],           # the shop's ledge, the plinth
            keep=[R(941, 941, -0.283, 1.5765),                                         # its lit left arris
                  R(944, 946, -0.283, 1.6085),                                         # the downpipe
                  S(943, 943, 554, 554), S(943, 943, 623, 623), S(943, 943, 682, 682),   # its clamps' outer ends
                  R(964, 1003, 0.942, 1.283), R(963, 963, 0.942, 1.10),      # Red's door, its reveal, frame and rail
                  R(1007, 1022, 0.991, 1.283), R(1006, 1022, 0.991, 1.0005),  # the narrow window, its reveal and sill
                  R(964, 1003, 0.467, 0.801), R(963, 963, 0.467, 0.62),      # the second floor's window and rail
                  R(1007, 1022, 0.5235, 0.801), R(1006, 1022, 0.5235, 0.531),  # the violet window, its reveal and sill
                  R(957, 998, -0.283, 0.395), R(999, 1004, 0.16, 0.395),     # the shop front, its recess,
                  R(1005, 1022, -0.283, 0.395)]),                            # the lit entrance (the pier between: wall)
  'C': dict(out=[R(1066, 1121, 0.39, 2.0)],                                  # (to its corner's dark line, x 1122)
            tint=[S(1066, 1121, 66, 69)],                                    # its coping: the wall's tone, no joints
            trim=[R(1066, 1121, 1.226, 1.302), R(1066, 1121, 0.850, 0.8985), R(1066, 1121, 0.3955, 0.4185)],   # ledges
            keep=[S(1066, 1122, 0, 65),
                  R(1080, 1108, 0.962, 1.199),                               # the top window and its sill
                  R(1081, 1108, 0.494, 0.797), R(1080, 1110, 0.494, 0.4995),   # the lit window, its reveal, frame, sill
                  R(1066, 1122, -0.40, 0.3955),                              # the ground floor: the door, its awning
                  PS((1109.5, 413), (1112, 405), (1116, 400), (1123, 396), (1123, 463), (1109.5, 463))]),  # ramen's sign
}
SHADE = {'A': dict(sr=8, sv=0.7, sc=7), 'B': dict(sr=10, sv=0.7, sc=7), 'C': dict(sr=10, sv=0.7, sc=12)}
TRIM_GRAIN = {'A': 0.0, 'B': 0.04, 'C': 0.04}   # (wood trims: faint streaks along the board)
CAP = 1.0                            # the parapets' sheet-metal caps (kasagi), relative to the concrete
DRIFT = {   # a gentle drift of the wood's value over the wall, as the painter's boards have: B lighter by its lit left
            # arris, darker toward the pole and under its cap; C each plank's tone wandering slowly up the wall
  'B': lambda: (1.08 - 0.14 * np.clip((XX - 941) / 81, 0, 1)) * (1 - 0.10 * np.clip(1 - (1.5765 - V) / 0.12, 0, 1)),
  'C': lambda: 1 + 0.06 * np.sin(YY / 37.0 + 6.28 * h2(np.floor(np.nan_to_num(ZCOL, posinf=0, neginf=0) / 0.18).astype(np.int64)[None, :], 7, 5))}
GRAIN = 0.1                          # how much of the painter's own grain stays on the new walls
ARM_AXIS = [(974, 168.5), (984, 169.0), (990, 169.8), (995, 171.0), (1000, 172.6), (1004, 175.0), (1007.5, 178.5),
            (1010.0, 183.5), (1010.5, 222.0)]   # the lamp's arm over B, its curve and its drop (scene px)
ARM_PLATE = S(1013, 1022, 178, 223)  # its plate on the pole


def shape(s):
    if s[0] == 'r':
        _, x0, x1, v0, v1 = s; return (XX >= x0) & (XX <= x1) & (V >= v0) & (V <= v1)
    if s[0] == 's':
        _, x0, x1, y0, y1 = s; return (XX >= x0) & (XX <= x1) & (YY >= y0) & (YY <= y1)
    pts = np.array(s[1], float); x0, x1 = int(pts[:, 0].min()) - 1, int(pts[:, 0].max()) + 1
    X = XC[:, x0:x1 + 1]; Q = (YC if s[0] == 'ps' else V)[:, x0:x1 + 1]; inside = np.zeros(X.shape, bool)
    for (ax, ay), (bx, by) in zip(pts, np.roll(pts, -1, 0)):        # (even-odd, pixel centres)
        cond = (ay > Q) != (by > Q)
        with np.errstate(divide='ignore', invalid='ignore'):
            xi = ax + (Q - ay) * (bx - ax) / (by - ay)
        inside ^= cond & (X < xi)
    m = np.zeros((H, W), bool); m[:, x0:x1 + 1] = inside; return m


def union(shapes):
    m = np.zeros((H, W), bool)
    for s in shapes: m |= shape(s)
    return m


def load(p, mode='RGBA'):
    return np.asarray(Image.open(p).convert(mode)).astype(float)


def lum(a): return a[..., :3] @ np.array([0.299, 0.587, 0.114])


# ---- what is in front: the pole (its occlusion runs in street.js), the lit windows' overlays, the lamp's arm
def front_mask(city, js=None):
    s = open(js or A_('street.js'), encoding='utf-8').read()
    m = np.zeros((H, W), bool)
    for a, b, c, d in json.loads(re.search(r'const COCC = (\{.*?\});', s).group(1))['pole']['runs']: m[a:b + 1, c:d + 1] = True
    return m | arm_mask(city, union(BLD['B']['out']) & (city[:, :, 3] > 250) & ~m)


def arm_mask(city, region, rad=3.6, core=1.6, tol=7.0):
    # a corridor round the arm's axis; in it, the pixels that do not continue the wall along their own ray are the arm's
    d = np.full((H, W), 1e9); P = np.array(ARM_AXIS)
    for (ax, ay), (bx, by) in zip(P[:-1], P[1:]):
        vx, vy = bx - ax, by - ay; t = np.clip(((XC - ax) * vx + (YC - ay) * vy) / (vx * vx + vy * vy), 0, 1)
        d = np.minimum(d, np.hypot(XC - (ax + t * vx), YC - (ay + t * vy)))
    T = d <= rad; C3 = city[:, :, :3]; out = np.zeros((H, W), bool)
    for y, x in zip(*np.where(T & region)):
        if d[y, x] <= core: out[y, x] = True; continue
        v = V[y, x]; samp = []
        for sgn in (-1, 1):
            k = 0; xx = x
            while k < 2:
                xx += sgn; yy = int(round(yv(xx, v)))
                if not (0 <= yy < H) or not region[yy, xx] or abs(xx - x) > 12: break
                if not T[yy, xx]: samp.append(C3[yy, xx]); k += 1
        if not samp or np.abs(C3[y, x] - np.median(np.array(samp), 0)).max() > tol: out[y, x] = True
    return out | (shape(ARM_PLATE) & region)


def masks(name, city, front):
    b = BLD[name]; out = union(b['out']) & (city[:, :, 3] > 250) & ~front
    keep = union(b['keep'] + b.get('tint', []) + b.get('cap', []) + b.get('trim', [])) & out
    return out & ~keep


# ---- the painter's light on a wall: a bilateral filter along each pixel's own ray (sr px), across it (sv rows) and in
# luminance (sc levels), over the wall's pixels only
def bilat(img, mask, sr, sv, sc, guide=None):
    rr = int(np.ceil(2.5 * sr)); rv = int(np.ceil(2.5 * sv))
    ys, xs = np.nonzero(mask); y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1   # (the wall's own box)
    G = lum(img) if guide is None else guide; g0 = G[y0:y1, x0:x1]; m = mask.astype(float)
    Xb, Vb = XX[y0:y1, x0:x1], V[y0:y1, x0:x1]
    acc = np.zeros((y1 - y0, x1 - x0, img.shape[2])); ws = np.zeros((y1 - y0, x1 - x0))
    for dx in range(-rr, rr + 1):
        xn = np.clip(Xb + dx, 0, W - 1); yc = yv(xn, Vb)
        for dr in range(-rv, rv + 1):
            w = np.exp(-0.5 * (dx / sr) ** 2 - 0.5 * (dr / sv) ** 2)
            if w < 1e-4: continue
            yn = np.clip(np.round(yc + dr).astype(int), 0, H - 1)
            ww = w * m[yn, xn] * np.exp(-0.5 * ((G[yn, xn] - g0) / sc) ** 2)
            acc += ww[..., None] * img[yn, xn]; ws += ww
    out = img.copy(); out[y0:y1, x0:x1] = acc / np.maximum(ws, 1e-9)[..., None]
    return out


# ---- materials: relative albedo maps (the new wall's albedo over the concrete's), in facade coordinates
def h2(a, b, s=0):                   # a stable hash in [0, 1)
    a = np.asarray(a, np.int64); b = np.asarray(b, np.int64)
    h = (a * 374761393 + b * 668265263 + s * 2246822519 + 12345) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFFFF) / float(1 << 24)


def lumn(c): c = np.asarray(c, float); return c / (c @ [0.299, 0.587, 0.114])
def chroma(rgb, k): return 1 + k * (lumn(rgb) - 1)
XS_ = np.arange(W)
with np.errstate(divide='ignore', invalid='ignore'):
    ZCOL = KD / (XS_ + 0.5 - VPX)    # each column's depth along the street (m)


def first_rows(f):                   # each column's topmost row of each band of floor(f) (f grows upward)
    n = np.floor(f).astype(np.int64); return n != np.roll(n, 1, axis=0), n


def first_cols(fz):                  # the first column of each band of floor(fz)
    n = np.floor(fz).astype(np.int64); return np.r_[False, n[1:] != n[:-1]], n


def tiles(st=0.13, sz=0.30, y0=0.0, z0=0.0, face=1.55, gh=0.80, gv=0.90, tvar=0.05, top=1.05, ch=0.55, stain=0.82, hue=(1, 1, 1),
          seed=5):
    # small glazed tiles (tex_tiles): rows st m high along the rays, columns sz m deep; the grout (a joint row on each
    # tile's top, a joint column on its far side), a tone per tile, a third of them stained (a few browner pixels), each
    # tile's top row catching the sky
    Y = V * XS; gr, r = first_rows((Y - y0) / st); gc, c = first_cols((ZCOL - z0) / sz)
    gc2 = np.broadcast_to(gc[None, :], gr.shape); key = r * 7919 + c[None, :]
    A = (face * (1 + tvar * (2 * h2(key, 3, seed) - 1)))[..., None] * chroma([164, 137, 95], ch)
    A[np.roll(gr, 1, axis=0) & ~gr] *= top
    sm = (h2(key, 9, seed) < 0.33) & (h2(XX * 31 + YY, 17, seed) < 0.45) & ~gr & ~gc2
    A[sm] *= stain * chroma([150, 112, 72], ch) / chroma([164, 137, 95], ch)
    A[gc2] = face * gv * chroma([120, 100, 70], ch)
    A[gr] = face * gh * chroma([90, 78, 52], ch)
    return A * lumn(hue)


def hboards(hb=0.21, y0=0.0, bat=0.91, z0=0.0, dark=0.72, shadow=0.50, under=0.86, lip=1.14, tvar=0.06, butt=3.64,
            grain=0.05, ch=0.6, tone=(46, 44, 46), batlit=1.16, batside=0.70, battens=True, profile=False, seed=3):
    # horizontal weatherboards (shitamiita): boards hb m high along the rays; a dark row under each board's lip, the
    # lip's edge lit; butt joints staggered; a grain of short streaks along the boards; battens (oshibuchi) every bat m
    Y = V * XS; fr, m = first_rows((Y - y0) / hb)
    seg = np.floor((ZCOL[None, :] + h2(m, 11, seed) * butt) / butt).astype(np.int64)
    t = dark * (1 + tvar * (2 * h2(m * 31 + seg, 5, seed) - 1))
    q = np.floor((Y - y0) / (hb / 4)).astype(np.int64)                 # (four grain bands a board, along the rays)
    g = h2(np.floor((XX + h2(q, 13, seed) * 6) / 6).astype(np.int64) * 131 + q, 19, seed)
    t = t * np.where(g < 0.15, 1 - grain, np.where(g > 0.88, 1 + grain, 1.0))
    A = t[..., None] * chroma(tone, ch)
    if profile:                                  # (as the painter draws the left house's boards: under the dark line of
        f = (Y - y0) / hb; up = f - np.floor(f)  # the lap a lit band, a duller middle, the lip lit again above the next)
        hp = hb * (XX + 0.5 - VPX) / XS; dtop = (1 - up) * hp; dbot = up * hp
        lw = np.maximum(1.0, 0.68 * np.sqrt(1 + V * V))  # (the lap's line as thick across as along a steep ray: solid, not dotted)
        k = np.where(dtop < lw, shadow, np.where(dtop < lw + 2, PROF[0], np.where(dbot < 1, PROF[2], np.where(dbot < 2.5, PROF[1], PROF[3]))))
        A *= k[..., None]
    else:
        A[fr] *= shadow
        A[np.roll(fr, 1, axis=0) & ~fr] *= under
        A[np.roll(fr, -1, axis=0) & ~fr] *= lip
    A[(seg != np.roll(seg, 1, axis=1)) & ~fr] *= 0.72
    if battens:
        bc, _ = first_cols((ZCOL - z0) / bat)
        A[np.broadcast_to(bc[None, :], fr.shape)] = dark * batlit * chroma(tone, ch)
        A[np.broadcast_to(np.r_[False, bc[:-1]][None, :], fr.shape)] = dark * batside * chroma(tone, ch)
    return A


PROF = (1.22, 1.08, 1.42, 0.88)        # (the board's top band, its lower band, its lip, its middle)


WOOD_T = np.array([[28.6, 31.1, 38.4], [33, 31.7, 36.1], [31.4, 30.8, 36.2], [41.4, 40.6, 43.5], [13.8, 16.9, 21.8],
                   [28.2, 30.7, 38.2], [54.2, 50.4, 48.7], [82.9, 75, 67.6], [30.5, 32.1, 38.6], [35.2, 35.1, 38.4]])
# (the ten boards of the owner's tex_wood_planks, their mean colours)


def vplanks(bw=0.18, bp=0.63, bh=0.09, y0=0.3, z0=0.0, dark=0.95, seam=0.42, tc=0.6, ch=0.6, grain=0.06, batlit=1.5,
            nail=1.0, edge=1.0, seed=1):
    # vertical planks (tex_wood_planks): boards bw m wide with the texture's ten tones (their spread halved), a dark seam
    # column, the battens behind every bp m seen in the seams, a nail on each board at each batten; vertical grain
    Y = V * XS; sc, n = first_cols((ZCOL - z0) / bw)
    tone = WOOD_T[np.mod(n * 7 + 3, 10)]; lt = tone @ [0.299, 0.587, 0.114]
    t = dark * (1 + tc * (np.clip(lt / 37.0, 0.6, 1.5) - 1)) * (1 + 0.08 * (2 * h2(n, 3, seed) - 1))   # (its own tone)
    col = 1 + ch * (tone / lt[:, None] - 1)
    A = np.ones((H, W, 3)) * (t[:, None] * col)[None, :, :]
    run = np.floor((Y * 40 + h2(XS_, 7, seed)[None, :] * 5) / 5).astype(np.int64)
    g = h2(XS_[None, :] + 0 * run, run, seed + 1)
    A *= np.where(g < 0.16, 1 - grain, np.where(g > 0.86, 1 + grain, 1.0))[..., None]
    fb = (Y - y0) / bp; bat = (fb - np.floor(fb)) * bp < bh
    scm = np.broadcast_to(sc[None, :], bat.shape)
    A[scm] *= seam; A[scm & bat] *= batlit
    lit = np.broadcast_to(np.r_[False, sc[:-1]][None, :], bat.shape) & ~scm   # (each board's edge toward the street lamp)
    A[lit] *= edge
    zc = (ZCOL - z0) / bw; mid = np.abs(zc - np.floor(zc) - 0.5) <= 0.5 * np.abs(np.gradient(zc)) + 1e-9
    nr, _ = first_rows((Y - y0 - bh * 0.5) / bp)
    A[nr & mid[None, :] & ~scm] *= nail
    return A


def plaster(face=1.75, amp=0.03, tone=(228, 220, 204), ch=0.45, seed=7):
    rng = np.random.default_rng(seed)
    from scipy.ndimage import gaussian_filter
    n = gaussian_filter(rng.standard_normal((H, W)), (1.5, 2.5)); n /= n.std()
    return (face * (1 + amp * n))[..., None] * chroma(tone, ch)


TILES = dict(st=0.15, sz=0.35, ch=0.7, face=1.6, gh=0.72, gv=0.86)
TILES2 = dict(st=0.15, sz=0.35, ch=0.0, face=1.26, gh=0.62, gv=0.78, top=1.10)   # (a light glazed tile, neutral)
HUE = {'A': (1.45, 1.0, 1.08)}       # (A's light is painted teal: where it is, its tiles turn the lavender grey the painter
# gives light walls in that light, as beyond A; its lavender highlights stay as they are)
VARIANTS = {   # (the alternatives compared; v1 is the one kept, see the docstring)
  'v1': {'A': lambda: hboards(), 'B': lambda: tiles(**TILES), 'C': lambda: vplanks()},
  'v2': {'A': lambda: plaster(), 'B': lambda: hboards(), 'C': lambda: tiles(**TILES)},
  'v3': {'A': lambda: tiles(**TILES), 'B': lambda: hboards(), 'C': lambda: vplanks()},
  'v4': {'A': lambda: hboards(), 'B': lambda: plaster(), 'C': lambda: vplanks()},
  'v5': {'A': lambda: plaster(), 'B': lambda: hboards(), 'C': lambda: vplanks()},
  'v6': {'A': lambda: tiles(**TILES2), 'B': lambda: hboards(battens=False, dark=0.82, butt=1e6, profile=True, tvar=0.09), 'C': lambda: vplanks(z0=0.18, edge=1.15)},
  'v7': {'A': lambda: hboards(), 'B': lambda: tiles(**TILES2), 'C': lambda: vplanks()},
}
VARIANT = 'v6'


def hue_fix(S, hue):
    # a per-channel tint, at its full strength where the painter's light is teal (green over red), fading to none where
    # it is already lavender (red at or over green)
    l = np.maximum(lum(S), 1.0); w = np.clip((S[:, :, 1] - S[:, :, 0]) / (0.45 * l), 0, 1)[..., None]
    return lumn(hue) ** w


AGE = {   # per building: rain streak sources (x, v of the element's underside), the splash band's height (m), the caps' v
  'A': dict(streaks=[(911, 0.884), (912, 0.884), (934, 0.884), (911, 0.459), (934, 0.459), (920, 0.771), (930, 0.347)],
            splash=0.45, cap=1.190),
  'B': dict(streaks=[(952, 0.836), (963, 0.467), (964, 0.467), (1002, 0.467), (1007, 0.991), (1007, 0.5235), (1015, 0.5235),
                     (958, 0.8715), (975, 0.8715), (996, 0.8715), (950, 1.334), (990, 1.372), (944, 0.390)],
            splash=0.45, cap=1.5765),
}


def age_map(name):
    a = AGE[name]; f = np.ones((H, W, 3)); hgt = EYE + XS * V
    band = np.clip(hgt / a['splash'], 0, 1)                            # (the splash band: darker toward the foot)
    f *= (0.82 + 0.18 * band ** 0.7)[..., None]
    for i, (x, v) in enumerate(a['streaks']):                          # (a streak: one column dark, its neighbour less,
        y0 = int(np.ceil(yv(x, v))); n = int(12 + 14 * h2(i, x, 47))   # fading over n px)
        for k in range(n):
            t = 1 - k / n
            for dx, amp in ((0, 0.20), (1, 0.09)):
                if 0 <= y0 + k < H: f[y0 + k + (1 if dx and k % 3 == 0 else 0), x + dx] *= 1 - amp * t ** 1.3
    cap = (V < a['cap']) & (V > a['cap'] - 4.0 / np.maximum(XX + 0.5 - VPX, 1))   # (the 4 px under the cap: a rust tint)
    f[cap] *= np.array([1.06, 0.99, 0.94])
    return f


def walls(city, unlit, variant=VARIANT, js=None):
    front = front_mask(city, js)
    out_c, out_u = city.copy(), unlit.copy(); changed = np.zeros((H, W), bool); shades = {}
    for name, mat in VARIANTS[variant].items():
        wall = masks(name, city, front)
        er = union(BLD[name].get('erase', [])) & wall
        if er.any():                                 # (what went with the old: the wall's own value from above and below)
            city, unlit = city.copy(), unlit.copy()
            for y, x in zip(*np.nonzero(er)):
                for Lr in (city, unlit):
                    nb = [Lr[int(round(yv(x, V[y, x] + dv))), x, :3] for dv in (-0.016, 0.016)]
                    Lr[y, x, :3] = 0.5 * (nb[0] + nb[1])
        Sc = bilat(city[:, :, :3], wall, **SHADE[name])
        Su = bilat(unlit[:, :, :3], wall, guide=lum(city), **SHADE[name])
        A = mat()
        if name == 'A':                              # (its narrow pier right of the door: the joints along the rays only,
            A[:, 935:941] = tiles(**dict(TILES2, gv=1.0))[:, 935:941]   # its columns too close at this depth to draw)
        if name in DRIFT: A = A * DRIFT[name]()[..., None]
        new = Sc * A * ((city[:, :, :3] + 1) / (Sc + 1)) ** GRAIN
        if name in HUE: new = new * hue_fix(Sc, HUE[name])
        ratio = np.clip((Su + 0.5) / (Sc + 0.5), 0, 1.2)
        out_c[wall, :3] = new[wall]; out_u[wall, :3] = new[wall] * ratio[wall]
        tm = union(BLD[name].get('tint', [])) & (city[:, :, 3] > 250) & ~front & ~wall
        if tm.any():                                 # (trims the material wraps: its mean tone over the painted one)
            k = np.median(new[wall] / np.maximum(Sc[wall], 1), 0)
            out_c[tm, :3] = city[tm, :3] * k; out_u[tm, :3] = unlit[tm, :3] * k
        cm = union(BLD[name].get('cap', [])) & (city[:, :, 3] > 250) & ~front & ~wall
        if cm.any():                                 # (the parapet's cap: sheet metal, the painter's light on it, no grain)
            Cc = bilat(city[:, :, :3], cm, sr=12, sv=0.5, sc=6); Cu = bilat(unlit[:, :, :3], cm, guide=lum(city), sr=12, sv=0.5, sc=6)
            g = (1 + 0.02 * (2 * h2(XX, YY, 37) - 1))[..., None]
            out_c[cm, :3] = (Cc * CAP * g)[cm]; out_u[cm, :3] = (Cu * CAP * g)[cm]
        tr = union(BLD[name].get('trim', [])) & (city[:, :, 3] > 250) & ~front & ~union(BLD[name]['keep']) & ~wall & ~cm & ~tm
        if tr.any():                                 # (the ledges and hoods: the material's own tone, flat, on their light)
            St = bilat(city[:, :, :3], tr, sr=12, sv=0.5, sc=8); Sut = bilat(unlit[:, :, :3], tr, guide=lum(city), sr=12, sv=0.5, sc=8)
            alb = np.median(A[wall], 0)
            q = np.floor(V * 300).astype(np.int64)                         # (streaks along the rays)
            g = (1 + TRIM_GRAIN[name] * (2 * h2(np.floor((XX + 7 * h2(q, 3, 43)) / 6).astype(np.int64), q, 41) - 1))[..., None]
            k = alb * g * ((city[:, :, :3] + 1) / (St + 1)) ** GRAIN
            if name in HUE: k = k * hue_fix(St, HUE[name])
            out_c[tr, :3] = (St * k)[tr]; out_u[tr, :3] = (Sut * k)[tr]
        ag = (wall | tr) & ~cm
        if name in AGE and ag.any():                 # (weathering: rain streaks under sills and slabs, the splash band
            f = age_map(name)                        # at the foot, a rust tint under the caps)
            out_c[ag, :3] *= f[ag]; out_u[ag, :3] *= f[ag]
        changed |= wall | tm | cm | tr; shades[name] = (wall, Sc)
    return out_c, out_u, changed, shades, front


# ---- signs of life, drawn from the owner's sprite sheets (tools/src/zone5_sheet*), each placed in the scene's
# own perspective (the camera of the ground model: f = KD / XS px, the eye 1.41 m up) and lit by the light it stands in
SRC = lambda p: os.path.join(ROOT, 'tools', 'src', p)
FOC, EYE = KD / XS, 1.41
ALB = 0.45                           # the concrete's albedo: a sprite's colour / 255 / ALB is its albedo relative to it
SPRITE_LIT = 1.25                    # the light on what stands on the sidewalk, over the wall's at its foot
POT_LIT = np.array([1.0, 0.95, 0.88])   # (the plant by A's door: the Center's warm light from the left on it)
CUT_K, CUT_ADD = 0.41, 17.0          # the wall at B's foot renders L 32 at dusk (13.4 painted + the lamp's additive air) and 13
                                     # in the cut: what stands there drops to CUT_K x (its painted value + CUT_ADD) at most
RIM_X0, RIM_K = 945, 1.0             # B's lit entrance's rim on them: from x RIM_X0, its strength at the door


def sheet(n):
    return np.asarray(Image.open(SRC(n)).convert('RGB')).astype(float)


def cut(img, box, tol=24):
    # a sprite out of its sheet (box x0, y0, x1, y1): opaque but where the white paper reaches from the box's border
    from scipy import ndimage
    x0, y0, x1, y1 = box; a = img[y0:y1, x0:x1]
    lab, n = ndimage.label(np.abs(a - 255).max(2) <= tol)
    edge = set(np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]])) - {0}
    return np.dstack([a, (~np.isin(lab, list(edge))).astype(float)])


def kpal(rgba, k=10, seed=0):
    # the sprite's own palette (k colours of its opaque pixels, k-means)
    px = rgba[rgba[:, :, 3] > 0.5][:, :3]; rng = np.random.default_rng(seed)
    c = px[rng.choice(len(px), k, replace=False)].copy()
    for _ in range(20):
        d = ((px[:, None, :] - c[None, :, :]) ** 2).sum(2); l = d.argmin(1)
        for j in range(k):
            if (l == j).any(): c[j] = px[l == j].mean(0)
    return c


def grade(rgb, sat=0.6, con=0.75):
    # a sprite's colours brought to the scene's dusk: their saturation and their own lighting's contrast lowered
    l = (rgb @ np.array([0.299, 0.587, 0.114]))[..., None]; m = 110.0
    return np.clip((m + (l - m) * con) + (rgb - l) * sat * con, 0, 255)


def render_frontal(lay, mask, X, Z, hb, hm, spr, pal, light, over=None, sat=0.6):
    # an upright thing facing the street (a pot, a plant): its foot at depth Z, X m from the eye's line, hb m up, hm m
    # tall, at its own distance's scale (FOC / Z px a metre); each pixel the commonest of the sprite's own colours over
    # its footprint (the art's crisp colours, no averaging), drawn where the sprite covers half of it
    k = FOC / Z; h, w = spr.shape[:2]; ph = hm * k; pw = ph * w / h
    cx = VPX + FOC * X / Z; by = VPY + FOC * (EYE - hb) / Z
    x0, x1 = int(np.floor(cx - pw / 2)), int(np.ceil(cx + pw / 2)); y0, y1 = int(np.floor(by - ph)), int(np.ceil(by))
    idx = ((spr[..., None, :3] - pal) ** 2).sum(-1).argmin(-1)          # the sprite on its palette
    op = spr[..., 3] > 0.5
    for y in range(y0, y1):
        for x in range(x0, x1):
            u0, u1 = (x - (cx - pw / 2)) / pw, (x + 1 - (cx - pw / 2)) / pw
            w0, w1 = (y - (by - ph)) / ph, (y + 1 - (by - ph)) / ph
            a0, a1 = int(np.clip(np.floor(u0 * w), 0, w)), int(np.clip(np.ceil(u1 * w), 0, w))
            b0, b1 = int(np.clip(np.floor(w0 * h), 0, h)), int(np.clip(np.ceil(w1 * h), 0, h))
            if a1 <= a0 or b1 <= b0: continue
            o = op[b0:b1, a0:a1]
            if o.mean() < 0.5 or (over is not None and over[y, x]): continue
            ids = idx[b0:b1, a0:a1][o]
            col = pal[np.bincount(ids, minlength=len(pal)).argmax()]
            lt = light[y, x] if light.ndim == 3 else light
            lay[y, x, :3] = grade(col[None, :], sat=sat, con=0.8)[0] / 255.0 / ALB * lt; lay[y, x, 3] = 255; mask[y, x] = True
    return (x0, y0, x1, y1)


def garment(kind, U, Wv):
    # a garment's cloth in its own (u across, w down) square: inside, and the light on it (the sky from above: the top
    # and the folds' crests lit, the hem and the side away in shade); stripes for the towel
    au = np.abs(U - 0.5)
    if kind == 'tee':
        ins = ((au <= 0.30) & (Wv >= 0)) | ((au <= 0.5) & (Wv >= 0.03 + 0.10 * (au - 0.30) / 0.2) & (Wv <= 0.30 - 0.06 * (au - 0.30) / 0.2))
        ins &= ~((au < 0.09) & (Wv < 0.05))
    elif kind == 'trousers':
        ins = (au <= 0.42) & ~((au < 0.05) & (Wv > 0.32))
    elif kind == 'shirt':
        ins = ((au <= 0.32) & (Wv >= 0)) | ((au <= 0.5) & (Wv >= 0.03 + 0.08 * (au - 0.32) / 0.18) & (Wv <= 0.50 - 0.05 * (au - 0.32) / 0.18))
    else:
        ins = (U >= 0) & (U < 1) & (Wv >= 0) & (Wv < 1)
    ins &= (U >= 0) & (U < 1) & (Wv >= 0) & (Wv < 1)
    t = 1.0 + 0.14 * np.clip(1 - Wv / 0.25, 0, 1) - 0.14 * Wv + 0.05 * np.cos(U * 2 * np.pi * 1.5 + Wv * 3)
    t = t - 0.10 * (U > 0.78)                                        # (the side away from the street's light)
    stripe = np.zeros_like(ins)
    if kind == 'towel':
        stripe = ((Wv > 0.74) & (Wv < 0.80)) | ((Wv > 0.85) & (Wv < 0.89)) | ((U > 0.14) & (U < 0.26))
    if kind == 'shirt':
        stripe = (np.abs(U - 0.5) < 0.06) & (Wv > 0.08)                  # (its button placket)
    return ins, t, stripe


def render_laundry(lay, mask, L, city, unlit, u):
    # laundry dried indoors (heya-boshi, as it is at night and in the rain): a tee, trousers and a towel on hangers from
    # the curtain rail just inside B's second-floor window, L['X'] m from the eye's line, seen only through the glass
    # (its frames and the balcony's rail stay in front): each pixel the glass's own value (its sky reflection) dimmed or
    # lifted by the cloth behind it, tinted by the cloth's colour; in the power cut the room is dark, they only darken it
    x0, y0, x1, y1 = L['box']; X, ph = L['X'], L['rail']; n = 4
    sx = (np.arange(n) + 0.5) / n
    xs = np.arange(x0, x1)[None, :, None, None] + sx[None, None, None, :]
    ys = np.arange(y0, y1)[:, None, None, None] + sx[None, None, :, None]
    Z = FOC * X / (xs - VPX); hh = EYE + (VPY - ys) * Z / FOC
    alb = np.zeros((y1 - y0, x1 - x0, 3)); cov = np.zeros((y1 - y0, x1 - x0), bool)
    for kind, za, zb, length, c0, c1 in L['items']:
        U = (za - Z) / (za - zb); Wv = (ph - 0.04 - hh) / length
        ins, t, st = garment(kind, U, Wv)
        c = np.where(st[..., None], np.asarray(c1, float), np.asarray(c0, float)) * t[..., None]
        a = ins.astype(float); cv = a.mean((2, 3))
        cc = (c * a[..., None]).sum((2, 3)) / np.maximum(a.sum((2, 3)), 1e-9)[..., None]
        put = cv >= 0.5; alb[put] = cc[put]; cov |= put
        zz = 0.5 * (za + zb); xp = int(np.floor(VPX + FOC * X / zz)); yp = int(np.floor(VPY + FOC * (EYE - ph) / zz))
        if x0 <= xp < x1 and y0 <= yp < y1 and not cov[yp - y0, xp - x0]: alb[yp - y0, xp - x0] = (40, 40, 48); cov[yp - y0, xp - x0] = True
    glass = union(L['glass']) & (lum(city) > 14) & ~union(L['not_glass'])
    on = cov & glass[y0:y1, x0:x1]
    a = alb / 255.0; la = (a @ np.array([0.299, 0.587, 0.114]))[..., None]
    k = (0.40 + 0.85 * la) * (a / np.maximum(la, 1e-3)) ** 0.6           # (dimmed or lifted, and tinted, by the cloth)
    sub = lay[y0:y1, x0:x1]; su = u[y0:y1, x0:x1]
    sub[on, :3] = city[y0:y1, x0:x1][on][:, :3] * k[on]
    su[on, :3] = unlit[y0:y1, x0:x1][on][:, :3] * k[on] * 0.8
    mask[y0:y1, x0:x1] |= on
    return on


LAUNDRY = dict(X=5.30, rail=5.55, box=(958, 360, 1008, 470),             # inside B's second-floor window
               glass=[R(964, 1003, 0.467, 0.801)], not_glass=[R(962, 1004, 0.583, 0.600)],   # (the balcony rail's top)
               items=[('tee', 18.80, 18.20, 0.66, (168, 84, 66), (168, 84, 66)),     # (a rust-red tee, dark trousers,
                      ('trousers', 17.95, 17.50, 0.95, (54, 56, 70), (54, 56, 70)),  # a white towel with a band, as on
                      ('towel', 17.32, 16.98, 0.62, (226, 222, 212), (150, 140, 130))])   # sheet 2's rack)
POTS = [  # (sheet, box, X m from the eye's line, depth Zd m, height m, saturation): on the sidewalk at the walls' feet
    ('zone5_sheet3.webp', (902, 148, 1047, 356), 4.86, 22.36, 0.62, 1.0),   # a leafy plant in a terracotta pot, left of A's door
]


SHOJI = dict(cols=[(912, 916), (918, 928), (930, 934)], v=(0.4865, 0.7075), kz=0.45, kh=0.30, lift=1.0, cream=(255, 200, 184))   # A's lit window: its panes


def shoji(c, u, city, unlit, lm):
    # A's lit window: behind its glass a shoji, its paper lit by the room (the window's own warm light, evened, a little
    # brighter at mid height), its kumiko lattice dark against it (bars every kz m along the street, every kh m up); with
    # the power out, the paper as dark as the window was
    v0, v1 = SHOJI['v']; Y = V * XS
    win = np.zeros((H, W), bool)
    for a, b in SHOJI['cols']: win |= (XX >= a) & (XX <= b) & (V >= v0) & (V <= v1)
    ref = np.median(city[(XX >= 1085) & (XX <= 1100) & (V > 0.55) & (V < 0.75)][:, :3], 0)   # (C's curtained window)
    lref = ref @ np.array([0.299, 0.587, 0.114])
    paper = lref * SHOJI['lift'] * lumn(SHOJI['cream'])                # (warm cream, as bright as the curtained windows)
    vm = 0.5 * (v0 + v1); g = 1 + 0.05 * (1 - np.abs(V - vm) / (0.5 * (v1 - v0)))
    gc, _ = first_cols((ZCOL - 0.07) / SHOJI['kz']); gr, _ = first_rows((Y - 0.05) / SHOJI['kh'])
    bars = (np.broadcast_to(gc[None, :], gr.shape) | gr) & win
    edge = win & ~np.roll(win, 1, 1)                                   # (the pane's far side: its frame's own shadow)
    new = paper[None, None, :] * g[..., None] * (1 + 0.015 * (2 * h2(XX, YY, 29) - 1))[..., None]
    new[bars] = paper * np.array([0.42, 0.36, 0.36])                  # (the kumiko: dark wood against the paper)
    sash = win & ((XX == 916) | (XX == 930))                           # (the glass's sash in front: the painter's dark bar
    new[sash] = city[sash][:, :3] * 0 + np.array([0.30, 0.28, 0.30]) * lref  # at 917 and 929 made two pixels heavy)
    c[win, :3] = new[win]
    ul = np.median(unlit[win][:, :3], 0)
    nu = np.broadcast_to(ul, (H, W, 3)).copy(); nu[bars] = ul * 0.7
    u[win, :3] = nu[win]
    lm |= win


# a city bicycle (mamachari, as on sheets 1 to 3: step-through, a basket in front, a carrier behind; its frame cream),
# parked on the sidewalk along B's shutter: modelled in metres (s along the bike from its rear axle, h up, l across,
# + toward the wall), projected through the scene's camera, drawn far to near a pixel at a time
BIKE = dict(Xf=4.70, Zf=16.60, yaw=0.0, k=0.9)         # its front axle (X m from the eye's line, depth m); its nose turned
                                                  # yaw degrees toward the wall (0: along the wall, its front toward us)


def bike_axles():
    t = np.radians(BIKE['yaw']); Zr = BIKE['Zf'] + 1.08 * BIKE['k'] * np.cos(t); Xr = BIKE['Xf'] - 1.08 * BIKE['k'] * np.sin(t)
    return Zr, Xr, t
BIKE_COL = {'frame': (176, 164, 140), 'tyre': (20, 20, 24), 'rim': (126, 128, 136), 'dark': (40, 40, 46), 'seat': (26, 24, 28),
            'seattop': (96, 92, 100), 'fender': (100, 100, 106), 'case': (36, 36, 42), 'grip': (24, 24, 28),
            'basket': (60, 60, 68), 'inside': (26, 26, 32), 'hub': (96, 98, 106),
            'brim': (110, 112, 120)}             # (albedo: a cream frame, black tyres, saddle and wire basket, steel)


def bike_parts():
    P = []                                       # (part, [(s, h, l), ...] polyline, width m)
    arc = lambda c, r, a0, a1, k=48: [(c[0] + r * np.cos(t), c[1] + r * np.sin(t), 0.0) for t in np.linspace(a0, a1, k)]
    q = lambda *pts: [p if len(p) == 3 else (p[0], p[1], 0.0) for p in pts]
    for ax in (0.0, 1.08):
        P.append(('tyre', arc((ax, 0.33), 0.312, 0, 2 * np.pi, 120), 0.045))
        P.append(('rim', arc((ax, 0.33), 0.275, 0, 2 * np.pi, 120), 0.012))
        P.append(('hub', [(ax, 0.33, -0.05), (ax, 0.33, 0.05)], 0.05))
        P.append(('fender', arc((ax, 0.33), 0.345, np.radians(40), np.radians(140), 40), 0.018))   # (its top third)
    for hh in np.arange(0.24, 0.37, 0.006):                                       # the chain case, from the crank to
        P.append(('case', q((0.02, hh + 0.03 * (0.33 - hh)), (0.46, hh - 0.04)), 0.01))   # the rear hub
    P += [('frame', q((0.42, 0.27), (0.30, 0.80)), 0.04),                       # seat tube
          ('frame', q((0.42, 0.27), (0.58, 0.33), (0.74, 0.46), (0.86, 0.60)), 0.05),   # the step-through's low tube
          ('frame', q((0.86, 0.60), (0.92, 0.80)), 0.05),                          # head tube
          ('frame', q((0.0, 0.33), (0.29, 0.74)), 0.025),                           # seat stays
          ('frame', q((0.86, 0.60), (1.00, 0.45), (1.08, 0.33)), 0.025),           # fork
          ('dark', q((0.92, 0.80), (0.90, 0.99)), 0.03),                          # stem
          ('dark', q((0.72, 0.97, -0.27), (0.86, 0.99, -0.14), (0.90, 0.99, 0.0), (0.86, 0.99, 0.14), (0.72, 0.97, 0.27)), 0.025),
          ('grip', q((0.66, 0.965, -0.30), (0.74, 0.97, -0.27)), 0.035), ('grip', q((0.66, 0.965, 0.30), (0.74, 0.97, 0.27)), 0.035),
          ('dark', q((0.30, 0.80), (0.28, 0.86)), 0.03),                          # seat post
          ('seat', q((0.14, 0.87, 0.0), (0.40, 0.89, 0.0)), 0.11),                # saddle
          ('seattop', q((0.14, 0.905, 0.0), (0.38, 0.915, 0.0)), 0.05),
          ('dark', q((-0.12, 0.72, -0.08), (0.24, 0.72, -0.08)), 0.02), ('dark', q((-0.12, 0.72, 0.08), (0.24, 0.72, 0.08)), 0.02),
          ('dark', q((-0.12, 0.72, 0.0), (0.0, 0.33)), 0.02),                     # carrier and its strut
          ('dark', q((0.02, 0.33), (0.10, 0.0)), 0.02)]                           # the stand
    B0, B1, BW, BH0, BH1 = 1.00, 1.24, 0.15, 0.74, 0.95       # (the basket: along the bike, half its width, its floor and rim)
    for hh in np.arange(BH0, BH1 - 0.004, 0.004):                                      # the basket: its far side and back,
        P.append(('inside', q((B0, hh, BW), (B1, hh, BW)), 0.012))        # seen through its near faces' wires
        P.append(('inside', q((B0, hh, -BW), (B0, hh, BW)), 0.012))
    for u in np.arange(-BW, BW + 0.001, 0.008): P.append(('inside', q((B0, BH0, u), (B1, BH0, u)), 0.012))   # (its floor)
    for hh in (BH0, 0.5 * (BH0 + BH1)):                                                       # its near end and street side: black
        P.append(('basket', q((B0, hh, -BW), (B1, hh, -BW), (B1, hh, BW)), 0.012))   # wire, upright every
    for u in np.arange(-BW, BW + 0.001, 0.056): P.append(('basket', q((B1, BH0, u), (B1, BH1, u)), 0.012))   # 6.4 cm,
    for s in np.arange(B0, B1 + 0.001, 0.06): P.append(('basket', q((s, BH0, -BW), (s, BH1, -BW)), 0.012))   # a band
    P.append(('brim', q((B0, BH1, -BW), (B1, BH1, -BW), (B1, BH1, BW), (B0, BH1, BW), (B0, BH1, -BW)), 0.016))   # its steel rim
    P.append(('dark', q((B1 - 0.02, BH0, 0.0), (1.08, 0.33, 0.0)), 0.015))            # its strut to the front hub
    return P


def render_bike(c, lm, light):
    Zr, Xr, t = bike_axles()
    pix = {}                                                       # (x, y) -> (depth, rgb)
    for part, pts, wid in bike_parts():
        pts = np.array(pts, float) * BIKE['k']; wid = wid * BIKE['k']   # (a 24-inch mamachari: the 26-inch one x 0.9)
        seg = []
        for a, b in zip(pts[:-1], pts[1:]):
            n = max(2, int(np.ceil(np.abs(b - a).max() / 0.004)))
            seg.append(a[None, :] + (b - a)[None, :] * np.linspace(0, 1, n)[:, None])
        sm = np.concatenate(seg)
        Zs = Zr - sm[:, 0] * np.cos(t) + sm[:, 2] * np.sin(t); hs = sm[:, 1]; Xs = Xr + sm[:, 0] * np.sin(t) + sm[:, 2] * np.cos(t)
        xs = VPX + FOC * Xs / Zs; ys = VPY + FOC * (EYE - hs) / Zs
        rad = 0.5 * wid * FOC / Zs; dep = np.hypot(Xs, Zs)
        base = np.asarray(BIKE_COL[part], float)
        for x, y, r, d, h in zip(xs, ys, rad, dep, hs):
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    px, py = int(np.floor(x + dx * 0.5)), int(np.floor(y + dy * 0.5))
                    if (px + 0.5 - x) ** 2 + (py + 0.5 - y) ** 2 > max(r, 0.55) ** 2: continue
                    k = (px, py); hk = h / BIKE['k']; sh = 1.0 + (0.12 if part == 'rim' and hk > 0.5 else 0) + (0.6 if part == 'tyre' and hk > 0.6 else 0)
                    if k not in pix or d < pix[k][0]: pix[k] = (d, base * sh)
    for (x, y), (d, rgb) in pix.items():
        if 0 <= x < W and 0 <= y < H:                              # (its lit side toward the lamp, up left; its shadow
            side = 1.2 if (x - 1, y) not in pix or (x, y - 1) not in pix else 0.75 if (x + 1, y) not in pix else 1.0   # side)
            c[y, x, :3] = grade(rgb[None, :], sat=0.8, con=0.95)[0] / 255.0 / ALB * light * side; c[y, x, 3] = 255; lm[y, x] = True


# A's mailbox, on the pier right of its door (a stainless box, as the sheet 1 one's shape: its lid lighter, a slot): a box
# against the wall, modelled in metres and projected; we see its face toward the street, its end toward us and a
# sliver of its lid; a line of shade on the wall under it
MAILBOX = dict(X0=4.90, X1=5.0, Z0=19.72, Z1=19.95, h0=1.22, h1=1.56)
MAIL_LIT = 0.8                       # (a neutral light on it, at the pier's value: stainless takes no blue of its own)
MAIL_COL = {'face': (150, 152, 156), 'end': (104, 106, 112), 'lid': (196, 198, 204), 'slot': (30, 30, 36), 'edge': (180, 182, 188)}   # (stainless)


def render_mailbox(c, lm, light):
    M = MAILBOX; pix = {}
    def face(name, P0, du, dv, nu, nv, col):
        for i in range(nu + 1):
            for j in range(nv + 1):
                X, Zd, h = (np.asarray(P0, float) + du * i / nu + dv * j / nv)
                x = VPX + FOC * X / Zd; y = VPY + FOC * (EYE - h) / Zd; d = np.hypot(X, Zd)
                k = (int(np.floor(x)), int(np.floor(y)))
                cc = col(i / nu, j / nv)
                if k not in pix or d < pix[k][0] - 1e-6: pix[k] = (d, cc)
    X0, X1, Z0, Z1, h0, h1 = M['X0'], M['X1'], M['Z0'], M['Z1'], M['h0'], M['h1']
    C = {k: np.asarray(v, float) for k, v in MAIL_COL.items()}
    def street(u, v):                                  # (u along the depth, v up)
        if v > 0.93: return C['lid']
        if abs(v - 0.80) < 0.03: return C['slot']
        return C['face'] * (1.0 + 0.06 * v)
    def near(u, v):                                    # (u from the wall out, v up)
        if v > 0.93: return C['lid'] * 0.85
        return C['edge'] if u < 0.1 else C['end']
    face('street', (X0, Z1, h0), np.array([0, Z0 - Z1, 0]), np.array([0, 0, h1 - h0]), 60, 60, street)
    face('near', (X1, Z0, h0), np.array([X0 - X1, 0, 0]), np.array([0, 0, h1 - h0]), 40, 60, near)
    face('top', (X0, Z1, h1), np.array([0, Z0 - Z1, 0]), np.array([X1 - X0, 0, 0]), 60, 30, lambda u, v: C['lid'] * 1.1)
    for (x, y), (d, rgb) in pix.items():
        c[y, x, :3] = rgb / 255.0 / ALB * light; c[y, x, 3] = 255; lm[y, x] = True
    ys = [y for (x, y) in pix]; xs = [x for (x, y) in pix]
    return min(xs), min(ys), max(xs), max(ys)


def contact(c, u, lm, spots, k=0.3):
    # the shade on the ground right round what stands there: an ellipse of radius r m on the ground plane, darkest at
    # its middle (on both the street and its power cut)
    for X, Zd, r in spots:
        for y in range(int(VPY + FOC * EYE / (Zd + r)) - 1, int(VPY + FOC * EYE / (Zd - r)) + 2):
            for x in range(int(VPX + FOC * (X - r) / Zd) - 1, int(VPX + FOC * (X + r) / Zd) + 2):
                if not (0 <= y < H and 0 <= x < W) or lm[y, x]: continue
                zz = FOC * EYE / (y + 0.5 - VPY); xx = (x + 0.5 - VPX) * zz / FOC     # (the ground point under the pixel)
                d = np.hypot((zz - Zd) / r, (xx - X) / (r * 1.3))
                if d < 1:
                    f = k + (1 - k) * d * d
                    c[y, x, :3] *= f; u[y, x, :3] *= f


LAUNDRY_ON = False                   # (the laundry behind B's window: read as a figure at the window; left out)
LIFE = 2                             # how much life: 1 the laundry and the shoji, 2 all below, 3 a few more pots
POTS3 = [('zone5_sheet2.webp', (718, 148, 865, 351), 4.86, 20.13, 0.42, 0.6),   # a hydrangea right of the door
         ('zone5_sheet3.webp', (601, 48, 775, 357), 4.80, 19.90, 0.78, 0.6)]     # a small tree in a blue pot
KOSHI_ON = True
KOSHI = dict(x=(915, 934), v=(-0.2295, 0.2515), kz=0.28, rails=(0.45, 1.05, 2.58))   # A's shutter: its body; the
# kick board's top, the mid rail, the lintel's foot (m above the ground)


def koshi(c, u, city, unlit, lm, light):
    # A's rolling shutter becomes the house's sliding door, a wooden lattice (koshi-do, as on ref_house_trad 1 to 3):
    # dense slats of cedar every kz m along the street (two thirds slat, a third gap, the slat's edge toward the
    # lamp lit), the warm glow of the hall through frosted glass between them (none in the power cut), a solid kick
    # board up to its first rail, a mid rail; over it a lintel (kamoi), the shutter's guides its wooden jambs. On the rays
    v0, v1 = KOSHI['v']; x0, x1 = KOSHI['x']; Y = V * XS + EYE
    door = (XX >= x0) & (XX <= x1) & (V >= v0) & (V <= v1)
    fz = (ZCOL - 0.03) / KOSHI['kz']; fz = fz - np.floor(fz)
    gapc = fz < 0.36; litc = (fz >= 0.36) & (np.roll(fz, 1) < 0.36)    # (a third of each pitch the gap; the slat's edge
    slat = np.broadcast_to((~gapc)[None, :], door.shape)               # next to it toward the lamp, lit)
    sedge = np.broadcast_to(litc[None, :], door.shape)
    r0, r1, lt = KOSHI['rails']
    kick = Y < r0
    rail = (np.abs(Y - r1) < 0.03) | (np.abs(Y - r0) < 0.03)
    lintel = door & (Y > lt)
    jamb = ((XX == 913) | (XX == 914) | (XX == 935)) & (V >= v0) & (V <= KOSHI['v'][1] + 0.004)
    wood = 1.1 * chroma((150, 86, 56), 1.4)                            # (cedar, warm brown)
    gap = door & ~slat & ~kick & ~rail & ~lintel
    warm = np.median(city[(XX >= 930) & (XX <= 934) & (V > 0.5) & (V < 0.7)][:, :3], 0)   # (the lit window's warm)
    new = light * wood[None, None, :] * np.ones(door.shape)[..., None]
    new[sedge & ~kick & ~rail & ~lintel] *= 1.25
    new[gap] = (light * wood * 0.25)[gap] + warm * 0.42 * np.clip((Y[gap] - r0) / (lt - r0), 0.45, 1)[:, None]   # (frosted
    new[kick & ~rail] *= 0.9                                                # glass behind, the warm glow, more up high)
    new *= (1 + 0.03 * (2 * h2(XX, YY, 31) - 1))[..., None]
    lb = lintel & ~np.roll(lintel, 1, 0)                               # (the lintel: its face, a lit lower edge, a shade
    new[lintel] = (light * wood * 1.05)[lintel]                         # over it under the ledge)
    new[lintel & ~np.roll(lintel, -1, 0)] *= 1.18
    new[lb] *= 0.75
    new[jamb] = (light * wood * 0.95)[jamb]; new[jamb & (XX == 935)] *= 1.15
    edge = door & ~np.roll(door, -1, 0)                                # (its foot: the sill's shade)
    new[edge] *= 0.7
    m = door | jamb
    c[m, :3] = new[m]
    nu = new.copy(); nu[gap] = (light * wood * 0.25)[gap]                  # (in the power cut: no glow)
    u[m, :3] = nu[m] * ((unlit[m][:, :3] + 1) / (city[m][:, :3] + 1)).mean(0)
    lm |= m


def life(c, u, city, unlit, shades):
    lm = np.zeros((H, W), bool)
    wB, SB = shades['B']
    lw = np.zeros((H, W), bool)
    if LAUNDRY_ON: render_laundry(c, lw, LAUNDRY, city, unlit, u)
    sh = np.zeros((H, W), bool); shoji(c, u, city, unlit, sh)
    if LIFE < 2:
        lm |= sh; return lm
    if KOSHI_ON:
        wA, SA = shades['A']; la = np.broadcast_to(np.median(SA[wA & (V < 0.25)], 0), (H, W, 3))
        koshi(c, u, city, unlit, sh, la)
    lm |= sh
    foot = np.median(SB[wB & (V < 0.0) & (XX < 957)], 0) * 1.15
    sheets = {}; shadows = []; sp = np.zeros((H, W), bool)          # (sp: what stands on the sidewalk)
    for n, box, X, Zd, hm, sat in POTS + (POTS3 if LIFE >= 3 else []):
        if n not in sheets: sheets[n] = sheet(n)
        spr = cut(sheets[n], box)
        bx = render_frontal(c, sp, X, Zd, 0.0, hm, spr, kpal(spr, 14), foot * SPRITE_LIT * POT_LIT, sat=sat)
        shadows.append((X, Zd, 0.20))
        lv = foot * SPRITE_LIT * POT_LIT
        warm = sp & (c[:, :, 0] / lv[0] > 1.1 * c[:, :, 2] / lv[2]) & (YY >= bx[1]) & (YY <= bx[3]) & (XX >= bx[0]) & (XX <= bx[2])
        n_ = [int(warm[y].sum()) for y in range(bx[1], bx[3] + 1)]; y = bx[3]
        while y > bx[1] and n_[y - bx[1]] == 0: y -= 1
        rows = []                                      # (the pot: the run of terracotta rows up from its foot)
        while y >= bx[1] and n_[y - bx[1]] >= 5: rows.insert(0, y); y -= 1
        if rows:                                       # (its lip lit, a darker band under it, the body a shade under the
            y0 = rows[0]                               # pavement)
            body = warm & (YY > y0) & (YY <= rows[-1]); lip = warm & (YY == y0); band = body & (YY <= y0 + 2)
            for L_ in (c, u): L_[body, :3] *= 0.8; L_[band, :3] *= 0.75; L_[lip, :3] *= 1.45
        for x in range(bx[0], bx[2]):                  # (the dark line where the pot meets the ground)
            col = np.nonzero(sp[:, x])[0]
            if len(col) and col.max() >= bx[3] - 2:
                y = col.max() + 1; c[y, x, :3] *= 0.55; u[y, x, :3] *= 0.55
    wA, SA = shades['A']
    la = np.median(SA[wA & (XX >= 930) & (V > -0.1) & (V < 0.1)], 0)
    bx = render_mailbox(c, sp, (0.5 * la + 0.5 * la.mean()) * SPRITE_LIT * MAIL_LIT)
    for x in range(bx[0], bx[2] + 2):                 # (its shade on the pier under it)
        col = np.nonzero(sp[:, x])[0]
        if len(col):
            y = col.max() + 1
            for dy, k in ((0, 0.6), (1, 0.8)):
                if not sp[y + dy, x]: c[y + dy, x, :3] *= k; u[y + dy, x, :3] *= k
    render_bike(c, sp, foot * SPRITE_LIT)
    Zr, Xr, t = bike_axles(); shadows += [(Xr, Zr, 0.13), (BIKE['Xf'], BIKE['Zf'], 0.13)]
    lm |= sp
    contact(c, u, lm, shadows)
    # the power cut: as dark as what is around them was (the laundry, and all that stands on the sidewalk, drawn over
    # the door's lattice too)
    from scipy.ndimage import gaussian_filter
    r = np.zeros((H, W, 3))
    for k in range(3): r[:, :, k] = gaussian_filter((unlit[:, :, k] + 1) / (city[:, :, k] + 1), 3)
    lr = (lm & ~sh) | sp
    u[lr, :3] = c[lr, :3] * np.clip(r[lr], 0, 1); u[lr, 3] = c[lr, 3]
    u[sp, :3] = np.minimum(u[sp, :3], CUT_K * (c[sp, :3] + CUT_ADD))   # (as the wall drops in the rendered frames)
    # B's lit entrance (x 1004-1022) lights the near side of what stands before it: a rim on their edges facing it,
    # fading with the distance (a painted light: in the street's layer only, so gone in the power cut, red in the red night)
    ent = (XX >= 1009) & (XX <= 1019) & (YY >= 640) & (YY <= 690)
    glow = np.clip(np.median(city[ent][:, :3], 0) - foot / 1.15, 0, None)          # (its pink over the wall's light)
    rim = np.zeros((H, W), bool)                                       # (their outer edge toward the door: the rightmost
    for y in range(600, H):                                            # pixel of each row)
        xs_ = np.nonzero(sp[y, RIM_X0:1030])[0]
        if len(xs_) and RIM_X0 + xs_.max() < 1006: rim[y, RIM_X0 + xs_.max()] = True
    f = np.clip((XX - RIM_X0) / (1004 - RIM_X0), 0, 1) * RIM_K
    c[rim, :3] += glow * f[rim][:, None]
    return lm


COMPS = {'win_z1_top': (963, 226), 'win_z1_violet': (1006, 358), 'win_z1_warm': (1081, 288)}   # the lit windows' overlays


def comps_update(c_old, c_new, changed, I=A_):
    # where a lit window's overlay covers wall (the room's light on the wall beside it), its pixels take the wall's new
    # material: each multiplied by the ratio the street's layer took there
    out = {}
    for n, (x, y) in COMPS.items():
        a = load(I(n + '.webp')); h, w = a.shape[:2]
        m = (a[:, :, 3] > 0) & changed[y:y + h, x:x + w]
        if not m.any(): continue
        k = (c_new[y:y + h, x:x + w, :3] + 1) / (c_old[y:y + h, x:x + w, :3] + 1)
        a[m, :3] = np.clip(a[m, :3] * k[m], 0, 255); out[n] = a
    return out


def save(arr, p):
    Image.fromarray(np.clip(np.round(arr), 0, 255).astype(np.uint8), 'RGBA').save(p, 'WEBP', lossless=True, quality=100, method=6, exact=True)


def main():
    global LIFE
    ap = argparse.ArgumentParser(); ap.add_argument('--variant', default=VARIANT); ap.add_argument('--life', type=int, default=LIFE)
    ap.add_argument('--out', default=None); ap.add_argument('--src', default=None)   # (trials: write there, read there)
    ap.add_argument('--force', action='store_true')
    a = ap.parse_args(); LIFE = a.life
    I = (lambda n: os.path.join(a.src, n)) if a.src else A_
    city, unlit = load(I('layer_city_off.webp')), load(I('street_unlit.webp'))
    if zone_sha(city) != ZONE_SHA and not a.force:
        print('the zone is not as painted (already done?): nothing written (--force to run anyway)'); return
    wet = load(I('wet.webp'), 'RGB')
    js = I('street.js') if os.path.exists(I('street.js')) else None
    c2, u2, ch, shades, front = walls(city, unlit, a.variant, js)
    comps = comps_update(city, c2, ch, I)
    lm = life(c2, u2, city, unlit, shades)
    dry = lm[600:]; wet[dry, 0] = 0; wet[dry, 2] = 0          # (what stands on the wet sidewalk is not the sidewalk)
    nf = load(I('night_far.webp'), 'RGB')                     # (a few wall pixels coded as the tree's mass: the street's)
    nfix = (ch | lm) & (nf[:, :, 0] != 0) & (city[:, :, 3] > 250); nf[nfix] = 0
    if a.out:
        os.makedirs(a.out, exist_ok=True)
        for n, arr in [('layer_city_off', c2), ('street_unlit', u2)] + list(comps.items()):
            Image.fromarray(np.clip(np.round(arr), 0, 255).astype(np.uint8), 'RGBA').save(os.path.join(a.out, n + '.png'))
        Image.fromarray(np.clip(np.round(wet), 0, 255).astype(np.uint8), 'RGB').save(os.path.join(a.out, 'wet.png'))
        Image.fromarray(nf.astype(np.uint8), 'RGB').save(os.path.join(a.out, 'night_far.png'))
    else:
        save(c2, A_('layer_city_off.webp')); save(u2, A_('street_unlit.webp'))
        for n, arr in comps.items(): save(arr, A_(n + '.webp'))
        for n, arr in (('wet', wet), ('night_far', nf)):
            Image.fromarray(np.clip(np.round(arr), 0, 255).astype(np.uint8), 'RGB').save(A_(n + '.webp'), 'WEBP', lossless=True, quality=100, method=6, exact=True)
    print('changed', int((ch | lm).sum()), 'px')


if __name__ == '__main__':
    main()
