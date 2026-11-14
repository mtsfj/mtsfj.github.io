#!/usr/bin/env python3
"""The two roofs on the left, their eaves redrawn: Kirua's house (the roof he sits on, over the dagashi-ya) and the dojo's
house above it (its eave's end at the top left). Old tiles, a clean gutter, the roofs in the street's own perspective.

    (a module: tools/redraw_zones.py's zones 'eaveKs', 'eaveK1'..'eaveK5', 'eaveD' and 'eaveP' call draw() on the street
     as the zones before them leave it, each inside its own box; it also writes, from the zone's before copies
     tools/src/edits/<zone>_before_{sun,nf}.webp, the street_sun marks of what it draws and night_far's 0 there.
     python3 tools/left_eaves.py --preview DIR   draws them from the zones' before copies into DIR, nothing in assets/)

What was there: along each eave a band of navy blotches nobody could read (the tiles and the gutter in one mush), as
thick at Kirua's far end as at his house's near corner (a band of one size that does not grow toward the viewer is not
in perspective), its top edge drifting off the street's rays; round the near corner a black mass with a faint line;
the eave's far end at x 346 (tools/kirua_gutter.py had shortened it there): 38 cm short of the far wall, whose corner
is at x 325 on the wall but at x 357 on the eave's line, so the roof stopped before the house did; the dojo's eave a
dark wedge whose outer edge ran off the rays, its end a blob, its downpipe running up into its soffit.

Each roof is now a small model in the street's perspective (VP (700, 615), the eye 1.41 m up, f 959.5 px, as
tools/arcade_eave.py: a line along the street keeps (615 - y) / (700 - x), its height over the eye over its distance
from the street's axis; a line across the street is level), each pixel the colour of what its middle ray meets first
(3 x 3 rays a pixel give the edge against the sky its alpha):
- the tiles: kawara, old and smoked: at the eave the barrels' (round tiles') ends, a disc every 27 cm, a slight bump
  (3 cm) over the flat tiles' lip (karakusa) between them, so the row's edge is gently toothed and the bumps shrink
  with distance; each disc lit on its top and on its side toward the far end of the street (the night's light comes down
  the street) against the shaded troughs, a shade apart from its neighbours (old tiles are never one colour), its
  shadow on the lip at its near side; between two discs, over the lip, the next barrel's top going up the roof;
- the gutter: half-round (9 cm), hung under the lip and a little in front of it: its rolled rim a lit pixel, its belly
  darker as it turns under, a hanger strapped round it every 60 cm and hooked over its rim;
- Kirua's house, a hipped roof (the painter's level return at its near corner says so): its front's top under the
  soffit on the painter's ray (s 0.983), its corners at x 158 and x 325, its eave 44 cm out (the house's scale under
  Kirua, 78 px/m at his seat); round the near corner (tucked under the dojo's eave) the level hip eave in the shade, its
  tiles' ends face on, small and flush in the row (a pixel's bump), mitred into the front's; at the far end the eave runs
  on K_OVER past the far wall and turns the far corner: there the hip's fascia board seen from below (its inner face, its
  foot lit), the gutter hung on its far side (its belly under the board's foot), the street's gutter mitred into it; the
  overhang's underside in a soft shade, lighter toward the corner, the rafters' feet square to each eave and the hip
  rafter on the diagonal; on the hip's gutter, over the wall's corner, the rain head (K_HEAD) and a short neck down to
  the painter's downpipe on that corner (tools/kirua_gutter.py's), which goes on down as he painted it (the owner, on a
  first far end: a long level bar floating under the eave, sky over it, a swan neck under it, a flat black wedge); the
  ridge and the hips are behind the eaves from the street. The beam the
  painter drew under the soffit, clean on its ray (his tones across it). Kirua's seat (KM.seat in assets/street.js) is
  on the tiles' tops, his feet over the gutter; the drips (DRIPS 'kirua') fall from the gutter's far corner;
- the dojo's house: the same tiles and gutter, the gutter's rim catching the dusk as the painter had it (his pink,
  marked in street_sun as his was, so the hours read it the same), its far end the gutter's circle; under it the
  painter's soffit cleaned whole (his dark, the beam along the wall a little lighter, on its ray), its end edge level;
  under the gutter's end a box and a swan neck into the downpipe the two houses share (x 137..140), a bracket round
  the pipe; the old pipe's stub up into the soffit gone (the corner's shadow beside it there).
The pipes are round (lit toward the street and the sky), each in the painter's own colours, column for column where they
come down the wall. What the painter's band had beyond the new edges is the sky again (transparent), or his soffit
under them. Colours are the painter's (picked from his band, his soffit and beams, his dusk rim, his downpipes); the
power cut the same as lit (the painter's unlit layer is his lit one there: no light of the street reaches the roofs).
In layer_city_off and street_unlit (by the zones' patches), street_sun (the dusk rim and the pipes marked as the
painter's, nothing else of what changed) and night_far (0, the street's, as round them: two of the dojo's old tile
pixels were marked sky). Needs numpy, Pillow.
"""
import os
import sys
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDITS = os.path.join(ROOT, 'tools', 'src', 'edits')
VP = (700.0, 615.0)
F = 959.5                                      # px per m at 1 m (tools/r6_sprites.py)
EYE = 1.41
SS = 3                                         # rays a pixel, each way

# the painter's colours: his eave band's light, darkest first (its quantiles, the pixel nearest each one's mean), his
# soffits and the beam along the dojo's wall, his downpipe, the dojo's dusk rim
N = [(3, 7, 13), (7, 15, 25), (11, 20, 38), (15, 25, 46), (18, 28, 55), (22, 33, 63), (30, 37, 70), (38, 40, 75),
     (54, 55, 86)]
