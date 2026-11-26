#!/usr/bin/env python3
"""The road's white lines as real road markings: the two edge lines (外側線) from the bottom of the frame to the stop line,
and the stop line (停止線) across the road before the far crossing, in the same old thermoplastic paint as 止まれ.

    (a module: tools/redraw_zones.py's zone 'lanes' calls draw() on the street as the zones before it leave it, last;
     it also writes the ground lights that carry the lines, assets/gl_*.webp, and the wet ground under them,
     assets/wet.webp, each from its before crop, on the lines' own pixels only)
    python3 tools/lane_lines.py --befores        the zone's before copies (tools/src/edits/lanes_before_{city,unlit}.webp:
                                                 the painter's pixels, as redraw_zones.py lays every zone's before copies
                                                 back), the ground lights' (lanes_before_gl_<gl>.webp) and the wet
                                                 ground's (lanes_wet_before.webp), once, from the assets as they are
    python3 tools/lane_lines.py --preview DIR    the layer's box before and after, x3 (nothing written in assets/)

What was there: three near-flat lavender bands (each one value from end to end, a few dark specks), next to the worn
止まれ stickers again, right under the name on a phone.

The geometry (the street's ground model, tools/zebra_crossing.py's: VP (700, 615), f 959.5 px, the eye 1.41 m over the
road), measured on the painter's lines: the edge lines are rays through the vanishing point, X -2.25 to -2.10 m and
+2.10 to +2.25 m (15 cm wide, as Japan's 外側線; both edges within 0.3 px of a ray, the pixel's own rounding), from the
bottom of the frame to row YTOP, just past the stop line; the stop line the painter's rows 680-681.6 (about 0.5 m on the
ground at 20.5 m) between his ends, x 588.4 to 811.6. Their shapes and places are those, each pixel's share of a line the
exact area of the pixel it covers (sub-rows), then crisp on the pixel grid (CRISP).

The paint (tools/tomare_marking.py's, accepted on 24/11; no new texture): its texture the image model's top-down sheet of
old thermoplastic, tools/src/edits/tomare_draft.webp (its left panel the paint off the wheels, its right one the same
paint in a wheel path, half of it worn to the asphalt in flakes drawn out along the traffic; 1.4 m across, 1.9 m along),
laid on each line's own ground: the edge lines take strips of the sheet as wide as the line, one after the other along
it (each 1.9 m a strip of its own, seeded), the stop line the sheet's panels side by side across the road (a band of
rows as deep as the line, seeded). Wear where the wheels run (the far crossing's tracks, +-0.55 and +-2.05 m): the stop
line, where cars brake and stop, mostly the worn panel in the tracks and a little of it everywhere (WSTOP); the edge
lines only lightly, their inner edge, by the outer wheels, more than their outer one (WEDGE). Each pixel the exact mean
of the ground it covers (its footprint on the line's ground, by summed areas): the far stop line, a pixel 0.3 m along
the road, smooth along and broken across in the tracks; the near edge lines, a pixel 3 cm along, their chips. Then, as
止まれ: the wear brought to the painting's pixel (SHARP, LEVELS, WORN), the raised edge (LIP), the paint darker where the
road is wetter (WETD).

Its tones are the painter's, layer by layer, as tools/tomare_marking.py does (the street, the power cut, each ground
light that falls on the lines): where a line was and is no more, the asphalt (its light smoothed from the asphalt round
it, ROAD: the gutters' concrete and the kerbs left out, and 止まれ, and the puddles) with the grain of an asphalt pixel
near it; the paint, that asphalt times the paint's own ratio to it (the old lines' median, channel by channel, in that
layer), with a share (GRAIN) of the grain of a pixel of the old paint of the same line; worn, the asphalt between. So the
hours, the street lamp's pool, the oden's orange, the power cut and the red night take the lines as they take the road.
The wet ground (wet.webp, from its before crop): the paint stands proud of the water, so it is a little less of a mirror
than the asphalt (its wetness, R, times 1 - DRY); the puddles (B) are left as they are, and the wet ground in them too.
Only the lines' pixels change (the kerbs, the sidewalks, 止まれ, the far crossing and the puddles as they were). The
draws are seeded: the same bytes each time. Needs numpy, scipy, Pillow.
"""
import os
import re
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as nd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDITS = os.path.join(ROOT, 'tools', 'src', 'edits')
BOX = (376, 678, 1024, 816)                      # the zone: the three lines (rows 678-679 only read: the asphalt before the line)
VPX, VPY, F, EYE = 700.0, 615.0, 959.5, 1.41     # the street's ground model (tools/zebra_crossing.py's)
EDGES = ((-2.25, -2.10), (2.10, 2.25))           # the edge lines across the road (m): rays through VP, measured
YTOP = 682.4                                     # their far end (row), past the stop line
STOP = (588.4, 811.6, 680.0, 681.62)             # the stop line: its painted ends (x) and its edges (rows), measured
PANELS = ((0, 511), (513, 1024))                 # tomare_draft.webp's two panels' columns: the paint off the wheels, in a wheel path
PW, PH = 1.4, 1.9                                # a panel on the ground (m): across, along the traffic
BEAD = 1.0                                       # the sheet's glass-bead sand (draft px, 2-3 mm) smoothed: under the near pixel
LA, LP, PMAX = 80.0, 185.0, 1.15                 # the draft's luminance: its bare asphalt, its whole paint (tools/tomare_marking.py)
WHEELS, WSIG = (-2.05, -0.55, 0.55, 2.05), 0.16  # the wheel paths (m) and their spread (tools/zebra_crossing.py's)
WEDGE = 0.25                                     # the edge lines' share of worn paint at a track's centre (lightly)
WSTOP = (0.1, 0.55)                              # the stop line's: everywhere, and more at a track's centre
GRAIN = 0.5                                      # (tools/tomare_marking.py's: the old paint's grain kept)
CRISP = 1.5                                      # the edges' coverage steepened (crisp on the pixel grid)
SHARP, LEVELS, WORN = 0.8, 4, 1.3                # the wear's contrast over a pixel's neighbours, its steps, its curve
LIP = (0.07, 0.05)                               # the raised edge: its face toward the eye a little darker, its far rim lighter
WETD, DRY = 0.08, 0.25                           # the paint darker where the road is wetter; its wetness less than the asphalt's
ROAD = 2.7                                       # |X| (m) of the asphalt read for the road's light (the gutters and kerbs outside)
LETTERS = (620, 780, 682)                        # 止まれ's columns (from its first row): left out of the asphalt read
SUBY = 16
SEED = 41
OUT = os.path.join(ROOT, 'assets')               # (where the ground lights and the wet ground are written)

