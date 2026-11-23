#!/usr/bin/env python3
"""The giant screen on Kirua's house switched off: what an outdoor LED screen's face is when it is dark, in its frame's
perspective, in the street's night.

    (a module: tools/redraw_zones.py's zone 'screenoff', the last, calls draw(city, unlit, box) on the street as the
     zones before it leave it: both layers in its box, the same bytes each time)
    python3 tools/screen_off.py --before       once: the zone's before crops (tools/src/edits/screenoff_before_*.webp)
    python3 tools/screen_off.py --preview DIR  both layers' box before and after, x1 and x6 (nothing written)

What was there: the screen's box (tools/soda_corner.py, layout B: 4.20 x 1.50 m, 10 cm off the house's front, its frame
7 cm) and in it, wherever its clips are not playing (late at night, NHOURS.screen [8.5, 25]; the power cut; while it
fades, openK('screen')), one flat near-black glass (11, 13, 21) with a faint smooth ramp: a panel of nothing.

What a switched-off outdoor screen is (checked on makers' pages: Hikvision's and Unilumin's outdoor fixed displays, die-cast
cabinets of 960 x 960 mm and the like, front-serviced modules of 320 x 160 mm, P4 to P10; Daktronics' notes on ambient
contrast: louvres over each row of LEDs shade them from the sky, a deep matte black paint on the louvres and textured
module faces that diffuse what they reflect instead of mirroring it): a black matte face made of cabinets bolted
edge to edge, their joints a regular grid, each cabinet a few modules whose masks are never quite the same black,
the LED rows and their louvres far finer than a scene pixel here (P10: 0.6 to 0.7 px), so they read as a fine matte grain
along the rows, not as lines.

What it is now, in the screen's own geometry (soda_corner's camera: F 1400, VP (700, 615), the eye 1.5 m; the face the
box's front, X -6.23 m, Z 19.12..23.18, Y 2.79..4.15; each pixel SS x SS rays onto it):
- the active area 4.06 x 1.36 m: six cabinets across and two down (0.677 x 0.680 m, the 640 mm cabinets' kind), each two
  modules across and four down (0.338 x 0.170 m: 320 x 160 mm's); the cabinets' joints one crisp pixel each (vertical
  ones a plain column: a vertical line on the wall is upright; the two rows' joint on its ray to the vanishing point, a
  pixel a column), the lower cabinets' top lip just under it catching the sky a step lighter; each module's mask its
  own black within a level (MURA), the LED rows' louvres a grain along the rows (ROWS: one value a row of P10 and a
  module's length, each louvre strip being the module's own; each pixel the mean of its rays);
- its light, only what reaches it: the sky over the street, the same on the whole face (one tone, as the old glass's
  mean); the street lamp does not reach it (from its head, 8.9 m out on the right, the face lies 67 to 80 degrees off
  the lamp's nadir, past its hood's cut-off: in the painting it lights neither the boards round the screen nor its
  frame, the two layers are one there) and its mirror image falls far nearer the eye than the screen; the drinks
  machines and their side panel stand under the canopy, 1 m deep under the screen, their fronts facing the street below
  it and the panel facing the eye: none of their light can climb past the canopy onto a face behind their own fronts;
- its sheen, what its matte face sends back of the street (SHEEN): a vertical mirror parallel to the camera's axis keeps
  each pixel's row, its reflected ray reaching the far right of the street at nearly three times its depth (tools/
  ichiraku_interior.py's mirror_source, with the right fronts' plane X 5.53): the end house's gable, the cherry and the
  dusk sky over them, there each layer's own (the far layers under the street's where it is transparent), taken through
  a matte face's wide lobe (a blur of SHEEN[1] px) and at a share of a few hundredths (Fresnel at 72-75 degrees, the
  louvres and the textured mask taking most of it): a faint lift, a hair warmer toward the top;
- both layers: the same face, its sheen each layer's own; the hours and the red night grade it as the street (its glass
  stays out of the low-sun mask, as its frame); only the pixels the clips cover whole in every frame are written (the
  comp's alpha is 255 there: the glass's sub-pixel coverage 1, soda_corner's own), so when the screen is on nothing of
  this shows round its pictures, and the glass's edge pixels (the comp's partial alpha) stay as they were. Needs Pillow,
  numpy, scipy.
"""
import os
import sys
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDITS = os.path.join(ROOT, 'tools', 'src', 'edits')
ASSETS = os.path.join(ROOT, 'assets')
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import soda_corner as S                           # (the screen's box, its camera, its glass's coverage)

