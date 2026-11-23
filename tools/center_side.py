#!/usr/bin/env python3
"""The roji's far wall, the Pokemon Center's side seen face on: the front's cladding carried round the corner, in the
alley's own light.

    (a module: tools/redraw_zones.py's zone 'cside', the last, calls draw(city, unlit, box) on the street as the zones
     before it leave it: both layers in its box and the exit sign's lit comp (assets/z5_alley.webp, as tools/roji_alley.py
     has just written it) over the wall, the same bytes each time)
    python3 tools/center_side.py --before       once: the zone's before copies (tools/src/edits/cside_before_*.webp), the
                                                earlier zones' own before copies laid over their boxes first (what
                                                tools/redraw_zones.py restores there before any zone runs)
    python3 tools/center_side.py --preview DIR  the wall before and after over the layers as they are (run it on layers
                                                without the zone): off, lit (the sign's comp over it) and in the power cut,
                                                x1 and x6, and the layers and the comp it would write (nothing written in
                                                assets/)

What was there (tools/roji_alley.py): under the Center's bands turning the corner (its coping, the red sign band, the
lines under it: rows 441..484), from row 485 down to the alley's floor (row 667), one smooth lavender plaster at one
value (39, 38, 77; the front's old lilac times 0.8) with only the steel exit door (x 927 on, behind B's corner from x 941)
and its green exit sign: a flat plane about as light as the Center's lit front, the same deep in the alley as at its
corner.

What the camera sees (tools/roji_alley.py's model: the street's camera, VP (700, 615), f 960, the eye 1.41 m; the right
fronts on the plane 5 m right of the eye's line): the alley runs square to the street between the Center's corner
(23.08 m down the street) and B's (19.92 m): 3.16 m wide. Its far wall is the Center's side, a frontal plane at 23.08 m
(41.6 px a metre), of which the eye sees its first 0.79 m (the rest behind B's corner), from its roof line (5.59 m) to the
alley's floor (the sidewalk's level, 0.13 m).

What it is now:
- the material: the front's own cladding (tools/center_wall.py: light grey-white panels in courses of 0.51 m) turning the
  corner, as a Center's panels run round a corner the street shows and as the image model drew this very side when it
  drew the front (tools/src/edits/cwall_wall_model.webp: the same panels on the side, level, the base along its foot): its
  courses level here, each joint one crisp pixel at the very row of the front's joint at the corner (the courses meet at
  the arris; only the front's own: from row 532 down, as tools/center_wall.py draws them), a vertical joint on the door's
  jamb from its head up to the bands (the front's rule: its verticals on its door's jambs), the dark base turning the
  corner along the foot up to the door (the front's stone, its lit top on the front's row, R5), the wet starter course over
  it (the front's factor), a fine fixed grain (the front's); one tone over the plane (R29), the front's panels' colour;
- its light, only what reaches it: the side faces the eye and turns away from the street, so it is a step darker than
  the front (K_SIDE: the street's half of the sky it sees, as the painter's near side of Naruto's building and the bands
  turning this corner are); the street's light comes in through the alley's mouth, so it falls off going back (each
  point's view factor to the mouth, an opening 3.16 m wide from the floor up, plus what B's side and the floor send back:
  FILL; from the corner to B's, 0.77, as the image model's side falls off), and a little at the foot (the floor in front
  of the mouth); from above the sky, lighter up (the image model's light on this side, row by row: PROFILE, a smooth curve,
  its joints left out), a darker splash zone over the base; rain streaks hanging from the band's metal edge (a value noise
  in metres: a few thin streaks, 0.35 to 1 m long, a few levels at most); no lamp of the street reaches it (the Center's
  lamps and its Poke Ball face the street from behind this plane);
- the exit sign's light on it (the comp z5_alley, street.js: a 'tube' on its hours 'exit', lit day and night, steady, red
  in the red night as the street's lights are): its green glow round it, tools/roji_alley.py's (sign_light, GLIFT, GLOW),
  on the new wall, taken by the panels as the pale panels they are (the side's shade is the street's light it lacks, not a
  darker surface: the glow reads stronger on it than on the old plaster); and on its battery in the power cut (the layer: the comp is off then) the same glow at the battery's
  share (SIGN_BATT), on the wall, the door, its step and the floor in front, as the sign's own face is;
- the layers: the wall the same in both (the street's power lights nothing in the alley); the door, the sign, the step, the
  floor, the bands and B's corner as tools/roji_alley.py draws them; Red and Pikachu sit over the bands above (rows 441 to
  464), over none of this. Needs Pillow, numpy, scipy.
"""
import os
import sys
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter1d, median_filter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDITS = os.path.join(ROOT, 'tools', 'src', 'edits')
ASSETS = os.path.join(ROOT, 'assets')
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import roji_alley as RA                          # noqa: E402  (the alley's model: its camera, its wall, the sign's light)
import center_wall as CW                         # noqa: E402  (the front's cladding: its courses, joints, base, grain)

