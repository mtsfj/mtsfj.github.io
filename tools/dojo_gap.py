#!/usr/bin/env python3
"""The narrow gap between the dojo and the dagashi-ya: what the street's camera really sees in it, the dagashi-ya's house's
end wall face on, in the gap's own dark.

    (a module: tools/redraw_zones.py's zone 'dojogap', the last, calls draw(city, unlit, box) on the street as the zones
     before it leave it: both layers in its box, the same bytes each time)
    python3 tools/dojo_gap.py --before       once: the zone's before crops (tools/src/edits/dojogap_before_*.webp) and the
                                             painter's boards of that wall upstairs (dojogap_boards.webp)
    python3 tools/dojo_gap.py --preview DIR  both layers before and after, x1 and x6 (nothing written)

What was there: between the dojo's corner post (x 107) and the downpipe (x 132..139), from under the tree's leaves (row
471) down to the dojo's step, one flat near-black (1, 3, 10) in both layers, at every hour: a slab, no material, no light.

What the camera sees (the street's camera, tools/facade_foot.py's: VP (700, 615), f 960 px, the eye 1.41 m over the road,
the sidewalk 0.15 m up; the left fronts 5.5 m left of the eye's line): the dojo's corner is on the street's line at
8.91 m, the dagashi-ya's (behind the downpipe) at 9.42 m: a gap 0.51 m wide, running straight back from the street. Its
near wall (the dojo's house's side) faces away from the eye; its far wall, the dagashi-ya's house's end wall (Kirua's
house, its end wall seen upstairs over the dojo's roof: tools/kirua_house_side.py), faces the eye, a frontal plane at
9.42 m (102 px a metre): its lines level, not on the street's rays. Past the dojo's post the eye sees only its first
0.30 m (the ray grazing the post meets it there), so no fence, no back, no AC unit: the gap's depth is out of sight
behind the post; its floor lies behind the dojo's step (its top up to row 737), but for three columns by the downpipe.
So the slab is that wall: 24 columns of it, from the sidewalk (row 743.4: level) up under the eaves.

What it is now:
- the wall: Kirua's boards, the painter's own from that very wall upstairs (BOARDS: one period of four boards, his laps
  at rows 90, 109, 117 and 131 there, tiled down on its phase, his columns back and forth), each row made level and crisp
  (its median across), his grain along each board kept softer; one material from the roof to the foot (R25);
- under them a mortar base course 0.30 m high (a wooden house's sill on its base, the splash skirt), its drip edge one
  lit row, its shadow under it, a fixed fine grain, its foot behind the dojo's step (the crease seen by the downpipe);
- its light: only what reaches it, the street's night through the gap's mouth (its view factor, each pixel's, to the
  opening between the two corners, from the step's top to the eaves, the downpipe standing in it near the wall, plus
  what the dojo's side wall sends back): one tone a plane (R29) under that light, a little darker toward the dojo's
  post (deeper in), in the downpipe's shade beside it, under the eaves at the top; as dark as the place (its boards
  at a luminance of 8, the fronts beside it 15 to 20), in the street's navy on the boards' rose. The shops' lights do
  not reach it: the shoji, the dagashi-ya's window and the drinks machines face the street, and their pools on the
  pavement at the mouth (2 to 10) send back less than a level onto it;
- the layers: the same wall in both (no light of the street's power falls in the gap), so the dojo's shut picture (its
  zone, x < 112) and the power cut show it alike; the red night grades it as the street; the wet pavement before the
  mouth mirrors it live. Needs Pillow, numpy, scipy.
"""
import os
import sys
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDITS = os.path.join(ROOT, 'tools', 'src', 'edits')
ASSETS = os.path.join(ROOT, 'assets')
BOX = (108, 436, 132, 746)                       # the zone (redraw_zones.py 'dojogap'): the gap's columns, the leaves to the floor
LUM = np.array([0.299, 0.587, 0.114])
# the street's camera (tools/facade_foot.py's): VP (700, 615), f 960, the eye 1.41 m over the road, the sidewalk 0.15 m
# up, the left fronts 5.5 m left of the eye's line (their feet on the ray v 0.229)
VPX, VPY, F, ES, XL = 700.0, 615.0, 960.0, 1.26, 5.5
CORNER_D, CORNER_K = 139.5, 107.5                # the corners on the street's line: the dagashi-ya's (behind the downpipe),
Z_W = F * XL / (VPX - CORNER_D)                  # the dojo's post's; the end wall's plane (m) and the gap's width
GAP_W = Z_W - F * XL / (VPX - CORNER_K)
Y_FOOT = VPY + F * ES / Z_W                      # (the sidewalk's level on the end wall: a level row, the wall faces us)
WALL_X = (108, 131)                              # the wall's columns, the dojo's post to the downpipe
LEAVES, FLOOR = 471, 743                         # (from under the tree's leaves; the crease at the floor, beside the step)
MOUTH = (0.17, 3.1)                              # the mouth's opening (m): over the dojo's step, under the eaves
PIPE = (0.03, 0.10, 0.8)                         # the downpipe in it: from its gap to the wall to its far side (m), its share
NZ, NH = 24, 60                                  # (the opening's points)
FILL = 0.04                                      # (what the dojo's side wall, lit by the mouth, sends back)
REF, LEVEL = (124, 1.2), 8.0                     # the boards' mean luminance at this column, this height (m)
BOARDS, BOARDS_X = (57, 90), (142, 157)          # the painter's boards upstairs: one period (rows) from its first row; columns
BOARD_SIG, BOARD_CLIP, BOARD_K = 5.0, (0.3, 1.8), 0.85   # (their light taken off at this scale; their contrast kept)
FINE = (0.2, 0.6)                                # (the grain along a board: its range, the share kept)
BASE_H = 0.30                                    # the base course under the boards (m), its drip edge on top
CH_BOARDS = np.array([1.0, 0.8, 2.0])            # the boards' colour at luminance 1: the street's navy on Kirua's rose boards
CH_BASE = np.array([0.903, 0.945, 1.539])        # the base's: the street's navy on grey mortar
BASE_K, EDGE_K, DRIP_SHADE, CREASE = 1.15, 1.8, 0.7, 0.55
GRAIN = 0.05                                     # (a fixed fine grain on the mortar)


