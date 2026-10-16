"""Intégrité des renvois documentaires, sans inférence de raccordements."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / 'build/data.json').read_text(encoding='utf-8'))
nodes = {n['id']: n for n in data['nodes']}
boards = {b['id']: b for b in data['boards']}
for board in boards.values():
    assert not board.get('facade') or board['facade'] in data['facades'], board['id']
    assert not board.get('loc') or board['loc'] in data['loc'], board['id']
    for half in board.get('halves', []):
        assert half['id'] in nodes, (board['id'], half['id'])
for node in nodes.values():
    assert not node.get('feeds') or node['feeds'] in boards, node['id']
for fid, facade in data['facades'].items():
    for cell in facade.get('cells', []):
        assert not cell.get('node') or cell['node'] in nodes, (fid, cell)
    for column in facade.get('cols', []):
        for unit in column.get('units', []):
            for key in ('dep', 'node'):
                assert not unit.get(key) or unit[key] in nodes, (fid, unit)
print('OK : façades, demi-tableaux, localisations et destinations sans renvoi orphelin')