BOX = (908, 484, 941, 691)                       # the zone (redraw_zones.py 'cside'): the far wall under the bands, the floor
TOP = 484                                        # the wall's first row under the band (its shadow line, as on the front's
                                                 # arris: the front's lilac there before, times 0.8)
VPX, VPY, F, EYE, XF = RA.VPX, RA.VPY, RA.F, RA.EYE, RA.XF
ZF, ZB, HS = RA.ZF, RA.ZB, RA.HS                 # the far wall's depth (23.08 m), B's corner's (19.92 m), the floor (0.13 m)
LUM = np.array([0.299, 0.587, 0.114])
CORNER = 907                                     # the front's last column (its arris): the courses meet there
FRONT_PANEL = ((901, 907), (488, 499))           # the front's cladding read here (columns, rows): its colour over its upper
                                                 # strip at the corner, out of its lamps' fans
FRONT_BASE = ((900, 907), (653, 664))            # the front's dark stone base (the painter's), and its lit top's row
K_SIDE = 0.74                                    # the side's light against the front's at the corner (turned from the street)
FILL = 0.05                                      # (what B's side and the floor, lit by the mouth, send back onto it)
MOUTH_TOP = 9.0                                  # (the mouth's opening, from the floor up to here: B's lit floors beyond)
PROFILE_COLS, PROFILE_ROWS = (909, 918), (487, 644)   # the image model's side: its light by row read here (left of its
                                                 # joint, out of the sign's glow; over its wet course, which is the front's
                                                 # factor here)
H_FLOOR = 1.2                                    # (under this height the floor in front sends back what it hides of the
                                                 # mouth: the mouth's light taken at this height)
JAMB = 927                                       # the door's jamb's column (its frame from here): its joint up to the bands
STREAK = dict(cell=0.03, thr=0.58, amp=0.12, len=(0.35, 1.0), seed=23)   # (rain streaks from the band's edge: a value noise
                                                 # along the wall in metres, its cells; the share that streaks; their
                                                 # darkening at the edge; their lengths, m)
GRAIN_SEED = 5


def load(p, mode='RGBA'):
    return np.asarray(Image.open(p).convert(mode)).astype(float)


def save(a, p):
    Image.fromarray(np.clip(np.round(a), 0, 255).astype(np.uint8), 'RGBA' if a.shape[-1] == 4 else 'RGB').save(
        p, 'WEBP', lossless=True, quality=100, method=6, exact=True)


# ---- the far wall in the street's camera
def x_m(x):
    """how far from the street's line (m) the far wall is at column x's middle"""
    return (np.asarray(x, float) + 0.5 - VPX) * ZF / F - XF


def h_m(y):
    """the height (m) of row y's middle on the far wall"""
    return EYE + (VPY - (np.asarray(y, float) + 0.5)) * ZF / F


