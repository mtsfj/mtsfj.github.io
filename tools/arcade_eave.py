#!/usr/bin/env python3
"""The arcade's low roof under the rooftop unit, redrawn on the pixel grid (the owner's pick #11, "+ gouttière").

    (a module: tools/redraw_zones.py's zone 'arceave' calls draw() on the street as the zones before it leave it)

What was there (x 1236..1456, y 290..400): the roof's front edge, a row of 37 px "blocks" (the eave tiles' front lips,
one per tile, never foreshortened, and drifting off the street's rays toward the left, 5 px at the corner), shapeless
pale tufts on top of them, and under the unit a blurred box (its stand). Now, in the street's own perspective (VP
(700, 615), the eye 1.41 m up, f 959.5 px, as tools/r6_sprites.py; a line along the street keeps v = (615 - y) /
(x - 700), its height over the eye over its distance from the street's axis):
- the eave tiles: the front band of the eave on the painter's two rays (its top v 0.411, its lip v 0.386, measured on
  the right where his row is straight: X 4.61 m, 3.19..3.31 m up), one tile every 30 cm along the street, so they shorten
  toward the vanishing point (37 px on the right, 20 at the end): round tiles lying along the eave, each lit along its
  top, darker as it turns under (the painter's tones, dithered a row where they meet), its far end a dome whose rim
  catches the light, laid over the farther tile, which is in its shadow there; no two quite the same shade; the row ends
  where the painter's did;
- above it, no tufts: the dark behind (the tall building's wall), from the dark round them;
- the unit's stand: a plain steel frame, a rail under each bottom edge of the unit (the side one on the unit's ray, the
  front one level), a leg at each corner in sight down behind the tiles, the rails' lit top edge and the legs' lit side
  (the unit's metal); the unit's side face carried down to its bottom edge (its plain metal under the fan guard);
- the gutter: half-round (9.4 cm), hung in front of the tiles' lip (its rim 1 cm under the eave, 3 cm in front): seen from
  below, its rolled rim lit by the sky (its top edge, one pixel), its round belly darker as it turns under (its shadow
  side, against the black under the eave), a hanger every 60 cm (a dark strap round the belly, hooked over the rim: its
  cross-section, undistorted, the plane it lies in facing us), closed at the eave's end; the painter's downpipe at the
  building's corner carried up the wall to it (the wall camera, street.js R6C, laid 6 px right and 4 down from where
  tools/r6_sprites.py puts it: beside the pipe, 2 px under the gutter, as it was under the eave's lip);
- at the row's end, in front of Ichiraku's sign: what the painter's higher row covered is the sign's underside again (its
  maroon, from round it) and, right of the sign, the dark.
Colours are the painter's: each element takes pixels of his row (the lit tops, the faces, the lip), of the unit's metal
and of his downpipe. The power cut: the same picture times the painter's own darkening there (unlit over lit, smoothed,
channel by channel), which is about 1 here (no light of the street reaches it).
"""
import numpy as np
from scipy.ndimage import gaussian_filter

VP = (700.0, 615.0)
F = 959.5                                      # px per m at 1 m (tools/r6_sprites.py)
EYE = 1.41
XE = 4.61                                      # the eave's front (m from the street's axis)
VT, VL = 0.411, 0.386                          # its tiles' top and lip (rays)
TILE = 0.30                                    # a tile's width along the street (m)
X_END = 1238                                   # the row's far end (the painter's), its last tile whole from there
GUT = dict(xg=4.58, yr=3.18, r=0.047)          # the gutter: its axis, its rim's height, its radius (m)
HANG = 0.60                                    # a hanger every 60 cm
G_END = 1246                                   # the gutter's closed end (its axis's x there)
PIPE = (1302, 1308)                            # the painter's downpipe's columns (its dark edges included), up from its top
PIPE_TOP = 418
SIGN_EDGE = 1266                               # Ichiraku's sign's right edge (what is cleared left of it is its underside)
UNIT_V = 0.4684                                # the unit's bottom edges: its side (a ray) meets its front (level, y 292)
UNIT_CORNER = (1388, 292)                      # at its near corner; its far edge at x 1359
UNIT_FAR = 1359
BOX_V = 0.505                                  # (the painter's box under it rose to this ray, left of the unit)
TUFT_V = 0.455                                 # (his tufts and his higher row, to this ray)

