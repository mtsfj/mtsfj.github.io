#!/usr/bin/env python3
"""Le grain des figures : un atlas de sprites ramené au grain de la peinture (des familles de tons, un grain fin dans chacune).

    python3 tools/regrain.py                        (les sprites de la rue : l'équipe, la horde, les zombies du bus ; lit les
                                                     originaux de tools/src/regrain_orig/, réécrit assets/crew_*.webp,
                                                     horde_L0..L4.webp, bus_zombies.webp et bus_zombies_spill.webp ; on peut
                                                     le relancer, il repart des originaux et écrit la même chose)
    python3 tools/regrain.py --only crew,horde      (une partie seulement)
    python3 tools/regrain.py --report               (en plus : le grain de chaque feuille avant et après, cellule par cellule)

    python3 tools/regrain.py sheet IN.webp OUT.webp [--grid CWxCH | --cells cells.json] [--group all|rows]
                                [--families 20] [--p95 80] [--knee 30] [--with calque.webp] [--anchor AX,AY] [--report]
                                                    (n'importe quel atlas RGBA : une nouvelle planche passe par le même
                                                     chemin ; sans --grid ni --cells, les cellules sont trouvées seules)

Les figures en 3D réduites (l'équipe, la horde, les zombies du bus) ont des centaines de couleurs, des taches de 2 à 9 px,
moitié de pixels isolés, des dégradés lisses : de la bouillie à côté de la peinture, qui a 7 à 27 familles de tons (à 8
niveaux près) sur 90 % d'un objet, un grain fin de 1 à 3 niveaux dans chaque famille, des taches de 60 à 500 px, des
bords nets, pas de contour noir (tools/figures_audit.py, ses mesures ; les règles du grain de la maison). Pour chaque
personnage (toutes ses images ensemble : ses familles ne changent pas d'une image à l'autre, rien ne scintille) :

- Les poussières : dans chaque image, les bouts détachés du corps (8-connexes) de STRAY px au plus sont ôtés ; une main
  détachée par le rendu est gardée (pour la horde : 15 px au plus sur son niveau de 290 px, à l'aire près sur les
  autres, et rien qui tombe, rapporté par les ancres, sur une partie du niveau de 290 px). Rien d'autre du masque ne
  bouge : le contour reste pixel pour pixel, opaque ou vide.
- L'étalonnage (la nuit) : au-dessus du genou (KNEE, en luminance 0-255), les clairs sont comprimés (chaque couleur
  ramenée sur sa propre teinte) jusqu'à ce que le p95 de chaque image tienne sous P95 : la peinture voisine + 15 %. Les
  sombres ne bougent pas.
- Les familles : k-moyennes en OKLab sur tous les pixels du personnage (FAMILIES familles), les familles trop proches
  (MERGE en OKLab) fondues.
- Chaque pixel prend une famille : la plus proche de sa couleur, mais un pixel compte aussi ses quatre voisins (un modèle
  de Potts, résolu en damier par ICM : la différence de couleur en unités de SCALE, bornée à CAP, contre le nombre de
  voisins de la même famille) : les taches de camouflage et les points isolés rejoignent la masse autour d'eux (un point
  seul dont deux voisins s'accordent prend leur famille, si différent soit-il : les mouchetures orange de la horde s'en
  vont), un trait d'un pixel de large reste ; d'une image à la suivante d'un même mouvement (recalée sur ses ancres), un
  pixel dont la couleur n'a presque pas bougé garde sa famille (TEMPO). Les reflets d'un pixel du métal et du verre
  (plus clairs que leurs quatre voisins, presque gris) ne sont gardés que sur demande (--glint) : sur ces rendus, ce que
  la règle trouve là est du bruit de camouflage et du bord, pas une arme.
- Le grain : la couleur de la famille, plus un grain fin baké : l'écart de luminance du pixel d'origine à sa famille
  (GRAIN_K), plus un tramage ordonné (Bayer 4 x 4, ancré au pied de la figure : il la suit, et le webp sans perte reprend
  son motif), arrondi et borné à 1, 2 ou 3 niveaux selon la luminance de la famille (1 dans les noirs). Le même décalage
  sur les trois canaux : la teinte reste.
- Les calques liés aux pixels de la figure (la lumière de l'éclair de l'équipe, la lumière de la rue sur les zombies du
  bus) prennent, tache par tache (une famille, d'un seul tenant, dans une image), leur moyenne : la lumière éclaire une
  tache entière, elle ne refait pas de dégradé. L'éclair n'est pas étalonné (sa propre lumière) ; la lueur des zombies du
  bus (bus_zombies_glow.webp, un calque de lumière) n'est pas touchée.

Les cellules : pour la rue, lues dans assets/street.js (CRW, HRD, BZ ; des données, rien n'y est écrit) ; pour une planche,
une grille (--grid), une liste (--cells : {"groupes": {"nom": [[x, y, w, h], ...]}}, ou une liste de boîtes), ou
trouvées seules (les taches de l'alpha, rapprochées de --gap px, rangées ligne par ligne). --group : all (un personnage
par planche), rows (un personnage par rangée de cellules). Il faut Pillow, numpy, scipy.
"""
import argparse
import json
import os
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as nd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIG = os.path.join(ROOT, 'tools', 'src', 'regrain_orig')
ASSETS = os.path.join(ROOT, 'assets')
LUM = np.array([0.299, 0.587, 0.114])               # (la luminance de tools/figures_audit.py)

