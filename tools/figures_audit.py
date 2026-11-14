#!/usr/bin/env python3
"""Les gens de la rue : leur taille, leur tête et leur grain, mesurés contre la peinture (une mesure, rien n'est écrit dans assets/).

    python3 tools/figures_audit.py                      (le tableau en markdown sur la sortie, et dans le dossier --out, par
                                                         défaut /tmp/figures_audit : figures_audit.json, sheet_b_proportions.png)
    python3 tools/figures_audit.py --shots dossier      (avec des captures 1456 x 816 de la rue : sheet_a_in_place.png, chaque
                                                         figure à sa place x4, et sheet_c_grain.png, la peinture autour d'elle et
                                                         elle x6 ; les captures attendues et leurs boîtes : SHOTS)
    python3 tools/figures_audit.py --out dossier --only obaa,oden_d

La caméra. Deux modèles du sol sont dans le code : A (F = 1400 px, l'œil à 1,5 m du trottoir, 1,65 m de la chaussée ; ZR, les
maquettes de l'oden, du dagashi-ya, d'Ichiraku, de l'arcade) et B (CF = 959,5 px, CEYE = 1,41 m de la chaussée, 1,26 m du
trottoir ; l'équipe, la horde, le drone). Tous deux ont l'horizon à 615 ; pour une figure debout, sa hauteur à l'écran ne dépend
que de la hauteur de l'œil : h = H (y_pied - 615) / œil (la focale s'annule). La peinture tranche (CUES, mesurés ici
colonne par colonne) : la bordure du trottoir (15 cm) et les bandes du passage piéton (45 + 45 cm) donnent l'œil à 1,41 m de la
chaussée, B exactement ; la profondeur du passage (4 m) donne F ~ 960 ; les portes et les distributeurs peints, un peu plus
grands que nature, le mettent encore un peu plus bas (1,13 à 1,27 m du trottoir). A fait donc toutes ses figures 16 % trop
petites (1,26 / 1,5 = 0,84) : une figure placée par A doit faire 1,19 fois sa taille A (FIX_A), ou, dans les outils en A, ses
mètres x 1,19 (un homme de 1,70 m y fait 2,02 « mètres A »).

Les figures (CHARS) : pour chacune, ses images (cellules de son atlas, lues dans assets/street.js), sa place à l'écran (px de
la scène par px de l'image), l'échelle de B à cette place, sa taille voulue (H, l'espèce, l'âge), sa tête mesurée à l'œil sur
l'image de référence (HEAD : du haut du crâne ou des cheveux au menton, chapeau et casque compris s'ils collent au crâne) et
l'estimation automatique (la rangée la plus étroite sous la tête, à revérifier). Le grain : les mêmes mesures que sur la
peinture autour d'elle (PAINT : des boîtes de la peinture, layer_city_off.webp, à côté de chaque figure) : couleurs exactes,
familles de couleurs (écart de 8 au plus), la taille des taches, les pixels isolés, le pas de lumière entre voisins, les
alphas partiels, l'anneau du bord contre l'anneau d'en dessous (< 0,6 : un contour sombre ; > 1,1 : un liseré clair).
Il faut Pillow, numpy, scipy.
"""
import argparse
import json
import os
import re
import sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as nd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = lambda p: os.path.join(ROOT, 'assets', p)
JS = open(A('street.js'), encoding='utf-8').read()
LUM = np.array([0.299, 0.587, 0.114])

# ---- la caméra
HZ = 615.0
EYE_A, EYE_B = 1.5, 1.41 - 0.15            # l'œil au-dessus du trottoir (A ; B : 1,41 de la chaussée, trottoir à 15 cm)
FIX_A = EYE_A / EYE_B                      # 1,19 : ce qu'une figure placée par A doit gagner
# les repères de la peinture (layer_city_off.webp), mesurés colonne par colonne : [quoi, colonne, rangée du pied, hauteur px,
# taille réelle supposée (m), sur la chaussée (True) ou le trottoir]
CUES = [
    ('bordure droite, x 924 (15 cm)', 924, 728, 12, 0.15, True),
    ('bordure droite, x 980 (15 cm)', 980, 756, 15, 0.15, True),
    ('bordure droite, x 1000 (15 cm)', 1000, 766, 16, 0.15, True),
    ('passage piéton : période des bandes à la rangée 668,5 (0,90 m, en travers)', 700, 668.5, 34.5, 0.90, True),
    ('distributeur proche, x 285 (1,83 m)', 285, 724, 176, 1.83, False),
    ('portes d\'Ichiraku, x 1160 (linteau 520 - seuil 744 ; 2,0 m)', 1160, 744, 224, 2.0, False),
    ('portes d\'Ichiraku, la même (2,2 m)', 1160, 744, 224, 2.2, False),
    ('porte de l\'oden, x 440 (linteau 576 - seuil 670 ; 2,0 m)', 440, 670, 94, 2.0, False),
    ('porte rose de la zone 1, x 1090 (506 - 722 avec l\'imposte ; 2,3 m)', 1090, 722, 216, 2.3, False),
    ('garde-corps du fond (622 - 637 ; 1,0 m)', 700, 637, 15, 1.0, False),
    ('porte de la maison du fond, zone 5 (576 - 637 ; 2,0 m) : le fond agrandi par le peintre', 580, 637, 61, 2.0, False),
]


