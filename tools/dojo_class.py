#!/usr/bin/env python3
"""The karate dojo's evening class, seen as shadows on its lit shoji (the dojo at the street's left edge, 空手道場).

    python3 tools/dojo_class.py --input       writes the pose guide (tools/src/edits/dojoclass_in.webp: four rows of six
                                              cells, a mannequin in each, at one scale, its feet on the cell's floor line)
    python3 tools/dojo_class.py --ask         asks the image model for the sheet (its prompt dojoclass_prompt.txt, its
                                              answer dojoclass_model.webp)
    python3 tools/dojo_class.py               writes assets/dojo_class.webp (the frames, the shadow's density in their
                                              alpha, at the scene's pixels; the paper's mask after them) and, in
                                              assets/street.js, the line DJC (the frames, the class's segments); again:
                                              the same bytes
    python3 tools/dojo_class.py --preview DIR [a,b]   the sheet at x2 and each segment (or those named) as a GIF at x3 over
                                              the lit street, nothing written in assets/

Behind the two shoji doors the dojo's room is lit (the paper painted lit in layer_city_off.webp; the place shut by the hour,
street.js HRS). The shadows are those of people in the room between its lamp and the paper: a sensei and his students,
their poses drawn by the image model (R28) after a pose guide of mannequins in side view (kihon: the bow, yoi,
choku-zuki, gedan-barai, oi-zuki, age-uke, mae-geri; Heian Shodan's tettsui-uchi and shuto-uke in kokutsu-dachi, its
transitions; seiza and its bow; the sensei walking, his arms folded; three front views for the kata's turns), as solid
silhouettes in a karate gi (the wide sleeves, the jacket's skirt, the belt's knot and its two ends), each keyed off its
pale ground, anchored on its soles and its hips' column.

The geometry, in the street's camera (tools/facade_foot.py's: VP (700, 615), f 960, the eye 1.41 m; the left fronts
receding): at the paper a metre is VPX px high and HPX px along the front (two leaves of 0.9 m). The dojo's floor is 0.32 m
over the street (tools/tree_bc.py's FRONT_FOOT, 746 at the doors), the eye 1.09 m over it, so the wall's heights run level
across the doors. The paper shows from the kickboard's top (0.44 m) to under the noren (1.78 m). The room's lamp hangs H m
over the floor, D m behind the paper, at column XL: a man d m behind the paper throws a shadow k = D / (D - d) times his size,
centred on XL + (X - XL) k, a body height y falling at the wall's H + (y - H) k: the further in, the bigger, the lower (his
legs behind the kickboard), the softer (a penumbra of LAMP d / (D - d) m) and the paler. Every frame is drawn for the depth
it is used at, on the same rows (STRIP): each scene pixel the mean of what it covers, solid from half covered, its density
in a few steps, at most dens_of(d): the paper still glows through it.

The class (segments(), real moves): the line-up and its bows in seiza (opening and closing), kihon on the spot (choku-zuki,
counted to ten, the kiai on the tenth) and moving (oi-zuki, age-uke, gedan-barai, mae-geri, shuto-uke: three steps, the
kiai on the third, mawatte, three back), Heian Shodan whole (21 moves, the kiai on the 9th and the 17th, its rei before and
after), rests while the sensei walks along the line; the children's class the same at their size, without the kata. They
face the kamiza on the left (the house's end), the sensei them from the left door. street.js (DJC) plays the segments on
the dojo's hours (the children late in the afternoon, the adults in the evening, breaks and empty moments between), as a
darkening blend over the street (the paper's light times one minus the density: right in every grade, the red night's),
clipped by the paper's mask (the frames, the rails and the noren in front untouched), only while the dojo is open and on
screen; none in the power cut, none under reduced motion.
Needs Pillow, numpy, scipy.
"""
import base64
import io
import json
import math
import os
import re
import sys
import urllib.request
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDITS = os.path.join(ROOT, 'tools', 'src', 'edits')
ASSETS = os.path.join(ROOT, 'assets')
JS = os.path.join(ASSETS, 'street.js')
MODEL = 'openai/gpt-5.4-image-2'
SHEET = (6, 4, 256, 256)                         # the guide: columns, rows, a cell's width and height (1536 x 1024)
G = 116.0                                        # (the guide's px a metre: 1.70 m, 197 px)
BASE, HIPX = 238, 104                            # (in each cell: the floor's row, the hips' column of a side view)

# ---- the poses (side views face right: x forward, y up, metres; near limbs 1, far limbs 2; front views: x the figure's
# left, to the image's right as it faces us). Joints: hd head's centre, sh shoulder, hp hip, k knee, a ankle, t toe,
# e elbow, w wrist, f the hand's end (a fist's front, the fingertips)
def side(hp, sh, hd, k1, a1, t1, e1, w1, f1, k2=None, a2=None, t2=None, e2=None, w2=None, f2=None, **kw):
    return dict(view='side', hp=hp, sh=sh, hd=hd, L=[(k1, a1, t1), (k2 or k1, a2 or a1, t2 or t1)],
                A=[(e1, w1, f1), (e2 or e1, w2 or w1, f2 or f1)], **kw)


