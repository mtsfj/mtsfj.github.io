#!/usr/bin/env python3
"""assets/fuji_tree.webp: the cherry's small gaps veiled, the dusk left exactly as painted.

    python3 tools/cherry_gaps.py      (once; then tools/fuji_aux.py)

The cherry (fuji_tree.webp) has small gaps inside its canopy (148 of them, 1 to 168 px) where the sky behind shows. At
the painted dusk that sky is coral, the blossoms' own tone: they read as light through the tree. At every other hour the
sky takes the hour and the tree keeps its colours, so they turned to spots: dark violet at night, sky blue in the morning.
Each gap gets a veil of 60 %: what the dusk shows there (the sky's own pixel, layer_sky.webp as its plane maps it) is
painted into the gap with the alpha that keeps the dusk's result unchanged (a * c + (1 - a) * sky = what it was). By day
the gap is then the dusk's light through the blossoms, a soft lighter cluster, under 40 % of the sky. The canopy's outer
outline, open to the sky, is left as it is. Needs Pillow, numpy and scipy.
"""
import os
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = lambda p: os.path.join(ROOT, 'assets', p)
BOX = (376, 66)                        # the far layers' place in the scene
SKY = (-160, -160, 1776, 1136)         # the sky's plane (x, y, w, h), its image stretched over it
VEIL = 0.6


def main():
    ft = np.asarray(Image.open(A('fuji_tree.webp')).convert('RGBA')).astype(float)
    fn = np.asarray(Image.open(A('fuji_night.webp')).convert('RGBA')).astype(float)
    sky = np.asarray(Image.open(A('layer_sky.webp')).convert('RGB')).astype(float)
    H, W = ft.shape[:2]; yy, xx = np.mgrid[0:H, 0:W]; X, Y = xx + BOX[0], yy + BOX[1]
    op = ft[:, :, 3] > 128
    gaps = ndi.binary_fill_holes(op) & ~op & (X >= 740) & (fn[:, :, 3] <= 128)
    sx = np.clip(((X + 0.5 - SKY[0]) / SKY[2] * sky.shape[1]).astype(int), 0, sky.shape[1] - 1)
    sy = np.clip(((Y + 0.5 - SKY[1]) / SKY[3] * sky.shape[0]).astype(int), 0, sky.shape[0] - 1)
    behind = sky[sy, sx]
    a0 = ft[:, :, 3:4] / 255
    c = (a0 * ft[:, :, :3] + (VEIL - a0) * behind) / VEIL      # (a * c + (1 - a) * sky: the dusk's result kept)
    out = ft.copy()
    out[gaps, :3] = np.clip(np.round(c[gaps]), 0, 255); out[gaps, 3] = round(VEIL * 255)
    Image.fromarray(out.astype(np.uint8), 'RGBA').save(A('fuji_tree.webp'), 'WEBP', lossless=True, quality=100, method=6, exact=True)
    print('gaps veiled:', int(gaps.sum()), 'px')


if __name__ == '__main__':
    main()
