#!/usr/bin/env python3
"""Le dagashi-ya (sous la façade de Kirua) : par sa porte ouverte et la vitre de sa porte fermée, la boutique en petite maquette
3D, vue par l'œil de la rue.

    python3 tools/dagashi_interior.py                  (il reprend sa zone au commit BEFORE à chaque fois, on peut donc le
                                                         relancer : il écrit la même chose)
    python3 tools/dagashi_interior.py --preview dossier (des aperçus seulement, rien d'écrit dans assets/)

Il remplace tools/dagashi_front.py (qui redressait la pièce peinte) : même zone, même commit BEFORE, mêmes calques.

La caméra de la rue est une perspective à un point : focale F = 1400 px, point de fuite VP (700, 615), l'œil à EYE = 1,5 m du
trottoir. La devanture est sur la façade de gauche, qui court vers VP : la porte de gauche fermée (sa vitre, PANE : au-dessus et
au-dessous de sa traverse ; son panneau de bois), celle de droite glissée derrière elle, et l'ouverture (OPEN : du montant de
la porte de gauche au poteau du fond). Le seuil (SILL_COLS : sur chaque colonne de l'ouverture, la dernière rangée claire du
sol du peintre, puis son bois sombre) est sur un rayon vers VP à 1,5 m sous l'œil : la façade est à X_F = 6,33 m à gauche de
l'œil, l'ouverture de Z = 17,05 à 18,63 m le long de la rue ; le dessous du linteau (LINTEL, la première rangée de la pièce
peinte, mesurée colonne par colonne) à 2,46 m ; la vitre de 0,80 m à 2,40 m, sa traverse à 1,35 m.

La boutique, une boîte derrière la façade (DEPTH de fond, haute de CEIL). Par la porte, un rayon file le long de la rue (un
tiers de mètre vers le fond pour un mètre le long de la rue) : ce qu'il rencontre au bout est le mur du bout de la boutique,
de travers à la rue, donc de face (ses horizontales horizontales), à Z_E = 27 m (8,4 m derrière la porte, 52 px par mètre).
L'image du propriétaire (tools/src/dagashi_room.webp : les étagères de bocaux, les boîtes, la glacière à ramune, les machines à
gacha, les masques et les jouets de papier pendus, la lampe) y est posée à K = 375 pixels de l'image par mètre (ses étagères à
32 cm l'une de l'autre, ses bocaux de 19 cm), la planche sous ses bocaux du bas à 1,05 m (V0), glissée pour que sa machine à
gacha rouge soit à droite de l'ouverture (U_AT) : par l'ouverture, au-dessus de l'obaa-chan, la lampe, le masque de renard et
celui d'Okame, les cartes de papier pendues, les boîtes, les bocaux, la gacha rouge au-dessus du comptoir ; par la vitre, le
moulin à vent et le ballon, le daruma, les bocaux, la glacière à ramune (ses bouteilles bleues) et les sucettes. Devant ce mur,
le plancher surélevé où elle s'assied (PLAT), puis le comptoir (CTR : de face à Z = 25,7 m, son dessus à 0,75 m ; sa face de
planches, chacune au ton de la sienne dans l'image, leurs joints, son arête claire, l'ombre sous elle, le retrait du pied), le
sol de planches qui courent vers le fond (FLOOR : chacune son ton, tiré du sol de l'image) ; près de la porte, contre le poteau
du fond, la caisse de ballons de l'image (CRATE : sa face et ses ballons, de face). Le tableau du poteau du fond (T_J d'épaisseur
de mur : sa face de travers à la rue, de face) et la sous-face du linteau : le bois du peintre, éclairé par la pièce (JAMB).

Le rendu. Chaque pixel de l'ouverture et de la vitre est pris sur SS x SS rayons de l'œil ; la lumière : un tube au plafond
près de la porte (LIGHT : la flaque du sol, la face du comptoir plus sombre vers le sol et sous son arête) ; chaque rayon ramené
à la lumière de la rue (GRADE : en linéaire, la clarté médiane de l'image et ses clairs posés un peu au-dessus de ceux de la
pièce peinte allumée ; un peu moins saturée, plus chaude ; l'ampoule et la glacière gardent leur éclat, KNEE), puis à la
palette de la boutique (PAL couleurs tirées de la pièce ainsi éclairée, autant de chaque tranche de clarté) ; le pixel entier
prend la surface qui en tient le plus, et dedans la couleur que portent le plus de ses rayons (reduce : pas de mélange, un bord
ne fait pas une troisième couleur ; le cœur de l'ampoule gardé). Le grain du peintre (GRAIN : fixe, plein sur l'uni, léger sur le
chargé), un grain ne sautant jamais plus d'une marche. Derrière la vitre : un peu plus sombre (GLASS_DIM), un reflet en biais,
deux bandes nettes (SHEEN).

Éteinte (la boutique fermée, la coupure de courant : layer_city_off et street_unlit, les mêmes ici) : la même pièce dans le
sombre de la pièce peinte éteinte, de son plus sombre à son plus clair selon la clarté de la pièce allumée (ses grandes formes :
la moyenne de ses voisins surtout ; OFF : ses centiles), à ses couleurs (sa palette), le reflet de la vitre gardé. Allumée : le
comp (assets/win_z7_shop.webp, ce qui change quand elle s'allume ; sa boîte dans assets/street.js, sa version gardée). La nuit
rouge rougit sa lumière (le comp moins la rue sans courant). Le cadre de la porte, le poteau, le linteau, le seuil : tels qu'au
commit BEFORE. night_far et street_sun : 0 ici, tels quels. tools/dagashi_obaachan.py lit la maquette (Model, cut) pour poser
l'obaa-chan dedans. Il faut git, Pillow, numpy.
"""
import os
import re
import sys
import numpy as np
from PIL import Image

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import interieur as I

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'tools', 'src', 'dagashi_room.webp')
BEFORE = '4faa10a'                   # (les calques et le comp avant les outils de la boutique : sa zone reprise de là à chaque fois)
ZONE = (146, 525, 228, 745)          # x0, y0, x1, y1 : la devanture, cadre compris (à gauche de x 146 rien ne change : la descente)
UP, UP_POS = 'win_z7_shop', (105, 505)   # le comp de la boutique (sa place au commit BEFORE)

