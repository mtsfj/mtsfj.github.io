#!/usr/bin/env python3
"""The Monolith (Clair Obscur: Expedition 33) on the horizon: a colossal far spire right of Fuji, its "33" painted on it.

    python3 tools/e33_monolith.py      (writes assets/e33_monolith.webp, e33_monolith_aux.webp, e33_mono33.webp; no layer)

What: the owner's drawing (tools/src/e33_monolith_gold33.webp: a dark slender spire on white, a broken top in two
points, cracked faces, a gold 33 with drips, its foot flaring into rubble) brought to the scene as a far plane of its
own, as the tower is (assets/tower.webp), drawn by street.js behind Fuji (z -1.6).
Where: low over Fuji's right flank, left of the cherry (its axis AX, its top TOP, under Fuji's summit): only its broken
top shows, broad, the rest of a giant far off under the horizon behind the mountain; clear of the sixteen stars and Mars
(the star secret's count holds), also as the sky drifts down with the page's scroll (22 px): checked here (ROOM), it
stops if not. The mountain's right flank cuts it on its diagonal, lost in the valley's haze above it: farther than Fuji,
the farthest thing on the ground.
How: the drawing's stone, its rows filled (its 33's white-hot core is stone too), scaled to H scene px from its top to
its foot (its rubble left out), SX narrower (a needle at that distance), turned left for right (MIRROR: its higher point
clear of the star above it, its lit faces toward the sunset behind Fuji); each scene pixel's facet the level that covers
most of it (cracks, the body, mid faces, lit faces: crisp planes at the scene's grain, no blur; where the drawing has
its own 33 and its glow, the painter's faces from just under it are carried up in their place); its outline whole pixels
and a soft edge of one (the far layers'), a pixel in or out every JOG rows (a stone's edge, not a ruler's), its top TIP
rows hard (the broken point, no soft blob).
Its own colour (the image's: the stone before the air): STONE by facet (F), its two faces (SIDE: the one toward the
western sky lit by it, the other in shade), its edge there rimmed warm (RIM), a mottle, a grain and sparse darker specks
as the pagoda's. The air in front of it is street.js's: each pixel is its stone, as the hour lights it (the dawn's first
sun on its lit face and its tip most, before Fuji's summit and as long), mixed by the stone's share in the air
(e33_monolith_aux.webp R: T, less down toward the valley, by rows as by height, to T[2] at the flank's lowest row
HAZE[1]) with the air's colour: the sky's behind it at that hour, read where the sky plane is now and smoothed (the
sky's painted streaks and grain are the sky's, not the air's); the plane ends a few rows under the flank, opaque: the
haze is a colour in front of it, never a hole, and the moon and the stars stay behind it.
The 33 is the drawing's own, brushed (PBOX: its strokes, their lean; never mirrored), at K33 of its size (about four
fifths of the face), its middle on the column on row Y33: each pixel's paint in three steps, the house stipple between
them (worn, brushed paint, no font's clean edge), less of it deep in a crack, no drips under it (at its distance each would be a hundred metres of paint). It is
paint on the stone (PIGMENT, INK: darker than it, a little warmer; the drips are paint's): by day a darker mark on its
faces.
Its light (assets/e33_mono33.webp): the paint's own map in the owner's pale gold (GLOW, not Mars's orange; the strokes'
thick middles brighter, CORE), seen through the same air as the stone (each pixel's alpha its paint times the stone's
share there), whole pixels, crisp, no halo (HALO 0); street.js lays it over the stone (not added: the far air's
warm glow, not a lamp), its strength by the hour: a warm glow at the haze's level at dusk, faint by night, a little more
in the fuses' cut (it is not on the city's grid: the dark shows it), out when the first sun reaches it and in the
morning's air, red in the red night.
Needs Pillow, numpy.
"""
import os
import numpy as np
from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = lambda p: os.path.join(ROOT, 'assets', p)
SRC = os.path.join(ROOT, 'tools', 'src', 'e33_monolith_gold33.webp')
AX, TOP = 776, 280                      # its axis (the drawing's column AXD), its top (scene px): low over Fuji's right flank, left of the cherry
H, SX = 450, 1.0                        # its height from its top to its foot (most of it under the horizon, behind Fuji), its width's share:
                                        # only its broken top shows, broad (40-47 px at the flank), a giant far off, not a needle
