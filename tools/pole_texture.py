#!/usr/bin/env python3
"""The right pole's concrete, redrawn: a cylinder in the painter's light, weathered cast concrete wrapped on it, its
bands, bolt and conduits clean (the owner: "texture poto").

    (a module: tools/redraw_zones.py's zone 'poletex' calls draw() on the street as the zones before it leave it;
     then its zone 'polelamp', tools/pole_lamp.py, the street lamp it carries)
    python3 tools/pole_texture.py --preview DIR   (only shows it: the zone drawn on the layers as they are, before and
                                                   after, x4, in DIR; run it on layers without the zone (the commit
                                                   before it); nothing in the repository changes)

What was there: a column of near black green (the painter's body, 0-5 of 255) with a lit stripe down its left edge, a
dark outline either side, two thin conduits, an orange rim down its right edge with gaps, and between 176 and 476 a
stack of bands, a lit "elbow", a pink ring and the ghosts of more, all of it smeared (a survey and the owner: "redo the
pole's texture: a real concrete pole"). Now each row is a cylinder (its columns 1023..1063 down to row 454, the house's
lit edge at 1064 left as it is; 1023..1064 under it, where its dark right limb is, as the foot, tools/pole_foot.py),
every pixel shaded from the normal of the surface it shows:
- its lit side: the light from the left (the street lamp on its arm, the open street beyond it), its share falling
  off round the cylinder as a side light's does (not in a stripe), at the colour the painter lit its left edge row by
  row (in the street and in the power cut each, the lamp's share with it: the brightest of his columns 1024..1032, over
  his hardware's rows and his pink accents filled from round them; its light smoothed down the pole, its hue slower
  still, so no tinted patch);
- its shade: concrete in the night's navy (a share of the power cut's lit side, the same in both layers: the painter's
  black green read as a metal tube), the front a little lighter than the turning sides, the side away from the light
  darker;
- its rim: the painter's light on its right edge (his columns 1059..1063, gaps filled, smoothed): the low sun's warm
  line on its upper part, the night's cool one under it; the street's sun mask (street_sun.webp) follows it, warm
  where it is warm, so the night turns it cool as before;
- its concrete: a generated photograph of weathered cast concrete, square on in overcast light (tools/src/edits/
  pole_concrete_src.webp, the left panel of the sheet painted on 24/11 for the arcade's strip, its prompt beside it:
  pole_concrete_prompt.txt), wrapped on the cylinder at the pole's true scale (the street's camera: f 960 px, the foot
  8.89 m away, 108 px a metre, the pole 0.39 m across; the photograph 3.07 mm a pixel): u round the visible half (each
  pixel the mean of the photograph over the arc it shows, wider toward the limbs), v down its height, the rain streaks
  straight down it, and its finest grain (what that mean averages away) at the pixel's centre, as the painting keeps a
  grain; only its relative light (its luminance over its own mean: the damp foot as it is; the mottling, the streaks
  and the hairline cracks half as much again, to read in the night's light) multiplies the pole's own light, in the pole's own hue (one tone per plane). Three takes up the
  pole so nothing repeats, each from other columns of the photograph (the top one mirrored), each seam under a band:
  the foot's from the sidewalk to the band at 423 (the photograph's whole height, its damp foot on the sidewalk), then
  to the band at 268 and to the cap, each from the photograph's top (its streaks run down from under the band);
- no outline: the limbs are the cylinder's own, the lit one bright against the wall, the far one dark (R12);
- its cap (tools/pole_cut.py's, inside its own outline): the same concrete, its dome lit from above by the sky;
- its hardware, crisp: a band under the cap; the street lamp's two bands (its bracket and arm: tools/pole_lamp.py);
  a band where the painter's lines were at 268, 313 and 423 (steel: their top edge lit, a glint where the light meets
  the eye, their lower edge dark, a line of shadow under each); the painter's pink ring a bolt (a round head on a
  square washer, a little left of his ring, clear of the conduit: lit upper left in steps, its shadow lower right); the
  two conduits straight from the band under the cap down into the sidewalk (small
  pipes, lit on their left, a thin shadow on the pole to their right where the pole is lit), under the bands; the
  painter's stray dash under the sign (684) gone (R7);
- the sign that was wrapped round it (うちは眼科 under the Uchiha fan, rows 522..661) gone (the owner: "vire le truc
  Uchiha du poteau : on a déjà assez de références à Naruto"): the concrete runs through, its light measured over the
  whole pole at once with the sign's rows left out;
- what stays as it is: the foot's shape and its ground (tools/pole_foot.py: its ellipse, its last rows darker, redrawn here in the new concrete, the ground's
  occlusion and the lamp's light on the ground untouched); the pole's trace (COCC in street.js) and its silhouette.
The street and the power cut each from their own pixels (only the lit side's colour differs between them: the lamp).
Needs Pillow, numpy, scipy.
"""
import os
import sys
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, median_filter, uniform_filter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDITS = os.path.join(ROOT, 'tools', 'src', 'edits')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

