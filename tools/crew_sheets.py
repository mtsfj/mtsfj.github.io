#!/usr/bin/env python3
"""L'équipe du TranZit (Dempsey, Nikolai, Takeo, Richtofen) image par image, depuis les planches du propriétaire.

    python3 tools/crew_sheets.py                    (lit tools/src/planches/crew_<héros>_1_deplacements_v1|v2.png et
                                                     crew_<héros>_2_combat_v1|v2.png ; écrit assets/crew_<héros>.webp,
                                                     assets/crew_<héros>_flash.webp et la ligne CRW de assets/street.js ;
                                                     relancé, il écrit les mêmes octets)
    python3 tools/crew_sheets.py --only nikolai     (un seul ; la ligne CRW garde les autres tels qu'ils sont)
    python3 tools/crew_sheets.py --preview DOSSIER  (en plus : chaque héros, toutes ses images coupées x4 (leur mouvement,
                                                     leur image de la planche, l'ancre, la bouche du canon), et ses visées
                                                     avec la lumière de l'éclair x4)
    python3 tools/crew_sheets.py --dry              (rien n'est écrit dans assets/)

Les planches : 1536 x 1024, fond blanc. deplacements : la marche (8, de trois quarts vers nous et vers la droite, l'arme en
travers), la descente d'une haute marche (4, de face) puis la montée d'une marche vue de dos (4), debout au repos (2) puis la
joie (4 ; Nikolai boit). combat : à genou, face à nous, la visée (8 : des directions, chacune visée puis recul), le
rechargement (8), à genou au repos (4). Takeo n'a pas de descente de face : sa deuxième rangée est vue de dos tout du long.

Pour chaque héros, les choix (HEROES) : la version de chaque rangée (v1 ou v2 : les proportions tenues d'une image à l'autre,
une coupe nette, le même homme, l'arme tenue de la même façon ; voir les notes de chacun), les images de chaque mouvement, les
directions de la visée et leurs images (visée, recul), la bouche du canon quand on ne peut pas la trouver seule (de face).

Le chemin, image par image :
- La figure sur le blanc : un pixel est de la figure s'il s'écarte du blanc (255 - min(r, g, b) > 40) ; les trous enfermés
  restent de la figure sauf les grands d'un blanc pur (le jour entre le bras et le corps) ; les rangées et les images trouvées
  par les bandes vides, les images qui se touchent (un fusil contre le coude de la voisine) recoupées à la colonne la plus
  creuse, les bouts détachés rendus à l'image la plus proche. Les couleurs ne viennent que du coeur de la figure (le masque
  rogné de 2 px) : le liseré blanchâtre du bord (le kaki clair de Takeo s'y fond) ne donne jamais sa couleur.
- Une échelle par rangée de planche (scales : les planches dessinent plus grandes leurs rangées de 6 ou 4 images), la même
  pour toutes ses images : debout au repos, H px (la taille du héros à la porte du bus, CRW.ppm 26,1 px/m : le modèle B x K,
  la taille de ce qui est debout dans la peinture, comme la horde et les zombies du bus (tools/zombie_sol.py) ; 45 à 47 px,
  1,72 à 1,80 m ; 0,6 du bus, sous le haut de sa porte) ; la
  marche, 0,97 H ; à genou au repos, K px (sa vraie hauteur à genou, ~0,7 de debout ; la tête y garde la taille qu'elle a
  debout, à un pixel près) ; le rechargement, 0,96 K.
- Une ligne de sol : le bas de chaque image sur la rangée ay (la dernière rangée de la figure est ay - 1), sauf là où le pied
  est sur le plancher du bus (+FLOOR px) ou entre les deux (la descente, la montée : leur hauteur dans HEROES). Le recalage
  en x : par la tête pour la marche, la descente et la montée (le corps avance d'un pas régulier, les pieds glissent dessous),
  par les appuis au sol (les 6 % du bas : le genou et le pied, ou les deux pieds) pour tout ce qui est immobile ; à la
  fraction de pixel près (pas de saut d'une image à l'autre).
- La taille de la scène par majorité (comme ZRM) : chaque pixel de la scène couvre 1/s x 1/s px de la planche ; il est plein
  si la figure en couvre la moitié, et prend la couleur qui en couvre le plus (les couleurs du héros rangées en 32 teintes sur
  toutes ses images) : la moyenne de ses pixels de cette teinte-là. Rien n'est lissé, aucune couleur n'est inventée.
- La nuit : les couleurs x EXPOSE (0,37 : la médiane de l'équipe à celle de la peinture autour d'elle).
- Le grain : tools/regrain.py (regrain_group), une seule famille de tons par héros pour toutes ses images (24 familles, le
  grain fin baké, les clairs sous la peinture voisine + 15 %, les poussières ôtées).
- L'éclair sur le tireur (crew_<héros>_flash.webp, la même grille ; ajouté par street.js en mélange additif, seulement dans
  la visée, le temps de l'éclair) : pour chaque image de visée, la lumière de la bouche du canon (muz) sur ses pixels, le
  visage, les mains, l'arme et le devant du buste, en 1 / (1 + (d / R)^2), chaude, prise tache par tache (regrain).
- Les tailles (LEVELS) : chaque image cuite à x 1 (à la porte du bus, 46 px debout), x 1,13 et x 1,26 (59 px, à 32 m), ensemble
  dans un atlas, une bande par taille, une seule famille de tons pour toutes (regrain) ; street.js prend la plus petite au
  moins aussi grande que lui là où il est et la ramène à sa taille en pixels entiers, par majorité (ZRM) : il grandit d'un
  pixel à la fois en venant vers nous, le même grain à toutes les tailles.
- La marche vers nous, le pied posé sur son pixel (comme celle de l'obaa-chan) : les planches dessinent la marche de face ou de
  trois quarts vers nous, presque sur place ; ils marchent donc vers nous, comme dessinés. Sur chaque image de marche, à chaque
  taille, ses pieds au sol (talon, pointe) ; d'une image à la suivante le corps va de côté de lv.ws px entiers (le moins qui
  pose un pied au sol de l'une sur un pied au sol de l'autre, à un pixel près, jamais en arrière ; sans pied commun l'autre se
  pose plus loin et le corps reste) ; le reste de WALK_V (1,2 m/s à la taille de la peinture ; x K en mètres de B, ceux de
  street.js) vers nous (vz) ; chaque image dure la longueur de son pas
  sur le sol, deux pas par seconde (CADENCE), bornée à TF (wtf). Dempsey vient à 18° de droit sur nous, Nikolai (sa marche
  v2) à 43°, Takeo à 8° (vers notre gauche : son miroir), Richtofen à 6°. Un pas vers nous, à 33 à 40 m, fait moins d'un
  pixel : le pied posé descend d'un pixel au plus.

Il faut Pillow, numpy, scipy.
"""
import argparse
import json
import os
import sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as nd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import regrain as RG                                                  # noqa: E402

