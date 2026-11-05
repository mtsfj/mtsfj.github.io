#!/usr/bin/env python3
"""Red (le dresseur de Pokémon de la première génération, Pikachu sur l'épaule) à la porte du balcon, au-dessus du centre
Pokémon : ses silhouettes, découpées de la planche dessinée pour lui par le propriétaire.

    python3 tools/red_sheet.py      (lit tools/src/red_sheet.webp ; écrit assets/red_sil.webp et remet à jour les tables ZR,
                                     ZRC et ZRB de assets/street.js ; on peut le relancer)

La source, sur fond blanc : la marche de profil vers la droite (8 images), l'attente de face (4), le lancer de la Poké
Ball de face (8, la balle dessinée), le demi-tour de face jusqu'à son dos (6 : de trois quarts, de profil vers la gauche
aux images 3 et 4, puis le dos et le sac). Derrière le verre dépoli on ne voit que son ombre : seule la forme compte.

Chaque image est découpée du blanc : sa couverture, pleine dedans (les blancs intérieurs aussi : le devant de la
casquette, les semelles), le liseré d'anticrénelage du bord pris pour sa part de trait (un gris entre le trait noir et le
blanc), rien autour (pas de halo ; les traits de vitesse, l'ombre au sol, les poussières laissés). Puis une seule
échelle : PPM px par mètre, Red debout 1.6 m du haut de la casquette aux semelles, Pikachu compris, chaque rangée de la
source ramenée à cette taille (elles ne sont pas dessinées à la même), la marche un peu plus basse (jambes écartées) ; un
seul sol, le bas des semelles ; chaque pixel de la planche prend la part de la source qu'il couvre (une boîte exacte).

La marche : la source dessine des jambes écartées qui ne reculent pas sous lui (son pied posé ne bouge presque pas d'une
image à l'autre) ; un pas est pris de quatre de ses images (PAS : la pose du talon, le poids dessus, l'autre pied qui part,
il passe), le pas mesuré du talon de derrière à celui de devant à la pose, et le pied posé recule d'un quart de pas à
chaque image sous sa racine : là où le dessin ne le fait pas, les jambes penchent (une cisaille, nulle aux hanches). Ce pas
est ZR.D ; street.js avance son point au sol le long de sa ligne en px de la planche à l'échelle de chaque endroit (zrU),
un pied posé y reste donc où il est. walkT vers la droite (il vient vers nous), walkA son miroir (il repart).

L'arrêt (settle) : le dernier demi-pas, le profil du demi-tour en miroir, posé là où le pied de la dernière image de marche
reste posé ; puis il se tourne vers nous, la tête d'abord (sa tête de face et Pikachu sur son épaule droite sur son corps
de trois quarts en miroir), puis de face (le demi-tour, image 1). Le demi-tour (turn) : de face jusqu'à son profil gauche,
sur place ; le départ : la première image de walkA, posée là où le pied de derrière du profil reste posé. xa0 et xr0 en
découlent (le long de sa ligne).

Le lancer : la balle ôtée de sa main (son disque vidé, ses doigts gardés) et de l'air, la queue de Pikachu ôtée derrière
sa tête (elle n'y est pas dans l'attente : les cheveux de l'attente à sa place) ; la balle est dessinée à part par
street.js, nette sur le verre flou, à son centre de ZRB : dans la main où la source la dessine, en l'air lâchée de la
paume ouverte, montée à hauteur de ses yeux (près de sa tête, sur la vitre claire), rattrapée dans la paume, une parabole
(g = 9.81) tous les 0.05 s.
Il faut Pillow, numpy, scipy.
"""
import json
import math
import os
import re
import numpy as np
from PIL import Image
from scipy import ndimage as nd

ICI = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ICI, 'src', 'red_sheet.webp')
OUT = os.path.join(os.path.dirname(ICI), 'assets', 'red_sil.webp')
PPM = 88.0                      # px de la planche par mètre
TAILLE = 1.6                    # Red debout, du haut de la casquette aux semelles (m)
RANGS = {'marche': 20, 'attente': 282, 'lancer': 568, 'tour': 844}   # le haut des quatre rangées de la source
CAM = {'x': 6.72, 'zs': 33.4129}                                     # (street.js, ZR : sa ligne de marche, la distance de son arrêt)
PORTE = 963                                                          # (le bord gauche de la boîte de la porte, z1Door)


