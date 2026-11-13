#!/usr/bin/env python3
"""La façade de Kirua, au-dessus du magasin de boissons : une grande baie vitrée à la place de la petite fenêtre, sa pièce éclairée.

    python3 tools/kirua_bay_window.py      (le dernier de ce coin : après tools/kirua_house_side.py et tools/kirua_gutter.py,
                                            dont les zones couvrent la sienne ; il reprend sa zone au commit BEFORE à chaque
                                            fois, on peut donc le relancer)

La façade de la maison de Kirua (x 158..325, de son angle à la descente) n'avait qu'une petite fenêtre (x 248..273) dans
un grand mur de planches vide. À sa place, une grande baie, et derrière elle la pièce que le propriétaire a faite pour
elle (tools/src/kirua_bay_room.webp : un bureau éclairé, un voilage à gauche, deux spots au plafond, une plante et une
lampe, l'écran et sa ville violette, le dos de la chaise, une affiche du Fuji encadrée, une étagère à livres avec une
figurine et une plante), posée dans le mur dans la perspective de la
façade : son linteau et son appui sur des rayons vers le point de fuite de la façade FVP (sur des joints de planches :
KH et KS comptés en planches, D étant l'écart des planches vu de FVP), ses montants d'aplomb, ses colonnes de plus en
plus serrées vers FVP (comme un mur qui s'éloigne). Elle va de x XL, derrière l'arbre (son coin haut au-dessus du
feuillage), à x XR, loin de l'angle ; son linteau deux planches sous la gouttière, son appui neuf planches plus bas.

Une baie posée dans l'épaisseur du mur, sans trait noir autour : un chambranle (CASE : ses montants de quelques colonnes,
son haut sur deux rayons vers FVP), sa face en bois un peu plus clair que les planches (CASE_F), ses arêtes claires en
haut et à gauche, et celle du montant droit vers la baie (EDGE), son dessous sombre (UNDER_F), son ombre sur les
planches à droite du montant droit et sur la vitre à droite du montant gauche (CASE_SH). Dedans, l'ébrasement : la vitre
est en retrait de J colonnes (son plan est celui de la façade poussé dans la maison, de face comme le pignon) ; on voit
la sous-face du linteau, d'en dessous, dans l'ombre (SOFFIT_F), et le tableau du fond, vers FVP, à mi-ombre (JAMB_F,
le ton du pignon) ; le tableau proche est caché. Chaque face a son ton, tiré du bois du peintre avec son grain (WOOD :
le corps d'une de ses planches, entre ses joints, le long de son rayon pour ce qui suit la façade, en travers pour ce
qui est d'aplomb), et l'occlusion dans les angles rentrants (AO : la sous-face contre le dormant, le tableau contre le
dormant et sous la sous-face). Le dormant en retrait (FRAME, le bleu nuit du peintre : sa traverse haute, son montant
droit, son meneau et sa traverse devant le voilage, MULLIONS, TRANSOMS, en fractions de la vitre). L'ombre du linteau en
haut de la vitre, rangée par rangée (HEAD_SH ; allumée, la pièce en garde une part : HEAD_LIT). Un appui en saillie
sous la baie, plus large qu'elle : son arête claire, sa face, son dessous sombre, son ombre portée sur les planches en
deux marches (SILL_SH). Toutes ses lignes sur des rayons vers FVP ou d'aplomb, au pixel près, sans flou. Le bois prend
le couchant et les heures comme les planches ; le verre et le dormant, non.

La pièce, une petite boîte derrière l'ouverture, vue par l'œil de la rue (une perspective à un point, FVP au centre :
ce qui longe la rue court vers FVP, ce qui entre dans la maison est horizontal, ce qui est vertical d'aplomb ; la baie,
haute de WIN_M[0] et large de WIN_M[1], en donne l'échelle). Son mur du fond, au droit du tableau du fond, est de face :
l'image du propriétaire y est posée sans biais (ses horizontales horizontales, ses verticales d'aplomb), assez grande
pour couvrir toute la baie jusqu'à l'appui, jusque dans l'angle de l'appui et du tableau du fond (PPM pixels de l'image
par mètre) ; son angle avec la façade caché par le tableau (CORNER : l'étagère de l'image reste derrière lui), l'affiche
et l'écran au milieu, le bureau et ses tiroirs dans l'angle de l'appui, la lampe derrière le voilage (LAMP) ; sa
corniche contre le plafond, CEIL au-dessus du haut de la baie. Le plafond, vu d'en dessous, entre le haut de la baie
(un rayon) et celui du mur (horizontal), plus large vers le montant proche : le ton de l'image, plus sombre vers la
fenêtre (CEIL_TONES), son spot net au-dessus du cône de lumière de l'image sur le mur, sa lueur en quelques marches
(SPOTS). Pas de sol : l'appui le cache. Le voilage reste sur le plan de la vitre, dans la partie près du meneau,
devant la pièce et derrière le meneau (le voilage de l'image, pris là jadis par INNER, s'y lisait en flammes jaunes entre
les feuilles de l'arbre : il est dessiné, voir plus bas). Sa profondeur : une
ligne sombre douce au plafond contre le mur (JUNCTION), le mur plus sombre dans l'angle de la fenêtre (CORNER_AO) ;
allumée, le mur plus sombre loin de la lampe (FALL) et toute la pièce un peu plus sombre que les arêtes claires
(ROOM_DIM) ; l'ombre du linteau et du chambranle sur elle.

Sans grain mais avec ses détails (le Fuji et la pagode de l'affiche, l'écran et sa ville, l'enceinte et la pile de
livres sur le bureau, ses tiroirs, les plis du voilage, la lumière des spots) : son image adoucie d'abord à sa pleine
taille, selon ses bords (SMOOTH : un petit filtre médian là où elle a des bords, un médian plus large puis une moyenne
là où elle est lisse, ses murs et la lumière des spots en dégradés doux), puis chaque pixel de vitre pris sur ce qu'il
voit (SUB x SUB points sur le voilage, le mur ou le plafond) : la couleur de la moitié de ses points s'il y en a une,
sinon la plus proche de leur moyenne (NPAL tons de l'image, et ses touches, ACCENTS : les violets de l'écran, le blanc
de la neige, le vert de la plante, le bleu et le rouge des livres), sans tramage ; un point seul de moins de MIN_REG
pixels prend le ton qui l'entoure, ses fines lignes gardées (en diagonale aussi). Par-dessus, redessinés nets d'après
la géométrie de l'image et de sa couleur (LINES) : la corniche, le cadre de l'affiche, le bord de l'écran, le dessus du
bureau, son dessous et son caisson, les planches et les montants de l'étagère (sur le mur : horizontaux ou d'aplomb),
deux plis du voilage (le long des rayons vers FVP), le Fuji, sa neige et la pagode de l'affiche, la poignée du tiroir
(des formes) ; le spot au plafond. Allumés, le mur et le plafond n'ont pas ces tons en marches : là où l'image est lisse
(hors des lignes, de l'écran, de l'affiche, du spot ; WALL_SMOOTH), chaque pixel la couleur moyenne de ses points,
adoucie avec ses voisins, allumée comme la palette ; au bord d'un objet, le pixel qui a la couleur du mur la prend aussi.

Le voilage, dessiné (VOILE) : un rideau léger aux quelques plis d'aplomb doux, plus serrés en haut, éclairé par la pièce
derrière lui (l'image très floue au point du mur qu'il cache : plus chaud en bas, où la lampe est derrière lui), passé
vers le crème d'un tissu clair, jamais plus clair que la pièce ; éteint, un tissu clair dans le verre sombre. La fenêtre
est entrouverte : dans le vent, il est poussé dans la pièce (SWAY : vers la gauche, tenu à sa tringle, son bord libre
découvrant la pièce derrière lui) ; ses SWAY['n'] images, côte à côte dans assets/win_z7_curtain.webp (chacune le comp
dans la boîte du voilage, celle de s = 0 le comp même), que street.js (BAYC) pose dans l'image du comp sur les rafales.

Éteinte, comme elle est dans les calques : le verre sombre du peintre (celui de sa
petite fenêtre), les grandes formes de la pièce à peine lisibles dedans (leur clarté seule, les taches de moins de
MIN_OFF pixels fondues, l'écran éteint). Allumée, le sprite de la fenêtre d'habitation (le comp win_z7_up de
assets/street.js, celui de la petite fenêtre : allumée longtemps, éteinte un moment, éteinte dans la coupure de
courant, rouge la nuit rouge, la télé certains soirs) : la pièce ramenée à mi-chemin de la fenêtre éclairée de la rue
(la moyenne et l'écart de chaque canal de la lumière de la petite fenêtre, au commit BEFORE ; à mi-chemin : ses
couleurs encore à elle), l'écran (SCREEN) et les touches gardant leur teinte, l'arête de l'appui sous la vitre prise
dans la lumière de la pièce (SILL_LIT). L'arbre reste devant tout : ses feuilles (trouvées comme dans
tools/kirua_house_side.py) ne sont pas touchées, et la lumière n'est que là où elles s'ouvrent sur GLOW_MIN pixels
ensemble.

Là où la petite fenêtre était et que la baie ne couvre pas (sous l'appui), les planches du peintre, refaites comme
tools/kirua_house_side.py les refait : chaque pixel sa planche sur son rayon vers FVP, prise dans ses planches à droite
(SRC_X), un pixel différent de cette planche par colonne, en miroir, pour que le grain reste. Dans layer_city_off,
street_unlit (les mêmes, moins la lumière de la rue qui tombait là, du rapport des deux calques au commit BEFORE : celle
que la nuit rouge dessine en rouge), night_far (0, celui de la rue) et street_sun ; écrit aussi assets/win_z7_up.webp et
sa boîte dans assets/street.js, assets/win_z7_curtain.webp et sa boîte (BAYC). Ensuite : cd tools && python3
redraw_zones.py, python3 tools/bake_retouches.py (leurs zones kiosktop et dojofoot sont sous la sienne), python3
tools/build_street.py. Il faut git, Pillow, numpy.
"""
import io
import os
import re
import subprocess
import numpy as np
from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = lambda p: os.path.join(ROOT, 'assets', p)
BEFORE = '119e468'                   # (les calques avant cet outil : sa zone reprise de là à chaque fois)
OLD, TREE = '8d4ca3c^', '8d4ca3c'    # (avant le changement de l'arbre devant le dojo ; ce changement : ses feuilles)
REF = os.path.join(ROOT, 'tools', 'src', 'kirua_bay_room.webp')
ZONE = (100, 0, 340, 440)            # x0, y0, x1, y1 : où l'on cherche le feuillage
FRONT_X = (158, 326)                 # (les colonnes de la façade, reprises de BEFORE ; la descente au-delà)
FRONT_TOP = (162, 86)                # (le haut de la façade sous la gouttière : le rayon vers FVP par ce point)
FVP = (700.0, 615.0)                 # le point de fuite du peintre pour ces maisons (ses planches, le linteau et l'appui de sa
                                     # petite fenêtre, les rebords de la maison du fond y courent)
