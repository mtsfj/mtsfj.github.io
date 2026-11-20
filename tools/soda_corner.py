#!/usr/bin/env python3
"""The drinks corner on the left sidewalk, rebuilt whole (the owner: "faut refaire toute cette zone"; "la dernière soda
prend la place de là où il y a la caisse"; "j'ai validé juste les atouts ; le reste, rien d'obligatoire : juste que ça
soit beau"): Kirua's house's ground floor from under the painter's boards down to the sidewalk, from the dagashi-ya's
edge to the bench, laid out in 3D first, then painted from that layout by the image API and brought into the street.

    (a module: tools/redraw_zones.py's zone 'soda' calls draw() on the street as the zones before it leave it)
    python3 tools/soda_corner.py --guide V CTX.png OUT   the blocked-in guide of layout V over CTX (a 22 h render of the
                                                         street, 1456 x 816), its top view and its lines (OUT/...)
    python3 tools/soda_corner.py --fit V CTX.png         fit the takes of V on the street (their registration, their
                                                         colours) and print FIT[V] (paste it below)
    python3 tools/soda_corner.py --preview DIR           the zone off, lit, in the stutter, before and after (nothing
                                                         in the repository changes)

1. The layout (layout(V)), in the street's camera as the dagashi-ya next door has it (tools/dagashi_interior.py: F 1400
   px, VP (700, 615), the eye 1.5 m over the sidewalk; X across, left negative; Y up from the sidewalk; Z along the
   street): the house's front on the dagashi-ya's line (X -6.33) to its corner (its downpipe, x 326); the three drinks
   machines (Speed Cola, Double Tap, Juggernog, near to far: the zombies game's Perk-a-Cola, street.js PERKS) side by
   side against it, 1 m along the street, 0.82 m deep, 2 m high, their fronts to the street; a small tiled canopy
   (hisashi) on the house over them, its line on the wall at the dagashi-ya's lintel (2.62 m, y 531 at its edge), 1 m
   out, its pitch 3 in 10 (its eave 2.32 m: 30 cm over the machines); no two volumes meet.
   A and C: a tobacco booth at the near end (its front to us: the たばこ sign, its service window; 0.75 m out from the
   house, 1.14 m long, under the canopy), the machines after it; an LED ad sign projecting from the wall over them (its
   face to us). A: a small lit lattice window on the wall; C: the wall the painter's boards, plain.
   B (the owner's choice, VARIANT here): the machines first, the nearest one's side to us a backlit ad panel; the
   canopy a real one seen from under it (its wooden soffit, rafters and fascia with the round tile ends from end to
   end, its near end cut, three knee braces), run on to the house's corner; on the house's front just over it, well
   under Kirua's bay, a giant screen (its box, frame, bolts; its clips: SCREEN_CLIPS says how to change
   them); the house's boards round it the painter's own; then a grain pass over the machines, the panel, the canopy
   and the ground at their feet (EDIT: generated from the corner as composed here, laid on those parts only), the
   machines brought into the painting's range (MACH_TONE), their headers backlit drinks banners (heads(), HEADS);
   the house's whole front from under Kirua's bay down to the canopy, round and behind the screen, the dagashi-ya's
   own boards carried along their lines (face_boards(), FACE_*: one building, one plane, one material and tone, R29).
2. The takes (tools/src/soda_<V>_lit.webp, soda_<V>_off.webp; R28): the street around the corner at 22 h and the
   layout's blocked-in render over it (tools/src/soda_<V>_guide.webp, --guide) given to the image API with the parts
   to paint (the prompts: tools/src/soda_prompts.txt); the lit take first, the off ones an edit of the lit corners
   (every light out), registered back on them (kept as WebP at quality 92: below a level once averaged as here).
3. Each take registered on the street (a scale and an offset, fitted once on the street round the corner: FIT), brought
   down to the street's pixels by area (each street pixel the mean of the take's pixels over it), its colours carried
   into the painter's (one gain and an offset per channel, from the means and spreads of the street just round the
   corner where the take left it as it was, FIT; the off take the lit one's), a few flat colours (median cut, no
   dither: QUANT); a face a take got wrong from another take of the same layout (BORROW); the take's house boards
   brought to the painter's tone where his end (WALL_MATCH: a gain per channel, their lights left as they add); the
   machines' display windows drawn on the layout's fronts (DISPLAY: the takes copy the guide's placeholder stripes);
   laid in the zone's mask (mask(): the house's boards above the old roof's flashing and the tree above the old roof
   kept, the bench and its lamp kept, the sidewalk kept under the things' feet) - the off take in the layers (the
   power cut: the same).
4. The lights, from the lit take less the off one: the machines' comp z7_vending (z7_vendoff: the middle one's front
   off, its stutter; the light pool vend_pool moved under them), the booth's window win_z7_kiosk (A, C; B: none, nor its
   comp nor its light on the ground), the ad's comp
   z7_adscreen (the six frames of the three ads, tools/src/soda_ads_model.webp, in its glass; its light on the wall
   from the take), A's window win_z7_low; B's giant screen z7_bigscreen (its clips in its glass in perspective, a sheet a
   clip, their light on the boards and the canopy round it; B's side panel the perks' retro ads; street.js's ADS gets
   the clips, their frames and versions, SODA_FX the corner's small lights' places).
   The rain (drip_points(), wet_ground()): the canopy's drips off its round tile ends (DRIPS 'kiosk': a trickle every
   other channel, bigger ones at its two corners, little bursts at the channels between); the ground under it in the
   street's water map (assets/wet.webp, wet_mirror.webp, from their before copies: WET_SRC): dry under the things, the
   mirror line at their feet, damp in the canopy's shelter, a wetter splash line where the drops land with a small puddle
   under each trickle, the painter's old drip line's band dried, the ground his lean-to stood on wet as the sidewalk.
   The perks' shields (assets/*_perk.webp, their first frame) laid on the headers, as the takes drew their badges
   (B: none, the side panel's ads carry the perks). street.js: PERKS' columns and BZ.soda from the machines' fronts, the drips
   off the canopy's eave (DRIPS 'kiosk'), the comps' places. Needs Pillow, numpy, scipy.
"""
import os
import sys
import json
import re
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter, binary_dilation

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'tools', 'src')
EDITS = os.path.join(SRC, 'edits')
RET = os.path.join(SRC, 'retouches')
VARIANT = 'B'                                  # (the layout and the takes this branch lays: A, B or C)
BOX = (227, 320, 390, 745)
F, VX, VY, EYE = 1400.0, 700.0, 615.0, 1.5
XH = -6.33                                     # the house's front (the dagashi-ya's line)
ZC = F * -XH / (VX - 326.0)                    # its corner (the downpipe at x 326-330)
LINTEL = 2.62                                  # the dagashi-ya's lintel line (y 531 at its edge)
CROP = (130, 220, 490, 760)                    # what the takes show (2:3)
K = 4                                          # the guide's pixels per street pixel
FLASH = 0.446                                  # the old roof's flashing on the house (its ray): above it the painter's
ROOF = (326, 390, 532)                         # (past the corner, the old roof's edge down to x 390, y 532)
QUANT = 48                                     # flat colours over the zone (median cut, no dither)
PERK_NAMES = ('speed', 'tap', 'jugg')
AD_N = 6
AD_PAD = 6                                     # (the ad's comp: its light on the wall so many pixels out)
AD_MODEL = 'soda_ads_model.webp'               # the three ads (ramune, ramen, the arcade's games), on black
AD_PANELS = [(70, 61, 431, 711), (508, 61, 869, 711), (946, 61, 1307, 711)]
# the takes' registration on the street (s: take pixels per street pixel; ox, oy: the crop's corner in the take) and
# their colours' map (3 x 4, on 0..255) into the painter's: written by --fit, once, from the takes as made
FIT = {'B': {"lit": {"s": 4.7111, "ox": 0.0, "oy": -8.0, "M": [[1.0487, 0.0, 0.0, -2.4161], [0.0, 1.0487, 0.0, -0.5586], [0.0, 0.0, 1.0487, -2.7556]]}, "off": {"s": 4.7111, "ox": 0.0, "oy": -8.0, "M": [[1.0487, 0.0, 0.0, -2.4161], [0.0, 1.0487, 0.0, -0.5586], [0.0, 0.0, 1.0487, -2.7556]]}}}
# (per variant: small shifts of the shields and of the ad's glass, in street pixels, to sit on the take's own drawing)
NUDGE = {'A': dict(shield=(0, 0), ad=(0, 0)), 'B': dict(shield=(0, 0), ad=(0, 0)), 'C': dict(shield=(0, 0), ad=(0, 0))}
# (C's take painted a machine where the booth's side wall is: that face, and the first machine's side, from A's takes)
BORROW = {'C': ('A', [('booth', (1, 3)), ('mach0', (4,))])}
WALL_MATCH = (232, 320, 6)                     # (the boards' tone matched over these columns, so many rows each side)


def P(X, Y, Z):
    return VX + F * X / Z, VY - F * (Y - EYE) / Z


def layout(v):
    """The volumes of layout v: boxes (X0, X1, Y0, Y1, Z0, Z1), the canopy, the ad's face (or panel)."""
    L = {}
    if v in ('A', 'C'):
        L['booth'] = (XH, -5.58, 0.0, 2.28, 18.66, 19.80)
        z0 = 19.80
    else:
        z0 = 18.66
    L['mach'] = [(XH, -5.51, 0.0, 2.0, z0 + i, z0 + i + 1.0) for i in range(3)]
    L['canopy'] = dict(z0=18.66, z1=min(z0 + 3.2, ZC - 0.3), y_wall=LINTEL, proj=1.0, pitch=0.3, th=0.07, tile=0.2)
    if v == 'B':
        # (B as chosen: the canopy a real one seen from below, run on to the house's corner; over it, on the house's
        # front, the giant screen, just above the canopy and well under Kirua's bay (its sill 5.3 m up, the screen's
        # top 4.22 m): its box 10 cm off the wall, X0..X1, Y0..Y1, Z0..Z1)
        L['canopy'].update(z1=ZC - 0.3, th=0.16)
        L['bigscreen'] = (XH, XH + 0.10, 2.72, 4.22, 19.05, 23.25)
    if v in ('A', 'C'):
        L['screen'] = (-6.25, -5.65, 2.95, 3.95, 20.30, 20.42)
        s = L['screen']
        L['glass'] = (s[0] + 0.04, s[1] - 0.04, s[2] + 0.04, s[3] - 0.04, s[4])     # (X0, X1, Y0, Y1, Z: its face)
    else:
        m = L['mach'][0]
        L['glass'] = (m[0] + 0.07, m[1] - 0.07, 0.22, 1.90, m[4])
    if v == 'A':
        L['window'] = (XH, 2.86, 3.36, 19.0, 19.55)                                # (X, Y0, Y1, Z0, Z1: on the wall)
    L['ad'] = v != 'C'                                                             # (C: an unlit enamel sign there)
    return L


def ray_box(dx, dy, b):
    """Rays from the eye along (dx, dy, 1): the Z where each meets box b (inf if not), the face (0 X-, 1 X+, 2 Y-, 3 Y+,
    4 Z-)."""
    X0, X1, Y0, Y1, Z0, Z1 = b
    with np.errstate(divide='ignore', invalid='ignore'):
        tx0, tx1 = X0 / dx, X1 / dx
        ty0, ty1 = (Y0 - EYE) / dy, (Y1 - EYE) / dy
    txn, txf = np.minimum(tx0, tx1), np.maximum(tx0, tx1)
    tyn, tyf = np.minimum(ty0, ty1), np.maximum(ty0, ty1)
    tn = np.maximum(np.maximum(txn, tyn), Z0); tf = np.minimum(np.minimum(txf, tyf), Z1)
    hit = tn <= tf
    face = np.where(tn == Z0, 4, np.where(tn == txn, np.where(dx > 0, 0, 1), np.where(dy > 0, 2, 3)))
    return np.where(hit, tn, np.inf), face


def canopy_hit(dx, dy, C):
    """The canopy, a slab: its top from the wall (XH, y_wall) down at its pitch to XH + proj, th thick, z0 to z1. The Z
    of the hit and the part (0 its tiles, 1 its soffit, 2 its eave, 3 its near end)."""
    zs = np.full(dx.shape, np.inf); part = np.zeros(dx.shape, int)
    xe = XH + C['proj']
    yt = lambda X: C['y_wall'] - C['pitch'] * (X - XH)
    with np.errstate(divide='ignore', invalid='ignore'):
        for k_, off in ((0, 0.0), (1, -C['th'])):
            Z = (C['y_wall'] + off + C['pitch'] * XH - EYE) / (dy + C['pitch'] * dx)
            X = dx * Z
            ok = (Z > 0) & (X >= XH) & (X <= xe) & (Z >= C['z0']) & (Z <= C['z1'])
            better = ok & (Z < zs); zs = np.where(better, Z, zs); part = np.where(better, k_, part)
        Z = xe / dx
    Y = EYE + dy * Z
    ok = (Z > 0) & (Y <= yt(xe)) & (Y >= yt(xe) - C['th'] - 0.03) & (Z >= C['z0']) & (Z <= C['z1'])
    better = ok & (Z < zs); zs = np.where(better, Z, zs); part = np.where(better, 2, part)
    Z = np.full(dx.shape, C['z0']); X = dx * Z; Y = EYE + dy * Z
    ok = (X >= XH) & (X <= xe) & (Y <= yt(X)) & (Y >= yt(X) - C['th'])
    better = ok & (Z < zs); zs = np.where(better, Z, zs); part = np.where(better, 3, part)
    return zs, part


def rays(box, k=1):
    x0, y0, x1, y1 = box
    xs = x0 + (np.arange((x1 - x0) * k) + 0.5) / k; ys = y0 + (np.arange((y1 - y0) * k) + 0.5) / k
    X, Y = np.meshgrid(xs, ys)
    return (X - VX) / F, -(Y - VY) / F, X, Y


def cast(v, box, k=1):
    """What each pixel of box (k x k rays each, one per sub-pixel) sees of layout v: its name ('' the street as it is),
    its face, its Z."""
    L = layout(v)
    dx, dy, X, Y = rays(box, k)
    zbest = np.full(dx.shape, np.inf); what = np.full(dx.shape, '', object); face = np.zeros(dx.shape, int)
    with np.errstate(divide='ignore'):
        zw = XH / dx
    yw = EYE + dy * zw
    wall = region(X, Y) & (zw > 0) & (zw <= ZC) & (zw >= 18.6) & (yw >= 0)
    zbest = np.where(wall, zw, zbest); what = np.where(wall, 'wall', what)
    items = ([('booth', L['booth'])] if 'booth' in L else []) + [('mach%d' % i, m) for i, m in enumerate(L['mach'])]
    if 'screen' in L: items.append(('screen', L['screen']))
    if 'bigscreen' in L: items.append(('bigscreen', L['bigscreen']))
    for name, b in items:
        z, f = ray_box(dx, dy, b)
        better = z < zbest; zbest = np.where(better, z, zbest); what = np.where(better, name, what); face = np.where(better, f, face)
    zc, pc = canopy_hit(dx, dy, L['canopy'])
    better = zc < zbest; zbest = np.where(better, zc, zbest); what = np.where(better, 'canopy', what); face = np.where(better, pc, face)
    return what, face, zbest, dx, dy, X, Y


def region(X, Y):
    """The rebuilt area (street coordinates): under the old flashing's ray on the house, under the old roof's edge past
    the corner, x 227..389, y 395..744."""
    top = np.where(X <= ROOF[0], VY - FLASH * (VX - X), np.interp(X, ROOF[:2], [VY - FLASH * (VX - ROOF[0]), ROOF[2]]))
    return (X >= BOX[0]) & (X < BOX[2]) & (Y >= top) & (Y < BOX[3]) & (Y >= BOX[1])


# ---------------------------------------------------------------- the guide (what the image API was given) ----

