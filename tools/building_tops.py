#!/usr/bin/env python3
"""The tops of the buildings, each its real parts (the owner, 2026-11-14: "faut penser le haut comme un vrai haut
d'immeuble avec détail, pas juste un rectangle", "pareil pour les autres toits").

    (a module: tools/redraw_zones.py's zones topB, topC, topPC, topEnd, topOden and topOdenShop call draw(city, unlit,
     box) on the street as the zones before them leave it, the box telling which top; each also sets
     assets/night_far.webp to the street's (0) where it changed a pixel)
    python3 tools/building_tops.py --preview OUT [ZONE]   the layers as they are, each top drawn again (nothing written
                                                          in assets/), x6 crops with the model's lines in OUT

Each top is modelled in the street's camera (tools/arcade_eave.py, tools/r6_sprites.py: the eye 1.41 m up on the street's
axis, f 959.5 px, VP (700, 615); a point X m right of the axis, Y m up, Z m ahead is seen at x = 700 + f X / Z,
y = 615 - f (Y - 1.41) / Z; a line along the street keeps v = (615 - y) / (x - 700)) and drawn on the pixel grid from it:
each pixel's centre (or 4 x 4 rays in it, on the silhouettes) followed into the model, its part and its face giving its
tone. Tones are the painter's (sampled on the walls and edges round each top), lit edges soft (the sky's light on a
rounded nose, a step over the face, never a bright stripe), a faint grain of the painter's (the plaster's noise); the
power cut (street_unlit) takes the same picture times the painter's darkening there, smoothed (about 1 on the tops: no
street light reaches them). Where a top's outline changes, the layer's alpha follows (the sky is a layer of its own:
where it shows, the street is transparent; the far layers, the cherry behind B and the end house, show as they are).
What stands in front is laid back over the new top as it was drawn (R24): the street lamp's arm and bracket over B
(tools/pole_lamp.py's own coverage), the pole (street.js COCC), the Pokemon Center's ball, the trees.
"""
import os
import sys
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
H, W = 816, 1456
VP = (700.0, 615.0)
F = 959.5
EYE = 1.41
SS = 4                                           # rays a pixel each way on the silhouettes
LUMA = np.array([0.299, 0.587, 0.114])
YY, XX = np.mgrid[0:H, 0:W]
with np.errstate(divide='ignore', invalid='ignore'):
    V = (VP[1] - (YY + 0.5)) / (XX + 0.5 - VP[0])   # each pixel's ray (right facades)


def ray_y(x, v):
    """The row (continuous: a pixel's centre at row + 0.5) of the ray v at column x (its centre)."""
    return VP[1] - v * (np.asarray(x, float) + 0.5 - VP[0])


def proj(X, Y, Z):
    """A point of the model on the screen (continuous)."""
    return VP[0] + F * X / Z, VP[1] - F * (Y - EYE) / Z


def depth_at(x, X):
    """The depth Z (m) of a line along the street at X (m right of the axis) seen at column x (its centre)."""
    return F * X / (np.asarray(x, float) + 0.5 - VP[0])


def x_at(Z, X):
    """The column (continuous) where a line along the street at X is at depth Z."""
    return VP[0] + F * X / Z


def noise(seed, sigma=(1.5, 2.5)):
    """The plaster's grain (tools/zone5_facades.py's plaster: a smoothed field, unit deviation), whole scene."""
    rng = np.random.default_rng(seed)
    n = gaussian_filter(rng.standard_normal((H, W)), sigma)
    return n / n.std()


def med(img, m):
    return np.median(img[m][:, :3], 0)


def darkening(city, unlit, m, sigma=4.0):
    """The painter's power cut over the mask's surroundings: unlit over lit, smoothed, per channel (whole scene)."""
    w = (city[..., 3] > 200).astype(float)
    r = np.stack([gaussian_filter(((unlit[..., c] + 1) / (city[..., c] + 1)) * w, sigma) for c in range(3)], -1)
    return np.clip(r / np.maximum(gaussian_filter(w, sigma), 1e-6)[..., None], 0, 1.2)


def lay(city, unlit, new, cov, m, ratio=None):
    """new (RGB, whole scene) laid on both layers where m, with coverage cov (0..1) over what is there (the alpha
    follows: over the sky, the new pixel's own coverage); the power cut the same picture times ratio."""
    for arr, k in ((city, None), (unlit, ratio)):
        col = new if k is None else np.clip((new + 1) * k - 1, 0, 255)
        a0 = arr[..., 3:] / 255.0; c = cov[..., None]
        prem = arr[..., :3] * a0 * (1 - c) + col * c
        na = c + a0 * (1 - c)
        out = prem / np.maximum(na, 1e-6)
        arr[..., :3][m] = out[m]; arr[..., 3][m] = (255 * na[..., 0])[m]


# ---------------------------------------------------------------------------------------------------------------------
# B: the apartment block behind the right pole (zone5's B, x 941..1022, its facade 5 m right of the street's axis, one
# plaster since 2026-11-13: redraw_zones.py's bwall). Its top was the painter's: a slanted cap 9 px deep over a black
# groove (a "boudin" along the edge), the cherry's blossoms painted on it, the downpipe run up into the cap.
# A three-storey RC block of the 1980s with a flat roof, as in Japan: a parapet 0.8 m over the roof slab (its foot the
# painter's cornice, v 1.372..1.414: the slab's edge and its drip), its top an aluminium coping (kasagi: its rounded
# front nose lit by the sky, its face, its drip lip, a crisp shadow under it), a joint cover every 1.8 m along it; the
# downpipe from a rain head under the cornice (the roof's scupper through the parapet over it), no longer up into the
# cap; and over the parapet the top of the stair penthouse (toya), set back 1 m, its own coping, its far corner plumb:
# from the street, 58 degrees up, only its top shows over the parapet (each pixel's ray followed past the parapet's edge),
# running on behind the pole. The cherry behind (the far layers, and the painter's blossoms over the cap, graded as the
# tree by night_far) stays where nothing of the building stands in front of it.
B = dict(
    XF=5.0, x0=942, x1=1022,                     # its facade (m right of the axis), its columns (941: its lit arris, kept)
    vT=1.6085, vcap=1.5765, vcor=1.414,          # its parapet's top, zone5's cap's foot, the cornice's top
    cop=0.09, nose=0.022, drip=0.016, shad=0.03, # the coping's face (m), its nose, its drip lip, its shadow under it
    joint=1.8, z_far=19.9,                       # a joint cover every 1.8 m from the far end (x 941)
    pent=dict(X=6.0, D=2.8, z=(16.0, 19.6), top=11.45, cop=0.08),   # the penthouse: front X, depth, Z span, top Y, coping
    pipe=(943, 947), head=(0.20, 0.016),         # the downpipe's columns (its clamps' column included), the rain head:
)                                                # its height (m), its top under the cornice (in v)


