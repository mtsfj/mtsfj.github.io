#!/usr/bin/env python3
"""Ichiraku : derrière sa vitrine, la boutique en petite maquette 3D, vue par l'œil de la rue.

    python3 tools/ichiraku_interior.py                  (la boutique fermée, tools/src/edits/shop_off_before.webp, et le
                                                          masque assets/ramen_glass.webp ; on peut le relancer : il écrit la
                                                          même chose ; puis la chaîne, tools/redraw_zones.py et la suite)
    python3 tools/ichiraku_interior.py --preview dossier (des aperçus seulement, rien d'écrit)
    (un module aussi : la zone 'vitrine' de tools/redraw_zones.py, la dernière, appelle draw() : la vitrine dans les calques)

La caméra de la rue est une perspective à un point : focale F = 1400 px, point de fuite VP (700, 615), l'œil à EYE = 1,5 m
du trottoir. La façade du ramen est à droite de la rue et court vers VP ; sa devanture en est (tools/ichiraku_front.py : le
propriétaire, « Faut refaire Ichiraku, la devanture, proprement ») : un panneau vitré fixe étroit à gauche et la porte
coulissante, une glace claire chacun dans son cadre de bois, au-dessus de leurs soubassements (VITRE : les colonnes de la baie ;
le verre, glass_columns ; au commit BEFORE, quatre vitres et une traverse, PEINTES). Le seuil des portes
(SEUIL : la première rangée du trottoir sous elles, mesurée colonne par colonne) est sur des rayons vers VP à 1,5 m sous
l'œil : la façade est à X_F = 5,53 m à droite de l'œil, la baie de Z = 14,8 à 16,8 m le long de la rue ; le bas du verre
sur la traverse des soubassements, à 1,01 m (il cache les tabourets et le bas des gens), l'ourlet du noren à 1,74 m, le haut
du verre sous la traverse haute des portes, à 2,60 m.

La boutique, une boîte derrière la façade (D_ROOM de fond, le plafond à CEIL). Par une porte de côté, un rayon file le long de
la rue (un tiers de mètre vers le fond pour un mètre le long de la rue) : ce qu'il rencontre au bout est le mur du bout de la
boutique, de travers à la rue, donc de face (ses horizontales horizontales), et on ne voit qu'une bande de la pièce. Le
comptoir des clients est de face lui aussi, son dessus à CTR_H = 1 m : son arête sur la rangée CTR_ROW = 641, la ligne où
assets/street.js coupe Teuchi (inchangée), le met à Z_C = 26,3 m ; derrière lui l'allée de Teuchi (AISLE), le comptoir de
travail (BACK_D, caché par celui des clients), le mur du bout à Z_E = 28,4 m (11,5 m derrière la porte, 49 px par mètre).
L'image du propriétaire (tools/src/ichiraku_room.webp : étagères, bouteilles, bols, bocaux, casseroles et louches, la
marmite) est posée sur ce mur à K_WALL = 230 pixels de l'image par mètre (ses étagères à 30 cm l'une de l'autre en
moyenne, ses bouteilles de 35 à 40 cm, ses bols de 20 cm), le haut de son comptoir de travail (V_REF) à 0,9 m, glissée
pour que sa marmite soit au milieu de la vitrine (POT). Par le verre, sous le noren, on en voit une bande de 1,3 m de
large, de 1 m à 1,9 m de haut : les casseroles et les louches, la marmite à couvercle, des bocaux, l'armoire aux bols, le
haut de la grande marmite. Sur le
comptoir des clients, des objets de l'image (OBJETS : deux bols, chacun devant son tabouret, celui du milieu et celui de
Naruto ; un verre, des condiments, une bouteille ; de face, posés sur son dessus, à l'échelle d'un bol de 21 cm, K_OBJ ; leur
silhouette, shape_ok) ; sa face en planches (PLANK : leur ton tiré
des planches de l'image, leurs joints), à l'ombre sous son arête, plus sombre vers le sol ; le retrait du pied, la barre pour
les pieds (RAIL). Devant lui, trois tabourets (STOOLS : sous le client du coin, sous Naruto, un entre eux) : un coussin rond
rouge, quatre pieds, l'anneau. Au-dessus du comptoir, pendue à 1,6 m, une lanterne de l'image (LANTERN). Le sol ne se voit
pas (la maquette l'a quand même) ; le plafond, par le haut de la vitrine derrière le noren (ses fentes, la boutique fermée) :
son bois, éclairé par les lampes du fond, plus sombre vers la façade (CEIL_C, CEIL_K).

Le rendu. Chaque pixel du verre (ses deux vitres) est pris sur SS x SS rayons de l'œil, puis ramené au pixel entier selon ses
bords
(reduce : les surfaces nettes, les éclats gardés). La lumière : le haut à l'ombre du noren (HAUT), la vapeur au-dessus de la
marmite plus claire (STEAM). Le grain du peintre (GRAIN : fixe, plein sur l'uni, léger sur le chargé), puis chaque pixel
ramené à la palette de la boutique (40 couleurs tirées de son verre allumé d'avant, ses quatre vitres, du noren et des
lanternes allumés), un grain ne sautant jamais plus d'une marche. La glace elle-même (skin : « on dirait zéro vitre », puis
« reflet trop important et elle reflète pas le bon endroit ») : ce qu'elle reflète vraiment, la scène retournée sur le plan des
vitres dans la caméra de la rue (mirror_source : de l'œil, des vitres presque rasantes renvoient le bout gauche de la rue, le
coin de l'oden à 48-55 m et le trottoir devant, pas le dagashi-ya d'en face), faible, un peu plus en haut et aux bords qu'au
droit des gens ; un lustre à peine (REFLET) ; un fil clair le long de ses bords ; quelques gouttes ; un peu de buée aux coins du
bas. Fermée, un verre sombre où les lumières d'en face ne sont que des reflets doux (shop_off) ; dans
la coupure, la rue coupée qu'elle reflète (street_unlit) ; allumée, assets/ramen_glass_skin.webp, que street.js ajoute sur la
pièce et ses gens, plus fort de jour, la glace prenant un peu de ce qu'on voit au travers.

Dans layer_city_off (allumée) ; street_unlit (la coupure de courant : la même pièce dans le bleu nuit du verre coupé, de son
plus sombre à son plus clair selon la clarté de la pièce allumée, à ses couleurs) : par draw(), la zone 'vitrine' ;
tools/src/edits/shop_off_before.webp (fermée : tout le verre couvert de son bleu nuit, posé à 0,88, la pièce allumée n'y
passe qu'à 12 % ; tools/redraw_zones.py en fait assets/shop_off.webp) ; assets/ramen_glass.webp (le masque du verre où
passent les ombres de Teuchi et du client, la lumière de la pièce qui respire et la vapeur : plein au-dessus du comptoir, un
peu moins sur le plus sombre, MASK ; une part égale sur sa face, sous la ligne des figures ; rien ailleurs que sur le verre :
ni sur le cadre, ni sur la lisière du bas). Le cadre, la façade : tels que les zones d'avant les laissent. night_far et
street_sun : 0 ici, tels quels. Il faut git, Pillow, numpy.
"""
import os
import sys
import numpy as np
from PIL import Image

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import interieur as I

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'tools', 'src', 'ichiraku_room.webp')
EDITS = os.path.join(ROOT, 'tools', 'src', 'edits')
NAMES = (('layer_city_off.webp', 'RGBA'), ('street_unlit.webp', 'RGBA'))
SO_BEFORE = os.path.join(EDITS, 'shop_off_before.webp')   # (la boutique fermée, avant tools/redraw_zones.py, qui la pose)
BEFORE = '402ebae'                   # (les calques avant l'outil d'Ichiraku : sa zone reprise de là à chaque fois)
ZONE = (1150, 500, 1232, 700)        # x0, y0, x1, y1 : la vitrine et son cadre
SHOP_OFF, GLASS = (1112, 448), (1150, 520)   # (edits/shop_off_before.webp, ramen_glass.webp : leur place)

