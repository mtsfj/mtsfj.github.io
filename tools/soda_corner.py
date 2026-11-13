#!/usr/bin/env python3
"""The drinks corner on the left sidewalk: the tobacco kiosk's lean-to roof in old Japanese tiles, the three drinks
machines under it, the kiosk's front (the owner: "à refaire : le haut-vent toit tuile au-dessus soda, les soda, la
caisse soda").

    (a module: tools/redraw_zones.py's zone 'soda' calls draw() on the street as the zones before it leave it)
    python3 tools/soda_corner.py --preview DIR   (the layers as they are now, before and after, in DIR; nothing in the
                                                  repository changes)

All of it is drawn in the street's own camera (tools/relief.py's, the one the old machines were built in: VP (700, 615),
f 959.5 px, the eye 1.41 m up, the sidewalk 0.15 m; a point X across, Y up, Z along the street is seen at
x = 700 + f X / Z, y = 615 - f (Y - 1.41) / Z): each pixel is cast as 3 x 3 rays onto a few planes and the tiles'
heightfield, the nearest thing each ray meets gives its colour, the nine are averaged (an edge a pixel soft, as the
painter's). Measured on the painting:
- the roof: a lean-to over the kiosk, from Kirua's wall down toward the street. Its top under the flashing on the ray
  v 0.434 (v = (615 - y) / (700 - x)), its eave on v 0.265, its near verge (in the kiosk's front plane, Z 10.99) from
  (226, 411) to (306, 511): a plane 1.48 m long and steep (52 deg), from Z 10.99 to 13.88 (its far verge, against the
  tree, from (325, 452) to (388, 533));
- the machines: their feet from (282, 725) to (349, 707.5) on the sidewalk, a row 2.08 m long at X -4.785 (three
  machines of 0.69 m), 2.03 m high (tools/alt_vend.py, retired, measured them so); the kiosk's side wall above them,
  X -4.81, under the roof.

What is drawn:
- the tiles: sangawara (J-shaped pan tiles), a pan and a roll in each, one every 23.7 cm along the street (so they
  shorten toward the vanishing point: 10 px at the near verge, 6 at the far one) with their pans where the painter's
  corrugations had their troughs at the eave (street.js DRIPS 'kiosk': the water still runs off there), in courses of
  23.5 cm down the slope (their lines run to the vanishing point), each course's foot a step that catches the light
  and casts its shadow on the course under it, each roll's end rounded off; shaded as the painter shades a relief (the
  roll lit along its top, its side toward us darker, the pans darker where they meet the rolls), in his roof's
  colours, no two tiles quite alike; the far verge's last roll catching the dusk (his lit edge); the flashing at the
  top as he painted it;
- the eave: the tiles cut plumb, the eave tiles' lip and the round end of each roll (a row of small ovals, their rims
  lit on top), a thin fascia under them in the shadow; the near verge: the verge tiles' roll and flange toward us,
  their courses, the barge board under them with its lit edge, over the kiosk's gable;
- the kiosk's side wall over the machines (its planks along the street), in the roof's shadow, lit a little by the
  machines' headers in the comp;
- the machines (the comp z7_vending lights them; the layers hold them off, as the power cut and the stutter show
  them): two blue and a red one as the painter had them, each with its lit header, its display window recessed (the far
  jamb's inside, the tube under the lintel, three shelves of samples: cans and bottles cast as cylinders, so the
  nearer hides the farther as the eye sees them, lit from the front and darker as they turn; under each shelf its
  price labels and buttons, now and then one sold out), a backlit poster with a bottle on it, the money plate (the
  amount in red, the coin and bill slots, the lever, the change cup), the outlet's flap, the plinth, the seams; the
  roof's shadow on their top; their light on the bezels round the windows. z7_vendoff (the middle display out while
  its tube stutters) is the street's own pixels where the middle machine lights itself;
- the kiosk's front: its enamel sign (the painter's glyphs, the red even, the rim cream, its rivets, its shadow on the
  planks), its service window as the owner chose it (B: a Showa tobacco window) drawn clean: the jamb's inside, the
  cabin's left wall lit orange, cartons stacked on the shelves behind, the two panes in wooden frames (the right one
  slid open), the cash tray, the low showcase lit from inside with packs laid in rows; lit in its comp (win_z7_kiosk),
  shut in the layers (the same, darkened as the painter darkens a shut window: the night's blue); its two small enamel
  plates, whose marks nobody could read, now 塩 (salt, white on blue) and 〒 (stamps, red on cream), as tobacco shops
  had them.
The power cut: the same, times the painter's own darkening there (1 here). Needs Pillow, numpy, scipy.
"""
import os
import sys
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDITS = os.path.join(ROOT, 'tools', 'src', 'edits')
RET = os.path.join(ROOT, 'tools', 'src', 'retouches')
F, EYE, VP = 959.5, 1.41, (700.0, 615.0)
GROUND = 0.15                                  # the sidewalk's top
BOX = (227, 405, 390, 735)
SS = 3                                         # rays per pixel, each way

# ---- the roof (a lean-to): its plane from the measured rays, its tiles ----
ZN = 10.99                                     # the near verge (the kiosk's front plane)
V_TOP, V_EAVE = 0.434, 0.265                   # its top (under the flashing) and its eave, as rays
XT = (226 - VP[0]) * ZN / F; YT = EYE - V_TOP * XT
XE = (306 - VP[0]) * ZN / F; YE = EYE - V_EAVE * XE
ZF = F * XE / (388.5 - VP[0])                  # the far verge (where the painter's lit edge meets the eave)
L = np.hypot(XT - XE, YT - YE)
TU = np.array([XT - XE, YT - YE]) / L          # up the slope (X, Y)
NR = np.array([TU[1], -TU[0]])                 # the roof's normal (up and out toward the street)
PITCH = 0.2373                                 # a tile's width along the street: its pans where the painter's troughs
PAN0 = 10.9275                                 # were (street.js DRIPS 'kiosk', the water off the eave: kept)
COURSE = 0.235                                 # a course's exposed length up the slope
DP, RR, BASE, STEP = 0.016, 0.032, 0.02, 0.028  # the pan's depth, the roll's height, the battens, a tile's thickness
PANW = 0.62                                    # the pan's share of a tile's width (the roll the rest)
V_KEEP = 0.4265                                # above this ray at the top, the painter's flashing as it is
LIP = (0.03, 0.050)                           # the eave tiles' front lip (height) and the round ends' radius (m)
FASCIA = 0.035                                 # the eave's board under the lip
SODE, BARGE = 0.032, 0.048                     # the verge tiles' flange, the barge board under it (m, down from the plane)
XLIP = XE + (BASE + STEP) * NR[0]           # the eave tiles' front (plumb)
HC = BASE + STEP + 0.1 * RR                   # the round ends' centres, over the plane
XW = -4.81                                     # the kiosk's side wall over the machines
XM, ZM0, ZM1, YM = -4.785, 10.99, 13.07, 2.18  # the machines' front, their row's ends, their top

# the painter's colours (picked on his roof, his flashing, his far verge's lit edge, the kiosk's planks and the dark
# under the verge, in the street as it is)
TILE = [(0.00, (5, 6, 12)), (0.22, (9, 10, 19)), (0.40, (13, 13, 25)), (0.55, (18, 17, 32)), (0.70, (26, 22, 39)),
        (0.84, (38, 28, 47)), (1.00, (62, 38, 62))]
