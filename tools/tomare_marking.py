#!/usr/bin/env python3
"""止まれ on the road as a real road marking: the three characters from the font, each long on the ground as the real
ones are, with a clear space between them, in the road's perspective, in old thermoplastic paint on the wet asphalt.

    (a module: tools/redraw_zones.py's zone 'tomare' calls draw() on the street as the zones before it leave it, last;
     it also writes the ground lights that carry the paint, assets/gl_*.webp, and the wet ground under it,
     assets/wet.webp, each from its before crop)
    python3 tools/tomare_marking.py --befores      the ground lights' before crops (tools/src/edits/tomare_before_<gl>.webp),
                                                   once, from the assets as they are, before the zone is first run
    python3 tools/tomare_marking.py --wet-before   the wet ground's (tomare_wet_before.webp), once, the same way
    python3 tools/tomare_marking.py --ask          the paint's texture asked of the image model (OpenRouter's key in
                                                   ~/.config/openrouter/key; about 0.24 $): tomare_prompt.txt, no input
                                                   image; its answer tomare_draft.webp (the marking is drawn from the saved
                                                   answer, never a new call)
    python3 tools/tomare_marking.py --preview DIR  the street's two layers, the ground lights and the wet ground as the zone
                                                   leaves them, written into DIR (nothing in assets/): to serve in their place

The letters (15/11; tools/tomare.py, retired, drew 止 on ま with no space: "集れ"): each character of IPAGothic (1000 px,
thickened THICK px) stretched over its own rectangle of the road, LEN m long and the painter's width (X from XL to XR,
measured on his letters), GAP m of asphalt between them, from ZFAR (just past the crosswalk's line) to ZNEAR (short of
the puddle): 止 farthest, ま, れ nearest, as Japan writes them for the driver. Their shapes, places and order as they were.

The paint (24/11: a near-flat lavender fill with a little noise before, a sticker): Japanese road text is hot-applied
thermoplastic (加熱溶融式), 1.5 to 2 mm thick, white, glass beads mixed in and sprinkled on; traffic wears it off where
the tyres run and chips it elsewhere, the asphalt showing through. Its texture is the image model's (R28): one top-down
sheet (tomare_draft.webp) of that paint off the wheels (old, a few chips and hairline cracks, tyre grime) and in a wheel
path (half of it worn to the asphalt, in flakes drawn out along the traffic). On each letter's ground grid (N x N, u
across, v along) its share of paint is the draft's luminance between its bare asphalt (LA) and its whole paint (LP):
the light panel's, the wheel path's where the tyres run (WHEELS: the far crossing's tracks, the same columns of the
road, at WMAX), each letter reading the draft its own way round (FLIPS). Each pixel takes the exact mean of the ground
it covers (its footprint on the grid, by cumulative sums: a pixel of 止 at 28 m covers 0.37 m along the road, one of れ
at 14 m 0.09 m), so the far 止 is smoother and finer, the near れ shows its chips; then the letters' edges crisp on the
pixel grid (CRISP), the wear brought to the painting's pixel (its contrast over its neighbours, SHARP; a few steps of
paint, LEVELS, each a family of the painter's tones; its curve, WORN). The raised edge (1.5-2 mm, a fraction of a pixel
here): the face toward the eye a touch darker, the far rim a touch lighter (LIP). Wet as the road round it: the paint
darker where the wet ground is wetter (WETD, wet.webp's R).

Its tones are the painter's, layer by layer (the street, the power cut, and each ground light whose box touches it: the
paint gives back more of a light than the asphalt): where a letter was and is no more, the asphalt (smoothed along its
row from the asphalt round it) and the grain of an asphalt pixel of the same row; the paint, the asphalt times the
paint's own ratio to it (its median over the old letters, channel by channel, in that layer) with a share (GRAIN) of the
grain of a pixel of the old paint from the nearest painted rows; worn, the asphalt between in its measure. So the hours,
the power cut, the red night and the ground lights (the street lamp's pool on れ, the oden's orange) take it as they
take the road. The wet ground (wet.webp, from its before crop): the paint stands proud of the water, so it is a little
less of a mirror than the asphalt (its wetness, R, times 1 - DRY) and holds no still water (B); the wet pass's live
reflections and the rain lie on it as on the rest of the road. The stop line, the lane lines and the far crossing are
not this zone's. The draws are seeded: the same bytes each time. Needs numpy, scipy, Pillow.
"""
import os
import re
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as nd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDITS = os.path.join(ROOT, 'tools', 'src', 'edits')
BOX = (600, 682, 800, 790)                       # the zone: below the crosswalk's line (680-681), short of the puddle
VP, F, EYE = (700.0, 615.0), 1400.0, 1.5         # (tools/tomare.py's camera of the road)
GLYPHS = '止まれ'                                 # far to near
ZFAR, ZNEAR, GAP = 31.0, 12.6, 1.8               # m: the far end of 止, the near end of れ, the asphalt between two
XL, XR = -0.71, 0.65                             # m: the letters' width, the painter's
THICK = 44                                       # px of the 1000 px glyph added round its strokes
FONT = '/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf'
SEED = 33
PANELS = ((0, 511), (513, 1024))                 # the draft's two panels' columns: the paint off the wheels, in a wheel path
LA, LP, PMAX = 80.0, 185.0, 1.15                 # the draft's luminance: its bare asphalt, its whole paint (their medians)
N = 1024                                         # a letter's ground grid (N x N: u across, v along)
FLIPS = ((False, False), (True, False), (False, True))   # 止, ま, れ: the draft as it is, flipped across, flipped along
WHEELS = tuple(w * EYE / 1.41 for w in (-2.05, -0.55, 0.55, 2.05))   # the wheel paths (m): the far crossing's tracks
WSIG, WMAX = 0.16 * EYE / 1.41, 0.4              # (tools/zebra_crossing.py's, in its camera: the same columns of the road)
GRAIN = 0.5                                      # the share of the old paint's grain kept (the draft's wear is the rest)
CRISP = 1.5                                      # the edges' coverage steepened (crisp on the pixel grid)
SHARP, LEVELS, WORN = 0.8, 4, 1.3                # the wear's: its contrast over a pixel's neighbours, its steps, its curve
LIP = (0.07, 0.05)                               # the raised edge: its face toward the eye a little darker, its far rim lighter
WETD, DRY = 0.08, 0.25                           # the paint darker where the road is wetter; its wetness less than the asphalt's
COLS = (630, 770)                                # (where the old letters are)
MODEL = 'openai/gpt-5.4-image-2'
OUT = os.path.join(ROOT, 'assets')               # (where the ground lights and the wet ground are written; --preview: its DIR)