def implied_eye(c):
    _, _, y, h, m, road = c
    e = m * (y - HZ) / h
    return e - 0.15 if road else e   # (rapporté au trottoir)


# ---- les données de street.js
def J(name):
    i = JS.find('const ' + name + ' = ')
    if i < 0:
        i = JS.find(' ' + name + ' = {')
        i = JS.find('{', i)
    else:
        i += len('const ' + name + ' = ')
    return json.JSONDecoder().raw_decode(JS[i:])[0]


def jsnum(pat):
    m = re.search(pat, JS)
    return float(m.group(1)) if m else None


def img(name):
    return np.asarray(Image.open(A(name)).convert('RGBA'))


def cell(a, c):
    sx, sy, w, h = [int(v) for v in c[:4]]
    return a[sy:sy + h, sx:sx + w]


# ---- les mesures du grain
def bbox(alpha, thr=128):
    ys, xs = np.nonzero(alpha >= thr)
    if not len(ys):
        return None
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def grain(rgb, mask=None, tol=8):
    rgb = rgb[..., :3].astype(int)
    H, W = rgb.shape[:2]
    if mask is None:
        mask = np.ones((H, W), bool)
    px = rgb[mask]
    n = len(px)
    if not n:
        return {}
    key = (px[:, 0] << 16) | (px[:, 1] << 8) | px[:, 2]
    u, inv, cnt = np.unique(key, return_inverse=True, return_counts=True)
    order = np.argsort(-cnt)
    cols = np.stack([(u >> 16) & 255, (u >> 8) & 255, u & 255], 1)[order]
    ent, idx = [], np.zeros(len(cols), int)
    for i, c in enumerate(cols):                    # des familles : chaque couleur dans la première à 8 près, les plus fréquentes d'abord
        for j, e in enumerate(ent):
            if np.abs(c - e).max() <= tol:
                idx[i] = j
                break
        else:
            ent.append(c)
            idx[i] = len(ent) - 1
    fam = np.empty(len(u), int)
    fam[order] = idx
    fcnt = np.sort(np.bincount(fam[inv]))[::-1]
    lab = np.full((H, W), -1)
    lab[mask] = fam[inv]
    sizes = []
    for e in np.unique(lab[mask]):
        l, k = nd.label(lab == e)
        if k:
            sizes.extend(np.bincount(l.ravel())[1:].tolist())
    sizes = np.array(sizes, float)
    L = rgb @ LUM
    d = np.concatenate([np.abs(L[:, 1:] - L[:, :-1])[mask[:, 1:] & mask[:, :-1]], np.abs(L[1:] - L[:-1])[mask[1:] & mask[:-1]]])
    lp = np.pad(lab, 1, constant_values=-2)
    c = lp[1:-1, 1:-1]
    same = (lp[:-2, 1:-1] == c) | (lp[2:, 1:-1] == c) | (lp[1:-1, :-2] == c) | (lp[1:-1, 2:] == c)
    Lm = L[mask]
    return dict(uniq=int(len(u)), fam=len(ent), fam90=int(np.searchsorted(np.cumsum(fcnt) / n, 0.9) + 1),
                tache=round(float((sizes ** 2).sum() / sizes.sum()), 1),          # (la tache où tombe un pixel, en moyenne)
                isole=round(float((~same & mask).sum() / mask.sum()), 3),
                pas=round(float(np.median(d[d > 0])) if (d > 0).any() else 0, 1),   # (le pas de lumière médian entre voisins différents)
                doux=round(float(((d > 0) & (d <= 3)).sum() / max(1, len(d))), 2),   # (part des voisins à 1-3 près : le grain fin du peintre)
                L5=int(np.percentile(Lm, 5)), L50=int(np.percentile(Lm, 50)), L95=int(np.percentile(Lm, 95)))


def edge(rgba):
    a = rgba[..., 3].astype(int)
    op = a >= 128
    part = float(((a > 0) & (a < 250)).sum() / max(1, (a > 0).sum()))   # (250-254 : pleins ; la horde y range ses jambes, tools/zombie_sheets.py)
    e1 = nd.binary_erosion(op)
    e2 = nd.binary_erosion(e1)
    L = rgba[..., :3].astype(float) @ LUM
    r1, r2 = L[op & ~e1], L[e1 & ~e2]
    return dict(alpha_part=round(part, 2), anneau=round(float(r1.mean() / max(1e-6, r2.mean())) if len(r1) and len(r2) else 0, 2))


