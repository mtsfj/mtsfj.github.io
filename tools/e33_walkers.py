#!/usr/bin/env python3
"""Les passants du Gommage (Clair Obscur : Expedition 33) : deux personnages, tirés des planches du propriétaire.

    python3 tools/e33_walkers.py      (lit tools/src/e33_walker_sheet_24.webp et e33_walker_sheet_23.jpg ;
                                       écrit assets/e33_walkers.webp et la description WKS dans assets/street.js)

Chaque planche est une figure en pixel art sur fond blanc, de profil vers la droite : une rangée de marche (8 images), une
rangée où elle s'arrête et se tourne jusqu'au dos, une rangée de vues de dos puis de face. La 23 a des filets noirs entre
ses rangées (laissés de côté) et une vue de dos sans parapluie (sautée). Pour chaque personnage, le même traitement :

- Découpe : le masque est ce qui s'écarte du blanc (le plus pâle des trois canaux sous 225), les rangées repérées par leurs
  bandes non blanches, les images par les colonnes blanches qui les séparent ; seuls les pixels intérieurs (le masque
  érodé d'un pixel) donnent la couleur, les pixels de bord mêlés au blanc ne comptent que pour la couverture : pas de
  liseré clair.
- Échelle et ligne de sol : la personne (du haut du chapeau à la semelle, mesurés sur la planche) fait 36 px, 1,71 m à
  21 px le mètre, l'échelle du trottoir du fond (les portes de la maison du fond : 2 m pour 44 px ; l'ancien passant :
  1,65 m pour 35 px) ; la semelle la plus basse de chaque image sur la rangée AY de la cellule.
- Réduction : chaque pixel de la scène est le bloc de pixels de la planche qu'il couvre ; opaque si la figure en couvre
  au moins 45 % ; sa couleur, la moyenne des pixels intérieurs les plus proches de leur médiane (la moitié la plus
  proche : un bord ne mêle pas deux matières, pas de bouillie), puis toutes les images d'un personnage ramenées à une
  palette commune (k-moyennes, 22 couleurs : ni grain ni scintillement d'une image à l'autre). Un pixel de bord (mêlé au
  blanc) prend la couleur du pixel intérieur le plus proche : une baleine, un doigt gardent leur couleur, sans blanc.
- Le manteau sans moucheture : un pixel seul de sa couleur (aucun de ses quatre voisins ne l'a) dont deux voisins au moins
  partagent une couleur proche de la sienne (SPECK, dans la palette) la prend ; l'écharpe, le visage, les bottes, loin des
  tons du manteau, restent. Le masque ne bouge pas : l'alpha (le tour du Gommage) est le même.
- Étalonnage : chaque planche ramenée à la même exposition (la luminance médiane de la figure), puis passée de son plein
  jour au crépuscule de ce trottoir comme l'ancien passant l'était (son manteau (19, 19, 34), son écharpe (84, 24, 40),
  sa peau (66, 50, 62)) : en linéaire, la luminance presque proportionnelle dans les sombres et les clairs retenus (un
  visage sous le parapluie), la teinte de la planche gardée et passée à la lumière bleutée du soir ; street.js les
  rééchelonne par la lumière de la rue à ses pieds.
- Ancres : la colonne AX de chaque cellule est le milieu du buste (la médiane des pixels du buste et des hanches, sans
  l'écharpe qui vole).
- Marche : les images de marche des deux planches gardent leurs deux bottes presque au même endroit sous le corps (la 23
  ne bouge pas les jambes) : avancées telles quelles, elles glisseraient. Le pas est mesuré sur la planche (l'écart entre
  les deux bottes posées, sa médiane) ; la foulée (deux pas), arrondie au pixel, fixe l'avance du corps, dx[i] pixels
  entiers à l'image i. Sous l'ourlet du manteau, les jambes sont reposées : la botte de la planche (ses pixels), la tige
  de la jambe à la couleur de ses pixels ; chaque pied posé 5 images sur 8 à sa place au sol (il recule dans la cellule
  d'autant que le corps avance : il reste sur son pixel), puis 3 en l'air jusqu'au pas suivant ; le pied lointain un ton
  plus sombre. La vitesse : la foulée en 1,1 s.
- Gommage : l'alpha de chaque pixel opaque est son tour dans le Gommage, 128 (le premier) .. 255 : les bords d'abord,
  en semis (un tirage fixe).
- Pétales : le rouge de l'écharpe de chaque personnage (ses pixels les plus rouges, étalonnés), pour ses pétales.

L'atlas : une rangée de cellules de CW x CH par personnage (la marche, l'arrêt et le demi-tour, le dos, la face). La
description (WKS) est écrite dans street.js entre ses marqueurs : street.js ne fait que la lire (une nouvelle planche
est un changement de données). Il faut Pillow, numpy, scipy.
"""
import json, os, re
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CW, CH, AX, AY = 32, 48, 15, 45                 # la cellule, la colonne du buste, la rangée de la semelle
PERSON = 36                                     # px, du haut du chapeau à la semelle (1,71 m à 21 px/m)
PAL = 22
SPECK = 0.09                                    # (le manteau sans moucheture : l'écart de couleur, sRGB 0-1, qu'un point seul franchit)
CHARS = [
    # src, hauteur de la personne sur la planche (px), rangées : (rôle, nombre d'images, images sautées)
    dict(id='a', src='tools/src/e33_walker_sheet_24.webp', person=274,
         rows=[('walk', 8, ()), ('turn', 4, ()), ('backfront', 4, ())], back=2),
    dict(id='b', src='tools/src/e33_walker_sheet_23.jpg', person=205,
         rows=[('walk', 8, ()), ('turn', 6, ()), ('backfront', 6, (2,))], back=2),
]
LUMA = np.array([0.2126, 0.7152, 0.0722])
EXPO = 0.012                                    # (chaque planche ramenée à la même exposition : la luminance médiane de la figure)
GRADE_K, GRADE_G, GRADE_S, GRADE_T = 0.62, 1.12, 0.12, np.array([0.9, 0.9, 2.2])   # (l'ancien passant : manteau (19, 19, 34), écharpe (84, 24, 40), peau (66, 50, 62))


