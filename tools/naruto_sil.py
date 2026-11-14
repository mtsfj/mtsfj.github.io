#!/usr/bin/env python3
"""Naruto à la fenêtre du balcon : ses silhouettes ramenées aux proportions de la rue et au pixel près.

    python3 tools/naruto_sil.py      (lit tools/src/naruto_sil.webp, la planche telle que l'a faite build_zzzchar_naruto.py ;
                                      écrit assets/naruto_sil.webp ; on peut le relancer ; puis tools/naruto_col.py, qui la
                                      peint en couleur : assets/naruto_col.webp, ce que street.js dessine)

La planche source (hors du dépôt, son outil aussi) le dessine 1,39 m (1,54 m aux pointes des cheveux) à 75 px le mètre, une
rangée par mouvement, les cases et leur point au sol dans la table NC_SRC ci-dessous. Trois choses y sont reprises :

- sa taille : un enfant de 1,39 m derrière une baie dont le verre monte à 2,4 m au-dessus de son plancher et une rambarde
  de 1,1 m ; le jeune homme qu'il est fait 1,65 à 1,70 m. Son corps (tout ce qui est sous le cou) est agrandi de GRAND
  (1,3) autour du point au sol, sa tête gardée à sa taille (ci-dessous) : 1,67 m au crâne, 1,78 m aux pointes des
  cheveux, sept têtes et quart de haut, et non plus cinq trois quarts (les épaules et les bras d'un adolescent, plus d'un
  enfant de dessin animé) ; les cases agrandies d'autant (la table NC de assets/street.js, que l'outil calcule et
  vérifie), leur haut au même écart au-dessus de ses cheveux ; street.js fait ses pas, ses courses et ses arrêts GRAND
  fois plus longs (NG : walkD, runD, walkV, runV, xa0, xr0), pour que ses pieds ne glissent pas ;

- sa tête : elle faisait 4,9 têtes de haut (24 px de la planche, 22 px à l'écran devant la vitre), une tête d'enfant de
  dessin animé trop grosse pour la rue (0,32 m). Tout ce qui est au-dessus du cou est ramené à TETE (0,8 : 17,5 px devant la
  vitre, 14 px à l'entrée), reposé sur la ligne du cou (montée de GRAND avec le corps) : le cou de chaque image (la rangée
  la plus étroite sous la tête, ou, quand ses bras l'entourent, la hauteur du cou des images debout au-dessus du sol), son
  milieu pour pivot ; l'échelle passe de TETE à GRAND sur les quelques rangées du cou (RAMPE), pour que rien ne s'y casse
  (ses bras levés autour de sa tête) ; la même règle pour toutes les images d'une rangée, donc sa tête ne saute pas d'une
  image à l'autre ;
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
GRAND = 1.3                      # son corps (tout ce qui est sous le cou) à cette échelle
TETE = 0.8                       # sa tête (tout ce qui est au-dessus du cou) à cette échelle
RAMPE = (3, 2)                   # l'échelle passe de TETE à GRAND de 3 rangées au-dessus du cou à 2 rangées en dessous
NC_SRC = {'walkT': [0, 50, 125, 16, 24, 119], 'walkA': [125, 50, 125, 16, 26, 118], 'runT': [250, 58, 125, 12, 29, 118],
          'runA': [375, 58, 118, 12, 29, 111], 'settleT': [493, 50, 126, 6, 21, 122], 'settleA': [743, 50, 125, 6, 29, 116],
          'startT': [619, 50, 124, 4, 21, 120], 'startA': [868, 50, 125, 4, 29, 118], 'turn': [993, 46, 124, 9, 23, 119],
          'look': [1117, 55, 123, 4, 27, 118], 'seal': [1240, 46, 123, 3, 27, 118]}   # (les rangées de la planche source :
                                                 # haut, largeur et hauteur des cases, images, point au sol dans la case)
COU = (24, 34)                   # (le cou : la rangée la plus étroite entre ces rangées sous le haut des cheveux)
COU_ETROIT = 16                  # (plus large que ça, ses bras l'entourent : la hauteur du cou des images debout)
SS = 4                           # (points par pixel, sur chaque axe)


def table_nc():
    js = open(os.path.join(RACINE, 'assets', 'street.js'), encoding='utf-8').read()
    m = re.search(r'const NC = (\{[^;]*\});', js).group(1)
    return json.loads(re.sub(r'(\w+):', r'"\1":', m))


def table_grande(h_cou):
    """Les cases agrandies : GRAND fois plus larges, le point au sol à GRAND fois son x, le haut au même écart au-dessus de
    ses cheveux (sa tête, gardée, ne monte que de ce dont monte son cou), le bas GRAND fois plus bas ; rangées dans l'ordre."""
    out, t = {}, 0
    for k, (t0, w, h, n, ax, ay) in sorted(NC_SRC.items(), key=lambda kv: kv[1][0]):
        ay2 = ay + int(round(h_cou * (GRAND - 1)))
        h2 = ay2 + int(np.ceil((h - ay) * GRAND))
        out[k] = [t, int(round(w * GRAND)), h2, n, int(round(ax * GRAND)), ay2]
        t += h2
    return {k: out[k] for k in NC_SRC}


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
    """L'échelle à la rangée y de la source (cou en yc) : TETE au-dessus de la rampe, GRAND en dessous, linéaire entre."""
    a, b = yc - RAMPE[0], yc + RAMPE[1]
    return np.where(y <= a, TETE, np.where(y >= b, GRAND, TETE + (GRAND - TETE) * (y - a) / (b - a)))


