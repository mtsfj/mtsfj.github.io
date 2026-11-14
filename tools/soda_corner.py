#!/usr/bin/env python3
"""The drinks corner on the left sidewalk: the tobacco kiosk, the three drinks machines set in its side, a small tiled
canopy over them, and what the old big lean-to hid (the owner: "à refaire : le haut-vent toit tuile au-dessus soda, les
soda, la caisse soda"; then "trop de contraste, pas assez de grain ; le haut-vent est juste trop grand, pentu, faut le
refaire entier"; the machines keep their perk from the zombies game).

    (a module: tools/redraw_zones.py's zone 'soda' calls draw() on the street as the zones before it leave it)
    python3 tools/soda_corner.py --preview DIR   (the zone from its before copies, off, lit and in the stutter, in DIR;
                                                  nothing in the repository changes)

All of it in the street's own camera (tools/relief.py's: VP (700, 615), f 959.5 px, the eye 1.41 m up, the sidewalk
0.15 m; X across, Y up, Z along the street: x = 700 + f X / Z, y = 615 - f (Y - 1.41) / Z): each pixel cast as 3 x 3
rays onto a few planes and the tiles' heightfield, the nearest thing each ray meets gives its colour, the nine averaged.
- The kiosk: its front face on in the plane Z 10.99 (x 229 to 280, as painted), its side wall toward the street at
  X -4.81 to Z 13.3, the machines set in it, its corner boards; its top now at 3.0 m (the old lean-to had it rise to a
  gable under a steep roof): a fascia board along its front and its side (a lit moulding at its foot), a slim coping
  over it (its lit edge, the drip's shadow under it).
- What the old lean-to hid (R24): Kirua's house's side wall behind the kiosk (X -5.43, the plane the old roof met on
  the ray v 0.434, to its downpipe at x 327), its weatherboards run on down from the painter's, one every 7.6 cm up
  the wall in the phase of his lowest ones, each board his own profile of light (a touch firmer), the wall's light
  his lowest boards', a little lower as it goes down, his grain over them; his downpipe on down the corner behind the
  kiosk; past the house's corner,
  the tree's leaves further in (tools/tree_a.py's way: its own drawing again, lower and to the left, in the shade).
- The canopy (hisashi): fixed to the kiosk's side wall over the machines, 52 cm out, its pitch 4 in 10, from the
  kiosk's front to just past the machines; its eave on a ray to the vanishing point; small pan tiles (16 cm along the
  street, three courses), seen at a grazing angle from the street; the eave tiles' round ends a row of small bumps
  whose rims catch the sky, a thin dark fascia, its near end's verge tiles and board; two wooden brackets under it (an
  arm, a strut down to the wall); under it the wall in its soft shadow, and its shadow's edge across the machines'
  headers. The water runs off at each pan (street.js DRIPS 'kiosk', written here).
- The machines (the comp z7_vending lights them; the layers hold them off, as the power cut and the stutter show them):
  ordinary drinks machines, two blue and a red one as the painter had them, their light and colour brought into his
  range (muted, soft at the edges, the displays' glow falling off on the bezels): the display windows recessed (the far
  jamb's inside, the tube under the lintel, three shelves of samples cast as cylinders, the nearer hiding the farther,
  lit from the front), price strips and buttons, a dark lower panel with a hint of its colour, the money plate (the
  amount in red, the slots, the lever, the change cup), the outlet, the plinth; on each header its perk's shield as the
  zombies game's icons draw it (assets/*_perk.webp; street.js PERKS, near to far): Speed Cola (green, a hand),
  Double Tap (brown-red, a burst and two rounds), Juggernog (red, the cross); PERKS' columns and BZ.soda written here
  from the machines' edges. z7_vendoff (the middle one out while its tube stutters): the street's own pixels where it
  lights itself.
- The kiosk's front: its enamel sign (the painter's glyphs, soft as he drew them), its service window as the owner chose
  it (B: a Showa tobacco window) drawn clean, lit in its comp (win_z7_kiosk), shut in the layers (darkened as the painter
  darkens a shut window), its two plates 塩 and 〒.
- Grain: everything drawn takes the painter's own (his plaster's fine structure in the alcove, as a ratio to its light),
  the lit things half of it.
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

# ---- the kiosk, Kirua's wall behind it, the canopy over the machines ----
ZN = 10.99                                     # the kiosk's front plane (and the canopy's near end)
XW = -4.81                                     # the kiosk's side wall, toward the street (the machines set in it)
XK0 = (229 - VP[0]) * ZN / F                   # the kiosk front's left edge
YKT = 3.0                                      # the kiosk's top (its cap): it no longer rises to the old roof
ZKE = 13.3                                     # the kiosk's far end, a little past the machines
XK = -5.43                                     # Kirua's house's side wall behind (the old roof met it on the ray v 0.434)
ZKC = F * XK / (327.5 - VP[0])                 # its far corner (its downpipe, x 326-329)
V_FLASH = 0.446                                # (over the old roof's flashing: above it, the painter's wall)
BOARD = 0.0759                                 # Kirua's weatherboards, one every this much up the wall (measured)
PIPE_X = (326, 330)                            # (his downpipe's columns, at the house's corner)
FASCIA_K = (2.83, 2.962)                       # the kiosk's fascia board under its coping (Y), its coping to YKT
# the canopy (hisashi): small, low-pitched, fixed to the kiosk's side wall over the machines, its eave on a ray
CY_TOP, CPITCH, CPROJ = 2.50, 0.40, 0.52       # its tiles' top at the wall, its pitch (rise over run), its reach
ZF = 13.12                                     # its far end, just past the machines
XT, YT = XW + 0.01, CY_TOP
XE, YE = XW + CPROJ, CY_TOP - CPITCH * CPROJ
L = np.hypot(XT - XE, YT - YE)
TU = np.array([XT - XE, YT - YE]) / L          # up the slope (X, Y)
NR = np.array([TU[1], -TU[0]])                 # its normal (up and out toward the street)
PITCH = 0.16                                   # a tile's width along the street (small tiles)
PAN0 = ZN - 0.26 * PITCH + 0.31 * PITCH        # (a roll at the near end)
COURSE = 0.15                                  # a course's exposed length up the slope (three courses)
DP, RR, BASE, STEP = 0.010, 0.022, 0.012, 0.016  # the pan's depth, the roll's height, the battens, a tile's thickness
PANW = 0.62                                    # the pan's share of a tile's width (the roll the rest)
LIP = (0.016, 0.031)                           # the eave tiles' front lip (height) and the round ends' radius (m)
FASCIA = 0.03                                  # the eave's board under the lip
SODE, BARGE = 0.012, 0.028                     # the verge tiles' flange, the board under it (m, down from the plane)
XLIP = XE + (BASE + STEP) * NR[0]              # the eave tiles' front (plumb)
HC = BASE + STEP + 0.1 * RR                    # the round ends' centres, over the plane
XM, ZM0, ZM1, YM = -4.785, 10.99, 13.07, 2.18  # the machines' front, their row's ends, their top
BRACKETS = (ZN + 0.09, ZF - 0.1)               # the canopy's two brackets (Z): an arm under it, a strut to the wall
CSHADE = 1.9                                   # its shadow's edge on the machines' fronts (Y): the sky shut out above

# the painter's colours (picked on his roof, his flashing, his far verge's lit edge, the kiosk's planks and the dark
# under the verge, in the street as it is)
TILE = [(0.00, (5, 6, 12)), (0.22, (9, 10, 19)), (0.40, (13, 13, 25)), (0.55, (18, 17, 32)), (0.70, (26, 22, 39)),
        (0.84, (38, 28, 47)), (1.00, (62, 38, 62))]
RIM = (118, 48, 70)                            # (his far verge's lit edge: the last roll's crest in the dusk)
WOOD = (25, 15, 28)                            # (his maroon along the verge)
WOOD_D = (12, 10, 21)
EDGE_LIT = (72, 64, 94)                        # (the lit edge of a roof in this light: the painter's flashing)
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


def cast_tiles(dx, dy, n=96):
    """Where each ray first meets the tiles (Z, or inf): marched through the tiles' slab, then bisected."""
    a = NR[0] * dx + NR[1] * dy; b = -NR[0] * XE + NR[1] * (EYE - YE)
    hmax, hmin = BASE + RR + STEP + 0.005, BASE - DP - 0.005
    with np.errstate(divide='ignore', invalid='ignore'):
        za, zb = (hmax - b) / a, (hmin - b) / a
    z0 = np.maximum(np.minimum(za, zb), ZN - 0.05); z1 = np.minimum(np.maximum(za, zb), ZF + 0.05)
    ok = z1 > z0
    z0 = np.where(ok, z0, ZN); z1 = np.where(ok, z1, ZN + 1e-3)
    hitz = np.full(dx.shape, np.inf); prev = z0.copy(); found = ~ok
    for i in range(n + 1):
        Z = z0 + (z1 - z0) * i / n
        hr, s = on_roof(dx, dy, Z)
        surf = np.where((Z >= ZN) & (Z <= ZF) & (s >= 0) & (s <= L) & (dx * Z <= XLIP), tile_h(Z, s), -9)
        new = ~found & (hr <= surf)
        lo, hi = prev.copy(), Z.copy()
        for _ in range(7):                                 # (bisect between the last miss and the hit)
            m = (lo + hi) / 2; hr_, s_ = on_roof(dx, dy, m)
            inside = (m >= ZN) & (m <= ZF) & (s_ >= 0) & (s_ <= L) & (dx * m <= XLIP)
            okk = inside & (hr_ <= np.where(inside, tile_h(m, s_), -9))
            hi = np.where(okk, m, hi); lo = np.where(okk, lo, m)
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
    t_pan = 0.46 - 0.12 * np.exp(-phi / 0.07) - 0.12 * np.exp(-(PANW - phi) / 0.06)
    t_roll = np.where(u < 0.5, 0.5 + 0.34 * (u / 0.5) ** 2, 0.84 - 0.7 * (u - 0.5))
    t = np.where(phi < PANW, t_pan, t_roll)
    t = np.where(fr < 0.06, t + 0.1, t)                          # (a course's lower edge catches the light)
    t = t * np.where(fr > 0.86, 0.6, 1.0) * np.where(fr > 0.78, 0.88, 1.0)   # (under the next course's butt: its shadow)
    t = np.where(riser, 0.16, t)
    ti = np.floor(col); ci = np.floor(cs)
    t = t * (0.88 + 0.22 * hsh(ti, ci))
    t = t + 0.16                                                  # (its tiles face the sky: lighter than the wall behind)
    near_top = np.clip((s - (L - 0.05)) / 0.05, 0, 1)            # (against the wall: its flashing's shadow)
    t = t * (1 - 0.4 * near_top)
    c = ramp(t, TILE)
    # the far verge: the last roll's crest catching the dusk (the painter's lit edge)
    rim = (ZF - Z < 0.035) & ~riser
    c = np.where(rim[..., None], np.array(RIM, float)[None, :] * np.where(fr > 0.86, 0.6, 1.0)[..., None], c)
    return c