RIM = (118, 48, 70)                            # (his far verge's lit edge: the last roll's crest in the dusk)
WOOD = (25, 15, 28)                            # (his maroon along the verge)
WOOD_D = (12, 10, 21)
PLANK, GROOVE = (18, 29, 58), (12, 20, 40)     # (the kiosk's planks: a board's face, the joint)
UNDER = (11, 11, 22)                           # (the dark under the verge)
LUMA = np.array([0.299, 0.587, 0.114])


def ramp(t, stops):
    """The colour at t (0..1, an array) along stops ((t0, rgb), ...)."""
    t = np.clip(t, 0, 1); out = np.zeros(t.shape + (3,))
    ts = [a for a, _ in stops]; cs = np.array([c for _, c in stops], float)
    for c in range(3): out[..., c] = np.interp(t, ts, cs[:, c])
    return out


def hsh(*a):
    """A fixed pseudo-random number in 0..1 for integer arguments (no two tiles quite alike, the same each run)."""
    x = np.sin(sum(np.asarray(v, float) * k for v, k in zip(a, (12.9898, 78.233, 37.719, 4.581)))) * 43758.5453
    return x - np.floor(x)


def prof(phi):
    """A tile's cross-section along the street (m over the battens' plane): its pan, then its roll."""
    pan = -DP * np.sin(np.pi * np.clip(phi / PANW, 0, 1))
    roll = RR * np.sin(np.pi * np.clip((phi - PANW) / (1 - PANW), 0, 1))
    return np.where(phi < PANW, pan, roll)


def tile_h(Z, s):
    """The tiles' surface over the roof's plane at (Z, s up the slope): the profile, each course's tilt (its lower end
    lies on the course under it: a step of a tile's thickness at each course's foot)."""
    col = (Z - (PAN0 - 0.31 * PITCH)) / PITCH; phi = col - np.floor(col)
    cs = s / COURSE; fr = cs - np.floor(cs)
    p = prof(phi)
    p = np.where(p > 0, p * np.sqrt(np.clip(fr * COURSE / 0.035, 0.25, 1)), p)   # (a roll's end rounded off at its butt)
    return BASE + p + STEP * (1 - fr)


def rays(box, ss=SS):
    """The rays through each pixel's ss x ss sub-points: their directions per unit Z (dx, dy), shape (h, w, ss*ss)."""
    x0, y0, x1, y1 = box
    o = (np.arange(ss) + 0.5) / ss
    X = np.arange(x0, x1)[None, :, None, None] + o[None, None, None, :]
    Y = np.arange(y0, y1)[:, None, None, None] + o[None, None, :, None]
    X, Y = np.broadcast_arrays(X, Y)
    h, w = y1 - y0, x1 - x0
    return ((X - VP[0]) / F).reshape(h, w, ss * ss), ((VP[1] - Y) / F).reshape(h, w, ss * ss)


def on_roof(dx, dy, Z):
    """The point of each ray at Z, in the roof's frame: its height over the plane, its distance up the slope."""
    px, py = dx * Z - XE, EYE + dy * Z - YE
    return NR[0] * px + NR[1] * py, TU[0] * px + TU[1] * py


def cast_tiles(dx, dy, n=40):
    """Where each ray first meets the tiles (Z, or inf): marched through the tiles' slab, then bisected."""
    a = NR[0] * dx + NR[1] * dy; b = -NR[0] * XE + NR[1] * (EYE - YE)
    hmax, hmin = BASE + RR + STEP + 0.005, BASE - DP - 0.005
    z0 = np.maximum((hmax - b) / a, ZN - 0.5); z1 = (hmin - b) / a
    hitz = np.full(dx.shape, np.inf); prev = z0.copy(); found = np.zeros(dx.shape, bool)
    for i in range(n + 1):
        Z = z0 + (z1 - z0) * i / n
        hr, s = on_roof(dx, dy, Z)
        surf = np.where((Z >= ZN) & (Z <= ZF) & (s >= 0) & (s <= L) & (dx * Z <= XLIP), tile_h(Z, s), -9)
        new = ~found & (hr <= surf)
        lo, hi = prev.copy(), Z.copy()
        for _ in range(8):                                 # (bisect between the last miss and the hit)
            m = (lo + hi) / 2; hr_, s_ = on_roof(dx, dy, m)
            inside = (m >= ZN) & (m <= ZF) & (s_ >= 0) & (s_ <= L) & (dx * m <= XLIP)
            ok = inside & (hr_ <= np.where(inside, tile_h(m, s_), -9))
            hi = np.where(ok, m, hi); lo = np.where(ok, lo, m)
        hitz = np.where(new, hi, hitz); found |= new; prev = Z
    return hitz


def plane_x(dx, X):
    """Where each ray meets the plane X = const (a face toward the street): its Z."""
    with np.errstate(divide='ignore'):
        return np.where(dx < 0, X / dx, np.inf)


def shade_tiles(dx, dy, Z):
    """The tiles' colour where the rays met them, as the painter shades a relief: each roll lit along its top, its side
    toward us a little darker, the pans darker where they meet the rolls; each course's foot a lit edge, the course
    under it in its shadow; each tile its own shade."""
    hr, s = on_roof(dx, dy, Z)
    col = (Z - (PAN0 - 0.31 * PITCH)) / PITCH; phi = col - np.floor(col)
    cs = s / COURSE; fr = cs - np.floor(cs)
    riser = np.abs(hr - tile_h(Z, s)) > 0.004                       # (a course's butt, toward the eave)
    u = np.clip((phi - PANW) / (1 - PANW), 0, 1)
    t_pan = 0.44 - 0.20 * np.exp(-phi / 0.07) - 0.20 * np.exp(-(PANW - phi) / 0.06)
    t_roll = np.where(u < 0.5, 0.46 + 0.56 * (u / 0.5) ** 2, 1.02 - 0.9 * (u - 0.5))
    t = np.where(phi < PANW, t_pan, t_roll)
    t = np.where(fr < 0.06, t + 0.18, t)                          # (a course's lower edge catches the light)
    t = t * np.where(fr > 0.86, 0.32, 1.0) * np.where(fr > 0.78, 0.78, 1.0)   # (under the next course's butt: its shadow)
    t = np.where(riser, 0.16, t)
    ti = np.floor(col); ci = np.floor(cs)
    t = t * (0.88 + 0.22 * hsh(ti, ci))
    near_top = np.clip((s - (L - 0.07)) / 0.07, 0, 1)            # (under the flashing: its shadow)
    t = t * (1 - 0.6 * near_top)
    c = ramp(t, TILE)
    # the far verge: the last roll's crest catching the dusk (the painter's lit edge)
    rim = (ZF - Z < 0.035) & ~riser
    c = np.where(rim[..., None], np.array(RIM, float)[None, :] * np.where(fr > 0.86, 0.6, 1.0)[..., None], c)
    return c


