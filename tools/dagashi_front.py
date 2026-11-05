#!/usr/bin/env python3
"""Le dagashi-ya (sous la façade de Kirua, à gauche du kiosque à tabac) : par sa porte ouverte, une vraie boutique.

    python3 tools/dagashi_front.py      (il reprend sa zone au commit BEFORE à chaque fois, on peut donc le relancer)

Sa devanture est sur la façade de Kirua, qui court vers le point de fuite des maisons de gauche VP (mesuré sur la
devanture même : l'enseigne, le linteau, le seuil y courent, à moins d'un pixel sur sa largeur). Deux portes coulissantes :
celle de gauche fermée (sa vitre, ses marchandises derrière, son panneau bas en bois), celle de droite glissée derrière
elle, et par l'ouverture (x XA..XB, le montant du fond juste après) la boutique éclairée. Le peintre l'avait peinte comme
une affiche collée dans l'ouverture : ses étagères, son tube, le pied de ses meubles et le sol sur les rayons de la
façade, cisaillés comme elle.

Ici c'est une pièce, vue par l'œil de la rue (une perspective à un point, VP au centre : ce qui longe la rue court vers
VP, ce qui entre dans la boutique est horizontal, ce qui est vertical d'aplomb) :

- le mur du fond, de face (il fait face à la rue qui descend : ses horizontales horizontales, ses verticales d'aplomb),
  un peu au-delà du montant du fond (son plan rejoindrait celui de la façade en x XW, derrière le montant) : les
  pixels du peintre, chacun dans sa colonne ; chaque rayon de sa peinture devient l'horizontale qu'il a à la dernière
  colonne du mur XR (là, sa peinture telle quelle ; plus près, ses rangées resserrées de (VP_x - x) / (VP_x - XR) autour
  de l'horizon, pas plus : moins de 8 % à la colonne la plus proche) ; ce qui dépasse en haut et en bas passe derrière le
  plafond et le sol ; chaque bord net de sa peinture (les planches, les bocaux, le dessus du meuble) suivi colonne par
  colonne (EDGE_*) et posé exactement sur sa rangée, sans marche, les rangées entre deux bords réparties entre eux
  (aucune doublée, celles en trop sautées là où sa peinture est la plus unie) ;
- le plafond, vu d'en dessous, entre le linteau (un rayon) et le haut du mur (une horizontale) : un coin plus large
  vers le montant proche ; le grain du haut sombre de la pièce du peintre (CEIL_SRC, chaque pixel rapporté à ses
  voisins : GRAIN), répété en miroir, à ses tons : sombre vers la porte, plus clair près du tube (CEIL, en bandes) ;
- le tube du peintre au plafond, de travers à la rue (horizontal, rangée TUBE_ROW), redessiné net (sa boîte, chaque
  rangée de la couleur médiane de la sienne, ses bouts à lui) ; allumée, sa lueur autour de lui en trois marches
  (GLOW) ;
- le sol, entre le pied du mur (une horizontale) et le seuil du peintre : le grain de son sol (chaque colonne de son
  sol ramenée à FLOOR_ROWS rangées, chaque pixel rapporté à ses voisins), répété en miroir ; allumé, à la flaque de
  lumière qu'il y avait mise (près du seuil, au milieu de l'ouverture), posée à plat sur lui (en perspective : ses
  bords s'aplatissent), en bandes de ses tons à lui (POOL) ; éteint, à ses deux tons éteints, le plus clair vers le
  seuil (FLOOR_OFF) ; le pied du mur assombri contre lui (FOOT) ;
- le tableau du fond, la face intérieure du montant (de face aussi, J colonnes avant lui : le bois du montant, éclairé
  par la pièce, plus vers elle et vers le sol clair : JAMB) ; la sous-face du linteau, une rangée sombre (avec ce que la
  pièce du peintre avait au-dessus d'elle) ; sous le montant, le seuil du peintre.

Allumée, la pièce garde la lumière du peintre (ses couleurs mêmes), un peu plus sombre vers le bas du mur (FALL), et la
ligne du plafond contre le mur (JUNCTION). La vitre de la porte de gauche reste où elle est (ses marchandises contre le
verre, comme une vitrine), mais derrière un verre (GLASS_DIM) et éclairée de côté, par l'ouverture et le tube : plus
sombre vers la gauche et vers le bas (PANE_FALL) ; un reflet en biais, à peine, deux bandes nettes (SHEEN). Éteinte, comme
elle est dans les calques : la même géométrie prise dans les pixels sombres du peintre, le plafond et le sol à leurs
tons éteints.

Dans layer_city_off et street_unlit (les mêmes ici : leur rapport au commit BEFORE gardé), night_far (0) et street_sun
(0) ; écrit assets/win_z7_shop.webp (le comp de la boutique, ce qui change quand elle s'allume) et sa boîte dans
assets/street.js. Il faut git, Pillow, numpy.
"""
import io
import os
import re
import subprocess
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = lambda p: os.path.join(ROOT, 'assets', p)
BEFORE = '4faa10a'                   # (les calques et le comp avant cet outil : sa zone reprise de là à chaque fois)
ZONE = (146, 525, 228, 745)          # x0, y0, x1, y1 : la devanture, cadre compris (à gauche de x 146 rien ne change : la descente du passage)
VP = (700.0, 615.0)                  # le point de fuite de la devanture (mesuré : l'enseigne, le linteau et le seuil y courent)
XA, XB = 181, 224                    # l'ouverture : ses colonnes (la porte de gauche avant, le montant du fond après)
CH, CF, CT = -0.15125, 0.2155, 0.2355   # les rayons de la peinture, y = VP_y + c (VP_x - x) : le linteau (la première
                                     # rangée de la pièce dessous), le pied des étagères (le bord du sol vers elles), le seuil
                                     # (la dernière rangée du sol au-dessus)
