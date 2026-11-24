#!/usr/bin/env python3
"""The strip between Ichiraku and the arcade's door, under the arcade's eave: Ichiraku's building's own end wall
(concrete) and, beside the arcade's door, its tiled panel (small square glazed tiles), their materials from one
generated sheet and the light that really reaches them on its hours.

    (a module: tools/redraw_zones.py's zone 'arcwall' calls draw(city, unlit, box) on the street as the zones before it
     leave it, before the fronts' feet (tools/facade_foot.py's footR lays their plinths); it writes the strip's light,
     assets/arcade_post_light.webp, and the arcade's spill without its old stipple on these walls,
     assets/arcade_spill.webp: the same bytes each time)
    python3 tools/arcade_shade.py --input        the sheet's layout guide (tools/src/edits/arcwall_in.webp)
    python3 tools/arcade_shade.py --ask          the sheet asked of the image model, once (OpenRouter's key in
                                                 ~/.config/openrouter/key; about 0.25 $): arcwall_prompt.txt on arcwall_in.webp,
                                                 its answer tools/src/edits/arcwall_draft.webp; the walls are drawn from the
                                                 saved answer, never a new call

What was there: two near-black bands at every hour, their textures drawn in code (vertical streaks; a grid of squares).

The geometry (tools/facade_foot.py's camera: VP (700, 615), f 960 px, the eye 1.26 m over the sidewalk; the fronts on the
right 4.45 m from the eye's line): the arcade is set back 30 cm from Ichiraku's front, so
- A (x 1267..1301): Ichiraku's building's own near end wall, a frontal plane at Z_A 7.55 m (the plane Naruto's end wall is
  over the arcade's roof), the 30 cm the set-back arcade leaves in view, from Ichiraku's arris (x 1266) to the inside
  corner and the downpipe (x 1302..1306), from under the arcade's eave (y 410) to its level foot (row 775, where
  facade_foot lays its plinth);
- B (x 1321..1350): the arcade's front between its post (x 1310..1319, the painter's, kept) and its door's frame (x 1351..,
  kept), on the plane X 4.75 m (Z 7.34..7.00 m), from under the GAME sign's fascia to its foot (the plinth facade_foot lays).
Their pixels: the painter's navy fill there (the zone 'arcgap'), each column's run (as before).

The materials (R28; the owner, 23/11: generate an image, if only for the texture), from one sheet the image model painted
on a layout guide (tools/src/edits/arcwall_*: in, prompt, draft): a strip of weathered Japanese cast concrete (rain streaks
from the top, mottling, a damp foot) and a wall of 100 mm square glazed tiles ("hyaku-kaku", kiln-varied deep blue-green
glaze, light grey cement joints), both square on in flat daylight. Brought into the street:
- A: the concrete's own picture over A's metres (Z_A's plane: X across, h up; 0.3 m of the sheet's 1.5 m), each scene
  pixel the mean of the sheet's pixels it covers; only its relief kept (its luminance over its mean: its mottling whole,
  its long rain streaks at a share, as a thin dark streak reads as a joint at 1:1 in the dark; the damp foot's large fall
  compressed), on the end wall's own tone (R29: the plane over the arcade's roof, END_REF; its grain about a fifth of its
  tone there), darker under the eave, a little lighter low down (the paving's light), darker into the inside corner;
- B: the tiles on the street's rays: courses of 0.10 m from the plinth's top, columns of 0.10 m from the door's frame
  (the cut tile by the post), each joint one crisp pixel (its column; its row on each column), each tile's face the mean
  of its own tile in the sheet (a block of the sheet's grid, kept in its order: a tile's kiln colour, its glaze's cloud,
  the grime lower down), the joints the sheet's grout there; the night's tones the arcade's (its post's light, a deep
  teal glaze, the grout a step lighter), in the shade of the fascia over it and a little lighter low down.
Both layers the same (no light of their own: the power cut changes nothing there).

Their light (assets/arcade_post_light.webp, three additive cells, street.js APL: each its source's own, so it lives,
flickers and goes out with it; out in the power cut, red in the red night), what really reaches them:
- 'sign': the GAME sign's tubes, its invader and its bulbs (assets/arcade_sign.webp, row 0 and the bulbs at their mean),
  each lit pixel a small source on the board (3 cm proud of the fascia: the invader's LED cells flush on it, lighting
  only in front of it, their cosine; the neon tubes on their standoffs and the bulbs in their sockets 3 cm off it, all
  round), each wall point's light cos / r^2 where neither the board nor the downpipe stands between: A faces it (its
  upper part, under the eave's soffit, which shades the corner where they meet), the post and B take it at a grazing
  angle under the board; on the tiles the light each surface takes (the face at grazing incidence, the cushioned top
  edge of each tile tilted up to the sign much more, the joints recessed), the colours each reflects (the teal glaze
  little of the pink), and on each tile's upper near corner, where its glaze's curve sends the sign's image to the eye,
  a glint (one pixel, the sources it can mirror, fainter with their distance); the light added in linear terms over
  each pixel's own tone (a little light shows on a dark wall); the sign's own glow (assets/arcade_sign_glow.webp,
  tools/arcade_sign.py) run on past its box's bottom edge (y 470) over these walls, where it stopped short, scaled to
  its last row; with the sign (its glow's level: the arcade's hours, its tubes' stutter);
- 'lamp': Ichiraku's right wall lamp hangs 0.6 m behind the end wall's plane (Z 7.8 against 7.55): its fan cannot fall on
  A's face; only the arris and the end wall's first column, the corner's rounding, catch it (a share of the fan on the
  boards' corner column, tools/ichiraku_wall.py); with that lamp's glow (the shop's hours, the zone's power);
- 'pink': the arcade's room lights its lit sill and the wet paving before its door (the arcade canvas's sill, a stone
  step proud of the wall, and the floor's spill); the door stands in B's own plane, so none of the room's light falls on
  B directly: what reaches it is what that sill and that paving send back, faint, strongest low by the frame, more on
  A's lower part, which faces them; with the arcade's spill (its hours, its flicker, its power).
And the arcade's spill on the sidewalk (assets/arcade_spill.webp) loses the stipple it laid on these walls (an old
fan of the room's light on a flank there, R10): its pixels over A, the post and B cleared, from its before copy
(tools/src/edits/arcwall_spill_before.webp).
Needs Pillow, numpy, scipy.
"""
import base64
import io
import json
import os
import sys
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter, map_coordinates