Zof = lambda y: F * EYE / (y - VPY)
Xof = lambda x, y: (x - VPX) * EYE / (y - VPY)


def panels():
    """the draft's two panels (1024 rows along the traffic, 511 columns across): the paint's share of each point, its
    asphalt 0 and its whole paint 1 (a greyer, dirtier paint under 1, a cleaner one a little over, up to PMAX)"""
    A = np.asarray(Image.open(os.path.join(EDITS, 'tomare_draft.webp')).convert('RGB')).astype(float)
    L = 0.299 * A[..., 0] + 0.587 * A[..., 1] + 0.114 * A[..., 2]
    return [np.clip((nd.gaussian_filter(L[:, c0:c1], BEAD) - LA) / (LP - LA), 0.0, PMAX) for c0, c1 in PANELS]


def band(X):
    """the wheel paths' weight at X (m): 1 at a track's centre"""
    return np.max([np.exp(-0.5 * ((X - c) / WSIG) ** 2) for c in WHEELS], 0)


def edge_ground(X0, X1, z0, z1, rng):
    """an edge line's ground (rows along Z from z0, columns across from X0 to X1): strips of the sheet as wide as the line,
    one after the other along it (each 1.9 m its own strip, seeded), the worn panel's share by the wheels"""
    pw, pr = panels(); H, Wp = pw.shape
    nu = int(round((X1 - X0) / PW * Wp)); ns = Wp // nu
    rows = int(np.ceil((z1 - z0) / PH * H))
    X = X0 + (np.arange(nu) + 0.5) / nu * (X1 - X0)
    w = WEDGE * band(X)[None, :]
    segs, order = [], rng.permutation(ns)
    for j in range(rows // H + 1):
        s = order[j % ns] * nu
        a, b = pw[:, s:s + nu], pr[:, s:s + nu]
        if j % 2: a, b = a[::-1], b[::-1]
        if rng.random() < 0.5: a, b = a[:, ::-1], b[:, ::-1]
        segs.append(a * (1 - w) + b * w)
    return np.concatenate(segs, 0)[:rows], (X0, X1, nu), (z0, PH / H)


def stop_ground(X0, X1, z0, z1, rng):
    """the stop line's ground (rows along Z from z0, columns across from X0 to X1): the sheet's panels side by side across
    the road, each a band of rows as deep as the line (seeded), the worn panel's share everywhere and more in the tracks"""
    pw, pr = panels(); H, Wp = pw.shape
    nu = int(np.ceil((X1 - X0) / PW * Wp)); rows = int(np.ceil((z1 - z0) / PH * H))
    X = X0 + (np.arange(nu) + 0.5) / nu * (X1 - X0)
    w = (WSTOP[0] + WSTOP[1] * band(X))[None, :]
    a = np.zeros((rows, nu)); b = np.zeros((rows, nu))
    for i in range(nu // Wp + 1):
        r = rng.integers(0, H - rows); c0, c1 = i * Wp, min(nu, (i + 1) * Wp)
        pa_, pb_ = pw[r:r + rows], pr[r:r + rows]
        if i % 2: pa_, pb_ = pa_[:, ::-1], pb_[:, ::-1]
        a[:, c0:c1], b[:, c0:c1] = pa_[:, :c1 - c0], pb_[:, :c1 - c0]
    return a * (1 - w) + b * w, (X0, X1, nu), (z0, (z1 - z0) / rows)


def sat(T):
    S = np.zeros((T.shape[0] + 1, T.shape[1] + 1)); S[1:, 1:] = T.cumsum(0).cumsum(1)
    return S


def sat_at(S, v, u):
    """the summed area S at fractional (v, u), bilinear"""
    nv, nu = S.shape[0] - 1, S.shape[1] - 1
    v = np.clip(v, 0, nv); u = np.clip(u, 0, nu)
    i = np.minimum(np.floor(v).astype(int), nv - 1); j = np.minimum(np.floor(u).astype(int), nu - 1)
    fv, fu = v - i, u - j
    return (S[i, j] * (1 - fv) * (1 - fu) + S[i + 1, j] * fv * (1 - fu) + S[i, j + 1] * (1 - fv) * fu + S[i + 1, j + 1] * fv * fu)


def box_mean(S, v0, v1, u0, u1):
    area = (v1 - v0) * (u1 - u0)
    s = sat_at(S, v1, u1) - sat_at(S, v0, u1) - sat_at(S, v1, u0) + sat_at(S, v0, u0)
    return np.where(area > 1e-9, s / np.maximum(area, 1e-9), 0.0), area


def lines(box=BOX):
    """each pixel's share of a line (cov: the exact area, by sub-rows), the paint's share still there in it (f: the exact
    mean of the line's ground the pixel covers), and which line it is (lab: 1 the stop line, 2 the left edge, 3 the right)"""
    x0, y0, x1, y1 = box
    H, W = y1 - y0, x1 - x0
    xs = np.arange(x0, x1, dtype=float)
    cov = np.zeros((H, W)); q = np.zeros((H, W)); lab = np.zeros((H, W), int)
    rng = np.random.default_rng(SEED)
    zb = Zof(y1 + 1.0)
    grounds = [('stop', stop_ground(-2.6, 2.6, Zof(STOP[3]), Zof(STOP[2]), rng))]
    for X0, X1 in EDGES:
        grounds.append(('edge', edge_ground(X0, X1, zb, Zof(YTOP), rng)))
    for n, (kind, (T, (X0, X1, nu), (z0, dz))) in enumerate(grounds):
        S = sat(T)
        for r in range(H):
            y = y0 + r
            ys = y + (np.arange(SUBY) + 0.5) / SUBY
            if kind == 'stop':
                lo = np.full(SUBY, STOP[0]); hi = np.full(SUBY, STOP[1]); on = (ys >= STOP[2]) & (ys < STOP[3])
                ya, yb = max(y, STOP[2]), min(y + 1, STOP[3])
            else:
                lo = VPX + X0 * (ys - VPY) / EYE; hi = VPX + X1 * (ys - VPY) / EYE; on = ys >= YTOP
                ya, yb = max(y, YTOP), y + 1
            if not on.any(): continue
            c = np.clip(np.minimum(xs[:, None] + 1, hi[None, :]) - np.maximum(xs[:, None], lo[None, :]), 0, 1)
            c = (c * on[None, :]).mean(1)
            if c.max() <= 0: continue
            yc = (ya + yb) / 2
            ea, eb = (STOP[0], STOP[1]) if kind == 'stop' else (VPX + X0 * (yc - VPY) / EYE, VPX + X1 * (yc - VPY) / EYE)
            ua = (Xof(np.clip(xs, ea, eb), yc) - X0) / (X1 - X0) * nu
            ub = (Xof(np.clip(xs + 1, ea, eb), yc) - X0) / (X1 - X0) * nu
            va, vb = (Zof(yb) - z0) / dz, (Zof(ya) - z0) / dz
            m, _ = box_mean(S, np.full(W, va), np.full(W, vb), ua, ub)
            cov[r] += c; q[r] += c * m; lab[r][c > 0] = n + 1
    f = np.where(cov > 0, q / np.maximum(cov, 1e-9), 0.0)
    return np.clip(cov, 0, 1), np.clip(f, 0, PMAX), lab


def lisse(v, w, sy, sx):
    num = nd.gaussian_filter(v * w[..., None], (sy, sx, 0)); den = nd.gaussian_filter(w.astype(float), (sy, sx))[..., None]
    return num / np.maximum(den, 1e-6)


def plan(V0, wet, box=BOX):
    """what goes and what comes, and the pixels each one's grain is drawn from (seeded): from the street's layer (V0, the
    zone's box as the zones before it leave it: the painter's lines there) and the wet ground's before crop"""
    x0, y0, x1, y1 = box
    H, W = V0.shape[:2]
    cov, f, lab = lines(box)
    c2 = np.clip((cov - 0.5) * CRISP + 0.5, 0, 1)                 # (the lines' edges crisp on the pixel grid)
    ins = (cov > 0.5).astype(float)                               # (the wear crisp on the pixel grid, as 止まれ's)
    fb = nd.gaussian_filter(f * ins, 1.0) / np.maximum(nd.gaussian_filter(ins, 1.0), 1e-6)
    f = np.where(ins > 0, np.clip(f + SHARP * (f - fb), 0, PMAX), f)
    f = np.where(f < 1, (np.round(np.clip(f, 0, 1) * LEVELS) / LEVELS) ** WORN, f)
    new = c2 * f
    pad = np.pad(c2, ((1, 1), (0, 0)))
    near, far = np.clip(c2 - pad[2:], 0, 1), np.clip(c2 - pad[:-2], 0, 1)
    mult = (1 - LIP[0] * near + LIP[1] * far) * (1 - WETD * np.clip(wet[..., 0] / 128.0, 0, 1))
    ys, xs = np.mgrid[y0:y1, x0:x1].astype(float)
    road = np.abs(Xof(xs + 0.5, np.maximum(ys + 0.5, VPY + 1))) < ROAD
    letters = np.zeros((H, W), bool); letters[LETTERS[2] - y0:, LETTERS[0] - x0:LETTERS[1] - x0] = True
    near_l = nd.binary_dilation((cov > 0) & (lab > 1), iterations=2)   # (the old lines are read only next to the new ones:
    near_l |= nd.binary_dilation((cov > 0) & (lab == 1), np.ones((1, 5)), iterations=1)   # the stop line on its rows)
    near_l &= ~letters
    away = ~nd.binary_dilation((cov > 0) & (lab > 1), iterations=3) & ~nd.binary_dilation((cov > 0) & (lab == 1), np.ones((1, 7)))
    clean = road & away & ~letters & (wet[..., 2] == 0)           # (the asphalt: the rows either side of the stop line in it)
    As0 = lisse(V0, clean, 1.0, 10)
    e = V0[..., 2] - As0[..., 2]                                  # (the old paint's blue over the asphalt's)
    full = (cov > 0.99) & near_l
    cov0 = np.zeros((H, W))
    for n in (1, 2, 3):
        m = full & (nd.grey_dilation(lab, size=5) == n)
        p = np.percentile(e[m], 70) if m.sum() > 20 else 60.0
        z = near_l & (nd.grey_dilation(lab, size=5) == n)
        cov0[z] = np.clip(e[z] / max(p, 1.0), 0, 1)
    labn = nd.grey_dilation(lab, size=5)
    old = cov0 > 0.1
    touch = (old | (cov > 1e-3)) & (np.arange(H)[:, None] + y0 >= STOP[2]) & ~letters
    paint = (cov0 > 0.85) & full
    rng = np.random.default_rng(SEED)
    pa = np.zeros((H, W, 2), int); pp = np.zeros((H, W, 2), int)
    prow = {n: np.where((paint & (labn == n)).any(1))[0] for n in (1, 2, 3)}
    for r, c in zip(*np.where(touch)):
        ra, rb = max(0, r - 2), min(H, r + 3)
        for d in range(30, W, 10):
            cl = clean[ra:rb, max(0, c - d):c + d + 1]
            if cl.sum() >= 8: break
        cr, cc = np.where(cl)
        k = rng.integers(len(cr)); pa[r, c] = (cr[k] + ra, cc[k] + max(0, c - d))
        n = labn[r, c] if labn[r, c] else 1
        pr_ = prow[n]
        near_r = pr_[np.argsort(np.abs(pr_ - r), kind='stable')][:3]
        cand = [(a, b) for a in near_r for b in np.where(paint[a] & (labn[a] == n))[0] if abs(b - c) <= 60]
        if not cand: cand = [(a, b) for a in near_r for b in np.where(paint[a] & (labn[a] == n))[0]]
        pp[r, c] = cand[rng.integers(len(cand))]
    return dict(new=new, cov=c2, mult=mult, old=old, touch=touch, clean=clean, paint=paint, pa=pa, pp=pp, cov0=cov0, lab=labn)


def repaint(V, P, have=None):
    """one layer's box (H, W, 3) with the new lines (have: where the layer has pixels, a ground light's)"""
    have = np.ones(V.shape[:2], bool) if have is None else have
    As = lisse(V, P['clean'] & have, 1.0, 10)
    pm = P['paint'] & have
    k = np.clip(np.median(V[pm], 0) / np.maximum(np.median(As[pm], 0), 1e-3), 1.0, 6.0) if pm.sum() > 20 else np.ones(3)
    out = V.copy()
    for r, c in zip(*np.where(P['touch'] & have)):
        a, b = P['pa'][r, c]; e, f = P['pp'][r, c]
        base = As[r, c] + (V[a, b] - As[a, b]) * have[a, b] if P['old'][r, c] else V[r, c]
        pnt = (As[r, c] * k + (V[e, f] - As[e, f] * k) * GRAIN * have[e, f]) * P['mult'][r, c]
        q = P['new'][r, c]
        out[r, c] = (1 - q) * base + q * pnt
    return np.clip(out, 0, 255)


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


def save(a, path, mode='RGBA'):
    Image.fromarray(np.clip(np.round(a), 0, 255).astype(np.uint8), mode).save(path, 'WEBP', lossless=True, quality=100, method=6, exact=True)


def wet_before():
    return np.asarray(Image.open(os.path.join(EDITS, 'lanes_wet_before.webp')).convert('RGB')).astype(float)


def draw(city, unlit, box=BOX):
    """The zone: both layers' boxes in place, the ground lights and the wet ground written on the lines' pixels; returns
    what changed (whole scene)."""
    x0, y0, x1, y1 = box
    H, W = city.shape[:2]
    wet = wet_before()
    P = plan(city[y0:y1, x0:x1, :3].copy(), wet, box)
    t = P['touch']
    for L in (city, unlit):
        V = L[y0:y1, x0:x1, :3]
        V[t] = repaint(V.copy(), P)[t]
    for n, (gx, gy) in ground_lights():
        path = os.path.join(OUT, n + '.webp')
        g = np.asarray(Image.open(os.path.join(ROOT, 'assets', n + '.webp')).convert('RGBA')).astype(float).copy()
        a, b, c, d = clip_box(gx, gy, g)
        gb = np.asarray(Image.open(os.path.join(EDITS, f'lanes_before_{n}.webp')).convert('RGBA')).astype(float)
        full = np.zeros((y1 - y0, x1 - x0, 3)); full[b - y0:d - y0, a - x0:c - x0] = gb[..., :3]
        hv = np.zeros((y1 - y0, x1 - x0), bool); hv[b - y0:d - y0, a - x0:c - x0] = gb[..., 3] > 0
        out = repaint(full, P, hv)
        m = (t & hv)[b - y0:d - y0, a - x0:c - x0]
        G = g[b - gy:d - gy, a - gx:c - gx]
        G[m, :3] = out[b - y0:d - y0, a - x0:c - x0][m]; G[m, 3] = gb[m, 3]
        save(g, path)
    w = np.asarray(Image.open(os.path.join(ROOT, 'assets', 'wet.webp')).convert('RGB')).astype(float).copy()
    wb = wet.copy(); q = np.clip(P['new'], 0, 1)
    dry = t & (wet[..., 2] == 0)                                  # (the puddles left as they are)
    wb[..., 0] = np.where(dry, wet[..., 0] * (1 - DRY * q), wet[..., 0])
    W0 = w[y0 - 600:y1 - 600, x0:x1]; W0[t] = wb[t]
    save(w, os.path.join(OUT, 'wet.webp'), 'RGB')
    print('lanes: edge lines X %s m from row %.1f, stop line x %.1f-%.1f rows %.2f-%.2f; paint kept %.2f; %d px' % (
        EDGES, YTOP, STOP[0], STOP[1], STOP[2], STOP[3], float(P['new'].sum() / max(P['cov'].sum(), 1)), int(t.sum())))
    ch = np.zeros((H, W), bool); ch[y0:y1, x0:x1] = t
    return ch


def befores():
    """the zone's before copies: the layers as redraw_zones.py leaves them once it has laid every zone's before copies back
    (the painter's pixels; this zone's own left out), the ground lights' and the wet ground's from the assets as they are"""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import redraw_zones as rz
    x0, y0, x1, y1 = BOX
    for tag, f in (('city', 'layer_city_off'), ('unlit', 'street_unlit')):
        a = np.asarray(Image.open(os.path.join(ROOT, 'assets', f + '.webp')).convert('RGBA')).copy()
        for name, cfg in rz.ZONES.items():
            if name == 'lanes': continue
            bx0, by0, bx1, by1 = cfg['box']
            a[by0:by1, bx0:bx1] = np.asarray(Image.open(os.path.join(EDITS, f'{name}_before_{tag}.webp')).convert('RGBA'))
        save(a[y0:y1, x0:x1], os.path.join(EDITS, f'lanes_before_{tag}.webp')); print('lanes_before_' + tag)
    for n, (gx, gy) in ground_lights():
        g = np.asarray(Image.open(os.path.join(ROOT, 'assets', n + '.webp')).convert('RGBA'))
        a, b, c, d = clip_box(gx, gy, g)
        save(g[b - gy:d - gy, a - gx:c - gx], os.path.join(EDITS, f'lanes_before_{n}.webp')); print('lanes_before_' + n, (a, b, c, d))
    w = np.asarray(Image.open(os.path.join(ROOT, 'assets', 'wet.webp')).convert('RGB'))
    save(w[y0 - 600:y1 - 600, x0:x1], os.path.join(EDITS, 'lanes_wet_before.webp'), 'RGB'); print('lanes_wet_before')


def preview(d):
    """the layer's box before and after, x3, written into d (nothing in assets/)"""
    x0, y0, x1, y1 = BOX
    city = np.asarray(Image.open(os.path.join(ROOT, 'assets', 'layer_city_off.webp')).convert('RGBA')).astype(float).copy()
    before = city[y0:y1, x0:x1, :3].copy()
    P = plan(before.copy(), wet_before())
    after = before.copy(); after[P['touch']] = repaint(before.copy(), P)[P['touch']]
    os.makedirs(d, exist_ok=True)
    big = lambda a: Image.fromarray(np.clip(np.round(a), 0, 255).astype(np.uint8)).resize(((x1 - x0) * 3, (y1 - y0) * 3), Image.NEAREST)
    big(before).save(os.path.join(d, 'lanes_before_x3.png')); big(after).save(os.path.join(d, 'lanes_after_x3.png'))
    np.save(os.path.join(d, 'lanes_plan.npy'), dict(new=P['new'], cov0=P['cov0'], touch=P['touch'], cov=P['cov']), allow_pickle=True)
    print('paint kept', round(float(P['new'].sum() / max(P['cov'].sum(), 1)), 3), 'touched', int(P['touch'].sum()))


if __name__ == '__main__':
    if '--befores' in sys.argv:
        befores()
    elif '--preview' in sys.argv:
        preview(sys.argv[sys.argv.index('--preview') + 1])
