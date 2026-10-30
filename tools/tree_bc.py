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
SHOJI_X1 = 78                                      # the shoji's right side; their rails (they close in toward the street), the
RAILS = (lambda x: 554.6 + 0.085 * x, lambda x: 599.4 + 0.017 * x,         # last line their paper's foot
         lambda x: 644.3 - 0.047 * x, lambda x: 681.5 + 0.03 * x)
KERB_Y = lambda x: 816 - 0.38 * (x - 230)          # the pavement's kerb, its upper edge (below it the kerb stone)
VPG = (646.0, 634.0)                               # the ground's vanishing point (the pavement's long joints run to it; its
                                                   # cross joints are level)
STEP = lambda x: VPG[1] + 100 * (VPG[0] - x) / 550  # the dojo's lit step, its upper edge (to the vanishing point)
STEP_BOT = lambda x: VPG[1] + 118 * (VPG[0] - x) / 550   # and its lower edge, on the pavement
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


def inpaint(layers, hole, allowed, guide, P=3, R=32):
    """Fills hole in every layer, patch by patch (exemplar-based, Criminisi et al.): the fill front's pixel whose patch is
    the most known and lies across the strongest structure first, from the patch of the painting (within R px, inside
    allowed, wholly known at the start) that best matches its known pixels in guide; each filled pixel takes its source's
    value in every layer."""
    H, W = hole.shape; k = 2 * P + 1
    E = P + 4 * R
    pad = lambda a, v: np.pad(a, ((E, E), (E, E)) + ((0, 0),) * (a.ndim - 2), constant_values=v)
    G = pad(guide.astype(float), 0); M = pad(hole.copy(), False); inside = pad(np.ones((H, W), bool), False)
    ok = pad(allowed & ~hole, False)
    srcc = ndi.uniform_filter((~ok).astype(float), size=k, mode='constant', cval=1) < 1e-6      # (sources: whole patches)
    C = (~M).astype(float); src_y = np.full(M.shape, -1); src_x = np.full(M.shape, -1)
    Lg = G[..., :3] @ [0.299, 0.587, 0.114]
    while M.any():
        front = M & ndi.binary_dilation(~M & inside)
        if not front.any(): break
        ys, xs = np.where(front)
        conf = ndi.uniform_filter(C, size=k)[ys, xs]
        Lf = np.where(M, ndi.uniform_filter(np.where(M, 0, Lg), 5) / np.maximum(ndi.uniform_filter((~M).astype(float), 5), 1e-3), Lg)
        gx, gy = ndi.sobel(Lf, 1), ndi.sobel(Lf, 0); nx, ny = ndi.sobel(M.astype(float), 1), ndi.sobel(M.astype(float), 0)
        nn = np.hypot(nx, ny) + 1e-6
        data = np.abs(-gy[ys, xs] * nx[ys, xs] / nn[ys, xs] + gx[ys, xs] * ny[ys, xs] / nn[ys, xs]) / 255
        i = int(np.argmax(conf * (data + 0.05))); py, px = ys[i], xs[i]
        T = G[py - P:py + P + 1, px - P:px + P + 1]; Tk = ~M[py - P:py + P + 1, px - P:px + P + 1] & inside[py - P:py + P + 1, px - P:px + P + 1]
        for Rr in (R, 2 * R, 4 * R):                                          # (no source near: look further)
            win = G[py - Rr - P:py + Rr + P + 1, px - Rr - P:px + Rr + P + 1]
            if win.shape[0] < 2 * Rr + k or win.shape[1] < 2 * Rr + k: break
            sw = np.lib.stride_tricks.sliding_window_view(win, (k, k), axis=(0, 1))          # (2R+1, 2R+1, ch, k, k)
            d = ((sw - T.transpose(2, 0, 1)[None, None]) ** 2 * Tk[None, None, None]).sum((2, 3, 4)) / max(Tk.sum(), 1)
            dyy, dxx = np.mgrid[-Rr:Rr + 1, -Rr:Rr + 1]; d = d + 6.0 * np.hypot(dyy, dxx)
            d[~srcc[py - Rr:py + Rr + 1, px - Rr:px + Rr + 1]] = np.inf
            if np.isfinite(d).any(): break
        if not np.isfinite(d).any(): M[py, px] = False; continue
        j = int(np.argmin(d)); qy, qx = py - Rr + j // (2 * Rr + 1), px - Rr + j % (2 * Rr + 1)
        fill = M[py - P:py + P + 1, px - P:px + P + 1] & inside[py - P:py + P + 1, px - P:px + P + 1]
        oy, ox = np.where(fill)
        G[py - P + oy, px - P + ox] = G[qy - P + oy, qx - P + ox]
        sy0, sx0 = src_y[qy - P + oy, qx - P + ox], src_x[qy - P + oy, qx - P + ox]
        src_y[py - P + oy, px - P + ox] = np.where(sy0 >= 0, sy0, qy - P + oy)
        src_x[py - P + oy, px - P + ox] = np.where(sx0 >= 0, sx0, qx - P + ox)
        C[py - P + oy, px - P + ox] = conf[i] if conf[i] > 0 else 0.01
        M[py - P + oy, px - P + ox] = False
    o = E; fy, fx = np.where(hole & (src_y[o:o + H, o:o + W] >= 0))
    sy, sx = src_y[o + fy, o + fx] - o, src_x[o + fy, o + fx] - o
    for L in layers: L[fy, fx] = L[sy, sx]