# ---- la source : chaque image découpée du blanc -------------------------------------------------------------------
def source():
    rgb = np.asarray(Image.open(SRC).convert('RGB')).astype(np.float32)
    return rgb, 765 - rgb.sum(2)                 # (l'encre : l'écart au blanc, de 0 à 765 ; le fond 0..6, le trait ~750)


def figures(rgb, d):
    m = d > 40
    lab, n = nd.label(m, np.ones((3, 3)))
    sz = nd.sum(m, lab, range(1, n + 1)); sl = nd.find_objects(lab)
    out = {k: [] for k in RANGS}
    for l in (i + 1 for i in range(n) if sz[i] > 5000):
        s = sl[l - 1]
        k = min(RANGS, key=lambda k: abs(RANGS[k] - s[0].start))
        out[k].append((s[1].start - 6, s[0].start - 6, np.pad(lab[s] == l, 6)))
    fr = {}
    for k in out:
        fr[k] = []
        for x0, y0, comp in sorted(out[k], key=lambda t: t[0]):
            h, w = comp.shape
            f = {'x0': x0, 'y0': y0, 'comp': comp, 'rgb': rgb[y0:y0 + h, x0:x0 + w], 'd': d[y0:y0 + h, x0:x0 + w]}
            f['A'] = alpha(f)
            fr[k].append(f)
    return fr


def alpha(f):
    """La couverture de chaque pixel : 1 dedans (les blancs intérieurs compris : la casquette, les semelles), le liseré
    d'anticrénelage au bord pris pour ce qu'il couvre (un gris entre le trait et le blanc : son encre sur celle du trait)."""
    comp, d, rgb = f['comp'], f['d'], f['rgb']
    full = nd.binary_fill_holes(comp)
    inner = nd.binary_erosion(full, np.ones((3, 3)))
    a = inner.astype(np.float32)
    dmax = nd.maximum_filter(np.where(inner, d, 0), size=3)   # le trait le plus sombre juste dedans
    gris = rgb.max(2) - rgb.min(2) < 45
    ring = full & ~inner
    a[ring] = np.where((dmax[ring] > 600) & gris[ring], np.clip((d[ring] - 6) / np.maximum(dmax[ring] - 6, 1), 0, 1), 1.0)
    out = nd.binary_dilation(full, np.ones((3, 3))) & ~full   # dehors, contre le bord : ce qui reste d'encre
    a[out] = np.clip((d[out] - 8) / 740, 0, 0.25)
    return a


def mesure(f):
    """Le haut de la casquette (son premier rang de rouge), ses bords, et le sol (le bas des semelles, au sous-pixel)."""
    A = f['A']; R, G, B = f['rgb'][..., 0], f['rgb'][..., 1], f['rgb'][..., 2]
    rouge = (R > 150) & (G < 90) & (B < 100) & (A > 0.5)
    cap = int(np.argmax(rouge.sum(1) >= 3))
    xs = np.where(rouge[cap:cap + 22].any(0))[0]
    rows = np.where(A.max(1) > 0.5)[0]; b = rows[-1]
    col = A[b - 6:].sum(0) + (b - 6)                       # le bord bas de chaque colonne (pleine au-dessus)
    plein = A[b - 6] > 0.9
    sol = float(np.percentile(col[plein], 95)) if plein.any() else b + 1.0
    return {'cap': cap, 'cg': int(xs.min()), 'cd': int(xs.max()), 'sol': sol}


def pieds(A, sol, haut=14):
    """Les chaussures au sol : les colonnes couvertes dans les `haut` derniers px au-dessus du sol, en morceaux."""
    colm = A[int(sol) - haut:int(math.ceil(sol))].max(0) > 0.5
    lab, n = nd.label(colm)
    return [(s[0].start, s[0].stop) for s in nd.find_objects(lab) if s[0].stop - s[0].start > 5]