def mouth(d, h):
    """the share of the street's light a point of the far wall (d m from the street's line, h m up) gets through the
    alley's mouth: its view factor to the opening (a rectangle square to the wall, from the wall's plane to B's, from the
    floor up to MOUTH_TOP), in closed form"""
    d = np.maximum(np.asarray(d, float), 1e-4); B = np.sqrt(d * d + (ZF - ZB) ** 2)
    f = lambda t: np.arctan(t / d) - d / B * np.arctan(t / B)
    return (f(MOUTH_TOP - h) - f(HS - h)) / (2 * np.pi)


def draft_profile():
    """the image model's light on this side, row by row (tools/src/edits/cwall_wall_model.webp, darkened back as
    tools/center_wall.py does; its rows through the pier's anchors, its columns through its fit): the median of its
    luminance over PROFILE_COLS, its joints left out (a median over 7 rows), smooth (sigma 3), 1 at row 490"""
    A = CW.answer(); ra = CW.ROWS['pier']
    rows = np.arange(PROFILE_ROWS[0], PROFILE_ROWS[1]); cols = np.arange(*PROFILE_COLS)
    acc = np.zeros((len(rows), len(cols))); ss = 6
    for j in range(ss):
        for i in range(ss):
            xa = (cols[None, :] + (i + 0.5) / ss - CW.DRAFT[0]) * CW.SX + CW.OX
            ya = np.interp(rows[:, None] + (j + 0.5) / ss, [a for a, _ in ra], [b for _, b in ra])
            acc += A[np.clip(ya.astype(int), 0, A.shape[0] - 1), np.clip(xa.astype(int), 0, A.shape[1] - 1)] @ LUM
    p = np.median(acc / ss / ss, 1)
    p = gaussian_filter1d(median_filter(p, 7, mode='nearest'), 3.0, mode='nearest')
    return dict(zip(rows.tolist(), (p / p[490 - PROFILE_ROWS[0]]).tolist()))


def course_rows():
    """the front's course joints at its corner (tools/center_wall.py's rows there, from row 532 down): the side's, level"""
    return sorted({int(np.round(CW.row_of(CORNER, h))) for h in CW.COURSES if np.round(CW.row_of(CORNER, h)) >= 532})


def base_rows():
    """the base's lit top on the front at the corner, and the wet starter course's first row over it"""
    top = int(np.round(CW.row_of(CORNER, EYE + CW.V_BASE * XF) - 0.5 + 0.5))
    wet0 = int(np.floor(CW.row_of(CORNER, CW.COURSES[0]) + 0.5)) + 1
    return top, wet0


def hashf(x, y, k):
    v = np.sin(np.asarray(x) * 12.9898 + np.asarray(y) * 78.233 + k * 37.719) * 43758.5453
    return v - np.floor(v)


def streaks(X, depth):
    """the rain's streaks from the band's metal edge (a darkening factor <= 1): along the wall a value noise in metres
    (cells of STREAK['cell'], smooth between them), where it passes its threshold a streak, its length its own, fading down"""
    c = STREAK['cell']; u = np.asarray(X) / c; i0 = np.floor(u).astype(int); t = u - i0; t = t * t * (3 - 2 * t)
    n0, n1 = hashf(i0, 0.0, STREAK['seed']), hashf(i0 + 1, 0.0, STREAK['seed'])
    n = n0 + (n1 - n0) * t
    s = np.clip((n - STREAK['thr']) / (1 - STREAK['thr']), 0, 1)
    L0, L1 = STREAK['len']; L = L0 + (L1 - L0) * hashf(np.round(u).astype(int), 1.0, STREAK['seed'] + 1)
    return 1.0 - STREAK['amp'] * s * np.exp(-np.maximum(depth, 0) / L)


def walls():
    """the far wall's pixels under the bands (tools/roji_alley.py's cast: the plane's own, not the door, the sign, the
    step), each its (x, y), and every surface the sign's comp may light in the box"""
    hit = RA.cast(x0=BOX[0], x1=BOX[2], y0=BOX[1], y1=BOX[3])
    wall = [(x, y) for (x, y), s in hit.items() if s[0] == 'wall' and y >= TOP]
    sign = {(x, y) for (x, y), s in hit.items() if s[0] == 'sign'}
    return wall, sign, hit


