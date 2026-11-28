#!/usr/bin/env python3
"""The dojo's noren taken in at night: its doorway with the curtain gone, as the street shows the dojo shut.

    python3 tools/dojo_noren.py                 writes assets/dojo_noren_in.webp (the same bytes each time)
    python3 tools/dojo_noren.py --preview DIR   the doorway before and after, x8 (nothing written)

A noren hangs out while a place is open and is taken in when it shuts (暖簾をしまう): the dojo's (空手道場, four panels of
navy cloth under its lintel, painted in both layers) hung there all night, after the dojo had shut at 22 h. street.js
shows this picture over the dojo's door while it is shut (HRS.k.dojo out, the street's unlit picture there): the
curtain gone, the doorway as the street_unlit layer has it.

What is behind the curtain is the doorway's two sliding doors, run up to the lintel: their stiles go on, their rails go
on at the doors' own spacing (one panel up per rail: 44 px at x 18, the spacing shrinking toward the vanishing point
(700, 615) as the wall recedes, 42 px at x 58), so each row of the hidden part is the row one panel below it (filled
from the hem up, the painter's own pixels of the panels under the curtain). The loops the curtain hung by, above its top
edge, are filled along the lintel's slope from the columns beside them. Only the curtain's pixels and the rows between
its top and its hem are written (alpha 255 there, 0 elsewhere): the lintel, the vertical sign and the tree are the
layer's. Needs numpy and Pillow.
"""
import os
import sys
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOX = (0, 452, 84, 562)                       # x0, y0, x1, y1 (the curtain, its loops and its hem, the rows round them)
OUT = os.path.join(ROOT, 'assets', 'dojo_noren_in.webp')
VP = (700.0, 615.0)
P0, PX = 44.0, 18                             # the doors' rail spacing at x 18 (rails at 555 and 599 there)
RAIL = (553, 0.1)                              # the doors' first rail under the curtain: y = 553 + 0.1 x (555 at x 18, 559 at x 58)


def curtain(city):
    """The curtain's pixels in the box: its navy cloth and its pale letters (the city layer, where both read)."""
    c = city.astype(int); R, G, B = c[..., 0], c[..., 1], c[..., 2]
    blue = (B > R + 18) & (B > G + 4)
    letter = (c.sum(2) / 3 > 110) & (B >= R - 10)
    return blue | letter


def taken_in(city, unlit):
    x0, y0, x1, y1 = BOX
    m = curtain(city[y0:y1, x0:x1])
    m[:, 80:] = False                          # (right of x 80 the vertical sign, never the curtain)
    out = unlit[y0:y1, x0:x1].astype(np.float64).copy()
    full = unlit.astype(np.float64)
    W = x1 - x0
    cols = [np.nonzero(m[:, i])[0] for i in range(W)]
    hem = np.full(W, -1); top = np.full(W, -1)
    for i, r in enumerate(cols):
        if len(r) > 8: hem[i] = r.max(); top[i] = r.min()
    ok = hem >= 0
    xs = np.arange(W)
    # the curtain's top edge: a straight line under its loops (the lowest tenth of the column tops), its hem the lowest rows
    tfit = np.polyfit(xs[ok], top[ok], 1)
    resid = top[ok] - np.polyval(tfit, xs[ok]); keep = resid > -2
    tfit = np.polyfit(xs[ok][keep], top[ok][keep], 1)
    hem_w = np.array([hem[max(0, i - 2):i + 3][hem[max(0, i - 2):i + 3] >= 0].max() if ok[max(0, i - 2):i + 3].any() else -1 for i in range(W)])
    written = np.zeros(m.shape, bool)
    # 1. the rows between the top edge and the doors' first rail under the hem (the hem's dark edge and the navy the curtain
    #    cast on the glass under it go with it): a panel up per rail
    for i in range(W):
        if hem_w[i] < 0: continue
        ta = int(np.floor(np.polyval(tfit, i))); hb = max(hem_w[i] + 1, int(round(RAIL[0] + RAIL[1] * (x0 + i))) - 1 - y0)
        P = P0 * (VP[0] - (x0 + i)) / (VP[0] - PX)
        for r in range(hb, ta - 1, -1):
            yy = y0 + r + P
            k = int(np.floor(yy)); f = yy - k
            if k + 1 - y0 < out.shape[0]:
                a = out[k - y0, i] if k - y0 >= 0 else full[k, x0 + i]
                b = out[k + 1 - y0, i]
            else:
                a, b = full[k, x0 + i], full[k + 1, x0 + i]
            out[r, i] = a if f < 0.5 else b       # (the nearest row: no blend)
            written[r, i] = True
    # 2. the loops above the top edge: along the lintel's slope, from the nearest column on either side not under a loop
    slope = tfit[0]
    for i in range(W):
        for r in range(out.shape[0]):
            if not m[r, i] or written[r, i]: continue
            for d in range(1, 12):
                done = False
                for j in (i - d, i + d):
                    if 0 <= j < W:
                        rr = int(round(r + slope * (j - i)))
                        if 0 <= rr < out.shape[0] and not m[rr, j] and not written[rr, j]:
                            out[r, i] = out[rr, j]; written[r, i] = True; done = True; break
                if done: break
    rgba = np.zeros((out.shape[0], W, 4), np.uint8)
    rgba[..., :3] = np.clip(np.round(out), 0, 255).astype(np.uint8)
    rgba[..., 3] = np.where(written, 255, 0)
    return rgba


def main():
    city = np.array(Image.open(os.path.join(ROOT, 'assets', 'layer_city_off.webp')).convert('RGB'))
    unlit = np.array(Image.open(os.path.join(ROOT, 'assets', 'street_unlit.webp')).convert('RGB'))
    rgba = taken_in(city, unlit)
    if len(sys.argv) > 2 and sys.argv[1] == '--preview':
        d = sys.argv[2]; os.makedirs(d, exist_ok=True)
        x0, y0, x1, y1 = BOX
        before = Image.fromarray(unlit[y0:y1, x0:x1])
        a = Image.fromarray(unlit[y0:y1, x0:x1]).convert('RGBA'); a.alpha_composite(Image.fromarray(rgba))
        for name, im in (('before', before.convert('RGB')), ('after', a.convert('RGB'))):
            im.resize((im.width * 8, im.height * 8), Image.NEAREST).save(os.path.join(d, 'dojo_noren_' + name + '.png'))
        return
    Image.fromarray(rgba).save(OUT, lossless=True, quality=100, method=6, exact=True)
    print('wrote', OUT)


if __name__ == '__main__':
    main()
