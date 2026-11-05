#!/usr/bin/env python3
"""止まれ sur la chaussée, dans le bon ordre : 止 au loin, ま, れ au plus près.

    python3 tools/tomare.py      (il reprend sa zone au commit BEFORE à chaque fois, on peut donc le relancer)

Le marquage au sol se lit dans le sens de la marche, du plus loin au plus près : 止 contre le passage piéton, puis ま, puis
れ. Le peintre avait mis れ au loin et 止 au plus près. ま reste ; 止 et れ changent de place.

La chaussée vue par l'œil de la rue : le point de fuite VP, la focale F, l'œil à EYE m du sol ; un point du sol à X m à
droite de l'axe et Z m devant se voit en x = VP_x + F X / Z, y = VP_y + F EYE / Z. Les deux places (LOIN, PRES : leurs
rangées) sont des rectangles du sol : la largeur et la longueur de la lettre qui y était (sa peinture, de la rangée où
elle commence à celle où elle finit). Chaque lettre va dans l'autre place à la même largeur et à la longueur de cette
place, en suivant la perspective.

- 止 au loin : la peinture du peintre (sa couverture, lue sur la chaussée de layer_city_off au commit BEFORE), portée par le
  sol de sa place à l'autre et moyennée sur chaque pixel (SUB x SUB points), ses bords en fondu comme les siens.
- れ au plus près : celle du loin n'a que 14 rangées, trop peu pour la grandir sans bouillie. La lettre est donc tirée
  d'une gothique (tools/src/tomare_re.png : れ en IPAGothic à 1000 px, épaissie de 24 px, l'épaisseur où les lettres du
  peintre lui ressemblent le plus), portée sur le sol de la même façon.

Dans chaque calque où la chaussée est peinte (layer_city_off, street_unlit, et les lumières au sol gl_* dont la boîte
touche les lettres : la peinture y renvoie plus de lumière que l'asphalte), chaque pixel est l'asphalte (un fond lisse,
moyenne des pixels d'asphalte voisins, surtout de la même rangée) plus la peinture (son surcroît, lisse aussi, moyenne
des pixels de peinture voisins) à sa couverture, plus le grain. Là où une lettre partait, l'asphalte et le grain d'un
pixel d'asphalte de la même rangée ; là où une lettre arrive, la peinture et le grain d'un pixel de peinture de la même
place. Ces pixels sont tirés au sort une fois (RNG), aux mêmes endroits pour tous les calques. Les autres pixels de la
chaussée restent tels quels ; ま, le passage piéton et sa ligne ne bougent pas. Il faut git, Pillow, numpy, scipy.
"""
import io
import os
import re
import subprocess
import numpy as np
from PIL import Image
from scipy import ndimage as nd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = lambda p: os.path.join(ROOT, 'assets', p)
BEFORE = '4faa10a'                   # (les calques avant cet outil : sa zone reprise de là à chaque fois)
ZONE = (560, 676, 840, 762)          # x0, y0, x1, y1 : la chaussée autour des trois lettres
COLS = (640, 760)                    # les colonnes des lettres
LOIN, PRES = (683, 696), (721, 750)  # les rangées des deux places (れ, puis 止 chez le peintre) ; ま de 698 à 718
GARDE = ((682, 697), (719, 752))     # les rangées où l'on peut toucher (ni ま, ni la ligne du passage à 680-681)
VP, F, EYE = (700, 615), 1400, 1.5   # le point de fuite, la focale, la hauteur de l'œil (m)
SUB = 6                              # points par côté de pixel
GLYPH = os.path.join(ROOT, 'tools', 'src', 'tomare_re.png')
SEED = 33

Zof = lambda y: F * EYE / (y - VP[1])
Xof = lambda x, Z: (x - VP[0]) * Z / F


def load(p, at=None):
    data = subprocess.run(['git', 'show', f'{at}:assets/{p}'], cwd=ROOT, capture_output=True, check=True).stdout if at else open(A(p), 'rb').read()
    return np.asarray(Image.open(io.BytesIO(data)).convert('RGBA')).astype(float)


def save(arr, p, mode='RGBA'):
    Image.fromarray(np.clip(np.round(arr), 0, 255).astype(np.uint8), 'RGBA').convert(mode).save(A(p), 'WEBP', lossless=True, quality=100, method=6, exact=True)


