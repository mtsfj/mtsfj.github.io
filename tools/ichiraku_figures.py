#!/usr/bin/env python3
"""Ichiraku : les gens de la boutique dans la maquette de tools/ichiraku_interior.py, chacun à sa profondeur et à sa vraie
taille, découpés dans les deux planches du propriétaire (tools/src/ichiraku_teuchi_sheet.webp : Teuchi ;
tools/src/ichiraku_regular_sheet.webp : l'habitué en costume), dans l'un de trois styles.

    python3 tools/ichiraku_figures.py                       (après tools/ichiraku_interior.py ; réécrit assets/ramen_figures.webp
                                                             et, dans assets/street.js, la ligne IRF : on peut le relancer, il
                                                             écrit la même chose)
    python3 tools/ichiraku_figures.py --style couleur       (le style : ombre (A), couleur (B), liseré (C, par défaut))
    python3 tools/ichiraku_figures.py --preview dossier     (des aperçus seulement : l'atlas, la ligne IRF en json)

Les styles (STYLE, ou --style) :
  - ombre (A) : des silhouettes sombres, comme avant, mais découpées dans les planches : le contour porte le détail (le noeud
    du bandeau, la perche, les manches retroussées ; la veste, le sac, sa bandoulière, le bol). Trois tons sombres proches
    (TONES : le plus sombre où la planche a ses traits et ses sombres, le ton de base, un peu moins sombre où elle est claire) :
    le bras se détache du buste ; posées comme avant (Teuchi à 0,86 avec tout le grain du peintre, les gens plus près à 0,95
    avec la moitié) ;
  - couleur (B) : les couleurs de la planche sous la lumière chaude de la boutique, chacun en FAMILIES familles de tons, d'un
    grain fin (GRAIN_B niveaux) dans chacune, au plus ISOLATED de pixels seuls ; les traits du visage selon la taille de la tête
    (FACE : sous 10 pixels aucun, jusqu'à 15 un pixel par oeil, au-delà la bouche, le nez) ; leur clarté gardée dans celle de
    la peinture autour (VALUES) ;
  - liseré (C) : l'ombre de A, et un liseré d'un pixel de la lumière de la boutique sur les bords tournés vers elle (LIGHT :
    d'en haut, et du côté de la lanterne pour Teuchi au comptoir et le client assis), pris dans les couleurs claires du
    personnage lui-même (ses familles de B), posé après le grain.
Dans les trois : un pixel plein ou vide, jamais à demi ; pas de trait sombre continu au bord (OUTLINE_DL : un pixel plus sombre
seulement du côté de l'ombre, SHADOW_COS, ou là où deux parts se touchent).

La vraie taille. Teuchi fait 1,78 m (son bandeau compris), le client 1,82 m ; la maquette de la rue met l'œil à 1,5 m quand
les repères du sol de la peinture le mettent à 1,26 m : les gens y sont donc pris à SCALE = 1,19 mètre de maquette pour un vrai
(la pièce, le comptoir, les tabourets tels quels). Les planches sont dessinées en grosse tête (Teuchi fait 3,7 têtes de haut, le
client 4,3 ; leurs jambes sont courtes) : chaque image est redressée en trois parts, chacune à son échelle (REF : mesurées sur
l'image de référence de chacun, debout de trois quarts face ; GROUP : chaque groupe de poses à son zoom z de planche, et la
hauteur de sa tête) :
  - la tête (du haut du crâne à la ligne du cou : le menton, la nuque de dos) à HEAD de haut (Teuchi 0,245 m, le client 0,26 m,
    le bandeau et les cheveux compris) et HEAD_W = 0,2 m de large au plus, sans déformation sinon ;
  - le buste (de la ligne du cou à l'entrejambe, ou à l'assise pour les gens assis) à sa vraie longueur (jusqu'à CROTCH =
    0,465 de la taille), en largeur à de vraies épaules de SHOULDERS = 0,45 m ; les bras, le bol, le sac suivent ;
  - les jambes, de l'entrejambe aux pieds, jusqu'au sol (debout), ou de l'assise (SEAT_H, le dessus du coussin) au sol.
La ligne du cou de chaque image : son haut du crâne (la première rangée d'au moins 14 pixels pleins, ou donnée) et la hauteur
de tête de son groupe (la même pour tout le groupe : rien ne saute d'une image à l'autre). Autour de la tête, sa largeur à
elle et celle du corps se rejoignent en douceur (une main sur le front reste sur le front, la perche reste droite). La
perche de Teuchi, plus fine (POLE_W), montée d'un bloc derrière sa main jusqu'à la tringle par crans (POLE_UP). Teuchi
derrière le comptoir : la planche le coupe au ventre ; au comptoir et à la marmite, sous son buste, le bas du buste de sa marche
de face (le kimono, le cordon, le haut du tablier ; TORSO de large), ailleurs une bande de sa couleur, jusqu'à BOTTOM_T (le
comptoir des clients le coupe à 1 m). Naruto : ses images agrandies de N_SCALE, posées sur le coussin.

Chaque image de la planche (T_FR, R_FR : sa boîte, ce qu'il faut ôter autour, son groupe) :
  - la découpe : le fond est le blanc relié au bord de la boîte (les blancs enfermés, la veste, le bandeau, restent à la figure ;
    le blanc pur pris entre un bras et le corps s'en va) ; les meubles de la planche ôtés selon l'image (le comptoir sous son
    dessus, la marmite sous son bord, le tabouret sous l'assise sauf le pantalon, l'étagère : la figure qui pousse depuis le corps
    sans passer par le bois ni par les longs traits des planches) ; la plus grande pièce (et ce qu'elle tient de détaché : le bol,
    la passoire) ; un liseré d'un pixel à demi transparent, l'anticrénelage clair du bord repeint de la couleur voisine ;
  - la réduction : chaque pixel de la scène pris sur SS x SS points de la planche ; plein dès la moitié couverte (pas de
    demi-teinte au bord) ; sa couleur, celle de ses traits sombres s'ils en couvrent assez (INK : les yeux, les doigts, le
    noeud de la cravate restent nets), sinon celle du reste (pas de bouillie) ; les sombres du client un peu relevés (LIFT) ; la
    lumière de la boutique (chaude, d'en haut) ; puis chacun en ses familles de tons (B) ou ses tons d'ombre (A, C).
Où va chaque image : Teuchi au comptoir (idle, calm, nod, smile, serve), à la marmite (stir, lift), à l'étagère de dos (shelf),
sa marche de côté dans l'allée (walk) et à la porte (dwalk), de face à la porte (dfront), sa perche montée par crans jusqu'à la
tringle (dpole), s'essuyant le front (dbrow) ; le client assis de dos (seat, chop, sip, done), qui se retourne (turn), se lève
(rise), remet sa veste en place (jacket), debout (stand), qui marche vers nous à chaque taille entre son tabouret et la porte
(W), qui remonte la bandoulière de son sac à la porte (fix). Naruto : ses images d'avant, agrandies, en silhouette. Le reste de IRF : ce
qui est devant Teuchi (O), le verre colonne par colonne avec l'ourlet du noren (G), d'où monte la vapeur (wisps), le style
(look : son genre, l'alpha et le grain des deux passes, où sont les liserés dans l'atlas).
"""
import json
import os
import re
import sys
import numpy as np
from PIL import Image

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import interieur as I
import ichiraku_interior as R

ROOT = R.ROOT
JS = os.path.join(ROOT, 'assets', 'street.js')
OUT = 'ramen_figures.webp'
SHEETS = {'teuchi': os.path.join(ROOT, 'tools', 'src', 'ichiraku_teuchi_sheet.webp'),
          'regular': os.path.join(ROOT, 'tools', 'src', 'ichiraku_regular_sheet.webp')}
F, VX, VY, EYE = R.F, R.VX, R.VY, R.EYE
STYLES = {'a': 'ombre', 'b': 'couleur', 'c': 'liseré', 'ombre': 'ombre', 'couleur': 'couleur', 'liseré': 'liseré', 'lisere': 'liseré'}
STYLE = 'liseré'                             # le style écrit (C, choisi par le propriétaire) ; --style le change

# ---- les profondeurs (m, le long de la rue) et les échelles (px par mètre : F / Z)
Z_T = R.Z_C + R.CTR_D + R.AISLE / 2          # Teuchi, au milieu de son allée
Z_S = R.Z_C - R.STOOL['dz'] - 0.12           # le dos des clients assis sur les tabourets
Z_STOOL = R.Z_C - R.STOOL['dz']              # (le milieu des tabourets)
SCALE = 1.19                                 # les mètres de la maquette (l'œil de la rue à 1,5 m) pour un vrai mètre : les repères du sol
                                             # de la peinture (les bordures, les bandes du passage) mettent l'œil à 1,26 m ; la pièce, le
                                             # comptoir, les tabourets restent tels quels, les gens seuls à cette échelle
