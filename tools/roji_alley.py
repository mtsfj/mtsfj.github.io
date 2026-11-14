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
  0.79 m nearest the street (the rest behind B's corner, R22); its plaster the Center's lavender, in the alley's shade
  (lighter toward its top under the sky and toward the street, darker at its foot), its top a real one (R27): the
  Center's front band turning the corner as its parapet, a metal coping at the roof line (row 441: its lit edge, its face,
  the shade under its lip), a drip line under the band; on it a small frosted window upstairs
  (its sill, its head's soffit and its far jamb seen in the recess, as the eye sees a recess right of it and above it), a
  steel back door (its leaf set in its frame, a lever, its right part behind B's corner) and, beside its head, a small
  wall lamp (its plate, its arm toward the street, a glass box under an iron cap);
- the alley's floor at the sidewalk's level (the painter's foot line of the old building, v -0.2555: 13 cm over the
  ground model), concrete, a gutter's grate across the alley's mouth along the sidewalk's edge, a hydrangea in its pot by
  the door (the owner's sprite sheet 2, as zone5 cut its plants), its shade on the floor;
- above the Center's roof: nothing (transparent: the cherry and the sky of the far layers, night_far 0 as it was); the
  cherry's painted foot there, which the old building hid, had holes onto the dusk's horizon: filled (far_layers).
B's left edge is its corner now: its painter's lit arris (x 941) evened along its height, what the old building's
mailbox laid on it (rows 606..627) taken back from above and below. The plant zone5 put on the sidewalk in front of the
Center's corner stays where it stands (its pixels kept, the alley behind it).
Light: the street's (the layer: the lamp off), the Pokemon Center's sign's own light on the wall's top half as the
painter put it on the old wall (the street over its power cut there, per row: the power cut takes it off), and the lamp
(the comp z5_alley, street.js: a 'lamp', on all night, out in the power cut, red in the red night): its glass lit, its
light on the wall round it (a soft pool, cut above by its cap), on the door, the plant and the floor, warm as the
painter's lantern light on a lavender wall (his paper lantern's comp: the wall's own colour lifted toward mauve and rose).
A fine grain on the plaster, the door and the floor (the painter's). Needs Pillow, numpy, scipy.
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
WIN = dict(x=(5.13, 5.43), h=(3.55, 4.05), d=0.06, frame=0.028)
SILL = dict(x=(5.10, 5.46), h=(3.50, 3.55), d=(0.0, 0.05))
DOOR = dict(x=(5.47, 6.27), h=(HS, HS + 2.0), d=0.07, frame=0.045)
HANDLE = dict(x=(5.53, 5.63), h=(HS + 0.97, HS + 1.0))         # its lever, on the leaf
LAMP = dict(plate=((5.335, 5.385), (2.20, 2.40), (0.0, 0.02)), arm=((5.353, 5.367), (2.345, 2.365), (0.02, 0.15)),
            cap=((5.285, 5.435), (2.30, 2.34), (0.12, 0.27)), glass=((5.30, 5.42), (2.12, 2.30), (0.135, 0.255)),
            foot=((5.32, 5.40), (2.10, 2.12), (0.15, 0.24)))
LAMP_AT = (5.36, 2.21, 0.195)                    # its light's source (X, h, d)
TOP = dict(lit=0.025, face=0.06, lip=0.08, band=0.30, drip=0.32)   # the wall's top under the roof line (m down from it): the
                                                 # coping's lit edge, its face, the shade under its lip, the parapet's band, its drip line
PARAPET = TOP['band']
GRATE = (5.0, 5.18)                              # the gutter's grate across the mouth (X)
PLANT = ('zone5_sheet2.webp', (718, 148, 865, 351), 5.32, 0.17, 0.38)   # sheet, box, X, d (its foot off the wall), height
# tones (the layer: the lamp off), the painter's: the Center's lavender in the alley's shade, his navy for what is dark
C = {'wall': (24, 24, 47), 'band': (54, 42, 68), 'coping': (70, 56, 86), 'glass': (30, 31, 57), 'frame': (36, 36, 61),
     'door': (21, 27, 43), 'dframe': (12, 15, 26), 'handle': (60, 60, 82), 'iron': (17, 17, 29), 'iron_lit': (34, 33, 52),
     'lens': (44, 37, 60), 'floor': (12, 17, 31), 'grate': (6, 9, 18), 'bar': (15, 21, 36), 'sill': (30, 30, 54)}
FACE = {'front': 1.0, 'left': 1.08, 'right': 0.62, 'top': 1.15, 'bottom': 0.52}    # (the street's light comes from the left)
WARM, LIFT = np.array([46.0, 15.0, 3.0]), 0.45   # the lamp's light: the surface lifted by LIFT of itself and WARM (his lantern's,
                                                 # a little less rose: a bulb's, not a red paper's)
LENS_LIT = (np.array([250.0, 224.0, 182.0]), np.array([226.0, 158.0, 118.0]))   # the lit glass: its middle, its rim
GRAIN = 0.035
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
    r = box_hit(dx, dh, (SILL['x'], SILL['h'], SILL['d']))
    if r: take(r[0], 'sill', r[1])
    if dh < 0:                                                     # the floor
        t = (HS - EYE) / dh
        if t <= ZF:
            X = t * dx
            take(t, 'out' if X < XF else 'grate' if X < GRATE[1] else 'floor', 'top')
    tw = ZF; Xw, hw = tw * dx, EYE + tw * dh
    if hw > HT: take(tw + 1e6, 'sky', '')
    elif WIN['x'][0] <= Xw <= WIN['x'][1] and WIN['h'][0] <= hw <= WIN['h'][1]:
        t, f, X, h = recess(dx, dh, (WIN['x'], WIN['h']), WIN['d'])
        fr = WIN['frame']
        s = 'win_' + ('frame' if f == 'back' and min(X - WIN['x'][0], WIN['x'][1] - X, h - WIN['h'][0], WIN['h'][1] - h) < fr
                      else 'glass' if f == 'back' else f)
        take(t, s, 'front' if f == 'back' else f)
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


def wall_tone(X, h):
    u = (X - XF) / (ZF * (GX1 - VPX) / F - XF)                     # 0 at the Center's corner, 1 at B's
    g = (0.86 + 0.24 * np.clip((h - HS) / (HT - HS), 0, 1)) * (1.06 - 0.12 * u)
    if h < HS + 0.30: g *= 0.88 + 0.12 * (h - HS) / 0.30             # (the alley's grime at its foot)
    return np.array(C['wall'], float) * g


def tone(s, f, X, h, d, px, py):
    """The pixel's colour with the lamp off (before the sign's light), and whether it takes the grain."""
    if s == 'wall':
        dn = HT - h
        if dn < TOP['lit']: return np.array(C['coping'], float), False
        if dn < TOP['face']: return np.array(C['band'], float) * 0.86, False
        if dn < TOP['lip']: return np.array(C['band'], float) * 0.5, False
        if dn < TOP['band']: return np.array(C['band'], float) * (0.94 + 0.06 * (TOP['band'] - dn) / TOP['band']), True
        if dn < TOP['drip']: return wall_tone(X, h) * 0.72, False
        return wall_tone(X, h), True
    if s == 'win_glass':
        k = (h - WIN['h'][0]) / (WIN['h'][1] - WIN['h'][0])
        return np.array(C['glass'], float) * (0.92 + 0.16 * k), False
    if s == 'win_frame': return np.array(C['frame'], float), False
    if s in ('win_jamb', 'door_jamb'): return wall_tone(X, h) * 0.9, True              # (it faces the street)
    if s in ('door_sillin', 'win_sillin'): return np.array(C['floor'], float) * 0.8, False
    if s in ('win_soffit', 'door_soffit'): return wall_tone(X, h) * FACE['bottom'], False
    if s == 'sill':
        return np.array(C['sill'], float) * FACE.get(f, 1.0), False
    if s == 'door': return np.array(C['door'], float) * (0.94 + 0.06 * (h - HS) / 2.0), True
    if s == 'door_frame': return np.array(C['dframe'], float), False
    if s == 'door_handle': return np.array(C['handle'], float), False
    if s == 'lamp_glass': return np.array(C['lens'], float) * (1.06 if h > 2.24 else 0.96), False
    if s in ('lamp_cap', 'lamp_plate', 'lamp_arm', 'lamp_foot'):
        lit = s == 'lamp_cap' and f == 'front' and h > LAMP['cap'][1][1] - 0.015
        return np.array(C['iron_lit'] if lit else C['iron'], float) * (FACE.get(f, 1.0) if not lit else 1.0), False
    if s == 'floor':
        c = np.array(C['floor'], float)
        if d < 0.05: c = c * 0.78                                   # (its meeting with the far wall)
        return c, True
    if s == 'grate':
        return np.array(C['bar'] if (int(px) + int(py)) % 2 == 0 else C['grate'], float), False
    return None, False


def sign_gain(city, unlit):
    """The Pokemon Center's sign's light on the old building's wall, as the painter put it (the street over its power cut,
    per row and channel: the plaster's columns 910..939, smoothed): what the far wall takes in the street, not in the cut."""
    from scipy.ndimage import gaussian_filter1d
    rows = np.arange(city.shape[0]); g = np.ones((city.shape[0], 3))
    a, b = city[:, 909:912, :3], unlit[:, 909:912, :3]              # (its plain pier by the Center)
    r = np.median((a + 1) / (b + 1), axis=1)
    sel = (rows >= TOP_ROW) & (rows < 670)
    g[sel] = gaussian_filter1d(np.clip(r[sel], 1.0, 2.0), 4.0, axis=0)
    return g


def grain_field(shape, seed=11):
    from scipy.ndimage import gaussian_filter
    rng = np.random.default_rng(seed)
    n = gaussian_filter(rng.standard_normal(shape), 0.7); return n / n.std()


def plant(lay, mask, light):
    """The hydrangea by the door (zone5's render_frontal: the sprite's own colours, its pixel size at its depth)."""
    import zone5_facades as Z
    sh, bx, X, d, hm = PLANT
    spr = Z.cut(Z.sheet(sh), bx)
    return Z.render_frontal(lay, mask, X, ZF - d, HS, hm, spr, Z.kpal(spr, 12), light, sat=0.8)


def zone5_pot_mask(shape):
    """The plant zone5 put on the sidewalk in front of the Center's corner: its pixels (kept as they are)."""
    import zone5_facades as Z
    n, bx, X, Zd, hm, sat = Z.POTS[0]
    spr = Z.cut(Z.sheet(n), bx); lay = np.zeros(shape[:2] + (4,)); m = np.zeros(shape[:2], bool)
    Z.render_frontal(lay, m, X, Zd, 0.0, hm, spr, Z.kpal(spr, 14), np.ones(3), sat=sat)
    return m


def draw_layers(city, unlit, box=BOX):
    """Both layers changed in place; returns what changed and the lit comp (RGBA, its box COMP)."""
    H, W = city.shape[:2]
    old = (city[..., 3] > 128)
    keep = zone5_pot_mask((H, W))
    gain = sign_gain(city, unlit)
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
    base = np.zeros((H, W, 3)); amb = np.zeros((H, W, 3)); took = np.zeros((H, W), bool)
    for (x, y), (s, f, X, h, d) in hit.items():
        if keep[y, x] or s == 'out': continue
        if s == 'sky':
            if old[y, x]:
                city[y, x, 3] = 0; unlit[y, x, 3] = 0
                city[y, x, :3] = city[300, x, :3]; unlit[y, x, :3] = unlit[300, x, :3]   # (a hidden colour of the sky's)
                ch[y, x] = True
            continue
        c, gn = tone(s, f, X, h, d, x, y)
        if gn: c = c * (1 + GRAIN * gr[y, x])
        amb[y, x] = c
        I = lamp_light(X, h, d, f if s not in ('wall', 'door', 'door_frame', 'door_handle', 'win_glass', 'win_frame') else 'front')
        cs = c * gain[y]
        if s == 'lamp_glass':
            k = np.clip(1 - abs(X - LAMP_AT[0]) / 0.06, 0, 1) * np.clip(1 - abs(h - LAMP_AT[1]) / 0.09, 0, 1)
            lt = LENS_LIT[1] + (LENS_LIT[0] - LENS_LIT[1]) * k
        else:                                                       # (the warm light as much as the surface takes it)
            lt = cs + I * (LIFT * cs + WARM * np.clip(lum3(c) / lum3(C['wall']), 0.15, 1.3))
        city[y, x, :3] = cs; unlit[y, x, :3] = c; city[y, x, 3] = unlit[y, x, 3] = 255
        lit[y, x] = lt; ch[y, x] = True; took[y, x] = True
    # the hydrangea by the door: in the street's light, and in the lamp's
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
        city[y, x, :3] = lay[y, x, :3] * gain[y]; unlit[y, x, :3] = lay[y, x, :3]; lit[y, x] = lay_lit[y, x, :3] * gain[y]
        city[y, x, 3] = unlit[y, x, 3] = 255; ch[y, x] = True
    Xp, Zp = PLANT[2], ZF - PLANT[3]                                 # its shade on the floor round its foot
    for (x, y), (s, f, X, h, d) in hit.items():
        if s not in ('floor', 'grate') or keep[y, x] or lm[y, x]: continue
        dd = np.hypot((ZF - d - Zp) / 0.13, (X - Xp) / 0.19)
        if dd < 1:
            k = 0.5 + 0.5 * dd * dd
            city[y, x, :3] *= k; unlit[y, x, :3] *= k; lit[y, x] *= k
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
    """The model's lines over a crop (x0, y0, enlarged k): the far wall, its top, the floor's edges, the mouth, B's corner,
    the window, the door, the lamp."""
    from PIL import ImageDraw
    d = ImageDraw.Draw(img)
    P = lambda X, h, Z: ((VPX + F * X / Z - x0) * k, (VPY - F * (h - EYE) / Z - y0) * k)
    seg = lambda a, b, col: d.line([P(*a), P(*b)], fill=col, width=1)
    Xb = ZF * (GX1 - VPX) / F
    for a, b in [((XF, HS, ZF), (Xb, HS, ZF)), ((XF, HT, ZF), (Xb, HT, ZF)), ((XF, HS, ZF), (XF, HT, ZF)),
                 ((XF, HS, ZF), (XF, HS, ZB)), ((XF, HT - PARAPET, ZF), (Xb, HT - PARAPET, ZF))]:
        seg(a, b, (255, 255, 0))
    seg((XF, 0.0, ZB), (XF, 9.0, ZB), (255, 255, 255))                                   # B's corner
    seg((XF, HS, 26.0), (XF, HS, 17.0), (0, 255, 0))                                     # the facades' foot (a ray)
    seg((GRATE[1], HS, ZF), (GRATE[1], HS, ZB), (0, 200, 255))
    for (xa, xb), (ha, hb) in [(WIN['x'], WIN['h']), (DOOR['x'], DOOR['h'])]:
        for a, b in [((xa, ha), (xb, ha)), ((xb, ha), (xb, hb)), ((xb, hb), (xa, hb)), ((xa, hb), (xa, ha))]:
            seg((a[0], a[1], ZF), (b[0], b[1], ZF), (255, 120, 0))
    (xa, xb), (ha, hb), (da, db) = LAMP['glass']
    for dd in (da, db):
        for a, b in [((xa, ha), (xb, ha)), ((xb, ha), (xb, hb)), ((xb, hb), (xa, hb)), ((xa, hb), (xa, ha))]:
            seg((a[0], a[1], ZF - dd), (b[0], b[1], ZF - dd), (255, 0, 255))
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
        x0, y0, x1, y1 = 880, 420, 960, 700
        z = arr[y0:y1, x0:x1].copy(); z[z[..., 3] < 128, :3] = (150, 70, 90)
        im = Image.fromarray(np.clip(np.round(z[..., :3]), 0, 255).astype(np.uint8)).resize(((x1 - x0) * 6, (y1 - y0) * 6), Image.NEAREST)
        im.save(os.path.join(out, f'{tag}_x6.png'))
        if tag == 'lit': lines(im.copy(), x0, y0, 6).save(os.path.join(out, 'lines_x6.png'))
    print('changed', int(ch.sum()), 'px; comp', int((comp[..., 3] > 0).sum()), 'px')


if __name__ == '__main__':
    if '--preview' in sys.argv: preview(sys.argv[sys.argv.index('--preview') + 1])
