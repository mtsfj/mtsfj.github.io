#!/usr/bin/env python3
"""The floor above Naruto's window removed: the building ends a floor lower, its roof a garden.

    python3 tools/naruto_roof.py      (once, on the layers as they are; it stops if the floor is gone already)

(Since redrawn over it by tools/naruto_floor.py, the zone 'narufloor' of tools/redraw_zones.py: the parapet, its coping,
the lip and the near side on the street's vanishing point, the garden set on the new coping with this tool's own plants,
the downpipes; its helpers and its garden() are used from there.)

What was there: over Naruto's window (the overlay WL, x 1188..1268 from y 100) the building rose out of the frame: a balcony
(its railing, its slab's lit lip), the floor's wall behind it, the concrete pillar at its far end (x 1124..1149) and, over
the right house's eave, the floor's near side wall (the painter's teal, x 1288..1376).
What it becomes: the old balcony's slab is the roof. On its lip (kept, the painter's, followed pixel by pixel) stands a
parapet in the lip's own plane (its lines on the building's vanishing point, measured on the old railing and the lip:
(985, 377)), its face the pillar's own concrete one pixel per pixel, a coping on top drawn as a small lip (its top lit by
the sky, the shadow of its edge under it, the grain of the painter's lip); the street lamp's glint on the lip's far end
stays (the old railing's bars over it were as cool as the rest: the glint is the lip's edge's alone). The pillar (the
building's end, by C) now ends with the parapet: the coping runs over it to C's corner, its own face and lit edge under
it, the parapet's face over it too. At the near corner (x 1250) the coping turns and runs level along the near side:
that side (the parapet's end, the slab's end, the side wall over the right house's eave) faces us: the street face's own
concrete at the near side's darker value (the painter's teal as a tint), lighter up high where the sky lights it, rain
streaks under the coping; the corner reads by that step of value (no lit arris beside the menu's "Contact"). The old
balcony's post there (x 1280..1285) is gone. Over the right house's eave, past where it rises over that coping, the sky.
Under the slab, right of the window (x 1256..1316, y 57..311), what the painter had there, redrawn in straight bands (see
STRIP): the street face's last pier to the corner, the roof's downpipe down the corner (where a conduit wavered), the near
side's wall, the right house's corner boards, the shade under the slab's end and the eave with a level edge.
What the floor hid: building C (the zone-5 house beyond, its top y 66) is taller than the new roof, so its corner would
stand against the sky as a card. Its near side wall shows now over the parapet. C's front is a street face (its ledges
run to the right facades' vanishing point, (700, 615)), its coping painted level on rows 66..68 to the corner (x 1123);
its near side faces us (its lines level), so the side's coping runs on from the corner on the same rows: one coping line
turning the corner, no step, no notch of sky (the front coping's own colours, a step darker on the side, its grain
mirrored round), the corner read under it by the painter's dark joint and lit arris (x 1122, 1123) and by the side's
darker wall (at the window's 67-row crop the coping's last two rows run along the frame's top, as C's front's did); boards as
wide as its front's by the corner, in zone 5's tones, with its front's own grain, rain streaks under the coping, a little
of the sky's light under it and darker down by Naruto's roof; as dark as the painter's own near side of Naruto's building
(lum 9 at dusk, both street faces 17: only the eastern sky lights them). Under the near side's face the slab's end: the
lip's band turned round the corner, hardly lighter than the wall. The right house's side wall toward the
building faces away from the street: never seen; its tiles, against the sky now, get the sky's light on their top.
The guard: none drawn; the parapet is the roof's edge as seen from the street (along the street a rail d m back is hidden
by the 0.55 m parapet as long as 1.1 < 0.55 + 1.37 d, d > 0.4 m).
The garden: seen from far below, only what rises over the parapet shows (a plant d m back must be taller than about
0.55 + 1.37 d m), over the street's parapet, against C's side wall and the sky. A Japanese maple in a raised bed toward
the far end (its crown in tiers, x 1134..1202, y 51..~92, about 1.8 m wide at its depth; its forked trunk seen over the
coping; the colours of the painter's red tree beyond the left houses), clipped cushions of shrubs in the planters along the
parapet at the far end, a low clipped hedge along it toward the near corner (the left tree's leaves: dark, their tops lit
by the sky). The menu's text falls on this band at a place that depends on the window (16:9: y 22..42; 1920x950 crops the
scene's top 67 rows, the text then over y ~84..106; 1366x650: 98 rows, ~121..153): the leaves are dark there (the hedge
calmer still under the 16:9 text), and no plant's top or bottom sits at a crop row (y 64..67, 98): the crown goes out of
the frame there as a mass, not as a strip. The small tree that hung into the frame's top over the near corner is gone
(it crowded the menu's "Contact").
The near side takes 0.9 of the street face's light, C's revealed side wall about 0.75 of C's front's.
Where: x 1124..1380, y 0..200; nothing at or under the lip but the slab's end on the near side (x 1250..1295, y 46..56)
and the strip right of the window (x 1256..1316, y 57..311; the window's glass, x 1196..1267 from row 100, untouched),
nothing of C left of x 1124, nothing of the right house under its eave's tiles. In layer_city_off; street_unlit (the
same, but the street lamp's share on the parapet by the lip's lit end, as on the old railing's bars there; the strip
from that layer's own pixels); night_far (0: the street's, the sky's here too) and street_sun (0). Needs Pillow, numpy.
"""
import os
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = lambda p: os.path.join(ROOT, 'assets', p)
SRC = lambda p: os.path.join(ROOT, 'tools', 'src', p)
LUM = np.array([0.299, 0.587, 0.114])