def b_parts(O):
    """B's tones from the street as it is (the plaster of the parapet's face, the cornice's lit top and its face, the
    cap's metal): the coping's nose, face and drip, the shadow factor, the plaster."""
    b = B; xs = (XX >= 950) & (XX <= 1018)
    plaster = med(O, xs & (V > 1.43) & (V < 1.55) & (O[..., 3] > 250) & (O[..., :3] @ LUMA < 45))
    cap = med(O, xs & (V > 1.590) & (V < 1.606) & (O[..., 3] > 250) & (O[..., :3] @ LUMA < 60) & (O[..., :3] @ LUMA > 20))
    lit = med(O, xs & (V > 1.406) & (V < 1.4125) & (O[..., 3] > 250) & (O[..., :3] @ LUMA > 30))
    return dict(plaster=plaster, face=0.5 * (cap + plaster * 1.25), nose=0.65 * lit + 0.35 * cap * 1.3,
                drip=plaster * 0.55, under=plaster * 0.6)


def lamp_cover(on):
    """The street lamp's arm and bracket as tools/pole_lamp.py draws them: coverage and colour, whole scene."""
    import pole_lamp as PL
    cov = np.zeros((H, W)); col = np.zeros((H, W, 3)); x0, y0, x1, y1 = PL.BOX
    for c, k in (PL.render_arm(PL.BOX, on), PL.render_straps(PL.BOX, on)):
        m = c > 0; sub = cov[y0:y1, x0:x1]; sc = col[y0:y1, x0:x1]
        sub[m] = c[m]; sc[m] = k[m]
    return cov, col


def pole_mask(js=None):
    import json, re
    s = open(js or os.path.join(ROOT, 'assets', 'street.js'), encoding='utf-8').read()
    m = np.zeros((H, W), bool)
    for a, b_, c, d in json.loads(re.search(r'const COCC = (\{.*?\});', s).group(1))['pole']['runs']:
        m[a:b_ + 1, c:d + 1] = True
    return m


def top_b(city, unlit, box, lines=None):
    b = B; x0, y0, x1, y1 = box
    O = city.copy(); T = b_parts(O)
    zone = np.zeros((H, W), bool); zone[y0:y1, x0:x1] = True
    cols = (XX >= b['x0']) & (XX <= b['x1'])
    pole = pole_mask()
    n = noise(11); tex = (1 + 0.03 * n)[..., None]
    new = O[..., :3].copy(); cov = np.zeros((H, W)); ch = np.zeros((H, W), bool)
    XF = b['XF']; YT = EYE + XF * b['vT']
    v_face = (YT - b['cop'] - EYE) / XF                       # the coping's foot
    v_nose = (YT - b['nose'] - EYE) / XF
    v_drip = (YT - b['cop'] + b['drip'] - EYE) / XF
    v_shad = (YT - b['cop'] - b['shad'] - EYE) / XF
    # 1. the parapet's face up to the coping: where zone5's cap and its black groove were, the plaster carried up each
    # column from under them (its light: the median of the rows just under the old cap, its grain the plaster's)
    for x in range(b['x0'], b['x1'] + 1):
        ya, yb = int(np.floor(ray_y(x, b['vT']))), int(np.ceil(ray_y(x, b['vcap']))) + 1
        src = [y for y in range(yb, yb + 6) if O[y, x, 3] > 250]
        base = np.median(O[src, x, :3], 0) if src else T['plaster']
        for y in range(ya, yb):
            new[y, x] = base * tex[y, x]; cov[y, x] = 1; ch[y, x] = True
    o = (np.arange(SS) + 0.5) / SS
    # 2. the stair penthouse over the parapet: each pixel's rays past the parapet's edge onto its front face (X = pX):
    # its coping (nose, face, drip), its plaster, its far corner plumb; behind the parapet's coping (drawn after it)
    p = b['pent']; pX = p['X']; vt_p = (p['top'] - EYE) / pX; vc_p = (p['top'] - p['cop'] - EYE) / pX
    vn_p = (p['top'] - 0.025 - EYE) / pX
    xa = x_at(p['z'][1], pX)                                  # its far corner (continuous column)
    for x in range(int(np.floor(xa)), b['x1'] + 1):
        for y in range(int(np.floor(ray_y(x, vt_p))) - 1, int(np.ceil(ray_y(x, b['vT']))) + 1):
            if pole[y, x]: continue
            tone = []
            for sy in o:
                for sx in o:
                    xc, yc = x + sx, y + sy
                    v = (VP[1] - yc) / (xc - VP[0])
                    if v <= b['vT'] or xc < xa or v > vt_p: continue
                    if v >= vn_p: tone.append(T['nose'])
                    elif v >= vc_p: tone.append(T['face'])
                    elif v >= vc_p - 0.005: tone.append(T['drip'])
                    else:                                       # its plaster, a shade darker by its far corner
                        k = 0.93 + 0.07 * min((xc - xa) / 6.0, 1.0)
                        tone.append(T['plaster'] * k * 1.03 * tex[y, x, 0])
            c = len(tone) / SS / SS
            if c < 0.2: continue
            new[y, x] = np.mean(tone, 0); cov[y, x] = 1.0 if c > 0.85 else c; ch[y, x] = True
    # 3. the parapet's coping over it: its nose lit by the sky (soft: a step over the face), its face, its drip lip, a
    # crisp shadow under it on the plaster; a joint cover every 1.8 m (a pixel wide: its edge a shade darker, its face
    # a shade lighter); over the penthouse or the sky behind, by its coverage
    zj = [b['z_far'] - b['joint'] * k for k in range(1, 6)]
    xj = [int(np.floor(x_at(z, XF) - 0.5)) for z in zj]
    for x in range(b['x0'], b['x1'] + 1):
        for y in range(int(np.floor(ray_y(x, b['vT']))) - 1, int(np.ceil(ray_y(x, v_shad))) + 1):
            if pole[y, x]: continue
            vt, vb = (VP[1] - y) / (x + 0.5 - VP[0]), (VP[1] - y - 1) / (x + 0.5 - VP[0])
            c = float(np.clip((b['vT'] - vb) / max(vt - vb, 1e-9), 0, 1))
            if c < 0.2: continue
            c = 1.0 if c > 0.85 else c
            v = min((vt + vb) / 2, b['vT'])
            if v >= v_nose: t = T['nose']
            elif v >= v_drip: t = T['face'] * tex[y, x, 0]
            elif v >= v_face: t = T['drip']
            elif v >= v_shad: t = new[y, x] * 0.62
            else: continue
            if x in xj and v >= v_drip: t = t * 0.84
            if x - 1 in xj and v >= v_drip and v < v_nose: t = t * 1.07
            if c < 1 and cov[y, x] > 0 and ch[y, x] and V[y, x] > b['vT'] - 0.01:     # (the penthouse behind its edge)
                new[y, x] = t * c + new[y, x] * (1 - c); cov[y, x] = max(cov[y, x], c)
            else:
                new[y, x] = t; cov[y, x] = c if O[y, x, 3] < 250 else 1.0
            ch[y, x] = True
    # 4. the rain head: the downpipe stops in it under the cornice (a pixel wider each side, its top rim lit, its lit
    # side, its face, its dark side, its foot narrowing to the pipe); over it, up to the coping, the parapet and the
    # cornice where the pipe was (from the columns right of it, on their rays)
    pa, pb = b['pipe']
    Zr = depth_at((pa + pb) / 2, XF); rh_px = b['head'][0] * F / Zr
    y_rh = int(np.ceil(ray_y((pa + pb) / 2, b['vcor'] - 0.042))) + 1          # (under the cornice's dark underside)
    for x in range(pa, pb + 1):
        ytop = int(np.floor(ray_y(x, b['vcap'])))
        for y in range(ytop, y_rh):
            if O[y, x, 3] < 250: continue
            v = V[y, x]; xs_ = x + 5 + (pb - x)
            ys_ = int(np.round(ray_y(xs_, v) - 0.5))
            new[y, x] = new[ys_, xs_] if ch[ys_, xs_] else O[ys_, xs_, :3]; cov[y, x] = 1; ch[y, x] = True
    pl = O[y_rh + 20, pa + 1, :3]; pm = O[y_rh + 20, pa + 2, :3]; pd = O[y_rh + 20, pa + 3, :3]   # (the pipe's lit side,
    hy0, hy1 = y_rh, y_rh + int(round(rh_px))                                                    # its face, its dark side)
    for y in range(hy0, hy1 + 1):
        foot = (y - hy0) >= (hy1 - hy0) - 1
        for x in range(pa, pb + 1):
            if foot and x in (pa, pb): continue
            t = [pl * 0.8, pl, pm, pm * 0.7, pd][x - pa]
            if y == hy0 and x < pb: t = pl * 0.95
            new[y, x] = t; cov[y, x] = 1; ch[y, x] = True
    ch &= zone & cols
    ratio = darkening(city, unlit, ch)
    lay(city, unlit, new, cov, ch, ratio)
    # 5. what stands in front laid back: the lamp's arm and its bracket, as tools/pole_lamp.py draws them
    for arr, on in ((city, True), (unlit, False)):
        lc, lcol = lamp_cover(on); m = (lc > 0) & ch
        if m.any(): lay(arr, arr, lcol, lc, m)
    if lines is not None:
        lines += [('ray', b['x0'], b['x1'], b['vT']), ('ray', b['x0'], b['x1'], v_face), ('ray', b['x0'], b['x1'], b['vcor']),
                  ('ray', xa, b['x1'], vt_p)] + [('v', x, ray_y(x, b['vT']) - 3, ray_y(x, v_face) + 2) for x in xj]
    return ch


