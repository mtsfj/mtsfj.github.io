#!/usr/bin/env python3
"""The dagashi-ya's sign over its window (the owner: "Maj panneau dagashi, je pense aplat moche actuellement"; after rounds
of options, "A, caisson laiteux"; then, of that box pixelated from a drawing: "Bizarre, pas précis, quali"): an old lit
sign box on the shop's dark fascia, placed pixel by pixel on the layer's own grid, as crisp as the street's other signs
(Ichiraku's 一楽ラーメン, the oden's おでん box and lantern, the old だがし it replaces).

    (a module: tools/redraw_zones.py's zone 'dagsign', the last, calls draw() on the street as the zones before it leave
    it: the box unlit in the layers; and it writes its light, assets/z7_dagsign.webp, which assets/street.js lays on it
    on the shop's hours: the same bytes each time)
    python3 tools/dagashi_sign.py --before         once: the zone's before crops (tools/src/edits/dagsign_before_*.webp)
    python3 tools/dagashi_sign.py --preview DIR    the box unlit and lit over the layers as they are, x1 and x6
    python3 tools/dagashi_sign.py --ask            the drawing asked again (OpenRouter's key in ~/.config/openrouter/key)

Its design is the drawing the owner chose (the image model in the street's context, R28: tools/src/edits/dagsign_in.webp,
_prompt.txt, _model.webp): a long box, its milky face lit warm from inside and a little uneven, a worn wooden frame, a
rain streak, だがし in red-brown. Its tones are taken from that drawing (its lit face's tones at TONE_Q, a little milkier,
MILK; its letters' colour), everything else is placed here on the street's pixels (the owner: "pas précis"; brought down
from the drawing, its letters were soft blobs and its light a smear):

- the fascia it hangs on, found in the street's camera (FASCIA: from the post to its right end, from the window's head
  at 2.44 m to its top at 3.07 m, the painter's own edges, on their rays to VP); the box (SIZE: 2.41 x 0.32 m) centred on
  it in depth and height (the owner, of the larger box: "un poil mieux centré"), its margins equal in metres (0.25 m at
  each end), an even band of dark wood above and below; its face in true perspective, 4 cm proud of the front (XB), its
  top and bottom on the rays, its ends plumb, each pixel in or out by its centre, no partial pixel;
- the junction of the front's two materials over it (the owner: "faire une liaison propre entre les deux matériaux de la
  façade"; junction()): the fascia's top one clean edge on its ray from the post to its right end, a drip cap along it (its
  top catching the sky as the bay's sill does, its front in shade, a pixel each), the clapboards' ends sitting on it;
  under it the painter's fascia back where the face's boards had run down over it in steps (where he had let them bite
  into its top right, his fascia from a few rows lower); in both layers and in the low-sun mask (the cap's top lit as the
  face, the fascia and the box not);
- its face in four tone steps (the tubes behind it: brighter in the middle, darker to its ends and edges), a yellowed
  patch at its right end, the painting's grain in it (a pixel's tone a step off now and then, a level or two of noise:
  a fixed hash of its place, the same bytes each run), a 1-px rain streak under its top;
- だがし from a font rendered without antialias at its own pixel size (FONT; LETTERS: their places along the face), each
  letter upright on the face's middle line at its centre (sheared column by column the strokes broke up; the painter's
  own letters stood upright too), its vertical strokes made 2 px (BOLD), fixed by hand where a stroke closes up (FIX);
- its frame FRAME px of dark old wood, a 1-px catch of the sky on its top, one corner chipped;
- unlit (the layers: the shop shut, the power cut): its milky face in the dusk's grey (OFF: four steps), its letters
  dark red-brown, legible; lit (the comp): the face's warm tones, the letters' red-brown, the frame's inner edge caught
  by the light, and its spill on the fascia, the band below and the boards round it in two short steps (GLOW: a ring
  each, the street's own light spills, no halo), its alpha the difference (as tools/soda_corner.py's comp_from).

street.js: a 'sign' on the shop's hours (NSCHED 'dagashi'), breathing a little (lightLife), out in the power cut and red
in the red night as every comp; its box in ASSETS.comps kept here (its version kept). Its light does not reach the wet
sidewalk 3 m below in any measurable way: no ground light. Needs Pillow, numpy, scipy.
"""
import os
import re
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDITS = os.path.join(ROOT, 'tools', 'src', 'edits')
ASSETS = os.path.join(ROOT, 'assets')
MODEL = 'openai/gpt-5.4-image-2'
GAMMA = 2.0
REG = (0, 300, 1.995, 1.0, -2.5)               # (the drawing on the street: street origin, its pixels a street pixel, shift)
COLOR = ((1.09, -1.0), (0.92, 0.9), (1.02, 0.8))   # (from the 22 h render's colours to the base layer's: gain, offset)
BOX = (138, 470, 227, 541)                     # the zone (redraw_zones.py 'dagsign'): the fascia, its trim on top
CBOX = (134, 470, 231, 544)                    # its light's box (street.js ASSETS.comps.z7_dagsign)
VP, EYE = (700.0, 615.0), 1.5                  # (the street's camera: F 1400)
XB, XH = 6.29, 6.33                            # (the box's face, 4 cm proud of the house's front; the front; m left of the eye)
FASCIA = (140, 227, 2.44, 3.07)                # (the shop's dark fascia on the house's front: from its left post to its
                                               #  right end, columns; its bottom, the window's head, and its top, m: the
                                               #  painter's own edges, on their rays)
