#!/usr/bin/env python3
"""Clean-ups of the street drawn by an image-editing model, laid back into the painting (the owner's choice, package
clean-3): each zone's model output (tools/src/edits/<zone>_model.webp, from <zone>_prompt.txt) is brought back to the
painting's pixels and written as patches for tools/bake_retouches.py.

    python3 tools/redraw_zones.py            writes tools/src/retouches/<zone>_{city,unlit}.webp, the neon's glow texture
                                            and the closed shop's overlay (assets/shop_off.webp)
    python3 tools/redraw_zones.py --call Z   asks the model again for zone Z (OpenRouter, the key from the environment's
                                            vault or OPENROUTER_API_KEY), then rewrites everything; costs about 0.14 $

Always from the painter's own pixels (tools/src/edits/<zone>_before_{city,unlit}.webp, the layers before any edit), never
from layers already edited, so a second run writes the same bytes. Per zone:
- the model saw the crop brightened (255 (x/255)^0.5, enlarged with nearest pixels); its answer is boxed down to the
  painting's grid and darkened back (^2), then registered by the integer shift whose gradients best match the
  untouched surroundings (the model may move things by a pixel or two);
- each part of the zone is a polygon with its method:
    hist    the model's structure (its ranks), the painter's values (per-channel histogram matching inside the polygon):
            the painter's palette and value range, nothing else of the model's colours;
    detail  the painter's light, shading and colour (low frequencies, gaussian SIGMA, computed without the polygons of
            `fill`, which are filled from around them: what is removed there, like a smear, leaves no light behind) carry
            the model's fine structure (its luminance minus its own low frequencies, times K) in the painter's hue;
            `keep_lit` keeps the painter's crisp lit strokes as painted;
    copy    the painter's own pixels from beside (`src`: dx, dy), to continue a pavement where an object stood;
    direct  the model's pixels, their global tint brought back to the painting's (a per-channel line fitted on the
            surroundings); with `neon` they are split into the board as it is unlit (the base, in both layers) and the
            light the tubes add (the glow texture, additive, which street.js switches with the shop, the power and the
            red night): lit, base + glow is the model's picture; out, only the base;
- the unlit layer (the power cut) takes the same change as a ratio (unlit x new / old), the direct parts their base;
  `unlit='lf_ratio'` (the places that shut): the new picture times the painter's darkening, smoothed channel by channel.
The overlays street.js lays on a zone follow it (R10): the closed shop's (shop_off), the oden's lantern frames and its
door's sliding leaf (oden_overlays: from tools/src/edits/<name>_before.webp; after tools/oden_interior.py rewrites
assets/oden_door.webp, copy it there and run this again); a lit window's comp (the kiosk's win_z7_kiosk, `comp` and
`lit` parts: its new lit picture in the comp, the street under it the same darkened as the painter's shut one).
"""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter, binary_dilation

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDITS = os.path.join(ROOT, 'tools', 'src', 'edits')
OUT = os.path.join(ROOT, 'tools', 'src', 'retouches')
GAMMA = 2.0
VP = (700.0, 615.0)                            # the street's vanishing point (measured on the painting)
MODEL = 'google/gemini-3-pro-image'

ODEN_LANTERN = dict(warm=(398, 536, 424, 573))                    # the oden's paper lantern at rest (it swings: oden_lantern*)
def circle(cx, cy, r, n=48):
    """A round polygon (a sign seen face on)."""
    return [(cx + r * np.cos(2 * np.pi * i / n), cy + r * np.sin(2 * np.pi * i / n)) for i in range(n)]


ODEN_UNDER_BOX = [(468, 661), (485, 661), (485, 670), (468, 670)]   # the pavement under the box removed from the oden's front
ODEN_KEEP = [ODEN_LANTERN, dict(rect=(409, 536, 412, 542)),          # and its hook
             dict(rect=(424, 579, 460, 620)), dict(rect=(467, 564, 495, 619))]   # the door's and the window's glass (oden_interior)
ODEN_BOARD = [(475, 482), (510, 482), (510, 540), (475, 528)]       # its roof light box (oden_sign_*: the light it loses, exact)
# what street.js lays over the oden (R10) and copies its wall into: the lantern's frames (the wall behind it where it
# hung at rest) and the door's sliding leaf (its painted wooden bottom, resampled at each step: tools/oden_interior.py);
# their pixels that are the painter's wall take the same change as the layer under them
ODEN_OVL = dict(lantern=[('oden_lantern', 'city'), ('oden_lantern_off', 'unlit')], lantern_box=(390, 528, 46, 56), lantern_n=23,
                lantern_hook=(410.31, 537.0), lantern_angles=[-7.5 + 0.5 * i for i in range(23)],   # (street.js ODEN.lantern)
                door='oden_door', pan_box=(421, 580, 40, 91), pan_wood=621,   # (its wood: below the glass, y 621)
                pan_cells=[[0, 122], [41, 122], [82, 122], [0, 214], [41, 214], [82, 214], [0, 306], [41, 306], [82, 306],
                           [0, 398], [41, 398], [82, 398], [0, 490], [41, 490], [82, 490], [0, 582], [41, 582]])
WALL_TOL = 24                                  # (a frame's pixel within this of the layer's is its wall, maybe lit by the lantern)
PAN_TOL = 40                                   # (the leaf's, resampled at each step: its lit edges are much further)

