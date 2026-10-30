import io, subprocess, sys
import numpy as np
from PIL import Image
R='/home/user/mtsfj.github.io/'
def load(p, at=None):
    data = subprocess.run(['git','show',f'{at}:assets/{p}'],cwd=R,capture_output=True,check=True).stdout if at else open(R+'assets/'+p,'rb').read()
    return Image.open(io.BytesIO(data)).convert('RGBA')
def comp(at=None):
    sky=load('layer_sky.webp').convert('RGB')
    W,H=1456,816; PAD=160
    sk=sky.resize((W+2*PAD,H+2*PAD),Image.BILINEAR).crop((PAD,PAD,PAD+W,PAD+H)).convert('RGBA')
    for n in ('fuji_night.webp','fuji_tree.webp','fuji_front.webp'):
        L=load(n); tmp=Image.new('RGBA',(W,H),(0,0,0,0)); tmp.paste(L,(376,66)); sk.alpha_composite(tmp)
    sk.alpha_composite(load('layer_city_off.webp',at))
    return sk.convert('RGB')
