#!/usr/bin/env python3
"""The narrow building between the Pokemon Center and the apartment building taken away: a roji in its place.

    (a module: tools/redraw_zones.py's zone 'alley' calls draw() on the street as the zones before it leave it; it also
     writes assets/z5_alley.webp, the alley lamp's lit comp, and the cherry's foot behind the gap in assets/fuji_night.webp
     and fuji_aux.webp (far_layers): the same bytes each time)
    python3 tools/roji_alley.py --preview DIR   (only shows it: the zone drawn on the layers as they are, written to DIR
                                                 with its comp and its model's lines over a x6 crop; run it on layers
                                                 without the zone; nothing in the repository changes)

The owner (2026-11-14): "le bâtiment entre le Pokémon Center et l'autre bâtiment est trop comprimé : soit le refaire
entièrement, soit le supprimer et créer une rue". The building (zone5's A, x 908..940, three metres of front squeezed
between its neighbours) is gone; between the Center and the apartment building (B) a narrow side alley runs into the
block, square to the street.

In the street's camera (tools/zone5_facades.py's and tools/arcade_eave.py's: the vanishing point (700, 615), f 960 px,
the eye 1.41 m up; the right facades in the plane 5 m right of the eye's line), the alley is the gap between the Center's
corner (x 908: 23.08 m down the street) and B's (its lit arris, x 941: 19.92 m). From the street one sees in it, cast
pixel by pixel (4 x 4 rays a pixel, each pixel the surface most of its rays meet, its tones flat as the painter shades):
- the alley's far wall: the Center's side, square to the view (drawn face on, no foreshortening: 41.6 px a metre), its
  0.79 m nearest the street (the rest behind B's corner, R22). Its front's bands turn the corner (the owner: "le rouge doit
  faire le tour"): the metal coping (topPC's: its lit nose, its face, its drip, the shade under it), the white cladding,
  the shadow line, the red sign band, the dark lines under it, the white band, each at its own height (the front's rows
  at the corner), level here, in the front's own colours taken at that height along its rays (both layers: the sign's
  light in the street, not in the power cut), a little darker (SIDE: the side in its own light, one factor for the whole
  plane), the corner a crisp edge between the two faces. From the white band down the side is one plaster (the owner:
  "diff de couleur entre le devant et le côté : soit tout uni, soit côté et façade différents, mais identiques sur le même
  pan"): the front's lilac over its awning times SIDE, one value over the plane in each layer, only the light on it: the
  sky's from above (a little lighter up), the contact shade at its foot, the lamp's falloff (the comp), a fine grain within
  that value. On it, as on a small shop's side in a roji (the owner: "la façade ruelle plus de détail"; R25: a few things
  that say what they are; the window with its lattice that was upstairs taken off: "retire la grille ... la façade face à
  nous"); R28: each drawn by the image model in its context, tools/src/edits/alley_objects_model.webp from
  alley_objects_in.webp and _prompt.txt, laid on this tool's model of it (its place, its size; its colours brought to
  the street's and quantised, the sign's and the lamp's light on it as on the plaster): an air conditioner's outdoor unit
  on its wall bracket
  (its casing, louvred side, the fan's grille, its right part behind B's corner); the electricity meter (its glass) and
  under it the gas meter with its pipe down to the floor and its riser; the steel back door in its frame (a lever) on a
  concrete step; beside it a small wall lamp (its glass lit as this tool lights it); at the wall's foot an
  upturned plastic crate, a hydrangea in its pot on it;
- the alley's floor at the sidewalk's level (the painter's foot line of the old building, v -0.2555: 13 cm over the
  ground model), concrete, a gutter's grate across the alley's mouth along the sidewalk's edge (the hydrangea, the owner's
  sprite sheet 2 cut as zone5 cut its plants);
- above the Center's roof: nothing (transparent: the cherry and the sky of the far layers, night_far 0 as it was); the
  cherry's painted foot there, which the old building hid, had holes onto the dusk's horizon: filled (far_layers).
B's left edge is its corner now: its painter's lit arris (x 941) evened along its height, what the old building's
mailbox laid on it (rows 606..627) taken back from above and below. The plant zone5 put on the sidewalk in front of the
Center's corner stays where it stands (its pixels kept, the alley behind it).
Light: the street's (the layer: the lamp off), the Pokemon Center's sign's own light on the plane as the painter put it
on the front's lilac (the street over its power cut there: the power cut takes it off), and the lamp
(the comp z5_alley, street.js: a 'lamp', on all night, out in the power cut, red in the red night): its glass lit, its
light on the wall round it (a soft pool falling off, cut above by its cap), on the meters, the door and its step, the
crate, the plant and the floor, warm as the
painter's lantern light on a lavender wall (his paper lantern's comp: the wall's own colour lifted toward mauve and rose).
A fine grain on the plaster, the bands, the door and the floor (the painter's). Needs Pillow, numpy, scipy.
"""
import os
import sys
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
VPX, VPY, F, EYE = 700.0, 615.0, 960.0, 1.41
XF = 5.0                                         # the facades' plane (m right of the eye's line)
GX0, GX1 = 908, 941                              # the gap's columns (941, B's arris, is B's)
ZF = F * XF / (GX0 - VPX)                        # the far wall: the Center's side, at its corner's depth (23.08 m)
ZB = F * XF / (GX1 - VPX)                        # B's corner (19.92 m)
HS = EYE - 0.2555 * XF                           # the sidewalk's level, the alley's floor (0.13 m)
TOP_ROW = 441                                    # the Center's roof line at its corner (its front's first row)
HT = EYE + (VPY - TOP_ROW) * ZF / F              # the far wall's top (5.59 m)
BOX = (904, 300, 944, 690)                       # the zone (redraw_zones.py 'alley')
SS = 4                                           # rays a pixel, each way
# the far wall's things, in metres: X across the alley from the street, h up, d out of the wall toward the street
DOOR = dict(x=(5.47, 6.27), h=(HS + 0.15, HS + 2.15), d=0.07, frame=0.045)
HANDLE = dict(x=(5.53, 5.63), h=(HS + 1.12, HS + 1.15))         # its lever, on the leaf
LAMP = dict(plate=((5.335, 5.385), (2.20, 2.40), (0.0, 0.02)), arm=((5.353, 5.367), (2.345, 2.365), (0.02, 0.15)),
            cap=((5.285, 5.435), (2.30, 2.34), (0.12, 0.27)), glass=((5.30, 5.42), (2.12, 2.30), (0.135, 0.255)),
            foot=((5.32, 5.40), (2.10, 2.12), (0.15, 0.24)))
