#!/usr/bin/env python3
"""Naruto's floor over Ichiraku, redrawn on the pixel grid: its window, its balcony's railing, its walls and its slabs, and
the roof's edge over it, its garden and its downpipes, on the same lines.

    (a module: tools/redraw_zones.py's zone 'narufloor' calls draw() on the street as the zones before it leave it; it
     also writes assets/window_panes.webp and assets/window_lit_ukki.webp, the window's lit overlay in street.js, WL;
     assets/roof_sway.webp, the garden's wind data (street.js ROOF: its box printed); and assets/street_sun.webp over its
     box, from its before crop: the low sun's glint on the lip, moved with it)
    python3 tools/naruto_floor.py --preview OUT     previews in OUT (nothing written in assets/)

The roof (the owner, after the floor: "rebord, tuyauterie et géométrie du toit pas correctes"): tools/naruto_roof.py had
kept the painter's lip and stood its parapet on it, on a vanishing point of its own (985, 377), much steeper than the
floor's lines under it. Now the slab's lip is on the ray where its underside's front edge meets the soffit's back edge (W's
top) at the same depth (V_LB = WALL_V x KW), its lit band, the parapet's face and its coping over it in the painter's
proportions at x 1200 (11, 22 and 5 px) scaled along the rays (their thickness constant in perspective); the coping lit on
top, a crisp shadow under it; at the far end the parapet stops on a plumb line at C's corner, over the pillar its face the
pillar's own concrete (cleaned with it); round the near corner (over the railing's corner, XPN) the same rows run level
across the near side: the slab's end over the balcony and over the near wall to the right house's corner (XNS), the near
wall and its coping on over the right house's eave (to XE). What the old edge covered and the new one does not is the sky,
or C's side wall under its coping (naruto_roof's planks); the right house's tiles now against the sky take its light on
their top (naruto_roof's rule). The low sun's glint on the lip's far end (street_sun) moves with the lip. The garden is
naruto_roof's own (its maple, its shrubs and hedge in the planters along the parapet, their clumps, seeds, colours and
light), set on the new coping: the leaves it had are taken off with what they covered (roof_sway_before.webp), the plants
drawn again by its garden() over the new edge; roof_sway.webp is made from them as tools/roof_sway.py made it. The
downpipes: the far one on the pillar's face, round (PIPE_K: lit from the left and the front), from a rain head under the
parapet's outlet at the roof's level straight down behind the sign, a bracket every PIPE_STEP rows; the near corner's
(naruto_roof's) from a socket under the slab's end, its brackets evened out (CPIPE).

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
  shade lighter), clear glass (the owner: "fenêtre de Naruto transparente et Naruto visible aussi"): the room behind it
  (room_lit: its ceiling and its lamp seen from below, its far wall face on with a few of his things, the curtains drawn
  back at the jambs, Ukki-kun on the far sill), out in the night's dark under the glass's faint sheen;
- the railing on P: a handrail (its lit top, its face, its underside), a rail under it, a bottom rail over the floor's
  edge, square bars every BAR m along it (foreshortened toward the vanishing point: 4.3 px apart at the corner, 3 at the
  far end, 2 px wide (a lit side, a shaded one) where there is room; 11 px across the frontal section), posts at its ends
  and at the corner, down to the slab; lit by the street lamp, more at the far end (LAMP: in the power cut that share
  goes, as the painter's railing lost it);
- the balcony's slab under it: its front edge's lit arris, its face, its lower arris, its end facing us at the near end,
  its underside back to the ground floor's wall, then that wall (Ichiraku's, in the painter's teal) down to the sign, a
  shadow under the slab on it; at the far end, under the slab, the pillar's side face again;
- the lit room (window_lit_ukki.webp, added on the panes by street.js, pane after pane): what the lit room adds to it out
  (the sheen stays), and the room's light on the soffit over the window (a soft warm pool, strongest at the wall);
  window_panes.webp says which pane each lit pixel follows (red = pane x 50) and where the light is (alpha): the glass and
  that pool, never the frame or the railing in front; Naruto (street.js, in colour: tools/naruto_col.py) hides the room
  behind him and is drawn in its light, behind the bars.
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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import naruto_roof as NR   # noqa: E402  (the roof garden, the old roof's geometry, its helpers)
import roof_sway as RS     # noqa: E402  (the garden's wind data: its rules)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDITS = os.path.join(ROOT, 'tools', 'src', 'edits')
ASSETS = os.path.join(ROOT, 'assets')
BOX = (1120, 0, 1381, 390)                     # the zone (redraw_zones.py 'narufloor'): the roof's edge and the floor
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
PILLAR = (1124, 1152)                           # the far pillar's face, between C's corner (x 1122, 1123: its joint and lit
PILLAR_SIGMA = 3.0                              # arris) and the balcony: its light below this scale kept, its blotches
                                                # gone, from under the parapet's coping down to the sign (the parapet's
                                                # face over it the same concrete); the downpipe in front of it
# the roof's edge on P, on rays of the same family as the floor's: the slab's lip (its underside's front edge meets the
# soffit's back edge, W's top, at the same depth: WALL_V x KW), its lit band, the parapet's face over it, its coping; at
# x 1200 the painter's proportions (lip 11 px, parapet 22, coping 5), scaled along the rays; round the near corner (XPN,
# over the railing's corner) the same rows level across the near side to its end (XNS)
V_LB = WALL_V * KW
V_LT = V_LB + 11.0 / 500.5
V_PF = V_LT + 22.0 / 500.5
V_CT = V_PF + 5.0 / 500.5
X0R, XNS, XE = 1124, 1297, 1381                # the parapet's far end (against C's corner); the slab's end band on the near
                                                # side to x XNS (the right house's corner boards from there); the near side
                                                # over the right house's eave to XE
SWAY_AT = (1127, 11)                            # roof_sway_before.webp's place (street.js ROOF: B.x0, B.y0)
PIPE = (1145, 1152)                             # the downpipe on the pillar's face: its columns
PIPE_K = (0.55, 1.12, 1.18, 1.0, 0.84, 0.66, 0.45)   # across it: lit from the left and the front, its shade side
PIPE_C = np.array((28.0, 36.0, 58.0))           # its metal (the painter's pipe)
PIPE_UNLIT = 0.78                               # what the power cut leaves of it (the painter's pipe: the lamp lights it)
PIPE_STEP = 45                                  # a bracket every PIPE_STEP rows from the rain head down
CPIPE = (1281, 1288, 50)                        # the near corner's downpipe (tools/naruto_roof.py's strip): its columns, its brackets' step

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


def first_row(yline):
    """the first row whose centre is at or under a line's continuous y"""
    return int(np.ceil(yline - 0.5))


