#!/usr/bin/env python3
"""The road's bare asphalt between the kerbs, given the grain of old wet asphalt: its fine aggregate, from the far crossing
down to the bottom of the frame, on the painter's own tones.

    (a module: tools/redraw_zones.py's zone 'asphalt' calls draw() on the street as the zones before it leave it, last,
     after the lanes; it also writes the ground lights that fall on the asphalt, assets/gl_*.webp, each from its before
     crop, on the asphalt's own pixels only)
    python3 tools/asphalt_grain.py --befores       the zone's before copies (tools/src/edits/asphalt_before_{city,unlit}.webp:
                                                   the painter's pixels, as redraw_zones.py lays every zone's before copies
                                                   back) and the ground lights' (asphalt_before_<gl>.webp), once, from the
                                                   assets as they are
    python3 tools/asphalt_grain.py --preview DIR   the street's two layers with the zone drawn on them as they are (nothing
                                                   in assets/; to serve in their place with tools/dev/shot.cjs), and the
                                                   rows' tones before and after

What was there: next to the worn 止まれ and the worn lane lines (both from a real top-down texture), the bare asphalt was
the road's last smooth surface: large parts of it nearly flat (a 9 x 9 window's std under 1.6), right under the name on a
phone.

The texture (no new one): the asphalt between the paint of the image model's top-down sheet that 止まれ and the lane lines
already use, tools/src/edits/tomare_draft.webp: its right panel, the paint in a wheel path, half of it worn to the asphalt
(1.4 m across, 1.9 m along). Its paint is left out (its share over PAINT, in flakes over SPECK px, grown MARGIN px: the
lone bright chips of the aggregate kept); what is left is the asphalt's aggregate, its stones and the binder between them,
over its own mean (HP: the chips, not the stains), and the paint's holes are filled with the same asphalt from elsewhere
on the sheet (seeded shifts). The sheet shows no sealed cracks and no patches: none are added. On the road's ground (the
street's ground model, tools/zebra_crossing.py's and tools/lane_lines.py's: VP (700, 615), f 959.5 px, the eye 1.41 m
over the road), sheets laid side by side across and one after the other along, each its own way round (seeded). Each
pixel takes the exact mean of the ground it covers (tools/lane_lines.py's summed areas: a pixel at the bottom of the frame
covers 7 mm across and 3 cm along, one by the stop line 2 cm and 30 cm): the far rows smooth by that averaging, the near
ones showing the chips.

Its tones are the painter's: the grain is the painter's own value times 1 + AMP g (g the pixel's mean of the aggregate's
relative contrast), channel by channel, so the hue, the light (the street lamp's pool, the oden's orange, the hour, the
power cut, the red night) and the mean of each band of rows stay his; one tone per plane, no contrast added (each band's
mean and std measured before and after, --preview). Left as they are (the grain faded out round them): the kerbs and the
gutter's dark foot (ROAD), the lines and 止まれ (their own tools' coverage), the puddles and their reflections (wet.webp's
still water), the painter's cracks, patches' edges and specks (a pixel off its neighbours' median by over CRACK). The
ground lights that fall on the asphalt take the same factor (the light the ground sends back is its albedo's), from their
before crops; the wet ground and its mirror (wet.webp) are unchanged. The draws are seeded: the same bytes each time.
Needs numpy, scipy, Pillow.
"""
import os
import re
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as nd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lane_lines as LL                          # (the road's ground model, the summed-area means, the ground lights' list)
import tomare_marking as TM                      # (止まれ's coverage: left as it is)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDITS = os.path.join(ROOT, 'tools', 'src', 'edits')
BOX = (300, 680, 1100, 816)                      # the zone: the road between the kerbs, from the stop line down
VPX, VPY, F, EYE = LL.VPX, LL.VPY, LL.F, LL.EYE  # the street's ground model
PANEL = LL.PANELS[1]                             # the sheet's wheel-path panel: half of it bare asphalt between the flakes
PW, PH = LL.PW, LL.PH                            # the sheet on the ground (m): across, along the traffic
PAINT, SPECK, MARGIN = 0.25, 40, 3               # the sheet's paint: its share over PAINT (2 px smoothed), flakes over SPECK px, grown
HP = 14                                          # the aggregate over its own mean within this (sheet px, gaussian): chips, not stains
FILLS = 400                                      # the shifts tried to fill the paint's holes with the sheet's asphalt
AMP = 1.0                                        # the share of the sheet's own relative contrast (its asphalt's, as it is)
ROAD = (2.55, 2.72)                              # |X| (m): the grain whole inside, none past (the gutter's dark foot at ~2.82)
CRACK = (3.0, 6.0)                               # a pixel off its neighbours' median by more (luminance): the painter's, kept
PUDDLE = (1.5, 2.0)                              # the puddles kept: px from their still water, then the fade
SEED = 53

