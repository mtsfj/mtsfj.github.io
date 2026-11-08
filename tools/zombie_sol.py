#!/usr/bin/env python3
"""Le sol des zombies : où ils marchent, à quelle taille, derrière quoi ; mesuré sur la peinture, écrit dans street.js (SOL).

    python3 tools/zombie_sol.py                     (le tableau des repères et le plan sur la sortie ; réécrit la ligne SOL de
                                                     assets/street.js ; relancé, les mêmes octets)
    python3 tools/zombie_sol.py --controle DIR      (en plus : sol_peinture.png, le plan reporté sur la peinture (x2), et
                                                     sol_carte.png, le plan vu de dessus, ses obstacles et ses départs)
    python3 tools/zombie_sol.py --controle DIR --chemins chemins.json
                                                    (sur la carte : des chemins de zombies, {nom: [[[X, D], ...], ...]}, en
                                                     mètres, un jeu par couleur)

La caméra est le modèle B (tools/figures_audit.py) : F = 959,5 px, l'œil à 1,41 m de la chaussée, l'horizon à 615, et
le trottoir à 15 cm (l'œil à 1,26 m au-dessus de lui). Un point du sol (X : de côté, D : en profondeur, en mètres ; G : la
hauteur du sol, 0 ou 0,15) se voit à x = 700 + F X / D, à la rangée 615 + F (1,41 - G) / D. Les zombies avaient leurs pieds
sur la chaussée partout : sur un trottoir, la rangée de leurs pieds disait 11 % plus près que leur taille.

La taille (REPERES). Les marques au sol (la bordure de 15 cm, les bandes du passage de 45 cm) font B exactement ; ce qui est
debout dans la peinture est plus grand : le bus (3 m de haut), les distributeurs (1,83 m), les portes (2 à 2,3 m) font
1,08 à 1,11 fois leur taille en B, près de nous comme au bus. Une figure posée à côté doit leur ressembler : sa taille en px
est K x B (K, le facteur de la peinture, la médiane pondérée de ces repères ; un seul pour toute la rue : de 11 à 41 m, aucune
pente). Les portes d'Ichiraku (1,04 : leur hauteur réelle incertaine) et les roues du bus (1,15) y pèsent peu ; le vélo
(0,86) et le fond du carrefour (la maison du fond, 1,75 ; le garde-corps, 0,86), où aucun zombie ne va, pas du tout. Le pas
d'un zombie va avec sa taille (son pas en mètres de B : K fois le sien), ses pieds restent posés.

Le plan (ZONES, en mètres de B, chaque zone sa hauteur de sol) : la chaussée de la rue (bordures à |X| = 2,80, mesurées
colonne par colonne des deux côtés) jusqu'au carrefour, la rue de travers (sa bordure proche à 28,8 m, la lointaine à 46,5 m) ;
le trottoir de droite jusqu'aux façades (4,62 m : les pieds des boutiques, d'Ichiraku et des suivantes ; PEINT, les points
mesurés, et leur place dans le plan sur la sortie), le coin du
Pokémon Center à 26,9 m ; celui de gauche jusqu'au dojo et à la dagashi-ya (5,45 m), devant les distributeurs (4,55 m : leurs
faces peintes de face), devant l'oden (5,0 m), le coin à 23,7 m ; le passage derrière les distributeurs d'où sortent ceux de la
« ruelle ». Les obstacles (OBST : le poteau, le vélo, le pot de fleurs) en cercles, leur rayon peint. Un zombie garde son corps
(0,3 m) dans le plan et hors des obstacles. Les départs de la horde (DEPARTS) : sous le bas de l'image, sur la chaussée ou le
trottoir, la moitié droite de la rue pour ceux qui y sont déjà, le passage caché pour la ruelle.

Ce qui cache (cache()) : la profondeur de chaque chose peinte devant laquelle ou derrière laquelle un zombie passe, par colonne
(les façades de gauche, les distributeurs, l'oden : leur plan et la rangée de leur pied) ou d'un bloc (le poteau, d'après son
tracé COCC, à la profondeur de son pied sur le trottoir) : street.js en fait la texture des profondeurs (crewOccTex), un
zombie plus loin que la chose y est caché, plus près il passe devant.

Il faut Pillow, numpy.
"""
import argparse
import json
import math
import os
import re
import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = lambda p: os.path.join(ROOT, 'assets', p)
JSF = A('street.js')