XW = 270                             # le plan du mur du fond rejoint celui de la façade à cette colonne (derrière le montant)
J = 5                                # la face intérieure du montant du fond : ses colonnes
XR = XB - J                          # (la dernière colonne du mur : la peinture y reste telle quelle)
UP = 'win_z7_shop'; UP_POS = (105, 505); UP_V = 8   # le comp de la boutique (sa place au commit BEFORE), sa version
LUM = np.array([0.299, 0.587, 0.114])
F_PX, EYE = 1250.0, 1.5              # (la focale de la vue, en pixels, estimée sur les distributeurs voisins (un mètre de large
                                     # chacun), et la hauteur de l'œil : seulement pour la lumière, en mètres)
EDGE_MIN, EDGE_RUN = 8, 4            # un bord de la peinture : un saut de clarté d'au moins tant entre deux rangées, suivi le
                                     # long de son rayon sur tant de colonnes au moins (à deux colonnes près)
CEIL = ((0.35, 'lit'), (0.9, 'mid'), (1e9, 'dark'))   # le plafond : ses tons selon la distance au tube (m), en bandes
TUBE = (197, 217)                    # le tube du peintre : ses colonnes (ses bouts), les rayons de ses bords haut et bas (mesurés) ;
TUBE_RAYS = (-0.1453, -0.1370)       # au plafond, de travers à la rue (horizontal), sa première rangée à TUBE_ROW
TUBE_ROW = 544
GLOW = (0.4, 0.2, 0.08)              # allumée, sa lueur autour de lui (mur et plafond) : la part de sa couleur à 1, 2, 3 pixels
CEIL_ON = {'lit': (118, 58, 52), 'mid': (78, 38, 44), 'dark': (45, 27, 41)}   # (allumée : près du tube, plus loin, vers la porte)
CEIL_OFF = {'lit': (44, 27, 40), 'mid': (40, 25, 39), 'dark': (36, 24, 38)}   # (éteinte)
POOL = ((16.6, 0.25), (0.6, 0.55), (0.7, 0.4, 0.16, 0.05, 0.0), (78, 64, 48, 32, 16))   # allumé, la flaque de lumière sur le
                                     # sol : son centre (le long de la rue, dans la boutique, m), ses rayons, les limites de ses
                                     # bandes (sa part), leurs tons (centiles de clarté des pixels du sol du peintre)
FLOOR_OFF = (0.45, (35, 65))         # éteint : ses deux tons (centiles), le plus clair passé cette part du coin vers le seuil
CEIL_SRC = (181, 196, 6)             # le grain du plafond : le haut sombre de la pièce du peintre (ses colonnes, ses rangées
                                     # sous son linteau), à gauche de son tube
