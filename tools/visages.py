#!/usr/bin/env python3
"""(un module) Les visages des figures, dessinés à la main pixel par pixel : de petits gabarits par pose, en lettres, posés sur
la boîte du visage que chaque outil trouve (tools/dagashi_obaachan.py, tools/oden_master.py).

À ces tailles (9 à 16 px de tête) un visage ne se réduit pas : chercher les traits sur une planche dessinée au huitième et les
poser au pixel qu'ils couvrent le plus fait des yeux trop écartés, une bouche trop basse, un nez seul au milieu, des lunettes en
bandeau. Les gabarits suivent les conventions du pixel art : d'abord le volume (la peau claire du côté de la lumière, l'ombre
de l'autre, l'ombre sous le menton là où la tête rencontre le col, l'ombre des cheveux sur le front et les tempes), puis les
yeux (un pixel chacun, sur une même rangée, symétriques autour du milieu du visage, de la couleur sombre des cheveux et des
yeux, jamais noirs ; de trois quarts et de profil poussés vers le côté où il se tourne), la bouche (au repos, rien ou un pixel
de peau un peu plus sombre et plus rouge ; un rouge chaud sombre pour le rire, jamais une barre brune), le nez seulement
suggéré (un pixel de l'ombre de la peau, du côté de l'ombre, juste sous les yeux). Les expressions changent un ou deux pixels du
même gabarit.

Un gabarit : (coin, rangées). Les rangées : un texte, une rangée par ligne, « forme | marques » (deux chaînes de même longueur ;
sans marques, la forme seule), les lignes vides et les blancs du début ignorés. Le coin dit quel coin de la boîte du visage
tient le gabarit : 'tl' en haut à gauche (sa première lettre sur le premier pixel de la boîte), 'tr' en haut à droite, 'bl' en
bas à gauche, 'br' en bas à droite (sa dernière rangée sur la dernière de la boîte, sa dernière colonne sur la sienne) ; le coin
qui bouge le moins d'une pose à l'autre du même visage. La forme (toujours posée) :
    .  rien (le pixel reste celui de la figure)
    L  la peau éclairée          M  la peau          S  la peau à l'ombre          D  l'ombre profonde (sous le menton, la
    H  les cheveux à l'ombre (le bord qui encadre le visage)                              lisière des cheveux)
    (L, M, S, D : sur la peau de la figure seulement ; un cheveu sous eux reste un cheveu)
Les marques (posées sur la forme, chacune à partir d'une variante ; avant, le pixel garde sa forme) :
    sobre   E  un œil ouvert      e  un œil fermé (un sombre plus clair)      g  le reflet d'un verre (plus clair)
            O  la bouche qui rit (un rouge chaud sombre)                      B  l'ombre du sourcil sous le bandeau
    moyen   m  la bouche au repos (la peau un peu plus sombre et plus rouge)  o  la bouche ouverte (l'éventail, le bonbon)
            r  le bord extérieur d'un verre (un ton moyen)                    u  le sourire (un pixel)
            b  la barbe : la mâchoire un peu plus sombre et plus froide
    detail  n  l'ombre du nez     c  la chaleur des joues      k  la courbe d'un œil fermé (son second pixel)
            q  le bord d'un verre (moyen), la courbe de l'œil fermé sous lui (detail)
Chaque outil donne la couleur de chaque rôle (ses propres familles de tons) ; ce module ne fait que lire les gabarits.
"""

LEVELS = ('sobre', 'moyen', 'detail')
FORM = {'L': 'lit', 'M': 'mid', 'S': 'shade', 'D': 'deep', 'H': 'hair'}
SKIN = ('lit', 'mid', 'shade', 'deep')   # (la forme de la peau : sur la peau seulement, la silhouette reste celle de la planche)
MARKS = {'E': ('eye',) * 3, 'e': ('shut',) * 3, 'g': ('glint',) * 3, 'O': ('laugh',) * 3, 'B': ('brow',) * 3,
         'm': (None, 'mouth', 'mouth'), 'o': (None, 'open', 'open'), 'r': (None, 'rim', 'rim'), 'u': (None, 'smile', 'smile'),
         'b': (None, 'stubble', 'stubble'), 'n': (None, None, 'nose'), 'c': (None, None, 'cheek'), 'k': (None, None, 'shut'),
         'q': (None, 'rim', 'shut')}   # (chaque marque : son rôle en sobre, moyen, detail ; None : la forme)


def level(face):
    assert face in LEVELS, 'FACE : %s ?' % face
    return LEVELS.index(face)


def rows(text):
    """les rangées d'un gabarit écrit en texte : [(forme, marques)]"""
    out = []
    for ln in text.strip('\n').split('\n'):
        ln = ln.strip()
        if not ln: continue
        f, _, m = ln.partition('|')
        f, m = f.strip(), m.strip()
        out.append((f, m or '.' * len(f)))
    return out


def pixels(tpl, box, face):
    """les pixels d'un gabarit posé sur la boîte du visage (x0, y0, x1, y1 : x1, y1 compris) à la variante face : {(x, y): rôle}"""
    corner, rows_ = tpl
    rows_ = rows(rows_) if isinstance(rows_, str) else rows_
    lv = level(face)
    w, h = len(rows_[0][0]), len(rows_)
    x0 = box[0] if corner[1] == 'l' else box[2] - w + 1
    y0 = box[1] if corner[0] == 't' else box[3] - h + 1
    out = {}
    for i, (form, marks) in enumerate(rows_):
        assert len(form) == len(marks) == w, 'gabarit : rangée %d de %d et %d lettres, pas %d' % (i, len(form), len(marks), w)
        for j, (f, m) in enumerate(zip(form, marks)):
            role = FORM.get(f)
            assert role or f == '.', 'gabarit : forme %r ?' % f
            if m != '.':
                assert m in MARKS, 'gabarit : marque %r ?' % m
                role = MARKS[m][lv] or role
            if role: out[(x0 + j, y0 + i)] = role
    return out


def forms(tpl):
    """la forme seule d'un gabarit (pour vérifier que deux poses du même visage ont la même)"""
    r = rows(tpl[1]) if isinstance(tpl[1], str) else tpl[1]
    return tpl[0], tuple(f for f, _ in r)
