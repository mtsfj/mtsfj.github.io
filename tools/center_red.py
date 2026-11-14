#!/usr/bin/env python3
"""Le Centre Pokémon : Red, le dresseur des premiers jeux, Pikachu sur l'épaule, assis sur le bord du toit du Centre, à son
angle au-dessus de la ruelle, comme Kirua sur son toit : face à nous, les jambes pendant dans la ruelle, devant le mur de
côté du Centre (le mur du fond de la ruelle, vu de face).

    python3 tools/center_red.py                    (écrit assets/center_red.webp et, dans assets/street.js, la ligne CRD :
                                                    on peut le relancer, il écrit la même chose)
    python3 tools/center_red.py --preview dossier  (des aperçus seulement : l'atlas x6 sur le mur, CRD en json)

La planche (tools/src/center_red_sheet.webp, un brouillon fait pour lui d'après la planche de Red du propriétaire,
tools/src/red_sheet.webp, pour le dessin ; la rue autour de sa place et Kirua sur son toit pour le style : peint, modelé
doux, tramé, les couleurs éteintes de la nuit, les proportions vraies, sans contour ; sur fond blanc) : assis sur un rebord
qu'on ne voit pas,
face à nous, les cuisses sur le rebord, les jambes pendantes, Pikachu sur l'épaule : au repos les mains posées sur le
rebord, la Poké Ball à la main, la main levée qui la lance (et qui salue), le poing levé ; endormi, la tête basse, Pikachu endormi contre son cou ; qui se réveille en se frottant l'œil. Chaque image
découpée (tools/ichiraku_figures.py : cut, son fond blanc ôté, son plus grand morceau), réduite d'une seule échelle (warp,
pick : chaque pixel de la scène sur 8 x 8 points de la planche, plein dès la moitié couverte, ses traits sombres s'ils en
couvrent assez), posée par son assise ; ses jambes qui balancent (swing, swing2 : ses tibias d'un pixel en avant, en
arrière ; la planche les lançait loin à droite, derrière l'angle de B) : le rebord, la rangée où ses mains se posent sur la planche (LEDGE), au milieu de
son corps.

Sa taille : celle de sa place. Le mur du fond de la ruelle (tools/roji_alley.py : le côté du Centre, de face, à 23,08 m :
41,6 px le mètre, son toit à la rangée 441, son angle à la colonne 908, l'angle de l'immeuble B, plus près, à 941) : assis,
le haut de sa casquette 0,88 m au-dessus du rebord (SEAT_H : 37 px), ses jambes pendant de 0,53 m sous lui. Son assise sur
le chaperon du mur (SEAT : sa colonne, la rangée du toit) ; ce qui passe à droite de l'angle de B est derrière lui (la rue
le coupe là).

Pas de contour (le propriétaire : « pas de contour au perso », « trop pixel de jeu ») : la planche, peinte, n'en a pas ;
son bord se lit par sa valeur contre ce qui est derrière lui, et par la lumière qui le touche (RIM_SKY d'en haut, RIM_SIGN
du côté de l'enseigne). Sa lumière : deux calques. La nuit seule (AMB : le ciel de nuit et la rue, froide), avec son ombre : sur le chaperon sous
lui et, douce, sur le mur sous ses jambes (la lumière vient de l'enseigne, à sa gauche et en dessous : l'ombre un peu à
droite, SHADOW) ; et la lumière de l'enseigne Poké Ball (SIGN : son rouge et son blanc, plus forte du côté de l'enseigne,
SIDE, et par en dessous), que la rue pose sur le premier au niveau de l'enseigne et du courant de sa zone. Chaque calque en
ses familles de tons (FAMILIES), gardées dans la clarté de la peinture, pas de trait sombre au bord, peu de pixels seuls,
un grain fin en carreau. Il faut Pillow, numpy (et ce qu'il faut à tools/ichiraku_figures.py).
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
SHEET = os.path.join(ICI, 'src', 'center_red_sheet.webp')
OUT = os.path.join(ROOT, 'assets', 'center_red.webp')
JS = os.path.join(ROOT, 'assets', 'street.js')
PPM = 960.0 / (960.0 * 5.0 / (908 - 700))     # (le mur du fond de la ruelle, à 23,08 m : 41,6 px le mètre)
SEAT_H = 0.88                                 # (assis : le haut de sa casquette au-dessus du rebord, m)
SEAT = (921, 441)                             # son assise : le milieu de son corps, la rangée du toit du Centre à son angle
LEDGE = (288, 710, 1128)                            # (le rebord dans la planche : la rangée où ses mains se posent, une par rangée d'images)
# les images de la planche : leur boîte (x0, y0, x1, y1), leur rangée
FRAMES = {'idle': ((80, 28, 360, 436), 0), 'ball': ((476, 28, 750, 438), 0), 'toss': ((86, 440, 380, 858), 1),
          'cheer': ((462, 434, 755, 860), 1), 'doze': ((128, 870, 378, 1272), 2), 'wake': ((444, 856, 735, 1272), 2)}
SWING = 4                                     # (ses jambes qui balancent : sous le rebord, à tant de rangées, ses tibias d'un pixel d'un côté, de l'autre)
AMB = (0.46, 0.45, 0.60)                      # le ciel de nuit et la rue sur lui (froids)
# « plus sombre, comme ce qui l'entoure » (le propriétaire) : autour de lui à 22 h (le chaperon, les bandes, le mur de côté,
# le cerisier) la clarté L* fait 24 à 43 en moyenne, 33 à 61 au plus clair, la saturation C* 22 à 36 : ses couleurs dans
# cette plage (VALUES : au-dessus du premier seuil, ramenées sous le second ; la nuit, et l'enseigne), éteintes (CHROMA)
VALUES = {'night': (26.0, 44.0), 'lit': (30.0, 54.0)}
CHROMA = 1.0                                  # (la planche, peinte, a déjà les couleurs éteintes de la nuit)
SIGN = (0.56, 0.34, 0.40)                     # la lumière de l'enseigne Poké Ball (son rouge et son blanc), en plus
SIDE = (1.0, 0.25)                            # (de son côté gauche, celui de l'enseigne, à son côté droit : de tant à tant)
BELOW = (0.7, 1.15)                           # (et d'en bas : de sa casquette à ses semelles, de tant à tant)
SHADOW = ((3, 1), 0.42, (0.5, 0.18))          # son ombre sur le mur sous lui : décalée de tant (px), sa force sur le chaperon, sur le mur (du haut au bas)
RIM_SKY = ((118, 126, 186), 0.18)             # (le bord tourné vers le ciel : sa couleur, sa part)
RIM_SIGN = ((214, 150, 172), 0.22)            # (le bord tourné vers l'enseigne : son rouge et son blanc, sa part)
FAMILIES = 22
GRAIN, GRAIN_T = 2, 8                         # (le grain : plus ou moins tant de niveaux, un carreau de tant de pixels)
LIGHT = (-0.8, 0.3)                           # (la lumière dans l'image : de l'enseigne, à gauche, un peu d'en bas)


def values(P, v):
    """des couleurs gardées dans la clarté de ce qui l'entoure (v : au-dessus du premier seuil, la clarté ramenée sous le
    second, en proportion)"""
    lab_ = R.lab(P); L = lab_[:, 0]; top = max(L.max(), v[1] + 1e-6)
    lab_[:, 0] = np.where(L > v[0], v[0] + (L - v[0]) * (v[1] - v[0]) / (top - v[0]), L)
    return FG.lab2rgb(lab_)


def frames():
    """chaque image à l'échelle de sa place : ses couleurs, son plein, sa tête ; (ox, oy) : son assise (le milieu de son corps
    sur le rebord)"""
    sheet = {'red': np.asarray(Image.open(SHEET).convert('RGB')).astype(float)}
    Q1, a1, _ = FG.cut(sheet, 'red', FRAMES['idle'][0], 'free', {})   # (sa hauteur seulement)
    top1 = FRAMES['idle'][0][1] + np.nonzero((a1 > 0.5).any(1))[0][0]
    s = SEAT_H * PPM / (LEDGE[0] - top1)                                 # (px de la scène par px de planche : la même pour toutes)
    out = {}
    for n, (box, rw) in FRAMES.items():
        Q, a, _ = FG.cut(sheet, 'red', box, 'free', {})                  # (la planche, peinte, n'a pas de contour)
        m = a > 0.5; ys = np.nonzero(m.any(1))[0]; top, bot = ys[0], ys[-1] + 1
        ledge = LEDGE[rw] - box[1]
        band = m[max(top, ledge - 40):ledge]; cols = np.nonzero(band.sum(0) >= 0.5 * band.shape[0])[0]   # (son corps à hauteur du rebord)
        xn = (cols[0] + cols[-1] + 1) / 2 if len(cols) else m.shape[1] / 2
        hx = np.nonzero(m[top:top + 30].any(0))[0]
        g = dict(crown=top, neck=top + 0.24 * (ledge - top), hx=(hx[0] + hx[-1] + 1) / 2, hw=hx[-1] - hx[0] + 1, xn=xn)
        K = [(top, -s * (ledge - top)), (ledge, 0.0)]
        C, A, T, Lc, hd = FG.warp(Q, a, K, s, s, s, g, 0.0)
        rgb, mm = FG.pick(C, A); hd &= mm
        yy, xx = np.nonzero(mm); t, b_, l, r_ = yy.min(), yy.max() + 1, xx.min(), xx.max() + 1
        out[n] = dict(rgb=rgb[t:b_, l:r_], m=mm[t:b_, l:r_], hd=hd[t:b_, l:r_],
                      hy=(-s * (ledge - top) - T - t, -s * (ledge - g['neck']) - T - t), ox=-(Lc + l), oy=-(T + t))
    return out, s


def layers(raw):
    """les deux calques de chaque image : la nuit (avec son ombre sur le chaperon et sur le mur), et avec l'enseigne ; chacun
    en ses familles, gardées dans la clarté de la peinture, pas de trait sombre au bord (du côté de la lumière), peu de pixels
    seuls, le grain"""
    base = {n: np.clip(c['rgb'], 0, 255) for n, c in raw.items()}
    def lit(n, sign):
        c = raw[n]; m = c['m']; h, w = m.shape
        xs = np.nonzero(m.any(0))[0]; u = np.clip((np.arange(w) - xs[0]) / max(1, xs[-1] - xs[0]), 0, 1)
        ys = np.nonzero(m.any(1))[0]; v = np.clip((np.arange(h) - ys[0]) / max(1, ys[-1] - ys[0]), 0, 1)
        side = SIDE[0] + (SIDE[1] - SIDE[0]) * u; below = BELOW[0] + (BELOW[1] - BELOW[0]) * v
        k = np.array(AMB)[None, None] * (1.08 - 0.16 * v)[:, None, None] + sign * (side[None, :] * below[:, None])[..., None] * np.array(SIGN)[None, None]
        return base[n] * k
    out = {n: dict(c) for n, c in raw.items()}
    for li, sign in (('night', 0.0), ('lit', 1.0)):
        cols = {n: lit(n, sign) for n in raw}
        for n in raw:                             # (son bord : la lumière qui le touche, pas un trait ; le ciel d'en haut, l'enseigne de gauche)
            cols[n] = FG.rim(cols[n], raw[n]['m'], (0.0, -1.0), RIM_SKY[0], RIM_SKY[1])
            if sign: cols[n] = FG.rim(cols[n], raw[n]['m'], (-1.0, 0.25), RIM_SIGN[0], RIM_SIGN[1], cos=0.6)
        cols = {n: FG.mute(cols[n], CHROMA) for n in raw}
        allc = np.concatenate([cols[n][raw[n]['m']] for n in raw])
        fam = FG.palette(np.clip(allc, 0, 255), FAMILIES); Lf = R.lab(fam)[:, 0]; famB = values(fam, VALUES[li])
        tile = np.random.default_rng(31 if sign else 13).integers(-GRAIN, GRAIN + 1, (GRAIN_T, GRAIN_T))
        for n, c in raw.items():
            m = c['m']; h, w = m.shape
            idx = np.where(m, R.nearest(np.clip(cols[n].reshape(-1, 3), 0, 255), fam).reshape(m.shape), -1)
            idx = FG.no_outline(idx, m, Lf, LIGHT)
            idx, keep = FG.face_detail(idx, m, c['hd'], c['hy'], fam)
            idx = FG.unspeckle(idx, m, keep)
            gr = np.tile(tile, (h // GRAIN_T + 1, w // GRAIN_T + 1))[:h, :w]
            rgba = np.zeros((h, w, 4)); rgba[..., 3] = m * 255
            rgba[..., :3] = np.clip(np.round(famB[np.maximum(idx, 0)] + gr[..., None]), 0, 255) * m[..., None]
            out[n][li] = rgba
    for n, c in out.items():                      # (son ombre, dans le calque de la nuit : la case agrandie à droite et en bas)
        (dx, dy), k0, (k1, k2) = SHADOW; m = c['m']; h, w = m.shape; oy = int(c['oy'])
        H2, W2 = h + dy + 1, w + dx + 1
        sh = np.zeros((H2, W2)); ys, xs = np.nonzero(m)
        below = ys >= oy                                                  # (ce qui est sous le rebord : ses jambes, sur le mur)
        sh[ys[below] + dy, xs[below] + dx] = 1
        sh = np.maximum(sh, np.roll(sh, 1, 1) * 0.6)                      # (douce : un pixel de plus à droite, plus clair)
        rows = np.arange(H2)[:, None]; fall = k1 + (k2 - k1) * np.clip((rows - oy) / max(1, H2 - oy), 0, 1)
        alpha = sh * fall
        on = np.zeros((H2, W2), bool); on[:h, :w] = m
        night = np.zeros((H2, W2, 4)); night[:h, :w] = c['night']
        shade = (alpha > 0) & ~on
        night[shade, 3] = np.round(255 * alpha[shade])
        if 0 < oy <= H2:                                                  # (sur le chaperon, sous lui : une rangée sombre d'un bout à l'autre)
            xs_ = np.nonzero(m[min(h - 1, oy - 1)])[0]
            if len(xs_):
                row = oy; lo, hi = max(0, xs_[0] - 1), min(W2, xs_[-1] + 2)
                ok = ~on[row, lo:hi]; night[row, lo:hi][ok, 3] = np.maximum(night[row, lo:hi][ok, 3], round(255 * k0))
        lit_ = np.zeros((H2, W2, 4)); lit_[:h, :w] = c['lit']
        c['night'], c['lit'], c['m'] = night, lit_, on
    return out


def swing(c, d):
    """ses jambes qui balancent : sous le rebord (SWING rangées plus bas), ses tibias d'un pixel de côté"""
    o = dict(c); y0 = int(c['oy']) + SWING
    for li in ('night', 'lit'):
        im = c[li].copy(); low = im[y0:].copy(); im[y0:] = 0
        if d > 0: im[y0:, 1:] = low[:, :-1]
        else: im[y0:, :-1] = low[:, 1:]
        o[li] = im
    m = c['m'].copy(); low = m[y0:].copy(); m[y0:] = False
    if d > 0: m[y0:, 1:] = low[:, :-1]
    else: m[y0:, :-1] = low[:, 1:]
    o['m'] = m
    return o