SIZE = (2.41, 0.32)                            # (the box's face: its length along the street and its height, m)
TRIM_LIT, TRIM_DARK = (146.0, 70.0, 84.0), (44.0, 22.0, 30.0)   # (the drip cap on the fascia's top: its top catching the
                                               #  sky as the bay's sill does, its front in shade; 1 px each)
TONE_FACE = (153, 219, 2.5965, 2.8526)         # (the drawing's own lit face, where its tones are read)
FRAME = 2                                      # (its frame round the face, px)
TONE_Q, MILK = (30, 55, 78, 94), (0.3, (255.0, 236.0, 200.0))   # (the face's four tones: the drawing's lit face at these
                                               #  centiles, mixed so much toward a milky cream)
STEPS = (0.5, 0.7, 0.86)                       # (the light over the face, 0..1, where it steps from one tone to the next)
OFF = ((50.0, 53.0, 71.0), (55.0, 58.0, 76.0), (60.0, 63.0, 81.0), (65.0, 68.0, 86.0))   # (its face unlit: four greys)
INK_OFF = (44.0, 25.0, 29.0)                   # (its letters unlit)
WOOD, SKY, CHIP = (44.0, 30.0, 28.0), (92.0, 68.0, 68.0), (78.0, 58.0, 50.0)   # (the frame, its top's catch of the sky,
                                               #  the bare wood at its chipped corner)
EDGE_LIT = 0.55                                # (the frame's inner edge lit: so far toward the face's second tone)
GLOW = (0.3, 0.12)                             # (its spill round the frame: two rings, so far toward the face's third tone)
LETTERS = ('だがし', (0.24, 0.5, 0.76))         # (its word, its letters' centres along the face)
FONT = ('/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf', 20)   # (a gothic rendered without antialias at 20 px:
                                               #  17 rows of it here)
BOLD = 1                                       # (vertical strokes widened by so many px)
FIX = []                                       # (hand fixes on the letters: (x, y, on) in street pixels)
COMP = 'z7_dagsign'


def load(p, mode='RGBA'):
    return np.asarray(Image.open(p).convert(mode)).astype(float)


def lum(a):
    return a @ [0.299, 0.587, 0.114]


def depth(x, plane=XH):
    """How far along the street (m) column x is on a plane so far left of the eye."""
    return 1400.0 * plane / (VP[0] - x)


def centred():
    """The box's face (its columns, its bottom and top) centred on the fascia in the street's depth and height: its
    margins equal in metres, not in pixels; under the trim's dark row (1 px), over the window's head."""
    z0, z1 = depth(FASCIA[0]), depth(FASCIA[1]); zc = (z0 + z1) / 2
    zl, zr = zc - SIZE[0] / 2, zc + SIZE[0] / 2
    top = FASCIA[3] - XH / (VP[0] - (FASCIA[0] + FASCIA[1]) / 2)        # (under the trim's dark row: a pixel's height)
    yc = (FASCIA[2] + top) / 2
    return (VP[0] - 1400.0 * XB / zl, VP[0] - 1400.0 * XB / zr, yc - SIZE[1] / 2, yc + SIZE[1] / 2)