def edge_rows(x):
    """the roof's edge at column x: (the coping's first row, the parapet face's, the lip's, the soffit's)"""
    xc = min(x + 0.5, XPN)                         # (round the near corner: level)
    return tuple(first_row(Y(xc, v)) for v in (V_CT, V_PF, V_LT, V_LB))


def lip_bottom(box):
    """per column: the lip's last row (the slab's end's on the near side), the floor's top"""
    x0, y0, x1, y1 = box
    return {x: edge_rows(x)[3] - 1 for x in range(x0, x1)}


def sign_top(box):
    """per column: Ichiraku's sign's first row (the zone 'ramen' redrew it from there down: its polygon's top edge)"""
    x0, y0, x1, y1 = box
    return {x: int(np.floor(393 + (302 - 393) * (x + 0.5 - 1106) / (1278 - 1106))) - 1 for x in range(x0, x1)}


def roles(box, lip, sign):
    """what each pixel of the zone shows (its centre, front to back), and a parameter for its shading"""
    x0, y0, x1, y1 = box; h, w = y1 - y0, x1 - x0
    R = np.full((h, w), '', 'U12'); T = np.zeros((h, w)); P = np.zeros((h, w), int)
    for xi in range(w):
        x = x0 + xi; xc = x + 0.5
        if x < XPF:                                # (the pillar's face under the parapet's coping, cleaned)
            if PILLAR[0] <= x < PILLAR[1]:
                top = edge_rows(x)[1]
                for yi in range(h):
                    if top <= y0 + yi < sign[x]: R[yi, xi] = 'pillar'
            continue
        if x >= XWN:
            continue                               # (the near side: the roof's edge only)
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


def paint(O, U, box, R, T, P, O0, U0):
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
    # the glass: clear, the room behind it out (the night's dark) under the glass's faint sheen; Ukki-kun on the far sill
    m = R == 'glass'
    uk = ukki_pixels()
    for yi, xi in zip(*np.nonzero(m)):
        x, y = x0 + xi, y0 + yi
        lit_c, out_c, dark_c = room_pixel(x, y, T[yi, xi], n[yi, xi])
        if (x, y) in uk: out_c = out_c - dark_c + uk[(x, y)] * ROOM_DARK
        new[yi, xi] = out_c
    # the far pillar's face: the painter's light on it (below PILLAR_SIGMA), the fine grain of the rest, in both layers
    pm = R == 'pillar'
    if pm.any():
        new[pm] = pillar_light(O0, pm, box)[pm] * (1 + GRAIN * n[pm])[:, None]
    # the power cut: the lamp's share off the railing and the slab's edge; the walls, the glass and the slabs' shaded
    # faces as they are (no light of the street on them; the painter's own power cut changes nothing there)
    unew = U.copy(); done = R != ''
    unew[done] = new[done]
    unew[lit] = new[lit] * lamp_k(X[lit])[:, None]
    if pm.any():
        unew[pm] = pillar_light(U0, pm, box)[pm] * (1 + GRAIN * n[pm])[:, None]
    return new, unew, done


def pillar_light(A, pm, box):
    """the far pillar's light (A: the zone's pixels before it), from its old face only (under tools/naruto_roof.py's coping,
    clear of the downpipe's shadow): below PILLAR_SIGMA, carried up to the new coping at a wider scale"""
    x0, y0 = box[:2]; h, w = pm.shape; src = np.zeros_like(pm)
    for xi in range(w):
        x = x0 + xi
        if PILLAR[0] <= x <= 1142:
            r = NR.front_rows(x)[1] + 2 - y0
            src[max(r, 0):, xi] = pm[max(r, 0):, xi]
    a = lowpass_in(A, src, PILLAR_SIGMA); wa = gaussian_filter(src.astype(float), PILLAR_SIGMA)
    b = lowpass_in(A, src, 10.0)
    t = np.clip((wa - 0.08) / 0.3, 0, 1)[..., None]
    return a * t + b * (1 - t)


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