# les réglages par défaut (une planche nouvelle : les mêmes, ses cibles en paramètres)
DEF = dict(families=20, merge=0.015, scale=0.04, cap=2.5, iters=6, tempo=2.0, tempo_de=0.02, grain_k=0.2, dither=1.6, pattern='bayer',
           stray=3, knee=30.0, p95=None, p95_stat=1.0, glint_dl=None, glint_c=0.04)

# les sprites de la rue. local : la peinture autour d'eux (layer_city_off.webp, L 5/50/95), leur cible p95 = local + 15 %
STREET = {
    'crew': dict(local=(13, 29, 70), box='x 700-950, rangées 590-660 (le carrefour derrière l\'équipe)', families=24, knee=20.0),
    'horde': dict(local=(2, 19, 60), box='x 850-1300, rangées 620-816 (la chaussée et le trottoir de droite)', families=26, knee=20.0),
    'bus': dict(local=(14, 30, 78), box='x 500-900, rangées 585-650 (le carrefour, à la hauteur du bus)', families=14, knee=30.0),
}


# ---- couleurs
def _lin(c):
    c = np.asarray(c, float) / 255
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def _srgb(c):
    c = np.clip(c, 0, 1)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * np.power(c, 1 / 2.4) - 0.055) * 255


def oklab(rgb):
    l = _lin(rgb)
    M1 = np.array([[0.4122214708, 0.5363325363, 0.0514459929], [0.2119034982, 0.6806995451, 0.1073969566], [0.0883024619, 0.2817188376, 0.6299787005]])
    M2 = np.array([[0.2104542553, 0.7936177850, -0.0040720468], [1.9779984951, -2.4285922050, 0.4505937099], [0.0259040371, 0.7827717662, -0.8086757660]])
    return np.cbrt(l @ M1.T) @ M2.T


def from_oklab(lab):
    M2i = np.array([[1.0, 0.3963377774, 0.2158037573], [1.0, -0.1055613458, -0.0638541728], [1.0, -0.0894841775, -1.2914855480]])
    M1i = np.array([[4.0767416621, -3.3077115913, 0.2309699292], [-1.2684380046, 2.6097574011, -0.3413193965], [-0.0041960863, -0.7034186147, 1.7076147010]])
    return _srgb((np.asarray(lab) @ M2i.T) ** 3 @ M1i.T)


def luma(rgb):
    return np.asarray(rgb, float)[..., :3] @ LUM


def tone(rgb, knee, s):
    """les clairs comprimés au-dessus du genou (luminance knee), chaque couleur gardant sa teinte : L' = knee + (L - knee) s"""
    rgb = np.asarray(rgb, float)
    L = luma(rgb)
    Lt = np.where(L > knee, knee + (L - knee) * s, L)
    return rgb * (Lt / np.maximum(L, 1e-6))[..., None]


BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16 + 1 / 32


def bayer(h, w, ox=0, oy=0):
    """le tramage ordonné de Bayer 4 x 4 (0..1), ancré en (ox, oy) : un motif qui se répète (le webp sans perte le reprend)"""
    y, x = np.mgrid[0:h, 0:w]
    return BAYER[(y - oy) % 4, (x - ox) % 4]


def ign(h, w, ox=0, oy=0):
    """le tramage ordonné : bruit à gradient entrelacé (0..1), ancré en (ox, oy)"""
    y, x = np.mgrid[0:h, 0:w]
    x, y = x - ox, y - oy
    return np.mod(52.9829189 * np.mod(0.06711056 * x + 0.00583715 * y, 1.0), 1.0)


# ---- les cellules
def auto_cells(alpha, gap=2, minpx=12):
    """les figures d'un atlas : les taches de l'alpha rapprochées de gap px ; leurs boîtes, ligne par ligne"""
    m = alpha > 0
    lab, n = nd.label(nd.binary_dilation(m, iterations=gap) if gap else m, structure=np.ones((3, 3)))
    boxes = []
    for i, sl in enumerate(nd.find_objects(lab)):
        if sl is None:
            continue
        sub = m[sl] & (lab[sl] == i + 1)
        if sub.sum() < minpx:
            continue
        ys, xs = np.nonzero(sub)
        boxes.append([sl[1].start + int(xs.min()), sl[0].start + int(ys.min()), int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1)])
    if not boxes:
        return []
    hmed = np.median([b[3] for b in boxes])
    boxes.sort(key=lambda b: (round((b[1] + b[3]) / max(1.0, hmed / 2)), b[0]))     # (par rangée de pieds, puis de gauche à droite)
    return boxes


