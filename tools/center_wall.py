#!/usr/bin/env python3
"""The Pokemon Center's front wall (the face along the street, from its far corner by the end house, x 870, to its near
corner on the roji, x 907): light cladding panels in the street's camera, lit by the Center's own lights.

    (a module: tools/redraw_zones.py's zone 'cwall', the last, calls draw(city, unlit, box) on the street as the zones
     before it leave it: both layers in its box, from the zone's before copies, and the lit shop's comp
     assets/win_z4_shop.webp over the wall (as tools/facade_foot.py has just written it): the same bytes each time)
    python3 tools/center_wall.py --input       once: the draft's input (tools/src/edits/cwall_in.webp: the street's layer
                                               round the Center, every comp there lit, the Poke Ball's light on the front)
    python3 tools/center_wall.py --before      once: the zone's before crops (tools/src/edits/cwall_before_*.webp)
    python3 tools/center_wall.py --ask wall    the draft asked of the image model (OpenRouter's key in
                                               ~/.config/openrouter/key; about 0.25 $), from cwall_in.webp brightened and
                                               enlarged 6 times; its prompt tools/src/edits/cwall_wall_prompt.txt, its answer
                                               cwall_wall_model.webp; the wall is drawn from the saved answer, never a new call
    python3 tools/center_wall.py --preview DIR the wall off, lit and in the power cut over the layers as they are, x1 and x6

What was there: under the red sign band, round the lit glass door and down to the dark base, one flat lavender fill
(48, 47, 94 at the top, 36, 35, 71 low down), the same at every hour and in every state: no material, no joint, no light
of the shop's on it but a few warm pixels by the door's frame and the right lamp in the lit comp.

What the camera sees (the street's camera: VP (700, 615), f 960, the eye 1.41 m; the right fronts in the plane 5 m right
of the eye's line, tools/roji_alley.py's): the Center's front is a receding face, 23.13 m deep at its near corner (x 907,
on the roji) to 28.15 m at its far one (x 870, the corner on the cross street, the end house behind it): 5.0 m of front.
Its lines run to the vanishing point: the band's lower edge on the ray v 0.635 (4.59 m up), the dark base's top on
v -0.174 (0.54 m), its foot on v -0.252 (the sidewalk, 0.15 m). The glazed door is 3 m of it (x 875..897, 27.35 to
24.30 m), the pier on its right 1.17 m (x 898..907, the right lamp on it at 2.8 m), the strip on its left 0.8 m (x 870..873,
the left lamp, the grey box on the corner before it); over the awning (its top 4.0 m at the corner) a strip of wall up to
the band, the whole front long. The roji's far wall (x 908 on) is the Center's side, face on, kept as it is: the front is
clad, the side in the alley plain plaster (a street front clad, a side wall in a roji plain, as the owner's rule allows:
"soit tout uni, soit cote et facade differents, mais identiques sur le meme pan").

What it is now (R28: the image model drew the wall in its context, tools/src/edits/cwall_wall_model.webp, from
cwall_in.webp and cwall_wall_prompt.txt: the Center's front as the games and the official stores show it, light grey-white
cladding panels with fine joints, a crisp edge under the red band, a stone base, lit by its lamps and its door in the rain):
- the panels: its layout read on the answer and put on the street's rays, each joint one crisp pixel: its courses every
  0.51 m from 0.70 m up (its lowest, a short starter course over the base, the splash zone), its vertical joints on the
  door's jambs and halfway along the door over the awning (1.5 m panels), the pier and the left strip one panel each; one
  tone a plane (R29): the painter's own light on it (his low frequencies: the sky's from above, a little darker low down),
  a little paler and greyer than his lilac (the panels' light grey-white against the plaster of the side, as the answer
  has them), a fine fixed grain within it, the joints a step darker, the corner's arris a hair lighter;
- the band's edge: the wall's first row under the band its shadow line; the awning's top a contact shade on the wall;
- the base: the painter's dark stone base, its top edge lit on its ray (R5), the starter course over it wet (darker);
- its light (the comp win_z4_shop, the Center's shop: on at every hour, dimmed in its night mode 1-6 h, out in the power
  cut, red in the red night, its stutter as it opens): the answer's light, its low frequencies on each plane over the
  answer's unlit side wall at the same height (what its lamps and its door add, in their warm colour), brought to the
  street's scale and added to the new wall, each pixel's share as the wall's own (a joint takes less): the fan of each
  lamp down its plane to the base, strongest under it, the door's frame in its shadow; the lamps' and the door's own
  pixels as they are; darker and cooler away from them, the wall over the awning the night's and the Poke Ball's;
- the layers: off (the shop's light in its comp), the power cut the same (the painter's unlit layer is his lit one there).
Needs Pillow, numpy, scipy.
"""
import base64
import io
import json
import os
import re
import sys
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDITS = os.path.join(ROOT, 'tools', 'src', 'edits')
ASSETS = os.path.join(ROOT, 'assets')
sys.path.insert(0, os.path.join(ROOT, 'tools'))
MODEL = 'openai/gpt-5.4-image-2'
GAMMA = 2.0                                      # (the draft's input brightened, its answer darkened back: z ** GAMMA)
DRAFT = (820, 440, 980, 680)                     # the draft's crop (the Center, its sign, the alley, B's corner)
SCALE = 6                                        # (a street pixel a 6 x 6 block in the draft's input)
BOX = (868, 480, 908, 670)                       # the zone (redraw_zones.py 'cwall'): the front, its far corner to its near
COMP = ('win_z4_shop', 800, 538)                 # the lit shop's comp (street.js ASSETS.comps), its place
GLOW = ('z4_emblem_glow', 876, 444)              # (the Poke Ball's light on the front, added in street.js: in the input only)
VPX, VPY, F, EYE, XF = 700.0, 615.0, 960.0, 1.41, 5.0
FRONT = (870, 907)                               # the front's columns (inclusive): its far corner, its near corner's arris
JAMBS = (874, 897)                               # the door's frame columns (the comp's, the PC's): left as they are
V_BAND, V_BASE, V_FOOT = 0.635, -0.174, -0.252   # rays: the band's lower edge, the base's top, the foot
COURSES = [0.699 + 0.5127 * k for k in range(8)]  # the answer's courses (m: its joints on the pier, rows 917, 832, 747, 660
                                                 # of the answer, through its rows' map below)
