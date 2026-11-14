#!/usr/bin/env python3
"""The small canopy over the pink-lit entrance right of the pole, and its end against Ichiraku (the owner: "le haut-vent
juste à droite... porte rose : petit truc bizarre entre ça et la façade d'Ichiraku").

    (a module: tools/redraw_zones.py's zone 'canopy' calls draw() on the street as the zones before it leave it)

What was there (the 'pole' zone's draft, x 1069..1118, y 466..528): a corrugated awning seen from above, though it hangs
over the eye (its top a pale slanted band with pink glints), its lower edge ragged; under it a black band down to the
lit transom; at its right end, against Ichiraku's front, a dark slot four pixels wide from the ledge down to the
transom (x 1115..1119), the corner of the two walls lost in it.
Now, in the street's own camera (the vanishing point 700, 615, f 960 px, the eye 1.41 m up; the house's front a plane
4.45 m right of the eye's line, its foot on the sidewalk's line v -0.283, as the 'pole' zone found it):
- a thin aluminium canopy (a box 4.5 cm thick, 0.65 m deep, falling 6 cm to its front) fixed to the wall 2.66 m up, a
  hand's width over the transom, from behind the pole (its far end) to 2 px short of the corner (no brackets: the
  cantilevered aluminium hoods of Japanese entrances): seen from below, as the eye sees a thing over it (cast pixel by
  pixel, 4 x 4 rays a pixel, each pixel one face): its near end square to the view, a straight edge rising to the wall
  (its thickness, its top lip lit, its lower edge darker); under it, its underside, a wedge widening toward the pole,
  lit by the hall's pink-violet light from the transom under it (lighter by the wall, in steps), dark in the power cut;
  its front edge, facing the street, runs behind the pole, which hides it (R24: the pole's pixels are not touched);
- the wall: the house's dark vertical planks run down from under the ledge to the canopy's top (each column its own
  plank, from the painter's rows under the ledge), and under the canopy, in its shadow, down to the transom's frame
  (the planks darkened, the transom's pink on the rows over it); its left corner trim (x 1065..1068) left as it is;
- the corner: the two buildings meet as they do above and below the old slot (the house's last plank, the seam, then
  Ichiraku's corner and its plaster, each column the painter's from under it, rows 548..600, its light the plaster's
  beside it row by row): no slot.
In the power cut the walls are the power cut's own pixels by the same rule, the canopy its street colours darkened as
the planks are there, its underside dark. Ichiraku's wall lamp's glow (street.js IRL) still falls on the corner.
Needs Pillow, numpy.
"""
import numpy as np

VPX, VPY, FOC, EYE = 700.0, 615.0, 960.0, 1.41
BOX = (1065, 452, 1124, 532)                    # the zone (redraw_zones.py 'canopy')
XF = 4.45                                       # the house's front (m right of the eye's line)
CAN = dict(h=2.66, d=0.65, drop=0.06, t=0.045, z0=10.32, z1=11.9)   # fixed at h, depth, its fall to the front,
                                                # thickness, its near and far ends (m along the street)
LEDGE_V = 0.3938                                # the ledge's underside (a ray: v = (615 - y) / (x - 700))
TRANSOM_V = 0.229                               # the transom's top frame (a ray)
X_WALL = (1069, 1115)                           # the planks' columns (the corner trim left of them, the seam right)
JUNCTION = (1116, 1119, 459, 528)               # the corner's columns and the old slot's rows
BELOW = (548, 600)                              # (the corner's rows under the entrance: the clean junction)
PLASTER_REF = 1122                              # (Ichiraku's plaster beside it: its light row by row)
SHADE = 0.55                                    # the wall in the canopy's shadow
# the canopy's faces (street; the power cut: the same times the planks' darkening, its underside dark)
END = dict(top=(56, 56, 92), face=(38, 40, 68), low=(26, 28, 50))   # (the ledge's lit line over it: 33, 35, 68)
FRONT = (94, 88, 126)
UNDER = [(104, 64, 98), (74, 48, 80), (48, 34, 60)]    # by the wall .. its front (the hall's light, in steps)
UNDER_CUT = (14, 16, 30)
TRANSOM_SPILL = np.array([22.0, 10.0, 20.0])   # (the transom's pink on the wall's row over its frame)


def ray(x, v):
    """The row (float) of the ray v at column x (pixel centres)."""
    return VPY - v * (x + 0.5 - VPX) - 0.5