Zof = lambda y: F * EYE / (y - VPY)
Xof = lambda x, y: (x - VPX) * EYE / (y - VPY)


def aggregate():
    """the sheet's asphalt (1024 rows along the traffic, 511 columns across): each point's luminance over its asphalt's mean
    round it, minus one (the paint left out, its holes filled with the same sheet's asphalt from elsewhere), zero-mean"""
    A = np.asarray(Image.open(os.path.join(EDITS, 'tomare_draft.webp')).convert('RGB')).astype(float)
    L = (0.299 * A[..., 0] + 0.587 * A[..., 1] + 0.114 * A[..., 2])[:, PANEL[0]:PANEL[1]]
    P = np.clip((nd.gaussian_filter(L, LL.BEAD) - LL.LA) / (LL.LP - LL.LA), 0, LL.PMAX)
    lab, n = nd.label(nd.gaussian_filter(P, 2.0) > PAINT)
    size = nd.sum(np.ones_like(L), lab, np.arange(1, n + 1))
    flakes = np.isin(lab, np.where(size > SPECK)[0] + 1)          # (the lone bright stones of the aggregate are not paint)
    M = ~nd.binary_dilation(flakes, iterations=MARGIN)
    Lb = nd.gaussian_filter(L * M, HP) / np.maximum(nd.gaussian_filter(M.astype(float), HP), 1e-6)
    d = np.where(M, L / np.maximum(Lb, 1.0) - 1.0, 0.0)
    T, have = d.copy(), M.copy()
    rng = np.random.default_rng(SEED)
    H, W = L.shape
    for _ in range(FILLS):
        if have.all(): break
        s = (int(rng.integers(-H // 2, H // 2)), int(rng.integers(-W // 2, W // 2)))
        take = ~have & np.roll(M, s, (0, 1))
        T[take] = np.roll(d, s, (0, 1))[take]; have |= take
    T[~have] = 0.0
    return T - T.mean()


def ground(T, box=BOX):
    """the road's ground under the box (rows along Z from z0, columns across from X0 to X1): the sheet's asphalt laid side
    by side across and one after the other along, each its own way round and its own shift (seeded)"""
    x0, y0, x1, y1 = box
    H, Wp = T.shape
    X0, X1 = -ROAD[1] - 0.1, ROAD[1] + 0.1
    z0, z1 = Zof(y1 + 1.0), Zof(y0 - 1.0)
    nu = int(np.ceil((X1 - X0) / PW * Wp)); rows = int(np.ceil((z1 - z0) / PH * H))
    G = np.zeros((rows, nu))
    rng = np.random.default_rng(SEED + 1)
    for j in range(rows // H + 1):
        for i in range(nu // Wp + 1):
            t = np.roll(T, (int(rng.integers(H)), int(rng.integers(Wp))), (0, 1))
            if rng.random() < 0.5: t = t[::-1]
            if rng.random() < 0.5: t = t[:, ::-1]
            r0, c0 = j * H, i * Wp
            r1, c1 = min(rows, r0 + H), min(nu, c0 + Wp)
            if r1 > r0 and c1 > c0: G[r0:r1, c0:c1] = t[:r1 - r0, :c1 - c0]
    return G, (X0, X1, nu), (z0, PH / H)


def grain(box=BOX):
    """each pixel's exact mean of the aggregate's relative contrast over the ground it covers (its footprint, by summed
    areas), and |X| at its centre (m)"""
    x0, y0, x1, y1 = box
    G, (X0, X1, nu), (z0, dz) = ground(aggregate(), box)
    S = LL.sat(G)
    xs = np.arange(x0, x1, dtype=float)
    g = np.zeros((y1 - y0, x1 - x0))
    for r in range(y1 - y0):
        y = y0 + r; yc = y + 0.5
        ua = (np.clip(Xof(xs, yc), X0, X1) - X0) / (X1 - X0) * nu
        ub = (np.clip(Xof(xs + 1, yc), X0, X1) - X0) / (X1 - X0) * nu
        va, vb = (Zof(y + 1) - z0) / dz, (Zof(y) - z0) / dz
        g[r], _ = LL.box_mean(S, np.full(x1 - x0, va), np.full(x1 - x0, vb), ua, ub)
    ys, xs2 = np.mgrid[y0:y1, x0:x1].astype(float)
    return g, np.abs(Xof(xs2 + 0.5, ys + 0.5))


def feather(mask, inner, ramp):
    """0 on the mask and within inner px of it, 1 from inner + ramp px"""
    if not mask.any(): return np.ones(mask.shape)
    return np.clip((nd.distance_transform_edt(~mask) - inner) / ramp, 0, 1)


def plan(V0, box=BOX):
    """the factor each pixel's value takes (f) and where (w > 0), from the street's layer as the zones before it leave it"""
    x0, y0, x1, y1 = box
    g, aX = grain(box)
    wr = np.clip((ROAD[1] - aX) / (ROAD[1] - ROAD[0]), 0, 1)       # (the kerbs and the gutter's foot left out)
    lc, _, _ = LL.lines(box)
    tc, _ = TM.marking(box)
    paint = nd.binary_dilation((lc > 1e-3) | (tc > 1e-3))         # (the lines, the stop line and 止まれ as they are)
    wet = np.asarray(Image.open(os.path.join(ROOT, 'assets', 'wet.webp')).convert('RGB'))[y0 - 600:y1 - 600, x0:x1]
    wp = feather(wet[..., 2] > 0, *PUDDLE)                         # (the puddles and what they mirror)
    L = 0.299 * V0[..., 0] + 0.587 * V0[..., 1] + 0.114 * V0[..., 2]
    dev = np.abs(L - nd.median_filter(L, size=(5, 9)))
    wc = 1 - nd.grey_dilation(np.clip((dev - CRACK[0]) / (CRACK[1] - CRACK[0]), 0, 1), size=(3, 3))
    w = wr * ~paint * wp * wc
    return dict(f=1 + AMP * g * w, w=w, g=g)


def apply(V, P, have=None):
    """one layer's box (H, W, 3) with the grain (have: where the layer has pixels, a ground light's)"""
    m = P['w'] > 0
    if have is not None: m &= have
    out = V.copy()
    out[m] = V[m] * P['f'][m][:, None]
    return np.clip(out, 0, 255), m


def ground_lights():
    """the ground lights whose box touches the zone: (name, (x, y)) from street.js"""
    js = open(os.path.join(ROOT, 'assets', 'street.js'), encoding='utf-8').read()
    x0, y0, x1, y1 = BOX; out = []
    for m in re.finditer(r"url: 'assets/(gl_[a-z0-9_]+)\.webp\?v=\d+', box: \[(\d+), (\d+), (\d+), (\d+)\]", js):
        n, bx, by, bw, bh = m.group(1), *map(int, m.groups()[1:])
        if bx < x1 and bx + bw > x0 and by < y1 and by + bh > y0: out.append((n, (bx, by)))
    return out


def clip_box(gx, gy, g):
    x0, y0, x1, y1 = BOX
    return max(x0, gx), max(y0, gy), min(x1, gx + g.shape[1]), min(y1, gy + g.shape[0])


def draw(city, unlit, box=BOX):
    """The zone: both layers' boxes in place, the ground lights written on the asphalt's pixels; returns what changed
    (whole scene)."""
    x0, y0, x1, y1 = box
    H, W = city.shape[:2]
    P = plan(city[y0:y1, x0:x1, :3].copy(), box)
    for L in (city, unlit):
        L[y0:y1, x0:x1, :3], m = apply(L[y0:y1, x0:x1, :3], P)
    n_gl = 0
    for n, (gx, gy) in ground_lights():
        path = os.path.join(ROOT, 'assets', n + '.webp')
        g = np.asarray(Image.open(path).convert('RGBA')).astype(float)
        a, b, c, d = clip_box(gx, gy, g)
        gb = np.asarray(Image.open(os.path.join(EDITS, f'asphalt_before_{n}.webp')).convert('RGBA')).astype(float)
        full = np.zeros((y1 - y0, x1 - x0, 3)); full[b - y0:d - y0, a - x0:c - x0] = gb[..., :3]
        hv = np.zeros((y1 - y0, x1 - x0), bool); hv[b - y0:d - y0, a - x0:c - x0] = gb[..., 3] > 0
        out, mg = apply(full, P, hv)
        mm = mg[b - y0:d - y0, a - x0:c - x0]
        G = g.copy(); Gs = G[b - gy:d - gy, a - gx:c - gx]
        Gs[mm, :3] = out[b - y0:d - y0, a - x0:c - x0][mm]; Gs[mm, 3] = gb[mm, 3]
        if not np.array_equal(np.round(G), np.round(g)):
            LL.save(G, path); n_gl += 1
    print('asphalt: the grain on %d px, |g| %.3f near / %.3f far, factor %.3f-%.3f; %d ground lights' % (
        int(m.sum()), float(np.abs(P['g'][-20:]).mean()), float(np.abs(P['g'][:20]).mean()),
        float(P['f'].min()), float(P['f'].max()), n_gl))
    ch = np.zeros((H, W), bool); ch[y0:y1, x0:x1] = m
    return ch


def befores():
    """the zone's before copies: the layers as redraw_zones.py leaves them once it has laid every zone's before copies back
    (the painter's pixels; this zone's own left out), the ground lights' from the assets as they are"""
    import redraw_zones as rz
    x0, y0, x1, y1 = BOX
    for tag, f in (('city', 'layer_city_off'), ('unlit', 'street_unlit')):
        a = np.asarray(Image.open(os.path.join(ROOT, 'assets', f + '.webp')).convert('RGBA')).copy()
        for name, cfg in rz.ZONES.items():
            if name == 'asphalt': continue
            bx0, by0, bx1, by1 = cfg['box']
            a[by0:by1, bx0:bx1] = np.asarray(Image.open(os.path.join(EDITS, f'{name}_before_{tag}.webp')).convert('RGBA'))
        LL.save(a[y0:y1, x0:x1], os.path.join(EDITS, f'asphalt_before_{tag}.webp')); print('asphalt_before_' + tag)
    for n, (gx, gy) in ground_lights():
        g = np.asarray(Image.open(os.path.join(ROOT, 'assets', n + '.webp')).convert('RGBA'))
        a, b, c, d = clip_box(gx, gy, g)
        LL.save(g[b - gy:d - gy, a - gx:c - gx], os.path.join(EDITS, f'asphalt_before_{n}.webp'))
        print('asphalt_before_' + n, (a, b, c, d))


def bands(before, after, w, step=17):
    """each band of rows' mean, std and median local std (9 x 9, luminance) over the asphalt (w > 0.5), before -> after"""
    x0, y0, x1, y1 = BOX
    lum = lambda v: 0.299 * v[..., 0] + 0.587 * v[..., 1] + 0.114 * v[..., 2]
    def lstd(v):
        m = nd.uniform_filter(v, 9); return np.sqrt(np.maximum(nd.uniform_filter(v * v, 9) - m * m, 0))
    Lb, La = lum(before), lum(after); sb, sa = lstd(Lb), lstd(La)
    for r0 in range(0, y1 - y0, step):
        k = (slice(r0, r0 + step)); m = w[k] > 0.5
        if m.sum() < 50: continue
        print('rows %d-%d: mean %.2f -> %.2f, std %.2f -> %.2f, local std %.2f -> %.2f (%d px)' % (
            y0 + r0, y0 + min(r0 + step, y1 - y0) - 1, Lb[k][m].mean(), La[k][m].mean(), Lb[k][m].std(), La[k][m].std(),
            np.median(sb[k][m]), np.median(sa[k][m]), int(m.sum())))


def preview(d):
    """the street's layers with the zone drawn on them as they are (the zones before it already in), written into d"""
    os.makedirs(d, exist_ok=True)
    x0, y0, x1, y1 = BOX
    L = {}
    for f in ('layer_city_off', 'street_unlit'):
        L[f] = np.asarray(Image.open(os.path.join(ROOT, 'assets', f + '.webp')).convert('RGBA')).astype(float).copy()
    before = L['layer_city_off'][y0:y1, x0:x1, :3].copy()
    P = plan(before.copy())
    for f, a in L.items():
        a[y0:y1, x0:x1, :3], _ = apply(a[y0:y1, x0:x1, :3], P)
        LL.save(a, os.path.join(d, f + '.webp'))
    after = np.round(L['layer_city_off'][y0:y1, x0:x1, :3])
    bands(before, after, P['w'])
    np.save(os.path.join(d, 'asphalt_plan.npy'), dict(w=P['w'], g=P['g']), allow_pickle=True)


if __name__ == '__main__':
    if '--befores' in sys.argv:
        befores()
    elif '--preview' in sys.argv:
        preview(sys.argv[sys.argv.index('--preview') + 1])
