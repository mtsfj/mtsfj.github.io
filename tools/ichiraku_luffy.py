#!/usr/bin/env python3
"""Ichiraku : Luffy (One Piece) au comptoir, le quatrième des quatre héros, assis comme les clients, de dos, sur le tabouret
du milieu, qui dévore ses ramen ; à côté de lui, sur le comptoir, la pile de ses bols vides.

    python3 tools/ichiraku_luffy.py                    (après tools/ichiraku_figures.py ; écrit assets/ichiraku_luffy.webp
                                                        et, dans assets/street.js, la ligne ILF : on peut le relancer, il
                                                        écrit la même chose)
    python3 tools/ichiraku_luffy.py --preview dossier  (des aperçus seulement : l'atlas x6, la ligne ILF en json)

La planche (tools/src/ichiraku_luffy_sheet.webp, un brouillon fait pour lui sur le modèle de la planche du client, sur fond
blanc, assis sur un tabouret qu'on ne voit pas) : de dos comme le client, ses cheveux noirs en bataille, son chapeau de paille
pendu dans le dos par son cordon, son gilet rouge, son short bleu au revers clair, ses sandales ; il mange (le bol à hauteur de
menton, les baguettes à la bouche, la joue pleine), lève ses nouilles, boit le bouillon le bol sur le visage, tend son bol vide,
mâche les joues pleines ; il se retourne avec son grand sourire, et salue. Retournée (FLIP) : son bol, ses gestes du côté de
Teuchi et de la pile. Le même chemin que les gens de la boutique (tools/ichiraku_figures.py et ses fonctions : la découpe,
l'assise sur le tabouret qu'on ne voit pas et les jambes resserrées (sit), les trois parts chacune à sa vraie échelle, la
lumière chaude d'en haut, ses couleurs vives un peu éteintes (mute), ses familles de tons, pas de trait au bord, le grain) ;
son style, celui des autres : la couleur (B).

Sa vraie taille : 1,74 m, à la profondeur des clients assis (Z_S : les mêmes tabourets, le même comptoir), assis sur le coussin
comme le client (SIT : penché sur son bol) ; sa mesure (REF) prise sur la première image : la tête jusqu'au col, le col à
l'assise, ses hanches (ses épaules de 43 cm, S), la largeur de ses cheveux. Sa colonne (X_COL) : sur le tabouret du milieu,
un peu à droite de son milieu, sa tête derrière la troisième vitre (pas derrière le montant). Ce qui est fait des images : le
sourire gardé (le blanc des dents que la découpe prendrait pour le fond, rendu à la tête) ; la cicatrice sous son oeil gauche
(SCAR) ; le bras tendu, en caoutchouc (stretch : de sa main au bol, poussés de STRETCH pixels, l'avant-bras étiré entre) ; la
main qui salue d'un pixel de côté (wave_b).

La pile : ses bols vides sur le comptoir, à sa gauche, devant le tabouret du coin, vide (STACK : leur colonne, la rangée du
comptoir à leur profondeur) : six au plus, une petite pile nette ; des bols de ramen blancs dans la lumière chaude (BOWL),
emboîtés (un bol de plus : son bord STEP pixels plus haut, son dessous plus étroit) ; le bol du haut montre son dedans. Il faut Pillow, numpy (et ce qu'il faut à tools/ichiraku_figures.py).
"""
import json
import os
import re
import sys
import numpy as np
from PIL import Image

sys.dont_write_bytecode = True
ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import ichiraku_figures as FG                                    # noqa: E402
import ichiraku_interior as R                                    # noqa: E402

ROOT = os.path.dirname(ICI)
SHEET = os.path.join(ICI, 'src', 'ichiraku_luffy_sheet.webp')
OUT = os.path.join(ROOT, 'assets', 'ichiraku_luffy.webp')
JS = os.path.join(ROOT, 'assets', 'street.js')
H_L = 1.74 * FG.SCALE                         # sa taille (mètres de la maquette)
HN = 60                                       # (de dos : du haut du crâne au col, en pixels de planche)
REF = dict(H=H_L, head=HN, torso=106 / FG.SIT, sh=85, hw=56, S=0.43 * FG.SCALE)   # (la première image : le crâne à 22, le col
GROUP = ('L', 1.0, HN, 'seat')                #  à 82, l'assise à 188 ; ses hanches, 106, pour des épaules de 85 ; ses cheveux en
                                              #  bataille, 64 de large : 27 cm)