ZONES = {
    # the rooftop unit over the arcade: its side face was an illegible smudge; one fan guard in its perspective
    'fan': dict(box=(1296, 160, 1456, 320), scale=6, parts=[
        dict(poly=[(1361, 222), (1387, 207), (1387, 290), (1361, 290)], method='hist')]),
    # Ichiraku's front: a new signboard (the owner: a logo, a little depth), its plaster cleaned, the vent legible,
    # the painted steam smear removed (the animated puffs stay)
    'ramen': dict(box=(1090, 290, 1300, 570), scale=5, parts=[
        dict(poly=[(1106, 393), (1278, 302), (1278, 402), (1106, 466)], method='direct', neon=True, emblem=(1129, 408, 11)),
        dict(poly=[(1119, 462), (1266, 407), (1266, 560), (1236, 560), (1236, 502), (1168, 502), (1168, 560), (1119, 560)],
             method='detail', sigma=6.0, k=0.6,
             fill=[[(1134, 426), (1166, 426), (1166, 506), (1134, 506)],          # the painted steam smear
                   [(1130, 490), (1142, 490), (1142, 498), (1130, 498)],          # the lanterns' painted brackets:
                   [(1244, 459), (1256, 459), (1256, 467), (1244, 467)]])]),       # the wall lamps bring their own arms
    # Ichiraku's door, after the owner's choice among four (2026-11-12): no awning, no vent box; over the doorway a wooden
    # lattice transom lit from inside (V3), the plaster around it. The doorway itself, its glass and its frame stay as
    # painted: the closed shop's overlay (shop_off) and the life behind the glass are laid on them.
    'door': dict(box=(1100, 390, 1280, 580), scale=5, parts=[
        dict(poly=[(1119, 452), (1266, 397), (1266, 472), (1119, 500)], method='direct')]),
    # the plaster below, on both sides of the door, down to the pavement (the owner: the bottom was all grain, the top
    # clean; one wall, one finish). The menu board and its frame stay as painted (Luffy's posters are laid in it).
    'base': dict(box=(1100, 530, 1280, 740), scale=5, parts=[
        dict(poly=[(1118, 556), (1157, 556), (1157, 729), (1118, 729)], method='detail', sigma=6.0, k=0.6,
             cut=[[(1125, 573), (1155, 573), (1155, 651), (1125, 651)]]),
        dict(poly=[(1232, 556), (1267, 556), (1267, 731), (1232, 731)], method='detail', sigma=6.0, k=0.6)]),
    # the karate dojo at the street's left edge: its noren (four indigo panels on a rod), its shoji's lattice, its
    # signboard 心源流, its plaster strip and kick-panels, all cleaned of their grain. The dojo shuts by the hour (street.js
    # HRS: the unlit layer shown over it), so the unlit layer gets the new picture darkened as the painter darkened his.
    'dojo': dict(box=(0, 400, 160, 720), scale=5, parts=[
        dict(poly=[(0, 458), (100, 458), (100, 720), (0, 720)], method='direct', unlit='lf_ratio'),
        dict(poly=[(0, 530), (80, 530), (80, 688), (0, 688)], method='hist', unlit='lf_ratio')]),   # the shoji: the painter's warm light
    # the oden shop's front: its blotchy walls and eave cleaned (the painter's light, the drawing's planks), its noren
    # redrawn crisp; the glass of its door and window (tools/oden_interior.py), its roof light box (oden_sign_*), its
    # paper lantern left as they are (its frames and the door's sliding leaf carry the wall: oden_overlays). It shuts.
    # the tobacco kiosk (the cabin behind its glass: tools/tabako_window.py, lit by its comp win_z7_kiosk; the draft was
    # asked of it lit): the two enamel plates under the window, its pale ledge, its planks cleaned. Shut and power cut
    # are the same layer here.
    # the Pokemon Center's ball sign (lit by its comp z4_emblem): a clean sphere, no outline (the owner: "si c'est une
    # sphère, il y a de l'ombre sur le côté, pas de contour"): the painter's dark rim around it gives way to the street
    # behind; the ball itself lit in the comp, the same darkened in the street (the sign off, the power cut)
    'pokeball': dict(box=(838, 440, 912, 510), scale=8, comp=('z4_emblem', (849, 450)), despeckle=30, parts=[
        dict(poly=circle(870.5, 470.5, 25), method='direct', unlit='lf_ratio', outside_comp=True),   # the rim, gone
        dict(poly=circle(870.5, 470.5, 25), method='direct', fit='self_red', glow=(871.0, 470.5, 9.0), lit=True, cover=1)]),
        # the ball, lit: the drawing's sphere in the painter's colours, its button glowing as the painter's did
    # the kiosk's planks above its window, up to its roof: their pale stains gone (R9: the wall cleaned whole, with the
    # planks under the sign); the sign, the roof's edge, the neighbour's eave lines and the post kept
    'kiosktop': dict(box=(224, 420, 280, 560), scale=8, parts=[
        dict(poly=[(240, 437), (277, 483), (277, 560), (229, 560), (229, 474), (240, 474)], method='detail',
             sigma=6.0, k=0.6, keep=[dict(rect=(231, 530, 270, 560))])]),                              # (the sign)
    'kiosk': dict(box=(224, 560, 280, 690), scale=8, comp=('win_z7_kiosk', (230, 575)), parts=[
        dict(poly=[(229, 561), (277, 561), (277, 690), (229, 690)], method='detail', sigma=6.0, k=0.6,       # the planks
             cut=[[(229, 574), (271, 574), (271, 649), (229, 649)], [(229, 650), (267, 650), (267, 679), (229, 679)]]),
        dict(poly=[(229, 650), (267, 650), (267, 670), (229, 670)], method='hist'),                        # the plates
        dict(poly=[(229, 670), (267, 670), (267, 679), (229, 679)], method='hist'),                        # the ledge
        # its lit cabin as the owner chose among three shown in the street (B): a Showa tobacco shop's service window,
        # a low glass showcase of packs under a sliding pane, a cash tray on it (kiosk_optB_model.webp); the first
        # redraw, crisper but the same, was not kept ("je comprends pas ce qui a changé")
        dict(poly=[(230, 575), (270, 575), (270, 648), (230, 648)], method='direct', fit='self', lit=True, shut_k=0.6,
             model='kiosk_optB_model.webp')]),
    'oden': dict(box=(390, 462, 525, 690), scale=5, parts=[
        dict(poly=[(398, 537), (463, 537), (503, 548), (503, 664), (398, 684)], method='detail', sigma=10.0, k=0.7, unlit='lf_ratio',   # its walls, the door's wood
             # (sigma 10: its blotches are five pixels wide, wider than Ichiraku's grain; its light falls off over twenty)
             keep=ODEN_KEEP + [dict(warm=(463, 538, 500, 562))],                                 # the two lamps over the window
             # the box under the window (two stacked capsule machines or a menu? unreadable at 12 x 36 px, "les boîtes aux
             # lettres") and the two red dots by it go (R7): the planks run down to the pavement
             erase=[[(468, 628), (484, 628), (484, 660), (468, 660)], [(483, 628), (502, 628), (502, 640), (483, 640)]],
             cut=[ODEN_UNDER_BOX]),                                   # (the wall's foot there is at y 660: the box stood on the pavement)
        dict(poly=ODEN_UNDER_BOX, method='copy', src=(17, 0)),       # the pavement it stood on: the pavement beside it, same rows
        dict(poly=[(420, 507), (465, 507), (465, 521), (514, 531), (514, 553), (463, 541), (420, 537)], method='detail',
             sigma=4.0, k=0.8, unlit='lf_ratio', feather=3, cut=[ODEN_BOARD],                # the eave, faded into the roof
             keep=[dict(warm=(436, 519, 457, 540))]),                                           # (the lamp over the noren)
        dict(poly=[(420, 537), (463, 537), (463, 580), (420, 580)], method='hist', unlit='lf_ratio',
             keep=ODEN_KEEP + [dict(warm=(436, 519, 457, 540))])]),                              # the noren
}
SHOP_OFF = dict(src='shop_off_before.webp', out='shop_off.webp', at=(1112, 448), grow_top=28,   # (grown upward: the transom)
                clear=[(1128, 438), (1258, 398), (1258, 470), (1128, 498)],   # the old eave's and vent's lit strips, the dashes
                lit_from='door', lit_part=0)                                   # the lattice transom's warm light, shut