# ---- la caméra (B)
CF, CEYE, CHZ, TR = 959.5, 1.41, 615.0, 0.15


def rangee(D, G=0.0):
    return CHZ + CF * (CEYE - G) / D


def ecran(X, D, G=0.0):
    return 700.0 + CF * X / D, rangee(D, G)


def sol(x, r, G=0.0):
    """le point du sol de hauteur G vu au pixel (x, r) : (X, D)"""
    D = CF * (CEYE - G) / (r - CHZ)
    return (x - 700.0) * D / CF, D


# ---- la taille : les repères debout de la peinture [quoi, colonne, rangée du pied, hauteur px, taille réelle (m), sol
# (G), poids] ; la hauteur en B à cette rangée, K = peint / B. Poids 0 : mesuré, pas compté
REPERES = [
    ('le bus, du toit (rangée 9 du bus) aux roues (87) : 77,5 px pour 3,0 m', 700, 648.0, 77.5, 3.0, 0.0, 3),
    ('le bus, l\'appui de ses fenêtres (rangée 44) : 43 px pour 1,7 m', 700, 648.0, 43.0, 1.7, 0.0, 1),
    ('le bus, ses roues (27 px pour 1,0 m)', 700, 648.0, 27.0, 1.0, 0.0, 1),
    ('distributeur proche, x 285 (176 px pour 1,83 m)', 285, 724.0, 176.0, 1.83, TR, 3),
    ('porte rose de la zone 1, x 1090 (imposte comprise, 216 px pour 2,3 m)', 1090, 722.0, 216.0, 2.3, TR, 2),
    ('porte de l\'oden, x 440 (94 px pour 2,0 m)', 440, 670.0, 94.0, 2.0, TR, 2),
    ('portes d\'Ichiraku, x 1160 (224 px pour 2,1 m)', 1160, 744.0, 224.0, 2.1, TR, 1),
    ('le vélo, x 965 : ses roues (37 px pour 0,66 m)', 965, 697.0, 37.0, 0.66, TR, 0),
    ('le garde-corps du fond (15 px pour 1,0 m)', 700, 637.0, 15.0, 1.0, TR, 0),
    ('la porte de la maison du fond (61 px pour 2,0 m)', 580, 637.0, 61.0, 2.0, TR, 0),
]


def facteur():
    rows, w = [], []
    for nom, x, r, h, m, G, p in REPERES:
        D = CF * (CEYE - G) / (r - CHZ)
        k = h / (m * CF / D)
        rows.append((nom, D, k, p))
        w += [k] * p
    K = float(np.median(w))
    return round(K, 2), rows