H_T, H_R = 1.78 * SCALE, 1.82 * SCALE        # Teuchi (son bandeau compris), le client (ses cheveux) : leur taille
DOOR_Z, POLE_X = 17.6, 1215.0                # Teuchi à la porte : sa profondeur (il y vient de côté, de derrière le montant gauche),
                                             # la colonne de sa perche (au milieu de la vitre de droite : lui un peu à gauche)
WALK_END = (1175.0, 0.32)                    # le client qui s'en va : à la porte, la colonne de son milieu, derrière la vitre de tant
PLACES = {'counter': 1199.0, 'pots': -0.25, 'shelf': 9.42}   # Teuchi : au comptoir (sa colonne), à la marmite (à tant de
                                             # son X, la louche à bout de bras), à l'étagère (son X, devant les bocaux de gauche)
N_TOP, N_ROWS = 614, 47                      # Naruto : la rangée 0 de ses images (ses épis à 626), jusqu'au coussin (rangée 660)
N_COL = (20, 6, 10)                          # (Naruto, tel qu'avant : une silhouette sombre)

# ---- les vraies proportions : la tête (haut, largeur au plus), les épaules, l'entrejambe (part de la taille), l'assise
HEAD = {'T': 0.245 * SCALE, 'R': 0.26 * SCALE}   # (du haut du crâne au menton : le bandeau, les cheveux compris)
HEAD_W, SHOULDERS, CROTCH = 0.20 * SCALE, 0.45 * SCALE, 0.465
SEAT_H = R.STOOL['top']
BOTTOM_T, TORSO = 0.9, 0.36 * SCALE          # (Teuchi au comptoir : son buste jusque-là au moins, sous l'arête du comptoir, de tant de large)
# l'image de référence de chacun (debout, de trois quarts face, zoom 1) : sa taille, en pixels de planche la hauteur de sa
# tête (du haut du crâne au menton), de son buste (du menton à l'entrejambe), de ses épaules, la largeur de sa tête de face
REF = {'T': dict(H=H_T, head=50, torso=96, sh=70, hw=48.3),     # (Teuchi : sa marche de face, 582 / 632 / 728 ; au comptoir 58 / 1,2)
       'R': dict(H=H_R, head=56, torso=112, sh=75, hw=48)}      # (le client debout : 515 / 571 / 683)
# chaque groupe de poses : qui, son zoom (pixels de planche pour un de la référence), la hauteur de sa tête (du haut du crâne
# à la ligne du cou), ce qui le pose (le haut de sa tête à sa taille, ses pieds au sol, son assise sur le coussin) ; de dos
# (BACK), du haut du crâne au col, la tête et la nuque que les cheveux cachent : HEAD aussi (pas moins haute que de face)
GROUP = {'buste': ('T', 1.2, 60, 'head'),    # (la rangée du comptoir : le crâne à 23, le menton à 83)
         'buste2': ('T', 1.22, 61, 'head'),  # (la deuxième rangée : 216 / 277)
         'dos': ('T', 0.95, 41, 'head'),     # (l'étagère, de dos : la largeur de sa tête ; le col à 289)
         'pied': ('T', 1.0, 50, 'feet'),     # (la rangée du bas)
         'assis': ('R', 1.08, 49, 'seat'),   # (de dos : la largeur de sa tête et de ses épaules ; le col à 63, l'assise à 176)
         'tourne': ('R', 1.08, 57, 'seat'),  # (le col à 319, l'assise à 425)
         'leve': ('R', 1.0, 55, 'feet'),     # (le menton à 316, à 308)
         'debout': ('R', 1.0, 56, 'feet')}
BACK = ('dos', 'assis', 'tourne')

# ---- les planches du propriétaire : chaque image, sa boîte dans la planche, sa découpe, son groupe (et ce qui le précise :
# le haut du crâne, la ligne du cou, l'entrejambe et sa hauteur, le milieu de la tête)
G = lambda g, **k: dict(g=g, **k)
T_FR = {   # Teuchi
    'idle': (('teuchi', (0, 15, 176, 194), 'counter', G('buste')),),
    'calm': (('teuchi', (176, 15, 352, 194), 'counter', G('buste')),),
    'nod': (('teuchi', (352, 15, 528, 194), 'counter', G('buste')),),
    'smile': (('teuchi', (528, 15, 704, 194), 'counter', G('buste')),),
    'stir': (('teuchi', (716, 15, 875, 194), 'below', G('buste', row=130)), ('teuchi', (889, 15, 1050, 194), 'below', G('buste', row=136)),
             ('teuchi', (1066, 15, 1227, 194), 'below', G('buste', row=136)), ('teuchi', (1241, 15, 1402, 194), 'below', G('buste', row=136)),
             ('teuchi', (189, 205, 344, 386), 'below', G('buste2', row=331)), ('teuchi', (366, 205, 518, 386), 'below', G('buste2', row=331))),
    'lift': (('teuchi', (15, 195, 167, 386), 'below', G('buste2', row=331, crown=216)),),
    'serve': (('teuchi', (540, 205, 699, 386), 'free', G('buste2', multi=True)), ('teuchi', (718, 205, 872, 386), 'free', G('buste2', multi=True))),
    'shelf': (('teuchi', (880, 200, 1056, 386), 'shelf', G('dos', top=243, low=299, crown=248)),
              ('teuchi', (1232, 200, 1408, 386), 'shelf', G('dos', top=243, low=299, crown=248))),
    'walk': tuple(('teuchi', b, 'free', G('pied')) for b in ((558, 576, 666, 768), (741, 576, 845, 768), (920, 576, 1017, 768),
                                                             (1096, 576, 1194, 768), (1265, 576, 1372, 768))),
    'front': (('teuchi', (392, 576, 485, 768), 'free', G('pied')),),
    'pole': (('teuchi', (33, 572, 157, 768), 'free', G('pied', crown=586)),),
    'brow': (('teuchi', (208, 578, 324, 768), 'free', G('pied', crown=586)),),
}
R_FR = {   # le client
    'seat': (('regular', (55, 8, 205, 252), 'stool', G('assis')),),
    'chop': (('regular', (358, 8, 524, 252), 'stool', G('assis')),),
    'sip': (('regular', (570, 8, 707, 252), 'stool', G('assis')), ('regular', (804, 8, 942, 252), 'stool', G('assis'))),
    'done': (('regular', (1105, 8, 1273, 252), 'stool', G('assis')),),
    'turn': (('regular', (83, 252, 219, 503), 'stool', G('tourne', crown=262)), ('regular', (435, 252, 570, 503), 'stool', G('tourne', crown=262))),
    'rise': (('regular', (756, 252, 926, 503), 'stool', G('leve', x=(750, 850), run=12, crown=261, crotch=430, crotch_h=0.62)),
             ('regular', (1167, 247, 1334, 503), 'stool', G('leve', x=(1160, 1245), run=12, crown=253, crotch=408))),
    'stand': (('regular', (26, 508, 134, 762), 'free', G('debout', flip=True)),),   # (retourné : son sac du côté où il le porte en marchant)
    'jacket': (('regular', (935, 508, 1112, 762), 'free', G('debout')), ('regular', (1117, 508, 1258, 762), 'free', G('debout'))),
    'walk': tuple(('regular', b, 'free', G('debout')) for b in ((326, 508, 452, 762), (480, 508, 605, 762), (630, 508, 753, 762), (785, 508, 896, 762))),
    'fix': (('regular', (1264, 508, 1391, 762), 'free', G('debout', tint=((1279, 618, 1306, 674, (112, 64, 42)),))),),
}
SS = 8                                       # (les points de planche pris par pixel de la scène : SS x SS)
INK = (0.55, 0.3)                            # un trait sombre : plus sombre que tant de fois le clair de son pixel ; il le colore s'il
                                             # en couvre au moins tant
BLEND = (0.35, 0.1)                          # (autour de la tête, de sa largeur à celle du corps : sur tant de sa largeur à côté, tant de
                                             # sa hauteur sous le cou)
POLE_W = 0.55                                # (la perche, moins large que dessinée : 3 cm)
WARM = (0.96, 0.87, 0.75)                    # la lumière de la boutique sur eux (chaude) ; d'en haut : la tête plus claire que le
TOPLIGHT = (1.07, 0.9)                       # bas de la figure (de tant à tant)
LIFT = {'T': 1.0, 'R': 0.85}                 # (les sombres relevés : le costume bleu nuit du client, de dos, garde ses plis)
FAMILIES = 16                                # les couleurs de chacun, après réduction : autant de familles de tons (B), chacune d'un grain
GRAIN_B = 3                                  # fin de plus ou moins tant de niveaux (pas d'aplat), au plus ISOLATED de pixels seuls dans
ISOLATED = 0.2                               # leur famille (sans voisin de la même)
VALUES = (42.0, 66.0)                        # la clarté (L*) des couleurs, gardée dans celle de la peinture autour (son 98e centile sur le verre,
                                             # la lanterne à part) : au-dessus du premier, ramenée sous le second
OUTLINE_DL = 12.0                            # pas de trait sombre continu au bord : un pixel du bord plus sombre de tant que le dedans en prend
                                             # la couleur, sauf du côté de l'ombre (SHADOW_COS : tourné à l'opposé de la lumière, LIGHT)