def kirua_wall(C, box):
    """Kirua's side wall (X = XK) where the old roof hid it: its siding run on down to the kiosk's top, as the painter's
    boards above it: one every BOARD up the wall in the phase of his lowest ones, each board his own profile of light
    (its lit lower edge, its shadowed lap: as a ratio to the wall's light, read off his), the wall's light his lowest
    boards', a little lower as it goes down (the sky's fading), his grain laid on it afterwards (build); his downpipe on
    down the corner, its own pixels. C: the layer (whole scene, RGB floats). Returns the colour over box."""
    from scipy.ndimage import gaussian_filter
    x0, y0, x1, y1 = box; h, w = y1 - y0, x1 - x0
    lf = np.stack([gaussian_filter(C[..., c], 3.0) for c in range(3)], -1)
    Yof = lambda x, y: EYE + (VP[1] - (y + 0.5)) * (F * XK / (x + 0.5 - VP[0])) / F
    # his boards just over the flashing (rays v 0.447 to 0.50, left of the old window's frame): their phase and profile
    ref = [(x, y) for x in range(231, 296) for y in range(int(VP[1] - 0.50 * (VP[0] - x)), int(VP[1] - 0.447 * (VP[0] - x)))]
    Yr = np.array([Yof(x, y) for x, y in ref]); R = np.array([C[y, x] / (lf[y, x] + 1.0) for x, y in ref])
    best = None
    for y0p in np.linspace(0, BOARD, 24, endpoint=False):
        ph = ((Yr - y0p) / BOARD) % 1; b = np.minimum((ph * 8).astype(int), 7)
        prof = np.array([R[b == i].mean(0) if (b == i).any() else np.ones(3) for i in range(8)])
        var = (prof @ LUMA).var()
        if best is None or var > best[0]: best = (var, y0p, prof)
    _, Y0, prof = best
    prof = prof.mean(0) + (prof - prof.mean(0)) * 1.25          # (his boards' relief, a touch firmer: no flat wall)
    out = np.zeros((h, w, 3))
    for xi in range(w):
        x = x0 + xi
        yref = int(VP[1] - 0.452 * (VP[0] - x - 0.5))          # (his lowest clean boards' light, this column)
        top = lf[max(yref - 2, 0):yref + 1, x].mean(0)
        pipe = PIPE_X[0] <= x < PIPE_X[1]
        for yi in range(h):
            y = y0 + yi
            if y <= yref: out[yi, xi] = C[y, x]; continue
            fade = 0.8 + 0.2 * np.exp(-(y - yref) / 45.0)
            if pipe:                                           # (the downpipe: straight, its own pixels from above)
                out[yi, xi] = C[yref - 1 - (y - yref) % 9, x] * fade; continue
            ph = ((Yof(x, y) - Y0) / BOARD) % 1
            fi = ph * 8 - 0.5; i0 = int(np.floor(fi)) % 8; i1 = (i0 + 1) % 8; t = fi - np.floor(fi)
            r = prof[i0] * (1 - t) + prof[i1] * t
            out[yi, xi] = (top * fade + 1.0) * r - 1.0
    return out


