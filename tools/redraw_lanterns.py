#!/usr/bin/env python3
"""Ichiraku's two paper lanterns, redrawn (the owner's choice, package clean-3): assets/ichiraku_lanterns.webp from one
clean drawing of the lantern (tools/src/edits/lantern_model.webp, from lantern_prompt.txt, on a flat green ground).

    python3 tools/redraw_lanterns.py        writes assets/ichiraku_lanterns.webp (then its ?v= in street.js)

The atlas is street.js's (IRA): 23 columns, the swing from -7.5 to +3.5 degrees by half a degree (negative: the foot to
the left, as the wind from the right carries it), 48 x 84 cells; rows 0-2 the left lantern (its 38 x 66 at the cell's top
left), rows 3-5 the right one; in each, the lantern as the street lights it with the shop shut (base), lit from inside
(lit) and the light it throws around it (glow, added). Each lantern keeps the old one's place and size: the drawing is
fitted to the box the old one filled (BOXES, its outline with 2 px around), and swings about the old hook (PIVOTS).
Every frame is the drawing turned at 16 x (bicubic) and boxed down to scene pixels, its edge cut at half coverage, so
the outline stays crisp; the cord to the hook is drawn a pixel wide. Same input, same bytes.
"""
import os
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, binary_erosion

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'tools', 'src', 'edits', 'lantern_model.webp')
OUT = os.path.join(ROOT, 'assets', 'ichiraku_lanterns.webp')
CW, CH, COLS = 48, 84, 23
K = 16
LANTERNS = [  # (first row, cell size used, the drawing's box in the cell, the hook)
    dict(row=0, size=(38, 66), box=(10, 3, 27, 61), pivot=(18.5, 5.0)),
    dict(row=3, size=(48, 84), box=(12, 3, 35, 81), pivot=(23.5, 5.0))]
BASE = np.array([0.19, 0.17, 0.27])        # the paper unlit, as the old base row against its lit row
GLOW = np.array([36.0, 16.0, 10.0])        # the old halo's strongest light


def drawing():
    """The model's lantern, its green ground keyed out (alpha from how green a pixel is), premultiplied."""
    a = np.array(Image.open(SRC).convert('RGB')).astype(float)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    green = np.clip((g - np.maximum(r, b) - 40) / 80.0, 0, 1)
    alpha = 1 - green
    rgb = a.copy(); rgb[..., 1] = np.minimum(g, np.maximum(r, b) + 10)   # no green fringe
    return rgb * alpha[..., None], alpha


def frame(prem, alpha, L, angle):
    """One lantern at one angle, at scene pixels: premultiplied colour and coverage, its cell's size."""
    w, h = L['size']; bx0, by0, bx1, by1 = L['box']
    can_c = np.zeros((h * K, w * K, 3)); can_a = np.zeros((h * K, w * K))
    bw, bh = (bx1 - bx0) * K, (by1 - by0) * K
    c = np.stack([np.array(Image.fromarray(prem[..., i].astype(np.float32), 'F').resize((bw, bh), Image.BICUBIC)) for i in range(3)], -1)
    a = np.array(Image.fromarray(alpha.astype(np.float32), 'F').resize((bw, bh), Image.BICUBIC))
    can_c[by0 * K:by0 * K + bh, bx0 * K:bx0 * K + bw] = c; can_a[by0 * K:by0 * K + bh, bx0 * K:bx0 * K + bw] = a
    px, py = L['pivot'][0] * K, L['pivot'][1] * K
    rot = lambda ch: np.array(Image.fromarray(ch.astype(np.float32), 'F').rotate(angle, resample=Image.BICUBIC, center=(px, py)))
    can_c = np.stack([rot(can_c[..., i]) for i in range(3)], -1); can_a = rot(can_a)
    box = lambda ch: ch.reshape(h, K, w, K).mean(axis=(1, 3))
    cc = np.stack([box(can_c[..., i]) for i in range(3)], -1); ca = box(np.clip(can_a, 0, 1))
    return cc, ca


def rows(cc, ca):
    """The three rows of one frame: base, lit, glow (RGBA, 0-255)."""
    on = ca >= 0.5
    col = np.where(on[..., None], cc / np.maximum(ca, 1e-6)[..., None], 0)
    lit = np.dstack([np.clip(col, 0, 255), on * 255.0])
    base = np.dstack([np.clip(col * BASE, 0, 255), on * 255.0])
    ring = gaussian_filter(on.astype(float), 2.0) * ~binary_erosion(on, iterations=1)
    g = np.clip(ring * 1.8, 0, 1)
    glow = np.dstack([g[..., None] * GLOW, (g > 0.04) * 255.0])
    glow[..., :3] *= (g > 0.04)[..., None]
    return base, lit, glow


def cord(base, lit, L, angle):
    """The cord from the hook to the cap, one pixel wide, along the lantern's axis (too thin to survive the boxing)."""
    px, py = L['pivot']; on = lit[..., 3] > 0
    top = np.nonzero(on.any(1))[0].min()
    t = np.tan(np.radians(angle))
    for y in range(int(py), top):
        x = int(np.floor(px + (y + 0.5 - py) * t))
        for im in (base, lit):
            im[y, x] = (24.0, 17.0, 19.0, 255.0)


def main():
    prem, alpha = drawing()
    atlas = np.zeros((6 * CH, COLS * CW, 4))
    for L in LANTERNS:
        w, h = L['size']
        for f in range(COLS):
            ang = -7.5 + 0.5 * f
            base, lit, glow = rows(*frame(prem, alpha, L, ang))
            cord(base, lit, L, ang)
            for r, im in enumerate((base, lit, glow)):
                y = (L['row'] + r) * CH; x = f * CW
                atlas[y:y + h, x:x + w] = im
    Image.fromarray(np.round(atlas).astype(np.uint8), 'RGBA').save(OUT, 'WEBP', lossless=True, quality=100, method=6, exact=True)
    print('wrote', OUT, atlas.shape[1], 'x', atlas.shape[0])


if __name__ == '__main__':
    main()
