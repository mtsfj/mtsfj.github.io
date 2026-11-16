#!/usr/bin/env python3
"""Where a layer changed against a git revision: each changed region's pixel count and box (x0, x1, y0, y1), so a merge or a fix
can be checked to touch only the place it meant to.

    python3 tools/dev/changed_regions.py [REV] [LAYER]      (REV default HEAD; LAYER default assets/layer_city_off.webp)

Needs Pillow, numpy, scipy.
"""
import io, subprocess, sys
import numpy as np
from PIL import Image
from scipy import ndimage

rev = sys.argv[1] if len(sys.argv) > 1 else 'HEAD'
layer = sys.argv[2] if len(sys.argv) > 2 else 'assets/layer_city_off.webp'
old = Image.open(io.BytesIO(subprocess.run(['git', 'show', f'{rev}:{layer}'], capture_output=True, check=True).stdout))
A = np.asarray(old.convert('RGBA')).astype(int)
B = np.asarray(Image.open(layer).convert('RGBA')).astype(int)
d = np.abs(A - B).max(2) > 2
lab, n = ndimage.label(ndimage.binary_dilation(d, iterations=8))
print(f'{int(d.sum())} pixels changed in {layer} against {rev}')
for i in range(1, n + 1):
    m = (lab == i) & d
    if m.sum():
        ys, xs = np.nonzero(m)
        print(f'  {int(m.sum()):6d} px  x {xs.min()}..{xs.max()}  y {ys.min()}..{ys.max()}')
