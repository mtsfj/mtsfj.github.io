#!/usr/bin/env python3
"""L'oden : derrière sa porte vitrée et sa fenêtre, la boutique en petite maquette 3D, vue par l'œil de la rue.

    python3 tools/oden_interior.py                  (il reprend sa zone au commit BEFORE à chaque fois, on peut donc le relancer :
                                                      il écrit la même chose)
    python3 tools/oden_interior.py --preview dossier (des aperçus seulement, rien d'écrit dans assets/)

La caméra de la rue est une perspective à un point : focale F = 1400 px, point de fuite VP (700, 615), l'œil à EYE = 1,5 m
du trottoir. La façade de l'oden est à gauche de la rue et court vers VP. Le seuil de sa porte (SEUIL : la première rangée du
trottoir sous elle, mesurée colonne par colonne) est sur des rayons vers VP à 1,5 m sous l'œil : la façade est à X_F = 6,79 m
à gauche de l'œil ; la porte (deux vantaux coulissants, chacun son quadrillage de trois sur trois) de Z = 34,5 à 39,5 m le
long de la rue, la fenêtre (deux châssis, leurs montants de rencontre au milieu) de Z = 40,8 à 46,4 m. Le verre de la porte
va de sous l'ourlet du noren peint (2,41 m) à 1,41 m, celui de la fenêtre de 2,99 m à 1,42 m : par l'un comme par l'autre
on ne voit que le haut de la pièce, de 1,4 m au plafond (les rayons y sont presque de niveau : ils descendent de 3 cm au
plus jusqu'au mur du bout).

La boutique, une boîte derrière la façade (le mur de façade de WALL_IN d'épaisseur, la pièce de D_ROOM de fond, le plafond à
CEIL). Par une ouverture de côté, un rayon file le long de la rue (cinq à sept mètres pour un mètre vers le fond) : il
rencontre le mur du bout de la boutique (de travers à la rue, donc de face) à Z_E = 48 m, juste avant l'angle de la façade
(x 504). L'image du propriétaire (tools/src/oden_room.webp : lanternes, noren, plaquettes du menu, bouteilles de saké,
étagères) couvre ce mur d'un coin à l'autre, du mur de façade au mur de derrière : K_WALL = 348 pixels de l'image par mètre,
ses grandes bouteilles de 1,8 l à 0,40 m ; son haut sous le plafond. Par le verre on en voit les lanternes, le noren, les
plaquettes et les bouteilles (debout sur leur étagère à 1,40 m) ; par le haut de la fenêtre, un coin du plafond. Devant le
mur, l'allée du maître (Z_M), le comptoir des clients (son dessus à CTR_H = 1 m, de Z_C à Z_C + CTR_D, du passage au mur de
façade), la marmite d'oden posée dessus (POT : derrière la fenêtre, d'où monte la vapeur), deux tabourets devant lui, le
comptoir de travail contre le mur : plus bas que le verre, aucun rayon par le verre ne les atteint ; on les voit quand le
vantail de droite est ouvert (le sol, le comptoir, un tabouret), derrière le maître dans l'embrasure. Les montants du verre
sont de la maquette : le quadrillage de la porte (des lattes de 3 cm dans l'épaisseur de la façade, d'aplomb aux tiers de
chaque vantail, ses deux traverses à 1,83 et 2,23 m : là où le peintre les avait mis) et les montants de rencontre de la
fenêtre (deux châssis de 3 cm).

Le rendu. Chaque pixel est pris sur SS x SS rayons de l'œil, puis ramené au pixel entier selon ses bords (reduce : la
surface qui en tient le plus, deux groupes nets séparés, les éclats gardés) ; un barreau dès qu'il en tient 30 %. Le grain du
peintre (GRAIN, léger sur ce qui est chargé), puis chaque pixel ramené à la palette de la boutique (40 couleurs tirées de son
verre allumé d'avant, de son noren et de sa lanterne), un grain ne sautant jamais plus d'une marche. Les barreaux à la couleur
des barreaux peints (BARS_PEINTS : allumée, éteinte).

Dans layer_city_off (allumée) ; street_unlit (la coupure de courant, et la boutique fermée par ses heures : la même pièce dans
le bleu nuit de son verre éteint d'avant, du plus sombre au plus clair selon la clarté de la pièce allumée) ; la nuit rouge
en découle (street.js la tire de ces deux calques). assets/oden_window.webp : le verre de la fenêtre (sans ses montants), où
monte la vapeur. assets/oden_door.webp, ce que street.js pose sur la porte et la fenêtre quand le maître y passe : le verre où
il se montre (porte fermée ; porte ouverte, l'embrasure du vantail de droite jusqu'au seuil), la pièce vue par l'embrasure
ouverte, et le vantail de droite (ses barreaux, ses montants, son bas de bois peint) à chaque pas de son coulissement vers la
gauche, derrière le vantail de gauche (un pixel de son bord arrière à chaque image ; la profondeur fait grandir ce qui vient
vers nous) ; sa description dans la ligne ODM de assets/street.js (avec la marmite, d'où part la vapeur). night_far et
street_sun : 0 ici, tels quels. tools/oden_master.py lit cette maquette. Il faut git, Pillow, numpy.
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

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'tools', 'src', 'oden_room.webp')
JS = os.path.join(ROOT, 'assets', 'street.js')
BEFORE = '7fcd4bb'                   # (les calques avant cet outil : sa zone reprise de là à chaque fois)
ZONE = (420, 556, 500, 624)          # x0, y0, x1, y1 : la porte, la fenêtre et leurs cadres
WIN_M = (462, 556, 40, 68)           # (le masque du verre de la fenêtre : sa boîte, celle de ODEN.window dans street.js)
BOX = (420, 556, 82, 121)            # (ce que street.js pose sur la porte et la fenêtre : sa boîte, du haut de la fenêtre au seuil)

# ---- la caméra de la rue, la façade et ses ouvertures
F, VX, VY, EYE = R.F, R.VX, R.VY, R.EYE
SEUIL = ((424, 676), (428, 675), (432, 674), (438, 673), (442, 672), (446, 671), (450, 670), (452, 670))
C_SEUIL = float(np.mean([(y - VY) / (VX - x) for x, y in SEUIL]))
X_F = EYE / C_SEUIL
DOOR = ((424, 441), (444, 458))      # les colonnes de verre de chaque vantail (les montants de rencontre entre : 442 celui de gauche,
DOOR_TOP, DOOR_BOT = 579, 618        # 443 celui de droite) ; (le haut du verre où le noren ne descend pas ; sa dernière rangée)
OPEN = (443, 458)                    # l'embrasure du vantail de droite ouvert (ses colonnes ; jusqu'à trois rangées au-dessus du seuil)
WIN = (467, 494)                     # les colonnes de verre de la fenêtre
WIN_TOP, WIN_BOT = 0.2190, 617       # (son haut : sur le rayon y = VP_y - c |x - VP_x| ; sa dernière rangée de verre)
KUMI = dict(d=0.03, w=0.03, rails=(1.826, 2.227))   # le quadrillage de la porte : la profondeur et la largeur des lattes, les
                                     # hauteurs des deux traverses (les lattes d'aplomb aux tiers de chaque vantail)
MEET = dict(d=0.03, w=0.04)          # les montants de rencontre de la fenêtre : deux châssis, chacun tant de profondeur et de large

# ---- la boutique
WALL_IN = 0.15                       # (l'épaisseur du mur de façade)
K_WALL = 348.0                       # pixels de l'image par mètre sur le mur du bout (ses bouteilles de 1,8 l : 0,40 m)
D_ROOM = WALL_IN + 887 / K_WALL      # la pièce, de la façade au mur de derrière : l'image d'un coin à l'autre
Z_E = 48.0                           # le mur du bout (l'angle de la façade est à 48,5 m)
CEIL = 3.1                           # le plafond ; le haut de l'image dessous
BACK_D, BACK_H = 0.45, 0.85          # le comptoir de travail contre le mur du bout
Z_M = Z_E - BACK_D - 0.45            # l'allée du maître (le milieu de son corps)
CTR_D, CTR_H = 0.6, 1.0              # le comptoir des clients : sa profondeur, son dessus
Z_C = Z_M - 0.4 - CTR_D              # (sa face, côté clients)
CTR_X = (-(X_F + D_ROOM) + 0.8, -(X_F + WALL_IN))   # (de 0,8 m du mur de derrière, le passage, au mur de façade)
POT = dict(x=470.0, w=0.7, d=0.4, h=0.13)   # la marmite : la colonne de la rue où tombe son milieu, sa largeur, sa profondeur,
                                     # sa hauteur au-dessus du comptoir
STOOLS = (dict(dx=-0.55), dict(dx=0.25))   # deux tabourets devant le comptoir (de tant de la marmite)
STOOL = dict(dz=0.32, r=0.17, top=0.68, leg=0.02)
SS = 8                               # (SS x SS rayons par pixel)
GRAIN = 0.05                         # (le grain : son écart, en clarté)
TINT = (1.03, 0.98, 0.92)            # (l'image dans la lumière de la boutique : un peu plus chaude)
CUT = (12, 85)                       # (éteinte : les centiles du verre d'avant, son plus sombre, son plus clair)
BARS_PEINTS = ((431, 586), (432, 586), (433, 586), (434, 586), (449, 584), (449, 585), (449, 593), (449, 594), (449, 595),
               (454, 609), (454, 610), (454, 611), (454, 612), (442, 585), (442, 595), (442, 605), (442, 615), (430, 580),
               (430, 581), (430, 582))   # (des pixels des barreaux peints : leur couleur, allumée et éteinte, celle des lattes)


def col_X(x, Z):                     # (la colonne x de la rue, à la profondeur Z : son X)
    return (x - VX) * Z / F


def zf(x):                           # (le x de la rue sur le plan de la façade : son Z ; le pixel x va de x à x + 1)
    return F * X_F / (VX - x)


def pot_at():
    """la marmite : son milieu (X, Z) et le haut de son bord"""
    Zp = Z_C + CTR_D / 2
    return col_X(POT['x'], Zp), Zp, CTR_H + POT['h']


def hems(lit):
    """l'ourlet du noren peint au-dessus de la porte : sa dernière rangée, colonne par colonne (son rouge) ; DOOR_TOP - 1 où il
    ne descend pas"""
    out = {}
    for x in range(DOOR[0][0], DOOR[1][1] + 1):
        c = lit[560:DOOR_TOP + 4, x, :3]
        red = [560 + i for i, (r, g, b) in enumerate(c) if r > 80 and g < 0.36 * r and b < 0.36 * r]
        out[x] = max(red[-1], DOOR_TOP - 1) if red and red[-1] >= DOOR_TOP - 2 else DOOR_TOP - 1
    return out


def sill(x):                         # (la dernière rangée de l'embrasure : trois au-dessus de la première du trottoir, sur le seuil)
    return int(np.ceil(VY + C_SEUIL * (VX - x))) - 3


def pixels(lit):
    """les pixels de la maquette : le verre de la porte (sous l'ourlet du noren, jusqu'à DOOR_BOT ; les montants de rencontre
    hors), celui de la fenêtre (de son haut, un rayon, à WIN_BOT), et l'embrasure du vantail de droite ouvert (OPEN, de sous
    l'ourlet au seuil). Rend les pixels et leur sorte : 'door' (le verre de la porte), 'win', 'open' (l'embrasure, hors verre)"""
    hm = hems(lit)
    kind = {}
    for a, b in DOOR:
        for x in range(a, b + 1):
            for y in range(hm[x] + 1, DOOR_BOT + 1): kind[(x, y)] = 'door'
    for x in range(OPEN[0], OPEN[1] + 1):
        for y in range(hm[x] + 1, sill(x) + 1): kind.setdefault((x, y), 'open')
    for x in range(WIN[0], WIN[1] + 1):
        for y in range(int(np.ceil(VY - WIN_TOP * (VX - x) - 0.5)), WIN_BOT + 1): kind[(x, y)] = 'win'
    pix = sorted(kind, key=lambda p: (p[1], p[0]))
    return np.array(pix), [kind[p] for p in pix], hm


def rays(pix):
    o = (np.arange(SS) + 0.5) / SS
    ox, oy = np.meshgrid(o, o)
    return (pix[:, 0:1] + ox.ravel()[None] - VX) / F, -(pix[:, 1:2] + oy.ravel()[None] - VY) / F


def render(src, pix):
    """la pièce sans le verre : ce que chaque rayon rencontre le premier (sa couleur, sa surface, sa profondeur). Surfaces : 1 le
    mur du bout, 2 le plafond, 4 le sol, 5 le comptoir des clients, 6 la marmite, 7 les tabourets, 8 le comptoir de travail et le
    mur de derrière"""
    DX, DY = rays(pix)
    sh = DX.shape
    Zh = np.full(sh, np.inf); col = np.zeros(sh + (3,)); sid = np.zeros(sh, int)
    def hit(Z, ok, c, k):
        nonlocal Zh, sid
        m = ok & (Z < Zh) & (Z > 0)
        Zh = np.where(m, Z, Zh); sid = np.where(m, k, sid)
        col[m] = np.broadcast_to(np.asarray(c, float), sh + (3,))[m]
    def look(img, u, v):
        return img[np.clip(np.floor(v).astype(int), 0, img.shape[0] - 1), np.clip(np.floor(u).astype(int), 0, img.shape[1] - 1)]
    def plane_h(hh):
        down = (hh - EYE) / np.where(DY != 0, DY, 1e-9)
        return np.where(down > 0, down, np.inf)
    XI, XB = -(X_F + WALL_IN), -(X_F + D_ROOM)                               # (le mur de façade dedans, le mur de derrière)
    inside = lambda Z: (DX * Z <= XI) & (DX * Z >= XB)
    wood = lambda u, v: look(src, u, v)
    # le mur du bout, de face : l'image du propriétaire d'un coin à l'autre, son haut sous le plafond
    Z = np.full(sh, Z_E); X = DX * Z; h = EYE + DY * Z
    hit(Z, inside(Z) & (h > 0) & (h < CEIL), look(src, 887 - (XI - X) * K_WALL, (CEIL - h) * K_WALL), 1)
    # le plafond : des planches le long de la rue (le bois sombre de l'image), plus sombre loin du mur du bout
    Zc = plane_h(CEIL); Xc = np.where(np.isfinite(Zc), DX * Zc, 0)
    q = (Xc - XI) / 0.18
    plank = np.where(np.floor(q) % 2 == 0, 1.0, 0.86) * np.where(q % 1 < 0.08, 0.7, 1.0)
    ceil_c = np.array([62., 32., 20.]) * (plank * (0.75 + 0.25 * np.clip(1 - (Z_E - np.where(np.isfinite(Zc), Zc, Z_E)) / 6, 0, 1)))[..., None]
    hit(Zc, inside(Zc) & (Zc < Z_E), ceil_c, 2)
    # le sol : des carreaux de terre cuite sombres, plus clairs vers la lumière du fond
    Zf = plane_h(0.0); Xf = np.where(np.isfinite(Zf), DX * Zf, 0); Zq = np.where(np.isfinite(Zf), Zf, 0)
    tile = np.where((np.floor(Xf / 0.3) + np.floor(Zq / 0.3)) % 2 == 0, 1.0, 0.9) * np.where((Xf / 0.3) % 1 < 0.07, 0.75, 1.0)
    floor_c = np.array([92., 50., 32.]) * (tile * (0.7 + 0.3 * np.clip(1 - (Z_E - Zq) / 10, 0, 1)))[..., None]
    hit(Zf, inside(Zf) & (Zf < Z_E), floor_c, 4)
    # le mur de derrière et le comptoir de travail (le bois de l'image)
    Zs = XB / DX; hit(Zs, (Zs < Z_E) & (EYE + DY * Zs > 0) & (EYE + DY * Zs < CEIL), np.array([70., 36., 22.]), 8)
    Zb = np.full(sh, Z_E - BACK_D); hit(Zb, inside(Zb) & (EYE + DY * Zb <= BACK_H), np.array([60., 30., 20.]), 8)
    # le comptoir des clients : sa face de planches (le bois du bas de l'image, ses joints), plus sombre vers le sol ; son dessus
    cx0, cx1 = CTR_X
    Z = np.full(sh, Z_C); X = DX * Z; h = EYE + DY * Z
    face = wood(60 + ((X - cx0) * K_WALL) % 760, 1500 + np.clip(CTR_H - h, 0, 0.6) * 300) * (0.55 + 0.35 * np.clip(h / CTR_H, 0, 1))[..., None]
    hit(Z, (X >= cx0) & (X <= cx1) & (h <= CTR_H) & (h >= 0), face, 5)
    Zt = plane_h(CTR_H); Xt = DX * Zt
    hit(Zt, (Zt >= Z_C) & (Zt <= Z_C + CTR_D) & (Xt >= cx0) & (Xt <= cx1), np.array([170., 96., 52.]), 5)
    # la marmite (l'inox de l'image) posée sur le comptoir
    Xp, Zp, hp = pot_at()
    Z = np.full(sh, Zp - POT['d'] / 2); X = DX * Z; h = EYE + DY * Z
    hit(Z, (np.abs(X - Xp) <= POT['w'] / 2) & (h >= CTR_H) & (h <= hp), np.array([150., 128., 104.]), 6)
    Zt = plane_h(hp); Xt = DX * Zt
    hit(Zt, (np.abs(Xt - Xp) <= POT['w'] / 2) & (np.abs(Zt - Zp) <= POT['d'] / 2), np.array([214., 160., 96.]), 6)
    # les tabourets : un coussin rond (le bleu à vagues de l'image), quatre pieds de bois
    for s in STOOLS:
        Zs0, Xs = Z_C - STOOL['dz'], Xp + s['dx']
        bb = -2 * (DX * Xs + Zs0); cc = Xs * Xs + Zs0 * Zs0 - STOOL['r'] ** 2; aa = DX * DX + 1
        disc = bb * bb - 4 * aa * cc
        Zy = np.where(disc >= 0, (-bb - np.sqrt(np.maximum(disc, 0))) / (2 * aa), np.inf); hy = EYE + DY * Zy
        hit(Zy, (hy <= STOOL['top']) & (hy >= STOOL['top'] - 0.08), np.array([62., 52., 92.]), 7)
        for ex, ez in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            lx, lz = Xs + ex * 0.11, Zs0 + ez * 0.11
            bb = -2 * (DX * lx + lz); cc = lx * lx + lz * lz - STOOL['leg'] ** 2
            disc = bb * bb - 4 * aa * cc
            Zl = np.where(disc >= 0, (-bb - np.sqrt(np.maximum(disc, 0))) / (2 * aa), np.inf)
            hit(Zl, EYE + DY * Zl <= STOOL['top'] - 0.08, np.array([150., 86., 46.]) * (1.0 if ez < 0 else 0.7), 7)
    return col, sid, Zh


def door_bars():
    """les lattes d'aplomb de la porte : leur Z, aux tiers de chaque vantail"""
    out = []
    for a, b in DOOR:
        z0, z1 = zf(a), zf(b + 1)
        out += [z0 + (z1 - z0) * k / 3 for k in (1, 2)]
    return out