FLOOR_SRC, FLOOR_ROWS = (190, 219), 8   # le grain du sol : les colonnes de son sol, ramenées à tant de rangées
GRAIN = (0.78, 1.28)                 # (le grain : un pixel rapporté à ses voisins, borné)
FOOT = 0.78                          # le pied du mur contre le sol, sa rangée (allumée et éteinte)
JUNCTION = (0.8, 0.9)                # la ligne du plafond contre le mur : sa rangée de plafond, la première du mur (allumée)
FALL = 0.1                           # allumée : le mur un peu plus sombre loin du tube, vers son pied (sa part perdue)
JAMB = ((71, 49, 46), (0.12, 0.3, 0.45))   # la face du montant : le bois du montant du peintre ; allumée, la part de son
                                     # bord éclairé (sa couleur) : loin de la pièce, au milieu, contre elle (et plus bas, vers le
                                     # sol clair)
SOFFIT = 0.8                         # la sous-face du linteau : le bois sombre du montant, plus sombre encore
PANE = (146, 547, 178, 680)          # la vitre de la porte de gauche (x0, y0, x1, y1) : ses marchandises contre le verre
GLASS_DIM = 0.94                     # allumée : derrière ce verre, un peu plus sombre que l'ouverture ; et éclairées de côté,
PANE_FALL = (0.24, 0.12)             # par l'ouverture et le tube : plus sombres vers la gauche, vers le bas (leur part perdue)
SHEEN = ((0.55, 4.0, 3.0), (0.62, 1.5, 6.0))   # le reflet en biais : (sa pente (x par rangée), sa largeur, son ajout) : une
                                     # bande large et faible, une fine un peu plus claire, nettes ; sur la vitre seule
SHEEN_AT = (152, 560)                # (le point où passent leurs milieux)


def load(p, mode='RGBA', at=None):
    data = subprocess.run(['git', 'show', f'{at}:assets/{p}'], cwd=ROOT, capture_output=True, check=True).stdout if at else open(A(p), 'rb').read()
    return np.asarray(Image.open(io.BytesIO(data)).convert(mode)).astype(float)


def save(arr, p, mode):
    Image.fromarray(np.clip(np.round(arr), 0, 255).astype(np.uint8), mode).save(A(p), 'WEBP', lossless=True, quality=100, method=6, exact=True)


def ray(c, x):                                                               # (la ligne à x du rayon c vers VP)
    return VP[1] + c * (VP[0] - x)


def tracks_of(Lm):
    """les bords nets de la peinture dans la pièce (entre son linteau et le pied de ses étagères) : des sauts de clarté entre
    deux rangées, groupés par rayon vers VP ; chacun (son rayon c, son signe, ses points (x, bord))"""
    edges = []
    for x in range(XA, XB - J + 1):
        y0, y1 = int(np.ceil(ray(CH, x))) + 1, int(np.floor(ray(CF, x))) - 1
        Dv = Lm[y0 + 1:y1 + 1, x] - Lm[y0:y1, x]
        for i in range(1, len(Dv) - 1):
            if abs(Dv[i]) >= EDGE_MIN and abs(Dv[i]) >= abs(Dv[i - 1]) and abs(Dv[i]) >= abs(Dv[i + 1]):
                b = y0 + i + 0.5
                edges.append((x, b, np.sign(Dv[i]), abs(Dv[i]), (b - VP[1]) / (VP[0] - x)))
    E = np.array(edges)
    cands = []
    for c in np.arange(E[:, 4].min(), E[:, 4].max(), 0.0004):
        for s in (1, -1):
            sel = {}
            for k, (x, b, sg, m, ce) in enumerate(E):
                d = abs(ray(c, x) - b)
                if sg == s and d <= 0.75 and (x not in sel or d < sel[x][1]): sel[x] = (k, d)
            if len(sel) >= EDGE_RUN: cands.append((sum(E[k, 3] for k, _ in sel.values()), c, s, sel))
    cands.sort(key=lambda t: -t[0])
    used, tracks = set(), []
    for w, c, s, sel in cands:
        ks = [k for k, _ in sel.values() if k not in used]
        if len(ks) < EDGE_RUN: continue
        xs = sorted(E[k, 0] for k in ks); runs, cur = [], [xs[0]]
        for a in xs[1:]:
            if a - cur[-1] <= 2: cur.append(a)
            else: runs.append(cur); cur = [a]
        runs.append(cur); run = max(runs, key=len)
        if len(run) < EDGE_RUN: continue
        ks = [k for k in ks if run[0] <= E[k, 0] <= run[-1]]
        used |= set(ks)
        cc = float(np.mean([(E[k, 1] - VP[1]) / (VP[0] - E[k, 0]) for k in ks]))
        tracks.append((cc, len(ks), {int(E[k, 0]): E[k, 1] for k in ks}, (int(run[0]), int(run[-1]))))
    return tracks