def load(p, mode='RGBA'):
    return np.asarray(Image.open(p).convert(mode)).astype(float)


def save(a, p):
    Image.fromarray(np.clip(np.round(a), 0, 255).astype(np.uint8), 'RGBA' if a.shape[-1] == 4 else 'RGB').save(
        p, 'WEBP', lossless=True, quality=100, method=6, exact=True)


# ---- the street's camera on the gap
def depth(x):
    """how far into the gap (m, from its mouth on the street's line) the end wall is at column x's middle"""
    return (CORNER_D - (np.asarray(x, float) + 0.5)) * Z_W / F


def height(y):
    """the height (m) over the sidewalk of row y's middle on the end wall"""
    return (Y_FOOT - (np.asarray(y, float) + 0.5)) * Z_W / F


def mouth_light(d, h):
    """the share of the street's light a point of the end wall gets through the gap's mouth (its view factor to the
    opening, a rectangle in the street's line between the two corners, from the step's top to the eaves, the downpipe
    standing in it near the wall), plus what the dojo's side wall sends back (FILL)"""
    d = np.atleast_1d(np.asarray(d, float)); h = np.atleast_1d(np.asarray(h, float))
    zs = (np.arange(NZ) + 0.5) / NZ * GAP_W                    # (the opening's points: their distance from the end wall,
    hs = MOUTH[0] + (np.arange(NH) + 0.5) / NH * (MOUTH[1] - MOUTH[0])   # and their height)
    dA = (GAP_W / NZ) * ((MOUTH[1] - MOUTH[0]) / NH)
    pass_ = np.where((zs >= PIPE[0]) & (zs < PIPE[1]), 1.0 - PIPE[2], 1.0)
    out = np.zeros(np.broadcast(d, h).shape)
    D, Hh = np.broadcast_arrays(d, h)
    for i in np.ndindex(D.shape):
        dz = zs[:, None]; dy = hs[None, :] - Hh[i]; dx = D[i]
        r2 = dx * dx + dz * dz + dy * dy
        out[i] = np.sum(pass_[:, None] * (dz / np.sqrt(r2)) * (dx / np.sqrt(r2)) / (np.pi * r2)) * dA
    return out + FILL