def frames_cov(pix, kind, which='both'):
    """la part de chaque pixel que couvrent les montants (sur SS x SS rayons) : sur la porte les lattes de ses deux vantaux
    fermés (which 'left' : du seul vantail de gauche), sur la fenêtre ses montants de rencontre. Un rayon traverse l'épaisseur de la
    façade de Z0 à Z1 : une latte d'aplomb en Zb le coupe si [Z0, Z1] touche [Zb - w/2, Zb + w/2] ; une traverse, si le rayon y
    passe à sa hauteur"""
    DX, DY = rays(pix)
    Z0, Z1 = X_F / -DX, (X_F + KUMI['d']) / -DX
    door = np.array([k in ('door', 'open') for k in kind])[:, None]
    hitm = np.zeros(DX.shape, bool)
    zr = zf(DOOR[1][0])                                                      # (le vantail de droite : son bord de verre)
    for i, zb in enumerate(door_bars()):
        if which == 'left' and i >= 2: continue
        hitm |= door & (Z1 >= zb - KUMI['w'] / 2) & (Z0 <= zb + KUMI['w'] / 2)
    ha, hb = EYE + DY * Z0, EYE + DY * Z1
    for hr in KUMI['rails']:
        on = door & (np.maximum(ha, hb) >= hr - KUMI['w'] / 2) & (np.minimum(ha, hb) <= hr + KUMI['w'] / 2)
        hitm |= on & (Z0 < zr - 0.07) if which == 'left' else on
    if which == 'both':
        win = ~door
        zm = (zf(WIN[0]) + zf(WIN[1] + 1)) / 2
        for k, (za, zb) in enumerate(((zm - MEET['w'], zm), (zm, zm + MEET['w']))):   # (le châssis de devant, celui de derrière)
            Za, Zb_ = (X_F + k * MEET['d']) / -DX, (X_F + (k + 1) * MEET['d']) / -DX
            hitm |= win & (Zb_ >= za) & (Za <= zb)
    return hitm.mean(1)