def grid_cells(W, H, cw, ch):
    return [[x, y, cw, ch] for y in range(0, H - ch + 1, ch) for x in range(0, W - cw + 1, cw)]


# ---- les poussières
def strays(alpha, maxpx, keep=None):
    """les bouts détachés (8-connexes) de maxpx px au plus, hors du plus grand ; keep(composante) -> True : gardé"""
    m = alpha > 0
    lab, n = nd.label(m, structure=np.ones((3, 3)))
    out = np.zeros_like(m)
    if n <= 1:
        return out
    sz = np.bincount(lab.ravel())
    sz[0] = 0
    big = int(sz.argmax())
    for i in range(1, n + 1):
        if i == big or sz[i] > maxpx:
            continue
        comp = lab == i
        if keep is not None and keep(comp):
            continue
        out |= comp
    return out


# ---- les familles
def kmeans(X, w, K, seed=7, iters=40):
    """k-moyennes pondérées (X : couleurs OKLab uniques, w : leurs comptes), départ k-means++ déterministe"""
    rng = np.random.default_rng(seed)
    K = min(K, len(X))
    C = [X[int(np.argmax(w))]]
    d2 = ((X - C[0]) ** 2).sum(1)
    for _ in range(1, K):
        p = d2 * w
        C.append(X[int(rng.choice(len(X), p=p / p.sum()))] if p.sum() > 0 else X[int(rng.integers(len(X)))])
        d2 = np.minimum(d2, ((X - C[-1]) ** 2).sum(1))
    C = np.array(C)
    for _ in range(iters):
        lab = ((X[:, None] - C[None]) ** 2).sum(2).argmin(1)
        C2 = np.array([np.average(X[lab == k], 0, w[lab == k]) if (lab == k).any() else C[k] for k in range(K)])
        if np.abs(C2 - C).max() < 1e-6:
            break
        C = C2
    lab = ((X[:, None] - C[None]) ** 2).sum(2).argmin(1)
    return C, lab


def families(lab_px, K, merge, seed=7):
    """les familles d'un personnage : k-moyennes sur ses couleurs, puis les familles à moins de merge (OKLab) fondues"""
    q = np.round(lab_px * 2000).astype(np.int64)                 # (les couleurs uniques, à 1/2000 près)
    u, inv, cnt = np.unique(q, axis=0, return_inverse=True, return_counts=True)
    X = np.zeros((len(u), 3))
    np.add.at(X, inv.ravel(), lab_px)
    X /= cnt[:, None]
    w = cnt.astype(float)
    C, lab = kmeans(X, w, K, seed)
    while True:
        W = np.array([w[lab == k].sum() for k in range(len(C))])
        keep = W > 0
        C, W = C[keep], W[keep]
        d = np.sqrt(((C[:, None] - C[None]) ** 2).sum(2)) + np.eye(len(C)) * 9
        i, j = np.unravel_index(int(d.argmin()), d.shape)
        if d[i, j] >= merge or len(C) <= 2:
            break
        C[i] = (C[i] * W[i] + C[j] * W[j]) / (W[i] + W[j])
        C = np.delete(C, j, 0)
        lab = ((X[:, None] - C[None]) ** 2).sum(2).argmin(1)
        for _ in range(5):                                         # (quelques passes : les centres recalés)
            C = np.array([np.average(X[lab == k], 0, w[lab == k]) if (lab == k).any() else C[k] for k in range(len(C))])
            lab = ((X[:, None] - C[None]) ** 2).sum(2).argmin(1)
    order = np.argsort(C[:, 0])                                     # (du plus sombre au plus clair)
    return C[order]


SW = np.sqrt([1.0, 2.0, 2.0])                                       # (OKLab, la teinte comptée double : deux lumières sur une chemise
                                                                     #  restent deux familles, pas une moyenne beige)


def glints(X, M, dl, cmax):
    """les reflets du métal et du verre : un pixel plus clair que ses 4 voisins de dl (L d'OKLab), lui et eux presque gris"""
    L = X[..., 0]
    ch = np.hypot(X[..., 1], X[..., 2])
    P = lambda a, v: np.pad(a, 1, constant_values=v)
    Lp, Mp, cp = P(L, -9), P(M, False), P(ch, 0)
    nb = [(Lp[:-2, 1:-1], Mp[:-2, 1:-1], cp[:-2, 1:-1]), (Lp[2:, 1:-1], Mp[2:, 1:-1], cp[2:, 1:-1]),
          (Lp[1:-1, :-2], Mp[1:-1, :-2], cp[1:-1, :-2]), (Lp[1:-1, 2:], Mp[1:-1, 2:], cp[1:-1, 2:])]
    hi = np.max([np.where(m, l, -9) for l, m, _ in nb], 0)
    cn = np.sum([np.where(m, c, 0) for _, m, c in nb], 0) / np.maximum(1, np.sum([m for _, m, _ in nb], 0))
    return M & (L - hi >= dl) & (ch < cmax) & (cn < cmax)


