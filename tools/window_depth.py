#!/usr/bin/env python3
"""The windows of the two buildings round the right pole given their depth: the plaster block behind the pole (zone5's
B: its balcony door, Red's, and the window under it) and the narrow planked building between the pole and Ichiraku
(zone5's C: its tall lit window and its top storey's window). The owner, circling them in the whole street: "refaire les
fenêtres de ce bâtiment-là : dessinées, 0 volume, moche"; then (R28) what is detailed generated, then pixelated.

    (a module: tools/redraw_zones.py's zones winB and winC call b_windows() and c_window() (the method 'hand') on the
     street as the zones before them leave it; each gives back its window's lit comp, win_z1_top or win_z1_warm (written
     last by redraw_zones.py), and writes the glass street.js draws that window's visitor in: z1_top_glaze.webp (Red at
     the balcony door), z1_warm_mask.webp (the shadow crossing the curtain))
    python3 tools/window_depth.py --preview OUT    the street as it was before these windows (git BEFORE), both zones
                                                   drawn (nothing written in assets/): crops off, lit, in the power cut
    python3 tools/window_depth.py --ask NAME       a draft from the image model (tools/redraw_zones.py's call(): about
                                                   0.14 $; OPENROUTER_API_KEY): NAME a key of DRAFTS, NAME:K an option

What was there: each window a flat picture on its wall (the painter's; zone5's keep boxes): the lit curtains out to the
wall's edge, a strip of light for a reveal, a dark line for a frame, the railing a row of bars drawn on the wall's own
plane across the bottom of the opening, no sill: stickers on the plaster.
What it is. Its geometry (simple: R28 leaves it to a model) a small model in the street's camera (tools/zone5_facades.py's:
the facades 5 m right of the street's axis, f 959.5 px, VP (700, 615); a point X m right of the axis, Y m over the eye,
Z m ahead is seen at x = 700 + f X / Z, y = 615 - f Y / Z: a line along the street keeps v = Y / X, one across it is
level), each pixel followed by 4 x 4 rays into axis-aligned boxes, each ray's first face named and shaded:
- the opening cut into the wall, the glass set back (DEPTH): the jamb on the far side (toward the vanishing point, the
  one the street sees: R23) a face-on band, the head's soffit over the glass; the near jamb and the recess's floor
  hidden, as they are from below;
- the frame (aluminium) in the recess, its sashes (two sliding ones meeting half way across the frame; one on C's tall
  window), their glass;
- B's balconies: a slab (PROJ out, SLAB thick) under each opening, a steel railing on it set in from its edge (a handrail,
  a bottom rail, flat bars every BAR m along the street, foreshortened toward the vanishing point, a post at each front
  corner, the two short returns to the wall level and face on); C's sills, metal; the slabs, the railings and the sills
  shade the wall round them (the sky's light, from above and the street's side, cast through the model).
What is in it (the reveals and soffits lit by the rooms, the frames, the curtains, the ceiling lamp's glow, the room, the
night's sheen on dark glass, the slabs' lit edges, the railings) drawn by the image model (DRAFTS: the street lit, these
windows in the model's geometry, asked as real windows set in a wall seen from below at night; its answers kept in
tools/src/edits/<name>_model.webp, never asked again by a run): boxed down to the street's pixels, darkened back,
registered on the walls round them; laid in by the model's outline (each pixel's share of rays that are not wall), the
walls the painter's (his plaster and planks, darkened only where the model's shadows fall; where his flat window or
railing was and the wall now shows, the plaster run on from round it: its light from about it, its grain from beside);
its colours its own (within a few levels of the painter's) given his tint window by window (a gain per channel, glass and
the rest apart, on the model's picture of the same pixels: his reveals, frames, hoods' tones, his curtains column by
column) and snapped to his palette there (a median cut of his pixels round the window and of his old lit window). Its
light by state is the model's: the draft is the lit window; off (layer_city_off) and in the power cut (street_unlit) it
is the same picture times the model's own change there (the room dimmed as the painter dims his, channel by channel,
under the night's reflection; then out: the reflection alone; the frames, slabs and railings unchanged). A room never
lit (B's lower window, C's top one) is fitted on its off picture.
The hoods over B's windows, the lamp's arm and bracket (tools/pole_lamp.py's: never drawn over), the pole, the ramen
shop's side sign (laid back over C's sill) and C's roof (topC) stay as they are.
Sources: tools/src/edits/win_z1_top_before.webp and win_z1_warm_before.webp (the painter's lit comps: his curtains, his
palette), wdBC_* and wdCU_* (the drafts: input, prompt, answer).
Needs Pillow, numpy, scipy.
"""
import os
import sys
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
ASSETS = os.path.join(ROOT, 'assets')
EDITS = os.path.join(ROOT, 'tools', 'src', 'edits')
H, W = 816, 1456
VPX, VPY, F = 700.0, 615.0, 959.5
XS = 5.0                                       # the facades' distance from the street's axis (m)
SS = 4                                         # rays a pixel each way

