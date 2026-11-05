#!/usr/bin/env python3
"""Les affiches WANTED de Luffy, collées sur le panneau à gauche de la porte d'Ichiraku, à la place de l'écran.

    python3 tools/luffy_wanted.py      (lit tools/src/luffy_wanted.webp et luffy_wanted_gear5.webp, le quadrilatère LB de
                                        assets/street.js ; écrit assets/luffy_wanted.webp et, dans street.js, la ligne LWP ;
                                        on peut le relancer : il écrit les mêmes octets)

Les deux affiches du propriétaire, de même mise en page (1:3) : la classique (Luffy qui rit sous son chapeau de paille,
WANTED, DEAD OR ALIVE, MONKEY.D. LUFFY, la prime, le Jolly Roger en bas, le papier déchiré) et celle du Gear 5 (cheveux
blancs, il rit aux éclats ; pas de crâne). La large (luffy_wanted_wide.webp, 2:3, le WANTED rouge et le navire) n'entre
pas dans ce cadre étroit : elle n'est pas prise ici, gardée pour un mur plus large.

Chaque affiche est détourée de son fond blanc : le blanc relié au bord de l'image (son liseré sombre ferme le papier, les
blancs du dedans restent), le bord déchiré gardé tel quel ; le trou de punaise de la classique percé (TROUS) ; sur celle du
Gear 5, l'étoile en filigrane du coin bas (FILIGRANE) rebouchée par le papier le plus proche.

Puis elle est dessinée directement dans le quadrilatère du panneau à l'écran (LB de street.js, en pixels de la scène, la
perspective de la façade) : chaque pixel de la scène prend la moyenne de ce qu'il couvre de l'affiche (N x N points remontés
par l'homographie du quadrilatère vers le papier, couleur et couverture), sans texture filtrée ; un pixel couvert à moitié
ou plus est du papier, opaque, les autres rien (des bords nets, pas de halo). A 17 x 54 px le texte ne fait que se deviner ;
la mise en page se lit : la bande sombre du WANTED, la photo (le chapeau jaune et son ruban rouge, le rire), les lignes du
texte, la prime, le crâne. Pour que le WANTED, le chapeau et le rire tombent sur des pixels entiers, l'affiche est posée
dans le cadre à moins de 0,4 px près (ses bords haut et bas, gauche et droit, CALE) là où ces parties sont le moins mêlées
au papier : l'écart à sa propre palette franche (ses couleurs pleines, prises sur la source) y compte quatre fois.
Puis chaque affiche a sa palette de 16 couleurs (k-moyennes en Lab, départ fixe : la plus sombre puis la plus éloignée),
chaque pixel la plus proche ; et les petits traits qui doivent tenir leur pixel (TRAITS : le ruban rouge du chapeau) leur
propre couleur là où ils couvrent assez du pixel.

La lumière : c'est du papier. Sans courant, la lumière du soir là où est le panneau : la peinture du panneau dans la rue
sans courant (street_unlit) comme un panneau clair (albédo PANNEAU) la montre ; allumée, celle d'Ichiraku en plus : la
lanterne de gauche juste au-dessus (sa couleur allumée) et la vitre de la porte à droite (ce qu'elle ajoute à la rue),
LAMPE de leur teinte. Deux images par affiche : sans courant, et ce que leur lumière y ajoute (l'éclairée moins elle,
couleur par couleur de la palette : les deux ensemble font l'éclairée exactement). street.js pose la première à la note
de la rue (l'heure, la nuit rouge) comme le bois et le mur autour, et ajoute la seconde comme une lumière, à la mesure de
la lanterne et de la cuisine (leur niveau, le courant de la zone ; rouge dans la nuit rouge, comme la lumière peinte de la
rue sur sa façade).

Le passage d'une affiche à l'autre : une seule image où le papier se soulève (son bas remonté de LEVE px, le panneau
dessous), puis l'autre affiche.

L'atlas (assets/luffy_wanted.webp) : une case de la boîte du quadrilatère (19 x 56 px) par image, 4 colonnes (la classique,
le Gear 5, la classique soulevée, le Gear 5 soulevé), 2 rangées (sans courant, la lumière d'Ichiraku) ; dessiné à 1:1 en
NearestFilter. La ligne LWP de street.js : la boîte, l'atlas, l'étoile des quatre héros près de son chapeau.
Il faut Pillow, numpy, scipy.
"""
import json
import os
import re

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
SRC = os.path.join(ICI, 'src')
JS = os.path.join(RACINE, 'assets', 'street.js')
OUT = os.path.join(RACINE, 'assets', 'luffy_wanted.webp')
AFFICHES = [('classique', 'luffy_wanted.webp'), ('gear5', 'luffy_wanted_gear5.webp')]
TROUS = {'classique': [(597, 98)]}                         # un point dans chaque trou du papier (px de la source)
FILIGRANE = {'gear5': (252, 940, 292, 972, 212)}            # l'étoile du coin : sa boîte (x0, y0, x1, y1), sa luminance mini
# les parties à poser sur des pixels entiers, en hauteur relative du papier (0 en haut, 1 en bas) : le WANTED, le chapeau, le rire
PARTIES = {'classique': [(0.087, 0.201), (0.205, 0.33), (0.38, 0.435)], 'gear5': [(0.05, 0.141), (0.16, 0.30), (0.31, 0.355)]}
# les petits traits qui tiennent leur pixel : là où ils couvrent au moins tant du pixel (dans leur bande de hauteur), leur
# propre couleur franche, en plus des 16 (le ruban rouge du chapeau, à cette taille un trait en biais de quatre pixels)
TRAITS = {'classique': [('ruban', lambda a: (a[..., 0] > 120) & (a[..., 1] < 70) & (a[..., 2] < 60), (0.21, 0.30), 0.33)],
          'gear5': []}
