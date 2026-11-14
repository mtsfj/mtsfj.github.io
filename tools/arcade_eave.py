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
- above it, no tufts: the roof's surface. The eave is the foot of a canopy along the arcade's front, a lean-to up to
  the building's wall, at a kawara roof's 6/10 pitch: steeper than the eye's line to the eave (0.411), so from the
  street its surface shows over the tiles (as the painter's tufts and higher row said), from their top line up to the
  wall's foot, and as far as the arcade goes (its end, where the row ends, a slope rising from the last tile: in front
  of Ichiraku's sign too); lit by the sky, as much of it as the unit and its stand leave (their contact shadow under
  them, soft round it); past the arcade's end and above the wall's foot, the dark (from the dark round them);
- what holds the unit (the owner: "la ventilation, c'est quoi dessous ?"; it stood on an empty dark frame whose feet
  were hidden behind the tiles): a roof-mounted stand, as units on a canopy's slope stand in Japan, of 3 cm angle
  irons: at each end of the unit a frame, its leg at the front (downhill, 20 cm), a short one at the back, the top bar
  the unit's foot is bolted to, standing on a bar that lies on the roof down its slope; a rail under the unit's face
  ties the two. Each pixel's ray from the eye followed into that model, each iron drawn as a member of a few pixels
  (the owner: "l'aplat gris"; drawn flat, the frame and the casing over it read as one grey slab): its faces toward
  the street lit at most as the unit's face (darker toward the roof), toward us dark as the unit's end, facing down
  darker, each with its edge toward the light a step lighter and its other edge a step darker; open between them: the
  unit's underside in its shadow, the roof's tiles (a course every 20 cm up the slope, a line a step darker under each)
  and its contact shadow. The unit's face carried down to its bottom edge on its ray (to y 312 at its far edge, as its
  top's ray demands): its fan guard, cut level at y 290 by its zone, completed (its upper half mirrored about the line
  through its hub along the face: the rings close, the guard round), under it the painter's casing, each column his
  metal there, its base pan's last two rows in its shadow;
- the gutter: half-round (9.4 cm), hung in front of the tiles' lip (its rim 1 cm under the eave, 3 cm in front): seen from
  below, its rolled rim lit by the sky (its top edge, one pixel), its round belly darker as it turns under (its shadow
  side, against the black under the eave), a hanger every 60 cm (a dark strap round the belly, hooked over the rim: its
  cross-section, undistorted, the plane it lies in facing us), closed at the eave's end; the painter's downpipe at the
  building's corner carried up the wall to it (the wall camera, street.js R6C, laid 6 px right and 4 down from where
  tools/r6_sprites.py puts it: beside the pipe, 2 px under the gutter, as it was under the eave's lip);
- at the row's end, in front of Ichiraku's sign: what the painter's higher row covered is the sign's underside again (its
  maroon, from round it), but for the roof's last wedge over the row.
Colours are the painter's: each element takes pixels of his row (the lit tops, the faces, the lip), of the unit's metal
and of his downpipe; the roof and the stand ramps of his tones, the roof's mixed by a 2x2 ordered dither. The power cut:
the same picture times the painter's own darkening there (unlit over lit, smoothed, channel by channel), which is about 1
here (no light of the street reaches it).
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
BOX_V = 0.505                                  # (the painter's box under the unit rose to this ray, left of it)
TUFT_V = 0.455                                 # (his tufts and his higher row, to this ray)