COMP_OUT = {}                                   # zone -> [comp name, its new pixels, its slice]: written by main
NEON_ZONE = 'ramen'
NEON_OUT = os.path.join(ROOT, 'assets', 'ichiraku_neon_glow.webp')

lum = lambda z: 0.299 * z[..., 0] + 0.587 * z[..., 1] + 0.114 * z[..., 2]


def load(path):
    return np.array(Image.open(path).convert('RGBA')).astype(float)


def poly_mask(P, box):
    x0, y0, x1, y1 = box
    m = Image.new('L', (x1 - x0, y1 - y0), 0)
    ImageDraw.Draw(m).polygon([(px - x0, py - y0) for px, py in P], fill=255)
    return np.array(m) > 127


def obj_masks(specs, orig, box):
    """What a part keeps as painted, by its shape rather than a box around it (R20): `rect` (x0, y0, x1, y1) as it is;
    `warm` the lit things in that box (a lantern, a lamp, a board: red over blue), grown by a pixel and their holes
    filled, so their dark ribs and outline go with them."""
    from scipy.ndimage import binary_fill_holes
    x0, y0, x1, y1 = box; k = np.zeros((y1 - y0, x1 - x0), bool)
    for sp in specs:
        if 'rect' in sp:
            a, b, c, d = sp['rect']; k[max(b - y0, 0):d - y0, max(a - x0, 0):c - x0] = True
        if 'warm' in sp:
            a, b, c, d = sp['warm']; r = np.zeros_like(k); r[b - y0:d - y0, a - x0:c - x0] = True
            w = r & (orig[..., 0] > 90) & (orig[..., 0] > orig[..., 2] + 30)
            k |= binary_fill_holes(binary_dilation(w, iterations=sp.get('grow', 1))) & binary_dilation(r, iterations=1)
    return k


def grad(z):
    l = lum(z); gx = np.zeros_like(l); gy = np.zeros_like(l)
    gx[:, 1:] = l[:, 1:] - l[:, :-1]; gy[1:] = l[1:] - l[:-1]
    return np.hypot(gx, gy)


def shift(a, dy, dx):
    """a moved by (dy, dx), its edge pixels repeated into what it uncovers (not wrapped round)."""
    h, w = a.shape[:2]; yi = np.clip(np.arange(h) - dy, 0, h - 1); xi = np.clip(np.arange(w) - dx, 0, w - 1)
    return a[yi][:, xi]


def register(e, orig, ref, reach=4):
    go = grad(orig); go = (go - go[ref].mean()) / (go[ref].std() + 1e-6); best = None
    for dy in range(-reach, reach + 1):
        for dx in range(-reach, reach + 1):
            g = grad(shift(e, dy, dx)); g = (g - g[ref].mean()) / (g[ref].std() + 1e-6)
            c = (g[ref] * go[ref]).mean()
            if best is None or c > best[0]: best = (c, dx, dy)
    return best


def lowpass_filled(img, hole, sigma):
    """Gaussian low frequencies of img, the pixels of `hole` left out (normalised convolution)."""
    w = (~hole).astype(float)
    num = np.stack([gaussian_filter(img[..., c] * w, sigma) for c in range(3)], -1)
    den = gaussian_filter(w, sigma)[..., None]
    # a hole wider than the kernel: widen until every pixel has support
    s = sigma
    while (den < 1e-3).any() and s < 64:
        s *= 1.6
        num = np.stack([gaussian_filter(img[..., c] * w, s) for c in range(3)], -1); den = gaussian_filter(w, s)[..., None]
    return num / np.maximum(den, 1e-6)