def cast(xs, ys):
    """What the eye's rays through (xs, ys) meet first on the canopy: 0 none, 1 its near end, 2 its front, 3 its
    underside; and how far from the wall (0 at the wall, 1 at its front) for the underside."""
    c = CAN; n = len(xs)
    tx, ty = (xs - VPX) / FOC, (VPY - ys) / FOC          # (a ray: X = tx Z, Y = EYE + ty Z)
    xo = XF - c['d']
    bot = lambda X: c['h'] - c['drop'] * (XF - X) / c['d']   # (its underside's height at X)
    kind = np.zeros(n, int); frac = np.zeros(n); best = np.full(n, np.inf)
    # its near end: the plane Z = z0
    Z = np.full(n, c['z0']); X, Y = tx * Z, EYE + ty * Z
    m = (X >= xo) & (X <= XF) & (Y >= bot(X)) & (Y <= bot(X) + c['t'])
    kind[m] = 1; best[m] = Z[m]
    # its front: the plane X = xo
    with np.errstate(divide='ignore', invalid='ignore'):
        Z = np.where(tx > 0, xo / tx, np.inf)
    Y = EYE + ty * Z
    m = (Z >= c['z0']) & (Z <= c['z1']) & (Y >= bot(xo)) & (Y <= bot(xo) + c['t']) & (Z < best)
    kind[m] = 2; best[m] = Z[m]
    # its underside: Y = bot(X), with X = tx Z: solve EYE + ty Z = h - drop (XF - tx Z) / d
    a = ty - c['drop'] * tx / c['d']; b = c['h'] - c['drop'] * XF / c['d'] - EYE
    with np.errstate(divide='ignore', invalid='ignore'):
        Z = np.where(np.abs(a) > 1e-9, b / a, np.inf)
    X = tx * Z
    m = (Z >= c['z0']) & (Z <= c['z1']) & (X >= xo) & (X <= XF) & (Z < best)
    kind[m] = 3; best[m] = Z[m]; frac[m] = (XF - X[m]) / c['d']
    return kind, frac


def canopy(box):
    """Per pixel of box: which face (the most of its rays: crisp), and for the underside how far out (its middle ray)."""
    x0, y0, x1, y1 = box; h, w = y1 - y0, x1 - x0
    o = (np.arange(4) + 0.5) / 4
    gy, gx = np.mgrid[y0:y1, x0:x1].astype(float)
    xs = (gx[..., None, None] + o[None, None, None, :]).repeat(4, 2).reshape(-1)
    ys = (gy[..., None, None] + o[None, None, :, None]).repeat(4, 3).reshape(-1)
    kind, frac = cast(xs, ys)
    K = kind.reshape(h, w, 16); F = frac.reshape(h, w, 16)
    cnt = np.stack([(K == k).sum(-1) for k in range(4)], -1)
    face = np.where(cnt[..., 1:].sum(-1) >= 8, 1 + cnt[..., 1:].argmax(-1), 0)
    n3 = (K == 3).sum(-1)
    fr = np.where(K == 3, F, 0).sum(-1) / np.maximum(n3, 1)
    return face, fr


def planks(arr, x):
    """The house's plank at column x: the painter's colour under the ledge (rows 3..8 under its underside)."""
    r = int(np.floor(ray(x, LEDGE_V))) + 1
    return np.median(arr[r + 3:r + 9, x, :3], 0), r + 3


def draw(city, unlit, box=BOX):
    """The zone (redraw_zones.py): both layers changed in place over box; returns what changed (whole scene)."""
    x0, y0, x1, y1 = box
    H, W = city.shape[:2]
    ch = np.zeros((H, W), bool)
    face, fr = canopy(box)
    # the planks' darkening in the power cut (the canopy's colours there)
    pc = np.array([planks(city, x)[0] for x in range(*X_WALL)]); pu = np.array([planks(unlit, x)[0] for x in range(*X_WALL)])
    dark = 0.72 * np.clip((np.median(pu, 0) + 1) / (np.median(pc, 0) + 1), 0.3, 1.2)   # (and the lamp's share out)
    for arr, cut in ((city, False), (unlit, True)):
        src = arr.copy()
        # the wall: planks down from under the ledge, in the canopy's shadow under it, to the transom's frame
        for x in range(X_WALL[0], X_WALL[1] + 1):
            p, r0 = planks(src, x)
            r1 = int(np.ceil(ray(x, TRANSOM_V)))                     # (the transom's frame: from here down, as it is)
            under = False
            for y in range(max(r0, y0), min(r1, y1)):
                f = face[y - y0, x - x0]
                if f: under = True; continue
                c = p * SHADE if under else p
                if under and not cut and 1081 <= x <= 1113 and y >= r1 - 3:   # (the transom's glow on the rows over it)
                    c = c + TRANSOM_SPILL * (1.0 - 0.33 * (r1 - 1 - y))
                arr[y, x, :3] = c; ch[y, x] = True
        # the corner: as under the entrance (each column its own), its light the plaster's beside it
        ja, jb, ra, rb = JUNCTION
        ref = np.median(src[BELOW[0]:BELOW[1], PLASTER_REF, :3], 0) + 1
        for x in range(ja, jb + 1):
            base = np.median(src[BELOW[0]:BELOW[1], x, :3], 0)
            for y in range(ra, rb + 1):
                k = np.clip((src[y, PLASTER_REF, :3] + 1) / ref, 0.7, 1.3)
                arr[y, x, :3] = base * k; ch[y, x] = True
        # the canopy
        for y in range(y0, y1):
            for x in range(x0, x1):
                f = face[y - y0, x - x0]
                if not f: continue
                if f == 1:                                           # its near end: its top lip lit, its lower edge dark
                    up = face[y - 1 - y0, x - x0] if y - 1 >= y0 else 0
                    dn = face[y + 1 - y0, x - x0] if y + 1 < y1 else 0
                    c = np.array(END['top'] if up != 1 and up != 2 else END['low'] if dn == 3 or dn == 0 else END['face'], float)
                elif f == 2:
                    c = np.array(FRONT, float)
                else:
                    c = np.array(UNDER_CUT if cut else UNDER[min(2, int(fr[y - y0, x - x0] * 3))], float)
                if cut and f != 3: c = c * dark
                arr[y, x, :3] = c; arr[y, x, 3] = 255; ch[y, x] = True
    return ch