AXD, FOOT = 334, 1700                   # the drawing: its axis column, the row where its rubble starts
WHITE = 200                             # the drawing's white: lighter than this is not stone
LEV = (40, 56, 76)                      # the drawing's stone by lightness: cracks | body | mid faces | lit faces
BOX33 = (250, 425, 870, 1200)           # the drawing's 33 and its glow (x0, x1, y0, y1): its faces carried up there
ROW33 = 1012                            # the drawing's 33's middle row
SHIFT = 350                             # where its faces are taken from for the 33's strokes: that many rows under them
MIRROR = True                           # the drawing turned left for right: its higher point on the right (clear of the star above
                                        # it), its lit faces toward the sunset behind Fuji
STONE = (50, 34, 56)                    # the stone at dusk (the shaded rock against the evening sky), its own colour before the air
F = (0.6, 0.86, 1.0, 1.24)              # by facet: cracks, body, mid faces, lit faces
SIDE, RIM = (1.45, 0.8), (1.35, 1.12, 1.0)  # its two faces: the one toward the western sky lit by it, the other in shade; its edge there, rimmed
MOTTLE, GRAIN, SPECK = 0.07, 0.16, (0.3, 0.8)     # the pagoda's grain: a clumped mottle, a fine grain at each pixel, darker specks
JOG = (2, 5)                            # its edges: a pixel in or out every 2-5 rows (a rock's, not a ruler's), never on the tip
CHIP = [(1, 4), (0, 3), (0, 2), (0, 1), (0, 1)]   # its top rows' corners knocked off (left, right px): a broken top, not a flat one
TIP = 12                                # its top rows drawn hard (no soft edge): the broken point
T = (0.5, 0.4, 0.0)                     # the stone's share in the far air (the rest is the sky behind, in street.js): at its top, at
HAZE = (300, 366)                       # HAZE[0], at HAZE[1] (the flank's lowest row under it); the plane ends a few rows lower
PBOX = (250, 425, 870, 1330)            # the drawing's 33 with its drips (x0, x1, y0, y1), its middle C33, its scale on the face
C33, K33 = (336, 1012), (0.16, 0.15)    # (about 0.8 of the face's width; its digits as the drawing's, a little less tall)
FOG = 328                               # from this row down, its foot goes into the valley's haze in a stipple (the pagoda's)
DRIP = 0                                # its drips: none (at its distance a drip would be a hundred metres of paint)
Y33 = 334                               # the 33's middle row: on its broad body, above the flank
PIGMENT, INK = 0.5, (1.1, 0.95, 0.85)    # the 33's paint on the stone by day: darker than it, a little warmer (paint, with its drips)
GLOW, CORE, HALO = (255, 178, 84), (255, 214, 140), 0.0     # its light (a veiled amber; Mars, orange-red, stays redder), its core, no halo (whole pixels, crisp)
STARS = [(648, 88), (686, 101), (711, 78), (729, 95), (744, 82), (806, 79), (840, 109), (871, 86), (894, 123), (667, 139),
         (713, 167), (781, 134), (826, 160), (566, 160), (601, 183), (631, 150)]   # (street.js STARS)
MARS = (757, 184)
DRIFT, ROOM = 22, (9, 14)               # the sky's drift with the scroll (px down); the room kept round a star, round Mars (px)


def hsh(x, y, z=0):
    h = (x * 374761393 + y * 668265263 + z * 2246822519) & 0xffffffff
    h = ((h ^ (h >> 13)) * 1274126177) & 0xffffffff
    return ((h ^ (h >> 16)) & 0xffffffff) / 4294967296.0


def dab(x, y, share, seed):
    """the house stipple (street.js skDab): 2 x 2 dabs (or two 2 x 1, two 1 x 2) in clumps; 1 where it takes the upper step"""
    bx, by, q = x >> 1, y >> 1, (x & 1) + 2 * (y & 1)
    sh = hsh(bx, by, seed + 1)
    key = 0 if sh < 0.5 else (1 + (q >> 1) if sh < 0.75 else 3 + (q & 1))
    return 1 if hsh(bx, by, seed + 10 + key) + (hsh(bx >> 1, by >> 1, seed + 2) - 0.5) * 0.35 < share else 0


