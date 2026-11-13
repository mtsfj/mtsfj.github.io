#!/usr/bin/env python3
"""The house at the street's end (zone 9, x 762-870): its paper lantern by the door, its upstairs lit window and its ground
floor, drawn on the pixel grid (the owner's picks, 2026-11-13). Three zones of tools/redraw_zones.py (z9lan, z9win,
z9base, in that order: method 'hand') call this module; run that tool, then tools/bake_retouches.py. Same input, same bytes.

The lantern (x 801-807, y 579-587, by the doorway's left jamb; lit it is the comp win_z9_lantern, from 8:30 to 0:30;
off, at 3 h and in the power cut, the street's layers show): off, the painter had a flat red disc there. Now one paper
lantern, the same in both states: a barrel of paper 7 px wide (5 on its top and foot rows), a lacquered cap over and
under it, and what holds it: an iron bracket on the jamb (a plate under the door's head, at x 806), its arm over to the
lantern's axis, the hook down to the cap. Lit, the paper keeps the painter's lit colours, laid by rank on a barrel's
shading (bright on its axis, darker toward its turning sides and its caps); off, that picture darkened as the painter
darkened his lantern (his off disc over his lit paper, channel by channel: a crimson in the night's blue, not a dim
orange), its caps and bracket the night's dark of the door's head line. Lit, the comp's glow on the wall and on the
jamb stays the painter's.

The window (x 807-856, y 499-530, a sliding window to the floor of its little balcony; lit it is the comp win_z9_window,
a home's light on about three quarters of the time; off, the street's layers): its right pane was dark blocks nobody
could read, its railing irregular bars with a smudge. Now a pair of curtains drawn across the panes: lit, the painter's
left one as he drew it (its folds, its heading cool in the head's shadow, warm and bright low down), its smudge (dark
strokes on its right) filled down each column from the rows over and under it, its foot behind the railing run down
from the row over the rail at his light there; the right one the left mirrored about the meeting stiles, a little
dimmer; what is new in his lit palette (his colours by brightness). Off, the same curtains in the painter's dark glass
(his off light, smoothed, carrying half of the folds' relief). In front, the railing
in both states, as the painter's elements: its top rail (a lit row over its face), its kick rail, its end posts, and five
bars on the balcony's own rhythm, every 9.5 px between the posts (813, 822, 832, 841, 851: the middle one on the panes'
meeting stiles); the Pokemon Center's awning stays in front of its lower right corner. The comp is clear over the railing
(the street's railing shows, lit or not) and takes the new curtains over the glass; its frame pixels stay the painter's.

The ground floor (x 760-869, y 566-640; the zone z9base, after z9lan: the owner, "la maison, refaire le bas, pas hyper
clean"): blotches nobody could read as doors. The house faces the street at its end, so it is drawn face on, its lines
level and plumb as the painter's head line (577), mid rail (610) and sill (634) are. Now, on the painter's light (his
picture's low frequencies over each part, SIG; R2, R18): left of the lantern a lattice window over a wainscot of three
boards, the jamb the lantern hangs by, and the two sliding doors, each a lattice over a plain kick panel; one rail line
across the front (the window's sill and the doors' mid rail, its shadow on the painter's dark line at 610); slats every
3 px, symmetric in each opening; members lit on their left edge and their top, a shade on their right and under them.
The right leaf is open a little: the gap between the leaves (x 832-836) the dark inside, the sill running under it (the
cat's eyes show there, street.js CAT). The posts each column evened down (the left one's ledge along its rows), the
boards under the balcony and the lintel each row evened along it, the sill a lit top and its face, the sidewalk in the
eave's shadow evened along its rows; the curb under it, the meter box, the banner and the plaque (tools/e33_banner.py:
its shadow on the boards laid again) and the lantern (z9lan) as they are. The power cut: the same picture times the
painter's darkening there, smoothed. Lit, the lantern's light (its comp, win_z9_lantern, taken on from z9lan's): the
painter's streaks made a soft pool (his lit over unlit picture, smoothed over POOL, its light in total his), laid on the
new front, taken more by the slats and the frames that face it than by the dark behind them (SPREAD).
"""
import os
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, gaussian_filter1d

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDITS = os.path.join(ROOT, 'tools', 'src', 'edits')
lum = lambda z: 0.299 * z[..., 0] + 0.587 * z[..., 1] + 0.114 * z[..., 2]