def col_map(x, tracks, Co, Fo, Lm):
    """une colonne du mur : pour chacune de ses rangées, la rangée de la peinture qu'elle montre. Chaque rayon de la peinture
    devient l'horizontale qu'il a à la colonne XR (là, la peinture telle quelle ; ailleurs ses rangées resserrées de
    (VP_x - x) / (VP_x - XR) autour de l'horizon, pas plus) ; des repères (rangée de sortie, rangée de la peinture) : le
    haut et le pied du mur, chaque bord suivi posé sur sa rangée ; monotones, et jamais plus serrés dans la peinture qu'au
    mur (en cas de conflit, le bord le plus court lâché). Entre deux repères, les rangées de la peinture dans l'ordre,
    celles en trop sautées là où elle est la plus unie (là où une rangée ressemble le plus à ses voisines)"""
    half = lambda t: np.round(t - 0.5) + 0.5                                # (une limite entre deux rangées)
    K = (VP[0] - x) / (VP[0] - XR)                                           # (le rayon c au mur : sa rangée à la colonne XR)
    anc = [(half(Co), half(VP[1] + (Co - VP[1]) * K), 1e9), (half(Fo), half(VP[1] + (Fo - VP[1]) * K), 1e9)]
    for cc, n, pts, (xa, xb) in tracks:
        t = half(ray(cc, XR))
        if xa <= x <= xb and half(Co) < t < half(Fo):
            anc.append((t, pts.get(x, half(ray(cc, x))), n))
    anc.sort()
    ok = False
    while not ok:
        ok = True
        for i in range(len(anc) - 1):
            (t0, s0, w0), (t1, s1, w1) = anc[i], anc[i + 1]
            if t1 - t0 < 0.5 or s1 - s0 < t1 - t0:
                anc.pop(i if w0 < w1 else i + 1); ok = False; break
    flat = lambda y: abs(Lm[y, x] - Lm[y - 1, x]) + abs(Lm[y + 1, x] - Lm[y, x])
    out = {}
    for (t0, s0, _), (t1, s1, _) in zip(anc[:-1], anc[1:]):
        ts = list(range(int(t0 + 0.5), int(t1 + 0.5)))                     # (les rangées entre les deux)
        ss = list(range(int(s0 + 0.5), int(s1 + 0.5)))
        drop = sorted(ss, key=lambda y: (flat(y), abs(y - (ss[0] + ss[-1]) / 2)))[:len(ss) - len(ts)]
        ss = [y for y in ss if y not in drop]
        out.update(zip(ts, ss))
    return out


def tile(P, i, j):                                                           # (un motif répété en miroir : son pixel (i, j))
    h, w = P.shape[:2]; i %= 2 * h; j %= 2 * w
    return P[i if i < h else 2 * h - 1 - i, j if j < w else 2 * w - 1 - j]


def grain(P):                                                                # (le grain d'un motif : chaque pixel rapporté à
    Pp = np.pad(P, ((1, 1), (1, 1), (0, 0)), mode='reflect')               # la moyenne de ses voisins, borné)
    m = sum(Pp[a:a + P.shape[0], b:b + P.shape[1]] for a in range(3) for b in range(3)) / 9
    return np.clip((P + 1) / (m + 1), GRAIN[0], GRAIN[1])