LAMP_AT = (5.36, 2.21, 0.195)                    # its light's source (X, h, d)
BOXES = {                                        # what stands out of the wall: X range, h range, d range
    'step': ((5.44, 6.32), (HS, HS + 0.15), (0.0, 0.30)),
    'crate': ((5.06, 5.32), (HS, HS + 0.31), (0.02, 0.38)),
    'emeter': ((5.05, 5.21), (1.80, 2.06), (0.0, 0.11)),
    'gmeter': ((5.06, 5.24), (1.14, 1.42), (0.0, 0.13)),
    'gpipe': ((5.135, 5.165), (HS, 1.14), (0.03, 0.06)),
    'griser': ((5.19, 5.22), (1.42, 1.66), (0.03, 0.06)),
    'ac': ((5.50, 6.30), (2.58, 3.12), (0.10, 0.40)),
    'acarm1': ((5.56, 5.59), (2.55, 2.58), (0.0, 0.42)), 'acarm2': ((6.20, 6.23), (2.55, 2.58), (0.0, 0.42)),
    'acplate1': ((5.56, 5.59), (2.38, 2.58), (0.0, 0.015)), 'acplate2': ((6.20, 6.23), (2.38, 2.58), (0.0, 0.015)),
}
AC_FAN = (5.70, 2.85, 0.17)                      # the unit's fan grille on its front (X, h, radius)
EMETER_GLASS = ((5.08, 5.18), (1.92, 2.02))      # the meter's window on its front
SIDE = 0.80                                      # the side's light against the front's, at the same height (one factor, the
                                                 # whole plane: its bands and its plaster alike)
TOP = dict(nose=0.026, face=0.061, drip=0.077, shad=0.095)   # topPC's coping on the front, under the roof line (m)
FRONT_COLS = (900, 907)                          # the front's columns the bands are read at (topPC's start at 905)
BAND_FOOT = 507                                  # the white band's last row at the corner (the awning under it is the front's)
WHITE_LOW = 499                                  # from here down the front's band is behind its awning: its colour from above
WHITE_TOP = 485                                  # the white band's first row at the corner: from here down the side is one plaster
WHITE_ROWS = (486, 499)                          # the rows its tone is read at (the front's lilac over the awning)
PARAPET = HT - (EYE + (VPY - BAND_FOOT - 1) * ZF / F)   # (the bands' depth, for the lines)
GRATE = (5.0, 5.18)                              # the gutter's grate across the mouth (X)
PLANT = ('zone5_sheet2.webp', (718, 148, 865, 351), 5.20, 0.20, 0.34, HS + 0.31)   # sheet, box, X, d, height, its foot (on the crate)
# tones (the layer: the lamp off), the painter's: the Center's lavender in the alley's shade, his navy for what is dark
C = {'wall': (24, 24, 47), 'glass': (34, 34, 61), 'frame': (36, 36, 61), 'wood': (34, 25, 30), 'wood_lit': (48, 35, 40),
     'door': (21, 27, 43), 'dframe': (12, 15, 26), 'handle': (60, 60, 82), 'iron': (17, 17, 29), 'iron_lit': (34, 33, 52),
     'lens': (44, 37, 60), 'floor': (12, 17, 31), 'grate': (6, 9, 18), 'bar': (15, 21, 36), 'sill': (30, 30, 54),
     'step': (24, 25, 40), 'crate': (20, 30, 66), 'crate_hole': (9, 12, 26), 'meter': (36, 37, 58), 'mglass': (52, 56, 80),
     'gas': (44, 40, 46), 'pipe': (30, 30, 42), 'ac': (40, 41, 66), 'ac_grille': (16, 17, 30), 'steel': (16, 16, 26)}
FACE = {'front': 1.0, 'left': 1.08, 'right': 0.62, 'top': 1.15, 'bottom': 0.52}    # (the street's light comes from the left)
WARM, LIFT = np.array([46.0, 15.0, 3.0]), 0.45   # the lamp's light: the surface lifted by LIFT of itself and WARM (his lantern's,
                                                 # a little less rose: a bulb's, not a red paper's)
LENS_LIT = (np.array([250.0, 224.0, 182.0]), np.array([226.0, 158.0, 118.0]))   # the lit glass: its middle, its rim
GRAIN = 0.025                                    # (a fine grain within the plane's one value)
DRAFT = dict(name='alley_objects', crop=(876, 520, 972, 691), scale=6, gamma=2.0, reach=3,   # (R28: the wall's things drawn by
             model='google/gemini-3-pro-image')  # the image model in their context, 9:16, laid in on the model's masks)
COMP = ('z5_alley', (908, 441), (33, 237))       # the lit comp: street.js ASSETS.comps.z5_alley (x, y), (w, h)
MAILBOX_ROWS = (606, 627)                        # what the old mailbox laid on B's corner (x 941..943)
FAR = dict(box=(904, 420, 944, 446), fill=(906, 428, 942, 442))   # the cherry's foot behind the gap (scene x0, y0, x1, y1)
FAR_N, FAR_A = (376, 66), (320, 66)              # fuji_night.webp's and fuji_aux.webp's places in the scene


def lum3(c): return float(np.dot(np.asarray(c, float), [0.299, 0.587, 0.114]))


def ray(px, py):
    return (px - VPX) / F, -(py - VPY) / F       # (X, h) per metre of depth


def slab(o, dv, lo, hi):
    if abs(dv) < 1e-12: return (-np.inf, np.inf) if lo <= o <= hi else (np.inf, -np.inf)
    a, b = (lo - o) / dv, (hi - o) / dv
    return (a, b) if a < b else (b, a)


