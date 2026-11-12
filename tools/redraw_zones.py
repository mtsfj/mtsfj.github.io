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
    direct  the model's pixels, their global tint brought back to the painting's (a per-channel line fitted on the
            surroundings); with `neon` they are split into the board as it is unlit (the base, in both layers) and the
            light the tubes add (the glow texture, additive, which street.js switches with the shop, the power and the
            red night): lit, base + glow is the model's picture; out, only the base;
- the unlit layer (the power cut) takes the same change as a ratio (unlit x new / old), the direct parts their base;
  `unlit='lf_ratio'` (the places that shut): the new picture times the painter's darkening, smoothed channel by channel.
The overlays street.js lays on a zone follow it (R10): the closed shop's (shop_off), the oden's lantern frames and its
door's sliding leaf (oden_overlays: from tools/src/edits/<name>_before.webp; after tools/oden_interior.py rewrites
assets/oden_door.webp, copy it there and run this again).
"""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter, binary_dilation

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDITS = os.path.join(ROOT, 'tools', 'src', 'edits')
OUT = os.path.join(ROOT, 'tools', 'src', 'retouches')
GAMMA = 2.0
MODEL = 'google/gemini-3-pro-image'

ODEN_LANTERN = [(399, 538), (422, 538), (422, 571), (399, 571)]   # the oden's paper lantern at rest (it swings: oden_lantern*)
ODEN_BOARD = [(475, 482), (510, 482), (510, 540), (475, 528)]       # its roof light box (oden_sign_*: the light it loses, exact)
# what street.js lays over the oden (R10) and copies its wall into: the lantern's frames (the wall behind it where it
# hung at rest) and the door's sliding leaf (its painted wooden bottom, resampled at each step: tools/oden_interior.py);
# their pixels that are the painter's wall take the same change as the layer under them
ODEN_OVL = dict(lantern=[('oden_lantern', 'city'), ('oden_lantern_off', 'unlit')], lantern_box=(390, 528, 46, 56), lantern_n=23,
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
    'oden': dict(box=(390, 462, 525, 690), scale=5, parts=[
        dict(poly=[(398, 537), (463, 537), (503, 548), (503, 664), (398, 684)], method='detail', sigma=10.0, k=0.7, unlit='lf_ratio',   # its walls, the door's wood
             # (sigma 10: its blotches are five pixels wide, wider than Ichiraku's grain; its light falls off over twenty)
             cut=[ODEN_LANTERN, [(422, 576), (462, 576), (462, 621), (422, 621)],              # the door's glass
                  [(462, 557), (497, 557), (497, 619), (462, 619)],                                 # the window's glass
                  [(466, 541), (476, 541), (476, 557), (466, 557)], [(484, 541), (494, 541), (494, 557), (484, 557)],   # its two lamps
                  [(469, 631), (481, 631), (481, 667), (469, 667)]]),                               # the menu board
        dict(poly=[(420, 507), (465, 507), (465, 521), (514, 531), (514, 553), (463, 541), (420, 537)], method='detail',
             sigma=4.0, k=0.8, unlit='lf_ratio', cut=[ODEN_BOARD, [(438, 521), (455, 521), (455, 538), (438, 538)]]),   # the eave (its lamp kept)
        dict(poly=[(420, 537), (463, 537), (463, 580), (420, 580)], method='hist', unlit='lf_ratio', cut=[ODEN_LANTERN])]),   # the noren
}
SHOP_OFF = dict(src='shop_off_before.webp', out='shop_off.webp', at=(1112, 448), grow_top=28,   # (grown upward: the transom)
                clear=[(1128, 438), (1258, 398), (1258, 470), (1128, 498)],   # the old eave's and vent's lit strips, the dashes
                lit_from='door', lit_part=0)                                   # the lattice transom's warm light, shut
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


def grad(z):
    l = lum(z); gx = np.zeros_like(l); gy = np.zeros_like(l)
    gx[:, 1:] = l[:, 1:] - l[:, :-1]; gy[1:] = l[1:] - l[:-1]
    return np.hypot(gx, gy)


def register(e, orig, ref):
    go = grad(orig); go = (go - go[ref].mean()) / (go[ref].std() + 1e-6); best = None
    for dy in range(-4, 5):
        for dx in range(-4, 5):
            g = grad(np.roll(np.roll(e, dy, 0), dx, 1)); g = (g - g[ref].mean()) / (g[ref].std() + 1e-6)
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
    e = np.array(Image.open(os.path.join(EDITS, f'{name}_model.webp')).convert('RGB').resize((w, h), Image.BOX)).astype(float) / 255.0
    e = (e ** GAMMA) * 255.0
    masks = []
    for p in cfg['parts']:
        m = poly_mask(p['poly'], box)
        for q in p.get('cut', []): m &= ~poly_mask(q, box)
        masks.append(m)
    allm = np.any(masks, 0); ref = ~binary_dilation(allm, iterations=3); ref[:6] = ref[-6:] = False; ref[:, :6] = ref[:, -6:] = False
    corr, dx, dy = register(e, orig, ref)
    e = np.roll(np.roll(e, dy, 0), dx, 1)
    new, unew = orig.copy(), unlit0[..., :3].copy()
    glow = None
    for p, m in zip(cfg['parts'], masks):
        if p['method'] == 'hist':
            out = orig.copy()
            for c in range(3):
                src, refv = e[..., c][m], orig[..., c][m]
                order = np.argsort(src, kind='stable'); v = np.empty_like(src); v[order] = np.sort(refv); out[..., c][m] = v
            if p.get('unlit') == 'lf_ratio':           # the unlit layer: this picture times the painter's darkening
                dark = np.stack([(gaussian_filter(unlit0[..., c], 4.0) + 1.0) / (gaussian_filter(orig[..., c], 4.0) + 1.0) for c in range(3)], -1)
                new[m] = out[m]; unew[m] = np.clip(out * np.clip(dark, 0, 1.5), 0, 255)[m]
            else:
                ratio = (out + 1.0) / (orig + 1.0)
                new[m] = out[m]; unew[m] = np.clip(unlit0[..., :3] * ratio, 0, 255)[m]
        elif p['method'] == 'detail':
            m = m.copy()
            if p.get('keep_lit'):
                Lo = lum(orig); warm = ((orig[..., 0] - orig[..., 2]) > 10) & (Lo > 30)
                m &= ~(warm & ((Lo - gaussian_filter(Lo, 2.0)) > 4))
            hole = np.zeros_like(m)
            for q in p.get('fill', []): hole |= poly_mask(q, box)
            lf = lowpass_filled(orig, hole, p['sigma'])
            le = lum(e); hf = le - gaussian_filter(le, p['sigma'])
            out = np.clip(lf + p['k'] * hf[..., None] * (lf + 1.0) / (lum(lf) + 1.0)[..., None], 0, 255)
            ratio = (out + 1.0) / (orig + 1.0)
            ul = unlit0[..., :3]
            if p.get('unlit') == 'lf_ratio':           # the painter's darkening, smoothed (a ratio pixel by pixel blows up
                dark = np.stack([(gaussian_filter(ul[..., c], 4.0) + 1.0) / (gaussian_filter(orig[..., c], 4.0) + 1.0) for c in range(3)], -1)
                new[m] = out[m]; unew[m] = np.clip(out * np.clip(dark, 0, 1.5), 0, 255)[m]   # where a blotch was black)
                continue
            if hole.any():                         # where the smear was, the unlit layer is rebuilt the same way
                ulf = lowpass_filled(ul, hole, p['sigma'])
                uout = np.clip(ulf + p['k'] * hf[..., None] * (ulf + 1.0) / (lum(ulf) + 1.0)[..., None], 0, 255)
                ur = np.where(hole[..., None], uout, np.clip(ul * ratio, 0, 255))
            else:
                ur = np.clip(ul * ratio, 0, 255)
            new[m] = out[m]; unew[m] = ur[m]
        elif p['method'] == 'direct':
            A = [np.polyfit(e[..., c][ref], orig[..., c][ref], 1) for c in range(3)]
            ec = np.stack([np.clip(A[c][0] * e[..., c] + A[c][1], 0, 255) for c in range(3)], -1)
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
                dark = np.stack([(gaussian_filter(unlit0[..., c], sig) + 1.0) / (gaussian_filter(orig[..., c], sig) + 1.0) for c in range(3)], -1)
                new[m] = ec[m]; unew[m] = np.clip(ec * np.clip(dark, 0, 1.5), 0, 255)[m]
            else:
                new[m] = ec[m]; unew[m] = ec[m]
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
    z = load(os.path.join(EDITS, f'{name}_before_city.webp'))[..., :3] / 255.0
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


def oden_overlays(before, after):
    """The oden's overlays brought to its new wall: in the lantern's frames and in the door's sliding leaf, the pixels that
    are the wall (within WALL_TOL of the layer before) take the layer's change there (after - before), the lantern itself
    and the drawn bars left as they are. From the overlays as tools/oden_interior.py and the lantern tool wrote them
    (tools/src/edits/<name>_before.webp)."""
    o = ODEN_OVL; lx, ly, lw, lh = o['lantern_box']
    for name, tag in o['lantern']:
        A = load(os.path.join(EDITS, name + '_before.webp')); b, a = before[tag], after[tag]
        old = b[ly:ly + lh, lx:lx + lw, :3]; d = a[ly:ly + lh, lx:lx + lw, :3] - old; n = 0
        for k in range(o['lantern_n']):
            f = A[:, k * lw:(k + 1) * lw]
            wall = (f[..., 3] > 250) & (np.abs(f[..., :3] - old).max(-1) <= WALL_TOL) & (np.abs(d).max(-1) > 0)
            f[..., :3][wall] = np.clip(f[..., :3][wall] + d[wall], 0, 255); n += int(wall.sum())
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


if __name__ == '__main__':
    main()