def main():
    names = (('layer_city_off.webp', 'RGBA'), ('street_unlit.webp', 'RGBA'), ('night_far.webp', 'RGB'), ('street_sun.webp', 'RGB'))
    L = [load(n, m) for n, m in names]; B = [load(n, m, BEFORE) for n, m in names]
    zx0, zy0, zx1, zy1 = ZONE
    for l, b in zip(L, B): l[zy0:zy1, zx0:zx1] = b[zy0:zy1, zx0:zx1]       # (la devanture comme avant)
    H, W = B[0].shape[:2]
    off = B[0][..., :3].copy()
    cp = load(UP + '.webp', 'RGBA', BEFORE); px, py = UP_POS; ch, cw = cp.shape[:2]
    on = off.copy(); al = cp[..., 3:4] / 255
    on[py:py + ch, px:px + cw] = on[py:py + ch, px:px + cw] * (1 - al) + cp[..., :3] * al
    cut = np.clip((B[1][..., :3] + 0.5) / (B[0][..., :3] + 0.5), 0, 1)     # (ce que la coupure de courant ôte ici : rien)
    S = {'on': on, 'off': off}; N = {k: v.copy() for k, v in S.items()}
    lit0 = np.zeros((H, W), bool); lit0[py:py + ch, px:px + cw] = cp[..., 3] > 0   # (ce que le comp allumait)

    # la géométrie : le haut du mur (le linteau au plan du mur), son pied (le seuil au plan du mur) ; la peinture y est
    # redressée colonne par colonne, ses bords sur leurs rangées (col_map)
    Co, Fo = ray(CH, XW), ray(CT, XW)
    tracks = tracks_of(on @ LUM)
    first = lambda r: int(np.round(r - 0.5)) + 1                             # (la première rangée sous une ligne : son
    last = lambda r: first(r) - 1                                            # centre au-delà ; la dernière au-dessus)
    def sill_row(x):                                                         # (le seuil : la dernière rangée claire du sol du
        for y in range(last(ray(CT, x)) + 3, last(ray(CT, x)) - 3, -1):      # peintre au-dessus de son bois sombre, à deux
            if on[y, x] @ LUM > 25: return max(y, last(ray(CT, x)))          # rangées près ; son rayon là où son sol est
        return last(ray(CT, x))                                              # sombre)
    cw0, fw1 = first(Co), last(Fo)                                           # (les rangées du mur)
    jt, jb = first(ray(CH, XB + 1)), last(ray(CT, XB + 1))                   # (celles de la face du montant : de face)
    a_m = EYE / CT                                                           # (l'écart de la façade à l'œil, m : le seuil)
    Zw = F_PX * a_m / (VP[0] - XW)                                           # (le mur du fond, à tant de mètres)
    cls, tbot = {}, {}
    for x in range(XA, XB + 1):
        h0, t1 = first(ray(CH, x)), sill_row(x); tbot[x] = t1 + 0.5
        if x > XB - J:                                                       # la face du montant : de face, du linteau au seuil
            for y in range(h0 - 3, h0):
                if lit0[y, x]: cls[y, x] = 'soffit'
            for y in range(h0, t1 + 1): cls[y, x] = 'soffit' if y < jt else 'jamb' if y <= jb else 'sill'
            continue
        for y in range(h0 - 3, h0 + 1):                                     # (la sous-face : sa rangée, et ce que la pièce du
            if y == h0 or lit0[y, x]: cls[y, x] = 'soffit'                   # peintre avait au-dessus d'elle)
        for y in range(h0 + 1, t1 + 1): cls[y, x] = 'ceil' if y < cw0 else 'wall' if y <= fw1 else 'floor'
    maps = {x: col_map(x, tracks, Co, Fo, on @ LUM) for x in range(XA, XR + 1)}

    # le plafond : le grain du haut sombre de la pièce du peintre (CEIL_SRC), répété en miroir, à ses tons (sa distance au
    # tube, en bandes) ; le sol : le grain de son sol (chaque colonne de son sol ramenée à FLOOR_ROWS rangées), allumé à la
    # flaque de lumière posée sur lui (en perspective), éteint à ses tons éteints (plus clair vers le seuil)
    cx0, cx1, cdy = CEIL_SRC
    cpat = {k: grain(np.array([[S[k][first(ray(CH, x)) + 1 + i, x] for x in range(cx0, cx1)] for i in range(cdy)])) for k in S}
    fcols = [x for x in range(FLOOR_SRC[0], FLOOR_SRC[1])]
    def fcol(k, x):
        ys = list(range(first(ray(CF, x)), int(tbot[x])))
        return [S[k][ys[int(i * len(ys) / FLOOR_ROWS)], x] for i in range(FLOOR_ROWS)]
    fpat = {k: grain(np.array([fcol(k, x) for x in fcols]).transpose(1, 0, 2)) for k in S}
    fpx = {k: np.array([S[k][y, x] for x in range(XA, XR + 1) for y in range(first(ray(CF, x)), int(tbot[x]))]) for k in S}
    def tones(px, pcs):
        o = px[np.argsort(px @ LUM)]; n = len(o)
        return [np.median(o[int(n * max(0, p - 5) / 100):max(int(n * max(0, p - 5) / 100) + 1, int(n * min(100, p + 5) / 100))], 0) for p in pcs]
    ftone = {'on': tones(fpx['on'], POOL[3]), 'off': tones(fpx['off'], FLOOR_OFF[1])}
    tx0, tx1 = ((t - VP[0]) * Zw / F_PX for t in TUBE)                       # (le tube : ses bouts, m)
    Zt = Zw * (VP[1] - Co) / (VP[1] - (TUBE_ROW + len(TUBE_RAYS) / 2))      # (sa profondeur : celle de sa rangée au plafond)

    def floor_px(k, x, y):
        Z = F_PX * EYE / (y - VP[1]); X = (VP[0] - x) * Z / F_PX - a_m       # (sur le sol : le long de la rue, dans la boutique)
        g = tile(fpat[k], y - fw1 - 1, x - XA)
        if k == 'on':
            e = np.exp(-((Z - POOL[0][0]) / POOL[1][0]) ** 2 - ((X - POOL[0][1]) / POOL[1][1]) ** 2)
            return ftone['on'][next(i for i, lim in enumerate(POOL[2]) if e >= lim)] * g
        u = (y - Fo) / max(1e-6, tbot[x] - Fo)
        return ftone['off'][0 if u < FLOOR_OFF[0] else 1] * g

    def ceil_px(k, x, y):
        Z = Zw * (VP[1] - Co) / (VP[1] - y); X = (x - VP[0]) * Z / F_PX
        d = np.hypot(max(0.0, tx0 - X, X - tx1), Zt - Z)
        band = next(b for lim, b in CEIL if d < lim)
        return np.array((CEIL_ON if k == 'on' else CEIL_OFF)[band], float) * tile(cpat[k], y - cw0, x - XA)

    for (y, x), c in cls.items():
        for k in S:
            if c == 'wall':
                col = S[k][maps[x][y], x].copy()
                if k == 'on':
                    col *= 1 - FALL * max(0.0, (y - 600) / (Fo - 600))
                    if y == cw0: col *= JUNCTION[1]
                if y == fw1: col *= FOOT
            elif c == 'ceil':
                col = ceil_px(k, x, y)
                if k == 'on' and y == cw0 - 1: col = col * JUNCTION[0]
            elif c == 'floor':
                col = floor_px(k, x, y)
            elif c == 'jamb':
                edge = np.array(JAMB[0], float); i = min(2, (XB - x) * 3 // J)   # (0 loin de la pièce … 2 contre elle)
                share = JAMB[1][i] * (0.75 + 0.25 * (y - jt) / max(1, jb - jt)) if k == 'on' else 0.0
                col = S['off'][y, XB + 1] * (1 - share) + edge * share
            elif c == 'soffit':
                col = S['off'][y, XB + 1] * SOFFIT if y >= ZONE[1] else S[k][y, x]
            elif c == 'sill':                                                # (sous le montant : le seuil du peintre)
                col = S[k][y, x]
            N[k][y, x] = col

    # le tube, au plafond (de travers à la rue : horizontal), redessiné net : chaque rangée de sa boîte de la couleur médiane
    # de la rangée de même rang du tube du peintre, le long de ses rayons ; ses bouts, ceux du peintre ; là où le plafond se
    # voit (sous la sous-face)
    nt = int(round(ray(TUBE_RAYS[1], 207) - ray(TUBE_RAYS[0], 207))) + 1     # (ses rangées)
    tcol = {k: [np.median([S[k][first(ray(TUBE_RAYS[0], xs)) + i, xs] for xs in range(TUBE[0] + 1, TUBE[1])], 0) for i in range(nt)] for k in S}
    tube = set()
    for i in range(nt):
        y = TUBE_ROW + i
        for x in range(TUBE[0], TUBE[1] + 1):
            if cls.get((y, x)) != 'ceil': continue
            for k in S:
                N[k][y, x] = tcol[k][i] if TUBE[0] < x < TUBE[1] else S[k][first(ray(TUBE_RAYS[0], x)) + i, x]
            tube.add((y, x))
    # allumée, sa lueur autour de lui, sur le plafond et le haut du mur, en marches (GLOW : la part de sa couleur à 1, 2, 3 px)
    tc = tcol['on'][0]
    for (y, x), c in cls.items():
        if c in ('wall', 'ceil') and (y, x) not in tube:
            d = max(TUBE[0] - x, x - TUBE[1], TUBE_ROW - y, y - (TUBE_ROW + nt - 1), 0)
            if 1 <= d <= len(GLOW) and N['on'][y, x] @ LUM < tc @ LUM: N['on'][y, x] = N['on'][y, x] + (tc - N['on'][y, x]) * GLOW[d - 1]

    # la vitre de la porte de gauche : allumée, plus sombre loin de l'ouverture et du tube (vers la gauche, vers le bas :
    # ses marchandises éclairées de côté) et derrière un verre ; un reflet en biais, à peine, sur le verre seul
    gx0, gy0, gx1, gy1 = PANE
    for y in range(gy0, gy1):
        for x in range(gx0, gx1):
            if lit0[y, x]:
                N['on'][y, x] *= GLASS_DIM * (1 - PANE_FALL[0] * (gx1 - 1 - x) / (gx1 - 1 - gx0)) * (1 - PANE_FALL[1] * (y - gy0) / (gy1 - gy0))
    glass = np.zeros((H, W), bool)
    for y in range(gy0, gy1):
        for x in range(gx0, gx1):
            glass[y, x] = (S['on'][y, x] @ LUM) > (S['off'][y, x] @ LUM) + 3 or (S['off'][y, x] @ LUM) > 22
    for slope, wdt, add in SHEEN:
        for y in range(gy0, gy1):
            for x in range(gx0, gx1):
                if glass[y, x] and abs((x - SHEEN_AT[0]) + slope * (y - SHEEN_AT[1])) < wdt / 2:
                    for k in S: N[k][y, x] = N[k][y, x] + add

    # les calques : la devanture éteinte (et la même dans la coupure de courant), ni plan lointain ni couchant ; le comp :
    # ce qui change quand elle s'allume
    zs = (slice(zy0, zy1), slice(zx0, zx1))
    L[0][zs][..., :3] = N['off'][zs]; L[0][zs][..., 3] = 255
    L[1][zs][..., :3] = N['off'][zs] * cut[zs]; L[1][zs][..., 3] = 255
    for (n, m), l in zip(names, L): save(l, n, m)
    diff = np.zeros((H, W), bool); diff[zs] = np.abs(np.round(N['on'][zs]) - np.round(N['off'][zs])).sum(2) > 0
    keep = np.zeros((H, W), bool); keep[py:py + ch, px:px + cw] = cp[..., 3] > 0
    keep[zs] = False                                                         # (hors de la devanture, le comp tel quel)
    spr = np.zeros((H, W, 4))
    spr[keep] = np.concatenate([on[keep], np.full((keep.sum(), 1), 255.0)], 1)
    spr[diff] = np.concatenate([N['on'][diff], np.full((diff.sum(), 1), 255.0)], 1)
    ys, xs = np.where(spr[..., 3] > 0)
    bx, by, bw, bh = int(xs.min()), int(ys.min()), int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1)
    save(spr[by:by + bh, bx:bx + bw], UP + '.webp', 'RGBA')
    s_ = open(A('street.js'), encoding='utf-8').read()
    s_, n_s = re.subn(r'"%s": \{"src": "assets/%s\.webp\?v=\d+", "x": \d+, "y": \d+, "w": \d+, "h": \d+\}' % (UP, UP),
                      f'"{UP}": {{"src": "assets/{UP}.webp?v={UP_V}", "x": {bx}, "y": {by}, "w": {bw}, "h": {bh}}}', s_)
    assert n_s == 1, 'street.js : le comp de la boutique est introuvable'
    open(A('street.js'), 'w', encoding='utf-8').write(s_)
    worst = max((max(m.values()) - min(m.values()) + 1) / len(m) for m in maps.values())   # (les rangées de la peinture par rangée du mur)
    print('ouverture', XB - XA + 1, 'colonnes |', len(tracks), 'bords suivis | mur', cw0, '..', fw1, '| montant', jt, '..', jb,
          '| resserrement des étagères au plus %.1f %%' % (100 * (worst - 1)), '| comp', (bx, by, bw, bh), int(diff.sum()), 'px')


if __name__ == '__main__':
    main()
