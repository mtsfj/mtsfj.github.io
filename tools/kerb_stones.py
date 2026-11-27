#!/usr/bin/env python3
"""The two near kerbs along the road as precast concrete kerb stones (歩車道境界ブロック), weathered and wet: their top, its
lit arris and their face down to the road, from the bottom of the frame to the far end's corners.

    (a module: tools/redraw_zones.py's zones 'kerbL' and 'kerbR' call draw() on the street as the zones before them leave
     it, last; each also writes the ground lights that fall on its kerb, assets/gl_*.webp, and the wet ground on its top,
     assets/wet.webp, from their before crops, on the kerb's own pixels only)
    python3 tools/kerb_stones.py --befores      once: the zones' before copies (tools/src/edits/kerb{L,R}_before_{city,
                                                unlit}.webp: the painter's pixels, as redraw_zones.py lays every zone's
                                                before copies back), the ground lights' (kerb{L,R}_before_<gl>.webp) and
                                                the wet ground's (kerb{L,R}_wet_before.webp), from the assets as they are
    python3 tools/kerb_stones.py --preview DIR  each box before and after, both layers, x3, and the planes' measures
                                                (nothing written in assets/)

What was there: along each sidewalk, a lit row (the arris) over a dark band (the face), each the same value from end to
end with a pixel's noise in it; at x3 a smooth lit line over a smooth dark band, concrete with no concrete in it. The
painter's joints are there: a dark column across the face and a dark row across the top where each stone meets the next.

The geometry (the street's ground model: VP (700, 615), f 959.5 px, the eye 1.41 m over the road; tools/lane_lines.py,
tools/far_end.py), measured on the painter's edges: each kerb's face is the plane |X| = 2.80 m (its arris within 0.3 px
of that ray on 600 columns, its foot within 0.6 px; street.js's petals already run in the gutter to "the curb's face at
2.8"), 0.15 m high (the sidewalk's height); its top 0.17 m deep, to |X| = 2.97 m (the painter's paving joint just
behind it): a Japanese kerb stone's section (15-18 cm on top, 15 cm proud of the road). His joints fall on every whole
metre of depth, from 6 m to the corner (both sides, x within a pixel of Z = n m): his stones are 1 m long, and only his
joints are kept (no new grid: the owner turned down a too regular one on 24/11). Each pixel belongs to one plane by its
centre (crisp on the pixel grid, the painter's own rows): the top, its arris (the top's last row, where the rounded
edge catches the light) and the face; the last metre before each corner (Z 26-27 m) and the corner itself are left as
painted.

The concrete: the weathered cast concrete already generated (tools/src/edits/pole_concrete_src.webp, the left panel of
the 24/11 sheet, used by tools/pole_texture.py for the pole on 26/11; no new image), 3.07 mm a pixel, its long rain
streaks taken out (what runs long down the wall and narrow across it: a wall's washes down a 15 cm face read as
flutes), its mottling, pits and efflorescence kept. Each stone is unfolded (from the top's back edge over the arris and
down the face to the road: 0.32 m) onto a patch of it 1 m long, seeded (its own columns and rows, mirrored or not), so
the stones differ where the painter's joints are. Each pixel the exact mean of the photograph over the ground it covers
(by summed areas: the near stones 2-12 mm a pixel, the far ones 4-10 cm), on the face drawn out along the kerb (EXT:
so steep a plane shows patches along it, not one flute a column); only its relative light (its luminance over its own
mean within 46 cm, stone by stone and plane by plane: no stone lighter than the next, no light of its own) modulates
each plane's tone, at the spread of the painter's own grain there (K, depth by depth, at most KMAX times its own: the
near stones' mottling as it is, the far ones' a little raised to read).

Its tones are the painter's, plane by plane, in each layer and in each ground light that falls on the kerb (R29: one
tone per plane): each pixel's tone is the mean of its own plane's pixels along the kerb (the same row of that plane,
the columns round it, Gaussian SIGMA, his joints left out), so his light (the street lamp's, the hall's, the shops',
the vending machines', the pole's contact shade) and the lit arris stay where the lights really reach them; the
concrete's relative light times it (each plane's mean, and the kerb's spread, as before: measured by --preview); his
joints as he painted them. The power cut's layer the same from its own pixels; a ground light's light (its colour times
its alpha) the same, its alpha kept; the hours, the power cut and the red night take the kerbs as they take the ground.
The wet ground (wet.webp): the top's wetness a little more in the concrete's darker, damper patches and less in its
lighter ones (WETK, its mean kept), so the wet pass's sheen on it is mottled as on wet concrete; the face (vertical,
no mirror), the arris and the puddles as they were. Only the kerbs' pixels change. Needs numpy, scipy, Pillow.
"""
import os
import re
import sys
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, gaussian_filter1d

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDITS = os.path.join(ROOT, 'tools', 'src', 'edits')
OUT = os.path.join(ROOT, 'assets')
BOXES = {'kerbL': (224, 650, 600, 816), 'kerbR': (800, 650, 1176, 816)}   # (each zone's box: its kerb to its corner)
VPX, VPY, F, EYE = 700.0, 615.0, 959.5, 1.41     # the street's ground model
KH, XF, XB = 0.15, 2.80, 2.97                    # the kerb: its height, its face's plane, its top's back edge (|X|, m)
ZMAX = 26.0                                      # (past this the last stone and the corner, as painted)
ZJ = range(5, 27)                                # the painter's joints: Z = n m
TEX = os.path.join(EDITS, 'pole_concrete_src.webp')
TEX_M, TEX_FOOT = 0.00307, 968                   # the photograph: metres a pixel, its wall's foot (tools/pole_texture.py)
REL = 150.0                                      # (its relative light: over its own mean within this, its pixels: 46 cm)
STREAK = (25.0, 10.0, 0.0)                       # (its rain streaks, long down the wall: taken out, a wall's washes down a
                                                 # 15 cm face read as flutes; its mottling, pits and efflorescence stay)
