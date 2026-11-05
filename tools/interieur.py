#!/usr/bin/env python3
"""Ce que les outils des vitrines partagent : une pièce vue par une ouverture d'une façade de côté, redressée.

    (un module : tools/ichiraku_interior.py, tools/center_interior.py, tools/oden_window.py s'en servent)

La caméra regarde la rue qui descend (une perspective à un point, VP au centre : ce qui longe la rue court vers VP, ce qui
lui est de travers est horizontal, ce qui est vertical d'aplomb). Par une porte ou une fenêtre d'une façade de côté, un
rayon qui entre dans la boutique avance bien plus le long de la rue qu'il ne s'enfonce : il rencontre le mur du bout de la
boutique (de travers à la rue, juste au-delà du tableau du fond) bien avant son mur de derrière. Ce qu'on voit au fond est
donc de face : ses horizontales horizontales, sans cisaillement ; le plafond et le sol en coins entre les tableaux.

Le peintre avait peint ces intérieurs de face puis posés sur la façade, cisaillés le long de ses rayons. On les redresse
colonne par colonne, ses pixels gardés : chaque rayon de sa peinture devient l'horizontale qu'il a à la colonne du fond
(XREF : la plus proche de VP ; là, sa peinture telle quelle ; ailleurs ses rangées resserrées de |x - VP_x| / |XREF -
VP_x| autour de l'horizon) ; chaque bord net suivi le long de son rayon et posé exactement sur sa rangée (sans marche) ;
entre deux bords, les rangées en trop sautées là où la peinture est la plus unie (aucune doublée). Ce qui, plus près de
la façade, tombe au-delà de ce que le peintre a peint (au-dessus de son haut, sous son bas) : le haut et le bas de la pièce,
au grain de ses propres pixels (répétés en miroir), plus sombres vers le plafond et le sol. Les montants, meneaux,
traverses de la porte ne bougent pas (ils sont sur la façade) ; seul ce qu'on voit par le verre est redressé.
"""
import io
import os
import subprocess
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = lambda p: os.path.join(ROOT, 'assets', p)
VP = (700.0, 615.0)
LUM = np.array([0.299, 0.587, 0.114])
EDGE_MIN, EDGE_RUN = 8, 4            # un bord de la peinture : un saut de clarté d'au moins tant entre deux rangées, suivi le
                                     # long de son rayon sur tant de colonnes au moins (à deux colonnes près)
GRAIN = (0.78, 1.28)                 # (le grain : un pixel rapporté à ses voisins, borné)


def load(p, mode='RGBA', at=None):
    data = subprocess.run(['git', 'show', f'{at}:assets/{p}'], cwd=ROOT, capture_output=True, check=True).stdout if at else open(A(p), 'rb').read()
    return np.asarray(Image.open(io.BytesIO(data)).convert(mode)).astype(float)


def save(arr, p, mode):
    Image.fromarray(np.clip(np.round(arr), 0, 255).astype(np.uint8), mode).save(A(p), 'WEBP', lossless=True, quality=100, method=6, exact=True)


def ray(c, x):                       # (la ligne à x du rayon c vers VP : y = VP_y + c |x - VP_x|)
    return VP[1] + c * abs(x - VP[0])


def half(t):                         # (une limite entre deux rangées)
    return np.round(t - 0.5) + 0.5


def tracks_of(Lm, inside, cols):
    """les bords nets de la peinture vue par le verre : des sauts de clarté entre deux rangées du verre (inside), groupés
    par rayon vers VP ; chacun (son rayon c, son nombre de points, ses points {x: bord}, ses colonnes (x0, x1))"""
    edges = []
    for x in cols:
        ys = [y for y in range(1, Lm.shape[0] - 1) if inside[y, x] and inside[y + 1, x]]
        for y in ys:
            d = Lm[y + 1, x] - Lm[y, x]
            dm = Lm[y, x] - Lm[y - 1, x] if inside[y - 1, x] else 0
            dp = Lm[y + 2, x] - Lm[y + 1, x] if inside[y + 2, x] else 0
            if abs(d) >= EDGE_MIN and abs(d) >= abs(dm) and abs(d) >= abs(dp):
                b = y + 0.5
                edges.append((x, b, np.sign(d), abs(d), (b - VP[1]) / abs(x - VP[0])))
    if not edges: return []
    E = np.array(edges); cands = []
    for c in np.arange(E[:, 4].min(), E[:, 4].max() + 1e-9, 0.0004):
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
        cc = float(np.mean([(E[k, 1] - VP[1]) / abs(VP[0] - E[k, 0]) for k in ks]))
        tracks.append((cc, len(ks), {int(E[k, 0]): E[k, 1] for k in ks}, (int(run[0]), int(run[-1]))))
    return tracks