# the openings on the wall's face: their columns (continuous: the far edge's left side, the near edge's) and rays
B_TOP = dict(xl=964.0, xr=1004.0, vt=1.283, vb=0.942, sashes=2, draft='wdBC')   # Red's balcony door (zone5: R(964, 1003, 0.942, 1.283))
B_LOW = dict(xl=964.0, xr=1004.0, vt=0.803, vb=0.467, sashes=2, dark=True, draft='wdBC')   # the window under it (R(964, 1003, 0.467, 0.801))
C_WIN = dict(xl=1081.0, xr=1109.0, vt=0.797, vb=0.4995, sashes=1, draft='wdBC')  # C's tall window (zone5: R(1081, 1108, 0.494, 0.797))
C_TOP = dict(xl=1080.0, xr=1109.0, vt=1.199, vb=0.962, sashes=2, dark=True, draft='wdCU')   # C's top storey's (R(1080, 1108, 0.962, 1.199))
DEPTH = dict(B=0.10, C=0.07)                   # the glass set back (m): the reveal
FRAME = dict(d=0.07, w=0.035)                  # the frame: its depth, its members' width (m)
SASH = dict(d=0.03, w=0.035, rail=0.045)       # a sash: its depth, its stiles' width, its rails' height
PROJ, SLAB, OVER = 0.16, 0.10, 0.12            # B's balconies: the slab's projection, its thickness, past the opening
RAIL = dict(h=0.56, inset=0.025, top=0.035, topd=0.035, bot=(0.06, 0.085), bar=(0.012, 0.022), post=0.03)
BAR = 0.18                                     # a flat bar every BAR m along the street
SILL = dict(p=0.05, t=0.035, over=0.04)        # C's metal sill
C_SIGN = [(1109.5, 413), (1112, 405), (1116, 400), (1123, 396), (1123, 463), (1109.5, 463)]   # ramen's side sign

B_BOX = (944, 205, 1021, 526)                  # the zone winB (redraw_zones.py)
C_BOX = (1074, 112, 1112, 440)                 # the zone winC (not below 440: the hall's entrance)
B_COMP = (963, 222, 43, 141)                   # win_z1_top's box (street.js ASSETS, and the glass Red is drawn in)
C_COMP = (1081, 288, 30, 138)                  # win_z1_warm's (and the curtain the shadow crosses)

# the painter's tones (the street with its lights off), sampled round these windows: his hoods' undersides, lit edges
# and faces, his reveals and frames
TONE = {k: np.array(v, float) for k, v in dict(
    soffit=(5, 9, 16), soffit_arris=(22, 26, 46),
    frame=(9, 11, 19), frame_side=(30, 32, 50), frame_under=(5, 7, 13),
    slab=(34, 37, 72), slab_arris=(56, 48, 84), slab_low=(17, 20, 38), slab_end=(20, 24, 44), slab_under=(3, 8, 12),
    rail=(9, 11, 20), rail_hand=(22, 24, 44), rail_top=(62, 58, 96), rail_side=(12, 14, 25), rail_under=(5, 7, 12),
    sill=(26, 28, 44), sill_arris=(58, 54, 84), sill_low=(10, 12, 22), sill_end=(16, 18, 30), sill_under=(3, 6, 11),
).items()}
JAMB_K = dict(B=(0.55, 0.72, 0.58), C=(0.80, 0.85, 0.80))   # the jamb in the wall's shade (B: his reveal under the low window)
FRAME_K = dict(B=1.0, C=0.6)                   # (C's frame on its darker planks)
REVEAL_LIT = np.array((118.0, 70.0, 90.0))     # his lit reveals (B 110..131, C 101..116: brighter by the glass)
SOFFIT_LIT = np.array((66.0, 39.0, 52.0))      # his lit soffit (C's head)
FRAME_LIT = np.array((26.0, 18.0, 27.0))       # his frames against the lit room
OFF_K = np.array((0.405, 0.37, 0.44))          # his room off over lit (B 0.41, 0.36, 0.45 and 0.37, 0.42, 0.44; C 0.40, 0.37, 0.45)
REFL = dict(B=((40.0, 42.0, 82.0), (20.0, 23.0, 47.0)), C=((30.0, 32.0, 62.0), (13.0, 16.0, 32.0)))   # the night in the glass
# his light down the curtains (the share at heights w: 0 the sill, 1 the head), relative to where his columns are read
YS_B = ([0.0, 0.42, 0.65, 0.96, 1.0], [0.68, 0.85, 0.97, 1.04, 1.05])
YS_C = ([0.0, 0.22, 0.475, 0.73, 0.94, 1.0], [0.75, 0.875, 1.0, 1.106, 1.135, 1.14])


# ------------------------------------------------------------------------------------------------- the camera, the model
def z_wall(x, X=XS):
    """The depth (m) of the wall's point seen at column x (continuous)."""
    return F * X / (x - VPX)


def rays(box):
    """SS x SS rays in each pixel of box: their directions (dx, dy, 1), shapes (h, w, SS * SS)."""
    x0, y0, x1, y1 = box; h, w = y1 - y0, x1 - x0
    o = (np.arange(SS) + 0.5) / SS
    xs = np.arange(x0, x1)[None, :, None, None] + o[None, None, None, :] + np.zeros((h, 1, SS, 1))
    ys = np.arange(y0, y1)[:, None, None, None] + o[None, None, :, None] + np.zeros((1, w, 1, SS))
    return (xs.reshape(h, w, SS * SS) - VPX) / F, (VPY - ys.reshape(h, w, SS * SS)) / F


class Scene:
    """Axis-aligned boxes (X0, X1, Y0, Y1, Z0, Z1), each a part of the model (its name)."""
    def __init__(self):
        self.b, self.name = [], []

    def add(self, name, X0, X1, Y0, Y1, Z0, Z1):
        self.b.append((min(X0, X1), max(X0, X1), min(Y0, Y1), max(Y0, Y1), min(Z0, Z1), max(Z0, Z1)))
        self.name.append(name)

    def cast(self, dx, dy):
        """The first box each ray (from the eye, going up: dy > 0) meets: its index (-1: none), the depth Z there, the
        face it enters by (0: the one facing the street, -X; 1: facing down, -Y; 2: facing us, -Z)."""
        t = np.full(dx.shape, np.inf); idx = np.full(dx.shape, -1); face = np.zeros(dx.shape, int)
        for i, (X0, X1, Y0, Y1, Z0, Z1) in enumerate(self.b):
            tx0, tx1, ty0, ty1 = X0 / dx, X1 / dx, Y0 / dy, Y1 / dy
            tn = np.maximum(np.maximum(tx0, ty0), Z0); tf = np.minimum(np.minimum(tx1, ty1), Z1)
            ok = (tn < tf) & (tn > 0) & (tn < t)
            f = np.where(tn == tx0, 0, np.where(tn == ty0, 1, 2))
            t = np.where(ok, tn, t); idx = np.where(ok, i, idx); face = np.where(ok, f, face)
        return idx, t, face

    def blocked(self, P, L, names):
        """Whether the ray from each point P (n, 3) toward L meets a box of the given parts."""
        out = np.zeros(len(P), bool)
        for i, bx in enumerate(self.b):
            if self.name[i] not in names: continue
            tn = np.full(len(P), 1e-4); tf = np.full(len(P), np.inf)
            for a in range(3):
                lo, hi = bx[2 * a], bx[2 * a + 1]
                if abs(L[a]) < 1e-9:
                    tf = np.where((P[:, a] >= lo) & (P[:, a] <= hi), tf, -1.0); continue
                t0, t1 = (lo - P[:, a]) / L[a], (hi - P[:, a]) / L[a]
                tn = np.maximum(tn, np.minimum(t0, t1)); tf = np.minimum(tf, np.maximum(t0, t1))
            out |= tn < tf
        return out