def guide(v, ctx, sign, ad, shields):
    """The blocked-in render of layout v over ctx (the street over CROP, a 22 h render), K times larger: flat faces and
    a few lines (boards, planks, tiles, the machines' parts), the sign, the ad, the shields where they go."""
    L = layout(v)
    what, face, zb, dx, dy, X, Y = cast(v, CROP, K)
    old = (X >= 260) & (X < 325) & (Y >= 416) & (Y < 512)            # (v4's screen in the render: wall)
    with np.errstate(divide='ignore'):
        zw = XH / dx
    what = np.where(old & (what == ''), 'wall', what); zb = np.where(old & (zb == np.inf), zw, zb)
    base = np.asarray(Image.fromarray(ctx).resize(((CROP[2] - CROP[0]) * K, (CROP[3] - CROP[1]) * K), Image.NEAREST)).astype(float)
    Xw, Yw, Zw = dx * zb, EYE + dy * zb, zb
    col = np.zeros(base.shape)
    with np.errstate(invalid='ignore'):
        m = what == 'wall'
        col[m] = np.where(((Yw / 0.09) % 1.0 < 0.18)[m][:, None], (16, 20, 44), (30, 38, 74))
        if 'window' in L:
            w = L['window']; win = m & (Yw > w[1]) & (Yw < w[2]) & (Zw > w[3]) & (Zw < w[4])
            lat = (((Zw - w[3]) / 0.09) % 1.0 < 0.2) | (((Yw - w[1]) / 0.1) % 1.0 < 0.2)
            col[win] = np.where(lat[win][:, None], (60, 40, 36), (226, 176, 110))
        if 'booth' in L:
            b = L['booth']
            m = (what == 'booth') & (face == 4)
            u = (Xw - b[0]) / (b[1] - b[0])
            col[m] = np.where(((u * 5) % 1.0 < 0.1)[m][:, None], (18, 24, 50), (32, 42, 82))
            win = m & (u > 0.08) & (u < 0.62) & (Yw > 0.75) & (Yw < 1.85)
            col[win] = (214, 168, 104)
            col[m & (u > 0.05) & (u < 0.65) & (Yw > 0.70) & (Yw < 1.90) & ~win] = (40, 30, 34)
            col[m & (u > 0.03) & (u < 0.67) & (Yw > 0.70) & (Yw < 0.78)] = (90, 70, 60)
            m = (what == 'booth') & (face != 4)
            col[m] = np.where((((Zw - b[4]) / 0.15) % 1.0 < 0.12)[m][:, None], (12, 16, 36), (22, 30, 60))
        PERKC = [(70, 150, 90), (176, 120, 64), (180, 54, 54)]
        for i, b in enumerate(L['mach']):
            nm = 'mach%d' % i
            m = (what == nm) & (face == 1)
            u = (Zw - b[4]) / (b[5] - b[4]); h = Yw
            col[m] = np.array(PERKC[i]) * 0.55
            disp = m & (u > 0.08) & (u < 0.92) & (h > 1.02) & (h < 1.70)
            rows_ = ((h - 1.02) / 0.226) % 1.0
            dc = np.where((rows_ < 0.18)[..., None], np.array((120, 130, 150), float), np.array((226, 232, 236), float))
            bott = ((u * 9) % 1.0 < 0.55) & (rows_ > 0.3) & (rows_ < 0.85)
            pal = np.array([(220, 90, 80), (80, 150, 220), (240, 200, 80)], float)
            dc = np.where(bott[..., None], pal[np.nan_to_num(u * 9).astype(int) % 3], dc)
            col[disp] = dc[disp]
            col[m & (h > 1.76) & (h < 1.96)] = (24, 26, 40)
            col[m & (h > 0.15) & (h < 0.95)] = np.array(PERKC[i]) * 0.35
            col[m & (u > 0.62) & (u < 0.9) & (h > 0.62) & (h < 0.95)] = (60, 66, 80)
            col[m & (u > 0.1) & (u < 0.6) & (h > 0.2) & (h < 0.38)] = (8, 10, 18)
            side = (what == nm) & (face != 1)
            col[side] = (40, 44, 60) if (v == 'B' and i == 0) else np.array(PERKC[i]) * 0.3
        col[what == 'screen'] = (26, 26, 36)
        m = what == 'canopy'; C = L['canopy']
        top = m & (face == 0)
        col[top] = np.where((((Zw - C['z0']) / C['tile']) % 1.0 < 0.35)[top][:, None], (22, 20, 34), (46, 42, 64))
        col[m & (face == 1)] = (14, 14, 26); col[m & (face == 2)] = (104, 86, 116); col[m & (face == 3)] = (60, 50, 72)
    out = base.copy(); hit = what != ''; out[hit] = col[hit]
    img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
    if 'booth' in L:
        b = L['booth']; x0_, y0_ = P(b[0] + 0.05, 2.25, b[4]); x1_, y1_ = P(b[1] - 0.05, 1.93, b[4])
        paste_box(img, sign, (x0_, y0_, x1_, y1_))
    g = L['glass']; x0_, y0_ = P(g[0], g[3], g[4]); x1_, y1_ = P(g[1], g[2], g[4])
    paste_box(img, ad, (x0_, y0_, x1_, y1_))
    for i, b in enumerate(L['mach']):
        zc_ = b[4] + 0.5; x_, y_ = P(b[1], 1.86, zc_); w_ = F * 0.15 / zc_; hh = F * 0.18 / zc_
        paste_box(img, shields[i], (x_ - w_ / 2, y_ - hh / 2, x_ + w_ / 2, y_ + hh / 2))
    return img


def paste_box(img, src, b):
    x0, y0, x1, y1 = [(b[0] - CROP[0]) * K, (b[1] - CROP[1]) * K, (b[2] - CROP[0]) * K, (b[3] - CROP[1]) * K]
    w, h = int(round(x1 - x0)), int(round(y1 - y0))
    if w < 2 or h < 2: return
    s = src.convert('RGBA').resize((w, h), Image.LANCZOS)
    img.paste(s, (int(round(x0)), int(round(y0))), s)


def top_view(v, scale=60):
    """The layout from above: X across, Z along; the rays of a few columns; the volumes, named."""
    L = layout(v)
    xr, zr = (-8.4, -3.4), (16.8, 25.0)
    W, H = int((xr[1] - xr[0]) * scale), int((zr[1] - zr[0]) * scale)
    im = Image.new('RGB', (W + 240, H + 40), (250, 250, 248)); d = ImageDraw.Draw(im)
    T = lambda X, Z: ((X - xr[0]) * scale + 10, H - (Z - zr[0]) * scale + 30)
    for z in np.arange(17, 25.01, 1):
        d.line([T(xr[0], z), T(xr[1], z)], fill=(228, 228, 228)); d.text((W + 14, T(0, z)[1] - 5), 'Z %.0f m' % z, fill=(120, 120, 120))
    for x in (225, 290, 330, 360, 390):
        d.line([T((x - VX) * zr[0] / F, zr[0]), T((x - VX) * zr[1] / F, zr[1])], fill=(205, 205, 235))
        d.text(T((x - VX) * zr[0] / F - 0.1, zr[0] + 0.1), 'x %d' % x, fill=(150, 150, 200))
    d.line([T(XH, zr[0]), T(XH, 18.63)], fill=(140, 90, 40), width=3); d.text(T(XH - 1.3, 17.6), 'dagashi-ya', fill=(140, 90, 40))
    d.line([T(XH, 18.63), T(XH, ZC)], fill=(40, 40, 130), width=3); d.line([T(XH, ZC), T(XH - 1.2, ZC)], fill=(40, 40, 130), width=3)
    d.text(T(XH - 1.55, 21.0), "Kirua's house", fill=(40, 40, 130)); d.text(T(XH - 1.2, ZC + 0.15), 'its corner', fill=(40, 40, 130))
    C = L['canopy']; d.rectangle([T(XH, C['z1']), T(XH + C['proj'], C['z0'])], outline=(120, 120, 120), width=1)
    d.text(T(XH + C['proj'] + 0.05, C['z1'] - 0.25), 'canopy (2.32-2.62 m)', fill=(110, 110, 110))
    if 'booth' in L:
        b = L['booth']; d.rectangle([T(b[0], b[5]), T(b[1], b[4])], outline=(160, 30, 40), width=2, fill=(242, 214, 214))
        d.text(T(b[1] + 0.06, b[4] + 0.35), 'tabako booth', fill=(160, 30, 40))
    names = ('Speed Cola', 'Double Tap', 'Juggernog'); cols = ((40, 130, 70), (170, 105, 40), (170, 40, 40))
    for i, b in enumerate(L['mach']):
        d.rectangle([T(b[0], b[5]), T(b[1], b[4])], outline=cols[i], width=2, fill=tuple(int(c * 0.3 + 175) for c in cols[i]))
        d.text(T(b[1] + 0.06, b[4] + 0.42), names[i], fill=cols[i])
    if 'screen' in L:
        s = L['screen']; d.rectangle([T(s[0], s[5]), T(s[1], s[4])], fill=(60, 160, 150)); d.text(T(XH - 1.95, s[4] - 0.1), 'ad sign, 2.95-3.95 m', fill=(40, 120, 110))
    if v == 'B':
        m = L['mach'][0]; d.line([T(m[0], m[4]), T(m[1], m[4])], fill=(60, 200, 190), width=4); d.text(T(m[1] + 0.06, m[4] - 0.25), 'ad panel', fill=(40, 140, 130))
    d.text((12, 6), 'Layout %s, from above (camera at X 0, Z 0, far below; F 1400, eye 1.5 m)' % v, fill=(0, 0, 0))
    return im


def lines(v, img, k=3, bx=(200, 380, 420, 760)):
    """The volumes' edges over a crop of the street, k times larger."""
    L = layout(v)
    im = img.crop(bx).resize(((bx[2] - bx[0]) * k, (bx[3] - bx[1]) * k), Image.NEAREST).convert('RGB'); d = ImageDraw.Draw(im)
    T = lambda X, Y, Z: ((P(X, Y, Z)[0] - bx[0]) * k, (P(X, Y, Z)[1] - bx[1]) * k)

    def box(b, col):
        X0, X1, Y0, Y1, Z0, Z1 = b
        for a_, b_ in [((X0, Y0, Z0), (X1, Y0, Z0)), ((X1, Y0, Z0), (X1, Y1, Z0)), ((X1, Y1, Z0), (X0, Y1, Z0)), ((X0, Y1, Z0), (X0, Y0, Z0)),
                       ((X1, Y0, Z0), (X1, Y0, Z1)), ((X1, Y1, Z0), (X1, Y1, Z1)), ((X1, Y0, Z1), (X1, Y1, Z1)), ((X0, Y1, Z0), (X0, Y1, Z1))]:
            d.line([T(*a_), T(*b_)], fill=col, width=1)
    if 'booth' in L: box(L['booth'], (255, 80, 80))
    for i, b in enumerate(L['mach']): box(b, ((80, 255, 120), (255, 180, 60), (255, 60, 60))[i])
    if 'screen' in L: box(L['screen'], (80, 240, 240))
    C = L['canopy']; xe = XH + C['proj']; ye = C['y_wall'] - C['pitch'] * C['proj']
    for z in (C['z0'], C['z1']): d.line([T(XH, C['y_wall'], z), T(xe, ye, z)], fill=(255, 255, 255))
    d.line([T(xe, ye, C['z0']), T(xe, ye, C['z1'])], fill=(255, 255, 255)); d.line([T(XH, C['y_wall'], C['z0']), T(XH, C['y_wall'], C['z1'])], fill=(255, 255, 255))
    d.line([T(XH, 0, 18.63), T(XH, 0, ZC)], fill=(130, 130, 255)); d.line([T(XH, 0, ZC), T(XH, 4.2, ZC)], fill=(130, 130, 255))
    return im


# ---------------------------------------------------------------- the takes, on the street ----

def sat(T):
    S = np.zeros((T.shape[0] + 1, T.shape[1] + 1) + T.shape[2:])
    S[1:, 1:] = T.cumsum(0).cumsum(1)
    return S


def lerp_axis(S, t, axis):
    t = np.clip(t, 0, S.shape[axis] - 1.000001); i = np.floor(t).astype(int); f = t - i
    a, b = np.take(S, i, axis=axis), np.take(S, i + 1, axis=axis)
    sh = [1] * S.ndim; sh[axis] = -1; f = f.reshape(sh)
    return a * (1 - f) + b * f


def sample(S, fit, box, k=1):
    """The take (its summed-area table S) over box, k x k samples per street pixel: each the mean of the take's pixels
    over it (fit: s, ox, oy; sy if the take's rows are scaled apart; o, the street point its ox, oy are taken from: the
    crop it was made of, CROP if not given)."""
    s, ox, oy = fit['s'], fit['ox'], fit['oy']; sy = fit.get('sy', s); o = fit.get('o', CROP[:2])
    x0, y0, x1, y1 = box
    ex = (x0 - o[0] + np.arange((x1 - x0) * k + 1) / k) * s + ox
    ey = (y0 - o[1] + np.arange((y1 - y0) * k + 1) / k) * sy + oy
    A = lerp_axis(lerp_axis(S, ex, 1), ey, 0)
    return (A[1:, 1:] - A[:-1, 1:] - A[1:, :-1] + A[:-1, :-1]) / (s * sy / k / k)


def take(v, kind):
    return np.asarray(Image.open(os.path.join(SRC, 'soda_%s_%s.webp' % (v, kind))).convert('RGB')).astype(float)


def colours(rgb, M):
    return np.clip(rgb @ np.asarray(M)[:, :3].T + np.asarray(M)[:, 3], 0, 255)


def fit(v, ctx_path):
    """The takes' registration (on the 22 h render they were made from: their high frequencies outside the corner) and
    their colours' map (on the layer as it is, where the render shows it unlit)."""
    ctx = np.asarray(Image.open(ctx_path).convert('RGB')).astype(float)
    lay = np.asarray(Image.open(os.path.join(ROOT, 'assets', 'layer_city_off.webp')).convert('RGBA')).astype(float)
    x0, y0, x1, y1 = CROP
    ref = ctx[y0:y1, x0:x1]; lref = lay[y0:y1, x0:x1]
    X, Y = np.meshgrid(np.arange(x0, x1) + 0.5, np.arange(y0, y1) + 0.5)
    out = binary_dilation(region(X, Y) | ((X >= 255) & (X < 330) & (Y >= 410) & (Y < 520)), iterations=8)
    out |= (X < 140) | (X > 480) | (Y < 228) | (Y > 752)
    luma = lambda a: a @ [0.299, 0.587, 0.114]
    hp = lambda a: a - gaussian_filter(a, 2.0)
    R = hp(luma(ref)); w = ~out
    near = binary_dilation(region(X, Y), iterations=40)            # (the colours: only just round the corner)
    res = {}
    for kind in ('lit', 'off'):
        T = take(v, kind); S = sat(T); S1 = sat(luma(T))
        s0 = T.shape[1] / (x1 - x0)
        best = None
        for s in s0 * np.linspace(0.97, 1.03, 13):
            for ox in np.arange(-24, 25, 4.0):
                for oy in np.arange(-24, 25, 4.0):
                    a = hp(sample(S1, dict(s=s, ox=ox, oy=oy), CROP))
                    c = np.corrcoef(a[w], R[w])[0, 1]
                    if best is None or c > best[0]: best = (c, s, ox, oy)
        c, s, ox, oy = best
        for step in (1.0, 0.5, 0.25):
            for ds in (-0.004, -0.002, 0, 0.002, 0.004):
                for dx_ in (-2 * step, -step, 0, step, 2 * step):
                    for dy_ in (-2 * step, -step, 0, step, 2 * step):
                        a = hp(sample(S1, dict(s=s * (1 + ds), ox=ox + dx_, oy=oy + dy_), CROP))
                        cc = np.corrcoef(a[w], R[w])[0, 1]
                        if cc > c: c, s, ox, oy = cc, s * (1 + ds), ox + dx_, oy + dy_
        f = dict(s=round(float(s), 4), ox=round(float(ox), 2), oy=round(float(oy), 2))
        rgb = sample(S, f, CROP)
        same = w & near & (np.abs(ref - lref[..., :3]).max(2) <= 6) & (lref[..., 3] > 250)
        same &= np.abs(luma(rgb) - luma(ref)) < 12                     # (what the take left as it was)
        A_ = np.concatenate([rgb[same], np.ones((same.sum(), 1))], 1); B_ = lref[..., :3][same]
        if kind == 'lit':                      # (the off take, an edit of the lit one, takes the lit one's map)
            M = np.zeros((3, 4)); st = []      # (one gain, the spreads' ratio, so that whites stay white; an offset per
            for ch in range(3):                # channel, from the means: the street just round the corner as the take
                a_, b_ = np.sort(A_[:, ch]), np.sort(B_[:, ch])          # has it and as the layer has it, their
                n5 = len(a_) // 20; st.append((a_[n5:-n5], b_[n5:-n5]))  # tails trimmed)
            g_ = float(np.mean([b_.std() / a_.std() for a_, b_ in st]))
            for ch, (a_, b_) in enumerate(st): M[ch, ch], M[ch, 3] = g_, b_.mean() - g_ * a_.mean()
        f['M'] = [[round(float(q), 4) for q in r] for r in M]
        res[kind] = f
        print(kind, 'corr %.3f' % c, f, 'colour fit on', int(same.sum()), 'px, rms %.1f' % np.sqrt(((A_ @ M.T - B_) ** 2).mean()))
    print('FIT[%r] = %s' % (v, json.dumps(res)))
    return res


# ---------------------------------------------------------------- the zone ----

def mask(v, box=BOX):
    """What the zone lays: the area, less the bench and its lamp past the machines (under the canopy's end, kept) and
    the sidewalk under the things' feet (kept: one pixel of their shade under them)."""
    what, face, zb, dx, dy, X, Y = cast(v, box)
    L = layout(v)
    m = region(X, Y)
    xfar = P(L['mach'][2][1], 0, L['mach'][2][5])[0]
    yeave = P(XH + L['canopy']['proj'], L['canopy']['y_wall'] - L['canopy']['pitch'] * L['canopy']['proj'], L['mach'][2][5])[1]
    m &= ~((X > xfar + 1) & (Y > yeave + 4) & (what != 'canopy'))
    things = (what != '') & (what != 'wall')
    low = np.zeros(m.shape, bool)
    for j in range(m.shape[1]):
        col = np.where(things[:, j] | (what[:, j] == 'wall'))[0]
        if len(col): low[col.max() + 2:, j] = True
    return m & ~low, what, face


