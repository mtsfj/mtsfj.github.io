#!/usr/bin/env python3
"""The game centre's sign on the arcade's front, between its tiled eave and its lit doorway (the owner: "j'aurais fait un
petit logo / devanture arcade animé").

    (a module: tools/redraw_zones.py's zone 'arcsign', the last, calls draw() on the street as the zones before it leave
    it: the board as it is unlit, in the layers; and it writes the sign's light, assets/arcade_sign.webp and
    assets/arcade_sign_glow.webp, which assets/street.js lays on it: the same bytes each time)
    python3 tools/arcade_sign.py --before          once: the zone's before crops (tools/src/edits/arcsign_before_*.webp)

What was there: the arcade's fascia, a flat navy band (12, 24, 44) under the eave's soffit (its top on the ray 0.343, the
roller shutter's box under it on 0.266), from the corner's downpipe to the frame's edge.

The sign itself is drawn by the image model (the owner's rule R28: a detailed thing generated, then pixelated into the
scene), face on, on a flat green, in tools/src/arcade_sign/ (each with its prompt): lit_model.webp (asked on layout.png,
a dark rectangle of the board's proportions: a game centre's fascia board at night, dark lacquer, a marquee of warm bulbs
all round, the crab invader in cyan LED cells, GAME in pink neon tubes), unlit_model.webp (the same, its power off: the
tubes' dim glass, the LEDs and the bulbs dark) and pose2_model.webp (the same lit, the invader in its second pose). The
three answers share the board's rectangle to a pixel (x 37..1371, y 229..539: keyed off the green).

Here it is put in the street's perspective (VP (700, 615), the eye 1.41 m up, f 959.5 px): the board 3 cm proud of the
fascia (4.30 m from the street's axis), as long as the fascia allows (1.08 m) and as tall as the drawing's proportions
make it (25 cm, from 2.59 m up), each screen pixel's ray followed onto it and the drawing averaged over that pixel's
footprint (so it shortens toward the vanishing point as the wall does, 9 to 11 drawing pixels a scene pixel). In the
layers: the unlit drawing brought to the street's night (its colours scaled into the fascia's range, then quantised to
six colours of its own), the invader's LEDs only where both poses light them (the rest of the panel dark); its
underside and its thickness at its near end (simple geometry) in its edge's tones. Its light, the lit drawing less the
unlit one, taken only where something shines (a tube, an LED, a bulb: the drawing's soft glow on the board left to the
glow below), a pixel lit when the shining part covers enough of its footprint, its colour the shining part's mean,
quantised to six colours: the atlas assets/arcade_sign.webp (the board's box; rows: the tubes and the invader in its
first and its second pose, then the bulbs in the three steps of their chase, every third one bright and the others low,
the bulbs found in the drawing and counted round the board); and its glow, assets/arcade_sign_glow.webp: that light on
the wall round it, the eave's underside and its gutter, the shutter's box (a wide soft pool, no halo hugging the
letters), a little on the board's lacquer, never past the eave's tiles nor on the doorway's room.
"""
import os
import sys
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, label, binary_dilation

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDITS = os.path.join(ROOT, 'tools', 'src', 'edits')
SRC = os.path.join(ROOT, 'tools', 'src', 'arcade_sign')
ASSETS = os.path.join(ROOT, 'assets')
VP = (700.0, 615.0)
F, EYE = 959.5, 1.41
XF, XB = 4.30, 4.27                            # the fascia's wall, the board's face (m from the street's axis)
XS = (1326, 1450)                              # its face's far and near ends (screen columns)
ZF, ZN = F * XB / (XS[0] - VP[0]), F * XB / (XS[1] - VP[0])   # their depths (6.54, 5.46 m)
L = ZF - ZN                                    # its length along the street (1.08 m)
RECT = (37, 229, 1372, 540)                    # the board in the drawings (x0, y0, x1, y1: keyed off their green)
H = L * (RECT[3] - RECT[1]) / (RECT[2] - RECT[0])   # its height, the drawing's proportions (0.25 m)
Y0 = 2.59; Y1 = Y0 + H                          # its bottom and top (m up)
BOX = (1320, 356, 1456, 446)                   # the zone (redraw_zones.py 'arcsign')
GBOX = (1276, 326, 1456, 470)                  # the glow's box
VT = 0.411                                     # the eave tiles' top (tools/arcade_eave.py): no light above it
DOOR = lambda x: 456.0 - 24.0 * (x - 1356.0) / 100.0   # the doorway's top (street.js ARC: the room below it)
INV_X = 478                                    # the invader's part of the drawings (x < this: its second pose from there)
SHINE = 60.0                                   # what shines: its light's luma over this
COVER = 0.28                                   # a scene pixel lit when the shining part covers this much of its footprint
NIGHT = (0.55, (11.0, 10.0, 18.0))             # the unlit drawing into the street's night: x 0.55, + this
EDGE = dict(under=(6, 6, 13), end=(12, 11, 21))   # (its underside, its thickness toward us: the edge's tones in shade)