SHADOW_COS = -0.25
FACE = (10, 15, (0.42, 0.66))                # le détail selon la tête (pixels de haut) : sous le premier, pas de traits ; jusqu'au second, un
                                             # pixel pour chaque oeil (dans cette bande de la tête) ; au-delà, la bouche, le nez
N_SCALE = 1.4                                # (Naruto : ses images agrandies d'autant, posées sur le coussin)
POLE_UP = (0.0, 0.35, 0.7, 1.0)              # la perche de Teuchi montée de tant (part de ce qu'il faut pour atteindre la tringle)
# l'ombre : ses trois tons (le plus sombre, la base d'avant, un peu moins sombre) pour Teuchi derrière le comptoir et pour les
# gens plus près ; leur clarté (L*) dans la planche réduite qui sépare les tons ; l'alpha et le grain de chaque passe
TONES = {'far': ((24, 8, 5), (34, 10, 6), (47, 17, 10)), 'near': ((13, 4, 7), (20, 6, 10), (32, 12, 15))}
TONE_L = {'T': (30.0, 62.0), 'R': (12.0, 45.0)}   # (Teuchi en blanc, le client en bleu nuit : ses traits plus sombres que lui)
SHADE = {'alpha': [0.86, 0.95], 'grain': [1, 0.5]}
# le liseré : la lumière qui l'allume (une direction dans l'image, y vers le bas) pour chaque groupe de cases ; un bord la
# reçoit s'il lui fait face d'au moins tant ; la clarté (L*) qu'il prend au moins
LIGHT = {'T': (-0.45, -1.0), 'D': (0.0, -1.0), 'S': (0.55, -1.0), 'W': (0.3, -1.0)}
RIM_COS, RIM_L, RIM_DOWN = 0.42, (50.0, 66.0), 0.42   # (sa clarté : entre tant et tant ; sur tant du haut de la figure)
RIM_WARM = (1.0, 0.84, 0.62)                 # (la lumière chaude qui choisit, dans les couleurs claires du personnage, celle du liseré)


def row(h, Z):                               # (la rangée d'une hauteur h à la profondeur Z)
    return VY - (h - EYE) * F / Z


def col(X, Z):
    return VX + F * X / Z


# ---- la découpe : le fond blanc ôté (le blanc relié au bord de la case), les accessoires de la planche ôtés (comptoir,
# marmite, étagère, tabouret : la maquette a les siens), les poussières ôtées, le liseré clair du bord repris à la couleur du
# trait le plus proche, l'alpha partiel seulement sur ce liseré
def grow(m, n=1):
    for _ in range(n):
        d = m.copy(); d[1:] |= m[:-1]; d[:-1] |= m[1:]; d[:, 1:] |= m[:, :-1]; d[:, :-1] |= m[:, 1:]; m = d
    return m


def label(m):
    H, W = m.shape; lab_ = np.zeros((H, W), np.int32); n = 0
    for y0, x0 in zip(*np.nonzero(m)):
        if lab_[y0, x0]: continue
        n += 1; st = [(y0, x0)]; lab_[y0, x0] = n
        while st:
            y, x = st.pop()
            for yy, xx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
                if 0 <= yy < H and 0 <= xx < W and m[yy, xx] and not lab_[yy, xx]: lab_[yy, xx] = n; st.append((yy, xx))
    return lab_, n


def cut(sheets, sheet, box, kind, o):
    x0, y0, x1, y1 = box; P = sheets[sheet][y0:y1, x0:x1].copy()
    for a0, b0, a1, b1, hue in o.get('tint', ()):   # (un rabat de sac peint en transparence sur le blanc : rendu à sa couleur)
        S = P[b0 - y0:b1 - y0, a0 - x0:a1 - x0]; sat = S.max(2) - S.min(2); lum = S.sum(2)
        m_ = (sat < 45) & (lum > 200) & (lum < 600)
        S[m_] = np.array(hue, float)[None] * (lum[m_] / sum(hue))[:, None]
    r, g, b = P[..., 0], P[..., 1], P[..., 2]; L = P.sum(2)
    ink = (255 - P).sum(2)
    solid = ink > 60; void = np.zeros_like(solid); seat = None
    if kind == 'counter':                    # (le comptoir de la planche : sous son dessus)
        brown = (r > 100) & (r < 200) & (b < r - 40)
        tops = [y for y in range(len(P) - 1, 0, -1) if brown[y].mean() > 0.6]
        void[(min(tops) if tops else len(P)) - 3:] = True
    if kind == 'below':                      # (la marmite de la planche : sous son bord)
        void[o['row'] - y0:] = True
    if kind == 'stool':                      # (le tabouret de la planche : sous l'assise, entre les jambes, tout sauf le pantalon)
        wood = (r > 85) & (r < 225) & (r - b > 40) & (r - g > 22) & (L > 230)
        if 'x' in o: wood[:, :max(0, o['x'][0] - x0)] = False; wood[:, max(0, o['x'][1] - x0):] = False
        rows = [y for y in range(int(len(P) * 0.55), len(P)) if wood[y].sum() >= o.get('run', 28)]
        st = (rows[0] if rows else len(P)) - 2; seat = y0 + st
        cols = np.nonzero(wood[st:].any(0))[0]
        if len(cols):
            navy = (b > r + 8) & (b > 25)
            void[st:, cols.min():cols.max() + 1] = ~navy[st:, cols.min():cols.max() + 1]
    if kind == 'shelf':                      # (l'étagère, ses planches et ses bocaux : la figure, c'est ce qui pousse depuis le corps
        brown = (r > 95) & (r < 216) & (r - b > 45) & (r - g > 25) & (b < 0.6 * r)   # sous la planche du bas, sans passer par le
        def runs(m):                                                    # bois ni par les longs traits des planches (le sombre de leur
            out = np.zeros(m.shape, int)                                # bord, le clair de leur arête) ; ce qu'elle enferme lui reste,
            for y in range(len(m)):                                     # sauf le bois)
                d = np.diff(np.r_[0, m[y].astype(int), 0])
                for s0, s1 in zip(np.nonzero(d == 1)[0], np.nonzero(d == -1)[0]): out[y, s0:s1] = s1 - s0
            return out
        near = grow(brown, 3); dark = L < 200; light = (L > 450) & (ink > 40)
        line = (dark & (runs(dark) >= 10) & near) | (light & (runs(light) >= 16) & near)
        low = o['low'] - y0; top = o['top'] - y0
        body = solid.copy(); body[:low] = False
        cols = np.nonzero(body[low:low + 12].any(0))[0]
        go = solid & ~brown & ~line; go[:top] = False
        go[:, :max(0, cols.min() - 4)] = False; go[:, cols.max() + 5:] = False
        keep = body.copy(); st = list(zip(*np.nonzero(body[low:low + 1]))); st = [(y + low, x) for y, x in st]
        while st:
            y, x = st.pop()
            for yy, xx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1), (y - 1, x - 1), (y - 1, x + 1)):
                if 0 <= yy < low and 0 <= xx < keep.shape[1] and go[yy, xx] and not keep[yy, xx]: keep[yy, xx] = True; st.append((yy, xx))
        hl, hn = label(~keep)                # (ce qu'elle enferme)
        edge = set(hl[0]) | set(hl[-1]) | set(hl[:, 0]) | set(hl[:, -1])
        keep |= ~np.isin(hl, list(edge)) & (hl > 0)
        thin = runs(keep.T).T <= 2; thin[low:] = False                 # (pas de fil : les bouts d'arête restés au bord d'une main)
        keep &= ~thin; kl, _ = label(keep); keep = np.isin(kl, np.unique(kl[low][keep[low]]))
        keep[:low] &= ~brown[:low]
        void |= ~keep
    solid &= ~void
    free = ~solid | void                     # le fond : le blanc relié au bord (les blancs enfermés restent à la figure)
    ext = np.zeros_like(free); H, W = free.shape
    st = [(y, x) for y in range(H) for x in (0, W - 1) if free[y, x]] + [(y, x) for x in range(W) for y in (0, H - 1) if free[y, x]]
    for y, x in st: ext[y, x] = True
    while st:
        y, x = st.pop()
        for yy, xx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
            if 0 <= yy < H and 0 <= xx < W and free[yy, xx] and not ext[yy, xx]: ext[yy, xx] = True; st.append((yy, xx))
    fig = ~ext & ~void
    gap = fig & (ink < 20)                   # (le fond pris entre un bras et le corps : blanc pur, enfermé)
    gl_, gn = label(gap)
    if gn:
        gs = np.bincount(gl_.ravel()); gs[0] = 0
        fig &= ~(gs >= 12)[gl_]
    lab_, n = label(fig)
    if n:                                    # (la figure ; ce qu'elle tient de détaché aussi s'il est assez grand ; pas de poussière)
        sizes = np.bincount(lab_.ravel()); sizes[0] = 0
        keepc = (sizes >= 300) if o.get('multi') else (np.arange(len(sizes)) == sizes.argmax())
        keepc[0] = False; fig = keepc[lab_]
    ring = grow(fig) & ~fig & ~void
    a = np.where(fig, 1.0, np.where(ring, np.clip((ink - 25) / 110, 0, 1), 0))
    aa = (a > 0) & grow(~fig, 2) & (ink < 450)   # (le clair et le gris d'entre le trait et le blanc : pas de liseré clair)
    Q = P.copy(); have = (a > 0) & ~aa
    for _ in range(6):
        if have[a > 0].all(): break
        acc = np.zeros_like(Q); cnt = np.zeros(have.shape)
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            sh = np.roll(np.roll(have, dy, 0), dx, 1); acc += np.roll(np.roll(Q, dy, 0), dx, 1) * sh[..., None]; cnt += sh
        new = ~have & (cnt > 0); Q[new] = acc[new] / cnt[new][:, None]; have |= new
    if o.get('flip'): Q, a = Q[:, ::-1].copy(), a[:, ::-1].copy()
    return Q, a, seat