def reprend(c, yc, xc, src, dst):
    """La case c (booléens, la case source src) dans une case dst : son corps à GRAND autour du point au sol, sa tête à
    TETE autour de (xc, yc), par majorité de SS x SS points par pixel."""
    h, w = c.shape
    ax, ay = src[4], src[5]
    w2, h2, ax2, ay2 = dst[1], dst[2], dst[4], dst[5]
    b = yc + RAMPE[1]
    # la rangée de sortie de chaque rangée de la source (y continu) : GRAND fois sa hauteur au-dessus du sol sous la rampe,
    # l'intégrale de l'échelle au-dessus
    fy = np.linspace(-40, h, (h + 40) * 64 + 1)
    s = echelle(fy, yc)
    d = np.concatenate([[0], np.cumsum((s[1:] + s[:-1]) / 2 * np.diff(fy))])
    d -= np.interp(b, fy, d)
    gy = ay2 + GRAND * (b - ay) + d                                # (y de sortie pour chaque fy, croissant)
    oy = (np.arange(h2 * SS) + 0.5) / SS
    ox = (np.arange(w2 * SS) + 0.5) / SS
    sy = np.interp(oy, gy, fy)                                     # la rangée de la source sous chaque point
    sc = echelle(sy, yc)
    P = ax2 + GRAND * (xc - ax)                                    # (le pivot de la tête, où le corps l'a mené)
    SX = xc + (ox[None, :] - P) / sc[:, None]
    SY = np.repeat(sy[:, None], len(ox), 1)
    iy, ix = np.floor(SY).astype(int), np.floor(SX).astype(int)
    ok = (iy >= 0) & (iy < h) & (ix >= 0) & (ix < w)
    v = np.zeros(SX.shape, np.float32)
    v[ok] = c[iy[ok], ix[ok]]
    return v.reshape(h2, SS, w2, SS).mean((1, 3)) >= 0.5


def main():
    NC = NC_SRC
    src = np.asarray(Image.open(SRC).convert('RGBA'))
    A = src[..., 3] >= 128                                         # (la silhouette : plus de la moitié couverte)
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
    NG = table_grande(h_cou)
    out = np.zeros((sum(v[2] for v in NG.values()), max(v[1] * v[3] for v in NG.values())), bool)
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
            t2, w2, h2 = NG[k][:3]
            out[t2:t2 + h2, i * w2:(i + 1) * w2] = reprend(c, yc, xc, NC[k], NG[k])
        rapport.append('%s : le cou à %s px au-dessus du sol' % (k, ','.join(str(v) for v in ycs)))
    rgba = np.zeros(out.shape + (4,), np.uint8)
    rgba[..., 3] = np.where(out, 255, 0)
    Image.fromarray(rgba, 'RGBA').save(OUT, lossless=True, quality=100, method=6)
    print('\n'.join(rapport))
    print('cou des images debout : %d px au-dessus du sol ; %s : %d x %d, %d pixels pleins (avant %d, dont %d à demi)' % (
        h_cou, OUT, out.shape[1], out.shape[0], out.sum(), (src[..., 3] > 0).sum(), ((src[..., 3] > 0) & (src[..., 3] < 255)).sum()))
    ligne = 'const NC = {' + ', '.join('%s: [%s]' % (k, ', '.join(str(x) for x in v)) for k, v in NG.items()) + '};'
    if table_nc() != NG:
        raise SystemExit('assets/street.js : la table NC doit être celle des cases agrandies :\n  ' + ligne)
    print('NC de assets/street.js : celle des cases agrandies')


if __name__ == '__main__':
    main()