# ---------------------------------------------------------------------------------------------------------------------
# C: the tall narrow building between the pole and Ichiraku's (zone5's C, x 1066..1121, dark vertical planks). The
# painter ran its top level at y 66 over its whole front, the level top of its near side wall (the frontal face that
# shows over Naruto's roof right of x 1122) carried on over a facade that runs to the vanishing point: its own lines (the
# ledges, zone5's) all run on rays, and the highest of them, the lit ledge at v 1.30, meets the near corner exactly
# (1122, 66). That ledge is the roof's edge: the front's top runs on its ray, from the near corner down to the pole, and
# what the painter drew over it (a triangle of planks, up to the level top) is the sky. The edge itself, as the street's
# other parapets: the painter's ledge made a metal coping (its nose lit by the sky, soft; its face; its drip lip; its
# shadow on the planks under it, the painter's dark soffit row), a joint cover where the 1.8 m lengths meet. C is 12 m
# away: what could stand on its roof (a railing, an antenna, a tank) would be a metre a 75 px over a top 55 px wide, so
# nothing (R25); its near corner columns (1120, 1121) are the next agent's (Naruto's top): its top meets them on the ray.
C = dict(x0=1065, x1=1119, v_top=(VP[1] - 66.0) / (1122.0 - VP[0]), nose=0.0034, face=0.0170, drip=0.0200,
         shad=0.0265, joint=1.8, z_near=11.37, XF=5.0, v_soffit=1.2485, v_plank=(1.205, 1.244))