D = 0.0199                           # l'écart des planches vu de FVP (rad)
XL, XR = 215, 311                    # la baie : les colonnes des bords de son ouverture
KH, KS = 36.59, 27.78                # son linteau et son appui : leurs rayons vers FVP, en planches (sur des joints du peintre)
J = 6                                # la profondeur de l'ébrasement, en colonnes à XR
HORN = 3                             # (l'appui dépasse de l'ouverture de tant de colonnes de chaque côté)
INNER = (0, 0, 1774, 887)            # son image (x0, y0, x1, y1) posée sur le plan de la vitre, pour le voilage : son côté
                                     # gauche (le voilage) tombe dans la partie près du meneau
WIN_M = (1.6, 2.4)                   # la baie en mètres (haute, large) : l'échelle de la pièce derrière elle
CEIL = 0.15                          # le plafond de la pièce, au-dessus du haut de la baie (m)
PPM = 435                            # (pixels de son image par mètre sur le mur du fond : elle couvre la baie jusqu'à
                                     # l'appui, jusque dans l'angle du tableau du fond ; l'écran y fait 0,74 m)
CORNER = (1320, 150)                 # (x, y dans son image) : l'angle du mur du fond, de la façade et du plafond (sous la
                                     # corniche) ; l'image de face, son côté gauche au fond de la pièce : l'affiche, l'écran,
                                     # les tiroirs du bureau dans l'angle de l'appui, l'étagère derrière le tableau du fond
LAMP = 590                           # (le x de la lampe dans l'image : derrière le voilage)
SPOTS = ((1146, 0.15),)              # les spots du plafond : le x de leur cône dans l'image, leur distance au mur du fond (m)
SPOT_R, GLOW_R = 0.05, 0.38          # (le rayon d'un spot, de sa lueur au plafond, m)
CEIL_TONES = ((700, 100, 1050, 140), (700, 0, 1050, 6),     # le plafond, des boîtes de l'image : son ton contre le
              (1131, 84, 1163, 92), (1110, 93, 1180, 100))  # mur, loin de lui (vers la fenêtre, à CEIL_FADE m), le
CEIL_FADE = 1.0                                             # spot, sa lueur
JUNCTION = (0.92, 0.85, 0.92)        # la ligne sombre du plafond contre le mur (ses trois rangées)
CORNER_AO, AO_W = 0.12, 0.15         # le mur plus sombre dans l'angle de la fenêtre (sa part, sur tant de mètres)
FALL, FALL_D = 0.1, 1.3              # allumée : le mur plus sombre loin de la lampe (sa part perdue à tant de mètres)
ROOM_DIM = 0.9                       # allumée : la pièce un peu plus sombre que les arêtes claires, derrière la vitre
MULLIONS = ((118 / 716, 144 / 716),)  # (u0, u1, en travers de la vitre) : son meneau, entre le rideau et la pièce
TRANSOMS = ((234 / 344, 245 / 344, 0.0, 118 / 716),)   # (v0, v1, u0, u1) : sa traverse, devant le rideau
SMOOTH = (3, 9, 10, 7, 10, 5)        # la pièce adoucie d'abord, à sa pleine taille, selon ses bords : là où elle en a, un
                                     # filtre médian de ce côté (ses détails gardés) ; là où elle est lisse (ses murs, la
                                     # lumière des spots), un médian de ce côté puis une moyenne de ce rayon (des dégradés
                                     # doux) ; lisse : l'écart de sa clarté sous ce rayon, moindre que ce seuil, sur cette
                                     # rampe (le grain que la réduction changerait en mouchetis ôté, ses bords gardés)
NPAL = 26                            # ses couleurs (coupe médiane), plus ses touches (ACCENTS, la médiane de leurs pixels) :
ACCENTS = (('ecran', (735, 548, 1045, 712), 'violet'), ('ecran_clair', (735, 548, 1045, 712), 'violet clair'),
           ('ville', (735, 548, 1045, 712), 'violet sombre'), ('neige', (1033, 333, 1052, 347), 'tout clair'),
           ('plante', (280, 345, 560, 700), 'vert'), ('livres_bleus', (1290, 170, 1680, 880), 'bleu'),
           ('livres_rouges', (1290, 170, 1680, 880), 'rouge'))
SCREEN = (735, 548, 1045, 712)       # (x0, y0, x1, y1) : l'écran, sa lumière à lui
LINES = [('h', (320, 146, 1285, 154)),                                                # la corniche, contre le plafond
         ('cadre', (862, 228, 1177, 512, 14)), ('cadre', (727, 545, 1047, 717, 10)),  # le cadre de l'affiche, le bord de l'écran
         ('h', (448, 745, 669, 757)), ('h', (932, 745, 1287, 757)),                 # le dessus du bureau (la chaise devant)
         ('h', (932, 770, 1277, 777)), ('v', (1122, 772, 1134, 887)), ('v', (1240, 772, 1250, 887)),   # son dessous, son
         ('forme', ([(1187, 822), (1213, 822), (1213, 831), (1187, 831)], (1187, 822, 1213, 831, 50))),  # caisson, sa poignée
         ('h', (1300, 148, 1690, 160)), ('h', (1300, 287, 1690, 297)), ('h', (1300, 427, 1690, 437)),
         ('h', (1300, 577, 1690, 587)), ('h', (1300, 737, 1690, 747)),             # les planches de l'étagère
         ('v', (1276, 145, 1300, 887)), ('v', (1665, 145, 1690, 887)),             # ses montants
         ('v', (100, 0, 112, 887)), ('v', (195, 0, 207, 887)),                     # deux plis du rideau
         ('forme', ([(925, 385), (1042, 327), (1110, 375), (1110, 392), (925, 392)], (1045, 355, 1080, 372, 50))),   # le Fuji
         ('forme', ([(1018, 352), (1042, 327), (1068, 352)], (1033, 333, 1052, 347, 97))),   # sa neige
         ('forme', ([(1104, 445), (1104, 350), (1118, 334), (1132, 350), (1132, 445)], (1112, 380, 1125, 440, 50)))]   # la pagode
                                     # (dans l'image de la pièce) : redessinés nets par-dessus, chacun de la couleur de
                                     # l'image sous lui, une ligne d'un pixel au moins (sur le mur du fond, horizontale ou
                                     # d'aplomb ; sur le voilage, le long des rayons vers FVP ou d'aplomb), un cadre en quatre
                                     # lignes