# ---- le plan : les points peints (x, rangée, G) d'où viennent ses bords, et ses zones en (X, D)
PEINT = {
    'bordure droite (pied, chaussée)': [(924, 728, 0.0), (980, 756, 0.0), (1000, 766, 0.0)],
    'bordure gauche (arête, trottoir)': [(260, 813, TR), (340, 777, TR), (420, 741, TR), (480, 714, TR)],
    'façade droite (pieds des boutiques)': [(1100, 727, TR), (1150, 740, TR), (1200, 750, TR), (1260, 763, TR), (1350, 793, TR), (1010, 698, TR)],
    'coin du Pokémon Center': [(870, 660, TR)],
    'bordure proche de la rue de travers': [(505, 657, TR), (600, 657, TR), (805, 656, TR), (865, 656, TR)],
    'bordure lointaine (garde-corps)': [(600, 641, TR), (760, 641, TR)],
    'dojo, son seuil': [(0, 775, TR), (103, 750, TR)],
    'dagashi-ya': [(140, 745, TR), (225, 728, TR)],
    'distributeurs (leurs faces, peintes de face)': [(230, 729, TR), (345, 712, TR)],
    'alcôve du banc (son sol)': [(352, 690, TR), (398, 690, TR)],
    'oden, son pied': [(405, 676, TR), (470, 668, TR)],
    'coin de l\'oden': [(500, 666, TR)],
    'poteau, son pied (x 1024-1065)': [(1044.5, 751, TR)],
}
XB = 2.80                                  # les bordures de la rue
XR = 4.62                                  # la façade de droite (la moyenne de ses pieds)
DCN, DCF = 28.8, 46.5                      # la rue de travers : sa bordure proche, la lointaine
ZONES = [                                  # [nom, G, polygone (X, D)] : la chaussée, puis les trottoirs
    ['chaussée', 0.0, [[-XB, 2.0], [XB, 2.0], [XB, DCN], [40.0, DCN], [40.0, DCF], [-40.0, DCF], [-40.0, DCN], [-XB, DCN]]],
    ['trottoir droit', TR, [[XB, 2.0], [4.11, 2.0], [4.11, 6.0], [XR, 6.0], [XR, 26.9], [14.0, 26.9], [14.0, DCN], [XB, DCN]]],
    ['trottoir gauche', TR, [[-XB, 2.0], [-XB, DCN], [-14.0, DCN], [-14.0, 23.7], [-5.0, 23.7], [-5.0, 16.3], [-4.55, 16.3],
                             [-4.55, 10.7], [-5.3, 10.7], [-5.45, 9.3], [-5.45, 2.0]]],
    ['passage des distributeurs', TR, [[-4.55, 12.9], [-4.55, 15.9], [-8.0, 15.9], [-8.0, 12.9]]],
]
CACHE_ZONES = ['passage des distributeurs']   # (hors de vue : on n'y naît que pour en sortir)
OBST = [                                   # [nom, X, D, r] : ce qui est posé sur le sol, dans le plan
    ['poteau', 3.19, 8.89, 0.20],
    ['vélo', 4.06, 14.5, 0.28], ['vélo', 4.06, 15.1, 0.28], ['vélo', 4.06, 15.7, 0.28],
    ['pot de fleurs', 4.08, 19.2, 0.24],
]
CORPS = 0.30                               # le corps d'un zombie : ce qu'il garde d'un mur ou d'un obstacle


# ---- ce qui cache : la profondeur des choses peintes, par colonne ou d'un bloc
def cache():
    """les façades de gauche (du bord à x 504, où le coin de l'oden finit) : par colonne, la profondeur du plan qu'on y voit
    et la rangée de son pied ; le poteau en rectangles [x0, y0, x1, y1, D] (son tracé, COCC ; sa profondeur, celle de son
    pied sur le trottoir : 8,89 m, pas les 9,95 de la chaussée). Le vélo et le pot de fleurs de droite sont contre la façade,
    à moins d'un corps d'elle : personne ne passe derrière eux ; le banc de l'alcôve est derrière ceux qui sortent de la
    ruelle : ils ne cachent personne"""
    # (le dojo, son seuil ; la porte sombre ; la dagashi-ya : leurs pieds le long de la rue ; les distributeurs, peints de face :
    #  leur pied, d'un bord à l'autre ; l'alcôve du banc : ouverte, son fond derrière quiconque y passe ; l'oden et son coin)
    PIECES = [(0, 103, [(0, 775), (103, 750)]), (103, 140, [(103, 750), (140, 745)]), (140, 225, [(140, 745), (225, 728)]),
              (225, 352, [(230, 729), (345, 712)]), (352, 399, None), (399, 504, [(405, 676), (470, 668), (504, 666)])]

    def colonne(x):
        for x0, x1, pts in PIECES:
            if x0 <= x < x1:
                if pts is None:
                    return None
                r = float(np.interp(x, [p[0] for p in pts], [p[1] for p in pts]))
                return CF * (CEYE - TR) / (r - CHZ), int(round(r))
        return None
    cols = []
    for x in range(504):
        c = colonne(x)
        cols.append([round(c[0], 2), c[1]] if c else [0, 0])
    js = open(JSF, encoding='utf-8').read()
    i = js.index('  const COCC = ') + len('  const COCC = ')
    pole = json.JSONDecoder().raw_decode(js[i:])[0]['pole']['runs']
    D_pole = sol(1044.5, 751, TR)[1]
    return cols, [[r[2], r[0], r[3] + 1, r[1] + 1, round(D_pole, 2)] for r in pole]


