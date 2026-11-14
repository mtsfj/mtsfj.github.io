#!/usr/bin/env python3
"""The kept retouches, laid into the street's own layers (the owner's choice among the clean pass's alternatives, branch
agent/clean, tools/relief.py and tools/alt_*.py there): the drinks machines (vend); and the model clean-ups written by
tools/redraw_zones.py: the rooftop unit's fan (fan) and Ichiraku's front with its new signboard (ramen) its door (door) and the plaster below (base); the dojo's front (dojo); the oden's front (oden); the tobacco kiosk's plates and planks (kiosk, kiosktop), its cabin shut (kiosk: its lit cabin is the comp win_z7_kiosk); the Pokemon Center's ball sign without its rim, shut (pokeball: lit, the comp z4_emblem); the ground floors behind the right pole, its two lit entrances (pole, after Ichiraku's: it overlaps them); the apartment building left of it, its ground floor a shop window (bfloor), its front one plaster (bwall); the dojo's foot, its post and the gap beside it (dojofoot); Ichiraku's door bottoms and its wall's foot (ichifoot); a far window behind the railing (farwin); the navy shadows by the arcade (arcgap); the house at the street's end, its paper lantern (z9lan: lit, the comp win_z9_lantern) and its upstairs window and railing (z9win: lit, the comp win_z9_window; after the Pokemon Center's ball, whose box it overlaps); the right pole's foot planted in the sidewalk (polefoot, after pole and bfloor: it overlaps them); the dagashi-ya's room shut for the night, its cooler left on (dagashi: lit, its comp win_z7_shop); the arcade's low roof under the rooftop unit, its tiles, the unit's stand and a gutter (arceave); the end house's ground floor, its lattice window and sliding doors on the painter's light, the lantern's light on them a soft pool (z9base: lit, the comp win_z9_lantern; after z9lan, whose box it overlaps); Ichiraku's menu board taken away, its plaster run through (board, last: it overlaps base and pole); the right pole's concrete, its bands, bolt and conduits (poletex: also the rim's sun mask, street_sun.webp; after pole, bfloor, bwall and polefoot, which it overlaps) and the street lamp it carries, its arm, bracket and head (polelamp: lit, the comp lamp.webp; also night_far.webp); Naruto's floor over Ichiraku, its window, railing, walls and slabs (narufloor, after ramen and arceave: it overlaps them); the end house's ground floor, its frosted glass window and sliding lattice doors on the painter's light, the lantern's light on them a soft pool (z9base: lit, the comp win_z9_lantern; after z9lan, whose box it overlaps); the drinks corner; Ichiraku's menu board taken away, its plaster run through (board: it overlaps base and pole); the narrow building between the Pokemon Center and the apartment building, one plaster, its top a flat roof edge (awall, after pokeball, bfloor and bwall: it overlaps them); Naruto's floor over Ichiraku, its window, railing, walls and slabs, the roof's edge over it and its downpipes (narufloor, after ramen, fan and arceave: it overlaps them); the roofs on the left, Kirua's eave and the dojo's, old tiles and a clean gutter in the street's perspective, their downpipes fed by swan necks (eaveKs, eaveK1..K5, eaveD, eaveP: EAVES); the canopy over the pink-lit entrance right of the pole and the corner with Ichiraku (canopy, after pole, ramen, door and poletex: it overlaps them); the buildings' tops, each its real parts (topB, topC, topPC, topEnd, topOden, topOdenShop: TOPS, tools/building_tops.py); the narrow building between the Pokemon Center and the apartment building taken away, a roji in its place, its lamp's lit comp z5_alley (alley, after pokeball, bfloor and bwall: it overlaps them)..K5, eaveD, eaveP: EAVES); the canopy over the pink-lit entrance right of the pole and the corner with Ichiraku (canopy, after pole, ramen, door and poletex: it overlaps them); the tops of the two buildings on the right, Naruto's parapet and coping, its downpipe, the arcade's tiled eave and boards (naruroof, last: over narufloor, fan, arceave and ramen).
; redrawn whole by tools/soda_corner.py, the kiosk's tiled lean-to, the machines, the kiosk's front (soda: last, over vend,.
    python3 tools/bake_retouches.py

Each patch (tools/src/retouches/) replaces the layer's pixels at its place, alpha included (as the street laid it on the GPU):
layer_city_off.webp and street_unlit.webp take vend at (282, 523), fan at (1296, 160), ramen at (1090, 290), door at (1100, 390) base at (1100, 530), dojo at (0, 400), oden at (390, 462), kiosk at (224, 560) with its upper planks at (224, 420), pokeball at (838, 440), pole at (990, 425), bfloor at (880, 415), bwall at (940, 60), dojofoot at (0, 440), ichifoot at (1150, 676), farwin at (640, 622), arcgap at (1265, 410), z9lan at (796, 572), z9win at (800, 496) and polefoot at (995, 690), dagashi at (142, 525), arceave at (1232, 262), z9base at (760, 566), board at (1110, 548), poletex at (1005, 44), polelamp at (845, 128), narufloor at (1120, 0), soda at (227, 405), alley at (904, 300), recess at (1065, 452), naruroof at (1120, 0), arcsign at (1320, 356), entree at (1050, 440), hall at (1066, 500), hallB at (975, 520); z7_vending.webp (the machines' lit
comp, now 91 x 205 at 280, 522) and z7_vendoff.webp (their stutter, 23 x 166 at 307, 552) are the patches themselves. Lossless,
; (vend_z7_*.webp, written by tools/soda_corner.py, the zone soda of tools/redraw_zones.py). Lossless,.exact: run again after a tool rewrites a layer (build_zzzsec_unlit.py ...), then the ?v= of what changed and tools/poster.py.
"""
import os
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'tools', 'src', 'retouches')
LAYERS = {'layer_city_off.webp': [('vend_city.webp', 282, 523), ('fan_city.webp', 1296, 160), ('ramen_city.webp', 1090, 290), ('door_city.webp', 1100, 390), ('base_city.webp', 1100, 530), ('dojo_city.webp', 0, 400), ('oden_city.webp', 390, 462), ('kiosk_city.webp', 224, 560), ('kiosktop_city.webp', 224, 420), ('pokeball_city.webp', 838, 440), ('pole_city.webp', 990, 425), ('bfloor_city.webp', 880, 415), ('bwall_city.webp', 940, 60), ('dojofoot_city.webp', 0, 440), ('ichifoot_city.webp', 1150, 676), ('farwin_city.webp', 640, 622), ('arcgap_city.webp', 1265, 410), ('z9lan_city.webp', 796, 572), ('z9win_city.webp', 800, 496), ('polefoot_city.webp', 995, 690), ('dagashi_city.webp', 142, 525), ('arceave_city.webp', 1232, 262), ('z9base_city.webp', 760, 566), ('board_city.webp', 1110, 548), ('poletex_city.webp', 1005, 44), ('polelamp_city.webp', 845, 128), ('narufloor_city.webp', 1120, 0), ('soda_city.webp', 227, 405), ('alley_city.webp', 904, 300), ('recess_city.webp', 1065, 452), ('naruroof_city.webp', 1120, 0), ('arcsign_city.webp', 1320, 356), ('entree_city.webp', 1050, 440), ('hall_city.webp', 1066, 500), ('hallB_city.webp', 975, 520)],
          'street_unlit.webp': [('vend_unlit.webp', 282, 523), ('fan_unlit.webp', 1296, 160), ('ramen_unlit.webp', 1090, 290), ('door_unlit.webp', 1100, 390), ('base_unlit.webp', 1100, 530), ('dojo_unlit.webp', 0, 400), ('oden_unlit.webp', 390, 462), ('kiosk_unlit.webp', 224, 560), ('kiosktop_unlit.webp', 224, 420), ('pokeball_unlit.webp', 838, 440), ('pole_unlit.webp', 990, 425), ('bfloor_unlit.webp', 880, 415), ('bwall_unlit.webp', 940, 60), ('dojofoot_unlit.webp', 0, 440), ('ichifoot_unlit.webp', 1150, 676), ('farwin_unlit.webp', 640, 622), ('arcgap_unlit.webp', 1265, 410), ('z9lan_unlit.webp', 796, 572), ('z9win_unlit.webp', 800, 496), ('polefoot_unlit.webp', 995, 690), ('dagashi_unlit.webp', 142, 525), ('arceave_unlit.webp', 1232, 262), ('z9base_unlit.webp', 760, 566), ('board_unlit.webp', 1110, 548), ('poletex_unlit.webp', 1005, 44), ('polelamp_unlit.webp', 845, 128), ('narufloor_unlit.webp', 1120, 0), ('soda_unlit.webp', 227, 405), ('alley_unlit.webp', 904, 300), ('recess_unlit.webp', 1065, 452), ('naruroof_unlit.webp', 1120, 0), ('arcsign_unlit.webp', 1320, 356), ('entree_unlit.webp', 1050, 440), ('hall_unlit.webp', 1066, 500), ('hallB_unlit.webp', 975, 520)]}
