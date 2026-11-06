#!/usr/bin/env python3
"""Le dagashi-ya : son obaa-chan, assise derrière son comptoir dans la maquette de tools/dagashi_interior.py, à sa vraie taille,
découpée dans les deux planches du propriétaire.

    python3 tools/dagashi_obaachan.py                  (après tools/dagashi_interior.py ; réécrit assets/dagashi_obaachan.webp
                                                         et, dans assets/street.js, la ligne DGO : on peut le relancer, il écrit
                                                         la même chose)
    python3 tools/dagashi_obaachan.py --preview dossier (des aperçus seulement : l'atlas x4 et en numpy, la ligne DGO en json)

Les planches (SHEETS, tools/src/planches/, chacune en deux versions sur fond blanc ; la v1 des deux retenue) : le chignon gris et
son épingle à boule rouge, les lunettes rondes, le gilet de laine rouge sombre à torsades, le kimono bleu nuit à fleurs de
cerisier, le tablier beige noué dans le dos, les tabi blancs et les zori. obaa_1_assise : derrière un comptoir bas, à mi-corps,
au repos (s0), souriante les yeux fermés (s1), l'éventail (s2), assoupie la joue dans la main (s3), le boulier (a0, a1), le
bonbon tendu (c0), le rire, les mains jointes (l0). obaa_2_debout : de dos, debout (b0), le bras levé vers l'étagère (r0), sa
longue baguette à la main (k0) ; la marche de profil, voûtée, les mains dans le dos (w0..w5). La v1 plutôt que la v2 : debout,
ses trois vues de dos de la même taille (la v2 : 2,7 % plus petite le bras levé), une vraie marche à deux pas (le pied qui
quitte le sol derrière, passe, se tend devant et se pose ; la v2 traîne le même pied derrière trois images de suite, ses tabi
gris puis blancs), l'épingle du même côté qu'assise (à sa gauche ; dans la v2 de dos, à sa droite) ; assise, un visage plus
net (de grands yeux, moins de rides qui deviennent une bouillie à cette taille), les tailles d'une image à l'autre aussi
régulières que dans la v2. FRAMES repère chaque image par un point de sa planche ; WALK : l'ordre de la marche (les images 5 et 6
de la planche échangées : le pied d'appui ne recule jamais ainsi).

- Découpe : la figure est ce qui s'écarte du blanc (les tabi, le papier de l'éventail en sont : WHITE), d'un seul morceau avec
  ce qu'elle tient ; un blanc pur enfermé (entre deux jambes) est du fond, un reflet enfermé (moins de HOLE px) reste à elle ;
  derrière le comptoir, tout ce qui est sous son haut (sa première rangée qui couvre toute la largeur de la figure) ôté : la
  maquette a son propre comptoir, qui la cache.
- Sa vraie taille : 1,45 m chignon compris (H_REAL), à SCALE_B = 1,19 mètre de la maquette pour un vrai (l'œil de la maquette à
  1,5 m, celui de la peinture à 1,26 m) : 1,73 m de maquette. Les planches la dessinent à 5,2 têtes (du haut du crâne à la
  nuque de dos, au menton de face et de profil : HEAD, mesurées à l'œil sur s0, b0, w0) ; chaque image est redressée à HEADS =
  6,5 têtes : la tête seule ramenée (de 0,77, ce qu'il faut à b0) autour de la ligne du cou (sur sa largeur, et en douceur vers
  les épaules et ce qui la touche : WARP ; la baguette, le bras levé, l'éventail restent à la taille du corps), le corps tel quel. Debout, du haut du
  chignon à la semelle, la vue de dos b0 fait sa taille ; derrière le comptoir, les images sont dessinées plus grandes (la
  largeur de ses cheveux posée sur celle de la vue de dos) et ramenées à la même échelle. Dans la maquette elle est à Z_O =
  26,45 m (52,9 px par mètre de maquette : 91 px debout, la tête 14 px) ; assise, le haut du comptoir la coupe sous les avant-
  bras (on voit 36 px d'elle, sa tête 14 px du crâne au menton, 16 avec le chignon : le haut de sa tête à 1,42 m de maquette,
  sur une chaise ; le comptoir n'a que 0,75 m) ; debout sur le plancher surélevé, sa semelle à 0,35 m (rangée 676), le haut de
  sa tête à 2,08 m, 27 px plus haut qu'assise.
- Réduction : chaque pixel de la scène est le bloc de la planche qu'il couvre ; plein si la figure en couvre au moins la moitié,
  vide sinon (jamais à demi) ; sa couleur, la moyenne de ses pixels intérieurs les plus proches de leur médiane (un bord ne mêle
  pas deux matières). Pas de trait sombre repris de la planche (ni contour) : la réduction lui laisse un visage de peau unie.
- Lumière et grain : allumée, la lumière de la boutique (sa lampe à incandescence, plus chaude que le jour des planches : LAMP ;
  puis l'étalonnage de la maquette, celui de la pièce) ; ses clairs ramenés sous la pièce
  autour d'elle + 15 % (P95 : le p95 de la clarté de la pièce allumée là où elle passe) ; puis, toutes ses images ensemble
  (tools/regrain.py : ses fonctions), ses 24 familles de tons (PALETTE : celles que regrain tirait de ses images, figées, pour
  que ses visages n'en changent aucune), chaque pixel à la sienne contre ses quatre voisins (peu de pixels seuls), un grain fin
  baké de 1 à 3 niveaux (Bayer 4 x 4, ancré à elle). Éteinte (la coupure de courant, boutique ouverte) : chaque famille au
  sombre de la pièce éteinte selon sa clarté, à sa palette, le même grain plus léger.
- Ses visages, dessinés à la main (tools/visages.py ; à 14 px de tête, chercher ses traits sur la planche et les poser au pixel
  qu'ils couvrent faisait un masque, une moustache, un nez seul au milieu) : par pose un petit gabarit en lettres (TEMPLATES : la
  forme | les marques), posé sur la boîte de son visage (face_box : sa peau entre le haut de sa tête et son menton), chaque
  lettre à l'une de ses familles (ROLES), sans grain, la forme sur sa peau seulement (un cheveu reste un cheveu). La lampe en
  haut à gauche : l'ombre sur le côté droit du visage, sous la frange et sur les tempes, sous le menton là où il rencontre le
  col. Les yeux d'un pixel, sur la rangée du milieu de la tête plus une (un vieux visage), trois pixels de peau entre eux,
  symétriques ; fermés, un brun moyen ; de trois quarts (le bonbon), poussés vers où elle se tourne. Ses lunettes jamais en
  bandeau : un reflet clair en haut de chaque verre, de son côté extérieur (et, en moyen, un pixel de son bord en bas). La
  bouche deux rangées sous les yeux : rien au repos en sobre, un pixel rose en moyen, le rouge sombre pour l'« o » de
  l'éventail, le bonbon et le rire (celui-ci dès sobre). Trois variantes (FACE, ou --face) : sobre (la forme, les yeux, l'ombre
  des cheveux, les reflets des verres ; une bouche pour le rire seulement), moyen (la bouche, le bord des verres), detail (l'ombre
  du nez, le rose des joues, les courbes des yeux fermés). Le même visage dessiné deux fois (SAME_FACE : le repos et le sourire,
  le boulier) a la même forme. De profil, en marchant : l'œil juste derrière le verre que la planche dessine, à la même rangée
  de la rue dans les six images, le reflet sur le verre devant lui, la branche des lunettes derrière (moyen).
- La marche : d'une image à la suivante le corps avance de dx pixels entiers, ceux qui gardent le pied posé sur son pixel (les
  pointes des semelles au sol de l'une sur celles de l'autre, jamais en arrière : 34 px les deux pas) ; chaque image dure le temps de son
  pas à SPEED (0,5 m/s, une vieille dame voûtée : 1,1 s les deux pas ; chaque image entre 0,1 et 0,3 s : TF) : le corps avance
  d'un pas régulier, le pied d'appui ne glisse pas.
- La place : assise, chaque image posée par le comptoir que la planche dessine sous elle (le milieu du buste de SEAT_REF à X_SEAT :
  le visage ne saute pas d'une pose à l'autre), son ancre sur la rangée du haut du comptoir derrière elle ; debout, sa
  semelle sur le plancher surélevé ; devant l'étagère, vue par la vitre de la porte de gauche, au plus près de SHELF_AT : de
  REST (les pieds joints) à REST, par les mêmes images à l'aller et au retour (elle revient juste à sa place). Ce qui est devant
  elle dans la maquette (le comptoir, le poteau, le montant et le cadre de la porte, la traverse et le panneau de bois sous la
  vitre) la cache : V, le masque de la devanture à sa profondeur (alpha : ce qu'on voit d'elle, la majorité des rayons du pixel
  passant derrière elle ; rouge : la vitre ; vert : le reflet de la vitre, x 40). Il ne dépend que de sa profondeur : plus
  grande, elle reste cachée là où il faut.

assets/dagashi_obaachan.webp : une rangée par état (allumée, éteinte), ses images côte à côte, chacune sa boîte et son ancre
(le milieu du buste ; assise, la rangée du haut du comptoir, debout, la semelle), s2b (l'éventail qui bat : s2, l'éventail
décalé d'un pixel, ce qu'il découvre repris de s0) ; le masque V à leur droite ; la ligne DGO de assets/street.js dit où est
chacune et où la poser. Il faut git, Pillow, numpy, scipy.
"""
import json
import os
import re
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as nd

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import interieur as I
import dagashi_interior as D
import regrain as RG
import visages as VI

