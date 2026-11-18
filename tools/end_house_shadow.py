#!/usr/bin/env python3
"""The far house's upstairs window (the comp win_z9_window: its curtains lit warm, a 'home' on its hours): now and then the
soft shadow of someone in the room on them, crossing, or stopping to stretch.

    python3 tools/end_house_shadow.py --input      writes the sheet's guide (tools/src/edits/z9shadow_in.webp: two rows of six
                                                   cells, a baseline and a head mark in each)
    python3 tools/end_house_shadow.py --ask        asks the image model for the sheet (its prompt z9shadow_prompt.txt, its
                                                   answer z9shadow_model.webp; about 0.25 $)
    python3 tools/end_house_shadow.py              writes assets/z9_shadow.webp (the frames, the shadow's density in their
                                                   alpha, at the scene's pixels) and, in assets/street.js, the line Z9S;
                                                   again: the same bytes
    python3 tools/end_house_shadow.py --preview D  the frames at x8 and over the lit window, nothing written in assets/

The silhouettes are drawn by the image model (R28): one person at home in twelve frames, a walk in profile, a stop, a turn,
a morning stretch; each frame keyed off its pale ground (the silhouette's cover, its antialias kept), its figure alone (the
largest shape), anchored on its feet's baseline and its torso's middle (the feet are below the window: what shows is the
head, the shoulders, the arms and the chest), brought to the scene (each scene pixel the mean of what it covers, FIG_PX for
the whole figure: the shadow a little larger than the person, cast by the room's light behind), softened as a shadow cast
through a curtain is (PENUMBRA), at DENSITY at most: the curtain still glows through it. street.js lays it over the comp with
a darkening blend (the lit curtain times one minus the density: right in every grade, the red night's too), clipped by the
comp's lit curtains (its alpha times its light: the railing in front, the frame and the mullion untouched;
a mask after the frames in the sheet), only while the window is lit and on screen; never under reduced motion,
never in the power cut.
Needs Pillow, numpy, scipy.
"""
import base64
import io
import json
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
SHEET = (6, 2, 256, 512)                         # the guide: columns, rows, a cell's width and height (1536 x 1024)
GUIDE = dict(base=480, head=80)                  # (in each cell: the feet's baseline, the head's mark)
NAMES = ['w0', 'w1', 'w2', 'w3', 'w4', 'w5', 'stand', 'turn', 'front', 'rise', 'up', 'lean']
FIG_PX = 50                                      # the whole figure in scene px (1.65 m at ~30 px a metre on the house's front,
                                                 # a little larger cast on the curtain)
CELL = (34, 44, 17)                              # a frame in the scene: its width, its height, its anchor's column
TOP = -9                                         # the frame's top row in the window (its anchor, the feet, 68 rows under it:
                                                 # the head at row 9, the hands of the stretch over the window's head)
MASK = (50.0, 90.0)                              # (the comp's light, from dark to lit curtain: the mask's ramp)
PENUMBRA = 0.5                                   # (the shadow's softness, px)
DENSITY = 0.58                                   # (its darkest: the curtain's light times 1 - this)


def guide():
    c, r, w, h = SHEET
    im = Image.new('RGB', (c * w, r * h), (234, 224, 210)); g = ImageDraw.Draw(im)
    for j in range(r):
        for i in range(c):
            x0, y0 = i * w, j * h
            g.rectangle([x0, y0, x0 + w - 1, y0 + h - 1], outline=(176, 168, 158), width=2)
            g.line([x0 + 24, y0 + GUIDE['base'], x0 + w - 24, y0 + GUIDE['base']], fill=(150, 144, 136), width=3)
            g.line([x0 + 6, y0 + GUIDE['head'], x0 + 22, y0 + GUIDE['head']], fill=(150, 144, 136), width=3)
    return im


def api_key():
    k = os.environ.get('OPENROUTER_API_KEY')
    if k: return k
    p = os.path.expanduser('~/.config/openrouter/key')
    return open(p).read().strip() if os.path.exists(p) else 'proxy-injected'