SOFFIT_K = (1, 6, 1)                           # (Kirua's, under his eave and its return)
SOFFIT_D, BEAM_D = (0, 4, 1), (6, 12, 14)      # (the dojo's, and its beam along the wall)
PIPE = dict(dark=(7, 14, 25), mid=(20, 28, 49), lit=(31, 36, 66), rim=(94, 60, 90))
DUSK = [(63, 36, 58), (79, 52, 66), (102, 73, 101)]
LUMA = np.array([0.299, 0.587, 0.114])


def eave(**k):
    """An eave along the street at X (m from the axis), its discs' tops on the ray s_top, what hangs on it."""
    e = dict(rd=0.06, lip=(-0.035, 0.030), pitch=0.27, first=0.15, rg=0.045, gdrop=0.075, gout=0.005, tilt=0.5,
             hang=0.60, hang0=0.20)
    e.update(k)
    e['yt'] = EYE + e['s_top'] * e['X']        # the discs' tops (the barrels' ends, 3 cm over the flat tiles' lip)
    e['yc'] = e['yt'] - e['rd']                # their centres; the lip about them
    e['yr'] = e['yc'] - e['gdrop']             # the gutter's rim (under the discs)
    e['xg'] = e['X'] - e['gout']               # its axis (its front rim in front of the lip)
    e['ys'] = e['yr'] - e['rg']                # the soffit (the gutter's bottom)
    return e


# Kirua's house, a hipped roof (the painter's level return at its near corner): its discs' tops on his edge where Kirua
# sits (x 290..345, s 1.110: his seat (325, 199) on the tiles), its scale the house's under him (78 px/m at his seat:
# the eave 4.8 m from the street's axis); its front's top under the soffit on the painter's ray (s 0.983,
# tools/kirua_house_side.py), so the wall 5.24 m out; its near corner (x 158 on the wall) and its far one (x 325, the
# downpipe's arris), the eave's near corner at x 200 (the painter's, tucked under the dojo's eave: a 6 cm overhang
# there), and past the far wall an overhang of K_OVER (the eave had stopped 38 cm short of that wall, at x 346: the
# roof ended before the house)
K_OVER = 0.35
K = eave(X=4.80, s_top=1.110, x_corner=200.0, first=0.08)
K['yso'] = K['yc'] + K['lip'][0]                # (its soffit: the ceiling of the overhang, at the lip's foot)
K['xw'] = (K['yso'] - EYE) / 0.983               # (the front wall, its top under the soffit on the painter's ray)
K['zs'] = F * K['X'] / (VP[0] - K['x_corner'])   # (the near hip's eave)
K['zn'] = F * K['xw'] / (VP[0] - 158.0)          # (the near end wall)
K['zf'] = F * K['xw'] / (VP[0] - 325.5)          # (the far end wall)
K['ze'] = K['zf'] + K_OVER                       # (the far hip's eave)
K['x_end'] = VP[0] - F * K['X'] / K['ze']
K_X0 = 141                                       # (left of this the painter's: the dojo's corner, the shared downpipe)
K_CORNER_X = 325                                 # (the house's far corner: from here the model draws all, under the eave too)
K_SIDE = (59, 84)                                # (the painter's band round the corner: its rows, its end wall under it)
K_BEAM = (1.0425, 1.0560, 202, 324)              # the beam under the soffit (the painter's, on its ray: s from, to; x)
BEAM_K = [(10, 16, 26), (13, 21, 36), (10, 19, 34), (7, 16, 30), (6, 13, 22), (4, 10, 15)]   # (his, from its lower edge)
K_FASC = (0.075, 0.02)                           # the hip's fascia: its height under the soffit, the gutter's gap to it
K_RAFT = 0.45                                    # the rafters' spacing under the overhang
K_HEAD = 5.22                                    # the rain head on the hip's gutter: m from the axis (over the wall's corner)
RET_D = (0.042, 0.010)                           # the near return's tile ends, face on: their radius, their rise over the lip
# the downpipes: the painter's (Kirua's: tools/kirua_gutter.py's, x 326..330 against the far corner; the dojo's, x 137..140
# on its corner), each now fed from its gutter by a collecting box under the gutter's end and a swan neck (yobi-toi:
# two bends, a short slanting run back to the wall), the pipe down from the lower bend; m, from the street's axis
KP = dict(x=5.20, cx=328.5, r=0.034, top=6.20, cols=(326, 330), ref=285, box=(0.045, 0.09),
          ramp=[PIPE['dark'], PIPE['mid'], PIPE['lit'], PIPE['rim']], sun=(0, 0, 0, 232))
# the dojo's house: its discs' tops on the painter's outer edge (s 1.134), its far end at x 183.5, the soffit's edge on
# the wall on the painter's ray (s 1.040, his boards' corner), his beam along it
D = eave(X=4.83, s_top=1.134, x_end=183.5)
D['ze'] = F * D['X'] / (VP[0] - D['x_end'])
D['xw'] = (D['ys'] - EYE) / 1.040                # (the wall under it)
D_BEAM = 0.09                                    # (the beam along the wall: its width under the soffit)
D_X0, D_Y1 = 100, 50                             # (the dojo's eave and soffit: from here, above this row)
D_CORNER = 131                                   # (its corner post: x 131..141, the shared downpipe on it)
DP = dict(x=5.15, cx=139.0, r=0.019, top=6.51, cols=(137, 140), ref=66, box=(0.03, 0.07), bracket=6.39,
          ramp=[(14, 1, 1), (11, 8, 13), (58, 24, 26), (102, 38, 38), (102, 47, 49)], sun=(0, 0, 255, 255, 255))
for _P in (KP, DP): _P['z'] = F * _P['x'] / (VP[0] - _P['cx'])