# the lantern (scene px): its paper rows (x0, x1 inclusive), its caps, its bracket
LANTERN_COMP = ('win_z9_lantern', 775, 559)
PAPER = {580: (802, 806), 581: (801, 807), 582: (801, 807), 583: (801, 807), 584: (801, 807), 585: (801, 807),
         586: (802, 806)}
CAPS = {579: (802, 806), 587: (802, 806)}
AXIS = (804.5, 583.5)                      # (its centre, continuous coordinates)
BRACKET = [(806, 575), (806, 576), (804, 576), (805, 576), (804, 577), (806, 577), (804, 578)]   # (plate, arm, hook)
HEAD = [(x, 577) for x in list(range(807, 813)) + list(range(816, 826))]   # the door's head line: the night's dark
ROUND = (0.42, 0.22)                       # the barrel's shading: across (u^2), along (v^2)

# the window (scene px)
WINDOW_COMP = ('win_z9_window', 804, 497)
PANES = [(807, 830), (834, 856)]           # the glass, left and right of the meeting stiles (x 831-833)
GLASS_Y = (499, 530)                       # its rows: from under the head to the balcony's floor (row 531)
SMUDGE = (824, 503, 830, 512)              # (the painter's dark strokes on his left curtain, inclusive)
RIGHT_K = 0.88                             # the right curtain's light against the left one's
TOP_RAIL, TOP_FACE, KICK_RAIL = 518, 519, 528
OLD_BARS = [810, 819, 828, 838, 849]       # (the painter's bars, irregular)
POSTS = [(803, 804, 805), (860, 861, None)]   # (lit columns, its shade column), rows 518-530
BARS = [813, 822, 832, 841, 851]          # one px each, rows 520-530: 9.5 px apart between the posts' centres
BAR_Y = (520, 530)
SHUT_K = 0.5                               # the folds' relief kept behind the dark glass

# the ground floor (scene px, inclusive)
GROUND_BOX = (760, 566, 870, 641)
POST_L, LEDGE = (761, 774), (610, 611)     # the corner post (its ledge's rows)
POST_R = (861, 869)                        # the right post (its shade line at 861)
METER = (865, 603, 872, 624)               # the meter box on it, as painted (x0, y0, x1, y1)
BAND = (566, 577)                          # the boards under the balcony, the lintel, its shadow on 577
FRONT, ROWS = (775, 860), (578, 633)       # the window, the jamb, the leaves: drawn
WINDOW, JAMB = (775, 802), (803, 807)
LEAVES = [(808, 831), (837, 860)]
GAP = (832, 836)                           # the right leaf open a little: the dark inside
MID = (606, 609)                           # the window's sill and the doors' mid rail (its shadow on 610)
BOARDS = [(611, 616), (618, 623), (625, 630)]   # the wainscot's boards under the window
SILL, STEP = (634, 635), (636, 640)        # the sill; the sidewalk in the eave's shadow (the curb, 641-645, as painted)
SIG = 6.0                                  # the painter's light kept over this (his blotches: 3 to 5 px)
LIT, FACE, SHADE, DEEP, BACK, SLAT, PANEL = 1.32, 1.0, 0.84, 0.62, 0.70, 1.22, 0.95   # (reliefs, on his light)
POOL = 2.5                                 # the lantern's light on the wall: the painter's, smoothed over this
SPREAD = {0: 1.0, 1: 1.25, 2: 0.8, 3: 0.85, 4: 0.15}   # the share of it each kind takes: face, lit, shade, behind, gap
_LAST = {}                                 # (the lantern's comp as z9lan left it: the ground floor's light goes on it)


