#!/usr/bin/env python3
"""The right pole's foot, planted in the sidewalk (the owner: "la transition poteau trottoir pas dingue").

    a zone of tools/redraw_zones.py ('polefoot', `tool`): run that, then tools/bake_retouches.py; it also writes
    assets/gl_lamp.webp (from tools/src/edits/gl_lamp_before.webp: the same bytes each time)
    python3 tools/pole_foot.py --preview DIR   (only shows it: the layers as they are now, before and after, x4, in DIR,
                                                with the three files to render; nothing in the repository changes)

The painter's pole ended in a flat cut on the sidewalk, its last fifty rows crossed by the sidewalk's joints (its foot
read as see-through), its dark outline gone under y 705, one pixel narrower at its left foot: a box laid on the
pavement. Now, in the street's own camera (tools/zone5_facades.py's: the vanishing point 700, 615, f 960 px, the eye
1.41 m up; the pole as street.js places it, SOL: 3.19 m right of the eye's line, its foot 8.89 m away on the sidewalk,
0.15 m up; its radius from its 42 painted columns):
- its foot solid down to the ground: each column the painter's own pole a little higher (rows 686-705, clean: their
  median, and their fine grain cycled down the lit face), the lit face, the two conduits and the outline running on
  into the pavement;
- where it enters the pavement, the circle of its foot seen from the eye: an ellipse, so its bottom sags from its edges
  (row 750, the painter's) to 753 a little right of its middle (the point nearest the eye); its last rows a shade darker
  (the wet foot, the ground's occlusion);
- the ground's occlusion right round the foot, in the layers (the light that stays all night, and the power cut's):
  an ellipse on the ground plane, darkest in the crease;
- the lamp's shadow, in the lamp's own light on the ground (assets/gl_lamp.webp, added by street.js with the lamp's
  level: none by day, none in the power cut, half in the red night): the lamp hangs on the pole's arm 1.5 m to its left
  at its depth, so the pole's shadow runs right along the sidewalk at the foot's depth, soft with the glass's size
  (a disc 0.4 m across) and wider with distance, as far as the lamp's light reaches; the occlusion there too, and the
  lamp's light taken off the new rows of the foot.
What stands over it stays as it is: the pole's trace (COCC in street.js: occlusion, the lamp's air and pool taken off it,
the dry ground under it in wet.webp) already covers the solid foot but for a few pixels of its sag (rows 750-753, under
the trace's last rows): they lie in front of the sidewalk under the pole, where nothing behind the pole reaches and the
wet pass mirrors only the pole's own dark foot (its mirror line there is the pole's base on the road, 766, or its
outline's, 742). Needs Pillow, numpy, scipy.
"""
import os
import sys
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDITS = os.path.join(ROOT, 'tools', 'src', 'edits')
VPX, VPY, FOC, EYE = 700.0, 615.0, 960.0, 1.41   # the street's camera (zone5_facades.py)
WALK = 0.15                                       # the sidewalk's height (m; SOL 'trottoir droit')
PX0, PX1 = 1023, 1064                             # the pole's columns (its dark outline .. its last dark column)
ZP = 8.89                                         # its foot's depth (m; SOL 'poteau')
CX = 0.5 * (PX0 + PX1 + 1)                        # its axis on the screen (1044)
XP = (CX - VPX) * ZP / FOC                        # (m)
RP = 0.5 * (PX1 + 1 - PX0) * ZP / FOC             # its radius (m)
SRC = (686, 706)                                  # its clean rows (under the small bar at 683-684)
GRAIN = 1026                                      # (from this column on, the source's fine grain cycled down; the outline
                                                  # and the dark edge beside it each one value, their median)