CALE = np.linspace(-0.4, 0.4, 9)                           # les écarts essayés pour chaque bord (px de la scène)
N = 24                                                     # points par côté de pixel (16 pour chercher la cale)
K = 16                                                     # couleurs par affiche
PANNEAU = 0.65                                             # l'albédo du panneau peint (clair) : la lumière du soir = sa couleur / 0.65
LAMPE = 0.22                                               # la lumière d'Ichiraku sur le papier, de la teinte de la lanterne et de la vitre
LEVE = 4                                                   # le papier soulevé : son bas remonté de tant (px)
ETOILE = ('classique', 0.86, 0.235)                        # l'étoile des quatre héros : en haut à droite du chapeau (relatif au papier)


def lire_lb():
    t = open(JS, encoding='utf-8').read()
    m = re.search(r'const LB = (\[\[[^;]*\]\]);', t)
    return [tuple(p) for p in json.loads(m.group(1))]


def detoure(a, nom):
    """La couverture du papier : tout sauf le blanc relié au bord ; les trous percés ; le filigrane rebouché."""
    blanc = (a.min(2) >= 222) & ((a.max(2) - a.min(2)) <= 14)
    zones, _ = ndi.label(blanc)
    bord = np.setdiff1d(np.unique(np.r_[zones[0], zones[-1], zones[:, 0], zones[:, -1]]), [0])
    papier = ~np.isin(zones, bord)
    for (x, y) in TROUS.get(nom, []):
        clair = a.min(2) >= 200
        tl, _ = ndi.label(clair)
        papier &= tl != tl[y, x]
    if nom in FILIGRANE:
        x0, y0, x1, y1, lmin = FILIGRANE[nom]
        lum = a @ np.array([0.299, 0.587, 0.114])
        tache = np.zeros(lum.shape, bool); tache[y0:y1, x0:x1] = lum[y0:y1, x0:x1] >= lmin
        _, (iy, ix) = ndi.distance_transform_edt(tache, return_indices=True)
        a = a[iy, ix]
    return a, papier


def homographie(Q):
    """Le carré unité (0,0) (1,0) (1,1) (0,1) vers le quadrilatère Q (haut-gauche, haut-droite, bas-droite, bas-gauche)."""
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = Q
    dx1, dx2, dx3, dy1, dy2, dy3 = x1 - x2, x3 - x2, x0 - x1 + x2 - x3, y1 - y2, y3 - y2, y0 - y1 + y2 - y3
    d = dx1 * dy2 - dx2 * dy1
    g, h = (dx3 * dy2 - dx2 * dy3) / d, (dx1 * dy3 - dx3 * dy1) / d
    return np.array([[x1 - x0 + g * x1, x3 - x0 + h * x3, x0], [y1 - y0 + g * y1, y3 - y0 + h * y3, y0], [g, h, 1.0]])


def dessine(pm, boite, Q, cadre, rect, n):
    """Le papier posé dans le rectangle rect = (s0, t0, s1, t1) du carré unité de Q : pour chaque pixel du cadre (X, Y, W, H),
    la moyenne de n x n points (couleur prémultipliée, couverture)."""
    X, Y, W, H = cadre
    Hi = np.linalg.inv(homographie(Q))
    o = (np.arange(n) + 0.5) / n
    gx, gy = (X + np.arange(W)[:, None] + o).ravel(), (Y + np.arange(H)[:, None] + o).ravel()
    PX, PY = np.meshgrid(gx, gy)
    v = np.tensordot(Hi, np.stack([PX, PY, np.ones_like(PX)]), 1)
    s0, t0, s1, t1 = rect
    s, t = (v[0] / v[2] - s0) / (s1 - s0), (v[1] / v[2] - t0) / (t1 - t0)
    dedans = (s >= 0) & (s < 1) & (t >= 0) & (t < 1)
    bx0, by0, bx1, by1 = boite
    u = np.clip(np.floor(bx0 + s * (bx1 - bx0)).astype(int), 0, pm.shape[1] - 1)
    w = np.clip(np.floor(by0 + t * (by1 - by0)).astype(int), 0, pm.shape[0] - 1)
    p = pm[w, u] * dedans[..., None]
    return p.reshape(H, n, W, n, 4).mean((1, 3))