# ---- the room behind the clear glass (the owner: "génère ... un intérieur de maison, qualité nulle là") ----
# Seen from the street far below and along the facade, a ray through the glass runs much further along the street than it
# goes into the room: it meets the room's far wall, face on (tools/interieur.py, tools/kirua_bay_window.py: the same). That
# wall is a picture drawn for it (tools/src/naruto_room.webp: Naruto's studio flat at night, its ceiling lamp, Team 7's photo,
# the Uzumaki spiral, cup noodles and a cactus on a shelf, the edge of his bed; ROOM_CROP: its inside, without the frame it
# was drawn in), laid face on behind the glass without shear at ROOM_SCALE scene px per px of it, its corner at ROOM_AT
# (the lamp under the window's head over the near sashes); past its edges, its edge rows and columns carried on (the
# ceiling, the wall). Brought to the scene's pixels: each pixel the mean of what it covers, then ROOM_PAL tones of it, a
# pixel alone melted into its neighbours (no blur, no mush); lit as it was drawn, a little lower (ROOM_K); the curtains drawn
# back at both jambs (CURTAIN: m along W from each jamb). Out, the same in the night's dark (ROOM_DARK, channel by channel)
# with the glass's faint sheen over it (SHEEN).
ROOM_CROP = (105, 110, 690, 1070)                # (x0, y0, x1, y1) of the picture's inside
ROOM_SCALE = 0.14
ROOM_AT = (1188.0, 124.0)                        # the picture's corner in the scene
ROOM_PAL = 24
ROOM_K = 0.56                                    # (its light brought to the street's lit windows: Kirua's bay, B's, a median
ROOM_TINT = np.array((1.0, 0.86, 0.74))          # lightness about theirs, warmer: it glows, it is not the brightest thing)
POSTER = ((545, 455, 690, 750), 0.75, (548, 480))   # the spiral's poster (its box in the picture, cut by the picture's edge),
                                                 # made smaller and moved left, into the near sash between its stile and the
                                                 # jamb; the wall carried over where it was
CURTAIN = (0.30, 0.24)                           # the curtains drawn back at the far and the near jamb (m along W)
ROOM_DARK = np.array((0.055, 0.065, 0.11))       # out: the room's colours in the night's dark
SHEEN = np.array((5.0, 7.0, 13.0))               # the glass's faint sheen (the sky in it), at its brightest
CURT_C = np.array((214.0, 104.0, 40.0))


def room_picture():
    """the room's picture on the scene's grid (cached): RGB float"""
    if getattr(room_picture, 'img', None) is not None: return room_picture.img
    a, b, c, d = ROOM_CROP
    src = Image.open(os.path.join(ROOT, 'tools', 'src', 'naruto_room.webp')).convert('RGB')
    (pa, pb, pc, pd), k, (qa, qb) = POSTER
    poster = src.crop((pa, pb, pc, pd))
    arr = np.asarray(src).copy()
    arr[pb:pd, pa:pc] = arr[pb:pd, pa - 15:pa - 14]             # (the wall, row by row, from just left of it)
    src = Image.fromarray(arr)
    src.paste(poster.resize((int(round((pc - pa) * k)), int(round((pd - pb) * k))), Image.LANCZOS), (qa, qb))
    im = src.crop((a, b, c, d))
    w, h = int(round((c - a) * ROOM_SCALE)), int(round((d - b) * ROOM_SCALE))
    px = np.asarray(im.resize((w, h), Image.BOX)).astype(float)
    flat = px.reshape(-1, 3); rng_ = np.random.default_rng(3)
    C = flat[rng_.choice(len(flat), ROOM_PAL, replace=False)].copy()
    for _ in range(30):
        lab = ((flat[:, None] - C[None]) ** 2).sum(-1).argmin(1)
        for j in range(ROOM_PAL):
            if (lab == j).any(): C[j] = flat[lab == j].mean(0)
    q = ((px[..., None, :] - C[None, None]) ** 2).sum(-1).argmin(-1); q2 = q.copy()
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            nb = [q[y - 1, x], q[y + 1, x], q[y, x - 1], q[y, x + 1]]
            if len(set(nb)) == 1 and nb[0] != q[y, x]: q2[y, x] = nb[0]
    room_picture.img = C[q2] * ROOM_K * ROOM_TINT
    return room_picture.img


def room_lit(x, y):
    """the lit room at the glass pixel (x, y): its picture's pixel there (its edges carried on past it)"""
    img = room_picture(); h, w = img.shape[:2]
    i = int(np.clip(np.floor(y - ROOM_AT[1]), 0, h - 1)); j = int(np.clip(np.floor(x - ROOM_AT[0]), 0, w - 1))
    return img[i, j], 'room'


