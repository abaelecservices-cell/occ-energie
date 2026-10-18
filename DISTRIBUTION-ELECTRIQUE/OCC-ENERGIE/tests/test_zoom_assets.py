"""Contrôle des 22 tuiles satellite haute définition OCC Énergie.

Garantit qu'une livraison complète reconstruite conserve le niveau 12, que
chaque WebP correspond exactement au référentiel source et que le mode léger
reste autonome. Ne valide ni câblages ni manœuvres électriques.
"""
import base64
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = json.loads((ROOT / 'build/data.json').read_text(encoding='utf-8'))
ALL = SRC['site']['tiles']
ZOOM12 = {k: v for k, v in ALL.items() if k.startswith('12/')}
assert len(ZOOM12) == 22, f"{len(ZOOM12)} tuiles de zoom 12 (attendu : 22)"
for key, value in ZOOM12.items():
    expected = base64.b64decode(value.split(',', 1)[1], validate=True)
    target = ROOT / 'assets' / 'ts8_site_tiles' / (key + '.webp')
    assert target.is_file(), f"Tuile absente : {target}"
    actual = target.read_bytes()
    assert actual == expected, f"Tuile différente de la source : {key}"
    assert actual[:4] == b'RIFF' and actual[8:12] == b'WEBP', key

def model_from_html(filename):
    html = (ROOT / filename).read_text(encoding='utf-8')
    token = 'window.OCC_DATA='
    start = html.index(token) + len(token)
    end = html.index(';</script>', start)
    return json.loads(html[start:end]), html

main, main_html = model_from_html('OCC_ENERGIE.html')
for filename in ('OCC_ENERGIE_TS8.html', 'OCC_ENERGIE_VECTORIEL_MOBILE.html'):
    model, content = model_from_html(filename)
    assert content == main_html, f"HTML complet divergent : {filename}"
for key in ZOOM12:
    assert main['site']['tiles'][key] == 'assets/ts8_site_tiles/' + key + '.webp', key
assert len(main['site']['tiles']) == len(ALL) == 34
assert len(main['nodes']) == 730 and len(main['edges']) == 735 and len(main['boards']) == 66
assert len(main['referentielSAP']['tableaux']) == 28

lite, lite_html = model_from_html('OCC_ENERGIE_2024_LITE.html')
assert not any(k.startswith('12/') for k in lite['site']['tiles'])
assert all(str(v).startswith('data:image/webp;base64,') for v in lite['site']['tiles'].values())
assert len(lite['nodes']) == len(main['nodes'])
assert len(lite['edges']) == len(main['edges'])
assert (ROOT / 'OCC_ENERGIE_SAP_20261017_LITE.html').read_text(encoding='utf-8') == lite_html

print('OK : 22 WebP zoom 12 identiques à la source ; 3 HTML complets cohérents, lite autonome')
