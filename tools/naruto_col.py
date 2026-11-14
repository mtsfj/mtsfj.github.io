#!/usr/bin/env python3
"""Naruto à sa fenêtre, en couleur : ses images peintes, une par case de sa planche (assets/naruto_col.webp).

    python3 tools/naruto_col.py                 (lit les planches peintes tools/src/naruto_paint_*.webp, les silhouettes
                                                 du rig assets/naruto_sil.webp et la table NC de assets/street.js ; écrit
                                                 assets/naruto_col.webp ; on peut le relancer, il écrit la même chose)
    python3 tools/naruto_col.py --preview DIR   (des aperçus seulement : la planche x4 sur la lumière de la pièce)

Le propriétaire : « Naruto plus grand, un poil plus réaliste, et pas de contour. » Ses images sont peintes pour lui
(tools/src/naruto_paint_*.webp : cinq planches de seize images, chacune d'après un guide de poses tiré des silhouettes
agrandies de son rig, assets/naruto_sil.webp, tools/naruto_sil.py, les quatre dernières d'après la première pour le dessin) :
un jeune homme de dix-sept ans aux proportions vraies (sept têtes, de vraies épaules, de vrais bras), toujours Naruto (ses
cheveux en pointes, son bandeau et sa plaque à la feuille, ses yeux bleus, ses moustaches, sa veste orange aux épaules et au
col noirs, ses sandales), modelé par la lumière et non par des aplats : la lampe chaude de la pièce derrière lui en liseré
sur ses bords, une lumière froide et basse de face ; aucun trait de contour, sa silhouette faite par ses valeurs contre la
pièce, comme le peintre.

Chaque planche : son fond vert uni ôté (tout ce où le vert domine, et le pixel de bord mêlé de vert ; le vert ôté du reste,
sans toucher ses couleurs, où le vert ne domine jamais), chaque figure d'un seul tenant, rangée par rangée, le côté où il
regarde noté (SIDES : de face, de dos, de profil vers la gauche, comme la caméra le voit). Toutes les figures ramenées à PAL
tons communs (k-moyennes, graine fixe : rien ne change de teinte d'une image à l'autre). Chaque case de la planche (les 92
images de ses allures, NC) prend, parmi les figures qui regardent du même côté que la sienne, celle qui couvre le mieux sa
silhouette du rig une fois ramenée à sa hauteur (des cheveux aux semelles), posée sur son point au sol et décalée de quelques
pixels au mieux. La réduction au pas de la planche : chaque pixel plein dès qu'il est à moitié couvert, du ton qui en couvre
la plus grande part (pas de moyenne : pas de bouillie), sauf un ton qui tranche (ACCENT : ses yeux, ses moustaches, sa
plaque, une ombre de pli) dès qu'il en couvre ACCENT[1] ; puis une figure nette : son plus grand morceau seul (rien d'une
figure voisine, pas de miettes), aucun pixel pâle et gris sur son bord, un pixel seul parmi un autre ton proche fondu dans
ses voisins (pas ses yeux : ils tranchent). Le tout dans la lumière de la pièce de nuit (ROOM : chaude, basse ; à
contre-jour, il est plus sombre que la pièce derrière lui, son liseré plus clair ; ses couleurs un peu plus franches,
ses noirs un peu plus noirs, CHROMA, DARK : le reflet de la vitre les grise). Ses allures, leur rythme et leurs points
au sol restent ceux du rig ; sa forme est celle de la peinture (street.js la prend par majorité).
Il faut Pillow, numpy, scipy.
"""
import json
import os
import re
import sys
import numpy as np
from PIL import Image
from scipy.ndimage import binary_erosion, label

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
SIL = os.path.join(RACINE, 'assets', 'naruto_sil.webp')
OUT = os.path.join(RACINE, 'assets', 'naruto_col.webp')
SIDES = {'wt': 'FFFFFBBB' + 'BBBBBBBB', 'wa': 'FFFFFBBB', 'b': 'FFFBBBLL' + 'FFFBFBLL', 'c': 'BBBLLLFF' + 'FLLLBBBB'}
SIDES = {s: [{'F': 'front', 'B': 'back', 'L': 'left'}[c] for c in v] for s, v in SIDES.items()}
SHEET_K = {'b': ((0.72, 0.72, 0.80), 40.0, 100.0)}   # the run's sheet came out brighter (its orange 188,106,52, the others'
                                                   # 136,76,41, their darks alike): its lights x k, from clarity l0 to l1