BOX = (1005, 44, 1070, 757)                     # the zone (redraw_zones.py 'poletex')
UPPER = (61, 454, 1023, 1063)                   # the body: rows, columns (the house's lit edge at 1064 above)
LOWER = (455, 753, 1023, 1064)                  # from where its dark right limb is 1064, to the foot (tools/pole_foot.py's)
CAP = (50, 61)                                  # the cap's rows (tools/pole_cut.py), reshaded inside its alpha
LIT_COLS = (1024, 1032)                         # where the painter's lit side is (its brightest pixel, row by row)
RIM_COLS = (1059, 1064)                         # and his rim
HW = [(76, 86), (172, 232), (258, 346), (416, 478), (518, 666), (680, 690)]   # his hardware's and the sign's rows: not
                                                # measured, filled round
RIM_HW = [(76, 86), (174, 208), (518, 666)]     # (on his rim: the old clamp's, the sign's)
LIGHT = np.array([-1.0, -0.06]) / np.hypot(1.0, 0.06)  # the light on the pole's side (X right, Z away from us)
POW = 1.8                                       # (how fast the lit side falls off round the cylinder)
U_EDGE = -0.83                                  # where the painter's lit edge is (its columns 1025..1027)
KB = 0.22                                       # the shade: this share of the power cut's lit side
SHADE_SIDE = 0.35                               # (the side away from the light: this much darker)
RIM = (0.74, 0.93)                              # the rim: its rise round the right limb (u)
BANDS = [(80, 3), (183, 4), (215, 4), (268, 3), (313, 3), (423, 3)]   # (top row, rows): steel bands round the pole
                                                # (183, 215: the street lamp's, tools/pole_lamp.py STRAPS)
BOLT = (1032.5, 329.5, 2.6)                     # the bolt (the painter's pink ring): its centre, radius (px)
CONDUITS = [(1038, 1040), (1052, 1054)]         # two small pipes up its face (their columns)
CONDUIT_TOP = 83                                # (they start under the band below the cap)
TEX = os.path.join(EDITS, 'pole_concrete_src.webp')   # the concrete (494 x 1000: its wall rows 0..967, the pavement under)
TEX_FOOT = 968                                  # (its wall's foot: the pavement from there)
TEX_MEAN = (100, 600)                           # (its mean light measured over these rows: dry, under the eave's band)
TEX_M = 0.00307                                 # its metres a pixel (1.5 m x 3 m over 494 x 968)
POLE_M = 8.89 / 960.0                           # the pole's metres a pixel (tools/pole_foot.py: ZP / FOC)
Y_GROUND = 615.0 + 960.0 * (1.41 - 0.15) / 8.89 # (its axis's foot on the sidewalk, the row: the photograph's foot there)
TEX_K = 1.5                                     # its mottling and streaks, half as much again (to read at night); its
                                                # light down the wall (the damp foot) and its grain as they are
