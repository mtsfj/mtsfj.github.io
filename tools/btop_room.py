#!/usr/bin/env python3
"""The balcony door of the top storey of the narrow plastered building left of the pole (B; tools/window_depth.py's
B_TOP, the comp win_z1_top), lived in: its room was switched fully on or off now and then, at any hour, one picture.

    (a module: tools/redraw_zones.py's zone 'btop', after winB, calls draw() on the street as the zones before it leave
    it: the layers stay as they are; it adds the room's late picture to the comp winB gives back, assets/win_z1_top.webp)
    python3 tools/btop_room.py --before         once: the zone's before crops (tools/src/edits/btop_before_*.webp)
    python3 tools/btop_room.py --preview DIR    the door off, lit by the ceiling lamp, late, over the layer as it is, x1, x6

Another household than the one in the top window right of the pole (tools/ctop_room.py, win_c_top), lit the same way
(R30, PLAYBOOK §5: one painting, several states): the evening under the ceiling lamp, as the door was painted (window_depth's
room behind it, the sheer drawn across the left pane, the ceiling and its lamp seen through the right one); late, the
ceiling lamp off and a desk lamp left on low in the room, behind the sheer, on the left. No new drawing: the late picture
is the painted room relit in code. The ceiling lamp's light on the glass (the painted light, the lit picture minus the
off one: its luminance, blurred over each pane by SIG px) is taken out and the desk lamp's put in its place (LAMP: its
light on the sheer and the far wall rising from the bottom of the glass, brightest above the lamp, falling off up the
glass and across it; a faint ring on the ceiling over its shade; a little of the room's bounce everywhere), the painted
detail kept as it is (the sheer's folds, the ceiling lamp's own disc, now unlit, a ghost on the dark ceiling). The night's
reflection on the glass the painting's own (the more of it the darker the room behind: each pixel between the off and the
lit picture), the light out of the pink into the street's homes' warm ramp (window_depth.warm: the dimmer, the oranger),
a level of grain, then its own tones (a median cut of its glass, NPAL): crisp, a tone a pixel. Round the glass (the left
reveal, the frame, the railing's bars against the room, the slab's lit edge) the room's light as much as the glass has
next to it. Off (its layers, the power cut) the door stays exactly as painted; the frame, the glass, the railing, the
balcony and B's plaster untouched.

street.js: a 'home' (COMP_KIND) with its own spells and its own bedtime (its rank on NIGHT.home: between about 1:20 and
2:40), its sheet two frames side by side, BTOP choosing one with cTopStep (the same switch as win_c_top's): the desk lamp
from its own moment each night (21:45 to 23:00) till bedtime, swapped at once as a switch does; back to the ceiling lamp
only while the door is dark. The power cut and the red night as every comp; the poster (14 h, the painted evening) shows
the ceiling lamp, as before. Its light does not reach the wet sidewalk in any measurable way: no ground light. Needs
Pillow, numpy, scipy.
"""
import os
import sys
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDITS = os.path.join(ROOT, 'tools', 'src', 'edits')
ASSETS = os.path.join(ROOT, 'assets')
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from ctop_room import load, lum, save, hashf, comp_of   # (the same helpers as the window right of the pole)

COMP = 'win_z1_top'
ZONE = 'btop'
SRC_ZONE = 'winB'                              # (the zone whose comp this is: tools/window_depth.py, b_windows)
BOX = (963, 222, 1006, 363)                    # the comp's frame (window_depth.B_COMP) and the zone
SIG = 4.0                                      # (the ceiling lamp's light: the painted light's luminance blurred so, px)
# the desk lamp's light on what the glass shows, across the door (ux: 0 its left jamb, 1 its right) and up it (wv: 0 the
# sill, 1 the head): its pool over the lamp (at u, falling off across by su and up by sw, its power p), the ring on the
# ceiling over its shade (ring, its widths ru, rw), the room's bounce (base); PEAK its light at the most (luminance added to
# the glass off: behind the railing, where the ceiling lamp added 35, above it 105)
LAMP = dict(u=0.24, su=0.52, sw=0.40, p=1.25, ring=0.08, ru=0.20, rw=0.18, base=0.07)
PEAK = 95.0
SMAX = (3.0, 1.5)                              # (the late light at most these times the ceiling lamp's: the glass, round it)
NPAL = 20                                      # (its tones: a median cut of its glass)


def geometry():
    """Over BOX: the share of each pixel's rays on the door's glass (window_depth's model of B: the panes, the railing's
    bars before them left out), and each pixel's place on the door (ux across, wv up: along the head's and the sill's
    rays from the vanishing point)."""
    import window_depth as WD
    S, G, ops = WD.model('B')
    dx, dy = WD.rays(BOX)
    idx, t, face = S.cast(dx, dy)
    names = np.array(S.name + ['none'], dtype=object)[idx]
    gl = np.isin(names, ['glassT0', 'glassT1']).mean(2)
    x0, y0, x1, y1 = BOX
    Y, X = np.mgrid[y0:y1, x0:x1] + 0.5
    o = WD.B_TOP
    ux = (X - o['xl']) / (o['xr'] - o['xl'])
    wv = ((WD.VPY - Y) / (X - WD.VPX) - o['vb']) / (o['vt'] - o['vb'])
    return gl, ux, wv


def blur(a, w, s):
    """a blurred over the pixels of weight w (a normalised convolution), and the weight there."""
    from scipy.ndimage import gaussian_filter
    n = gaussian_filter(a * w, s, mode='nearest'); d = gaussian_filter(w, s, mode='nearest')
    return n / np.maximum(d, 1e-6), d


