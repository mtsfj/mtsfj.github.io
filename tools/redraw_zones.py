#!/usr/bin/env python3
"""Clean-ups of the street drawn by an image-editing model, laid back into the painting (the owner's choice, package
clean-3): each zone's model output (tools/src/edits/<zone>_model.webp, from <zone>_prompt.txt) is brought back to the
painting's pixels and written as patches for tools/bake_retouches.py.

    python3 tools/redraw_zones.py            writes tools/src/retouches/<zone>_{city,unlit}.webp, the neon's glow texture
                                            and the closed shop's overlay (assets/shop_off.webp)
    python3 tools/redraw_zones.py --call Z   asks the model again for zone Z (OpenRouter, the key from the environment's
                                            vault or OPENROUTER_API_KEY), then rewrites everything; costs about 0.14 $

Always from the painter's own pixels (tools/src/edits/<zone>_before_{city,unlit}.webp, the layers before any edit), never
from layers already edited, so a second run writes the same bytes. Per zone:
- the model saw the crop brightened (255 (x/255)^0.5, enlarged with nearest pixels); its answer is boxed down to the
  painting's grid and darkened back (^2), then registered by the integer shift whose gradients best match the
  untouched surroundings (the model may move things by a pixel or two);
- each part of the zone is a polygon with its method:
    hist    the model's structure (its ranks), the painter's values (per-channel histogram matching inside the polygon):
            the painter's palette and value range, nothing else of the model's colours;
    detail  the painter's light, shading and colour (low frequencies, gaussian SIGMA, computed without the polygons of
            `fill`, which are filled from around them: what is removed there, like a smear, leaves no light behind) carry
            the model's fine structure (its luminance minus its own low frequencies, times K) in the painter's hue;
            `keep_lit` keeps the painter's crisp lit strokes as painted; `tex` takes the fine structure from beside where
            an object is taken away (a board: its wall run on through);
    copy    the painter's own pixels from beside (`src`: dx, dy), to continue a pavement where an object stood;
    tool    a drawing made on the pixel grid by a module of its own (`tool`: tools/<tool>.py, its draw()), no model;
    direct  the model's pixels, their global tint brought back to the painting's (a per-channel line fitted on the
            surroundings); with `neon` they are split into the board as it is unlit (the base, in both layers) and the
            light the tubes add (the glow texture, additive, which street.js switches with the shop, the power and the
            red night): lit, base + glow is the model's picture; out, only the base;
    night   a lit window's room shut for the night (night_room, no drawing asked for): its comp's lit picture darkened as
            the painter darkens a shut neighbour, one light left on in it (the dagashi-ya's cooler), out in the power cut;
            what is what in the room from its own tool's model (room_model: tools/dagashi_interior.py);
- the unlit layer (the power cut) takes the same change as a ratio (unlit x new / old), the direct parts their base;
  `unlit='lf_ratio'` (the places that shut): the new picture times the painter's darkening, smoothed channel by channel.
The overlays street.js lays on a zone follow it (R10): the closed shop's (shop_off), the oden's lantern frames and its
door's sliding leaf (oden_overlays: from tools/src/edits/<name>_before.webp; after tools/oden_interior.py rewrites
assets/oden_door.webp, copy it there and run this again); a lit window's comp (the kiosk's win_z7_kiosk, `comp` and
`lit` parts: its new lit picture in the comp, the street under it the same darkened as the painter's shut one); a figure
in a room shut by `night` (the dagashi-ya's obaa-chan, `atlas`: her dark row, seen in a power cut while the shop is open,
in the same dark; from tools/src/edits/dagashi_obaachan_before.webp: after tools/dagashi_obaachan.py rewrites
assets/dagashi_obaachan.webp, copy it there and run this again; after tools/dagashi_interior.py, its zone's before crops
and dagashi_comp_before.webp too).
"""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter, binary_dilation

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDITS = os.path.join(ROOT, 'tools', 'src', 'edits')
OUT = os.path.join(ROOT, 'tools', 'src', 'retouches')
GAMMA = 2.0
VP = (700.0, 615.0)                            # the street's vanishing point (measured on the painting)
MODEL = 'google/gemini-3-pro-image'

ODEN_LANTERN = dict(warm=(398, 536, 424, 573))                    # the oden's paper lantern at rest (it swings: oden_lantern*)
def ray(x, v):
    """The row of the ray v at column x: a line on a right facade running to VP (v = (615 - y) / (x - 700), as
    tools/zone5_facades.py: its ledges, the foot of its walls at v = -0.283)."""
    return VP[1] - v * (x + 0.5 - VP[0]) - 0.5


def circle(cx, cy, r, n=48):
    """A round polygon (a sign seen face on)."""
    return [(cx + r * np.cos(2 * np.pi * i / n), cy + r * np.sin(2 * np.pi * i / n)) for i in range(n)]


BOARD = [(1121, 566), (1152, 566), (1152, 655), (1121, 655)]   # Ichiraku's menu board and the ring round it (board; edges inclusive)
ODEN_UNDER_BOX = [(468, 661), (485, 661), (485, 670), (468, 670)]   # the pavement under the box removed from the oden's front
ODEN_KEEP = [ODEN_LANTERN, dict(rect=(409, 536, 412, 542)),          # and its hook
             dict(rect=(424, 579, 460, 620)), dict(rect=(467, 564, 495, 619))]   # the door's and the window's glass (oden_interior)
ODEN_BOARD = [(475, 482), (510, 482), (510, 540), (475, 528)]       # its roof light box (oden_sign_*: the light it loses, exact)
# what street.js lays over the oden (R10) and copies its wall into: the lantern's frames (the wall behind it where it
# hung at rest) and the door's sliding leaf (its painted wooden bottom, resampled at each step: tools/oden_interior.py);
# their pixels that are the painter's wall take the same change as the layer under them
ODEN_OVL = dict(lantern=[('oden_lantern', 'city'), ('oden_lantern_off', 'unlit')], lantern_box=(390, 528, 46, 56), lantern_n=23,
                lantern_hook=(410.31, 537.0), lantern_angles=[-7.5 + 0.5 * i for i in range(23)],   # (street.js ODEN.lantern)
                door='oden_door', pan_box=(421, 580, 40, 91), pan_wood=621,   # (its wood: below the glass, y 621)
                pan_cells=[[0, 122], [41, 122], [82, 122], [0, 214], [41, 214], [82, 214], [0, 306], [41, 306], [82, 306],
                           [0, 398], [41, 398], [82, 398], [0, 490], [41, 490], [82, 490], [0, 582], [41, 582]])
# the right pole as street.js traces it (COCC.pole: rows y0..y1, columns x0..x1, from the painting): what stands in front
# of a zone redrawn whole behind it (`front`), laid back over the drawing as painted
POLE_RUNS = [[50, 52, 1026, 1063], [53, 53, 1024, 1063], [54, 57, 1023, 1063], [58, 65, 1025, 1063], [66, 90, 1025, 1064],
             [91, 93, 1024, 1064], [94, 454, 1023, 1064], [455, 529, 1023, 1068], [530, 665, 1022, 1068],
             [666, 719, 1023, 1068], [720, 742, 1023, 1065], [743, 749, 1024, 1065], [750, 751, 1036, 1065]]
B_PLASTER = dict(face=1.0, tone=(210, 210, 222), ch=0.3)   # (the building left of the pole: its one plaster)
WALL_TOL = 24                                  # (a frame's pixel within this of the layer's is its wall, maybe lit by the lantern)
PAN_TOL = 40                                   # (the leaf's, resampled at each step: its lit edges are much further)