def lab(c):
    c = np.asarray(c, float) / 255.0
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    xyz = c @ np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]]).T / np.array([0.9505, 1.0, 1.089])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def kmoyennes(C, k, tours=40):
    """k couleurs (moyennes sRGB de leurs pixels), réparties en Lab ; départ fixe : la plus sombre, puis la plus éloignée."""
    L = lab(C)
    G = [L[np.argmin(L[:, 0])]]
    for _ in range(k - 1):
        G.append(L[np.argmax(np.min(((L[:, None] - np.array(G)[None]) ** 2).sum(-1), 1))])
    G = np.array(G)
    for _ in range(tours):
        q = np.argmin(((L[:, None] - G[None]) ** 2).sum(-1), 1)
        G = np.array([L[q == j].mean(0) if (q == j).any() else G[j] for j in range(k)])
    q = np.argmin(((L[:, None] - G[None]) ** 2).sum(-1), 1)
    return np.array([C[q == j].mean(0) for j in range(k) if (q == j).any()])


def proche(C, P):
    return np.argmin(((lab(C)[:, None] - lab(P)[None]) ** 2).sum(-1), 1)


def couleurs(acc):
    A = acc[..., 3]
    return acc[..., :3] / np.maximum(A[..., None], 1e-9), A >= 0.5


def ecart(acc, franche, poids):
    """Ce qui est mêlé : l'écart (Lab) de chaque pixel de papier à la palette franche, pondéré ; et les bords à moitié couverts."""
    c, vu = couleurs(acc)
    d = np.min(((lab(c[vu])[:, None] - franche[None]) ** 2).sum(-1), 1)
    A = acc[..., 3]
    return (d * poids[vu]).sum() / poids[vu].sum() + 40.0 * (1 - np.abs(2 * A - 1)).mean()


def cale(pm, boite, Q, cadre, franche, parties):
    """Le rectangle du papier dans le cadre (à moins de 0,4 px de chaque bord) où ses parties sont le moins mêlées."""
    X, Y, W, H = cadre
    hq = np.mean([Q[3][1] - Q[0][1], Q[2][1] - Q[1][1]]); wq = np.mean([Q[1][0] - Q[0][0], Q[2][0] - Q[3][0]])
    # le poids de chaque pixel : 4 dans les parties (leur hauteur relative le long du quadrilatère), 1 ailleurs
    ty = (Y + np.arange(H) + 0.5 - np.mean([Q[0][1], Q[1][1]])) / hq
    poids = np.ones((H, W))
    for (a, b) in parties:
        poids[(ty >= a) & (ty <= b)] = 4.0
    meil = None
    for e0 in CALE:                                       # le haut et le bas d'abord
        for e1 in CALE:
            r = (0.0, e0 / hq, 1.0, 1 + e1 / hq)
            sc = ecart(dessine(pm, boite, Q, cadre, r, 16), franche, poids)
            if meil is None or sc < meil[0] - 1e-9:
                meil = (sc, r)
    _, (s0, t0, s1, t1) = meil
    for e0 in CALE:                                       # puis la gauche et la droite
        for e1 in CALE:
            r = (e0 / wq, t0, 1 + e1 / wq, t1)
            sc = ecart(dessine(pm, boite, Q, cadre, r, 16), franche, poids)
            if sc < meil[0] - 1e-9:
                meil = (sc, r)
    return meil[1]


def lumieres():
    """La lumière du soir sur le panneau (sans courant) et celle d'Ichiraku, en facteurs de l'albédo (0..1)."""
    unlit = np.asarray(Image.open(os.path.join(RACINE, 'assets', 'street_unlit.webp')).convert('RGB'), float)
    city = np.asarray(Image.open(os.path.join(RACINE, 'assets', 'layer_city_off.webp')).convert('RGB'), float)
    soir = np.median(unlit[590:635, 1133:1146].reshape(-1, 3), 0) / 255.0 / PANNEAU      # (le panneau peint, sans courant)
    lan = np.asarray(Image.open(os.path.join(RACINE, 'assets', 'ichiraku_lanterns.webp')).convert('RGBA'), float)
    c = lan[84:150, 15 * 48:15 * 48 + 38]; c = c[c[..., 3] > 200][:, :3].mean(0)           # la lanterne de gauche allumée (droite)
    v = (city - unlit)[595:640, 1152:1182].reshape(-1, 3).mean(0)                          # ce que la vitre de la porte ajoute
    teinte = 0.7 * c / c.max() + 0.3 * np.maximum(v, 0) / v.max()
    return soir, LAMPE * teinte / teinte.max()


