#!/usr/bin/env python3
"""Ichiraku : les gens de la boutique dans la maquette de tools/ichiraku_interior.py, chacun à sa profondeur, découpés dans les
deux planches du propriétaire (tools/src/ichiraku_teuchi_sheet.webp : Teuchi ; tools/src/ichiraku_regular_sheet.webp : l'habitué en
costume).

    python3 tools/ichiraku_figures.py                  (après tools/ichiraku_interior.py ; réécrit assets/ramen_figures.webp et,
                                                         dans assets/street.js, la ligne IRF : on peut le relancer, il écrit la
                                                         même chose)
    python3 tools/ichiraku_figures.py --preview dossier (des aperçus seulement : l'atlas sur fond sombre, la ligne IRF en json)

Chaque image de la planche (T_FR, R_FR : sa boîte, ce qu'il faut ôter autour) :
  - la découpe : le fond est le blanc relié au bord de la boîte (les blancs enfermés, la veste, le bandeau, restent à la figure ;
    le blanc pur pris entre un bras et le corps s'en va) ; les meubles de la planche ôtés selon l'image (le comptoir sous son
    dessus, la marmite sous son bord, le tabouret sous l'assise sauf le pantalon, l'étagère : la figure qui pousse depuis le corps
    sans passer par le bois ni par les longs traits des planches) ; la plus grande pièce (et ce qu'elle tient de détaché : le bol,
    la passoire) ; un liseré d'un pixel à demi transparent, l'anticrénelage clair du bord repeint de la couleur voisine ;
  - la taille : chaque rangée ramenée à une taille vraie (Teuchi 1,65 m, le client 1,72 m : PPM, pixels de planche par mètre ;
    les images en buste d'après la largeur de la tête), posée par le haut de la tête (Teuchi en buste, sa tête à 1,65 m) ou par les
    pieds (au sol à sa profondeur) ;
  - la réduction : à l'échelle de sa profondeur (F / Z px par mètre), moyenne des couleurs sur l'aire de chaque pixel pondérée par
    l'alpha, un pixel plein dès la moitié couverte (pas de demi-teinte au bord) ; les sombres du client un peu relevés (LIFT) ;
    la lumière de la boutique (chaude, d'en haut) ; puis chacun à sa palette (PALETTE couleurs) : des visages, des mains, des
    bols en pixels nets.
Où va chaque image : Teuchi au comptoir (idle, calm, nod, smile, serve), à la marmite (stir, lift), à l'étagère de dos (shelf),
sa marche de côté dans l'allée (walk) et à la porte (dwalk), de face à la porte (dfront), sa perche montée par crans jusqu'à la
tringle (dpole : POLE_UP), s'essuyant le front (dbrow) ; le client assis de dos (seat, chop, sip, done), qui se retourne (turn),
se lève (rise), remet sa veste en place (jacket), debout (stand), qui marche vers nous à chaque taille entre son tabouret et la
porte (W), qui remonte la bandoulière de son sac à la porte (fix). Naruto : ses images d'avant, en silhouette. Le reste de IRF : ce
qui est devant Teuchi (O), le verre colonne par colonne avec l'ourlet du noren (G), d'où monte la vapeur (wisps).
"""
import json
import os
import re
import sys
import numpy as np
from PIL import Image

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import interieur as I
import ichiraku_interior as R

ROOT = R.ROOT
JS = os.path.join(ROOT, 'assets', 'street.js')
OUT = 'ramen_figures.webp'
SHEETS = {'teuchi': os.path.join(ROOT, 'tools', 'src', 'ichiraku_teuchi_sheet.webp'),
          'regular': os.path.join(ROOT, 'tools', 'src', 'ichiraku_regular_sheet.webp')}
F, VX, VY, EYE = R.F, R.VX, R.VY, R.EYE

# ---- les profondeurs (m, le long de la rue) et les échelles (px par mètre : F / Z)
Z_T = R.Z_C + R.CTR_D + R.AISLE / 2          # Teuchi, au milieu de son allée
Z_S = R.Z_C - R.STOOL['dz'] - 0.12           # le dos des clients assis sur les tabourets
Z_STOOL = R.Z_C - R.STOOL['dz']              # (le milieu des tabourets)
H_T, H_R = 1.65, 1.72                        # Teuchi, le client : leur taille
DOOR_Z, POLE_X = 17.6, 1215.0                # Teuchi à la porte : sa profondeur (il y vient de côté, de derrière le montant gauche),
                                             # la colonne de sa perche (au milieu de la vitre de droite : lui un peu à gauche)
