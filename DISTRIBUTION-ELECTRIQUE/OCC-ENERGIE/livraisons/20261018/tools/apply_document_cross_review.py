"""Ajoute les sources et contradictions sans arbitrer les raccordements."""
import json
from pathlib import Path


def apply(data, root):
    path = Path(root) / 'build/document-cross-review.json'
    if not path.exists():
        return data
    review = json.loads(path.read_text(encoding='utf-8'))
    boards = {board['id']: board for board in data['boards']}
    for patch in review['boards']:
        boards[patch['id']].update(patch)
    facade = data['facades']['PL20']
    facade.update(nophoto=False, mode='photo-partial', src='photo.zip / IMG_4334 à IMG_4381', conf='Façade dédiée relevée sur photos : huit fonctions EDF / CNR, caissons hauts, relais, commandes et coffrets saillants. Proportions indicatives ; dimensions non mesurées.')
    boards['PL20']['note'] = '48 photos du poste de livraison disponibles ; façade dédiée reconstruite depuis les vues générales et détails. Les positions des commandes et clés sont illustratives, pas un état réel. Les coffrets muraux auxiliaires restent en galerie.'
    comparison = 'docs/PL20-COMPARAISON.html'
    if comparison not in boards['PL20'].setdefault('photos', []):
        boards['PL20']['photos'].append(comparison)
    data['documentReview'] = {key: value for key, value in review.items() if key != 'boards'}
    import runpy
    return runpy.run_path(str(Path(root) / 'tools/apply_equipment_audit.py'))['apply'](data, root)