# ---- la caméra de la rue, la façade, la porte
F, VX, VY, EYE = 1400.0, 700.0, 615.0, 1.5
OPEN = (181, 224)                    # l'ouverture : ses colonnes (la porte de gauche avant, le poteau du fond après)
SILL_COLS = (183, 223)               # (le seuil mesuré sur ces colonnes : la dernière rangée claire du sol du peintre)
LINTEL = -0.1517                     # le dessous du linteau : y = VY + c (VX - x) (la première rangée de la pièce dessous)
PANE = (146, 176)                    # la vitre de la porte de gauche : ses colonnes
PANE_TOP, PANE_RAIL, PANE_BOT = -0.1415, 0.0235, 0.110   # (ses rayons : le haut du verre, la traverse (une rangée), le bas)
POST = 225                           # (la face du poteau du fond, sur la façade : sa première colonne)

# ---- la boutique (m ; X : de l'œil vers la gauche, à travers la façade ; Z : le long de la rue ; h : du trottoir)
Z_E = 27.0                           # le mur du bout, de face
DEPTH = 4.8                          # (la pièce : son fond depuis la façade)
CEIL = 3.1
T_J = 0.06                           # (l'épaisseur du mur : le tableau du poteau du fond, la sous-face du linteau)
K = 375.0                            # pixels de l'image par mètre (ses étagères à 32 cm l'une de l'autre, ses bocaux de 19 cm)
V0 = 1251.0                          # (la rangée de l'image au sol du mur : la planche sous ses bocaux du bas, rangée 858, à 1,05 m)
U_AT = (650.0, 9.373)                # (la colonne de l'image à tel X : la machine à gacha rouge à droite de l'ouverture)
CTR = dict(z=25.7, d=0.45, h=0.75, x0=8.6, x1=9.93, lip=0.022, kick=(0.09, 0.05),   # le comptoir : sa face, sa profondeur, son
           board=(0.115, 0.026), face=(1340, 1540, 190, 690), top=(1238, 1246))   # dessus, ses bouts (X), l'arête, le retrait du
                                     # pied ; les planches de sa face (leur largeur, le joint), leurs tons pris sur celles de l'image
                                     # (ses rangées, ses colonnes), son arête claire (ses rangées dans l'image)
PLAT = 0.35                          # (derrière le comptoir, le plancher surélevé où elle est assise)
CRATE = dict(z=21.0, x1=7.18, k=500.0, u1=857.0, v0=1712.0, rect=(735, 1488, 857, 1712),   # la caisse de ballons de l'image, près
             balls=((765, 1442, 47), (820, 1470, 39), (842, 1398, 36)))   # de la porte contre le poteau du fond : sa face (Z), son bord
                                     # droit (X), son échelle (px de l'image par mètre : 26 cm de large), sa colonne de droite et sa
                                     # rangée au sol dans l'image ; sa forme : la caisse, ses ballons (centre, rayon)