def couverture(L):
    """la peinture de la chaussée, de 0 à 1 : le bleu de chaque pixel entre l'asphalte de sa rangée (la médiane) et la peinture"""
    x0, y0, x1, y1 = ZONE
    b = L[y0:y1, x0:x1, 2]; c = np.zeros_like(b)
    for r in range(b.shape[0]):
        row = b[r]; a = np.median(row); m = row > a + 35
        p = np.percentile(row[m], 80) if m.sum() > 3 else a + 80
        c[r] = np.clip((row - a) / max(p - a, 1), 0, 1)
    return c


def place(cov, rows):
    """le rectangle du sol d'une place : la largeur de sa peinture, de sa première à sa dernière rangée"""
    x0, y0 = ZONE[:2]; xs = []
    for y in range(rows[0], rows[1] + 1):
        w = np.where(cov[y - y0, COLS[0] - x0:COLS[1] - x0] > 0.5)[0] + COLS[0]
        if len(w): Z = Zof(y + 0.5); xs += [Xof(w.min(), Z), Xof(w.max() + 1, Z)]
    return min(xs), max(xs), Zof(rows[1] + 1), Zof(rows[0])          # X gauche, X droite, Z près, Z loin


def porter(sample, dst, rows):
    """la couverture d'une lettre dans la place dst (ses rangées rows) : chaque pixel moyenné sur SUB x SUB points du sol ;
    sample(u, v) donne la lettre en (u à travers, v du loin au près), de 0 à 1"""
    x0, y0, x1, y1 = ZONE
    Xl, Xr, Zn, Zf = dst; out = np.zeros((y1 - y0, x1 - x0))
    xs = np.arange(x0, x1)
    for y in range(rows[0], rows[1] + 1):
        acc = np.zeros(x1 - x0)
        for i in range(SUB):
            Z = Zof(y + (i + 0.5) / SUB); v = (Zf - Z) / (Zf - Zn)
            if not 0 <= v < 1: continue
            for j in range(SUB):
                u = (Xof(xs + (j + 0.5) / SUB, Z) - Xl) / (Xr - Xl)
                ok = (u >= 0) & (u < 1)
                acc += np.where(ok, sample(np.clip(u, 0, 0.999999), v), 0)
        out[y - y0] = acc / (SUB * SUB)
    return out


def lisse(v, w, sy, sx):
    """moyenne des valeurs v là où w, à gaussienne (sy rangées, sx colonnes)"""
    num = nd.gaussian_filter(v * w[..., None], (sy, sx, 0)); den = nd.gaussian_filter(w.astype(float), (sy, sx))[..., None]
    return num / np.maximum(den, 1e-6)


def calques():
    """layer_city_off, street_unlit, et les lumières au sol dont la boîte touche les lettres (leur place lue dans street.js)"""
    out = [('layer_city_off.webp', (0, 0), 'RGBA'), ('street_unlit.webp', (0, 0), 'RGBA')]
    js = open(A('street.js'), encoding='utf-8').read()
    for m in re.finditer(r"url: 'assets/(gl_[a-z0-9_]+\.webp)\?v=\d+', box: \[(\d+), (\d+), (\d+), (\d+)\]", js):
        n, bx, by, bw, bh = m.group(1), *map(int, m.groups()[1:])
        if bx < COLS[1] and bx + bw > COLS[0] and by < GARDE[1][1] + 1 and by + bh > GARDE[0][0]: out.append((n, (bx, by), 'RGBA'))
    return out


