#!/usr/bin/env python3
"""Naruto's floor over Ichiraku, redrawn on the pixel grid: its window, its balcony's railing, its walls and its slabs.

    (a module: tools/redraw_zones.py's zone 'narufloor' calls draw() on the street as the zones before it leave it; it
     also writes assets/window_panes.webp and assets/window_lit_ukki.webp, the window's lit overlay in street.js, WL)
    python3 tools/naruto_floor.py --preview OUT     previews in OUT (nothing written in assets/)

What was there (x 1152..1278, from under the roof's lip down to Ichiraku's signboard): the painter's balcony, its lines
drawn to a vanishing point of their own (the railing's top to x ~810, the window's head steeper still, while Ichiraku's
sign under it and the houses beside it run to the street's (700, 615)): an irregular railing over a lilac smear, frosted
panes, a strip of dark slats nobody could name at the balcony's far end with a box over them, grooves and smudges under
the roof's lip and under the balcony.
What it is (the owner: "à refaire : fenêtre, rambarde, appart Naruto, façade premier"), in the street's perspective
(every line along the street on a ray to VP; what faces us level; what stands, plumb):
- the balcony is set into the building's near corner: its front P (the far pillar's face, the railing, the slabs' edges)
  and the window wall W behind it, D deep; at the near end (Z_n) P is at x XPN, W at XWN (the corner), the railing
  turning there and running back to W level (the frontal section, as the painter had it); at the far end P meets the
  pillar (XPF) and the pillar's side face runs back to W (XWF = W's x at that depth), plain concrete facing us;
- the roof's slab over it (its lit lip, tools/naruto_roof.py's, kept): its underside, the soffit, in deep shadow (navy, as
  the street's deep shadows), a lit arris under the lip; it meets W on a ray (WALL_V, the pier's top as naruto_roof drew
  it) and the side face on a level line;
- W, one concrete (the pier's own colour at the corner), darker under the soffit and into the corner by the side face;
  in it the sliding window (2.1 m, four sashes on Naruto's own camera, NG in street.js: the panes he walks behind): a dark
  aluminium frame (its head, its jambs, the stiles between the sashes, each with its side toward the vanishing point a
  shade lighter), the glass the painter's night glass, the head's shadow at its top, and behind it a lace curtain drawn
  across (its folds faint in the dark glass) between two heavy drapes gathered at the jambs;
- the railing on P: a handrail (its lit top, its face, its underside), a rail under it, a bottom rail over the floor's
  edge, square bars every BAR m along it (foreshortened toward the vanishing point: 4.3 px apart at the corner, 3 at the
  far end, 2 px wide (a lit side, a shaded one) where there is room; 11 px across the frontal section), posts at its ends
  and at the corner, down to the slab; lit by the street lamp, more at the far end (LAMP: in the power cut that share
  goes, as the painter's railing lost it);
- the balcony's slab under it: its front edge's lit arris, its face, its lower arris, its end facing us at the near end,
  its underside back to the ground floor's wall, then that wall (Ichiraku's, in the painter's teal) down to the sign, a
  shadow under the slab on it; at the far end, under the slab, the pillar's side face again;
- the lit room (window_lit_ukki.webp, added on the panes by street.js, pane after pane): the lace lit warm by the room's
  ceiling light (brightest at the third pane as the painter's, its folds, a fine grain), the drapes at the jambs dimmer
  and redder, the head's shadow at the top, Ukki-kun (Naruto's potted plant) on the far sash's sill a dark shape against
  the lace (cut from the old sheet, set on the new handrail as it sat on the old), and the room's light on the soffit
  over the window (a soft warm pool, strongest at the wall); window_panes.webp says which pane each lit pixel follows
  (red = pane x 50) and where the light is (alpha): the glass and that pool, never the frame or the railing in front, so
  Naruto's silhouette (cut out of the light) stays behind the bars.
The far pillar's face (PILLAR, from under the parapet's coping to the sign) keeps the painter's light below PILLAR_SIGMA,
its blotches gone, in both layers.
The power cut (street_unlit): the same picture, the lamp's share off the railing and the slab's edge (LAMP); the walls,
the glass and the slabs' shaded faces as they are (no light of the street on them). Colours are the painter's (sampled on his pier, his
glass, his railing's lit tops, his soffit made navy), each surface with a fine even grain (GRAIN) instead of blotches.
Needs Pillow, numpy, scipy.
"""
import os
import sys
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDITS = os.path.join(ROOT, 'tools', 'src', 'edits')
ASSETS = os.path.join(ROOT, 'assets')
BOX = (1120, 55, 1279, 390)                    # the zone (redraw_zones.py 'narufloor')
VPX, VPY = 700.0, 615.0                        # the street's vanishing point
LUMA = np.array([0.299, 0.587, 0.114])