COPIES = {'z7_vending.webp': 'vend_z7_vending.webp', 'z7_vendoff.webp': 'vend_z7_vendoff.webp'}
# the roofs on the left (tools/left_eaves.py, by tools/redraw_zones.py's zones of the same names): Kirua's eave along its
# slope and round both its corners, the dojo's eave's end and its downpipe by its corner; each at its box's corner
EAVES = [('eaveKs', 141, 50), ('eaveK1', 206, 56), ('eaveK2', 236, 90), ('eaveK3', 266, 123), ('eaveK4', 296, 157),
         ('eaveK5', 322, 186), ('eaveD', 100, 0), ('eaveP', 128, 50)]
for _layer, _tag in (('layer_city_off.webp', 'city'), ('street_unlit.webp', 'unlit')):
    LAYERS[_layer] += [(f'{n}_{_tag}.webp', x, y) for n, x, y in EAVES]
# the buildings' tops (tools/building_tops.py, by tools/redraw_zones.py's zones of the same names): the apartment block's
# parapet and penthouse behind the pole, the narrow building's top on its ray, the Pokemon Center's coping, the end house's
# gable, the roof garden across the crossroads, the oden's roof; each at its box's corner, laid last (over the zones
# whose boxes they overlap)
TOPS = [('topB', 942, 40), ('topC', 1065, 30), ('topPC', 884, 436), ('topEnd', 752, 434), ('topOden', 486, 424),
        ('topOdenShop', 455, 478)]
