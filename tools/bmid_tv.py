#!/usr/bin/env python3
"""The middle storey's window of the narrow plastered building right of the cherry (zone5's B, tools/window_depth.py's
B_LOW: under Red's old balcony door, behind the second, small balcony), lived in: at every hour it was two flat violet
slabs of night, never lit. Someone watches television there in the evening and late at night.

    (a module: tools/redraw_zones.py's zone 'bmid', the last, calls draw() on the street as the zones before it leave
    it: the layers stay as they are; it writes the window's light, assets/win_b_mid.webp, and its box in street.js)
    python3 tools/bmid_tv.py --input          once: the drawing's input (tools/src/edits/bmid_in.webp: the street's layer
                                              round the window as the zones leave it, the floor above lit)
    python3 tools/bmid_tv.py --before         once: the zone's before crops (tools/src/edits/bmid_before_*.webp)
    python3 tools/bmid_tv.py --ask room       the drawing asked of the image model (OpenRouter's key in
                                              ~/.config/openrouter/key; about 0.25 $), from bmid_in.webp brightened and
                                              enlarged 8 times; its prompt tools/src/edits/bmid_room_prompt.txt, its answer
                                              bmid_room_model.webp; the window is drawn from the saved answer, never from a
                                              new call
    python3 tools/bmid_tv.py --preview DIR    the window off and lit over the layer as it is, x1 and x6
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
GAMMA = 2.0                                    # (the draft's input brightened, its answer darkened back: z ** (1 / GAMMA))
DRAFT = (926, 364, 1054, 492)                  # the draft's crop (B's middle window, its balcony, the pole on the right)
SCALE = 8                                      # (each street pixel an 8 x 8 block in the draft)
ABOVE = ('win_z1_top', 963, 222)               # (the floor above lit in the draft's input, as at 22 h)
COMP = 'win_b_mid'
BOX = (960, 366, 1008, 490)                    # the zone (redraw_zones.py 'bmid') and the comp's frame: the far jamb, the
                                               #  head's underside, the frame, the glass, the balcony's rail before it
# the answer on the street: it came back at the input's size, a hair smaller (the image model's own framing), fitted on
# the walls and the pole round the window (answer pixels a street pixel, x and y; the answer's offset): a point (X, Y)
# of the street is the answer's (X - DRAFT x0) * sx + ox, (Y - DRAFT y0) * sy + oy
REG = (7.86, 7.81, -3.25, -4.75)
# the glass, on the painting (tools/window_depth.py's model of B_LOW: the rays' first hit on a sash's glass, over half
# the pixel, the railing's bars before it left out) and in the answer: each pane's columns [a, b) and the answer's; along
# each column its top and bottom as rays from the vanishing point (v = (615 - y) / (x - 700): the head and the sill run
# along them). The answer drew the same window with a thinner head: its glass's top a ray higher (V_ANS), its bottom the
# painting's. Each pane of the answer laid in the painting's: across, a linear map of its columns; along, of its rays.
PANES = {'glassL0': dict(cols=(973, 988), ans=(972.5, 987.0), v=(0.4687, 0.7636)),
         'glassL1': dict(cols=(989, 1004), ans=(989.8, 1004.0), v=(0.4718, 0.7687))}
V_ANS_TOP = 0.773                              # (the answer's glass top, both panes: its head's ray)
GAIN = 0.85                                    # (the answer's room brought to a television's light in the street)
NPAL = 22                                      # (its tones: a median cut of its glass)
REFL_K = 0.14                                  # (the night's reflection kept on the lit glass)
REFL_MAX = 0.55                                # (and on its darkest: the glass there mostly the night)
DARK = 1.7                                     # (the answer darkened back: z ** DARK)
SS = 8                                         # (points a pixel each way, sampling the answer)
FACE_K = dict(jamb=0.45, soffit=0.25, frame=0.6, slab=0.35)   # (the screen's light round the glass)


def load(p, mode='RGBA'):
    return np.asarray(Image.open(p).convert(mode)).astype(float)


def lum(a):
    return a @ np.array([0.299, 0.587, 0.114])


def save(a, p):
    Image.fromarray(np.clip(np.round(a), 0, 255).astype(np.uint8), 'RGBA' if a.shape[-1] == 4 else 'RGB').save(
        p, 'WEBP', lossless=True, quality=100, method=6, exact=True)


def make_input():
    """The draft's input: the street's layer over DRAFT (the zones done), the floor above lit (its comp laid on it)."""
    x0, y0, x1, y1 = DRAFT
    a = load(os.path.join(ASSETS, 'layer_city_off.webp'))[y0:y1, x0:x1, :3]
    n, cx, cy = ABOVE
    c = load(os.path.join(ASSETS, n + '.webp'))
    h, w = c.shape[:2]
    oy0, ox0 = max(cy - y0, 0), max(cx - x0, 0)
    oy1, ox1 = min(cy + h, y1) - y0, min(cx + w, x1) - x0
    if oy1 > oy0 and ox1 > ox0:
        s = c[oy0 + y0 - cy:oy1 + y0 - cy, ox0 + x0 - cx:ox1 + x0 - cx]
        al = s[..., 3:] / 255.0
        a[oy0:oy1, ox0:ox1] = a[oy0:oy1, ox0:ox1] * (1 - al) + s[..., :3] * al
    save(a, os.path.join(EDITS, 'bmid_in.webp'))
    print('bmid_in.webp', a.shape[1], 'x', a.shape[0])


def ask(name):
    """The drawing asked of the image model: 'room' from bmid_in.webp (brightened, scaled)."""
    import urllib.request
    z = load(os.path.join(EDITS, 'bmid_in.webp'), 'RGB') / 255.0
    x0, y0, x1, y1 = DRAFT
    im = Image.fromarray((np.clip(z ** (1 / GAMMA), 0, 1) * 255).astype(np.uint8)).resize(((x1 - x0) * SCALE, (y1 - y0) * SCALE), Image.NEAREST)
    buf = io.BytesIO(); im.save(buf, 'PNG')
    key = open(os.path.expanduser('~/.config/openrouter/key')).read().strip()
    content = [{"type": "text", "text": open(os.path.join(EDITS, 'bmid_%s_prompt.txt' % name)).read().strip()},
               {"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()}}]
    body = {"model": MODEL, "modalities": ["image", "text"], "usage": {"include": True}, "messages": [{"role": "user", "content": content}]}
    req = urllib.request.Request('https://openrouter.ai/api/v1/chat/completions', data=json.dumps(body).encode(),
                                 headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'})
    d = json.loads(urllib.request.urlopen(req, timeout=900).read())
    url = d['choices'][0]['message']['images'][0]['image_url']['url']
    Image.open(io.BytesIO(base64.b64decode(url.split(',', 1)[1]))).save(os.path.join(EDITS, 'bmid_%s_model.webp' % name), 'WEBP', lossless=True, quality=100, method=6)
    print('bmid_%s_model.webp saved; cost' % name, d.get('usage', {}).get('cost'), '$')


def answer():
    """The answer darkened back to the street's light (floats, 0..255)."""
    a = load(os.path.join(EDITS, 'bmid_room_model.webp'), 'RGB') / 255.0
    return (a ** DARK) * 255.0