TILE, LIP, GUT, HANGER, SOFF, DISC, VPIPE, PIPEK, VPIPE_D, WALL, FASC = 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11
KP['vk'], DP['vk'] = VPIPE, VPIPE_D


def rays(xs, ys):
    """Sample positions (pixel coordinates, continuous) -> per unit Z: dx (m to the left), dy (m up)."""
    return (VP[0] - xs) / F, (VP[1] - ys) / F


def roots(a, b, c):
    disc = b * b - 4 * a * c
    return np.where(disc >= 0, (-b - np.sqrt(np.maximum(disc, 0))) / (2 * a), np.inf)


def cyl_z(dx, dy, xa, ya, r):
    """Where the rays first meet a cylinder along the street (axis at X xa, height ya): their Z, or inf."""
    return roots(dx * dx + dy * dy, -2 * (dx * xa + dy * (ya - EYE)), xa * xa + (ya - EYE) ** 2 - r * r)


def cyl_x(dx, dy, ya, za, r):
    """Where the rays first meet a cylinder across the street (axis at height ya, Z za): their Z, or inf."""
    return roots(dy * dy + 1, -2 * (dy * (ya - EYE) + za), (ya - EYE) ** 2 + za * za - r * r)


def cyl_any(dx, dy, p0, ax, r):
    """Where the rays first meet a cylinder through p0 along the unit vector ax: (Z, position along it)."""
    d = np.stack([dx, dy, np.ones_like(dx)], -1); w = np.array([0.0, EYE, 0.0]) - np.array(p0); ax = np.asarray(ax)
    dp = d - (d @ ax)[..., None] * ax; wp = w - (w @ ax) * ax
    z = roots((dp * dp).sum(-1), 2 * (dp @ wp), wp @ wp - r * r)
    return z, (w @ ax) + z * (d @ ax)


def capsule(dx, dy, a, b, r):
    """Where the rays first meet the capsule from a to b (radius r; a pipe with its rounded bends): Z, the unit normal."""
    d = np.stack([dx, dy, np.ones_like(dx)], -1); dn = np.linalg.norm(d, axis=-1, keepdims=True); rd = d / dn
    ro = np.array([0.0, EYE, 0.0]); a = np.asarray(a, float); b = np.asarray(b, float)
    ba = b - a; oa = ro - a; baba = ba @ ba; bard = rd @ ba; baoa = ba @ oa; rdoa = rd @ oa; oaoa = oa @ oa
    A = baba - bard * bard; B = baba * rdoa - baoa * bard; C = baba * oaoa - baoa * baoa - r * r * baba
    h = B * B - A * C
    t = np.where((h >= 0) & (A > 1e-12), (-B - np.sqrt(np.maximum(h, 0))) / np.where(A > 1e-12, A, 1), np.inf)
    yy = baoa + t * bard
    side = np.isfinite(t) & (yy > 0) & (yy < baba)
    oc = np.where((yy <= 0)[..., None], oa, ro - b)                      # (else its rounded ends)
    bb = (rd * oc).sum(-1); cc = (oc * oc).sum(-1) - r * r; hh = bb * bb - cc
    tc = np.where(hh > 0, -bb - np.sqrt(np.maximum(hh, 0)), np.inf)
    t = np.where(side, t, tc)
    p = ro + rd * t[..., None]
    k = np.clip(((p - a) @ ba) / baba, 0, 1)
    n = (p - a - k[..., None] * ba) / r
    return np.where(np.isfinite(t) & (t > 0), t * rd[..., 2], np.inf), n


def box_hit(dx, dy, lo, hi):
    """Where the rays first meet the box lo..hi (x, y, z corners): Z, the unit normal of the face met."""
    d = np.stack([dx, dy, np.ones_like(dx)], -1); ro = np.array([0.0, EYE, 0.0])
    with np.errstate(divide='ignore'):
        t1 = (np.asarray(lo) - ro) / d; t2 = (np.asarray(hi) - ro) / d
    tn = np.minimum(t1, t2); tf = np.maximum(t1, t2)
    tin = tn.max(-1); tout = tf.min(-1); ax = tn.argmax(-1)
    ok = (tin <= tout) & (tin > 0)
    n = np.zeros(d.shape); idx = np.indices(ax.shape)
    n[(*idx, ax)] = -np.sign(np.take_along_axis(d, ax[..., None], -1)[..., 0])
    return np.where(ok, tin, np.inf), n


def tone(ramp, L, parity, band=0.07):
    """A colour of the ramp (darkest first) for the light L in 0..1; at a step the two tones meet in a checkerboard."""
    ramp = np.asarray(ramp, float); n = len(ramp)
    q = np.clip(np.nan_to_num(L, nan=0.0, posinf=1.0, neginf=0.0), 0, 0.999) * n; i = np.floor(q).astype(int); f = q - i
    j = np.where((f < band) & (parity % 2 == 1), np.maximum(i - 1, 0), i)
    return ramp[j]


class Hit:
    """The nearest thing each ray meets (its depth, colour, kind, dusk mark); whether it passed over a roof or under it."""
    def __init__(self, shape):
        self.z = np.full(shape, np.inf); self.rgb = np.zeros(shape + (3,)); self.kind = np.zeros(shape, int)
        self.sun = np.zeros(shape); self.over = np.zeros(shape, bool); self.under = np.zeros(shape, bool)

    def put(self, z, ok, rgb, kind, sun=0.0):
        m = ok & (z < self.z) & (z > 0)
        self.z[m] = z[m]; self.rgb[m] = np.broadcast_to(rgb, self.rgb.shape)[m]
        self.kind[m] = kind; self.sun[m] = np.broadcast_to(sun, self.sun.shape)[m]


