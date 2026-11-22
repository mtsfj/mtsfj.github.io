#!/usr/bin/env python3
"""The grey building's garage shutter at the street's end (under the study, left of its red door): a real roller
shutter (シャッター) where the painter left one flat dark blue block.

    (a module: tools/redraw_zones.py's zone 'gshutter', the last, calls draw(city, unlit, box) on the street as the zones
     before it leave it: both layers in its box, the same bytes each time)
    python3 tools/grey_shutter.py --befores        once: the zone's before copies (tools/src/edits/gshutter_before_*.webp)
                                                   from the assets as they are, the earlier zones' own before copies laid
                                                   over their boxes first (oden's, footO's: what tools/redraw_zones.py
                                                   restores there before any zone runs)
    python3 tools/grey_shutter.py --input          the draft's input (tools/src/edits/gshutter_in.webp: the street's layer
                                                   round the building, its comps lit)
    python3 tools/grey_shutter.py --ask shutter    the draft asked of the image model (OpenRouter's key in
                                                   ~/.config/openrouter/key; about 0.25 $), from gshutter_in.webp
                                                   brightened and enlarged 8 times; its prompt gshutter_shutter_prompt.txt,
                                                   its answer gshutter_shutter_model.webp (the shutter is drawn from the
                                                   saved answer, never a new call)
    python3 tools/grey_shutter.py --preview DIR    the opening before and after, both layers, x8 (nothing written)

What was there: in the garage opening on the building's ground floor (x 510-563, from its head at row 586 down to the
building's foot at 641), one flat dark blue block (16, 21, 44 on average) with a faint grid of the painter's blotches, the
same in both layers (no light of any lamp on it), its top rows dark under the head.

What the camera sees (the street's camera: VP (700, 615), f 960, the eye 1.41 m over the road, the sidewalks 0.15 m up;
tools/facade_foot.py's): the building faces the street square on across the crossroads, its foot level on row 641
(facade_foot's 'farL'), so its front is the frontal plane at Z = 960 x 1.26 / 26 = 46.5 m: 20.6 px a metre. The opening
is 54 px wide, 2.62 m, and 55 rows high from the sidewalk, 2.67 m: a one-car garage's, as a Japanese light shutter
(軽量シャッター) closes them. It stands 20 m behind the oden's front plane (X -5.5 m; the opening is at X -9.2 to -6.6
m, left of it), round the oden's corner: none of the oden's lights (its windows face the street, its lantern hangs in
front of its wall) reaches it; nor does the red door's (a lamp inside its recess), nor the street lamp's (35 m away);
what lights it is the night sky (the city's glow in the clouds), from above, as the wall round it. So both layers alike,
as the painter had them: the power cut takes nothing from it, the hours and the red night grade it as the street.

What it is now (R28: the image model drew the shutter in its context, tools/src/edits/gshutter_shutter_model.webp, from
gshutter_in.webp and gshutter_shutter_prompt.txt: a closed steel roller shutter, its head cover with a slot under it, the
guide rails, the bottom bar with its handle, grime and thin rust streaks, the lowest part wet): its layout read on the
answer (registered on the street: the answer is the input at 1024 / 192 = 5.33 a pixel, no offset), put on the pixel
grid as the simple geometry it is, each plane its own tone (R29), in the painter's own light (R2: his low frequencies
inside the opening, as a row profile: the sky's light, darker under the head, lighter low down; his colour):
- the head cover (the case's front, 0.24 m: rows 586-590): one flat steel plate, the lintel's shadow on its top row, a
  bead along its foot; the slot under it (591) where the curtain goes up into the case, the first slat in its shade;
- the guide rails: a steel channel down each jamb (columns 510 and 563), their flat face in the jamb's shade, as the
  answer has them;
- the curtain (rows 592-637): steel slats 1.5 px = 7.3 cm apart (a light shutter's are 5-8 cm), each one's profile on
  the sky's light (its hooked joint in shade, its upper face turned up to the sky and lit, its face, its lower curl
  turning under), every row the mean of what of the slats it covers (SUB points), so they read as fine level ribs, a
  pixel and sub-pixel tone steps, crisp, no moire (their period three rows exactly); a little darker by each jamb (the
  jamb hides part of the sky);
- the bottom bar (座板, rows 638-639): its top bead catching the sky, its face, the pull handle and its lock at the
  middle (its lit lip, the dark under it); row 640 its seal on the threshold, the contact's shade;
- the weather, the answer's (its fine structure only: its columns' grime over its own low frequencies, its rust's warmth
  over its own, the answer's slats averaged out): the grime streaking down, a few thin rust streaks from the head cover
  and down the right rail; the splash zone (its lowest 0.4 m) darker, wet, its slats' lit edges a little sharper (the
  wet steel's sheen); the threshold (row 641, the opening's width) wet, a faint sheen.
The road's wet mirror (street.js, live) shows its foot as it is now; no ground light (GL) falls on its foot (gl_oden's
and the rest's are 0-5 there). Needs Pillow, numpy, scipy.
"""
import base64
import io
import json
import os
import re
import sys
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, gaussian_filter1d

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDITS = os.path.join(ROOT, 'tools', 'src', 'edits')
ASSETS = os.path.join(ROOT, 'assets')
MODEL = 'openai/gpt-5.4-image-2'
GAMMA = 2.0                                      # (the draft's input brightened, its answer darkened back: z ** GAMMA)
DRAFT = (440, 540, 632, 668)                     # the draft's crop (the oden's end, the grey building's ground floor, the railing)
SCALE = 8                                        # (a street pixel an 8 x 8 block in the draft's input)
ANS = 1024 / 192                                 # (the answer: the input at this scale, no offset; fitted, r 0.995)
BOX = (505, 572, 566, 642)                       # the zone (redraw_zones.py 'gshutter'): the opening, its jambs' edges, the threshold
OPEN = (510, 564)                                # the opening's columns [x0, x1)
HEAD, SLOT, CURT, BAR, SEAL, SILL = (586, 591), 591, (592, 638), (638, 640), 640, 641   # its rows
RAILS = (510, 563)                               # the guide rails' columns
PITCH = 1.5                                      # the slats' pitch (px): 7.3 cm at 20.6 px a metre
# a slat's profile from its joint down, (share of the pitch, its light times the plane's): the hooked joint in shade, the
# upper face turned to the sky, the face, the lower curl turning under (normalised to a mean of 1: the plane keeps its value)
PROFILE = ((0.12, 0.30), (0.22, 1.90), (0.44, 1.00), (0.22, 0.45))
SUB = 24                                         # (points a row: each row the mean of the slats it covers)
K = dict(cover=1.08, cover_top=0.60, bead=0.80, slot=0.30, slot_slat=0.72, rail=0.95, jamb=0.10,
         bar_top=1.22, bar=0.92, handle_top=1.50, handle_dk=0.55, lock=0.42, seal=0.58)
