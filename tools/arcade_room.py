#!/usr/bin/env python3
"""La salle d'arcade vue par sa porte : une petite maquette en 3D de la salle et de l'œil de la rue, projetée.

    python3 tools/arcade_room.py                (réécrit assets/arcade_interior.webp et, dans assets/street.js, ARC_PINS et la
                                                 version de la texture : on peut le relancer)
    python3 tools/arcade_room.py --theta 0      (un autre angle pour la salle ; --preview chemin.png : des aperçus seulement)

La porte, dans la rue. La caméra de la rue est une perspective à un point : focale F = 1400 px, point de fuite (700, 615) sur
l'horizon, l'œil à EYE = 1,5 m du trottoir (celle de Red, ZR dans assets/street.js : F 1400, ses pieds sur des rayons de ce
point). Le linteau et le seuil de la porte (topAt, botAt dans assets/street.js) sont deux rayons vers ce point : le seuil, à
1,5 m sous l'œil, donne la façade à X_F = 5,35 m à droite de l'œil ; le linteau, 1,30 m au-dessus de l'œil (2,80 m du
trottoir) ; le montant du fond (x 1356) à Z = 11,41 m, le bord droit de l'image (x 1456) coupe la porte à Z = 9,90 m ; le
sol de la salle 4,9 cm au-dessus du trottoir (thrAt). Le montant a un tableau de REVEAL = 6 cm : on le voit, à l'ombre
(le bleu nuit de la façade), son arête prise dans la lumière de la salle.

La salle. Une boîte derrière la porte, tournée de THETA autour de la verticale (le seul réglage : PRESETS en tire la
profondeur du mur du bout le long de l'axe, l'orientation du tube et la place de l'image) ; son origine à l'angle intérieur
du montant du fond. À -24° (la version de la rue, celle que le propriétaire a choisie) son axe file vers la rue, vers un point
de fuite à x 77 sur l'horizon, et son mur du bout, à 5 m du montant, se voit de biais : la machine à pinces et les bornes
en rang, en perspective. Le dessin du propriétaire (tools/src/arcade_wall.webp, 667 x 2000 : le mur du bout de face) est posé
sur ce mur à l'échelle de la rue, une borne de CAB_M = 1,7 m (K = 438 pixels du dessin par mètre : le dessin fait 1,52 x
4,56 m, son plafond à 3,29 m) ; glissé en travers pour que la coupe de la machine à pinces, à son bord gauche, reste juste
derrière le montant (ou, à 0 et +24°, son bord droit au bord droit de la rue : le coffret électrique à ce bord). Ce qu'on
voit par la porte n'est qu'une bande de la salle ; au-delà du bord droit du dessin, le mur est prolongé uni (WALL_EXT), et
l'affiche de la fusée, cachée à sa place par le montant, y est rependue (HUNG). La machine à pinces et les bornes sont des
boîtes posées contre le mur (BOXES : leur face, celle du dessin ; leur flanc vers nous, du ton du bord de leur face, à
l'ombre, plus sombre contre le mur) ; la troisième borne, au-delà du dessin, prend la face de la première (CAB3). Le sol :
des planches le long de l'axe, leur bois tiré des bandes de planches du dessin (BANDS, leurs reflets ôtés, leur grain
gardé), chaque planche sa bande et ses lames décalées, sans répétition visible ; leurs joints et les bouts des lames redessinés
nets d'un pixel, plus pâles là où ils se serrent. Le plafond : les dalles du haut du dessin, leurs joints en travers. Le tube :
des réglettes (tube, boîtier, deux suspentes) pendues sous le plafond, en travers de la salle, parallèles au mur et au haut
des bornes, comme dans le dessin (TUBE_TRAVERS).

Le mur du bout, nu (tout ce que la porte en montre au-dessus des bornes, hors de ce qui y est posé : WALL_OBJ, l'enseigne
murale, les affiches, le tube électrique et le coffret, gardés de l'image) : des plaques de plâtre peintes, comme les murs des
salles de jeux japonaises (石膏ボード, peinture mate ; le bleu-violet sombre de l'image), une plaque サブロク de 910 mm du sol au
plafond, ses joints verticaux (WALL_JOINT) ; sa matière, celle que le modèle d'image a peinte de face pour lui
(tools/src/edits/arcback_prompt.txt, sa réponse arcback_draft.webp, un seul appel : python3 tools/arcade_room.py --ask) à son
échelle (DRAFT_PPM), son éclairage ôté, sa seule luminance (un ton par plan : W0, celui de l'image à côté du coffret, WALL_W0),
moyennée par chaque pixel de la porte ; ses joints nets d'un pixel, pâles comme dans la réponse. Sa lumière, calculée dans le
modèle (wall_light_map) : le tube, à 1,2 m devant lui et 0,2 m sous le plafond, la plus forte à sa hauteur puis décroissante
vers les bornes ; le flanc vitré de la machine à pinces sur le bas près du montant ; une lueur serrée autour du néon de
l'enseigne murale ; ce que la salle renvoie (WALL_AMB) ; les ombres de ce qui y est posé (le coffret, à 10 cm du mur, en fait
une sous lui). Les écrans et les frontons des bornes regardent la salle, les bornes sont adossées au mur : rien d'eux ne l'atteint.
Rapportée à la lumière du point WALL_REF, où l'image a son ton W0. Fermée : le tube, l'enseigne et la vitrine éteints, le mur
n'a plus que ce qui reste de lumière dans la salle (CLOSED, de sa lumière moyenne allumée, égal partout) et le pourtour vert de
la sortie de secours.

Le rendu. Chaque pixel de la porte est pris sur SS x SS rayons de l'œil (le tableau, la sous-face du linteau, le dessus du
seuil, puis la salle) ; la lumière : le tube, les écrans, la vitrine à pinces, l'enseigne (des points, la distance au carré,
l'angle), sur le sol (rapportée à celle que le dessin montre devant les bornes : le sol plus sombre vers nous), le plafond
(autour du tube), les flancs ; le sol reflète la salle (le rayon renvoyé, flou en hauteur) ; l'ombre de contact le long du
montant. Puis réduit au pixel entier selon ses bords : là où les rayons d'un pixel font deux groupes nets, la couleur du
groupe qui en tient plus de la moitié, sinon leur moyenne ; les reflets du sol, flous, par leur moyenne ; jamais de grain. Le dessin est d'abord adouci selon ses bords
(un petit médian là où il en a, un médian et une moyenne ailleurs). Mise à la nuit de la rue : l'équilibre de ses canaux à
mi-chemin (GRADE) de celui de l'ancienne salle (au commit BEFORE, déjà dans la lumière de la rue), ce qui luit moins
(ACC_GRADE), un peu moins saturée (SAT) ; le montant n'y est pas. Fermée : le même modèle, ses tubes, son enseigne et sa
vitrine éteints, ses écrans, la moitié de ses frontons et sa sortie de secours allumés (CLOSED : ce qui reste de lumière).

Écrit assets/arcade_interior.webp (100 x 772 : la salle allumée, rangées 0-385 du canevas de la porte, puis fermée) ; dans
assets/street_unlit.webp (la rue sans courant), sous la porte, la salle éteinte (UNLIT) à la place du rideau de fer peint, le
reste repris au commit BEFORE (la nuit rouge y lit la lumière de la salle : les lames du rideau y faisaient des traits rouges) ;
et, dans assets/street.js, ARC_PINS : où le modèle met ce que drawArcade anime (les écrans des bornes, l'enseigne, les
frontons, la vitrine à pinces, l'afficheur du coffret : des quadrilatères ; le coffret, la sortie de secours : des boîtes), et
les versions des deux images (une de plus seulement si elles ont changé). Il faut git, Pillow, numpy.
    python3 tools/arcade_room.py --ask           (la matière du mur du bout redemandée au modèle d'image : un nouvel appel)
"""
import io
import json
import os
import re
import subprocess
import sys
import numpy as np
from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = lambda p: os.path.join(ROOT, 'assets', p)
SRC = os.path.join(ROOT, 'tools', 'src', 'arcade_wall.webp')
EDITS = os.path.join(ROOT, 'tools', 'src', 'edits')
WALL_DRAFT = os.path.join(EDITS, 'arcback_draft.webp')
MODEL = 'openai/gpt-5.4-image-2'
BEFORE = 'c79076a'
LUM = np.array([0.299, 0.587, 0.114])