ROWS = (40, 860)                                 # (the photograph's rows a stone's patch is taken from: under the eave's
                                                 # shade, over the damp foot's moss)
STONE = 1.0                                      # a stone's length (m): the painter's joints
EXT = (1.0, 3.0)                                 # (a pixel's footprint along the kerb, drawn out: top, face)
SIGMA = 4.0                                      # (each plane's tone along the kerb: columns)
K = 1.0                                          # the concrete's spread round each plane's tone: this share of the
                                                 # painter's own grain there (his pixel noise, 7-9 %), depth by depth
                                                 # (2 m bands): no added contrast, and the far stones as readable as
                                                 # the near ones (their pixels the mean of 4-10 cm of it)
KMAX = 2.5                                       # (at most this gain over the photograph's own)
WETK = 1.0                                       # (the top's wetness: this much of the concrete's relative darkness)
JFACE, JTOP = 0.93, 0.90                         # (a joint of the painter's: its face column, its top row, this much darker)
SEED = 27
LUMA = np.array([0.299, 0.587, 0.114])


def side(box):
    return -1.0 if box[0] < VPX else 1.0


def planes(box):
    """each pixel's plane in the box (0 none, 1 top, 2 arris, 3 face), its rectified row (the top's rows counted back
    from the arris; the face's from the arris down its upper half, from its foot up its lower half), its depth's range
    and its place across the stone (s: m from the top's back edge, over the arris, down the face)"""
    x0, y0, x1, y1 = box
    H, W = y1 - y0, x1 - x0
    pl = np.zeros((H, W), int); kk = np.zeros((H, W), int)
    za = np.zeros((H, W)); zb = np.zeros((H, W)); sa = np.zeros((H, W)); sb = np.zeros((H, W))
    for c in range(W):
        x = x0 + c
        d = abs(x + 0.5 - VPX)
        if d < 1: continue
        ya = VPY + d * (EYE - KH) / XF            # (the arris: the top's front edge)
        yb = VPY + d * (EYE - KH) / XB            # (the top's back edge)
        yf = VPY + d * EYE / XF                   # (the face's foot)
        rows = np.arange(y0, y1)
        yc = rows + 0.5
        top = (yc >= yb) & (yc < ya); face = (yc >= ya) & (yc < yf)
        if not (top.any() or face.any()): continue
        ar = int(np.ceil(ya - 0.5) - 1)           # (the arris row: the last row whose centre is above ya)
        fl = int(np.ceil(yf - 0.5) - 1)           # (the face's last row, maybe under the frame)
        # face: its depth is the column's, its height the row's
        dl, dr = abs(x - VPX), abs(x + 1 - VPX)
        zf = sorted((F * XF / max(dl, 1e-6), F * XF / max(dr, 1e-6)))
        zc = F * XF / d
        for i in np.where(face)[0]:
            y = rows[i]
            ha = np.clip(EYE - (y + 1 - VPY) * zc / F, 0, KH); hb = np.clip(EYE - (y - VPY) * zc / F, 0, KH)
            if zc >= ZMAX: continue
            pl[i, c] = 3
            kt, kb = y - ar, fl - y
            kk[i, c] = kt if kt <= kb + 1 else -(kb + 1)
            za[i, c], zb[i, c] = zf
            sa[i, c], sb[i, c] = (XB - XF) + (KH - hb), (XB - XF) + (KH - ha)
        for i in np.where(top)[0]:
            y = rows[i]
            zt = sorted((F * (EYE - KH) / (y - VPY), F * (EYE - KH) / (y + 1 - VPY)))
            zcc = F * (EYE - KH) / (y + 0.5 - VPY)
            if zcc >= ZMAX: continue
            pl[i, c] = 2 if y == ar else 1
            kk[i, c] = ar - y
            za[i, c], zb[i, c] = zt
            xa, xb2 = sorted((dl * zcc / F, dr * zcc / F))
            sa[i, c], sb[i, c] = XB - np.clip(xb2, XF, XB), XB - np.clip(xa, XF, XB)
    return dict(pl=pl, k=kk, za=za, zb=zb, sa=sa, sb=sb)