def box_hit(dx, dh, bx):
    """A box (X range, h range, d range out of the wall): the depth t of the ray's entry and the face it enters by."""
    (x0, x1), (h0, h1), (d0, d1) = bx
    tx, th, tz = slab(0.0, dx, x0, x1), slab(EYE, dh, h0, h1), (ZF - d1, ZF - d0)
    tmin = max(tx[0], th[0], tz[0]); tmax = min(tx[1], th[1], tz[1])
    if tmin > tmax or tmin <= 0: return None
    face = 'left' if tmin == tx[0] else ('bottom' if dh > 0 else 'top') if tmin == th[0] else 'front'
    return tmin, face


def recess(dx, dh, op, depth):
    """A ray that enters an opening (op: X range, h range) in the wall: its back (at depth) or a reveal it meets first."""
    (x0, x1), (h0, h1) = op
    tb = ZF + depth; Xb, hb = tb * dx, EYE + tb * dh
    if x0 <= Xb <= x1 and h0 <= hb <= h1: return tb, 'back', Xb, hb
    cands = []
    if Xb > x1: cands.append((x1 / dx, 'jamb'))                    # (the far jamb, facing the street)
    if hb > h1: cands.append(((h1 - EYE) / dh, 'soffit'))         # (the head's underside, above the eye)
    if hb < h0 and dh < 0: cands.append(((h0 - EYE) / dh, 'sillin'))
    t, f = min(cands)
    return t, f, t * dx, EYE + t * dh


def surface(px, py):
    """What the ray through screen point (px, py) meets: (surface, face, X, h, d)."""
    dx, dh = ray(px, py)
    best = None
    def take(t, s, f):
        nonlocal best
        if best is None or t < best[0]: best = (t, s, f)
    for name, bx in LAMP.items():
        r = box_hit(dx, dh, bx)
        if r: take(r[0], 'lamp_' + name, r[1])
    for name, bx in BOXES.items():
        r = box_hit(dx, dh, bx)
        if r: take(r[0], name, r[1])
    if dh < 0:                                                     # the floor
        t = (HS - EYE) / dh
        if t <= ZF:
            X = t * dx
            take(t, 'out' if X < XF else 'grate' if X < GRATE[1] else 'floor', 'top')
    tw = ZF; Xw, hw = tw * dx, EYE + tw * dh
    if hw > HT: take(tw + 1e6, 'sky', '')
    elif DOOR['x'][0] <= Xw <= DOOR['x'][1] and DOOR['h'][0] <= hw <= DOOR['h'][1]:
        t, f, X, h = recess(dx, dh, (DOOR['x'], DOOR['h']), DOOR['d'])
        if f == 'back':
            fr = DOOR['frame']
            s = 'door_frame' if min(X - DOOR['x'][0], DOOR['h'][1] - h) < fr else 'door'
            hx, hh = HANDLE['x'], HANDLE['h']
            if hx[0] <= X <= hx[1] and hh[0] <= h <= hh[1]: s = 'door_handle'
            take(t, s, 'front')
        else:
            take(t, 'door_' + f, f)
    else:
        take(tw, 'wall', 'front')
    t, s, f = best
    if s == 'sky': return s, f, 0.0, 0.0, 0.0
    return s, f, t * dx, EYE + t * dh, ZF - t


def cast(x0=GX0, x1=GX1, y0=TOP_ROW - 2, y1=690):
    """Each pixel of the gap: its surface (the most of its rays), the hit point of its ray nearest the pixel's middle."""
    out = {}
    offs = (np.arange(SS) + 0.5) / SS
    for y in range(y0, y1):
        for x in range(x0, x1):
            hits = [(surface(x + a, y + b), (a - 0.5) ** 2 + (b - 0.5) ** 2) for b in offs for a in offs]
            names = [h[0][0] for h in hits]
            s = max(set(names), key=lambda n: (names.count(n), n))
            rep = min((h for h in hits if h[0][0] == s), key=lambda h: h[1])[0]
            out[(x, y)] = rep
    return out


def lamp_light(X, h, d, normal):
    """The lamp's light on a point (0 .. ~1.4): soft, its cap shading what is above it."""
    lx, lh, ld = LAMP_AT
    v = np.array([lx - X, lh - h, ld - d]); dist = np.sqrt((v * v).sum()) + 1e-6
    if h < lh: dist = np.sqrt((lx - X) ** 2 + (0.75 * (lh - h)) ** 2 + (ld - d) ** 2) + 1e-6   # (its glass throws down)
    n = {'front': (0, 0, 1), 'left': (-1, 0, 0), 'right': (1, 0, 0), 'top': (0, 1, 0), 'bottom': (0, -1, 0),
         'jamb': (-1, 0, 0), 'soffit': (0, -1, 0), 'sillin': (0, 1, 0)}.get(normal, (0, 0, 1))
    cos = max(0.0, float(np.dot(n, v)) / dist)
    k = 0.68 * cos / (dist * dist + 0.35 ** 2)
    c0 = LAMP['cap'][1][1]; k *= 1 - 0.65 * np.clip((h - c0 + 0.05) / 0.35, 0, 1) ** 2   # (above its cap, less)
    return min(1.4, k)


def frac(v): return v - np.floor(v)


WALL = {'c': np.array(C['wall'], float)}          # the side's plaster (the power cut's), set from the front's lilac by draw_layers


def wall_tone(X, h):
    """The side's plaster: one value over the plane, only the light on it: the sky's from above (a little lighter up), the
    contact shade at its foot."""
    return WALL['c'] * light_profile(h)


def light_profile(h):
    """The light on the side's plaster by height: the sky's from above (a little lighter up), the street's shade at its
    foot (soft over its last 1.2 m, as the front's pilaster darkens toward the sidewalk)."""
    g = 0.92 + 0.08 * np.clip((h - HS) / (EYE + (VPY - WHITE_TOP) * ZF / F - HS), 0, 1)
    if h < HS + 1.2: g *= 0.74 + 0.26 * ((h - HS) / 1.2) ** 0.8
    return g