# ---- les départs : où la horde entre dans le plan (X, D) ; voir street.js (crewSpawn, wave)
DEPARTS = {
    'droite, de chez nous': [[0.6, 5.8], [3.8, 6.7]],       # (leurs pieds juste sous l'image : 5,8 à 6,0 m sur le trottoir,
    'droite, au milieu de la rue': [[0.4, 12.0], [2.4, 26.0]],   #  6,5 à 6,7 sur la chaussée ; la moitié droite de la rue)
    'gauche, de chez nous': [[-3.8, 5.8], [-0.6, 6.7]],
    'gauche, au milieu de la rue': [[-2.4, 12.0], [-0.4, 26.0]],
    'ruelle (derrière les distributeurs)': [[-7.0, 13.3], [-6.8, 14.5]],
}


def dans(p, poly):
    x, y = p
    c = False
    for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]):
        if (y0 > y) != (y1 > y) and x < x0 + (x1 - x0) * (y - y0) / (y1 - y0):
            c = not c
    return c


def zone(X, D):
    for nom, G, p in ZONES:
        if dans((X, D), p):
            return nom, G
    return None, None


def donnees():
    K, rows = facteur()
    cols, rect = cache()
    S = {'k': K, 'tr': TR, 'corps': CORPS,
         'z': [[nom, G, [[round(a, 3), round(b, 3)] for a, b in p]] for nom, G, p in ZONES],
         'cz': CACHE_ZONES,
         'o': [[nom, X, D, r] for nom, X, D, r in OBST],
         'gc': cols, 'gr': rect,
         'dep': DEPARTS}
    return S, rows


def verifier(rows):
    print('| repère | D (m) | K = peint / B | poids |\n|---|---|---|---|')
    for nom, D, k, p in rows:
        print('| %s | %.1f | %.3f | %d |' % (nom, D, k, p))
    K, _ = facteur()
    print('\nK = %.2f (la médiane pondérée)\n' % K)
    print('| bord peint | point (x, rangée) | X (m) | D (m) | zone du plan |\n|---|---|---|---|---|')
    for nom, pts in PEINT.items():
        for x, r, G in pts:
            X, D = sol(x, r, G)
            z, _ = zone(X, D)
            print('| %s | %d, %d | %.2f | %.2f | %s |' % (nom, x, r, X, D, z or '-'))
    for nom, (a, b) in DEPARTS.items():
        for X in (a[0], b[0]):
            for D in (a[1], b[1]):
                z, _ = zone(X, D)
                assert z, ('départ hors du plan', nom, X, D)


def ligne(js, nom, data):
    pat = re.compile(r'^(  const ' + nom + r' = )(\{.*?\});(.*)$', re.M)
    m = pat.search(js)
    if not m:
        raise SystemExit('la ligne %s de assets/street.js est introuvable' % nom)
    txt = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
    return js[:m.start()] + m.group(1) + txt + ';' + m.group(3) + js[m.end():]


