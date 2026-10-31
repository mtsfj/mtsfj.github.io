#!/usr/bin/env python3
"""Between the dojo's house and Kirua's: their shared downpipe back, Kirua's house's end wall, its front in one perspective.

    python3 tools/kirua_house_side.py      (after tools/dojo_window.py; it takes its zones back from commit BEFORE each
                                            time, so it can be run again)

The painter had, where the two houses meet, the dojo's house's corner in shadow (x 130..136) and the downpipe both roofs
drain into (x 137..140, from under the upper eave); boards redrawn over the wall had covered them (they ran out into the
sky between the two roofs). They are his again (JUNCTION, from OLD), in each layer, the new tree's leaves still in front.

Kirua's front runs to the painter's vanishing point for these houses (FVP: his boards right of the small window, his
small window's head and sill run to it, his eave within 2 degrees; a little left of and above the street's). Left of that
window its boards had been redrawn toward the street's (VP), across his: they are his again, each pixel the painter's board on its own ray to FVP (a different pixel of that board for each
column, back and forth, so that his grain and contrast stay), taken from his boards right of the window
(SRC_X, his stains of old foliage taken off first: a pixel much darker or lighter than the median along its ray nearby
takes that median), the board a whole number of boards over (FRONT_DTHETA) where its ray finds none. The front goes up
to under the eave (FRONT_TOP, the owner's line, on a ray to FVP, so the dark band under the gutter keeps one width):
where the eave's shadow had left a black wedge, the boards a whole number of boards below, the same shift all along
(a little darker against the eave). Leaves that the black hid, alone in the air over the crown, go with it.

Under its roof's end its end wall shows (SIDE, x 141..157, from SIDE_TOP), its front corner at x 158, as deep as its
front: its boards the front's, round the corner (each row the board that meets the corner there, its grain the front's
along that board, mirrored across the corner, horizontal since that wall faces us), one shade all over (the sunset being
down the street), no sunset on it (street_sun 0). Each pixel taken in each layer from the same place (street_unlit,
street_sun: so the power cut and the hours read it as the boards it comes from); night_far 0 (the street's). Needs git,
Pillow, numpy.
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
ZONE = (100, 0, 340, 440)            # x0, y0, x1, y1: where the crown is found, and this tool's zone
JUNCTION = (129, 30, 141, 330)       # x0, y0, x1, y1: the painter's corner shadow and shared downpipe, his pixels again
SIDE = (141, 158)                    # Kirua's house's end wall: its columns; its front corner at the second
SIDE_TOP, SIDE_FOOT = 84, 430        # (from under its roof's end, as far down as it goes behind the tree)
SIDE_F = 0.66                        # its shade: one tone all over (a flat wall, as deep as the front)
FVP = (700.0, 615.0)                 # Kirua's front's vanishing point: the painter's for these houses (his boards, his small
                                     # window's head and sill run to it; his eave within 2 degrees)
FRONT_TOP = (162, 86)                # its front's top, under the eave: the ray to FVP through this point (the owner's line)
FRONT_X = (158, 325)                 # (its columns, the downpipe past them)
SRC_X = (278, 325)                   # the painter's own boards, right of the small window
SAMPLE_W = 47                        # (taken from these first columns of them)
FRONT_FOOT = 430                     # (as far down as its front is rebuilt, behind the tree)
FRONT_DTHETA = 0.0199                # its boards' spacing seen from FVP (rad)
EAVE_SHADE = (0.72, 3)               # (the eave's shadow on its top: this dark against the eave, gone over that many rows)
WINDOW = (246, 250, 278, 360)        # (the small window's box: its frame and glass in it left as they are)
REACH, OFF, PASSES = 14, 0.16, 2     # (a stain: darker or lighter by this than the median along its ray, this many columns either way)
TUFT, CLEAR = 800, 135               # (a tuft of leaves alone in the air: fewer pixels than this, over this row)
STAIN_Y, STAIN_X = 400, 300          # (black stains on the front taken off above this row and left of this column: the
                                     # awning's roof below, the downpipe's clamps right)
LEAF = 45
LUM = np.array([0.299, 0.587, 0.114])


def load(p, mode='RGBA', at=None):
    data = subprocess.run(['git', 'show', f'{at}:assets/{p}'], cwd=ROOT, capture_output=True, check=True).stdout if at else open(A(p), 'rb').read()
    return np.asarray(Image.open(io.BytesIO(data)).convert(mode)).astype(float)


def save(arr, p, mode):
    Image.fromarray(np.clip(np.round(arr), 0, 255).astype(np.uint8), mode).save(A(p), 'WEBP', lossless=True, quality=100, method=6, exact=True)


def fray(y, x_from, x_to):                                                   # (the row at x_to of the ray to FVP through (x_from, y))
    return FVP[1] + (y - FVP[1]) * (FVP[0] - x_to) / (FVP[0] - x_from)


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
    L = [load(n, m) for n, m in names]; O = [load(n, m, OLD) for n, m in names]; B = [load(n, m, BEFORE) for n, m in names]
    x0, y0, x1, y1 = ZONE
    for l, b in zip(L, B): l[y0:y1, SIDE[0]:FRONT_X[1]] = b[y0:y1, SIDE[0]:FRONT_X[1]]   # (this tool's zone as it was before it)
    city = L[0]; H, W = city.shape[:2]

    # the new tree's leaves (the dark pixels its change put there, joined to the crown through runs of three, and the
    # dark ones close to them): they stay in front of everything here
    o, t = load('layer_city_off.webp', 'RGBA', OLD)[y0:y1, x0:x1], load('layer_city_off.webp', 'RGBA', TREE)[y0:y1, x0:x1]
    still = np.abs(city[y0:y1, x0:x1] - t).sum(2) == 0
    dark = (np.abs(o - t).sum(2) > 0) & still & (t[..., :3] @ LUM < LEAF)
    core = dark & np.roll(dark, 1, 1) & np.roll(dark, -1, 1)
    leaf = grow(flood(core, [(y1 - y0 - 1, x) for x in range(x1 - x0)])) & dark
    front = np.zeros((H, W), bool); front[y0:y1, x0:x1] = leaf | (grow(leaf, 2) & dark)
    wx0, wy0, wx1, wy1 = WINDOW                                             # (the small window: its frame and glass, the navy and
    navy = np.zeros((H, W), bool)                                           # violet joined to its middle, inside its box)
    navy[wy0:wy1, wx0:wx1] = city[wy0:wy1, wx0:wx1, 2] >= city[wy0:wy1, wx0:wx1, 0] - 4
    win = flood(navy, [((wy0 + wy1) // 2, (wx0 + wx1) // 2)])
    box = np.zeros((H, W), bool); box[wy0:wy1, wx0:wx1] = True               # (and whatever its frame encloses: the curtain's
    out = flood(box & ~win, [(y, x) for y in range(wy0, wy1) for x in (wx0, wx1 - 1)] + [(y, x) for x in range(wx0, wx1) for y in (wy0, wy1 - 1)])
    win = box & ~out                                                        # light in the glass is the window's)

    force = np.zeros((H, W), bool)

    # the junction: the painter's corner shadow and shared downpipe
    jx0, jy0, jx1, jy1 = JUNCTION
    n_j = 0
    for y in range(jy0, jy1):
        for x in range(jx0, jx1):
            if front[y, x]: continue
            for l, ol in zip(L, O): l[y, x] = ol[y, x]
            n_j += 1

    def board(x, y):                                                         # (a lit board of the front, as it stands)
        return 0 <= y < H and city[y, x, 3] == 255 and city[y, x, :3] @ LUM >= 30 and city[y, x, 0] > city[y, x, 2] \
            and not front[y, x] and not win[y, x]
    top = {x: int(np.ceil(fray(FRONT_TOP[1], FRONT_TOP[0], x))) for x in range(*FRONT_X)}
    lit = {x: next(y for y in range(top[x], H) if all(board(x, y + i) for i in range(4))) for x in range(*SRC_X)}

    # the painter's boards right of the window: his stains of old foliage off, each against its own board nearby
    n_b = 0
    for _ in range(PASSES):
        src = [l.copy() for l in L]
        for x in range(*SRC_X):
            for y in range(lit[x], FRONT_FOOT):
                if not board(x, y) and not (src[0][y, x, :3] @ LUM < 30 and not front[y, x] and not win[y, x]): continue
                pts = [(int(round(fray(y, x, xx))), xx) for xx in range(x - REACH, x + REACH + 1) if xx != x and xx < SRC_X[1]]
                pts = [(yy, xx) for yy, xx in pts if board(xx, yy)]
                if len(pts) < 6: continue
                med = np.median([src[0][p][:3] for p in pts], 0)
                if abs(src[0][y, x, :3] @ LUM - med @ LUM) > OFF * (med @ LUM):
                    for k, l in enumerate(L): l[y, x] = np.median([src[k][p] for p in pts], 0)
                    n_b += 1

    # leaves the eave's black hid, alone in the air over the crown: they go with the black
    above = np.zeros((H, W), bool)
    for x in range(*FRONT_X): above[top[x]:CLEAR, x] = True
    above[SIDE_TOP:CLEAR, SIDE[0]:SIDE[1]] = True
    held = front.copy()
    for x in range(*FRONT_X): held[:top[x], x] = False
    held[:SIDE_TOP, SIDE[0]:SIDE[1]] = False
    seen = np.zeros((H, W), bool)
    for y, x in zip(*np.where(front & above)):
        if seen[y, x]: continue
        comp = flood(held, [(y, x)]); seen |= comp
        if comp.sum() < TUFT: front &= ~comp

    # over the painter's boards right of the window, up to the owner's line: his boards a whole number of boards below,
    # one shift for all of it
    th = lambda x, y: np.arctan2(y - FVP[1], x - FVP[0])
    K = max(int(np.ceil((th(x, top[x]) - th(x, lit[x] + 2)) / FRONT_DTHETA)) for x in range(*SRC_X))
    src = [l.copy() for l in L]
    good = np.zeros((H, W), bool)
    for x in range(*SRC_X):
        for y in range(lit[x], FRONT_FOOT): good[y, x] = board(x, y)
    n_f = 0
    def take(x, y, ys, xs, g=1.0):
        for k in (0, 1): L[k][y, x, :3] = src[k][ys, xs, :3] * g; L[k][y, x, 3] = 255
        L[2][y, x] = 0; L[3][y, x] = src[3][ys, xs]
    for x in range(*SRC_X):
        for y in range(top[x], lit[x]):
            if front[y, x]: continue
            for k in [K - j for j in range(K)] + [K + j for j in range(1, 12)]:
                ys = int(round(FVP[1] + np.tan(th(x, y) - k * FRONT_DTHETA) * (x - FVP[0])))
                if 0 <= ys < H and good[ys, x]: break
            else: continue
            take(x, y, ys, x, EAVE_SHADE[0] + (1 - EAVE_SHADE[0]) * min(1.0, (y - top[x]) / EAVE_SHADE[1]))
            good[y, x] = True; n_f += 1
    src = [l.copy() for l in L]

    # left of the window and over it: each pixel the painter's board on its own ray to FVP (the same board along it), or
    # where that ray finds none, the board a whole number of boards over
    for x in range(FRONT_X[0], SRC_X[0]):
        first = next((y for y in range(top[x], H) if all(board(x, y + i) for i in range(4))), top[x])   # (its boards as they stood)
        for y in range(top[x], FRONT_FOOT):
            if front[y, x] or win[y, x]: continue
            if y >= first and not force[y, x] and not (city[y, x, 3] == 255 and (city[y, x, 0] >= city[y, x, 2] or (y < STAIN_Y and x < STAIN_X and city[y, x, :3] @ LUM < 35))):
                continue                                                     # (the front's, its black stains too, nothing else)
            got = None
            for k in [0] + [s * j for j in range(1, 12) for s in (1, -1)]:
                a = th(x, y) - k * FRONT_DTHETA
                pts = [(int(round(FVP[1] + np.tan(a) * (xs - FVP[0]))), xs) for xs in range(SRC_X[0], SRC_X[0] + SAMPLE_W)]
                pts = [p for p in pts if 0 <= p[0] < H and good[p]]
                if pts:                                                      # (its grain kept: along the board, a different pixel
                    n = len(pts); i = (SRC_X[0] - 1 - x) % (2 * n)          # of his for each column, mirrored from his edge, back and forth)
                    got = pts[i if i < n else 2 * n - 1 - i]; break
            if not got: continue
            g = EAVE_SHADE[0] + (1 - EAVE_SHADE[0]) * min(1.0, (y - top[x]) / EAVE_SHADE[1])
            take(x, y, got[0], got[1], g); n_f += 1

    # Kirua's house's end wall, under its roof's end: one tone all over, as deep as its front
    sx0, sx1 = SIDE
    n_s = 0
    for x in range(sx0, sx1):
        d = sx1 - x                                                          # (its distance from the front corner)
        for y in range(SIDE_TOP, SIDE_FOOT):
            if front[y, x]: continue
            for k in range(d, d + 60):                                       # (its board: the one meeting the corner on this row;
                xs = sx1 + k; ys = int(round(fray(y, sx1, xs)))              # its grain the front's along that board, mirrored
                if board(xs, ys): break                                      # across the corner, past any leaf)
            else: continue
            for l in L[:2]: l[y, x, :3] = l[ys, xs, :3] * SIDE_F; l[y, x, 3] = 255
            L[2][y, x] = 0; L[3][y, x] = 0
            n_s += 1

    for (n, m), l in zip(names, L): save(l, n, m)
    print('junction', n_j, 'px | front', n_f, 'px rebuilt (FVP', FVP, ', K', K, ') | stains', n_b, 'px | end wall', n_s, 'px')


if __name__ == '__main__':
    main()