def tree_fill(C, A, box, hole):
    """The tree behind where the old roof was: its own leaves further in (tools/tree_a.py's: the same drawing again,
    lower and to the left, in the crown's shade), darker toward the alley's foot. C, A: the layer's colour and alpha
    (whole scene); hole: the pixels to fill over box."""
    x0, y0, x1, y1 = box; h, w = y1 - y0, x1 - x0
    out = np.zeros((h, w, 3))
    ys, xs = np.nonzero(hole)
    for yi, xi in zip(ys, xs):
        x, y = x0 + xi, y0 + yi
        for n in range(1, 8):
            sx, sy = x + 26 * n, y - 40 * n
            inside = x0 <= sx < x1 and y0 <= sy < y1 and hole[sy - y0, sx - x0]
            if sy >= 0 and sx < C.shape[1] and A[sy, sx] >= 250 and not inside:
                break
        shade = 0.62 ** n * (1 - 0.35 * np.clip((y - 470) / 70.0, 0, 1))
        out[yi, xi] = C[sy, sx] * shade
    return out


def kiosk_top(Y):
    """The kiosk's top by height Y (an array): its coping (its lit edge, its face, the drip's shadow under it), its fascia
    board (a lit moulding along its foot); NaN below."""
    out = np.full(Y.shape + (3,), np.nan)
    f = (Y > FASCIA_K[0]) & (Y <= FASCIA_K[1])
    out[f] = (24, 20, 36)
    out[f & (Y < FASCIA_K[0] + 0.014)] = (40, 42, 70)
    out[f & (Y > FASCIA_K[1] - 0.013)] = (9, 10, 22)
    c = Y > FASCIA_K[1]
    out[c] = (28, 34, 60)
    out[c & (Y > YKT - 0.013)] = (62, 66, 100)
    return out


