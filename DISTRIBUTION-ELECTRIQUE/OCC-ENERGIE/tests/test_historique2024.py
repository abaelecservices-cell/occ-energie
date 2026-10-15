"""Controle documentaire du referentiel Excel 2024 embarque dans OCC Energie.

Aucun test ne certifie l'installation physique ni n'autorise une manoeuvre.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HIST = ROOT / 'sources' / 'referentiel_excel_2024.json'
MODEL = ROOT / 'build' / 'data.json'
APP = ROOT / 'OCC_ENERGIE.html'

h = json.loads(HIST.read_text(encoding='utf-8'))
depts = h['departIndex2024']
ages = h['ageEquipements2024']
assert len(depts) == 36, f"{len(depts)} depart(s), attendu 36"
assert len(ages) == 68, f"{len(ages)} historique(s), attendu 68"
assert {e['tgbt'] for e in depts} == {1, 2, 4}
assert all(e['statut'] == 'archive_2024_non_validee_2026' for e in depts)
assert all('INDEX' in e['source'] for e in depts)
assert all('Age equipement' in e['source'] for e in ages)
assert len({(e['tgbt'], e['cote'], e['colonne'], e['case']) for e in depts}) == 36
assert any(e['ts'] == 'TS8' and e['tgbt'] == 4 and e['cote'] == 'A' and e['colonne'] == 1 and e['case'] == '23' for e in depts)
assert any(e['ts'] == 'TS1' and e['tgbt'] == 1 and e['colonne'] == 2 and e['case'] == '72' for e in depts)
assert sum(e['anomalieSaisie'] for e in ages) == 3
model = json.loads(MODEL.read_text(encoding='utf-8'))
assert 'historique2024' not in model, 'Le graphe actif ne doit pas etre modifie'
assert not any(edge.get('src', '').startswith('Distribution électrique 2024.xlsx') for edge in model['edges']), 'Liaisons historiques promues en graphe'
assert APP.is_file(), 'HTML non reconstruit'
s = APP.read_text(encoding='utf-8')
assert '"historique2024":' in s
assert 'Referentiel Excel 2024' in s or 'Référentiel Excel 2024' in s
assert 'hx24-list' in s
LITE = ROOT / 'OCC_ENERGIE_2024_LITE.html'
assert LITE.is_file(), 'HTML leger absent'
sl = LITE.read_text(encoding='utf-8')
assert '"historique2024":' in sl and 'hx24-list' in sl
assert 'Mode léger 2024' in sl
print('OK : historique 2024 (36 departs, 68 lignes) trace et integre, graphe actif preserve')