FLOOR = (0.15, (40, 1610, 850, 1760))   # le sol : la largeur de ses planches (chacune son ton : à cette distance leurs joints ne
                                     # tiennent pas un demi-pixel), leur ton pris dans ce sol de l'image
SS = 8

# ---- la lumière, l'étalonnage, la palette
LIGHT = dict(tube=21.0, pool=(0.55, 0.5, 2.8), foot=(0.35, 0.45), face=(1.0, 0.62), under=0.6, top=1.15)
                                     # le tube au plafond près de la porte (Z) : la flaque du sol (le sombre, l'ajout, sa demi-
                                     # longueur), le sol contre le pied du comptoir (sa part perdue, sur tant de m) ; la face du
                                     # comptoir (en haut, au pied), l'ombre sous l'arête, l'arête et le dessus
GRADE = ((100.0, 62.0), (201.0, 156.0), 0.9, (1.04, 0.98, 0.9))   # deux clartés de l'image (sa médiane, ses clairs) et celles qu'elles
                                     # prennent ; la saturation gardée ; la teinte de la lampe
KNEE = (0.45, 0.95, 0.97, ((400, 220, 500, 320), (40, 915, 240, 1235)))   # (les sources de lumière de l'image, l'ampoule de la
                                     # lampe et l'intérieur de la glacière (u0, v0, u1, v1) : au-dessus de cette clarté (linéaire),
                                     # jusqu'à celle-ci, leur lumière gardée à tant)
PAL = 48
GRAIN = 0.07                         # (le grain : son écart, en clarté)
JAMB = ((71.0, 49.0, 46.0), (0.12, 0.3, 0.45))   # le tableau du poteau : le bois éclairé du peintre ; allumée, sa part (loin de la
                                     # pièce, au milieu, contre elle ; plus vers le sol clair)
OFF = (10, 92, 14)                   # éteinte : les centiles du sombre de la pièce peinte (le plus sombre, le plus clair), sa palette
GLASS_DIM = 0.92                     # derrière la vitre, allumée : un peu plus sombre
SHEEN = ((0.55, 4.0, 3.0), (0.62, 1.5, 6.0))   # le reflet en biais : (sa pente (x par rangée), sa largeur, son ajout), une bande large
SHEEN_AT = (152, 560)                # et faible, une fine un peu plus claire, nettes ; sur la vitre seule (le point où passent leurs milieux)


def ray_y(c, x):                     # (la ligne à x du rayon c vers VP)
    return VY + c * (VX - x)


def first(r):                        # (la première rangée sous une ligne, la dernière au-dessus)
    return int(np.round(r - 0.5)) + 1


def last(r):
    return first(r) - 1


def lin(c): c = np.clip(np.asarray(c, float), 0, 255) / 255.0; return np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
def srgb(c): c = np.clip(c, 0, 1); return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055) * 255


def lab(rgb):
    c = lin(rgb)
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = c @ M.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def palette(P, k, per=600):
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
    return np.argmin(((lab(c)[:, None] - lab(pal)[None]) ** 2).sum(2), 1)


def measure_sill(on):
    """le seuil : sur chaque colonne de SILL_COLS, la plus forte chute de clarté sous le sol éclairé du peintre (la dernière
    rangée claire, puis le bois sombre) ; le rayon c médian de la limite (la façade à EYE / c de l'œil)"""
    L = on @ I.LUM; cs = []
    for x in range(SILL_COLS[0], SILL_COLS[1] + 1):
        col = L[700:750, x]; i = int(np.argmin(np.diff(col)))
        if col[i] - col[i + 1] > 12 and i > 15: cs.append((700 + i + 1 - VY) / (VX - x))
    return float(np.median(cs)), len(cs)


def before():
    """les calques au commit BEFORE, la devanture éteinte (off) et allumée (on : son comp posé dessus), le comp"""
    names = (('layer_city_off.webp', 'RGBA'), ('street_unlit.webp', 'RGBA'))
    B = [I.load(n, m, BEFORE) for n, m in names]
    cp = I.load(UP + '.webp', 'RGBA', BEFORE); px, py = UP_POS; ch, cw = cp.shape[:2]
    off = B[0][..., :3].copy(); on = off.copy(); al = cp[..., 3:4] / 255
    on[py:py + ch, px:px + cw] = on[py:py + ch, px:px + cw] * (1 - al) + cp[..., :3] * al
    return names, B, cp, off, on