# ---------------------------------------------------------------- B as chosen: the house's boards, the canopy from
# below, the giant screen (the owner: "façade avec la fenêtre remplacée par écran géant", "juste au-dessus, pas la baie
# de Kirua", "le truc sous les tuiles : bleu-vert clair, va pas jusqu'au bout", "garde le panneau de pub côté") ----
BOARD_C = 0.013978                             # the painter's boards: one every BOARD_C (700 - x) pixels down a column
PIPE = (326, 331)                              # his downpipe's columns, at the house's corner
BOARD_CLEAR = 240                              # (left of this, his boards over the flashing hide behind the leaves)
WALL_SRC = 16                                  # (the old lean-to's shade over its flashing: so many pixels high)
WALL_SHADE = (0.62, 0.8)                       # (the wall in the canopy's shade, under the screen box's foot)
# the house's front (the owner: "tout ça c'est le même bâtiment, donc censé être identique"): one face from the dagashi-ya
# to the downpipe, from under Kirua's bay (its sill's lit edge on the ray through FACE_SILL, the sill two rows, its
# shadow under it FACE_SILL_SH, rows) down to the canopy, behind the screen. Its boards the painter's over the dagashi-ya
# (his wide planks, one every FACE_P m, the clean band from his lap line at FACE_Y0 m up two planks, over the columns
# FACE_SRC, under the tree's leaves and over the sign; the upper plank's top FACE_TOP m, where the leaves come down, and
# a leaf in it taken from the lower one), carried along their own lines at their own height (the planks alternating
# between his two, each along his columns from its own place: their joints staggered);
# left of the zone, behind the tree, its boards seen between the leaves the same (FACE_LEFT, a zone of its own);
# then (the owner: "uniforme comme le haut : clair plutôt, pour l'écran géant") the face round the screen in the light
# tone of his boards higher up: his pair of boards just under the bay's sill (FACE_UP: so many rows under its line; his
# columns left of FACE_UP[1], where the tree's leaves come down, taken to and fro from there) carried down along their
# lines over the whole face to the canopy and behind the tree's leaves, one tone, no fall-off (upper_boards()); in the
# street's low-sun mask as those boards are (street_sun.webp, sun_mask(): FACE_UP[2]), so every hour grades them alike;
# over the dagashi-ya too (the owner, of what was left there: "c'est surtout sombre, pas propre"): all the face that
# shows from its left post (FACE_POST) down to its sign's top (FACE_SIGN) and up behind the tree, his boards and his
# dusk-lit pink between the leaves alike, with his dark joints, his edge line and his dirt on them (face_left_sel(),
# FACE_BOARDS); only the tree's leaves in front kept as he drew them, clumps whole (in the zone: darker than FACE_LEAF,
# and as he drew them just past its edge, FACE_TREE); his columns brought to the tone of his unshaded ones (FACE_TONE),
# so the face is one tone; the tree's shade on his boards over the shop softened (FACE_SHADE: the owner, "s'il y a de l'ombre ok, mais là pas de raison
# autant"); only real light on it: the canopy's shade, the screen box's foot, the sill's shadow, and the screen's own
# light (its comp)
FACE_X = (227, 326)                            # (its columns: from the zone's edge to his downpipe)
FACE_SILL = (312, 376, 212, 314)               # (the sill's lit edge at a column, its row; its two ends)
FACE_LEFT = (138, 300, 227, 496)               # (the face left of the zone, behind the tree: zone 'sodaface'; what of it
                                               #  shows, face_left_sel(): his dusk-lit pink, FACE_PINK: R over B, luminance)
FACE_PINK = (8, 25)
FACE_BOARDS = (16, 3, 2, 30, 6, 5)             # (his boards between the leaves: lighter than [0], in areas of [3] px or
                                               #  more once specks under [1] px across are opened away, grown back [2] px;
                                               #  the dark between two of them over [5] rows or fewer (his joints), holes in
                                               #  them under [4] px (his dirt): the face too; the rest his leaves)
FACE_POST = (145, 466)                         # (the dagashi-ya's left post, its face and its side: left of x, from row on)
FACE_SIGN = ((138, 484), (160, 489), (182, 494), (226, 500))   # (his sign's top over the shop: the face stops on it)
FACE_SILL_SH = (0.55, 0.8)
FACE_Y0, FACE_P, FACE_TOP = 3.06, 0.197, 0.03
FACE_SRC = (186, 225)
FACE_TONE = (206, 225, 4.0, (0.8, 1.6))        # (his unshaded columns, whose tone the carried boards take; the columns'
                                               #  tones smoothed over so many; the gain's bounds)
FACE_SHADE = (0.3, 3.0, 3.9, 10)               # (the tree's shade on his boards over the shop: so much of it kept, between
                                               #  these heights (m), fading in from the zone's edge over so many px)
FACE_TREE = (231, 400, 434)                    # (the tree's leaves past the zone's edge, as he drew them: left of x, rows)
FACE_FADE = 1
FACE_UP = (4, 240, 255)
FACE_LEAF = 16
SCREEN_INSET = 0.07                            # its frame's width (m)
SCREEN_GLOW = (2, 1.0, 0.5)                    # its light round it: so many pixels out, falling off over so many; what
                                               #  it adds, times the surface's own colour and its light's (0..1): a rim on
                                               #  its frame's inner edge only, none on the boards (the owner: "sombre
                                               #  direct, pas de dégradé")
WOOD = dict(fascia=(64, 46, 50), fascia_lit=(104, 82, 84), soffit=(30, 24, 32), rafter=(48, 37, 45),
            rafter_lit=(66, 52, 60), end=(50, 37, 43), end_lit=(92, 72, 76), tile=(64, 68, 90), tile_rim=(126, 126, 150),
            bracket=(54, 39, 43))
SCREEN_C = dict(frame=(34, 36, 50), frame_lit=(86, 88, 110), side=(24, 26, 38), under=(17, 19, 29), glass=(11, 13, 21),
                bolt=(120, 122, 138))


def painter_boards(city, box, sel):
    """The painter's boards where sel (over box; city the whole layer): his boards as they are round Kirua's bay, lit by
    the dusk (the two just over the dark band the old lean-to's shade left above its flashing, WALL_SRC), a whole
    number of pairs of boards lower down each column (the plane's lines all run to VP, so a board's height in pixels is
    BOARD_C (700 - x)): his pixels, his tone, his grain, one tone over the plane (R29). By the dagashi-ya's edge his
    boards hide behind the tree's leaves: there, the same boards a few pixels further along their own lines."""
    x0, y0 = box[:2]
    out = np.zeros(sel.shape + (3,))
    ys, xs = np.nonzero(sel)
    X = xs + x0 + 0.5; Y = ys + y0 + 0.5
    Xs = np.where(X < BOARD_CLEAR, X + (BOARD_CLEAR - box[0]), X)
    Y = VY - (VY - Y) * (VX - Xs) / (VX - X)
    p = 2 * BOARD_C * (VX - Xs); top = VY - FLASH * (VX - Xs) - WALL_SRC
    k = np.floor((Y - top) / p) + 1
    yi = np.clip(np.floor(Y - k * p).astype(int), 0, city.shape[0] - 1)
    out[ys, xs] = city[yi, np.clip(np.floor(Xs).astype(int), 0, city.shape[1] - 1), :3]
    return out


def face_boards(city, box, sel):
    """The dagashi-ya's boards where sel (over box; city the whole layer as the zones before it leave it): each pixel on
    the house's plane (X = XH) at its height Y, the same height in his clean band (FACE_Y0 + its place in its plank),
    the planks alternating between his two (the upper one's top, where his leaves come down, the lower one's), each
    plank along his columns (FACE_SRC, to and fro) from its own place, so that his joints fall staggered as on a wall
    of boards."""
    x0, y0 = box[:2]
    out = np.zeros(sel.shape + (3,))
    ys, xs = np.nonzero(sel)
    x = xs + x0 + 0.5; y = ys + y0 + 0.5
    Z = F * -XH / (VX - x); Y = EYE + (VY - y) * Z / F
    w = FACE_SRC[1] - FACE_SRC[0] + 1
    k = np.floor((Y - FACE_Y0) / FACE_P); ph = (Y - FACE_Y0) - k * FACE_P
    off = np.floor((np.sin(k * 12.9898 + 4.1414) * 43758.5453 % 1.0) * 2 * w).astype(int)
    q = np.mod(np.floor(x - FACE_X[0]).astype(int) + off, 2 * w)
    xsrc = np.where(q < w, FACE_SRC[1] - q, FACE_SRC[0] + (q - w))       # (his columns to and fro: no seam)
    Zs = F * -XH / (VX - (xsrc + 0.5))
    row = lambda Ys: np.clip(np.floor(VY - F * (Ys - EYE) / Zs).astype(int), 0, city.shape[0] - 1)
    lo, hi = row(FACE_Y0 + ph), row(FACE_Y0 + FACE_P + ph)
    c_lo, c_hi = city[lo, xsrc, :3], city[hi, xsrc, :3]
    ok = (np.mod(k, 2) == 1) & (ph < FACE_P - FACE_TOP) & ((c_hi @ [0.299, 0.587, 0.114]) >= FACE_LEAF * 0.45)
    out[ys, xs] = np.where(ok[:, None], c_hi, c_lo) * face_gain(city)[xsrc - FACE_SRC[0], None]
    return out


def upper_boards(city, box, sel):
    """His boards just under the bay's sill where sel (over box; city the whole layer as the zones before it leave it):
    each pixel at its height on the house's plane, in his pair of boards FACE_UP[0] rows under the sill's line in its
    column (left of FACE_UP[1], one of his columns from there to the downpipe, to and fro, at the same height), a whole
    number of pairs away."""
    x0, y0 = box[:2]
    out = np.zeros(sel.shape + (3,))
    ys, xs = np.nonzero(sel)
    X = xs + x0 + 0.5; Y = ys + y0 + 0.5
    w = FACE_X[1] - 1 - FACE_UP[1]; q = np.mod(FACE_UP[1] - X, 2 * w)       # (left of FACE_UP[1]: his columns to and fro)
    Xs = np.where(X < FACE_UP[1], FACE_UP[1] + np.where(q < w, q, 2 * w - q), X)
    Ys = VY - (VY - Y) * (VX - Xs) / (VX - X)
    top = VY - (VY - FACE_SILL[1]) * (VX - Xs) / (VX - FACE_SILL[0]) + FACE_UP[0]
    p = 2 * BOARD_C * (VX - Xs)
    yi = np.clip(np.floor(Ys - np.floor((Ys - top) / p) * p).astype(int), 0, city.shape[0] - 1)
    out[ys, xs] = city[yi, np.clip(np.floor(Xs).astype(int), 0, city.shape[1] - 1), :3]
    return out


def face_tone(city):
    """His band's tone column by column (FACE_SRC: their mean luminance over his two planks, his leaves left out,
    smoothed over FACE_TONE[2] columns) and the tone of his unshaded columns (FACE_TONE)."""
    from scipy.ndimage import gaussian_filter1d
    xs = np.arange(FACE_SRC[0], FACE_SRC[1] + 1)
    Zs = F * -XH / (VX - (xs + 0.5))
    Ys = np.arange(FACE_Y0, FACE_Y0 + 2 * FACE_P - FACE_TOP, 0.004)
    rows = np.clip(np.floor(VY - F * (Ys[:, None] - EYE) / Zs[None, :]).astype(int), 0, city.shape[0] - 1)
    L = city[rows, xs[None, :], :3] @ [0.299, 0.587, 0.114]
    m = np.array([L[:, j][L[:, j] >= FACE_LEAF * 0.45].mean() for j in range(len(xs))])
    m = gaussian_filter1d(m, FACE_TONE[2], mode='nearest')
    return m, m[FACE_TONE[0] - FACE_SRC[0]:FACE_TONE[1] - FACE_SRC[0] + 1].mean()


def face_gain(city):
    """The gain that brings each of his columns to the tone of his unshaded ones (bounded: FACE_TONE[3])."""
    m, t = face_tone(city)
    return np.clip(t / m, *FACE_TONE[3])


def canopy_paint(v, box, ss=3):
    """The canopy as one sees it from the sidewalk, under it (layout v): its soffit's boards between the rafters, the
    wooden fascia along its whole eave with the round tile ends over it, its near end cut, three knee braces to the
    wall. Returns its colour over box and its coverage (0..1)."""
    L = layout(v); C = L['canopy']; xe = XH + C['proj']
    yt = lambda X_: C['y_wall'] - C['pitch'] * (X_ - XH)
    dx, dy, X, Y = rays(box, ss)
    zc, part = canopy_hit(dx, dy, C)
    Xw, Yw, Zw = dx * zc, EYE + dy * zc, zc
    col = np.zeros(dx.shape + (3,)); hit = np.isfinite(zc)
    W = {k_: np.array(c_, float) for k_, c_ in WOOD.items()}
    with np.errstate(invalid='ignore'):
        s1 = hit & (part == 1)                                   # the soffit: rafters every 0.3 m, boards between
        r = ((Zw - C['z0']) / 0.30) % 1.0
        col[s1] = np.where((r[s1] < 0.17)[:, None], np.where((r[s1] < 0.05)[:, None], W['rafter_lit'], W['rafter']), W['soffit'])
        shade = np.clip((Xw - XH) / C['proj'], 0, 1)[..., None] * 0.35 + 0.65       # (darker into the wall)
        col = np.where(s1[..., None], col * shade, col)
        s2 = hit & (part == 2)                                   # the fascia: its top edge lit, a joint every 1.8 m
        ytop = yt(xe)
        col[s2] = np.where(((ytop - Yw) < 0.018)[s2][:, None], W['fascia_lit'], W['fascia'])
        joint = s2 & (((Zw - C['z0']) / 1.8) % 1.0 < 0.012)
        col[joint] = W['fascia'] * 0.7
        s3 = hit & (part == 3)                                   # its near end: the cut, lit along its top
        col[s3] = np.where(((yt(Xw) - Yw) < 0.02)[s3][:, None], W['end_lit'], W['end'])
    # the round tile ends along the eave, a little proud of the fascia
    with np.errstate(divide='ignore', invalid='ignore'):
        zt_ = (xe + 0.02) / dx
    yt_ = EYE + dy * zt_
    kk = np.floor((zt_ - C['z0']) / C['tile']); zc_ = C['z0'] + (kk + 0.5) * C['tile']; yc_ = yt(xe) + 0.012
    rr = np.hypot(zt_ - zc_, (yt_ - yc_) * 1.0)
    tiles = (rr < 0.05) & (zt_ > C['z0']) & (zt_ < C['z1']) & (zt_ < np.where(hit, zc, np.inf) + 0.05)
    col[tiles] = np.where(((yt_ - yc_) > 0.022)[tiles][:, None], W['tile_rim'], W['tile'])
    cov = hit | tiles
    # three knee braces from the wall, under the soffit
    zb_all = np.full(dx.shape, np.inf)
    for zb in (C['z0'] + 0.4, (C['z0'] + C['z1']) / 2, C['z1'] - 0.4):
        Xb, Yb = dx * zb, EYE + dy * zb
        a = np.array([XH, 2.08]); b = np.array([XH + 0.62, yt(XH + 0.62) - C['th']])
        t_ = np.clip(((Xb - a[0]) * (b[0] - a[0]) + (Yb - a[1]) * (b[1] - a[1])) / ((b - a) ** 2).sum(), 0, 1)
        d_ = np.hypot(Xb - (a[0] + t_ * (b[0] - a[0])), Yb - (a[1] + t_ * (b[1] - a[1])))
        on = (d_ < 0.03) & (zb < np.where(cov, zc, np.inf)) & (zb < zb_all)
        col[on] = np.where((Yb - (a[1] + t_ * (b[1] - a[1])) > 0.012)[on][:, None], W['rafter_lit'], W['bracket'])
        zb_all = np.where(on, zb, zb_all); cov = cov | on
    h, w = box[3] - box[1], box[2] - box[0]
    c_ = cov.reshape(h, ss, w, ss).mean((1, 3))
    rgb = (col * cov[..., None]).reshape(h, ss, w, ss, 3).sum((1, 3)) / np.maximum(c_[..., None] * ss * ss, 1)
    return rgb, c_


def screen_paint(v, box, ss=3):
    """The giant screen's box on the house (layout v): its frame on the front (a lit top edge, four bolts), its near
    side and its underside, its glass dark. Returns the colour over box, its coverage, and for the glass's sub-pixels
    (u along it from its near end, w down it) to lay the pictures in."""
    L = layout(v); b = L['bigscreen']; I = SCREEN_INSET
    dx, dy, X, Y = rays(box, ss)
    z, f = ray_box(dx, dy, b)
    hit = np.isfinite(z)
    Xw, Yw, Zw = dx * z, EYE + dy * z, z
    S = {k_: np.array(c_, float) for k_, c_ in SCREEN_C.items()}
    col = np.zeros(dx.shape + (3,))
    front = hit & (f == 1)
    glass = front & (Zw > b[4] + I) & (Zw < b[5] - I) & (Yw > b[2] + I) & (Yw < b[3] - I)
    frame = front & ~glass
    col[frame] = np.where(((b[3] - Yw) < 0.02)[frame][:, None], S['frame_lit'], S['frame'])
    for zz in (b[4] + I / 2, b[5] - I / 2):
        for yy in (b[2] + I / 2, b[3] - I / 2):
            bolt = frame & (np.hypot(Zw - zz, Yw - yy) < 0.022)
            col[bolt] = S['bolt']
    col[hit & (f == 4)] = S['side']; col[hit & (f == 2)] = S['under']
    u = (Zw - b[4] - I) / (b[5] - b[4] - 2 * I); w_ = (b[3] - I - Yw) / (b[3] - b[2] - 2 * I)
    refl = np.zeros(dx.shape + (1,))                                         # (a faint sheen on the dark glass)
    refl[glass] = np.clip(1 - (u[glass] + w_[glass]) * 0.6, 0, 1)[:, None] * 8.0
    col[glass] = (S['glass'] + refl)[glass]
    h, wd = box[3] - box[1], box[2] - box[0]
    c_ = hit.reshape(h, ss, wd, ss).mean((1, 3))
    rgb = (col * hit[..., None]).reshape(h, ss, wd, ss, 3).sum((1, 3)) / np.maximum(c_[..., None] * ss * ss, 1)
    g_ = glass.reshape(h, ss, wd, ss).mean((1, 3))
    return rgb, c_, (glass, u, w_), g_


def screen_frame(uvg, box, pic, ss=3, pal=None):
    """One picture (480 x 160) as the giant screen shows it, over box: laid in the glass in its perspective (sampled at the
    glass's sub-pixels), a few flat colours (its cut's palette, pal, when it has one), a fine LED row every other row, a
    little dimmed; and its mean light."""
    glass, u, w_ = uvg
    h, wd = box[3] - box[1], box[2] - box[0]
    im = pic.convert('RGB').resize((480, 160), Image.LANCZOS)
    im = (im.quantize(palette=pal, dither=Image.Dither.NONE) if pal is not None else im.quantize(colors=24, method=0, dither=0)).convert('RGB')
    A = np.asarray(im).astype(float); H_, W_ = A.shape[:2]
    smp = A[(np.clip(w_, 0, 0.9999) * H_).astype(int), (np.clip(u, 0, 0.9999) * W_).astype(int)]
    row = np.where((np.floor(np.clip(w_, 0, 1) * 54) % 2) == 1, 0.86, 1.0)[..., None]
    c = smp * row * 0.8 * glass[..., None]
    g_ = glass.reshape(h, ss, wd, ss).sum((1, 3))
    return c.reshape(h, ss, wd, ss, 3).sum((1, 3)) / np.maximum(g_[..., None], 1), c.sum((0, 1)) / max(glass.sum(), 1)