def tone(s, f, X, h, d, px, py):
    """The pixel's colour with the lamp off (before the sign's light), and whether it takes the grain."""
    k = FACE.get(f, 1.0)
    if s == 'wall': return wall_tone(X, h), True
    if s == 'door_jamb': return wall_tone(X, h) * 0.9, True                          # (it faces the street)
    if s == 'door_sillin': return np.array(C['floor'], float) * 0.8, False
    if s == 'door_soffit': return wall_tone(X, h) * FACE['bottom'], False
    if s == 'step': return np.array(C['step'], float) * k, True
    if s == 'crate':                                                 # (an upturned crate: its grid of holes)
        (x0, x1), (h0, h1), (d0, d1) = BOXES['crate']
        u, w, z = (X - x0) / (x1 - x0), (h - h0) / (h1 - h0), (d - d0) / (d1 - d0)
        if f == 'front': hole = 0.08 < w < 0.92 and 0.3 < frac(w * 4) < 0.8 and 0.25 < frac(u * 5) < 0.85
        elif f == 'top': hole = 0.08 < u < 0.92 and 0.08 < z < 0.92 and 0.25 < frac(u * 5) < 0.85 and 0.25 < frac(z * 6) < 0.85
        else: hole = 0.08 < w < 0.92 and 0.3 < frac(w * 4) < 0.8 and 0.2 < frac(z * 6) < 0.85
        return np.array(C['crate_hole'] if hole else C['crate'], float) * (1.0 if hole else k), not hole
    if s == 'emeter':
        (gx0, gx1), (gh0, gh1) = EMETER_GLASS
        if f == 'front' and gx0 <= X <= gx1 and gh0 <= h <= gh1: return np.array(C['mglass'], float), False
        return np.array(C['meter'], float) * k, False
    if s == 'gmeter': return np.array(C['gas'], float) * k * (1.15 if f == 'front' and h > BOXES['gmeter'][1][1] - 0.02 else 1.0), False
    if s in ('gpipe', 'griser'): return np.array(C['pipe'], float) * k, False
    if s == 'ac':
        if f == 'front':
            fx, fh, r = AC_FAN; rr = np.hypot(X - fx, h - fh) / r
            if rr < 1:
                if rr > 0.86: return np.array(C['ac'], float) * 0.72, False
                return np.array(C['ac_grille'], float) * (1.45 if frac((h - fh) / 0.03) < 0.4 else 1.0), False
            return np.array(C['ac'], float) * (0.96 + 0.08 * (h - BOXES['ac'][1][0]) / 0.54), True
        if f == 'left': return np.array(C['ac'], float) * k * (0.72 if frac((h - BOXES['ac'][1][0]) / 0.035) < 0.45 else 1.0), False
        return np.array(C['ac'], float) * k, False
    if s.startswith('acarm') or s.startswith('acplate'): return np.array(C['steel'], float) * k, False
    if s == 'door': return np.array(C['door'], float) * (0.94 + 0.06 * (h - HS) / 2.0), True
    if s == 'door_frame': return np.array(C['dframe'], float), False
    if s == 'door_handle': return np.array(C['handle'], float), False
    if s == 'lamp_glass': return np.array(C['lens'], float) * (1.06 if h > 2.24 else 0.96), False
    if s in ('lamp_cap', 'lamp_plate', 'lamp_arm', 'lamp_foot'):
        lit = s == 'lamp_cap' and f == 'front' and h > LAMP['cap'][1][1] - 0.015
        return np.array(C['iron_lit'] if lit else C['iron'], float) * (k if not lit else 1.0), False
    if s == 'floor':
        c = np.array(C['floor'], float)
        if d < 0.05: c = c * 0.78                                   # (its meeting with the far wall)
        for name in ('step', 'crate'):                              # (and with what stands on it)
            (x0, x1), _, (d0, d1) = BOXES[name]
            if x0 - 0.02 <= X <= x1 + 0.02 and d1 <= d < d1 + 0.08: c = c * 0.72
        return c, True
    if s == 'grate':
        return np.array(C['bar'] if (int(px) + int(py)) % 2 == 0 else C['grate'], float), False
    return None, False


def front_bands(L):
    """The Center's front at the height of each of the side's rows from its roof line to the white band's foot: the
    painter's colours there (read along the front's rays at FRONT_COLS, their median), and its coping's lit nose and
    cladding (for the coping's rows, as topPC draws them)."""
    out = {}
    for y in range(TOP_ROW, BAND_FOOT + 1):
        h = EYE + (VPY - (y + 0.5)) * ZF / F; px = []
        for x in range(*FRONT_COLS):
            Z = F * XF / (x + 0.5 - VPX); yi = int(round(VPY - F * (h - EYE) / Z - 0.5))
            if L[yi, x, 3] > 250: px.append(L[yi, x, :3])
        if px: out[y] = np.median(np.array(px), 0)
    for y in range(WHITE_LOW, BAND_FOOT + 1): out[y] = out[WHITE_LOW - 1]   # (the awning hides the band's foot on the front)
    lit = max((L[y, x, :3] for y in range(TOP_ROW, TOP_ROW + 4) for x in range(903, 908) if L[y, x, 3] > 250), key=lum3)
    face = np.median(np.array([L[y, x, :3] for y in range(446, 453) for x in range(905, 907)]), 0)
    return out, np.asarray(lit, float), face


def band_tone(B, y, h):
    rows, lit, face = B; dn = HT - h
    if dn < TOP['nose']: return 0.8 * lit + 0.2 * face
    if dn < TOP['face']: return face * 1.03
    if dn < TOP['drip']: return face * 0.78
    if dn < TOP['shad']: return face * 0.86
    return rows[min(rows, key=lambda r: abs(r - y))] if y not in rows else rows[y]


def grain_field(shape, seed=11, sigma=0.7):
    from scipy.ndimage import gaussian_filter
    rng = np.random.default_rng(seed)
    n = gaussian_filter(rng.standard_normal(shape), sigma); return n / n.std()


def plant(lay, mask, light):
    """The hydrangea by the door (zone5's render_frontal: the sprite's own colours, its pixel size at its depth)."""
    import zone5_facades as Z
    sh, bx, X, d, hm, hb = PLANT
    spr = Z.cut(Z.sheet(sh), bx)
    return Z.render_frontal(lay, mask, X, ZF - d, hb, hm, spr, Z.kpal(spr, 12), light, sat=0.8)