# ---- la caméra de la rue, la façade et ses portes
F, VX, VY, EYE = 1400.0, 700.0, 615.0, 1.5
SEUIL = ((1160, 744), (1170, 744), (1180, 746), (1190, 747), (1200, 749), (1210, 751), (1220, 753))
X_F = EYE / float(np.mean([(y - VY) / (x - VX) for x, y in SEUIL]))
VITRE = (1160, 1223)                 # les colonnes de la baie, d'un montant du cadre à l'autre : son verre, celui des deux vitres
                                     # de la devanture (tools/ichiraku_front.py, glass_columns), leurs montants entre
ARETES = ()                          # (les arêtes des montants : dessinées par la devanture)
BAS_RAYON = 0.1467                   # (la lisière claire du bas des vitres du peintre : y = VP_y + c |x - VP_x|)
PEINTES = (((1160, 1170), (1173, 1185), (1192, 1205), (1209, 1223)), (631, 636))   # (les quatre vitres du peintre au commit
                                     # BEFORE, leurs colonnes et leur traverse : où prendre les tons de son verre allumé, coupé)
REFLET = ((-1.0, 1186.0, 6.0, 0.07, 515, 650), (-1.0, 1199.0, 2.0, 0.045, 520, 655))   # le lustre de la glace : deux bandes
                                     # en biais, le haut des vitres (x + y - VP_y = leur milieu ; leur demi-largeur, leur part, leurs
                                     # rangées : fondues sur 12 à chaque bout)
REFLET_C = (176.0, 186.0, 232.0)     # (sa couleur : la nuit bleue de la rue)
# la glace (le propriétaire : « on dirait zéro vitre, trop transparent », puis « reflet trop important et elle reflète pas le
# bon endroit ») : ce qu'elle ajoute de lumière à ce qu'on voit au travers, pixel par pixel (skin). Son reflet : la scène
# retournée sur le plan des vitres (X_D, mirror_source). Un miroir d'aplomb parallèle à l'axe de la caméra garde la profondeur
# et la hauteur de ce qu'il renvoie : chaque pixel du verre montre ce que la rue a sur la même rangée, à la colonne
# 2 VP_x + 2 F X_D / Z - x, Z la profondeur de ce que son rayon renvoyé rencontre d'abord : la façade d'en face (le plan de
# l'oden, OPPOSITE : X = -6,79 m, mesuré par tools/oden_interior.py ; le rayon y arrive à Z = Z_vitre (2 X_D - X_O) / X_D,
# 48 à 55 m) ou, sous l'horizon, le sol (Z = EYE F / (y - VP_y)). Ce qui est au-delà du coin de l'oden (48 m) est caché à
# l'œil par l'oden lui-même : la rue en a, à ces colonnes, le fond sombre de la maison du bout (le même lointain). Faible : le
# verre en renvoie REFL (à 70° d'incidence, de l'ordre de 0,17), un peu plus en haut et au bord des vitres, moins sur les gens ;
# un lustre à peine (REFLET) ; un fil clair le long des bords ; quelques gouttes ; un peu de buée chaude aux coins du bas.
# Allumée : assets/ramen_glass_skin.webp, ajouté par street.js (un peu plus de jour) ; fermée et coupée : sur le verre sombre
OPPOSITE = -6.79                     # (le plan des façades d'en face au bout de la rue : l'oden, tools/oden_interior.py X_F)
MIRROR_BLUR = 1.0
SKIN = dict(refl=0.17, top=0.4, edge=0.8, people=0.4, rim=(205.0, 215.0, 232.0, 0.22), drops=10, drop=0.5,
            fog=(230.0, 214.0, 196.0, 0.2, 12, 9), shut=1.0, cut=1.0, dark=0.55)
RIM_SIDES = (1.0, 0.7, 0.35, 0.25)   # (le fil des bords : en haut, à gauche, à droite, en bas)
PEOPLE = ((1176, 588, 1224, 661), (1163, 612, 1173, 642))   # (où se tiennent les gens et la pile : le reflet y est moindre)
SKIN_OUT = 'ramen_glass_skin.webp'   # (au coin du masque, GLASS)
NOREN = ('ichiraku_noren.webp', 1150, 500, 79, 104)   # (le noren au repos, pendu dehors devant la porte : son ourlet, colonne par colonne)

# ---- la boutique
CTR_H, CTR_D, CTR_ROW = 1.0, 0.5, 641   # le comptoir des clients : son dessus (m), sa profondeur, la rangée de son arête
Z_C = F * (EYE - CTR_H) / (CTR_ROW + 0.6 - VY)
LIP = 0.018                          # (l'arête du dessus, prise dans la lumière)
KICK = (0.12, 0.05)                  # (le retrait du pied : sa hauteur, sa profondeur)
RAIL = (0.24, 0.016, 0.1)            # (la barre pour les pieds : sa hauteur, son rayon, devant la face)
PLANK = (0.15, 0.012, (0, 893, 506, 1020), (130.0, 64.0, 36.0), (58.0, 27.0, 18.0))   # (les planches de la face : largeur,
                                     # joint, leur bande dans l'image, le ton en haut et au pied)