POSES = {'b': (6, 7, 14, 15)}    # (the figures of a sheet of steps that stand: the seal, the look down)
GREEN = 30                       # le fond : le vert y passe le rouge et le bleu d'au moins tant
MIN_FIG = 4000                   # (une figure : au moins tant de points d'un seul tenant)
PAL = 44                         # tons de toutes les figures (et le bleu de ses yeux)
EYE = (60, 130)                  # (ses yeux : le bleu passe le rouge de tant, et cette clarté)
WHISKER = 2                      # ses moustaches : tant de rangées sous ses yeux
ACCENT = (80.0, 0.22)            # un ton qui tranche (à tant de lui en RVB : le bleu de ses yeux sur sa peau, ses moustaches,
                                 # sa plaque, son liseré) : dès qu'il couvre tant du pixel
ROOM = np.array((0.88, 0.84, 0.78))   # la lumière de la pièce de nuit sur lui (un peu chaude, un peu basse)
CHROMA, DARK = 1.25, (70.0, 0.88)    # ses couleurs un peu plus franches, ses noirs un peu plus noirs (derrière la vitre, son
                                     # reflet les grise : il reste orange et noir)
FAMILY = {'walkT': 'front', 'runT': 'front', 'settleT': 'front', 'startT': 'front',
          'walkA': 'back', 'runA': 'back', 'settleA': 'back', 'startA': 'back',
          'turn': ['back', 'back', 'back', 'left', 'left', 'left', 'front', 'front', 'front'],
          'look': 'left', 'seal': 'left'}
LUM = np.array([0.299, 0.587, 0.114])


def table_nc():
    js = open(os.path.join(RACINE, 'assets', 'street.js'), encoding='utf-8').read()
    m = re.search(r'const NC = (\{[^;]*\});', js).group(1)
    return json.loads(re.sub(r'(\w+):', r'"\1":', m))


def fam(k, i):
    f = FAMILY[k]
    return f if isinstance(f, str) else f[i]


def figures():
    """the painted figures: each sheet's green ground keyed out, its figures (one piece each) row by row, with the side
    he faces (SIDES); [(rgb float, alpha bool, side)] cropped to each figure"""
    out = []
    for s in SIDES:
        im = np.asarray(Image.open(os.path.join(ICI, 'src', f'naruto_paint_{s}.webp')).convert('RGB')).astype(float)
        r, g, b = im[..., 0], im[..., 1], im[..., 2]
        fg = g < np.maximum(r, b) + GREEN
        fg = binary_erosion(fg, np.ones((3, 3)))                       # (the edge's pixel, half green, off)
        im[..., 1] = np.minimum(g, np.maximum(r, b))                    # (the green spill off: his colours never lead in green)
        if s in SHEET_K:                                                # (a sheet painted brighter: its lights brought to the others')
            k, l0, l1 = SHEET_K[s]
            t = np.clip((im @ LUM - l0) / (l1 - l0), 0, 1)[..., None]
            im = im * (1 - t + t * np.array(k))
        lf, nf = label(fg, structure=np.ones((3, 3)))
        sz = np.bincount(lf.ravel()); sz[0] = 0
        boxes = []
        for j in np.nonzero(sz >= MIN_FIG)[0]:
            ys, xs = np.nonzero(lf == j); boxes.append((ys.min(), xs.min(), ys.max() + 1, xs.max() + 1, j))
        H = im.shape[0]
        boxes.sort(key=lambda bx: (int((bx[0] + bx[2]) / 2 >= H / 2), bx[1]))
        assert len(boxes) == len(SIDES[s]), (s, len(boxes))
        for n, ((y0, x0, y1, x1, j), side) in enumerate(zip(boxes, SIDES[s])):
            out.append((im[y0:y1, x0:x1], lf[y0:y1, x0:x1] == j, side, role(s, n), s, n))
    return out


def role(s, n):
    """what a painted figure is: a step of the walk (the walk's sheets), of the run (the run's sheet), or a pose"""
    if s in ('wt', 'wa'): return 'walk'
    if s == 'b' and n not in POSES['b']: return 'run'
    return 'pose'


# (toward the camera, his walk has five painted steps, the first five of its sixteen: each of its cells takes the step nearest
# in the cycle, the mirrored ones eight further on, the other foot; the other rows, the figure that covers their cell best)
def fits(k, r):
    """the figures a row of the rig may take: its own gait's steps (and their mirror: the other foot), else the poses
    and the walk's steps"""
    if k in ('walkT', 'walkA'): return r == 'walk'
    if k in ('runT', 'runA'): return r == 'run'
    return r in ('walk', 'pose')


