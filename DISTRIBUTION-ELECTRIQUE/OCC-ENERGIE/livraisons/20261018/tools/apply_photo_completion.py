"""Complète les façades et les repères explicitement lus sur les photos."""
import json
from pathlib import Path

def apply(data, root):
    path = Path(root) / 'build/photo-completion.json'
    if not path.exists():
        return data
    review = json.loads(path.read_text(encoding='utf-8'))
    for key, target in [('additionalBoards', 'boards'), ('additionalNodes', 'nodes')]:
        existing = {item['id'] for item in data[target]}
        data[target].extend(item for item in review.get(key, []) if item['id'] not in existing)
    boards = {item['id']: item for item in data['boards']}
    nodes = {item['id']: item for item in data['nodes']}
    for patch in review.get('boards', []):
        patch = dict(patch)
        observations = patch.pop('observations', [])
        board = boards[patch['id']]
        board.update(patch)
        for observation in observations:
            if observation not in board.setdefault('obs', []):
                board['obs'].append(observation)
    for patch in review.get('nodes', []):
        nodes[patch['id']].update(patch)
    data['facades'].update(review.get('facades', {}))
    return data