GRAIN_K = 1.0                                   # its grain kept (the painting's grain: the photograph's own, at its pixel)
TAKES = [(61, 267, 'top', 4, 148, True),        # (scene rows, the take's anchor, the photograph's row there, its first
         (271, 422, 'top', 4, 297, False),      #  column, mirrored): under the cap, between the bands at 268 and 423,
         (426, 760, 'foot', TEX_FOOT, 0, False)]  # and from that band to the sidewalk
LUMA = np.array([0.299, 0.587, 0.114])


def body_rows(y):
    """The pole's columns at row y (x0, x1 inclusive) and its axis and radius, or None."""
    for y0, y1, x0, x1 in (UPPER, LOWER):
        if y0 <= y <= y1: return x0, x1, 0.5 * (x0 + x1 + 1), 0.5 * (x1 + 1 - x0)
    return None


def measure(arr, rows, cols, sigma, hw=HW, cool=False):
    """The painter's colour row by row (the brightest of cols in each row), his hardware's rows filled from round them
    (and, `cool`, the rows where that pixel is warm: his pink accents on the lit side), smoothed down the pole: an array
    over rows[0]..rows[1]."""
    y0, y1 = rows; ys = np.arange(y0, y1 + 1)
    sub = arr[y0:y1 + 1, cols[0]:cols[1] + 1, :3]
    i = np.argmax(sub @ LUMA, 1); c = sub[np.arange(len(ys)), i]
    ok = np.ones(len(ys), bool)
    for a, b in hw: ok &= ~((ys >= a) & (ys <= b))
    if cool: ok &= c[:, 0] <= c[:, 2] + 2
    out = np.stack([np.interp(ys, ys[ok], c[ok, k]) for k in range(3)], -1)
    out = median_filter(out, size=(31, 1), mode='nearest')
    return gaussian_filter(out, (sigma, 0), mode='nearest')


def measure_rim(arr, rows):
    """The painter's rim row by row: the low sun's warm line where his rim is warm (from its first warm row to its last,
    his gaps in it filled from the warm rows round them), his cool rim elsewhere; smoothed, its end faded."""
    y0, y1 = rows; ys = np.arange(y0, y1 + 1)
    sub = arr[y0:y1 + 1, RIM_COLS[0]:RIM_COLS[1] + 1, :3]
    i = np.argmax(sub @ LUMA, 1); c = sub[np.arange(len(ys)), i]
    hw = np.zeros(len(ys), bool)                # (only the old clamp and the band rows: his warm rim runs past the rest)
    for a, b in RIM_HW: hw |= (ys >= a) & (ys <= b)
    warm = (c[:, 0] > c[:, 2] + 30) & ~hw
    cool = measure(arr, rows, RIM_COLS, 3.0, cool=True)
    if warm.sum() < 8: return cool
    wy = ys[warm]; a, b = wy.min(), wy.max()
    wc = np.stack([np.interp(ys, wy, median_filter(c[warm, k], 9, mode='nearest')) for k in range(3)], -1)
    wc = gaussian_filter(wc, (4, 0), mode='nearest')
    k = np.clip((ys - a + 0.5) / 6.0, 0, 1) * np.clip((b - ys + 0.5) / 10.0, 0, 1)   # (in over 6 rows, out over 10)
    return wc * k[:, None] + cool * (1 - k[:, None])


def even(E, s_lum=10.0, s_hue=40.0):
    """The lit side's colour down the pole: its light as the painter's (smoothed), its hue slower still (no tinted
    patches: his pink accents gone with his hardware)."""
    lum = np.maximum(E @ LUMA, 1.0)
    hue = gaussian_filter(E / lum[:, None], (s_hue, 0), mode='nearest')
    return hue * gaussian_filter(lum, s_lum, mode='nearest')[:, None]