# the balcony (continuous scene coordinates: a pixel (x, y) covers [x, x+1) x [y, y+1))
XPN, XWN = 1236.0, 1279.0                      # at the near end: P's corner (the frontal section's left end), W's corner
XPF = 1152.0                                   # P at the far end: the pillar's right edge (its downpipe's)
KW = (XWN - VPX) / (XPN - VPX)                 # W's offset over P's, from the vanishing point (the balcony's depth)
XWF = VPX + (XPF - VPX) * KW                   # W at the far end (the side face runs from XPF to it)
V = lambda x, y: (VPY - y) / (x - VPX)
Y = lambda x, v: VPY - v * (x - VPX)
YRT, YFL, YSB = 211.0, 262.0, 274.0            # at the near end: the handrail's top, the floor's edge, the slab's bottom
V_RT, V_FL, V_SB = V(XPN, YRT), V(XPN, YFL), V(XPN, YSB)
V_GW = V(XWN, YSB)                             # the underside's back edge, on the ground floor's wall (W)
WALL_V = 0.9135                                # W meets the soffit (the pier's top as tools/naruto_roof.py drew it)
YSIDE = Y(XWF, WALL_V)                         # the side face's top (level)
Y_FAR_SB = Y(XPF, V_SB)                        # the slab's bottom at the far end (the underside's far edge, level)
# the window on W, its sashes on Naruto's camera (street.js NG: zn, the near end's depth in m; positions s m from the
# corner along W), its head and sill on rays through the near jamb
ZN = 18.7166
xw = lambda s: VPX + (XWN - VPX) * ZN / (ZN + s)
sw = lambda x: ZN * ((XWN - VPX) / (x - VPX) - 1)
S_NEAR, S_FAR = sw(1268.0), sw(1190.0)          # the frame's outer edges (the pier from the corner to x 1268)
SASH = [xw(S_NEAR + k * (S_FAR - S_NEAR) / 4) for k in range(5)]   # its sashes' edges, near to far
V_HEAD, V_GLASS, V_SILL = V(1268.5, 100.0), V(1268.5, 103.0), V(1268.5, 259.0)   # the frame's top, the glass's, the sill
FRAME_W = 2                                     # the jambs' and the stiles' width (px)
DRAPE = (0.36, 0.30)                            # the drapes gathered at the far and the near jamb (m along W)
# the railing (P): rows at the near end, scaled along the rays; bars every BAR m (on the same camera); posts
BAR = 0.15
RT_H, MR_OFF, MR_H, BR_OFF, BR_H = 3, 8, 2, 7, 2   # handrail height; mid rail: its top under the handrail's, height;
                                                    # bottom rail: its top over the floor's edge, height
xp = lambda s: VPX + (XPN - VPX) * ZN / (ZN + s)
sp = lambda x: ZN * ((XPN - VPX) / (x - VPX) - 1)
KZ = 74.8                                       # px per m at the near end's depth (NG's kzn: P, W and his path alike)
LAMP = ((1185.0, 0.68), (1202.0, 0.94))         # the street lamp's share on the railing and the slab's edge: what the power
                                                # cut leaves of it (the painter's railing: 0.68 at the far end, 0.94 by the corner)
GRAIN = 0.07                                    # the surfaces' fine grain (relative)
PILLAR = (1124, 1143)                           # the far pillar's face, between C's corner (x 1122, 1123: its joint and lit
PILLAR_SIGMA = 3.0                              # arris) and the downpipe's shadow: its light below this scale kept, its
                                                # blotches gone, from under the parapet's coping down to the sign