def palette(figs):
    """PAL tones for all the figures (k-means on a sample of their points, fixed seed)"""
    rng = np.random.default_rng(5)
    px = np.concatenate([rgb[a][rng.choice(int(a.sum()), min(int(a.sum()), 1500), replace=False)] for rgb, a, *_ in figs])
    C = px[rng.choice(len(px), PAL, replace=False)].copy()
    for _ in range(30):
        lab = ((px[:, None, :] - C[None]) ** 2).sum(-1).argmin(1)
        for j in range(PAL):
            if (lab == j).any(): C[j] = px[lab == j].mean(0)
    eye = np.concatenate([rgb[a & (rgb[..., 2] - rgb[..., 0] > EYE[0]) & (rgb[..., 2] > EYE[1])] for rgb, a, *_ in figs])
    return np.vstack([C, eye.mean(0)])                              # (his eyes' blue: too few points for a k-means tone)


def face(q, al, C):
    """his whiskers: on a face seen from the front (its eyes' blue in the top fifth of him), a pixel of his cheek's shade on
    either side, WHISKER rows under the eyes and one column outside them"""
    q = q.copy(); E = len(C) - 1; h = al.shape[0]
    ys, xs = np.nonzero((q == E) & al)
    top = ys < h // 5; ys, xs = ys[top], xs[top]
    if not len(ys): return q
    L = C @ LUM; skin = (C[:, 0] > C[:, 1]) & (C[:, 1] > C[:, 2]) & (C[:, 0] - C[:, 2] > 40) & (L > 70)
    y = ys.min() + WHISKER
    for x in (xs.min() - 1, xs.max() + 1):
        if 0 <= y < h and 0 <= x < al.shape[1] and al[y, x] and skin[q[y, x]]:
            q[y, x] = int(((C - C[q[y, x]] * 0.62) ** 2).sum(-1).argmin())
    return q


def to_index(rgb, C):
    out = np.zeros(rgb.shape[:2], int)
    for r in range(0, rgb.shape[0], 64):
        out[r:r + 64] = ((rgb[r:r + 64, :, None, :] - C[None, None]) ** 2).sum(-1).argmin(-1)
    return out


def reduce(q, a, hc, C):
    """a painted figure (q: its tone per point, a: its points) brought down to hc pixels high: full from half covered, each
    pixel the tone that covers most of it, or a tone that stands out from it (ACCENT) where it covers ACCENT[1] of it"""
    H, W = a.shape; f = hc / H; w = max(1, int(round(W * f)))
    Y = np.minimum((np.arange(H) * f).astype(int), hc - 1); X = np.minimum((np.arange(W) * f).astype(int), w - 1)
    cnt = np.zeros((hc, w, len(C)))
    yy, xx = np.nonzero(a)
    np.add.at(cnt, (Y[yy], X[xx], q[yy, xx]), 1.0)
    area = np.bincount(Y, minlength=hc)[:, None] * np.bincount(X, minlength=w)[None, :]
    tot = cnt.sum(-1)
    alpha = tot * 2 >= area
    best = cnt.argmax(-1)
    D = np.sqrt(((C[:, None, :] - C[None, :, :]) ** 2).sum(-1))
    far = D[best] >= ACCENT[0]
    acc = np.where(far, cnt, 0)
    use = acc.max(-1) >= ACCENT[1] * area
    best = np.where(use, acc.argmax(-1), best)
    return best, alpha


def clean(idx, alpha, C):
    """one figure, crisp: its largest piece only, no pale grey pixel on its edge, a pixel alone among one other close tone
    taken into it"""
    lab, n = label(alpha, structure=np.ones((3, 3)))
    if n > 1:
        sz = np.bincount(lab.ravel()); sz[0] = 0; alpha = lab == sz.argmax()
    col = C[idx]; L = col @ LUM; sat = col.max(-1) - col.min(-1)
    rim = alpha & ~binary_erosion(alpha, np.ones((3, 3)), border_value=0)
    alpha = alpha & ~(rim & (L > 160) & (sat < 40))
    h, w = idx.shape; out = idx.copy()
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            if not alpha[y, x]: continue
            nb = ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1))
            if not all(alpha[v] for v in nb): continue
            vals = {idx[v] for v in nb}
            if len(vals) == 1:
                v = vals.pop()
                if v != idx[y, x] and np.sqrt(((C[v] - C[idx[y, x]]) ** 2).sum()) < ACCENT[0]: out[y, x] = v
    return out, alpha


