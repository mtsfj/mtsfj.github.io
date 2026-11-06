#!/usr/bin/env python3
"""Les zombies de la horde et du bus, image par image, découpés dans les planches du propriétaire (tools/src/planches/).

    python3 tools/zombie_sheets.py                  (relit les planches, réécrit assets/horde_L0..L4.webp, assets/bus_zombies.webp,
                                                     bus_zombies_glow.webp, bus_zombies_spill.webp et les lignes ZH et BZ de
                                                     assets/street.js ; relancé, il écrit les mêmes octets)
    python3 tools/zombie_sheets.py --planches DIR   (en plus : une planche par zombie, toutes ses images découpées x4, ses
                                                     variantes comprises, et la planche des échelles)
    python3 tools/zombie_sheets.py --only horde     (horde | bus)

Les planches : cinq zombies (01 chemise blanche, 02 veste brune, 03 salopette bleue, 04 robe claire, 05 tenue bleue), trois
planches chacun, en deux versions (v1, v2), 1536 x 1024 sur blanc :
  zombie_NN_horde         rangée 1 : la marche vue de dos (8) ; rangée 2 : touché de face, rejeté en arrière (2), les genoux
                          qui lâchent (2), la chute en avant, face contre terre (2, la dernière à plat).
  zombie_NN_course        rangée 1 : la course de profil vers la droite (8) ; rangée 2 : le saut en courant sur un rebord haut
                          (accroupi, l'élan, en l'air, la prise, le rétablissement, accroupi dessus : 8) ; rangée 3 : vu de dos,
                          le saut pour attraper quelque chose à hauteur de tête, pendu, qui tire (6).
  zombie_NN_toit_fenetre  rangée 1 : accroupi sur le toit du bus, de profil vers la droite, qui se tient et tangue, se dresse et
                          griffe l'air (8) ; rangée 2 : vu de dos à une fenêtre, la planche clouée qu'il agrippe, arrache et jette
                          en arrière, puis il griffe la vitre et se retourne (8).
Le choix des versions, rangée par rangée : CHOIX (et pourquoi).

Le chemin, pour chaque zombie :
- Le détourage : le blanc du fond pris depuis les bords (à 244 et plus, presque gris), les poches de blanc fermées par la figure
  (entre un bras et le corps) ôtées, puis le liseré : un pixel du bord qui n'est qu'un mélange de la figure et du blanc (son
  alpha estimé contre la couleur de la figure juste dedans, sous 1/2, et plus clair qu'elle) part, trois passes ; une chemise
  pâle reste à elle (sa couleur est la sienne, pas un mélange).
- Les images : les taches de la figure, rangée par rangée ; deux images collées (un bras qui touche le voisin) coupées à la
  colonne la plus creuse ; les bouts détachés (une mèche, la planche en l'air) rendus à l'image la plus proche. Le compte
  de chaque rangée est vérifié.
- L'échelle : une par zombie et par vue, d'après sa taille (TAILLE, en mètres) : la marche de dos (la horde), le zombie debout
  de dos au bus (sa planche, les deux dernières images) et le premier saut de dos (la course), mesurés du haut de la tête
  (au milieu du corps : pas les mains levées) à la semelle ; la course de profil et le toit à l'échelle de leur planche.
  Aucune image ne change de taille : une échelle pour toute une planche.
- La ligne du sol : chaque image posée sur sa semelle la plus basse (la marche, la course, le toit), au milieu des jambes de
  dos, au milieu du corps de profil, au milieu de ce qui touche le sol pour la chute ; les sauts posés par leurs mains (la
  prise) ou par le code (leur courbe).
- La réduction : par majorité, jamais de filtre : chaque pixel prend la famille de couleur (k-moyennes en OKLab sur tout le
  zombie) qui couvre le plus de son empreinte, sa couleur la moyenne de cette famille dans l'empreinte ; opaque quand la
  figure couvre la moitié de l'empreinte au moins. La semelle et l'ancre tombent sur des bords de pixels entiers.
- La nuit (NUIT) : les planches sont d'un ton de plein jour ; chaque silhouette (toutes ses images ensemble) ramenée aux
  valeurs des figures que la rue a déjà la nuit (ses p5, p50, p95 de luminance : la horde 6/22/56, le bus 22/40/74), une
  courbe en trois morceaux, chaque couleur gardant sa teinte.
- Le grain : tools/regrain.py (ses fonctions : regrain_group), un personnage par silhouette (toutes ses images et ses tailles
  ensemble : ses familles ne changent pas d'une image à l'autre), ses cibles de la rue (la horde, le bus).
- Les variantes de la horde (VARIANTES) : les vêtements et les cheveux recolorés (la teinte et la saturation d'une plage de
  couleurs, dans une zone du corps), la peau et l'ombre gardées : douze silhouettes pour cinq zombies.
- La planche (zombie_NN_toit_fenetre, rangée 2) : le bois repéré dans ses images (sa teinte, d'un seul tenant, allongé), ôté de
  la figure ; sa place et son angle par image (le centre, l'axe) donnent la trace que suit la planche du code
  (assets/bus_plank.webp) : clouée, dans ses mains, lancée, c'est toujours la même.

Ce qui est écrit :
- la horde : horde_L0..L4.webp, à ses cinq tailles d'avant (64, 100, 150, 290 et 42 px pour 1,76 m), et la ligne ZH (les
  images de chaque silhouette par taille : [x, y, l, h, ax, ay], l'ancre sur la semelle) ;
- le bus : bus_zombies.webp (à 41 m, 23,4 px/m), bus_zombies_glow.webp (la lumière du salon du bus sur eux : leurs bords,
  calque additif), bus_zombies_spill.webp (R : le côté gauche, l'orange de l'oden ; G : le côté droit, le rouge de l'auvent)
  et la ligne BZ (les images par zombie et par mouvement, les yeux, la trace de la planche, les foulées).
Il faut Pillow, numpy, scipy.
"""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')     # (les sommes dans le même ordre : les mêmes octets à chaque fois)
os.environ.setdefault('OMP_NUM_THREADS', '1')
import argparse
import json
import re
import sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as nd
from scipy import sparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PL = os.path.join(ROOT, 'tools', 'src', 'planches')
ASSETS = os.path.join(ROOT, 'assets')
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import regrain as RG                                  # noqa: E402  (ses couleurs, ses familles, son grain)

LUMA = np.array([0.299, 0.587, 0.114])
ZN = ['01', '02', '03', '04', '05']
NOMS = {'01': 'chemise blanche', '02': 'veste brune', '03': 'salopette bleue', '04': 'robe claire', '05': 'tenue bleue'}
ATTENDU = {'horde': [8, 6], 'course': [8, 8, 6], 'toit_fenetre': [8, 8]}
# la taille de chacun, debout (m) : la horde la dessine sur ses niveaux de 1,76 m ; un plus petit y est plus petit
TAILLE = {'01': 1.76, '02': 1.72, '03': 1.78, '04': 1.64, '05': 1.66}
HN = 1.76                                             # (la taille nominale des niveaux de la horde)
NIVEAUX = [64, 100, 150, 290, 42]                     # (horde_L0..L4 : leur hauteur pour 1,76 m ; l'ordre de street.js)
CF, CEYE, CHZ = 959.5, 1.41, 615.0                    # (la caméra B de street.js)
BUS_ROW = 648.0                                       # (le pied du bus : sa voie, 41 m)
BUS_PPM = (BUS_ROW - CHZ) / CEYE                      # (23,4 px par mètre à la profondeur du bus)


