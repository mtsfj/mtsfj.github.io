#!/usr/bin/env python3
"""The street's far end, between the far zebra crossing and the belvedere's railing: the belvedere's sidewalk edge, its kerb,
and the cross street's wet asphalt, in the street's camera; and what that wet road mirrors from there.

    (a module: tools/redraw_zones.py's zone 'farend', the last, calls draw(city, unlit, box) on the street as the zones
     before it leave it: both layers in its box, the same bytes each time)
    python3 tools/far_end.py --befores        once: the zone's before copies (tools/src/edits/farend_before_*.webp) from
                                              the assets as they are (footO's box reaches it and leaves it as painted)
    python3 tools/far_end.py --geometry       the mirror's numbers, checked against the wet pass in assets/street.js
    python3 tools/far_end.py --preview DIR    the band before and after, both layers, x8 (nothing written)

What was there: across the street's far end (x 600-800), under the belvedere's railing and the two houses either side of
it, one dark, nearly flat strip: the kerb's lit edge one flat row (row 642, the same value from end to end), its face
three flat rows, the cross street a flat dark fill; and in the water over it a single orange smear (the far city's lights
from below the horizon, which a wet road there cannot show).

The geometry (the street's ground model: VP (700, 615), f 959.5 px, the eye 1.41 m over the road; tools/zebra_crossing.py,
tools/facade_foot.py). The cross street runs square across the view. Its far kerb's foot is the wet pass's mirror line
there (assets/wet_mirror.webp: 646.10 on every column from 590 to 810), so the kerb stands at Z = 959.5 x 1.41 / 31.10 =
43.5 m (22.1 px a metre across); a sidewalk kerb 0.15 m high (歩車道境界ブロック, as the street's sidewalks
measure) puts its top edge at row 642.79: the painter's lit row 642 is its rounded arris and its narrow top (0.15-0.20 m
deep there: a tenth of a row), rows 643-645 its face (3.3 rows), the road from 646. Behind it the belvedere's plaza at the
kerb's height (rows 638-641), and at its back the railing on a low wall (the painter's rows 636-637), its foot on the plaza
at row 638: Z = 959.5 x 1.26 / 23 = 52.6 m, where its posts, 37.5 px apart, stand 2.05 m apart, as a Japanese guard fence's
(転落防止柵) do; the two houses' fronts nearer (their feet on row 641: 46.5 m).

What the wet road shows there (street.js's wet pass, WET_FS, its far-end branch: the mirror built in this camera). A ray
from the eye that meets the cross street at row y goes up from it at the angle it came down; mirrored, a thing at depth Z
shows at 2 y0(Z) - its row, y0(Z) = 615 + 959.5 x 1.41 / Z the road's row under it. So:
- rows 646-649.4: the kerb's own face (its mirror about its foot, 646.10), dark: nothing given back (the dark walls give
  nothing), as the wet pass already had it; the plaza's top cannot show at all (a ray going up never meets a floor);
- from 649.4 the ray clears the kerb's top and goes on to the railing's plane, 9 m further: the railing's mirror is about
  that plane's own line, y0(52.6 m) = 640.74, not the kerb's: its low wall at 645.5 (hidden behind the kerb's mirror), its
  bottom rail at 649.5 (just clear of it), the middle rail at 654.0, the top rail at 659.0, the posts' tops at 659.5 (the
  painter's rails on rows 632, 627-628 and 622-623; their shape, rail_dark.webp's, the railing's own dimmed picture): a
  rail or a post gives back the rail as it is drawn now (lit by the city's glow at dusk, dimmed with the far windows late:
  RAILD; out in the power cut; red in the red night);
- between the rails and over them the ray goes on into the far city, mirrored about the horizon (615, 2 px of parallax,
  as the wet pass mirrors the far planes): what shows is what stands above the road's level, the city's lit hillside on
  rows 560-600, never its lights below the horizon (the old smear);
- how much: at this grazing angle (1.9-2.6 degrees: 87.4-88.1 degrees from the normal) water gives back 76-82 % of the
  light (Fresnel, n 1.333: Rs 0.85, Rp 0.75 at row 650); the wet pass's own Fresnel there is 79-84 %, its wetness and still
  water the ground's own (wet.webp, unchanged: no new water, no new rain); a rough wet road streaks a light toward the eye,
  so the rails' and the windows' images run down a few rows into the crossing's (the wet pass's streak, as on the rest of
  the road). The rain's ripples move it; the far city breathing, the hours, the power cut and the red night come with what
  it mirrors; under reduced motion it holds still.
The wet pass decides it at each tap's own column (x 609-760, the railing's span between the houses), on the road's rows
646-679; elsewhere it is as it was.

The layers (R2, R28, R29: simple geometry, the painter's light, his own grain from his own surfaces): in the zone's box
(x 600-800, rows 642-657), each plane a row or a few rows, the painter's own pixels kept (his light, his strokes of rain;
his kerb one flat value a row), and over them
- the kerb's arris and top (row 642): the painter's concrete, the near right kerb's (x 806-870), its lit arris' own
  variation along it, in short runs (a rounded edge's chips and wear), relative to its light;
- the kerb's face (rows 643-645): that kerb's face's grain, in runs copied along the row, relative; its foot (645) the
  painter's darker wet row;
- the cross street (rows 646-657): the asphalt's grain, the painter's own just nearer (rows 658-661, where the cross street
  meets the crossing, his asphalt as he left it), in short runs along each row (its strokes, not a noise), on each row's
  light (his streaks of rain kept).
The unlit layer takes the same change as a ratio (it is the same as the street's there: no painted light falls on it); the
ground lights that fall there (the end house's lantern on the plaza's edge and the road before it, the oden's on the
kerb's face) are added over it by street.js as they were. Needs numpy, scipy, Pillow.
"""
import os
import re
import sys
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter1d

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDITS = os.path.join(ROOT, 'tools', 'src', 'edits')
BOX = (600, 642, 800, 658)                       # the kerb's arris (642), its face (643-645), the cross street (646-657)
VPX, VPY, F, EYE = 700.0, 615.0, 959.5, 1.41     # the street's ground model
KERB_H = 0.15                                    # the kerb (and the plaza) over the road (m)
WALL_FOOT = 638.0                                # the railing's low wall's foot on the plaza (the painter's rows: its face 636-637)
RAIL_X = (609, 760)                              # the railing's span (rail_dark.webp's posts at its ends)
ARRIS, FACE, ROAD = (642, 643), (643, 646), (646, 658)
GRAIN_SIG = 10.0                                 # the asphalt's grain: its residual over its row's light smoothed along it (px)
K_ARRIS, K_FACE, K_ROAD = 0.8, 0.8, 1.0          # each grain's share (the far kerb a little finer than the near one)
CONCRETE = (806, 660, 870, 692)                  # the near right kerb (the painter's concrete), its face and its arris
ASPHALT = (610, 658, 790, 662)                   # the painter's asphalt just nearer, the same road (rows 658-661)
SEED = 23
lum = lambda z: 0.299 * z[..., 0] + 0.587 * z[..., 1] + 0.114 * z[..., 2]


