#!/usr/bin/env python3
"""Ichiraku's umbrella stand (kasa-tate): on its hours a glazed Shigaraki stand on the sidewalk just right of its step, against
the plaster under the right wall lamp, holding the umbrellas of the customers inside (one each: Luffy's clear konbini one,
Naruto's navy one when he comes down); taken in with the noren at closing.

    python3 tools/ramen_umbrellas.py --ask      the pieces asked of the image model (OpenRouter's key in
                                                ~/.config/openrouter/key; about 0.25 $): tools/src/edits/umbrella_in.webp
                                                (the street at 22 h round the door, tools/dev/shot.cjs; sent brightened, x3)
                                                and umbrella_prompt.txt; its answer umbrella_model.webp. The sheet is drawn
                                                from the saved answer, never from a new call
    python3 tools/ramen_umbrellas.py            writes assets/ramen_kasa.webp and, in assets/street.js, the line KST
    python3 tools/ramen_umbrellas.py --preview DIR   the frames over the layer (lit, in the power cut), x1 and x6

The answer (tools/src/edits/umbrella_model.webp, on a flat green) holds five pieces: 1 the stand empty, 2 the clear umbrella,
3 the navy one, 4 and 5 the model's own assemblies (looked at, not used: their stands differ a little from piece 1's, and a
frame swapped when a customer comes must not move the stand). From pieces 1-3, at the answer's one scale:
- the stand set at its place in the street's camera (F 1400, VP (700, 615), the eye 1.5 m: tools/ichiraku_front.py), its
  axis at Z_POT along the street, against the plaster; its round rim and foot brought to what the eye sees from there (a rim
  0.43 m up, 14 m away, is an ellipse 0.076 as high as wide, the foot 0.108): each column of the drawing remapped between
  its rim's back edge, its rim's front edge and its foot's front edge;
- each umbrella leaned in it (its tip on the stand's floor, its shaft through the rim at its own place, tilted), what is
  below the rim's front edge hidden by the stand;
- each scene pixel the mean of SS x SS points of that drawing, solid from half covered;
- graded into the place at 22 h (OKLab: each material's lightness mapped into the range of what is round it, its chroma
  muted, the painting's grain: a few families of tones, a fine ordered grain); the power cut's state taken from the layers'
  own change there (street_unlit over layer_city_off: the plaster right of the door keeps the arcade's violet, the warm light
  of the shop's glass and of the lamp goes), per side of the stand;
- a contact shade on the paving round its foot (in metres, lit frames only).
The sheet: four frames (none, Luffy's, Naruto's, both) on two rows (lit, the power cut). street.js (KST) lays them as two
sprites over the street (graded as the street; the cut's row over the lit one at 1 - the zone's power) and swaps the
frame only when the count changes; a bead of water now and then runs down the glaze from the rim to the paving.
"""
import base64
import io
import json
import os
import re
import sys
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDITS = os.path.join(ROOT, 'tools', 'src', 'edits')
ASSETS = os.path.join(ROOT, 'assets')
sys.path.insert(0, os.path.join(ROOT, 'tools'))
MODEL = 'openai/gpt-5.4-image-2'
IN_SCALE = 3                                   # (the input: each street pixel a 3 x 3 block, brightened z ** (1 / 2))
OUT = os.path.join(ASSETS, 'ramen_kasa.webp')

# ---- the street's camera at the stand (tools/ichiraku_front.py)
F, VX, VY, EYE, X_F = 1400.0, 700.0, 615.0, 1.5, 5.5343
U_LEN = 0.86                                   # an umbrella's length (m): a konbini vinyl one, 60 cm ribs
R_POT = 0.12                                   # (the stand's radius and its axis: on the sidewalk right of the step's end, its back
Z_POT = 13.88                                  #  2 cm off the plaster, short of the wall's corner at Z 13.69)
X_POT = X_F - R_POT - 0.02
PXM = F / Z_POT                                # scene px a metre there (100.9)
CX, CY = VX + F * X_POT / Z_POT, VY + EYE * PXM   # (its axis's foot in the scene)