def mottle(w, h, sx, sy, seed):
    """a smooth value noise in [-0.5, 0.5], one value per sx x sy px"""
    gx, gy = w // sx + 2, h // sy + 2
    g = np.array([[hsh(i, j, seed) for i in range(gx)] for j in range(gy)])
    ys, xs = np.mgrid[0:h, 0:w].astype(float)
    u, v = xs / sx, ys / sy; i, j = u.astype(int), v.astype(int); fu, fv = u - i, v - j
    fu, fv = fu * fu * (3 - 2 * fu), fv * fv * (3 - 2 * fv)
    return (g[j, i] * (1 - fu) + g[j, i + 1] * fu) * (1 - fv) + (g[j + 1, i] * (1 - fu) + g[j + 1, i + 1] * fu) * fv - 0.5


def shape():
    """the drawing at the scene's scale: per scene pixel its facet level (0 none, 1..4) and its cover; its top row; the 33's row"""
    im = np.asarray(Image.open(SRC).convert('RGB')).astype(float)
    L = im.mean(-1)
    m = L < WHITE
    for r in range(FOOT):                                      # (no hole in the stone: the 33's white-hot core is stone)
        nz = np.nonzero(m[r])[0]
        if len(nz) > 1: m[r, nz[0]:nz[-1] + 1] = True
    m[FOOT:] = False
    top = int(np.nonzero(m.any(1))[0].min())
    s = H / (FOOT - top)
    w, h = int(round(im.shape[1] * s * SX)), int(round(FOOT * s))
    lev = np.digitize(L, LEV) + 1
    lev[~m] = 0
    b = BOX33; n = b[3] - b[2]                                 # (the drawing's 33 and its glow, gold: the painter's own faces from just
    sat = im.max(-1) - im.min(-1)                              # under it carried up in their place, the rest of the band as drawn)
    gold = np.zeros_like(m); gold[b[2]:b[3], b[0]:b[1]] = (sat > 28)[b[2]:b[3], b[0]:b[1]] & (L > 40)[b[2]:b[3], b[0]:b[1]]
    gold = np.asarray(Image.fromarray((gold * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(9))) > 0
    src = lev[b[2] + SHIFT:b[3] + SHIFT]
    for r in range(n):
        y = b[2] + r; on = np.nonzero(m[y])[0]; son = np.nonzero(src[r])[0]
        if not len(on) or not len(son): continue
        for x in np.nonzero(gold[y] & m[y])[0]:               # (the source row a little wider: mapped across this row's width)
            u = (x - on[0]) / max(1, on[-1] - on[0]); xs = int(round(son[0] + u * (son[-1] - son[0])))
            lev[y, x] = src[r, xs] or 2
    ys = np.clip((np.arange(h + 1) / s).astype(int), 0, FOOT); xs = np.clip((np.arange(w + 1) / (s * SX)).astype(int), 0, im.shape[1])
    out = np.zeros((h, w), int)
    for i in range(h):                                         # the level that covers most of each pixel (ties: the darker)
        blk = lev[ys[i]:ys[i + 1]]
        for j in range(w):
            n = np.bincount(blk[:, xs[j]:xs[j + 1]].ravel(), minlength=5); n[0] = 0
            if n.sum(): out[i, j] = n.argmax()
    mi = Image.fromarray((m[:FOOT] * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(float(0.45 / s)))
    cov = np.asarray(mi.resize((w, h), Image.BOX)).astype(float) / 255
    t0 = int(round(top * s)); out, cov, cx = out[t0:], cov[t0:], AXD * s * SX
    if MIRROR: out, cov, cx = out[:, ::-1].copy(), cov[:, ::-1].copy(), w - 1 - cx
    return out, cov, cx, (ROW33 - top) * s, s


def paint33():
    """the drawing's own 33 at the scene's scale (its brushed strokes, their lean; never mirrored): per pixel its paint, 0, 1/3,
    2/3 or 1, the house stipple between the steps; cut at its bowls' foot (DRIP px of drips under it: none); where its middle falls in that map"""
    im = np.asarray(Image.open(SRC).convert('RGB')).astype(float)
    L = im.mean(-1); sat = im.max(-1) - im.min(-1)
    p = (np.clip((L - 60) / 130, 0, 1) * (sat > 28))[PBOX[2]:PBOX[3], PBOX[0]:PBOX[1]]
    kx, ky = K33
    w, h = int(round(p.shape[1] * kx)), int(round(p.shape[0] * ky))
    q = np.asarray(Image.fromarray((p * 255).astype(np.uint8)).resize((w, h), Image.BOX)).astype(float) / 255
    out = np.zeros_like(q)
    for (i, j), v in np.ndenumerate(q):
        u = min(3.0, v * 3.4); lo = int(u)
        out[i, j] = min(3, lo + dab(j, i, u - lo, 21)) / 3
    out[out < 0.34] = 0
    last = int(round((1064 - PBOX[2]) * ky))                        # (the digits' last row, their bowls' foot; under it, the drips)
    for j in range(w):
        run = np.nonzero(out[last + 1:, j])[0]
        out[last + 1:, j] = 0
        if out[last - 1:last + 1, j].max() > 0 and len(run) >= 3:      # (a drip under a stroke: a short, unbroken streak, fading)
            for k in range(min(DRIP, run.max() + 1)): out[last + 1 + k, j] = max(1 / 3, 1 - k / DRIP)
    ys, xs = np.nonzero(out)
    return out, ((C33[0] - PBOX[0]) * kx, (C33[1] - PBOX[2]) * ky), (xs.min(), xs.max())


def clear_of_stars(B, X0, Y0):
    ys, xs = np.nonzero(B); px = np.stack([xs + X0, ys + Y0], 1).astype(float)
    for (x, y), room in [(st, ROOM[0]) for st in STARS] + [(MARS, ROOM[1])]:
        for d in range(0, DRIFT + 1):
            g = float(np.min(np.hypot(px[:, 0] - x, px[:, 1] - (y + d))))
            if g < room: raise SystemExit('%s at %d, %d (the sky %d px down): %.1f px from the monolith' % ('Mars' if (x, y) == MARS else 'a star', x, y, d, g))



def main():
    lev, cov, cx, r33, sc = shape()
    n = HAZE[1] + 5 - TOP; lev, cov = lev[:n].copy(), cov[:n]                   # (the plane ends a little under the flank)
    h, w = cov.shape
    X0, Y0 = int(round(AX - cx)), TOP
    B = cov >= 0.5                                                   # its edges: a pixel in or out every JOG rows (seeded), the tip left be
    for side in (0, 1):
        i, seg = TIP, 0
        while i < h:
            ln = JOG[0] + int(hsh(i, side, 61) * (JOG[1] - JOG[0] + 1)); o = (-1, 0, 1, 0)[int(hsh(i, side, 62) * 4)]
            for r in range(i, min(h, i + ln)):
                xs = np.nonzero(B[r])[0]
                if len(xs) < 5 or o == 0: continue
                e = xs[0] if side == 0 else xs[-1]; out_ = e - 1 if side == 0 else e + 1
                if o > 0: B[r, e] = False
                elif 0 <= out_ < w and cov[r, out_] > 0.05: B[r, out_] = True; lev[r, out_] = lev[r, e]
            i += ln
    alpha = B.astype(float)
    for r in range(TIP, h):                                          # a soft edge of a pixel (the far layers'), none on the hard tip
        for x in range(w):
            if not B[r, x] and cov[r, x] >= 0.2 and ((x > 0 and B[r, x - 1]) or (x < w - 1 and B[r, x + 1])): alpha[r, x] = 0.5
    for r in range(TIP, h):                                          # (no lone soft pixel: one with nothing over or under it is a stray)
        for x in range(w):
            if alpha[r, x] == 0.5 and not ((r > 0 and alpha[r - 1, x] > 0) or (r < h - 1 and alpha[r + 1, x] > 0)): alpha[r, x] = 0
    for i, (cl, cr) in enumerate(CHIP):                              # its broken top: the corners of its first rows knocked off
        xs = np.nonzero(B[i])[0]
        if len(xs): B[i, xs[0]:xs[0] + cl] = False; B[i, xs[-1] - cr + 1:xs[-1] + 1] = False; alpha[i] = B[i]
    clear_of_stars(alpha > 0, X0, Y0)
    mot = mottle(w, h, 5, 3, 11)
    G, (gcx, gcy), _ = paint33(); gh, gw = G.shape                   # the 33: its middle on the column's middle, on row Y33
    row = Y33 - Y0; on = np.nonzero(B[row])[0]
    gx, gy = int(round((on[0] + on[-1]) / 2 - gcx)), int(round(row - gcy))
    P = np.zeros((h, w)); y0_, y1_ = max(0, gy), min(h, gy + gh); x0_, x1_ = max(0, gx), min(w, gx + gw)
    P[y0_:y1_, x0_:x1_] = G[y0_ - gy:y1_ - gy, x0_ - gx:x1_ - gx]
    P *= B
    P[lev == 1] *= 0.4                                               # (less paint deep in a crack)
    out = np.zeros((h, w, 4)); aux = np.zeros((h, w, 3)); K = np.zeros(h)
    for i in range(h):
        y = Y0 + i                                                   # the far air, thicker toward the valley (by rows: as height)
        K[i] = T[0] + (T[1] - T[0]) * min(1, i / max(1, HAZE[0] - Y0)) if y < HAZE[0] else T[1] + (T[2] - T[1]) * min(1, (y - HAZE[0]) / (HAZE[1] - HAZE[0]))
        xs = np.nonzero(B[i])[0]
        if not len(xs): continue
        xm = (xs[0] + xs[-1]) / 2
        for j in range(w):
            if alpha[i, j] == 0: continue
            x = X0 + j
            f = F[max(1, lev[i, j]) - 1] * (1 + 2 * MOTTLE * mot[i, j] + 2 * GRAIN * (hsh(x, y, 5) - 0.5))
            if dab(x, y, SPECK[0], 51): f *= SPECK[1]
            c = np.array(STONE) * f * (SIDE[0] if j < xm else SIDE[1])
            if B[i, j] and (j == 0 or not B[i, j - 1]): c = c * np.array(RIM)     # (its edge toward the western sky)
            if P[i, j] > 0:                                          # the 33's paint on it
                c = c * (1 - P[i, j] * (1 - PIGMENT * np.array(INK)))
            out[i, j, :3] = c; out[i, j, 3] = alpha[i, j] * 255
            k = K[i] * (1 + 0.5 * (hsh(x, y, 9) - 0.5))                 # (the air's grain on it)
            if y >= FOG and dab(x, y, min(1.0, (y - FOG) / (HAZE[1] - FOG)), 71): k *= 0.25   # (its foot: the haze takes it in a stipple)
            aux[i, j, 0] = min(1.0, k) * 255
    cols = np.nonzero(alpha.max(0) > 0)[0]; c0, c1 = cols[0], cols[-1] + 1             # (its own columns only)
    out, aux = out[:, c0:c1], aux[:, c0:c1]
    Image.fromarray(np.clip(np.round(out), 0, 255).astype(np.uint8), 'RGBA').save(A('e33_monolith.webp'), 'WEBP', lossless=True, quality=100, method=6, exact=True)
    Image.fromarray(np.clip(np.round(aux), 0, 255).astype(np.uint8), 'RGB').save(A('e33_monolith_aux.webp'), 'WEBP', lossless=True, quality=100, method=6, exact=True)
    # its light: the paint's own, seen through the same air as the stone (its share), in whole pixels
    ys, xs = np.nonzero(P > 0); by0, by1, bx0, bx1 = ys.min() - 1, ys.max() + 2, xs.min() - 1, xs.max() + 2
    Q = P[by0:by1, bx0:bx1]; Bq = B[by0:by1, bx0:bx1]; lt = np.zeros(Q.shape + (4,))
    Q = (Q >= 0.26).astype(float)                                    # (whole pixels: a crisp glyph, no soft step; in a crack too)
    for (i, j), v in np.ndenumerate(Q):
        nbs = [Q[ii, jj] for ii, jj in ((i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)) if 0 <= ii < Q.shape[0] and 0 <= jj < Q.shape[1]]
        a = v if v > 0 else HALO * max(nbs + [0]) * Bq[i, j]               # (the halo on the stone only)
        core = v >= 1 and sum(n >= 2 / 3 for n in nbs) >= 3                 # (the stroke's middle, where the paint is thick: brighter)
        lt[i, j, :3] = CORE if core else GLOW; lt[i, j, 3] = 255 * a * K[by0 + i] / T[0]
    Image.fromarray(np.clip(np.round(lt), 0, 255).astype(np.uint8), 'RGBA').save(A('e33_mono33.webp'), 'WEBP', lossless=True, quality=100, method=6, exact=True)
    print('assets/e33_monolith.webp: %d x %d at %d, %d; assets/e33_mono33.webp: %d x %d at %d, %d' % (c1 - c0, h, X0 + c0, Y0, Q.shape[1], Q.shape[0], X0 + bx0, Y0 + by0))


if __name__ == '__main__':
    main()