def geometry():
    """the mirror's numbers (rows, depths), from the wet mirror's line and the painter's rows"""
    m = np.asarray(Image.open(os.path.join(ROOT, 'assets', 'wet_mirror.webp')).convert('RGBA')).astype(float)
    ym = 560 + m[0, :, 0] + m[0, :, 1] / 256
    foot = float(np.median(ym[RAIL_X[0]:RAIL_X[1] + 1]))
    zk = F * EYE / (foot - VPY)
    zr = F * (EYE - KERB_H) / (WALL_FOOT - VPY)
    g = dict(foot=foot, zk=zk, top=VPY + F * (EYE - KERB_H) / zk, clear=VPY + F * (EYE + KERB_H) / zk,
             zr=zr, line=VPY + F * EYE / zr, post_m=37.5 * zr / F)
    g['rails'] = {k: 2 * g['line'] - r for k, r in (('wall', 636.0), ('bottom', 632.0), ('middle', 627.5), ('top', 622.5), ('posts', 622.0))}
    return g


def check_street(g):
    """the wet pass's far-end branch uses these numbers: say so, or say which differs"""
    js = open(os.path.join(ROOT, 'assets', 'street.js'), encoding='utf-8').read()
    want = {'kerb top': f"step(yN, {g['top']:.1f})", 'railing line': f"{g['line']:.2f} - (gP.y - {g['line']:.2f}) * e",
            'span': f"step({RAIL_X[0]:.1f}, sx) * step(sx, {RAIL_X[1]:.1f})"}
    bad = [k for k, s in want.items() if s not in js]
    print('street.js wet pass:', 'its far-end numbers match' if not bad else 'DIFFERS: ' + ', '.join(f'{k} ({want[k]})' for k in bad))
    return not bad


