#!/usr/bin/env python3
"""L'oden : son maître, découpé de la planche du propriétaire, à sa profondeur dans la maquette de tools/oden_interior.py.

    python3 tools/oden_master.py                  (après tools/oden_interior.py ; réécrit assets/oden_master.webp et, dans
                                                    assets/street.js, la ligne OMF : on peut le relancer, il écrit la même chose)
    python3 tools/oden_master.py --preview dossier (des aperçus seulement)

La planche (tools/src/oden_master_sheet_b.webp, la variante ronde du propriétaire), sur fond blanc : de face derrière un
comptoir (au repos, la tête qui penche, les yeux fermés, le rire), au travail de face (les baguettes dans la marmite, le
daikon levé, la louche de bouillon, l'assiette servie, l'assiette tendue), l'essuyage du comptoir (deux images), la porte
coulissante de profil (la main sur sa poignée ; la seconde, la rue la nuit derrière lui, n'est pas prise : son fond touche
son samue), la marche de profil vers la droite (debout, quatre pas, debout). C'est elle et non la première planche : la
porte de l'oden est vue de biais (la façade à 11° du regard), un homme dans son embrasure y est de profil, et elle seule le
dessine de profil à la porte et debout de profil (la première le met de face dans l'embrasure, coupé aux genoux) ; à sa taille
dans la rue (une tête de 10 à 15 px) sa grande serviette blanche se lit, le bandeau fin de l'autre se perd dans la lumière
orange de la boutique. Ses proportions sont celles de la première (4,3 têtes de haut contre 4,1), plus large seulement.

Chaque image : sa couverture (ce qui s'écarte du blanc, ses trous bouchés, rien de détaché d'elle : ni les traits du rire,
ni la vapeur dessinée), sans ses accessoires (le comptoir, la marmite, les bols : tout ce qui est sous CUT de haut, plus bas
que le verre de la boutique ; la porte de la planche, sauf la main sur sa poignée) ; ce qu'il tient gardé (les baguettes, la
louche). Une seule échelle : debout, du haut de la serviette aux semelles, H_TOP = 1,70 m ; les rangées dessinées plus
grandes ramenées à la même tête (HEAD : leur tête mesurée contre celle de la marche) ; un seul sol, sous ses semelles (celui
des images de face : H_TOP sous le haut de la serviette). À la porte, la main sur la poignée, ses jambes sont celles de
l'image debout (la planche le coupe au tablier).

Réduction à la taille de chaque place (F / Z px par mètre) : chaque pixel prend la part de la planche qu'il couvre (une boîte
exacte), plein dès la moitié couverte (ni halo ni bord flou) ; sa couleur, la moyenne des pixels de la planche les plus
proches de leur médiane (un bord ne mêle pas deux matières) ; puis la lumière de la boutique (LIGHT : chaude, un peu dans son
dos ; à la porte plus sombre vers l'avant et un peu violette, DOOR_LIGHT, DOOR_TINT : la boutique dans son dos, la rue devant
lui) et une palette commune à toutes ses images (PAL couleurs : ni grain ni scintillement d'une image à l'autre).

Ses places (tools/oden_interior.py) : à la marmite, derrière le comptoir dans son allée (Z_M), de face, vu par la fenêtre
(au-dessus de son appui on voit sa serviette, ses yeux) ; il y vient de la cuisine (à gauche, au fond) de profil, par
derrière la porte et le trumeau ; à la porte, dans l'embrasure du vantail de droite (Z_D, sur le seuil), de profil vers la
rue : il y vient de l'intérieur, de profil, le vantail fermé devant lui, l'ouvre, regarde la pluie, le referme. Ses pieds ne
se voient jamais quand il marche (derrière le comptoir, derrière le bas de bois des vantaux) ; seulement debout, dans
l'embrasure ouverte. Sa marche : WALK (1 m/s, une image de pas toutes les 0,17 s). Tout va dans
assets/oden_master.webp (rangé en étagères) ; assets/street.js lit la ligne OMF : chaque image, son ancre (le pied de son axe
sur le sol), ses places en px de la rue, son pas. Il faut Pillow, numpy, scipy.
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

ROOT = O.ROOT
SHEET = os.path.join(ROOT, 'tools', 'src', 'oden_master_sheet_b.webp')
JS = os.path.join(ROOT, 'assets', 'street.js')
OUT = 'oden_master.webp'
F, VX, VY, EYE = O.F, O.VX, O.VY, O.EYE
H_TOP = 1.70                          # debout, du haut de sa serviette aux semelles (m)
ROWS = ((0, 240), (245, 520), (525, 775), (778, 1024))   # les quatre rangées de la planche (y)
HEAD = (92 / 50, 92 / 50, 87.5 / 50, 1.0)   # (sa tête, du haut de la serviette au menton, rangée par rangée contre la marche : 92,
                                      # 92, 87,5 et 50 px)
NAMES = (('idle', 'nod', 'happy', 'laugh'), ('pick', 'lift', 'ladle', 'serve', 'offer'), ('wipe', 'wipe2', 'grab', None),
         ('stand', 'w1', 'w2', 'w3', 'w4', 'stand2'))
CUT = 1.2                             # (de face : rien de lui sous tant de haut, le comptoir et ce qui est dessus ; plus bas que le
                                      # verre, 1,38 m au plus bas)
DOOR_X = 932                          # (la porte de la planche, image « grab » : son bord gauche ; la main sur sa poignée gardée)
LIGHT = (1.0, 0.86, 0.76)             # (la lumière de la boutique sur lui : chaude ; un peu dans son dos)
GAIN = 0.86
DOOR_LIGHT, DOOR_TINT = (0.9, 0.3), (0.9, 0.88, 1.06)   # (à la porte : la part de lumière dans son dos, ce qu'il en perd vers l'avant ;
                                      # la teinte de la rue devant lui)
PAL = 22


def sheet():
    rgb = np.asarray(Image.open(SHEET).convert('RGB')).astype(float)
    return rgb, 765 - rgb.sum(2)      # (l'encre : l'écart au blanc)


def frames(rgb, ink):
    """les images de la planche, rangée par rangée de gauche à droite : leur boîte, leur couverture (ses trous bouchés, les
    morceaux détachés laissés)"""
    m = ink > 60
    lab, n = nd.label(m, np.ones((3, 3)))
    sz = nd.sum(m, lab, range(1, n + 1)); sl = nd.find_objects(lab)
    out = {}
    for r, (y0, y1) in enumerate(ROWS):
        comps = sorted([(sl[i][1].start, i + 1) for i in range(n) if sz[i] > 5000 and y0 <= sl[i][0].start < y1])
        for k, (x0, l) in enumerate(comps):
            name = NAMES[r][k] if k < len(NAMES[r]) else None
            if not name: continue
            s = sl[l - 1]
            box = (s[1].start, s[0].start, s[1].stop, s[0].stop)
            cov = nd.binary_fill_holes(lab[s] == l)
            out[name] = dict(row=r, box=box, rgb=rgb[s].copy(), m=cov)
    return out


def body_x(f, a, b):
    """l'axe de son corps : le milieu de sa couverture entre les rangées a et b (de la planche)"""
    y0 = f['box'][1]
    xs = [np.where(f['m'][y - y0])[0] for y in range(max(a, y0), min(b, f['box'][3]))]
    xs = [x for x in xs if len(x)]
    return f['box'][0] + float(np.median([(x.min() + x.max() + 1) / 2 for x in xs]))


