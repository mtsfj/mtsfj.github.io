#!/usr/bin/env python3
"""L'oden : son maître, découpé des deux planches du propriétaire, à sa vraie taille et à sa profondeur dans la maquette de
tools/oden_interior.py, au grain de la peinture.

    python3 tools/oden_master.py                  (après tools/oden_interior.py ; réécrit assets/oden_master.webp et, dans
                                                    assets/street.js, la ligne OMF : on peut le relancer, il écrit la même chose)
    python3 tools/oden_master.py --preview dossier (des aperçus seulement : l'atlas, l'atlas x4, la ligne OMF en json)

Les planches (tools/src/planches/, fond blanc, chacune en deux versions v1 et v2 ; on prend les v1, SHEETS) :
oden_1_comptoir, à mi-corps derrière un comptoir (au repos, la tête qui penche, content les yeux fermés, le rire ; à la
marmite fumante : les baguettes, le daikon levé, la louche de bouillon, l'assiette servie, l'assiette tendue ; l'essuyage du
comptoir, deux images) ; oden_2_entier, en entier (de profil debout, de profil la main à hauteur de taille sur une poignée
qu'on ne voit pas, de trois quarts appuyé au cadre en regardant la pluie ; sa marche de profil en six images). Pourquoi les
v1 : leurs deux planches sont le même homme (le même bleu du samue, 55-60-82 contre 55-62-85, le même beige du tablier, le
même visage rond et souriant, une barbe de quelques jours), quand la v2 du comptoir a un bleu plus gris, un tablier plus
sombre que celui de sa v2 en entier, et de la vapeur peinte par-dessus son tablier (elle resterait dans ses couleurs) ; la
marche de la v1 est une vraie marche (les bras qui balancent, le pas qui passe), celle de la v2 garde les bras le long du
corps et répète presque la même image. Les rangées de la v1 en entier ne sont pas dessinées à la même échelle (la marche à
0,845 de la rangée du haut : sa hauteur, son tablier, son col), mais chacune est d'une seule proportion : on les ramène.

Sa taille (le modèle B de tools/figures_audit.py) : l'œil de la peinture est à 1,26 m du trottoir, celui de la maquette à
1,5 m ; un homme de H_REAL = 1,70 m y fait donc H_TOP = 2,02 mètres de maquette (SIZE), la pièce, le comptoir et la porte
inchangés. Les planches le dessinent à 6 têtes de haut ; il en fait HEADS = 6,7 (sa tête 0,30 m de maquette : 11 px à la
porte, 9 à la marmite) : chaque image redressée en deux parts (head) : la tête (du haut des cheveux et du bandeau au menton,
ce qui n'est ni le samue ni le tablier, d'un seul tenant) ramenée autour du cou à sa hauteur, sans déformation ; le corps
dessous à sa vraie longueur, du menton aux semelles.

Chaque rangée de planche a son échelle (ROWS : son rapport à la rangée du haut de la planche en entier, mesuré à la hauteur
et au tablier pour la marche, à la largeur du visage pour les rangées du comptoir, à la hauteur de la tête pour passer d'une
planche à l'autre ; et la hauteur de sa tête, px de la planche). En entier, ses semelles font le sol ; au comptoir (la
planche le coupe), le sol de la rangée est sous son menton à la longueur de son corps (celui de sa première image : une tête
qui penche ne le fait pas descendre). Ce qui est sous CUT de haut s'en va (le comptoir, la marmite, sa vapeur : plus bas que
le verre, 1,40 m au plus bas) ; ce qu'il tient reste (les baguettes, le daikon, la louche, l'assiette).

L'image découpée : ce qui s'écarte du blanc (le halo clair du bord dehors), ses trous bouchés, la plus grande pièce ; sa
couleur prise sur le dedans (deux pixels de la planche sous le bord : pas de liseré blanc). Le visage : sous 10 px de tête
aucun trait, de 10 à 15 un pixel par œil (les règles du grain de la maison) ; tout ce qui n'est pas de la peau dans le visage
(les yeux, les sourcils, la barbe jusqu'au bord du menton, la bouche) y est repeint de la peau voisine, et à la porte (sa tête
de 11 px) un pixel sombre à la place de chaque œil (eyes_of). Les plis sombres des mains plus petits qu'un pixel de la rue (les
doigts d'un poing) : repeints de leur peau (no_specks), ce seraient des trous.

Réduction à la taille de chaque place (F / Z px par mètre) : chaque pixel prend la part de la planche qu'il couvre (une
boîte exacte), plein dès la moitié couverte (ni halo ni bord flou) ; sa couleur, la moyenne des pixels de la planche les plus
proches de leur médiane (un bord ne mêle pas deux matières). Puis la lumière : à la marmite, celle de la boutique (LIGHT,
chaude, d'en haut) ; à la porte, la boutique dans son dos (à gauche, chaude) et la nuit de la rue de l'autre côté (à droite,
COOL : plus sombre et bleue), la même au monde quel que soit son sens (les images de son retour, tourné vers la boutique,
retournées avant la lumière, non à l'affichage). Pas de trait sombre continu au bord : un pixel du bord tourné vers la
lumière n'est jamais plus sombre que celui qu'il couvre (no_outline) ; plus sombre seulement du côté de l'ombre. Enfin le
grain de la peinture (tools/regrain.py, le même chemin que les figures de la rue) : par place, toutes ses images ensemble,
FAMILIES familles de tons (k-moyennes en OKLab), chaque pixel à la sienne contre ses quatre voisins, un grain fin baké de 1 à
3 niveaux (Bayer 4 x 4 ancré à ses pieds), ses clairs ramenés sous la peinture voisine + 15 % (P95 : la porte et sa façade,
le verre de la fenêtre).

Ses places (tools/oden_interior.py) : à la marmite, derrière le comptoir dans son allée (Z_M), de face, vu par la fenêtre (au-
dessus de son appui on voit sa tête, ses épaules, le haut de son buste et ce que ses mains lèvent) ; il y vient de la cuisine
(à gauche, au fond) de profil, par derrière la porte et le trumeau. À la porte (Z_D, le milieu du vantail de droite) : il
vient de l'intérieur de profil jusqu'au vantail fermé, sa main tendue sur sa poignée (X_LEAF : le dedans du vantail ; PULL :
la poignée près du bord qui touche le cadre ; il se tient à la longueur de son bras derrière, GRAB), le fait glisser à gauche
derrière l'autre, s'avance d'un pas dans l'embrasure (X_LOOK, sur le seuil), y regarde la pluie (debout, puis appuyé de trois
quarts, le nez levé, sa tête là où elle était debout, son bras sur le mur derrière le cadre ; puis debout), recule
d'un pas, referme et s'en va. Ses pieds ne se voient jamais quand il marche (derrière le comptoir, derrière le bas de bois des
vantaux) ; seulement dans l'embrasure ouverte. Sa marche : WALK (1 m/s, une image toutes les 0,17 s, six images). Tout va dans
assets/oden_master.webp (rangé en étagères) ; assets/street.js lit la ligne OMF : chaque image, son ancre (le pied de son axe
sur le sol), ses places en px de la rue, son pas ; à la porte, les images de son retour déjà retournées (leur nom + '_m').
Il faut Pillow, numpy, scipy.
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
import oden_interior as O
import regrain as RG

ROOT = O.ROOT
PL = os.path.join(ROOT, 'tools', 'src', 'planches')
SHEETS = {'c': os.path.join(PL, 'oden_1_comptoir_v1.png'), 'e': os.path.join(PL, 'oden_2_entier_v1.png')}
JS = os.path.join(ROOT, 'assets', 'street.js')
OUT = 'oden_master.webp'
LUM = np.array([0.299, 0.587, 0.114])

SIZE = 1.5 / 1.26                     # mètres de la maquette pour un vrai (l'œil de la maquette à 1,5 m, celui de la peinture à 1,26)
H_REAL = 1.70                         # sa taille, du haut du bandeau aux semelles (m)
H_TOP = H_REAL * SIZE                 # (2,02 m de maquette)
HEADS = 6.7                           # sa hauteur en têtes
HEAD_M = H_TOP / HEADS                # (sa tête, du haut au menton : 0,30 m de maquette)
# les rangées de chaque planche : leurs rangées de la planche (y), leurs images, leur échelle contre la rangée du haut de la
# planche en entier, la hauteur de leur tête (du haut des cheveux au menton, une image droite ; px de la planche)
ROWS = {'e': (((0, 550), ('stand', 'grab', 'stand2'), 1.0, 84.0),
              ((550, 1024), ('w1', 'w2', 'w3', 'w4', 'w5', 'w6'), 0.845, 75.0)),
        'c': (((0, 360), ('idle', 'nod', 'happy', 'laugh'), 102 / 84, 102.0),
              ((360, 720), ('pick', 'lift', 'ladle', 'serve', 'offer'), 102 / 84 * 0.85, 86.7),
              ((720, 1024), ('wipe', 'wipe2'), 102 / 84 * 0.94, 95.9))}
CUT = 1.3                             # (au comptoir : rien de lui sous tant de haut, le comptoir et ce qui est dessus ; la planche met
                                      #  son comptoir à 1,25 m, la maquette à 1 m)
INK, HALO = 705, 740                  # (la somme R + G + B : sous INK, une image ; sous HALO, la figure ; au-dessus, le blanc et son halo)
FACE_PX = (10, 15)                    # (une tête de moins de 10 px : aucun trait ; jusqu'à 15 : un pixel par œil)


def classes(rgb):
    """les matières de la planche : la peau, le bleu du samue, le beige du tablier"""
    R, G, B = (rgb[..., c] for c in range(3))
    s = rgb.sum(-1)
    skin = (R > 150) & (G > 90) & (B < 160) & (R - B > 55)
    navy = (B > R + 12) & (s < 400)
    beige = (R > 185) & (G > 160) & (B > 110) & (R - B > 25) & (R - B < 80) & (G - B > 15)
    return skin & ~beige, navy, beige


def frames():
    """les images des deux planches, rangée par rangée de gauche à droite : leur boîte, leur couverture (ce qui s'écarte du
    blanc, le halo clair du bord dehors, ses trous bouchés, ce qui tient à l'image), leur rangée (son échelle, sa tête)"""
    out = {}
    for key, path in SHEETS.items():
        rgb = np.asarray(Image.open(path).convert('RGB')).astype(float)
        s = rgb.sum(2)
        core = s < INK
        lab, n = nd.label(core, np.ones((3, 3)))
        sz = nd.sum(core, lab, range(1, n + 1)); sl = nd.find_objects(lab)
        for (y0, y1), names, rk, head in ROWS[key]:
            comps = sorted([(sl[i][1].start, i + 1) for i in range(n) if sz[i] > 5000 and y0 <= sl[i][0].start < y1])
            assert len(comps) == len(names), (key, y0, len(comps))
            for (_, l), name in zip(comps, names):
                a = sl[l - 1]
                by0, bx0 = max(0, a[0].start - 4), max(0, a[1].start - 4)
                by1, bx1 = min(rgb.shape[0], a[0].stop + 4), min(rgb.shape[1], a[1].stop + 4)
                m = s[by0:by1, bx0:bx1] < HALO
                ml = nd.label(m, np.ones((3, 3)))[0]
                seed = nd.binary_dilation(lab[by0:by1, bx0:bx1] == l, iterations=2)
                m = np.isin(ml, np.unique(ml[seed & m]))
                m = nd.binary_fill_holes(m)
                out[name] = dict(sheet=key, rgb=rgb[by0:by1, bx0:bx1].copy(), m=m, x0=bx0, y0=by0, rk=rk, head=head,
                                 row0=names[0], frontal=key == 'c')
    return out


def biggest(m):
    lab, n = nd.label(m, np.ones((3, 3)))
    if n <= 1: return m
    sz = nd.sum(m, lab, range(1, n + 1))
    return nd.binary_fill_holes(lab == 1 + int(np.argmax(sz)))


def top_of(m):
    return int(np.where(m.any(1))[0][0])


def clean(F):
    """chaque image : son échelle (px de la planche par mètre), son menton, son sol ; au comptoir sans ce qui est sous CUT ;
    son visage sans traits (ses yeux notés) ; sa tête ramenée à HEAD_M autour du cou ; son axe"""
    for f in F.values():
        f['top'] = top_of(f['m']); f['chin'] = f['top'] + f['head']
    st = F['stand']
    ppm0 = (np.where(st['m'].any(1))[0][-1] + 1 - st['chin']) / (H_TOP - HEAD_M)   # (le corps de « stand », du menton aux semelles)
    for name, f in F.items():
        f['ppm'] = ppm = ppm0 * f['rk']
        if f['frontal']:                                                    # (au comptoir : le sol de la rangée, sous le menton de sa
            r0 = F[f['row0']]                                               #  première image ; sans ce qui est sous CUT)
            f['floor'] = r0['chin'] + r0['y0'] - f['y0'] + (H_TOP - HEAD_M) * ppm
            f['m'][int(np.ceil(f['floor'] - CUT * ppm)):] = False
            f['m'] = biggest(f['m'])
        else:
            f['floor'] = float(np.where(f['m'].any(1))[0][-1] + 1)
    for f in F.values():
        face(f)
        head(f)
        ya = lambda h: int(round(f['floor'] - h * f['ppm']))               # (la rangée de la planche à la hauteur h)
        skin = classes(f['rgb'])[0]
        if f['frontal']:                                                    # (de face : l'axe du visage, la peau entre ses yeux et son menton)
            sk = f['m'] & skin
            mids = [(np.where(sk[y])[0].min() + np.where(sk[y])[0].max() + 1) / 2 for y in range(int(f['top'] + 0.35 * f['hd']), int(f['chin'])) if sk[y].any()]
            f['ax'] = float(np.median(mids))
        else:                                                               # (de profil : le milieu du buste, sous les bras)
            xs = [np.where(f['m'][y])[0] for y in range(ya(1.75), ya(1.55))]
            f['ax'] = float(np.median([(x.min() + x.max() + 1) / 2 for x in xs if len(x)]))
    return F


def face(f):
    """le visage sans traits : ce qui, dans la peau du visage, n'en est pas (les yeux, les sourcils, la barbe, la bouche) repeint
    de la peau la plus proche ; les yeux notés (leurs centres, px de l'image) pour la porte"""
    rgb, m = f['rgb'], f['m']
    skin, navy, _ = classes(rgb)
    chin = int(round(f['chin'])) + 2
    hz = np.zeros_like(m); hz[:chin] = True
    sk = biggest(skin & m & hz & nd.binary_erosion(m, iterations=3))      # (la peau du visage : la plus grande pièce de peau sur le menton)
    zone = nd.binary_fill_holes(nd.binary_closing(sk, np.ones((7, 7)), iterations=2)) & m & hz
    R, B = rgb[..., 0], rgb[..., 2]
    beard = m & hz & ~skin & ~navy & (R - B > 18) & (rgb @ LUM < 150) & nd.binary_dilation(sk, iterations=4)   # (la barbe au bord du
    feat = (zone & ~skin) | beard                                                                            #  menton, hors du visage)
    L = rgb @ LUM
    lab, n = nd.label(feat & (L < 110), np.ones((3, 3)))
    eyes = []
    for i in range(n):
        c = lab == i + 1; k = int(c.sum())
        if k < 12: continue
        ys, xs = np.where(c)
        eyes.append(dict(y=float(ys.mean()), x=float(xs.mean()), n=k, w=int(xs.max() - xs.min() + 1), h=int(ys.max() - ys.min() + 1),
                         L=float(L[c].mean())))
    f['feat'] = eyes
    idx = nd.distance_transform_edt(~sk, return_distances=False, return_indices=True)
    rgb[feat] = rgb[idx[0][feat], idx[1][feat]]
    f['face'] = zone


def head(f):
    """la tête ramenée à HEAD_M de haut autour du cou (le milieu de la peau sous le menton), sans déformation : ce qui est sur
    le menton et n'est ni le samue ni le tablier, d'un seul tenant ; le corps dessous tel quel"""
    rgb, m = f['rgb'], f['m']
    skin, navy, beige = classes(rgb)
    chin = int(round(f['chin']))
    cand = m & ~navy & ~beige; cand[chin:] = False
    hb = biggest(cand)
    neck = m & skin; neck[:chin] = False; neck[chin + int(0.2 * f['head']):] = False
    xs = np.where(neck.any(0))[0]
    px = float(np.median([(np.where(neck[y])[0].min() + np.where(neck[y])[0].max() + 1) / 2 for y in range(chin, chin + int(0.2 * f['head'])) if neck[y].any()])) \
        if len(xs) else float(np.median(np.where(hb)[1]))
    sh = HEAD_M * f['ppm'] / f['head']                                      # (la tête : de f['head'] px à HEAD_M)
    body = m & ~hb
    H, W = m.shape
    yy, xx = np.mgrid[0:chin, 0:W]
    sy = np.floor(chin - (chin - (yy + 0.5)) / sh).astype(int); sx = np.floor(px + (xx + 0.5 - px) / sh).astype(int)
    ok = (sy >= 0) & (sx >= 0) & (sx < W)
    sy, sx = np.clip(sy, 0, H - 1), np.clip(sx, 0, W - 1)
    hm = ok & hb[sy, sx]
    nm = body.copy(); nm[:chin] |= hm
    nrgb = rgb.copy(); nrgb[:chin][hm] = rgb[sy[hm], sx[hm]]
    fz = np.zeros_like(m); fz[:chin][ok & f['face'][sy, sx] & hm] = True; fz[chin:] = f['face'][chin:]
    f['m'] = biggest(nm)
    f['rgb'] = nrgb
    f['face'] = fz & f['m']
    f['top'] = chin - (chin - f['top']) * sh
    f['hd'] = (chin - f['top'])
    f['sh'], f['px'] = sh, px
    for e in f['feat']:                                                     # (les traits notés, là où la tête les a mis)
        if e['y'] < chin: e['y'], e['x'] = chin - (chin - e['y']) * sh, px + (e['x'] - px) * sh


def boite(A, f, ox, oy, W, H):
    """A (pixels de la planche) à l'échelle f, son point (0, 0) en (ox, oy) de la sortie W x H : la part de chaque pixel"""
    h, w = A.shape
    S = np.zeros((h + 1, w + 1)); S[1:, 1:] = A.cumsum(0).cumsum(1)
    def integ(ys, xs):
        ys = np.clip(ys, 0, h); xs = np.clip(xs, 0, w)
        y0 = np.minimum(np.floor(ys).astype(int), h - 1); x0 = np.minimum(np.floor(xs).astype(int), w - 1)
        fy = ys - y0; fx = xs - x0
        return S[y0, x0] * (1 - fy) * (1 - fx) + S[y0 + 1, x0] * fy * (1 - fx) + S[y0, x0 + 1] * (1 - fy) * fx + S[y0 + 1, x0 + 1] * fy * fx
    gy = (np.arange(H + 1) - oy) / f; gx = (np.arange(W + 1) - ox) / f
    Y, X = np.meshgrid(gy, gx, indexing='ij'); Q = integ(Y, X)
    return np.clip((Q[1:, 1:] - Q[:-1, 1:] - Q[1:, :-1] + Q[:-1, :-1]) * f * f, 0, 1)


def cell(f, s):
    """l'image à s px par mètre : RGBA (alpha plein dès la moitié couverte), sa couleur prise sur son dedans ; son ancre (AX, AY) :
    le pixel de son axe sur le sol (le bas de ses semelles au bas de la rangée AY) ; ses yeux (px de la cellule)"""
    k = s / f['ppm']
    hh, ww = f['m'].shape
    l, r = -f['ax'] * k, (ww - f['ax']) * k
    AX = int(np.ceil(-l)) + 1; W = AX + int(np.ceil(r)) + 2
    AY = int(np.ceil(f['floor'] * k)) + 1; H = AY + 2
    ox = AX + 0.5 - f['ax'] * k; oy = AY + 1 - f['floor'] * k              # (le coin de l'image dans la cellule)
    cov = boite(f['m'].astype(float), k, ox, oy, W, H)
    a = cov >= 0.5
    inner = nd.binary_erosion(f['m'], iterations=2)
    rgb = np.zeros((H, W, 3)); fc = np.zeros((H, W), bool)
    for i, j in zip(*np.where(a)):
        ya, yb = (i - oy) / k, (i + 1 - oy) / k; xa, xb = (j - ox) / k, (j + 1 - ox) / k
        r0, r1 = max(0, int(np.floor(ya))), min(hh, int(np.ceil(yb))); c0, c1 = max(0, int(np.floor(xa))), min(ww, int(np.ceil(xb)))
        mm = inner[r0:r1, c0:c1]
        if mm.sum() < 3: mm = f['m'][r0:r1, c0:c1]
        px = f['rgb'][r0:r1, c0:c1][mm]
        if not len(px): continue
        med = np.median(px, 0); d = np.abs(px - med).sum(1)
        sel = px[d <= np.median(d)] if len(px) > 3 else px
        rgb[i, j] = sel.mean(0)
        fc[i, j] = f['face'][r0:r1, c0:c1].mean() >= 0.5
    eyes = [(e['x'] * k + ox, e['y'] * k + oy, e) for e in f['feat']]
    return np.concatenate([rgb, a[..., None] * 255.0], 2), AX, AY, fc, eyes


# ---- la lumière
LIGHT = (1.0, 0.86, 0.76)             # la lumière de la boutique sur lui : chaude
GAIN = 0.86
TOP_K = (1.06, 0.9)                   # (à la marmite : d'en haut, sa tête un peu plus claire que ses pieds)
COOL = (0.40, 0.44, 0.58)             # (à la porte : la nuit de la rue de son côté droit, plus sombre et bleue ; à gauche la boutique,
DOOR_K = 1.22                         #  dans son dos, plus forte qu'à la marmite : elle l'éclaire de près)
OUTLINE_DL = 6                        # (un pixel du bord tourné vers la lumière : jamais plus sombre de tant que celui qu'il couvre)


def light(c, place):
    """la lumière de sa place : à la marmite, la boutique d'en haut ; à la porte, la boutique à gauche et la rue à droite (t : la
    place du pixel de gauche à droite, à moitié dans sa rangée, à moitié dans toute l'image)"""
    a = c[..., 3] > 0
    H, W = a.shape
    ys, xs = np.where(a)
    if place == 'A':
        v = np.clip((np.arange(H) - ys.min()) / max(1, ys.max() - ys.min()), 0, 1)[:, None, None]
        k = np.array(LIGHT) * GAIN * (TOP_K[0] + (TOP_K[1] - TOP_K[0]) * v)
    else:
        tb = np.clip((np.arange(W) - xs.min()) / max(1, xs.max() - xs.min()), 0, 1)[None, :].repeat(H, 0)
        tr = np.zeros((H, W))
        for y in np.unique(ys):
            x = np.where(a[y])[0]
            tr[y] = np.clip((np.arange(W) - x.min()) / max(1, x.max() - x.min()), 0, 1)
        t = (0.5 * tb + 0.5 * tr)[..., None]
        k = np.array(LIGHT) * GAIN * DOOR_K * (1 - t) + np.array(COOL) * t
    out = c.copy()
    out[..., :3] = np.clip(c[..., :3] * k, 0, 255)
    return out


def no_outline(c, place):
    """pas de trait sombre continu au bord : un pixel du bord tourné vers la lumière (à la marmite : tout sauf le bas ; à la porte :
    la gauche et le haut, la boutique) prend la couleur de celui qu'il couvre s'il est plus sombre que lui de OUTLINE_DL"""
    a = c[..., 3] > 0
    L = c[..., :3] @ LUM
    P = np.pad(a, 1)
    out = c.copy()
    lit = (lambda nx, ny: ny <= 0) if place == 'A' else (lambda nx, ny: -0.8 * nx - 0.6 * ny > 0.05)
    for y, x in zip(*np.where(a)):
        nx = int(not P[y + 1, x]) - int(not P[y + 1, x + 2]); ny = int(not P[y, x + 1]) - int(not P[y + 2, x + 1])
        nx, ny = -nx, -ny                                                   # (vers le dehors)
        if (nx, ny) == (0, 0) or not lit(nx, ny): continue
        if abs(nx) >= abs(ny): iy, ix = y, x - nx
        else: iy, ix = y - ny, x
        if not (0 <= iy < a.shape[0] and 0 <= ix < a.shape[1] and a[iy, ix]): continue
        if L[y, x] < L[iy, ix] - OUTLINE_DL: out[y, x, :3] = c[iy, ix, :3]
    return out


# ---- ses places dans la maquette (tools/oden_interior.py) : à la marmite (derrière le comptoir, vu par la fenêtre), à la porte
Z_D = 38.2                            # à la porte : la profondeur du milieu du vantail de droite (36,7 px par mètre)
X_LEAF = -(O.X_F + O.KUMI['d'])       # (le dedans du vantail fermé : sa main y est, GRAB, son bras tendu)
PULL = 0.25                           # (sa poignée : à tant du bord du vantail qui touche le cadre, le côté qui reste à portée ouvert)
X_LOOK = -6.95                        # (dans l'embrasure, sur le seuil : il y regarde la pluie)
D_IN = 1.13                           # (il vient de tant derrière, hors de vue)
GRAB = (1.15, 1.55)                   # (son poing : le plus avancé de lui entre ces hauteurs, sur « grab »)
X_A = -9.69                           # (à la marmite : il vient de là, de la cuisine)
WALK = (1.0, 0.17)                    # (sa marche : m/s, s par image)
WK = ('w1', 'w2', 'w3', 'w4', 'w5', 'w6')
USE = {'A': ('idle', 'nod', 'happy', 'laugh', 'pick', 'lift', 'ladle', 'serve', 'offer', 'wipe', 'wipe2', 'stand') + WK,
       'D': ('stand', 'stand2', 'grab') + WK}
MIRROR = {'D': ('stand',) + WK}       # (à la porte, son retour : ces images retournées avant la lumière)
FAMILIES = 16
P95 = {'A': 128 * 1.15, 'D': 116 * 1.15}   # (la peinture voisine : le verre de la fenêtre allumé, la porte et sa façade ; son p95 + 15 %)


def eyes_of(name, f, eyes):
    """les yeux parmi les traits notés : de profil, le plus avancé des petits traits sombres (le sourcil au-dessus de lui, l'oreille
    plus grande) ; de trois quarts, les deux petits qui n'ont pas un trait juste dessous (les sourcils)"""
    small = [(x, y, e) for x, y, e in eyes if 15 <= e['n'] <= 50 and e['h'] <= 8 and e['L'] < 80]
    small = [(x, y, e) for x, y, e in small if not any(0 < e2['y'] - e['y'] < 14 and abs(e2['x'] - e['x']) < 12 for _, _, e2 in small)]
    if not small: return []
    if name == 'stand2': return small[:2]
    return [max(small, key=lambda t: t[2]['x'])]


def build(F):
    """chaque image à chacune de ses places, à sa lumière, son bord ; RGBA, ancre, ses yeux (px de la cellule)"""
    cells = {}
    for p, Z in (('A', O.Z_M), ('D', Z_D)):
        s = O.F / Z
        for n in USE[p] + tuple(k + '_m' for k in MIRROR.get(p, ())):
            base = n[:-2] if n.endswith('_m') else n
            c, ax, ay, fc, ey = cell(F[base], s)
            c = no_specks(c)
            ey = eyes_of(base, F[base], ey)
            if n.endswith('_m'):
                c = c[:, ::-1].copy(); fc = fc[:, ::-1]; ax = c.shape[1] - 1 - ax; ey = [(c.shape[1] - x, y, e) for x, y, e in ey]
            c = no_outline(light(c, p), p)
            a = c[..., 3] > 0
            ys, xs = np.where(a)
            y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1      # (serrée sur lui)
            hd = F[base]['hd'] * s / F[base]['ppm']
            c, fc = c[y0:y1, x0:x1], fc[y0:y1, x0:x1]
            ey = [inward(int(np.floor(x)) - x0, int(np.floor(y)) - y0, fc) for x, y, e in ey] if FACE_PX[0] <= hd + 0.5 else []
            cells[(p, n)] = dict(c=c, ax=ax - x0, ay=ay - y0, eyes=ey, face=fc, hd=hd)
    hc = lambda k: (lambda xs: (xs.min() + xs.max() + 1) / 2)(np.where((k['c'][:int(round(k['hd'])), :, 3] > 0).any(0))[0])
    S, L = cells[('D', 'stand')], cells[('D', 'stand2')]                     # (appuyé au cadre : sa tête là où elle était debout, son
    L['ax'] = int(round(hc(L) - (hc(S) - S['ax'])))                         #  bras sur le mur, derrière le cadre)
    return cells


def no_specks(c):
    """les traits de la planche plus petits qu'un pixel de la rue (les doigts d'un poing, un pli de la main) : une tache sombre de six
    pixels au plus que la peau entoure (le bord de la main mis à part) prend la couleur de cette peau (à cette taille ce serait un
    trou)"""
    a = c[..., 3] > 0
    skin = classes(c[..., :3])[0] & a
    L = c[..., :3] @ LUM
    out = c.copy()
    lab, n = nd.label(a & ~skin)
    cross = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], bool)
    for i in range(1, n + 1):
        m = lab == i
        if m.sum() > 6: continue
        ring = nd.binary_dilation(m, cross) & ~m & a
        if ring.sum() < m.sum() + 3 or not skin[ring].all() or L[m].mean() > L[ring].mean() - 30: continue
        out[m, :3] = c[ring, :3].mean(0)
    return out


