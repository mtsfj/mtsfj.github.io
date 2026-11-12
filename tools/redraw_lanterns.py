#!/usr/bin/env python3
"""Ichiraku's two paper lanterns, redrawn (the owner's choice, package clean-3): assets/ichiraku_lanterns.webp from one
clean drawing of the lantern (tools/src/edits/lantern_model.webp, from lantern_prompt.txt, on a flat green ground).

    python3 tools/redraw_lanterns.py        writes assets/ichiraku_lanterns.webp (then its ?v= in street.js)

The atlas is street.js's (IRA): 23 columns, the swing from -7.5 to +3.5 degrees by half a degree (negative: the foot to
the left, as the wind from the right carries it), 64 x 100 cells (wide enough for the round lantern's foot at full swing, tall enough for its light on the wall);
rows 0-2 the left lantern (its 54 x 80 at the cell's top left), rows 3-5 the right one; in each, the lantern as the street lights it with the shop shut (base), lit from inside
(lit) and the light it throws around it: a rim and a pool on the wall behind it (glow, added). Each lantern hangs from the old one's hook and reaches its
old foot; its width follows the drawing (the owner: round is fine, it need not stay slender).
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
CW, CH, COLS = 64, 100, 23
K = 16
LANTERNS = [  # (first row, the cell's part used, the hook in it, the lantern's top and foot rows)
    dict(row=0, size=(54, 80), pivot=(26.5, 5.0), span=(5, 59)),
    dict(row=3, size=(64, 100), pivot=(31.5, 5.0), span=(5, 79))]
BASE = np.array([0.19, 0.17, 0.27])        # the paper unlit, as the old base row against its lit row
GLOW = np.array([36.0, 16.0, 10.0])        # the old halo's strongest light, along the outline
POOL = np.array([70.0, 30.0, 14.0])        # the light the lantern throws on the wall behind it, at its strongest
POOL_SIGMA = 7.0                           # how far that light reaches (scene px)
ROUND = (0.45, 0.6)                        # a row's light: ROUND[0] at its edges, ROUND[0] + ROUND[1] across its middle


def drawing():
    """The drawn lantern, its green ground keyed out (alpha from how green a pixel is), premultiplied, and rounded: each
    row darkened toward its two edges as a cylinder turns away (the owner: the lanterns looked flat)."""
    a = np.array(Image.open(SRC).convert('RGB')).astype(float)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    green = np.clip((g - np.maximum(r, b) - 40) / 80.0, 0, 1)
    alpha = 1 - green
    rgb = a.copy(); rgb[..., 1] = np.minimum(g, np.maximum(r, b) + 10)   # no green fringe
    shade = np.ones(alpha.shape)
    for y in range(alpha.shape[0]):
        xs = np.nonzero(alpha[y] > 0.5)[0]
        if len(xs) < 4: continue
        u = (np.arange(alpha.shape[1]) - (xs[0] + xs[-1]) / 2) / max(1, (xs[-1] - xs[0]) / 2)
        shade[y] = ROUND[0] + ROUND[1] * np.sqrt(np.clip(1 - u * u, 0, 1))
    return rgb * (alpha * shade)[..., None], alpha


def frame(prem, alpha, L, angle):
    """One lantern at one angle, at scene pixels: premultiplied colour and coverage, its cell's size. The drawing (its
    outline, cord included) is scaled to run from the hook to the old foot, centred under the hook."""
    w, h = L['size']; top, foot = L['span']; px, py = L['pivot']
    ys, xs = np.nonzero(alpha > 0.5); dy0, dy1, dx0, dx1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    hook_x = xs[ys == dy0].mean() + 0.5
    s = (foot - top) * K / (dy1 - dy0)
    sw, sh = max(1, round(prem.shape[1] * s)), max(1, round(prem.shape[0] * s))
    c = np.stack([np.array(Image.fromarray(prem[..., i].astype(np.float32), 'F').resize((sw, sh), Image.BICUBIC)) for i in range(3)], -1)
    a = np.array(Image.fromarray(alpha.astype(np.float32), 'F').resize((sw, sh), Image.BICUBIC))
    ox, oy = round(px * K - hook_x * s), round(top * K - dy0 * s)        # the drawing's hook on the hook
    can_c = np.zeros((h * K, w * K, 3)); can_a = np.zeros((h * K, w * K))
    X0, Y0 = max(0, ox), max(0, oy); X1, Y1 = min(w * K, ox + sw), min(h * K, oy + sh)
    can_c[Y0:Y1, X0:X1] = c[Y0 - oy:Y1 - oy, X0 - ox:X1 - ox]; can_a[Y0:Y1, X0:X1] = a[Y0 - oy:Y1 - oy, X0 - ox:X1 - ox]
    rot = lambda ch: np.array(Image.fromarray(ch.astype(np.float32), 'F').rotate(angle, resample=Image.BICUBIC, center=(px * K, py * K)))
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
    pool = np.clip(gaussian_filter(on.astype(float), POOL_SIGMA) * 2.2, 0, 1) * ~on   # the wall lit around it
    h, w = on.shape; yy, xx = np.mgrid[0:h, 0:w]
    edge = np.minimum(np.minimum(xx, w - 1 - xx), np.minimum(yy, h - 1 - yy)).astype(float)
    pool *= np.clip(edge / 8.0, 0, 1) ** 2                                           # faded out before the cell's edge
    light = g[..., None] * GLOW + pool[..., None] * POOL
    keep = light.max(-1) > 1.5
    glow = np.dstack([light * keep[..., None], keep * 255.0])
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
