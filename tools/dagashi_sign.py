#!/usr/bin/env python3
"""The dagashi-ya's sign over its window (the owner: "Maj panneau dagashi, je pense aplat moche actuellement"; after three
rounds of options, "le style ne va pas avec le reste", then "A, caisson laiteux"): an old lit sign box on the shop's dark
fascia, painted as the street's own signs are (the oden's red box on its roof, its lantern, the dojo's 心源流 plank).

    (a module: tools/redraw_zones.py's zone 'dagsign', the last, calls draw() on the street as the zones before it leave
    it: the box unlit in the layers; and it writes its light, assets/z7_dagsign.webp, which assets/street.js lays on it
    on the shop's hours: the same bytes each time)
    python3 tools/dagashi_sign.py --before         once: the zone's before crops (tools/src/edits/dagsign_before_*.webp)
    python3 tools/dagashi_sign.py --preview DIR    the box unlit and lit over the layers as they are, x1 and x4
    python3 tools/dagashi_sign.py --ask            the image call again (OpenRouter's key in ~/.config/openrouter/key)

The box is drawn by the image model (R28) in its context: the street at 22 h round the shop, its neighbours' signs in it,
brightened (x ** (1 / GAMMA)) and enlarged twice (tools/src/edits/dagsign_in.webp), asked in the painter's style (the
prompt: dagsign_prompt.txt): a long horizontal box, its milky face lit warm from inside and a little uneven, a worn
wooden frame with a chipped corner, a rain streak, だがし in thick red-brown letters, its glow on the fascia round it
(the answer: dagsign_model.webp). Here the answer is registered on the street (REG: its scale and shift, fitted once on
what did not change round the sign), its brightening undone, brought down to the street's pixels by area (each pixel
the mean of 4 x 4 samples), its colours carried from the 22 h render into the base layer (COLOR: a gain and an offset
per channel, fitted on the unchanged ring round it).

The box itself (its face: what is lighter than FACE_LUM on the sign's place, holes filled; its frame, FRAME px round
it), quantised to COLORS tones of its own. In the layers (layer_city_off and street_unlit alike: the shop shut, the
power cut), the box unlit: its frame as drawn, a little darker (FRAME_OFF); its milky face in the dusk's cool grey
(OFF_TONE, the drawing's own unevenness kept in it), its letters and its streak dark red-brown (the lit ones, INK_OFF);
round it the painter's fascia as he left it. Its light, assets/z7_dagsign.webp over CBOX: the lit box where it is lighter
than the unlit one, and its warm glow on the fascia, the band below and the boards round it (the answer there, where it
is warmer and lighter than the street, GLOW px at most from the box), its alpha the difference, as the street's other
comps (tools/soda_corner.py's comp_from). street.js: a 'sign' on the shop's hours (NSCHED 'dagashi'), breathing a
little (lightLife), out in the power cut and red in the red night as every comp; its box in ASSETS.comps kept here
(its version kept). Its light does not reach the wet sidewalk 3 m below in any measurable way: no ground light.
Needs Pillow, numpy, scipy.
"""
import os
import re
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDITS = os.path.join(ROOT, 'tools', 'src', 'edits')
ASSETS = os.path.join(ROOT, 'assets')
MODEL = 'openai/gpt-5.4-image-2'
GAMMA = 2.0
REG = (0, 300, 1.995, 1.0, -2.5)               # (the answer's street origin, its pixels a street pixel, its shift: answer
                                               #  pixel = ((x - ox) * s + dx, (y - oy) * s + dy))
COLOR = ((1.09, -1.0), (0.92, 0.9), (1.02, 0.8))   # (from the 22 h render's colours to the base layer's: gain, offset)
BOX = (138, 476, 227, 541)                     # the zone (redraw_zones.py 'dagsign'): the sign's place on the fascia
CBOX = (134, 470, 231, 544)                    # its light's box (street.js ASSETS.comps.z7_dagsign)
TOP = ((138, 484), (160, 489), (182, 494), (226, 500))   # (the fascia's top, under the face: soda_corner.FACE_SIGN)
BOT, X0, X1 = 536, 140, 227                    # (the fascia's last row over the window's frame; from the post to the corner)
VP, F_, EYE = (700.0, 615.0), 1400.0, 1.5     # (the street's camera)
XB = 6.29                                      # (the box's face: 4 cm proud of the house's front, m left of the eye)
FACE_LUM = 70.0                                # (the box's lit face in the answer: lighter than this)
FRAME = 2                                      # (its wooden frame round the face, px)
FRAME_TONE = np.array([38.0, 26.0, 28.0])      # (the frame unlit: dark old wood, the answer's grain in it)
OFF_TONE = np.array([46.0, 49.0, 68.0])        # (its milky face unlit, at dusk: a cool grey a little lighter than the post)
INK_T, INK_OFF = 0.78, 0.5                     # (its letters and its streak: darker than this share of the face's light
                                               #  round them; unlit, their lit colour times this)