ZONES = {
    # the rooftop unit over the arcade: its side face was an illegible smudge; one fan guard in its perspective
    'fan': dict(box=(1296, 160, 1456, 320), scale=6, parts=[
        dict(poly=[(1361, 222), (1387, 207), (1387, 290), (1361, 290)], method='hist')]),
    # Ichiraku's front: a new signboard (the owner: a logo, a little depth), its plaster cleaned, the vent legible,
    # the painted steam smear removed (the animated puffs stay)
    'ramen': dict(box=(1090, 290, 1300, 570), scale=5, parts=[
        dict(poly=[(1106, 393), (1278, 302), (1278, 402), (1106, 466)], method='direct', neon=True, emblem=(1129, 408, 11)),
        dict(poly=[(1119, 462), (1266, 407), (1266, 560), (1236, 560), (1236, 502), (1168, 502), (1168, 560), (1119, 560)],
             method='detail', sigma=6.0, k=0.6,
             fill=[[(1134, 426), (1166, 426), (1166, 506), (1134, 506)],          # the painted steam smear
                   [(1130, 490), (1142, 490), (1142, 498), (1130, 498)],          # the lanterns' painted brackets:
                   [(1244, 459), (1256, 459), (1256, 467), (1244, 467)]])]),       # the wall lamps bring their own arms
    # Ichiraku's door, after the owner's choice among four (2026-11-12): no awning, no vent box; over the doorway a wooden
    # lattice transom lit from inside (V3), the plaster around it. The doorway itself, its glass and its frame stay as
    # painted: the closed shop's overlay (shop_off) and the life behind the glass are laid on them.
    'door': dict(box=(1100, 390, 1280, 580), scale=5, parts=[
        dict(poly=[(1119, 452), (1266, 397), (1266, 472), (1119, 500)], method='direct')]),
    # the plaster below, on both sides of the door, down to the pavement (the owner: the bottom was all grain, the top
    # clean; one wall, one finish). The menu board left of the door, its frame and its shadow: taken away last (board).
    'base': dict(box=(1100, 530, 1280, 740), scale=5, parts=[
        dict(poly=[(1118, 556), (1157, 556), (1157, 729), (1118, 729)], method='detail', sigma=6.0, k=0.6,
             cut=[[(1128, 576), (1151, 576), (1151, 647), (1128, 647)]],          # (its wooden frame: the grain round it
             fill=[[(1125, 573), (1155, 573), (1155, 652), (1125, 652)]]),         # cleaned too, the board none of its light)
        # the board's shadow on the plaster under it and on its right (the lamp is above it)
        dict(poly=[(1129, 647), (1153, 647), (1153, 649), (1129, 649)], method='shade', f=0.72),
        dict(poly=[(1151, 579), (1152.5, 579), (1152.5, 647), (1151, 647)], method='shade', f=0.85),
        dict(poly=[(1232, 556), (1267, 556), (1267, 731), (1232, 731)], method='detail', sigma=6.0, k=0.6)]),
    # the karate dojo at the street's left edge: its noren (four indigo panels on a rod), its shoji's lattice, its
    # signboard 心源流, its plaster strip and kick-panels, all cleaned of their grain. The dojo shuts by the hour (street.js
    # HRS: the unlit layer shown over it), so the unlit layer gets the new picture darkened as the painter darkened his.
    'dojo': dict(box=(0, 400, 160, 720), scale=5, parts=[
        dict(poly=[(0, 458), (100, 458), (100, 720), (0, 720)], method='direct', unlit='lf_ratio'),
        dict(poly=[(0, 530), (80, 530), (80, 688), (0, 688)], method='hist', unlit='lf_ratio')]),   # the shoji: the painter's warm light
    # the oden shop's front: its blotchy walls and eave cleaned (the painter's light, the drawing's planks), its noren
    # redrawn crisp; the glass of its door and window (tools/oden_interior.py), its roof light box (oden_sign_*), its
    # paper lantern left as they are (its frames and the door's sliding leaf carry the wall: oden_overlays). It shuts.
    # the tobacco kiosk (the cabin behind its glass: tools/tabako_window.py, lit by its comp win_z7_kiosk; the draft was
    # asked of it lit): the two enamel plates under the window, its pale ledge, its planks cleaned. Shut and power cut
    # are the same layer here.
    # the Pokemon Center's ball sign (lit by its comp z4_emblem): a clean sphere, no outline (the owner: "si c'est une
    # sphère, il y a de l'ombre sur le côté, pas de contour"): the painter's dark rim around it gives way to the street
    # behind; the ball itself lit in the comp, the same darkened in the street (the sign off, the power cut)
    'pokeball': dict(box=(838, 440, 912, 510), scale=8, comp=('z4_emblem', (849, 450)), despeckle=30, parts=[
        dict(poly=circle(870.5, 470.5, 25), method='direct', unlit='lf_ratio', outside_comp=True),   # the rim, gone
        dict(poly=circle(870.5, 470.5, 25), method='direct', fit='self_red', glow=(871.0, 470.5, 9.0), lit=True, cover=1)]),
        # the ball, lit: the drawing's sphere in the painter's colours, its button glowing as the painter's did
    # the kiosk's planks above its window, up to its roof: their pale stains gone (R9: the wall cleaned whole, with the
    # planks under the sign); the sign, the roof's edge, the neighbour's eave lines and the post kept
    'kiosktop': dict(box=(224, 420, 280, 560), scale=8, parts=[
        dict(poly=[(240, 437), (277, 483), (277, 560), (229, 560), (229, 474), (240, 474)], method='detail',
             sigma=6.0, k=0.6, keep=[dict(rect=(231, 530, 270, 560))])]),                              # (the sign)
    'kiosk': dict(box=(224, 560, 280, 690), scale=8, comp=('win_z7_kiosk', (230, 575)), parts=[
        dict(poly=[(229, 561), (277, 561), (277, 690), (229, 690)], method='detail', sigma=6.0, k=0.6,       # the planks
             cut=[[(229, 574), (271, 574), (271, 649), (229, 649)], [(229, 650), (267, 650), (267, 679), (229, 679)]]),
        dict(poly=[(229, 650), (267, 650), (267, 670), (229, 670)], method='hist'),                        # the plates
        dict(poly=[(229, 670), (267, 670), (267, 679), (229, 679)], method='hist'),                        # the ledge
        # its lit cabin as the owner chose among three shown in the street (B): a Showa tobacco shop's service window,
        # a low glass showcase of packs under a sliding pane, a cash tray on it (kiosk_optB_model.webp); the first
        # redraw, crisper but the same, was not kept ("je comprends pas ce qui a changé")
        dict(poly=[(230, 575), (270, 575), (270, 648), (230, 648)], method='direct', fit='self', lit=True, shut_k=0.6,
             model='kiosk_optB_model.webp')]),
    'oden': dict(box=(390, 462, 525, 690), scale=5, parts=[
        dict(poly=[(398, 537), (463, 537), (503, 548), (503, 664), (398, 684)], method='detail', sigma=10.0, k=0.7, unlit='lf_ratio',   # its walls, the door's wood
             # (sigma 10: its blotches are five pixels wide, wider than Ichiraku's grain; its light falls off over twenty)
             keep=ODEN_KEEP + [dict(warm=(463, 538, 500, 562))],                                 # the two lamps over the window
             # the box under the window (two stacked capsule machines or a menu? unreadable at 12 x 36 px, "les boîtes aux
             # lettres") and the two red dots by it go (R7): the planks run down to the pavement
             erase=[[(468, 628), (484, 628), (484, 660), (468, 660)], [(483, 628), (502, 628), (502, 640), (483, 640)]],
             cut=[ODEN_UNDER_BOX]),                                   # (the wall's foot there is at y 660: the box stood on the pavement)
        dict(poly=ODEN_UNDER_BOX, method='copy', src=(17, 0)),       # the pavement it stood on: the pavement beside it, same rows
        dict(poly=[(420, 507), (465, 507), (465, 521), (514, 531), (514, 553), (463, 541), (420, 537)], method='detail',
             sigma=4.0, k=0.8, unlit='lf_ratio', feather=3, cut=[ODEN_BOARD],                # the eave, faded into the roof
             keep=[dict(warm=(436, 519, 457, 540))]),                                           # (the lamp over the noren)
        dict(poly=[(420, 537), (463, 537), (463, 580), (420, 580)], method='hist', unlit='lf_ratio',
             keep=ODEN_KEEP + [dict(warm=(436, 519, 457, 540))])]),                              # the noren
    # the ground floors on either side of the right pole, drawn whole behind it (the owner: "fais un truc global
    # derrière le poteau et après tu repasses le poteau devant"): the draft asked of the street with the pole taken
    # out (its crop 9:16, not stretched), the pole laid back over it as painted (`front`, its trace in street.js), so
    # the walls run on behind it and nothing is squeezed into the strips beside it. Left, the apartment building's lit
    # hall (its lamp, intercom and panels, mush at this size, gone: its wall alone, lit); right, the house's entrance
    # (its awning, its frosted transom and sidelight lit, a dark door with a slit window, its step on the sidewalk's
    # line) and its planked wall up to the pole (no more "garage"). From the ledges (zone5's rays) to the foot of the
    # walls (v -0.283); after Ichiraku's zones, whose box it overlaps.
    'pole': dict(box=(990, 425, 1170, 745), scale=6, front=POLE_RUNS, fringe=15,
                 reg=[[(992, 428), (1020, 428), (1020, 470), (992, 470)],               # (what the draft kept: the floors
                      [(1072, 428), (1110, 428), (1110, 440), (1072, 440)],             # above, Ichiraku)
                      [(1122, 430), (1168, 430), (1168, 740), (1122, 740)]], parts=[
        dict(poly=[(1004, ray(1004, 0.390)), (1022, ray(1022, 0.390)), (1069, ray(1069, 0.3955)), (1117, ray(1117, 0.3955)),
                   (1117, ray(1117, -0.283) + 1), (1004, ray(1004, -0.283) + 1)], method='direct', unlit='rel',
             erase=[[(1006, 563), (1022, 563), (1022, 665), (1006, 665)]],              # (the hall's lamp, intercom, panels)
             erase_from=[(1006, 540), (1022, 540), (1022, 699), (1006, 699)]),          # (its lit wall)
        # a post at the awning's right end, under Ichiraku's sign (a bracket? it reads as a stray thing): the awning
        # and the ledge over it continued from 10 px to its left, along their ray (4 rows down)
        dict(poly=[(1103, 448), (1112, 448), (1112, 479), (1103, 479)], method='copy', src=(-10, 4), from_new=True),
        dict(poly=[(1112, 455), (1117, 455), (1117, 479), (1112, 479)], method='copy', src=(-10, 4), from_new=True),
        # (and on to Ichiraku's wall, from what the first copy laid)
        # the foot of Ichiraku's wall beside the step (the owner: "moche, trottoir à côté d'Ichiraku"): a speckled band
        # under its cleaned plaster (base, to y 728). The plaster down to the facades' foot (v -0.283, as the step), its
        # rows from higher up; under that line the sidewalk, the painter's own from 30 px to the left along the line
        dict(poly=[(1116, 729), (1157, 729), (1157, ray(1157, -0.283) + 1), (1116, ray(1116, -0.283) + 1)], method='copy',
             src=(0, -16), from_new=True),
        dict(poly=[(1117, ray(1117, -0.283) + 1), (1157, ray(1157, -0.283) + 1), (1157, 743), (1117, 743)], method='copy',
             src=(-30, -8))]),
    # the apartment building's ground floor left of the pole (the owner: "ce rdc est à refaire complet"): its shop shut
    # for the night (the shutter, its box, its signboard, its side door), its weatherboards and downpipe, the bicycle and
    # the bucket, up to the lit hall (the pole zone's); after it and the Pokemon Center's ball, whose boxes it overlaps
    'bfloor': dict(box=(880, 415, 1070, 753), scale=6,
                   reg=[[(942, 430), (1020, 430), (1020, 490), (942, 490)], [(900, 705), (1020, 705), (1020, 750), (900, 750)],
                        [(1026, 430), (1064, 430), (1064, 740), (1026, 740)]], parts=[      # (floors above, sidewalk, pole)
        # from under the shop's ledge (zone5's ray) to the foot of the wall, past it under the bicycle and the bucket
        # (their wheels and base on the sidewalk); its lit left arris (x 941) and the hall (x 1004 on) left as they are
        dict(poly=[(942, ray(942, 0.390)), (1004, ray(1004, 0.390)), (1004, ray(1004, -0.283) + 1), (996, ray(996, -0.283) + 1),
                   (996, 704), (948, 704), (948, ray(948, -0.283) + 1), (942, ray(942, -0.283) + 1)], method='direct', unlit='rel',
             # its wall the plaster's tint over the ledge (the owner: "pas la même teinte"); the shop window's frame and
             # room as drawn, the sidewalk under the bicycle as the painter's
             match=dict(plaster=B_PLASTER, src=(943, 1000, 0.43, 0.47), dst=(947, 1000, 0.25, 0.38), v_min=-0.283,
                        skip=[[(956, ray(956, 0.2245)), (1000, ray(1000, 0.2245)), (1000, ray(1000, -0.105)), (956, ray(956, -0.105))]]))]),
    # the same building's floors above it in the plain plaster of its ground floor, the whole front one material (the
    # owner, choosing the shop window: "unifier sa texture sur tout le bât"; zone5 had given it weatherboards); its two lit
    # windows' overlays, which carry the wall beside them, take the same change (`comps`, from <name>_before.webp)
    # its two narrow windows right of the big ones go (the owner: "vire les petites fenêtres à droite des grosses"),
    # plaster over them, filled from round them (the violet one's lit overlay and its light on the ground go with it)
    'bwall': dict(box=(940, 60, 1023, 522), nodraft=True, comps=[('win_z1_top', 963, 226)], parts=[
        dict(poly=[(941, 60), (1023, 60), (1023, 522), (941, 522)], method='zone5', v0=0.390, **B_PLASTER,
             fill=[(1006, 1022, 0.991, 1.283), (1006, 1022, 0.5235, 0.801)])]),   # (zone5's boxes for them, sills included)
    # the dojo's foot, its right corner post and the dark gap between it and the dagashi-ya (a survey, 2026-11-13: the
    # dojo's zone stopped at y 720 over speckled kick panels and a grainy threshold; the gap a flat black-green)
    'dojofoot': dict(box=(0, 440, 180, 760), scale=6, reg=[(5, 445), (95, 445), (95, 560), (5, 560)], parts=[   # (the dojo's top)
        # its kick panels down to the threshold, the threshold on its ray (v 0.197 to 0.229, the painter's line), as the
        # dojo's front above them (direct, darkened as the painter's when it shuts); from y 720, where the dojo's zone ends
        dict(poly=[(0, 720), (96, 720), (96, ray(96, 0.229) + 1), (0, ray(0, 0.229) + 1)], method='direct', unlit='lf_ratio'),
        dict(poly=[(96, 470), (110, 470), (110, ray(110, 0.229) + 1), (96, ray(96, 0.229) + 1)], method='direct', unlit='lf_ratio'),   # its post
        # the gap: a passage in deep navy shadow, the sidewalk a little way into it (its downpipe, x 132-137, and the
        # tree's leaves over it as painted); the same in the power cut (no light of its own)
        dict(poly=[(110, 471), (132, 471), (132, 752), (110, 752)], method='direct')]),   # (down to the sidewalk: the olive slab went to y 750)
    # the bottom of Ichiraku's two sliding doors and the foot of its wall right of them (a survey, 2026-11-13: the doors'
    # kick panels a red and blue mush, a square of old grain under the cleaned plaster); after base and pole
    'ichifoot': dict(box=(1150, 676, 1280, 780), scale=7,
                     reg=[[(1150, 680), (1156, 680), (1156, 740), (1150, 740)], [(1235, 680), (1265, 680), (1265, 728), (1235, 728)],
                          [(1165, 676), (1225, 676), (1225, 685), (1165, 685)]], parts=[      # (the plaster, the glass)
        # the doors' rail and kick panels: the drawing's boards in the painter's light and wood (detail), to the threshold
        dict(poly=[(1157, 688), (1232, 688), (1232, 757), (1157, 745)], method='detail', sigma=6.0, k=0.5, unlit='lf_ratio'),
        # right of the doors, the cleaned plaster (base, to y 730) carried down to the sidewalk's line (v -0.267 there)
        dict(poly=[(1232, 731), (1267, 731), (1267, ray(1267, -0.267) + 1), (1232, ray(1232, -0.267) + 1)], method='copy',
             src=(0, -36), from_new=True)]),
    # a blob of light behind the railing at the crossroads (the only light of the valley at 3 h): one window of the far
    # city, its rails in front (the owner: "si seul allumé, c'est une fenêtre de la ville du fond")
    'farwin': dict(box=(640, 622, 668, 642), nodraft=True, parts=[
        dict(poly=[(650, 629), (658, 629), (658, 631), (650, 631)], method='from_unlit', ref=(640, 629, 645, 636)),   # (edges inclusive)
        dict(poly=[(650, 633), (658, 633), (658, 635), (650, 635)], method='from_unlit', ref=(640, 629, 645, 636)),
        dict(poly=[(652, 629), (654, 629), (654, 631), (652, 631)], method='paint', rgb=(226, 136, 98)),        # (the rail at
        dict(poly=[(652, 633), (654, 633), (654, 635), (652, 635)], method='paint', rgb=(214, 124, 92))]),      # y 632 in front)
    # the two flat shadows by the arcade (between Ichiraku and the downpipe, between the post and the arcade): the
    # painter's green-black there made the navy of the street's deep shadows (as the dojo's gap)
    'arcgap': dict(box=(1265, 410, 1355, 790), nodraft=True, parts=[
        dict(poly=[(1265, 410), (1302, 410), (1302, 790), (1265, 790)], method='navy', rgb=(1, 3, 11)),
        dict(poly=[(1319, 410), (1355, 410), (1355, 790), (1319, 790)], method='navy', rgb=(1, 3, 11))]),
    # the house at the street's end (the owner's picks, drawn by tools/end_house.py): its paper lantern by the door, off a
    # flat red disc (no caps, no shading, no hook): a barrel with its caps and its bracket, the same lit (the comp
    # win_z9_lantern) and off (darkened as the painter darkened his); its upstairs window, its right pane dark blocks and
    # its railing's bars irregular: a curtain across each pane, lit (the comp win_z9_window) and off, the railing's bars on
    # the balcony's own rhythm in both. (z9win: after the Pokemon Center's ball, whose box it overlaps; it changes none of
    # the ball's rows)
    'z9lan': dict(box=(796, 572, 828, 592), nodraft=True, parts=[
        dict(poly=[(796, 572), (828, 572), (828, 592), (796, 592)], method='hand', fn='end_house.lantern', comp='win_z9_lantern')]),
    'z9win': dict(box=(800, 496, 866, 536), nodraft=True, parts=[
        dict(poly=[(800, 496), (866, 496), (866, 536), (800, 536)], method='hand', fn='end_house.window', comp='win_z9_window')]),
    # the right pole's foot planted in the sidewalk (the owner: "la transition poteau trottoir pas dingue"): solid to the
    # ground, its foot an ellipse, its contact shadow; drawn by tools/pole_foot.py, after pole and bfloor (it overlaps them)
    'polefoot': dict(box=(995, 690, 1100, 800), tool='pole_foot'),
    # the dagashi-ya shut (the owner: "petite lumière de nuit ? et fermé"): its room, seen through the open door and the
    # left door's glass, was a mauve ghost of the lit one (tools/dagashi_interior.py's dark: the painter's own shut room,
    # its pale end), the crate of balls by the door a pale mass. Now the lit room (its comp, win_z7_shop, as it is)
    # darkened as the painter darkens a shut place (the dojo's shoji, lit and shut: the night's blue), a little lighter by
    # the door (the crate a box), its lamp out; the ramune cooler behind the glass left on, its cold light on the jars
    # and the counter by it; in the power cut, out with the rest. The obaa-chan's dark (her in a power cut while it is
    # open) in the same room's dark (`atlas`)
    'dagashi': dict(box=(142, 525, 227, 745), nodraft=True, comp=('win_z7_shop', (142, 537)),
                    atlas=dict(name='dagashi_obaachan', dark=112, w=730, z=26.45), parts=[
        dict(poly=[(142, 525), (227, 525), (227, 745), (142, 745)], method='night', room='dagashi_interior',
             fit=(0, 530, 80, 688), knee=(140.0, 0.3), lamp_out=(60.0, 0.15), door=(17.0, 27.0, 1.2),
             src=dict(rect=(146, 649, 155, 675), tint=(0.84, 1.0, 1.1), k=0.85, amp=0.6, r=9.0))]),
    # the arcade's low roof under the rooftop unit (the owner's pick #11, "+ gouttière": blotches nobody could name on its
    # edge, a blurred box under the unit): drawn on the pixel grid in the street's perspective by tools/arcade_eave.py
    # (its eave tiles on the painter's rays, foreshortened; the tufts gone; a steel stand under the unit; a half-round
    # gutter with its hangers, the downpipe at the corner carried up to it; the wall camera moved under it in street.js)
    'arceave': dict(box=(1232, 262, 1456, 430), nodraft=True, parts=[
        dict(poly=[(1232, 262), (1456, 262), (1456, 430), (1232, 430)], method='tool', tool='arcade_eave')]),
    # the house at the street's end, its ground floor (the owner: "la maison, refaire le bas, pas hyper clean"): blotches
    # drawn as what they are, face on as the house is (tools/end_house.py, ground): a frosted glass window on its sill, the
    # jamb the lantern hangs by, two sliding lattice doors over plain kick panels, the right one open a little (the cat's
    # gap), on the painter's light; the boards and the lintel over them and the posts evened, the sill, the sidewalk in the
    # eave's shadow; lit, the lantern's light on it a soft pool (its comp, on from z9lan's: after it, whose box it overlaps)
    'z9base': dict(box=(760, 566, 870, 641), nodraft=True, parts=[
        dict(poly=[(760, 566), (870, 566), (870, 641), (760, 641)], method='hand', fn='end_house.ground', comp='win_z9_lantern')]),
    # Ichiraku's menu board gone (the owner, 2026-11-13: "juste le mur"; Luffy's posters were in it): its wooden frame
    # (x 1128-1151, y 576-649) and the ring base drew round it from its draft (the board's edges and shadow, the plaster
    # darker beside it: BOARD) made the cleaned plaster round it. Its light: the wall's round it run through it (`fill`:
    # the board lends it none; `lf_fill`: down each column from the plaster above it to the plaster below, so the
    # doorway's warm glow on the plaster runs on through as the stripe it is above and below, made good against the wall
    # on its left; the doorway's lit frame on its right lends it nothing); its fine grain each layer's own plaster from
    # under it (`tex`: the high frequencies of the rows 104 and 54 below, taken without the board). Last, so the zones
    # before it (pole: its draft's registration and tint are fitted on Ichiraku's front) see the street as they were made on.
    'board': dict(box=(1110, 548, 1172, 736), nodraft=True, parts=[
        dict(poly=BOARD, method='detail', sigma=6.0, k=1.0, fill=[BOARD], lf_fill=[(1121, 566, 1152, 655)],
             tex=[([(1121, 566), (1152, 566), (1152, 615), (1121, 615)], (0, 104)),
                  ([(1121, 616), (1152, 616), (1152, 655), (1121, 655)], (0, 54))])]),
    # the right pole's concrete (the owner: "texture poto"): a near black green column with a lit stripe, an outline, an
    # orange rim with gaps and a stack of smeared bands, now a concrete cylinder in the painter's light (its lit side
    # round from the left, its shade the night's navy, his rim continuous, a fine even grain on its own surface), its
    # bands, bolt and conduits crisp; its cap, its sign and its foot's shape kept. Drawn by tools/pole_texture.py, after
    # pole, bfloor, bwall and polefoot (it overlaps them); it also writes the rim's sun mask (assets/street_sun.webp)
    'poletex': dict(box=(1005, 44, 1070, 757), tool='pole_texture'),
    # the street lamp the pole carries (the owner: "luminaire du poteau"): its head a model in the street's camera (a
    # steel hood, a milky lens under it, lit in its comp, off and in the power cut in the layers), its arm one clean
    # tube, its bracket two straps to the pole's bands; the old head and arm gone from the sky, the wall behind them
    # carried along its rays. Drawn by tools/pole_lamp.py, after poletex; it also writes assets/lamp.webp (its lit comp)
    # and assets/night_far.webp over its box
    'polelamp': dict(box=(845, 128, 1023, 230), tool='pole_lamp'),
    # Naruto's floor over Ichiraku (the owner: "à refaire : fenêtre, rambarde, appart Naruto, façade premier"): its window,
    # its balcony's railing, its walls and slabs redrawn on the pixel grid in the street's perspective by
    # tools/naruto_floor.py, down to the sign's top edge (the sign, 'ramen', the rooftop unit, 'fan', and the arcade's
    # eave, 'arceave', whose boxes it overlaps, as they leave them); then ("rebord, tuyauterie et géométrie du toit pas
    # correctes") the roof's edge over it on the same rays, its near side, the garden set on the new coping, the
    # downpipes; it writes the window's lit overlay too (assets/window_panes.webp, window_lit_ukki.webp), the garden's
    # wind data (roof_sway.webp) and the low sun's glint on the lip (street_sun.webp)
    'narufloor': dict(box=(1120, 0, 1381, 390), tool='naruto_floor'),
    # the drinks corner on the left sidewalk (the owner: "à refaire : le haut-vent toit tuile au-dessus soda, les soda, la
    # caisse soda"), drawn in the street's camera by tools/soda_corner.py: the kiosk's lean-to in old Japanese tiles (its
    # pans where the painter's troughs were: the eave's drips stay), the three machines (their comps z7_vending and
    # z7_vendoff written for tools/bake_retouches.py), the kiosk's sign, its service window (its comp win_z7_kiosk,
    # handed on in COMP_OUT after the kiosk zone's) and its plates; after the kiosk zones, whose boxes it overlaps
    'soda': dict(box=(227, 405, 390, 735), tool='soda_corner'),
    # the narrow building between the Pokemon Center and the apartment building (zone5's A, x 908..940; the owner: "le
    # bâtiment entre Pokécenter et bâtiment refait : mur lisse"): its glazed tiles made one plaster from its cap to the
    # sidewalk, a tone of its own beside B's (R25), by tools/narrow_plaster.py (zone5's walls() and life() again, A in
    # plaster: its ledges in it, its lit window, door, mailbox and plant as zone5 drew them); its top redrawn on the
    # facade's rays (the owner: "le haut est moche, l'espèce de boudin de béton qui fait le contour ; pas droit, angle
    # bizarre"): a slim coping under the roof edge, the plaster up to it and out to a plain corner, the upper window in
    # the plain wall with a thin frame and sill; after pokeball, bfloor and bwall, whose boxes it overlaps (it changes
    # none of their pixels)
    'awall': dict(box=(905, 315, 941, 690), nodraft=True, parts=[
        dict(poly=[(905, 315), (941, 315), (941, 690), (905, 690)], method='tool', tool='narrow_plaster')]),
    # the roofs on the left (the owner: "gouttière et finition toit sous Kirua et dojo : tuile ancienne, gouttière clean
    # et vraie perspective du toit"): Kirua's eave, the one he sits on over the dagashi-ya, and the dojo's house's eave end
    # at the top left, drawn on the pixel grid by tools/left_eaves.py (old round tiles' ends, a half-round gutter with its
    # lit roll and hangers, both on the street's rays and growing toward the viewer). Kirua's is a hipped roof modelled
    # whole: its level return round the near corner (the tiles' ends flush there), its eave on past the far wall (it had
    # stopped 38 cm short of it) and turning the far corner, the overhang's soffit, a collecting box and a swan neck into
    # the painter's downpipe; the dojo's rim in the painter's dusk, its soffit cleaned whole, its gutter's box and swan neck
    # into the downpipe the two houses share (eaveP: the pipe by the dojo's corner). Kirua's in narrow boxes along its
    # slope (they change nothing of his front's boards or the bay window), each its own zone; their street_sun marks (and
    # night_far's, the dojo's) from tools/src/edits/<zone>_before_{sun,nf}.webp
    'eaveKs': dict(box=(141, 50, 206, 102), tool='left_eaves'),
    'eaveK1': dict(box=(206, 56, 236, 136), tool='left_eaves'),
    'eaveK2': dict(box=(236, 90, 266, 167), tool='left_eaves'),
    'eaveK3': dict(box=(266, 123, 296, 198), tool='left_eaves'),
    'eaveK4': dict(box=(296, 157, 322, 225), tool='left_eaves'),
    'eaveK5': dict(box=(322, 186, 374, 290), tool='left_eaves'),
    'eaveD': dict(box=(100, 0, 190, 50), tool='left_eaves'),
    'eaveP': dict(box=(128, 50, 141, 84), tool='left_eaves'),
    # the small canopy over the pink-lit entrance right of the pole and its end against Ichiraku (the owner: "le haut-vent
    # juste à droite... petit truc bizarre entre ça et la façade d'Ichiraku"): the draft's corrugated awning, seen from
    # above though it hangs over the eye, its ragged edge and the dark slot at its end, now a thin aluminium hood in the
    # street's camera, seen from below (its near end's lit edge, its underside lit by the hall's pink light), the house's
    # planks down to it and in its shadow under it, the two walls' corner as under the entrance; drawn by
    # tools/entrance_canopy.py, after pole, ramen, door and poletex (it overlaps their boxes; the pole's pixels untouched)
    'canopy': dict(box=(1065, 452, 1124, 532), tool='entrance_canopy'),
}
SHOP_OFF = dict(src='shop_off_before.webp', out='shop_off.webp', at=(1112, 448), grow_top=28,   # (grown upward: the transom)
                clear=[(1128, 438), (1258, 398), (1258, 470), (1128, 498)],   # the old eave's and vent's lit strips, the dashes
                lit_from='door', lit_part=0)                                   # the lattice transom's warm light, shut
