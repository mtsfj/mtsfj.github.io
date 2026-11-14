#!/usr/bin/env python3
"""The light of the entrance hall right of the pole, in a tone a Japanese apartment entrance has at night (the owner:
"change le ton porte rose, c'est bizarre").

    (a module: tools/redraw_zones.py's zone 'hall' calls draw() on the street as the zones before it leave it, last)

The draft lit the hall pink to magenta: its transom pink-white, its sidelight magenta, its door's slit window, the
recess's left reveal and its head, the step and the sidewalk before it mauve. The hall's light is what the street has
there over the power cut (the street's layer minus street_unlit.webp, where the hall is dark); each pixel keeps its
power cut as it is and its light's brightness, and the light takes the tone (TONE):
    warm  an incandescent hall light, soft amber-white (the street's warm windows, Naruto's room);
    cool  a fluorescent tube, white a little toward blue-green (a stairwell's);
where the light is most of the pixel (the frosted glass) the power cut's own blue under it goes with its colour (its
lightness kept), so the glass is the light's tone and not tinted by the night. Only in the hall's light: a pixel
whose light is not warmer than green (the street lamp's, the sky's) is left as it is. The power cut is not changed (the
hall is out with the street); the red night reads its light from the two layers, so it follows; its hours are the
street's. The pole (x < 1065), the house's corner trim and Ichiraku's corner (x > 1115) are outside. Needs numpy.
"""
import numpy as np

BOX = (1066, 500, 1116, 732)                    # the zone (redraw_zones.py 'hall')
TONE = 'warm'
TONES = {'warm': (255, 214, 160), 'cool': (200, 236, 230)}
LUMA = np.array([0.299, 0.587, 0.114])
MIN_LIGHT = 1.5                                 # (a light under this, of 255, is noise between the layers)


def draw(city, unlit, box=BOX):
    """The zone (redraw_zones.py): the street changed in place over box (the power cut as it is); returns what changed."""
    x0, y0, x1, y1 = box
    H, W = city.shape[:2]
    c, u = city[y0:y1, x0:x1, :3], unlit[y0:y1, x0:x1, :3]
    d = np.clip(c - u, 0, None)
    Ld = d @ LUMA; Lu = u @ LUMA
    hall = (Ld > MIN_LIGHT) & (d[..., 0] > d[..., 1] + 1)             # (its light: pink, mauve, warm; not the lamp's blue)
    t = np.array(TONES[TONE], float); t = t / (t @ LUMA)
    w = (Ld / np.maximum(Ld + Lu, 1e-6))[..., None]                   # (how much of the pixel is the hall's light)
    base = u * (1 - w) + Lu[..., None] * w                            # (the power cut under it, its colour gone with it)
    new = np.clip(base + Ld[..., None] * t, 0, 255)
    c[hall] = new[hall]
    ch = np.zeros((H, W), bool); ch[y0:y1, x0:x1] = hall
    return ch