def clean(F):
    """chaque image sans ses accessoires ; son échelle (px de la planche par mètre), le haut de sa serviette, son sol, son axe"""
    st = F['stand']
    ppm4 = (st['box'][3] - st['box'][1]) / H_TOP
    for name, f in F.items():
        x0, y0, x1, y1 = f['box']; ppm = ppm4 * HEAD[f['row']]
        f['ppm'] = ppm; f['top'] = y0
        if f['row'] < 3:
            f['floor'] = y0 + H_TOP * ppm
            cut = int(np.ceil(y0 + (H_TOP - CUT) * ppm)) - y0
            if name != 'grab': f['m'][cut:] = False
        else:
            f['floor'] = float(y1)
        if name == 'grab':                                                   # (la porte de la planche ôtée, la main gardée)
            R, G, B = (f['rgb'][..., c] for c in range(3))
            skin = (R > 150) & (G > 90) & (B < 150) & (R - B > 55)
            keep = nd.binary_dilation(skin, np.ones((5, 5))) & ((R + G + B) / 3 < 70) | skin
            xx = np.arange(f['m'].shape[1])[None] + x0
            door = xx >= DOOR_X
            wr = np.where(skin[:, DOOR_X - 8 - x0:DOOR_X - x0].any(1))[0]               # (le poignet : la main, à ses rangées ; la poignée
            rows = np.zeros_like(door); rows[max(0, wr.min() - 4):wr.max() + 5] = True  # dorée au-dessus et au-dessous ôtée)
            f['m'] &= ~door | (keep & rows)
        lab, n = nd.label(f['m'], np.ones((3, 3)))                           # (ce qui ne tient plus à lui : dehors)
        if n > 1:
            sz = nd.sum(f['m'], lab, range(1, n + 1)); f['m'] = lab == 1 + int(np.argmax(sz))
        f['m'] = nd.binary_fill_holes(f['m'])
        ya = lambda h: int(round(f['floor'] - h * ppm))                     # (la rangée de la planche à la hauteur h)
        if f['row'] < 2 or name.startswith('wipe'):                         # (de face : l'axe de son visage, la peau entre ses yeux et son
            R_, G_, B_ = (f['rgb'][..., c] for c in range(3))                   # menton ; la serviette et son nœud n'y sont pas)
            sk = f['m'] & (R_ > 150) & (G_ > 90) & (B_ < 150) & (R_ - B_ > 55)
            mids = [(np.where(sk[y - y0])[0].min() + np.where(sk[y - y0])[0].max() + 1) / 2 for y in range(ya(1.55), ya(1.40)) if sk[y - y0].any()]
            f['ax'] = x0 + float(np.median(mids))
        else: f['ax'] = body_x(f, ya(1.40), ya(1.25))
    # « grab » : la planche le coupe au tablier ; sous lui, les jambes de « stand » à son échelle, sous son axe (sa main pendante
    # ôtée : la jambe et le tablier derrière elle, pris à sa gauche sur la même rangée)
    g = F['grab']; k = g['ppm'] / st['ppm']
    h_lo = (g['floor'] - g['box'][3]) / g['ppm'] + 0.01                      # (le bas de « grab », en m)
    y_lo = int(np.floor(g['floor'] - h_lo * g['ppm'])) - g['top']           # (sa rangée, dans la case de « grab »)
    xs = np.arange(int(g['ax'] - 0.6 * g['ppm']), int(g['ax'] + 0.6 * g['ppm']))
    off = max(0, g['box'][0] - xs[0])
    W = max(xs[-1] + 1 - g['box'][0], g['m'].shape[1]) + off; H = int(np.ceil(g['floor'] - g['top'])) + 1
    M = np.zeros((H, W), bool); C = np.full((H, W, 3), 255.0)
    M[:y_lo, off:off + g['m'].shape[1]] = g['m'][:y_lo]; C[:y_lo, off:off + g['m'].shape[1]] = g['rgb'][:y_lo]
    sR, sG, sB = (st['rgb'][..., c] for c in range(3))
    sskin = (sR > 150) & (sG > 90) & (sB < 150) & (sR - sB > 55)
    for y in range(y_lo, H):
        h = (g['floor'] - (y + g['top'])) / g['ppm']
        r = int(round(st['floor'] - h * st['ppm'])) - st['box'][1]
        if not (0 <= r < st['m'].shape[0]): continue
        last = None
        for x in xs:
            sx = int(round(st['ax'] + (x - g['ax']) / k)) - st['box'][0]
            if not (0 <= sx < st['m'].shape[1] and st['m'][r, sx]): continue
            c = st['rgb'][r, sx]
            if sskin[r, sx] and h > 0.42: c = last if last is not None else c   # (la main pendante : ce qui est derrière)
            elif st['rgb'][r, sx].sum() > 120: last = c
            M[y, x - g['box'][0] + off] = True; C[y, x - g['box'][0] + off] = c
    g['m'] = M; g['rgb'] = C; g['box'] = (g['box'][0] - off, g['top'], g['box'][0] - off + W, g['top'] + H)
    return F


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
    """l'image à s px par mètre : RGBA (alpha plein dès la moitié couverte) ; son ancre (AX, AY) : le pixel de son axe sur le
    sol (le bas de ses semelles au bas de la rangée AY)"""
    k = s / f['ppm']
    x0, y0, x1, y1 = f['box']
    l, r = (x0 - f['ax']) * k, (x1 - f['ax']) * k
    AX = int(np.ceil(-l)) + 1; W = AX + int(np.ceil(r)) + 2
    t = (y0 - f['floor']) * k
    AY = int(np.ceil(-t)) + 1; H = AY + 2
    ox = AX + 0.5 + (x0 - f['ax']) * k; oy = AY + 1 + (y0 - f['floor']) * k   # (le coin de la planche dans la cellule)
    cov = boite(f['m'].astype(float), k, ox, oy, W, H)
    a = cov >= 0.5
    rgb = np.zeros((H, W, 3))
    hh, ww = f['m'].shape
    for i, j in zip(*np.where(a)):
        ya, yb = (i - oy) / k, (i + 1 - oy) / k; xa, xb = (j - ox) / k, (j + 1 - ox) / k
        r0, r1 = max(0, int(np.floor(ya))), min(hh, int(np.ceil(yb))); c0, c1 = max(0, int(np.floor(xa))), min(ww, int(np.ceil(xb)))
        mm = f['m'][r0:r1, c0:c1]; px = f['rgb'][r0:r1, c0:c1][mm]
        if not len(px): continue
        med = np.median(px, 0); d = np.abs(px - med).sum(1)
        sel = px[d <= np.median(d)] if len(px) > 3 else px
        rgb[i, j] = sel.mean(0)
    return np.concatenate([rgb, a[..., None] * 255.0], 2), AX, AY


