#!/usr/bin/env python3
"""Kirua's skateboard: leaning on his back with its tail caught in the gutter (it stood near upright on the roof's slope).

    python3 tools/kirua_board.py      (it takes the sheet back from commit BEFORE each time, so it can be run again)

The board leaned 11 degrees on his back, its foot on the eave's top edge as if it stood on the slope by itself. Each of its
nine frames (the gusts rock it off his back and it falls back: lean 11.4 .. 7.5 degrees) is turned about the point where
its top rests on his back (PIVOT), by TURN degrees, so its foot swings out and down into the gutter: leaning 20.4 .. 16.5
degrees now, its tail wedged in the gutter, the gutter's lit front (LIP rows under the eave's top edge) hiding its end. The
turn is made at 8x (nearest), each scene pixel then taking the colour most of its 64 samples have (no colour made up, no
blended edge). The soft shadow it cast under its foot on the roof goes (its foot is in the gutter now). The sheet keeps its
size and place (KM.board in assets/street.js; its lean list and its rest angle there follow). Needs git, Pillow, numpy.
"""
import io
import os
import subprocess
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = lambda p: os.path.join(ROOT, 'assets', p)
BEFORE = 'e53d4da'                   # (the sheet as baked: the board near upright)
CELL, N, AT = (29, 43), 9, (284, 139)   # a frame's size, the frames, the sheet's place in the scene (KM.board)
PIVOT = (24.5, 1.5)                  # (in a frame) where its top rests on his back
TURN = 9.0                           # degrees, its foot out from him
LIP = 3                              # the gutter's lit front starts this many rows under the eave's top edge: its end hidden there
SS = 8


def main():
    sheet = np.asarray(Image.open(io.BytesIO(subprocess.run(['git', 'show', f'{BEFORE}:assets/killua_board.webp'], cwd=ROOT,
                                                             capture_output=True, check=True).stdout)).convert('RGBA'))
    city = np.asarray(Image.open(A('layer_city_off.webp')).convert('RGBA'))
    W, H = CELL
    edge = {x: int(np.where(city[100:260, AT[0] + x, 3] > 0)[0].min()) + 100 - AT[1] for x in range(W)}   # (the eave's top edge, frame rows)
    out = np.zeros_like(sheet)
    for f in range(N):
        cell = sheet[:, f * W:(f + 1) * W].copy()
        cell[cell[..., 3] < 200] = 0                                         # (the board only: its soft shadow goes)
        big = Image.fromarray(cell).resize((W * SS, H * SS), Image.NEAREST)
        big = np.asarray(big.rotate(-TURN, resample=Image.NEAREST, center=(PIVOT[0] * SS, PIVOT[1] * SS)))
        blk = big.reshape(H, SS, W, SS, 4).transpose(0, 2, 1, 3, 4).reshape(H, W, SS * SS, 4)
        for y in range(H):
            for x in range(W):
                s = blk[y, x]; on = s[s[:, 3] > 0]
                if len(on) * 2 < SS * SS or y >= edge[x] + LIP: continue        # (mostly sky; or behind the gutter's front)
                cols, n = np.unique(on, axis=0, return_counts=True)
                out[y, f * W + x] = cols[n.argmax()]
    Image.fromarray(out, 'RGBA').save(A('killua_board.webp'), 'WEBP', lossless=True, quality=100, method=6, exact=True)
    print('board: turned', TURN, 'deg about', PIVOT, '| foot rows', [int(np.where(out[:, f * W:(f + 1) * W, 3].any(1))[0].max()) for f in range(N)])


if __name__ == '__main__':
    main()