HEAD_L = 0.25 * FG.SCALE                      # (du haut du crâne au col, ses cheveux en bataille compris)
LEGS = 0.7                                    # (ses jambes resserrées d'autant : la planche les écarte, accroupi)
ANKLE = (14, 0.07)                            # (ses sandales : tant de pixels de planche au-dessus du bas, à tant de m du sol, à l'échelle du
                                              #  corps ; ses jambes seules étirées jusqu'à l'assise)
INK_FACE = (0.55, 0.65)                       # (le sourire : ses dents blanches gardées, un trait sombre pris s'il couvre au moins tant)
X_COL = 1197.0                                # la colonne de son milieu (le tabouret du milieu est à 1189,5 : il est assis sur son bord)
FLIP = True                                   # (la planche retournée : son bol, ses gestes vers la droite, vers Teuchi et la pile)
# les images de la planche : leur boîte (x0, y0, x1, y1) ; face : le blanc des dents gardé
FRAMES = {'eat': ((54, 0, 230, 247), {}), 'noodles': ((360, 0, 515, 247), {}), 'drink': ((570, 0, 735, 247), {}),
          'hold': ((780, 4, 970, 247), {}), 'chew': ((1136, 8, 1290, 247), {}),
          'grin': ((70, 247, 232, 502), dict(face=True)), 'wave': ((420, 246, 600, 502), dict(face=True))}
HAT = 1.0                                     # (son chapeau, pendu à son cou par le cordon : ramené vers le milieu de son dos de tant ;
                                              #  la planche le met sur une épaule, derrière un montant de la vitre)
CHROMA = 0.8                                  # (ses couleurs vives dans la lumière de la boutique : leur saturation gardée à tant)
FACE = {'grin': (2, 12), 'wave': (3, 14)}     # (son visage tourné vers nous, trop petit pour que la réduction garde ses traits : redessiné,
                                              #  le milieu du visage à tant de sa colonne, les yeux à tant de son haut de crâne ; les yeux
                                              #  fermés de rire, la cicatrice sous son oeil gauche, le grand sourire)
STRETCH = (9, 18)                             # (le bras tendu, en caoutchouc : de tant de pixels de la scène, puis de tant)
BOWL = ((226, 208, 178), (204, 184, 156), (150, 128, 108), (112, 92, 78), (96, 52, 34))   # (des bols de ramen blancs, à la lumière chaude :
                                             #  le bord, le flanc, son dessous à l'ombre, le pied, le dedans ; « pas de bouillie »)
STACK = (1165.5, 641)                         # la pile : la colonne de son milieu (à sa gauche, à la place du tabouret du coin, vide : toute
                                              #  derrière la première vitre, rien devant elle), la rangée du comptoir sous elle
STEP = 3                                      # (un bol emboîté de plus : son bord tant de rangées plus haut : son bord, son flanc, son
                                              #  dessous plus étroit, d'un bol à l'autre)
FAMILIES = 20
SEED = 7


def hair_crown(Q, a):
    """le haut de son crâne (rangée de la case) : la première rangée d'au moins six pixels de ses cheveux noirs (ni le bol, ni
    les baguettes, ni les nouilles levés au-dessus de sa tête)"""
    m = a > 0.5; hair = m & (Q.max(2) < 70) & (Q.max(2) - Q.min(2) < 25)
    return int(np.nonzero(hair.sum(1) >= 6)[0][0])


def keep_teeth(Q, a, crown):
    """le blanc enfermé dans sa tête (ses dents : la découpe le prend pour le fond) rendu à la figure"""
    fig = a > 0.5; lab_, n = FG.label(~fig); H, W = fig.shape
    edge = set(lab_[0]) | set(lab_[-1]) | set(lab_[:, 0]) | set(lab_[:, -1])
    a = a.copy()
    for j in range(1, n + 1):
        if j in edge: continue
        ys, xs = np.nonzero(lab_ == j)
        if ys.min() >= crown and ys.max() <= crown + HN: a[ys, xs] = 1.0
    return a