SRC = os.path.join(ROOT, 'tools', 'src', 'planches')
ASSETS = os.path.join(ROOT, 'assets')
JSF = os.path.join(ASSETS, 'street.js')

ROWS = {'deplacements': ('walk', 'step', 'stand'), 'combat': ('aim', 'reload', 'kneel')}
SHEET_OF = {r: s for s, rs in ROWS.items() for r in rs}
EXPECT = {'deplacements': (8, 8, 6), 'combat': (8, 8, 4)}
FILE = {'deplacements': 'crew_%s_1_deplacements_%s.png', 'combat': 'crew_%s_2_combat_%s.png'}

TH = 40                     # (255 - min(r, g, b) au-dessus : la figure)
CORE = 2                    # (le coeur : le masque rogné de tant de px de la planche)
HOLE = (40, 10, 0.5)        # (un trou enfermé d'au moins 40 px dont la moitié est d'un blanc pur (écart < 10) : du jour, pas la figure)
PALETTE = 32                # (les teintes de la majorité)
EXPOSE = 0.37               # (la nuit : les couleurs des planches, peintes en plein jour, x 0,37 (r, g et b ensemble : la teinte
                            #  reste) ; la luminance médiane de l'équipe ~30, celle de la peinture autour d'eux (29) et de
                            #  l'équipe d'avant (21 à 34) ; le même pour les quatre : le kaki de Takeo plus clair que le manteau
                            #  de Richtofen, comme dessinés ; regrain ne comprime plus les clairs, déjà sous la cible)
FLOOR = 9                   # (le plancher du bus au-dessus de la chaussée, à la porte : DOOR.floor 78, BUS.ground 87)
from zombie_sol import facteur, CF, CEYE, CHZ                         # noqa: E402
K_PEINT = facteur()[0]      # (K : la taille de ce qui est debout dans la peinture, 1,10 fois le modèle B ; tools/zombie_sol.py)
ROW_DOOR = 648.5            # (le pied de la porte du bus, 40,4 m)
PPM = round(K_PEINT * (ROW_DOOR - CHZ) / CEYE, 1)   # (CRW.ppm : px par mètre à la porte, à la taille de la peinture : 23,76 en B
                            #  x 1,10 = 26,1 ; un homme de 1,80 m y fait 47 px, 0,6 du bus (77,5 px pour 3 m), comme la horde)
FLASH = dict(rgb=(255, 196, 128), peak=0.26, R=5.5, floor=0.02)     # (la lumière de l'éclair : couleur, force au canon, rayon, seuil)
CADENCE = 2.0               # (la marche : deux pas par seconde, le haut d'un pas d'homme (1,6 à 2) : un cycle de deux pas en 1 s)
WALK_V = 1.2                # (m/s : leur pas, vers nous ; le pas de côté que le dessin donne, le reste vers nous)
LEVELS = (1.0, 1.13, 1.26)  # (les tailles cuites : x 1 à la porte (46 px debout), jusqu'à x 1,26 (59 px), assez pour le plus proche :
                            #  Dempsey en lastStand, 8,2 m devant la porte (32,2 m : x 1,257) ; street.js prend la plus petite au moins
                            #  aussi grande que lui là où il est et la ramène à sa taille, en px entiers, par majorité ; jamais agrandie)
TF = (0.08, 0.3)            # (une image de la marche dure entre tant et tant de s)
KICKS = [0.0, 0.3]          # (la visée, le recul : H.kick au-dessus de 0,3 dans street.js)