AISLE, BACK_D, BACK_H = 0.9, 0.65, 0.9   # l'allée de Teuchi, le comptoir de travail (profondeur, hauteur)
Z_E = Z_C + CTR_D + AISLE + BACK_D
D_ROOM = 5.4                         # (la pièce : son fond depuis la façade, assez pour que le mur du bout couvre les vitres)
CEIL = 2.7
CEIL_C, CEIL_K = (88.0, 48.0, 30.0), (0.5, 0.75)   # (le plafond : son bois, sa part de lumière contre la façade, en plus au fond)
K_WALL = 230.0                       # pixels de l'image par mètre sur le mur du bout
V_REF = 620.0                        # (la rangée de l'image du haut de son comptoir de travail, à BACK_H)
POT = (382.0, 1198.0)                # (la colonne de l'image au milieu de la marmite, la colonne de la rue où elle tombe)
WALL_GAIN = 1.2                      # (l'image dans la lumière de la boutique : plus claire, un peu plus chaude)
TINT = (1.04, 0.98, 0.9)
OBJ_Z, K_OBJ = 0.17, 420.0           # les objets du comptoir : derrière son arête de tant, pixels de l'image par mètre
STOOLS = (1163.0, 1189.5, 1216.0)    # les tabourets : la colonne de la rue où tombe leur milieu
STOOL = dict(dz=0.28, r=0.16, top=0.66, th=0.055, leg=0.013, at=0.115, ring=0.27)   # (devant le comptoir de dz, le coussin :
                                     # son rayon, son dessus, son épaisseur ; les pieds : leur rayon, leur écart ; l'anneau)
BOL = lambda i: round(VX + (STOOLS[i] - VX) * (Z_C - STOOL['dz']) / (Z_C + OBJ_Z), 1)   # (un bol devant le tabouret i : son
                                     # X, sa colonne à la profondeur des objets)
OBJETS = (('bol', (303, 786, 389, 838), BOL(1)),
          ('verre', (398, 784, 426, 826), 1192.5),
          ('rect', (430, 758, 450, 799), 1196.5),
          ('rect', (455, 758, 476, 799), 1200.0),
          ('bol', (390, 650, 461, 692), BOL(2)),
          ('bouteille', (184, 744, 213, 801), 1166.0))
LANTERN = ((232, 246, 277, 314), 1179.0, 0.19, 1.6, 0.12)   # (sa boîte dans l'image, sa colonne, sa largeur, son bas (m),
                                     # derrière l'arête du comptoir de tant)
SS = 8                               # (SS x SS rayons par pixel)
HAUT = (0.6, 0.8, 0.92)              # sous l'ourlet du noren, à son ombre : la part gardée (la rangée contre lui, les suivantes)
STEAM = (1198.0, 619, 20, 5.0, 0.14, (236, 206, 170))   # (la vapeur : sa colonne, la rangée du bord de la marmite, sa
                                     # hauteur, sa demi-largeur, sa part, sa couleur)
GRAIN = 0.075                        # (le grain : son écart, en clarté)
CUT = (12, 85)
MASK = ((25, 70), (120, 255), 96)    # (le masque : de la clarté 25 à 70, de 120 à 255 ; sur la face du comptoir)


def col_X(x, Z):                     # (la colonne x de la rue, à la profondeur Z : son X)
    return (x - VX) * Z / F


def lab(rgb):
    c = np.clip(np.asarray(rgb, float), 0, 255) / 255.0
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = c @ M.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def palette(P, k, per=500):
    """une palette de k couleurs tirée de P : autant de pixels de chaque tranche de clarté (les clairs, rares, comptent), puis
    leurs k moyennes (k-means, départ fixe : la même palette à chaque fois)"""
    P = np.asarray(P, float); L = lab(P); o = np.lexsort((L[:, 2], L[:, 1], L[:, 0])); P, L = P[o], L[o]
    pick = []
    for a in range(0, 100, 10):
        idx = np.where((L[:, 0] >= a) & (L[:, 0] < a + 10))[0]
        pick += list(idx[np.linspace(0, len(idx) - 1, min(per, len(idx))).astype(int)]) if len(idx) else []
    P, L = P[pick], L[pick]
    C = L[np.linspace(0, len(L) - 1, k).astype(int)].copy()
    for _ in range(50):
        a = np.argmin(((L[:, None] - C[None]) ** 2).sum(2), 1)
        for j in range(k):
            if (a == j).any(): C[j] = L[a == j].mean(0)
    a = np.argmin(((L[:, None] - C[None]) ** 2).sum(2), 1)
    return np.array([P[a == j].mean(0) for j in range(k) if (a == j).any()])


def nearest(c, pal):
    d = ((lab(c)[:, None] - lab(pal)[None]) ** 2).sum(2)
    return np.argmin(d, 1)


def around(xs, ys, v):
    """la moyenne et l'écart de v sur chaque pixel du verre et ses voisins de verre (3 x 3)"""
    zx0, zy0, zx1, zy1 = ZONE
    S1 = np.zeros((zy1 - zy0 + 2, zx1 - zx0 + 2)); S2 = S1.copy(); N = S1.copy()
    S1[ys - zy0 + 1, xs - zx0 + 1] = v; S2[ys - zy0 + 1, xs - zx0 + 1] = v * v; N[ys - zy0 + 1, xs - zx0 + 1] = 1
    box = lambda A: sum(A[1 + a + ys - zy0, 1 + b + xs - zx0] for a in (-1, 0, 1) for b in (-1, 0, 1))
    n = box(N); m = box(S1) / n
    return m, np.sqrt(np.maximum(box(S2) / n - m * m, 0))


def shape_ok(kind, s, t):
    """la silhouette d'un objet dans sa boîte de l'image (s de -1 à 1 en travers, t de 0 en haut à 1 en bas)"""
    if kind == 'bol':
        return np.abs(s) <= np.where(t < 0.16, 1.0, 1.0 - 0.42 * np.clip((t - 0.16) / 0.84, 0, 1) ** 1.8)
    if kind == 'bouteille':
        return np.abs(s) <= np.where(t < 0.3, 0.38, 1.0)
    if kind == 'lanterne':
        body = 0.72 + 0.28 * np.sin(np.pi * np.clip((t - 0.08) / 0.84, 0, 1))
        return np.abs(s) <= np.where((t < 0.08) | (t > 0.92), 0.5, body)
    return np.abs(s) <= 1.0


def glass_bot(x):                    # (la dernière rangée des vitres du peintre : au-dessus de leur lisière claire du bas)
    return int(np.round(VY + BAS_RAYON * (x - VX) - 0.5)) - 1