def centre_hat(Q, a):
    """son chapeau de paille ramené vers le milieu de son dos (au-dessus du milieu de ses hanches ; de HAT) : le chapeau, un
    disque (l'ellipse de la boîte de sa paille : le bord, la bande, le fond, leur trait), déplacé ; là où il était, son gilet
    (le rouge médian de la rangée), ou le fond au-delà du bord de la figure (le gilet : l'autre côté de son dos en miroir, ses plis et son ombre, pas un aplat)"""
    r, g, b = Q[..., 0], Q[..., 1], Q[..., 2]; fig = a > 0.5; H, W = fig.shape
    straw = fig & (r > 150) & (g > 105) & (b < 115) & (r - b > 75) & (g - b > 45)
    lab_, n = FG.label(straw); sz = np.bincount(lab_.ravel()); sz[0] = 0
    ys, xs = np.nonzero(lab_ == sz.argmax()); y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    my, mx = 0.3 * (y1 - y0), 0.3 * (x1 - x0)
    for j in np.nonzero(sz >= 40)[0]:                         # (le fond du chapeau, que sa bande sépare du bord)
        jy, jx = np.nonzero(lab_ == j)
        if jy.min() >= y0 - my and jy.max() <= y1 + my and jx.min() >= x0 - mx and jx.max() <= x1 + mx:
            y0, y1, x0, x1 = min(y0, jy.min()), max(y1, jy.max()), min(x0, jx.min()), max(x1, jx.max())
    cy, cx, ry, rx = (y0 + y1) / 2, (x0 + x1) / 2, (y1 - y0) / 2 + 1.5, (x1 - x0) / 2 + 1.5
    Y, X = np.mgrid[0:H, 0:W]
    disc = lambda c: ((Y - cy) / ry) ** 2 + ((X - c) / rx) ** 2 <= 1
    hat = fig & disc(cx)
    blue = fig & (b > r + 20) & (b > 90)                          # (son short : le milieu de ses hanches)
    by = np.nonzero(blue.sum(1) >= 0.5 * blue.sum(1).max())[0]; hips = np.nonzero(blue[by].any(0))[0]
    xs = (hips.min() + hips.max() + 1) / 2; dx = int(round(HAT * (xs - cx)))
    if dx == 0: return Q, a
    vest = fig & ~hat & (r > 90) & (g < 0.42 * r) & (b < 0.5 * r)
    Q2, a2 = Q.copy(), a.copy()
    for y in np.unique(np.nonzero(hat)[0]):
        ref = Q[y][vest[y]] if vest[y].any() else Q[vest]; c = np.median(ref, 0)
        outside = np.nonzero(fig[y] & ~hat[y])[0]
        for x in np.nonzero(hat[y])[0]:
            if (dx > 0 and not (outside < x).any()) or (dx < 0 and not (outside > x).any()): a2[y, x] = 0
            else:                            # (son gilet, l'autre côté de son dos en miroir : ses plis, son ombre ; sinon le rouge de la rangée)
                xm = int(round(2 * xs - x))
                Q2[y, x] = Q[y, xm] if 0 <= xm < W and vest[y, xm] else c
    hy, hx = np.nonzero(hat); ok = (hx + dx >= 0) & (hx + dx < W)
    Q2[hy[ok], hx[ok] + dx] = Q[hy[ok], hx[ok]]; a2[hy[ok], hx[ok] + dx] = 1.0
    return Q2, a2


def cells():
    """chaque image de la planche à sa profondeur et à sa vraie taille : ses couleurs, son plein, sa tête, et où la poser"""
    FG.REF['L'] = REF; FG.GROUP['luffy'] = GROUP; FG.HEAD['L'] = HEAD_L
    if 'luffy' not in FG.BACK: FG.BACK = FG.BACK + ('luffy',)
    sheets = {'luffy': np.asarray(Image.open(SHEET).convert('RGB')).astype(float)}
    s = FG.F / FG.Z_S; anchor = FG.row(0, FG.Z_S)
    out = {}
    for name, (box, o) in FRAMES.items():
        Q, a, _ = FG.cut(sheets, 'luffy', box, 'free', dict(multi=True, flip=FLIP))
        crown = hair_crown(Q, a); face = o.get('face')
        if face: a = keep_teeth(Q, a, crown)
        o = dict(g='luffy', crown=box[1] + crown)
        Q, a = centre_hat(Q, a)
        Q, a, seat = FG.sit(Q, a, LEGS)
        g = FG.measure(a, o, box[1]); cx = FG.chest(a)
        K, kh, khx, kb = FG.knots('L', o, g, a, seat, s, anchor)
        feet = K[-1][0]; K = K[:-1] + [(feet - ANKLE[0], anchor - s * ANKLE[1] * FG.SCALE), K[-1]]
        C, A, T, Lc, hd = FG.warp(Q, a, K, kh, khx, kb, g, -(cx - g['xn']) * kb)
        ink = FG.INK
        if face: FG.INK = INK_FACE
        rgb, m = FG.pick(C, A); hd &= m; FG.INK = ink
        ky, kY = [k[0] for k in K], [k[1] for k in K]
        Yc = np.interp(g['crown'], ky, kY); Yn = np.interp(g['neck'], ky, kY)
        ys, xs = np.nonzero(m); t, b_, l, r_ = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        out[name] = dict(rgb=rgb[t:b_, l:r_], m=m[t:b_, l:r_], hd=hd[t:b_, l:r_], hy=(Yc - T - t, Yn - T - t),
                         ox=-(Lc + l), oy=int(round(anchor)) - (T + t))
    return out


