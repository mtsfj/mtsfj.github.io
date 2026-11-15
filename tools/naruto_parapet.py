#!/usr/bin/env python3
"""The tops of the two buildings on the right, over Ichiraku and over the arcade, as the tops of real buildings, from a
small 3D model in the street's camera (each pixel's ray followed into it): Naruto's a deep flat-roofed concrete block,
the arcade's a low one, its ground floor under its tiled lean-to, Naruto's near side over it.

    (a module: tools/redraw_zones.py's zone 'naruroof' calls draw() on the street as the zones before it leave it, after
     'narufloor', whose roof edge and garden it redraws; it rewrites assets/roof_sway.webp (the garden's wind data, see
     below), street_sun, the end wall's windows' comps and the terrace's lights' comp, roof_lights.webp)
    python3 tools/naruto_parapet.py --before        once: the zone's before crops (tools/src/edits/naruroof_before_*.webp)
    python3 tools/naruto_parapet.py --preview OUT [SRC]   the zone drawn on the layers of SRC (default assets/), crops
                                                    before and after in OUT, the model's lines over x6 crops

The owner (2026-11-14, on tools/naruto_floor.py's roof edge): "toit Naruto toujours bizarre : gouttière trop de contraste,
forme pas logique et qui représente rien", "faut penser le haut comme un vrai haut d'immeuble avec détail, pas juste un
rectangle", "pareil pour les autres toits". What was there: on the street face a pale band along the roof's edge (the
slab's lit lip, read as a gutter), a darker parapet over it, a box at the near corner with a line across it, a T on the
far downpipe and a second downpipe from a socket under that box. A first pass (v1) had the logic right but read at 1:1
as large plain dark masses; v2 kept the logic and gave every surface its parts, its grain and its light (R27); v4 took
the painter's tall board wall over the arcade away; v5 gives Naruto's building its depth back over it, the AC unit
whole, and takes the downpipe away; v6 gives that end wall its face; v7 takes the arcade's parapet away (below).
The camera is the street's (tools/arcade_eave.py, tools/r6_sprites.py): the eye 1.41 m up on the street's axis, f 959.5
px, the vanishing point (700, 615); a line along the street at X m from the axis and Y m up runs on the ray
v = (Y - 1.41) / X (redraw_zones.ray's v; the interiors' camera, f 1400 and the eye 1.5 m, tools/ichiraku_interior.py,
puts the painting's lines on the same rays: f only scales the depths). Naruto's street face P is X_P = 10.1 m out (49.5 px a metre at x 1200: the
old railing's 1.1 m, tools/naruto_roof.py's PPM), its near side faces us at Z_N (P's corner, x 1236), its far end at C's
corner (x 1124); its rows are tools/naruto_floor.py's (the soffit's front edge V_LB and the coping's top V_CT kept, so the
floor under it, the window, the railing and the garden stay where they are).
- Naruto's building, a flat-roofed concrete block with a roof garden: a parapet flush with the facade, of its concrete
  (one face from the soffit's edge up: no lit lip, no band), its terrace 0.30 m over the soffit, the parapet 0.47 m over
  it; an aluminium coping on it (6.5 cm, 3 cm overhang): its top arris one crisp lit row (the sky), its face, its drip
  edge, the drip's shadow a dark row on the wall under it, a joint every ~1.6 m (three lengths along the street, one
  on the near side: a dark tick through the coping). The parapet's face in the painter's own grain (his pillar's
  concrete, its lightness over its local mean, laid as a texture), lighter up where the sky lights it, darker toward
  the near corner and toward its lower arris but for the arris itself (the street's light catches it); thin rain streaks
  from the coping's joints. Round the near corner (plumb at P's corner, its arris a lit column) the same rows run level
  across the near side, which faces us a step darker (turned from the street), down over the balcony's opening to the
  soffit, then as the near wall (one face, the same grain) down to the arcade's canopy. The owner on it: "cette façade
  face à nous, bizarre : on dirait qu'il y a un bâtiment entre Ichiraku et celui de l'arcade". So the near side is the
  front's own concrete (W's last pier's, by the corner) at 0.82 of its light, its corner with the front one crisp lit
  column from the roof slab down to the canopy, the roof slab's lower arris and the balcony's slab (its lit edge, its
  face, its lower arris, as over the opening) running round the corner across it at their own rows, a little lighter
  lower down; the painter's dark box over the canopy is that wall (and, left of the corner, the front's) carried down to
  the canopy, a flashing where the canopy's roof meets them. Past the arcade's far corner (x 1297) the arcade is low
  (below) and the near side shows over its roof, down to its coping. The building is deep (the owner on a back corner
  at x 1340: "l'immeuble de Naruto fait 50 cm de profondeur"): its back 12 m behind its front (X_BACK), so its near
  side, a frontal plane in this one-point perspective, runs on past the frame's edge (4.2 m of it at x 1456), its
  coping level across it at the roof's height (a joint every 1.6 m), the roof slab's arris and the floor slab across it
  at their rows, the sky only over the coping; that broad wall in a mottled grain of the painter's measure (wall_grain:
  his streaked texture, repeated over it, showed a motif and read as boards). Then its face (the owner: "Améliore cette
  façade": a big plain dark wall with one small window) as the image model painted it in its context crop at 22 h
  (R28: FACE_CROP x4, brightened; tools/src/edits/naruroof_face_draft.webp from naruroof_face_prompt.txt; lay_face): one
  tone of concrete with its grain and weathering streaks under the coping and the sills, its slab lines where they
  were; on Naruto's floor a sliding window lit through a drawn curtain (sill 1.6 m over the floor; its light the comp
  win_naru_side, a home's window in assets/street.js, on and off by its hours; in the layers its glass off, the
  curtain's folds faint on dark glass) and to its right a small frosted bathroom window, dark, its vent cap by it; on
  the ground floor, over the arcade's roof, the ramen shop's kitchen hood. Boxed down to the street's pixels (at 22 h
  the street's grade leaves the layer as it is), brought to the painter's concrete by a gain per channel (the near
  side's own median: the building keeps its one tone), laid on the near side's face, two pixels clear of the AC unit.
  The two windows lived in (the owner: "Faudra animer la fenêtre, celle-là, et la salle de bain, comme si quelqu'un
  vivait là"), their light as the image model painted it in their context crop at 22 h (R28: WIN_CROP x8, brightened;
  tools/src/edits/naruroof_windows_draft.webp, then naruroof_windows_fig_draft.webp painted on it; lay_windows): the
  room's window lit warm, its curtain half drawn on a glimpse of the lit room (a pendant lamp, a picture, a table), the
  bathroom's frosted pane lit warm-white, each street.js's to show (assets/win_naru_side.webp, win_naru_bath.webp: its
  NWIN block, on and off by their own clocks); a person's soft shadow on the curtain and a blurred figure behind the
  frosted pane (what the second draft darkens of the first: win_naru_side_fig.webp, win_naru_bath_fig.webp), which
  NWIN moves over the lit glass; in the layers the room's glass off as it now is (its curtain and room faint on dark
  glass), the bathroom's as the face's draft left it.
- The planters: the roof garden's shrubs, hedge and maple stand in concrete planters behind the parapet, their rims just
  showing over the coping under the plants (a lit top, its edge, the planter's face in shade over the coping's lit edge); the leaves the rims cover leave the garden's
  wind data (roof_sway.webp: no longer leaves, never shown there).
- The garden itself (the owner: "Améliore le jardin de toit de droite"), as the image model painted it in its context
  crop at 22 h (R28: GARDEN_CROP x8, brightened, on this zone's drawing; tools/src/edits/naruroof_garden_draft.webp from
  naruroof_garden_prompt.txt; lay_garden): the red-leafed tree's tiered pads on its thin trunk, a pruned pine, round
  clipped shrubs, a grass tuft and a pink azalea in concrete planters, a potted maple, a bamboo trellis with a climber,
  the hedge at the corner, lit from below by the city's glow, a warm rim from the street lamp. Over the coping only:
  first its ground (the old plants taken off: what each covered, from the wind data tools/naruto_floor.py wrote), then
  the draft where it differs from that ground (each plant whole), the sky clear round them; the power cut at the old
  garden's ratio. Its wind data written anew over GARDEN_CROP (street.js ROOF's box, 1124, 32): what each leaf covers in
  both layers, each plant's own leaves and clumps (PLANTS: the trees free up their crowns and out to their pads' ends,
  the pine stiffer; the shrubs, the pot and the azalea at their tops; the climber and the hedge calmer, the hedge still
  under the menu's text), where a leaf may show (over the coping).
- The terrace lived in (the owner: "le jardin de son toit peut être amélioré (parasol, j'en sais rien)"), as the image
  model painted it in its context crop at 22 h (R28: TERRACE_CROP x8, brightened, on the street as it is;
  tools/src/edits/naruroof_terrace_draft.webp from naruroof_terrace_prompt.txt; lay_terrace): a small parasol right of the
  red tree, behind the trellis, its fabric a faded sage, seen from below (its underside, its ribs); the slatted backs of two
  folding chairs over the coping under it; a string of small bulbs from its pole to a post at the roof's corner; a paper
  lantern from its edge. Laid over the sky only (the plants, the trellis and the parapet in front), the parasol a little
  lower than painted (under the menu's text); in the layers off (the bulbs dark on their wire, the lantern's paper in the
  night's glow, the underside lit from the street below); lit (the bulbs, the lantern, their glow on the underside)
  assets/roof_lights.webp, street.js's RLT block: on warm evenings, its own hours. Its hem in the garden's wind data (the
  canopy's last rows, freer at its edge; still under the text), what the new things hide theirs.
- No downpipe (the owner, circling the one down the pillar by the balcony: "Vire cette gouttière"): no scupper, no rain
  head, no pipe, no bracket; the pillar's face one wall from the coping to the sign, in the painter's grain on the
  cleaned pillar's light (its rows' light smoothed down the wall, darker into C's corner), the coping unbroken to the
  far corner; the pillar's side face beside it, in the balcony's recess, the painter's grain too, a little lighter lower
  down. The street lamp's light on the far end as before (tools/naruto_roof.lamp's warm share, the lit layer only).
- The arcade's building, the right neighbour (the owner on the painter's tall board wall over it, under a high tiled
  eave: "je sais pas à qui ça appartient, le truc en bois", then "Et le mur, juste vire-le : au-dessus de l'arcade, fais
  juste un truc clean"; then, on the parapet and coping v4 ran over its lean-to: "Boudin en béton derrière la clim :
  c'est quoi ça ? Ça représente rien, non ?"): a low building, its ground floor under its tiled lean-to
  (tools/arcade_eave.py's canopy), the lean-to's roof running up to Naruto's near side and meeting it on the ray V_FOOT
  with a flashing (its fold lit by the sky, its face, a shade on the wall over it); left of x 1346, where the lean-to's
  far end rises to its top and the painter's dark showed past it, the near side carried down to that edge, the
  flashing along it. Over it Naruto's near side, its concrete down to the flashing (the board wall, its tiled eave, its
  row of round tiles, the painter's pipes and line on it gone; under the parapet's top that was there, ray V_ATOP, the
  wall's last ten rows over it repeated: the drafts were drawn with it, none of theirs is laid there). The AC unit on
  the lean-to (tools/arcade_eave.py's box, on its stand), against that wall: as the zones before leave it (ac_unit:
  what is not the painter's green black, from its top rim down, his pipes over it and past its end left out), its
  pipes in a cover out of its valves' box down the wall into the lean-to's roof at the flashing (ac_duct); then (the
  owner: "il manque la moitié de la
  ventilation": its side was a dark open frame) redrawn whole by the image model in its context crop (R28: DRAFT_CROP
  x4, brightened, on this zone's drawing; tools/src/edits/naruroof_ac_draft.webp from naruroof_ac_prompt.txt): its fan
  guard fully round in its casing, its side one solid panel with its service cover, the valves' cover low on it and its
  pipes into the cover, its warm rim. Boxed down to the street's pixels, brought to the painting's colours by a gain per
  channel (its wall to this zone's), laid where it differs from this zone's drawing, within the unit's silhouette in the
  street's camera (unit_reach; lay_draft);
  the power cut at the painter's ratios on his unit and its rim.
Colours are the painting's (Naruto's concrete from his pillar and the near strip; the flashing a blue-grey of the
lean-to's metal). The power cut (street_unlit): the same, but the street lamp's share (the far end,
the metal) and the side window's light (a comp, off). street_sun (the low sun's
share) is 0 on what is redrawn; night_far stays 0 (the street's, the sky's). Needs Pillow, numpy, scipy.
"""
import os
import sys
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, binary_fill_holes, label, distance_transform_edt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import naruto_floor as NF   # noqa: E402  (the floor's rows: the soffit's edge, the coping's top, P's corners)
import naruto_roof as NR    # noqa: E402  (the street lamp's share near the far end)
import arcade_eave as AE    # noqa: E402  (the arcade's lean-to: where it meets its wall; the AC unit on it)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDITS = os.path.join(ROOT, 'tools', 'src', 'edits')
ASSETS = os.path.join(ROOT, 'assets')
BOX = (1120, 0, 1456, 376)                     # the zone (redraw_zones.py 'naruroof')
NF_BOX = NF.BOX                                # (the zone 'narufloor': street_sun and roof_sway are its own there)
VPX, VPY = 700.0, 615.0
F, EYE = 959.5, 1.41                           # the street's camera (tools/arcade_eave.py)
LUMA = np.array([0.299, 0.587, 0.114])