def model():
    """tools/window_depth.py's model of B's windows over BOX: each pixel's rays' first hits (their names, faces, points)
    and the low window's opening."""
    import window_depth as WD
    S, G, ops = WD.model('B')
    dx, dy = WD.rays(BOX)
    idx, t, face = S.cast(dx, dy)
    t = np.where(idx >= 0, t, 1.0)
    P = np.stack([dx * t, dy * t, t], -1)
    names = np.array(S.name + ['none'], dtype=object)[idx]
    bx = np.array(S.b + [(0, 0, 0, 0, 0, 0)], float)[idx]
    return names, face, P, bx, ops[1], t


def glass(city):
    """The painting's glass over BOX, by pane (bool): the rays' first hit on that sash's glass over half the pixel, a
    pixel the railing covers in part and painted dark (a bar) left out."""
    names, *_ = model()
    x0, y0, x1, y1 = BOX
    L = lum(city[y0:y1, x0:x1, :3])
    rail = np.isin(names, ['rail', 'rail_hand']).mean(2)
    return {k: ((names == k).mean(2) > 0.5) & ~((rail > 0.2) & (L < 12.0)) for k in PANES}


def lay(ans, panes):
    """The answer's room in the painting's panes: each pixel the mean of SS x SS points, each point mapped into the
    answer's pane (across: its columns; along: its rays, the painting's glass top to the answer's) and on the answer
    (REG), read there (bilinear). Over BOX, zero outside the glass."""
    from scipy.ndimage import map_coordinates
    x0, y0, x1, y1 = BOX
    out = np.zeros((y1 - y0, x1 - x0, 3))
    sx, sy, ox, oy = REG
    o = (np.arange(SS) + 0.5) / SS
    for k, p in PANES.items():
        ys, xs = np.nonzero(panes[k])
        if not len(ys): continue
        X = (xs + x0)[:, None, None] + o[None, None, :]
        Y = (ys + y0)[:, None, None] + o[None, :, None]
        X, Y = np.broadcast_to(X, (len(xs), SS, SS)), np.broadcast_to(Y, (len(xs), SS, SS))
        v = (615.0 - Y) / (X - 700.0)
        v0, v1 = p['v']
        va = v0 + (v - v0) * (V_ANS_TOP - v0) / (v1 - v0)
        (a, b), (aa, ab) = p['cols'], p['ans']
        Xa = np.clip(aa + (X - a) * (ab - aa) / (b - a), aa + 0.05, ab - 0.05)
        Ya = 615.0 - va * (Xa - 700.0)
        u = (Xa - DRAFT[0]) * sx + ox - 0.5; w = (Ya - DRAFT[1]) * sy + oy - 0.5
        for c in range(3):
            out[ys, xs, c] = map_coordinates(ans[..., c], [w.ravel(), u.ravel()], order=1, mode='nearest').reshape(len(xs), SS * SS).mean(1)
    return out