WALK_END = (1175.0, 0.32)                    # le client qui s'en va : à la porte, la colonne de son milieu, derrière la vitre de tant
PLACES = {'counter': 1199.0, 'pots': -0.25, 'shelf': 9.42}   # Teuchi : au comptoir (sa colonne), à la marmite (à tant de
                                             # son X, la louche à bout de bras), à l'étagère (son X, devant les bocaux de gauche)
N_TOP, N_ROWS = 614, 47                      # Naruto : la rangée 0 de ses images (ses épis à 626), jusqu'au coussin (rangée 660)
N_COL = (20, 6, 10)                          # (Naruto, tel qu'avant : une silhouette sombre)

# ---- les planches du propriétaire : chaque image, sa boîte dans la planche, sa découpe ; l'échelle de chaque rangée
# (pixels de la planche par mètre : la figure entière de la rangée du bas pour sa taille, les autres d'après la largeur de la
# tête) ; ce qui la pose : sa tête (le haut à sa taille) ou ses pieds (au sol)
PPM = {'teuchi_top': 119.8, 'teuchi_full': 110.9, 'regular_seat': 150.0, 'regular_full': 140.1}
T_FR = {   # Teuchi
    'idle': (('teuchi', (0, 15, 176, 194), 'counter', {}),),
    'calm': (('teuchi', (176, 15, 352, 194), 'counter', {}),),
    'nod': (('teuchi', (352, 15, 528, 194), 'counter', {}),),
    'smile': (('teuchi', (528, 15, 704, 194), 'counter', {}),),
    'stir': (('teuchi', (716, 15, 875, 194), 'below', {'row': 130}), ('teuchi', (889, 15, 1050, 194), 'below', {'row': 136}),
             ('teuchi', (1066, 15, 1227, 194), 'below', {'row': 136}), ('teuchi', (1241, 15, 1402, 194), 'below', {'row': 136}),
             ('teuchi', (189, 205, 344, 386), 'below', {'row': 331}), ('teuchi', (366, 205, 518, 386), 'below', {'row': 331})),
    'lift': (('teuchi', (15, 195, 167, 386), 'below', {'row': 331}),),
    'serve': (('teuchi', (540, 205, 699, 386), 'free', {'multi': True}), ('teuchi', (718, 205, 872, 386), 'free', {'multi': True})),
    'shelf': (('teuchi', (880, 200, 1056, 386), 'shelf', {'top': 243, 'low': 299}), ('teuchi', (1232, 200, 1408, 386), 'shelf', {'top': 243, 'low': 299})),
    'walk': tuple(('teuchi', b, 'free', {}) for b in ((558, 576, 666, 768), (741, 576, 845, 768), (920, 576, 1017, 768),
                                                      (1096, 576, 1194, 768), (1265, 576, 1372, 768))),
    'front': (('teuchi', (392, 576, 485, 768), 'free', {}),),
    'pole': (('teuchi', (33, 572, 157, 768), 'free', {}),),
    'brow': (('teuchi', (208, 578, 324, 768), 'free', {}),),
}
R_FR = {   # le client
    'seat': (('regular', (55, 8, 205, 252), 'stool', {}),),
    'chop': (('regular', (358, 8, 524, 252), 'stool', {}),),
    'sip': (('regular', (570, 8, 707, 252), 'stool', {}), ('regular', (804, 8, 942, 252), 'stool', {})),
    'done': (('regular', (1105, 8, 1273, 252), 'stool', {}),),
    'turn': (('regular', (83, 252, 219, 503), 'stool', {}), ('regular', (435, 252, 570, 503), 'stool', {})),
    'rise': (('regular', (756, 252, 926, 503), 'stool', {'x': (750, 850), 'run': 12}), ('regular', (1167, 247, 1334, 503), 'stool', {'x': (1160, 1245), 'run': 12})),
    'stand': (('regular', (26, 508, 134, 762), 'free', {'flip': True}),),   # (retourné : son sac du côté où il le porte en marchant)
    'jacket': (('regular', (935, 508, 1112, 762), 'free', {}), ('regular', (1117, 508, 1258, 762), 'free', {})),
    'walk': tuple(('regular', b, 'free', {}) for b in ((326, 508, 452, 762), (480, 508, 605, 762), (630, 508, 753, 762), (785, 508, 896, 762))),
    'fix': (('regular', (1264, 508, 1391, 762), 'free', {'tint': ((1279, 620, 1302, 674, (112, 64, 42)),)}),),
}
WARM = (0.96, 0.87, 0.75)                    # la lumière de la boutique sur eux (chaude) ; d'en haut : la tête plus claire que le
TOPLIGHT = (1.07, 0.9)                       # bas de la figure (de tant à tant)
LIFT = {'T': 1.0, 'R': 0.85}                 # (les sombres relevés : le costume bleu nuit du client, de dos, garde ses plis)
PALETTE = 64                                 # (les couleurs de chacun, après réduction)
POLE_UP = (0.0, 0.35, 0.7, 1.0)              # la perche de Teuchi montée de tant (part de ce qu'il faut pour atteindre la tringle)


