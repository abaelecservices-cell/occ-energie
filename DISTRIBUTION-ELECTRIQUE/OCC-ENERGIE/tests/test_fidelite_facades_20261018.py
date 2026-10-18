"""Protection contre les régressions de classement photographique.
Ce test ne certifie aucune liaison électrique ni position sur le terrain.
"""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
d = json.loads((ROOT/'build/data.json').read_text(encoding='utf-8'))
bs = {b['id']: b for b in d['boards']}
assert len(d['boards']) == 66
assert len(d['nodes']) == 730
assert len(d['edges']) == 735
assert len(d['facades']) >= 54

ts1 = d['facades']['TS1']
ts8 = d['facades']['TS8']
assert ts1['style'] == 'ensimage_bleu_gris'
assert len(ts1['cols']) == 7, "7 zones visuelles TS1 demandées par IMG_3990"
assert 'IMG_3978' in ts1['src'] and 'IMG_3992' in ts1['src']
assert 'IMG_3967' not in ts1['src'], "Cette archive est TS8, pas TS1"
assert 'IMG_3966' in ts8['src'] and 'IMG_3977' in ts8['src']
assert 'IMG_3990' not in ts8['src']
assert 'corrig' in ts1['conf'].lower() or 'REVUE' in ts1['conf']
assert ts8['style'] == 'okken_beige'

for b in d['boards']:
    if b.get('facade'):
        f = b.get('controle_photo')
        assert isinstance(f, dict), b['id']
        assert f.get('cote_certifiee') is False
        assert f.get('manoeuvre_autorisee') is False
        assert f.get('statut') != 'photographie_exacte_validee'
assert bs['ENSIM_A']['controle_photo']['statut'] == 'identification_source_non_validee'
assert bs['ENSIM_B']['controle_photo']['statut'] == 'identification_source_non_validee'
assert bs['TS17']['controle_photo']['statut'] == 'correspondance_partielle_a_confirmer'

app = (ROOT/'OCC_ENERGIE.html').read_text(encoding='utf-8')
lite = (ROOT/'OCC_ENERGIE_2024_LITE.html').read_text(encoding='utf-8')
for html in (app, lite):
    assert '"controle_photo":' in html
    assert "photoValidationHTML" in html
    assert "ensimage_bleu_gris" in html
print('OK : TS1/TS8 sources rétablies, 7 zones TS1, 54+ façades sans certification fictive.')