def front(H, E, dx, dy, par, z0, z1, gz0, gz1=None):
    """An eave along the street from Z z0 to z1 (its gutter from gz0 to gz1): its lip, discs, round tiles, gutter,
    hangers. The barrels' ends a slight bump over the flat tiles' lip (3 cm), lit along their tops against the shaded
    troughs between them."""
    X, yc, rd, P = E['X'], E['yc'], E['rd'], E['pitch']
    lo, hi = yc + E['lip'][0], yc + E['lip'][1]
    gz1 = z1 if gz1 is None else gz1
    # the lip (the flat tiles' front: the troughs between the barrels), its top a pixel lighter; the disc's shade on it
    zl = X / dx; yl = EYE + zl * dy
    inz = (zl >= z0) & (zl <= z1)
    over = inz & (yl > hi)
    H.over |= over; H.under |= inz & (yl < lo)
    near = ((z0 + E['first'] + np.round((zl - z0 - E['first']) / P) * P) - zl) / rd
    sh = (near > 0.9) & (near < 1.5)
    Ll = np.where(yl > hi - 0.011, 0.30, 0.20) - 0.12 * sh
    H.put(zl, inz & (yl >= lo) & (yl <= hi), tone(N[1:8], Ll, par), LIP)
    # the discs (the barrels' ends), a little proud of the lip; each its own shade, lit on top
    zd = (X - 0.006) / dx; yd = EYE + zd * dy
    kd = np.round((zd - z0 - E['first']) / P); zk = z0 + E['first'] + kd * P
    yr_, zr_ = (yd - yc) / rd, (zd - zk) / rd
    ok = (kd >= 0) & (zk <= z1 - 0.05) & (yr_ ** 2 + zr_ ** 2 <= 1.0)
    Ld = 0.50 + 0.42 * yr_ + 0.12 * zr_ + 0.05 * np.sin(kd * 2.3 + 0.7)
    Ld = np.where((yr_ ** 2 + zr_ ** 2 > 0.64) & (zr_ < 0), Ld - 0.15, Ld)  # (its rim turning away from the light)
    H.put(zd, ok, tone(N[2:9], Ld, par), DISC)
    # the barrels up the roof behind each disc, their part over the flat tiles: seen only over the lip
    ax = np.array([1.0, E['tilt'], 0.0]); ax /= np.linalg.norm(ax)
    nrm = np.array([-E['tilt'], 1.0, 0.0]) / np.linalg.norm([E['tilt'], 1.0])
    rb = rd * 0.92; flat = (hi - yc) * nrm[1]                          # (the flat tiles' surface over the barrels' axes)
    for k in range(int((z1 - z0 - E['first']) / P) + 1):
        zk_ = z0 + E['first'] + k * P
        if zk_ > z1 - 0.05: break
        zb, t = cyl_any(dx, dy, (X, yc, zk_), ax, rb)
        Pb = np.stack([zb * dx - X, EYE + zb * dy - yc, zb - zk_], -1)
        hgt = np.clip(((Pb @ nrm) - flat) / (rb - flat), -1, 1)          # (0 at the flat tiles, 1 on the barrel's ridge)
        side = Pb[..., 2] / rb                                             # (-1 its flank toward us, 1 toward the far end)
        okb = (t > 0.0) & (t < 1.2) & (hgt > -0.05) & over
        Lb = 0.10 + 0.70 * hgt + 0.08 * side + 0.05 * np.sin(k * 2.3 + 0.7)
        H.put(zb, okb, tone(N[1:8], Lb, par), TILE)
    # the gutter, in front of the lip and under it: its rim, its belly turning under; the hangers' straps round it
    zg = cyl_z(dx, dy, E['xg'], E['yr'], E['rg'])
    Xg, Yg = zg * dx, EYE + zg * dy
    okg = (zg >= gz0) & (zg <= gz1) & (Yg <= E['yr'] + 1e-4)
    ang = np.degrees(np.arctan2(-(Yg - E['yr']), -(Xg - E['xg'])))     # (0 at its front rim, 90 under it)
    Lg = np.clip(0.80 - ang / 110.0, 0, 1)
    rgb = tone(N[1:8], Lg, par, 0.09)
    zh = z1 - E['hang0'] - np.round((z1 - E['hang0'] - zg) / E['hang']) * E['hang']
    strap = (np.abs(zg - zh) * F * X / np.maximum(zg, 1) ** 2 < 0.5) & (ang > 8)
    rgb = np.where(strap[..., None], np.array(N[1], float), rgb)
    H.put(zg, okg, rgb, GUT)
    H.kind[(H.kind == GUT) & strap & (H.z == zg)] = HANGER
    # the hangers' hooks over the rim: a dark pixel just over it
    zr = E['xg'] - E['rg']
    for zh_ in np.arange(z1 - E['hang0'], gz0, -E['hang']):
        hx, hy = (VP[0] - F * zr / zh_), (VP[1] - F * (E['yr'] + 0.012 - EYE) / zh_)
        m = (np.abs(VP[0] - F * dx - hx) < 0.5) & (np.abs(VP[1] - F * dy - hy) < 0.5)
        H.put(np.full(dx.shape, zh_ - 0.01), m, np.array(N[1], float), HANGER)
    return zg, okg, ang


