"""Prépare la vue aérienne (image du PowerPoint « site l ardoise ») :
rotation selon la diapositive, détourage à la première délimitation rouge (périmètre du site), WebP avec transparence.
Écrit aussi build/aerial_crop.json (cadre de recadrage en fraction de l'image d'origine) pour recaler les repères.
"""
import sys, zipfile, io, json, os
from PIL import Image, ImageDraw
z = zipfile.ZipFile(sys.argv[1])
im = Image.open(io.BytesIO(z.read('ppt/media/image1.png'))).convert('RGBA')
im = im.rotate(90, expand=True)  # rot=270° (sens horaire) dans la diapositive
im.thumbnail((2000, 2000), Image.LANCZOS)
W, H = im.size
# Premier périmètre rouge relevé par détection des pixels rouges (image 1933 x 1473) : bord gauche x≈20,
# bord haut de (22,30) à (1872,82), bord droit x≈1872 jusqu'à y≈282, diagonale intérieure jusqu'à (885,1447), bord bas y≈1447.
k = W / 1933.0
poly = [(x * k, y * k) for x, y in [(16, 26), (1876, 78), (1876, 282), (888, 1450), (16, 1450)]]
mask = Image.new('L', (W, H), 0)
ImageDraw.Draw(mask).polygon(poly, fill=255)
alpha = Image.composite(im.getchannel('A'), Image.new('L', (W, H), 0), mask)
im.putalpha(alpha)
box = tuple(int(v) for v in (min(p[0] for p in poly), min(p[1] for p in poly), max(p[0] for p in poly) + 1, max(p[1] for p in poly) + 1))
im = im.crop(box)
im.save(sys.argv[2], 'WEBP', quality=76, method=6)
json.dump(dict(x0=box[0] / W, y0=box[1] / H, x1=box[2] / W, y1=box[3] / H, poly=[((x - box[0]) / (box[2] - box[0]), (y - box[1]) / (box[3] - box[1])) for x, y in poly]),
          open(os.path.join(os.path.dirname(sys.argv[2]), 'aerial_crop.json'), 'w'))
print('sortie', im.size, 'cadre', box)
