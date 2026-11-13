#!/usr/bin/env python3
"""The drinks machines' cold light on the sidewalk before them (assets/vend_pool.webp, laid additively by street.js at
262, 716, at the machines' level): a soft pool, no dither, no hard edge.

    python3 tools/vend_pool.py      (reads tools/src/edits/vend_pool_before.webp, the pool as it was; writes the same bytes
                                     each time)

The old pool was a trapezoid of light quantised in steps of about 9 levels and dithered in blocks, cut straight on its
left and top: at true size a pixelated rectangle on the sidewalk, worst in the red night and at 3 h (a survey, 2026-11-13).
Here its own footprint, smoothed (gaussian SIGMA: the dither and the cut edges go, its falloff from the machines' feet
toward the curb stays), times the sidewalk's own relief under it (the joints and the grain of layer_city_off there, as
ratios to their surroundings, softened by TEX: light falls on the pavement, so it shows its pavement); its colour the old
one's (the machines' cold white), its light the old one's in total, channel by channel.
"""
import os
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AT = (262, 716)                      # (where street.js lays it)
SIGMA = 5.0                          # the footprint's smoothing (px): wider than the dither's blocks and steps
TEX = 0.6                            # how much of the pavement's relief the light carries
EDGE = 0.4                           # (below this, in levels, no light: the pool's alpha)


def lum(a):
    return a[..., :3] @ np.array([0.299, 0.587, 0.114])


def main():
    old = np.array(Image.open(os.path.join(ROOT, 'tools', 'src', 'edits', 'vend_pool_before.webp')).convert('RGBA')).astype(float)
    h, w = old.shape[:2]; x0, y0 = AT
    E = gaussian_filter(lum(old), SIGMA, mode='constant')          # the footprint, soft (its outside dark)
    lay = np.array(Image.open(os.path.join(ROOT, 'assets', 'layer_city_off.webp')).convert('RGB')).astype(float)[y0:y0 + h, x0:x0 + w]
    Lp = lum(lay); T = np.clip((Lp + 1.0) / (gaussian_filter(Lp, 3.0) + 1.0), 0.6, 1.4) ** TEX
    lit = lum(old) > 2
    col = old[lit, :3].mean(0); col = col / (col @ np.array([0.299, 0.587, 0.114]))   # (its cold colour, unit luminance)
    new = (E * T)[..., None] * col[None, None, :]
    new *= (old[..., :3].sum((0, 1)) / np.maximum(new.sum((0, 1)), 1e-6))[None, None, :]   # (its light in total)
    a = np.where(new.max(-1) > EDGE, 255.0, 0.0)
    out = np.dstack([np.where(a[..., None] > 0, new, 0.0), a])
    Image.fromarray(np.clip(np.round(out), 0, 255).astype(np.uint8), 'RGBA').save(
        os.path.join(ROOT, 'assets', 'vend_pool.webp'), 'WEBP', lossless=True, quality=100, method=6, exact=True)
    print('vend_pool: soft, peak', np.round(new.max((0, 1)), 1).tolist(), 'total', np.round(new.sum((0, 1))).tolist())


if __name__ == '__main__':
    main()