ZEN = dict(k1=(0.47, 0.43), a1=(0.55, 0.08), t1=(0.75, 0.0), k2=(-0.22, 0.44), a2=(-0.47, 0.08), t2=(-0.30, 0.0))   # (zenkutsu-dachi)
PASS = dict(k1=(0.25, 0.46), a1=(0.02, 0.08), t1=(0.22, 0.0), k2=(0.20, 0.45), a2=(-0.04, 0.08), t2=(0.16, 0.0))   # (feet passing)
HIKITE = dict(e2=(-0.24, 1.02), w2=(-0.04, 0.95), f2=(0.03, 0.95))      # (the other fist pulled back to the hip, palm up)
POSES = [
    # row 1: the ceremony, kihon on the spot
    ('attention', side((0, 0.90), (0.0, 1.42), (0.02, 1.59), (0.02, 0.48), (0.0, 0.08), (0.21, 0.0),
                       (0.03, 1.15), (0.06, 0.88), (0.08, 0.72), hand='open')),
    ('rei', side((-0.05, 0.90), (0.22, 1.36), (0.36, 1.47), (0.01, 0.48), (0.0, 0.08), (0.21, 0.0),
                 (0.21, 1.08), (0.17, 0.84), (0.17, 0.68), hand='open')),
    ('yoi', side((0, 0.90), (0.0, 1.42), (0.02, 1.59), (0.02, 0.48), (0.0, 0.08), (0.21, 0.0),
                 (0.07, 1.14), (0.15, 0.93), (0.19, 0.88))),
    ('choku', side((0, 0.90), (0.0, 1.42), (0.02, 1.59), (0.02, 0.48), (0.0, 0.08), (0.21, 0.0),
                   (0.30, 1.35), (0.57, 1.28), (0.66, 1.27), e2=(-0.24, 1.12), w2=(-0.05, 1.0), f2=(0.03, 1.0))),
    ('oizuki_f', dict(view='front')),             # (the front views' joints: FRONT below)
    ('seiza', side((-0.06, 0.34), (-0.03, 0.86), (0.0, 1.03), (0.40, 0.10), (-0.10, 0.08), (-0.30, 0.0),
                   (0.06, 0.62), (0.26, 0.38), (0.36, 0.36), hand='open')),
    # row 2: the stances, the kata's techniques
    ('gedan', side((0.0, 0.78), (-0.02, 1.30), (0.0, 1.47), e1=(0.20, 1.05), w1=(0.42, 0.80), f1=(0.49, 0.74), **ZEN, **HIKITE)),
    ('oizuki', side((0.0, 0.78), (0.0, 1.30), (0.02, 1.47), e1=(0.29, 1.24), w1=(0.56, 1.18), f1=(0.65, 1.17), **ZEN, **HIKITE)),
    ('ageuke', side((0.0, 0.78), (0.0, 1.30), (0.02, 1.47), e1=(0.20, 1.55), w1=(0.05, 1.72), f1=(-0.02, 1.78), **ZEN, **HIKITE)),
    ('shuto', side((-0.12, 0.75), (-0.08, 1.28), (-0.06, 1.45), (0.27, 0.42), (0.48, 0.08), (0.66, 0.0),
                   (0.15, 1.07), (0.34, 1.22), (0.47, 1.31), (0.0, 0.34), (-0.38, 0.08), (-0.20, 0.0),
                   (-0.12, 1.02), (0.10, 1.06), (0.24, 1.08), hand='knife')),
    ('tettsui', side((0, 0.86), (0.0, 1.40), (0.02, 1.57), (0.12, 0.47), (0.16, 0.08), (0.35, 0.0),
                     (0.27, 1.40), (0.52, 1.31), (0.60, 1.29), (-0.04, 0.47), (-0.10, 0.08), (0.09, 0.0), **HIKITE)),
    ('maegeri', side((0.0, 0.84), (-0.09, 1.35), (-0.10, 1.52), (0.42, 0.93), (0.84, 0.97), (0.95, 1.03),
                     (0.18, 1.02), (0.38, 0.83), (0.45, 0.78), (0.03, 0.45), (-0.02, 0.08), (0.18, 0.0), **HIKITE)),
    # row 3: the transitions (a step, its arms on their way), the knee raised, the bow from seiza
    ('step', side((0.0, 0.79), (0.0, 1.31), (0.02, 1.48), e1=(0.29, 1.25), w1=(0.56, 1.19), f1=(0.65, 1.18), **PASS, **HIKITE)),
    ('gedan_prep', side((0.0, 0.79), (0.0, 1.31), (0.02, 1.48), e1=(0.14, 1.10), w1=(0.02, 1.40), f1=(-0.03, 1.46),
                        e2=(0.20, 1.06), w2=(0.40, 0.84), f2=(0.46, 0.78), **PASS)),
    ('ageuke_prep', side((0.0, 0.79), (0.0, 1.31), (0.02, 1.48), e1=(0.22, 1.22), w1=(0.30, 1.47), f1=(0.32, 1.58),
                         e2=(0.18, 1.04), w2=(0.32, 1.20), f2=(0.36, 1.27), hand='open', **PASS)),
    ('shuto_prep', side((0.0, 0.79), (0.0, 1.31), (0.02, 1.48), e1=(0.10, 1.20), w1=(-0.02, 1.43), f1=(-0.05, 1.55),
                        e2=(0.20, 1.06), w2=(0.40, 0.86), f2=(0.50, 0.80), hand='knife', **PASS)),
    ('maegeri_ch', side((0.0, 0.85), (-0.05, 1.37), (-0.05, 1.54), (0.40, 0.97), (0.30, 0.54), (0.45, 0.50),
                        (0.18, 1.04), (0.38, 0.84), (0.45, 0.79), (0.04, 0.46), (-0.01, 0.08), (0.19, 0.0), **HIKITE)),
    ('seiza_rei', side((-0.04, 0.32), (0.40, 0.52), (0.58, 0.50), (0.40, 0.10), (-0.10, 0.08), (-0.30, 0.0),
                       (0.44, 0.26), (0.62, 0.06), (0.74, 0.03), hand='open')),
    # row 4: the sensei walking along the line (his hands clasped behind his back), his arms folded; the kata's front views
    ('walk_a', side((0, 0.92), (0.0, 1.44), (0.03, 1.61), (0.14, 0.50), (0.28, 0.08), (0.46, 0.02),
                    (-0.16, 1.17), (-0.20, 0.95), (-0.18, 0.88), (-0.10, 0.50), (-0.30, 0.10), (-0.14, 0.0), hand='open')),
    ('walk_b', side((0, 0.94), (0.0, 1.46), (0.03, 1.63), (0.08, 0.53), (0.02, 0.08), (0.21, 0.0),
                    (-0.16, 1.19), (-0.20, 0.97), (-0.18, 0.90), (0.18, 0.56), (-0.06, 0.24), (0.06, 0.12), hand='open')),
    ('fold', side((0, 0.90), (0.0, 1.42), (0.02, 1.59), (0.02, 0.48), (0.0, 0.08), (0.21, 0.0),
                  (0.08, 1.17), (0.20, 1.25), (0.22, 1.27), hand='open')),
    ('yoi_f', dict(view='front')),
    ('gedan_f', dict(view='front')),
    ('ageuke_f', dict(view='front')),
]
NAMES = [n for n, _ in POSES]
# the front views: x the figure's left (to the image's right), y up; each side its leg and arm
FRONT = {
    'yoi_f': dict(hp=(0, 0.90), sh=0.20, hd=(0, 1.59), legs=[((-0.12, 0.48), (-0.16, 0.08)), ((0.12, 0.48), (0.16, 0.08))],
                  arms=[((-0.27, 1.15), (-0.14, 0.93)), ((0.27, 1.15), (0.14, 0.93))]),
    'oizuki_f': dict(hp=(0, 0.78), sh=0.20, hd=(0, 1.47), legs=[((-0.15, 0.42), (-0.17, 0.08)), ((0.14, 0.44), (0.18, 0.08))],
                     arms=[((-0.08, 1.20), (0.0, 1.18)), ((0.32, 1.02), (0.20, 0.95))]),
    'gedan_f': dict(hp=(0, 0.78), sh=0.20, hd=(0, 1.47), legs=[((-0.15, 0.42), (-0.17, 0.08)), ((0.14, 0.44), (0.18, 0.08))],
                    arms=[((-0.32, 1.02), (-0.20, 0.95)), ((0.30, 1.04), (0.36, 0.78))]),
    'ageuke_f': dict(hp=(0, 0.78), sh=0.20, hd=(0, 1.47), legs=[((-0.15, 0.42), (-0.17, 0.08)), ((0.14, 0.44), (0.18, 0.08))],
                     arms=[((-0.32, 1.02), (-0.20, 0.95)), ((0.30, 1.56), (-0.16, 1.70))]),
}


