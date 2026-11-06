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
  pas deux matières). Pas de trait sombre repris de la planche (ni contour) : ses traits sont posés pixel par pixel là où la
  planche les dessine (FACE ; le propriétaire voulait un peu plus de détail de face qu'un pixel par œil) : de face, ses yeux au
  centre des verres de ses lunettes (EYES ; un pixel ouverts, deux fermés : SHUT), la monture de part et d'autre de chaque œil
  et le pont plus clair entre eux, l'ombre de ses cheveux sur le haut du visage, celle du nez du côté opposé à la lampe, le
  rose des joues, la bouche entre les yeux et sous eux (MOUTH : deux pixels de lèvres ; un pixel sombre un peu ouverte, deux
  ouverte, sur deux rangées grande ouverte) ; le même visage dessiné deux fois (SAME_FACE : le repos et le sourire, le
  boulier) a ses traits aux mêmes pixels ; de profil, l'œil à deux pixels du bout du visage, la branche des lunettes derrière
  lui (SIDE). Ces pixels gardent leur famille, sans grain.
- Lumière et grain : allumée, la lumière de la boutique (sa lampe à incandescence, plus chaude que le jour des planches : LAMP ;
  puis l'étalonnage de la maquette, celui de la pièce) ; ses clairs ramenés sous la pièce
  autour d'elle + 15 % (P95 : le p95 de la clarté de la pièce allumée là où elle passe) ; puis, toutes ses images ensemble
  (tools/regrain.py : ses fonctions), FAMILIES familles de tons fixes d'une image à l'autre, chaque pixel à la sienne contre ses
  quatre voisins (peu de pixels seuls), un grain fin baké de 1 à 3 niveaux (Bayer 4 x 4, ancré à elle) ; ses traits gardés.
  Éteinte (la coupure de courant, boutique ouverte) : chaque famille au sombre de la pièce éteinte selon sa clarté, à sa
  palette, le même grain plus léger.
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
EYES = (0.50, 0.82, 80, 0.15, 0.62)  # (les yeux : la bande de la tête où ils sont, du haut ; plus sombre que tant : les verres et
                                     # les yeux ; de face, de tant à tant de demi-largeurs de tête du nez)
EYES_SIDE = (0.50, 0.72, 95)         # (de profil : la bande, le sombre ; la monture y est plus claire)
EYE_RGB, SHUT = (38.0, 22.0, 18.0), ('s1', 's3', 'l0')   # (ouverts ; les images aux yeux fermés)
SEAT_REF = 's0'                      # (assise : les images posées par leur comptoir dessiné, le buste de celle-ci au milieu)
FACE = dict(rim=(128.0, 84.0, 64.0), shut=(72.0, 42.0, 34.0), lip=(198.0, 84.0, 78.0), open=(100.0, 36.0, 34.0),
            cheek=(236.0, 142.0, 128.0), shade=0.9)   # (de face, à la demande du propriétaire : la monture des lunettes, les yeux
                                     # fermés, les lèvres, la bouche ouverte, le rose des joues ; l'ombre sur la peau (le nez, sous
                                     # les cheveux), de tant)
MOUTH = (0.12, 0.98, 15, 40, 70)     # (la bouche dessinée : de tant de hauteurs de tête sous les yeux à tant du haut de la tête,
                                     # entre les yeux ; un peu ouverte (un pixel sombre), ouverte (deux), grande ouverte (deux, sur
                                     # deux rangées) dès tant de px sombres de la planche)
SIDE = (2, 2)                        # (de profil : l'œil à tant de pixels du bout du visage ; la branche des lunettes, tant de px)
SAME_FACE = (('s0', 's1'), ('a0', 'a1'))   # (le même visage dessiné deux fois : ses traits aux mêmes pixels)
LAMP = np.array([1.0, 0.93, 0.80])   # (sous la lampe à incandescence, juste au-dessus du comptoir : plus chaude que le jour des planches)
P95 = 1.15                           # (ses clairs : sous le p95 de la pièce allumée autour d'elle, + 15 %)
FAMILIES = 24
GRAIN = dict(scale=0.04, cap=2.5, iters=6, tempo=2.0, tempo_de=0.02, grain_k=0.2, dither=1.6, merge=0.015, knee=60.0)
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


def eyes(f, hh_out):
    """ses yeux (de face : deux ; de profil : un) : au centre de ses verres, le poids des sombres de la bande des yeux (les verres,
    leurs montures, les yeux ouverts ou fermés ; plus sombre, plus lourd) de part et d'autre du nez, ou tout devant le profil"""
    c, m, h = f['rgb'], f['m'], f['head']
    L = c @ I.LUM
    Y0, Y1, Lm = EYES[:3] if f['kind'] == 'seat' else EYES_SIDE
    y0, y1 = int(h['crown'] + Y0 * hh_out), int(h['crown'] + Y1 * hh_out)
    dark = np.zeros(m.shape, bool); dark[y0:y1] = m[y0:y1] & (L[y0:y1] < Lm)
    ys, xs = np.nonzero(dark)
    dx = xs + 0.5 - h['hx']
    wt = Lm - L[ys, xs]
    if f['kind'] == 'seat':
        out = []
        for side in ((dx < -EYES[3] * h['R']) & (dx > -EYES[4] * h['R']), (dx > EYES[3] * h['R']) & (dx < EYES[4] * h['R'])):
            if side.sum() >= 5: out.append((float(np.average(xs[side], weights=wt[side])) + 0.5, float(np.average(ys[side], weights=wt[side])) + 0.5))
        return out
    front = (dx > 0) & (xs >= np.percentile(xs[dx > 0], 70)) if (dx > 0).sum() >= 10 else None   # (de profil : le verre, tout devant)
    if front is None: return []
    return [(float(np.average(xs[front], weights=wt[front])) + 0.5, float(np.average(ys[front], weights=wt[front])) + 0.5)]


def mouth(f, hh_out, E):
    """sa bouche dessinée (de face) : sous ses yeux, entre eux (E : leurs centres, px de la planche ; pas la manche ni la main
    contre sa joue), ce qui est rouge et plus sombre que la peau (les lèvres, la bouche ouverte) ; son milieu, sa largeur,
    combien elle est ouverte (ses px sombres)"""
    c, m, h = f['rgb'], f['m'], f['head']
    L = c @ I.LUM
    if len(E) != 2: return None
    y0, y1 = int(max(E[0][1], E[1][1]) + MOUTH[0] * hh_out), int(h['crown'] + MOUTH[1] * hh_out)
    x0, x1 = int(min(E[0][0], E[1][0])), int(max(E[0][0], E[1][0])) + 1
    red = np.zeros(m.shape, bool)
    red[y0:y1, x0:x1] = (m & (c[..., 0] - c[..., 1] > 45) & (L < 175))[y0:y1, x0:x1]
    if red.sum() < 8: return None
    ys, xs = np.nonzero(red)
    return float(xs.mean()) + 0.5, float(ys.mean()) + 0.5, float(np.ptp(xs) + 1), int((red & (L < 95)).sum())


def face(c, E, Mo, kind, shut):
    """ses traits, au pixel près, là où la planche les dessine (E : ses yeux, Mo : sa bouche, dans la case) : de face, l'ombre de
    ses cheveux sur le haut de son visage, ses lunettes (la monture de part et d'autre de chaque œil, le pont plus clair entre
    eux), ses yeux (un pixel ouverts, deux fermés), l'ombre du nez du côté opposé à la lampe, le rose des joues, la bouche (deux
    pixels de lèvres, sombre ouverte, sur deux rangées grande ouverte) ; de profil, l'œil et le verre devant lui. Rend les
    pixels posés (gardés tels quels ensuite)"""
    rgb, a = c[..., :3], c[..., 3] > 0
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    skin = a & (r > 150) & (r - b > 45) & (g - b > 15) & (r - g > 25)
    grey = a & (np.abs(r - g) < 16) & (np.abs(g - b) < 18) & (r > 90) & (r < 225)
    H, W = a.shape
    lk = np.zeros((H, W), bool)
    def put(j, i, col, need=skin):
        if 0 <= i < H and 0 <= j < W and need[i, j] and not lk[i, j]:
            rgb[i, j] = col; lk[i, j] = True
    sh = lambda j, i: rgb[i, j] * FACE['shade'] if 0 <= i < H and 0 <= j < W else 0
    mix = lambda j, i, col: 0.5 * rgb[i, j] + 0.5 * np.array(col) if 0 <= i < H and 0 <= j < W else 0
    E = sorted(E)
    if kind == 'side':                                                     # (de profil : l'œil à deux pixels du bout de son visage,
        for _, ey in E:                                                    #  à la rangée du verre ; la branche des lunettes derrière)
            js = np.nonzero(skin[ey])[0]
            if not len(js): continue
            ex = int(js.max()) - SIDE[0]
            put(ex, ey, EYE_RGB)
            for d in range(1, SIDE[1] + 1): put(ex - d, ey, FACE['rim'])
        return lk
    if len(E) != 2:
        for ex, ey in E: put(ex, ey, FACE['shut'] if shut else EYE_RGB, a)
        return lk
    (j1, i1), (j2, i2) = E
    for (ex, ey), side in zip(E, (-1, 1)):                                 # (les yeux)
        if shut: put(ex, ey, FACE['shut']); put(ex - side, ey, FACE['shut'])
        else: put(ex, ey, EYE_RGB, a)
    for (ex, ey), side in zip(E, (-1, 1)):                                 # (la monture, le pont)
        put(ex + side, ey, FACE['rim']); put(ex - side, ey, FACE['rim'])
    if i1 == i2:
        for j in range(j1 + 2, j2 - 1): put(j, i1, sh(j, i1))
    top = min(i1, i2)
    for i in range(1, top):                                                # (l'ombre des cheveux)
        for j in range(j1 - 2, j2 + 3):
            if 0 <= j < W and skin[i, j] and grey[i - 1, j]: put(j, i, sh(j, i))
    if (Mo[1] if Mo else 99) - max(i1, i2) >= 3:                           # (le nez, du côté de l'ombre, s'il a sa rangée)
        put((j1 + j2) // 2 + 1, max(i1, i2) + 2, sh((j1 + j2) // 2 + 1, max(i1, i2) + 2))
    put(j1 - 1, i1 + 2, mix(j1 - 1, i1 + 2, FACE['cheek'])); put(j2 + 1, i2 + 2, mix(j2 + 1, i2 + 2, FACE['cheek']))
    if Mo:                                                                 # (la bouche, au pixel du milieu dessiné et celui vers
        mx, my, fx, dark = Mo                                              #  lequel il penche)
        js = [mx] if MOUTH[2] <= dark < MOUTH[3] else [mx, mx + (1 if fx >= 0.5 else -1)]
        for j in js: put(j, my, FACE['open'] if dark >= MOUTH[2] else FACE['lip'])
        if dark >= MOUTH[4]:
            for j in js: put(j, my + 1, FACE['lip'])
    return lk


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


def regrain(cells, locks, goal):
    """toutes ses images, allumées, ensemble : les clairs sous goal (au-dessus de GRAIN['knee'], chaque couleur sur sa teinte),
    FAMILIES familles (OKLab), chaque pixel à la sienne contre ses voisins (Potts, l'image d'avant du même mouvement en mémoire),
    un grain fin baké (Bayer, ancré à l'ancre de l'image) ; ses yeux gardés. Rend les images et, pour chacune, sa famille par
    pixel ; et les familles"""
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
    C = RG.families(np.concatenate([X[k][M[k]] for k in keys]), FAMILIES, P['merge'])
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
        lab = RG.assign(X[k], M[k], C, P['scale'], P['iters'], prior, prior_ok, P['tempo'], P['cap'], locks[k])
        prev[mv] = k
        h, w = M[k].shape
        d = RG.bayer(h, w, AX, AY)
        g = np.clip(np.round(P['grain_k'] * (RG.luma(G[k]) - Lb[lab]) + (d - 0.5) * P['dither']), -A[lab], A[lab])
        g[locks[k]] = 0
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
    cells, locks, info, feats = {}, {}, {}, {}
    for k, f in F.items():
        s = s_s if f['kind'] == 'seat' else s_w
        ys, xs = np.nonzero(f['m'])
        AX = int(np.ceil((f['ax'] - xs.min()) * s)) + 1; AY = int(np.ceil((f['ay'] - ys.min()) * s)) + 1
        W = AX + int(np.ceil((xs.max() + 1 - f['ax']) * s)) + 1; H = AY + (3 if f['kind'] == 'seat' else 0)
        c = reduce(f, s, AX, AY, W, H)
        if f['kind'] == 'seat':                                             # (sous le haut du comptoir : sa dernière rangée, trois fois,
            for r in range(AY, H): c[r] = c[AY - 1]                         # que son souffle ne découvre rien)
        hh_out = HEAD[f['kind']] * kh
        E = [to_cell(f, ex, ey, s, AX, AY) for ex, ey in (eyes(f, hh_out) if f['kind'] != 'back' else [])]
        Mo = mouth(f, hh_out, eyes(f, hh_out)) if f['kind'] == 'seat' else None
        if Mo: Mo = to_cell(f, Mo[0], Mo[1], s, AX, AY) + ((AX + (Mo[0] - f['ax']) * s) % 1, Mo[3])
        feats[k] = [[(j - AX, i - AY) for j, i in E], (Mo[0] - AX, Mo[1] - AY) + Mo[2:] if Mo else None]
        mv = 'seat' if f['kind'] == 'seat' else f['kind']
        cells[k] = [c, AX, AY, mv]
        info[k] = dict(h=int(np.ptp(np.nonzero(c[..., 3].any(1))[0]) + 1), head=round(hh_out * s, 1))
        print('%s : %d x %d, ancre (%d, %d), %.3f px de la scène par px de la planche, la tête %.1f px' % (k, W, H, AX, AY, s, hh_out * s))
    for a_, b_ in SAME_FACE:                                               # (le même visage : les traits de l'un sur l'autre, à un
        Ea, Eb = feats[a_][0], feats[b_][0]                                #  pixel près)
        if len(Ea) == len(Eb) and all(abs(p[0] - q[0]) <= 1 and abs(p[1] - q[1]) <= 1 for p, q in zip(sorted(Ea), sorted(Eb))):
            feats[b_][0] = list(Ea)
            if feats[a_][1] and feats[b_][1] and abs(feats[a_][1][0] - feats[b_][1][0]) <= 1 and abs(feats[a_][1][1] - feats[b_][1][1]) <= 1:
                feats[b_][1] = feats[a_][1][:3] + feats[b_][1][3:]
    for k, (c, AX, AY, mv) in cells.items():
        E = [(x + AX, y + AY) for x, y in feats[k][0]]
        Mo = feats[k][1]; Mo = (Mo[0] + AX, Mo[1] + AY) + Mo[2:] if Mo else None
        locks[k] = face(c, E, Mo, F[k]['kind'], k in SHUT)
        print('%s : les traits %s, la bouche %s, %d px posés' % (k, E, Mo and (Mo[0], Mo[1], round(Mo[2], 2), Mo[3]), locks[k].sum()))
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
    LIT, LAB, base, slope = regrain(lit, locks, goal)
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