def _comp(name):
    return np.array(Image.open(os.path.join(EDITS, name + '_before.webp')).convert('RGBA')).astype(float)


def _fill(img, hole, sigma):
    """img's low frequencies with the pixels of `hole` left out (normalised convolution, widened until defined)."""
    w = (~hole).astype(float); s = sigma
    while True:
        num = np.stack([gaussian_filter(img[..., c] * w, s) for c in range(3)], -1); den = gaussian_filter(w, s)[..., None]
        if (den > 1e-3).all() or s > 64: return num / np.maximum(den, 1e-6)
        s *= 1.6


def _rank(order_key, colours):
    """colours laid on the pixels by the rank of order_key: per channel, the k-th smallest key takes the k-th smallest
    value (the painter's values, the drawing's structure)."""
    n = len(order_key); out = np.zeros((n, 3))
    q = (np.arange(n) + 0.5) / n
    rank = np.argsort(np.argsort(order_key, kind='stable'), kind='stable')
    for c in range(3):
        v = np.sort(colours[:, c]); out[:, c] = np.interp(q[rank], (np.arange(len(v)) + 0.5) / len(v), v)
    return out


def _put(new, unew, orig, unlit, box, pts, rgb):
    """street pixels (scene px) set; the power cut takes the same change as a ratio to its own pixel."""
    x0, y0 = box[0], box[1]
    for (x, y), c in zip(pts, rgb):
        new[y - y0, x - x0] = c
        unew[y - y0, x - x0] = np.clip(unlit[y - y0, x - x0] * (np.asarray(c) + 1.0) / (orig[y - y0, x - x0] + 1.0), 0, 255)


def lantern(box, orig, unlit, new, unew, m):
    x0, y0, x1, y1 = box
    cname, cx, cy = LANTERN_COMP; cb = _comp(cname); comp = cb.copy()
    at = lambda arr, x, y: arr[y - y0, x - x0]
    on = orig.copy()                           # (the painter's lit picture here: the street with his comp laid on it)
    for y in range(y0, y1):
        for x in range(x0, x1):
            a = cb[y - cy, x - cx, 3] / 255.0; on[y - y0, x - x0] = on[y - y0, x - x0] * (1 - a) + cb[y - cy, x - cx, :3] * a
    paper = [(x, y) for y, (a, b) in PAPER.items() for x in range(a, b + 1)]
    caps = [(x, y) for y, (a, b) in CAPS.items() for x in range(a, b + 1)]
    # the painter's: his lit paper (the bright pixels of his lantern), his lit caps, his off disc, the night's dark
    lit_paper = np.array([at(on, x, y) for y in range(580, 588) for x in range(800, 809) if at(on, x, y)[0] > 140])
    lit_cap = np.median([at(on, x, y) for x, y in [(802, 579), (803, 579), (804, 579), (805, 579), (802, 587), (803, 587),
                                                   (804, 587), (805, 587), (806, 587)]], 0)
    disc = [(x, y) for y in range(577, 590) for x in range(798, 810) if at(orig, x, y)[0] > at(orig, x, y)[1] + 12]
    off_disc = np.median([at(orig, x, y) for x, y in disc], 0)
    dark = (off_disc + 1.0) / (np.median(lit_paper, 0) + 1.0)       # (his darkening, channel by channel)
    night = np.median([at(orig, x, y) for x, y in HEAD], 0)
    # the barrel: its shading (across and along), the painter's lit colours by rank on it
    key = np.array([1 - ROUND[0] * ((x + 0.5 - AXIS[0]) / 3.5) ** 2 - ROUND[1] * ((y + 0.5 - AXIS[1]) / 3.5) ** 2
                    for x, y in paper])
    litp = _rank(key, lit_paper)
    offp = np.clip(litp * dark, 0, 255)
    # off: the street; what of the old disc is not the lantern any more, the wall from round it
    old = np.zeros(orig.shape[:2], bool)
    for x, y in disc: old[y - y0, x - x0] = True
    shape = np.zeros_like(old)
    for x, y in paper + caps + BRACKET: shape[y - y0, x - x0] = True
    wall = _fill(orig, old | shape, 1.2)
    rest = [(x, y) for x, y in disc if not shape[y - y0, x - x0]]
    _put(new, unew, orig, unlit, box, rest, [at(wall, x, y) for x, y in rest])
    _put(new, unew, orig, unlit, box, paper, offp)
    _put(new, unew, orig, unlit, box, caps + BRACKET, [night] * (len(caps) + len(BRACKET)))
    # lit: the comp. The paper and caps as drawn; the four corners of his lit paper outside the barrel now take his lit
    # wall from round them; the bracket dark against the lit wall (a little of the lantern's light under its arm)
    corners = [(801, 586), (807, 586), (801, 587), (807, 587)]
    hole = shape.copy()
    for x, y in corners: hole[y - y0, x - x0] = True
    lit_wall = _fill(on, hole, 1.0)
    def lay(x, y, c):
        comp[y - cy, x - cx, :3] = c; comp[y - cy, x - cx, 3] = 255
    for (x, y), c in zip(paper, litp): lay(x, y, c)
    for x, y in caps: lay(x, y, lit_cap)
    for x, y in BRACKET: lay(x, y, lit_cap * (0.85 if y >= 577 else 0.7))
    for x, y in corners: lay(x, y, at(lit_wall, x, y))
    print('z9lan: the painter\'s darkening', np.round(dark, 3).tolist(), 'paper lit', np.round(litp.mean(0)).tolist(),
          'off', np.round(offp.mean(0)).tolist(), 'caps off', np.round(night).tolist())
    _LAST['lantern'] = comp
    return comp