Zof = lambda y: F * EYE / (y - VP[1])
Yof = lambda Z: VP[1] + F * EYE / Z
Xof = lambda x, Z: (x - VP[0]) * Z / F


def glyph(ch):
    f = ImageFont.truetype(FONT, 1000)
    im = Image.new('L', (1300, 1300), 0); ImageDraw.Draw(im).text((150, 50), ch, font=f, fill=255)
    g = nd.binary_dilation(np.asarray(im) > 127, iterations=THICK // 2)
    ys, xs = np.where(g)
    return g[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def places():
    LEN = (ZFAR - ZNEAR - GAP * (len(GLYPHS) - 1)) / len(GLYPHS)
    out, zf = [], ZFAR
    for ch in GLYPHS:
        out.append((ch, zf - LEN, zf)); zf -= LEN + GAP
    return out


def texture():
    """the draft's two panels on the ground grid (N x N, u across, v along): the paint's share of each point, its asphalt
    0 and its whole paint 1 (the draft's luminance between LA and LP: a greyer, dirtier paint under 1, a cleaner one a
    little over, up to PMAX)"""
    A = np.asarray(Image.open(os.path.join(EDITS, 'tomare_draft.webp')).convert('RGB')).astype(np.float32)
    L = 0.299 * A[..., 0] + 0.587 * A[..., 1] + 0.114 * A[..., 2]
    out = []
    for c0, c1 in PANELS:
        P = np.asarray(Image.fromarray(np.ascontiguousarray(L[:, c0:c1]), 'F').resize((N, N), Image.BILINEAR)).astype(float)
        out.append(np.clip((P - LA) / (LP - LA), 0.0, PMAX))
    return out


def wheels():
    """the wheel paths' weight across a letter (N,): 1 in a track, 0 away from them"""
    X = XL + (np.arange(N) + 0.5) / N * (XR - XL)
    return WMAX * np.max([np.exp(-0.5 * ((X - c) / WSIG) ** 2) for c in WHEELS], 0)


def ground():
    """each letter on its ground grid: (ch, zn, zf, G its share of the letter's shape, Gp its share of paint still there)"""
    pl, pr = texture(); w = wheels()[None, :]
    out = []
    for (ch, zn, zf), (fx, fy) in zip(places(), FLIPS):
        g = glyph(ch).astype(np.float32)
        G = np.asarray(Image.fromarray(g, 'F').resize((N, N), Image.BOX)).astype(float)
        a, b = pl, pr
        if fx: a, b = a[:, ::-1], b[:, ::-1]
        if fy: a, b = a[::-1], b[::-1]
        out.append((ch, zn, zf, G, G * (a * (1 - w) + b * w)))
    return out


def cumul(F, axis):
    s = np.cumsum(F, axis)
    return np.concatenate([np.zeros_like(s[:1]) if axis == 0 else np.zeros_like(s[..., :1]), s], axis)


def interp(C, t):
    """the cumulative sum C (N + 1 along its first axis) at the fractional index t"""
    i = np.clip(np.floor(t).astype(int), 0, N - 1); f = t - i
    return C[i] + (f * (C[i + 1] - C[i]).T).T


def marking(box=BOX):
    """each pixel's mean over the ground it covers (exactly, its footprint on each letter's grid): cov, the letters'
    share; q, the paint's share still there (its tone in it)"""
    x0, y0, x1, y1 = box
    cov = np.zeros((y1 - y0, x1 - x0)); q = np.zeros_like(cov)
    xs = np.arange(x0, x1 + 1, dtype=float)
    for ch, zn, zf, G, Gp in ground():
        CG, CP = cumul(G, 0), cumul(Gp, 0)
        for y in range(max(y0, int(Yof(zf)) - 1), min(y1, int(Yof(zn)) + 2)):
            v0, v1 = (zf - Zof(y)) / (zf - zn), (zf - Zof(y + 1)) / (zf - zn)
            a, b = np.clip(v0, 0, 1) * N, np.clip(v1, 0, 1) * N
            if b <= a: continue
            us = (Xof(xs, Zof(y + 0.5)) - XL) / (XR - XL); uc = np.clip(us, 0, 1) * N; du = (us[1:] - us[:-1]) * N
            for C, out in ((CG, cov), (CP, q)):
                row = (interp(C, b) - interp(C, a)) / ((v1 - v0) * N)
                D = interp(cumul(row, 0), uc)
                out[y - y0] += (D[1:] - D[:-1]) / du
    return np.clip(cov, 0, 1), np.clip(q, 0, PMAX)


def old_paint(V):
    """the old letters' coverage, 0..1, from the street's layer (its blue over each row's asphalt), as tools/tomare.py reads it"""
    b = V[..., 2]; c = np.zeros_like(b)
    for r in range(b.shape[0]):
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
    cov, q = marking(BOX)
    c2 = np.clip((cov - 0.5) * CRISP + 0.5, 0, 1)            # (the letters' edges crisp on the pixel grid)
    f = np.where(cov > 0, q / np.maximum(cov, 1e-6), 0.0)        # (the paint still there over the letter's own ground)
    ins = (cov > 0.5).astype(float)                              # (its wear crisp on the pixel grid: steepened over the
    fb = nd.gaussian_filter(f * ins, 1.0) / np.maximum(nd.gaussian_filter(ins, 1.0), 1e-6)   # letter's pixels, then a few
    f = np.where(ins > 0, np.clip(f + SHARP * (f - fb), 0, PMAX), f)                         # steps of paint, a family each)
    f = np.where(f < 1, (np.round(np.clip(f, 0, 1) * LEVELS) / LEVELS) ** WORN, f)
    new = c2 * f
    pad = np.pad(c2, ((1, 1), (0, 0)))
    near, far = np.clip(c2 - pad[2:], 0, 1), np.clip(c2 - pad[:-2], 0, 1)   # (the edges toward the eye, and away from it)
    wet = np.asarray(Image.open(os.path.join(EDITS, 'tomare_wet_before.webp')).convert('RGB')).astype(float)
    mult = (1 - LIP[0] * near + LIP[1] * far) * (1 - WETD * np.clip(wet[..., 0] / 128.0, 0, 1))
    old = nd.binary_dilation(cov0 > 0.12)
    touch = old | (cov > 1e-3)
    clean = ~nd.binary_dilation(cov0 > 0.05, iterations=2)
    paint = cov0 > 0.85
    H, W = cov0.shape
    rng = np.random.default_rng(SEED)
    prow = np.where(paint.any(1))[0]
    pa = np.zeros((H, W, 2), int); pp = np.zeros((H, W, 2), int)
    for r, c in zip(*np.where(touch)):
        for d in range(40, W, 10):
            cs = np.where(clean[r, max(0, c - d):c + d + 1])[0] + max(0, c - d)
            if len(cs) >= 8: break
        pa[r, c] = (r, cs[rng.integers(len(cs))])
        near_r = prow[np.argsort(np.abs(prow - r), kind='stable')][:3]
        cand = [(a, b) for a in near_r for b in np.where(paint[a])[0]]
        pp[r, c] = cand[rng.integers(len(cand))]
    return dict(new=new, cov=c2, mult=mult, wet=wet, old=old, touch=touch, clean=clean, paint=paint, pa=pa, pp=pp)


def repaint(V, P, have=None):
    """one layer's box (H, W, 3) with the new letters (have: where the layer has pixels, a ground light's box)"""
    have = np.ones(V.shape[:2], bool) if have is None else have
    As = lisse(V, P['clean'] & have, 1.0, 10)
    pm = P['paint'] & have
    k = np.clip(np.median(V[pm], 0) / np.maximum(np.median(As[pm], 0), 1e-3), 1.0, 6.0) if pm.sum() > 20 else np.ones(3)
    out = V.copy()
    for r, c in zip(*np.where(P['touch'])):
        a, b = P['pa'][r, c]; e, f = P['pp'][r, c]
        base = As[r, c] + (V[a, b] - As[a, b]) if P['old'][r, c] else V[r, c]
        pnt = (As[r, c] * k + (V[e, f] - As[e, f] * k) * GRAIN) * P['mult'][r, c]
        q = P['new'][r, c]
        out[r, c] = (1 - q) * base + q * pnt
    return np.clip(out, 0, 255)


def wet_ground(P):
    """the wet ground under the letters (assets/wet.webp in the box, from its before crop): the paint stands 1.5-2 mm proud
    of the asphalt, so less water lies on it (its wetness, R, times 1 - DRY) and no still water (B: the puddles drain off it)"""
    x0, y0, x1, y1 = BOX
    w = np.asarray(Image.open(os.path.join(ROOT, 'assets', 'wet.webp')).convert('RGB')).copy()
    b = P['wet'].copy(); q = np.clip(P['new'], 0, 1)
    b[..., 0] *= 1 - DRY * q
    b[..., 2] *= 1 - q
    w[y0 - 600:y1 - 600, x0:x1] = np.clip(np.round(b), 0, 255).astype(np.uint8)
    Image.fromarray(w, 'RGB').save(os.path.join(OUT, 'wet.webp'), 'WEBP', lossless=True, quality=100, method=6, exact=True)


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


def befores():
    for n, (gx, gy) in ground_lights():
        g = np.asarray(Image.open(os.path.join(ROOT, 'assets', n + '.webp')).convert('RGBA'))
        a, b, c, d = clip_box(gx, gy, g)
        Image.fromarray(g[b - gy:d - gy, a - gx:c - gx], 'RGBA').save(os.path.join(EDITS, f'tomare_before_{n}.webp'), 'WEBP',
                                                                       lossless=True, quality=100, method=6, exact=True)
        print('tomare_before_' + n, (a, b, c, d))


def draw(city, unlit, box=BOX):
    """The zone: both layers' boxes in place, the ground lights written; returns what changed (whole scene)."""
    x0, y0, x1, y1 = box
    H, W = city.shape[:2]
    P = plan(city[y0:y1, x0:x1, :3].copy())
    for L in (city, unlit):
        L[y0:y1, x0:x1, :3] = repaint(L[y0:y1, x0:x1, :3].copy(), P)
    for n, (gx, gy) in ground_lights():
        g = np.asarray(Image.open(os.path.join(ROOT, 'assets', n + '.webp')).convert('RGBA')).astype(float).copy()
        a, b, c, d = clip_box(gx, gy, g)
        g[b - gy:d - gy, a - gx:c - gx] = np.asarray(Image.open(os.path.join(EDITS, f'tomare_before_{n}.webp')).convert('RGBA')).astype(float)
        full = np.zeros((y1 - y0, x1 - x0, 3)); full[b - y0:d - y0, a - x0:c - x0] = g[b - gy:d - gy, a - gx:c - gx, :3]
        hv = np.zeros((y1 - y0, x1 - x0), bool); hv[b - y0:d - y0, a - x0:c - x0] = True
        out = repaint(full, P, hv)
        g[b - gy:d - gy, a - gx:c - gx, :3] = out[b - y0:d - y0, a - x0:c - x0]
        Image.fromarray(np.round(g).astype(np.uint8), 'RGBA').save(os.path.join(OUT, n + '.webp'), 'WEBP', lossless=True, quality=100, method=6, exact=True)
    wet_ground(P)
    print('tomare:', ', '.join(f'{ch} rows {Yof(zf):.1f}-{Yof(zn):.1f}' for ch, zn, zf in places()))
    ch = np.zeros((H, W), bool); ch[y0:y1, x0:x1] = P['touch']
    return ch


def ask():
    """The paint's texture asked of the image model (once: tools/src/edits/tomare_prompt.txt, no input image; the answer
    tools/src/edits/tomare_draft.webp, which the marking is drawn from, never a new call)."""
    import base64, io, json, urllib.request
    key = open(os.path.expanduser('~/.config/openrouter/key')).read().strip()
    content = [{"type": "text", "text": open(os.path.join(EDITS, 'tomare_prompt.txt')).read().strip()}]
    body = {"model": MODEL, "modalities": ["image", "text"], "usage": {"include": True}, "messages": [{"role": "user", "content": content}]}
    req = urllib.request.Request('https://openrouter.ai/api/v1/chat/completions', data=json.dumps(body).encode(),
                                 headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'})
    d = json.loads(urllib.request.urlopen(req, timeout=900).read())
    url = d['choices'][0]['message']['images'][0]['image_url']['url']
    im = Image.open(io.BytesIO(base64.b64decode(url.split(',', 1)[1]))).convert('RGB')
    im.save(os.path.join(EDITS, 'tomare_draft.webp'), 'WEBP', lossless=True, quality=100, method=6)
    print('tomare_draft.webp', im.size, 'saved; cost', d.get('usage', {}).get('cost'), '$')


def wet_before():
    x0, y0, x1, y1 = BOX
    w = np.asarray(Image.open(os.path.join(ROOT, 'assets', 'wet.webp')).convert('RGB'))
    Image.fromarray(w[y0 - 600:y1 - 600, x0:x1], 'RGB').save(os.path.join(EDITS, 'tomare_wet_before.webp'), 'WEBP',
                                                             lossless=True, quality=100, method=6, exact=True)
    print('tomare_wet_before', BOX)


def preview(d):
    """the street's layers, the ground lights and the wet ground with the zone redrawn, written into the folder d (nothing in
    assets/): to be served in their place (a render of the street as it will be)"""
    global OUT
    OUT = d; os.makedirs(d, exist_ok=True)
    x0, y0, x1, y1 = BOX
    L = {}
    for tag, f in (('city', 'layer_city_off'), ('unlit', 'street_unlit')):
        a = np.asarray(Image.open(os.path.join(ROOT, 'assets', f + '.webp')).convert('RGBA')).astype(float).copy()
        a[y0:y1, x0:x1] = np.asarray(Image.open(os.path.join(EDITS, f'tomare_before_{tag}.webp')).convert('RGBA')).astype(float)
        L[f] = a
    draw(L['layer_city_off'], L['street_unlit'])
    for f, a in L.items():
        Image.fromarray(np.clip(np.round(a), 0, 255).astype(np.uint8), 'RGBA').save(os.path.join(d, f + '.webp'), 'WEBP',
                                                                                    lossless=True, quality=100, method=6, exact=True)


if __name__ == '__main__':
    if '--befores' in sys.argv:
        befores()
    elif '--wet-before' in sys.argv:
        wet_before()
    elif '--preview' in sys.argv:
        preview(sys.argv[sys.argv.index('--preview') + 1])
    elif '--ask' in sys.argv:
        ask()