def zone(name, cfg, city, unlit):
    box = cfg['box']; x0, y0, x1, y1 = box; w, h = x1 - x0, y1 - y0
    city0, unlit0 = city[y0:y1, x0:x1].copy(), unlit[y0:y1, x0:x1].copy()
    orig = city0[..., :3]
    if cfg.get('nodraft'):                     # (a zone mended from its own pixels, no drawing asked for)
        e = orig.copy()
    else:
        e = np.array(Image.open(os.path.join(EDITS, f'{name}_model.webp')).convert('RGB').resize((w, h), Image.BOX)).astype(float) / 255.0
        e = (e ** GAMMA) * 255.0
    masks, keeps = [], []
    for p in cfg['parts']:
        m = poly_mask(p['poly'], box)
        for q in p.get('cut', []): m &= ~poly_mask(q, box)
        k = obj_masks(p.get('keep', []), orig, box); m &= ~k
        masks.append(m); keeps.append(k)
    on = None                                  # a lit window's zone (`comp`: its comp's name and place): the draft was
    if cfg.get('comp'):                        # made of it lit, the street with the comp laid on it
        cname, (cx, cy) = cfg['comp']; cb = load(os.path.join(EDITS, f'{name}_comp_before.webp')); ch, cw = cb.shape[:2]
        csl = (slice(cy - y0, cy - y0 + ch), slice(cx - x0, cx - x0 + cw)); ca = cb[..., 3:4] / 255.0
        on = orig.copy(); on[csl] = on[csl] * (1 - ca) + cb[..., :3] * ca
        cin = np.zeros((h, w), bool); cin[csl] = cb[..., 3] > 0
        cov = cin.copy(); grow = max([q.get('cover', 0) for q in cfg['parts']] + [0])
        if grow:                                   # (`cover`: the lit area grown by that many pixels, inside the comp's box:
            cbox = np.zeros_like(cin); cbox[csl] = True   # the redrawn sign's own edge lit with it, not left in the street)
            cov = binary_dilation(cin, iterations=grow) & cbox
    allm = np.any(masks, 0); ref = ~binary_dilation(allm, iterations=3); ref[:6] = ref[-6:] = False; ref[:, :6] = ref[:, -6:] = False
    if ref.sum() < 200:                        # (a zone redrawn whole: registered on all of it, its margins aside)
        ref = np.zeros_like(allm); ref[6:-6, 6:-6] = True
    if cfg.get('reg'):                         # (`reg`: where the drawing and the painting match, to register on)
        ref = poly_mask(cfg['reg'], box)
    corr, dx, dy = (1.0, 0, 0) if cfg.get('nodraft') else register(e, on if on is not None else orig, ref, cfg.get('reach', 4))
    e = shift(e, dy, dx)
    if cfg.get('persp'):                       # (`persp`: x where the drawing stands right. A drawing made face on, put on
        xc = cfg['persp']                      # a wall that runs to the vanishing point: each column's heights scaled
        X = np.arange(x0, x1) + 0.5            # about the eye line by its distance to VP over xc's, so its horizontals
        sc = (X - VP[0]) / (xc - VP[0])        # run to VP: the lintel rises, the step falls, toward the near side)
        Y = np.arange(y0, y1) + 0.5
        ysrc = VP[1] + (Y[:, None] - VP[1]) / sc[None, :] - y0 - 0.5
        yi = np.clip(np.round(ysrc).astype(int), 0, h - 1)
        e = e[yi, np.arange(w)[None, :]]
    if cfg.get('floor'):                       # (`floor`: yf, slope, xr. A drawing's step made level, its front edge put on
        yf, slope, xr = cfg['floor']           # the street's slope: below row yf each column pushed down by slope (x - xr),
        e = e.copy(); e0 = e.copy()            # what it uncovers the drawing's sill row: the recess floor seen as a wedge)
        for xi in range(w):
            d = int(round(slope * (x0 + xi + 0.5 - xr)))
            if d <= 0: continue
            r0 = yf - y0
            e[r0 + d:, xi] = e0[r0:h - d, xi]; e[r0:r0 + d, xi] = e0[r0, xi]
    e_zone = e

    def part_draft(fname):                     # (`model`: a part drawn from its own draft, the option chosen for it,
        ep = np.array(Image.open(os.path.join(EDITS, fname)).convert('RGB').resize((w, h), Image.BOX)).astype(float) / 255.0
        return shift((ep ** GAMMA) * 255.0, dy, dx)   # made from the same crop: the zone's registration holds)

    new, unew = orig.copy(), unlit0[..., :3].copy()
    glow = None
    for p, m, keep in zip(cfg['parts'], masks, keeps):
        pn, pu = new.copy(), unew.copy()           # (what the part is laid over: its feathered edge fades into it)
        e = part_draft(p['model']) if p.get('model') else e_zone
        is_lit = bool(p.get('lit')) and on is not None
        if is_lit: m = m & cov                       # (a lit part: the comp's pixels, taken lit)
        if p.get('outside_comp') and on is not None: m = m & ~cov   # (the street around a lit sign, not the sign)
        O = on if is_lit else orig
        if p['method'] == 'hist':
            out = O.copy()
            for c in range(3):
                src, refv = e[..., c][m], O[..., c][m]
                order = np.argsort(src, kind='stable'); v = np.empty_like(src); v[order] = np.sort(refv); out[..., c][m] = v
            if p.get('unlit') == 'lf_ratio':           # the unlit layer: this picture times the painter's darkening
                dark = np.stack([(gaussian_filter(unlit0[..., c], 4.0) + 1.0) / (gaussian_filter(O[..., c], 4.0) + 1.0) for c in range(3)], -1)
                new[m] = out[m]; unew[m] = np.clip(out * np.clip(dark, 0, 1.5), 0, 255)[m]
            else:
                ratio = (out + 1.0) / (O + 1.0)
                new[m] = out[m]; unew[m] = np.clip(unlit0[..., :3] * ratio, 0, 255)[m]
        elif p['method'] == 'detail':
            m = m.copy()
            if p.get('keep_lit'):
                Lo = lum(O); warm = ((O[..., 0] - O[..., 2]) > 10) & (Lo > 30)
                m &= ~(warm & ((Lo - gaussian_filter(Lo, 2.0)) > 4))
            hole = keep.copy()                     # (what is kept, a lantern or a lit pane, lends the wall none of its light)
            for q in p.get('fill', []): hole |= poly_mask(q, box)
            er = np.zeros_like(m)                  # `erase`: an object removed, the wall continued through it: no light
            for q in p.get('erase', []): er |= poly_mask(q, box)   # of its own, and the drawing's planks run down
            hole |= er                             # over it from the rows above (the draft drew the object there too)
            lf = lowpass_filled(O, hole, p['sigma'])
            le = lum(e)
            for x in np.nonzero(er.any(0))[0]:
                ys = np.nonzero(er[:, x])[0]; le[ys, x] = le[max(ys[0] - 1, 0), x]
            if keep.any():                         # the draft's own drawing of what is kept (a bright lamp, a pane) filled
                he = binary_dilation(keep, iterations=2)   # from around, else its edge rings dark on the wall beside it
                le = np.where(he, lowpass_filled(np.repeat(le[..., None], 3, -1), he, 2.0)[..., 0], le)
            hf = le - gaussian_filter(le, p['sigma'])
            out = np.clip(lf + p['k'] * hf[..., None] * (lf + 1.0) / (lum(lf) + 1.0)[..., None], 0, 255)
            ratio = (out + 1.0) / (O + 1.0)
            ul = unlit0[..., :3]
            if p.get('unlit') == 'lf_ratio':           # the painter's darkening, smoothed (a ratio pixel by pixel blows up
                if er.any():                       # (an erased object's own darkening left out, and all but this wall's)
                    dh = ~(m & ~er); dark = (lowpass_filled(ul, dh, 4.0) + 1.0) / (lowpass_filled(O, dh, 4.0) + 1.0)
                else:
                    dark = np.stack([(gaussian_filter(ul[..., c], 4.0) + 1.0) / (gaussian_filter(O[..., c], 4.0) + 1.0) for c in range(3)], -1)
                new[m] = out[m]; unew[m] = np.clip(out * np.clip(dark, 0, 1.5), 0, 255)[m]   # where a blotch was black)
            elif hole.any():                       # where the smear was, the unlit layer is rebuilt the same way
                ulf = lowpass_filled(ul, hole, p['sigma'])
                uout = np.clip(ulf + p['k'] * hf[..., None] * (ulf + 1.0) / (lum(ulf) + 1.0)[..., None], 0, 255)
                ur = np.where(hole[..., None], uout, np.clip(ul * ratio, 0, 255))
                new[m] = out[m]; unew[m] = ur[m]
            else:
                new[m] = out[m]; unew[m] = np.clip(ul * ratio, 0, 255)[m]
        elif p['method'] == 'direct':
            fit = m if p.get('fit') in ('self', 'self_red') else ref   # (`fit='self'`: the tint fitted on the part
            A = [np.polyfit(e[..., c][fit], O[..., c][fit], 1) for c in range(3)]   # itself, a sign's colours on the
            ec = np.stack([np.clip(A[c][0] * e[..., c] + A[c][1], 0, 255) for c in range(3)], -1)   # painter's own;
            if p.get('fit') == 'self_red':         # 'self_red': its red and its other colours fitted apart, so a white
                rd = (e[..., 0] > 1.4 * e[..., 1]) & (e[..., 0] > 40)   # half keeps the painter's white, not a pink)
                for grp in (rd, ~rd):
                    g = m & grp
                    if g.sum() < 20: continue
                    Ag = [np.polyfit(e[..., c][g], O[..., c][g], 1) for c in range(3)]
                    eg = np.stack([np.clip(Ag[c][0] * e[..., c] + Ag[c][1], 0, 255) for c in range(3)], -1)
                    ec[grp] = eg[grp]
            if p.get('glow'):                      # (`glow`: x, y, r: the painter's light there, where brighter, given back
                gx, gy, gr = p['glow']; yy, xx = np.mgrid[y0:y1, x0:x1]   # to the drawing, fading out to r: a lit button)
                wgt = np.clip(1 - np.hypot(xx + 0.5 - gx, yy + 0.5 - gy) / gr, 0, 1)[..., None]
                gl = np.stack([gaussian_filter(O[..., c], 1.5) - gaussian_filter(ec[..., c], 1.5) for c in range(3)], -1)
                ec = np.clip(ec + wgt * np.clip(gl, 0, 255), 0, 255)
            if p.get('neon'):
                # the tubes and their light: warm, saturated, brighter than the board around them
                L = lum(ec); sat = ec.max(-1) - ec.min(-1)
                warm = (ec[..., 0] > ec[..., 2] + 20) & (ec[..., 0] > ec[..., 1] + 10)
                lit = m & warm & (sat > 25)
                # the board as it is unlit: its colour from the non-lit pixels around (normalised convolution)
                bd = lowpass_filled(ec, ~m | lit, 3.0)
                # the emblem (a disc at `emblem`: x, y, radius) is painted, not a tube: it stays in the base
                if p.get('emblem'):
                    cx, cy, r = p['emblem']; yy, xx = np.mgrid[y0:y1, x0:x1]
                    lit &= ~(((xx - cx) ** 2 + (yy - cy) ** 2) <= r * r)
                core = lit & (L > np.percentile(L[lit], 60)) if lit.any() else lit
                base = ec.copy()
                base[lit] = bd[lit]
                base[core] = 0.7 * bd[core] + 0.3 * np.array([62.0, 39.0, 45.0])   # the glass of an unlit tube
                glow = np.clip(ec - base, 0, 255) * lit[..., None]
                if p.get('emblem'):                # the neon lights the emblem too: part of its brightness goes with the light
                    disc = m & (((xx - cx) ** 2 + (yy - cy) ** 2) <= r * r)
                    base[disc] = 0.55 * ec[disc]; glow[disc] = 0.45 * ec[disc]
                new[m] = base[m]; unew[m] = base[m]
            elif p.get('unlit') == 'lf_ratio':
                # the unlit layer: the new picture times the painter's own darkening there (unlit over lit, smoothed),
                # so the lattice is the new one and the shut dojo as dark as the painter made it
                sig = 4.0                              # (channel by channel: the shut colour too, not only the darkness)
                dark = np.stack([(gaussian_filter(unlit0[..., c], sig) + 1.0) / (gaussian_filter(O[..., c], sig) + 1.0) for c in range(3)], -1)
                new[m] = ec[m]; unew[m] = np.clip(ec * np.clip(dark, 0, 1.5), 0, 255)[m]
            else:
                new[m] = ec[m]; unew[m] = ec[m]
        elif p['method'] == 'flat':                # a strip in shadow, even: each row one value across the strip (its
                                                   # pct percentile: above the black crumbs that broke its edge),
            from scipy.ndimage import gaussian_filter1d   # then softened down the rows (sigma_y), both layers
            fc = p.get('from_cols')                # (`from_cols`: x0, x1: each row's value taken there instead, the wall
            for src, dst in ((O, new), (unlit0[..., :3], unew)):   # beside carried across the strip, row by row)
                rows = np.nonzero(m.any(1))[0]; fl = src.copy()
                for y in rows:
                    xs = np.nonzero(m[y])[0]; xsrc = np.arange(fc[0] - x0, fc[1] - x0) if fc else xs
                    fl[y, xs] = np.percentile(src[y, xsrc], p.get('pct', 50), axis=0)
                fl = gaussian_filter1d(fl, p.get('sigma_y', 1.5), axis=0)
                dst[m] = fl[m]
        elif p['method'] == 'shade':               # a shadow line: what is there darkened by f, both layers
            new[m] = new[m] * p['f']; unew[m] = unew[m] * p['f']
        elif p['method'] == 'copy':                # the painter's own pixels from beside (src: dx, dy), both layers
            sx, sy = p['src']
            new[m] = np.roll(np.roll(O, -sy, 0), -sx, 1)[m]; unew[m] = np.roll(np.roll(unlit0[..., :3], -sy, 0), -sx, 1)[m]
        if p.get('feather'):                       # its edge on the old painting: a ramp over `feather` pixels, no seam
            from scipy.ndimage import distance_transform_edt
            wgt = np.clip(distance_transform_edt(poly_mask(p['poly'], box)) / p['feather'], 0, 1)[..., None]
            new[m] = (wgt * new + (1 - wgt) * pn)[m]; unew[m] = (wgt * unew + (1 - wgt) * pu)[m]
        if is_lit:                                 # the new lit picture goes to the comp; the street under it (the window
            litp = new.copy()                      # shut) the same picture darkened as the painter's shut one, channel by
            if p.get('cover'):                     # (the grown edge: the darkening carried out from the old lit area)
                dark = (lowpass_filled(orig, ~cin, 2.0) + 1.0) / (lowpass_filled(on, ~cin, 2.0) + 1.0)
            else:
                dark = np.stack([(gaussian_filter(orig[..., c], 2.0) + 1.0) / (gaussian_filter(on[..., c], 2.0) + 1.0) for c in range(3)], -1)
            offp = np.clip(litp * np.clip(dark, 0, 1.5), 0, 255)   # channel; behind shut glass its detail as soft as
            if p.get('shut_k', 1.0) != 1.0:        # the painter's there (shut_k: the share of it kept)
                olf = np.stack([gaussian_filter(offp[..., c], 3.0) for c in range(3)], -1)
                offp = np.clip(olf + p['shut_k'] * (offp - olf), 0, 255)
            comp = COMP_OUT.setdefault(name, [cname, cb.copy(), csl])[1]
            sub = m[csl]; comp[..., :3][sub] = litp[csl][sub]; comp[..., 3][sub] = 255
            new[m] = offp[m]; unew[m] = np.clip(unlit0[..., :3] * (offp + 1.0) / (orig + 1.0), 0, 255)[m]
    if cfg.get('despeckle'):                   # (`despeckle` on the zone: what its parts laid side by side left as a lone
        from scipy.ndimage import median_filter   # bright pixel, the street's and the power cut's, takes its neighbours')
        done = np.any(masks, 0) | (cov if on is not None else False)
        for arr in (new, unew):
            med = np.stack([median_filter(arr[..., c], size=3) for c in range(3)], -1)
            spk = done & ((lum(arr) - lum(med)) > cfg['despeckle']); arr[spk] = med[spk]
    print(f'{name}: registered dx={dx} dy={dy} (gradient correlation {corr:.2f}); pixels changed {int((np.abs(new - orig).sum(-1) > 0).sum())}')
    city[y0:y1, x0:x1, :3], unlit[y0:y1, x0:x1, :3] = new, unew
    return glow, masks