def f_lit(u):
    """The light's share on the cylinder at u (-1 the left limb, 1 the right), 1 at the painter's lit edge."""
    def raw(u):
        nx, nz = u, -np.sqrt(np.clip(1 - u * u, 0, 1))
        return np.clip(nx * LIGHT[0] + nz * LIGHT[1], 0, 1) ** POW
    return raw(np.asarray(u, float)) / raw(np.array(U_EDGE))


def g_rim(u):
    t = np.clip((np.asarray(u, float) - RIM[0]) / (RIM[1] - RIM[0]), 0, 1)
    return t * t * (3 - 2 * t)


def ambient(u):
    u = np.asarray(u, float)
    t = np.clip((u - 0.05) / 0.55, 0, 1)
    return (0.7 + 0.3 * np.sqrt(np.clip(1 - u * u, 0, 1))) * (1 - SHADE_SIDE * t * t * (3 - 2 * t))


class Concrete:
    """The photograph's relative light, wrapped on the pole: at(y, u0, u1, r) is the mean of the photograph over the arc
    (u0..u1, -1 the left limb) and the row y of the pole shows, over its own mean."""
    def __init__(self):
        a = np.asarray(Image.open(TEX).convert('RGB')).astype(float)[:TEX_FOOT]
        L = a @ LUMA
        L /= L[TEX_MEAN[0]:TEX_MEAN[1]].mean()
        self.h, self.w = L.shape
        self.T = gaussian_filter(L.mean(1), 20, mode='nearest')   # (its light down the wall: the damp foot, as it is)
        M = L / self.T[:, None]                 # (and over it, its mottling and streaks)
        self.S = np.zeros((self.h + 1, self.w + 1)); self.S[1:, 1:] = M.cumsum(0).cumsum(1)
        self.k = POLE_M / TEX_M                 # (the photograph's pixels in one of the pole's)
        n = int(round(self.k))                  # its grain: what the mean over one of the pole's pixels averages away
        self.F = L - uniform_filter(L, n, mode='reflect')

    def _I(self, r, c):                         # (the summed table at fractional r, c: bilinear)
        r = np.clip(r, 0, self.h); c = np.clip(c, 0, self.w)
        r0 = np.minimum(np.floor(r).astype(int), self.h - 1); c0 = np.minimum(np.floor(c).astype(int), self.w - 1)
        fr, fc = r - r0, c - c0; S = self.S
        return ((1 - fr) * (1 - fc) * S[r0, c0] + (1 - fr) * fc * S[r0, c0 + 1] + fr * (1 - fc) * S[r0 + 1, c0]
                + fr * fc * S[r0 + 1, c0 + 1])

    def at(self, y, u0, u1, r):
        for a, b, anchor, row, col, mirror in TAKES:
            if a <= y <= b: break
        else: return np.ones_like(np.asarray(u0, float))
        if anchor == 'top': r0 = row + (y - a) * self.k
        else: r0 = row - (Y_GROUND - y) * self.k
        r0 = np.clip(r0, 0, self.h - self.k); r1 = r0 + self.k
        arc = lambda u: r * POLE_M * (np.arcsin(np.clip(u, -1, 1)) + np.pi / 2) / TEX_M   # (photograph px from the left limb)
        s0, s1 = arc(np.asarray(u0, float)), arc(np.asarray(u1, float))
        if mirror: c0, c1 = col + np.pi * r * POLE_M / TEX_M - s1, col + np.pi * r * POLE_M / TEX_M - s0
        else: c0, c1 = col + s0, col + s1
        c1 = np.maximum(c1, c0 + 0.5)
        tot = self._I(r1, c1) - self._I(r0, c1) - self._I(r1, c0) + self._I(r0, c0)
        rc = np.clip(np.round(0.5 * (r0 + r1)).astype(int), 0, self.h - 1)
        cc = np.clip(np.round(0.5 * (c0 + c1)).astype(int), 0, self.w - 1)
        g = self.F[rc, cc] * GRAIN_K / np.sqrt(np.maximum(1.0, (c1 - c0) / self.k))   # (finer toward the limbs)
        m = np.maximum(1.0 + TEX_K * (tot / ((r1 - r0) * (c1 - c0)) - 1.0), 0.2)
        return self.T[rc] * m + g