def joints(V, P, box):
    """the painter's joints in the box: the face's columns and the top's rows at Z = n m that he drew darker than the
    stones' tone round them (from his own pixels, V: the zone's before copy)"""
    x0, y0, x1, y1 = box
    H, W = P['pl'].shape
    L = V[..., :3] @ LUMA
    T = tone(L[..., None], P, np.zeros((H, W), bool))[..., 0]
    r = np.where(T > 0, L / np.maximum(T, 1e-6), 1.0)
    J = np.zeros((H, W), bool)
    s = side(box)
    for n in ZJ:
        xn = VPX + s * F * XF / n
        for c in range(int(np.floor(xn)) - 1 - x0, int(np.floor(xn)) + 2 - x0):
            if not 0 <= c < W: continue
            m = P['pl'][:, c] == 3
            if m.sum() < 2: continue
            k = P['k'][:, c]
            core = m & (k > 0) if (m & (k > 0)).sum() >= 1 else m
            if r[core, c].mean() < JFACE: J[m, c] = True
        yn = VPY + F * (EYE - KH) / n
        for rr in range(int(np.floor(yn)) - 1 - y0, int(np.floor(yn)) + 2 - y0):
            if not 0 <= rr < H: continue
            m = P['pl'][rr] == 1
            if m.sum() < 2: continue
            if r[rr, m].mean() < JTOP: J[rr, m] = True
    return J


def tone(V, P, J, have=None):
    """each plane's tone at each of its pixels: the mean of the same plane's pixels on the same rectified row, along the
    kerb (Gaussian SIGMA over the columns), joints and pixels without data left out"""
    H, W = P['pl'].shape
    have = np.ones((H, W), bool) if have is None else have
    out = np.zeros(V.shape)
    for p in (1, 2, 3):
        on = (P['pl'] == p)
        for k in np.unique(P['k'][on]):
            m = on & (P['k'] == k)
            cols = np.where(m.any(0))[0]
            rows = np.argmax(m, 0)                # (one pixel a column on a rectified row)
            w = (m & ~J & have)[rows, np.arange(W)].astype(float)
            v = V[rows, np.arange(W)] * w[:, None]
            num = gaussian_filter1d(v, SIGMA, axis=0, mode='constant'); den = gaussian_filter1d(w, SIGMA, mode='constant')
            t = num / np.maximum(den, 1e-6)[:, None]
            bad = den < 1e-3
            if bad.any() and (~bad).any():        # (no data near: the nearest tone along)
                idx = np.where(~bad)[0]
                t[bad] = t[idx[np.abs(idx[None, :] - np.where(bad)[0][:, None]).argmin(1)]]
            out[rows[cols], cols] = t[cols]
    return out


def photo():
    """the photograph's relative light: its luminance, its long rain streaks mostly taken out (what is long down the
    wall and narrow across it), over its own mean within REL pixels (the wall only)"""
    A = np.asarray(Image.open(TEX).convert('RGB')).astype(float)[:TEX_FOOT]
    L = A @ LUMA
    sy, sx, keep = STREAK
    Vy = gaussian_filter(L, (sy, 0), mode='reflect')
    L = L - (1 - keep) * (Vy - gaussian_filter(Vy, (0, sx), mode='reflect'))
    return L / np.maximum(gaussian_filter(L, REL, mode='reflect'), 1e-6)