def hashf(X, Y, k):
    """A fixed pseudo-random 0..1 per pixel (integer arithmetic: the same bytes everywhere)."""
    v = (X.astype(np.int64) * 73856093) ^ (Y.astype(np.int64) * 19349663) ^ (k * 83492791)
    return (v % 1000003) / 1000003.0


def frame_light(off, tv):
    """The screen's light on what is round the glass (tools/window_depth.py's model of the opening: its rays, its faces),
    FACE_K of it: the far jamb (more toward the glass), the head's underside, the frame and the sashes' inner faces, the
    balcony slab's lit arris under the glass; tv the screen's colour on them. Over BOX: the light added."""
    import window_depth as WD
    names, face, P, bx, op, t = model()
    px = WD.F / t
    c = np.broadcast_to(off[:, :, None, :], P.shape).copy()
    lit = c.copy()
    inop = (P[..., 2] > op['zn'] - 0.5) & (P[..., 2] < op['zf'] + 1e-3) & (P[..., 1] > op['yb'] - 1e-3) & (P[..., 1] < op['yt'] + 1e-3)
    dep = np.clip((P[..., 0] - WD.XS) / op['d'], 0, 1)[..., None]
    low = np.clip((op['yt'] - P[..., 1]) / (op['yt'] - op['yb']), 0, 1)[..., None]   # (the screen is low in the room)
    K = FACE_K
    m = (names == 'wall') & (face == 2) & inop
    lit[m] = (c + K['jamb'] * tv * (0.35 + 0.65 * dep) * (0.6 + 0.4 * low))[m]
    m = (names == 'wall') & (face == 1) & inop
    lit[m] = (c + K['soffit'] * tv * (0.3 + 0.7 * dep))[m]
    near = (P[..., 1] > op['yb'] - 0.3) & (P[..., 1] < op['yt'] + 0.1)   # (the low window's own frame, not the door's above)
    for nm in ('frame', 'sash'):
        for f, k in ((0, 0.25), (1, 0.15), (2, 0.5)):
            m = (names == nm) & (face == f) & near
            lit[m] = (c + K['frame'] * tv * k)[m]
    m = (names == 'slab') & (face == 0) & (np.abs(P[..., 1] - op['yb']) < 0.25) & ((bx[..., 3] - P[..., 1]) * px < 1.0)
    lit[m] = (c + K['slab'] * tv * 0.5)[m]
    return lit.mean(2) - off


def build(city):
    """The window lit by the screen over BOX, the painting's (off), the glass."""
    x0, y0, x1, y1 = BOX
    off = city[y0:y1, x0:x1, :3].copy()
    panes = glass(city)
    m = np.zeros(off.shape[:2], bool)
    for v in panes.values(): m |= v
    Y, X = np.mgrid[y0:y1, x0:x1]
    room = lay(answer(), panes) * GAIN
    tv = np.median(room[m & (lum(room) > np.percentile(lum(room[m]), 60))], 0)   # (the screen's light: its lit room's colour)
    fl = frame_light(off, tv)
    kr = np.clip(1.0 - lum(room) / 70.0, REFL_K, REFL_MAX)[..., None]   # (the night's reflection: the more, the darker behind)
    g = room + kr * off
    g = g + (hashf(X, Y, 5)[..., None] - 0.5) * 3.0                  # (a level or so of grain before the tones)
    import window_depth as WD
    pal = WD.palette(g[m], NPAL)
    g = WD.snap(np.clip(g, 0, 255), pal)
    lit = off + fl
    lit[m] = g[m]
    return off, lit, m


def comp_of(off, lit):
    """The lit picture where it differs from the painting's (alpha 255 there, else clear)."""
    lo, ll = np.round(off), np.round(np.clip(lit, 0, 255))
    d = np.abs(ll - lo).max(-1) > 0
    c = np.zeros(off.shape[:2] + (4,)); c[..., :3] = np.where(d[..., None], ll, 0); c[..., 3] = 255 * d
    return c