class Light:
    """The pole's light in one layer: the lit side's colour E, the rim's R and the shade B, row by row."""
    def __init__(self, arr, unlit):
        self.E, self.R, self.B = {}, {}, {}
        for part in ((UPPER[0], LOWER[1]),):      # (the whole pole at once: one light down it)
            rows = (part[0], part[1])
            E = even(measure(arr, rows, LIT_COLS, 8.0, cool=True))
            Eu = even(measure(unlit, rows, LIT_COLS, 8.0, cool=True))
            R = measure_rim(arr, rows)
            B = KB * gaussian_filter(Eu, (25, 0), mode='nearest')
            for i, y in enumerate(range(rows[0], rows[1] + 1)):
                self.E[y], self.R[y], self.B[y] = E[i], R[i], B[i]
        self.E_top, self.R_top, self.B_top = self.E[UPPER[0]], self.R[UPPER[0]], self.B[UPPER[0]]

    def at(self, y):
        return (self.E.get(y, self.E_top), self.R.get(y, self.R_top), self.B.get(y, self.B_top))

    def shade(self, u, y, rim=1.0):
        """The concrete's colour at azimuth u (array) in row y."""
        E, R, B = self.at(y); u = np.asarray(u, float)[..., None]
        return (B * ambient(u) + np.maximum(E - B, 0) * f_lit(u) + rim * np.maximum(R - B, 0) * g_rim(u))

    def warm(self, y):
        R = self.at(y)[1]
        return float(np.clip((R[0] - R[2] - 4) / 30.0, 0, 1))


def steel(L, u, y, glint):
    """A steel band's face: the concrete's light on it, a little brighter, a glint where the light meets the eye."""
    c = L.shade(u, y) * 1.12
    g = np.exp(-((np.asarray(u, float) - (-0.6)) / 0.13) ** 2)[..., None]
    return c + g * glint


