"""Compare les cellules du classeur, sans transformer une mention en câble."""
import re
import unicodedata

ALIASES = {'TS17A':'TS17', 'TS17B':'TS17', 'HTA20':'PL20', 'HTA20-DEP':'PL20',
           'INSTR':'ARM110', 'ECLAIRAGE':'ECLSST1', 'POMPES':'PEG'}

def normalize(text):
    return ' '.join(unicodedata.normalize('NFKC', text).split()).casefold()

def compare(incoming, excel):
    known = {}
    for sheet in excel['sheets']:
        name = sheet['sheet']
        known.update({(name, cell): label for cell, label in sheet.get('cells', {}).items()})
        for half in sheet.get('halves', {}).values():
            if half.get('cell'):
                known[name, half['cell']] = half.get('board', '')
            for item in half.get('items', []):
                known[name, item['cell']] = item['label']
        for block in sheet.get('blocks', []):
            if block.get('cell'):
                known[name, block['cell']] = block['header']
            for item in block.get('items', []):
                known[name, item['cell']] = item['label']
    rows = []
    for item in incoming['distribution']:
        old = known.get((item['sheet'], item['cell']))
        state = 'nouveau' if old is None else 'identique' if normalize(old) == normalize(item['text']) else 'ecart'
        match = re.match(r'TR\s+(\d+)', item['sheet'])
        rows.append(dict(item, status=state, previous=old, board='TGBT'+match[1] if match else None))
    return rows

def board_ids(key, boards):
    key = re.sub(r'-SUP$|-PLAQUE$', '', key)
    if key == 'GRADATHYR':
        return ['TGBT8', 'GRADATHYR']
    key = ALIASES.get(key, key)
    return [key] if key in boards else []
