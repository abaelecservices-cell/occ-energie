"""Pyramide de zoom de la vue aérienne, embarquée dans l'application (fichier HTML unique, hors ligne).

Source : assets/vue_aerienne/OCC_usine_IGN_2024_20cm.png (IGN BD ORTHO 2024, 20 cm/pixel, 2008 × 2636, transparent hors contour).
Traitement : rotation de 90° dans le sens antihoraire demandée par l'exploitant (transposition exacte : aucun pixel recalculé),
puis découpage Deep Zoom (tuiles 512 px, recouvrement 1 px). Niveau final = pixels d'origine ; niveaux inférieurs réduits (LANCZOS).
Tuiles en WebP sans perte (mêmes pixels que le PNG, plus compact), encodées en data URI.
Usage : py -3 -I tools/site_tiles.py <png maître> <rotation en degrés, 90 ou 0> <sortie json>
"""
import sys, io, json, math, base64
from PIL import Image
src, rot, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
im = Image.open(src).convert('RGBA')
if rot == 90: im = im.transpose(Image.Transpose.ROTATE_90)        # sens antihoraire, sans rééchantillonnage
W, H = im.size
T, OV = 512, 1
L = math.ceil(math.log2(max(W, H)))
tiles, n, total = {}, 0, 0
for lv in range(L, -1, -1):
    k = 2 ** (L - lv)
    lw, lh = math.ceil(W / k), math.ceil(H / k)
    img = im if k == 1 else im.resize((lw, lh), Image.LANCZOS)
    for c in range(math.ceil(lw / T)):
        for r in range(math.ceil(lh / T)):
            x0, y0 = max(0, c * T - OV), max(0, r * T - OV)
            x1, y1 = min(lw, (c + 1) * T + OV), min(lh, (r + 1) * T + OV)
            t = img.crop((x0, y0, x1, y1))
            if t.getchannel('A').getbbox() is None: continue             # tuile entièrement transparente : inutile
            b = io.BytesIO(); t.save(b, 'WEBP', lossless=True, quality=100, method=6)
            tiles[f'{lv}/{c}_{r}'] = 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()
            n += 1; total += len(b.getvalue())
    if lw <= 64: break
json.dump(dict(width=W, height=H, tileSize=T, overlap=OV, maxLevel=L, rotation=rot, tiles=tiles), open(out, 'w'))
print('image', (W, H), 'niveaux', L, 'tuiles', n, 'poids', total // 1024, 'Ko')