def opening(o, d):
    """An opening in the model (m): its far and near depths, its sill and head heights on the wall, the glass's set
    back, its sashes (two sliding ones meet half way across the frame)."""
    zf, zn = z_wall(o['xl']), z_wall(o['xr'])
    return dict(zf=zf, zn=zn, yb=o['vb'] * XS, yt=o['vt'] * XS, d=d, n=o['sashes'], zm=0.5 * (zf + zn), dark=o.get('dark', False),
                draft=o['draft'])


def add_wall(S, ops, zr, yr):
    """The wall (from X 5 m, 0.6 m thick) over the depths zr and heights yr, the openings cut out of it."""
    zs = sorted({zr[0], zr[1]} | {o[k] for o in ops for k in ('zn', 'zf')})
    ys = sorted({yr[0], yr[1]} | {o[k] for o in ops for k in ('yb', 'yt')})
    for za, zb in zip(zs[:-1], zs[1:]):
        for ya, yb in zip(ys[:-1], ys[1:]):
            zc, yc = 0.5 * (za + zb), 0.5 * (ya + yb)
            if not any(o['zn'] < zc < o['zf'] and o['yb'] < yc < o['yt'] for o in ops):
                S.add('wall', XS, XS + 0.6, ya, yb, za, zb)


def add_window(S, o, tag, G):
    """The frame and its sashes in an opening (two sliding ones, the near one on the outer track; or one), their glass
    (G: each pane's opening and the depths of its visible edges, far and near)."""
    X0 = XS + o['d']; fd, fw = FRAME['d'], FRAME['w']; sd, sw, sr = SASH['d'], SASH['w'], SASH['rail']
    zf, zn, yb, yt, zm = o['zf'], o['zn'], o['yb'], o['yt'], o['zm']
    S.add('frame', X0, X0 + fd, yb, yt, zf - fw, zf)                       # its far member
    S.add('frame', X0, X0 + fd, yt - fw, yt, zn - 0.4, zf)                 # its head (on behind the near jamb)
    S.add('frame', X0, X0 + fd, yb, yb + fw, zn - 0.4, zf)                 # its sill
    zi, yh, yl = zf - fw, yt - fw, yb + fw
    zn_ = zn + fw                                                          # (the near member's inner edge, behind the wall)
    sashes = ((zm - sw, zi, X0 + 0.038), (zn_, zm + sw, X0 + 0.004)) if o['n'] == 2 else ((zn_, zi, X0 + 0.02),)
    for k, (za, zb, xa) in enumerate(sashes):                              # far, near
        S.add('sash', xa, xa + sd, yl, yh, zb - sw, zb)                    # its far stile
        S.add('sash', xa, xa + sd, yl, yh, za, za + sw)                    # its near stile
        S.add('sash', xa, xa + sd, yh - sr, yh, za, zb)                    # its top rail
        S.add('sash', xa, xa + sd, yl, yl + sr, za, zb)                    # its bottom rail
        xg = xa + 0.5 * sd
        S.add(f'glass{tag}{k}', xg, xg + 0.004, yl + sr, yh - sr, za + sw, zb - sw)
        near = zn * xg / XS if k == len(sashes) - 1 else zm + sw   # (the near pane's visible edge: behind the wall's edge)
        G[f'glass{tag}{k}'] = dict(op=o, zfar=zb - sw, znear=near, k=k, tag=tag)


def add_balcony(S, o):
    """B's balcony under an opening: the slab, the railing on it."""
    zf, zn, yb = o['zf'] + OVER, o['zn'] - OVER, o['yb']
    S.add('slab', XS - PROJ, XS, yb - SLAB, yb, zn, zf)
    r = RAIL; xr = XS - PROJ + r['inset']; yt = yb + r['h']; p = r['post'] / 2; td = r['topd'] / 2
    S.add('rail_hand', xr - td, xr + td, yt - r['top'], yt, zn, zf)                                  # the handrail
    S.add('rail', xr - 0.008, xr + 0.008, yb + r['bot'][0], yb + r['bot'][1], zn, zf)               # the bottom rail
    for z in (zn + p, zf - p):
        S.add('rail', xr - p, xr + p, yb, yt - r['top'], z - p, z + p)                              # a corner post
        S.add('rail_hand', xr, XS, yt - r['top'], yt, z - td, z + td)                               # its return
        S.add('rail', xr, XS, yb + r['bot'][0], yb + r['bot'][1], z - 0.008, z + 0.008)
        for xb in (xr + 0.068,):
            S.add('rail', xb - r['bar'][0] / 2, xb + r['bar'][0] / 2, yb + r['bot'][0], yt - r['top'], z - 0.006, z + 0.006)
    span = zf - zn - 4 * p; n = int(np.floor(span / BAR)); z0 = zn + 2 * p + 0.5 * (span - n * BAR)
    for k in range(n + 1):                                                                          # the flat bars
        z = z0 + k * BAR
        S.add('rail', xr - r['bar'][1] / 2, xr + r['bar'][1] / 2, yb + r['bot'][1], yt - r['top'], z - r['bar'][0] / 2, z + r['bar'][0] / 2)