# the unit and what holds it, in metres (X right of the street's axis, Y up, Z ahead; the eye at (0, EYE, 0)). The
# painter's unit: its face with the fan along the street (its top edge on the ray 0.594), its near vertical edge between
# columns 1404 and 1405, its far one at x 1359, its end toward us dark (his service panel, to x 1441); its bottom edges
# from its near bottom corner (1405, 291): the face's on a ray (down to y 312 at its far edge, as its top's ray demands),
# the end's level. A 0.65 m unit: its face 4.78 m from the axis, 17 cm behind the eave's front, its bottom 3.61 m up.
UC = (1405.0, 291.0)                           # (continuous: right of column 1404, under row 290)
UF = 1359.0
XU, DU = 4.78, 0.244                           # its face, its depth
VB = (VP[1] - UC[1]) / (UC[0] - VP[0])         # its bottom edges' ray (0.4596)
VTOP = 0.5943                                  # its top's
ZC, ZF = F * XU / (UC[0] - VP[0]), F * XU / (UF - VP[0])   # its near and far ends (6.51, 6.96 m)
YB = EYE + VB * XU                             # its bottom
UNIT_TOP = 289                                 # (rows the painter's face ends at: the casing drawn from here, the grille's
GRILLE = (1361, 1386, 291)                     # panel's columns from its bottom; his near end's from y 291)
# the fan guard (zone 'fan': its panel cut level at y 290, so its rings ended flat there, the casing under it a flat wedge
# that read as a grey slab): it is round, so its lower half is its upper half mirrored about the line through its hub
# along the face (a ray), down to the panel's edge mirrored from its top edge (the zone's polygon), on the rows under 290
GUARD = dict(hub=(1372.5, 256.5), v=0.533, top=((1361, 222), (1387, 207)))
# the roof under it: the eave is a lean-to roof's foot (a canopy along the arcade's front, up to the building's wall
# behind the unit), at a kawara roof's 6/10 pitch: steeper than the eye's line to the eave (0.411), so its surface shows
# over the tiles, from their top line up to the wall, and as far as the arcade goes (the row's far end, X_END); steep
# enough that under the unit it is the roof that shows, not the dark past the arcade's end
S = 0.6                                        # its pitch (rise over run)
YR0 = EYE + VT * XE                            # it runs on from the tiles' top line (3.30 m at XE)
XW = 5.45                                      # the wall behind (the canopy 84 cm deep; the unit's back 43 cm from it)
AI = 0.025                                     # the stand's angle irons (25 mm)
COURSE = 0.20                                  # the roof's tiles: a course every 20 cm up the roof (in X)


def roof_y(X):
    return YR0 + S * (np.asarray(X, float) - XE)


def parts():
    """The unit and its stand, as boxes ((x0, y0, z0), (x1, y1, z1), what it is); a 'sled' box's Y is over the roof's
    plane (Y - S X), so it lies on it. The stand is a roof-mounted one, as units on a canopy's slope sit: at each end of
    the unit a frame of angle irons (its leg at the front, the downhill side, a short one at the back, the top bar the
    unit's foot is bolted to), standing on a bar that lies on the roof down its slope; a rail under the unit's face
    joins the two."""
    c = YR0 - S * XE                               # (the roof's plane: Y - S X = c)
    P = [((XU, YB, ZC), (XU + DU, EYE + VTOP * XU, ZF), 'unit')]
    for z0, z1 in ((ZC, ZC + AI), (ZF - AI, ZF)):
        P += [((XU - 0.02, c, z0), (XU + DU + 0.02, c + AI, z1), 'sled'),
              ((XU, float(roof_y(XU + AI / 2)) + AI, z0), (XU + AI, YB, z1), 'leg'),
              ((XU + DU - AI, float(roof_y(XU + DU - AI / 2)) + AI, z0), (XU + DU, YB, z1), 'leg'),
              ((XU, YB - AI, z0), (XU + DU, YB, z1), 'bar')]
    P += [((XU, YB - AI, ZC), (XU + AI, YB, ZF), 'rail')]
    return P


