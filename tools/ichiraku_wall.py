#!/usr/bin/env python3
"""Ichiraku's front wall either side of its entrance (the casing's left and right, from under the sign's ledge down to the
sidewalk): dark-stained vertical boards in the street's camera, lit by its two wall lamps on the shop's hours.

    (a module: tools/redraw_zones.py's zone 'ichiwall', the last, calls draw(city, unlit, box) on the street as the zones
     before it leave it: both layers in its box, from the zone's before copies; it writes the lamps' light on the wall,
     assets/ichiraku_wall_light.webp, from the same inputs: the same bytes each time)
    python3 tools/ichiraku_wall.py --before      once: the zone's before crops (tools/src/edits/ichiwall_before_*.webp)
    python3 tools/ichiraku_wall.py --ask         the draft asked of the image model (OpenRouter's key in
                                                 ~/.config/openrouter/key; about 0.25 $), from tools/src/edits/ichiwall_in.webp
                                                 (the street rendered at 22 h, x 1060..1316, y 400..784) brightened and enlarged
                                                 4 times; its prompt ichiwall_prompt.txt, its answer ichiwall_model.webp; the
                                                 wall is drawn from the saved answer, never a new call
    python3 tools/ichiraku_wall.py --preview DIR the wall off, lit (both lamps) and in the power cut over the layers as they
                                                 are, x1 and x4 (nothing written)

What was there: left of the entrance's casing (x 1117..1153) and right of it (x 1231..1265), from the sign's ledge to the
sidewalk, one near-flat dark plum-navy fill (about 10, 12, 22 high up, a magenta glow by the casing low down: the doorway's
light painted on a wall that stands in the doorway's own plane, where none of it can fall), at every hour and in every
state; the two wall lamps lit only a small halo round themselves (their glow, tools/redraw_lamps.py), never the wall below.

What the camera sees (Ichiraku's camera, tools/ichiraku_front.py: F 1400, VP (700, 615), the eye 1.5 m, the front the plane
X_F 5.53 m right of the eye): the two strips are that plane, the casing's jambs flush with it. The left strip runs from the
corner with the narrow building's recess (x 1117, Z 18.56 m) to the far jamb (x 1154, Z 17.07 m): 1.5 m of wall; the right
one from the near jamb (x 1231, Z 14.59 m) to the front's corner on the arcade (x 1265, its arris; Z 13.71 m): 0.9 m. Both
from the sidewalk (h 0) up to the sign's ledge (h H_TOP; under the arcade's eave on the right). The step stands before the
left strip's foot and the right one's first columns; the lamps hang on the wall, their glass's mouths both at 2.7 m (x 1131 and
x 1241: one line on the front, as the owner wants a pair), 7 px (about 0.1 m) out from their plates.

What it is now (R28: the image model drew the wall in its context, tools/src/edits/ichiwall_model.webp, from ichiwall_in.webp
and ichiwall_prompt.txt: dark-stained vertical cedar boards with fine dark joints, each lamp throwing a warm fan down them):
- the boards: board-and-joint cladding as a Japanese shopfront has it, its boards BOARD wide (the answer's own, read on its
  joints and put on the street's rays: vertical joints, each one crisp pixel at its column), one tone a plane (R29): the
  painter's night light on the front (his profile by height away from the doorway: the sign's ledge's shade at the top),
  a little greyer and darker than his plaster (the answer's stain), each board a hair different, the answer's grain in it
  (brought down to the scene's pixels, at a small share), the joints a step darker; the first rows under the ledge its
  shadow line; the lowest WET of the boards wet from the rain (darker); the corner's arris a hair lighter; the sidewalk's
  first rows under the right strip's foot its contact shade;
- its light (assets/ichiraku_wall_light.webp, two additive cells, street.js IRWL: each lamp's own, so it catches, flickers
  and goes out with it: on the shop's hours, one lamp after the other at closing, out in the power cut, red in the red
  night): a soft fan down the boards from each lamp's glass, shaped as a shaded lamp close to a wall lights it (a cone
  pointing down, its falloff fitted on the answer's light: strongest just under the glass, opening and fading downward),
  in the lamp's warm colour, each pixel's share as the board's own (a joint takes less; the joint's edge facing the lamp a
  little more: the boards' relief), the wet foot a little glossier; the right lamp's fan on the near jamb's casing too;
- the layers: the wall unlit by the shop (its light in its own sprite); the power cut the painter's own darkening of the
  wall, channel by channel, away from the doorway.
Needs Pillow, numpy, scipy.
"""
import base64
import io
import json
import os
import sys
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, map_coordinates

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ichiraku_front as T

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDITS = os.path.join(ROOT, 'tools', 'src', 'edits')
ASSETS = os.path.join(ROOT, 'assets')
MODEL = 'openai/gpt-5.4-image-2'
F, VX, VY, EYE, X_F = T.F, T.VX, T.VY, T.EYE, T.X_F
GAMMA = 2.0                                      # (the draft's input brightened, its answer darkened back: z ** GAMMA)
DRAFT = (1060, 400, 1316, 784)                   # the draft's crop (the front, the neighbours' edges)
SCALE = 4                                        # (a street pixel a 4 x 4 block in the draft's input)
FIT = (3.83, -2.0, 3.19, -24.0)                  # the answer's frame (R21: it came back square, squeezed): answer x = (crop x)
                                                 # * kx + bx, y = (crop y) * ky + by, fitted on what it kept (the casing, the
                                                 # door, the noren, the lamps, the sign, the neighbours: correlation 0.97)