ROOT = D.ROOT
SHEETS = {'assise': os.path.join(ROOT, 'tools', 'src', 'planches', 'obaa_1_assise_v1.png'),
          'debout': os.path.join(ROOT, 'tools', 'src', 'planches', 'obaa_2_debout_v1.png')}
OUT = 'dagashi_obaachan.webp'
JS = os.path.join(ROOT, 'assets', 'street.js')
H_REAL, SCALE_B = 1.45, 1.19         # m, debout, du haut du chignon à la semelle ; mètres de la maquette pour un vrai
HEADS = 6.5                          # (sa taille en têtes, une fois la tête redressée)
Z_O = 26.45                          # sa profondeur (m) : entre le comptoir et le mur du bout
X_SEAT = 204                         # le milieu de son buste, assise (dans l'ouverture, entre le montant de la porte et le poteau)
SHELF_AT = 170                       # (devant l'étagère, vue par la vitre, sa baguette et sa main levée dans l'ouverture : à peu près là)
FRAMES = {                           # chaque image : sa planche, un point sur elle (x, y), sa sorte (derrière le comptoir, de dos, de
                                     # profil) ; sa boîte est celle de la figure qui passe par ce point (une autre planche : ces points)
    's0': ('assise', (192, 300), 'seat'), 's1': ('assise', (576, 300), 'seat'), 's2': ('assise', (960, 300), 'seat'),
    's3': ('assise', (1344, 320), 'seat'), 'a0': ('assise', (192, 810), 'seat'), 'a1': ('assise', (576, 810), 'seat'),
    'c0': ('assise', (960, 810), 'seat'), 'l0': ('assise', (1344, 810), 'seat'),
    'b0': ('debout', (400, 300), 'back'), 'r0': ('debout', (757, 300), 'back'), 'k0': ('debout', (1085, 300), 'back'),
    'w0': ('debout', (130, 800), 'side'), 'w1': ('debout', (385, 800), 'side'), 'w2': ('debout', (632, 800), 'side'),
    'w3': ('debout', (878, 800), 'side'), 'w4': ('debout', (1136, 800), 'side'), 'w5': ('debout', (1385, 800), 'side')}
WALK = ('w0', 'w1', 'w2', 'w3', 'w5', 'w4')   # (l'ordre de la marche : pieds joints, le pied de derrière qui se lève, qui se tend
                                     # devant, posé (grand écart), l'autre qui se lève derrière, qui passe ; pieds joints)
REST = ('w0',)                       # (les images aux deux pieds posés côte à côte : elle s'y lève, s'y arrête, s'y rassied)
HEAD = {'seat': 182, 'back': 80, 'side': 81}   # la tête dessinée (px de la planche) : du haut du chignon au menton (de face), du
                                     # haut du crâne à la nuque (de dos), au menton (de profil)
WARP = (0.6, 0.3)                    # (autour de la tête : la marge où sa taille rejoint celle du corps, en largeurs de demi-tête ;
                                     # sous la ligne du cou, en hauteurs de tête)
WHITE, HOLE = 244, 40                # (la figure : un canal sous tant, ou une teinte ; un blanc enfermé de moins de tant de px)
COVER = 0.5
FACE = 'moyen'                       # (ses visages : sobre | moyen | detail, tools/visages.py ; les gabarits : TEMPLATES)
ROLES = dict(lit='b7855d', mid='b7855d', shade='a17854', deep='8c6346', hair='65574a', eye='3c2518', shut='6d422c',
             glint='c8b292', rim='7d553e', mouth='a46c57', open='5b1f1a', laugh='5b1f1a', nose='a17854', cheek='a46c57')
                                     # (chaque rôle des gabarits : sa famille (PALETTE). Sa peau, une seule (la lampe la tient
                                     # sous sa clarté, il n'y en a pas de plus claire), son ombre, l'ombre profonde ; l'œil, le brun
                                     # le plus sombre de ses cheveux et de ses yeux (pas le presque noir), fermé un brun moyen ; le
                                     # reflet des verres, le plus clair ; leur bord, un brun moyen ; la bouche et les joues, le rose
                                     # de sa peau ; ouverte, le rouge sombre)