def build(city):
    """the new wall over the layer `city` (as the zones before this one leave it): {(x, y): colour}, and the sign's lit
    colour on each pixel"""
    wall, sign, _ = walls()
    (fx0, fx1), (fy0, fy1) = FRONT_PANEL
    Cf = np.median(city[fy0:fy1, fx0:fx1, :3].reshape(-1, 3), 0); Lf = float(Cf @ LUM); chroma = Cf / Lf
    (bx0, bx1), (by0, by1) = FRONT_BASE
    top, wet0 = base_rows()
    Cb = np.median(city[by0:by1, bx0:bx1, :3].reshape(-1, 3), 0)
    kb = float(np.median(city[top, bx0:bx1, :3] @ LUM) / max(Cb @ LUM, 1.0))
    P = draft_profile(); rows = course_rows()
    p_lo, p_hi = min(P), max(P)
    d0 = x_m(BOX[0])
    out, lit = {}, {}
    h_edge = h_m(TOP - 0.5)                                         # (the band's metal edge, the streaks' start)
    for x, y in wall:
        X, h = x_m(x), h_m(y)
        he = max(h, H_FLOOR)
        R = (mouth(X, he) + FILL) / (mouth(d0, he) + FILL)          # (the street's light through the mouth, its fall-off)
        g = 1.0 + CW.GRAIN * (hashf(x, y, GRAIN_SEED) * 2 - 1)
        if y >= top:                                                # the base: the front's stone, its lit top
            m = Cb * g * (kb if y == top else 1.0); k = K_SIDE * R
        else:                                                       # the panels: the front's, as lit as the front (m),
            m = chroma * (Lf * g * streaks(X + XF, h_edge - h))     # times the light the side gets (k)
            if y in rows or (x == JAMB and y <= rows[2]): m = m * CW.K['joint']   # (the joints: the courses, the jamb's)
            if y >= wet0: m = m * CW.K['wet']                                     # (the wet starter course)
            k = K_SIDE * P[min(max(y, p_lo), p_hi)] * R * (CW.K['band'] if y == TOP else 1.0)   # (the band's shadow line)
        c = m * k
        out[(x, y)] = c
        # the sign's light on it: tools/roji_alley.py's, taken by the material as it is (a pale panel takes as much as the
        # front's would: the side's own shade is the street's light it lacks, not a darker surface)
        I = RA.sign_light(X + XF, h, 0.0, 'front')
        al = np.clip(float(m @ LUM) / RA.lum3(RA.C['wall']), 0.15, 1.3)
        lit[(x, y)] = c + I * (RA.GLIFT * m + RA.GLOW * al)
    return out, lit, sign


def draw(city, unlit, box=BOX):
    """Zone 'cside': both layers in place (the wall alike in both), the sign's comp over the new wall, its battery's glow in
    the power cut's layer; returns what changed in the layers"""
    H, W = city.shape[:2]
    ch = np.zeros((H, W), bool)
    out, lit, sign = build(city)
    cname, (cx, cy), (cw, chh) = RA.COMP
    pc = os.path.join(ASSETS, cname + '.webp')
    comp = load(pc)
    for (x, y), c in out.items():
        c = np.round(np.clip(c, 0, 255)); lt = np.round(np.clip(lit[(x, y)], 0, 255))
        for a in (city, unlit):
            if np.abs(a[y, x, :3] - c).max() > 0: ch[y, x] = True
            a[y, x, :3] = c
        on = np.abs(lt - c).max() >= 1
        comp[y - cy, x - cx, :3] = lt if on else 0; comp[y - cy, x - cx, 3] = 255 if on else 0
    # on its battery in the power cut (the comp off): the sign's light at the battery's share, on all it lights in the box
    x0, y0, x1, y1 = box
    for y in range(y0, min(y1, cy + chh)):
        for x in range(x0, min(x1, cx + cw)):
            if comp[y - cy, x - cx, 3] == 0 or (x, y) in sign: continue
            add = np.maximum(comp[y - cy, x - cx, :3] - city[y, x, :3], 0.0) * RA.SIGN_BATT
            v = np.round(np.clip(unlit[y, x, :3] + add, 0, 255))
            if np.abs(v - unlit[y, x, :3]).max() > 0: ch[y, x] = True
            unlit[y, x, :3] = v
    save(comp, pc)
    inb = np.zeros((H, W), bool); inb[y0:y1, x0:x1] = True
    assert not (ch & ~inb).any(), 'changed outside the box'
    return ch