def place(q, alpha, sil, ay):
    """a reduced figure laid in a cell: its soles on the cell's ground row, across at the shift that covers the rig's
    silhouette best; (tone index, alpha) the cell's size, and how well it covers it"""
    h, w = sil.shape; fh, fw = alpha.shape
    best, out = -1, None
    sx0 = int(np.nonzero(sil.any(0))[0].mean() - fw / 2)
    ys, xs = np.nonzero(alpha)
    for dx in range(sx0 - 10, sx0 + 11):
        A2 = np.zeros((h, w), bool); C2 = np.zeros((h, w), int)
        Y, X = ys + ay - fh, xs + dx
        ok = (Y >= 0) & (Y < h) & (X >= 0) & (X < w)
        A2[Y[ok], X[ok]] = True; C2[Y[ok], X[ok]] = q[ys[ok], xs[ok]]
        sc = (A2 & sil).sum() / max((A2 | sil).sum(), 1)
        if sc > best: best, out = sc, (C2, A2)
    return out[0], out[1], best


def tone(C):
    """the palette, its chroma x CHROMA round its clarity, its darks (under DARK[0]) x DARK[1]"""
    L = (C @ LUM)[:, None]
    return np.clip((L + (C - L) * CHROMA) * np.where(L < DARK[0], DARK[1], 1.0), 0, 255)


def build():
    NC = table_nc()
    A = np.asarray(Image.open(SIL).convert('RGBA'))[..., 3] >= 128
    figs = figures()
    C = palette(figs)
    Q = [to_index(rgb, C) for rgb, *_ in figs]
    rgba = np.zeros(A.shape + (4,), np.uint8); report = {}; memo = {}
    for k, (t, w, h, n, ax, ay) in NC.items():
        for i in range(n):
            sil = A[t:t + h, i * w:(i + 1) * w]
            ys = np.nonzero(sil.any(1))[0]; hc = int(ay - ys[0])           # (his height in the cell: hair to sole)
            best = ((-99, -1), None)
            for j, (rgb, a, side, r, sh, nn) in enumerate(figs):
                if side != fam(k, i) or not fits(k, r): continue
                if k == 'walkT' and sh != 'wt': continue
                for m in ((False, True) if r in ('walk', 'run') else (False,)):
                    if (j, m, hc) not in memo:
                        qq, aa = clean(*reduce(Q[j][:, ::-1] if m else Q[j], a[:, ::-1] if m else a, hc, C), C)
                        memo[(j, m, hc)] = (face(qq, aa, C) if side == 'front' else qq), aa
                    q, al = memo[(j, m, hc)]
                    c2, a2, sc = place(q, al, sil, ay)
                    ph = -min((i - nn - 8 * m) % n, (nn + 8 * m - i) % n) if k == 'walkT' else 0
                    if (ph, sc) > best[0]: best = ((ph, sc), (c2, a2, j, m))
            c2, a2, j, m = best[1]; report[f'{k}{i}'] = (j, 'm' if m else '', round(best[0][1], 2))
            cell = np.zeros((h, w, 4), np.uint8)
            cell[..., :3] = np.clip(np.round(tone(C)[c2] * ROOM), 0, 255); cell[..., 3] = np.where(a2, 255, 0)
            cell[~a2, :3] = 0
            rgba[t:t + h, i * w:(i + 1) * w] = cell
    return rgba, report, figs


def main():
    rgba, report, frames = build()
    if '--preview' in sys.argv:
        d = sys.argv[sys.argv.index('--preview') + 1]; os.makedirs(d, exist_ok=True)
        bg = np.zeros(rgba.shape[:2] + (3,)); bg[:] = (176, 140, 100)
        a = rgba[..., 3:] / 255.0; z = bg * (1 - a) + rgba[..., :3] * a
        Image.fromarray(z.astype(np.uint8)).resize((rgba.shape[1] * 4, rgba.shape[0] * 4), Image.NEAREST).save(os.path.join(d, 'naruto_col_x4.png'))
        print(report)
        return
    Image.fromarray(rgba, 'RGBA').save(OUT, 'WEBP', lossless=True, quality=100, method=6, exact=True)
    back = np.asarray(Image.open(OUT).convert('RGBA'))
    assert (back == rgba).all(), 'naruto_col: le WebP n\'est pas la planche'
    print('naruto_col :', OUT, '; images peintes', len(frames), '; cases', len(report))
    print(report)


if __name__ == '__main__':
    main()