def reduce(col, sid):
    """au pixel entier : la surface qui en tient le plus ; dedans, là où ses rayons font deux groupes nets, la couleur du groupe
    qui en tient 60 % ou plus, sinon leur moyenne ; un éclat (le cœur d'une lanterne) gardé dans son pixel"""
    out = np.zeros((col.shape[0], 3)); acc = np.zeros(col.shape[0], bool); surf = np.zeros(col.shape[0], int)
    for i in range(col.shape[0]):
        ids, n = np.unique(sid[i], return_counts=True)
        k = surf[i] = ids[np.argmax(n)]
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


def around(xs, ys, v):
    """l'écart de v sur chaque pixel et ses voisins de la maquette (3 x 3)"""
    x0, y0 = xs.min() - 1, ys.min() - 1
    S1 = np.zeros((ys.max() - y0 + 2, xs.max() - x0 + 2)); S2 = S1.copy(); N = S1.copy()
    S1[ys - y0, xs - x0] = v; S2[ys - y0, xs - x0] = v * v; N[ys - y0, xs - x0] = 1
    box = lambda A: sum(A[a + ys - y0, b + xs - x0] for a in (-1, 0, 1) for b in (-1, 0, 1))
    n = box(N); m = box(S1) / n
    return np.sqrt(np.maximum(box(S2) / n - m * m, 0))