def window(box, orig, unlit, new, unew, m):
    x0, y0, x1, y1 = box; h, w = orig.shape[:2]
    cname, cx, cy = WINDOW_COMP; cb = _comp(cname); comp = cb.copy(); ch, cw = cb.shape[:2]
    X = np.arange(x0, x1)[None, :] + np.zeros((h, 1), int); Y = np.arange(y0, y1)[:, None] + np.zeros((1, w), int)
    on = orig.copy(); sl = (slice(cy - y0, cy - y0 + ch), slice(cx - x0, cx - x0 + cw))
    a = cb[..., 3:4] / 255.0; on[sl] = on[sl] * (1 - a) + cb[..., :3] * a
    # the awning in front of the railing's lower right corner (red), and a pixel of its blended edge: never touched
    red = (orig[..., 0] > orig[..., 2] + 10) & (orig[..., 0] > 40)
    awn = np.zeros_like(red)
    for r in range(h):
        xs = np.nonzero(red[r])[0]
        if len(xs): awn[r, max(xs[0] - 1, 0):] = True
    # the railing
    rail = np.zeros((h, w), bool); parts = {}
    def el(name, mk):
        mk = mk & ~awn; parts[name] = mk; return mk
    xa, xb = POSTS[0][0], POSTS[1][1]
    el('top', (Y == TOP_RAIL) & (X >= xa) & (X <= xb)); el('face', (Y == TOP_FACE) & (X >= xa) & (X <= xb))
    el('kick', (Y == KICK_RAIL) & (X >= xa) & (X <= xb))
    inb = (Y >= BAR_Y[0]) & (Y <= BAR_Y[1]) & (Y != KICK_RAIL)
    el('post', inb & np.isin(X, [c for p in POSTS for c in p[:2]]))
    el('pshade', inb & np.isin(X, [p[2] for p in POSTS if p[2]]))
    el('bar', inb & np.isin(X, BARS))
    for k in parts: rail |= parts[k]
    # each element the painter's colour for it (off): his rails' rows, his posts, his bars; what the sky lights (the top
    # rail, the posts, the bars) the brighter half of his strokes there, what faces down or away their median
    med = lambda mk: np.median(orig[mk & ~awn], 0)
    def lit_med(mk):
        px = orig[mk & ~awn]; l = lum(px); return np.median(px[l >= np.median(l)], 0)
    old_bars = inb & np.isin(X, OLD_BARS)
    ref = dict(top=lit_med(parts['top']), face=med(parts['face']), kick=med(parts['kick']), post=lit_med(parts['post']),
               pshade=med(parts['pshade']), bar=lit_med(old_bars))
    # the glass: the curtains, lit (the comp) and off (the street)
    glass = np.zeros((h, w), bool)
    for a_, b_ in PANES: glass |= (X >= a_) & (X <= b_)
    glass &= (Y >= GLASS_Y[0]) & (Y <= GLASS_Y[1]) & ~rail & ~awn
    gl_all = np.zeros((h, w), bool)
    for a_, b_ in PANES: gl_all |= (X >= a_) & (X <= b_)
    gl_all &= (Y >= GLASS_Y[0]) & (Y <= GLASS_Y[1])
    Lp = lum(on)
    left = gl_all & (X <= PANES[0][1])
    sx0, sy0, sx1, sy1 = SMUDGE
    smudge = (X >= sx0) & (X <= sx1) & (Y >= sy0) & (Y <= sy1)
    # the left curtain: the painter's (his folds, his light: the heading cool in the head's shadow, warm and bright low
    # down), its smudge filled down each column from the rows over and under it; its foot behind the railing (rows
    # 520-530: his bars, rails and a blob there) the same curtain run down from the row over the rail, at his light
    # there (row by row, his bright pixels against that row's)
    cur = Lp.copy()
    for x in range(sx0, sx1 + 1):
        a, b = Lp[sy0 - 1 - y0, x - x0], Lp[sy1 + 1 - y0, x - x0]
        for y in range(sy0, sy1 + 1):
            cur[y - y0, x - x0] = a + (b - a) * (y - sy0 + 1) / (sy1 - sy0 + 2)
    base = TOP_RAIL - 1; f = 1.0; prof = {}
    for y in range(TOP_FACE + 1, GLASS_Y[1] + 1):
        r = left[y - y0] & (Lp[y - y0] > 90)
        if r.sum() >= 3: f = float(np.clip(np.median(Lp[y - y0][r] / np.maximum(Lp[base - y0][r], 1.0)), 0.6, 1.15))
        cur[y - y0] = cur[base - y0] * f; prof[y] = round(f, 2)
    # the right curtain: the left one mirrored about the meeting stiles (a pair, gathered to the sides), a little dimmer
    mid = (PANES[0][1] + PANES[1][0]) // 2
    for x in range(PANES[1][0], PANES[1][1] + 1):
        cur[:, x - x0] = RIGHT_K * cur[:, 2 * mid - x - x0]
    # his lit palette (his colours by brightness: the median per band of 6 over his left curtain) for what is new; his
    # own pixels where his curtain is kept
    gp = left & (Y < TOP_RAIL) & ~smudge & (Lp > 30)
    bands = np.arange(36, 216, 6); tab = []
    for b in bands:
        s = gp & (np.abs(Lp - b) <= 6)
        tab.append(np.median(on[s], 0) if s.sum() >= 3 else None)
    ok = [i for i, t in enumerate(tab) if t is not None]; bands = bands[ok]; tab = np.array([tab[i] for i in ok])
    litc = np.stack([np.interp(cur, bands, tab[:, c]) for c in range(3)], -1)
    kept = left & (Y < TOP_RAIL) & ~smudge
    litc[kept] = on[kept]
    # off: his dark glass (his off picture smoothed over the glass, without his bars), with half the folds' relief
    offlf = _fill(orig, ~gl_all | old_bars | np.isin(Y, [TOP_RAIL, TOP_FACE, KICK_RAIL]), 5.0)
    rel = (lum(litc) + 1.0) / (lum(_fill(litc, ~gl_all, 3.0)) + 1.0)
    offc = np.clip(offlf * (1 + SHUT_K * (rel - 1))[..., None], 0, 255)
    pts = list(zip(X[glass], Y[glass]))
    _put(new, unew, orig, unlit, box, pts, offc[glass])
    for k in ('top', 'face', 'kick', 'post', 'pshade', 'bar'):
        pk = parts[k]; _put(new, unew, orig, unlit, box, list(zip(X[pk], Y[pk])), [ref[k]] * int(pk.sum()))
    # the comp: the curtains lit over the glass, clear over the railing
    csub = lambda mk: mk[sl]
    comp[..., :3][csub(glass)] = litc[sl][csub(glass)]; comp[..., 3][csub(glass)] = 255
    comp[..., 3][csub(rail)] = 0; comp[..., :3][csub(rail)] = 0
    print('z9win: railing', {k: np.round(v).astype(int).tolist() for k, v in ref.items()},
          'curtains lit', np.round(litc[glass].mean(0)).tolist(), 'off', np.round(offc[glass].mean(0)).tolist(), 'foot', prof)
    return comp


