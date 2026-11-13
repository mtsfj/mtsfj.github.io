#!/usr/bin/env python3
"""The street lamp's pool of light on the ground (assets/lamp_pool.webp, laid additively by street.js at 673, 707) taken
off the right pole: the pole stands on the sidewalk in front of the light the pool paints on the ground, so where the pole
is (its trace, COCC.pole in assets/street.js) the pool adds nothing (its foot read as see-through: the pavement's light
on it, a survey, 2026-11-13). The lamp's cone of lit air skips the pole the same way (assets/street.js, lcAir).

    python3 tools/pole_light_mask.py      (reads tools/src/edits/lamp_pool_before.webp, the pool as it was; the same bytes
                                           each time)
"""
import json, os, re
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AT = (673, 707)


def main():
    a = np.array(Image.open(os.path.join(ROOT, 'tools', 'src', 'edits', 'lamp_pool_before.webp')).convert('RGBA'))
    h, w = a.shape[:2]; x0, y0 = AT
    runs = json.loads(re.search(r'const COCC = (\{.*?\});', open(os.path.join(ROOT, 'assets', 'street.js'), encoding='utf-8').read()).group(1))['pole']['runs']
    n = 0
    for ya, yb, xa, xb in runs:
        for y in range(max(ya, y0), min(yb, y0 + h - 1) + 1):
            xs = slice(max(xa, x0) - x0, min(xb, x0 + w - 1) - x0 + 1)
            n += int((a[y - y0, xs, 3] > 0).sum()); a[y - y0, xs] = 0
    Image.fromarray(a, 'RGBA').save(os.path.join(ROOT, 'assets', 'lamp_pool.webp'), 'WEBP', lossless=True, quality=100, method=6, exact=True)
    print('lamp_pool: the pole taken off it,', n, 'px')


if __name__ == '__main__':
    main()