def colour(raw):
    """la couleur (B), celle des autres : la lumière chaude d'en haut, ses couleurs vives un peu éteintes, ses familles de tons
    gardées dans la clarté de la peinture, pas de trait au bord (la lumière des gens assis), les traits du visage selon la taille
    de sa tête, peu de pixels seuls, un grain fin"""
    graded = {n: FG.mute(FG.grade(np.clip(c['rgb'], 0, 255), c['m']), CHROMA) for n, c in raw.items()}
    allc = np.concatenate([graded[n][raw[n]['m']] for n in raw])
    fam = FG.palette(np.clip(allc, 0, 255), FAMILIES); Lf = R.lab(fam)[:, 0]; famB = FG.cap_values(fam)
    out = {}
    for i, (n, c) in enumerate(raw.items()):
        m = c['m']
        idx = np.where(m, R.nearest(np.clip(graded[n].reshape(-1, 3), 0, 255), fam).reshape(m.shape), -1)
        idx = FG.no_outline(idx, m, Lf, FG.LIGHT['S'])
        idx, keep = FG.face_detail(idx, m, c['hd'], c['hy'], fam)
        idx = FG.unspeckle(idx, m, keep)
        g = np.random.default_rng(SEED + i).integers(-FG.GRAIN_B, FG.GRAIN_B + 1, m.shape)
        rgba = np.zeros(m.shape + (4,)); rgba[..., 3] = m * 255
        rgba[..., :3] = np.clip(np.round(famB[np.maximum(idx, 0)] + g[..., None]), 0, 255) * m[..., None]
        if n in FACE:                         # (son visage : les yeux fermés de rire, la cicatrice, les dents, la lèvre)
            dx, dy = FACE[n]; x = int(c['ox']) + dx; y = int(np.floor(c['hy'][0])) + dy
            lab_ = R.lab(famB); dark = famB[np.argmin(lab_[:, 0])]
            white = famB[np.argmax(lab_[:, 0] - 3 * np.hypot(lab_[:, 1], lab_[:, 2]))]
            scar = famB[np.argmin(np.abs(lab_[:, 0] - 30) + np.abs(lab_[:, 1] - 30) + np.abs(lab_[:, 2] - 20))]
            for xx, yy, cc in ([(x - 3, y, dark), (x - 2, y, dark), (x + 1, y, dark), (x + 2, y, dark), (x + 2, y + 2, scar)]
                               + [(xx, y + 3, white) for xx in range(x - 3, x + 3)] + [(x - 3, y + 4, dark), (x + 2, y + 4, dark)]
                               + [(xx, y + 4, white) for xx in range(x - 2, x + 2)] + [(xx, y + 5, dark) for xx in range(x - 2, x + 2)]):
                rgba[yy, xx, :3] = cc
        out[n] = dict(c, rgba=rgba)
    return out


def stretch(c, d):
    """le bras qui tient le bol, tendu en caoutchouc : sur les rangées du bras et du bol, ce qui est à droite de son poignet
    (sa main, le bol) poussé de d pixels, le poignet étiré entre (sa coupe, répétée) ; le reste tel quel"""
    rgba = c['rgba']; m = rgba[..., 3] > 0; h, w = m.shape
    L = rgba[..., :3].mean(2); sat = rgba[..., :3].max(2) - rgba[..., :3].min(2)
    bowl = m & (sat < 40) & (L < 80); bowl[:, :int(c['ox']) + 8] = False   # (le bol : sombre, peu saturé, loin du buste ; son plus
    lab_, n = FG.label(bowl); sz = np.bincount(lab_.ravel()); sz[0] = 0      #  grand morceau)
    ys, xs = np.nonzero(lab_ == sz.argmax()); bx = int(xs.min()); r0, r1 = max(0, ys.min() - 2), ys.max() + 3
    skin = m & (rgba[..., 0] > rgba[..., 2] + 30) & (rgba[..., 1] > 0.45 * rgba[..., 0])
    xc = max(range(bx - 5, bx), key=lambda x: (int(skin[r0:r1, x].sum()), x))   # (sa main, juste avant le bol : la peau qu'on étire)
    new = np.zeros((h, w + d, 4)); new[:, :w] = rgba
    new[r0:r1, xc:] = 0; new[r0:r1, xc + d:] = rgba[r0:r1, xc:]
    new[r0:r1, xc:xc + d] = rgba[r0:r1, xc:xc + 1]
    return dict(c, rgba=new)


