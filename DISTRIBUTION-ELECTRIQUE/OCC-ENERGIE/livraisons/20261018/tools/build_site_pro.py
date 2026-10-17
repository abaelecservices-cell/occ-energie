"""Prépare le rectangle et les détails natifs de l’export Google Earth Pro."""
import base64
import hashlib
import io
import json
import math
import shutil
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / 'assets/vue_aerienne/google-earth-pro-20261017'
CROP = (2150, 350, 5850, 3050)
TILE, OVERLAP = 512, 1
TARGET.mkdir(exist_ok=True)
source = Path(sys.argv[1])
registration = json.loads(Path(sys.argv[2]).read_text(encoding='utf-8'))
view_file = ROOT / 'build/site-view.json'
previous = ROOT / 'assets/vue_aerienne/google-earth-20261017/site-view.json'
if not previous.exists():
    shutil.copy2(view_file, previous)
view = json.loads(previous.read_text(encoding='utf-8'))
raw = Image.open(source).convert('RGB')
assert raw.size == (8192, 3748)
if source.resolve() != (TARGET / 'export-google-earth-pro-8192.jpg').resolve():
    shutil.copy2(source, TARGET / 'export-google-earth-pro-8192.jpg')
reference = json.loads((ROOT/'build/site-reference-registration.json').read_text(encoding='utf-8'))
reference_path = TARGET/'reference-utilisateur.png'
image = Image.open(reference_path).convert('RGB')
font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 24)
# Le crédit est affiché par la visionneuse, le fichier reçu reste intact.
preview = image.copy()
preview.thumbnail((2048, 2048))
preview.save(TARGET / 'apercu.webp', 'WEBP', quality=92, method=6)
width, height = image.size
level = math.ceil(math.log2(max(width, height)))
tiles = {}
for current in range(level-2, level+1):
    factor = 2 ** (level-current)
    frame = image if factor == 1 else image.resize((math.ceil(width/factor), math.ceil(height/factor)), Image.Resampling.LANCZOS)
    for column in range(math.ceil(frame.width/TILE)):
        for row in range(math.ceil(frame.height/TILE)):
            box = (max(0,column*TILE-OVERLAP), max(0,row*TILE-OVERLAP), min(frame.width,(column+1)*TILE+OVERLAP), min(frame.height,(row+1)*TILE+OVERLAP))
            tile = frame.crop(box)
            name = f'{current}-{column}-{row}.webp'
            tile.save(TARGET/name, 'WEBP', lossless=True, method=4)
            if current == level:
                assert Image.open(TARGET/name).convert('RGB').tobytes() == tile.tobytes()
            tiles[f'{current}/{column}_{row}'] = 'data:image/webp;base64,'+base64.b64encode((TARGET/name).read_bytes()).decode() if current == level-2 else str((TARGET/name).relative_to(ROOT)).replace('\\','/')
    print('Niveau', current, 'terminé', flush=True)
def point(x, y):
    px = (x*1000+registration['dx'])*raw.width/registration['proWidth']
    py = (y*573+registration['dy'])*raw.height/round(raw.height*registration['proWidth']/raw.width)
    return [(px*reference['width']/raw.width-reference['dx'])/reference['refWidth'], (py*reference['height']/raw.height-reference['dy'])/reference['refHeight']]
for zone in view['zones']:
    zone['cx'], zone['cy'] = point(zone['cx'],zone['cy'])
    zone['polys'] = [[point(x,y) for x,y in polygon] for polygon in zone.get('polys',[])]
view.update(image=str((TARGET/'apercu.webp').relative_to(ROOT)).replace('\\','/'), w=width, h=height, ratio=width/height, tiles=tiles, tileSize=TILE, overlap=OVERLAP, maxLevel=level, attribution='Google Earth Pro · Image © 2026 Airbus · 16/04/2026', src=f'Image fournie par l’utilisateur, {width} × {height} pixels, cadrage intégral conservé ; recalage indicatif.')
view_file.write_text(json.dumps(view,ensure_ascii=False,indent=2),encoding='utf-8')
metadata = dict(source='Google Earth Pro', producer='Airbus', imageDate='2026-04-16', exportSize=list(raw.size), crop=None, referenceFile='reference-utilisateur.png', referenceSha256=hashlib.sha256(reference_path.read_bytes()).hexdigest(), referenceRegistration=reference, appSize=list(image.size), registration=registration, tiles=len(tiles), nativeTiles='WebP sans perte, pixels décodés comparés au rectangle source', sourceSha256=hashlib.sha256(source.read_bytes()).hexdigest())
(TARGET/'metadata.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding='utf-8')
print('Export conservé, rectangle et',len(tiles),'tuiles prêts',flush=True)
