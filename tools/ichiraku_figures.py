#!/usr/bin/env python3
"""Ichiraku : les gens de la boutique dans la maquette de tools/ichiraku_interior.py, chacun à sa profondeur.

    python3 tools/ichiraku_figures.py                  (après tools/ichiraku_interior.py ; réécrit assets/ramen_figures.webp et,
                                                         dans assets/street.js, la ligne IRF : on peut le relancer, il écrit la
                                                         même chose)
    python3 tools/ichiraku_figures.py --preview dossier (des aperçus seulement)

La maquette (tools/ichiraku_interior.py : l'œil de la rue, la façade, les portes, le comptoir des clients, ses tabourets, l'allée,
le mur du bout) dit où est chacun et à quelle échelle : à la profondeur Z (le long de la rue), F / Z pixels par mètre, une
hauteur h à la rangée VY - (h - EYE) F / Z, ce qui est de face (perpendiculaire à la rue) de face, sans biais.

Teuchi, debout dans son allée (Z_T = 27,3 m, 51 px par mètre), face à nous au comptoir, de dos à la marmite et à l'étagère, de
profil quand il va de l'une à l'autre : le haut de sa toque à 1,75 m (rangée 602), le comptoir le coupe à sa rangée (641) ;
ses places (PLACES) : au comptoir, à la marmite (son X, la louche à bout de bras), devant les bocaux de gauche. Devant lui,
la lanterne, les objets du comptoir, son arête : ce qui, dans la maquette, est plus près que lui (l'image O, le verre vu de
la maquette, chaque pixel dont la surface n'est ni le mur du bout ni le fond) ne laisse rien passer de lui.

Teuchi à la porte qui rentre ou sort le noren : debout derrière la vitre (R_BACK), au milieu des portes (R_X), à 84 px par
mètre ; la tringle du noren est sur la façade, sur un rayon vers VP à 2,64 m du trottoir (au-dessus des vitres du haut) : il
y monte une perche à crochet, tenue droite puis tendue jusqu'à elle (reach).

Le client du coin (son chapeau de paille), assis de dos sur le tabouret de gauche, et Naruto sur celui de droite : leur dos
à Z_S = 25,9 m (54 px par mètre), le haut du chapeau à 1,32 m (rangée 625), les épis de Naruto à la rangée 626, le dessus
du coussin à 0,66 m (rangée 660) ; leurs bols devant eux sur le comptoir (le bol de Naruto : celui de la maquette). Quand
il s'en va, le client se lève et va de son tabouret à la porte, vers nous (WALK_END : la colonne de son milieu à la porte,
derrière la vitre de tant) : debout, de face, une image nette pour chaque pixel de sa hauteur (de 98 à 149 px), ses pieds
sur le sol à sa profondeur.

Teuchi et le client sont redessinés à leur taille (des formes simples : têtes, toque, chapeau, épaules qui tombent, bras,
jambes, la perche ; prises sur SS x SS points par pixel, un pixel plein dès la moitié couverte : des silhouettes nettes, sans
mise à l'échelle) ; les six images de Naruto (assets/naruto_ramen.webp) sont déjà à l'échelle du tabouret : gardées pixel
pour pixel, le bas de son dos prolongé jusqu'au coussin. Tout va dans assets/ramen_figures.webp (l'alpha : la silhouette),
rangé en étagères ; assets/street.js lit la ligne IRF : où est chaque image et où la poser, le verre colonne par colonne (de
sous la tringle à la traverse, de la traverse à la lisière du bas : rien d'eux ailleurs), d'où monte la vapeur (le bord des
bols, la marmite), les places de Teuchi, le chemin du client (en mètres). Il faut git, Pillow, numpy.
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
F, VX, VY, EYE = R.F, R.VX, R.VY, R.EYE
SS = 8

# ---- les profondeurs (m, le long de la rue) et les échelles (px par mètre : F / Z)
Z_T = R.Z_C + R.CTR_D + R.AISLE / 2          # Teuchi, au milieu de son allée
Z_S = R.Z_C - R.STOOL['dz'] - 0.12           # le dos des clients assis sur les tabourets
Z_STOOL = R.Z_C - R.STOOL['dz']              # (le milieu des tabourets)
T_TOP = 1.753                                # le haut de la tête de Teuchi (sa toque) : rangée 602
SEAT = R.STOOL['top']                        # le dessus du coussin


def row(h, Z):                               # (la rangée d'une hauteur h à la profondeur Z)
    return VY - (h - EYE) * F / Z


def col(X, Z):
    return VX + F * X / Z


def raster(shapes, W, H, s, top_h, cu=None):
    """une silhouette nette : les formes (en mètres, u en travers depuis le milieu de la case, h la hauteur) prises sur SS x SS
    points par pixel, un pixel plein dès la moitié couverte ; la case de W x H pixels, sa rangée 0 à la hauteur top_h, s pixels
    par mètre"""
    cu = W / 2 if cu is None else cu
    yy, xx = np.mgrid[0:H * SS, 0:W * SS]
    u = ((xx + 0.5) / SS - cu) / s; h = top_h - ((yy + 0.5) / SS) / s
    m = np.zeros(u.shape, bool)
    for sh in shapes:
        k = sh[0]
        if k == 'ell':
            _, a, b, ra, rb = sh; m |= ((u - a) / ra) ** 2 + ((h - b) / rb) ** 2 <= 1
        elif k == 'cap':
            _, a0, b0, a1, b1, r = sh
            da, db = a1 - a0, b1 - b0; L2 = da * da + db * db
            t = np.clip(((u - a0) * da + (h - b0) * db) / L2, 0, 1) if L2 > 0 else 0
            m |= (u - a0 - t * da) ** 2 + (h - b0 - t * db) ** 2 <= r * r
        elif k == 'poly':
            P = sh[1]; ins = np.zeros(u.shape, bool)
            for (a0, b0), (a1, b1) in zip(P, P[1:] + P[:1]):
                c = ((b0 > h) != (b1 > h)) & (u < (a1 - a0) * (h - b0) / ((b1 - b0) if b1 != b0 else 1e-9) + a0)
                ins ^= c
            m |= ins
    return m.reshape(H, SS, W, SS).mean((1, 3)) >= 0.5


def mirror(shapes):
    out = []
    for sh in shapes:
        if sh[0] == 'ell': out.append(('ell', -sh[1], sh[2], sh[3], sh[4]))
        elif sh[0] == 'cap': out.append(('cap', -sh[1], sh[2], -sh[3], sh[4], sh[5]))
        else: out.append(('poly', [(-a, b) for a, b in sh[1]][::-1]))
    return out


def body(neck, low, w=0.2, waist=0.19):
    """un buste de face : la base du cou à la hauteur neck, les épaules qui tombent, la taille, jusqu'à low"""
    return [('poly', [(-0.07, neck), (-w + 0.02, neck - 0.04), (-w - 0.015, neck - 0.075), (-w - 0.02, neck - 0.13),
                      (-waist, low + 0.1), (-waist + 0.01, low), (waist - 0.01, low), (waist, low + 0.1), (w + 0.02, neck - 0.13),
                      (w + 0.015, neck - 0.075), (w - 0.02, neck - 0.04), (0.07, neck)])]


