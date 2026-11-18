#!/usr/bin/env python3
"""The door of the grey building at the street's end (under the study, right of its shutter): a red steel door at the back
of its recess, where the painter left a smear.

    (a module: tools/redraw_zones.py's zone 'greydoor' calls draw(city, unlit, box): both layers, from the zone's before
    copies, the same bytes each time)
    python3 tools/grey_door.py --preview OUT      the doorway before and after, both layers, at x8 (nothing written)

What was there: in the opening (x 572-590, from its dark soffit at 577 down to the step at 635) a red blotch of five-pixel
smears with a brighter round middle, an orange strip down its left and a dark column on its right: lit by a light in the
recess (in the power cut the strip goes dark and the red stays, dull: a painted door, not a lit glass). Nothing in it read
as a door at 1:1 or at x3 ("something that represents nothing"). The eye is right of it (the vanishing point at x 700), so
the recess shows its left reveal, facing us, and hides its right one behind the jamb's edge.

Redrawn on the pixel grid as the simple geometry it is (R28: a flush door, a reveal, a frame): each plane its own light,
the painter's (his low frequencies taken inside that plane alone, wider than his smears: R2, R18), one tone a plane (R29)
with a fixed fine grain; the left reveal lit and falling off down its height, the frame a dark line on its left and head,
the leaf's hinge edge catching the light (R5), the leaf in the painter's red under the same light, a lever handle on its lock side at 1 m (a lit top pixel, its shadow
under it), the shadow line at its foot; the soffit, the jamb's edges, the step and the sidewalk his. Both layers alike,
each from its own pixels: in the power cut the reveal's light goes and the leaf is the dull red the painter left.
Needs Pillow, numpy, scipy.
"""
import os
import sys
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REVEAL = (573, 576, 579, 634)                    # the left reveal (x0, x1, y0, y1; excl.): facing the eye, lit
FRAME = (576, 579)                               # the door frame's column (against the reveal) and its head's row
LEAF = (577, 590, 580, 632)                      # the leaf, at the back of the recess, its right edge behind the jamb's (590)
FOOT = (632, 634)                                # (the shadow line under the leaf, over the step)
HANDLE = (586, 589, 606)                         # the lever: its columns (the rose on the right, the lock side) and its row
SIG = dict(reveal=(5.0, 0.6), leaf=(5.0, 4.0))   # the painter's light in each plane (sigma y, x): wider than his smears
GRAIN = 0.035                                    # (a fixed fine grain, each pixel its own: no flat block)
FRAME_K, FOOT_K = 0.45, 0.42                     # (the frame's line, the foot's shadow: the plane's light times this)
TOP_SHADE = 0.78                                 # (the reveal's first row under the soffit)
EDGE_K = 1.25                                    # (the leaf's hinge edge, proud of the frame: its first column catching the light)
HANDLE_K = ((1.9, 0.35), (0.62, 0.0))            # (the lever's top: the leaf's light times, toward its grey; its shadow row)


def plane_light(P, m, sig):
    """the painter's light inside the mask m alone (a normalised gaussian: nothing from the next plane)"""
    w = gaussian_filter(m.astype(float), sig)
    return np.stack([gaussian_filter(np.where(m, P[..., c], 0.0), sig) for c in range(3)], -1) / np.maximum(w, 1e-4)[..., None]


def redraw(P, x0, y0):
    """the doorway redrawn in P (a layer's crop at (x0, y0), RGB float), its own light; returns the new crop"""
    H, W = P.shape[:2]; yy, xx = np.mgrid[0:H, 0:W]; yy = yy + y0; xx = xx + x0
    box = lambda b: (xx >= b[0]) & (xx < b[1]) & (yy >= b[2]) & (yy < b[3])
    rev, leaf = box(REVEAL), box(LEAF)
    out = P.copy()
    g = 1.0 + GRAIN * (np.random.default_rng(5790).random((H, W)) * 2 - 1)   # (the same grain in both layers)
    for m, s in ((rev, SIG['reveal']), (leaf, SIG['leaf'])):
        out[m] = (plane_light(P, m, s) * g[..., None])[m]
    top = rev & (yy == REVEAL[2]); out[top] *= TOP_SHADE
    fr = ((xx == FRAME[0]) & (yy >= FRAME[1]) & (yy < LEAF[3])) | ((yy == FRAME[1]) & (xx >= FRAME[0]) & (xx < LEAF[1]))
    lf = plane_light(P, leaf, SIG['leaf'])
    out[fr] = (lf * FRAME_K)[fr]
    ed = leaf & (xx == LEAF[0]); out[ed] = (lf * EDGE_K * g[..., None])[ed]
    ft = (xx >= FRAME[0]) & (xx < LEAF[1]) & (yy >= FOOT[0]) & (yy < FOOT[1]); out[ft] = (lf * FOOT_K)[ft]
    hx0, hx1, hy = HANDLE; lum = lambda a: a @ np.array([0.299, 0.587, 0.114])
    (kt, grey), (ks, _) = HANDLE_K
    for row, k, gr in ((hy, kt, grey), (hy + 1, ks, 0.0)):
        m = (yy == row) & (xx >= hx0) & (xx < hx1)
        if row == hy: m |= (yy == row + 1) & (xx == hx1 - 1)   # (the rose under its lever's end)
        c = lf[m] * k; out[m] = c * (1 - gr) + lum(c)[:, None] * gr
    return np.clip(out, 0, 255)


def draw(city, unlit, box):
    """tools/redraw_zones.py's zone 'greydoor': both layers, in place; what changed"""
    x0, y0, x1, y1 = box; ch = np.zeros(city.shape[:2], bool)
    for a in (city, unlit):
        sub = a[y0:y1, x0:x1]; old = sub[..., :3].copy()
        sub[..., :3] = np.round(redraw(old, x0, y0))
        ch[y0:y1, x0:x1] |= np.abs(sub[..., :3] - old).max(-1) > 0
    return ch


def preview(out):
    os.makedirs(out, exist_ok=True)
    E = os.path.join(ROOT, 'tools', 'src', 'edits')
    x0, y0, x1, y1 = (566, 572, 598, 642)
    tiles = []
    for tag in ('city', 'unlit'):
        b = np.asarray(Image.open(os.path.join(E, f'greydoor_before_{tag}.webp')).convert('RGB')).astype(float)
        a = redraw(b, x0, y0)
        for im in (b, a): tiles.append(Image.fromarray(im.astype(np.uint8)).resize(((x1 - x0) * 8, (y1 - y0) * 8), Image.NEAREST))
    c = Image.new('RGB', (sum(t.width + 8 for t in tiles), tiles[0].height))
    x = 0
    for t in tiles: c.paste(t, (x, 0)); x += t.width + 8
    c.save(os.path.join(out, 'greydoor_x8.png'))


if __name__ == '__main__':
    if '--preview' in sys.argv: preview(sys.argv[sys.argv.index('--preview') + 1])