class Model:
    """la maquette : la façade d'après le seuil, la pièce derrière elle"""
    def __init__(self, c_sill):
        self.c_sill = c_sill
        self.X_F = EYE / c_sill
        self.Z_A = F * self.X_F / (VX - (OPEN[0] - 0.5))       # (l'ouverture le long de la rue : le montant de la porte de gauche,
        self.Z_B = F * self.X_F / (VX - (OPEN[1] + 0.5))       # le poteau du fond)
        self.H_L = EYE - LINTEL * self.X_F
        self.src = np.asarray(Image.open(SRC).convert('RGB')).astype(float)
        u0, v0, u1, v1 = FLOOR[1]
        self.ftone = np.median(self.src[v0:v1, u0:u1].reshape(-1, 3), 0)    # (le ton du sol de l'image)
        fv0, fv1, fu0, fu1 = CTR['face']; n = int(np.ceil((CTR['x1'] - CTR['x0']) / CTR['board'][0]))
        bu = np.linspace(fu0, fu1, n + 1)                                   # (chaque planche du comptoir : la médiane de la sienne dans
        self.btone = np.array([np.median(self.src[fv0:fv1, int(a) + 3:int(b) - 3].reshape(-1, 3), 0) for a, b in zip(bu, bu[1:])])   # l'image)
        self.lip = np.median(self.src[CTR['top'][0]:CTR['top'][1], fu0:fu1].reshape(-1, 3), 0)

    def pixels(self):
        """ce qu'on voit de la pièce : l'ouverture (de sous le linteau au seuil), la vitre (au-dessus et au-dessous de sa
        traverse) ; chacun avec son verre (0 : l'air de l'ouverture, 1 : la vitre)"""
        pix, glass = [], []
        for x in range(OPEN[0], OPEN[1] + 1):
            for y in range(first(ray_y(LINTEL, x)), last(ray_y(self.c_sill, x)) + 1):
                pix.append((x, y)); glass.append(0)
        for x in range(PANE[0], PANE[1] + 1):
            rail = int(np.round(ray_y(PANE_RAIL, x)))
            for y in range(first(ray_y(PANE_TOP, x)), last(ray_y(PANE_BOT, x)) + 1):
                if y != rail: pix.append((x, y)); glass.append(1)
        return np.array(pix), np.array(glass)

    def render(self, pix, ss=SS):
        """chaque pixel pris sur ss x ss rayons de l'œil : ce que chacun rencontre le premier dans la maquette (sa couleur
        éclairée, sa surface, sa profondeur Z)"""
        o = (np.arange(ss) + 0.5) / ss
        ox, oy = np.meshgrid(o, o)
        DX = (VX - (pix[:, 0:1] + ox.ravel()[None])) / F; DY = (VY - (pix[:, 1:2] + oy.ravel()[None])) / F
        sh = DX.shape
        Zh = np.full(sh, np.inf); col = np.zeros(sh + (3,)); sid = np.zeros(sh, int); self.glow = np.zeros(sh)
        XF, src = self.X_F, self.src
        def hit(Z, ok, c, k):
            nonlocal Zh, sid
            m = ok & (Z < Zh) & (Z > 0)
            Zh = np.where(m, Z, Zh); sid = np.where(m, k, sid)
            col[m] = np.broadcast_to(np.asarray(c, float), sh + (3,))[m]
        def look(u, v):
            return src[np.clip(np.floor(v).astype(int), 0, src.shape[0] - 1), np.clip(np.floor(u).astype(int), 0, src.shape[1] - 1)]
        def plane_h(hh):
            down = (hh - EYE) / np.where(DY != 0, DY, 1e-9)
            return np.where(down > 0, down, np.inf)
        inside = lambda Z: (DX * Z > XF) & (DX * Z < XF + DEPTH)            # (derrière la façade, dans la pièce)
        # le mur du bout, de face : l'image du propriétaire à l'échelle K
        Z = np.full(sh, Z_E); X = DX * Z; h = EYE + DY * Z
        u, v = U_AT[0] - (X - U_AT[1]) * K, V0 - h * K
        hit(Z, inside(Z) & (h > 0) & (h < CEIL), look(u, v), 1)
        self.glow = sum(((u >= a) & (u < c) & (v >= b) & (v < d)).astype(float) for a, b, c, d in KNEE[3])   # (une source de lumière là)
        # le plafond (on ne le voit pas d'ici), le plancher surélevé et sa contremarche
        Zc = plane_h(CEIL); hit(Zc, inside(Zc) & (Zc < Z_E), (60., 36., 24.), 2)
        Zp = plane_h(PLAT); hit(Zp, (Zp > CTR['z'] + CTR['d']) & (Zp < Z_E), self.ftone * 0.8, 4)
        Zr = np.full(sh, CTR['z'] + CTR['d']); hr = EYE + DY * Zr; hit(Zr, (hr > 0) & (hr < PLAT) & inside(Zr), self.ftone * 0.4, 4)
        # le sol : des planches qui courent vers le fond, chacune son ton ; la flaque du tube, l'ombre contre le pied du comptoir
        Zf = plane_h(0.0); Xf = DX * Zf
        kq = np.floor(np.nan_to_num((Xf - XF) / FLOOR[0], posinf=0, neginf=0)).astype(int)
        tone = 0.86 + 0.28 * ((np.sin(kq * 12.9898 + 4.1) * 43758.5453) % 1.0)
        dk, ad, ln = LIGHT['pool']; fl, fd = LIGHT['foot']
        lit = (dk + ad * np.exp(-((Zf - LIGHT['tube']) / ln) ** 2)) * (1 - fl * np.exp(-np.maximum(0, CTR['z'] - Zf) / fd))
        fc = self.ftone * (tone * lit)[..., None]
        hit(Zf, inside(Zf) & (Zf < Z_E), fc, 3)
        # le comptoir : sa face de planches (celle de l'image), plus sombre vers le sol et sous l'arête ; l'arête et le dessus
        # pris dans la lumière ; le retrait du pied
        c = CTR; Z = np.full(sh, c['z']); X = DX * Z; h = EYE + DY * Z
        okx = (X >= c['x0']) & (X <= c['x1'])
        bw, sw = c['board']
        qb = (c['x1'] - X) / bw; kb = np.floor(qb).astype(int); fb = qb - kb
        sh_ = LIGHT['face'][1] + (LIGHT['face'][0] - LIGHT['face'][1]) * np.clip((h - c['kick'][0]) / (c['h'] - c['kick'][0]), 0, 1)
        sh_ = sh_ * np.where(h > c['h'] - c['lip'] - 0.03, LIGHT['under'], 1.0)
        face = self.btone[np.clip(kb, 0, len(self.btone) - 1)] * (sh_ * (0.9 + 0.2 * ((np.sin(kb * 7.31 + 1.7) * 9631.17) % 1.0)))[..., None]
        seam = (fb < sw / bw) & (h <= c['h'] - c['lip'] - 0.03)
        hit(Z, okx & (h >= c['kick'][0]) & (h <= c['h'] - c['lip']) & ~seam, face, 5)
        hit(Z, okx & (h >= c['kick'][0]) & seam, face * 0.55, 11)
        hit(Z, okx & (h > c['h'] - c['lip']) & (h <= c['h']), self.lip * LIGHT['top'], 6)
        Zt = plane_h(c['h']); Xt = DX * Zt
        hit(Zt, (Zt >= c['z']) & (Zt <= c['z'] + c['d']) & (Xt >= c['x0']) & (Xt <= c['x1']), self.lip * LIGHT['top'] * 0.92, 6)
        Zk = np.full(sh, c['z'] + c['kick'][1]); Xk = DX * Zk; hk = EYE + DY * Zk
        hit(Zk, (Xk >= c['x0']) & (Xk <= c['x1']) & (hk >= 0) & (hk < c['kick'][0]), self.ftone * 0.25, 9)
        # la caisse de ballons, de face, près de la porte (sa forme : la caisse et les ballons de l'image) ; la lumière du tube
        c = CRATE; Z = np.full(sh, c['z']); X = DX * Z; h = EYE + DY * Z
        u, v = c['u1'] - (X - c['x1']) * c['k'], c['v0'] - h * c['k']
        a0, b0, a1, b1 = c['rect']
        shape = ((u >= a0) & (u < a1) & (v >= b0) & (v < b1)) | sum((u - bu) ** 2 + (v - bv) ** 2 <= br ** 2 for bu, bv, br in c['balls'])
        shape = (shape > 0) & (u < a1) & (h >= 0)
        lit = LIGHT['pool'][0] + LIGHT['pool'][1] * np.exp(-((c['z'] - LIGHT['tube']) / LIGHT['pool'][2]) ** 2)
        hit(Z, shape & inside(Z), look(u, v) * min(1.0, 0.25 + lit), 12)
        # la porte : le tableau du poteau du fond, la sous-face du linteau (leurs couleurs : le bois du peintre, plus tard)
        Z = np.full(sh, self.Z_B); X = DX * Z; h = EYE + DY * Z
        hit(Z, (X >= XF) & (X <= XF + T_J) & (h >= 0) & (h <= self.H_L), (0., 0., 0.), 7)
        Zs = plane_h(self.H_L); Xs = DX * Zs
        hit(Zs, (Xs >= XF) & (Xs <= XF + T_J) & (Zs >= self.Z_A) & (Zs <= self.Z_B), (0., 0., 0.), 8)
        return col, sid, Zh