# Naruto's building (metres: X out from the street's axis, Y up, Z ahead)
XP = 10.1                                      # its street face P
Z_of = lambda x: F * XP / (x - VPX)            # P's depth at column x
ZN, ZF = Z_of(NF.XPN), Z_of(1124.0)            # its near side (P's corner), its far end (C's corner)
ZPIL = Z_of(NF.XPF)                            # the pillar's edge (the balcony from there to ZN)
XW = XP * NF.KW                                # the window wall W (the near wall from its corner)
Y_LB = EYE + NF.V_LB * XP                      # the soffit's front edge (the parapet's foot on P)
Y_CT = EYE + NF.V_CT * XP                      # the coping's top
COP, OVH = 0.065, 0.03                         # the coping's height, its overhang
Y_T = Y_LB + 0.30                              # the terrace
X_BACK = XP + 12.0                             # its back: 12 m behind its front (its near side, a frontal plane, runs on
DEEP = X_BACK - XP                             # past the frame's edge: at x 1456 it is 4.2 m deep)
JOINTS_P = [ZN + k * (ZF - ZN) / 3 for k in (1, 2)]   # the coping's joints along P (three lengths)
JOINTS_N = [XP + 1.6 * k for k in range(1, 8)]   # and on the near side, every 1.6 m
NEAR_K = 0.82                                  # the near side's light over the front's (turned from the street)
SLAB_ROWS = (262, 275)                         # the balcony's slab at the near corner (tools/naruto_floor.py's YFL, YSB)
CANOPY_X = (1270, 1297)                        # where the arcade's canopy meets Naruto's walls under it (its flashing)
STRIP = (1279, 1297, 312)                      # the near wall beside the window: its columns, down to the box over the awning
# the planters behind the parapet: where the garden's plants stand over the coping (from roof_sway.webp's leaves), their
# rims two rows over the coping's top
RIM_GAP = 3                                    # (spans of plants closer than this are one planter)
# the arcade's building, the right neighbour, a low one (the owner, v4: "Et le mur, juste vire-le : au-dessus de
# l'arcade, fais juste un truc clean"; v7, on the parapet and coping drawn over its lean-to: "Boudin en béton derrière la
# clim : c'est quoi ça ? Ça représente rien, non ?"): its ground floor under its tiled lean-to (tools/arcade_eave.py's
# canopy), whose roof runs up to Naruto's near side and meets it on the ray V_FOOT, a flashing there; its street face XA
# (its far corner at x 1297); V_ATOP the ray of the parapet's top that was there (the drafts below were drawn with it)
XA = (1297.0 - VPX) * ZN / F
V_FOOT = (float(AE.roof_y(AE.XW)) - AE.EYE) / AE.XW     # (0.4401)
Y_FOOT = EYE + V_FOOT * XA
V_ATOP = V_FOOT + 0.036
FLASH = (np.array((26.0, 36.0, 58.0)), np.array((15.0, 22.0, 38.0)))   # the flashing: its lit fold, its face
LEAN_END = 1346                                # (left of this the lean-to's far end edge rises to its top: under it, past
                                               # its end, the painter's dark, now the near side down to its edge)
# the AC unit on the lean-to (tools/arcade_eave.py's, as the zones before leave it), kept: its face's top on the ray
# AE.VTOP from its far edge (AE.UF), its end's top level (its near top corner's row) to AC_X[1], its valves under it
# to the frame; what the painter had round it on the wall (a pipe up from its top, one up the far right, a line along
# its top to the frame) goes with the wall; its pipes in a cover from its valves down into the arcade's roof (DUCT)
AC_X = (1352, 1448)
AC_TOP = 194                                   # (its end's top rim, the painter's: 2 rows over AE.VTOP's)
DUCT = (1443, 1447, 264)                       # (the cover's columns, its top row: from the valves' box, down)
# what is detailed there (R28) as the image model redrew it in its context crop (DRAFT_CROP x4, brightened, on this zone's
# drawing without it; tools/src/edits/naruroof_ac_draft.webp from naruroof_ac_prompt.txt; the owner: "il manque la moitié
# de la ventilation"): the AC unit whole and solid (its fan guard fully round, its casing, its side panel, its service
# valves' cover and their pipes into its cover), laid where the draft differs from that drawing, in the unit's reach
# (DRAFT_AC: from its far edge to the frame, from its top down to the lean-to); the small window it drew too (DRAFT_WIN,
# kept out of its colours' fit) is the face's now (below)
DRAFT = 'naruroof_ac_draft.webp'
DRAFT_CROP = (1280, 96, 1456, 336)
DRAFT_AC = (1345, 185)
DRAFT_WIN = (1296, 108, 1362, 186)
# Naruto's near side, its face (the owner: "Améliore cette façade"; R28): the image model's painting of it in its context
# crop at 22 h (FACE_CROP x4, brightened, the street as this zone draws it: at that hour the street's grade leaves the
# layer as it is; tools/src/edits/naruroof_face_draft.webp from naruroof_face_prompt.txt): the concrete in one tone with
# its grain and weathering streaks under the coping and the sills, its slab lines, on Naruto's floor a sliding window
# lit through a drawn curtain (LIT: its reach; its glass the draft's warm pixels there) and a small frosted bathroom
# window (FROST: its glass) with a vent cap by it, on the ground floor the ramen shop's kitchen hood; laid on the near
# side's face but round the AC unit; the lit window's light a comp (LIT_COMP, a home's window in assets/street.js)
FACE_DRAFT = 'naruroof_face_draft.webp'
FACE_CROP = (1216, 0, 1456, 360)
LIT = (1300, 128, 1358, 188)
FROST = (1393, 121, 1419, 136)
LIT_COMP = 'win_naru_side.webp'
# the two windows lived in (the owner: "Faudra animer la fenêtre, celle-là, et la salle de bain, comme si quelqu'un vivait
# là"; R28): their light as the image model painted it in their context crop at 22 h (WIN_CROP x8, brightened, on this
# zone's drawing; tools/src/edits/naruroof_windows_draft.webp from naruroof_windows_prompt.txt): the room's window lit
# warm, its curtain half drawn, a glimpse of the lit room; the bathroom's frosted pane lit warm-white; then on that
# (naruroof_windows_fig_draft.webp from naruroof_windows_fig_prompt.txt) a person's soft shadow on the curtain and a
# blurred figure behind the frosted pane: what each darkens of the lit glass, the figures street.js moves (NWIN). The room
# window's light over ROOM (LIT_COMP), its figure over ROOM_FIG; the bathroom's over BATH (BATH_COMP), its figure over
# BATH_FIG
WIN_CROP = (1296, 96, 1424, 224)
WIN_DRAFT, WIN_FIG_DRAFT = 'naruroof_windows_draft.webp', 'naruroof_windows_fig_draft.webp'
ROOM = LIT
ROOM_FIG = (1332, 146, 1355, 182)
BATH = (1389, 118, 1424, 140)
BATH_FIG = (1388, 122, 1406, 137)
BATH_COMP = 'win_naru_bath.webp'
# the roof garden over the parapet (the owner: "Améliore le jardin de toit de droite"; R28): the image model's painting
# of it in its context crop at 22 h (GARDEN_CROP x8, brightened, on this zone's drawing; tools/src/edits/
# naruroof_garden_draft.webp from naruroof_garden_prompt.txt; lay_garden): the red-leafed tree's tiered pads, a pruned
# pine, round clipped shrubs, a grass tuft and a pink azalea in their concrete planters, a potted maple, a bamboo trellis
# with a climber, the hedge at the corner; laid where it differs from the garden's ground (the zone's drawing with the
# old plants taken off: their wind data's ground) over the coping; its wind data written anew (assets/roof_sway.webp,
# over GARDEN_CROP: street.js ROOF's box), each plant its own (PLANTS: its kind, its reach, how free)
GARDEN_DRAFT = 'naruroof_garden_draft.webp'
GARDEN_CROP = (1124, 32, 1252, 160)
GARDEN_UNLIT = np.array((0.92, 0.94, 0.96))   # (the old garden's power cut over its lit layer: the street lamp's share)
OLD_SWAY_AT = (1127, 34)                       # (tools/naruto_floor.py's wind data's box: the old garden's)
# (kind: 1 a tree (freer up its crown and out to its pads' ends), 2 a shrub (its top rows), 3 a climber or the hedge (its
# top rows, calmer); leaf: which of its pixels are leaves (red, green, any); its reach in the street; its freedom)
PLANTS = [(2, 'green', (1156, 92, 1188, 111), 0.8),     # the clipped shrubs (the small ones first: each claims its own)
          (2, 'green', (1149, 109, 1168, 123), 0.8),
          (2, 'green', (1128, 126, 1148, 140), 0.8),
          (2, 'green', (1125, 115, 1142, 128), 1.0),    # the grass tuft
          (2, 'red', (1139, 117, 1158, 132), 0.8),      # the azalea
          (2, 'red', (1177, 76, 1195, 93), 0.9),        # the potted maple
          (3, 'green', (1195, 52, 1214, 84), 0.7),      # the climber on its trellis
          (1, 'green', (1132, 90, 1162, 121), 0.7),     # the pine's pads (stiffer)
          (1, 'red', (1132, 48, 1199, 92), 1.0),        # the red-leafed tree's pads
          (3, 'any', (1212, 34, 1250, 62), 0.6)]        # the hedge at the corner