SAME_FACE = (('s0', 's1'), ('a0', 'a1'))   # (le même visage dessiné deux fois : la même forme, d'autres marques)
TEMPLATES = {                        # (ses visages, tools/visages.py : par pose, la forme | les marques. La lampe est en haut à
                                     # gauche : l'ombre à droite du visage, sous la frange, sous le menton. Les yeux à la rangée du
                                     # milieu de la tête, un de plus pour un vieux visage ; la bouche deux rangées sous eux)
    # de face, au repos : les yeux ouverts, le reflet en haut et le bord en bas de chaque verre, de leur côté extérieur
    's0': ('br', """
        ....SSS.... | ...........
        ..SSSSSS... | ...........
        .SMMMMMMS.. | ...........
        .MMMMMMMS.. | ...........
        .MMMMMMMMS. | ..g.....g..
        .MMMMMMMMS. | ...E...E...
        .MMMMMMMMS. | ..r...n.r..
        .MMMMMMMSS. | .c...m...c.
        .MMMMMMMSS. | ...........
        .MMMMMMMSS. | ...........
        ..MMMMMSS.. | ...........
        ...DDDDD... | ...........
    """),
    # le sourire, les yeux fermés (detail : leurs courbes, sous le bord des verres), la bouche de deux pixels
    's1': ('br', """
        ....SSS.... | ...........
        ..SSSSSS... | ...........
        .SMMMMMMS.. | ...........
        .MMMMMMMS.. | ...........
        .MMMMMMMMS. | ..g.....g..
        .MMMMMMMMS. | ...e...e...
        .MMMMMMMMS. | ..q...n.q..
        .MMMMMMMSS. | .c..mm...c.
        .MMMMMMMSS. | ...........
        .MMMMMMMSS. | ...........
        ..MMMMMSS.. | ...........
        ...DDDDD... | ...........
    """),
    # l'éventail : le visage de s0 (le front plus haut d'une rangée), la bouche ouverte en « o » ; l'éventail laissé
    's2': ('br', """
        ....SSS.... | ...........
        ..SSSSSS... | ...........
        .SMMMMMMS.. | ...........
        .MMMMMMMS.. | ...........
        .MMMMMMMMS. | ..g.....g..
        .MMMMMMMMS. | ...E...E...
        .MMMMMMMMS. | ..r...n.r..
        .MMMMMMMSS. | .c...o...c.
        .MMMMMMMSS. | ...........
        .MMMMMMMSS. | ...........
        ...MMMMSS.. | ...........
        ....DDDD... | ...........
    """),
    # assoupie, la tête penchée sur sa main (à gauche) : les yeux fermés, celui de gauche une rangée plus bas, l'ombre des cheveux
    # en biais, l'ombre de la main sur la joue
    's3': ('br', """
        ....SSS.... | ...........
        ..SSMMMS... | ...........
        .SMMMMMMS.. | ...........
        .SMMMMMMMS. | ...........
        .MMMMMMMMMS | ........g..
        .MMMMMMMMMS | ..g.....ke.
        .MMMMMMMMMS | ..rek...r..
        ...SMMMMMMS | .......n.c.
        ....SMMMMMS | ......m....
        .....SMMMS. | ...........
        ......MMS.. | ...........
    """),
    # le boulier, la tête penchée : plus de cheveux, les yeux une rangée plus bas, baissés sur ses boules (les paupières : le brun
    # moyen des yeux fermés)
    'a0': ('br', """
        ...SSSS... | ..........
        ..SMMMMMS. | ..........
        ..MMMMMMS. | ..........
        .MMMMMMMMS | ..g.....g.
        .MMMMMMMMS | ...e...e..
        .MMMMMMMS. | ..r...n.r.
        .MMMMMMMS. | .c...m..c.
        .MMMMMMSS. | ..........
        ..MMMMMSS. | ..........
        ...DDDDD.. | ..........
    """),
    'a1': ('br', """
        ...SSSS... | ..........
        ..SMMMMMS. | ..........
        ..MMMMMMS. | ..........
        .MMMMMMMMS | ..g.....g.
        .MMMMMMMMS | ...e...e..
        .MMMMMMMS. | ..r...n.r.
        .MMMMMMMS. | .c...m..c.
        .MMMMMMSS. | ..........
        ..MMMMMSS. | ..........
        ...DDDDD.. | ..........
    """),
    # le bonbon tendu, de trois quarts vers la gauche (l'enfant) : les yeux poussés à gauche, l'œil lointain près du bord, la
    # joue proche à l'ombre, le sourire ouvert
    'c0': ('br', """
        ..SSSSSS.. | ..........
        .SMMMMMM.. | ..........
        .MMMMMMMS. | ..........
        .MMMMMMMMS | .g.....g..
        .MMMMMMMMS | ..E...E...
        .MMMMMMMMS | .r...n.r..
        .MMMMMMMSS | .c.oo...c.
        .MMMMMMMSS | ..........
        .MMMMMMMSS | ..........
        ..MMMMMMSS | ..........
        ...DDDDDD. | ..........
    """),
    # le rire, les mains jointes : les yeux fermés (detail : leurs courbes), la bouche ouverte, rouge sombre (dès sobre)
    'l0': ('br', """
        .....S...... | ............
        ...SSSSSS... | ............
        ..SMMMMMMS.. | ............
        ..MMMMMMMS.. | ............
        ..MMMMMMMS.. | ...g....g...
        ..MMMMMMMS.. | ....e..e....
        ..MMMMMMMS.. | ...q....q...
        ..MMMMMMMS.. | ..c..OO..c..
        ..MMMMMMSS.. | ............
        ..MMMMMMSS.. | ............
        ..MMMMMMSS.. | ............
        .....DDDD... | ............
    """),
    # de profil, en marchant (vers la droite ; retournée à l'affichage vers la gauche) : la boîte de la tête au bout du nez et à
    # la rangée du cou (la même dans la rue d'une image à l'autre) ; l'œil juste derrière le verre que la planche dessine, à la même
    # rangée de la rue dans les six images, le reflet sur le verre devant lui, la branche des lunettes derrière (moyen) ; l'ombre
    # des cheveux sur le front et la tempe ; detail : l'ombre sous le nez, la joue
    'w0': ('br', """
        ......SS.. | ..........
        ......S... | ..........
        .....S.... | ..........
        ....S..... | ..........
        .......... | ..........
        .......... | ....r.Eg..
        .......... | ..........
        .......... | .....c....
        .......... | ........n.
        .......... | ..........
        .......... | ..........
    """),
    'w1': ('br', """
        .......S.. | ..........
        ......S... | ..........
        .....S.... | ..........
        .....S.... | ..........
        ....S..... | ..........
        .......... | .....r.Eg.
        .......... | ..........
        .......... | ......c...
        .......... | ........n.
        .......... | ..........
        .......... | ..........
    """),
    'w2': ('br', """
        .......S.. | ..........
        ......S... | ..........
        ......S... | ..........
        .....S.... | ..........
        ....S..... | ..........
        .......... | .....r.Eg.
        .......... | ..........
        .......... | ......c...
        .......... | ........n.
        .......... | ..........
        .......... | ..........
    """),
    'w3': ('br', """
        .......... | ..........
        ......SS.. | ..........
        .....S.... | ..........
        .....S.... | ..........
        ....S..... | ..........
        .......... | ....r.Eg..
        .......... | ..........
        .......... | .....c....
        .......... | ..........
        .......... | ........n.
        .......... | ..........
    """),
    'w4': ('br', """
        .......S.. | ..........
        .....S.... | ..........
        .....S.... | ..........
        .....S.... | ..........
        ....S..... | ..........
        .......... | ....r.Eg..
        .......... | ..........
        .......... | .....c....
        .......... | ........n.
        .......... | ..........
        .......... | ..........
    """),
    'w5': ('br', """
        .......... | ..........
        ......SS.. | ..........
        ......S... | ..........
        ......S... | ..........
        .....S.... | ..........
        .......... | .....r.Eg.
        .......... | ..........
        .......... | ......c...
        .......... | ..........
        .......... | ........n.
        .......... | ..........
    """),
}
SEAT_REF = 's0'                      # (assise : les images posées par leur comptoir dessiné, le buste de celle-ci au milieu)
LAMP = np.array([1.0, 0.93, 0.80])   # (sous la lampe à incandescence, juste au-dessus du comptoir : plus chaude que le jour des planches)
P95 = 1.15                           # (ses clairs : sous le p95 de la pièce allumée autour d'elle, + 15 %)
PALETTE = (                          # (ses familles de tons, allumée, en OKLab : celles que tools/regrain.py tirait de ses images
                                     # avant les gabarits, figées : ses visages n'en changent plus aucune, ils y prennent leurs tons)
    (0.14208, 0.01486, 0.01330), (0.19356, 0.00694, -0.00472), (0.22214, 0.04320, 0.02187), (0.23378, 0.00844, -0.00514),   # 110704 171317 2e110e 201c20
    (0.25135, 0.00881, -0.00466), (0.26082, 0.05252, 0.02581), (0.28989, 0.02621, 0.03120), (0.30188, 0.06172, 0.03045),   # 252024 3c1715 3c2518 4b1e1b
    (0.33130, 0.07975, 0.04190), (0.35130, 0.03000, 0.03704), (0.41007, 0.01014, 0.02279), (0.42390, 0.04651, 0.05051),   # 5b1f1a 4f3423 54483c 6d422c
    (0.46742, 0.01145, 0.02590), (0.48794, 0.04076, 0.04903), (0.53577, 0.03735, 0.05649), (0.53718, 0.01248, 0.03091),   # 65574a 7d553e 8c6346 7b6b59
    (0.55194, 0.09869, 0.05390), (0.58352, 0.01653, 0.03732), (0.58603, 0.05813, 0.05162), (0.60439, 0.03291, 0.06369),   # aa564b 8c7762 a46c57 a17854
    (0.64397, 0.02134, 0.05683), (0.65595, 0.04213, 0.07057), (0.72195, 0.01345, 0.04473), (0.77345, 0.01097, 0.04898),   # a68765 b7855d b7a185 c8b292
)
GRAIN = dict(scale=0.04, cap=2.5, iters=6, tempo=2.0, tempo_de=0.02, grain_k=0.2, dither=1.6, knee=60.0)
SPEED, TF = 0.5, (0.1, 0.3)          # (sa marche, m/s ; une image dure entre tant et tant de s)
FAN = ('s2', (-1, 1))                # (l'éventail qui bat : s2 et sa copie, l'éventail décalé de tant)
LOCAL = (146, 560, 225, 676)         # (la pièce allumée autour d'elle, pour son p95 : la vitre et l'ouverture, à sa hauteur)


