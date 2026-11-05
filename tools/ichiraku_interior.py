#!/usr/bin/env python3
"""Ichiraku : derrière les portes vitrées, la boutique vue par l'œil de la rue (son fond de face), plus une affiche posée sur la façade.

    python3 tools/ichiraku_interior.py      (il reprend sa zone au commit BEFORE à chaque fois, on peut donc le relancer ;
                                             le module tools/interieur.py fait le redressement)

La façade du ramen est à droite de la rue ; ses deux portes coulissantes vitrées (quatre vitres en largeur, une traverse
entre le haut et le bas) courent vers le point de fuite VP comme elle. Derrière, le peintre avait peint la boutique de face
(ses étagères et ses objets sur le comptoir sous le noren, la lumière du comptoir en bandes dans les vitres du bas) puis
l'avait posée sur la façade : tout y suit ses rayons. Or par une porte de côté on voit le mur du bout de la boutique (de
travers à la rue) : de face, ses horizontales horizontales.

Ici, ce qu'on voit par le verre (VERRE : les vitres sous le noren peint et celles du bas, sans les montants, les meneaux, la
traverse) est redressé par tools/interieur.py : chaque rayon de la peinture devient l'horizontale qu'il a à la vitre la
plus proche de VP (XREF : là, la peinture telle quelle ; plus près, ses rangées resserrées de |x - VP_x| / |XREF - VP_x|
autour de l'horizon, 14 % au plus à la vitre la plus proche de nous), ses bords nets sur leurs rangées, sans marche. Ce qui
tombe au-delà de ce qu'il a peint, plus près de nous : sous le noren, le haut de la pièce à l'ombre du noren (HAUT, le grain
des rangées qu'il a peintes juste dessous, en miroir) ; au pied des vitres du bas, le bas du comptoir dans l'ombre (BAS).
Le noren peint, les montants, la traverse ne bougent pas (sur la façade).

Le même redressement pour tout ce qui suit ces pixels : layer_city_off (la boutique allumée), street_unlit (la coupure de
courant), assets/shop_off.webp (la boutique fermée : son verre sombre, posé à 1112, 448) et assets/ramen_glass.webp (le
masque du verre où passent les ombres de Teuchi et du client, à 1150, 520 : redressé avec lui, il les garde sur le verre
éclairé). Les figures (Teuchi, le client, Naruto au comptoir) et leurs temps ne changent pas : leurs places sont celles du
comptoir, qui reste à sa hauteur à la vitre du fond. night_far et street_sun : 0 ici, tels quels. Il faut git, Pillow,
numpy.
"""
import os
import sys
import numpy as np

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import interieur as I

BEFORE = '402ebae'                   # (les calques avant cet outil : sa zone reprise de là à chaque fois)
ZONE = (1150, 590, 1232, 700)        # x0, y0, x1, y1 : les vitres et leur cadre
VITRES = ((1159, 1170), (1172, 1186), (1191, 1206), (1208, 1224))   # les vitres : leurs colonnes (les montants entre)
BANDES = ((598, 631), (636, None))   # les rangées vues par le verre : sous le noren peint jusqu'à la traverse ; sous la
BAS_RAYON = 0.1467                   # traverse jusqu'au bas des vitres : la lisière claire de la traverse du bas, un rayon vers
                                     # VP (y = VP_y + c |x - VP_x|), reste sur la porte ; le verre s'arrête la rangée au-dessus
XREF = 1159                          # la vitre la plus proche de VP : la peinture y reste telle quelle
HAUT = (0.78, 0.9)                   # sous le noren, le haut de la pièce à son ombre : la part gardée (la rangée contre le
                                     # noren, les suivantes)
BAS = (0.72, 0.85)                   # au pied des vitres du bas, le bas du comptoir dans l'ombre (la rangée du bas, les autres)
SHOP_OFF, GLASS = (1112, 448), (1150, 520)   # (shop_off.webp, ramen_glass.webp : leur place)


def main():
    names = (('layer_city_off.webp', 'RGBA'), ('street_unlit.webp', 'RGBA'))
    L = [I.load(n, m) for n, m in names]; B = [I.load(n, m, BEFORE) for n, m in names]
    zx0, zy0, zx1, zy1 = ZONE
    for l, b in zip(L, B): l[zy0:zy1, zx0:zx1] = b[zy0:zy1, zx0:zx1]       # (la zone comme avant)
    H, W = B[0].shape[:2]
    so = I.load('shop_off.webp', 'RGBA', BEFORE); gl = I.load('ramen_glass.webp', 'RGBA', BEFORE)
    def place(a, at):                                                        # (une image posée dans la scène)
        o = np.zeros((H, W, a.shape[2])); o[at[1]:at[1] + a.shape[0], at[0]:at[0] + a.shape[1]] = a; return o
    imgs = {'on': B[0].copy(), 'cut': B[1].copy(), 'off': place(so, SHOP_OFF), 'glass': place(gl, GLASS)}

    inside = np.zeros((H, W), bool); cols = []
    for x0, x1 in VITRES:
        for x in range(x0, x1 + 1):
            cols.append(x)
            bot = int(np.round(I.ray(BAS_RAYON, x) - 0.5)) - 1
            for (y0, y1) in BANDES: inside[y0:(y1 if y1 else bot) + 1, x] = True

    rows = {x: [y for y in range(H) if inside[y, x]] for x in cols}
    def fill(k, x, y, side, d):                                              # (au-delà de la peinture : en miroir, à l'ombre)
        r = rows[x]
        if side == 'haut': s = r[min(len(r) - 1, d - 1)]; f = HAUT[0] if d == 1 else HAUT[1]
        else: s = r[max(0, len(r) - d)]; f = BAS[0] if d == 1 else BAS[1]
        v = imgs[k][s, x].copy()
        if k == 'on': v[:3] = v[:3] * f                                        # (le verre sombre : pas de pièce)
        return v
    Lm = imgs['on'][..., :3] @ I.LUM
    out, plan, tr = I.redress(imgs, inside, XREF, cols, Lm, 1.0, fill)

    zs = (slice(zy0, zy1), slice(zx0, zx1))
    L[0][zs] = out['on'][zs]; L[1][zs] = out['cut'][zs]
    for (n, m), l in zip(names, L): I.save(l, n, m)
    so2 = out['off'][SHOP_OFF[1]:SHOP_OFF[1] + so.shape[0], SHOP_OFF[0]:SHOP_OFF[0] + so.shape[1]]
    gl2 = out['glass'][GLASS[1]:GLASS[1] + gl.shape[0], GLASS[0]:GLASS[0] + gl.shape[1]]
    I.save(so2, 'shop_off.webp', 'RGBA'); I.save(gl2, 'ramen_glass.webp', 'RGBA')
    k = max(abs(x - I.VP[0]) / abs(XREF - I.VP[0]) for x in cols)
    n_h = sum(1 for m in plan.values() for s in m.values() if s == 'haut'); n_b = sum(1 for m in plan.values() for s in m.values() if s == 'bas')
    print('vitres', len(cols), 'colonnes |', len(tr), 'bords suivis | resserrement au plus %.1f %%' % (100 * (k - 1)),
          '| haut', n_h, 'px, bas', n_b, 'px')


if __name__ == '__main__':
    main()