# the terrace lived in (the owner: "le jardin de son toit peut être amélioré (parasol, j'en sais rien)"; R28, R30): the image
# model's painting of it in its context crop at 22 h (TERRACE_CROP x8, brightened, on the street as it is; tools/src/edits/
# naruroof_terrace_draft.webp from naruroof_terrace_prompt.txt; lay_terrace): a small parasol right of the red tree, behind
# the trellis, its fabric a faded sage; the slatted backs of two folding chairs over the coping under it; a string of small
# bulbs from its pole to a post at the roof's corner; a paper lantern hanging from its edge. Taken from the draft where it
# differs from its sky, in its parts' boxes (T_*: the draft's columns and rows in the crop, at TERRACE_SHIFT: its whole-pixel
# offset on the near side's wall), and laid over the sky only (behind the plants, the trellis, the parapet); the parasol and
# the lantern T_DROP rows lower than painted (under the menu's text), the string sheared down to them from the post. Lit
# (the bulbs, the lantern, their glow on the parasol's underside): LIGHTS_COMP, street.js's to show on warm evenings; in the
# layers off (the bulbs dark on their wire, the lantern's paper in the night's glow, the underside lifted by the street's
# light from below). The parasol's hem in the garden's wind data (its last rows, freer at the edge), still under the text
TERRACE_DRAFT = 'naruroof_terrace_draft.webp'
TERRACE_CROP = (1132, 0, 1260, 128)
TERRACE_SHIFT = (-1, 2)                        # (the draft's offset, columns and rows: best on the near side's wall)
T_CANOPY, T_POLE, T_LANTERN = (42, 26, 96, 44), (67, 42, 73, 66), (44, 40, 55, 49)
T_STRING, T_STRING_ENDS = (70, 30, 112, 49), (71, 104)
T_CHAIRS = [(59, 60, 65, 67), (74, 60, 84, 67)]
T_DROP = 8
T_STILL_ABOVE = 42                             # (the street's row: the hem moves only below it, under the menu's text)
LIGHTS_COMP = 'roof_lights.webp'
LIGHTS_BOX = (1172, 34, 70, 26)              # (its box: street.js RLT's)
BULB_OFF = np.array((34.0, 28.0, 30.0))

GRAIN = 0.05


def boxes():
    """the model: (name, lo, hi) boxes, axis-aligned"""
    B = [('par', (XP, Y_LB, ZN), (XP + 0.25, Y_CT - COP, ZF)),                     # the parapet and the slab on P
         ('pil', (XP, 0.0, ZPIL), (XP + 0.6, Y_LB, ZF)),                           # the pillar under it
         ('near', (XP, Y_LB, ZN), (XP + DEEP, Y_CT - COP, ZN + 0.25)),             # the near side's parapet and slab end
         ('near', (XW, 0.0, ZN), (XP + DEEP, Y_LB, ZN + 3.0)),                     # the near wall under the slab
         ('cop', (XP - OVH, Y_CT - COP, ZN - OVH), (XP + 0.25 + OVH, Y_CT, ZF)),   # the coping on P
         ('cop', (XP - OVH, Y_CT - COP, ZN - OVH), (X_BACK + OVH, Y_CT, ZN + 0.25 + OVH))]   # on the near side
    return B


def cast(box):
    """each pixel's ray (its centre) into the model: the nearest hit's name, its normal and point"""
    x0, y0, x1, y1 = box
    xs = np.arange(x0, x1) + 0.5; ys = np.arange(y0, y1) + 0.5
    X, Yp = np.meshgrid(xs, ys)
    d = np.stack([(X - VPX) / F, (VPY - Yp) / F, np.ones_like(X)])
    o = np.array([0.0, EYE, 0.0])
    h, w = X.shape
    best = np.full((h, w), np.inf); name = np.full((h, w), '', 'U8'); nrm = np.zeros((3, h, w))
    for nm, lo, hi in boxes():
        tmin = np.full((h, w), -np.inf); tmax = np.full((h, w), np.inf); ax = np.zeros((h, w), int); sg = np.zeros((h, w))
        for k in range(3):
            with np.errstate(divide='ignore', invalid='ignore'):
                t1 = (lo[k] - o[k]) / d[k]; t2 = (hi[k] - o[k]) / d[k]
            a = np.minimum(t1, t2); b = np.maximum(t1, t2)
            new = a > tmin
            ax = np.where(new, k, ax); sg = np.where(new, np.where(t1 < t2, -1.0, 1.0), sg)
            tmin = np.maximum(tmin, a); tmax = np.minimum(tmax, b)
        hit = (tmax >= tmin) & (tmin > 0) & (tmin < best)
        best[hit] = tmin[hit]; name[hit] = nm
        for k in range(3):
            nrm[k][hit] = np.where(ax[hit] == k, sg[hit], 0.0)
    P = o[:, None, None] + best[None] * d
    name[(name == 'par') & (nrm[2] < -0.5)] = 'near'                 # (the parapet's end, turned to us, is the near side)
    return name, nrm, P


def first_row(yline):
    return int(np.ceil(yline - 0.5))


def under_old_top(box):
    """over box: the pixels under the parapet's top that was over the arcade's lean-to (its ray V_ATOP, from x 1297; a row
    of margin; its coping's overhang from x 1293), which the drafts below were drawn with: none of theirs is laid there"""
    x0, y0, x1, y1 = box
    m = np.zeros((y1 - y0, x1 - x0), bool)
    for x in range(max(x0, 1293), x1):
        m[max(int(np.floor(AE.ray_y(x, V_ATOP))) - 1 - y0, 0):, x - x0] = True
    return m


def specks(m, c):
    """over m's frame: its dark pixels (luminance under 8 in c) with three or fewer of m's pixels round them: specks"""
    nb = sum(np.roll(np.roll(m, dy, 0), dx, 1).astype(int) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dy or dx)
    return m & (c @ LUMA < 8) & (nb <= 3)


def unit_reach(box):
    """over box: the AC unit's silhouette in the street's camera (tools/arcade_eave.py's box: its face along the street
    from its top's ray, the painter's rim a few rows over it, to its bottom's, from its far edge, x 1359, on: no stub of
    the draft's past it; its end; its valves and their pipes' cover down to the lean-to): where its draft is laid"""
    x0, y0, x1, y1 = box
    m = np.zeros((y1 - y0, x1 - x0), bool)
    for x in range(max(x0, 1359), min(x1, 1452)):
        if x < 1405: a, b = int(np.floor(AE.ray_y(x, AE.VTOP))) - 5, int(np.ceil(AE.ray_y(x, AE.VB))) + 1
        elif x < 1443: a, b = 191, 293
        else: a, b = 0, 0
        if 1428 <= x < 1443: a, b = min(a, 255), max(b, foot_row(x))   # (its pipes' cover past it: ac_duct's)
        m[max(a - y0, 0):max(b - y0, 0), x - x0] = True
    return m


def wall_bottom(M, box, x):
    """the first row under the zone's drawing in column x (x 1297 on): the lean-to's top there, or its end's edge"""
    x0, y0, x1, y1 = box
    y = foot_row(x)
    while y < y1 and M[y - y0, x - x0]: y += 1
    return y


def foot_row(x):
    """the first row of the arcade's lean-to at column x (tools/arcade_eave.py's roof: the pixels whose centre's ray meets
    it short of its wall)"""
    return int(np.ceil(AE.ray_y(x, V_FOOT) - 0.5))


def mask(box, sign):
    """the pixels Naruto's model redraws (the rest of the box as the zones before it leave it)"""
    x0, y0, x1, y1 = box; h, w = y1 - y0, x1 - x0
    M = np.zeros((h, w), bool)
    for x in range(1124, x1):
        i = x - x0
        ct, pf, lt, lb = NF.edge_rows(x)
        if x < NF.XPF: M[ct - y0:sign[x] - y0, i] = True               # the pillar's face, its downpipe, to the sign
        elif x < NF.XPN: M[ct - y0:lb - y0, i] = True                  # P: the parapet and the slab's edge
        elif x < STRIP[0]: M[ct - y0:86 - y0, i] = True                # the near side over the balcony's opening
        elif x < STRIP[1]: M[ct - y0:STRIP[2] - y0, i] = True          # the near wall, its downpipe gone, to the awning
        else: M[:foot_row(x) - y0, i] = True                          # over the arcade's lean-to: Naruto's
                                                                       # near side, the sky (the AC unit: see draw)
    return M


def palette(city):
    """the painting's colours for the model's surfaces, sampled on the layers as the zones before leave them"""
    med = lambda a, xs, ys: np.median(a[ys[0]:ys[1], xs[0]:xs[1], :3].reshape(-1, 3), 0)
    par = med(city, (1128, 1141), (176, 236))           # Naruto's concrete: his pillar's face (under the parapet)
    pier = med(city, (1269, 1278), (120, 250))           # his front's concrete by the corner: W's last pier
    return dict(par=par, near=pier * NEAR_K, pier=pier,
                cop=par * 1.45, cop_top=par * 2.8, cop_low=par * 1.2, rim=par * 1.15, rim_top=par * 1.9, rim_face=par * 0.6)


def grain(shape, seed, s=0.7):
    n = gaussian_filter(np.random.default_rng(seed).normal(size=shape), s)
    return n / (n.std() + 1e-9)


def painter_grain():
    """the painter's concrete grain: his pillar's face as he painted it (this zone's before crop, x 1125..1143, y
    180..330), each pixel's lightness over its local mean (sigma 4), softened"""
    b = np.asarray(Image.open(os.path.join(EDITS, 'naruroof_before_city.webp')).convert('RGB')).astype(float)
    L = b[180:330, 1125 - BOX[0]:1144 - BOX[0]] @ LUMA + 1.0
    g = np.clip(L / gaussian_filter(L, 4.0), 0.7, 1.35) ** 0.6
    return np.concatenate([g, g[:, ::-1]], 1)


def wall_grain(shape, seed):
    """a concrete grain for a wall too broad for the painter's texture (laid by turns over it, it would show as a motif;
    streaked as his pillar's, it would read as boards): mottled, a little longer down the wall, and a fine speckle, 0.07
    of its light"""
    r = np.random.default_rng(seed)
    a = gaussian_filter(r.normal(size=shape), (3.0, 2.0)); b = gaussian_filter(r.normal(size=shape), 0.7)
    n = 0.7 * a / a.std() + 0.5 * b / b.std()
    return np.clip(1 + 0.07 * n / n.std(), 0.85, 1.15)