COMP_OUT = {}                                   # zone -> [comp name, its new pixels, its slice]: written by main
NEON_ZONE = 'ramen'
NEON_OUT = os.path.join(ROOT, 'assets', 'ichiraku_neon_glow.webp')

lum = lambda z: 0.299 * z[..., 0] + 0.587 * z[..., 1] + 0.114 * z[..., 2]


def load(path):
    return np.array(Image.open(path).convert('RGBA')).astype(float)


def poly_mask(P, box):
    x0, y0, x1, y1 = box
    m = Image.new('L', (x1 - x0, y1 - y0), 0)
    ImageDraw.Draw(m).polygon([(px - x0, py - y0) for px, py in P], fill=255)
    return np.array(m) > 127


def obj_masks(specs, orig, box):
    """What a part keeps as painted, by its shape rather than a box around it (R20): `rect` (x0, y0, x1, y1) as it is;
    `warm` the lit things in that box (a lantern, a lamp, a board: red over blue), grown by a pixel and their holes
    filled, so their dark ribs and outline go with them."""
    from scipy.ndimage import binary_fill_holes
    x0, y0, x1, y1 = box; k = np.zeros((y1 - y0, x1 - x0), bool)
    for sp in specs:
        if 'rect' in sp:
            a, b, c, d = sp['rect']; k[max(b - y0, 0):d - y0, max(a - x0, 0):c - x0] = True
        if 'warm' in sp:
            a, b, c, d = sp['warm']; r = np.zeros_like(k); r[b - y0:d - y0, a - x0:c - x0] = True
            w = r & (orig[..., 0] > 90) & (orig[..., 0] > orig[..., 2] + 30)
            k |= binary_fill_holes(binary_dilation(w, iterations=sp.get('grow', 1))) & binary_dilation(r, iterations=1)
    return k