def runs_of(m):
    d = np.diff(np.r_[0, m.astype(int), 0])
    return list(zip(np.nonzero(d == 1)[0], np.nonzero(d == -1)[0]))


def chest(a):
    """le milieu du buste d'une figure découpée (la moyenne des colonnes entre 35 et 60 % de sa hauteur) : ce qui la pose en x"""
    rows = np.nonzero((a > 0.5).sum(1) >= 8)[0]; top, bot = rows[0], rows[-1] + 1
    band = a[top + int(0.35 * (bot - top)):top + int(0.6 * (bot - top))] > 0.5
    return np.nonzero(band)[1].mean() + 0.5


def measure(a, o, y0):
    """la mesure d'une image (en pixels de la case) : le haut du crâne (la première rangée d'au moins 14 pixels pleins, ou
    donnée), la ligne du cou (le crâne plus la hauteur de tête de son groupe, ou donnée), l'entrejambe ; le milieu de la tête
    (la médiane des milieux de ses rangées pleines du haut) et sa largeur, le milieu du cou"""
    who, z, hn, pose = GROUP[o['g']]; m = a > 0.5
    crown = o['crown'] - y0 if 'crown' in o else next(y for y in range(len(m)) if any(e - s >= 14 for s, e in runs_of(m[y])))
    neck = o['neck'] - y0 if 'neck' in o else crown + hn
    mids, wids = [], []
    for y in range(crown + int(0.15 * hn), crown + int(0.7 * hn)):
        rr = runs_of(m[y])
        if rr: s, e = max(rr, key=lambda r: r[1] - r[0]); mids.append((s + e) / 2); wids.append(e - s)
    hx = o.get('hx', float(np.median(mids[:max(3, len(mids) // 2)])))
    hw = min(float(np.median(wids)), REF[who]['hw'] * z * 1.1)
    rr = [r for r in runs_of(m[neck - 1]) if r[0] <= hx + hw / 2 and r[1] >= hx - hw / 2]
    xn = (min(max((rr[0][0] + rr[0][1]) / 2, hx - hw / 4), hx + hw / 4)) if rr else hx
    crotch = o['crotch'] - y0 if 'crotch' in o else neck + REF[who]['torso'] * z
    return dict(crown=crown, neck=neck, crotch=crotch, hx=hx, hw=hw, xn=xn)


def knots(who, o, g, a, seat_row, s, anchor_y):
    """la rangée de la scène de chaque rangée de la case (une ligne brisée : la tête, le buste, les jambes ou l'assise), posée
    par le haut du crâne (anchor_y : sa rangée), les pieds ou l'assise (anchor_y : la rangée du sol) ; rend les noeuds
    (rangée de la case, rangée de la scène), la pente au-dessus du crâne, et l'échelle de la tête et du corps en largeur"""
    w_, z, hn, pose = GROUP[o['g']]; ref = REF[who]
    hd = HEAD[who]
    mh = hd / (hn if o['g'] in BACK else ref['head'] * z)              # (m par pixel de planche : la tête,
    mt = (ref['H'] * (1 - CROTCH) - hd) / ref['torso'] / z              # le buste,
    mx = SHOULDERS / ref['sh'] / z                                      # le corps en largeur,
    mhx = min(hd / ref['head'] / z, HEAD_W / ref['hw'] / z)            # la tête en largeur)
    crown, neck, crotch = g['crown'], g['neck'], g['crotch']
    ys = np.nonzero((a > 0.5).any(1))[0]; feet = ys[-1] + 1
    if pose == 'head':
        K = [(crown, anchor_y), (neck, anchor_y + s * (neck - crown) * mh), (feet + 400, anchor_y + s * ((neck - crown) * mh + (feet + 400 - neck) * mt))]
    else:
        if pose == 'seat': low, low_h = seat_row, SEAT_H
        else: low, low_h = crotch, o['crotch_h'] * SCALE if 'crotch_h' in o else CROTCH * ref['H']
        h_neck = low_h + (low - neck) * mt
        K = [(crown, anchor_y - s * (h_neck + (neck - crown) * mh)), (neck, anchor_y - s * h_neck), (low, anchor_y - s * low_h), (feet, anchor_y)]
    return K, s * mh, s * mhx, s * mx


def warp(Q, a, K, up, kh, kb, g, X_n, pole=None):
    """la case réduite à l'échelle de la scène : les rangées par la ligne brisée K (au-dessus de son premier noeud, la pente
    up) ; les colonnes autour du milieu du cou (xn, qui tombe en X_n), kh pixels de la scène par pixel de planche dans la tête,
    kb dans le corps, de l'une à l'autre en douceur autour de la tête (BLEND) ; chaque pixel pris sur SS x SS points (le
    plus proche de la planche). Rend la case (ses points : couleurs, alpha) et sa rangée, sa colonne de la scène du haut à
    gauche ; pole : (x0, x1, axe, échelle) les colonnes de la perche, plus fine autour de son axe"""
    H, W = a.shape
    ky = np.array([k[0] for k in K], float); kY = np.array([k[1] for k in K], float)
    def Y_of(y):
        y = np.asarray(y, float)
        return np.where(y < ky[0], kY[0] - (ky[0] - y) * up, np.where(y > ky[-1], kY[-1] + (y - ky[-1]) * (kY[-1] - kY[-2]) / (ky[-1] - ky[-2]),
                                                                         np.interp(y, ky, kY)))
    def y_of(Y):
        Y = np.asarray(Y, float)
        return np.where(Y < kY[0], ky[0] - (kY[0] - Y) / up, np.where(Y > kY[-1], ky[-1] + (Y - kY[-1]) * (ky[-1] - ky[-2]) / (kY[-1] - kY[-2]),
                                                                         np.interp(Y, kY, ky)))
    ys, xs = np.nonzero(a > 0)
    T = int(np.floor(Y_of(ys.min()))) - 1; Bm = int(np.ceil(Y_of(ys.max() + 1))) + 1
    xn, hx, hw, neck = g['xn'], g['hx'], g['hw'], g['neck']
    Lc = int(np.floor(X_n + (xs.min() - xn) * kb)) - 2; Rc = int(np.ceil(X_n + (xs.max() + 1 - xn) * kb)) + 2
    nr, nc = Bm - T, Rc - Lc
    xg = np.arange(-2.0, W + 2.0, 0.25)
    dist = np.maximum(0, np.abs(xg - hx) - hw / 2)
    wx = np.clip(1 - dist / (BLEND[0] * hw), 0, 1)
    Xd = Lc + (np.arange(nc * SS) + 0.5) / SS
    C = np.zeros((nr * SS, nc * SS, 3)); A = np.zeros((nr * SS, nc * SS)); Hd = np.zeros((nr * SS, nc * SS), bool)
    Yd = T + (np.arange(nr * SS) + 0.5) / SS; Ys = y_of(Yd)
    hn = neck - g['crown']
    for i, yv in enumerate(Ys):
        wy = 1.0 if yv < neck else max(0.0, 1 - (yv - neck) / (BLEND[1] * hn))
        w = wx * wy
        Xg = X_n + (xg - xn) * (w * kh + (1 - w) * kb)
        if pole is not None:                 # (la perche plus fine autour de son axe : du fond de part et d'autre)
            p0, p1, ax, k = pole; inp = (xg >= p0) & (xg < p1)
            Xg[inp] = X_n + (ax - xn) * kb + (xg[inp] - ax) * kb * k
            right = xg >= p1; Xg[right] = X_n + (ax - xn) * kb + (p1 - ax) * kb * k + (xg[right] - p1) * kb
        xsrc = np.interp(Xd, Xg, xg)
        yi = int(np.floor(yv))
        if yi < 0 or yi >= H: continue
        xi = np.floor(xsrc).astype(int); ok = (xi >= 0) & (xi < W)
        C[i, ok] = Q[yi, xi[ok]]; A[i, ok] = a[yi, xi[ok]]
        if yv < neck: Hd[i] = np.abs(xsrc - hx) <= hw / 2 + 2
    blocks = lambda X: X.reshape((nr, SS, nc, SS) + X.shape[2:]).swapaxes(1, 2).reshape((nr, nc, SS * SS) + X.shape[2:])
    return blocks(C), blocks(A), T, Lc, blocks(Hd).mean(2) >= 0.5


def pick(C, A):
    """chaque pixel : plein dès la moitié couverte ; sa couleur, celle de ses traits sombres s'ils en couvrent assez (INK), sinon
    la moyenne du reste"""
    lum = C @ np.array([0.299, 0.587, 0.114]); on = A > 0.5
    lit = np.where(on, lum, -1); ref = np.percentile(np.where(on, lum, np.nan), 80, axis=2) if on.any() else None
    ref = np.nan_to_num(ref, nan=0.0)
    dark = on & (lum < INK[0] * ref[..., None])
    n_on = on.sum(2); n_dark = dark.sum(2)
    use = np.where((n_dark >= INK[1] * np.maximum(n_on, 1))[..., None], dark, on & ~dark)
    use = np.where((use.sum(2) == 0)[..., None], on, use)
    rgb = (C * use[..., None]).sum(2) / np.maximum(use.sum(2), 1)[..., None]
    return rgb, A.mean(2) >= 0.5


def grade(rgb, m):
    """la lumière chaude de la boutique, d'en haut"""
    ys = np.nonzero(m.any(1))[0]
    if not len(ys): return rgb
    t = np.clip((np.arange(len(m))[:, None, None] - ys[0]) / max(1, ys[-1] - ys[0]), 0, 1)
    return rgb * np.array(WARM) * (TOPLIGHT[0] + (TOPLIGHT[1] - TOPLIGHT[0]) * t)


def palette(P, k):
    """une palette de k couleurs tirée de P (k-means en Lab, départ fixe : la même à chaque fois) ; chaque tranche de clarté y
    compte à proportion de la racine de son nombre de pixels (les sombres nombreux d'un costume gardent leurs nuances, les clairs
    rares comptent encore)"""
    P = np.asarray(P, float); L = R.lab(P); o = np.lexsort((L[:, 2], L[:, 1], L[:, 0])); P, L = P[o], L[o]
    bands = [np.where((L[:, 0] >= a) & (L[:, 0] < a + 10))[0] for a in range(0, 100, 10)]
    w = np.array([np.sqrt(len(b)) for b in bands]); pick_ = []
    for b, n in zip(bands, np.round(5000 * w / w.sum()).astype(int)):
        if len(b) and n: pick_ += list(b[np.linspace(0, len(b) - 1, min(n, len(b))).astype(int)])
    P, L = P[pick_], L[pick_]
    C = L[np.linspace(0, len(L) - 1, k).astype(int)].copy()
    for _ in range(50):
        a = np.argmin(((L[:, None] - C[None]) ** 2).sum(2), 1)
        for j in range(k):
            if (a == j).any(): C[j] = L[a == j].mean(0)
    a = np.argmin(((L[:, None] - C[None]) ** 2).sum(2), 1)
    return np.array([P[a == j].mean(0) for j in range(k) if (a == j).any()])


def rim_of(m, light):
    """les pixels du bord d'une silhouette tournés vers la lumière (sa direction dans l'image), sur le haut de la figure"""
    p = np.pad(m, 1); inside = p[1:-1, 1:-1]
    edge = inside & ~(p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:])
    ys = np.nonzero(m.any(1))[0]; edge[ys[0] + int(np.ceil(RIM_DOWN * (ys[-1] + 1 - ys[0]))):] = False
    f = np.pad(m.astype(float), 3)
    for _ in range(2):
        f = sum(np.roll(np.roll(f, dy, 0), dx, 1) for dy in (-1, 0, 1) for dx in (-1, 0, 1)) / 9
    gy, gx = np.gradient(f); gy, gx = -gy[3:-3, 3:-3], -gx[3:-3, 3:-3]   # (la normale vers le dehors)
    n = np.hypot(gx, gy) + 1e-9; l = np.array(light, float); l /= np.hypot(*l)
    return edge & ((gx * l[0] + gy * l[1]) / n >= RIM_COS)


def ring_depth(m, n=3):
    """la profondeur de chaque pixel d'une figure depuis son bord (1 : le bord, jusqu'à n)"""
    d = np.zeros(m.shape, int); cur = m.copy()
    for k in range(1, n + 1):
        p = np.pad(cur, 1); inner = cur & p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:]
        d[cur & ~inner] = k; cur = inner
    d[cur] = n + 1
    return d


def normals(m):
    """la normale du bord (vers le dehors) de chaque pixel"""
    f = np.pad(m.astype(float), 3)
    for _ in range(2):
        f = sum(np.roll(np.roll(f, dy, 0), dx, 1) for dy in (-1, 0, 1) for dx in (-1, 0, 1)) / 9
    gy, gx = np.gradient(f); gy, gx = -gy[3:-3, 3:-3], -gx[3:-3, 3:-3]
    n = np.hypot(gx, gy) + 1e-9
    return gx / n, gy / n


def no_outline(v, m, L, light):
    """pas de trait sombre continu au bord : les pixels des deux premiers rangs du bord plus sombres (de OUTLINE_DL) que le plus
    proche du dedans (le troisième rang, à deux pixels au plus) en prennent la couleur ; pas du côté de l'ombre"""
    d = ring_depth(m); nx, ny = normals(m); l = np.array(light, float); l /= np.hypot(*l)
    shade = nx * l[0] + ny * l[1] <= SHADOW_COS
    out = v.copy(); H, W = m.shape
    for y, x in zip(*np.nonzero((d >= 1) & (d <= 2) & ~shade)):
        best = None
        for r in (1, 2):
            for yy in range(max(0, y - r), min(H, y + r + 1)):
                for xx in range(max(0, x - r), min(W, x + r + 1)):
                    if d[yy, xx] >= 3 and (best is None or abs(yy - y) + abs(xx - x) < best[0]): best = (abs(yy - y) + abs(xx - x), yy, xx)
            if best: break
        if best and L[v[y, x]] < L[v[best[1], best[2]]] - OUTLINE_DL: out[y, x] = v[best[1], best[2]]
    return out


def isolated(v, m, keep):
    """les pixels seuls dans leur famille (aucun de leurs quatre voisins de la figure ne l'a)"""
    p = np.pad(np.where(m, v, -2), 1, constant_values=-2); c = p[1:-1, 1:-1]
    same = (p[:-2, 1:-1] == c) | (p[2:, 1:-1] == c) | (p[1:-1, :-2] == c) | (p[1:-1, 2:] == c)
    return m & ~same


def unspeckle(v, m, keep):
    """au plus ISOLATED de pixels seuls : les seuls (hors ceux gardés : les yeux) prennent la famille la plus nombreuse de leurs
    huit voisins (la plus petite à égalité), tant qu'il le faut"""
    v = v.copy()
    for _ in range(4):
        iso = isolated(v, m, keep)
        if iso.sum() <= ISOLATED * m.sum(): break
        p = np.pad(np.where(m, v, -1), 1, constant_values=-1); H, W = m.shape; new = v.copy()
        for y, x in zip(*np.nonzero(iso & ~keep)):
            nb = p[y:y + 3, x:x + 3].ravel(); nb = nb[(nb >= 0)]; nb = nb[nb != v[y, x]] if (nb != v[y, x]).any() else nb
            vals, cnt = np.unique(nb, return_counts=True); new[y, x] = vals[np.argmax(cnt)]
        v = new
    return v


def face_detail(v, m, hd, hy, fam):
    """les traits du visage selon la hauteur de la tête (FACE) : un trait, ce que la peau de la tête enferme ; sous le premier
    seuil, pris par la peau ; jusqu'au second, un pixel par trait dans la bande des yeux (le plus sombre), le reste à la peau ;
    au-delà, tels quels. Rend aussi les pixels gardés"""
    keep = np.zeros(m.shape, bool); h = hy[1] - hy[0]
    if h >= FACE[1] or not hd.any(): return v, keep
    lab_ = R.lab(fam)
    skin_f = np.nonzero((lab_[:, 1] >= 8) & (lab_[:, 1] <= 40) & (lab_[:, 2] >= 10) & (lab_[:, 2] <= 45) & (lab_[:, 0] >= 30))[0]
    S = hd & np.isin(v, skin_f)
    if not S.any(): return v, keep
    v0, v = v, v.copy(); skin_c = np.bincount(v0[S]).argmax()
    hl, n = label(hd & ~S)
    for j in range(1, n + 1):
        comp = hl == j; ring = grow(comp) & ~comp
        if (ring & S).sum() < 0.75 * ring.sum(): continue          # (pas enfermé par la peau : les cheveux, le bandeau, le col)
        ys, xs = np.nonzero(comp); v[comp] = skin_c
        if h >= FACE[0]:
            band = (ys >= hy[0] + FACE[2][0] * h) & (ys <= hy[0] + FACE[2][1] * h)
            if band.any():
                k_ = np.argmin(np.where(band, lab_[v0[ys, xs], 0], 1e9))
                v[ys[k_], xs[k_]] = v0[ys[k_], xs[k_]]; keep[ys[k_], xs[k_]] = True
    return v, keep


def cap_values(P):
    """des couleurs gardées dans la clarté de la peinture autour (VALUES) : au-dessus du premier seuil, la clarté ramenée sous le
    second, en proportion"""
    lab_ = R.lab(P); L = lab_[:, 0]; top = max(L.max(), VALUES[1] + 1e-6)
    lab_[:, 0] = np.where(L > VALUES[0], VALUES[0] + (L - VALUES[0]) * (VALUES[1] - VALUES[0]) / (top - VALUES[0]), L)
    return lab2rgb(lab_)

class Atlas:
    """les cases, rangées en étagères dans une image ; leur boîte [sx, sy, w, h]"""
    def __init__(self, width):
        self.W, self.x, self.y, self.rowh, self.cells = width, 0, 0, 0, []

    def add(self, rgba, rim=None):
        h, w = rgba.shape[:2]
        if self.x + w > self.W: self.x, self.y, self.rowh = 0, self.y + self.rowh + 1, 0
        self.cells.append((self.x, self.y, rgba, rim)); box = [self.x, self.y, w, h]
        self.x += w + 1; self.rowh = max(self.rowh, h)
        return box

    def image(self):
        """l'atlas ; s'il y a des liserés, leur atlas dessous (à la même place, plus la hauteur de l'atlas et un : look.rim)"""
        H = self.y + self.rowh; rims = any(r is not None for *_, r in self.cells)
        a = np.zeros(((2 * H + 1) if rims else H, self.W, 4), np.uint8)
        for x, y, c, r in self.cells:
            a[y:y + c.shape[0], x:x + c.shape[1]] = c
            if r is not None: a[H + 1 + y:H + 1 + y + r.shape[0], x:x + r.shape[1]] = r
        return a, (H + 1 if rims else 0)


def naruto_cells():
    """Naruto au comptoir, de dos : ses six images (assets/naruto_ramen.webp, 23 x 37 : assis, penché, deux pour aspirer, la
    tête levée, les bouts du bandeau), le bas du dos prolongé jusqu'au coussin (ses rangées du bas, qui se resserraient, refaites
    droites), agrandies de N_SCALE, posées sur le coussin (leur forme lissée : chaque pixel plein dès la moitié couverte) ; une
    silhouette sombre, comme avant. Rend les images, la rangée du haut, le milieu"""
    a = I.load('naruto_ramen.webp', 'RGBA')[..., 3] > 128
    H2, W2 = int(round(N_ROWS * N_SCALE)), int(round(23 * N_SCALE)); out = []
    for f in range(6):
        c = a[:, f * 23:(f + 1) * 23]
        m = np.zeros((N_ROWS, 23), bool); m[:33] = c[:33]
        for r in range(33, N_ROWS):
            k = int(round(1.5 * (r - 33) / (N_ROWS - 34)))
            m[r, 3 + k:20 - k] = True
        src = Image.fromarray(np.pad(m, 4).astype(np.uint8) * 255, 'L')
        bx = (4 + 11.5 - W2 / N_SCALE / 2, 4 + N_ROWS - H2 / N_SCALE, 4 + 11.5 + W2 / N_SCALE / 2, 4 + N_ROWS)
        up = np.asarray(src.resize((W2 * 4, H2 * 4), Image.BILINEAR, box=bx)).astype(float) / 255
        mm = up.reshape(H2, 4, W2, 4).mean((1, 3)) >= 0.5
        rgba = np.zeros((H2, W2, 4), np.uint8); rgba[..., :3] = N_COL; rgba[..., 3] = mm * 255
        out.append(rgba)
    return out, N_TOP + N_ROWS - H2, W2 / 2

def glass_rows(hem):
    """chaque colonne de verre : la rangée sous la tringle du noren (un rayon vers VP), la dernière au-dessus de la traverse, la
    première au-dessous, la dernière au-dessus de la lisière du bas ; la dernière de l'ourlet du noren (sous lui, son ombre)"""
    out = []
    for a, b in R.VITRES:
        for x in range(a, b + 1):
            top = int(np.ceil(VY - 0.2065 * (x - VX))) + 1
            bot = int(np.round(VY + R.BAS_RAYON * (x - VX) - 0.5)) - 1
            out.append([x, top, R.TRAVERSE[0], R.TRAVERSE[1], bot, int(hem[x])])
    return out


DEBUG, QUAL = [], []                         # (ce que chaque case a mesuré, la part de ses pixels seuls : pour les aperçus)


def main():
    style = STYLE
    if '--style' in sys.argv: style = STYLES[sys.argv[sys.argv.index('--style') + 1].lower()]
    prev = sys.argv[sys.argv.index('--preview') + 1] if '--preview' in sys.argv else None
    sheets = {k: np.asarray(Image.open(p).convert('RGB')).astype(float) for k, p in SHEETS.items()}
    cuts = {}
    for who, table in (('T', T_FR), ('R', R_FR)):
        for name, frames in table.items():
            cuts[who, name] = [(cut(sheets, *f[:3], dict(f[3])), f) for f in frames]

    # ---- chaque case à sa profondeur et à sa vraie taille : Teuchi dans l'allée et à la porte, le client assis, debout, en
    # marche (une taille par pixel de haut) ; puis les couleurs de chacun ramenées à sa palette
    raw = {'T': [], 'R': []}                 # (qui, la passe, groupe, clé, couleurs, plein, case : ox, oy)
    def prepare(who, cq, f, s, anchor_y, int_y=False, strip=True):
        """une image : sa mesure, ses noeuds, ses échelles ; Teuchi derrière le comptoir, son buste coupé au-dessus du bord (du
        comptoir, de la marmite de la planche) et prolongé vers le bas (strip : d'une bande de sa couleur ; sinon pas)"""
        (Q, a, seat), (sheet, box, kind, o) = cq, f
        o = dict(o); y0 = box[1]
        g = measure(a, o, y0); cx = chest(a)
        K, kh, khx, kb = knots(who, o, g, a, None if seat is None else seat - y0, s, anchor_y)
        if GROUP[o['g']][3] == 'head':       # (sous l'arête du comptoir : sa rangée d'un peu au-dessus du bord, au-dessus du bord de la
            ys = np.nonzero((a > 0.5).any(1))[0]   # marmite de la planche, plein ou vide)
            r_ = o['row'] - y0 - 7 if kind == 'below' else ys[-1] - 3
            need = (row(BOTTOM_T, Z_T) - np.interp(r_ + 1, [k[0] for k in K], [k[1] for k in K])) / ((K[-1][1] - K[-2][1]) / (K[-1][0] - K[-2][0]))
            if need > 0 and not strip:
                Q, a = Q[:r_ + 1], a[:r_ + 1]
            elif need > 0:                   # (le buste seul, TORSO de large, de sa couleur claire, son trait sur ses deux bords)
                n = int(np.ceil(need)) + 4; ref = REF[who]; z = GROUP[o['g']][1]
                tw = TORSO / (SHOULDERS / ref['sh'] / z); c0, c1 = int(round(cx - tw / 2)), int(round(cx + tw / 2))
                B = Q[r_ - 6:r_ + 1, c0:c1].reshape(-1, 3); on = (a[r_ - 6:r_ + 1, c0:c1] > 0.5).ravel()
                lum = B @ np.array([0.299, 0.587, 0.114]); lit = on & (lum >= np.median(lum[on]))
                q = np.zeros((a.shape[1], 3)); q[c0:c1] = np.median(B[lit], 0); q[c0:c0 + 3] = q[c1 - 3:c1] = B[on][np.argmin(lum[on])]
                al = np.zeros(a.shape[1]); al[c0:c1] = 1.0
                Q = np.concatenate([Q[:r_ + 1], np.repeat(q[None], n, 0)])
                a = np.concatenate([a[:r_ + 1], np.repeat(al[None], n, 0)])
        if int_y:                            # (le sol sur un coin de pixel)
            K = [(k0, k1 - anchor_y) for k0, k1 in K]
        return Q, a, dict(g=g, K=K, kh=kh, khx=khx, kb=kb, X_n=-(cx - g['xn']) * kb, box=box)   # (le milieu du buste au coin 0)

    def render(Q, a, P, pole=None):
        C, A, T, Lc, hd = warp(Q, a, P['K'], P['kh'], P['khx'], P['kb'], P['g'], P['X_n'], pole)
        rgb, m = pick(C, A)
        return rgb, m, T, Lc, hd & m

    def store(who, part, group, key, rgb, m, T, Lc, hd, P, anchor_y, int_y=False):
        ys, xs = np.nonzero(m)
        t, b_, l, r_ = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        ox, oy = -(Lc + l), (0 if int_y else int(round(anchor_y))) - (T + t)
        DEBUG.append(dict(who=who, part=part, group=group, key=key, box=P['box'], g=P['g'], K=P['K'], kh=P['kh'], khx=P['khx'], kb=P['kb'], X_n=P['X_n'],
                          cell=(b_ - t, r_ - l), ox=ox, oy=oy, anchor_y=anchor_y))
        ky, kY = [k[0] for k in P['K']], [k[1] for k in P['K']]
        Yc, Yn = (kY[0] - (ky[0] - P['g'][q]) * P['kh'] if P['g'][q] < ky[0] else np.interp(P['g'][q], ky, kY) for q in ('crown', 'neck'))
        raw[who].append((part, group, key, rgb[t:b_, l:r_], m[t:b_, l:r_], ox, oy, hd[t:b_, l:r_], (Yc - T - t, Yn - T - t)))

    def put(who, part, group, key, cq, f, s, anchor_y, int_y=False):
        Q, a, P = prepare(who, cq, f, s, anchor_y, int_y)
        store(who, part, group, key, *render(Q, a, P), P, anchor_y, int_y)
    s_t, s_door, s_s = F / Z_T, F / DOOR_Z, F / Z_S
    # au comptoir, à la marmite : sous son buste (la planche le coupe au ventre), le bas de son buste de face (sa marche de face :
    # le kimono, le cordon et le haut du tablier), TORSO de large, jusque sous l'arête du comptoir
    _, _, Pf = prepare('T', cuts['T', 'front'][0][0], cuts['T', 'front'][0][1], s_t, row(0, Z_T))
    fr_, fm_, fT_, fL_, _ = render(*cuts['T', 'front'][0][0][:2], Pf)
    tw = TORSO * s_t; bottom = int(np.ceil(row(BOTTOM_T, Z_T))); fr_, fm_ = fr_[:bottom - fT_], fm_[:bottom - fT_]
    for name in ('idle', 'calm', 'nod', 'smile', 'stir', 'lift'):
        for cq, f in cuts['T', name]:
            Q, a, P = prepare('T', cq, f, s_t, row(H_T, Z_T), strip=False)
            br, bm, bT, bL, bh = render(Q, a, P)
            yb = bT + np.nonzero(bm.any(1))[0][-1]
            T0, L0 = min(bT, fT_), min(bL, fL_); Hc = max(bT + bm.shape[0], bottom) - T0; Wc = max(bL + bm.shape[1], fL_ + fm_.shape[1]) - L0
            rgb = np.zeros((Hc, Wc, 3)); m = np.zeros((Hc, Wc), bool); hd = np.zeros((Hc, Wc), bool)
            Yf = fT_ + np.arange(fm_.shape[0])[:, None]; Xf = fL_ + np.arange(fm_.shape[1])[None] + 0.5
            low = fm_ & (Yf >= yb - 1) & (Yf < bottom) & (np.abs(Xf) <= tw / 2)
            sl = (slice(fT_ - T0, fT_ - T0 + fm_.shape[0]), slice(fL_ - L0, fL_ - L0 + fm_.shape[1]))
            rgb[sl][low] = fr_[low]; m[sl] |= low
            sl = (slice(bT - T0, bT - T0 + bm.shape[0]), slice(bL - L0, bL - L0 + bm.shape[1]))
            rgb[sl][bm] = br[bm]; m[sl] |= bm; hd[sl] |= bh
            store('T', 'T', name, None, rgb, m, T0, L0, hd, P, row(H_T, Z_T))
    for name in ('serve', 'shelf'):
        for cq, f in cuts['T', name]: put('T', 'T', name, None, cq, f, s_t, row(H_T, Z_T))
    for cq, f in cuts['T', 'walk']: put('T', 'T', 'walk', None, cq, f, s_t, row(0, Z_T))
    for cq, f in cuts['T', 'walk']: put('T', 'D', 'dwalk', None, cq, f, s_door, row(0, DOOR_Z))
    for cq, f in cuts['T', 'front']: put('T', 'D', 'dfront', None, cq, f, s_door, row(0, DOOR_Z))
    for cq, f in cuts['T', 'brow']: put('T', 'D', 'dbrow', None, cq, f, s_door, row(0, DOOR_Z))
    # la perche montée vers la tringle : la perche entière (son bois, son trait, le crochet au-dessus de la tête ; sa part cachée
    # par la main refaite d'après la rangée au-dessus) glissée vers le haut derrière la main, la figure au sol
    ((Qp, ap, _), fp), = cuts['T', 'pole']
    rr, gg, bb = Qp[..., 0], Qp[..., 1], Qp[..., 2]
    xs_pole = np.nonzero(((rr - bb > 25) & (rr < 170) & (ap > 0.5)).sum(0) > 0.55 * (ap > 0.5).any(1).sum())[0]
    p0, p1 = xs_pole.min() - 2, xs_pole.max() + 3
    o = dict(fp[3]); g = measure(ap, o, fp[1][1])
    reg = np.zeros(ap.shape, bool); reg[:, p0:p1] = True; reg[:g['crown'], p0:] = True
    beside = ap[:, p0 - 6:p0] > 0.5; beside = np.c_[beside, ap[:, p1:p1 + 6] > 0.5].any(1); beside[:g['crown']] = False
    hand = beside | np.r_[False, beside[:-1]] | np.r_[beside[1:], False]   # (les rangées de la main : la perche n'y est pas seule)
    pole = reg & (ap > 0.5) & ~hand[:, None]
    prow = np.nonzero(pole[:, p0:p1].any(1))[0]
    width = pole[:, p0:p1].sum(1); full = np.median(width[prow])
    Qf, pf = Qp.copy(), pole.copy()
    ok = np.nonzero(width >= 0.6 * full)[0]
    for y in range(ok[0], ok[-1] + 1):       # (la part derrière la main : la coupe de la perche au-dessus d'elle)
        if width[y] < 0.6 * full:
            src = next(yy for yy in range(y, ok[0] - 1, -1) if width[yy] >= 0.6 * full)
            pf[y, p0:p1] = pole[src, p0:p1]; Qf[y, p0:p1] = Qp[src, p0:p1]
    rail = VY - 0.2065 * (POLE_X - VX) + 1   # (la tringle, à sa colonne)
    _, _, P = prepare('T', (Qp, ap, None), fp, s_door, row(0, DOOR_Z))
    X_pole = (xs_pole.mean() + 0.5 - chest(ap)) * P['kb']                    # (la perche, du milieu de son buste, dans la scène)
    door_x = POLE_X - round(X_pole)                                          # (la colonne de son milieu)
    thin = (p0, p1, xs_pole.mean() + 0.5, POLE_W)
    fr, fm, fT, fL, fh = render(Qp, np.where(grow(pole) & ~hand[:, None], 0, ap), P, thin)   # (la figure sans sa perche, la main gardée)
    pr, pm, pT, pL, _ = render(Qf, pf.astype(float), P, thin)                # (la perche entière, au sol)
    need = pT + np.nonzero(pm.any(1))[0][0] - rail                           # (de combien la monter, en pixels de la scène)
    for up in POLE_UP:
        D = int(round(up * need)); T0 = min(fT, pT - D); L0 = min(fL, pL)
        Hc = max(fT + fm.shape[0], pT - D + pm.shape[0]) - T0; Wc = max(fL + fm.shape[1], pL + pm.shape[1]) - L0
        rgb = np.zeros((Hc, Wc, 3)); m = np.zeros((Hc, Wc), bool); hd = np.zeros((Hc, Wc), bool)
        for c_, m_, t_, l_ in ((pr, pm, pT - D, pL), (fr, fm, fT, fL)):   # (la perche derrière la main)
            sl = (slice(t_ - T0, t_ - T0 + m_.shape[0]), slice(l_ - L0, l_ - L0 + m_.shape[1]))
            rgb[sl][m_] = c_[m_]; m[sl] |= m_; hd[sl] &= ~m_
        hd[fT - T0:fT - T0 + fh.shape[0], fL - L0:fL - L0 + fh.shape[1]] |= fh
        store('T', 'D', 'dpole', D, rgb, m, T0, L0, hd, P, row(0, DOOR_Z))
    for name in ('seat', 'chop', 'sip', 'done', 'turn', 'rise', 'stand', 'jacket'):
        for cq, f in cuts['R', name]: put('R', 'S', name, None, cq, f, s_s, row(0, Z_S))
    Xe = R.X_F + WALK_END[1]; Ze = F * Xe / (WALK_END[0] - VX)
    H0, H1 = int(np.floor(H_R * F / Z_S)), int(np.ceil(H_R * F / Ze)) + 1
    for H in range(H0, H1 + 1):
        for cq, f in cuts['R', 'walk']: put('R', 'W', 'walk', H, cq, f, H / H_R, 0.0, int_y=True)
    Hf = int(round(H_R * F / Ze))            # (à la porte : la taille qu'il y a en marchant)
    for cq, f in cuts['R', 'fix']: put('R', 'W', 'fix', None, cq, f, Hf / H_R, 0.0, int_y=True)

    A = Atlas(1024)
    cells = {'T': {}, 'R': {}}; QUAL.clear()
    for who in ('T', 'R'):
        graded = [(p, gr, k, grade(255 * (np.clip(rgb, 0, 255) / 255) ** LIFT[who], m), m, ox, oy, hd, hy) for p, gr, k, rgb, m, ox, oy, hd, hy in raw[who]]
        allc = np.concatenate([c[m] for _, _, _, c, m, *_ in graded])
        fam = palette(np.clip(allc, 0, 255), FAMILIES); Lf = R.lab(fam)[:, 0]; famB = cap_values(fam)
        for i, (p, gr, k, rgb, m, ox, oy, hd, hy) in enumerate(graded):
            idx = np.where(m, R.nearest(np.clip(rgb.reshape(-1, 3), 0, 255), fam).reshape(m.shape), -1)
            rgba = np.zeros(rgb.shape[:2] + (4,), np.uint8); rgba[..., 3] = m * 255; rim = None
            if style == 'couleur':           # (les familles ; pas de trait au bord ; les traits du visage selon la tête ; peu de pixels
                idx = no_outline(idx, m, Lf, LIGHT[p])   # seuls ; le grain)
                idx, keep = face_detail(idx, m, hd, hy, fam)
                idx = unspeckle(idx, m, keep)
                o = np.random.default_rng(1000 * (who == 'R') + i).integers(-GRAIN_B, GRAIN_B + 1, m.shape)
                rgba[..., :3] = np.clip(np.round(famB[np.maximum(idx, 0)] + o[..., None]), 0, 255)
                QUAL.append((who, p, gr, k, isolated(idx, m, keep).sum() / m.sum()))
            else:                            # (l'ombre : trois tons sombres selon la clarté de la planche réduite ; la tête d'un seul ; pas de
                tl = TONE_L[who]             # trait au bord)
                tn = np.where(m, np.where(hd, 1, (Lf[np.maximum(idx, 0)] >= tl[0]).astype(int) + (Lf[np.maximum(idx, 0)] >= tl[1]).astype(int)), -1)
                tn = unspeckle(no_outline(tn, m, np.array([0.0, 50.0, 100.0]), LIGHT[p]), m, np.zeros_like(m))
                rgba[..., :3] = np.array(TONES['far' if p == 'T' else 'near'], np.uint8)[np.maximum(tn, 0)]
                QUAL.append((who, p, gr, k, isolated(tn, m, np.zeros_like(m)).sum() / m.sum()))
                if style == 'liseré':        # (le liseré : la couleur du bord, éclaircie, prise dans les couleurs claires du personnage)
                    e = rim_of(m, LIGHT[p]); rim = np.zeros_like(rgba)
                    if e.any():
                        lab_ = R.lab(np.clip(fam[idx[e]], 0, 255)); lab_[:, 0] = np.clip(lab_[:, 0] + 30, *RIM_L)
                        Lp = R.lab(famB)[:, 0]; light = famB[(Lp >= RIM_L[0] - 4) & (Lp <= RIM_L[1] + 2)]
                        rim[e, :3] = np.round(light[R.nearest(lab2rgb(lab_) * np.array(RIM_WARM), light)]); rim[e, 3] = 255
            box = A.add(rgba, rim)
            cells[who].setdefault(gr, []).append((k, box + [int(ox), int(oy)]))
    NC, N_Y, N_CX = naruto_cells(); NA = [A.add(c) for c in NC]
    # ce qui est devant Teuchi (la lanterne, les objets et l'arête du comptoir, les tabourets) : rien de lui n'y passe
    src = np.asarray(Image.open(R.SRC).convert('RGB')).astype(float)
    pix, hem = R.glass_pixels()
    col_, sid = R.render(src, pix)
    surf = R.reduce(col_, sid)[2]
    zx0, zy0, zx1, zy1 = R.ZONE
    occ = np.zeros((zy1 - zy0, zx1 - zx0, 4), np.uint8)
    for (x, y), k in zip(pix, surf):
        if k not in (1, 10): occ[y - zy0, x - zx0] = (0, 0, 0, 255)
    OC = A.add(occ)
    X_POT = R.col_X(R.POT[1], R.Z_E)
    places = {'counter': PLACES['counter'], 'pots': round(col(X_POT + PLACES['pots'], Z_T), 1), 'shelf': round(col(PLACES['shelf'], Z_T), 1)}
    wisps = []
    for kind, (u0, v0, u1, v1), xc in R.OBJETS:
        if kind == 'bol':
            Zo = R.Z_C + R.OBJ_Z; hb = R.CTR_H + (v1 - v0) / R.K_OBJ
            wisps.append([xc, int(round(row(hb, Zo))), round(0.35 * F / Zo, 1), round(0.06 * F / Zo, 1)])
    wisps.append([R.POT[1], int(round(row(R.BACK_H + (R.V_REF - 515) / R.K_WALL, R.Z_E - 0.35))), round(0.5 * F / R.Z_E, 1), round(0.1 * F / R.Z_E, 1)])
    Xs = R.col_X(R.STOOLS[0], Z_STOOL); Xn = R.col_X(R.STOOLS[2], Z_STOOL)
    img, rim_dy = A.image()
    look = {'kind': style} if style == 'couleur' else dict(kind=style, **SHADE, rim=rim_dy)
    # chaque case : [sx, sy, w, h, ox, oy] (ox, oy : où tombe dans la case le milieu du buste, au haut de la tête ou au sol) ;
    # les rangées où les poser : la tête à sa taille, les pieds au sol, à leur profondeur
    lst = lambda who, g: [b for _, b in cells[who][g]]
    IRF = {'T': {g: lst('T', g) for g in ('idle', 'calm', 'nod', 'smile', 'stir', 'lift', 'serve', 'shelf', 'walk')},
           'Ty': {'head': round(row(H_T, Z_T), 2), 'feet': round(row(0, Z_T), 2)}, 'Tz': round(Z_T, 2), 'at': places,
           'D': {g: lst('T', g) for g in ('dwalk', 'dfront', 'dbrow', 'dpole')},
           'Dz': [door_x, DOOR_Z, round(row(0, DOOR_Z), 2)],
           'S': {g: lst('R', g) for g in ('seat', 'chop', 'sip', 'done', 'turn', 'rise', 'jacket', 'stand')},
           'Sx': round(col(Xs, Z_S), 1), 'Sy': round(row(0, Z_S), 2),
           'W': {'h0': H0, 'cells': [[b for k, b in cells['R']['walk'] if k == H] for H in range(H0, H1 + 1)], 'fix': lst('R', 'fix'),
                 'top': H_R, 'from': [round(Xs, 3), round(Z_S, 2)], 'to': [round(Xe, 3), round(Ze, 2)]},
           'N': {'cells': NA, 'x': round(col(Xn, Z_S), 1), 'y': N_Y, 'cx': N_CX},
           'O': OC + [zx0, zy0], 'G': glass_rows(hem), 'wisps': wisps, 'look': look}
    print('style %s | Teuchi Z %.2f (%.1f px/m), à la porte Z %.2f (%.1f px/m, colonne %d, sa perche à %d) | le client assis Z %.2f '
          '(%.1f px/m), en marche de Z %.2f à %.2f (%d à %d px) | %d cases, atlas %d x %d' % (style, Z_T, s_t, DOOR_Z, s_door,
          door_x, POLE_X, Z_S, s_s, Z_S, Ze, H0, H1, len(A.cells), img.shape[1], img.shape[0]))
    if prev:
        bg = np.full(img.shape[:2] + (3,), (90, 40, 30), float); al = img[..., 3:] / 255
        bg = bg * (1 - al) + img[..., :3] * al
        Image.fromarray(bg.astype(np.uint8)).save(os.path.join(prev, 'atlas_x1.png'))
        json.dump(IRF, open(os.path.join(prev, 'irf.json'), 'w'))
        return IRF, img
    Image.fromarray(img, 'RGBA').save(I.A(OUT), 'WEBP', lossless=True, quality=100, method=6, exact=True)
    js = open(JS, encoding='utf-8').read()
    line = 'const IRF = ' + json.dumps(IRF, separators=(',', ':')) + ';'
    js2, n = re.subn(r'const IRF = \{.*?\};', lambda m: line, js, count=1)
    assert n == 1, 'la ligne IRF manque dans assets/street.js'
    if js2 != js: open(JS, 'w', encoding='utf-8').write(js2)


def lab2rgb(L):
    """Lab (D65) vers RGB 0..255"""
    L = np.asarray(L, float); fy = (L[..., 0] + 16) / 116; fx = fy + L[..., 1] / 500; fz = fy - L[..., 2] / 200
    f = np.stack([fx, fy, fz], -1); xyz = np.where(f > 0.206897, f ** 3, (f - 16 / 116) / 7.787) * np.array([0.95047, 1.0, 1.08883])
    M = np.linalg.inv(np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]]))
    c = np.clip(xyz @ M.T, 0, 1)
    return 255 * np.where(c > 0.0031308, 1.055 * c ** (1 / 2.4) - 0.055, 12.92 * c)


if __name__ == '__main__':
    main()