# ---------------------------------------------------------------- the two screens' loops (the owner: "pub rétro pour les
# 3 atouts, mode zombie de BO2, réf rétro"; "5-6 animations refs qui défilent aléatoirement") ----
# The giant screen plays short anime cuts in a random order (never the same twice running), a few frames of static
# between (the owner, then: "plus de framerate, plus fluide et propre, proche des vrais animes en termes de fidélité
# d'environnement ... remplace Totoro par Levi de SNK"; a sixth since, Goku's Kamehameha in Dragon Ball Z's wasteland, its
# sheet and prompt asked by ask_clip, laid over one landscape by CLIP_STEADY): each cut eight (or twelve) consecutive
# keyframes drawn by the image API in the anime's own look, the character on model in their world (tools/src/screen2_<name>.webp, a sheet of 3:1
# panels, SCREEN_CLIPS: its grid; a sheet of 2:1 panels its sides carried out to 3:1, 'pad'; the prompts in
# tools/src/soda_prompts.txt), played smooth here: each keyframe held CLIP_HOLD frames, an in-between to the next, the
# whole cut pushing in slowly (CLIP_PUSH), one palette for the whole cut so nothing flickers, at CLIP_FPS. To change what
# it shows: put a new sheet in tools/src/, list it in SCREEN_CLIPS, run the chain again; street.js gets the clips' sheets
# and their versions from here (ADS). The side panel: the three perks' ads (the owner: "plus proche du jeu et de la série
# Black Ops ... rien d'inventer comme la canette"): a 1950s-60s TV commercial each for Jugger-Nog, Speed Cola and Double
# Tap Root Beer as the Zombies mode has them (their machines and lettering, their glass bottles with the emblem's
# sticker, the emblems the site's own icons given as references), eight frames a perk (tools/src/screen2_perk_<p>.webp,
# PERK_SHEETS: their panels' columns and rows in the sheet), each held PERK_HOLD frames with a slight push in, a VHS look
# over all.
SCREEN_CLIPS = [('naruto', 'screen2_naruto.webp', (4, 2), None), ('luffy', 'screen2_luffy.webp', (4, 3), 'pad'),
                ('killua', 'screen2_killua.webp', (4, 2), None), ('pika', 'screen2_pika.webp', (4, 2), None),
                ('levi', 'screen2_levi.webp', (4, 2), None), ('goku', 'screen2_goku.webp', (4, 2), None)]
CLIP_FPS, CLIP_LOOPS, CLIP_HOLD, CLIP_PUSH = 10, 2, 2, 0.05   # (frames a second, plays before the next, frames a keyframe
                                                            #  is held, the push in over the cut)
CLIP_COLORS = 40                               # (the cut's palette)
STATIC_N, STATIC_FPS = 3, 12
PERK_SHEETS = [('jugg', 'screen2_perk_jugg.webp', ((40, 455), (492, 909), (946, 1364), (1401, 1818)), ((33, 1131), (1169, 2269))),
               ('speed', 'screen2_perk_speed.webp', ((40, 441), (500, 900), (959, 1360), (1418, 1819)), ((44, 1026), (1184, 2170))),
               ('tap', 'screen2_perk_tap.webp', ((37, 464), (489, 916), (939, 1366), (1391, 1818)), ((28, 1136), (1167, 2254)))]
PERK_HOLD, PERK_FPS = 2, 8


def ask_clip(name, redo=None):
    """Asks the image API for a cut's sheet (python3 tools/soda_corner.py --ask-clip NAME [PANEL]): its prompt
    tools/src/edits/screen2_NAME_prompt.txt; the answer saved as tools/src/screen2_NAME.webp (lossless), as SCREEN_CLIPS
    reads it. With PANEL (1-8): that one keyframe redrawn in the sheet already there (its prompt
    screen2_NAME_redo_prompt.txt, the sheet given as the image; the answer screen2_NAME_redo.webp, its panel taken by
    CLIP_STEADY's 'redo'). With 'plate': the cut's first keyframe twice, one over the other, the lower one asked without
    the character (its prompt screen2_NAME_plate_prompt.txt, the input kept as tools/src/edits/screen2_NAME_plate_in.webp,
    the answer screen2_NAME_plate.webp): the landscape behind him, for the shared background (steady_keys)."""
    import base64, io, urllib.request
    k = os.environ.get('OPENROUTER_API_KEY') or open(os.path.expanduser('~/.config/openrouter/key')).read().strip()
    out = os.path.join(SRC, 'screen2_%s.webp' % name)
    tag = '' if not redo else ('_plate' if redo == 'plate' else '_redo')
    body = {'model': 'openai/gpt-5.4-image-2', 'aspect_ratio': '3:2', 'quality': 'high', 'n': 1, 'output_format': 'png',
            'prompt': open(os.path.join(EDITS, 'screen2_%s%s_prompt.txt' % (name, tag))).read().strip()}
    if redo:
        src = Image.open(out).convert('RGB')
        if redo == 'plate':                    # (its first panel at 3:1, twice)
            p = grid_panels(out, *dict((n_, g_) for n_, _, g_, _ in SCREEN_CLIPS)[name])[0].resize((1536, 512), Image.LANCZOS)
            src = Image.new('RGB', (1536, 1024)); src.paste(p, (0, 0)); src.paste(p, (0, 512))
            src.save(os.path.join(EDITS, 'screen2_%s_plate_in.webp' % name), 'WEBP', lossless=True, quality=100, method=6)
        buf = io.BytesIO(); src.save(buf, 'PNG')
        body['input_references'] = [{'type': 'image_url', 'image_url': {'url': 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()}}]
    req = urllib.request.Request('https://openrouter.ai/api/v1/images', data=json.dumps(body).encode(),
                                 headers={'Authorization': 'Bearer ' + k, 'Content-Type': 'application/json'})
    d = json.loads(urllib.request.urlopen(req, timeout=900).read())
    im = Image.open(io.BytesIO(base64.b64decode(d['data'][0]['b64_json']))).convert('RGB')
    im.save(out.replace('.webp', tag + '.webp'), 'WEBP', lossless=True, quality=100, method=6)
    print(name, im.size, 'cost', d.get('usage', {}).get('cost'), '$')


def sheet_panels(path, rows, cols=1, dark=40):
    """The panels of a sheet separated by dark gaps (rows x cols), top to bottom, left to right."""
    im = Image.open(path).convert('RGB'); a = np.asarray(im).astype(float).mean(2)

    def runs(prof, n):
        on = prof > dark; segs, st = [], None
        for i, o in enumerate(on):
            if o and st is None: st = i
            if not o and st is not None: segs.append((st, i)); st = None
        if st is not None: segs.append((st, len(on)))
        segs = [s_ for s_ in segs if s_[1] - s_[0] > len(prof) / (n * 3)]
        return sorted(sorted(segs, key=lambda s_: s_[0] - s_[1])[:n], key=lambda s_: s_[0])
    out = []
    for r0, r1 in runs(a.mean(1), rows):
        for c0, c1 in runs(a[r0:r1].mean(0), cols):
            out.append(im.crop((c0, r0, c1, r1)))
    return out


def grid_panels(path, rows, cols, dark=30):
    """The panels of a sheet laid out rows x cols, top to bottom, left to right: its gaps the runs of rows (columns) whose
    brightest pixels stay dark, the one nearest each even division taken (a dark picture's own dark runs left alone)."""
    im = Image.open(path).convert('RGB'); a = np.asarray(im).astype(float).mean(2)

    def cuts(prof, n, L):
        runs_, st = [], None
        for i, o in enumerate(prof < dark):
            if o and st is None: st = i
            if not o and st is not None: runs_.append((st, i)); st = None
        if st is not None: runs_.append((st, L))
        edges = [(0, 0)]
        for k in range(1, n):
            e = k * L / n
            near_ = [r for r in runs_ if abs((r[0] + r[1]) / 2 - e) < L / (4 * n)]
            edges.append(min(near_, key=lambda r: abs((r[0] + r[1]) / 2 - e)) if near_ else (int(e), int(e)))
        edges.append((L, L))
        lo = next((r[1] for r in runs_ if r[0] == 0), 0); hi = next((r[0] for r in runs_ if r[1] == L), L)
        spans = [(edges[k][1], edges[k + 1][0]) for k in range(n)]
        spans[0] = (max(spans[0][0], lo), spans[0][1]); spans[-1] = (spans[-1][0], min(spans[-1][1], hi))
        return [(a0 + 2, b0 - 2) for a0, b0 in spans]
    out = []
    for r0, r1 in cuts(np.percentile(a, 98, axis=1), rows, a.shape[0]):
        for c0, c1 in cuts(np.percentile(a, 98, axis=0), cols, a.shape[1]):
            out.append(im.crop((c0, r0, c1, r1)))
    return out


def clip_keys(file, grid, fit):
    """A sheet's keyframes, 480 x 160 each, in order: its panels (grid: rows, columns); 'pad': a 2:1 panel set in the 3:1
    frame, its sides carried out from its own edge columns, softened."""
    from scipy.ndimage import gaussian_filter
    keys = []
    for k in grid_panels(os.path.join(SRC, file), *grid):
        if fit == 'pad':
            w0 = int(round(k.width * 160 / k.height)); core = np.asarray(k.resize((w0, 160), Image.LANCZOS)).astype(float)
            pw = (480 - w0) // 2; out = np.zeros((160, 480, 3))
            out[:, pw:pw + w0] = core
            for side, sl, src in ((0, slice(0, pw), core[:, :1]), (1, slice(pw + w0, 480), core[:, -1:])):
                n_ = sl.stop - sl.start
                band = np.repeat(gaussian_filter(src, (2, 0, 0)), n_, 1)
                mir = core[:, :n_][:, ::-1] if side == 0 else core[:, -n_:][:, ::-1]
                t_ = np.linspace(0, 1, n_)[None, :, None]; t_ = t_[:, ::-1] if side == 0 else t_
                out[:, sl] = mir * (1 - t_) * 0.6 + band * (1 - (1 - t_) * 0.6)
            keys.append(Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)))
        else:
            keys.append(k.resize((480, 160), Image.LANCZOS))
    return keys


# ---------------------------------------------------------------- a cut over one landscape (the owner, on Goku's: its
# end cut to another shot, its wasteland shifting between keyframes): CLIP_STEADY lays a cut's figure and its light over
# one background plate, so the landscape never moves and the figure stays planted. plate: the landscape alone, asked of
# the image API from the cut's first keyframe (ask_clip NAME plate: its lower half); redo: keyframes taken from a sheet
# redrawn by the API instead (ask_clip NAME PANEL); keys: for each keyframe (480 x 160, its own pixels): bg, its landscape
# registered on the plate (a scale about the frame's centre and a move: the keyframe scaled by s, moved by d, matches the
# plate; measured on the edges round the figure), or None where the API redrew the landscape (the beam's two keyframes:
# the plate matched there by its tones only); fig, where the figure goes in the plate (the same kind of move: his legs
# registered on the first keyframe's, then all of them set where the second keyframe has him, the middle of his places);
# box, where the figure is (minus not); halo, how far round him his aura reaches (px: whole, then gone); glow: the light
# he sheds on the sky and the ground round him carried too; beam, air, dust, steam, spark: where the beam, the wind's
# streaks and the flying stones, the dust at his feet, the steam off his palms, the beam's last sparkles are.
CLIP_STEADY = {'goku': dict(
    plate='screen2_goku_plate.webp', redo=('screen2_goku_redo.webp', (8,)),
    keys={1: dict(bg=(1.0, 0.0, 0.0), fig=(0.976, -26.32, 1.98), box=(55, 0, 245, 158), halo=(2, 5)),
          2: dict(bg=(0.9925, 1.14, -0.66), fig=(1.0, 0.0, 0.0), box=(20, 0, 245, 158), halo=(28, 48)),
          3: dict(bg=(0.9925, 1.65, -0.80), fig=(1.02, -18.27, -1.66), box=(30, 0, 252, 160), halo=(28, 48)),
          4: dict(bg=(1.0075, 1.09, -0.96), fig=(0.995, -1.04, -0.17), box=(0, 0, 300, 160), halo=(28, 48), glow=1),
          5: dict(bg=(1.045, -2.00, 1.92), fig=(1.015, -20.22, 5.0), box=(0, 0, 312, 160), halo=(28, 48), glow=1),
          6: dict(bg=None, fig=(1.029, 30.97, 3.69), box=(15, 0, 178, 152), sky=72, beam=(160, 24, 480, 86), air=(0, 0, 140, 100)),
          7: dict(bg=None, fig=(1.029, 23.76, 13.98), box=(15, 0, 170, 150), sky=66, beam=(140, 12, 480, 80), air=(0, 0, 165, 100),
                  dust=(0, 92, 205, 160)),
          8: dict(bg=(0.99, -3.94, 1.81), fig=(1.029, 22.73, -2.49), box=(10, 0, 182, 158), not_=(0, 0, 52, 108),
                  halo=(2, 5), steam=(150, 30, 205, 82), spark=(190, 6, 480, 80))})}