# the painter's colours (night, the street with its lights off; sampled on his pier, glass, railing, soffit)
C = dict(
    soffit=(0, 2, 6), soffit_lo=(1, 4, 10), arris=(10, 16, 29),
    wall=(6, 16, 27),
    side=(3, 8, 16), side_low=(2, 6, 12),
    frame=(3, 6, 12), frame_side=(10, 16, 27), head_lo=(8, 13, 23), reveal=(5, 11, 19),
    glass=(20, 27, 44), drape=(11, 14, 26),
    rail_top=(70, 80, 114), rail=(42, 48, 78), rail_under=(18, 22, 38),
    mid_top=(46, 54, 86), mid=(24, 28, 46), bot_top=(54, 56, 98), bot=(26, 28, 50),
    bar_lit=(40, 47, 78), bar=(24, 29, 50), post_lit=(50, 56, 90), post_mid=(32, 36, 60), post=(16, 19, 33),
    edge=(54, 56, 100), edge2=(26, 28, 52), slab=(9, 15, 27), slab_lo=(11, 18, 31), slab_arris=(16, 24, 40),
    end=(8, 14, 25),
    under=(0, 2, 6), under_back=(2, 5, 11),
    gwall=(2, 9, 15))
C = {k: np.array(v, float) for k, v in C.items()}
LIT_ROLES = ('rail_top', 'rail', 'rail_under', 'mid_top', 'mid', 'bot_top', 'bot', 'bar_lit', 'bar', 'post_lit',
             'post_mid', 'post', 'edge', 'edge2')
# the lit room (additive, street.js WL): the lace's warm light at its brightest, the ceiling lamp over the third pane
WARM = np.array((168.0, 110.0, 32.0))
WL = (1188, 56, 91, 244)                         # the overlay's box (street.js WL: x, y, w, h)
UKKI_OLD = (1193, 220, 1210, 242)                # Ukki-kun's shadow on the old sheet (its scene box), sitting on the old
UKKI_RAIL_OLD = lambda x: 282.0 - 0.946 * (x - 1158)   # handrail (the painter's: its top row)


def rng(seed):
    return np.random.default_rng(seed)


def grain(shape, seed, s=0.7):
    n = gaussian_filter(rng(seed).normal(size=shape), s)
    return n / (n.std() + 1e-9)


def lamp_k(x):
    """what the power cut leaves of the lamp-lit colours at column x"""
    (xa, ka), (xb, kb) = LAMP
    return np.interp(x, [xa, xb], [ka, kb])


def lip_bottom(O, box):
    """per column: the roof's lip's last row as painted (its lit band, tools/naruto_roof.py's lip), the zone's top"""
    x0, y0, x1, y1 = box; L = O @ LUMA; out = {}
    for x in range(x0, x1):
        if x >= 1250:
            out[x] = 56; continue                  # (the slab's end band on the near side, rows 46..56)
        r = int(np.floor(376.9 + (107.5 - 376.9) * (x - 985.4) / (1200.0 - 985.4) + 0.5))   # naruto_roof's lip, its first row
        y = max(r, y0); last = r - 1
        for yy in range(y, min(r + 16, y1)):
            q = O[yy - y0, x - x0]
            if L[yy - y0, x - x0] >= 12 or q[0] > q[2] + 4: last = yy     # (its lit band, or the low sun's glint on it)
            elif yy > last + 1: break
        out[x] = last
    return out


def coping_rows(O, box):
    """per column over the far pillar: the parapet's coping's lowest lit row as tools/naruto_roof.py drew it"""
    x0, y0 = box[:2]; L = O @ LUMA; out = {}
    for x in range(PILLAR[0], PILLAR[1]):
        ys = [y for y in range(140, 200) if L[y - y0, x - x0] >= 25]
        out[x] = max(ys) if ys else 190
    return out


def sign_top(box):
    """per column: Ichiraku's sign's first row (the zone 'ramen' redrew it from there down: its polygon's top edge)"""
    x0, y0, x1, y1 = box
    return {x: int(np.floor(393 + (302 - 393) * (x + 0.5 - 1106) / (1278 - 1106))) - 1 for x in range(x0, x1)}


