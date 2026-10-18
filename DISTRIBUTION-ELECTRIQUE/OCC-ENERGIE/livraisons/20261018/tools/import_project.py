"""Récupère les données absentes d’un HTML OCC, avec comparaison et provenance."""
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path
from project_assets import extract
from project_compare import compare, board_ids
from project_pages import write_page

root = Path(__file__).resolve().parents[1]
source = Path(sys.argv[1])
text = source.read_text(encoding='utf-8')
incoming = json.loads(re.search(r'window\.OCC_DATA=([\s\S]*?);</script>', text)[1])
photos = json.loads(re.search(r'const PHOTOS=(\[[\s\S]*?\]);', text)[1])
marker = 'const OCC_PLAN_SOURCES='
incoming['planImages'], _ = json.JSONDecoder().raw_decode(text[text.index(marker)+len(marker):])
current = json.loads(re.search(r'window\.OCC_DATA=([\s\S]*?);</script>', (root/'OCC_ENERGIE.html').read_text(encoding='utf-8'))[1])
oldpage = (root/'docs/PHOTOTHEQUE-MODULE.html').read_text(encoding='utf-8')
groups = {}
for group, body in re.findall(r'<section id="([^"]+)">([\s\S]*?)</section>', oldpage):
    groups.update({sha:group for sha in re.findall(r'photos-module/([a-f0-9]+)\.jpg', body)})
catalog = extract(root, incoming, photos, groups)
rows = compare(incoming, json.loads((root/'build/excel.json').read_text(encoding='utf-8')))
boards = {b['id']:dict(photos=[], documents=[], notes=[], distribution=[]) for b in current['boards']}
boards['SANS-AFFECTATION'] = dict(photos=[], documents=[], notes=[], distribution=[])
for photo in catalog['photos']:
    ids = board_ids(photo['board'], boards) or ['SANS-AFFECTATION']
    for key in ids:
        boards[key]['photos'].append(photo)
for document in catalog['documents']:
    ids = board_ids(document['id'], boards) or ['SANS-AFFECTATION']
    for key in ids:
        boards[key]['documents'].append(document)
for row in rows:
    boards.get(row['board'], boards['SANS-AFFECTATION'])['distribution'].append(row)
for relation in incoming['relations']:
    aliases = {'PDL':'PL20', '7PM03':'PEG', '7PM65':'PEG'}
    key = aliases.get(relation['equipment'], relation['equipment'])
    boards.get(key, boards['SANS-AFFECTATION'])['notes'].append(relation)
for location in incoming['nearby']:
    for key in board_ids(location['id'].upper(), boards):
        boards[key]['notes'].append(dict(text=location['position']+f" · zone {location['zone']}", source=location['status']+' — projet reçu'))
summary = dict(source=source.name, sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
    photos=len(photos), documents=len(catalog['documents']), pages=sum(len(d['pages']) for d in catalog['documents']),
    newPhotos=sum(p['newToModule'] for p in catalog['photos']), newCells=sum(r['status']=='nouveau' for r in rows),
    matchingCells=sum(r['status']=='identique' for r in rows), conflictingCells=sum(r['status']=='ecart' for r in rows),
    correctedGroups=sum(p['groupCorrected'] for p in catalog['photos']), addedMedia=catalog['addedMedia'])
summary['scope'] = f"{summary['photos']} photos, {summary['documents']} galeries ({summary['pages']} pages), cinq implantations et 438 références récupérées : {summary['matchingCells']} cellules déjà présentes, {summary['newCells']} intitulés complémentaires. Une photo TS8 supplémentaire. Classements existants préservés ; raccordements non déduits."
catalog.update(boards=boards, summary=summary, distribution=rows)
for field in ['rooms','nearby','relations','supplementary_sources','site','highlights','photos','disclaimer']:
    if field != 'photos':
        catalog[field] = incoming[field]
write_page(root, catalog)
compiled = {key:dict(photos=item['photos'], documentPages=sum(len(d['pages']) for d in item['documents']),
    documentNames=[d['source'] for d in item['documents']], notes=item['notes'], distribution=item['distribution'])
    for key,item in boards.items() if any(item.values()) and key!='SANS-AFFECTATION'}
(root/'build/project-import.json').write_text(json.dumps(dict(summary=summary,boards=compiled),ensure_ascii=False,indent=2),encoding='utf-8')
(root/'build/project-import-catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2),encoding='utf-8')
archive = root/'sources/projects/20261018'
archive.mkdir(parents=True, exist_ok=True)
shutil.copy2(source, archive/source.name)
print(json.dumps(summary,ensure_ascii=False),flush=True)
