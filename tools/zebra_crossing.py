#!/usr/bin/env python3
"""The far zebra crossing (横断歩道), past 止まれ and its stop line, as real road markings at that distance: five stripes of
worn thermoplastic paint on the wet road, laid on the ground plane in the street's camera.

    (a module: tools/redraw_zones.py's zone 'zebra' calls draw() on the street as the zones before it leave it, last;
     it also writes the ground lights that fall on the stripes, assets/gl_*.webp, and the wet ground under them,
     assets/wet.webp, each from its before crop)
    python3 tools/zebra_crossing.py --befores        the zone's before copies (tools/src/edits/zebra_before_{city,unlit}.webp),
                                                     the ground lights' (zebra_before_gl_<gl>.webp) and the wet ground's
                                                     (zebra_wet_before.webp), once, from the assets as they are, before the
                                                     zone is first run
    python3 tools/zebra_crossing.py --preview DIR    the layer's box before and after, x8 (nothing written)

What was there: five pink-white blocks, each one flat value from edge to edge in the layer and in every ground light that
falls on them (the oden's orange, the Pokemon Center's shop), the brightest things on the road at 22 h: stickers.

The geometry (the street's ground model: VP (700, 615), f 959.5 px, the eye 1.41 m over the road): Japan's crossing
(道路標識、区画線及び道路標示に関する命令, 横断歩道 201): stripes 45 cm wide, 45 cm apart (45-50 cm; up to 90 cm since 2024),
along the traffic; the carriageway here 5.63 m between the kerbs' feet (X -2.82 .. +2.81 m, measured at rows 664-674),
its edge lines at +-2.2 m, the concrete gutters outside them: five stripes (4.05 m) centred on it, X 0, +-0.9, +-1.8 m,
from Z 22.95 to 26.95 m (a 4 m crossing, the painter's rows 665-673; the stop line 2.3 m before it, at 680). The
painter had the widths right; his edges are kept within a pixel, now each one on its ray.

The paint (R2: the painter's own pixels, layer by layer, as tools/tomare_marking.py does): the asphalt where a stripe was
and is no more (its row's light smoothed along it from the asphalt round it, the grain of an asphalt pixel of the same
row); the paint, that asphalt times the paint's own ratio to it (the old stripes' median, channel by channel, in that
layer), its excess over the asphalt kept at PAINT only (old thermoplastic, dirty, at 25 m in the rain: as dark as the far
road, no longer the brightest thing on it), with the grain of a pixel of the old paint (scaled alike). Worn as such paint
wears (WEAR): the tyres take it off in the wheel paths (two cars' tracks, one each way, at +-0.55 and +-2.05 m: the inner
edges of the +-0.9 stripes, the outer ones of the +-1.8), chipped elsewhere; the wear a value noise on the ground plane
(in metres, so foreshortened as the road is), the edges a little ragged; each pixel the share of its SUB x SUB points of
ground that still have paint, the asphalt showing through the rest. No light of its own: the ground lights that fall
there (the oden's orange from the left, the Center's shop from the right) repainted the same way (the paint gives back
more of a light than the asphalt, the worn patches as the asphalt), so the stripes take the light that is really there,
its falloff across them, and go dark with it (its hours, the power cut, red in the red night); the wet pass's live sheen
(the far city, the far house, its lantern) lies on them as on the rest of the road. The wet ground: the paint stands a
few millimetres proud, so the puddles' still water (wet.webp's B) stays in the gaps and drains off the stripes; on them a
film of rain over a smooth surface, a sharper sheen than the rough asphalt's (B at SHEEN, R at least FILM). The draws
are seeded: the same bytes each time. Needs numpy, scipy, Pillow.
"""
import os
import re
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as nd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDITS = os.path.join(ROOT, 'tools', 'src', 'edits')
BOX = (600, 658, 800, 680)                       # the zone: the crossing and the asphalt round it, short of the stop line (680)
VPX, VPY, F, EYE = 700.0, 615.0, 959.5, 1.41     # the street's ground model (tools/facade_foot.py, tools/arcade_eave.py)
XC, HW = (-1.8, -0.9, 0.0, 0.9, 1.8), 0.225      # the stripes' centres across the road and their half width (m)
ZN, ZF = 22.95, 26.95                            # the crossing's near and far edges (m)
PAINT = 0.75                                     # the share of the paint's excess over the asphalt kept
WHEELS, WSIG = (-2.05, -0.55, 0.55, 2.05), 0.16  # the wheel paths (m) and their spread
WEAR = dict(chip=0.12, path=0.45, rag=0.02)      # the chipped share, the extra share worn in a wheel path, the edges' wobble (m)
NS = (0.07, 0.9, 0.025, 0.3)                     # the wear's noise: its cells across and along the road (m), two octaves
FILM, SHEEN = 48.0, 80.0                         # wet.webp on the paint: its wetness at least (R), its smoothness (B)
SUB = 6
SEED = 21
COLS = (606, 795)                                # the asphalt read for the row's light (the kerbs' feet outside)