def ask():
    content = [{"type": "text", "text": open(os.path.join(EDITS, 'z9shadow_prompt.txt')).read().strip()}]
    buf = io.BytesIO(); Image.open(os.path.join(EDITS, 'z9shadow_in.webp')).convert('RGB').save(buf, 'PNG')
    content.append({"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()}})
    body = {"model": MODEL, "modalities": ["image", "text"], "usage": {"include": True}, "messages": [{"role": "user", "content": content}]}
    req = urllib.request.Request('https://openrouter.ai/api/v1/chat/completions', data=json.dumps(body).encode(),
                                 headers={'Authorization': 'Bearer ' + api_key(), 'Content-Type': 'application/json'})
    d = json.loads(urllib.request.urlopen(req, timeout=900).read())
    url = d['choices'][0]['message']['images'][0]['image_url']['url']
    im = Image.open(io.BytesIO(base64.b64decode(url.split(',', 1)[1])))
    im.save(os.path.join(EDITS, 'z9shadow_model.webp'), 'WEBP', lossless=True, quality=100, method=6)
    print('answer', im.size, 'saved; cost', d.get('usage', {}).get('cost'), '$')


def cover(a):
    """the silhouette's cover in a cell (0..1, its antialias kept): its figure alone, the guide's lines and borders out"""
    L = a @ np.array([0.299, 0.587, 0.114])
    bg = np.percentile(L, 90); fg = np.percentile(L[L < bg - 60], 20) if (L < bg - 60).any() else bg - 150
    cov = np.clip((bg - 12 - L) / max(1.0, bg - 12 - fg), 0, 1)
    lab, n = ndimage.label(cov > 0.5)
    if n == 0: return cov * 0
    keep = lab == (1 + int(np.argmax(ndimage.sum(np.ones_like(L), lab, range(1, n + 1)))))
    keep = ndimage.binary_dilation(keep, iterations=3)
    return cov * keep


def frames():
    """the twelve frames at the scene's pixels: each its shadow's density (h, w), its anchor (the feet, the torso's middle)
    on CELL's anchor column and on the row 68 - TOP under the frame's top"""
    im = np.asarray(Image.open(os.path.join(EDITS, 'z9shadow_model.webp')).convert('RGB')).astype(float)
    c, r = SHEET[0], SHEET[1]; H, W = im.shape[:2]; cw, ch = W / c, H / r
    covs, meas = [], []
    for k in range(c * r):
        i, j = k % c, k // c
        a = im[int(j * ch) + 8:int((j + 1) * ch) - 8, int(i * cw) + 8:int((i + 1) * cw) - 8]
        cv = cover(a); covs.append(cv)
        ys, xs = np.nonzero(cv > 0.5)
        meas.append([ys.min(), ys.max(), 0.0])
    # one scale a row (the answer drew its two rows a little apart in size): the figure's height upright in each, FIG_PX
    upright = {0: range(0, 6), 1: range(6, 10)}         # (the walk; the stand, the turn, the front, the arms rising)
    hu = {j: np.median([meas[k][1] - meas[k][0] for k in ks]) for j, ks in upright.items()}
    S = {j: FIG_PX / h for j, h in hu.items()}          # (scene px an answer px)
    for k, cv in enumerate(covs):                       # (the anchor's column: the torso's middle, from the chest to the hips,
        ys, xs = np.nonzero(cv > 0.5); h = hu[k // c]    # measured up from the soles: the raised arms left out)
        band = (ys < meas[k][1] - 0.5 * h) & (ys > meas[k][1] - 0.78 * h)
        meas[k][2] = xs[band].mean() if band.any() else xs.mean()
    out = []
    fw, fh, ax = CELL; feet = 9 + FIG_PX - TOP          # (the anchor's row in the frame: its bottom edge on the soles)
    for k, (cv, (top, foot, cx)) in enumerate(zip(covs, meas)):
        n = 1.0 / S[k // c]                             # (answer px a scene px)
        pad = int(4 * fh * n)
        big = np.pad(cv, pad)
        x0, y0 = cx + pad - ax * n - 0.5 * n, foot + 1 + pad - feet * n   # (the frame's corner in the answer: the anchor's pixel
        im_ = Image.fromarray(big.astype(np.float32), 'F')                # centred on the torso, the soles on its row's foot)
        f = np.asarray(im_.resize((fw, fh), Image.BOX, box=(x0, y0, x0 + fw * n, y0 + fh * n))).astype(float)   # (each scene
        f = np.where(f >= 0.5, np.maximum(f, 0.85), f * 0.6)    # pixel the mean of what it covers; solid from half covered)
        f = ndimage.gaussian_filter(f, PENUMBRA)
        out.append(np.clip(f, 0, 1) * DENSITY)
    return out, S[0]


def curtain_mask():
    """where the comp lights the curtains (its alpha times its light: the frame, the mullion and the wall round them out)"""
    c = np.asarray(Image.open(os.path.join(ASSETS, 'win_z9_window.webp')).convert('RGBA')).astype(float)
    L = c[..., :3] @ np.array([0.299, 0.587, 0.114])
    return np.clip((L - MASK[0]) / (MASK[1] - MASK[0]), 0, 1) * c[..., 3] / 255


def sheet():
    fr, s = frames(); fw, fh, ax = CELL; m = curtain_mask(); mh, mw = m.shape
    a = np.zeros((max(fh, mh), fw * len(fr) + mw, 4))
    for k, f in enumerate(fr): a[:fh, k * fw:(k + 1) * fw, 3] = np.round(f * 255)
    a[:mh, fw * len(fr):, 3] = np.round(m * 255)              # (the curtains' mask, after the frames)
    return a.astype(np.uint8), s


def build():
    a, s = sheet()
    Image.fromarray(a, 'RGBA').save(os.path.join(ASSETS, 'z9_shadow.webp'), 'WEBP', lossless=True, quality=100, method=6, exact=True)
    fw, fh, ax = CELL
    z = dict(w=fw, h=fh, ax=ax, top=TOP, mask=fw * len(NAMES), f={n: k for k, n in enumerate(NAMES)})
    js = open(JS, encoding='utf-8').read()
    line = '  const Z9S = ' + json.dumps(z, separators=(',', ':')) + ';   // (tools/end_house_shadow.py)'
    js2, n = re.subn(r'  const Z9S = \{.*?\};   // \(tools/end_house_shadow\.py\)', lambda m: line, js, count=1)
    assert n == 1, 'the line Z9S is missing from assets/street.js'
    if js2 != js: open(JS, 'w', encoding='utf-8').write(js2)
    print('z9 shadow: %d frames %d x %d (%.3f scene px an answer px), Z9S %s' % (len(NAMES), fw, fh, s, 'written' if js2 != js else 'unchanged'))


def preview(out):
    os.makedirs(out, exist_ok=True)
    a, s = sheet(); fw, fh, ax = CELL
    al = a[..., 3].astype(float) / 255
    bg = np.array([236, 150, 120.0]); img = bg * (1 - al[..., None])
    Image.fromarray(img.astype(np.uint8)).resize((a.shape[1] * 8, fh * 8), Image.NEAREST).save(os.path.join(out, 'z9_shadow_x8.png'))
    win = np.asarray(Image.open(os.path.join(ASSETS, 'win_z9_window.webp')).convert('RGBA')).astype(float)
    tiles = []
    for k, x in ((0, 14), (3, 30), (8, 28), (10, 28), (11, 28)):
        w = win.copy(); f = al[:, k * fw:(k + 1) * fw]
        for yy in range(fh):
            for xx in range(fw):
                X, Y = x - ax + xx, TOP + yy
                if 0 <= X < w.shape[1] and 0 <= Y < w.shape[0]: w[Y, X, :3] *= 1 - f[yy, xx] * w[Y, X, 3] / 255
        tiles.append(Image.fromarray(w.astype(np.uint8), 'RGBA').resize((w.shape[1] * 8, w.shape[0] * 8), Image.NEAREST))
    c = Image.new('RGBA', (sum(t.width + 8 for t in tiles), tiles[0].height), (0, 0, 0, 255)); x = 0
    for t in tiles: c.paste(t, (x, 0), t); x += t.width + 8
    c.save(os.path.join(out, 'z9_shadow_in_window_x8.png'))


def main():
    if '--input' in sys.argv:
        guide().save(os.path.join(EDITS, 'z9shadow_in.webp'), 'WEBP', lossless=True, quality=100, method=6); return
    if '--ask' in sys.argv: ask(); return
    if '--preview' in sys.argv: preview(sys.argv[sys.argv.index('--preview') + 1]); return
    build()


if __name__ == '__main__':
    main()