def glass_columns():
    """les vitres de la devanture (tools/ichiraku_front.py : le panneau fixe et la porte, leur verre entre leurs montants et
    leurs traverses, de sous la traverse haute à la traverse du soubassement) : {colonne : (première rangée, dernière)}"""
    import ichiraku_front as FR
    b = FR.BOX; m = FR.glass_mask(b); out = {}
    for j in range(m.shape[1]):
        ys = np.nonzero(m[:, j])[0]
        if len(ys): out[b[0] + j] = (b[1] + int(ys.min()), b[1] + int(ys.max()))
    return out


def hems():
    """la dernière rangée de l'ourlet du noren (son image au repos), colonne par colonne de la vitrine"""
    nr = I.load(NOREN[0], 'RGBA')[:NOREN[4], :NOREN[3], 3]
    return {x: NOREN[2] + int(np.max(np.where(nr[:, x - NOREN[1]] > 0)[0])) for x in range(NOREN[1], NOREN[1] + NOREN[3])
            if (nr[:, x - NOREN[1]] > 0).any()}


def glass_pixels():
    """le verre : les vitres de la devanture (glass_columns), colonne par colonne ; sous l'ourlet du noren, ce qu'on en voit"""
    hem = hems()
    pix = [(x, y) for x, (a, b) in sorted(glass_columns().items()) for y in range(a, b + 1)]
    return np.array(pix), hem


def painted_pixels(hem):
    """le verre des quatre vitres du peintre (PEINTES), sous l'ourlet : où sont pris les tons de son verre allumé et coupé"""
    (cols, (ta, tb)) = PEINTES
    return [(x, y) for a, b in cols for x in range(a, b + 1)
            for y in list(range(hem[x] + 1, ta + 1)) + list(range(tb, glass_bot(x) + 1))]


def reflet(xs, ys):
    """la part du reflet de la rue sur la glace, pixel par pixel : des traînées en biais (REFLET), pleines en leur milieu"""
    xs, ys = np.asarray(xs, float), np.asarray(ys, float)
    return sum(k * np.clip(1 - np.abs(xs - p * (ys - VY) - c) / w, 0, 1) * np.clip(np.minimum(ys - y0, y1 - ys) / 12, 0, 1)
               for p, c, w, k, y0, y1 in REFLET)


def mirror_source(xs, ys):
    """where the street shows what each glass pixel (xs, ys) reflects: the scene turned over the panes' plane X_D in the street's
    camera; (columns, rows) in the street, the same rows. Its reflected ray meets the opposite facades' plane (OPPOSITE) or,
    below the horizon, the ground first"""
    import ichiraku_front as FR
    XD = X_F + FR.REVEAL
    xc, yc = np.asarray(xs, float) + 0.5, np.asarray(ys, float) + 0.5
    Zp = F * XD / (xc - VX)                                                  # (the pane's own depth)
    Zf = Zp * (2 * XD - OPPOSITE) / XD                                       # (the opposite facade)
    Zg = np.where(yc > VY + 1e-6, EYE * F / np.maximum(yc - VY, 1e-6), np.inf)   # (the ground)
    Z = np.minimum(Zf, Zg); X = XD * (2 - Z / Zp)
    return VX + F * X / Z - 0.5, np.asarray(ys, float)


def skin(pix, layer, k_refl=1.0, k_fx=1.0):
    """la lumière que la glace ajoute à chaque pixel de verre (pix) : la rue d'en face reflétée (prise sur layer, ses couleurs
    du calque), le lustre, le fil clair des bords, les gouttes, la buée ; k_refl : le reflet plus ou moins fort (fermée, coupée) ;
    k_fx : le lustre, le fil et les gouttes (sur une vitre sombre, il en faut moins : SKIN['dark'])"""
    from scipy.ndimage import gaussian_filter, map_coordinates
    import ichiraku_front as FR
    xs, ys = pix[:, 0].astype(float), pix[:, 1].astype(float)
    blur = np.stack([gaussian_filter(layer[..., c], MIRROR_BLUR) for c in range(3)], -1)
    xq, yq = mirror_source(xs, ys)
    refl = np.stack([map_coordinates(blur[..., c], [yq, xq], order=1, mode='nearest') for c in range(3)], -1)
    cols = glass_columns(); hem = hems(); bot = np.array([cols[int(x)][1] for x in xs])
    top = np.array([max(cols[int(x)][0], hem.get(int(x), 0) + 1) for x in xs])    # (from under the noren: what is seen of it)
    t = np.clip((ys - top) / np.maximum(bot - top, 1), 0, 1)
    on = {(int(x), int(y)) for x, y in pix}
    d = np.full(len(pix), 9.0)                                   # (la distance au bord de sa vitre, jusqu'à 8)
    for r in range(8, 0, -1):
        near = np.array([any((int(x) + a, int(y) + b) not in on for a, b in ((r, 0), (-r, 0), (0, r), (0, -r))) for x, y in pix])
        d[near] = r
    a = SKIN['refl'] * k_refl * (1 - SKIN['top'] * t) * (1 + SKIN['edge'] * np.exp(-(d - 1) / 2.5))
    ppl = np.ones(len(pix))
    for x0, y0, x1, y1 in PEOPLE:
        ppl = np.where((xs >= x0) & (xs < x1) & (ys >= y0) & (ys < y1), SKIN['people'], ppl)
    light = refl * (a * ppl)[:, None]
    light += np.array(REFLET_C)[None] * (k_fx * ppl * reflet(xs, ys))[:, None]   # (le lustre, moindre sur les gens)
    rr, rg, rb, ra = SKIN['rim']                                  # (le fil clair des bords : le haut et la gauche, vers la rue et
    ew = np.array([max(w for (a_, b_), w in zip(((0, -1), (-1, 0), (1, 0), (0, 1)), RIM_SIDES)   # ses lampes, plus que la droite et
                       if (int(x) + a_, int(y) + b_) not in on) if d[i] == 1 else 0.0          # le bas)
                   for i, (x, y) in enumerate(pix)])
    light += np.array((rr, rg, rb))[None] * (k_fx * ra * ew)[:, None]
    rng = np.random.default_rng(31)                               # (les gouttes : plutôt vers le bas, une pointe claire, son
    at = {(int(x), int(y)): i for i, (x, y) in enumerate(pix)}    # ventre plus doux sous elle ; aucune sur les gens)
    pd = (0.3 + t) * (ppl == 1)
    for i in rng.choice(len(pix), SKIN['drops'], replace=False, p=pd / pd.sum()):
        light[i] += np.array(REFLET_C) * SKIN['drop'] * k_fx
        j = at.get((int(xs[i]), int(ys[i]) + 1))
        if j is not None: light[j] += np.array(REFLET_C) * SKIN['drop'] * k_fx * 0.4
    fr, fg, fb, fa, fh, fw = SKIN['fog']                          # (la buée : aux coins du bas de chaque vitre, en taches)
    up = np.clip((ys - (bot - fh)) / fh, 0, 1)
    lft = np.array([min(r for r in range(1, 90) if (int(x) - r, int(y)) not in on) for x, y in pix])
    rgt = np.array([min(r for r in range(1, 90) if (int(x) + r, int(y)) not in on) for x, y in pix])
    side = np.clip(1 - (np.minimum(lft, rgt) - 1) / fw, 0, 1)
    n = gaussian_filter(np.random.default_rng(57).normal(0, 1, (200, 120)), 1.2); n = (n - n.min()) / (n.max() - n.min())
    fog = fa * up * side * (0.5 + n[(ys - 500).astype(int) % 200, (xs - 1140).astype(int) % 120])
    light += np.array((fr, fg, fb))[None] * fog[:, None]
    return np.clip(light, 0, 255)


