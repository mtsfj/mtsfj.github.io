#!/usr/bin/env python3
"""La façade de Kirua, au-dessus du magasin de boissons : une grande baie vitrée à la place de la petite fenêtre, sa pièce éclairée.

    python3 tools/kirua_bay_window.py      (le dernier de ce coin : après tools/kirua_house_side.py et tools/kirua_gutter.py,
                                            dont les zones couvrent la sienne ; il reprend sa zone au commit BEFORE à chaque
                                            fois, on peut donc le relancer)

La façade de la maison de Kirua (x 158..325, de son angle à la descente) n'avait qu'une petite fenêtre (x 248..273) dans
un grand mur de planches vide. À sa place, la baie d'une maison de référence du propriétaire (tools/src/kirua_bay_ref.png,
ref_facade_4 : un bureau éclairé, son rideau derrière un meneau, la chaise, l'écran, l'étagère, le plafond et ses spots ;
pas la ref_facade_2, dont la pièce est déjà celle de la maison du fond), posée dans le mur dans la perspective de la
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
droit, le meneau et la traverse de la référence refaits nets à leur place, MULLIONS, TRANSOMS). L'ombre du linteau en
haut de la vitre, rangée par rangée (HEAD_SH ; allumée, la pièce en garde une part : HEAD_LIT). Un appui en saillie
sous la baie, plus large qu'elle : son arête claire, sa face, son dessous sombre, son ombre portée sur les planches en
deux marches (SILL_SH). Toutes ses lignes sur des rayons vers FVP ou d'aplomb, au pixel près, sans flou. Le bois prend
le couchant et les heures comme les planches ; le verre et le dormant, non.

La pièce : chaque pixel de vitre est la moyenne de la référence sur son morceau du plan de la vitre (SUB x SUB points,
le meneau et la traverse à part), ramenée à la plus proche des couleurs de la référence (NPAL couleurs, plus ACCENT
couleurs vives que la coupe médiane perd, celles de l'écran), sans tramage ; un pixel seul parmi des voisins d'accord
prend leur couleur (CLEAN passes). Éteinte, comme elle est dans les calques : le verre sombre du peintre (celui de sa
petite fenêtre), la pièce à peine lisible dedans (sa clarté seule, ses lumières éteintes). Allumée, le sprite de la
fenêtre d'habitation (le comp win_z7_up de assets/street.js, celui de la petite fenêtre : allumée longtemps, éteinte un
moment, éteinte dans la coupure de courant, rouge la nuit rouge, la télé certains soirs) : la pièce ramenée à la fenêtre
éclairée de la rue (la moyenne et l'écart de chaque canal de la lumière de la petite fenêtre, au commit BEFORE), l'écran
(SCREEN, sa boîte dans la référence) gardant sa propre lumière froide, l'arête de l'appui sous la vitre prise dans la
lumière de la pièce (SILL_LIT). L'arbre reste devant tout : ses feuilles (trouvées comme dans tools/kirua_house_side.py)
ne sont pas touchées, et la lumière n'est que là où elles s'ouvrent sur GLOW_MIN pixels ensemble.

Là où la petite fenêtre était et que la baie ne couvre pas (sous l'appui), les planches du peintre, refaites comme
tools/kirua_house_side.py les refait : chaque pixel sa planche sur son rayon vers FVP, prise dans ses planches à droite
(SRC_X), un pixel différent de cette planche par colonne, en miroir, pour que le grain reste. Dans layer_city_off,
street_unlit (les mêmes, moins la lumière de la rue qui tombait là, du rapport des deux calques au commit BEFORE : celle
que la nuit rouge dessine en rouge), night_far (0, celui de la rue) et street_sun ; écrit aussi assets/win_z7_up.webp et
sa boîte dans assets/street.js. Il faut git, Pillow, numpy.
"""
import io
import os
import re
import subprocess
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = lambda p: os.path.join(ROOT, 'assets', p)
BEFORE = '119e468'                   # (les calques avant cet outil : sa zone reprise de là à chaque fois)
OLD, TREE = '8d4ca3c^', '8d4ca3c'    # (avant le changement de l'arbre devant le dojo ; ce changement : ses feuilles)
REF = os.path.join(ROOT, 'tools', 'src', 'kirua_bay_ref.png')
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
INNER = (19, 36, 735, 380)           # dans la référence (x0, y0, x1, y1) : l'intérieur de la baie, son cadre autour
MULLIONS = ((137, 163),)             # (x0, x1) : son meneau, entre le rideau et la pièce
TRANSOMS = ((270, 281, 19, 137),)    # (y0, y1, x0, x1) : sa traverse, derrière le rideau
SCREEN = (384, 219, 473, 290)        # (x0, y0, x1, y1) : l'écran, sa lumière à lui
NPAL, ACCENT = 12, (4, 50)           # les couleurs de la référence (coupe médiane) ; plus tant de couleurs vives, celles
                                     # de ses pixels plus loin que tant de toutes les autres