# ---- la caméra de la rue et la porte (assets/street.js : ARC, topAt, botAt, thrAt)
F, VX, VY = 1400.0, 700.0, 615.0
EYE = 1.5
ARC = (1356, 430, 100, 386)
TOP, BOT, THR = (26.0, -24.0), (369.0, 28.0), 6.0
S_BOT = ((ARC[1] + BOT[0] - VY) / (ARC[0] - VX) + (ARC[1] + BOT[0] + BOT[1] - VY) / (ARC[0] + ARC[2] - VX)) / 2
S_TOP = ((VY - ARC[1] - TOP[0]) / (ARC[0] - VX) + (VY - ARC[1] - TOP[0] - TOP[1]) / (ARC[0] + ARC[2] - VX)) / 2
X_F = EYE / S_BOT
Y_HEAD = S_TOP * X_F
Z_FAR = F * X_F / (ARC[0] - VX)
Z_EDGE = F * X_F / (ARC[0] + ARC[2] - VX)
Y_FL = -EYE + THR * Z_FAR / F
REVEAL = 0.06
O_X, O_Z = X_F + REVEAL, Z_FAR                    # (l'angle intérieur du montant du fond, en plan : l'origine de la salle)

# ---- la salle, tournée de THETA autour de la verticale
THETA = -24                            # la salle tournée de tant de degrés autour de la verticale (le seul réglage : son mur du
                                     # bout et ses tubes suivent, PRESETS) ; 0 : d'équerre avec la rue ; +24 : son axe vers le
                                     # fond rentrant dans la maison, comme l'ancienne ; -24 : son axe tourné vers la rue
PRESETS = {0: (5.0, 'travers', 'droite'), 24: (8.5, 'travers', 'droite'), -24: (5.0, 'travers', 'pince')}   # (le mur du bout à tant
                                     # du montant le long de l'axe ; le tube : en travers, parallèle au mur comme dans l'image,
                                     # ou le long de l'axe ; l'image glissée sur le mur : son bord droit au bord droit de la rue,
                                     # ou la coupe de la machine à pinces juste derrière le montant (le mur au-delà de l'image
                                     # alors prolongé, uni : WALL_EXT)
WALL_EXT = (640, 666, 690, 890)      # (le mur uni à droite de l'image : ses colonnes u0..u1, le coffret sauté de v0 à v1)
HUNG = (((230, 548, 393, 878), 800),)   # (sur ce mur, rependue : l'affiche de la fusée, cachée à sa place par le montant : sa
                                     # boîte dans l'image, sa colonne)
CAB3 = 517                           # (la troisième borne, au-delà de l'image : la face de la première, tant de colonnes plus loin)
CAB_M = 1.7
CAB_ROWS = (948, 1693)
K = (CAB_ROWS[1] - CAB_ROWS[0]) / CAB_M
FOOT = 1693
CEIL_ROW = 250
Y_C = Y_FL + (FOOT - CEIL_ROW) / K
BOXES = [('claw', -400, 118, 765, 1730, 0.85), ('cab1', 140, 392, 948, 1693, 0.75),
         ('cab2', 405, 655, 948, 1693, 0.75), ('cab3', 657, 907, 948, 1693, 0.75)]
TUBE_R, TUBE_HW, TUBE_HH = 0.016, 0.045, 0.035     # le tube : son rayon ; son boîtier (demi-largeur, épaisseur)
TUBE_AXE = (1405, 0.06, ((0.4, 1.25), (1.95, 1.25), (3.5, 1.25)))   # le long de l'axe : sa colonne dans la rue au bout de la
                                     # réglette du fond, sous le plafond de tant (m), ses réglettes (à tant du mur, leur longueur)
TUBE_TRAVERS = (((35, 620), (650, 1235)), 1.2, 0.2)   # en travers : ses réglettes (de la colonne u0 à u1 de l'image), à
                                     # tant du mur, sous le plafond de tant (m) ; comme dans l'image, parallèle au mur et aux bornes
PLANK = 0.2
BANDS = ((1754, 1777), (1783, 1813), (1819, 1852), (1858, 1895), (1901, 1936), (1943, 1978))
CEIL_PANEL = 1.2
SS = 8
OUT = 'arcade_interior.webp'
SCREENS = ((175, 1085, 357, 1260), (432, 1085, 606, 1260), (692, 1085, 874, 1260))   # (dans l'image : u0, v0, u1, v1) les écrans
                                                                # des trois bornes,
CLAW_GLASS = (0, 765, 118, 1400)                                # la vitrine à pinces (son haut lumineux, sa vitre), l'enseigne,
SIGN = (35, 345, 550, 490)                                      # le coffret électrique, son afficheur (sur ses ouïes), les
FUSEBOX = (563, 697, 663, 885)                                  # frontons des bornes, la sortie de secours (fermée)
DISPLAY = (567, 706, 661, 752)
MARQUEES = ((160, 962, 378, 1032), (418, 962, 640, 1032), (677, 962, 895, 1032))
EXIT = (1020, 330, 1062, 350)
EXIT_C = ((22, 96, 54), (40, 150, 82), (150, 240, 180))
FLOOR_AMB = 0.04
GRADE, ACC_GRADE = 0.5, 0.2
SAT = 0.85
GROOVE_K, JOINT_K = 0.16, 0.12
REVEAL_C, SOFFIT_C, ARRIS_C = (8, 13, 25), (5, 10, 19), (36, 20, 46)
CLOSED = 0.34
UNLIT = (0.1, (5.4, 3.6, 14.4))    # sans courant (street_unlit, sous la porte) : la salle allumée à tant, plus le sombre que
                                     # assets/street.js pose sur elle dans la coupure (rgba(6,4,16,0.9))
LIT = (((175, 1085, 357, 1260), 1.0), ((432, 1085, 606, 1260), 1.0),
       ((160, 962, 378, 1032), 0.5), ((418, 962, 640, 1032), 0.5),
       ((280, 1450, 302, 1495), 1.0), ((540, 1450, 562, 1495), 1.0))

GRADE_MN = (47.09756757304888, 32.04330884257255, 85.88874855872511)   # (la moyenne de la salle allumée que grade() rapporte à
                                     # celle de l'ancienne : mesurée une fois, le mur uni d'avant ; gardée telle, pour que le mur
                                     # refait ne change rien aux bornes ni au reste)

# ---- le mur du bout : sa matière et sa lumière
WALL_OBJ = (('sign', 35, 348, 550, 487, 0.05), ('cat', 410, 549, 546, 841, 0.008), ('rocket', 231, 555, 392, 873, 0.008),
            ('conduit', 600, 250, 625, 697, 0.03), ('coupling', 597, 555, 625, 572, 0.035), ('gland', 593, 671, 625, 697, 0.04),
            ('fuse', 563, 697, 662, 878, 0.10))
                                     # (ce qui est posé sur le mur, dans l'image : u0, v0, u1, v1, son épaisseur en m ; ses pixels
                                     # gardés, le reste de l'image du mur refait ; l'affiche de la fusée aussi rependue, HUNG)
WALL_W0 = (550, 500, 596, 690)       # (dans l'image : le mur nu entre l'affiche du chat et le tube électrique, son ton W0 ; à son
WALL_REF = (573, 595)                #  milieu, la lumière qu'il y reçoit dans le modèle, E_REF : le mur est W0 x E / E_REF)
WALL_JOINT, PANEL = 720, 0.91        # (les joints des plaques de plâtre peintes : l'un à cette colonne de l'image, puis tous les
                                     #  910 mm, une plaque サブロク de bout en bout, sans joint horizontal)
DRAFT_PPM, DRAFT_SIGMA = 630 / 0.91, 150    # (la réponse du modèle d'image : ses deux joints à 630 px l'un de l'autre, 692 px le
DRAFT_JOINTS = ((195, 200), (824, 830))     #  mètre ; son éclairage ôté au-dessus de 150 px ; ses joints, effacés de la peinture)
JOINT_K = 0.06                       # (un joint : le trait pâle de la réponse (31 % plus clair sur un de ses pixels, 1,4 mm),
                                     #  comme les joints du sol, net d'un pixel de la porte, au cinquième de son contraste)
WALL_AMB = 0.3                       # (la lumière que la salle renvoie sur le mur, du rose du tube, en plus du direct)
PAINT_GAIN = 1.0                     # (la peinture de la réponse, ses écarts à 1 multipliés par tant)
SIGN_I, EXIT_I = 0.01, 0.015         # (le néon de l'enseigne murale, son cadre, par m ; la sortie de secours, fermée, son pourtour)
CLAW_SIDE = (118, 0.85)              # (le flanc vitré de la machine à pinces vers les bornes : sa colonne, sa profondeur)

S_OUT, S_RISER, S_SOFFIT, S_SILL, S_REVEAL, S_CEIL, S_FLOOR, S_WALL = 0, 1, 2, 3, 4, 5, 6, 7
S_TUBE, S_TUBEC, S_HOUSE, S_HOUSEC = 30, 31, 32, 33     # (le tube : son dessous et son flanc ; son embout ; le boîtier ; son bout)


