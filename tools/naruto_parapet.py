#!/usr/bin/env python3
"""The tops of the two buildings on the right, over Ichiraku and over the arcade, as the tops of real buildings: Naruto's
from a small 3D model in the street's camera (each pixel's ray followed into it), the arcade's the painter's own, made
clean and given its material.

    (a module: tools/redraw_zones.py's zone 'naruroof' calls draw() on the street as the zones before it leave it, after
     'narufloor', whose roof edge it redraws; it rewrites assets/roof_sway.webp's planters (see below) and street_sun)
    python3 tools/naruto_parapet.py --before        once: the zone's before crops (tools/src/edits/naruroof_before_*.webp)
    python3 tools/naruto_parapet.py --preview OUT [SRC]   the zone drawn on the layers of SRC (default assets/), crops
                                                    before and after in OUT, the model's lines over x6 crops

The owner (2026-11-14, on tools/naruto_floor.py's roof edge): "toit Naruto toujours bizarre : gouttière trop de contraste,
forme pas logique et qui représente rien", "faut penser le haut comme un vrai haut d'immeuble avec détail, pas juste un
rectangle", "pareil pour les autres toits". What was there: on the street face a pale band along the roof's edge (the
slab's lit lip, read as a gutter), a darker parapet over it, a box at the near corner with a line across it, a T on the
far downpipe and a second downpipe from a socket under that box. A first pass (v1) had the logic right but read at 1:1
as large plain dark masses, and had flattened the arcade's tiled top; this one keeps the logic and gives every surface
its parts, its grain and its light (R27), the arcade's tiles back.
The camera is the street's (tools/arcade_eave.py, tools/r6_sprites.py): the eye 1.41 m up on the street's axis, f 959.5
px, the vanishing point (700, 615); a line along the street at X m from the axis and Y m up runs on the ray
v = (Y - 1.41) / X (redraw_zones.ray's v). Naruto's street face P is X_P = 10.1 m out (49.5 px a metre at x 1200: the
old railing's 1.1 m, tools/naruto_roof.py's PPM), its near side faces us at Z_N (P's corner, x 1236), its far end at C's
corner (x 1124); its rows are tools/naruto_floor.py's (the soffit's front edge V_LB and the coping's top V_CT kept, so the
floor under it, the window, the railing and the garden stay where they are).
- Naruto's building, a flat-roofed concrete block with a roof garden: a parapet flush with the facade, of its concrete
  (one face from the soffit's edge up: no lit lip, no band), its terrace 0.30 m over the soffit, the parapet 0.47 m over
  it; an aluminium coping on it (6.5 cm, 3 cm overhang): its top arris one crisp lit row (the sky), its face, its drip
  edge, the drip's shadow a dark row on the wall under it, a joint every ~1.6 m (three lengths along the street, one
  on the near side: a dark tick through the coping). The parapet's face in the painter's own grain (his pillar's
  concrete, its lightness over its local mean, laid as a texture), lighter up where the sky lights it, darker toward
  the near corner and toward its lower arris but for the arris itself (the street's light catches it); thin rain streaks
  from the coping's joints. Round the near corner (plumb at P's corner, its arris a lit column) the same rows run level
  across the near side, which faces us a step darker (turned from the street), down over the balcony's opening to the
  soffit, then as the near wall (one face, the same grain) down to the arcade's canopy. The owner on it: "cette façade
  face à nous, bizarre : on dirait qu'il y a un bâtiment entre Ichiraku et celui de l'arcade". So the near side is the
  front's own concrete (W's last pier's, by the corner) at 0.82 of its light, its corner with the front one crisp lit
  column from the roof slab down to the canopy, the roof slab's lower arris and the balcony's slab (its lit edge, its
  face, its lower arris, as over the opening) running round the corner across it at their own rows, a little lighter
  lower down, a touch darker into the inside corner with the arcade; the painter's dark box over the canopy is that wall
  (and, left of the corner, the front's) carried down to the canopy, a flashing where the canopy's roof meets them, and
  where the arcade's roof meets the side wall over its tiles' far end.
- The planters: the roof garden's shrubs, hedge and maple stand in concrete planters behind the parapet, their rims just
  showing over the coping under the plants (a lit top, its edge, the planter's face in shade over the coping's lit edge); the leaves the rims cover leave the garden's
  wind data (roof_sway.webp: no longer leaves, never shown there).
- The water (the owner on the first one: "cette gouttière pas ouf", a flat grey bar with a blob on a flat wall): one
  scupper through the parapet at the far end, just over the terrace, its short spout (its dark mouth) over a rain head
  on the pillar's face (a small box: its lit top and rolled rim, its end to us lit, its face to the street, its funnel);
  from it one round downpipe of 6.6 cm, 1.5 cm off the wall, straight down the pillar into the sign's top, on the
  painter's downpipe line: 3 px at that depth, its lit side toward the street, a thin highlight line, its dark side,
  its shadow on the wall beside it; a clamp every 1.2 m (a ring lit on top, its strap and its plate on the wall, the
  plate's edge on the facade's ray), the rain head's shadow under it. Then (the owner's R28: what is detailed is drawn by
  the image model, not by hand) the pipe as google/gemini-3-pro-image drew it in its context crop (PIPE_CROP x4,
  brightened; tools/src/edits/naruroof_pipe_model.webp from naruroof_pipe_prompt.txt): a hopper rain head with its lit
  rim under the scupper's dark mouth, the slim pipe with its lit side and highlight, four clamps with their ears, their
  shadows; boxed down to the street's pixels, brought to this wall's colours by a gain per channel, and only what is the
  pipe's laid over the wall this model draws without its own (drawn_pipe). Its wall, the pillar's face, in the painter's
  grain on the cleaned pillar's light (its rows' light smoothed down the wall, darker into C's corner), a faint trace
  of the overflow under the rain head; the pillar's side face beside it, in the balcony's recess, the painter's grain
  too, a little lighter lower down. The street
  lamp's light on the far end as before (tools/naruto_roof.lamp's warm share, the lit layer only). The near corner's
  second downpipe (the painter's conduit, made a downpipe by tools/naruto_roof.py) is gone.
- The arcade's building, the right neighbour: the painter's top kept (his tiled eave's edge against the sky, as
  tools/naruto_roof.py made it a clean stair; under it his row of round tiles running to the frame's corner, the pent
  roof over its upper floor), the row redrawn clean on the street's ray through its middle (v 0.817): round tiles
  lying along it, each lit along its top, darker as it turns under, its far end a dome whose rim catches the light over the
  farther one's shadow, the row's far end a dome; its shadow on the wall under it; the stray lines round the old row gone. Its walls
  (the painter's flat green black, x 1297 on, the AC unit, its stand, the conduits and the corner's trims left as they
  are) given their material and light: vertical boards along the street face (18 cm, foreshortened, a dark seam, each
  board its own tone, a grain along it), dark under the eaves and lighter lower down, down to its canopy, its far
  corner (the painter's lit trims there, which read as another building's edge) an inside corner in shade against
  Naruto's side wall. Naruto's near side shows over its
  tiles at their far end only (x 1297..1303), drawn as round the corner.
Colours are the painting's (Naruto's concrete from his pillar and the near strip, the arcade's tiles from the painter's
row, its wall his green black lifted a little so its boards read). The power cut (street_unlit): the same, but the
street lamp's share (the far end, the metal); the arcade's tiles at the painter's own ratio. street_sun (the low sun's
share) is 0 on what is redrawn; night_far stays 0 (the street's, the sky's). Needs Pillow, numpy, scipy.
"""
import os
import sys
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, binary_dilation

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import naruto_floor as NF   # noqa: E402  (the floor's rows: the soffit's edge, the coping's top, P's corners)
import naruto_roof as NR    # noqa: E402  (the street lamp's share near the far end; the right house's eave)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDITS = os.path.join(ROOT, 'tools', 'src', 'edits')
ASSETS = os.path.join(ROOT, 'assets')
BOX = (1120, 0, 1456, 376)                     # the zone (redraw_zones.py 'naruroof')
NF_BOX = NF.BOX                                # (the zone 'narufloor': street_sun and roof_sway are its own there)
VPX, VPY = 700.0, 615.0
F, EYE = 959.5, 1.41                           # the street's camera (tools/arcade_eave.py)
LUMA = np.array([0.299, 0.587, 0.114])