def components(sheet):
    """les figures d'une planche : ce qui s'écarte du blanc, en morceaux (et leur taille)"""
    m = (sheet.min(2) < WHITE) | (np.ptp(sheet, 2) > 12)
    lab, n = nd.label(m)
    return m, lab, nd.find_objects(lab), nd.sum(m, lab, range(1, n + 1))


def cut(sheet, comp, point, kind):
    """une image : ses couleurs (RGB), son masque, son ancre (x : le milieu du buste ; y : le haut du comptoir ou la semelle)"""
    m0, lab, sl, sz = comp
    x, y = point
    i = lab[y, x] - 1
    if i < 0 or sz[i] < 2000:
        big = [j for j in range(len(sz)) if sz[j] >= 2000]
        mid = lambda j: ((sl[j][1].start + sl[j][1].stop) / 2, (sl[j][0].start + sl[j][0].stop) / 2)
        i = min(big, key=lambda j: np.hypot(mid(j)[0] - x, mid(j)[1] - y))
    y0, y1, x0, x1 = sl[i][0].start, sl[i][0].stop, sl[i][1].start, sl[i][1].stop
    for j in range(len(sz)):                                               # (ce qu'elle tient de détaché : dans sa boîte)
        if j != i and sz[j] >= 40 and sl[j][1].start >= x0 - 6 and sl[j][1].stop <= x1 + 6 and sl[j][0].start >= y0 - 6 and sl[j][0].stop <= y1 + 6:
            y0, y1, x0, x1 = min(y0, sl[j][0].start), max(y1, sl[j][0].stop), min(x0, sl[j][1].start), max(x1, sl[j][1].stop)
    rgb = sheet[y0 - 4:y1 + 4, x0 - 4:x1 + 4].astype(float)
    m = m0[y0 - 4:y1 + 4, x0 - 4:x1 + 4].copy()
    holes = nd.binary_fill_holes(m) & ~m                                   # (un blanc enfermé : un reflet à elle, ou le fond entre
    hl, hn = nd.label(holes)                                               #  deux jambes)
    if hn:
        hs = nd.sum(holes, hl, range(1, hn + 1))
        m |= np.isin(hl, 1 + np.nonzero(hs < HOLE)[0])
    if kind == 'seat':                                                     # (le comptoir : en bas, les rangées qui couvrent toute la
        top = m.shape[0] - 5                                               # largeur de la figure ; la première d'entre elles)
        while top > 0 and m[top - 1, 5:-5].mean() >= 0.97: top -= 1
        cols = np.nonzero(m[top])[0]; cx = (cols.min() + cols.max() + 1) / 2   # (le milieu du comptoir dessiné)
        m[top:] = False
    l2, n2 = nd.label(m)
    if n2 > 1:                                                             # (les poussières : dehors)
        s2 = nd.sum(m, l2, range(1, n2 + 1)); m &= np.isin(l2, 1 + np.nonzero(s2 >= 0.15 * s2.max())[0])
    ys, xs = np.nonzero(m)
    ay = top if kind == 'seat' else ys.max() + 1
    return dict(rgb=rgb, m=m, ay=float(ay), org=(x0 - 4, y0 - 4), kind=kind, cx=cx if kind == 'seat' else None)


