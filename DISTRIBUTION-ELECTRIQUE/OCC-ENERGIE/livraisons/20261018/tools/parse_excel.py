"""Extrait le classeur 'Copie de Distribution.xlsm' en JSON traçable.

Chaque départ garde : onglet, cellule, libellé exact, tableau parent.
Usage : py -3 -I parse_excel.py <xlsm> <out.json>
"""
import sys, json, re, openpyxl

wb = openpyxl.load_workbook(sys.argv[1], data_only=True)
out = {'source': 'Copie de Distribution.xlsm', 'sheets': []}

# Colonnes principales : H = demi-tableau A, L = demi-tableau B (ligne 5 = nom du TGBT)
MAIN = {'H': 'A', 'L': 'B'}

def clean(v):
    return re.sub(r'\s+', ' ', str(v)).strip()

for ws in wb.worksheets:
    cells = {}
    for row in ws.iter_rows():
        for c in row:
            if c.value not in (None, ''):
                cells[(c.column_letter, c.row)] = clean(c.value)
    sh = {'sheet': ws.title.strip(), 'title': cells.get(('H', 1)) or cells.get(('G', 1)),
          'cells': {}, 'halves': {}, 'blocks': []}
    for k in ('E', 'N'):
        sh['cells'][f'{k}2'] = cells.get((k, 2)); sh['cells'][f'{k}3'] = cells.get((k, 3))
    for col, half in MAIN.items():
        name = cells.get((col, 5))
        items = []
        r = 6
        while (col, r) in cells:
            items.append({'cell': f'{col}{r}', 'label': cells[(col, r)]})
            r += 1
        sh['halves'][half] = {'board': name, 'cell': f'{col}5', 'items': items}
    # Blocs secondaires : suite de cellules non vides dans une autre colonne, 1re = en-tête
    used = {(c, r) for c in MAIN for r in range(5, 60) if (c, r) in cells}
    cols = sorted({c for (c, r) in cells if c not in MAIN})
    for col in cols:
        rows = sorted(r for (c, r) in cells if c == col and r >= 6)
        block = []
        for r in rows + [10**6]:
            if block and r != block[-1] + 1:
                hdr = block[0]
                sh['blocks'].append({'header': cells[(col, hdr)], 'cell': f'{col}{hdr}',
                                     'items': [{'cell': f'{col}{x}', 'label': cells[(col, x)]} for x in block[1:]]})
                block = []
            if r < 10**6:
                block.append(r)
    out['sheets'].append(sh)

json.dump(out, open(sys.argv[2], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for s in out['sheets']:
    print(s['sheet'], {h: (v['board'], len(v['items'])) for h, v in s['halves'].items()},
          [(b['cell'], b['header'][:30], len(b['items'])) for b in s['blocks']])