# Les choix, héros par héros. ver : la version de chaque rangée. Une image : (rangée, colonne) ; dans down et rise,
# (rangée, colonne, hauteur du bas de l'image au-dessus du sol en px, dans l'embrasure[, version]).
# aims : (degrés de part et d'autre de droit sur nous, + vers notre droite ; visée ; recul) ; muz : la bouche du canon dans
# l'image de la planche (px depuis le coin de sa boîte) quand elle ne se trouve pas seule (de face) ; drop : l'image du
# rechargement où le chargeur (ou le clip) quitte l'arme ; cheer_u : les temps (fraction de la joie) d'une scène étirée.
HEROES = {
    # Dempsey : deplacements v2 (la marche l'arme en travers de la poitrine, comme demandé ; la joie qui monte : l'arme à la
    # hanche, à l'épaule, puis au-dessus de la tête, quand v1 l'a au-dessus de la tête dès la première image ; la descente,
    # le genou levé puis la réception), sauf la montée vue de dos (v1 : les genoux montent vraiment) ; combat v2 (chaque
    # direction visée puis son recul, le canon qui se relève ; en v1 la deuxième image de face est déjà tournée à droite et
    # ne fait pas un recul). Les deux versions coupent le bout du canon à la huitième image de la marche (le bord de la
    # planche) : un pixel du canon, gardé.
    'dempsey': dict(
        H=46, K=32, ver=dict(walk='v2', step='v2', stand='v2', aim='v2', reload='v2', kneel='v2'),
        walk=list(range(8)),
        down=[('stand', 0, FLOOR, True), ('step', 0, FLOOR, True), ('step', 1, 5, False), ('step', 2, 0, False), ('step', 3, 0, False)],
        rise=[('step', 4, 0, False, 'v1'), ('step', 5, 0, False, 'v1'), ('step', 6, 5, True, 'v1'), ('step', 7, FLOOR, True, 'v1')],
        stand=[0, 1], cheer=[2, 3, 4, 5],
        kneel=[('stand', 0), ('step', 2), ('kneel', 0)],
        aims=[(0, 0, 1), (55, 2, 3), (70, 4, 5), (85, 6, 7)], muz={0: [(82, 68), (93, 60)]},
        reload=list(range(8)), drop=2, idle=[0, 1, 2, 3]),
    # Nikolai : v1 partout, sauf la marche (v2 : son pied d'appui recule vraiment sous lui, 20 px le cycle contre 6 ; la
    # bouteille du même côté). La bouteille à sa hanche droite (à notre gauche) sur les deux planches v1 ; en v2 combat elle
    # change de côté d'une image à l'autre, et en v2 la joie (il boit) perd la PPSh. Sa visée : deux directions vers notre
    # gauche, deux vers notre droite ; les quatre images de « recul » de la planche sont toutes la même arme relevée vers
    # la droite : elles servent de recul aux deux de droite ; à gauche, pas de recul (l'image visée reste). Pas de visée
    # droit sur nous : son trois-quarts droit (4) en tient lieu (la horde vient sur notre droite de lui).
    'nikolai': dict(
        H=47, K=33, ver=dict(walk='v2', step='v1', stand='v1', aim='v1', reload='v1', kneel='v1'),
        walk=list(range(8)),
        down=[('stand', 0, FLOOR, True), ('step', 0, FLOOR, True), ('step', 1, 5, False), ('step', 2, 0, False), ('step', 3, 0, False)],
        rise=[('step', 4, 0, False), ('step', 5, 0, False), ('step', 6, 5, True), ('step', 7, FLOOR, True)],
        stand=[0, 1], cheer=[2, 3, 4, 5], cheer_u=[0, 0.1, 0.18, 0.82],
        kneel=[('stand', 0), ('step', 2), ('kneel', 0)],
        aims=[(-85, 0, 0), (-55, 2, 2), (30, 4, 5), (80, 6, 7)], muz={2: [(162, 82), None]},
        reload=list(range(8)), drop=2, idle=[0, 1, 2, 3]),
    # Takeo : v2 partout (le sabre dans son fourreau en travers du dos, un seul : en v1 combat il en a deux, un à chaque
    # épaule, à la moitié des visées ; les pattes de col rouges des deux planches v2). Sa deuxième rangée est vue de dos
    # sur les huit images (pas de descente de face) : sa descente, debout puis deux pas de sa marche, du plancher au sol ;
    # sa visée : de face, à notre gauche, à notre droite (les images 7 et 8 de la planche refont la visée de face).
    'takeo': dict(
        H=45, K=31, ver=dict(walk='v2', step='v2', stand='v2', aim='v2', reload='v2', kneel='v2'),
        walk=list(range(8)),
        down=[('stand', 0, FLOOR, True), ('walk', 1, FLOOR, True), ('walk', 2, 7, False), ('walk', 3, 5, False), ('walk', 4, 3, False),
              ('walk', 5, 1, False), ('stand', 1, 0, False)],
        rise=[('step', 4, 0, False), ('step', 5, 0, False), ('step', 6, 5, True), ('step', 7, FLOOR, True)],
        stand=[0, 1], cheer=[2, 3, 4, 5],
        kneel=[('stand', 0), ('kneel', 0)],
        aims=[(-60, 2, 3), (0, 0, 1), (60, 4, 5)], muz={1: [(77, 65), (74, 62)]},
        reload=list(range(8)), drop=2, idle=[0, 1, 2, 3]),
    # Richtofen : v1 partout (la sacoche et les taches du manteau aux mêmes places sur ses deux planches ; en v2 combat la
    # sacoche passe de l'autre côté), sauf la marche : v2, de trois quarts vers la droite (v1 marche de face, en allant à
    # droite il semble glisser de côté), sur ses sept premières images (la huitième est coupée par le bord de la planche :
    # l'épaule, le manteau, l'arme ; le cycle se referme de la septième à la première, pieds joints).
    'richtofen': dict(
        H=47, K=33, ver=dict(walk='v2', step='v1', stand='v1', aim='v1', reload='v1', kneel='v1'),
        walk=list(range(7)),
        down=[('stand', 0, FLOOR, True), ('step', 0, FLOOR, True), ('step', 1, 5, False), ('step', 2, 0, False), ('step', 3, 0, False)],
        rise=[('step', 4, 0, False), ('step', 5, 0, False), ('step', 6, 5, True), ('step', 7, FLOOR, True)],
        stand=[0, 1], cheer=[2, 3, 4, 5],
        kneel=[('stand', 0), ('step', 2), ('kneel', 0)],
        aims=[(0, 0, 1), (45, 2, 3), (65, 4, 5), (85, 6, 7)], muz={0: [(89, 71), (57, 49)], 1: [(147, 65), None]},
        reload=list(range(8)), drop=2, idle=[0, 1, 2, 3]),
}
ORDER = ['dempsey', 'nikolai', 'takeo', 'richtofen']