# ---- Teuchi derrière le comptoir (le haut du corps : le comptoir le coupe) : de face, de profil (vers la gauche), de dos
def teuchi(view, arm=0, bob=0.0):
    t = T_TOP - bob
    S = [('poly', [(-0.092, t - 0.075), (-0.088, t - 0.008), (0.088, t - 0.008), (0.092, t - 0.075)]),   # la toque
         ('ell', 0, t - 0.02, 0.088, 0.02)]
    if view == 'side':
        S += [('ell', -0.005, t - 0.135, 0.098, 0.112), ('ell', -0.1, t - 0.145, 0.022, 0.02),          # la tête, le nez
              ('cap', 0.0, t - 0.25, 0.0, t - 0.3, 0.055),                                                # le cou
              ('poly', [(-0.11, t - 0.3), (0.1, t - 0.3), (0.13, t - 0.42), (0.125, 0.8), (-0.15, 0.8),
                        (-0.16, t - 0.6), (-0.135, t - 0.42)])]                                           # le buste, le ventre
        sw = (0.0, 0.0), (-0.08, -0.13), (0.07, 0.1)
        e, hnd = sw[arm]
        S += [('cap', 0.0, t - 0.34, e, t - 0.62, 0.05), ('cap', e, t - 0.62, hnd, t - 0.86, 0.045)]       # le bras qui balance
        return S
    S += [('ell', 0, t - 0.135, 0.088, 0.112),                                                            # la tête
          ('ell', -0.09, t - 0.14, 0.016, 0.03), ('ell', 0.09, t - 0.14, 0.016, 0.03),                    # les oreilles
          ('cap', 0, t - 0.25, 0, t - 0.3, 0.056)] + body(t - 0.3, 0.8)                                  # le cou, le buste
    if view == 'front':                           # au comptoir : les avant-bras vers lui, les coudes qui travaillent
        P = {0: ((-0.235, -0.62, -0.225, -0.88), (0.235, -0.62, 0.225, -0.88)),
             1: ((-0.265, -0.58, -0.12, -0.68), (0.24, -0.62, 0.14, -0.74)),
             2: ((-0.24, -0.62, -0.14, -0.74), (0.265, -0.58, 0.12, -0.68))}[arm]
    else:                                         # de dos : la louche, le coude qui tourne
        P = {0: ((-0.235, -0.62, -0.225, -0.88), (0.235, -0.62, 0.225, -0.88)),
             1: ((-0.24, -0.62, -0.14, -0.74), (0.3, -0.5, 0.13, -0.58)),
             2: ((-0.24, -0.62, -0.14, -0.74), (0.28, -0.58, 0.12, -0.66))}[arm]
    for ex, ey, hx, hy in P:
        sx = -0.19 if ex < 0 else 0.19
        S += [('cap', sx, t - 0.37, ex, t + ey, 0.05), ('cap', ex, t + ey, hx, t + hy, 0.045)]
    return S