def model():
    """la maquette rendue : ses pixels, leur sorte, leur couleur allumée et éteinte, leur surface et leur profondeur ; les
    barreaux de la porte fermée"""
    src = np.asarray(Image.open(SRC).convert('RGB')).astype(float)
    B = [I.load(n, 'RGBA', BEFORE) for n in ('layer_city_off.webp', 'street_unlit.webp')]
    pix, kind, hm = pixels(B[0])
    xs, ys = pix[:, 0], pix[:, 1]
    col, sid, Zh = render(src * np.array(TINT), pix)
    rgb, acc, surf = reduce(col, sid)
    depth = np.array([np.median(Zh[i][sid[i] == surf[i]]) for i in range(len(pix))])
    bar = (frames_cov(pix, kind) >= 0.3) & np.array([k != 'open' for k in kind])

    # la palette de la boutique : son verre allumé d'avant (porte et fenêtre), son noren peint, sa lanterne allumée
    Pg = [B[0][y, x, :3] for (x, y), k in zip(pix, kind) if k != 'open']
    nb = B[0][560:578, 432:460, :3].reshape(-1, 3)
    la = I.load('oden_lantern.webp', 'RGBA'); la = la[la[..., 3] > 250][:, :3]
    pal = R.palette(list(Pg) + list(nb) + list(la[::7]), 40)
    BAR_LIT = np.median([B[0][y, x, :3] for x, y in BARS_PEINTS], 0); BAR_CUT = np.median([B[1][y, x, :3] for x, y in BARS_PEINTS], 0)

    # le grain du peintre : une tache par pixel, fixe ; plein sur ce qui est uni, léger sur ce qui est chargé ; jamais un saut de
    # plus d'une marche de la palette
    Lsd = around(xs, ys, rgb @ I.LUM)
    gx0, gy0 = xs.min(), ys.min()
    g = np.random.default_rng(2511).normal(0, 1, (ys.max() - gy0 + 3, xs.max() - gx0 + 3))
    g = 0.7 * g[1:-1, 1:-1] + 0.15 * (g[:-2, 1:-1] + g[1:-1, :-2] + g[2:, 1:-1] + g[1:-1, 2:])
    g = (g / g.std())[ys - gy0, xs - gx0]
    amp = GRAIN * (0.3 + 0.7 * np.clip(1 - Lsd / 16, 0, 1))
    i0 = R.nearest(rgb, pal); i1 = R.nearest(np.clip(rgb * np.exp(amp * g)[:, None], 0, 255), pal)
    far = ((R.lab(pal[i0]) - R.lab(pal[i1])) ** 2).sum(1) > 14 ** 2
    lit = pal[np.where(acc | far, i0, i1)]
    Ll = lit @ I.LUM

    # éteinte (street_unlit) : le bleu nuit du verre éteint d'avant, de son plus sombre à son plus clair (CUT : ses centiles)
    # selon la clarté de la pièce allumée, à ses couleurs ; son grain plus léger, d'une marche au plus
    Cb = np.array([B[1][y, x, :3] for (x, y), k in zip(pix, kind) if k != 'open']); Lb = Cb @ I.LUM
    lo, hi = Cb[Lb <= np.percentile(Lb, CUT[0])].mean(0), Cb[Lb >= np.percentile(Lb, CUT[1])].mean(0)
    t = np.clip((Ll - 30) / 170, 0, 1) ** 0.9
    cut_c = lo + (hi - lo) * t[:, None]
    cpal = R.palette(Cb, 16)
    j0 = R.nearest(cut_c, cpal); j1 = R.nearest(np.clip(cut_c * np.exp(0.5 * amp * g)[:, None], 0, 255), cpal)
    cut = cpal[np.where(((R.lab(cpal[j0]) - R.lab(cpal[j1])) ** 2).sum(1) > 6 ** 2, j0, j1)]
    STILE = np.median([B[0][y, DOOR[1][0] - 1, :3] for y in range(582, DOOR_BOT)], 0)   # (le montant de rencontre du vantail de
    return dict(pix=pix, kind=kind, hm=hm, lit=lit, cut=cut, surf=surf, depth=depth, bar=bar, pal=pal, B=B,    # droite, peint : x 443)
                bar_lit=BAR_LIT, bar_cut=BAR_CUT, stile=STILE)