TOP = 704                                         # the first row redrawn (the joints crossed it from 707)
FOOT = (5, 0.7)                                   # its last rows darker: over this many rows, down to this factor
AO = (0.16, 0.32)                                 # the ground's occlusion: its reach from the pole's surface (m), its floor
LAMP = (1.70, 8.89, 0.20)                         # the lamp's glass: X, Z, radius (m; street.js LC: x 883, at the pole's depth)
GL = ('gl_lamp', (296, 720), (995, 720, 1260, 800))   # its light on the ground: the file, where street.js lays it, what is
                                                  # shaded here (x0, y0, x1, y1)
BOX = (995, 690, 1100, 800)                       # the zone in the layers (redraw_zones.py 'polefoot')


def ground(x, y, h=WALK):
    """The point at height h under pixel centres (x, y): its X, Z (m)."""
    Z = FOC * (EYE - h) / np.maximum(y + 0.5 - VPY, 1e-3)
    return (x + 0.5 - VPX) * Z / FOC, Z


def front_row(x, h=WALK):
    """The row (float) where the pole's circle at height h shows its front edge in column x."""
    ys = []
    for s in (0.25, 0.5, 0.75):                        # (within the column: its front-most point)
        t = (x + s - VPX) / FOC                         # the ray's X / Z; (X - XP)^2 + (Z - ZP)^2 = RP^2 with X = t Z
        a, b, c = t * t + 1, -2 * (t * XP + ZP), XP * XP + ZP * ZP - RP * RP
        d = b * b - 4 * a * c
        Z = (-b - np.sqrt(d)) / (2 * a) if d > 0 else ZP
        ys.append(VPY + FOC * (EYE - h) / Z)
    return float(np.mean(ys))


def pole_mask(box):
    """The solid foot in box: from TOP down to the front of its circle on the sidewalk, column by column."""
    x0, y0, x1, y1 = box
    yy = np.arange(y0, y1)[:, None] + np.zeros((1, x1 - x0))
    m = np.zeros(yy.shape, bool)
    for x in range(max(PX0, x0), min(PX1 + 1, x1)):
        m[:, x - x0] = (yy[:, x - x0] >= TOP) & (yy[:, x - x0] + 0.5 < front_row(x))
    return m


def occlusion(box):
    """The ground's occlusion round the foot (a factor, 1 away from it) in box, and where the ground is."""
    x0, y0, x1, y1 = box
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(float)
    X, Z = ground(xx, yy)
    dist = np.hypot(X - XP, Z - ZP) - RP
    ong = (yy > 735) & ~pole_mask(box) & (dist > -0.02)
    d = np.clip(dist / AO[0], 0, 1)
    return np.where(ong, AO[1] + (1 - AO[1]) * d * d, 1.0), ong, X, Z


def lamp_vis(X, Z, n=7):
    """How much of the lamp's glass (a disc seen from above) a ground point sees past the pole (0..1)."""
    lx, lz, r = LAMP
    vis = np.zeros_like(X); k = 0
    for i in range(n):
        for j in range(n):
            u, v = 2 * (i + 0.5) / n - 1, 2 * (j + 0.5) / n - 1
            if u * u + v * v > 1: continue
            sx, sz = lx + r * u, lz + r * v; k += 1
            dx, dz = X - sx, Z - sz; L2 = dx * dx + dz * dz + 1e-9
            t = ((XP - sx) * dx + (ZP - sz) * dz) / L2  # (the line's closest approach to the pole's axis)
            px, pz = sx + t * dx - XP, sz + t * dz - ZP
            vis += ~((t > 0) & (t < 1) & (px * px + pz * pz < RP * RP))
    return vis / k


def draw_layers(city, unlit, box=BOX):
    """The foot and the occlusion in both layers (whole-scene float RGBA arrays, changed in place)."""
    x0, y0, x1, y1 = box
    pole = pole_mask(box)
    ao, ong, _, _ = occlusion(box)
    changed = np.zeros(pole.shape, bool)
    for arr in (city, unlit):
        sub = arr[y0:y1, x0:x1]
        src = arr[SRC[0]:SRC[1], PX0:PX1 + 1, :3].copy(); n = len(src)
        med = np.median(src, 0)
        for x in range(PX0, PX1 + 1):
            i = x - PX0; c = front_row(x)
            for j in np.nonzero(pole[:, x - x0])[0]:
                y = y0 + j
                p = src[(y - TOP) % n, i] if x >= GRAIN else med[i]
                k = np.clip((c - (y + 0.5)) / FOOT[0], 0, 1)
                sub[j, x - x0, :3] = p * (FOOT[1] + (1 - FOOT[1]) * k); sub[j, x - x0, 3] = 255
        g = ong & (ao < 0.999)
        sub[g, :3] = sub[g, :3] * ao[g][:, None]
        changed |= g | pole
    return changed


