#!/usr/bin/env python3
"""Ichiraku : Luffy (One Piece) au comptoir, le quatrième des quatre héros, assis comme les clients, de dos, sur le tabouret
du milieu, qui dévore ses ramen ; à côté de lui, sur le comptoir, la pile de ses bols vides.

    python3 tools/ichiraku_luffy.py                    (après tools/ichiraku_figures.py ; écrit assets/ichiraku_luffy.webp
                                                        et, dans assets/street.js, la ligne ILF : on peut le relancer, il
                                                        écrit la même chose)
    python3 tools/ichiraku_luffy.py --preview dossier  (des aperçus seulement : l'atlas x6, la ligne ILF en json)

Les planches (tools/src/ichiraku_luffy_sheet.webp, _b, _c : des brouillons faits pour lui, peints, sans contour, ses
proportions vraies, sur fond blanc, assis sur un tabouret qu'on ne voit pas ; le propriétaire : « juste regen plusieurs planches
si besoin », puis « la coiffure était mieux avant ») : de dos, sa tignasse d'un noir de jais, de grosses mèches en pointe tout
autour de sa tête, son chapeau de paille pendu dans le dos par son cordon, au milieu de son dos, sa calotte et son ruban rouge
vers nous, son bord tout autour ; son gilet rouge sans manches, son short bleu au revers clair, ses sandales ; il mange, lève
ses nouilles, boit le bouillon, mâche les joues pleines, tend son bol vide, son bras de caoutchouc un peu, puis un peu plus ; il
tourne la tête avec son grand sourire, et salue. Ses gestes vont à droite, vers Teuchi. Le bol dont il mange est devant lui :
de dos on ne le voit pas (« Luffy, le bol, on doit pas le voir s'il est de dos »), sauf levé au-dessus de son visage (son bord
dépasse au-dessus de sa tête, derrière ses cheveux) ou tendu vers Teuchi. Toutes refaites sur un même dos : son torse droit,
son chapeau au même endroit de son dos. Chaque image prise seule sur son blanc, ramenée à une largeur de hanches (HIPS : les
planches dessinent leurs images à des échelles un peu différentes), puis le même chemin
que les gens de la boutique (tools/ichiraku_figures.py et ses fonctions : la découpe, l'assise sur le tabouret qu'on ne voit
pas et les jambes resserrées (sit), les trois parts chacune à sa vraie échelle, la lumière chaude d'en haut, ses couleurs vives
un peu éteintes (mute), ses familles de tons, pas de trait au bord, le grain) ; son style, celui des autres : la couleur (B).
Rien n'y est repeint ni déplacé.

Sa vraie taille : 1,74 m, à la profondeur des clients assis (Z_S : les mêmes tabourets, le même comptoir), assis sur le coussin
comme le client (SIT : penché sur son bol) ; sa mesure (REF) prise sur ses images de dos : la tête jusqu'au col, le col à
l'assise, ses épaules (43 cm, S), la largeur de sa tête. Sa colonne (X_COL) : sur le tabouret du milieu, un peu à droite de son
milieu, sa tête au milieu de la vitrine ; chaque image posée par le milieu de ses hanches (ANCHOR) : assis, son assise et ses
jambes ne bougent pas d'une image à l'autre (au pixel près), le haut de son corps seul suit ses gestes, son chapeau avec lui
(à deux pixels près). Le sourire gardé (le blanc des dents que la découpe prendrait pour le fond, rendu à la tête).

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
SHEETS = {k: os.path.join(ICI, 'src', f'ichiraku_luffy_sheet{s}.webp') for k, s in (('a', ''), ('b', '_b'), ('c', '_c'))}
OUT = os.path.join(ROOT, 'assets', 'ichiraku_luffy.webp')
JS = os.path.join(ROOT, 'assets', 'street.js')
H_L = 1.74 * FG.SCALE                         # sa taille (mètres de la maquette)
HN = 65                                       # (de dos : du haut du crâne au col, en pixels de planche, ses hanches à HIPS)
REF = dict(H=H_L, head=HN, torso=138 / FG.SIT, sh=100, hw=58, S=0.43 * FG.SCALE)   # (mesurés sur ses images de dos, les bras
GROUP = ('L', 1.0, HN, 'seat')                #  le long du corps : du col à l'assise 138 ; ses épaules, 100 ; sa tête, 58 de large)
HEAD_L = 0.25 * FG.SCALE                      # (du haut du crâne au col, ses cheveux en bataille compris)
LEGS = 0.7                                    # (ses jambes resserrées d'autant : la planche les écarte, accroupi)
ANKLE = (14, 0.07)                            # (ses sandales : tant de pixels de planche au-dessus du bas, à tant de m du sol, à l'échelle du
                                              #  corps ; ses jambes seules étirées jusqu'à l'assise)
INK_FACE = (0.55, 0.65)                       # (le sourire : ses dents blanches gardées, un trait sombre pris s'il couvre au moins tant)
X_COL = 1197.0                                # la colonne de son milieu (le tabouret du milieu est à 1189,5 : il est assis sur son bord)
# les images des planches : la planche, leur boîte (x0, y0, x1, y1) ; face : le blanc des dents gardé. Ses gestes y vont déjà
# vers la droite, vers Teuchi : elles ne sont pas retournées. Le bol dont il mange est devant lui : de dos, sa tête, ses épaules
# et son dos le cachent (le propriétaire : « Luffy, le bol, on doit pas le voir s'il est de dos ») ; refaites sur le dos de la
# planche a (son image chew), la b : il mange (ses coudes seuls de part et d'autre), il boit (le bord du bol levé dépasse
# au-dessus de sa tête, derrière ses cheveux) ; la c : il lève ses nouilles, le bol caché devant sa poitrine
FRAMES = {'eat': ('b', (119, 199, 379, 613), {}), 'noodles': ('c', (178, 54, 537, 703), {}), 'drink': ('b', (878, 166, 1144, 613), {}),
          'chew': ('a', (784, 45, 914, 271), {}), 'hold': ('a', (315, 301, 463, 523), {}), 'stretch': ('a', (484, 299, 680, 523), {}),
          'stretch2': ('a', (700, 300, 933, 523), {}), 'grin': ('a', (397, 576, 525, 809), dict(face=True)),
          'wave': ('a', (546, 549, 680, 809), dict(face=True)), 'wave_b': ('a', (700, 567, 852, 809), dict(face=True))}
HIPS = 136.0                                  # (la largeur de ses hanches, son short juste sous l'assise, où chaque image est ramenée :
                                              #  la planche dessine ses rangées à des échelles un peu différentes)
ANCHOR = 'hips'                               # (ce qui pose chaque image en x : le milieu de ses hanches, assis sur le coussin : son
                                              #  assise ne bouge pas, le haut de son corps seul se penche avec ses gestes)
CHROMA = 0.8                                  # (ses couleurs vives dans la lumière de la boutique : leur saturation gardée à tant)
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


def hips_of(P, m):
    """son assise et ses hanches (pixels de la case) : la première rangée pleine de son short bleu, le milieu et la largeur du
    short juste dessous"""
    r, b = P[..., 0], P[..., 2]; blue = m & (b > r + 20)
    by = np.nonzero(blue.sum(1) > 0.3 * blue.sum(1).max())[0]; seat = int(by.min())
    ed = [(np.nonzero(blue[y])[0].min(), np.nonzero(blue[y])[0].max() + 1) for y in range(seat + 5, seat + 20) if blue[y].sum() > 20]
    return seat, float(np.median([(a + e) / 2 for a, e in ed])), float(np.median([e - a for a, e in ed]))


def load_sheet(path):
    """une planche, et ses taches d'encre (ce qui n'est pas le blanc, d'un tenant à deux pixels près)"""
    sheet = np.asarray(Image.open(path).convert('RGB')).astype(float)
    return sheet, FG.label(FG.grow((765 - sheet.sum(2)) > 60, 2))[0]