def add_sill(S, o):
    S.add('sill', XS - SILL['p'], XS + 0.02, o['yb'] - SILL['t'], o['yb'], o['zn'] - SILL['over'], o['zf'] + SILL['over'])


def sky_shadow(S, P, names):
    """The share of the sky's light (from above and the street's side) the parts `names` leave to points P."""
    seen = np.zeros(len(P))
    dirs = [np.array((-np.cos(el) * np.cos(az), np.sin(el), np.cos(el) * np.sin(az)))
            for el in (0.6, 0.9, 1.2) for az in (-0.45, -0.15, 0.15, 0.45)]
    for L in dirs:
        seen += ~S.blocked(P, L, names)
    return seen / len(dirs)


# ------------------------------------------------------------------------------------------------------- the painting
def lowfill(img, hole, s):
    """The low frequencies of img, the hole's pixels left out (normalised convolution)."""
    wgt = (~hole).astype(float)
    while True:
        num = np.stack([gaussian_filter(img[..., c] * wgt, s) for c in range(3)], -1)
        den = gaussian_filter(wgt, s)[..., None]
        if (den > 1e-3).all() or s > 40: break
        s *= 1.6
    return num / np.maximum(den, 1e-6)


def wall_clean(O, old, shift):
    """The wall where the painter's flat window or railing was: its light from the wall round it, its grain from
    `shift` (dx, dy) away (the wall's own, there)."""
    lf = lowfill(O, old, 3.0); hp = O - lowfill(O, np.zeros_like(old), 1.2)
    g = np.roll(np.roll(hp, -shift[1], 0), -shift[0], 1)
    return np.where(old[..., None], np.clip(lf + g, 0, 255), O)


def old_mask(box, spans, cols=()):
    """The painter's flat windows (each opening's columns, a pixel more on the far side, between rays) and the bars he
    drew on the wall by them (cols: x0, x1, v0, v1)."""
    x0, y0, x1, y1 = box
    yy, xx = np.mgrid[y0:y1, x0:x1] + 0.5
    v = (VPY - yy) / (xx - VPX); m = np.zeros(yy.shape, bool)
    for o, va, vb in spans:
        m |= (xx >= o['xl'] - 1.0) & (xx <= o['xr']) & (v >= va) & (v <= vb)
    for a, b, va, vb in cols:
        m |= (xx >= a) & (xx <= b) & (v >= va) & (v <= vb)
    return m


def painter_curtains(name, at, cols):
    """His lit colours across a pane, column by column (the comp `name` at `at`; cols: (x, rows) the rows of each
    column on his curtain, above his rail), medians."""
    a = np.asarray(Image.open(os.path.join(EDITS, name + '_before.webp')).convert('RGBA')).astype(float)
    return np.array([np.median(a[[y - at[1] for y in ys], x - at[0], :3], 0) for x, ys in cols])


def curtain(prof, ys, u, w):
    """prof across a pane (u: 0 its far edge, 1 its near one) times the light down it (ys at heights w)."""
    n = len(prof); q = np.clip(u, 0, 1) * (n - 1)
    i = np.clip(np.floor(q).astype(int), 0, n - 2); f = (q - i)[..., None]
    c = prof[i] * (1 - f) + prof[i + 1] * f
    return c * np.interp(np.clip(w, 0, 1), ys[0], ys[1])[..., None]


def reflection(which, w, u):
    """The night in the glass: the sky's violet over the darker roofs across (lighter up the pane), a faint slanted
    sheen."""
    top, low = (np.array(c) for c in REFL[which])
    c = low + (top - low) * np.clip(w, 0, 1)[..., None]
    return c * (1 + 0.10 * np.exp(-((w - 0.9 * u - 0.12) / 0.12) ** 2))[..., None]


def lamp_mask():
    """The street lamp's arm and bracket as tools/pole_lamp.py draws them (never drawn over here)."""
    import building_tops as BT
    cov, _ = BT.lamp_cover(True)
    return cov > 0


def sign_mask(box):
    from PIL import ImageDraw
    x0, y0, x1, y1 = box
    m = Image.new('L', (x1 - x0, y1 - y0), 0)
    ImageDraw.Draw(m).polygon([(x - x0, y - y0) for x, y in C_SIGN], fill=255)
    return np.asarray(m) > 127


# ------------------------------------------------------------------------------------------------------------ drawing
def model(which):
    S = Scene(); G = {}
    if which == 'B':
        ops = [opening(B_TOP, DEPTH['B']), opening(B_LOW, DEPTH['B'])]
        x0, y0, x1, y1 = B_BOX
        add_wall(S, ops, (z_wall(x1 + 8), z_wall(x0 - 40)), (B_LOW['vb'] * XS - 1.2, B_TOP['vt'] * XS + 1.2))
        add_window(S, ops[0], 'T', G); add_window(S, ops[1], 'L', G)
        add_balcony(S, ops[0]); add_balcony(S, ops[1])
    else:
        ops = [opening(C_WIN, DEPTH['C']), opening(C_TOP, DEPTH['C'])]
        x0, y0, x1, y1 = C_BOX
        add_wall(S, ops, (z_wall(x1 + 8), z_wall(x0 - 10)), (C_WIN['vb'] * XS - 1.2, C_TOP['vt'] * XS + 1.2))
        add_window(S, ops[0], 'C', G); add_sill(S, ops[0])
        add_window(S, ops[1], 'D', G); add_sill(S, ops[1])
    return S, G, ops