sys.dont_write_bytecode = True
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDITS = os.path.join(ROOT, 'tools', 'src', 'edits')
ASSETS = os.path.join(ROOT, 'assets')
MODEL = 'openai/gpt-5.4-image-2'

BOX = (1262, 400, 1360, 792)                     # the zone (redraw_zones.py 'arcwall')
SLABS = [(1266, 1303), (1319, 1357)]             # A, B: the columns searched for the painter's navy fill (end excluded)
VP, F, ES = (700.0, 615.0), 960.0, 1.26          # the camera (tools/facade_foot.py's), the eye over the sidewalk
XA = 4.45                                        # m: Ichiraku's front (A's near edge, its arris)
Z_A = F * XA / (1265.5 - VP[0])                  # A's plane (7.554 m)
XB = 4.75                                        # m: the arcade's front (the post's, B's, its door's plane)
FOOT_A = 775                                     # A's foot (its level row: facade_foot's endA), its rows above
END_REF = (1300, 300, 1356, 345)                 # the end wall just over the arcade's roof: A's plane, its tone
POST = (1307, 1321)                              # the post's columns (the painter's, kept; it takes the light)
FRAME = 1351                                     # the door's frame's first column (kept): B's tiles counted from it
TILE = 0.10                                      # m: a tile's module (a 95 mm tile and its joint)
H0 = 0.06                                        # m: the first course's foot (the plinth's top, facade_foot's 'arcade')

# ---- the sheet (tools/src/edits/arcwall_draft.webp, 1024 x 1024): its two panels as the answer drew them
SHEET = 1024
PANELS = [(17, 17, 507, 1007), (517, 17, 1007, 1007)]   # the guide's panels (the concrete, the tiles)
GRID = (15, 30)                                  # the guide's tiles (across, down)
CONC = dict(x=(15, 505), floor=983.0, top=12.0, u0=172.0)   # the concrete as drawn: its columns, its foot's row (the
                                                 # pavement's line under it), its top; the strip of it A shows from u0
                                                 # (its pixels a metre: (floor - top) / 3 m both ways)
GROUT_X = [549, 580, 612, 643, 675, 707, 738, 770, 802, 833, 865, 896, 927, 958, 988]   # the joints' centres, found
GROUT_Y0, GROUT_DY, GROUT_NY = 48.0, 36.33, 27   # on the answer (its tiles 31.4 x 36.3 px; the courses from row 48)
I0 = 5                                           # the sheet's tile column B's nearest column takes (then the next ones)

# ---- the night's tones
K_A = dict(relief=1.0, streak=0.4, streak_len=24.0, fall=0.3, eave=0.86, low=1.08, corner=0.84, arris=1.18)
                                                 # A: the concrete's relief's share (the painter's own grain on the end wall
                                                 # over the roof: about a fifth of its tone), its long rain streaks' share
                                                 # and length (rows), its large fall's (the damp foot), the shade under the
                                                 # eave at the top, the paving's light at the foot, the inside corner, the
                                                 # arris column
TILE_NIGHT = (5.0, 15.0, 23.0)                   # B: a tile's face in the night (the arcade's teal, its glaze deep)
GROUT_NIGHT = (10.0, 19.0, 29.0)                 # B: its grout (light cement: a step lighter than the glaze)
K_B = dict(var=1.0, top=0.88, low=1.06, edge=0.9)   # B: the sheet's variation's share, the fascia's shade at the top,
                                                 # the paving's light low down, the darker first column by the post

# ---- the light
APL_CELLS = {'sign': (1262, 400, 90, 392), 'lamp': (1265, 480, 3, 296), 'pink': (1262, 420, 90, 372)}
                                                 # each cell's box in the street (x, y, w, h), side by side in the atlas
BOARD = dict(x=4.717, h=(2.5635, 2.84), z=(6.03, 7.23), led=0.005, tube=0.03)
                                                 # the sign's board in this camera (tools/arcade_sign.py's fascia 4.30 m is
                                                 # this camera's 4.75): its face 3 cm proud, its bottom and top, its far and
                                                 # near ends; how far off its face its light sits (the invader's LED cells
                                                 # flush, the neon tubes on their standoffs and the bulbs in their sockets)