def board_rows():
    """the painter's boards of this very wall (Kirua's house's end wall, under its roof: tools/kirua_house_side.py's SIDE),
    their light taken off: each pixel's luminance over its own low frequencies (one period of boards, tiled round)"""
    src = load(os.path.join(EDITS, 'dojogap_boards.webp'), 'RGB')
    L = src @ LUM
    t = np.concatenate([L, L, L], 0)
    from scipy.ndimage import gaussian_filter
    low = gaussian_filter(t, (BOARD_SIG, 50.0), mode='wrap')[len(L):2 * len(L)]
    rel = np.clip(L / np.maximum(low, 1.0), *BOARD_CLIP) ** BOARD_K
    row = np.median(rel, 1, keepdims=True)                     # (each row level: the laps straight across, crisp; the
    fine = np.clip(rel / row, 1 - FINE[0], 1 + FINE[0])        # painter's grain along each board kept, softer)
    rel = row * (1 + FINE[1] * (fine - 1))
    return rel / rel.mean()


def board_at(rel, xs, ys):
    """the boards' relative light at scene columns xs, rows ys: their rows continue the wall's upstairs (one period, its
    phase kept), their columns back and forth across the painter's"""
    p = rel.shape[0]; n = rel.shape[1]
    r = (np.asarray(ys) - BOARDS[1]) % p
    k = (np.asarray(xs) - WALL_X[0]) % (2 * n - 2)
    c = np.where(k < n, k, 2 * n - 2 - k)
    return rel[r, c]


def grain(xs, ys, seed):
    v = np.sin(np.asarray(xs) * 12.9898 + np.asarray(ys) * 78.233 + seed * 37.719) * 43758.5453
    return 1.0 + GRAIN * ((v - np.floor(v)) * 2 - 1)


def gap_mask(P, x0, y0):
    """the gap's pixels in the crop P (RGB at (x0, y0)): its flat dark between the dojo's post and the downpipe, from
    under the tree's leaves down to the step (and, beside the step, to the floor), and between the leaves the same dark
    where it is one with it"""
    from scipy.ndimage import label
    H, W = P.shape[:2]; yy, xx = np.mgrid[0:H, 0:W]; X = xx + x0; Y = yy + y0
    r, g, b = P[..., 0], P[..., 1], P[..., 2]
    cols = (X >= WALL_X[0]) & (X <= WALL_X[1])
    flat = cols & (Y >= LEAVES) & (Y <= FLOOR) & (P @ LUM <= 5.0) & (b >= g + 3) & (r <= 3)
    holes = cols & (Y < LEAVES) & (r + g + b <= 7)
    lab, _ = label(flat | holes, np.ones((3, 3)))
    keep = np.unique(lab[flat]); keep = keep[keep > 0]
    return np.isin(lab, keep) & (flat | holes), X, Y


def redraw(P, x0, y0):
    """the end wall in the crop P (a layer's, RGB float at (x0, y0)); the new crop and the mask of what changed"""
    m, X, Y = gap_mask(P, x0, y0)
    out = P.copy()
    ys, xs = np.nonzero(m); Xs, Ys = xs + x0, ys + y0
    d, h = depth(Xs), height(Ys)
    ref = mouth_light(depth(REF[0]), REF[1])[0]
    lt = mouth_light(d, h) / ref * LEVEL                           # (the wall's luminance, its boards' mean)
    rel = board_rows()
    hb = h >= BASE_H                                               # the boards; under them the base course
    top = np.abs(h - BASE_H) < 0.5 * Z_W / F                       # (its drip edge, one row)
    col = np.where(hb[:, None], CH_BOARDS[None, :], CH_BASE[None, :])
    f = np.where(hb, board_at(rel, Xs, Ys), BASE_K * grain(Xs, Ys, 3))
    f = np.where(top, EDGE_K, f)
    f = np.where((~hb) & (np.abs(h - BASE_H + Z_W / F) < 0.5 * Z_W / F), f * DRIP_SHADE, f)   # (the drip's shadow under it)
    f = np.where(Ys >= FLOOR, f * CREASE, f)                                                  # (the crease at the floor)
    out[ys, xs] = np.clip(col * (lt * f)[:, None], 0, 255)
    return out, m