def rooms():
    """Each pane's room, lit: the painter's curtains (prof across the pane) and his light down them (ys)."""
    rows = lambda x, va, vb: [y for y in range(200, 440) if VPY - va * (x + 0.5 - VPX) + 3 < y + 0.5 < VPY - vb * (x + 0.5 - VPX) - 2]
    top = lambda x: rows(x, 1.283, 1.07)
    far = painter_curtains('win_z1_top', (963, 226), [(x, top(x)) for x in range(969, 983)])
    near = painter_curtains('win_z1_top', (963, 226), [(x, top(x)) for x in range(984, 1003)])
    cr = list(range(330, 400))                                       # (C: one sash; his mullion at 1095 left out)
    cw = painter_curtains('win_z1_warm', (1081, 288), [(x, cr) for x in list(range(1088, 1095)) + list(range(1096, 1108))])
    return {'T0': (far, YS_B), 'T1': (near, YS_B), 'C0': (cw, YS_C)}


def draw(which, box, O, U):
    """One zone: (off, lit, power cut) pictures over box (floats), the share of each pixel's rays on the glass (by
    pane) and on what changed."""
    S, G, ops = model(which)
    x0, y0, x1, y1 = box; h, w = y1 - y0, x1 - x0; n = SS * SS
    dx, dy = rays(box)
    idx, t, face = S.cast(dx, dy)
    t = np.where(idx >= 0, t, 1.0)                                   # (a ray that meets nothing: none of it is drawn)
    P = np.stack([dx * t, dy * t, t], -1)
    names = np.array(S.name + ['none'], dtype=object)[idx]
    bx = np.array(S.b + [(0, 0, 0, 0, 0, 0)], float)[idx]           # each ray's box
    px = F / t                                                       # px a metre at the hit
    off = np.zeros((h, w, n, 3)); lit = np.zeros_like(off); cut = np.zeros_like(off)

    def put(m, c_off, c_lit=None, c_cut=None):
        c_off = np.broadcast_to(c_off, off.shape)
        off[m] = c_off[m]
        lit[m] = np.broadcast_to(c_lit if c_lit is not None else c_off, off.shape)[m]
        cut[m] = np.broadcast_to(c_cut if c_cut is not None else c_off, off.shape)[m]

    # the wall: the painting (where his flat window was, the wall run on), in the model's shadows
    if which == 'B':
        old = old_mask(box, [(B_TOP, 0.935, 1.283), (B_LOW, 0.46, 0.803)], cols=[(962.0, 964.0, 0.935, 1.11), (962.0, 964.0, 0.46, 0.63),
                                                                                 (1004.0, 1006.0, 0.935, 1.11), (1004.0, 1006.0, 0.46, 0.63)])
        shift = (-14, 0); casters = ('slab', 'rail', 'rail_hand')
    else:
        old = old_mask(box, [(C_WIN, 0.488, 0.797), (C_TOP, 0.955, 1.199)]); shift = (-12, 0); casters = ('sill',)
    Oc, Uc = wall_clean(O, old, shift), wall_clean(U, old, shift)
    wall = (names == 'wall') & (face == 0)
    sh = np.ones((h, w, n)); sh[wall] = 0.42 + 0.58 * sky_shadow(S, P[wall], casters)
    put(wall, Oc[:, :, None, :] * sh[..., None], None, Uc[:, :, None, :] * sh[..., None])
    tone = np.median(Oc[~old & (np.abs(Oc - O).max(-1) == 0)], 0)
    # the recess: the far jamb, the soffit (the wall's faces in an opening)
    for op in ops:
        inop = (P[..., 2] > op['zn'] - 0.5) & (P[..., 2] < op['zf'] + 1e-3) & (P[..., 1] > op['yb'] - 1e-3) & (P[..., 1] < op['yt'] + 1e-3)
        dep = np.clip((P[..., 0] - XS) / op['d'], 0, 1)
        up = np.exp(-np.clip(op['yt'] - P[..., 1], 0, None) / 0.18)
        jamb = (names == 'wall') & (face == 2) & inop
        c = tone * np.array(JAMB_K[which]) * ((1.12 - 0.42 * dep) * (1 - 0.35 * up))[..., None]
        put(jamb, c, c * 0.25 + REVEAL_LIT * ((0.55 + 0.45 * dep) * (1 - 0.2 * up))[..., None])
        sof = (names == 'wall') & (face == 1) & inop
        c = np.where(((P[..., 0] - XS) * px < 1.0)[..., None], TONE['soffit_arris'], TONE['soffit'])
        put(sof, c, c * 0.4 + SOFFIT_LIT * (0.35 + 0.65 * dep)[..., None])
    # the frame and the sashes
    fk = FRAME_K[which]
    for nm in ('frame', 'sash'):
        for f, tn, k in ((0, 'frame', 0.4), (1, 'frame_under', 0.3), (2, 'frame_side', 0.6)):
            m = (names == nm) & (face == f)
            put(m, TONE[tn] * fk, TONE[tn] * fk * 0.6 + FRAME_LIT * k)
    # the glass: the room behind it
    R = rooms(); gl = np.zeros((h, w, n), bool); pane = {}
    for key, g in G.items():
        m = names == key
        if not m.any(): continue
        op = g['op']; gl |= m; pane[key] = m
        u = (g['zfar'] - P[..., 2]) / (g['zfar'] - g['znear'])
        wv = (P[..., 1] - op['yb']) / (op['yt'] - op['yb'])
        uo = (op['zf'] - P[..., 2]) / (op['zf'] - op['zn'])
        refl = reflection(which, wv, uo)
        rk = g['tag'] + str(g['k'])
        if rk in R:
            room = curtain(R[rk][0], R[rk][1], u, wv)
            if rk == 'T0':                                           # the ceiling lamp behind the sheer: a little more
                room = room * (1 + 0.06 * np.exp(-((u - 0.55) / 0.35) ** 2 - ((1 - wv) / 0.22) ** 2))[..., None]
            put(m, room * OFF_K * 0.82 + refl * 0.30, room + refl * 0.12, refl * 0.40 + room * 0.02)
        else:                                                        # (the low window: never lit; a drape at each jamb)
            fold = 1 - 0.08 * np.exp(-(np.minimum(u, 1 - u) / 0.12) ** 2) * (0.6 + 0.4 * np.cos(u * 40.0))
            put(m, refl * fold[..., None])
    # the balconies' slabs, C's sill: the front face with its lit arris and its dark lower edge, its end, its underside
    for nm, pre in (('slab', 'slab'), ('sill', 'sill')):
        m = names == nm
        if not m.any(): continue
        below_top = (bx[..., 3] - P[..., 1]) * px; over_bot = (P[..., 1] - bx[..., 2]) * px
        fc = np.where((below_top < 1.0)[..., None], TONE[pre + '_arris'],
                      np.where((over_bot < 1.0)[..., None], TONE[pre + '_low'], TONE[pre]))
        put(m & (face == 0), fc); put(m & (face == 1), TONE[pre + '_under']); put(m & (face == 2), TONE[pre + '_end'])
        for op in ops:                                               # (a lit room's light on its sill's front edge)
            if op['dark']: continue
            mo = m & (face == 0) & (np.abs(P[..., 1] - op['yb']) < 0.25)
            k = np.where(below_top < 1.0, 0.45, 0.15)[..., None]
            lit[mo] = (lit + REVEAL_LIT * k)[mo]
    # the railings: dark steel, the handrail's top lit
    for nm in ('rail', 'rail_hand'):
        m = names == nm
        if not m.any(): continue
        lit_top = ((bx[..., 3] - P[..., 1]) * px < 1.0) & (nm == 'rail_hand')
        body = TONE['rail_hand'] if nm == 'rail_hand' else TONE['rail']
        put(m & (face == 0), np.where(lit_top[..., None], TONE['rail_top'], body))
        put(m & (face == 1), TONE['rail_under'])
        put(m & (face == 2), np.where(lit_top[..., None], TONE['rail_top'], body if nm == 'rail_hand' else TONE['rail_side']))
    rest = names == 'none'
    put(rest, O[:, :, None, :], None, U[:, :, None, :])
    for op in ops:                                                   # (a room never lit: its recess the same lit or not)
        if op['dark']:
            m = (P[..., 0] >= XS) & (P[..., 2] > op['zn'] - 0.5) & (P[..., 2] < op['zf'] + 1e-3) & (P[..., 1] > op['yb'] - 1e-3) & (P[..., 1] < op['yt'] + 1e-3)
            lit[m] = off[m]
    A = [a.mean(2) for a in (off, lit, cut)]
    wallr = ((names == 'wall') & (face == 0)) | (names == 'none')  # (R28: what is not wall drawn from the draft, its
    Ds = {op['draft']: draft_grid(box, op['draft']) for op in ops}   # light by state the model's)
    if any(d is not None for d in Ds.values()):
        cn = 'win_z1_top' if which == 'B' else 'win_z1_warm'           # (the palettes: his pixels round here, his old window
        oc = np.asarray(Image.open(os.path.join(EDITS, cn + '_before.webp')).convert('RGBA')).astype(float)   # lit and off)
        oc = oc[oc[..., 3] > 0][:, :3]
        nw = ~wallr; sh_ = nw.mean(2); cnt = np.maximum(nw.sum(2), 1)[..., None]
        NW = [(a * nw[..., None]).sum(2) / cnt for a in (off, lit, cut)]
        WP = [(a * wallr[..., None]).sum(2) / n for a in (off, lit, cut)]
        yn = (P[..., 1] * nw).sum(2) / cnt[..., 0]
        for op in ops:
            D = Ds[op['draft']]
            if D is None: continue                                   # (no draft yet: as the model drew it)
            reg = (sh_ > 0) & (np.abs(yn - 0.5 * (op['yb'] + op['yt'])) < 0.5 * (op['yt'] - op['yb']) + SLAB + 0.25)
            k = 0 if op['dark'] else 1                               # (a dark room: fitted on its off picture)
            gs = gl.sum(2) / cnt[..., 0]                             # (the glass, the rest: each its own tint)
            fg, fo = reg & (sh_ > 0.5) & (gs > 0.5), reg & (sh_ > 0.5) & (gs <= 0.5)
            tg = tint(D[reg], D[fg], NW[k][fg], 1.25 if k else 3.0) if fg.sum() >= 30 else None
            to = tint(D[reg], D[fo], NW[k][fo]) if fo.sum() >= 30 else None
            tg, to = (tg if tg is not None else to), (to if to is not None else tg)
            dl = tg * gs[reg][:, None] + to * (1 - gs[reg][:, None])
            dm = np.zeros_like(D); dm[reg] = dl
            ys_, xs_ = np.nonzero(reg)                               # (its palettes: the painter's pixels round this
            loc = np.zeros_like(reg)                                 # window, his old window there, lit and off)
            loc[max(ys_.min() - 8, 0):ys_.max() + 9, max(xs_.min() - 8, 0):xs_.max() + 9] = True
            pal = [np.vstack([palette(O[loc & old], 20), palette(O[loc & ~old], 20)]),
                   np.vstack([palette(oc, 32), palette(O[loc & ~old], 16)]) if k else None,
                   np.vstack([palette(U[loc & old], 16), palette(U[loc & ~old], 20)])]
            pal[1] = pal[1] if k else pal[0]
            for j, (a, wp) in enumerate(zip(A, WP)):                 # each state: the draft times the model's change
                r = (NW[j] + 1) / (NW[k] + 1)                        # from its fitted state there (the room off, out)
                c = snap(np.clip((dm + 1) * r - 1, 0, 255), pal[j])
                a[reg] = (wp + sh_[..., None] * c)[reg]
        if which == 'B' and Ds['wdBC'] is not None:                  # (Red's glass: where the draft shows the room)
            pane = {k_: m_ & glass_seen(Ds['wdBC'], names, k_) for k_, m_ in pane.items()}
    yy, xx = np.mgrid[0:h, 0:w]                                      # (nothing changes on the box's edge: the model's
    edge = np.clip(np.minimum(np.minimum(yy, h - 1 - yy), np.minimum(xx, w - 1 - xx)) / 4.0, 0, 1)[..., None]   # shadows fade
    for a, src in zip(A, (O, O, U)):                                 # out over its last 4 px)
        a[:] = src + (a - src) * edge
    keep = np.zeros((h, w), bool)                                    # what stands in front: as it is
    if which == 'B':
        keep |= lamp_mask()[y0:y1, x0:x1]
    else:
        keep |= sign_mask(box)
    for a, src in zip(A, (O, O, U)):
        a[keep] = src[keep]
    covg = {k: (m.mean(2) * ~keep) for k, m in pane.items()}
    return A, covg, keep


