#!/usr/bin/env python3
"""The Expedition's banner on the balcony of the house at the street's end, and a small plaque by its door.

    python3 tools/e33_banner.py      (it reads the street's layers and writes them back; again: the same)

The house at the end of the street (x 762-870) has a balcony across its upper floor: its top rail on row 546 (lit by the
sky along its top), its balusters every 9-10 px (x 773, 783, 792: a lit left side, a shade beside), its floor's dark
edge on rows 563-565. The banner hangs over its left bay as the owner's drawing has it (tools/src/e33_banner_v2_33.webp:
a black cloth on a rod with a ball finial, two iron clamps, gold piping down both sides, a brushed gold 33 with drips,
its foot torn on a diagonal, longer on the right; only the cloth and its rod are taken, the drawing's own balcony is the
house's here), redrawn by hand at the house's scale (about 22 px a metre there: its doors are 44 px): the rod 20 px (0.9
m) on two short brackets over the rail's posts, its finial a lit ball of 2 x 2; the cloth 15 px wide (0.7 m), held by
the clamps at its corners and sagging a pixel between them, near black (darker than the wall), its folds falling from
the clamps; in place of the drawing's 33 (the Monolith carries it) a crest of 7 x 7 px, a ring and its heart, a pale gold dye lit on its upper left; the piping down
both sides, the left one lit (toward the sky), ending where the tear begins; the tear on a diagonal down to the right,
its hem one clean cut, a shade darker; its tip on row 570: the lantern's light on the ground
floor (the comp win_z9_lantern) starts on row 571 under it, so none of its pixels are ever drawn over the banner. Its
shadow (SHADE) on the wall under the rod and on the rail and wall along its right side (the light from the sky, up and
left).
The lantern lights its tip as it lights the wall beside it: two pixels of the banner's tip (TIPLIT) are put in the
lantern's own comp, each the banner's colour scaled as the comp scales the wall pixels nearest it (their lit / unlit
ratio, by channel, a little less farther off), so that warmth comes and goes with the lantern, the fuses' cut and the
red night.
The plaque: bronze, 4 x 7 px upright on the house's left post by the door (PLAQUE), its top and left edges lit, its face
pale (polished), a column of dark letters on it (its words are the page's, on hover: « Pour ceux qui viendront après »).
In layer_city_off, and in street_unlit each pixel darkened as the facade round it is (the median of its wall's cut 7 px
about it: the house is lit the same in the fuses' cut, but for a few hundredths by its corner); night_far stays 0 (the street), street_sun 0. What it covers
is kept as it was in tools/src/e33_banner_under.png (written on the first run, read on the next): run again, the same.
Needs Pillow, numpy.
"""
import os
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = lambda p: os.path.join(ROOT, 'assets', p)
ROD = (772, 541)                       # the banner's top-left (its finial), scene px
PLAQUE = (764, 598)                    # the plaque's top-left (on the post's face, between its joints at 762 and 769)
LAST = 570                             # the banner's lowest row (the lantern's comp starts under it)
PAL = {                                # (its golds toned to the facade's light: about as much above the wall as its lit rail)
    'K': (70, 60, 58), 'k': (44, 38, 42), 'd': (24, 21, 27),          # the finial (a ball, 2 x 2): its lit top-left, its body, its shade
    'R': (54, 47, 52), 'r': (26, 23, 30), 'c': (40, 35, 40),          # the rod (dark wood): its top lit by the sky, its underside; its end cap
    'B': (46, 46, 76),                                                # a bracket (iron, on the rail), its face lit as the rail's top
    'i': (12, 12, 20), 'I': (34, 34, 52),                             # a clamp, its lit top
    '0': (13, 12, 16), '1': (18, 16, 21), '2': (23, 21, 27), '3': (30, 27, 34),   # the cloth, black in the house's haze (as dark as the wall, not its blue): deep fold .. crest
    'h': (40, 35, 34), 'G': (33, 29, 30), 'g': (26, 23, 26),          # its piping (dark gold, a step off the cloth): lit (the left, toward the sky), mid, in shade
    'H': (78, 70, 58), 'P': (64, 58, 50), 'p': (50, 46, 41), 'q': (40, 36, 34),   # its crest (a ring and its heart, a pale gold dye, in the haze): lit, mid, its shaded side
    'T': (74, 64, 57), 't': (30, 25, 29), 's': (58, 50, 45), 'x': (16, 14, 24),   # the plaque (bronze, its face polished): its lit edges, its letters, its face, its shadow
}
SHADE = 0.72                           # 'z': the banner's shadow on what is under it (the wall, the rail): that pixel, darker
BANNER = [                             # cols 0.. = x 772.., rows 0.. = y 541..
    "KkRRRRRRRRRRRRRRRRRc",
    "kdrIrrrrrrrrrrrIrrrc",
    "zBgi3zzzzzzzzz3igzBz",
    ".Bh2122101221212GzB.",
    ".Bh2122101221212GzB.",
    "..h1121012101211Gz..",
    "..G11210HHP01211Gz..",
    "..h1121H121p1211Gz..",
    "..h112H01210p211Gz..",
    "..G112H01P10p211Gz..",
    "..h112H01210p211Gz..",
    "..h1121P121p1211Gz..",
    "..G11210ppp01211Gz..",
    "..G1121012101211Gz..",
    "..h1121012101211Gz..",
    "..h1121012101211Gz..",
    "..G1121012101211Gz..",
    "..h1121012101211Gz..",
    "..h1121012101211Gz..",
    "..g1121012101211Gz..",
    "...g121012101211Gz..",
    "....gg1012101211Gz..",
    "......g012101211Gz..",
    ".......gg2101211Gz..",
    ".........g101211Gz..",
    "..........g01211Gz..",
    "...........gg211Gz..",
    ".............g11Gz..",
    "..............ggGz..",
    "...............ggz..",
]
BRACKETS = []                          # (in BANNER: 'B', the brackets under the rod's ends, down to the rail, lit on their face)
UNDER, UBOX = os.path.join(ROOT, 'tools', 'src', 'e33_banner_under.png'), (760, 540, 796, 608)   # what it covers, as it was (x0, y0, x1, y1)
LANTERN = 'win_z9_lantern.webp'      # the lantern's light on the ground floor (a comp at 775, 559): it reaches the banner's tip
LBOX = (775, 559)
TIPLIT = [(788, 569), (788, 570)]       # (the tip's pixels it lights, as it lights the wall beside them)
PLQ = [                                # a name plate, upright as by a Japanese door: its lit edges, one column of letters as faint dots
    "TTTx",
    "Tstx",
    "Tssx",
    "Tstx",
    "Tssx",
    "Tstx",
    "xxxx",
]