def lin(c): c = np.asarray(c, float) / 255; return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
def srgb(c): c = np.clip(c, 0, 1); return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055) * 255


def runs(v, gap=1, minw=5):
    out, s = [], None
    for i, x in enumerate(v):
        if x and s is None: s = i
        if not x and s is not None: out.append((s, i - 1)); s = None
    if s is not None: out.append((s, len(v) - 1))
    return [r for r in out if r[1] - r[0] >= minw]


def frames(ch):
    im = np.array(Image.open(os.path.join(ROOT, ch['src'])).convert('RGB')).astype(int)
    fig = im.min(2) < 225
    fig[fig.mean(1) > 0.95] = False                                   # (les filets entre les rangées)
    bands = runs(fig.any(1), minw=60)
    assert len(bands) == len(ch['rows']), bands
    out = []
    for (y0, y1), (role, n, skip) in zip(bands, ch['rows']):
        lo = y0 + int(0.4 * (y1 - y0))                                # (les corps : sous les parapluies, qui se touchent parfois)
        cols = runs(fig[lo:y1 + 1].any(0), minw=20)
        assert len(cols) == n, (role, cols)
        cnt = fig[y0:y1 + 1].sum(0)                                   # (la coupe : la colonne la plus vide entre deux corps)
        cuts = [0] + [cols[i][1] + int(np.argmin(cnt[cols[i][1]:cols[i + 1][0] + 1])) for i in range(n - 1)] + [im.shape[1]]
        for k in range(n):
            x0, x1 = cuts[k], cuts[k + 1]
            if k in skip: continue
            m = fig[y0:y1 + 1, x0:x1 + 1]
            lab, nl = ndimage.label(m)                                # (les poussières : dehors)
            if nl > 1:
                sz = ndimage.sum(m, lab, range(1, nl + 1)); keep = np.isin(lab, 1 + np.nonzero(sz >= 40)[0]); m = m & keep
            out.append(dict(role=role, k=k, rgb=im[y0:y1 + 1, x0:x1 + 1], m=m))
    return out