# ---- the answer: its green, its pieces (left to right), the stand's outline on piece 1 (axis, half width, the drawn rim's and
# foot's ellipses: their centre rows and half heights)
BG = np.array([14.0, 248.0, 15.0])
POT = dict(cx=117.5, a=67.0, cyT=470.0, bT=19.0, cyB=720.0, bB=27.0)
S = None                                       # (scene px an answer px: set from the umbrella's length, below)
H_POT = None                                   # (the stand's rim height, m: the answer's stand at S)
# each umbrella: its piece, the scene offset of its shaft at the rim from the stand's axis (m, along X), its lean (degrees,
# to the left negative), the answer's column of its shaft
UMB = {'L': dict(piece=1, dx=-0.030, lean=-12.0), 'N': dict(piece=2, dx=0.035, lean=9.0)}
TIP_UP = 0.03                                  # (its tip on the stand's floor, m above the paving)
FRAMES = ['', 'L', 'N', 'LN']                  # (none, Luffy's, Naruto's, both)
SS = 8                                         # (points a pixel each way)
SHADE = dict(k=0.42, reach=0.035)              # the contact shade on the paving: its alpha at the foot, its reach (m)
# the grade: each material's OKLab lightness (its 5th and 95th percentiles mapped to these: the plaster beside it is 0.22, the
# paving 0.20, the step's lit top 0.30, the door's kickboard 0.20-0.37), its chroma times C
GRADE = {'pot': dict(L=(0.17, 0.36), C=0.55), 'rim': dict(L=(0.24, 0.42), C=0.55), 'clear': dict(L=(0.26, 0.50), C=0.45),
         'navy': dict(L=(0.14, 0.30), C=0.7), 'dark': dict(L=(0.10, 0.24), C=0.5)}
FAM = 14                                       # (the families of tones over all the frames)


def load(p, mode='RGBA'):
    return np.asarray(Image.open(p).convert(mode)).astype(float)


def save(a, p):
    Image.fromarray(np.clip(np.round(a), 0, 255).astype(np.uint8), 'RGBA' if a.shape[-1] == 4 else 'RGB').save(
        p, 'WEBP', lossless=True, quality=100, method=6, exact=True)


