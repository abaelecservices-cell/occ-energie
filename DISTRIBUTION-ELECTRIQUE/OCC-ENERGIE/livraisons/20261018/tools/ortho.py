"""Orthophoto IGN 2024 (20 cm/px) : reconstitue l'image pleine résolution à partir des tuiles base64 du fichier
« OCC_usine_vue_zoomable.html » (config window.OCC_ORTHOPHOTO_CONFIG), puis écrit :
  build/ortho.webp       image complète, transparente hors périmètre (WebP, embarquée dans l'application)
  build/ortho.json       dimensions, résolution, emprise Lambert 93, périmètre
  build/ortho_full.png   image de travail (non embarquée)
Usage : py -3 -I tools/ortho.py <fichier html> <dossier build>
"""
import sys, json, base64, io, os
from PIL import Image, ImageDraw
src, out = sys.argv[1], sys.argv[2]
line = next(l for l in open(src, encoding='utf-8') if 'OCC_ORTHOPHOTO_CONFIG' in l and '{' in l)
cfg = json.loads(line[line.index('{'):line.rindex('}') + 1])
W, H, T, ov, L = cfg['width'], cfg['height'], cfg['tileSize'], cfg['overlap'], cfg['maxLevel']
img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
n = 0
for key, uri in cfg['tiles'].items():
    lv, cr = key.split('/'); c, r = map(int, cr.split('_'))
    if int(lv) != L: continue
    t = Image.open(io.BytesIO(base64.b64decode(uri.split(',', 1)[1]))).convert('RGBA')
    left, top = max(0, c * T - ov), max(0, r * T - ov)
    cx, cy = c * T - left, r * T - top
    cw, ch = min(T, W - c * T), min(T, H - r * T)
    img.paste(t.crop((cx, cy, cx + cw, cy + ch)), (c * T, r * T)); n += 1
# périmètre fourni : transparence à l'extérieur
mask = Image.new('L', (W, H), 0)
ImageDraw.Draw(mask).polygon([tuple(p) for p in cfg['perimeterPixels']], fill=255)
a = Image.composite(img.getchannel('A'), Image.new('L', (W, H), 0), mask)
img.putalpha(a)
img.save(os.path.join(out, 'ortho_full.png'))
img.save(os.path.join(out, 'ortho.webp'), 'WEBP', quality=80, method=6)
json.dump(dict(w=W, h=H, res=cfg['resolutionM'], bbox=cfg['bboxLambert93'], perim=cfg['perimeterPixels'],
               src='Orthophoto IGN BD ORTHO® 2024 · 20 cm/pixel · Licence Ouverte Etalab 2.0'),
          open(os.path.join(out, 'ortho.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print('tuiles', n, 'image', img.size, 'webp', os.path.getsize(os.path.join(out, 'ortho.webp')) // 1024, 'Ko')