SUB, MIN_REG, MIN_OFF = 4, 3, 30     # (points par pixel, de chaque côté ; un point de moins de tant de pixels, seul, prend le
                                     # ton qui l'entoure (ses fines lignes gardées) ; éteinte, une tache de moins de tant :
                                     # il n'en reste que les grandes formes)
OLDBOX = (244, 244, 281, 366)        # (la boîte de la petite fenêtre du peintre)
SRC_X = (278, 325)                   # les planches du peintre, à droite de la petite fenêtre
CASE = (3, 2, 0.3)                   # le chambranle : ses montants (colonnes, à gauche et à droite), son haut (en planches)
FRAME = (20, 20, 41)                 # le bleu nuit du dormant du peintre (sa petite fenêtre)
EDGE, SILL_LIT = (178, 82, 99), 0.35 # les arêtes claires (le clair des planches) ; allumée, la part de la pièce dans celle de
                                     # l'appui
WOOD = (33, 31, 30, 32)              # les planches du peintre d'où vient le bois du chambranle, de la sous-face, du tableau,
BODY = (0.05, 0.75)                  # de l'appui ; (leur corps, entre leurs joints, en planches)
CASE_F, UNDER_F, SILL_F = 1.12, 0.35, 1.18  # les tons : le chambranle, les dessous (du chambranle et de l'appui), l'appui
SOFFIT_F, JAMB_F = 0.42, 0.66        # la sous-face du linteau (dans l'ombre), le tableau du fond (à mi-ombre, comme le pignon)
AO = 0.72                            # l'occlusion dans les angles rentrants de l'ébrasement
HEAD_SH = (0.62, 0.62, 0.8, 0.8)     # l'ombre du linteau en haut de la vitre, rangée par rangée (éteinte)
HEAD_LIT = 0.55                      # (allumée : la part de ces ombres sur la pièce)
CASE_SH = (0.75, 0.8)                # l'ombre du chambranle : sur la vitre à sa droite, sur les planches à droite du sien
SILL_SH = (0.55, 0.8)                 # l'ombre de l'appui sur les planches, rangée par rangée
OFF_Z, OFF_K = (-2.0, 0.8), 0.14     # éteinte : la clarté de la pièce (en écarts, bornée) et sa part dans le verre
GLOW_MIN = 6                         # (sa lumière où les feuilles s'ouvrent sur tant de pixels ensemble, au moins)
UP, UP_V = 'win_z7_up', 7            # sa lumière : le comp de la petite fenêtre, sa version
CURT_V = 1                           # (la version des images du voilage, CURT)
SCR_PX = (231, 321, 268, 344)        # (x0, y0, x1, y1, dans la scène) : la face de l'écran ; son bord de deux pixels en haut,
                                     # à droite et en bas (à gauche, le meneau le cache), net et sans trou
LEAF = 45                            # (une feuille : plus sombre que ça, là où le changement de l'arbre a mis un pixel)
WALL_SMOOTH = (0.6, 1.2, 22)         # les murs et le plafond sans marches : un pixel de mur où l'image est lisse en moyenne sous
                                     # ses points (au moins tant), sa couleur la moyenne de ses points, adoucie de ce rayon (px) ;
                                     # au bord d'un objet, le pixel dont la couleur allumée est à moins de tant de celle du mur
VOILE = dict(folds=2.5, gather=0.35, warp=0.07, crest=0.94, trough=0.78, edge=0.85, cream=(1.08, 1.0, 0.86), desat=0.35,
             blur=40.0, top=300, off=(0.5, 2.0))
                                     # le voilage : ses plis d'aplomb (tant sur sa largeur, plus serrés en haut, froncés sur la
                                     # tringle, inégaux de warp), sa lumière celle de la pièce derrière lui (son image très floue,
                                     # de ce rayon, au point du mur qu'il cache, pas plus haut que top dans l'image : la lumière
                                     # du mur à mi-hauteur ; allumée) passée vers le crème d'un tissu clair (desat), tant à la
                                     # crête et au creux d'un pli (jamais plus clair que la pièce), son bord libre près du meneau
                                     # (son ourlet) un peu plus sombre ; éteint, un tissu clair un peu plus clair que la pièce
                                     # sombre (off : sa clarté, en écarts, et celle de ses plis)
SWAY = dict(amp=2.5, s=(-0.25, 1.0), n=11, v0=0.15)
                                     # le voilage dans le vent (la fenêtre entrouverte) : poussé dans la pièce, vers la gauche, de
                                     # tant de pixels au plus, tenu à la tringle (le tissu s'en écarte sur v0 de la hauteur de la
                                     # vitre : 1 - exp(-v / v0)), son bord libre découvrant la pièce derrière lui ; n images de
                                     # s0 à s1 (0 : au repos, le comp). Le haut seul se voit, l'arbre cache le bas
CURT = 'win_z7_curtain'              # (ses images, côte à côte : assets/win_z7_curtain.webp ; sa boîte dans assets/street.js)
LUM = np.array([0.299, 0.587, 0.114])


def load(p, mode='RGBA', at=None):
    data = subprocess.run(['git', 'show', f'{at}:assets/{p}'], cwd=ROOT, capture_output=True, check=True).stdout if at else open(A(p), 'rb').read()
    return np.asarray(Image.open(io.BytesIO(data)).convert(mode)).astype(float)


def save(arr, p, mode):
    Image.fromarray(np.clip(np.round(arr), 0, 255).astype(np.uint8), mode).save(A(p), 'WEBP', lossless=True, quality=100, method=6, exact=True)


def ray(k, x, g=1.0):                                                        # (la ligne à x du rayon vers FVP à k planches ;
    return FVP[1] - (FVP[0] - x) * np.tan(k * D) / g                         # g : sur le plan de la vitre)


def fray(y, x_from, x_to):                                                   # (la ligne à x_to du rayon vers FVP par (x_from, y))
    return FVP[1] + (y - FVP[1]) * (FVP[0] - x_to) / (FVP[0] - x_from)


def grow(m, n=1):
    for _ in range(n):
        g = m.copy(); g[1:] |= m[:-1]; g[:-1] |= m[1:]; g[:, 1:] |= m[:, :-1]; g[:, :-1] |= m[:, 1:]; m = g
    return m


def flood(ok, seeds):
    hit = np.zeros_like(ok); todo = list(seeds); h, w = ok.shape
    while todo:
        y, x = todo.pop()
        if 0 <= y < h and 0 <= x < w and ok[y, x] and not hit[y, x]:
            hit[y, x] = True; todo += [(y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)]
    return hit