def tile(tex, h, w, oy=0, ox=0):
    """tex laid over (h, w), mirrored by turns"""
    th, tw = tex.shape
    ys = (np.arange(h) + oy) % (2 * th); ys = np.where(ys < th, ys, 2 * th - 1 - ys)
    xs = (np.arange(w) + ox) % (2 * tw); xs = np.where(xs < tw, xs, 2 * tw - 1 - xs)
    return tex[ys][:, xs]


def runs_from_top(m):
    """per pixel of mask m: its rank in its column's run (0 at the run's first row), and the run's length"""
    h, w = m.shape; rk = np.zeros((h, w), int); ln = np.zeros((h, w), int)
    for i in range(w):
        y = 0
        while y < h:
            if not m[y, i]: y += 1; continue
            e = y
            while e < h and m[e, i]: e += 1
            rk[y:e, i] = np.arange(e - y); ln[y:e, i] = e - y; y = e
    return rk, ln


def screen_dist(P, which, at):
    """how far (px) a hit point is from a line across a surface: along P (receding: Z) or the near side (frontal: X)"""
    P = np.where(np.isfinite(P), P, 1e6)                             # (no hit: far away)
    if which == 'near':
        return (P[0] - at) * F / np.maximum(P[2], 1.0)
    return (at - P[2]) * F * XP / np.maximum(P[2], 1.0) ** 2


def shade(box, name, nrm, P, pal, M, city, unlit):
    """Naruto's model's colours over M: (the lit layer before the lamp's share, the power cut, where that share applies)"""
    x0, y0, x1, y1 = box; h, w = name.shape
    X = np.arange(x0, x1)[None, :] + np.zeros((h, 1), int); Yr = np.arange(y0, y1)[:, None] + np.zeros((1, w), int)
    col = np.zeros((h, w, 3)); n = grain((h, w), 23)
    pg = tile(painter_grain(), h, w, 17, 5)
    pg = np.where((name == 'near') & (X >= STRIP[0]), wall_grain((h, w), 61), pg)   # (the near wall, broad)
    lampable = np.ones((h, w), bool)
    # the coping: its top arris one crisp lit row, its face, its drip edge; the near side's a step darker; a joint every
    # ~1.6 m a dark tick through it
    m = (name == 'cop') & M
    rk, ln = runs_from_top(m)
    c = np.where((rk == 0)[..., None], pal['cop_top'], np.where(((rk == ln - 1) & (ln > 2))[..., None], pal['cop_low'], pal['cop']))
    turned = nrm[2] < -0.5
    c = c * np.where(turned, 0.85, 1.0)[..., None]
    c = np.where((nrm[1] < -0.5)[..., None], pal['cop_low'] * 0.7, c)
    dz = np.stack([screen_dist(P, 'p', z) for z in JOINTS_P]); dx = np.stack([screen_dist(P, 'near', x) for x in JOINTS_N])
    pick = lambda D: D[np.argmin(np.abs(D), 0), np.arange(h)[:, None], np.arange(w)[None, :]]
    dj = np.where(turned, pick(dx), pick(dz))
    c = np.where((np.abs(dj) < 0.5)[..., None], c * 0.4, c)
    col[m] = (c * (1 + 0.03 * n[..., None]))[m]
    # the walls: P (the parapet over the soffit, over the pillar), the near side and the near wall: the drip's shadow
    # under the coping, the painter's grain, the light (below)
    wall = ((name == 'par') | (name == 'pil') | (name == 'near')) & M
    rk, ln = runs_from_top(wall)
    k = np.where(rk == 0, 0.45, 1.0) * (1 - 0.2 * np.exp(-np.maximum(rk - 1, 0) / 2.0))
    onp = (name == 'par') & (X >= NF.XPF)
    lbr = np.array([first_row(NF.Y(x + 0.5, NF.V_LB)) for x in range(x0, x1)])[None, :] + np.zeros((h, 1), int)
    d_lb = lbr - 1 - Yr
    t = np.clip(rk / np.maximum(ln - 1, 1), 0, 1)                    # (0 under the coping, 1 at the lower arris)
    corner = np.clip((X - 1195.0) / (NF.XPN - 1195.0), 0, 1) ** 1.5   # (toward the near corner)
    kp = (1.12 - 0.2 * t) * (1 - 0.14 * corner) * np.where(d_lb == 0, 1.3, 1.0)
    k = np.where(onp, k * kp, k)
    onn = name == 'near'
    k = np.where(onn & (Yr < 86), k * (1.1 - 0.12 * np.clip((Yr - 49) / 36.0, 0, 1)), k)
    k = np.where(onn & (X >= NF.XPN) & (Yr == 85), k * 1.25, k)       # (the roof slab's lower arris, round the corner on)
    k = np.where(onn & (X == int(NF.XPN)) & (Yr < 86), k * 1.3, k)           # (the corner's arris over the opening)
    # the near wall beside the window, the same face down to the arcade's canopy and, past it, over the arcade's low roof
    # to the back corner: its corner with the front (W's) one lit column all the way down, a little lighter lower down, its
    # back arris (against the sky) a step darker; the balcony's slab round the corner at its own rows (its edge's lit line,
    # its face, its lower arris, a shade under it: see draw)
    sw = onn & (X >= STRIP[0]) & (Yr >= 86)
    ks = 0.94 + 0.12 * np.clip((Yr - 90) / 220.0, 0, 1)
    k = np.where(sw, k * ks, k)
    back = onn & ~np.isin(np.concatenate([name[:, 1:], name[:, -1:]], 1), ('near', 'cop'))
    k = np.where(back, k * 0.88, k)
    # rain streaks from the coping: thin, each its own length and depth, fading down, longer under the joints and the corner
    rng = np.random.default_rng(31)
    for x in range(x0, x1):
        i = x - x0
        if x < NF.XPN:
            z = Z_of(x + 0.5); j = min(abs(z - zz) for zz in JOINTS_P) * F * XP / z ** 2 < 1.0
        else:
            xm = (x + 0.5 - VPX) * ZN / F; j = min(abs(xm - xx) for xx in JOINTS_N) * F / ZN < 1.0
        j = j or abs(x + 0.5 - NF.XPN) < 1.5
        r = rng.random(); L = int(rng.integers(10, 24)) if j else int(rng.integers(4, 16)); dk = 0.06 + 0.08 * rng.random()
        if j or r < 0.25:
            s_ = rk[:, i] - 1
            fade = np.clip(1 - s_ / L, 0, 1) * (s_ >= 0)
            k[:, i] = np.where(wall[:, i] & (Yr[:, i] < 86 + 30 * (x >= STRIP[0])), k[:, i] * (1 - dk * fade), k[:, i])
    base = np.where(onn[..., None], pal['near'], pal['par'])
    colu = col.copy()
    col[wall] = (base * k[..., None] * pg[..., None] * (1 + 0.3 * GRAIN * n[..., None]))[wall]
    # over the pillar (left of its edge) the wall is the pillar's own light as tools/naruto_floor.py cleaned it, in each
    # layer: each row's mean over the pillar's clean columns (x 1126..1141), smoothed down the wall, from just under the
    # old coping's rows up carried as it is there; a little darker into C's corner; the painter's grain on it; the same
    # shading; no lamp's share added (it is in the pillar's own light). No pipe on it (the owner: "Vire cette gouttière")
    pm = wall & (X < NF.XPF)
    lampable &= ~pm
    for lay, out in ((city, col), (unlit, colu)):
        rowm = np.array([lay[y, 1126:1142, :3].mean(0) for y in range(y0, y1)])
        rowm = np.stack([gaussian_filter(rowm[:, c], 3.0, mode='nearest') for c in range(3)], -1)
        ref = np.zeros((h, w, 3))
        for x in range(x0, min(x1, int(NF.XPF))):
            i = x - x0
            if not pm[:, i].any(): continue
            pf = NF.edge_rows(x)[1]
            for r in np.nonzero(pm[:, i])[0]:
                ref[r, i] = rowm[max(r, pf + 3 - y0)] * (1 - 0.15 * np.exp(-(x - 1124) / 2.0))
        out[pm] = (ref * k[..., None] * pg[..., None])[pm]
    other = M & ~pm
    colu[other] = col[other]
    return col, colu, lampable


def planters(city, unlit, box, pal, sw_):
    """the planters' rims over the coping under the garden's plants (three rows: a lit top, its edge, the planter's face in
    the shade over the coping's lit edge); the garden's wind data
    (sw_, roof_sway.webp as tools/naruto_floor.py wrote it, its box at naruto_floor's SWAY_AT... printed box) made to
    know them: no leaf there, none may show there. Returns the rims' pixels."""
    bx, by = 1127, 34                                    # (street.js ROOF: B.x0, B.y0, naruto_floor's box)
    H = sw_.shape[0] // 3; W = sw_.shape[1]
    leaf = sw_[2 * H:, :, 0] >= 16
    cols = {}
    for i in range(W):
        x = bx + i
        if x < 1126 or x >= 1260: continue
        ct = NF.edge_rows(x)[0]
        r0 = ct - 3 - by
        if 0 <= r0 and leaf[r0:ct - by, i].any(): cols[x] = ct       # (a plant right over the coping there)
    xs = sorted(cols); spans = []
    for x in xs:
        if spans and x - spans[-1][1] <= RIM_GAP: spans[-1][1] = x
        else: spans.append([x, x])
    px = []
    for a, b in spans:
        for x in range(a - 1, b + 2):
            ct = NF.edge_rows(x)[0]
            for j, y in enumerate((ct - 3, ct - 2, ct - 1)):
                c = (pal['rim_top'], pal['rim'], pal['rim_face'])[j]
                if x == a - 1 or x == b + 1: c = c * 0.8                 # (its ends turned away)
                k = 1 + NR.lamp(x, y)
                city[y, x, :3] = c * k; unlit[y, x, :3] = c; city[y, x, 3] = unlit[y, x, 3] = 255
                px.append((x, y))
                i, r = x - bx, y - by
                if 0 <= i < W and 0 <= r < H:
                    sw_[r, i] = np.clip(np.round(city[y, x]), 0, 255); sw_[H + r, i] = np.clip(np.round(unlit[y, x]), 0, 255)
                    sw_[2 * H + r, i] = (0, 0, 0, 255)
    return px


def ac_unit(city, box, name):
    """the AC unit on the arcade's lean-to and what holds it, as the zones before leave them (a mask over box): what is
    not the painter's green black over the lean-to from its top rim down (x AC_X), but his pipes and line on the wall
    round it (over its top, and past its end over its valves' box), its dark pixels inside it kept; against the sky its
    dark edge pixels (his line round it against his dark wall, broken: specks against the sky) go, twice over, and along
    its face's lit top rim the darker specks over it"""
    x0, y0, x1, y1 = box; h, w = y1 - y0, x1 - x0
    c = city[y0:y1, x0:x1, :3]
    gb = (c.max(-1) <= 9) & (c[..., 1] >= c[..., 0]) & (c[..., 1] + 1 >= c[..., 2])
    m = np.zeros((h, w), bool)
    for x in range(AC_X[0], min(AC_X[1], x1)):
        top = AC_TOP if x < 1433 else 259                             # (past its end: its valves' box only)
        m[top - y0:foot_row(x) - y0, x - x0] = True
    m &= ~gb
    m[AC_TOP - y0, 1404 - x0:1434 - x0] = True                         # (its end's top rim, whole)
    m = binary_fill_holes(m)
    L = c @ LUMA
    rim = (np.arange(x0, x1) < 1404)[None, :] & (L < 30)              # (along its face's lit top rim: its darker specks)
    for _ in range(2):
        sky = (name == '') & ~m
        nb = np.zeros((h, w), bool); up = np.zeros((h, w), bool)
        nb[1:] |= sky[:-1]; nb[:-1] |= sky[1:]; nb[:, 1:] |= sky[:, :-1]; nb[:, :-1] |= sky[:, 1:]
        up[1:] = sky[:-1]
        m &= ~((L < 8) & nb) & ~(rim & up)
    return m