def before():
    """once: the zone's before copies (the overlapping zones' own before copies, in their order, over the layers' pixels
    where no zone is)"""
    import redraw_zones as R
    x0, y0, x1, y1 = BOX
    for tag, f in (('city', 'layer_city_off.webp'), ('unlit', 'street_unlit.webp')):
        a = load(os.path.join(ASSETS, f))[y0:y1, x0:x1].copy()
        for name, cfg in R.ZONES.items():
            if name == 'cside': continue
            b = cfg['box']
            ox0, oy0, ox1, oy1 = max(b[0], x0), max(b[1], y0), min(b[2], x1), min(b[3], y1)
            if ox0 >= ox1 or oy0 >= oy1: continue
            z = load(os.path.join(EDITS, '%s_before_%s.webp' % (name, tag)))
            a[oy0 - y0:oy1 - y0, ox0 - x0:ox1 - x0] = z[oy0 - b[1]:oy1 - b[1], ox0 - b[0]:ox1 - b[0]]
        save(a, os.path.join(EDITS, 'cside_before_%s.webp' % tag))
        print('cside_before_%s.webp' % tag, a.shape[1], 'x', a.shape[0])


def preview(out):
    """the wall before and after over the layers as they are (off, lit, power cut), x1 and x6, and its lines"""
    import shutil
    os.makedirs(out, exist_ok=True)
    pc = os.path.join(ASSETS, RA.COMP[0] + '.webp'); keep = open(pc, 'rb').read()
    try:
        L = {t: load(os.path.join(ASSETS, f)) for t, f in (('city', 'layer_city_off.webp'), ('unlit', 'street_unlit.webp'))}
        B = {t: a.copy() for t, a in L.items()}; cb = load(pc)
        ch = draw(L['city'], L['unlit'])
        ca = load(pc)
    finally:
        open(pc, 'wb').write(keep)
    (cx, cy), (cw, chh) = RA.COMP[1], RA.COMP[2]
    def on(a, c):
        o = a.copy(); al = c[..., 3:4] / 255.0
        o[cy:cy + chh, cx:cx + cw, :3] = o[cy:cy + chh, cx:cx + cw, :3] * (1 - al) + c[..., :3] * al
        return o
    x0, y0, x1, y1 = 880, 430, 960, 692
    tiles = [B['city'], L['city'], on(B['city'], cb), on(L['city'], ca), B['unlit'], L['unlit']]
    tiles = [t[y0:y1, x0:x1, :3] for t in tiles]
    for s in (1, 6):
        row = np.concatenate([np.concatenate([t, np.full((t.shape[0], 2, 3), 255.0)], 1) for t in tiles], 1)
        Image.fromarray(np.clip(np.round(row), 0, 255).astype(np.uint8)).resize((row.shape[1] * s, row.shape[0] * s), Image.NEAREST).save(os.path.join(out, 'cside_x%d.png' % s))
    for t in ('city', 'unlit'): save(L[t], os.path.join(out, {'city': 'layer_city_off.webp', 'unlit': 'street_unlit.webp'}[t]))
    save(ca, os.path.join(out, RA.COMP[0] + '.webp'))
    print('changed', int(ch.sum()), 'px; courses', course_rows(), '; base top, wet', base_rows())


if __name__ == '__main__':
    if '--before' in sys.argv: before()
    elif '--preview' in sys.argv: preview(sys.argv[sys.argv.index('--preview') + 1])
    else: print(__doc__)
