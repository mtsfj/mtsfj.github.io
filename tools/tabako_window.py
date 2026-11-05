#!/usr/bin/env python3
"""La fenêtre du tabac (le mur de face entre le dagashi-ya et les distributeurs) : derrière sa vitre, une petite cabine.

    python3 tools/tabako_window.py      (il reprend sa zone au commit BEFORE à chaque fois, on peut donc le relancer)

Le kiosque avance sur le trottoir devant la façade de Kirua : son mur sous l'enseigne « たばこ » est de face (ses planches,
son enseigne, le haut et le bas de sa fenêtre sont horizontaux, mesurés), à gauche du point de fuite VP. Le peintre y avait
peint la cabine comme une affiche éclairée : ses paquets, son présentoir, la coupelle de la monnaie, collés au cadre, d'une
même lumière d'un bord à l'autre ; seule une colonne claire et une sombre à gauche pour dire son côté.

Ici, une cabine vue par l'œil de la rue (une perspective à un point, VP à droite : ce qui entre dans la cabine court vers
VP, ce qui lui fait face est de face) :

- le tableau gauche du cadre, sa face intérieure (JAMB colonnes : elle fuit vers VP, on la voit puisque VP est à droite ;
  la droite est cachée) : le bois sombre du cadre, un peu éclairé par la cabine allumée ;
- la paroi gauche de la cabine, de la vitre au fond (SIDE colonnes) : celle du peintre (sa colonne claire et la suivante,
  les planches du présentoir dessus, leurs rayons presque horizontaux à cette taille) élargie à sa profondeur, plus
  sombre vers l'angle (SIDE_F) ; l'angle, sa colonne sombre ;
- le fond, de face : les pixels du peintre tels quels, poussés de SHIFT colonnes vers VP (le fond est plus loin que la
  vitre : il glisse vers le point de fuite, sa droite passe derrière le tableau droit du cadre, la coupelle avec) ; plus
  sombre contre l'angle (AO) ;
- allumée, la lumière d'un tube caché derrière le linteau : le haut le plus clair, le bas un peu moins (FALL) ; et derrière
  un verre, un peu plus sombre que le cadre éclairé (GLASS_DIM) ;
- la vitre : un reflet en biais, à peine, deux bandes nettes (SHEEN), allumée comme éteinte.

Éteinte, comme elle est dans les calques : la même cabine prise dans les pixels sombres du peintre. Dans layer_city_off
et street_unlit (les mêmes ici : leur rapport au commit BEFORE gardé), night_far (0) et street_sun (0) ; écrit
assets/win_z7_kiosk.webp (le comp de la fenêtre, ce qui change quand elle s'allume) et sa boîte dans assets/street.js.
Il faut git, Pillow, numpy.
"""
import io
import os
import re
import subprocess
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = lambda p: os.path.join(ROOT, 'assets', p)
BEFORE = 'd3b63a6'                   # (les calques et le comp avant cet outil : sa zone reprise de là à chaque fois)
ZONE = (228, 572, 272, 652)          # x0, y0, x1, y1 : la fenêtre, son cadre compris
VP = (700.0, 615.0)                  # le point de fuite (le mur du kiosque est de face : ses horizontales le sont, mesurées)
GX, GY = (231, 262), (579, 647)      # la vitre du peintre : ses colonnes, ses rangées (premières et dernières)
JAMB, SIDE = 2, 5                    # le tableau gauche du cadre, la paroi gauche de la cabine : leurs colonnes
SHIFT = 5                            # le fond poussé vers VP de tant de colonnes
SRC0 = 234                           # (la première colonne du fond du peintre, après sa colonne claire et sa sombre)
HIS_SIDE = (231, 232)                # (la paroi du peintre : sa colonne claire et la suivante ; son angle, la sombre après)
SIDE_F = (1.0, 0.7)                  # la paroi : sa lumière, côté vitre, côté angle (de celle du peintre)
AO = (0.8, 0.92)                     # le fond contre l'angle (ses deux premières colonnes)
FRAME = (229, 230)                   # (le cadre du peintre à gauche de la vitre : sa face, son bord)
JAMB_LIT = (0.18, 0.3)               # allumée : la part de la lumière de la cabine sur le tableau (côté cadre, côté vitre)
FALL = 0.22                          # allumée : le bas de la cabine plus sombre que le haut (sa part perdue)
GLASS_DIM = 0.93                     # allumée : derrière le verre
SHEEN = ((0.5, 4.0, 3.0), (0.56, 1.5, 6.0))   # le reflet en biais : (sa pente (x par rangée), sa largeur, son ajout)
SHEEN_AT = (247, 600)                # (le point où passent leurs milieux)
UP = 'win_z7_kiosk'; UP_POS = (227, 575); UP_V = 7   # le comp de la fenêtre (sa place au commit BEFORE), sa version
LUM = np.array([0.299, 0.587, 0.114])


def load(p, mode='RGBA', at=None):
    data = subprocess.run(['git', 'show', f'{at}:assets/{p}'], cwd=ROOT, capture_output=True, check=True).stdout if at else open(A(p), 'rb').read()
    return np.asarray(Image.open(io.BytesIO(data)).convert(mode)).astype(float)


def save(arr, p, mode):
    Image.fromarray(np.clip(np.round(arr), 0, 255).astype(np.uint8), mode).save(A(p), 'WEBP', lossless=True, quality=100, method=6, exact=True)