def write_glow(glow, box):
    """The neon's light as street.js lays it (additive, alpha 255 where it adds anything): its bounding box."""
    x0, y0 = box[0], box[1]
    nz = glow.max(-1) > 2
    ys, xs = np.nonzero(nz)
    gx0, gy0, gx1, gy1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    g = glow[gy0:gy1, gx0:gx1]; a = (g.max(-1) > 2) * 255.0
    Image.fromarray(np.dstack([np.round(g), a]).astype(np.uint8), 'RGBA').save(NEON_OUT, 'WEBP', lossless=True, quality=100, method=6, exact=True)
    pos = dict(x=int(x0 + gx0), y=int(y0 + gy0), w=int(gx1 - gx0), h=int(gy1 - gy0))
    print('neon glow:', pos)
    return pos


def call(name):
    import base64, urllib.request
    cfg = ZONES[name]; x0, y0, x1, y1 = cfg['box']; s = cfg['scale']
    src = os.path.join(EDITS, f'{name}_before_on.webp')    # (a lit window's zone: the draft is asked of it lit)
    z = load(src if os.path.exists(src) else os.path.join(EDITS, f'{name}_before_city.webp'))[..., :3] / 255.0
    im = Image.fromarray((np.clip(z ** (1 / GAMMA), 0, 1) * 255).astype(np.uint8)).resize(((x1 - x0) * s, (y1 - y0) * s), Image.NEAREST)
    import io; buf = io.BytesIO(); im.save(buf, 'PNG')
    body = {"model": MODEL, "modalities": ["image", "text"], "usage": {"include": True}, "messages": [{"role": "user", "content": [
        {"type": "text", "text": open(os.path.join(EDITS, f'{name}_prompt.txt')).read().strip()},
        {"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()}}]}]}
    key = os.environ.get('OPENROUTER_API_KEY', 'proxy-injected')
    req = urllib.request.Request('https://openrouter.ai/api/v1/chat/completions', data=json.dumps(body).encode(),
                                 headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'})
    d = json.loads(urllib.request.urlopen(req, timeout=600).read())
    url = d['choices'][0]['message']['images'][0]['image_url']['url']
    Image.open(io.BytesIO(base64.b64decode(url.split(',', 1)[1]))).save(os.path.join(EDITS, f'{name}_model.webp'), 'WEBP', lossless=True, quality=100, method=6)
    print(name, 'model answer saved; cost', d.get('usage', {}).get('cost'), '$')


def shop_off(city, masks_by_zone):
    """The closed shop's overlay (street.js: shopOff, laid over the street as the kitchen shuts): its old pixels on the
    eave and the vent cleared, the lattice transom's warm light added as it looks shut (the wood without the shop's light)."""
    c = SHOP_OFF; ax, ay = c['at']
    so = load(os.path.join(EDITS, c['src']))
    g = c.get('grow_top', 0)                       # rows added above the old overlay (street.js lays it that much higher)
    so = np.concatenate([np.zeros((g,) + so.shape[1:]), so], 0); ay -= g
    H, W = so.shape[:2]; box = (ax, ay, ax + W, ay + H)
    so[poly_mask(c['clear'], box)] = 0
    zb = ZONES[c['lit_from']]['box']; m = masks_by_zone[c['lit_from']][c['lit_part']]
    full = np.zeros(city.shape[:2], bool); full[zb[1]:zb[3], zb[0]:zb[2]] = m
    sub = full[ay:ay + H, ax:ax + W]; px = city[ay:ay + H, ax:ax + W, :3]
    lit = sub & (px[..., 0] > px[..., 2] + 15) & (lum(px) > 40)
    so[lit, :3] = px[lit] * np.array([0.2, 0.17, 0.24]); so[lit, 3] = 255     # (as dark as the painter's shut glass)
    Image.fromarray(np.clip(np.round(so), 0, 255).astype(np.uint8), 'RGBA').save(
        os.path.join(ROOT, 'assets', c['out']), 'WEBP', lossless=True, quality=100, method=6, exact=True)
    print('shop_off: cleared the old eave and vent, the lattice transom shut:', int(lit.sum()), 'px')


def swung(mask, deg, hook, box):
    """A mask turned by deg degrees about the hook (absolute x, y), in its box (nearest pixel)."""
    x0, y0, x1, y1 = box; h, w = mask.shape; hx, hy = hook[0] - x0, hook[1] - y0
    yy, xx = np.mgrid[0:h, 0:w]; t = np.deg2rad(deg); c, s = np.cos(t), np.sin(t)
    X, Y = xx + 0.5 - hx, yy + 0.5 - hy
    ix = np.floor(c * X + s * Y + hx).astype(int); iy = np.floor(-s * X + c * Y + hy).astype(int)
    ok = (ix >= 0) & (ix < w) & (iy >= 0) & (iy < h); out = np.zeros_like(mask); out[ok] = mask[iy[ok], ix[ok]]
    return out


def oden_overlays(before, after):
    """The oden's overlays brought to its new wall: in the lantern's frames, the wall it uncovers where it hung takes the
    new wall (its planks continued from under it), the wall around (within WALL_TOL of the layer before) the layer's
    change there (after - before); in the door's sliding leaf, its wood resampled from the new layer; the lantern itself
    and the drawn bars left as they are. From the overlays as tools/oden_interior.py and the lantern tool wrote them
    (tools/src/edits/<name>_before.webp)."""
    from scipy.ndimage import binary_fill_holes
    o = ODEN_OVL; lx, ly, lw, lh = o['lantern_box']; lbox = (lx, ly, lx + lw, ly + lh)
    rest = obj_masks([ODEN_LANTERN], before['city'][ly:ly + lh, lx:lx + lw, :3], lbox)   # the lantern at rest
    for name, tag in o['lantern']:
        A = load(os.path.join(EDITS, name + '_before.webp')); b, a = before[tag], after[tag]
        old = b[ly:ly + lh, lx:lx + lw, :3]; d = a[ly:ly + lh, lx:lx + lw, :3] - old; n = 0
        behind = a[ly:ly + lh, lx:lx + lw, :3].copy()   # the new wall behind it: its planks run down, so each column
        for x in np.nonzero(rest.any(0))[0]:            # of the lantern takes the wall just under it
            ys = np.nonzero(rest[:, x])[0]; yb = min(ys[-1] + 1, lh - 1); behind[ys, x] = behind[yb, x]
        for k in range(o['lantern_n']):
            f = A[:, k * lw:(k + 1) * lw]; R, B = f[..., 0], f[..., 2]
            lit = ((R > 90) & (R > B + 30)) if tag == 'city' else ((R > 18) & (R > B + 5))   # (the paper, lit or dark crimson)
            lan = binary_fill_holes(binary_dilation(lit, iterations=1))   # the lantern in this frame: its paper, and its
            lan |= binary_dilation(swung(rest, -o['lantern_angles'][k], o['lantern_hook'], lbox), iterations=1)   # shape at rest swung
            wall = (f[..., 3] > 250) & ~lan
            under = wall & rest                       # where the lantern hung: the wall it uncovers as it swings
            f[..., :3][under] = behind[under]
            near = wall & ~rest & (np.abs(f[..., :3] - old).max(-1) <= WALL_TOL) & (np.abs(d).max(-1) > 0)
            f[..., :3][near] = np.clip(f[..., :3][near] + d[near], 0, 255); n += int(under.sum() + near.sum())
        Image.fromarray(np.round(A).astype(np.uint8), 'RGBA').save(os.path.join(ROOT, 'assets', name + '.webp'), 'WEBP', lossless=True, quality=100, method=6, exact=True)
        print(name + ':', n, 'wall pixels brought to the new wall')
    A = load(os.path.join(EDITS, o['door'] + '_before.webp')); b, a = before['city'], after['city']
    px, py, pw, ph = o['pan_box']; n = 0
    c00, c01, r00, r01 = 22, 38, 8, 89            # the leaf at rest (the first cell): its columns and rows in the box
    for u0, v0 in o['pan_cells']:                  # the leaf slides left and grows a little at each step: each of its
        f = A[v0:v0 + ph, u0:u0 + pw]; op = f[..., 3] > 250   # pixels taken back to the leaf at rest (nearest), its wood
        cols = np.nonzero(op.any(0))[0]        # (below the glass) the new wood there when it was the old one
        if len(cols) < 2: continue
        c0, c1 = cols[0], cols[-1]; rows = np.nonzero(op[:, (c0 + c1) // 2])[0]; r0, r1 = rows[0], rows[-1]
        for u in range(c0, c1 + 1):
            sx = px + int(round(c00 + (u - c0) * (c01 - c00) / max(c1 - c0, 1)))
            for r in np.nonzero(op[:, u])[0]:
                sy = py + int(round(r00 + (r - r0) * (r01 - r00) / max(r1 - r0, 1)))
                if sy < o['pan_wood'] or sy >= b.shape[0]: continue
                if np.abs(f[r, u, :3] - b[sy, sx, :3]).max() <= PAN_TOL and np.abs(a[sy, sx, :3] - b[sy, sx, :3]).max() > 0:
                    f[r, u, :3] = a[sy, sx, :3]; n += 1
    Image.fromarray(np.round(A).astype(np.uint8), 'RGBA').save(os.path.join(ROOT, 'assets', o['door'] + '.webp'), 'WEBP', lossless=True, quality=100, method=6, exact=True)
    print(o['door'] + ':', n, 'pixels of the sliding leaf brought to the new wood')


def main():
    if '--call' in sys.argv: call(sys.argv[sys.argv.index('--call') + 1])
    os.makedirs(OUT, exist_ok=True)
    city = load(os.path.join(ROOT, 'assets', 'layer_city_off.webp')); unlit = load(os.path.join(ROOT, 'assets', 'street_unlit.webp'))
    for name, cfg in ZONES.items():                # the painter's own pixels back in every zone first
        x0, y0, x1, y1 = cfg['box']
        city[y0:y1, x0:x1] = load(os.path.join(EDITS, f'{name}_before_city.webp'))
        unlit[y0:y1, x0:x1] = load(os.path.join(EDITS, f'{name}_before_unlit.webp'))
    masks_by_zone = {}; before = dict(city=city.copy(), unlit=unlit.copy())
    for name, cfg in ZONES.items():                # then the zones, in order: each sees the ones before it
        glow, masks = zone(name, cfg, city, unlit); masks_by_zone[name] = masks
        if name == NEON_ZONE and glow is not None:
            json.dump(write_glow(glow, cfg['box']), open(os.path.join(EDITS, 'neon_glow_box.json'), 'w'))
    for name, cfg in ZONES.items():                # the patches, cut from the finished layers (any order lays the same)
        x0, y0, x1, y1 = cfg['box']
        for tag, a in (('city', city), ('unlit', unlit)):
            Image.fromarray(np.clip(np.round(a[y0:y1, x0:x1]), 0, 255).astype(np.uint8), 'RGBA').save(
                os.path.join(OUT, f'{name}_{tag}.webp'), 'WEBP', lossless=True, quality=100, method=6, exact=True)
    shop_off(city, masks_by_zone)
    oden_overlays(before, dict(city=city, unlit=unlit))
    for name, (cname, comp, _) in COMP_OUT.items():   # a lit window's comp, its new picture where it lit before
        Image.fromarray(np.clip(np.round(comp), 0, 255).astype(np.uint8), 'RGBA').save(
            os.path.join(ROOT, 'assets', cname + '.webp'), 'WEBP', lossless=True, quality=100, method=6, exact=True)
        print(cname + ': the lit window redrawn')


if __name__ == '__main__':
    main()