# ---- les planches : la figure sur le blanc, ses rangées, ses images
def cut_sheet(path, expect):
    a = np.asarray(Image.open(path).convert('RGB')).astype(np.int16)
    d = 255 - a.min(2)
    fg = d > TH
    lab, n = nd.label(~fg)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    sz = np.bincount(lab.ravel(), minlength=n + 1)
    white = np.bincount(lab.ravel(), (d < HOLE[1]).ravel().astype(float), minlength=n + 1)
    keep_bg = np.zeros(n + 1, bool)
    keep_bg[edge] = True
    keep_bg |= (sz >= HOLE[0]) & (white >= HOLE[2] * sz)
    keep_bg[0] = False
    fg |= ~keep_bg[lab] & (lab > 0)
    pr = fg.sum(1)
    rl, _ = nd.label(pr > 0)
    bands = [s[0] for s in nd.find_objects(rl) if s[0].stop - s[0].start > 60]
    while len(bands) < len(expect):                                   # (deux rangées qui se touchent : coupées à la rangée la plus creuse)
        k = max(range(len(bands)), key=lambda i: bands[i].stop - bands[i].start)
        b = bands.pop(k)
        lo, hi = b.start + (b.stop - b.start) // 4, b.stop - (b.stop - b.start) // 4
        c = lo + int(np.argmin(pr[lo:hi]))
        bands[k:k] = [slice(b.start, c), slice(c, b.stop)]
    frames = []
    for bi, b in enumerate(bands[:len(expect)]):
        sub = fg[b]
        cl, cn = nd.label(sub, structure=np.ones((3, 3)))
        szc = np.bincount(cl.ravel(), minlength=cn + 1)
        szc[0] = 0
        ref = np.sort(szc)[-min(cn, expect[bi])]
        comps = {i: cl == i for i in range(1, cn + 1) if szc[i] > 0.15 * ref}
        while len(comps) < expect[bi]:                                # (deux images qui se touchent : la colonne la plus creuse)
            k = max(comps, key=lambda i: np.ptp(np.nonzero(comps[i].any(0))[0]))
            M = comps.pop(k)
            xs = np.nonzero(M.any(0))[0]
            x0, x1 = xs.min(), xs.max()
            proj = M.sum(0)
            lo, hi = x0 + (x1 - x0) // 4, x1 - (x1 - x0) // 4
            c = lo + int(np.argmin(proj[lo:hi]))
            L, R = M.copy(), M.copy()
            L[:, c:] = False
            R[:, :c] = False
            comps[(k, 0)] = L
            comps[(k, 1)] = R
        keys = sorted(comps, key=lambda i: np.nonzero(comps[i].any(0))[0].mean())
        owner = np.zeros(sub.shape, np.int16)
        for j, k in enumerate(keys):
            owner[comps[k]] = j + 1
        _, (iy, ix) = nd.distance_transform_edt(owner == 0, return_indices=True)
        rest = sub & (owner == 0)
        owner[rest] = owner[iy[rest], ix[rest]]
        for j in range(len(keys)):
            M = owner == j + 1
            ys, xs = np.nonzero(M)
            y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
            m = np.zeros((y1 - y0, x1 - x0), bool)
            m[ys - y0, xs - x0] = True
            frames.append(dict(row=bi, col=j, box=(int(x0), int(y0 + b.start), int(x1), int(y1 + b.start)), m=m,
                               rgb=a[y0 + b.start:y1 + b.start, x0:x1].astype(np.uint8), d=d[y0 + b.start:y1 + b.start, x0:x1],
                               edge=bool(x0 == 0 or x1 == a.shape[1] or y0 + b.start == 0 or y1 + b.start == a.shape[0])))
    return frames


_SHEETS = {}


def sheet(hero, kind, ver):
    k = (hero, kind, ver)
    if k not in _SHEETS:
        p = os.path.join(SRC, FILE[kind] % (hero, ver))
        fr = cut_sheet(p, EXPECT[kind])
        got = [sum(1 for f in fr if f['row'] == r) for r in range(len(EXPECT[kind]))]
        if tuple(got) != EXPECT[kind]:
            sys.exit('%s : %s images par rangée, %s attendues' % (p, got, EXPECT[kind]))
        _SHEETS[k] = fr
    return _SHEETS[k]


def frame(hero, row, col, ver=None):
    kind = SHEET_OF[row]
    ver = ver or HEROES[hero]['ver'][row]
    fr = sheet(hero, kind, ver)
    ri = ROWS[kind].index(row)
    f = [q for q in fr if q['row'] == ri and q['col'] == col][0]
    return dict(f, hero=hero, kind=kind, ver=ver, name='%s.%s%d' % (ver, row, col))


# ---- la mesure d'une image
def core(f):
    """le coeur : le masque rogné de CORE px, sans un pixel presque blanc (un trou rempli, le liseré)"""
    return nd.binary_erosion(f['m'], iterations=CORE, border_value=0) & (f['d'] > TH)


def reg_head(m):
    """le recalage par la tête : le milieu des pixels de ses 12 % du haut (x, dans la boîte)"""
    ys, xs = np.nonzero(m)
    t = ys.min()
    sel = ys < t + 0.12 * (ys.max() - t + 1)
    return float(xs[sel].mean()) + 0.5


def reg_feet(m):
    """le recalage par les appuis : le milieu des pixels de ses 6 % du bas"""
    ys, xs = np.nonzero(m)
    b = ys.max()
    sel = ys > b - 0.06 * (b - ys.min() + 1)
    return float(xs[sel].mean()) + 0.5


# ---- la taille de la scène, par majorité
def spans(n_src, lo, step, n_out):
    """chaque pixel x de la planche couvre [(x - lo) / step, (x + 1 - lo) / step) en pixels de la scène (moins d'un : step > 1) :
    ses deux pixels de la scène et la part de chacun (en pixels de la scène)"""
    u0 = (np.arange(n_src) - lo) / step
    u1 = u0 + 1 / step
    i = np.floor(u0).astype(int)
    w0 = np.minimum(u1, i + 1) - u0
    w1 = np.maximum(0.0, u1 - (i + 1))
    out = []
    for idx, w in ((i, w0), (i + 1, w1)):
        ok = (idx >= 0) & (idx < n_out) & (w > 0)
        out.append((np.where(ok, idx, 0), np.where(ok, w, 0.0)))
    return out