def assign(X, M, C, scale, iters, prior=None, prior_ok=None, tempo=0.0, cap=None, lock=None):
    """chaque pixel du masque M (X : OKLab pondéré) à une famille de C : sa couleur (en unités de scale, bornée à cap : un point
    isolé, si différent soit-il, rejoint ses voisins s'ils sont d'accord) contre ses 4 voisins (Potts, ICM en damier) ; lock : gardés"""
    H, W = M.shape
    K = len(C)
    D0 = ((X[:, :, None, :] - C[None, None]) ** 2).sum(-1) / scale ** 2
    lab = D0.argmin(-1)
    D = np.minimum(D0, cap) if cap else D0
    if lock is not None:
        D = D.copy()
        D[lock] = 1e6
        D[lock, lab[lock]] = -1e6
    if prior is not None:
        pm = prior_ok & M
    yy, xx = np.mgrid[0:H, 0:W]
    board = (yy + xx) % 2
    for _ in range(iters):
        for par in (0, 1):
            oh = np.zeros((H + 2, W + 2, K))
            ys, xs = np.nonzero(M)
            oh[ys + 1, xs + 1, lab[ys, xs]] = 1
            N = oh[:-2, 1:-1] + oh[2:, 1:-1] + oh[1:-1, :-2] + oh[1:-1, 2:]
            E = D - N
            if prior is not None:
                E[pm, prior[pm]] -= tempo
            new = E.argmin(-1)
            upd = M & (board == par)
            lab = np.where(upd, new, lab)
    if cap:                                                            # (un point encore seul, dont deux voisins ou plus sont d'une même
        for _ in range(2):                                             #  famille : il la prend ; les reflets gardés restent)
            P_ = np.pad(np.where(M, lab, -1), 1, constant_values=-1)
            nb = np.stack([P_[:-2, 1:-1], P_[2:, 1:-1], P_[1:-1, :-2], P_[1:-1, 2:]], -1)
            alone = M & ~(nb == lab[..., None]).any(-1)
            if lock is not None:
                alone &= ~lock
            best, bn = lab.copy(), np.zeros(lab.shape, int)
            for j in range(4):
                k = nb[..., j]
                n = (nb == k[..., None]).sum(-1)
                take = (k >= 0) & ((n > bn) | ((n == bn) & (np.take_along_axis(D0, np.maximum(k, 0)[..., None], -1)[..., 0] < np.take_along_axis(D0, best[..., None], -1)[..., 0])))
                best = np.where(take, k, best)
                bn = np.where(take, n, bn)
            lab = np.where(alone & (bn >= 2), best, lab)
    return lab


def align(pr, c, anchor):
    """l'image d'avant (pr : X, lab, M, anchor) recalée sur la cellule de c, ancre sur ancre (un décalage de pixels entiers)"""
    H, W = c['M'].shape
    a0, a1 = pr.get('anchor') or (0, 0), anchor or (0, 0)
    dx, dy = int(round(a1[0] - a0[0])), int(round(a1[1] - a0[1]))
    X = np.zeros((H, W, 3))
    lab = np.zeros((H, W), int)
    M = np.zeros((H, W), bool)
    ph, pw = pr['M'].shape
    ys, ye = max(0, dy), min(H, ph + dy)
    xs, xe = max(0, dx), min(W, pw + dx)
    if ye > ys and xe > xs:
        X[ys:ye, xs:xe] = pr['X'][ys - dy:ye - dy, xs - dx:xe - dx]
        lab[ys:ye, xs:xe] = pr['lab'][ys - dy:ye - dy, xs - dx:xe - dx]
        M[ys:ye, xs:xe] = pr['M'][ys - dy:ye - dy, xs - dx:xe - dx]
    return X, lab, M


def patches(lab, M):
    """les taches : une famille, d'un seul tenant (4-connexe), dans une image ; leur numéro par pixel"""
    out = np.zeros(lab.shape, int)
    n = 0
    for k in np.unique(lab[M]):
        l, c = nd.label(M & (lab == k))
        out[l > 0] = l[l > 0] + n
        n += c
    return out, n


def patch_mean(layer, pt, n, M):
    """un calque lié aux pixels de la figure : chaque tache prend sa moyenne (canaux 0-2, arrondie)"""
    out = layer.copy()
    idx = pt[M]
    cnt = np.bincount(idx, minlength=n + 1).astype(float)
    for ch in range(3):
        s = np.bincount(idx, weights=layer[..., ch][M].astype(float), minlength=n + 1)
        mean = np.round(s / np.maximum(cnt, 1))
        out[..., ch][M] = np.clip(mean[idx], 0, 255).astype(layer.dtype)
    return out