def enter(o, d, lo, hi, shear=0.0):
    """Where rays o + t d enter the box lo..hi (its Y taken as Y - shear X): (t, the axis they enter by), t inf if
    they miss it. o, d: (3, n) arrays."""
    oo = (o[0], o[1] - shear * o[0], o[2]); dd = (d[0], d[1] - shear * d[0], d[2])
    tmin = np.full(d[0].shape, -np.inf); tmax = np.full(d[0].shape, np.inf); ax = np.zeros(d[0].shape, int)
    for k in range(3):
        with np.errstate(divide='ignore', invalid='ignore'):
            t1 = (lo[k] - oo[k]) / dd[k]; t2 = (hi[k] - oo[k]) / dd[k]
        a = np.where(np.isnan(t1), -np.inf, np.minimum(t1, t2)); b = np.where(np.isnan(t1), np.inf, np.maximum(t1, t2))
        ax = np.where(a > tmin, k, ax); tmin = np.maximum(tmin, a); tmax = np.minimum(tmax, b)
    return np.where((tmax >= tmin) & (tmin > 1e-6), tmin, np.inf), ax


def sky(p, n, skip, m=96):
    """How much of the sky the points p (3, n) see over their face (normal n): the share of m directions (cosine-
    weighted round n, fixed: a Fibonacci spiral) that leave past the unit and its stand (the part `skip` aside)."""
    n = np.asarray(n, float) / np.linalg.norm(n)
    t1 = np.cross(n, (0.0, 0.0, 1.0)); t1 /= np.linalg.norm(t1); t2 = np.cross(n, t1)
    seen = np.zeros(p.shape[1])
    for i in range(m):
        u, ph = (i + 0.5) / m, i * np.pi * (3 - np.sqrt(5))
        r = np.sqrt(u); d = r * np.cos(ph) * t1 + r * np.sin(ph) * t2 + np.sqrt(1 - u) * n
        D = np.repeat(d[:, None], p.shape[1], 1); free = np.ones(p.shape[1], bool)
        for j, (lo, hi, kind) in enumerate(parts()):
            if j == skip: continue
            t, _ = enter(p + 1e-4 * n[:, None], D, lo, hi, S if kind == 'sled' else 0.0)
            free &= ~np.isfinite(t)
        seen += free
    return seen / m


BAYER = np.array([[0.125, 0.625], [0.875, 0.375]])


def ramp(t, cols, x, y):
    """A colour of the ramp cols at t (0 its first, 1 its last), two neighbours mixed by a 2x2 ordered dither (the
    painter's way between two tones), no new colour."""
    k = np.clip(t, 0, 1) * (len(cols) - 1); i = int(np.floor(k)); f = k - i
    if i >= len(cols) - 1: return np.array(cols[-1], float)
    return np.array(cols[i + 1] if f > BAYER[y % 2, x % 2] else cols[i], float)

# the painter's colours (picked from his row, the unit's side face and the black round them, in the street as it is)
C = dict(
    tile_top=(34, 44, 72), tile_up=(21, 31, 55), tile_mid=(14, 23, 40), tile_low=(6, 15, 22), tile_lip=(13, 22, 38),
    joint=(2, 8, 12),
    bead=(58, 66, 104), g_face=(30, 38, 64), g_mid=(20, 27, 47), g_low=(11, 17, 30), g_belly=(5, 9, 17), strap=(2, 5, 9),
)
# the roof, the stand and the unit's underside: ramps from dark to lit, in the painter's tones (the tiles' navy for the
# roof, a little under their lit top; for the irons' faces toward the street the unit's lit metal at most, for those
# toward us its dark end's tones; under the unit, its shadow)
R_ROOF = [(4, 8, 14), (8, 13, 24), (13, 20, 35), (18, 26, 45), (23, 32, 55), (27, 37, 62)]
R_LIT = [(10, 13, 25), (15, 19, 35), (21, 25, 45), (27, 31, 56), (32, 37, 66)]
R_END = [(4, 7, 13), (8, 11, 21), (12, 15, 28), (18, 22, 40)]
UNDER = (3, 6, 12)
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


def draw(city, unlit, box):
    """The zone's tool (tools/redraw_zones.py, zone 'arceave'): city, unlit, the street and its power cut whole (RGBA
    floats) as the zones before it leave them; draws in box, in place. Returns the mask of what changed there."""
    x0, y0, x1, y1 = box
    new, unew, mask = draw_box(city[y0:y1, x0:x1, :3].copy(), unlit[y0:y1, x0:x1, :3].copy(), box, city[..., :3])
    city[y0:y1, x0:x1, :3][mask] = new[mask]; unlit[y0:y1, x0:x1, :3][mask] = unew[mask]
    return mask