def concrete_grain(city):
    """the painter's concrete, the near right kerb: its arris' pixels along its diagonal (relative to their mean) and its
    face's runs (each row's run between the dark foot and the lit arris, relative to that run's mean)"""
    x0, y0, x1, y1 = CONCRETE
    S = city[y0:y1, x0:x1, :3].astype(float); L = lum(S)
    arris, face = [], []
    for r in range(S.shape[0]):
        row = L[r]
        for c in range(2, S.shape[1] - 1):
            if row[c] >= 30 and row[c] >= row[c - 1] + 8 and row[c - 1] <= 18:     # the lit arris, the face just left of it
                arris.append(S[r, c])
                a = c - 1; b = a
                while b > 0 and 11 <= row[b - 1] <= 18: b -= 1
                if a - b >= 3: face.append(S[r, b:a])                            # (from just past the foot to the arris)
                break
    arris = np.array(arris); am = arris.mean(0)
    face = [f / f.mean(0) - 1 for f in face]
    return arris / am - 1, face


def asphalt_grain(city):
    """the painter's asphalt just nearer (the same cross street): each pixel's residual over its row's light"""
    x0, y0, x1, y1 = ASPHALT
    S = city[y0:y1, x0:x1, :3].astype(float)
    return S - gaussian_filter1d(S, GRAIN_SIG, axis=1, mode='nearest')


def runs(rng, W, pick, lo, hi):
    """a row of W residuals: short runs, each copied whole from a source run (pick(n) gives n residuals, 3 channels)"""
    out = np.zeros((W, 3)); x = 0
    while x < W:
        n = int(rng.integers(lo, hi + 1)); n = min(n, W - x)
        out[x:x + n] = pick(n); x += n
    return out


def plan(city):
    """the new street layer's box (H, W, 3) from the painter's pixels there, seeded"""
    x0, y0, x1, y1 = BOX
    V = city[y0:y1, x0:x1, :3].astype(float)
    W = x1 - x0
    rng = np.random.default_rng(SEED)
    base = V                                                                 # the painter's own pixels: his light, his strokes
    out = base.copy()
    arris, face = concrete_grain(city)
    asph = asphalt_grain(city)
    for y in range(y0, y1):
        r = y - y0
        if ARRIS[0] <= y < ARRIS[1]:                                         # the arris: a value held over 2-5 px (wear, chips)
            g = runs(rng, W, lambda n: np.repeat(arris[rng.integers(len(arris))][None], n, 0), 2, 5)
            out[r] = base[r] * (1 + K_ARRIS * g)
        elif FACE[0] <= y < FACE[1]:                                         # the face: its runs, copied along the row
            def pf(n):
                f = face[rng.integers(len(face))]
                s = int(rng.integers(0, max(1, len(f) - n + 1)))
                q = f[s:s + n]
                return q if len(q) == n else np.resize(q, (n, 3))
            out[r] = base[r] * (1 + K_FACE * runs(rng, W, pf, 2, 5))
        else:                                                                # the cross street: the asphalt's strokes
            def pa(n):
                a = int(rng.integers(asph.shape[0])); s = int(rng.integers(0, asph.shape[1] - n + 1))
                return asph[a, s:s + n]
            out[r] = base[r] + K_ROAD * runs(rng, W, pa, 3, 8)
    return np.clip(out, 0, 255)