def draw_pole(arr, unlit, tex, glint, sun=None):
    """One layer (arr, whole-scene RGBA floats, changed in place); unlit: the power cut (its lit side sets the shade).
    Returns the mask of what changed (whole scene)."""
    from pole_foot import front_row, FOOT, TOP as FOOT_TOP
    H, W = arr.shape[:2]
    L = Light(arr, unlit)
    ch = np.zeros((H, W), bool)
    orig = arr[..., :3].copy()
    fy = {}                                    # (the foot: each column's front row)
    for y in list(range(UPPER[0], UPPER[1] + 1)) + list(range(LOWER[0], LOWER[1] + 1)):
        x0, x1, cx, r = body_rows(y)
        xs = np.arange(x0, x1 + 1)
        if y >= FOOT_TOP:                      # (the foot: down to its circle's front on the sidewalk)
            keep = np.array([y + 0.5 < fy.setdefault(x, front_row(x)) for x in xs])
            if not keep.any(): continue
            xs = xs[keep]
        u = (xs + 0.5 - cx) / r
        c = L.shade(u, y)
        if y == int(BOLT[1]): plain = dict(zip(xs, c.copy()))   # (the bolt takes the concrete's light, not its stains)
        c = c * tex.at(y, (xs - cx) / r, (xs + 1 - cx) / r, r)[:, None]
        # the conduits: small pipes on its face, lit on their left, a thin shadow right of them where the pole is lit
        if y >= CONDUIT_TOP:
            for a, b in CONDUITS:
                for k, x in enumerate(range(a, b + 1)):
                    j = np.nonzero(xs == x)[0]
                    if not len(j): continue
                    uc = (0.5 * (a + b + 1) - cx) / r
                    un = np.clip(uc + (k - 1) * 0.75, -0.97, 0.97)
                    cc = L.shade(np.array([un]), y, rim=0.0)[0]
                    E, R, B = L.at(y)        # (a small pipe: its lit side a little under the pole's lit edge)
                    c[j[0]] = B * ambient(un) + (cc - B * ambient(un)) * 0.75 if k == 0 else cc * (0.92 if k == 1 else 1.0)
                j = np.nonzero(xs == b + 1)[0]
                if len(j):
                    lit = float(np.clip(f_lit((b + 1.5 - cx) / r) * 2, 0, 1))
                    c[j[0]] *= 1 - 0.3 * lit
        # the foot's last rows darker (tools/pole_foot.py: the wet foot, the ground's occlusion)
        if y >= FOOT_TOP:
            k = np.clip((np.array([fy[x] for x in xs]) - (y + 0.5)) / FOOT[0], 0, 1)
            c *= (FOOT[1] + (1 - FOOT[1]) * k)[:, None]
        arr[y, xs, :3] = c; arr[y, xs, 3] = 255; ch[y, xs] = True
        if sun is not None and y < 662:        # (the street's sun mask: the rim, where the rim is the sun's)
            w = L.warm(y)
            sun[y, xs] = 0
            sun[y, xs[g_rim(u) > 0.25]] = round(255 * w)
    # the bands: steel rings round it
    for yb, n in BANDS:
        x0, x1, cx, r = body_rows(yb)
        xs = np.arange(x0, x1 + 1); u = (xs + 0.5 - cx) / r
        for i in range(n):
            c = steel(L, u, yb + i, glint)
            if i == 0: c = c * 1.3 + 4
            elif i == n - 1: c = c * 0.6
            arr[yb + i, xs, :3] = c
        arr[yb + n, xs, :3] *= 0.72            # (its shadow on the concrete under it)
        ch[yb:yb + n + 1, xs] = True
    # the bolt: a round head on a square washer, lit upper left (stepped), its shadow lower right on the concrete
    bx, by, br = BOLT
    E = L.at(int(by))[0]
    C = plain[int(bx)]                                        # (the concrete there: the bolt in its light)
    tones = [C * 0.45, C * 1.0, C * 1.45 + 8, E * 1.2 + 10]   # (dark, mid, lit, its glint)
    for y in range(int(by - br - 2), int(by + br + 3)):
        for x in range(int(bx - br - 2), int(bx + br + 3)):
            dx, dy = x + 0.5 - bx, y + 0.5 - by
            if max(abs(dx), abs(dy)) <= br + 0.6 and not (dx * dx + dy * dy < br * br):   # (the washer's corners)
                arr[y, x, :3] = C * 1.15 if dx + dy < 0 else C * 0.7; ch[y, x] = True; continue
            if dx * dx + dy * dy < br * br:
                nx, ny = dx / br, -dy / br; nz = np.sqrt(max(0.0, 1 - nx * nx - ny * ny))
                lam = max(0.0, -0.7 * nx + 0.5 * ny + 0.5 * nz)
                k = 3 if lam > 0.9 else 2 if lam > 0.6 else 1 if lam > 0.25 else 0
                arr[y, x, :3] = tones[k]; ch[y, x] = True
            elif 0 < dx <= br + 2 and 0 < dy <= br + 2 and (dx - 1.2) ** 2 + (dy - 1.2) ** 2 < (br + 0.6) ** 2:
                arr[y, x, :3] *= 0.7; ch[y, x] = True                # (its shadow)
    # the cap: the same concrete inside its own outline (tools/pole_cut.py's), its dome lit from above by the sky
    SKY, LIT, CREST = np.array([27., 36., 69.]), np.array([64., 61., 105.]), np.array([35., 44., 82.])
    cx, rr = 1043.5, 21.5
    apex, ylip = CAP[0], 57
    for y in range(CAP[0], CAP[1]):
        xs = np.nonzero(arr[y, 1018:1070, 3] > 0)[0] + 1018
        for x in xs:
            u = float(np.clip((x + 0.5 - cx) / rr, -0.99, 0.99))
            if y >= ylip:                      # the sleeve: the pole's own light, a pixel proud
                c = L.shade(np.array([u]), UPPER[0])[0] * (1.25 if y == ylip else 0.8 if y == CAP[1] - 1 else 1.05)
            else:                              # the dome: the sky's light from above, stepped as the painter shades
                v = min(1.0, (ylip - y - 0.5) / (ylip - apex)); w = np.sqrt(max(1e-6, 1 - v * v))
                uu = float(np.clip(u / w, -0.99, 0.99))
                up = round(min(1.0, v * 1.15) * 3) / 3
                c = L.shade(np.array([uu]), UPPER[0])[0] * (1 - up) + (SKY + (LIT - SKY) * max(0.0, -uu) * 0.6) * up
                if y == apex or arr[y - 1, x, 3] == 0: c = np.maximum(c, CREST)
            arr[y, x, :3] = c; ch[y, x] = True
        arr[UPPER[0], UPPER[2]:UPPER[3] + 1, :3] *= 0.6   # (the shadow under the sleeve)
    return ch