def pipe(H, dx, dy, par, P, gutter, zbox, xbox=None):
    """A downpipe fed from its gutter: the collecting box under the gutter (its bottom at the gutter's, centred at Z
    zbox), the swan neck from the box down and back to the wall (one straight run, its two bends rounded), the pipe down
    the wall from the lower bend (VPIPE: in the painter's pipe's own columns), a bracket round it (P bracket)."""
    xg, gb = gutter
    xg = xg if xbox is None else xbox
    bw, bh = P['box']
    zb, nb = box_hit(dx, dy, (xg - bw, gb - bh, zbox - bw), (xg + bw, gb, zbox + bw))
    Lbx = 0.45 + 0.45 * nb[..., 1] - 0.35 * nb[..., 0] - 0.25 * nb[..., 2]   # (its face to the street lit, its side to us
    ramp = P['ramp']; sun = np.array(P['sun'], float)                       # darker, its bottom dark)
    q = np.clip(np.nan_to_num(Lbx) * len(ramp), 0, len(ramp) - 1e-3).astype(int)
    H.put(zb, np.isfinite(zb), np.array(ramp, float)[q], PIPEK, sun[q] / 255.0)
    a = (xg, gb - bh * 0.8, zbox); b = (P['x'], P['top'], P['z'])
    for (p0, p1, kind) in ((a, b, PIPEK), (b, (P['x'], P['top'] - 1.2, P['z']), P['vk'])):
        zc, n = capsule(dx, dy, p0, p1, P['r'])
        L = 0.45 + 0.40 * n[..., 1] - 0.35 * n[..., 0] - 0.10 * n[..., 2]
        q = np.clip(np.nan_to_num(L) * len(ramp), 0, len(ramp) - 1e-3).astype(int)
        H.put(zc, np.isfinite(zc), np.array(ramp, float)[q], kind, sun[q] / 255.0)
    if P.get('bracket'):                                                    # (a band round it, 2 cm: its top edge lit
        yb = P['bracket']                                                   # as the pipe's face, its underside dark)
        zc, n = capsule(dx, dy, (P['x'], yb + 0.05, P['z']), (P['x'], yb - 0.07, P['z']), P['r'] * 1.35)
        Y = EYE + zc * dy
        band = np.isfinite(zc) & (Y <= yb + 0.002) & (Y >= yb - 0.018)
        top = Y > yb - 0.008
        H.put(zc, band, np.where(top[..., None], np.array(ramp[-1], float), np.array(ramp[0], float)), PIPEK,
              np.where(top, sun[-1] / 255.0, 0.0))


def kirua(H, dx, dy, par):
    E = K
    zs, ze = E['zs'], E['ze']
    front(H, E, dx, dy, par, zs, ze, zs - E['gout'] - E['rg'], ze + K_FASC[1] + 2 * E['rg'])
    X, yc, rd, P = E['X'], E['yc'], E['rd'], E['pitch']
    lo, hi = yc + E['lip'][0], yc + E['lip'][1]
    # the near hip's eave, face on and in the shade: its lip, its tiles' ends (round, small, flush in the row: a bump of
    # a pixel over it), its level gutter, from the corner in (the corner mitred)
    xp = zs * dx; yp = EYE + zs * dy
    inx = xp >= X
    H.over |= inx & (yp > hi); H.under |= inx & (yp < lo)
    rr0, rise = RET_D
    jl = ((X + E['first'] + np.round((xp - X - E['first']) / P) * P) - xp) / rr0
    sh = (jl < -0.9) & (jl > -1.5)                                       # (the disc's shade, on its right)
    Ll = np.where(yp > hi - 0.011, 0.42, 0.26) - 0.12 * sh
    H.put(np.full(dx.shape, zs), inx & (yp >= lo) & (yp <= hi), tone(N[0:6], Ll, par), LIP)
    zd = zs - 0.004; xd = zd * dx; yd = EYE + zd * dy
    jd = np.round((xd - X - E['first']) / P); xj = X + E['first'] + jd * P
    ycr = hi + rise - rr0
    yr_, xr_ = (yd - ycr) / rr0, (xd - xj) / rr0
    rr = np.sqrt(yr_ ** 2 + xr_ ** 2)
    ok = (jd >= 0) & (rr <= 1.0)
    Ld = 0.36 + 0.04 * np.sin(jd * 1.9 + 2.0) + np.where(rr > 0.7, 0.26 * yr_ - 0.06 * xr_, 0.0) - 0.10 * (rr < 0.3)
    H.put(np.full(dx.shape, zd), ok, tone(N[0:6], Ld, par), DISC)
    zgs = cyl_x(dx, dy, E['yr'], zs - E['gout'], E['rg'])
    Xs, Ys = zgs * dx, EYE + zgs * dy
    oks = (Xs >= E['xg'] - E['rg']) & (Ys <= E['yr'] + 1e-4)
    angs = np.degrees(np.arctan2(-(Ys - E['yr']), -(zgs - (zs - E['gout']))))
    H.put(zgs, oks, tone(N[0:6], np.clip(0.82 - angs / 105.0, 0, 1), par, 0.09), GUT)
    # the far hip's eave, seen from below: its fascia board (its inner face toward us, its foot lit), the gutter hung on
    # its far side (only its belly under the board's foot), mitred into the street's at the corner
    fh, fo = K_FASC
    zf_ = np.full(dx.shape, ze); xf_ = ze * dx; yf_ = EYE + ze * dy
    okb = (xf_ >= E['X'] - 0.004) & (yf_ <= E['yso']) & (yf_ >= E['yso'] - fh)
    near = np.clip((xf_ - E['X']) / 0.55, 0, 1)                           # (the light from the corner, fading in)
    Lf = np.where(yf_ < E['yso'] - fh + 0.012, 0.62, 0.36) - 0.22 * near
    H.put(zf_, okb, tone(N[0:6], Lf, par, 0.08), FASC)
    zgf = ze + fo + E['rg']
    zgx = cyl_x(dx, dy, E['yr'], zgf, E['rg'])
    Xf, Yf = zgx * dx, EYE + zgx * dy
    okf = (Xf >= E['xg'] - E['rg']) & (Yf <= E['yr'] + 1e-4)
    af = np.degrees(np.arctan2(-(Yf - E['yr']), (zgx - zgf)))           # (0 its far rim, 90 under it, 180 its near rim)
    H.put(zgx, okf, tone(N[0:6], np.clip(0.62 - (af - 40) / 150.0, 0, 1), par, 0.09), GUT)
    # the soffit under the overhang: its boards in a soft shade, lighter toward the eaves' corner; the rafters' feet, square
    # to each eave (the street's run back to the wall, the hip's toward us), the hip rafter on the diagonal
    zso = (E['yso'] - EYE) / dy; xso = zso * dx
    oks = (xso >= E['X'] - 0.002) & (zso >= zs) & (zso <= ze) & ((xso <= E['xw']) | (zso >= E['zf']))
    u, v = xso - E['X'], ze - zso                                          # (in from the street's eave, in from the hip's)
    t = np.clip(1.0 - np.hypot(u, v) / 0.75, 0, 1) ** 1.3                 # (the soft light, from the corner)
    hipd = u - v
    zk = ze - 0.12 - np.round((ze - 0.12 - zso) / K_RAFT) * K_RAFT
    xk = E['X'] + 0.12 + np.round((xso - E['X'] - 0.12) / K_RAFT) * K_RAFT
    raft = ((hipd < 0) & (np.abs(zso - zk) < 0.024)) | ((hipd >= 0) & (np.abs(xso - xk) < 0.024))
    hip = np.abs(hipd) < 0.03
    lo_, hi_ = np.array(SOFFIT_K, float), np.array(BEAM_K[1], float)
    rgb = lo_ + (hi_ - lo_) * (0.55 * t)[..., None]
    rgb = np.where((raft | hip)[..., None], lo_ * 0.6 + (np.array(N[3], float) - lo_ * 0.6) * (0.25 + 0.75 * t)[..., None], rgb)
    H.put(zso, oks, rgb, SOFF)
    # his front wall (the painter's): in front of what lies behind its far corner
    zw = E['xw'] / dx; yw = EYE + zw * dy
    H.put(zw, (zw >= E['zn']) & (zw <= E['zf']) & (yw <= E['yso']), np.zeros(3), WALL)
    # the rain head under the hip's gutter at the wall's corner, a short neck down to the painter's pipe on that corner
    pipe(H, dx, dy, par, KP, (E['xg'], E['ys']), zgf, xbox=K_HEAD)