Zof = lambda y: F * EYE / (y - VPY)
Xof = lambda x, Z: (x - VPX) * Z / F
lum = lambda z: 0.299 * z[..., 0] + 0.587 * z[..., 1] + 0.114 * z[..., 2]


def vnoise(X, Z, sx, sz, seed):
    """value noise on the ground plane (cells sx x sz m, smooth between them), 0..1"""
    rng = np.random.default_rng(seed); G = rng.random((64, 64))
    u, v = X / sx + 32.0, Z / sz
    i0, j0 = np.floor(u).astype(int), np.floor(v).astype(int); fu, fv = u - i0, v - j0
    fu, fv = fu * fu * (3 - 2 * fu), fv * fv * (3 - 2 * fv)
    g = lambda i, j: G[np.mod(j, 64), np.mod(i, 64)]
    return (g(i0, j0) * (1 - fu) + g(i0 + 1, j0) * fu) * (1 - fv) + (g(i0, j0 + 1) * (1 - fu) + g(i0 + 1, j0 + 1) * fu) * fv


def coverage(box=BOX):
    """each pixel's share of ground inside a stripe (cov) and of ground still painted (paint), 0..1: SUB x SUB points"""
    x0, y0, x1, y1 = box
    ys, xs = np.mgrid[y0:y1, x0:x1].astype(float)
    cov = np.zeros(ys.shape); pnt = np.zeros(ys.shape)
    for i in range(SUB):
        for j in range(SUB):
            Z = Zof(ys + (i + 0.5) / SUB); X = Xof(xs + (j + 0.5) / SUB, Z)
            along = (Z >= ZN) & (Z < ZF)
            rag = WEAR['rag'] * (2 * vnoise(X, Z, 0.5, 0.08, SEED + 1) - 1)
            ins = np.zeros(ys.shape, bool)
            for c in XC: ins |= np.abs(X - c) < HW + rag
            ins &= along
            band = np.max([np.exp(-0.5 * ((X - w) / WSIG) ** 2) for w in WHEELS], 0)
            n = 0.65 * vnoise(X, Z, NS[0], NS[1], SEED) + 0.35 * vnoise(X, Z, NS[2], NS[3], SEED + 2)
            worn = n < WEAR['chip'] + WEAR['path'] * band
            cov += ins; pnt += ins & ~worn
    return cov / SUB ** 2, pnt / SUB ** 2


def old_paint(V):
    """the old stripes' coverage, 0..1, from the street's layer (its blue over each row's asphalt), rows 663-675"""
    b = V[..., 2]; c = np.zeros_like(b)
    for r in range(b.shape[0]):
        if not 663 <= BOX[1] + r <= 675: continue
        row = b[r]; a = np.median(row); m = row > a + 35
        p = np.percentile(row[m], 80) if m.sum() > 3 else a + 80
        c[r] = np.clip((row - a) / max(p - a, 1), 0, 1)
    c[:, :COLS[0] - BOX[0]] = 0; c[:, COLS[1] - BOX[0]:] = 0
    return c


