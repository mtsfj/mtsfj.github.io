#!/usr/bin/env python3
"""The top storey's window of the narrow planked building right of the pole (zone5's C, tools/window_depth.py's C_TOP),
lived in: at 22 h, by the lit homes round it, it was a tall dark pane with nothing behind it, never lit.

    (a module: tools/redraw_zones.py's zone 'ctop', the last, calls draw() on the street as the zones before it leave
    it: the layers stay as they are; it writes the window's light, assets/win_c_top.webp, and its box in street.js)
    python3 tools/ctop_room.py --input          once: the drawing's input (tools/src/edits/ctop_in.webp: the street's layer
                                                round the window as the zones leave it, the floor below lit)
    python3 tools/ctop_room.py --before         once: the zone's before crops (tools/src/edits/ctop_before_*.webp)
    python3 tools/ctop_room.py --ask NAME       a drawing asked of the image model (OpenRouter's key in
                                                ~/.config/openrouter/key; about 0.25 $): NAME 'room' (the window lit, from
                                                ctop_in.webp brightened and enlarged 8 times) or 'lamp' (the same room
                                                late, from the room's answer); its prompt tools/src/edits/ctop_NAME_prompt.txt,
                                                its answer ctop_NAME_model.webp; the window is drawn from the saved
                                                answers, never from a new call
    python3 tools/ctop_room.py --preview DIR    the window off, lit and late over the layer as it is, x1 and x6

What the street sees of it (R28: what is detailed is drawn by the image model in context, then brought to the street's
pixels). The window is 7 m over the pavement, set back in the planks (window_depth.py's model: two sliding sashes, 0.9 m
along the street, 1.2 m tall, its sill 4.8 m over the eye); from below, through it, only the top of the room: its
ceiling, and under a level line a little below the glass's middle the top of its far side wall, face on. The room was
painted twice by the image model in the street at 22 h (its prompts say so): lit by its ceiling lamp (a cream ceiling,
brightest toward the lamp deeper in the room, a pale curtain drawn back on the left, a small framed picture, the top of
a bookcase with a box and books), then the same room late, the ceiling lamp off and a small table lamp left on (much
dimmer, its glow rising from the bottom of the glass, the lamp's shade just showing at the right pane's foot, the
ceiling in a warm shadow). Each answer, darkened back (GAMMA), is laid into the painting's two panes as they are (the
frame, the sashes, the meeting stiles, the sill, the reveal all the painter's: the answer drew a thinner frame): each
pane of the answer mapped onto the painting's, each street pixel the mean of 8 x 8 points of it (REG, PANES, S_*). Its
light brought to the street's lit homes (GAIN), the night's reflection on the glass the painting's own (the more of it
the darker the room behind), a level of grain, then its own tones (a median cut of its glass, NPAL): crisp, a tone a
pixel. Round the glass the room's light as window_depth.py lights the window under it (its model's rays: the far jamb,
the head's underside, the frame's faces, the sill's top edge; FACE_K of it, in the street's homes' warm ramp); late, as
much of it as the glass has at that height. Off (its layers, the power cut) the window stays exactly as painted.

street.js: a 'home' (COMP_KIND), longer spells than a home's, out at its bedtime (its rank on NIGHT.home), never in step
with the others; its sheet two frames side by side, CTOP choosing one: late in the evening (each night its own moment,
22:45 to 0:30) the ceiling lamp switched off, the small lamp left on till bedtime, swapped at once as a switch does. The
power cut and the red night as every comp. Its light does not reach the wet sidewalk 7 m below in any measurable way,
nor the water's mirror (its reflection would fall far below the frame): no ground light. Needs Pillow, numpy, scipy.
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
DRAFT = (1025, 110, 1155, 305)                 # the draft's crop (the pole, C's top storey, the head of its lit window)
SCALE = 8                                      # (each street pixel an 8 x 8 block in the draft)
LOWER = ('win_z1_warm', 1081, 288)             # (the floor below lit in the draft's input: the street's homes' light)
COMP = 'win_c_top'
BOX = (1075, 124, 1111, 254)                   # the zone (redraw_zones.py 'ctop') and the comp's frame: the reveal, the
                                               #  head's underside, the frame, the glass, the sill
# the answers on the street: they came back square, the crop's top 1040 x 1092 px (the image model's own framing),
# fitted on the walls and the pole round the window (street px a pixel of the answer, x and y; the answer's origin)
REG = (0.1285, 0.129, 1024.9375, 110.25)
LAMP_SHIFT = (2, 3)                            # (the late answer on the first: its pixels moved so, x and y)
# the glass, on the painting (the layer as window_depth.py leaves it) and in the answer, in the street's coordinates: each
# pane's columns [a, b), its top and bottom along the window's head and sill lines (s = x + y at a pixel's centre,
# continuous: the head and the sill run at 45 degrees there). The painting's top is its first row of glass under the
# head's dark, its bottom the row over the sill's lit line (x + y = 1325..1327 at its pixels);
# the answer drew the same window with a thinner frame and a deeper bottom rail: its left pane four columns wider (the
# curtain in them), its glass ending 7 px higher. Each pane of the answer laid in the painting's: across, a linear map
# of its columns; along the column, of its top and bottom.
PANES = {'L': dict(cols=(1092, 1098), ans=(1088.0, 1098.0)), 'R': dict(cols=(1101, 1109), ans=(1101.0, 1109.0))}
S_TOP = {'L': 1255.5, 'R': 1253.5}            # (the painting's glass: its top edge, x + 0.5 + its first row, by pane)
S_BOT = 1325.5                                 # (its bottom edge: its last pixel's centre x + y + 1 = 1325, + 0.5)
S_ANS = (1250.5, 1316.0)                       # (the answer's glass, top and bottom edges, inside its frame)
GAIN = (0.8, 1.1)                              # (the answer's room brought to the street's lit homes, their median
                                               #  luminance 73..95, their 90th centile 98..156; the late one a little
                                               #  more: the small lamp's glow, not a dark room)
FACE_K = dict(jamb=0.55, soffit=0.3, frame=0.7, sill=0.8)   # (the room's light round the glass, of tools/window_depth.py's)
NPAL = 20                                      # (its tones: a median cut of each state's glass)
REFL_K = 0.12                                  # (the night's reflection kept on the lit glass)
SS = 8                                         # (points a pixel each way, sampling the answer)


def load(p, mode='RGBA'):
    return np.asarray(Image.open(p).convert(mode)).astype(float)


def lum(a):
    return a @ np.array([0.299, 0.587, 0.114])


def save(a, p):
    Image.fromarray(np.clip(np.round(a), 0, 255).astype(np.uint8), 'RGBA' if a.shape[-1] == 4 else 'RGB').save(
        p, 'WEBP', lossless=True, quality=100, method=6, exact=True)


def make_input():
    """The draft's input: the street's layer over DRAFT (the zones done), the floor below lit (its comp laid on it)."""
    x0, y0, x1, y1 = DRAFT
    a = load(os.path.join(ASSETS, 'layer_city_off.webp'))[y0:y1, x0:x1, :3]
    n, cx, cy = LOWER
    c = load(os.path.join(ASSETS, n + '.webp'))
    h, w = c.shape[:2]
    oy0, ox0 = max(cy - y0, 0), max(cx - x0, 0)
    oy1, ox1 = min(cy + h, y1) - y0, min(cx + w, x1) - x0
    if oy1 > oy0 and ox1 > ox0:
        s = c[oy0 + y0 - cy:oy1 + y0 - cy, ox0 + x0 - cx:ox1 + x0 - cx]
        al = s[..., 3:] / 255.0
        a[oy0:oy1, ox0:ox1] = a[oy0:oy1, ox0:ox1] * (1 - al) + s[..., :3] * al
    save(a, os.path.join(EDITS, 'ctop_in.webp'))
    print('ctop_in.webp', a.shape[1], 'x', a.shape[0])


def ask(name):
    """A drawing asked of the image model: 'room' from ctop_in.webp (brightened, scaled), 'lamp' from the room's answer."""
    import urllib.request
    if name == 'room':
        z = load(os.path.join(EDITS, 'ctop_in.webp'), 'RGB') / 255.0
        x0, y0, x1, y1 = DRAFT
        im = Image.fromarray((np.clip(z ** (1 / GAMMA), 0, 1) * 255).astype(np.uint8)).resize(((x1 - x0) * SCALE, (y1 - y0) * SCALE), Image.NEAREST)
    else:
        im = Image.open(os.path.join(EDITS, 'ctop_room_model.webp')).convert('RGB')
    buf = io.BytesIO(); im.save(buf, 'PNG')
    key = open(os.path.expanduser('~/.config/openrouter/key')).read().strip()
    content = [{"type": "text", "text": open(os.path.join(EDITS, 'ctop_%s_prompt.txt' % name)).read().strip()},
               {"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()}}]
    body = {"model": MODEL, "modalities": ["image", "text"], "usage": {"include": True}, "messages": [{"role": "user", "content": content}]}
    req = urllib.request.Request('https://openrouter.ai/api/v1/chat/completions', data=json.dumps(body).encode(),
                                 headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'})
    d = json.loads(urllib.request.urlopen(req, timeout=900).read())
    url = d['choices'][0]['message']['images'][0]['image_url']['url']
    Image.open(io.BytesIO(base64.b64decode(url.split(',', 1)[1]))).save(os.path.join(EDITS, 'ctop_%s_model.webp' % name), 'WEBP', lossless=True, quality=100, method=6)
    print('ctop_%s_model.webp saved; cost' % name, d.get('usage', {}).get('cost'), '$')


def answer(name):
    """An answer darkened back to the street's light (floats, 0..255), the late one moved onto the first."""
    a = load(os.path.join(EDITS, 'ctop_%s_model.webp' % name), 'RGB') / 255.0
    a = (a ** GAMMA) * 255.0
    if name == 'lamp':
        a = np.roll(np.roll(a, LAMP_SHIFT[1], 0), LAMP_SHIFT[0], 1)
    return a


def glass():
    """The painting's glass over BOX (bool): each pane's columns, from its top edge (S_TOP: the head's line) to the row
    over the sill's lit line."""
    x0, y0, x1, y1 = BOX
    Y, X = np.mgrid[y0:y1, x0:x1]
    m = np.zeros(X.shape, bool)
    for k, p in PANES.items():
        a, b = p['cols']
        m |= (X >= a) & (X < b) & (X + 0.5 + Y >= S_TOP[k]) & (X + 0.5 + Y + 0.5 <= S_BOT)
    return m


def lay(ans):
    """The answer's room in the painting's panes: each pixel the mean of SS x SS points, each point mapped into the
    answer's pane (across: its columns; along each column: its top and bottom, S_TOP..S_BOT to S_ANS) and on the answer
    (REG), read there (bilinear). Over BOX, zero outside the glass."""
    from scipy.ndimage import map_coordinates
    x0, y0, x1, y1 = BOX
    out = np.zeros((y1 - y0, x1 - x0, 3))
    m = glass()
    sx, sy, ox, oy = REG
    o = (np.arange(SS) + 0.5) / SS
    for k, p in PANES.items():
        a, b = p['cols']; (aa, ab) = p['ans']
        for x in range(a, b):
            for y in range(y0, y1):
                if not m[y - y0, x - x0]: continue
                yp = y + o[:, None] + np.zeros((1, SS)); xp = x + o[None, :] + np.zeros((SS, 1))
                t = np.clip(((x + 0.5) + yp - S_TOP[k]) / (S_BOT - S_TOP[k]), 0.0, 1.0)
                xd = np.clip(aa + (xp - a) * (ab - aa) / (b - a), aa + 0.1, ab - 0.1)
                yd = S_ANS[0] + t * (S_ANS[1] - S_ANS[0]) - (np.floor(xd) + 0.5)
                u = (xd - ox) / sx - 0.5; v = (yd - oy) / sy - 0.5
                out[y - y0, x - x0] = [map_coordinates(ans[..., c], [v.ravel(), u.ravel()], order=1, mode='nearest').mean() for c in range(3)]
    return out


def hashf(X, Y, k):
    """A fixed pseudo-random 0..1 per pixel (integer arithmetic: the same bytes everywhere)."""
    v = (X.astype(np.int64) * 73856093) ^ (Y.astype(np.int64) * 19349663) ^ (k * 83492791)
    return (v % 1000003) / 1000003.0


def frame_light(off):
    """The room's light on what is round the glass (tools/window_depth.py's model of the opening, C_TOP: its rays, its
    faces, their lit tones), FACE_K of it: the far jamb, the head's underside, the frame and the sashes, the sill's top
    edge; the painting's pixels (off) what each face is; in the street's homes' warm ramp. Over BOX: the light added
    (the lit picture minus off)."""
    import window_depth as WD
    S, G, ops = WD.model('C')
    op = ops[1]
    dx, dy = WD.rays(BOX)
    idx, t, face = S.cast(dx, dy)
    t = np.where(idx >= 0, t, 1.0)
    P = np.stack([dx * t, dy * t, t], -1)
    names = np.array(S.name + ['none'], dtype=object)[idx]
    bx = np.array(S.b + [(0, 0, 0, 0, 0, 0)], float)[idx]
    px = WD.F / t
    c = np.broadcast_to(off[:, :, None, :], P.shape).copy()
    lit = c.copy()
    inop = (P[..., 2] > op['zn'] - 0.5) & (P[..., 2] < op['zf'] + 1e-3) & (P[..., 1] > op['yb'] - 1e-3) & (P[..., 1] < op['yt'] + 1e-3)
    dep = np.clip((P[..., 0] - WD.XS) / op['d'], 0, 1)[..., None]
    up = np.exp(-np.clip(op['yt'] - P[..., 1], 0, None) / 0.18)[..., None]
    K = FACE_K
    m = (names == 'wall') & (face == 2) & inop
    lit[m] = (c + K['jamb'] * (c * 0.25 + WD.REVEAL_LIT * ((0.55 + 0.45 * dep) * (1 - 0.2 * up)) - c))[m]
    m = (names == 'wall') & (face == 1) & inop
    lit[m] = (c + K['soffit'] * (c * 0.4 + WD.SOFFIT_LIT * (0.35 + 0.65 * dep) - c))[m]
    near = (P[..., 1] > op['yb'] - 0.3)                                 # (C_TOP's own frame, not the lower window's)
    for nm in ('frame', 'sash', 'glassD0', 'glassD1'):                  # (what the model calls glass, the painting frame:
        for f, k in ((0, 0.4), (1, 0.3), (2, 0.6)):                     #  the frame's light)
            m = (names == nm) & (face == f) & near
            lit[m] = (c + K['frame'] * (c * 0.6 + WD.FRAME_LIT * k - c))[m]
    m = (names == 'sill') & (face == 0) & (np.abs(P[..., 1] - op['yb']) < 0.25)
    top_edge = ((bx[..., 3] - P[..., 1]) * px < 1.0)[..., None]
    lit[m] = (c + K['sill'] * WD.REVEAL_LIT * np.where(top_edge, 0.45, 0.15))[m]
    return WD.warm('B', off, lit.mean(2)) - off


def build(city):
    """The window's two lit pictures over BOX (the ceiling lamp's, the small lamp's), the painting's (off), the glass."""
    import window_depth as WD
    x0, y0, x1, y1 = BOX
    off = city[y0:y1, x0:x1, :3].copy()
    m = glass()
    Y, X = np.mgrid[y0:y1, x0:x1]
    rooms = [lay(answer(n)) * g for n, g in zip(('room', 'lamp'), GAIN)]
    fl = frame_light(off)
    # late, the light round the glass as the glass's own there (row by row: the small lamp lights the low part)
    rk = np.array([lum(rooms[1][r][m[r]]).mean() / max(lum(rooms[0][r][m[r]]).mean(), 1.0) if m[r].any() else np.nan for r in range(y1 - y0)])
    ok = ~np.isnan(rk); rk = np.interp(np.arange(len(rk)), np.nonzero(ok)[0], rk[ok])
    lits = []
    for k, r in enumerate(rooms):
        # the night's reflection on the glass: the more of it, the darker the room behind (the painting's glass is it)
        kr = np.clip(1.0 - lum(r) / 70.0, REFL_K, 0.8)[..., None]
        g = r + kr * off
        g = g + (hashf(X, Y, 3 + k)[..., None] - 0.5) * 3.0             # (a level or so of grain before the tones)
        pal = WD.palette(g[m], NPAL)                                    # (its own tones: a median cut of its glass)
        g = WD.snap(np.clip(g, 0, 255), pal)
        lit = off + fl * (1.0 if k == 0 else np.clip(rk, 0, 1)[:, None, None])
        lit[m] = g[m]
        lits.append(lit)
    return off, lits, m


def comp_of(off, lit):
    """The lit picture where it differs from the painting's (alpha 255 there, else clear)."""
    lo, ll = np.round(off), np.round(np.clip(lit, 0, 255))
    d = np.abs(ll - lo).max(-1) > 0
    c = np.zeros(off.shape[:2] + (4,)); c[..., :3] = np.where(d[..., None], ll, 0); c[..., 3] = 255 * d
    return c


def street_js():
    """Its box in street.js's ASSETS.comps (one frame's: the sheet holds two side by side; its version kept)."""
    path = os.path.join(ASSETS, 'street.js')
    s = open(path, encoding='utf-8').read()
    x0, y0, x1, y1 = BOX
    m = re.search(r', "%s": \{"src": "assets/%s\.webp\?v=(\w+)", "x": \d+, "y": \d+, "w": \d+, "h": \d+\}' % (COMP, COMP), s)
    ent = ', "%s": {"src": "assets/%s.webp?v=%s", "x": %d, "y": %d, "w": %d, "h": %d}' % (COMP, COMP, m.group(1) if m else '1', x0, y0, x1 - x0, y1 - y0)
    if m: s2 = s[:m.start()] + ent + s[m.end():]
    else:
        m2 = re.search(r', "win_z1_warm": \{[^}]*\}', s); s2 = s[:m2.end()] + ent + s[m2.end():]
    if s2 != s: open(path, 'w', encoding='utf-8').write(s2)


def draw(city, unlit, box=BOX):
    """Zone 'ctop': the layers as they are (the room dark behind the glass, as painted); the window's light written to
    assets/win_c_top.webp (the ceiling lamp's, then the small lamp's, side by side) and its box in street.js. Returns
    what changed (nothing)."""
    off, lits, _ = build(city)
    sheet = np.concatenate([comp_of(off, l) for l in lits], 1)
    save(sheet, os.path.join(ASSETS, COMP + '.webp'))
    street_js()
    return np.zeros((box[3] - box[1], box[2] - box[0]), bool)


def before():
    """The zone's before crops: the layers' pixels in its box before the zones run (the overlapping zones' own before
    crops, in their order, over the layers' pixels where no zone is)."""
    import redraw_zones as R
    x0, y0, x1, y1 = BOX
    for tag, f in (('city', 'layer_city_off.webp'), ('unlit', 'street_unlit.webp')):
        a = load(os.path.join(ASSETS, f))[y0:y1, x0:x1].copy()
        for name, cfg in R.ZONES.items():
            if name == 'ctop': continue
            b = cfg['box']
            ox0, oy0, ox1, oy1 = max(b[0], x0), max(b[1], y0), min(b[2], x1), min(b[3], y1)
            if ox0 >= ox1 or oy0 >= oy1: continue
            z = load(os.path.join(EDITS, '%s_before_%s.webp' % (name, tag)))
            a[oy0 - y0:oy1 - y0, ox0 - x0:ox1 - x0] = z[oy0 - b[1]:oy1 - b[1], ox0 - b[0]:ox1 - b[0]]
        save(a, os.path.join(EDITS, 'ctop_before_%s.webp' % tag))
        print('ctop_before_%s.webp' % tag, a.shape[1], 'x', a.shape[0])


def preview(out):
    """The window off, lit by its ceiling lamp, lit by its small lamp, over the layer as it is, x1 and x6."""
    os.makedirs(out, exist_ok=True)
    city = load(os.path.join(ASSETS, 'layer_city_off.webp'))
    off, lits, m = build(city)
    for tag, a in (('off', off), ('ceiling', lits[0]), ('lamp', lits[1])):
        for k in (1, 6):
            Image.fromarray(np.clip(np.round(a), 0, 255).astype(np.uint8)).resize((a.shape[1] * k, a.shape[0] * k), Image.NEAREST).save(os.path.join(out, '%s_x%d.png' % (tag, k)))


if __name__ == '__main__':
    if '--input' in sys.argv: make_input()
    elif '--before' in sys.argv: before()
    elif '--ask' in sys.argv: ask(sys.argv[sys.argv.index('--ask') + 1])
    elif '--preview' in sys.argv: preview(sys.argv[sys.argv.index('--preview') + 1])
    else: print(__doc__)