def draw(city, unlit, box=BOX):
    """The zone: both layers' boxes in place; returns what changed (scene)."""
    x0, y0, x1, y1 = box
    old = city[y0:y1, x0:x1, :3].astype(float).copy()
    new = plan(city)
    city[y0:y1, x0:x1, :3] = new
    u = unlit[y0:y1, x0:x1, :3].astype(float)
    unlit[y0:y1, x0:x1, :3] = np.clip(u * (new + 1) / (old + 1), 0, 255)   # (the same change as a ratio; the same layer there)
    g = geometry()
    print(f"farend: the kerb at {g['zk']:.1f} m (its top on row {g['top']:.2f}, the road clear of it in the mirror from "
          f"{g['clear']:.2f}), the railing at {g['zr']:.1f} m (posts {g['post_m']:.2f} m apart; its mirror about {g['line']:.2f}: "
          + ', '.join(f'{k} {v:.1f}' for k, v in g['rails'].items()) + ')')
    ch = np.zeros(city.shape[:2], bool)
    ch[y0:y1, x0:x1] = np.abs(np.round(new) - old).max(-1) > 0
    return ch


def save(a, path, mode='RGBA'):
    Image.fromarray(np.round(a).astype(np.uint8), mode).save(path, 'WEBP', lossless=True, quality=100, method=6, exact=True)


def befores():
    x0, y0, x1, y1 = BOX
    for tag, f in (('city', 'layer_city_off'), ('unlit', 'street_unlit')):
        a = np.asarray(Image.open(os.path.join(ROOT, 'assets', f + '.webp')).convert('RGBA')).copy()
        fo = np.asarray(Image.open(os.path.join(EDITS, f'footO_before_{tag}.webp')).convert('RGBA'))
        a[630:712, 346:620] = fo                                           # (footO's own before copy where it reaches the box)
        save(a[y0:y1, x0:x1], os.path.join(EDITS, f'farend_before_{tag}.webp')); print('farend_before_' + tag)


def preview(out_dir):
    x0, y0, x1, y1 = BOX
    os.makedirs(out_dir, exist_ok=True)
    city = np.asarray(Image.open(os.path.join(ROOT, 'assets', 'layer_city_off.webp')).convert('RGBA')).astype(float).copy()
    unlit = np.asarray(Image.open(os.path.join(ROOT, 'assets', 'street_unlit.webp')).convert('RGBA')).astype(float).copy()
    for tag, L in (('city', city), ('unlit', unlit)):
        L[y0:y1, x0:x1] = np.asarray(Image.open(os.path.join(EDITS, f'farend_before_{tag}.webp')).convert('RGBA')).astype(float)
    pad = (x0 - 10, 630, x1 + 10, 666)
    big = lambda a: Image.fromarray(np.clip(np.round(a[pad[1]:pad[3], pad[0]:pad[2], :3]), 0, 255).astype(np.uint8)).resize(
        ((pad[2] - pad[0]) * 8, (pad[3] - pad[1]) * 8), Image.NEAREST)
    big(city).save(os.path.join(out_dir, 'farend_before_x8.png'))
    draw(city, unlit)
    big(city).save(os.path.join(out_dir, 'farend_after_x8.png')); big(unlit).save(os.path.join(out_dir, 'farend_after_unlit_x8.png'))


if __name__ == '__main__':
    if '--befores' in sys.argv:
        befores()
    elif '--geometry' in sys.argv:
        g = geometry(); print({k: (round(v, 3) if isinstance(v, float) else {a: round(b, 2) for a, b in v.items()}) for k, v in g.items()})
        check_street(g)
    elif '--preview' in sys.argv:
        preview(sys.argv[sys.argv.index('--preview') + 1])
