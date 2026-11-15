#!/usr/bin/env python3
"""Where each building meets the sidewalk (the owner: "Faudra faire toutes les liaisons façade–trottoir proprement, car
là ça fait coupé net, l'image"): every foot of a front, from the dojo to the arcade, grounded as a real street's is.

    zones of tools/redraw_zones.py ('footL', 'footB', 'footR': `tool`), the last ones: run that, then
    tools/bake_retouches.py (it also writes the ground lights it shades, GL, from their before copies)
    python3 tools/facade_foot.py --preview DIR   the current layers before and after, x4 crops in DIR (nothing written)
    python3 tools/facade_foot.py --input SIDE    the draft's input (tools/src/edits/foot_SIDE_in.webp; SIDE: L or R)
    python3 tools/facade_foot.py --ask SIDE      asks the image model for it (tools/src/edits/foot_SIDE_model.webp)

The painter's fronts ran straight into the paving, a knife's cut between a wall and the stones. Now, in the street's
camera (tools/zone5_facades.py's: VP (700, 615), f 960 px, the eye 1.41 m over the road, the sidewalks 0.15 m up; a
line along the street keeps its ray v = (615 - y) / (x - 700), its height over the sidewalk h at v_foot (1 - h / 1.26)):
- a base course along each front (BASES): a concrete plinth or a stone sill a few centimetres proud of the wall, from
  its foot ray up to its own ray; its top edge (one row, seen from above) catching the light, its face a step darker,
  its last row in the crease; its tone one tone a plane (R29): the pavement's and the wall's light at its foot (their
  low frequencies along the front, sampled in each layer), times the plinth's own make-up (FACE, TOP, CREASE);
  across a door a threshold of its own (a stone or wooden sill), none across what stands in front of it (the bicycle's
  wheels and frame kept as painted, `keep`);
- over it, the rain's grime on the wall's foot (GRIME): the splash line a few tens of centimetres high, darker down to
  the plinth, its streaks and splashes the image model's (below);
- on the ground, the contact shade (AO): each front, step, post, pipe and thing standing on the sidewalk is a shape on
  the ground's plane (a segment along its foot, a circle, a box: SHAPES); each ground pixel's ray is followed down to
  the sidewalk and its distance to each shape taken in metres, its light times 1 - depth exp(-d / reach): a soft dark
  line along every foot, darkest in the crease and wider into the corners, its ends rounded where a wall ends, nearer
  pixels a wider line (the metres fixed, not the pixels). The ground lights (street.js GL: each shop's light on the
  sidewalk, a layer of its own) take the same shade, from their before copies (tools/src/edits/<gl>_before.webp; the
  street lamp's as tools/pole_foot.py leaves it);
- the downpipes' feet (PIPES): a collar into the drain at the pipe's foot, its lit top, the shade round it (B's at
  its corner left as painted).
What is detailed is drawn by the image model (R28): the street's bottom band with the plinths and shade laid in by this
tool, brightened, asked to weather them as a rainy Japanese street's (concrete's grain, splash marks and streaks of
dirt, a wet dark foot), its answer registered on the street, brought down to its pixels, and only its fine structure
(its luminance over its own low frequencies, DETAIL) laid on the plinths and the grime's band; the light stays this
tool's and the painter's (R2). The power cut: the same make-up on that layer's own light (its pavement and wall sampled
there), the same grime and shade. Ichiraku's front (its sill and step) and the drinks machines' bases are another
tool's: the zones stop at Ichiraku's frames and at the machines' sides.
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
from scipy.ndimage import gaussian_filter, gaussian_filter1d, map_coordinates

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDITS = os.path.join(ROOT, 'tools', 'src', 'edits')
VPX, VPY, F, EYE, WALK = 700.0, 615.0, 960.0, 1.41, 0.15   # the street's camera (tools/zone5_facades.py)
ES = EYE - WALK                                   # the eye over the sidewalk (m)
lum = lambda z: 0.299 * z[..., 0] + 0.587 * z[..., 1] + 0.114 * z[..., 2]

# ---- the fronts' feet. Each base: its columns [x0, x1), its foot (a ray v through VP, moved dy rows where the painter's
# line drifts off it; or a level row y for a front facing the street), its plinth (h: its height over the sidewalk, m;
# 0: none), its grime (g: m), its make-up (mk: MAKEUP's), its columns where a sill replaces it (sills: (x0, x1, h, mk)),
# what stands in front of it and is kept as painted (keep: polygons; only its pixels that differ from the wall)
MAKEUP = {                                        # its face lit as the wall over it (a vertical face: the wall's light, its
    # colour pulled `grey` toward a grey of its luminance, times `face`), its top edge as the ground (a level edge: the
    # pavement's light times `top`), its last row the face's times `crease`; `gl`: the share of the ground lights (the
    # shops' light on the sidewalk, street.js GL) its top edge and its face take
    'concrete': dict(grey=0.45, face=0.72, top=1.70, crease=0.86, gl=(0.7, 0.3)),
    'stone': dict(grey=0.4, face=0.68, top=1.80, crease=0.84, gl=(0.7, 0.3)),
    'wood': dict(grey=0.1, face=0.66, top=1.60, crease=0.84, gl=(0.6, 0.3)),
    # a stone sill under shop doors and their open doorway: one plane across both, so its face lit as the ground
    # under it (the room's floor behind the doorway is no light of its face's)
    'sill': dict(grey=0.3, face=0.74, top=1.80, crease=0.86, gl=(0.7, 0.3), src='pave'),
}
BASES = [
    # the left side (its feet on v 0.229: the walls 5.5 m left of the eye's line)
    dict(n='dojo_slab', side='L', x=(0, 128), v=0.229, dy=0.0, h=0.0, g=0.0),          # (its threshold slab: dojofoot's)
    dict(n='dagashi', side='L', x=(139, 227), v=0.229, dy=1.0, h=0.05, g=0.0, mk='sill'),   # (its doors, its doorway)
    dict(n='oden', side='L', x=(398, 504), v=0.229, dy=0.0, h=0.11, g=0.28, mk='stone',
         sills=[(420, 463, 0.04, 'wood')]),                                             # (its door: the sill painted)
    # the right side (its feet on v -0.283: the walls 4.45 m right of it)
    dict(n='center', side='R', x=(870, 907), v=-0.26, dy=-3.0, h=0.0, g=0.0),            # (its dark base: the painter's)
    dict(n='B', side='R', x=(946, 1004), v=-0.283, dy=0.0, h=0.08, g=0.26, mk='concrete',
         keep=[(949, 650, 980, 702)]),                                                   # (the bicycle)
    dict(n='hallB', side='R', x=(1004, 1022), v=-0.283, dy=0.0, h=0.03, g=0.0, mk='sill'),     # (its threshold)
    dict(n='entrance', side='R', x=(1068, 1116), v=-0.283, dy=0.0, h=0.0, g=0.0),      # (its step: entree's)
    # right of Ichiraku: the arcade is set back 30 cm (its feet 10 rows over the front's ray); between them Ichiraku's
    # building's own end wall, a frontal plane at Z 7.55 m (its foot level, row 775: tools/arcade_shade.py), to the
    # downpipe in the inside corner; then the arcade's front, its post and its tiled recess, one plinth along them
    dict(n='endA', side='F', x=(1266, 1302), y=775.0, h=0.08, g=0.0, mk='concrete'),
    dict(n='arcade', side='R', x=(1306, 1356), v=-0.283, dy=-9.5, h=0.06, g=0.0, mk='concrete'),
    # things on the ground: the bench's low platform in front of Kirua's wall (its front face toward us, level), the
    # downpipes' feet
    dict(n='bench', side='F', x=(351, 400), y=692.0, h=0.0, g=0.0),
    # across the crossroads, the building facing the street on the left (its garage, its lit doorway): its foot level
    dict(n='farL', side='F', x=(505, 600), y=641.0, h=0.0, g=0.0),
    dict(n='pipeL', side='L', x=(129, 139), v=0.229, dy=5.5, h=0.0, g=0.0, ao=(0.3, 0.06)),
    dict(n='pipeR', side='R', x=(1301, 1307), v=-0.283, dy=-11.0, h=0.0, g=0.0, ao=(0.3, 0.06)),
]
AO = dict(reach=0.12, depth=0.55)                 # the contact shade's reach (m) and depth (at the crease)
# the downpipes: their columns (the pipe's own, its dark edges included), their foot's row; a collar into the drain there
# (B's at its corner, x 943..945, left as painted: the owner, "pas nécessaire"; B's plinth starts behind it)
PIPES = [dict(x=(132, 139), y=750, side='L'), dict(x=(1302, 1307), y=774, side='R')]
# small things standing on the sidewalk: the bicycle's two tyres (their contact points, a little shade along each)
SHAPES = [dict(at=(955.5, 691.0), r=0.03, depth=0.62, reach=0.07), dict(at=(970.5, 697.0), r=0.03, depth=0.62, reach=0.07)]
# the drafts (R28): the image model asked to weather the feet in their context (a crop of the street as this tool lays
# its bases in, brightened, enlarged k times); their fine structure only, over the plinths and the grime
MODEL = 'openai/gpt-5.4-image-2'
DRAFTS = {'L': dict(crop=(0, 470, 504, 806), k=3, map=(2.05, 0.0, 1.02)),
          'R': dict(crop=(880, 540, 1136, 796), k=4, map=(3.93, -7.0, 0.5))}
GAMMA = 2.0                                       # (the drafts' brightening, as tools/redraw_zones.py's)
SIGMA_D, CLIP_D, DETAIL = 1.2, 0.3, 0.8           # their grain: over its low frequencies at this scale, bounded, its strength
BOXES = {'footL': (0, 640, 227, 800), 'footO': (346, 630, 620, 712), 'footB': (860, 620, 1117, 765),
         'footR': (1262, 740, 1456, 816)}


def active_boxes():
    """The zones that draw this tool (tools/redraw_zones.py's ZONES with tool 'facade_foot', when it runs them), else
    BOXES: what lies outside them is left as it is."""
    rz = sys.modules.get('__main__')
    z = getattr(rz, 'ZONES', None)
    if isinstance(z, dict):
        return [c['box'] for c in z.values() if c.get('tool') == 'facade_foot']
    return list(BOXES.values())


def _inside(x, y):
    return any(a <= x < c and b <= y < d for (a, b, c, d) in active_boxes())


def bases():
    return [b for b in BASES if _inside((b['x'][0] + b['x'][1]) // 2, foot(b, (b['x'][0] + b['x'][1]) // 2) - 1)]


def pipes():
    return [q for q in PIPES if _inside(q['x'][0], q['y'] - 1)]


def shapes():
    return [q for q in SHAPES if _inside(int(q['at'][0]), int(q['at'][1]))]


def foot(b, x):
    """The foot's row (continuous, pixel edges: rows whose centre is above it are wall) at column x (centre x + .5)."""
    if b['side'] == 'F': return float(b['y'])
    return VPY - b['v'] * (x + 0.5 - VPX) + b['dy']


def top(b, x, h):
    """The row of the line h m over the sidewalk on b's wall, at column x."""
    if b['side'] == 'F':
        Z = F * ES / (b['y'] - VPY); return b['y'] - F * h / Z
    v = b['v'] * (1.0 - h / ES)
    return VPY - v * (x + 0.5 - VPX) + b['dy']


def ground_xz(x, y):
    """The point of the sidewalk under pixel centres (x, y): X (m, right of the eye's line), Z (m ahead)."""
    d = np.maximum(y + 0.5 - VPY, 1e-3)
    Z = F * ES / d
    return (x + 0.5 - VPX) * Z / F, Z


def wall_segment(b):
    """b's foot as a segment on the ground's plane: its two ends (X, Z)."""
    x0, x1 = b['x']
    pts = []
    for x in (x0, x1 - 1e-3):
        X, Z = ground_xz(np.array(float(x)), np.array(foot(b, x) - 0.5))
        pts.append((float(X), float(Z)))
    return pts


def seg_dist(X, Z, a, c):
    """Distance (m) from ground points to the segment a-c."""
    ax, az = a; cx, cz = c
    dx, dz = cx - ax, cz - az; L2 = dx * dx + dz * dz + 1e-12
    t = np.clip(((X - ax) * dx + (Z - az) * dz) / L2, 0, 1)
    return np.hypot(X - (ax + t * dx), Z - (az + t * dz))


def poly_mask(P, shape, off=(0, 0)):
    m = Image.new('L', (shape[1], shape[0]), 0)
    ImageDraw.Draw(m).polygon([(px - off[0], py - off[1]) for px, py in P], fill=255)
    return np.array(m) > 127


def save(a, path, mode='RGBA'):
    Image.fromarray(np.round(np.clip(a, 0, 255)).astype(np.uint8), mode).save(path, 'WEBP', lossless=True, quality=100, method=6, exact=True)


def _rows(a, b):
    """The pixel rows whose centres lie in [a, b)."""
    return range(int(np.ceil(a - 0.5)), int(np.ceil(b - 0.5)))


def light_at_foot(img, b, keep, n_m=0.12):
    """Per column of b: the pavement's light just under its foot and the wall's just over its plinth (medians over
    n_m metres, then smoothed along the front), in this layer."""
    x0, x1 = b['x']; pv, wl = [], []
    for x in range(x0, x1):
        f = foot(b, x); ppm = max(abs(x + 0.5 - VPX) * abs(b.get('v', 0.0)) / ES, 1.0) if b['side'] != 'F' else F * (f - VPY) / (F * ES)
        n = max(3, int(round(n_m * ppm)))
        ys = [y for y in range(int(np.ceil(f - 0.5)) + 1, int(np.ceil(f - 0.5)) + 1 + n) if not keep[y, x]]
        pv.append(np.median(img[ys, x, :3], 0) if ys else np.full(3, np.nan))
        t = top(b, x, max(b.get('h', 0.0), 0.0))
        ys = [y for y in range(int(np.ceil(t - 0.5)) - n - 1, int(np.ceil(t - 0.5)) - 1) if not keep[y, x]]
        wl.append(np.median(img[ys, x, :3], 0) if ys else np.full(3, np.nan))
    out = []
    for arr in (np.array(pv), np.array(wl)):
        for c in range(3):                                   # (columns hidden by what is in front: from their neighbours)
            col = arr[:, c]; ok = ~np.isnan(col)
            col[~ok] = np.interp(np.nonzero(~ok)[0], np.nonzero(ok)[0], col[ok]) if (~ok).any() else col[~ok]
        out.append(np.stack([gaussian_filter1d(arr[:, c], 3.0, mode='nearest') for c in range(3)], -1))
    return out


def makeup(pave, wall, mk):
    """The plinth's tones at a column: its face lit as the wall over it (a vertical face; its colour toward a grey), its
    top edge as the ground (a level one; never darker than twice the face), its last row a touch darker."""
    w = pave if mk.get('src') == 'pave' else wall
    face = (w + mk['grey'] * (lum(w) - w)) * mk['face']
    top = pave * mk['top']
    top = top * max(1.0, lum(face) * 2.0 / max(lum(top), 1.0))
    return dict(face=face, top=top, crease=face * mk['crease'])


def keep_mask(b, img, shape):
    """What stands in front of b and stays as painted: its pixels within the polygons (x0, y0, x1, y1) that differ
    from the wall or the ground beside it (each row's tone over the REF columns right of the polygon)."""
    k = np.zeros(shape[:2], bool)
    L = lum(img)
    for (x0, y0, x1, y1) in b.get('keep', []):
        for y in range(y0, y1):
            ref = np.median(L[y, x1 + 2:x1 + 2 + KEEP_REF])
            k[y, x0:x1] = np.abs(L[y, x0:x1] - ref) > 4
    return k


KEEP_REF = 14                                     # (the columns the wall's or the ground's tone is read over)


def draw_bases(img, keep_all):
    """The plinths and sills of BASES in one layer (in place); returns their pixels' roles (1 the top edge, 2 the face,
    3 the last row, 0 none) and their share of the ground lights."""
    H, W = img.shape[:2]
    plinth = np.zeros((H, W), np.int8); share = np.zeros((H, W))
    for b in bases():
        if b.get('h', 0.0) <= 0 and not b.get('sills'): continue
        keep = keep_all[b['n']]
        pave, wall = light_at_foot(img, b, keep)
        x0, x1 = b['x']
        for x in range(x0, x1):
            h, mk = b.get('h', 0.0), MAKEUP.get(b.get('mk', 'concrete'))
            for sx0, sx1, sh, smk in b.get('sills', []):
                if sx0 <= x < sx1: h, mk = sh, MAKEUP[smk]
            if h <= 0: continue
            i = x - x0
            T = makeup(pave[i], wall[i], mk)
            f, t = foot(b, x), top(b, x, h)
            rows = list(_rows(t, f))
            if not rows: rows = [int(np.ceil(f - 0.5)) - 1]
            for j, y in enumerate(rows):
                if keep[y, x]: continue
                r = 1 if j == 0 else (3 if j == len(rows) - 1 and len(rows) > 2 else 2)
                img[y, x, :3] = T[{1: 'top', 2: 'face', 3: 'crease'}[r]]; img[y, x, 3] = 255
                plinth[y, x] = r; share[y, x] = mk['gl'][0] if r == 1 else mk['gl'][1]
    return plinth, share


def grime_factor(shape):
    """The rain's grime over the plinths: a factor on the wall's rows from the plinth's top up to g m."""
    H, W = shape[:2]
    g = np.ones((H, W))
    for b in bases():
        if b.get('g', 0.0) <= 0: continue
        x0, x1 = b['x']
        for x in range(x0, x1):
            h = b.get('h', 0.0)
            for sx0, sx1, sh, _ in b.get('sills', []):
                if sx0 <= x < sx1: h = -1
            if h < 0: continue
            tg, tp = top(b, x, b['g']), top(b, x, h)
            for y in _rows(tg, tp):
                s = ((y + 0.5) - tg) / max(tp - tg, 1e-3)           # 0 at the splash line, 1 at the plinth
                g[y, x] = 1.0 - GRIME * s ** 1.6
    return g


GRIME = 0.22                                      # the grime's darkening at the plinth (none at its top)


def ao_factor(shape):
    """The contact shade on the ground (a factor, 1 where none) and where the ground is (under the bases' feet)."""
    H, W = shape[:2]
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    X, Z = ground_xz(xx, yy)
    gnd = np.zeros((H, W), bool)
    for b in bases():
        x0, x1 = b['x']
        for x in range(x0, x1):
            gnd[int(np.ceil(foot(b, x) - 0.5)):, x] = True
    f = np.ones((H, W))
    for b in bases():
        a, c = wall_segment(b)
        d = seg_dist(X, Z, a, c)
        dep, rea = b.get('ao', (AO['depth'], AO['reach']))
        f *= 1.0 - dep * np.exp(-d / rea)
    for s in shapes():                                 # (a round thing's foot: its distance from its rim)
        cx, cz = ground_xz(np.array(s['at'][0] - 0.5), np.array(s['at'][1] - 0.5))
        d = np.maximum(np.hypot(X - cx, Z - cz) - s['r'], 0.0)
        f *= 1.0 - s['depth'] * np.exp(-d / s['reach'])
    for xa, xb in AO_FADE:                             # (toward a front another tool draws: the shade fades out)
        for x in range(min(xa, xb), max(xa, xb) + 1):
            t = np.clip((x - xa) / (xb - xa), 0, 1); f[:, x] = 1.0 - (1.0 - f[:, x]) * t * t * (3 - 2 * t)
    return np.where(gnd, f, 1.0), gnd


AO_FADE = [(1263, 1268), (1116, 1106)]            # (Ichiraku's front, its own sill and step: from x 1117 to 1265)


def draw_pipes(img):
    """Each downpipe's foot: a collar a pixel wider than the pipe on each side, its top row lit, its face the pipe's a
    step darker, over the drain it goes into (in place); returns its pixels."""
    H, W = img.shape[:2]
    m = np.zeros((H, W), bool)
    for p in pipes():
        x0, x1 = p['x']; y = p['y']
        pipe = np.median(img[y - 8:y - 2, x0:x1, :3], 0)            # (its columns' own tones, lit side to dark)
        pipe = np.concatenate([pipe[:1], pipe, pipe[-1:]], 0)
        for i, x in enumerate(range(x0 - 1, x1 + 1)):
            img[y - 2, x, :3] = pipe[i] * 1.12; img[y - 1, x, :3] = pipe[i] * 0.72
            img[y - 2:y, x, 3] = 255; m[y - 2:y, x] = True
    return m


GL = ['gl_lamp', 'gl_oden', 'gl_win_z4_shop', 'gl_win_z7_shop', 'gl_dojo', 'gl_win_z9_lantern', 'gl_z4_emblem',
      'gl_win_z1_warm', 'gl_win_z7_kiosk']           # the ground lights the shade takes (not the machines', not Ichiraku's)


def gl_boxes():
    js = open(os.path.join(ROOT, 'assets', 'street.js'), encoding='utf-8').read()
    out = {}
    for m in re.finditer(r"url: 'assets/(gl_[a-z0-9_]+)\.webp\?v=\d+', box: \[(\d+), (\d+), (\d+), (\d+)\]", js):
        out[m.group(1)] = tuple(int(m.group(i)) for i in range(2, 6))
    return out


def gl_shaded(ao, pl):
    """The ground lights with the contact shade (their alpha, which scales their light, times it), and on the plinths
    (pl: their roles and shares) a share of the light on the ground at their foot: {name: array}. From their before
    copies (tools/src/edits/<name>_before.webp), the street lamp's as tools/pole_foot.py writes it."""
    role, share = pl
    out = {}
    for name, (gx, gy, gw, gh) in gl_boxes().items():
        if name not in GL: continue
        sub = ao[gy:gy + gh, gx:gx + gw]; rs = role[gy:gy + gh, gx:gx + gw]
        if (sub >= 0.999).all() and not rs.any(): continue
        src = os.path.join(ROOT, 'assets', name + '.webp') if name == 'gl_lamp' else os.path.join(EDITS, name + '_before.webp')
        g = np.asarray(Image.open(src).convert('RGBA')).astype(float).copy()
        lit = g[..., :3] * g[..., 3:] / 255.0                    # (its light, before the shade)
        g[..., 3] = np.round(g[..., 3] * sub)
        for b in bases():                                         # (each plinth's columns: the light on the ground at its foot)
            x0, x1 = b['x']
            for x in range(max(x0, gx), min(x1, gx + gw)):
                col = np.nonzero(rs[:, x - gx])[0]
                if not len(col): continue
                fy = int(np.ceil(foot(b, x) - 0.5)) - gy
                below = lit[max(fy + 1, 0):max(fy + 4, 0), x - gx]
                if not len(below): continue
                L = np.median(below, 0)
                for j in col:
                    v = L * share[gy + j, x]
                    a = max(v.max(), 1e-6)
                    g[j, x - gx, :3] = np.clip(v / a * 255.0, 0, 255); g[j, x - gx, 3] = np.clip(round(a), 0, 255)
        g[g[..., 3] == 0] = 0
        b0 = np.asarray(Image.open(src).convert('RGBA')).astype(float)
        if name == 'gl_lamp' or np.abs(np.round(g) - b0).max() > 0: out[name] = g   # (left as it is when untouched)
    return out


def compose(city, unlit, detail=True):
    """Both layers redrawn (new arrays) and the contact shade's factor (for the ground lights)."""
    H, W = city.shape[:2]
    keep = {b['n']: keep_mask(b, city, city.shape) for b in bases()}
    keep_all = np.zeros((H, W), bool)
    for k in keep.values(): keep_all |= k
    ao, gnd = ao_factor(city.shape)
    ao[keep_all] = 1.0
    gr = grime_factor(city.shape)
    gr[keep_all] = 1.0
    outs = []
    for img, tag in ((city, 'city'), (unlit, 'unlit')):
        n = img.copy()
        role, share = draw_bases(n, keep)
        plinth = role > 0
        wallg = (gr < 1.0) & ~plinth
        n[wallg, :3] *= gr[wallg][:, None]
        n[..., :3] *= ao[..., None]
        draw_pipes(n)
        outs.append(n)
    if detail:                                         # (the drafts' grain, registered on the lit layer as drawn so far)
        dm = (role > 0) | ((gr < 1.0) & (role == 0))
        dm &= ~keep_all
        det = detail_factor(outs[0], dm)
        for n in outs: n[dm, :3] *= det[dm][:, None]
    return outs[0], outs[1], ao, (role, share)


def draft_input(nc, side):
    """The draft's input: the street with this tool's bases laid in (the lit layer), its crop brightened
    (x ** (1 / GAMMA)) and enlarged with nearest pixels, as tools/redraw_zones.py asks its drafts."""
    x0, y0, x1, y1 = DRAFTS[side]['crop']; k = DRAFTS[side]['k']
    z = np.clip(nc[y0:y1, x0:x1, :3] / 255.0, 0, 1) ** (1 / GAMMA)
    return Image.fromarray((z * 255).round().astype(np.uint8)).resize(((x1 - x0) * k, (y1 - y0) * k), Image.NEAREST)


def api_key():
    k = os.environ.get('OPENROUTER_API_KEY')
    if k: return k
    p = os.path.expanduser('~/.config/openrouter/key')
    return open(p).read().strip() if os.path.exists(p) else 'proxy-injected'


def ask(side):
    """Asks the image model for the weathered feet (tools/src/edits/foot_SIDE_in.webp and _prompt.txt); saves its answer
    as tools/src/edits/foot_SIDE_model.webp."""
    buf = io.BytesIO(); Image.open(os.path.join(EDITS, f'foot_{side}_in.webp')).convert('RGB').save(buf, 'PNG')
    content = [{"type": "text", "text": open(os.path.join(EDITS, f'foot_{side}_prompt.txt')).read().strip()},
               {"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()}}]
    body = {"model": MODEL, "modalities": ["image", "text"], "usage": {"include": True}, "messages": [{"role": "user", "content": content}]}
    req = urllib.request.Request('https://openrouter.ai/api/v1/chat/completions', data=json.dumps(body).encode(),
                                 headers={'Authorization': 'Bearer ' + api_key(), 'Content-Type': 'application/json'})
    d = json.loads(urllib.request.urlopen(req, timeout=900).read())
    url = d['choices'][0]['message']['images'][0]['image_url']['url']
    im = Image.open(io.BytesIO(base64.b64decode(url.split(',', 1)[1])))
    im.save(os.path.join(EDITS, f'foot_{side}_model.webp'), 'WEBP', lossless=True, quality=100, method=6)
    print(side, 'answer', im.size, 'saved; cost', d.get('usage', {}).get('cost'), '$')


def _grad(z):
    l = lum(z); gx = np.zeros_like(l); gy = np.zeros_like(l)
    gx[:, 1:] = l[:, 1:] - l[:, :-1]; gy[1:] = l[1:] - l[:-1]
    return np.hypot(gx, gy)


def _shift(a, dy, dx):
    h, w = a.shape[:2]; yi = np.clip(np.arange(h) - dy, 0, h - 1); xi = np.clip(np.arange(w) - dx, 0, w - 1)
    return a[yi][:, xi]


def detail_factor(nc, mask):
    """The drafts' fine structure over the plinths and the grime (mask): each answer darkened back (x ** GAMMA), boxed
    down to the street's pixels, registered on it (the integer shift whose gradients best match it), its luminance over
    its own low frequencies (SIGMA_D), bounded, to the power DETAIL: a factor, 1 where no draft."""
    H, W = nc.shape[:2]; f = np.ones((H, W))
    for side, dr in DRAFTS.items():
        p = os.path.join(EDITS, f'foot_{side}_model.webp')
        if not os.path.exists(p): continue
        x0, y0, x1, y1 = dr['crop']; w, h = x1 - x0, y1 - y0
        # (its answer came back square, the crop scaled into it: its place there, `map` (S, ox, oy), measured once on
        # the answer: the crop's pixel (u, v) at (ox + S (u + .5), oy + S (v + .5)) in it; averaged over each pixel)
        S, ox, oy = dr['map']
        m = np.asarray(Image.open(p).convert('RGB')).astype(float) / 255.0
        m = m ** GAMMA * 255.0
        vv, uu = np.mgrid[0:h, 0:w].astype(float)
        e = np.zeros((h, w, 3))
        for c in range(3):
            mc = gaussian_filter(m[..., c], S * 0.42)
            for sy in (-0.25, 0.25):
                for sx in (-0.25, 0.25):
                    e[..., c] += map_coordinates(mc, [oy + S * (vv + 0.5 + sy) - 0.5, ox + S * (uu + 0.5 + sx) - 0.5],
                                                 order=1, mode='nearest') / 4
        o = nc[y0:y1, x0:x1, :3]
        go = _grad(o); go = (go - go.mean()) / (go.std() + 1e-6); best = None
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                g = _grad(_shift(e, dy, dx)); g = (g - g.mean()) / (g.std() + 1e-6)
                c = float((g * go).mean())
                if best is None or c > best[0]: best = (c, dx, dy)
        e = _shift(e, best[2], best[1])
        L = lum(e) + 1.0
        d = np.clip(L / (gaussian_filter(L, SIGMA_D) + 1e-6), 1 - CLIP_D, 1 + CLIP_D) ** DETAIL
        sub = f[y0:y1, x0:x1]; m = mask[y0:y1, x0:x1]
        sub[m] = d[m]
        print(f'foot draft {side}: registered dx={best[1]} dy={best[2]} (correlation {best[0]:.2f})')
    return f


_DONE = {}
# the lit windows' comps that carry the feet (street.js lays them over the layer when lit): the dagashi-ya's room (from
# the copy its zone reads, dagashi_comp_before.webp), the Pokemon Center's shop (from its before copy); each takes the
# change the layer took under it (its pixels times new over old, in luminance: the room's light keeps its hue on what
# is new)
COMPS = [('win_z7_shop', (142, 537), 'dagashi_comp_before'), ('win_z4_shop', (800, 538), 'win_z4_shop_before')]


def comps_after(city, nc):
    """COMPS with the feet: {name: the array to write}, only those something changed under."""
    out = {}
    for name, (cx, cy), src in COMPS:
        A = np.asarray(Image.open(os.path.join(EDITS, src + '.webp')).convert('RGBA')).astype(float).copy()
        h, w = A.shape[:2]
        o, n = city[cy:cy + h, cx:cx + w, :3], nc[cy:cy + h, cx:cx + w, :3]
        m = (A[..., 3] > 0) & (np.abs(n - o).max(-1) > 0.5)
        r = ((lum(n) + 1.0) / (lum(o) + 1.0))[..., None]            # (its light's hue kept: the change's luminance)
        A[..., :3][m] = np.clip(A[..., :3][m] * r[m], 0, 255)
        if m.any(): out[name] = A
    return out


def draw(city, unlit, box):
    """A zone of tools/redraw_zones.py (BOXES: they run one after another): the whole street's feet are drawn once, on
    the layers as the zones before the first of them leave them, the ground lights written then; each zone lays its
    box of it. Returns what changed there."""
    if 'nc' not in _DONE:
        nc, nu, ao, pl = compose(city, unlit)
        _DONE.update(nc=np.round(nc), nu=np.round(nu))
        for name, g in gl_shaded(ao, pl).items():
            save(g, os.path.join(ROOT, 'assets', name + '.webp'))
        for name, a in comps_after(city, _DONE['nc']).items():     # (the lit windows' comps over the feet: R10)
            save(a, os.path.join(ROOT, 'assets', name + '.webp'))
        out = np.ones(city.shape[:2], bool)
        for (a, b, c, d) in active_boxes(): out[b:d, a:c] = False
        lost = out & ((np.abs(_DONE['nc'] - city).max(-1) > 0.5) | (np.abs(_DONE['nu'] - unlit).max(-1) > 0.5))
        assert not lost.any(), f'facade_foot: {int(lost.sum())} changed pixels outside the zones\' boxes'
    x0, y0, x1, y1 = box
    nc, nu = _DONE['nc'], _DONE['nu']
    ch = (np.abs(nc[y0:y1, x0:x1] - city[y0:y1, x0:x1]).max(-1) > 0.5) | (np.abs(nu[y0:y1, x0:x1] - unlit[y0:y1, x0:x1]).max(-1) > 0.5)
    city[y0:y1, x0:x1] = nc[y0:y1, x0:x1]; unlit[y0:y1, x0:x1] = nu[y0:y1, x0:x1]
    return ch


CROPS = {'L1': (0, 690, 240, 800), 'L2': (330, 630, 520, 700), 'R1': (860, 640, 1030, 720), 'R2': (1000, 680, 1125, 750),
         'R3': (1270, 740, 1456, 816)}


def preview(out):
    os.makedirs(out, exist_ok=True)
    L = {t: np.asarray(Image.open(os.path.join(ROOT, 'assets', f)).convert('RGBA')).astype(float)
         for t, f in (('city', 'layer_city_off.webp'), ('unlit', 'street_unlit.webp'))}
    nc, nu, ao, pl = compose(L['city'], L['unlit'])
    A = {'city': nc, 'unlit': nu}
    for t in ('city', 'unlit'):
        for nm, (a, b, c, d) in CROPS.items():
            zs = []
            for arr in (L[t], A[t]):
                z = arr[b:d, a:c]
                z = z[..., :3] * (z[..., 3:] / 255.0)
                zs.append(255 * (np.clip(z, 0, 255) / 255) ** 0.6)
            z = np.concatenate([zs[0], np.full((2, c - a, 3), 255.0), zs[1]], 0)
            Image.fromarray(np.round(z).astype(np.uint8)).resize(((c - a) * 4, z.shape[0] * 4), Image.NEAREST).save(os.path.join(out, f'{nm}_{t}.png'))
    for t, arr in (('city', nc), ('unlit', nu)):
        save(arr, os.path.join(out, ('layer_city_off' if t == 'city' else 'street_unlit') + '.webp'))
    for name, g in gl_shaded(ao, pl).items():
        save(g, os.path.join(out, name + '.webp'))
    for name, a in comps_after(L['city'], nc).items():
        save(a, os.path.join(out, name + '.webp'))
    print('preview in', out)


def layers():
    return {t: np.asarray(Image.open(os.path.join(ROOT, 'assets', f)).convert('RGBA')).astype(float)
            for t, f in (('city', 'layer_city_off.webp'), ('unlit', 'street_unlit.webp'))}


if __name__ == '__main__':
    if '--preview' in sys.argv: preview(sys.argv[sys.argv.index('--preview') + 1])
    elif '--input' in sys.argv:                       # (from the layers as they are: run it before this tool's zones are
        side = sys.argv[sys.argv.index('--input') + 1]   # baked in, on the street as the zones before them leave it)
        L = layers(); nc = compose(L['city'], L['unlit'], detail=False)[0]
        draft_input(nc, side).save(os.path.join(EDITS, f'foot_{side}_in.webp'), 'WEBP', lossless=True, quality=100, method=6)
        print('foot', side, 'input written')
    elif '--ask' in sys.argv: ask(sys.argv[sys.argv.index('--ask') + 1])
    else: print(__doc__)
