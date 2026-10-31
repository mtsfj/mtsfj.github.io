#!/usr/bin/env python3
"""Between the dojo's house and Kirua's: their shared downpipe back, Kirua's house's end wall, its boards cleaned.

    python3 tools/kirua_house_side.py      (after tools/dojo_window.py; it takes its zone back from commit BEFORE each time,
                                            so it can be run again)

The painter had, where the two houses meet, the dojo's house's corner in shadow (x 130..136) and the downpipe both roofs
drain into (x 137..140, from under the upper eave); boards redrawn over the wall had covered them (they ran out into the
sky between the two roofs). They are his again (JUNCTION, from OLD), in each layer, the new tree's leaves still in front.

Kirua's house stands out from the dojo's toward the street, its roof's end square to us: under that end its end wall
shows (SIDE, x 141..157), its front corner at x 158. Its boards are the front's, round the corner: each row the board
that meets the corner there, its grain the front's along that board (mirrored across the corner), horizontal since that
wall faces us; in the shade, the sunset being down the street (darkest in the inner corner, lighter toward the front
corner, and under the roof's end), and no sunset on it (street_sun 0).

Its front, by the small window (BLOTCH): the old foliage's shadows had left dark stains and a black bar on the boards
(they run on the rays to the street's vanishing point VP, each the same board all along its ray). A pixel much darker than
its own board nearby, or much lighter (the median along its ray, within REACH columns, the window and the leaves left
out) takes that median, in each layer. In layer_city_off, street_unlit, night_far (0, the street's) and street_sun. Needs git, Pillow, numpy.
"""
import io
import os
import subprocess
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = lambda p: os.path.join(ROOT, 'assets', p)
OLD, TREE = '8d4ca3c^', '8d4ca3c'    # (the painter's, before the tree in front of the dojo was changed; the tree's change)
BEFORE = 'acfeeca'                   # (the layers before this tool: its zones taken back from there each run)
ZONE = (100, 0, 340, 430)            # x0, y0, x1, y1: where the crown is found
JUNCTION = (129, 30, 141, 330)       # x0, y0, x1, y1: the painter's corner shadow and shared downpipe, his pixels again
SIDE = (141, 158)                    # Kirua's house's end wall: its columns; its front corner at the second
SIDE_FOOT = 430                      # (as far down as it goes, behind the tree)
SHADE = (0.50, 0.68, 0.72, 6)        # its shade: in the inner corner, at the front corner; under the roof's end, over that many rows
BLOTCH = (186, 182, 322, 300)        # x0, y0, x1, y1: the front's stained boards by the small window
WINDOW = (245, 252, 277, 358)        # (the small window and its frame, left out)
REACH, OFF, PASSES = 14, 0.16, 2                # (its board nearby: this many columns either way; a stain: darker or lighter than it by this)
LEAF = 45
VP = (725.0, 625.0)
LUM = np.array([0.299, 0.587, 0.114])


def load(p, mode='RGBA', at=None):
    data = subprocess.run(['git', 'show', f'{at}:assets/{p}'], cwd=ROOT, capture_output=True, check=True).stdout if at else open(A(p), 'rb').read()
    return np.asarray(Image.open(io.BytesIO(data)).convert(mode)).astype(float)


def save(arr, p, mode):
    Image.fromarray(np.clip(np.round(arr), 0, 255).astype(np.uint8), mode).save(A(p), 'WEBP', lossless=True, quality=100, method=6, exact=True)


def ray(y, x_from, x_to):
    return VP[1] + (y - VP[1]) * (VP[0] - x_to) / (VP[0] - x_from)


def grow(m, n=1):
    for _ in range(n):
        g = m.copy(); g[1:] |= m[:-1]; g[:-1] |= m[1:]; g[:, 1:] |= m[:, :-1]; g[:, :-1] |= m[:, 1:]; m = g
    return m


def flood(ok, seeds):
    hit = np.zeros_like(ok); todo = list(seeds); h, w = ok.shape
    while todo:
        y, x = todo.pop()
        if 0 <= y < h and 0 <= x < w and ok[y, x] and not hit[y, x]:
            hit[y, x] = True; todo += [(y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)]
    return hit