DRAFTS = {                                     # the drafts (R28: tools/src/edits/<name>_draft_in.webp, _prompt.txt, _model.webp)
    'wdBC': dict(box=(942, 205, 1122, 525), scale=4),   # the street lit: B's two windows, C's lit one
    'wdCU': dict(box=(1030, 110, 1126, 280), scale=8),  # C's top storey's window
}


def draft_grid(box, name):
    """A draft (tools/src/edits/<name>_model.webp, the image model's answer to the street lit with these windows as the
    model here drew them) brought to the street's pixels over box: boxed down to its crop's grid, darkened back (the
    call brightened it), moved by the whole pixel that best matches the walls round the windows (tools/redraw_zones.py's
    register). None while there is none."""
    path = os.path.join(EDITS, name + '_model.webp')
    if not os.path.exists(path): return None
    import redraw_zones as RZ
    dx0, dy0, dx1, dy1 = DRAFTS[name]['box']; dw, dh = dx1 - dx0, dy1 - dy0
    e = np.asarray(Image.open(path).convert('RGB').resize((dw, dh), Image.BOX)).astype(float) / 255.0
    e = (e ** RZ.GAMMA) * 255.0
    if name not in _DR:
        src = np.asarray(Image.open(os.path.join(EDITS, name + '_draft_in.webp')).convert('RGB')).astype(float)
        ref = np.zeros((dh, dw), bool)
        ref[8:-8, 8:-8] = True                                       # (the walls: the windows, the pole and the sign out)
        yy, xx = np.mgrid[dy0:dy1, dx0:dx1] + 0.5
        v = (VPY - yy) / (xx - VPX)
        for o, va, vb in ((B_TOP, 0.85, 1.40), (B_LOW, 0.40, 0.90), (C_WIN, 0.46, 0.85), (C_TOP, 0.93, 1.21)):
            ref &= ~((xx > o['xl'] - 22) & (xx < o['xr'] + 6) & (v > va) & (v < vb))
        ref &= ~((xx > 1018) & (xx < 1072))
        _DR[name] = RZ.register(e, src, ref, 3)
        print('window_depth: the draft', name, 'registered', _DR[name])
    _, sx, sy = _DR[name]
    e = RZ.shift(e, sy, sx)
    x0, y0, x1, y1 = box
    yi = np.clip(np.arange(y0, y1) - dy0, 0, dh - 1); xi = np.clip(np.arange(x0, x1) - dx0, 0, dw - 1)
    return e[yi][:, xi]