# plane P (the lip's, the old railing's, the pillar's street face): its lines meet at (VX, VY); v is a line's y at x XR
VX, VY, XR = 985.4, 376.9, 1200.0
LIPV = 107.5                     # the lip's first row
PPM = 49.5                       # px per metre at x XR (the old railing, 1.1 m: v 52.9 .. 107.5); it scales as x - VX
X0, XP, XC, XE = 1124, 1150, 1250, 1380   # the pillar's left edge, the lip's first column, the near corner, the zone's end
CTOP = 66                        # building C's coping, its first row
CCOP_K = 0.85                    # C's side coping: its front coping's colours, a step darker (the side turned from the street)
HP, HC = 0.45, 0.10              # the parapet over the lip, its coping (m)
SLAB_END = 45                    # the near side: the parapet's end over the slab's end down to this row; the slab's end under it
SLAB = (46, 56, 1295)            # the slab's end band on the near side (the lip's rows), its shadow row, its last column (the eave's cap)
LIPC = np.array([(26, 37, 72), (21, 32, 60), (17, 26, 45)], float)   # the coping: its lit top, its face, its lower arris (the lip's rows)
SHADE = 0.45                     # the shadow of a coping's edge on the wall's first row under it
TEAL = np.array((0.19, 8.72, 10.98))     # Naruto's old near side wall as the painter coloured it (x 1300..1325, y 18..30)
NEARK = 0.9                      # the near side's light over the street face's
CSIDE = np.array((4.8, 14.4, 23.3))       # building C's near side wall (facing us, as the painter's teal side, a little farther: bluer)
GAM = 0.8                        # the concrete's grain (its relative lightness) to this power on the frontal faces
# building C's planks on its side wall: as wide as its front's boards by its corner (7 to 8 px), the ten tones of the owner's
# tex_wood_planks (as zone 5 gives C's front), a dark seam column, the battens behind the seams (their rows), a nail on each
# board at each batten, the grain of C's front's own boards (their lightness over a 9-row mean), rain streaks under the
# coping; C's coping tinted, on the front's rows, the front coping's grain carried round the corner
PLANK_W = 7.6
WOOD_T = np.array([[28.6, 31.1, 38.4], [33, 31.7, 36.1], [31.4, 30.8, 36.2], [41.4, 40.6, 43.5], [13.8, 16.9, 21.8],
                   [28.2, 30.7, 38.2], [54.2, 50.4, 48.7], [82.9, 75, 67.6], [30.5, 32.1, 38.6], [35.2, 35.1, 38.4]])