def street_copy(out, cur, hole, ok, ring, steps, fit='local'):
    """Fills hole from the same ground further along the street: p -> the vanishing point + (p - it) k, k = 1 / (1 + a (y -
    its y)) (a step along the street, a in steps): its long joints stay on their lines, its cross joints level. The moves
    whose copy best matches the fine detail (the joints) of ring first, each filling what it can from ok pixels. Then the
    copy's light (in the street's two lit layers) matched to ring: 'local', to the painting right round each pixel;
    'plane', by a gain varying linearly across it (the painting's own gradient), fitted on ring."""
    H, W = hole.shape; vx, vy = VPG
    hy, hx = np.where(hole); ry, rx = np.where(ring)
    hp = cur[0][:, :, :3] - ndi.uniform_filter(cur[0][:, :, :3], size=(7, 7, 1))
    def src(y, x, a):
        k = 1 / (1 + a * (y - vy)); return np.round(vy + (y - vy) * k).astype(int), np.round(vx + (x - vx) * k).astype(int)
    def valid(sy, sx):
        v = (sy >= 0) & (sy < H) & (sx >= 0) & (sx < W); v[v] &= ok[sy[v], sx[v]]; return v
    costs = []
    for a in steps:
        sy, sx = src(ry, rx, a); v = valid(sy, sx)
        if v.sum() < 30: continue
        costs.append((float(np.abs(hp[ry[v], rx[v]] - hp[sy[v], sx[v]]).mean()), a))
    costs.sort()
    left = np.ones(len(hy), bool); filled = np.zeros((H, W), bool)
    for _, a in costs:
        sy, sx = src(hy, hx, a); v = left & valid(sy, sx)
        for L, O in zip(out, cur): L[hy[v], hx[v]] = O[sy[v], sx[v]]
        filled[hy[v], hx[v]] = True; left &= ~v
        if not left.any(): break
    hole &= ~filled
    fy, fx = np.where(filled)
    for li, L in enumerate(out[:2]):
        for ch in range(3):
            if fit == 'plane':                                                # (the copy at ring's places, by the best move)
                sy, sx = src(ry, rx, costs[0][1]); v = valid(sy, sx)
                lo_o = ndi.uniform_filter(cur[li][:, :, ch], 5)[ry[v], rx[v]]; lo_c = ndi.uniform_filter(cur[li][:, :, ch], 5)[sy[v], sx[v]]
                A_ = np.stack([np.ones(v.sum()), rx[v], ry[v]], 1)
                cf = np.linalg.lstsq(A_ * lo_c[:, None], lo_o, rcond=None)[0]
                g = cf[0] + cf[1] * fx + cf[2] * fy
            else:
                seen = ring
                w0 = ndi.gaussian_filter(seen.astype(float), 5); w1 = ndi.gaussian_filter(filled.astype(float), 5)
                m0 = ndi.gaussian_filter(np.where(seen, L[:, :, ch], 0), 5) / np.maximum(w0, 1e-6)
                m1 = ndi.gaussian_filter(np.where(filled, L[:, :, ch], 0), 5) / np.maximum(w1, 1e-6)
                g = np.where(w0 > 0.02, (m0 + 2) / (m1 + 2), 1)[fy, fx]
            L[fy, fx, ch] = np.clip(L[fy, fx, ch] * np.clip(g, 0.6, 1.6), 0, 255)


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
    # the old bush: only its leaves go, the dojo's front, its step and the pavement under them stay as painted. Under the
    # shoji (their foot at y 690), the front's stone foot, then the lit stone step (a light band ~17 px, toward the vanishing
    # point), then the pavement. Its leaves: on the front, dark and green (no blue as the stone's specks, no orange as the
    # paper, no red as the wood), in blobs of 5 px or more; on the step, anything dark; on the pavement, darker than any of
    # its own pixels; with their soft edges; not the dark gap by the door nor its frame. The red thing half hidden at the
    # front's foot goes with them (half of it made no sense)
    r_, g_, b_ = city[:, :, 0], city[:, :, 1], city[:, :, 2]
    reg = (yy >= 592) & (xx < 126) & ~((xx >= 100) & (yy < 752))              # (the door's dark gap and its warm foot: as painted)
    top, bot = STEP(xx), STEP_BOT(xx)
    foot = RAILS[3](xx)
    kick = (yy >= foot) & (yy < top) & (xx < 100)
    band = (yy >= top) & (yy < bot) & (xx < 100)                              # (right of it, the door's dark gap: as painted)
    pave = (yy >= bot) & ~((xx >= 100) & (yy < 752))
    seed = reg & ~band & ~pave & (g_ >= b_ - 3) & (((g_ >= r_ - 6) & (Lc < 22)) | ((g_ >= r_ + 4) & (Lc < 45)))
    lab, n = ndi.label(seed, structure=np.ones((3, 3)))
    seed &= np.isin(lab, 1 + np.where(ndi.sum(seed, lab, range(1, n + 1)) >= 5)[0])
    seed |= reg & band & (Lc < 25)
    seed |= reg & pave & ((Lc < 11) | ((Lc < 16) & (b_ - g_ < 5)) | ((r_ > g_ + 6) & (xx < 100)))   # (and the red thing's reflection)
    seed |= reg & kick & (xx < 60) & (r_ > 80) & (r_ > g_ + 40)
    around = ndi.uniform_filter(np.where(seed, 0, Lc), 7) / np.maximum(ndi.uniform_filter((~seed).astype(float), 7), 1e-3)
    leaves = seed | (ndi.binary_dilation(seed, structure=np.ones((3, 3))) & reg & ~band & (Lc < around - 6))
    # the shoji: each pixel's place in its cell (between two rails), the same place in the other cells, the nearest first
    R_ = [np.asarray(f(xx), float) for f in RAILS]
    shoji_z = (yy >= R_[0]) & (yy < R_[3]) & (xx < SHOJI_X1)
    cell = np.where(yy < R_[1], 0, np.where(yy < R_[2], 1, 2))
    pick = lambda Rk, i: np.take_along_axis(np.stack(Rk), i[None], 0)[0]
    lo, hi = pick(R_, cell), pick(R_, cell + 1); f = (yy - lo) / (hi - lo)
    cands = []
    for d in (-1, 1, -2, 2):
        j = cell + d; okj = (j >= 0) & (j <= 2); jj = np.clip(j, 0, 2)
        sy = np.clip(np.round(pick(R_, jj) + f * (pick(R_, jj + 1) - pick(R_, jj))).astype(int), 0, H - 1)
        cands.append((okj & shoji_z, sy))
    def first_clean(mask):
        src = np.full((H, W), -1)
        for okj, sy in cands[::-1]:
            good = okj & ~mask[sy, xx]; src = np.where(good, sy, src)
        return src
    src0 = first_clean(leaves)
    refL = np.where(src0 >= 0, Lc[np.maximum(src0, 0), xx], np.nan)        # (on the paper: what is darker than the same place
    near = ndi.binary_dilation(leaves, iterations=3)                         # in a clean cell, near the leaves or much darker)
    leaves |= shoji_z & reg & (((Lc < np.nan_to_num(refL, nan=0) - 20) & near) | (Lc < np.nan_to_num(refL, nan=0) - 30))
    need_b = leaves.copy(); hole = leaves.copy()
    if os.environ.get('LEAVES'): np.save(os.environ['LEAVES'], leaves)
    src = first_clean(leaves)
    for y, x in zip(*np.where(leaves & shoji_z & (src >= 0))):
        for L, O in zip(out, cur): L[y, x] = O[src[y, x], x]
        hole[y, x] = False
    # the stone foot, the step and the pavement: each patch by patch from its own painting round it (exemplar inpainting),
    # the same source in every layer
    gd = lambda: np.concatenate([out[0][:, :, :3], out[1][:, :, :3]], -1)
    inpaint(out, hole & kick, kick, guide=gd())
    # the step and the pavement: the same step, the same pavement further down the street (each pixel along its line to the
    # vanishing point, scaled as the depth: the long joints stay on their lines, the cross joints level), the moves that
    # best line up with what shows between the leaves first; then their light matched to the painting round them
    street_copy(out, cur, hole & band, band & ~leaves, band & ~leaves, np.r_[np.linspace(-0.004, -0.0002, 40), np.linspace(0.0002, 0.012, 120)])
    if (hole & band).any(): inpaint(out, hole & band, band, guide=gd())
    # (the pavement where the bush stood, all of it: what showed of it was in the bush's shade)
    pv = (poly(OLD_BUSH, H, W) & pave) | (leaves & pave)
    pv_ok = pave & ~pv & (yy < KERB_Y(xx)) & ~((xx >= 124) & (xx <= 133))
    ring = ndi.binary_dilation(pv, iterations=8) & pv_ok
    hole |= pv; need_b |= pv
    street_copy(out, cur, hole & pv, pv_ok, ring, np.linspace(0.0005, 0.012, 240), fit='plane')
    if (hole & pv).any(): inpaint(out, hole & pv, pave & (xx < 300), guide=gd())
    rest = hole & ~kick & ~pave & ~band
    if rest.any(): inpaint(out, rest, reg, guide=gd())
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
    left = crown_old & ~cm & ~dm & ~bm & ~fm & ~(need | need_f | seen) & ~(xx < 4) & ~(wall & lit)
    if os.environ.get('LEFT'): np.save(os.environ['LEFT'], left)
    save(city, 'layer_city_off.webp', 'RGBA'); save(unlit, 'street_unlit.webp', 'RGBA')
    save(nf, 'night_far.webp', 'RGB'); save(sun, 'street_sun.webp', 'RGB')
    print('crown', int(cm.sum()), '| behind it', int(dm.sum()), '| bush', int(bm.sum()), '| wall rebuilt', int(need.sum()),
          '| the bush\'s leaves out', int(need_b.sum()), '| old pixels left as they were', int(left.sum()))


if __name__ == '__main__':
    main()