# ---- le choix des versions, rangée par rangée (regardées à leur taille dans la rue : 100 px pour la horde, 41 px au bus) :
# la horde : v2 pour 01, 03, 04, 05 (des blocs plus nets, une marche d'une taille plus égale d'image en image : 01 v1 va de 373 à
# 397 px, v2 tient sa tête ; 05 v1 est sourd, bleu sur bleu), v1 pour 02 (sa marche et son rejet en arrière plus lisibles) ;
# la course : v1 pour 01 (en v2 les deux dernières foulées sont des fentes, les bras jetés à travers l'image voisine) et 02,
# v2 pour 03, 04, 05 (leur premier saut de dos part debout, les deux pieds au sol ; en v1 il part déjà en l'air) ; le toit et
# la fenêtre : v2 pour 01 et 02 (accroupis quatre images, tanguant, avant de se dresser), v1 pour 03, 04, 05 (en v2 la
# dernière image du toit retombe ou grandit d'un coup). Une planche entière par version, jamais des images mêlées : l'échelle
# est celle d'une planche.
CHOIX = {
    '01': {'horde': ['v2', 'v2'], 'course': ['v1', 'v1', 'v1'], 'toit_fenetre': ['v2', 'v2']},
    '02': {'horde': ['v1', 'v1'], 'course': ['v1', 'v1', 'v1'], 'toit_fenetre': ['v2', 'v2']},
    '03': {'horde': ['v2', 'v2'], 'course': ['v2', 'v2', 'v2'], 'toit_fenetre': ['v1', 'v1']},
    '04': {'horde': ['v2', 'v2'], 'course': ['v2', 'v2', 'v2'], 'toit_fenetre': ['v1', 'v1']},
    '05': {'horde': ['v2', 'v2'], 'course': ['v2', 'v2', 'v2'], 'toit_fenetre': ['v1', 'v1']},
}


# ---- couleurs
def oklab(rgb):
    return RG.oklab(np.asarray(rgb, float))


def to_rgb(lab):
    return np.clip(np.round(RG.from_oklab(lab)), 0, 255)


# ---- le détourage
def detoure(rgb):
    """la figure sur le blanc : le fond pris depuis les bords, tout blanc pris dans la figure ôté (les poches entre un bras et
    le corps, entre les mèches), puis le liseré de mélange"""
    a = rgb.astype(float)
    mn, mx = a.min(2), a.max(2)
    near = (mn >= 244) & (mx - mn <= 10)
    lab, n = nd.label(near)
    border = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    border = border[border > 0]
    fig = ~np.isin(lab, border)
    fig &= ~((mn >= 240) & (mx - mn <= 12))          # (aucun blanc dans les figures : ni chemise ni robe n'y montent)
    L = a @ LUMA
    for _ in range(4):                                # (le liseré : l'alpha d'un pixel du bord contre la figure juste dedans,
        bg = ~fig                                     #  la luminance moyenne des pixels à 3 px du fond ou plus, autour de lui)
        dedans = (nd.distance_transform_edt(fig) >= 3).astype(float)
        bord = fig & nd.binary_dilation(bg)
        Lref = np.full(L.shape, np.nan)
        for k in (7, 13):
            S = nd.uniform_filter(L * dedans, k)
            N = nd.uniform_filter(dedans, k)
            Lref = np.where(np.isnan(Lref) & (N > 1e-6), S / np.maximum(N, 1e-9), Lref)
        ok = ~np.isnan(Lref)
        Lr = np.where(ok, Lref, 0)
        al = (255.0 - L) / np.maximum(255.0 - Lr, 1.0)
        ote = bord & ok & (L > Lr + 4) & (al < 0.6)
        if not ote.any():
            break
        fig &= ~ote
    l2, n2 = nd.label(fig, structure=np.ones((3, 3)))
    if n2:                                            # (les poussières : moins de 6 px)
        sz = np.bincount(l2.ravel())
        keep = sz >= 6
        keep[0] = False
        fig = keep[l2]
    return fig


# ---- les images
def images(fig, attendu):
    """les images d'une planche, rangée par rangée : [{'box': (x0, y0, x1, y1), 'm': masque de la boîte}]"""
    lab, n = nd.label(nd.binary_dilation(fig, iterations=1), structure=np.ones((3, 3)))
    lab = np.where(fig, lab, 0)
    area = np.bincount(lab.ravel())
    objs = nd.find_objects(lab)
    comps = [(i + 1, sl) for i, sl in enumerate(objs) if sl is not None and area[i + 1] > 0]
    top = np.sort(area[1:])[::-1][:sum(attendu)]
    thr = 0.35 * np.median(top)
    big = sorted([c for c in comps if area[c[0]] >= thr], key=lambda c: (c[1][0].start + c[1][0].stop) / 2)
    small = [c for c in comps if area[c[0]] < thr]
    rows = []
    for c in big:
        cy = (c[1][0].start + c[1][0].stop) / 2
        if rows and abs(cy - np.mean([(q[1][0].start + q[1][0].stop) / 2 for q in rows[-1]])) < 150:
            rows[-1].append(c)
        else:
            rows.append([c])
    if len(rows) != len(attendu):
        raise SystemExit('rangées : %d trouvées, %d attendues' % (len(rows), len(attendu)))
    fr = []
    for ri, r in enumerate(rows):
        r.sort(key=lambda c: c[1][1].start)
        rr = [{'ids': [i], 'x': (sl[1].start, sl[1].stop), 'box': (sl[1].start, sl[0].start, sl[1].stop, sl[0].stop)} for i, sl in r]
        while len(rr) < attendu[ri]:                 # (deux images collées : coupées à la colonne la plus creuse)
            j = int(np.argmax([f['box'][2] - f['box'][0] for f in rr]))
            f = rr[j]
            x0, y0, x1, y1 = f['box']
            col = np.isin(lab[y0:y1, x0:x1], f['ids']).sum(0).astype(float)
            w = x1 - x0
            cut = int(w * 0.3) + int(np.argmin(col[int(w * 0.3):int(w * 0.7)]))
            rr[j:j + 1] = [dict(f, x=(x0, x0 + cut), box=(x0, y0, x0 + cut, y1)), dict(f, x=(x0 + cut, x1), box=(x0 + cut, y0, x1, y1))]
        if len(rr) != attendu[ri]:
            raise SystemExit('rangée %d : %d images, %d attendues' % (ri + 1, len(rr), attendu[ri]))
        fr.append(rr)
    allf = [f for r in fr for f in r]
    for i, sl in small:                               # (un bout détaché : à l'image la plus proche, en largeur d'abord)
        cx, cy = (sl[1].start + sl[1].stop) / 2, (sl[0].start + sl[0].stop) / 2
        f = min(allf, key=lambda f: 3 * max(0, f['box'][0] - cx, cx - f['box'][2]) + max(0, f['box'][1] - cy, cy - f['box'][3]))
        f.setdefault('extra', []).append(i)
    out = []
    for r in fr:
        rr = []
        for f in r:
            m = np.isin(lab, f['ids'])
            if f['x'] != (None, None):
                cm = np.zeros_like(m)
                cm[:, f['x'][0]:f['x'][1]] = True
                m &= cm
            ex = np.isin(lab, f.get('extra', [])) if f.get('extra') else np.zeros_like(m)
            m |= ex
            ys, xs = np.nonzero(m)
            x0, y0, x1, y1 = int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1
            rr.append({'box': (x0, y0, x1, y1), 'm': m[y0:y1, x0:x1], 'ex': ex[y0:y1, x0:x1]})
        out.append(rr)
    return out