def row(h, Z):                               # (la rangée d'une hauteur h à la profondeur Z)
    return VY - (h - EYE) * F / Z


def col(X, Z):
    return VX + F * X / Z


def lab(rgb):
    return R.lab(rgb)


# ---- la découpe : le fond blanc ôté (le blanc relié au bord de la case), les accessoires de la planche ôtés (comptoir,
# marmite, étagère, tabouret : la maquette a les siens), les poussières ôtées, le liseré clair du bord repris à la couleur du
# trait le plus proche, l'alpha partiel seulement sur ce liseré
def grow(m, n=1):
    for _ in range(n):
        d = m.copy(); d[1:] |= m[:-1]; d[:-1] |= m[1:]; d[:, 1:] |= m[:, :-1]; d[:, :-1] |= m[:, 1:]; m = d
    return m


def label(m):
    H, W = m.shape; lab_ = np.zeros((H, W), np.int32); n = 0
    for y0, x0 in zip(*np.nonzero(m)):
        if lab_[y0, x0]: continue
        n += 1; st = [(y0, x0)]; lab_[y0, x0] = n
        while st:
            y, x = st.pop()
            for yy, xx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
                if 0 <= yy < H and 0 <= xx < W and m[yy, xx] and not lab_[yy, xx]: lab_[yy, xx] = n; st.append((yy, xx))
    return lab_, n