for _layer, _tag in (('layer_city_off.webp', 'city'), ('street_unlit.webp', 'unlit')):
    LAYERS[_layer] += [(f'{n}_{_tag}.webp', x, y) for n, x, y in TOPS]
# the windows round the right pole given their depth (tools/window_depth.py, by tools/redraw_zones.py's zones winB and
# winC): B's balcony door and the window under it with their balconies, C's two windows and their sills
WINDOWS = [('winB', 944, 205), ('winC', 1074, 112)]
for _layer, _tag in (('layer_city_off.webp', 'city'), ('street_unlit.webp', 'unlit')):
    LAYERS[_layer] += [(f'{n}_{_tag}.webp', x, y) for n, x, y in WINDOWS]


def main():
    for layer, patches in LAYERS.items():
        path = os.path.join(ROOT, 'assets', layer)
        a = np.array(Image.open(path).convert('RGBA'))
        for f, x, y in patches:
            p = np.array(Image.open(os.path.join(SRC, f)).convert('RGBA'))
            a[y:y + p.shape[0], x:x + p.shape[1]] = p
        if (np.array(Image.open(path).convert('RGBA')) == a).all():
            print(layer, 'already has them'); continue
        Image.fromarray(a, 'RGBA').save(path, 'WEBP', lossless=True, quality=100, method=6, exact=True)
        print(layer, 'laid:', ', '.join(f for f, _, _ in patches))
    for dst, src in COPIES.items():
        b = open(os.path.join(SRC, src), 'rb').read(); path = os.path.join(ROOT, 'assets', dst)
        if not os.path.exists(path) or open(path, 'rb').read() != b:
            open(path, 'wb').write(b); print(dst, 'from', src)


if __name__ == '__main__':
    main()