def wave_b(c):
    """la main qui salue, d'un pixel vers la gauche : au-dessus du haut de sa tête, à gauche de son milieu"""
    rgba = c['rgba']; h, w = rgba.shape[:2]
    wb = np.zeros((h, w + 1, 4)); wb[:, 1:] = rgba
    hh = int(np.ceil(c['hy'][0])) + 1; x0 = int(c['ox']) - 6
    hand = wb[:hh, 1:x0 + 1].copy(); wb[:hh, :x0 + 1] = 0; wb[:hh, :x0] = hand
    return dict(c, rgba=wb, ox=c['ox'] + 1)


def bowls():
    """deux cases : un bol vu de côté dans la pile (son bord clair sur toute sa largeur, son flanc, son dessous à l'ombre plus
    étroit, son pied) et le bol du haut (son dedans sous son bord) ; 9 pixels de large (la première vitre en a 11)"""
    rim, body, shade, foot, inside = (np.array(c, float) for c in BOWL)
    side = np.zeros((4, 9, 4)); top = np.zeros((5, 9, 4))
    def put(img, y, x0, x1, col): img[y, x0:x1, :3] = col; img[y, x0:x1, 3] = 255
    put(side, 0, 0, 9, rim); put(side, 1, 0, 9, body); put(side, 2, 1, 8, shade); put(side, 3, 3, 6, foot)
    put(top, 0, 1, 8, rim); put(top, 1, 0, 9, rim); top[1, 2:7, :3] = inside; put(top, 2, 0, 9, body)
    put(top, 3, 1, 8, shade); put(top, 4, 3, 6, foot)
    return side, top


def main():
    prev = sys.argv[sys.argv.index('--preview') + 1] if '--preview' in sys.argv else None
    raw = cells(); col = colour(raw)
    col['stretch'] = stretch(col['hold'], STRETCH[0]); col['stretch2'] = stretch(col['hold'], STRETCH[1])
    col['wave_b'] = wave_b(col['wave'])
    side, topb = bowls()
    order = ['eat', 'noodles', 'drink', 'hold', 'chew', 'stretch', 'stretch2', 'grin', 'wave', 'wave_b']
    A = FG.Atlas(512); boxes = {}
    for n in order:
        c = col[n]; box = A.add(np.round(c['rgba']).astype(np.uint8))
        boxes[n] = box + [int(c['ox']), int(c['oy'])]
    bs = A.add(np.round(side).astype(np.uint8)); bt = A.add(np.round(topb).astype(np.uint8))
    img, _ = A.image()
    hy = {n: round(float(col[n]['hy'][0]), 1) for n in order}
    ILF = {'cells': boxes, 'x': X_COL, 'y': round(FG.row(0, FG.Z_S), 2), 'head': hy, 'bowl': bs, 'top': bt,
           'stack': [STACK[0], STACK[1], STEP]}
    print('Luffy : Z %.2f (%.1f px/m), colonne %.1f, sol %.1f, le haut de sa tête à %d | %d cases, atlas %d x %d' % (
        FG.Z_S, FG.F / FG.Z_S, X_COL, ILF['y'], int(round(ILF['y'])) - boxes['eat'][5] + int(round(hy['eat'])),
        len(boxes) + 2, img.shape[1], img.shape[0]))
    if prev:
        os.makedirs(prev, exist_ok=True)
        bg = np.full(img.shape[:2] + (3,), (90, 40, 30), float); al = img[..., 3:] / 255
        Image.fromarray((bg * (1 - al) + img[..., :3] * al).astype(np.uint8)).resize((img.shape[1] * 6, img.shape[0] * 6), Image.NEAREST).save(os.path.join(prev, 'atlas_x6.png'))
        json.dump(ILF, open(os.path.join(prev, 'ilf.json'), 'w'))
        return ILF, img
    Image.fromarray(img, 'RGBA').save(OUT, 'WEBP', lossless=True, quality=100, method=6, exact=True)
    js = open(JS, encoding='utf-8').read()
    line = 'const ILF = ' + json.dumps(ILF, separators=(',', ':')) + ';'
    js2, n = re.subn(r'const ILF = \{.*?\};', lambda m: line, js, count=1)
    if n and js2 != js: open(JS, 'w', encoding='utf-8').write(js2)
    print('wrote', OUT, '| street.js ILF', 'updated' if n else 'NOT FOUND')


if __name__ == '__main__':
    main()