def ac_duct(city, unlit, box, acm, done):
    """the AC unit's pipes, in a cover: out of the side of its valves' box, an elbow, then down the wall behind into
    its lean-to's roof (DUCT: the down run's columns, the cover's top row); four pixels across, its top lit by the sky, its
    side toward the street lit, its other side in shade, its outer corner round; a collar where it goes into the roof;
    its shadow on the wall beside it and under the elbow. Its colours the unit's casing's"""
    x0, y0, x1, y1 = box
    xa, xb, ya = DUCT
    met = np.median(city[230:280, 1392:1400, :3].reshape(-1, 3), 0) * 0.85
    xs = min(max(x for x in range(1430, xa) if acm[y - y0, x - x0]) for y in range(ya, ya + 4)) + 1
    cover = {}
    for y in range(ya, ya + 4):                                       # the elbow, out of the valves' box
        for x in range(xs, xb):
            cover[(x, y)] = (1.3, 1.05, 0.95, 0.72)[y - ya]
    for x in range(xa, xb):                                           # the run down
        for y in range(ya, foot_row(x) + 1):
            k = (1.15, 1.0, 0.92, 0.7)[x - xa]
            if y < ya + 4: k = max(k, cover.get((x, y), 0)) if x < xb - 1 else min(k, cover.get((x, y), 9))
            if y >= foot_row(x) - 1: k *= 0.6                         # (its collar into the roof)
            cover[(x, y)] = k
    cover.pop((xb - 1, ya), None)                                     # (its outer corner, round)
    for (x, y), k in cover.items():
        if acm[y - y0, x - x0]: continue
        for lay in (city, unlit): lay[y, x, :3] = met * k; lay[y, x, 3] = 255
        done[y - y0, x - x0] = True
    for (x, y) in [(xb, y) for y in range(ya + 1, foot_row(xb))] + [(x, ya + 4) for x in range(xs, xa)]:
        if (x, y) in cover or acm[y - y0, x - x0] or x >= x1: continue  # (its shadow on the wall)
        for lay in (city, unlit): lay[y, x, :3] *= 0.72


def lay_draft(city, unlit, box, name, M, done):
    """the image model's draft (DRAFT, R28) laid into the street: boxed down to the street's pixels (its x4 brightened
    input undone), brought to the painting's colours by a gain per channel (its wall to this zone's: their medians on
    Naruto's near side, away from what it redraws), then laid where it differs from what this zone drew (the state it was
    drawn on) by more than 6 in a channel, within the AC unit's reach (a whole: its holes filled, specks dropped; its
    window's reach, DRAFT_WIN, now the face's: lay_face). The power cut: the unit at the painter's ratio on his unit
    (0.93, 0.96, 0.98), its warm rim (the street lamps' light on it) at his rim's (0.37, 0.5, 0.7). Returns what it laid
    (a mask over box)"""
    x0, y0, x1, y1 = box
    laid = np.zeros((y1 - y0, x1 - x0), bool)
    src = os.path.join(EDITS, DRAFT)
    if not os.path.exists(src): return laid
    x0, y0, x1, y1 = box
    cx0, cy0, cx1, cy1 = DRAFT_CROP
    d = np.asarray(Image.open(src).convert('RGB').resize((cx1 - cx0, cy1 - cy0), Image.BOX)).astype(float) / 255.0
    d = (d ** 2.0) * 255.0
    cur = city[cy0:cy1, cx0:cx1, :3]
    nm = name[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0]; Mc = M[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0]
    h, w = cur.shape[:2]
    reach = np.zeros((h, w), bool); win = np.zeros((h, w), bool)
    for x in range(DRAFT_AC[0], cx1):
        reach[DRAFT_AC[1] - cy0:foot_row(x) - cy0, x - cx0] = True
    wx0, wy0, wx1, wy1 = DRAFT_WIN
    win[wy0 - cy0:wy1 - cy0, wx0 - cx0:wx1 - cx0] = True
    ref = (nm == 'near') & Mc & ~reach & ~win & ~under_old_top((cx0, cy0, cx1, cy1))
    gain = np.median(cur[ref], 0) / np.maximum(np.median(d[ref], 0), 1e-3)
    q = d * gain
    obj = np.abs(q - cur).max(-1) > 6.0
    put = np.zeros((h, w), bool)
    m = obj & reach & unit_reach((cx0, cy0, cx1, cy1))
    lab, n = label(m)
    sizes = np.bincount(lab.ravel())
    m = np.isin(lab, [i for i in range(1, n + 1) if sizes[i] >= 6])
    put |= binary_fill_holes(m) & reach
    put &= ~specks(put, q)                                            # (no dark speck alone over its rim)
    warm = (q[..., 0] > q[..., 1] + 25) & (q[..., 0] > q[..., 2] + 15)
    ku = np.where(warm[..., None], (0.37, 0.5, 0.7), (0.93, 0.96, 0.98))
    ys, xs = np.nonzero(put)
    city[cy0 + ys, cx0 + xs, :3] = q[ys, xs]; unlit[cy0 + ys, cx0 + xs, :3] = (q * ku)[ys, xs]
    city[cy0 + ys, cx0 + xs, 3] = 255; unlit[cy0 + ys, cx0 + xs, 3] = 255
    done[cy0 - y0 + ys, cx0 - x0 + xs] = True
    laid[cy0 - y0 + ys, cx0 - x0 + xs] = True
    return laid


def lay_face(city, unlit, box, name, M, done, unit):
    """Naruto's near side's face as the image model painted it (FACE_DRAFT, R28) laid into the street: boxed down to the
    street's pixels (its x4 brightened input undone: at 22 h the street's grade leaves the layer as it is, so the draft is
    in the layer's colours already), brought to the painter's concrete by a gain per channel (its wall to this zone's
    near side: their medians, so the building keeps its one tone), laid on the near side's face (the zone's 'near'
    pixels), but two pixels round the AC unit (unit: its pixels, the stand's; there the zone's wall and its shade). The
    lit window: in the layers its glass off (the draft's curtain folds, its light over their mean, on the frosted
    window's dark glass), its light the comp LIT_COMP (the draft's glass as it painted it, at 22 h, opaque on the glass,
    clear round it). The power cut: as lit, but the window's light (a comp, off). Returns the comp (RGBA over LIT)"""
    src = os.path.join(EDITS, FACE_DRAFT)
    if not os.path.exists(src): return None
    x0, y0, x1, y1 = box
    cx0, cy0, cx1, cy1 = FACE_CROP
    d = np.asarray(Image.open(src).convert('RGB').resize((cx1 - cx0, cy1 - cy0), Image.BOX)).astype(float) / 255.0
    d = (d ** 2.0) * 255.0
    cur = city[cy0:cy1, cx0:cx1, :3]
    nm = name[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0]; Mc = M[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0]
    near_unit = np.zeros(nm.shape, bool)
    u = unit[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0]
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            near_unit |= np.roll(np.roll(u, dy, 0), dx, 1)
    face = (nm == 'near') & Mc & ~near_unit & ~under_old_top((cx0, cy0, cx1, cy1))
    gain = np.median(cur[face], 0) / np.maximum(np.median(d[face], 0), 1e-3)
    q = d * gain
    lx0, ly0, lx1, ly1 = LIT
    reach = np.zeros(nm.shape, bool); reach[ly0 - cy0:ly1 - cy0, lx0 - cx0:lx1 - cx0] = True
    glass = reach & (d[..., 0] > d[..., 2] + 8) & (d[..., 0] > 20) & face   # (its edge pixels, half glass, too)
    fx0, fy0, fx1, fy1 = FROST
    dark = np.median(q[fy0 - cy0:fy1 - cy0, fx0 - cx0:fx1 - cx0].reshape(-1, 3), 0)
    Lg = d @ LUMA
    fold = np.clip(Lg / max(np.mean(Lg[glass]), 1.0), 0.6, 1.4)
    off = dark[None, None, :] * (0.75 + 0.35 * fold)[..., None]
    q = np.where(glass[..., None], off, q)
    # (round the unit, where the draft's own unit may stray: its wall carried in from the nearest face pixel, no ring of
    # the zone's lighter wall round it)
    ring = near_unit & ~u & (nm == 'near') & Mc & ~under_old_top((cx0, cy0, cx1, cy1))
    if ring.any():
        _, (iy, ix) = distance_transform_edt(~face, return_indices=True)
        q = np.where(ring[..., None], q[iy, ix], q)
        face = face | ring
    ys, xs = np.nonzero(face)
    for lay in (city, unlit):
        lay[cy0 + ys, cx0 + xs, :3] = q[ys, xs]; lay[cy0 + ys, cx0 + xs, 3] = 255
    done[cy0 - y0 + ys, cx0 - x0 + xs] = True
    # under the parapet's top that was there (the draft drew it), the wall carried down to the lean-to's flashing: its
    # last ten rows over it repeated (their streaks, their tone), a shade over the flashing
    low = (nm == 'near') & Mc & ~near_unit & under_old_top((cx0, cy0, cx1, cy1))
    for c in np.nonzero(low.any(0))[0]:
        x = cx0 + c
        cut = int(np.argmax(under_old_top((cx0, cy0, cx1, cy1))[:, c]))
        yf = wall_bottom(M, box, x) - 2 - cy0
        for r in np.nonzero(low[:, c])[0]:
            if r >= yf: continue
            sr = cut - 1 - (r - cut) % 10
            if not face[sr, c]: continue
            k = 0.85 if r == yf - 1 else 1.0
            for lay in (city, unlit): lay[cy0 + r, x, :3] = q[sr, c] * k
    comp = np.zeros((ly1 - ly0, lx1 - lx0, 4))
    g = glass[ly0 - cy0:ly1 - cy0, lx0 - cx0:lx1 - cx0]
    comp[..., :3] = d[ly0 - cy0:ly1 - cy0, lx0 - cx0:lx1 - cx0]
    comp[..., 3] = np.where(g, 255.0, 0.0)
    return np.clip(np.round(comp), 0, 255).astype(np.uint8)