def grid(rows):
    h, w = len(rows), max(len(r) for r in rows)
    a = np.zeros((h, w, 4), np.uint8)
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch in PAL: a[y, x, :3] = PAL[ch]; a[y, x, 3] = 255
    return a


def main():
    city = np.asarray(Image.open(A('layer_city_off.webp')).convert('RGBA')).astype(float)
    unlit = np.asarray(Image.open(A('street_unlit.webp')).convert('RGBA')).astype(float)
    x0, y0, x1, y1 = UBOX                                               # (from what was there before it, both layers: once or again, the same)
    if os.path.exists(UNDER):
        u = np.asarray(Image.open(UNDER).convert('RGBA')).astype(float); hh = y1 - y0
        city[y0:y1, x0:x1], unlit[y0:y1, x0:x1] = u[:hh], u[hh:]
    else:
        Image.fromarray(np.concatenate([city[y0:y1, x0:x1], unlit[y0:y1, x0:x1]]).astype(np.uint8), 'RGBA').save(UNDER)
    new = city.copy()
    for (x, y0, y1) in BRACKETS:
        new[y0:y1 + 1, x, :3] = PAL['b']
    for rows, (x0, y0) in ((BANNER, ROD), (PLQ, PLAQUE)):
        for j, r in enumerate(rows):
            for i, ch in enumerate(r):
                if ch in PAL: new[y0 + j, x0 + i, :3] = PAL[ch]; new[y0 + j, x0 + i, 3] = 255
                elif ch == 'z': new[y0 + j, x0 + i, :3] = city[y0 + j, x0 + i, :3] * SHADE
        assert (x0, y0) == PLAQUE or y0 + len(rows) - 1 <= LAST
    ch = np.any(new != city, axis=-1)
    r = np.clip((unlit[..., :3] + 0.5) / (city[..., :3] + 0.5), 0.5, 1.0)   # the cut on the facade round each pixel (the median, by channel,
    for (y, x) in zip(*np.nonzero(ch)):                                       # of what was there 7 px about it): it darkens as its wall does
        w = r[max(0, y - 7):y + 8, max(0, x - 7):x + 8].reshape(-1, 3)
        unlit[y, x, :3] = new[y, x, :3] * np.median(w, 0); unlit[y, x, 3] = 255
    for arr, name in ((new, 'layer_city_off.webp'), (unlit, 'street_unlit.webp')):
        Image.fromarray(np.clip(np.round(arr), 0, 255).astype(np.uint8), 'RGBA').save(A(name), 'WEBP', lossless=True, quality=100, method=6, exact=True)
    # the lantern's light on the tip: in its own comp (so it comes and goes with the lantern, the fuses and the red night), each
    # pixel the banner's, lit as the comp lights the wall pixels nearest it (their lit / unlit ratio, by channel)
    lan = np.asarray(Image.open(A(LANTERN)).convert('RGBA')).astype(float)
    keep = lan[..., 3] > 200
    for (x, y) in TIPLIT: keep[y - LBOX[1], x - LBOX[0]] = False             # (the wall it lights, not the tip itself on a second run)
    ly, lx = np.nonzero(keep)
    for (x, y) in TIPLIT:
        d = np.hypot(lx + LBOX[0] - x, ly + LBOX[1] - y); near = np.argsort(d)[:4]
        rr = np.mean([(lan[ly[q], lx[q], :3] + 0.5) / (city[ly[q] + LBOX[1], lx[q] + LBOX[0], :3] + 0.5) for q in near], 0)
        fall = max(0.0, 1 - (d[near].mean() - 1) / 6)                     # (fainter a little farther from what it lights)
        lan[y - LBOX[1], x - LBOX[0], :3] = np.clip(new[y, x, :3] * (1 + (rr - 1) * fall), 0, 255); lan[y - LBOX[1], x - LBOX[0], 3] = 255
    Image.fromarray(np.clip(np.round(lan), 0, 255).astype(np.uint8), 'RGBA').save(A(LANTERN), 'WEBP', lossless=True, quality=100, method=6, exact=True)
    ys, xs = np.nonzero(ch)
    print('banner at %d, %d; plaque at %d, %d; %d px changed in x %d-%d, y %d-%d; %s: %d px' % (ROD + PLAQUE + (ch.sum(), xs.min(), xs.max(), ys.min(), ys.max(), LANTERN, len(TIPLIT))))


if __name__ == '__main__':
    main()