def rays(xs, ys):
    """Each pixel's ray from the eye (dz = 1: t is the depth)."""
    return (xs + 0.5 - VP[0]) / F, (VP[1] - (ys + 0.5)) / F


def board(box):
    """Over box: what of the board each pixel shows ('' none, 'face', 'under', 'end'), and on its face (u along it from its
    far end, v up from its bottom, m), and the face's pixels per metre across and up there."""
    x0, y0, x1, y1 = box
    ys, xs = np.mgrid[y0:y1, x0:x1].astype(float)
    dx, dy = rays(xs, ys)
    Z = XB / dx; Y = EYE + dy * Z                             # (on the face's plane)
    u, v = ZF - Z, Y - Y0
    face = (u >= 0) & (u <= L) & (v >= 0) & (v <= H)
    tu = (Y0 - EYE) / dy; Xu = dx * tu                       # (on the underside's plane)
    under = ~face & (Xu >= XB) & (Xu <= XF) & (tu >= ZN) & (tu <= ZF)
    Xe, Ye = dx * ZN, EYE + dy * ZN                           # (on the near end's plane)
    end = ~face & ~under & (Xe >= XB) & (Xe <= XF) & (Ye >= Y0) & (Ye <= Y1)
    what = np.where(face, 'face', np.where(under, 'under', np.where(end, 'end', '')))
    return what, u, v, F * XB / Z ** 2, F / Z


def model(name):
    return np.asarray(Image.open(os.path.join(SRC, f'{name}_model.webp')).convert('RGB')).astype(float)


def kmeans(X, k, it=20):
    """k colours for the rows of X (deterministic: started on the luma's quantiles)."""
    lum = X @ [0.299, 0.587, 0.114]
    C = np.array([X[np.argsort(lum, kind='stable')[int((i + 0.5) / k * (len(X) - 1))]] for i in range(k)])
    for _ in range(it):
        a = np.argmin(((X[:, None] - C[None]) ** 2).sum(-1), 1)
        C = np.array([X[a == j].mean(0) if (a == j).any() else C[j] for j in range(k)])
    return C


def quantise(img, mask, k):
    """img's pixels in mask to k colours of their own."""
    if mask.sum() < k: return img
    C = kmeans(img[mask], k); out = img.copy()
    out[mask] = C[np.argmin(((img[mask][:, None] - C[None]) ** 2).sum(-1), 1)]
    return out


class Footprint:
    """Means of a drawing over each scene pixel's footprint on the board (a summed-area table)."""
    def __init__(self, what, u, v, sx, sy):
        bw, bh = RECT[2] - RECT[0], RECT[3] - RECT[1]
        hu, hv = 0.5 / sx, 0.5 / sy
        f = lambda a, lo, hi: np.clip(np.round(a), lo, hi).astype(int)
        self.x0 = f(RECT[0] + (u - hu) / L * bw, RECT[0], RECT[2] - 1)
        self.x1 = np.maximum(f(RECT[0] + (u + hu) / L * bw, RECT[0], RECT[2]), self.x0 + 1)
        self.y0 = f(RECT[3] - (v + hv) / H * bh, RECT[1], RECT[3] - 1)
        self.y1 = np.maximum(f(RECT[3] - (v - hv) / H * bh, RECT[1], RECT[3]), self.y0 + 1)
        self.face = what == 'face'

    def mean(self, a):
        """a: (h, w) or (h, w, c), the drawing's size: its mean over each face pixel's footprint (0 elsewhere)."""
        S = np.pad(np.cumsum(np.cumsum(a, 0), 1), [(1, 0), (1, 0)] + [(0, 0)] * (a.ndim - 2))
        x0, x1, y0, y1 = self.x0, self.x1, self.y0, self.y1
        s = S[y1, x1] - S[y0, x1] - S[y1, x0] + S[y0, x0]
        n = ((x1 - x0) * (y1 - y0)).astype(float)
        out = s / (n[..., None] if a.ndim == 3 else n)
        out[~self.face] = 0
        return out