def sat(T):
    S = np.zeros((T.shape[0] + 1, T.shape[1] + 1)); S[1:, 1:] = T.cumsum(0).cumsum(1)
    return S


def sat_at(S, v, u):
    nv, nu = S.shape[0] - 1, S.shape[1] - 1
    v = np.clip(v, 0, nv); u = np.clip(u, 0, nu)
    i = np.minimum(np.floor(v).astype(int), nv - 1); j = np.minimum(np.floor(u).astype(int), nu - 1)
    fv, fu = v - i, u - j
    return (S[i, j] * (1 - fv) * (1 - fu) + S[i + 1, j] * fv * (1 - fu) + S[i, j + 1] * (1 - fv) * fu + S[i + 1, j + 1] * fv * fu)


def texture(P, name):
    """each kerb pixel's concrete: the mean of the photograph's relative light over what it covers on its stone(s)"""
    R = photo(); S = sat(R); h, w = R.shape
    lu = int(round(STONE / TEX_M)); lv = int(np.ceil((XB - XF + KH) / TEX_M))
    rng = np.random.default_rng(SEED + (0 if name == 'kerbL' else 1))
    c0 = rng.integers(0, w - lu, 40); r0 = rng.integers(ROWS[0], ROWS[1] - lv, 40); mir = rng.random(40) < 0.5
    on = P['pl'] > 0
    m = np.ones(on.shape)
    za, zb, sa, sb = P['za'][on], P['zb'][on], P['sa'][on], P['sb'][on]
    zc = 0.5 * (za + zb); n = np.floor(zc / STONE)     # (each footprint drawn out along the kerb, within its stone: what the
    hw = 0.5 * (zb - za) * np.where(P['pl'][on] == 3, EXT[1], EXT[0])   # eye cannot part along so steep a plane reads
    one = np.floor(za / STONE) == np.floor((zb - 1e-9) / STONE)          # as patches along it, not as flutes)
    za = np.where(one, np.maximum(zc - hw, n * STONE), za); zb = np.where(one, np.minimum(zc + hw, (n + 1) * STONE), zb)
    acc = np.zeros(za.shape); wt = np.zeros(za.shape)
    n0 = np.floor(za / STONE).astype(int); n1 = np.floor((zb - 1e-9) / STONE).astype(int)
    for which in (0, 1):
        n = n0 if which == 0 else n1
        a = np.maximum(za, n * STONE); b = np.minimum(zb, (n + 1) * STONE)
        ok = (b > a) & ((which == 0) | (n1 != n0))
        t0, t1 = (a - n * STONE) / STONE, (b - n * STONE) / STONE
        t0, t1 = np.where(mir[n], 1 - t1, t0), np.where(mir[n], 1 - t0, t1)
        u0, u1 = c0[n] + t0 * lu, c0[n] + t1 * lu
        v0, v1 = r0[n] + sa / TEX_M, r0[n] + np.maximum(sb, sa + 1e-6) / TEX_M
        area = (u1 - u0) * (v1 - v0)
        s = sat_at(S, v1, u1) - sat_at(S, v0, u1) - sat_at(S, v1, u0) + sat_at(S, v0, u0)
        mean = s / np.maximum(area, 1e-9)
        acc += np.where(ok, mean * (b - a), 0); wt += np.where(ok, b - a, 0)
    m[on] = acc / np.maximum(wt, 1e-12)
    return m


def plan(name, box, Vb):
    P = planes(box)
    J = joints(Vb, P, box)
    m = texture(P, name)
    L = Vb @ LUMA
    T = tone(Vb, P, J) @ LUMA
    zc = 0.5 * (P['za'] + P['zb'])
    zn = np.floor(zc / STONE)
    for p in (1, 2, 3):                           # (each plane's concrete over its own mean, stone by stone: its tone the
        q = (P['pl'] == p)                        # painter's, no stone lighter or darker than the next)
        for n in np.unique(zn[q]):
            b = q & (zn == n)
            m[b] = m[b] / m[b].mean()
    top = P['pl'] == 1                            # (one material: the gain the top needs, depth by depth, on every plane:
    zs, ks = [], []                               # K times the painter's grain there over the photograph's own)
    for z0 in np.arange(6.0, ZMAX, 2.0):
        b = top & ~J & (zc >= z0) & (zc < z0 + 2.0)
        if b.sum() < 20: continue
        sp = np.std(L[b] / np.maximum(T[b], 1e-6)); st = np.std(m[b])
        zs.append(z0 + 1.0); ks.append(np.clip(K * sp / max(st, 1e-4), 1.0, KMAX))
    g = np.where(P['pl'] > 0, np.interp(zc, zs, ks), 1.0)
    P.update(J=J, m=m, gain=g, mod=1 + g * (m - 1), touch=(P['pl'] > 0) & ~J)
    return P