COLORS = 20
GLOW = 5                                       # (its light round it: so many px from the box at most)
COMP = 'z7_dagsign'


def load(p, mode='RGBA'):
    return np.asarray(Image.open(p).convert(mode)).astype(float)


def lit_picture(box=CBOX, k=4):
    """The answer over box (street pixels), registered, its brightening undone, k x k samples a pixel, in the base
    layer's colours."""
    a = load(os.path.join(EDITS, 'dagsign_model.webp'), 'RGB')
    lin = (np.clip(a / 255.0, 0, 1) ** GAMMA) * 255
    ox, oy, s, dx, dy = REG; x0, y0, x1, y1 = box; w, h = x1 - x0, y1 - y0
    o = (np.arange(k) + 0.5) / k
    xs = ((np.arange(x0, x1)[:, None] + o[None, :] - ox) * s + dx).ravel()
    ys = ((np.arange(y0, y1)[:, None] + o[None, :] - oy) * s + dy).ravel()
    xi = np.clip(np.floor(xs).astype(int), 0, lin.shape[1] - 1); yi = np.clip(np.floor(ys).astype(int), 0, lin.shape[0] - 1)
    px = lin[yi][:, xi].reshape(h, k, w, k, 3).mean((1, 3))
    for c, (g, of) in enumerate(COLOR): px[..., c] = px[..., c] * g + of
    return np.clip(px, 0, 255)


def place(box=CBOX):
    """The sign's place over box: the fascia between the face's line and the window's frame, from the post to the corner."""
    x0, y0, x1, y1 = box
    X, Y = np.meshgrid(np.arange(x0, x1) + 0.5, np.arange(y0, y1) + 0.5)
    top = np.interp(X, [p[0] for p in TOP], [p[1] for p in TOP])
    return (X >= X0) & (X < X1) & (Y >= top) & (Y < BOT + 1) & (X >= BOX[0]) & (X < BOX[2]) & (Y >= BOX[1]) & (Y < BOX[3])


def lum(a):
    return a @ [0.299, 0.587, 0.114]


def shapes(lit):
    """The box over CBOX, in true perspective: its face's top and bottom on the house's rays (their heights fitted on
    the answer's lit face, the median over its middle columns), its ends where the answer's face ends; and the face
    with its frame (FRAME px round it)."""
    pl = place()
    f = ndi.binary_closing((lum(lit) > FACE_LUM) & pl, np.ones((3, 3)))
    lab, n = ndi.label(f)
    f = ndi.binary_fill_holes(lab == (1 + np.argmax(ndi.sum(np.ones(f.shape), lab, np.arange(1, n + 1)))))
    x0, y0, x1, y1 = CBOX
    cols = np.nonzero(f.any(0))[0]; c0, c1 = cols.min(), cols.max() + 1
    mid = cols[(cols >= c0 + 0.15 * (c1 - c0)) & (cols < c1 - 0.15 * (c1 - c0))]
    height = lambda x, y: EYE + (VP[1] - y) * XB / (VP[0] - x)             # (a point's height on the box's face, m)
    yt = np.median([height(x0 + c + 0.5, y0 + np.nonzero(f[:, c])[0].min()) for c in mid])
    yb = np.median([height(x0 + c + 0.5, y0 + np.nonzero(f[:, c])[0].max() + 1) for c in mid])
    X, Y = np.meshgrid(np.arange(x0, x1) + 0.5, np.arange(y0, y1) + 0.5)
    row = lambda h_: VP[1] - (h_ - EYE) * (VP[0] - X) / XB
    face = (X >= x0 + c0) & (X < x0 + c1) & (Y >= row(yt)) & (Y < row(yb)) & pl
    return face, ndi.binary_dilation(face, iterations=FRAME) & pl


