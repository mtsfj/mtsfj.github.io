#!/usr/bin/env python3
"""The owner's study window (zone 5, the house at the street's end): his room and himself at his PC, redone.

    python3 tools/owner_study.py                 writes the room's states (assets/win_z5_room.webp: the lamp and the screen,
                                                 z5_lamp.webp: the lamp alone, z5_screen.webp: the screen alone,
                                                 z5_dark.webp: the room dark), his frames (assets/study_him.webp) and, in
                                                 assets/street.js, the line MSA (his frames' cells and the room's points);
                                                 again: the same bytes
    (a module: tools/redraw_zones.py's zone 'study' calls draw(): the dark room behind the glass in both layers)
    python3 tools/owner_study.py --input room    writes the room's input for the image model (the street round the window,
                                                 its room blocked out: tools/src/edits/study_room_in.webp)
    python3 tools/owner_study.py --ask NAME      asks the image model for NAME (room, room2, sheetS, sheetB, sheetC, walk,
                                                 screens, herA, herB: its
                                                 input and prompt in tools/src/edits/study_NAME_in.webp, _prompt.txt, its
                                                 references REFS; its answer study_NAME_model.webp; about 0.26 $ each)
    python3 tools/owner_study.py --preview DIR   (only shows the room's four states at x4; nothing written in assets/)

The owner: "Améliore mon perso qui me représente et ma chambre, les anims et le perso sont pas dingue". The room was five
flat orange shapes, the figure a rig of capsules. Both redone from pictures drawn for them (R28), pixelated here:
- the room: the image model painted it in the street (the window blocked out where the desk, the monitor, the keyboard,
  the chair, the floor lamp and the bed's corner go; its first answer, study_room0, kept as its reference for the second):
  a bedroom-study, shelves of books with figurines, headphones on a hook, a whiteboard of maths, the monitor's code, a mug,
  plants, the gaming chair in profile, a floor lamp with a paper shade, a poster of a starry night, the bed's corner. Its
  glass box fitted behind the window's (ROOM_FIT: it painted the room taller than the window, its top above the window's
  head), resampled (Lanczos), in NPAL tones. One painting, four states (room_states): dark, the layer's own dark room (its
  glass's sheen) with the room's shapes faint in it; the screen alone, its light from the monitor falling off over the
  room's own colours; the lamp alone, the painting with the screen asleep and its glow taken off; lit, the lamp alone and
  the screen's light (street.js tints that part with the hour: the code's green, Overleaf's white, Valorant's red). The
  owner then ("la chambre top ; juste remplacer ce qu'il y a sur l'écran et le poster par des trucs mieux, et décoller un
  peu le lit du mur"): the answer edited (study_room2: a new print, a dusk landscape; the bed out of the wall, its head
  against it, its foot and side in the room), the whole of it used, registered; what the screen shows drawn apart
  (study_screens: his code, Overleaf's source and PDF, a shooter's view), read into what street.js draws alive at the
  glass's 17 x 11 pixels by the hour (screens(): the code's and the source's lines in tokens, the page's tones, the game's
  view, a picture);
- him: four sheets drawn after pose guides (the old rig's poses as grey mannequins): sheet S (standing in profile, turning
  round, square to the street, the hand on the pane, sitting down and getting up; it replaced sheet A, whose heads were a
  few pale pixels: "debout, j'ai pas de tête"), the walk (eight frames, its near and far legs alternating), B and C
  (seated at the desk facing left: sitting down, typing, a nod, a look up, a glance at the street, leaning back,
  stretching, his mug, rubbing his eyes, a yawn, thinking, Valorant with his headphones on, a fist at a kill, getting up).
  Each frame keyed off its green, brought to his true size (SHEETS: 1.77 m, 35 px at 19.8 px a metre) on an anchor (his
  seat on the chair's, or his hips over his soles), reduced SS x SS points a pixel (his dark strokes kept: his eyes), his
  tones graded into the room's light and darker down his body (VSHADE), in NFAM families for all frames (his head's own:
  his hair a warm dark brown against the shelves, his face lit, his neck), no lone pixels
  but his face and hands; on each pixel the lamp's rim (the edges facing it, up right) and the screen's light (the edges
  facing it, his face and hands), which street.js weighs with the lamp's and the screen's levels. The walk's frames in a
  step's order, each frame as long as its step at his pace, his planted foot kept on its pixel (walk_steps); its mirror to
  walk out. His mug on the desk where he takes it (a cell of its own, hidden while he drinks).
- her (the owner: "Faut ajouter ma copine"; from a description only, no picture of her): two sheets drawn after pose
  guides at 1.65 m (study_herA, study_herB), in his style, cut whole (a figure may reach past its cell), at her true size,
  a little darker (HER_DIM: her bare skin), her own families after his in the atlas; her walk's and her mug walk's steps;
  her mug (cut from the frame where she sets it down); her places (HER_BED, HER_AT, HER_MUG_X) in MSA.her.
Needs Pillow, numpy, scipy (and tools/ichiraku_interior.py, tools/ichiraku_figures.py).
"""
import base64
import io
import json
import math
import os
import re
import sys
import urllib.request
import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDITS = os.path.join(ROOT, 'tools', 'src', 'edits')
ASSETS = os.path.join(ROOT, 'assets')
MODEL = 'openai/gpt-5.4-image-2'
WIN = (511, 502, 87, 53)                         # the window's canvas in street.js (x, y, w, h): the glass x 512..596, y 502..554
CTX = (490, 464, 618, 592)                       # the room's input: the street round the window (scene x0, y0, x1, y1; square:
                                                 # the model answers 1024 x 1024)
CTX_SRC = (460, 450)                             # (tools/src/edits/study_ctx_city.webp: the layer round it, from there)
CTX_K, GAMMA = 8, 2.0                            # (enlarged with nearest pixels, brightened x ** (1 / GAMMA), as the zones' drafts)


def load(p):
    return np.asarray(Image.open(p).convert('RGBA')).astype(float)


def save(a, p):
    Image.fromarray(np.clip(np.round(a), 0, 255).astype(np.uint8), 'RGBA').save(p, 'WEBP', lossless=True, quality=100, method=6, exact=True)


# ---- the room's input: the street round the window, the window's room blocked out where its things go ----
def room_input():
    city = load(os.path.join(EDITS, 'study_ctx_city.webp'))   # (the layer as it was round the window: tools/src/edits)
    x0, y0, x1, y1 = CTX; k = CTX_K; sx, sy = CTX_SRC
    city = city[y0 - sy:y1 - sy, x0 - sx:x1 - sx]
    big = Image.fromarray(city[..., :3].astype(np.uint8)).resize(((x1 - x0) * k, (y1 - y0) * k), Image.NEAREST)
    g = ImageDraw.Draw(big); wx, wy = WIN[0] - x0, WIN[1] - y0
    def R(a, b, c, d, col): g.rectangle([(wx + a) * k, (wy + b) * k, (wx + c) * k - 1, (wy + d) * k - 1], fill=col)
    def P(pts, col): g.polygon([((wx + x) * k, (wy + y) * k) for x, y in pts], fill=col)
    R(2, 1, 56, 52, (150, 92, 70)); R(58, 1, 85, 52, (150, 92, 70))                     # the back wall, lit
    P([(2, 1), (10, 6), (10, 52), (2, 52)], (70, 44, 46))                                # the left wall, receding
    P([(2, 1), (85, 1), (85, 6), (10, 6)], (96, 60, 54))                                 # the ceiling's edge
    R(10, 39, 42, 41, (92, 58, 40)); R(11, 41, 13, 52, (60, 38, 30)); R(38, 41, 40, 52, (60, 38, 30))   # the desk
    R(19, 26, 33, 37, (20, 22, 30)); R(20, 27, 32, 36, (120, 220, 230)); R(25, 37, 27, 39, (30, 30, 36))   # the monitor
    R(33, 38, 40, 39, (40, 40, 48))                                                      # the keyboard
    R(49, 27, 53, 44, (24, 40, 46)); R(43, 43, 53, 46, (24, 40, 46)); R(47, 46, 49, 52, (30, 30, 34))   # the chair
    R(64, 9, 70, 15, (250, 210, 140)); R(66, 15, 67, 52, (50, 40, 36))                   # the floor lamp
    R(68, 41, 85, 52, (70, 90, 100)); R(78, 37, 85, 42, (200, 190, 180))                 # the bed's corner, its pillow
    a = (np.asarray(big).astype(float) / 255.0) ** (1 / GAMMA) * 255.0
    return Image.fromarray(np.round(a).astype(np.uint8))