FACE = centred()


def row(h, x, plane=XB):
    """The row a height h (m) on a plane (the box's face) projects to at column x."""
    return VP[1] - (h - EYE) * (VP[0] - x) / plane


def grid(box=CBOX):
    x0, y0, x1, y1 = box
    return np.meshgrid(np.arange(x0, x1) + 0.5, np.arange(y0, y1) + 0.5)


def hashf(X, Y, k):
    """A fixed pseudo-random 0..1 per pixel (integer arithmetic: the same bytes everywhere)."""
    xi = X.astype(np.int64); yi = Y.astype(np.int64)
    v = (xi * 73856093) ^ (yi * 19349663) ^ (k * 83492791)
    return (v % 1000003) / 1000003.0


def geometry(face_=None):
    """Over CBOX: the face (by pixel centres), its frame, where along the face (u 0..1) and up it (v 0..1) each pixel is."""
    X, Y = grid()
    fx0, fx1, hb, ht = face_ or FACE
    yt, yb = row(ht, X), row(hb, X)
    face = (X >= fx0) & (X < fx1) & (Y >= yt) & (Y < yb)
    outer = (X >= fx0 - FRAME) & (X < fx1 + FRAME) & (Y >= yt - FRAME) & (Y < yb + FRAME)
    u = (X - fx0) / (fx1 - fx0); v = (yb - Y) / (yb - yt)
    return face, outer & ~face, u, v


def tones():
    """The face's four lit tones and its letters' colour, from the drawing's lit face (a little milkier)."""
    x0, y0, x1, y1 = CBOX
    a = load(os.path.join(EDITS, 'dagsign_model.webp'), 'RGB')
    lin = (np.clip(a / 255.0, 0, 1) ** GAMMA) * 255
    ox, oy, s, dx, dy = REG
    X, Y = grid()
    xi = np.clip(np.floor((X - ox) * s + dx).astype(int), 0, lin.shape[1] - 1); yi = np.clip(np.floor((Y - oy) * s + dy).astype(int), 0, lin.shape[0] - 1)
    px = lin[yi, xi]
    for c, (g, of) in enumerate(COLOR): px[..., c] = px[..., c] * g + of
    face, _, _, _ = geometry(TONE_FACE)
    L = lum(px)
    k, cream = MILK
    T = []
    for q in TONE_Q:
        v = np.percentile(L[face], q); sel = face & (np.abs(L - v) < 6)
        T.append(np.clip(px[sel].mean(0) * (1 - k) + np.array(cream) * k, 0, 255))
    ink = px[face & (L < np.percentile(L[face], 12))].mean(0)
    return np.array(T), ink


