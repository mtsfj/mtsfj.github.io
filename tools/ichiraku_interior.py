#!/usr/bin/env python3
"""Ichiraku : derrière les portes vitrées, la boutique en petite maquette 3D, vue par l'œil de la rue.

    python3 tools/ichiraku_interior.py                  (il reprend sa zone au commit BEFORE à chaque fois, on peut donc le
                                                          relancer : il écrit la même chose)
    python3 tools/ichiraku_interior.py --preview dossier (des aperçus seulement, rien d'écrit dans assets/)

La caméra de la rue est une perspective à un point : focale F = 1400 px, point de fuite VP (700, 615), l'œil à EYE = 1,5 m
du trottoir. La façade du ramen est à droite de la rue et court vers VP ; ses deux portes coulissantes vitrées en sont (quatre
vitres en largeur, VITRES : leurs colonnes de verre ; une traverse entre le haut et le bas, TRAVERSE). Le seuil des portes
(SEUIL : la première rangée du trottoir sous elles, mesurée colonne par colonne) est sur des rayons vers VP à 1,5 m sous
l'œil : la façade est à X_F = 5,53 m à droite de l'œil, les portes de Z = 14,8 à 16,8 m le long de la rue ; le bas des
vitres (BAS_RAYON) à 0,69 m du trottoir, la traverse à 1,29 m, l'ourlet du noren à 1,74 m.

La boutique, une boîte derrière la façade (D_ROOM de fond, le plafond à CEIL). Par une porte de côté, un rayon file le long de
la rue (un tiers de mètre vers le fond pour un mètre le long de la rue) : ce qu'il rencontre au bout est le mur du bout de la
boutique, de travers à la rue, donc de face (ses horizontales horizontales), et on ne voit qu'une bande de la pièce. Le
comptoir des clients est de face lui aussi, son dessus à CTR_H = 1 m : son arête sur la rangée CTR_ROW = 641, la ligne où
assets/street.js coupe Teuchi (inchangée), le met à Z_C = 26,3 m ; derrière lui l'allée de Teuchi (AISLE), le comptoir de
travail (BACK_D, caché par celui des clients), le mur du bout à Z_E = 28,4 m (11,5 m derrière la porte, 49 px par mètre).
L'image du propriétaire (tools/src/ichiraku_room.webp : étagères, bouteilles, bols, bocaux, casseroles et louches, la
marmite) est posée sur ce mur à K_WALL = 230 pixels de l'image par mètre (ses étagères à 30 cm l'une de l'autre en
moyenne, ses bouteilles de 35 à 40 cm, ses bols de 20 cm), le haut de son comptoir de travail (V_REF) à 0,9 m, glissée
pour que sa marmite soit derrière la troisième vitre (POT). Par le verre, sous le noren, on en voit une bande de 1,3 m de
large, de 1 m à 1,9 m de haut : les casseroles et les louches, la marmite à couvercle, des bocaux, l'armoire aux bols, le
haut de la grande marmite. Sur le
comptoir des clients, des objets de l'image (OBJETS : deux bols, chacun devant son tabouret, celui du milieu et celui de
Naruto ; un verre, des condiments, une bouteille ; de face, posés sur son dessus, à l'échelle d'un bol de 21 cm, K_OBJ ; leur
silhouette, shape_ok) ; sa face en planches (PLANK : leur ton tiré
des planches de l'image, leurs joints), à l'ombre sous son arête, plus sombre vers le sol ; le retrait du pied, la barre pour
les pieds (RAIL). Devant lui, trois tabourets (STOOLS : sous le client du coin, sous Naruto, un entre eux) : un coussin rond
rouge, quatre pieds, l'anneau. Au-dessus du comptoir, pendue à 1,6 m, une lanterne de l'image (LANTERN). Le plafond et le sol
ne se voient pas par ces vitres (la maquette les a quand même) : les rayons du verre montent d'au plus 1,7 % et descendent
d'au plus 5,4 %, ils rencontrent le comptoir ou le mur du bout bien avant.

Le rendu. Chaque pixel du verre (de sous l'ourlet du noren, son image au repos, à la traverse ; de la traverse à la rangée
au-dessus de la lisière claire du bas) est pris sur SS x SS rayons de l'œil, puis ramené au pixel entier selon ses bords
(reduce : les surfaces nettes, les éclats gardés). La lumière : le haut à l'ombre du noren (HAUT), la vapeur au-dessus de la
marmite plus claire (STEAM). Le grain du peintre (GRAIN : fixe, plein sur l'uni, léger sur le chargé), puis chaque pixel
ramené à la palette de la boutique (40 couleurs tirées de son verre allumé d'avant, du noren et des lanternes allumés), un
grain ne sautant jamais plus d'une marche. Les arêtes claires des montants contre le verre (ARETES) gardent leurs pixels, à
la lumière de la nouvelle pièce.

Dans layer_city_off (allumée) ; street_unlit (la coupure de courant : la même pièce dans le bleu nuit du verre coupé, de son
plus sombre à son plus clair selon la clarté de la pièce allumée, à ses couleurs) ; assets/shop_off.webp (fermée : tout le
verre couvert de son bleu nuit, posé à 0,88, la pièce allumée n'y passe qu'à 12 %) ; assets/ramen_glass.webp (le masque du
verre où passent les ombres de Teuchi et du client, la lumière de la pièce qui respire et la vapeur : plein au-dessus du
comptoir, un peu moins sur le plus sombre, MASK ; une part égale sur sa face, sous la ligne des figures ; sous l'ourlet,
rien ailleurs que sur le verre : ni sur les montants, ni sur la traverse, ni sur la lisière du bas). Le noren peint
au-dessus de l'ourlet, les montants, la traverse, la façade : tels qu'au commit BEFORE. night_far et street_sun : 0 ici,
tels quels. Il faut git, Pillow, numpy.
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
BEFORE = '402ebae'                   # (les calques avant l'outil d'Ichiraku : sa zone reprise de là à chaque fois)
ZONE = (1150, 590, 1232, 700)        # x0, y0, x1, y1 : les vitres et leur cadre
SHOP_OFF, GLASS = (1112, 448), (1150, 520)   # (shop_off.webp, ramen_glass.webp : leur place)

# ---- la caméra de la rue, la façade et ses portes
F, VX, VY, EYE = 1400.0, 700.0, 615.0, 1.5
SEUIL = ((1160, 744), (1170, 744), (1180, 746), (1190, 747), (1200, 749), (1210, 751), (1220, 753))
X_F = EYE / float(np.mean([(y - VY) / (x - VX) for x, y in SEUIL]))
VITRES = ((1160, 1170), (1173, 1185), (1192, 1205), (1209, 1223))   # les colonnes de verre de chaque vitre (les montants entre)
ARETES = ((1159, 1160), (1186, 1185), (1191, 1192), (1206, 1205), (1208, 1209), (1224, 1223))   # (l'arête claire d'un montant,
                                     # la colonne de verre contre elle)
TRAVERSE = (631, 636)                # la dernière rangée de verre au-dessus de la traverse, la première au-dessous
BAS_RAYON = 0.1467                   # la lisière claire du bas des vitres : y = VP_y + c |x - VP_x| (le verre s'arrête au-dessus)
NOREN = ('ichiraku_noren.webp', 1155, 500, 79, 104)   # (le noren au repos : son ourlet, colonne par colonne)

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


def glass_pixels():
    """le verre : chaque colonne des vitres, de sous l'ourlet du noren (son image au repos) à la traverse, puis de la traverse
    à la rangée au-dessus de la lisière claire du bas (un rayon vers VP)"""
    nr = I.load(NOREN[0], 'RGBA')[:NOREN[4], :NOREN[3], 3]
    pix, hem = [], {}
    for a, b in VITRES:
        for x in range(a, b + 1):
            hem[x] = NOREN[2] + int(np.max(np.where(nr[:, x - NOREN[1]] > 0)[0]))
            bot = int(np.round(VY + BAS_RAYON * (x - VX) - 0.5)) - 1
            for y in list(range(hem[x] + 1, TRAVERSE[0] + 1)) + list(range(TRAVERSE[1], bot + 1)):
                pix.append((x, y))
    return np.array(pix), hem


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
    Zc = plane_h(CEIL); hit(Zc, (Zc < Z_E) & (DX * Zc < X_F + D_ROOM), np.array([40., 20., 14.]), 10)
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


def main():
    prev = sys.argv[sys.argv.index('--preview') + 1] if '--preview' in sys.argv else None
    src = np.asarray(Image.open(SRC).convert('RGB')).astype(float)
    names = (('layer_city_off.webp', 'RGBA'), ('street_unlit.webp', 'RGBA'))
    Lc = [I.load(n, m) for n, m in names]; B = [I.load(n, m, BEFORE) for n, m in names]
    zx0, zy0, zx1, zy1 = ZONE
    for l, b in zip(Lc, B): l[zy0:zy1, zx0:zx1] = b[zy0:zy1, zx0:zx1]       # (la zone comme avant)
    so = I.load('shop_off.webp', 'RGBA', BEFORE); gl = I.load('ramen_glass.webp', 'RGBA', BEFORE)
    pix, hem = glass_pixels()
    xs, ys = pix[:, 0], pix[:, 1]
    col, sid = render(src * np.array(TINT), pix)
    rgb, acc, surf = reduce(col, sid)

    # la palette de la boutique : son verre allumé (BEFORE), le noren et les lanternes allumés
    P = [B[0][y, x, :3] for x, y in pix if y >= 599]
    nr = I.load(NOREN[0], 'RGBA'); n1 = nr[NOREN[4]:2 * NOREN[4], :NOREN[3]]; P += list(n1[n1[..., 3] > 250][:, :3])
    la = I.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'edits', 'lanterns_before.webp'), 'RGBA')   # (the paper lanterns' atlas this was built from)
    for r in (1, 4):
        c = la[r * 84:(r + 1) * 84, 15 * 48:16 * 48]; P += list(c[c[..., 3] > 250][:, :3])
    pal = palette(P, 40)

    # la lumière : le haut à l'ombre du noren, la vapeur au-dessus de la marmite plus claire
    d = ys - np.array([hem[x] for x in xs])
    rgb = rgb * np.array(HAUT + (1.0,))[np.minimum(d, len(HAUT) + 1) - 1][:, None]
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
    Cb = np.array([B[1][y, x, :3] for x, y in pix if y >= 599]); Lb = Cb @ I.LUM
    lo, hi = Cb[Lb <= np.percentile(Lb, CUT[0])].mean(0), Cb[Lb >= np.percentile(Lb, CUT[1])].mean(0)
    t = np.clip((Ll * np.where(surf == 8, 0.45, 1.0) - 30) / 170, 0, 1) ** 0.9   # (la lanterne éteinte)
    cut_c = lo + (hi - lo) * t[:, None]
    cpal = palette(Cb, 20)
    j0 = nearest(cut_c, cpal); j1 = nearest(np.clip(cut_c * np.exp(0.5 * amp * g)[:, None], 0, 255), cpal)
    cut = cpal[np.where(((lab(cpal[j0]) - lab(cpal[j1])) ** 2).sum(1) > 6 ** 2, j0, j1)]

    # fermée (shop_off, posé à 0,88) : tout le verre couvert de son bleu nuit, la pièce allumée n'y passe qu'à 12 %. Le masque
    # du verre (ramen_glass : les ombres de Teuchi et du client, la lumière de la pièce qui respire, la vapeur) : plein sur ce
    # qu'on voit au-dessus du comptoir, un peu moins sur le plus sombre (sa clarté prise sur ses voisins : pas de pixel isolé) ;
    # sur la face du comptoir, sous les figures coupées à sa hauteur, une part égale (la lumière seule)
    Ls = around(xs, ys, Ll)[0]
    a_gl = np.where(ys <= CTR_ROW, np.interp(Ls, MASK[0], MASK[1]), MASK[2])
    old = B[0].copy()
    nr0 = I.load(NOREN[0], 'RGBA')[:NOREN[4], :NOREN[3], 3]
    for x in range(zx0, min(zx1, GLASS[0] + gl.shape[1])):                    # (sous l'ourlet, le masque n'est que sur le verre : rien
        c = x - NOREN[1]                                                     # sur les montants, la traverse, la lisière du bas)
        top = NOREN[2] + int(np.max(np.where(nr0[:, c] > 0)[0])) + 1 if 0 <= c < NOREN[3] and nr0[:, c].max() else zy0
        gl[top - GLASS[1]:zy1 - GLASS[1], x - GLASS[0], 3] = 0
    for i, (x, y) in enumerate(pix):
        Lc[0][y, x, :3] = lit[i]; Lc[1][y, x, :3] = cut[i]
        so[y - SHOP_OFF[1], x - SHOP_OFF[0]] = (14, 9, 22, 255)
        if y - GLASS[1] < gl.shape[0]: gl[y - GLASS[1], x - GLASS[0]] = (255, 255, 255, a_gl[i])
    # les arêtes claires des montants contre le verre : la lumière de la nouvelle pièce
    k5 = np.ones(5) / 5
    for ex, gx in ARETES:
        rows = [y for x, y in pix if x == gx]
        new = np.array([Lc[0][y, gx, :3] @ I.LUM for y in rows]); was = np.array([old[y, gx, :3] @ I.LUM for y in rows])
        sm = lambda v: np.convolve(np.pad(v, 2, mode='edge'), k5, 'valid')
        r = np.clip(sm(new) / np.maximum(sm(was), 1), 0.45, 1.2)
        for y, rr in zip(rows, r): Lc[0][y, ex, :3] = np.round(old[y, ex, :3] * rr)

    print('façade à X_F %.2f m de l\'œil ; portes de Z %.2f à %.2f m ; comptoir à Z %.2f m (dessus à %.2f m, rangée %d) ; mur du '
          'bout à Z %.2f m (%.2f m derrière la porte), %.1f px par mètre ; pièce de %.1f m de fond | %d pixels de verre, %d éclats, '
          'palette %d couleurs' % (X_F, F * X_F / (VITRES[0][0] - VX), F * X_F / (VITRES[-1][1] - VX), Z_C, CTR_H, CTR_ROW, Z_E,
                                   Z_E - F * X_F / (VITRES[0][0] - VX), F / Z_E, D_ROOM, len(pix), acc.sum(), len(pal)))
    if prev:
        for k, im in (('lit', Lc[0]), ('cut', Lc[1])):
            Image.fromarray(np.clip(im[580:705, 1140:1240, :3], 0, 255).astype(np.uint8)).resize((800, 1000), Image.NEAREST).save(os.path.join(prev, k + '_x8.png'))
        bl = Lc[0][..., :3].copy(); sa = so[..., 3:] / 255 * 0.88
        bl[448:448 + 248, 1112:1112 + 164] = bl[448:448 + 248, 1112:1112 + 164] * (1 - sa) + so[..., :3] * sa
        Image.fromarray(np.clip(bl[580:705, 1140:1240], 0, 255).astype(np.uint8)).resize((800, 1000), Image.NEAREST).save(os.path.join(prev, 'shut_x8.png'))
        ga = np.zeros((125, 100, 3)); ga[:110, 10:90] = gl[60:170, :, 3:]
        Image.fromarray(ga.astype(np.uint8)).resize((800, 1000), Image.NEAREST).save(os.path.join(prev, 'mask_x8.png'))
        Image.fromarray(np.repeat(np.repeat(pal[None].astype(np.uint8), 20, 0), 20, 1)).save(os.path.join(prev, 'palette.png'))
        return
    for (n, m), l in zip(names, Lc): I.save(l, n, m)
    I.save(so, 'shop_off.webp', 'RGBA'); I.save(gl, 'ramen_glass.webp', 'RGBA')


if __name__ == '__main__':
    main()