# ---- the room: the model's painting fitted behind the glass, pixelated ----
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import ichiraku_interior as RI                   # noqa: E402  (lab, palette, nearest: the street's tools' own)
ROOM_FIT = dict(x=(182, 826), yb=842, sy=9.2)    # the answer's room: its glass between these columns (the mullion at 604..614,
                                                 # local 56..57 as the window's), down to its sill (yb); it painted the room
                                                 # taller than the window (1.07 : 1 for 1.6 : 1): kept at sy answer px a row
                                                 # (its desk 0.67 m, its chair's back at his head), its top (the string of
                                                 # lights over the shelves) above the window's head
ROOM_SRC = ('room2', (-6.0, -8.0, 0.99))         # the room as the owner asked it again ("remplacer le poster", "décoller le lit
                                                 # du mur"): the answer edited (study_room2: a new print, the bed out of the
                                                 # wall), the whole of it, a little moved and scaled (registered on the room's
                                                 # left part: dx, dy, its scale about the image's centre)
GLASS = (2, 1, 85, 52)                           # the glass's columns and rows in the window (local x0, y0, x1, y1)
NPAL = 40                                        # (the room's tones)
GBACK = 1.3                                      # (the answer, asked of the brightened street, darkened back x ** GBACK)


def fit_room(name=None):
    """The answer's room, as the glass's pixels see it: its glass box resampled to the window's (Lanczos, the room's lines
    kept crisp), darkened back a little (GBACK), in NPAL tones (nearest, no dithering)."""
    name, (dx, dy, k) = ROOM_SRC if name is None else (name, (0.0, 0.0, 1.0))
    a = Image.open(os.path.join(EDITS, f'study_{name}_model.webp')).convert('RGB')
    T = lambda v, d: (v - 512.0) * k + 512.0 + d
    (ax0, ax1), yb, sy = ROOM_FIT['x'], ROOM_FIT['yb'], ROOM_FIT['sy']
    gx0, gy0, gx1, gy1 = GLASS; w, h = gx1 - gx0, gy1 - gy0
    c = np.asarray(a.resize((w, h), Image.LANCZOS, box=(T(ax0, dx), T(yb - h * sy, dy), T(ax1, dx), T(yb, dy)))).astype(float)
    c = 255.0 * (np.clip(c, 0, 255) / 255.0) ** GBACK
    pal = RI.palette(c.reshape(-1, 3), NPAL)
    idx = RI.nearest(c.reshape(-1, 3), pal).reshape(h, w)
    return pal[idx], pal, idx


# ---- him: four sheets drawn for him (R28: tools/src/edits/study_walk_model.webp, study_sheet{A,B,C}_model.webp, each from
# its pose guide, the old rig's poses as grey mannequins, study_walk_in.webp, study_sheetX_in.webp), cut off their green,
# brought to his true size ----
SHEETS = {   # its name: (columns, rows), its cells, its scale (sheet px a scene px): the walk's (W) and S's, his standing
             # height there for 1.77 m (35 px at 19.8 px a metre: 335 px, 264 px); B and C, his head's width in profile there
             # (46 px against the walk's 36) at its scale. Sheet A (its standing frames' heads a few pale pixels at this size: the
             # owner, "debout, j'ai pas de tête") and its own walk (its four poses twice) are not used: S redrew them
    'W': ((4, 2), ['walk0', 'walk1', 'walk2', 'walk3', 'walk4', 'walk5', 'walk6', 'walk7'], 335.0 / 35.0),
    'S': ((4, 3), ['standR', 'lookR', 'turnR', 'front', 'turnL', 'standL', 'hand1', 'hand2', 'hinge', 'standup', 'lookL', 'hand3'],
          264.0 / 35.0),
    'B': ((4, 3), ['-', 'sitdown', 'type1', 'type2', 'type3', 'nod', 'lookup', 'glance', 'lean', 'stretch1', 'stretch2', 'sip1'], 7.55),
    'C': ((4, 3), ['sip2', 'sip3', 'rub1', 'rub2', 'yawn', 'think', 'game1', 'game2', 'game3', 'gfist', '-', 'lean2'], 7.55)}
SHEET_FILE = {'W': 'study_walk_model.webp', 'S': 'study_sheetS_model.webp', 'B': 'study_sheetB_model.webp', 'C': 'study_sheetC_model.webp'}
SEATED = {'sitdown', 'type1', 'type2', 'type3', 'nod', 'lookup', 'glance', 'lean', 'stretch1', 'stretch2', 'sip1', 'sip2', 'sip3',
          'rub1', 'rub2', 'yawn', 'think', 'game1', 'game2', 'game3', 'gfist', 'lean2'}
MIRROR = ['walk0', 'walk1', 'walk2', 'walk3', 'walk4', 'walk5', 'walk6', 'walk7']   # (walking out, to the left: their mirror, lit anew)
SS = 8                                           # (points a pixel, each way)
INK = (0.62, 0.3)                                # (a pixel takes its dark strokes' colour when they cover this share of it: eyes, brows)
NFAM, NFAM_HEAD = 24, 10                         # his tones, all frames: his body's, his head's
HEAD_ROWS = 7                                    # (his head's rows, from its top: his hair, his face, his neck)
HEAD_LIFT = (1.12, 2.0)                          # (his head's tones a step lighter: L* a L + b)
HAIR, SKIN_LIFT = (7.0, 12.0), 5.0               # (his hair's warmth, a* and b* at least; his face's lift, L*)
GRADE = dict(L=(0.8, -1.0), C=0.9)               # (his colours under the lamp's fill, as dark as the room round him: L* a L + b, chroma)
VSHADE = 0.42                                    # (darker down his body: his feet this much darker than his head)
RIM = (0.8, 0.3, 1.0, 0.5, 0.6)                  # (the lamp's rim: its edge row, its second row; the screen's: its edge row, its
                                                 # second row, on his skin)
LAMP_DIR = (0.62, -0.78)                         # the lamp, up right of him (his rim)
SCR_DIR = (-1.0, 0.1)                            # the screen, in front of him on the left (seated)
LAMP_COL = (255, 176, 108)                       # (the lamp's light, the screen's before the hour's tint)
SCR_COL = (168, 212, 236)