def repaint(V, P, have=None):
    """one layer's box (H, W, 3) with the kerb's stones (have: where the layer has pixels, a ground light's)"""
    T = tone(V, P, P['J'], have)
    out = V.copy()
    t = P['touch'] if have is None else P['touch'] & have
    out[t] = T[t] * P['mod'][t][:, None]
    return np.clip(out, 0, 255)


def load(path, mode='RGBA'):
    return np.asarray(Image.open(path).convert(mode)).astype(float)


def save(a, path, mode='RGBA'):
    Image.fromarray(np.clip(np.round(a), 0, 255).astype(np.uint8), mode).save(path, 'WEBP', lossless=True, quality=100, method=6, exact=True)


def ground_lights(box):
    """the ground lights whose box touches this one: (name, (x, y)) from street.js"""
    js = open(os.path.join(ROOT, 'assets', 'street.js'), encoding='utf-8').read()
    x0, y0, x1, y1 = box; out = []
    for mm in re.finditer(r"url: 'assets/(gl_[a-z0-9_]+)\.webp\?v=\d+', box: \[(\d+), (\d+), (\d+), (\d+)\]", js):
        n, bx, by, bw, bh = mm.group(1), *map(int, mm.groups()[1:])
        if bx < x1 and bx + bw > x0 and by < y1 and by + bh > y0: out.append((n, (bx, by)))
    return out


def clip_box(box, gx, gy, g):
    x0, y0, x1, y1 = box
    return max(x0, gx), max(y0, gy), min(x1, gx + g.shape[1]), min(y1, gy + g.shape[0])


def name_of(box):
    return [n for n, b in BOXES.items() if tuple(b) == tuple(box)][0]


def draw(city, unlit, box):
    """The zone: both layers' boxes in place, the ground lights and the wet ground written on the kerb's pixels; returns
    what changed (whole scene)."""
    name = name_of(box)
    x0, y0, x1, y1 = box
    Vb = load(os.path.join(EDITS, f'{name}_before_city.webp'))[..., :3]
    P = plan(name, box, Vb)
    t = P['touch']
    for L in (city, unlit):
        V = L[y0:y1, x0:x1, :3]
        V[t] = repaint(V.copy(), P)[t]
    for n, (gx, gy) in ground_lights(box):
        g = load(os.path.join(OUT, n + '.webp')).copy()
        a, b, c, d = clip_box(box, gx, gy, g)
        gb = load(os.path.join(EDITS, f'{name}_before_{n}.webp'))
        full = np.zeros((y1 - y0, x1 - x0, 4)); full[b - y0:d - y0, a - x0:c - x0] = gb
        al = full[..., 3]; hv = al > 0
        E = full[..., :3] * (al / 255.0)[..., None]   # (the light it adds: its colour times its alpha)
        En = repaint(E, P, hv)
        mt = t & hv
        an = np.maximum(al, np.ceil(En.max(-1) - 1e-6))   # (its alpha raised only where the light would not fit)
        rgb = En * 255.0 / np.maximum(an, 1)[..., None]
        out = full.copy(); out[mt, :3] = rgb[mt]; out[mt, 3] = an[mt]
        G = g[b - gy:d - gy, a - gx:c - gx]
        sl = (slice(b - y0, d - y0), slice(a - x0, c - x0))
        mm = mt[sl]
        if not mm.any(): continue                 # (a ground light that does not reach the kerb: left as it is)
        G[mm] = out[sl][mm]
        save(g, os.path.join(OUT, n + '.webp'))
    w = load(os.path.join(OUT, 'wet.webp'), 'RGB').copy()
    wb = load(os.path.join(EDITS, f'{name}_wet_before.webp'), 'RGB')
    top = t & (P['pl'] == 1) & (wb[..., 2] == 0)
    wn = wb.copy(); wn[..., 0] = np.where(top, wb[..., 0] * (1 - WETK * (P['mod'] - 1)), wb[..., 0])
    W0 = w[y0 - 600:y1 - 600, x0:x1]; W0[top] = wn[top]
    save(w, os.path.join(OUT, 'wet.webp'), 'RGB')
    print('%s: face |X| %.2f m, %.2f m high, top %.2f m deep, to Z %.0f m; %d joints px kept; %d px' % (
        name, XF, KH, XB - XF, ZMAX, int(P['J'].sum()), int(t.sum())))
    ch = np.zeros(city.shape[:2], bool); ch[y0:y1, x0:x1] = t
    return ch


