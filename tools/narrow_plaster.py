#!/usr/bin/env python3
"""The narrow building between the Pokemon Center and the apartment building (zone5's A, x 908..940) in one plaster.

    (a module: tools/redraw_zones.py's zone 'awall' calls draw() on the street as the zones before it leave it)

The owner (2026-11-13): "le bâtiment entre Pokécenter et bâtiment refait : mur lisse". Zone 5 (tools/zone5_facades.py)
had given it small glazed tiles, a grid of joints over its whole front; its neighbour B was made one plaster the same
day (tools/redraw_zones.py, zone bwall). Now A is one plaster too, from its cap to the sidewalk (R25), in a tone of its
own: B's is a cool slate, A's a warm dove grey, a shade lighter, that the night turns a dusty mauve beside B's navy
(two neighbours, two plasters, one family; compared: B's own tone, a sand, a rose, a grey stone, weaker and stronger).

How: zone5's own walls() and life(), run again on the layers as they were before it (git AT), A's material plaster()
instead of tiles(): the painter's light on the wall (its bilateral filter along the facade's rays), a tenth of his grain,
its weathering (rain streaks under the sills and ledges, the splash band at the foot, a rust tint under the cap), its
two ledges in the same material with their own light (lit top, face, dark underside); its narrow pier right of the door
(zone5 drew its tiles' joints there apart) the same plaster. What stands on it is drawn again as zone5 drew it: the lit
window's shoji, the lattice door (koshi-do), the mailbox on the pier and its shade, the potted plant and its shade on
the ground. zone5 is run twice, A in its tiles and A in plaster, everything else alike; what differs between the two
(A's wall, its ledges, the shades laid on them) is what changes, A's columns only (B's lit arris, x 941, is B's). In
the power cut the same, darkened as the painter darkened his wall (zone5's ratio). Then its top (the painter's cap and
upper window, which zone5 kept) is redrawn on the pixel grid: top().

Nothing street.js lays there carries A's wall: the Pokemon Center's ball (z4_emblem, x 849..898) stops short of it, its
glow (z4_emblem_glow) is added over whatever wall is there, and no lit window's comp covers A (its shoji is in the
layers).
"""
import io
import os
import subprocess
import sys
import tempfile
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import zone5_facades as Z                        # noqa: E402

AT = 'cd2d002^'                                  # the layers as painted, before zone5
JS_AT = 'cd2d002'                                # street.js as zone5 read it (the pole's trace, which shapes B's wall)
PLASTER = dict(face=1.25, amp=0.03, tone=(242, 208, 196), ch=1.0)    # A's plaster (B's: 1.0, (210, 210, 222), 0.3)
X0, X1 = 900, 940                                # A's columns, its shades on the ground left of it included


def _git(ref, path):
    return subprocess.run(['git', 'show', f'{ref}:{path}'], cwd=ROOT, capture_output=True, check=True).stdout


_RUN = {}
def zone5_a(material, plaster=None):
    """The street and its power cut as zone5 leaves them with A in `material` ('tiles': as zone5 made it; 'plaster'),
    whole-scene RGB arrays (cached)."""
    pl = dict(plaster or PLASTER); key = (material, tuple(sorted((k, str(v)) for k, v in pl.items())))
    if key not in _RUN:
        old = lambda f: np.array(Image.open(io.BytesIO(_git(AT, 'assets/' + f))).convert('RGBA')).astype(float)
        city, unlit = old('layer_city_off.webp'), old('street_unlit.webp')
        mat = (lambda: Z.tiles(**Z.TILES2)) if material == 'tiles' else (lambda: Z.plaster(**pl))
        Z.VARIANTS['a_' + material] = {'A': mat, 'B': Z.VARIANTS[Z.VARIANT]['B']}   # (B for its light: what stands at its
        tiles = Z.tiles                                                             # foot is lit by it)
        if material != 'tiles':                  # (zone5 drew the pier right of A's door apart, in tiles' joints: here
            Z.tiles = lambda **k: Z.plaster(**pl)    # the same plaster as the rest)
        with tempfile.NamedTemporaryFile('wb', suffix='.js') as js:
            js.write(_git(JS_AT, 'assets/street.js')); js.flush()
            try:
                c2, u2, _, shades, _ = Z.walls(city, unlit, 'a_' + material, js.name)
            finally:
                Z.tiles = tiles
        Z.life(c2, u2, city, unlit, shades)
        _RUN[key] = (c2[..., :3], u2[..., :3]); _RUN['alpha'] = city[..., 3]
    return _RUN[key]