def lisse(v, w, sy, sx):
    num = nd.gaussian_filter(v * w[..., None], (sy, sx, 0)); den = nd.gaussian_filter(w.astype(float), (sy, sx))[..., None]
    return num / np.maximum(den, 1e-6)


def plan(V0):
    """what goes and what comes, and the pixels each one's grain is drawn from (seeded): from the street's layer"""
    cov0 = old_paint(V0)
    cov, pnt = coverage(BOX)
    old = nd.binary_dilation(cov0 > 0.12)
    touch = old | (cov > 0)
    H, W = cov0.shape
    cols = np.zeros((H, W), bool); cols[:, COLS[0] - BOX[0]:COLS[1] - BOX[0]] = True
    clean = ~nd.binary_dilation(cov0 > 0.05, iterations=2) & cols
    paint = cov0 > 0.85
    rng = np.random.default_rng(SEED)
    prow = np.where(paint.any(1))[0]
    pa = np.zeros((H, W, 2), int); pp = np.zeros((H, W, 2), int)
    for r, c in zip(*np.where(touch)):
        for d in range(40, W, 10):
            cs = np.where(clean[r, max(0, c - d):c + d + 1])[0] + max(0, c - d)
            if len(cs) >= 8: break
        pa[r, c] = (r, cs[rng.integers(len(cs))])
        near = prow[np.argsort(np.abs(prow - r), kind='stable')][:3]
        cand = [(a, b) for a in near for b in np.where(paint[a])[0]]
        pp[r, c] = cand[rng.integers(len(cand))]
    return dict(new=pnt, cov=cov, old=old, touch=touch, clean=clean, paint=paint, pa=pa, pp=pp)


def repaint(V, P, have=None):
    """one layer's box (H, W, 3) with the new stripes (have: where the layer has pixels, a ground light's box)"""
    have = np.ones(V.shape[:2], bool) if have is None else have
    As = lisse(V, P['clean'] & have, 1.0, 10)
    pm = P['paint'] & have
    k = np.clip(np.median(V[pm], 0) / np.maximum(np.median(As[pm], 0), 1e-3), 1.0, 6.0) if pm.sum() > 20 else np.ones(3)
    kn = 1 + (k - 1) * PAINT
    out = V.copy()
    for r, c in zip(*np.where(P['touch'] & have)):
        a, b = P['pa'][r, c]; e, f = P['pp'][r, c]
        base = As[r, c] + (V[a, b] - As[a, b]) * have[a, b] if P['old'][r, c] else V[r, c]
        pnt = As[r, c] * kn + (V[e, f] - As[e, f] * k) * PAINT * have[e, f]
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
    Image.fromarray(np.round(a).astype(np.uint8), mode).save(path, 'WEBP', lossless=True, quality=100, method=6, exact=True)


def befores():
    x0, y0, x1, y1 = BOX
    for tag, f in (('city', 'layer_city_off'), ('unlit', 'street_unlit')):
        a = np.asarray(Image.open(os.path.join(ROOT, 'assets', f + '.webp')).convert('RGBA'))
        save(a[y0:y1, x0:x1], os.path.join(EDITS, f'zebra_before_{tag}.webp')); print('zebra_before_' + tag)
    for n, (gx, gy) in ground_lights():
        g = np.asarray(Image.open(os.path.join(ROOT, 'assets', n + '.webp')).convert('RGBA'))
        a, b, c, d = clip_box(gx, gy, g)
        save(g[b - gy:d - gy, a - gx:c - gx], os.path.join(EDITS, f'zebra_before_{n}.webp')); print('zebra_before_' + n, (a, b, c, d))
    w = np.asarray(Image.open(os.path.join(ROOT, 'assets', 'wet.webp')).convert('RGB'))
    save(w[y0 - 600:y1 - 600, x0:x1], os.path.join(EDITS, 'zebra_wet_before.webp'), 'RGB'); print('zebra_wet_before')