def lay_garden(city, unlit, box, sway0):
    """the roof garden as the image model painted it (GARDEN_DRAFT, R28) laid into the street: boxed down to the street's
    pixels (its x8 brightened input undone: at 22 h the layer's own colours), over Naruto's coping only (the garden stands
    behind the parapet), right of C's corner; its ground first (the zone's drawing with the old plants taken off: what
    each covered, sway0's first two blocks, the street's wind data as tools/naruto_floor.py wrote it), then where the draft
    differs from that ground by more than 10 in a channel (each plant a whole: specks dropped, holes filled) the draft;
    the power cut at the old garden's ratio (GARDEN_UNLIT). Returns the new wind data (roof_sway.webp's three blocks over
    GARDEN_CROP: what each leaf covers in each layer; each leaf's plant, clump and freedom, where a leaf may show)"""
    src = os.path.join(EDITS, GARDEN_DRAFT)
    if not os.path.exists(src): return None
    x0, y0, x1, y1 = box
    gx0, gy0, gx1, gy1 = GARDEN_CROP
    W, H = gx1 - gx0, gy1 - gy0
    d = np.asarray(Image.open(src).convert('RGB').resize((W, H), Image.BOX)).astype(float) / 255.0
    d = (d ** 2.0) * 255.0
    C = city[gy0:gy1, gx0:gx1].copy(); U = unlit[gy0:gy1, gx0:gx1].copy()
    # the ground: the old plants off (their wind data: what each covered, where it differs from the layer)
    sh = sway0.shape[0] // 3; sw = sway0.shape[1]; sx, sy = OLD_SWAY_AT
    G, GU = C.copy(), U.copy()
    for yy in range(sh):
        for xx in range(sw):
            x, y = sx + xx, sy + yy
            if not (gx0 <= x < gx1 and gy0 <= y < gy1): continue
            und = sway0[yy, xx].astype(float)
            if np.abs(und - C[y - gy0, x - gx0]).max() > 0:
                G[y - gy0, x - gx0] = und; GU[y - gy0, x - gx0] = sway0[sh + yy, xx]
    area = np.zeros((H, W), bool)
    for x in range(max(gx0, 1125), gx1):
        area[:max(NF.edge_rows(x)[0] - gy0, 0), x - gx0] = True
    gc = np.where((G[..., 3:4] > 127), G[..., :3], 0.0)
    sky = G[..., 3] < 128
    rows = np.arange(16)                                  # (the draft's sky: its gradient over its top rows, over C)
    med = np.array([np.median(d[y, 0:80], 0) for y in rows])
    skyc = np.stack([np.polyval(np.polyfit(rows, med[:, c], 1), np.arange(H)) for c in range(3)], -1)[:, None, :]
    diff = np.where(sky, np.abs(d - skyc).max(-1), np.abs(d - gc).max(-1))
    obj = (diff > 10.0) & area
    lab, n = label(obj)
    sizes = np.bincount(lab.ravel())
    obj = np.isin(lab, [i for i in range(1, n + 1) if sizes[i] >= 4])
    obj = binary_fill_holes(obj) & area
    # the layers: the ground over the area, the draft on the plants
    newc = np.where(area[..., None], G, C); newu = np.where(area[..., None], GU, U)
    newc[obj, :3] = d[obj]; newc[obj, 3] = 255
    newu[obj, :3] = d[obj] * GARDEN_UNLIT; newu[obj, 3] = 255
    newc[sky & area & ~obj] = 0; newu[sky & area & ~obj] = 0
    city[gy0:gy1, gx0:gx1] = np.clip(np.round(newc), 0, 255); unlit[gy0:gy1, gx0:gx1] = np.clip(np.round(newu), 0, 255)
    # the wind data: what each leaf covers (the ground), each plant's leaves, their clumps, their freedom
    out = np.zeros((3 * H, W, 4), np.uint8)
    gr = np.where(area[..., None], G, newc); gu = np.where(area[..., None], GU, newu)
    out[:H] = np.clip(np.round(gr), 0, 255); out[H:2 * H] = np.clip(np.round(gu), 0, 255)
    blk = out[2 * H:]
    blk[..., 3] = 255; blk[..., 2] = np.where(area, 255, 0)
    r, g, b = d[..., 0], d[..., 1], d[..., 2]
    chroma = d.max(-1) - d.min(-1)
    leafy = {'red': (r > g + 4) & (r > b - 2), 'green': (g >= r) & ((chroma >= 4) | (d @ LUMA < 9)) & ~((r > b + 3) & (g > b)),
             'any': np.ones((H, W), bool)}
    kcount = {}
    for kind, leaf, (ax0, ay0, ax1, ay1), free in PLANTS:
        reach = np.zeros((H, W), bool); reach[max(ay0 - gy0, 0):ay1 - gy0, max(ax0 - gx0, 0):ax1 - gx0] = True
        m = obj & reach & leafy[leaf] & (blk[..., 0] == 0)
        if not m.any(): continue
        lab, n = label(m, structure=np.ones((3, 3), bool))
        ys, xs = np.nonzero(m)
        top, base = ys.min(), ys.max(); cx, rx = xs.mean(), max(1.0, (xs.max() - xs.min()) / 2)
        for j in range(1, n + 1):
            k = kcount.get(kind, 0); kcount[kind] = min(k + 1, 15)
            pys, pxs = np.nonzero(lab == j)
            for yy, xx in zip(pys, pxs):
                if kind == 1:
                    up = (base - yy) / max(base - top, 1); out_ = min(1.0, abs(xx - cx) / rx)
                    f = (0.35 + 0.65 * up) * (0.75 + 0.25 * out_)
                else:
                    col = np.nonzero(lab[:, xx] == j)[0]
                    dd = yy - col.min()
                    f = max(0.0, 1.0 - dd / 4.0) * (0.8 if kind == 2 else 0.6)
                    if kind == 3: f *= float(np.clip((gy0 + yy - 44) / 4.0, 0, 1))   # (the hedge still under the menu's text)
                blk[yy, xx, 0] = 16 * kind + k; blk[yy, xx, 1] = int(round(255 * f * free))
    return out


def lay_terrace(city, unlit, sw):
    """the terrace's parasol, chairs, string lights and lantern from their draft (TERRACE_DRAFT, R28) laid over the sky
    (the layers off); returns the lights' comp (LIGHTS_COMP: RGBA, its box x, y, w, h) and the new pixels (a mask over
    TERRACE_CROP); sw, the garden's wind data over GARDEN_CROP, given the parasol's hem and what it now hides"""
    src = os.path.join(EDITS, TERRACE_DRAFT)
    if not os.path.exists(src): return None, None, None
    x0, y0, x1, y1 = TERRACE_CROP; W, H = x1 - x0, y1 - y0
    d = np.asarray(Image.open(src).convert('RGB').resize((W, H), Image.BOX)).astype(float) / 255.0
    d = np.roll(np.roll((d ** 2.0) * 255.0, TERRACE_SHIFT[1], 0), TERRACE_SHIFT[0], 1)
    C, U = city[y0:y1, x0:x1].copy(), unlit[y0:y1, x0:x1].copy()
    sky = C[..., 3] < 128
    sk = np.zeros((H, 3)); last = d[0, 0]
    for y in range(H):                                                      # (each row's sky as the draft painted it)
        if sky[y].sum() > 8: last = np.median(d[y][sky[y]], 0)
        sk[y] = last
    diff = np.abs(d - sk[:, None, :]).max(-1)
    Ld = d @ LUMA
    warm = d[..., 0] > d[..., 2] + 20

    def inb(b):
        m = np.zeros((H, W), bool); m[b[1]:b[3], b[0]:b[2]] = True; return m
    canopy, pole, lantern, string = inb(T_CANOPY), inb(T_POLE), inb(T_LANTERN), inb(T_STRING)
    off = np.zeros((H, W, 3)); om = np.zeros((H, W), bool); lit = np.zeros((H, W, 3)); lm = np.zeros((H, W), bool)
    cm = np.zeros((H, W), bool)
    for y, x in zip(*np.nonzero((diff > 12) & (canopy | pole | lantern))):   # the parasol and the lantern, lower
        Y = y + T_DROP
        if Y >= H: continue
        if lantern[y, x] and warm[y, x]:                                    # (its paper off in the night's glow, its
            lit[Y, x] = d[y, x]; lm[Y, x] = True                            # caps dim, its halo only lit)
            if Ld[y, x] > 70: off[Y, x] = np.array((0.95, 0.9, 1.08)) * Ld[y, x] * 0.36; om[Y, x] = True
            elif Ld[y, x] > 35: off[Y, x] = d[y, x] * 0.45; om[Y, x] = True
        elif canopy[y, x] and y >= 35 and Ld[y, x] < 35:                   # (its underside: the street's light from
            off[Y, x] = d[y, x] * 0.6 + np.array((14.0, 14.0, 20.0)); om[Y, x] = True   # below; the lights' glow)
            lit[Y, x] = off[Y, x] + np.array((38.0, 24.0, 10.0)); lm[Y, x] = True; cm[Y, x] = True
        else:
            off[Y, x] = d[y, x]; om[Y, x] = True; cm[Y, x] = canopy[y, x]
    a, b = T_STRING_ENDS
    for y, x in zip(*np.nonzero((diff > 12) & string & ~(canopy & (np.arange(H)[:, None] < 44)))):   # the string, sheared
        Y = y + int(round(T_DROP * np.clip((b - x) / (b - a), 0, 1)))
        if Y >= H: continue
        if warm[y, x]:
            lit[Y, x] = d[y, x]; lm[Y, x] = True
            if Ld[y, x] > 70: off[Y, x] = BULB_OFF; om[Y, x] = True
        else:
            off[Y, x] = d[y, x]; om[Y, x] = True
    for bx in T_CHAIRS:                                                     # the chairs' backs: the draft's wood
        m = inb(bx) & (d[..., 0] > d[..., 2] + 4) & (diff > 12)
        off[m] = d[m]; om |= m
    om &= sky; lm &= sky
    lab, n = label(om, structure=np.ones((3, 3), bool))                     # (specks off)
    sizes = np.bincount(lab.ravel())
    om &= np.isin(lab, [i for i in range(1, n + 1) if sizes[i] >= 3])
    # the layers: the things off
    for lay, ref, k in ((city, C, 1.0), (unlit, U, GARDEN_UNLIT)):
        s = ref.copy(); s[om, :3] = off[om] * k; s[om, 3] = 255
        lay[y0:y1, x0:x1] = np.clip(np.round(s), 0, 255)
    # the lights' comp: lit where it differs from off (the sky round a bulb, its glow, a halo pixel or two)
    base = np.where(om[..., None], off, C[..., :3])
    lm &= np.abs(np.round(lit) - np.round(base)).max(-1) > 0
    cb = LIGHTS_BOX
    sub = (slice(cb[1] - y0, cb[1] - y0 + cb[3]), slice(cb[0] - x0, cb[0] - x0 + cb[2]))
    assert lm[sub].sum() == lm.sum(), 'the lights out of LIGHTS_BOX'
    comp = np.zeros((cb[3], cb[2], 4), np.uint8)
    comp[..., :3] = np.clip(np.round(np.where(lm[sub][..., None], lit[sub], 0)), 0, 255)
    comp[..., 3] = np.where(lm[sub], 255, 0)
    # the wind data: what the new things now hide is theirs; the parasol's hem a leaf, freer at its edge
    gx0, gy0, gx1, gy1 = GARDEN_CROP; gh = sw.shape[0] // 3
    for yy, xx in zip(*np.nonzero(om)):
        X, Y = x0 + xx, y0 + yy
        if not (gx0 <= X < gx1 and gy0 <= Y < gy1): continue
        i, j = Y - gy0, X - gx0
        if sw[2 * gh + i, j, 0] >= 16: continue                            # (a leaf there: as it was)
        sw[i, j] = city[Y, X]; sw[gh + i, j] = unlit[Y, X]
    hem = np.zeros((H, W)); can = om & cm
    for xx in range(W):
        rows = np.nonzero(can[:, xx])[0]
        if not len(rows): continue
        for k, f in enumerate((0.75, 0.5, 0.25)):
            yy = rows.max() - k
            if yy >= 0 and can[yy, xx] and y0 + yy >= T_STILL_ABOVE: hem[yy, xx] = f
    for yy, xx in zip(*np.nonzero(hem > 0)):
        X, Y = x0 + xx, y0 + yy
        if not (gx0 <= X < gx1 and gy0 <= Y < gy1): continue
        i, j = Y - gy0, X - gx0
        sw[i, j] = C[yy, xx]; sw[gh + i, j] = U[yy, xx]                    # (what the hem covers: the sky)
        sw[2 * gh + i, j, 0] = 16 * 2 + 15; sw[2 * gh + i, j, 1] = int(round(255 * hem[yy, xx]))
        sw[2 * gh + i, j, 2] = 255; sw[2 * gh + i, j, 3] = 255
    return comp, cb, om