SUB, CLEAN = 4, 2                    # (points par pixel, de chaque côté ; passes contre les pixels seuls)
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
UP, UP_V = 'win_z7_up', 3            # sa lumière : le comp de la petite fenêtre, sa version
LEAF = 45                            # (une feuille : plus sombre que ça, là où le changement de l'arbre a mis un pixel)
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
    uref = lambda xr: (xr - rx0) / (rx1 - rx0); vref = lambda yr: (yr - ry0) / (ry1 - ry0)
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

    # la pièce : chaque pixel de vitre, la moyenne de la référence sur son morceau du plan de la vitre (le meneau et la
    # traverse à part), puis la plus proche de ses couleurs, sans tramage
    ref = Image.open(REF).convert('RGB'); R_ = np.asarray(ref).astype(float)
    inner = ref.crop(INNER)
    pal = np.asarray(inner.quantize(colors=NPAL, method=Image.Quantize.MEDIANCUT).getpalette()[:3 * NPAL]).reshape(NPAL, 3).astype(float)
    ip = np.asarray(inner).reshape(-1, 3).astype(float)
    far = ip[np.sqrt(((ip[:, None, :] - pal[None]) ** 2).sum(2)).min(1) > ACCENT[1]]
    vivid = Image.fromarray(far.astype(np.uint8)[None]).quantize(colors=ACCENT[0], method=Image.Quantize.MEDIANCUT)
    pal = np.vstack([pal, np.asarray(vivid.getpalette()[:3 * ACCENT[0]]).reshape(-1, 3)])
    bar = lambda xr, yr: any(m0 - 1 <= xr < m1 + 1 for m0, m1 in MULLIONS) or \
        any(t0 - 1 <= yr < t1 + 1 and tx0 <= xr < tx1 for t0, t1, tx0, tx1 in TRANSOMS)
    sx0, sy0, sx1, sy1 = SCREEN
    q, scr = {}, set()
    for (y, x) in zip(*np.where(cls == 7)):
        pts = []
        for a in range(SUB):
            xs = x - 0.5 + (a + 0.5) / SUB; xr = rx0 + U(xs) * (rx1 - rx0)
            for b in range(SUB):
                yr = ry0 + V(xs, y - 0.5 + (b + 0.5) / SUB) * (ry1 - ry0)
                if rx0 <= xr < rx1 and ry0 <= yr < ry1 and not bar(xr, yr): pts.append((xr, yr))
        c = np.mean([R_[int(yr), int(xr)] for xr, yr in pts], 0) if pts else ip.mean(0)
        q[y, x] = int(np.argmin(((pal - c) ** 2).sum(1)))
        if pts and np.mean([sx0 <= xr < sx1 and sy0 <= yr < sy1 for xr, yr in pts]) >= 0.5: scr.add((y, x))
    N8 = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
    for _ in range(CLEAN):                                                   # (un pixel seul parmi des voisins d'accord : le leur)
        q0 = dict(q)
        for (y, x), k in q0.items():
            nb = [q0[y + dy, x + dx] for dy, dx in N8 if (y + dy, x + dx) in q0]
            if len(nb) >= 6:
                best = max(set(nb), key=nb.count)
                if best != k and nb.count(best) >= 5 and nb.count(k) <= 1: q[y, x] = best

    # ce qu'on en voit : la vitre que les feuilles ne cachent pas ; sa lumière où elles s'ouvrent sur GLOW_MIN pixels
    vis = (cls == 7) & ~front
    lab = np.zeros((H, W), int); n_lab = 0
    for (y, x) in zip(*np.where(vis)):
        if lab[y, x]: continue
        n_lab += 1; comp = flood(vis & (lab == 0), [(y, x)]); lab[comp] = n_lab
    size = np.bincount(lab.ravel())
    lit = [(y, x) for (y, x) in zip(*np.where(vis)) if size[lab[y, x]] >= GLOW_MIN]
    edge = [(y, x) for (y, x) in zip(*np.where(cls == 8)) if XL < x < XR and not front[y, x]]

    # éteinte : le verre sombre du peintre, la pièce à peine lisible dedans (sa clarté seule, ses lumières éteintes)
    hg = city[old & ~grow(~old, 3)][:, :3]
    lum = pal @ LUM; ks = np.array([q[k] for k in lit])
    z = np.clip((lum - np.median(lum[ks])) / lum[ks].std(), *OFF_Z)
    offp = hg.mean(0)[None, :] * (1 + OFF_K * z)[:, None]
    # allumée : la fenêtre éclairée de la rue (la moyenne et l'écart de chaque canal de la lumière de la petite fenêtre),
    # l'écran gardant sa lumière (sa clarté ramenée de même), l'arête de l'appui dans la lumière de la pièce
    upi = load(UP + '.webp', 'RGBA', BEFORE); upl = upi[upi[..., 3] == 255][:, :3]
    onp = np.clip(upl.mean(0) + (pal - pal[ks].mean(0)) / pal[ks].std(0) * upl.std(0), 0, 255)
    onq = np.clip(upl.mean(0) + (pal - pal[ks].mean(0)) * (upl @ LUM).std() / lum[ks].std(), 0, 255)
    room = sorted({q[k] for k in lit if k not in scr}, key=lambda k: lum[k])
    sill = np.array(EDGE) + SILL_LIT * (onp[room[-1]] - np.array(EDGE))

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
        elif c == 7: col, sun = offp[q[y, x]] * MUL[y, x, 0], 0
        else: col, sun = face(c, x, y) * MUL[y, x, 0], 255
        L[0][y, x, :3] = col; L[1][y, x, :3] = col * cut[y, x]; L[0][y, x, 3] = L[1][y, x, 3] = 255
        L[2][y, x] = 0; L[3][y, x] = sun
        n_w += 1
    spr = np.zeros((H, W, 4))
    for (y, x) in lit: spr[y, x] = [*((onq if (y, x) in scr else onp)[q[y, x]] * MUL[y, x, 1]), 255]
    for (y, x) in edge: spr[y, x] = [*sill, 255]

    for (n, m), l in zip(names, L): save(l, n, m)
    ys, xs = np.where(spr[..., 3] > 0)
    bx, by, bw, bh = int(xs.min()), int(ys.min()), int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1)
    save(spr[by:by + bh, bx:bx + bw], UP + '.webp', 'RGBA')
    s_ = open(A('street.js'), encoding='utf-8').read()
    s_, n_s = re.subn(r'"%s": \{"src": "assets/%s\.webp\?v=\d+", "x": \d+, "y": \d+, "w": \d+, "h": \d+\}' % (UP, UP),
                      f'"{UP}": {{"src": "assets/{UP}.webp?v={UP_V}", "x": {bx}, "y": {by}, "w": {bw}, "h": {bh}}}', s_)
    assert n_s == 1, 'street.js : le comp de la petite fenêtre est introuvable'
    open(A('street.js'), 'w', encoding='utf-8').write(s_)
    sp = spr[spr[..., 3] > 0][:, :3]
    print('baie', XR - XL + 1, 'colonnes,', n_w, 'px | planches refaites', n_b, 'px | meneau', sorted(mcols),
          '| sa lumière', len(xs), 'px en', (bx, by, bw, bh), ': moyenne', sp.mean(0).round(1), 'écart', sp.std(0).round(1),
          '(la petite fenêtre :', upl.mean(0).round(1), upl.std(0).round(1), ')')


if __name__ == '__main__':
    main()