def majority(f, s, rx, ry, cw, ch, ax, ay, K, lab):
    """l'image f à l'échelle s dans une cellule cw x ch : (rx, ry) de la planche (dans la boîte) sur (ax + 0,5, ay) ; chaque
    pixel de la scène plein si la figure en couvre la moitié, de la teinte (lab, K teintes) qui en couvre le plus : la
    moyenne de ses pixels de cette teinte-là"""
    m = f['m']
    Hs, Ws = m.shape
    SX = spans(Ws, rx - (ax + 0.5) / s, 1 / s, cw)
    SY = spans(Hs, ry - ay / s, 1 / s, ch)
    rgb = f['rgb'].astype(float)
    cov = np.zeros(ch * cw)
    hist = np.zeros(ch * cw * K)
    csum = np.zeros((ch * cw * K, 3))
    fy, fx = np.nonzero(m)
    l = lab[fy, fx]
    c = l >= 0
    for iy, wy in SY:
        for ix, wx in SX:
            w = wy[fy] * wx[fx]
            o = iy[fy] * cw + ix[fx]
            cov += np.bincount(o, w, ch * cw)
            k = o[c] * K + l[c]
            hist += np.bincount(k, w[c], ch * cw * K)
            for ci in range(3):
                csum[:, ci] += np.bincount(k, w[c] * rgb[fy[c], fx[c], ci], ch * cw * K)
    cov = cov.reshape(ch, cw)
    hist = hist.reshape(ch, cw, K)
    best = hist.argmax(-1)
    bw = np.take_along_axis(hist, best[..., None], -1)[..., 0]
    col = np.take_along_axis(csum.reshape(ch, cw, K, 3), best[..., None, None], 2)[:, :, 0] / np.maximum(bw, 1e-12)[..., None]
    full = cov >= 0.5
    have = full & (bw > 0)
    if (full & ~have).any():                                          # (plein, mais sans coeur dessous : la couleur du voisin plein le plus proche)
        _, (iy, ix) = nd.distance_transform_edt(~have, return_indices=True)
        col = np.where((full & ~have)[..., None], col[iy, ix], col)
    tk, tc = thin_lines(f, s, SX, SY, cw, ch)                          # (le canon, la bretelle : un trait d'un pixel, pas effacé)
    add = tk & ~full
    col = np.where(add[..., None], tc, col)
    full |= add
    out = np.zeros((ch, cw, 4), np.uint8)
    out[..., :3] = np.where(full[..., None], np.clip(np.round(col * EXPOSE), 0, 255), 0).astype(np.uint8)
    out[..., 3] = np.where(full, 255, 0)
    return out


THIN = dict(r=0.6, ct=0.2, len=1.5, area=0.35)   # (un trait fin : sa part d'un pixel de la scène au moins, sa longueur et son aire en px de la scène)


def thin_lines(f, s, SX, SY, cw, ch):
    """les parties de la figure plus fines qu'un pixel de la scène (ce que l'ouverture par un disque d'un pixel de la scène
    ôte : un canon, une bretelle, un doigt), qu'une majorité effacerait : chacune rendue par un trait d'un pixel, le long
    de son axe (sa part de chaque pixel de la scène, gardée là où elle passe son maximum en travers de l'axe), de la couleur
    de sa moitié la plus sombre (son coeur ; le bord est mêlé de blanc)"""
    m, d, rgb = f['m'], f['d'].astype(float), f['rgb'].astype(float)
    r = max(1, int(round(THIN['r'] / s)))
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
    disk = xx * xx + yy * yy <= r * r
    thin = m & ~nd.binary_opening(m, structure=disk)
    keep = np.zeros((ch, cw), bool)
    tcol = np.zeros((ch, cw, 3))
    lab, n = nd.label(thin, structure=np.ones((3, 3)))
    for i in range(1, n + 1):
        ys, xs = np.nonzero(lab == i)
        if len(ys) < THIN['area'] / s ** 2:
            continue
        P = np.stack([xs, ys], 1).astype(float)
        P -= P.mean(0)
        ev, V = np.linalg.eigh(P.T @ P / len(P))
        if 4 * np.sqrt(ev[1]) < THIN['len'] / s:                        # (pas un trait : une bosse du bord)
            continue
        nx, ny = V[:, 0]                                                # (la normale : la plus petite étendue)
        dirs = [(0, 1), (1, 0), (1, 1), (1, -1)]
        dy, dx = max(dirs, key=lambda q: abs(q[1] * nx + q[0] * ny) / np.hypot(*q))
        ct = np.zeros(ch * cw)
        sm = np.zeros((ch * cw, 3))
        sw = np.zeros(ch * cw)
        dark = d[ys, xs] >= np.median(d[ys, xs])
        for iy, wy in SY:
            for ix, wx in SX:
                w = wy[ys] * wx[xs]
                o = iy[ys] * cw + ix[xs]
                ct += np.bincount(o, w, ch * cw)
                sw += np.bincount(o[dark], w[dark], ch * cw)
                for c in range(3):
                    sm[:, c] += np.bincount(o[dark], w[dark] * rgb[ys[dark], xs[dark], c], ch * cw)
        ct = ct.reshape(ch, cw)
        P_ = np.pad(ct, 1)
        fwd = P_[1 + dy:1 + dy + ch, 1 + dx:1 + dx + cw]
        bwd = P_[1 - dy:1 - dy + ch, 1 - dx:1 - dx + cw]
        k = (ct >= THIN['ct']) & (ct >= fwd) & (ct > bwd) & (sw.reshape(ch, cw) > 0)
        keep |= k
        tcol = np.where(k[..., None], (sm / np.maximum(sw, 1e-12)[:, None]).reshape(ch, cw, 3), tcol)
    return keep, tcol


