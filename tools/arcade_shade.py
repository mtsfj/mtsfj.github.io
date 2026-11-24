#!/usr/bin/env python3
"""Between Ichiraku and the arcade's door, under the arcade's eave: what were two flat navy slabs (the zone 'arcgap', the
painter's green-black made the night's navy, 37 x 380 px each) drawn as what the street's camera says they are.

    (a module: tools/redraw_zones.py's zone 'arcwall' calls draw() on the street as the zones before it leave it, before
     the fronts' feet (tools/facade_foot.py's footR, which lays their plinths))

The geometry (tools/facade_foot.py's camera: VP (700, 615), f 960 px, the eye 1.26 m over the sidewalk; the fronts on the
right 4.45 m from the eye's line, their feet on the ray v -0.283): the arcade is set back 30 cm from Ichiraku's front
(its feet 10 rows over that ray: X 4.75 m), from Z 7.55 m toward us. Its eave's far end, 50 cm out, falls at x 1240, and
the downpipe from its gutter at x 1303, in the inside corner (X 4.75, Z 7.55). So:
- A (x 1266..1302): Ichiraku's building's own side, its near end wall (the frontal plane Naruto's end wall is, over the
  arcade's roof), the 30 cm of it the set-back arcade leaves in view: from Ichiraku's corner (its arris, x 1266) to the
  inside corner and the downpipe; its foot level (a frontal plane: row FOOT_A, where facade_foot lays its plinth); its
  concrete the end wall's own tone, read on it over the arcade's roof (R29: one plane), a little darker under the eave
  and into the inside corner, a fine grain; the arris one column a hair lighter;
- B (x 1319..1356): the arcade's own front, its recess beside the door under the GAME sign: its back wall clad in small
  square tiles (10 cm, their rows on the rays, their columns crowding toward the vanishing point), the arcade's teal navy
  (its post's tone) in the recess's shade, each tile a tone of its own within a few levels, its joints darker.
Neither has a light of its own: the same in the power cut; Ichiraku's lamp's halo and the GAME sign's glow lie over them
in street.js on their hours. Needs numpy, scipy.
"""
import numpy as np
from scipy.ndimage import gaussian_filter

BOX = (1262, 400, 1360, 792)                     # the zone (redraw_zones.py 'arcwall')
SLABS = [(1266, 1303), (1319, 1357)]             # A, B: their columns (end excluded)
VP, F, ES = (700.0, 615.0), 960.0, 1.26          # the camera (tools/facade_foot.py's), the eye over the sidewalk
XB = 4.75                                        # m: the arcade's front (B's back wall: X 4.75 + its recess, 0.3 m)
FOOT_A = 775                                     # A's foot (a frontal plane at Z 7.55: 615 + f ES / Z), its rows above
END_REF = (1300, 300, 1356, 345)                 # the end wall just over the arcade's roof: A's plane, its tone
POST_REF = (1309, 450, 1317, 760)                # the arcade's post: B's material
TILE = 0.10                                      # m
SEED = 7


def slab_mask(city, box):
    """the slabs' pixels: the navy fill (r, g small, b 5..16) in their columns, each column's run filled; A down to its
    level foot"""
    x0, y0, x1, y1 = box
    c = city[y0:y1, x0:x1, :3]
    nav = (c[..., 0] <= 3.5) & (c[..., 1] <= 6.5) & (c[..., 2] >= 5) & (c[..., 2] <= 16.5)
    m = np.zeros(nav.shape, bool); a_m = np.zeros(nav.shape, bool)
    for k, (a, b) in enumerate(SLABS):
        for x in range(a, b):
            ys = np.where(nav[:, x - x0])[0]
            ys = ys[ys + y0 >= 405]
            if len(ys) <= 20: continue
            bot = FOOT_A - y0 if k == 0 else ys.max() + 1
            m[ys.min():bot, x - x0] = True
            if k == 0: a_m[ys.min():bot, x - x0] = True
    return m, a_m


def draw(city, unlit, box=BOX):
    """The zone: both layers changed in place over the slabs; returns what changed (whole scene)."""
    x0, y0, x1, y1 = box
    H, W = city.shape[:2]
    m, a_m = slab_mask(city, box)
    b_m = m & ~a_m
    rng = np.random.default_rng(SEED)
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(float)
    grain = gaussian_filter(rng.standard_normal(m.shape), 0.6)
    # A: Ichiraku's building's end wall, its concrete the end wall's own (over the arcade's roof)
    a, b_, c, d = END_REF
    end = np.median(city[b_:d, a:c, :3].reshape(-1, 3), 0)
    v = np.clip((yy - 405) / (FOOT_A - 405), 0, 1)
    shade = (0.82 + 0.22 * v) * (1.0 - 0.16 * np.clip((xx - 1290) / 12, 0, 1))   # (under the eave; into the inside corner)
    arris = (xx == SLABS[0][0])
    streak = gaussian_filter(rng.standard_normal(m.shape), (7.0, 0.7)) * 9.0     # (the end wall's vertical weathering, as over the roof)
    wall_a = end[None, None, :] * (shade * np.where(arris, 1.3, 1.0))[..., None] \
        + (streak + 0.6 * grain)[..., None] * np.array([0.45, 0.65, 1.0])
    # B: the arcade's recess, small tiles in its post's teal navy, in the recess's shade
    a, b_, c, d = POST_REF
    post = city[b_:d, a:c, :3].reshape(-1, 3).mean(0)
    Z = F * XB / (xx + 0.5 - VP[0])                               # the back wall's depth at each column
    col = np.floor(Z / TILE).astype(int); fz = Z / TILE - col
    hgt = (VP[1] - (yy + 0.5)) * Z / F + ES                       # the height over the sidewalk of each pixel's point
    row = np.floor(hgt / TILE).astype(int); fh = hgt / TILE - row
    dz = np.abs(np.gradient(Z / TILE, axis=1)).clip(1e-3); dh = np.abs(np.gradient(hgt / TILE, axis=0)).clip(1e-3)
    joint = (fz < dz) | (fh < dh)                                 # (one px of joint on each tile's near side and foot)
    lift = (fh > 1 - dh) & ~joint                                 # (its top edge: a hair lighter)
    tone = 1.0 + 0.06 * rng.standard_normal((col.max() - col.min() + 2) * 64 + 64)
    t = tone[((col - col.min()) * 64 + (row - row.min()) % 64) % len(tone)]
    vb = np.clip((yy - 450) / 330, 0, 1)
    wall_b = post[None, None, :] * (0.60 * (0.86 + 0.18 * vb) * t * np.where(joint, 0.7, np.where(lift, 1.08, 1.0)))[..., None] \
        + grain[..., None] * np.array([0.4, 0.6, 0.9])
    out = np.clip(np.where(a_m[..., None], wall_a, wall_b), 0, 255)
    for L in (city, unlit):
        sub = L[y0:y1, x0:x1]; sub[..., :3][m] = out[m]; sub[..., 3][m] = 255
    ch = np.zeros((H, W), bool); ch[y0:y1, x0:x1] = m
    return ch