def bust(f):
    """le milieu du buste : la colonne médiane de la figure entre 45 et 75 % de sa hauteur"""
    ys, xs = np.nonzero(f['m'])
    H = f['ay'] - ys.min()
    band = (ys > ys.min() + 0.45 * H) & (ys < ys.min() + 0.75 * H)
    return float(np.median(xs[band])) + 0.5


def hair(f, hh):
    """sa tête : le haut du crâne (la première rangée d'au moins 10 px de cheveux gris), le milieu et la demi-largeur des cheveux
    sur la hauteur de sa tête"""
    c, m = f['rgb'], f['m']
    g = m & (np.abs(c[..., 0] - c[..., 1]) < 16) & (np.abs(c[..., 1] - c[..., 2]) < 18) & (c[..., 0] > 100) & (c[..., 0] < 225)
    rows = np.nonzero(g.sum(1) >= 10)[0]
    crown = int(rows.min())
    ys, xs = np.nonzero(g[crown:crown + int(0.8 * hh)])
    spans = [np.ptp(np.nonzero(r)[0]) + 1 for r in g[crown:crown + int(0.8 * hh)] if r.sum() >= 6]
    return crown, float(np.median(xs)) + 0.5, 0.5 * float(max(spans))


def reproportion(f, kh, hh):
    """la tête ramenée de kh autour de la ligne du cou (le haut du crâne + hh), sur sa largeur ; autour, sa taille rejoint en
    douceur celle du corps (WARP) ; ce qui est loin d'elle (la baguette, le bras levé) ne bouge pas. Chaque pixel de l'image
    prend celui de la planche qui tombe dessous (la planche est bien plus fine que la scène)"""
    crown, hx, R = hair(f, hh)
    neck = crown + hh
    H, W = f['m'].shape
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    dx, dy = xx + 0.5 - hx, yy + 0.5 - neck
    sm = lambda t: np.clip(t, 0, 1) ** 2 * (3 - 2 * np.clip(t, 0, 1))
    Rh, M, T = R * kh, WARP[0] * R, WARP[1] * hh
    w = np.where(dy <= 0, 1.0, sm(1 - dy / T)) * np.where(np.abs(dx) <= Rh, 1.0, sm(1 - (np.abs(dx) - Rh) / M))
    s = 1 + (1 / kh - 1) * w
    sx = np.floor(hx + dx * s).astype(int); sy = np.floor(neck + dy * s).astype(int)
    ok = (sx >= 0) & (sx < W) & (sy >= 0) & (sy < H)
    sx, sy = np.clip(sx, 0, W - 1), np.clip(sy, 0, H - 1)
    g = dict(f)
    g['rgb'] = f['rgb'][sy, sx]; g['m'] = f['m'][sy, sx] & ok
    g['head'] = dict(crown=neck - kh * hh, neck=neck, hx=hx, R=Rh)
    g['src'] = (sx, sy)                                                    # (pour chaque pixel, d'où il vient dans la planche)
    ys, _ = np.nonzero(g['m'])
    g['top'] = int(ys.min()); g['ax'] = bust(g)
    return g


def face_arg():
    """la variante des visages : FACE, ou --face sobre | moyen | detail (pour les comparer ; ce qui est écrit par défaut : FACE)"""
    return sys.argv[sys.argv.index('--face') + 1] if '--face' in sys.argv else FACE


def skin_families(base):
    """les familles de sa peau (sous la lampe : un brun-rose saturé, assez clair)"""
    r, g, b = base[:, 0], base[:, 1], base[:, 2]
    return (r > 140) & (r - b > 60) & (r - g > 20) & (g - b > 15)


def face_box(a, sk, rows):
    """la boîte de son visage dans une image : la plus grande pièce de peau (4-connexe) entre le haut de sa tête et son menton
    (rows, de l'outil : sa tête ramenée) ; x0, y0, x1, y1 compris"""
    m = a & sk
    m[:max(0, rows[0])] = False; m[rows[1] + 1:] = False
    lab, n = nd.label(m)
    if not n: return None
    big = 1 + int(np.argmax(nd.sum(m, lab, range(1, n + 1))))
    ys, xs = np.nonzero(lab == big)
    return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())


def roles(base):
    """chaque rôle d'un visage à sa famille (ROLES, de PALETTE)"""
    hexes = ['%02x%02x%02x' % tuple(int(v) for v in c) for c in base]
    return {r: hexes.index(h) for r, h in ROLES.items()}


def faces(LIT, LAB, base, heads, variant):
    """ses visages : chaque gabarit (TEMPLATES) posé sur la boîte de son visage (face_box), chaque rôle à sa famille (roles),
    sans grain (dans la rangée éteinte ensuite, chacun au sombre de sa famille). Rend les boîtes"""
    sk = skin_families(base)
    boxes = {}
    for k, rows in heads.items():
        a = LIT[k][..., 3] > 0
        boxes[k] = face_box(a, sk[LAB[k][0]], rows)
    fam = roles(base)
    print('les visages (%s) : %s' % (variant, ', '.join('%s %02x%02x%02x' % ((r,) + tuple(int(v) for v in base[i])) for r, i in fam.items())))
    for a_, b_ in SAME_FACE:
        if a_ in TEMPLATES and b_ in TEMPLATES: assert VI.forms(TEMPLATES[a_]) == VI.forms(TEMPLATES[b_]), 'le même visage, deux formes : %s, %s' % (a_, b_)
    for k, tpl in TEMPLATES.items():
        lab, g = LAB[k]
        c = LIT[k]
        off = []
        for (x, y), r in sorted(VI.pixels(tpl, boxes[k], variant).items()):
            if not (0 <= y < c.shape[0] and 0 <= x < c.shape[1] and c[y, x, 3] > 0): off.append((x, y)); continue
            if r in VI.SKIN and not sk[lab[y, x]]: continue                # (la forme sur sa peau seulement : jamais un cheveu
            lab[y, x] = fam[r]; g[y, x] = 0; c[y, x, :3] = base[fam[r]]    #  repeint de peau)
        if off: print('  %s : %d pixels du gabarit hors d\'elle %s' % (k, len(off), off))
    return boxes