# ---- rééchantillonnage : chaque pixel de la planche prend la part de la source qu'il couvre (boîte exacte) -----------------
def boite(A, f, ox, oy, W, H):
    """A (pixels de la source) à l'échelle f, son point (0, 0) en (ox, oy) de la sortie W x H."""
    h, w = A.shape
    S = np.zeros((h + 1, w + 1), np.float64); S[1:, 1:] = A.cumsum(0).cumsum(1)
    def integ(ys, xs):                           # l'intégrale de A sur [0, y] x [0, x] (bilinéaire entre les coins : exacte)
        ys = np.clip(ys, 0, h); xs = np.clip(xs, 0, w)
        y0 = np.minimum(np.floor(ys).astype(int), h - 1); x0 = np.minimum(np.floor(xs).astype(int), w - 1)
        fy = ys - y0; fx = xs - x0
        return (S[y0, x0] * (1 - fy) * (1 - fx) + S[y0 + 1, x0] * fy * (1 - fx) + S[y0, x0 + 1] * (1 - fy) * fx + S[y0 + 1, x0 + 1] * fy * fx)
    gy = (np.arange(H + 1) - oy) / f; gx = (np.arange(W + 1) - ox) / f
    Y, X = np.meshgrid(gy, gx, indexing='ij')
    I = integ(Y, X)
    out = (I[1:, 1:] - I[:-1, 1:] - I[1:, :-1] + I[:-1, :-1]) * f * f
    return np.clip(out, 0, 1).astype(np.float32)


def cisaille(A, dx, y0, y1):
    """Les jambes penchées : chaque rang décalé de dx * (y - y0) / (y1 - y0) (0 aux hanches y0, dx aux semelles y1, dx
    au-delà), au sous-pixel ; la sortie élargie de P de chaque côté."""
    h, w = A.shape
    P = int(abs(dx)) + 2
    k = np.clip((np.arange(h) - y0) / (y1 - y0), 0, 1)[:, None] * dx
    yy, xx = np.mgrid[0:h, 0:w + 2 * P].astype(np.float32)
    return nd.map_coordinates(A, [yy, xx - P - k], order=1, cval=0).astype(np.float32), P


# ---- les images de la planche ---------------------------------------------------------------------------------------
class Fig:
    """Une image : son alpha (px de la source), son échelle vers la planche, sa racine (x) et son sol (y) dans l'alpha."""
    def __init__(self, A, f, rx, sol, nom):
        self.A, self.f, self.rx, self.sol, self.nom = A, f, rx, sol, nom
    def miroir(self):
        return Fig(self.A[:, ::-1].copy(), self.f, self.A.shape[1] - self.rx, self.sol, self.nom + "'")
    def place(self, CW, CH, AX, AY):
        return boite(self.A, self.f, AX - self.f * self.rx, AY - self.f * self.sol, CW, CH)


def chaussures(A, sol, haut=14):
    """Les deux chaussures (arrière, avant) en x continus [a, b], et leur levée (px au-dessus du sol)."""
    out = []
    for a, b in pieds(A, sol, haut):
        rows = np.where(A[:, a:b].max(1) > 0.5)[0]
        out.append((float(a), float(b), round(sol - rows[-1] - 1, 1)))
    return out


def u_de_w(w):                                   # où est son point au sol le long de sa ligne, en px de la planche
    return -CAM['x'] * PPM * math.log(CAM['zs'] - w)


def w_de_u(u):
    return CAM['zs'] - math.exp(-u / (CAM['x'] * PPM))


def sans_balle(f, centre, r=12.5):
    """La Poké Ball ôtée de la main : son disque vidé, sauf la peau (les doigts devant elle) et leur trait ; son centre
    (y, x dans la source) rendu dans l'image (x, y)."""
    A = f['A'].copy(); R, G, B = (f['rgb'][..., c] for c in range(3))
    h, w = A.shape; yy, xx = np.mgrid[0:h, 0:w]
    cy, cx = centre[0] - f['y0'], centre[1] - f['x0']
    disque = (yy - cy) ** 2 + (xx - cx) ** 2 <= r * r
    peau = (R > 170) & (G > 110) & (B > 80) & (R - B > 45) & (G - B > 15)
    garde = nd.binary_dilation(peau & disque, np.ones((3, 3)))
    A[disque & ~garde] = 0
    lab, n = nd.label(A > 0.02, np.ones((3, 3)))   # (ce qui ne tient plus à lui)
    if n > 1:
        sz = nd.sum(A > 0.02, lab, range(1, n + 1)); A[(lab > 0) & (lab != 1 + int(np.argmax(sz)))] = 0
    return A, (cx, cy)