def main():
    names = (('layer_city_off.webp', 'RGBA'), ('street_unlit.webp', 'RGBA'), ('night_far.webp', 'RGB'), ('street_sun.webp', 'RGB'))
    L = [load(n, m) for n, m in names]; O = [load(n, m, OLD) for n, m in names]
    B = [load(n, m, BEFORE) for n, m in names]
    for bx in ((SIDE[0], 0, SIDE[1], SIDE_FOOT), BLOTCH):                   # (this tool's zones as they were before it)
        for l, b in zip(L, B): l[bx[1]:bx[3], bx[0]:bx[2]] = b[bx[1]:bx[3], bx[0]:bx[2]]
    city = L[0]; H, W = city.shape[:2]

    # the new tree's leaves (the dark pixels its change put there, joined to the crown through runs of three, and the
    # dark ones close to them): they stay in front of everything here
    x0, y0, x1, y1 = ZONE
    o, t = load('layer_city_off.webp', 'RGBA', OLD)[y0:y1, x0:x1], load('layer_city_off.webp', 'RGBA', TREE)[y0:y1, x0:x1]
    still = np.abs(city[y0:y1, x0:x1] - t).sum(2) == 0
    dark = (np.abs(o - t).sum(2) > 0) & still & (t[..., :3] @ LUM < LEAF)
    core = dark & np.roll(dark, 1, 1) & np.roll(dark, -1, 1)
    leaf = grow(flood(core, [(y1 - y0 - 1, x) for x in range(x1 - x0)])) & dark
    front = np.zeros((H, W), bool); front[y0:y1, x0:x1] = leaf | (grow(leaf, 2) & dark)

    # the junction: the painter's corner shadow and shared downpipe
    jx0, jy0, jx1, jy1 = JUNCTION
    n_j = 0
    for y in range(jy0, jy1):
        for x in range(jx0, jx1):
            if front[y, x]: continue
            for l, ol in zip(L, O): l[y, x] = ol[y, x]
            n_j += 1

    # Kirua's house's end wall, under its roof's end (the roof's foot over each column: its last dark pixel from the top)
    sx0, sx1 = SIDE
    s0, s1, s2, sn = SHADE
    n_s = 0
    for x in range(sx0, sx1):
        top = next(y for y in range(62, 200) if city[y, x, 3] == 255 and city[y, x, 0] > city[y, x, 2] + 2)   # (the first board under it)
        d = sx1 - x                                                          # (its distance from the front corner)
        f = s0 + (s1 - s0) * (1 - (d - 1) / (sx1 - sx0 - 1))                 # (darker toward the inner corner)
        for y in range(top, SIDE_FOOT):
            if front[y, x]: continue
            for k in range(d, d + 40):                                       # (its board: the one meeting the corner on this row;
                xs = sx1 + k; ys = int(round(ray(y, sx1, xs)))               # its grain the front's along that board, mirrored
                if not front[ys, xs] and city[ys, xs, 3] == 255: break       # across the corner, past any leaf)
            g = f * (s2 + (1 - s2) * min(1.0, (y - top) / sn))               # (under the roof's end, darker still)
            for l in L[:2]: l[y, x, :3] = l[ys, xs, :3] * g; l[y, x, 3] = 255
            L[2][y, x] = 0; L[3][y, x] = 0
            n_s += 1

    # its front by the small window: stains off, each pixel against its own board nearby
    bx0, by0, bx1, by1 = BLOTCH
    wx0, wy0, wx1, wy1 = WINDOW
    def facade(x, y):
        return (0 <= y < H and 0 <= x < W and not front[y, x] and city[y, x, 3] == 255 and not (wx0 <= x < wx1 and wy0 <= y < wy1)
                and city[y, x, 0] > city[y, x, 2] - 6)
    n_b = 0
    for _ in range(PASSES):
        src = [l.copy() for l in L]
        for x in range(bx0, bx1):
            for y in range(by0, by1):
                if not facade(x, y) and not (src[0][y, x, :3] @ LUM < 30 and not front[y, x] and not (wx0 <= x < wx1 and wy0 <= y < wy1)): continue
                pts = [(int(round(ray(y, x, xx))), xx) for xx in range(x - REACH, x + REACH + 1) if xx != x]
                pts = [(yy, xx) for yy, xx in pts if facade(xx, yy)]
                if len(pts) < 6: continue
                med = np.median([src[0][p][:3] for p in pts], 0)
                if abs(src[0][y, x, :3] @ LUM - med @ LUM) > OFF * (med @ LUM):
                    for k, l in enumerate(L):
                        l[y, x] = np.median([src[k][p] for p in pts], 0)
                    n_b += 1

    for (n, m), l in zip(names, L): save(l, n, m)
    print('junction', n_j, 'px | end wall', n_s, 'px | stains', n_b, 'px')


if __name__ == '__main__':
    main()