def render(src, pix):
    """chaque pixel du verre pris sur SS x SS rayons de l'œil : ce que chacun rencontre le premier dans la maquette (sa couleur,
    sa surface)"""
    o = (np.arange(SS) + 0.5) / SS
    ox, oy = np.meshgrid(o, o)
    DX = (pix[:, 0:1] + ox.ravel()[None] - VX) / F; DY = -(pix[:, 1:2] + oy.ravel()[None] - VY) / F
    sh = DX.shape
    Zh = np.full(sh, np.inf); col = np.zeros(sh + (3,)); sid = np.zeros(sh, int)
    def hit(Z, ok, c, k):
        nonlocal Zh, sid
        m = ok & (Z < Zh) & (Z > 0)
        Zh = np.where(m, Z, Zh); sid = np.where(m, k, sid)
        col[m] = np.broadcast_to(np.asarray(c, float), sh + (3,))[m]
    def look(img, u, v):
        return img[np.clip(np.floor(v).astype(int), 0, img.shape[0] - 1), np.clip(np.floor(u).astype(int), 0, img.shape[1] - 1)]
    def plane_h(hh):                                                         # (un plan horizontal à la hauteur hh)
        down = (hh - EYE) / np.where(DY != 0, DY, 1e-9)
        return np.where(down > 0, down, np.inf)
    def rod(p0, p1, rr):                                                     # (un barreau : le segment p0 p1, son rayon)
        p0, p1 = np.array(p0), np.array(p1); dv = np.stack([DX, DY, np.ones(sh)], -1)
        n = np.linalg.norm(dv, axis=-1, keepdims=True); dv = dv / n
        e = p1 - p0; ee = e @ e; de = dv @ e; dp = dv @ p0; ep = e @ p0
        den = ee - de * de
        s = np.clip((ee * dp - de * ep) / np.where(den > 1e-12, den, 1e-12), 0, None)
        t = np.clip((de * s - ep) / ee, 0, 1)
        q = p0 + t[..., None] * e; dist = np.linalg.norm(s[..., None] * dv - q, axis=-1)
        Z = (s[..., None] * dv)[..., 2]
        return np.where(dist <= rr, Z, np.inf), t
    def cyl(cx, cz, rr):                                                     # (un cylindre d'aplomb : son axe, son rayon)
        bb = -2 * (DX * cx + cz); cc = cx * cx + cz * cz - rr * rr; aa = DX * DX + 1
        disc = bb * bb - 4 * aa * cc
        return np.where(disc >= 0, (-bb - np.sqrt(np.maximum(disc, 0))) / (2 * aa), np.inf)

    # le mur du bout, de face : l'image du propriétaire, à l'échelle K_WALL
    X_POT = col_X(POT[1], Z_E)
    Z = np.full(sh, Z_E); X = DX * Z; h = EYE + DY * Z
    wall = look(src, POT[0] + (X - X_POT) * K_WALL, V_REF - (h - BACK_H) * K_WALL) * WALL_GAIN
    hit(Z, (h > 0) & (h < CEIL) & (X < X_F + D_ROOM), wall, 1)
    # le plafond, le sol, le mur d'en face (le long de la rue) : on ne les voit pas d'ici, mais ils ferment la boîte
    Zc = plane_h(CEIL); tc = np.clip((Zc - X_F / DX) / (Z_E - X_F / DX), 0, 1)[..., None]   # (le plafond, vu par le haut de la
    hit(Zc, (Zc < Z_E) & (DX * Zc < X_F + D_ROOM), np.array(CEIL_C) * (CEIL_K[0] + CEIL_K[1] * tc ** 1.5), 10)   # vitrine : les
                                                                             # lampes du fond l'éclairent, plus sombre vers la façade)
    Zf = plane_h(0.0); hit(Zf, (Zf < Z_E) & (DX * Zf < X_F + D_ROOM), np.array([50., 26., 18.]), 10)
    Zs = (X_F + D_ROOM) / DX; hit(Zs, (Zs < Z_E) & (EYE + DY * Zs > 0) & (EYE + DY * Zs < CEIL), np.array([70., 34., 22.]), 10)
    # le comptoir de travail du fond (caché par celui des clients)
    Zb = np.full(sh, Z_E - BACK_D); hit(Zb, (EYE + DY * Zb >= 0) & (EYE + DY * Zb <= BACK_H), np.array([60., 30., 20.]), 10)
    # le comptoir des clients : son dessus, son arête, sa face de planches (sous l'arête à l'ombre, plus sombre vers le sol), le
    # retrait du pied, la barre pour les pieds
    pw, pg, (pu0, pv0, pu1, pv1), ptop, pbot = PLANK
    Z = np.full(sh, Z_C); X = DX * Z; h = EYE + DY * Z
    q = X / pw; k = np.floor(q).astype(int); fr = q - k
    tone = np.array([src[pv0:pv1, (pu0 + 37 * j) % (pu1 - 8):(pu0 + 37 * j) % (pu1 - 8) + 6].mean() for j in range(400)])
    tone = tone / tone.mean()
    up = np.clip((h - KICK[0]) / (CTR_H - LIP - KICK[0]), 0, 1)
    ptop, pbot = np.array(ptop), np.array(pbot)
    face = (pbot + (ptop - pbot) * up[..., None] ** 0.8) * (tone[k % 400] ** 0.6)[..., None]
    face = face * np.where(h > CTR_H - LIP - 0.035, 0.62, 1.0)[..., None]
    lipc = np.array([235., 140., 70.])
    on = (h >= KICK[0]) & (h <= CTR_H)
    hit(Z, on & (h > CTR_H - LIP), lipc, 2)
    hit(Z, on & (h <= CTR_H - LIP) & (fr > pg / pw), face, 2)
    hit(Z, on & (h <= CTR_H - LIP) & (fr <= pg / pw), face * 0.72, 11)
    Zk = np.full(sh, Z_C + KICK[1]); hk = EYE + DY * Zk
    hit(Zk, (hk >= 0) & (hk < KICK[0]), np.array([30., 13., 9.]), 2)
    Zt = plane_h(CTR_H)
    hit(Zt, (Zt >= Z_C) & (Zt <= Z_C + CTR_D), np.array([240., 150., 75.]), 3)
    Zr = np.full(sh, Z_C - RAIL[2]); hr = EYE + DY * Zr
    rail = np.where((hr > RAIL[0])[..., None], np.array([205., 135., 72.]), np.array([96., 52., 30.]))
    hit(Zr, np.abs(hr - RAIL[0]) <= RAIL[1], rail, 4)
    # les objets sur le comptoir, de face, posés sur son dessus (leur échelle K_OBJ : un bol de 21 cm)
    for kind, (u0, v0, u1, v1), xc in OBJETS:
        Zo = np.full(sh, Z_C + OBJ_Z); Xo = DX * Zo; ho = EYE + DY * Zo
        u = (u0 + u1) / 2 + (Xo - col_X(xc, Zo)) * K_OBJ; v = v1 - (ho - CTR_H) * K_OBJ
        s = (u - (u0 + u1) / 2) / ((u1 - u0) / 2); t = (v - v0) / (v1 - v0)
        hit(Zo, (t >= 0) & (t <= 1) & shape_ok(kind, s, t), look(src, u, v) * 1.1, 5)
    # les tabourets devant le comptoir : un coussin rond (son dessus pris dans la lumière, son flanc rouge, son dessous à
    # l'ombre), quatre pieds (ceux de derrière plus sombres), l'anneau pour les pieds
    S = STOOL
    for xs in STOOLS:
        Zs0 = Z_C - S['dz']; Xs = col_X(xs, Zs0)
        Zc = cyl(Xs, Zs0, S['r']); hc = EYE + DY * Zc
        rel = (S['top'] - hc) / S['th']
        seat = np.where((rel < 0.22)[..., None], np.array([226., 112., 72.]),
                        np.where((rel < 0.8)[..., None], np.array([158., 42., 34.]), np.array([84., 22., 22.])))
        hit(Zc, (rel >= 0) & (rel <= 1), seat, 6)
        Ztop = plane_h(S['top']); Xt = DX * Ztop
        hit(Ztop, (Xt - Xs) ** 2 + (Ztop - Zs0) ** 2 <= S['r'] ** 2, np.array([210., 96., 64.]), 6)
        for ex, ez in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            Zl, tl = rod((Xs + ex * S['at'], S['top'] - S['th'] - EYE, Zs0 + ez * S['at']),
                         (Xs + ex * S['at'], -EYE, Zs0 + ez * S['at']), S['leg'])
            hit(Zl, np.isfinite(Zl), np.array([170., 98., 54.]) * (1.0 - 0.5 * tl[..., None]) * (1.0 if ez < 0 else 0.6), 7)
        Zg = cyl(Xs, Zs0, S['at'] * 1.414); hg = EYE + DY * Zg
        hit(Zg, np.abs(hg - S['ring']) <= 0.011, np.array([128., 74., 42.]), 7)
    # la lanterne, pendue au-dessus du comptoir (celle de l'image, sa largeur en vrai)
    (u0, v0, u1, v1), xl, wl, hb, dzl = LANTERN
    Zl = np.full(sh, Z_C + dzl); Xl = DX * Zl; hl = EYE + DY * Zl
    kl = (u1 - u0) / wl
    u = (u0 + u1) / 2 + (Xl - col_X(xl, Zl)) * kl; v = v1 - (hl - hb) * kl
    s = (u - (u0 + u1) / 2) / ((u1 - u0) / 2); t = (v - v0) / (v1 - v0)
    hit(Zl, (t >= 0) & (t <= 1) & shape_ok('lanterne', s, t), look(src, u, v) * 1.12, 8)
    hit(Zl, (v < v0) & (np.abs(Xl - col_X(xl, Zl)) < 0.006), np.array([40., 20., 14.]), 9)
    return col, sid