def reduce(f, s, AX, AY, W, H):
    """l'image à s pixels de la scène par pixel de la planche, son ancre en (AX, AY) d'une case W x H : chaque pixel plein si la
    figure couvre la moitié de son bloc, sa couleur la moyenne de ses pixels intérieurs les plus proches de leur médiane"""
    rgb, m = f['rgb'], f['m']
    inner = nd.binary_erosion(m, iterations=1)
    iy, ix = nd.distance_transform_edt(~inner, return_distances=False, return_indices=True)
    rgb = rgb[iy, ix]                                                      # (chaque pixel : la couleur de l'intérieur le plus proche)
    h, w = m.shape
    out = np.zeros((H, W, 4))
    for i in range(H):
        ya = f['ay'] + (i - AY) / s; yb = ya + 1 / s
        for j in range(W):
            xa = f['ax'] + (j - AX) / s; xb = xa + 1 / s
            r0, r1, c0, c1 = max(int(np.floor(ya)), 0), min(int(np.ceil(yb)), h), max(int(np.floor(xa)), 0), min(int(np.ceil(xb)), w)
            if r1 <= r0 or c1 <= c0: continue
            wy = np.clip(np.minimum(np.arange(r0, r1) + 1, yb) - np.maximum(np.arange(r0, r1), ya), 0, 1)
            wx = np.clip(np.minimum(np.arange(c0, c1) + 1, xb) - np.maximum(np.arange(c0, c1), xa), 0, 1)
            wgt = wy[:, None] * wx[None, :]; mm = m[r0:r1, c0:c1]
            if (wgt * mm).sum() * s * s < COVER: continue
            ii = mm & (wgt > 0.2)
            if not ii.any(): ii = mm
            px = rgb[r0:r1, c0:c1][ii]
            med = np.median(px, 0); dd = np.abs(px - med).sum(1)
            out[i, j, :3] = px[dd <= np.median(dd)].mean(0) if len(px) > 3 else px.mean(0); out[i, j, 3] = 1
    return out


def to_cell(f, x, y, s, AX, AY):
    """un point de l'image (px de la planche) dans sa case réduite"""
    return int(np.floor(AX + (x - f['ax']) * s)), int(np.floor(AY + (y - f['ay']) * s))


def soles(f):
    """ses semelles posées (les zori, leur bois brun, à moins de 5 px du sol de l'image) : le bout de chacune (elle va vers la
    droite de la planche ; le talon d'un pied peut être caché par l'autre, jamais sa pointe), par rapport au buste (px de la
    planche)"""
    c, m = f['rgb'], f['m']
    ys, _ = np.nonzero(m); g = ys.max()
    s = m & (c[..., 0] > 110) & (c[..., 0] < 210) & (c[..., 1] > 60) & (c[..., 1] < 140) & (c[..., 2] < 100) & (c[..., 0] - c[..., 2] > 60)
    s[:int(g - 0.12 * (g - ys.min()))] = False
    lab, n = nd.label(nd.binary_closing(s, iterations=2))
    out = []
    for j in range(1, n + 1):
        yy, xx = np.nonzero(lab == j)
        if len(yy) >= 40 and g - yy.max() <= 5: out.append(float(xx.max()) + 1 - f['ax'])
    return out


def walk_steps(F, s):
    """d'une image de la marche à la suivante, de combien le corps avance (px entiers de la scène) : le moins, jamais en arrière,
    qui pose une semelle posée de l'une sur une semelle posée de l'autre (le pied d'appui ne bouge pas)"""
    out = []
    for k0, k1 in zip(WALK, WALK[1:] + WALK[:1]):
        d = [a - b for a in soles(F[k0]) for b in soles(F[k1]) if a - b >= -1]
        out.append(max(0, int(round(min(d) * s))) if d else 0)
    return out


def regrain(cells, goal):
    """toutes ses images, allumées, ensemble : les clairs sous goal (au-dessus de GRAIN['knee'], chaque couleur sur sa teinte),
    FAMILIES familles (OKLab), chaque pixel à la sienne contre ses voisins (Potts, l'image d'avant du même mouvement en mémoire),
    un grain fin baké (Bayer, ancré à l'ancre de l'image). Rend les images et, pour chacune, sa famille et son grain par pixel ;
    et les familles"""
    P = GRAIN
    keys = list(cells)
    M = {k: cells[k][0][..., 3] > 0 for k in keys}
    rgb = {k: cells[k][0][..., :3] for k in keys}
    def stat(sv):
        return max(np.percentile(RG.luma(RG.tone(rgb[k][M[k]], P['knee'], sv)), 95) for k in keys)
    s = 1.0
    if stat(1.0) > goal - 2:
        lo, hi = 0.0, 1.0
        for _ in range(30):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if stat(mid) <= goal - 2 else (lo, mid)
        s = lo
    G = {k: RG.tone(rgb[k], P['knee'], s) for k in keys}
    X = {k: RG.oklab(np.clip(G[k], 0, 255)) * RG.SW for k in keys}
    C = np.array(PALETTE) * RG.SW
    base = np.clip(np.round(RG.from_oklab(C / RG.SW)), 0, 255)
    Lb = RG.luma(base); A = RG.amp(Lb)
    seq = {}
    for k in keys:
        seq.setdefault(cells[k][3], []).append(k)
    out, labs, prev = {}, {}, {}
    for k in keys:
        c, AX, AY, mv = cells[k]
        prior = prior_ok = None
        if mv in prev:                                                     # (l'image d'avant du même mouvement, ancre sur ancre)
            pk = prev[mv]; pc, pAX, pAY, _ = cells[pk]
            pr = dict(X=X[pk], lab=labs[pk][0], M=M[pk], anchor=(pAX, pAY))
            pX, plab, pM = RG.align(pr, dict(M=M[k]), (AX, AY))
            prior, prior_ok = plab, pM & M[k] & (np.sqrt(((X[k] - pX) ** 2).sum(-1)) < P['tempo_de'])
        lab = RG.assign(X[k], M[k], C, P['scale'], P['iters'], prior, prior_ok, P['tempo'], P['cap'])
        prev[mv] = k
        h, w = M[k].shape
        d = RG.bayer(h, w, AX, AY)
        g = np.clip(np.round(P['grain_k'] * (RG.luma(G[k]) - Lb[lab]) + (d - 0.5) * P['dither']), -A[lab], A[lab])
        o = np.zeros(c.shape)
        o[..., :3] = np.clip(base[lab] + g[..., None], 0, 255); o[..., 3] = np.where(M[k], 255.0, 0.0)
        o[~M[k]] = 0
        out[k], labs[k] = o, (lab, g)
    return out, labs, base, s