def letters():
    """だがし over CBOX: each letter rendered without antialias (FONT), its vertical strokes widened (BOLD), upright on the
    face's middle line at its centre."""
    X, Y = grid(); x0, y0 = CBOX[:2]
    fx0, fx1, hb, ht = FACE
    m = np.zeros(X.shape, bool)
    word, at = LETTERS
    F_ = ImageFont.truetype(*FONT)
    for ch, uc in zip(word, at):
        xc = fx0 + uc * (fx1 - fx0)
        im = Image.new('L', (FONT[1] * 3, FONT[1] * 3), 0); d = ImageDraw.Draw(im); d.fontmode = '1'
        d.text((FONT[1], FONT[1]), ch, font=F_, fill=255)
        g = np.asarray(im) > 127
        ys, xs = np.nonzero(g); g = g[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        if BOLD: g = g | np.pad(g, ((0, 0), (BOLD, 0)))[:, :g.shape[1]]
        h, w = g.shape
        left = int(round(xc - w / 2)); top = int(round((row(ht, xc) + row(hb, xc)) / 2 - h / 2))
        m[top - y0:top - y0 + h, left - x0:left - x0 + w] |= g        # (upright, on the face's middle line at its centre)
    for x, y, on in FIX: m[y - y0, x - x0] = bool(on)
    return m


def paint():
    """The box over CBOX, lit and unlit (RGB), its pixels (face and frame), the frame's inner edge, its glow's rings."""
    X, Y = grid()
    face, frame, u, v = geometry()
    T, ink = tones()
    # the light over the face: brighter in the middle, darker to its ends and edges; four steps
    b = 1 - 0.55 * np.abs(2 * u - 1) ** 3 - 0.4 * np.abs(2 * v - 1) ** 2
    t = np.digitize(b, STEPS)
    t = np.where((u > 0.84) & (v < 0.6), t - 1, t)                    # (a yellowed patch at its right end)
    hz = hashf(X, Y, 1)
    t = np.where(hz < 0.09, t - 1, np.where(hz > 0.965, t + 1, t))     # (the painting's grain: a step off now and then)
    fx0, fx1, hb, ht = FACE
    xs_ = int(fx0 + 0.69 * (fx1 - fx0)) + 0.5
    streak = (np.abs(X - xs_) < 0.5) & (Y >= row(ht, X)) & (Y < row(ht, X) + 5)
    t = np.where(streak, t - 1, t)
    t = np.clip(t, 0, 3)
    n = (hashf(X, Y, 2) - 0.5) * 4                                       # (a level or two of noise)
    lit = T[t] + n[..., None]; off = np.array(OFF)[t] + n[..., None]
    lm = letters() & face
    lit[lm] = ink; off[lm] = INK_OFF
    # the frame: dark old wood, its top's catch of the sky, a chipped corner; lit, its inner edge caught
    fr = frame
    top = fr & ~np.roll(fr, 1, 0) & (Y < row(ht, X))
    lit[fr] = WOOD; off[fr] = WOOD
    lit[top] = SKY; off[top] = SKY
    chip_x, chip_y = fx0 - FRAME, None
    cb = fr & (X < fx0 - FRAME + 2) & (Y >= row(hb, X) + FRAME - 2)  # (its bottom left corner chipped: 2 x 2)
    inner = fr & ndi.binary_dilation(face, structure=np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]]))
    lit[inner] = WOOD + (T[1] - WOOD) * EDGE_LIT
    lit = np.clip(lit, 0, 255); off = np.clip(off, 0, 255)
    rings = []
    k8 = np.ones((3, 3), bool); prev = face | fr
    for _ in GLOW:
        r = ndi.binary_dilation(prev, structure=k8) & ~prev; rings.append(r); prev = prev | r
    return lit, off, face | (fr & ~cb), cb, rings, T


def build(city):
    """The box unlit over CBOX (and where it is), and its light (RGBA over CBOX), on city as the zones before leave it."""
    x0, y0, x1, y1 = CBOX
    lit, off, m, cb, rings, T = paint()
    base = city[y0:y1, x0:x1, :3].copy()
    unl = base.copy(); unl[m] = off[m]
    unl[cb & (grid()[0] < FACE[0] - FRAME + 1)] = np.array(CHIP)            # (the bare wood showing at the chip)
    on = unl.copy(); on[m] = lit[m]
    for r, k in zip(rings, GLOW):
        on[r] = base[r] + (T[2] - base[r]) * k
    return unl, m | cb, comp_from(on, unl, m | cb | np.any(rings, 0))


def comp_from(lit, off, m, thr=1.0):
    """The lit picture where it is lighter than the unlit one (its alpha the difference, so that laid over the layer it
    gives the lit picture), under m."""
    d = lum(lit - off)
    al = np.clip((d - thr) / 12.0, 0, 1) * m
    rgb = np.where(al[..., None] > 0, np.clip((lit - off * (1 - al[..., None])) / np.maximum(al[..., None], 1e-3), 0, 255), 0)
    return np.dstack([rgb, al * 255])


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


OLD_EDGE = ((138, 484), (160, 489), (182, 494), (226, 500))   # (where the face's boards stopped: soda_corner.FACE_SIGN)


