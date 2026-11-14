#!/usr/bin/env python3
"""Naruto à sa fenêtre, en couleur : ses images peintes dans le style de la rue, une par case de sa planche
(assets/naruto_col.webp).

    python3 tools/naruto_col.py                 (lit les planches peintes tools/src/naruto_paint_*.webp, les silhouettes
                                                 du rig assets/naruto_sil.webp et la table NC de assets/street.js ; écrit
                                                 assets/naruto_col.webp ; on peut le relancer, il écrit la même chose)
    python3 tools/naruto_col.py --preview DIR   (des aperçus seulement : la planche x4 sur la lumière de la pièce)

Le propriétaire : « Naruto à faire idem s'il ne suit pas les mêmes règles » : comme Red (tools/center_red.py), peint dans
le style de la peinture, sans contour, aussi sombre que ce qui l'entoure. Ses planches (tools/src/naruto_paint_*.webp :
quatre planches, 64 images, chacune d'après un guide de poses tiré des silhouettes de son rig, assets/naruto_sil.webp,
tools/naruto_sil.py, et pour le style d'après la rue autour de sa fenêtre et Kirua sur son toit : du pixel art peint, un
modelé doux tramé, les couleurs éteintes de la nuit, des proportions vraies, aucun trait de contour ; sur fond vert uni) :
Naruto à seize ans, celui de l'arc de Pain (le propriétaire : « je préfère la version jeune ou arc Pain » ; celui-ci, pour
qu'il reste le client d'Ichiraku), ses cheveux en pointes un peu plus longs sur un long bandeau noir et sa plaque, une tête
aux proportions vraies, ses yeux bleus, ses moustaches, sa veste orange aux épaules et au col noirs, son pantalon orange, ses
sandales ; la lampe chaude de la pièce derrière lui en liseré, le côté qu'on voit dans l'ombre froide de la rue. Chaque
planche suit son guide image pour image (GUIDE) ; les profils peints tournés vers la droite sont retournés (FLIP).

Chaque planche : son fond vert ôté (tout ce où le vert domine, et le pixel de bord mêlé de vert ; le vert ôté du reste, sans
toucher ses couleurs, où le vert ne domine jamais), chaque figure d'un seul tenant, rangée par rangée, le côté où il regarde
noté (SIDES : de face, de dos, de profil vers la gauche, comme la caméra le voit), ce qu'elle est (un pas de sa marche, de sa
course, une pose). Chaque case de la planche (les 92 images de ses allures, NC) prend la figure peinte sur son propre guide
(toute la marche, les pas pairs de la course, le demi-tour, les gestes) ; les autres cases, parmi les figures qui regardent du
même côté et sont de son allure (et leur miroir pour la course : l'autre pied), celle qui couvre le mieux leur silhouette du
rig ; chacune ramenée à sa hauteur (des cheveux aux semelles), posée sur son point au sol et décalée de quelques pixels au
mieux ; réduite à cette hauteur, chaque pixel de SUB x SUB points de la peinture (comme tools/ichiraku_figures.py, pick : plein
dès la moitié couverte, la couleur de ses traits sombres s'ils en couvrent assez, ses yeux, ses sourcils, ses moustaches, sinon
la moyenne du reste : pas de bouillie autour du visage), son plus grand morceau seul.

Sa lumière et ses valeurs, comme Red : la rue froide sur le côté qu'on voit (AMB), la lampe de la pièce sur son bord tourné
vers elle (RIM : en haut, ses cheveux et ses épaules ; ses côtés, moins), ses couleurs éteintes (CHROMA) ; toutes ses cases
ramenées à FAMILIES familles de tons communes, et le bleu de ses yeux (rien ne change de teinte d'une image à l'autre), gardées dans la clarté de ce
qui l'entoure à sa profondeur (VALUES : mesuré à 22 h la fenêtre allumée, la pièce derrière lui L* 40 en médiane, 50 au
p90, Kirua sur son toit 34 et 40, la façade autour 7 à 17 : ses clartés au-dessus de 24 ramenées sous 44, plus sombre que
la pièce, à contre-jour), pas de trait sombre au bord (tools/ichiraku_figures.py : no_outline), peu de pixels seuls (ses yeux
gardés), un grain fin en carreau. Ses allures, leur rythme et leurs points au sol restent ceux du rig ; sa forme est celle de
la peinture (street.js la prend par majorité).
Il faut Pillow, numpy, scipy (et ce qu'il faut à tools/ichiraku_figures.py).
"""
import json
import os
import re
import sys
import numpy as np
from PIL import Image
from scipy.ndimage import binary_erosion, label

sys.dont_write_bytecode = True
ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import ichiraku_figures as FG                                    # noqa: E402
import ichiraku_interior as R                                    # noqa: E402