def wet_ground(P):
    """the wet ground under the stripes (wet.webp in the box, from its before crop): the puddles' still water drained off the
    raised paint into the gaps; on the paint a film of rain over a smooth surface (a sheen sharper than the rough
    asphalt's: B at SHEEN, R at least FILM), so it gives back the lights the water sees (the far city, the far house's
    lantern) more than the asphalt beside it does"""
    x0, y0, x1, y1 = BOX
    pw = os.path.join(ROOT, 'assets', 'wet.webp')
    wet = np.asarray(Image.open(pw).convert('RGB')).copy()
    wb = np.asarray(Image.open(os.path.join(EDITS, 'zebra_wet_before.webp')).convert('RGB')).astype(float)
    q = P['new']
    wb[..., 0] += np.maximum(0, FILM - wb[..., 0]) * q
    wb[..., 2] = wb[..., 2] * (1 - q) + SHEEN * q
    wet[y0 - 600:y1 - 600, x0:x1] = np.clip(np.round(wb), 0, 255).astype(np.uint8)
    save(wet, pw, 'RGB')


def draw(city, unlit, box=BOX):
    """The zone: both layers' boxes in place, the ground lights and the wet ground written; returns what changed (scene)."""
    x0, y0, x1, y1 = box
    H, W = city.shape[:2]
    P = plan(city[y0:y1, x0:x1, :3].copy())
    for L in (city, unlit):
        L[y0:y1, x0:x1, :3] = repaint(L[y0:y1, x0:x1, :3].copy(), P)
    for n, (gx, gy) in ground_lights():
        path = os.path.join(ROOT, 'assets', n + '.webp')
        g = np.asarray(Image.open(path).convert('RGBA')).astype(float).copy()
        a, b, c, d = clip_box(gx, gy, g)
        g[b - gy:d - gy, a - gx:c - gx] = np.asarray(Image.open(os.path.join(EDITS, f'zebra_before_{n}.webp')).convert('RGBA')).astype(float)
        full = np.zeros((y1 - y0, x1 - x0, 3)); full[b - y0:d - y0, a - x0:c - x0] = g[b - gy:d - gy, a - gx:c - gx, :3]
        hv = np.zeros((y1 - y0, x1 - x0), bool); hv[b - y0:d - y0, a - x0:c - x0] = g[b - gy:d - gy, a - gx:c - gx, 3] > 0
        out = repaint(full, P, hv)
        g[b - gy:d - gy, a - gx:c - gx, :3] = out[b - y0:d - y0, a - x0:c - x0]
        save(g, path)
    wet_ground(P)
    print('zebra: stripes at x', ', '.join(f'{VPX + (c - HW) * 58.5 / EYE:.1f}-{VPX + (c + HW) * 58.5 / EYE:.1f}' for c in XC),
          f'(row 673.5), rows {VPY + F * EYE / ZF:.2f}-{VPY + F * EYE / ZN:.2f}; painted share {P["new"].sum() / max(P["cov"].sum(), 1):.2f}')
    ch = np.zeros((H, W), bool); ch[y0:y1, x0:x1] = P['touch']
    return ch


def preview(out_dir):
    x0, y0, x1, y1 = BOX
    city = np.asarray(Image.open(os.path.join(ROOT, 'assets', 'layer_city_off.webp')).convert('RGBA')).astype(float)
    before = np.asarray(Image.open(os.path.join(EDITS, 'zebra_before_city.webp')).convert('RGBA')).astype(float)
    city[y0:y1, x0:x1] = before
    P = plan(city[y0:y1, x0:x1, :3].copy())
    after = repaint(city[y0:y1, x0:x1, :3].copy(), P)
    os.makedirs(out_dir, exist_ok=True)
    big = lambda a: Image.fromarray(np.clip(np.round(a), 0, 255).astype(np.uint8)).resize(((x1 - x0) * 8, (y1 - y0) * 8), Image.NEAREST)
    big(before[..., :3]).save(os.path.join(out_dir, 'zebra_before_x8.png')); big(after).save(os.path.join(out_dir, 'zebra_after_x8.png'))
    print('painted share', round(float(P['new'].sum() / max(P['cov'].sum(), 1)), 3))


if __name__ == '__main__':
    if '--befores' in sys.argv:
        befores()
    elif '--preview' in sys.argv:
        preview(sys.argv[sys.argv.index('--preview') + 1])