def draw_roof(off, box):
    """The roof and what hangs from it in the layer (off: the street, RGB floats over box, changed in place).
    Returns the mask of the pixels drawn and the per-pixel coverage."""
    x0, y0, x1, y1 = box; h, w = y1 - y0, x1 - x0
    dx, dy = rays(box)
    zt = cast_tiles(dx, dy)
    # the eave: the tiles cut plumb at their ends (the eave tiles' front, a lip hanging under the pans, the round end of
    # each roll), the fascia board under them: faces toward the street
    zl = plane_x(dx, XLIP); yl = EYE + dy * zl
    hl = NR[0] * (XLIP - XE) + NR[1] * (yl - YE); sl = TU[0] * (XLIP - XE) + TU[1] * (yl - YE)
    col = (zl - (PAN0 - 0.31 * PITCH)) / PITCH; phi = col - np.floor(col)
    rc = (np.floor(col) + PANW + (1 - PANW) / 2) * PITCH + (PAN0 - 0.31 * PITCH)   # (the roll's middle)
    yc = YE + (XLIP - XE - HC * NR[0]) / TU[0] * TU[1] + HC * NR[1]               # (its round end's centre)
    rr = np.sqrt((zl - rc) ** 2 + (yl - yc) ** 2)
    manju = (rr < LIP[1]) & (zl >= ZN + 0.02)
    lip = ((sl >= 0) & (hl <= tile_h(zl, np.maximum(sl, 0)))) | ((yl <= yc) & (yl >= yc - LIP[0])) | manju
    lip &= (zl >= ZN - 0.004) & (zl <= ZF)
    xf = XLIP - 0.012; zf_ = plane_x(dx, xf); yf = EYE + dy * zf_
    fascia = (yf <= yc - LIP[0] + 0.01) & (yf >= yc - LIP[0] - FASCIA) & (zf_ >= ZN - 0.004) & (zf_ <= ZF)
    # the verge: the verge tiles' flange and the barge board under it, in the kiosk's front plane (toward the eye)
    zv = ZN - 0.004
    hv, sv = on_roof(dx, dy, zv)
    vtop = BASE + STEP * (1 - (sv / COURSE - np.floor(sv / COURSE))) + 0.026   # (its roll, along the edge)
    sode = (hv <= vtop) & (hv >= -SODE) & (sv >= 0) & (sv <= L)
    barge = (hv < -SODE) & (hv >= -SODE - BARGE) & (sv >= -0.02) & (sv <= L)
    # the kiosk's side wall above the machines, under the roof
    zw = plane_x(dx, XW); yw = EYE + dy * zw
    hw_, sw_ = on_roof(dx, dy, zw)
    wall = (zw >= ZN) & (zw <= ZM1 + 0.02) & (yw >= YM) & (hw_ < 0)
    # the nearest of them per ray
    INF = np.inf
    cand = np.stack([np.where(zt < INF, zt, INF), np.where(lip, zl - 1e-4, INF), np.where(fascia, zf_, INF),
                     np.where(sode, zv, INF), np.where(barge, zv - 1e-4, INF), np.where(wall, zw, INF)])
    k = np.argmin(cand, 0); hit = np.isfinite(cand.min(0))
    colr = np.zeros(dx.shape + (3,))
    m = hit & (k == 0)
    if m.any(): colr[m] = shade_tiles(dx[m], dy[m], zt[m])
    m = hit & (k == 1)                                            # the tiles' ends: toward the eave, in the eave's own
    if m.any():                                                    # shade; the round ends' rims catch the sky on top
        t = np.full(m.sum(), 0.30)
        dym = yl[m] - yc
        rim = manju[m] & (rr[m] > LIP[1] - 0.012)
        t = np.where(manju[m], 0.50, t)
        t = np.where(rim & (dym > 0.004), 0.86, np.where(rim & (dym < -0.012), 0.16, t))   # (its rim: lit on top, dark below)
        t = np.where(~manju[m] & (yl[m] < yc - LIP[0] + 0.012), 0.14, t)              # (the lip's lower edge: dark)
        t = t * (0.9 + 0.18 * hsh(np.floor(col[m]), 99))
        colr[m] = ramp(t, TILE)
    m = hit & (k == 2)                                            # the fascia: dark wood in the eave's shadow, its lower
    if m.any():                                                    # edge lit a little
        edge = yf[m] < YE - FASCIA + 0.012
        colr[m] = np.where(edge[:, None], np.array(WOOD, float) * 1.1, np.array(WOOD_D, float))
    m = hit & (k == 3)                                            # the verge tiles: their roll along the edge lit on
    if m.any():                                                    # top, their flange toward us, each course's foot
        frv = sv[m] / COURSE - np.floor(sv[m] / COURSE)
        top = hv[m] > vtop[m] - 0.012
        t = np.where(top, 0.80, np.where(frv > 0.88, 0.14, np.where(frv < 0.06, 0.5, 0.32)))
        colr[m] = ramp(t * (0.9 + 0.18 * hsh(np.floor(sv[m] / COURSE), 7)), TILE)
    m = hit & (k == 4)                                            # the barge board: wood, its lower edge lit
    if m.any():
        edge = hv[m] < -SODE - BARGE + 0.012
        colr[m] = np.where(edge[:, None], np.array(WOOD, float) * 1.3, np.array(WOOD, float) * 0.8)
    m = hit & (k == 5)                                            # the side wall: its planks along the street, in the roof's
    if m.any():                                                    # shadow (darker toward the roof)
        yy = yw[m]; pl = (yy - YM) / 0.105; fr = pl - np.floor(pl)
        base = np.where((fr < 0.16)[:, None], np.array(GROOVE, float), np.array(PLANK, float))
        sh = 0.55 * np.clip(1 - (yy - YM) / 0.9, 0.35, 1)
        colr[m] = base * sh[:, None]
    if os.environ.get('SODA_DEBUG'):                              # (a map of what each pixel's middle ray met)
        pal = np.array([(200, 60, 60), (60, 200, 60), (60, 60, 220), (220, 200, 40), (200, 40, 200), (40, 200, 200), (0, 0, 0)])
        kk = np.where(hit, k, 6)[..., SS * SS // 2]
        Image.fromarray(pal[kk].astype(np.uint8)).resize((w * 6, h * 6), Image.NEAREST).save(os.environ['SODA_DEBUG'])
    cov = hit.mean(-1)
    out = (colr * hit[..., None]).sum(-2) / np.maximum(hit.sum(-1), 1)[..., None]
    # (the painter's flashing at the top as it is)
    X = np.arange(x0, x1)[None, :] + 0.5; Y = np.arange(y0, y1)[:, None] + 0.5
    keep = (VP[1] - Y) / (VP[0] - X) > V_KEEP
    cov = np.where(keep, 0, cov)
    off[:] = off * (1 - cov[..., None]) + out * cov[..., None]
    return cov > 0, cov


# ---- the machines: three drinks machines side by side, their fronts toward the street (X = XM) ----
WM = (ZM1 - ZM0) / 3                           # a machine's width along the street
WIN = (0.07, 0.56, 1.03, 1.83)                 # its display window: u (from its near edge) and Y
DEP = 0.045                                    # the display's depth behind the bezel (its far jamb shows: 3-4 px)
ROW = (WIN[3] - WIN[2]) / 3                    # a shelf's height
STRIP = 0.042                                  # the price and button strip under each shelf
HEAD = (1.87, 2.13)                            # the lit header (the brand)
AD = (0.06, 0.43, 0.56, 0.98)                  # the lower advert panel: u, Y
MONEY = (0.465, 0.64, 0.60, 1.0)               # the money plate: u, Y
OUTLET = (0.07, 0.60, 0.27, 0.47)              # the product outlet (its flap): u, Y
NPROD = 9                                      # samples per shelf
# colours (off, lit): the painter's, measured on his machines and on the comp of the old ones (tools/alt_vend.py's
# families of his displays' drinks; his blue bodies and his red one)
BODY = [((12, 21, 44), (14, 24, 50)), ((12, 21, 44), (14, 24, 50)), ((28, 19, 40), (32, 22, 46))]
BEZEL = [((22, 33, 64), (34, 50, 88)), ((22, 33, 64), (34, 50, 88)), ((44, 26, 48), (64, 36, 62))]
HEADER = [((16, 22, 46), (36, 62, 112)), ((24, 24, 40), (120, 112, 100)), ((30, 18, 32), (104, 32, 46))]
HEADMARK = [((22, 28, 54), (104, 128, 168)), ((30, 24, 42), (124, 46, 56)), ((38, 26, 40), (148, 128, 140))]
ADC = [((12, 22, 30), (28, 66, 54)), ((26, 24, 34), (96, 74, 56)), ((30, 16, 28), (86, 30, 44))]
BACK = ((22, 24, 48), (186, 202, 210))
BACK_LO = ((20, 22, 44), (146, 170, 188))
JAMB = ((36, 40, 72), (142, 168, 190))
SHELF = ((40, 46, 78), (150, 182, 198))
TUBE = ((44, 48, 80), (226, 236, 238))
PRICE = ((16, 20, 44), (44, 74, 128))
LABEL = ((34, 38, 62), (184, 196, 208))
LED = ((24, 30, 56), (112, 178, 218))
SOLD = ((40, 26, 44), (204, 92, 102))
METAL = ((26, 34, 62), (40, 52, 86))
SLOT = ((4, 6, 14), (4, 6, 14))
DIGIT = ((30, 14, 22), (236, 92, 64))
FLAP = ((8, 12, 26), (12, 18, 36))
PROD = [(47, 86, 140), (86, 160, 193), (90, 120, 159), (61, 119, 174), (104, 88, 146), (62, 66, 94), (214, 104, 146),
        (190, 62, 68), (76, 168, 100), (222, 150, 74), (226, 208, 168)]
PROD_W = np.array([6, 6, 6, 6, 5, 4, 6, 6, 5, 5, 4], float)


def products():
    """The samples on the shelves: (machine, shelf, centre Z, radius, foot Y, height, bottle, colour index), fixed."""
    out = []
    cum = np.cumsum(PROD_W) / PROD_W.sum()
    for i in range(3):
        for r in range(3):
            y0 = WIN[2] + r * ROW + STRIP
            kind = (i + r) % 3                          # (a shelf of bottles, of cans, of both)
            prev = -1
            for k in range(NPROD):
                h = float(hsh(i, r, k, 3))
                c = int(np.searchsorted(cum, float(hsh(i, r, k, 1))))
                if c == prev and hsh(i, r, k, 5) > 0.3: c = (c + 3) % len(PROD)
                prev = c
                bottle = kind == 0 or (kind == 2 and h > 0.5)
                z = ZM0 + i * WM + WIN[0] + 0.03 + (k + 0.5) * (WIN[1] - WIN[0] - 0.06) / NPROD
                out.append((i, r, z, 0.023 if bottle else 0.026, y0, (0.19 + 0.02 * h) if bottle else (0.125 + 0.015 * h),
                            bottle, c))
    return out


PRODS = products()


def machines(box):
    """The machines over box, as each pixel's 3 x 3 rays meet them: (off, lit) RGB, the coverage, the machine of each
    pixel's middle ray (-1: none), and the mask of what lights itself (the displays, the headers, the posters)."""
    x0, y0, x1, y1 = box; h, w = y1 - y0, x1 - x0
    dx, dy = rays(box)
    zf = plane_x(dx, XM); yf = EYE + dy * zf
    on = (zf >= ZM0) & (zf <= ZM1) & (yf >= GROUND) & (yf <= YM)
    mi = np.clip(np.floor((zf - ZM0) / WM), 0, 2).astype(int); u = zf - ZM0 - mi * WM
    OFF = np.zeros(dx.shape + (3,)); LIT = np.zeros(dx.shape + (3,))

    def put(m, pair, k=1.0):
        if not m.any(): return
        OFF[m] = np.array(pair[0], float) * k; LIT[m] = np.array(pair[1], float) * k

    def per_machine(m, table, k=1.0):
        for i in range(3): put(m & (mi == i), table[i], k)

    # the body, its bezel round the window, the seams between the machines, the near edge lit a little
    per_machine(on, BODY)
    ua, ub, ya, yb = WIN
    per_machine(on & (u > ua - 0.025) & (u < ub + 0.025) & (yf > ya - 0.03) & (yf < yb + 0.03), BEZEL)
    per_machine(on & (yf > HEAD[0] - 0.015) & (yf < HEAD[1] + 0.015) & (u > 0.03) & (u < WM - 0.03), BEZEL)
    hd = on & (yf > HEAD[0]) & (yf < HEAD[1]) & (u > 0.045) & (u < WM - 0.045)
    per_machine(hd, HEADER)
    mark = hd & (np.abs((yf - (HEAD[0] + HEAD[1]) / 2) - 0.05 * (0.5 - u / WM) * (1 - 2 * (mi == 1))) < 0.012)
    per_machine(mark, HEADMARK)                                      # (the brand: a band, a curve; no words at this size)
    ad = on & (u > AD[0]) & (u < AD[1]) & (yf > AD[2]) & (yf < AD[3])
    for i in range(3):                                               # (backlit: brighter at its top)
        mm = ad & (mi == i)
        put(mm, ADC[i], (0.78 + 0.3 * np.clip((yf[mm] - AD[2]) / (AD[3] - AD[2]), 0, 1))[:, None])
    uc = (AD[0] + AD[1]) / 2                                         # (the drink on the poster: a bottle, pale)
    adm = ad & (((np.abs(u - uc) < 0.045) & (yf > 0.64) & (yf < 0.84)) | ((np.abs(u - uc) < 0.018) & (yf >= 0.84) & (yf < 0.9)))
    for i in range(3):
        mm = adm & (mi == i)
        put(mm, (tuple(np.array(ADC[i][0]) * 1.4), tuple(np.array(ADC[i][1]) * 0.55 + 90)))
    mo = on & (u > MONEY[0]) & (u < MONEY[1]) & (yf > MONEY[2]) & (yf < MONEY[3])
    put(mo, METAL)
    dig = mo & (yf > 0.94) & (yf < 0.975) & (u > 0.49) & (u < 0.62)
    put(dig, DIGIT)                                                  # the amount, lit red
    put(mo & (yf > 0.885) & (yf < 0.905) & (u > 0.52) & (u < 0.60), SLOT)             # the coin slot
    put(mo & (yf > 0.78) & (yf < 0.81) & (u > 0.48) & (u < 0.625), SLOT)              # the bill slot
    put(mo & (yf > 0.84) & (yf < 0.86) & (u > 0.50) & (u < 0.53), LABEL)             # the return lever
    put(on & (u > 0.50) & (u < 0.62) & (yf > 0.62) & (yf < 0.70), SLOT)             # the change cup
    ol = on & (u > OUTLET[0]) & (u < OUTLET[1]) & (yf > OUTLET[2]) & (yf < OUTLET[3])
    put(ol, FLAP)
    put(ol & (yf > OUTLET[3] - 0.018), BEZEL[0])                                       # (its lip catching the light)
    put(on & (yf < GROUND + 0.07), ((6, 9, 18), (7, 10, 20)))                         # the plinth, set back
    put(on & ((u < 0.012) | (u > WM - 0.012)), ((4, 7, 16), (5, 8, 18)))              # the seams
    per_machine(on & (u >= 0.012) & (u < 0.03) & (mi == 0), BEZEL, 1.15)
    # the display windows: into each recess, the nearest of its far jamb, its sill, the tube under its lintel, the price
    # strips, the samples, its back
    win = on & (u > ua) & (u < ub) & (yf > ya) & (yf < yb)
    INF = np.inf
    zj = ZM0 + mi * WM + ub
    xj = dx * zj; yj = EYE + dy * zj
    c_j = np.where(win & (xj >= XM - DEP) & (xj <= XM) & (yj > ya) & (yj < yb), zj, INF)
    with np.errstate(divide='ignore', invalid='ignore'):
        zs = np.where(dy < 0, (ya - EYE) / dy, INF); zt_ = np.where(dy > 0, (yb - EYE) / dy, INF)
    c_s = np.where(win & (dx * zs >= XM - DEP) & (dx * zs <= XM), zs, INF)
    c_t = np.where(win & (dx * zt_ >= XM - DEP) & (dx * zt_ <= XM), zt_, INF)
    zp = plane_x(dx, XM - 0.004); yp = EYE + dy * zp; up_ = zp - ZM0 - mi * WM
    rowp = np.floor((yp - ya) / ROW); fp = yp - ya - rowp * ROW
    strip = win & (fp < STRIP) & (fp >= 0) & (up_ > ua) & (up_ < ub)
    c_p = np.where(strip, zp, INF)
    zb = plane_x(dx, XM - DEP); c_b = np.where(win, zb, INF)
    c_q = np.full(dx.shape, INF); qi = np.full(dx.shape, -1)
    xc = XM - DEP + 0.026
    for n, (i, r, zc, rad, fy, ht, bot, ci) in enumerate(PRODS):
        sel = win & (mi == i)
        if not sel.any(): continue
        # the ray (X = dx Z) against the circle (X - xc)^2 + (Z - zc)^2 = rad^2, in the ground plane
        A = dx * dx + 1; B = -2 * (dx * xc + zc); C = xc * xc + zc * zc - rad * rad
        disc = B * B - 4 * A * C
        ok = sel & (disc >= 0)
        zz = np.where(ok, (-B - np.sqrt(np.maximum(disc, 0))) / (2 * A), INF)
        yy = EYE + dy * zz
        if bot:                                               # (a bottle: its neck narrower over its shoulder)
            neck = yy > fy + 0.72 * ht
            Cn = xc * xc + zc * zc - (0.4 * rad) ** 2; dn = B * B - 4 * A * Cn
            zz = np.where(neck, np.where(dn >= 0, (-B - np.sqrt(np.maximum(dn, 0))) / (2 * A), INF), zz)
            yy = EYE + dy * zz
        ok = ok & np.isfinite(zz) & (yy >= fy) & (yy <= fy + ht)
        closer = ok & (zz < c_q)
        c_q = np.where(closer, zz, c_q); qi = np.where(closer, n, qi)
    cand = np.stack([c_j, c_s, c_t, c_p, c_q, c_b])
    kk = np.argmin(cand, 0); wz = cand.min(0)
    wy = EYE + dy * wz
    put(win & (kk == 0), JAMB)
    put(win & (kk == 1), SHELF)
    put(win & (kk == 2), TUBE)
    m = win & (kk == 3)
    if m.any():
        f = fp[m]; uu = up_[m]; slot = (uu - ua - 0.03) / ((ub - ua - 0.06) / NPROD); sf = slot - np.floor(slot)
        lab = (f > STRIP * 0.48) & (sf > 0.12) & (sf < 0.88)
        led = (f < STRIP * 0.36) & (f > STRIP * 0.08) & (sf > 0.3) & (sf < 0.7)
        sold = led & (hsh(mi[m], rowp[m], np.floor(slot), 9) > 0.86)
        o = np.tile(np.array(PRICE[0], float), (m.sum(), 1)); l = np.tile(np.array(PRICE[1], float), (m.sum(), 1))
        for sel, pair in ((lab, LABEL), (led & ~sold, LED), (sold, SOLD)):
            o[sel] = pair[0]; l[sel] = pair[1]
        OFF[m] = o; LIT[m] = l
    m = win & (kk == 4)
    if m.any():
        q = qi[m]; zz = wz[m]; xx = dx[m] * zz; yy = wy[m]
        P = np.array([(p[2], p[3], p[4], p[5], p[6], p[7]) for p in PRODS], float)
        zc, rad, fy, ht, bot, ci = (P[q, j] for j in range(6))
        nx = (xx - xc) / np.maximum(np.hypot(xx - xc, zz - zc), 1e-6)
        lit_k = 0.42 + 0.62 * np.clip(nx, 0, 1)                            # (lit from the front, darker as it turns)
        cols = np.array(PROD, float)[ci.astype(int)]
        rel = (yy - fy) / ht
        cap = (rel > 0.93) | ((bot > 0) & (rel > 0.88))
        band = (rel > 0.42) & (rel < 0.62)                                   # (its label's band, lighter)
        cl = np.where(band[:, None], cols * 0.55 + 0.45 * np.array(LABEL[1], float), cols)
        cl = np.where(cap[:, None], np.array(LABEL[1], float) * np.where(bot[:, None] > 0, 0.95, 0.75), cl)
        sheen = (np.abs(nx - 0.86) < 0.07) & ~cap                          # (a can's metal: a bright line)
        cl = np.where(sheen[:, None], cl * 0.5 + 120, cl)
        LIT[m] = np.clip(cl * lit_k[:, None], 0, 255)
        OFF[m] = cl * 0.08 + np.array((18, 20, 40), float)
    m = win & (kk == 5)
    if m.any():
        t = np.clip((wy[m] - ya) / (yb - ya), 0, 1)
        fr_ = ((wy[m] - ya) / ROW) % 1
        OFF[m] = np.array(BACK[0], float)
        LIT[m] = (np.array(BACK_LO[1], float) * (1 - t[:, None]) + np.array(BACK[1], float) * t[:, None]) * (0.86 + 0.14 * fr_[:, None])
    # the roof's shadow on them (the sky shut out under the eave): darker toward their top, off and lit alike on the
    # body (the displays and the lit panels have their own light)
    occ = 1 - 0.38 * np.clip((yf - 1.3) / (YM - 1.3), 0, 1)
    OFF *= occ[..., None]
    selflit = win | hd | ad | dig
    LIT = np.where(selflit[..., None], LIT, LIT * occ[..., None])
    # the displays' light on the bezel and the body round them (lit only): a cold glow falling off
    dwin = np.maximum(np.maximum(ua - u, u - ub), np.maximum(ya - yf, yf - yb))
    glow = np.clip(1 - dwin / 0.12, 0, 1) ** 2 * on * ~win
    LIT = LIT + glow[..., None] * np.array((26, 36, 44), float)
    cov = on.mean(-1)
    n = np.maximum(on.sum(-1), 1)[..., None]
    off = (OFF * on[..., None]).sum(-2) / n; lit = (LIT * on[..., None]).sum(-2) / n
    mid = np.where(on[..., SS * SS // 2], mi[..., SS * SS // 2], -1)
    own = (selflit & on).mean(-1) > 0
    return off, lit, cov, mid, own


# ---- the kiosk's front, face on (its planks, its sign, its service window, its two small plates) ----
SIGN = (231, 532, 267, 557)                    # the enamel sign's rim, inclusive (the painter's)
GLASS = (231, 579, 262, 645)                   # inside the service window's frame, inclusive (its sill kept)
COMP_AT, COMP_WH = (230, 575), (40, 73)        # the window's comp (street.js win_z7_kiosk)
PLATES = ((230, 652, 243, 668), (246, 652, 260, 668))   # the two small plates under the window, inclusive
# the glyphs, drawn by hand on the pixel grid: 塩 (salt, which tobacco shops sold) and 〒 (stamps)
SHIO = ['.X....X...',
        '.X...XXXXX',
        'XXX.X.....',
        '.X...XXXX.',
        '.X...X..X.',
        '.X...XXXX.',
        '.X........',
        '.X..XXXXXX',
        '.XX.X.X.XX',
        'XX..X.X.XX',
        '...XXXXXXX']
YUBIN = ['XXXXXXX',
         '.......',
         'XXXXXXX',
         '...X...',
         '...X...',
         '...X...',
         '...X...',
         '...X...']
# the cabin's colours, lit (a warm tube behind the head of the window: the owner's pick B, a Showa service window)
WALL_L = ((166, 96, 54), (118, 60, 40))        # its left wall, top and bottom (the painter's orange)
JAMB_K = (74, 50, 44)
BACKW = ((112, 74, 50), (84, 54, 42))          # the back wall behind the shelves, top and bottom
SHELF_K = (196, 146, 92)
STILE = (58, 36, 30)
CASE_IN = ((200, 160, 102), (152, 106, 64))    # inside the showcase, top and bottom (lit from inside)
CASE_TOP = (214, 180, 128)
CASE_FR = (70, 44, 34)
PACKS = [(214, 206, 190), (178, 52, 48), (64, 86, 158), (200, 160, 74), (70, 128, 86), (226, 222, 214), (40, 52, 104),
         (160, 40, 64), (214, 130, 60)]
TRAY = ((152, 140, 120), (34, 62, 64))         # the cash tray: its rim, its rubber
SHUT = (np.array([0.14, 0.16, 0.27]), np.array([8.0, 10.0, 22.0]))   # shut: lit x k + the night (as the painter's shut one)


def kiosk_window():
    """The service window's inside, lit, over GLASS (rows, columns, RGB)."""
    gx0, gy0, gx1, gy1 = GLASS
    W_, H_ = gx1 - gx0 + 1, gy1 - gy0 + 1
    img = np.zeros((H_, W_, 3))
    lerp = lambda a, b, t: np.array(a, float) * (1 - t) + np.array(b, float) * t
    for j in range(H_):
        y = gy0 + j; t = j / (H_ - 1)
        for i in range(W_):
            x = gx0 + i
            if x <= 232: c = np.array(JAMB_K, float) * (1.0 if x == 232 else 0.7)       # the left jamb's inside
            elif x <= 236: c = lerp(*WALL_L, t) * (1.0 - 0.08 * (x - 233))              # the cabin's left wall
            else: c = lerp(*BACKW, t)                                                    # its back wall
            img[j, i] = c
    # the shelves on the back wall, cartons on them (dimmer: further in)
    for sy in (589, 599, 609):
        for x in range(237, gx1 + 1):
            img[sy - gy0, x - gx0] = SHELF_K; img[sy + 1 - gy0, x - gx0] = np.array(BACKW[1], float) * 0.6
        x = 238; k = 0                                     # (cartons lying flat, in stacks of two or three)
        while x + 4 <= gx1 + 1:
            wdt = 5 if hsh(sy, k, 1) < 0.6 else 4; n = 2 + int(hsh(sy, k, 2) * 2)
            for q in range(n):
                c = np.array(PACKS[int(hsh(sy, k, q, 3) * len(PACKS))], float) * 0.62
                top = sy - 1 - 3 * (q + 1)
                for xx in range(x, min(x + wdt, gx1 + 1)):
                    img[top - gy0, xx - gx0] = c * 1.18
                    img[top + 1 - gy0, xx - gx0] = c
                    img[top + 2 - gy0, xx - gx0] = c * 0.62
            x += wdt + 1; k += 1
    # the two panes in their wooden frames: the meeting stiles, the right pane slid open behind the left one
    for y in range(gy0, 621):
        for x in (249, 250): img[y - gy0, x - gx0] = np.array(STILE, float) * (1.15 if x == 249 else 1.0)
    for x in range(233, gx1 + 1):
        img[620 - gy0, x - gx0] = STILE; img[621 - gy0, x - gx0] = np.array(STILE, float) * 0.7
    # the head's shadow on the top row
    img[0] *= 0.55
    # the showcase counter: its top's lit edge, packs laid in rows under its glass, lit from inside, its frame
    for x in range(233, gx1 + 1):
        img[622 - gy0, x - gx0] = CASE_TOP
    for y in range(623, 644):
        t = (y - 623) / 20
        for x in range(237, gx1 + 1):
            img[y - gy0, x - gx0] = lerp(*CASE_IN, t)
        for x in range(233, 237):
            img[y - gy0, x - gx0] = lerp(*WALL_L, 0.9) * 0.85
    for r, ry in enumerate((625, 631, 637)):            # (packs laid in rows, as a shop lays them: not quite even)
        x = 238 + (r * 2) % 3; k = 0
        while x + 1 <= gx1:
            wdt = 3 if hsh(r, k, 6) < 0.65 else 2
            c = np.array(PACKS[int(hsh(r, k, 7) * len(PACKS))], float) * 0.8 + 0.2 * np.array(CASE_IN[0], float)
            for xx in range(x, min(x + wdt, gx1 + 1)):
                for yy in range(ry, ry + 4):
                    img[yy - gy0, xx - gx0] = c * (1.12 if yy == ry else 0.9 if yy == ry + 3 else 1.0) * (0.8 if xx == x + wdt - 1 else 1.0)
            x += wdt + (1 if hsh(r, k, 8) < 0.8 else 2); k += 1
    for x in range(233, gx1 + 1):
        img[644 - gy0, x - gx0] = CASE_FR; img[645 - gy0, x - gx0] = np.array(CASE_FR, float) * 0.7
    for y in range(622, 646): img[y - gy0, 237 - gx0] = CASE_FR       # (its near end)
    # the cash tray on the counter, at the left
    for x in range(239, 246):
        img[619 - gy0, x - gx0] = TRAY[0]
        img[620 - gy0, x - gx0] = TRAY[1]; img[621 - gy0, x - gx0] = np.array(TRAY[1], float) * 0.75
    # the left pane's glass: a faint slanted sheen, two bands
    for j in range(H_):
        for i in range(W_):
            x, y = gx0 + i, gy0 + j
            if 237 <= x <= 248 and y < 620:
                d = (x - 242) + 0.55 * (y - 600)
                if abs(d) < 1.5: img[j, i] = img[j, i] + 14
                elif abs(d - 5) < 0.6: img[j, i] = img[j, i] + 8
    return np.clip(img, 0, 255)


def draw_glyph(a, rows, x0, y0, col):
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch == 'X': a[y0 + j, x0 + i] = col


def kiosk_front(L, box):
    """The kiosk's front in the layer L (the street over box, RGB floats, changed in place): its sign crisp, its window
    shut (as the painter darkens a shut one), its plates. Returns the window's lit picture over GLASS and the mask of
    the pixels changed."""
    x0, y0 = box[:2]
    ch = np.zeros(L.shape[:2], bool)
    P = lambda x, y: (y - y0, x - x0)
    # the sign: its glyphs as the painter drew them (his light pixels on the red), the red even and deep, the rim cream,
    # four rivets, the plate's edge a pixel darker under it and its shadow on the planks
    sx0, sy0, sx1, sy1 = SIGN
    G = L[sy0 - y0 + 1:sy1 - y0, sx0 - x0 + 1:sx1 - x0]
    glyph = np.clip((G[..., 1] - 45) / 100, 0, 1)                # (his glyphs' strength, edges soft as he drew them)
    glyph[:2] = 0; glyph[-2:] = 0; glyph[:, :2] = 0; glyph[:, -2:] = 0
    for y in range(sy0, sy1 + 1):
        for x in range(sx0, sx1 + 1):
            if y in (sy0, sy1) or x in (sx0, sx1):
                c = (146, 116, 108) if (y == sy0 or x == sx0) else (112, 104, 98)
            else:
                t = ((y - sy0) / (sy1 - sy0) * 0.7 + (x - sx0) / (sx1 - sx0) * 0.3)
                c = np.array((138, 32, 46), float) * (1 - t) + np.array((100, 24, 31), float) * t
                g = glyph[y - sy0 - 1, x - sx0 - 1]
                c = c * (1 - g) + np.array((196, 180, 172), float) * g
            L[P(x, y)] = c; ch[P(x, y)] = True
    for x, y in ((sx0 + 2, sy0 + 2), (sx1 - 2, sy0 + 2), (sx0 + 2, sy1 - 2), (sx1 - 2, sy1 - 2)):
        L[P(x, y)] = (46, 22, 30)
    for x in range(sx0 + 1, sx1 + 2):
        L[P(x, sy1 + 1)] = L[P(x, sy1 + 1)] * 0.55; ch[P(x, sy1 + 1)] = True
    for y in range(sy0 + 1, sy1 + 1):
        L[P(sx1 + 1, y)] = L[P(sx1 + 1, y)] * 0.6; ch[P(sx1 + 1, y)] = True
    # the window, shut, as it is in the layers
    lit = kiosk_window()
    gx0, gy0, gx1, gy1 = GLASS
    L[gy0 - y0:gy1 - y0 + 1, gx0 - x0:gx1 - x0 + 1] = lit * SHUT[0] + SHUT[1]
    for y in range(gy0, gy1 + 1):                    # (shut, the glass gives back a little of the street: the sheen)
        for x in range(237, gx1 + 1):
            if (x <= 248 and y < 620) or 623 <= y < 644:
                d = (x - 242) + 0.55 * (y - 600) - (20 if y >= 623 else 0)
                if abs(d) < 1.5: L[P(x, y)] = L[P(x, y)] + np.array((7, 9, 15), float)
                elif abs(d - 5) < 0.6: L[P(x, y)] = L[P(x, y)] + np.array((4, 5, 9), float)
    ch[gy0 - y0:gy1 - y0 + 1, gx0 - x0:gx1 - x0 + 1] = True
    # the plates: enamel, a cream rim, 塩 white on blue and 〒 red on cream, their shadow on the planks
    for (px0, py0, px1, py1), field, rim, glyph_rows, gcol in (
            (PLATES[0], (22, 30, 66), (76, 76, 80), SHIO, (104, 104, 106)),
            (PLATES[1], (68, 66, 68), (76, 76, 80), YUBIN, (96, 26, 36))):
        for y in range(py0, py1 + 1):
            for x in range(px0, px1 + 1):
                edge = y in (py0, py1) or x in (px0, px1)
                t = (y - py0) / (py1 - py0)
                c = np.array(rim, float) * (1.0 if (y == py0 or x == px0) else 0.78) if edge else np.array(field, float) * (1.06 - 0.16 * t)
                L[P(x, y)] = c; ch[P(x, y)] = True
        gw, gh = len(glyph_rows[0]), len(glyph_rows)
        gx_, gy_ = px0 + (px1 - px0 + 1 - gw) // 2 + ((px1 - px0 + 1 - gw) % 2), py0 + (py1 - py0 + 1 - gh) // 2
        sub = L[gy_ - y0:gy_ - y0 + gh, gx_ - x0:gx_ - x0 + gw]
        draw_glyph(sub, glyph_rows, 0, 0, gcol)
        for x in range(px0 + 1, px1 + 2):
            L[P(x, py1 + 1)] = L[P(x, py1 + 1)] * 0.6; ch[P(x, py1 + 1)] = True
        for y in range(py0 + 1, py1 + 1):
            L[P(px1 + 1, y)] = L[P(px1 + 1, y)] * 0.65; ch[P(px1 + 1, y)] = True
    return lit, ch


# ---- the zone: the layers, the comps ----
CLEAR = (346, 526, 362, 542)                   # (x0, y0, x1, y1: the old beam's lit end past the machines, gone)
VEND = ('z7_vending', 280, 522)                # the machines' lit comp (its place in street.js)
VOFF = ('z7_vendoff', 307, 552, 23, 166)       # the middle display out while its tube stutters (street.js: its box)


def load(path):
    return np.asarray(Image.open(path).convert('RGBA')).astype(float)


def build(city, unlit, box, kcomp):
    """Everything over box from the layers as the zones before leave them (whole-scene RGBA floats, not changed):
    the new street and power cut over box, the three comps (RGBA floats), the mask of what changed."""
    x0, y0, x1, y1 = box
    O = city[y0:y1, x0:x1, :3].copy(); U = unlit[y0:y1, x0:x1, :3].copy()
    new = O.copy()
    klit, kch = kiosk_front(new, box)
    rmask, rcov = draw_roof(new, box)
    moff, mlit, mcov, mid, own = machines(box)
    new = new * (1 - mcov[..., None]) + moff * mcov[..., None]
    # the street under the lit comps, lit: the machines lit; the old comp's light outside them (the painter's: the bench
    # in the alcove, what the displays lit round them) kept, times the change the street took there
    vb = load(os.path.join(EDITS, 'soda_vending_before.webp')); vh, vw = vb.shape[:2]
    _, vx, vy = VEND
    vs = (slice(vy - y0, vy - y0 + vh), slice(vx - x0, vx - x0 + vw))
    litv = new * (1 - mcov[..., None]) + mlit * mcov[..., None]
    a = vb[..., 3] > 0
    oldlit = vb[..., :3]; o0, n0 = O[vs], new[vs]
    kept = np.abs(np.round(new[vs]) - np.round(o0)).max(-1) == 0
    carry = a & (mcov[vs] == 0) & kept
    cx_ = np.arange(vx, vx + vw)[None, :]; cy_ = np.arange(vy, vy + vh)[:, None]
    carry &= (cx_ >= 350) & ~((cx_ >= CLEAR[0]) & (cx_ < CLEAR[2]) & (cy_ >= CLEAR[1]) & (cy_ < CLEAR[3]))   # (the alcove's)
    gain = np.clip((oldlit - o0), 0, 255)                      # (the light the old comp added there)
    lv = litv[vs]
    lv[carry] = np.clip(n0[carry] + gain[carry], 0, 255)
    litv[vs] = lv
    # their headers' cold light on the kiosk's wall just over them (under the roof), falling off upward
    X = np.arange(x0, x1)[None, :] + 0.5; Y = np.arange(y0, y1)[:, None] + 0.5
    xa, xb = VP[0] + F * XM / ZM0, VP[0] + F * XM / ZM1
    ytop = VP[1] - (YM - EYE) * (VP[0] - X) / -XM          # (the machines' top, a ray)
    up = ytop - Y
    gl = np.where((X > xa) & (X < xb - 1) & (up > 0) & (mcov == 0), np.exp(-up / 6.0), 0) * (rcov > 0)
    litv = litv + gl[..., None] * np.array((16, 24, 34), float)
    vcomp = np.zeros((vh, vw, 4))
    d = np.abs(np.round(litv[vs]) - np.round(new[vs])).max(-1) > 0
    vcomp[d, :3] = litv[vs][d]; vcomp[d, 3] = 255
    # the middle display out: the street's own pixels where the middle machine lights itself
    _, ox, oy, ow, oh = VOFF
    os_ = (slice(oy - y0, oy - y0 + oh), slice(ox - x0, ox - x0 + ow))
    ocomp = np.zeros((oh, ow, 4))
    od = (mid[os_] == 1) & (np.abs(np.round(litv[os_]) - np.round(new[os_])).max(-1) > 0)
    ocomp[od, :3] = new[os_][od]; ocomp[od, 3] = 255
    # the kiosk's window: its comp as the kiosk zone left it, the inside of the glass the new lit cabin
    kc = kcomp.copy(); cx, cy = COMP_AT
    gx0, gy0, gx1, gy1 = GLASS
    kc[gy0 - cy:gy1 - cy + 1, gx0 - cx:gx1 - cx + 1, :3] = klit
    kc[gy0 - cy:gy1 - cy + 1, gx0 - cx:gx1 - cx + 1, 3] = 255
    # the power cut: the same, times the painter's own darkening there (unlit over lit, smoothed, channel by channel)
    from scipy.ndimage import gaussian_filter
    dark = np.stack([(gaussian_filter(U[..., c], 4.0) + 1.0) / (gaussian_filter(O[..., c], 4.0) + 1.0) for c in range(3)], -1)
    changed = np.abs(np.round(new) - np.round(O)).max(-1) > 0
    unew = U.copy(); unew[changed] = np.clip(new * np.clip(dark, 0, 1.5), 0, 255)[changed]
    return np.clip(new, 0, 255), unew, vcomp, ocomp, kc, changed


def save(arr, path, mode='RGBA'):
    Image.fromarray(np.clip(np.round(arr), 0, 255).astype(np.uint8), mode).save(path, 'WEBP', lossless=True, quality=100, method=6, exact=True)


def draw(city, unlit, box=BOX):
    """The zone (tools/redraw_zones.py, 'soda'): the layers changed in place; the machines' comps written where
    tools/bake_retouches.py copies them from; the kiosk's window comp handed to redraw_zones (COMP_OUT, written after
    the kiosk zone's); returns what changed in box."""
    rz = sys.modules.get('__main__')
    kz = getattr(rz, 'COMP_OUT', {}).get('kiosk')
    kcomp = kz[1] if kz is not None else load(os.path.join(EDITS, 'kiosk_comp_before.webp'))
    new, unew, vcomp, ocomp, kc, ch = build(city, unlit, box, kcomp)
    x0, y0, x1, y1 = box
    city[y0:y1, x0:x1, :3] = new; city[y0:y1, x0:x1, 3] = 255
    unlit[y0:y1, x0:x1, :3] = unew; unlit[y0:y1, x0:x1, 3] = 255
    save(vcomp, os.path.join(RET, 'vend_z7_vending.webp'))
    save(ocomp, os.path.join(RET, 'vend_z7_vendoff.webp'))
    if hasattr(rz, 'COMP_OUT'): rz.COMP_OUT['soda'] = ['win_z7_kiosk', kc, None]
    return ch


def preview(out):
    """The zone on the layers as they are now (not written): before and after, off and lit, in out."""
    os.makedirs(out, exist_ok=True)
    x0, y0, x1, y1 = BOX
    city = load(os.path.join(ROOT, 'assets', 'layer_city_off.webp')); unlit = load(os.path.join(ROOT, 'assets', 'street_unlit.webp'))
    kcomp = load(os.path.join(ROOT, 'assets', 'win_z7_kiosk.webp'))
    new, unew, vcomp, ocomp, kc, ch = build(city, unlit, BOX, kcomp)

    def lay(base, comps):
        a = base.copy()
        for c, (cx, cy) in comps:
            h, w = c.shape[:2]; al = c[..., 3:] / 255
            a[cy - y0:cy - y0 + h, cx - x0:cx - x0 + w] = a[cy - y0:cy - y0 + h, cx - x0:cx - x0 + w] * (1 - al) + c[..., :3] * al
        return a
    old = city[y0:y1, x0:x1, :3]
    vold = load(os.path.join(EDITS, 'soda_vending_before.webp'))
    views = {'before_off': old, 'after_off': new, 'after_unlit': unew,
             'before_lit': lay(old, [(vold, VEND[1:]), (kcomp, COMP_AT)]),
             'after_lit': lay(new, [(vcomp, VEND[1:]), (kc, COMP_AT)]),
             'after_stutter': lay(lay(new, [(vcomp, VEND[1:]), (kc, COMP_AT)]), [(ocomp, VOFF[1:3])])}
    for tag, a in views.items():
        for k in (1, 4):
            Image.fromarray(np.clip(np.round(a), 0, 255).astype(np.uint8)).resize(((x1 - x0) * k, (y1 - y0) * k), Image.NEAREST).save(os.path.join(out, f'{tag}_x{k}.png'))
    print('changed', int(ch.sum()), '| comps', int((vcomp[..., 3] > 0).sum()), int((ocomp[..., 3] > 0).sum()), int((kc[..., 3] > 0).sum()))


if __name__ == '__main__':
    if '--preview' in sys.argv: preview(sys.argv[sys.argv.index('--preview') + 1])