def zone5_pot_mask(shape):
    """The plant zone5 put on the sidewalk in front of the Center's corner: its pixels (kept as they are)."""
    import zone5_facades as Z
    n, bx, X, Zd, hm, sat = Z.POTS[0]
    spr = Z.cut(Z.sheet(n), bx); lay = np.zeros(shape[:2] + (4,)); m = np.zeros(shape[:2], bool)
    Z.render_frontal(lay, m, X, Zd, 0.0, hm, spr, Z.kpal(spr, 14), np.ones(3), sat=sat)
    return m


EDITS = os.path.join(ROOT, 'tools', 'src', 'edits')
GROUPS = {'ac': ('ac', 'acarm1', 'acarm2', 'acplate1', 'acplate2'), 'emeter': ('emeter',), 'gmeter': ('gmeter', 'gpipe', 'griser'),
          'door': ('door', 'door_frame', 'door_handle', 'door_jamb', 'door_soffit', 'door_sillin'), 'step': ('step',),
          'crate': ('crate',), 'lamp': ('lamp_plate', 'lamp_arm', 'lamp_cap', 'lamp_glass', 'lamp_foot')}
                                                 # the things the draft redraws (the lamp's glass lit as this tool lights it)


def draft_input(city):
    """The draft's input: the street with the wall's things as the model of this tool draws them (the layer, lamp off),
    its crop brightened (x ** (1 / gamma)) and enlarged with nearest pixels, as tools/redraw_zones.py asks its drafts."""
    x0, y0, x1, y1 = DRAFT['crop']; k = DRAFT['scale']
    z = np.clip(city[y0:y1, x0:x1, :3] / 255.0, 0, 1) ** (1 / DRAFT['gamma'])
    z[city[y0:y1, x0:x1, 3] < 128] = (0.6, 0.45, 0.5)
    return Image.fromarray((z * 255).round().astype(np.uint8)).resize(((x1 - x0) * k, (y1 - y0) * k), Image.NEAREST)