def configure(theta):
    """la salle tournée de theta degrés (son axe vers le fond : + rentrant dans la maison, - vers la rue), son mur du bout à tant
    du montant du fond le long de cet axe (PRESETS) ; l'image posée dessus, son bord droit sur le bord droit de l'image de la rue
    (la bande qu'on voit : le coffret électrique à son bord, une borne et son écran) ; ses tubes"""
    global TH, CT, ST, S_END, T_L, TUBES, TUBE_Y, VPA, KIND, PLACE
    TH = np.radians(theta); CT, ST = np.cos(TH), np.sin(TH)
    S_END, KIND, PLACE = PRESETS[int(round(theta))]
    VPA = VX + F * np.tan(TH)
    if PLACE == 'droite': T_L = hit_t(ARC[0] + ARC[2], S_END) - 667 / K
    else: T_L = hit_t(F * (X_F + REVEAL) / Z_FAR + VX - 3, S_END - BOXES[0][5])
    if KIND == 'axe':
        x, drop, runs = TUBE_AXE
        TUBE_Y = Y_C - drop - TUBE_R
        tt = hit_t(x, S_END - runs[0][0])
        TUBES = [('axe', tt, S_END - a - l, S_END - a) for a, l in runs]
    else:
        runs, back, drop = TUBE_TRAVERS
        TUBE_Y = Y_C - drop - TUBE_R
        TUBES = [('travers', S_END - back, T_L + u0 / K, T_L + u1 / K) for u0, u1 in runs]


def to_room(X, Z):
    return (X - O_X) * CT - (Z - O_Z) * ST, (X - O_X) * ST + (Z - O_Z) * CT


def to_world(t, s):
    return O_X + t * CT + s * ST, O_Z - t * ST + s * CT


def hit_t(x, s):
    """la colonne x de la rue rencontre le plan s de la salle (horizontalement) à ce t"""
    dx = (x - VX) / F
    t0, s0 = to_room(0.0, 0.0); dt, ds = dx * CT - ST, dx * ST + CT
    return t0 + (s - s0) / ds * dt


def proj(X, Y, Z):
    return VX + F * X / Z, VY - F * Y / Z


def proj_room(t, Y, s):
    X, Z = to_world(t, s)
    return proj(X, Y, Z)


def smooth_src():
    im0 = Image.open(SRC).convert('RGB')
    fine = np.asarray(im0.filter(ImageFilter.MedianFilter(3))).astype(float)
    soft = np.asarray(im0.filter(ImageFilter.MedianFilter(7)).filter(ImageFilter.BoxBlur(6))).astype(float)
    def box(a, r):
        p_ = np.pad(a, r + 1, mode='edge').cumsum(0).cumsum(1); n_ = 2 * r + 1
        return (p_[n_:, n_:] - p_[:-n_, n_:] - p_[n_:, :-n_] + p_[:-n_, :-n_])[:a.shape[0], :a.shape[1]] / n_ ** 2
    lg = np.asarray(im0.convert('L')).astype(float); mu = box(lg, 5)
    w = np.clip((9 - np.sqrt(np.maximum(box(lg * lg, 5) - mu ** 2, 0))) / 5, 0, 1)[..., None]
    return fine * (1 - w) + soft * w


def tex(img, u, v):
    h, w = img.shape[:2]
    return img[np.clip(np.floor(v).astype(int), 0, h - 1), np.clip(np.floor(u).astype(int), 0, w - 1)]


def plain_wall(img):
    """le mur uni au-delà du bord droit de l'image, rangée par rangée : la médiane de ses dernières colonnes (WALL_EXT), le
    coffret sauté (ses rangées : de l'une à l'autre de ses voisines)"""
    u0, u1, v0, v1 = WALL_EXT
    P = np.median(img[:, u0:u1], 1)
    k = (np.arange(v0, v1) - v0) / (v1 - v0)
    P[v0:v1] = P[v0 - 1] * (1 - k[:, None]) + P[v1] * k[:, None]
    return P


def wall_tex(img, pw, u, v):
    c = tex(img, u, v)
    out = u >= img.shape[1] - 1
    if out.any(): c[out] = pw[np.clip(np.floor(v[out]).astype(int), 0, img.shape[0] - 1)]
    for (a0, b0, a1, b1), d in HUNG:                                       # (les affiches rependues là)
        m = (u >= d) & (u < d + a1 - a0) & (v >= b0) & (v < b1)
        if m.any(): c[m] = tex(img, u[m] - d + a0, v[m])
    return c


def hsh(n, s=0):
    return (np.sin(n * 12.9898 + s * 78.233) * 43758.5453) % 1.0


def tube_boxes():
    """les réglettes en boîtes de la salle (t0, t1, y0, y1, s0, s1, leurs faces : de face, de gauche, de dessous) : le tube, son
    boîtier au-dessus, ses deux suspentes"""
    r, hw, hh, B = TUBE_R, TUBE_HW, TUBE_HH, []
    for kind, c, a0, a1 in TUBES:
        def bx(w, y0, y1, l0, l1, ids):
            B.append((c - w, c + w, y0, y1, l0, l1, ids) if kind == 'axe' else (l0, l1, y0, y1, c - w, c + w, ids))
        end, side = (S_TUBEC, S_TUBE) if kind == 'axe' else (S_TUBE, S_TUBEC)
        bx(r, TUBE_Y - r, TUBE_Y + r, a0, a1, (end, side, S_TUBE))
        bx(hw, TUBE_Y + r, TUBE_Y + r + TUBE_HH, a0 - 0.03, a1 + 0.03, ((S_HOUSEC, S_HOUSE) if kind == 'axe' else (S_HOUSE, S_HOUSEC)) + (S_HOUSE,))
        for m in (a0 + 0.2, a1 - 0.2):
            B.append((c - 0.006, c + 0.006, TUBE_Y + r + hh, Y_C, m - 0.006, m + 0.006, (S_HOUSEC,) * 3) if kind == 'axe'
                     else (m - 0.006, m + 0.006, TUBE_Y + r + hh, Y_C, c - 0.006, c + 0.006, (S_HOUSEC,) * 3))
    return B


def tube_points(n=8):
    for kind, c, a0, a1 in TUBES:
        for a in range(n):
            q = a0 + (a + 0.5) / n * (a1 - a0)
            yield (to_world(c, q) if kind == 'axe' else to_world(q, c)), (a1 - a0) / n


def cast_room(O, D, live):
    """les rayons dans la salle (origine O, direction D, dans la rue) : ce que chacun touche le premier ; leurs coordonnées dans la
    salle (t en travers, Y, s vers le fond)"""
    INF = 1e9
    ot, os_ = to_room(O[..., 0], O[..., 2]); oy = O[..., 1]
    dt = D[..., 0] * CT - D[..., 2] * ST; ds = D[..., 0] * ST + D[..., 2] * CT; dy = D[..., 1]
    lb = np.full(D.shape[:-1], INF); sid = np.zeros(D.shape[:-1], np.int16)
    def take(l, ok, s):
        nonlocal lb, sid
        m = live & ok & (l > 1e-6) & (l < lb)
        lb = np.where(m, l, lb); sid = np.where(m, s, sid)
    with np.errstate(divide='ignore', invalid='ignore'):
        lt = lambda v: (v - ot) / dt
        ly = lambda v: (v - oy) / dy
        ls = lambda v: (v - os_) / ds
        T = lambda l: ot + l * dt
        Yy = lambda l: oy + l * dy
        S = lambda l: os_ + l * ds
        inn = lambda v, a, b: (v >= a) & (v <= b)
        l = ls(S_END); take(l, np.ones_like(live), S_WALL)
        l = ly(Y_C); take(l, (dy > 0) & (S(l) <= S_END), S_CEIL)
        l = ly(Y_FL); take(l, (dy < 0) & (S(l) <= S_END), S_FLOOR)
        for b, (name, u0, u1, vt, vb, d) in enumerate(BOXES):
            t0, t1, y1, s0 = T_L + u0 / K, T_L + u1 / K, Y_FL + (vb - vt) / K, S_END - d
            l = ls(s0); take(l, inn(T(l), t0, t1) & inn(Yy(l), Y_FL, y1), 10 + 2 * b)
            l = lt(t0); take(l, (dt > 0) & inn(S(l), s0, S_END) & inn(Yy(l), Y_FL, y1), 11 + 2 * b)
        for t0, t1, y0, y1, s0, s1, (fr, lf, bt) in tube_boxes():           # (les réglettes : leur face, leur flanc, leur dessous)
            l = ls(s0); take(l, (ds > 0) & inn(T(l), t0, t1) & inn(Yy(l), y0, y1), fr)
            l = lt(t0); take(l, (dt > 0) & inn(S(l), s0, s1) & inn(Yy(l), y0, y1), lf)
            l = ly(y0); take(l, (dy > 0) & inn(T(l), t0, t1) & inn(S(l), s0, s1), bt)
    P = O + lb[..., None] * D
    t, s = to_room(P[..., 0], P[..., 2])
    return sid, P, np.stack([t, P[..., 1], s], -1)


