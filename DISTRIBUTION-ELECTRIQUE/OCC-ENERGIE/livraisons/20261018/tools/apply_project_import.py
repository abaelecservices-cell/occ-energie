"""Ajoute les compléments documentaires aux fiches, sans changer le réseau."""
import json
from pathlib import Path

def apply(data, root):
    path = Path(root) / 'build/project-import.json'
    if not path.exists():
        return data
    imported = json.loads(path.read_text(encoding='utf-8'))
    data['projectImport'] = dict(imported['summary'], vectorOnly=True,
        scope='68 représentations vectorielles ; 39 fiches enrichies des repères, mentions de classeur et informations du projet reçu. Les raccordements incertains restent signalés.')
    for board in data['boards']:
        addition = imported['boards'].get(board['id'])
        if addition:
            board['projectImport'] = {key:value for key,value in addition.items() if key!='photos'}
            board['projectImport']['sourceCount'] = len(addition['photos'])
    return data