def frame_of(sheet, lab_, box):
    """une image de la planche seule sur son blanc (ce qui est d'elle : les taches d'encre de la planche, lab_, dont la moitié
    au moins tombe dans sa boîte ; pas la tête d'une voisine), ramenée à la largeur de hanches HIPS"""
    x0, y0, x1, y1 = box; H, W = sheet.shape[:2]; pd = 12
    a0, b0, a1, b1 = max(0, x0 - pd), max(0, y0 - pd), min(W, x1 + pd), min(H, y1 + pd)
    inbox = np.zeros((H, W), bool); inbox[y0:y1, x0:x1] = True
    ids = np.unique(lab_[b0:b1, a0:a1]); ids = ids[ids > 0]
    keep = [j for j in ids if (inbox & (lab_ == j)).sum() >= 0.5 * (lab_ == j).sum()]
    m = np.isin(lab_[b0:b1, a0:a1], keep)
    P = np.where(m[..., None], sheet[b0:b1, a0:a1], 255.0); ink = (765 - P.sum(2)) > 60
    k = HIPS / hips_of(P, ink & m)[2]
    im = Image.fromarray(np.clip(np.round(P), 0, 255).astype(np.uint8)).resize((round(P.shape[1] * k), round(P.shape[0] * k)), Image.LANCZOS)
    return np.asarray(im).astype(float)