# Naruto's building (metres: X out from the street's axis, Y up, Z ahead)
XP = 10.1                                      # its street face P
Z_of = lambda x: F * XP / (x - VPX)            # P's depth at column x
ZN, ZF = Z_of(NF.XPN), Z_of(1124.0)            # its near side (P's corner), its far end (C's corner)
ZPIL = Z_of(NF.XPF)                            # the pillar's edge (the balcony from there to ZN)
XW = XP * NF.KW                                # the window wall W (the near wall from its corner)
Y_LB = EYE + NF.V_LB * XP                      # the soffit's front edge (the parapet's foot on P)
Y_CT = EYE + NF.V_CT * XP                      # the coping's top
COP, OVH = 0.065, 0.03                         # the coping's height, its overhang
Y_T = Y_LB + 0.30                              # the terrace
DEEP = 15.0                                    # (the building's back: out of the frame)
JOINTS_P = [ZN + k * (ZF - ZN) / 3 for k in (1, 2)]   # the coping's joints along P (three lengths)
JOINTS_N = [XP + 1.6]                          # and on the near side
# the downpipe on the pillar (the painter's line, x 1145..1151): its axis, its radius, its rain head and scupper
PR = 0.033                                     # (a 6.6 cm pipe: 3 px at that depth)
PZ = 21.55                                     # (its axis's depth: on the pillar, 11 cm from its edge)
PX = XP - 0.015 - PR
BRACKET = 1.2                                  # a bracket every BRACKET m from the funnel down
METAL = ('pipe', 'ring', 'strap', 'plate', 'rh', 'fun', 'spout')
NEAR_K = 0.82                                  # the near side's light over the front's (turned from the street)
SLAB_ROWS = (262, 275)                         # the balcony's slab at the near corner (tools/naruto_floor.py's YFL, YSB)
CANOPY_X = (1270, 1352)                        # where the arcade's canopy meets the walls under it (its flashing)
STRIP = (1279, 1297, 312)                      # the near wall beside the window: its columns, down to the box over the awning
# the planters behind the parapet: where the garden's plants stand over the coping (from roof_sway.webp's leaves), their
# rims two rows over the coping's top
RIM_GAP = 3                                    # (spans of plants closer than this are one planter)
# the arcade's building: its street face (its far corner at x 1297 against Naruto's near side), its pent roof's row of
# round tiles on the ray through the painter's row's middle (x 1406, y 38), from the painter's end (x
# 1350) to the frame's corner, 13 px thick there, a tile every 0.42 m; its walls the painter's green black (x 1297.., under its tiles' edge,
# off the AC unit's box) as vertical boards, 18 cm
XA = (1297.0 - VPX) * ZN / F
V_H, T_H, X_HL = 0.817, 13.0, 1350             # the row: its axis's ray, its thickness at x 1406 (the painter's), its far end
X_H = XA - 0.3                                 # (it stands 30 cm out from the wall)
TILE = 0.42
ROW_OLD = (67.0, -0.698, 1358)                 # the painter's row: its top edge (y at x 1358, slope), to clear round it
ROW_TOP = lambda x: 615.0 - (V_H + T_H / 2 / 706.0) * (x + 0.5 - VPX)
ROW_BOT = lambda x: 615.0 - (V_H - T_H / 2 / 706.0) * (x + 0.5 - VPX)
ROW_C = np.array([(6, 13, 22), (10, 20, 39), (17, 30, 55), (15, 29, 52), (10, 22, 41), (8, 19, 35), (7, 18, 30),
                  (8, 17, 29), (9, 21, 32), (9, 20, 30), (7, 15, 21), (2, 8, 10)], float)   # the painter's row across it (x 1400)
BOARD = 0.18
WALL_X = (1297, 1456)
EAVE_T = 8                                     # (the eave's tiles: so many rows from its edge, kept as painted)
AC_BOX = (1352, 186, 1447, 340)
CONDUITS = ((1402, 84, 1409, 196), (1443, 68, 1451, 196), (1426, 66, 1451, 90))   # (the painter's conduits: their edges kept)                # the AC unit and its stand: left as they are
WALL_LOW, WALL_TOP = np.array((5.0, 11.0, 12.0)), np.array((2.0, 6.0, 6.0))   # its boards lit low down, in the eaves' shade

GRAIN = 0.05


NO_PIPE = [False]                              # (the model without its downpipe: the wall behind it, for the drawn one)
PIPE_MODEL = 'naruroof_pipe_model.webp'        # the downpipe drawn by the image model in its context crop (R28), from
PIPE_CROP = (1083, 112, 1229, 372)             # naruroof_pipe_prompt.txt, on this crop of the street (x4, brightened; the
                                               # pipe carried down from its last row to the sign's top)
PIPE_BAND = (1138, 1159)                       # the columns it is laid in (the pipe, its rain head, its clamps, shadows)
PIPE_GAMMA = 2.0


def boxes():
    """the model: (name, lo, hi) boxes, axis-aligned"""
    B = [('par', (XP, Y_LB, ZN), (XP + 0.25, Y_CT - COP, ZF)),                     # the parapet and the slab on P
         ('pil', (XP, 0.0, ZPIL), (XP + 0.6, Y_LB, ZF)),                           # the pillar under it
         ('near', (XP, Y_LB, ZN), (XP + DEEP, Y_CT - COP, ZN + 0.25)),             # the near side's parapet and slab end
         ('near', (XW, 0.0, ZN), (XP + DEEP, Y_LB, ZN + 3.0)),                     # the near wall under the slab
         ('cop', (XP - OVH, Y_CT - COP, ZN - OVH), (XP + 0.25 + OVH, Y_CT, ZF)),   # the coping on P
         ('cop', (XP - OVH, Y_CT - COP, ZN - OVH), (XP + DEEP, Y_CT, ZN + 0.25 + OVH)),   # on the near side
         ('spout', (XP - 0.07, Y_T, PZ - 0.04), (XP, Y_T + 0.06, PZ + 0.04)),      # the scupper's spout, the rain head,
         ('rh', (XP - 0.13, Y_T - 0.25, PZ - 0.075), (XP, Y_T - 0.04, PZ + 0.075)),  # its funnel into the pipe
         ('fun', (PX - PR * 1.3, Y_T - 0.30, PZ - 0.045), (XP, Y_T - 0.25, PZ + 0.045))]
    for yb in brackets():                                                           # the brackets: a strap from the
        B.append(('strap', (PX, yb, PZ - 0.006), (XP, yb + 0.025, PZ + 0.006)))    # ring to the wall, its plate on it
        B.append(('plate', (XP - 0.006, yb - 0.015, PZ - 0.035), (XP, yb + 0.04, PZ + 0.035)))
    if NO_PIPE[0]: B = [b for b in B if b[0] not in METAL]
    return B