PIPE = dict(x=4.728, z=7.525, r=0.021)          # the downpipe in the inside corner (a vertical cylinder)
GAMMA = 2.2                                      # (light added in linear terms over each pixel's own tone, then back)
SIGN = dict(gain=2.0, bevel=0.6, grout=0.55, spec=0.9, soffit=(8.0, 0.35), glow_to=640)
                                                 # the tubes' radiance over what the screen shows of them (a tube is far
                                                 # brighter than white); a tile's top edge's tilt (its normal's h share);
                                                 # the joints' share (recessed: in their own shade at this angle); the
                                                 # glaze's mirror (a corner's curve, its Fresnel); the eave's soffit over A
                                                 # (the rows its corner shades, the light at its top); the glow carried on to
                                                 # this row
RHO = dict(conc=128.0, grout=117.0, tile=(10.0, 72.0, 80.0))   # the sheet's tones (its concrete, its grout, its tiles):
                                                 # what each surface reflects, linear
LAMP = dict(arris=0.42, first=0.14)              # Ichiraku's lamp: the share of its fan on the boards' corner column the arris
                                                 # (x 1266) and A's first column take
PINK = dict(gain=3.0, sill=(4.55, 4.75, 0.05), door=(6.03, 6.87), reach=0.7, spread=0.25, floor=(36.0, 18.0, 40.0))
                                                 # the room's light sent back: over what the screen shows (its room's floor
                                                 # and its sill are brighter than they read); the sill (X from, to; its top,
                                                 # m), the doorway (Z), the paving's lit reach out from the sill and past the
                                                 # door's far edge (m); the room's light on the paving (the floor inside it)
SAMP = 4                                         # sub-samples a pixel (each way)


def load(p, mode='RGBA'):
    return np.asarray(Image.open(p).convert(mode)).astype(float)


def save(a, p):
    Image.fromarray(np.clip(np.round(a), 0, 255).astype(np.uint8), 'RGBA' if a.shape[-1] == 4 else 'RGB').save(
        p, 'WEBP', lossless=True, quality=100, method=6, exact=True)


def lum(a):
    return a @ np.array([0.299, 0.587, 0.114])


# ---- the draft
def guide():
    """tools/src/edits/arcwall_in.webp: the sheet's layout (a grey ground, the two panels, the tiles' grid lines)."""
    im = Image.new('RGB', (SHEET, SHEET), (118, 118, 118)); d = ImageDraw.Draw(im)
    (a0, b0, a1, b1), (c0, d0, c1, d1) = PANELS
    d.rectangle([a0, b0, a1 - 1, b1 - 1], fill=(150, 150, 146))
    d.rectangle([c0, d0, c1 - 1, d1 - 1], fill=(38, 92, 96))
    for i in range(1, GRID[0]):
        x = int(round(c0 + i * (c1 - c0) / GRID[0])); d.line([x, d0, x, d1 - 1], fill=(170, 172, 168), width=3)
    for j in range(1, GRID[1]):
        y = int(round(d0 + j * (d1 - d0) / GRID[1])); d.line([c0, y, c1 - 1, y], fill=(170, 172, 168), width=3)
    save(np.asarray(im).astype(float), os.path.join(EDITS, 'arcwall_in.webp'))
    print('arcwall_in.webp', SHEET, 'x', SHEET)