def curtain_k(s):
    """how much curtain is behind the glass at s (m along W from the corner): 1 at the jambs, fading over a few cm"""
    a = np.clip((S_FAR - s) / CURTAIN[0], 0, 1); b = np.clip((s - S_NEAR) / CURTAIN[1], 0, 1)
    return np.clip(np.maximum(1.6 - 1.6 * a, 1.6 - 1.6 * b), 0, 1)


def room_pixel(x, y, Tt, seed_n):
    """the glass pixel (x, y): (lit RGB, out RGB): the room (or the curtains drawn back at the jambs), lit and out; the
    sheen of the glass on the out one (it stays under the room's light, which is added)"""
    xc = x + 0.5; s = sw(xc)
    c, what = room_lit(x, y)
    ck = float(curtain_k(np.array([s]))[0])
    if ck > 0:
        fold = 0.7 + 0.3 * np.cos(2 * np.pi * s / 0.07)
        cl = CURT_C * fold * 0.62                              # (lit from behind: the fabric glows dim)
        c = c * (1 - ck) + cl * ck
    c = c * (1 + 0.015 * seed_n)
    dark = c * ROOM_DARK
    # the sheen: the sky in the glass, a soft band across each sash, lighter up high
    p = 4 - int(np.searchsorted(-np.array(SASH), -xc)); p = min(max(p, 1), 4)
    x0p, x1p = SASH[p], SASH[p - 1]
    u = (xc - x0p) / max(x1p - x0p, 1.0)
    band = np.exp(-((u + (y - 100) / 160.0 - 0.75) / 0.18) ** 2)
    sheen = SHEEN * (0.35 + 0.65 * band) * (1.0 - 0.4 * np.clip((y - 100) / 180.0, 0, 1))
    return c, dark + sheen, dark


def overlay(R, T, P, box):
    """the window's lit overlay (street.js WL): which pane each lit pixel follows, and the room's light"""
    x0, y0 = box[:2]; wx, wy, ww, wh = WL
    mask = np.zeros((wh, ww, 4), np.uint8); lit = np.zeros((wh, ww, 4), float)
    gn = grain(R.shape, 7); uk = ukki_pixels()            # (the zone's grain, as paint() has it: the same room)
    for yy in range(wh):
        for xx in range(ww):
            x, y = wx + xx, wy + yy
            if not (box[0] <= x < box[2] and box[1] <= y < box[3]): continue
            r = R[y - y0, x - x0]; xc, yc = x + 0.5, y + 0.5
            if r == 'glass':
                p = P[y - y0, x - x0]
                lit_c, out_c, dark_c = room_pixel(x, y, T[y - y0, x - x0], gn[y - y0, x - x0])
                if (x, y) in uk: lit_c = uk[(x, y)]
                lit[yy, xx, :3] = np.clip(lit_c - dark_c, 0, 255); lit[yy, xx, 3] = 255
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
    return mask, lit


def ukki_pixels():
    """Ukki-kun (Naruto's potted plant, droite-09) on the far sash's sill, through the clear glass: his shape cut from the
    old sheet (its shadow there), set on the new handrail as he sat on the old one; his leaves green against the lit room,
    his pot terracotta: {(x, y): his colour lit}"""
    old = np.asarray(Image.open(os.path.join(EDITS, 'window_lit_ukki_before.webp')).convert('RGBA')).astype(float)
    ox, oy = 1188, 100                                  # (the old sheet's place)
    a, b, c, d = UKKI_OLD
    sub = old[b - oy:d - oy, a - ox:c - ox]
    L = sub[..., :3] @ LUMA; ref = np.median(L[L > 30]) if (L > 30).any() else 1
    k = np.where(sub[..., 3] > 0, np.clip(L / ref, 0, 1), 1.0)
    shape = k < 0.75
    out = {}
    if not shape.any(): return out
    ys, xs = np.nonzero(shape)
    xm = a + xs.mean(); bot = ys.max()
    dy = int(round(Y(xm + 0.5, V_RT) - UKKI_RAIL_OLD(xm)))
    for yy, xx in zip(ys, xs):
        if bot - yy < 3: col = (150.0, 80.0, 50.0) if bot - yy > 0 else (110.0, 58.0, 38.0)
        else: col = (74.0, 122.0, 62.0) if not shape[max(yy - 1, 0), xx] or yy == 0 else (44.0, 84.0, 44.0)
        out[(a + xx, b + yy + dy)] = np.array(col)
    return out


# ---- the roof's edge (on the floor's rays), the garden set on it, the downpipes ----
RC = {k: np.array(v, float) for k, v in dict(
    cop_top=(28, 40, 76), cop=(15, 22, 40), cop_low=(11, 17, 31),          # the coping: its top lit by the sky, its face, its
    par=(7, 14, 24),                                                       # lower arris; the parapet's face (the pillar's concrete)
    lip_top=(32, 44, 82), lip=(24, 34, 64), lip_low=(19, 28, 52), lip_arris=(14, 21, 40),   # the slab's lit lip (the painter's)
    npar=(6, 13, 22),                                                      # the near side, turned from the street
    slab_top=(9, 17, 27), slab=(6, 12, 19), slab_low=(4, 9, 15)).items()}  # the slab's end on the near side (naruto_roof's)
NEAR_K = 0.85                                   # the near side's coping's light over the street face's