def befores():
    """the zones' before copies: the layers as redraw_zones.py leaves them once it has laid every zone's before copies
    back (the painter's pixels; these zones' own left out), the ground lights' and the wet ground's from the assets"""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import redraw_zones as rz
    for tag, f in (('city', 'layer_city_off'), ('unlit', 'street_unlit')):
        a = np.asarray(Image.open(os.path.join(ROOT, 'assets', f + '.webp')).convert('RGBA')).copy()
        for zn, cfg in rz.ZONES.items():
            if zn in BOXES: continue
            bx0, by0, bx1, by1 = cfg['box']
            a[by0:by1, bx0:bx1] = np.asarray(Image.open(os.path.join(EDITS, f'{zn}_before_{tag}.webp')).convert('RGBA'))
        for name, (x0, y0, x1, y1) in BOXES.items():
            save(a[y0:y1, x0:x1], os.path.join(EDITS, f'{name}_before_{tag}.webp')); print(f'{name}_before_{tag}')
    w = np.asarray(Image.open(os.path.join(ROOT, 'assets', 'wet.webp')).convert('RGB'))
    for name, box in BOXES.items():
        x0, y0, x1, y1 = box
        for n, (gx, gy) in ground_lights(box):
            g = np.asarray(Image.open(os.path.join(ROOT, 'assets', n + '.webp')).convert('RGBA'))
            a, b, c, d = clip_box(box, gx, gy, g)
            save(g[b - gy:d - gy, a - gx:c - gx], os.path.join(EDITS, f'{name}_before_{n}.webp')); print(f'{name}_before_{n}', (a, b, c, d))
        save(w[y0 - 600:y1 - 600, x0:x1], os.path.join(EDITS, f'{name}_wet_before.webp'), 'RGB'); print(f'{name}_wet_before')


def measures(name, P, V, out):
    """each plane's mean and its pixels' spread round their tone, before and after (no added contrast)"""
    L0, L1 = V @ LUMA, out @ LUMA
    T = tone(V, P, P['J']) @ LUMA
    s = []
    for p, nm in ((1, 'top'), (2, 'arris'), (3, 'face')):
        q = (P['pl'] == p) & ~P['J']
        r0 = L0[q] / np.maximum(T[q], 1e-6) - 1; r1 = L1[q] / np.maximum(T[q], 1e-6) - 1
        s.append('%s mean %.2f -> %.2f, spread %.1f%% -> %.1f%%' % (nm, L0[q].mean(), L1[q].mean(), 100 * r0.std(), 100 * r1.std()))
    q = P['pl'] > 0
    s.append('whole kerb std %.2f -> %.2f' % (L0[q].std(), L1[q].std()))
    return name + ': ' + '; '.join(s)


def preview(d):
    os.makedirs(d, exist_ok=True)
    for tag, f in (('city', 'layer_city_off'), ('unlit', 'street_unlit')):
        A = load(os.path.join(ROOT, 'assets', f + '.webp'))[..., :3]
        for name, box in BOXES.items():
            x0, y0, x1, y1 = box
            Vb = load(os.path.join(EDITS, f'{name}_before_city.webp'))[..., :3]
            P = plan(name, box, Vb)
            V = A[y0:y1, x0:x1].copy()
            out = V.copy(); out[P['touch']] = repaint(V, P)[P['touch']]
            print(tag, measures(name, P, V, out))
            big = lambda a: Image.fromarray(np.clip(np.round(a), 0, 255).astype(np.uint8)).resize(((x1 - x0) * 3, (y1 - y0) * 3), Image.NEAREST)
            big(V).save(os.path.join(d, f'{name}_{tag}_before_x3.png')); big(out).save(os.path.join(d, f'{name}_{tag}_after_x3.png'))


if __name__ == '__main__':
    if '--befores' in sys.argv:
        befores()
    elif '--preview' in sys.argv:
        preview(sys.argv[sys.argv.index('--preview') + 1])