def reduce(col, sid):
    """au pixel entier : la surface qui en tient le plus (un barreau, un joint dès 30 %) ; dedans, là où ses rayons font deux
    groupes nets, la couleur du groupe qui en tient 60 % ou plus, sinon leur moyenne ; un éclat (le cœur d'une lanterne, le
    bord d'un bol) gardé dans son pixel : la moyenne tirée vers ses rayons les plus clairs. Rend aussi la surface de chacun"""
    out = np.zeros((col.shape[0], 3)); acc = np.zeros(col.shape[0], bool); surf = np.zeros(col.shape[0], int)
    for i in range(col.shape[0]):
        ids, n = np.unique(sid[i], return_counts=True)
        thin = [k for k, c in zip(ids, n) if k in (7, 9, 11) and c >= 0.3 * sid.shape[1]]
        k = surf[i] = thin[0] if thin else ids[np.argmax(n)]
        c = col[i][sid[i] == k]
        L = c @ I.LUM
        m = c.mean(0)
        if len(c) >= 4 and L.max() - L.min() > 40:
            sel = L > np.median(L)
            for _ in range(6):
                ca, cb = c[~sel].mean(0) if (~sel).any() else m, c[sel].mean(0) if sel.any() else m
                sel = ((c - cb) ** 2).sum(1) < ((c - ca) ** 2).sum(1)
            a, b = c[~sel], c[sel]
            if len(a) and len(b):
                big, small = (a, b) if len(a) >= len(b) else (b, a)
                if len(big) >= 0.6 * len(c) and abs((big @ I.LUM).mean() - (small @ I.LUM).mean()) > 35:
                    m = big.mean(0)
        nb = max(1, len(L) // 8); top = np.sort(L)[-nb:]
        if top.mean() > 200 and top.mean() - m @ I.LUM > 60:
            m = 0.45 * m + 0.55 * c[L >= top[0]].mean(0); acc[i] = True
        out[i] = m
    return out, acc, surf


def compute(layers=None):
    """la vitrine : chacun de ses pixels de verre (pix), allumé (lit), coupé (cut, la glace et son reflet compris), sa part du
    masque (a_gl) ; la palette de la boutique (pal), les éclats (acc), les calques au commit BEFORE (B), ceux d'où la glace prend
    la rue qu'elle reflète (layers : ceux de la chaîne, sinon ceux d'assets/)"""
    if layers is None: layers = [I.load(n, m) for n, m in NAMES]
    src = np.asarray(Image.open(SRC).convert('RGB')).astype(float)
    B = [I.load(n, m, BEFORE) for n, m in NAMES]
    zx0, zy0, zx1, zy1 = ZONE
    pix, hem = glass_pixels()
    xs, ys = pix[:, 0], pix[:, 1]
    col, sid = render(src * np.array(TINT), pix)
    rgb, acc, surf = reduce(col, sid)
    painted = painted_pixels(hem)

    # la palette de la boutique : son verre allumé (BEFORE, ses quatre vitres), le noren et les lanternes allumés
    P = [B[0][y, x, :3] for x, y in painted if y >= 599]
    nr = I.load(NOREN[0], 'RGBA'); n1 = nr[NOREN[4]:2 * NOREN[4], :NOREN[3]]; P += list(n1[n1[..., 3] > 250][:, :3])
    la = I.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'edits', 'lanterns_before.webp'), 'RGBA')   # (the paper lanterns' atlas this was built from)
    for r in (1, 4):
        c = la[r * 84:(r + 1) * 84, 15 * 48:16 * 48]; P += list(c[c[..., 3] > 250][:, :3])
    pal = palette(P, 40)

    # la lumière : le haut à l'ombre du noren, la vapeur au-dessus de la marmite plus claire
    d = ys - np.array([hem[x] for x in xs])                                  # (au-dessus de l'ourlet, derrière le noren : rien)
    rgb = rgb * np.where(d >= 1, np.array(HAUT + (1.0,))[np.clip(d, 1, len(HAUT) + 1) - 1], 1.0)[:, None]
    sx, sb, sh_, sw, sk, sc = STEAM
    w = sk * np.exp(-((xs - sx) / sw) ** 2) * np.clip((sb - ys) / 3, 0, 1) * np.clip(1 - (sb - ys) / sh_, 0, 1) ** 0.7
    rgb = rgb * (1 - w[:, None]) + np.array(sc) * w[:, None]

    # le grain du peintre : une tache par pixel, fixe ; plein sur ce qui est uni (la face du comptoir), léger sur ce qui est
    # chargé ; jamais un saut de plus d'une marche de la palette
    Lsd = around(xs, ys, rgb @ I.LUM)[1]
    g = np.random.default_rng(1915).normal(0, 1, (zy1 - zy0 + 2, zx1 - zx0 + 2))
    g = 0.7 * g[1:-1, 1:-1] + 0.15 * (g[:-2, 1:-1] + g[1:-1, :-2] + g[2:, 1:-1] + g[1:-1, 2:])
    g = (g / g.std())[ys - zy0, xs - zx0]
    amp = GRAIN * (0.3 + 0.7 * np.clip(1 - Lsd / 16, 0, 1))
    i0 = nearest(rgb, pal); i1 = nearest(np.clip(rgb * np.exp(amp * g)[:, None], 0, 255), pal)
    far = ((lab(pal[i0]) - lab(pal[i1])) ** 2).sum(1) > 14 ** 2
    lit = pal[np.where(acc | far, i0, i1)]
    Ll = lit @ I.LUM

    # coupée (street_unlit) : le verre sombre de la coupure, du bleu nuit de son verre le plus sombre à son plus clair (CUT : ses
    # centiles) selon la clarté de la pièce allumée, à ses couleurs ; son grain plus léger, d'une marche au plus
    Cb = np.array([B[1][y, x, :3] for x, y in painted if y >= 599]); Lb = Cb @ I.LUM
    lo, hi = Cb[Lb <= np.percentile(Lb, CUT[0])].mean(0), Cb[Lb >= np.percentile(Lb, CUT[1])].mean(0)
    t = np.clip((Ll * np.where(surf == 8, 0.45, 1.0) - 30) / 170, 0, 1) ** 0.9   # (la lanterne éteinte)
    cut_c = lo + (hi - lo) * t[:, None]
    cpal = palette(Cb, 20)
    j0 = nearest(cut_c, cpal); j1 = nearest(np.clip(cut_c * np.exp(0.5 * amp * g)[:, None], 0, 255), cpal)
    cut = cpal[np.where(((lab(cpal[j0]) - lab(cpal[j1])) ** 2).sum(1) > 6 ** 2, j0, j1)]
    cut = np.clip(cut + skin(pix, layers[1][..., :3], SKIN['cut'], SKIN['dark']), 0, 255)   # (la glace : la rue coupée qu'elle reflète)

    # fermée (shop_off, posé à 0,88) : tout le verre couvert de son bleu nuit, la pièce allumée n'y passe qu'à 12 %. Le masque
    # du verre (ramen_glass : les ombres de Teuchi et du client, la lumière de la pièce qui respire, la vapeur) : plein sur ce
    # qu'on voit au-dessus du comptoir, un peu moins sur le plus sombre (sa clarté prise sur ses voisins : pas de pixel isolé) ;
    # sur la face du comptoir, sous les figures coupées à sa hauteur, une part égale (la lumière seule)
    Ls = around(xs, ys, Ll)[0]
    a_gl = np.where(ys <= CTR_ROW, np.interp(Ls, MASK[0], MASK[1]), MASK[2])
    return dict(pix=pix, lit=lit, cut=cut, a_gl=a_gl, pal=pal, acc=acc, B=B, layers=layers)