def inward(x, y, fc):
    """un œil sur le bord du visage (le nez de profil) : un pixel vers le dedans"""
    H, W = fc.shape
    if not (0 <= y < H and 0 <= x < W): return (x, y)
    for d in (1, -1):
        if not (0 <= x + d < W and fc[y, x + d]) and 0 <= x - d < W and fc[y, x - d]: return (x - d, y)
    return (x, y)


class Atlas:
    """les cases, rangées en étagères ; leur boîte [sx, sy, w, h]"""
    def __init__(self, width):
        self.W, self.x, self.y, self.rowh, self.cells = width, 0, 0, 0, []

    def add(self, m):
        h, w = m.shape[:2]
        if self.x + w > self.W: self.x, self.y, self.rowh = 0, self.y + self.rowh + 1, 0
        self.cells.append((self.x, self.y, m)); box = [self.x, self.y, w, h]
        self.x += w + 1; self.rowh = max(self.rowh, h)
        return box

    def image(self):
        a = np.zeros((self.y + self.rowh, self.W, 4), np.uint8)
        for x, y, m in self.cells: a[y:y + m.shape[0], x:x + m.shape[1]] = np.clip(np.round(m), 0, 255)
        return a


def grain(img, C, boxes):
    """le grain de la peinture (tools/regrain.py), place par place, toutes ses images ensemble : ses familles, chaque pixel à la
    sienne, le grain fin baké ancré à ses pieds, ses clairs sous P95 ; puis ses yeux (un pixel sombre : la famille la plus sombre
    de ses cheveux)"""
    infos = {}
    for p in ('A', 'D'):
        items = []
        for (q, n), b in boxes.items():
            if q != p: continue
            k = C[(q, n)]
            base = n[:-2] if n.endswith('_m') else n
            seq = (('wk_m' if n.endswith('_m') else 'wk') + p, WK.index(base)) if base in WK else (n, 0)   # (la marche : chaque image après la précédente)
            items.append(dict(a=img, box=tuple(b[:4]), anchor=(k['ax'], k['ay']), seq=seq))
        P = dict(RG.DEF); P.update(families=FAMILIES, p95=round(P95[p], 1))
        infos[p] = RG.regrain_group(items, P, 'oden ' + p)
        base = np.array(infos[p]['base'], float)
        dark = [b for b in base if abs(b[2] - b[0]) < 0.25 * b.max() + 4] or list(base)
        eye = np.array(dark[0])
        for (q, n), b in boxes.items():
            if q != p: continue
            for ex, ey in C[(q, n)]['eyes']:
                fc = C[(q, n)]['face']
                if 0 <= ey < fc.shape[0] and 0 <= ex < fc.shape[1] and fc[ey, ex]:
                    img[b[1] + ey, b[0] + ex, :3] = eye
    return infos


