#!/usr/bin/env python3
"""Clean-ups of the street drawn by an image-editing model, laid back into the painting (the owner's choice, package
clean-3): each zone's model output (tools/src/edits/<zone>_model.webp, from <zone>_prompt.txt) is brought back to the
painting's pixels and written as patches for tools/bake_retouches.py.

    python3 tools/redraw_zones.py            writes tools/src/retouches/<zone>_{city,unlit}.webp (+ the neon's glow texture)
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
- the unlit layer (the power cut) takes the same change as a ratio (unlit x new / old), the direct parts their base.
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

ZONES = {
    # the rooftop unit over the arcade: its side face was an illegible smudge; one fan guard in its perspective
    'fan': dict(box=(1296, 160, 1456, 320), scale=6, parts=[
        dict(poly=[(1361, 222), (1387, 207), (1387, 290), (1361, 290)], method='hist')]),
    # Ichiraku's front: a new signboard (the owner: a logo, a little depth), its plaster cleaned, the vent legible,
    # the painted steam smear removed (the animated puffs stay)
    'ramen': dict(box=(1090, 290, 1300, 570), scale=5, parts=[
        dict(poly=[(1106, 393), (1278, 302), (1278, 402), (1106, 466)], method='direct', neon=True, emblem=(1129, 408, 11)),
        dict(poly=[(1119, 462), (1266, 407), (1266, 560), (1236, 560), (1236, 502), (1168, 502), (1168, 560), (1119, 560)],
             method='detail', sigma=6.0, k=0.6, keep_lit=True,
             fill=[[(1134, 426), (1166, 426), (1166, 506), (1134, 506)]])]),
}
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


def zone(name, cfg):
    box = cfg['box']; x0, y0, x1, y1 = box; w, h = x1 - x0, y1 - y0
    city0, unlit0 = load(os.path.join(EDITS, f'{name}_before_city.webp')), load(os.path.join(EDITS, f'{name}_before_unlit.webp'))
    orig = city0[..., :3]
    e = np.array(Image.open(os.path.join(EDITS, f'{name}_model.webp')).convert('RGB').resize((w, h), Image.BOX)).astype(float) / 255.0
    e = (e ** GAMMA) * 255.0
    masks = [poly_mask(p['poly'], box) for p in cfg['parts']]
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
            else:
                new[m] = ec[m]; unew[m] = ec[m]
    print(f'{name}: registered dx={dx} dy={dy} (gradient correlation {corr:.2f}); pixels changed {int((np.abs(new - orig).sum(-1) > 0).sum())}')
    city1, unlit1 = city0.copy(), unlit0.copy()
    city1[..., :3], unlit1[..., :3] = new, unew
    for tag, a in (('city', city1), ('unlit', unlit1)):
        Image.fromarray(np.clip(np.round(a), 0, 255).astype(np.uint8), 'RGBA').save(
            os.path.join(OUT, f'{name}_{tag}.webp'), 'WEBP', lossless=True, quality=100, method=6, exact=True)
    return glow


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


def main():
    if '--call' in sys.argv: call(sys.argv[sys.argv.index('--call') + 1])
    os.makedirs(OUT, exist_ok=True)
    for name, cfg in ZONES.items():
        glow = zone(name, cfg)
        if name == NEON_ZONE and glow is not None:
            pos = write_glow(glow, cfg['box'])
            json.dump(pos, open(os.path.join(EDITS, 'neon_glow_box.json'), 'w'))


if __name__ == '__main__':
    main()
