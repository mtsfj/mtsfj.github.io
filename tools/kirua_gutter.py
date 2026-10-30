#!/usr/bin/env python3
"""The eave under Kirua (the left house's roof edge, right end): shortened, its end finished, a downpipe.

    python3 tools/kirua_gutter.py      (last: after tools/tree_a.py and tools/tree_bc.py, which take their zones back)

The roof's edge ran on 31 px past the house's corner (x 326) into the sky, a thin stick ending in a point. It now stops
just past Kirua's feet (END_X), cut square as an eave board is, its gutter closed by a round end cap. From the cap a
downpipe drops, turns back to the wall (a swan neck, as on the houses of the references) and runs down the house's
corner to the dagashi's awning, held by a clamp every 40 px. Its metal is the gutter's own (its colours taken from the
eave's dark body and its lit rim): dark, its side toward the sky lit as the gutter's top edge is. What the cut leaves is
the sky (transparent in the street's layers). In layer_city_off, street_unlit (the eave's own change there), night_far
(0, the street's) and street_sun (0). Needs Pillow, numpy.
"""
import os
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = lambda p: os.path.join(ROOT, 'assets', p)
END_X = 351                          # the eave's new end (Kirua's feet reach x ~350)
PIPE = [(348.0, 240.0), (348.0, 244.0), (325.0, 262.0), (325.0, 409.0)]   # the downpipe's axis: down, back to the wall, down
CLAMPS = (300, 340, 380)             # its clamps on the wall (y)


def load(p, mode='RGBA'):
    return np.asarray(Image.open(A(p)).convert(mode)).astype(float)


def save(arr, p, mode):
    Image.fromarray(np.clip(np.round(arr), 0, 255).astype(np.uint8), mode).save(A(p), 'WEBP', lossless=True, quality=100, method=6, exact=True)


def main():
    city, unlit = load('layer_city_off.webp'), load('street_unlit.webp')
    nf, sun = load('night_far.webp', 'RGB'), load('street_sun.webp', 'RGB')
    H, W = city.shape[:2]; yy, xx = np.mgrid[0:H, 0:W]
    eave = (xx >= 326) & (xx <= 372) & (yy >= 205) & (yy <= 250) & (city[:, :, 3] > 0)
    Lc = city[:, :, :3] @ [0.299, 0.587, 0.114]
    body = np.median(city[eave & (Lc < 20)][:, :3], 0)                     # (the gutter's dark metal)
    rim = np.median(city[eave & (Lc > 40)][:, :3], 0)                      # (its edge lit by the sky)
    ratio = np.median((unlit[eave][:, :3] + 1) / (city[eave][:, :3] + 1), 0)

    # the cut: past END_X the eave goes (the sky behind)
    cut = eave & (xx > END_X)
    for L in (city, unlit): L[cut] = 0
    nf[cut] = 0; sun[cut] = 0
    # its end, square: the eave board's end grain a shade darker, the gutter's round cap (lit on its top)
    end = eave & (xx >= END_X - 1) & (xx <= END_X) & ~cut
    city[end, :3] = city[end, :3] * 0.7
    ys = np.where(eave[:, END_X])[0]
    if len(ys):
        cy = ys.min() + 2
        for dy, dx, c in ((-1, 1, rim), (0, 1, body * 1.4), (1, 1, body), (0, 2, body)):
            if 0 <= cy + dy < H: city[cy + dy, END_X + dx, :3] = c; city[cy + dy, END_X + dx, 3] = 255

    # the downpipe: 3 px across its axis; its side toward the sky (right, then up) lit, the other in shade
    pipe = np.zeros((H, W), int)                                             # (0 none, 1 shade, 2 body, 3 lit)
    for (x0, y0), (x1, y1) in zip(PIPE, PIPE[1:]):
        n = int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 1
        dx, dy = x1 - x0, y1 - y0; L_ = np.hypot(dx, dy); nx, ny = dy / L_, -dx / L_      # (its normal, toward the right / up)
        if nx < 0 or (abs(nx) < 1e-6 and ny > 0): nx, ny = -nx, -ny
        for t in np.linspace(0, 1, n):
            px, py = x0 + dx * t, y0 + dy * t
            for o, k in ((-1, 1), (0, 2), (1, 3)):
                X, Y = int(round(px + nx * o)), int(round(py + ny * o))
                if 0 <= X < W and 0 <= Y < H: pipe[Y, X] = max(pipe[Y, X], k) if pipe[Y, X] != 2 or k == 2 else 2
    for cy_ in CLAMPS:                                                       # (its clamps: a short band round it, onto the wall)
        for x in range(321, 328): pipe[cy_, x] = max(pipe[cy_, x], 2)
        for x in range(322, 327): pipe[cy_ + 1, x] = max(pipe[cy_ + 1, x], 1)
    col = {1: body, 2: body + (rim - body) * 0.35, 3: rim}                 # (its shade side, its body, its side lit by the sky)
    for k, c in col.items():
        m = pipe == k
        city[m, :3] = c; city[m, 3] = 255
        unlit[m, :3] = c * ratio; unlit[m, 3] = 255
        nf[m] = 0; sun[m] = 0
    save(city, 'layer_city_off.webp', 'RGBA'); save(unlit, 'street_unlit.webp', 'RGBA')
    save(nf, 'night_far.webp', 'RGB'); save(sun, 'street_sun.webp', 'RGB')
    print('eave cut', int(cut.sum()), 'px | downpipe', int((pipe > 0).sum()), 'px')


if __name__ == '__main__':
    main()
