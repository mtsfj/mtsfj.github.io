#!/usr/bin/env python3
"""Le dagashi-ya : son obaa-chan, assise derrière son comptoir dans la maquette de tools/dagashi_interior.py, tirée de la planche
du propriétaire.

    python3 tools/dagashi_obaachan.py                  (après tools/dagashi_interior.py ; réécrit assets/dagashi_obaachan.webp
                                                         et, dans assets/street.js, la ligne DGO : on peut le relancer, il écrit
                                                         la même chose)
    python3 tools/dagashi_obaachan.py --preview dossier (des aperçus seulement)

La planche (SHEET, tools/src/dagashi_obaachan_sheet_c.webp : le chignon gris et son épingle rouge, les lunettes rondes, le gilet
de laine rouge sombre sur un kimono bleu nuit à fleurs roses, le tablier beige ; le style et les proportions des gens d'Ichiraku),
sur fond blanc : derrière un comptoir bas, à mi-corps, au repos (s0), souriante les yeux fermés (s1), l'éventail (s2), assoupie
le menton dans la main (s3) ; les boules du boulier qu'elle fait glisser (a0, a1), le bonbon tendu (c0), le rire, les mains
jointes (l0) ; de dos, debout (b0), le bras levé vers l'étagère (r0), sa longue baguette à la main (k0) ; la marche de profil,
voûtée, les mains dans le dos (w0..w5). FRAMES les repère chacune par un point : une autre planche, ces points seuls.

- Découpe : la figure est ce qui s'écarte du blanc, d'un seul morceau avec ce qu'elle tient (l'éventail, le boulier, le bonbon, la
  baguette ; les petits traits de mouvement dessinés autour d'elle ôtés) ; derrière le comptoir, tout ce qui est sous son haut
  (sa première rangée qui couvre toute la largeur de la figure) ôté : la maquette a son propre comptoir, qui la cache. Seuls ses
  pixels intérieurs (le masque érodé d'un pixel) donnent la couleur : pas de liseré blanc.
- Une seule taille : debout, du haut du chignon à la semelle, TALL = 1,5 m (la vue de dos droite, HEAD_REF ; voûtée en marchant,
  un peu moins) ; les images derrière le comptoir sont dessinées plus grandes (1,64 fois : la largeur de leur tête, rangée par
  rangée, posée sur celle de la vue de dos) et ramenées à la même échelle. Dans la maquette elle est à Z_O = 26,45 m (53 px par
  mètre : 79 px debout) : assise, sa tête à 1,6 m, le haut du comptoir la coupe (la maquette sait où) ; debout sur le plancher
  surélevé, sa semelle à 0,35 m (rangée 676), la tête à 1,85 m.
- Réduction : chaque pixel de la scène est le bloc de la planche qu'il couvre ; plein si la figure en couvre au moins la
  moitié ; sa couleur, la moyenne de ses pixels intérieurs les plus proches de leur médiane (un bord ne mêle pas deux
  matières), un trait fin sur le visage ou une main gardé (INK : les lunettes, les yeux, la bouche, les doigts) ; toutes ses
  images ramenées à une palette commune (PAL couleurs : ni grain ni scintillement d'une image à l'autre).
- Lumière : allumée, la lumière de la boutique (l'étalonnage de la maquette, sous la lampe un peu plus claire : LAMP) ; éteinte
  (la coupure de courant, boutique ouverte), le sombre de la pièce éteinte selon sa clarté, à sa palette.
- La marche : les pieds mesurés sur chaque image réduite (les morceaux de ses dernières rangées) ; d'une image à la suivante le
  corps avance de dx pixels entiers, le moins qui garde un pied posé sur son pixel (jamais en arrière) : 24 px le pas.
- La place : le milieu de son buste assise à X_SEAT, son ancre sur la rangée du haut du comptoir derrière elle ; debout, sa
  semelle sur le plancher surélevé ; devant l'étagère, vue par la vitre de la porte de gauche, au plus près de SHELF_AT : d'une
  image aux pieds joints à une autre, par les mêmes images à l'aller et au retour (elle revient juste à sa place). Ce qui est
  devant elle dans la maquette (le comptoir, le poteau, le montant et le cadre de la porte, le panneau de bois sous la vitre) la
  cache : V, le masque de la devanture à sa profondeur (alpha : ce qu'on voit d'elle, la majorité des rayons du pixel passant
  derrière elle ; rouge : la vitre ; vert : le reflet de la vitre, x 40).

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

ROOT = D.ROOT
SHEET = os.path.join(ROOT, 'tools', 'src', 'dagashi_obaachan_sheet_c.webp')
OUT = 'dagashi_obaachan.webp'
JS = os.path.join(ROOT, 'assets', 'street.js')
TALL = 1.5                           # m, debout, du haut du chignon à la semelle
HEAD_REF = ('b0', ('s0', 's1', 'a0'))   # (l'échelle des images derrière le comptoir : la largeur de leur tête, rangée par rangée, posée
                                     # sur celle de cette vue de dos debout, de face elle aussi)
Z_O = 26.45                          # sa profondeur (m) : entre le comptoir et le mur du bout
X_SEAT = 192                         # le milieu de son buste, assise
SHELF_AT = 162                       # (devant l'étagère, vue par la vitre : à peu près là)
PAL = 32
FRAMES = {                           # chaque image : un point de la planche sur elle (x, y), sa sorte (derrière le comptoir, debout) ;
                                     # sa boîte est celle de la figure qui passe par ce point (une autre planche : ces points seuls)
    's0': ((128, 130), 'seat'), 's1': ((384, 130), 'seat'), 's2': ((640, 130), 'seat'), 's3': ((890, 130), 'seat'),
    'a0': ((128, 390), 'seat'), 'a1': ((384, 390), 'seat'), 'c0': ((640, 390), 'seat'), 'l0': ((890, 390), 'seat'),
    'b0': ((129, 640), 'stand'), 'r0': ((398, 640), 'stand'), 'k0': ((646, 640), 'stand'),
    'w0': ((111, 890), 'stand'), 'w1': ((369, 890), 'stand'), 'w2': ((629, 890), 'stand'), 'w3': ((889, 890), 'stand'),
    'w4': ((1146, 890), 'stand'), 'w5': ((1408, 890), 'stand')}
FAN = ('s2', (-1, 1))                # (l'éventail qui bat : s2 et sa copie, l'éventail décalé de tant)
COVER = 0.5
INK = (80, 0.16, 0.3)                # (un trait fin de la planche (plus sombre que tant) qui tient tant de son bloc sur le visage ou une
                                     # main (tant de peau) : le pixel prend sa couleur : les lunettes, les yeux, la bouche, les doigts)
LAMP = 1.1                           # (sous la lampe, juste au-dessus du comptoir : un peu plus claire que le mur)


def boxes(sheet):
    """la boîte de chaque image de FRAMES : la figure (ce qui s'écarte du blanc) qui passe par son point (ou la plus proche), et ce
    qui est dans sa boîte sans être à une autre"""
    m = sheet.min(2) < 225
    lab, n = nd.label(m); sl = nd.find_objects(lab); sz = nd.sum(m, lab, range(1, n + 1))
    big = [i for i in range(n) if sz[i] >= 40]
    own = {}
    for k, ((x, y), _) in FRAMES.items():
        i = lab[y, x] - 1
        if i < 0 or sz[i] < 2000:
            mid = lambda j: ((sl[j][1].start + sl[j][1].stop) / 2, (sl[j][0].start + sl[j][0].stop) / 2)
            i = min((j for j in big if sz[j] >= 2000), key=lambda j: np.hypot(mid(j)[0] - x, mid(j)[1] - y))
        own[k] = i
    out = {}
    for k, i in own.items():
        y0, y1, x0, x1 = sl[i][0].start, sl[i][0].stop, sl[i][1].start, sl[i][1].stop
        for j in big:                                                        # (un éventail, un bonbon détachés : dans sa boîte)
            if j in own.values() and j != i: continue
            if sl[j][1].start >= x0 - 6 and sl[j][1].stop <= x1 + 6 and sl[j][0].start >= y0 - 6 and sl[j][0].stop <= y1 + 6:
                y0, y1, x0, x1 = min(y0, sl[j][0].start), max(y1, sl[j][0].stop), min(x0, sl[j][1].start), max(x1, sl[j][1].stop)
        out[k] = (x0, y0, x1, y1)
    return out


def frame(sheet, box, kind):
    """une image : ses couleurs (RGB), son masque, son ancre (x : le milieu du buste ; y : le haut du comptoir ou la semelle)"""
    x0, y0, x1, y1 = box
    rgb = sheet[y0 - 3:y1 + 3, x0 - 3:x1 + 3].astype(float); m = rgb.min(2) < 225
    if kind == 'seat':                                                     # (le comptoir : en bas, les rangées qui couvrent toute la
        top = m.shape[0] - 4                                               # largeur de la figure ; la première d'entre elles)
        while top > 0 and m[top - 1, 3:-3].mean() >= 0.97: top -= 1
        m[top:] = False
    lab, n = nd.label(m)
    if n > 1:                                                              # (les poussières, les traits de mouvement dessinés autour
        sz = nd.sum(m, lab, range(1, n + 1)); m &= np.isin(lab, 1 + np.nonzero(sz >= 0.15 * sz.max())[0])   # d'elle : dehors)
    ys, xs = np.nonzero(m)
    if kind == 'seat': ay = top
    else: ay = ys.max() + 1
    H = ay - ys.min()
    band = (ys > ys.min() + 0.45 * H) & (ys < ys.min() + 0.75 * H)          # (le buste : sa colonne médiane)
    return dict(rgb=rgb, m=m, ax=float(np.median(xs[band])) + 0.5, ay=float(ay), top=int(ys.min()), org=(x0 - 3, y0 - 3), kind=kind)


def head_ratio(F):
    """de combien les images derrière le comptoir sont dessinées plus grandes que celles debout : la largeur de la figure rangée par
    rangée du haut de sa tête, posée au mieux sur celle de la vue de dos HEAD_REF (sa tête et son cou), la médiane"""
    def prof(f, n):
        m = f['m']; t = f['top']
        return np.array([np.ptp(np.nonzero(m[t + y])[0]) + 1 if m[t + y].any() else 0 for y in range(n)], float)
    ref, seats = HEAD_REF
    hb = int(0.22 * (F[ref]['ay'] - F[ref]['top'])); wb = prof(F[ref], hb)
    out = []
    for k in seats:
        ws = prof(F[k], 3 * hb)
        err = lambda r: np.abs(np.interp(np.arange(hb) * r, np.arange(3 * hb), ws) / r - wb)[hb // 10:].mean()
        out.append(min(np.arange(0.8, 2.5, 0.005), key=err))
    return float(np.median(out))


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
            ink = px.max(1) < INK[0]; skin = (px[:, 0] > 170) & (px[:, 1] > 110) & (px[:, 0] - px[:, 2] > 40)
            if ink.mean() >= INK[1] and skin.mean() >= INK[2]: px = px[ink]     # (un trait fin sur le visage, les mains : gardé)
            med = np.median(px, 0); dd = np.abs(px - med).sum(1)
            out[i, j, :3] = px[dd <= np.median(dd)].mean(0) if len(px) > 3 else px.mean(0); out[i, j, 3] = 1
    return out


def feet(c):
    """les pieds d'une image de marche réduite : les morceaux de ses deux dernières rangées pleines (leurs colonnes)"""
    a = c[..., 3] > 0; rows = np.nonzero(a.any(1))[0]; b = rows.max()
    lab, n = nd.label(a[b - 2:b + 1].any(0))
    return sorted((float(np.nonzero(lab == k)[0].mean()), int((lab == k).sum())) for k in range(1, n + 1))


def main():
    prev = sys.argv[sys.argv.index('--preview') + 1] if '--preview' in sys.argv else None
    sheet = np.asarray(Image.open(SHEET).convert('RGB'))
    B = boxes(sheet)
    F = {k: frame(sheet, B[k], kind) for k, (_, kind) in FRAMES.items()}
    s_scene = D.F / Z_O                                                    # (px de la scène par mètre, à sa profondeur)
    ref = F[HEAD_REF[0]]; s_w = s_scene * TALL / (ref['ay'] - ref['top'])  # (px de la scène par px de la planche : debout, d'après la
                                                                           # vue de dos droite ; voûtée en marchant, moins haute)
    head = head_ratio(F); s_s = s_w / head
    cells = {}
    for k, f in F.items():
        s = s_s if f['kind'] == 'seat' else s_w
        ys, xs = np.nonzero(f['m'])
        AX = int(np.ceil((f['ax'] - xs.min()) * s)) + 1; AY = int(np.ceil((f['ay'] - ys.min()) * s)) + 1
        W = AX + int(np.ceil((xs.max() + 1 - f['ax']) * s)) + 1; H = AY + (3 if f['kind'] == 'seat' else 0)
        c = reduce(f, s, AX, AY, W, H)
        if f['kind'] == 'seat':                                             # (sous le haut du comptoir : sa dernière rangée, trois fois,
            for r in range(AY, H): c[r] = c[AY - 1]                         # que son souffle ne découvre rien)
        cells[k] = [c, AX, AY]
        print('%s : %d x %d, ancre (%d, %d), %.3f px de la scène par px de la planche' % (k, W, H, AX, AY, s))
    print('assise : dessinée %.2f fois plus grande que debout' % head)
    # l'éventail qui bat : une copie de s2, l'éventail (ses pixels clairs, son cercle rouge, ses nervures) décalé ; ce qu'il
    # découvre repris de s0 (la même pose, sans lui)
    k, (dx, dy) = FAN
    c, AX, AY = cells[k]; c0_, AX0, AY0 = cells['s0']
    fan = np.zeros(c.shape[:2], bool)
    rgbf = c[..., :3]; a = c[..., 3] > 0
    pale = a & (rgbf.min(2) > 175) & (np.ptp(rgbf, 2) < 60)
    lab_, n_ = nd.label(nd.binary_closing(pale, iterations=2))
    big = 1 + int(np.argmax(nd.sum(pale, lab_, range(1, n_ + 1))))
    disk = nd.binary_fill_holes(lab_ == big)
    fan = disk & a
    b = c.copy()
    for y, x in zip(*np.nonzero(fan)):                                     # (d'abord ce qu'il découvre : s0 là)
        yy, xx = y - AY + AY0, x - AX + AX0
        b[y, x] = c0_[yy, xx] if 0 <= yy < c0_.shape[0] and 0 <= xx < c0_.shape[1] else 0
    for y, x in zip(*np.nonzero(fan)):
        if 0 <= y + dy < b.shape[0] and 0 <= x + dx < b.shape[1]: b[y + dy, x + dx] = c[y, x]
    cells['s2b'] = [b, AX, AY]

    # la lumière de la boutique (l'étalonnage de la maquette), une palette commune ; éteinte, le sombre de la pièce éteinte
    R = D.cut()
    lo, hi, dpal = R['dark_ramp']
    lit_px = np.concatenate([D.grade(c[c[..., 3] > 0][:, :3] * LAMP) for c, _, _ in cells.values()])
    pal = D.palette(lit_px, PAL)
    LIT, DARK = {}, {}
    for k, (c, AX, AY) in cells.items():
        a = c[..., 3] > 0
        L = np.zeros(c.shape); Dk = np.zeros(c.shape)
        q = pal[D.nearest(D.grade(c[a][:, :3] * LAMP), pal)]
        L[a] = np.concatenate([q, np.full((len(q), 1), 255.0)], 1)
        t = np.clip((q @ I.LUM - 25) / 175, 0, 1) ** 0.85
        dq = dpal[D.nearest(lo + (hi - lo) * t[:, None], dpal)]
        Dk[a] = np.concatenate([dq, np.full((len(dq), 1), 255.0)], 1)
        LIT[k], DARK[k] = L, Dk

    # la marche : les pieds de chaque image (par rapport à l'ancre) ; d'une image à la suivante le corps avance du moins qui garde un
    # pied posé sur son pixel (jamais en arrière) ; le trajet jusqu'à l'étagère : d'une image aux pieds joints à une autre, au plus
    # près de SHELF_AT, par les mêmes images à l'aller et au retour (il revient juste à sa place)
    cyc = [k for k in FRAMES if k[0] == 'w']; L = len(cyc)
    ft = {k: [x - cells[k][1] for x, n in feet(cells[k][0])] for k in cyc}
    step = []
    for k0, k1 in zip(cyc, cyc[1:] + cyc[:1]):
        d = [f - g for f in ft[k0] for g in ft[k1] if f - g >= -1]
        step.append(max(0, int(round(min(d)))) if d else 0)
    joined = [i for i, k in enumerate(cyc) if len(ft[k]) == 1]
    trip = min(((i, n) for i in joined for n in range(1, 3 * L) if (i + n) % L in joined),
               key=lambda q: abs(X_SEAT - sum(step[(q[0] + j) % L] for j in range(q[1])) - SHELF_AT) + 0.5 * q[1])
    shelf = X_SEAT - sum(step[(trip[0] + j) % L] for j in range(trip[1]))
    print('pieds', {k: [round(x, 1) for x in v] for k, v in ft.items()}, '| pas', step, '| foulée', sum(step), 'px | vers l\'étagère',
          trip, '->', shelf)

    # le masque de la devanture à sa profondeur : ce qu'on voit d'elle (la majorité des rayons du pixel passent derrière elle),
    # la vitre, son reflet
    zx0, zy0, zx1, zy1 = D.ZONE
    V = np.zeros((zy1 - zy0, zx1 - zx0, 4))
    for (x, y), gl, z, sh in zip(R['pix'], R['glass'], R['Zh'], R['sheen']):
        if (z > Z_O).mean() >= 0.5: V[y - zy0, x - zx0] = (255 * gl, 40 * sh, 0, 255)

    # l'atlas : la rangée allumée, la rangée éteinte sous elle, le masque à leur droite
    keys = list(cells)
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
    rise = (y_seat - out['s0'][5]) - (y_stand - out[cyc[trip[0]]][5])     # (debout, sa tête plus haut qu'assise de tant)
    DGO = {'cells': out, 'dark': Hl + 1, 'V': [Wl, 0, V.shape[1], V.shape[0], zx0, zy0],
           'seat': [X_SEAT, y_seat], 'stand': y_stand, 'shelf': shelf, 'trip': list(trip), 'walk': cyc, 'step': step, 'rise': rise,
           'z': Z_O, 'ppm': round(D.F / Z_O, 2)}
    print('Z_O %.2f m (%.1f px/m) : assise, le comptoir à la rangée %d ; debout, la semelle à %d (%d px plus haut) | atlas %d x %d, '
          'palette %d couleurs' % (Z_O, D.F / Z_O, y_seat, y_stand, rise, A.shape[1], A.shape[0], len(pal)))
    if prev:
        bg = np.full(A.shape[:2] + (3,), 128.0); al = A[..., 3:] / 255
        im = Image.fromarray(np.clip(bg * (1 - al) + A[..., :3] * al, 0, 255).astype(np.uint8))
        im.resize((A.shape[1] * 4, A.shape[0] * 4), Image.NEAREST).save(os.path.join(prev, 'atlas_x4.png'))
        json.dump(DGO, open(os.path.join(prev, 'dgo.json'), 'w'))
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