def primary():
    H, W = ARC[3], ARC[2]
    j, i = np.mgrid[0:H * SS, 0:W * SS]
    sx = ARC[0] + (i + 0.5) / SS; sy = ARC[1] + (j + 0.5) / SS
    dx = (sx - VX) / F; dy = (VY - sy) / F
    D = np.stack([dx, dy, np.ones_like(dx)], -1)
    z0 = X_F / dx; y0 = dy * z0
    inside = (y0 <= Y_HEAD) & (y0 >= Y_FL)
    riser = (y0 < Y_FL) & (y0 >= -EYE)
    z1 = (X_F + REVEAL) / dx
    INF = 1e9
    zb = np.full(dx.shape, INF); sid = np.zeros(dx.shape, np.int16)
    def take(z, ok, s):
        nonlocal zb, sid
        m = ok & (z < zb)
        zb = np.where(m, z, zb); sid = np.where(m, s, sid)
    take(np.full(dx.shape, Z_FAR), inside & (dx * Z_FAR <= X_F + REVEAL), S_REVEAL)
    with np.errstate(divide='ignore', invalid='ignore'):
        zs = np.where(dy > 0, Y_HEAD / dy, INF); zf = np.where(dy < 0, Y_FL / dy, INF)
    take(zs, inside & (zs >= z0) & (zs <= np.minimum(z1, Z_FAR)), S_SOFFIT)
    take(zf, inside & (zf >= z0) & (zf <= np.minimum(z1, Z_FAR)), S_SILL)
    room = inside & (z1 <= Z_FAR) & (sid == 0)
    rs, RP, RQ = cast_room(np.zeros(D.shape), D, room)
    sid = np.where(room, rs, sid)
    P = np.where(room[..., None], RP, D * zb[..., None])
    sid = np.where(riser, S_RISER, np.where(inside, sid, S_OUT))
    return sid, P, RQ, D


# ---- les lumières : des points (position, normale d'émission ou None, couleur x intensité x aire), dans la rue
def lights(img, state):
    L = []
    na = (-ST, 0.0, -CT)                                                   # (ce qui fait face à la porte, dans la salle)
    def rect(t0, t1, y0, y1, s, col, I, n=4):
        for a in range(n):
            for b in range(n):
                X, Z = to_world(t0 + (a + 0.5) / n * (t1 - t0), s)
                L.append(((X, y0 + (b + 0.5) / n * (y1 - y0), Z), na, np.array(col) / 255 * I * (t1 - t0) * (y1 - y0) / n / n))
    def src_rect(u0, u1, v0, v1, vb, s, I, n=4, pos=None):
        col = img[v0:v1, u0:u1].reshape(-1, 3).mean(0)
        p0, p1 = pos or (u0, u1)
        rect(T_L + p0 / K, T_L + p1 / K, Y_FL + (vb - v1) / K, Y_FL + (vb - v0) / K, s, col, I, n)
    sc = S_END - BOXES[1][5]
    src_rect(185, 350, 1095, 1250, FOOT, sc, 1.0)                                   # l'écran de la première borne
    src_rect(440, 600, 1095, 1250, FOOT, sc, 1.0)                                   # celui de la seconde
    src_rect(185, 350, 1095, 1250, FOOT, sc, 1.0, pos=(185 + CAB3, 350 + CAB3))     # celui de la troisième
    if state == 'lit':
        src_rect(5, 110, 880, 1380, BOXES[0][4], S_END - BOXES[0][5], 1.0, 5, pos=(-260, 110))   # la vitrine à pinces
        src_rect(40, 545, 350, 485, FOOT, S_END - 0.01, 0.6, 4)                     # l'enseigne
        col = np.array([250, 120, 200]) / 255
        for (X, Z), dl in tube_points():                                   # les tubes
            L.append(((X, TUBE_Y - TUBE_R, Z), None, col * 1.1 * dl))
    return L


def blur(a, sigma):
    """un flou gaussien (trois flous en boîte, les bords en miroir) d'une image en niveaux"""
    r = max(1, int(round((np.sqrt(4 * sigma ** 2 + 1) - 1) / 2)))
    for ax in (0, 1):
        for _ in range(3):
            p = np.pad(a, [(r + 1, r), (0, 0)] if ax == 0 else [(0, 0), (r + 1, r)], mode='symmetric')
            c = np.cumsum(p, ax)
            a = ((c[2 * r + 1:] - c[:-2 * r - 1]) if ax == 0 else (c[:, 2 * r + 1:] - c[:, :-2 * r - 1])) / (2 * r + 1)
    return a


def wall_paint():
    """la peinture du mur : la réponse du modèle d'image (tools/src/edits/arcback_draft.webp : le mur nu de face, peint, à
    DRAFT_PPM px le mètre), sa luminance rapportée à son propre flou (DRAFT_SIGMA : son éclairage ôté, sa matière gardée : le
    grain du rouleau, ses taches, ses traces de ruban, ses éraflures), ses deux joints effacés (wall_joints les remet à leur
    place) : un rapport autour de 1, du même ton partout"""
    a = np.asarray(Image.open(WALL_DRAFT).convert('RGB')).astype(float) @ LUM
    for x0, x1 in DRAFT_JOINTS:
        k = (np.arange(x0, x1) - (x0 - 1)) / (x1 - x0 + 1)
        a[:, x0:x1] = a[:, x0 - 1:x0] * (1 - k[None]) + a[:, x1:x1 + 1] * k[None]
    return 1 + PAINT_GAIN * (a / blur(a, DRAFT_SIGMA) - 1)


def mirror(x, n):
    x = np.mod(x, 2 * n)
    return np.where(x >= n, 2 * n - 1 - x, x)


def wall_detail(paint, t, Y):
    """la peinture au point (t, Y) du mur : la réponse à son échelle (DRAFT_PPM), d'un seul tenant, en miroir à ses bords (le pli
    du milieu derrière l'affiche de la fusée rependue)"""
    h, w = paint.shape
    x = (t - (T_L + 880 / K)) * DRAFT_PPM + w - 0.5
    y = (Y_C - Y) * DRAFT_PPM
    return paint[mirror(np.floor(y).astype(int), h), mirror(np.floor(x).astype(int), w)]


def wall_objects(u, v):
    """ce qui est posé sur le mur (WALL_OBJ) aux points (u, v) de l'image : leurs pixels sont ceux de l'image"""
    m = np.zeros(np.shape(u), bool)
    du = HUNG[0][1] - HUNG[0][0][0]
    for name, u0, v0, u1, v1, _ in WALL_OBJ:
        m |= (u >= u0) & (u < u1) & (v >= v0) & (v < v1)
        if name == 'rocket': m |= (u >= u0 + du) & (u < u1 + du) & (v >= v0) & (v < v1)
    return m


def wall_boxes():
    """ce qui est posé sur le mur, en boîtes de la salle (t0, t1, Y0, Y1, épaisseur) : leurs ombres"""
    B, du = [], HUNG[0][1] - HUNG[0][0][0]
    for name, u0, v0, u1, v1, d in WALL_OBJ:
        for o in ((0, du) if name == 'rocket' else (0,)):
            B.append((T_L + (u0 + o) / K, T_L + (u1 + o) / K, Y_FL + (FOOT - v1) / K, Y_FL + (FOOT - v0) / K, d))
    return B


def wall_lights(img, state):
    """ce qui éclaire le mur du bout, en points (position dans la rue, normale d'émission ou None, couleur x puissance, portée en
    m ou None). Allumée : le tube, ses deux réglettes à 1,2 m du mur et 0,2 m sous le plafond (une ligne de points nus : sa
    lumière tombe sur le mur de face et d'en haut, la plus forte à sa hauteur, puis en descendant) ; le flanc vitré de la machine
    à pinces, au-dessus de la première borne (CLAW_SIDE : la vitrine éclairée de l'intérieur, son rose sur le bas du mur près
    du montant) ; le cadre de néon de l'enseigne murale, devant sa boîte (une lueur serrée autour d'elle). Les écrans et les
    frontons des bornes regardent la salle et les bornes sont adossées au mur : rien de leur lumière ne monte sur lui. Fermée :
    la sortie de secours (son pourtour vert), le reste éteint"""
    L = []
    if state == 'lit':
        col = np.array([250, 120, 200]) / 255
        for kind, c, a0, a1 in TUBES:
            n = 24
            for a in range(n):
                q = a0 + (a + 0.5) / n * (a1 - a0)
                X, Z = to_world(c, q) if kind == 'axe' else to_world(q, c)
                L.append(((X, TUBE_Y, Z), None, col * 1.1 * (a1 - a0) / n, None))
        u, d = CLAW_SIDE
        t0, y0, y1 = T_L + u / K + 1e-3, Y_FL + CAB_M, Y_FL + (BOXES[0][4] - BOXES[0][3]) / K
        ccol, ne, n = img[880:1380, 5:110].reshape(-1, 3).mean(0) / 255, (CT, 0.0, -ST), 6
        for a in range(n):
            for b in range(n):
                X, Z = to_world(t0, S_END - d + (a + 0.5) / n * d)
                L.append(((X, y0 + (b + 0.5) / n * (y1 - y0), Z), ne, ccol * d * (y1 - y0) / n / n, None))
        name, u0, v0, u1, v1, dep = WALL_OBJ[0]
        scol = img[352:357, 60:540].reshape(-1, 3).mean(0) / 255
        L += ring(u0, v0, u1, v1, dep + 0.005, scol * SIGN_I, 0.02, 0.5)
    else:
        u0, v0, u1, v1 = EXIT
        L += ring(u0, v0, u1, v1, 0.03, np.array(EXIT_C[1]) / 255 * EXIT_I, 0.01, 0.3)
    return L