def dojo(H, dx, dy, par):
    E = D
    ze = E['ze']
    zg, okg, ang = front(H, E, dx, dy, par, 0.0, ze, 0.0)
    # the dusk on its gutter's rim (the painter's pink), marked
    rim = (H.kind == GUT) & (H.z == zg) & (ang < 26)
    H.rgb[rim] = np.where((ang[rim] < 12)[:, None], np.array(DUSK[2], float), np.array(DUSK[1], float)); H.sun[rim] = 1.0
    # the soffit: from the gutter back to the wall (the beam along it), to the eave's end; past the house's corner
    # (right of the post) the overhang's soffit runs on behind it to the end edge
    zs_ = (E['ys'] - EYE) / dy; xs_ = zs_ * dx
    post = VP[0] - F * dx <= D_CORNER + 10
    ok = (xs_ >= E['xg']) & (zs_ <= ze) & ((xs_ <= E['xw']) | ~post)
    rgb = np.where(((xs_ >= E['xw'] - D_BEAM) & (xs_ <= E['xw']))[..., None], np.array(BEAM_D, float), np.array(SOFFIT_D, float))
    H.put(zs_, ok, rgb, SOFF)
    H.under[:] = (zs_ <= ze) & (xs_ > E['xw']) & post                    # (past the wall: the painter's wall and post)


def dojo_pipe(H, dx, dy, par):
    """The dojo's gutter into the downpipe the two houses share: its box under the gutter's end, its swan neck."""
    pipe(H, dx, dy, par, DP, (D['xg'], D['ys']), D['ze'] - 0.06)


def render(x0, y0, x1, y1, which):
    """The model over the box: per pixel its colour, the share of its rays meeting the eave, its kind, the share
    passing under it and over it, its dusk mark. which: 'K' Kirua's roof, 'D' or 'P' the dojo's; the dojo's downpipe
    with each (its swan neck passes in front of Kirua's near corner)."""
    w, h = x1 - x0, y1 - y0
    o = (np.arange(SS) + 0.5) / SS
    xs = np.broadcast_to(np.arange(x0, x1)[None, :, None, None] + o[None, None, None, :], (h, w, SS, SS))
    ys = np.broadcast_to(np.arange(y0, y1)[:, None, None, None] + o[None, None, :, None], (h, w, SS, SS))
    par = np.broadcast_to((np.arange(x0, x1)[None, :] + np.arange(y0, y1)[:, None])[..., None, None], (h, w, SS, SS))
    dx, dy = rays(xs, ys)
    Hh = Hit(dx.shape)
    with np.errstate(invalid='ignore', divide='ignore'):                # (rays that meet nothing: inf depths)
        (kirua if which == 'K' else dojo)(Hh, dx, dy, par)
        dojo_pipe(Hh, dx, dy, par)
    c = SS // 2
    hit = np.isfinite(Hh.z)
    rgb = Hh.rgb[:, :, c, c].copy(); kind = Hh.kind[:, :, c, c].copy(); sun = Hh.sun[:, :, c, c].copy()
    miss = ~hit[:, :, c, c] & hit.any((2, 3))                           # (its middle ray missed: the first that hit)
    if miss.any():
        first = hit.reshape(h, w, -1).argmax(-1); iy, ix = np.nonzero(miss)
        rgb[iy, ix] = Hh.rgb.reshape(h, w, -1, 3)[iy, ix, first[iy, ix]]
        kind[iy, ix] = Hh.kind.reshape(h, w, -1)[iy, ix, first[iy, ix]]; sun[iy, ix] = Hh.sun.reshape(h, w, -1)[iy, ix, first[iy, ix]]
    return dict(rgb=rgb, cov=hit.mean((2, 3)), kind=kind, sun=sun,
                under=(Hh.under & ~hit).mean((2, 3)), over=(Hh.over & ~hit).mean((2, 3)))