_DR = {}


def tint(vals, src, tgt, hi=1.25):
    """The draft's colours (vals: already close to the painter's, his wall within 2 levels) brought to his tint there:
    a gain per channel, the model's picture of the same pixels (tgt: his tones and light) over the draft's (src), on
    their means, held within a quarter (the draft's contrast and its structure kept; a dark room's glass, the draft's
    much darker than his navy reflection, up to `hi`)."""
    g = np.clip(tgt.mean(0) / np.maximum(src.mean(0), 1e-3), 0.8, hi)
    return np.clip(vals * g, 0, 255)


def palette(pix, n):
    """n colours of the painter's (median cut over his pixels: deterministic)."""
    side = int(np.ceil(np.sqrt(len(pix))))
    a = np.zeros((side * side, 3), np.uint8); a[:len(pix)] = np.clip(np.round(pix), 0, 255); a[len(pix):] = a[0]
    q = Image.fromarray(a.reshape(side, side, 3), 'RGB').quantize(colors=n, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    return np.array(q.getpalette()[:3 * n], float).reshape(-1, 3)


def snap(img, pal):
    """Each pixel the nearest of the palette's colours."""
    if pal is None: return img
    f = img.reshape(-1, 3)
    d = ((f[:, None, :] - pal[None, :, :]) ** 2).sum(-1)
    return pal[np.argmin(d, 1)].reshape(img.shape)



def glass_seen(D, names, key):
    """(per ray) the glass where the draft shows it bright (not a bar or a frame it drew in front)"""
    L = D @ np.array([0.299, 0.587, 0.114])
    return (L > 0.45 * np.percentile(L, 99.5))[..., None] & np.ones(names.shape, bool)


def write_mask(path, cov, comp_box, box):
    """A glass street.js draws in (white, its alpha the share of the pixel that is glass)."""
    cx, cy, cw, ch = comp_box; x0, y0 = box[0], box[1]
    a = np.zeros((ch, cw, 4), np.uint8); a[..., :3] = 255
    sub = cov[cy - y0:cy - y0 + ch, cx - x0:cx - x0 + cw]
    a[..., 3] = np.round(255 * np.clip(sub, 0, 1)).astype(np.uint8)
    Image.fromarray(a, 'RGBA').save(path, 'WEBP', lossless=True, quality=100, method=6, exact=True)


def comp_of(off, lit, comp_box, box):
    """The lit window as street.js lays it over the street: the lit picture where it differs from the off one."""
    cx, cy, cw, ch = comp_box; x0, y0 = box[0], box[1]
    sl = (slice(cy - y0, cy - y0 + ch), slice(cx - x0, cx - x0 + cw))
    lo, ll = np.round(off[sl]), np.round(np.clip(lit[sl], 0, 255))
    c = np.zeros((ch, cw, 4)); diff = np.abs(ll - lo).max(-1) > 0
    c[..., :3] = ll; c[..., 3] = 255 * diff; c[~diff, :3] = 0
    return c


def hand(which, box, O, U, new, unew, m, out=ASSETS):
    (off, lit, cut), covg, keep = draw(which, box, O, U)
    new[m] = np.clip(off, 0, 255)[m]; unew[m] = np.clip(cut, 0, 255)[m]
    if which == 'B':
        cov = sum(c for k, c in covg.items() if k.startswith('glassT'))
        write_mask(os.path.join(out, 'z1_top_glaze.webp'), cov, B_COMP, box)
        return comp_of(np.clip(off, 0, 255), lit, B_COMP, box)
    cov = sum(c for k, c in covg.items() if k.startswith('glassC'))
    write_mask(os.path.join(out, 'z1_warm_mask.webp'), cov, C_COMP, box)
    return comp_of(np.clip(off, 0, 255), lit, C_COMP, box)


def b_windows(box, O, U, new, unew, m):
    """redraw_zones.py, zone winB ('hand'): B's two windows; gives back the lit comp win_z1_top."""
    return hand('B', box, O, U, new, unew, m)


def c_window(box, O, U, new, unew, m):
    """redraw_zones.py, zone winC ('hand'): C's lit window; gives back the lit comp win_z1_warm."""
    return hand('C', box, O, U, new, unew, m)


# ------------------------------------------------------------------------------------------------------------ preview
def preview(out):
    os.makedirs(out, exist_ok=True)
    import io, subprocess
    old = lambda f: np.asarray(Image.open(io.BytesIO(subprocess.run(['git', 'show', f'{BEFORE}:{f}'], cwd=ROOT, capture_output=True,
                                                                check=True).stdout)).convert('RGBA')).astype(float)
    city, unlit = old('assets/layer_city_off.webp'), old('assets/street_unlit.webp')   # (the street before these windows)
    oldc = {c: old(f'assets/{c}.webp') for c in ('win_z1_top', 'win_z1_warm')}
    for which, box, fn, comp, cbox in (('B', B_BOX, 'b', 'win_z1_top', B_COMP), ('C', C_BOX, 'c', 'win_z1_warm', C_COMP)):
        x0, y0, x1, y1 = box
        O, U = city[y0:y1, x0:x1, :3].copy(), unlit[y0:y1, x0:x1, :3].copy()
        new, unew = O.copy(), U.copy(); m = np.ones(O.shape[:2], bool)
        c = hand(which, box, O, U, new, unew, m, out=out)
        Image.fromarray(np.clip(np.round(c), 0, 255).astype(np.uint8), 'RGBA').save(os.path.join(out, comp + '.webp'), 'WEBP', lossless=True)
        # the old lit state for comparison
        oc = oldc[comp]
        old_lit = city[..., :3].copy(); ox, oy = {'win_z1_top': (963, 226), 'win_z1_warm': (1081, 288)}[comp]
        sub = old_lit[oy:oy + oc.shape[0], ox:ox + oc.shape[1]]; a = oc[..., 3:] / 255
        sub[:] = sub * (1 - a) + oc[..., :3] * a
        new_lit = new.copy(); cx, cy, cw, ch = cbox; a = c[..., 3:] / 255
        s2 = new_lit[cy - y0:cy - y0 + ch, cx - x0:cx - x0 + cw]; s2[:] = s2 * (1 - a) + c[..., :3] * a
        tiles = [O, new, old_lit[y0:y1, x0:x1], new_lit, U, unew]
        k = 6; gap = 6
        im = Image.new('RGB', ((x1 - x0) * k * 6 + gap * 5, (y1 - y0) * k), (255, 0, 255))
        for i, tl in enumerate(tiles):
            im.paste(Image.fromarray(np.clip(np.round(tl), 0, 255).astype(np.uint8)).resize(((x1 - x0) * k, (y1 - y0) * k), Image.NEAREST), (i * ((x1 - x0) * k + gap), 0))
        im.save(os.path.join(out, f'{fn}_x{k}.png'))
        for tag, tl in (('off', new), ('lit', new_lit), ('cut', unew), ('before_off', O), ('before_lit', old_lit[y0:y1, x0:x1])):
            Image.fromarray(np.clip(np.round(tl), 0, 255).astype(np.uint8)).save(os.path.join(out, f'{fn}_{tag}_1x.png'))
        print(which, 'done')


BEFORE = 'e987b8c'                             # (the street as it was before these windows: --preview starts from it)


def ask(name):
    """A draft asked of the image model by tools/redraw_zones.py's call() (its model, its brightening, its pixel blocks):
    tools/src/edits/<name>_draft_in.webp (the street lit, these windows as the model here drew them) and <name>_prompt.txt
    (or <name>_opt<K>_prompt.txt for NAME:K), its answer saved as tools/src/edits/<name>[_opt<K>]_model.webp. Costs about
    0.14 $; the windows are drawn from the saved answers, never from a new call."""
    import redraw_zones as RZ
    for k, cfg in DRAFTS.items():
        RZ.ZONES.setdefault(k, cfg)
    RZ.call(name)


if __name__ == '__main__':
    if '--ask' in sys.argv:
        ask(sys.argv[sys.argv.index('--ask') + 1])
    elif '--preview' in sys.argv:
        preview(sys.argv[sys.argv.index('--preview') + 1])
    else:
        print(__doc__)
