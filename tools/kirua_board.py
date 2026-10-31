#!/usr/bin/env python3
"""Kirua's skateboard: across his lap, wheels down on his thighs, under his hand (it stood near upright on the roof's slope,
touching only his hair).

    python3 tools/kirua_board.py      (it reads the board's colours from commit BEFORE, so it can be run again)

The board stood on its tail on the roof's slope, leaning 11 degrees with its top against his hair: it could not stand so.
It now lies across his lap, as a board is held sitting: seen side on along his thighs (DECK: its ends, its underside's
row at each end, a pixel over the thighs' top), its nose and tail turned up, its two near wheels on his thighs (3 px
discs, lit on their upper side by the sky) under their trucks, his hand resting on it (the deck passes under his hand).
Its colours are the old board's own (its shade, body, mid, lit and highlight tones); the page grades it as before (the
sunset, the night, the cut). Drawn in front of his body and legs (KM.board's plane, assets/street.js); the sheet keeps
its nine frames (the same picture: it no longer rocks in the gusts). Needs git, Pillow, numpy.
"""
import io
import os
import subprocess
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = lambda p: os.path.join(ROOT, 'assets', p)
BEFORE = 'e53d4da'                   # (the board as baked, standing: its colours are taken from it)
DECK = ((309, 188), (345, 190))       # the deck's two ends: column, its underside's row there (over his thighs, under his hand)
AT, SIZE, N = (304, 178), (46, 20), 9   # the sheet's frame: its place in the scene (KM.board), its size, its frames
WHEELS = (0.16, 0.84)                # its near wheels along it (share of its length)


def main():
    old = np.asarray(Image.open(io.BytesIO(subprocess.run(['git', 'show', f'{BEFORE}:assets/killua_board.webp'], cwd=ROOT,
                                                          capture_output=True, check=True).stdout)).convert('RGBA'))[:, :29].astype(float)
    op = old[old[..., 3] > 220][:, :3]; lum = op @ [0.299, 0.587, 0.114]
    tone = lambda lo, hi: np.round(op[(lum >= lo) & (lum < hi)].mean(0))
    SHADE, BODY, MID, LIT, HIGH = tone(0, 36), tone(36, 42), tone(42, 55), tone(55, 80), tone(80, 256)
    W, H = SIZE; f = np.zeros((H, W, 4), np.uint8)

    def put(x, y, c):
        X, Y = x - AT[0], y - AT[1]
        if 0 <= X < W and 0 <= Y < H: f[Y, X, :3] = c; f[Y, X, 3] = 255

    (x0, y0), (x1, y1) = DECK; n = x1 - x0
    row = lambda x: round(y0 + (y1 - y0) * (x - x0) / n)                   # (its underside's row at x)
    for x in range(x0, x1 + 1):                                             # the deck: its top edge lit, its body; nose and tail up
        k = min(x - x0, x1 - x); up = 2 if k == 0 else 1 if k <= 2 else 0
        put(x, row(x) - 1 - up, HIGH if k == 0 else LIT); put(x, row(x) - up, BODY if k else MID)
    for w in WHEELS:                                                        # a near wheel under it, its truck between
        c = round(x0 + w * n); r = row(c)
        put(c, r + 1, SHADE); put(c + 1, r + 1, SHADE)
        for dx, dy, col in ((-1, -1, HIGH), (0, -1, LIT), (1, -1, MID), (-1, 0, LIT), (0, 0, MID), (1, 0, SHADE), (0, 1, SHADE)):
            put(c + dx, r + 3 + dy, col)                                    # (a 3 px disc: lit up and left, shaded down)
    sheet = np.concatenate([f] * N, axis=1)
    Image.fromarray(sheet, 'RGBA').save(A('killua_board.webp'), 'WEBP', lossless=True, quality=100, method=6, exact=True)
    print('board: across his lap, x', DECK[0][0], '..', DECK[1][0], '| frame', AT, SIZE, '| px', int((f[..., 3] > 0).sum()))


if __name__ == '__main__':
    main()