def ring(u0, v0, u1, v1, dep, col, step, reach):
    """des points de lumière le long du pourtour d'une boîte de l'image posée sur le mur, à tant devant lui (un néon, un liseré)"""
    L, s = [], S_END - dep
    ta, tb, ya, yb = T_L + u0 / K, T_L + u1 / K, Y_FL + (FOOT - v1) / K, Y_FL + (FOOT - v0) / K
    for (p0, p1) in (((ta, ya), (tb, ya)), ((tb, ya), (tb, yb)), ((tb, yb), (ta, yb)), ((ta, yb), (ta, ya))):
        ln = np.hypot(p1[0] - p0[0], p1[1] - p0[1]); n = max(1, int(np.ceil(ln / step)))
        for a in range(n):
            k = (a + 0.5) / n
            X, Z = to_world(p0[0] + k * (p1[0] - p0[0]), s)
            L.append(((X, p0[1] + k * (p1[1] - p0[1]), Z), None, col * ln / n, reach))
    return L


WALL_GRID = 0.005


def wall_light_map(img, state):
    """la lumière que le mur du bout reçoit, sur une grille de WALL_GRID m (t en travers, Y), ombres comprises : chaque point de
    lumière caché par ce qui est posé sur le mur (WALL_OBJ, à son épaisseur) n'y compte pas (le coffret électrique, à 10 cm du
    mur, fait sous lui une ombre de la largeur de sa porte, la plus franche contre lui) ; plus WALL_AMB, ce que la salle allumée
    renvoie. Rapportée à celle du point WALL_REF (E_REF, allumée), elle donne le ton du mur : W0 x E / E_REF"""
    ta, tb = T_L + 380 / K, T_L + 1260 / K
    ya, yb = Y_FL + CAB_M - 0.05, Y_C
    nt, ny = int(np.ceil((tb - ta) / WALL_GRID)) + 1, int(np.ceil((yb - ya) / WALL_GRID)) + 1
    tt, yy = np.meshgrid(ta + np.arange(nt) * WALL_GRID, ya + np.arange(ny) * WALL_GRID)
    X, Z = to_world(tt, S_END)
    P = np.stack([X, yy, Z], -1).reshape(-1, 3)
    tP, YP = tt.reshape(-1), yy.reshape(-1)
    nW = -np.array([ST, 0.0, CT])
    E = np.zeros(P.shape)
    boxes = wall_boxes()
    for (p, ne, c, reach) in wall_lights(img, state):
        p = np.array(p, float)
        tl, sl = to_room(p[0], p[2]); yl = p[1]; dz = S_END - sl
        idx = np.arange(len(P)) if reach is None else np.nonzero((np.abs(tP - tl) < reach) & (np.abs(YP - yl) < reach))[0]
        d = p - P[idx]
        r2 = (d ** 2).sum(-1) + 1e-5; r = np.sqrt(r2)
        w = np.maximum(0, d @ nW / r) / r2
        if ne is not None: w = w * np.maximum(0, -(d @ np.array(ne)) / r)
        for (b0, b1, c0, c1, db) in boxes:                                  # (le segment du mur à la lumière, sur l'épaisseur de
            lm = 1.0 if dz <= db else db / dz                               #  la boîte : passe-t-il dedans ?)
            near = (tP[idx] > b0 - 0.4) & (tP[idx] < b1 + 0.4) & (YP[idx] > c0 - 0.4) & (YP[idx] < c1 + 0.1)
            if not near.any(): continue
            j = np.nonzero(near)[0]
            tq, yq = tP[idx][j], YP[idx][j]
            lo, hi = np.zeros(len(j)), np.full(len(j), lm)
            for q, a0, a1, e in ((tq, b0, b1, tl), (yq, c0, c1, yl)):
                dd = e - q
                with np.errstate(divide='ignore', invalid='ignore'):
                    k0, k1 = (a0 - q) / dd, (a1 - q) / dd
                flat_ = np.abs(dd) < 1e-12
                inside = (q >= a0) & (q <= a1)
                lo = np.maximum(lo, np.where(flat_, np.where(inside, -np.inf, np.inf), np.minimum(k0, k1)))
                hi = np.minimum(hi, np.where(flat_, np.where(inside, np.inf, -np.inf), np.maximum(k0, k1)))
            w[j] = np.where(lo < hi, 0, w[j])
        E[idx] += w[:, None] * c
    if state == 'lit':
        E += WALL_AMB * np.array([250, 120, 200]) / 255
    return E.reshape(ny, nt, 3), (ta, ya)


def wall_light_at(Emap, t, Y):
    """la lumière du mur aux points (t, Y) : sa grille, bilinéaire"""
    E, (ta, ya) = Emap
    ny, nt = E.shape[:2]
    x = np.clip((t - ta) / WALL_GRID, 0, nt - 1.001); y = np.clip((Y - ya) / WALL_GRID, 0, ny - 1.001)
    x0, y0 = np.floor(x).astype(int), np.floor(y).astype(int); fx, fy = (x - x0)[:, None], (y - y0)[:, None]
    return (E[y0, x0] * (1 - fx) * (1 - fy) + E[y0, x0 + 1] * fx * (1 - fy) + E[y0 + 1, x0] * (1 - fx) * fy
            + E[y0 + 1, x0 + 1] * fx * fy)


def irradiance(L, P, n, wrap=0.0):
    E = np.zeros(P.shape)
    for (p, ne, c) in L:
        d = np.array(p) - P
        r2 = (d ** 2).sum(-1) + 0.02
        r = np.sqrt(r2)
        cr = np.maximum(0, ((d * n).sum(-1) / r + wrap) / (1 + wrap))
        ce = np.maximum(0, -(d * np.array(ne)).sum(-1) / r) if ne is not None else 1.0
        E += (cr * ce / r2)[..., None] * c
    return E


# ---- le sol : les planches de l'image, le long de l'axe de la salle
def floor_library(img):
    strips = []
    for v0, v1 in BANDS:
        band = img[v0:v1 + 1, :, :]
        st = np.asarray(Image.fromarray(np.clip(band, 0, 255).astype(np.uint8)).resize((band.shape[1], 12), Image.BILINEAR)).astype(float)
        med = np.median(st.reshape(-1, 3), 0)
        lum = st @ LUM; ml = np.median(lum)
        g = np.clip(lum / max(ml, 1), 0.85, 1.15)
        g = 1 + (g - np.convolve(g.mean(0), np.ones(31) / 31, 'same')[None]) * 0.5   # (son grain, ses reflets ôtés)
        strips.append(med[None, None] * g[..., None])
    return strips


def plank(t, s):
    """la planche sous (t, s) : son rang, sa lame (son bout : où elle commence le long de l'axe)"""
    n = np.floor(t / PLANK)
    blen = 1.1 + 0.9 * hsh(n, 2); off = hsh(n, 3) * 3.0
    return n, np.floor((s + off) / blen), blen, off


def floor_col(lib, t, s):
    n, bi, blen, off = plank(t, s)
    f = t / PLANK - n
    k = (hsh(n, 1) * len(lib)).astype(int)
    tone = 0.95 + 0.1 * hsh(bi * 7 + n, 4)
    u = (((s + off) * K * 0.7 + hsh(bi, 5) * 400) % 600).astype(int) + 30
    v = np.clip((f * 12).astype(int), 0, 11)
    out = np.zeros(t.shape + (3,))
    for j, st in enumerate(lib):
        m = k == j
        out[m] = st[v[m], u[m]]
    return out * tone[..., None]


_WALL = {}


def wall_setup(img):
    """une fois : la peinture (wall_paint), la lumière du mur allumée et fermée (wall_light_map), le ton du mur W0 (la médiane
    de l'image sur WALL_W0) et E_REF (la lumière allumée en WALL_REF)"""
    if not _WALL:
        u0, v0, u1, v1 = WALL_W0
        _WALL['W0'] = np.median(img[v0:v1, u0:u1].reshape(-1, 3), 0)
        _WALL['paint'] = wall_paint()
        _WALL['E'] = {s: wall_light_map(img, s) for s in ('lit', 'closed')}
        _WALL['E_REF'] = wall_light_at(_WALL['E']['lit'], np.array([T_L + WALL_REF[0] / K]), np.array([Y_FL + (FOOT - WALL_REF[1]) / K]))[0]
        E, (ta, ya) = _WALL['E']['lit']                                    # (sa lumière moyenne, allumée, sur ce qu'on en voit)
        tt, yy = ta + np.arange(E.shape[1]) * WALL_GRID, ya + np.arange(E.shape[0]) * WALL_GRID
        sel = ((tt >= T_L + 457 / K) & (tt <= T_L + 1222 / K))[None] & (yy >= Y_FL + CAB_M)[:, None]
        _WALL['E_MEAN'] = E[sel].mean(0)
    return _WALL