def roles(box, lip, sign, coping):
    """what each pixel of the zone shows (its centre, front to back), and a parameter for its shading"""
    x0, y0, x1, y1 = box; h, w = y1 - y0, x1 - x0
    R = np.full((h, w), '', 'U12'); T = np.zeros((h, w)); P = np.zeros((h, w), int)
    for xi in range(w):
        x = x0 + xi; xc = x + 0.5
        if x < XPF:                                # (the downpipe and its shadow: kept; the pillar's face under the
            if PILLAR[0] <= x < PILLAR[1]:         # coping, cleaned)
                top = coping[x] + 2
                for yi in range(h):
                    if top <= y0 + yi < sign[x]: R[yi, xi] = 'pillar'
            continue
        for yi in range(h):
            y = y0 + yi; yc = y + 0.5
            if y <= lip[x] or y >= sign[x]:
                continue
            r, t, p = role_at(xc, yc)
            R[yi, xi] = r; T[yi, xi] = t; P[yi, xi] = p
    return R, T, P


def bar_at(xc, frontal):
    """what of the railing's uprights is at column centre xc: a post (its lit, middle or shaded column), a bar (lit or
    shaded column: 2 px where they are 3.8 px apart or more, else 1), or nothing; along P, or across the frontal section
    (level, at the near end's scale: a bar every BAR m, evened out between the corner post and the wall's)"""
    if XPN - 1 <= xc < XPN + 2:                    # the corner post, shared
        return ('post_lit', 'post_mid', 'post')[int(xc - (XPN - 1))]
    if frontal:
        if xc >= XWN - 2:                          # the post against W
            return ('post_lit', 'post')[min(int(xc - (XWN - 2)), 1)]
        n = int(round((XWN - XPN) / KZ / BAR)); step = (XWN - XPN) / n
        for k in range(1, n):
            xb = XPN + k * step
            if xb - 1 <= xc < xb + 1:
                return 'bar_lit' if xc < xb else 'bar'
        return None
    if xc < XPF + 3:                               # the far post, against the pillar
        return ('post_lit', 'post_mid', 'post')[min(int(xc - XPF), 2)]
    k = int(np.floor(sp(xc) / BAR))
    for j in (k, k + 1):
        if j < 1: continue
        xb = xp(j * BAR); gap = xp((j - 1) * BAR) - xb
        half = 1.0 if gap >= 3.8 else 0.5
        if xb - half <= xc < xb + half:
            return 'bar_lit' if (half == 0.5 or xc < xb) else 'bar'
    return None