RACINE = os.path.dirname(ICI)
SIL = os.path.join(RACINE, 'assets', 'naruto_sil.webp')
OUT = os.path.join(RACINE, 'assets', 'naruto_col.webp')
SIDES = {'wt': 'F' * 16, 'wa': 'B' * 16, 'b': 'FFFFFFLL' + 'BBBBBBLL', 'c': 'BBBLLLFF' + 'FLLLFBFB'}
SIDES = {s: [{'F': 'front', 'B': 'back', 'L': 'left'}[c] for c in v] for s, v in SIDES.items()}
POSES = {'b': (6, 7, 14, 15)}    # (les figures d'une planche de pas qui se tiennent debout : le signe, le regard en bas)
FLIP = {'b': (6, 7, 15)}         # (les profils peints tournés vers la droite : retournés, il regarde à gauche comme son rig)
# chaque planche peinte suit son guide, image pour image : la case du rig de chaque figure (les autres cases prennent la
# figure qui couvre le mieux leur silhouette)
GUIDE = {'wt': [('walkT', i) for i in range(16)], 'wa': [('walkA', i) for i in range(16)],
         'b': [('runT', i) for i in range(0, 12, 2)] + [('seal', 0), ('seal', 2)] + [('runA', i) for i in range(0, 12, 2)] + [('seal', 1), ('look', 3)],
         'c': [('turn', i) for i in range(9)] + [('look', 0), ('look', 1), ('look', 2), ('settleT', 5), ('settleA', 5), ('startT', 0), ('startA', 0)]}
GREEN = 40                       # le fond : le vert y passe le rouge et le bleu d'au moins tant
MIN_FIG = 3000                   # (une figure : au moins tant de points d'un seul tenant)
AMB = (0.92, 0.94, 1.0)          # la rue froide sur le côté qu'on voit (la planche, peinte, l'a déjà dans l'ombre froide)
RIM = ((232, 172, 108), 0.30, 0.16)   # la lampe de la pièce sur son bord : sa couleur, sa part en haut, sur ses côtés
CHROMA = 0.92                    # (ses couleurs un peu éteintes, comme la nuit de la peinture)
FAMILIES = 32
VALUES = (24.0, 44.0)            # ses clartés L* : au-dessus du premier seuil, ramenées sous le second
SUB = 8                          # (points de la peinture par pixel, sur chaque axe)
GRAIN, GRAIN_T = 2, 8            # (le grain : plus ou moins tant de niveaux, un carreau de tant de pixels)
LIGHT = (0.0, -1.0)              # (la lumière dans l'image : la pièce derrière lui, d'en haut)
EYE = (-18.0, 30.0)              # (ses yeux : une famille bleue de plus, b* sous tant, L* au-dessus de tant ; gardée)
FAMILY = {'walkT': 'front', 'runT': 'front', 'settleT': 'front', 'startT': 'front',
          'walkA': 'back', 'runA': 'back', 'settleA': 'back', 'startA': 'back',
          'turn': ['back', 'back', 'back', 'left', 'left', 'left', 'front', 'front', 'front'],
          'look': 'left', 'seal': 'left'}


def table_nc():
    js = open(os.path.join(RACINE, 'assets', 'street.js'), encoding='utf-8').read()
    m = re.search(r'const NC = (\{[^;]*\});', js).group(1)
    return json.loads(re.sub(r'(\w+):', r'"\1":', m))


def fam(k, i):
    f = FAMILY[k]
    return f if isinstance(f, str) else f[i]


def role(s, n):
    """what a painted figure is: a step of the walk (the walk's sheets), of the run (the run's sheet), or a pose"""
    if s in ('wt', 'wa'): return 'walk'
    if s == 'b' and n not in POSES['b']: return 'run'
    return 'pose'


def fits(k, r):
    """the figures a row of the rig may take: its own gait's steps (and their mirror: the other foot), else the poses and the
    walk's steps"""
    if k in ('walkT', 'walkA'): return r == 'walk'
    if k in ('runT', 'runA'): return r == 'run'
    return r in ('walk', 'pose')


