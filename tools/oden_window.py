#!/usr/bin/env python3
"""La fenêtre de l'oden : derrière ses deux vitres, la boutique de face (son fond), le plafond en coin au-dessus.

    python3 tools/oden_window.py      (il reprend sa zone au commit BEFORE à chaque fois, on peut donc le relancer ; le module
                                       tools/interieur.py fait le redressement)

La façade de l'oden est à gauche de la rue et court vers le point de fuite VP. Sa fenêtre (deux vitres, le montant de
rencontre entre elles) montre la boutique éclairée : le peintre l'avait peinte de face puis posée sur la façade, ses
rangées le long des rayons de celle-ci. Par une fenêtre de côté on voit le mur du bout de la boutique, de face.

Ici, ce qu'on voit par le verre (le masque du verre de la fenêtre, assets/oden_window.webp, celui de sa vapeur) est
redressé par tools/interieur.py : chaque rayon de la peinture devient l'horizontale qu'il a à la colonne de verre la plus
proche de VP (XREF : la peinture y reste telle quelle ; plus près de nous, ses rangées resserrées autour de l'horizon,
13 % au plus), ses bords nets sur leurs rangées. Au-dessus de ce qu'il a peint, plus près de nous, le plafond en coin
(un rayon en haut, le linteau ; une horizontale en bas) : le grain de ses rangées du haut, en miroir, à l'ombre
(PLAFOND). Le comptoir et la marmite (près de l'horizon) ne bougent pas d'un pixel : la vapeur part toujours de la
marmite, le masque du verre reste le sien. Dans layer_city_off (allumée) et street_unlit (la coupure de courant, et la
boutique fermée par ses heures) ; night_far et street_sun : 0 ici, tels quels. Il faut git, Pillow, numpy.
"""
import os
import sys
import numpy as np

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import interieur as I

BEFORE = '402ebae'                   # (les calques avant cet outil : sa zone reprise de là à chaque fois)
ZONE = (462, 556, 502, 624)          # x0, y0, x1, y1 : la fenêtre (la boîte de son verre dans assets/street.js)
MASK, AT = 'oden_window.webp', (462, 556)   # le masque de son verre, sa place
XREF = 495                           # la colonne de verre la plus proche de VP : la peinture y reste telle quelle
PLAFOND = (0.55, 0.7)                # le plafond, à l'ombre : la part gardée (la rangée contre le mur, les suivantes)
COMPTOIR = 608                       # (à partir de cette rangée, près de l'horizon, la peinture reste où elle est : le comptoir,
                                     # la marmite d'où part la vapeur)


def main():
    names = (('layer_city_off.webp', 'RGBA'), ('street_unlit.webp', 'RGBA'))
    L = [I.load(n, m) for n, m in names]; B = [I.load(n, m, BEFORE) for n, m in names]
    zx0, zy0, zx1, zy1 = ZONE
    for l, b in zip(L, B): l[zy0:zy1, zx0:zx1] = b[zy0:zy1, zx0:zx1]       # (la zone comme avant)
    H, W = B[0].shape[:2]
    mk = I.load(MASK, 'RGBA', BEFORE)
    inside = np.zeros((H, W), bool)
    inside[AT[1]:AT[1] + mk.shape[0], AT[0]:AT[0] + mk.shape[1]] = mk[..., 3] > 128
    cols = sorted(set(np.where(inside)[1]))
    imgs = {'on': B[0].copy(), 'cut': B[1].copy()}
    rows = {x: [y for y in range(H) if inside[y, x]] for x in cols}
    def fill(k, x, y, side, d):                                              # (le plafond : en miroir, à l'ombre ; le bas ne
        r = rows[x]                                                          # sert pas ici)
        s = r[min(len(r) - 1, d - 1)] if side == 'haut' else r[max(0, len(r) - d)]
        v = imgs[k][s, x].copy()
        if k == 'on': v[:3] = v[:3] * (PLAFOND[0] if d == 1 else PLAFOND[1])   # (éteinte, le verre sombre : pas de pièce)
        return v
    out, plan, tr = I.redress(imgs, inside, XREF, cols, imgs['on'][..., :3] @ I.LUM, 1.0, fill)
    for x in cols:                                                           # (le comptoir et la marmite, à l'horizon : à moins
        for y in range(COMPTOIR, H):                                         # d'un pixel de leur place, ils y restent)
            if inside[y, x]:
                for k in imgs: out[k][y, x] = imgs[k][y, x]
                plan[x][y] = y
    zs = (slice(zy0, zy1), slice(zx0, zx1))
    L[0][zs] = out['on'][zs]; L[1][zs] = out['cut'][zs]
    for (n, m), l in zip(names, L): I.save(l, n, m)
    moved = sum(1 for x, m in plan.items() for y, s in m.items() if s != y)
    pot = [(y, x) for x in range(485, 496) for y in range(610, 618) if plan.get(x, {}).get(y, y) != y]
    print('vitres', len(cols), 'colonnes |', len(tr), 'bords suivis | plafond', sum(1 for m in plan.values() for s in m.values() if s == 'haut'),
          'px |', moved, 'px déplacés | la marmite :', 'immobile' if not pot else '%d px bougent' % len(pot))


if __name__ == '__main__':
    main()