VJOINTS = [27.35, 25.83, 24.30]                  # the answer's vertical joints over the awning (m down the street: the door's
                                                 # jambs and its middle, answer columns 326, 389, 467)
# the answer's frame against the street's (R21: it came back square, squeezed down, its lower part shorter still): a
# scene column x is the answer's (x - 820 + 0.5) * SX + OX (fitted on what it kept: the ball, the awning, the door, the
# houses); a row, through anchors per plane (scene row, answer row: the band's edge, the awning, the lamp, the base)
SX, OX = 5.969, -5.19
ROWS = {'upper': [(470, 150), (487, 219), (509, 321)],     # (the lamps: their hood's top and their lens's foot)
        'pier': [(487, 219), (509, 321), (540, 490), (554, 544), (563.5, 592), (650, 947), (667, 1015)],
        'left': [(540, 470), (551, 540), (564, 590), (571.5, 626), (645, 927), (660, 990)]}
COLS = {'pier': ((898, 908), (474.0, 515.0)), 'left': ((870, 874), (302.0, 338.0))}   # (scene [a, b), answer [a, b): each
                                                 # plane from the door's frame to its corner, as the answer drew them)
SIDE_COLS = (532, 600)                           # the answer's side wall (unlit by the shop): its light at each answer row
GRAIN = 0.022                                    # (a fixed fine grain within each plane)
K = dict(joint=0.72, band=0.70, awning=0.86, arris=1.05, base_top=1.55, wet=0.90)
PANEL = dict(lift=1.10, grey=0.3)                # (the cladding's light grey-white against the plaster's lilac: the painter's
                                                 # light on the front a little paler and greyer, as the answer's panels over
                                                 # its plaster side; one value a plane)
AMB = 45.0 / 70.0                                # (the answer's night on a panel, its side wall's, to the painter's: its
                                                 # light brought to the street's scale by the same factor)
LIGHT_K = 0.8                                    # (the answer's light over its unlit side, laid at this share: under the
                                                 # right lamp a little brighter than the old comp's few lit pixels there)