def role_at(xc, yc):
    # 1. the railing (on P, in front of everything); its frontal section across the near end
    frontal = xc >= XPN
    if xc >= XPF:
        if frontal:
            yt, yf = YRT, YFL; sc = 1.0
        else:
            yt, yf = Y(xc, V_RT), Y(xc, V_FL); sc = (xc - VPX) / (XPN - VPX)
        if yt <= yc < yf:
            q = (yc - yt) / sc                         # (near-end pixels from the handrail's top)
            qb = (yf - yc) / sc                        # (near-end pixels over the floor's edge)
            b = bar_at(xc, frontal)
            if q < RT_H:
                return ('rail_top', 'rail', 'rail_under')[min(int(q), 2)], 0, 0
            if b and b.startswith('post'):             # (the posts down to the slab)
                return b, 0, 0
            if MR_OFF <= q < MR_OFF + MR_H:
                return ('mid_top' if q < MR_OFF + 1 else 'mid'), 0, 0
            if BR_OFF - BR_H < qb <= BR_OFF:
                return ('bot_top' if qb > BR_OFF - 1 else 'bot'), 0, 0
            if b and qb > BR_OFF - BR_H:
                return b, 0, 0
    # 2. the balcony's slab: its edge on P (a lit arris, a lighter row under it), its end facing us at the near end
    if XPF <= xc < XPN:
        yf, yb = Y(xc, V_FL), Y(xc, V_SB)
        if yf <= yc < yb:
            sc = (xc - VPX) / (XPN - VPX); q = (yc - yf) / sc
            return ('edge' if q < 1 else 'edge2' if q < 2 else 'slab_arris' if yb - yc < sc else 'slab'), q / (YSB - YFL), 0
    if XPN <= xc < XWN and YFL <= yc < YSB:
        q = yc - YFL
        return ('edge' if q < 1 else 'edge2' if q < 2 else 'slab_arris' if YSB - yc < 1 else 'end'), q / (YSB - YFL), 0
    # 3. under the slab: its underside, the ground floor's wall, the pillar's side face at the far end
    if xc >= XPF:
        yb = Y(xc, V_SB) if xc < XPN else YSB
        if yc >= yb:
            if xc < XWF:
                if yc < Y_FAR_SB:
                    return 'under', (yc - yb) / max(Y_FAR_SB - yb, 1), 0
                return 'side_low', (yc - Y_FAR_SB), 0
            yg = Y(xc, V_GW)
            if yc < yg:
                return 'under', (yc - yb) / max(yg - yb, 1), 0
            return 'gwall', yc - yg, 0
    # 4. behind the railing, over the floor: the side face, then W and its window; over them the soffit
    if xc < XWF:
        if yc >= YSIDE:
            return 'side', (yc - YSIDE), 0
        return 'soffit', 0, 0
    yw = Y(xc, WALL_V)
    if yc < yw:
        return 'soffit', yw - yc, 0
    # W: the window between its jambs, the pier at the corner
    xa, xb = SASH[4], SASH[0]                      # far and near outer edges
    if xa <= xc < xb:
        yh, yg, ys = Y(xc, V_HEAD), Y(xc, V_GLASS), Y(xc, V_SILL)
        if yc < yh:
            return 'wall', yc - yw, 0
        if yc >= ys:
            return 'frame', 0, 0
        if xc < xa + FRAME_W:                      # the far jamb (its side toward the vanishing point lit)
            return ('frame_side' if xc < xa + 1 else 'frame'), 0, 0
        if xc >= xb - FRAME_W:
            return ('frame_side' if xc < xb - FRAME_W + 1 else 'frame'), 0, 0
        for k in (1, 2, 3):                        # the stiles between the sashes
            if SASH[k] - FRAME_W / 2 <= xc < SASH[k] + FRAME_W / 2:
                return ('frame_side' if xc < SASH[k] - FRAME_W / 2 + 1 else 'frame'), 0, 0
        if yc < yg:
            return ('head_lo' if yc >= yg - 1 else 'frame'), 0, 0
        pane = 4 - int(np.searchsorted(-np.array(SASH), -xc))   # (1: the far sash, 4: the near one)
        return 'glass', yc - yg, min(max(pane, 1), 4)
    if xc < xa:
        return ('reveal' if yc >= Y(xc, V_HEAD) else 'wall'), yc - yw, 0
    return 'wall', yc - yw, 0