def amp(L):
    """la borne du grain selon la luminance de la famille : 1 niveau dans les noirs, 2, puis 3"""
    return np.where(L < 14, 1, np.where(L < 40, 2, 3))


# ---- un personnage
def regrain_group(items, P, name=''):
    """items : ses images, chacune {'a': l'atlas RGBA (modifié en place), 'box': (x, y, w, h), 'anchor': (ax, ay) dans la
    cellule ou None, 'seq': (mouvement, rang) ou None, 'keep': fonction(composante, item) -> True pour une partie détachée
    à garder, 'with': [calques liés aux pixels (RGBA ou RGB), modifiés en place]}. P : les réglages."""
    cells = []
    for it in items:
        x, y, w, h = it['box']
        c = it['a'][y:y + h, x:x + w]
        st = strays(c[..., 3], it.get('stray', P['stray']), (lambda comp, it=it: it['keep'](comp, it)) if it.get('keep') else None)
        cells.append(dict(it=it, rgb=c[..., :3].astype(float), M=(c[..., 3] >= 128) & ~st, stray=st))
    # l'étalonnage : la pente au-dessus du genou qui tient le p95 de (presque) chaque image sous la cible
    s = 1.0
    if P.get('p95'):
        def stat(sv):
            v = [np.percentile(luma(tone(c['rgb'][c['M']], P['knee'], sv)), 95) for c in cells if c['M'].sum() >= 30]
            return np.quantile(v, P['p95_stat']) if v else 0
        goal = P['p95'] - 2                                            # (la marge du grain baké, jusqu'à +3)
        if stat(1.0) > goal:
            lo, hi = 0.0, 1.0
            for _ in range(30):
                mid = (lo + hi) / 2
                lo, hi = (mid, hi) if stat(mid) <= goal else (lo, mid)
            s = lo
    for c in cells:
        c['g'] = tone(c['rgb'], P['knee'], s)
        c['X'] = oklab(np.clip(c['g'], 0, 255)) * SW
    allpx = np.concatenate([c['X'][c['M']] for c in cells])
    C = families(allpx, P['families'], P['merge'], P.get('seed', 7))
    base = np.clip(np.round(from_oklab(C / SW)), 0, 255)
    Lb = luma(base)
    A = amp(Lb)
    # les images, dans l'ordre de leurs mouvements (le prior : l'image d'avant du même mouvement)
    order = sorted(range(len(cells)), key=lambda i: (cells[i]['it'].get('seq') or (i, 0)))
    prev = {}
    nfl = nst = nlock = 0
    for i in order:
        c = cells[i]
        it = c['it']
        seq = it.get('seq')
        pr = prev.get(seq[0]) if seq else None
        prior = prior_ok = None
        if pr is not None:                                             # (l'image d'avant posée sur celle-ci par leurs ancres)
            pX, plab, pM = align(pr, c, it.get('anchor'))
            prior = plab
            prior_ok = pM & c['M'] & (np.sqrt(((c['X'] - pX) ** 2).sum(-1)) < P['tempo_de'])
        lock = glints(c['X'] / SW, c['M'], P['glint_dl'], P['glint_c']) if P.get('glint_dl') else None
        lab = assign(c['X'], c['M'], C, P['scale'], P['iters'], prior, prior_ok, P['tempo'], P.get('cap'), lock)
        nlock += int(lock.sum()) if lock is not None else 0
        if prior is not None:                                          # (le scintillement : même couleur d'origine, famille changée)
            nst += int(prior_ok.sum())
            nfl += int((prior_ok & (lab != prior)).sum())
        if seq:
            prev[seq[0]] = dict(X=c['X'], lab=lab, M=c['M'], anchor=it.get('anchor'))
        h, w = c['M'].shape
        ax, ay = it.get('anchor') or (0, 0)
        d = (bayer if P.get('pattern') == 'bayer' else ign)(h, w, int(round(ax)), int(round(ay)))
        off = luma(c['g']) - Lb[lab]
        g = np.clip(np.round(P['grain_k'] * off + (d - 0.5) * P['dither']), -A[lab], A[lab])
        out = np.clip(base[lab] + g[..., None], 0, 255).astype(np.uint8)
        x, y, w2, h2 = it['box']
        tile = it['a'][y:y + h2, x:x + w2]
        tile[..., :3] = np.where(c['M'][..., None], out, tile[..., :3])
        tile[..., 3] = np.where(c['M'], 255, np.where(c['stray'], 0, tile[..., 3]))
        tile[..., :3][c['stray']] = 0
        if it.get('with'):
            pt, n = patches(lab, c['M'])
            for L in it['with']:
                t2 = L[y:y + h2, x:x + w2]
                lit = c['M'] & ((t2[..., 3] > 0) if t2.shape[-1] == 4 else True)
                t2[...] = patch_mean(t2, pt, n, lit)
                if t2.shape[-1] == 4:
                    t2[..., 3][c['stray']] = 0
                    t2[..., :3][c['stray']] = 0
        c['lab'] = lab
    info = dict(name=name, families=len(C), slope=round(s, 3), knee=P['knee'], p95=P.get('p95'), cells=len(cells),
                strays=int(sum(c['stray'].sum() for c in cells)), flicker=round(nfl / max(1, nst), 4), glints=nlock,
                base=[[int(v) for v in b] for b in base])
    return info