def street_js():
    """Its box in street.js's ASSETS.comps (its version kept)."""
    path = os.path.join(ASSETS, 'street.js')
    s = open(path, encoding='utf-8').read()
    x0, y0, x1, y1 = BOX
    m = re.search(r', "%s": \{"src": "assets/%s\.webp\?v=(\w+)", "x": \d+, "y": \d+, "w": \d+, "h": \d+\}' % (COMP, COMP), s)
    ent = ', "%s": {"src": "assets/%s.webp?v=%s", "x": %d, "y": %d, "w": %d, "h": %d}' % (COMP, COMP, m.group(1) if m else '1', x0, y0, x1 - x0, y1 - y0)
    if m: s2 = s[:m.start()] + ent + s[m.end():]
    else:
        m2 = re.search(r', "win_c_top": \{[^}]*\}', s); s2 = s[:m2.end()] + ent + s[m2.end():]
    if s2 != s: open(path, 'w', encoding='utf-8').write(s2)


def draw(city, unlit, box=BOX):
    """Zone 'bmid': the layers as they are (the room dark behind the glass, as painted); the window's light written to
    assets/win_b_mid.webp and its box in street.js. Returns what changed (nothing)."""
    off, lit, _ = build(city)
    save(comp_of(off, lit), os.path.join(ASSETS, COMP + '.webp'))
    street_js()
    return np.zeros((box[3] - box[1], box[2] - box[0]), bool)


def preview(out):
    """The window off and lit, over the layer as it is, x1 and x6; and the lit one with its light at half and cooled
    or warmed as street.js shows its shots."""
    os.makedirs(out, exist_ok=True)
    city = load(os.path.join(ASSETS, 'layer_city_off.webp'))
    off, lit, m = build(city)
    c = comp_of(off, lit)
    a = c[..., 3:] / 255.0
    for tag, k, tint in (('lit', 1.0, (1, 1, 1)), ('half', 0.55, (1, 1, 1)), ('cool', 0.8, (0.8, 0.9, 1)), ('warm', 0.8, (1, 0.9, 0.78))):
        img = off * (1 - a * k) + c[..., :3] * np.array(tint) * a * k
        for s in (1, 6):
            Image.fromarray(np.clip(np.round(img), 0, 255).astype(np.uint8)).resize((img.shape[1] * s, img.shape[0] * s), Image.NEAREST).save(os.path.join(out, '%s_x%d.png' % (tag, s)))
    for s in (1, 6):
        Image.fromarray(np.clip(np.round(off), 0, 255).astype(np.uint8)).resize((off.shape[1] * s, off.shape[0] * s), Image.NEAREST).save(os.path.join(out, 'off_x%d.png' % s))
    g = lit[m]
    print('glass', int(m.sum()), 'px; luminance median', round(float(np.median(lum(g))), 1), 'p90', round(float(np.percentile(lum(g), 90)), 1),
          'max', round(float(lum(g).max()), 1), '; mean colour', np.round(g.mean(0), 1))


def before():
    """The zone's before crops: the layers' pixels in its box before the zones run (the overlapping zones' own before
    crops, in their order, over the layers' pixels where no zone is)."""
    import redraw_zones as R
    x0, y0, x1, y1 = BOX
    for tag, f in (('city', 'layer_city_off.webp'), ('unlit', 'street_unlit.webp')):
        a = load(os.path.join(ASSETS, f))[y0:y1, x0:x1].copy()
        for name, cfg in R.ZONES.items():
            if name == 'bmid': continue
            b = cfg['box']
            ox0, oy0, ox1, oy1 = max(b[0], x0), max(b[1], y0), min(b[2], x1), min(b[3], y1)
            if ox0 >= ox1 or oy0 >= oy1: continue
            z = load(os.path.join(EDITS, '%s_before_%s.webp' % (name, tag)))
            a[oy0 - y0:oy1 - y0, ox0 - x0:ox1 - x0] = z[oy0 - b[1]:oy1 - b[1], ox0 - b[0]:ox1 - b[0]]
        save(a, os.path.join(EDITS, 'bmid_before_%s.webp' % tag))
        print('bmid_before_%s.webp' % tag, a.shape[1], 'x', a.shape[0])


if __name__ == '__main__':
    if '--input' in sys.argv: make_input()
    elif '--before' in sys.argv: before()
    elif '--ask' in sys.argv: ask(sys.argv[sys.argv.index('--ask') + 1])
    elif '--preview' in sys.argv: preview(sys.argv[sys.argv.index('--preview') + 1])
    else: print(__doc__)