# ---- Teuchi qui rentre ou sort le noren : debout derrière la porte, face à nous, la perche à crochet levée jusqu'à la tringle
def reach(k, pole_h):
    t = 1.75
    S = [('poly', [(-0.092, t - 0.075), (-0.088, t - 0.008), (0.088, t - 0.008), (0.092, t - 0.075)]), ('ell', 0, t - 0.02, 0.088, 0.02),
         ('ell', 0, t - 0.135, 0.088, 0.112), ('cap', 0, t - 0.25, 0, t - 0.3, 0.056)] + body(t - 0.3, 0.86) + [
         ('cap', -0.095, 0.9, -0.1, 0.04, 0.08), ('cap', 0.095, 0.9, 0.1, 0.04, 0.08)]                     # les jambes
    if k == 0:                                    # la perche tenue droite devant lui, des deux mains (à la poitrine, au menton)
        hand = (0.05, t - 0.2)
        S += [('cap', -0.19, t - 0.37, -0.22, t - 0.62, 0.05), ('cap', -0.22, t - 0.62, 0.03, t - 0.42, 0.045),
              ('cap', 0.19, t - 0.37, 0.2, t - 0.55, 0.05), ('cap', 0.2, t - 0.55, hand[0], hand[1], 0.045)]
        tip = (0.08, pole_h - 0.22)
    else:                                         # les bras tendus, le crochet sur la tringle
        hand = (0.12, t + 0.32)
        S += [('cap', -0.2, t - 0.35, -0.2, t + 0.0, 0.05), ('cap', -0.2, t + 0.0, 0.06, t + 0.2, 0.045),
              ('cap', 0.2, t - 0.35, 0.18, t + 0.05, 0.05), ('cap', 0.18, t + 0.05, hand[0], hand[1], 0.045)]
        tip = (0.15, pole_h)
    S += [('cap', hand[0] - 0.02, hand[1] - 0.4, tip[0], tip[1] - 0.06, 0.014),                             # la perche
          ('cap', tip[0], tip[1] - 0.06, tip[0] + 0.035, tip[1], 0.012), ('cap', tip[0] + 0.035, tip[1], tip[0] + 0.06, tip[1] - 0.03, 0.012)]
    return S