class Lay:
    """the scene's layers for tools/naruto_roof.py's garden: put() as its Layers' (the street, its power cut, the sun's share)"""
    def __init__(s, city, unlit, sun):
        s.city, s.unlit, s.sun = city, unlit, sun; s.H, s.W = city.shape[:2]
        s.nf = np.zeros((1, 1, 3))

    def put(s, x, y, rgb, unlit=None):
        if 0 <= y < s.H and 0 <= x < s.W:
            s.city[y, x, :3] = rgb; s.city[y, x, 3] = 255
            s.unlit[y, x, :3] = rgb if unlit is None else unlit; s.unlit[y, x, 3] = 255
            s.sun[y, x] = 0


def old_top(x):
    """the roof's top as tools/naruto_roof.py drew it (its coping's first row; the near side's level one from its corner)"""
    if x < NR.XC: return NR.front_rows(x)[0]
    return 13 if x < 1300 else min(13, NR.EAVE[x - 1296])


def c_wall(city):
    """building C's near side wall as tools/naruto_roof.py paints it (its planks, its coping carried round): f(x, y, top)"""
    X0 = NR.X0; LUM = NR.LUM
    Lf = city[160:211, 1067:1121, :3] @ LUM + 1.0
    Lp = np.concatenate([Lf[:1].repeat(4, 0), Lf, Lf[-1:].repeat(4, 0)]); cs = np.concatenate([np.zeros((1, Lf.shape[1])), Lp.cumsum(0)])
    gr = np.clip(Lf / ((cs[9:] - cs[:-9]) / 9.0), 0.8, 1.2); gr = np.concatenate([gr, gr[::-1]])
    cf = city[NR.CTOP:NR.CTOP + 3, 1067:X0 - 1, :3]; Lcf = cf @ LUM + 1.0
    ok = Lcf > 0.6 * np.median(Lcf, 1, keepdims=True)
    crow = np.array([cf[j][ok[j]].mean(0) for j in range(3)]); mrow = np.array([Lcf[j][ok[j]].mean() for j in range(3)])
    gcf = np.clip(Lcf / mrow[:, None], 0.7, 1.4); ncf = gcf.shape[1]
    stc = NR.streaks(NR.XE - X0 + 1, 13, 0.2, 30)

    def f(x, y, top):
        u = (x - X0) % (2 * ncf); u = ncf - 1 - u if u < ncf else u - ncf
        j = y - NR.CTOP
        if j < 3: return crow[j] * gcf[j, u] * NR.CCOP_K
        drift = (1.0 + 0.1 * max(0.0, 1.0 - (j - 4) / 8.0) if j > 3 else 1.0) * (1.0 - 0.3 * max(0.0, 1.0 - (top - 1 - y) / 15.0))
        return NR.CSIDE * NR.plank(x - X0, y, gr) * drift * (NR.SHADE if j == 3 else 0.82 if j - 3 < stc[x - X0] else 1.0)
    return f