def light(c):                         # (la lumière de la boutique sur lui : chaude, un peu dans son dos)
    return np.clip(c[..., :3] * np.array(LIGHT) * GAIN, 0, 255)


def palette(cells, n=PAL):            # (une palette commune : ni grain ni scintillement d'une image à l'autre)
    px = np.concatenate([c[c[..., 3] > 0][:, :3] for c in cells])
    return O.R.palette(px, n, per=800)


# ---- ses places dans la maquette (tools/oden_interior.py) : à la marmite (derrière le comptoir, vu par la fenêtre), à la porte
Z_D = 38.2                            # à la porte : la profondeur du milieu du vantail de droite (36,7 px par mètre)
X_D = (-8.08, -6.95)                  # (il y vient de là, au fond, hors de vue ; il s'arrête là, sa main sur la poignée)
X_A = -9.69                           # (à la marmite : il vient de là, de la cuisine)
WALK = (1.0, 0.17)                    # (sa marche : m/s, s par image)
USE = {'A': ('idle', 'nod', 'happy', 'laugh', 'pick', 'lift', 'ladle', 'serve', 'offer', 'wipe', 'wipe2', 'stand', 'w1', 'w2', 'w3', 'w4'),
       'D': ('stand', 'stand2', 'grab', 'w1', 'w2', 'w3', 'w4')}