def ask():
    """The sheet asked of the image model (one call), from arcwall_in.webp and arcwall_prompt.txt: arcwall_draft.webp."""
    import urllib.request
    im = Image.open(os.path.join(EDITS, 'arcwall_in.webp')).convert('RGB')
    buf = io.BytesIO(); im.save(buf, 'PNG')
    key = open(os.path.expanduser('~/.config/openrouter/key')).read().strip()
    content = [{"type": "text", "text": open(os.path.join(EDITS, 'arcwall_prompt.txt')).read().strip()},
               {"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()}}]
    body = {"model": MODEL, "modalities": ["image", "text"], "usage": {"include": True}, "messages": [{"role": "user", "content": content}]}
    req = urllib.request.Request('https://openrouter.ai/api/v1/chat/completions', data=json.dumps(body).encode(),
                                 headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'})
    d = json.loads(urllib.request.urlopen(req, timeout=900).read())
    url = d['choices'][0]['message']['images'][0]['image_url']['url']
    Image.open(io.BytesIO(base64.b64decode(url.split(',', 1)[1]))).save(os.path.join(EDITS, 'arcwall_draft.webp'), 'WEBP',
                                                                         lossless=True, quality=100, method=6)
    print('arcwall_draft.webp saved; cost', d.get('usage', {}).get('cost'), '$')


def sheet():
    return load(os.path.join(EDITS, 'arcwall_draft.webp'), 'RGB')


def sample(img, ys, xs):
    """img (H, W, 3) bilinear at float rows ys, columns xs (same shape): (..., 3)"""
    return np.stack([map_coordinates(img[..., c], [ys, xs], order=1, mode='nearest') for c in range(3)], -1)


# ---- the camera
def z_b(x):
    return F * XB / (np.asarray(x, float) - VP[0])            # (x: a column's edge or a pixel's centre, + 0.5)


def h_at(y, z):
    return ES + (VP[1] - np.asarray(y, float)) * z / F         # (y: a row's centre, + 0.5)


def row_of(h, z):
    return VP[1] - (h - ES) * F / z                            # (a row's position, its centre at k + 0.5)


# ---- the walls' pixels
def slab_mask(city, box):
    """A's and B's pixels: the painter's navy fill (r, g small, b 5..16) in SLABS's columns, each column's run filled;
    A down to its level foot."""
    x0, y0, x1, y1 = box
    c = city[y0:y1, x0:x1, :3]
    nav = (c[..., 0] <= 3.5) & (c[..., 1] <= 6.5) & (c[..., 2] >= 5) & (c[..., 2] <= 16.5)
    a_m = np.zeros(nav.shape, bool); b_m = np.zeros(nav.shape, bool)
    for k, (a, b) in enumerate(SLABS):
        for x in range(a, b):
            ys = np.where(nav[:, x - x0])[0]
            ys = ys[ys + y0 >= 405]
            if len(ys) <= 20: continue
            bot = FOOT_A - y0 if k == 0 else ys.max() + 1
            (a_m if k == 0 else b_m)[ys.min():bot, x - x0] = True
    return a_m, b_m


def post_mask(box, a_m, b_m):
    """the post and the dark line either side of it (the painter's, kept): the light only, from A's top to its foot"""
    x0, y0, x1, y1 = box
    yy, xx = np.mgrid[y0:y1, x0:x1]
    top = y0 + np.nonzero(a_m.any(1))[0].min()
    foot = VP[1] + 0.283 * (xx + 0.5 - VP[0]) - 9.5            # (facade_foot's 'arcade' foot ray)
    return (xx >= POST[0]) & (xx < POST[1]) & (yy >= top) & (yy < foot) & ~a_m & ~b_m


# ---- A: the concrete
def concrete(a_m, box):
    """A's concrete: each pixel's relief (mean 1) from the sheet's concrete over its footprint in metres."""
    x0, y0, x1, y1 = box
    S = sheet(); L = lum(S)
    cx0, cx1 = CONC['x']; ppm = (CONC['floor'] - CONC['top']) / 3.0
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(float)
    acc = np.zeros(xx.shape)
    for j in range(SAMP):
        for i in range(SAMP):
            px = xx + (i + 0.5) / SAMP; py = yy + (j + 0.5) / SAMP
            X = (px - VP[0]) * Z_A / F; h = ES + (VP[1] - py) * Z_A / F
            u = CONC['u0'] + (X - XA) * ppm; v = CONC['floor'] - h * ppm
            acc += map_coordinates(L, [v, u], order=1, mode='nearest')
    L_a = acc / SAMP ** 2
    m = a_m
    big = gaussian_filter(np.where(m, L_a, L_a[m].mean()), 30.0)       # (the large fall: the damp foot)
    rel = L_a / np.maximum(big, 1.0) - 1.0
    streak = gaussian_filter(np.where(m, rel, 0.0), (K_A['streak_len'], 0.0))   # (the rain's long streaks: at 1:1 in the
    mottle = rel - streak                                                        # dark a thin dark streak reads as a joint)
    fall = big / L_a[m].mean()
    return (1.0 + K_A['relief'] * (mottle + K_A['streak'] * streak)) * (1.0 + K_A['fall'] * (fall - 1.0))


def tone_a(city, a_m, box, tex):
    """A in the night: the end wall's tone (R29) times its light (the eave's shade, the paving's, the inside corner), its
    relief; the arris column a hair lighter"""
    x0, y0, x1, y1 = box
    a, b, c, d = END_REF
    end = np.median(city[b:d, a:c, :3].reshape(-1, 3), 0)
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(float)
    top = y0 + np.nonzero(a_m.any(1))[0].min()
    v = np.clip((yy - top) / (FOOT_A - top), 0, 1)
    light = K_A['eave'] + (K_A['low'] - K_A['eave']) * np.sqrt(v)
    light *= 1.0 - (1.0 - K_A['corner']) * np.clip((xx - 1289) / 12.0, 0, 1) ** 1.5
    first = xx == SLABS[0][0] + 1
    light = np.where(first, light * K_A['arris'], light)
    return end[None, None, :] * (light * tex)[..., None]


# ---- B: the tiles
def tile_grid(b_m, box):
    """B's tiles on the street's rays: for each pixel its column (from the frame) and course (from the plinth), whether it
    is a joint, and its place in its tile's face (f across from its near joint, g up from its foot, each 0..1)"""
    x0, y0, x1, y1 = box
    H, W = b_m.shape
    xs = np.arange(x0, x1)
    z_frame = z_b(FRAME)                                       # (the frame's edge: the first joint)
    zc = z_b(xs + 0.5)                                         # (each column's centre)
    col_k = np.floor((zc - z_frame) / TILE).astype(int)        # (its tile column)
    vj = np.zeros(W, bool)                                     # a column a vertical joint: the first column (from the
    for i in range(1, W):                                      # frame) of each new tile column, one pixel
        vj[i] = col_k[i] != col_k[i - 1]
    vj[FRAME - 1 - x0] = False
    jm = np.zeros((H, W), bool); fpos = np.zeros((H, W)); gpos = np.zeros((H, W)); ci = np.zeros((H, W), int); cj = np.zeros((H, W), int)
    for i in range(W):
        if not b_m[:, i].any(): continue
        # the columns of this tile column: the span between its joints (exclusive)
        k = col_k[i]
        same = np.nonzero((col_k == k) & ~vj)[0]
        a, b = same.min(), same.max()
        f = (i - a + 0.5) / (b - a + 1)                        # (0 at its far side, 1 at its near side)
        f = 1.0 - f                                            # (from its near joint)
        z = zc[i]
        courses = np.arange(0, 40)
        rows = np.floor(row_of(H0 + courses * TILE, z)).astype(int) - y0   # each course line's row on this column
        ys = np.nonzero(b_m[:, i])[0]
        for y in ys:
            hrow = h_at(y + y0 + 0.5, z)
            c = int(np.floor((hrow - H0) / TILE))
            cj[y, i] = c; ci[y, i] = k
            if vj[i] or (c >= 0 and y == rows[c]) or (c + 1 < len(rows) and y == rows[c + 1]):
                jm[y, i] = True
            r_lo = rows[c] if c >= 0 else y                    # (its course's foot row) and top row
            r_hi = rows[c + 1] if c + 1 < len(rows) else y
            g = (r_lo - y - 0.5) / max(r_lo - r_hi - 1, 1)     # (0 at its foot, 1 at its top)
            fpos[y, i] = f; gpos[y, i] = np.clip(g, 0, 1)
    return dict(joint=jm & b_m, f=fpos, g=gpos, ci=ci, cj=cj, vj=vj)


def tiles(b_m, box, G):
    """B's tiles from the sheet: each tile's face the mean over each pixel's footprint of its own tile there (a block of
    the sheet's grid, in its order: column I0 + its column, course from the sheet's bottom), each joint the sheet's grout
    along it: each pixel's colour against the sheet's mean tile (its mean grout for a joint)."""
    S = sheet().astype(float)
    sat = S.max(-1) - S.min(-1)
    tile_px = sat >= 45; grout_px = ~tile_px
    tile_mean = np.median(S[17:1007, 520:1005][tile_px[17:1007, 520:1005]], 0)
    grout_mean = np.median(S[17:1007, 520:1005][grout_px[17:1007, 520:1005]], 0)
    gx = np.array(GROUT_X, float); gy = GROUT_Y0 + GROUT_DY * np.arange(GROUT_NY)
    H, W = b_m.shape
    out = np.ones((H, W, 3))
    for (y, i) in zip(*np.nonzero(b_m)):
        I = I0 + G['ci'][y, i]; J = GROUT_NY - 2 - G['cj'][y, i]
        I = int(np.clip(I, 0, len(gx) - 2)); J = int(np.clip(J, 0, GROUT_NY - 2))
        xr, xl = gx[I + 1], gx[I]                              # (its tile: the near joint on the right)
        yb, yt = gy[J + 1], gy[J]
        if G['joint'][y, i]:
            if G['vj'][i]:                                     # a vertical joint: the grout along the tile's near side
                sx = np.full(SAMP, xr); sy = yb - (G['g'][y, i] + (np.arange(SAMP) - 1.5) * 0.05) * (yb - yt)
            else:                                              # a course joint: along its foot
                sx = xr - (G['f'][y, i] + (np.arange(SAMP) - 1.5) * 0.04) * (xr - xl); sy = np.full(SAMP, yb)
            out[y, i] = ratio(sample(S, sy, sx).mean(0), grout_mean)
        else:
            fx = np.clip(G['f'][y, i] + (np.arange(SAMP)[None, :] - 1.5) * 0.06, 0.17, 0.83)   # (inside the tile's face:
            gy_ = np.clip(G['g'][y, i] + (np.arange(SAMP)[:, None] - 1.5) * 0.04, 0.17, 0.83)  # its joint is a pixel of its own)
            sx = xr - fx * (xr - xl) + 0 * gy_; sy = yb - gy_ * (yb - yt) + 0 * fx
            out[y, i] = ratio(sample(S, sy, sx).reshape(-1, 3).mean(0), tile_mean)
    return out


def ratio(c, mean):
    """c against mean: its luminance's ratio times its hue's (each channel's share), the hue's bounded (a kiln's
    variation, not another colour)"""
    lc, lm = max(lum(c), 1e-3), max(lum(mean), 1e-3)
    return lc / lm * np.clip((c / lc) / (mean / lm), 0.8, 1.25)


def tone_b(b_m, box, G, rel):
    """B in the night: the glaze's and the grout's tones times the sheet's variation (at a share), in the fascia's shade
    at the top and a little lighter low down"""
    x0, y0, x1, y1 = box
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(float)
    top = np.where(b_m.any(0), np.argmax(b_m, 0), 0)[None, :] + y0
    bot = FOOT_A + 10
    v = np.clip((yy - top) / (bot - top), 0, 1)
    light = K_B['top'] + (K_B['low'] - K_B['top']) * np.sqrt(v)
    first = np.zeros(b_m.shape, bool)
    cols = np.nonzero(b_m.any(0))[0]
    first[:, cols.min()] = True
    light = np.where(first, light * K_B['edge'], light)
    base = np.where(G['joint'][..., None], np.array(GROUT_NIGHT), np.array(TILE_NIGHT))
    var = 1.0 + K_B['var'] * (rel - 1.0)
    return base * var * light[..., None]


# ---- the light
def lin(v):
    return (np.clip(v, 0, None) / 255.0) ** GAMMA


def srgb(l):
    return 255.0 * np.clip(l, 0, None) ** (1.0 / GAMMA)


def sign_sources():
    """The sign's lit pixels as sources (assets/arcade_sign.webp: its tubes and invader, its bulbs at their mean): their
    points on the board (X, h, Z), their radiance (linear, times SIGN's gain) times their area (m^2), and which are flat
    (the LED cells, which light only in front of the board, as their cosine: a tube or a bulb lights all round)"""
    A = load(os.path.join(ASSETS, 'arcade_sign.webp'))
    bx, by = 1320, 356
    src = A[0:90, :, :3] + A[180:450].reshape(3, 90, 136, 4)[..., :3].mean(0)
    ys, xs = np.nonzero(lum(src) > 6)
    x = bx + xs + 0.5; y = by + ys + 0.5
    Z = F * BOARD['x'] / (x - VP[0]); h = ES + (VP[1] - y) * Z / F
    area = (Z / F) * (Z * Z / (F * BOARD['x']))
    c = src[ys, xs]
    cyan = (c[:, 1] > c[:, 0] + 40) & (c[:, 2] > c[:, 0] + 40)              # (the invader's LED cells)
    P = np.stack([BOARD['x'] - np.where(cyan, BOARD['led'], BOARD['tube']), h, Z], -1)
    return P, lin(c) * SIGN['gain'] * area[:, None], cyan


def blocked(P, S):
    """for points P (N, 3) and sources S (M, 3): (N, M) whether the board or the downpipe stands between them (the
    segment's stretch inside the board's depth crossing its face's rectangle, or its plan within the pipe's radius)"""
    sx, sh, sz = S[None, :, 0], S[None, :, 1], S[None, :, 2]
    dx, dh, dz = P[:, None, 0] - sx, P[:, None, 1] - sh, P[:, None, 2] - sz
    with np.errstate(divide='ignore', invalid='ignore'):
        lo = np.where(dx > 1e-6, (BOARD['x'] - sx) / dx, 2.0); hi = np.ones(dx.shape)
        for d, s, (a, b) in ((dh, sh, BOARD['h']), (dz, sz, BOARD['z'])):
            ta, tb = (a - s) / d, (b - s) / d
            t0 = np.where(np.abs(d) > 1e-9, np.minimum(ta, tb), np.where((s >= a) & (s <= b), -np.inf, np.inf))
            t1 = np.where(np.abs(d) > 1e-9, np.maximum(ta, tb), np.where((s >= a) & (s <= b), np.inf, -np.inf))
            lo = np.maximum(lo, t0); hi = np.minimum(hi, t1)
    out = lo <= hi
    qx, qz = PIPE['x'] - sx, PIPE['z'] - sz
    L2 = dx * dx + dz * dz
    t = np.clip((qx * dx + qz * dz) / np.maximum(L2, 1e-9), 0, 1)
    d2 = (qx - t * dx) ** 2 + (qz - t * dz) ** 2
    out |= (d2 < PIPE['r'] ** 2) & (t > 0) & (t < 0.999)
    return out


def irradiance(P, N, S, C, flat, chunk=500):
    """the light falling at points P (normals N) from sources S of radiance x area C: sum of C cos / r^2 (unblocked; a
    flat source's own cosine too)"""
    E = np.zeros((len(P), 3))
    for i in range(0, len(P), chunk):
        p, n = P[i:i + chunk], N[i:i + chunk]
        l = S[None] - p[:, None]
        r2 = (l * l).sum(-1); r = np.sqrt(r2)
        cos = np.clip((l * n[:, None]).sum(-1) / r, 0, None)
        cs = np.where(flat[None], np.clip(l[..., 0] / r, 0, None), 1.0)
        E[i:i + chunk] = (cos * cs / r2 * ~blocked(p, S)) @ C
    return E


def glints(P, S, C, flat, chunk=500):
    """a tile's upper near corner, its glaze's curve a small convex mirror: the sources whose image it sends to the eye
    (the normal halfway between the eye and the source tilted up and toward us, within the curve's 70 degrees of the
    face's), each its radiance x area / r^2 (the image's size on the curve)"""
    eye = np.array([0.0, ES, 0.0])
    E = np.zeros((len(P), 3))
    for i in range(0, len(P), chunk):
        p = P[i:i + chunk]
        l = S[None] - p[:, None]; r2 = (l * l).sum(-1); lh = l / np.sqrt(r2)[..., None]
        d = eye[None] - p; dh = d / np.linalg.norm(d, axis=-1, keepdims=True)
        n = lh + dh[:, None]; n /= np.linalg.norm(n, axis=-1, keepdims=True)
        ok = (n[..., 0] < -np.cos(np.radians(70))) & (n[..., 1] >= 0) & (n[..., 2] <= 0)
        cs = np.where(flat[None], np.clip(l[..., 0] / np.sqrt(r2), 0, None), 1.0)
        E[i:i + chunk] = (ok * cs * ~blocked(p, S) / r2) @ C
    return E


def glow_more(box):
    """the sign's glow (tools/arcade_sign.py's glow: its sources spread wide and soft) over this box past its own box's
    bottom edge (y 470), where it stops short over these walls"""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import arcade_sign as AS
    x0, y0, x1, y1 = box
    A = load(os.path.join(ASSETS, 'arcade_sign.webp'))
    tubes, bulb = A[0:90, :, :3], A[180:450].reshape(3, 90, 136, 4)[..., :3].mean(0)
    bulb_full = bulb * 3.0 / (1.0 + 2 * 0.33)                  # (the bulbs as the glow takes them: D['bulb'])
    gx0, gy0, gx1, gy1 = min(AS.GBOX[0], x0), AS.GBOX[1], AS.GBOX[2], max(AS.GBOX[3], y1)
    bx0, by0, bx1, by1 = AS.BOX
    src = np.zeros((gy1 - gy0, gx1 - gx0, 3))
    src[by0 - gy0:by1 - gy0, bx0 - gx0:bx1 - gx0] = tubes + 0.45 * bulb_full
    g = np.stack([0.5 * gaussian_filter(src[..., c], 8.0) + 2.4 * gaussian_filter(src[..., c], 22.0) for c in range(3)], -1)
    out = g[y0 - gy0:y1 - gy0, x0 - gx0:x1 - gx0]
    last = AS.GBOX[3] - 1                                       # (its last row, as the sprite has it: the free fall below
    have = load(os.path.join(ASSETS, 'arcade_sign_glow.webp'))  # scaled to it, column by column, so it runs on unbroken)
    k = np.ones((x1 - x0, 3))
    for i, x in enumerate(range(x0, x1)):
        if AS.GBOX[0] <= x < AS.GBOX[2]:
            k[i] = (have[last - AS.GBOX[1], x - AS.GBOX[0], :3] + 0.5) / (g[last - gy0, x - gx0] + 0.5)
    yy = np.mgrid[y0:y1, x0:x1][0]
    return np.where((yy > last)[..., None], out * k[None], 0.0)


def lights(base, a_m, b_m, p_m, G, rel, box):
    """the three cells' light over the box (additive, scene units): each light added in linear terms over each pixel's
    own tone (base: the walls unlit) and brought back"""
    x0, y0, x1, y1 = box
    H, W = a_m.shape
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(float)
    walls = a_m | b_m | p_m
    # each wall pixel's point and normal (A frontal, facing us; the post and B on the arcade's front, facing the street)
    Xp = np.where(a_m, (xx + 0.5 - VP[0]) * Z_A / F, XB)
    Zp = np.where(a_m, Z_A, z_b(xx + 0.5))
    hp = h_at(yy + 0.5, Zp)
    idx = np.nonzero(walls)
    P = np.stack([Xp[idx], hp[idx], Zp[idx]], -1)
    N = np.where(a_m[idx][:, None], [0.0, 0.0, -1.0], [-1.0, 0.0, 0.0])
    # what each surface reflects (linear): the sheet's concrete, glaze and grout, each pixel's own variation; the post
    # as its tone against B's tiles'
    rho = np.zeros((len(P), 3))
    am, bm, pm = a_m[idx], b_m[idx], p_m[idx]
    jb = G['joint'][idx] & bm; tb = bm & ~jb
    rho[am] = lin(RHO['conc'] * rel[idx][am])
    rho[tb] = lin(np.array(RHO['tile']) * rel[idx][tb])
    rho[jb] = lin(RHO['grout'] * rel[idx][jb]) * SIGN['grout']
    rho[pm] = lin(np.array(RHO['tile'])) * (base[idx][pm] + 1) / (np.array(TILE_NIGHT) + 1)
    b_lin = lin(base[idx])
    # the sign
    S, C, flat = sign_sources()
    E = irradiance(P, N, S, C, flat)
    topedge = b_m & ~G['joint'] & np.roll(G['joint'] & ~G['vj'][None, :], 1, 0)     # (each tile's cushioned top edge:
    te = topedge[idx]                                                                 # half its row tilted to the sign)
    bt = SIGN['bevel']; Nt = np.array([-np.sqrt(1 - bt * bt), bt, 0.0])
    E[te] = 0.5 * E[te] + 0.5 * irradiance(P[te], np.repeat(Nt[None], te.sum(), 0), S, C, flat)
    add = rho / np.pi * E
    corner = topedge & np.roll(G['vj'][None, :] & b_m, -1, 1)                       # (each tile's upper near corner)
    ci = corner[idx]
    sheen = np.clip(lum(rel[idx][ci]) - 0.85, 0, 0.6) / 0.6 + 0.35                  # (a paler, glossier tile catches more)
    add[ci] += SIGN['spec'] * glints(P[ci], S, C, flat) * sheen[:, None]
    top = y0 + np.nonzero(a_m.any(1))[0].min()                                      # (A's top: the eave's soffit over it
    n, k0 = SIGN['soffit']                                                         # shades the corner where they meet)
    add[am] *= (k0 + (1 - k0) * np.clip((idx[0][am] + y0 - top + 0.5) / n, 0, 1) ** 0.7)[:, None]
    sign = np.zeros((H, W, 3)); sign[idx] = srgb(b_lin + add) - base[idx]
    sign += glow_more(box) * walls[..., None] * (yy < SIGN['glow_to'])[..., None]
    # Ichiraku's right lamp: its fan on the boards' corner column, a share on the arris and A's first column
    IW = load(os.path.join(ASSETS, 'ichiraku_wall_light.webp'))
    cu, cw, chh, cx, cy = 46, 47, 306, 1220, 466                # (street.js IRWL's right cell)
    corner_col = IW[0:chh, cu + (1265 - cx), :3]
    lamp = np.zeros((H, W, 3))
    for x, k in ((1266, LAMP['arris']), (SLABS[0][0] + 1, LAMP['first'])):
        for yi in range(chh):
            y = cy + yi
            if y0 <= y < min(y1, FOOT_A) and (x == 1266 or a_m[y - y0, x - x0]):
                lamp[y - y0, x - x0] = k * corner_col[yi]
    # the room's light sent back by its lit sill and the wet paving before the door
    pink = np.zeros((H, W, 3)); pink[idx] = srgb(b_lin + rho / np.pi * pink_light(P, N)) - base[idx]
    return sign, lamp, pink


def pink_light(P, N):
    """the light falling at P from the arcade's lit sill and the wet paving before its door (the room's light sent back
    up): sum over their patches of L cos cos dA / r^2 (L: the room's floor's tone, linear, times PINK's gain; the sill
    at its whole, the paving falling off out from it and past the door's far edge)"""
    L0 = lin(np.array(PINK['floor'])) * PINK['gain']
    pts, rad = [], []
    za, zb_ = PINK['door']
    for Z in np.linspace(za, zb_ + PINK['spread'] * 2, 24):
        k_z = 1.0 if Z <= zb_ else np.exp(-(Z - zb_) / PINK['spread'])
        dZ = (zb_ + PINK['spread'] * 2 - za) / 23
        for X in np.linspace(PINK['sill'][0], PINK['sill'][1], 4):          # the sill's top
            pts.append((X, PINK['sill'][2], Z, 0.05 * dZ)); rad.append(L0 * k_z)
        for X in np.linspace(PINK['sill'][0] - 1.5, PINK['sill'][0], 12):   # the paving out from it
            d = PINK['sill'][0] - X
            pts.append((X, 0.0, Z, 0.125 * dZ)); rad.append(L0 * 0.4 * np.exp(-d / PINK['reach']) * k_z)
    Q = np.array(pts); R = np.array(rad)
    E = np.zeros((len(P), 3))
    for i in range(0, len(P), 800):
        p, n = P[i:i + 800], N[i:i + 800]
        l = Q[None, :, :3] - p[:, None]; r2 = (l * l).sum(-1); r = np.sqrt(r2)
        cw = np.clip((l * n[:, None]).sum(-1) / r, 0, None); cs = np.clip(-l[..., 1] / r, 0, None)
        E[i:i + 800] = (cw * cs / r2 * Q[None, :, 3]) @ R
    return E


# ---- the atlas
def atlas(cells, box):
    """the cells side by side (assets/arcade_post_light.webp), each its box of the street; additive (alpha 255 where it
    adds anything)"""
    x0, y0 = box[0], box[1]
    Wt = sum(c[2] for c in APL_CELLS.values()); Ht = max(c[3] for c in APL_CELLS.values())
    out = np.zeros((Ht, Wt, 4)); u = 0
    for name, (cx, cy, cw, ch) in APL_CELLS.items():
        a = np.zeros((ch, cw, 3))
        src = cells[name]
        ys0, xs0 = max(cy, y0), max(cx, x0); ys1, xs1 = min(cy + ch, y0 + src.shape[0]), min(cx + cw, x0 + src.shape[1])
        a[ys0 - cy:ys1 - cy, xs0 - cx:xs1 - cx] = src[ys0 - y0:ys1 - y0, xs0 - x0:xs1 - x0]
        a = np.clip(np.round(a), 0, 255)
        out[:ch, u:u + cw, :3] = a; out[:ch, u:u + cw, 3] = np.where(a.max(-1) > 0, 255, 0)
        u += cw
    return out


def spill_clean(walls, box):
    """assets/arcade_spill.webp without its stipple on these walls (from its before copy)"""
    p = os.path.join(EDITS, 'arcwall_spill_before.webp')
    if not os.path.exists(p): save(load(os.path.join(ASSETS, 'arcade_spill.webp')), p)
    A = load(p); sx, sy = 1100, 700
    x0, y0 = box[0], box[1]
    for (y, x) in zip(*np.nonzero(walls)):
        X, Y = x + x0 - sx, y + y0 - sy
        if 0 <= X < A.shape[1] and 0 <= Y < A.shape[0]: A[Y, X] = 0
    save(A, os.path.join(ASSETS, 'arcade_spill.webp'))


# ---- the zone
def build(city, box):
    a_m, b_m = slab_mask(city, box)
    p_m = post_mask(box, a_m, b_m)
    texA = concrete(a_m, box)
    G = tile_grid(b_m, box)
    rel = tiles(b_m, box, G)
    out = np.zeros(a_m.shape + (3,))
    out[a_m] = tone_a(city, a_m, box, texA)[a_m]
    out[b_m] = tone_b(b_m, box, G, rel)[b_m]
    out = np.clip(np.round(out), 0, 255)
    x0, y0, x1, y1 = box
    base = np.where((a_m | b_m)[..., None], out, city[y0:y1, x0:x1, :3])
    relA = np.where(a_m[..., None], texA[..., None], rel)
    sign, lamp, pink = lights(base, a_m, b_m, p_m, G, relA, box)
    return dict(a=a_m, b=b_m, p=p_m, out=out, G=G, sign=sign, lamp=lamp, pink=pink)


def draw(city, unlit, box=BOX):
    """The zone: both layers changed in place over A and B, the light written; returns what changed (whole scene)."""
    x0, y0, x1, y1 = box
    H, W = city.shape[:2]
    R = build(city, box)
    m = R['a'] | R['b']
    for L in (city, unlit):
        sub = L[y0:y1, x0:x1]; sub[..., :3][m] = np.clip(np.round(R['out'][m]), 0, 255); sub[..., 3][m] = 255
    save(atlas({'sign': R['sign'], 'lamp': R['lamp'], 'pink': R['pink']}, box), os.path.join(ASSETS, 'arcade_post_light.webp'))
    spill_clean(m | R['p'], box)
    ch = np.zeros((H, W), bool); ch[y0:y1, x0:x1] = m
    return ch


if __name__ == '__main__':
    if '--input' in sys.argv: guide()
    elif '--ask' in sys.argv: ask()
    else: print(__doc__)
