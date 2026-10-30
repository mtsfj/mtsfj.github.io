#!/usr/bin/env python3
"""assets/night_far.webp, cleaned: the street's pixels it puts in a far plane where nothing far is there.

    python3 tools/night_far_clean.py      (after tools/fuji_aux.py; again whenever night_far.webp is made anew)

night_far tells the hours' shader which pixels of the street's layers show the far planes (R: 80 the sky, 160 the mountain
or the tree, 255 the far city); those pixels take their plane's hour. Four kinds were wrong, and showed at dawn:
- 'sky' pixels that are not the sky's colour at dusk (the street lamp's lit glass, the blossoms by the right building's
  corner): graded as the morning sky they turned sky blue, holes where the night has none. Now the tree's where the
  cherry is (fuji_aux.webp R), else the street's.
- 'mountain or tree' pixels over neither (on the lamp's head and arm, against the sky): graded as the lit mountain.
  Now the street's.
- the far city seen between the fence's rails left as the street's in a row over the top rail and one under the lower
  one: they kept the dusk's pink at dawn, a magenta line along the fence. A saturated pixel there (not the rails' grey)
  with the far city just above or below is the far city's.
- small islands of 'street' inside the far city (a streak of 8 px at x 616): untouched by the morning's haze around them,
  a dark line in it. An island of up to 30 px with only the far city round it is the far city's.
Needs Pillow, numpy and scipy.
"""
import os
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = lambda p: os.path.join(ROOT, 'assets', p)


def main():
    nf = np.asarray(Image.open(A('night_far.webp')).convert('RGB')).copy()
    city = np.asarray(Image.open(A('layer_city_off.webp')).convert('RGBA')).astype(int)
    sky = np.asarray(Image.open(A('layer_sky.webp')).convert('RGB')).astype(int)
    aux = np.asarray(Image.open(A('fuji_aux.webp')).convert('RGB'))
    fn = np.asarray(Image.open(A('fuji_night.webp')).convert('RGBA'))
    H, W = nf.shape[:2]
    cherry = np.zeros((H, W), bool); mountain = np.zeros((H, W), bool)
    cherry[66:706, 376:1016] = aux[:, :, 0] > 127
    mountain[66:706, 376:1016] = (fn[:, :, 3] > 127) & ~cherry[66:706, 376:1016]
    r = nf[:, :, 0].astype(int)
    is_sky = (r > 51) & (r < 99); is_far = (r > 140) & (r <= 229)
    off_sky = is_sky & (city[:, :, 3] > 0) & (np.abs(city[:, :, :3] - sky).max(-1) > 25)
    box = np.zeros((H, W), bool); box[66:706, 378:1016] = True             # (the far layers' box: out of it, nothing to judge by)
    to_tree = off_sky & cherry; to_street = (off_sky & ~cherry) | (is_far & box & ~cherry & ~mountain)
    nf[to_tree] = 160; nf[to_street] = 0
    rgb = city[:, :, :3]; sat = (rgb.max(-1) - rgb.min(-1)) / np.maximum(rgb.max(-1), 1)
    fence = np.zeros((H, W), bool); fence[612:633, 610:773] = True
    far_city = nf[:, :, 0] > 229
    near_far = np.zeros((H, W), bool); near_far[1:] |= far_city[:-1]; near_far[:-1] |= far_city[1:]; near_far[2:] |= far_city[:-2]; near_far[:-2] |= far_city[2:]
    rails = np.zeros((H, W), bool)                                   # (the rails' own rows: the street's all along)
    for y in range(612, 633):
        if (r[y, 610:760] == 0).mean() > 0.9: rails[y] = True
    to_city = fence & ~rails & (nf[:, :, 0] == 0) & near_far & (sat > 0.33) & (city[:, :, 3] > 0)
    nf[to_city] = 255
    from scipy import ndimage as ndi
    street = nf[:, :, 0] == 0; fc = nf[:, :, 0] > 229
    lab, n = ndi.label(street); isl = np.zeros((H, W), bool)
    for i, sl in enumerate(ndi.find_objects(lab)):
        m = lab[sl] == i + 1
        if m.sum() > 30: continue
        ring = ndi.binary_dilation(lab == i + 1) & ~(lab == i + 1)
        if fc[ring].all(): isl |= lab == i + 1
    nf[isl] = 255
    Image.fromarray(nf).save(A('night_far.webp'), 'WEBP', lossless=True, quality=100, method=6, exact=True)
    print('sky -> tree', int(to_tree.sum()), '| sky -> street', int((off_sky & ~cherry).sum()), '| far over nothing -> street', int((is_far & box & ~cherry & ~mountain).sum()), '| fence rows -> far city', int(to_city.sum()), '| islands -> far city', int(isl.sum()))


if __name__ == '__main__':
    main()
