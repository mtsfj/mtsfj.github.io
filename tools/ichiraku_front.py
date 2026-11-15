#!/usr/bin/env python3
"""Ichiraku's front, redone from scratch (the owner: "Faut refaire Ichiraku, la devanture, proprement"): the entrance under
the approved sign, its two lamps and its lattice transom, modelled in the street's camera (F 1400, VP (700, 615), the eye at
1.5 m: tools/interieur.py, tools/ichiraku_interior.py) and drawn on the pixel grid, face by face, edge by edge.

    (a module: tools/redraw_zones.py's zone 'front' calls draw(), before the zone 'vitrine' lays the room in the glass)
    python3 tools/ichiraku_front.py --guide DIR    the blockout (each face its flat tone) in the street at 22 h: the input of
                                                   the painted draft (tools/src/edits/front_draft_in.webp)
    python3 tools/ichiraku_front.py --preview DIR  the front drawn on the layers as they are, x4 (nothing written)

The facade is the plane X = X_F (5.53 m right of the eye, along the street Z); the doorway between its two jambs runs from
Z_L to Z_R. From the street inwards:
- the step: a stone slab on the sidewalk before the doorway (STEP: its top, its depth, how far it overruns the doorway), its
  top in the street lamp's light, its riser in shade, a contact shade and the wet grime at its foot;
- the sill: the doors' wooden threshold on the step (SILL), its top worn lighter;
- the frame: the jambs' casing on the facade (JAMB: its width) and the head beam over the doorway (HEAD), dark wood; the
  far jamb's reveal (the doors stand REVEAL behind the facade);
- the doors in their plane, X_F + REVEAL: a narrow fixed glazed panel on the left and the sliding door (SPLIT: where they
  meet, left of where the customers sit, so that no stile crosses anyone), each a wooden frame (STILE, the rails RAILS) round
  one clear pane, a wooden kickboard (KICK) below it that hides the stools and the people's legs; the glass itself is laid
  by the zone 'vitrine' (tools/ichiraku_interior.py, its panes: panes() here);
- the noren is a sprite (street.js IRNR, tools/redraw_noren.py), hung outside on its pole in front of the head beam.
The faces take their materials from the painted draft (tools/src/edits/front_draft.webp, asked of the blockout in the
street at 22 h, R28): each face's picture taken where the draft paints it, brought to the painting's palette and its light.
"""
import os
import sys
import numpy as np
from PIL import Image

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ichiraku_interior as R

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDITS = os.path.join(ROOT, 'tools', 'src', 'edits')
F, VX, VY, EYE, X_F = R.F, R.VX, R.VY, R.EYE, R.X_F

Z_L, Z_R = F * X_F / (1160 - VX), F * X_F / (1224 - VX)   # the doorway: its far and near jambs' inner faces (m along the street)
JAMB = (0.20, 0.20)                  # the casing's width on the facade, far and near (m)
HEAD = (2.66, 2.94)                  # the head beam: its underside and its top, under the lattice transom (m)
REVEAL = 0.04                        # the doors behind the facade (m)
SPLIT = 16.45                        # where the fixed panel meets the sliding door (Z, m): left of the customers
STILE = 0.045                        # a stile's width (m)
RAILS = dict(bottom=(0.15, 0.25), mid=(0.95, 1.01), top=(2.60, 2.66))   # the doors' rails (from, to: m)
STEP = dict(top=0.12, out=0.40, over=0.12)   # the step: its top, how far it comes out of the facade, how far past the jambs
SILL = dict(top=0.15, out=0.03, inn=0.10)    # the sill: its top, out of the facade, in behind it
BOX = (1118, 484, 1240, 768)         # the zone (redraw_zones.py 'front')
SS = 4                               # (each pixel taken on SS x SS points)


def proj(X, Z, h):
    """a point of the street (X across, Z along, h up, m) in the picture (x, y)"""
    return VX + F * X / Z, VY + (EYE - h) * F / Z


def quad_vertical(X, Z0, Z1, h0, h1):
    """a vertical face along the street (constant X), from Z0 to Z1 and h0 to h1: its corners in the picture"""
    return [proj(X, Z0, h0), proj(X, Z1, h0), proj(X, Z1, h1), proj(X, Z0, h1)]