# ---- le client du coin, assis (de dos, son chapeau de paille), et debout qui s'en va (de face, vers la porte)
KASA = [(-0.225, 0.0), (-0.215, 0.02), (-0.06, 0.1), (0.0, 0.125), (0.06, 0.1), (0.215, 0.02), (0.225, 0.0)]


def seated(arm=0):
    b = 1.195                                     # le bord du chapeau
    S = [('poly', [(a, b + c) for a, c in KASA]), ('ell', 0, b - 0.04, 0.08, 0.075),                     # le chapeau, la nuque
         ('cap', 0, 1.12, 0, 1.07, 0.06)] + body(1.08, SEAT - 0.01, 0.2, 0.18)
    el = {0: ((-0.27, 0.93), (0.27, 0.93)), 1: ((-0.27, 0.93), (0.29, 0.99)), 2: ((-0.29, 0.99), (0.27, 0.93))}[arm]
    for ex, ey in el:
        sx = 0.19 if ex > 0 else -0.19
        S += [('cap', sx, 1.02, ex, ey, 0.05), ('ell', ex * 0.98, ey - 0.005, 0.055, 0.05)]
    return S


def standing(k):
    top = 1.82; b = top - 0.125                   # (le haut du chapeau ; son bord)
    S = [('poly', [(a - 0.02, b + c) for a, c in KASA]), ('ell', -0.015, b - 0.06, 0.085, 0.09),
         ('cap', -0.01, b - 0.15, -0.01, 1.43, 0.055)] + body(1.45, 0.82)
    leg = {0: ((-0.085, 0.0), (0.085, 0.0)), 1: ((-0.1, 0.06), (0.09, 0.0)), 2: ((-0.085, 0.0), (0.105, 0.06))}[k]
    for (fx, fy), hx in zip(leg, (-0.09, 0.09)):
        S += [('cap', hx, 0.86, fx, fy + 0.045, 0.08), ('ell', fx - 0.02, fy + 0.035, 0.1, 0.04)]
    arm = {0: (0.0, 0.0), 1: (0.05, -0.04), 2: (-0.04, 0.05)}[k]
    for sx, d in zip((-0.2, 0.2), arm):
        S += [('cap', sx, 1.36, sx * 1.1 + d, 1.1, 0.05), ('cap', sx * 1.1 + d, 1.1, sx * 1.02 + 2 * d, 0.84, 0.045)]
    return S


class Atlas:
    """les cases, rangées en étagères dans une image (alpha : la silhouette) ; leur boîte [sx, sy, w, h]"""
    def __init__(self, width):
        self.W, self.x, self.y, self.rowh, self.cells = width, 0, 0, 0, []

    def add(self, m):
        h, w = m.shape
        if self.x + w > self.W: self.x, self.y, self.rowh = 0, self.y + self.rowh + 1, 0
        self.cells.append((self.x, self.y, m)); box = [self.x, self.y, w, h]
        self.x += w + 1; self.rowh = max(self.rowh, h)
        return box

    def image(self):
        H = self.y + self.rowh
        a = np.zeros((H, self.W, 4), np.uint8)
        for x, y, m in self.cells:
            a[y:y + m.shape[0], x:x + m.shape[1], 3] = np.where(m, 255, 0)
        return a


def naruto_cells():
    """Naruto au comptoir, de dos : ses six images (assets/naruto_ramen.webp, 23 x 37 : assis, penché, deux pour aspirer, la
    tête levée, les bouts du bandeau) gardées pixel pour pixel (leur échelle est déjà celle du tabouret), le bas du dos
    prolongé jusqu'au coussin (ses rangées du bas, qui se resserraient, refaites droites)"""
    a = I.load('naruto_ramen.webp', 'RGBA')[..., 3] > 128
    out = []
    for f in range(6):
        c = a[:, f * 23:(f + 1) * 23]
        m = np.zeros((N_ROWS, 23), bool); m[:33] = c[:33]
        for r in range(33, N_ROWS):
            k = int(round(1.5 * (r - 33) / (N_ROWS - 34)))
            m[r, 3 + k:20 - k] = True
        out.append(m)
    return out