def figures():
    """the painted figures: each sheet's green ground keyed out, its figures (one piece each) row by row, with the side he
    faces (SIDES) and what each is; [(rgb float, alpha bool, side, role)] cropped to each figure"""
    out = []
    for s in SIDES:
        im = np.asarray(Image.open(os.path.join(ICI, 'src', f'naruto_paint_{s}.webp')).convert('RGB')).astype(float)
        r, g, b = im[..., 0], im[..., 1], im[..., 2]
        fg = g < np.maximum(r, b) + GREEN
        fg = binary_erosion(fg, np.ones((3, 3)))                       # (the edge's pixel, half green, off)
        im[..., 1] = np.minimum(g, np.maximum(r, b))                    # (the green spill off: his colours never lead in green)
        lf, nf = label(fg, structure=np.ones((3, 3)))
        sz = np.bincount(lf.ravel()); sz[0] = 0
        boxes = []
        for j in np.nonzero(sz >= MIN_FIG)[0]:
            ys, xs = np.nonzero(lf == j); boxes.append((ys.min(), xs.min(), ys.max() + 1, xs.max() + 1, j))
        H = im.shape[0]
        boxes.sort(key=lambda bx: (int((bx[0] + bx[2]) / 2 >= H / 2), bx[1]))
        assert len(boxes) == len(SIDES[s]), (s, len(boxes))
        for n, ((y0, x0, y1, x1, j), side) in enumerate(zip(boxes, SIDES[s])):
            rgb_, a_ = im[y0:y1, x0:x1], lf[y0:y1, x0:x1] == j
            if n in FLIP.get(s, ()): rgb_, a_ = rgb_[:, ::-1], a_[:, ::-1]
            out.append((rgb_, a_, side, role(s, n), GUIDE[s][n]))
    return out


def reduce(rgb, a, hc):
    """a painted figure brought down to hc pixels high, each pixel from SUB x SUB points of the painting (as
    tools/ichiraku_figures.py's pick): full from half covered; its colour, its dark strokes' where they cover enough of it
    (FG.INK: his eyes, his brows, his whiskers, a fold), else the mean of the rest (no mush round his face); its largest
    piece only"""
    H, W = a.shape; f = hc / H; w = max(1, int(round(W * f)))
    def box(arr, ww, hh): return np.asarray(Image.fromarray(arr.astype(np.float32), 'F').resize((ww, hh), Image.BOX))
    A8 = box(a.astype(float), w * SUB, hc * SUB)
    C8 = np.stack([box(rgb[..., c] * a, w * SUB, hc * SUB) for c in range(3)], -1) / np.maximum(A8, 1e-6)[..., None]
    A8 = A8.reshape(hc, SUB, w, SUB).transpose(0, 2, 1, 3).reshape(hc, w, SUB * SUB)
    C8 = C8.reshape(hc, SUB, w, SUB, 3).transpose(0, 2, 1, 3, 4).reshape(hc, w, SUB * SUB, 3)
    on = A8 > 0.5; lum = C8 @ np.array([0.299, 0.587, 0.114])
    ref = np.percentile(np.where(on, lum, -1.0), 80, axis=2, method='nearest')     # (a pixel's light: its 80th percentile)
    dark = on & (lum < FG.INK[0] * ref[..., None])
    use = np.where((dark.sum(2) >= FG.INK[1] * np.maximum(on.sum(2), 1))[..., None], dark, on & ~dark)
    use = np.where((use.sum(2) == 0)[..., None], on, use)
    col = (C8 * use[..., None]).sum(2) / np.maximum(use.sum(2), 1)[..., None]
    m = A8.mean(2) >= 0.5
    lab_, n = label(m, structure=np.ones((3, 3)))
    if n > 1:
        sz = np.bincount(lab_.ravel()); sz[0] = 0; m = lab_ == sz.argmax()
    return col, m


def place(col, m, sil, ay):
    """a reduced figure laid in a cell: its soles on the cell's ground row, across at the shift that covers the rig's
    silhouette best; (rgb, mask) the cell's size, and how well it covers it"""
    h, w = sil.shape; fh, fw = m.shape
    best, out = -1, None
    sx0 = int(np.nonzero(sil.any(0))[0].mean() - fw / 2)
    ys, xs = np.nonzero(m)
    for dx in range(sx0 - 10, sx0 + 11):
        A2 = np.zeros((h, w), bool); C2 = np.zeros((h, w, 3))
        Y, X = ys + ay - fh, xs + dx
        ok = (Y >= 0) & (Y < h) & (X >= 0) & (X < w)
        A2[Y[ok], X[ok]] = True; C2[Y[ok], X[ok]] = col[ys[ok], xs[ok]]
        sc = (A2 & sil).sum() / max((A2 | sil).sum(), 1)
        if sc > best: best, out = sc, (C2, A2)
    return out[0], out[1], best


def values(P, v):
    """colours kept in the clarity of what is round him (v: over the first threshold, the clarity brought under the second,
    in proportion; tools/center_red.py)"""
    lab_ = R.lab(P); L = lab_[:, 0]; top = max(L.max(), v[1] + 1e-6)
    lab_[:, 0] = np.where(L > v[0], v[0] + (L - v[0]) * (v[1] - v[0]) / (top - v[0]), L)
    return FG.lab2rgb(lab_)