def roof(city, unlit, sun, box):
    """the roof's edge redrawn on the floor's rays, what it no longer covers (the sky, C's wall), the low sun's glint moved
    with the lip, the right house's tiles against the sky, the garden set on the new coping; returns the garden's record"""
    x0, y0, x1, y1 = box
    c0, u0, s0 = city.copy(), unlit.copy(), sun.copy()
    # 1. the old garden's leaves out: what each covered (roof_sway_before.webp's blocks), over the old coping
    sw_ = np.asarray(Image.open(os.path.join(EDITS, 'roof_sway_before.webp')).convert('RGBA')).astype(float)
    H = sw_.shape[0] // 3; W = sw_.shape[1]; bx, by = SWAY_AT
    for x in range(max(bx, NR.X0 + 6), min(bx + W, NR.XC)):
        for y in range(by, min(by + H, NR.front_rows(x)[0])):
            city[y, x] = sw_[y - by, x - bx]; unlit[y, x] = sw_[H + y - by, x - bx]
    # 2. what the old edge covered and the new one does not: C's side wall under its coping, else the sky
    cw = c_wall(c0)
    eave = {1296 + i: e for i, e in enumerate(NR.EAVE)}
    for x in range(X0R, XE):
        ct = edge_rows(x)[0]
        for y in range(old_top(x), ct):
            if x >= 1296 and y >= eave[x]: continue                 # (the right house's tiles)
            if y >= NR.CTOP and ct > NR.CTOP and x < NR.XC:
                c = cw(x, y, ct); city[y, x, :3] = c; unlit[y, x, :3] = c; city[y, x, 3] = unlit[y, x, 3] = 255
            else:
                city[y, x] = 0; unlit[y, x] = 0
            sun[y, x] = 0
    # the right house's tiles now against the sky over the near side: a clean stair, the sky's light on their top
    for x in range(1297, XE):
        e = eave[x]; ct = edge_rows(x)[0]
        if e >= ct or old_top(x) >= e: continue                         # (against the near side still, or lit already)
        ee = min(e, eave[x - 1])
        for y in range(ee, e): city[y, x] = c0[e, x]; unlit[y, x] = u0[e, x]
        for lay, src in ((city, c0), (unlit, u0)):
            lay[ee, x, :3] = src[e, x, :3] * 0.3 + NR.EAVE_LIT * 0.7; lay[ee, x, 3] = 255
    # 3. the edge: the coping, the parapet's face, the lip (over the pillar the face is the pillar's own, cleaned with it),
    # round the near corner level: the near side's coping, its face, the slab's end over the balcony and the near wall
    n = grain(city.shape[:2], 41)
    def put(x, y, c, lamp=True):
        k = 1 + n[y, x] * 0.04
        la = NR.lamp(x, y) if lamp else 0.0
        city[y, x, :3] = c * k * (1 + la); unlit[y, x, :3] = c * k; city[y, x, 3] = unlit[y, x, 3] = 255; sun[y, x] = 0
    for x in range(X0R, XE):
        ct, pf, lt, lb = edge_rows(x); near = x >= XPN
        bot = eave[x] if x >= 1296 else 10 ** 6                         # (the right house's eave in front, from x 1296)
        kk = NEAR_K if near else 1.0
        for y in range(ct, min(pf, bot)):
            i = y - ct; m = pf - ct
            c = RC['cop_top'] if i == 0 else RC['cop_low'] if i == m - 1 else RC['cop']
            put(x, y, c * kk * (0.7 if x == X0R else 1.0))
        if x < XPF: continue
        lo = lb if x < XNS else bot
        for y in range(pf, min(lo, bot)):
            j = y - pf
            if near and (y < lt or x >= XNS):                           # (the near side's face, its wall over the eave)
                c = RC['npar'] * (1.25 - 0.25 * min(1.0, j / 18.0))
            elif y < lt:
                c = RC['par']
            else:
                i = y - lt; m = lb - lt
                if near:
                    c = RC['slab_top'] if i == 0 else RC['slab_low'] if i == m - 1 else RC['slab']
                else:
                    c = RC['lip_top'] if i == 0 else RC['lip_arris'] if i == m - 1 else RC['lip_low'] if i >= m - 3 else RC['lip']
            put(x, y, c * (0.5 if j == 0 else 1.0))
        if XWN <= x < XNS:                                              # (the slab's shadow on the near wall under it)
            for lay in (city, unlit): lay[lb, x, :3] *= 0.55
    # 4. the low sun's glint on the lip's far end (street_sun), moved with the lip, its colours kept
    bs = np.asarray(Image.open(os.path.join(EDITS, 'narufloor_before_sun.webp')).convert('RGB')).astype(float)
    bc = np.asarray(Image.open(os.path.join(EDITS, 'narufloor_before_city.webp')).convert('RGBA')).astype(float)
    bu = np.asarray(Image.open(os.path.join(EDITS, 'narufloor_before_unlit.webp')).convert('RGBA')).astype(float)
    for x in range(int(XPF), 1175):
        ct, pf, lt, lb = edge_rows(x); dy = lt - NR.ry(x, NR.LIPV)
        for y in range(140, 190):
            if bs[y - y0, x - x0, 0] <= 0: continue
            ny = y + dy
            if lt <= ny < lb:
                city[ny, x] = bc[y - y0, x - x0]; unlit[ny, x] = bu[y - y0, x - x0]; sun[ny, x] = bs[y - y0, x - x0]
    # 5. the garden on the new coping (tools/naruto_roof.py's own plants, clumps and light; the shrubs and the hedge in their
    # planters along the parapet: on its new coping); recorded for the wind (roof_sway.webp)
    rec = {'calls': [], 'clumps': [], 'clip': None}
    keep = (NR.front_rows, NR.foliage)
    NR.front_rows = lambda x: edge_rows(x)[:3]
    plain = keep[1]

    def foliage(clumps, rank, seed, clip, *a, **k):
        if not rec['calls']: rec['under'] = (city.copy(), unlit.copy())       # (the trunk and limbs in, no leaf yet)
        px = plain(clumps, rank, seed, clip, *a, **k)
        rec['calls'].append((px, RS.foliage_own(clumps, rank, seed, clip, *a, **k))); rec['clumps'].append(list(clumps))
        rec['clip'] = clip
        return px
    NR.foliage = foliage
    try:
        NR.garden(Lay(city, unlit, sun))
    finally:
        NR.front_rows, NR.foliage = keep
    return rec