def cut(sheets, sheet, box, kind, o):
    x0, y0, x1, y1 = box; P = sheets[sheet][y0:y1, x0:x1].copy()
    for a0, b0, a1, b1, hue in o.get('tint', ()):   # (un rabat de sac peint en transparence sur le blanc : rendu à sa couleur)
        S = P[b0 - y0:b1 - y0, a0 - x0:a1 - x0]; sat = S.max(2) - S.min(2); lum = S.sum(2)
        m_ = (sat < 45) & (lum > 200) & (lum < 520) & (S[..., 0] >= S[..., 2] - 2)
        S[m_] = np.array(hue, float)[None] * (lum[m_] / sum(hue))[:, None]
    r, g, b = P[..., 0], P[..., 1], P[..., 2]; L = P.sum(2)
    ink = (255 - P).sum(2)
    solid = ink > 60; void = np.zeros_like(solid)
    if kind == 'counter':                    # (le comptoir de la planche : sous son dessus)
        brown = (r > 100) & (r < 200) & (b < r - 40)
        tops = [y for y in range(len(P) - 1, 0, -1) if brown[y].mean() > 0.6]
        void[(min(tops) if tops else len(P)) - 3:] = True
    if kind == 'below':                      # (la marmite de la planche : sous son bord)
        void[o['row'] - y0:] = True
    if kind == 'stool':                      # (le tabouret de la planche : sous l'assise, entre les jambes, tout sauf le pantalon)
        wood = (r > 85) & (r < 225) & (r - b > 40) & (r - g > 22) & (L > 230)
        if 'x' in o: wood[:, :max(0, o['x'][0] - x0)] = False; wood[:, max(0, o['x'][1] - x0):] = False
        rows = [y for y in range(int(len(P) * 0.55), len(P)) if wood[y].sum() >= o.get('run', 28)]
        st = (rows[0] if rows else len(P)) - 2
        cols = np.nonzero(wood[st:].any(0))[0]
        if len(cols):
            navy = (b > r + 8) & (b > 25)
            void[st:, cols.min():cols.max() + 1] = ~navy[st:, cols.min():cols.max() + 1]
    if kind == 'shelf':                      # (l'étagère, ses planches et ses bocaux : la figure, c'est ce qui pousse depuis le corps
        brown = (r > 95) & (r < 216) & (r - b > 45) & (r - g > 25) & (b < 0.6 * r)   # sous la planche du bas, sans passer par le
        def runs(m):                                                    # bois ni par les longs traits des planches (le sombre de leur
            out = np.zeros(m.shape, int)                                # bord, le clair de leur arête) ; ce qu'elle enferme lui reste,
            for y in range(len(m)):                                     # sauf le bois)
                d = np.diff(np.r_[0, m[y].astype(int), 0])
                for s0, s1 in zip(np.nonzero(d == 1)[0], np.nonzero(d == -1)[0]): out[y, s0:s1] = s1 - s0
            return out
        near = grow(brown, 3); dark = L < 200; light = (L > 450) & (ink > 40)
        line = (dark & (runs(dark) >= 10) & near) | (light & (runs(light) >= 16) & near)
        low = o['low'] - y0; top = o['top'] - y0
        body = solid.copy(); body[:low] = False
        cols = np.nonzero(body[low:low + 12].any(0))[0]
        go = solid & ~brown & ~line; go[:top] = False
        go[:, :max(0, cols.min() - 4)] = False; go[:, cols.max() + 5:] = False
        keep = body.copy(); st = list(zip(*np.nonzero(body[low:low + 1]))); st = [(y + low, x) for y, x in st]
        while st:
            y, x = st.pop()
            for yy, xx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1), (y - 1, x - 1), (y - 1, x + 1)):
                if 0 <= yy < low and 0 <= xx < keep.shape[1] and go[yy, xx] and not keep[yy, xx]: keep[yy, xx] = True; st.append((yy, xx))
        hl, hn = label(~keep)                # (ce qu'elle enferme)
        edge = set(hl[0]) | set(hl[-1]) | set(hl[:, 0]) | set(hl[:, -1])
        keep |= ~np.isin(hl, list(edge)) & (hl > 0)
        thin = runs(keep.T).T <= 2; thin[low:] = False                 # (pas de fil : les bouts d'arête restés au bord d'une main)
        keep &= ~thin; kl, _ = label(keep); keep = np.isin(kl, np.unique(kl[low][keep[low]]))
        keep[:low] &= ~brown[:low]
        void |= ~keep
    solid &= ~void
    free = ~solid | void                     # le fond : le blanc relié au bord (les blancs enfermés restent à la figure)
    ext = np.zeros_like(free); H, W = free.shape
    st = [(y, x) for y in range(H) for x in (0, W - 1) if free[y, x]] + [(y, x) for x in range(W) for y in (0, H - 1) if free[y, x]]
    for y, x in st: ext[y, x] = True
    while st:
        y, x = st.pop()
        for yy, xx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
            if 0 <= yy < H and 0 <= xx < W and free[yy, xx] and not ext[yy, xx]: ext[yy, xx] = True; st.append((yy, xx))
    fig = ~ext & ~void
    gap = fig & (ink < 20)                   # (le fond pris entre un bras et le corps : blanc pur, enfermé)
    gl_, gn = label(gap)
    if gn:
        gs = np.bincount(gl_.ravel()); gs[0] = 0
        fig &= ~(gs >= 12)[gl_]
    lab_, n = label(fig)
    if n:                                    # (la figure ; ce qu'elle tient de détaché aussi s'il est assez grand ; pas de poussière)
        sizes = np.bincount(lab_.ravel()); sizes[0] = 0
        keepc = (sizes >= 300) if o.get('multi') else (np.arange(len(sizes)) == sizes.argmax())
        keepc[0] = False; fig = keepc[lab_]
    ring = grow(fig) & ~fig & ~void
    a = np.where(fig, 1.0, np.where(ring, np.clip((ink - 25) / 110, 0, 1), 0))
    aa = (a > 0) & grow(~fig, 2) & (ink < 450)   # (le clair et le gris d'entre le trait et le blanc : pas de liseré clair)
    Q = P.copy(); have = (a > 0) & ~aa
    for _ in range(6):
        if have[a > 0].all(): break
        acc = np.zeros_like(Q); cnt = np.zeros(have.shape)
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            sh = np.roll(np.roll(have, dy, 0), dx, 1); acc += np.roll(np.roll(Q, dy, 0), dx, 1) * sh[..., None]; cnt += sh
        new = ~have & (cnt > 0); Q[new] = acc[new] / cnt[new][:, None]; have |= new
    if o.get('flip'): Q, a = Q[:, ::-1].copy(), a[:, ::-1].copy()
    return Q, a


def marks(a):
    """une figure découpée : son haut (la première rangée d'au moins 8 pixels), son bas, le milieu de son buste (la moyenne
    des colonnes entre 35 et 60 % de sa hauteur)"""
    rows = np.nonzero((a > 0.5).sum(1) >= 8)[0]; top, bot = rows[0], rows[-1] + 1
    band = a[top + int(0.35 * (bot - top)):top + int(0.6 * (bot - top))] > 0.5
    xs = np.nonzero(band)[1]
    return top, bot, xs.mean() + 0.5