def light(rgb, m):
    """the street's cool light on the side we see, the room's lamp on his edge toward it (on top, then on his sides)"""
    out = rgb * np.array(AMB)
    out = FG.rim(out, m, LIGHT, RIM[0], RIM[1], cos=0.5)
    for side in ((1.0, -0.35), (-1.0, -0.35)):
        out = FG.rim(out, m, side, RIM[0], RIM[2], cos=0.75)
    return out


def build():
    NC = table_nc()
    A = np.asarray(Image.open(SIL).convert('RGBA'))[..., 3] >= 128
    figs = figures()
    cells, report, memo = {}, {}, {}
    for k, (t, w, h, n, ax, ay) in NC.items():
        for i in range(n):
            sil = A[t:t + h, i * w:(i + 1) * w]
            ys = np.nonzero(sil.any(1))[0]; hc = int(ay - ys[0])           # (his height in the cell: hair to sole)
            best = (-1, None)
            own = [j for j, f in enumerate(figs) if f[4] == (k, i)]       # (the figure painted on this cell's own guide)
            for j, (rgb, a, side, r, g) in enumerate(figs):
                if own and j not in own: continue
                if not own and (side != fam(k, i) or not fits(k, r)): continue
                for mi in ((False, True) if r in ('walk', 'run') and not own else (False,)):
                    if (j, mi, hc) not in memo:
                        memo[(j, mi, hc)] = reduce(rgb[:, ::-1] if mi else rgb, a[:, ::-1] if mi else a, hc)
                    col, m = memo[(j, mi, hc)]
                    c2, a2, sc = place(col, m, sil, ay)
                    if sc > best[0]: best = (sc, (c2, a2, j, mi))
            c2, a2, j, mi = best[1]; report[f'{k}{i}'] = (j, 'g' if own else 'm' if mi else '', round(float(best[0]), 2))
            cells[(k, i)] = (FG.mute(light(c2, a2), CHROMA), a2)
    allc = np.concatenate([c[m] for c, m in cells.values()])
    famc = FG.palette(np.clip(allc, 0, 255), FAMILIES)
    la = R.lab(np.clip(allc, 0, 255)); blue = (la[:, 2] < EYE[0]) & (la[:, 0] > EYE[1])
    if blue.any(): famc = np.vstack([famc, allc[blue].mean(0)])     # (his eyes' blue: too few pixels for a family of their own)
    labf = R.lab(famc); Lf = labf[:, 0]; famB = values(famc, VALUES)
    eye = (labf[:, 2] < EYE[0]) & (Lf > EYE[1])
    tile = np.random.default_rng(17).integers(-GRAIN, GRAIN + 1, (GRAIN_T, GRAIN_T))
    rgba = np.zeros(A.shape + (4,), np.uint8)
    for (k, i), (c, m) in cells.items():
        t, w, h, n, ax, ay = NC[k]
        idx = np.where(m, R.nearest(np.clip(c.reshape(-1, 3), 0, 255), famc).reshape(m.shape), -1)
        idx = FG.no_outline(idx, m, Lf, LIGHT)
        keep = m & eye[np.maximum(idx, 0)]
        idx = FG.unspeckle(idx, m, keep)
        gr = np.tile(tile, (h // GRAIN_T + 1, w // GRAIN_T + 1))[:h, :w]
        cell = np.zeros((h, w, 4), np.uint8)
        cell[..., :3] = (np.clip(np.round(famB[np.maximum(idx, 0)] + gr[..., None]), 0, 255) * m[..., None]).astype(np.uint8)
        cell[..., 3] = np.where(m, 255, 0)
        rgba[t:t + h, i * w:(i + 1) * w] = cell
    return rgba, report, figs, famB


def main():
    rgba, report, frames, famB = build()
    if '--preview' in sys.argv:
        d = sys.argv[sys.argv.index('--preview') + 1]; os.makedirs(d, exist_ok=True)
        bg = np.zeros(rgba.shape[:2] + (3,)); bg[:] = (150, 110, 74)
        a = rgba[..., 3:] / 255.0; z = bg * (1 - a) + rgba[..., :3] * a
        Image.fromarray(z.astype(np.uint8)).resize((rgba.shape[1] * 4, rgba.shape[0] * 4), Image.NEAREST).save(os.path.join(d, 'naruto_col_x4.png'))
        print(report)
        return
    Image.fromarray(rgba, 'RGBA').save(OUT, 'WEBP', lossless=True, quality=100, method=6, exact=True)
    back = np.asarray(Image.open(OUT).convert('RGBA'))
    assert (back == rgba).all(), 'naruto_col: le WebP n\'est pas la planche'
    L = R.lab(famB)[:, 0]
    print('naruto_col :', OUT, '; images peintes', len(frames), '; cases', len(report), '; L* de ses familles %.0f à %.0f' % (L.min(), L.max()))


if __name__ == '__main__':
    main()