def top_c(city, unlit, box, lines=None):
    c_ = C; x0, y0, x1, y1 = box
    O = city.copy()
    zone = np.zeros((H, W), bool); zone[y0:y1, x0:x1] = True
    cols = (XX >= c_['x0']) & (XX <= c_['x1'])
    pole = pole_mask()
    vT = c_['v_top']
    xs_ = (XX >= 1070) & (XX <= 1115) & (O[..., 3] > 250)
    # the painter's ledge: its lit top row (each column's brightest pixel in its top rows), its face
    lits, faces = [], []
    for x in range(1070, 1116):
        ya, yb = int(np.floor(ray_y(x, 1.3015))), int(np.ceil(ray_y(x, 1.290)))
        k = ya + int(np.argmax(O[ya:yb, x, :3] @ LUMA)); lits.append(O[k, x, :3])
        faces.append(np.median(O[k + 2:int(np.floor(ray_y(x, 1.266))), x, :3], 0))
    lit = np.median(np.array(lits), 0); face = np.median(np.array(faces), 0)
    n = noise(23); tex = (1 + 0.025 * n)[..., None]
    new = O[..., :3].copy(); cov = np.zeros((H, W)); ch = np.zeros((H, W), bool)
    xj = [int(np.floor(x_at(c_['z_near'] + c_['joint'] * (k + 0.5), c_['XF']) - 0.5)) for k in range(3)]
    v_nose, v_face, v_drip, v_shad = vT - c_['nose'], vT - c_['face'], vT - c_['drip'], vT - c_['shad']
    for x in range(c_['x0'], c_['x1'] + 1):
        # the planks run up to the coping: each column's own planks from under the old ledge, carried up a board's height
        pa, pb = int(np.ceil(ray_y(x, c_['v_plank'][1]))), int(np.floor(ray_y(x, c_['v_plank'][0])))
        for y in range(max(y0, 0), int(np.ceil(ray_y(x, c_['v_soffit']))) + 1):
            if pole[y, x]: continue
            vt, vb = (VP[1] - y) / (x + 0.5 - VP[0]), (VP[1] - y - 1) / (x + 0.5 - VP[0])
            cv = np.clip((vT - vb) / max(vt - vb, 1e-9), 0, 1)        # (the edge's coverage of the pixel)
            v = min((vt + vb) / 2, vT - 1e-6)
            if cv < 0.2:                                               # the sky over the edge
                if O[y, x, 3] > 0: cov[y, x] = 0; ch[y, x] = True; new[y, x] = O[y, x, :3]
                continue
            plank = O[pa + (y - pa) % max(pb - pa, 1), x, :3]
            if v >= v_nose: t = lit
            elif v >= v_face: t = face * 1.06 * tex[y, x, 0]
            elif v >= v_drip: t = face * 0.66
            elif v >= v_shad: t = plank * 0.75
            else: t = plank
            if x in xj and v < v_nose and v >= v_face: t = t * 0.8
            if x - 1 in xj and v < v_nose and v >= v_face: t = t * 1.08
            new[y, x] = t; cov[y, x] = 1.0 if cv > 0.85 else cv; ch[y, x] = True
    ch &= zone & cols & ~pole
    ratio = darkening(city, unlit, ch)
    clear = ch & (cov == 0)
    lay(city, unlit, new, cov, ch & ~clear, ratio)
    for arr in (city, unlit):
        arr[..., 3][clear] = 0
        arr[..., :3][clear] = 0
    if lines is not None:
        lines += [('ray', c_['x0'], c_['x1'], vT), ('ray', c_['x0'], c_['x1'], v_drip), ('ray', c_['x0'], c_['x1'], c_['v_soffit'])]
        lines += [('v', x, ray_y(x, vT) - 2, ray_y(x, v_drip) + 2) for x in xj if c_['x0'] <= x <= c_['x1']]
    return ch


# ---------------------------------------------------------------------------------------------------------------------
# The Pokemon Center (x ~850..907, its facade on the right side's rays, 23-26 m down the street): over its red sign band
# a lavender band 12 px deep (v 0.773..0.837: its parapet, clad white), the painter's lit row on top, all one flat
# fill. Its top as the parapets' of the street: a metal coping (the painter's lit row its nose, soft; its face; its drip
# lip; a shadow under it on the cladding), a joint cover every 1.8 m, the cladding's panel joints under the coping's
# ones, the shadow line over the red band as painted. From 25 m nothing on its roof shows over a parapet 5 m up (each
# ray past its edge goes over the roof). Only what shows between the ball (laid back: r 25.5 round 870.5, 470.5, the
# pokeball zone's circle) and x 904 (x 905..941 is the next agent's: the narrow building there is redone).
PC = dict(x0=884, x1=904, v_top=0.8372, nose=0.0052, face=0.0122, drip=0.0154, shad=0.0190, v_foot=0.7735,
          XF=5.0, joint=1.8, ball=(870.5, 470.5, 25.5))


def ball_mask():
    cx, cy, r = PC['ball']
    return np.hypot(XX + 0.5 - cx, YY + 0.5 - cy) < r


def top_pc(city, unlit, box, lines=None):
    p = PC; x0, y0, x1, y1 = box
    O = city.copy()
    zone = np.zeros((H, W), bool); zone[y0:y1, x0:x1] = True
    cols = (XX >= p['x0']) & (XX <= p['x1'])
    ball = ball_mask()
    band = cols & ~ball & (O[..., 3] > 250) & (V < p['v_top'] - 0.006) & (V > p['v_foot'] + 0.006)
    face = med(O, band)
    lits = []
    for x in range(p['x0'], p['x1'] + 1):
        ya, yb = int(np.floor(ray_y(x, p['v_top'] + 0.002))), int(np.ceil(ray_y(x, p['v_top'] - 0.012)))
        if ball[ya:yb, x].any(): continue
        lits.append(O[ya + int(np.argmax(O[ya:yb, x, :3] @ LUMA)), x, :3])
    lit = np.median(np.array(lits), 0)
    n = noise(31); tex = (1 + 0.02 * n)[..., None]
    new = O[..., :3].copy(); cov = np.zeros((H, W)); ch = np.zeros((H, W), bool)
    vT = p['v_top']; v_nose, v_face, v_drip, v_shad = vT - p['nose'], vT - p['face'], vT - p['drip'], vT - p['shad']
    zf = depth_at(p['x1'], p['XF'])
    xj = [int(np.floor(x_at(zf + p['joint'] * (k + 0.5), p['XF']) - 0.5)) for k in range(4)]
    for x in range(p['x0'], p['x1'] + 1):
        for y in range(int(np.floor(ray_y(x, vT))) - 1, int(np.ceil(ray_y(x, p['v_foot']))) + 1):
            if ball[y, x] or O[y, x, 3] < 1 and V[y, x] < vT: continue
            vt, vb = (VP[1] - y) / (x + 0.5 - VP[0]), (VP[1] - y - 1) / (x + 0.5 - VP[0])
            cv = np.clip((vT - vb) / max(vt - vb, 1e-9), 0, 1)
            if cv < 0.2: continue
            v = min((vt + vb) / 2, vT - 1e-6)
            if v < p['v_foot'] + 0.003: continue
            if v >= v_nose: t = 0.8 * lit + 0.2 * face
            elif v >= v_face: t = face * 1.03 * tex[y, x, 0]
            elif v >= v_drip: t = face * 0.78
            elif v >= v_shad: t = face * 0.86
            else: t = face * (0.97 + 0.03 * min((v_shad - v) / 0.02, 1)) * tex[y, x, 0]
            if x in xj and v < v_nose: t = t * (0.84 if v >= v_drip else 0.92)
            new[y, x] = t; cov[y, x] = 1.0 if cv > 0.85 else cv; ch[y, x] = True
    ch &= zone & cols & ~ball
    ratio = darkening(city, unlit, ch)
    lay(city, unlit, new, cov, ch, ratio)
    if lines is not None:
        lines += [('ray', p['x0'], p['x1'], vT), ('ray', p['x0'], p['x1'], v_drip), ('ray', p['x0'], p['x1'], p['v_foot'])]
        lines += [('v', x, ray_y(x, vT) - 2, ray_y(x, p['v_foot']) + 1) for x in xj if p['x0'] <= x <= p['x1']]
    return ch