def lay_windows(city, unlit, box):
    """the two windows' light and figures from their drafts (WIN_DRAFT, WIN_FIG_DRAFT, R28), boxed down to the street's
    pixels (their x8 brightened input undone: at 22 h the layer's colours): the room's lit glass (the draft's warm pixels in
    ROOM) and the bathroom's (in BATH), as street.js shows them over the layers (their own light: as painted); in the layers
    the room's glass off as it now is (the draft's curtain and room, their light over its mean, on the frosted pane's dark
    glass); each figure what the second draft darkens of the first over its box (smoothed a little, on the lit glass only),
    one colour (its core's) and that darkening as its opacity. Returns {asset name: RGBA}"""
    s1, s2 = (os.path.join(EDITS, f) for f in (WIN_DRAFT, WIN_FIG_DRAFT))
    if not (os.path.exists(s1) and os.path.exists(s2)): return {}
    wx0, wy0, wx1, wy1 = WIN_CROP
    W, H = wx1 - wx0, wy1 - wy0
    d1, d2 = ((np.asarray(Image.open(f).convert('RGB').resize((W, H), Image.BOX)).astype(float) / 255.0) ** 2.0 * 255.0
              for f in (s1, s2))
    warm = (d1[..., 0] > d1[..., 2] + 8) & (d1[..., 0] > 20)
    out = {}

    def box_mask(b):
        m = np.zeros((H, W), bool); m[b[1] - wy0:b[3] - wy0, b[0] - wx0:b[2] - wx0] = True
        return m
    room, bath = warm & box_mask(ROOM), warm & box_mask(BATH)
    for nm, b, gl in ((LIT_COMP, ROOM, room), (BATH_COMP, BATH, bath)):
        a = np.zeros((b[3] - b[1], b[2] - b[0], 4))
        sl = (slice(b[1] - wy0, b[3] - wy0), slice(b[0] - wx0, b[2] - wx0))
        a[..., :3] = d1[sl]; a[..., 3] = np.where(gl[sl], 255.0, 0.0)
        out[nm] = np.clip(np.round(a), 0, 255).astype(np.uint8)
    # the room's glass off in the layers
    fx0, fy0, fx1, fy1 = FROST
    dark = np.median(city[fy0:fy1, fx0:fx1, :3].reshape(-1, 3), 0)
    Lg = d1 @ LUMA
    fold = np.clip(Lg / max(np.mean(Lg[room]), 1.0), 0.6, 1.4)
    ys, xs = np.nonzero(room)
    for lay in (city, unlit):
        lay[wy0 + ys, wx0 + xs, :3] = dark * (0.75 + 0.35 * fold[ys, xs])[:, None]
    # the figures
    l1, l2 = gaussian_filter(d1 @ LUMA + 1, 0.7), gaussian_filter(d2 @ LUMA + 1, 0.7)
    dk = np.clip(1 - l2 / l1, 0, 1)
    for nm, b, gl in (('win_naru_side_fig.webp', ROOM_FIG, room), ('win_naru_bath_fig.webp', BATH_FIG, bath)):
        sl = (slice(b[1] - wy0, b[3] - wy0), slice(b[0] - wx0, b[2] - wx0))
        a = np.where(gl[sl], dk[sl], 0.0); a = np.where(a < 0.06, 0.0, a)
        core = a > 0.6 * a.max()
        col = np.median(d2[sl][core], 0)
        f = np.zeros(a.shape + (4,)); f[..., :3] = col; f[..., 3] = 255 * np.clip(a / max(a.max(), 1e-3), 0, 1)
        out[nm] = np.clip(np.round(f), 0, 255).astype(np.uint8)
    return out


def draw(city, unlit, box=BOX, write=True):
    """The zone (redraw_zones.py): the layers changed in place (whole-scene float RGBA); street_sun written (0 on what is
    redrawn; beyond the zone 'narufloor' from this zone's before crop) and roof_sway.webp's planters; returns what changed
    in box."""
    x0, y0, x1, y1 = box; h, w = y1 - y0, x1 - x0
    sign = NF.sign_top((x0, y0, x1, y1))
    name, nrm, P = cast(box)
    M = mask(box, sign)
    gbx = lambda x, y: city[y, x, :3].max() <= 12 and city[y, x, 1] >= city[y, x, 0]
    for x in range(STRIP[0], STRIP[1]):                # (the near wall on down to the canopy: the dark box over it)
        for y in range(STRIP[2], y1):
            if not gbx(x, y): break
            M[y - y0, x - x0] = True
    for x in range(STRIP[1], LEAN_END):                # (and down to the lean-to's far end, beyond which its painter's dark
        for y in range(foot_row(x), y1):               # showed under the wall's foot: the near side there, as far down)
            if not gbx(x, y): break
            M[y - y0, x - x0] = True
    acm = ac_unit(city, box, name)
    acm &= ~specks(acm, city[y0:y1, x0:x1, :3])
    for x in range(AC_X[0], 1359):                     # (left of the unit's far edge, over its bottom's ray: the painter's
        acm[:int(np.floor(AE.ray_y(x, AE.VB))) - y0, x - x0] = False   # broken line round it, the wall's now; its stand kept)
    M &= ~acm
    sky = M & (name == '')
    pal = palette(city)
    col, colu, lampable = shade(box, name, nrm, P, pal, M & ~sky, city, unlit)
    c0, u0 = city[y0:y1, x0:x1].copy(), unlit[y0:y1, x0:x1].copy()
    lampk = np.array([[NR.lamp(x, y) for x in range(x0, x1)] for y in range(y0, y1)])
    lit = M & ~sky
    city[y0:y1, x0:x1, :3][lit] = (col * (1 + np.where(lampable, lampk, 0.0))[..., None])[lit]
    unlit[y0:y1, x0:x1, :3][lit] = colu[lit]
    city[y0:y1, x0:x1, 3][lit] = 255; unlit[y0:y1, x0:x1, 3][lit] = 255
    city[y0:y1, x0:x1][sky] = 0; unlit[y0:y1, x0:x1][sky] = 0
    done = M.copy()
    ac_duct(city, unlit, box, acm, done)
    # the front by the corner, between the sign's end and the corner, over the canopy (the dark box): the front's own wall
    # there carried down (each column's light just over it), the painter's grain
    pg2 = tile(painter_grain(), h, w, 41, 3)
    for x in range(CANOPY_X[0], STRIP[0]):
        ref = c0[300 - y0:304 - y0, x - x0, :3].mean(0); refu = u0[300 - y0:304 - y0, x - x0, :3].mean(0)
        for y in range(STRIP[2], y1):
            q = c0[y - y0, x - x0, :3]
            if not (q.max() <= 12 and q[1] >= q[0]): break
            city[y, x, :3] = ref * pg2[y - y0, x - x0]; unlit[y, x, :3] = refu * pg2[y - y0, x - x0]
            city[y, x, 3] = unlit[y, x, 3] = 255; done[y - y0, x - x0] = True
    # the canopy's flashing where its roof meets the walls (the first row over its tiles); a shade on the wall over it;
    # past the arcade's far corner the same where the lean-to's roof meets Naruto's near side (its fold lit by the sky
    # over it, its face), but on the AC unit, its stand and its pipes' cover
    for x in range(CANOPY_X[0], CANOPY_X[1]):
        for y in range(STRIP[2], y1 - 1):
            if done[y - y0, x - x0] and not done[y + 1 - y0, x - x0]:
                for lay in (city, unlit):
                    lay[y, x, :3] = FLASH[1]; lay[y - 1, x, :3] *= 0.8
                break
    for x in range(CANOPY_X[1], x1):
        yf = wall_bottom(M, box, x)
        for y, c in ((yf - 2, FLASH[0]), (yf - 1, FLASH[1])):
            if not M[y - y0, x - x0] or acm[y - y0, x - x0] or name[y - y0, x - x0] != 'near': continue
            if DUCT[0] <= x < DUCT[1]: continue
            for lay in (city, unlit): lay[y, x, :3] = c
        if M[yf - 3 - y0, x - x0] and not acm[yf - 3 - y0, x - x0] and not DUCT[0] <= x < DUCT[1]:
            for lay in (city, unlit): lay[yf - 3, x, :3] *= 0.85
    # the near wall's corner with the front (W's last pier) one crisp lit column from the roof slab down to the canopy; the
    # balcony's slab round the corner at its own rows, as tools/naruto_floor.py draws its end over the opening (its edge's
    # lit line, its face, its lower arris), a step dimmer turned from the street, a shade under it
    sa, sb = SLAB_ROWS
    for y in range(86, y1):
        if not done[y - y0, STRIP[0] - x0]: break
        if sa <= y < sb: continue
        for lay, ref in ((city, pal['pier']), (unlit, pal['pier'])): lay[y, STRIP[0], :3] = ref * 1.35
    band = [NF.C['edge'] * 0.62, NF.C['edge2'] * 0.85] + [NF.C['end']] * (sb - sa - 4) + [NF.C['slab_arris'] * 0.9, pal['near'] * 0.5]
    for x in range(STRIP[0], x1):                                     # (across the near side, where it shows)
        g = 1 + 0.03 * ((x * 7 + 3) % 5 - 2)
        for j, y in enumerate(range(sa, sb)):
            if name[y - y0, x - x0] != 'near' or not M[y - y0, x - x0]: continue
            for lay in (city, unlit): lay[y, x, :3] = band[j] * g
    swp = os.path.join(ASSETS, 'roof_sway.webp')
    sw_ = np.asarray(Image.open(swp).convert('RGBA')).copy()
    for x, y in planters(city, unlit, box, pal, sw_): done[y - y0, x - x0] = True
    gsw = lay_garden(city, unlit, box, np.asarray(Image.open(swp).convert('RGBA')).copy())   # (its ground: the file as
    if gsw is not None:                                                                       # tools/naruto_floor.py wrote it)
        sw_ = gsw
        for x in range(1125, GARDEN_CROP[2]):
            done[GARDEN_CROP[1] - y0:NF.edge_rows(x)[0] - y0, x - x0] = True
    # the pillar's side face beside the pipe (tools/naruto_floor.py's 'side', in the balcony's recess, as it leaves it): the
    # painter's grain on it, a little lighter lower down (the street's light from below)
    nb = NF.BOX
    R = NF.roles(nb, NF.lip_bottom(nb), NF.sign_top(nb))[0]
    pg = tile(painter_grain(), h, w, 29, 11)
    for yy, xx in zip(*np.nonzero(np.isin(R, ('side', 'side_low')))):
        x, y = nb[0] + xx, nb[1] + yy
        if not (x0 <= x < x1 and y0 <= y < y1): continue
        f = pg[y - y0, x - x0] * (0.94 + 0.12 * min(1.0, max(0.0, (y - 160) / 120.0)))
        for lay in (city, unlit): lay[y, x, :3] = lay[y, x, :3] * f
        done[y - y0, x - x0] = True
    for lay in (city, unlit): lay[y0:y1, x0:x1] = np.clip(np.round(lay[y0:y1, x0:x1]), 0, 255)
    laid = lay_draft(city, unlit, box, name, M, done)
    comp = lay_face(city, unlit, box, name, M, done, laid | acm)
    wins = lay_windows(city, unlit, box)
    if wins: comp = None                                              # (the room's light: the windows' draft's now)
    for lay in (city, unlit): lay[y0:y1, x0:x1] = np.clip(np.round(lay[y0:y1, x0:x1]), 0, 255)
    lights, _, tm = lay_terrace(city, unlit, sw_)                     # (last: on the street as it now is)
    if lights is not None:
        wins[LIGHTS_COMP] = lights
        tx0, ty0, tx1, ty1 = TERRACE_CROP
        done[ty0 - y0:ty1 - y0, tx0 - x0:tx1 - x0] |= tm
    changed = (city[y0:y1, x0:x1] != c0).any(-1) | (unlit[y0:y1, x0:x1] != u0).any(-1)
    # street_sun: as 'narufloor' wrote it in its box, this zone's before crop beyond it; 0 on what is redrawn
    sun = np.asarray(Image.open(os.path.join(ASSETS, 'street_sun.webp')).convert('RGB')).astype(float)
    bs = np.asarray(Image.open(os.path.join(EDITS, 'naruroof_before_sun.webp')).convert('RGB')).astype(float)
    nx1 = NF_BOX[2]
    sun[y0:y1, nx1:x1] = bs[:, nx1 - x0:]
    sun[y0:y1, x0:x1][done] = 0
    if write:
        if comp is not None:
            Image.fromarray(comp, 'RGBA').save(os.path.join(ASSETS, LIT_COMP), 'WEBP', lossless=True, quality=100, method=6,
                                               exact=True)
        for nm, a in wins.items():
            Image.fromarray(a, 'RGBA').save(os.path.join(ASSETS, nm), 'WEBP', lossless=True, quality=100, method=6, exact=True)
        Image.fromarray(np.clip(np.round(sun), 0, 255).astype(np.uint8), 'RGB').save(
            os.path.join(ASSETS, 'street_sun.webp'), 'WEBP', lossless=True, quality=100, method=6, exact=True)
        Image.fromarray(sw_, 'RGBA').save(swp, 'WEBP', lossless=True, quality=100, method=6, exact=True)
    draw.last = (name, nrm, P, M, done, sun, sw_)
    return changed