def main():
    names = (('layer_city_off.webp', 'RGBA'), ('street_unlit.webp', 'RGBA'), ('night_far.webp', 'RGB'), ('street_sun.webp', 'RGB'))
    L = [load(n, m) for n, m in names]; B = [load(n, m, BEFORE) for n, m in names]
    zx0, zy0, zx1, zy1 = ZONE
    for l, b in zip(L, B): l[zy0:zy1, zx0:zx1] = b[zy0:zy1, zx0:zx1]       # (la fenêtre comme avant)
    H, W = B[0].shape[:2]
    off = B[0][..., :3].copy()
    cp = load(UP + '.webp', 'RGBA', BEFORE); px, py = UP_POS; ch, cw = cp.shape[:2]
    on = off.copy(); al = cp[..., 3:4] / 255
    on[py:py + ch, px:px + cw] = on[py:py + ch, px:px + cw] * (1 - al) + cp[..., :3] * al
    cut = np.clip((B[1][..., :3] + 0.5) / (B[0][..., :3] + 0.5), 0, 1)     # (ce que la coupure de courant ôte ici : rien)
    S = {'on': on, 'off': off}; N = {k: v.copy() for k, v in S.items()}

    x0, x1 = GX; y0, y1 = GY
    xj, xs, xc = x0 + JAMB, x0 + JAMB + SIDE, x0 + JAMB + SIDE              # (la paroi commence après le tableau ; l'angle)
    for k in S:
        for y in range(y0, y1 + 1):
            fall = 1 - FALL * (y - y0) / (y1 - y0) if k == 'on' else 1.0
            back = lambda x: S[k][y, x - SHIFT] if x - SHIFT >= SRC0 else S[k][y, SRC0]
            for x in range(x0, x1 + 1):
                if x < xj:                                                   # le tableau du cadre : son bois, un peu éclairé
                    wood = S['off'][y, FRAME[0]]
                    t = JAMB_LIT[x - x0] if k == 'on' else 0.0
                    col = wood + (S[k][y, SRC0] * 0.6 - wood) * t
                elif x < xs:                                                 # la paroi : celle du peintre (ses deux colonnes),
                    i = (x - xj) * len(HIS_SIDE) // SIDE                     # étirée sur la sienne, plus sombre vers l'angle
                    f = SIDE_F[0] + (SIDE_F[1] - SIDE_F[0]) * (x - xj) / max(1, SIDE - 1)
                    col = S[k][y, HIS_SIDE[i]] * f / SIDE_F[0] * fall * (GLASS_DIM if k == 'on' else 1.0)
                elif x == xc:                                                # l'angle : celui du peintre
                    col = S[k][y, HIS_SIDE[-1] + 1] * fall * (GLASS_DIM if k == 'on' else 1.0)
                else:                                                        # le fond, poussé vers VP ; contre l'angle plus sombre
                    ao = AO[x - xc - 1] if x - xc - 1 < len(AO) else 1.0
                    col = back(x) * ao * fall * (GLASS_DIM if k == 'on' else 1.0)
                N[k][y, x] = col
    # la vitre : un reflet en biais, à peine (de la paroi au tableau droit)
    for slope, wdt, add in SHEEN:
        for y in range(y0, y1 + 1):
            for x in range(xj, x1 + 1):
                if abs((x - SHEEN_AT[0]) + slope * (y - SHEEN_AT[1])) < wdt / 2:
                    for k in S: N[k][y, x] = N[k][y, x] + add

    zs = (slice(zy0, zy1), slice(zx0, zx1))
    L[0][zs][..., :3] = N['off'][zs]; L[0][zs][..., 3] = 255
    L[1][zs][..., :3] = N['off'][zs] * cut[zs]; L[1][zs][..., 3] = 255
    for (n, m), l in zip(names, L): save(l, n, m)
    diff = np.zeros((H, W), bool); diff[zs] = np.abs(np.round(N['on'][zs]) - np.round(N['off'][zs])).sum(2) > 0
    keep = np.zeros((H, W), bool); keep[py:py + ch, px:px + cw] = cp[..., 3] > 0
    keep[zs] = False                                                         # (hors de la fenêtre, le comp tel quel)
    spr = np.zeros((H, W, 4))
    spr[keep] = np.concatenate([on[keep], np.full((keep.sum(), 1), 255.0)], 1)
    spr[diff] = np.concatenate([N['on'][diff], np.full((diff.sum(), 1), 255.0)], 1)
    ys, xs_ = np.where(spr[..., 3] > 0)
    bx, by, bw, bh = int(xs_.min()), int(ys.min()), int(xs_.max() - xs_.min() + 1), int(ys.max() - ys.min() + 1)
    save(spr[by:by + bh, bx:bx + bw], UP + '.webp', 'RGBA')
    s_ = open(A('street.js'), encoding='utf-8').read()
    s_, n_s = re.subn(r'"%s": \{"src": "assets/%s\.webp\?v=\d+", "x": \d+, "y": \d+, "w": \d+, "h": \d+\}' % (UP, UP),
                      f'"{UP}": {{"src": "assets/{UP}.webp?v={UP_V}", "x": {bx}, "y": {by}, "w": {bw}, "h": {bh}}}', s_)
    assert n_s == 1, 'street.js : le comp de la fenêtre est introuvable'
    open(A('street.js'), 'w', encoding='utf-8').write(s_)
    print('vitre', x1 - x0 + 1, 'x', y1 - y0 + 1, '| tableau', x0, '..', xj - 1, '| paroi', xj, '..', xs - 1, '| angle', xc,
          '| comp', (bx, by, bw, bh), int(diff.sum()), 'px')


if __name__ == '__main__':
    main()