def hat_x(Q, a):
    """le milieu de son chapeau (colonne de la case) : la paille entre les bords de son gilet, du haut du gilet à l'assise ; les
    colonnes où elle est dense"""
    r, g, b = Q[..., 0], Q[..., 1], Q[..., 2]; m = a > 0.5
    vest = m & (r > 70) & (g < 0.5 * r) & (b < 0.45 * r) & (r - g > 50)
    seat = hips_of(Q, m)[0]; inside = np.zeros_like(m)
    for y in range(int(np.nonzero(vest.sum(1) > 15)[0][0]), seat):
        xs = np.nonzero(vest[y])[0]
        if len(xs) > 10: inside[y, xs.min():xs.max() + 1] = True
    straw = inside & m & (r > 110) & (g > 0.58 * r) & (b < 0.62 * r)
    lab_, n = FG.label(FG.grow(straw, 2) & inside); sz = np.bincount(lab_.ravel()); sz[0] = 0
    hat = (lab_ == sz.argmax()) & straw
    cols = hat.sum(0); c = np.nonzero(cols >= 0.25 * cols.max())[0]
    return (c.min() + c.max() + 1) / 2


def cells():
    """chaque image de la planche à sa profondeur et à sa vraie taille : ses couleurs, son plein, sa tête, et où la poser"""
    FG.REF['L'] = REF; FG.GROUP['luffy'] = GROUP; FG.HEAD['L'] = HEAD_L
    if 'luffy' not in FG.BACK: FG.BACK = FG.BACK + ('luffy',)
    sheets = {k: load_sheet(p) for k, p in SHEETS.items()}
    s = FG.F / FG.Z_S; anchor = FG.row(0, FG.Z_S)
    out = {}
    for name, (sk, box, o) in FRAMES.items():
        P = frame_of(*sheets[sk], box); box = (0, 0, P.shape[1], P.shape[0])
        Q, a, _ = FG.cut({'luffy': P}, 'luffy', box, 'free', dict(multi=True))
        crown = hair_crown(Q, a); face = o.get('face')
        if face: a = keep_teeth(Q, a, crown)
        o = dict(g='luffy', crown=box[1] + crown)
        Q, a, seat = FG.sit(Q, a, LEGS)
        g = FG.measure(a, o, box[1])
        cx = {'hat': hat_x, 'hips': lambda Q, a: hips_of(Q, a > 0.5)[1], 'chest': lambda Q, a: FG.chest(a)}[ANCHOR](Q, a)
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
        out[n] = dict(c, rgba=rgba)
    return out


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