_CACHE = {}


def planche(n, kind, v):
    """une planche : son RVB, sa figure, ses images"""
    k = (n, kind, v)
    if k not in _CACHE:
        rgb = np.asarray(Image.open(os.path.join(PL, 'zombie_%s_%s_%s.png' % (n, kind, v))).convert('RGB'))
        fig = detoure(rgb)
        _CACHE[k] = dict(rgb=rgb, fig=fig, rows=images(fig, ATTENDU[kind]))
    return _CACHE[k]


def rangee(n, kind, r):
    """les images de la rangée r (0, 1, 2) de la planche kind du zombie n, dans la version choisie : [(rgb, masque, boîte)]"""
    v = CHOIX[n][kind][r]
    P = planche(n, kind, v)
    out = []
    for f in P['rows'][r]:
        x0, y0, x1, y1 = f['box']
        out.append(dict(rgb=P['rgb'][y0:y1, x0:x1], m=f['m'].copy(), ex=f['ex'], box=f['box'], v=v))
    return out


# ---- les mesures d'une image (px de la planche, dans sa boîte)
def bas(m):
    return int(np.nonzero(m.any(1))[0].max()) + 1    # (le bord sous la semelle la plus basse)


def milieu_bande(m, y0, y1, how='median'):
    y0, y1 = max(0, int(y0)), min(m.shape[0], int(y1))
    ys, xs = np.nonzero(m[y0:y1])
    if not len(xs):
        return m.shape[1] / 2
    return float(np.median(xs)) + 0.5 if how == 'median' else (xs.min() + xs.max() + 1) / 2


def haut_tete(m, cx, hs):
    """le haut de la tête : le premier pixel dans la bande du milieu du corps (± 6 % de la taille debout)"""
    a, b = int(round(cx - 0.06 * hs)), int(round(cx + 0.06 * hs))
    ys = np.nonzero(m[:, max(0, a):max(1, b)].any(1))[0]
    return int(ys.min()) if len(ys) else 0


def contact(m, hs, tol=0.03):
    """le milieu de ce qui touche le sol : les colonnes dont le bas est à tol x la taille debout du bas de l'image"""
    H, W = m.shape
    has = m.any(0)
    low = np.where(has, H - 1 - np.argmax(m[::-1], 0), -1)
    yb = low.max()
    cols = np.nonzero(has & (low >= yb - tol * hs))[0]
    return float(np.median(cols)) + 0.5


# ---- les familles de vote (k-moyennes en OKLab, déterministes) et la réduction par majorité
def kmoy(X, K, seed=11, iters=30, w=None):
    """k-moyennes pondérées, départ k-means++ déterministe, par paquets (X : N x 3)"""
    rng = np.random.default_rng(seed)
    w = np.ones(len(X)) if w is None else w
    C = [X[int(np.argmax(w))]]
    d2 = ((X - C[0]) ** 2).sum(1)
    for _ in range(1, K):
        p = d2 * w
        C.append(X[int(rng.choice(len(X), p=p / p.sum()))])
        d2 = np.minimum(d2, ((X - C[-1]) ** 2).sum(1))
    C = np.array(C)
    for _ in range(iters):
        lab = proche(X, C)
        S = np.zeros_like(C)
        np.add.at(S, lab, X * w[:, None])
        n = np.bincount(lab, weights=w, minlength=len(C))
        C2 = np.where(n[:, None] > 0, S / np.maximum(n, 1e-9)[:, None], C)
        if np.abs(C2 - C).max() < 1e-7:
            C = C2
            break
        C = C2
    return C


def proche(X, C, chunk=200000):
    out = np.empty(len(X), np.int32)
    for i in range(0, len(X), chunk):
        out[i:i + chunk] = ((X[i:i + chunk, None, :] - C[None]) ** 2).sum(2).argmin(1)
    return out


def poids(n_src, a0, scale, n_out, off):
    """la part de chaque pixel de la planche (0..n_src) dans chaque pixel de sortie : le pixel de sortie i couvre
    [a0 + (i - off) / scale, a0 + (i + 1 - off) / scale] (en px de la planche) ; une matrice creuse n_out x n_src"""
    rows, cols, vals = [], [], []
    for i in range(n_out):
        u0, u1 = a0 + (i - off) / scale, a0 + (i + 1 - off) / scale
        for x in range(max(0, int(np.floor(u0))), min(n_src, int(np.ceil(u1)))):
            ov = min(u1, x + 1) - max(u0, x)
            if ov > 1e-9:
                rows.append(i)
                cols.append(x)
                vals.append(ov)
    return sparse.csr_matrix((vals, (rows, cols)), shape=(n_out, n_src))


def majorite(lab, rgb, m, ax, ay, scale):
    """une image réduite par majorité : lab (familles, -1 hors figure), son ancre (ax, ay) en px de la planche (ay : le bord
    sous la semelle), scale (px de sortie par px de la planche). L'ancre tombe sur un bord de pixel entier (AX, AY) de la
    sortie. Rend (RGBA, AX, AY)."""
    h, w = m.shape
    AX, AY = int(np.ceil(ax * scale - 1e-9)), int(np.ceil(ay * scale - 1e-9))
    W2 = AX + int(np.ceil((w - ax) * scale - 1e-9))
    H2 = AY + int(np.ceil((h - ay) * scale - 1e-9))
    Wy = poids(h, ay, scale, H2, AY)
    Wx = poids(w, ax, scale, W2, AX).T.tocsc()
    area = 1.0 / scale ** 2
    ks = np.unique(lab[m])
    best = np.zeros((H2, W2))
    bk = np.full((H2, W2), -1)
    tot = np.zeros((H2, W2))
    col = np.zeros((H2, W2, 3))
    src = rgb.astype(float)
    for k in ks:
        Mk = ((lab == k) & m).astype(float)
        Ck = np.asarray((Wy @ Mk) @ Wx)
        tot += Ck
        upd = Ck > best + 1e-12
        if upd.any():
            best = np.where(upd, Ck, best)
            bk = np.where(upd, k, bk)
            for c in range(3):
                Sc = np.asarray((Wy @ (Mk * src[..., c])) @ Wx)
                col[..., c] = np.where(upd, Sc / np.maximum(Ck, 1e-12), col[..., c])
    out = np.zeros((H2, W2, 4), np.uint8)
    op = tot >= 0.5 * area - 1e-9
    out[..., :3] = np.clip(np.round(col), 0, 255).astype(np.uint8)
    out[..., 3] = np.where(op, 255, 0)
    out[~op, :3] = 0
    return out, AX, AY