def grad(z):
    l = lum(z); gx = np.zeros_like(l); gy = np.zeros_like(l)
    gx[:, 1:] = l[:, 1:] - l[:, :-1]; gy[1:] = l[1:] - l[:-1]
    return np.hypot(gx, gy)


def shift(a, dy, dx):
    """a moved by (dy, dx), its edge pixels repeated into what it uncovers (not wrapped round)."""
    h, w = a.shape[:2]; yi = np.clip(np.arange(h) - dy, 0, h - 1); xi = np.clip(np.arange(w) - dx, 0, w - 1)
    return a[yi][:, xi]


def register(e, orig, ref, reach=4):
    go = grad(orig); go = (go - go[ref].mean()) / (go[ref].std() + 1e-6); best = None
    for dy in range(-reach, reach + 1):
        for dx in range(-reach, reach + 1):
            g = grad(shift(e, dy, dx)); g = (g - g[ref].mean()) / (g[ref].std() + 1e-6)
            c = (g[ref] * go[ref]).mean()
            if best is None or c > best[0]: best = (c, dx, dy)
    return best


def lowpass_filled(img, hole, sigma):
    """Gaussian low frequencies of img, the pixels of `hole` left out (normalised convolution)."""
    w = (~hole).astype(float)
    num = np.stack([gaussian_filter(img[..., c] * w, sigma) for c in range(3)], -1)
    den = gaussian_filter(w, sigma)[..., None]
    # a hole wider than the kernel: widen until every pixel has support
    s = sigma
    while (den < 1e-3).any() and s < 64:
        s *= 1.6
        num = np.stack([gaussian_filter(img[..., c] * w, s) for c in range(3)], -1); den = gaussian_filter(w, s)[..., None]
    return num / np.maximum(den, 1e-6)


def wall_fill(img, rects, box, sigma, n=3):
    """`lf_fill`: in each rect (x0, y0, x1, y1, edges inclusive) the light of the wall round it run through it: down each
    column from the wall just above it to the wall just below it (n rows each side, low-passed along the row as the
    zone's light is, sigma), so a light that runs down the wall beside a doorway runs on through as a stripe; and what
    that leaves against the wall on its left, made good by a membrane fading from there (zero above and below, its right
    side free: the doorway's lit frame on the right lends it nothing). Returns the light in the box (the rects' only)."""
    from scipy.ndimage import gaussian_filter1d, uniform_filter1d
    from scipy.sparse import lil_matrix
    from scipy.sparse.linalg import spsolve
    x0, y0 = box[0], box[1]; out = np.zeros_like(img); Hs = gaussian_filter1d(img, sigma, axis=1)
    for a, b, c, d in rects:
        r0, r1, c0, c1 = b - y0, d - y0, a - x0, c - x0; h, w = r1 - r0 + 1, c1 - c0 + 1
        t = ((np.arange(h) + (n + 1) / 2) / (h + n + 1))[:, None, None]
        lerp = lambda A: (1 - t) * A[r0 - n:r0, c0 - 1:c1 + 1].mean(0)[None] + t * A[r1 + 1:r1 + 1 + n, c0 - 1:c1 + 1].mean(0)[None]
        base, raw = lerp(Hs), lerp(img)
        res = uniform_filter1d(img[r0:r1 + 1, c0 - n:c0].mean(1), 5, axis=0) - raw[:, 0]   # (the wall on its left)
        A = lil_matrix((h * w, h * w)); rhs = np.zeros((h * w, img.shape[2]))
        for i in range(h):
            for j in range(w):
                k = i * w + j
                for di, dj in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    ii, jj = i + di, j + dj
                    if jj >= w: continue                    # (the right side: free)
                    A[k, k] += 1.0
                    if jj < 0: rhs[k] += res[i]
                    elif 0 <= ii < h: A[k, ii * w + jj] -= 1.0   # (above and below: zero)
        A = A.tocsr()
        u = np.stack([spsolve(A, rhs[:, ch]) for ch in range(img.shape[2])], -1)
        out[r0:r1 + 1, c0:c1 + 1] = base[:, 1:] + u.reshape(h, w, -1)
    return out


_Z5 = {}
def zone5_plaster(face, tone, ch, at='cd2d002^'):
    """The apartment building left of the pole (B) in one plain plaster (the owner: "unifier sa texture sur tout le
    bâtiment", 2026-11-13): tools/zone5_facades.py's own walls() on the layers as they were before it (git `at`), B alone,
    its material plaster on the painter's light (its drift, weathering, ledges and cap in the same material); its
    windows, balconies, downpipe, the lamp's arm and the pole as they are. Returns its street, its power cut and what it
    changed, whole-scene arrays (cached)."""
    key = (face, tone, ch, at)
    if key not in _Z5:
        import io, subprocess
        sys.path.insert(0, os.path.join(ROOT, 'tools')); import zone5_facades as Z
        old = lambda f: np.array(Image.open(io.BytesIO(subprocess.run(['git', 'show', f'{at}:assets/{f}'], cwd=ROOT,
                                 capture_output=True, check=True).stdout)).convert('RGBA')).astype(float)
        Z.VARIANTS['b_plaster'] = {'B': lambda: Z.plaster(face=face, amp=0.03, tone=tone, ch=ch)}
        c2, u2, chg, _, _ = Z.walls(old('layer_city_off.webp'), old('street_unlit.webp'), 'b_plaster')
        _Z5[key] = (c2[..., :3], u2[..., :3], chg, Z.V)
    return _Z5[key]