def main():
    names = (('layer_city_off.webp', 'RGBA'), ('street_unlit.webp', 'RGBA'), ('night_far.webp', 'RGB'), ('street_sun.webp', 'RGB'))
    L = [load(n, m) for n, m in names]; B = [load(n, m, BEFORE) for n, m in names]
    for l, b in zip(L, B): l[:ZONE[3], FRONT_X[0]:FRONT_X[1]] = b[:ZONE[3], FRONT_X[0]:FRONT_X[1]]   # (la façade comme avant)
    city = B[0]; H, W = city.shape[:2]

    # le feuillage de l'arbre (les pixels sombres que son changement a mis là, joints à la masse par des suites de trois,
    # et les sombres tout près) : il reste devant tout
    x0, y0, x1, y1 = ZONE
    o, t = load('layer_city_off.webp', 'RGBA', OLD)[y0:y1, x0:x1], load('layer_city_off.webp', 'RGBA', TREE)[y0:y1, x0:x1]
    still = np.abs(city[y0:y1, x0:x1] - t).sum(2) == 0
    dark = (np.abs(o - t).sum(2) > 0) & still & (t[..., :3] @ LUM < LEAF)
    core = dark & np.roll(dark, 1, 1) & np.roll(dark, -1, 1)
    leaf = grow(flood(core, [(y1 - y0 - 1, x) for x in range(x1 - x0)])) & dark
    front = np.zeros((H, W), bool); front[y0:y1, x0:x1] = leaf | (grow(leaf, 2) & dark)

    # la petite fenêtre du peintre (son cadre et sa vitre : le bleu joint à son milieu, et ce qu'il entoure)
    wx0, wy0, wx1, wy1 = OLDBOX
    navy = np.zeros((H, W), bool)
    navy[wy0:wy1, wx0:wx1] = city[wy0:wy1, wx0:wx1, 2] >= city[wy0:wy1, wx0:wx1, 0] - 4
    old = flood(navy, [((wy0 + wy1) // 2, (wx0 + wx1) // 2)])
    box = np.zeros((H, W), bool); box[wy0:wy1, wx0:wx1] = True
    out = flood(box & ~old, [(y, x) for y in range(wy0, wy1) for x in (wx0, wx1 - 1)] + [(y, x) for x in range(wx0, wx1) for y in (wy0, wy1 - 1)])
    old = box & ~out

    def board(x, y):                                                         # (une planche éclairée de la façade, telle quelle)
        return 0 <= y < H and city[y, x, 3] == 255 and city[y, x, :3] @ LUM >= 30 and city[y, x, 0] > city[y, x, 2] \
            and not front[y, x] and not old[y, x]

    # la baie, colonne par colonne (chaque ligne sur son rayon vers FVP, arrondie au pixel ; les montants d'aplomb) :
    # 1 une arête claire du chambranle, 2 sa face, 3 son dessous, 4 la sous-face du linteau, 5 le tableau, 6 le dormant,
    # 7 la vitre, 8 l'arête de l'appui, 9 sa face, 10 son dessous, 11 une ombre portée sur les planches (MUL : l'ombre, et
    # l'occlusion dans les angles rentrants)
    G = 1 + J / (FVP[0] - XR - 0.5)                                          # (le plan de la vitre : J colonnes plus loin à XR)
    xa, xb = XL - CASE[0] + 1, XR + CASE[1] - 1                              # (le chambranle, de son bord gauche à son bord droit)
    hC = {x: int(round(ray(KH + CASE[2], x))) for x in range(xa - HORN, xb + HORN + 2)}   # (le haut du chambranle)
    hO = {x: int(round(ray(KH, x))) for x in range(xa - HORN, xb + HORN + 2)}            # (son dessous : le haut de la baie)
    sO = {x: int(round(ray(KS, x))) for x in range(xa - HORN, xb + HORN + 2)}            # (l'appui)
    hJ = hO[XR]                                                              # (l'angle du tableau et de la sous-face : de face)
    a0, a1 = 1 / (FVP[0] - (XL - 0.5)), 1 / (FVP[0] - (XR + 0.5))
    U = lambda xg: (G / (FVP[0] - xg) - a0) / (a1 - a0)                     # (où tombe une colonne en travers de la vitre)
    V = lambda xg, y: (y - ray(KH, xg, G)) / (ray(KS, xg, G) - ray(KH, xg, G))   # (et une ligne de haut en bas)
    rx0, ry0, rx1, ry1 = INNER
    uref = vref = lambda f: f                                               # (le dormant : en fractions de la vitre)
    cls = np.zeros((H, W), np.int8); MUL = np.ones((H, W, 2))              # (MUL : éteinte, allumée)
    mcols = set()
    for m0, m1 in MULLIONS:                                                  # (le meneau : les colonnes qui tombent dessus)
        cs = [x for x in range(XL + 1, XR - J) if uref(m0) <= U(x) < uref(m1)]
        mcols |= set(cs or [min(range(XL + 1, XR - J), key=lambda x: abs(U(x) - uref((m0 + m1) / 2)))])
    rail = {}
    for x in range(xa, xb + 1):
        cls[hC[x], x] = 1                                                    # (le chambranle : son arête haute claire,
        cls[hC[x] + 1:sO[x], x] = 2                                          # sa face, de haut en bas sur ses côtés)
        if x == xa: cls[hC[x]:sO[x], x] = 1                                   # (son arête gauche claire)
        if XL < x < XR:
            cls[hO[x], x] = 3                                                # (au-dessus de la baie : son dessous, sombre)
            if x > XR - J:                                                   # (le tableau du fond, sous la sous-face)
                cls[hO[x] + 1:hJ + 1, x] = 4; cls[hJ + 1:sO[x], x] = 5
                MUL[hJ + 1, x] *= AO; continue
            r = rail[x] = int(round(ray(KH, x, G)))
            cls[hO[x] + 1:r, x] = 4; MUL[r - 1, x] *= AO                     # (la sous-face, son angle avec le dormant)
            if x == XR - J or x in mcols:
                cls[r:sO[x], x] = 6; continue
            cls[r, x] = 6; cls[r + 1:sO[x], x] = 7
            for i, f in enumerate(HEAD_SH): MUL[r + 1 + i, x] *= f          # (l'ombre du linteau en haut de la vitre)
            for t0, t1, tx0, tx1 in TRANSOMS:                                 # (la traverse : les lignes qui tombent dessus)
                if uref(tx0) <= U(x) < uref(tx1):
                    ts = [y for y in range(r + 1, sO[x]) if vref(t0) <= V(x, y) < vref(t1)]
                    for y in ts or [min(range(r + 1, sO[x]), key=lambda y: abs(V(x, y) - vref((t0 + t1) / 2)))]: cls[y, x] = 6
        elif x == XR:
            cls[hO[x] + 1:sO[x], x] = 1                                      # (l'arête du chambranle droit, vers la baie)
    MUL[:, XR - J + 1] *= np.where(cls[:, XR - J + 1] == 5, AO, 1)[:, None]  # (le tableau contre le dormant)
    MUL[:, XL + 1] *= np.where(cls[:, XL + 1] == 7, CASE_SH[0], 1)[:, None]  # (l'ombre du chambranle gauche sur la vitre)
    MUL[..., 1] = 1 - HEAD_LIT * (1 - MUL[..., 0])                           # (allumée, la pièce : ces ombres à moitié)
    for x in range(xa - HORN, xb + HORN + 1):                                # (l'appui : son arête, sa face, son dessous, son
        cls[sO[x], x] = 8; cls[sO[x] + 1:sO[x] + 3, x] = 9; cls[sO[x] + 3, x] = 10   # ombre sur les planches)
        for i, f in enumerate(SILL_SH): cls[sO[x] + 4 + i, x] = 11; MUL[sO[x] + 4 + i, x] = f
    for y in range(hC[xb] + 1, sO[xb + 1]):                                  # (l'ombre du chambranle droit sur les planches)
        if cls[y, xb + 1] == 0: cls[y, xb + 1] = 11; MUL[y, xb + 1] = CASE_SH[1]

    # les planches là où la petite fenêtre était et n'est plus : chaque pixel la planche du peintre sur son rayon vers FVP
    # (ou, si ce rayon n'en trouve pas, la planche un nombre entier de planches plus loin), un pixel différent de cette
    # planche par colonne, en miroir depuis le bord de ses planches
    src = [b.copy() for b in B]
    th = lambda x, y: np.arctan2(y - FVP[1], x - FVP[0])
    top = {x: int(np.ceil(fray(FRONT_TOP[1], FRONT_TOP[0], x))) for x in range(*FRONT_X)}
    good = np.zeros((H, W), bool)
    for x in range(*SRC_X):
        for y in range(top[x] + 3, 430):
            good[y, x] = board(x, y)
    # la lumière de la rue sur le mur (ce que la coupure de courant lui ôte : le rapport des deux calques), là où la petite
    # fenêtre était, reprise en douceur des planches autour : planches refaites et baie la gardent à leur place
    cut = np.clip((B[1][..., :3] + 0.5) / (B[0][..., :3] + 0.5), 0, 1)
    bx0, by0, bx1, by1 = OLDBOX; c_ = cut[by0 - 1:by1 + 1, bx0 - 1:bx1 + 1]; h_ = old[by0 - 1:by1 + 1, bx0 - 1:bx1 + 1]
    c_[h_] = c_[~h_].mean(0)
    for _ in range(400):
        c_[h_] = ((np.roll(c_, 1, 0) + np.roll(c_, -1, 0) + np.roll(c_, 1, 1) + np.roll(c_, -1, 1)) / 4)[h_]

    def rebuild(x, y):
        for k in [0] + [s * j for j in range(1, 12) for s in (1, -1)]:
            a = th(x, y) - k * D
            pts = [(int(round(FVP[1] + np.tan(a) * (xs - FVP[0]))), xs) for xs in range(*SRC_X)]
            pts = [p for p in pts if 0 <= p[0] < H and good[p]]
            if pts:
                n = len(pts); i = (SRC_X[0] - 1 - x) % (2 * n)
                return pts[i if i < n else 2 * n - 1 - i]
    n_b = 0
    for y, x in zip(*np.where(old & ((cls == 0) | (cls == 11)) & ~front)):
        ys, xs = rebuild(x, y)
        L[0][y, x] = src[0][ys, xs]; L[1][y, x] = [*(src[0][ys, xs, :3] * cut[y, x]), 255]
        L[2][y, x] = 0; L[3][y, x] = src[3][ys, xs]; n_b += 1

    # la pièce : son image adoucie selon ses bords (SMOOTH), ses couleurs (NPAL, et ses touches), sans tramage
    im0 = Image.open(REF).convert('RGB')
    fine = np.asarray(im0.filter(ImageFilter.MedianFilter(SMOOTH[0]))).astype(float)
    soft = np.asarray(im0.filter(ImageFilter.MedianFilter(SMOOTH[1])).filter(ImageFilter.BoxBlur(SMOOTH[2]))).astype(float)
    def box(a, r):
        p_ = np.pad(a, r + 1, mode='edge').cumsum(0).cumsum(1); n_ = 2 * r + 1
        return (p_[n_:, n_:] - p_[:-n_, n_:] - p_[n_:, :-n_] + p_[:-n_, :-n_])[:a.shape[0], :a.shape[1]] / n_ ** 2
    lg = np.asarray(im0.convert('L')).astype(float); mu_ = box(lg, SMOOTH[3])
    w_ = np.clip((SMOOTH[4] - np.sqrt(np.maximum(box(lg * lg, SMOOTH[3]) - mu_ ** 2, 0))) / SMOOTH[5], 0, 1)[..., None]
    R_ = np.round(fine * (1 - w_) + soft * w_); ref = Image.fromarray(R_.astype(np.uint8))
    inner = ref.crop(INNER); ip = np.asarray(inner).reshape(-1, 3).astype(float)
    pal = np.asarray(inner.quantize(colors=NPAL, method=Image.Quantize.MEDIANCUT).getpalette()[:3 * NPAL]).reshape(NPAL, 3).astype(float)
    pick = {'tout': lambda c: c[:, 0] >= 0, 'violet': lambda c: c[:, 2] > c[:, 0],
            'vert': lambda c: (c[:, 1] > c[:, 0] - 15) & (c[:, 1] > c[:, 2] + 5),
            'bleu': lambda c: c[:, 2] > c[:, 0] + 20, 'rouge': lambda c: (c[:, 0] > 1.6 * c[:, 2]) & (c[:, 0] > 120)}
    for name, (ax0, ay0, ax1, ay1), kind in ACCENTS:
        c = R_[ay0:ay1, ax0:ax1].reshape(-1, 3); c = c[pick[kind.split()[0]](c)]
        pal = np.vstack([pal, np.percentile(c, {'clair': 80, 'sombre': 20}.get(kind.split()[-1], 50), axis=0)])
    du, dv = 1 / (rx1 - rx0), 1 / (ry1 - ry0)
    bar = lambda u, v: any(m0 - du <= u < m1 + du for m0, m1 in MULLIONS) or \
        any(t0 - dv <= v < t1 + dv and u0 <= u < u1 for t0, t1, u0, u1 in TRANSOMS)
    IH = R_.shape[0]

    # derrière la vitre, une boîte vue par l'œil de la rue (FVP au centre : ce qui longe la rue y court, ce qui entre dans
    # la maison est horizontal, ce qui est vertical d'aplomb), la façade à XF mètres de lui (la baie haute de WIN_M[0]) ;
    # le mur du fond, au droit du tableau, de face (SW pixels par mètre, ZW mètres plus loin le long de la rue : la baie
    # large de WIN_M[1]), son haut CEIL plus haut que celui de la baie : le plafond entre les deux, vu d'en dessous
    XF = WIN_M[0] / (np.tan(KH * D) - np.tan(KS * D))
    SW, SN = (FVP[0] - (XR + 0.5)) / XF, (FVP[0] - (XL - 0.5)) / XF
    ZW = WIN_M[1] / (1 / SW - 1 / SN) / SW
    WT = int(round(ray(KH, XR + 0.5) - CEIL * SW))                          # (la première rangée du mur, sous le plafond)
    kz = lambda ys: (FVP[1] - (WT - 0.5)) / (FVP[1] - ys)                    # (au plafond : la distance à l'œil, en part
    dc = lambda xs, ys: ((FVP[0] - xs) * kz(ys) - (FVP[0] - XR - 0.5)) / SW  # de celle du mur ; l'enfoncement dans la
    dm = lambda xs: (XR + 0.5 - xs) / SW                                     # maison, m ; au mur, de même)
    wall_xy = lambda xs, ys: (CORNER[0] - dm(xs) * PPM, CORNER[1] + (ys - (WT - 0.5)) / SW * PPM)   # (dans son image)
    near_sec = lambda x: U(x) < MULLIONS[0][0]                                # (la partie près du meneau : le voilage)
    glass_xy = lambda xs, ys: (rx0 + U(xs) * (rx1 - rx0), ry0 + V(xs, ys) * (ry1 - ry0))
    tone = lambda bx: np.median(np.asarray(im0)[bx[1]:bx[3], bx[0]:bx[2]].reshape(-1, 3).astype(float), 0)
    c_wall, c_far, c_spot, c_glow = (tone(b_) for b_ in CEIL_TONES)
    spots = [((CORNER[0] - sx_) / PPM, sz_) for sx_, sz_ in SPOTS]
    def ceiling(xs, ys):                                                     # (le plafond : plus sombre vers la fenêtre, la
        d, z = dc(xs, ys), ZW * (1 - kz(ys))                                 # lueur des spots autour d'eux)
        c = c_wall + (c_far - c_wall) * min(1.0, z / CEIL_FADE)
        for sd, sz in spots:
            c = c + (c_glow - c) * max(0.0, 1 - max(0.0, np.hypot(d - sd, z - sz) - SPOT_R) / (GLOW_R - SPOT_R)) ** 2
        return c
    def wall(ix, iy):                                                        # (le mur : son image, qui couvre toute la baie)
        assert 0 <= ix < R_.shape[1] and 0 <= iy < IH, 'la pièce ne couvre pas la baie (PPM, CORNER)'
        return R_[int(iy), int(ix)]

    # chaque pixel de vitre : SUB x SUB points sur ce qu'il voit (le voilage sur le plan de la vitre, le mur du fond, le
    # plafond) ; la couleur de la moitié de ces points s'il y en a une, sinon la plus proche de leur moyenne
    q, scr, surf = {}, set(), {}
    cont, smooth = {}, {}                                                   # (la couleur moyenne de ses points ; l'image lisse
    sx0, sy0, sx1, sy1 = SCREEN                                              # sous eux, en moyenne : les murs sans marches)
    for (y, x) in zip(*np.where(cls == 7)):
        cols, pts = [], []
        kind = 'rideau' if near_sec(x) else ('mur' if y >= WT else 'plafond')
        for a in range(SUB):
            xs = x - 0.5 + (a + 0.5) / SUB
            for b in range(SUB):
                ys = y - 0.5 + (b + 0.5) / SUB
                if kind == 'rideau':
                    u, v = U(xs), V(xs, ys)
                    if 0 <= u < 1 and 0 <= v < 1 and not bar(u, v):
                        xr, yr = glass_xy(xs, ys); cols.append(R_[int(yr), int(xr)])
                elif kind == 'mur':
                    xr, yr = wall_xy(xs, ys); cols.append(wall(xr, yr)); pts.append((xr, yr))
                else:
                    cols.append(ceiling(xs, ys))
        cs = np.array(cols) if cols else ip.mean(0)[None]
        ks = np.bincount(np.argmin(((cs[:, None, :] - pal[None]) ** 2).sum(2), 1))
        q[y, x] = int(ks.argmax()) if ks.max() >= len(cs) / 2 else int(np.argmin(((pal - cs.mean(0)) ** 2).sum(1)))
        surf[y, x] = kind
        if kind != 'rideau': cont[y, x] = cs.mean(0)
        if kind == 'mur': smooth[y, x] = float(np.mean([w_[int(yr), int(xr), 0] for xr, yr in pts]))
        elif kind == 'plafond': smooth[y, x] = 1.0
        if pts and np.mean([sx0 <= xr < sx1 and sy0 <= yr < sy1 for xr, yr in pts]) >= 0.5: scr.add((y, x))

    def regions(q, least, keep=frozenset()):                                 # (les taches de moins de least pixels : le ton
        q = dict(q); N4 = ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))   # qui l'entoure le plus ; ni
                                                                             # ses fines lignes, ni les lignes : keep)
        for _ in range(12):
            seen, changed = set(), False
            for p0 in sorted(q):
                if p0 in seen: continue
                comp, todo = [], [p0]; seen.add(p0)
                while todo:
                    p_ = todo.pop(); comp.append(p_)
                    for dy, dx in N4:
                        n_ = (p_[0] + dy, p_[1] + dx)
                        if n_ in q and n_ not in seen and q[n_] == q[p0]: seen.add(n_); todo.append(n_)
                if len(comp) >= least or all(p_ in keep for p_ in comp): continue
                ts = [q[p_[0] + dy, p_[1] + dx] for p_ in comp for dy, dx in N4
                      if (p_[0] + dy, p_[1] + dx) in q and q[p_[0] + dy, p_[1] + dx] != q[p0]]
                if not ts: continue
                t = max(sorted(set(ts)), key=ts.count)
                for p_ in comp: q[p_] = t
                changed = True
            if not changed: break
        return q
    q = regions(q, MIN_REG)

    # par-dessus, nettes, les grandes lignes de la pièce (LINES), chacune de la couleur de l'image sous elle, sur ce qui
    # la porte (le voilage, le mur) ; les spots, nets, au plafond
    near = lambda c: int(np.argmin(((pal - c) ** 2).sum(1)))
    med = lambda bx: np.median(R_[bx[1]:bx[3], bx[0]:bx[2]].reshape(-1, 3), 0)
    gl = [k for k in sorted(q) if surf[k] != 'plafond']
    img = lambda k, xs, ys: glass_xy(xs, ys) if surf[k] == 'rideau' else wall_xy(xs, ys)
    lines = set()
    def paint(kind, bx, t):
        x0_, y0_, x1_, y1_ = bx
        for (y, x) in gl:
            cx, cy = img((y, x), x, y)
            if kind == 'h':                                                  # (de travers : une rangée au moins)
                c_, d_ = sorted((img((y, x), x, y - 0.5)[1], img((y, x), x, y + 0.5)[1]))
                if x0_ <= cx < x1_ and (max(0, min(d_, y1_) - max(c_, y0_)) >= (d_ - c_) / 2 or c_ <= (y0_ + y1_) / 2 < d_):
                    q[y, x] = t; lines.add((y, x))
            elif kind == 'v':                                                # (d'aplomb : une colonne au moins)
                a_, b_ = sorted((img((y, x), x - 0.5, y)[0], img((y, x), x + 0.5, y)[0]))
                if y0_ <= cy < y1_ and (max(0, min(b_, x1_) - max(a_, x0_)) >= (b_ - a_) / 2 or a_ <= (x0_ + x1_) / 2 < b_):
                    q[y, x] = t; lines.add((y, x))
    def inside(poly, px, py):
        c_, j_ = False, len(poly) - 1
        for i_ in range(len(poly)):
            (xi, yi), (xj, yj) = poly[i_], poly[j_]
            if (yi > py) != (yj > py) and px < (xj - xi) * (py - yi) / (yj - yi) + xi: c_ = not c_
            j_ = i_
        return c_
    for kind, bx in LINES:
        if kind == 'forme':                                                  # (une forme : les pixels dont le centre y tombe)
            poly, (sx0_, sy0_, sx1_, sy1_, pc) = bx
            t = near(np.percentile(np.asarray(im0)[sy0_:sy1_, sx0_:sx1_].reshape(-1, 3).astype(float), pc, axis=0))   # (l'image même)
            for (y, x) in gl:
                if inside(poly, *img((y, x), x, y)): q[y, x] = t; lines.add((y, x))
            continue
        if kind == 'cadre':                                                  # (un cadre : quatre lignes de sa couleur)
            x0_, y0_, x1_, y1_, e_ = bx
            t = near(np.median(np.vstack([R_[y0_:y0_ + e_, x0_:x1_].reshape(-1, 3), R_[y0_:y1_, x0_:x0_ + e_].reshape(-1, 3)]), 0))
            for k_, b2 in (('h', (x0_, y0_, x1_, y0_ + e_)), ('h', (x0_, y1_ - e_, x1_, y1_)),
                           ('v', (x0_, y0_, x0_ + e_, y1_)), ('v', (x1_ - e_, y0_, x1_, y1_))):
                paint(k_, b2, t)
            continue
        paint(kind, bx, near(med(bx)))
    for (y, x), k in surf.items():                                           # (un spot : les pixels dont le centre y tombe)
        if k == 'plafond' and any(np.hypot(dc(x, y) - sd, ZW * (1 - kz(y)) - sz) < SPOT_R for sd, sz in spots):
            q[y, x] = near(c_spot); lines.add((y, x))
    q = regions(q, MIN_REG, frozenset(lines))
    scr = {k for k in scr if k not in lines}

    # sa profondeur : la ligne sombre du plafond contre le mur, le mur plus sombre dans l'angle de la fenêtre (éteinte
    # et allumée) ; allumée, le mur plus sombre loin de la lampe, et toute la pièce un peu plus sombre que les arêtes
    # claires
    DEP = np.ones((H, W, 2))
    d0 = dm(XR - J - 0.5)
    for (y, x), k in surf.items():
        if k == 'rideau': continue
        if 0 <= y - (WT - 1) < 3: DEP[y, x] *= JUNCTION[y - (WT - 1)]
        if k == 'mur':
            DEP[y, x] *= 1 - CORNER_AO * max(0.0, 1 - (dm(x) - d0) / AO_W)
            DEP[y, x, 1] *= 1 - FALL * min(1.0, abs(dm(x) - (CORNER[0] - LAMP) / PPM) / FALL_D)
        DEP[y, x, 1] *= ROOM_DIM

    # ce qu'on en voit : la vitre que les feuilles ne cachent pas ; sa lumière où elles s'ouvrent sur GLOW_MIN pixels
    vis = (cls == 7) & ~front
    lab = np.zeros((H, W), int); n_lab = 0
    for (y, x) in zip(*np.where(vis)):
        if lab[y, x]: continue
        n_lab += 1; comp = flood(vis & (lab == 0), [(y, x)]); lab[comp] = n_lab
    size = np.bincount(lab.ravel())
    lit = [(y, x) for (y, x) in zip(*np.where(vis)) if size[lab[y, x]] >= GLOW_MIN]
    edge = [(y, x) for (y, x) in zip(*np.where(cls == 8)) if XL < x < XR and not front[y, x]]

    # éteinte : le verre sombre du peintre, les grandes formes de la pièce à peine lisibles dedans (leur clarté seule, les
    # taches de moins de MIN_OFF pixels fondues dans ce qui les entoure, ses lumières et son écran éteints)
    hg = city[old & ~grow(~old, 3)][:, :3]
    lum = pal @ LUM; ks = np.array([q[k] for k in lit])
    z = np.clip((lum - np.median(lum[ks])) / lum[ks].std(), *OFF_Z)
    qo = regions({k: (int(np.argmin(lum)) if k in scr else t) for k, t in q.items()}, MIN_OFF)
    OFF = {k: hg.mean(0) * (1 + OFF_K * z[t]) for k, t in qo.items()}
    # allumée : à mi-chemin de la fenêtre éclairée de la rue (la moyenne et l'écart de chaque canal de la lumière de la
    # petite fenêtre) ; ses touches et l'écran gardent leur teinte (leur clarté ramenée de même) ; l'arête de l'appui dans
    # sa lumière
    upi = load(UP + '.webp', 'RGBA', BEFORE); upl = upi[upi[..., 3] == 255][:, :3]
    onp = np.clip(upl.mean(0) + (pal - pal[ks].mean(0)) / pal[ks].std(0) * upl.std(0), 0, 255)
    onq = np.clip(upl.mean(0) + (pal - pal[ks].mean(0)) * (upl @ LUM).std() / lum[ks].std(), 0, 255)
    onp = (onp + onq) / 2                                                    # (à mi-chemin : ses couleurs encore à elle)
    ON = {k: (onq if (k in scr or t >= NPAL) else onp)[t] for k, t in q.items()}
    room = sorted({q[k] for k in lit if k not in scr and q[k] < NPAL}, key=lambda k: lum[k])
    sill = np.array(EDGE) + SILL_LIT * (onp[room[-1]] - np.array(EDGE))
    pm, ps, lr = pal[ks].mean(0), pal[ks].std(0), (upl @ LUM).std() / lum[ks].std()
    def onmap(c):                                                            # (la palette allumée, pour toute couleur de l'image)
        c = np.asarray(c, float)
        return (np.clip(upl.mean(0) + (c - pm) / ps * upl.std(0), 0, 255) + np.clip(upl.mean(0) + (c - pm) * lr, 0, 255)) / 2
    assert np.allclose(onmap(pal), onp)

    # les murs et le plafond sans marches : là où l'image est lisse sous ses points (ses murs, la lumière des spots sur eux,
    # le plafond), hors des lignes, de l'écran, de l'affiche et du spot, chaque pixel la couleur moyenne de ses points,
    # adoucie avec ses voisins de la même surface (WALL_SMOOTH), allumée comme la palette : des dégradés de lumière au lieu
    # d'aplats en marches
    frames_ = [bx[:4] for kind, bx in LINES if kind == 'cadre']             # (ce qu'un cadre entoure reste tel quel : l'affiche)
    framed = {k for k in cont if surf[k] == 'mur' and any(a_ <= wall_xy(k[1], k[0])[0] < c_ and b_ <= wall_xy(k[1], k[0])[1] < d_
                                                         for a_, b_, c_, d_ in frames_)}
    flat = [k for k in sorted(cont) if smooth[k] >= WALL_SMOOTH[0] and k not in lines and k not in scr and k not in framed]
    if flat:
        ys_, xs_ = np.array([k[0] for k in flat]), np.array([k[1] for k in flat])
        oy, ox = ys_.min() - 4, xs_.min() - 4; hh, ww = ys_.max() + 5 - oy, xs_.max() + 5 - ox
        r_ = int(np.ceil(3 * WALL_SMOOTH[1])); kern = np.exp(-0.5 * (np.arange(-r_, r_ + 1) / WALL_SMOOTH[1]) ** 2)
        def gb(a):                                                           # (un flou gaussien, sans sortir de la boîte)
            a = np.pad(a, ((r_, r_), (r_, r_)) + ((0, 0),) * (a.ndim - 2))
            a = sum(kern[i] * a[i:i + a.shape[0] - 2 * r_] for i in range(2 * r_ + 1))
            return sum(kern[i] * a[:, i:i + a.shape[1] - 2 * r_] for i in range(2 * r_ + 1))
        for kind in ('mur', 'plafond'):                                      # (chaque surface à part : la corniche entre elles)
            m_ = np.zeros((hh, ww)); c_ = np.zeros((hh, ww, 3))
            for k in flat:
                if surf[k] == kind: m_[k[0] - oy, k[1] - ox] = 1; c_[k[0] - oy, k[1] - ox] = cont[k]
            wm_ = gb(m_); cb_ = gb(c_ * m_[..., None]) / np.maximum(wm_, 1e-9)[..., None]
            for k in flat:
                if surf[k] == kind: ON[k] = onmap(cb_[k[0] - oy, k[1] - ox])
            for k in sorted(cont):                                           # (et le pixel de mur au bord d'un objet, où l'image
                j_ = (k[0] - oy, k[1] - ox)                                  # n'est plus lisse, si sa couleur est celle du mur à
                if surf[k] != kind or k in lines or k in scr or k in framed or not (0 <= j_[0] < hh and 0 <= j_[1] < ww):
                    continue                                                 # côté : sans liseré)
                if not m_[j_] and wm_[j_] >= 1 and np.linalg.norm(ON[k] - onmap(cb_[j_])) < WALL_SMOOTH[2]: ON[k] = onmap(cb_[j_])

    # le voilage, sur le plan de la vitre, du tableau proche au meneau : un rideau léger aux plis d'aplomb (VOILE : plus
    # serrés en haut, froncé sur la tringle), éclairé par la pièce derrière lui (l'image très floue au point du mur qu'il
    # cache : plus chaud en bas, où la lampe est derrière lui, plus sombre en haut), allumé, passé vers le crème ; un pli à sa
    # crête à peine moins clair que la pièce, à son creux un peu moins, jamais plus clair qu'elle. Éteint, sa clarté seule
    # dans le verre sombre (comme le reste de la pièce). Dans le vent (SWAY), poussé dans la pièce : le pixel montre le tissu
    # venu de plus à droite, ou, passé son bord libre, la pièce derrière lui (le mur ou le plafond, allumés comme eux)
    im_b = R_.astype(float)
    for _ in range(3): im_b = np.stack([box(im_b[..., c], int(VOILE['blur'])) for c in range(3)], -1)
    vu0, vu1 = U(XL + 0.5), MULLIONS[0][0]
    u_edge = 1 - 0.9 * (U(min(mcols)) - U(min(mcols) - 1)) / (vu1 - vu0)   # (son bord libre : son dernier pixel)
    lamp_d = (CORNER[0] - LAMP) / PPM
    def dep_lit(x, y):                                                       # (un pixel du mur allumé : sa profondeur, comme DEP)
        d = (1 - CORNER_AO * max(0.0, 1 - (dm(x) - d0) / AO_W)) * (1 - FALL * min(1.0, abs(dm(x) - lamp_d) / FALL_D))
        return d * (JUNCTION[y - (WT - 1)] if 0 <= y - (WT - 1) < 3 else 1) * ROOM_DIM
    def behind(xs, ys):                                                      # (la pièce derrière le voilage : sa lumière)
        ix, iy = wall_xy(xs, ys)
        return im_b[int(np.clip(iy, VOILE['top'], IH - 1)), int(np.clip(ix, 0, R_.shape[1] - 1))]
    def cloth(xs, ys, s):                                                    # (le tissu à ce point : sa part de la lumière,
        v = min(1.0, max(0.0, V(xs, ys)))                                    # ou None : la pièce, passé son bord libre)
        u = (U(xs + s * SWAY['amp'] * (1 - np.exp(-v / SWAY['v0']))) - vu0) / (vu1 - vu0)
        if u >= 1: return None
        g = u * (1 + VOILE['gather'] * (1 - v)); g += VOILE['warp'] * np.sin(2 * np.pi * 1.3 * g + 0.7)
        f = VOILE['trough'] + (VOILE['crest'] - VOILE['trough']) * (0.5 + 0.5 * np.cos(2 * np.pi * VOILE['folds'] * g))
        return f * (VOILE['edge'] if u > u_edge else 1)
    def tint(c):                                                             # (sa lumière passée vers le crème : le tissu, pas le
        return c + VOILE['desat'] * ((c @ LUM) * np.array(VOILE['cream']) / (np.array(VOILE['cream']) @ LUM) - c)   # mur)
    def voile(y, x, s):                                                      # (un pixel du voilage : allumé, et sa clarté éteint)
        lit_, img_ = [], []
        for a in range(SUB):
            xs = x - 0.5 + (a + 0.5) / SUB
            for b in range(SUB):
                ys = y - 0.5 + (b + 0.5) / SUB
                f = cloth(xs, ys, s)
                if f is None:
                    xr, yr = wall_xy(xs, ys); c = wall(xr, yr) if 0 <= yr < IH else ceiling(xs, ys)
                    lit_.append(onmap(c) * dep_lit(x, y)); img_.append(0.0)
                else:
                    lit_.append(tint(onmap(behind(xs, ys))) * f * ROOM_DIM); img_.append(VOILE['off'][0] + VOILE['off'][1] * (f - 1))
        return np.mean(lit_, 0), float(np.mean(img_))
    curt = sorted(k for k in q if surf[k] == 'rideau')                      # (ses tons de palette d'avant restent dans ks : la
    for k in curt:                                                           # pièce allumée garde les siens)
        ON[k], z_ = voile(*k, 0.0); OFF[k] = hg.mean(0) * (1 + OFF_K * np.clip(z_, *OFF_Z))

    # le bois du peintre pour les faces de la baie : le corps d'une de ses planches (entre ses joints), pris le long de
    # son rayon (le chambranle du haut, la sous-face, l'appui : leur fil vers FVP) ou en travers (les montants, le
    # tableau : leur fil d'aplomb), chaque pixel un pixel différent, en miroir depuis le bord de ses planches
    sx = list(range(*SRC_X)); ns = len(sx)
    def wood(along, f, k):
        i = (SRC_X[0] - 1 - along) % (2 * ns); xs = sx[i if i < ns else 2 * ns - 1 - i]
        ys = int(round(ray(k + BODY[0] + (BODY[1] - BODY[0]) * min(1.0, max(0.0, f)), xs)))
        assert board(xs, ys), (xs, ys)
        return city[ys, xs, :3]
    def face(c, x, y):                                                       # (le bois d'un pixel de la baie, et sa part)
        if c in (2, 3):
            if xa < x < xb and y <= hO.get(x, -1):                           # (le chambranle du haut)
                return wood(x, (y - hC[x]) / max(1, hO[x] - hC[x]), WOOD[0]) * (CASE_F if c == 2 else CASE_F * UNDER_F)
            return wood(y, 0.25 if x <= XL else 0.75, WOOD[0]) * CASE_F       # (ses montants)
        if c == 4: return wood(x, (y - hO[x] - 1) / max(1, rail.get(x, hJ + 1) - hO[x] - 2), WOOD[1]) * SOFFIT_F
        if c == 5: return wood(y, (x - (XR - J + 1)) / max(1, J - 2), WOOD[2]) * JAMB_F
        if c in (9, 10): return wood(x, 0.3 if y == sO[x] + 1 else 0.7, WOOD[3]) * (SILL_F if c == 9 else SILL_F * UNDER_F)
    n_w = 0
    for y, x in zip(*np.where(cls > 0)):
        if front[y, x]: continue
        c = cls[y, x]
        if c == 11:                                                          # (une ombre portée sur les planches)
            for k in (0, 1): L[k][y, x, :3] *= MUL[y, x, 0]
            L[3][y, x] *= MUL[y, x, 0]
            continue
        if c in (1, 8): col, sun = np.array(EDGE, float), 255
        elif c == 6: col, sun = np.array(FRAME, float), 0
        elif c == 7: col, sun = OFF[y, x] * MUL[y, x, 0] * DEP[y, x, 0], 0
        else: col, sun = face(c, x, y) * MUL[y, x, 0], 255
        L[0][y, x, :3] = col; L[1][y, x, :3] = col * cut[y, x]; L[0][y, x, 3] = L[1][y, x, 3] = 255
        L[2][y, x] = 0; L[3][y, x] = sun
        n_w += 1
    spr = np.zeros((H, W, 4))
    for (y, x) in lit: spr[y, x] = [*(ON[y, x] * MUL[y, x, 1] * DEP[y, x, 1]), 255]
    for (y, x) in edge: spr[y, x] = [*sill, 255]

    # le bord de l'écran : ses lignes projetées laissaient des trous (le mur passait entre deux), un cadre de deux pixels
    # de sa teinte la plus sombre en haut, à droite et en bas, allumé comme éteint
    x0_, y0_, x1_, y1_ = SCR_PX
    ring = [(y, x) for y in (y0_ - 2, y0_ - 1, y1_, y1_ + 1) for x in range(x0_, x1_ + 2)] + \
           [(y, x) for y in range(y0_ - 2, y1_ + 2) for x in (x1_, x1_ + 1)]
    for arr in (spr, L[0], L[1]):
        band = arr[y0_ - 1, x0_:x1_ + 2, :3]; dark = band[band.sum(1) <= np.percentile(band.sum(1), 50)]
        tone = np.median(dark, 0)
        for (y, x) in set(ring):
            if (y, x) in lit and (y, x) not in edge: arr[y, x, :3] = tone          # (la pièce seule, pas l'appui ni le cadre)
    for (n, m), l in zip(names, L): save(l, n, m)
    ys, xs = np.where(spr[..., 3] > 0)
    bx, by, bw, bh = int(xs.min()), int(ys.min()), int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1)
    save(spr[by:by + bh, bx:bx + bw], UP + '.webp', 'RGBA')

    # le voilage dans le vent : ses SWAY['n'] images, chacune le comp tel quel dans la boîte du voilage allumé, le voilage
    # poussé de s (celle de s = 0 : le comp même), côte à côte ; street.js (BAYC) les pose dans l'image du comp
    lits = set(lit); cl = [k for k in curt if k in lits]
    fy0, fx0 = min(k[0] for k in cl), min(k[1] for k in cl)
    fh, fw = max(k[0] for k in cl) + 1 - fy0, max(k[1] for k in cl) + 1 - fx0
    S_ = np.linspace(*SWAY['s'], SWAY['n']); assert np.isclose(S_, 0).sum() == 1, 'SWAY : s = 0 parmi ses images'
    sheet = np.zeros((fh, fw * SWAY['n'], 4))
    for i, s in enumerate(S_):
        fr = spr[fy0:fy0 + fh, fx0:fx0 + fw].copy()
        if not np.isclose(s, 0):
            for (y, x) in cl: fr[y - fy0, x - fx0, :3] = voile(y, x, s)[0] * MUL[y, x, 1]
        sheet[:, i * fw:(i + 1) * fw] = fr
    save(sheet, CURT + '.webp', 'RGBA')
    s_ = open(A('street.js'), encoding='utf-8').read()
    s_, n_s = re.subn(r'"%s": \{"src": "assets/%s\.webp\?v=\d+", "x": \d+, "y": \d+, "w": \d+, "h": \d+\}' % (UP, UP),
                      f'"{UP}": {{"src": "assets/{UP}.webp?v={UP_V}", "x": {bx}, "y": {by}, "w": {bw}, "h": {bh}}}', s_)
    assert n_s == 1, 'street.js : le comp de la petite fenêtre est introuvable'
    s_, n_c = re.subn(r"const BAYC = \{ src: 'assets/%s\.webp\?v=\d+', box: \[[\d, ]+\], n: \d+, s: \[[-\d., ]+\]" % CURT,
                      f"const BAYC = {{ src: 'assets/{CURT}.webp?v={CURT_V}', box: [{fx0 - bx}, {fy0 - by}, {fw}, {fh}], "
                      f"n: {SWAY['n']}, s: [{SWAY['s'][0]}, {SWAY['s'][1]}]", s_)
    assert n_c == 1, 'street.js : le voilage (BAYC) est introuvable'
    open(A('street.js'), 'w', encoding='utf-8').write(s_)
    sp = spr[spr[..., 3] > 0][:, :3]
    print('baie', XR - XL + 1, 'colonnes,', n_w, 'px | planches refaites', n_b, 'px | meneau', sorted(mcols),
          '| sa lumière', len(xs), 'px en', (bx, by, bw, bh), ': moyenne', sp.mean(0).round(1), 'écart', sp.std(0).round(1),
          '(la petite fenêtre :', upl.mean(0).round(1), upl.std(0).round(1), ')')


if __name__ == '__main__':
    main()