def greffe(dst, src, s, ancre_dst, ancre_src, region):
    """src (l'alpha d'une autre image) à l'échelle s autour de son point ancre_src, posé sur ancre_dst de dst, dans region."""
    h, w = dst.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    sy = (yy - ancre_dst[1]) / s + ancre_src[1]; sx = (xx - ancre_dst[0]) / s + ancre_src[0]
    v = nd.map_coordinates(src, [sy, sx], order=1, cval=0)
    out = dst.copy(); out[region] = v[region]
    return out


def profil_pieds(g):
    """Un profil debout (ses pieds l'un derrière l'autre, d'un seul morceau) : le centre de chacun par rapport à la racine,
    coupés là où le bas de la semelle change de rang (celui de derrière, posé, plus bas)."""
    a, b = pieds(g.A, g.sol, 14)[0]
    bas = np.array([np.where(g.A[:, x] > 0.5)[0][-1] for x in range(a, b)])
    lo = bas >= bas.max() - 0.5
    xs = np.arange(a, b)
    c1 = (xs[~lo].min() + xs[~lo].max() + 1) / 2 if (~lo).any() else a
    c2 = (xs[lo].min() + xs[lo].max() + 1) / 2
    return sorted([(c1 - g.rx) * g.f, (c2 - g.rx) * g.f])


# ---- les réglages (indices des images de la source à partir de 1, rangée par rangée) --------------------------------
POSTURE = 0.985                  # la marche, jambes écartées : la tête un peu plus bas que debout
PAS = (2, 8, 6, 7)               # un pas, de profil : la pose (talon devant), le poids dessus, l'autre pied qui part, il passe
RACINE = 22                      # (la marche : sa racine, ce nombre de px de la source devant l'arrière de la casquette)
HANCHE = 100                     # (la marche : les jambes penchées depuis ce nombre de px au-dessus du sol)
COU = (55, 90, 66)               # (l'arrêt, son trois-quarts : la tête de face (et Pikachu) au-dessus de 55 px sous le haut de
                                 # la casquette, le corps de trois-quarts en dessous de 90 px, les deux entre, Pikachu du
                                 # trois-quarts (x > 66 avant le miroir) ôté ; la tête mène)
TOUR = (1, 2, 3)                 # le demi-tour : de face, de trois quarts, de profil (vers la gauche)
LANCER = (7, 1, 2, 3, 4, 5, 6, 8)   # le lancer : la main au gilet (la balle prise), la balle tenue, l'élan, lâchée, en l'air,
                                 # qui retombe, rattrapée, tenue
BALLE_MAIN = {1: (655.57, 32.4), 2: (655.57, 195.4), 6: (648.57, 853.4), 8: (657.57, 1182.4)}   # (le centre de la balle dans
BALLE_AIR = {4: (581.57, 516.40), 5: (610.23, 680.76)}                                          # la source (y, x), trouvé par sa forme)
PAUME = {3: (21, 79), 5: (21, 71)}   # (le lancer : la balle sur la paume ouverte, x et y dans les images 3 et 5)
SOMMET = 0.3                     # (le lancer : la balle monte de 0.3 m au-dessus de la main)