def quantise(a, m, k=COLORS):
    """a's pixels under m in k tones of their own (median cut, no dither)."""
    sp = np.clip(a[m], 0, 255).round().astype(np.uint8)[None]
    pal = Image.fromarray(sp).quantize(colors=k, method=0, dither=0)
    out = a.copy()
    out[m] = np.asarray(Image.fromarray(sp).quantize(palette=pal, dither=Image.Dither.NONE).convert('RGB')).astype(float)[0]
    return out


def unlit_box(q, face, frame):
    """The box unlit: its frame dark old wood (the answer's grain in it); its milky face in OFF_TONE (its own
    unevenness kept); its letters and streak (darker than the face round them) dark red-brown."""
    off = q.copy(); L = lum(q)
    fr = frame & ~face
    g = L / max(L[fr].mean(), 1.0)
    off[fr] = FRAME_TONE[None, :] * np.clip(0.85 + 0.3 * (g[fr] - 1), 0.7, 1.15)[:, None]
    S = ndi.gaussian_filter(L * face, 4) / np.maximum(ndi.gaussian_filter(face.astype(float), 4), 1e-3)
    t = L / np.maximum(S, 1.0)
    ink = face & (t < INK_T) & ndi.binary_erosion(face, iterations=2); pane = face & ~ink   # (not its edge: the answer's glow there)
    off[pane] = OFF_TONE[None, :] * np.clip(0.9 + 0.35 * (t[pane] - 1), 0.75, 1.1)[:, None]
    off[ink] = q[ink] * INK_OFF
    return quantise(off, frame, 12)


def comp_from(lit, off, m, thr=3.0):
    """The lit picture where it is lighter than the unlit one (its alpha the difference, so that laid over the layer it
    gives the lit picture), under m."""
    d = lum(lit - off)
    al = np.clip((d - thr) / 18.0, 0, 1) * m
    rgb = np.where(al[..., None] > 0, np.clip((lit - off * (1 - al[..., None])) / np.maximum(al[..., None], 1e-3), 0, 255), 0)
    return np.dstack([rgb, al * 255])


def build(city):
    """The box unlit over CBOX (and where it is), and its light (RGBA over CBOX), on city as the zones before leave it."""
    x0, y0, x1, y1 = CBOX
    lit = lit_picture()
    face, frame = shapes(lit)
    q = quantise(lit, frame)
    off = unlit_box(q, face, frame)
    base = city[y0:y1, x0:x1, :3].copy()
    unl = base.copy(); unl[frame] = off[frame]
    on = unl.copy(); on[frame] = q[frame]
    ring = ndi.binary_dilation(frame, iterations=GLOW) & ~frame
    warm = ring & ((lit - unl)[..., 0] > (lit - unl)[..., 2]) & (lum(lit) > lum(unl))
    on[warm] = lit[warm]
    return unl, frame, comp_from(on, unl, frame | warm)


def street_js():
    """Its box in street.js's ASSETS.comps (its version kept)."""
    path = os.path.join(ASSETS, 'street.js')
    s = open(path, encoding='utf-8').read()
    x0, y0, x1, y1 = CBOX
    m = re.search(r', "%s": \{"src": "assets/%s\.webp\?v=(\w+)", "x": \d+, "y": \d+, "w": \d+, "h": \d+\}' % (COMP, COMP), s)
    ent = ', "%s": {"src": "assets/%s.webp?v=%s", "x": %d, "y": %d, "w": %d, "h": %d}' % (COMP, COMP, m.group(1) if m else '1', x0, y0, x1 - x0, y1 - y0)
    if m: s2 = s[:m.start()] + ent + s[m.end():]
    else:
        m2 = re.search(r', "win_z7_shop": \{[^}]*\}', s); s2 = s[:m2.end()] + ent + s[m2.end():]
    if s2 != s: open(path, 'w', encoding='utf-8').write(s2)


def save(a, p):
    Image.fromarray(np.clip(np.round(a), 0, 255).astype(np.uint8), 'RGBA' if a.shape[-1] == 4 else 'RGB').save(
        p, 'WEBP', lossless=True, quality=100, method=6, exact=True)