BOX = (241, 418, 327, 540)                        # the zone (redraw_zones.py 'screenoff'): the comp z7_bigscreen's box
SS = 6                                            # rays a pixel, each way
LUM = np.array([0.299, 0.587, 0.114])
GRID = (6, 2, 2, 4)                               # cabinets across, down; modules a cabinet across, down
FACE = np.array([12.3, 14.95, 22.3])             # the matte black face in the night (with its sheen, the old glass's mean)
JOINT, LIP = 0.62, 1.14                           # a cabinets' joint (its gap, dark), the lower cabinets' top lip (lit by the sky)
MURA = (0.045, 0.03)                              # each cabinet's, each module's black: their spread (share of the face)
ROWS = (0.010, 0.08)                              # the LED rows (P10, m) and their louvres' spread (share), a value a row a module long
SHEEN = (0.035, 40.0)                             # the share of the street the face sends back, the lobe's blur (px)
X_R = 5.53                                        # the right fronts' plane in this camera (tools/ichiraku_interior.py X_F)
SEED = 23


def load(p, mode='RGBA'):
    return np.asarray(Image.open(p).convert(mode)).astype(float)


def save(a, p):
    Image.fromarray(np.clip(np.round(a), 0, 255).astype(np.uint8), 'RGBA' if a.shape[-1] == 4 else 'RGB').save(
        p, 'WEBP', lossless=True, quality=100, method=6, exact=True)


def geometry(box=BOX):
    """the face's pixels in box (where the glass covers the pixel whole: the comp's alpha 255 in every frame) and, for each
    pixel's SS x SS rays, where they meet the active area (u along it from its near end, w down from its top, m)"""
    b = S.layout('B')['bigscreen']; I = S.SCREEN_INSET
    gcov = S.screen_paint('B', box, 3)[3]
    face = gcov >= 1.0 - 1e-9
    dx, dy, X, Y = S.rays(box, SS)
    Z = b[1] / dx                                 # (the face's plane, X = b[1]: the box's front)
    Yw = S.EYE + dy * Z
    u = Z - (b[4] + I); w = (b[3] - I) - Yw
    W, H = b[5] - b[4] - 2 * I, b[3] - b[2] - 2 * I
    return face, u, w, W, H


def pattern(face, u, w, W, H):
    """the face's relative light, a pixel each: the cabinets' joints and lips, the modules' blacks, the rows' grain"""
    h, wd = face.shape
    nc, nr, mc, mr = GRID
    cw, ch = W / nc, H / nr
    rng = np.random.default_rng(SEED)
    cab = 1 + MURA[0] * rng.standard_normal((nr, nc))
    mod = 1 + MURA[1] * rng.standard_normal((nr * mr, nc * mc))
    rows = 1 + ROWS[1] * rng.standard_normal((int(np.ceil(H / ROWS[0])) + 2, nc * mc))   # (a row's louvre: a strip a module long)
    ci = np.clip(np.floor(u / cw), 0, nc - 1).astype(int); ri = np.clip(np.floor(w / ch), 0, nr - 1).astype(int)
    mi = np.clip(np.floor(u / (cw / mc)), 0, nc * mc - 1).astype(int); mj = np.clip(np.floor(w / (ch / mr)), 0, nr * mr - 1).astype(int)
    li = np.clip(np.floor(w / ROWS[0]), 0, len(rows) - 1).astype(int)
    sub = cab[ri, ci] * mod[mj, mi] * rows[li, mi]
    f = sub.reshape(h, SS, wd, SS).mean((1, 3))
    # the joints, crisp: the pixel whose middle is nearest each joint (its own column; on the rows' joint, a pixel a column)
    uc = u.reshape(h, SS, wd, SS).mean((1, 3)); wc = w.reshape(h, SS, wd, SS).mean((1, 3))
    du = np.abs(np.gradient(uc, axis=1)); dw = np.abs(np.gradient(wc, axis=0))
    joint = np.zeros(face.shape, bool); lip = np.zeros(face.shape, bool)
    for k in range(1, nc):
        joint |= np.abs(uc - k * cw) < du / 2
    for k in range(1, nr):
        on = np.abs(wc - k * ch) < dw / 2
        joint |= on
        lip |= np.roll(on, 1, axis=0) & ~on       # (the row under it: the lower cabinets' top edge, in the sky's light)
    f = np.where(joint, f * JOINT, np.where(lip, f * LIP, f))
    return f, joint, lip


def far_street(layer):
    """the street as it stands behind the screen's mirror (rest position): the sky, the far layers, the street's layer, its
    front layer; RGB float"""
    IW, IH, PAD = 1456, 816, 160
    sky = np.asarray(Image.open(os.path.join(ASSETS, 'layer_sky.webp')).convert('RGB').resize((IW + 2 * PAD, IH + 2 * PAD), Image.BILINEAR)).astype(float)[PAD:PAD + IH, PAD:PAD + IW]
    out = sky.copy()

    def over(a, x, y):
        nonlocal out
        h, w = a.shape[:2]; al = a[..., 3:] / 255.0
        out[y:y + h, x:x + w] = out[y:y + h, x:x + w] * (1 - al) + a[..., :3] * al
    over(load(os.path.join(ASSETS, 'fuji_night.webp')), 376, 66)
    over(load(os.path.join(ASSETS, 'fuji_tree.webp')), 376, 66)
    over(layer, 0, 0)
    over(load(os.path.join(ASSETS, 'fuji_front.webp')), 376, 66)
    return out