def bulbs(lit, unlit):
    """The marquee's bulbs in the drawing: each bulb's step in the chase (0, 1, 2 round the board, -1 none), per pixel."""
    lt = lit - unlit
    warm = (lt[..., 0] > 120) & (lt[..., 1] > 90) & (lit[..., 0] > 170) & (lit[..., 2] < 220)
    yy, xx = np.mgrid[0:lit.shape[0], 0:lit.shape[1]]
    band = (np.minimum.reduce([xx - RECT[0], RECT[2] - xx, yy - RECT[1], RECT[3] - yy]) < 48) & \
           (xx >= RECT[0]) & (xx < RECT[2]) & (yy >= RECT[1]) & (yy < RECT[3])
    lab, n = label(binary_dilation(warm & band, iterations=3))
    cx, cy, bw, bh = (RECT[0] + RECT[2]) / 2, (RECT[1] + RECT[3]) / 2, RECT[2] - RECT[0], RECT[3] - RECT[1]
    ang = []
    for i in range(1, n + 1):
        ys, xs = np.nonzero(lab == i)
        ang.append(np.arctan2((ys.mean() - cy) / bh, (xs.mean() - cx) / bw))   # (round the board, as it reads)
    step = np.full(lab.shape, -1)
    for rank, i in enumerate(np.argsort(ang, kind='stable')): step[lab == i + 1] = rank % 3
    return step


def design(box):
    """The sign over box from the drawings: what each pixel shows, the unlit face, the lights (tubes in each pose, the
    bulbs and their steps)."""
    what, u, v, sx, sy = board(box)
    FP = Footprint(what, u, v, sx, sy)
    lit, unlit, pose2 = model('lit'), model('unlit'), model('pose2')
    xx = np.arange(lit.shape[1])[None, :]; yy = np.arange(lit.shape[0])[:, None]
    litB = np.where((xx < INV_X)[..., None], pose2, lit)            # (the second pose: the invader's part only)
    cyan = lambda a: (a[..., 2] > 150) & (a[..., 1] > 150) & (a[..., 0] < 140)
    both = cyan(lit) & cyan(pose2)
    board_col = np.median(unlit[RECT[1] + 60:RECT[3] - 60, 500:1300].reshape(-1, 3), 0)
    unl = unlit.copy()                                               # (the panel's LEDs unlit: only those both poses light)
    inv = (xx < INV_X) & (yy > RECT[1] + 40) & (yy < RECT[3] - 40) & ~binary_dilation(both, iterations=2)
    unl[inv & ((unlit[..., 2] > unlit[..., 0] + 12) | cyan(lit) | cyan(pose2))] = board_col
    step = bulbs(lit, unlit)
    face = FP.face
    off = quantise(FP.mean(unl) * NIGHT[0] + np.array(NIGHT[1]), face, 6)
    lights = {}
    for name, src in (('A', lit), ('B', litB)):
        lt = np.clip(src - unlit, 0, 255); shine = (lt @ [0.299, 0.587, 0.114]) > SHINE
        for part, m in (('tubes', shine & (step < 0)), ('bulbs', shine & (step >= 0))):
            cov = FP.mean(m.astype(float)); col = FP.mean(lt * m[..., None]) / np.maximum(cov, 1e-6)[..., None]
            lights[name, part] = np.where((cov >= COVER)[..., None] & face[..., None], col, 0)
    ph = FP.mean(np.stack([(step == k).astype(float) for k in range(3)], -1)).argmax(-1)   # (each bulb pixel's step)
    allL = np.concatenate([lights['A', 'tubes'], lights['B', 'tubes'], lights['A', 'bulbs']], 0)
    q = quantise(allL, allL.max(-1) > 0, 6); hh = off.shape[0]
    return dict(what=what, off=off, tubes=(despeckle(q[:hh]), despeckle(q[hh:2 * hh])), bulb=q[2 * hh:], step=ph)


def despeckle(a):
    """A lit pixel unlike all its lit neighbours (four), three of which agree, takes theirs (the core's stipple inside a
    tube's stroke, from the footprints' mixes)."""
    out = a.copy(); h, w = a.shape[:2]; lit = a.max(-1) > 0
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            if not lit[y, x]: continue
            nb = [tuple(a[y + dy, x + dx]) for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)) if lit[y + dy, x + dx]]
            me = tuple(a[y, x])
            if len(nb) >= 3 and me not in nb:
                c = max(set(nb), key=nb.count)
                if nb.count(c) >= 3: out[y, x] = c
    return out


def off_picture(D, base):
    """The board unlit over base (RGB floats): its face the drawing's, its underside and its thickness."""
    out = base.copy(); w = D['what']
    out[w == 'face'] = D['off'][w == 'face']
    for k in ('under', 'end'): out[w == k] = EDGE[k]
    return out


def lights(D, off):
    """The sign's light (additive: each lit pixel's colour less the layer's there): the tubes with the invader in each
    pose, the bulbs in each step of their chase (the step's bulbs bright, the others at a third)."""
    rows = [D['tubes'][0], D['tubes'][1]]
    on = D['bulb'].max(-1) > 0
    for k in range(3): rows.append(np.where(on[..., None], D['bulb'] * np.where(D['step'] == k, 1.0, 0.33)[..., None], 0))
    return [np.where(x.max(-1, keepdims=True) > 0, np.maximum(x - off, 0), 0) for x in rows]