HANDLE = (535, 538)                              # the bar's pull handle (its columns; the lock at its middle)
WET = dict(m=0.4, dark=0.90, edge=1.12, sill=1.10)   # the splash zone's height (m) and make-up; the threshold's sheen
DETAIL, RUST = 0.6, (0.06, 0.22, (1.25, 1.0, 0.80))   # the answer's grime's strength; its rust: the warmth that is a
                                                 # whole streak, how much darker it is, its tint
GRAIN, SEED = 0.025, 586
PXM = 960 / 46.52                                # (px a metre on the front)

lum = lambda z: 0.299 * z[..., 0] + 0.587 * z[..., 1] + 0.114 * z[..., 2]


def load(p, mode='RGBA'):
    return np.asarray(Image.open(p).convert(mode)).astype(float)


def save(a, p):
    Image.fromarray(np.clip(np.round(a), 0, 255).astype(np.uint8), 'RGBA' if a.shape[-1] == 4 else 'RGB').save(
        p, 'WEBP', lossless=True, quality=100, method=6, exact=True)


def street_comps():
    s = open(os.path.join(ASSETS, 'street.js')).read().split('\n')[3]
    return json.loads(re.search(r'const ASSETS = (\{.*?\});', s).group(1))['comps']


# ---- the draft
def make_input():
    """The draft's input: the street's layer over DRAFT, its comps there lit (the study's spill)."""
    x0, y0, x1, y1 = DRAFT
    a = load(os.path.join(ASSETS, 'layer_city_off.webp'))[y0:y1, x0:x1, :3].copy()
    for n, c in street_comps().items():
        if n.startswith('z7_'): continue                 # (the drinks corner's sheets: far from here)
        im = load(os.path.join(ASSETS, c['src'].split('?')[0].replace('assets/', '')))[:c['h'], :c['w']]
        cx, cy = c['x'], c['y']; h, w = im.shape[:2]
        ox0, oy0, ox1, oy1 = max(cx, x0), max(cy, y0), min(cx + w, x1), min(cy + h, y1)
        if ox1 <= ox0 or oy1 <= oy0: continue
        s = im[oy0 - cy:oy1 - cy, ox0 - cx:ox1 - cx]; al = s[..., 3:] / 255.0
        d = a[oy0 - y0:oy1 - y0, ox0 - x0:ox1 - x0]; d[:] = d * (1 - al) + s[..., :3] * al
    save(np.clip(a, 0, 255), os.path.join(EDITS, 'gshutter_in.webp'))
    print('gshutter_in.webp', a.shape[1], 'x', a.shape[0])


