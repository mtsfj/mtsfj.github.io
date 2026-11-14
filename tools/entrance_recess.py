#!/usr/bin/env python3
"""The pink-lit entrance right of the pole: no canopy over it, its recess in the wall, and its end against Ichiraku (the
owner: "petit truc bizarre entre ça et la façade d'Ichiraku", then "haut-vent porte rose : à virer, laisse le renfoncement
du mur").

    (a module: tools/redraw_zones.py's zone 'recess' calls draw() on the street as the zones before it leave it)

What was there (the 'pole' zone's draft, x 1069..1118, y 466..528): a corrugated awning seen from above, though it would
hang over the eye, its lower edge ragged; under it a black band down to the lit transom; at its right end, against
Ichiraku's front, a dark slot four pixels wide (x 1115..1119), the corner of the two walls lost in it. (A thin aluminium
canopy replaced it a while; the owner wanted none.)
Now, in the street's own camera (the vanishing point 700, 615, f 960 px, the eye 1.41 m up; the house's front a plane
4.45 m right of the eye's line, its foot on the sidewalk's line v -0.283, as the 'pole' zone found it), the entrance is
what its drawing below already says, a recess: the door and its transom 17 cm back in the wall (the left reveal the
draft drew, x 1068..1081, is that depth seen from here), its head 2.49 m up, a hand over the transom:
- the house's dark vertical planks run down from under the ledge to the recess's head (each column its own plank, from
  the painter's rows under the ledge);
- the head's underside, seen from below: a thin band between the wall's line and the door's (both on the vanishing
  point), closed on the left by the reveal's top edge (level: it lies square to the view), lit from the transom under it
  (the hall's light, lighter toward the door, in two steps; dark in the power cut: the light the 'hall' zone tones);
- over the transom's frame, the door's own wall in the recess's shade; the reveal carried up to the head;
- the corner: the two buildings meet as they do above and below the old slot (the house's last plank, the seam, then
  Ichiraku's corner and its plaster, each column the painter's from under it, rows 548..600, its light the plaster's
  beside it row by row): no slot.
The power cut from its own pixels by the same rule. The pole's pixels (x < 1065) and the house's corner trim
(x 1065..1068) are not touched. Needs Pillow, numpy.
"""
import numpy as np

VPX, VPY, FOC, EYE = 700.0, 615.0, 960.0, 1.41
BOX = (1065, 452, 1124, 532)                    # the zone (redraw_zones.py 'recess')
XF, XD = 4.45, 4.62                             # the house's front, the door's plane (m right of the eye's line)
HEAD = 2.49                                     # the recess's head (m up)
ZFAR = 960 * XF / (1067.5 - VPX)                # its far side (the reveal), from the wall's edge at x 1067.5 (m)
LEDGE_V = 0.3938                                # the ledge's underside (a ray: v = (615 - y) / (x - 700))
TRANSOM_V = 0.229                               # the transom's top frame (a ray, on the door's plane)
X_WALL = (1069, 1115)                           # the planks' columns (the corner trim left of them, the seam right)
JUNCTION = (1116, 1119, 459, 528)               # the corner's columns and the old slot's rows
BELOW = (548, 600)                              # (the corner's rows under the entrance: the clean junction)
PLASTER_REF = 1122                              # (Ichiraku's plaster beside it: its light row by row)
SHADE = 0.55                                    # the door's wall over the transom, in the recess's shade
HEAD_LIGHT = (0.22, 0.12)                       # the transom's light on the head's underside: by the door, by the wall


def ray(x, v):
    """The row (float) of the ray v at column x (pixel centres)."""
    return VPY - v * (x + 0.5 - VPX) - 0.5


V_WALL, V_DOOR = (HEAD - EYE) / XF, (HEAD - EYE) / XD
Y_REVEAL = VPY - FOC * (HEAD - EYE) / ZFAR      # the reveal's top edge (level), row
X_DOOR_EDGE = VPX + FOC * XD / ZFAR             # the door's plane at the far side (column)


def planks(arr, x):
    """The house's plank at column x: the painter's colour under the ledge (rows 3..8 under its underside)."""
    r = int(np.floor(ray(x, LEDGE_V))) + 1
    return np.median(arr[r + 3:r + 9, x, :3], 0), r + 3


def draw(city, unlit, box=BOX):
    """The zone (redraw_zones.py): both layers changed in place over box; returns what changed (whole scene)."""
    x0, y0, x1, y1 = box
    H, W = city.shape[:2]
    ch = np.zeros((H, W), bool)
    src = {'city': city.copy(), 'unlit': unlit.copy()}
    # the transom's light (the street over the power cut, on its glass), for the head's underside
    tr = (slice(522, 546), slice(1083, 1112))
    light = np.median((src['city'][tr][..., :3] - src['unlit'][tr][..., :3]).reshape(-1, 3), 0)
    for arr, tag in ((city, 'city'), (unlit, 'unlit')):
        s = src[tag]
        for x in range(X_WALL[0], X_WALL[1] + 1):
            p, r0 = planks(s, x)
            yw = ray(x, V_WALL)                                      # the wall's line at the head
            yb = Y_REVEAL if x + 0.5 < X_DOOR_EDGE else ray(x, V_DOOR)   # the head's far edge: the reveal's top, the door's line
            r1 = int(np.ceil(ray(x, TRANSOM_V)))                     # (the transom's frame: from here down, as it is)
            base = np.median(s[r1:r1 + 4, x, :3], 0)                 # (the reveal, left of the door: carried up)
            for y in range(max(r0, y0), min(r1, y1)):
                c = y + 0.5
                if c < yw:                                           # the planks
                    col = p
                elif c < yb:                                         # the head's underside, lit from the transom
                    k = HEAD_LIGHT[0] if (c - yw) > 0.5 * (yb - yw) else HEAD_LIGHT[1]
                    col = p * 0.6 + (light * k if tag == 'city' else 0)
                elif x + 0.5 < X_DOOR_EDGE:                          # the reveal, up to the head
                    col = base
                else:                                                # the door's wall over the transom
                    col = p * SHADE
                arr[y, x, :3] = col; ch[y, x] = True
        # the corner: as under the entrance (each column its own), its light the plaster's beside it
        ja, jb, ra, rb = JUNCTION
        ref = np.median(s[BELOW[0]:BELOW[1], PLASTER_REF, :3], 0) + 1
        for x in range(ja, jb + 1):
            base = np.median(s[BELOW[0]:BELOW[1], x, :3], 0)
            for y in range(ra, rb + 1):
                k = np.clip((s[y, PLASTER_REF, :3] + 1) / ref, 0.7, 1.3)
                arr[y, x, :3] = base * k; ch[y, x] = True
    return ch