def lamp_light():
    """assets/gl_lamp.webp anew from its before copy: off the solid foot, the pole's shadow and occlusion in it (its
    alpha scales its light: scaled here)."""
    name, (gx, gy), box = GL
    g = np.asarray(Image.open(os.path.join(EDITS, name + '_before.webp')).convert('RGBA')).astype(float).copy()
    x0, y0, x1, y1 = box
    ao, ong, X, Z = occlusion(box)
    pole = pole_mask(box)
    f = np.where(ong, ao * gaussian_filter(lamp_vis(X, Z), 0.6), 1.0)
    f[pole] = 0.0
    sub = g[y0 - gy:y1 - gy, x0 - gx:x1 - gx]
    sub[..., 3] = np.round(sub[..., 3] * f)
    sub[sub[..., 3] == 0] = 0
    return g


def save(a, path):
    Image.fromarray(np.round(np.clip(a, 0, 255)).astype(np.uint8), 'RGBA').save(path, 'WEBP', lossless=True, quality=100, method=6, exact=True)


def draw(city, unlit, box=BOX):
    """The zone (redraw_zones.py): the layers changed in place, assets/gl_lamp.webp written; returns what changed in box."""
    ch = draw_layers(city, unlit, box)
    save(lamp_light(), os.path.join(ROOT, 'assets', GL[0] + '.webp'))
    return ch


def preview(out):
    os.makedirs(out, exist_ok=True)
    L = {t: np.asarray(Image.open(os.path.join(ROOT, 'assets', f)).convert('RGBA')).astype(float)
         for t, f in (('city', 'layer_city_off.webp'), ('unlit', 'street_unlit.webp'))}
    A = {t: a.copy() for t, a in L.items()}
    print('pixels changed', int(draw_layers(A['city'], A['unlit']).sum()))
    save(A['city'], os.path.join(out, 'layer_city_off.webp')); save(A['unlit'], os.path.join(out, 'street_unlit.webp'))
    gl = lamp_light(); save(gl, os.path.join(out, GL[0] + '.webp'))
    gb = np.asarray(Image.open(os.path.join(EDITS, GL[0] + '_before.webp')).convert('RGBA')).astype(float)
    B = (975, 650, 1115, 800); (gx, gy) = GL[1]
    for t in ('city', 'unlit'):
        for tag, arr, gg in (('before', L[t], gb), ('after', A[t], gl)):
            z = np.clip(arr[B[1]:B[3], B[0]:B[2], :3], 0, 255).copy()
            if t == 'city':                             # (the lamp's light added as street.js does, lamp at full)
                ys, xs = slice(max(B[1], gy) - gy, B[3] - gy), slice(B[0] - gx, B[2] - gx)
                z[max(B[1], gy) - B[1]:] += gg[ys, xs, :3] * gg[ys, xs, 3:] / 255.0
            z = np.clip(z, 0, 255)
            for gm, suf in ((1.0, ''), (0.5, 'b')):
                Image.fromarray(np.round(255 * (z / 255) ** gm).astype(np.uint8)).resize(((B[2] - B[0]) * 4, (B[3] - B[1]) * 4), Image.NEAREST).save(os.path.join(out, f'{t}_{tag}_x4{suf}.png'))


if __name__ == '__main__':
    if '--preview' in sys.argv: preview(sys.argv[sys.argv.index('--preview') + 1])
    else: print(__doc__)