_ROOM = {}
def room_model(tool, box):
    """A shop's room as its own tool models it (tools/dagashi_interior.py: its Model, from its commit BEFORE, the rays it
    casts from the street's eye through the door and the glass): on the zone's box, each pixel's surface (the most of its
    rays), its depth (their median Z, m), the glass and the sheen the tool lays on it, and its light sources (its
    picture's lamp and cooler, KNEE: most of its rays end there). Cached."""
    key = (tool, box)
    if key not in _ROOM:
        import importlib
        sys.path.insert(0, os.path.join(ROOT, 'tools')); T = importlib.import_module(tool)
        on = T.before()[4]; M = T.Model(T.measure_sill(on)[0])
        pix, glass = M.pixels(); _, sid, Zh = M.render(pix)
        surf = np.array([np.bincount(r).argmax() for r in sid])
        x0, y0, x1, y1 = box; h, w = y1 - y0, x1 - x0
        R = dict(inside=np.zeros((h, w), bool), surf=np.full((h, w), -1), Z=np.full((h, w), np.inf),
                 sheen=np.zeros((h, w)), light=np.zeros((h, w), bool))
        ok = (pix[:, 0] >= x0) & (pix[:, 0] < x1) & (pix[:, 1] >= y0) & (pix[:, 1] < y1)
        for i in np.nonzero(ok)[0]:
            yy, xx = pix[i, 1] - y0, pix[i, 0] - x0; s = surf[i]; on_s = sid[i] == s
            R['inside'][yy, xx] = True; R['surf'][yy, xx] = s
            if s: R['Z'][yy, xx] = np.median(Zh[i][on_s])
            R['light'][yy, xx] = ((M.glow[i] > 0) & (sid[i] == 1)).mean() > 0.5
        R['sheen'][pix[ok, 1] - y0, pix[ok, 0] - x0] = T.sheen(pix[ok, 0], pix[ok, 1]) * glass[ok]
        _ROOM[key] = R
    return _ROOM[key]


NIGHT = {}                                     # zone -> its night_room's darkening (for the figures laid in the room)
def night_room(name, p, m, box, on, cin, city, unlit, new, unew):
    """A lit window's room shut for the night (the owner on the dagashi-ya: "petite lumière de nuit ? et fermé"): its
    comp's lit picture (`on`), the room its tool models (`room`, room_model), the surfaces in `keep_surf` left as they
    are (the jamb, the lintel's underside: the painter's wood; the sill). The room darkened as the painter darkens what is
    off (R13): channel by channel, a line fitted on `fit` (x0, y0, x1, y1: a shut neighbour, its street lit and shut), its
    lit highlights tamed first (`knee`: above that luminance, that share kept), the model's other lights (its lamp: bulb,
    shade and halo) out (`lamp_out`: the same, lower and harder: an unlit lamp, its shape kept); a little of the street's
    light through the door (`door`: Z near, Z far, the gain at the door: what stands near it a little lighter, the back
    wall as dark as the fit); the sheen on its glass kept. One light left on (`src`: `rect`, x0, y0, x1, y1, the glass of
    a cooler as the comp draws it, in a cold light (`tint`), `k` of its lit luminance; and its light on what is round it,
    `amp` falling off over `r` px: each thing's own colour, half grey, in that cold light). The power cut: the same room,
    that light out too. Writes new and unew in place; returns the pixels it laid."""
    from scipy.ndimage import distance_transform_edt
    x0, y0, x1, y1 = box; h, w = y1 - y0, x1 - x0
    R = room_model(p['room'], box)
    m = m & cin & R['inside'] & ~np.isin(R['surf'], p.get('keep_surf', (0, 7, 8)))
    fx0, fy0, fx1, fy1 = p['fit']
    A = [np.polyfit(city[fy0:fy1, fx0:fx1, c].ravel(), unlit[fy0:fy1, fx0:fx1, c].ravel(), 1) for c in range(3)]
    zn, zf, gain = p['door']
    def tame(lit, kn, ks):
        L = lum(lit); return lit * (np.where(L > kn, kn + (L - kn) * ks, L) / np.maximum(L, 1e-3))[..., None]
    def dark(lit, Z):                          # (the lit picture as the night has it: tamed, the fitted line, the door's light)
        lit = tame(lit, *p['knee'])
        d = np.stack([A[c][0] * lit[..., c] + A[c][1] for c in range(3)], -1)
        return d * (1 + gain * np.clip((zf - Z) / (zf - zn), 0, 1))[..., None], lit
    sp = p['src']; src = np.zeros((h, w), bool)
    a0, b0, a1, b1 = sp['rect']; src[b0 - y0:b1 - y0, a0 - x0:a1 - x0] = True; src &= m
    lit = np.clip(on - R['sheen'][..., None], 0, 255)
    lamp = R['light'] & m & ~binary_dilation(src, iterations=4)
    lit = np.where(lamp[..., None], tame(lit, *p['lamp_out']), lit)
    dk, tamed = dark(lit, np.where(np.isfinite(R['Z']), R['Z'], zf)); sh = R['sheen'][..., None]
    unew[m] = np.clip(dk + sh, 0, 255)[m]
    t = np.array(sp['tint'], float)
    wgt = sp['amp'] * np.exp(-(distance_transform_edt(~src) / sp['r']) ** 2)
    lt = dk + wgt[..., None] * (0.5 * tamed + 0.5 * lum(tamed)[..., None]) * t
    lt[src] = (lum(on)[..., None] * sp['k'] * t)[src]
    new[m] = np.clip(lt + sh, 0, 255)[m]
    NIGHT[name] = dict(dark=dark)
    print(f'{name}: the room shut for the night, {int(m.sum())} px (the line {[tuple(np.round(a, 3)) for a in A]}); '
          f'its night light {int(src.sum())} px; its lamp out, {int(lamp.sum())} px')
    return m