def reduce(col, sid, pal):
    """au pixel entier : la surface qui en tient le plus ; dedans, chaque rayon ramené à la palette, la couleur que portent le
    plus de rayons (pas de mélange : un bord ne fait pas une troisième couleur) ; un éclat (le cœur de la lampe) gardé dans son
    pixel : la couleur de la palette la plus proche de leur moyenne tirée vers les rayons les plus clairs. Rend aussi la surface
    de chacun, et s'il est un éclat"""
    n, s = sid.shape
    q = np.zeros((n, s), int)
    for a in range(0, n, 2000): q[a:a + 2000] = nearest(col[a:a + 2000].reshape(-1, 3), pal).reshape(-1, s)
    out = np.zeros(n, int); acc = np.zeros(n, bool); surf = np.zeros(n, int)
    for i in range(n):
        ids, cnt = np.unique(sid[i], return_counts=True)
        k = surf[i] = ids[np.argmax(cnt)]
        on = sid[i] == k
        v, c = np.unique(q[i][on], return_counts=True)
        out[i] = v[np.argmax(c)]
        L = col[i][on] @ I.LUM
        nb = max(1, len(L) // 8); top = np.sort(L)[-nb:]
        if top.mean() > 230 and top.mean() - pal[out[i]] @ I.LUM > 60:
            m = 0.45 * col[i][on].mean(0) + 0.55 * col[i][on][L >= top[0]].mean(0)
            out[i] = nearest(m[None], pal)[0]; acc[i] = True
    return out, acc, surf


def grade(rgb, glow=None):
    """de la lumière de l'image à celle de la boutique dans la rue : en linéaire, une puissance qui pose sa médiane et ses clairs
    (GRADE) ; un peu moins saturée, à la teinte de la lampe ; là où glow est vrai (une source de lumière), ses clairs gardés"""
    (a0, b0), (a1, b1), sat, tint = GRADE
    g = np.log(lin(b0) / lin(b1)) / np.log(lin(a0) / lin(a1)); k = lin(b1) / lin(a1) ** g
    c = lin(rgb); Y = c @ np.array([0.2126, 0.7152, 0.0722])
    Yo = k * np.maximum(Y, 1e-6) ** g
    w = np.clip((Y - KNEE[0]) / (KNEE[1] - KNEE[0]), 0, 1); w = w * w * (3 - 2 * w) * (0 if glow is None else glow)
    Yo = Yo * (1 - w) + Y * KNEE[2] * w                                      # (les sources de lumière gardent leur éclat)
    c = c * (Yo / np.maximum(Y, 1e-6))[..., None]
    c = Yo[..., None] + (c - Yo[..., None]) * sat
    return srgb(c * np.array(tint))


def neighbours(xs, ys, v):
    """la moyenne et l'écart de v sur chaque pixel et ses voisins rendus (3 x 3)"""
    zx0, zy0, zx1, zy1 = ZONE
    S1 = np.zeros((zy1 - zy0 + 2, zx1 - zx0 + 2)); S2 = S1.copy(); N = S1.copy()
    S1[ys - zy0 + 1, xs - zx0 + 1] = v; S2[ys - zy0 + 1, xs - zx0 + 1] = v * v; N[ys - zy0 + 1, xs - zx0 + 1] = 1
    box = lambda A: sum(A[1 + a + ys - zy0, 1 + b + xs - zx0] for a in (-1, 0, 1) for b in (-1, 0, 1))
    n = box(N); m = box(S1) / n
    return m, np.sqrt(np.maximum(box(S2) / n - m * m, 0))


def sheen(xs, ys):
    """le reflet en biais sur la vitre : son ajout à chaque pixel"""
    add = np.zeros(len(xs))
    for slope, wdt, a in SHEEN:
        add += np.where(np.abs((xs - SHEEN_AT[0]) + slope * (ys - SHEEN_AT[1])) < wdt / 2, a, 0.0)
    return add


def cut():
    """la pièce dans ses deux états : ses pixels, leur verre, allumée (lit), éteinte (dark), la surface de chacun ; et la
    maquette (pour tools/dagashi_obaachan.py)"""
    names, B, cp, off, on = before()
    c_sill, n_sill = measure_sill(on)
    M = Model(c_sill)
    pix, glass = M.pixels()
    xs, ys = pix[:, 0], pix[:, 1]
    col, sid, Zh = M.render(pix)
    col = grade(col, M.glow * (sid == 1))
    surf = np.array([np.bincount(r).argmax() for r in sid])

    # le tableau du poteau, la sous-face du linteau : le bois du peintre (le poteau à sa rangée) ; allumée, le tableau éclairé
    # par la pièce, plus vers elle et vers le sol clair
    jt = {}
    for i, (x, y) in enumerate(pix):
        if surf[i] in (7, 8):
            wood = np.median(off[y - 3:y + 4, POST:POST + 2].reshape(-1, 3), 0)
            if surf[i] == 8: jt[i] = (wood * 0.8, wood * 0.8); continue
            Xh = (VX - x) * M.Z_B / F - M.X_F; k = min(2, int(3 * Xh / T_J))   # (0 loin de la pièce … 2 contre elle)
            h = EYE + (VY - y) * M.Z_B / F
            s = JAMB[1][k] * (0.75 + 0.25 * (1 - h / M.H_L))
            jt[i] = (wood * (1 - s) + np.array(JAMB[0]) * s, wood)

    # la palette de la boutique : la pièce ainsi éclairée ; le grain du peintre, fixe (plein sur l'uni, léger sur le chargé),
    # jamais un saut de plus d'une marche
    room = np.array([i not in jt for i in range(len(pix))]) & (surf != 0)
    pal = palette(col[room].reshape(-1, 3)[::7], PAL)
    qi, acc, surf = reduce(col, sid, pal)
    rgb = pal[qi]
    zx0, zy0, zx1, zy1 = ZONE
    Lsd = neighbours(xs, ys, rgb @ I.LUM)[1]
    g = np.random.default_rng(1957).normal(0, 1, (zy1 - zy0 + 2, zx1 - zx0 + 2))
    g = 0.7 * g[1:-1, 1:-1] + 0.15 * (g[:-2, 1:-1] + g[1:-1, :-2] + g[2:, 1:-1] + g[1:-1, 2:])
    g = (g / g.std())[ys - zy0, xs - zx0]
    amp = GRAIN * (0.3 + 0.7 * np.clip(1 - Lsd / 16, 0, 1))
    i0 = qi; i1 = nearest(np.clip(rgb * np.exp(amp * g)[:, None], 0, 255), pal)
    far = ((lab(pal[i0]) - lab(pal[i1])) ** 2).sum(1) > 14 ** 2
    lit = pal[np.where(acc | far, i0, i1)]
    Ll = lit @ I.LUM

    # éteinte : le sombre de la pièce peinte éteinte, de son plus sombre à son plus clair selon la clarté de la pièce allumée,
    # à ses couleurs (sa palette), son grain plus léger
    Cb = np.array([off[y, x] for x, y in pix]); Lb = Cb @ I.LUM
    lo, hi = Cb[Lb <= np.percentile(Lb, OFF[0])].mean(0), Cb[Lb >= np.percentile(Lb, OFF[1])].mean(0)
    Lm = 0.25 * Ll + 0.75 * neighbours(xs, ys, Ll)[0]                        # (les grandes formes : le détail fin s'éteint)
    t = np.clip((Lm - 25) / 175, 0, 1) ** 0.85
    dark_c = lo + (hi - lo) * t[:, None]
    dpal = palette(Cb, OFF[2])
    j0 = nearest(dark_c, dpal); j1 = nearest(np.clip(dark_c * np.exp(0.3 * amp * g)[:, None], 0, 255), dpal)
    dark = dpal[np.where(((lab(dpal[j0]) - lab(dpal[j1])) ** 2).sum(1) > 6 ** 2, j0, j1)]
    for i, (a, b) in jt.items(): lit[i], dark[i] = a, b

    # derrière la vitre : allumée un peu plus sombre ; le reflet, allumée comme éteinte
    sh = sheen(xs, ys) * glass
    lit = np.where(glass[:, None] == 1, lit * GLASS_DIM, lit) + sh[:, None]
    dark = dark + sh[:, None]
    e = surf == 0                                                            # (les rayons qui ne rencontrent rien : le seuil, tel quel)
    lit[e], dark[e] = [on[y, x] for x, y in pix[e]], [off[y, x] for x, y in pix[e]]
    info = dict(c_sill=c_sill, n_sill=n_sill, pal=len(pal), acc=int(acc.sum()))
    return dict(names=names, B=B, cp=cp, off=off, on=on, M=M, pix=pix, glass=glass, lit=lit, dark=dark, surf=surf, Zh=Zh,
                sheen=sh, info=info, dark_ramp=(lo, hi, dpal))


def main():
    prev = sys.argv[sys.argv.index('--preview') + 1] if '--preview' in sys.argv else None
    R = cut()
    M, pix, B, cp = R['M'], R['pix'], R['B'], R['cp']
    names, off, on = R['names'], R['off'], R['on']
    H, W = off.shape[:2]
    zx0, zy0, zx1, zy1 = ZONE
    N = {'on': on.copy(), 'off': off.copy()}
    for (x, y), a, b in zip(pix, R['lit'], R['dark']):
        N['on'][y, x] = a; N['off'][y, x] = b
    print('façade à X_F %.3f m (seuil c %.4f, %d colonnes) ; ouverture de Z %.2f à %.2f m, linteau à %.2f m ; mur du bout à Z %.1f m '
          '(%.1f m derrière la porte, %.1f px par mètre) ; comptoir à Z %.1f m (dessus à %.2f m) | %d pixels, %d éclats, palette %d '
          'couleurs' % (M.X_F, R['info']['c_sill'], R['info']['n_sill'], M.Z_A, M.Z_B, M.H_L, Z_E, Z_E - M.Z_B, F / Z_E, CTR['z'],
                        CTR['h'], len(pix), R['info']['acc'], R['info']['pal']))
    if prev:
        for k in N: np.save(os.path.join(prev, 'room_%s.npy' % k), N[k])
        for k in N:
            Image.fromarray(np.clip(np.round(N[k][520:750, 130:240]), 0, 255).astype(np.uint8)).resize((440, 920), Image.NEAREST).save(os.path.join(prev, k + '_x4.png'))
            Image.fromarray(np.clip(np.round(N[k][530:745, 140:232]), 0, 255).astype(np.uint8)).resize((736, 1720), Image.NEAREST).save(os.path.join(prev, k + '_x8.png'))
        return
    # les calques : la devanture éteinte (la même dans la coupure de courant) ; le comp : ce qui change quand elle s'allume
    zs = (slice(zy0, zy1), slice(zx0, zx1))
    L = [I.load(n, m) for n, m in names]
    for l, b in zip(L, B): l[zs] = b[zs]
    L[0][zs][..., :3] = N['off'][zs]; L[0][zs][..., 3] = 255
    L[1][zs][..., :3] = N['off'][zs]; L[1][zs][..., 3] = 255
    for (n, m), l in zip(names, L): I.save(l, n, m)
    px, py = UP_POS; ch, cw = cp.shape[:2]
    diff = np.zeros((H, W), bool); diff[zs] = np.abs(np.round(N['on'][zs]) - np.round(N['off'][zs])).sum(2) > 0
    keep = np.zeros((H, W), bool); keep[py:py + ch, px:px + cw] = cp[..., 3] > 0
    keep[zs] = False                                                         # (hors de la devanture, le comp tel quel)
    spr = np.zeros((H, W, 4))
    spr[keep] = np.concatenate([on[keep], np.full((keep.sum(), 1), 255.0)], 1)
    spr[diff] = np.concatenate([N['on'][diff], np.full((diff.sum(), 1), 255.0)], 1)
    ys, xs = np.where(spr[..., 3] > 0)
    bx, by, bw, bh = int(xs.min()), int(ys.min()), int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1)
    I.save(spr[by:by + bh, bx:bx + bw], UP + '.webp', 'RGBA')
    js = os.path.join(ROOT, 'assets', 'street.js')
    s_ = open(js, encoding='utf-8').read()
    s2, n_s = re.subn(r'("%s": \{"src": "assets/%s\.webp(?:\?v=\d+)?", )"x": \d+, "y": \d+, "w": \d+, "h": \d+\}' % (UP, UP),
                      lambda m: m.group(1) + '"x": %d, "y": %d, "w": %d, "h": %d}' % (bx, by, bw, bh), s_)
    assert n_s == 1, 'street.js : le comp de la boutique est introuvable'
    if s2 != s_: open(js, 'w', encoding='utf-8').write(s2)
    print('comp', (bx, by, bw, bh), int(diff.sum()), 'px')


if __name__ == '__main__':
    main()