BOX = (1114, 392, 1268, 772)                     # the zone (redraw_zones.py 'ichiwall')
PLANES = {'left': (1117, 1154), 'right': (1231, 1266)}   # the strips' columns [a, b): the recess's corner to the far jamb,
                                                 # the near jamb to the front's corner (1265 its arris)
H_TOP = 3.64                                     # the wall's top (m): just under the sign's lit ledge
WET = 0.22                                       # the boards' wet foot (m)
BOARD = 0.21                                     # a board's width (m, Ichiraku's camera's metres): the answer's
PHASE = {'left': 0.0, 'right': 0.0}              # (each strip's first joint from its corner, m: fitted on the answer, below)
Z_CASING = {'left': T.Z_L + T.JAMB[0], 'right': T.Z_R - T.JAMB[1]}   # (the casing's outer edges, m: the doorway's sides)
RED = (1261, 428, 1266, 438)                     # the red indicator lamp on the corner (a fire alarm's): kept as painted
LAMPS = [dict(name='left', glass=(1131.0, 518.5), plate=1138.0, cell=(1114, 490, 46, 252)),
         dict(name='right', glass=(1240.5, 489.5), plate=1248.0, cell=(1220, 466, 47, 306))]
                                                 # each lamp: its glass's mouth (scene px), its wall plate's column, its light's
                                                 # cell in the street (x, y, w, h)
LIGHT = dict(d=0.10, cone=75.0, soft=20.0, p=1.0, warm=(255.0, 150.0, 84.0), peak=80.0, cap=1.5, edge=1.25, joint=0.45,
             wet=1.2, casing=1.35, sheen=22.0, sheen_warm=(255.0, 176.0, 108.0), sheen_reach=0.35)
                                                 # the fan: the glass d m out from the wall, its shade's cone (half angle and
                                                 # softness, degrees), the falloff's power, its colour, the added light at
                                                 # 0.2 m under the glass (scene units), capped there so much, the joint's edge
                                                 # facing the lamp, a joint, the wet foot, the casing; the wet foot's sheen by
                                                 # the doorway (the lit step and paving in the wet boards: at most so much, its
                                                 # tone, its reach along the wall, m)
K = dict(joint=0.64, ledge=(0.62, 0.84), wet=(0.74, 0.88), arris=1.12, stain=0.85, grey=0.2, board=0.07, grain=0.6,
         fine=0.035, contact=(0.74, 0.88))
                                                 # (a joint, the ledge's shadow rows, the wet foot and its edge, the arris; the
                                                 # stain against the painter's plaster, its grey; each board's tone (at most so
                                                 # much off), the answer's grain within a board (its share), the fine grain)
PREVIEW_AT = 'f7fdbc1'                           # (--preview: the layers before this zone, as the zones before it left them)
GRAIN_SIG = (3.0, 1.0)                           # (the answer's grain: its relief over its own light at this scale)


def load(p, mode='RGBA'):
    return np.asarray(Image.open(p).convert(mode)).astype(float)


def save(a, p):
    Image.fromarray(np.clip(np.round(a), 0, 255).astype(np.uint8), 'RGBA' if a.shape[-1] == 4 else 'RGB').save(
        p, 'WEBP', lossless=True, quality=100, method=6, exact=True)