def _nconv(img, wgt, sig, axis=None):
    """img smoothed over the pixels of wgt only (normalised convolution): along one axis (a row or a column evened) or
    both (axis None)."""
    w = wgt.astype(float)
    f = (lambda a: gaussian_filter(a, sig)) if axis is None else (lambda a: gaussian_filter1d(a, sig, axis=axis))
    num = np.stack([f(img[..., c] * w) for c in range(3)], -1)
    return num / np.maximum(f(w), 1e-6)[..., None]


def _front():
    """The front drawn (x FRONT, rows ROWS): its relief on the painter's light, its parts (each keeps his light on average:
    1 the window, 2 its wainscot, 3 the jamb, 4 and 5 the leaves, 6 the gap) and each pixel's kind (0 a face, 1 lit, 2 in
    shade, 3 the dark behind a lattice, 4 the gap)."""
    X0, Y0 = FRONT[0], ROWS[0]; h, w = ROWS[1] - Y0 + 1, FRONT[1] - X0 + 1
    rel = np.ones((h, w)); part = np.zeros((h, w), int); kind = np.zeros((h, w), int)
    def r(xa, xb, ya, yb, v, k, p=None):
        s = (slice(ya - Y0, yb - Y0 + 1), slice(xa - X0, xb - X0 + 1)); rel[s] = v; kind[s] = k
        if p is not None: part[s] = p
    def rails(xa, xb):                         # the head rail in the lintel's shadow, the mid rail, the bottom rail
        r(xa, xb, 578, 578, SHADE, 2); r(xa, xb, 579, 580, FACE, 0)
        r(xa, xb, MID[0], MID[0], LIT, 1); r(xa, xb, MID[0] + 1, MID[1] - 1, FACE, 0); r(xa, xb, MID[1], MID[1], SHADE, 2)
        r(xa, xb, MID[1] + 1, MID[1] + 1, DEEP, 2)
        r(xa, xb, ROWS[1] - 2, ROWS[1] - 2, LIT, 1); r(xa, xb, ROWS[1] - 1, ROWS[1], FACE, 0)
    def lattice(xa, xb):                       # slats every 3 px over the dark behind, symmetric in the opening
        r(xa, xb, 581, MID[0] - 1, BACK, 3)
        for x in range(xa + 2, xb - 1, 3): r(x, x, 581, MID[0] - 1, SLAT, 1)
    a, b = WINDOW                              # the lattice window over its wainscot
    r(a, b, ROWS[0], MID[1], FACE, 0, 1); r(a, b, MID[1] + 1, ROWS[1], FACE, 0, 2)
    rails(a + 1, b); lattice(a + 3, b - 2)
    for ya, yb in BOARDS:
        r(a + 1, b, ya, ya, 1.08, 1); r(a + 1, b, yb, yb, 0.93, 0)
        if yb + 1 < ROWS[1] - 2: r(a + 1, b, yb + 1, yb + 1, DEEP, 2)
    r(a, a, ROWS[0], ROWS[1], LIT, 1)
    r(b - 1, b - 1, 579, MID[0] - 1, FACE, 0); r(b, b, 579, MID[0] - 1, SHADE, 2)
    a, b = JAMB
    r(a, b, ROWS[0], ROWS[1], FACE, 0, 3); r(a, a, ROWS[0], ROWS[1], LIT, 1); r(b, b, ROWS[0], ROWS[1], SHADE, 2)
    for p, (a, b) in enumerate(LEAVES, 4):     # the leaves: a lattice over a plain kick panel, their stiles lit on the left
        r(a, b, ROWS[0], ROWS[1], FACE, 0, p)
        rails(a + 2, b - 2); lattice(a + 2, b - 2); r(a + 2, b - 2, MID[1] + 2, ROWS[1] - 3, PANEL, 0)
        r(a, a, ROWS[0], ROWS[1], LIT, 1); r(a + 1, a + 1, 579, ROWS[1], FACE, 0)
        r(b - 1, b - 1, 579, ROWS[1], FACE, 0); r(b, b, 579, ROWS[1], SHADE, 2)
    r(GAP[0], GAP[1], ROWS[0], ROWS[1], 1.0, 4, 6)
    return rel, part, kind