BATTENS = ((102, 110), (156, 163))
# the right house's eave: the first row of its tiles' dark outline, x 1296..1380 (measured on the painting)
EAVE = [50, 50, 47, 47, 48, 46, 46, 46, 44, 44, 43, 43, 42, 40, 39, 39, 37, 37, 37, 37, 34, 34, 33, 34, 32, 32, 31, 31, 30, 29,
        29, 29, 27, 26, 25, 24, 24, 23, 23, 22, 21, 20, 20, 19, 19, 18, 17, 16, 18, 15, 16, 14, 14, 12, 11, 10, 11, 10, 10, 8,
        7, 6, 6, 6, 4, 4, 0, 0, 1, 0, 2, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
# the left tree's leaves at dusk, by lightness (its colours)
LEAF = np.array([(1.8, 6.5, 5.5), (3.7, 9.4, 11.6), (7.0, 13.4, 19.2), (11.2, 17.6, 27.1), (17.5, 23.0, 37.3), (25.7, 28.1, 46.8)])
EAVE_LIT = np.array((14, 22, 40))         # the sky's light on the right house's tiles' top, now against the sky
# the garden: the maple's crown in tiers (clumps: centre x, centre y, half width, half height; the later in front), its trunk
# and limbs ((from), (to), width), the shrubs' cushions and the near hedge; the maple in the painter's red tree's colours
# (beyond the left houses, x 350..440, y 410..490: its dark navy clumps, their tops maroon and pink), the shrubs in the
# left tree's (LEAF) with their sky-lit tops; the power cut takes them as it takes the red tree (MUNLIT)
MAPLE = [(1166, 57, 10, 6), (1153, 64, 11, 6), (1179, 63, 12, 7), (1144, 74, 9, 6), (1165, 71, 14, 8), (1189, 75, 10, 6),
         (1154, 84, 12, 6), (1177, 79, 12, 6), (1195, 83, 6, 4), (1140, 87, 6, 4), (1167, 87, 5, 3)]
MAPLE_LIMBS = [((1170, 130), (1168, 101), 3), ((1168, 106), (1156, 88), 2), ((1169, 103), (1180, 87), 2), ((1169, 100), (1167, 90), 1)]
MAPLE_C = np.array([(2, 8, 13), (6, 13, 21), (12, 16, 28), (26, 21, 36), (48, 28, 44), (80, 36, 54), (112, 54, 72)], float)
BARK = np.array([(3, 6, 10), (8, 11, 18), (18, 20, 30)], float)
MUNLIT = np.array((0.90, 0.95, 0.95))
# the shrubs' cushions: x, height over the coping, half width, half height (a row behind, then the front row)
SHRUBS = [(1141, 22, 7, 6), (1154, 21, 8, 6), (1166, 17, 7, 5),
          (1131, 11, 7, 7), (1143, 15, 9, 8), (1156, 12, 9, 7), (1169, 9, 8, 6), (1137, 6, 6, 4)]
HEDGE = (1214, 1243, 8)                  # the near hedge: its first and last columns, its height over the coping
SHRUB = np.vstack([LEAF[:5], [(27, 31, 50), (38, 44, 62)]])        # (their tops lit by the sky over the roof)
SLABC = np.array([(8, 15, 24), (5, 11, 17), (3, 8, 13)], float)   # the slab's end on the near side: its lit top, its face, its lower arris
# the strip right of the window, under the slab's end band down to the dark box over the awning (x 1268..1316, y 57..311):
# the painter had a pier of the street face whose edge wandered, a conduit wavering down the corner, a diagonal shadow
# smeared over the near side and the right house's corner boards; redrawn as straight bands, each in the painter's own
# colour for it (its medians over the rows where it is clean, taken in each layer): the street face's last pier to the
# corner (x 1268..1278, its lit top on the building's lines), the roof's downpipe in front of the corner (a cylinder lit
# from the street like the painter's far one, a socket under the slab, two clamps), the near side's wall in the shade of
# the pipe, the right house's corner boards column by column as painted; dark under the slab's end and the eave (the
# painter's shade, a level edge with a mid row), lit under it
STRIP = (57, 312)                # its rows (the box over the awning from row 312)
SH_ROW = 82                      # the shade's edge on the near side: dark above, this row mid, lit under
PIER = (1268, 1278)              # the street face's last pier (the window's glass ends at x 1267), the corner at x 1278
PIER_V, PIER_LOW = 164.0, 209    # its lit top on the building's lines (v at XR, through (1270.5, 94) as painted, the top of the
                                 # window's last narrow pane x 1264..1267 at row 100 on it too); from row 209 the balcony's railing
                                 # stands in front of it (x 1268..1277 kept as painted there)
SOFFIT = (1256, 1267, 70, 100)   # over the window's last panes: the shade under the slab, a faint line the painter ran down to
                                 # the right across it (from the old balcony's underside, on no line of the building) gone
PIPE_X = 1281                    # the downpipe's body x 1281..1287, its outline x 1280, the corner's shade x 1279, its own x 1288..1289
PIPE_K = (0.7, 1.0, 1.0, 0.9, 0.85, 0.7, 0.5)   # across it (the painter's far downpipe's profile)
PIPE_BANDS = (57, 140, 226)      # its socket under the slab, its clamps (a lit edge over a dark band)
SIDE = (1290, 1296)              # the near side's wall (the painter's panel x 1292..1296)
BOARDS = (1297, 1316)            # the right house's corner boards, as painted column by column (the eave's shade over rows 57..61)


def load(p, mode='RGBA'):
    return np.asarray(Image.open(A(p)).convert(mode)).astype(float)


def save(arr, p, mode):
    Image.fromarray(np.clip(np.round(arr), 0, 255).astype(np.uint8), mode).save(A(p), 'WEBP', lossless=True, quality=100, method=6, exact=True)


def yv(x, v): return VY + (v - VY) * (x - VX) / (XR - VX)
def ry(x, v): return int(np.floor(yv(x, v) + 0.5))
def sc(x): return PPM * (x - VX) / (XR - VX)
def front_rows(x):
    """plane P at column x: (the coping's first row, the parapet face's first row, the lip's first row)"""
    vp = LIPV - HP * PPM
    return ry(x, vp - HC * PPM), ry(x, vp), ry(x, LIPV)


class Layers:
    def __init__(s):
        s.city, s.unlit = load('layer_city_off.webp'), load('street_unlit.webp')
        s.nf, s.sun = load('night_far.webp', 'RGB'), load('street_sun.webp', 'RGB')
        s.H, s.W = s.city.shape[:2]
    def put(s, x, y, rgb, unlit=None):
        if 0 <= y < s.H and 0 <= x < s.W:
            s.city[y, x, :3] = rgb; s.city[y, x, 3] = 255
            s.unlit[y, x, :3] = rgb if unlit is None else unlit; s.unlit[y, x, 3] = 255
            s.nf[y, x] = 0; s.sun[y, x] = 0
    def clear(s, x, y):
        s.city[y, x] = 0; s.unlit[y, x] = 0; s.nf[y, x] = 0; s.sun[y, x] = 0
    def shade(s, x, y, k):
        s.city[y, x, :3] *= k; s.unlit[y, x, :3] *= k
    def save(s):
        save(s.city, 'layer_city_off.webp', 'RGBA'); save(s.unlit, 'street_unlit.webp', 'RGBA')
        save(s.nf, 'night_far.webp', 'RGB'); save(s.sun, 'street_sun.webp', 'RGB')


def cop(i, n, k=1.0, g=1.0):
    """a coping's row i of n: its top lit by the sky, its face (k: its light, less turned from the street), its lower arris;
    g: the grain of the painter's lip or coping at that pixel"""
    return (LIPC[0] if i == 0 else (LIPC[2] if i == n - 1 else LIPC[1]) * k) * g


def lip_grain(Lc, lip):
    """the painter's lip, its rows 0..2 from its first lit one, x 1170..1249 (clear of the lamp's glint): each pixel's
    lightness over its row's mean, the grain of the new copings and of the slab's end (no flat fill)"""
    rows = np.array([[Lc[lip[x] + r, x] for x in range(1170, XC)] for r in range(3)]) + 1.0
    return np.clip(rows / rows.mean(1, keepdims=True), 0.75, 1.3)


def rel_at(rel, i, j, seed):
    """the concrete's grain for a frontal face's pixel (i, j): strips of the pillar's columns side by side, mirrored by turns,
    each from its own rows (no repeat in sight)"""
    th, tw = rel.shape
    k, u = divmod(i + 7 * seed, tw); u = u if k % 2 == 0 else tw - 1 - u
    return rel[(j + 37 * k + 11 * seed) % th, u]


def pil_at(pil, i, j):
    """the parapet's face at its pixel (i, j) (columns from its far end, rows from its top): the pillar's concrete one pixel
    per pixel (the scene's grain), strips of its columns 1..17 (its dark edge column left out) side by side, mirrored by
    turns, each from its own rows near the pillar's top"""
    th, tw = pil.shape[:2]; n = tw - 2
    k, u = divmod(i, n); u = 1 + (u if k % 2 == 0 else n - 1 - u)
    return pil[(j + (k * 23) % 40) % th, u]


def streaks(n, seed, p, lmax):
    """rain streaks under a coping: per column, the length of a darker run (0: none)"""
    rng = np.random.default_rng(seed); out = np.zeros(n, int)
    for i in range(n):
        if rng.random() < p: out[i] = rng.integers(2, lmax + 1)
    return out


def plank(i, y, grain):
    """C's planks' albedo (over its old concrete's) at column i from its corner, row y: the board's tone, its seam (lit where
    a batten is behind it), a nail on the board's middle at each batten, the grain of a board of C's front (grain: its
    columns' lightness over their 9-row mean, mirrored by turns down the wall), each board's from its own columns and rows"""
    n = int(np.floor(i / PLANK_W)); tone = WOOD_T[(n * 7 + 3) % 10]; lt = tone @ LUM
    a = 0.95 * (1 + 0.45 * (lt / 37.0 - 1)) * (1 + 0.6 * (tone / lt - 1))
    bat = [b for b in BATTENS if b[0] <= y <= b[1]]
    if int(np.floor((i - 1) / PLANK_W)) != n: return a * 0.65 * (1.3 if bat else 1.0)
    if bat and y == (bat[0][0] + bat[0][1]) // 2 and i == int(n * PLANK_W + PLANK_W / 2): return a * 0.6
    gh, gw = grain.shape
    return a * grain[(y - CTOP + 23 * n) % gh, (i - int(np.ceil(n * PLANK_W)) + 5 * n) % gw] ** 1.4 * 1.06


def lamp(x, y):
    """the street lamp's share of a new pixel's colour near the lip's lit end (as on the old railing's bars there)"""
    d = np.hypot((x - 1152) / 30.0, (y - 160) / 26.0)
    return max(0.0, 0.32 * (1.0 - d)) if x < 1192 else 0.0


def main():
    Ls = Layers()
    if Ls.city[5, 1240, 3] == 0 and Ls.city[30, 1180, 3] == 0:   # (the old floor there: the sky once cut)
        print('naruto_roof: the floor is gone already, nothing done'); return
    sun0 = Ls.sun[:, :, 0].copy()                          # (the lamp's glint on the lip's end: its pixels stay)
    Lc = Ls.city[:, :, :3] @ LUM
    lip = {}                                               # the lip's first row as painted (its stair steps), within a row of the line
    for x in range(XP, XC):
        r = ry(x, LIPV); f = next((y for y in range(r - 1, r + 2) if Lc[y, x] >= 20), r); lip[x] = f
    pil = Ls.city[0:171, 1125:1144, :3].copy()              # the pillar's street face over the slab: the painter's concrete
    rel = (pil @ LUM) / (pil.reshape(-1, 3).mean(0) @ LUM)  # (its grain)
    lg = lip_grain(Lc, lip); nl = lg.shape[1]
    Lt = Lc[0:18, 1310:1341] + 1.0; mt = np.clip(Lt / Lt.mean(), 0.85, 1.15)   # (the painter's teal on the old near side wall: its mottling)
    cg = lambda i, n, x: lg[0 if i == 0 else 2 if i == n - 1 else 1, (x + 29 * i) % nl]
    eave = {1296 + i: e for i, e in enumerate(EAVE)}
    for x in range(1341, XE + 1):                         # (against the sky now, the tiles' top made a clean stair: a notch of
        e = min(eave[x], eave[x - 1])                     # the old wall between two tile ends is filled with the tile's outline)
        for y in range(e, eave[x]): Ls.put(x, y, Ls.city[eave[x], x, :3], Ls.unlit[eave[x], x, :3])
        eave[x] = e
    yt = front_rows(XC - 1)[0]; ncs = front_rows(XC - 1)[1] - yt      # the near side's coping, level, as high as the corner's

    # the new top per column; all above it goes (the sky: transparent, night_far and street_sun 0, as the sky was here)
    top = {}
    for x in range(X0, XE + 1):
        if x < XC: t = front_rows(x)[0]
        else: t = min(yt, eave[x]) if x >= 1300 else yt
        top[x] = t
        for y in range(0, max(t, 0)): Ls.clear(x, y)

    # building C's near side wall, from its coping (carried round its corner, level, a row thicker) down to the building's
    # new top: its planks face on, in the light of a side turned from the street, rain streaks under the coping
    Lf = Ls.city[160:211, 1067:1121, :3] @ LUM + 1.0     # (C's front's boards under its diagonal band, x 1067..1120: their grain)
    Lp = np.concatenate([Lf[:1].repeat(4, 0), Lf, Lf[-1:].repeat(4, 0)]); cs = np.concatenate([np.zeros((1, Lf.shape[1])), Lp.cumsum(0)])
    grain = np.clip(Lf / ((cs[9:] - cs[:-9]) / 9.0), 0.8, 1.2); grain = np.concatenate([grain, grain[::-1]])
    cf = Ls.city[CTOP:CTOP + 3, 1067:X0 - 1, :3]; Lcf = cf @ LUM + 1.0   # (C's front's coping, x 1067..1122, as painted)
    ok = Lcf > 0.6 * np.median(Lcf, 1, keepdims=True)                   # (its joints left out of its colours)
    crow = np.array([cf[j][ok[j]].mean(0) for j in range(3)]); mrow = np.array([Lcf[j][ok[j]].mean() for j in range(3)])
    gcf = np.clip(Lcf / mrow[:, None], 0.7, 1.4); ncf = gcf.shape[1]
    stc = streaks(XE - X0 + 1, 13, 0.2, 30)
    for x in range(X0, XE + 1):
        u = (x - X0) % (2 * ncf); u = ncf - 1 - u if u < ncf else u - ncf     # (mirrored round the corner, by turns)
        for y in range(CTOP, top[x]):
            j = y - CTOP
            if j < 3: col = crow[j] * gcf[j, u] * CCOP_K               # (the front's coping carried round, on its rows)
            else:
                drift = (1.0 + 0.1 * max(0.0, 1.0 - (j - 4) / 8.0) if j > 3 else 1.0) * (1.0 - 0.3 * max(0.0, 1.0 - (top[x] - 1 - y) / 15.0))
                col = CSIDE * plank(x - X0, y, grain) * drift * (SHADE if j == 3 else 0.82 if j - 3 < stc[x - X0] else 1.0)
            Ls.put(x, y, col)

    # the front: the coping, from the near corner to C's corner (over the old pillar too, which now ends with the parapet),
    # the parapet's face down to the lip (over the pillar: down to the lip's line, the pillar's own face and lit edge under it)
    for x in range(X0, XC):
        ya, yb, yl = front_rows(x)
        for i, y in enumerate(range(ya, yb)):
            c = cop(i, yb - ya, 0.65, cg(i, yb - ya, x)) * (0.6 if x == X0 else 0.9 if i == 0 else 1.0)   # (its lit top, its face in shade below it; no lit end against C's wall)
            Ls.put(x, y, c * (1 + lamp(x, y)), c)
        for y in range(yb, lip[x] if x >= XP else yl):
            if sun0[y, x] > 0: continue
            c = pil_at(pil, x - X0 + 9, y - yb) * (SHADE if y == yb else 1.0)
            Ls.put(x, y, c * (1 + lamp(x, y)), c)

    # the near side: the level coping, the wall under it: the street face's own concrete at the near side's darker value
    # (the painter's teal as a tint only), a little more of the sky's light up high; the corner reads by that value step
    st = streaks(XE - XC + 1, 9, 0.2, 9)
    for x in range(XC, XE + 1):
        bot = SLAB_END if x < 1300 else eave[x] - 1
        for y in range(yt, bot + 1):
            j = y - yt
            if j < ncs: Ls.put(x, y, cop(j, ncs, 0.5, cg(j, ncs, x + 31))); continue
            lift = 1.0 + 0.3 * max(0.0, 1.0 - (j - ncs) / 26.0) + 0.12 * max(0.0, 1.0 - (x - XC) / 30.0)
            u, v = (x - XC) % 60, (j - ncs) % 34; u, v = (u if u < 30 else 59 - u), (v if v < 17 else 33 - v)
            c = (pil_at(pil, x - XC + 3, j - ncs) * NEARK * 0.65 + TEAL * mt[v, u] * 0.35) * lift
            Ls.put(x, y, c * (SHADE if j == ncs else 1.0) * (0.8 if ncs < j <= ncs + st[x - XC] else 1.0))
    # the slab's end under it, on the near side: the lip's band turned round the corner, level, in the near side's light (the
    # concrete's grain, its top edge lit, hardly lighter than the wall over it), its shadow under it (the old balcony's
    # post that stood there, x 1280..1285, goes with the strip under it)
    for x in range(XC, SLAB[2] + 1):
        for y in range(SLAB[0], SLAB[1]):
            j = y - SLAB[0]; n = SLAB[1] - SLAB[0]
            r = 0 if j == 0 else 2 if j == n - 1 else 1; c = SLABC[r] * lg[r, (x + 17 * j) % nl]
            Ls.put(x, y, c * (0.72 if x == SLAB[2] else 0.86 if x == SLAB[2] - 1 else 1.0))   # (the eave's shade on its end)
    for x in range(XC, SLAB[2] + 1): Ls.shade(x, SLAB[1], SHADE)
    # the right house's tiles, now against the sky: the sky's light on their top
    for x in range(XC, XE + 1):
        if x >= 1300 and top[x] == eave[x] and eave[x] > 0:
            Ls.put(x, eave[x], Ls.city[eave[x], x, :3] * 0.3 + EAVE_LIT * 0.7, Ls.unlit[eave[x], x, :3] * 0.3 + EAVE_LIT * 0.7)

    strip(Ls)
    garden(Ls)
    Ls.save()
    print('naruto_roof: done')


def strip(Ls):
    """the strip right of the window (STRIP): per column, its colour in the shade (rows 62..80 as painted), lit (rows 100..200),
    the boards under the eave (rows 57..59), each a median of the painter's pixels in each layer, then the bands drawn"""
    y0, y1 = STRIP
    for lay in (Ls.city, Ls.unlit):
        med = lambda xs, ys: np.median(lay[ys[0]:ys[1], xs[0]:xs[1] + 1, :3].reshape(-1, 3), 0)
        dark, dark_t = med((1301, 1304), (100, 200)), med((1268, 1275), (60, 80))
        pier = {x: med((x, x), (120, 200)) for x in range(PIER[0], 1276)}; pl = med((1272, 1275), (120, 200))
        side, side_t = med((1292, 1296), (100, 140)), med((1290, 1296), (62, 80))
        p = lay[90:300, PIPE_X + 1:PIPE_X + 8, :3].reshape(-1, 3); pipe = np.median(p[p @ LUM > 15], 0)
        brd = {x: (med((x, x), (57, 59)), med((x, x), (62, 80)), med((x, x), (100, 200))) for x in range(BOARDS[0], BOARDS[1] + 1)}
        col = {}
        sh = np.clip(side_t / np.maximum(side, 1.0), 0.0, 1.0)          # (the shade's own tint, as on the near side's wall)
        lt = dark_t @ LUM + 1.0
        shade = lambda x, y: lay[y, x, :3].copy() if lay[y, x, :3] @ LUM < lt else dark_t   # (the painter's dark kept, what was lit in it gone)
        for x in range(SOFFIT[0], SOFFIT[1] + 1):                       # (the window's head: its glass from row 100 untouched)
            for y in range(SOFFIT[2] if x < 1264 else y0, SOFFIT[3]):
                col[(x, y)] = pier.get(PIER[0], pl) if x >= 1264 and y + 0.5 >= yv(x + 0.5, PIER_V) else shade(x, y)
        for x in range(PIER[0], BOARDS[1] + 1):
            for y in range(y0, y1):
                k = 0.0 if y < SH_ROW else 0.5 if y == SH_ROW else 1.0            # (the shade's edge on the near side)
                if x <= PIER[1]:
                    if x < PIER[1] and y >= PIER_LOW: continue
                    c = pier.get(x, pl) if y + 0.5 >= yv(x + 0.5, PIER_V) else shade(x, y)
                elif x < PIPE_X or PIPE_X + 7 <= x < SIDE[0]: c = dark
                elif x < PIPE_X + 7:
                    c = pipe * PIPE_K[x - PIPE_X] * (sh + (1.0 - sh) * k)
                    for b in PIPE_BANDS: c = c * (1.25 if y == b else 0.55 if y == b + 1 else 1.0)
                elif x <= SIDE[1]: c = side_t + (side - side_t) * k
                else:
                    e, t, l = brd[x]; c = e if y < 62 else t + (l - t) * k
                col[(x, y)] = c
        for (x, y), c in col.items():
            lay[y, x, :3] = c; lay[y, x, 3] = 255
    for (x, y) in col: Ls.nf[y, x] = 0; Ls.sun[y, x] = 0


def foliage(clumps, rank, seed, clip, lift=0.0, rim=1.6, spots=0.0):
    """a mass of leaves: its clumps (centre x, centre y, half width, half height), the later ones in front; each clump's
    edge ragged (bumps of 2 to 4 px, a leaf or two out, a leaf or two missing, from the leaves' grain), its light from
    above (the sky): its top a step lighter, its rim lighter still, its underside dark and darker where it overhangs
    the clump under it; spots: clusters of lit leaves on its upper half, dark gaps between the leaves, its rim broken where
    a gap meets it (the leaves' grain). clip(x, y): where a leaf may be (above the parapet's coping). Returns {(x, y): step}"""
    rng = np.random.default_rng(seed); th, tw = rank.shape
    own = {}
    for k, (cx, cy, rx, ry) in enumerate(clumps):
        nb = 24; bump = np.convolve(rng.random(nb + 4), np.ones(3) / 3, 'valid')[:nb]   # (the edge's bumps, by angle)
        for y in range(int(cy - ry - 3), int(cy + ry + 3)):
            for x in range(int(cx - rx - 3), int(cx + rx + 4)):
                nx, ny = (x - cx) / rx, (y - cy) / ry; d = np.hypot(nx, ny)
                a = (np.arctan2(ny, nx) / (2 * np.pi) + 0.5) * nb; e = bump[int(a) % nb] * (1 - a % 1) + bump[int(a + 1) % nb] * (a % 1)
                g = rank[(y + 13 * seed) % th, (x + 7 * seed) % tw]
                lim = 1.0 + 0.32 * (e - 0.5) / max(rx, ry) * 6 + (0.12 if g < 0.12 else -0.1 if g > 0.85 else 0.0)
                if d <= lim and clip(x, y): own[(x, y)] = (k, nx, ny, g, d / lim)
    px = {}
    for (x, y), (k, nx, ny, g, dd) in own.items():
        up = own.get((x, y - 1)); up2 = own.get((x, y - 2))
        l = 2.4 + lift - 2.3 * ny - 0.35 * nx + 1.6 * (g - 0.5)               # (lit from above, a little from the left)
        if up is None or up[0] < k: l += rim * (0.5 if spots and g > 0.8 else 1.0)   # (its rim against the sky or the clump behind)
        elif up2 is None or up2[0] < k: l += 0.45 * rim
        dn = own.get((x, y + 2))
        if dn is not None and dn[0] > k: l -= 1.2                              # (the shade over the clump in front, under it)
        if dd > 0.86 and ny > 0.2: l -= 0.8                                    # (the underside's edge)
        if spots and g < 0.2 and ny < 0.35: l = max(l, 3.2 + spots - 1.2 * ny)   # (a cluster of lit leaves)
        elif spots and g > 0.78 and ny > -0.6: l -= spots                      # (a gap between the leaves)
        px[(x, y)] = int(np.clip(np.round(l), 0, 6))
    for q in [q for q in px if sum((q[0] + i, q[1] + j) in px for i, j in ((1, 0), (-1, 0), (0, 1), (0, -1))) <= 1]:
        del px[q]                                                              # (no leaf alone or dangling)
    return px


def garden(Ls):
    """the roof garden, seen from below over the street's parapet: a Japanese maple in a raised bed near the far end (its
    crown in tiers like the painter's red tree beyond the left houses, in its colours; its forked trunk seen over the
    coping), clipped cushions of shrubs in the planters behind the parapet (the left tree's leaves: dark, their tops
    lit by the sky), a low clipped hedge toward the near corner. Their tops sit clear of the window's top edge at the
    crops of the scene's top (y 64..67 and 98: a crown going out of frame there, never a strip of leaves) and of C's
    coping (y 66..68), their bases hidden by the parapet, nothing left of x 1130 (C's corner)"""
    leaves = np.asarray(Image.open(SRC('naruto_roof_leaves.png')).convert('RGB')).astype(float) @ LUM
    th, tw = leaves.shape; rank = np.argsort(np.argsort(leaves.ravel())).reshape(th, tw) / (th * tw - 1.0)
    cop_top = lambda x: front_rows(x)[0]
    clip = lambda x, y: X0 + 6 <= x < XC and 0 <= y < cop_top(x)
    def paint(px, pal, dark=None):
        for (x, y), k in px.items():
            if dark is not None and dark(x, y): k = min(k, 3)               # (calm and dark under the menu's text)
            c = pal[k]; Ls.put(x, y, c * (1 + lamp(x, y)), c * MUNLIT)
    # the maple's trunk and limbs (behind its crown and the shrubs)
    tr = {}
    for (x0, y0), (x1, y1), w in MAPLE_LIMBS:
        n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
        for i in range(n + 1):
            f = i / n; x, y = int(round(x0 + (x1 - x0) * f)), int(round(y0 + (y1 - y0) * f))
            for j in range(w):
                if clip(x + j, y): tr[(x + j, y)] = 2 if j == 0 else (1 if j < w - 1 else 0)   # (its left side lit by the sky)
    for (x, y), k in tr.items(): Ls.put(x, y, BARK[k], BARK[k] * MUNLIT)
    paint(foliage(MAPLE, rank, 3, clip, 0.0, 2.0, 1.2), MAPLE_C)
    paint(foliage([(x, cop_top(x) - h + ry, rx, ry) for x, h, rx, ry in SHRUBS], rank, 7, clip, -1.3, 3.2, 0.9), SHRUB)
    rng = np.random.default_rng(21); hx = list(range(HEDGE[0], HEDGE[1], 4))
    hedge = [(x, cop_top(x) - HEDGE[2] + 4 + int(rng.integers(-1, 2)), 4, 4) for x in hx]
    paint(foliage(hedge, rank, 9, clip, 0.4), SHRUB, lambda x, y: y < 44)


if __name__ == '__main__':
    main()