# ---- les images de contrôle
def controle(out, S, chemins=None):
    os.makedirs(out, exist_ok=True)
    im = Image.open(A('layer_city_off.webp')).convert('RGB')
    im = Image.eval(im, lambda v: min(255, int(v * 2.2)))
    k = 2
    im = im.resize((im.width * k, im.height * k), Image.NEAREST)
    d = ImageDraw.Draw(im)
    col = {'chaussée': (255, 210, 60), 'trottoir droit': (90, 255, 120), 'trottoir gauche': (90, 255, 120), 'passage des distributeurs': (255, 120, 255)}
    for nom, G, p in S['z']:
        for (X0, D0), (X1, D1) in zip(p, p[1:] + p[:1]):
            pts = []
            for t in np.linspace(0, 1, 40):
                X, D = X0 + (X1 - X0) * t, D0 + (D1 - D0) * t
                x, r = ecran(X, D, G)
                pts.append((x * k, r * k))
            d.line(pts, fill=col.get(nom, (255, 255, 255)), width=1)
    for nom, X, D, r in S['o']:
        pts = [ecran(X + r * math.cos(a), D + r * math.sin(a), TR) for a in np.linspace(0, 2 * math.pi, 40)]
        d.line([(x * k, y * k) for x, y in pts], fill=(255, 80, 80), width=2)
    for x0, y0, x1, y1, D in S['gr']:
        if D != S['gr'][0][4]:
            d.rectangle([x0 * k, y0 * k, x1 * k, y1 * k], outline=(80, 200, 255))
    for x, (dd, r) in enumerate(S['gc']):
        if dd:
            d.point((x * k, r * k), fill=(80, 200, 255))
    for nom, pts in PEINT.items():
        for x, r, G in pts:
            d.ellipse([x * k - 3, r * k - 3, x * k + 3, r * k + 3], outline=(255, 255, 255))
    im.crop((0, 560 * k, im.width, im.height)).save(os.path.join(out, 'sol_peinture.png'))
    # vu de dessus : X de -10 à 10 m, D de 0 à 50 m, 30 px par mètre en X, 12 en D
    sx, sd, W, H = 30, 12, 600, 600
    c = Image.new('RGB', (W + 40, H + 76), (18, 18, 24))
    g = ImageDraw.Draw(c)
    P = lambda X, D: (20 + (X + 10) * sx, 60 + H - D * sd)
    fill = {'chaussée': (52, 52, 64), 'trottoir droit': (70, 92, 76), 'trottoir gauche': (70, 92, 76), 'passage des distributeurs': (80, 60, 86)}
    for nom, G, p in S['z']:
        g.polygon([P(max(-10, min(10, X)), D) for X, D in p], fill=fill.get(nom, (60, 60, 60)), outline=(140, 140, 150))
    for D in range(0, 51, 5):
        g.line([P(-10, D), P(-9.6, D)], fill=(200, 200, 200)); g.text(P(-9.5, D + 0.6), '%d m' % D, fill=(160, 160, 170))
    for nom, X, D, r in S['o']:
        x, y = P(X, D)
        g.ellipse([x - r * sx, y - r * sd, x + r * sx, y + r * sd], fill=(200, 70, 70))
        g.ellipse([x - (r + CORPS) * sx, y - (r + CORPS) * sd, x + (r + CORPS) * sx, y + (r + CORPS) * sd], outline=(200, 70, 70))
    for nom, ((X0, D0), (X1, D1)) in S['dep'].items():
        g.rectangle([P(X0, D1), P(X1, D0)], outline=(250, 220, 90))
    if chemins:                                    # ({nom: [chemin, ...]} : chaque jeu sa couleur, sa légende)
        cols = [(255, 90, 90), (120, 220, 255), (170, 255, 140), (240, 120, 220)]
        for i, (nom, chs) in enumerate(chemins.items()):
            for ch in chs:
                g.line([P(max(-10, min(10, X)), D) for X, D in ch if D <= 50], fill=cols[i % 4], width=1)
            g.text((24, 30 + 13 * i), nom, fill=cols[i % 4])
    g.text((24, 4), 'le sol des zombies vu de dessus : X de -10 a 10 m, D de 0 a 50 m', fill=(230, 230, 230))
    g.text((24, 17), 'chaussee (gris), trottoirs (vert), passage cache (violet), obstacles et leur marge (rouge), departs (jaune)', fill=(170, 170, 180))
    c.save(os.path.join(out, 'sol_carte.png'))


def main():
    ap = argparse.ArgumentParser(description='le sol des zombies (voir la docstring)')
    ap.add_argument('--controle', default=None, help='un dossier : le plan sur la peinture et vu de dessus')
    ap.add_argument('--chemins', default=None, help='des chemins à tracer sur la carte (JSON : {nom: [[[X, D], ...], ...]})')
    o = ap.parse_args()
    S, rows = donnees()
    verifier(rows)
    js = open(JSF, encoding='utf-8').read()
    js2 = ligne(js, 'SOL', S)
    if js2 != js:
        with open(JSF, 'w', encoding='utf-8') as f:
            f.write(js2)
    if o.controle:
        ch = json.load(open(o.chemins)) if o.chemins else None
        controle(o.controle, S, ch)


if __name__ == '__main__':
    main()