def reduce(Q, a, k, ax, ay):
    """à l'échelle de la scène : k pixels de la scène par pixel de la planche ; (ax, ay) le point de la planche qui tombe sur un
    coin de pixel ; moyenne des couleurs sur l'aire de chaque pixel (pondérée par l'alpha), un pixel plein dès la moitié
    couverte. Rend la case (couleurs, plein), et où tombe ce point dans la case"""
    pad = 8; Q = np.pad(Q, ((pad, pad), (pad, pad), (0, 0))); a = np.pad(a, pad); ax += pad; ay += pad
    H, W = a.shape
    x0 = int(np.ceil(-ax * k)); x1 = int(np.floor((W - ax) * k)); y0 = int(np.ceil(-ay * k)); y1 = int(np.floor((H - ay) * k))
    box = (ax + x0 / k, ay + y0 / k, ax + x1 / k, ay + y1 / k)
    ch = [np.asarray(Image.fromarray((c).astype(np.float32), 'F').resize((x1 - x0, y1 - y0), Image.BOX, box=box))
          for c in [Q[..., i] * a for i in range(3)] + [a]]
    A = ch[3]; rgb = np.stack(ch[:3], -1) / np.maximum(A, 1e-6)[..., None]
    m = A >= 0.5
    ys, xs = np.nonzero(m)
    if not len(ys): return rgb[:1, :1], m[:1, :1], (0, 0)
    t, b_, l, r_ = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    return rgb[t:b_, l:r_], m[t:b_, l:r_], (-x0 - l, -y0 - t)


def palette(P, k):
    """une palette de k couleurs tirée de P (k-means en Lab, départ fixe : la même à chaque fois) ; chaque tranche de clarté y
    compte à proportion de la racine de son nombre de pixels (les sombres nombreux d'un costume gardent leurs nuances, les clairs
    rares comptent encore)"""
    P = np.asarray(P, float); L = R.lab(P); o = np.lexsort((L[:, 2], L[:, 1], L[:, 0])); P, L = P[o], L[o]
    bands = [np.where((L[:, 0] >= a) & (L[:, 0] < a + 10))[0] for a in range(0, 100, 10)]
    w = np.array([np.sqrt(len(b)) for b in bands]); pick = []
    for b, n in zip(bands, np.round(5000 * w / w.sum()).astype(int)):
        if len(b) and n: pick += list(b[np.linspace(0, len(b) - 1, min(n, len(b))).astype(int)])
    P, L = P[pick], L[pick]
    C = L[np.linspace(0, len(L) - 1, k).astype(int)].copy()
    for _ in range(50):
        a = np.argmin(((L[:, None] - C[None]) ** 2).sum(2), 1)
        for j in range(k):
            if (a == j).any(): C[j] = L[a == j].mean(0)
    a = np.argmin(((L[:, None] - C[None]) ** 2).sum(2), 1)
    return np.array([P[a == j].mean(0) for j in range(k) if (a == j).any()])


def grade(rgb, m):
    """la lumière chaude de la boutique, d'en haut"""
    ys = np.nonzero(m.any(1))[0]
    t = np.clip((np.arange(len(m))[:, None, None] - ys[0]) / max(1, ys[-1] - ys[0]), 0, 1)
    return rgb * np.array(WARM) * (TOPLIGHT[0] + (TOPLIGHT[1] - TOPLIGHT[0]) * t)


class Atlas:
    """les cases, rangées en étagères dans une image ; leur boîte [sx, sy, w, h]"""
    def __init__(self, width):
        self.W, self.x, self.y, self.rowh, self.cells = width, 0, 0, 0, []

    def add(self, rgba):
        h, w = rgba.shape[:2]
        if self.x + w > self.W: self.x, self.y, self.rowh = 0, self.y + self.rowh + 1, 0
        self.cells.append((self.x, self.y, rgba)); box = [self.x, self.y, w, h]
        self.x += w + 1; self.rowh = max(self.rowh, h)
        return box

    def image(self):
        H = self.y + self.rowh
        a = np.zeros((H, self.W, 4), np.uint8)
        for x, y, c in self.cells: a[y:y + c.shape[0], x:x + c.shape[1]] = c
        return a


