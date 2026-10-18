"""Corrige les identités du plan sans transformer un repère en câble vérifié."""
import json
from pathlib import Path


def apply(data, root):
    path = Path(root) / 'build/network-review.json'
    if not path.exists():
        return data
    review = json.loads(path.read_text(encoding='utf-8'))
    boards = {b['id']: b for b in data['boards']}
    for patch in review['boards']:
        boards[patch['id']].update(patch)
    ids = {n['id'] for n in data['nodes']}
    data['nodes'].extend(n for n in review['nodes'] if n['id'] not in ids)
    plan = next(p for p in data['plans'] if p['id'] == 'PLAN_SS1')
    for patch in review['planPatches']:
        fields = {k: v for k, v in patch.items() if k != 'index'}
        plan['items'][patch['index']].update(fields)
    facade = data['facades'].get(boards['TGBT8']['facade'])
    if facade:
        facade['title'] = 'TGBT8 — Gradathyr N3,1 creuset'
    face_path = Path(root) / 'build/tgbt8-facade-review.json'
    if face_path.exists():
        data['facades']['TGBT8'] = json.loads(face_path.read_text(encoding='utf-8'))
    import runpy
    return runpy.run_path(str(Path(root) / 'tools/apply_document_cross_review.py'))['apply'](data, root)