def ground(box, orig, unlit, new, unew, m):
    import e33_banner as E33
    x0, y0, x1, y1 = box; h, w = orig.shape[:2]
    X = np.arange(x0, x1)[None, :] + np.zeros((h, 1), int); Y = np.arange(y0, y1)[:, None] + np.zeros((1, w), int)
    inb = lambda xa, xb, ya, yb: (X >= xa) & (X <= xb) & (Y >= ya) & (Y <= yb)
    # what stays as it is: the lantern (z9lan), the banner, its shadow and the plaque (tools/e33_banner.py), the meter box
    lantern = np.zeros((h, w), bool)
    for x, y in [(x, y) for y, (a, b) in list(PAPER.items()) + list(CAPS.items()) for x in range(a, b + 1)] + BRACKET:
        lantern[y - y0, x - x0] = True
    keep = lantern.copy(); shade = np.zeros((h, w), bool)
    for rows, (bx, by) in ((E33.BANNER, E33.ROD), (E33.PLQ, E33.PLAQUE)):
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                x, y = bx + i, by + j
                if x0 <= x < x1 and y0 <= y < y1 and ch in E33.PAL: keep[y - y0, x - x0] = True
                elif x0 <= x < x1 and y0 <= y < y1 and ch == 'z': shade[y - y0, x - x0] = True
    keep |= inb(*METER[0::2], *METER[1::2])
    out = orig.copy()
    def even(src, dst, sig, axis):
        sm = _nconv(out, src, sig, axis); out[dst] = sm[dst]
    # 1. the posts, each column evened down its parts (the left one's ledge along its rows)
    pl = inb(*POST_L, BAND[0], SILL[1]) & ~keep
    for part in (pl & (Y < LEDGE[0]), pl & (Y > LEDGE[1])): even(part, part, 4.0, 0)
    le = pl & (Y >= LEDGE[0]) & (Y <= LEDGE[1]); even(le, le, 3.0, 1)
    pr = inb(*POST_R, ROWS[0], SILL[1]) & ~keep; even(pr, pr, 4.0, 0)
    # 2. the boards under the balcony and the lintel, each row evened along itself; the banner's shadow on them again
    band = inb(FRONT[0], POST_R[1], *BAND) & ~keep & ~shade
    sh = shade & inb(FRONT[0], POST_R[1], *BAND)
    even(band, band | sh, SIG, 1); out[sh] *= E33.SHADE
    # 3. the front drawn on the painter's light (his low frequencies over it, the gap and the lantern aside), each part
    # keeping his light on average; the gap his dark inside
    rel, part, kind = _front()
    fr = inb(*FRONT, *ROWS)
    REL, PART, KIND = np.ones((h, w)), np.zeros((h, w), int), np.full((h, w), -1)
    s = (slice(ROWS[0] - y0, ROWS[1] - y0 + 1), slice(FRONT[0] - x0, FRONT[1] - x0 + 1))
    REL[s], PART[s], KIND[s] = rel, part, kind
    gap = fr & (KIND == 4)
    lf = _nconv(orig, fr & ~gap & ~lantern, SIG)
    for p in range(1, 6):
        pm = fr & (PART == p) & ~keep; REL[pm] /= REL[pm].mean()
    fm = fr & ~gap & ~keep
    out[fm] = np.clip(lf * REL[..., None], 0, 255)[fm]
    out[gap & ~keep] = np.median(orig[gap], 0)
    # 4. the sill (its lit top, its face) and the sidewalk in the eave's shadow, evened along its rows
    sr = inb(FRONT[0], POST_R[1], *SILL)
    sm = _nconv(orig, sr, 10.0, 1); smean = (sm[SILL[0] - y0] + sm[SILL[1] - y0]) / 2
    for y, k in ((SILL[0], 1.16), (SILL[1], 0.84)):
        rr = sr[y - y0] & ~keep[y - y0]; out[y - y0][rr] = np.clip(smean[rr] * k, 0, 255)
    st = inb(POST_L[0], POST_R[1], *STEP); even(st, st, SIG, 1)
    ch = m & ~keep & (np.abs(out - orig).max(-1) > 0)
    # the power cut: the same picture times the painter's darkening there (smoothed, channel by channel)
    dark = np.stack([(gaussian_filter(unlit[..., c], 4.0) + 1.0) / (gaussian_filter(orig[..., c], 4.0) + 1.0) for c in range(3)], -1)
    new[ch] = out[ch]; unew[ch] = np.clip(out * np.clip(dark, 0, 1.5), 0, 255)[ch]
    # 5. lit: the lantern's light (its comp as z9lan left it), the painter's streaks made a soft pool on the new front
    comp = _LAST.get('lantern')
    if comp is None: comp = _comp(LANTERN_COMP[0])
    _, cx, cy = LANTERN_COMP; ch_, cw_ = comp.shape[:2]
    r0, r1 = y0 - cy, min(y1 - cy, ch_)        # (the comp's rows in the box; its columns all in it)
    bs = (slice(0, r1 - r0), slice(cx - x0, cx - x0 + cw_)); cs = (slice(r0, r1), slice(0, cw_))
    on = orig.copy(); a = comp[cs][..., 3:4] / 255.0; on[bs] = on[bs] * (1 - a) + comp[cs][..., :3] * a
    hole = lantern | keep
    gain = (_fill(on, hole, POOL) + 1.0) / (_fill(orig, hole, POOL) + 1.0) - 1.0
    take = np.ones((h, w))
    for k, v in SPREAD.items(): take[KIND == k] = v
    off = new.copy(); total = (lum(on) - lum(orig))[~hole].sum(); g = 1.0
    for _ in range(3):                         # (its light in total the painter's)
        litc = np.clip(off * (1 + g * (gain * take[..., None])), 0, 255)
        g *= total / max((lum(litc) - lum(off))[~hole].sum(), 1e-6)
    litc = np.clip(off * (1 + g * (gain * take[..., None])), 0, 255)
    pool = (np.abs(litc - off).max(-1) >= 0.5) & ~keep
    cb = comp[cs]; lb, pb, kb = litc[bs], pool[bs], keep[bs]
    cb[..., 3][~kb] = 0; cb[..., :3][~kb] = off[bs][~kb]
    cb[..., :3][pb] = lb[pb]; cb[..., 3][pb] = 255
    comp[cs] = cb
    print('z9base: the front drawn,', int(ch.sum()), 'px; the gap', np.round(np.median(orig[gap], 0)).tolist(),
          '; the lantern\'s pool', int(pb.sum()), 'px, its light the painter\'s in total (x %.3f)' % g)
    return comp