def neck_guess(alpha, thr=128):
    """une estimation de la tête : du haut à la rangée la plus étroite entre 6 et 32 % de la hauteur, sous la plus large"""
    b = bbox(alpha, thr)
    if not b:
        return None
    x0, y0, x1, y1 = b
    H = y1 - y0
    w = (alpha[y0:y1, x0:x1] >= thr).sum(1)
    lo, hi = max(1, int(0.06 * H)), max(2, int(0.32 * H))
    hw = int(np.argmax(w[:lo + 1 + (hi - lo) // 2]))
    seg = w[max(hw + 1, lo):hi + 1]
    return None if not len(seg) else max(hw + 1, lo) + int(np.argmin(seg))


# ---- les figures. place : (nom, k = px de la scène par px de l'image, sB = px par mètre de B à cette place, rangée du pied ou None)
DGO, OMF, IRF, WKS = J('DGO'), J('OMF'), J('IRF'), J('WKS')
ZR = dict(zs=jsnum(r'const ZR = \{[^}]*zs: ([\d.]+)'), w0=jsnum(r'const ZR = \{[^}]*w0: (-?[\d.]+)'), ppm=jsnum(r'const ZR = \{[^}]*ppm: ([\d.]+)'))
ZRC = {k: [int(v) for v in re.search(k + r': \[([\d, ]+)\]', re.search(r'const ZRC = \{[^;]*\};', JS).group(0)).group(1).split(',')]
       for k in ('walkT', 'idle')}
NG = dict(vx=810.0, uzn=jsnum(r'uzn: ([\d.]+)'), kzn=jsnum(r'kzn: ([\d.]+)'), zn=jsnum(r'zn: ([\d.]+), ppm'), ppm=jsnum(r'const NG = \{[^}]*ppm: ([\d.]+)'))
NCL = [int(v) for v in re.search(r'look: \[([\d, ]+)\]', re.search(r'const NC = \{[^;]*\};', JS).group(0)).group(1).split(',')]
nU = lambda s: NG['vx'] + (NG['uzn'] - NG['vx']) * NG['zn'] / (NG['zn'] - s)
nK = lambda u: NG['kzn'] * (u - NG['vx']) / (NG['uzn'] - NG['vx'])
i = JS.find('const CRW = ') + 12
CRW = json.JSONDecoder().raw_decode(JS[i:])[0]
KZ = J('SOL').get('k', 1.0) if 'const SOL = ' in JS else 1.0   # (la horde et le bus à la taille de ce qui est debout dans la peinture : B x K, tools/zombie_sol.py)
HRD = J('ZH') if 'const ZH = ' in JS else json.JSONDecoder().raw_decode(JS[JS.find('HRD = ', i) + 6:])[0]   # (la horde : ZH, tools/zombie_sheets.py)
BZ = J('BZ')
sB_floor = lambda y: (y - HZ) / EYE_B            # B, debout sur le trottoir (ou le sol d'une boutique au niveau du trottoir)
sB_road = lambda y: (y - HZ) / (EYE_B + 0.15)    # B, debout sur la chaussée


def crew_cell(who, move, i=0):
    C = CRW['heroes'][who]
    n = C['moves'][move][i]['cell']
    L = C['lv'][0]                                   # (sa taille à la porte, x 1 ; plus près, la même, plus grande)
    return [(n % C['cols']) * L['cw'], L['y'] + (n // C['cols']) * L['ch'], L['cw'], L['ch']]


Z_T = float(IRF['Tz'] if 'Tz' in IRF else IRF['T']['z'])
Z_S = float(IRF['W']['from'][1])
Z_E = float(IRF['W']['to'][1])
Z_OA = float(OMF['A']['z'])
k_red = lambda w: (1400 / (ZR['zs'] - w)) / ZR['ppm']
GGK = jsnum(r'box: \[[\d, ]+\], k: ([\d.]+)') or 0.5      # (Gengar : px de la scène par px de sa planche)
CHARS = [
    dict(id='oden_d', nom="maître de l'oden, à la porte", outil='tools/oden_master.py (oden_door.webp : tools/oden_interior.py)',
         asset='oden_master.webp', js='OMF, ODM, stepOdenDoor', modele='A', H=1.70, tete=7.0,
         ref=OMF['D']['stand'], head=11, places=[('dans l\'embrasure, Z %.1f m (A ; seuil %.0f)' % (OMF['D']['z'], OMF['D']['floor']), 1.0, 1400 / OMF['D']['z'] * FIX_A, None)]),
    dict(id='oden_a', nom="maître de l'oden, à la marmite", outil='tools/oden_master.py', asset='oden_master.webp', js='OMF.A', modele='A',
         H=1.70, tete=7.0, ref=OMF['A']['stand'], head=9, places=[('allée, Z %.1f m (A)' % Z_OA, 1.0, 1400 / Z_OA * FIX_A, None)]),
    dict(id='obaa', nom='obaa-chan du dagashi-ya', outil='tools/dagashi_obaachan.py', asset='dagashi_obaachan.webp', js='DGO, OBA, stepOba',
         modele='A', H=1.45, tete=6.5, ref=DGO['cells']['b0'], head=14,
         places=[('derrière le comptoir, Z %.2f m (A)' % DGO['z'], 1.0, DGO['ppm'] * FIX_A, None)]),
    dict(id='red', nom='Red au balcon (zone 1)', outil='tools/red_sheet.py', asset='red_sil.webp', js='ZR, ZRC, ZRB, z1Red', modele='A',
         H=1.65, tete=6.5, ref=[0, ZRC['idle'][0], ZRC['idle'][1], ZRC['idle'][2]], head=27,
         places=[('à l\'arrêt (w 0)', k_red(0), 1400 / ZR['zs'] * FIX_A, None), ('entrée (w %.2f)' % ZR['w0'], k_red(ZR['w0']), 1400 / (ZR['zs'] - ZR['w0']) * FIX_A, None)]),
    dict(id='naruto_win', nom='Naruto à la fenêtre du balcon', outil='tools/naruto_sil.py (sa source : build_zzzchar_naruto.py, hors du dépôt)',
         asset='naruto_sil.webp', js='NG, NC, NAR, nDraw', modele='fenêtre peinte = 2,1 m', H=1.78, tete=7.0, ref=[NCL[1], NCL[0], NCL[1], NCL[2]], head=19,
         places=[('devant la vitre (s -1,5)', nK(nU(-1.5)) / NG['ppm'], nK(nU(-1.5)), None), ('entrée (s -6,2)', nK(nU(-6.2)) / NG['ppm'], nK(nU(-6.2)), None)]),
    dict(id='killua', nom='Killua sur le toit', outil='build_zzzchar_killua.py (hors du dépôt)', asset='killua_body/legs/head.webp',
         js='KM, KIL, stepKillua', modele='la maison (~78 px/m), = B', H=1.58, tete=6.5, ref=None, head=19, seated=58,
         places=[('assis, au bord du toit', 1.0, 78.0, None)]),
    dict(id='teuchi', nom='Teuchi (Ichiraku) — en cours', outil='tools/ichiraku_figures.py', asset='ramen_figures.webp', js='IRF.T, TCH, stepTeuchi',
         modele='A', H=1.78, tete=7.0, ref=IRF['T']['idle'][0] if 'idle' in IRF['T'] else IRF['T']['cells'][0], head=11, full=1.753 * 1400 / Z_T,
         places=[('au comptoir, Z %.2f m (A) ; le comptoir le coupe' % Z_T, 1.0, 1400 / Z_T * FIX_A, None)]),
    dict(id='regular', nom='le client (Ichiraku) qui sort — en cours', outil='tools/ichiraku_figures.py', asset='ramen_figures.webp', js='IRF.W, REG, regWalk',
         modele='A', H=1.82, tete=7.0, ref=IRF['W']['cells'][-1][0], head=14,
         places=[('au tabouret, Z %.2f m' % Z_S, IRF['W']['h0'] / IRF['W']['cells'][-1][0][3], 1400 / Z_S * FIX_A, None),
                 ('à la porte, Z %.2f m' % Z_E, 1.0, 1400 / Z_E * FIX_A, None)]),
    dict(id='naruto_ramen', nom='Naruto au comptoir (Ichiraku) — en cours', outil='tools/ichiraku_figures.py (naruto_ramen.webp)', asset='ramen_figures.webp',
         js='IRF.N, NRM', modele='A', H=0.77, tete=None, ref=IRF['N']['cells'][0], head=None, note='assis : du sommet au coussin (0,53 de 1,45 m)',
         places=[('sur le tabouret, Z %.2f m' % Z_S, 1.0, 1400 / Z_S * FIX_A, None)]),
    dict(id='e33', nom="passant de l'Expédition 33", outil='tools/e33_walkers.py', asset='e33_walkers.webp', js='WKS, WKP, stepE33',
         modele='portes du fond (21 px/m)', H=1.71, tete=7.0, ref=[0, 0, WKS['cw'], WKS['ch']], head=6, person=36,
         places=[('trottoir du fond (rangée 640)', 1.0, sB_floor(640), 640)]),
    dict(id='mathis', nom='Mathis à son bureau (zone 5)', outil='procédural (drawCoder, BONE, POSE)', asset='—', js='ws, RJ, BONE, coderParts',
         modele='plan de la pièce, 19,8 px/m', H=1.75, tete=7.0, ref=None, head=5.5, full=35.0, places=[('dans la pièce', 1.0, sB_floor(638), None)]),
    dict(id='crew', nom="l'équipe (Dempsey ; Nikolai, Takeo, Richtofen pareils)", outil='tools/crew_sheets.py (les planches du propriétaire)', asset='crew_*.webp',
         js='CRW, CSPOT, crewHeroDraw', modele='B', H=1.80, tete=7.0, ref=crew_cell('dempsey', 'walk'), head=7, sheet='crew_dempsey.webp',
         places=[('à l\'arrêt (rangée 649), x K', 1.0, sB_road(649), 649)]),
    dict(id='horde', nom='la horde (niveau 100 px ; 01, chemise blanche)', outil='tools/zombie_sheets.py', asset='horde_L0..L4.webp', js='ZH, crewZDraw, ZRM',
         modele='B', H=1.76, tete=7.5, ref=HRD['L'][1]['frames'][0][0][:4], head=12, sheet='horde_L1.webp',
         places=[('D 17,0 m (rangée %.0f), x K' % (615 + 959.5 * 1.41 / 17.0), 1.76 * KZ * 959.5 / 17.0 / HRD['L'][1]['h'], 959.5 / 17.0, None)]),
    dict(id='horde_pres', nom='la horde, de près (niveau 290 px)', outil='tools/zombie_sheets.py', asset='horde_L3.webp', js='ZH, crewZDraw, ZRM',
         modele='B', H=1.76, tete=7.5, ref=HRD['L'][3]['frames'][0][0][:4], head=34, sheet='horde_L3.webp',
         places=[('D 6,6 m (le bas du cadre), x K', 1.76 * KZ * 959.5 / 6.6 / HRD['L'][3]['h'], 959.5 / 6.6, None)]),
    dict(id='horde_loin', nom='la horde, au carrefour (niveau 42 px)', outil='tools/zombie_sheets.py', asset='horde_L4.webp', js='ZH, crewZDraw, ZRM',
         modele='B', H=1.76, tete=7.5, ref=HRD['L'][4]['frames'][0][0][:4], head=5, sheet='horde_L4.webp',
         places=[('D 44 m, x K', 1.76 * KZ * 959.5 / 44.0 / HRD['L'][4]['h'], 959.5 / 44.0, None)]),
    dict(id='bus_zombie', nom='zombie du bus, à sa fenêtre (01)', outil='tools/zombie_sheets.py', asset='bus_zombies.webp', js='BZ, BZC, busZStep',
         modele='B', H=1.76, tete=7.5, ref=(BZ['Z'][0]['plank'][6][:4] if 'Z' in BZ else [0, 0, 48, 66]), head=5, sheet='bus_zombies.webp',
         places=[('41 m (le bus, rangée 648), x K', 1.0, sB_road(648), None)]),
    dict(id='gengar', nom='Ectoplasma (Gengar) au Centre', outil='— (gengar_shadow.webp)', asset='gengar_shadow.webp', js='GG, stepGengar',
         modele='B', H=1.50, tete=None, ref=[0, 0, 64, 64], head=None, full=48 * GGK, note='Pokédex : 1,5 m ; la vitre de la porte : 32 px, 0,9 m',
         places=[('derrière la porte du Centre (seuil ~660)', GGK, sB_floor(660), None)]),
    dict(id='climber', nom='le grimpeur du Fuji', outil='— (fuji_climber.webp, CLB)', asset='fuji_climber.webp', js='CLB, stepClimber',
         modele='symbole (le sommet du Fuji)', H=None, tete=None, ref=[(20 % 16) * 18, (20 // 16) * 14, 18, 14], head=None, places=[]),
]


def measure(C):
    out = dict(id=C['id'], nom=C['nom'], outil=C['outil'], asset=C['asset'], js=C['js'], modele=C['modele'])
    a = None
    src = C.get('sheet') or C['asset']
    if C['ref'] is not None and src.endswith('.webp') and os.path.exists(A(src)):
        a = cell(img(src), C['ref'])
    if a is not None:
        b = bbox(a[..., 3])
        a = a[b[1]:b[3], b[0]:b[2]]
        out['h_img'] = b[3] - b[1]
        out['tete_auto'] = neck_guess(a[..., 3])
        g = grain(a[..., :3], a[..., 3] >= 128)
        g.update(edge(a))
        out['grain'] = g
    rows = []
    for (pn, k, sB, foot) in C['places']:
        h = C.get('full') or (C.get('person') or out.get('h_img', 0)) * k
        if C.get('seated'):
            h = C['seated'] / 0.52            # (assis : la hauteur du sommet au siège est 0,52 de la taille)
        tgt = C['H'] * sB if C['H'] else None
        hd = C['head'] * k if C['head'] else None
        rows.append(dict(place=pn, k=round(k, 3), sB=round(sB, 1), h=round(h, 1), cible=round(tgt, 1) if tgt else None,
                         ratio=round(h / tgt, 2) if tgt else None, tete=round(hd, 1) if hd else None,
                         tetes=round(h / hd, 1) if hd else None, tete_cible=round(tgt / C['tete'], 1) if (tgt and C['tete']) else None,
                         tete_m=round(hd / sB, 2) if hd else None))   # (sa tête en mètres de B : 0,22-0,25 pour un adulte)
    out['places'] = rows
    return out


def human(H_px, heads=7.5):
    """la silhouette de référence : un homme de H_px, heads têtes de haut"""
    h = H_px / heads
    im = Image.new('RGBA', (int(H_px * 0.32) + 4, int(H_px) + 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx = im.width / 2
    col = (230, 230, 240, 255)
    d.ellipse([cx - h * 0.38, 0, cx + h * 0.38, h], fill=col)
    d.rectangle([cx - h * 0.12, h * 0.9, cx + h * 0.12, h * 1.25], fill=col)
    d.polygon([(cx - h * 0.95, h * 1.25), (cx + h * 0.95, h * 1.25), (cx + h * 0.7, h * 3.9), (cx - h * 0.7, h * 3.9)], fill=col)
    d.polygon([(cx - h * 0.7, h * 3.8), (cx - h * 0.08, h * 3.8), (cx - h * 0.15, H_px), (cx - h * 0.6, H_px)], fill=col)
    d.polygon([(cx + h * 0.08, h * 3.8), (cx + h * 0.7, h * 3.8), (cx + h * 0.6, H_px), (cx + h * 0.15, H_px)], fill=col)
    d.polygon([(cx - h * 0.95, h * 1.3), (cx - h * 1.25, h * 1.35), (cx - h * 1.1, h * 4.0), (cx - h * 0.8, h * 4.0)], fill=col)
    d.polygon([(cx + h * 0.95, h * 1.3), (cx + h * 1.25, h * 1.35), (cx + h * 1.1, h * 4.0), (cx + h * 0.8, h * 4.0)], fill=col)
    return im


def sheet_b(res, path, ppm=80.0):
    """chaque figure à la même échelle (ppm px par mètre de B) à côté d'un homme de 1,70 m (7,5 têtes) ; à gauche de chacune,
    en jaune, la tête qu'elle devrait avoir (sa taille voulue / ses têtes voulues), posée au haut de sa tête"""
    tiles = [('homme 1,70 m', '7,5 tetes', '', human(1.70 * ppm), 1.70 / 7.5)]   # (la police par défaut : sans accents)
    for C, R in res:
        if C['ref'] is None or not R['places'] or not C['H']:
            continue
        sheet = C.get('sheet') or C['asset']
        if not sheet.endswith('.webp') or not os.path.exists(A(sheet)) or C.get('full') and C['id'] != 'gengar':
            continue
        a = cell(img(sheet), C['ref'])
        b = bbox(a[..., 3])
        a = a[b[1]:b[3], b[0]:b[2]]
        P = R['places'][0]
        f = P['k'] / P['sB'] * ppm                 # (px de l'image -> px de la planche : sa taille à l'écran, rapportée à B)
        if C.get('person'):
            f = P['h'] / C['person'] / P['sB'] * ppm
        if C['id'] == 'gengar':
            f = P['h'] / a.shape[0] / P['sB'] * ppm
        im = Image.fromarray(a)
        w, h = max(1, round(im.width * f)), max(1, round(im.height * f))
        im = im.resize((w, h), Image.NEAREST)
        if a[..., :3].max() < 8 or C['id'] == 'gengar':        # (une silhouette : en gris pour qu'elle se lise)
            arr = np.asarray(im).copy()
            arr[..., :3] = 90
            im = Image.fromarray(arr)
        hd = (C['H'] / C['tete']) if C.get('tete') else None
        tiles.append((C['id'], '%.0f %% de la cible' % (100 * P['ratio']), '%.2f m, tete %s' % (P['h'] / P['sB'], ('%.2f m' % P['tete_m']) if P.get('tete_m') else '-'), im, hd))
    W = sum(max(t[3].width, 110) + 24 for t in tiles) + 70
    Hh = int(2.15 * ppm) + 70
    can = Image.new('RGBA', (W, Hh), (52, 50, 62, 255))
    d = ImageDraw.Draw(can)
    ground = Hh - 52
    for m in (0.5, 1.0, 1.45, 1.70, 2.0):              # les tailles de référence
        y = ground - m * ppm
        d.line([(0, y), (W, y)], fill=(150, 110, 110, 255) if m == 1.70 else (88, 86, 108, 255))
        d.text((2, y - 11), '%.2f m' % m, fill=(180, 180, 200, 255))
    x = 70
    for (lab, l2, l3, im, hd) in tiles:
        top = int(ground - im.height)
        can.alpha_composite(im, (x + 8, top))
        if hd:                                          # la tête voulue, en jaune, au haut de la figure
            d.rectangle([x, top, x + 3, top + hd * ppm], fill=(230, 190, 70, 255))
        d.text((x, ground + 4), lab, fill=(240, 240, 240, 255))
        d.text((x, ground + 18), l2, fill=(240, 200, 120, 255))
        d.text((x, ground + 32), l3, fill=(190, 190, 210, 255))
        x += max(im.width, 110) + 24
    can = can.resize((can.width * 2, can.height * 2), Image.NEAREST)
    can.save(path)


# ---- les captures : (capture, boîte de la figure, boîte de la peinture voisine pour le grain ou None[, zoom de la planche a, 4 par défaut])
SHOTS = {
    'oden_d': ('p1_a.png', (414, 590, 470, 682), (466, 600, 522, 692)),
    'oden_a': ('p1_c.png', (440, 556, 500, 640), None),
    'obaa': ('p2_up.png', (140, 575, 225, 680), (225, 585, 300, 680)),
    'obaa_assise': ('p2_base.png', (172, 605, 228, 660), None),
    'obaa_etagere': ('p2_reach.png', (140, 565, 200, 680), None),
    'red': ('p1_a.png', (955, 260, 1012, 366), None),
    'naruto_win': ('p1_a.png', (1180, 120, 1275, 300), None),
    'killua': ('p1_a.png', (282, 128, 362, 232), (230, 150, 290, 232)),
    'ichiraku': ('p1_a.png', (1148, 560, 1236, 720), None),
    'regular': ('p1_c.png', (1148, 560, 1236, 745), None),
    'e33': ('p1_a.png', (598, 594, 660, 646), (660, 594, 722, 646)),
    'e33_retour': ('p1_d.png', (690, 594, 752, 646), None),
    'climber': ('p1_a.png', (600, 244, 645, 276), None),
    'drone': ('p1_c.png', (888, 708, 940, 752), None),
    'cat': ('p1_a.png', (822, 618, 848, 642), None),
    'crew': ('p3_a.png', (770, 590, 880, 660), (660, 590, 770, 660)),
    'horde': ('p3_c.png', (900, 600, 1200, 816), None, 2),
    'horde_far': ('p3_a.png', (860, 600, 1020, 720), None, 2),
    'bus': ('p3_a.png', (500, 540, 880, 660), None, 2),
    'gengar': ('p4_gengar.png', (850, 570, 912, 640), None),
    'mathis': ('p6_mathis.png', (508, 498, 602, 558), (508, 440, 602, 498)),
}


def sheets_from_shots(shots, out):
    tiles = []
    for k, v in SHOTS.items():
        f, box, z = v[0], v[1], (v[3] if len(v) > 3 else 4)
        p = os.path.join(shots, f)
        if not os.path.exists(p):
            continue
        im = Image.open(p).convert('RGB').crop(box)
        tiles.append(('%s (x%d)' % (k, z), im.resize((im.width * z, im.height * z), Image.NEAREST)))
    if tiles:
        cols, x, y, rowh, W = [], 0, 0, 0, 1800
        place = []
        for k, t in tiles:
            if x + t.width > W:
                x, y, rowh = 0, y + rowh + 22, 0
            place.append((k, t, x, y))
            x += t.width + 8
            rowh = max(rowh, t.height)
        can = Image.new('RGB', (W, y + rowh + 22), (24, 22, 30))
        d = ImageDraw.Draw(can)
        for k, t, x, y in place:
            can.paste(t, (x, y + 18))
            d.text((x + 2, y + 2), k, fill=(240, 220, 120))
        can.save(os.path.join(out, 'sheet_a_in_place.png'))
    tiles = []
    for k, v in SHOTS.items():
        f, box, pb = v[:3]
        p = os.path.join(shots, f)
        if pb is None or not os.path.exists(p):
            continue
        im = Image.open(p).convert('RGB')
        a, b = im.crop(box), im.crop(pb)
        h = max(a.height, b.height)
        t = Image.new('RGB', ((a.width + b.width) * 6 + 12, h * 6 + 20), (24, 22, 30))
        t.paste(b.resize((b.width * 6, b.height * 6), Image.NEAREST), (0, 20))
        t.paste(a.resize((a.width * 6, a.height * 6), Image.NEAREST), (b.width * 6 + 12, 20))
        ImageDraw.Draw(t).text((4, 4), k + ' : la peinture voisine | la figure (x6)', fill=(240, 220, 120))
        tiles.append(t)
    if tiles:
        W = max(t.width for t in tiles)
        can = Image.new('RGB', (W, sum(t.height + 10 for t in tiles)), (24, 22, 30))
        y = 0
        for t in tiles:
            can.paste(t, (0, y))
            y += t.height + 10
        can.save(os.path.join(out, 'sheet_c_grain.png'))


# ---- la peinture autour des figures (layer_city_off.webp), pour le grain
PAINT = {
    'porte et façade de l\'oden': (420, 576, 464, 677), 'distributeur proche': (282, 548, 300, 724),
    'portes basses d\'Ichiraku': (1155, 640, 1230, 740), 'porte rose (zone 1)': (1075, 506, 1115, 722),
    'maisons du fond (trottoir du fond)': (560, 570, 640, 640), 'façade de la zone 9': (770, 560, 860, 640),
    'toit et mur sous Killua': (230, 170, 330, 260), 'pied du poteau': (1023, 600, 1064, 750), 'banc': (350, 640, 395, 700),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='/tmp/figures_audit')
    ap.add_argument('--shots', default=None)
    ap.add_argument('--only', default=None)
    o = ap.parse_args()
    os.makedirs(o.out, exist_ok=True)
    print('## La caméra : la hauteur de l\'œil (au-dessus du trottoir) que donne chaque repère peint')
    print('| repère | rangée du pied | px | réel (m) | œil (m) |\n|---|---|---|---|---|')
    for c in CUES:
        print('| %s | %.1f | %.1f | %.2f | %.2f |' % (c[0], c[2], c[3], c[4], implied_eye(c)))
    print('\nA : %.2f m ; B : %.2f m ; une figure placée par A doit faire x%.3f\n' % (EYE_A, EYE_B, FIX_A))
    res = []
    sel = o.only.split(',') if o.only else None
    print('## Les figures\n| figure | place | k | px/m (B) | h (px) | cible (px) | h/cible | tête (px) | têtes | tête cible | tête (m de B) |\n|---|---|---|---|---|---|---|---|---|---|---|')
    for C in CHARS:
        if sel and C['id'] not in sel:
            continue
        R = measure(C)
        res.append((C, R))
        for P in R['places']:
            print('| %s | %s | %.3f | %.1f | %.1f | %s | %s | %s | %s | %s | %s |' % (C['id'], P['place'], P['k'], P['sB'], P['h'], P['cible'], P['ratio'], P['tete'], P['tetes'], P['tete_cible'], P['tete_m']))
    print('\n## Le grain des figures (leur image de référence)\n| figure | couleurs | familles (90 %) | tache | isolés | pas | doux | alpha partiel | anneau | L 5/50/95 | tête auto |\n|---|---|---|---|---|---|---|---|---|---|---|')
    for C, R in res:
        g = R.get('grain')
        if g:
            print('| %s | %d | %d (%d) | %.1f | %.2f | %.1f | %.2f | %.2f | %.2f | %d/%d/%d | %s |' % (C['id'], g['uniq'], g['fam'], g['fam90'], g['tache'], g['isole'], g['pas'], g['doux'], g['alpha_part'], g['anneau'], g['L5'], g['L50'], g['L95'], R.get('tete_auto')))
    paint = np.asarray(Image.open(A('layer_city_off.webp')).convert('RGB'))
    print('\n## Le grain de la peinture (layer_city_off.webp)\n| boîte | couleurs | familles (90 %) | tache | isolés | pas | doux | L 5/50/95 |\n|---|---|---|---|---|---|---|---|')
    pg = {}
    for k, (x0, y0, x1, y1) in PAINT.items():
        g = grain(paint[y0:y1, x0:x1])
        pg[k] = g
        print('| %s | %d | %d (%d) | %.1f | %.2f | %.1f | %.2f | %d/%d/%d |' % (k, g['uniq'], g['fam'], g['fam90'], g['tache'], g['isole'], g['pas'], g['doux'], g['L5'], g['L50'], g['L95']))
    json.dump(dict(cues=[dict(c=c[0], eye=round(implied_eye(c), 3)) for c in CUES], figures=[R for _, R in res], peinture=pg),
              open(os.path.join(o.out, 'figures_audit.json'), 'w'), ensure_ascii=False, indent=1)
    sheet_b(res, os.path.join(o.out, 'sheet_b_proportions.png'))
    if o.shots:
        sheets_from_shots(o.shots, o.out)
    print('\n(écrit dans %s)' % o.out, file=sys.stderr)


if __name__ == '__main__':
    main()