def breathe(c):
    """au repos, le souffle : le haut du corps (au-dessus de sa taille, un tiers de la hauteur au-dessus du rebord) d'un pixel
    plus haut"""
    o = dict(c); h = c['m'].shape[0]; wst = int(c['oy'] - 0.33 * c['oy'])
    for li in ('night', 'lit'):
        im = c[li]; new = np.zeros((h + 1,) + im.shape[1:]); new[:wst + 1] = im[:wst + 1]; new[wst + 1:] = im[wst:]
        o[li] = new
    o['oy'] = c['oy'] + 1; o['m'] = np.r_[c['m'][:wst + 1], c['m'][wst:]]
    return o


def points(c, n):
    """ce que la rue y pose (en pixels de la scène, depuis son assise) : la main qui lance la balle (toss : la peau la plus
    haute à droite de sa tête), la tête de Pikachu (ses étincelles), le haut de sa tête (son étoile)"""
    m = c['lit'][..., 3] > 0; h, w = m.shape; im = np.zeros((h, w, 3)); hh, ww = c['rgb'].shape[:2]; im[:hh, :ww] = c['rgb']
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    ox, oy = int(c['ox']), int(c['oy']); ys, xs = np.nonzero(m)
    near = m[:, max(0, ox - 6):ox + 7]; top = int(np.nonzero(near.any(1))[0][0])   # (le haut de sa casquette, au-dessus de son milieu)
    P = {'head': [int(np.median(np.nonzero(near[top])[0])) + max(0, ox - 6) - ox, top - oy]}
    skin = m & (r > g + 15) & (g > b) & (r > 90) & (g > 0.5 * r)
    if n == 'toss':                              # (sa main levée, à gauche de sa tête : la peau la plus haute)
        sy, sx = np.nonzero(skin[:, :max(1, ox - 4)]); i = np.argmin(sy); P['hand'] = [int(sx[i]) - ox, int(sy[i]) - oy - 2]
    yellow = m & (r > 120) & (g > 0.7 * r) & (b < 0.6 * g)
    lab_, k = FG.label(yellow)
    if k:
        sz = np.bincount(lab_.ravel()); sz[0] = 0; yy, xx = np.nonzero(lab_ == sz.argmax()); top = yy <= np.percentile(yy, 40)
        P['pika'] = [int(np.median(xx[top])) - ox, int(np.median(yy[top])) - oy]
    return P