def brackets():
    y = Y_T - 0.30 - 0.45
    out = []
    while y > Y_LB - 6.0:
        out.append(y); y -= BRACKET
    return out


def cylinders():
    """(name, X, Z, r, ylo, yhi): the downpipe, its brackets' rings"""
    if NO_PIPE[0]: return []
    return [('pipe', PX, PZ, PR, 0.0, Y_T - 0.30)] + [('ring', PX, PZ, PR + 0.006, yb, yb + 0.025) for yb in brackets()]


def cast(box):
    """each pixel's ray (its centre) into the model: the nearest hit's name, its normal and point"""
    x0, y0, x1, y1 = box
    xs = np.arange(x0, x1) + 0.5; ys = np.arange(y0, y1) + 0.5
    X, Yp = np.meshgrid(xs, ys)
    d = np.stack([(X - VPX) / F, (VPY - Yp) / F, np.ones_like(X)])
    o = np.array([0.0, EYE, 0.0])
    h, w = X.shape
    best = np.full((h, w), np.inf); name = np.full((h, w), '', 'U8'); nrm = np.zeros((3, h, w))
    for nm, lo, hi in boxes():
        tmin = np.full((h, w), -np.inf); tmax = np.full((h, w), np.inf); ax = np.zeros((h, w), int); sg = np.zeros((h, w))
        for k in range(3):
            with np.errstate(divide='ignore', invalid='ignore'):
                t1 = (lo[k] - o[k]) / d[k]; t2 = (hi[k] - o[k]) / d[k]
            a = np.minimum(t1, t2); b = np.maximum(t1, t2)
            new = a > tmin
            ax = np.where(new, k, ax); sg = np.where(new, np.where(t1 < t2, -1.0, 1.0), sg)
            tmin = np.maximum(tmin, a); tmax = np.minimum(tmax, b)
        hit = (tmax >= tmin) & (tmin > 0) & (tmin < best)
        best[hit] = tmin[hit]; name[hit] = nm
        for k in range(3):
            nrm[k][hit] = np.where(ax[hit] == k, sg[hit], 0.0)
    for nm, cx, cz, r, ylo, yhi in cylinders():
        a = d[0] ** 2 + d[2] ** 2; b = -2 * (d[0] * cx + d[2] * cz); c = cx * cx + cz * cz - r * r
        disc = b * b - 4 * a * c
        with np.errstate(invalid='ignore'):
            t = (-b - np.sqrt(disc)) / (2 * a)
        yy = o[1] + t * d[1]
        hit = (disc >= 0) & (t > 0) & (yy >= ylo) & (yy <= yhi) & (t < best)
        best[hit] = t[hit]; name[hit] = nm
        nrm[0][hit] = (t * d[0] - cx)[hit] / r; nrm[1][hit] = 0.0; nrm[2][hit] = (t * d[2] - cz)[hit] / r
    P = o[:, None, None] + best[None] * d
    name[(name == 'par') & (nrm[2] < -0.5)] = 'near'                 # (the parapet's end, turned to us, is the near side)
    return name, nrm, P


def first_row(yline):
    return int(np.ceil(yline - 0.5))


def eave_row(x):
    """the arcade's tiled eave's first row at column x (tools/naruto_roof.py's EAVE); past the frame's top (x 1362 on) its
    line carried on, over the frame"""
    if 1296 <= x < 1362: return NR.EAVE[x - 1296]
    return int(np.floor(-0.76 * (x - 1361)))


def mask(box, sign):
    """the pixels Naruto's model redraws (the rest of the box as the zones before it leave it)"""
    x0, y0, x1, y1 = box; h, w = y1 - y0, x1 - x0
    M = np.zeros((h, w), bool)
    for x in range(1124, x1):
        i = x - x0
        ct, pf, lt, lb = NF.edge_rows(x)
        if x < NF.XPF: M[ct - y0:sign[x] - y0, i] = True               # the pillar's face, its downpipe, to the sign
        elif x < NF.XPN: M[ct - y0:lb - y0, i] = True                  # P: the parapet and the slab's edge
        elif x < STRIP[0]: M[ct - y0:86 - y0, i] = True                # the near side over the balcony's opening
        elif x < STRIP[1]: M[ct - y0:STRIP[2] - y0, i] = True          # the near wall, its downpipe gone, to the awning
        elif eave_row(x) > ct: M[ct - y0:eave_row(x) - y0, i] = True   # over the arcade's tiles' far end
    return M


def palette(city):
    """the painting's colours for the model's surfaces, sampled on the layers as the zones before leave them"""
    med = lambda a, xs, ys: np.median(a[ys[0]:ys[1], xs[0]:xs[1], :3].reshape(-1, 3), 0)
    par = med(city, (1128, 1141), (176, 236))           # Naruto's concrete: his pillar's face (under the parapet)
    pier = med(city, (1269, 1278), (120, 250))           # his front's concrete by the corner: W's last pier
    return dict(par=par, near=pier * NEAR_K, pier=pier,
                cop=par * 1.45, cop_top=par * 2.8, cop_low=par * 1.2, rim=par * 1.15, rim_top=par * 1.9, rim_face=par * 0.6,
                pipe=np.array((17.0, 25.0, 44.0)), hole=np.array((1.0, 3.0, 6.0)))


def grain(shape, seed, s=0.7):
    n = gaussian_filter(np.random.default_rng(seed).normal(size=shape), s)
    return n / (n.std() + 1e-9)


def painter_grain():
    """the painter's concrete grain: his pillar's face as he painted it (this zone's before crop, x 1125..1143, y
    180..330), each pixel's lightness over its local mean (sigma 4), softened"""
    b = np.asarray(Image.open(os.path.join(EDITS, 'naruroof_before_city.webp')).convert('RGB')).astype(float)
    L = b[180:330, 1125 - BOX[0]:1144 - BOX[0]] @ LUMA + 1.0
    g = np.clip(L / gaussian_filter(L, 4.0), 0.7, 1.35) ** 0.6
    return np.concatenate([g, g[:, ::-1]], 1)


def tile(tex, h, w, oy=0, ox=0):
    """tex laid over (h, w), mirrored by turns"""
    th, tw = tex.shape
    ys = (np.arange(h) + oy) % (2 * th); ys = np.where(ys < th, ys, 2 * th - 1 - ys)
    xs = (np.arange(w) + ox) % (2 * tw); xs = np.where(xs < tw, xs, 2 * tw - 1 - xs)
    return tex[ys][:, xs]


def runs_from_top(m):
    """per pixel of mask m: its rank in its column's run (0 at the run's first row), and the run's length"""
    h, w = m.shape; rk = np.zeros((h, w), int); ln = np.zeros((h, w), int)
    for i in range(w):
        y = 0
        while y < h:
            if not m[y, i]: y += 1; continue
            e = y
            while e < h and m[e, i]: e += 1
            rk[y:e, i] = np.arange(e - y); ln[y:e, i] = e - y; y = e
    return rk, ln