def lamp(ux, wv):
    """The desk lamp's light (relative) at each place on the door."""
    L = LAMP
    pool = np.exp(-((ux - L['u']) / L['su']) ** 2) * np.exp(-(np.clip(wv, 0, None) / L['sw']) ** L['p'])
    ring = np.exp(-((ux - L['u']) / L['ru']) ** 2 - ((1 - wv) / L['rw']) ** 2)
    return L['base'] + (1 - L['base']) * pool + L['ring'] * ring


def build(off, lit):
    """The door's late picture over BOX (floats), from the painting off and lit by its ceiling lamp; the glass."""
    import window_depth as WD
    x0, y0, x1, y1 = BOX
    gl, ux, wv = geometry()
    diff = np.abs(np.round(lit) - np.round(off)).max(-1) > 0
    m = (gl > 0.5) & diff                                                  # (the glass the room lights)
    Ld = np.clip(lum(lit - off), 0, None)
    ceil, _ = blur(Ld, m.astype(float), SIG)                               # the ceiling lamp's light on the glass
    s = np.clip(PEAK * lamp(ux, wv) / np.maximum(ceil, 1.0), 0, SMAX[0])   # (the late light over the ceiling lamp's)
    # round the glass: as much of it as the glass has next to it (its rows' own beyond: the slab's edge under it)
    se, w = blur(s, m.astype(float), 3.0)
    rows = np.array([s[r][m[r]].mean() if m[r].any() else np.nan for r in range(y1 - y0)])
    ok = ~np.isnan(rows); rows = np.interp(np.arange(len(rows)), np.nonzero(ok)[0], rows[ok])
    se = np.where(w > 0.08, se, rows[:, None])
    k = np.where(m, s, np.clip(se, 0, SMAX[1]))[..., None]
    late = off + k * (lit - off)                                           # (between the room off and lit: the night's
    late = WD.warm('B', off, late)                                         #  reflection the more, the darker the room)
    Y, X = np.mgrid[y0:y1, x0:x1]
    g = late + (hashf(X, Y, 11)[..., None] - 0.5) * 3.0                    # (a level or so of grain before the tones)
    pal = WD.palette(g[m], NPAL)
    g = WD.snap(np.clip(g, 0, 255), pal)
    late[m] = g[m]
    late[~diff] = off[~diff]                                               # (what the room does not light: as painted)
    return late, m


def draw(city, unlit, box=BOX):
    """Zone 'btop': the layers as they are; the comp winB hands to redraw_zones (COMP_OUT: the ceiling lamp's picture)
    given its late frame beside it (a sheet of two). Returns what changed (nothing)."""
    rz = sys.modules.get('__main__')
    x0, y0, x1, y1 = BOX
    if hasattr(rz, 'COMP_OUT') and SRC_ZONE in rz.COMP_OUT:
        c = rz.COMP_OUT[SRC_ZONE][1]
        off = city[y0:y1, x0:x1, :3].copy()
        a = c[..., 3:] / 255.0
        lit = off * (1 - a) + c[..., :3] * a
        late, _ = build(off, lit)
        rz.COMP_OUT[SRC_ZONE][1] = np.concatenate([c[:, :x1 - x0], comp_of(off, late)], 1)
    return np.zeros((box[3] - box[1], box[2] - box[0]), bool)


def before():
    """The zone's before crops: the layers' pixels in its box before the zones run (the overlapping zones' own before
    crops, in their order, over the layers' pixels where no zone is)."""
    import redraw_zones as R
    x0, y0, x1, y1 = BOX
    for tag, f in (('city', 'layer_city_off.webp'), ('unlit', 'street_unlit.webp')):
        a = load(os.path.join(ASSETS, f))[y0:y1, x0:x1].copy()
        for name, cfg in R.ZONES.items():
            if name == ZONE: continue
            b = cfg['box']
            ox0, oy0, ox1, oy1 = max(b[0], x0), max(b[1], y0), min(b[2], x1), min(b[3], y1)
            if ox0 >= ox1 or oy0 >= oy1: continue
            z = load(os.path.join(EDITS, '%s_before_%s.webp' % (name, tag)))
            a[oy0 - y0:oy1 - y0, ox0 - x0:ox1 - x0] = z[oy0 - b[1]:oy1 - b[1], ox0 - b[0]:ox1 - b[0]]
        save(a, os.path.join(EDITS, '%s_before_%s.webp' % (ZONE, tag)))
        print('%s_before_%s.webp' % (ZONE, tag), a.shape[1], 'x', a.shape[0])


def preview(out):
    """The door off, lit by its ceiling lamp, late, over the layer as it is (its comp's first frame), x1 and x6."""
    os.makedirs(out, exist_ok=True)
    x0, y0, x1, y1 = BOX
    off = load(os.path.join(ASSETS, 'layer_city_off.webp'))[y0:y1, x0:x1, :3]
    c = load(os.path.join(ASSETS, COMP + '.webp'))[:, :x1 - x0]
    a = c[..., 3:] / 255.0
    lit = off * (1 - a) + c[..., :3] * a
    late, _ = build(off, lit)
    for tag, im in (('off', off), ('ceiling', lit), ('late', late)):
        for k in (1, 6):
            Image.fromarray(np.clip(np.round(im), 0, 255).astype(np.uint8)).resize((im.shape[1] * k, im.shape[0] * k), Image.NEAREST).save(os.path.join(out, '%s_x%d.png' % (tag, k)))


if __name__ == '__main__':
    if '--before' in sys.argv: before()
    elif '--preview' in sys.argv: preview(sys.argv[sys.argv.index('--preview') + 1])
    else: print(__doc__)