def build(F):
    """chaque image à chacune de ses places ; une palette commune (sous la lumière de la boutique), chaque pixel ramené à elle"""
    Xp, Zp, hp = O.pot_at()
    places = {'A': O.Z_M, 'D': Z_D}
    cells = {}
    for p, Z in places.items():
        for n in USE[p]:
            c, ax, ay = cell(F[n], O.F / Z)
            c[..., :3] = light(c)
            if p == 'D':                                                     # (à la porte : la lumière de la boutique dans son dos, la rue
                xs = np.where(c[..., 3].max(0) > 0)[0]                       # devant lui ; plus sombre et un peu violet vers l'avant)
                r = np.clip((np.arange(c.shape[1]) - xs.min()) / max(1, xs.max() - xs.min()), 0, 1)[None, :, None]
                c[..., :3] *= (DOOR_LIGHT[0] - DOOR_LIGHT[1] * r) * (1 + (np.array(DOOR_TINT) - 1) * r)
            cells[(p, n)] = (c, ax, ay)
    pal = palette([c for c, _, _ in cells.values()])
    out = {}
    for k, (c, ax, ay) in cells.items():
        a = c[..., 3] > 0
        q = pal[O.R.nearest(c[..., :3].reshape(-1, 3), pal)].reshape(c.shape[:2] + (3,))
        rgba = np.zeros(c.shape[:2] + (4,), np.uint8); rgba[..., :3] = np.where(a[..., None], np.round(q), 0); rgba[..., 3] = np.where(a, 255, 0)
        ys, xs = np.where(a)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1      # (serrée sur lui)
        out[k] = (rgba[y0:y1, x0:x1], ax - x0, ay - y0)
    return out, pal


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
        for x, y, m in self.cells: a[y:y + m.shape[0], x:x + m.shape[1]] = m
        return a