# ---- les mesures (celles de tools/figures_audit.py)
def report(atlas, boxes, label):
    try:
        sys.path.insert(0, os.path.join(ROOT, 'tools'))
        import figures_audit as FA
    except Exception as e:                                             # (sans assets/street.js : pas de mesure)
        print('(pas de mesure : %s)' % e)
        return None
    rows = []
    for (x, y, w, h) in boxes:
        c = atlas[y:y + h, x:x + w]
        m = c[..., 3] >= 128
        if m.sum() < 30:
            continue
        g = FA.grain(c[..., :3], m)
        g.update(FA.edge(c))
        lab, n = nd.label(c[..., 3] > 0, structure=np.ones((3, 3)))
        sz = np.bincount(lab.ravel())[1:]
        g['stray'] = int(sz.sum() - sz.max()) if n > 1 else 0
        rows.append(g)
    keys = ['uniq', 'fam', 'fam90', 'tache', 'isole', 'doux', 'L5', 'L50', 'L95', 'anneau', 'alpha_part']
    med = {k: round(float(np.median([r[k] for r in rows])), 3) for k in keys}
    med['isole_max'] = round(float(max(r['isole'] for r in rows)), 3)
    med['fam90_max'] = int(max(r['fam90'] for r in rows))
    med['L95_p90'] = round(float(np.quantile([r['L95'] for r in rows], 0.9)), 1)
    med['detache_px'] = int(sum(r['stray'] for r in rows))
    print('  %-26s %s' % (label, json.dumps(med)))
    return med


# ---- la rue
def street_data():
    JS = open(os.path.join(ASSETS, 'street.js'), encoding='utf-8').read()
    dec = json.JSONDecoder()
    i = JS.find('const CRW = ') + 12
    CRW = dec.raw_decode(JS[i:])[0]
    HRD = dec.raw_decode(JS[JS.find('HRD = ', i) + 6:])[0]
    BZ = dec.raw_decode(JS[JS.find('const BZ = ') + 11:])[0]
    return CRW, HRD, BZ


def load(name):
    p = os.path.join(ORIG, name)
    if not os.path.exists(p):
        sys.exit('il manque l\'original %s (tools/src/regrain_orig/ : les feuilles d\'avant le grain, d\'où l\'outil repart toujours)' % p)
    return np.array(Image.open(p).convert('RGBA'))


def save(arr, name, rgb=False):
    im = Image.fromarray(arr if not rgb else arr[..., :3], 'RGB' if rgb else 'RGBA')
    im.save(os.path.join(ASSETS, name), 'WEBP', lossless=True, quality=100, method=6, exact=True)


def params(kind, **kw):
    P = dict(DEF)
    S = STREET[kind]
    P.update(families=S['families'], knee=S['knee'], p95=round(S['local'][2] * 1.15, 1))
    P.update(kw)
    return P