def paint(O, U, box, R, T, P):
    """the new street and its power cut over box, from the roles"""
    x0, y0, x1, y1 = box; h, w = R.shape
    X = np.arange(x0, x1)[None, :] + 0.5 + np.zeros((h, 1))
    new = O.copy(); n = grain((h, w), 7)
    def put(m, c, g=GRAIN):
        new[m] = c * (1 + g * n[m])[:, None]
    for r in ('rail_top', 'rail', 'rail_under', 'mid_top', 'mid', 'bot_top', 'bot', 'bar_lit', 'bar', 'post_lit', 'post_mid',
              'post', 'frame', 'frame_side', 'head_lo', 'reveal', 'slab_arris', 'end', 'edge', 'edge2'):
        m = R == r
        if m.any(): put(m, C[r], 0.04)
    lit = np.isin(R, LIT_ROLES)                     # (the street lamp's light on them, stronger toward the far end)
    new[lit] *= np.interp(X[lit], [1160.0, 1236.0], [1.15, 1.0])[:, None]
    # the soffit: navy, a little lighter toward W (the street's light from below), the lip's lower arris lit
    m = R == 'soffit'
    k = np.clip(T / 14.0, 0, 1)[m][:, None]
    new[m] = (C['soffit_lo'] * (1 - k) + C['soffit'] * k) * (1 + 0.05 * n[m])[:, None]
    lipm = np.zeros_like(m)                         # (its first row under the lip)
    for xi in range(w):
        ys = np.nonzero(m[:, xi])[0]
        if len(ys) and X[0, xi] < 1250: lipm[ys[0], xi] = True
    new[lipm] = C['arris']
    # W: the pier's concrete, darker under the soffit (AO over a few px) and into the corner by the side face
    m = R == 'wall'
    ao = (1 - 0.4 * np.exp(-T / 2.5)) * (1 - 0.25 * np.exp(-np.clip(X - XWF, 0, None) / 3.0))
    new[m] = C['wall'] * ao[m][:, None] * (1 + GRAIN * n[m])[:, None]
    # the side face (frontal): darker into the corner with W and under the soffit
    for r in ('side', 'side_low'):
        m = R == r
        if not m.any(): continue
        a = (1 - 0.35 * np.exp(-np.clip(XWF - X, 0, None) / 4.0)) * (1 - 0.3 * np.exp(-T / 3.0))
        new[m] = C[r] * a[m][:, None] * (1 + GRAIN * n[m])[:, None]
    # the slab's face (lighter toward its lower arris), its underside (darker at the front), the ground wall (a shadow
    # under the slab on it)
    m = R == 'slab'; tt = np.clip(T[m], 0, 1)[:, None]
    new[m] = (C['slab'] * (1 - tt) + C['slab_lo'] * tt) * (1 + GRAIN * n[m])[:, None]
    m = R == 'under'; tt = np.clip(T[m], 0, 1)[:, None]
    new[m] = (C['under'] * (1 - tt) + C['under_back'] * tt) * (1 + 0.05 * n[m])[:, None]
    m = R == 'gwall'; sh = 1 - 0.5 * np.exp(-T[m] / 1.5)
    new[m] = C['gwall'] * sh[:, None] * (1 + GRAIN * n[m])[:, None]
    # the glass: the painter's night glass, the head's shadow at its top, the lace's folds faint, the drapes darker
    m = R == 'glass'
    s = sw(X[m])
    lace = 1 + 0.06 * np.sin(2 * np.pi * s / 0.11 + 1.3 * np.sin(s * 7.1))
    dr = drape_k(s)
    top = 1 - 0.25 * np.exp(-T[m] / 1.6)
    low = 0.94 + 0.06 * np.clip(T[m] / 120.0, 0, 1)
    g = C['glass'][None, :] * (lace * top * low)[:, None]
    g = g * (1 - dr)[:, None] + C['drape'][None, :] * (top * (0.8 + 0.2 * drape_fold(s)))[:, None] * dr[:, None]
    new[m] = g * (1 + 0.025 * n[m])[:, None]
    # the far pillar's face: the painter's light on it (below PILLAR_SIGMA), the fine grain of the rest, in both layers
    pm = R == 'pillar'
    if pm.any():
        new[pm] = lowpass_in(O, pm, PILLAR_SIGMA)[pm] * (1 + GRAIN * n[pm])[:, None]
    # the power cut: the lamp's share off the railing and the slab's edge; the walls, the glass and the slabs' shaded
    # faces as they are (no light of the street on them; the painter's own power cut changes nothing there)
    unew = U.copy(); done = R != ''
    unew[done] = new[done]
    unew[lit] = new[lit] * lamp_k(X[lit])[:, None]
    if pm.any():
        unew[pm] = lowpass_in(U, pm, PILLAR_SIGMA)[pm] * (1 + GRAIN * n[pm])[:, None]
    return new, unew, done


def lowpass_in(A, m, s):
    """A's low frequencies inside mask m only (normalised convolution: nothing from outside it)"""
    w = gaussian_filter(m.astype(float), s) + 1e-6
    return np.stack([gaussian_filter(A[..., c] * m, s) / w for c in range(3)], -1)


def drape_k(s):
    """how much of the drape is behind the glass at s (m along W from the corner): 1 at the jambs, 0 on the lace"""
    a = np.clip((S_FAR - s) / DRAPE[0], 0, 1); b = np.clip((s - S_NEAR) / DRAPE[1], 0, 1)
    soft = lambda u: np.clip(1.6 - 1.6 * u, 0, 1)
    return np.maximum(soft(a), soft(b))


def drape_fold(s):
    return 0.5 + 0.5 * np.cos(2 * np.pi * s / 0.09)