def old_roof(box):
    """The pixels the old roof, its verge, its eave and the old machines' beam covered (over box)."""
    x0, y0, x1, y1 = box
    X = np.arange(x0, x1)[None, :] + 0.5; Y = np.arange(y0, y1)[:, None] + 0.5
    v = (VP[1] - Y) / (VP[0] - X)
    m = (v < V_FLASH) & (v > 0.158) & (X >= 225)
    m &= ~((X > 325) & (Y < 452 + 1.278 * (X - 325) - 2))       # (right of its far verge: the tree, as painted)
    m &= ~((X > 352) & (v < 0.236))                             # (under its far eave: the alley's leaves, as painted)
    return m


def draw_upper(C, A, box):
    """The kiosk's top, its side wall, Kirua's wall behind, the tree, and the canopy over the machines, over box (C, A:
    the layer, whole scene). Returns the new colour over box, the coverage of what is rebuilt (0..1), and the classes'
    coverages (for the comps)."""
    x0, y0, x1, y1 = box; h, w = y1 - y0, x1 - x0
    dx, dy = rays(box)
    INF = np.inf
    zt = cast_tiles(dx, dy)
    # the eave: the tiles cut plumb at their ends (the eave tiles' front, a lip under the pans, each roll's round end),
    # the fascia board under them: toward the street
    zl = plane_x(dx, XLIP); yl = EYE + dy * zl
    hl = NR[0] * (XLIP - XE) + NR[1] * (yl - YE); sl = TU[0] * (XLIP - XE) + TU[1] * (yl - YE)
    col = (zl - (PAN0 - 0.31 * PITCH)) / PITCH; phi = col - np.floor(col)
    rc = (np.floor(col) + PANW + (1 - PANW) / 2) * PITCH + (PAN0 - 0.31 * PITCH)
    yc = YE + (XLIP - XE - HC * NR[0]) / TU[0] * TU[1] + HC * NR[1]
    rr = np.sqrt((zl - rc) ** 2 + (yl - yc) ** 2)
    manju = (rr < LIP[1]) & (zl >= ZN + 0.02)
    lip = ((sl >= 0) & (hl <= tile_h(zl, np.maximum(sl, 0)))) | ((yl <= yc) & (yl >= yc - LIP[0])) | manju
    lip &= (zl >= ZN - 0.004) & (zl <= ZF)
    xf = XLIP - 0.008; zf_ = plane_x(dx, xf); yf = EYE + dy * zf_
    fascia = (yf <= yc - LIP[0] + 0.006) & (yf >= yc - LIP[0] - FASCIA) & (zf_ >= ZN - 0.004) & (zf_ <= ZF)
    # its near end, toward us: the verge tiles' edge and the board under it
    zv = ZN - 0.004
    hv, sv = on_roof(dx, dy, zv)
    vtop = BASE + STEP * (1 - (sv / COURSE - np.floor(sv / COURSE))) + RR * 0.8
    sode = (hv <= vtop) & (hv >= -SODE) & (sv >= 0) & (sv <= L)
    barge = (hv < -SODE) & (hv >= -SODE - BARGE) & (sv >= -0.01) & (sv <= L)
    # the kiosk: its side wall (the machines in it), its front (as it is, under its cap), Kirua's wall behind it
    zw = plane_x(dx, XW); yw = EYE + dy * zw
    wall = (zw >= ZN) & (zw <= ZKE) & (yw >= GROUND) & (yw <= YKT)
    xn = dx * ZN; yn = EYE + dy * ZN
    front = (xn >= XK0) & (xn <= XW) & (yn >= GROUND) & (yn <= YKT)
    zk = plane_x(dx, XK); kir = zk <= F * XK / (330 - VP[0])
    ycb = lambda X: YT + (X - XT) * (YE - YT) / (XE - XT) - (BASE + 0.012)          # (the canopy's underside over X)
    brk = np.zeros(dx.shape, bool); zbk = np.full(dx.shape, np.inf); bedge = np.zeros(dx.shape, bool)
    for zb in BRACKETS:
        Xb, Yb = dx * zb, EYE + dy * zb
        on_arm = (Xb >= XW) & (Xb <= XE - 0.03) & (Yb <= ycb(Xb)) & (Yb >= ycb(Xb) - 0.045)
        xa_, ya_ = XW, ycb(XW) - 0.36; xb_, yb_ = XE - 0.06, ycb(XE - 0.06) - 0.03
        t_ = np.clip(((Xb - xa_) * (xb_ - xa_) + (Yb - ya_) * (yb_ - ya_)) / ((xb_ - xa_) ** 2 + (yb_ - ya_) ** 2), 0, 1)
        dd = np.hypot(Xb - (xa_ + t_ * (xb_ - xa_)), Yb - (ya_ + t_ * (yb_ - ya_)))
        on_st = (dd < 0.02) & (Xb >= XW)
        hitb = (on_arm | on_st) & (zb < zbk)
        bedge |= hitb & ((on_arm & (Yb > ycb(Xb) - 0.012)) | (on_st & (Yb - (ya_ + t_ * (yb_ - ya_)) > 0.008)))
        brk |= hitb; zbk = np.where(hitb, zb - 2e-3, zbk)
    cand = np.stack([np.where(zt < INF, zt, INF), np.where(lip, zl - 1e-4, INF), np.where(fascia, zf_, INF),
                     np.where(sode, zv, INF), np.where(barge, zv - 1e-4, INF), np.where(wall, zw, INF),
                     np.where(front, ZN, INF), np.where(kir, zk, INF), np.where(brk, zbk, INF)])
    k = np.argmin(cand, 0); k = np.where(np.isfinite(cand.min(0)), k, 9)   # (8: a bracket; 9: the tree, the alley)
    colr = np.zeros(dx.shape + (3,))
    m = k == 0
    if m.any(): colr[m] = shade_tiles(dx[m], dy[m], zt[m])
    m = k == 1                                                    # the tiles' ends: their lip lit along its top (the
    if m.any():                                                    # eave's thin edge), the round ends' rims too
        t = np.full(m.sum(), 0.30)
        dym = yl[m] - yc
        rim = manju[m] & (rr[m] > LIP[1] - 0.011)
        t = np.where(manju[m], 0.52 + 0.25 * np.clip(dym / LIP[1], 0, 1), t)
        t = np.where(rim & (dym < -0.008), 0.2, t)
        t = np.where(~manju[m] & (yl[m] < yc - LIP[0] + 0.008), 0.24, t)
        t = t * (0.92 + 0.14 * hsh(np.floor(col[m]), 99))
        cc = ramp(t, TILE)
        edge = rim & (dym > 0.0)                                                     # (its ends' rims lit by the sky: the
        cc[edge] = np.array(EDGE_LIT, float) * (0.9 + 0.12 * hsh(np.floor(col[m][edge]), 98))[:, None]   # painter's flashing's)
        colr[m] = cc
    m = k == 2                                                    # the fascia, in the eave's soft shade
    if m.any(): colr[m] = np.array(WOOD_D, float) * 1.15
    m = k == 3                                                    # the verge tiles' edge: lit along its top
    if m.any():
        top = hv[m] > vtop[m] - 0.01
        cc = ramp(np.full(m.sum(), 0.46) * (0.92 + 0.14 * hsh(np.floor(sv[m] / COURSE), 7)), TILE)
        cc[top] = np.array(EDGE_LIT, float) * 0.85
        colr[m] = cc
    m = k == 4                                                    # the board under it: wood, its lower edge lit
    if m.any():
        edge = hv[m] < -SODE - BARGE + 0.01
        colr[m] = np.where(edge[:, None], np.array(WOOD, float) * 1.2, np.array(WOOD, float) * 0.85)
    m = k == 5                                                    # the kiosk's side wall: its planks along the street, as
    if m.any():                                                    # its front's, a little darker; under the canopy its
        yy = yw[m]; pl = (yy - GROUND) / 0.105; fr = pl - np.floor(pl)   # soft shadow; its cap along the top
        base = np.where((fr < 0.16)[:, None], np.array(GROOVE, float), np.array(PLANK, float)) * 0.86
        ycb = YE - LIP[0] - FASCIA                                 # (the canopy's lower edge)
        under = (yy < CY_TOP) & (yy > YM)
        sh = np.where(under, 0.62 + 0.38 * np.clip((ycb - yy) / 0.3, 0, 1) ** 0.7, 1.0)
        sh = np.where(yy < YM, 0.7, sh)                            # (past the machines, beside them: in their shade)
        top = kiosk_top(yy)
        base = np.where(np.isnan(top[:, :1]), base, top)
        zz = zw[m]
        base = np.where(((zz < ZN + 0.045) & (yy > YM))[:, None], np.array((34, 46, 82), float), base)   # (its corner boards:
        base = np.where((zz > ZKE - 0.04)[:, None], np.array((14, 18, 36), float), base)         # the near one lit)
        colr[m] = base * np.where(np.isnan(top[:, 0]), sh, 1.0)[:, None]
    m = k == 6                                                    # the kiosk's front: its fascia and coping; under them,
    cap_f = m & (yn > FASCIA_K[0])                               # as it is
    if cap_f.any():
        colr[cap_f] = kiosk_top(yn[cap_f]) * 1.06
    m = k == 8                                                    # the canopy's brackets: dark wood, a lit upper edge
    if m.any():
        colr[m] = np.where(bedge[m][:, None], np.array((34, 32, 52), float), np.array((16, 13, 26), float))
    # per pixel: each class's share of the rays
    share = lambda mm: mm.mean(-1)
    canopy = share(k <= 4); side = share(k == 5); capc = share(cap_f | ((k == 5) & (yw > YKT - 0.045)))
    keepf = share((k == 6) & ~cap_f); kirc = share(k == 7); back = share(k == 9)
    dm = (k <= 5) | cap_f | (k == 8)
    drawn = share(dm)
    dsum = np.maximum(dm.sum(-1), 1)[..., None]
    dcol = (colr * dm[..., None]).sum(-2) / dsum
    old = old_roof(box)
    kw = kirua_wall(C, box)
    hole = (back > 0) & old
    tf = tree_fill(C, A, box, hole)
    cur = C[y0:y1, x0:x1].copy()
    # the composition: what is drawn; Kirua's wall and the tree where the old roof was (else the painter's); the kiosk's
    # front under its cap as it is
    kir_t = np.where(old, kirc, 0); back_t = np.where(old, back, 0)
    rest = 1 - drawn - kir_t - back_t
    new = dcol * drawn[..., None] + kw * kir_t[..., None] + tf * back_t[..., None] + cur * rest[..., None]
    rebuilt = drawn + kir_t + back_t
    if os.environ.get('SODA_DEBUG'):
        pal = np.array([(200, 60, 60), (60, 200, 60), (60, 60, 220), (220, 200, 40), (200, 40, 200), (40, 200, 200),
                        (120, 120, 120), (230, 150, 150), (250, 250, 250), (20, 90, 20)])
        Image.fromarray(pal[k[..., SS * SS // 2]].astype(np.uint8)).resize((w * 5, h * 5), Image.NEAREST).save(os.environ['SODA_DEBUG'])
    return new, rebuilt, dict(canopy=canopy, side=side, drawn=drawn, kirua=kir_t)


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
HEADER = [((13, 20, 40), (28, 40, 70)), ((13, 20, 40), (34, 40, 66)), ((26, 16, 30), (52, 26, 40))]
# each machine's perk on its header (the zombies game's machines, street.js PERKS: near to far Speed Cola, Double Tap,
# Juggernog), its shield as the game's icons draw it: the field, the rim, the symbol (lit; off, the same in the dark)
PERK = [dict(field=(44, 80, 40), rim=(108, 114, 88), sym=(150, 160, 136)),   # Speed Cola: a white hand, its speed
        dict(field=(74, 30, 22), rim=(112, 92, 70), sym=(176, 128, 52), sym2=(152, 142, 122)),   # Double Tap: a burst, two rounds
        dict(field=(82, 28, 24), rim=(108, 80, 66), sym=(164, 154, 138))]   # Juggernog: the cross
ADC = [((12, 22, 30), (20, 38, 36)), ((14, 20, 36), (36, 32, 34)), ((28, 16, 28), (46, 22, 32))]
BACK = ((22, 24, 48), (164, 182, 198))
BACK_LO = ((20, 22, 44), (122, 144, 168))
JAMB = ((32, 36, 66), (118, 140, 164))
SHELF = ((36, 42, 72), (128, 152, 174))
TUBE = ((40, 44, 74), (196, 208, 218))
PRICE = ((16, 20, 44), (40, 62, 104))
LABEL = ((30, 34, 58), (156, 168, 184))
LED = ((24, 30, 56), (96, 156, 196))
SOLD = ((36, 24, 40), (176, 84, 94))
METAL = ((26, 34, 62), (40, 52, 86))
SLOT = ((4, 6, 14), (4, 6, 14))
DIGIT = ((26, 14, 22), (196, 84, 60))
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
    # the perk's shield on the header: its field, its rim, its symbol (in the shield's own coordinates s, t)
    S_ = (u - 0.20) / 0.30; T_ = (2.115 - yf) / 0.23
    half = np.where(T_ < 0.62, 0.5, 0.5 * (1 - (T_ - 0.62) / 0.38))
    shield = hd & (T_ >= 0) & (T_ <= 1) & (np.abs(S_ - 0.5) <= half)
    rimm = shield & ((np.abs(S_ - 0.5) > half - 0.11) | (T_ < 0.08))
    for i, P in enumerate(PERK):
        sh_i = shield & (mi == i)
        if not sh_i.any(): continue
        dk = lambda c: tuple(np.array(c, float) * 0.16 + np.array((10, 12, 24), float))
        put(sh_i, (dk(P['field']), P['field']))
        put(rimm & (mi == i), (dk(P['rim']), P['rim']))
        s_, t_ = S_, T_
        if i == 0:                                           # Speed Cola: a hand, its fingers streaming back
            sym = (((s_ - 0.62) / 0.2) ** 2 + ((t_ - 0.56) / 0.17) ** 2 < 1) | \
                  ((s_ < 0.62) & (t_ < 0.62) & (s_ + t_ > 0.62) & ((((s_ - t_) * 3.4) % 1) < 0.5))
            put(sh_i & ~rimm & sym, (dk(P['sym']), P['sym']))
        elif i == 1:                                         # Double Tap: a burst, two rounds across it
            th = np.arctan2(t_ - 0.36, s_ - 0.46); rr_ = np.hypot(s_ - 0.46, t_ - 0.36)
            put(sh_i & ~rimm & (rr_ < 0.12 + 0.09 * np.abs(np.cos(4 * th))), (dk(P['sym']), P['sym']))
            rounds = ((np.abs(s_ + t_ - 1.02) < 0.055) | (np.abs(s_ + t_ - 1.24) < 0.055)) & (s_ > 0.22) & (s_ < 0.86)
            put(sh_i & ~rimm & rounds, (dk(P['sym2']), P['sym2']))
        else:                                                # Juggernog: the cross
            cross = ((np.abs(s_ - 0.5) < 0.11) & (t_ > 0.13) & (t_ < 0.8)) | ((np.abs(t_ - 0.41) < 0.1) & (s_ > 0.19) & (s_ < 0.81))
            put(sh_i & ~rimm & cross, (dk(P['sym']), P['sym']))
    ad = on & (u > AD[0]) & (u < AD[1]) & (yf > AD[2]) & (yf < AD[3])
    for i in range(3):                                               # (the lower panel: dark, a hint of its colour, a
        mm = ad & (mi == i)                                          # little light at its top)
        put(mm, ADC[i], (0.85 + 0.25 * np.clip((yf[mm] - AD[2]) / (AD[3] - AD[2]), 0, 1) ** 2)[:, None])
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
        cl = cl * 0.72 + 0.28 * np.array(BACK_LO[1], float)              # (muted, in the display's light)
        LIT[m] = np.clip(cl * lit_k[:, None] * 0.92, 0, 255)
        OFF[m] = cl * 0.08 + np.array((18, 20, 40), float)
    m = win & (kk == 5)
    if m.any():
        t = np.clip((wy[m] - ya) / (yb - ya), 0, 1)
        fr_ = ((wy[m] - ya) / ROW) % 1
        OFF[m] = np.array(BACK[0], float)
        LIT[m] = (np.array(BACK_LO[1], float) * (1 - t[:, None]) + np.array(BACK[1], float) * t[:, None]) * (0.86 + 0.14 * fr_[:, None])
    # the roof's shadow on them (the sky shut out under the eave): darker toward their top, off and lit alike on the
    # body (the displays and the lit panels have their own light)
    occ = (1 - 0.18 * np.clip((yf - 1.3) / (YM - 1.3), 0, 1)) * (1 - 0.45 * np.clip((yf - CSHADE + 0.02) / 0.05, 0, 1))
    OFF *= occ[..., None]
    selflit = win | hd | ad | dig
    LIT = np.where(selflit[..., None], np.where((hd & ~shield)[..., None], LIT * (0.4 + 0.6 * occ)[..., None], LIT), LIT * occ[..., None])
    # the displays' light on the bezel and the body round them (lit only): a cold glow falling off
    dwin = np.maximum(np.maximum(ua - u, u - ub), np.maximum(ya - yf, yf - yb))
    glow = np.clip(1 - dwin / 0.22, 0, 1) ** 2 * on * ~win
    LIT = LIT + glow[..., None] * np.array((22, 30, 38), float)
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
WALL_L = ((150, 86, 50), (104, 56, 38))        # its left wall, top and bottom (the painter's orange)
JAMB_K = (74, 50, 44)
BACKW = ((100, 66, 46), (74, 48, 38))          # the back wall behind the shelves, top and bottom
SHELF_K = (164, 120, 78)
STILE = (58, 36, 30)
CASE_IN = ((168, 128, 82), (126, 88, 56))    # inside the showcase, top and bottom (lit from inside)
CASE_TOP = (180, 148, 104)
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
                c = np.array(PACKS[int(hsh(sy, k, q, 3) * len(PACKS))], float) * 0.4 + 0.3 * np.array(BACKW[0], float)
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
            c = np.array(PACKS[int(hsh(r, k, 7) * len(PACKS))], float) * 0.55 + 0.45 * np.array(CASE_IN[0], float)
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
            (PLATES[0], (20, 28, 60), (64, 64, 70), SHIO, (92, 92, 96)),
            (PLATES[1], (56, 56, 62), (64, 64, 70), YUBIN, (88, 26, 36))):
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


GRAIN_SRC = (356, 575, 388, 650)               # the alcove's plaster under its lamp: the painter's grain, no shapes in it
GRAIN_K = 1.45                                 # (brought to his planks' and his old machines' strength, about 0.13)


def grain_field(O, box):
    """The painter's own grain over box: the relative fine structure of his plaster in the alcove (its luminance over
    its own pixel-wide blur), mirror-tiled; O: the zone's pixels as handed over (RGB floats over box)."""
    from scipy.ndimage import gaussian_filter
    x0, y0, x1, y1 = box; gx0, gy0, gx1, gy1 = GRAIN_SRC
    P = O[gy0 - y0:gy1 - y0, gx0 - x0:gx1 - x0] @ LUMA
    lp = gaussian_filter(P, 1.0); rel = (P - lp) / (lp + 4.0); rel = rel - rel.mean()
    T = np.concatenate([rel, rel[:, ::-1]], 1); T = np.concatenate([T, T[::-1]], 0)
    yy = np.arange(y1 - y0)[:, None] % T.shape[0]; xx = (np.arange(x1 - x0)[None, :] + 7) % T.shape[1]
    return np.clip(T[yy, xx] * GRAIN_K, -0.25, 0.25)


def build(city, unlit, box, kcomp):
    """Everything over box from the layers as the zones before leave them (whole-scene RGBA floats, not changed):
    the new street and power cut over box, the three comps (RGBA floats), the mask of what changed."""
    x0, y0, x1, y1 = box
    O = city[y0:y1, x0:x1, :3].copy(); U = unlit[y0:y1, x0:x1, :3].copy()
    from scipy.ndimage import gaussian_filter
    new, rebuilt, cls = draw_upper(city[..., :3], city[..., 3], box)
    klit, kch = kiosk_front(new, box)
    rcov = cls['side']
    moff, mlit, mcov, mid, own = machines(box)
    # their edges a little soft, as the painter's (a pixel's worth), then everything drawn takes his grain
    wb = gaussian_filter(mcov, 0.75) + 1e-6
    soft = lambda a: 0.7 * a + 0.3 * np.stack([gaussian_filter(a[..., c] * mcov, 0.75) for c in range(3)], -1) / wb[..., None]
    moff, mlit = soft(moff), soft(mlit)
    G = grain_field(O, box)
    wsurf = np.clip(cls['drawn'] + cls['kirua'] + kch, 0, 1)
    new = new * (1 + G * wsurf)[..., None]
    Gm = np.where(own, 0.5 * G, G)                         # (what lights itself: half of it, as a lit pane shows it)
    moff = moff * (1 + G)[..., None]; mlit = mlit * (1 + Gm)[..., None]
    gx0, gy0, gx1, gy1 = GLASS
    klit = klit * (1 + G[gy0 - y0:gy1 - y0 + 1, gx0 - x0:gx1 - x0 + 1])[..., None]
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
    kc[gy0 - cy:gy1 - cy + 1, gx0 - cx:gx1 - cx + 1, :3] = klit
    kc[gy0 - cy:gy1 - cy + 1, gx0 - cx:gx1 - cx + 1, 3] = 255
    # the power cut: the same, times the painter's own darkening there (unlit over lit, smoothed, channel by channel)
    from scipy.ndimage import gaussian_filter
    dark = np.stack([(gaussian_filter(U[..., c], 4.0) + 1.0) / (gaussian_filter(O[..., c], 4.0) + 1.0) for c in range(3)], -1)
    changed = np.abs(np.round(new) - np.round(O)).max(-1) > 0
    unew = U.copy(); unew[changed] = np.clip(new * np.clip(dark, 0, 1.5), 0, 255)[changed]
    return np.clip(new, 0, 255), unew, vcomp, ocomp, kc, changed


def street_js():
    """What street.js keeps of this corner, from its geometry: the drips off the canopy's eave (DRIPS 'kiosk': a trickle
    at each pan's lip, falling to the sidewalk under it; 'shoe': none, Kirua's downpipe now runs on down behind the
    kiosk), the machines' columns for the zombies game's Perk-a-Cola (PERKS x0, x1; BZ.soda: where a click buys).
    Rewritten each run, the same bytes."""
    import json, re
    path = os.path.join(ROOT, 'assets', 'street.js')
    s = open(path, encoding='utf-8').read()
    m = re.search(r'  const DRIPS = (\[.*?\]);   // per eave', s)
    D = json.loads(m.group(1))
    yc = YE + (XLIP - XE - HC * NR[0]) / TU[0] * TU[1] + HC * NR[1]
    ylb = yc - LIP[0]                                          # (the lip's lower edge: where a drop hangs)
    st = []
    k = 1
    while PAN0 + k * PITCH < ZF - 0.04:
        Z = PAN0 + k * PITCH
        x = int(np.floor(VP[0] + F * XLIP / Z)); y = int(np.floor(VP[1] - F * (ylb - EYE) / Z))
        land = round(VP[1] + F * (EYE - GROUND) / Z, 2)
        rate = 20.0 if k == 1 else round(7.0 + 7.0 * float(hsh(k, 41)), 2)
        st.append([x, y, land, round(9626.0 / Z, 1), round(9.225 / Z, 3), 0.0, rate, int(round(84.0 / Z)), int(round(36.0 / Z))])
        k += 1
    for E in D:
        if E['n'] == 'kiosk':
            E['st'] = st; E['px'] = int(round(np.mean([q[0] for q in st]))); E['py'] = int(round(np.mean([q[1] for q in st])))
        if E['n'] == 'shoe':
            E['st'] = []; E['bu'] = []
    s = s[:m.start(1)] + json.dumps(D, separators=(',', ':'), ensure_ascii=False) + s[m.end(1):]
    edges = [int(round(VP[0] + F * XM / (ZM0 + i * WM))) for i in range(4)]
    for name, (a, b) in zip(('speed', 'tap', 'jugg'), zip(edges[:-1], edges[1:])):
        s, n = re.subn(r'(\b%s: \{ x0: )\d+(, x1: )\d+' % name, r'\g<1>%d\g<2>%d' % (a, b), s)
        assert n == 1, name
    s, n = re.subn(r'"soda":\[\d+,(\d+),\d+,(\d+)\]', r'"soda":[%d,\1,%d,\2]' % (edges[0], edges[-1]), s)
    assert n == 1, 'BZ.soda'
    if s != open(path, encoding='utf-8').read():
        open(path, 'w', encoding='utf-8').write(s)
    return st, edges


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
    city[y0:y1, x0:x1, :3] = new; city[y0:y1, x0:x1, 3] = np.where(ch, 255, city[y0:y1, x0:x1, 3])
    unlit[y0:y1, x0:x1, :3] = unew; unlit[y0:y1, x0:x1, 3] = np.where(ch, 255, unlit[y0:y1, x0:x1, 3])
    save(vcomp, os.path.join(RET, 'vend_z7_vending.webp'))
    save(ocomp, os.path.join(RET, 'vend_z7_vendoff.webp'))
    if hasattr(rz, 'COMP_OUT'): rz.COMP_OUT['soda'] = ['win_z7_kiosk', kc, None]
    street_js()
    return ch


def preview(out):
    """The zone on the layers as they are now (not written): before and after, off and lit, in out."""
    os.makedirs(out, exist_ok=True)
    x0, y0, x1, y1 = BOX
    city = load(os.path.join(ROOT, 'assets', 'layer_city_off.webp')); unlit = load(os.path.join(ROOT, 'assets', 'street_unlit.webp'))
    city[y0:y1, x0:x1] = load(os.path.join(EDITS, 'soda_before_city.webp'))      # (the zone as the pipeline hands it over,
    unlit[y0:y1, x0:x1] = load(os.path.join(EDITS, 'soda_before_unlit.webp'))    # but for the kiosk zones' own change)
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