N_TOP = 614                                  # (la rangée 0 des images de Naruto : ses épis à 626)
N_ROWS = 47                                  # (jusqu'au coussin, rangée 660)
T_ROW0, T_ROWS, T_W = 600, 43, 48            # Teuchi : sa première rangée, ses rangées (sous le comptoir comprises), sa largeur
S_ROW0, S_ROWS, S_W = 620, 42, 36            # le client assis
R_X, R_BACK, R_ROW0, R_ROWS, R_W = 1194.0, 0.35, 500, 192, 84   # Teuchi à la porte : sa colonne, derrière la vitre de tant (m)
WALK_END = (1175.0, 0.32)                    # le client qui s'en va : à la porte, la colonne de son milieu, derrière la vitre de tant
WALK_TOP = 1.82                              # (le haut de son chapeau)
PLACES = {'counter': 1199.0, 'pots': -0.25, 'shelf': 9.42}   # Teuchi : au comptoir (sa colonne), à la marmite (à tant de
                                             # son X, la louche à bout de bras), à l'étagère (son X, devant les bocaux de gauche)


def glass_rows():
    """chaque colonne de verre : la rangée sous la tringle du noren (un rayon vers VP), la dernière au-dessus de la traverse, la
    première au-dessous, la dernière au-dessus de la lisière du bas"""
    out = []
    for a, b in R.VITRES:
        for x in range(a, b + 1):
            top = int(np.ceil(VY - 0.2065 * (x - VX))) + 1
            bot = int(np.round(VY + R.BAS_RAYON * (x - VX) - 0.5)) - 1
            out.append([x, top, R.TRAVERSE[0], R.TRAVERSE[1], bot])
    return out


