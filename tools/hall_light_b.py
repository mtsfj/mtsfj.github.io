#!/usr/bin/env python3
"""The apartment building's entrance hall left of the pole (B's, the switch box on its wall) in the same warm white as the
entrance right of it (the owner, choosing the warm white there: "le hall rose de B aussi").

    (a module: tools/redraw_zones.py's zone 'hallB' calls draw() on the street as the zones before it leave it, last)

The hall (x 1003..1022, y 520..701: its lit back wall and side, seen past the pole) was pink-violet, its light on the
sidewalk before it too. As tools/hall_light.py does for the other entrance: the hall's light is what the street has
over the power cut (street_unlit.webp, the hall dark there); each pixel keeps its light's brightness, the light takes
hall_light.py's tone (TONE), and where it is most of the pixel the power cut's colour under it goes with it. In the hall
every light is its own; on the sidewalk only its pink (a light no greener than it is blue: the shop window's warm light
beside it is left as it is). In the power cut the hall's wall was a dim mauve: it is the building's plaster there (its
lightness kept, the hue of the plaster round the hall in the power cut), so the hall is out like the rest of the
building. The switch box on its wall takes the same light in street.js (swRim). The red night reads its light from the
two layers, so it follows. The shop window (x < 1003) and the pole (x > 1022) are outside. Needs numpy.

The hall's old pink ran further than the zone: a band of it along the sidewalk and over the kerb onto the road, down to
x ~805, the downpipe and the shop window's frame by B's corner lit pink, all cut by a straight line at the zone's left
edge (x 975), pink on one side and the warm white on the other. The zone 'hallBwalk' (WALK, last in redraw_zones.py)
retones that pink the same way (draw() called with its box): one source, one tone, no seam.
"""
import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hall_light

BOX = (975, 520, 1023, 762)                     # the zone (redraw_zones.py 'hallB'): the hall, the sidewalk before it
HALL = (1003, 520, 1023, 702)                   # the hall itself (x0, y0, x1, y1)
PLASTER = (945, 452, 1000, 520)                 # (the building's plaster over the shop, in the power cut: its hue)
WALK = (800, 495, 975, 766)                     # the zone 'hallBwalk': the hall's pink left of BOX (sidewalk, road, B's corner)
WALK_CORNER = 938                               # (above the sidewalk only B's corner, x >= this: not the Pokemon Center's light)
WALK_GROUND = 636                               # (the sidewalk and the road from this row down)
LUMA = np.array([0.299, 0.587, 0.114])


def walk(city, unlit, box=WALK):
    """The zone 'hallBwalk': the hall's pink light left of BOX in the warm white, as draw() does on the sidewalk (each
    pixel its light's brightness, the power cut under it as it is); the street's layer only."""
    x0, y0, x1, y1 = box
    H, W = city.shape[:2]
    c, u = city[y0:y1, x0:x1, :3], unlit[y0:y1, x0:x1, :3]
    d = np.clip(c - u, 0, None)
    Ld = d @ LUMA; Lu = u @ LUMA
    yy, xx = np.mgrid[y0:y1, x0:x1]
    pink = (Ld > hall_light.MIN_LIGHT) & (d[..., 0] > d[..., 1] + 1) & (d[..., 2] >= d[..., 1] - 1)
    pink &= (yy >= WALK_GROUND) | (xx >= WALK_CORNER)
    t = np.array(hall_light.TONES[hall_light.TONE], float); t = t / (t @ LUMA)
    w = (Ld / np.maximum(Ld + Lu, 1e-6))[..., None]
    new = np.clip(u * (1 - w) + Lu[..., None] * w + Ld[..., None] * t, 0, 255)
    c[pink] = new[pink]
    ch = np.zeros((H, W), bool); ch[y0:y1, x0:x1] = pink
    return ch


def draw(city, unlit, box=BOX):
    """The zone (redraw_zones.py): both layers changed in place over box; returns what changed (whole scene)."""
    if tuple(box) == WALK:
        return walk(city, unlit, box)
    x0, y0, x1, y1 = box
    H, W = city.shape[:2]
    c, u = city[y0:y1, x0:x1, :3], unlit[y0:y1, x0:x1, :3]
    u0 = u.copy()
    yy, xx = np.mgrid[y0:y1, x0:x1]
    hall = (xx >= HALL[0]) & (xx < HALL[2]) & (yy >= HALL[1]) & (yy < HALL[3])
    d = np.clip(c - u0, 0, None)
    Ld = d @ LUMA; Lu = u0 @ LUMA
    lit = (Ld > hall_light.MIN_LIGHT) & (d[..., 0] > d[..., 1] + 1)
    pink = lit & (d[..., 2] >= d[..., 1] - 1)
    m = (hall & lit) | (~hall & pink)
    # the power cut: the hall's mauve made the plaster's dark (its lightness kept)
    ref = unlit[PLASTER[1]:PLASTER[3], PLASTER[0]:PLASTER[2], :3].reshape(-1, 3).mean(0)
    hue = ref / max(ref @ LUMA, 1e-6)
    un = np.where(hall[..., None], Lu[..., None] * hue, u0)
    # the street: the light retoned over that power cut
    t = np.array(hall_light.TONES[hall_light.TONE], float); t = t / (t @ LUMA)
    w = (Ld / np.maximum(Ld + Lu, 1e-6))[..., None]
    base = un * (1 - w) + Lu[..., None] * w
    new = np.clip(base + Ld[..., None] * t, 0, 255)
    c[m] = new[m]
    rest = hall & ~m                                                  # (the hall's unlit corners: the same plaster)
    c[rest] = np.clip(un + (c - u0), 0, 255)[rest]
    u[hall] = np.clip(un, 0, 255)[hall]
    ch = np.zeros((H, W), bool); ch[y0:y1, x0:x1] = m | hall
    return ch