def wall_joints(out, surf):
    """les joints des plaques, nets d'un pixel : chacun une verticale du mur, donc une colonne de la porte ; le trait pâle de la
    réponse (31 % plus clair sur un pixel de la réponse) rapporté à la part de la colonne qu'il couvre ; pas sur ce qui est posé"""
    H, W = ARC[3], ARC[2]
    for k in range(-3, 5):
        uj = WALL_JOINT + k * PANEL * K
        tj = T_L + uj / K
        X, Z = to_world(tj, S_END)
        x = VX + F * X / Z - ARC[0]
        c = int(np.floor(x))
        if not 0 <= c < W: continue
        for r in range(H):
            if surf[r, c] != S_WALL: continue
            v = FOOT - ((VY - (ARC[1] + r + 0.5)) * Z / F - Y_FL) * K
            if not wall_objects(np.array(uj), np.array(v)): out[r, c] *= 1 + JOINT_K
    return out


def shade_points(img, sid, P, Q, lib, Ls, state):
    """la couleur de chaque point touché (P dans la rue, Q dans la salle), sa surface éclairée par la salle"""
    LS_LIT = lights(img, 'lit')
    PW = plain_wall(img)
    t, Y, s = Q[..., 0], Q[..., 1], Q[..., 2]
    C = np.zeros(sid.shape + (3,)); EM = np.zeros(sid.shape)
    lit = state == 'lit'
    nB = np.array([-CT, 0, ST])                                            # (la normale d'un flanc gauche)
    def flat(m, u, v):                                                     # (le mur et les faces des meubles : l'image ; fermée,
        c = wall_tex(img, PW, u, v)                                        # sombre, ses écrans et ses voyants gardés)
        k = np.zeros(len(u))
        for (u0, v0, u1, v1), kk in LIT:
            k = np.maximum(k, kk * ((u >= u0) & (u < u1) & (v >= v0) & (v < v1)))
        EM[m] = k
        return c if lit else c * (CLOSED + (1 - CLOSED) * k[:, None])
    m = sid == S_WALL
    if m.any():                                                            # (le mur nu : sa peinture, dans la lumière qu'il reçoit ;
        u, v = (t[m] - T_L) * K, FOOT - (Y[m] - Y_FL) * K                  #  ce qui y est posé, l'image)
        c = flat(m, u, v)
        bg = ~wall_objects(u, v)
        if bg.any():
            W = wall_setup(img)
            tb, yb = t[m][bg], Y[m][bg]
            E = wall_light_at(W['E'][state], tb, yb) / W['E_REF']
            c[bg] = W['W0'] * wall_detail(W['paint'], tb, yb)[:, None] * (E if lit else CLOSED * W['E_MEAN'] / W['E_REF'] + E)
        C[m] = c
    for b, (name, u0, u1, vt, vb, d) in enumerate(BOXES):
        m = sid == 10 + 2 * b
        u = (t[m] - T_L) * K
        if name == 'cab3': u = u - CAB3
        if name == 'claw': u = np.maximum(u, 2)
        C[m] = flat(m, u, vb - (Y[m] - Y_FL) * K)
        m = sid == 11 + 2 * b
        if m.any():                                                        # (un flanc : le bord de sa face, à l'ombre, plus
            ue = max(u0, 0) - (CAB3 if name == 'cab3' else 0)              # sombre contre le mur)
            v = vb - (Y[m] - Y_FL) * K
            edge = np.mean([tex(img, np.full(m.sum(), ue + k + 0.5), v) for k in range(1, 7)], 0)
            q = (S_END - s[m]) / d
            kk = 1 if lit else CLOSED
            C[m] = edge * (0.30 + 0.12 * q[:, None]) * kk + edge * np.minimum(irradiance(Ls, P[m], nB) * 0.9, 0.6) \
                + (0 if lit else edge * np.minimum(irradiance(LS_LIT, P[m], nB) * 0.9, 0.6) * CLOSED)
    m = sid == S_FLOOR
    if m.any():                                                            # (le sol : ses planches dans la lumière de la salle,
        fc = floor_col(lib, t[m], s[m])                                    # rapportée à celle qu'il a dans l'image, devant les bornes)
        n_ = np.array([0, 1.0, 0])
        X, Z = to_world(T_L + 400 / K, S_END - 1.15)
        Eref = irradiance(LS_LIT, np.array([[X, Y_FL, Z]]), n_)[0]
        Sg = (FLOOR_AMB + irradiance(LS_LIT, P[m], n_)) / (FLOOR_AMB + Eref)
        if not lit: Sg = Sg * CLOSED + irradiance(Ls, P[m], n_) / (FLOOR_AMB + Eref)
        C[m] = fc * np.clip(Sg, 0, 1.6)
    m = sid == S_CEIL
    if m.any():
        dd = (S_END - s[m]) / CEIL_PANEL; f = dd - np.floor(dd)
        a, b = np.median(img[60:100, 200:450].reshape(-1, 3), 0), np.median(img[10:30, 200:450].reshape(-1, 3), 0)
        cc = a[None] * (1 - f[:, None]) + b[None] * f[:, None]
        E = irradiance(LS_LIT, P[m], np.array([0, -1.0, 0]), wrap=0.35)
        C[m] = (cc * 0.3 + cc * np.minimum(E * 0.5, 1.2)) * (1 if lit else CLOSED)
    r = TUBE_R
    m = sid == S_TUBE                                                      # (le tube : en travers de lui, de son flanc à son dessous,
    if m.any():                                                            # le rose de l'image, le cœur clair)
        prof = np.array([[189, 9, 133], [245, 53, 170], [252, 140, 200], [254, 174, 211], [252, 140, 200], [245, 53, 170], [189, 9, 133]], float)
        kind, c = TUBES[0][0], np.array([q[1] for q in TUBES])
        across = t[m] if kind == 'axe' else s[m]                           # (en travers du tube, sur son dessous)
        c0 = c[np.abs(across[:, None] - c[None]).argmin(1)]
        w = np.where(Y[m] > TUBE_Y - r + 1e-4, (TUBE_Y + r - Y[m]) / (2 * r) * 0.5, 0.5 + 0.5 * (across - (c0 - r)) / (2 * r))
        C[m] = prof[np.clip((w * len(prof)).astype(int), 0, len(prof) - 1)]
        EM[m] = 1
        if not lit: C[m] = C[m] * 0.1 + 18
    m = sid == S_TUBEC
    C[m] = (88, 74, 140) if lit else (22, 18, 34)
    m = sid == S_HOUSE                                                     # (le boîtier : le métal de l'image, son dessous pris
    if m.any():                                                            # dans la lumière du tube)
        under = Y[m] < TUBE_Y + r + 1e-4
        C[m] = np.where(under[:, None], np.array([150, 60, 140]) if lit else np.array([26, 18, 40]), np.array([46, 24, 80]) * (1 if lit else 0.5))
    m = sid == S_HOUSEC
    C[m] = (40, 22, 70) if lit else (16, 10, 26)
    C[sid == S_REVEAL] = REVEAL_C
    C[(sid == S_SOFFIT) | (sid == S_SILL) | (sid == S_RISER)] = SOFFIT_C
    return C, EM


def render(img, state):
    lib = floor_library(img)
    Ls = lights(img, state)
    sid, P, Q, D = primary()
    C, EM = shade_points(img, sid, P, Q, lib, Ls, state)
    RF = np.zeros(C.shape)                                                 # (ses reflets, à part : réduits par leur moyenne)
    # le sol luit : ce qu'il reflète (le rayon renvoyé vers le haut, flou en hauteur, réparti sur les points du pixel)
    m = sid == S_FLOOR
    if m.any():
        h, w = sid.shape
        jy = ((np.arange(h)[:, None] % SS) * SS + (np.arange(w)[None] % SS)) / (SS * SS) - 0.5
        Dr = D[m].copy(); Dr[:, 1] = np.maximum(-Dr[:, 1] + 0.25 * jy[m], 0.002)
        rs, RP, RQ = cast_room(P[m], Dr, np.ones(m.sum(), bool))
        RC, _ = shade_points(img, rs, RP, RQ, lib, Ls, state)
        cosg = np.abs(D[m][:, 1]) / np.sqrt((D[m] ** 2).sum(-1))
        R = 0.03 + 0.25 * (1 - cosg) ** 5
        C[m] = C[m] * (1 - 0.5 * R[:, None]); RF[m] = RC * R[:, None]
    return sid, P, C, EM, RF