def measure(f, s):                              # la semelle, le milieu du buste (px de planche)
    m = f['m']; ys, xs = np.nonzero(m); sole = ys.max()
    P = PERSON / s
    c = f['rgb'][ys, xs]; red = (c[:, 0] - np.maximum(c[:, 1], c[:, 2])) > 40      # (l'écharpe qui vole : dehors)
    band = (ys > sole - 0.82 * P) & (ys < sole - 0.42 * P) & ~red      # (le buste et les hanches)
    f['sole'] = sole; f['cx'] = float(np.median(xs[band]))


def stance(F, s):                               # le pas : l'écart entre les deux bottes, posées, sur la planche (px de la scène)
    gaps = []
    for f in F:
        m = f['m']; sole = f['sole']; h = int(round(0.05 * PERSON / s))
        lab, nl = ndimage.label(m[sole - h:sole + 1]); cs = []
        for i in range(1, nl + 1):
            ys, xs = np.nonzero(lab == i)
            if len(xs) >= 6: cs.append(xs.mean())
        if len(cs) == 2: gaps.append(abs(cs[1] - cs[0]) * s)
    return float(np.median(gaps)), len(gaps)


def cell(f, s):                                 # une image réduite à la cellule : RGBA linéaire (A : couverture)
    rgb, m = lin(f['rgb']) * f.get('expo', 1.0), f['m']
    inner = ndimage.binary_erosion(m, iterations=1)
    iy, ix = ndimage.distance_transform_edt(~inner, return_distances=False, return_indices=True)
    rgb = rgb[iy, ix]                                                 # (chaque pixel : la couleur de l'intérieur le plus proche)
    H, W = m.shape
    out = np.zeros((CH, CW, 4))
    # le pixel (i, j) de la cellule couvre sur la planche x in [ (j - AX - sub) / s + cx, ... + 1/s ), y pareil depuis la semelle
    for i in range(CH):
        ya = (i - AY - 1) / s + f['sole'] + 1; yb = ya + 1 / s
        for j in range(CW):
            xa = (j - AX) / s + f['cx'] + 0.5; xb = xa + 1 / s
            r0, r1 = int(np.floor(ya)), int(np.ceil(yb)); c0, c1 = int(np.floor(xa)), int(np.ceil(xb))
            if r1 <= 0 or c1 <= 0 or r0 >= H or c0 >= W: continue
            r0c, r1c, c0c, c1c = max(r0, 0), min(r1, H), max(c0, 0), min(c1, W)
            wy = np.clip(np.minimum(np.arange(r0c, r1c) + 1, yb) - np.maximum(np.arange(r0c, r1c), ya), 0, 1)
            wx = np.clip(np.minimum(np.arange(c0c, c1c) + 1, xb) - np.maximum(np.arange(c0c, c1c), xa), 0, 1)
            w = wy[:, None] * wx[None, :]
            mm = m[r0c:r1c, c0c:c1c]; cov = (w * mm).sum() / (1 / s) ** 2
            if cov < 0.45: continue
            ii = mm & (w > 0.2)
            if not ii.any(): ii = mm
            px = rgb[r0c:r1c, c0c:c1c][ii]
            med = np.median(px, 0); dd = np.abs(px - med).sum(1)
            sel = px[dd <= np.median(dd)] if len(px) > 3 else px
            out[i, j, :3] = sel.mean(0); out[i, j, 3] = 1
    return out


