#!/usr/bin/env python3
"""The big tree on the left, in front of the house and the dojo (B+C), replaced.

    python3 tools/tree_bc.py      (after tools/tree_a.py; it takes its zone, x < 326, back from commit aa383bc each time)

The old tree's crown hung over the house's front and its lit side wall, its bush over the dojo's shoji. The new one
(tools/src/tree_bc.jpg, a pixel-art tree drawn on white) stands just off the frame on the left: its trunk is out of
the picture, its crown comes in over the house as the old one did, a second copy of the drawing behind it in shade fills
under it (its own leaves, no sky, no old leaves); its bush is in the bottom left corner, two copies of the drawing's bush,
the lower one cut by the frame's bottom (its foot out of the picture), the upper one behind it.
What showed through the old leaves and is now in the open is rebuilt from the painting itself: the lit side wall along
its planks' lines (they run to the street's vanishing point, about (669, 568)), the shoji and the stone pillar from their
own cells above (the shoji's rails 42 px apart), the pavement from its own row further right. In layer_city_off,
street_unlit, street_sun and night_far, each from the same source pixel. Colours: the old tree's own, by lightness (so
every hour grades it as it graded the old one), its power-cut change by place. Needs git, Pillow, numpy and scipy.
"""
import io
import os
import subprocess
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = lambda p: os.path.join(ROOT, 'assets', p)
BEFORE = 'aa383bc'
SRC = os.path.join(ROOT, 'tools', 'src', 'tree_bc.jpg')
X_MAX = 326                                        # its zone: left of the drinks shop's tree (tools/tree_a.py)
GRID = 2.37                                        # the source's pixel (in its pixels)
CROWN = (1.55, -95, 25)                            # the crown: scene pixels per source pixel, its left, its top (y)
CROWN_ROWS = 700                                   # (the source's rows above this: the crown; below, the bare trunk and the bush)
DEEP = (0, 50, 0.62)                                # its leaves further in: the crown again, moved (x, y), in shade
BUSH_ROWS = 860                                    # (the source's rows below this: the bush at the trunk's foot, its wood left out)
BUSHES = []                                        # (no bush: the pavement as clean as everywhere else)
SHOJI_STEP, SILL = 42, 6                           # the shoji's rails, one under the other; their sill's height
BASE = lambda x: 733 + 0.29 * (126 - x)            # the front's foot on the pavement (to the vanishing point, as the pavement's lines)
FASCIA = lambda x: 455 + 0.23 * x                   # the dojo's top board, its upper edge (lit, under the crown)
VP = (669.0, 568.0)                                # the street's vanishing point (the side wall's planks run to it)
OLD_CROWN = [(0, 70), (60, 72), (92, 98), (132, 108), (172, 148), (208, 198), (236, 248), (238, 312), (220, 362),
             (208, 410), (178, 440), (132, 462), (60, 472), (0, 472)]
OLD_BUSH = [(0, 586), (30, 590), (56, 614), (72, 660), (84, 704), (112, 738), (124, 800), (124, 816), (0, 816)]
OUT = os.environ.get('OUT')


def load(p, mode='RGBA', at=None):
    data = subprocess.run(['git', 'show', f'{at}:assets/{p}'], cwd=ROOT, capture_output=True, check=True).stdout if at else open(A(p), 'rb').read()
    return np.asarray(Image.open(io.BytesIO(data)).convert(mode)).astype(float)


def save(arr, p, mode):
    path = os.path.join(OUT, p) if OUT else A(p)
    Image.fromarray(np.clip(np.round(arr), 0, 255).astype(np.uint8), mode).save(path, 'WEBP', lossless=True, quality=100, method=6, exact=True)


def poly(pts, H, W):
    im = Image.new('L', (W, H), 0); ImageDraw.Draw(im).polygon(pts, fill=255); return np.asarray(im) > 0