def lum(a):
    return a @ np.array([0.299, 0.587, 0.114])


# ---- Ichiraku's camera on its front
def z_of(x):
    return F * X_F / (np.asarray(x, float) + 0.5 - VX)


def h_of(x, y):
    return EYE - (np.asarray(y, float) + 0.5 - VY) * z_of(x) / F


def row_of(x, h):
    return VY + (EYE - h) * F / z_of(x) - 0.5


def col_of(z):
    return VX + F * X_F / z - 0.5


# ---- the draft
def ask():
    """The drawing asked of the image model, from ichiwall_in.webp brightened and enlarged SCALE times."""
    import urllib.request
    z = load(os.path.join(EDITS, 'ichiwall_in.webp'), 'RGB') / 255.0
    x0, y0, x1, y1 = DRAFT
    im = Image.fromarray((np.clip(z ** (1 / GAMMA), 0, 1) * 255).round().astype(np.uint8)).resize(((x1 - x0) * SCALE, (y1 - y0) * SCALE), Image.NEAREST)
    buf = io.BytesIO(); im.save(buf, 'PNG')
    key = open(os.path.expanduser('~/.config/openrouter/key')).read().strip()
    content = [{"type": "text", "text": open(os.path.join(EDITS, 'ichiwall_prompt.txt')).read().strip()},
               {"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()}}]
    body = {"model": MODEL, "modalities": ["image", "text"], "usage": {"include": True}, "messages": [{"role": "user", "content": content}]}
    req = urllib.request.Request('https://openrouter.ai/api/v1/chat/completions', data=json.dumps(body).encode(),
                                 headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'})
    d = json.loads(urllib.request.urlopen(req, timeout=900).read())
    url = d['choices'][0]['message']['images'][0]['image_url']['url']
    Image.open(io.BytesIO(base64.b64decode(url.split(',', 1)[1]))).save(os.path.join(EDITS, 'ichiwall_model.webp'), 'WEBP', lossless=True, quality=100, method=6)
    print('ichiwall_model.webp saved; cost', d.get('usage', {}).get('cost'), '$')


def answer():
    """The answer at the street's pixels over DRAFT (each pixel the mean of 4 x 4 points of it), darkened back; rows past
    its bottom (it stops at the kickboard, y ~726) mirrored up from there (the boards run on, upright)"""
    A = (load(os.path.join(EDITS, 'ichiwall_model.webp'), 'RGB') / 255.0) ** GAMMA * 255.0
    x0, y0, x1, y1 = DRAFT; H, W = y1 - y0, x1 - x0; kx, bx, ky, by = FIT; ss = 4
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    last = (A.shape[0] - 1 - by) / ky - 1.0                                  # (the last crop row it covers)
    yy = np.where(yy > last, 2 * last - yy, yy)
    acc = np.zeros((H, W, 3))
    for j in range(ss):
        for i in range(ss):
            ax = (xx + (i + 0.5) / ss) * kx + bx; ay = (yy + (j + 0.5) / ss) * ky + by
            for c in range(3):
                acc[..., c] += map_coordinates(A[..., c], [ay, ax], order=1, mode='nearest')
    return acc / ss / ss


def crop(a, box):
    """a DRAFT-frame array cut to a box of the street (its edge rows carried on past it)"""
    ys = np.clip(np.arange(box[1], box[3]) - DRAFT[1], 0, a.shape[0] - 1)
    xs = np.clip(np.arange(box[0], box[2]) - DRAFT[0], 0, a.shape[1] - 1)
    return a[ys][:, xs]


# ---- the front's planes
def planes(P, box):
    """the two strips' pixels in the box (P: the layer's RGB there): each a mask; the pixels of the front's faces (the step,
    the sill, the casing), of the arcade's eave over the right strip's top and of the red lamp on the corner left out"""
    x0, y0, x1, y1 = box
    yy, xx = np.mgrid[y0:y1, x0:x1]
    h = h_of(xx, yy)
    front = np.zeros(xx.shape, bool)
    for name, c in T.faces():
        front |= T.raster(c, None, box)
    eave = (yy < 414) & ((P[..., 2] > 24) & (P[..., 2] > P[..., 0] + 9) | (lum(P) > 18))
    red = (xx >= RED[0]) & (xx < RED[2]) & (yy >= RED[1]) & (yy < RED[3]) & (P[..., 0] > 20) & (P[..., 0] > P[..., 2] + 6)
    out = {}
    for k, (a, b) in PLANES.items():
        out[k] = (xx >= a) & (xx < b) & (h <= H_TOP) & (h >= 0) & ~front & ~eave & ~red
    return out, xx, yy, h


def ambient(P, ms, xx, yy, h):
    """the painter's night light on the front, away from the doorway (the strips' outer columns), by height: a colour per
    0.05 m band, smoothed"""
    far = (ms['left'] & (xx <= 1126)) | (ms['right'] & (xx >= 1252) & (xx <= 1262))
    bands = np.arange(0.0, H_TOP + 0.05, 0.05)
    prof = np.zeros((len(bands), 3)); have = np.zeros(len(bands), bool)
    for i, b in enumerate(bands):
        m = far & (np.abs(h - b) < 0.08)
        if m.sum() >= 6: prof[i] = np.median(P[m], 0); have[i] = True
    for c in range(3):
        prof[:, c] = np.interp(bands, bands[have], prof[have, c])
        prof[:, c] = gaussian_filter(prof[:, c], 2.0, mode='nearest')
    return np.stack([np.interp(h, bands, prof[:, c]) for c in range(3)], -1)


def joints(name, xx):
    """the columns of the strip's joints (one crisp pixel each, on its board's edge in metres) and each pixel's board"""
    a, b = PLANES[name]
    za = z_of(a - 0.5)                                       # (the strip's corner side: its far edge on the left, its near
    zb = z_of(b - 0.5)                                       # edge on the right)
    z = z_of(xx)
    zs = za if name == 'left' else zb                        # boards counted from the corner
    k = np.floor((np.abs(z - zs) - PHASE[name]) / BOARD).astype(int)
    cols = set()
    for n in range(0, 40):
        zj = zs - (PHASE[name] + n * BOARD) if name == 'left' else zs + (PHASE[name] + n * BOARD)
        c = int(np.floor(col_of(zj) + 0.5))
        if a < c < b - 1: cols.add(c)
    return sorted(cols), k


def fit_phase(S, box):
    """each strip's first joint (PHASE) where the answer's joints are: the phase whose joint columns are darkest in the
    answer's relief (its luminance over its own light), over the strip's rows away from the lamps"""
    Sb = crop(S, box); L = lum(Sb); rel = L / np.maximum(gaussian_filter(L, (3.0, 2.0)), 1.0)
    x0, y0, x1, y1 = box
    yy, xx = np.mgrid[y0:y1, x0:x1]
    for name, (a, b) in PLANES.items():
        rows = (yy[:, 0] > 540) & (yy[:, 0] < 720)
        prof = rel[rows][:, a - x0:b - x0].mean(0)
        best = None
        for ph in np.arange(0.0, BOARD, 0.005):
            PHASE[name] = ph
            cols, _ = joints(name, xx)
            s = np.mean([prof[c - a] for c in cols]) if cols else 9
            if best is None or s < best[0]: best = (s, ph)
        PHASE[name] = round(float(best[1]), 3)
    return dict(PHASE)


def hashf(X, Y, k):
    v = np.sin(X * 12.9898 + Y * 78.233 + k * 37.719) * 43758.5453
    return v - np.floor(v)


def texture(S, ms, xx, yy, box):
    """the boards' albedo, relative (mean 1): each board's own tone (the answer's, where it drew a board there), the
    answer's grain within it (its relief over its own light, running up and down the board), a fine fixed grain drawn out
    along the board (the painting's), its joints a step darker; and the joints' mask"""
    Sb = crop(S, box); L = lum(Sb)
    rel = L / np.maximum(gaussian_filter(L, (8.0, 4.0)), 1.0)
    grain = np.clip(rel / np.maximum(gaussian_filter(rel, GRAIN_SIG), 1e-3) - 1.0, -0.2, 0.2)
    grain = gaussian_filter(grain, (1.2, 0.0))                  # (wood grain: drawn out along the board)
    fine = gaussian_filter(hashf(xx, yy, 3) * 2 - 1, (1.5, 0.0)); fine /= max(fine.std(), 1e-6)
    tex = np.ones(xx.shape); jm = np.zeros(xx.shape, bool)
    for name, m in ms.items():
        cols, k = joints(name, xx)
        jj = m & np.isin(xx, cols)
        jm |= jj
        for kk in np.unique(k[m]):
            bm = m & (k == kk) & ~jj
            if bm.sum() < 4: continue
            r = np.clip(np.median(rel[bm]) - 1.0, -0.15, 0.15) / 0.15
            r = 0.6 * r + 0.4 * (hashf(np.array(kk, float), np.array(7.0 if name == 'left' else 11.0), 5) * 2 - 1)
            tex[bm] = 1.0 + K['board'] * r
        t = m & ~jj
        tex[t] *= 1.0 + K['grain'] * grain[t] + K['fine'] * fine[t]
        tex[jj] = K['joint']
    return tex, jm


def fan(lamp, xx, yy, h, recv):
    """one lamp's light on the front (its plane X_F; recv the receiving pixels): a shaded lamp close to the wall, its cone
    down, normalised to 1 at 0.2 m under the glass on the wall behind it, capped"""
    gx, gy = lamp['glass']; d = LIGHT['d']
    zl = F * (X_F - d) / (gx - VX); hl = EYE - (gy - VY) * zl / F
    z = z_of(xx)
    dz, dh = z - zl, h - hl
    def E(dz, dh):
        r = np.sqrt(d * d + dz * dz + dh * dh)
        cphi = -dh / r
        a0, s = np.radians(LIGHT['cone']), np.radians(LIGHT['soft'])
        t = np.clip((cphi - np.cos(a0 + s)) / (np.cos(a0 - s) - np.cos(a0 + s)), 0, 1)
        cone = t * t * (3 - 2 * t)
        return cone * d / r ** (LIGHT['p'] + 1) * r            # (the cosine at the wall d / r, the falloff 1 / r^p)
    ref = E(np.array(0.0), np.array(-0.2))
    e = np.minimum(E(dz, dh) / ref, LIGHT['cap'])
    return np.where(recv, e, 0.0), zl


def build(P, box):
    """The front redrawn in the box (P: the layer's RGB there, as the zones before leave it): the wall off (the layers), each
    lamp's added light (its cell), and the masks"""
    ms, xx, yy, h = planes(P, box)
    wall = ms['left'] | ms['right']
    S = answer()
    fit_phase(S, box)
    amb = ambient(P, ms, xx, yy, h)
    # the stain: a little greyer and darker than the painter's plaster, at his light (the answer's boards against his wall)
    Sb = crop(S, box)
    stain = np.median(Sb[(ms['left'] & (xx <= 1126) & (yy > 600)) | (ms['right'] & (xx >= 1252) & (yy > 600))], 0)
    hue = stain / max(lum(stain), 1e-3)
    base = amb * (1 - K['grey']) + lum(amb)[..., None] * hue * K['grey']
    base *= K['stain']
    tex, jm = texture(S, ms, xx, yy, box)
    off = P.copy()
    off[wall] = (base * tex[..., None])[wall]
    # the ledge's shadow line: the strip's first rows under its top
    for i, kk in enumerate(K['ledge']):
        first = wall & ~np.roll(wall, i + 1, 0)
        if i: first &= ~(wall & ~np.roll(wall, 1, 0))
        off[first] *= kk
    # the wet foot
    w1 = wall & (h < WET); w2 = wall & (h >= WET) & (h < WET + 0.05)
    off[w1] *= K['wet'][0]; off[w2] *= K['wet'][1]
    # the corner's arris
    ar = ms['right'] & (xx == PLANES['right'][1] - 1)
    off[ar] *= K['arris']
    # the sidewalk's contact shade under the right strip's foot (past the step's end)
    foot = np.zeros(wall.shape, bool)
    for x in range(PLANES['right'][0], PLANES['right'][1]):
        col = ms['right'][:, x - box[0]]
        if col.any():
            yb = np.nonzero(col)[0].max()
            if yb + box[1] >= int(np.floor(row_of(x, 0.0) + 0.5)) - 1: foot[yb, x - box[0]] = True
    c1 = np.roll(foot, 1, 0) & ~wall; c2 = np.roll(foot, 2, 0) & ~wall & ~c1
    off[c1] *= K['contact'][0]; off[c2] *= K['contact'][1]
    new = wall | c1 | c2
    # the lamps' light
    casing = np.zeros(wall.shape, bool)
    for name, c in T.faces():
        if name == 'jamb_near': casing |= T.raster(c, None, box)
    lights = []
    for lamp in LAMPS:
        recv = ms[lamp['name']] | (casing if lamp['name'] == 'right' else False)
        e, zl = fan(lamp, xx, yy, h, recv)
        share = np.where(casing, LIGHT['casing'], tex)
        z = z_of(xx)                                          # the boards' relief: the board's edge just past a joint, on
        nxt = np.roll(jm, 1, 1); prv = np.roll(jm, -1, 1)     # the far side of it from the lamp, faces the lamp
        facing = (nxt & (z < zl)) | (prv & (z > zl))
        share = np.where(facing & ~jm & wall, share * LIGHT['edge'], share)
        share = np.where(jm, LIGHT['joint'], share)
        share = np.where(h < WET, share * LIGHT['wet'], share)
        add = e[..., None] * share[..., None] * np.array(LIGHT['warm'])[None, None] / 255.0 * LIGHT['peak']
        # the wet foot's sheen by the doorway: the lit step and the wet paving before it in the wet boards, fading along the
        # wall away from the casing and up the wet band (on the shop's hours with this lamp)
        m = ms[lamp['name']]
        zc = Z_CASING[lamp['name']]
        wetk = np.clip(1.0 - h / WET, 0, 1) ** 1.5
        sh = LIGHT['sheen'] * wetk * np.exp(-np.abs(z_of(xx) - zc) / LIGHT['sheen_reach']) * np.where(jm, LIGHT['joint'], 1.0)
        add += np.where(m & (h < WET), sh, 0.0)[..., None] * np.array(LIGHT['sheen_warm'])[None, None] / 255.0
        lights.append(add)
    return off, lights, new, wall, ms


def before():
    """The zone's before crops: the layers' pixels in its box before the zones run (the overlapping zones' own before
    crops, in their order, over the layers' pixels where no zone is)."""
    import redraw_zones as R
    x0, y0, x1, y1 = BOX
    for tag, f in (('city', 'layer_city_off.webp'), ('unlit', 'street_unlit.webp')):
        a = load(os.path.join(ASSETS, f))[y0:y1, x0:x1].copy()
        for name, cfg in R.ZONES.items():
            if name == 'ichiwall': continue
            b = cfg['box']
            ox0, oy0, ox1, oy1 = max(b[0], x0), max(b[1], y0), min(b[2], x1), min(b[3], y1)
            if ox0 >= ox1 or oy0 >= oy1: continue
            z = load(os.path.join(EDITS, '%s_before_%s.webp' % (name, tag)))
            a[oy0 - y0:oy1 - y0, ox0 - x0:ox1 - x0] = z[oy0 - b[1]:oy1 - b[1], ox0 - b[0]:ox1 - b[0]]
        save(a, os.path.join(EDITS, 'ichiwall_before_%s.webp' % tag))
        print('ichiwall_before_%s.webp' % tag, a.shape[1], 'x', a.shape[0])


def cut_ratio(P, U, ms, xx):
    """the power cut's darkening of the wall, channel by channel: the painter's (unlit / lit) away from the doorway"""
    far = (ms['left'] & (xx <= 1128)) | (ms['right'] & (xx >= 1250))
    return np.array([np.median(U[far, c] / np.maximum(P[far, c], 1.0)) for c in range(3)])


def light_atlas(lights, box):
    """the lamps' light cells side by side (assets/ichiraku_wall_light.webp): each its lamp's cell of the street"""
    W = sum(l['cell'][2] for l in LAMPS); H = max(l['cell'][3] for l in LAMPS)
    out = np.zeros((H, W, 4)); ox = 0
    for lamp, add in zip(LAMPS, lights):
        cx, cy, cw, ch = lamp['cell']
        sub = add[cy - box[1]:cy - box[1] + ch, cx - box[0]:cx - box[0] + cw]
        a = np.clip(np.round(sub), 0, 255)
        out[:ch, ox:ox + cw, :3] = a; out[:ch, ox:ox + cw, 3] = np.where(a.max(-1) > 0, 255, 0)
        ox += cw
    return out


WALL = []                                        # (the boards' pixels, as draw() last found them: the box and the mask)


def wall_mask(shape):
    """the boards' pixels in the whole street (as draw() found them): the closed shop's overlay (redraw_zones.shop_off)
    leaves them to the layer, where it carried the old wall (R19)"""
    m = np.zeros(shape, bool)
    if WALL:
        (x0, y0, x1, y1), w = WALL; m[y0:y1, x0:x1] = w
    return m


def draw(city, unlit, box=BOX):
    """Zone 'ichiwall': both layers in place (the wall off; the power cut at the painter's own darkening), the lamps' light
    written; returns what changed in the layers."""
    x0, y0, x1, y1 = box
    ch = np.zeros(city.shape[:2], bool)
    P = city[y0:y1, x0:x1, :3].copy(); U = unlit[y0:y1, x0:x1, :3].copy()
    off, lights, new, wall, ms = build(P, box)
    WALL[:] = [box, wall]
    yy, xx = np.mgrid[y0:y1, x0:x1]
    r = cut_ratio(P, U, ms, xx)
    for a, k in ((city, None), (unlit, r)):
        sub = a[y0:y1, x0:x1]; old = sub[..., :3].copy()
        if k is None: v = off
        else: v = np.where(wall[..., None], off * k, off * (old + 1.0) / (P + 1.0))   # (the contact shade: its own darkening)
        sub[..., :3] = np.where(new[..., None], np.round(np.clip(v, 0, 255)), old)
        ch[y0:y1, x0:x1] |= np.abs(sub[..., :3] - old).max(-1) > 0
    save(light_atlas(lights, box), os.path.join(ASSETS, 'ichiraku_wall_light.webp'))
    return ch


def preview(out):
    """The front off, lit (both lamps) and in the power cut, before and after, x1 and x4 (nothing written)."""
    os.makedirs(out, exist_ok=True)
    x0, y0, x1, y1 = BOX
    import subprocess                            # (the layers as the zones before this one left them: at PREVIEW_AT)
    old = lambda f: np.asarray(Image.open(io.BytesIO(subprocess.run(['git', 'show', '%s:assets/%s' % (PREVIEW_AT, f)], cwd=ROOT,
                               capture_output=True, check=True).stdout)).convert('RGB')).astype(float)
    b = old('layer_city_off.webp')[y0:y1, x0:x1]; u = old('street_unlit.webp')[y0:y1, x0:x1]
    off, lights, new, wall, ms = build(b, BOX)
    yy, xx = np.mgrid[y0:y1, x0:x1]
    r = cut_ratio(b, u, ms, xx)
    cut = np.where(wall[..., None], off * r, u)
    lit = off + lights[0] + lights[1]
    A = load(os.path.join(ASSETS, 'ichiraku_lamps.webp'))           # (the lamps over it, lit, and their glow, as street.js lays them)
    def lamps(base, on):
        o = base.copy()
        for (row, (bx, by, w, hh)) in ((0, (1110, 491, 54, 80)), (3, (1215, 460, 64, 100))):
            cell = A[(row + (1 if on else 0)) * 100:(row + (1 if on else 0)) * 100 + hh, :w]; g = A[(row + 2) * 100:(row + 2) * 100 + hh, :w]
            for yy_ in range(hh):
                for xx_ in range(w):
                    X, Y = bx + xx_ - x0, by + yy_ - y0
                    if 0 <= X < x1 - x0 and 0 <= Y < y1 - y0:
                        a = cell[yy_, xx_, 3] / 255.0
                        o[Y, X] = o[Y, X] * (1 - a) + cell[yy_, xx_, :3] * a + (g[yy_, xx_, :3] if on else 0)
        return o
    tiles = [lamps(b, True), lamps(off, False), lamps(lit, True), u, cut]
    for s in (1, 4):
        row = np.concatenate([np.concatenate([t, np.full((t.shape[0], 2, 3), 255.0)], 1) for t in tiles], 1)
        Image.fromarray(np.clip(np.round(row), 0, 255).astype(np.uint8)).resize((row.shape[1] * s, row.shape[0] * s), Image.NEAREST).save(os.path.join(out, 'ichiwall_x%d.png' % s))
    print('wall', int(wall.sum()), 'px; phase', PHASE, '; cut ratio', np.round(r, 3), '; light max', [round(float(lum(l).max()), 1) for l in lights])


if __name__ == '__main__':
    if '--before' in sys.argv: before()
    elif '--ask' in sys.argv: ask()
    elif '--preview' in sys.argv: preview(sys.argv[sys.argv.index('--preview') + 1])
    else: print(__doc__)