def screen_dist(P, which, at):
    """how far (px) a hit point is from a line across a surface: along P (receding: Z) or the near side (frontal: X)"""
    P = np.where(np.isfinite(P), P, 1e6)                             # (no hit: far away)
    if which == 'near':
        return (P[0] - at) * F / np.maximum(P[2], 1.0)
    return (at - P[2]) * F * XP / np.maximum(P[2], 1.0) ** 2


def shade(box, name, nrm, P, pal, M, city, unlit):
    """Naruto's model's colours over M: (the lit layer before the lamp's share, the power cut, where that share applies)"""
    x0, y0, x1, y1 = box; h, w = name.shape
    X = np.arange(x0, x1)[None, :] + np.zeros((h, 1), int); Yr = np.arange(y0, y1)[:, None] + np.zeros((1, w), int)
    col = np.zeros((h, w, 3)); n = grain((h, w), 23)
    pg = tile(painter_grain(), h, w, 17, 5)
    lampable = np.ones((h, w), bool)
    # the coping: its top arris one crisp lit row, its face, its drip edge; the near side's a step darker; a joint every
    # ~1.6 m a dark tick through it
    m = (name == 'cop') & M
    rk, ln = runs_from_top(m)
    c = np.where((rk == 0)[..., None], pal['cop_top'], np.where(((rk == ln - 1) & (ln > 2))[..., None], pal['cop_low'], pal['cop']))
    turned = nrm[2] < -0.5
    c = c * np.where(turned, 0.85, 1.0)[..., None]
    c = np.where((nrm[1] < -0.5)[..., None], pal['cop_low'] * 0.7, c)
    dz = np.stack([screen_dist(P, 'p', z) for z in JOINTS_P]); dx = np.stack([screen_dist(P, 'near', x) for x in JOINTS_N])
    pick = lambda D: D[np.argmin(np.abs(D), 0), np.arange(h)[:, None], np.arange(w)[None, :]]
    dj = np.where(turned, pick(dx), pick(dz))
    c = np.where((np.abs(dj) < 0.5)[..., None], c * 0.4, c)
    col[m] = (c * (1 + 0.03 * n[..., None]))[m]
    # the walls: P (the parapet over the soffit, over the pillar), the near side and the near wall: the drip's shadow
    # under the coping, the painter's grain, the light (below)
    wall = ((name == 'par') | (name == 'pil') | (name == 'near')) & M
    rk, ln = runs_from_top(wall)
    k = np.where(rk == 0, 0.45, 1.0) * (1 - 0.2 * np.exp(-np.maximum(rk - 1, 0) / 2.0))
    onp = (name == 'par') & (X >= NF.XPF)
    lbr = np.array([first_row(NF.Y(x + 0.5, NF.V_LB)) for x in range(x0, x1)])[None, :] + np.zeros((h, 1), int)
    d_lb = lbr - 1 - Yr
    t = np.clip(rk / np.maximum(ln - 1, 1), 0, 1)                    # (0 under the coping, 1 at the lower arris)
    corner = np.clip((X - 1195.0) / (NF.XPN - 1195.0), 0, 1) ** 1.5   # (toward the near corner)
    kp = (1.12 - 0.2 * t) * (1 - 0.14 * corner) * np.where(d_lb == 0, 1.3, 1.0)
    k = np.where(onp, k * kp, k)
    onn = name == 'near'
    k = np.where(onn & (Yr < 86), k * (1.1 - 0.12 * np.clip((Yr - 49) / 36.0, 0, 1)), k)
    k = np.where(onn & (X >= NF.XPN) & (Yr == 85), k * 1.25, k)       # (the roof slab's lower arris, round the corner on)
    k = np.where(onn & (X == int(NF.XPN)) & (Yr < 86), k * 1.3, k)           # (the corner's arris over the opening)
    # the near wall beside the window, the same face down to the arcade's canopy: its corner with the front (W's) one lit
    # column all the way down, a little lighter lower down, a touch darker into the corner with the arcade; the balcony's
    # slab round the corner at its own rows (its edge's lit line, its face, its lower arris, a shade under it)
    sw = onn & (X >= STRIP[0]) & (X < STRIP[1]) & (Yr >= 86)
    ks = (0.94 + 0.12 * np.clip((Yr - 90) / 220.0, 0, 1)) * (1 - 0.12 * np.exp(-(STRIP[1] - 1 - X) / 1.5))
    k = np.where(sw, k * ks, k)
    # rain streaks from the coping: thin, each its own length and depth, fading down, longer under the joints and the corner
    rng = np.random.default_rng(31)
    for x in range(x0, x1):
        i = x - x0
        if x < NF.XPN:
            z = Z_of(x + 0.5); j = min(abs(z - zz) for zz in JOINTS_P) * F * XP / z ** 2 < 1.0
        else:
            xm = (x + 0.5 - VPX) * ZN / F; j = min(abs(xm - xx) for xx in JOINTS_N) * F / ZN < 1.0
        j = j or abs(x + 0.5 - NF.XPN) < 1.5
        r = rng.random(); L = int(rng.integers(10, 24)) if j else int(rng.integers(4, 16)); dk = 0.06 + 0.08 * rng.random()
        if j or r < 0.25:
            s_ = rk[:, i] - 1
            fade = np.clip(1 - s_ / L, 0, 1) * (s_ >= 0)
            k[:, i] = np.where(wall[:, i] & (Yr[:, i] < 86 + 30 * (x >= STRIP[0])), k[:, i] * (1 - dk * fade), k[:, i])
    base = np.where(onn[..., None], pal['near'], pal['par'])
    colu = col.copy()
    col[wall] = (base * k[..., None] * pg[..., None] * (1 + 0.3 * GRAIN * n[..., None]))[wall]
    # over the pillar (left of its edge) the wall is the pillar's own light as tools/naruto_floor.py cleaned it, in each
    # layer: under the old coping's rows each column's light from just under them, by the pipe each row's mean over the
    # pillar's clean columns (x 1130..1141); the same shading; no lamp's share added (it is in the pillar's own light)
    pm = wall & (X < NF.XPF)
    lampable &= ~pm
    # (the pillar's face: its light from tools/naruto_floor.py's cleaned pillar, each row's mean over its clean columns,
    # smoothed down the wall; a little darker into C's corner; the painter's grain on it; under the rain head a faint trace
    # of its overflow down the wall beside the pipe)
    stain = np.zeros((h, w))
    rh_rows = np.nonzero((name == 'fun').any(1))[0]
    if len(rh_rows):
        r0 = rh_rows.max() + 1
        for x in (1142, 1143):
            stain[r0:r0 + 60, x - x0] = 0.12 * np.clip(1 - np.arange(min(60, h - r0)) / 60.0, 0, 1)
    for lay, out in ((city, col), (unlit, colu)):
        rowm = np.array([lay[y, 1126:1142, :3].mean(0) for y in range(y0, y1)])
        rowm = np.stack([gaussian_filter(rowm[:, c], 3.0, mode='nearest') for c in range(3)], -1)
        ref = np.zeros((h, w, 3))
        for x in range(x0, min(x1, int(NF.XPF))):
            i = x - x0
            if not pm[:, i].any(): continue
            pf = NF.edge_rows(x)[1]
            for r in np.nonzero(pm[:, i])[0]:
                ref[r, i] = rowm[max(r, pf + 3 - y0)] * (1 - 0.15 * np.exp(-(x - 1124) / 2.0))
        out[pm] = (ref * k[..., None] * pg[..., None] * (1 - stain)[..., None])[pm]
    other = M & ~pm
    colu[other] = col[other]
    # the downpipe: round, lit from the street's side and from us, its far side in shade; the rings, the straps
    m = ((name == 'pipe') | (name == 'ring')) & M
    Ld = np.array((-0.8, 0.0, -0.6)); Ld = Ld / np.linalg.norm(Ld)
    Pf = np.where(np.isfinite(P), P, 1.0)
    V = -Pf / np.maximum(np.linalg.norm(Pf, axis=0), 1e-6)
    Hh = Ld[:, None, None] + V; Hh = Hh / np.maximum(np.linalg.norm(Hh, axis=0), 1e-6)
    lam = np.clip(nrm[0] * Ld[0] + nrm[2] * Ld[2], 0, 1)
    spec = np.clip(nrm[0] * Hh[0] + nrm[2] * Hh[2], 0, 1) ** 24
    kq = 0.3 + 0.75 * lam + 0.9 * spec                                # (its lit side, a dark core, a thin highlight line)
    rkr, lnr = runs_from_top((name == 'ring') & M)
    kq = np.where(name == 'ring', np.where(rkr == 0, 1.45, 0.85) * (0.6 + 0.5 * lam), kq)   # (a clamp: its lit top)
    col[m] = (pal['pipe'] * kq[..., None] * (1 + 0.03 * n[..., None]))[m]
    m = (name == 'strap') & M; col[m] = pal['pipe'] * 0.9
    m = (name == 'plate') & M                                          # (its plate on the wall, its top edge on the ray)
    rkp, _ = runs_from_top(m)
    col[m] = (pal['pipe'] * np.where(rkp == 0, 1.25, 0.95)[..., None])[m]
    # the rain head: its face to the street and its end to us lit, its top rim the sky's, the funnel darker; the spout
    for nm, kk in (('rh', 1.0), ('fun', 0.8), ('spout', 1.05)):
        m = (name == nm) & M
        if not m.any(): continue
        rk2, _ = runs_from_top(m)
        k2 = np.where(nrm[2] < -0.5, 1.25, np.where(nrm[1] < -0.5, 0.7, 0.95)) * kk
        if nm == 'rh': k2 = np.where(rk2 == 0, 1.6, np.where(rk2 == 1, k2 * 1.1, k2))   # (its lit top, its rolled rim)
        c = pal['pipe'] * k2[..., None]
        if nm == 'spout': c = np.where((nrm[0] < -0.5)[..., None], pal['hole'], c)   # (its mouth)
        col[m] = (c * (1 + 0.04 * n[..., None]))[m]
    metal = np.isin(name, METAL) & M
    colu[metal] = col[metal] * 0.8                                     # (the street lamps' share off the metal)
    # the rain head's and the pipe's shadows on the pillar's face (the light from the street, its left): under the rain
    # head two rows, right of the pipe a dark column and a lighter one, a little under each clamp's plate
    for x in range(1138, 1152):
        i = x - x0
        for r in range(2, h):
            if not pm[r, i]: continue
            kk = 1.0
            if name[r - 1, i] in ('rh', 'fun', 'spout'): kk = 0.62
            elif name[r - 2, i] in ('rh', 'fun', 'spout'): kk = 0.8
            if name[r, i - 1] in ('pipe', 'ring', 'strap'): kk *= 0.6
            elif name[r, i - 2] in ('pipe', 'ring', 'strap'): kk *= 0.85
            if name[r - 1, i] == 'plate': kk *= 0.75
            col[r, i] *= kk; colu[r, i] *= kk
    return col, colu, lampable