def downpipes(city, unlit, box, sign):
    """the far downpipe on the pillar's face: from a rain head under the parapet's outlet (at the roof's level, over the lip's
    first row) straight down behind the sign, round, lit from the left and the front, a bracket every PIPE_STEP rows; the near
    corner's downpipe (tools/naruto_roof.py's) from under the slab's end, its brackets evened out"""
    a, b = PIPE
    cx = (a + b) / 2.0
    lt = edge_rows(a + 3)[2]                                            # (the roof's level at the pipe: the lip's top)
    rh = (lt - 1, lt + 6)                                               # the rain head's rows
    drawn = set()
    def put(x, y, c, k_un=PIPE_UNLIT):
        city[y, x, :3] = c; unlit[y, x, :3] = c * k_un; city[y, x, 3] = unlit[y, x, 3] = 255; drawn.add((x, y))
    # the outlet through the parapet just over the roof's level: a dark mouth, its lit sill
    for y in range(lt - 5, lt - 2):
        for x in range(a + 2, a + 5):
            put(x, y, np.array((2.0, 4.0, 8.0)) if y < lt - 3 else PIPE_C * 0.9)
    # the rain head: a box wider than the pipe, its rim lit, its sides shaded, its funnel narrowing into the pipe
    for y in range(*rh):
        i = y - rh[0]; w = 5.5 if i < 4 else 4.5 if i < 5 else 3.5
        for x in range(int(np.floor(cx - w)), int(np.ceil(cx + w))):
            u = (x + 0.5 - (cx - w)) / (2 * w)
            k = 1.25 if i == 0 else (1.15 - 0.6 * u) * (0.8 if i >= 5 else 1.0)
            put(x, y, PIPE_C * k)
    # the pipe, its brackets (a lit strap's top, its dark band, its ear on the pillar's face)
    for x in range(a, b):
        for y in range(rh[1], sign[x]):
            c = PIPE_C * PIPE_K[x - a]
            j = (y - rh[1]) % PIPE_STEP
            if y - rh[1] >= PIPE_STEP // 2 and j == PIPE_STEP // 2: c = c * 1.3
            elif y - rh[1] >= PIPE_STEP // 2 and j == PIPE_STEP // 2 + 1: c = c * 0.5
            put(x, y, c)
    for y in range(rh[1] + PIPE_STEP // 2, sign[a - 1], PIPE_STEP):
        put(a - 1, y, PIPE_C * 0.9); put(a - 1, y + 1, PIPE_C * 0.4)
    # the near corner's downpipe: from the slab's end down to the box over the awning, its brackets every CPIPE[2] rows
    ca, cb, st = CPIPE
    lb = edge_rows(ca)[3]
    for x in range(ca, cb):
        col = np.median(city[100:300, x, :3], 0); colu = np.median(unlit[100:300, x, :3], 0)
        for y in range(lb, 312):
            j = (y - lb) % st; k = 1.25 if j == 0 else 0.55 if j == 1 else 1.0
            if y - lb < 2: k = (1.25, 0.55)[y - lb]
            city[y, x, :3] = col * k; unlit[y, x, :3] = colu * k; drawn.add((x, y))
    return drawn


def sway(city, unlit, rec):
    """the garden's wind data (assets/roof_sway.webp, street.js ROOF): tools/roof_sway.py's blocks for the garden as set on
    the new coping; returns its box"""
    LUM = NR.LUM; under = rec['under']
    mass = {}; clump = {}
    for m, (px, own) in enumerate(rec['calls']):
        for q in px: mass[q] = m + 1; clump[q] = own[q]
    xs = [q[0] for q in mass]; ys = [q[1] for q in mass]
    x0, y0 = min(xs) - 3, max(0, min(ys) - 3); x1, y1 = max(xs) + 4, max(ys) + 4
    W, H = x1 - x0, y1 - y0
    fin = [np.clip(np.round(a), 0, 255) for a in (city, unlit)]
    und = [f.copy() for f in fin]
    for q in mass:                                                      # (what each leaf covers)
        x, y = q
        for u, src in zip(und, under): u[y, x] = np.clip(np.round(src[y, x]), 0, 255)
    out = np.zeros((3 * H, W, 4), np.uint8)
    out[0:H] = und[0][y0:y1, x0:x1]; out[H:2 * H] = und[1][y0:y1, x0:x1]
    clip = rec['clip']
    L = fin[0][:, :, :3] @ LUM / 255.0; Lu = fin[1][:, :, :3] @ LUM / 255.0
    ext = {}
    for q, m in mass.items():
        e = ext.setdefault(m, [1e9, -1e9, 1e9, -1e9]); e[0] = min(e[0], q[0]); e[1] = max(e[1], q[0]); e[2] = min(e[2], q[1]); e[3] = max(e[3], q[1])
    ctop = {}
    for q, m in mass.items():
        if m > 1: key = (m, clump[q], q[0]); ctop[key] = min(ctop.get(key, 1e9), q[1])
    for y in range(y0, y1):
        for x in range(x0, x1):
            o = out[2 * H + y - y0, x - x0]
            o[3] = 255; o[2] = 255 if clip(x, y) else 0
            m = mass.get((x, y))
            if not m: continue
            if L[y, x] - Lu[y, x] > RS.LAMP_LIT: continue
            k = clump[(x, y)]
            if m == 1:
                cx, cy, rx, ry = rec['clumps'][0][k]
                up = np.clip((100 - y) / (100 - ext[1][2]), 0, 1); out_ = np.clip(abs(x - cx) / rx, 0, 1)
                f = (0.35 + 0.65 * up) * (0.75 + 0.25 * out_)
            else:
                d = y - ctop[(m, k, x)]
                f = max(0.0, 1.0 - d / 4.0) * (0.8 if m == 2 else 0.6 * float(np.clip((y - RS.HEDGE_CALM) / 4.0, 0, 1)))
            o[0] = 16 * m + k; o[1] = int(round(255 * f))
    return out, (x0, y0, W, H)


def draw(city, unlit, box=BOX, write=True):
    """The zone (redraw_zones.py): the layers changed in place (whole-scene float RGBA); the window's overlay, the garden's
    wind data and the low sun's share (street_sun) written; returns what changed in box."""
    x0, y0, x1, y1 = box
    sun = np.asarray(Image.open(os.path.join(ASSETS, 'street_sun.webp')).convert('RGB')).astype(float)
    sun[y0:y1, x0:x1] = np.asarray(Image.open(os.path.join(EDITS, 'narufloor_before_sun.webp')).convert('RGB')).astype(float)
    before = city[y0:y1, x0:x1].copy(), unlit[y0:y1, x0:x1].copy()
    O0, U0 = before[0][..., :3].copy(), before[1][..., :3].copy()
    rec = roof(city, unlit, sun, box)
    O, U = city[y0:y1, x0:x1, :3].copy(), unlit[y0:y1, x0:x1, :3].copy()
    lip = lip_bottom(box); sign = sign_top(box)
    R, T, P = roles(box, lip, sign)
    new, unew, done = paint(O, U, box, R, T, P, O0, U0)
    city[y0:y1, x0:x1, :3][done] = np.clip(np.round(new[done]), 0, 255)
    unlit[y0:y1, x0:x1, :3][done] = np.clip(np.round(unew[done]), 0, 255)
    city[y0:y1, x0:x1, 3][done] = 255; unlit[y0:y1, x0:x1, 3][done] = 255
    sun[y0:y1, x0:x1][done] = 0
    for x in range(PILLAR[0], PILLAR[1]):                   # (the coping's shadow on the pillar's face under it)
        y = edge_rows(x)[1]
        for lay in (city, unlit): lay[y, x, :3] = np.round(lay[y, x, :3] * 0.5)
    for (x, y) in downpipes(city, unlit, box, sign): sun[y, x] = 0
    for lay in (city, unlit): lay[y0:y1, x0:x1] = np.clip(np.round(lay[y0:y1, x0:x1]), 0, 255)
    mask, lit = overlay(R, T, P, box)
    sw_, sbox = sway(city, unlit, rec)
    if write:
        save(mask, os.path.join(ASSETS, 'window_panes.webp'))
        save(lit, os.path.join(ASSETS, 'window_lit_ukki.webp'))
        save(sw_, os.path.join(ASSETS, 'roof_sway.webp'))
        Image.fromarray(np.clip(np.round(sun), 0, 255).astype(np.uint8), 'RGB').save(
            os.path.join(ASSETS, 'street_sun.webp'), 'WEBP', lossless=True, quality=100, method=6, exact=True)
    print('naruto_floor: roof_sway box', sbox)
    draw.last = (R, T, P, mask, lit, sun, sw_, sbox)
    return (city[y0:y1, x0:x1] != before[0]).any(-1) | (unlit[y0:y1, x0:x1] != before[1]).any(-1)


def save(a, path):
    Image.fromarray(np.round(np.clip(a, 0, 255)).astype(np.uint8), 'RGBA').save(path, 'WEBP', lossless=True, quality=100, method=6, exact=True)


def preview(out):
    """the zone drawn on the layers as they are (or as given), its crops before and after, lit and not, x4"""
    os.makedirs(out, exist_ok=True)
    L = {t: np.asarray(Image.open(os.path.join(ASSETS, f)).convert('RGBA')).astype(float)
         for t, f in (('city', 'layer_city_off.webp'), ('unlit', 'street_unlit.webp'))}
    A = {t: a.copy() for t, a in L.items()}             # (the zone's input: its before crop over the sign's line and,
    x0, y0, x1, y1 = BOX                                # right of the corner, over the rooftop unit; under them what
    sg = sign_top(BOX)                                  # the zones before it leave)
    keep = np.array([[y < (sg[x] if x < XWN else 160) for x in range(x0, x1)] for y in range(y0, y1)])
    for t in ('city', 'unlit'):
        b = np.asarray(Image.open(os.path.join(EDITS, f'narufloor_before_{t}.webp')).convert('RGBA')).astype(float)
        A[t][y0:y1, x0:x1][keep] = b[keep]
    draw(A['city'], A['unlit'], BOX, write=False)
    R, T, P, mask, lit = draw.last[:5]
    old_m = np.asarray(Image.open(os.path.join(ASSETS, 'window_panes.webp')).convert('RGBA')).astype(float)
    old_l = np.asarray(Image.open(os.path.join(ASSETS, 'window_lit_ukki.webp')).convert('RGBA')).astype(float)
    B = (1100, 0, 1390, 400)
    def crop(a): return np.clip(a[B[1]:B[3], B[0]:B[2], :3], 0, 255).copy()
    def add(z, m, l, at):
        ax, ay = at; g = (m[..., 3] >= 128)[..., None]
        hh, ww = m.shape[:2]
        z[ay - B[1]:ay - B[1] + hh, ax - B[0]:ax - B[0] + ww] += np.where(g, l[..., :3], 0)
        return np.clip(z, 0, 255)
    shots = {'city_before': crop(L['city']), 'city_after': crop(A['city']),
             'unlit_before': crop(L['unlit']), 'unlit_after': crop(A['unlit']),
             'lit_before': add(crop(L['city']), old_m, old_l, WL[:2]), 'lit_after': add(crop(A['city']), mask, lit, WL[:2])}
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