def key_out(a):
    """his figure off the green: the background, what is far enough from it; the largest piece and what touches it (a mug);
    its edge despilled (its green no higher than its other channels allow)"""
    from scipy import ndimage as ndi
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    m = ~((g > r + 45) & (g > b + 35))
    m = ndi.binary_opening(m, iterations=1)
    lab, n = ndi.label(m)
    sz = ndi.sum(m, lab, range(1, n + 1)); k = int(np.argmax(sz)) + 1
    keep = lab == k; near = ndi.binary_dilation(keep, iterations=6)
    for j in range(1, n + 1):
        if j != k and sz[j - 1] > 30 and (near & (lab == j)).any(): keep |= lab == j
    holes = ndi.binary_fill_holes(keep) & ~keep
    hl, hn = ndi.label(holes)                    # (small holes filled; the green between his legs or his arm and his side stays out)
    if hn:
        hs = ndi.sum(holes, hl, range(1, hn + 1))
        keep |= np.isin(hl, 1 + np.nonzero(hs < 40)[0])
    edge = keep & ~ndi.binary_erosion(keep, iterations=3)
    out = a.copy(); gmax = np.maximum(r, b) + 6
    out[..., 1] = np.where((edge | (g > r + 25) & (g > b + 15)) & (g > gmax), gmax, g)   # (and any pixel of his that the green tints)
    return out, keep


def anchor(m, kind):
    """where a frame stands: seated, the back of his seat (the lowest row of his right part, the rightmost column over it);
    standing, his hips' middle over his soles; half sat (hinge, standup), his feet's middle"""
    ys, xs = np.nonzero(m); L, R_ = xs.min(), xs.max(); top, bot = ys.min(), ys.max()
    if kind == 'seat':
        yb = np.nonzero(m[:, int(R_ - 0.3 * (R_ - L)):].any(1))[0].max()
        xr = np.nonzero(m[max(0, yb - 18):yb + 1].any(0))[0].max()
        return float(xr + 1), float(yb + 1)
    if kind == 'feet':
        low = m[bot - int(0.06 * (bot - top)):bot + 1]; c = np.nonzero(low.any(0))[0]
        return float(c.mean() + 0.5), float(bot + 1)
    band = m[top + int(0.47 * (bot - top)):top + int(0.53 * (bot - top))]; c = np.nonzero(band.any(0))[0]
    return float((c.min() + c.max() + 1) / 2), float(bot + 1)


def reduce_cell(a, m, ax, ay, s):
    """the frame at the scene's pixels, its anchor on a pixel's corner: each pixel SS x SS points of the sheet, full when
    half of them are his, its colour his dark strokes' if they cover INK[1] of it, else the rest's"""
    ys, xs = np.nonzero(m)
    X0 = int(np.floor((xs.min() - ax) / s)) - 1; X1 = int(np.ceil((xs.max() + 1 - ax) / s)) + 1
    Y0 = int(np.floor((ys.min() - ay) / s)) - 1; Y1 = int(np.ceil((ys.max() + 1 - ay) / s)) + 1
    w, h = X1 - X0, Y1 - Y0
    u = ax + (X0 + (np.arange(w * SS) + 0.5) / SS) * s; v = ay + (Y0 + (np.arange(h * SS) + 0.5) / SS) * s
    xi = np.clip(np.floor(u).astype(int), 0, m.shape[1] - 1); yi = np.clip(np.floor(v).astype(int), 0, m.shape[0] - 1)
    inb = ((u >= 0) & (u < m.shape[1]))[None, :] & ((v >= 0) & (v < m.shape[0]))[:, None]
    C = a[yi][:, xi].reshape(h, SS, w, SS, 3).transpose(0, 2, 1, 3, 4).reshape(h, w, SS * SS, 3)
    A = (m[yi][:, xi] & inb).reshape(h, SS, w, SS).transpose(0, 2, 1, 3).reshape(h, w, SS * SS)
    lum = C @ np.array([0.299, 0.587, 0.114])
    ref = np.array([[np.percentile(lum[y, x][A[y, x]], 80) if A[y, x].any() else 0 for x in range(w)] for y in range(h)])
    dark = A & (lum < INK[0] * ref[..., None])
    use = np.where((dark.sum(2) >= INK[1] * np.maximum(A.sum(2), 1))[..., None], dark, A & ~dark)
    use = np.where((use.sum(2) == 0)[..., None], A, use)
    rgb = (C * use[..., None]).sum(2) / np.maximum(use.sum(2), 1)[..., None]
    return rgb, A.mean(2) >= 0.5, -X0, -Y0      # (its anchor in the cell: column, row)


