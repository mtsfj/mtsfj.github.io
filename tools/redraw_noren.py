#!/usr/bin/env python3
"""Ichiraku's noren, redrawn clean (package clean-3): assets/ichiraku_noren.webp from one clean drawing of the curtain
at rest, lit (tools/src/edits/noren_model.webp, from noren_prompt.txt, on a flat green ground).

    python3 tools/redraw_noren.py        writes assets/ichiraku_noren.webp (then its ?v= in street.js)

The atlas is street.js's (IRNR): 4 frames of 79 x 104 (at rest, then the hem lifted to the left by three gusts), in two
rows (base: the cloth as the street lights it; lit: with the shop's light through it). The old atlas
(tools/src/edits/noren_before.webp) gives the outline of each frame and the light the shop adds; the drawing gives the
cloth:
- lit, frame 0: the drawing (its ground keyed out, its slits left open onto the doorway behind), boxed down to scene
  pixels, darkened back from the brightened picture the drawing was made from, inside the old outline;
- the gusts: rows shifted left as the old frames shift them (SHIFTS), each frame inside its old outline;
- base: the lit picture times the old base's light against the old lit row's (per channel, smoothed).
Same input, same bytes.
"""
import os
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'tools', 'src', 'edits', 'noren_model.webp')
OLD = os.path.join(ROOT, 'tools', 'src', 'edits', 'noren_before.webp')
OUT = os.path.join(ROOT, 'assets', 'ichiraku_noren.webp')
FW, FH = 79, 104
BRIGHT = 0.6                     # the drawing was made from the lit frame raised to this power
# per frame, (first row, shift) steps: rows from that one on move that many pixels (left), as measured on the old frames
SHIFTS = {0: [], 1: [(66, -1)], 2: [(48, -1), (84, -2)], 3: [(52, -1), (76, -2), (94, -3)]}


def drawing():
    a = np.array(Image.open(SRC).convert('RGB')).astype(float)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    alpha = 1 - np.clip((g - np.maximum(r, b) - 40) / 80.0, 0, 1)
    a[..., 1] = np.minimum(g, np.maximum(r, b) + 10)
    rgb = np.stack([np.array(Image.fromarray((a[..., c] * alpha).astype(np.float32), 'F').resize((FW, FH), Image.BOX)) for c in range(3)], -1)
    al = np.array(Image.fromarray(alpha.astype(np.float32), 'F').resize((FW, FH), Image.BOX))
    col = rgb / np.maximum(al, 1e-6)[..., None]
    col = ((np.clip(col, 0, 255) / 255.0) ** (1.0 / BRIGHT)) * 255.0
    return col, al >= 0.5


def shifted(img, f):
    out = img.copy()
    for y0, s in SHIFTS[f]:
        out[y0:] = np.roll(img[y0:], s, axis=1)
        if s < 0: out[y0:, s:] = 0 if out.ndim == 2 else out[y0:, s:]
    return out


def main():
    old = np.array(Image.open(OLD).convert('RGBA')).astype(float)
    col, on = drawing()
    o_base, o_lit = old[:FH, :FW], old[FH:, :FW]
    m0 = (o_lit[..., 3] > 0) & on
    lit0 = np.dstack([col * m0[..., None], m0 * 255.0])
    ratio = np.stack([(gaussian_filter(o_base[..., c] * (o_base[..., 3] > 0), 3) + 1) / (gaussian_filter(o_lit[..., c] * (o_lit[..., 3] > 0), 3) + 1) for c in range(3)], -1)
    base0 = lit0.copy(); base0[..., :3] = np.clip(lit0[..., :3] * np.clip(ratio, 0, 1.5), 0, 255)
    atlas = np.zeros_like(old)
    for f in range(4):
        keep = old[FH:, f * FW:(f + 1) * FW, 3] > 0                    # this frame's old outline
        for r, im in enumerate((base0, lit0)):
            fr = np.stack([shifted(im[..., c], f) for c in range(4)], -1)
            fr[..., 3] *= keep; fr[..., :3] *= (fr[..., 3] > 0)[..., None]
            atlas[r * FH:(r + 1) * FH, f * FW:(f + 1) * FW] = fr
    Image.fromarray(np.clip(np.round(atlas), 0, 255).astype(np.uint8), 'RGBA').save(OUT, 'WEBP', lossless=True, quality=100, method=6, exact=True)
    print('wrote', OUT)


if __name__ == '__main__':
    main()