def ask():
    import urllib.request
    z = load(os.path.join(EDITS, 'umbrella_in.webp'), 'RGB') / 255.0
    h, w = z.shape[:2]
    im = Image.fromarray((np.clip(z ** 0.5, 0, 1) * 255).astype(np.uint8)).resize((w * IN_SCALE, h * IN_SCALE), Image.NEAREST)
    buf = io.BytesIO(); im.save(buf, 'PNG')
    key = open(os.path.expanduser('~/.config/openrouter/key')).read().strip()
    content = [{"type": "text", "text": open(os.path.join(EDITS, 'umbrella_prompt.txt')).read().strip()},
               {"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()}}]
    body = {"model": MODEL, "modalities": ["image", "text"], "usage": {"include": True}, "messages": [{"role": "user", "content": content}]}
    req = urllib.request.Request('https://openrouter.ai/api/v1/chat/completions', data=json.dumps(body).encode(),
                                 headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'})
    d = json.loads(urllib.request.urlopen(req, timeout=900).read())
    url = d['choices'][0]['message']['images'][0]['image_url']['url']
    Image.open(io.BytesIO(base64.b64decode(url.split(',', 1)[1]))).save(os.path.join(EDITS, 'umbrella_model.webp'), 'WEBP', lossless=True, quality=100, method=6)
    print('umbrella_model.webp saved; cost', d.get('usage', {}).get('cost'), '$')


# ---- the answer's pieces
def key(a):
    """the answer's pixels: their coverage (0..1) from the green, their colour unmixed from it at the edges"""
    gx = a[..., 1] - np.maximum(a[..., 0], a[..., 2])
    al = np.clip((233.0 - gx) / (233.0 - 25.0), 0, 1)
    al[gx < 25] = 1.0
    c = (a - (1 - al[..., None]) * BG) / np.maximum(al[..., None], 1e-3)
    c[..., 1] = np.minimum(c[..., 1], np.maximum(c[..., 0], c[..., 2]) + 12)   # (no green spill left on an edge)
    al[al < 0.08] = 0
    return np.clip(c, 0, 255), al


def answer():
    from scipy import ndimage as nd
    c, al = key(load(os.path.join(EDITS, 'umbrella_model.webp'), 'RGB'))
    lab, n = nd.label(al > 0.5)
    boxes = sorted((s[1].start, s[0].start, s[1].stop, s[0].stop) for i, s in enumerate(nd.find_objects(lab)) if (lab[s] == i + 1).sum() > 2000)
    return c, al, boxes


def setup(c, al, boxes):
    """the one scale (the umbrella U_LEN long) and the stand's rim height at it; each umbrella's shaft column and length"""
    global S, H_POT
    for k, U in UMB.items():
        x0, y0, x1, y1 = boxes[U['piece']]
        col = al[y1 - 12:y1, x0:x1] > 0.5                       # (its tip: the shaft's column)
        U['ax'] = x0 + float(np.nonzero(col.any(0))[0].mean()) + 0.5
        U['top'], U['len'] = float(y0), float(y1 - y0)
    S = U_LEN * PXM / np.mean([U['len'] for U in UMB.values()])
    H_POT = (POT['cyB'] - POT['cyT']) * S / PXM
    for U in UMB.values():                                      # (its pivot: where its shaft crosses the rim's plane)
        U['vis'] = U['len'] - (H_POT - TIP_UP) / np.cos(np.radians(U['lean'])) * PXM / S


# ---- the drawing in the street's frame: a scene point's answer point (the stand's foot on its axis at the answer's foot
# centre), and what is there
def to_answer(xs, ys):
    return POT['cx'] + (xs - CX) / S, POT['cyB'] + (ys - CY) / S


def rims():
    """the true half heights of the rim's and the foot's ellipses, in answer px"""
    return POT['a'] * (EYE - H_POT) / Z_POT, POT['a'] * EYE / Z_POT


def look(c, al, x, y):
    xi = np.clip(np.floor(x).astype(int), 0, c.shape[1] - 1); yi = np.clip(np.floor(y).astype(int), 0, c.shape[0] - 1)
    inside = (x >= 0) & (x < c.shape[1]) & (y >= 0) & (y < c.shape[0])
    return c[yi, xi], al[yi, xi] * inside


def pot_at(c, al, box, xa, ya):
    """piece 1 at answer points of the true geometry: each column's rows remapped (back edge, front edge, foot)"""
    P = POT; bT, bB = rims()
    r = np.sqrt(np.clip(1 - ((xa - P['cx']) / (P['a'] + 3)) ** 2, 0, 1))
    sb, sf, sd = P['cyT'] - P['bT'] * r, P['cyT'] + P['bT'] * r, P['cyB'] + P['bB'] * r
    nb, nf, nd_ = P['cyT'] - bT * r, P['cyT'] + bT * r, P['cyB'] + bB * r
    src = np.where(ya < nf, sb + (ya - nb) * (sf - sb) / np.maximum(nf - nb, 1e-3), sf + (ya - nf) * (sd - sf) / np.maximum(nd_ - nf, 1e-3))
    col, a = look(c, al, xa, src)
    x0, y0, x1, y1 = box
    a = a * (ya >= nb - 0.5) * (ya <= nd_ + 0.5) * (xa >= x0) * (xa < x1)
    return col, a, nf


def umb_at(c, al, U, box, xa, ya):
    """an umbrella leaned in the stand: the answer point turned back about its pivot into its piece (only that piece)"""
    px, py = POT['cx'] + U['dx'] * PXM / S, POT['cyT']             # (its pivot in the stand's frame)
    t = np.radians(U['lean'])
    dx, dy = xa - px, ya - py
    ux, uy = dx * np.cos(t) + dy * np.sin(t), -dx * np.sin(t) + dy * np.cos(t)
    x, y = U['ax'] + ux, U['top'] + U['vis'] + uy
    col, a = look(c, al, x, y)
    x0, y0, x1, y1 = box
    return col, a * (x >= x0) * (x < x1) * (y >= y0) * (y < y1)


def classify(c, kind):
    """a piece's materials: the stand's glaze and its rolled rim; the clear umbrella and its white handle; the navy one, its black
    handle and metal"""
    L = c @ np.array([0.299, 0.587, 0.114])
    if kind == 'pot':
        warm = c[..., 0] - c[..., 2]
        return np.where((warm > 28) & (L > 70), 'rim', 'pot')
    if kind == 'L':
        return np.where(L > 70, 'clear', 'dark')
    return np.where((c[..., 2] > c[..., 0] + 4) & (L > 18), 'navy', 'dark')


def frame(c, al, boxes, which, box):
    """one frame over the scene box (x0, y0, x1, y1): RGBA, its materials, its points' mean"""
    x0, y0, x1, y1 = box
    H, W = y1 - y0, x1 - x0
    ys, xs = (np.mgrid[0:H * SS, 0:W * SS] + 0.5) / SS
    xa, ya = to_answer(xs + x0, ys + y0)
    col, a, nf = pot_at(c, al, boxes[0], xa, ya)
    mat = np.where(a > 0.5, classify(col, 'pot'), '')
    for k in which:
        U = UMB[k]
        uc, ua = umb_at(c, al, U, boxes[U['piece']], xa, ya)
        ua = ua * (ya < nf - 2.0)
        on = ua > 0.5
        col = np.where(on[..., None], uc, col); a = np.where(on, np.maximum(ua, 0), a)
        mat = np.where(on, classify(uc, k), mat)
    # each scene pixel: the mean of its points (premultiplied), solid from half covered; its material the most of its points
    pre = col * a[..., None]
    def pool(v): return v.reshape(H, SS, W, SS, *v.shape[2:]).mean((1, 3))
    A = pool(a); C = pool(pre) / np.maximum(A[..., None], 1e-6)
    M = np.empty((H, W), dtype=object)
    mats = ['pot', 'rim', 'clear', 'navy', 'dark']
    cnt = np.stack([pool((mat == m).astype(float)) for m in mats], -1)
    M[:] = np.array(mats, dtype=object)[cnt.argmax(-1)]
    M[A < 0.5] = ''
    return C, (A >= 0.5), M


def grade(frames):
    """the frames graded into the place at 22 h, all at once (one map a material: a swapped frame keeps the stand's pixels):
    OKLab lightness, each material's 5th..95th percentiles to its range (GRADE), its chroma muted and pulled toward the night's
    violet on the plaster round it (AMB); then the families of tones (FAM, over all the frames) and a fine ordered grain"""
    from regrain import oklab, from_oklab, families, bayer
    labs = [oklab(C) for C, _, _ in frames]
    out = [np.zeros_like(lb) for lb in labs]
    for m, G in GRADE.items():
        sel = [(M == m) & sol for (_, sol, M) in frames]
        Ls = np.concatenate([lb[s][:, 0] for lb, s in zip(labs, sel)])
        if not len(Ls): continue
        p0, p1 = np.percentile(Ls, [5, 95])
        for lb, o, s in zip(labs, out, sel):
            v = lb[s]
            L = G['L'][0] + (v[:, 0] - p0) * (G['L'][1] - G['L'][0]) / max(p1 - p0, 1e-3)
            L = np.where(L > G['L'][1], G['L'][1] + (L - G['L'][1]) * 0.35, L)        # (a gloss above the range, softened)
            L = np.where(L < G['L'][0], G['L'][0] + (L - G['L'][0]) * 0.5, L)
            ab = v[:, 1:] * G['C'] + AMB * (1 - G['C']) * 0.6
            o[s] = np.concatenate([L[:, None], ab], 1)
    allpx = np.concatenate([o[s] for o, (_, s, _) in zip(out, frames)])
    W = np.array([1.0, 2.0, 2.0]) ** 0.5
    Cf = families(allpx * W, FAM, 0.018) / W
    res = []
    for o, (_, s, _) in zip(out, frames):
        h, w = s.shape
        lab = o.copy()
        d = (((o[s][:, None] - Cf[None]) * W) ** 2).sum(2)
        f = Cf[d.argmin(1)]
        g = (o[s][:, 0] - f[:, 0]) * 0.5 + (bayer(h, w)[s] - 0.5) * 0.012           # (the fine grain: its own pull, a dither)
        f[:, 0] += np.clip(g, -0.012, 0.012)
        lab[s] = f
        rgb = from_oklab(lab)
        res.append(np.where(s[..., None], rgb, 0))
    return res


AMB = np.array([0.020, -0.044])                # (the plaster's violet beside the stand, OKLab a, b)


def shade(box, solid):
    """the contact shade on the paving round the stand's foot (alpha), in metres on the ground, where the stand is not"""
    x0, y0, x1, y1 = box
    ys, xs = np.mgrid[y0:y1, x0:x1] + 0.5
    Z = F * EYE / np.maximum(ys - VY, 1e-3); X = (xs - VX) * Z / F
    d = np.hypot(X - X_POT, Z - Z_POT) - R_POT
    wall = X_F - X                                              # (the plaster's foot behind it: the corner shaded a little)
    a = SHADE['k'] * np.exp(-np.maximum(d, 0) / SHADE['reach']) * (d > -0.02)
    a = np.maximum(a, 0.5 * SHADE['k'] * np.exp(-np.maximum(wall, 0) / 0.02) * np.exp(-np.maximum(d, 0) / 0.08) * (wall > 0))
    a = np.where(solid, 0, a) * (ys > CY - R_POT * EYE / Z_POT * PXM - 1)
    return np.where(a * 255 >= 3, a, 0)


def cut_state(rgb, solid, box):
    """the power cut's frame: what the layers lose there, side by side: the plaster behind the stand keeps the arcade's violet
    (street_unlit over layer_city_off: 0.97-1.0), the step's end beside it loses the shop's warm light (CUT_WARM); the stand's
    side toward the door takes the step's change, its far side the plaster's, its tops the lamp's light gone (CUT_TOP)"""
    x0, y0, x1, y1 = box
    xs = np.arange(x0, x1) + 0.5
    w = np.clip((CX + 4 - xs) / 16.0, 0, 1)[None, :, None]              # (toward the door)
    L = rgb @ np.array([0.299, 0.587, 0.114])
    top = np.zeros(L.shape)
    for j in range(L.shape[1]):                                         # (each column's top pixels: the lamp's)
        r = np.nonzero(solid[:, j])[0]
        if len(r): top[r[:2], j] = 1
    k = np.array(CUT_WALL)[None, None] * (1 - w) + np.array(CUT_WARM)[None, None] * w
    k = k * (1 - top[..., None] * (1 - CUT_TOP))
    return np.where(solid[..., None], rgb * k, 0)


CUT_WALL, CUT_WARM, CUT_TOP = (0.98, 0.99, 1.0), (0.74, 0.89, 1.03), 0.8


def build():
    c, al, boxes = answer()
    setup(c, al, boxes)
    big = (1218, 650, 1272, 776)
    frames = [frame(c, al, boxes, w, big) for w in FRAMES]
    sol = np.any([s for _, s, _ in frames], 0)
    sh = shade(big, sol)
    m = sol | (sh > 1 / 255)
    ys, xs = np.nonzero(m)
    bx = (int(big[0] + xs.min()), int(big[1] + ys.min()), int(big[0] + xs.max() + 1), int(big[1] + ys.max() + 1))
    sl = (slice(bx[1] - big[1], bx[3] - big[1]), slice(bx[0] - big[0], bx[2] - big[0]))
    frames = [(C[sl], s[sl], M[sl]) for C, s, M in frames]
    lit = grade(frames)
    fw, fh = bx[2] - bx[0], bx[3] - bx[1]
    sheet = np.zeros((2 * fh, len(FRAMES) * fw, 4))
    for i, ((_, s, _), g) in enumerate(zip(frames, lit)):
        a = shade(bx, s)
        cell = np.zeros((fh, fw, 4))
        cell[..., 3] = np.round(a * 255)                                # (the shade: black at its alpha)
        cell[s, :3] = g[s]; cell[s, 3] = 255
        sheet[:fh, i * fw:(i + 1) * fw] = cell
        cut = np.zeros((fh, fw, 4)); u = cut_state(g, s, bx)
        cut[s, :3] = u[s]; cut[s, 3] = 255
        sheet[fh:, i * fw:(i + 1) * fw] = cut
    # the beads' runs: down the glaze's front, from under the rim to the foot's front edge, columns under each umbrella
    s0 = frames[0][1]
    runs = {}
    for k, U in UMB.items():
        x = int(np.floor(CX + U['dx'] * PXM * 0.8)) - bx[0]
        cols = [j for j in (x - 1, x, x + 1) if 0 <= j < fw and s0[:, j].any()]
        runs[k] = [[bx[0] + j, bx[1] + int(np.nonzero(s0[:, j])[0].min()) + 3, bx[1] + int(np.nonzero(s0[:, j])[0].max())] for j in cols]
    KST = {'box': [bx[0], bx[1], fw, fh], 'sheet': [sheet.shape[1], sheet.shape[0]], 'frames': FRAMES, 'runs': runs}
    return sheet, KST


def write():
    sheet, KST = build()
    save(sheet, OUT)
    JS = os.path.join(ASSETS, 'street.js')
    js = open(JS, encoding='utf-8').read()
    line = 'const KST = ' + json.dumps(KST, separators=(',', ':')) + ';'
    js2, n = re.subn(r'const KST = \{.*?\};', lambda m: line, js, count=1)
    if n and js2 != js: open(JS, 'w', encoding='utf-8').write(js2)
    print('wrote', OUT, KST['box'], '| street.js KST', 'updated' if n else 'NOT FOUND')


def preview(d):
    """the frames over the layer at 22 h (as street.js lays them), lit and in the power cut, x1 and x6"""
    os.makedirs(d, exist_ok=True)
    sheet, KST = build()
    x, y, w, h = KST['box']
    tiles = []
    for name, lay in (('lit', 'layer_city_off'), ('cut', 'street_unlit')):
        base = load(os.path.join(ASSETS, lay + '.webp'), 'RGB')
        for i in range(len(FRAMES)):
            cell = sheet[(name == 'cut') * h:(name == 'cut') * h + h, i * w:(i + 1) * w] / 255.0
            o = base[y - 20:y + h + 20, x - 30:x + w + 30].copy()
            sub = o[20:20 + h, 30:30 + w]
            sub[:] = sub * (1 - cell[..., 3:]) + cell[..., :3] * 255 * cell[..., 3:]
            tiles.append(Image.fromarray(np.clip(np.round(o), 0, 255).astype(np.uint8)).resize((o.shape[1] * 6, o.shape[0] * 6), Image.NEAREST))
    W = sum(t.width + 8 for t in tiles[:4]); O = Image.new('RGB', (W, 2 * tiles[0].height + 8), (255, 255, 255))
    for i, t in enumerate(tiles): O.paste(t, ((i % 4) * (t.width + 8), (i // 4) * (t.height + 8)))
    O.save(os.path.join(d, 'kasa_frames_x6.png'))
    Image.fromarray(np.clip(np.round(sheet), 0, 255).astype(np.uint8), 'RGBA').resize((sheet.shape[1] * 6, sheet.shape[0] * 6), Image.NEAREST).save(os.path.join(d, 'kasa_sheet_x6.png'))
    print(json.dumps(KST))


if __name__ == '__main__':
    if '--ask' in sys.argv:
        ask()
    elif '--preview' in sys.argv:
        preview(sys.argv[sys.argv.index('--preview') + 1])
    else:
        write()