def cells(sheets=None, files=None, seated=None, feet=('hinge', 'standup'), px=None):
    """every frame: its colours and its mask at the scene's pixels, its anchor (a sheet's scale a number, or 'h': each frame
    brought to px pixels tall)"""
    sheets, files, seated = sheets or SHEETS, files or SHEET_FILE, seated or SEATED
    out = {}
    for S, ((nc, nr), names, s0) in sheets.items():
        a = np.asarray(Image.open(os.path.join(EDITS, files[S])).convert('RGB')).astype(float)
        H, W = a.shape[:2]; cw, ch = W / nc, H / nr
        free = files is not SHEET_FILE                     # (her sheets: a figure may reach past its cell: each taken whole,
        if free:                                           # the figure whose middle is in the cell, with a margin round it)
            from scipy import ndimage as ndi
            g = a[..., 1]; fig = ~((g > a[..., 0] + 45) & (g > a[..., 2] + 35)); lab_, k = ndi.label(ndi.binary_opening(fig))
            com = ndi.center_of_mass(fig, lab_, range(1, k + 1)); sz = ndi.sum(fig, lab_, range(1, k + 1))
        for i, n in enumerate(names):
            if n == '-': continue
            x0, y0 = int((i % nc) * cw), int((i // nc) * ch)
            if free:
                js = [j for j in range(k) if sz[j] > 400 and x0 <= com[j][1] < x0 + cw and y0 <= com[j][0] < y0 + ch]
                ys, xs = np.nonzero(np.isin(lab_, [j + 1 for j in js]))
                bx0, by0, bx1, by1 = max(0, xs.min() - 12), max(0, ys.min() - 12), min(W, xs.max() + 13), min(H, ys.max() + 13)
                sub, m = key_out(a[by0:by1, bx0:bx1])
            else:
                sub, m = key_out(a[y0:int(y0 + ch), x0:int(x0 + cw)])
            kind = 'seat' if n in seated else 'feet' if n in feet else 'stand'
            ax, ay = anchor(m, kind)
            s = s0.get(n, s0['*']) if isinstance(s0, dict) else s0
            if s == 'h': ys = np.nonzero(m.any(1))[0]; s = (ys[-1] - ys[0] + 1) / px
            rgb, mm, cx, cy = reduce_cell(sub, m, ax, ay, s)
            out[n] = dict(rgb=rgb, m=mm, ax=cx, ay=cy, kind=kind, sheet=S, sub=sub, mask=m, sax=ax, say=ay, s=s)
    return out


# ---- his walk: the sheet's eight poses in a step's order (its rows came a pair late: the contact, the stance, the passing, the
# swing), each frame's planted foot kept on its pixel: the body moves by that foot's step back at each frame, and each frame
# lasts as long as its step at his pace (no foot sliding, no lurching) ----
WALK_ORDER = ['walk2', 'walk3', 'walk0', 'walk1', 'walk6', 'walk7', 'walk4', 'walk5']
WALK_V = 19.5                                    # his pace (scene px a second: about 1 m/s)
FRAME_T = (0.07, 0.3)                            # (a frame's time, at least, at most)


def feet(c):
    """his feet in a frame (sheet's resolution): each foot's sole, its column and its height from his anchor (scene px)"""
    from scipy import ndimage as ndi
    m = c['mask']; s = c['s']; ax, ay = c['sax'], c['say']
    ys, xs = np.nonzero(m); top, bot = ys.min(), ys.max(); y0 = int(bot - 0.1 * (bot - top))
    low = np.zeros_like(m); low[y0:] = m[y0:]; lab, n = ndi.label(low); out = []
    for j in range(1, n + 1):
        yy, xx = np.nonzero(lab == j)
        if len(yy) < 20: continue
        yl = yy.max(); out.append(((xx[yy >= yl - 4].mean() - ax) / s, (yl + 1 - ay) / s))
    return out


def walk_steps(C, order=None):
    """[frame, its time (s), the step to the next (scene px)]: the planted foot (on the ground in both frames) moved back the
    least (a foot that lands, a foot that goes on bearing)"""
    out = []; order = order or WALK_ORDER
    for k, n in enumerate(order):
        a, b = feet(C[n]), feet(C[order[(k + 1) % len(order)]])
        cand = [fa[0] - fb[0] for fa in a for fb in b if fa[1] > -0.6 and fb[1] > -0.6 and fa[0] >= fb[0]]
        adv = min(cand) if cand else 2.9
        out.append([n, round(float(np.clip(adv / WALK_V, *FRAME_T)), 3), round(float(adv), 2)])
    return out


# ---- his tones and his light: all frames in NFAM families (graded into the room's light), each family's colour under the
# lamp's fill, on an edge the lamp catches, on what the screen lights; each pixel's share of the lamp's rim (the edges that
# face it, up right; a second, softer row) and of the screen's light (the edges that face it, on the left; his face and
# hands) ----
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import ichiraku_figures as FG                    # noqa: E402  (lab2rgb, normals, ring_depth: the figures' own)


def graded(rgb):
    lab = RI.lab(rgb.reshape(-1, 3)); a, b = GRADE['L']
    lab[:, 0] = np.clip(a * lab[:, 0] + b, 0, 100); lab[:, 1:] *= GRADE['C']
    return FG.lab2rgb(lab).reshape(rgb.shape)


def lights(m, skin):
    """the lamp's rim and the screen's light on a frame, 0..1 a pixel"""
    d = FG.ring_depth(m); nx, ny = FG.normals(m); h = m.shape[0]
    ys = np.nonzero(m.any(1))[0]; t = np.clip((np.arange(h) - ys[0]) / max(1, ys[-1] - ys[0]), 0, 1)[:, None]
    def facing(dirv, k2):
        l = np.array(dirv, float); l /= np.hypot(*l); c = nx * l[0] + ny * l[1]
        return np.where(d == 1, np.clip((c - 0.2) / 0.8, 0, 1), np.where(d == 2, k2 * np.clip(c - 0.5, 0, 1) / 0.5, 0)) * m
    rimL = RIM[0] * facing(LAMP_DIR, RIM[1]) * (1.0 - 0.65 * t)          # (the lamp is high: his legs catch less of it)
    rimS = np.maximum(RIM[2] * facing(SCR_DIR, RIM[3]), RIM[4] * skin) * (1.0 - 0.5 * t)
    return np.clip(rimL, 0, 1), np.clip(rimS, 0, 1)


def shaded(c):
    """a frame's colours under the lamp's fill: graded, darker down his body (the lamp is high; under the desk, his legs)"""
    m = c['m']; ys = np.nonzero(m.any(1))[0]; h = m.shape[0]
    t = np.clip((np.arange(h) - ys[0]) / max(1, ys[-1] - ys[0]), 0, 1)[:, None, None]
    return graded(c['rgb'] * (1.0 - VSHADE * t ** 1.5))


def head_band(c):
    """his head's rows (his hair, his face, his neck): the top HEAD_ROWS rows of the frame"""
    m = c['m']; ys = np.nonzero(m.any(1))[0]; b = np.zeros(m.shape, bool); b[ys[0]:ys[0] + HEAD_ROWS] = True
    return b & m


def families(C):
    """the families (their three colours) and each frame's indices: his head's own (his hair's browns, his skin: they never
    fall into the hoodie's teal or the room's dark), the rest of him"""
    sh = {n: shaded(c) for n, c in C.items()}
    hb = {n: head_band(c) for n, c in C.items()}
    famH = RI.palette(np.concatenate([sh[n][hb[n]] for n in C]), NFAM_HEAD)
    labH = RI.lab(famH); labH[:, 0] = np.clip(labH[:, 0] * HEAD_LIFT[0] + HEAD_LIFT[1], 0, 100)   # (his hair a step lighter: read)
    skinH = (labH[:, 1] >= 6) & (labH[:, 2] >= 8) & (labH[:, 0] >= 34)
    hair = ~skinH & (labH[:, 0] < 40)                 # (his hair a warm dark brown, not the night's grey: HAIR, a*, b* at least)
    labH[hair, 1] = np.maximum(labH[hair, 1] * 1.3, HAIR[0]); labH[hair, 2] = np.maximum(labH[hair, 2] * 1.3, HAIR[1])
    labH[skinH, 0] = np.clip(labH[skinH, 0] + SKIN_LIFT, 0, 100)                                     # (his face lit)
    famH = FG.lab2rgb(labH)
    famB = RI.palette(np.concatenate([sh[n][c['m'] & ~hb[n]] for n, c in C.items()]), NFAM)
    fam = np.concatenate([famH, famB])
    lum = fam @ np.array([0.299, 0.587, 0.114]); k = lum[:, None] / 255.0
    c1 = np.clip(fam * 0.85 + np.array(LAMP_COL) * (0.16 + 0.42 * k), 0, 255)     # (the lamp on an edge: warm, brighter)
    c2 = np.clip(fam * 0.6 + np.array(SCR_COL) * (0.16 + 0.4 * k), 0, 255)        # (the screen on him: cool, before the hour's tint)
    labf = RI.lab(fam)
    skinf = (labf[:, 1] >= 8) & (labf[:, 1] <= 40) & (labf[:, 2] >= 8) & (labf[:, 2] <= 45) & (labf[:, 0] >= 28)
    idx = {}
    for n, c in C.items():
        nh = len(famH); v = np.full(c['m'].shape, -1)
        v[hb[n]] = RI.nearest(sh[n][hb[n]], famH)
        body = c['m'] & ~hb[n]; v[body] = nh + RI.nearest(sh[n][body], famB)
        ys = np.nonzero(c['m'].any(1))[0]; keep = np.zeros(c['m'].shape, bool)
        keep[ys[0]:ys[0] + 9] = c['m'][ys[0]:ys[0] + 9]            # (his head as drawn: his face's few pixels, his eyes)
        keep |= c['m'] & skinf[np.maximum(v, 0)]                   # (and his hands)
        idx[n] = FG.unspeckle(v, c['m'], keep)
    return fam, c1, c2, skinf, idx


# ---- the room's points (measured on the fitted room, scene px) and his places ----
SEAT = (557, 547)                                # the back of the chair's seat, where his seat's anchor goes
FLOOR = 556                                      # his soles' row standing (the floor, just under the sill)
STAND = SEAT[0] - 13                             # standing at the chair, before it (his hips' middle)
DOOR, AT_GLASS = 505, 530                        # (the door, behind the frame on the left; where he stands at the glass)
SCREEN = (19, 24, 36, 35)                        # the monitor's glass in the window (local x0, y0, x1, y1)
LAMP_AT = (67, 5)                                # the lamp's shade (local)
DESK_Y = 38                                      # the desk's top row (local): his mug stands on it


# ---- the room's four states, one painting relit: lit (the lamp and the screen), the lamp alone (the screen asleep), the
# screen alone, dark. The dark room: the painting lit by the night alone (night_room: the layer's own dark, its glass's sheen
# and low frequencies, with the room's shapes in it); the screen's light: from the monitor (a soft falloff, wider than high, more toward the desk and him in front
# of it), the room's own colours under it turned to the screen's light at their luminance; the lamp alone: the painting with
# the screen asleep and its glow taken off; lit: the lamp alone and the screen's light added (street.js tints that part) ----
ROOM_GAIN = 1.1                                  # (the room's light against the street's other lit windows)
DARK_K = 0.3                                     # (how much of the room's shapes the screen's base keeps: its light's measure)
NIGHT = dict(K=0.9, sig=7.0, top=0.4, chroma=0.15, A=(0.2, 1.7))   # the dark room, the painting lit by the night alone (night_room):
                                                 # how much of its shapes it keeps, the lamp's falloff taken off below this
                                                 # scale (px), the light from below on the ceiling's side (its top this much
                                                 # brighter), the painting's own hue kept, its shapes' range
SCR_FALL = (17.0, 11.0, 3.0)                     # (the screen's light: its spread across and up and down, px; its centre lowered by)
SCR_K = 1.9                                      # (its strength)
SCR_LIT = 0.55                                   # (its share in the room lit by the lamp too)
STANDBY = (22, 26, 36)                           # (the screen asleep: a dark glass)
CHAIR, CHAIR_TONE = ((38, 20, 55, 53), (31, 37, 55, 53)), (1.1, 0.9, 0.95)   # (the chair's boxes in the window, local: its back,
                                                 # its seat under the desk's end, the monitor kept out; its black, at its luminance)


def room_states():
    rgb, pal, idx = fit_room()
    before = load(os.path.join(EDITS, 'study_before_city.webp'))[..., :3]
    galpha = load(os.path.join(ASSETS, 'z5_glass.webp'))[..., 3]
    gx0, gy0, gx1, gy1 = GLASS
    rgb = rgb.copy()                                                  # (the chair black, not teal: he sits in it in his teal hoodie)
    for cx0, cy0, cx1, cy1 in CHAIR:
        sub = rgb[cy0 - gy0:cy1 - gy0, cx0 - gx0:cx1 - gx0]
        teal = (sub[..., 2] > sub[..., 0] + 3) & (sub[..., 1] > sub[..., 0])
        sub[teal] = (sub[teal] @ np.array([0.299, 0.587, 0.114]))[:, None] * np.array(CHAIR_TONE)
    full = before.copy(); full[gy0:gy1, gx0:gx1] = rgb * ROOM_GAIN
    frame = galpha < 250; full[frame] = before[frame]                # (the frame and the mullion: the layer's, in front)
    H, W = full.shape[:2]; yy, xx = np.mgrid[0:H, 0:W]
    lum = lambda a: a @ np.array([0.299, 0.587, 0.114])
    from scipy.ndimage import gaussian_filter
    low = np.stack([gaussian_filter(before[..., c], 6) for c in range(3)], -1)
    rel = lum(full) / max(1.0, np.median(lum(full)[~frame])) - 1.0
    dark = np.clip(low * (1.0 + DARK_K * np.clip(rel, -0.8, 1.5))[..., None], 0, 255)
    dark[frame] = before[frame]
    sx0, sy0, sx1, sy1 = SCREEN
    box = (xx >= sx0) & (xx < sx1) & (yy >= sy0) & (yy < sy1)
    scr = box & (full[..., 2] > full[..., 0] + 10) & (lum(full) > 40)  # (the screen's glowing pixels)
    cx, cy = (sx0 + sx1) / 2, (sy0 + sy1) / 2 + SCR_FALL[2]
    g = np.exp(-((xx - cx) ** 2 / (2 * SCR_FALL[0] ** 2) + (yy - cy) ** 2 / (2 * SCR_FALL[1] ** 2)))
    g *= np.where(xx > cx, 1.0, 0.75); g[frame] = 0
    under = np.clip(full - dark, 0, 255); Lu = lum(under)[..., None]
    sc = np.array(SCR_COL); turned = 0.75 * Lu * sc / lum(sc) + 0.25 * under
    s_only = dark + SCR_K * g[..., None] * turned
    s_only[scr] = full[scr]
    lamp = np.maximum(full - 0.35 * (s_only - dark), 0.85 * full)     # (its own glow taken off, never a hole: 15 % at most)
    lamp[scr] = np.array(STANDBY) + 0.12 * (full[scr] - lum(full[scr])[..., None])
    lit = np.clip(lamp + SCR_LIT * (s_only - dark), 0, 255); lit[scr] = full[scr]   # (with the lamp on, its light counts for less)
    night = night_room(lamp, low, frame, yy); night[frame] = before[frame]   # (the lamp off: the same room by the night's light)
    s_only = s_only - dark + night; s_only[scr] = full[scr]; dark = night
    for a in (lamp, s_only, lit): a[frame] = before[frame]
    return dict(lit=lit, lamp=lamp, scr=s_only, dark=dark, scrmask=scr, frame=frame)


def night_room(lamp, low, frame, yy):
    """The room with the lamp off and the screen asleep, the night alone lighting it: what the window showed of it was the
    pane's own dark with a third of the room's shapes, a flat block in the middle of the phone's view. The painting with its
    screen asleep (the lamp state), its lamp's light taken off (its luminance over its own low pass, the glass only: the
    shapes' albedo, crisp), lit by the pane's dark (the painter's low frequencies, its sheen), a little brighter toward the
    top (the street's light comes from below, onto the ceiling's side and the walls' tops), in that dark's colour with a
    little of the room's own hue: the books, the whiteboard, the dark monitor, the chair, the lamp's paper shade, the print
    and the bed read, as the street's other dark rooms do"""
    from scipy.ndimage import gaussian_filter
    lum = lambda a: a @ np.array([0.299, 0.587, 0.114])
    K, sig, top, chroma, (a0, a1) = NIGHT['K'], NIGHT['sig'], NIGHT['top'], NIGHT['chroma'], NIGHT['A']
    gx0, gy0, gx1, gy1 = GLASS; m = ~frame; L = lum(lamp)
    w = gaussian_filter(m.astype(float), sig); Lb = gaussian_filter(np.where(m, L, 0.0), sig) / np.maximum(w, 1e-3)
    A = np.clip(L / np.maximum(Lb, 1.0), a0, a1)
    base = low * (1.0 + top * np.clip(1.0 - (yy - gy0) / (gy1 - gy0), 0, 1) ** 1.5)[..., None]
    hue = lambda a: a / np.maximum(lum(a)[..., None], 1.0)
    out = (hue(base) * (1 - chroma) + hue(lamp) * chroma) * (lum(base) * (1.0 + K * (A - 1.0)))[..., None]
    return np.clip(out, 0, 255)


def mirrored(c):
    o = dict(c); o['rgb'] = c['rgb'][:, ::-1]; o['m'] = c['m'][:, ::-1]; o['ax'] = c['m'].shape[1] - c['ax']
    return o


def mug_cell(c):
    """his mug, from the frame where he takes it: its white pixels in front of him"""
    lab = RI.lab(c['rgb'].reshape(-1, 3)).reshape(c['rgb'].shape)
    Cs = np.hypot(lab[..., 1], lab[..., 2]); m = c['m'] & (lab[..., 0] > 48) & (Cs < 20)
    m[:, int(0.45 * m.shape[1]):] = False
    m[int(c['ay']) - 2:] = False                  # (above his seat: his soles are white too)
    from scipy import ndimage as ndi
    lab_, n = ndi.label(m)
    if n > 1: m = lab_ == 1 + int(np.argmax(ndi.sum(m, lab_, range(1, n + 1))))
    ys, xs = np.nonzero(m); y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    return dict(rgb=c['rgb'][y0:y1, x0:x1], m=m[y0:y1, x0:x1], ax=c['ax'] - x0, ay=c['ay'] - y0, kind='prop')


# ---- his girlfriend (the owner: "Faut ajouter ma copine"; from a description only, no picture of her anywhere): two sheets
# drawn for her after pose guides at 1.65 m (study_herA: her walk, standing, turning, at the glass, holding a mug; study_herB:
# on the bed with her phone, getting up, setting a mug down, leaning over his chair, turning to him, a kiss on his cheek,
# walking with a mug), in his style; at her true size (33 px standing: HER_PX), her own families (her light-chestnut hair,
# her skin, her black clothes), the same light on her as on him ----
HER_PX = 33.0
HER_DIM = 0.74
HER_SHEETS = {   # (A's walk at its rows' height, 200 px; its standing frames each at its own height; B at its walk's, 250 px)
    'HA': ((4, 4), ['hwalk0', 'hwalk1', 'hwalk2', 'hwalk3', 'hwalk4', 'hwalk5', 'hwalk6', 'hwalk7', 'hstandR', 'hstandL', 'hfront',
                    'hturnL', 'hturnR', 'hglass', 'hjoin', 'hmugStand'], {'*': 'h', **{f'hwalk{k}': 200.0 / HER_PX for k in range(8)}}),
    'HB': ((4, 3), ['hbed1', 'hbed2', 'hbedLook', 'hrise', 'hset', 'hwatch', 'hlook', 'hkiss', 'hmug0', 'hmug1', 'hmug2', 'hmug3'], 250.0 / HER_PX)}
HER_FILE = {'HA': 'study_herA_model.webp', 'HB': 'study_herB_model.webp'}
HER_SEATED = {'hbed1', 'hbed2', 'hbedLook'}
HER_FEET = ('hrise', 'hset', 'hwatch', 'hlook', 'hkiss')   # (bent: anchored on her feet)
HER_WALKS = (['hwalk0', 'hwalk1', 'hwalk2', 'hwalk3', 'hwalk4', 'hwalk5', 'hwalk6', 'hwalk7'],   # (the order a step's frames come in:
             ['hwalk2', 'hwalk3', 'hwalk0', 'hwalk1', 'hwalk6', 'hwalk7', 'hwalk4', 'hwalk5'])   #  the one whose steps are the evenest)
HER_BED = (584, 546)                             # her seat on the bed's edge (the duvet's top, local 73, 44)
HER_AT = dict(watch=566, glass=543, sit=574)     # (her places, her feet's middle: by his chair's back, at the glass by him, before the bed)
HER_MUG_X = 526                                  # (where she sets her mug down on the desk, left of the monitor: its left edge)


def her_mug(c):
    """her mug, from the frame where she sets it down (facing right): its few pixels at the tip of her reach (not her skin)"""
    lab = RI.lab(c['rgb'].reshape(-1, 3)).reshape(c['rgb'].shape)
    m = c['m'].copy(); xs = np.nonzero(m.any(0))[0]; m[:, :xs[-1] - 2] = False
    skin = (lab[..., 1] > 10) & (lab[..., 2] > 12) & (lab[..., 0] > 40); m &= ~skin
    ys, xs = np.nonzero(m); y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    return dict(rgb=c['rgb'][y0:y1, x0:x1], m=m[y0:y1, x0:x1], ax=c['ax'] - x0, ay=c['ay'] - y0, kind='prop')


def her():
    """her frames (her walk's mirror to the left, her mug walk's to the right, her mug), her steps"""
    C = cells(HER_SHEETS, HER_FILE, HER_SEATED, HER_FEET, HER_PX)
    for c in C.values(): c['rgb'] = c['rgb'] * HER_DIM       # (her bare skin, much of her: as dark as the room round her)
    st = min((walk_steps(C, o) for o in HER_WALKS), key=lambda w: np.std([a for _, _, a in w]))
    for k in range(8): C[f'hwalkL{k}'] = mirrored(C[f'hwalk{k}'])
    for k in range(4): C[f'hmugR{k}'] = mirrored(C.pop(f'hmug{k}'))
    mst = min((walk_steps(C, o) for o in (['hmugR0', 'hmugR1', 'hmugR2', 'hmugR3'], ['hmugR2', 'hmugR3', 'hmugR0', 'hmugR1'])),
              key=lambda w: np.std([a for _, _, a in w]))
    adv = [a for _, _, a in mst]                      # (her mug walk's four frames: a step that jumps, all steps the same)
    if max(adv) > 2.2 * np.median(adv):
        u = float(np.mean(adv)); mst = [[n, round(float(np.clip(u / WALK_V, *FRAME_T)), 3), round(u, 2)] for n, _, _ in mst]
    C['hsetR'] = mirrored(C.pop('hset')); C['hmugStandR'] = mirrored(C.pop('hmugStand'))   # (she sets it down facing right: from the
    C['hmugProp'] = her_mug(C['hsetR'])                                                    #  door's side, on the desk's free left part)
    return C, st, mst


def him():
    """his frames (and the walk's mirrors, the mug) as the atlas street.js reads: R a family, G the lamp's rim, B the screen's
    light, A his shape; their cells [x, y, w, h, anchor x, anchor y]; the families' colours; the walk's steps"""
    C = cells()
    for n in MIRROR: C[n.replace('walk', 'walkL')] = mirrored(C[n])
    C['mug'] = mug_cell(C['sip1'])
    fam, c1, c2, skinf, idx = families(C)
    CH, hsteps, hmsteps = her()                       # (hers after his: her families' indices after his)
    hfam, hc1, hc2, hskin, hidx = families(CH); off = len(fam)
    for n, v in hidx.items(): idx[n] = np.where(v >= 0, v + off, -1)
    fam, c1, c2, skinf = np.concatenate([fam, hfam]), np.concatenate([c1, hc1]), np.concatenate([c2, hc2]), np.concatenate([skinf, hskin])
    C.update(CH)
    names = sorted(C, key=lambda n: (-C[n]['m'].shape[0], n))
    W, x, y, rowh, boxes = 256, 0, 0, 0, {}
    for n in names:
        h, w = C[n]['m'].shape
        if x + w > W: x, y, rowh = 0, y + rowh + 1, 0
        boxes[n] = [x, y, w, h]; x += w + 1; rowh = max(rowh, h)
    img = np.zeros((y + rowh, W, 4), np.uint8)
    for n in names:
        bx, by, w, h = boxes[n]; v = idx[n]; m = C[n]['m']
        rl, rs = lights(m, m & skinf[np.maximum(v, 0)])
        if C[n].get('kind') in ('stand', 'feet'): rs = rs * 0.35          # (standing, he faces the screen no more: little of its light)
        cell = np.zeros((h, w, 4), np.uint8)
        cell[..., 0] = np.maximum(v, 0); cell[..., 1] = np.round(255 * rl); cell[..., 2] = np.round(255 * rs); cell[..., 3] = m * 255
        img[by:by + h, bx:bx + w] = cell
        boxes[n] += [int(C[n]['ax']), int(C[n]['ay'])]
    steps = walk_steps(C)
    mug = C['mug']                                   # (its place: where he holds it as he takes it, its foot on the desk's top)
    mug_at = [SEAT[0], WIN[1] + DESK_Y - (mug['m'].shape[0] - mug['ay'])]
    famt = [[int(round(v)) for v in list(fam[i]) + list(c1[i]) + list(c2[i])] for i in range(len(fam))]
    return img, dict(cells=boxes, fam=famt, walk=steps, mug=mug_at, C=C, idx=idx, fam_rgb=(fam, c1, c2), hwalk=hsteps, hmug=hmsteps)


INPUTS = {'room': room_input}
REFS = {'room': ['study_room0_model.webp'], 'sheetA': ['study_room_model.webp'],   # (the references after each input: the
        'sheetB': ['study_sheetA_model.webp', 'study_room_model.webp'],             # first room for the room's second ask,
        'sheetC': ['study_sheetA_model.webp', 'study_room_model.webp'],             # the room and sheet A for his sheets)
        'walk': ['study_sheetA_model.webp'],
        'sheetS': ['study_sheetB_model.webp', 'study_walk_model.webp'],
        'herA': ['study_sheetS_model.webp', 'study_room2_model.webp'],          # (her sheets: his for the style, the room;
        'herB': ['study_herA_model.webp', 'study_sheetS_model.webp']}            # then her first sheet for herself)


# ---- what his screen shows by the hour (the owner: "remplacer ce qu'il y a sur l'écran", then "PC ok": alive): four screens
# drawn by the image model on a grey board (study_screens: his code editor, the same scrolled, Overleaf's source and its
# PDF, a shooter's view at dusk). At the glass's 17 x 11 pixels a screen of text is its lines: each line of the drawing,
# its coloured words and their places across, read into a row of tokens (SCR_TOK tones), which street.js types out on
# every other row as he types, its cursor blinking, scrolling down the file; now and then a terminal with a training run
# (its loss curve going down, its progress bar); Overleaf: the source typed on the left, the PDF's page on the right (its
# title, its columns, its chart), recompiled now and then; the game's view, a picture, resampled in its own tones
# (study_screens.webp), its crosshair, a kill feed line at each kill. Their light a little under the room's (SCR_GAIN) ----
SCREENS = ['code', 'code2', 'paper', 'game']
SCR_GAIN, SCR_TOK = 0.86, 6


def screen_boxes(a):
    from scipy import ndimage as ndi
    bg = np.abs(a - 128).max(-1) < 14; lab_, n = ndi.label(~bg); sz = ndi.sum(~bg, lab_, range(1, n + 1)); boxes = []
    for j in np.argsort(sz)[::-1][:4]:
        ys, xs = np.nonzero(lab_ == j + 1); boxes.append((xs.min() + 3, ys.min() + 3, xs.max() - 2, ys.max() - 2))
    return sorted(boxes, key=lambda b: (round(b[1] / 200), b[0]))   # (row by row, left to right: as SCREENS)


def text_lines(P, ground, x0f, x1f, cols):
    """the lines of text in P (between the fractions x0f..x1f of its width): each a list of cols colours (None: ground)"""
    h, w = P.shape[:2]; xa, xb = int(x0f * w), int(x1f * w); Q = P[:, xa:xb]
    ink = np.abs(Q - ground).max(-1) > 40; prof = ink.mean(1) > 0.01
    lines, y = [], 0
    while y < h:
        if prof[y]:
            y1 = y
            while y1 < h and prof[y1]: y1 += 1
            if y1 - y >= 4: lines.append((y, y1))
            y = y1
        else: y += 1
    out = []
    for ya, yb in lines:
        band, inkb = Q[ya:yb], ink[ya:yb]; row = []
        for c in range(cols):
            ca, cb = int(c * Q.shape[1] / cols), int((c + 1) * Q.shape[1] / cols); m = inkb[:, ca:cb]
            row.append(np.median(band[:, ca:cb][m], 0) if m.mean() > 0.22 else None)
        out.append(row)
    return out


def tokens(lines, k):
    """lines of colours into a few tones and strings of their indices ('0': the ground)"""
    cols = np.array([c for L in lines for c in L if c is not None]); pal = RI.palette(cols, k)
    out = []
    for L in lines:
        out.append(''.join('0' if c is None else str(1 + int(RI.nearest(np.asarray(c)[None], pal)[0])) for c in L))
    return pal, out


def screens():
    """the game's view at the glass's pixels, and what street.js draws the others with (MSA.scrn)"""
    a = np.asarray(Image.open(os.path.join(EDITS, 'study_screens_model.webp')).convert('RGB')).astype(float)
    sx0, sy0, sx1, sy1 = SCREEN; w, h = sx1 - sx0, sy1 - sy0; B = dict(zip(SCREENS, screen_boxes(a)))
    rgb = lambda c: [int(round(v)) for v in np.clip(np.asarray(c) * SCR_GAIN, 0, 255)]
    x0, y0, x1, y1 = B['game']; P = a[y0:y1, x0:x1]       # (a picture: resampled in its tones, the enemy a red pixel, the health bar)
    im = np.asarray(Image.fromarray(P.astype(np.uint8)).resize((w, h), Image.LANCZOS)).astype(float)
    im = np.clip(im * 1.25, 0, 255)                         # (a game's screen: brighter than a page of code)
    pal = RI.palette(im.reshape(-1, 3), 10); im = pal[RI.nearest(im.reshape(-1, 3), pal)].reshape(h, w, 3)
    red = (P[..., 0] > 150) & (P[..., 1] < 90) & (P[..., 2] < 90)
    red[:int(0.35 * P.shape[0])] = False; red[:, :int(0.3 * P.shape[1])] = False   # (not the minimap's dot)
    if red.any():
        ys, xs = np.nonzero(red); im[int(np.median(ys) * h / P.shape[0]), int(np.median(xs) * w / P.shape[1])] = (232, 64, 52)
    grn = (P[..., 1] > 140) & (P[..., 0] < 140) & (P[..., 2] < 120)
    if grn.any(): im[h - 1, 1:6] = np.median(P[grn], 0)
    game = np.clip(im * SCR_GAIN, 0, 255)
    code = []                                               # (his code: both screens' lines, in tokens)
    for n in ('code', 'code2'):
        x0, y0, x1, y1 = B[n]; P = a[y0:y1, x0:x1]
        ground = np.median(P[:, int(0.3 * P.shape[1]):].reshape(-1, 3), 0); code += text_lines(P, ground, 0.13, 1.0, w - 3)
    gut = np.median(P[:, :int(0.08 * P.shape[1])].reshape(-1, 3), 0)
    num = np.median(P[:, int(0.02 * P.shape[1]):int(0.06 * P.shape[1])].reshape(-1, 3), 0)
    cpal, clines = tokens(code, SCR_TOK)
    x0, y0, x1, y1 = B['paper']; P = a[y0:y1, x0:x1]         # (Overleaf: its source's lines; its page's tones)
    pg = np.median(P[:, :int(0.4 * P.shape[1])].reshape(-1, 3), 0); half = w // 2
    ppal, plines = tokens(text_lines(P, pg, 0.08, 0.5, half - 2), 3)
    Pg = P[:, int(0.53 * P.shape[1]):].reshape(-1, 3); paper = np.percentile(Pg, 70, axis=0); dark = Pg[np.argmin(Pg.sum(1))]
    bars = [Pg[np.argmax(Pg @ np.array(m))] for m in ((-1, -0.2, 1), (1, 0.4, -1), (1, -1, -1))]
    data = dict(code=dict(g=rgb(ground), gut=rgb(gut), num=rgb(0.5 * gut + 0.5 * np.array([140, 146, 160])), cur=rgb((236, 236, 228)),
                          pal=[rgb(c) for c in cpal], lines=clines),
                paper=dict(g=rgb(pg), pal=[rgb(c) for c in ppal], lines=plines, page=rgb(paper), title=rgb(0.6 * dark + 0.4 * paper),
                           text=rgb(0.55 * paper + 0.45 * np.array([120, 120, 128])), axis=rgb(0.6 * paper + 0.4 * np.array([90, 90, 96])),
                           bars=[rgb(c) for c in bars]),
                game=dict(cross=rgb((236, 236, 228)), hit=rgb((240, 70, 60)), feed=rgb((228, 228, 220)), red=rgb((232, 64, 52))))
    return game, data


JS = os.path.join(ASSETS, 'street.js')
OUTS = {'lit': 'win_z5_room.webp', 'lamp': 'z5_lamp.webp', 'scr': 'z5_screen.webp', 'dark': 'z5_dark.webp'}


def build():
    """everything in assets/ and the line MSA in street.js"""
    R = room_states()
    for k, f in OUTS.items():
        a = np.dstack([np.clip(np.round(R[k]), 0, 255), np.full(R[k].shape[:2], 255.0)])
        if k == 'dark': Image.fromarray(a[..., :3].astype(np.uint8), 'RGB').save(os.path.join(ASSETS, f), 'WEBP', lossless=True, quality=100, method=6, exact=True)
        else: save(a, os.path.join(ASSETS, f))
    img, meta = him()
    Image.fromarray(img, 'RGBA').save(os.path.join(ASSETS, 'study_him.webp'), 'WEBP', lossless=True, quality=100, method=6, exact=True)
    seated = SEATED
    cells_ = {n: b + [1 if n in seated or n == 'mug' else 2 if n in HER_SEATED else 0] for n, b in meta['cells'].items()}   # (1: on his seat, 2: on the bed)
    wx, wy = WIN[0], WIN[1]; sx0, sy0, sx1, sy1 = SCREEN
    sc, scd = screens()
    save(np.dstack([sc, np.full(sc.shape[:2], 255.0)]), os.path.join(ASSETS, 'study_screens.webp'))
    msa = dict(cells=cells_, fam=meta['fam'], walk=meta['walk'], mug=[int(v) for v in meta['mug']],
               scrn=dict(at=[WIN[0] + sx0, WIN[1] + sy0], w=sx1 - sx0, h=sy1 - sy0, **scd),
               her=dict(walk=meta['hwalk'], mug=meta['hmug'], bed=list(HER_BED), mugX=HER_MUG_X, **HER_AT),
               at=dict(seat=list(SEAT), stand=STAND, floor=FLOOR, door=DOOR, glass=AT_GLASS, scr=[wx + sx0, wy + sy0, sx1 - sx0, sy1 - sy0],
                       lamp=[wx + LAMP_AT[0], wy + LAMP_AT[1]]))
    js = open(JS, encoding='utf-8').read()
    line = '  const MSA = ' + json.dumps(msa, separators=(',', ':')) + ';   // (tools/owner_study.py)'
    js2, n = re.subn(r'  const MSA = \{.*?\};   // \(tools/owner_study\.py\)', lambda m: line, js, count=1)
    assert n == 1, 'the line MSA is missing from assets/street.js'
    if js2 != js: open(JS, 'w', encoding='utf-8').write(js2)
    print('study: the room (4 states), his frames (%d cells, atlas %d x %d), MSA %s' % (len(cells_), img.shape[1], img.shape[0], 'written' if js2 != js else 'unchanged'))


def draw(city, unlit, box):
    """tools/redraw_zones.py's zone 'study': the dark room behind the glass in both layers (the frame and the mullion as they
    are); what changed"""
    R = room_states(); x0, y0, x1, y1 = box
    assert (x0, y0, x1 - x0, y1 - y0) == tuple(WIN), 'the zone is the window'
    galpha = load(os.path.join(ASSETS, 'z5_glass.webp'))[..., 3]; g = galpha >= 250
    ch = np.zeros(city.shape[:2], bool)
    for a in (city, unlit):
        sub = a[y0:y1, x0:x1]; old = sub[..., :3].copy()
        sub[..., :3][g] = np.round(np.clip(R['dark'], 0, 255))[g]
        ch[y0:y1, x0:x1] |= np.abs(sub[..., :3] - old).max(-1) > 0
    return ch


def api_key():
    k = os.environ.get('OPENROUTER_API_KEY')
    if k: return k
    p = os.path.expanduser('~/.config/openrouter/key')
    return open(p).read().strip() if os.path.exists(p) else 'proxy-injected'


def ask(name):
    """Asks the image model (its input images: study_NAME_in.webp and the references REFS[name]; its prompt
    study_NAME_prompt.txt); saves its answer as study_NAME_model.webp."""
    imgs = [os.path.join(EDITS, f'study_{name}_in.webp')] + [os.path.join(EDITS, r) for r in REFS.get(name, [])]
    content = [{"type": "text", "text": open(os.path.join(EDITS, f'study_{name}_prompt.txt')).read().strip()}]
    for p in imgs:
        buf = io.BytesIO(); Image.open(p).convert('RGB').save(buf, 'PNG')
        content.append({"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()}})
    body = {"model": MODEL, "modalities": ["image", "text"], "usage": {"include": True}, "messages": [{"role": "user", "content": content}]}
    req = urllib.request.Request('https://openrouter.ai/api/v1/chat/completions', data=json.dumps(body).encode(),
                                 headers={'Authorization': 'Bearer ' + api_key(), 'Content-Type': 'application/json'})
    d = json.loads(urllib.request.urlopen(req, timeout=900).read())
    url = d['choices'][0]['message']['images'][0]['image_url']['url']
    im = Image.open(io.BytesIO(base64.b64decode(url.split(',', 1)[1])))
    im.save(os.path.join(EDITS, f'study_{name}_model.webp'), 'WEBP', lossless=True, quality=100, method=6)
    print(name, 'answer', im.size, 'saved; cost', d.get('usage', {}).get('cost'), '$')



def main():
    if '--input' in sys.argv:
        n = sys.argv[sys.argv.index('--input') + 1]
        INPUTS[n]().save(os.path.join(EDITS, f'study_{n}_in.webp'), 'WEBP', lossless=True, quality=100, method=6); return
    if '--ask' in sys.argv:
        ask(sys.argv[sys.argv.index('--ask') + 1]); return
    if '--preview' in sys.argv:
        out = sys.argv[sys.argv.index('--preview') + 1]; os.makedirs(out, exist_ok=True)
        R = room_states()
        a = np.concatenate([R[k] for k in ('lit', 'lamp', 'scr', 'dark')], 0)
        Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).resize((a.shape[1] * 4, a.shape[0] * 4), Image.NEAREST).save(os.path.join(out, 'room_states_x4.png'))
        return
    build()


if __name__ == '__main__':
    main()