def planters(city, unlit, box, pal, sw_):
    """the planters' rims over the coping under the garden's plants (three rows: a lit top, its edge, the planter's face in
    the shade over the coping's lit edge); the garden's wind data
    (sw_, roof_sway.webp as tools/naruto_floor.py wrote it, its box at naruto_floor's SWAY_AT... printed box) made to
    know them: no leaf there, none may show there. Returns the rims' pixels."""
    bx, by = 1127, 34                                    # (street.js ROOF: B.x0, B.y0, naruto_floor's box)
    H = sw_.shape[0] // 3; W = sw_.shape[1]
    leaf = sw_[2 * H:, :, 0] >= 16
    cols = {}
    for i in range(W):
        x = bx + i
        if x < 1126 or x >= 1260: continue
        ct = NF.edge_rows(x)[0]
        r0 = ct - 3 - by
        if 0 <= r0 and leaf[r0:ct - by, i].any(): cols[x] = ct       # (a plant right over the coping there)
    xs = sorted(cols); spans = []
    for x in xs:
        if spans and x - spans[-1][1] <= RIM_GAP: spans[-1][1] = x
        else: spans.append([x, x])
    px = []
    for a, b in spans:
        for x in range(a - 1, b + 2):
            ct = NF.edge_rows(x)[0]
            for j, y in enumerate((ct - 3, ct - 2, ct - 1)):
                c = (pal['rim_top'], pal['rim'], pal['rim_face'])[j]
                if x == a - 1 or x == b + 1: c = c * 0.8                 # (its ends turned away)
                k = 1 + NR.lamp(x, y)
                city[y, x, :3] = c * k; unlit[y, x, :3] = c; city[y, x, 3] = unlit[y, x, 3] = 255
                px.append((x, y))
                i, r = x - bx, y - by
                if 0 <= i < W and 0 <= r < H:
                    sw_[r, i] = np.clip(np.round(city[y, x]), 0, 255); sw_[H + r, i] = np.clip(np.round(unlit[y, x]), 0, 255)
                    sw_[2 * H + r, i] = (0, 0, 0, 255)
    return px