def reduce(C, sid, EM, RF):
    """chaque pixel de la scène pris sur ses SS x SS points : là où ils font deux groupes nets (un bord), la couleur du groupe qui
    en tient au moins 55 % ; sinon leur moyenne (sans grain). Les points hors de la porte laissés de côté (assets/street.js
    découpe ce bord)"""
    H, W = ARC[3], ARC[2]
    c = C.reshape(H, SS, W, SS, 3).transpose(0, 2, 1, 3, 4).reshape(H, W, SS * SS, 3)
    s = sid.reshape(H, SS, W, SS).transpose(0, 2, 1, 3).reshape(H, W, SS * SS)
    inn = s > 0
    c = np.where(inn[..., None], c, (c * inn[..., None]).sum(2, keepdims=True) / np.maximum(inn.sum(2), 1)[..., None, None])
    mean = c.mean(2)
    lum = c @ LUM
    thr = lum.mean(2, keepdims=True)
    for _ in range(4):
        g = lum > thr
        n1 = g.sum(2); n0 = SS * SS - n1
        m1 = (lum * g).sum(2) / np.maximum(n1, 1); m0 = (lum * ~g).sum(2) / np.maximum(n0, 1)
        thr = np.where((n1 > 0) & (n0 > 0), (m0 + m1) / 2, thr[..., 0])[..., None]
    g = lum > thr
    n1 = g.sum(2); n0 = SS * SS - n1
    c1 = (c * g[..., None]).sum(2) / np.maximum(n1, 1)[..., None]
    c0 = (c * ~g[..., None]).sum(2) / np.maximum(n0, 1)[..., None]
    gap = np.abs(c1 - c0).max(-1)
    maj = np.where((n1 >= n0)[..., None], c1, c0)
    share = np.maximum(n1, n0) / (SS * SS)
    out = np.where(((gap > 14) & (share >= 0.55))[..., None], maj, mean)
    out = out + RF.reshape(H, SS, W, SS, 3).mean((1, 3))                  # (les reflets du sol, flous : leur moyenne, jamais de grain)
    ids = np.unique(s)
    cnt = np.stack([(s == k).sum(2) for k in ids], -1)
    surf = ids[cnt.argmax(-1)]
    em = EM.reshape(H, SS, W, SS).transpose(0, 2, 1, 3).reshape(H, W, SS * SS).mean(2)
    return out, surf, inn.mean(2), em


def segment(p0, p1):
    """les pixels d'un segment du canevas (d'un pixel de large, sans trou)"""
    (x0, y0), (x1, y1) = p0, p1
    n = int(np.ceil(max(abs(x1 - x0), abs(y1 - y0)))) + 1
    k = np.linspace(0, 1, n)
    return np.floor(y0 + k * (y1 - y0)).astype(int), np.floor(x0 + k * (x1 - x0)).astype(int)


def floor_px(t, s):
    x, y = proj_room(t, Y_FL, s)
    return x - ARC[0], y - ARC[1]


def _gap(t0, t1, y):
    """l'écart, en pixels et en travers, entre les joints t0 et t1 du sol vers la rangée y du canevas"""
    Z = F * -Y_FL / (y + ARC[1] - VY) if y + ARC[1] > VY + 1 else 1e3
    s0 = (Z - O_Z + t0 * ST) / CT
    a, b = floor_px(t0, s0), floor_px(t0, s0 + 1.0)
    c = floor_px(t1, (Z - O_Z + t1 * ST) / CT)
    d = np.subtract(b, a); e = np.subtract(c, a)
    return abs(d[0] * e[1] - d[1] * e[0]) / max(np.hypot(*d), 1e-6)


def lines(out, surf):
    """nets, d'un pixel : les joints entre les planches (le long de l'axe, vers son point de fuite) et les bouts des lames (en
    travers), plus pâles là où ils se serrent (moins de 2 à 4 pixels entre deux joints) ; les joints des dalles du plafond"""
    H, W = ARC[3], ARC[2]
    fl = surf == S_FLOOR
    if fl.any():
        ts = [hit_t(ARC[0] + c, S_END) for c in (0, W)] + [hit_t(ARC[0] + c, -1.0) for c in (0, W)]
        S0 = -2.0
        fade = lambda d: np.clip((d - 2.0) / 2.0, 0, 1)
        for n in range(int(np.floor(min(ts) / PLANK)) - 1, int(np.ceil(max(ts) / PLANK)) + 2):
            t0, t1 = n * PLANK, (n + 1) * PLANK
            a, b = floor_px(t0, S0), floor_px(t0, S_END)
            rr, cc = segment(a, b)
            for r_, c_ in zip(rr, cc):
                if not (0 <= r_ < H and 0 <= c_ < W and fl[r_, c_]): continue
                k = GROOVE_K * fade(_gap(t0, t1, r_ + 0.5))
                out[r_, c_] *= 1 - k
            # (les bouts des lames de cette planche : de travers, d'un joint à l'autre)
            _, _, blen, off = plank(np.array(t0 + 0.5 * PLANK), np.array(0.0))
            for j in range(int(np.floor((S0 + off) / blen)), int(np.ceil((S_END + off) / blen)) + 1):
                sj = j * blen - off
                if not S0 < sj < S_END: continue
                p, q = floor_px(t0, sj), floor_px(t1, sj)
                k = JOINT_K * fade(_gap(t0, t1, (p[1] + q[1]) / 2))
                rr, cc = segment(p, q)
                for r_, c_ in list(zip(rr, cc))[1:-1]:
                    if 0 <= r_ < H and 0 <= c_ < W and fl[r_, c_]: out[r_, c_] *= 1 - k
    for n in range(1, 12):
        sn = S_END - n * CEIL_PANEL
        for c in range(W):
            tt = hit_t(ARC[0] + c + 0.5, sn)
            X, Z = to_world(tt, sn)
            y = VY - F * Y_C / Z - ARC[1]; r = int(np.floor(y))
            if 0 <= r < H and surf[r, c] == S_CEIL: out[r, c] *= 0.8
    return out


def post_edge(out, surf):
    """le montant : l'arête du tableau du fond prise dans la lumière de la salle, et l'ombre de contact à droite de lui"""
    xin = F * (X_F + REVEAL) / Z_FAR + VX - ARC[0]
    c = int(np.floor(xin))
    rev = surf == S_REVEAL
    room = (surf >= S_CEIL)
    for x, k in ((c, 0.62), (c + 1, 0.8), (c + 2, 0.92)):
        out[:, x] = np.where(room[:, x, None], out[:, x] * k, out[:, x])
    out[:, c - 1] = np.where(rev[:, c - 1, None], np.array(ARRIS_C, float), out[:, c - 1])
    return out


def old_stats():
    data = subprocess.run(['git', 'show', f'{BEFORE}:assets/arcade_interior.webp'], cwd=ROOT, capture_output=True, check=True).stdout
    o = np.asarray(Image.open(io.BytesIO(data)).convert('RGB')).astype(float).reshape(-1, 3)
    return o.mean(0), o.std(0)


def grade(res):
    """à la nuit de la rue : l'équilibre de ses canaux à mi-chemin (GRADE) de celui de l'ancienne salle (BEFORE, déjà dans la
    lumière de la rue), mesuré une fois sur ce qu'on voyait de la salle allumée (GRADE_MN, avant que son mur du bout ne soit
    refait : la même mise à la nuit pour tout) ; ce qui luit (écrans, enseigne, tube, vitrine) moins (ACC_GRADE) ; un peu moins
    saturée (SAT), ses lumières gardées. Le montant (la façade) n'y est pas"""
    mo, so = old_stats()
    out, surf, a, em = res['lit']
    mn = np.array(GRADE_MN)
    for st, (o, sf, aa, e) in res.items():
        acc = np.clip(np.maximum(e, (o.max(-1) - 170) / 60), 0, 1)[..., None]
        k = GRADE * (1 - acc) + ACC_GRADE * acc
        g = o * (1 + k * (mo / mn - 1))
        l = (g @ LUM)[..., None]
        g = l + (g - l) * (SAT + (1 - SAT) * acc)
        res[st] = (np.where((sf >= S_CEIL)[..., None], g, o), sf, aa, e)
    return res


def front_quad(u0, v0, u1, v1, vb, s):
    """une boîte de l'image (colonnes u, rangées v ; vb : la rangée posée au sol) sur le plan s de la salle : ses quatre coins
    dans le canevas de la porte (haut gauche, haut droit, bas droit, bas gauche)"""
    pts = []
    for u, v in ((u0, v0), (u1, v0), (u1, v1), (u0, v1)):
        x, y = proj_room(T_L + u / K, Y_FL + (vb - v) / K, s)
        pts.append([round(float(x - ARC[0]), 2), round(float(y - ARC[1]), 2)])
    return pts