def main():
    prev = sys.argv[sys.argv.index('--preview') + 1] if '--preview' in sys.argv else None
    A = Atlas(512)
    # Teuchi : 0-2 de face (debout, les bras qui travaillent), 3-5 de profil (le pas), 6-8 de dos (debout, la louche)
    s_t = F / Z_T; top_t = EYE + (VY - T_ROW0) * Z_T / F
    T = []
    for view in ('front', 'side', 'back'):
        for a in range(3):
            T.append(A.add(raster(teuchi(view, a, 0.015 if view == 'side' and a else 0.0), T_W, T_ROWS, s_t, top_t)))
    # Teuchi à la porte, la perche levée jusqu'à la tringle (sa rangée dans la rue, ramenée à son plan)
    Xr = R.X_F + R_BACK; Zr = F * Xr / (R_X - VX); s_r = F / Zr; top_r = EYE + (VY - R_ROW0) * Zr / F
    RE = []
    for k, dx in ((0, 0.1), (1, 0.15)):
        xt = R_X + dx * s_r; pole = EYE + (VY - (VY - 0.2065 * (xt - VX) + 1)) * Zr / F
        RE.append(A.add(raster(reach(k, pole), R_W, R_ROWS, s_r, top_r)))
    # le client du coin, assis : au milieu de son tabouret
    Xs = (STOOL_X := R.col_X(R.STOOLS[0], Z_STOOL)); s_s = F / Z_S; top_s = EYE + (VY - S_ROW0) * Z_S / F
    SE = [A.add(raster(seated(a), S_W, S_ROWS, s_s, top_s)) for a in range(3)]
    # Naruto, sur le tabouret de droite
    Xn = R.col_X(R.STOOLS[2], Z_STOOL)
    NA = [A.add(m) for m in naruto_cells()]
    # le client qui s'en va, à chaque taille de son chemin (un pixel de haut de plus à chaque fois)
    Xe = R.X_F + WALK_END[1]; Ze = F * Xe / (WALK_END[0] - VX)
    H0, H1 = int(np.floor(WALK_TOP * F / Z_S)), int(np.ceil(WALK_TOP * F / Ze)) + 1
    WK = []
    for H in range(H0, H1 + 1):
        s = H / WALK_TOP; W = int(np.ceil(0.32 * s)) * 2 + 2
        WK.append([A.add(raster(standing(k), W, H, s, WALK_TOP)) for k in range(3)])
    # ce qui est devant Teuchi (la lanterne, les objets et l'arête du comptoir, les tabourets) : rien de lui n'y passe
    src = np.asarray(Image.open(R.SRC).convert('RGB')).astype(float)
    pix, hem = R.glass_pixels()
    col_, sid = R.render(src, pix)
    surf = R.reduce(col_, sid)[2]
    zx0, zy0, zx1, zy1 = R.ZONE
    occ = np.zeros((zy1 - zy0, zx1 - zx0), bool)
    for (x, y), k in zip(pix, surf):
        if k not in (1, 10): occ[y - zy0, x - zx0] = True
    OC = A.add(occ)
    # Teuchi : ses places
    X_POT = R.col_X(R.POT[1], R.Z_E)
    places = {'counter': PLACES['counter'], 'pots': round(col(X_POT + PLACES['pots'], Z_T), 1), 'shelf': round(col(PLACES['shelf'], Z_T), 1)}
    # la vapeur : des bols (leur bord) et de la marmite
    wisps = []
    for kind, (u0, v0, u1, v1), xc in R.OBJETS:
        if kind == 'bol':
            Zo = R.Z_C + R.OBJ_Z; hb = R.CTR_H + (v1 - v0) / R.K_OBJ
            wisps.append([xc, int(round(row(hb, Zo))), round(0.35 * F / Zo, 1), round(0.06 * F / Zo, 1)])
    wisps.append([R.POT[1], int(round(row(R.BACK_H + (R.V_REF - 515) / R.K_WALL, R.Z_E - 0.35))), round(0.5 * F / R.Z_E, 1), round(0.1 * F / R.Z_E, 1)])
    IRF = {'T': {'cells': T, 'y': T_ROW0, 'cx': T_W // 2, 'z': round(Z_T, 2), 'at': places},
           'R': {'cells': RE, 'x': R_X, 'y': R_ROW0, 'cx': R_W // 2, 'z': round(Zr, 2)},
           'S': {'cells': SE, 'x': round(col(STOOL_X, Z_S), 1), 'y': S_ROW0, 'cx': S_W // 2},
           'N': {'cells': NA, 'x': round(col(Xn, Z_S), 1), 'y': N_TOP, 'cx': 11.5},
           'W': {'h0': H0, 'cells': WK, 'top': WALK_TOP, 'from': [round(STOOL_X, 3), round(Z_S, 2)], 'to': [round(Xe, 3), round(Ze, 2)]},
           'O': OC + [zx0, zy0], 'G': glass_rows(), 'wisps': wisps}
    img = A.image()
    print('Teuchi Z %.2f (%.1f px/m) | client et Naruto Z %.2f (%.1f px/m) | Teuchi à la porte Z %.2f (%.1f px/m) | le client s\'en va de '
          'Z %.2f à %.2f (%d à %d px de haut) | atlas %d x %d' % (Z_T, F / Z_T, Z_S, F / Z_S, Zr, s_r, Z_S, Ze, H0, H1, img.shape[1], img.shape[0]))
    if prev:
        bg = np.full(img.shape[:2] + (3,), (200, 170, 120), np.uint8); bg[img[..., 3] > 0] = (30, 10, 8)
        Image.fromarray(bg).resize((img.shape[1] * 2, img.shape[0] * 2), Image.NEAREST).save(os.path.join(prev, 'atlas_x2.png'))
        json.dump(IRF, open(os.path.join(prev, 'irf.json'), 'w'))
        return
    Image.fromarray(img, 'RGBA').save(I.A(OUT), 'WEBP', lossless=True, quality=100, method=6, exact=True)
    js = open(JS, encoding='utf-8').read()
    line = 'const IRF = ' + json.dumps(IRF, separators=(',', ':')) + ';'
    js2, n = re.subn(r'const IRF = \{.*?\};', lambda m: line, js, count=1)
    assert n == 1, 'la ligne IRF manque dans assets/street.js'
    if js2 != js: open(JS, 'w', encoding='utf-8').write(js2)


if __name__ == '__main__':
    main()