def guide():
    """the pose guide: in each cell a grey mannequin (its far limbs paler), its feet on the floor line, one scale"""
    c, r, w, h = SHEET
    im = Image.new('RGB', (c * w, r * h), (236, 230, 220)); g = ImageDraw.Draw(im)
    for k, (name, p) in enumerate(POSES):
        i, j = k % c, k // c; x0, y0 = i * w, j * h
        g.rectangle([x0, y0, x0 + w - 1, y0 + h - 1], outline=(186, 178, 168), width=2)
        g.line([x0 + 12, y0 + BASE, x0 + w - 12, y0 + BASE], fill=(170, 162, 152), width=2)
        if p['view'] == 'side':
            P = lambda q: (x0 + HIPX + q[0] * G, y0 + BASE - q[1] * G)
            far, near, body = (178, 176, 174), (104, 102, 100), (132, 130, 128)
            def limb(pts, wd, col):
                for a, b in zip(pts, pts[1:]): g.line([P(a), P(b)], fill=col, width=int(wd * G))
                for q in pts[:-1]: X, Y = P(q); rr = wd * G / 2; g.ellipse([X - rr, Y - rr, X + rr, Y + rr], fill=col)
            (k2, a2, t2), (e2, w2, f2) = p['L'][1], p['A'][1]
            limb([p['hp'], k2, a2, t2], 0.11, far); limb([p['sh'], e2, w2, f2], 0.075, far)
            limb([p['hp'], p['sh']], 0.24, body)
            X, Y = P(p['hd']); rr = 0.105 * G; g.ellipse([X - rr, Y - rr, X + rr, Y + rr], fill=body)
            limb([p['sh'], p['hd']], 0.09, body)
            (k1, a1, t1), (e1, w1, f1) = p['L'][0], p['A'][0]
            limb([p['hp'], k1, a1, t1], 0.12, near); limb([p['sh'], e1, w1, f1], 0.08, near)
        else:
            q = FRONT[name]; cx = x0 + w // 2
            P = lambda v: (cx + v[0] * G, y0 + BASE - v[1] * G)
            col = (124, 122, 120)
            def limb(pts, wd):
                for a, b in zip(pts, pts[1:]): g.line([P(a), P(b)], fill=col, width=int(wd * G))
                for v in pts: X, Y = P(v); rr = wd * G / 2; g.ellipse([X - rr, Y - rr, X + rr, Y + rr], fill=col)
            hy, sy = q['hp'][1], q['hd'][1] - 0.17
            g.polygon([P((-0.17, hy)), P((0.17, hy)), P((q['sh'], sy)), P((-q['sh'], sy))], fill=col)
            for s, (kn, an) in zip((-1, 1), q['legs']): limb([(0.09 * s, hy), kn, an, (an[0] + 0.06 * s, 0.0)], 0.13)
            for s, (el, wr) in zip((-1, 1), q['arms']): limb([(q['sh'] * s, sy), el, wr], 0.085)
            X, Y = P(q['hd']); rr = 0.105 * G; g.ellipse([X - rr, Y - rr, X + rr, Y + rr], fill=col)
            limb([(0, sy), q['hd']], 0.09)
    return im


def api_key():
    k = os.environ.get('OPENROUTER_API_KEY')
    if k: return k
    p = os.path.expanduser('~/.config/openrouter/key')
    return open(p).read().strip() if os.path.exists(p) else 'proxy-injected'