def drawing():
    src = Image.open(SRC).convert('RGB'); a = np.asarray(src).astype(float)
    fg = a @ [0.299, 0.587, 0.114] < 150                                     # (the white ground and its light halo out)
    fg = ndi.binary_opening(fg, structure=np.ones((2, 2)))
    lab, n = ndi.label(fg); fg = np.isin(lab, 1 + np.where(ndi.sum(fg, lab, range(1, n + 1)) > 40)[0])
    # the ground and the gaps painted with the nearest leaf's colour: no white bleeding into the leaves round them when scaled
    _, (iy, ix) = ndi.distance_transform_edt(~fg, return_indices=True)
    src = Image.fromarray(a[iy, ix].astype(np.uint8))
    return src, fg


def part(src, fg, rows, scale, mirror=False, leaves_only=False):
    """A part of the drawing (rows: slice) at a scale: (rgb, alpha); leaves_only: without the trunk's brown wood."""
    s = scale / GRID; im = src.crop((0, rows.start, src.width, rows.stop)); m = fg[rows].copy()
    if leaves_only:
        q = np.asarray(im).astype(float); m &= ~(q[..., 0] >= q[..., 2] - 4)     # (the bark: brown or grey, not the leaves' teal)
        lab, n = ndi.label(m); m = lab == 1 + np.argmax(ndi.sum(m, lab, range(1, n + 1)))
    ys, xs = np.where(m); im = im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)); m = m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    w, h = round(im.width * s), round(im.height * s)
    rgb = np.asarray(im.resize((w, h), Image.LANCZOS)).astype(float)
    al = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).resize((w, h), Image.BOX)) > 127
    lab, n = ndi.label(al); al = np.isin(lab, 1 + np.where(ndi.sum(al, lab, range(1, n + 1)) > 12)[0])
    return (rgb[:, ::-1], al[:, ::-1]) if mirror else (rgb, al)


def put(mask, col, rgb, al, x0, y0):
    H, W = mask.shape; h, w = al.shape
    ys, xs = slice(max(0, y0), min(H, y0 + h)), slice(max(0, x0), min(W, x0 + w))
    sub = al[ys.start - y0:ys.stop - y0, xs.start - x0:xs.stop - x0]
    mask[ys, xs] |= sub; col[ys, xs][sub] = rgb[ys.start - y0:ys.stop - y0, xs.start - x0:xs.stop - x0][sub]


def recolour(rgb, al, ref):
    """The drawing's pixels in the reference pixels' colours, by lightness (rank for rank)."""
    out = rgb.copy(); Ls = rgb @ [0.299, 0.587, 0.114]; RL = ref @ [0.299, 0.587, 0.114]
    qs = np.linspace(0, 100, 101); L2 = np.interp(Ls[al], np.percentile(Ls[al], qs), np.percentile(RL, qs))
    bins = np.linspace(RL.min(), RL.max(), 24); idx = np.digitize(RL, bins); cent, cols = [], []
    for k in range(1, len(bins) + 1):
        m = idx == k
        if m.sum() >= 8: cent.append(RL[m].mean()); cols.append(ref[m].mean(0))
    cent, cols = np.array(cent), np.array(cols)
    out[al] = np.stack([np.interp(L2, cent, cols[:, ch]) for ch in range(3)], -1)
    return out