def draw_box(O, U, box, above=None):
    """O, U: the street and its power cut over box (x0, y0, x1, y1), RGB floats, as the zones before leave them; above:
    the street whole (what the guard's lower half is mirrored from, over the box). Returns the new street, the new power
    cut and the mask of what changed."""
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
        if x < UF: hi = row(x, TUFT_V if x < 1330 else BOX_V)
        elif x < UC[0]: hi = UNIT_TOP if x >= GRILLE[1] else GRILLE[2]   # (the unit's face: from under the grille)
        else:                                          # (under its end; past it, from where the roof meets the wall)
            hi = int(UC[1]) if x < VP[0] + F * (XU + DU) / ZC else min(int(UC[1]), row(x, (float(roof_y(XW)) - EYE) / XW))
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

    # 2. the unit's foot, what holds it and what it stands on: each pixel cleared above the tiles (and under the painter's
    # unit), its ray from the eye followed into the scene. What it meets first: the unit's face (its casing under the
    # grille, down to its bottom edge: each column the painter's own metal there, its last row in the shadow of the
    # base), its underside (seen from below, in its own shadow), the stand's angle irons (their faces toward the street
    # lit as the unit's face, darker toward the roof; toward us dark as the unit's end; facing down darker still), the
    # bars lying on the roof (their top as lit as the sky leaves it), the roof (lit by the sky as much as the unit and
    # the stand leave it: under them their contact shadow, soft round it), else the dark behind (the wall, past the
    # arcade's end: what step 1 filled)
    P = parts(); c0 = YR0 - S * XE; zend = F * XE / (X_END - 0.5 - VP[0])
    strip = np.median(O[280 - y0:289 - y0, 1390 - x0:1399 - x0].reshape(-1, 3), 0)   # (his casing's metal, the grille's
    cand = role == 'clear'                                                            # right)
    for xi, x in enumerate(X):                            # (and, in front of Ichiraku's sign, the roof's last wedge over
        if X_END <= x < SIGN_EDGE: cand[row(x, VT) - 12 - y0:row(x, VT) - y0, xi] = True   # the row: only where hit)
    ys, xs = np.nonzero(cand)
    px, py = xs + x0, ys + y0; n = len(px)
    d = np.stack([(px + 0.5 - VP[0]) / F, (VP[1] - (py + 0.5)) / F, np.ones(n)]); o = np.zeros_like(d); o[1] = EYE
    best = np.full(n, np.inf); what = np.full(n, -1); axis = np.zeros(n, int)
    for j, (lo, hi, kind) in enumerate(P):
        t, ax = enter(o, d, lo, hi, S if kind == 'sled' else 0.0)
        nb = t < best; best[nb] = t[nb]; what[nb] = j; axis[nb] = ax[nb]
    with np.errstate(divide='ignore', invalid='ignore'):  # the roof's plane (Y - S X = c0), from the eave to the wall, as
        tr = (c0 - EYE) / (d[1] - S * d[0])                # far as the arcade goes
    nb = (tr > 0) & (tr * d[0] >= XE) & (tr * d[0] <= XW) & (tr <= zend) & (tr < best)
    best[nb] = tr[nb]; what[nb] = len(P)
    hp = o + np.where(np.isfinite(best), best, 0) * d    # (where each ray meets what it meets)
    nrm = (-S, 1.0, 0.0)
    lit = np.ones(n)                                      # the sky each roof point, each bar's top, sees
    on_roof = what == len(P)
    if on_roof.any(): lit[on_roof] = sky(hp[:, on_roof], nrm, -1)
    for j, (lo, hi, kind) in enumerate(P):
        sel = (what == j) & (axis == 1) & (kind == 'sled')
        if sel.any(): lit[sel] = sky(hp[:, sel], nrm, j)
    last = {}                                             # (each column's last row of casing: the base's shadow line)
    for i in np.nonzero((what == 0) & (axis == 0))[0]: last[px[i]] = max(last.get(px[i], 0), py[i])
    key = np.full((h, w), -1)                             # (what each pixel shows: its part and its face; the roof's
    for i in range(n):                                    # course, for the tiles' lines)
        if what[i] >= 0: key[py[i] - y0, px[i] - x0] = what[i] * 3 + axis[i]
    course = np.full((h, w), -1)
    for i in np.nonzero(what == len(P))[0]: course[py[i] - y0, px[i] - x0] = int((hp[0, i] - XE) // COURSE)
    nb = lambda arr, yy, xx: arr[yy, xx] if 0 <= yy < h and 0 <= xx < w else -1
    for i in range(n):
        x, y, j, a = int(px[i]), int(py[i]), int(what[i]), int(axis[i])
        if j < 0 or (j < len(P) and px[i] < SIGN_EDGE): continue   # (the dark behind, as filled; by the sign, as it is)
        X_, Y_, Z_ = hp[:, i]; yi, xi = y - y0, x - x0
        if j == len(P):                                   # the roof: the sky it sees, a touch darker at the wall's foot;
            t = 0.08 + 0.92 * lit[i] ** 0.8              # its tiles' courses, a line a step darker under each one's
            if X_ > XW - 0.05: t *= 0.7                   # lower edge (where the course above it changes)
            up = nb(course, yi - 1, xi)
            if up >= 0 and up != course[yi, xi]: t -= 0.2
            put(y, xi, ramp(t, R_ROOF, x, y), "roof"); continue
        kind = P[j][2]
        if kind == 'unit':
            if a == 0:                                    # its face: the painter's metal of the column (the grille's
                col = strip if GRILLE[0] <= x < GRILLE[1] else np.median(O[280 - y0:289 - y0, xi], 0)   # own: his
                if y == last.get(x): col = col * 0.6      # casing's), its base pan's two last rows in its shadow; the
                elif y == last.get(x, -9) - 1: col = col * 0.82   # guard's lower half where it reaches
                elif above is not None and GRILLE[0] <= x < GRILLE[1]:
                    (hx, hy), (ax_, ay_), (bx_, by_) = GUARD['hub'], *GUARD['top']
                    c = hy - GUARD['v'] * (x + 0.5 - hx); top = ay_ + (by_ - ay_) * (x - ax_) / (bx_ - ax_)
                    rs = int(np.floor(2 * c - (y + 0.5)))
                    if int(np.ceil(top)) + 1 <= rs < GRILLE[2]: col = above[rs, x]
                put(y, xi, col, 'casing')
            else: put(y, xi, np.array(UNDER, float), 'stand')   # (its underside: the shadow under it)
            continue
        # an angle iron: each face its tone, its edge toward the light a step lighter, its other edge a step darker
        k = key[yi, xi]; hgt = np.clip((Y_ - float(roof_y(X_))) / max(YB - float(roof_y(X_)), 1e-3), 0, 1)
        lit_e = nb(key, yi - 1, xi) != k or nb(key, yi, xi - 1) != k
        dark_e = nb(key, yi + 1, xi) != k or nb(key, yi, xi + 1) != k
        if kind == 'sled' and a == 1: cols, s0 = R_LIT, 1 + int(round(2 * lit[i]))     # (its top, lit by the sky)
        elif a == 0: cols, s0 = R_LIT, (2 + int(round(hgt)) if kind == 'leg' else 2)   # (toward the street: lit)
        elif a == 2: cols, s0 = R_END, 1 + int(round(hgt))                             # (toward us: dark)
        else: cols, s0 = R_END, 0                                                       # (facing down)
        s1 = s0 - 1 if dark_e else s0 + 1 if lit_e else s0
        put(y, xi, np.array(cols[int(np.clip(s1, 0, len(cols) - 1))], float), 'stand')

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