def arcade(city, unlit, box):
    """the arcade's top: its row of round tiles redrawn clean on its ray, its walls' boards and light; returns what it
    drew (a mask over box)"""
    x0, y0, x1, y1 = box; h, w = y1 - y0, x1 - x0
    c0, u0 = city[y0:y1, x0:x1, :3].copy(), unlit[y0:y1, x0:x1, :3].copy()
    done = np.zeros((h, w), bool)
    # the walls: the painter's green black, under the tiles' edge, off the AC unit's box
    gb = (c0.max(-1) <= 9) & (c0[..., 1] >= c0[..., 0]) & (c0[..., 1] + 1 >= c0[..., 2])
    region = np.zeros((h, w), bool)
    for x in range(WALL_X[0], min(WALL_X[1], x1)):
        i = x - x0
        region[max(eave_row(x) + EAVE_T, 0) - y0:y1 - y0, i] = True   # (under the eave's tiles, EAVE_T rows from its edge,
                                                                       # down to its canopy: the painter's dark box over it)
    # (in the AC unit's box and along the conduits their own dark pixels stay: green black next to anything else is an edge)
    near_thing = binary_dilation(~gb, structure=np.ones((3, 3), bool)) & gb
    ax0, ay0, ax1, ay1 = AC_BOX
    acb = np.zeros((h, w), bool); acb[ay0 - y0:ay1 - y0, ax0 - x0:ax1 - x0] = True
    for bx0, by0, bx1, by1 in CONDUITS: acb[by0 - y0:by1 - y0, bx0 - x0:bx1 - x0] = True
    # the painter's row and the stray lines round it: cleared to the wall (a band along his row)
    clear = np.zeros((h, w), bool)
    for x in range(1317, x1):
        i = x - x0
        yt = ROW_OLD[0] + ROW_OLD[1] * (x - ROW_OLD[2])
        a, b = max(eave_row(x) + EAVE_T, 0), int(np.ceil(yt + 34)) if x >= 1344 else 0
        b = max(b, int(np.ceil(ROW_BOT(x))) + 2 if x >= X_HL else 0)
        if x < X_HL: b = max(b, 64)                                   # (the stray line under the eave's far end)
        clear[max(a, 0) - y0:max(b, 0) - y0, i] = True
    # (its far corner's trims, x 1297..1316, the painter's lit boards there: the wall's own boards, the corner an inside
    # one against Naruto's side wall, in its shade: no lit edge that would read as another building's)
    trims = np.zeros((h, w), bool); trims[:STRIP[2] - y0, 1297 - x0:1317 - x0] = True
    wallm = region & ((gb & ~(near_thing & acb)) | clear | trims)
    # the boards: vertical, along the street face (seams at Z = ZN - k BOARD, foreshortened), each its own tone, a grain
    # along it; dark under the eaves (the tiles' edge, the pent roof's row) and lighter lower down
    X = np.arange(x0, x1)[None, :] + 0.5 + np.zeros((h, 1)); Yr = np.arange(y0, y1)[:, None] + 0.5 + np.zeros((1, w))
    Z = F * XA / np.maximum(X - VPX, 1.0)
    kf = (ZN - Z) / BOARD; kb = np.floor(kf).astype(int)
    seam = (kf - kb) * BOARD * F * XA / Z ** 2 < 1.0                 # (the seam's pixel column)
    tone = np.random.default_rng(57).uniform(0.86, 1.14, 400)[np.clip(kb, 0, 399)]
    g = gaussian_filter(np.random.default_rng(58).normal(size=(h, w)), (3.0, 0.4)); g = 1 + 0.07 * g / (g.std() + 1e-9)
    top = np.array([[max(eave_row(int(x - 0.5)), 0)] for x in X[0]]).T + np.zeros((h, 1))
    rowb = ROW_BOT(X - 0.5)
    under_row = (X >= X_HL) & (Yr > rowb)
    dy = np.where(under_row, Yr - rowb, Yr - top)
    lt = np.clip(dy / 70.0, 0, 1) ** 0.8
    c = WALL_TOP * (1 - lt[..., None]) + WALL_LOW * lt[..., None]
    c = c * (tone * g * np.where(seam, 0.6, 1.0))[..., None]
    c = np.where((under_row & (Yr - rowb < 4))[..., None], c * (0.55 + 0.1 * (Yr - rowb))[..., None], c)   # (the row's shadow)
    c = c * (1 - 0.35 * np.exp(-(X - 1297.5) / 1.5))[..., None]       # (the inside corner with Naruto's side wall)
    city[y0:y1, x0:x1, :3][wallm] = c[wallm]; unlit[y0:y1, x0:x1, :3][wallm] = c[wallm]
    city[y0:y1, x0:x1, 3][wallm] = 255; unlit[y0:y1, x0:x1, 3][wallm] = 255
    done |= wallm
    # the row of round tiles on its ray, from the painter's far end to the frame's corner: across it the painter's own
    # profile (ROW_C, scaled to its thickness there); along it a tile every TILE m, the near end of each a rim catching the
    # light over the farther one's shadow; its far end a dome; the power cut at the painter's own ratio on his row
    pr = np.median(u0[clear & ~gb] @ LUMA + 1) / np.median(c0[clear & ~gb] @ LUMA + 1) if (clear & ~gb).any() else 1.0
    zl = F * X_H / (X_HL - VPX)
    for x in range(X_HL, x1):
        i = x - x0
        a, b = ROW_TOP(x), ROW_BOT(x)
        z = F * X_H / (x + 0.5 - VPX)
        s = (zl - z) / TILE; sk = s - np.floor(s)                     # (where along its tile, 0 at its far end)
        sp = TILE * F * X_H / z ** 2                                  # (a tile's length in px there)
        end = x - X_HL
        for y in range(int(np.floor(a)), int(np.ceil(b))):
            u = (y + 0.5 - a) / (b - a)
            if not 0 <= u < 1: continue
            if end < 3 and abs(u - 0.5) > 0.2 + 0.15 * end: continue  # (its far end, a dome)
            joint = sk * sp < 1.0 or (1 - sk) * sp < 1.0
            if joint and abs(u - 0.5) > 0.5 - 1.0 / (b - a): continue  # (round ends: the row narrows at each joint)
            cc = ROW_C[min(int(u * len(ROW_C)), len(ROW_C) - 1)].copy()
            if sk * sp < 1.0: cc = cc * 1.4                           # (a tile's far end, its rim catching the light,
            elif sk * sp < 2.0: cc = cc * 1.15                        # its collar)
            elif (1 - sk) * sp < 1.5: cc = cc * 0.5                   # (the farther tile's end under it, in its shadow)
            if end < 3: cc = cc * (0.85 + 0.05 * end)
            if 0 <= y - y0 < h:
                city[y, x, :3] = cc; unlit[y, x, :3] = cc * pr; city[y, x, 3] = unlit[y, x, 3] = 255; done[y - y0, i] = True
    return done


def drawn_pipe(city, unlit, box, sign, pal, name):
    """the downpipe as the image model drew it in its context crop (R28: tools/src/edits/naruroof_pipe_model.webp), laid
    into the street: boxed down to the street's pixels (its x4 brightened input undone), its colours brought to the
    painting's by a gain per channel (the model's wall round it in the band to this zone's: their medians), then
    only what is the pipe's (its rain head, the scupper's mouth, the pipe, its clamps, their shadows: where it differs
    from the wall this zone draws without its own pipe) laid over that wall, in the band, from under the coping to the
    sign; in the power cut its metal at the street lamps' share off (0.8), its shadows as they are"""
    src = os.path.join(EDITS, PIPE_MODEL)
    if not os.path.exists(src): return
    x0, y0, x1, y1 = box; h, w = y1 - y0, x1 - x0
    cx0, cy0, cx1, cy1 = PIPE_CROP
    d = np.asarray(Image.open(src).convert('RGB').resize((cx1 - cx0, cy1 - cy0), Image.BOX)).astype(float) / 255.0
    d = (d ** PIPE_GAMMA) * 255.0
    # the wall this zone draws without its own downpipe (the model cast again without it)
    NO_PIPE[0] = True
    try:
        nm0, nrm0, P0 = cast(box)
        M0 = mask(box, sign)
        c0w, u0w, _ = shade(box, nm0, nrm0, P0, pal, M0 & (nm0 != ''), city, unlit)
    finally:
        NO_PIPE[0] = False
    lampk = np.array([[NR.lamp(x, y) for x in range(x0, x1)] for y in range(y0, y1)])
    bx0, bx1 = PIPE_BAND
    rows = {x: (NF.edge_rows(x)[1] + 2, sign[x]) for x in range(bx0, bx1)}
    # the colours: a gain per channel, the model's wall in the band (away from both pipes) to this zone's
    wa, wb = [], []
    for x in range(bx0, bx1):
        if 1143 <= x <= 1152: continue
        for y in range(*rows[x]):
            if name[y - y0, x - x0] not in ('pil', 'par') or not M0[y - y0, x - x0]: continue
            wa.append(d[min(y, cy1 - 1) - cy0, x - cx0]); wb.append(c0w[y - y0, x - x0])
    wa, wb = np.array(wa), np.array(wb)
    gain = np.median(wb, 0) / np.maximum(np.median(wa, 0), 1.0)
    dfit = d * gain[None, None, :]
    for x in range(bx0, bx1):
        for y in range(*rows[x]):
            i, j = y - y0, x - x0
            if not M0[i, j] or nm0[i, j] == '': continue
            wall_c, wall_u = c0w[i, j] * (1 + (lampk[i, j] if x >= NF.XPF else 0.0)), u0w[i, j]
            q = dfit[min(y, cy1 - 1) - cy0, x - cx0]                  # (under the crop's last row, the pipe carried down)
            obj = np.abs(q - wall_c).max() > 3.0
            if obj:
                metal = q @ LUMA > wall_c @ LUMA
                city[y, x, :3] = q; unlit[y, x, :3] = q * (0.8 if metal else wall_u @ LUMA / max(wall_c @ LUMA, 1.0))
            else:
                city[y, x, :3] = wall_c; unlit[y, x, :3] = wall_u
            city[y, x, 3] = unlit[y, x, 3] = 255