def main():
    cur = [load('layer_city_off.webp'), load('street_unlit.webp'), load('night_far.webp', 'RGB'), load('street_sun.webp', 'RGB')]
    old = [load('layer_city_off.webp', at=BEFORE), load('street_unlit.webp', at=BEFORE), load('night_far.webp', 'RGB', at=BEFORE),
           load('street_sun.webp', 'RGB', at=BEFORE)]
    for c, o in zip(cur, old): c[:, :X_MAX] = o[:, :X_MAX]                   # (its zone as painted, every time)
    city, unlit, nf, sun = cur
    H, W = city.shape[:2]; yy, xx = np.mgrid[0:H, 0:W]
    zone = xx < X_MAX

    # the old tree: its crown over the house, its leaves on the lit side wall (holes in the low sun's light there), its bush
    # over the shoji (holes in their light)
    lit = sun[:, :, 0] > 0
    wall = ndi.binary_fill_holes(ndi.binary_closing(lit, structure=np.ones((5, 5)), iterations=3)) & zone
    window = (xx >= 243) & (xx <= 278) & (yy >= 248) & (yy <= 362)
    Lc0 = city[:, :, :3] @ [0.299, 0.587, 0.114]
    on_wall = wall & ~window & (yy < 440) & (~lit | (Lc0 < 24))                # (a leaf: out of the sun, or dark as no plank is)
    on_wall |= ndi.binary_dilation(on_wall) & wall & ~window & (Lc0 < 34)      # (and its soft edge)
    crown_old = (poly(OLD_CROWN, H, W) | on_wall) & zone
    # (and its dark lower leaves, hanging over the shop's upper wall in the shade, right of that outline)
    Lc = city[:, :, :3] @ [0.299, 0.587, 0.114]
    dark = (Lc < 20) & (xx >= 90) & (xx < 235) & (yy >= 360) & (yy < 472) & ~lit
    lab, n = ndi.label(dark | crown_old); touch = np.unique(lab[crown_old]); crown_old |= dark & np.isin(lab, touch[touch > 0])
    lab, n = ndi.label(crown_old & ~poly(OLD_CROWN, H, W))
    for i, sl in enumerate(ndi.find_objects(lab)):                            # (not the downpipe: long and thin)
        m = lab[sl] == i + 1
        if sl[0].stop - sl[0].start > 40 and sl[1].stop - sl[1].start <= 6: crown_old[sl][m] = False
    glow = (city[:, :, :3] - unlit[:, :, :3]).max(-1) > 12
    shoji = glow & (xx < 120) & (yy > 520) & (yy < 800)
    panes = ndi.binary_fill_holes(ndi.binary_closing(shoji, structure=np.ones((5, 5)), iterations=3))
    bush_old = (poly(OLD_BUSH, H, W) | (panes & ~shoji & (xx < 110) & (yy > 590))) & zone

    # the new tree
    src, fg = drawing()
    rc = poly(OLD_CROWN, H, W) & (city[:, :, :3] @ [0.299, 0.587, 0.114] < 40) & (city[:, :, 3] > 200) & (city[:, :, 2] >= city[:, :, 0])
    ref_c = city[rc][:, :3]                                                   # (its leaves in the shade: not those lit pink on the wall)
    ref_b = city[poly(OLD_BUSH, H, W) & ~shoji & (city[:, :, 3] > 200)][:, :3]
    sc, cx, cy = CROWN
    rgb, al = part(src, fg, slice(0, CROWN_ROWS), sc); rgb = recolour(rgb, al, ref_c)
    cm = np.zeros((H, W), bool); cc = np.zeros((H, W, 3)); put(cm, cc, rgb, al, cx, cy)
    dm = np.zeros((H, W), bool); dc = np.zeros((H, W, 3)); put(dm, dc, rgb * DEEP[2], al, cx + DEEP[0], cy + DEEP[1])
    bm = np.zeros((H, W), bool); bc = np.zeros((H, W, 3))
    for s_, bx, by, mir in BUSHES:
        r_, a_ = part(src, fg, slice(BUSH_ROWS, src.height), s_, mir, leaves_only=True); r_ = recolour(r_, a_, ref_b)
        m_ = np.zeros((H, W), bool); c_ = np.zeros((H, W, 3)); put(m_, c_, r_, a_, bx, H - a_.shape[0] + by)
        bm |= m_; bc[m_] = c_[m_]                                             # (the later one in front)
    keep = (yy >= 476) & (yy < 560) & (xx < 240)                             # (the dojo's and the shop's signs: in front)
    cm &= zone & ~keep; bm &= zone
    low = np.where(cm.any(0), H - 1 - np.argmax(cm[::-1], 0), 0)            # (the crown's lowest leaf, column by column)
    dm &= zone & ~keep & ~cm & (yy <= np.maximum(low[None, :], 0))          # (behind it: never lower than the crown itself)

    # the old crown's leaves left in the shade, not under the new crown: its own leaves further in (the drawing again, in
    # shade, at several places), in the old leaves' outline
    low = np.where(cm.any(0), H - 1 - np.argmax(cm[::-1], 0), 0)
    fill = crown_old & ~wall & ~cm & ~dm & ~keep & (xx >= 4) & ((yy <= low[None, :]) | ((Lc < 20) & ~((xx < 130) & (yy > FASCIA(xx) - 6))))
    tex_m = np.zeros((H, W), bool); tex = np.zeros((H, W, 3))
    for ox, oy in ((DEEP[0], DEEP[1]), (60, 70), (-40, 90), (110, 40), (20, 130)):
        m_ = np.zeros((H, W), bool); c_ = np.zeros((H, W, 3)); put(m_, c_, rgb * DEEP[2], al, cx + ox, cy + oy)
        new_ = m_ & ~tex_m; tex[new_] = c_[new_]; tex_m |= new_
    fm = fill & tex_m; fc = tex
    dark_rgb = np.median(ref_c[ref_c @ [0.299, 0.587, 0.114] < np.percentile(ref_c @ [0.299, 0.587, 0.114], 10)], 0)
    fc[fill & ~tex_m] = dark_rgb * DEEP[2] / 0.62; fm = fill

    # what shows again: rebuilt from the painting
    out = [L.copy() for L in cur]
    def copy(dst, sy, sx):
        for L, O in zip(out, cur): L[dst] = O[sy, sx]
    # the lit side wall: along its planks, toward the vanishing point, from the nearest pixel of it with no leaf
    need = crown_old & wall & on_wall & ~cm & ~dm
    clean = wall & lit & ~crown_old & (Lc0 >= 24)
    ys, xs = np.where(need)
    for y, x in zip(ys, xs):
        dx, dy = VP[0] - x, VP[1] - y; n_ = np.hypot(dx, dy); dx, dy = dx / n_, dy / n_
        for t in range(1, 200):
            sx, sy = int(round(x + dx * t)), int(round(y + dy * t))
            if sx >= X_MAX or sy >= H: break
            if clean[sy, sx]:
                for L, O in zip(out, cur): L[y, x] = O[sy, sx]
                break
    # the shoji, down to their sill, from their cell above (the same column, one, two or three rails up); their sill, the
    # same wood as their head rail; the stone pillar, the dark gap and the door's frame right of them, from their own
    # column above; the pavement under the front's foot, along its own lines (to the vanishing point) from its clean part
    base = np.round(BASE(xx)).astype(int)
    need_b = bush_old & (yy < base - SILL) & (xx < 80)
    for y, x in zip(*np.where(need_b)):
        for k in range(1, 6):
            sy = y - SHOJI_STEP * k
            if sy < 540: break
            if not bush_old[sy, x]:
                for L, O in zip(out, cur): L[y, x] = O[sy, x]
                break
    sill = bush_old & (yy >= base - SILL) & (yy < base) & (xx < 80)
    rail = (yy >= 599) & (yy <= 601) & (xx >= 4) & (xx < 74) & ~bush_old       # (the shoji's own rail: their wood)
    wood = [np.median(O[rail], 0) for O in cur]
    rng = np.random.default_rng(3); tone = rng.normal(1, 0.06, (H, W))
    for y, x in zip(*np.where(sill)):
        k = tone[y, x] * (1.12 if y == base[y, x] - SILL else 1.0)          # (its top edge a little lighter)
        for L, wv in zip(out, wood): L[y, x] = wv * (k if wv.shape[0] < 4 else np.r_[[k] * 3, [1]][:wv.shape[0]])
    side = bush_old & (yy < base) & (xx >= 80)
    for y, x in zip(*np.where(side)):
        col = np.where(~bush_old[:y, x])[0]
        if len(col):
            for L, O in zip(out, cur): L[y, x] = O[col[-1], x]
    need_b |= sill | side
    # the dojo's top board under the crown (its lit edges between the old leaves): along its own lines, from its visible bits
    band = crown_old & (xx < 130) & (yy > FASCIA(xx) - 6) & (yy < 476) & ~cm & ~dm & ~fill
    seen = band & (Lc >= 20)
    need_f = band & ~seen
    for y, x in zip(*np.where(need_f)):
        for t in range(1, 60):
            for sgn in (1, -1):
                sx, sy = x + sgn * t, int(round(y + sgn * t * 0.23))
                if 0 <= sx < 130 and seen[sy, sx]:
                    for L, O in zip(out, cur): L[y, x] = O[sy, sx]
                    break
            else: continue
            break

    need_g = bush_old & (yy >= base)
    paved = ((yy >= 748) | ((yy >= 736) & (xx >= 140))) & ~bush_old & (xx >= 133) & (xx < X_MAX)   # (not the door's white stile, x 125..132)
    for y, x in zip(*np.where(need_g)):
        dx, dy = VP[0] - x, VP[1] - y; n_ = np.hypot(dx, dy); dx, dy = dx / n_, dy / n_
        hit = None
        for t in range(1, 400):                                               # (along its line: the clean pavement as far beyond
            sx, sy = int(round(x + dx * t)), int(round(y + dy * t))           # its edge as the pixel is before it, mirrored: its
            if sx >= X_MAX or sy < 736: break                                 # texture, and no seam)
            if paved[sy, sx]:
                hit = (sy, sx)
                sx2, sy2 = int(round(x + dx * 2 * t)), int(round(y + dy * 2 * t))
                if sx2 < X_MAX and paved[sy2, sx2]: hit = (sy2, sx2)
                break
        if hit is None:                                                       # (near the front's foot: its own row, mirrored)
            sx = 2 * 133 - x
            if sx < X_MAX and paved[y, sx]: hit = (y, sx)
            else:
                sx = np.argmax(paved[y, x:]) + x
                if paved[y, sx]: hit = (y, sx)
        if hit:
            for L, O in zip(out, cur): L[y, x] = O[hit]
    city, unlit, nf, sun = out

    # the power cut: the old tree's own change there, by place
    old_all = crown_old | bush_old
    wt = ndi.gaussian_filter(old_all.astype(float), 6)
    ratio = np.stack([ndi.gaussian_filter(np.where(old_all, (cur[1][:, :, ch] + 1) / (cur[0][:, :, ch] + 1), 0), 6) for ch in range(3)], -1) / np.maximum(wt, 1e-6)[..., None]
    ratio = np.where(wt[..., None] > 0.02, np.clip(ratio, 0.3, 1.0), 1.0)
    for m, c in ((fm, fc), (dm, dc), (cm, cc), (bm, bc)):
        city[m, :3] = c[m]; city[m, 3] = 255
        unlit[m, :3] = c[m] * ratio[m]; unlit[m, 3] = 255
        nf[m] = 0; sun[m] = 0
    # (the old crown's last pixels at the frame's edge, out of the drawing: the leaves next to them)
    left = crown_old & ~cm & ~dm & ~wall & (xx < 4)
    for y, x in zip(*np.where(left)):
        for sx in range(x + 1, 12):
            if cm[y, sx] or dm[y, sx]:
                for L in out: L[y, x] = L[y, sx]
                break
    left = old_all & ~cm & ~dm & ~bm & ~fm & ~(need | need_b | need_g | need_f | seen) & ~(xx < 4) & ~(wall & lit)
    if os.environ.get('LEFT'): np.save(os.environ['LEFT'], left)
    save(city, 'layer_city_off.webp', 'RGBA'); save(unlit, 'street_unlit.webp', 'RGBA')
    save(nf, 'night_far.webp', 'RGB'); save(sun, 'street_sun.webp', 'RGB')
    print('crown', int(cm.sum()), '| behind it', int(dm.sum()), '| bush', int(bm.sum()), '| wall rebuilt', int(need.sum()),
          '| shoji rebuilt', int(need_b.sum()), '| pavement', int(need_g.sum()), '| old pixels left as they were', int(left.sum()))


if __name__ == '__main__':
    main()
