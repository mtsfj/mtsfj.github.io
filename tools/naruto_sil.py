#!/usr/bin/env python3
"""Naruto à la fenêtre du balcon : ses silhouettes ramenées aux proportions de la rue et au pixel près.

    python3 tools/naruto_sil.py      (lit tools/src/naruto_sil.webp, la planche telle que l'a faite build_zzzchar_naruto.py ;
                                      écrit assets/naruto_sil.webp ; on peut le relancer)

La planche source (hors du dépôt, son outil aussi) le dessine 1,39 m (1,54 m aux pointes des cheveux) à 75 px le mètre, une
rangée par mouvement, les cases et leur point au sol dans la table NC de assets/street.js (lue ici, inchangée). Deux choses
y sont reprises :

- sa tête : elle faisait 4,9 têtes de haut (24 px de la planche, 22 px à l'écran devant la vitre), une tête d'enfant de
  dessin animé trop grosse pour la rue (0,32 m). Tout ce qui est au-dessus du cou est ramené à TETE (0,8 : 17,5 px devant la
  vitre, 14 px à l'entrée), reposé sur la ligne du cou : le cou de chaque image (la rangée la plus étroite sous la tête, ou,
  quand ses bras l'entourent, la hauteur du cou des images debout au-dessus du sol), son milieu pour pivot ; l'échelle passe
  de TETE à 1 sur les quelques rangées du cou (RAMPE), pour que rien ne s'y casse (ses bras levés autour de sa tête) ; la
  même règle pour toutes les images d'une rangée, donc sa tête ne saute pas d'une image à l'autre ;
- ses bords : la planche source les anticrénelait (un pixel sur trois de son bord à demi transparent) ; chaque pixel est
  ici plein ou vide, plein quand la silhouette en couvre la plus grande part (4 x 4 points par pixel).

street.js le dessine pixel entier par pixel entier (ses cases rééchantillonnées à l'échelle de chaque endroit de la même
façon, par majorité, et posées sur des pixels entiers de la scène).
Il faut Pillow, numpy, scipy.
"""
import json
import os
import re
import numpy as np
from PIL import Image

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
SRC = os.path.join(ICI, 'src', 'naruto_sil.webp')
OUT = os.path.join(RACINE, 'assets', 'naruto_sil.webp')
TETE = 0.8                       # sa tête (tout ce qui est au-dessus du cou) à cette échelle
RAMPE = (3, 2)                   # l'échelle passe de TETE à 1 de 3 rangées au-dessus du cou à 2 rangées en dessous
COU = (24, 34)                   # (le cou : la rangée la plus étroite entre ces rangées sous le haut des cheveux)
COU_ETROIT = 16                  # (plus large que ça, ses bras l'entourent : la hauteur du cou des images debout)
SS = 4                           # (points par pixel, sur chaque axe)


def table_nc():
    js = open(os.path.join(RACINE, 'assets', 'street.js'), encoding='utf-8').read()
    m = re.search(r'const NC = (\{[^;]*\});', js).group(1)
    return json.loads(re.sub(r'(\w+):', r'"\1":', m))


def cou(c, top):
    """La rangée du cou (la plus étroite, au milieu des ex aequo) et le milieu du cou, ou None si ses bras l'entourent."""
    w = c.sum(1)
    ys = np.arange(top + COU[0], top + COU[1] + 1)
    mn = w[ys].min()
    if mn > COU_ETROIT:
        return None
    lo = ys[w[ys] <= mn]
    y = int(round(np.median(lo)))
    xs = np.where(c[y])[0]
    runs = np.split(xs, np.where(np.diff(xs) > 1)[0] + 1)
    hx = np.where(c[top:top + 12].any(0))[0].mean()                  # (le milieu de sa tête, pour choisir le bon morceau)
    r = min(runs, key=lambda r: abs((r[0] + r[-1]) / 2 - hx))
    return y, (r[0] + r[-1] + 1) / 2