def pins():
    """où le modèle met, dans le canevas de la porte, ce que assets/street.js anime"""
    xin = float(np.ceil(F * (X_F + REVEAL) / Z_FAR + VX - ARC[0]))
    sc, sw = S_END - BOXES[1][5], S_END
    def cut(q):                                                            # (à droite du tableau du montant : ce qu'on en voit)
        for p in q: p[0] = max(p[0], xin)
        return q
    def rect(q):                                                           # (de face ou presque : sa boîte, au pixel)
        xs, ys = [p[0] for p in q], [p[1] for p in q]
        x0, y0, x1, y1 = round(min(xs)), round(min(ys)), round(max(xs)), round(max(ys))
        return [x0, y0, x1 - x0, y1 - y0]
    def whole(q):                                                          # (au pixel : ses colonnes, ses rangées)
        return [[float(round(x)), round(y, 2)] for x, y in q]
    return {'scr': [cut(front_quad(*a, FOOT, sc)) for a in SCREENS], 'sign': cut(front_quad(*SIGN, FOOT, sw)),
            'claw': cut(front_quad(*CLAW_GLASS, BOXES[0][4], S_END - BOXES[0][5])),
            'marq': [cut(front_quad(*m, FOOT, sc)) for m in MARQUEES], 'box': rect(front_quad(*FUSEBOX, FOOT, sw)),
            'disp': whole(front_quad(*DISPLAY, FOOT, sw)), 'exit': rect(front_quad(*EXIT, FOOT, sw))}


def build(img):
    res = {}
    for state in ('lit', 'closed'):
        sid, P, C, EM, RF = render(img, state)
        out, surf, a, em = reduce(C, sid, EM, RF)
        out = lines(out, surf)
        out = wall_joints(out, surf)
        out = post_edge(out, surf)
        res[state] = (out, surf, a, em)
    res = grade(res)
    pn = pins()
    x, y, w, h = pn['exit']                                                # (fermée, la sortie de secours reste allumée)
    o = res['closed'][0]; o[y:y + h, x:x + w] = EXIT_C[0]; o[y + 1:y + h - 1, x + 1:x + w - 1] = EXIT_C[1]
    o[y + 1:y + h - 1, x + 2:x + 3] = EXIT_C[2]
    return res, pn


def unlit_zone(lit):
    """la rue sans courant sous la porte (street_unlit.webp : la coupure de courant, et ce sur quoi la nuit rouge lit la lumière de
    la salle) : la salle elle-même, éteinte, à la place du rideau de fer peint (ses lames feraient des traits rouges dans la nuit
    rouge) ; de la tête au bord du sol de la porte, les pixels dont le centre y est ; le reste du cadre de la porte (ARC) repris au
    commit BEFORE, hors de ce cadre le fichier tel qu'il est (ce que d'autres outils y ont fait reste)"""
    data = subprocess.run(['git', 'show', f'{BEFORE}:assets/street_unlit.webp'], cwd=ROOT, capture_output=True, check=True).stdout
    B = np.asarray(Image.open(io.BytesIO(data)).convert('RGBA')).astype(float)
    U = np.asarray(Image.open(A('street_unlit.webp')).convert('RGBA')).astype(float).copy()
    U[ARC[1]:ARC[1] + ARC[3], ARC[0]:ARC[0] + ARC[2]] = B[ARC[1]:ARC[1] + ARC[3], ARC[0]:ARC[0] + ARC[2]]
    k, c = UNLIT
    for lx in range(ARC[2]):
        x = lx + 0.5
        top = TOP[0] + TOP[1] * x / ARC[2]; bot = BOT[0] + BOT[1] * x / ARC[2]
        fl = bot - THR * (bot - top) / (BOT[0] - TOP[0])
        for ly in range(int(np.ceil(top - 0.5)), min(int(np.floor(fl - 0.5)) + 1, ARC[3])):
            U[ARC[1] + ly, ARC[0] + lx, :3] = lit[ly, lx] * k + np.array(c)
    buf = io.BytesIO()
    Image.fromarray(np.clip(np.round(U), 0, 255).astype(np.uint8), 'RGBA').save(buf, 'WEBP', lossless=True, quality=100, method=6, exact=True)
    return buf.getvalue()


def ask():
    """la matière du mur du bout demandée au modèle d'image (la clé d'OpenRouter dans ~/.config/openrouter/key ; environ
    0,25 $), de son seul texte (tools/src/edits/arcback_prompt.txt) ; sa réponse arcback_draft.webp (le mur est fait de la
    réponse gardée, jamais d'un nouvel appel)"""
    import base64
    import urllib.request
    key = open(os.path.expanduser('~/.config/openrouter/key')).read().strip()
    content = [{"type": "text", "text": open(os.path.join(EDITS, 'arcback_prompt.txt'), encoding='utf-8').read().strip()}]
    body = {"model": MODEL, "modalities": ["image", "text"], "usage": {"include": True}, "messages": [{"role": "user", "content": content}]}
    req = urllib.request.Request('https://openrouter.ai/api/v1/chat/completions', data=json.dumps(body).encode(),
                                 headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'})
    d = json.loads(urllib.request.urlopen(req, timeout=900).read())
    url = d['choices'][0]['message']['images'][0]['image_url']['url']
    Image.open(io.BytesIO(base64.b64decode(url.split(',', 1)[1]))).save(WALL_DRAFT, 'WEBP', lossless=True, quality=100, method=6)
    print('arcback_draft.webp', Image.open(WALL_DRAFT).size, '; coût', d.get('usage', {}).get('cost'), '$')


def main():
    if '--ask' in sys.argv:
        ask()
        return
    theta = float(sys.argv[sys.argv.index('--theta') + 1]) if '--theta' in sys.argv else THETA
    configure(theta)
    img = smooth_src()
    res, pn = build(img)
    pv = sys.argv[sys.argv.index('--preview') + 1] if '--preview' in sys.argv else None
    if pv:
        for state, (out, surf, a, em) in res.items():
            rgba = np.concatenate([out, a[..., None] * 255], -1)
            Image.fromarray(np.clip(np.round(rgba), 0, 255).astype(np.uint8), 'RGBA').save(pv.replace('.png', '_' + state + '.png'))
        print(json.dumps(pn))
        return
    tex_ = np.concatenate([res['lit'][0], res['closed'][0]], 0)
    old = open(A(OUT), 'rb').read() if os.path.exists(A(OUT)) else b''
    buf = io.BytesIO()
    Image.fromarray(np.clip(np.round(tex_), 0, 255).astype(np.uint8), 'RGB').save(buf, 'WEBP', lossless=True, quality=100, method=6, exact=True)
    open(A(OUT), 'wb').write(buf.getvalue())
    js = open(A('street.js'), encoding='utf-8').read()
    js, n1 = re.subn(r"const ARC_PINS = \{.*?\};", 'const ARC_PINS = ' + json.dumps(pn, separators=(', ', ': ')) + ';', js)
    bump = 1 if buf.getvalue() != old else 0                                # (sa version : une de plus si la texture a changé)
    js, n2 = re.subn(r"assets/%s\?v=(\d+)" % re.escape(OUT), lambda m: 'assets/%s?v=%d' % (OUT, int(m.group(1)) + bump), js)
    assert n1 == 1 and n2 == 1, 'street.js : ARC_PINS ou la texture de la salle introuvable'
    un = unlit_zone(res['lit'][0]); old = open(A('street_unlit.webp'), 'rb').read()   # (la rue sans courant sous la porte, et sa version)
    if un != old:
        open(A('street_unlit.webp'), 'wb').write(un)
        js, n3 = re.subn(r"assets/street_unlit\.webp\?v=(\d+)", lambda m: 'assets/street_unlit.webp?v=%d' % (int(m.group(1)) + 1), js)
        assert n3 == 1, 'street.js : street_unlit introuvable'
    open(A('street.js'), 'w', encoding='utf-8').write(js)
    sc = S_END - BOXES[1][5]
    X, Z = to_world(T_L + 266 / K, sc)
    print('la porte : façade X %.3f m (l\'œil à %.2f m du trottoir), montant du fond Z %.3f m, bord droit de l\'image Z %.3f m, '
          'linteau %.3f m, sol de la salle %.3f m au-dessus du trottoir' % (X_F, EYE, Z_FAR, Z_EDGE, Y_HEAD + EYE, Y_FL + EYE))
    print('la salle : tournée de %.1f° (point de fuite de son axe x %.0f), mur du bout à %.2f m du montant le long de l\'axe, plafond '
          '%.2f m, image %.1f px/m (%.2f x %.2f m), son bord gauche à t %.3f m ; la première borne : sa face à %.2f m de l\'œil, '
          '%.1f px/m, %.0f px de haut' % (theta, VPA, S_END, Y_C - Y_FL, K, 667 / K, 2000 / K, T_L, np.hypot(X, Z), F / Z, CAB_M * F / Z))
    lo = res['lit'][0][(res['lit'][1] >= S_CEIL) & (res['lit'][2] > 0.99)]
    print('sa lumière (moyenne de ce qu\'on voit, allumée) :', lo.mean(0).round(1))
    print('ARC_PINS', json.dumps(pn))


if __name__ == '__main__':
    main()