# ---------------------------------------------------------------------------------------------------------------------
# The house at the street's end (tools/end_house.py: it faces the street, drawn face on): its roof a gable to the street,
# kawara tiles. From the street, far below its eaves, only its gable end shows: its two verges, the ridge's end between
# them, the eave's corner at the foot of each verge (the roof's slopes face up, away from the eye). The painter's verge
# was a band 13 px deep of tile-like mottle under a lit top row, a lump at the apex. Now, face on, its lines on the
# painter's slope (0.55: his verge's top, fitted; the right verge its mirror about the apex, x 832.5):
# - the verge tiles' roll (sode-gawara) along the top: its round top lit by the sky (soft, the painter's lit row), its
#   middle, its underside, the roll's shadow under it; a tile joint every 5 px (0.28 m, a tile's course along the slope:
#   the tiles' rows, seen at the verge), the overlapping tile's end a notch;
# - the barge board (hafu-ita) under it: a plain dark board (the painter's band's own tone, evened), its lower arris
#   lit from the street (his light line), its shadow on the gable wall;
# - at the apex the ridge's end: the onigawara (an arched plaque, its rim lit as the rolls are, its face darker, the
#   boss in its middle) on the stack of ridge tiles, whose ends step out over the two verges;
# - at the foot of the left verge the eave's corner: the round end tile of the eave's first course, and under it the end
#   of the half-round gutter along the left eave (its end cap, its rim lit), the right one behind the ball.
END = dict(xc=832.5, slope=0.55, y822=447.9, roll=3, board=8, joint=5.0, x0=755, x1=852,
           oni=dict(cx=832.5, top=437.0, w=14.0, h=10.5), corner=757.0)


def top_end(city, unlit, box, lines=None):
    e = END; x0, y0, x1, y1 = box
    O = city.copy()
    zone = np.zeros((H, W), bool); zone[y0:y1, x0:x1] = True
    ball = ball_mask()
    near_ball = np.hypot(XX + 0.5 - PC['ball'][0], YY + 0.5 - PC['ball'][1]) < PC['ball'][2] + 2.5
    xc, s = e['xc'], e['slope']
    def ytop(xf):                                   # the verge's top line (continuous x), both sides
        u = np.where(xf <= xc, xf, 2 * xc - xf)
        return e['y822'] + s * (822.5 - u)
    # the painter's tones along the left verge (its rows under the top line), the wall under the band
    rows = {k: [] for k in range(16)}
    for x in range(765, 818):
        t = ytop(x + 0.5)
        for k in range(16):
            y = int(np.floor(t)) + k
            if O[y, x, 3] > 250: rows[k].append(O[y, x, :3])
    R = {k: np.median(np.array(v), 0) for k, v in rows.items() if v}
    lumk = {k: float(R[k] @ LUMA) for k in R}
    k_lit = max(range(0, 4), key=lambda k: lumk.get(k, 0))
    lit, mid, low = R[k_lit], R[k_lit + 1], R[k_lit + 2]
    board = np.median(np.array([R[k] for k in range(k_lit + 3, k_lit + 11)]), 0)
    arris = R[max(range(k_lit + 9, k_lit + 14), key=lambda k: lumk[k])]
    wall = R[15]
    n = noise(41, (1.0, 1.0)); tex = (1 + 0.04 * n)[..., None]
    new = O[..., :3].copy(); cov = np.zeros((H, W)); ch = np.zeros((H, W), bool)
    rl, bd = e['roll'], e['board']
    o = (np.arange(SS) + 0.5) / SS
    oni = e['oni']
    def in_oni(xf, yf):                             # the onigawara on the ridge's end: a bell, narrow at its rounded top,
        dx = abs(xf - oni['cx']); r = oni['w'] / 2      # stepping out to the stack at its foot (the painter's lump, evened)
        k = (yf - oni['top']) / oni['h']
        if k < 0 or k > 1: return False
        half = r * (0.40 + 0.60 * k ** 0.8)
        if k < 0.14: half *= np.sqrt(k / 0.14)
        return dx <= half
    def role(xf, yf):
        if in_oni(xf, yf):
            inner = in_oni(xf, yf - 1.0) and in_oni(xf - 1.0, yf) and in_oni(xf + 1.0, yf)
            if not inner: return 'oni_rim' if not in_oni(xf, yf - 1.0) else 'oni_side'
            return 'oni_face'
        d = yf - ytop(xf)
        if d < 0: return None
        # the ridge tiles' stack under the plaque: its ends step out over the verges
        if abs(xf - xc) < oni['w'] / 2 + 3 and yf < oni['top'] + oni['h'] + 2.5 and yf >= oni['top'] + oni['h'] - 1:
            return 'stack_lit' if (yf - (oni['top'] + oni['h'] - 1)) < 1.2 else 'stack'
        if d < 1: return 'lit'
        if d < 2: return 'mid'
        if d < rl: return 'low'
        if d < rl + 1: return 'rshadow'
        if d < rl + 1 + bd - 1: return 'board'
        if d < rl + 1 + bd: return 'arris'
        if d < rl + 2 + bd: return 'wshadow'
        return 'wall'
    tone = dict(lit=0.85 * lit + 0.15 * mid, mid=mid, low=low, rshadow=board * 0.62, board=board, arris=arris,
                wshadow=wall * 0.75, oni_rim=0.45 * lit + 0.55 * mid, oni_side=0.5 * low + 0.5 * board,
                oni_face=0.15 * mid + 0.85 * board * 0.92, stack_lit=mid, stack=low * 0.9)
    for x in range(max(x0, e['x0']), min(x1, e['x1'] + 1)):
        for y in range(y0, y1):
            if ball[y, x]: continue
            got = []; cols_ = []
            u = abs(x + 0.5 - xc) - oni['w'] / 2 - 2.0
            for sy in o:
                for sx in o:
                    r = role(x + sx, y + sy)
                    if r is None: continue
                    got.append(r)
                    if r == 'wall': cols_.append(O[y, x, :3]); continue
                    t = tone[r]
                    if r == 'board': t = t * tex[y, x, 0] * (0.94 if (y + sy - ytop(x + sx)) < rl + 2 else 1.0)
                    # the tiles along the roll, one every e['joint'] px from the apex: each tile's upper end a little
                    # brighter (its back toward the sky), darker toward its lower end, which laps the next one: there a
                    # notch (the seam, in the lapping tile's shadow)
                    us = abs(x + sx - xc) - oni['w'] / 2 - 2.0
                    if r in ('mid', 'low', 'lit') and us > 0:
                        ph = (us % e['joint']) / e['joint']
                        if ph < 0.2: t = t * (0.8 if r == 'lit' else 0.62)
                        elif ph < 0.55: t = t * 1.1
                        else: t = t * (1.0 - 0.12 * (ph - 0.55) / 0.45)
                    cols_.append(t)
            c = len(got) / SS / SS
            if c < 0.2:                                 # over the new outline: the sky (the painter's lump, his mottle;
                if O[y, x, 3] > 0 and not near_ball[y, x]:  # by the ball's edge as it is)
                    new[y, x] = O[y, x, :3]; cov[y, x] = 0; ch[y, x] = True
                continue
            if all(r == 'wall' for r in got): continue
            if O[y, x, 3] > 250: c = 1.0
            new[y, x] = np.mean(cols_, 0); cov[y, x] = 1.0 if c > 0.85 else c; ch[y, x] = True
    # the eave's corner at the foot of the left verge: the eave's round end tile and the gutter's end cap under it
    cx_ = e['corner']; yc_ = ytop(cx_ + 0.5)
    for (dx, dy, t) in [(-1, 0, lit), (0, 0, lit), (1, 0, mid), (-1, 1, mid), (0, 1, low), (1, 1, low), (-1, 2, low), (0, 2, board * 0.8),
                        (-2, rl + 2, mid), (-1, rl + 2, lit), (0, rl + 2, mid), (1, rl + 2, low),
                        (-2, rl + 3, low), (-1, rl + 3, mid), (0, rl + 3, low), (1, rl + 3, board * 0.7),
                        (-1, rl + 4, board * 0.7), (0, rl + 4, board * 0.7)]:
        x, y = int(cx_) + dx, int(np.floor(yc_)) + dy
        if ball[y, x] or not zone[y, x]: continue
        new[y, x] = t; cov[y, x] = 1; ch[y, x] = True
    ch &= zone & ~ball
    ratio = darkening(city, unlit, ch)
    clear = ch & (cov == 0)
    lay(city, unlit, new, cov, ch & ~clear, ratio)
    for arr in (city, unlit):
        arr[..., 3][clear] = 0; arr[..., :3][clear] = 0
    if lines is not None:
        for xa, xb in ((e['x0'], xc), (xc, e['x1'] + 1)):
            for k in (0, rl, rl + 1 + bd):
                lines.append(('seg', (xa, ytop(xa) + k), (xb, ytop(xb) + k)))
    return ch