LIGHT_SIG = 1.2                                  # (its low frequencies within the plane: its shape, not its joints)


def load(p, mode='RGBA'):
    return np.asarray(Image.open(p).convert(mode)).astype(float)


def save(a, p):
    Image.fromarray(np.clip(np.round(a), 0, 255).astype(np.uint8), 'RGBA' if a.shape[-1] == 4 else 'RGB').save(
        p, 'WEBP', lossless=True, quality=100, method=6, exact=True)


def lum(a):
    return a @ np.array([0.299, 0.587, 0.114])


def street_comps():
    s = open(os.path.join(ASSETS, 'street.js')).read().split('\n')[3]
    return json.loads(re.search(r'const ASSETS = (\{.*?\});', s).group(1))['comps']


# ---- the street's camera on the front
def z_of(x):
    """the depth (m) of the front at column x's middle"""
    return F * XF / (np.asarray(x, float) + 0.5 - VPX)


def row_of(x, h):
    """the row (float, the pixel's middle at .0) of height h (m) on the front at column x"""
    return VPY - (h - EYE) * F / z_of(x) - 0.5


def h_of(x, y):
    return EYE + (VPY - (np.asarray(y, float) + 0.5)) * z_of(x) / F


def col_of(z):
    return VPX + F * XF / z - 0.5


# ---- the draft
def make_input():
    """The draft's input: the street's layer over DRAFT, every comp there lit, the Poke Ball's light on the front."""
    x0, y0, x1, y1 = DRAFT
    a = load(os.path.join(ASSETS, 'layer_city_off.webp'))[y0:y1, x0:x1, :3].copy()
    def lay(src, cx, cy, add=False, wh=None):
        c = load(os.path.join(ASSETS, src))
        if wh: c = c[:wh[1], :wh[0]]                 # (an atlas: its first frame)
        h, w = c.shape[:2]
        ox0, oy0, ox1, oy1 = max(cx, x0), max(cy, y0), min(cx + w, x1), min(cy + h, y1)
        if ox1 <= ox0 or oy1 <= oy0: return
        s = c[oy0 - cy:oy1 - cy, ox0 - cx:ox1 - cx]; al = s[..., 3:] / 255.0
        d = a[oy0 - y0:oy1 - y0, ox0 - x0:ox1 - x0]
        d[:] = d + s[..., :3] * al if add else d * (1 - al) + s[..., :3] * al
    for n, c in street_comps().items():
        lay(c['src'].split('?')[0].replace('assets/', ''), c['x'], c['y'], wh=(c['w'], c['h']))
    lay(GLOW[0] + '.webp', GLOW[1], GLOW[2], add=True)
    save(np.clip(a, 0, 255), os.path.join(EDITS, 'cwall_in.webp'))
    print('cwall_in.webp', a.shape[1], 'x', a.shape[0])