def build():
    rgb, d = source()
    F = figures(rgb, d)
    M = {k: [mesure(f) for f in F[k]] for k in F}
    H = {k: np.mean([m['sol'] - m['cap'] for m in M[k]]) for k in M}
    ech = {k: TAILLE * PPM / H[k] for k in H}
    ech['marche'] = TAILLE * PPM * POSTURE / H['marche']
    fig = lambda k, i, rx: Fig(F[k][i - 1]['A'], ech[k], rx, M[k][i - 1]['sol'], k[0] + str(i))

    # la marche (de profil, vers la droite) : un pas en len(PAS) images ; le pied posé (S, celui de devant à la pose) recule
    # d'autant à chaque image sous la racine (l'arrière de la casquette + RACINE) : là où il ne le fait pas, les jambes
    # penchent (cisaille, nulle aux hanches) ; le pas, du talon de derrière à celui de devant à la pose
    fm = ech['marche']
    W = []
    for i in PAS:
        f, m = F['marche'][i - 1], M['marche'][i - 1]
        ch = chaussures(f['A'], m['sol'])
        W.append({'i': i, 'rx': m['cg'] + RACINE, 'S': ch[-1][0], 'B': ch[0][0], 'ch': ch})
    n = len(W)
    pas = W[0]['S'] - W[0]['B']                  # (px de la source)
    a = pas / n
    req = [(W[0]['S'] - W[0]['rx']) - j * a - (W[j]['S'] - W[j]['rx']) for j in range(n)]
    d0 = -(min(req) + max(req)) / 2
    walk = []
    for j, w in enumerate(W):
        dx = req[j] + d0
        f, m = F['marche'][w['i'] - 1], M['marche'][w['i'] - 1]
        A2, P = cisaille(f['A'], dx, m['sol'] - HANCHE, m['sol'])
        walk.append(Fig(A2, fm, w['rx'] + P, m['sol'], 'w%d' % w['i']))
        w['dx'] = dx
    print('marche : pas %.1f px de la source (%.1f px de la planche, %.3f m), %.2f px de la planche par image ; cisailles %s' % (
        pas, pas * fm, pas * fm / PPM, a * fm, [round(w['dx'], 1) for w in W]))
    ab = a * fm                                  # (px de la planche par image de marche)
    racine = lambda k, i: sum(chaussures(F[k][i - 1]['A'], M[k][i - 1]['sol'])[q][e] for q, e in ((0, 0), (-1, 1))) / 2

    # l'attente : les pieds au même endroit (leur milieu), de face
    idle = [fig('attente', i, racine('attente', i)) for i in range(1, 5)]

    # le lancer : la balle ôtée de la main (son centre gardé), à gauche au-dessus des épaules la queue de Pikachu ôtée (les
    # cheveux de l'attente à sa place, posés sur le coin de la casquette)
    I1, m1 = F['attente'][0], M['attente'][0]
    s_ia = ech['attente'] / ech['lancer']
    toss, balle = [], {}
    for i in LANCER:
        f, m = F['lancer'][i - 1], M['lancer'][i - 1]
        A = f['A']
        if i in BALLE_MAIN: A, balle[i] = sans_balle(f, BALLE_MAIN[i])
        if i in BALLE_AIR: balle[i] = (BALLE_AIR[i][1] - f['x0'], BALLE_AIR[i][0] - f['y0'])
        h, w = A.shape; yy, xx = np.mgrid[0:h, 0:w]
        haut = (yy < m['cap'] + 56) & (xx < m['cg'] + 3)
        bas = (yy >= m['cap'] + 56) & (yy < m['cap'] + 70) & (xx < m['cg'] - 16)
        coin = ((m['cg'], m['cap']), (m1['cg'], m1['cap']))
        A = greffe(A, I1['A'], s_ia, *coin, haut)
        A[bas] = np.minimum(A[bas], greffe(A, I1['A'], s_ia, *coin, bas)[bas])
        g = Fig(A, ech['lancer'], racine('lancer', i), m['sol'], 'l%d' % i)
        toss.append(g)
        if i in balle: g.balle = balle[i]

    # le demi-tour (de face à son profil gauche) : il pivote sur place, la racine au milieu des pieds
    turn = [fig('tour', i, racine('tour', i)) for i in TOUR]

    # l'arrêt (il arrivait de profil vers la droite, il se tourne vers nous) : le profil du demi-tour en miroir (Pikachu
    # derrière lui, à gauche, comme en marchant), puis son trois-quarts la tête seule en miroir (Pikachu reste sur l'épaule
    # de droite, celle où il est de face), puis de face
    t2m = turn[1].miroir(); f1, m1t = F['tour'][0], M['tour'][0]; m2 = M['tour'][1]
    A = t2m.A; h, w = A.shape; yy = np.mgrid[0:h, 0:w][0]
    c2 = (w - m2['cd'] + w - m2['cg']) / 2           # (le milieu de sa casquette, en miroir)
    T1 = greffe(np.zeros_like(A), f1['A'], 1.0, (c2, m2['cap']), ((m1t['cg'] + m1t['cd']) / 2, m1t['cap']), np.ones_like(A, bool))
    xx = np.mgrid[0:h, 0:w][1]
    haut, bande = yy < m2['cap'] + COU[0], (yy >= m2['cap'] + COU[0]) & (yy < m2['cap'] + COU[1])
    Ab = np.where(xx >= w - COU[2], A, 0)          # (dans la bande, Pikachu du trois-quarts (à gauche, en miroir) ôté)
    synth = Fig(np.where(haut, T1, np.where(bande, np.maximum(T1, Ab), A)), ech['tour'], t2m.rx, m2['sol'], "t1+t2'")
    settle = [turn[2].miroir(), synth, turn[0]]

    # où il est : l'arrêt pris là où le pied posé de la dernière image de marche reste posé (le centre des chaussures), les
    # images de l'arrêt et du demi-tour sur place ; le départ (la première image de la marche en miroir) là où le pied
    # de derrière du profil reste posé. En px de la planche, le long de sa ligne (vers nous : +), à partir de la pose
    # suivante de la marche (l'arrêt) ou de sa place debout (le départ)
    def centre(g, q):                            # le centre de la chaussure q (0 : la plus à gauche) par rapport à la racine
        ch = chaussures(g.A, g.sol); a, b = ch[q][0], ch[q][1]
        return ((a + b) / 2 - g.rx) * g.f
    t3m = turn[2].miroir()
    pose_t3 = profil_pieds(t3m)                  # (ses deux pieds dans le profil : le plus à gauche, l'autre)
    S = -ab + centre(walk[-1], -1)               # la dernière image de marche : sa racine une image avant la pose
    x_arret = S - pose_t3[0]
    t3 = turn[2]; pose = profil_pieds(t3)
    x_depart = pose[1] - centre(walk[0].miroir(), -1)
    print('arrêt : à %.2f px de la pose suivante ; départ : à %.2f px de sa place' % (x_arret, x_depart))
    walkA = [g.miroir() for g in walk]
    return {'walkT': walk, 'walkA': walkA, 'settle': [t3m, synth], 'idle': idle, 'toss': toss, 'turn': turn}, ab, x_arret, x_depart, ech