def draw(city, unlit, box=BOX, write=True):
    """The zone (redraw_zones.py): the layers changed in place (whole-scene float RGBA); street_sun written (0 on what is
    redrawn; beyond the zone 'narufloor' from this zone's before crop) and roof_sway.webp's planters; returns what changed
    in box."""
    x0, y0, x1, y1 = box; h, w = y1 - y0, x1 - x0
    sign = NF.sign_top((x0, y0, x1, y1))
    name, nrm, P = cast(box)
    M = mask(box, sign)
    gbx = lambda x, y: city[y, x, :3].max() <= 12 and city[y, x, 1] >= city[y, x, 0]
    for x in range(STRIP[0], STRIP[1]):                # (the near wall on down to the canopy: the dark box over it)
        for y in range(STRIP[2], y1):
            if not gbx(x, y): break
            M[y - y0, x - x0] = True
    sky = M & (name == '')
    pal = palette(city)
    col, colu, lampable = shade(box, name, nrm, P, pal, M & ~sky, city, unlit)
    c0, u0 = city[y0:y1, x0:x1].copy(), unlit[y0:y1, x0:x1].copy()
    lampk = np.array([[NR.lamp(x, y) for x in range(x0, x1)] for y in range(y0, y1)])
    lit = M & ~sky
    city[y0:y1, x0:x1, :3][lit] = (col * (1 + np.where(lampable, lampk, 0.0))[..., None])[lit]
    unlit[y0:y1, x0:x1, :3][lit] = colu[lit]
    city[y0:y1, x0:x1, 3][lit] = 255; unlit[y0:y1, x0:x1, 3][lit] = 255
    city[y0:y1, x0:x1][sky] = 0; unlit[y0:y1, x0:x1][sky] = 0
    drawn_pipe(city, unlit, box, sign, pal, name)
    done = arcade(city, unlit, box) | M
    # the front by the corner, between the sign's end and the corner, over the canopy (the dark box): the front's own wall
    # there carried down (each column's light just over it), the painter's grain
    pg2 = tile(painter_grain(), h, w, 41, 3)
    for x in range(CANOPY_X[0], STRIP[0]):
        ref = c0[300 - y0:304 - y0, x - x0, :3].mean(0); refu = u0[300 - y0:304 - y0, x - x0, :3].mean(0)
        for y in range(STRIP[2], y1):
            q = c0[y - y0, x - x0, :3]
            if not (q.max() <= 12 and q[1] >= q[0]): break
            city[y, x, :3] = ref * pg2[y - y0, x - x0]; unlit[y, x, :3] = refu * pg2[y - y0, x - x0]
            city[y, x, 3] = unlit[y, x, 3] = 255; done[y - y0, x - x0] = True
    # the canopy's flashing where its roof meets the walls (the first row over its tiles), the arcade's roof's against
    # Naruto's side wall over its tiles' far end; a shade on the wall over the flashing
    for x in range(CANOPY_X[0], CANOPY_X[1]):
        for y in range(STRIP[2], y1 - 1):
            if done[y - y0, x - x0] and not done[y + 1 - y0, x - x0]:
                for lay in (city, unlit):
                    lay[y, x, :3] = np.array((15.0, 22.0, 38.0)); lay[y - 1, x, :3] *= 0.8
                break
    for x in range(1297, 1300):
        y = eave_row(x) - 1
        if y > NF.edge_rows(x)[0] + 3:
            for lay in (city, unlit): lay[y, x, :3] = np.array((15.0, 22.0, 38.0))
    # the near wall's corner with the front (W's last pier) one crisp lit column from the roof slab down to the canopy; the
    # balcony's slab round the corner at its own rows, as tools/naruto_floor.py draws its end over the opening (its edge's
    # lit line, its face, its lower arris), a step dimmer turned from the street, a shade under it
    sa, sb = SLAB_ROWS
    for y in range(86, y1):
        if not done[y - y0, STRIP[0] - x0]: break
        if sa <= y < sb: continue
        for lay, ref in ((city, pal['pier']), (unlit, pal['pier'])): lay[y, STRIP[0], :3] = ref * 1.35
    band = [NF.C['edge'] * 0.62, NF.C['edge2'] * 0.85] + [NF.C['end']] * (sb - sa - 4) + [NF.C['slab_arris'] * 0.9, pal['near'] * 0.5]
    for x in range(STRIP[0], STRIP[1]):
        g = 1 + 0.03 * ((x * 7 + 3) % 5 - 2)
        for j, y in enumerate(range(sa, sb)):
            for lay in (city, unlit): lay[y, x, :3] = band[j] * g * (0.9 if x == STRIP[1] - 1 else 1.0)
    swp = os.path.join(ASSETS, 'roof_sway.webp')
    sw_ = np.asarray(Image.open(swp).convert('RGBA')).copy()
    for x, y in planters(city, unlit, box, pal, sw_): done[y - y0, x - x0] = True
    # the pillar's side face beside the pipe (tools/naruto_floor.py's 'side', in the balcony's recess, as it leaves it): the
    # painter's grain on it, a little lighter lower down (the street's light from below)
    nb = NF.BOX
    R = NF.roles(nb, NF.lip_bottom(nb), NF.sign_top(nb))[0]
    pg = tile(painter_grain(), h, w, 29, 11)
    for yy, xx in zip(*np.nonzero(np.isin(R, ('side', 'side_low')))):
        x, y = nb[0] + xx, nb[1] + yy
        if not (x0 <= x < x1 and y0 <= y < y1): continue
        f = pg[y - y0, x - x0] * (0.94 + 0.12 * min(1.0, max(0.0, (y - 160) / 120.0)))
        for lay in (city, unlit): lay[y, x, :3] = lay[y, x, :3] * f
        done[y - y0, x - x0] = True
    for lay in (city, unlit): lay[y0:y1, x0:x1] = np.clip(np.round(lay[y0:y1, x0:x1]), 0, 255)
    changed = (city[y0:y1, x0:x1] != c0).any(-1) | (unlit[y0:y1, x0:x1] != u0).any(-1)
    # street_sun: as 'narufloor' wrote it in its box, this zone's before crop beyond it; 0 on what is redrawn
    sun = np.asarray(Image.open(os.path.join(ASSETS, 'street_sun.webp')).convert('RGB')).astype(float)
    bs = np.asarray(Image.open(os.path.join(EDITS, 'naruroof_before_sun.webp')).convert('RGB')).astype(float)
    nx1 = NF_BOX[2]
    sun[y0:y1, nx1:x1] = bs[:, nx1 - x0:]
    sun[y0:y1, x0:x1][done] = 0
    if write:
        Image.fromarray(np.clip(np.round(sun), 0, 255).astype(np.uint8), 'RGB').save(
            os.path.join(ASSETS, 'street_sun.webp'), 'WEBP', lossless=True, quality=100, method=6, exact=True)
        Image.fromarray(sw_, 'RGBA').save(swp, 'WEBP', lossless=True, quality=100, method=6, exact=True)
    draw.last = (name, nrm, P, M, done, sun, sw_)
    return changed