def naruto_cells():
    """Naruto au comptoir, de dos : ses six images (assets/naruto_ramen.webp, 23 x 37 : assis, penché, deux pour aspirer, la
    tête levée, les bouts du bandeau) gardées pixel pour pixel (leur échelle est déjà celle du tabouret), le bas du dos
    prolongé jusqu'au coussin (ses rangées du bas, qui se resserraient, refaites droites) ; une silhouette sombre, comme avant"""
    a = I.load('naruto_ramen.webp', 'RGBA')[..., 3] > 128
    out = []
    for f in range(6):
        c = a[:, f * 23:(f + 1) * 23]
        m = np.zeros((N_ROWS, 23), bool); m[:33] = c[:33]
        for r in range(33, N_ROWS):
            k = int(round(1.5 * (r - 33) / (N_ROWS - 34)))
            m[r, 3 + k:20 - k] = True
        rgba = np.zeros((N_ROWS, 23, 4), np.uint8); rgba[..., :3] = N_COL; rgba[..., 3] = m * 255
        out.append(rgba)
    return out


def glass_rows(hem):
    """chaque colonne de verre : la rangée sous la tringle du noren (un rayon vers VP), la dernière au-dessus de la traverse, la
    première au-dessous, la dernière au-dessus de la lisière du bas ; la dernière de l'ourlet du noren (sous lui, son ombre)"""
    out = []
    for a, b in R.VITRES:
        for x in range(a, b + 1):
            top = int(np.ceil(VY - 0.2065 * (x - VX))) + 1
            bot = int(np.round(VY + R.BAS_RAYON * (x - VX) - 0.5)) - 1
            out.append([x, top, R.TRAVERSE[0], R.TRAVERSE[1], bot, int(hem[x])])
    return out