# ---- le vantail de droite qui coule vers la gauche, derrière celui de gauche
def slides():
    """les pas du coulissement : à chaque image son bord arrière (sur la gâche, x 458,5 fermé) un pixel plus à gauche, jusqu'à
    la rencontre (x 442,5) ; leur décalage s (m vers nous)"""
    z_tr = zf(DOOR[1][1] + 1)
    return [z_tr - zf(DOOR[1][1] + 1 - k) for k in range(DOOR[1][1] - DOOR[1][0] + 3)]


def panel(M, s, region):
    """le vantail de droite décalé de s : sur chaque pixel de region (x0, y0, w, h), ce qu'on en voit (SS x SS rayons sur le
    plan de la façade) : ses lattes, ses montants (le sien à la rencontre, x 443 fermé, et celui de son autre bord, sous la
    gâche fermé), son bas (le bois peint sous le verre, pris là où il était) ; ailleurs rien (son verre, ou hors de lui).
    RGBA, la couleur allumée"""
    x0, y0, w, h = region
    pix = np.array([(x, y) for y in range(y0, y0 + h) for x in range(x0, x0 + w)])
    DX, DY = rays(pix)
    Z = X_F / -DX; hh = EYE + DY * Z; Zl = Z + s                            # (sur la façade ; le point du vantail fermé)
    za, zb = zf(DOOR[1][0] - 1), zf(DOOR[1][1] + 1)                         # (le vantail fermé : de la rencontre à la gâche)
    zs = zf(DOOR[1][0])                                                     # (son montant de rencontre, x 443 : de za à zs)
    h_gb = EYE - (DOOR_BOT + 1 - VY) * zf(450.5) / F                        # (le bas de son verre)
    h_top = EYE + (VY - DOOR_TOP) * zf(450.5) / F + 0.1
    inpan = (Zl >= za) & (Zl <= zb + 0.12) & (hh >= 0) & (hh <= h_top)
    stile = inpan & ((Zl < zs) | (Zl > zb))
    low = inpan & ~stile & (hh < h_gb)
    Z0, Z1 = X_F / -DX, (X_F + KUMI['d']) / -DX                            # (ses lattes : comme fermées, décalées de s)
    bars = np.zeros(DX.shape, bool)
    for zbar in door_bars()[2:]:
        bars |= (Z1 + s >= zbar - KUMI['w'] / 2) & (Z0 + s <= zbar + KUMI['w'] / 2)
    ha, hb = EYE + DY * Z0, EYE + DY * Z1
    for hr in KUMI['rails']:
        bars |= (np.maximum(ha, hb) >= hr - KUMI['w'] / 2) & (np.minimum(ha, hb) <= hr + KUMI['w'] / 2)
    bars &= inpan & ~stile & ~low
    lit = M['B'][0]
    out = np.zeros((h, w, 4))
    for i, (x, y) in enumerate(pix):
        fb, fs, fl = bars[i].mean(), stile[i].mean(), low[i].mean()
        if fl >= 0.5:                                                        # (le bois du bas : son pixel peint, là où il était)
            zz = np.median(Zl[i][low[i]]); hq = np.median(hh[i][low[i]])
            sx = int(np.clip(np.floor(VX - F * X_F / zz), DOOR[1][0], DOOR[1][1])); sy = int(np.floor(VY - (hq - EYE) * F / zz))
            out[y - y0, x - x0] = list(lit[sy, sx, :3]) + [255]
        elif fs >= 0.4:
            out[y - y0, x - x0] = list(M['stile']) + [255]
        elif fb >= 0.3:
            out[y - y0, x - x0] = list(M['bar_lit']) + [255]
    return out