def change(plaster=None):
    """A in plaster: the new street, its power cut and what changed (whole-scene)."""
    tc, tu = zone5_a('tiles'); pc, pu = zone5_a('plaster', plaster)
    m = (np.abs(np.round(pc) - np.round(tc)).max(-1) > 0) | (np.abs(np.round(pu) - np.round(tu)).max(-1) > 0)
    cols = np.zeros(m.shape, bool); cols[:, X0:X1 + 1] = True
    return pc, pu, m & cols


def draw(O, U, box):
    """O, U: the street and its power cut over box (x0, y0, x1, y1), RGB floats, as the zones before leave them.
    Returns the new street, the new power cut and the mask of what changed."""
    x0, y0, x1, y1 = box
    pc, pu, m = top(*change())
    m = m[y0:y1, x0:x1]; tn, tu = O.copy(), U.copy()
    tn[m] = pc[y0:y1, x0:x1][m]; tu[m] = pu[y0:y1, x0:x1][m]
    return tn, tu, m


# ---- its top, redrawn on the pixel grid (the owner, 2026-11-13: "le haut est moche, l'espèce de boudin de béton qui
# fait le contour ; pas droit, angle bizarre, perspective bizarre"): zone5 kept the painter's top, a metal cap four rows
# deep over a black groove, a band of wall, then the upper window's deep reveal (its soffit nine rows of black, its far
# jamb six columns), the corner's lit column down the tree: a rounded frame round the upper floor. Now, on the facade's
# own rays (v = (615 - y) / (x - 700), the vanishing point (700, 615), as its silhouette, its ledges and B's cap): a
# slim coping under the roof edge (its lit front edge, its face, a crisp shadow row), the plaster straight up to it and
# out to the corner (a plain vertical edge on the tree), the window set in the plain wall: a one-row soffit, a thin
# frame, its panes and bars on the window below's columns (the shoji's: 916-917, 929-930), the painter's glass resampled
# into them (his panes' light, from their top to their foot), a thin sill (its lit front edge, its face, its shadow).
TOP_V, LEDGE_V = 1.2335, 0.832           # A's roof edge (its silhouette on the tree, as painted) and its floor ledge's top
CORNER = 908                             # its far corner (x 907 is the tree's)
COPING = 3                               # the coping's rows under the roof edge (its lit front edge, its face), then a shadow row
WIN = dict(x=(912, 935), head=1.153, sill=0.907, bars=((916, 917), (929, 930)), sill_x=(911, 936),
           panes=[((913, 915), (919, 921)), ((918, 928), (919, 927)), ((931, 934), (931, 934))],   # (new columns, the
           src_v=(1.105, 0.94))          # painter's they are drawn from), and the rays his glass runs between
SHADE = dict(coping=0.55, soffit=0.62, sill=0.6, sillface=0.78)   # the shadow rows: the plaster's light times this (the
                                         # sill's face: its lit edge's)
FILL_SIGMA = 2.5                         # the plaster's light carried into what was not wall (px)


def _filled(img, hole, sigma):
    """img's low frequencies with `hole` left out (normalised convolution), RGB."""
    from scipy.ndimage import gaussian_filter
    w = (~hole).astype(float); den = gaussian_filter(w, sigma)
    return np.stack([gaussian_filter(img[..., k] * w, sigma) for k in range(3)], -1) / np.maximum(den, 1e-6)[..., None]