# ---- la planche : une rangée par mouvement, chaque image posée sur son point au sol (le même dans toute la rangée) --------
ORDRE = ('walkT', 'walkA', 'settle', 'idle', 'toss', 'turn')


def planche(R):
    ZRC, cases, y = {}, [], 0
    for k in ORDRE:
        ext = []
        for g in R[k]:
            ys, xs = np.where(g.A > 0.002)
            ext.append((g.f * (xs.min() - g.rx), g.f * (xs.max() + 1 - g.rx), g.f * (ys.min() - g.sol), g.f * (ys.max() + 1 - g.sol)))
        AX = math.ceil(max(-e[0] for e in ext)) + 1; AY = math.ceil(max(-e[2] for e in ext)) + 1
        CW = AX + math.ceil(max(e[1] for e in ext)) + 1; CH = AY + math.ceil(max(e[3] for e in ext)) + 1
        ZRC[k] = [y, CW, CH, len(R[k]), AX, AY]
        cases.append([g.place(CW, CH, AX, AY) for g in R[k]])
        y += CH
    W = max(c[1] * c[3] for c in ZRC.values())
    S = np.zeros((y, W), np.float32)
    for k, row in zip(ORDRE, cases):
        top, CW, CH = ZRC[k][:3]
        for i, c in enumerate(row): S[top:top + CH, i * CW:(i + 1) * CW] = c
    return S, ZRC