def zone(name, cfg, city, unlit):
    if cfg.get('tool'):                        # (`tool`: a zone drawn by its own module, tools/<tool>.py: its draw(city,
        import importlib                       # unlit, box), on the layers as the zones before it left them)
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        ch = importlib.import_module(cfg['tool']).draw(city, unlit, cfg['box'])
        print(f'{name}: drawn by tools/{cfg["tool"]}.py; pixels changed {int(ch.sum())}')
        return None, []
    box = cfg['box']; x0, y0, x1, y1 = box; w, h = x1 - x0, y1 - y0
    city0, unlit0 = city[y0:y1, x0:x1].copy(), unlit[y0:y1, x0:x1].copy()
    orig = city0[..., :3]
    if cfg.get('nodraft'):                     # (a zone mended from its own pixels, no drawing asked for)
        e = orig.copy()
    else:
        e = np.array(Image.open(os.path.join(EDITS, f'{name}_model.webp')).convert('RGB').resize((w, h), Image.BOX)).astype(float) / 255.0
        e = (e ** GAMMA) * 255.0
    front = np.zeros((h, w), bool)             # (`front`: runs of what stands in front, as street.js traces it: the zone
    for ya, yb, xa, xb in cfg.get('front', []):    # drawn whole behind it, it laid back over the drawing as painted)
        front[max(ya - y0, 0):max(yb + 1 - y0, 0), max(xa - x0, 0):max(xb + 1 - x0, 0)] = True
    masks, keeps = [], []
    for p in cfg['parts']:
        m = poly_mask(p['poly'], box)
        for q in p.get('cut', []): m &= ~poly_mask(q, box)
        k = obj_masks(p.get('keep', []), orig, box); m &= ~k
        m &= ~front
        masks.append(m); keeps.append(k)
    on = None                                  # a lit window's zone (`comp`: its comp's name and place): the draft was
    if cfg.get('comp'):                        # made of it lit, the street with the comp laid on it
        cname, (cx, cy) = cfg['comp']; cb = load(os.path.join(EDITS, f'{name}_comp_before.webp')); ch, cw = cb.shape[:2]
        csl = (slice(cy - y0, cy - y0 + ch), slice(cx - x0, cx - x0 + cw)); ca = cb[..., 3:4] / 255.0
        on = orig.copy(); on[csl] = on[csl] * (1 - ca) + cb[..., :3] * ca
        cin = np.zeros((h, w), bool); cin[csl] = cb[..., 3] > 0
        cov = cin.copy(); grow = max([q.get('cover', 0) for q in cfg['parts']] + [0])
        if grow:                                   # (`cover`: the lit area grown by that many pixels, inside the comp's box:
            cbox = np.zeros_like(cin); cbox[csl] = True   # the redrawn sign's own edge lit with it, not left in the street)
            cov = binary_dilation(cin, iterations=grow) & cbox
    allm = np.any(masks, 0); ref = ~binary_dilation(allm, iterations=3); ref[:6] = ref[-6:] = False; ref[:, :6] = ref[:, -6:] = False
    if ref.sum() < 200:                        # (a zone redrawn whole: registered on all of it, its margins aside)
        ref = np.zeros_like(allm); ref[6:-6, 6:-6] = True
    if cfg.get('reg'):                         # (`reg`: where the drawing and the painting match, to register on: a
        regs = cfg['reg'] if isinstance(cfg['reg'][0][0], (list, tuple)) else [cfg['reg']]   # polygon, or several)
        ref = np.any([poly_mask(q, box) for q in regs], 0)
    ref = ref & ~binary_dilation(front, iterations=3)   # (a drawing made without what stands in front: not there)
    corr, dx, dy = (1.0, 0, 0) if cfg.get('nodraft') else register(e, on if on is not None else orig, ref, cfg.get('reach', 4))
    e = shift(e, dy, dx)
    if cfg.get('persp'):                       # (`persp`: x where the drawing stands right. A drawing made face on, put on
        xc = cfg['persp']                      # a wall that runs to the vanishing point: each column's heights scaled
        X = np.arange(x0, x1) + 0.5            # about the eye line by its distance to VP over xc's, so its horizontals
        sc = (X - VP[0]) / (xc - VP[0])        # run to VP: the lintel rises, the step falls, toward the near side)
        Y = np.arange(y0, y1) + 0.5
        ysrc = VP[1] + (Y[:, None] - VP[1]) / sc[None, :] - y0 - 0.5
        yi = np.clip(np.round(ysrc).astype(int), 0, h - 1)
        e = e[yi, np.arange(w)[None, :]]
    if cfg.get('floor'):                       # (`floor`: yf, slope, xr. A drawing's step made level, its front edge put on
        yf, slope, xr = cfg['floor']           # the street's slope: below row yf each column pushed down by slope (x - xr),
        e = e.copy(); e0 = e.copy()            # what it uncovers the drawing's sill row: the recess floor seen as a wedge)
        for xi in range(w):
            d = int(round(slope * (x0 + xi + 0.5 - xr)))
            if d <= 0: continue
            r0 = yf - y0
            e[r0 + d:, xi] = e0[r0:h - d, xi]; e[r0:r0 + d, xi] = e0[r0, xi]
    e_zone = e

    def part_draft(fname):                     # (`model`: a part drawn from its own draft, the option chosen for it,
        ep = np.array(Image.open(os.path.join(EDITS, fname)).convert('RGB').resize((w, h), Image.BOX)).astype(float) / 255.0
        return shift((ep ** GAMMA) * 255.0, dy, dx)   # made from the same crop: the zone's registration holds)

    new, unew = orig.copy(), unlit0[..., :3].copy()
    glow = None
    for p, m, keep in zip(cfg['parts'], masks, keeps):
        pn, pu = new.copy(), unew.copy()           # (what the part is laid over: its feathered edge fades into it)
        e = part_draft(p['model']) if p.get('model') else e_zone
        is_lit = bool(p.get('lit')) and on is not None
        if is_lit: m = m & cov                       # (a lit part: the comp's pixels, taken lit)
        if p.get('outside_comp') and on is not None: m = m & ~cov   # (the street around a lit sign, not the sign)
        O = on if is_lit else orig
        if p['method'] == 'hist':
            out = O.copy()
            for c in range(3):
                src, refv = e[..., c][m], O[..., c][m]
                order = np.argsort(src, kind='stable'); v = np.empty_like(src); v[order] = np.sort(refv); out[..., c][m] = v
            if p.get('unlit') == 'lf_ratio':           # the unlit layer: this picture times the painter's darkening
                dark = np.stack([(gaussian_filter(unlit0[..., c], 4.0) + 1.0) / (gaussian_filter(O[..., c], 4.0) + 1.0) for c in range(3)], -1)
                new[m] = out[m]; unew[m] = np.clip(out * np.clip(dark, 0, 1.5), 0, 255)[m]
            else:
                ratio = (out + 1.0) / (O + 1.0)
                new[m] = out[m]; unew[m] = np.clip(unlit0[..., :3] * ratio, 0, 255)[m]
        elif p['method'] == 'detail':
            m = m.copy()
            if p.get('keep_lit'):
                Lo = lum(O); warm = ((O[..., 0] - O[..., 2]) > 10) & (Lo > 30)
                m &= ~(warm & ((Lo - gaussian_filter(Lo, 2.0)) > 4))
            hole = keep.copy()                     # (what is kept, a lantern or a lit pane, lends the wall none of its light)
            for q in p.get('fill', []): hole |= poly_mask(q, box)
            er = np.zeros_like(m)                  # `erase`: an object removed, the wall continued through it: no light
            for q in p.get('erase', []): er |= poly_mask(q, box)   # of its own, and the drawing's planks run down
            hole |= er                             # over it from the rows above (the draft drew the object there too)
            lf = lowpass_filled(O, hole, p['sigma'])
            if p.get('lf_fill'): lf = np.where(hole[..., None], wall_fill(O, p['lf_fill'], box, p['sigma']), lf)
            le = lum(e)
            for x in np.nonzero(er.any(0))[0]:
                ys = np.nonzero(er[:, x])[0]; le[ys, x] = le[max(ys[0] - 1, 0), x]
            if keep.any():                         # the draft's own drawing of what is kept (a bright lamp, a pane) filled
                he = binary_dilation(keep, iterations=2)   # from around, else its edge rings dark on the wall beside it
                le = np.where(he, lowpass_filled(np.repeat(le[..., None], 3, -1), he, 2.0)[..., 0], le)
            hf = le - gaussian_filter(le, p['sigma'])
            uhf = hf                               # (`tex`: inside q, the fine structure from (sx, sy) away, the wall under an
            if p.get('tex'):                       # object taken away: each layer's own, its low frequencies taken without
                hp = lambda Lm: Lm - lowpass_filled(np.repeat(Lm[..., None], 3, -1), hole, p['sigma'])[..., 0]   # the object)
                hs, uhs = hp(le), hp(lum(unlit0[..., :3])); uhf = hf.copy()
                for q, (sx, sy) in p['tex']:
                    tm = poly_mask(q, box); sh = lambda a: np.roll(np.roll(a, -sy, 0), -sx, 1)
                    hf = np.where(tm, sh(hs), hf); uhf = np.where(tm, sh(uhs), uhf)
            out = np.clip(lf + p['k'] * hf[..., None] * (lf + 1.0) / (lum(lf) + 1.0)[..., None], 0, 255)
            ratio = (out + 1.0) / (O + 1.0)
            ul = unlit0[..., :3]
            if p.get('unlit') == 'lf_ratio':           # the painter's darkening, smoothed (a ratio pixel by pixel blows up
                if er.any():                       # (an erased object's own darkening left out, and all but this wall's)
                    dh = ~(m & ~er); dark = (lowpass_filled(ul, dh, 4.0) + 1.0) / (lowpass_filled(O, dh, 4.0) + 1.0)
                else:
                    dark = np.stack([(gaussian_filter(ul[..., c], 4.0) + 1.0) / (gaussian_filter(O[..., c], 4.0) + 1.0) for c in range(3)], -1)
                new[m] = out[m]; unew[m] = np.clip(out * np.clip(dark, 0, 1.5), 0, 255)[m]   # where a blotch was black)
            elif hole.any():                       # where the smear was, the unlit layer is rebuilt the same way
                ulf = lowpass_filled(ul, hole, p['sigma'])
                if p.get('lf_fill'): ulf = np.where(hole[..., None], wall_fill(ul, p['lf_fill'], box, p['sigma']), ulf)
                uout = np.clip(ulf + p['k'] * uhf[..., None] * (ulf + 1.0) / (lum(ulf) + 1.0)[..., None], 0, 255)
                ur = np.where(hole[..., None], uout, np.clip(ul * ratio, 0, 255))
                new[m] = out[m]; unew[m] = ur[m]
            else:
                new[m] = out[m]; unew[m] = np.clip(ul * ratio, 0, 255)[m]
        elif p['method'] == 'direct':
            if p.get('erase'):                     # (`erase`: what the drawing put there that reads as mush, gone: the wall
                er = np.any([poly_mask(q, box) for q in p['erase']], 0)   # (`erase_from`) continued through it, its
                wl = poly_mask(p['erase_from'], box) if p.get('erase_from') else m   # low frequencies from around)
                e = np.where(er[..., None], lowpass_filled(e, er | ~wl, p.get('erase_sigma', 3.0)), e)
            fit = m if p.get('fit') in ('self', 'self_red') else ref   # (`fit='self'`: the tint fitted on the part
            A = [np.polyfit(e[..., c][fit], O[..., c][fit], 1) for c in range(3)]   # itself, a sign's colours on the
            ec = np.stack([np.clip(A[c][0] * e[..., c] + A[c][1], 0, 255) for c in range(3)], -1)   # painter's own;
            if p.get('fit') == 'self_red':         # 'self_red': its red and its other colours fitted apart, so a white
                rd = (e[..., 0] > 1.4 * e[..., 1]) & (e[..., 0] > 40)   # half keeps the painter's white, not a pink)
                for grp in (rd, ~rd):
                    g = m & grp
                    if g.sum() < 20: continue
                    Ag = [np.polyfit(e[..., c][g], O[..., c][g], 1) for c in range(3)]
                    eg = np.stack([np.clip(Ag[c][0] * e[..., c] + Ag[c][1], 0, 255) for c in range(3)], -1)
                    ec[grp] = eg[grp]
            if p.get('glow'):                      # (`glow`: x, y, r: the painter's light there, where brighter, given back
                gx, gy, gr = p['glow']; yy, xx = np.mgrid[y0:y1, x0:x1]   # to the drawing, fading out to r: a lit button)
                wgt = np.clip(1 - np.hypot(xx + 0.5 - gx, yy + 0.5 - gy) / gr, 0, 1)[..., None]
                gl = np.stack([gaussian_filter(O[..., c], 1.5) - gaussian_filter(ec[..., c], 1.5) for c in range(3)], -1)
                ec = np.clip(ec + wgt * np.clip(gl, 0, 255), 0, 255)
            if p.get('match'):                     # (`match`: its wall brought to the tint of the plaster over it, channel by
                q = p['match']                     # channel: the mean of `src` (x0, x1, v0, v1) in zone5_plaster over the mean
                c5, _, ch5, V5 = zone5_plaster(**q['plaster'])   # of `dst` here, on the part off `skip` and above v_min)
                Vb = V5[y0:y1, x0:x1]; Xb = np.arange(x0, x1)[None, :] + np.zeros((h, 1))
                box_ = lambda r: (Xb >= r[0]) & (Xb <= r[1]) & (Vb >= r[2]) & (Vb <= r[3])
                sk = np.any([poly_mask(k, box) for k in q.get('skip', [])], 0) if q.get('skip') else np.zeros_like(m)
                gm = m & ~sk & (Vb >= q.get('v_min', -9))
                tgt = c5[y0:y1, x0:x1][box_(q['src']) & ch5[y0:y1, x0:x1]].mean(0); own = ec[box_(q['dst']) & gm].mean(0)
                ec = ec.copy(); ec[gm] = np.clip(ec[gm] * (tgt / np.maximum(own, 1e-3)), 0, 255)
                print(f'{name}: wall tint matched to the plaster, gains {np.round(tgt / np.maximum(own, 1e-3), 3).tolist()}')
            if p.get('neon'):
                # the tubes and their light: warm, saturated, brighter than the board around them
                L = lum(ec); sat = ec.max(-1) - ec.min(-1)
                warm = (ec[..., 0] > ec[..., 2] + 20) & (ec[..., 0] > ec[..., 1] + 10)
                lit = m & warm & (sat > 25)
                # the board as it is unlit: its colour from the non-lit pixels around (normalised convolution)
                bd = lowpass_filled(ec, ~m | lit, 3.0)
                # the emblem (a disc at `emblem`: x, y, radius) is painted, not a tube: it stays in the base
                if p.get('emblem'):
                    cx, cy, r = p['emblem']; yy, xx = np.mgrid[y0:y1, x0:x1]
                    lit &= ~(((xx - cx) ** 2 + (yy - cy) ** 2) <= r * r)
                core = lit & (L > np.percentile(L[lit], 60)) if lit.any() else lit
                base = ec.copy()
                base[lit] = bd[lit]
                base[core] = 0.7 * bd[core] + 0.3 * np.array([62.0, 39.0, 45.0])   # the glass of an unlit tube
                glow = np.clip(ec - base, 0, 255) * lit[..., None]
                if p.get('emblem'):                # the neon lights the emblem too: part of its brightness goes with the light
                    disc = m & (((xx - cx) ** 2 + (yy - cy) ** 2) <= r * r)
                    base[disc] = 0.55 * ec[disc]; glow[disc] = 0.45 * ec[disc]
                new[m] = base[m]; unew[m] = base[m]
            elif p.get('unlit') == 'rel':
                # (a drawing whose lights are not where the painter's were: the power cut is the painter's own dark there,
                # his unlit layer smoothed over the part, with the drawing's shapes on it as ratios to their surroundings,
                # softened (urel): its frames and panes faint in the dark, none of its glow)
                s = p.get('usigma', 6.0); hole = ~m
                ulf = lowpass_filled(unlit0[..., :3], hole, s)
                Le = lum(ec); rel = (Le + 1.0) / (lum(lowpass_filled(ec, hole, s)) + 1.0)
                new[m] = ec[m]; unew[m] = np.clip(ulf * (rel ** p.get('urel', 0.6))[..., None], 0, 255)[m]
            elif p.get('unlit') == 'lf_ratio':
                # the unlit layer: the new picture times the painter's own darkening there (unlit over lit, smoothed),
                # so the lattice is the new one and the shut dojo as dark as the painter made it
                sig = 4.0                              # (channel by channel: the shut colour too, not only the darkness)
                dark = np.stack([(gaussian_filter(unlit0[..., c], sig) + 1.0) / (gaussian_filter(O[..., c], sig) + 1.0) for c in range(3)], -1)
                new[m] = ec[m]; unew[m] = np.clip(ec * np.clip(dark, 0, 1.5), 0, 255)[m]
            else:
                new[m] = ec[m]; unew[m] = ec[m]
        elif p['method'] == 'flat':                # a strip in shadow, even: each row one value across the strip (its
                                                   # pct percentile: above the black crumbs that broke its edge),
            from scipy.ndimage import gaussian_filter1d   # then softened down the rows (sigma_y), both layers
            fc = p.get('from_cols')                # (`from_cols`: x0, x1: each row's value taken there instead, the wall
            for src, dst in ((O, new), (unlit0[..., :3], unew)):   # beside carried across the strip, row by row)
                rows = np.nonzero(m.any(1))[0]; fl = src.copy()
                for y in rows:
                    xs = np.nonzero(m[y])[0]; xsrc = np.arange(fc[0] - x0, fc[1] - x0) if fc else xs
                    fl[y, xs] = np.percentile(src[y, xsrc], p.get('pct', 50), axis=0)
                fl = gaussian_filter1d(fl, p.get('sigma_y', 1.5), axis=0)
                dst[m] = fl[m]
        elif p['method'] == 'zone5':               # (B's facade in plaster: zone5_plaster, above the ray v0 (its ground floor
            c5, u5, ch5, V5 = zone5_plaster(p['face'], tuple(p['tone']), p['ch'])   # a zone of its own))
            m = m.copy()
            Vb = V5[y0:y1, x0:x1]; Xb = np.arange(x0, x1)[None, :] + np.zeros((h, 1))
            wp = m & ch5[y0:y1, x0:x1] & (Vb >= p['v0'])
            fl = np.zeros_like(m)                  # (`fill`: what goes into the plaster too, boxes on the rays (x0, x1, v0,
            for a, b, va, vb in p.get('fill', []):   # v1): a window taken out, the plaster from round it)
                fl |= (Xb >= a) & (Xb <= b) & (Vb >= va) & (Vb <= vb)
            fl &= m
            for src, dst in ((c5, new), (u5, unew)):
                sb = src[y0:y1, x0:x1]; dst[wp] = sb[wp]
                if fl.any(): dst[fl] = lowpass_filled(sb, ~wp | fl, p.get('fill_sigma', 3.0))[fl]
            m = wp | fl
        elif p['method'] == 'from_unlit':          # (the street as the power cut has it, brought to the lit street's level:
            r0 = p['ref']; rr = (slice(r0[1] - y0, r0[3] - y0), slice(r0[0] - x0, r0[2] - x0))   # a light that only the lit
            g = np.median((O[rr] + 1.0) / (unlit0[..., :3][rr] + 1.0), axis=(0, 1))          # layer had, gone; `ref` a box
            new[m] = np.clip(unlit0[..., :3] * g, 0, 255)[m]                                # where both are the same scene)
        elif p['method'] == 'paint':               # (one colour, lit layer only: a small thing drawn on the pixel grid)
            new[m] = np.array(p['rgb'], float)
            if p.get('unlit_rgb'): unew[m] = np.array(p['unlit_rgb'], float)
        elif p['method'] == 'navy':                # (the painter's green-black of a deep shadow made the night's navy, its own
            for arr in (new, unew):                # values kept as ratios: what is that dark and greener than blue)
                L = lum(arr); gb = m & (arr[..., 1] >= arr[..., 0] + 1) & (arr[..., 1] >= arr[..., 2] + 1) & (L < p.get('below', 10))
                ref = np.array(p['rgb'], float); k = np.clip(L / max(lum(ref[None, None, :])[0, 0], 1e-3), 0.5, 2.0)
                arr[gb] = (ref[None, None, :] * k[..., None])[gb]
        elif p['method'] == 'hand':                # (drawn on the pixel grid by a tool of its own, `fn`: module.function in
            import importlib                       # tools/; it changes the street and the power cut in place and gives back
            mod, fn = p['fn'].rsplit('.', 1)       # the lit comp laid over them (`comp`: its name), or None)
            c = getattr(importlib.import_module(mod), fn)(box, O, unlit0[..., :3], new, unew, m)
            if c is not None: COMP_OUT[name] = [p['comp'], c, None]
        elif p['method'] == 'tool':                # (a part drawn on the pixel grid by its own module in tools/ (`tool`): its
            import importlib                       # draw(street, power cut, box) gives both layers and what it changed)
            tn, tu, tm = importlib.import_module(p['tool']).draw(O, unlit0[..., :3].copy(), box)
            m = m & tm; new[m] = tn[m]; unew[m] = tu[m]
        elif p['method'] == 'shade':               # a shadow line: what is there darkened by f, both layers
            new[m] = new[m] * p['f']; unew[m] = unew[m] * p['f']
        elif p['method'] == 'copy':                # the painter's own pixels from beside (src: dx, dy), both layers
            sx, sy = p['src']                      # (`from_new`: the zone's new pixels there, an earlier part's, instead)
            cs, cu = (new.copy(), unew.copy()) if p.get('from_new') else (O, unlit0[..., :3])
            new[m] = np.roll(np.roll(cs, -sy, 0), -sx, 1)[m]; unew[m] = np.roll(np.roll(cu, -sy, 0), -sx, 1)[m]
        elif p['method'] == 'night':               # (a lit window's room shut for the night: night_room)
            m = night_room(name, p, m, box, on, cin, city, unlit, new, unew)
        if p.get('feather'):                       # its edge on the old painting: a ramp over `feather` pixels, no seam
            from scipy.ndimage import distance_transform_edt
            wgt = np.clip(distance_transform_edt(poly_mask(p['poly'], box)) / p['feather'], 0, 1)[..., None]
            new[m] = (wgt * new + (1 - wgt) * pn)[m]; unew[m] = (wgt * unew + (1 - wgt) * pu)[m]
        if is_lit:                                 # the new lit picture goes to the comp; the street under it (the window
            litp = new.copy()                      # shut) the same picture darkened as the painter's shut one, channel by
            if p.get('cover'):                     # (the grown edge: the darkening carried out from the old lit area)
                dark = (lowpass_filled(orig, ~cin, 2.0) + 1.0) / (lowpass_filled(on, ~cin, 2.0) + 1.0)
            else:
                dark = np.stack([(gaussian_filter(orig[..., c], 2.0) + 1.0) / (gaussian_filter(on[..., c], 2.0) + 1.0) for c in range(3)], -1)
            offp = np.clip(litp * np.clip(dark, 0, 1.5), 0, 255)   # channel; behind shut glass its detail as soft as
            if p.get('shut_k', 1.0) != 1.0:        # the painter's there (shut_k: the share of it kept)
                olf = np.stack([gaussian_filter(offp[..., c], 3.0) for c in range(3)], -1)
                offp = np.clip(olf + p['shut_k'] * (offp - olf), 0, 255)
            comp = COMP_OUT.setdefault(name, [cname, cb.copy(), csl])[1]
            sub = m[csl]; comp[..., :3][sub] = litp[csl][sub]; comp[..., 3][sub] = 255
            new[m] = offp[m]; unew[m] = np.clip(unlit0[..., :3] * (offp + 1.0) / (orig + 1.0), 0, 255)[m]
    if front.any() and cfg.get('fringe'):      # (`fringe`: the edge pixel of what stands in front, where it was a blend of its
        done = np.any(masks, 0)                # outline and the old background (brighter than its outline by more than
        for arr, src in ((new, orig), (unew, unlit0[..., :3])):   # `fringe`), blended again, half its outline, half the
            L = lum(src)                       # new background beside it
            for y in range(h):
                xs = np.nonzero(front[y])[0]
                if len(xs) < 3: continue
                for xe, inner, out in ((xs[0], xs[0] + 1, xs[0] - 1), (xs[-1], xs[-1] - 1, xs[-1] + 1)):
                    if 0 <= out < w and done[y, out] and L[y, xe] - L[y, inner] > cfg['fringe']:
                        arr[y, xe] = 0.5 * src[y, inner] + 0.5 * arr[y, out]
    if cfg.get('despeckle'):                   # (`despeckle` on the zone: what its parts laid side by side left as a lone
        from scipy.ndimage import median_filter   # bright pixel, the street's and the power cut's, takes its neighbours')
        done = np.any(masks, 0) | (cov if on is not None else False)
        for arr in (new, unew):
            med = np.stack([median_filter(arr[..., c], size=3) for c in range(3)], -1)
            spk = done & ((lum(arr) - lum(med)) > cfg['despeckle']); arr[spk] = med[spk]
    print(f'{name}: registered dx={dx} dy={dy} (gradient correlation {corr:.2f}); pixels changed {int((np.abs(new - orig).sum(-1) > 0).sum())}')
    city[y0:y1, x0:x1, :3], unlit[y0:y1, x0:x1, :3] = new, unew
    return glow, masks


