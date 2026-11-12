#!/usr/bin/env python3
"""The kept retouches, laid into the street's own layers (the owner's choice among the clean pass's alternatives, branch
agent/clean, tools/relief.py and tools/alt_*.py there): the drinks machines (vend); and the model clean-ups written by
tools/redraw_zones.py: the rooftop unit's fan (fan) and Ichiraku's front with its new signboard (ramen) its door (door) and the plaster below (base).

    python3 tools/bake_retouches.py

Each patch (tools/src/retouches/) replaces the layer's pixels at its place, alpha included (as the street laid it on the GPU):
layer_city_off.webp and street_unlit.webp take vend at (282, 523), fan at (1296, 160), ramen at (1090, 290), door at (1100, 390) and base at (1100, 530); z7_vending.webp (the machines' lit
comp, now 91 x 205 at 280, 522) and z7_vendoff.webp (their stutter, 23 x 166 at 307, 552) are the patches themselves. Lossless,
exact: run again after a tool rewrites a layer (build_zzzsec_unlit.py ...), then the ?v= of what changed and tools/poster.py.
"""
import os
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'tools', 'src', 'retouches')
LAYERS = {'layer_city_off.webp': [('vend_city.webp', 282, 523), ('fan_city.webp', 1296, 160), ('ramen_city.webp', 1090, 290), ('door_city.webp', 1100, 390), ('base_city.webp', 1100, 530)],
          'street_unlit.webp': [('vend_unlit.webp', 282, 523), ('fan_unlit.webp', 1296, 160), ('ramen_unlit.webp', 1090, 290), ('door_unlit.webp', 1100, 390), ('base_unlit.webp', 1100, 530)]}
COPIES = {'z7_vending.webp': 'vend_z7_vending.webp', 'z7_vendoff.webp': 'vend_z7_vendoff.webp'}


def main():
    for layer, patches in LAYERS.items():
        path = os.path.join(ROOT, 'assets', layer)
        a = np.array(Image.open(path).convert('RGBA'))
        for f, x, y in patches:
            p = np.array(Image.open(os.path.join(SRC, f)).convert('RGBA'))
            a[y:y + p.shape[0], x:x + p.shape[1]] = p
        if (np.array(Image.open(path).convert('RGBA')) == a).all():
            print(layer, 'already has them'); continue
        Image.fromarray(a, 'RGBA').save(path, 'WEBP', lossless=True, quality=100, method=6, exact=True)
        print(layer, 'laid:', ', '.join(f for f, _, _ in patches))
    for dst, src in COPIES.items():
        b = open(os.path.join(SRC, src), 'rb').read(); path = os.path.join(ROOT, 'assets', dst)
        if not os.path.exists(path) or open(path, 'rb').read() != b:
            open(path, 'wb').write(b); print(dst, 'from', src)


if __name__ == '__main__':
    main()