def save(a, path, mode='RGBA'):
    Image.fromarray(np.round(np.clip(a, 0, 255)).astype(np.uint8), mode).save(path, 'WEBP', lossless=True, quality=100, method=6, exact=True)


def sun_layer():
    """assets/street_sun.webp with the zone's box from its before copy (the same bytes each time once drawn)."""
    s = np.asarray(Image.open(os.path.join(ROOT, 'assets', 'street_sun.webp')).convert('RGB')).astype(float).copy()
    x0, y0, x1, y1 = BOX
    s[y0:y1, x0:x1] = np.asarray(Image.open(os.path.join(EDITS, 'poletex_before_sun.webp')).convert('RGB')).astype(float)
    return s


def draw_layers(city, unlit, box=BOX):
    tex = Concrete()
    unlit0 = unlit.copy()
    sun = sun_layer(); sm = sun[..., 0].copy()
    ch = draw_pole(city, unlit0, tex, np.array([26.0, 20.0, 18.0]), sm)
    ch |= draw_pole(unlit, unlit0, tex, np.array([10.0, 11.0, 16.0]))
    sun[..., 0] = sun[..., 1] = sun[..., 2] = sm
    return ch, sun


def draw(city, unlit, box=BOX):
    """The zone (redraw_zones.py): both layers changed in place, assets/street_sun.webp written; returns what changed."""
    ch, sun = draw_layers(city, unlit, box)
    save(sun, os.path.join(ROOT, 'assets', 'street_sun.webp'), 'RGB')
    return ch


def preview(out):
    os.makedirs(out, exist_ok=True)
    L = {t: np.asarray(Image.open(os.path.join(ROOT, 'assets', f)).convert('RGBA')).astype(float)
         for t, f in (('city', 'layer_city_off.webp'), ('unlit', 'street_unlit.webp'))}
    A = {t: a.copy() for t, a in L.items()}
    ch, sun = draw_layers(A['city'], A['unlit'])
    print('pixels changed', int(ch.sum()))
    save(A['city'], os.path.join(out, 'layer_city_off.webp')); save(A['unlit'], os.path.join(out, 'street_unlit.webp'))
    save(sun, os.path.join(out, 'street_sun.webp'), 'RGB')
    for t in ('city', 'unlit'):
        for tag, arr in (('before', L[t]), ('after', A[t])):
            for (a, b, nm) in ((44, 400, 'top'), (400, 757, 'bot')):
                z = np.clip(arr[a:b, 990:1080, :3], 0, 255)
                for gm, suf in ((1.0, ''), (0.5, 'b')):
                    Image.fromarray(np.round(255 * (z / 255) ** gm).astype(np.uint8)).resize((90 * 4, (b - a) * 4), Image.NEAREST).save(os.path.join(out, f'{t}_{nm}_{tag}_x4{suf}.png'))


if __name__ == '__main__':
    if '--preview' in sys.argv: preview(sys.argv[sys.argv.index('--preview') + 1])
    else: print(__doc__)