def draw(city, unlit, box=BOX):
    """tools/redraw_zones.py's zone 'dojogap': both layers, in place (the same wall: no light of the street's power falls
    in the gap); what changed"""
    x0, y0, x1, y1 = box; ch = np.zeros(city.shape[:2], bool)
    P = city[y0:y1, x0:x1, :3].copy()
    new, m = redraw(P, x0, y0)
    for a in (city, unlit):
        sub = a[y0:y1, x0:x1]; old = sub[..., :3].copy()
        sub[..., :3] = np.where(m[..., None], np.round(new), old)
        ch[y0:y1, x0:x1] |= np.abs(sub[..., :3] - old).max(-1) > 0
    return ch


def before():
    """once: the zone's before crops (the overlapping zones' own before crops, in their order, over the layers' pixels
    where no zone is) and the painter's boards of the end wall upstairs (dojogap_boards.webp)"""
    sys.path.insert(0, os.path.join(ROOT, 'tools'))
    import redraw_zones as R
    x0, y0, x1, y1 = BOX
    for tag, f in (('city', 'layer_city_off.webp'), ('unlit', 'street_unlit.webp')):
        a = load(os.path.join(ASSETS, f))[y0:y1, x0:x1].copy()
        for name, cfg in R.ZONES.items():
            if name == 'dojogap': continue
            b = cfg['box']
            ox0, oy0, ox1, oy1 = max(b[0], x0), max(b[1], y0), min(b[2], x1), min(b[3], y1)
            if ox0 >= ox1 or oy0 >= oy1: continue
            z = load(os.path.join(EDITS, '%s_before_%s.webp' % (name, tag)))
            a[oy0 - y0:oy1 - y0, ox0 - x0:ox1 - x0] = z[oy0 - b[1]:oy1 - b[1], ox0 - b[0]:ox1 - b[0]]
        save(a, os.path.join(EDITS, 'dojogap_before_%s.webp' % tag))
        print('dojogap_before_%s.webp' % tag, a.shape[1], 'x', a.shape[0])
    c0, c1 = BOARDS_X; r0, r1 = BOARDS[1], BOARDS[1] + BOARDS[0]
    save(load(os.path.join(ASSETS, 'layer_city_off.webp'))[r0:r1, c0:c1, :3], os.path.join(EDITS, 'dojogap_boards.webp'))
    print('dojogap_boards.webp', c1 - c0, 'x', r1 - r0)


def preview(out):
    """both layers' box before and after (from the current layers), x1 and x6"""
    os.makedirs(out, exist_ok=True)
    x0, y0, x1, y1 = BOX
    tiles = []
    for f in ('layer_city_off.webp', 'street_unlit.webp'):
        b = load(os.path.join(ASSETS, f))[y0:y1, x0:x1, :3]
        a, m = redraw(b, x0, y0)
        tiles += [b, a]
    for s in (1, 6):
        row = np.concatenate([np.concatenate([t, np.full((t.shape[0], 2, 3), 255.0)], 1) for t in tiles], 1)
        Image.fromarray(np.clip(np.round(row), 0, 255).astype(np.uint8)).resize((row.shape[1] * s, row.shape[0] * s), Image.NEAREST).save(os.path.join(out, 'dojogap_x%d.png' % s))
    print('wall', int(m.sum()), 'px')


if __name__ == '__main__':
    if '--before' in sys.argv: before()
    elif '--preview' in sys.argv: preview(sys.argv[sys.argv.index('--preview') + 1])
    else: print(__doc__)