def glow(D):
    """The sign's light on what is round it (the wall, the eave's underside, its gutter, the shutter's box, a little on
    the board): its tubes (first pose) and its bulbs (at their mean) spread wide and soft; nothing above the eave's tiles,
    nothing on the doorway's room."""
    gx0, gy0, gx1, gy1 = GBOX; bx0, by0, bx1, by1 = BOX
    src = np.zeros((gy1 - gy0, gx1 - gx0, 3))
    src[by0 - gy0:by1 - gy0, bx0 - gx0:bx1 - gx0] = D['tubes'][0] + 0.45 * D['bulb']
    g = np.stack([0.5 * gaussian_filter(src[..., c], 8.0) + 2.4 * gaussian_filter(src[..., c], 22.0) for c in range(3)], -1)
    ys, xs = np.mgrid[gy0:gy1, gx0:gx1].astype(float)
    ok = (ys > VP[1] - VT * (xs + 0.5 - VP[0]) + 2) & ~((xs >= 1356) & (ys >= DOOR(xs)))
    k = ok.astype(float)
    k[by0 - gy0:by1 - gy0, bx0 - gx0:bx1 - gx0][D['what'] != ''] *= 0.35   # (the board's dark lacquer: a little of it)
    return np.clip(g * k[..., None], 0, 255)


def rgba(a):
    """An additive picture: alpha 255 wherever it adds anything."""
    q = np.clip(np.round(a), 0, 255).astype(np.uint8)
    return np.dstack([q, ((q.max(-1) > 0) * 255).astype(np.uint8)])


def textures(D, off):
    """assets/arcade_sign.webp (the board's box, five rows) and assets/arcade_sign_glow.webp (the glow's box)."""
    rows = [rgba(a) for a in lights(D, off)]
    Image.fromarray(np.concatenate(rows, 0), 'RGBA').save(os.path.join(ASSETS, 'arcade_sign.webp'), 'WEBP', lossless=True,
                                                           quality=100, method=6, exact=True)
    Image.fromarray(rgba(glow(D)), 'RGBA').save(os.path.join(ASSETS, 'arcade_sign_glow.webp'), 'WEBP', lossless=True,
                                                quality=100, method=6, exact=True)


def draw(city, unlit, box):
    """The zone's tool: the board unlit, in place, on the street and its power cut (RGBA floats, whole), the latter times
    the painter's darkening there; writes the sign's light. Returns the mask of what changed."""
    x0, y0, x1, y1 = box
    O, U = city[y0:y1, x0:x1, :3], unlit[y0:y1, x0:x1, :3]
    D = design(box)
    new = off_picture(D, O)
    mask = np.abs(new - O).max(-1) > 0
    dark = np.stack([(gaussian_filter(U[..., c], 4.0) + 1.0) / (gaussian_filter(O[..., c], 4.0) + 1.0) for c in range(3)], -1)
    unew = np.clip(new * np.clip(dark, 0, 1.5), 0, 255)
    city[y0:y1, x0:x1, :3][mask] = new[mask]; unlit[y0:y1, x0:x1, :3][mask] = unew[mask]
    textures(D, new)
    return mask


def _load(p):
    return np.asarray(Image.open(p).convert('RGBA')).astype(float)


def before():
    """The zone's before crops: the layers in its box as tools/redraw_zones.py's first pass leaves them without this zone
    (each zone's before crop laid back, in its order, on the layers as they are)."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import redraw_zones as RZ
    outs = [os.path.join(EDITS, f'arcsign_before_{t}.webp') for t in ('city', 'unlit')]
    if any(os.path.exists(p) for p in outs): sys.exit('arcade_sign: the before crops exist already (made once)')
    city, unlit = _load(os.path.join(ASSETS, 'layer_city_off.webp')), _load(os.path.join(ASSETS, 'street_unlit.webp'))
    for nm, cfg in RZ.ZONES.items():
        if nm == 'arcsign': continue
        a, b, c, d = cfg['box']
        city[b:d, a:c] = _load(os.path.join(EDITS, f'{nm}_before_city.webp'))
        unlit[b:d, a:c] = _load(os.path.join(EDITS, f'{nm}_before_unlit.webp'))
    x0, y0, x1, y1 = BOX
    for a, p in zip((city, unlit), outs):
        Image.fromarray(np.clip(np.round(a[y0:y1, x0:x1]), 0, 255).astype(np.uint8), 'RGBA').save(
            p, 'WEBP', lossless=True, quality=100, method=6, exact=True)
    print('arcade_sign: before crops written', BOX)


if __name__ == '__main__':
    if '--before' in sys.argv: before()
    else: print(__doc__)
