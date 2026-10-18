"""Extrait les médias embarqués sans exécuter le code du projet reçu."""
import base64
import hashlib
import io
from pathlib import Path
from PIL import Image

def extract(root, incoming, photos, previous_groups):
    target = root / 'assets/import-20261018'
    target.mkdir(exist_ok=True)
    known, added = {}, set()
    for path in root.rglob('*'):
        if path.is_file() and path.suffix.lower() in ('.jpg', '.jpeg', '.png', '.webp'):
            known.setdefault(hashlib.sha256(path.read_bytes()).hexdigest(), path)
    def media(uri):
        header, encoded = uri.split(',', 1)
        payload = base64.b64decode(encoded, validate=True)
        sha = hashlib.sha256(payload).hexdigest()
        path = known.get(sha)
        if path is None:
            ext = '.webp' if 'webp' in header else '.png' if 'png' in header else '.jpg'
            path = target / (sha + ext)
            path.write_bytes(payload)
            known[sha] = path
            added.add(sha)
        with Image.open(io.BytesIO(payload)) as im:
            width, height = im.size
        return dict(href=path.relative_to(root).as_posix(), sha256=sha, w=width, h=height)
    images = []
    for photo in photos:
        row = {k: v for k, v in photo.items() if k != 'data'}
        row.update(media(photo['data']))
        row['sourceGroup'] = photo['b']
        row['board'] = previous_groups.get(photo['sha'], photo['b'])
        row['newToModule'] = photo['sha'] not in previous_groups
        row['groupCorrected'] = row['board'] != photo['b']
        images.append(row)
    docs = []
    for key, document in incoming['docs'].items():
        pages = [dict(page=page['page'], **media(page['uri'])) for page in document['pages']]
        docs.append(dict(id=key, name=document['name'], source=document['source'], pages=pages))
    unif = dict(source=incoming['unif']['source'], text=incoming['unif']['text'], **media(incoming['unif']['uri']))
    layouts = {key: media(uri) for key, uri in incoming.get('planImages', {}).items()}
    return dict(photos=images, documents=docs, unif=unif, layouts=layouts,
                originalSiteImage=media(incoming['siteImage']), addedMedia=len(added))