def do_crew(CRW, rep):
    out = []
    for who, C in CRW['heroes'].items():
        a, f = load('crew_%s.webp' % who), load('crew_%s_flash.webp' % who)
        boxes = [[(n % C['cols']) * C['cw'], (n // C['cols']) * C['ch'], C['cw'], C['ch']] for n in range(C['n'])]
        if rep:
            report(a, boxes, 'crew_%s avant' % who)
        seq = {}
        for mv, fr in C['moves'].items():
            for k, F in enumerate(fr):
                seq.setdefault(F['cell'], (mv, k))
        items = [dict(a=a, box=b, anchor=(C['ax'], C['ay']), seq=seq.get(n), **{'with': [f]}) for n, b in enumerate(boxes)]
        info = regrain_group(items, params('crew'), 'crew_' + who)
        save(a, 'crew_%s.webp' % who)
        save(f, 'crew_%s_flash.webp' % who)
        if rep:
            report(a, boxes, 'crew_%s après' % who)
        out.append(info)
    return out


HSTRAY = 15                                                          # (la horde : un bout détaché de 15 px au plus sur le niveau de 290 px,
                                                                     #  à l'aire près sur les autres : 4 px à 150, 2 à 100, 1 à 64 et 42)


def do_horde(HRD, rep):
    sheets = [load('horde_L%d.webp' % i) for i in range(len(HRD['L']))]
    top = int(np.argmax([L['h'] for L in HRD['L']]))                # (le niveau de 290 px : ce qui y est une partie l'est partout)
    T = HRD['L'][top]
    if rep:
        for li, L in enumerate(HRD['L']):
            report(sheets[li], [F[:4] for fr in L['frames'] for F in fr], 'horde_L%d (%d px) avant' % (li, L['h']))
    ref = {}                                                         # (les parties détachées réelles du niveau du haut, par image)
    for b, fr in enumerate(T['frames']):
        for k, F in enumerate(fr):
            x, y, w, h = F[:4]
            al = sheets[top][y:y + h, x:x + w, 3] > 0
            lab, n = nd.label(al, structure=np.ones((3, 3)))
            sz = np.bincount(lab.ravel())
            sz[0] = 0
            real = np.isin(lab, np.nonzero(sz > HSTRAY)[0])
            ref[(b, k)] = (nd.binary_dilation(real, iterations=2), F)

    def keep(comp, it):                                              # (une partie : ses pixels tombent sur une partie du niveau du haut)
        li, b, k = it['lvl']
        if li == top:
            return False
        R, FT = ref[(b, k)]
        F = it['frame']
        sc = T['h'] / HRD['L'][li]['h']
        ys, xs = np.nonzero(comp)
        u = np.round(FT[4] + (xs + 0.5 - F[4]) * sc).astype(int)
        v = np.round(FT[5] + (ys + 0.5 - F[5]) * sc).astype(int)
        ok = (u >= 0) & (v >= 0) & (u < R.shape[1]) & (v < R.shape[0])
        hit = np.zeros(len(u), bool)
        hit[ok] = R[v[ok], u[ok]]
        return hit.mean() >= 0.5
    out = []
    for b in range(len(HRD['bodies'])):                              # (un personnage : un corps, ses cinq niveaux, ses 18 images)
        items = []
        for li, L in enumerate(HRD['L']):
            sc = L['h'] / T['h']
            for k, F in enumerate(L['frames'][b]):
                items.append(dict(a=sheets[li], box=F[:4], anchor=(F[4], F[5]), seq=('L%d' % li, k), keep=keep, lvl=(li, b, k), frame=F,
                                  stray=max(1, round(HSTRAY * sc * sc))))
        P = params('horde', stray=HSTRAY)
        out.append(regrain_group(items, P, 'horde corps %s' % HRD['bodies'][b]))
    for li in range(len(HRD['L'])):
        save(sheets[li], 'horde_L%d.webp' % li)
        if rep:
            report(sheets[li], [F[:4] for fr in HRD['L'][li]['frames'] for F in fr], 'horde_L%d (%d px) après' % (li, HRD['L'][li]['h']))
    return out


def do_bus(BZ, rep):
    a, sp = load('bus_zombies.webp'), load('bus_zombies_spill.webp')
    out, boxes = [], []
    groups = {}
    for sh in ('pull', 'roof', 'fall', 'fallhi', 'climb', 'emerge'):
        S = BZ[sh]
        for v, y in S['rows'].items():
            for k in range(S['n']):
                b = [k * S['w'], y, S['w'], S['h']]
                boxes.append(b)
                groups.setdefault(v, []).append(dict(a=a, box=b, anchor=(S['ax'], S['ay']), seq=(sh, k), **{'with': [sp]}))
    if rep:
        report(a, boxes, 'bus_zombies avant')
    for v, items in groups.items():                                  # (un personnage par rangée : A, B)
        out.append(regrain_group(items, params('bus'), 'bus_zombies ' + v))
    save(a, 'bus_zombies.webp')
    save(sp, 'bus_zombies_spill.webp', rgb=True)
    if rep:
        report(a, boxes, 'bus_zombies après')
    return out


def street(o):
    CRW, HRD, BZ = street_data()
    only = o.only.split(',') if o.only else ['crew', 'horde', 'bus']
    infos = []
    if 'crew' in only:
        infos += do_crew(CRW, o.report)
    if 'horde' in only:
        infos += do_horde(HRD, o.report)
    if 'bus' in only:
        infos += do_bus(BZ, o.report)
    for i in infos:
        print('%-22s %2d familles, pente %.3f au-dessus de %g (p95 visé %s), %d px détachés ôtés, %d reflets gardés, %.2f %% de pixels de même couleur changés de famille d\'une image à la suivante'
              % (i['name'], i['families'], i['slope'], i['knee'], i['p95'], i['strays'], i['glints'], 100 * i['flicker']))


def sheet(o):
    a = np.array(Image.open(o.src).convert('RGBA'))
    if o.cells:
        J = json.load(open(o.cells))
        groups = J.get('groupes', J.get('groups')) if isinstance(J, dict) else {'all': J}
    else:
        boxes = grid_cells(a.shape[1], a.shape[0], *[int(v) for v in o.grid.lower().split('x')]) if o.grid else auto_cells(a[..., 3], o.gap)
        boxes = [b for b in boxes if (a[b[1]:b[1] + b[3], b[0]:b[0] + b[2], 3] > 0).any()]
        if o.group == 'rows':                                          # (une rangée : les boîtes dont les hauteurs se chevauchent)
            groups, band = {}, None
            for b in sorted(boxes, key=lambda b: (b[1], b[0])):
                if band is None or b[1] >= band[1]:
                    band = [b[1], b[1] + b[3]]
                    groups['rangée %d' % b[1]] = []
                band[1] = max(band[1], b[1] + b[3])
                groups[list(groups)[-1]].append(b)
            for g in groups.values():
                g.sort(key=lambda b: b[0])
        else:
            groups = {'all': boxes}
    layers = [np.array(Image.open(p).convert('RGBA')) for p in (o.with_ or [])]
    allb = [b for g in groups.values() for b in g]
    if o.report:
        report(a, allb, 'avant')
    P = dict(DEF)
    for k in ('families', 'knee', 'p95', 'scale', 'merge', 'grain_k', 'stray', 'iters', 'cap', 'glint_dl'):
        v = getattr(o, k)
        if v is not None:
            P[k] = v
    for g, bs in groups.items():
        items = []
        for i, b in enumerate(bs):
            anc = [float(v) for v in o.anchor.split(',')] if o.anchor else (b[2] / 2, b[3])
            items.append(dict(a=a, box=b, anchor=anc, seq=('seq', i), **{'with': layers}))
        info = regrain_group(items, P, g)
        print('%s : %d images, %d familles, pente %.3f, %d px détachés ôtés, %.2f %% de scintillement' % (g, info['cells'], info['families'], info['slope'], info['strays'], 100 * info['flicker']))
    if o.dst.endswith('.webp'):
        Image.fromarray(a, 'RGBA').save(o.dst, 'WEBP', lossless=True, quality=100, method=6, exact=True)
    else:
        Image.fromarray(a, 'RGBA').save(o.dst)
    for p, L in zip(o.with_ or [], layers):
        q = os.path.splitext(o.dst)[0] + '_' + os.path.basename(p)
        Image.fromarray(L, 'RGBA').save(q, 'WEBP', lossless=True, quality=100, method=6, exact=True)
    if o.report:
        report(a, allb, 'après')


def main():
    ap = argparse.ArgumentParser(description='le grain des figures (voir la docstring)')
    sub = ap.add_subparsers(dest='cmd')
    ap.add_argument('--only', default=None, help='crew,horde,bus')
    ap.add_argument('--report', action='store_true')
    sp = sub.add_parser('sheet', help='un atlas quelconque')
    sp.add_argument('src')
    sp.add_argument('dst')
    sp.add_argument('--grid', default=None, help='CWxCH : une grille de cellules depuis le coin haut gauche')
    sp.add_argument('--cells', default=None, help='un JSON : {"groupes": {"nom": [[x, y, w, h], ...]}} ou une liste de boîtes')
    sp.add_argument('--gap', type=int, default=2, help='(cellules trouvées seules) les taches à gap px l\'une de l\'autre : une figure')
    sp.add_argument('--group', default='all', choices=['all', 'rows'], help='un personnage par planche, ou par rangée')
    sp.add_argument('--families', type=int, default=None)
    sp.add_argument('--knee', type=float, default=None, help='le genou de l\'étalonnage (luminance 0-255)')
    sp.add_argument('--p95', type=float, default=None, help='la cible : le p95 de luminance de chaque image (la peinture voisine + 15 %%) ; sans : pas d\'étalonnage')
    sp.add_argument('--scale', type=float, default=None, help='l\'écart OKLab que vaut un voisin de la même famille (plus grand : plus lisse)')
    sp.add_argument('--merge', type=float, default=None)
    sp.add_argument('--grain-k', dest='grain_k', type=float, default=None)
    sp.add_argument('--stray', type=int, default=None, help='la taille max (px) d\'un bout détaché ôté')
    sp.add_argument('--iters', type=int, default=None)
    sp.add_argument('--cap', type=float, default=None, help='la borne de l\'écart de couleur (0 : sans borne, un point isolé très différent reste)')
    sp.add_argument('--glint', dest='glint_dl', type=float, default=None, help='garder les reflets d\'un pixel plus clairs que leurs voisins de tant (L d\'OKLab, 0,07)')
    sp.add_argument('--anchor', default=None, help='AX,AY : l\'ancre du tramage dans chaque cellule (défaut : le milieu du bas)')
    sp.add_argument('--with', dest='with_', action='append', help='un calque lié aux pixels de la figure (même atlas) : sa moyenne par tache')
    sp.add_argument('--report', action='store_true')
    o = ap.parse_args()
    if o.cmd == 'sheet':
        sheet(o)
    else:
        street(o)


if __name__ == '__main__':
    main()
