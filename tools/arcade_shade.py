#!/usr/bin/env python3
"""The arcade's front wall in the deep shade of its eave, beside Ichiraku and beside its own door: what were two flat
navy slabs (the zone 'arcgap', the painter's green-black made the night's navy, 37 x 380 px each, no material and no
light) drawn as the wall they are.

    (a module: tools/redraw_zones.py's zone 'arcwall' calls draw() on the street as the zones before it leave it, last)

Where: the arcade's front, on the right-hand facades' plane (X = 5.3 m right of the street's axis, its foot on the ray
v = -0.283), between Ichiraku's right pillar and the downpipe (A), and between the arcade's corner post and its door
(B), under its tiled eave and, for B, under its GAME sign. What: vertical boards (BOARD m wide, laid along the street:
each seam the column where the wall's Z is a whole number of boards from the post, so they crowd toward the vanishing
point), each board a tone of its own within a few levels, its seam a darker line, its near edge a hair lighter (a
fine seeded grain), darker under the eave and a little lighter toward the sidewalk; the same in the power cut (no light
of its own). The light it catches is the street's own, on its hours, laid over it by street.js: Ichiraku's right wall
lamp's glow on A's left (IRL's halo, with the shop), the GAME sign's on both tops (ASGN.glow, with the arcade). The
wall's foot, the downpipe, the post and the door are left as they are. Needs numpy, scipy.
"""
import numpy as np
from scipy.ndimage import gaussian_filter

BOX = (1262, 400, 1360, 792)                     # the zone (redraw_zones.py 'arcwall')
SLABS = [(1266, 1303), (1319, 1357)]             # A, B: their columns (end excluded)
VP, F, XW = (700.0, 615.0), 1400.0, 5.3          # the street's camera; the right facades' plane (m)
BOARD = 0.18                                     # m
BASE = np.array([8.0, 10.5, 24.0])                # a board in the eave's deep shade (the street's navy darks)
SEAM = 0.45                                      # a seam's share of its board's tone
SEED = 7


def slab_mask(city, box):
    """the slabs' pixels: the navy fill (r, g small, b 5..16) in their columns, each column's run filled"""
    x0, y0, x1, y1 = box
    c = city[y0:y1, x0:x1, :3]
    nav = (c[..., 0] <= 3.5) & (c[..., 1] <= 6.5) & (c[..., 2] >= 5) & (c[..., 2] <= 16.5)
    m = np.zeros(nav.shape, bool)
    for a, b in SLABS:
        for x in range(a, b):
            ys = np.where(nav[:, x - x0])[0]
            ys = ys[ys + y0 >= 405]
            if len(ys) > 20: m[ys.min():ys.max() + 1, x - x0] = True
    return m & (nav | (c.sum(-1) < 40))


def draw(city, unlit, box=BOX):
    """The zone: both layers changed in place over the slabs; returns what changed (whole scene)."""
    x0, y0, x1, y1 = box
    H, W = city.shape[:2]
    m = slab_mask(city, box)
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(float)
    Z = F * XW / (xx + 0.5 - VP[0])                               # the wall's depth at each column
    k = (Z - F * XW / (1302.5 - VP[0])) / BOARD                   # boards counted from the downpipe's column
    board = np.floor(k).astype(int); frac = k - board
    rng = np.random.default_rng(SEED)
    tone = 1.0 + 0.09 * rng.standard_normal(board.max() - board.min() + 3)
    t = tone[board - board.min()]
    wpx = 1.0 / np.abs(np.gradient(k, axis=1)).clip(1e-3)         # a board's width in px here
    seam = frac * wpx < 1.0                                      # the board's far edge: one px of seam
    lit = (frac > 1 - 1.0 / wpx) & ~seam                         # its near edge: a hair lighter
    v = np.clip((yy - 400) / 380, 0, 1)
    shade = 0.78 + 0.34 * v ** 1.5                               # darker under the eave
    grain = gaussian_filter(rng.standard_normal(m.shape), 0.6) * 1.1
    base = BASE[None, None, :] * (t * shade * np.where(seam, SEAM, np.where(lit, 1.12, 1.0)))[..., None] + grain[..., None] * np.array([0.5, 0.6, 1.0])
    out = np.clip(base, 0, 255)
    for L in (city, unlit):
        sub = L[y0:y1, x0:x1, :3]; sub[m] = out[m]
    ch = np.zeros((H, W), bool); ch[y0:y1, x0:x1] = m
    return ch