def balle_vol(R, ZRC):
    """Un lancer : les images et leur durée, la balle (son centre dans la case) à chaque pas de 0.05 s. Dans la main :
    là où la source la dessine ; en l'air : lâchée de la paume de l'image 3 (au-dessus de la main, là où elle s'y pose),
    montée de SOMMET (à hauteur de ses yeux, près de sa tête : la source la lance plus haut, loin de lui), rattrapée dans
    la paume de l'image 5 ; une parabole (g = 9.81)."""
    c = ZRC['toss']; AX, AY = c[4], c[5]
    G = {g.nom: g for g in R['toss']}
    def case(g, x, y): return (AX + g.f * (x - g.rx), AY + g.f * (y - g.sol))
    rel = case(G['l3'], *PAUME[3]); att = case(G['l5'], *PAUME[5]); sommet = (None, rel[1] - SOMMET * PPM)
    hm = (rel[1] - sommet[1]) / PPM; hd = (att[1] - sommet[1]) / PPM
    tm, td = math.sqrt(2 * hm / 9.81), math.sqrt(2 * hd / 9.81); T = tm + td
    n = round(T / 0.05); dt = T / n
    def vol(t):                                  # (t depuis le lâcher)
        x = rel[0] + (att[0] - rel[0]) * t / T
        y = sommet[1] + 0.5 * 9.81 * (t - tm) ** 2 * PPM
        return [round(x, 1), round(y, 1)]
    idx = {g.nom: i for i, g in enumerate(R['toss'])}
    def tenue(nom, d): return [[idx[nom], d, *[round(v, 1) for v in case(G[nom], *G[nom].balle)]]]
    seq = tenue('l1', 0.3) + tenue('l2', 0.15)
    for j in range(n + 1):                       # en l'air : l'image 3 à la montée, la 4 autour du sommet, la 5 à la descente (et
                                                 # quand elle y retombe)
        t = j * dt; nom = 'l3' if t < tm * 0.6 else 'l4' if t < tm + td * 0.45 else 'l5'
        seq.append([idx[nom], round(dt, 4), *vol(t)])
    seq += tenue('l6', 0.25) + tenue('l8', 0.3)
    print('le lancer : %.2f m au-dessus de la main, %.2f s en l\'air (%d pas)' % (hm, T, n))
    return seq, idx


CADENCE = 0.6                    # (s par pas)


def main():
    R, ab, x_arret, x_depart, ech = build()
    S, ZRC = planche(R)
    seq, idx = balle_vol(R, ZRC)
    rgba = np.zeros(S.shape + (4,), np.uint8); rgba[..., 3] = np.round(S * 255).astype(np.uint8)
    Image.fromarray(rgba, 'RGBA').save(OUT, lossless=True, quality=100, method=6)
    n = ZRC['walkT'][3]
    D = ab * n                                   # (un pas : les n images de la rangée)
    xa0 = -w_de_u(u_de_w(0) - x_arret)           # (la marche s'arrête en -xa0, là où il poserait le pied suivant)
    xr0 = w_de_u(u_de_w(0) + x_depart)
    ext = max(ZRC[k][1] - ZRC[k][4] for k in ('walkT', 'walkA'))   # (ce qui dépasse devant sa racine vers la droite, px de la planche)
    s0 = (PORTE - 1 - 700) / (CAM['x'] + ext / PPM)                  # il entre et sort tout entier à gauche de la porte : là, w0
    w0 = math.floor((CAM['zs'] - 1400 / s0) * 100) / 100
    zr = {'ppm': PPM, 'w0': w0, 'D': round(float(D), 2), 'v': round(float(D) / CADENCE, 1), 'xa0': round(xa0, 4), 'xr0': round(xr0, 4)}
    zrc = '{ ' + ', '.join('%s: [%s]' % (k, ', '.join(str(v) for v in ZRC[k])) for k in ORDRE) + ' }'
    zrb = json.dumps([[i, round(float(dt), 4), float(x), float(y)] for i, dt, x, y in seq]).replace(' ', '')
    js = os.path.join(os.path.dirname(ICI), 'assets', 'street.js')   # (ses tables dans street.js, remises à jour)
    t = open(js, encoding='utf-8').read()
    def remplace(t, motif, f):
        n = len(re.findall(motif, t)); assert n == 1, motif
        return re.sub(motif, f, t)
    t = remplace(t, r'(const ZR = \{ f: 1400, kf: 6\.03, x: 6\.72, zs: 33\.4129, )ppm: [^,]+, w0: [^,]+, D: [^,]+, v: [^,]+, xa0: [^,]+, xr0: [^ ]+ \}',
                 lambda m: m.group(1) + 'ppm: %g, w0: %g, D: %g, v: %g, xa0: %g, xr0: %g }' % tuple(zr[k] for k in ('ppm', 'w0', 'D', 'v', 'xa0', 'xr0')))
    t = remplace(t, r'const ZRC = [^;]*;', lambda m: 'const ZRC = ' + zrc + ';')
    t = remplace(t, r'const ZRB = [^;]*;', lambda m: 'const ZRB = ' + zrb + ';')
    open(js, 'w', encoding='utf-8').write(t)
    print(OUT, S.shape[1], 'x', S.shape[0], '; street.js : ZR', zr)


if __name__ == '__main__':
    main()