def overlay(R, T, P, box):
    """the window's lit overlay (street.js WL): which pane each lit pixel follows, and the room's light"""
    x0, y0 = box[:2]; wx, wy, ww, wh = WL
    mask = np.zeros((wh, ww, 4), np.uint8); lit = np.zeros((wh, ww, 4), float)
    n = grain((wh, ww), 11, 0.8)
    for yy in range(wh):
        for xx in range(ww):
            x, y = wx + xx, wy + yy
            if not (box[0] <= x < box[2] and box[1] <= y < box[3]): continue
            r = R[y - y0, x - x0]; xc, yc = x + 0.5, y + 0.5
            if r == 'glass':
                p = P[y - y0, x - x0]; s = sw(xc)
                # the ceiling lamp over the third sash, the room a little darker low down and far
                lamp = 0.74 + 0.26 * np.exp(-((xc - 1236.0) / 26.0) ** 2) * np.exp(-((yc - 165.0) / 70.0) ** 2)
                lamp *= 0.92 + 0.08 * np.clip((xc - 1190.0) / 70.0, 0, 1)
                lace = 1 + 0.07 * np.sin(2 * np.pi * s / 0.11 + 1.3 * np.sin(s * 7.1))
                top = 1 - 0.45 * np.exp(-T[y - y0, x - x0] / 1.8)       # (the head's shadow)
                dk = drape_k(np.array([s]))[0]
                c = WARM * lamp * lace * top * (1 + 0.045 * n[yy, xx])
                dc = WARM * np.array((0.62, 0.42, 0.30)) * lamp * top * (0.65 + 0.35 * drape_fold(np.array([s]))[0])
                c = c * (1 - dk) + dc * dk
                lit[yy, xx, :3] = c; lit[yy, xx, 3] = 255
                mask[yy, xx] = (50 * p, 0, 0, 255)
            elif r == 'soffit' and x >= XWF:
                d = T[y - y0, x - x0]                  # (rows over W's top)
                if d > 26: continue
                p = 4 - int(np.searchsorted(-np.array(SASH), -xc)); p = min(max(p, 1), 4)
                ss = lambda u: np.clip(u, 0, 1) ** 2 * (3 - 2 * np.clip(u, 0, 1))   # (smoothstep)
                a = 0.22 * np.exp(-d / 6.0) * ss((xc - SASH[4] + 2) / 14) * ss((SASH[0] + 4 - xc) / 14)
                if a < 0.012: continue
                lit[yy, xx, :3] = WARM * a; lit[yy, xx, 3] = 255
                mask[yy, xx] = (50 * p, 0, 0, 255)
    ukki(lit, mask)
    return mask, lit


def ukki(lit, mask):
    """Ukki-kun (Naruto's potted plant, droite-09) on the far sash's sill: his dark shape cut from the old sheet, set on the
    new handrail as he sat on the old one"""
    old = np.asarray(Image.open(os.path.join(EDITS, 'window_lit_ukki_before.webp')).convert('RGBA')).astype(float)
    ox, oy = 1188, 100                                  # (the old sheet's place)
    a, b, c, d = UKKI_OLD
    sub = old[b - oy:d - oy, a - ox:c - ox]
    L = sub[..., :3] @ LUMA; ref = np.median(L[L > 30]) if (L > 30).any() else 1
    k = np.where(sub[..., 3] > 0, np.clip(L / ref, 0, 1), 1.0)
    shape = k < 0.75
    if not shape.any(): return
    ys, xs = np.nonzero(shape)
    xm = a + xs.mean(); base_old = b + ys.max()
    dy = int(round(Y(xm + 0.5, V_RT) - UKKI_RAIL_OLD(xm)))
    wx, wy = WL[:2]
    for yy, xx in zip(ys, xs):
        X_, Y_ = a + xx, b + yy + dy
        i, j = Y_ - wy, X_ - wx
        if 0 <= i < lit.shape[0] and 0 <= j < lit.shape[1] and mask[i, j, 3] and mask[i, j, 0] == 50:
            lit[i, j, :3] *= k[yy, xx] / 0.95