def quad_across(Z, X0, X1, h0, h1):
    """a vertical face across the street (constant Z): its corners"""
    return [proj(X0, Z, h0), proj(X1, Z, h0), proj(X1, Z, h1), proj(X0, Z, h1)]


def quad_flat(h, X0, X1, Z0, Z1):
    """a horizontal face (constant h): its corners"""
    return [proj(X0, Z0, h), proj(X1, Z0, h), proj(X1, Z1, h), proj(X0, Z1, h)]


def faces():
    """the front's faces, far to near (the nearer drawn over): (name, corners, (u, v) of each corner on the face)"""
    XD = X_F + REVEAL
    zl0, zr0 = Z_L + JAMB[0], Z_R - JAMB[1]
    out = []
    # the doors: the fixed panel (Z_L .. SPLIT) and the sliding door (SPLIT .. Z_R), their frames and kickboards
    for name, (za, zb) in (('panel', (Z_L, SPLIT)), ('door', (SPLIT, Z_R))):
        b0, b1 = RAILS['bottom']; m0, m1 = RAILS['mid']; t0, t1 = RAILS['top']
        out.append((name + '_kick', quad_vertical(XD, za, zb, b1, m0)))
        out.append((name + '_rail_b', quad_vertical(XD, za, zb, b0, b1)))
        out.append((name + '_rail_m', quad_vertical(XD, za, zb, m0, m1)))
        out.append((name + '_rail_t', quad_vertical(XD, za, zb, t0, t1)))
        out.append((name + '_stile_a', quad_vertical(XD, za, za - STILE, b0, t1)))
        out.append((name + '_stile_b', quad_vertical(XD, zb + STILE, zb, b0, t1)))
    # the far jamb's reveal (its inner face, seen from the street), the casing, the head beam
    out.append(('reveal', quad_across(Z_L, X_F, XD, SILL['top'], HEAD[0])))
    out.append(('jamb_far', quad_vertical(X_F, zl0, Z_L, 0.0, HEAD[1])))
    out.append(('jamb_near', quad_vertical(X_F, Z_R, zr0, 0.0, HEAD[1])))
    out.append(('head', quad_vertical(X_F, zl0, zr0, HEAD[0], HEAD[1])))
    out.append(('head_under', quad_flat(HEAD[0], X_F, XD, Z_L, Z_R)))
    # the sill, then the step before it
    out.append(('sill_top', quad_flat(SILL['top'], X_F - SILL['out'], XD + 0.06, Z_L, Z_R)))
    out.append(('sill_front', quad_vertical(X_F - SILL['out'], Z_L, Z_R, STEP['top'], SILL['top'])))
    zs0, zs1 = zl0 + STEP['over'], zr0 - STEP['over']
    Xs = X_F - STEP['out']
    out.append(('step_top', quad_flat(STEP['top'], Xs, X_F, zs0, zs1)))
    out.append(('step_front', quad_vertical(Xs, zs0, zs1, 0.0, STEP['top'])))
    out.append(('step_end', quad_across(zs1, Xs, X_F, 0.0, STEP['top'])))
    return out


def panes():
    """the glass of the two doors (their plane X_F + REVEAL): (Z from, Z to, h from, h to) each"""
    m1, t0 = RAILS['mid'][1], RAILS['top'][0]
    return [(Z_L - STILE, SPLIT + STILE, m1, t0), (SPLIT - STILE, Z_R + STILE, m1, t0)]