def model_lines():
    """the model's edges projected (for the report): [(name, [(x, y), ...])]"""
    pr = lambda X, Y, Z: (VPX + F * X / Z, VPY - F * (Y - EYE) / Z)
    zs = np.linspace(ZN, ZF, 20)
    xs = np.linspace(XP, XP + 12, 20)
    L = [('coping top P', [pr(XP - OVH, Y_CT, z) for z in zs]), ('coping foot P', [pr(XP - OVH, Y_CT - COP, z) for z in zs]),
         ('soffit edge', [pr(XP, Y_LB, z) for z in np.linspace(ZN, ZPIL, 10)]), ('terrace', [pr(XP, Y_T, z) for z in zs]),
         ('coping top near', [pr(x, Y_CT, ZN - OVH) for x in xs]), ('coping foot near', [pr(x, Y_CT - COP, ZN - OVH) for x in xs]),
         ('corner', [pr(XP, Y_LB, ZN), pr(XP, Y_CT, ZN)]), ('C corner', [pr(XP, Y_LB - 2, ZF), pr(XP, Y_CT, ZF)]),
         ('arcade lean-to top', [pr(XA, Y_FOOT, z) for z in (ZN, F * XA / 756.0)]),
         ('near roof slab', [pr(x, Y_LB, ZN) for x in (XP, X_BACK)]),
         ('near floor slab', [(STRIP[0], SLAB_ROWS[0]), (1456, SLAB_ROWS[0])]),
         ('near floor slab foot', [(STRIP[0], SLAB_ROWS[1]), (1456, SLAB_ROWS[1])])]
    # the AC unit's box (tools/arcade_eave.py's, in its own metres: the same rays)
    pa = lambda X, Y, Z: (VPX + AE.F * X / Z, VPY - AE.F * (Y - AE.EYE) / Z)
    yb, yt, x0, x1 = AE.YB, AE.EYE + AE.VTOP * AE.XU, AE.XU, AE.XU + AE.DU
    for nm, pts in (('unit face', [(x0, yt, AE.ZF), (x0, yt, AE.ZC), (x0, yb, AE.ZC), (x0, yb, AE.ZF), (x0, yt, AE.ZF)]),
                    ('unit end', [(x0, yt, AE.ZC), (x1, yt, AE.ZC), (x1, yb, AE.ZC), (x0, yb, AE.ZC)])):
        L.append(('arcade ' + nm, [pa(*q) for q in pts]))
    for nm, (wx0, wy0, wx1, wy1) in (('window lit', LIT), ('window frosted', FROST)):
        L.append((nm, [(wx0, wy0), (wx1, wy0), (wx1, wy1), (wx0, wy1), (wx0, wy0)]))
    return L


def _load(p, mode='RGBA'):
    return np.asarray(Image.open(p).convert(mode)).astype(float)


def before():
    """the zone's before crops: the layers in its box as tools/redraw_zones.py's first pass leaves them without this zone
    (each zone's before crop laid back, in its order, on the layers as they are), and street_sun beyond 'narufloor'"""
    import redraw_zones as RZ
    outs = [os.path.join(EDITS, f'naruroof_before_{t}.webp') for t in ('city', 'unlit', 'sun')]
    if any(os.path.exists(p) for p in outs):
        sys.exit('naruto_parapet: the before crops exist already (they are the layers before this zone: made once)')
    city, unlit = _load(os.path.join(ASSETS, 'layer_city_off.webp')), _load(os.path.join(ASSETS, 'street_unlit.webp'))
    for nm, cfg in RZ.ZONES.items():
        if nm == 'naruroof': continue
        a, b, c, d = cfg['box']
        city[b:d, a:c] = _load(os.path.join(EDITS, f'{nm}_before_city.webp'))
        unlit[b:d, a:c] = _load(os.path.join(EDITS, f'{nm}_before_unlit.webp'))
    x0, y0, x1, y1 = BOX
    sun = _load(os.path.join(ASSETS, 'street_sun.webp'), 'RGB')
    for a, t, mode in ((city, 'city', 'RGBA'), (unlit, 'unlit', 'RGBA'), (sun, 'sun', 'RGB')):
        Image.fromarray(np.clip(np.round(a[y0:y1, x0:x1]), 0, 255).astype(np.uint8), mode).save(
            os.path.join(EDITS, f'naruroof_before_{t}.webp'), 'WEBP', lossless=True, quality=100, method=6, exact=True)
    print('naruto_parapet: before crops written', BOX)


def preview(out, src=None):
    """the zone drawn on the layers of src (a folder with layer_city_off.webp, street_unlit.webp and roof_sway.webp as the
    zones before leave them; else assets/), crops before and after, x3 and x6 with the model's lines; the new layers and
    roof_sway.webp in out/layers"""
    global ASSETS
    os.makedirs(os.path.join(out, 'layers'), exist_ok=True)
    src = src or ASSETS
    L = {t: _load(os.path.join(src, f)) for t, f in (('city', 'layer_city_off.webp'), ('unlit', 'street_unlit.webp'))}
    A = {t: a.copy() for t, a in L.items()}
    keep = ASSETS
    import shutil
    for f in ('roof_sway.webp', 'street_sun.webp'):
        shutil.copy(os.path.join(src if os.path.exists(os.path.join(src, f)) else keep, f), os.path.join(out, 'layers', f))
    ASSETS = os.path.join(out, 'layers')
    try:
        draw(A['city'], A['unlit'], BOX, write=True)
    finally:
        ASSETS = keep
    sky = np.array((62.0, 45.0, 86.0))
    def comp(a, b):
        c = a[b[1]:b[3], b[0]:b[2]]; al = c[..., 3:4] / 255
        return c[..., :3] * al + sky * (1 - al)
    from PIL import ImageDraw
    for tag, b, k in (('roof', (1110, 20, 1310, 200), 6), ('right', (1260, 0, 1456, 376), 4), ('wide', (1060, 0, 1456, 400), 3)):
        for t in ('city', 'unlit'):
            for st, lay in (('before', L[t]), ('after', A[t])):
                z = comp(lay, b)
                for gm, suf in ((1.0, ''), (0.5, 'b')):
                    im = Image.fromarray(np.clip(np.round(255 * (z / 255) ** gm), 0, 255).astype(np.uint8))
                    im = im.resize(((b[2] - b[0]) * k, (b[3] - b[1]) * k), Image.NEAREST)
                    im.save(os.path.join(out, f'{tag}_{t}_{st}_x{k}{suf}.png'))
                    if st == 'after' and t == 'city' and suf == 'b':
                        g = ImageDraw.Draw(im)
                        for nm, pts in model_lines():
                            q = [((px - b[0]) * k, (py - b[1]) * k) for px, py in pts]
                            g.line(q, fill=(255, 200, 0) if 'arcade' in nm else (0, 255, 200) if 'pipe' in nm else (255, 80, 80), width=1)
                        im.save(os.path.join(out, f'{tag}_{t}_model_x{k}.png'))
    for t, f in (('city', 'layer_city_off.webp'), ('unlit', 'street_unlit.webp')):
        Image.fromarray(np.clip(np.round(A[t]), 0, 255).astype(np.uint8), 'RGBA').save(os.path.join(out, 'layers', f), 'WEBP', lossless=True, quality=100, method=6, exact=True)
    print('naruto_parapet: preview in', out)


if __name__ == '__main__':
    if '--before' in sys.argv:
        before()
    elif '--preview' in sys.argv:
        i = sys.argv.index('--preview')
        preview(sys.argv[i + 1], sys.argv[i + 2] if len(sys.argv) > i + 2 else None)
    else:
        print(__doc__)
