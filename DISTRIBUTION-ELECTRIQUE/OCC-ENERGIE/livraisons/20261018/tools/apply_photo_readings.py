"""Applique uniquement les transcriptions visuelles consignées, sans arêtes déduites."""
import json
from pathlib import Path

def apply(data,root):
    path=Path(root)/'build/photo-readings.json'
    if not path.exists():
        return data
    review=json.loads(path.read_text(encoding='utf-8'))
    known={node['id'] for node in data['nodes']}
    data['nodes'].extend(node for node in review['nodes'] if node['id'] not in known)
    nodes={node['id']:node for node in data['nodes']}
    for patch in review.get('nodeReadings',[]):
        nodes[patch['id']]['photoReading']=patch
    boards={board['id']:board for board in data['boards']}
    for patch in review.get('boards',[]):
        board=boards[patch['id']]
        for observation in patch.get('observations',[]):
            if observation not in board.setdefault('obs',[]):
                board['obs'].append(observation)
    data['photoReadingReview']={key:value for key,value in review.items() if key not in ['nodes','boards']}
    return data