# ---------------------------------------------------------------------------------------------------------------------
# The building across the crossroads behind the oden (x 488..611, 54 m away: 17.8 px a metre): two floors of dark siding
# under a flat roof, face on, its right side running to the vanishing point. On its roof four blocks with rounded tops,
# a small red maple on the last: a roof garden, as Naruto's roof (tools/naruto_roof.py): four planters along the parapet,
# their shrubs clipped into cushions, the maple planted in the last. The painter's blocks were mottle under a pink
# smear; now each what it is, in his tones (sampled on his blocks):
# - the parapet's coping along the front (his lit row 467: its nose, soft; its face; its drip's shadow), a joint every
#   1.85 m (33 px), turning the corner and running down the side face on its ray to the vanishing point;
# - each planter a box (his box rows 460..466: its top rim lit by the sky, its face darker toward its foot, its left end
#   a shade lighter, its right end darker: the light from the street's far end, as his highlights say), set back from
#   the parapet, its foot behind it; in it a clipped cushion (rows 450..459), round at its corners, lit from the upper
#   left (his warm highlight, soft and on its top only), darker toward its foot and its right (no outline: R12), a leafy
#   grain of two tones; the gaps between the planters the sky;
# - the maple as painted (crown and trunk), its trunk into the last cushion.
ODEN = dict(planters=[(490, 508), (512, 535), (540, 558), (562, 591)], top=450, box=460, coping=467, x0=488, corner=600.5,
            side_end=611, joints=(520, 553, 586), maple=(559, 595, 425, 451))