def echelle(y, yc):
    """L'échelle à la rangée y de la source (cou en yc) : TETE au-dessus de la rampe, 1 en dessous, linéaire entre."""
    a, b = yc - RAMPE[0], yc + RAMPE[1]
    return np.where(y <= a, TETE, np.where(y >= b, 1.0, TETE + (1 - TETE) * (y - a) / (b - a)))


def reprend(c, yc, xc):
    """La case c (booléens) : sa tête à TETE autour de (xc, yc), par majorité de SS x SS points par pixel."""
    h, w = c.shape
    b = yc + RAMPE[1]
    # la rangée de sortie de chaque rangée de la source (y continu) : identité sous la rampe, l'intégrale de l'échelle au-dessus
    fy = np.linspace(-40, h, (h + 40) * 64 + 1)
    s = echelle(fy, yc)
    d = np.concatenate([[0], np.cumsum((s[1:] + s[:-1]) / 2 * np.diff(fy))])
    d -= np.interp(b, fy, d)
    gy = b + d                                                     # (y de sortie pour chaque fy, croissant)
    oy = (np.arange(h * SS) + 0.5) / SS
    ox = (np.arange(w * SS) + 0.5) / SS
    sy = np.interp(oy, gy, fy)                                     # la rangée de la source sous chaque point
    sc = echelle(sy, yc)
    SX = xc + (ox[None, :] - xc) / sc[:, None]
    SY = np.repeat(sy[:, None], len(ox), 1)
    iy, ix = np.floor(SY).astype(int), np.floor(SX).astype(int)
    ok = (iy >= 0) & (iy < h) & (ix >= 0) & (ix < w)
    v = np.zeros(SX.shape, np.float32)
    v[ok] = c[iy[ok], ix[ok]]
    return v.reshape(h, SS, w, SS).mean((1, 3)) >= 0.5


def main():
    NC = table_nc()
    src = np.asarray(Image.open(SRC).convert('RGBA'))
    A = src[..., 3] >= 128                                         # (la silhouette : plus de la moitié couverte)
    out = np.zeros(A.shape, bool)
    # la hauteur du cou au-dessus du point au sol, dans les images debout où il se voit (pour celles où ses bras l'entourent)
    debout = []
    for k in ('turn', 'seal', 'settleT', 'settleA', 'startT', 'startA'):
        t, w, h, n, ax, ay = NC[k]
        for i in range(n):
            c = A[t:t + h, i * w:(i + 1) * w]
            r = cou(c, int(np.where(c.any(1))[0][0]))
            if r:
                debout.append(ay - r[0])
    h_cou = int(round(np.median(debout)))
    rapport = []
    for k, (t, w, h, n, ax, ay) in NC.items():
        ycs = []
        for i in range(n):
            c = A[t:t + h, i * w:(i + 1) * w]
            top = int(np.where(c.any(1))[0][0])
            r = cou(c, top)
            if r is None:                                          # (ses bras autour de sa tête : le cou des images debout)
                yc = ay - h_cou
                xc = np.where(c[top:top + 12].any(0))[0].mean() + 0.5
                r = (yc, xc)
            yc, xc = r
            ycs.append(ay - yc)
            out[t:t + h, i * w:(i + 1) * w] = reprend(c, yc, xc)
        rapport.append('%s : le cou à %s px au-dessus du sol' % (k, ','.join(str(v) for v in ycs)))
    rgba = np.zeros(A.shape + (4,), np.uint8)
    rgba[..., 3] = np.where(out, 255, 0)
    Image.fromarray(rgba, 'RGBA').save(OUT, lossless=True, quality=100, method=6)
    print('\n'.join(rapport))
    print('cou des images debout : %d px au-dessus du sol ; %s : %d x %d, %d pixels pleins (avant %d, dont %d à demi)' % (
        h_cou, OUT, A.shape[1], A.shape[0], out.sum(), (src[..., 3] > 0).sum(), ((src[..., 3] > 0) & (src[..., 3] < 255)).sum()))


if __name__ == '__main__':
    main()
