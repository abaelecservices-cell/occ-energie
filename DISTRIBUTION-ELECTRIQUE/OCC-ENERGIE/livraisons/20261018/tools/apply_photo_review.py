"""Applique le relevé photographique TS17 sans modifier les liaisons électriques."""
import json
from pathlib import Path

def apply(data, root):
    path = Path(root) / 'build/ts17-photo-review.json'
    if not path.exists():
        return data
    review = json.loads(path.read_text(encoding='utf-8'))
    board = next(item for item in data['boards'] if item['id'] == review['board']['id'])
    board.update(review['board'])
    for patch in review.get('boards', []):
        next(item for item in data['boards'] if item['id'] == patch['id']).update(patch)
    for issue in review.get('issues', []):
        if not any(item['id'] == issue['id'] for item in data['issues']):
            data['issues'].append(issue)
    data['facades']['TS17'] = review['facade']
    import runpy
    data = runpy.run_path(str(Path(root) / 'tools/apply_photo_completion.py'))['apply'](data, root)
    return runpy.run_path(str(Path(root) / 'tools/apply_network_review.py'))['apply'](data, root)