def ask():
    content = [{"type": "text", "text": open(os.path.join(EDITS, 'dojoclass_prompt.txt')).read().strip()}]
    buf = io.BytesIO(); Image.open(os.path.join(EDITS, 'dojoclass_in.webp')).convert('RGB').save(buf, 'PNG')
    content.append({"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()}})
    body = {"model": MODEL, "modalities": ["image", "text"], "usage": {"include": True}, "messages": [{"role": "user", "content": content}]}
    req = urllib.request.Request('https://openrouter.ai/api/v1/chat/completions', data=json.dumps(body).encode(),
                                 headers={'Authorization': 'Bearer ' + api_key(), 'Content-Type': 'application/json'})
    d = json.loads(urllib.request.urlopen(req, timeout=900).read())
    url = d['choices'][0]['message']['images'][0]['image_url']['url']
    im = Image.open(io.BytesIO(base64.b64decode(url.split(',', 1)[1])))
    im.save(os.path.join(EDITS, 'dojoclass_model.webp'), 'WEBP', lossless=True, quality=100, method=6)
    print('answer', im.size, 'saved; cost', d.get('usage', {}).get('cost'), '$')


# ---- the answer: its grid as drawn (the model drew 1024 x 1024: six even columns, four rows of its own heights, a floor
# line in each), each row at its own scale (measured: the poses' tops against the guide's)
GRID_X = [0, 170.5, 341, 511.5, 682, 853, 1023]
GRID_Y = [0, 213, 437, 671, 1023]
FLOOR = [169.5, 393.5, 624, 898.5]
NO_SCALE = ('seiza', 'seiza_rei')                 # (kneeling: their tops say nothing of the row's scale)

# ---- the street: the camera at the dojo (tools/facade_foot.py's: VP (700, 615), the eye 1.41 m over the street; the dojo's
# floor 0.32 m over it, behind the threshold: tools/tree_bc.py's FRONT_FOOT, 746 at x 38), the paper, the room's lamp
VPX = 120.4                                      # px a metre high at the paper (the doors' middle, x 38: (700 - 38) / 5.5)
HPX = 42.0                                       # px a metre along the front, foreshortened (two leaves of 0.9 m over x 1..75)
Y1 = 615 + (1.41 - 0.32 - 1.0) * VPX             # the row of the wall's height 1 m over the floor (near the eye's: level across)
H, D, LAMP, XL = 2.25, 8.0, 0.12, 38.0           # the room's lamp: its height over the floor, its distance behind the paper,
                                                 # its size (m); its column (between the doors)
STRIP = (524, 176)                               # the rows the shadows fall on (the wall from 1.85 m down to 0.40 m: the paper
                                                 # from under the noren to the kickboard's top), all frames on it
MASK_BOX = (0, 524, 80, 700)                     # the paper's box (x0, y0, x1, y1): the two doors under the noren
MASK = (30.0, 56.0)                              # (the paper's light over the unlit layer's, from frame to paper: the mask's ramp)
STEPS, SS = 4, 6                                 # the density's steps on the pixel grid; sub-pixels a scene pixel, each way
KID = 1.30                                       # a child's height (m)


def k_of(d): return D / (D - d)                  # how much bigger than him a man's shadow is, d m behind the paper
def dens_of(d): return max(0.32, 0.60 - 0.07 * d)   # its darkest (the paper's light kept: 1 - it): the far ones lighter
def shadow_x(X, d): return XL + (X - XL) * k_of(d)   # the column of his shadow (X: his column, at the paper's scale)


def top_of(name):
    """the guide's top of a pose (m): its head's, or a raised hand's"""
    if name in FRONT:
        q = FRONT[name]; return max(q['hd'][1] + 0.105, max(w[1] for _, w in q['arms']) + 0.05)
    p = dict(POSES)[name]
    return max(p['hd'][1] + 0.105, max(a[2][1] for a in p['A']) + 0.04)


def covers():
    """each pose's silhouette in the answer (its cover 0..1, the belt's and fists' pale strokes filled), its row's scale
    (answer px a metre), its soles' row and its hips' column in the cell"""
    im = np.asarray(Image.open(os.path.join(EDITS, 'dojoclass_model.webp')).convert('RGB')).astype(float)
    L = im @ np.array([0.299, 0.587, 0.114]); out = {}; meas = {}
    for k, name in enumerate(NAMES):
        i, j = k % SHEET[0], k // SHEET[0]
        x0, x1, y0, y1 = int(GRID_X[i]) + 4, int(GRID_X[i + 1]) - 3, int(GRID_Y[j]) + 4, int(GRID_Y[j + 1]) - 3
        c = L[y0:y1, x0:x1]; bg = np.percentile(c, 90); fg = np.percentile(c[c < bg - 60], 20)
        cov = np.clip((bg - 30 - c) / (bg - 30 - fg), 0, 1)
        lab, n = ndimage.label(cov > 0.5); keep = lab == (1 + int(np.argmax(ndimage.sum(cov > 0.5, lab, range(1, n + 1)))))
        solid = ndimage.binary_fill_holes(ndimage.binary_closing(keep, np.ones((5, 5)))) | keep
        cov = np.where(solid, 1.0, np.where(ndimage.binary_dilation(solid, iterations=2) & (cov > 0.3), cov, 0.0))
        ys, xs = np.nonzero(cov > 0.5)
        floor = FLOOR[j] - y0
        meas[name] = (j, (floor - ys.min()) / top_of(name))
        hx = (HIPX + (dict(POSES)[name]['hp'][0] * G if name not in FRONT else 128 - HIPX)) / SHEET[2] * (GRID_X[i + 1] - GRID_X[i]) - 4
        out[name] = [cov, floor, hx]
    S = {j: float(np.median([s for n, (jj, s) in meas.items() if jj == j and n not in NO_SCALE])) for j in range(4)}
    for name in NAMES: out[name].append(S[meas[name][0]])
    return out



def frame(c, floor, hx, s, d, kid=False, drop=0.0):
    """one pose at one depth, at the scene's pixels: its density, its anchor's column (the hips' shadow) and its top row
    in the strip; None if none of it shows over the kickboard. Each scene pixel the mean of what it covers (SS x SS
    samples), solid from half covered; its edge a penumbra growing with d (the lamp's size seen past him), its core denser
    than its thin parts (the light creeps round a sleeve, a belt's end), its density in STEPS steps. drop: the body
    lowered (m: kneeling down)"""
    k = k_of(d); sz = KID / 1.70 if kid else 1.0
    y0, nh = STRIP; ww = c.shape[1]
    x0 = int(math.floor((0 - hx) / s * sz * k * HPX)) - 3; x1 = int(math.ceil((ww - hx) / s * sz * k * HPX)) + 3; W = x1 - x0
    Y = y0 + (np.arange(nh * SS) + 0.5) / SS                     # (the scene's rows)
    h = 1.0 + (Y1 - Y) / VPX                                      # the wall's height there
    yb = H - (H - h) / k + drop                                   # the body's height that throws it
    r = floor - yb * s / sz                                       # (the cover's row)
    X = x0 + (np.arange(W * SS) + 0.5) / SS
    cc = hx + X / (k * HPX) * s / sz
    rr, cg = np.meshgrid(r, cc, indexing='ij')
    f = ndimage.map_coordinates(c, [rr - 0.5, cg - 0.5], order=1, mode='constant', cval=0.0).reshape(nh, SS, W, SS).mean((1, 3))
    hard = np.where(f >= 0.5, 1.0, np.where(f >= 0.2, 0.45, 0.0))
    w = LAMP * d / (D - d)                                        # the penumbra on the wall (m)
    sv, sh = w * VPX / 2.5, w * HPX / 2.5
    a = ndimage.gaussian_filter(hard, (sv, sh)) if sv > 0.45 else hard
    core = np.clip(ndimage.gaussian_filter((hard > 0.5).astype(float), 1.0) / 0.8, 0, 1)
    a = np.round(np.clip(a, 0, 1) * (0.8 + 0.2 * core) * STEPS) / STEPS * dens_of(d)
    ys, xs = np.nonzero(a > 0)
    if not len(ys): return None
    t, b, l, rg = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    return a[t:b, l:rg], -x0 - l, int(t)


def paper_mask():
    """the lit paper of the two doors (the street's light over its unlit layer's, from frame to paper: the rails, the
    stiles, the noren and the sign in front of it out)"""
    c = np.asarray(Image.open(os.path.join(ASSETS, 'layer_city_off.webp')).convert('RGB')).astype(float)
    u = np.asarray(Image.open(os.path.join(ASSETS, 'street_unlit.webp')).convert('RGB')).astype(float)
    x0, y0, x1, y1 = MASK_BOX
    dl = (c - u)[y0:y1, x0:x1] @ np.array([0.299, 0.587, 0.114])
    return np.clip((dl - MASK[0]) / (MASK[1] - MASK[0]), 0, 1)



# ---- the class (the evening's: the sensei and three students; the children's, late afternoon: three children). The kamiza
# on the left (the house's end): they line up facing left, in two staggered rows, the first row's nearest the paper; the
# sensei faces them from the left door. Places: (X: the column at the paper's scale, d: m behind the paper)
LINE = [(60, 0.6), (66, 1.5), (95, 2.3)]          # (their shadows: x 62, the right door; 72, its edge, bigger, softer; out)
KLINE = [(58, 0.55), (68, 1.2), (92, 1.8)]
KATA = [(62, 1.5), (30, 2.2), (100, 2.4)]          # the kata: spread out in the room (each needs his space)
SENSEI = (18, 0.8)                                 # (his shadow: x 16, the left door)
STEP = 0.85                                        # a step in zenkutsu-dachi (m)

# a class's moves, all in step: (seconds, pose, facing, dX (m, + to the right), dd (m, + deeper)). Facing: side views r, l
# (right, left: the frame mirrored); front views t (to the street, as drawn), T (mirrored: the other arm), a (away, seen
# from behind: mirrored), A (away, the other arm)
def kneel(face='l', down=True):
    m = [(0.22, 'attention', face, 0, 0, 0.2), (0.22, 'attention', face, 0, 0, 0.42), (0.3, 'seiza', face, 0, 0)]
    return m if down else [(0.3, 'attention', face, 0, 0, 0.42), (0.25, 'attention', face, 0, 0, 0.2)]


def ceremony(close=False):
    """the line-up (seiza, mokuso, shomen ni rei, sensei ni rei, otagai ni rei; standing, rei)"""
    m = [(4.0, 'attention', 'l', 0, 0)] + kneel()
    m += [(14.0 if close else 22.0, 'seiza', 'l', 0, 0)]          # mokuso
    for _ in range(3 if close else 2):
        m += [(0.35, 'seiza_rei', 'l', 0, 0), (2.0, 'seiza_rei', 'l', 0, 0), (1.8, 'seiza', 'l', 0, 0)]
    m += kneel(down=False) + [(2.5, 'attention', 'l', 0, 0), (1.3, 'rei', 'l', 0, 0), (2.2, 'attention', 'l', 0, 0)]
    return m


def sensei_ceremony(close=False):
    out = [(4.0, 'attention', 'r'), (0.22, 'attention', 'r', 0.2), (0.22, 'attention', 'r', 0.42), (0.3, 'seiza', 'r')]
    out += [(14.0 if close else 22.0, 'seiza', 'r')]
    for i in range(3 if close else 2):
        out += [(0.35, 'seiza_rei', 'r'), (2.0, 'seiza_rei', 'r'), (1.8, 'seiza', 'r')] if i else [(0.35, 'seiza', 'l'), (2.0, 'seiza_rei', 'l'), (1.8, 'seiza', 'r')]
    out += [(0.3, 'attention', 'r', 0.42), (0.25, 'attention', 'r', 0.2), (2.5, 'attention', 'r'), (1.3, 'rei', 'r'), (2.2, 'attention', 'r')]
    return out


def on_spot(tech, n=10, prep=None, tempo=1.05):
    """kihon on the spot, counted: yoi, then n of the technique (the last with a kiai: held), yame"""
    m = [(2.4, 'yoi', 'l', 0, 0)]
    for i in range(n):
        if prep: m += [(0.16, prep, 'l', 0, 0)]
        else: m += [(0.12, 'yoi', 'l', 0, 0)]
        m += [((1.6 if i == n - 1 else tempo - 0.14), tech, 'l', 0, 0)]
    return m + [(2.2, 'yoi', 'l', 0, 0)]


def moving(tech, prep, n=3, kamae='gedan', kick=False, length=STEP):
    """kihon moving: from yoi a step back into the stance, n techniques stepping forward (the last with a kiai), mawatte
    (a turn: gedan-barai to the rear), n back, mawatte, yame"""
    m = [(2.0, 'yoi', 'l', 0, 0), (0.2, 'gedan_prep', 'l', 0.3, 0), (1.2, kamae, 'l', 0.42, 0)]
    x = 0.42
    for face, sg in (('l', -1), ('r', 1)):
        for i in range(n):
            if kick:
                m += [(0.22, 'maegeri_ch', face, x, 0), (0.34, 'maegeri', face, x, 0), (0.2, 'maegeri_ch', face, x + sg * 0.25, 0)]
                x += sg * length; m += [((1.3 if i == n - 1 else 0.7), 'gedan', face, x, 0)]
            else:
                m += [(0.2, prep, face, x + sg * length / 2, 0)]
                x += sg * length; m += [((1.4 if i == n - 1 else 0.8), tech, face, x, 0)]
        nf = 'r' if face == 'l' else 'l'                            # mawatte: the turn, gedan-barai to the rear
        m += [(0.22, 'gedan_prep', nf, x, 0), (1.1 if face == 'l' else 0.5, 'gedan', nf, x, 0)]
    m[-2:] = [(0.22, 'gedan_prep', 'l', x, 0), (1.0, 'gedan', 'l', x, 0)]
    return m + [(0.2, 'step', 'l', 0.2, 0), (2.0, 'yoi', 'l', 0, 0)]


def heian_shodan():
    """the kata, its 21 moves (Shotokan; the kiai on the 9th and the 17th), facing left: N is to the left (-x), W toward
    the paper (-d), E away (+d), S to the right; its rei before and after"""
    L, R = 'l', 'r'
    m = [(2.5, 'attention', L, 0, 0), (1.4, 'rei', L, 0, 0), (1.2, 'attention', L, 0, 0), (2.2, 'yoi', L, 0, 0)]
    m += [(0.16, 'yoi_f', 't', 0, -0.2), (0.95, 'gedan_f', 't', 0, -0.4)]            # 1: W, gedan-barai (left)
    m += [(0.16, 'yoi_f', 't', 0, -0.8), (0.95, 'oizuki_f', 'T', 0, -1.2)]           # 2: oi-zuki (right)
    m += [(0.16, 'yoi_f', 'a', 0, -1.0), (0.95, 'gedan_f', 'A', 0, -0.8)]            # 3: turn to E, gedan-barai (right)
    m += [(0.3, 'ageuke_f', 'A', 0, -0.8), (0.9, 'oizuki_f', 'A', 0, -0.8)]          # 4: tettsui-uchi (right)
    m += [(0.16, 'yoi_f', 'a', 0, -0.4), (0.95, 'oizuki_f', 'a', 0, 0.0)]            # 5: oi-zuki (left)
    m += [(0.2, 'gedan_prep', L, -0.2, 0), (0.95, 'gedan', L, -0.4, 0)]              # 6: N, gedan-barai (left)
    for i, x in enumerate((-1.2, -2.0, -2.8)):                                       # 7-9: age-uke, stepping (kiai)
        m += [(0.2, 'ageuke_prep', L, x + 0.4, 0), ((1.5 if i == 2 else 0.75), 'ageuke', L, x, 0)]
    m += [(0.2, 'yoi_f', 'a', -2.8, 0.2), (0.95, 'gedan_f', 'a', -2.8, 0.4)]        # 10: turn 270 to E, gedan-barai
    m += [(0.16, 'yoi_f', 'a', -2.8, 0.8), (0.95, 'oizuki_f', 'A', -2.8, 1.2)]       # 11: oi-zuki
    m += [(0.16, 'yoi_f', 't', -2.8, 1.0), (0.95, 'gedan_f', 'T', -2.8, 0.8)]        # 12: turn to W, gedan-barai
    m += [(0.16, 'yoi_f', 't', -2.8, 0.4), (0.95, 'oizuki_f', 't', -2.8, 0.0)]       # 13: oi-zuki
    m += [(0.2, 'gedan_prep', R, -2.6, 0), (0.95, 'gedan', R, -2.4, 0)]              # 14: S, gedan-barai
    for i, x in enumerate((-1.6, -0.8, 0.0)):                                        # 15-17: oi-zuki, stepping (kiai)
        m += [(0.2, 'step', R, x - 0.4, 0), ((1.5 if i == 2 else 0.7), 'oizuki', R, x, 0)]
    m += [(0.25, 'shuto_prep', L, 0.0, -0.2), (0.95, 'shuto', L, -0.1, -0.4)]       # 18: turn 270 to W, shuto-uke (left)
    m += [(0.25, 'shuto_prep', L, -0.4, -0.7), (0.95, 'shuto', L, -0.6, -0.9)]      # 19: 45 degrees, shuto-uke (right)
    m += [(0.25, 'shuto_prep', R, -0.3, -0.6), (0.95, 'shuto', R, 0.1, -0.5)]       # 20: turn 135, shuto-uke (right)
    m += [(0.25, 'shuto_prep', R, 0.3, -0.7), (1.3, 'shuto', R, 0.5, -0.9)]         # 21: 45 degrees, shuto-uke (left)
    m += [(0.3, 'yoi', L, 0.2, -0.4), (2.4, 'yoi', L, 0, 0), (1.2, 'attention', L, 0, 0), (1.4, 'rei', L, 0, 0), (2.0, 'attention', L, 0, 0)]
    return m


def walk(X0, X1, d, v=0.75, t0=0):
    """a walk in profile from X0 to X1 (px), its two frames at a quarter of a second each (a step every half second)"""
    n = max(1, int(round(abs(X1 - X0) / HPX / v / 0.25))); f = 'r' if X1 > X0 else 'l'
    return [(0.25, ('walk_a', 'walk_b')[(i + t0) % 2], f, X0 + (X1 - X0) * i / n, d, X0 + (X1 - X0) * (i + 1) / n) for i in range(n)]


def students(moves, form, kid=False):
    """each student's track: the class's moves from his place"""
    return [[(m[0], m[1], m[2], X + m[3] * HPX, d + m[4], None, m[5] if len(m) > 5 else 0.0, kid) for m in moves] for X, d in form]


def stand(dur, pose='attention', face='l', X=0, d=0.6, kid=False, drop=0.0): return (dur, pose, face, X, d, None, drop, kid)


def sensei(items, X=SENSEI[0], d=SENSEI[1]):
    """the sensei's track: (seconds, pose, facing[, drop]) at his place, a walk's items as they are, (seconds,) away"""
    out = []
    for it in items:
        if len(it) == 1: out.append((it[0], None))
        elif len(it) == 6: out.append(it + (0.0, False))
        else: out.append((it[0], it[1], it[2], X, d, None, it[3] if len(it) > 3 else 0.0, False))
    return out


def regroup(A, B, dur=4.0, kid=False):
    """from one formation to the next, each walking (in profile, toward where he goes)"""
    out = []
    for (Xa, da), (Xb, db) in zip(A, B):
        n = int(dur / 0.25); f = 'r' if Xb >= Xa else 'l'
        out.append([(0.25, ('walk_a', 'walk_b')[i % 2], f, Xa + (Xb - Xa) * i / n, round(da + (db - da) * (i + 0.5) / n, 1),
                     Xa + (Xb - Xa) * (i + 1) / n, 0.0, kid) for i in range(n)])
    return out


def tlen(tr): return sum(it[0] for it in tr)


def pad(tr, T, at_end=None):
    """a track held to T seconds: its last item lengthened (or away)"""
    t = tlen(tr)
    if t < T - 1e-6: tr = tr + [((T - t),) + (tuple(at_end[1:]) if at_end else (None,))]
    return tr


def segments():
    """every segment the page plays: name -> its actors' tracks (each a list of items: (seconds, pose, facing, X, d, X at
    its end or None, drop, child) or (seconds, None): not there)"""
    S = {}
    for pre, form, kid in (('', LINE, False), ('k_', KLINE, True)):         # the line-up, the bows: opening, closing
        for nm, close in (('open', False), ('close', True)):
            st = students(ceremony(close), form, kid); T = tlen(st[0])
            S[pre + nm] = st + [pad(sensei(sensei_ceremony(close)), T)]
    for kid, form, pre in ((False, LINE, ''), (True, KLINE, 'k_')):
        reps = {'choku': on_spot('choku', 10), 'ageuke': moving('ageuke', 'ageuke_prep'), 'oizuki': moving('oizuki', 'step'),
                'gedan': moving('gedan', 'gedan_prep'), 'maegeri': moving(None, None, kick=True, length=0.7)}
        if not kid: reps['shuto'] = moving('shuto', 'shuto_prep', kamae='shuto', length=0.7)
        for name, mv in reps.items():
            st = students(mv, form, kid); T = tlen(st[0])
            # the sensei: shows the technique first, facing them (on the spot), or walks out of their way and along the line
            if name == 'choku':
                se = sensei([(3.0, 'fold', 'r'), (T - 9.0, 'fold', 'r'), (6.0, 'attention', 'r')])
            else:
                w = walk(SENSEI[0], -40, 0.3)
                se = sensei([(1.6, 'fold', 'r')] + w + [(T - 1.6 - tlen(w) - 6.0,)] + walk(-40, SENSEI[0], 0.3) )
                se = pad(se, T, at_end=(0, 'fold', 'r', SENSEI[0], SENSEI[1], None, 0.0, False))
            S[pre + name] = st + [se[:]]
        # a rest: they stand at ease, the sensei walks along the line (behind them, between them and the paper), stops,
        # looks, walks on, comes back to his place
        w1 = walk(-30, 52, 0.3); w2 = walk(52, 120, 0.3, t0=1); w3 = walk(120, SENSEI[0], 0.35)
        se = sensei(w1, 52, 0.3) + sensei([(1.2, 'attention', 'r'), (5.5, 'fold', 'r')], 52, 0.3) + sensei(w2 + [(6.0,)] + w3)
        T = tlen(se)
        st = [[stand(T * 0.45, 'attention', 'l', X, d, kid), stand(T * 0.55, 'yoi', 'l', X, d, kid)] for X, d in form]
        S[pre + 'rest'] = st + [se]
    # the kata: the class goes to its places, Heian Shodan, back to the line
    kt = students(heian_shodan(), KATA); T = tlen(kt[0])
    g1, g2 = regroup(LINE, KATA), regroup(KATA, LINE)
    out, back = walk(SENSEI[0], -40, 0.3), walk(-40, SENSEI[0], 0.3, t0=1)
    T0, T1 = tlen(g1[0]), tlen(g2[0])
    se = sensei([(T0 + 1.5, 'fold', 'r')] + out + [(T - 1.5 - tlen(out) - 7.0,)] + back + [(7.0 - tlen(back) + T1, 'fold', 'r')])
    S['kata'] = [a + b + c for a, b, c in zip(g1, kt, g2)] + [se]
    # out of class: someone crosses the room (the sensei, a student early or late), close to the paper or further in
    S['cross_r'] = [sensei(walk(-30, 120, 0.35))]
    S['cross_l'] = [sensei(walk(115, -35, 0.9, v=0.9))]
    for k, v in S.items():
        L = [tlen(t) for t in v]; assert max(L) - min(L) < 0.05, (k, L)
    return S


FRONT_VIEWS = set(FRONT)
MIRROR = {'r': 0, 'l': 1, 't': 0, 'T': 1, 'a': 1, 'A': 0}


def beats(tracks):
    """a segment's tracks cut at every change: [(seconds, [(pose, facing, X at its start, X at its end, d, drop, child)
    or None, an actor each])]"""
    cuts = {0.0}
    for tr in tracks:
        t = 0.0
        for it in tr: t += it[0]; cuts.add(round(t, 4))
    cuts = sorted(cuts); out = []
    for a, b in zip(cuts, cuts[1:]):
        if b - a < 1e-4: continue
        row = []
        for tr in tracks:
            t = 0.0
            for it in tr:
                if a < t + it[0] - 1e-6: break
                t += it[0]
            if len(it) == 2 or it[1] is None: row.append(None); continue
            dur, pose, face, X, d, Xe, drop, kid = it
            if Xe is None: X0 = X1 = X
            else: X0, X1 = X + (Xe - X) * (a - t) / dur, X + (Xe - X) * (b - t) / dur
            row.append((pose, face, X0, X1, d, drop, kid))
        out.append((b - a, row))
    return out


class Frames:
    """the frames as they are asked for: (pose, d to 0.1 m, child, drop) -> its index (None: nothing of it shows)"""
    def __init__(self): self.cv = covers(); self.key = {}; self.list = []

    def get(self, pose, d, kid, drop):
        k = (pose, round(d, 1), bool(kid), round(drop, 2))
        if k not in self.key:
            c, floor, hx, s = self.cv[pose]
            f = frame(c, floor, hx, s, k[1], k[2], k[3])
            self.key[k] = None if f is None else len(self.list)
            if f is not None: self.list.append(f)
        return self.key[k]


def encode(seg, FR):
    """a segment as the page plays it: beats [centiseconds, then for each actor seen: v, x at the beat's start, x at its
    end] (v: the frame's index + 1, negative mirrored; x: the column of the hips' shadow); the same beats running on merged"""
    out = []
    for dur, row in beats(seg):
        b = []
        for a in row:
            if a is None: continue
            pose, face, X0, X1, d, drop, kid = a
            i = FR.get(pose, d, kid, drop)
            if i is None: continue
            fa, ax, _ = FR.list[i]; w = fa.shape[1]; m = MIRROR[face]
            x0, x1 = (int(math.floor(shadow_x(X, round(d, 1)))) for X in (X0, X1))
            lo, hi = min(x0, x1), max(x0, x1)
            span = (lo - (w - 1 - ax), hi + ax + 1) if m else (lo - ax, hi - ax + w)
            if span[1] <= MASK_BOX[0] or span[0] >= MASK_BOX[2]: continue           # (all of it off the paper)
            b += [-(i + 1) if m else i + 1, x0, x1]
        cs = int(round(dur * 100))
        if out and out[-1][1:] == b and all(b[j + 1] == b[j + 2] for j in range(0, len(b), 3)): out[-1][0] += cs
        else: out.append([cs] + b)
    return out


def sheet():
    """the frames packed on shelves (the tallest first), the paper's mask on the last one; each f: [x, y, w, h, the
    anchor's column, the top row in the strip]"""
    FR = Frames(); S = {k: encode(v, FR) for k, v in segments().items()}
    W = 1024; order = sorted(range(len(FR.list)), key=lambda i: -FR.list[i][0].shape[0])
    place = {}; x = y = sh = 0
    for i in order:
        a = FR.list[i][0]
        if x + a.shape[1] > W: x, y, sh = 0, y + sh, 0
        place[i] = (x, y); x += a.shape[1]; sh = max(sh, a.shape[0])
    y += sh; m = paper_mask(); out = np.zeros((y + m.shape[0], W))
    F = []
    for i, (a, ax, top) in enumerate(FR.list):
        px, py = place[i]; out[py:py + a.shape[0], px:px + a.shape[1]] = a
        F.append([px, py, a.shape[1], a.shape[0], int(ax), top])
    out[y:y + m.shape[0], :m.shape[1]] = m
    meta = dict(F=F, M=[0, y, m.shape[1], m.shape[0]], box=[MASK_BOX[0], MASK_BOX[1], MASK_BOX[2] - MASK_BOX[0], MASK_BOX[3] - MASK_BOX[1]],
                y0=STRIP[0], S=S)
    return out, meta, FR


def build():
    a, meta, FR = sheet()
    rgba = np.zeros(a.shape + (4,), np.uint8); rgba[..., 3] = np.round(np.clip(a, 0, 1) * 255)
    Image.fromarray(rgba, 'RGBA').save(os.path.join(ASSETS, 'dojo_class.webp'), 'WEBP', lossless=True, quality=100, method=6, exact=True)
    js = open(JS, encoding='utf-8').read()
    line = '  const DJC = ' + json.dumps(meta, separators=(',', ':')) + ';   // (tools/dojo_class.py)'
    js2, n = re.subn(r'  const DJC = \{.*?\};   // \(tools/dojo_class\.py\)', lambda m: line, js, count=1)
    assert n == 1, 'the line DJC is missing from assets/street.js'
    if js2 != js: open(JS, 'w', encoding='utf-8').write(js2)
    print('dojo class: %d frames, sheet %d x %d, %d segments (%s s), DJC %d chars %s' % (len(meta['F']), a.shape[1], a.shape[0],
          len(meta['S']), ', '.join('%s %.0f' % (k, sum(b[0] for b in v) / 100) for k, v in meta['S'].items()), len(line),
          'written' if js2 != js else 'unchanged'))


def compose(a, meta, name, t, base, mask):
    """the paper at t seconds into a segment, as the page lays it (for previews): the street's crop darkened"""
    bx, by, bw, bh = meta['box']; cnv = np.zeros((bh, bw))
    T = 0
    for b in meta['S'][name]:
        if T + b[0] / 100 > t: break
        T += b[0] / 100
    u = (t - T) / max(1e-6, b[0] / 100)
    for j in range(1, len(b), 3):
        v, x0, x1 = b[j:j + 3]; i = abs(v) - 1; m = v < 0
        sx, sy, w, h, ax, top = meta['F'][i]; X = int(round(x0 + (x1 - x0) * u))
        f = a[sy:sy + h, sx:sx + w]
        if m: f = f[:, ::-1]; ax = w - 1 - ax
        for r in range(h):
            yy = top + meta['y0'] + r - by
            if not 0 <= yy < bh: continue
            for c in range(w):
                xx = X - ax + c - bx
                if 0 <= xx < bw: cnv[yy, xx] = 1 - (1 - cnv[yy, xx]) * (1 - f[r, c])
    cnv *= mask
    out = base.copy().astype(float); out[by:by + bh, bx:bx + bw] *= (1 - cnv[..., None])
    return out


def preview(out, names=None, fps=8, scale=3):
    """each segment as a GIF over the street's crop (the lit layer) at x scale, and the frames sheet at x4"""
    os.makedirs(out, exist_ok=True)
    a, meta, FR = sheet()
    Image.fromarray((255 - np.clip(a, 0, 1) * 255).astype(np.uint8)).resize((a.shape[1] * 2, a.shape[0] * 2), Image.NEAREST).save(os.path.join(out, 'sheet_x2.png'))
    base = np.asarray(Image.open(os.path.join(ASSETS, 'layer_city_off.webp')).convert('RGB')).astype(float)
    mask = paper_mask(); crop = (0, 500, 130, 760)
    for name in names or meta['S']:
        Tn = sum(b[0] for b in meta['S'][name]) / 100; ims = []
        for k in range(int(Tn * fps)):
            im = compose(a, meta, name, k / fps, base, mask)[crop[1]:crop[3], crop[0]:crop[2]]
            ims.append(Image.fromarray(np.clip(im, 0, 255).astype(np.uint8)).resize(((crop[2] - crop[0]) * scale, (crop[3] - crop[1]) * scale), Image.NEAREST))
        ims[0].save(os.path.join(out, name + '.gif'), save_all=True, append_images=ims[1:], duration=int(1000 / fps), loop=0)
        print(name, len(ims), 'frames')


def main():
    if '--ask' in sys.argv: ask(); return
    if '--preview' in sys.argv:
        i = sys.argv.index('--preview'); preview(sys.argv[i + 1], sys.argv[i + 2].split(',') if len(sys.argv) > i + 2 else None); return
    if '--input' in sys.argv:
        guide().save(os.path.join(EDITS, 'dojoclass_in.webp'), 'WEBP', lossless=True, quality=100, method=6); return
    build()


if __name__ == '__main__':
    main()