def familles_vote(frames, K=22):
    """les familles de vote d'un zombie : k-moyennes sur un échantillon régulier de tous ses pixels (OKLab)"""
    X = np.concatenate([oklab(f['rgb'][f['m']]) for f in frames])
    step = max(1, len(X) // 120000)
    C = kmoy(X[::step], K)
    return C


def haut_debout(f):
    """du haut de la tête (au milieu du corps) à la semelle, en px de la planche"""
    m = f['m']
    H = m.shape[0]
    yb = bas(m)
    cx = milieu_bande(m, yb - 0.55 * H, yb - 0.4 * H)
    return yb - haut_tete(m, cx, H)


def torse(f, a=0.30, b=0.42):
    """la largeur du torse de dos, bras levés : la course de pixels qui tient le milieu du corps, entre 30 et 42 % de la
    hauteur sous le haut de la tête (sous les aisselles)"""
    m = f['m']
    H = m.shape[0]
    yb = bas(m)
    cx = int(milieu_bande(m, yb - 0.55 * H, yb - 0.4 * H))
    top = haut_tete(m, cx, H)
    hs = yb - top
    ws = []
    for y in range(int(top + a * hs), int(top + b * hs)):
        row = m[y]
        if not row[cx]:
            continue
        l = r = cx
        while l > 0 and row[l - 1]:
            l -= 1
        while r < len(row) - 1 and row[r + 1]:
            r += 1
        ws.append(r - l + 1)
    return float(np.median(ws))


def echelles(n):
    """px de la planche par mètre, par planche : la horde par sa marche (le haut de la tête à 0,98 de la taille : le dos
    voûté) ; le toit par le zombie debout de dos (les deux dernières images de la fenêtre, 0,98) et dressé de profil (la
    dernière du toit, sa taille), la moyenne des deux ; la course par le toit, au rapport de leurs torses de dos bras levés
    (la planche agrippée, le zombie pendu)"""
    T = TAILLE[n]
    h = float(np.median([haut_debout(f) for f in rangee(n, 'horde', 0)])) / (0.98 * T)
    t2 = rangee(n, 'toit_fenetre', 1)
    t1 = rangee(n, 'toit_fenetre', 0)
    t = 0.5 * (float(np.median([haut_debout(f) for f in t2[6:8]])) / (0.98 * T) + t1[7]['m'].shape[0] / T)
    rap = float(np.median([torse(f) for f in t2[:2]])) / float(np.median([torse(f) for f in rangee(n, 'course', 2)[1:6]]))
    e = {'horde': h, 'toit_fenetre': t, 'course': t / rap}
    for k, c in CORR.get(n, {}).items():
        e[k] *= c
    return e


CORR = {'01': {'course': 1.10}, '04': {'course': 1.12}}   # (à l'œil : la course de 01 et 04 dessinée plus petite que ses autres
                                                      #  planches, les têtes et les corps côte à côte à la même échelle)


# ---- les ancres (px de la planche, dans la boîte de l'image) : (ax, ay), ay le bord sous la semelle la plus basse
def bande(m, yb, hs, a, b):
    return milieu_bande(m, yb - b * hs, yb - a * hs)


def ancre(kind, r, k, f, hs):
    m = f['m']
    yb = bas(m)
    if kind == 'horde' and (r == 0 or k < 2):         # (la marche, rejeté en arrière : le milieu des hanches)
        return bande(m, yb, hs, 0.50, 0.62), yb
    if kind == 'horde':                               # (les genoux, la chute : le milieu de ce qui touche le sol)
        return contact(m, hs), yb
    if kind == 'course' and r < 2:                    # (la course, le saut sur le toit, de profil : les hanches penchées)
        return bande(m, yb, hs, 0.30, 0.45), yb
    if kind == 'course':                              # (le saut de dos : le milieu des hanches)
        return bande(m, yb, hs, 0.42, 0.55), yb
    if r == 0:                                        # (le toit : ses pieds, qui ne bougent pas)
        return contact(m, hs), yb
    return bande(m, yb, hs, 0.50, 0.62), yb           # (à la fenêtre, de dos : les hanches)


def mains(m, hs):
    """les mains en haut (la prise) : le milieu de ce qui est à 5 % de la taille du haut de l'image, et ce haut"""
    ys, xs = np.nonzero(m)
    t = ys.min()
    sel = ys < t + 0.05 * hs
    return (xs[sel].min() + xs[sel].max() + 1) / 2, float(t)


# ---- la planche dans les mains (zombie_NN_toit_fenetre, rangée 2)
BOIS = dict(h=(40.0, 80.0), c=0.03, l=0.38, dens=0.45)   # (le bois des planches : sa teinte OKLab (degrés), sa saturation, sa
                                                          #  clarté ; et sa densité sur 9 x 9 px : la planche, pas des grains)
BOIS_Z = {'03': dict(c=0.042)}                            # (03 : sa chemise beige est presque de la couleur du bois, moins saturée)


def planche_bois(n, fr, hs):
    """repère la planche dans les images de la fenêtre (zombie_NN_toit_fenetre, rangée 2, ses six premières images) : les
    pixels couleur de bois (BOIS : une teinte orangée, assez saturée, assez claire ; ni la peau grise, ni les vêtements, ni
    la veste rouille de 02, plus sombre), là où ils sont denses (une moyenne sur 9 x 9 px), dans la moitié haute de la
    figure (pas les chaussures) ; leurs taches allongées (au moins le quart de la plus grande) : leur centre, leur axe, leur
    longueur, leur épaisseur. Ôtée de la figure : dans le rectangle de la planche, ce qui est plus près du bois de l'image
    que du reste de la figure (ses tons, k-moyennes), puis les bouts qui s'en trouvent détachés (les clous). Rend la trace :
    par image, [état (1 tenue, 2 lancée, 0 rien), cx, cy, angle, longueur, épaisseur] (px de la planche, dans la boîte)."""
    B = dict(BOIS, **BOIS_Z.get(n, {}))
    trace = []
    for i, f in enumerate(fr):
        if i >= 6 or (trace and trace[-1][0] == 2) or (len(trace) > 1 and trace[-1][0] == 0 and trace[-2][0]):
            trace.append([0, 0, 0, 0, 0, 0])          # (après le jet, plus de planche)
            continue
        X = oklab(f['rgb'])
        Cc = np.hypot(X[..., 1], X[..., 2])
        h = np.degrees(np.arctan2(X[..., 2], X[..., 1])) % 360
        m = f['m']
        bois = m & (Cc > B['c']) & (h > B['h'][0]) & (h < B['h'][1]) & (X[..., 0] > B['l'])
        wood = (nd.uniform_filter(bois.astype(float), 9) > B['dens']) & m
        t = np.nonzero(m.any(1))[0].min()
        wood[int(t + 0.5 * hs):] = False
        l, nn = nd.label(wood, structure=np.ones((3, 3)))
        if not nn:
            trace.append([0, 0, 0, 0, 0, 0])
            continue
        sz = np.bincount(l.ravel())
        sz[0] = 0
        comp = np.isin(l, np.nonzero(sz >= max(40, 0.25 * sz.max()))[0])
        ys, xs = np.nonzero(comp)
        if len(xs) < 0.002 * hs * hs:                 # (trop peu : pas de planche dans cette image)
            trace.append([0, 0, 0, 0, 0, 0])
            continue
        cx, cy = xs.mean() + 0.5, ys.mean() + 0.5
        ev, evec = np.linalg.eigh(np.cov(np.stack([xs - cx, ys - cy])))
        ux, uy = evec[:, 1]
        if ux < 0:
            ux, uy = -ux, -uy
        ang = float(np.arctan2(uy, ux)) % np.pi
        u = (xs + 0.5 - cx) * ux + (ys + 0.5 - cy) * uy
        v = -(xs + 0.5 - cx) * uy + (ys + 0.5 - cy) * ux
        L, E = float(u.max() - u.min()), float(np.percentile(v, 97) - np.percentile(v, 3))
        if L < 2.5 * E:                               # (pas allongée : pas une planche)
            trace.append([0, 0, 0, 0, 0, 0])
            continue
        lancee = bool(f['ex'][comp].mean() > 0.5)     # (le bout lancé, dessiné à part de la figure)
        trace.append([2 if lancee else 1, cx, cy, ang, L, E])
        H, W = m.shape
        yy, xx = np.mgrid[0:H, 0:W]
        uu = (xx + 0.5 - cx) * ux + (yy + 0.5 - cy) * uy
        vv = -(xx + 0.5 - cx) * uy + (yy + 0.5 - cy) * ux
        rect = m & (uu >= u.min() - 3) & (uu <= u.max() + 3) & (np.abs(vv) <= E / 2 + 3)
        Cw = kmoy(X[comp], 6, seed=3)                 # (les tons du bois, et ceux du reste de la figure)
        Co = kmoy(X[m & ~nd.binary_dilation(rect, iterations=2)][::2], 14, seed=3)
        Xr = X[rect]
        dw = ((Xr[:, None] - Cw[None]) ** 2).sum(2).min(1)
        do = ((Xr[:, None] - Co[None]) ** 2).sum(2).min(1)
        ote = np.zeros_like(m)
        ote[rect] = dw < do
        f['m'] &= ~(ote | comp | (f['ex'] & rect if lancee else False))
        l2, n2 = nd.label(f['m'], structure=np.ones((3, 3)))
        if n2 > 1:                                    # (les clous, un éclat : détachés, près de la planche)
            s2 = np.bincount(l2.ravel())
            s2[0] = 0
            big = int(s2.argmax())
            small = np.isin(l2, np.nonzero((s2 > 0) & (s2 < 0.02 * s2[big]))[0])
            f['m'] &= ~(small & nd.binary_dilation(rect, iterations=4))
    return trace


# ---- les yeux (de profil) : la tête (la figure ouverte d'un disque : sans les bras, les mèches, les doigts), sa partie
# avant, un peu au-dessus de son milieu ; ou, s'il est peint, l'orange de l'œil dans la tête
def oeil(f, hs):
    m = f['m']
    r = max(2, int(round(0.035 * hs)))
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
    o = nd.binary_opening(m, structure=(xx * xx + yy * yy) <= r * r)
    if not o.any():
        return None
    ys = np.nonzero(o.any(1))[0]
    t = ys.min()
    band = o.copy()
    band[int(t + 0.13 * hs):] = False
    l, nn = nd.label(band)
    if not nn:
        return None
    sz = np.bincount(l.ravel())
    sz[0] = 0
    head = l == int(sz.argmax())
    hy, hx = np.nonzero(head)
    x0, x1, y0, y1 = hx.min(), hx.max() + 1, hy.min(), hy.max() + 1
    ex, ey = x1 - 0.30 * (x1 - x0), y0 + 0.45 * (y1 - y0)
    X = oklab(f['rgb'])                                # (l'œil peint : un orange franc dans la moitié avant de la tête)
    sc = X[..., 1] + 0.5 * X[..., 2]
    ok = head & m & (X[..., 0] > 0.35) & (np.hypot(X[..., 1], X[..., 2]) > 0.07) & (xx_cols(m) > (x0 + x1) / 2)
    if ok.sum() >= 3:
        s = np.where(ok, sc, -9)
        idx = np.argsort(s.ravel())[-4:]
        py, px = np.unravel_index(idx, s.shape)
        if s[py, px].min() > 0.06:
            ex, ey = px.mean() + 0.5, py.mean() + 0.5
    return float(ex), float(ey)


def xx_cols(m):
    return np.broadcast_to(np.arange(m.shape[1])[None, :], m.shape)


# ---- les variantes de la horde : les vêtements recolorés (la peau, les cheveux et l'ombre gardés)
# une règle : (teinte min, teinte max (degrés OKLab), saturation min, clarté min, clarté max, rotation de teinte, facteur de
# saturation, décalage de clarté) ; une marge douce de 8 degrés et de 0,006 de saturation
VARIANTES = [
    ('01', '01b', [(220, 290, 0.012, 0.0, 1.0, 170, 0.85, 0.0)]),                          # (le jean en toile brune)
    ('02', '02b', [(25, 50, 0.009, 0.0, 1.0, 105, 0.8, -0.02)]),                            # (la veste et le pantalon verts, tout d'un ton)
    ('03', '03b', [(235, 285, 0.025, 0.0, 1.0, 165, 0.75, 0.0)]),                           # (la salopette en toile kaki)
    ('04', '04b', [(255, 305, 0.018, 0.36, 1.0, -105, 1.5, -0.03)]),                        # (la robe vert d'eau sombre ; ses cheveux noirs gardés)
    ('05', '05b', [(235, 265, 0.025, 0.0, 1.0, -150, 0.8, 0.0)]),                           # (la combinaison olive)
    ('01', '01c', [(220, 290, 0.012, 0.0, 1.0, 0, 0.25, -0.08),                             # (le jean noir,
                   (0, 360, 0.0, 0.62, 1.0, 0, 0.0, -0.03)]),                               #  la chemise grise)
    ('03', '03c', [(235, 285, 0.025, 0.0, 1.0, 108, 0.9, -0.04)]),                          # (la salopette bordeaux)
]


def recolore(rgba, regles):
    out = rgba.copy()
    m = rgba[..., 3] > 0
    if not m.any():
        return out
    X = oklab(rgba[..., :3][m].astype(float))
    L, a, b = X[:, 0], X[:, 1], X[:, 2]
    C = np.hypot(a, b)
    h = np.degrees(np.arctan2(b, a)) % 360
    for (h0, h1, c0, l0, l1, dh, kc, dl) in regles:
        if h1 - h0 >= 360:
            wh = np.ones_like(h)
        else:
            d0 = (h - h0 + 180) % 360 - 180
            d1 = (h1 - h + 180) % 360 - 180
            wh = np.clip(np.minimum(d0, d1) / 8 + 0.5, 0, 1)
        w = wh * np.clip((C - c0) / 0.006 + 0.5, 0, 1) * np.clip((L - l0) / 0.02 + 0.5, 0, 1) * np.clip((l1 - L) / 0.02 + 0.5, 0, 1)
        hn = np.radians(h + w * dh)
        Cn = C * (1 + w * (kc - 1))
        L = L + w * dl
        a, b = Cn * np.cos(hn), Cn * np.sin(hn)
        C, h = np.hypot(a, b), np.degrees(np.arctan2(b, a)) % 360
    out[..., :3][m] = to_rgb(np.stack([L, a, b], 1)).astype(np.uint8)
    return out


# ---- la nuit : les planches sont dessinées en plein jour, d'un ton moyen ; chaque silhouette ramenée aux valeurs de la rue la
# nuit (ses p5, p50 et p95 de luminance sur ceux de la horde et des zombies du bus d'avant, que la rue a déjà : la horde
# 6/22/56, le bus 22/40/74), par une courbe en trois morceaux, chaque couleur gardant sa teinte (ses trois canaux à la même
# échelle) : des figures sombres et franches devant la rue, plus de silhouettes grises et plates
NUIT = {'horde': (6.0, 22.0, 56.0), 'bus': (22.0, 40.0, 74.0)}


def nuit(imgs, cible):
    m = np.concatenate([i[..., 3].ravel() > 0 for i in imgs])
    L = np.concatenate([(i[..., :3].reshape(-1, 3).astype(float) @ LUMA) for i in imgs])[m]
    p = np.percentile(L, [5, 50, 95])
    xs = [0.0, p[0], p[1], p[2], 255.0]
    ys = [0.0, cible[0], cible[1], cible[2], cible[2] + 0.3 * (255.0 - p[2])]
    out = []
    for i in imgs:
        a = i.copy()
        mm = a[..., 3] > 0
        rgb = a[..., :3][mm].astype(float)
        Li = rgb @ LUMA
        k = np.interp(Li, xs, ys) / np.maximum(Li, 1e-6)
        a[..., :3][mm] = np.clip(np.round(rgb * k[:, None]), 0, 255).astype(np.uint8)
        out.append(a)
    return out


# ---- l'atlas : des étagères, les plus hautes d'abord
def range_atlas(tiles, W=2048, gap=1):
    order = sorted(range(len(tiles)), key=lambda i: (-tiles[i].shape[0], -tiles[i].shape[1], i))
    pos = [None] * len(tiles)
    x = y = sh = 0
    for i in order:
        h, w = tiles[i].shape[:2]
        if x + w > W:
            x, y, sh = 0, y + sh + gap, 0
        pos[i] = (x, y)
        x += w + gap
        sh = max(sh, h)
    H = y + sh
    a = np.zeros((H, W, 4), np.uint8)
    for i, t in enumerate(tiles):
        x, y = pos[i]
        a[y:y + t.shape[0], x:x + t.shape[1]] = t
    return a, pos


def coupe(n, kind, r, e, plank=False):
    """les images d'une rangée avec leurs ancres (px de la planche) ; plank : la planche repérée et ôtée (sa trace)"""
    fr = rangee(n, kind, r)
    hs = TAILLE[n] * e[kind]
    tr = planche_bois(n, fr, hs) if plank else None
    for k, f in enumerate(fr):
        f['a'] = ancre(kind, r, k, f, hs)
    return fr, hs, tr


def reduit(fr, C, scale):
    out = []
    for f in fr:
        lab = np.full(f['m'].shape, -1)
        lab[f['m']] = proche(oklab(f['rgb'][f['m']]), C)
        img, AX, AY = majorite(lab, f['rgb'], f['m'], f['a'][0], f['a'][1], scale)
        out.append(dict(img=sans_lisere(img), AX=AX, AY=AY))
    return out


def sans_lisere(img, it=2):
    """le liseré clair qui reste au bord après la réduction (le bout d'une mèche mêlé au blanc) : un pixel du bord, presque seul
    (trois voisins pleins au plus sur huit), plus clair que tous ses voisins pleins de 25 niveaux (de 40, avec quatre), s'en va"""
    a = img.copy()
    for _ in range(it):
        m = a[..., 3] > 0
        L = a[..., :3].astype(float) @ LUMA
        P = np.pad(m, 1)
        Lp = np.pad(np.where(m, L, -1.0), 1, constant_values=-1.0)
        n8 = sum(P[1 + dy:P.shape[0] - 1 + dy, 1 + dx:P.shape[1] - 1 + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dy or dx)
        mx = np.max([Lp[1 + dy:Lp.shape[0] - 1 + dy, 1 + dx:Lp.shape[1] - 1 + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dy or dx], 0)
        ote = m & (((n8 <= 3) & (L > mx + 25)) | ((n8 <= 4) & (L > mx + 40)))
        if not ote.any():
            break
        a[ote] = 0
    return a


def vers(f, p, scale, c):
    """un point de la planche (dans la boîte de l'image) vers la cellule réduite"""
    return [round((p[0] - f['a'][0]) * scale + c['AX'], 2), round((p[1] - f['a'][1]) * scale + c['AY'], 2)]


# ---- la horde
HSTRAY = 15                                           # (un bout détaché de 15 px au plus ôté sur le niveau de 290 px, à l'aire près ailleurs)
MOVES_H = ['walk'] * 8 + ['hit', 'hit', 'fall', 'fall', 'fall', 'down']


def cuire_horde(rep=False):
    looks, base = [], {}
    for n in ZN:                                      # (chaque zombie à ses cinq tailles, par majorité, depuis sa planche)
        e = echelles(n)
        f0, hs, _ = coupe(n, 'horde', 0, e)
        f1, _, _ = coupe(n, 'horde', 1, e)
        fr = f0 + f1
        C = familles_vote(fr)
        base[n] = [reduit(fr, C, (h / HN) / e['horde']) for h in NIVEAUX]
        looks.append((n, base[n]))
    for src, nom, regles in VARIANTES:                # (les variantes : ses images recolorées)
        looks.append((nom, [[dict(c, img=recolore(c['img'], regles)) for c in lv] for lv in base[src]]))
    graded = []                                       # (la nuit : une silhouette, toutes ses tailles et ses images ensemble)
    for nom, lv in looks:
        flat = [c['img'] for level in lv for c in level]
        g = iter(nuit(flat, NUIT['horde']))
        graded.append((nom, [[dict(c, img=next(g)) for c in level] for level in lv]))
    looks = graded
    sheets, frames = [], []
    for li, h in enumerate(NIVEAUX):
        tiles = [c['img'] for _, lv in looks for c in lv[li]]
        a, pos = range_atlas(tiles, 2048 if h < 200 else 3072)
        sheets.append(a)
        fl, i = [], 0
        for _, lv in looks:
            fl.append([[pos[i + k][0], pos[i + k][1], c['img'].shape[1], c['img'].shape[0], c['AX'], c['AY']] for k, c in enumerate(lv[li])])
            i += len(lv[li])
        frames.append(fl)
    infos = []
    for b, (nom, _) in enumerate(looks):              # (le grain : une silhouette, ses cinq tailles et ses 14 images ensemble)
        items = []
        for li, h in enumerate(NIVEAUX):
            for k, F in enumerate(frames[li][b]):
                items.append(dict(a=sheets[li], box=F[:4], anchor=(F[4], F[5]), seq=('L%d' % li, k),
                                  stray=max(1, round(HSTRAY * (h / 290.0) ** 2))))
        infos.append(RG.regrain_group(items, RG.params('horde', stray=HSTRAY), 'horde ' + nom))
    for li in range(len(NIVEAUX)):
        save(sheets[li], 'horde_L%d.webp' % li)
    ZH = {'levels': NIVEAUX, 'bodies': [nom for nom, _ in looks], 'stride': 0.9,
          'L': [{'h': h, 'moves': MOVES_H, 'frames': frames[li], 'size': [sheets[li].shape[1], sheets[li].shape[0]]} for li, h in enumerate(NIVEAUX)]}
    for i in infos:
        print('%-14s %2d familles, pente %.3f, %d px détachés ôtés' % (i['name'], i['families'], i['slope'], i['strays']))
    return ZH, sheets


def save(arr, name, rgb=False):
    im = Image.fromarray(arr[..., :3] if rgb else arr, 'RGB' if rgb else 'RGBA')
    im.save(os.path.join(ASSETS, name), 'WEBP', lossless=True, quality=100, method=6, exact=True)


# ---- les zombies du bus (à 41 m, 23,4 px/m)
MOVES_B = [('run', 'course', 0), ('leap', 'course', 1), ('jump', 'course', 2), ('roof', 'toit_fenetre', 0), ('plank', 'toit_fenetre', 1),
           ('fall', 'horde', 1)]
YEUX = {'run': range(8), 'leap': range(8), 'roof': range(8), 'plank': [7]}   # (les images où l'on voit son visage, de profil)
PLANK = dict(L=22, E=3)                               # (la planche du code : 22 px (0,94 m) sur 3, en travers d'une fenêtre de 20 px)


def foulee(fr, hs, e):
    """la foulée de la course (m par cycle de 8 images) : le pied posé recule sous les hanches pendant l'appui (la somme de
    ses reculs d'une image à l'autre, mesurée sur la planche) ; l'appui fait la moitié du cycle : la foulée, deux fois ce recul"""
    cs = [(contact(f['m'], hs, 0.02) - f['a'][0]) / e for f in fr]
    d = np.diff(cs + cs[:1])
    return round(float(2 * -d[d < 0].sum()), 3)


def lumiere(img):
    """les calques d'une cellule : spill (R : le côté gauche, G : le côté droit, la lumière de la rue qui vient de côté ; un
    fond de 0,35 partout) et glow (la lumière du salon du bus sur les bords du haut du corps, chaude et faible, additive)"""
    m = img[..., 3] > 0
    H, W = m.shape
    sp = np.zeros((H, W, 3), np.uint8)
    gl = np.zeros((H, W, 4), np.uint8)
    if not m.any():
        return sp, gl
    dl = np.zeros((H, W))
    dr = np.zeros((H, W))
    for y in range(H):                                # (la distance au bord gauche et au bord droit, le long de la rangée)
        run = 0
        for x in range(W):
            run = run + 1 if m[y, x] else 0
            dl[y, x] = run
        run = 0
        for x in range(W - 1, -1, -1):
            run = run + 1 if m[y, x] else 0
            dr[y, x] = run
    sp[..., 0] = np.where(m, np.round(90 + 165 * np.clip(1 - (dl - 1) / 2.5, 0, 1)), 0)
    sp[..., 1] = np.where(m, np.round(90 + 165 * np.clip(1 - (dr - 1) / 2.5, 0, 1)), 0)
    P = np.pad(m, 1)
    rim = m & ~(P[:-2, 1:-1] & P[2:, 1:-1] & P[1:-1, :-2] & P[1:-1, 2:])
    ys = np.nonzero(m.any(1))[0]
    rim[int(ys.min() + 0.6 * (ys.max() - ys.min() + 1)):] = False   # (le haut du corps, devant les fenêtres)
    gl[rim] = (18, 14, 8, 255)
    return sp, gl


def planche_sprite():
    """la planche du code (assets/bus_plank.webp) : 16 angles (k x 180°/16, l'axe vers (cos, sin), y vers le bas) et la
    planche couchée sur la chaussée ; chaque pixel plein quand la planche couvre la moitié de son empreinte (8 x 8 points) ;
    trois tons du bois de nuit dans son épaisseur (le dessus clair, le dessous sombre), un clou gris à chaque bout"""
    S = 25
    tons = [(66, 50, 44), (50, 38, 35), (36, 27, 28)]  # (les tons de la planche d'avant, de nuit, et ses clous)
    clou = (110, 100, 110)
    out = np.zeros((S, S * 17, 4), np.uint8)
    o = (np.arange(8) + 0.5) / 8
    for k in range(17):
        a = k * np.pi / 16 if k < 16 else 0.0
        L, E = PLANK['L'], (PLANK['E'] if k < 16 else 2)
        ux, uy = np.cos(a), np.sin(a)
        for y in range(S):
            for x in range(S):
                px = x + o[None, :] - S / 2
                py = y + o[:, None] - S / 2
                u = px * ux + py * uy
                v = -px * uy + py * ux
                ins = (np.abs(u) <= L / 2) & (np.abs(v) <= E / 2)
                if ins.mean() >= 0.5:
                    uu, vv = float(u[ins].mean()), float(v[ins].mean())
                    t = min(2, max(0, int((vv + E / 2) / E * 3))) if k < 16 else (0 if vv < 0 else 2)
                    c = clou if abs(abs(uu) - (L / 2 - 1.5)) < 0.75 and abs(vv) < 0.9 else tons[t]
                    out[y, k * S + x] = c + (255,)
    return out


def cuire_bus():
    cells, meta = [], []
    for n in ZN:
        e = echelles(n)
        rows = {}
        for mv, kind, r in MOVES_B:
            fr, hs, tr = coupe(n, kind, r, e, plank=(mv == 'plank'))
            rows[mv] = (fr, hs, tr, kind)
        C = familles_vote([f for fr, _, _, _ in rows.values() for f in fr])
        md = {'cells': {}, 'pts': {}, 'eyes': {}}
        for mv, (fr, hs, tr, kind) in rows.items():
            sc = BUS_PPM / e[kind]
            cs = reduit(fr, C, sc)
            md['cells'][mv] = cs
            if mv in ('leap', 'jump'):                # (les mains en haut : la prise du toit, de la planche)
                md['pts'][mv] = [vers(f, mains(f['m'], hs), sc, c) for f, c in zip(fr, cs)]
            if mv in YEUX:
                md['eyes'][mv] = [(vers(f, oeil(f, hs), sc, c) if k in YEUX[mv] and oeil(f, hs) else 0) for k, (f, c) in enumerate(zip(fr, cs))]
            if mv == 'plank':
                md['plank'] = [[t[0], round((t[1] - f['a'][0]) * sc, 2), round((t[2] - f['a'][1]) * sc, 2), round(t[3], 3)] if t[0] else [0, 0, 0, 0]
                               for f, t in zip(fr, tr)]
                md['plankL'] = [round(t[4] * sc, 1) for t in tr if t[0] == 1]
            if mv == 'run':
                md['stride'] = foulee(fr, hs, e[kind])
        flat = [c['img'] for mv, *_ in MOVES_B for c in md['cells'][mv]]   # (la nuit, toutes ses images ensemble)
        g = iter(nuit(flat, NUIT['bus']))
        for mv, *_ in MOVES_B:
            md['cells'][mv] = [dict(c, img=next(g)) for c in md['cells'][mv]]
        meta.append(md)
        for mv, *_ in MOVES_B:
            cells += [c['img'] for c in md['cells'][mv]]
    a, pos = range_atlas(cells, 1024)
    sp = np.zeros(a.shape[:2] + (3,), np.uint8)
    gl = np.zeros(a.shape, np.uint8)
    Z, i = [], 0
    for md in meta:
        zz = {}
        for mv, *_ in MOVES_B:
            fl = []
            for c in md['cells'][mv]:
                x, y = pos[i]
                h, w = c['img'].shape[:2]
                fl.append([x, y, w, h, c['AX'], c['AY']])
                s1, g1 = lumiere(c['img'])
                sp[y:y + h, x:x + w] = s1
                i += 1
            zz[mv] = fl
        Z.append(zz)
    infos = []
    for b, n in enumerate(ZN):                        # (le grain : un zombie, toutes ses images ensemble ; la lumière de la rue par tache)
        items = [dict(a=a, box=F[:4], anchor=(F[4], F[5]), seq=(mv, k), **{'with': [sp]}) for mv, *_ in MOVES_B for k, F in enumerate(Z[b][mv])]
        infos.append(RG.regrain_group(items, RG.params('bus'), 'bus ' + n))
    for b in range(len(ZN)):                          # (le liseré du salon, sur le masque final ; l'œil, un pixel orange)
        for mv, *_ in MOVES_B:
            for k, F in enumerate(Z[b][mv]):
                x, y, w, h = F[:4]
                _, g1 = lumiere(a[y:y + h, x:x + w])
                gl[y:y + h, x:x + w] = g1
                ey = meta[b]['eyes'].get(mv)
                if ey and ey[k]:
                    ex_, ey_ = int(np.floor(ey[k][0])), int(np.floor(ey[k][1]))
                    if 0 <= ex_ < w and 0 <= ey_ < h and a[y + ey_, x + ex_, 3]:
                        a[y + ey_, x + ex_, :3] = (232, 120, 40)
                        gl[y + ey_, x + ex_] = (110, 60, 20, 255)
    save(a, 'bus_zombies.webp')
    save(gl, 'bus_zombies_glow.webp')
    save(np.dstack([sp, np.full(sp.shape[:2], 255, np.uint8)]), 'bus_zombies_spill.webp', rgb=True)
    save(planche_sprite(), 'bus_plank.webp')
    BZ = {'W': a.shape[1], 'H': a.shape[0], 'ppm': round(BUS_PPM, 2), 'Z': Z,
          'P': [md['pts'] for md in meta], 'E': [md['eyes'] for md in meta], 'K': [md['plank'] for md in meta],
          'S': [md['stride'] for md in meta], 'pl': [PLANK['L'], PLANK['E'], 25, 17]}
    for i in infos:
        print('%-10s %2d familles, pente %.3f, %d px détachés ôtés' % (i['name'], i['families'], i['slope'], i['strays']))
    print('foulées (m par cycle) :', BZ['S'], ' planches tenues (px) :', [md['plankL'] for md in meta])
    return BZ, a


# ---- street.js : les lignes ZH et BZ (rien d'autre n'y est touché ; BZ garde ce qui n'est pas à l'outil : soda, drink)
JSF = os.path.join(ASSETS, 'street.js')


def ligne(js, nom, data, keep=()):
    pat = re.compile(r'^(  const ' + nom + r' = )(\{.*?\});(.*)$', re.M)
    m = pat.search(js)
    if not m:
        raise SystemExit('la ligne %s de assets/street.js est introuvable' % nom)
    if keep:
        old = json.loads(m.group(2))
        for k in keep:
            if k in old:
                data[k] = old[k]
    txt = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
    return js[:m.start()] + m.group(1) + txt + ';' + m.group(3) + js[m.end():]


def ecrire_js(ZH=None, BZ=None):
    js = open(JSF, encoding='utf-8').read()
    if ZH is not None:
        js = ligne(js, 'ZH', ZH)
    if BZ is not None:
        js = ligne(js, 'BZ', BZ, keep=('soda', 'drink'))
    with open(JSF, 'w', encoding='utf-8') as f:
        f.write(js)


# ---- les planches de contrôle (x4) : chaque zombie, toutes ses images découpées, ses variantes ; ses ancres en rouge
def planches_controle(out, ZH, BZ):
    os.makedirs(out, exist_ok=True)
    fond = (34, 32, 44)
    hord = [np.array(Image.open(os.path.join(ASSETS, 'horde_L%d.webp' % i)).convert('RGBA')) for i in range(len(NIVEAUX))]
    bus = np.array(Image.open(os.path.join(ASSETS, 'bus_zombies.webp')).convert('RGBA'))

    def tuile(a, F, k):
        x, y, w, h, ax, ay = F
        im = Image.fromarray(a[y:y + h, x:x + w], 'RGBA')
        bg = Image.new('RGBA', (w, h), fond + (255,))
        bg.alpha_composite(im)
        bg = bg.convert('RGB').resize((w * k, h * k), Image.NEAREST)
        d = ImageDraw.Draw(bg)
        d.line([(ax * k - 3, ay * k), (ax * k + 3, ay * k)], fill=(255, 60, 60))
        d.line([(ax * k, ay * k - 3), (ax * k, ay * k)], fill=(255, 60, 60))
        return bg

    def rang(tiles, titre):
        W = sum(t.width + 6 for t in tiles) + 6
        H = max(t.height for t in tiles) + 20
        c = Image.new('RGB', (W, H), (16, 16, 20))
        ImageDraw.Draw(c).text((6, 3), titre, fill=(240, 220, 130))
        x = 6
        for t in tiles:
            c.paste(t, (x, H - t.height))
            x += t.width + 6
        return c

    for b, n in enumerate(ZN):
        rows = []
        looks = [i for i, nom in enumerate(ZH['bodies']) if nom.startswith(n)]
        for i in looks:                                # (la horde, 100 px (x4) : la marche, touché, la chute)
            rows.append(rang([tuile(hord[1], F, 4) for F in ZH['L'][1]['frames'][i]], 'horde %s (%s), 100 px x4' % (ZH['bodies'][i], NOMS[n])))
        rows.append(rang([tuile(hord[3], F, 1) for F in ZH['L'][3]['frames'][b]], 'horde %s, 290 px x1' % n))
        for mv, *_ in MOVES_B:
            rows.append(rang([tuile(bus, F, 4) for F in BZ['Z'][b][mv]], 'bus %s : %s, 41 m x4' % (n, mv)))
        W = max(r.width for r in rows)
        H = sum(r.height for r in rows)
        c = Image.new('RGB', (W, H), (16, 16, 20))
        y = 0
        for r in rows:
            c.paste(r, (0, y))
            y += r.height
        c.save(os.path.join(out, 'zombie_%s_planche_x4.png' % n))


def main():
    ap = argparse.ArgumentParser(description='les zombies de la horde et du bus, découpés dans les planches (voir la docstring)')
    ap.add_argument('--only', default=None, help='horde | bus')
    ap.add_argument('--planches', default=None, help='un dossier : une planche de contrôle par zombie (x4)')
    o = ap.parse_args()
    only = o.only.split(',') if o.only else ['horde', 'bus']
    ZH = BZ = None
    if 'horde' in only:
        ZH, _ = cuire_horde()
    if 'bus' in only:
        BZ, _ = cuire_bus()
    ecrire_js(ZH, BZ)
    if o.planches:
        js = open(JSF, encoding='utf-8').read()
        dec = json.JSONDecoder()
        ZH = dec.raw_decode(js[js.index('  const ZH = ') + 13:])[0]
        BZ = dec.raw_decode(js[js.index('  const BZ = ') + 13:])[0]
        planches_controle(o.planches, ZH, BZ)


if __name__ == '__main__':
    main()