def draw(city, unlit, box=BOX):
    """Zone 'dagsign': the box unlit in both layers (its place only); its light written to assets/z7_dagsign.webp, its
    box in street.js. Returns what changed over box."""
    x0, y0, x1, y1 = CBOX
    unl, frame, comp = build(city)
    for a in (city, unlit):
        t = a[y0:y1, x0:x1]; t[..., :3][frame] = unl[frame]; t[..., 3][frame] = 255
    save(comp, os.path.join(ASSETS, COMP + '.webp'))
    street_js()
    full = np.zeros(city.shape[:2], bool); full[y0:y1, x0:x1] = frame
    return full[box[1]:box[3], box[0]:box[2]]


def before():
    """The zone's before crops: what tools/redraw_zones.py leaves in its box before the zones run (the painter's pixels:
    the overlapping zones' own before crops, in their order, over the layers' pixels where no zone is)."""
    sys.path.insert(0, os.path.join(ROOT, 'tools'))
    import redraw_zones as R
    x0, y0, x1, y1 = BOX
    for tag, f in (('city', 'layer_city_off.webp'), ('unlit', 'street_unlit.webp')):
        a = load(os.path.join(ASSETS, f))[y0:y1, x0:x1].copy()
        for name, cfg in R.ZONES.items():
            if name == 'dagsign': continue
            b = cfg['box']
            ox0, oy0, ox1, oy1 = max(b[0], x0), max(b[1], y0), min(b[2], x1), min(b[3], y1)
            if ox0 >= ox1 or oy0 >= oy1: continue
            z = load(os.path.join(EDITS, '%s_before_%s.webp' % (name, tag)))
            a[oy0 - y0:oy1 - y0, ox0 - x0:ox1 - x0] = z[oy0 - b[1]:oy1 - b[1], ox0 - b[0]:ox1 - b[0]]
        save(a, os.path.join(EDITS, 'dagsign_before_%s.webp' % tag))
        print('dagsign_before_%s.webp' % tag, a.shape[1], 'x', a.shape[0])


def preview(out):
    """The box unlit and lit over the layers as they stand (not written), x1 and x4."""
    os.makedirs(out, exist_ok=True)
    city = load(os.path.join(ASSETS, 'layer_city_off.webp'))
    x0, y0, x1, y1 = BOX
    city[y0:y1, x0:x1] = load(os.path.join(EDITS, 'dagsign_before_city.webp'))
    unl, frame, comp = build(city)
    a0, b0, a1, b1 = CBOX
    shut = city[b0:b1, a0:a1, :3].copy(); shut[frame] = unl[frame]
    al = comp[..., 3:] / 255; open_ = shut * (1 - al) + comp[..., :3] * al
    for tag, a in (('before', city[b0:b1, a0:a1, :3]), ('shut', shut), ('open', open_)):
        for k in (1, 4):
            Image.fromarray(np.clip(np.round(a), 0, 255).astype(np.uint8)).resize((a.shape[1] * k, a.shape[0] * k), Image.NEAREST).save(os.path.join(out, '%s_x%d.png' % (tag, k)))


def ask():
    """The image call: tools/src/edits/dagsign_in.webp and dagsign_prompt.txt; the answer saved as dagsign_model.webp."""
    import base64, io, json, urllib.request
    key = open(os.path.expanduser('~/.config/openrouter/key')).read().strip()
    buf = io.BytesIO(); Image.open(os.path.join(EDITS, 'dagsign_in.webp')).convert('RGB').save(buf, 'PNG')
    content = [{"type": "text", "text": open(os.path.join(EDITS, 'dagsign_prompt.txt')).read().strip()},
               {"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()}}]
    body = {"model": MODEL, "modalities": ["image", "text"], "usage": {"include": True}, "messages": [{"role": "user", "content": content}]}
    req = urllib.request.Request('https://openrouter.ai/api/v1/chat/completions', data=json.dumps(body).encode(),
                                 headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'})
    d = json.loads(urllib.request.urlopen(req, timeout=900).read())
    url = d['choices'][0]['message']['images'][0]['image_url']['url']
    Image.open(io.BytesIO(base64.b64decode(url.split(',', 1)[1]))).save(os.path.join(EDITS, 'dagsign_model.webp'), 'WEBP', lossless=True, quality=100, method=6)
    print('answer saved; cost', d.get('usage', {}).get('cost'), '$ (REG and COLOR to fit again on it)')


if __name__ == '__main__':
    if '--before' in sys.argv: before()
    elif '--preview' in sys.argv: preview(sys.argv[sys.argv.index('--preview') + 1])
    elif '--ask' in sys.argv: ask()
    else: print(__doc__)