def top_oden(city, unlit, box, lines=None):
    d = ODEN; x0, y0, x1, y1 = box
    O = city.copy()
    zone = np.zeros((H, W), bool); zone[y0:y1, x0:x1] = True
    L = O[..., :3] @ LUMA
    reg = np.zeros((H, W), bool); reg[d['top']:d['coping'], d['x0']:d['corner'].__int__() + 1] = True
    op = O[..., 3] > 250
    hi = med(O, reg & op & (L > 70) & (YY < 458))
    bushc = med(O, reg & op & (L > 18) & (L < 34) & (YY >= 452) & (YY < 459))
    boxc = med(O, reg & op & (YY >= 460) & (YY < 467) & (L > 28) & (L < 44))
    nose = med(O, (YY == d['coping']) & (XX >= 490) & (XX <= 598))
    face = med(O, (YY == d['coping'] + 1) & (XX >= 490) & (XX <= 598))
    wall = med(O, (YY >= d['coping'] + 3) & (YY <= d['coping'] + 6) & (XX >= 495) & (XX <= 595) & op)
    rng = np.random.default_rng(51)
    leaf = gaussian_filter(rng.standard_normal((H, W)), 0.7); leaf /= leaf.std()
    # the maple: kept as painted (its red crown, its trunk), from over the last cushion up
    mx0, mx1, my0, my1 = d['maple']
    maple = np.zeros((H, W), bool)
    sub = O[my0:my1, mx0:mx1]
    maple[my0:my1, mx0:mx1] = (sub[..., 3] > 0) & ((sub[..., 0] > sub[..., 2] + 6) | (np.arange(my0, my1)[:, None] >= 440))
    maple[my1 - 1:, :] = False
    new = O[..., :3].copy(); cov = np.zeros((H, W)); ch = np.zeros((H, W), bool); lit_tops = np.zeros((H, W), bool)
    o = (np.arange(SS) + 0.5) / SS
    # 1. what was there over the coping (the blocks, the smear) goes first: the sky
    for y in range(y0, d['coping']):
        for x in range(d['x0'], int(d['corner']) + 1):
            if O[y, x, 3] > 0 and not maple[y, x]: cov[y, x] = 0; ch[y, x] = True
    # 2. the planters and their cushions
    for a, b in d['planters']:
        w = b - a + 1; cxp = (a + b + 1) / 2
        for x in range(a, b + 1):
            for y in range(d['top'], d['coping']):
                if maple[y, x]: continue
                cols_ = []; nlit = 0
                for sy in o:
                    for sx in o:
                        xf, yf = x + sx, y + sy
                        if yf >= d['box'] - 0.0:            # the box
                            u = (xf - a) / w
                            if yf < d['box'] + 1: t = boxc * 1.14            # its top rim, lit by the sky
                            else: t = boxc * (1.02 - 0.10 * (yf - d['box'] - 1) / 6)
                            if u < 1.5 / w: t = t * 1.08                     # its left end
                            elif u > 1 - 1.5 / w: t = t * 0.82               # its right end
                            cols_.append(t); continue
                        # the cushion: a rounded box over the planter, its corners a quarter circle of radius rc
                        rc = 4.0; hw = w / 2 - 0.3; dx = abs(xf - cxp); top = d['top'] + 0.2
                        ex = max(dx - (hw - rc), 0.0); ey = max(top + rc - yf, 0.0)
                        if dx > hw or yf < top or (ex > 0 and ey > 0 and ex * ex + ey * ey > rc * rc): continue
                        # its light: the sky from the upper left, the street's far end; darker at its foot and right
                        k = 1 - 0.62 * (yf - top) / (d['box'] - top) - 0.38 * (xf - a) / w
                        k = float(np.clip(k + 0.10 * leaf[y, x], 0, 1))
                        if k > 0.76: t = 0.70 * hi + 0.30 * bushc * 1.5; nlit += 1
                        elif k > 0.66: t = 0.40 * hi + 0.60 * bushc * 1.3; nlit += 1
                        elif k > 0.52: t = bushc * 1.2
                        elif k > 0.32: t = bushc
                        else: t = bushc * 0.75
                        cols_.append(t)
                if not cols_: continue
                c = len(cols_) / SS / SS
                if c < 0.2: continue
                new[y, x] = np.mean(cols_, 0); cov[y, x] = 1.0 if c > 0.85 else c; ch[y, x] = True
                if nlit * 2 > len(cols_): lit_tops[y, x] = True
    # 3. the coping along the front, its joints, round the corner and down the side on its ray
    vs = (VP[1] - (d['coping'] + 0.5)) / (VP[0] - d['corner'])
    for x in range(d['x0'], d['side_end'] + 1):
        if x <= d['corner']:
            yt = float(d['coping'])
        else:
            yt = VP[1] - vs * (VP[0] - (x + 0.5)) - 0.5
        for y in range(int(np.floor(yt)) - 1, int(np.floor(yt)) + 4):
            cols_ = []; n = 0
            for sy in o:
                yf = y + sy; dd = yf - yt
                if dd < 0: continue
                n += 1
                if dd < 1: t = nose
                elif dd < 2: t = face
                elif dd < 3: t = wall * 0.62
                else: t = O[y, x, :3] if O[y, x, 3] > 0 else wall
                if x in d['joints'] and 1 <= dd < 2: t = t * 0.78
                if x > d['corner']: t = t * 0.9
                cols_.append(t)
            if not n: continue
            c = n / SS
            if c < 0.2: continue
            new[y, x] = np.mean(cols_, 0); cov[y, x] = 1.0 if (c > 0.85 or O[y, x, 3] > 250) else c; ch[y, x] = True
    ch &= zone
    ratio = darkening(city, unlit, ch)
    clear = ch & (cov == 0)
    lay(city, unlit, new, cov, ch & ~clear, ratio)
    for arr in (city, unlit):
        arr[..., 3][clear] = 0; arr[..., :3][clear] = 0
    NF_TREE[tuple(box)] = lit_tops & ch            # (the cushions' lit tops graded as the painter's were: as the trees)
    if lines is not None:
        lines += [('seg', (d['x0'], d['coping']), (d['corner'], d['coping'])),
                  ('seg', (d['corner'], d['coping']), (d['side_end'] + 1, VP[1] - vs * (VP[0] - d['side_end'] - 1)))]
        for a, b in d['planters']:
            lines += [('seg', (a, d['box']), (b + 1, d['box'])), ('seg', (a, d['top']), (b + 1, d['top']))]
    return ch


# ---------------------------------------------------------------------------------------------------------------------
# The oden's own roof (the low wooden shop under the sign おでん, the left side's first house past the drinks corner):
# between the tree in front of it (tools/tree_a.py's, kept) and the sign standing on it, its slope shows, a navy smear
# with no tiles, no ridge. A kawara roof along the street, its ridge and its courses on the left side's rays (u =
# (615 - y) / (700 - x)): the ridge the ray along the painter's top edge (u 0.551), its round ridge tile lit on top
# (soft) with the shadow under it; five courses down to the eave (u 0.405), each tile's back lit by the sky a little,
# its lower lip darker, the next course's top in its shadow; all on the painter's own light (his smear, smoothed: R2).
ODENSHOP = dict(x0=459, x1=474, u_ridge=(615 - 486.0) / (700 - 466.5), u_eave=0.405, courses=5)