def ask(name='wall'):
    """The drawing asked of the image model, from cwall_in.webp brightened and enlarged SCALE times; its prompt
    tools/src/edits/cwall_<name>_prompt.txt, its answer cwall_<name>_model.webp."""
    import urllib.request
    z = load(os.path.join(EDITS, 'cwall_in.webp'), 'RGB') / 255.0
    x0, y0, x1, y1 = DRAFT
    im = Image.fromarray((np.clip(z ** (1 / GAMMA), 0, 1) * 255).astype(np.uint8)).resize(((x1 - x0) * SCALE, (y1 - y0) * SCALE), Image.NEAREST)
    buf = io.BytesIO(); im.save(buf, 'PNG')
    key = open(os.path.expanduser('~/.config/openrouter/key')).read().strip()
    content = [{"type": "text", "text": open(os.path.join(EDITS, 'cwall_%s_prompt.txt' % name)).read().strip()},
               {"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()}}]
    body = {"model": MODEL, "modalities": ["image", "text"], "usage": {"include": True}, "messages": [{"role": "user", "content": content}]}
    req = urllib.request.Request('https://openrouter.ai/api/v1/chat/completions', data=json.dumps(body).encode(),
                                 headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'})
    d = json.loads(urllib.request.urlopen(req, timeout=900).read())
    url = d['choices'][0]['message']['images'][0]['image_url']['url']
    Image.open(io.BytesIO(base64.b64decode(url.split(',', 1)[1]))).save(os.path.join(EDITS, 'cwall_%s_model.webp' % name), 'WEBP', lossless=True, quality=100, method=6)
    print('cwall_%s_model.webp saved; cost' % name, d.get('usage', {}).get('cost'), '$')


def answer():
    """The answer darkened back to the street's light (floats, 0..255)."""
    return (load(os.path.join(EDITS, 'cwall_wall_model.webp'), 'RGB') / 255.0) ** GAMMA * 255.0


def ans_row(plane, y):
    r = ROWS[plane]
    return np.interp(np.asarray(y, float), [a for a, _ in r], [b for _, b in r])


def ans_col(plane, x):
    if plane in COLS:
        (a, b), (c, d) = COLS[plane]
        return c + (np.asarray(x, float) - a) * (d - c) / (b - a)
    return (np.asarray(x, float) - DRAFT[0]) * SX + OX


def sample(A, plane, xs, ys, ss=6):
    """the answer over each scene pixel (xs, ys: its corner): the mean of ss x ss points in it"""
    acc = np.zeros(np.shape(xs) + (3,))
    for j in range(ss):
        for i in range(ss):
            xa = ans_col(plane, xs + (i + 0.5) / ss); ya = ans_row(plane, ys + (j + 0.5) / ss)
            xi = np.clip(xa.astype(int), 0, A.shape[1] - 1); yi = np.clip(ya.astype(int), 0, A.shape[0] - 1)
            acc += A[yi, xi]
    return acc / ss / ss


def side_light(A):
    """the answer's unlit side wall: its light at each answer row (a smooth column, its joints left out)"""
    s = A[:, SIDE_COLS[0]:SIDE_COLS[1]]
    col = np.median(s, 1)
    return np.stack([gaussian_filter(col[:, c], 12) for c in range(3)], -1)


# ---- the painting's front
def classify(P, x0, y0):
    """the front's wall pixels in the crop P (RGB, at (x0, y0)), by plane: 'upper' (between the band and the awning),
    'pier', 'left'; and the base's pixels"""
    H, W = P.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W]; X = xx + x0; Y = yy + y0
    r, g, b = P[..., 0], P[..., 1], P[..., 2]
    lav = (b > 1.55 * np.maximum(r, 1)) & (b > 48) & (np.abs(r - g) < 12)   # (the lavender: not the red band, the awning,
    front = (X >= FRONT[0]) & (X <= FRONT[1])                                # the door's dark, the grey box, the lamps)
    below_band = Y > row_of(X, EYE + V_BAND * XF)
    above_base = Y < row_of(X, EYE + V_BASE * XF) - 0.5
    wall = front & lav & below_band & above_base
    upper = wall & (Y < 532)
    under = wall & (Y >= 532)
    pier = under & (X > JAMBS[1])
    left = under & (X < JAMBS[0])
    base = front & (Y >= row_of(X, EYE + V_BASE * XF) - 0.5) & (Y < row_of(X, EYE + V_FOOT * XF) - 0.5) & (lum(P) < 30)
    return dict(upper=upper, pier=pier, left=left), base, X, Y


def plane_light(P, m, sig):
    """the painter's light inside the mask m alone (a normalised gaussian: nothing from the next plane)"""
    w = gaussian_filter(m.astype(float), sig)
    return np.stack([gaussian_filter(np.where(m, P[..., c], 0.0), sig) for c in range(3)], -1) / np.maximum(w, 1e-4)[..., None]


def hashf(X, Y, k):
    v = np.sin(X * 12.9898 + Y * 78.233 + k * 37.719) * 43758.5453
    return v - np.floor(v)


def build(P, x0, y0):
    """The front redrawn in the crop P (RGB floats at (x0, y0)): the wall off (the layers) and lit (the comp), the mask
    of what is new."""
    planes, base, X, Y = classify(P, x0, y0)
    off = P.copy()
    new = np.zeros(P.shape[:2], bool)
    g = 1.0 + GRAIN * (hashf(X, Y, 1) * 2 - 1)
    for name, m in planes.items():
        L = plane_light(P, m, (5.0, 3.0) if name != 'upper' else (2.5, 5.0))   # (the painter's light: his falloff from the
        L = (L * (1 - PANEL['grey']) + lum(L)[..., None] * PANEL['grey']) * PANEL['lift']   # sky; the panels' paler grey)
        off[m] = (L * g[..., None])[m]
        new |= m
    wall = new.copy()
    # the joints, each one crisp pixel on its ray (courses) or its column (verticals over the awning)
    for h in COURSES:
        ry = np.round(row_of(X, h)).astype(int)
        jm = wall & (Y == ry) & ~planes['upper']
        off[jm] *= K['joint']
    for z in VJOINTS:
        cx = int(round(col_of(z)))
        jm = planes['upper'] & (X == cx)
        off[jm] *= K['joint']
    # the band's shadow line: the wall's first row under the band; the awning's contact on the wall over it
    first = wall & ~np.roll(wall, 1, 0)
    off[first & planes['upper']] *= K['band']
    last_up = planes['upper'] & ~np.roll(planes['upper'], -1, 0)
    off[last_up] *= K['awning']
    # the near corner's arris
    ar = wall & (X == FRONT[1]) & ~planes['upper']
    off[ar] *= K['arris']
    # the starter course (from the base's top to the first course): wet
    wet = wall & (Y > row_of(X, COURSES[0]) + 0.5)
    off[wet] *= K['wet']
    # the base's top edge lit, one pixel on its ray
    bt = base & (Y == np.round(row_of(X, EYE + V_BASE * XF) - 0.5 + 0.5).astype(int))
    off[bt] = P[bt] * K['base_top']
    new |= bt
    # the light: the answer's on each plane over its unlit side at the same answer row (what its lamps and door add, in
    # their warm colour), brought to the street's scale, its low frequencies within the plane; added to the wall, each
    # pixel's share as the wall's own (a joint takes less)
    A = answer(); S = side_light(A)
    add = np.zeros(P.shape)
    for name in ('pier', 'left'):
        m = planes[name]
        ys, xs = np.nonzero(m)
        if not len(ys): continue
        a = sample(A, name, xs + x0, ys + y0)
        ar_ = ans_row(name, ys + y0 + 0.5).astype(int)
        ref = S[np.clip(ar_, 0, len(S) - 1)]
        add[ys, xs] = np.clip(a - ref, 0, None) * AMB * LIGHT_K
        sm = plane_light(add, m, LIGHT_SIG)
        add[m] = sm[m]
    flat = np.ones(P.shape)
    for name, m in planes.items():
        if m.any():
            Lp = plane_light(off, m, (5.0, 3.0))
            flat[m] = (off / np.maximum(Lp, 1.0))[m]
    lit = off.copy()
    lit[wall] = (off + add * flat)[wall]
    return off, lit, new, wall, planes, add


def before():
    """The zone's before crops: the layers' pixels in its box before the zones run (the overlapping zones' own before
    crops, in their order, over the layers' pixels where no zone is)."""
    import redraw_zones as R
    x0, y0, x1, y1 = BOX
    for tag, f in (('city', 'layer_city_off.webp'), ('unlit', 'street_unlit.webp')):
        a = load(os.path.join(ASSETS, f))[y0:y1, x0:x1].copy()
        for name, cfg in R.ZONES.items():
            if name == 'cwall': continue
            b = cfg['box']
            ox0, oy0, ox1, oy1 = max(b[0], x0), max(b[1], y0), min(b[2], x1), min(b[3], y1)
            if ox0 >= ox1 or oy0 >= oy1: continue
            z = load(os.path.join(EDITS, '%s_before_%s.webp' % (name, tag)))
            a[oy0 - y0:oy1 - y0, ox0 - x0:ox1 - x0] = z[oy0 - b[1]:oy1 - b[1], ox0 - b[0]:ox1 - b[0]]
        save(a, os.path.join(EDITS, 'cwall_before_%s.webp' % tag))
        print('cwall_before_%s.webp' % tag, a.shape[1], 'x', a.shape[0])


def comp_with(lit, wall, x0, y0, comp=None, carry=None):
    """The shop's comp with the lit wall: over the wall's pixels in its box, the wall lit by the shop, opaque; and where it
    lays its light over what else changed (carry: the mask, the old and the new crop: the base's lit top), its pixels
    times the change's luminance there (R19, as tools/facade_foot.py carries the feet)."""
    n, cx, cy = COMP
    C = load(os.path.join(ASSETS, n + '.webp')).copy() if comp is None else comp.copy()
    h, w = C.shape[:2]
    for yy, xx in zip(*np.nonzero(wall)):
        X, Y = xx + x0, yy + y0
        if cx <= X < cx + w and cy <= Y < cy + h:
            C[Y - cy, X - cx, :3] = lit[yy, xx]; C[Y - cy, X - cx, 3] = 255
    if carry is not None:
        m, old, new = carry
        r = (lum(new) + 1.0) / (lum(old) + 1.0)
        for yy, xx in zip(*np.nonzero(m & ~wall)):
            X, Y = xx + x0, yy + y0
            if cx <= X < cx + w and cy <= Y < cy + h and C[Y - cy, X - cx, 3] > 0:
                C[Y - cy, X - cx, :3] = np.clip(C[Y - cy, X - cx, :3] * r[yy, xx], 0, 255)
    return C


def draw(city, unlit, box=BOX):
    """Zone 'cwall': both layers in place (the wall off: the painter's unlit layer is his lit one on this front), the
    shop's comp over the wall lit; returns what changed in the layers."""
    x0, y0, x1, y1 = box
    ch = np.zeros(city.shape[:2], bool)
    P = city[y0:y1, x0:x1, :3].copy()
    off, lit, new, wall, _, _ = build(P, x0, y0)
    for a in (city, unlit):
        sub = a[y0:y1, x0:x1]; old = sub[..., :3].copy()
        ratio = (sub[..., :3] + 1.0) / (P + 1.0)                 # (the unlit layer's own darkening, if it had any)
        sub[..., :3] = np.where(new[..., None], np.round(np.clip(off * ratio, 0, 255)), old)
        ch[y0:y1, x0:x1] |= np.abs(sub[..., :3] - old).max(-1) > 0
    save(comp_with(np.round(np.clip(lit, 0, 255)), wall, x0, y0, carry=(new, P, off)), os.path.join(ASSETS, COMP[0] + '.webp'))
    return ch


def preview(out):
    """The front off, lit and in the power cut over the layers as they are (before and after), x1 and x6."""
    os.makedirs(out, exist_ok=True)
    x0, y0, x1, y1 = BOX
    b = load(os.path.join(ASSETS, 'layer_city_off.webp'))[y0:y1, x0:x1, :3]   # (the layer as the zones before this one leave it)
    off, lit, new, wall, planes, gain = build(b, x0, y0)
    C = load(os.path.join(ASSETS, COMP[0] + '.webp'))
    n, cx, cy = COMP
    def with_comp(base, comp):
        o = base.copy()
        for yy in range(y1 - y0):
            for xx in range(x1 - x0):
                X, Y = xx + x0, yy + y0
                if cx <= X < cx + comp.shape[1] and cy <= Y < cy + comp.shape[0]:
                    a = comp[Y - cy, X - cx, 3] / 255.0
                    o[yy, xx] = o[yy, xx] * (1 - a) + comp[Y - cy, X - cx, :3] * a
        return o
    old_lit = with_comp(b, C)
    new_lit = with_comp(off, comp_with(lit, wall, x0, y0, C, carry=(new, b, off)))
    tiles = [b, off, old_lit, new_lit]
    for s in (1, 6):
        row = np.concatenate([np.concatenate([t, np.full((t.shape[0], 2, 3), 255.0)], 1) for t in tiles], 1)
        Image.fromarray(np.clip(np.round(row), 0, 255).astype(np.uint8)).resize((row.shape[1] * s, row.shape[0] * s), Image.NEAREST).save(os.path.join(out, 'cwall_x%d.png' % s))
    g = lum(gain)
    print('wall', int(wall.sum()), 'px; planes', {k: int(v.sum()) for k, v in planes.items()}, '; gain max', round(float(g.max()), 2))


if __name__ == '__main__':
    if '--input' in sys.argv: make_input()
    elif '--before' in sys.argv: before()
    elif '--ask' in sys.argv: ask(sys.argv[sys.argv.index('--ask') + 1])
    elif '--preview' in sys.argv: preview(sys.argv[sys.argv.index('--preview') + 1])
    else: print(__doc__)