def model_lines():
    """the model's edges projected (for the report): [(name, [(x, y), ...])]"""
    pr = lambda X, Y, Z: (VPX + F * X / Z, VPY - F * (Y - EYE) / Z)
    zs = np.linspace(ZN, ZF, 20)
    xs = np.linspace(XP, XP + 12, 20)
    L = [('coping top P', [pr(XP - OVH, Y_CT, z) for z in zs]), ('coping foot P', [pr(XP - OVH, Y_CT - COP, z) for z in zs]),
         ('soffit edge', [pr(XP, Y_LB, z) for z in np.linspace(ZN, ZPIL, 10)]), ('terrace', [pr(XP, Y_T, z) for z in zs]),
         ('coping top near', [pr(x, Y_CT, ZN - OVH) for x in xs]), ('coping foot near', [pr(x, Y_CT - COP, ZN - OVH) for x in xs]),
         ('corner', [pr(XP, Y_LB, ZN), pr(XP, Y_CT, ZN)]), ('C corner', [pr(XP, Y_LB - 2, ZF), pr(XP, Y_CT, ZF)]),
         ('pipe axis', [pr(PX, Y_T - 0.36, PZ), pr(PX, Y_LB - 5, PZ)]),
         ('arcade row top', [(x, ROW_TOP(x) + 0.5) for x in (X_HL, 1456)]),
         ('arcade row bottom', [(x, ROW_BOT(x) + 0.5) for x in (X_HL, 1456)]),
         ('arcade corner', [(1297, 60), (1297, 330)])]
    return L


def _load(p, mode='RGBA'):
    return np.asarray(Image.open(p).convert(mode)).astype(float)


def before():
    """the zone's before crops: the layers in its box as tools/redraw_zones.py's first pass leaves them without this zone
    (each zone's before crop laid back, in its order, on the layers as they are), and street_sun beyond 'narufloor'"""
    import redraw_zones as RZ
    outs = [os.path.join(EDITS, f'naruroof_before_{t}.webp') for t in ('city', 'unlit', 'sun')]
    if any(os.path.exists(p) for p in outs):
        sys.exit('naruto_parapet: the before crops exist already (they are the layers before this zone: made once)')
    city, unlit = _load(os.path.join(ASSETS, 'layer_city_off.webp')), _load(os.path.join(ASSETS, 'street_unlit.webp'))
    for nm, cfg in RZ.ZONES.items():
        if nm == 'naruroof': continue
        a, b, c, d = cfg['box']
        city[b:d, a:c] = _load(os.path.join(EDITS, f'{nm}_before_city.webp'))
        unlit[b:d, a:c] = _load(os.path.join(EDITS, f'{nm}_before_unlit.webp'))
    x0, y0, x1, y1 = BOX
    sun = _load(os.path.join(ASSETS, 'street_sun.webp'), 'RGB')
    for a, t, mode in ((city, 'city', 'RGBA'), (unlit, 'unlit', 'RGBA'), (sun, 'sun', 'RGB')):
        Image.fromarray(np.clip(np.round(a[y0:y1, x0:x1]), 0, 255).astype(np.uint8), mode).save(
            os.path.join(EDITS, f'naruroof_before_{t}.webp'), 'WEBP', lossless=True, quality=100, method=6, exact=True)
    print('naruto_parapet: before crops written', BOX)


def preview(out, src=None):
    """the zone drawn on the layers of src (a folder with layer_city_off.webp, street_unlit.webp and roof_sway.webp as the
    zones before leave them; else assets/), crops before and after, x3 and x6 with the model's lines; the new layers and
    roof_sway.webp in out/layers"""
    global ASSETS
    os.makedirs(os.path.join(out, 'layers'), exist_ok=True)
    src = src or ASSETS
    L = {t: _load(os.path.join(src, f)) for t, f in (('city', 'layer_city_off.webp'), ('unlit', 'street_unlit.webp'))}
    A = {t: a.copy() for t, a in L.items()}
    keep = ASSETS
    import shutil
    for f in ('roof_sway.webp', 'street_sun.webp'):
        shutil.copy(os.path.join(src if os.path.exists(os.path.join(src, f)) else keep, f), os.path.join(out, 'layers', f))
    ASSETS = os.path.join(out, 'layers')
    try:
        draw(A['city'], A['unlit'], BOX, write=True)
    finally:
        ASSETS = keep
    sky = np.array((62.0, 45.0, 86.0))
    def comp(a, b):
        c = a[b[1]:b[3], b[0]:b[2]]; al = c[..., 3:4] / 255
        return c[..., :3] * al + sky * (1 - al)
    from PIL import ImageDraw
    for tag, b, k in (('roof', (1110, 20, 1310, 200), 6), ('right', (1260, 0, 1456, 175), 6), ('wide', (1060, 0, 1456, 400), 3)):
        for t in ('city', 'unlit'):
            for st, lay in (('before', L[t]), ('after', A[t])):
                z = comp(lay, b)
                for gm, suf in ((1.0, ''), (0.5, 'b')):
                    im = Image.fromarray(np.clip(np.round(255 * (z / 255) ** gm), 0, 255).astype(np.uint8))
                    im = im.resize(((b[2] - b[0]) * k, (b[3] - b[1]) * k), Image.NEAREST)
                    im.save(os.path.join(out, f'{tag}_{t}_{st}_x{k}{suf}.png'))
                    if st == 'after' and t == 'city' and suf == 'b':
                        g = ImageDraw.Draw(im)
                        for nm, pts in model_lines():
                            q = [((px - b[0]) * k, (py - b[1]) * k) for px, py in pts]
                            g.line(q, fill=(255, 200, 0) if 'arcade' in nm else (0, 255, 200) if 'pipe' in nm else (255, 80, 80), width=1)
                        im.save(os.path.join(out, f'{tag}_{t}_model_x{k}.png'))
    for t, f in (('city', 'layer_city_off.webp'), ('unlit', 'street_unlit.webp')):
        Image.fromarray(np.clip(np.round(A[t]), 0, 255).astype(np.uint8), 'RGBA').save(os.path.join(out, 'layers', f), 'WEBP', lossless=True, quality=100, method=6, exact=True)
    print('naruto_parapet: preview in', out)


if __name__ == '__main__':
    if '--before' in sys.argv:
        before()
    elif '--preview' in sys.argv:
        i = sys.argv.index('--preview')
        preview(sys.argv[i + 1], sys.argv[i + 2] if len(sys.argv) > i + 2 else None)
    else:
        print(__doc__)