def bend_row(P):
    """The screen row of a downpipe's lower bend (from there down, the painter's pipe)."""
    return VP[1] - F * (P['top'] - EYE) / P['z']


def draw_layers(city, unlit, box, which, sunb=None):
    """One zone ('K' Kirua's roof, 'D' the dojo's eave, 'P' the dojo's pipe by its corner) drawn into the layers
    (whole-scene float RGBA, changed in place) inside box; returns what changed (over box) and the street_sun marks to
    lay there (-1 where unchanged). sunb: street_sun as it was over the box (the pipes' own marks)."""
    x0, y0, x1, y1 = box
    R = render(x0, y0, x1, y1, which)
    O = city[y0:y1, x0:x1].copy(); U = unlit[y0:y1, x0:x1].copy()
    new = O.copy(); h, w = O.shape[:2]
    sunb = np.zeros((h, w)) if sunb is None else sunb
    X = np.broadcast_to(np.arange(x0, x1)[None, :], (h, w)); Y = np.broadcast_to(np.arange(y0, y1)[:, None], (h, w))
    mine = (X >= K_X0) if which == 'K' else ((X >= D_X0) & (Y < D_Y1)) if which == 'D' else np.ones((h, w), bool)
    cov, rgb = R['cov'].copy(), R['rgb'].copy(); kind = R['kind']; sun = R['sun'].copy()
    # the gutter's rolled rim: its first pixel in each column, lit (the dusk's on the dojo's, already); the hips' in the
    # shade a step darker
    g = (kind == GUT) | (kind == HANGER)
    bead = (kind == GUT) & ~np.vstack([np.zeros((1, w), bool), g[:-1]]) & (R['sun'] == 0)
    if which == 'K':
        street = (X >= K['x_corner'] - 1) & (Y < VP[1] - 1.085 * (VP[0] - X - 0.5))
        rgb[bead] = np.where(street[bead][:, None], np.array(N[8], float), np.array(N[6], float))
    hit = mine & (cov > 0)
    wallh = hit & (kind == WALL)                                         # (his front wall: the painter's)
    if which == 'K': hit &= ~((kind == SOFF) & (X < K_CORNER_X)) & ~wallh   # (his front's soffit too)
    # the downpipes: from the lower bend, the painter's own pipe, column for column (its colours and marks)
    for P in (KP, DP):
        vp = hit & (kind == P['vk'])
        inside = vp & (X >= P['cols'][0]) & (X <= P['cols'][1]) & (P['ref'] >= y0) & (P['ref'] < y1)
        hit &= ~(vp & ~inside)
        if inside.any():
            xi = X[inside] - x0; ri = P['ref'] - y0
            rgb[inside] = O[ri, xi, :3]; sun[inside] = sunb[ri, xi] / 255.0; cov[inside] = 1.0
    # what the eave covers: its colour; against the sky its share of the rays as alpha (over the painter's soffit: opaque)
    a = np.where((R['under'] > 0) | (cov >= 0.999), 255.0, np.round(255 * cov))
    new[hit, :3] = rgb[hit]; new[hit, 3] = a[hit]
    # every ray over the roof: the sky (what the painter's band had above the new edge goes)
    new[mine & ~hit & (R['over'] > 0) & (R['under'] == 0)] = 0
    if which in ('D', 'P'):
        if which == 'D':                              # (past the eave's end, over or under: the sky)
            new[mine & ~hit & (R['under'] == 0) & (X > D_CORNER + 10)] = 0
        # the old pipe's stub over the new lower bend: the corner's shadow beside it, row by row
        stub = mine & ~hit & (X >= DP['cols'][0]) & (X <= DP['cols'][1]) & (Y < bend_row(DP)) & \
            (Y >= VP[1] - 1.040 * (VP[0] - X))
        if stub.any():
            dark = np.median(O[:, 133 - x0:136 - x0, :3], 1)
            new[stub, :3] = np.broadcast_to(dark[:, None, :], (h, w, 3))[stub]; new[stub, 3] = 255
    if which == 'K':                                  # under the eave, where the painter's band ran: his soffit
        under = mine & ~hit & (R['under'] > 0)
        top = np.array([(np.nonzero(O[:, xi, 3] > 0)[0].min() + y0) if (O[:, xi, 3] > 0).any() else 10 ** 6 for xi in range(w)])
        xr = np.arange(x0, x1)
        old = (Y >= np.minimum(top, K_SIDE[0])[None, :]) & (Y <= np.where(xr < K['x_corner'], K_SIDE[1] - 1, top + 16)[None, :])
        navy = O[..., 2] >= O[..., 0]                    # (his band, soffit and beam are navy; his front's boards red)
        sof = under & old & navy & (X < K_CORNER_X)
        new[sof, :3] = SOFFIT_K; new[sof, 3] = 255
        corner = mine & ~hit & (R['under'] > 0) & navy & (X >= 158) & (X < K['x_corner'] + 6) & (Y >= K_SIDE[0]) & \
            (Y < VP[1] - 0.983 * (VP[0] - X - 0.5) - 0.5)                   # (under the corner, to his front's top: soffit)
        new[corner, :3] = SOFFIT_K; new[corner, 3] = 255
        # past the far corner the model is all: what it does not meet is the sky (the old box and the pipe's top gone)
        wall = VP[1] - 0.983 * (VP[0] - X - 0.5)
        past = mine & ~hit & ~wallh & ((X > K_CORNER_X) | ((X == K_CORNER_X) & (Y < wall)))
        new[past] = 0
        # the beam under the soffit, on its ray: the painter's tones across it, clean along it; his soft edges, soffit
        sr = (VP[1] - (Y + 0.5)) / (VP[0] - (X + 0.5)); s0, s1, bx0, bx1 = K_BEAM
        span = mine & ~hit & (X >= bx0) & (X <= bx1)
        on = span & (sr >= s0) & (sr <= s1)
        u = np.clip(((sr - s0) / (s1 - s0) * len(BEAM_K)).astype(int), 0, len(BEAM_K) - 1)
        new[on, :3] = np.array(BEAM_K, float)[u[on]]; new[on, 3] = 255
        rim = span & ~on & (sr >= s0 - 0.006) & (sr <= s1 + 0.006)
        new[rim, :3] = SOFFIT_K; new[rim, 3] = 255
    ch = np.abs(new - O).max(-1) > 0
    un = U.copy(); un[ch] = new[ch]                    # (the power cut: the same, the painter's being the lit layer there)
    city[y0:y1, x0:x1] = new; unlit[y0:y1, x0:x1] = un
    marks = np.where(ch & hit, np.round(255 * sun), np.where(ch, 0, -1))
    return ch, marks