# the painter's colours (picked from his row, the unit's side face and the black round them, in the street as it is)
C = dict(
    tile_top=(34, 44, 72), tile_up=(21, 31, 55), tile_mid=(14, 23, 40), tile_low=(6, 15, 22), tile_lip=(13, 22, 38),
    joint=(2, 8, 12),
    bead=(58, 66, 104), g_face=(30, 38, 64), g_mid=(20, 27, 47), g_low=(11, 17, 30), g_belly=(5, 9, 17), strap=(2, 5, 9),
    rail_top=(40, 42, 76), rail=(14, 17, 33), leg_lit=(26, 29, 54), leg=(10, 12, 24),
    face=(12, 21, 39), face_edge=(28, 42, 74),
)
LUMA = np.array([0.299, 0.587, 0.114])


def ray_y(x, v):
    """The row (continuous; a pixel's centre at its row + 0.5) of the ray v at column x."""
    return VP[1] - v * (x + 0.5 - VP[0])


def row(x, v):
    return int(np.floor(ray_y(x, v)))


def gutter_hit(x, y):
    """Where the ray through pixel (x, y)'s centre meets the gutter's outer surface (its lower half, the side toward the
    eye): (its distance along the street Z, the angle from the front rim round the belly, degrees), or None."""
    g = GUT; dx, dy = (x + 0.5 - VP[0]) / F, (VP[1] - (y + 0.5)) / F
    a = dx * dx + dy * dy; b = -2 * (dx * g['xg'] + dy * (g['yr'] - EYE)); c = g['xg'] ** 2 + (g['yr'] - EYE) ** 2 - g['r'] ** 2
    disc = b * b - 4 * a * c
    if disc < 0: return None
    for l in sorted(((-b - np.sqrt(disc)) / (2 * a), (-b + np.sqrt(disc)) / (2 * a))):
        X, Y = l * dx, EYE + l * dy
        if Y <= g['yr'] + 1e-9:
            nx, ny = (X - g['xg']) / g['r'], (Y - g['yr']) / g['r']
            if nx * X + ny * (Y - EYE) < 0:
                return l, float(np.degrees(np.arctan2(-ny, -nx)))   # (0 at the front rim, 90 under it)
    return None


TONE = (1.0, 0.95, 1.04, 0.97, 1.02, 0.94, 1.03, 0.98)   # (no two tiles quite alike: each its own shade)


def step(t, levels, last, parity, d):
    """The tone for t over descending thresholds ((t0, tone0), (t1, tone1), ...), else last; within d of a threshold, the
    two tones meeting there in a checkerboard (parity: x + y)."""
    for i, (t0, c) in enumerate(levels):
        nxt = levels[i + 1][1] if i + 1 < len(levels) else last
        if abs(t - t0) < d: return c if parity % 2 else nxt
        if t > t0: return c
    return last


def fill(img, hole, src, s=3.0):
    """img's colours over hole, from the pixels src round it (gaussian normalised convolution, widened until it reaches)."""
    wgt = src.astype(float)
    while True:
        num = np.stack([gaussian_filter(img[..., c] * wgt, s) for c in range(3)], -1); den = gaussian_filter(wgt, s)[..., None]
        if (den[hole] > 1e-3).all() or s > 40: return num / np.maximum(den, 1e-6)
        s *= 1.5


