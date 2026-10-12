"""Audit qualité des photos (netteté, surexposition, sous-exposition, résolution) pour chaque page des PDF photo.

Netteté : variance du laplacien sur l'image ramenée à 1200 px (valeur faible = flou / bougé).
Surexposition : part des pixels > 245 ; sous-exposition : part des pixels < 25.
Usage : py -3 -I audit_photos.py "<dossier Plan électrique>" <sortie.csv>
"""
import sys, os, io, csv, pymupdf
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image, ImageFilter, ImageStat
Image.MAX_IMAGE_PIXELS = None
src, out = sys.argv[1], sys.argv[2]
rows = []
for f in sorted(os.listdir(src)):
    if not f.lower().endswith('.pdf'): continue
    d = pymupdf.open(os.path.join(src, f))
    for i, p in enumerate(d):
        imgs = p.get_images()
        if not imgs: continue
        x = d.extract_image(imgs[0][0])
        im = Image.open(io.BytesIO(x['image'])).convert('L')
        W, H = im.size
        im.thumbnail((1200, 1200))
        lap = im.filter(ImageFilter.Kernel((3, 3), [0, 1, 0, 1, -4, 1, 0, 1, 0], 1, 128))
        sharp = ImageStat.Stat(lap).var[0]
        hist = im.histogram(); n = sum(hist)
        over = sum(hist[246:]) / n; under = sum(hist[:25]) / n
        verdict = []
        if sharp < 550: verdict.append('FLOU')
        elif sharp < 700: verdict.append('peu net')
        if over > 0.62: verdict.append('SUREXPOSÉ')
        if under > 0.35: verdict.append('SOMBRE')
        rows.append([f.strip(), i + 1, W, H, round(sharp), round(over * 100), round(under * 100), ' / '.join(verdict) or 'OK'])
with open(out, 'w', encoding='utf-8-sig', newline='') as fh:
    c = csv.writer(fh, delimiter=';'); c.writerow(['Fichier', 'Page', 'Largeur px', 'Hauteur px', 'Netteté', '% surexposé', '% sombre', 'Verdict'])
    c.writerows(rows)
# netteté calibrée sur les photos : flou net à l'œil sous ~550 (Ts17A p1-p2), photos nettes 850-1300
# synthèse par fichier
from collections import defaultdict
agg = defaultdict(list)
for r in rows: agg[r[0]].append(r)
for k, v in agg.items():
    bad = [r for r in v if r[7] != 'OK']
    print(f"{k:45s} pages={len(v):3d}  netteté méd={sorted(r[4] for r in v)[len(v)//2]:5d}  problèmes={len(bad):2d}  " + ', '.join(f"p{r[1]}:{r[7]}" for r in bad[:8]))