def steady_keys(name, keys):
    """A cut's keyframes (480 x 160) as CLIP_STEADY lays them: each one's figure and light (its matte: where it leaves
    the plate brought to its light, or, where its landscape was redrawn, the figure's colours, the beam's and the
    streaks' light over the sky, the dust's over the ground) moved to his place, over the plate in that keyframe's light
    (each channel's tones carried to the keyframe's own over the landscape round him)."""
    from scipy.ndimage import (map_coordinates, binary_closing, binary_opening, binary_fill_holes, binary_erosion, label,
                               median_filter, distance_transform_edt)
    S_ = CLIP_STEADY[name]; H, W = 160, 480
    YY, XX = np.mgrid[0:H, 0:W].astype(float)
    A = lambda im: np.asarray(im.convert('RGB')).astype(float)
    K = [A(k) for k in keys]
    rf, nums = S_['redo']
    for n_ in nums: K[n_ - 1] = A(clip_keys(rf, (4, 2), None)[n_ - 1])
    pl = Image.open(os.path.join(SRC, S_['plate'])).convert('RGB')
    C = A(pl.crop((0, pl.height // 2, pl.width, pl.height)).resize((W, H), Image.LANCZOS))

    def warp(a, t, mode='nearest'):          # (a scaled by s about the centre, then moved by d)
        s, dx, dy = t; xs = W / 2 + (XX - W / 2 - dx) / s; ys = H / 2 + (YY - H / 2 - dy) / s
        return np.dstack([map_coordinates(a[..., c], [ys, xs], order=1, mode=mode) for c in range(a.shape[2])])
    inv = lambda t: (1 / t[0], -t[1] / t[0], -t[2] / t[0])
    sm = lambda x, a, b: (lambda t_: t_ * t_ * (3 - 2 * t_))(np.clip((x - a) / (b - a), 0, 1))
    lum = lambda a: a @ np.array([0.299, 0.587, 0.114])

    def box(*bs):
        m = np.zeros((H, W), bool)
        for b in bs:
            if b: m[b[1]:b[3], b[0]:b[2]] = True
        return m

    def main(m):                             # (the biggest blob and what touches it, its holes filled)
        lab, n = label(m)
        if not n: return m
        sz = np.bincount(lab.ravel()); sz[0] = 0
        return binary_fill_holes(np.isin(lab, np.unique(lab[binary_dilation(lab == sz.argmax(), iterations=2) & (lab > 0)])))

    def lmd(a, b):                           # (the nearest colour of b within a pixel, per pixel)
        return np.min([np.sqrt(((a - np.roll(b, (dy, dx), (0, 1))) ** 2).sum(2)) for dy in (-1, 0, 1) for dx in (-1, 0, 1)], 0)

    def tones(P, Kk, m):                     # (each channel's tones of P carried to Kk's, over m)
        q = np.linspace(0, 100, 41)
        return lambda X: np.dstack([np.interp(X[..., c], np.percentile(P[..., c][m], q), np.percentile(Kk[..., c][m], q)) for c in range(3)])
    # the figure's colours (a histogram's odds): his pixels in the first keyframe and the redrawn last, the landscape's
    # round him and in the beam's light
    cfg = S_['keys']; B_ = 16
    idx = lambda a: (lambda q: q[..., 0] * B_ * B_ + q[..., 1] * B_ + q[..., 2])(np.clip((a / 256 * B_).astype(int), 0, B_ - 1))
    fg = np.zeros(B_ ** 3); bgh = np.zeros(B_ ** 3)
    for k in (1, 8):
        c = cfg[k]; Pk = warp(C, inv(c['bg'])); D = lmd(K[k - 1], Pk)
        f = binary_erosion(binary_fill_holes(binary_closing((D > 60) & box(c['box']) & ~box(c.get('not_')), iterations=2)))
        fg += np.bincount(idx(K[k - 1])[f], minlength=B_ ** 3); bgh += np.bincount(idx(K[k - 1])[(D < 25) | ~box(c['box'])], minlength=B_ ** 3)
    for k, b in ((6, (240, 84, 480, 160)), (7, (240, 72, 480, 160)), (6, (60, 0, 90, 12)), (7, (240, 150, 480, 160))):
        bgh += 3 * np.bincount(idx(K[k - 1])[box(b)], minlength=B_ ** 3)
    fg = gaussian_filter(fg.reshape((B_,) * 3), 0.7).ravel() / fg.sum(); bgh = gaussian_filter(bgh.reshape((B_,) * 3), 0.7).ravel() / bgh.sum()
    odds = fg / (fg + bgh + 1e-9)
    # the plate's sky alone (its mesas and ground the sky of their row): what the beam's light is measured over
    sky = (C[..., 2] > C[..., 0] + 60) & (C[..., 2] > 150); Sk = C.copy()
    for y in range(H): Sk[y, ~sky[y]] = np.median(C[y][sky[y]], 0) if sky[y].sum() > 20 else Sk[y - 1, ~sky[y]].mean(0)
    Sk = gaussian_filter(Sk, (2, 6, 0))
    out = []
    for k in range(1, len(K) + 1):
        c = cfg[k]; Kk = K[k - 1]; reg = c['bg'] or (1.0, 0.0, 0.0)
        Pk = warp(C, inv(reg)); Sky = warp(Sk, inv(reg))
        parts = [c[n_] for n_ in ('beam', 'air', 'dust', 'steam', 'spark') if n_ in c]
        far = ~binary_dilation(box(c['box'], *parts), iterations=3) & (XX > 4) & (XX < W - 5)
        tn = tones(Pk, Kk, far); PG = tn(Pk); SG = tn(Sky)
        od = odds[idx(Kk)] > (0.6 if c['bg'] else 0.45)
        if not c['bg']:                      # (and, over his sky, whatever leaves it: his arms, his face in the beam's light)
            od |= (np.sqrt(((Kk - SG) ** 2).sum(2)) > 45) & (YY < c['sky'])
        core = main(binary_closing(od & box(c['box']) & ~box(c.get('not_')), iterations=1))
        glow = np.zeros((H, W, 3))
        if c['bg']:
            D = lmd(Kk, PG)
            core = main(core | (binary_closing(D > 45, iterations=2) & box(c['box']) & ~box(c.get('not_'))))
            near = 1 - sm(distance_transform_edt(~core), *c['halo'])
            a = np.maximum(sm(D, 28, 56) * box(c['box']) * near, sm(D, 28, 56) * box(c.get('steam')))
            if c.get('glow'):                # (the light he sheds, round his aura)
                glow = np.clip(gaussian_filter(Kk, (3, 3, 0)) - gaussian_filter(PG, (3, 3, 0)), 0, None) * \
                    (1 - sm(distance_transform_edt(~core), c['halo'][0] + 20, c['halo'][1] + 50))[..., None]
            if 'spark' in c:                 # (small bright points on the sky)
                lk = lum(Kk); md = median_filter(lk, 9)
                sp = (lk - md > 40) & (md < 150) & (Kk[..., 2] > 200) & box(c['spark']) & (warp(sky[..., None].astype(float), inv(reg))[..., 0] > 0.5)
                lab, n = label(binary_dilation(sp)); sz = np.bincount(lab.ravel()); sz[0] = 0
                a = np.maximum(a, np.clip(gaussian_filter(np.isin(lab, np.nonzero((sz > 0) & (sz < 30))[0]).astype(float), 0.6) * 1.6, 0, 1))
        else:
            ex = lum(Kk) - lum(SG); air = box(c['air']) & (YY < 118) & ~binary_dilation(core)
            a = np.maximum(core.astype(float), sm(ex, 14, 70) * box(c['beam']))
            a = np.maximum(a, sm(ex, 22, 70) * (binary_opening(ex > 22) & air))
            lab, n = label((-ex > 50) & air & (YY < 95)); sz = np.bincount(lab.ravel()); sz[0] = 0
            a = np.maximum(a, np.isin(lab, np.nonzero((sz > 2) & (sz < 40))[0]))      # (the stones flying)
            if 'dust' in c:
                ed = lum(Kk) - lum(PG)
                a = np.maximum(a, sm(ed, 35, 80) * binary_dilation(binary_opening(ed > 35, iterations=2) & box(c['dust'])))
        a = np.maximum(np.clip(gaussian_filter(np.clip(a, 0, 1), 0.5), 0, 1), binary_erosion(core))
        a *= np.clip(np.minimum(np.minimum(XX, W - 1 - XX), H - 1 - YY) / 10.0, 0, 1)    # (his frame's edges let go)
        lay = warp(np.dstack([Kk * a[..., None], a, glow * (1 - a[..., None])]), c['fig'], mode='constant')
        aw = np.clip(lay[..., 3:4], 0, 1)
        out.append(Image.fromarray(np.clip(tn(C) * (1 - aw) + lay[..., :3] + lay[..., 4:], 0, 255).astype(np.uint8)))
    return out


def clip_pictures(name, file, grid, fit):
    """A cut's pictures (480 x 160): its keyframes in order (over one landscape where CLIP_STEADY says), each held
    CLIP_HOLD frames, an in-between (the two mixed) before the next, the whole cut pushing in slowly (CLIP_PUSH); and its
    palette (CLIP_COLORS, from its keyframes)."""
    keys = clip_keys(file, grid, fit)
    if name in CLIP_STEADY: keys = steady_keys(name, keys)
    seq = []
    for i, k in enumerate(keys):
        seq += [k] * CLIP_HOLD
        if i + 1 < len(keys): seq.append(Image.blend(k, keys[i + 1], 0.5))
    out = []
    for j, im in enumerate(seq):
        z = 1.0 + CLIP_PUSH * j / max(len(seq) - 1, 1); w_, h_ = 480 / z, 160 / z
        out.append(im.resize((480, 160), Image.LANCZOS, box=((480 - w_) / 2, (160 - h_) / 2, (480 + w_) / 2, (160 + h_) / 2)))
    mos = Image.new('RGB', (480, 160 * len(keys)))
    for i, k in enumerate(keys): mos.paste(k, (0, 160 * i))
    return out, mos.quantize(colors=CLIP_COLORS, method=0, dither=0)


def static_pictures():
    """The few frames of static between clips: grey snow, a few bright tearing bars."""
    R = np.random.RandomState(11); out = []
    for k in range(STATIC_N):
        a = R.randint(30, 200, (160, 480, 1)).repeat(3, 2).astype(float)
        for b in range(3):
            y = R.randint(0, 150); a[y:y + R.randint(3, 10)] = a[y:y + R.randint(3, 10)].mean() * 0 + R.randint(150, 240)
        out.append(Image.fromarray(a.astype(np.uint8)))
    return out


def perk_pictures(w, h):
    """The side panel's perk commercials (w x h, its glass): each perk's eight frames (PERK_SHEETS), each held PERK_HOLD
    frames pushing in a little; a VHS look over all (scan lines, the colours a pixel apart, a tracking band rolling down)."""
    W2, H2 = w * 4, h * 4
    out = []
    for icon, file, cols, rows in PERK_SHEETS:
        sh = Image.open(os.path.join(SRC, file)).convert('RGB')
        for r0, r1 in rows:
            for c0, c1 in cols:
                st = sh.crop((c0, r0, c1, r1)).resize((W2, H2), Image.LANCZOS)
                for j in range(PERK_HOLD):
                    z = 1 + 0.025 * j; ww_, hh_ = W2 / z, H2 / z
                    out.append(st.resize((W2, H2), Image.LANCZOS, box=((W2 - ww_) / 2, (H2 - hh_) / 2, (W2 + ww_) / 2, (H2 + hh_) / 2)))
    R = np.random.RandomState(5); res = []
    for k, im in enumerate(out):
        a = np.asarray(im.resize((w, h), Image.BOX)).astype(float)
        a[..., 0] = np.roll(a[..., 0], 1, 1)                          # (the VHS colours a pixel apart)
        yy = np.arange(h)[:, None]
        a = a * np.where(yy % 2 == 1, 0.82, 1.0)[..., None]
        band = (k * 9) % (h + 20) - 10
        a[max(band, 0):max(band + 3, 0)] = a[max(band, 0):max(band + 3, 0)] * 0.6 + 70
        res.append(np.clip(a * 0.8, 0, 255))
    return res


SCR = {}                                       # (the giant screen's glass, from compose() for comps())
FACE_M = {}                                    # (the face's pixels over BOX, from compose() for sun_mask())

# B's grain pass (R28; the owner: "le bas et les machines en général manquent un peu de grain, texture à générer"): the
# corner as composed here (the street at 22 h over EDIT_CROP, the machines and the side panel lit, the screen dark) given
# to the image API with the parts to repaint (tools/src/soda_prompts.txt): the machines whole, the side panel's frame,
# the canopy from below (its fascia and round tile ends end to end), the ground at the machines' feet, the foliage past
# the house's corner; the lit result, then its edit with every light out. Laid on those parts only (EDIT_FIT: their
# registration on the composed corner and their colours, fitted once on what they were told to keep)
EDIT = {'B': ('soda_B_edit_lit.webp', 'soda_B_edit_off.webp')}
EDIT_CROP = (195, 360, 420, 760)
EDIT_FIT = {'B': {"lit": {"s": 6.8814, "sy": 6.88, "ox": -6.0, "oy": 0.0, "o": [195, 360], "M": [[1.0577, 0.0, 0.0, -2.868], [0.0, 1.0577, 0.0, -0.973], [0.0, 0.0, 1.0577, -5.544]]}, "off": {"s": 6.8608, "sy": 6.88, "ox": -4.5, "oy": 0.0, "o": [195, 360], "M": [[1.0577, 0.0, 0.0, -2.868], [0.0, 1.0577, 0.0, -0.973], [0.0, 0.0, 1.0577, -5.544]]}}}
FEET = 6                                       # (the ground at the machines' feet taken from the edits: so many rows)
MACH_TONE = (14.0, 0.80, 0.15)                 # (the machines: their darks lifted so much, a gain, a share of grey)
# their lower halves (the audit: "la moitié basse délavée, un voile laiteux"): under MACH_LOW[0] m on their fronts, their
# contrast round their own median times MACH_LOW[1], their darks down MACH_LOW[2] levels (not under MACH_LOW[3]), their
# colour back from the grey share by MACH_LOW[4]; fading in over the MACH_LOW[5] m above
MACH_LOW = (0.98, 1.45, 8.0, 8.0, 1.15, 0.12)
# the machines' headers (the owner: "j'aurais viré les logos des machines, ça rend mal, et la pub fait ce qu'il faut
# maintenant", then "sans logo, aplat de couleur moche"): what real Japanese machines have on top, a backlit printed
# drinks banner, each in its machine's colour family: Speed Cola's green with cold cans and つめた〜い, Double Tap's
# amber-brown with hot coffee and tea and あったか〜い, Juggernog's brick red with cola cans and コーラ. The machines' tops
# as composed here (over HEADS_CROP, x8, the headers plain panels) given to the image API to repaint the three panels
# (tools/src/soda_prompts.txt; R28); registered on the corner and its colours mapped on what it was told to keep
# (HEADS_FIT), brought down to the street's pixels by area, laid on each front's panel (HEAD, Y in m) only. There, its
# lightness brought into the painting's night (HEAD_TONE: its own p2..p98 to that range, its chroma times so much), a
# little darker to its edges as a print lit from a tube behind it (HEAD_FALL, HEAD_ENDS), a thin frame in its body's
# tone (HEAD_FRAME), a dark bezel under it to the display (HEAD_RIM); then the painting's grain (tools/regrain.py,
# regrain_group: so many tone families a panel, HEAD_FAMILIES, a fine baked grain, Bayer). Unlit in the power cut
# (HEAD_OFF); its light on the shade over the machines and the fascia's lower edge (HEAD_GLOW); it breathes with the machines' (street.js, 'vend')
HEADS = {'B': 'soda_B_heads.webp'}
HEADS_CROP = (262, 553, 362, 633)
HEADS_FIT = {'B': {"s": 23.1552, "sy": 23.2, "ox": -5.5, "oy": 0.0, "o": [262, 553], "M": [[1.0125, 0.0, 0.0, -0.647], [0.0, 1.0125, 0.0, 0.387], [0.0, 0.0, 1.0125, -2.716]]}}
HEAD = (1.66, 2.0)                             # (the panel on each front, Y in m: over the grain pass's old badges)
HEAD_RIM, HEAD_BEZEL = 1.635, (22.0, 24.0, 34.0)   # (the dark bezel between it and the display: from Y, its colour)
HEAD_TONE = (0.25, 0.53, 1.3, 0.72)            # (OKLab lightness: the banners' p2 and p98 to these, a gamma; their chroma
                                               #  times so much)
HEAD_FALL, HEAD_ENDS = 0.22, 0.35              # (so much darker at its edges than across its middle; at its two ends)
HEAD_FRAME = 0.25                              # (the frame: its body's tone, so much of the panel's edge in it)
HEAD_OFF = (0.34, 5.0)                         # (unlit: its lit colour times so much, plus so much)
HEAD_FAMILIES = {'lit': 10, 'off': 6}          # (the grain: so many tone families a panel)
HEAD_GLOW = (0.4, 3.5, 0.45)                   # (its light on the shade over the machines: a gain, its falloff up in px;
                                               #  on the fascia's lower edge: a gain)
# the rain under the canopy (the owner: "faut refaire les gouttes, flaques : le haut-vent a bougé"): its drips off the
# round tile ends' lower edge (DRIP_LIP: out of the fascia, under the tiles' line, m), in the channels between them as
# painted (DRIP_CHANNELS: their x on that line, read off the grain pass's tile ends, the dark gaps between them): a
# trickle every DRIP_EVERY channels at the rates of zone 9's channels (DRIP_RATE /s), a bigger one at each corner
# (DRIP_CORNER: the near one's and the far one's rates, how far in from the ends, m), a little burst at the others (their
# interval DRIP_BURST s). The ground under it in the water map (WET_SRC: wet.webp's rows WET_BOX and wet_mirror.webp's
# columns as the painter left them, under his lean-to): the mirror line at the side panel's and the fronts' feet (the
# painter's own past them, from column WET_OLD[2]); no water where the things stand; in the canopy's shelter, damp
# (WET_SHELTER: R at most); the band of the old drip line along his lean-to's foot taken down (WET_OLD: so much at the
# foot, its falloff in rows); the ground the lean-to stood on, wet as the sidewalk round it (its pattern mirrored about
# the old foot); the splash line where the drops land (WET_SPLASH: R added, its half-width and its centre out of the lip,
# m) and a small puddle under each trickle (WET_PUDDLE: half-length along the street and half-width across, m; its R;
# the corners' times so much)
DRIP_LIP = (0.02, -0.038)
DRIP_CHANNELS = (307, 313, 320, 327, 334, 341, 347, 353, 358, 364, 370, 376)
DRIP_EVERY = 2
DRIP_RATE = (5.5, 10.0)
DRIP_CORNER = (18.0, 15.0, 0.04)
DRIP_BURST = (1.5, 4.5)
WET_SRC = ('soda_wet_before.webp', 'soda_mirror_before.webp')
WET_BOX = (200, 680, 440, 780)                 # (x0, row0, x1, row1: scene rows; wet.webp starts at row 600)
WET_SHELTER = 6.0
WET_OLD = (0.45, 6.0, 356)
WET_SPLASH = (20.0, 0.07, 0.03)
WET_PUDDLE = (0.11, 0.07, 112.0, 1.5)
# the lamp's puddle under the bench (the audit: "un rectangle rouge à bords nets ... s'arrête net à x ~398"): over
# WET_BENCH (x0, y0, x1, y1), its still water and wetness softened (blurred so much, px) inside a soft ellipse fading out
# before the oden's edge (its centre, its half-axes, px); a puddle on the sidewalk before the side panel (the audit: "aucun
# reflet rouge dans le trottoir mouillé dessous"): its still water takes the panel's light (WET_PANEL: two ellipses,
# centre and half-axes in px, its R, the softness)
WET_BENCH = (340, 680, 410, 700, 1.1, (370.0, 688.0), (25.0, 7.5))
WET_PANEL = (((252.0, 760.0), (22.0, 6.0)), ((274.0, 768.0), (15.0, 4.5)), 104.0, 0.4)


def compose(v, city, off, lit, m, what, box):
    """B's drawn parts over the takes (off and lit, in place): the painter's boards on the house's whole front under
    the old flashing and his downpipe down the corner, the canopy as one sees it from under it, the giant screen's box
    (its glass dark). Returns what is the painter's own (kept out of the flat colours) and the screen's glass."""
    x0, y0, x1, y1 = box
    _, _, X, Y = rays(box)
    yfl = VY - FLASH * (VX - X)
    band = (X < PIPE[1]) & (Y >= yfl - WALL_SRC) & (Y < yfl)             # (the old lean-to's shade over its flashing)
    wall = (m & (what == 'wall')) | band
    pipe = (m | band) & (X >= PIPE[0]) & (X < PIPE[1]) & (Y > yfl - WALL_SRC) & ((what == '') | (what == 'wall'))
    # the face over the old lean-to's shade, up to the bay's sill (the leaves in front of it kept)
    xe_, ye_ = FACE_SILL[:2]
    ysill = VY - (VY - ye_) * (VX - X) / (VX - xe_)
    lum = city[y0:y1, x0:x1, :3] @ [0.299, 0.587, 0.114]
    up = (X >= FACE_X[0]) & (X < FACE_X[1]) & (Y >= ysill + 2) & (Y < yfl - WALL_SRC) & (lum >= FACE_LEAF)
    tree = (X < FACE_TREE[0]) & (Y >= FACE_TREE[1]) & (Y < FACE_TREE[2]) & (lum < FACE_LEAF)   # (his leaves past the edge)
    face = (wall | up) & ~tree
    b_ = np.zeros(m.shape + (3,))
    b_[face] = upper_boards(city, box, face)[face]
    b_[pipe] = painter_boards(city, box, pipe)[pipe]                     # (his downpipe down the corner)
    d_ = Y - (ysill + 2)                                                  # (the sill's shadow under it)
    b_ = b_ * np.where(up & (X < FACE_SILL[3] + 1) & (d_ < 1), FACE_SILL_SH[0], np.where(up & (X < FACE_SILL[3] + 1) & (d_ < 2), FACE_SILL_SH[1], 1.0))[..., None]
    beside = up & (X >= FACE_SILL[3] + 1)                                  # (beside the bay: his dusk light falling off)
    wf = np.clip(1 - d_ / FACE_FADE, 0, 1)[..., None]
    b_ = np.where(beside[..., None], city[y0:y1, x0:x1, :3] * wf + b_ * (1 - wf), b_)
    # only real light on it: the canopy's shade under it, the screen box's contact shade under its foot
    L = layout(v); C = L['canopy']; sb = L['bigscreen']
    with np.errstate(divide='ignore', invalid='ignore'):
        Zw = F * XH / (X - VX); Yw = EYE - (Y - VY) * Zw / F
    under = (Yw < C['y_wall']) & (Zw >= C['z0']) & (Zw <= C['z1'])
    foot = (Yw < sb[2]) & (Yw > sb[2] - 0.05) & (Zw >= sb[4]) & (Zw <= sb[5])
    b_ = b_ * np.where(under, WALL_SHADE[0], np.where(foot, WALL_SHADE[1], 1.0))[..., None]
    for a in (off, lit): a[face | pipe] = b_[face | pipe]
    FACE_M[v] = face
    crgb, ccov = canopy_paint(v, box)
    cv = (ccov > 0) & m
    for a in (off, lit): a[cv] = a[cv] * (1 - ccov[cv][:, None]) + crgb[cv] * ccov[cv][:, None]
    srgb, scov, uvg, gcov = screen_paint(v, box)
    sv = (scov > 0) & m
    for a in (off, lit): a[sv] = a[sv] * (1 - scov[sv][:, None]) + srgb[sv] * scov[sv][:, None]
    return (face | pipe) & ~cv & ~sv, (uvg, gcov, scov)


def apply_edit(v, off, lit, m, what, box):
    """B's grain pass laid on its parts (off and lit in place): the machines, the canopy and its braces, the foliage past
    the house's corner, the ground at the machines' feet. Returns the mask grown by that ground, and those parts."""
    from scipy.ndimage import binary_dilation as bd
    x0, y0, x1, y1 = box
    fl, fo = EDIT_FIT[v]['lit'], EDIT_FIT[v]['off']
    el = colours(sample(sat(np.asarray(Image.open(os.path.join(SRC, EDIT[v][0])).convert('RGB')).astype(float)), fl, box), fl['M'])
    eo = colours(sample(sat(np.asarray(Image.open(os.path.join(SRC, EDIT[v][1])).convert('RGB')).astype(float)), fo, box), fo['M'])
    _, _, X, Y = rays(box)
    mach = np.isin(what, ['mach0', 'mach1', 'mach2'])
    _, ccov = canopy_paint(v, box)
    feet = np.zeros(m.shape, bool)
    for j in range(m.shape[1]):
        r_ = np.nonzero(mach[:, j])[0]
        if len(r_): feet[r_.max() + 1:r_.max() + 1 + FEET, j] = True
    past = (X > PIPE[1]) & (what == '') & m
    part = (bd(mach, iterations=1) | bd(ccov > 0, iterations=1)) & m | past | feet
    off[part] = eo[part]; lit[part] = el[part]
    mt = bd(mach, iterations=1) & m            # (the machines into the painting's range: a touch muted, their darks less
    for a in (off, lit):                       # black, their lights less hot; their grain as it is)
        c = a[mt]; g_ = (c @ [0.299, 0.587, 0.114])[:, None]
        a[mt] = MACH_TONE[0] + (c * (1 - MACH_TONE[2]) + g_ * MACH_TONE[2]) * MACH_TONE[1]
    if v == 'B':                               # the lower halves: their contrast back
        w_, f_, z_, dx_, dy_, X_, Y_ = cast(v, box)
        with np.errstate(invalid='ignore'):
            Yh = EYE + dy_ * z_
        for i in range(len(layout(v)['mach'])):
            lo = (w_ == 'mach%d' % i) & (f_ == 1) & (Yh < MACH_LOW[0] + MACH_LOW[5]) & m
            wt = np.clip((MACH_LOW[0] + MACH_LOW[5] - Yh) / MACH_LOW[5], 0, 1)[lo][:, None]
            for a in (off, lit):
                c = a[lo]; g_ = (c @ [0.299, 0.587, 0.114])[:, None]; med = np.median(g_)
                c2 = g_ + (c - g_) * MACH_LOW[4]
                c2 = med + (c2 - med) * MACH_LOW[1] - MACH_LOW[2]
                c2 = np.maximum(c2, np.minimum(c, MACH_LOW[3]))
                a[lo] = np.clip(c * (1 - wt) + c2 * wt, 0, 255)
    if v == 'B':                               # the headers: a lit panel each, no emblem
        part = part | heads(v, off, lit, m, box)
    return m | feet, part


def heads(v, off, lit, m, box):
    """B's headers (off and lit in place): on each machine's front over HEAD, its banner (HEADS, HEADS_FIT) toned, a
    little darker to its edges, framed, the bezel under it (HEAD_*), through the painting's grain (regrain_group); its
    light under the canopy (HEAD_GLOW). Returns the pixels drawn."""
    from scipy.ndimage import binary_dilation as bd, binary_erosion as be
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import regrain as RG
    L = layout(v); ms = L['mach']
    w_, f_, z_, dx_, dy_, X_, Y_ = cast(v, box)
    with np.errstate(invalid='ignore'):
        Yh = EYE + dy_ * z_
    t = np.clip((Yh - HEAD[0]) / (HEAD[1] - HEAD[0]), 0, 1)
    hf = HEADS_FIT[v]
    gen = np.clip(colours(sample(sat(np.asarray(Image.open(os.path.join(SRC, HEADS[v])).convert('RGB')).astype(float)), hf, box), hf['M']), 0, 255)
    four = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], bool)
    hms = [bd((w_ == 'mach%d' % i) & (f_ == 1) & (Yh >= HEAD[0]) & (Yh <= HEAD[1]), iterations=1) & (w_ == 'mach%d' % i) & m
           for i in range(len(ms))]
    lab = RG.oklab(gen)
    lo, hi = np.percentile(lab[np.any(hms, 0)][:, 0], [2, 98])        # (the three banners' range together)
    drawn = np.zeros(m.shape, bool); light = []
    for i, b in enumerate(ms):
        on_ = (w_ == 'mach%d' % i) & (f_ == 1)
        hm = hms[i]; inner = be(hm, structure=four); frame = hm & ~inner
        u = np.clip((z_ - b[4]) / (b[5] - b[4]), 0, 1)
        lum = np.sin(np.pi * t) ** 0.7 * (1 - HEAD_ENDS * np.abs(2 * u - 1) ** 3)     # (the tube behind the print)
        Lk = HEAD_TONE[0] + np.clip((lab[..., 0] - lo) / (hi - lo), 0, 1.08) ** HEAD_TONE[2] * (HEAD_TONE[1] - HEAD_TONE[0])
        Lk = Lk * (1 - HEAD_FALL * (1 - lum))
        tl = np.dstack([Lk, lab[..., 1] * HEAD_TONE[3], lab[..., 2] * HEAD_TONE[3]])
        body = on_ & (Yh > 0.25) & (Yh < 0.95)
        ys, xs = np.nonzero(hm); r = (int(xs.min()), int(ys.min()), int(xs.max() + 1 - xs.min()), int(ys.max() + 1 - ys.min()))
        lit_rgb = RG.from_oklab(tl)
        for name, a in (('lit', lit), ('off', off)):
            rgb = lit_rgb if name == 'lit' else lit_rgb * HEAD_OFF[0] + HEAD_OFF[1]
            edge = np.median(rgb[inner & (t < 0.15)], 0)
            rgb = rgb.copy(); rgb[frame] = np.median(a[body], 0) * (1 - HEAD_FRAME) + edge * HEAD_FRAME
            at = np.zeros(m.shape + (4,), np.uint8)
            at[..., :3] = np.clip(np.round(rgb), 0, 255); at[..., 3] = 255 * hm
            P = dict(RG.DEF, families=HEAD_FAMILIES[name], p95=None, stray=0)
            RG.regrain_group([{'a': at, 'box': r}], P, 'head%d_%s' % (i, name))
            a[hm] = at[..., :3][hm]
            rim = on_ & (Yh >= HEAD_RIM) & (Yh < HEAD[0]) & ~hm & m       # (the dark bezel under it, to the display)
            a[rim] = HEAD_BEZEL
            drawn |= hm | rim
        light.append((b, lit[inner].mean(0)))
    # its light under the canopy: on the shade over the machines' tops (the house's wall seen there), falling off up
    # from each panel's top, and on the fascia's lower edge over it; a touch wider than the panel
    sh = (w_ == 'wall') & m & ~drawn; fa = (w_ == 'canopy') & (f_ == 2) & m
    add = np.zeros(m.shape + (3,)); rows = np.arange(m.shape[0])[:, None]
    for (b, col), hm in zip(light, hms):
        cols = np.nonzero(hm.any(0))[0]
        top = np.full(m.shape[1], -1); top[cols] = hm[:, cols].argmax(0)
        fb = np.where(fa.any(0), m.shape[0] - 1 - fa[::-1].argmax(0), -1)       # (the fascia's lowest row a column)
        up = (top[None, :] - rows).astype(float)
        on = (top[None, :] >= 0) & (up > 0)
        wsh = np.where(on & sh, HEAD_GLOW[0] * np.exp(-up / HEAD_GLOW[1]), 0)
        wfa = np.where(on & fa, HEAD_GLOW[2] * np.exp(-(fb[None, :] - rows) / 1.5) * np.exp(-(top - fb)[None, :] / 12.0), 0)
        add += (wsh + wfa)[..., None] * col
    add = gaussian_filter(add, (0, 1.0, 0)) * (sh | fa)[..., None]
    lit[:] = np.clip(lit + add, 0, 255)
    return drawn | ((add @ [0.299, 0.587, 0.114]) > 0.5)


def build(v, city, unlit, box=BOX):
    """The zone's new layers over box (off: the off take), the lit take, the mask, the comps."""
    x0, y0, x1, y1 = box
    fl, fo = FIT[v]['lit'], FIT[v]['off']
    lit = colours(sample(sat(take(v, 'lit')), fl, box), fl['M'])
    off = colours(sample(sat(take(v, 'off')), fo, box), fo['M'])
    m, what, face = mask(v, box)
    if v in BORROW:                            # (faces a take got wrong, from another take of the same layout)
        u, faces = BORROW[v]; gl, go = FIT[u]['lit'], FIT[u]['off']
        ul = colours(sample(sat(take(u, 'lit')), gl, box), gl['M']); uo = colours(sample(sat(take(u, 'off')), go, box), go['M'])
        b_ = np.zeros(m.shape, bool)
        for name, fs in faces: b_ |= (what == name) & np.isin(face, fs)
        b_ = binary_dilation(b_, iterations=1) & m & (what != 'canopy')
        lit[b_] = ul[b_]; off[b_] = uo[b_]
    # the house's boards: the take's tone brought to the painter's at the old flashing's ray (each channel's gain, the
    # take's boards just under it against his just over it, over x WALL_MATCH), on the whole of the take's wall, its
    # lights left as they add (A's window, the ad's glow): no step where his boards end
    _, _, X, Y = rays(box)
    d = Y - (VY - FLASH * (VX - X)); cols = (X > WALL_MATCH[0]) & (X < WALL_MATCH[1]); n_ = WALL_MATCH[2]
    wl = (what == 'wall') & m
    below = cols & wl & (d >= 1) & (d < n_); above = cols & ~m & (d >= -n_) & (d < -1) & (Y >= y0)
    g = np.clip(city[y0:y1, x0:x1, :3][above].mean(0) / np.maximum(off[below].mean(0), 1), 0.4, 1.6)
    add = lit[wl] - off[wl]; off[wl] = off[wl] * g; lit[wl] = np.clip(off[wl] + add, 0, 255)
    keep = np.zeros(m.shape, bool); SCR[v] = None
    if 'bigscreen' in layout(v):               # (B: its house's boards the painter's, its canopy and its screen drawn)
        keep, SCR[v] = compose(v, city, off, lit, m, what, box)
        m = m | keep                           # (the band of shade over the old flashing and the face up to the bay)
    if v in EDIT:                              # (its parts already in the painter's grain: kept out of the flat colours)
        m0 = m; m, ep = apply_edit(v, off, lit, m, what, box); keep = keep | ep
    if QUANT:
        q_ = m & ~keep
        both = np.concatenate([off[q_], lit[q_]])[None].astype(np.uint8)
        q = Image.fromarray(both).quantize(colors=QUANT, method=0, dither=0)
        pal = np.array(q.getpalette()[:QUANT * 3], float).reshape(-1, 3)
        idx = np.asarray(q)[0]; n = q_.sum()
        off[q_] = pal[idx[:n]]; lit[q_] = pal[idx[n:]]
    if v not in EDIT:                          # (B's grain pass paints its displays and its perks' headers)
        displays(v, off, lit, box)
        shields(v, off, lit, box)
    new = city[y0:y1, x0:x1, :3].copy(); new[m] = off[m]
    unew = unlit[y0:y1, x0:x1, :3].copy(); unew[m] = off[m]
    return new, unew, lit, off, m, what


# the machines' display windows, drawn on the takes' (theirs copy the guide's placeholder stripes): on each front, u along
# it from its near edge, Y up; three shelves of nine samples, a price strip under each; the colours (off, lit) v5's
DISPLAY = (0.08, 0.92, 1.02, 1.70)
NPROD = 9
BACK = ((22, 24, 48), (150, 170, 190))
BACK_LO = ((20, 22, 44), (112, 134, 160))
PRICE = ((16, 20, 44), (40, 62, 104))
LED = ((24, 30, 56), (96, 156, 196))
PROD = [(47, 86, 140), (86, 160, 193), (90, 120, 159), (61, 119, 174), (104, 88, 146), (62, 66, 94), (214, 104, 146),
        (190, 62, 68), (76, 168, 100), (222, 150, 74), (226, 208, 168)]
PROD_W = np.array([6, 6, 6, 6, 5, 4, 6, 6, 5, 5, 4], float)


def hsh(*a):
    """A fixed pseudo-random number in 0..1 for integer arguments (the same each run)."""
    x = np.sin(sum(float(v) * k for v, k in zip(a, (12.9898, 78.233, 37.719, 4.581)))) * 43758.5453
    return x - np.floor(x)


def displays(v, off, lit, box, ss=3):
    """Each machine's display window over the takes' (off and lit, street pixels over box), 3 x 3 rays a pixel: the back
    lit from above, its shelves' samples (bottles and cans, each its colour, their caps), the price strip and its lit
    buttons; off: the same behind dark glass."""
    L = layout(v); x0, y0, x1, y1 = box
    u0, u1, h0, h1 = DISPLAY; row = (h1 - h0) / 3
    cum = np.cumsum(PROD_W) / PROD_W.sum()
    for i, b in enumerate(L['mach']):
        X = b[1]
        xa = int(np.floor(P(X, h1, b[4] + u0 * (b[5] - b[4]))[0])); xb = int(np.ceil(P(X, h1, b[4] + u1 * (b[5] - b[4]))[0]))
        ya = int(np.floor(P(X, h1, b[4])[1])); yb = int(np.ceil(P(X, h0, b[4])[1]))
        sx = (np.arange((xb - xa) * ss) + 0.5) / ss + xa; sy = (np.arange((yb - ya) * ss) + 0.5) / ss + ya
        SX, SY = np.meshgrid(sx, sy)
        Z = F * X / (SX - VX); Y = EYE - (SY - VY) * Z / F
        u = (Z - b[4]) / (b[5] - b[4])
        inside = (u >= u0) & (u < u1) & (Y >= h0) & (Y < h1)
        r = np.clip(((Y - h0) / row).astype(int), 0, 2); fr = (Y - h0) / row - r
        k = np.clip(((u - u0) / (u1 - u0) * NPROD).astype(int), 0, NPROD - 1); fk = (u - u0) / (u1 - u0) * NPROD - k
        out = {}
        t = ((h1 - Y) / (h1 - h0))[..., None]
        for kind in (0, 1):
            c = np.array(BACK[kind], float) * (1 - t) + np.array(BACK_LO[kind], float) * t
            strip = fr < 0.17
            c = np.where(strip[..., None], np.array(PRICE[kind], float), c)
            led = strip & (fr > 0.05) & (fr < 0.11) & (np.abs(fk - 0.5) < 0.2)
            c = np.where(led[..., None], np.array(LED[kind], float), c)
            prod = np.zeros(Y.shape + (3,)); isp = np.zeros(Y.shape, bool)
            for rr in range(3):
                for kk in range(NPROD):
                    sel = (r == rr) & (k == kk)
                    if not sel.any(): continue
                    hh = hsh(i, rr, kk, 3); bottle = (i + rr) % 3 == 0 or ((i + rr) % 3 == 2 and hh > 0.5)
                    ci = int(np.searchsorted(cum, hsh(i, rr, kk, 1)))
                    top = 0.17 + (0.70 + 0.08 * hh if bottle else 0.52 + 0.06 * hh)
                    wid = 0.30 if bottle else 0.36
                    body = sel & (fr >= 0.17) & (fr < top) & (np.abs(fk - 0.5) < wid)
                    col = np.array(PROD[ci], float)
                    cap = body & (fr > top - (0.07 if bottle else 0.04))
                    neck = body & bottle & (fr > top - 0.2) & (np.abs(fk - 0.5) > wid * 0.55)
                    body &= ~neck
                    prod[body] = col; prod[cap] = (np.array((220, 220, 226), float) if bottle else col * 1.25)
                    isp |= body
            if kind == 1:
                pc = prod * (0.82 + 0.18 * (1 - t))
            else:
                pc = prod * 0.16 + np.array((8, 10, 24), float) * (prod.sum(-1, keepdims=True) > 0)
            c = np.where(isp[..., None], pc, c)
            out[kind] = c
        n_ = inside.reshape(yb - ya, ss, xb - xa, ss).mean((1, 3))
        for kind, arr in ((0, off), (1, lit)):
            avg = (out[kind] * inside[..., None]).reshape(yb - ya, ss, xb - xa, ss, 3).sum((1, 3)) / np.maximum(n_[..., None] * ss * ss, 1)
            Ya, Xa = ya - y0, xa - x0
            dst = arr[Ya:Ya + (yb - ya), Xa:Xa + (xb - xa)]
            dst[...] = dst * (1 - n_[..., None]) + avg * n_[..., None]


def shields(v, off, lit, box):
    """Each machine's perk on its header (the icon's first frame), on the front's plane (foreshortened as it is)."""
    L = layout(v); x0, y0 = box[:2]; nx, ny = NUDGE[v]['shield']
    for i, b in enumerate(L['mach']):
        ic = np.asarray(Image.open(os.path.join(ROOT, 'assets', '%s_perk.webp' % PERK_NAMES[i])).convert('RGBA').crop((0, 0, 32, 32))).astype(float)
        za, zb_ = b[4] + 0.18, b[5] - 0.18; ya, yb = 1.97, 1.66
        xa, ya_ = P(b[1], ya, za); xb_, _ = P(b[1], ya, zb_)
        for y in range(int(np.floor(P(b[1], ya, za)[1])), int(np.ceil(P(b[1], yb, za)[1])) + 1):
            for x in range(int(np.floor(xa)), int(np.ceil(xb_)) + 1):
                Z = F * b[1] / (x + 0.5 - VX); Yy = EYE - (y + 0.5 - VY) * Z / F
                u = (Z - za) / (zb_ - za); t = (ya - Yy) / (ya - yb)
                if not (0 <= u < 1 and 0 <= t < 1): continue
                c = ic[int(t * 32), int(u * 32)]
                if c[3] < 128: continue
                yy, xx = y + ny - y0, x + nx - x0
                if 0 <= yy < off.shape[0] and 0 <= xx < off.shape[1]:
                    lit[yy, xx] = c[:3] * 0.92; off[yy, xx] = c[:3] * 0.42 + off[yy, xx] * 0.1


def comp_from(lit, off, m, rect, box, thr=5.0, warm=False):
    """A comp over rect (x0, y0, x1, y1, street px): the lit take where it is lighter than the off one (its alpha the
    difference, so that laid over the layer it gives the lit take)."""
    x0, y0 = box[:2]; a0, b0, a1, b1 = rect
    L_, O_ = lit[b0 - y0:b1 - y0, a0 - x0:a1 - x0], off[b0 - y0:b1 - y0, a0 - x0:a1 - x0]
    mm = m[b0 - y0:b1 - y0, a0 - x0:a1 - x0]
    d = (L_ - O_) @ [0.299, 0.587, 0.114]
    al = np.clip((d - thr) / 18.0, 0, 1) * mm
    if warm: al = al * ((L_ - O_)[..., 0] > (L_ - O_)[..., 2])      # (a lamp's light only: not the ad's glow round it)
    rgb = np.where(al[..., None] > 0, np.clip((L_ - O_ * (1 - al[..., None])) / np.maximum(al[..., None], 1e-3), 0, 255), 0)
    return np.dstack([rgb, al * 255])


def bbox(P_):
    xs, ys = [p[0] for p in P_], [p[1] for p in P_]
    return int(np.floor(min(xs))), int(np.floor(min(ys))), int(np.ceil(max(xs))), int(np.ceil(max(ys)))


def comps(v, lit, off, m, box):
    """The lit comps: the machines (their fronts, their light round them), their middle one off (the stutter), the
    booth's window, the ad's six frames, A's window."""
    L = layout(v); x0, y0, x1, y1 = box
    out = {}
    ms = L['mach']
    pts = [P(b[1], Y, Z) for b in ms for Y in (0.0, b[3]) for Z in (b[4], b[5])]          # (their fronts, and the
    pts += [P(X, Y, ms[0][4]) for X in (L['booth'][1] if 'booth' in L else ms[0][0], ms[0][1]) for Y in (0.0, ms[0][3])]   # near one's side we see)
    a0, b0, a1, b1 = bbox(pts)
    C = L['canopy']; ye = C['y_wall'] - C['pitch'] * C['proj']
    vr = (max(a0 - 4, x0), max(int(P(XH + C['proj'], ye, ms[0][4])[1]) - 10, y0), min(a1 + 6, x1), min(b1 + 3, y1))
    if v == 'B': vr = (max(int(P(ms[0][1], 0, ms[0][4])[0]) - 1, x0),) + vr[1:]
    out['z7_vending'] = (comp_from(lit, off, m, vr, box), vr)
    b = ms[1]
    r = bbox([P(b[1], Y, Z) for Y in (0.0, b[3]) for Z in (b[4], b[5])])
    o = np.dstack([off[r[1] - y0:r[3] - y0, r[0] - x0:r[2] - x0], 255 * m[r[1] - y0:r[3] - y0, r[0] - x0:r[2] - x0]])
    out['z7_vendoff'] = (o, r)
    if 'booth' in L:
        bt = L['booth']; r = bbox([P(X, Y, bt[4]) for X in (bt[0], bt[1]) for Y in (0.6, 2.3)])   # (its sign too)
        r = (max(r[0], x0), r[1], r[2], r[3])
        out['win_z7_kiosk'] = (comp_from(lit, off, m, r, box), r)
    if 'window' in L:
        w = L['window']; r = bbox([P(w[0], Y, Z) for Y in (w[1] - 0.15, w[2] + 0.1) for Z in (w[3] - 0.2, w[4] + 0.2)])
        out['win_z7_low'] = (comp_from(lit, off, m, r, box, warm=True), r)
    if SCR.get(v) is not None:                 # the giant screen: its pictures in its glass, their light round it
        uvg, gcov, scov = SCR[v]
        R, G, A = SCREEN_GLOW
        from scipy.ndimage import distance_transform_edt
        d = distance_transform_edt(gcov < 0.5)
        near = (d > 0) & (d <= R) & m & ~np.isin(what_of(v, box), ['mach0', 'mach1', 'mach2'])   # (the frame's rim)
        ys_, xs_ = np.nonzero((gcov > 0) | near)
        r = (max(int(xs_.min()) + x0 - 1, x0), max(int(ys_.min()) + y0 - 1, y0), min(int(xs_.max()) + x0 + 2, x1), min(int(ys_.max()) + y0 + 2, y1))
        gg = gcov[r[1] - y0:r[3] - y0, r[0] - x0:r[2] - x0]

        def sheet(pics, pal=None):             # (a clip's frames side by side, each with its own light round it)
            fr = []
            for pic in pics:
                rgb, mean = screen_frame(uvg, box, pic, pal=pal)
                lf = off * (1 - gcov[..., None]) + rgb * gcov[..., None]
                lf[near] = np.clip(lf[near] * (1 + (np.asarray(mean, float) / 255.0)[None, :] * A * np.exp(-(d[near] - 1) / G)[:, None]), 0, 255)
                c = comp_from(lf, off, m | (gcov > 0), r, box, thr=1.0)
                c[..., :3] = np.where(gg[..., None] > 0, lf[r[1] - y0:r[3] - y0, r[0] - x0:r[2] - x0], c[..., :3])
                c[..., 3] = np.where(gg > 0, np.maximum(c[..., 3], 255 * gg), c[..., 3])
                fr.append(c)
            return np.concatenate(fr, 1)
        clips = [(name, sheet(*clip_pictures(name, f_, grid, fit))) for name, f_, grid, fit in SCREEN_CLIPS]
        clips.append(('static', sheet(static_pictures())))
        out['z7_bigscreen'] = (clips[0][1], r); out['z7_bigscreen_clips'] = clips
    if not L['ad']: return out
    g = L['glass']; nx, ny = NUDGE[v]['ad']
    ga, gb = P(g[0], g[3], g[4]), P(g[1], g[2], g[4])
    gx0, gy0, gx1, gy1 = int(round(ga[0])) + nx, int(round(ga[1])) + ny, int(round(gb[0])) + nx, int(round(gb[1])) + ny
    r = (max(gx0 - AD_PAD, x0), max(gy0 - AD_PAD, y0), min(gx1 + AD_PAD, x1), min(gy1 + AD_PAD, y1))
    glow = comp_from(lit, off, m, r, box)
    frames = perk_pictures(gx1 - gx0, gy1 - gy0) if v == 'B' else ad_frames(gx1 - gx0, gy1 - gy0)
    atlas = np.concatenate([glow.copy() for _ in range(len(frames))], 1); w_ = r[2] - r[0]
    ga_, gb_ = gx0 - r[0], gy0 - r[1]
    for n_, fr in enumerate(frames):
        atlas[gb_:gb_ + fr.shape[0], n_ * w_ + ga_:n_ * w_ + ga_ + fr.shape[1]] = np.dstack([fr, np.full(fr.shape[:2], 255.0)])
    out['z7_adscreen'] = (atlas, r)
    return out


def what_of(v, box):
    return cast(v, box)[0]


def ad_frames(w, h):
    """The six frames of the ad (h x w, RGB), lit: the three ads (ramune, ramen, the arcade's games: tools/src/
    soda_ads_model.webp) brought down to the glass's pixels and a few flat colours each (median cut, no dither), a fine
    scan line on every other row, a soft brighter bar sliding down from one frame to the next."""
    src = Image.open(os.path.join(SRC, AD_MODEL)).convert('RGB')
    yy = np.mgrid[0:h, 0:w][0]
    out = []
    for b in AD_PANELS:
        q = src.crop(b).resize((w, h), Image.BOX).quantize(colors=12, method=0, dither=0).convert('RGB')
        base = np.asarray(q).astype(float)
        for sub in range(2):
            bar = 1 + 0.07 * np.exp(-((yy - h * (0.3 + 0.4 * sub)) / 3.0) ** 2)
            out.append(np.clip(base * np.where(yy % 2 == 1, 0.86, 1.0)[..., None] * bar[..., None] * 0.78, 0, 255))
    return out


def street_js(v, cps):
    """What street.js keeps of the corner, from its layout: PERKS' columns and BZ.soda (the machines' fronts), the
    drips off the canopy's eave (DRIPS 'kiosk'), the comps' places (ASSETS.comps, their versions kept; COMP_KIND for
    A's window), z7_vendoff's and vend_pool's planes. Rewritten each run, the same bytes."""
    path = os.path.join(ROOT, 'assets', 'street.js')
    s0 = open(path, encoding='utf-8').read(); s = s0
    L = layout(v); ms = L['mach']
    for name in ('z7_vending', 'win_z7_kiosk', 'z7_adscreen', 'z7_bigscreen', 'win_z7_low'):
        m_ = re.search(r', "%s": \{"src": "assets/%s(?:_[a-z]+)?\.webp\?v=(\w+)", "x": \d+, "y": \d+, "w": \d+, "h": \d+\}' % (name, name), s)   # (the giant screen's: its first clip's sheet)
        if name not in cps:
            if m_: s = s[:m_.start()] + s[m_.end():]
            continue
        (img, r) = cps[name]; w_, h_ = r[2] - r[0], r[3] - r[1]
        ent = ', "%s": {"src": "assets/%s.webp?v=%s", "x": %d, "y": %d, "w": %d, "h": %d}' % (name, name, m_.group(1) if m_ else '1', r[0], r[1], w_, h_)
        if m_: s = s[:m_.start()] + ent + s[m_.end():]
        else:
            m2 = re.search(r', "z7_adscreen": \{[^}]*\}', s) or re.search(r', "z7_vending": \{[^}]*\}', s); s = s[:m2.end()] + ent + s[m2.end():]
    s, n = re.subn(r"z7_adscreen: 'ad'(, z7_bigscreen: 'ad')?(, win_z7_low: 'home')?", "z7_adscreen: 'ad'" + (", z7_bigscreen: 'ad'" if 'z7_bigscreen' in cps else '') + (", win_z7_low: 'home'" if 'win_z7_low' in cps else ''), s)
    assert n == 1, 'COMP_KIND'
    import hashlib
    hv = lambda f_: hashlib.md5(open(os.path.join(ROOT, f_), 'rb').read()).hexdigest()[:8]
    ads = {}
    if 'z7_adscreen' in cps:
        nf = int(cps['z7_adscreen'][0].shape[1] // (cps['z7_adscreen'][1][2] - cps['z7_adscreen'][1][0]))
        ads['z7_adscreen'] = {'n': nf, 'fps': PERK_FPS} if v == 'B' else {'n': nf}
    if 'z7_bigscreen_clips' in cps:
        w_ = cps['z7_bigscreen'][1][2] - cps['z7_bigscreen'][1][0]
        cl = [['assets/z7_bigscreen_%s.webp?v=%s' % (nm, hv('assets/z7_bigscreen_%s.webp' % nm)), int(sh.shape[1] // w_)] for nm, sh in cps['z7_bigscreen_clips']]
        ads['z7_bigscreen'] = {'fps': CLIP_FPS, 'loops': CLIP_LOOPS, 'clips': cl[:-1], 'trans': cl[-1] + [STATIC_FPS]}
    s, n = re.subn(r'const ADS = \{.*?\};\n', lambda m_: 'const ADS = %s;\n' % json.dumps(ads, separators=(',', ':')), s, count=1)
    assert n == 1, 'ADS'
    if 'z7_bigscreen_clips' in cps:            # (its comp's first picture: the first clip's sheet)
        s, n = re.subn(r'"z7_bigscreen": \{"src": "[^"]*"', '"z7_bigscreen": {"src": "%s"' % ads['z7_bigscreen']['clips'][0][0], s)
        assert n == 1, 'bigscreen src'
    # the corner's small lights (street.js's SODA_FX): the canopy's eave (near end, far end), the machines' outlets
    C = L['canopy']; xe = XH + C['proj']; ye = C['y_wall'] - C['pitch'] * C['proj'] - C['th']
    eave = [[round(P(xe, ye, z_)[0], 1), round(P(xe, ye, z_)[1], 1)] for z_ in (C['z0'], C['z1'])]
    outs = []
    for b in ms:
        q = bbox([P(b[1], Y_, b[4] + u_ * (b[5] - b[4])) for Y_ in (0.2, 0.38) for u_ in (0.1, 0.6)])
        outs.append([q[0], q[1], q[2] - q[0], q[3] - q[1]])
    s, n = re.subn(r'const SODA_FX = \{.*?\};', 'const SODA_FX = %s;' % json.dumps({'eave': eave, 'outlets': outs}, separators=(',', ':')), s, count=1)
    assert n == 1, 'SODA_FX'
    r = cps['z7_vendoff'][1]
    s, n = re.subn(r"(z7_vendoff\.webp\?v=\d+', )\d+, \d+, \d+, \d+", r"\g<1>%d, %d, %d, %d" % (r[0], r[1], r[2] - r[0], r[3] - r[1]), s)
    assert n == 1, 'vendoff'
    xa, ya = P(ms[0][1], 0, ms[0][4]); xb, yb = P(ms[2][1], 0, ms[2][5])
    # (the pool under them: placed on their fronts' feet as the painter's was on his machines')
    s, n = re.subn(r"(vend_pool\.webp\?v=\d+', )\d+, \d+", r"\g<1>%d, %d" % (int(round((xa + xb) / 2 - 53.5)), int(round(min(ya, yb) + 9))), s)
    assert n == 1, 'vend_pool'
    # (their light on the wet ground, split from the painter's when his machines' fronts were centred at x 315.5, the box
    # then at x 232: moved with them)
    s, n = re.subn(r"(gl_z7_vending\.webp\?v=\d+', box: \[)\d+", r"\g<1>%d" % int(round(232 + (xa + xb) / 2 - 315.5)), s)
    assert n == 1, 'gl_z7_vending'
    m = re.search(r'  const DRIPS = (\[.*?\]);   // per eave', s)
    D = json.loads(m.group(1))
    st, bu = [], []
    for Z, rate, _ in drip_points(v):
        x, y = lip_xy(v, Z)
        q = [int(np.floor(x)), int(np.floor(y)), round(VY + F * EYE / Z, 2), round(14045.0 / Z, 1), round(13.46 / Z, 3), 1.0 if rate else 0.0,
             rate, int(round(122.6 / Z)), int(round(52.5 / Z))]
        (st if rate else bu).append(q)
    for E in D:
        if E['n'] == 'kiosk':
            E['st'] = st; E['bu'] = bu; E['bi'] = list(DRIP_BURST)
            E['px'] = int(round(np.mean([q[0] for q in st]))); E['py'] = int(round(np.mean([q[1] for q in st])))
    s = s[:m.start(1)] + json.dumps(D, separators=(',', ':'), ensure_ascii=False) + s[m.end(1):]
    edges = [int(round(P(ms[0][1], 1.0, ms[0][4] + i)[0])) for i in range(4)]
    for name, (a, b) in zip(PERK_NAMES, zip(edges[:-1], edges[1:])):
        s, n = re.subn(r'(\b%s: \{ x0: )\d+(, x1: )\d+' % name, r'\g<1>%d\g<2>%d' % (a, b), s)
        assert n == 1, name
    top = int(np.floor(P(ms[0][1], ms[0][3], ms[0][4])[1])); bot = int(np.ceil(P(ms[0][1], 0, ms[0][4])[1]))
    s, n = re.subn(r'"soda":\[\d+,\d+,\d+,\d+\]', '"soda":[%d,%d,%d,%d]' % (edges[0], top, edges[-1], bot), s)
    assert n == 1, 'BZ.soda'
    if s != s0: open(path, 'w', encoding='utf-8').write(s)
    return edges


def lip_xy(v, Z):
    """Where a drop leaves the canopy at Z (street px): the round tile ends' lower edge, a little out of the fascia."""
    C = layout(v)['canopy']; xe = XH + C['proj']
    return P(xe + DRIP_LIP[0], C['y_wall'] - C['pitch'] * C['proj'] + DRIP_LIP[1], Z)


def drip_points(v):
    """The canopy's drip points along its eave, near to far: (Z, rate /s or 0 for a burst point, its puddle's size)."""
    C = layout(v)['canopy']; xl = XH + C['proj'] + DRIP_LIP[0]
    out = [(C['z0'] + DRIP_CORNER[2], DRIP_CORNER[0], WET_PUDDLE[3])]
    for k, x in enumerate(DRIP_CHANNELS):
        Z = F * xl / (x + 0.5 - VX)
        if k % DRIP_EVERY == DRIP_EVERY - 1:
            u = np.sin(k * 12.9898 + 41 * 78.233) * 43758.5453 % 1.0
            out.append((Z, round(DRIP_RATE[0] + (DRIP_RATE[1] - DRIP_RATE[0]) * u, 2), 1.0))
        else:
            out.append((Z, 0.0, 0.0))
    out.append((C['z1'] - DRIP_CORNER[2], DRIP_CORNER[1], WET_PUDDLE[3]))
    return out


def wet_ground(v):
    """assets/wet.webp and wet_mirror.webp round the corner, from their before copies (WET_SRC, WET_BOX): the ground under
    the canopy as the rain has it now (WET_*, drip_points). The same bytes each run."""
    L = layout(v); ms = L['mach']; C = L['canopy']; xe = XH + C['proj']
    x0, r0, x1, r1 = WET_BOX
    pw, pm = os.path.join(ROOT, 'assets', 'wet.webp'), os.path.join(ROOT, 'assets', 'wet_mirror.webp')
    wet = np.asarray(Image.open(pw).convert('RGB')).copy(); mir = np.asarray(Image.open(pm).convert('RGB')).copy()
    wb = np.asarray(Image.open(os.path.join(EDITS, WET_SRC[0])).convert('RGB')).astype(float)
    mb = np.asarray(Image.open(os.path.join(EDITS, WET_SRC[1])).convert('RGB')).astype(float)[0]
    R, G, B = wb[..., 0].copy(), wb[..., 1].copy(), wb[..., 2].copy()
    xs = np.arange(x0, x1) + 0.5; rows = np.arange(r0, r1) + 0.5
    Xc, Yc = np.meshgrid(xs, rows)
    Zg = F * EYE / np.maximum(Yc - VY, 1e-3); Xg = (Xc - VX) * Zg / F
    # the mirror line: the side panel's foot, the fronts' foot, the painter's own past them
    ym0 = 560 + mb[:, 0] + mb[:, 1] / 256; ym = ym0.copy()
    near, far = P(ms[0][1], 0, ms[0][4]), P(ms[-1][1], 0, ms[-1][5])
    jo = WET_OLD[2] - x0
    for j, x in enumerate(xs):
        if x < BOX[0] or x >= WET_OLD[2]: continue
        if x < near[0]: ym[j] = near[1]
        elif x < far[0]: ym[j] = VY + F * EYE * (x - VX) / (F * ms[0][1])
        else: ym[j] = ym0[jo]
    cols = (xs >= BOX[0]) & (xs < WET_OLD[2])
    ground = Yc >= ym[None, :]
    # the old foot (the painter's lean-to's: the first wet row a column), its band taken down, the ground it stood on wet
    b_ = np.where((R > 0).any(0), (R > 0).argmax(0), R.shape[0])
    d = np.arange(R.shape[0])[:, None] - b_[None, :]
    R = np.where(cols[None, :] & (d >= 0), R * (1 - WET_OLD[0] * np.exp(-d / WET_OLD[1])), R)
    src = np.clip(2 * b_[None, :] - 1 - np.arange(R.shape[0])[:, None], 0, R.shape[0] - 1)
    fill = cols[None, :] & (d < 0) & ground
    R = np.where(fill, np.take_along_axis(R, src, 0), R)
    R = np.where(cols[None, :] & ~ground, 0, R); G = np.where(cols[None, :] & ~ground, 0, G); B = np.where(cols[None, :] & ~ground, 0, B)
    # the canopy's shelter: damp
    under = np.clip((xe - Xg) / 0.04, 0, 1) * np.clip((Zg - C['z0']) / 0.04, 0, 1) * np.clip((C['z1'] - Zg) / 0.04, 0, 1)
    R = np.where(ground & (R > 0), R * (1 - under) + np.clip(R * 0.25, 2, WET_SHELTER) * under, R)
    # the splash line, and a small puddle under each trickle
    xl = xe + DRIP_LIP[0]
    ends = np.clip((Zg - C['z0'] + 0.05) / 0.1, 0, 1) * np.clip((C['z1'] - Zg + 0.05) / 0.1, 0, 1)
    R = np.where(ground & (R > 0), R + WET_SPLASH[0] * np.exp(-((Xg - xl - WET_SPLASH[2]) / WET_SPLASH[1]) ** 2) * ends, R)
    for n_, (Z, rate, size) in enumerate(drip_points(v)):
        if not size: continue
        u = np.sin(n_ * 78.233 + 12.9898) * 43758.5453 % 1.0          # (each its own size and place, a little)
        size = size * (0.8 + 0.4 * u); xo = xl + WET_SPLASH[2] + 0.03 * (u - 0.5)
        e = ((Zg - Z) / (WET_PUDDLE[0] * size)) ** 2 + ((Xg - xo) / (WET_PUDDLE[1] * size)) ** 2
        k = np.clip((1 - e) / 0.35, 0, 1) * ground
        B = np.maximum(B, 255 * k); R = np.maximum(R, WET_PUDDLE[2] * k)
    # the bench's puddle soft, fading out before the oden's edge
    bx0, by0, bx1, by1, bs, (bcx, bcy), (bax, bay) = WET_BENCH
    from scipy.ndimage import gaussian_filter as gf
    sl = (slice(by0 - r0, by1 - r0), slice(bx0 - x0, bx1 - x0))
    el = np.clip(1.6 * (1 - ((Xc[sl] - bcx) / bax) ** 2 - ((Yc[sl] - bcy) / bay) ** 2), 0, 1)
    pb = (B[sl] > 0)
    Bs, Rs = gf(B[sl], bs), gf(R[sl], bs)
    base = np.where(pb, np.median(R[sl][~pb]) if (~pb).any() else 20.0, R[sl])
    B[sl] = Bs * el
    R[sl] = np.where(pb | (Bs > 1), base + (Rs - base) * el, R[sl])
    # a puddle before the side panel, its still water taking the panel's light
    k = np.zeros(R.shape)
    for (cx, cy), (ax, ay) in WET_PANEL[:2]:
        k = np.maximum(k, np.clip((1 - ((Xc - cx) / ax) ** 2 - ((Yc - cy) / ay) ** 2) / WET_PANEL[3], 0, 1))
    k = k * ground
    B = np.maximum(B, 255 * k); R = np.maximum(R, WET_PANEL[2] * k)
    wet[r0 - 600:r1 - 600, x0:x1] = np.dstack([np.clip(np.round(c), 0, 255) for c in (R, G, B)]).astype(np.uint8)
    q = np.clip(ym - 560, 0, 255.996); hi = np.floor(q); lo = np.clip(np.round((q - hi) * 256), 0, 255)
    mir[0, x0:x1, 0] = hi.astype(np.uint8); mir[0, x0:x1, 1] = lo.astype(np.uint8)
    Image.fromarray(wet, 'RGB').save(pw, 'WEBP', lossless=True, quality=100, method=6, exact=True)
    Image.fromarray(mir, 'RGB').save(pm, 'WEBP', lossless=True, quality=100, method=6, exact=True)


def load(path):
    return np.asarray(Image.open(path).convert('RGBA')).astype(float)


def save(arr, path, mode='RGBA'):
    Image.fromarray(np.clip(np.round(arr), 0, 255).astype(np.uint8), mode).save(path, 'WEBP', lossless=True, quality=100, method=6, exact=True)


def sun_mask(city, v):
    """assets/street_sun.webp (R: how much of a pixel's colour is the low sun's, its night the sky's cool light; written by
    tools/kirua_bay_window.py over the house first): the face as his boards under the bay are in it (FACE_UP[2]): over
    the zone its pixels (FACE_M), left of it its boards behind the tree and over the dagashi-ya (face_left_sel; that box
    first as it was before, tools/src/edits/sodaface_before_sun.webp). The same bytes each run."""
    pth = os.path.join(ROOT, 'assets', 'street_sun.webp')
    sun = np.asarray(Image.open(pth).convert('RGB')).copy()
    if FACE_M.get(v) is not None:
        bx0, by0, bx1, by1 = BOX
        sun[by0:by1, bx0:bx1][FACE_M[v]] = FACE_UP[2]
    x0, y0, x1, y1 = FACE_LEFT
    sun[y0:y1, x0:x1] = np.asarray(Image.open(os.path.join(EDITS, 'sodaface_before_sun.webp')).convert('RGB'))
    face, _ = face_left_sel(city)
    sun[y0:y1, x0:x1][face] = FACE_UP[2]
    Image.fromarray(sun, 'RGB').save(pth, 'WEBP', lossless=True, quality=100, method=6, exact=True)


def face_left_sel(city, box=FACE_LEFT):
    """What of the face left of the zone (FACE_LEFT) shows, in the painter's pixels (city): under the bay's sill line,
    over his sign's top (FACE_SIGN), right of the dagashi-ya's post (FACE_POST), all of it but the tree's leaves in
    front: his boards between the leaves (FACE_BOARDS: what is lighter, in areas too big to be a leaf's light, grown
    back to their edges; his dusk-lit pink, FACE_PINK, however small), the dark between two of them a few rows high or
    a pixel wide (his joints), his edge line down the last column, and the small holes in them (his dirt) with them.
    Returns it, and how far under the sill's line each pixel is."""
    from scipy import ndimage as ndi
    x0, y0, x1, y1 = box
    X, Y = np.meshgrid(np.arange(x0, x1) + 0.5, np.arange(y0, y1) + 0.5)
    c = city[y0:y1, x0:x1, :3]; lum = c @ [0.299, 0.587, 0.114]
    d_ = Y - (VY - (VY - FACE_SILL[1]) * (VX - X) / (VX - FACE_SILL[0]) + 2)
    lo, k, grow, big, hole, joint = FACE_BOARDS
    light = lum >= lo
    lab, n = ndi.label(ndi.binary_opening(light, np.ones((k, k))))
    sz = ndi.sum(np.ones(lum.shape), lab, np.arange(1, n + 1))
    bd = np.isin(lab, 1 + np.nonzero(sz >= big)[0])
    for _ in range(grow): bd |= ndi.binary_dilation(bd) & light
    bd |= (c[..., 0] > c[..., 2] + FACE_PINK[0]) & (lum > FACE_PINK[1])
    bd |= ndi.binary_closing(bd, np.ones((joint, 1))) | ndi.binary_closing(bd, np.ones((1, 3)))
    bd[:, -1] |= bd[:, -2]                     # (his dark edge line down the box's last column: the zone's boards beside it)
    lab, n = ndi.label(~bd)
    sz = ndi.sum(np.ones(lum.shape), lab, np.arange(1, n + 1))
    bd |= np.isin(lab, 1 + np.nonzero(sz < hole)[0])
    sg = np.interp(np.arange(x0, x1) + 0.5, [q[0] for q in FACE_SIGN], [q[1] for q in FACE_SIGN])
    post = (X < FACE_POST[0]) & (Y >= FACE_POST[1])
    return bd & (d_ >= 0) & (Y < sg[None, :]) & ~post, d_


def face_left(city, unlit, box):
    """Zone 'sodaface' (FACE_LEFT): the house's face left of the zone, behind the tree and over the dagashi-ya: all of it
    that shows (face_left_sel) his upper boards (upper_boards), under the bay's sill its shadow; the leaves, the post and
    the sign as they are. Returns what changed."""
    x0, y0, x1, y1 = box
    X = np.meshgrid(np.arange(x0, x1) + 0.5, np.arange(y0, y1) + 0.5)[0]
    face, d_ = face_left_sel(city, box)
    b_ = upper_boards(city, box, face)
    sill = (X >= FACE_SILL[2]) & face
    b_ = b_ * np.where(sill & (d_ < 1), FACE_SILL_SH[0], np.where(sill & (d_ < 2), FACE_SILL_SH[1], 1.0))[..., None]
    for a in (city, unlit):
        t_ = a[y0:y1, x0:x1, :3]
        t_[face] = b_[face]
    return face


def draw(city, unlit, box=BOX):
    """The zone (tools/redraw_zones.py, 'soda'): the layers changed in place; the comps written (the machines' where
    tools/bake_retouches.py copies them from; the ad's and A's window's in assets; the booth's window handed to
    redraw_zones, COMP_OUT); street.js; returns what changed in box. Zone 'sodaface' (FACE_LEFT): face_left()."""
    if tuple(box) == FACE_LEFT: return face_left(city, unlit, box)
    v = VARIANT
    x0, y0, x1, y1 = box
    new, unew, lit, off, m, what = build(v, city, unlit, box)
    cps = comps(v, lit, off, m, box)
    city[y0:y1, x0:x1, :3] = new; city[y0:y1, x0:x1, 3] = np.where(m, 255, city[y0:y1, x0:x1, 3])
    unlit[y0:y1, x0:x1, :3] = unew; unlit[y0:y1, x0:x1, 3] = np.where(m, 255, unlit[y0:y1, x0:x1, 3])
    save(cps['z7_vending'][0], os.path.join(RET, 'vend_z7_vending.webp'))
    save(cps['z7_vendoff'][0], os.path.join(RET, 'vend_z7_vendoff.webp'))
    for name in ('z7_adscreen', 'z7_bigscreen', 'win_z7_low'):
        f_ = os.path.join(ROOT, 'assets', name + '.webp')
        if name in cps and name != 'z7_bigscreen': save(cps[name][0], f_)
        elif os.path.exists(f_): os.remove(f_)
    for name, sh in cps.get('z7_bigscreen_clips', []):          # (the giant screen: a sheet a clip, and the static)
        save(sh, os.path.join(ROOT, 'assets', 'z7_bigscreen_%s.webp' % name))
    rz = sys.modules.get('__main__')
    if hasattr(rz, 'COMP_OUT'):                # (the booth's window: A's and C's; B has none, so the kiosk zone's comp goes too)
        if 'win_z7_kiosk' in cps: rz.COMP_OUT['soda'] = ['win_z7_kiosk', cps['win_z7_kiosk'][0], None]
        else: rz.COMP_OUT.pop('kiosk', None)
    f_ = os.path.join(ROOT, 'assets', 'win_z7_kiosk.webp')
    if 'win_z7_kiosk' not in cps and os.path.exists(f_): os.remove(f_)
    street_js(v, cps)
    wet_ground(v)
    sun_mask(city, v)
    return m


def preview(out, v=None):
    """The zone on the layers as the pipeline hands them over (not written): off, lit, in the stutter, x1 and x4."""
    v = v or VARIANT
    os.makedirs(out, exist_ok=True)
    x0, y0, x1, y1 = BOX
    city = load(os.path.join(ROOT, 'assets', 'layer_city_off.webp')); unlit = load(os.path.join(ROOT, 'assets', 'street_unlit.webp'))
    city[y0:y1, x0:x1] = load(os.path.join(EDITS, 'soda_before_city.webp'))
    old = city[y0:y1, x0:x1, :3].copy()
    new, unew, lit, off, m, what = build(v, city, unlit, BOX)
    cps = comps(v, lit, off, m, BOX)

    def lay(base, names):
        a = base.copy()
        for n_ in names:
            c, r = cps[n_]
            if n_ in ('z7_adscreen', 'z7_bigscreen'): c = c[:, :r[2] - r[0]]
            h, w = c.shape[:2]; al = c[..., 3:] / 255
            ya, xa = r[1] - y0, r[0] - x0
            a[ya:ya + h, xa:xa + w] = a[ya:ya + h, xa:xa + w] * (1 - al) + c[..., :3] * al
        return a
    lits = [n_ for n_ in ('z7_vending', 'win_z7_kiosk', 'z7_adscreen', 'z7_bigscreen', 'win_z7_low') if n_ in cps]
    views = {'before': old, 'off': new, 'lit': lay(new, lits), 'stutter': lay(lay(new, lits), ['z7_vendoff'])}
    for tag, a in views.items():
        for k in (1, 3):
            Image.fromarray(np.clip(np.round(a), 0, 255).astype(np.uint8)).resize(((x1 - x0) * k, (y1 - y0) * k), Image.NEAREST).save(os.path.join(out, '%s_%s_x%d.png' % (v, tag, k)))
    return views


if __name__ == '__main__':
    if '--guide' in sys.argv:
        i = sys.argv.index('--guide'); v, ctxp, out = sys.argv[i + 1:i + 4]
        os.makedirs(out, exist_ok=True)
        full = Image.open(ctxp).convert('RGB'); ctx = np.asarray(full)[CROP[1]:CROP[3], CROP[0]:CROP[2]]
        Image.fromarray(ctx).save(os.path.join(out, 'ctx_crop.png'))
        sign = Image.open(os.path.join(EDITS, 'soda_before_city.webp')).convert('RGB').crop((231 - BOX[0], 532 - BOX[1], 268 - BOX[0], 558 - BOX[1]))
        ad = Image.open(os.path.join(SRC, AD_MODEL)).convert('RGB').crop(AD_PANELS[0])
        sh = [Image.open(os.path.join(ROOT, 'assets', '%s_perk.webp' % n)).crop((0, 0, 32, 32)) for n in PERK_NAMES]
        guide(v, ctx, sign, ad, sh).save(os.path.join(out, 'guide_%s.png' % v))
        top_view(v).save(os.path.join(out, 'top_%s.png' % v)); lines(v, full).save(os.path.join(out, 'lines_%s.png' % v))
    elif '--fit' in sys.argv:
        i = sys.argv.index('--fit'); fit(sys.argv[i + 1], sys.argv[i + 2])
    elif '--preview' in sys.argv:
        i = sys.argv.index('--preview'); preview(sys.argv[i + 1], sys.argv[i + 2] if len(sys.argv) > i + 2 else None)
    elif '--ask-clip' in sys.argv:
        i = sys.argv.index('--ask-clip'); ask_clip(sys.argv[i + 1], sys.argv[i + 2] if len(sys.argv) > i + 2 else None)
    else:
        print(__doc__)
