#!/usr/bin/env python3
"""The shop window of the apartment building left of the pole (B's ground floor, the owner's pick: "le plus beau c'est la
fenêtre") on its hours: lit while the shop is open, its room dark once it shuts.

    (a module: tools/redraw_zones.py's zone 'bshop' calls draw() on the street as the zones before it leave it, last;
     it writes assets/win_b_shop.webp, the comp street.js lights on the shop's hours)

The room was baked lit in the street's layer: the same warm room at 22 h, at 3 h, in every state but the power cut, a
light that never changed. Now its light is a comp of its own (COMP_KIND 'shop', NSCHED 'bshop' in street.js: open
8:30 to midnight, catching with a stutter as it opens, sputtering out as it shuts, steady with a rare waver of its tube
between; out in the power cut, red in the red night, as every comp). The comp is the lit room as the street drew it:
every pixel of the window, its sill and frame and the bike's basket under it that its warm light reaches (the light
over the power cut, warm, above MIN_LIGHT). Under it the street's layer takes the room shut: the power cut's room (the
street_unlit pixels: the room dark) plus the street lamp's cool light the plaster round the window has (its mean over
the plaster beside the window), so the dark glass and its frame stay in the wall's light. The power cut is not
changed. Needs numpy and Pillow.
"""
import os
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOX = (948, 536, 1004, 664)                     # the zone (redraw_zones.py 'bshop'): the window, its sill, the basket under it
WALL = [(946, 540, 952, 640), (958, 522, 1000, 534), (958, 666, 1000, 680)]   # (the plaster beside, over and under it)
LUMA = np.array([0.299, 0.587, 0.114])
MIN_LIGHT = 4.0                                 # (the shop's light, of 255, over the power cut)
COMP = 'win_b_shop'


def draw(city, unlit, box=BOX):
    """The zone: the lit room out of the street's layer into the comp, the shut room in its place; returns what changed."""
    x0, y0, x1, y1 = box
    H, W = city.shape[:2]
    c, u = city[y0:y1, x0:x1, :3], unlit[y0:y1, x0:x1, :3]
    d = np.clip(c - u, 0, None)
    Ld = d @ LUMA
    m = (Ld > MIN_LIGHT) & (d[..., 0] >= d[..., 2] + 2)          # (its warm light: not the street lamp's blue)
    ys, xs = np.where(m)
    wall = np.concatenate([np.clip(city[b:e, a:f, :3] - unlit[b:e, a:f, :3], 0, None).reshape(-1, 3) for a, b, f, e in WALL])
    cool = wall.mean(0)                                           # (the street lamp's light on the plaster round it)
    a0, a1, b0, b1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    comp = np.zeros((b1 - b0, a1 - a0, 4), np.uint8)
    comp[..., :3] = np.clip(np.round(c[b0:b1, a0:a1]), 0, 255).astype(np.uint8)
    comp[..., 3] = np.where(m[b0:b1, a0:a1], 255, 0)
    Image.fromarray(comp, 'RGBA').save(os.path.join(ROOT, 'assets', COMP + '.webp'), 'WEBP', lossless=True, quality=100,
                                       method=6, exact=True)
    print(f'{COMP}: {int(m.sum())} px at ({x0 + a0}, {y0 + b0}) {a1 - a0} x {b1 - b0}; the shut room the power cut\'s + {np.round(cool, 1)}')
    c[m] = np.clip(u + cool, 0, 255)[m]
    ch = np.zeros((H, W), bool); ch[y0:y1, x0:x1] = m
    return ch