def main():
    prev = sys.argv[sys.argv.index('--preview') + 1] if '--preview' in sys.argv else None
    sheets = {k: np.asarray(Image.open(p).convert('RGB')).astype(float) for k, p in SHEETS.items()}
    cuts = {}
    for who, table in (('T', T_FR), ('R', R_FR)):
        for name, frames in table.items():
            cuts[who, name] = [cut(sheets, *f[:3], dict(f[3])) for f in frames]

    # ---- chaque case à sa profondeur : Teuchi dans l'allée et à la porte, le client assis, debout, en marche (une taille par
    # pixel de haut) ; puis les couleurs de chacun ramenées à sa palette
    raw = {'T': [], 'R': []}                 # (qui, groupe, couleurs, plein, où poser : x du milieu, rangée du haut absolue)
    def put(who, group, Q, a, ppm_src, s_dst, anchor, key=None, cx=None):
        top, bot, cx0 = marks(a); cx = cx0 if cx is None else cx
        k = s_dst / ppm_src
        if anchor == 'head': ay, h0 = top, (H_T if who == 'T' else H_R)
        else: ay, h0 = bot, 0.0
        rgb, m, (ox, oy) = reduce(Q, a, k, cx, ay)
        raw[who].append((group, key, rgb, m, ox, oy, h0))
    s_t, s_door, s_s = F / Z_T, F / DOOR_Z, F / Z_S
    for name in ('idle', 'calm', 'nod', 'smile', 'stir', 'lift', 'serve', 'shelf'):
        for Q, a in cuts['T', name]: put('T', name, Q, a, PPM['teuchi_top'], s_t, 'head')
    for Q, a in cuts['T', 'walk']: put('T', 'walk', Q, a, PPM['teuchi_full'], s_t, 'feet')
    for Q, a in cuts['T', 'walk']: put('T', 'dwalk', Q, a, PPM['teuchi_full'], s_door, 'feet')
    for Q, a in cuts['T', 'front']: put('T', 'dfront', Q, a, PPM['teuchi_full'], s_door, 'feet')
    for Q, a in cuts['T', 'brow']: put('T', 'dbrow', Q, a, PPM['teuchi_full'], s_door, 'feet')
    # la perche montée vers la tringle : ses pixels (le bois clair et fin à droite de la main) glissés vers le haut
    Qp, ap = cuts['T', 'pole'][0]
    rr, gg, bb = Qp[..., 0], Qp[..., 1], Qp[..., 2]
    xs_pole = np.nonzero(((rr - bb > 25) & (rr < 170) & (ap > 0.5)).sum(0) > 0.55 * (ap > 0.5).any(1).sum())[0]
    p0, p1 = xs_pole.min() - 2, xs_pole.max() + 3
    top_p = np.nonzero((ap[:, p0:p1] > 0.5).any(1))[0][0]
    rail = VY - 0.2065 * (POLE_X - VX) + 1   # (la tringle, à sa colonne)
    t_, b_, cx_ = marks(ap); feet_row = row(0.0, DOOR_Z)
    door_x = POLE_X - round((xs_pole.mean() + 0.5 - cx_) * s_door / PPM['teuchi_full'])   # (la colonne de son milieu)
    pole_top_row = feet_row - (b_ - top_p) * s_door / PPM['teuchi_full']
    need = (pole_top_row - rail) * PPM['teuchi_full'] / s_door              # (de combien monter la perche, en pixels de la planche)
    for up in POLE_UP:
        d = int(round(up * need))
        Q2, a2 = Qp.copy(), ap.copy()
        if d:
            Q2 = np.pad(Q2, ((d, 0), (0, 0), (0, 0)), mode='edge'); a2 = np.pad(a2, ((d, 0), (0, 0)))
            strip_q, strip_a = Qp[:, p0:p1].copy(), ap[:, p0:p1].copy()
            hand = (strip_a > 0.5) & ~((strip_q[..., 0] - strip_q[..., 2] > 25) & (strip_q[..., 0] < 170))
            body = a2[:, p0:p1].copy(); body[d:] = np.where(hand, strip_a, 0); a2[:, p0:p1] = body
            a2[:len(strip_a), p0:p1] = np.maximum(a2[:len(strip_a), p0:p1], strip_a * ~hand)
            Q2[:len(strip_q), p0:p1] = np.where((strip_a * ~hand)[..., None] > 0, strip_q, Q2[:len(strip_q), p0:p1])
        # (la figure au sol, la perche plus haut : on pose par les pieds, la case plus haute de d)
        put('T', 'dpole', Q2, a2, PPM['teuchi_full'], s_door, 'feet', key=d, cx=cx_)
    for name in ('seat', 'chop', 'sip', 'done', 'turn'):
        for Q, a in cuts['R', name]: put('R', name, Q, a, PPM['regular_seat'], s_s, 'feet')
    for Q, a in cuts['R', 'rise']: put('R', 'rise', Q, a, PPM['regular_full'], s_s, 'feet')
    for Q, a in cuts['R', 'stand']: put('R', 'stand', Q, a, PPM['regular_full'], s_s, 'feet')
    for Q, a in cuts['R', 'jacket']: put('R', 'jacket', Q, a, PPM['regular_full'], s_s, 'feet')
    Xe = R.X_F + WALK_END[1]; Ze = F * Xe / (WALK_END[0] - VX)
    H0, H1 = int(np.floor(H_R * F / Z_S)), int(np.ceil(H_R * F / Ze)) + 1
    for H in range(H0, H1 + 1):
        for i, (Q, a) in enumerate(cuts['R', 'walk']): put('R', 'walk', Q, a, PPM['regular_full'], H / H_R, 'feet', key=H)
    Hf = int(round(H_R * F / Ze))            # (à la porte : la taille qu'il y a en marchant)
    for Q, a in cuts['R', 'fix']: put('R', 'fix', Q, a, PPM['regular_full'], Hf / H_R, 'feet')

    A = Atlas(1024)
    cells = {'T': {}, 'R': {}}
    pals = {}
    for who in ('T', 'R'):
        graded = [(g, k, grade(255 * (np.clip(rgb, 0, 255) / 255) ** LIFT[who], m), m, ox, oy, h0) for g, k, rgb, m, ox, oy, h0 in raw[who]]
        allc = np.concatenate([c[m] for _, _, c, m, *_ in graded])
        pal = palette(np.clip(allc, 0, 255), PALETTE); pals[who] = pal
        for g, k, rgb, m, ox, oy, h0 in graded:
            q = pal[R.nearest(np.clip(rgb.reshape(-1, 3), 0, 255), pal)].reshape(rgb.shape)
            rgba = np.zeros(rgb.shape[:2] + (4,), np.uint8); rgba[..., :3] = np.round(q); rgba[..., 3] = m * 255
            box = A.add(rgba)
            cells[who].setdefault(g, []).append((k, box + [int(ox), int(oy)]))
    NA = [A.add(c) for c in naruto_cells()]
    # ce qui est devant Teuchi (la lanterne, les objets et l'arête du comptoir, les tabourets) : rien de lui n'y passe
    src = np.asarray(Image.open(R.SRC).convert('RGB')).astype(float)
    pix, hem = R.glass_pixels()
    col_, sid = R.render(src, pix)
    surf = R.reduce(col_, sid)[2]
    zx0, zy0, zx1, zy1 = R.ZONE
    occ = np.zeros((zy1 - zy0, zx1 - zx0, 4), np.uint8)
    for (x, y), k in zip(pix, surf):
        if k not in (1, 10): occ[y - zy0, x - zx0] = (0, 0, 0, 255)
    OC = A.add(occ)
    X_POT = R.col_X(R.POT[1], R.Z_E)
    places = {'counter': PLACES['counter'], 'pots': round(col(X_POT + PLACES['pots'], Z_T), 1), 'shelf': round(col(PLACES['shelf'], Z_T), 1)}
    wisps = []
    for kind, (u0, v0, u1, v1), xc in R.OBJETS:
        if kind == 'bol':
            Zo = R.Z_C + R.OBJ_Z; hb = R.CTR_H + (v1 - v0) / R.K_OBJ
            wisps.append([xc, int(round(row(hb, Zo))), round(0.35 * F / Zo, 1), round(0.06 * F / Zo, 1)])
    wisps.append([R.POT[1], int(round(row(R.BACK_H + (R.V_REF - 515) / R.K_WALL, R.Z_E - 0.35))), round(0.5 * F / R.Z_E, 1), round(0.1 * F / R.Z_E, 1)])
    Xs = R.col_X(R.STOOLS[0], Z_STOOL); Xn = R.col_X(R.STOOLS[2], Z_STOOL)
    # chaque case : [sx, sy, w, h, ox, oy] (ox, oy : où tombe dans la case le milieu du buste, au haut de la tête ou au sol) ;
    # les rangées où les poser : la tête à sa taille, les pieds au sol, à leur profondeur
    lst = lambda who, g: [b for _, b in cells[who][g]]
    IRF = {'T': {g: lst('T', g) for g in ('idle', 'calm', 'nod', 'smile', 'stir', 'lift', 'serve', 'shelf', 'walk')},
           'Ty': {'head': round(row(H_T, Z_T), 2), 'feet': round(row(0, Z_T), 2)}, 'Tz': round(Z_T, 2), 'at': places,
           'D': {g: lst('T', g) for g in ('dwalk', 'dfront', 'dbrow', 'dpole')},
           'Dz': [door_x, DOOR_Z, round(row(0, DOOR_Z), 2)],
           'S': {g: lst('R', g) for g in ('seat', 'chop', 'sip', 'done', 'turn', 'rise', 'jacket', 'stand')},
           'Sx': round(col(Xs, Z_S), 1), 'Sy': round(row(0, Z_S), 2),
           'W': {'h0': H0, 'cells': [[b for k, b in cells['R']['walk'] if k == H] for H in range(H0, H1 + 1)], 'fix': lst('R', 'fix'),
                 'top': H_R, 'from': [round(Xs, 3), round(Z_S, 2)], 'to': [round(Xe, 3), round(Ze, 2)]},
           'N': {'cells': NA, 'x': round(col(Xn, Z_S), 1), 'y': N_TOP, 'cx': 11.5},
           'O': OC + [zx0, zy0], 'G': glass_rows(hem), 'wisps': wisps}
    img = A.image()
    print('Teuchi Z %.2f (%.1f px/m), à la porte Z %.2f (%.1f px/m, colonne %d, sa perche à %d) | le client assis Z %.2f (%.1f px/m), '
          'en marche de Z %.2f à %.2f (%d à %d px) | %d cases, atlas %d x %d, palettes %d et %d couleurs' % (Z_T, s_t, DOOR_Z, s_door,
          door_x, POLE_X, Z_S, s_s, Z_S, Ze, H0, H1, len(A.cells), img.shape[1], img.shape[0], len(pals['T']), len(pals['R'])))
    if prev:
        bg = np.full(img.shape[:2] + (3,), (90, 40, 30), float); al = img[..., 3:] / 255
        bg = bg * (1 - al) + img[..., :3] * al
        Image.fromarray(bg.astype(np.uint8)).save(os.path.join(prev, 'atlas_x1.png'))
        json.dump(IRF, open(os.path.join(prev, 'irf.json'), 'w'))
        return
    Image.fromarray(img, 'RGBA').save(I.A(OUT), 'WEBP', lossless=True, quality=100, method=6, exact=True)
    js = open(JS, encoding='utf-8').read()
    line = 'const IRF = ' + json.dumps(IRF, separators=(',', ':')) + ';'
    js2, n = re.subn(r'const IRF = \{.*?\};', lambda m: line, js, count=1)
    assert n == 1, 'la ligne IRF manque dans assets/street.js'
    if js2 != js: open(JS, 'w', encoding='utf-8').write(js2)


if __name__ == '__main__':
    main()