# the zones' boxes (their names as in tools/redraw_zones.py): Kirua's eave in boxes along its slope (each down to the
# soffit's rows it cleans, not into his front's boards), its near corner, its far end with the box and swan neck; the
# dojo's eave's end, and its downpipe by its corner
BOXES = {'eaveKs': (141, 50, 206, 102), 'eaveK1': (206, 56, 236, 136), 'eaveK2': (236, 90, 266, 167),
         'eaveK3': (266, 123, 296, 198), 'eaveK4': (296, 157, 322, 225), 'eaveK5': (322, 186, 374, 290),
         'eaveD': (100, 0, 190, 50), 'eaveP': (128, 50, 141, 84)}
MODE = lambda name: {'eaveD': 'D', 'eaveP': 'P'}.get(name, 'K')


def draw(city, unlit, box):
    """The zone (tools/redraw_zones.py): the eave whose box this is, drawn into both layers; in street_sun its marks
    (the dojo's dusk rim and both pipes' as the painter had them, the rest of what changed none), in night_far the
    street's 0 where it changed (two of the dojo's old tile pixels were marked sky there), each from the zone's before
    copy in tools/src/edits/."""
    name = next(n for n, b in BOXES.items() if tuple(b) == tuple(box))
    sunb = load(os.path.join(EDITS, f'{name}_before_sun.webp'), 'RGB')[..., 0]
    ch, sun = draw_layers(city, unlit, box, MODE(name), sunb)
    x0, y0, x1, y1 = box
    for f, tag, val in (('street_sun.webp', 'sun', sun), ('night_far.webp', 'nf', np.where(ch, 0, -1))):
        src = os.path.join(EDITS, f'{name}_before_{tag}.webp')
        if not os.path.exists(src): continue
        p = os.path.join(ROOT, 'assets', f)
        S0 = np.array(Image.open(p).convert('RGB')); S = S0.copy()
        S[y0:y1, x0:x1] = np.array(Image.open(src).convert('RGB'))
        sub = S[y0:y1, x0:x1]; m = val >= 0
        sub[m] = np.clip(val[m], 0, 255).astype(np.uint8)[:, None]
        if not np.array_equal(S, S0):
            Image.fromarray(S, 'RGB').save(p, 'WEBP', lossless=True, quality=100, method=6, exact=True)
    return ch


def load(p, mode='RGBA'):
    return np.asarray(Image.open(p).convert(mode)).astype(float)


def preview(out):
    os.makedirs(out, exist_ok=True)
    A = os.path.join(ROOT, 'assets')
    city = load(os.path.join(A, 'layer_city_off.webp')); unlit = load(os.path.join(A, 'street_unlit.webp'))
    for n, (x0, y0, x1, y1) in BOXES.items():                        # (the painter's, as the zones start from)
        city[y0:y1, x0:x1] = load(os.path.join(EDITS, f'{n}_before_city.webp'))
        unlit[y0:y1, x0:x1] = load(os.path.join(EDITS, f'{n}_before_unlit.webp'))
    c0 = city.copy()
    for n, b in BOXES.items():
        draw_layers(city, unlit, b, MODE(n), load(os.path.join(EDITS, f'{n}_before_sun.webp'), 'RGB')[..., 0])
    for tag, arr in (('before', c0), ('after', city)):
        bg = np.zeros(arr.shape[:2] + (3,)); bg[:] = (60, 44, 92)
        comp = bg * (1 - arr[..., 3:4] / 255) + arr[..., :3] * arr[..., 3:4] / 255
        im = Image.fromarray(np.clip(comp, 0, 255).astype(np.uint8))
        im.crop((0, 0, 420, 320)).save(os.path.join(out, f'{tag}_1x.png'))
        for nm, b, s in (('all', (96, 0, 380, 300), 4), ('end', (280, 160, 380, 300), 8), ('corner', (126, 20, 236, 120), 8),
                         ('dojo', (96, 0, 196, 90), 8)):
            im.crop(b).resize(((b[2] - b[0]) * s, (b[3] - b[1]) * s), Image.NEAREST).save(os.path.join(out, f'{tag}_{nm}.png'))
        g = Image.fromarray(np.clip(255 * (comp / 255) ** 0.55, 0, 255).astype(np.uint8))
        g.crop((96, 0, 380, 300)).resize((284 * 4, 300 * 4), Image.NEAREST).save(os.path.join(out, f'{tag}_bright.png'))


if __name__ == '__main__':
    if '--preview' in sys.argv: preview(sys.argv[sys.argv.index('--preview') + 1])