def col_map(x, xref, inside, tracks, Lm):
    """une colonne vue par le verre : pour chacune de ses rangées (inside), la rangée de la peinture qu'elle montre, ou
    'haut' / 'bas' là où elle tombe au-delà de ce que le peintre a peint. Chaque rayon de sa peinture devient l'horizontale
    qu'il a à xref ; des repères (rangée de sortie, rangée de la peinture) : le haut et le bas de sa peinture, chaque bord
    suivi posé sur sa rangée ; monotones, jamais plus serrés dans la peinture qu'à la sortie (en cas de conflit, le bord le
    plus court lâché) ; entre deux repères, les rangées de sa peinture dans l'ordre (les traverses de la porte sautées),
    celles en trop sautées là où elle est la plus unie"""
    rows = [y for y in range(inside.shape[0]) if inside[y, x]]
    if not rows: return {}
    K = abs(x - VP[0]) / abs(xref - VP[0])
    s0, s1 = rows[0] - 0.5, rows[-1] + 0.5                                   # (ce que le peintre a peint dans la colonne)
    out_of = lambda s: VP[1] + (s - VP[1]) / K                               # (où une rangée de sa peinture arrive)
    anc = [(half(out_of(s0)), s0, 1e9), (half(out_of(s1)), s1, 1e9)]
    for cc, n, pts, (xa, xb) in tracks:
        t = half(ray(cc, xref))
        if xa <= x <= xb and anc[0][0] < t < anc[1][0]:
            anc.append((t, pts.get(x, half(ray(cc, x))), n))
    anc.sort()
    ok = False
    while not ok:
        ok = True
        for i in range(len(anc) - 1):
            (t0, a0, w0), (t1, a1, w1) = anc[i], anc[i + 1]
            if t1 - t0 < 0.5 or a1 - a0 < t1 - t0:
                anc.pop(i if w0 < w1 else i + 1); ok = False; break
    flat = lambda y: abs(Lm[y, x] - Lm[y - 1, x]) + abs(Lm[y + 1, x] - Lm[y, x])
    out = {}
    for y in rows:                                                           # (au-delà de sa peinture : le haut, le bas)
        if y < anc[0][0]: out[y] = 'haut'
        elif y > anc[-1][0]: out[y] = 'bas'
    for (t0, a0, _), (t1, a1, _) in zip(anc[:-1], anc[1:]):
        ts = [y for y in range(int(t0 + 0.5), int(t1 + 0.5)) if inside[y, x]]
        ss = [y for y in range(int(a0 + 0.5), int(a1 + 0.5)) if inside[y, x]]
        if not ts: continue
        if len(ss) >= len(ts):
            drop = sorted(ss, key=lambda y: (flat(y), abs(y - (ss[0] + ss[-1]) / 2)))[:len(ss) - len(ts)]
            ss = [y for y in ss if y not in drop]
        else:                                                                # (une traverse de la porte entre les deux : la
            ss = [ss[min(len(ss) - 1, int(i * len(ss) / len(ts)))] for i in range(len(ts))] if ss else []   # rangée la plus proche)
        for t, s in zip(ts, ss): out[t] = s
        for t in ts[len(ss):]: out[t] = ss[-1] if ss else 'haut'
    return out


def tile(P, i, j):                   # (un motif répété en miroir : son pixel (i, j))
    h, w = P.shape[:2]; i %= 2 * h; j %= 2 * w
    return P[i if i < h else 2 * h - 1 - i, j if j < w else 2 * w - 1 - j]


def grain(P):                        # (le grain d'un motif : chaque pixel rapporté à la moyenne de ses voisins, borné)
    Pp = np.pad(P, ((1, 1), (1, 1), (0, 0)), mode='reflect')
    m = sum(Pp[a:a + P.shape[0], b:b + P.shape[1]] for a in range(3) for b in range(3)) / 9
    return np.clip((P + 1) / (m + 1), GRAIN[0], GRAIN[1])


def redress(imgs, inside, xref, cols, Lm, edge_f, fill):
    """redresse ce qu'on voit par le verre dans chaque image de imgs (le même plan pour toutes) ; fill(k, x, y, côté, d) : le
    pixel d'au-delà de la peinture (côté 'haut' ou 'bas', d rangées au-delà) ; edge_f : la part gardée par la rangée qui
    touche le haut (la ligne sombre du haut de la pièce). Rend les images redressées et le plan {x: {y: rangée ou côté}}"""
    tr = tracks_of(Lm, inside, cols)
    plan = {x: col_map(x, xref, inside, tr, Lm) for x in cols}
    out = {k: v.copy() for k, v in imgs.items()}
    for x, m in plan.items():
        tops = [y for y, s in m.items() if s == 'haut']; bots = [y for y, s in m.items() if s == 'bas']
        for y, s in m.items():
            for k, im in imgs.items():
                if s == 'haut': out[k][y, x] = fill(k, x, y, 'haut', max(tops) - y + 1)
                elif s == 'bas': out[k][y, x] = fill(k, x, y, 'bas', y - min(bots) + 1)
                else:
                    out[k][y, x] = im[s, x]
                    if tops and y == max(tops) + 1: out[k][y, x] = out[k][y, x] * edge_f
    return out, plan, tr