def main():
    prev = sys.argv[sys.argv.index('--preview') + 1] if '--preview' in sys.argv else None
    sheets = {k: np.asarray(Image.open(p).convert('RGB')).astype(int) for k, p in sorted(SHEETS.items())}
    comps = {k: components(v) for k, v in sheets.items()}
    F0 = {k: cut(sheets[sh], comps[sh], pt, kind) for k, (sh, pt, kind) in FRAMES.items()}
    # la tête ramenée : de combien pour que b0 fasse HEADS têtes ; assise, dessinée zoom fois plus grande (ses cheveux)
    b = F0['b0']; crown_b = hair(b, HEAD['back'])[0]
    kh = (b['ay'] - crown_b - HEAD['back']) / (HEADS - 1) / HEAD['back']
    zoom = float(np.median([2 * hair(F0[k], HEAD['seat'])[2] for k in F0 if F0[k]['kind'] == 'seat'])) / (2 * hair(b, HEAD['back'])[2])
    F = {k: reproportion(f, kh, HEAD[f['kind']]) for k, f in F0.items()}
    dx_seat = bust(F0[SEAT_REF]) - F0[SEAT_REF]['cx']                     # (assise : chaque image posée par son comptoir, tel que
    for f in F.values():                                                   #  dessiné ; le milieu du buste de s0 à X_SEAT)
        if f['kind'] == 'seat': f['ax'] = f['cx'] + dx_seat
    s_scene = D.F / Z_O                                                    # (px de la scène par mètre de la maquette, à sa profondeur)
    tall = s_scene * H_REAL * SCALE_B
    s_w = tall / (F['b0']['ay'] - F['b0']['top']); s_s = s_w / zoom
    print('la tête ramenée de %.3f (b0 : %d px de la planche, %.1f têtes) ; assise dessinée %.2f fois plus grande ; debout %.1f px '
          '(%.3f px de la scène par px de la planche)' % (kh, F['b0']['ay'] - F['b0']['top'], (F['b0']['ay'] - F['b0']['top']) /
                                                           (kh * HEAD['back']), zoom, tall, s_w))
    cells, info, heads = {}, {}, {}
    for k, f in F.items():
        s = s_s if f['kind'] == 'seat' else s_w
        ys, xs = np.nonzero(f['m'])
        AX = int(np.ceil((f['ax'] - xs.min()) * s)) + 1; AY = int(np.ceil((f['ay'] - ys.min()) * s)) + 1
        W = AX + int(np.ceil((xs.max() + 1 - f['ax']) * s)) + 1; H = AY + (3 if f['kind'] == 'seat' else 0)
        c = reduce(f, s, AX, AY, W, H)
        if f['kind'] == 'seat':                                             # (sous le haut du comptoir : sa dernière rangée, trois fois,
            for r in range(AY, H): c[r] = c[AY - 1]                         # que son souffle ne découvre rien)
        hh_out = HEAD[f['kind']] * kh
        heads[k] = (to_cell(f, f['head']['hx'], f['head']['crown'], s, AX, AY)[1], to_cell(f, f['head']['hx'], f['head']['neck'], s, AX, AY)[1])
        mv = 'seat' if f['kind'] == 'seat' else f['kind']
        cells[k] = [c, AX, AY, mv]
        info[k] = dict(h=int(np.ptp(np.nonzero(c[..., 3].any(1))[0]) + 1), head=round(hh_out * s, 1))
        print('%s : %d x %d, ancre (%d, %d), %.3f px de la scène par px de la planche, la tête %.1f px' % (k, W, H, AX, AY, s, hh_out * s))
    order = list(F)                                                        # (la marche dans son ordre : la mémoire d'une image à l'autre)
    cells = {k: cells[k] for k in [k for k in order if k not in WALK] + list(WALK)}
    # l'éventail qui bat : ses pixels (les plus pâles, d'un seul tenant, pleins) dans s2, avant la lumière
    fk, (fdx, fdy) = FAN
    c = cells[fk][0]
    pale = (c[..., 3] > 0) & (c[..., :3].min(2) > 175) & (np.ptp(c[..., :3], 2) < 70)
    lab_, n_ = nd.label(nd.binary_closing(pale, iterations=2))
    fan = nd.binary_fill_holes(lab_ == 1 + int(np.argmax(nd.sum(pale, lab_, range(1, n_ + 1)))))
    fan &= c[..., 3] > 0
    print('l\'éventail : %d px' % fan.sum())

    # la lumière de la boutique ; ses clairs sous la pièce autour d'elle + 15 % ; ses familles, son grain
    R = D.cut()
    lo, hi, dpal = R['dark_ramp']
    x0, y0, x1, y1 = LOCAL
    near = (R['pix'][:, 0] >= x0) & (R['pix'][:, 0] < x1) & (R['pix'][:, 1] >= y0) & (R['pix'][:, 1] < y1) & (R['surf'] != 0)
    local = np.percentile(R['lit'][near] @ RG.LUM, [5, 50, 95])
    goal = P95 * local[2]
    lit = {}
    for k, (c, AX, AY, mv) in cells.items():
        a = c[..., 3] > 0
        L = np.zeros(c.shape); L[a, :3] = D.grade(c[a][:, :3] * LAMP); L[a, 3] = 1
        lit[k] = [L, AX, AY, mv]
    LIT, LAB, base, slope = regrain(lit, goal)
    # ses visages : les gabarits de sa variante (FACE), dans ses familles, sans grain
    faces(LIT, LAB, base, heads, face_arg())
    # éteinte : chaque famille au sombre de la pièce éteinte selon sa clarté (sa palette), le même grain, plus léger
    t = np.clip((base @ I.LUM - 25) / 175, 0, 1) ** 0.85
    dbase = dpal[D.nearest(lo + (hi - lo) * t[:, None], dpal)]
    DARK = {}
    for k in LIT:
        lab, g = LAB[k]; a = LIT[k][..., 3] > 0
        Dk = np.zeros(LIT[k].shape)
        Dk[..., :3] = np.clip(dbase[lab] + np.clip(np.round(g / 2), -1, 1)[..., None], 0, 255); Dk[..., 3] = np.where(a, 255.0, 0.0)
        Dk[~a] = 0
        DARK[k] = Dk
    # s2b : l'éventail décalé ; ce qu'il découvre repris de s0 (la même pose, sans lui)
    _, AX, AY, _ = cells[fk]; _, AX0, AY0, _ = cells['s0']
    for ST in (LIT, DARK):
        c, c0_ = ST[fk], ST['s0']
        bb = c.copy()
        for y, x in zip(*np.nonzero(fan)):
            yy, xx = y - AY + AY0, x - AX + AX0
            bb[y, x] = c0_[yy, xx] if 0 <= yy < c0_.shape[0] and 0 <= xx < c0_.shape[1] else 0
        for y, x in zip(*np.nonzero(fan)):
            if 0 <= y + fdy < bb.shape[0] and 0 <= x + fdx < bb.shape[1]: bb[y + fdy, x + fdx] = c[y, x]
        ST['s2b'] = bb
    cells['s2b'] = [None, AX, AY, 'seat']

    # la marche : de combien le corps avance d'une image à la suivante ; combien de temps chacune dure ; le trajet jusqu'à
    # l'étagère : de REST à REST, au plus près de SHELF_AT, par les mêmes images à l'aller et au retour
    Lw = len(WALK)
    step = walk_steps(F, s_w)
    v = SPEED * SCALE_B * s_scene                                           # (px de la scène par s)
    tf = np.clip(np.array(step, float) / v, *TF); tf *= sum(step) / v / tf.sum()
    i0 = WALK.index(REST[0])
    n = min(range(1, 3 * Lw + 1), key=lambda q: (WALK[(i0 + q) % Lw] not in REST, abs(X_SEAT - sum(step[(i0 + j) % Lw] for j in range(q)) - SHELF_AT) + 0.5 * q))
    shelf = X_SEAT - sum(step[(i0 + j) % Lw] for j in range(n))
    print('pas', step, '| foulée', sum(step), 'px, %.2f s (%.0f pas par minute) | durées' % (sum(step) / v, 120 * v / sum(step)),
          [round(float(x), 3) for x in tf], '| vers l\'étagère', (i0, n), '->', shelf)

    # le masque de la devanture à sa profondeur : ce qu'on voit d'elle (la majorité des rayons du pixel passent derrière elle),
    # la vitre, son reflet
    zx0, zy0, zx1, zy1 = D.ZONE
    V = np.zeros((zy1 - zy0, zx1 - zx0, 4))
    for (x, y), gl, z, sh in zip(R['pix'], R['glass'], R['Zh'], R['sheen']):
        if (z > Z_O).mean() >= 0.5: V[y - zy0, x - zx0] = (255 * gl, 40 * sh, 0, 255)

    # l'atlas : la rangée allumée, la rangée éteinte sous elle, le masque à leur droite
    keys = [k for k in FRAMES] + ['s2b']
    Wl = sum(LIT[k].shape[1] + 1 for k in keys); Hl = max(LIT[k].shape[0] for k in keys)
    A = np.zeros((max(2 * Hl + 1, V.shape[0]), Wl + V.shape[1], 4))
    x = 0; out = {}
    for k in keys:
        h, w = LIT[k].shape[:2]
        A[:h, x:x + w] = LIT[k]; A[Hl + 1:Hl + 1 + h, x:x + w] = DARK[k]
        out[k] = [x, 0, w, h, cells[k][1], cells[k][2]]; x += w + 1
    A[:V.shape[0], Wl:] = V
    y_seat = int(round(D.VY + (D.EYE - D.CTR['h']) * D.F / (D.CTR['z'] + D.CTR['d'])))   # (la rangée du haut du comptoir derrière
    y_stand = int(round(D.VY + (D.EYE - D.PLAT) * D.F / Z_O))                      # elle ; celle de ses semelles, debout)
    rise = (y_seat - out['s0'][5]) - (y_stand - out[WALK[i0]][5])     # (debout, sa tête plus haut qu'assise de tant)
    DGO = {'cells': out, 'dark': Hl + 1, 'V': [Wl, 0, V.shape[1], V.shape[0], zx0, zy0],
           'seat': [X_SEAT, y_seat], 'stand': y_stand, 'shelf': shelf, 'trip': [i0, n], 'walk': list(WALK), 'step': step,
           'tf': [round(float(x), 3) for x in tf], 'rise': rise, 'z': Z_O, 'ppm': round(D.F / Z_O, 2)}
    lv = np.concatenate([LIT[k][LIT[k][..., 3] > 0][:, :3] for k in keys]) @ RG.LUM
    print('Z_O %.2f m (%.1f px/m) : assise, le comptoir à la rangée %d ; debout, la semelle à %d (%d px plus haut) | la pièce autour '
          'd\'elle L %d/%d/%d, ses clairs sous %.0f (pente %.3f) : elle %d/%d/%d | %d familles | atlas %d x %d'
          % (Z_O, D.F / Z_O, y_seat, y_stand, rise, *local, goal, slope, *np.percentile(lv, [5, 50, 95]), len(base), A.shape[1], A.shape[0]))
    if prev:
        os.makedirs(prev, exist_ok=True)
        bg = np.full(A.shape[:2] + (3,), 128.0); al = A[..., 3:] / 255
        im = Image.fromarray(np.clip(bg * (1 - al) + A[..., :3] * al, 0, 255).astype(np.uint8))
        im.resize((A.shape[1] * 4, A.shape[0] * 4), Image.NEAREST).save(os.path.join(prev, 'atlas_x4.png'))
        json.dump(DGO, open(os.path.join(prev, 'dgo.json'), 'w'))
        json.dump(info, open(os.path.join(prev, 'info.json'), 'w'))
        np.save(os.path.join(prev, 'atlas.npy'), A)
        return
    Image.fromarray(np.clip(np.round(A), 0, 255).astype(np.uint8), 'RGBA').save(I.A(OUT), 'WEBP', lossless=True, quality=100, method=6, exact=True)
    js = open(JS, encoding='utf-8').read()
    line = '  const DGO = ' + json.dumps(DGO, separators=(',', ':')) + ';   // (tools/dagashi_obaachan.py)'
    js2, n = re.subn(r'^  const DGO = .*;   // \(tools/dagashi_obaachan\.py\)$', lambda m: line, js, count=1, flags=re.M)
    assert n == 1, 'la ligne DGO manque dans assets/street.js'
    if js2 != js: open(JS, 'w', encoding='utf-8').write(js2)


if __name__ == '__main__':
    main()