def main():
    prev = sys.argv[sys.argv.index('--preview') + 1] if '--preview' in sys.argv else None
    rgb, ink = sheet()
    Fr = clean(frames(rgb, ink))
    C, pal = build(Fr)
    A = Atlas(256)
    OMF = {'A': {}, 'D': {}}
    for (p, n), (c, ax, ay) in sorted(C.items(), key=lambda t: (t[0][0], -t[1][0].shape[0], t[0][1])):
        OMF[p][n] = A.add(c) + [int(ax), int(ay)]
    Xp, Zp, hp = O.pot_at()
    sA, sD = O.F / O.Z_M, O.F / Z_D
    px = lambda X, Z: round(O.VX + O.F * X / Z, 2)
    OMF['A'].update({'z': round(O.Z_M, 2), 'floor': round(O.VY + O.EYE * sA, 2), 'from': px(X_A, O.Z_M), 'at': px(Xp, O.Z_M), 'v': round(WALK[0] * sA, 2)})
    OMF['D'].update({'z': Z_D, 'floor': round(O.VY + O.EYE * sD, 2), 'from': px(X_D[0], Z_D), 'at': px(X_D[1], Z_D), 'v': round(WALK[0] * sD, 2)})
    OMF['step'] = WALK[1]
    img = A.image()
    print('le maître : à la marmite Z %.2f (%.1f px/m, ses pieds à la rangée %.1f, de x %.1f à %.1f) ; à la porte Z %.2f (%.1f px/m, de x %.1f à %.1f) ; '
          '%d images, atlas %d x %d, palette %d' % (O.Z_M, sA, OMF['A']['floor'], OMF['A']['from'], OMF['A']['at'], Z_D, sD, OMF['D']['from'],
                                                   OMF['D']['at'], len(C), img.shape[1], img.shape[0], len(pal)))
    if prev:
        bg = np.zeros(img.shape[:3], float); bg[..., :3] = (60, 90, 60); bg[..., 3] = 255
        al = img[..., 3:] / 255.0; bg[..., :3] = bg[..., :3] * (1 - al) + img[..., :3] * al
        Image.fromarray(bg[..., :3].astype(np.uint8)).resize((img.shape[1] * 4, img.shape[0] * 4), Image.NEAREST).save(os.path.join(prev, 'master_atlas_x4.png'))
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