def lay(V, city, unlit):
    """la vitrine dans les deux calques (city : allumée, unlit : coupée ; RGBA, en place) : son verre, et les arêtes claires
    des montants du cadre contre lui à la lumière de la nouvelle pièce ; rend les pixels faits"""
    pix, old = V['pix'], V['B'][0]
    for i, (x, y) in enumerate(pix):
        city[y, x, :3] = V['lit'][i]; unlit[y, x, :3] = V['cut'][i]
    k5 = np.ones(5) / 5
    sm = lambda v: np.convolve(np.pad(v, 2, mode='edge'), k5, 'valid')
    for ex, gx in ARETES:
        rows = [y for x, y in pix if x == gx]
        new = np.array([city[y, gx, :3] @ I.LUM for y in rows]); was = np.array([old[y, gx, :3] @ I.LUM for y in rows])
        r = np.clip(sm(new) / np.maximum(sm(was), 1), 0.45, 1.2)
        for y, rr in zip(rows, r): city[y, ex, :3] = np.round(old[y, ex, :3] * rr)
    return [tuple(p) for p in pix] + [(ex, y) for ex, gx in ARETES for x, y in pix if x == gx]


BOX = (VITRE[0] - 1, 500, VITRE[1] + 2, 700)   # (la zone 'vitrine' de tools/redraw_zones.py : la vitrine et les arêtes du cadre)


