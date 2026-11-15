#!/usr/bin/env python3
"""Kirua's hair a notch darker: graded on the sky's lit edge behind him, as Red and Naruto were graded on what surrounds
them (assets/killua_head.webp, from its before copy tools/src/edits/killua_head_before.webp: the same bytes each time).

    python3 tools/killua_hair.py      (once; again after his head's sheet is redrawn: copy it to the before first)

His silver hair, lit by the dusk, came out near white at night (luma up to 255 in the sheet, 228 on screen) against a sky
of 80: the brightest thing on the left of the street after the screens, brighter than the lit edge of anything round
him. Here only the hair (its pale, unsaturated pixels: luma over HAIR_LO, a ramp to full over RAMP) is brought down
toward the sky's lit edge: its lights compressed (luma over KNEE scaled by SLOPE above it), the whole a touch cooler, its
shading and its edges kept (the ramp, no hard cut); his face, his clothes and his dark side are not touched, nor the rim
his lightning lays (killua_head_rim.webp). Needs numpy, Pillow.
"""
import os
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'tools', 'src', 'edits', 'killua_head_before.webp')
OUT = os.path.join(ROOT, 'assets', 'killua_head.webp')
LUMA = np.array([0.299, 0.587, 0.114])
HAIR_LO, RAMP, SAT = 96.0, 30.0, 0.32            # the hair: luma over 96 (fully over 126), saturation under 0.32
KNEE, SLOPE, DIM = 120.0, 0.62, 0.93              # its lights over the knee at 0.62 of their rise; the whole x 0.93
COOL = np.array([0.98, 0.99, 1.03])


def main():
    a = np.asarray(Image.open(SRC).convert('RGBA')).astype(float)
    rgb, al = a[..., :3], a[..., 3]
    L = rgb @ LUMA
    sat = (rgb.max(-1) - rgb.min(-1)) / np.maximum(rgb.max(-1), 1)
    w = np.clip((L - HAIR_LO) / RAMP, 0, 1) * np.clip((SAT + 0.08 - sat) / 0.08, 0, 1) * (al > 0)
    L2 = np.where(L > KNEE, KNEE + (L - KNEE) * SLOPE, L) * DIM
    k = (L2 / np.maximum(L, 1))[..., None] * COOL
    out = rgb * (1 - w[..., None]) + np.clip(rgb * k, 0, 255) * w[..., None]
    o = np.dstack([out, al])
    Image.fromarray(np.round(o).astype(np.uint8), 'RGBA').save(OUT, 'WEBP', lossless=True, quality=100, method=6, exact=True)
    h = w > 0.5
    print('killua_head: hair', int(h.sum()), 'px; its luma p90', round(float(np.percentile(L[h], 90)), 1), '->',
          round(float(np.percentile((out @ LUMA)[h], 90)), 1))


if __name__ == '__main__':
    main()