def ask(name='shutter'):
    """The drawing asked of the image model, from gshutter_in.webp brightened and enlarged SCALE times."""
    import urllib.request
    z = load(os.path.join(EDITS, 'gshutter_in.webp'), 'RGB') / 255.0
    x0, y0, x1, y1 = DRAFT
    im = Image.fromarray((np.clip(z ** (1 / GAMMA), 0, 1) * 255).astype(np.uint8)).resize(((x1 - x0) * SCALE, (y1 - y0) * SCALE), Image.NEAREST)
    buf = io.BytesIO(); im.save(buf, 'PNG')
    key = open(os.path.expanduser('~/.config/openrouter/key')).read().strip()
    content = [{"type": "text", "text": open(os.path.join(EDITS, 'gshutter_%s_prompt.txt' % name)).read().strip()},
               {"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()}}]
    body = {"model": MODEL, "modalities": ["image", "text"], "usage": {"include": True}, "messages": [{"role": "user", "content": content}]}
    req = urllib.request.Request('https://openrouter.ai/api/v1/chat/completions', data=json.dumps(body).encode(),
                                 headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'})
    d = json.loads(urllib.request.urlopen(req, timeout=900).read())
    url = d['choices'][0]['message']['images'][0]['image_url']['url']
    Image.open(io.BytesIO(base64.b64decode(url.split(',', 1)[1]))).save(os.path.join(EDITS, 'gshutter_%s_model.webp' % name), 'WEBP', lossless=True, quality=100, method=6)
    print('gshutter_%s_model.webp saved; cost' % name, d.get('usage', {}).get('cost'), '$')


def answer():
    """The answer over the street's grid (each scene pixel the mean of the answer's pixels it covers), darkened back:
    (H, W, 3) floats over DRAFT."""
    A = load(os.path.join(EDITS, 'gshutter_shutter_model.webp'), 'RGB')
    x0, y0, x1, y1 = DRAFT; H, W = y1 - y0, x1 - x0
    out = np.zeros((H, W, 3))
    e = lambda i: int(round(i * ANS))
    for j in range(H):
        for i in range(W):
            out[j, i] = A[e(j):max(e(j + 1), e(j) + 1), e(i):max(e(i + 1), e(i) + 1)].reshape(-1, 3).mean(0)
    return (out / 255.0) ** GAMMA * 255.0


def weather(box):
    """The answer's weather over the box: its grime (a factor about 1) and its rust (0..1), each from its fine structure
    alone, inside the shutter it drew (its slats averaged out down each column, its own light and its rails' and jambs'
    edges taken away)."""
    x0, y0, x1, y1 = box; dx0, dy0 = DRAFT[:2]
    A = answer()[y0 - dy0:y1 - dy0, x0 - dx0:x1 - dx0]
    H, W = A.shape[:2]; yy, xx = np.mgrid[0:H, 0:W]; X, Y = xx + x0, yy + y0
    M = (X >= OPEN[0] + 3) & (X < OPEN[1] - 3) & (Y >= HEAD[0] + 1) & (Y < BAR[1])
    def within(v, sig):                                          # (a low-pass inside M alone)
        return gaussian_filter(np.where(M, v, 0.0), sig) / np.maximum(gaussian_filter(M.astype(float), sig), 1e-4)
    Lv = gaussian_filter1d(lum(A) + 1.0, 1.6, axis=0)            # (its slats, ~6 rows apart, averaged out down the column)
    g = np.where(M, np.clip(Lv / within(Lv, (6, 8)), 0.8, 1.15), 1.0)
    wv = gaussian_filter1d((A[..., 0] + 1) / (A[..., 2] + 1), 1.2, axis=0)
    r = np.where(M, np.clip((wv - within(wv, (5, 5))) / RUST[0], 0, 1), 0.0)
    r = np.clip(gaussian_filter1d(r, 2.5, axis=0), 0, 1)        # (streaks run down: a lone spot fades, a streak stays)
    return g, r


# ---- the opening
def row_light(P, x0, y0):
    """the painter's light in the opening, a row profile (his low frequencies: the sky's, darker under the head, lighter
    low down; his colour): (rows of the box, 3)"""
    H = P.shape[0]
    a, b = OPEN[0] + 2 - x0, OPEN[1] - 2 - x0
    rows = np.arange(H) + y0
    m = (rows >= CURT[0] + 1) & (rows < CURT[1])
    prof = P[:, a:b].mean(1)
    out = np.zeros((H, 3))
    for c in range(3):
        v = np.interp(rows, rows[m], gaussian_filter1d(prof[m, c], 2.5, mode='nearest'))
        out[:, c] = v
    return out


def slats(rows):
    """each row's mean of the slats' profile it covers (a factor about 1)"""
    edges = np.cumsum([0.0] + [s for s, _ in PROFILE]); vals = np.array([v for _, v in PROFILE])
    vals = vals / (np.diff(edges) * vals).sum()
    out = np.zeros(len(rows))
    for k in range(SUB):
        t = ((rows - CURT[0] + (k + 0.5) / SUB) / PITCH) % 1.0
        out += vals[np.searchsorted(edges, t, side='right') - 1]
    return out / SUB


def hashf(X, Y, k):
    v = np.sin(X * 12.9898 + Y * 78.233 + k * 37.719) * 43758.5453
    return v - np.floor(v)


def redraw(P, x0, y0, wthr):
    """the opening redrawn in P (a layer's crop at (x0, y0), RGB floats); returns the new crop"""
    H, W = P.shape[:2]; yy, xx = np.mgrid[0:H, 0:W]; Y = yy + y0; X = xx + x0
    out = P.copy()
    Lr = row_light(P, x0, y0)[:, None, :] * np.ones((1, W, 1))   # (the plane's light, each row)
    g, rust = wthr
    grain = 1.0 + GRAIN * (hashf(X, Y, SEED) * 2 - 1)
    inside = (X >= OPEN[0]) & (X < OPEN[1])
    h = (CURT[1] - 0.5 - Y) / PXM                                # (height over the bar, m)
    wet = np.clip(1 - h / WET['m'], 0, 1)
    # the jambs hide a little of the sky: darker within a few pixels of each
    dj = np.minimum(X - OPEN[0], OPEN[1] - 1 - X).astype(float)
    jamb = 1 - K['jamb'] * np.exp(-dj / 2.0)
    weathered = 1 + DETAIL * (g - 1)
    tone = np.ones((H, W))
    # the head cover and its slot
    cov = inside & (Y >= HEAD[0]) & (Y < HEAD[1])
    tone[cov] = K['cover']                                       # (a flat plate a little proud of the curtain)
    tone[inside & (Y == HEAD[0])] = K['cover'] * K['cover_top']
    tone[inside & (Y == HEAD[1] - 1)] = K['cover'] * K['bead']
    tone[inside & (Y == SLOT)] = K['slot']
    # the curtain
    cur = inside & (Y >= CURT[0]) & (Y < CURT[1])
    s = slats(Y[:, 0].astype(float))[:, None] * np.ones((1, W))
    s_wet = 1 + (s - 1) * (1 + (WET['edge'] - 1) * 4 * wet)      # (wet: its lit edges a little sharper)
    tone[cur] = (s_wet * (1 - (1 - WET['dark']) * wet))[cur]
    tone[inside & (Y == CURT[0])] *= K['slot_slat']
    # the bottom bar, its handle and lock, its seal
    tone[inside & (Y == BAR[0])] = K['bar_top']
    tone[inside & (Y == BAR[0] + 1)] = K['bar'] * WET['dark']
    hd = (X >= HANDLE[0]) & (X < HANDLE[1])
    tone[hd & (Y == BAR[0])] = K['handle_top']
    tone[hd & (Y == BAR[0] + 1)] = K['handle_dk']
    tone[(X == (HANDLE[0] + HANDLE[1]) // 2) & (Y == BAR[0] + 1)] = K['lock']
    tone[inside & (Y == SEAL)] = K['seal']
    # the rails: their flat face (the bar's ends run into them)
    rail = np.isin(X, RAILS) & (Y > HEAD[1] - 1) & (Y < SEAL)
    tone[rail] = K['rail'] * (1 - (1 - WET['dark']) * wet[rail])
    tone[rail & (Y == SLOT)] = K['rail'] * 0.8
    # the light: the plane's row light (the curtain's; under the head the head's own row there), the jambs' shade, the weather
    new = Lr * (tone * jamb * weathered * grain)[..., None]
    rs = (rust * ((Y < BAR[0]) & ~rail))[..., None]
    new = np.clip(new * (1 - RUST[1] * rs) * (1 + rs * (np.array(RUST[2]) - 1)), 0, 255)
    drawn = inside & (Y >= HEAD[0]) & (Y <= SEAL)
    out[drawn] = new[drawn]
    # the threshold in front (its row, the opening's width): wet, a faint sheen of the sky
    th = inside & (Y == SILL)
    out[th] = np.clip(P[th] * WET['sill'] * grain[th][:, None], 0, 255)
    return out


def draw(city, unlit, box=BOX):
    """tools/redraw_zones.py's zone 'gshutter': both layers, in place, each from its own pixels; what changed"""
    x0, y0, x1, y1 = box; ch = np.zeros(city.shape[:2], bool)
    wthr = weather(box)
    for a in (city, unlit):
        sub = a[y0:y1, x0:x1]; old = sub[..., :3].copy()
        sub[..., :3] = np.round(redraw(old, x0, y0, wthr))
        ch[y0:y1, x0:x1] |= np.abs(sub[..., :3] - old).max(-1) > 0
    return ch


def befores():
    """the zone's before copies: the assets as they are, the earlier zones' before copies laid over their boxes first"""
    sys.path.insert(0, os.path.join(ROOT, 'tools'))
    import redraw_zones as R
    x0, y0, x1, y1 = BOX
    for tag, f in (('city', 'layer_city_off'), ('unlit', 'street_unlit')):
        a = load(os.path.join(ASSETS, f + '.webp'))
        for n, c in R.ZONES.items():
            if n == 'gshutter': break
            bx0, by0, bx1, by1 = c['box']
            if bx0 < x1 and bx1 > x0 and by0 < y1 and by1 > y0:
                a[by0:by1, bx0:bx1] = load(os.path.join(EDITS, f'{n}_before_{tag}.webp')); print(tag, 'under', n)
        save(a[y0:y1, x0:x1], os.path.join(EDITS, f'gshutter_before_{tag}.webp')); print('gshutter_before_' + tag)


def preview(out):
    os.makedirs(out, exist_ok=True)
    x0, y0, x1, y1 = BOX
    wthr = weather(BOX)
    tiles = []
    for tag in ('city', 'unlit'):
        b = load(os.path.join(EDITS, f'gshutter_before_{tag}.webp'), 'RGB')
        a = redraw(b, x0, y0, wthr)
        for im in (b, a): tiles.append(Image.fromarray(np.clip(np.round(im), 0, 255).astype(np.uint8)).resize(((x1 - x0) * 8, (y1 - y0) * 8), Image.NEAREST))
    c = Image.new('RGB', (sum(t.width + 8 for t in tiles), tiles[0].height))
    x = 0
    for t in tiles: c.paste(t, (x, 0)); x += t.width + 8
    c.save(os.path.join(out, 'gshutter_x8.png'))


if __name__ == '__main__':
    if '--befores' in sys.argv: befores()
    elif '--input' in sys.argv: make_input()
    elif '--ask' in sys.argv: ask(sys.argv[sys.argv.index('--ask') + 1])
    elif '--preview' in sys.argv: preview(sys.argv[sys.argv.index('--preview') + 1])