def write_glow(glow, box):
    """The neon's light as street.js lays it (additive, alpha 255 where it adds anything): its bounding box."""
    x0, y0 = box[0], box[1]
    nz = glow.max(-1) > 2
    ys, xs = np.nonzero(nz)
    gx0, gy0, gx1, gy1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    g = glow[gy0:gy1, gx0:gx1]; a = (g.max(-1) > 2) * 255.0
    Image.fromarray(np.dstack([np.round(g), a]).astype(np.uint8), 'RGBA').save(NEON_OUT, 'WEBP', lossless=True, quality=100, method=6, exact=True)
    pos = dict(x=int(x0 + gx0), y=int(y0 + gy0), w=int(gx1 - gx0), h=int(gy1 - gy0))
    print('neon glow:', pos)
    return pos


def call(name):
    import base64, urllib.request
    name, _, opt = name.partition(':')         # (NAME:OPT: an option, from <zone>_opt<OPT>_prompt.txt to its own model)
    tag = f'_opt{opt}' if opt else ''
    cfg = ZONES[name]; x0, y0, x1, y1 = cfg['box']; s = cfg['scale']
    src = os.path.join(EDITS, f'{name}_before_on.webp')    # (a lit window's zone: the draft is asked of it lit)
    din = os.path.join(EDITS, f'{name}_draft_in.webp')     # (a zone over cleaned neighbours: asked of the street as
    if os.path.exists(din): src = din                      # it is now, the zones before it done)
    z = load(src if os.path.exists(src) else os.path.join(EDITS, f'{name}_before_city.webp'))[..., :3] / 255.0
    im = Image.fromarray((np.clip(z ** (1 / GAMMA), 0, 1) * 255).astype(np.uint8)).resize(((x1 - x0) * s, (y1 - y0) * s), Image.NEAREST)
    import io; buf = io.BytesIO(); im.save(buf, 'PNG')
    body = {"model": MODEL, "modalities": ["image", "text"], "usage": {"include": True}, "messages": [{"role": "user", "content": [
        {"type": "text", "text": open(os.path.join(EDITS, f'{name}{tag}_prompt.txt')).read().strip()},
        {"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()}}]}]}
    key = os.environ.get('OPENROUTER_API_KEY', 'proxy-injected')
    req = urllib.request.Request('https://openrouter.ai/api/v1/chat/completions', data=json.dumps(body).encode(),
                                 headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'})
    d = json.loads(urllib.request.urlopen(req, timeout=600).read())
    url = d['choices'][0]['message']['images'][0]['image_url']['url']
    Image.open(io.BytesIO(base64.b64decode(url.split(',', 1)[1]))).save(os.path.join(EDITS, f'{name}{tag}_model.webp'), 'WEBP', lossless=True, quality=100, method=6)
    print(name + tag, 'model answer saved; cost', d.get('usage', {}).get('cost'), '$')


def shop_off(city, masks_by_zone):
    """The closed shop's overlay (street.js: shopOff, laid over the street as the kitchen shuts): its old pixels on the
    eave and the vent cleared, the lattice transom's warm light added as it looks shut (the wood without the shop's light)."""
    c = SHOP_OFF; ax, ay = c['at']
    so = load(os.path.join(EDITS, c['src']))
    g = c.get('grow_top', 0)                       # rows added above the old overlay (street.js lays it that much higher)
    so = np.concatenate([np.zeros((g,) + so.shape[1:]), so], 0); ay -= g
    H, W = so.shape[:2]; box = (ax, ay, ax + W, ay + H)
    so[poly_mask(c['clear'], box)] = 0
    zb = ZONES[c['lit_from']]['box']; m = masks_by_zone[c['lit_from']][c['lit_part']]
    full = np.zeros(city.shape[:2], bool); full[zb[1]:zb[3], zb[0]:zb[2]] = m
    sub = full[ay:ay + H, ax:ax + W]; px = city[ay:ay + H, ax:ax + W, :3]
    lit = sub & (px[..., 0] > px[..., 2] + 15) & (lum(px) > 40)
    so[lit, :3] = px[lit] * np.array([0.2, 0.17, 0.24]); so[lit, 3] = 255     # (as dark as the painter's shut glass)
    Image.fromarray(np.clip(np.round(so), 0, 255).astype(np.uint8), 'RGBA').save(
        os.path.join(ROOT, 'assets', c['out']), 'WEBP', lossless=True, quality=100, method=6, exact=True)
    print('shop_off: cleared the old eave and vent, the lattice transom shut:', int(lit.sum()), 'px')


def swung(mask, deg, hook, box):
    """A mask turned by deg degrees about the hook (absolute x, y), in its box (nearest pixel)."""
    x0, y0, x1, y1 = box; h, w = mask.shape; hx, hy = hook[0] - x0, hook[1] - y0
    yy, xx = np.mgrid[0:h, 0:w]; t = np.deg2rad(deg); c, s = np.cos(t), np.sin(t)
    X, Y = xx + 0.5 - hx, yy + 0.5 - hy
    ix = np.floor(c * X + s * Y + hx).astype(int); iy = np.floor(-s * X + c * Y + hy).astype(int)
    ok = (ix >= 0) & (ix < w) & (iy >= 0) & (iy < h); out = np.zeros_like(mask); out[ok] = mask[iy[ok], ix[ok]]
    return out


def oden_overlays(before, after):
    """The oden's overlays brought to its new wall: in the lantern's frames, the wall it uncovers where it hung takes the
    new wall (its planks continued from under it), the wall around (within WALL_TOL of the layer before) the layer's
    change there (after - before); in the door's sliding leaf, its wood resampled from the new layer; the lantern itself
    and the drawn bars left as they are. From the overlays as tools/oden_interior.py and the lantern tool wrote them
    (tools/src/edits/<name>_before.webp)."""
    from scipy.ndimage import binary_fill_holes
    o = ODEN_OVL; lx, ly, lw, lh = o['lantern_box']; lbox = (lx, ly, lx + lw, ly + lh)
    rest = obj_masks([ODEN_LANTERN], before['city'][ly:ly + lh, lx:lx + lw, :3], lbox)   # the lantern at rest
    for name, tag in o['lantern']:
        A = load(os.path.join(EDITS, name + '_before.webp')); b, a = before[tag], after[tag]
        old = b[ly:ly + lh, lx:lx + lw, :3]; d = a[ly:ly + lh, lx:lx + lw, :3] - old; n = 0
        behind = a[ly:ly + lh, lx:lx + lw, :3].copy()   # the new wall behind it: its planks run down, so each column
        for x in np.nonzero(rest.any(0))[0]:            # of the lantern takes the wall just under it
            ys = np.nonzero(rest[:, x])[0]; yb = min(ys[-1] + 1, lh - 1); behind[ys, x] = behind[yb, x]
        for k in range(o['lantern_n']):
            f = A[:, k * lw:(k + 1) * lw]; R, B = f[..., 0], f[..., 2]
            lit = ((R > 90) & (R > B + 30)) if tag == 'city' else ((R > 18) & (R > B + 5))   # (the paper, lit or dark crimson)
            lan = binary_fill_holes(binary_dilation(lit, iterations=1))   # the lantern in this frame: its paper, and its
            lan |= binary_dilation(swung(rest, -o['lantern_angles'][k], o['lantern_hook'], lbox), iterations=1)   # shape at rest swung
            wall = (f[..., 3] > 250) & ~lan
            under = wall & rest                       # where the lantern hung: the wall it uncovers as it swings
            f[..., :3][under] = behind[under]
            near = wall & ~rest & (np.abs(f[..., :3] - old).max(-1) <= WALL_TOL) & (np.abs(d).max(-1) > 0)
            f[..., :3][near] = np.clip(f[..., :3][near] + d[near], 0, 255); n += int(under.sum() + near.sum())
        Image.fromarray(np.round(A).astype(np.uint8), 'RGBA').save(os.path.join(ROOT, 'assets', name + '.webp'), 'WEBP', lossless=True, quality=100, method=6, exact=True)
        print(name + ':', n, 'wall pixels brought to the new wall')
    A = load(os.path.join(EDITS, o['door'] + '_before.webp')); b, a = before['city'], after['city']
    px, py, pw, ph = o['pan_box']; n = 0
    c00, c01, r00, r01 = 22, 38, 8, 89            # the leaf at rest (the first cell): its columns and rows in the box
    for u0, v0 in o['pan_cells']:                  # the leaf slides left and grows a little at each step: each of its
        f = A[v0:v0 + ph, u0:u0 + pw]; op = f[..., 3] > 250   # pixels taken back to the leaf at rest (nearest), its wood
        cols = np.nonzero(op.any(0))[0]        # (below the glass) the new wood there when it was the old one
        if len(cols) < 2: continue
        c0, c1 = cols[0], cols[-1]; rows = np.nonzero(op[:, (c0 + c1) // 2])[0]; r0, r1 = rows[0], rows[-1]
        for u in range(c0, c1 + 1):
            sx = px + int(round(c00 + (u - c0) * (c01 - c00) / max(c1 - c0, 1)))
            for r in np.nonzero(op[:, u])[0]:
                sy = py + int(round(r00 + (r - r0) * (r01 - r00) / max(r1 - r0, 1)))
                if sy < o['pan_wood'] or sy >= b.shape[0]: continue
                if np.abs(f[r, u, :3] - b[sy, sx, :3]).max() <= PAN_TOL and np.abs(a[sy, sx, :3] - b[sy, sx, :3]).max() > 0:
                    f[r, u, :3] = a[sy, sx, :3]; n += 1
    Image.fromarray(np.round(A).astype(np.uint8), 'RGBA').save(os.path.join(ROOT, 'assets', o['door'] + '.webp'), 'WEBP', lossless=True, quality=100, method=6, exact=True)
    print(o['door'] + ':', n, 'pixels of the sliding leaf brought to the new wood')


def main():
    if '--call' in sys.argv: call(sys.argv[sys.argv.index('--call') + 1])
    os.makedirs(OUT, exist_ok=True)
    city = load(os.path.join(ROOT, 'assets', 'layer_city_off.webp')); unlit = load(os.path.join(ROOT, 'assets', 'street_unlit.webp'))
    for name, cfg in ZONES.items():                # the painter's own pixels back in every zone first
        x0, y0, x1, y1 = cfg['box']
        city[y0:y1, x0:x1] = load(os.path.join(EDITS, f'{name}_before_city.webp'))
        unlit[y0:y1, x0:x1] = load(os.path.join(EDITS, f'{name}_before_unlit.webp'))
    masks_by_zone = {}; before = dict(city=city.copy(), unlit=unlit.copy())
    for name, cfg in ZONES.items():                # then the zones, in order: each sees the ones before it
        glow, masks = zone(name, cfg, city, unlit); masks_by_zone[name] = masks
        if name == NEON_ZONE and glow is not None:
            json.dump(write_glow(glow, cfg['box']), open(os.path.join(EDITS, 'neon_glow_box.json'), 'w'))
    for name, cfg in ZONES.items():                # the patches, cut from the finished layers (any order lays the same)
        x0, y0, x1, y1 = cfg['box']
        for tag, a in (('city', city), ('unlit', unlit)):
            Image.fromarray(np.clip(np.round(a[y0:y1, x0:x1]), 0, 255).astype(np.uint8), 'RGBA').save(
                os.path.join(OUT, f'{name}_{tag}.webp'), 'WEBP', lossless=True, quality=100, method=6, exact=True)
    shop_off(city, masks_by_zone)
    oden_overlays(before, dict(city=city, unlit=unlit))
    for name, cfg in ZONES.items():                # (`comps`: lit windows' overlays that carry the wall a zone changed:
        x0, y0, x1, y1 = cfg['box']                # their pixels times the change the layer took there, as zone5 did)
        for cname, cx, cy in cfg.get('comps', []):
            A = load(os.path.join(EDITS, cname + '_before.webp')); h, w = A.shape[:2]
            b, a = before['city'][cy:cy + h, cx:cx + w, :3], city[cy:cy + h, cx:cx + w, :3]
            inz = np.zeros((h, w), bool); inz[max(y0 - cy, 0):max(y1 - cy, 0), max(x0 - cx, 0):max(x1 - cx, 0)] = True
            mm = (A[..., 3] > 0) & inz & (np.abs(a - b).max(-1) > 0)
            A[..., :3][mm] = np.clip(A[..., :3][mm] * ((a + 1) / (b + 1))[mm], 0, 255)
            Image.fromarray(np.round(A).astype(np.uint8), 'RGBA').save(os.path.join(ROOT, 'assets', cname + '.webp'), 'WEBP', lossless=True, quality=100, method=6, exact=True)
            print(cname + ':', int(mm.sum()), 'pixels of its wall brought to the new one')
    for name, cfg in ZONES.items():                # (`atlas`: a figure in a room night_room shut, her dark row (a power cut
        a = cfg.get('atlas')                       # while it is open) its lit row in that room's dark, at her depth; from
        if not a or name not in NIGHT: continue    # tools/src/edits/<name>_before.webp: rerun after her tool rewrites it)
        A = load(os.path.join(EDITS, a['name'] + '_before.webp')); r, W = a['dark'], a['w']; H = A.shape[0] - r
        lit = A[:H, :W]; op = lit[..., 3] > 0
        dk = NIGHT[name]['dark'](lit[..., :3], np.full(op.shape, float(a['z'])))[0]
        A[r:r + H, :W, :3][op] = np.clip(dk, 0, 255)[op]
        Image.fromarray(np.round(A).astype(np.uint8), 'RGBA').save(os.path.join(ROOT, 'assets', a['name'] + '.webp'), 'WEBP', lossless=True, quality=100, method=6, exact=True)
        print(a['name'] + ':', int(op.sum()), 'pixels of her dark row in the shut room\'s dark')
    for name, (cname, comp, _) in COMP_OUT.items():   # a lit window's comp, its new picture where it lit before
        Image.fromarray(np.clip(np.round(comp), 0, 255).astype(np.uint8), 'RGBA').save(
            os.path.join(ROOT, 'assets', cname + '.webp'), 'WEBP', lossless=True, quality=100, method=6, exact=True)
        print(cname + ': the lit window redrawn')


if __name__ == '__main__':
    main()