def call():
    """Asks the image model for the wall's things (tools/src/edits/alley_objects_in.webp and _prompt.txt; the key from
    the environment's vault or OPENROUTER_API_KEY), saves its answer as tools/src/edits/alley_objects_model.webp."""
    import base64, io, json, urllib.request
    n = DRAFT['name']; buf = io.BytesIO(); Image.open(os.path.join(EDITS, n + '_in.webp')).convert('RGB').save(buf, 'PNG')
    body = {"model": DRAFT['model'], "modalities": ["image", "text"], "usage": {"include": True}, "messages": [{"role": "user", "content": [
        {"type": "text", "text": open(os.path.join(EDITS, n + '_prompt.txt')).read().strip()},
        {"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()}}]}]}
    key = os.environ.get('OPENROUTER_API_KEY', 'proxy-injected')
    req = urllib.request.Request('https://openrouter.ai/api/v1/chat/completions', data=json.dumps(body).encode(),
                                 headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'})
    d = json.loads(urllib.request.urlopen(req, timeout=600).read())
    url = d['choices'][0]['message']['images'][0]['image_url']['url']
    Image.open(io.BytesIO(base64.b64decode(url.split(',', 1)[1]))).save(os.path.join(EDITS, n + '_model.webp'), 'WEBP', lossless=True, quality=100, method=6)
    print(n, 'model answer saved; cost', d.get('usage', {}).get('cost'), '$')


def draft(street):
    """The model's answer brought back to the street's grid: boxed down to the crop's pixels, darkened back (x ** gamma),
    moved by the integer shift whose gradients best match the street's round the alley (its far wall left out), as the
    street's own rows and columns (whole-scene array, the crop only)."""
    from scipy.ndimage import binary_dilation
    p = os.path.join(EDITS, DRAFT['name'] + '_model.webp')
    if not os.path.exists(p): return None
    x0, y0, x1, y1 = DRAFT['crop']; w, h = x1 - x0, y1 - y0
    e = (np.asarray(Image.open(p).convert('RGB').resize((w, h), Image.BOX)).astype(float) / 255.0) ** DRAFT['gamma'] * 255.0
    o = street[y0:y1, x0:x1, :3]
    def grad(z):
        l = z @ np.array([0.299, 0.587, 0.114]); gx = np.zeros_like(l); gy = np.zeros_like(l)
        gx[:, 1:] = l[:, 1:] - l[:, :-1]; gy[1:] = l[1:] - l[:-1]; return np.hypot(gx, gy)
    ref = np.ones((h, w), bool); ref[:, GX0 - x0:GX1 - x0] = False; ref[:4] = ref[-4:] = False; ref[:, :4] = ref[:, -4:] = False
    go = grad(o); go = (go - go[ref].mean()) / (go[ref].std() + 1e-6); best = None
    def shift(a, dy, dx):
        yi = np.clip(np.arange(h) - dy, 0, h - 1); xi = np.clip(np.arange(w) - dx, 0, w - 1); return a[yi][:, xi]
    for dy in range(-DRAFT['reach'], DRAFT['reach'] + 1):
        for dx in range(-DRAFT['reach'], DRAFT['reach'] + 1):
            g = grad(shift(e, dy, dx)); g = (g - g[ref].mean()) / (g[ref].std() + 1e-6)
            c = float((g[ref] * go[ref]).mean())
            if best is None or c > best[0]: best = (c, dx, dy)
    out = np.zeros(street.shape[:2] + (3,)); out[y0:y1, x0:x1] = shift(e, best[2], best[1])
    print(f'alley draft: registered dx={best[1]} dy={best[2]} (gradient correlation {best[0]:.2f})')
    return out


DRAFT_DEV, DRAFT_K = 6.0, 6                      # (a pixel of the drawing is a thing's when it is that far from its wall; its tones)


def kq(px, k, seed=0, it=20):
    """px quantised to k of its own colours (k-means, a fixed seed: the same answer each time)."""
    px = np.asarray(px, float); k = min(k, len(px))
    rng = np.random.default_rng(seed); c = px[rng.choice(len(px), k, replace=False)].copy()
    for _ in range(it):
        l = ((px[:, None, :] - c[None]) ** 2).sum(-1).argmin(1)
        for j in range(k):
            if (l == j).any(): c[j] = px[l == j].mean(0)
    return c[((px[:, None, :] - c[None]) ** 2).sum(-1).argmin(1)]


def match(src, ref):
    """src's ranks given ref's values, channel by channel (the draft's drawing in the tool's own tones)."""
    out = np.empty_like(src)
    for c in range(3):
        o = np.argsort(src[:, c], kind='stable'); v = np.empty(len(src)); v[o] = np.sort(ref[:, c]); out[:, c] = v
    return out


def draw_layers(city, unlit, box=BOX):
    """Both layers changed in place; returns what changed and the lit comp (RGBA, its box COMP)."""
    H, W = city.shape[:2]
    old = (city[..., 3] > 128)
    keep = zone5_pot_mask((H, W))
    Bc, Bu = front_bands(city), front_bands(unlit)
    wc = np.median(np.array([Bc[0][y] for y in range(*WHITE_ROWS)]), 0)   # the front's lilac over its awning, both layers:
    wu = np.median(np.array([Bu[0][y] for y in range(*WHITE_ROWS)]), 0)   # the side's one plaster, a little darker (SIDE)
    WALL['c'] = wu * SIDE
    gain = (wc + 1) / (wu + 1)                                   # (the sign's light on the plane, the street over the cut)
    hit = cast()
    gr = grain_field((H, W))
    ch = np.zeros((H, W), bool)
    assert not old[BOX[1]:BOX[1] + 1, GX0:GX1].any(), 'the old building reaches over the box'
    for y in range(BOX[1], TOP_ROW - 2):                            # (over the Center's roof: the old building's top, gone)
        for x in range(GX0, GX1):
            if old[y, x]:
                city[y, x, 3] = unlit[y, x, 3] = 0; city[y, x, :3] = city[300, x, :3]; unlit[y, x, :3] = unlit[300, x, :3]
                ch[y, x] = True
    lit = city[..., :3].copy()                                      # (the comp's picture: the street with the lamp on)
    base = np.zeros((H, W, 3)); amb = np.zeros((H, W, 3)); took = np.zeros((H, W), bool); Iat = np.zeros((H, W))
    for (x, y), (s, f, X, h, d) in hit.items():
        if keep[y, x] or s == 'out': continue
        if s == 'sky':
            if old[y, x]:
                city[y, x, 3] = 0; unlit[y, x, 3] = 0
                city[y, x, :3] = city[300, x, :3]; unlit[y, x, :3] = unlit[300, x, :3]   # (a hidden colour of the sky's)
                ch[y, x] = True
            continue
        if s == 'wall' and y < WHITE_TOP:                          # (the front's bands turning the corner)
            g = 1 + 0.02 * gr[y, x]
            cs, c = band_tone(Bc, y, h) * SIDE * g, band_tone(Bu, y, h) * SIDE * g
        else:
            c, gn = tone(s, f, X, h, d, x, y)
            if gn: c = c * (1 + GRAIN * gr[y, x])
            cs = c * gain
        amb[y, x] = c
        I = lamp_light(X, h, d, f if s not in ('wall', 'door', 'door_frame', 'door_handle') else 'front')
        if s == 'lamp_glass':
            k = np.clip(1 - abs(X - LAMP_AT[0]) / 0.06, 0, 1) * np.clip(1 - abs(h - LAMP_AT[1]) / 0.09, 0, 1)
            lt = LENS_LIT[1] + (LENS_LIT[0] - LENS_LIT[1]) * k
        else:                                                       # (the warm light as much as the surface takes it)
            lt = cs + I * (LIFT * cs + WARM * np.clip(lum3(c) / lum3(C['wall']), 0.15, 1.3))
        city[y, x, :3] = cs; unlit[y, x, :3] = c; city[y, x, 3] = unlit[y, x, 3] = 255
        lit[y, x] = lt; ch[y, x] = True; took[y, x] = True; Iat[y, x] = I
    # the wall's things as the image model draws them (R28): its colours brought to the street's (a line per channel fitted on
    # the crop round the gap, which it was asked to keep), each thing's pixels where the drawing has it near this tool's
    # model of it (its mask grown 2 px: its place, its size), quantised to a few of its own tones (crisp, no model mush);
    # where the model's mask has plain wall in the drawing, the plaster; the sign's light and the lamp's on them as on the
    # rest (the power cut: the street's colour over the sign's gain)
    D = draft(city)
    if D is not None:
        from scipy.ndimage import binary_dilation, label
        x0, y0, x1, y1 = DRAFT['crop']
        ref = np.zeros((H, W), bool); ref[y0:y1, x0:x1] = True; ref[:, GX0 - 2:GX1 + 2] = False; ref &= city[..., 3] > 250
        fit = [np.polyfit(D[ref][:, c], city[ref][:, c], 1) for c in range(3)]
        Df = np.stack([fit[c][0] * D[..., c] + fit[c][1] for c in range(3)], -1)
        sid = np.full((H, W), '', 'U12')
        for (x, y), (s_, f_, X_, h_, d_) in hit.items():
            if took[y, x]: sid[y, x] = s_
        masks = {g: np.isin(sid, ns) for g, ns in GROUPS.items()}
        anyobj = np.any(list(masks.values()), 0)
        plain = (sid == 'wall') & ~binary_dilation(anyobj, iterations=4)
        wall_d = np.median(Df[plain], 0)
        dev = np.abs(Df - wall_d).max(-1)
        for gi, (g, m) in enumerate(masks.items()):
            if m.sum() < 4: continue
            near = binary_dilation(m, iterations=2) & took
            near &= ~np.any([mm for gg, mm in masks.items() if gg != g], 0)
            obj = near & (dev > DRAFT_DEV)
            lab, n = label(obj)
            for k in range(1, n + 1):
                if (lab == k).sum() < 3: obj[lab == k] = False
            ys, xs = np.nonzero(obj)
            if len(ys):
                q = kq(Df[ys, xs], DRAFT_K, seed=gi)
                for y, x, cq in zip(ys, xs, q):
                    city[y, x, :3] = cq; unlit[y, x, :3] = cq / gain
                    if sid[y, x] == 'lamp_glass': continue                # (its glass lit in the comp as this tool lights it)
                    al = np.clip(lum3(cq / gain) / lum3(C['wall']), 0.15, 1.3)
                    lit[y, x] = cq + Iat[y, x] * (LIFT * cq + WARM * al)
            for y, x in zip(*np.nonzero(m & ~obj & (sid != 'lamp_glass'))):   # (the model's thing not in the drawing: the plaster)
                dx_, dh_ = ray(x + 0.5, y + 0.5); X_, h_ = ZF * dx_, EYE + ZF * dh_
                c = wall_tone(X_, h_) * (1 + GRAIN * gr[y, x]); cs = c * gain; I_ = lamp_light(X_, h_, 0.0, 'front')
                city[y, x, :3] = cs; unlit[y, x, :3] = c
                lit[y, x] = cs + I_ * (LIFT * cs + WARM * np.clip(lum3(c) / lum3(C['wall']), 0.15, 1.3))
    # the hydrangea on the crate: in the street's light, and in the lamp's
    lm = np.zeros((H, W), bool); lay = np.zeros((H, W, 4))
    yy, xx = np.mgrid[0:H, 0:W]
    floor_amb = np.array(C['wall'], float) * 0.86
    plant(lay, lm, floor_amb)
    lm &= ~keep & (xx >= GX0) & (xx < GX1)
    lay_lit = np.zeros((H, W, 4)); lm2 = np.zeros((H, W), bool)
    L = np.ones((H, W, 3)) * floor_amb
    for y, x in zip(*np.nonzero(lm)):
        Xp = (x + 0.5 - VPX) * (ZF - PLANT[3]) / F; hp = EYE - (y + 0.5 - VPY) * (ZF - PLANT[3]) / F
        I = lamp_light(Xp, hp, PLANT[3], 'top')
        L[y, x] = floor_amb + I * (LIFT * floor_amb + WARM * 1.2)
    plant(lay_lit, lm2, L)
    for y, x in zip(*np.nonzero(lm)):
        city[y, x, :3] = lay[y, x, :3] * gain; unlit[y, x, :3] = lay[y, x, :3]; lit[y, x] = lay_lit[y, x, :3] * gain
        city[y, x, 3] = unlit[y, x, 3] = 255; ch[y, x] = True
    # B's corner: its lit arris evened along its height, the old mailbox off it
    from scipy.ndimage import gaussian_filter1d
    for L_ in (city, unlit):
        a0, a1 = MAILBOX_ROWS
        for x in (941, 942, 943):
            top, bot = L_[a0 - 1, x, :3].copy(), L_[a1 + 1, x, :3].copy()
            for y in range(a0, a1 + 1):
                w = (y - (a0 - 1)) / (a1 + 1 - (a0 - 1)); L_[y, x, :3] = (1 - w) * top + w * bot
            ch[a0:a1 + 1, x] = True
        col = L_[318:684, 941, :3]; L_[318:684, 941, :3] = gaussian_filter1d(col, 1.5, axis=0, mode='nearest')
        ch[318:684, 941] = True
    lit[MAILBOX_ROWS[0]:MAILBOX_ROWS[1] + 1, 941:944] = city[MAILBOX_ROWS[0]:MAILBOX_ROWS[1] + 1, 941:944, :3]
    # the comp: the lamp's picture where it differs from the street
    (cx, cy), (cw, chh) = COMP[1], COMP[2]
    comp = np.zeros((chh, cw, 4))
    sub = lit[cy:cy + chh, cx:cx + cw]; st = city[cy:cy + chh, cx:cx + cw, :3]
    on = (np.abs(np.round(sub) - np.round(st)).max(-1) >= 1) & took[cy:cy + chh, cx:cx + cw] | lm[cy:cy + chh, cx:cx + cw] & (np.abs(np.round(sub) - np.round(st)).max(-1) >= 1)
    comp[on, :3] = sub[on]; comp[on, 3] = 255
    full = (np.abs(np.round(lit) - np.round(city[..., :3])).max(-1) >= 1) & (took | lm)
    out = full.copy(); out[cy:cy + chh, cx:cx + cw] = False
    if out.any():
        ys, xs = np.nonzero(full)
        raise SystemExit(f'the lamp lights beyond its comp: {xs.min()}..{xs.max()} x {ys.min()}..{ys.max()}')
    x0, y0, x1, y1 = box
    inb = np.zeros((H, W), bool); inb[y0:y1, x0:x1] = True
    assert not (ch & ~inb).any(), 'changed outside the box'
    return ch, comp


def save(arr, p, mode='RGBA'):
    Image.fromarray(np.clip(np.round(arr), 0, 255).astype(np.uint8), mode).save(p, 'WEBP', lossless=True, quality=100, method=6, exact=True)


def far_layers():
    """The cherry's foot behind the gap: the old building hid it; its painted lower canopy (fuji_night.webp) has a few holes
    there (rows 433..441) where the dusk's horizon showed, bright orange blobs on the Center's roof. Each hole takes the
    canopy's nearest pixel (the tree goes on behind, R22) and fuji_aux.webp calls it the cherry's (R 255: its own colours
    at every hour). From before copies of both (tools/src/edits/alley_fuji_*_before.webp): the same bytes each time."""
    from scipy.ndimage import distance_transform_edt
    x0, y0, x1, y1 = FAR['box']; fx0, fy0, fx1, fy1 = FAR['fill']
    pn, pa = os.path.join(ROOT, 'assets', 'fuji_night.webp'), os.path.join(ROOT, 'assets', 'fuji_aux.webp')
    fn = np.asarray(Image.open(pn).convert('RGBA')).copy(); fa = np.asarray(Image.open(pa).convert('RGB')).copy()
    bn = np.asarray(Image.open(os.path.join(ROOT, 'tools', 'src', 'edits', 'alley_fuji_night_before.webp')).convert('RGBA'))
    ba = np.asarray(Image.open(os.path.join(ROOT, 'tools', 'src', 'edits', 'alley_fuji_aux_before.webp')).convert('RGB'))
    sn = (slice(y0 - FAR_N[1], y1 - FAR_N[1]), slice(x0 - FAR_N[0], x1 - FAR_N[0]))
    sa = (slice(y0 - FAR_A[1], y1 - FAR_A[1]), slice(x0 - FAR_A[0], x1 - FAR_A[0]))
    fn[sn] = bn; fa[sa] = ba
    sub = fn[sn].copy(); op = sub[..., 3] > 128
    hole = np.zeros(op.shape, bool); hole[fy0 - y0:fy1 - y0, fx0 - x0:fx1 - x0] = True; hole &= ~op
    iy, ix = distance_transform_edt(~op, return_indices=True)[1]
    sub[hole] = sub[iy[hole], ix[hole]]; sub[hole, 3] = 255
    fn[sn] = sub
    aux = fa[sa].copy(); aux[hole] = (255, 0, 0); fa[sa] = aux
    Image.fromarray(fn, 'RGBA').save(pn, 'WEBP', lossless=True, quality=100, method=6, exact=True)
    Image.fromarray(fa, 'RGB').save(pa, 'WEBP', lossless=True, quality=100, method=6, exact=True)
    return int(hole.sum())


def draw(city, unlit, box=BOX):
    """The zone (redraw_zones.py): both layers changed in place; assets/z5_alley.webp written, the cherry's foot behind
    the gap filled (assets/fuji_night.webp, fuji_aux.webp)."""
    ch, comp = draw_layers(city, unlit, box)
    save(comp, os.path.join(ROOT, 'assets', COMP[0] + '.webp'))
    far_layers()
    return ch


def lines(img, x0, y0, k):
    """The model's lines over a crop (x0, y0, enlarged k): the far wall and its bands (level, at the front's heights at the
    corner, the front's rays continuing them), the floor's edges, the mouth, B's corner, the window, the door, the boxes."""
    from PIL import ImageDraw
    d = ImageDraw.Draw(img)
    P = lambda X, h, Z: ((VPX + F * X / Z - x0) * k, (VPY - F * (h - EYE) / Z - y0) * k)
    seg = lambda a, b, col: d.line([P(*a), P(*b)], fill=col, width=1)
    Xb = ZF * (GX1 - VPX) / F
    for a, b in [((XF, HS, ZF), (Xb, HS, ZF)), ((XF, HT, ZF), (Xb, HT, ZF)), ((XF, HS, ZF), (XF, HT, ZF)),
                 ((XF, HS, ZF), (XF, HS, ZB))]:
        seg(a, b, (255, 255, 0))
    for y in (455, 481, BAND_FOOT + 1):                                                 # the bands: level on the side,
        h = EYE + (VPY - y) * ZF / F                                                     # on the front's rays before it
        seg((XF, h, ZF), (Xb, h, ZF), (255, 60, 60)); seg((XF, h, ZF), (XF, h, ZF + 4.0), (255, 60, 60))
    seg((XF, 0.0, ZB), (XF, 9.0, ZB), (255, 255, 255))                                   # B's corner
    seg((XF, HS, 26.0), (XF, HS, 17.0), (0, 255, 0))                                     # the facades' foot (a ray)
    seg((GRATE[1], HS, ZF), (GRATE[1], HS, ZB), (0, 200, 255))
    for (xa, xb), (ha, hb) in [(DOOR['x'], DOOR['h'])]:
        for a, b in [((xa, ha), (xb, ha)), ((xb, ha), (xb, hb)), ((xb, hb), (xa, hb)), ((xa, hb), (xa, ha))]:
            seg((a[0], a[1], ZF), (b[0], b[1], ZF), (255, 120, 0))
    for (xa, xb), (ha, hb), (da, db) in list(BOXES.values()) + [LAMP['glass']]:          # each box's front face
        Z = ZF - db
        for a, b in [((xa, ha), (xb, ha)), ((xb, ha), (xb, hb)), ((xb, hb), (xa, hb)), ((xa, hb), (xa, ha))]:
            seg((a[0], a[1], Z), (b[0], b[1], Z), (255, 0, 255))
    return img


def preview(out):
    os.makedirs(out, exist_ok=True)
    L = {t: np.asarray(Image.open(os.path.join(ROOT, 'assets', f)).convert('RGBA')).astype(float)
         for t, f in (('city', 'layer_city_off.webp'), ('unlit', 'street_unlit.webp'))}
    ch, comp = draw_layers(L['city'], L['unlit'])
    save(L['city'], os.path.join(out, 'layer_city_off.webp')); save(L['unlit'], os.path.join(out, 'street_unlit.webp'))
    save(comp, os.path.join(out, COMP[0] + '.webp'))
    on = L['city'].copy(); (cx, cy), (cw, chh) = COMP[1], COMP[2]
    a = comp[..., 3:4] / 255.0; on[cy:cy + chh, cx:cx + cw, :3] = on[cy:cy + chh, cx:cx + cw, :3] * (1 - a) + comp[..., :3] * a
    for tag, arr in (('city', L['city']), ('lit', on), ('unlit', L['unlit'])):
        x0, y0, x1, y1 = 880, 430, 960, 690
        z = arr[y0:y1, x0:x1].copy(); z[z[..., 3] < 128, :3] = (150, 70, 90)
        im = Image.fromarray(np.clip(np.round(z[..., :3]), 0, 255).astype(np.uint8)).resize(((x1 - x0) * 6, (y1 - y0) * 6), Image.NEAREST)
        im.save(os.path.join(out, f'{tag}_x6.png'))
        if tag == 'lit': lines(im.copy(), x0, y0, 6).save(os.path.join(out, 'lines_x6.png'))
    print('changed', int(ch.sum()), 'px; comp', int((comp[..., 3] > 0).sum()), 'px')


if __name__ == '__main__':
    if '--preview' in sys.argv: preview(sys.argv[sys.argv.index('--preview') + 1])
    if '--draft-in' in sys.argv:                 # (the draft's input from the street as it is: run it on layers with the zone)
        L = np.asarray(Image.open(os.path.join(ROOT, 'assets', 'layer_city_off.webp')).convert('RGBA')).astype(float)
        draft_input(L).save(os.path.join(EDITS, DRAFT['name'] + '_in.webp'), 'WEBP', lossless=True, quality=100, method=6)
    if '--call' in sys.argv: call()