def hero_palette(frames):
    """les 32 teintes de la majorité : k-moyennes (OKLab) sur les coeurs de toutes ses images"""
    px = np.concatenate([f['rgb'][core(f)] for f in frames]).astype(float)
    q = (px // 4).astype(np.int64)
    u, inv, cnt = np.unique(q[:, 0] * 4096 + q[:, 1] * 64 + q[:, 2], return_inverse=True, return_counts=True)
    X = np.zeros((len(u), 3))
    np.add.at(X, inv.ravel(), RG.oklab(px))
    X /= cnt[:, None]
    C, _ = RG.kmeans(X, cnt.astype(float), PALETTE, seed=11)
    return C


def labels(f, C):
    X = RG.oklab(f['rgb'].astype(float))
    lab = ((X[:, :, None, :] - C[None, None]) ** 2).sum(-1).argmin(-1)
    return np.where(core(f), lab, -1)


# ---- un héros : ses cellules
ROWK = dict(walk=0.97, step=0.97, stand=1.0, aim=0.96, reload=0.96, kneel=1.0)   # (la hauteur médiane de chaque rangée : H x, K x)
ROWREF = dict(walk='walk', step='walk', stand='stand', aim='reload', reload='reload', kneel='kneel')


def scales(hero):
    """une échelle par rangée de chaque planche : les planches dessinent plus grandes les rangées de moins d'images (6 ou 4
    au lieu de 8 : la figure remplit la place), on ne peut donc pas prendre la même pour toute une planche. La marche (et
    la descente et la montée, de la même grille de huit) : sa hauteur médiane -> 0,97 H (on marche les genoux un peu
    pliés) ; debout au repos (et la joie, sur la même rangée) : -> H ; le rechargement (et la visée, de la même grille) :
    -> 0,96 K ; à genou au repos : -> K. La tête garde ainsi sa taille d'un mouvement à l'autre (à un pixel près)."""
    Hc = HEROES[hero]
    out = {}
    vers = set(Hc['ver'].values()) | {r[4] for k in ('down', 'rise') for r in Hc[k] if len(r) > 4}
    for ver in sorted(vers):
        for kind, rows in ROWS.items():
            fr = sheet(hero, kind, ver)
            for ri, row in enumerate(rows):
                ref = ROWREF[row]
                rj = rows.index(ref)
                F = [f for f in fr if f['row'] == rj and (ref != 'stand' or f['col'] < 2)]
                tgt = (Hc['H'] if kind == 'deplacements' else Hc['K']) * Hc.get('rowk', {}).get(ref, ROWK[ref])
                out[(kind, ver, ri)] = tgt / float(np.median([f['m'].shape[0] for f in F]))
    return out


def uses(hero):
    """chaque image de chaque mouvement : (mouvement, rang, l'image, le recalage, la hauteur, ses champs)"""
    Hc = HEROES[hero]
    U = []
    for k, r in enumerate(Hc['down']):
        U.append(('down', k, (r[0], r[1]) + tuple(r[4:]), 'head', r[2], dict(inside=r[3])))
    for k, c in enumerate(Hc['walk']):
        U.append(('walk', k, ('walk', c), 'head', 0, {}))
    for k, r in enumerate(Hc['rise']):
        U.append(('rise', k, (r[0], r[1]) + tuple(r[4:]), 'head', r[2], dict(inside=r[3])))
    for k, c in enumerate(Hc['stand']):
        U.append(('stand', k, ('stand', c), 'feet', 0, {}))
    for k, ref in enumerate(Hc['kneel']):
        U.append(('kneel', k, ref, 'feet', 0, dict(kn=ref[0] == 'kneel')))
    for i, (deg, ca, cr) in enumerate(Hc['aims']):
        U.append(('aim', 2 * i, ('aim', ca), 'feet', 0, dict(deg=deg)))
        U.append(('aim', 2 * i + 1, ('aim', cr), 'feet', 0, dict(deg=deg)))
    for k, c in enumerate(Hc['reload']):
        U.append(('reload', k, ('reload', c), 'feet', 0, dict(drop=k == Hc['drop'])))
    for k, c in enumerate(Hc['cheer']):
        U.append(('cheer', k, ('stand', c), 'feet', 0, dict(u=Hc['cheer_u'][k]) if Hc.get('cheer_u') else {}))
    IU = [0, 0.18, 0.5, 0.82]
    for k, c in enumerate(Hc['idle']):
        U.append(('idle', k, ('kneel', c), 'feet', 0, dict(u=IU[k])))
    return U


def muzzle(f, deg, given):
    """la bouche du canon dans la boîte de l'image (x, y, px de la planche) : donnée, ou le bout de la figure du côté visé,
    entre 5 et 55 % de sa hauteur (l'arme à hauteur de poitrine et de visage)"""
    if given is not None:
        return given
    m = f['m']
    ys, xs = np.nonzero(m)
    t, b = ys.min(), ys.max()
    band = (ys > t + 0.05 * (b - t)) & (ys < t + 0.55 * (b - t))
    if abs(deg) < 20:
        return None
    x = xs[band].max() if deg > 0 else xs[band].min()
    yy = ys[band & (xs == x)]
    return (float(x) + (1.0 if deg > 0 else 0.0), float(yy.mean()) + 0.5)


def build(hero, kl=1.0, pal=None):
    Hc = HEROES[hero]
    S = {key: v * kl for key, v in scales(hero).items()}
    U = uses(hero)
    F = []
    for (mv, k, ref, regm, lift, extra) in U:
        f = frame(hero, *ref)
        s = S[(f['kind'], f['ver'], f['row'])]
        rx = reg_head(f['m']) if regm == 'head' else reg_feet(f['m'])
        F.append(dict(mv=mv, k=k, f=f, s=s, rx=rx, ry=float(f['m'].shape[0]), lift=float(lift) * kl, extra=extra))
    # la cellule : assez pour toutes
    ax = int(np.ceil(max(q['rx'] * q['s'] - 0.5 for q in F))) + 1
    cw = ax + int(np.ceil(max(0.5 + (q['f']['m'].shape[1] - q['rx']) * q['s'] for q in F))) + 1
    ay = int(np.ceil(max(q['lift'] + q['ry'] * q['s'] for q in F))) + 1
    ch = ay + 1
    # la majorité
    if pal is None:
        pal = hero_palette([q['f'] for q in F])
    labs = {}
    for q in F:
        key = (q['f']['kind'], q['f']['ver'], q['f']['row'], q['f']['col'])
        if key not in labs:
            labs[key] = labels(q['f'], pal)
        ry = q['ry'] + q['lift'] / q['s']
        for _ in range(3):                                             # (le bas de l'image sur sa rangée : un pixel de sol vide, on descend)
            c = majority(q['f'], q['s'], q['rx'], ry, cw, ch, ax, ay, len(pal), labs[key])
            rows = np.nonzero(c[..., 3].any(1))[0]
            want = ay - 1 - int(round(q['lift']))
            if rows.max() >= want:
                break
            ry -= 1 / q['s']
        q['cell'] = c
    return dict(hero=hero, F=F, cw=cw, ch=ch, ax=ax, ay=ay, S=S, kl=kl, pal=pal)


def build_levels(hero):
    """le héros à chacune des tailles LEVELS : les mêmes images, la même palette de majorité"""
    B0 = build(hero, LEVELS[0])
    return [B0] + [build(hero, k, B0['pal']) for k in LEVELS[1:]]


def ground_feet(c, ay):
    """les pieds au sol d'une image de marche (sa cellule, à la taille de la scène) : les morceaux de ses trois dernières
    rangées qui touchent l'une des deux dernières ; leur talon et leur pointe (colonnes)"""
    a = c[..., 3] > 0
    lab, n = nd.label(a[ay - 3:ay].any(0))
    out = []
    for k in range(1, n + 1):
        cols = np.nonzero(lab == k)[0]
        if a[ay - 2:ay, cols].any():
            out.append((int(cols.min()), int(cols.max())))
    return out


def walk_steps(cells, ay):
    """d'une image de la marche à la suivante (la dernière à la première), de combien le corps avance (px entiers de la
    scène) : le moins, jamais en arrière, qui pose un pied au sol de l'une sur un pied au sol de l'autre (sa pointe sur sa
    pointe, ou son talon sur son talon, à un pixel près) ; s'ils n'ont aucun pied commun (l'autre se pose plus loin), le
    corps ne bouge pas. Rend les pas et, pour chacun, de combien ce pied glisse encore (px)"""
    ft = [ground_feet(c, ay) for c in cells]
    step, slip = [], []
    for i in range(len(ft)):
        d = [a[e] - b[e] for a in ft[i] for b in ft[(i + 1) % len(ft)] for e in (0, 1) if a[e] - b[e] >= -1]
        st = max(0, min(d)) if d else 0
        step.append(int(st))
        slip.append(min(abs(x - st) for x in d) if d else 0)
    return step, slip


def walk_times(step):
    """sa marche vers nous : le pas de côté du dessin (step, px à la taille x 1, PPM px/m) en un cycle de deux pas à CADENCE,
    le reste de WALK_V vers nous (vz, m/s) ; chaque image dure la longueur de son pas sur le sol (son pas de côté et sa part
    du pas vers nous), bornée à TF : le corps va d'un pas régulier"""
    L = len(step)
    T = 2.0 / CADENCE
    lat = np.array(step, float) / PPM
    vlat = lat.sum() / T
    vz = float(np.sqrt(max(0.0, WALK_V ** 2 - vlat ** 2)))   # (en mètres de la peinture : street.js le prend x K, en mètres de B)
    w = np.hypot(lat, vz * T / L)
    tf = np.clip(w * T / w.sum(), *TF)
    for _ in range(20):
        tf = np.clip(tf * T / tf.sum(), *TF)
    return tf, vz, vlat


def light(cell, X, Y):
    """l'éclair à la bouche du canon (X, Y, px de la cellule) sur les pixels pleins de la cellule : RGBA (alpha 255 où il y a
    de la lumière), en 1 / (1 + (d / R)^2)"""
    h, w = cell.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.hypot(xx + 0.5 - X, yy + 0.5 - Y)
    I = FLASH['peak'] / (1 + (d / FLASH['R']) ** 2)
    on = (cell[..., 3] > 0) & (I > FLASH['floor'])
    out = np.zeros((h, w, 4), np.uint8)
    out[..., :3] = np.where(on[..., None], np.clip(np.round(I[..., None] * np.array(FLASH['rgb'])), 0, 255), 0).astype(np.uint8)
    out[..., 3] = np.where(on, 255, 0)
    return out


def assemble(BL, log=print):
    """les tailles d'un héros (BL : build_levels) dans un atlas, une taille par bande ; une seule famille de tons pour toutes"""
    hero = BL[0]['hero']
    Hc = HEROES[hero]
    n = len(BL[0]['F'])
    cols = 12
    rows = (n + cols - 1) // cols
    W = max(cols * B['cw'] for B in BL)
    bands, y = [], 0
    for B in BL:
        bands.append(y)
        y += rows * B['ch']
    A = np.zeros((y, W, 4), np.uint8)
    FL = np.zeros_like(A)
    items, muz0 = [], {}
    for li, B in enumerate(BL):
        cw, ch, ax, ay = B['cw'], B['ch'], B['ax'], B['ay']
        for i, q in enumerate(B['F']):
            x, y = (i % cols) * cw, bands[li] + (i // cols) * ch
            A[y:y + ch, x:x + cw] = q['cell']
            q['n'] = i
            q['box'] = [x, y, cw, ch]
            if q['mv'] == 'aim':
                deg = q['extra']['deg']
                given = Hc['muz'].get(q['k'] // 2)
                mz = muzzle(q['f'], deg, given[q['k'] % 2] if given else None)
                if mz is None:
                    sys.exit('%s : la bouche du canon de %s (visée %d°) n\'est pas donnée (HEROES.muz)' % (hero, q['f']['name'], deg))
                s = q['s']
                ry = q['ry'] + q['lift'] / s
                X, Y = ax + 0.5 + (mz[0] - q['rx']) * s, ay + (mz[1] - ry) * s
                mc, mr = int(np.floor(X)), int(np.floor(Y))           # (le pixel de la bouche : street.js y centre l'éclair)
                if li == 0:
                    muz0[i] = [mc - ax, mr - ay]
                FL[y:y + ch, x:x + cw] = light(q['cell'], mc + 0.5, mr + 0.5)
            items.append(dict(a=A, box=q['box'], anchor=(ax, ay), seq=(li, q['mv'], q['k']), **{'with': [FL]}))
    info = RG.regrain_group(items, RG.params('crew'), 'crew_' + hero)
    # la marche (sur la taille x 1) : le pas de côté de chaque image, le pied posé sur son pixel ; la durée de chaque image
    B0 = BL[0]
    walk = [q for q in B0['F'] if q['mv'] == 'walk']
    step, slip = walk_steps([A[q['box'][1]:q['box'][1] + B0['ch'], q['box'][0]:q['box'][0] + B0['cw']] for q in walk], B0['ay'])
    tf, vz, vlat = walk_times(step)
    mv = {}
    for q in B0['F']:
        e = dict(cell=q['n'])
        x = q['extra']
        if q['mv'] in ('down', 'rise'):
            e['inside'] = bool(x['inside'])
        if q['mv'] == 'kneel':
            e['kn'] = bool(x['kn'])
        if q['mv'] == 'aim':
            e['muz'] = muz0[q['n']]
        if q['mv'] == 'reload':
            e['drop'] = bool(x['drop'])
        if 'u' in x:
            e['u'] = x['u']
        mv.setdefault(q['mv'], []).append(e)
    order = ['down', 'walk', 'rise', 'stand', 'kneel', 'aim', 'reload', 'cheer', 'idle']
    ws = []                                                            # (le pas de chaque image à chaque taille : à x 1,22 un pied n'est pas
    for B in BL:                                                       #  toujours le pied de x 1 agrandi, sa pointe ou son talon bouge d'un px)
        wq = [q for q in B['F'] if q['mv'] == 'walk']
        ws.append(walk_steps([A[q['box'][1]:q['box'][1] + B['ch'], q['box'][0]:q['box'][0] + B['cw']] for q in wq], B['ay'])[0])
    J = dict(lv=[dict(k=B['kl'], y=bands[li], cw=B['cw'], ch=B['ch'], ax=B['ax'], ay=B['ay'], ws=ws[li]) for li, B in enumerate(BL)],
             cols=cols, n=n, size=[A.shape[1], A.shape[0]], wtf=[round(float(t), 3) for t in tf], vz=round(vz * K_PEINT, 3),
             dirs=[d for d, _, _ in Hc['aims']], moves={k: mv[k] for k in order})
    log('%-9s %d tailles de %d images (%s), %d familles, pente %.3f, %d px détachés ; la marche : pas de côté %s (%d px le cycle, le pied '
        'posé à %d px près ; aux autres tailles %s), %.2f m/s de côté, %.2f vers nous (%.0f° de droit sur nous), durées %s'
        % (hero, len(BL), n, ', '.join('%dx%d' % (B['cw'], B['ch']) for B in BL), info['families'], info['slope'], info['strays'], step, sum(step),
           max(slip), ws[1:], vlat, vz, np.degrees(np.arctan2(vlat, vz)), [round(float(t), 3) for t in tf]))
    return A, FL, J, info


def save_webp(arr, path):
    Image.fromarray(arr, 'RGBA').save(path, 'WEBP', lossless=True, quality=100, method=6, exact=True)


def write_crw(heroes_json):
    js = open(JSF, encoding='utf-8').read()
    i = js.find('const CRW = ') + len('const CRW = ')
    old, end = json.JSONDecoder().raw_decode(js[i:])
    new = dict(ppm=PPM, kicks=KICKS, heroes={})
    for h in ORDER:
        new['heroes'][h] = heroes_json.get(h) or old['heroes'][h]
    txt = json.dumps(new, separators=(',', ':'), ensure_ascii=False)
    js = js[:i] + txt + js[i + end:]
    open(JSF, 'w', encoding='utf-8').write(js)


def main():
    ap = argparse.ArgumentParser(description='l\'équipe du TranZit depuis les planches (voir la docstring)')
    ap.add_argument('--only', default=None, help='dempsey,nikolai,takeo,richtofen')
    ap.add_argument('--preview', default=None, help='un dossier : les images coupées x4, les mouvements, v1 | v2')
    ap.add_argument('--dry', action='store_true', help='rien n\'est écrit dans assets/')
    o = ap.parse_args()
    who = o.only.split(',') if o.only else ORDER
    out = {}
    for h in who:
        B = build_levels(h)
        A, FL, J, info = assemble(B)
        out[h] = J
        if not o.dry:
            save_webp(A, os.path.join(ASSETS, 'crew_%s.webp' % h))
            save_webp(FL, os.path.join(ASSETS, 'crew_%s_flash.webp' % h))
        if o.preview:
            preview(B, A, FL, J, o.preview)
    if not o.dry:
        write_crw(out)


def preview(BL, A, FL, J, d):
    """chaque image coupée x4, à chacune de ses tailles (une bande par taille : son mouvement, son image de la planche,
    l'ancre en rouge, la bouche du canon) ; et l'atlas éclairé par l'éclair"""
    os.makedirs(d, exist_ok=True)
    h, z = BL[0]['hero'], 4
    can = Image.new('RGBA', (A.shape[1], A.shape[0]), (96, 100, 108, 255))
    can.alpha_composite(Image.fromarray(A, 'RGBA'))
    dr = ImageDraw.Draw(can)
    for li, B in enumerate(BL):
        for q in B['F']:
            x, y, w, hh = q['box']
            dr.point((x + B['ax'], y + B['ay']), fill=(255, 60, 60, 255))
    can = can.resize((can.width * z, can.height * z), Image.NEAREST)
    dr = ImageDraw.Draw(can)
    for li, B in enumerate(BL):
        for q in B['F']:
            x, y, w, hh = q['box']
            dr.rectangle([x * z, y * z, (x + w) * z - 1, (y + hh) * z - 1], outline=(70, 76, 90, 255))
            dr.text((x * z + 3, y * z + 2), 'x%.2f %s%d %s' % (B['kl'], q['mv'], q['k'], q['f']['name']), fill=(240, 220, 120, 255))
            if q['mv'] == 'aim':
                mz = [e for e in J['moves']['aim'] if e['cell'] == q['n']][0]['muz']
                mx, my = x + B['ax'] + (mz[0] + 0.5) * B['kl'], y + B['ay'] + (mz[1] + 0.5) * B['kl']
                dr.ellipse([mx * z - 3, my * z - 3, mx * z + 3, my * z + 3], outline=(255, 80, 200, 255))
    can.convert('RGB').save(os.path.join(d, 'cells_%s_x4.png' % h))
    fl = Image.new('RGBA', (A.shape[1], A.shape[0]), (0, 0, 0, 255))
    lit = A.astype(int)
    lit[..., :3] = np.clip(lit[..., :3] + FL[..., :3].astype(int) * (FL[..., 3:] > 0), 0, 255)
    fl.alpha_composite(Image.fromarray(lit.astype(np.uint8), 'RGBA'))
    fl.resize((fl.width * z, fl.height * z), Image.NEAREST).convert('RGB').save(os.path.join(d, 'flash_%s_x4.png' % h))


if __name__ == '__main__':
    main()
