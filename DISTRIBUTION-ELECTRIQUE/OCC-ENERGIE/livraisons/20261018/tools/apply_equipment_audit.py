"""Applique les corrections de façade et le contrôle individuel sans toucher aux câbles."""
import json
from pathlib import Path


def apply(data, root):
    root = Path(root)
    path = root / 'build/facade-audit-corrections.json'
    if path.exists():
        review = json.loads(path.read_text(encoding='utf-8'))
        data['facades'].update(review['facades'])
    path = root / 'build/equipment-audit.json'
    if path.exists():
        records = json.loads(path.read_text(encoding='utf-8'))
        boards = {board['id']: board for board in data['boards']}
        for record in records:
            board = boards[record['id']]
            board['audit'] = record
            board['facadeMode'] = data['facades'][board['facade']].get('mode', 'photo-partial')
        data['equipmentAudit'] = {'count': len(records), 'date': '2026-10-16'}
    return data