def main():
    x0, y0, x1, y1 = ZONE
    cov = couverture(load('layer_city_off.webp', BEFORE))
    loin, pres = place(cov, LOIN), place(cov, PRES)
    # 止 : sa peinture (nette : sans les points isolés, sans trous), lue dans sa place à son endroit du sol
    to = cov.copy(); to[:PRES[0] - y0] = 0; to[PRES[1] + 1 - y0:] = 0; to[:, :COLS[0] - x0] = 0; to[:, COLS[1] - x0:] = 0
    m = nd.binary_fill_holes(to > 0.5); lab, n = nd.label(m); sz = nd.sum(m, lab, range(1, n + 1))
    m = np.isin(lab, 1 + np.where(sz >= 6)[0]).astype(float)
    def s_to(u, v):
        Xl, Xr, Zn, Zf = pres; Z = Zf - v * (Zf - Zn); X = Xl + u * (Xr - Xl)
        sy = VP[1] + F * EYE / Z - 0.5 - y0; sx = VP[0] + F * X / Z - 0.5 - x0
        return nd.map_coordinates(m, [np.full_like(sx, sy), sx], order=1, mode='constant')
    g = np.asarray(Image.open(GLYPH).convert('L')) > 127; gh, gw = g.shape
    s_re = lambda u, v: g[int(v * gh), (u * gw).astype(int)].astype(float)
    new = porter(s_to, loin, LOIN) + porter(s_re, pres, PRES)
    # ce qui part : la peinture des deux places, d'un pixel plus large ; seulement dans leurs rangées
    old = np.zeros_like(cov, bool)
    for (r0, r1) in GARDE:
        old[r0 - y0:r1 + 1 - y0, COLS[0] - x0 - 2:COLS[1] - x0 + 2] = nd.binary_dilation(cov > 0.12)[r0 - y0:r1 + 1 - y0, COLS[0] - x0 - 2:COLS[1] - x0 + 2]
    touch = old | (new > 0)
    clean = (nd.binary_dilation(cov > 0.05) == 0)                       # l'asphalte : aucun pixel de peinture autour
    paint = cov > 0.85
    # les pixels tirés au sort, une fois : un asphalte de la même rangée (à 40 colonnes au plus), une peinture de la même place
    rng = np.random.default_rng(SEED); H, W = cov.shape
    pa = np.zeros((H, W, 2), int); pp = np.zeros((H, W, 2), int)
    paint[:, :COLS[0] - x0] = False; paint[:, COLS[1] - x0:] = False
    for r, c in zip(*np.where(touch)):
        for d in range(40, W, 10):                                        # (au plus près, plus loin si la rangée est peinte)
            cs = np.where(clean[r, max(0, c - d):c + d + 1])[0] + max(0, c - d)
            if len(cs) >= 8: break
        pa[r, c] = (r, cs[rng.integers(len(cs))])
        r0, r1 = LOIN if r + y0 <= GARDE[0][1] else PRES; rr = np.arange(r0 - y0, r1 + 1 - y0)
        pr = [(a, b) for a in rr[np.argsort(np.abs(rr - r), kind='stable')][:3] for b in np.where(paint[a])[0]]
        pp[r, c] = pr[rng.integers(len(pr))]
    for n, (bx, by), mode in calques():
        full = load(n); box = full.copy()
        h, w = full.shape[:2]
        V = np.zeros((H, W, 4)); have = np.zeros((H, W), bool)                 # (le calque dans la zone)
        ys, xs = slice(max(y0, by), min(y1, by + h)), slice(max(x0, bx), min(x1, bx + w))
        have[ys.start - y0:ys.stop - y0, xs.start - x0:xs.stop - x0] = True
        b0 = load(n, BEFORE)                                             # (sa zone au commit BEFORE)
        V[ys.start - y0:ys.stop - y0, xs.start - x0:xs.stop - x0] = b0[ys.start - by:ys.stop - by, xs.start - bx:xs.stop - bx]
        As = lisse(V, clean & have, 1.0, 10)                              # l'asphalte, lisse
        Ps = lisse(V - As, paint & have, 3.0, 12)                         # le surcroît de la peinture, lisse
        out = V.copy()
        for r, c in zip(*np.where(touch & have)):
            k = new[r, c]
            base = As[r, c] + (V[tuple(pa[r, c])] - As[tuple(pa[r, c])]) if old[r, c] else V[r, c]
            pnt = As[r, c] + Ps[r, c] + (V[tuple(pp[r, c])] - As[tuple(pp[r, c])] - Ps[tuple(pp[r, c])])
            out[r, c] = (1 - k) * base + k * pnt
        box[ys.start - by:ys.stop - by, xs.start - bx:xs.stop - bx] = out[ys.start - y0:ys.stop - y0, xs.start - x0:xs.stop - x0]
        save(box, n, mode)
        print(n, 'pixels', int((touch & have).sum()))
    print('loin', ['%.2f' % v for v in loin], 'près', ['%.2f' % v for v in pres])


if __name__ == '__main__':
    main()