def main():
    prev = sys.argv[sys.argv.index('--preview') + 1] if '--preview' in sys.argv else None
    F = clean(frames())
    C = build(F)
    A = Atlas(256)
    OMF = {'A': {}, 'D': {}}
    boxes = {}
    for (p, n), k in sorted(C.items(), key=lambda t: (t[0][0], -t[1]['c'].shape[0], t[0][1])):
        boxes[(p, n)] = A.add(k['c'])
        OMF[p][n] = boxes[(p, n)] + [int(k['ax']), int(k['ay'])]
    img = A.image()
    infos = grain(img, C, boxes)
    Xp = O.pot_at()[0]
    sA, sD = O.F / O.Z_M, O.F / Z_D
    px = lambda X, Z: round(O.VX + O.F * X / Z, 2)
    g = F['grab']                                                         # (son poing sur la poignée : « grab » à sa longueur de bras
    rows = slice(int(round(g['floor'] - GRAB[1] * g['ppm'])), int(round(g['floor'] - GRAB[0] * g['ppm'])))   # derrière, à la
    reach = (np.where(g['m'][rows].any(0))[0].max() + 1 - g['ax']) / g['ppm']                                 # profondeur de la poignée)
    X_G, Z_G = X_LEAF - reach, O.zf(O.DOOR[1][1] + 1) - PULL
    OMF['A'].update({'z': round(O.Z_M, 2), 'floor': round(O.VY + O.EYE * sA, 2), 'from': px(X_A, O.Z_M), 'at': px(Xp, O.Z_M), 'v': round(WALK[0] * sA, 2)})
    OMF['D'].update({'z': Z_D, 'floor': round(O.VY + O.EYE * sD, 2), 'from': px(X_G - D_IN, Z_G), 'at': px(X_G, Z_G), 'look': px(X_LOOK, Z_D),
                     'v': round(WALK[0] * sD, 2)})
    OMF['step'] = WALK[1]; OMF['walk'] = list(WK)
    print('le maître, %.2f m de maquette (%.2f m, %.1f têtes) : à la marmite Z %.2f (%.1f px/m, %.1f px, sa tête %.1f px, ses pieds à la rangée %.1f, '
          'de x %.1f à %.1f) ; à la porte Z %.2f (%.1f px/m, %.1f px, sa tête %.1f px ; de x %.1f, son poing sur la poignée de x %.1f, dans '
          'l\'embrasure à %.1f) ; %d images, atlas %d x %d ; %s' % (
              H_TOP, H_REAL, HEADS, O.Z_M, sA, H_TOP * sA, HEAD_M * sA, OMF['A']['floor'], OMF['A']['from'], OMF['A']['at'], Z_D, sD, H_TOP * sD,
              HEAD_M * sD, OMF['D']['from'], OMF['D']['at'], OMF['D']['look'], len(C), img.shape[1], img.shape[0],
              ' ; '.join('%s %d familles (pente %.2f)' % (p, i['families'], i['slope']) for p, i in infos.items())))
    if prev:
        bg = np.zeros(img.shape[:2] + (3,), float); bg[...] = (60, 90, 60)
        al = img[..., 3:] / 255.0; bg = bg * (1 - al) + img[..., :3] * al
        Image.fromarray(bg.astype(np.uint8)).resize((img.shape[1] * 4, img.shape[0] * 4), Image.NEAREST).save(os.path.join(prev, 'master_atlas_x4.png'))
        json.dump(OMF, open(os.path.join(prev, 'omf.json'), 'w'))
        Image.fromarray(img, 'RGBA').save(os.path.join(prev, 'oden_master.png'))
        return
    Image.fromarray(img, 'RGBA').save(I.A(OUT), 'WEBP', lossless=True, quality=100, method=6, exact=True)
    js = open(JS, encoding='utf-8').read()
    line = 'const OMF = ' + json.dumps(OMF, separators=(',', ':')) + ';'
    js2, n = re.subn(r'const OMF = \{.*?\};', lambda m: line, js, count=1)
    assert n == 1, 'la ligne OMF manque dans assets/street.js'
    if js2 != js: open(JS, 'w', encoding='utf-8').write(js2)


if __name__ == '__main__':
    main()