def junction(city, unlit):
    """The fascia's top on its ray (FASCIA's top, on the house's plane), from the post to its right end: a drip cap along
    it, its top catching the sky (TRIM_LIT) over its front in shade (TRIM_DARK), a pixel each; under it the painter's
    fascia back where the face's boards had run down over it (his pixels from the zone's before crops; where he had let
    the boards bite into its top right, his fascia from a few rows lower); over it the face as the zones before leave it,
    the clapboards' ends on the cap. Both layers. Returns over BOX: what it laid, the cap's lit row, what is dark wood."""
    x0, y0, x1, y1 = BOX
    X, Y = grid(BOX)
    yl = row(FASCIA[3], X, XH)
    cols = (X >= FASCIA[0]) & (X < FASCIA[1])
    lit = cols & (Y >= yl - 1) & (Y < yl)
    dark = cols & (Y >= yl) & (Y < yl + 1)
    under = cols & (Y >= yl + 1) & (Y < np.interp(X, [q[0] for q in OLD_EDGE], [q[1] for q in OLD_EDGE]) + 2)
    for a, tag in ((city, 'city'), (unlit, 'unlit')):
        b = load(os.path.join(EDITS, 'dagsign_before_%s.webp' % tag))[..., :3]
        low = np.roll(b, -6, 0)                                         # (his fascia six rows lower)
        src = np.where((lum(b) > 25)[..., None], low, b)
        t = a[y0:y1, x0:x1]
        t[..., :3][under] = src[under]; t[..., :3][lit] = TRIM_LIT; t[..., :3][dark] = TRIM_DARK
        t[..., 3][lit | dark | under] = 255
    return lit | dark | under, lit, dark | under


def draw(city, unlit, box=BOX):
    """Zone 'dagsign': the fascia's trim (junction) and the box unlit in both layers; its light written to
    assets/z7_dagsign.webp, its box in street.js; the low-sun marks there (the cap's top and the face lit as the face, the
    fascia and the box not). Returns what changed over box."""
    laid, lit_row, wood = junction(city, unlit)
    x0, y0, x1, y1 = CBOX
    unl, m, comp = build(city)
    for a in (city, unlit):
        t = a[y0:y1, x0:x1]; t[..., :3][m] = unl[m]; t[..., 3][m] = 255
    save(comp, os.path.join(ASSETS, COMP + '.webp'))
    street_js()
    full = np.zeros(city.shape[:2], bool); full[y0:y1, x0:x1] = m
    sp = os.path.join(ASSETS, 'street_sun.webp')
    sun = np.asarray(Image.open(sp).convert('RGB')).copy()
    t = sun[box[1]:box[3], box[0]:box[2]]
    t[lit_row] = 255; t[wood | full[box[1]:box[3], box[0]:box[2]]] = 0
    Image.fromarray(sun, 'RGB').save(sp, 'WEBP', lossless=True, quality=100, method=6, exact=True)
    return full[box[1]:box[3], box[0]:box[2]] | laid


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
    """The trim and the box, unlit and lit, over the layers as they stand (not written: the box as they have it may
    show round the new one), x1 and x6."""
    os.makedirs(out, exist_ok=True)
    city = load(os.path.join(ASSETS, 'layer_city_off.webp')); unlit = load(os.path.join(ASSETS, 'street_unlit.webp'))
    a0, b0, a1, b1 = CBOX
    keep = city[b0:b1, a0:a1, :3].copy()
    junction(city, unlit)
    unl, m, comp = build(city)
    al = comp[..., 3:] / 255; open_ = unl * (1 - al) + comp[..., :3] * al
    for tag, a in (('before', keep), ('shut', unl), ('open', open_)):
        for k in (1, 6):
            Image.fromarray(np.clip(np.round(a), 0, 255).astype(np.uint8)).resize((a.shape[1] * k, a.shape[0] * k), Image.NEAREST).save(os.path.join(out, '%s_x%d.png' % (tag, k)))


def ask():
    """The drawing asked again: tools/src/edits/dagsign_in.webp and dagsign_prompt.txt; saved as dagsign_model.webp."""
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
    print('drawing saved; cost', d.get('usage', {}).get('cost'), '$ (REG and COLOR to fit again on it)')


if __name__ == '__main__':
    if '--before' in sys.argv: before()
    elif '--preview' in sys.argv: preview(sys.argv[sys.argv.index('--preview') + 1])
    elif '--ask' in sys.argv: ask()
    else: print(__doc__)
