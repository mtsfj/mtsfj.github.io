#!/usr/bin/env python3
"""The house at the street's end (zone 9, x 762-870): its paper lantern by the door and its upstairs lit window, drawn on
the pixel grid (the owner's picks, 2026-11-13). Two zones of tools/redraw_zones.py (z9lan, z9win: method 'hand') call
this module; run that tool, then tools/bake_retouches.py. Same input, same bytes.

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
"""
import os
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

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