def draw(city, unlit, box=BOX, write=True):
    """The zone (redraw_zones.py): the layers changed in place (whole-scene float RGBA), the window's overlay written;
    returns what changed in box."""
    x0, y0, x1, y1 = box
    O, U = city[y0:y1, x0:x1, :3].copy(), unlit[y0:y1, x0:x1, :3].copy()
    lip = lip_bottom(O, box); sign = sign_top(box)
    R, T, P = roles(box, lip, sign, coping_rows(O, box))
    new, unew, done = paint(O, U, box, R, T, P)
    city[y0:y1, x0:x1, :3][done] = np.clip(np.round(new[done]), 0, 255)
    unlit[y0:y1, x0:x1, :3][done] = np.clip(np.round(unew[done]), 0, 255)
    city[y0:y1, x0:x1, 3][done] = 255; unlit[y0:y1, x0:x1, 3][done] = 255
    mask, lit = overlay(R, T, P, box)
    if write:
        save(mask, os.path.join(ASSETS, 'window_panes.webp'))
        save(lit, os.path.join(ASSETS, 'window_lit_ukki.webp'))
    draw.last = (R, T, P, mask, lit)
    return done


def save(a, path):
    Image.fromarray(np.round(np.clip(a, 0, 255)).astype(np.uint8), 'RGBA').save(path, 'WEBP', lossless=True, quality=100, method=6, exact=True)


def preview(out):
    """the zone drawn on the layers as they are (or as given), its crops before and after, lit and not, x4"""
    os.makedirs(out, exist_ok=True)
    L = {t: np.asarray(Image.open(os.path.join(ASSETS, f)).convert('RGBA')).astype(float)
         for t, f in (('city', 'layer_city_off.webp'), ('unlit', 'street_unlit.webp'))}
    bc = os.path.join(EDITS, 'narufloor_before_city.webp')
    if os.path.exists(bc):                              # (from the painter's pixels, as redraw_zones does, over the sign:
        x0, y0, x1, y1 = BOX                            # under it, the sign as the zone 'ramen' left it)
        sg = sign_top(BOX); keep = np.array([[y < sg[x] for x in range(x0, x1)] for y in range(y0, y1)])
        for t in ('city', 'unlit'):
            b = np.asarray(Image.open(os.path.join(EDITS, f'narufloor_before_{t}.webp')).convert('RGBA')).astype(float)
            L[t][y0:y1, x0:x1][keep] = b[keep]
    A = {t: a.copy() for t, a in L.items()}
    draw(A['city'], A['unlit'], BOX, write=False)
    R, T, P, mask, lit = draw.last
    old_m = np.asarray(Image.open(os.path.join(EDITS, 'window_panes_before.webp')).convert('RGBA')).astype(float)
    old_l = np.asarray(Image.open(os.path.join(EDITS, 'window_lit_ukki_before.webp')).convert('RGBA')).astype(float)
    B = (1110, 40, 1300, 400)
    def crop(a): return np.clip(a[B[1]:B[3], B[0]:B[2], :3], 0, 255).copy()
    def add(z, m, l, at):
        ax, ay = at; g = (m[..., 3] >= 128)[..., None]
        hh, ww = m.shape[:2]
        z[ay - B[1]:ay - B[1] + hh, ax - B[0]:ax - B[0] + ww] += np.where(g, l[..., :3], 0)
        return np.clip(z, 0, 255)
    shots = {'city_before': crop(L['city']), 'city_after': crop(A['city']),
             'unlit_before': crop(L['unlit']), 'unlit_after': crop(A['unlit']),
             'lit_before': add(crop(L['city']), old_m, old_l, (1188, 100)), 'lit_after': add(crop(A['city']), mask, lit, WL[:2])}
    for k, z in shots.items():
        for gm, suf in ((1.0, ''), (0.55, 'b')):
            Image.fromarray(np.round(255 * (z / 255) ** gm).astype(np.uint8)).resize(((B[2] - B[0]) * 4, (B[3] - B[1]) * 4), Image.NEAREST).save(os.path.join(out, f'{k}_x4{suf}.png'))
        Image.fromarray(np.round(z).astype(np.uint8)).save(os.path.join(out, f'{k}_1.png'))
    print('pixels changed', int((R != '').sum()), 'sashes', [round(s, 1) for s in SASH], 'XWF', round(XWF, 1), 'side top', round(YSIDE, 1))


if __name__ == '__main__':
    if '--preview' in sys.argv:
        preview(sys.argv[sys.argv.index('--preview') + 1])
    else:
        print(__doc__)