def main():
    prev = sys.argv[sys.argv.index('--preview') + 1] if '--preview' in sys.argv else None
    raw, s = frames(); col = layers(raw)
    col['idle_b'] = breathe(col['idle']); col['swing'] = swing(col['idle'], 1); col['swing2'] = swing(col['idle'], -1)
    order = ['idle', 'idle_b', 'swing', 'swing2', 'ball', 'toss', 'cheer', 'doze', 'wake']
    U = FG.Atlas(256); boxes = {}
    for n in order:
        c = col[n]; box = U.add(np.round(c['night']).astype(np.uint8), np.round(c['lit']).astype(np.uint8))
        boxes[n] = box + [int(c['ox']), int(c['oy'])]
    img, dy = U.image()
    pts = {n: points(col[n], n) for n in order}
    CRD = {'cells': boxes, 'lit': dy, 'x': SEAT[0], 'y': SEAT[1], 'clip': 941, 'pts': pts}
    print('Red : %.3f px de la scène par px de planche (%.1f px le mètre), %d px de haut assis (assise à %d, %d) | %d cases, atlas %d x %d' % (
        s, PPM, boxes['idle'][3], SEAT[0], SEAT[1], len(boxes), img.shape[1], img.shape[0]))
    if prev:
        os.makedirs(prev, exist_ok=True)
        bg = np.full(img.shape[:2] + (3,), (24, 24, 47), float); al = img[..., 3:] / 255
        Image.fromarray((bg * (1 - al) + img[..., :3] * al).astype(np.uint8)).resize((img.shape[1] * 6, img.shape[0] * 6), Image.NEAREST).save(os.path.join(prev, 'atlas_x6.png'))
        json.dump(CRD, open(os.path.join(prev, 'crd.json'), 'w'))
        return CRD, img
    Image.fromarray(img, 'RGBA').save(OUT, 'WEBP', lossless=True, quality=100, method=6, exact=True)
    js = open(JS, encoding='utf-8').read()
    line = 'const CRD = ' + json.dumps(CRD, separators=(',', ':')) + ';'
    js2, n = re.subn(r'const CRD = \{.*?\};', lambda m: line, js, count=1)
    if n and js2 != js: open(JS, 'w', encoding='utf-8').write(js2)
    print('wrote', OUT, '| street.js CRD', 'updated' if n else 'NOT FOUND')


if __name__ == '__main__':
    main()