def raster(corners, shape, box):
    """the pixels a face covers (half its points at least), in the box"""
    x0, y0, x1, y1 = box; H, W = y1 - y0, x1 - x0
    o = (np.arange(SS) + 0.5) / SS
    ys, xs = np.mgrid[0:H * SS, 0:W * SS]
    px = x0 + (xs // SS) + o[xs % SS]; py = y0 + (ys // SS) + o[ys % SS]
    inside = np.ones(px.shape, bool); c = np.array(corners, float); n = len(c)
    area = sum(c[i, 0] * c[(i + 1) % n, 1] - c[(i + 1) % n, 0] * c[i, 1] for i in range(n))
    for i in range(n):
        ax, ay = c[i]; bx, by = c[(i + 1) % n]
        cr = (bx - ax) * (py - ay) - (by - ay) * (px - ax)
        inside &= (cr >= 0) if area > 0 else (cr <= 0)
    return inside.reshape(H, SS, W, SS).mean((1, 3)) >= 0.5


def glass_mask(box=BOX):
    """the panes' pixels (in the box): what the zone 'vitrine' fills with the room"""
    XD = X_F + REVEAL; m = np.zeros((box[3] - box[1], box[2] - box[0]), bool)
    for za, zb, h0, h1 in panes():
        m |= raster(quad_vertical(XD, za, zb, h0, h1), None, box)
    for name, c in faces():                  # (less what stands in front of the doors' plane: the casing, the reveal, the head)
        if not name.startswith(('panel', 'door')): m &= ~raster(c, None, box)
    return m


CROP = (1050, 400, 1310, 790)        # the drafts' frame in the street (x0, y0, x1, y1): front_draft_in.webp, 1024 x 1536 of it
DRAFTS = {'lit': ('front_draft.webp', None),         # (the shop open, at 22 h)
          'shut': ('front_draft_shut.webp', (1.02, 9, 13))}   # (the shop shut, relit from the lit one: its scale and shift on it)
REFS = [(1095, 525, 1140, 735), (1240, 520, 1262, 735), (1060, 772, 1300, 790)]   # (the walls beside the entrance and the
                                     # pavement: where the drafts are brought to the street's own tones, far from the lamps)
CUT_BLUE = 0.9                       # (in the power cut: the front in the cut's own blue, the facade's beside it, so much of it)
LIP = (16.0, 18.0, 24.0)             # (the frame's inner lip against the glass: the street's light added)
CONTACT = (0.72, 0.86)               # (the step's foot on the pavement: the rows just under it darkened so much, then so much)


def draft(kind):
    """a draft at the street's pixels over CROP (each pixel the mean of its footprint), registered on the lit one"""
    name, reg = DRAFTS[kind]
    a = np.asarray(Image.open(os.path.join(EDITS, name)).convert('RGB')).astype(float)
    if reg:
        from scipy.ndimage import map_coordinates
        s, dx, dy = reg; H, W = a.shape[:2]; Y, X = np.mgrid[0:H, 0:W]
        yb = (Y - H / 2) * s + H / 2 + dy; xb = (X - W / 2) * s + W / 2 + dx
        a = np.stack([map_coordinates(a[..., c], [yb, xb], order=1, mode='nearest') for c in range(3)], -1)
    x0, y0, x1, y1 = CROP
    return np.stack([np.asarray(Image.fromarray(a[..., c].astype(np.float32), 'F').resize((x1 - x0, y1 - y0), Image.BOX)) for c in range(3)], -1)


def tones(d, layer):
    """the draft brought to the layer's tones: each channel's quantiles on the walls and the pavement (REFS) matched"""
    x0, y0 = CROP[:2]; src, dst = [], []
    for a, b, c, e in REFS:
        src.append(d[b - y0:e - y0, a - x0:c - x0].reshape(-1, 3)); dst.append(layer[b:e, a:c, :3].reshape(-1, 3))
    src, dst = np.concatenate(src), np.concatenate(dst); q = np.linspace(2, 98, 25)
    out = np.empty_like(d)
    for c in range(3):
        qs, qd = np.percentile(src[:, c], q), np.percentile(dst[:, c], q)
        out[..., c] = np.interp(d[..., c], qs, qd, left=None, right=None)
        hi = d[..., c] > qs[-1]; out[..., c][hi] = qd[-1] + (d[..., c][hi] - qs[-1]) * (qd[-1] - qd[-2] + 1e-6) / (qs[-1] - qs[-2] + 1e-6)
    return np.clip(out, 0, 255)


def erode(m):
    e = m.copy(); e[1:] &= m[:-1]; e[:-1] &= m[1:]; e[:, 1:] &= m[:, :-1]; e[:, :-1] &= m[:, 1:]
    return e


def fill(d, m, smooth):
    """a face's pixels from the draft, taken inside it only (its edge from its inside: nothing of a neighbour bleeds in); a
    thin member (smooth) one even tone along it, a broad face its texture"""
    from scipy.ndimage import gaussian_filter
    inner = erode(m) if erode(m).sum() >= 0.3 * m.sum() else m
    sig = 2.0 if smooth else 0.8
    w = gaussian_filter(inner.astype(float), sig)
    acc = np.stack([gaussian_filter(d[..., c] * inner, sig) for c in range(3)], -1)
    sm = acc / np.maximum(w, 1e-6)[..., None]
    if smooth: return sm
    out = np.where(inner[..., None], d, sm)
    return out


THIN = ('stile', 'rail', 'jamb', 'reveal', 'sill_front', 'head_under')


def paint(kind, layer, box=BOX):
    """the front in one light (kind: lit, shut), on the layer's tones: (colours over the box, which pixels)"""
    x0, y0, x1, y1 = box; cx0, cy0 = CROP[:2]
    d = tones(draft(kind), layer)[y0 - cy0:y1 - cy0, x0 - cx0:x1 - cx0]
    out = np.zeros((y1 - y0, x1 - x0, 3)); done = np.zeros(out.shape[:2], bool)
    for name, c in faces():
        m = raster(c, None, box)
        out[m] = fill(d, m, any(t in name for t in THIN))[m]; done |= m
    g = glass_mask(box); done &= ~g
    lip = np.zeros_like(g); lip[1:] |= g[:-1]; lip[:-1] |= g[1:]; lip[:, 1:] |= g[:, :-1]; lip[:, :-1] |= g[:, 1:]
    lip &= done                                  # (the frame's inner lip against the glass: catching the street's light)
    out[lip] = np.clip(out[lip] + np.array(LIP), 0, 255)
    return out, done


def contact(box=BOX):
    """the pavement rows just under the step's foot (its riser and its near end): (first row, second row) masks"""
    zl0, zr0 = Z_L + JAMB[0], Z_R - JAMB[1]; zs0, zs1 = zl0 + STEP['over'], zr0 - STEP['over']; Xs = X_F - STEP['out']
    foot = raster(quad_vertical(Xs, zs0, zs1, 0.0, STEP['top']), None, box) | raster(quad_across(zs1, Xs, X_F, 0.0, STEP['top']), None, box)
    step = foot | raster(quad_flat(STEP['top'], Xs, X_F, zs0, zs1), None, box)
    one = np.zeros_like(foot); one[1:] = foot[:-1]; one &= ~step
    two = np.zeros_like(foot); two[2:] = foot[:-2]; two &= ~step & ~one
    side = np.zeros_like(foot); side[:, 1:] = foot[:, :-1]; side &= ~step & ~one & ~two      # (and the pixel right of the end)
    return one | side, two


def draw(city, unlit, box=BOX):
    """the zone 'front' (tools/redraw_zones.py): the front on the layers as the zones before it leave them, the power cut's
    at the walls' own ratio and in the cut's blue (cut_blue); the pavement under the step's foot in its contact shade; returns
    what changed"""
    x0, y0, x1, y1 = box
    was = city[y0:y1, x0:x1, :3].copy(), unlit[y0:y1, x0:x1, :3].copy()
    lit, m = paint('lit', city, box); shut, _ = paint('shut', city, box)
    ratio = np.array([np.median([np.median(unlit[b:e, a:c, k] / np.maximum(city[b:e, a:c, k], 1)) for a, b, c, e in REFS[:2]]) for k in range(3)])
    city[y0:y1, x0:x1, :3][m] = np.round(lit[m])
    blue = cut_blue(unlit)
    unlit[y0:y1, x0:x1, :3][m] = np.round(np.clip(blue(shut[m] * ratio), 0, 255))
    one, two = contact(box)
    for mm, k in ((one, CONTACT[0]), (two, CONTACT[1])):
        for L in (city, unlit): L[y0:y1, x0:x1, :3][mm] = np.round(L[y0:y1, x0:x1, :3][mm] * k)
    transom_cut(city, unlit, blue)               # (the lattice transom dark in the power cut; the door zone's patch carries it)
    wet_ground(); ground_light()                 # (the wet paving before the front, the shop's light on it)
    ch = np.zeros(city.shape[:2], bool)
    ch[y0:y1, x0:x1] = (np.abs(city[y0:y1, x0:x1, :3] - was[0]).max(-1) > 0) | (np.abs(unlit[y0:y1, x0:x1, :3] - was[1]).max(-1) > 0)
    return ch


TRANSOM_CUT = 0.12                   # (in the power cut, the lattice transom's lit pixels: so much of their light left, in the cut's blue)
WET_BOX = (1108, 734, 1264, 816)     # the wet ground before the front (x0, scene row 0, x1, row 1): wet.webp from row 600
WET = dict(near=150.0, far=70.0, reach=1.8, puddle=110.0, step=36.0)   # (wetness at the step's foot, 1.8 m out; a shallow
                                     # puddle's stillness; the step's own faces: as the pavement was)
GL = dict(box=(820, 716, 536, 100), fade=(830, 900), warm=(255.0, 178.0, 104.0), peak=46.0, n=6, rough=0.12, gloss=190.0,
          sheen=(255.0, 156.0, 72.0))
                                     # the shop's light on the wet ground (assets/gl_ramen_wet.webp, street.js GL 'ramen_wet': its
                                     # box, faded in over these columns on its left, short of the road marking's; its tone, at
                                     # most so much at the step's foot; the panes sampled n x n; the wet paving's sheen: its
                                     # roughness (Beckmann), at most so much, its tone)


LUM = np.array([0.299, 0.587, 0.114])


def cut_blue(unlit):
    """the power cut's own grade (the owner: « bleue »): a colour to the hue of the facade beside the entrance in the cut layer
    (REFS[0]), at its own luminance; CUT_BLUE of it"""
    a, b, c, e = REFS[0]
    w = unlit[b:e, a:c, :3].reshape(-1, 3).mean(0); hue = w / (w @ LUM)
    return lambda px: (1 - CUT_BLUE) * px + CUT_BLUE * (px @ LUM)[..., None] * hue


def transom_cut(city, unlit, blue):
    """the lattice transom over the doorway in the power cut: dark and blue like the rest of the shop (the door zone's first
    part; its lit pixels, warm and bright in the lit layer, at TRANSOM_CUT of their light; all of it in the cut's blue)"""
    import redraw_zones as RZ
    zb = RZ.ZONES['door']['box']; poly = RZ.ZONES['door']['parts'][0]['poly']
    m = raster([(float(x), float(y)) for x, y in poly], None, zb)
    px = city[zb[1]:zb[3], zb[0]:zb[2], :3]
    lit = m & (px[..., 0] > px[..., 2] + 15) & (px @ LUM > 40)
    sub = unlit[zb[1]:zb[3], zb[0]:zb[2], :3]; sub[lit] = px[lit] * TRANSOM_CUT
    sub[m] = np.round(np.clip(blue(sub[m]), 0, 255))
    return int(lit.sum())


def step_faces(box):
    """the step's faces' pixels in a box (its top, its riser, its end)"""
    m = np.zeros((box[3] - box[1], box[2] - box[0]), bool)
    for name, c in faces():
        if name.startswith('step'): m |= raster(c, None, box)
    return m


def wet_ground():
    """the wet paving before the front (assets/wet.webp, wet_mirror.webp in WET_BOX, from their before copies): wetter toward
    the step, a shallow still puddle at its foot, the step's own faces as they were; the mirror line at the step's foot, so the
    lit front and its step stand in the water. The same bytes each run"""
    from scipy.ndimage import gaussian_filter
    x0, r0, x1, r1 = WET_BOX
    pw, pm = os.path.join(ROOT, 'assets', 'wet.webp'), os.path.join(ROOT, 'assets', 'wet_mirror.webp')
    wet = np.asarray(Image.open(pw).convert('RGB')).copy(); mir = np.asarray(Image.open(pm).convert('RGB')).copy()
    wb = np.asarray(Image.open(os.path.join(EDITS, 'front_wet_before.webp')).convert('RGB')).astype(float)
    mb = np.asarray(Image.open(os.path.join(EDITS, 'front_mirror_before.webp')).convert('RGB')).copy()
    box = (x0, r0, x1, r1); st = step_faces(box)
    ys, xs = np.mgrid[r0:r1, x0:x1] + 0.5
    Z = F * EYE / np.maximum(ys - VY, 1e-3); X = (xs - VX) * Z / F          # (the ground under each pixel)
    out = X_F - STEP['out'] - X                                               # (how far out of the step's riser, m)
    zl0, zr0 = Z_L + JAMB[0], Z_R - JAMB[1]
    along = np.clip(np.minimum(Z - (zr0 - 0.5), (zl0 + 0.5) - Z) / 0.6, 0, 1)   # (before the doorway, fading past it)
    k = np.clip(1 - out / WET['reach'], 0, 1) * along * (out >= -0.02)
    R = np.maximum(wb[..., 0], WET['far'] * along * (out >= -0.02) + (WET['near'] - WET['far']) * k)
    n = gaussian_filter(np.random.default_rng(71).normal(0, 1, R.shape), 2.0); n = (n - n.mean()) / n.std()
    pud = np.clip(1 - out / 0.9, 0, 1) * along * np.clip(0.4 + 0.6 * n, 0, 1) * (out >= 0)
    Bc = np.maximum(wb[..., 2], WET['puddle'] * pud)
    R = np.where(st, WET['step'], R); Bc = np.where(st, 0, Bc); G = np.where(st, 0, wb[..., 1])
    wet[r0 - 600:r1 - 600, x0:x1] = np.clip(np.round(np.stack([R, G, Bc], -1)), 0, 255).astype(np.uint8)
    # the mirror line: under the step's riser and end (their foot), the pavement mirrors about it
    cols = np.nonzero(st.any(0))[0]
    mir[:, x0:x1] = mb
    for j in cols:
        foot = r0 + int(np.nonzero(st[:, j])[0].max()) + 1; v = foot - 560
        mir[0, x0 + j] = (min(255, max(0, v)), 0, 0)
    Image.fromarray(wet, 'RGB').save(pw, 'WEBP', lossless=True, quality=100, method=6, exact=True)
    Image.fromarray(mir, 'RGB').save(pm, 'WEBP', lossless=True, quality=100, method=6, exact=True)


def ground_light():
    """the shop's warm light on the wet paving before it (assets/gl_ramen_wet.webp, all its own, beside the shop's older ground
    light gl_ramen.webp): the two panes as an area light (sampled n x n) on the ground in front of the step, falling off with
    distance and the angles; and their sheen in the wet paving (a rough mirror: the panes' reflection toward the eye, a streak
    under the doorway down to the frame's edge, broken into short dashes as the wet pass breaks its own); nothing on the step's
    own faces (their picture has its light)"""
    x0, y0, w, h = GL['box']
    out = np.zeros((h, w, 4))
    ys, xs = np.mgrid[y0:y0 + h, x0:x0 + w] + 0.5
    Z = F * EYE / np.maximum(ys - VY, 1e-3); X = (xs - VX) * Z / F
    XD = X_F + REVEAL; I = np.zeros(Z.shape); S = np.zeros(Z.shape); m2 = GL['rough'] ** 2
    vl = np.sqrt(X * X + Z * Z + EYE * EYE); Vx, Vz, Vh = -X / vl, -Z / vl, EYE / vl          # (toward the eye)
    for za, zb, h0, h1 in panes():
        for u in (np.arange(GL['n']) + 0.5) / GL['n']:
            for v in (np.arange(GL['n']) + 0.5) / GL['n']:
                pz, ph = za + (zb - za) * u, h0 + (h1 - h0) * v
                dx, dz = XD - X, pz - Z; d2 = dx * dx + dz * dz + ph * ph; dl = np.sqrt(d2)
                I += np.clip(dx, 0, None) * ph / d2 ** 2 * abs(zb - za) * (h1 - h0)   # (cos at the pane, cos on the ground)
                hx, hz, hh = dx / dl + Vx, dz / dl + Vz, ph / dl + Vh; hl = np.sqrt(hx * hx + hz * hz + hh * hh)
                ch = hh / hl; vh = (Vx * hx + Vz * hz + Vh * hh) / hl
                Dm = np.exp(-(1 - ch * ch) / (ch * ch * m2)) / (np.pi * m2 * ch ** 4)   # (the paving's facets: Beckmann)
                S += Dm * (0.02 + 0.98 * (1 - vh) ** 5) / (4 * Vh) * np.clip(dx, 0, None) / dl / d2 * abs(zb - za) * (h1 - h0)
    front = X < X_F - STEP['out'] + 0.02
    I = I * front; S = S * front
    ref = I[(np.abs(X - (X_F - STEP['out'] - 0.1)) < 0.08) & (Z > Z_R) & (Z < Z_L)]
    I = I / (ref.max() if ref.size else I.max()) * GL['peak']
    sx0, sy0 = x0, y0; st = step_faces((sx0, sy0, sx0 + w, sy0 + h))
    I = np.where(st, 0, I); S = np.where(st, 0, S)
    S = S / S.max() * GL['gloss']
    rng = np.random.default_rng(23); ph_ = rng.random(h) * 3                     # (the dashes: 3 px, a phase per row)
    dash = rng.random((h, w // 3 + 2))[np.arange(h)[:, None], ((np.arange(w)[None] + ph_[:, None]) // 3).astype(int)]
    S = S * (0.6 + 0.4 * dash)
    fade = np.clip((xs - GL['fade'][0]) / (GL['fade'][1] - GL['fade'][0]), 0, 1)
    rgb = (np.array(GL['warm'])[None, None] * np.clip(I, 0, GL['peak'])[..., None] + np.array(GL['sheen'])[None, None] * S[..., None]) / 255.0 * fade[..., None]
    out[..., :3] = np.clip(rgb, 0, 255); out[..., 3] = np.where(np.round(out[..., :3]).max(-1) > 0, 255, 0)
    Image.fromarray(np.round(out).astype(np.uint8), 'RGBA').save(os.path.join(ROOT, 'assets', 'gl_ramen_wet.webp'), 'WEBP', lossless=True, quality=100, method=6, exact=True)


def shut_pixels(city, box=BOX):
    """the front as it looks shut (for the closed shop's overlay): its faces' pixels and colours, in the street's frame"""
    shut, m = paint('shut', city, box)
    ys, xs = np.nonzero(m)
    return xs + box[0], ys + box[1], shut[m]


BLOCK = {'kick': (92, 52, 34), 'rail': (64, 34, 24), 'stile': (64, 34, 24), 'reveal': (40, 22, 18), 'jamb': (52, 30, 24),
         'head': (58, 32, 24), 'head_under': (30, 16, 12), 'sill_top': (120, 84, 56), 'sill_front': (70, 44, 30),
         'step_top': (112, 112, 118), 'step_front': (62, 62, 70), 'step_end': (78, 78, 86), 'glass': (40, 48, 70)}


def tone(name):
    for k in sorted(BLOCK, key=len, reverse=True):
        if k in name: return BLOCK[k]
    return (255, 0, 255)


def blockout(img, box=BOX):
    """each face its flat tone over img (RGB, the street): the glass a flat blue-grey"""
    out = img.copy(); x0, y0, x1, y1 = box
    sub = out[y0:y1, x0:x1]
    for name, c in faces():
        sub[raster(c, None, box)] = tone(name)
    sub[glass_mask(box)] = BLOCK['glass']
    return out


if __name__ == '__main__':
    if '--guide' in sys.argv or '--preview' in sys.argv:
        d = sys.argv[sys.argv.index('--guide' if '--guide' in sys.argv else '--preview') + 1]; os.makedirs(d, exist_ok=True)
        L = np.asarray(Image.open(os.path.join(ROOT, 'assets', 'layer_city_off.webp')).convert('RGBA')).astype(float)
        U = np.asarray(Image.open(os.path.join(ROOT, 'assets', 'street_unlit.webp')).convert('RGBA')).astype(float)
        X0, Y0, X1, Y1 = 1080, 400, 1280, 790
        if '--guide' in sys.argv:
            b = blockout(L[..., :3])
            Image.fromarray(b[Y0:Y1, X0:X1].astype(np.uint8)).resize(((X1 - X0) * 4, (Y1 - Y0) * 4), Image.NEAREST).save(os.path.join(d, 'blockout_x4.png'))
        else:
            c, u = L.copy(), U.copy(); draw(c, u)
            xs, ys, sc = shut_pixels(L); s = c.copy(); s[ys, xs, :3] = s[ys, xs, :3] * 0.12 + sc * 0.88
            tiles = [Image.fromarray(np.clip(im[Y0:Y1, X0:X1, :3], 0, 255).astype(np.uint8)).resize(((X1 - X0) * 4, (Y1 - Y0) * 4), Image.NEAREST) for im in (c, s, u)]
            O = Image.new('RGB', (3 * tiles[0].width + 16, tiles[0].height), (255, 255, 255))
            for i, t in enumerate(tiles): O.paste(t, (i * (t.width + 8), 0))
            O.save(os.path.join(d, 'front_lit_shut_cut_x4.png'))
        print('faces', len(faces()))