def draw(O, U, box):
    """O, U: the street and its power cut over box (x0, y0, x1, y1), RGB floats, as the zones before leave them.
    Returns the new street, the new power cut and the mask of what changed."""
    x0, y0, x1, y1 = box; h, w = O.shape[:2]
    new = O.copy(); role = np.full((h, w), '', 'U6')
    X = np.arange(x0, x1)
    Lo = O @ LUMA
    put = lambda y, xi, c, r: (new.__setitem__((y - y0, xi), C[c] if isinstance(c, str) else c), role.__setitem__((y - y0, xi), r))

    # 1. what goes: the tufts, the painter's box and his higher row, from over them down to the new row's top
    for xi, x in enumerate(X):
        if x < X_END - 2: continue
        top = row(x, VT)
        if x < SIGN_EDGE:                              # (in front of the sign: only his row's blue-grey pixels)
            for y in range(row(x, 0.47), row(x, 0.37)):
                p = O[y - y0, xi]
                if p[2] > p[0] + 4 and p[1] > p[0]: role[y - y0, xi] = 'sign'
            continue
        if x < UNIT_FAR: hi = row(x, TUFT_V if x < 1330 else BOX_V)
        elif x <= UNIT_CORNER[0]: hi = row(x, UNIT_V) + 1
        else: hi = UNIT_CORNER[1] + 1
        for y in range(max(hi, y0), top): role[y - y0, xi] = 'clear'
    cl = role == 'clear'                               # the dark behind: from the dark round what goes
    new[cl] = fill(O, cl, ~cl & (Lo < 5) & (O[..., 1] >= O[..., 2]) & (role == ''))[cl]
    sg = role == 'sign'                                # the sign's underside: its maroon from round it, none of the eave's
    if sg.any():
        ys, xs = np.nonzero(sg)
        src = np.zeros((h, w), bool); src[max(ys.min() - 6, 0):ys.max() + 16, max(xs.min() - 10, 0):SIGN_EDGE - x0] = True
        src &= (O[..., 0] >= O[..., 2] - 4) & (Lo > 5) & ~sg
        for xi, x in enumerate(X):
            if x >= X_END - 2: src[row(x, 0.47) - y0:row(x, VL) - y0 + 2, xi] = False
        new[sg] = fill(O, sg, src, 2.5)[sg]

    # 2. the unit's side face down to its bottom edge (its plain metal, its far edge lit), the stand under it
    cx, cy = UNIT_CORNER
    for xi, x in enumerate(X):
        if UNIT_FAR <= x <= cx:
            for y in range(cy + 1, row(x, UNIT_V) + 1):
                put(y, xi, 'face_edge' if x <= UNIT_FAR + 1 else 'face', 'face')
    for xi, x in enumerate(X):
        top = row(x, VT)
        if UNIT_FAR <= x <= cx:                        # the side rail, under the unit's ray
            yb = row(x, UNIT_V) + 1
        elif x > cx:                                   # the front rail, level
            yb = cy + 1
        else: continue
        for k, c in ((0, 'rail_top'), (1, 'rail'), (2, 'rail')):
            if yb + k < top: put(yb + k, xi, c, 'stand')
        for lx in ((UNIT_FAR, UNIT_FAR + 1), (cx - 1, cx)):   # a leg at each corner in sight: 2 px, its left side lit
            if x in lx:
                for y in range(yb + 3, top): put(y, xi, 'leg_lit' if x == lx[0] else 'leg', 'stand')

    # 3. the tiles: their front band between the two rays, a tile every TILE metres (foreshortened toward the vanishing
    # point), each a round tile lying along the eave: lit along its top, darker as it turns under, its far end a dome a
    # pixel proud of it whose rim catches the light, laid over the farther tile (in its shadow there)
    z_end = F * XE / (X_END - 0.5 - VP[0])
    jx = [VP[0] + F * XE / (z_end - k * TILE) for k in range(int((z_end - F * XE / (x1 + 40 - VP[0])) / TILE) + 1)]

    def body(k, n, x):                                 # a tile's colour at row k of n, from its top (its tones dithered
        t = 1 - (k + 0.5) / n                          # a row where they meet, as the painter's)
        if k == 0: return np.array(C['tile_top'], float)
        if k == n - 1: return np.array(C['tile_lip'], float)
        return np.array(C[step(t, ((0.68, 'tile_up'), (0.45, 'tile_mid')), 'tile_low', x + k, 0.045)], float)
    for xi, x in enumerate(X):
        if x < X_END: continue
        top, bot = row(x, VT), row(x, VL); n = bot - top + 1; xc = x + 0.5
        i = max([q for q in range(len(jx)) if jx[q] <= xc] or [0])
        a, b = jx[i], (jx[i + 1] if i + 1 < len(jx) else x1 + 60)
        rx = min(0.42 * n, 0.4 * (b - a))              # (its dome's depth, in columns)
        for k in range(n):
            yr = (k + 0.5) / n * 2 - 1                 # (-1 at its top, 1 at its lip)
            edge = a + rx * (1 - np.sqrt(max(1 - yr * yr, 0)))
            col = body(k, n, x) * TONE[i % len(TONE)]
            if xc < edge:                              # left of the dome: the farther tile, in its shadow
                col = col * (0.45 if edge - xc < 1.5 else 0.7) if i > 0 else np.array(C['joint'], float)
                if i == 0: continue                    # (past the row's end: nothing)
            elif xc - edge < 1.0:                      # the dome's rim
                col = np.array(C['tile_top' if yr < 0.2 else 'tile_up'], float) * (1.0 if yr < 0.2 else 0.85)
            elif xc - edge < 2.0 and yr > -0.6:
                col = col * 1.08
            if b - xc < 1.0 and i + 1 < len(jx): col = col * 0.8   # (under the nearer tile's dome)
            put(top + k, xi, np.clip(col, 0, 255), 'tile')
        if a + 0.3 * rx <= xc <= a + 1.5 * rx:         # the dome stands a pixel proud of the row: its rim over the top line
            put(top - 1, xi, np.array(C['tile_up'], float) * (0.85 if xc > a + 1.1 * rx else 1.0), 'tile')

    # 4. the gutter, in front of the tiles' lip: per pixel where its ray meets the half-cylinder, shaded round the belly
    zh = []                                            # (its hangers: every HANG metres from 25 cm in from its end)
    z = F * GUT['xg'] / (G_END - VP[0]) - 0.25
    while z > F * GUT['xg'] / (x1 + 30 - VP[0]): zh.append(z); z -= HANG
    for xi, x in enumerate(X):
        if x < G_END - 10: continue
        col_rows = []
        for y in range(row(x, 0.396) - 1, row(x, 0.369) + 2):
            hit = gutter_hit(x, y)
            if hit is None: continue
            z, ang = hit
            if VP[0] + F * GUT['xg'] / z < G_END: continue   # (past its closed end)
            c = 'bead' if ang < 12 else step(-ang, ((-38, 'g_face'), (-62, 'g_mid'), (-86, 'g_low')), 'g_belly', x + y, 4.0)
            hz = min(zh, key=lambda q: abs(q - z)) if zh else -9
            if abs(hz - z) * F * GUT['xg'] / z ** 2 < 0.6: c = 'g_low' if c == 'bead' else 'strap'   # (a hanger's strap)
            put(y, xi, c, 'gutter'); col_rows.append(y)
        if col_rows:                                   # its rim: one lit pixel per column, the column's first
            for y in col_rows[1:]:
                if role[y - y0, xi] == 'gutter' and np.array_equal(new[y - y0, xi], C['bead']): new[y - y0, xi] = C['g_face']
            if not np.array_equal(new[col_rows[0] - y0, xi], C['g_low']): new[col_rows[0] - y0, xi] = C['bead']
    for z in zh:                                       # the hangers' hooks: a dark pixel over the rim
        xa = VP[0] + F * (GUT['xg'] - GUT['r']) / z; xi = int(np.floor(xa)) - x0
        if not (0 <= xi < w) or xa < G_END: continue
        ys = np.nonzero(role[:, xi] == 'gutter')[0]
        if len(ys): put(ys[0] + y0 - 1, xi, 'strap', 'gutter')

    # 5. the downpipe up the wall, from its top to under the gutter: each column the painter's own pixel of it
    prow = O[PIPE_TOP + 10 - y0, PIPE[0] - x0:PIPE[1] - x0].copy()
    for x in range(*PIPE):
        xi = x - x0; ys = np.nonzero(role[:, xi] == 'gutter')[0]
        if not len(ys): continue
        for y in range(ys[-1] + y0 + 1, min(PIPE_TOP + 8, y1)): put(y, xi, prow[x - PIPE[0]], 'pipe')

    mask = (np.abs(new - O).max(-1) > 0) | (role != '')
    # the power cut: the same, times the painter's darkening there (channel by channel, smoothed)
    dark = np.stack([(gaussian_filter(U[..., c], 4.0) + 1.0) / (gaussian_filter(O[..., c], 4.0) + 1.0) for c in range(3)], -1)
    unew = U.copy(); unew[mask] = np.clip(new * np.clip(dark, 0, 1.5), 0, 255)[mask]
    return np.clip(new, 0, 255), unew, mask