def top(pc, pu, m):
    """A's top redrawn over the plaster (change()): the new street, its power cut and what changed (whole-scene)."""
    from scipy.ndimage import gaussian_filter, gaussian_filter1d
    V, XX = Z.V, Z.XX; H, W = V.shape; alpha = _RUN['alpha']
    ys0, ys1, xs0, xs1 = 300, 470, CORNER - 4, X1 + 4           # (the work box)
    yv = lambda x, v: 615 - v * (x + 0.5 - 700) - 0.5
    first = lambda x, v: int(np.ceil(yv(x, v) - 1e-9))         # (a column's first row whose centre is on or under ray v)
    ytop = {x: int(np.nonzero(alpha[250:470, x] > 128)[0][0]) + 250 for x in range(CORNER, X1 + 1)}
    reg = np.zeros((H, W), bool); role = np.full((H, W), '', 'U8')
    for x in range(CORNER, X1 + 1):
        for y in range(ytop[x], first(x, LEDGE_V)):
            reg[y, x] = True; d = y - ytop[x]
            role[y, x] = 'lit' if d == 0 else 'face' if d < COPING else 'shadow' if d == COPING else 'wall'
    (wa, wb), (sa, sb) = WIN['x'], WIN['sill_x']
    for x in range(sa, sb + 1):
        yh, ys = first(x, WIN['head']), first(x, WIN['sill'])
        if wa <= x <= wb:
            for y in range(yh + 2, ys - 1): role[y, x] = 'glass'
            for y in (yh + 1, ys - 1): role[y, x] = 'frame'
            role[yh, x] = 'soffit'
            if x in (wa, wb): role[yh + 1:ys, x] = 'frame'
            for b0, b1 in WIN['bars']:
                if x == b0: role[yh + 1:ys, x] = 'frame'
                if x == b1: role[yh + 2:ys - 1, x] = 'bar'
        role[ys, x] = 'sill'; role[ys + 1, x] = 'sillface'; role[ys + 2, x] = 'sillsh'
    # the plaster: zone5's where it was wall (m, above the ledge, off the painter's cap, window and corner), carried into
    # the rest by its own light, its texture (the plaster's noise) laid back on
    old_win = ((XX >= 911) & (XX <= 936) & (V >= 0.870) & (V <= WIN['head'])) | (XX == CORNER) | (V >= 1.185)   # (with
    # the painter's dark line just under his sill's box, which zone5 had taken for wall)
    sup = m & reg & ~old_win
    rng = np.random.default_rng(7)                              # (Z.plaster's own noise: the same field)
    n = gaussian_filter(rng.standard_normal((H, W)), (1.5, 2.5)); n /= n.std(); tex = (1 + PLASTER['amp'] * n)[..., None]
    sl = (slice(ys0, ys1), slice(xs0, xs1)); c, u = pc.copy(), pu.copy()
    base = np.zeros_like(pc); base[sl] = _filled(pc[sl] / tex[sl], ~sup[sl], FILL_SIGMA)
    plas = base * tex
    ratio = np.ones_like(pc); ratio[sl] = _filled((pu[sl] + 1) / (pc[sl] + 1), ~sup[sl], 4.0)   # (the power cut's darkening)
    # the painter's tones: his cap's lit edge and face along the edge (smoothed along it), his frame, his sill's lit edge
    cols = list(range(CORNER, X1 + 1))
    lit = gaussian_filter1d(np.array([pc[ytop[x], x] for x in cols]), 2.0, axis=0, mode='nearest')
    face = gaussian_filter1d(np.array([np.median(pc[ytop[x] + 1:ytop[x] + 4, x], 0) for x in cols]), 2.0, axis=0, mode='nearest')
    gl = (XX >= 919) & (XX <= 927) & (V < WIN['src_v'][0]) & (V > WIN['src_v'][1])
    dark = np.median(pc[(XX == 929) & (V < 1.10) & (V > 0.95)], 0)
    edge = np.median(pc[(XX == 930) & (V < 1.10) & (V > 0.95)], 0)
    slit = np.median(np.array([pc[int(np.argmax(Z.lum(pc[first(x, 0.912):first(x, 0.896), x])) + first(x, 0.912)), x]
                               for x in range(914, 934)]), 0)
    new = plas.copy()
    for k, x in enumerate(cols):
        for y in np.nonzero(reg[:, x])[0]:
            r = role[y, x]
            if r == 'lit': new[y, x] = lit[k]
            elif r == 'face': new[y, x] = face[k]
            elif r == 'shadow': new[y, x] = plas[y, x] * SHADE['coping']
            elif r == 'soffit': new[y, x] = plas[y, x] * SHADE['soffit']
            elif r == 'frame': new[y, x] = dark
            elif r == 'bar': new[y, x] = edge
            elif r == 'sill': new[y, x] = slit
            elif r == 'sillface': new[y, x] = slit * SHADE['sillface']
            elif r == 'sillsh': new[y, x] = plas[y, x] * SHADE['sill']
            elif r == 'wall' and sup[y, x]: new[y, x] = pc[y, x]
    for (a, b), (sa_, sb_) in WIN['panes']:                       # the glass: the painter's panes resampled, column by
        for x in range(a, b + 1):                               # column (across), ray by ray (down)
            ys_ = np.nonzero(role[:, x] == 'glass')[0]
            xs = sa_ + int(round((x - a) * (sb_ - sa_) / max(b - a, 1)))
            for y in ys_:
                w = (y - ys_[0]) / max(ys_[-1] - ys_[0], 1)
                vo = WIN['src_v'][0] - w * (WIN['src_v'][0] - WIN['src_v'][1])
                new[y, x] = pc[int(round(yv(xs, vo))), xs]
    c[reg] = new[reg]; u[reg] = np.clip((new[reg] + 1) * ratio[reg] - 1, 0, 255)
    return c, u, m | reg