def main():
    prev = sys.argv[sys.argv.index('--preview') + 1] if '--preview' in sys.argv else None
    M = model()
    names = (('layer_city_off.webp', 'RGBA'), ('street_unlit.webp', 'RGBA'))
    Lc = [I.load(n, m) for n, m in names]
    zx0, zy0, zx1, zy1 = ZONE
    for l, b in zip(Lc, M['B']): l[zy0:zy1, zx0:zx1] = b[zy0:zy1, zx0:zx1]       # (la zone comme avant)
    for i, ((x, y), k) in enumerate(zip(M['pix'], M['kind'])):
        if k == 'open': continue
        Lc[0][y, x, :3] = M['bar_lit'] if M['bar'][i] else M['lit'][i]
        Lc[1][y, x, :3] = M['bar_cut'] if M['bar'][i] else M['cut'][i]

    # le verre de la fenêtre (la vapeur)
    wm = np.zeros((WIN_M[3], WIN_M[2], 4), np.uint8); wm[..., :3] = 255
    for i, ((x, y), k) in enumerate(zip(M['pix'], M['kind'])):
        if k == 'win' and not M['bar'][i]: wm[y - WIN_M[1], x - WIN_M[0], 3] = 255
    # ce que street.js pose sur la porte et la fenêtre (BOX) : le verre porte fermée, porte ouverte (l'embrasure du vantail de
    # droite jusqu'au seuil, le verre de gauche sans ses lattes) ; la pièce dans l'embrasure ; le vantail à chaque pas
    bx, by, bw, bh = BOX
    shut, opn = np.zeros((bh, bw), bool), np.zeros((bh, bw), bool)
    left_bar = frames_cov(M['pix'], M['kind'], 'left') >= 0.3
    for i, ((x, y), k) in enumerate(zip(M['pix'], M['kind'])):
        if k in ('door', 'win') and not M['bar'][i]: shut[y - by, x - bx] = True
        if k == 'win' and not M['bar'][i]: opn[y - by, x - bx] = True
        if k == 'door' and x <= DOOR[0][1] and not left_bar[i]: opn[y - by, x - bx] = True
        if x >= OPEN[0] and k in ('door', 'open'): opn[y - by, x - bx] = True
    ox0, oy0 = OPEN[0], min(M['hm'][x] for x in range(OPEN[0], OPEN[1] + 1)) + 1
    ow, oh = OPEN[1] - OPEN[0] + 1, max(sill(x) for x in range(OPEN[0], OPEN[1] + 1)) - oy0 + 1
    room = np.zeros((oh, ow, 4))
    for i, ((x, y), k) in enumerate(zip(M['pix'], M['kind'])):
        if x >= OPEN[0] and k in ('door', 'open'): room[y - oy0, x - ox0] = list(M['lit'][i]) + [255]
    PR = (DOOR[0][0] - 3, oy0, DOOR[1][1] - DOOR[0][0] + 6, oh + 1)            # (le vantail : la boîte de ses images)
    S = slides()
    pans = [panel(M, s, PR) for s in S]
    agree = [bool(pans[0][y - PR[1], x - PR[0], 3] > 0) == bool(b) for (x, y), k, b in zip(M['pix'], M['kind'], M['bar'])
             if k == 'door' and x >= DOOR[1][0]]                             # (fermé, le vantail a ses lattes là où les calques ont les leurs)
    A_W = bw * 2 + ow + 1
    A_H = max(bh, oh)
    atlas = np.zeros((A_H + (PR[3] + 1) * ((len(pans) + 2) // 3), max(A_W, (PR[2] + 1) * 3), 4))
    atlas[:bh, :bw] = np.where(shut[..., None], 255.0, 0.0); atlas[:bh, bw:2 * bw] = np.where(opn[..., None], 255.0, 0.0)
    atlas[:oh, 2 * bw + 1:2 * bw + 1 + ow] = room
    cells = []
    for i, p in enumerate(pans):
        cx, cy = (i % 3) * (PR[2] + 1), A_H + 1 + (i // 3) * (PR[3] + 1)
        atlas[cy:cy + PR[3], cx:cx + PR[2]] = p; cells.append([cx, cy])
    Xp, Zp, hp = pot_at()
    ODM = {'box': list(BOX), 'shut': [0, 0], 'open': [bw, 0], 'room': [2 * bw + 1, 0, ow, oh, ox0, oy0],
           'pan': {'box': list(PR), 'cells': cells, 'x': [DOOR[1][1] + 1 - k for k in range(len(S))]},
           'pot': [round(VX + F * (Xp - POT['w'] / 2) / Zp, 1), round(VX + F * (Xp + POT['w'] / 2) / Zp, 1), round(VY - (hp - EYE) * F / Zp, 1),
                   round(F / Zp, 2)]}
    print('façade à X_F %.2f m de l\'œil ; porte de Z %.2f à %.2f m, fenêtre de %.2f à %.2f m ; mur du bout à Z %.2f m (%.1f px par mètre), '
          'la pièce de %.2f m de fond, %.0f px de l\'image par mètre ; comptoir de Z %.2f à %.2f (dessus %.2f m), maître à Z %.2f (%.1f px/m), '
          'marmite en X %.2f Z %.2f (bord à %.2f m : rangée %.1f) | %d pixels, %d de barreaux, palette %d ; le vantail en %d pas, fermé '
          'comme les calques sur %d pixels de verre sur %d' % (
              X_F, zf(DOOR[0][0]), zf(DOOR[1][1] + 1), zf(WIN[0]), zf(WIN[1] + 1), Z_E, F / Z_E, D_ROOM, K_WALL,
              Z_C, Z_C + CTR_D, CTR_H, Z_M, F / Z_M, Xp, Zp, hp, VY - (hp - EYE) * F / Zp, len(M['pix']), M['bar'].sum(), len(M['pal']), len(S),
              sum(agree), len(agree)))
    if prev:
        for k, im in (('lit', Lc[0]), ('cut', Lc[1])):
            Image.fromarray(np.clip(im[550:680, 410:510, :3], 0, 255).astype(np.uint8)).resize((800, 1040), Image.NEAREST).save(os.path.join(prev, k + '_x8.png'))
        Image.fromarray(np.clip(np.round(atlas), 0, 255).astype(np.uint8), 'RGBA').save(os.path.join(prev, 'door_atlas.png'))
        json.dump(ODM, open(os.path.join(prev, 'odm.json'), 'w'))
        return
    for (n, m), l in zip(names, Lc): I.save(l, n, m)
    Image.fromarray(wm, 'RGBA').save(I.A('oden_window.webp'), 'WEBP', lossless=True, quality=100, method=6, exact=True)
    Image.fromarray(np.clip(np.round(atlas), 0, 255).astype(np.uint8), 'RGBA').save(I.A('oden_door.webp'), 'WEBP', lossless=True, quality=100, method=6, exact=True)
    js = open(JS, encoding='utf-8').read()
    line = 'const ODM = ' + json.dumps(ODM, separators=(',', ':')) + ';'
    js2, n = re.subn(r'const ODM = \{.*?\};', lambda m: line, js, count=1)
    assert n == 1, 'la ligne ODM manque dans assets/street.js'
    if js2 != js: open(JS, 'w', encoding='utf-8').write(js2)


if __name__ == '__main__':
    main()
