"""Applique le fond photographique et son recalage sans modifier le réseau."""
import base64
import json
from pathlib import Path


def apply(data, root):
    root = Path(root)
    source = root / 'build/site-view.json'
    if not source.exists():
        return data
    view = json.loads(source.read_text(encoding='utf-8'))
    image = root / view.pop('image')
    view['img'] = 'data:image/webp;base64,' + base64.b64encode(image.read_bytes()).decode()
    view['poly'] = None
    data['site'] = view
    return data