def draw(city, unlit, box=BOX):
    """la zone 'vitrine' de tools/redraw_zones.py, la dernière : la vitrine posée sur les calques tels que les zones d'avant
    les laissent (leurs pixels du peintre gardent les vitres d'avant : elles s'y règlent comme avant) ; rend ce qui a changé"""
    was = city.copy(), unlit.copy()
    lay(compute((city, unlit)), city, unlit)
    return (np.abs(city - was[0]).max(-1) > 0) | (np.abs(unlit - was[1]).max(-1) > 0)


def main():
    prev = sys.argv[sys.argv.index('--preview') + 1] if '--preview' in sys.argv else None
    V = compute(); pix, pal, acc, B = V['pix'], V['pal'], V['acc'], V['B']
    xs, ys = pix[:, 0], pix[:, 1]; a_gl = V['a_gl']
    zx0, zy0, zx1, zy1 = ZONE
    Lc = [I.load(n, m) for n, m in NAMES]
    so = np.asarray(Image.open(SO_BEFORE).convert('RGBA')).copy(); gl = I.load('ramen_glass.webp', 'RGBA', BEFORE)
    lay(V, *Lc)
    nr0 = I.load(NOREN[0], 'RGBA')[:NOREN[4], :NOREN[3], 3]
    for x in range(zx0, min(zx1, GLASS[0] + gl.shape[1])):                    # (le masque n'est que sur le verre : rien sur le
        c = x - NOREN[1]                                                     # cadre, la lisière du bas ; la vitrine, toute sa
        if VITRE[0] <= x <= VITRE[1]: top = GLASS[1]                         # colonne, son verre posé ensuite)
        else: top = NOREN[2] + int(np.max(np.where(nr0[:, c] > 0)[0])) + 1 if 0 <= c < NOREN[3] and nr0[:, c].max() else 590
        gl[top - GLASS[1]:zy1 - GLASS[1], x - GLASS[0], 3] = 0
    import ichiraku_front as FR                                              # (la devanture fermée : ses faces sans la lumière
    fx, fy, fc = FR.shut_pixels(Lc[0])                                       # de la boutique, sur la porte et la marche ; le
    b = FR.BOX                                                               # reste de sa boîte rendu à la rue ; l'image
    if so.shape[0] < b[3] - SHOP_OFF[1]:                                     # descend jusqu'au trottoir)
        so = np.concatenate([so, np.zeros((b[3] - SHOP_OFF[1] - so.shape[0],) + so.shape[1:], so.dtype)], 0)
    m = FR.glass_mask(b)
    for name, c in FR.faces(): m |= FR.raster(c, None, b)
    yy, xx = np.nonzero(m); yy, xx = yy + b[1] - SHOP_OFF[1], xx + b[0] - SHOP_OFF[0]
    ok = (yy >= 0) & (yy < so.shape[0]) & (xx >= 0) & (xx < so.shape[1]); so[yy[ok], xx[ok]] = 0
    yy, xx = fy - SHOP_OFF[1], fx - SHOP_OFF[0]; ok = (yy >= 0) & (yy < so.shape[0]) & (xx >= 0) & (xx < so.shape[1])
    so[yy[ok], xx[ok], :3] = np.clip(np.round(fc[ok]), 0, 255); so[yy[ok], xx[ok], 3] = 255
    dark = np.clip(np.array((14.0, 9.0, 22.0))[None] + skin(pix, Lc[0][..., :3], SKIN['shut'], SKIN['dark']), 0, 255)   # (un miroir sombre)
    sk = np.zeros(gl.shape[:2] + (4,)); lt = skin(pix, Lc[0][..., :3])                # (allumée : la glace, ajoutée par street.js)
    for i, (x, y) in enumerate(pix):
        so[y - SHOP_OFF[1], x - SHOP_OFF[0]] = tuple(np.round(dark[i]).astype(int)) + (255,)
        if 0 <= y - GLASS[1] < gl.shape[0]:
            gl[y - GLASS[1], x - GLASS[0]] = (255, 255, 255, a_gl[i]); sk[y - GLASS[1], x - GLASS[0]] = tuple(lt[i]) + (255,)

    print('façade à X_F %.2f m de l\'œil ; vitrine de Z %.2f à %.2f m ; comptoir à Z %.2f m (dessus à %.2f m, rangée %d) ; mur du '
          'bout à Z %.2f m (%.2f m derrière la porte), %.1f px par mètre ; pièce de %.1f m de fond | %d pixels de verre, %d éclats, '
          'palette %d couleurs' % (X_F, F * X_F / (VITRE[0] - VX), F * X_F / (VITRE[1] - VX), Z_C, CTR_H, CTR_ROW, Z_E,
                                   Z_E - F * X_F / (VITRE[0] - VX), F / Z_E, D_ROOM, len(pix), acc.sum(), len(pal)))
    if prev:
        for k, im in (('lit', Lc[0]), ('cut', Lc[1])):
            Image.fromarray(np.clip(im[495:705, 1140:1240, :3], 0, 255).astype(np.uint8)).resize((800, 1680), Image.NEAREST).save(os.path.join(prev, k + '_x8.png'))
        bl = Lc[0][..., :3].copy(); sa = so[..., 3:] / 255 * 0.88
        h_ = so.shape[0]; bl[448:448 + h_, 1112:1112 + 164] = bl[448:448 + h_, 1112:1112 + 164] * (1 - sa) + so[..., :3] * sa
        lt_ = bl.copy(); lt_[520:690, 1150:1230] = np.clip(Lc[0][520:690, 1150:1230, :3] + sk[..., :3] * sk[..., 3:] / 255 * 0.55, 0, 255)
        Image.fromarray(np.clip(lt_[495:705, 1140:1240], 0, 255).astype(np.uint8)).resize((800, 1680), Image.NEAREST).save(os.path.join(prev, 'lit_skin_x8.png'))
        Image.fromarray(np.clip(bl[495:705, 1140:1240], 0, 255).astype(np.uint8)).resize((800, 1680), Image.NEAREST).save(os.path.join(prev, 'shut_x8.png'))
        ga = np.zeros((185, 100, 3)); ga[:170, 10:90] = gl[:, :, 3:]
        Image.fromarray(ga.astype(np.uint8)).resize((800, 1480), Image.NEAREST).save(os.path.join(prev, 'mask_x8.png'))
        Image.fromarray(np.repeat(np.repeat(pal[None].astype(np.uint8), 20, 0), 20, 1)).save(os.path.join(prev, 'palette.png'))
        return
    I.save(gl, 'ramen_glass.webp', 'RGBA'); I.save(sk, SKIN_OUT, 'RGBA')
    Image.fromarray(so.astype(np.uint8), 'RGBA').save(SO_BEFORE, 'WEBP', lossless=True, quality=100, method=6, exact=True)


if __name__ == '__main__':
    main()