def top_odenshop(city, unlit, box, lines=None):
    d = ODENSHOP; x0, y0, x1, y1 = box
    O = city.copy()
    zone = np.zeros((H, W), bool); zone[y0:y1, x0:x1] = True
    with np.errstate(divide='ignore', invalid='ignore'):
        U = (VP[1] - (YY + 0.5)) / (VP[0] - (XX + 0.5))
    L = O[..., :3] @ LUMA
    # the tree in front (its blossoms reddish, its dark leaves), grown a pixel: kept as it is
    tree = (O[..., 0] > O[..., 2] + 6) | (L < 15)
    from scipy.ndimage import binary_dilation, binary_opening
    tree = binary_dilation(binary_opening(tree, np.ones((2, 2))), np.ones((3, 3))) & (XX < 466)
    roof = (XX >= d['x0']) & (XX <= d['x1']) & (U <= d['u_ridge']) & (U >= d['u_eave']) & zone & ~tree & (O[..., 3] > 250)
    # the painter's light over the roof, smoothed (his smear's low frequencies)
    w = roof.astype(float)
    lf = np.stack([gaussian_filter(O[..., c] * w, 3.0) for c in range(3)], -1) / np.maximum(gaussian_filter(w, 3.0), 1e-6)[..., None]
    n = noise(61, (0.6, 1.2)); tex = (1 + 0.035 * n)
    new = O[..., :3].copy(); cov = np.zeros((H, W)); ch = np.zeros((H, W), bool)
    du = (d['u_ridge'] - d['u_eave']) / d['courses']
    for y, x in zip(*np.nonzero(roof)):
        u = U[y, x]
        if u > d['u_ridge'] - 0.006: k = 1.18                  # the ridge tile's round top, lit
        elif u > d['u_ridge'] - 0.013: k = 0.78                # its underside, the shadow under it
        else:
            f = ((d['u_ridge'] - 0.013 - u) % du) / du          # (0 at a course's top, 1 at its lip)
            k = 1.10 if f < 0.35 else (1.0 if f < 0.75 else (0.86 if f < 0.9 else 0.72))
        new[y, x] = lf[y, x] * k * tex[y, x]; cov[y, x] = 1; ch[y, x] = True
    ratio = darkening(city, unlit, ch)
    lay(city, unlit, new, cov, ch, ratio)
    if lines is not None:
        for u in [d['u_ridge']] + [d['u_ridge'] - 0.013 - du * k for k in range(d['courses'])] + [d['u_eave']]:
            lines.append(('seg', (d['x0'] - 4, VP[1] - u * (VP[0] - d['x0'] + 4)), (d['x1'] + 2, VP[1] - u * (VP[0] - d['x1'] - 2))))
    return ch


NF_TREE = {}                                     # box -> pixels night_far codes as the trees' (160): foliage lit as theirs


def update_far(ch, tree=None):
    """assets/night_far.webp: the street's (0) where a top changed a pixel, the trees' (160) on foliage lit as theirs."""
    p = os.path.join(ROOT, 'assets', 'night_far.webp')
    nf = np.asarray(Image.open(p).convert('RGB')).copy()
    want = np.zeros(nf.shape[:2], np.uint8)
    if tree is not None: want[tree] = 160
    if (nf[ch] == want[ch][:, None]).all(): return
    nf[ch] = want[ch][:, None]
    Image.fromarray(nf, 'RGB').save(p, 'WEBP', lossless=True, quality=100, method=6, exact=True)


TOPS = {}                                        # box -> drawing function (filled below)


def draw(city, unlit, box):
    """The zone (redraw_zones.py): both layers (RGBA floats, whole scene) changed in place; returns what changed."""
    ch = TOPS[tuple(box)](city, unlit, box)
    update_far(ch, NF_TREE.get(tuple(box)))
    return ch


BOX_B = (942, 40, 1023, 300)
TOPS[BOX_B] = top_b
BOX_C = (1065, 40, 1120, 160)
TOPS[BOX_C] = top_c
BOX_PC = (884, 436, 905, 470)
TOPS[BOX_PC] = top_pc
BOX_END = (752, 434, 856, 500)
TOPS[BOX_END] = top_end
BOX_ODEN = (486, 424, 614, 486)
TOPS[BOX_ODEN] = top_oden
BOX_ODENSHOP = (455, 478, 478, 528)
TOPS[BOX_ODENSHOP] = top_odenshop


def preview(out, only=None):
    os.makedirs(out, exist_ok=True)
    L = {t: np.asarray(Image.open(os.path.join(ROOT, 'assets', f)).convert('RGBA')).astype(float)
         for t, f in (('city', 'layer_city_off.webp'), ('unlit', 'street_unlit.webp'))}
    A = {t: a.copy() for t, a in L.items()}
    for box, fn in TOPS.items():
        if only and fn.__name__ != only: continue
        lines = []
        ch = fn(A['city'], A['unlit'], box, lines)
        print(fn.__name__, 'pixels changed', int(ch.sum()))
        x0, y0, x1, y1 = box
        for tag, arr in (('before', L['city']), ('after', A['city'])):
            a = arr[y0:y1, x0:x1]; bg = np.array([40, 60, 90.0])
            rgb = a[..., :3] * a[..., 3:] / 255 + bg * (1 - a[..., 3:] / 255)
            im = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).resize(((x1 - x0) * 6, (y1 - y0) * 6), Image.NEAREST)
            if tag == 'after':
                from PIL import ImageDraw
                im2 = im.copy(); d = ImageDraw.Draw(im2)
                for ln in lines:
                    if ln[0] == 'ray':
                        _, xa, xb, v = ln
                        d.line([((xa - x0) * 6, (ray_y(xa - 0.5, v) - y0) * 6), ((xb + 1 - x0) * 6, (ray_y(xb + 0.5, v) - y0) * 6)], fill=(255, 220, 0), width=1)
                    elif ln[0] == 'v':
                        _, x, ya, yb = ln
                        d.line([((x + 0.5 - x0) * 6, (ya - y0) * 6), ((x + 0.5 - x0) * 6, (yb - y0) * 6)], fill=(0, 255, 160), width=1)
                    elif ln[0] == 'seg':
                        _, (xa, ya), (xb, yb) = ln
                        d.line([((xa - x0) * 6, (ya - y0) * 6), ((xb - x0) * 6, (yb - y0) * 6)], fill=(255, 220, 0), width=1)
                im2.save(os.path.join(out, f'{fn.__name__}_lines_x6.png'))
            im.save(os.path.join(out, f'{fn.__name__}_{tag}_x6.png'))
    for t, a in A.items():
        Image.fromarray(np.clip(np.round(a), 0, 255).astype(np.uint8), 'RGBA').save(
            os.path.join(out, {'city': 'layer_city_off.webp', 'unlit': 'street_unlit.webp'}[t]), 'WEBP', lossless=True, quality=100, method=6, exact=True)


if __name__ == '__main__':
    if '--preview' in sys.argv:
        i = sys.argv.index('--preview'); preview(sys.argv[i + 1], sys.argv[i + 2] if len(sys.argv) > i + 2 else None)
    else:
        print(__doc__)