def legs(cells, st, n):                         # la marche : les bottes de la planche reposées pas à pas (le pied posé fixe au sol)
    # (voir « Marche » plus haut : le corps de chaque image gardé, ses jambes reposées sous l'ourlet)
    def hem(c):                                 # la dernière rangée du manteau au-dessus des jambes
        a = c[..., 3] > 0
        for r in range(AY - 3, 0, -1):
            if a[r].sum() >= 8: return r
        return AY - 3
    c0 = cells[0]; a0 = c0[..., 3] > 0; h0 = hem(c0)
    lab, nl = ndimage.label(a0[AY - 2:AY + 1])                        # (les bottes : les trois dernières rangées)
    blobs = sorted([np.nonzero(lab == i) for i in range(1, nl + 1)], key=lambda b: -len(b[1]))[:2]
    boots = []
    for ys, xs in blobs:
        x0 = xs.min(); boots.append([(int(y), int(x - x0), c0[AY - 2 + y, x, :3].copy()) for y, x in zip(ys, xs)])
    boot = max(boots, key=len)                                        # (la plus nette des deux)
    shin = np.median(np.array([c0[r, x, :3] for r in range(h0 + 1, AY - 2) for x in range(CW) if a0[r, x]] or [b[2] for b in boot]), 0)
    blen = max(b[1] for b in boot) + 1
    q = st / 4                                                        # (le pied posé devant le corps d’un demi-pas)
    body = lambda L: int(np.floor((L % n) * st / n)) + (L // n) * st   # (la place du corps à l'image L, comptée depuis ce cycle)
    out = []
    for i, c in enumerate(cells):
        c = c.copy(); hr = hem(c)
        c[hr + 1:, :, 3] = 0
        b = body(i)
        for ph, dark in ((4, 0.72), (0, 1.0)):                        # (le pied lointain d'abord, le proche par-dessus)
            k = (i - ph) % n                                          # (0 : il se pose ; 0..4 posé ; 5..7 en l'air)
            land = body(i - k) + int(round(q))                        # (là où il s'est posé)
            if k <= 4: wx, lift = land, 0
            else:
                u = (k - 4) / 4; u = u * u * (3 - 2 * u)
                wx, lift = int(round(land + st * u)), 1 if k == 6 else 0
            fx = AX + wx - b                                       # (la cellule : le pied à sa place au sol, le corps à dx[i])
            hx = AX + 0.45 * (fx - AX)                                # (la jambe sort de l'ourlet entre la hanche et le pied)
            for r in range(hr + 1, AY - 1 - lift):
                t = (r - hr) / max(1, AY - 1 - lift - hr); x = hx + (fx - hx) * t
                for xx in (int(np.floor(x)), int(np.floor(x)) + 1):
                    if 0 <= xx < CW: c[r, xx, :3] = shin * dark; c[r, xx, 3] = 1
            for (y, x, col) in boot:
                yy, xx = AY - 2 + y - lift, fx - blen // 2 + x
                if 0 <= yy < CH and 0 <= xx < CW: c[yy, xx, :3] = col * dark; c[yy, xx, 3] = 1
        out.append(c)
    return out


def grade(c):                                   # du jour de la planche au crépuscule du trottoir du fond (linéaire)
    # la luminance comprimée comme l'ancien passant la portait (presque proportionnelle dans les sombres, les clairs
    # retenus : un visage sous le parapluie), la teinte de la planche gardée puis passée à la lumière bleutée du soir
    Y = (c * LUMA).sum(-1, keepdims=True); r = c / np.maximum(Y, 1e-5)
    Yo = GRADE_K * Y ** GRADE_G / np.sqrt(1 + (Y / GRADE_S) ** 2)
    return Yo * r * GRADE_T


def palette(cells, n=PAL, seed=7):
    px = np.concatenate([c[c[..., 3] > 0][:, :3] for c in cells])
    v = srgb(px) / 255
    rng = np.random.default_rng(seed); C = v[rng.choice(len(v), n, replace=False)]
    for _ in range(30):
        lab = ((v[:, None] - C[None]) ** 2).sum(2).argmin(1)
        for k in range(n):
            if (lab == k).any(): C[k] = v[lab == k].mean(0)
    return C


def despeckle(lab, a, C, tol=SPECK, passes=3):  # les points seuls du manteau rendus à la couleur de leurs voisins (voir plus haut)
    H, W = lab.shape
    for _ in range(passes):
        L = np.pad(np.where(a, lab, -1), 1, constant_values=-1)
        nb = np.stack([L[:-2, 1:-1], L[2:, 1:-1], L[1:-1, :-2], L[1:-1, 2:]], -1)
        alone = a & ~(nb == lab[..., None]).any(-1)
        best, bn = lab.copy(), np.zeros((H, W), int)
        for j in range(4):
            k = nb[..., j]
            n = (nb == k[..., None]).sum(-1)
            near = (k >= 0) & (np.sqrt(((C[np.maximum(k, 0)] - C[lab]) ** 2).sum(-1)) <= tol)
            take = near & (n > bn)
            best, bn = np.where(take, k, best), np.where(take, n, bn)
        new = np.where(alone & (bn >= 2), best, lab)
        if (new == lab).all():
            break
        lab = new
    return lab


def order(a, seed):                             # le tour de chaque pixel dans le Gommage, 0 (le premier) .. 1
    d = ndimage.distance_transform_edt(a)
    rng = np.random.default_rng(seed)
    o = 0.5 * np.clip((d - 1) / 3, 0, 1) + 0.5 * rng.random(a.shape)
    return (o - o[a].min()) / max(1e-6, o[a].max() - o[a].min())


def build():
    rows, desc = [], {'cw': CW, 'ch': CH, 'ax': AX, 'ay': AY, 'chars': []}
    for ci, ch in enumerate(CHARS):
        F = frames(ch); s = PERSON / ch['person']
        Y = np.concatenate([(lin(f['rgb'][f['m']]) * LUMA).sum(1) for f in F]); expo = EXPO / float(np.median(Y))
        for f in F: measure(f, s); f['expo'] = expo
        W = [f for f in F if f['role'] == 'walk']
        step, ng = stance(W, s)
        st = int(round(2 * step)); n = len(W)
        cells, roles = [], {'walk': [], 'turn': [], 'back': [], 'front': []}
        wc = legs([cell(f, s) for f in W], st, n)
        for c in wc: cells.append(c); roles['walk'].append(len(cells) - 1)
        dx = [int(np.floor(i * st / n)) for i in range(n)]
        for f in F:
            if f['role'] == 'walk': continue
            cells.append(cell(f, s))
            if f['role'] == 'turn': roles['turn'].append(len(cells) - 1)
            else: roles['back' if f['k'] < ch['back'] else 'front'].append(len(cells) - 1)
        g = [np.concatenate([grade(c[..., :3]), c[..., 3:]], 2) for c in cells]
        C = palette(g)
        out = []
        for i, c in enumerate(g):
            a = c[..., 3] > 0
            v = srgb(c[..., :3]) / 255
            lab = despeckle(((v[..., None, :] - C[None, None]) ** 2).sum(3).argmin(2), a, C)
            q = np.round(C[lab] * 255).astype(np.uint8)
            o = order(a, 33 + 100 * ci + i)
            rgba = np.zeros((CH, CW, 4), np.uint8); rgba[..., :3] = np.where(a[..., None], q, 0)
            rgba[..., 3] = np.where(a, 128 + np.round(127 * o), 0).astype(np.uint8)
            out.append(rgba)
        P = np.round(C * 255).astype(int)                             # (le rouge de l'écharpe : la couleur de la palette la plus rouge)
        sc = [(p[0] - max(p[1], p[2])) / (1 + p.max()) for p in P]
        red = P[int(np.argmax(sc))].tolist()
        rows.append(out)
        desc['chars'].append({'id': ch['id'], 'row': ci, 'stride': st, 'v': round(st / 1.1, 1), 'dx': dx, 'walk': roles['walk'], 'turn': roles['turn'],
                              'back': roles['back'], 'front': roles['front'], 'red': red})
        print('%s: %d images, pas mesuré %.2f px (%d images), foulée %d px, vitesse %.1f px/s' % (ch['id'], len(cells), step, ng, st, st / 1.1))
    n = max(len(r) for r in rows)
    A = Image.new('RGBA', (CW * n, CH * len(rows)), (0, 0, 0, 0))
    for ri, r in enumerate(rows):
        for i, c in enumerate(r): A.paste(Image.fromarray(c, 'RGBA'), (i * CW, ri * CH))
    desc['n'] = n; desc['rows'] = len(rows)
    A.save(os.path.join(ROOT, 'assets', 'e33_walkers.webp'), 'WEBP', lossless=True, quality=100, method=6, exact=True)
    js = os.path.join(ROOT, 'assets', 'street.js'); s = open(js, encoding='utf-8').read()
    line = '  const WKS = ' + json.dumps(desc, separators=(',', ':')) + ';   // (tools/e33_walkers.py)'
    s2, k = re.subn(r'^  const WKS = .*;   // \(tools/e33_walkers\.py\)$', lambda _: line, s, flags=re.M)
    if k == 1: open(js, 'w', encoding='utf-8').write(s2); print('street.js : WKS mis à jour')
    else: print(line)
    print('assets/e33_walkers.webp : %d x %d cellules de %d x %d' % (n, len(rows), CW, CH))


if __name__ == '__main__':
    build()