def sheen(layer, box=BOX):
    """what the face sends back of the street at each pixel of box: the street's pixel on the same row at the mirrored
    column (the reflected ray meets the right fronts' plane at Z (2 Xs - X_R) / Xs times the face's own depth), through
    the matte face's wide lobe, at its share"""
    from scipy.ndimage import gaussian_filter, map_coordinates
    b = S.layout('B')['bigscreen']; Xs = b[1]
    st = far_street(layer)
    blur = np.stack([gaussian_filter(st[..., c], SHEEN[1], mode='nearest') for c in range(3)], -1)
    x0, y0, x1, y1 = box
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(float)
    xc = xx + 0.5
    Zp = S.F * Xs / (xc - S.VX); Zf = Zp * (2 * Xs - X_R) / Xs; X = Xs * (2 - Zf / Zp)
    xq = S.VX + S.F * X / Zf - 0.5
    return np.stack([map_coordinates(blur[..., c], [yy, xq], order=1, mode='nearest') for c in range(3)], -1) * SHEEN[0]


def redraw(layer, box=BOX):
    """the face in a layer (RGBA float, whole): its new pixels over box and the mask of what is written"""
    face, u, w, W, H = geometry(box)
    f, _, _ = pattern(face, u, w, W, H)
    rgb = FACE[None, None, :] * f[..., None] + sheen(layer, box)
    return rgb, face


def draw(city, unlit, box=BOX):
    """tools/redraw_zones.py's zone 'screenoff': both layers, in place (the same face, its sheen each layer's); what changed"""
    x0, y0, x1, y1 = box; ch = np.zeros(city.shape[:2], bool)
    for a in (city, unlit):
        rgb, m = redraw(a, box)
        sub = a[y0:y1, x0:x1]; old = sub[..., :3].copy()
        sub[..., :3] = np.where(m[..., None], np.clip(np.round(rgb), 0, 255), old)
        ch[y0:y1, x0:x1] |= np.abs(sub[..., :3] - old).max(-1) > 0
    return ch


def before():
    """once: the zone's before crops (the overlapping zones' own before crops, in their order, over the layers' pixels
    where no zone is)"""
    import redraw_zones as R
    x0, y0, x1, y1 = BOX
    for tag, f in (('city', 'layer_city_off.webp'), ('unlit', 'street_unlit.webp')):
        a = load(os.path.join(ASSETS, f))[y0:y1, x0:x1].copy()
        for name, cfg in R.ZONES.items():
            if name == 'screenoff': continue
            b = cfg['box']
            ox0, oy0, ox1, oy1 = max(b[0], x0), max(b[1], y0), min(b[2], x1), min(b[3], y1)
            if ox0 >= ox1 or oy0 >= oy1: continue
            z = load(os.path.join(EDITS, '%s_before_%s.webp' % (name, tag)))
            a[oy0 - y0:oy1 - y0, ox0 - x0:ox1 - x0] = z[oy0 - b[1]:oy1 - b[1], ox0 - b[0]:ox1 - b[0]]
        save(a, os.path.join(EDITS, 'screenoff_before_%s.webp' % tag))
        print('screenoff_before_%s.webp' % tag, a.shape[1], 'x', a.shape[0])


def preview(out):
    """both layers' box before and after (from the current layers), x1 and x6"""
    os.makedirs(out, exist_ok=True)
    x0, y0, x1, y1 = BOX
    tiles = []
    for f in ('layer_city_off.webp', 'street_unlit.webp'):
        L = load(os.path.join(ASSETS, f))
        b = L[y0:y1, x0:x1, :3]
        rgb, m = redraw(L)
        a = np.where(m[..., None], np.clip(np.round(rgb), 0, 255), b)
        tiles += [b, a]
    for s in (1, 6):
        row = np.concatenate([np.concatenate([t, np.full((t.shape[0], 2, 3), 255.0)], 1) for t in tiles], 1)
        Image.fromarray(np.clip(np.round(row), 0, 255).astype(np.uint8)).resize((row.shape[1] * s, row.shape[0] * s), Image.NEAREST).save(os.path.join(out, 'screenoff_x%d.png' % s))
    print('face', int(m.sum()), 'px; tone', np.round((rgb[m] @ LUM).mean(), 2), 'range', np.round(np.percentile(rgb[m] @ LUM, [1, 50, 99]), 1))


if __name__ == '__main__':
    if '--before' in sys.argv: before()
    elif '--preview' in sys.argv: preview(sys.argv[sys.argv.index('--preview') + 1])
    else: print(__doc__)