def main():
    Q = lire_lb()
    xs, ys = [p[0] for p in Q], [p[1] for p in Q]
    X, Y = int(np.floor(min(xs))), int(np.floor(min(ys)))
    cadre = (X, Y, int(np.ceil(max(xs))) - X, int(np.ceil(max(ys))) - Y)
    W, H = cadre[2], cadre[3]
    soir, lampe = lumieres()
    cases, etoile = [], None
    for nom, f in AFFICHES:
        a = np.asarray(Image.open(os.path.join(SRC, f)).convert('RGB'), float)
        a, papier = detoure(a, nom)
        yy, xx = np.nonzero(papier)
        boite = (xx.min(), yy.min(), xx.max() + 1, yy.max() + 1)
        pm = np.dstack([a * papier[..., None], papier]).astype(np.float64)
        franche = lab(kmoyennes(a[papier][::7], 24))     # (ses couleurs pleines)
        r = cale(pm, boite, Q, cadre, franche, PARTIES[nom])
        acc = dessine(pm, boite, Q, cadre, r, N)
        c, vu = couleurs(acc)
        P = kmoyennes(c[vu], K); nk = len(P)
        ty = (np.arange(a.shape[0]) - boite[1]) / (boite[3] - boite[1])
        tr = []                                          # (chaque trait : ses pixels de la source, sa couleur, son seuil)
        for (_, f, (h0, h1), seuil) in TRAITS[nom]:
            m = f(a) & papier & ((ty >= h0) & (ty <= h1))[:, None]
            tr.append((np.dstack([np.repeat(m[..., None].astype(float), 3, 2), papier]), len(P), seuil))
            P = np.vstack([P, a[m].mean(0)])
        img = []
        for rr in (r, (r[0], r[1], r[2], r[1] + (r[3] - r[1]) * (1 - LEVE / H))):   # posée, soulevée
            acc = dessine(pm, boite, Q, cadre, rr, N)
            c, vu = couleurs(acc)
            q = np.zeros((H, W), int); q[vu] = proche(c[vu], P[:nk])
            for (pmt, j, seuil) in tr:
                q[vu & (dessine(pmt, boite, Q, cadre, rr, N)[..., 0] >= seuil)] = j
            img.append((q, vu))
        cases.append((nom, P, img))
        if nom == ETOILE[0]:
            Hm = homographie(Q); s0, t0, s1, t1 = r
            p = Hm @ [s0 + ETOILE[1] * (s1 - s0), t0 + ETOILE[2] * (t1 - t0), 1]
            etoile = [int(round(p[0] / p[2])), int(round(p[1] / p[2]))]
        print('%s : %d x %d px de source, posée à %s, %d couleurs' % (nom, boite[2] - boite[0], boite[3] - boite[1],
              ', '.join('%.4f' % v for v in r), len(np.unique(img[0][0][img[0][1]]))))
    atlas = np.zeros((2 * H, 4 * W, 4), np.uint8)
    for col, (k, j) in enumerate([(0, 0), (1, 0), (0, 1), (1, 1)]):        # la classique, le Gear 5, puis soulevées
        nom, P, img = cases[k]
        q, vu = img[j]
        sans = np.clip(np.round(P * soir), 0, 255)
        avec = np.clip(np.round(P * (soir + lampe)), 0, 255)
        for rang, pal in enumerate((sans, avec - sans)):                  # sans courant ; ce qu'Ichiraku y ajoute
            case = np.zeros((H, W, 4), np.uint8)
            case[vu, :3] = pal.astype(np.uint8)[q[vu]]; case[vu, 3] = 255
            atlas[rang * H:(rang + 1) * H, col * W:(col + 1) * W] = case
    Image.fromarray(atlas, 'RGBA').save(OUT, 'WEBP', lossless=True, quality=100, method=6, exact=True)
    lwp = {'box': [X, Y, W, H], 'cols': 4, 'star': etoile}
    t = open(JS, encoding='utf-8').read()
    ligne = 'const LWP = %s;' % json.dumps(lwp, separators=(',', ':'))
    t2, n = re.subn(r'const LWP = \{[^\n]*?\};', lambda m: ligne, t)
    assert n == 1, 'la ligne LWP de street.js'
    if t2 != t:
        open(JS, 'w', encoding='utf-8').write(t2)
    print(OUT, atlas.shape[1], 'x', atlas.shape[0], '; street.js :', ligne)


if __name__ == '__main__':
    main()
