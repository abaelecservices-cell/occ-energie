"""Construit build/data.json : modèle de graphe + inventaire + façades + registre.

Règles :
- chaque nœud / arête porte `src` (document + repère) et `conf` :
  'confirme' (lu sur document/plaque), 'probable' (déduit, cohérent), 'a_verifier'
  (contradiction ou hypothèse), 'inconnu'.
- aucune valeur inventée : champs inconnus absents -> l'interface affiche « Non documenté ».
Usage : py -3 -I build_data.py <excel.json> <out.json>
"""
import sys, json, re, unicodedata

EX = json.load(open(sys.argv[1], encoding='utf-8'))
OUT = sys.argv[2]

UNI = 'schema unifilaire 20 KV derniere version.pdf'  # Owens Corning R112529 rév. H
XL = 'Copie de Distribution.xlsm'
T2DOC = 'p1.zip › 11_TGBT N°2 › plan mise a jour TGBT N°2 (Bronzini).pdf'
T3DOC = 'p1 - Copie.zip › 12_TGBT N°3 › CX7810_C TQC.PDF'
T3LOCK = 'p1 - Copie.zip › 12_TGBT N°3 › Verrouillage DJ TR3A.pdf'
T1RPT = 'p1.zip › 10_TGBT N°1 › OnSite_TechRpt_WO-12101777.pdf'

nodes, edges, boards, deps, issues = {}, [], {}, {}, []

def N(id, t, label, **kw):
    assert id not in nodes, id
    nodes[id] = dict(id=id, t=t, label=label, **kw)
    return id

def E(a, b, src=None, conf='confirme', note=None):
    e = dict(a=a, b=b, conf=conf)
    if src: e['src'] = src
    if note: e['note'] = note
    edges.append(e)

def ISSUE(id, sev, title, text, refs=(), ents=()):
    issues.append(dict(id=id, sev=sev, title=title, text=text, refs=list(refs), ents=list(ents)))

def slug(s):
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^A-Za-z0-9]+', '', s).upper()

# --------------------------------------------------------------------------- sites
LOC = {
 'SITE': dict(name='Usine OCF — Laudun-l’Ardoise', parent=None, kind='site'),
 'PL': dict(name='Poste de livraison 20 kV', parent='SITE', kind='poste', note='Point de livraison commun CNR / EDF (unifilaire R112529).'),
 'SS1': dict(name='Sous-station 1', parent='SITE', kind='poste', note='Divisée en partie gauche et partie droite séparées par un sas (indication utilisateur). Implantation détaillée : PowerPoint non fourni.'),
 'SS1G': dict(name='SS1 — partie gauche', parent='SS1', kind='salle'),
 'SS1S': dict(name='SS1 — sas / passage', parent='SS1', kind='sas'),
 'SS1D': dict(name='SS1 — partie droite', parent='SS1', kind='salle'),
 'SS2': dict(name='Sous-station 2', parent='SITE', kind='poste', note='Rangées en vis-à-vis (indication utilisateur). Implantation détaillée : PowerPoint non fourni.'),
 'TERRAIN': dict(name='Tableaux disséminés sur site', parent='SITE', kind='zone', note='Positions à reporter sur la vue aérienne (captures Google Earth non fournies).'),
}

# --------------------------------------------------------------------------- HTA
N('SRC_EDF', 'src', 'EDF — source SECOURS', loc='PL', conf='confirme', src=f'{UNI} « A - SECOURS EDF »')
N('SRC_CNR', 'src', 'CNR — source NORMALE', loc='PL', conf='confirme', src=f'{UNI} « B - NORMAL CNR »')

def cb_hta(id, label, board, prot=None, **kw):
    return N(id, 'cb', label, board=board, kind='HTA', prot=prot, **kw)

# Poste de livraison
cb_hta('PL_A04', 'Disjoncteur arrivée EDF (cellule A, repère 04)', 'PL20',
       prot='DISJ. SF1 400A 24 kV 12,5 kA — TC 400/5-5A — relais S2036 (S03) : I>440A SIT 1,5 s à 10Is ; I>>600A DT 0,65 s ; Io=30A DT 0,65 s',
       cell='CS-400A — Sch. 3182344', keys='A · 04 · A2', conf='confirme', src=UNI)
cb_hta('PL_B01', 'Disjoncteur arrivée CNR (cellule B, repère 01)', 'PL20',
       prot='DISJ. SF1 400A 24 kV 12,5 kA — TC 400/5-5A — relais S2036 (S03) : I>440A SIT 1,5 s à 10Is ; I>>600A DT 0,65 s ; Io=30A DT 0,65 s',
       cell='CS-400A — Sch. 3182346', keys='B · 01 · B2', conf='confirme', src=UNI)
E('SRC_EDF', 'PL_A04', UNI); E('SRC_CNR', 'PL_B01', UNI)

# SS1 20 kV : demi-JdB gauche (arrivée A1 depuis EDF) / droite (arrivée A2 depuis CNR), couplage V500
N('SS1_BL', 'bus', 'SS1 20 kV — demi-JdB gauche', board='SS1_20', conf='confirme', src=UNI)
N('SS1_BR', 'bus', 'SS1 20 kV — demi-JdB droit', board='SS1_20', conf='confirme', src=UNI)
N('SS1_A1', 'sw', 'Arrivée A1 (A1E / A1C)', board='SS1_20', kind='HTA', cell='Interrupteur-sectionneur + MALT', keys='A1E · A1C', conf='confirme', src=UNI)
N('SS1_A2', 'sw', 'Arrivée A2 (A2E / A2C)', board='SS1_20', kind='HTA', cell='Interrupteur-sectionneur + MALT', keys='A2E · A2C', conf='confirme', src=UNI)
N('SS1_V500', 'cpl', 'Couplage V500 SS1', board='SS1_20', kind='HTA', cell='2 cellules de couplage (V500)', conf='confirme', src=UNI,
  note='Clés d’interverrouillage relevées en tête de tableau : A2 A1E A3E A1C A3C A1 / B2 A4E A2E A4C A2C B1. Logique de verrouillage non décrite sur l’unifilaire.')
E('PL_A04', 'SS1_A1', UNI, note='Câble pointillé A → A1E (tracé unifilaire)'); E('SS1_A1', 'SS1_BL', UNI)
E('PL_B01', 'SS1_A2', UNI, note='Câble pointillé B → A2E'); E('SS1_A2', 'SS1_BR', UNI)
E('SS1_BL', 'SS1_V500', UNI); E('SS1_V500', 'SS1_BR', UNI)

# SS2 20 kV
N('SS2_BL', 'bus', 'SS2 20 kV — demi-JdB gauche', board='SS2_20', conf='confirme', src=UNI)
N('SS2_BR', 'bus', 'SS2 20 kV — demi-JdB droit', board='SS2_20', conf='confirme', src=UNI)
N('SS2_A3', 'sw', 'Arrivée A3 (A3E / A3C)', board='SS2_20', kind='HTA', keys='A3E · A3C', conf='confirme', src=UNI)
N('SS2_A4', 'sw', 'Arrivée A4 (A4E / A4C)', board='SS2_20', kind='HTA', keys='A4E · A4C', conf='confirme', src=UNI)
N('SS2_CPL', 'cpl', 'Couplage SS2 20 kV', board='SS2_20', kind='HTA', cell='2 cellules de couplage', conf='confirme', src=UNI)
E('PL_A04', 'SS2_A3', UNI, note='Câble pointillé A → A3E'); E('SS2_A3', 'SS2_BL', UNI)
E('PL_B01', 'SS2_A4', UNI, note='Câble pointillé B → A4E'); E('SS2_A4', 'SS2_BR', UNI)
E('SS2_BL', 'SS2_CPL', UNI); E('SS2_CPL', 'SS2_BR', UNI)

TR = {}  # id -> dict
def transfo(id, kva, u2, cooling, bus, cell_id, cell_label, prot, lv=None, dest=None, loc_hta=None, conf='confirme', extra=None):
    cb_hta(cell_id, cell_label, loc_hta, prot=prot, conf='confirme', src=UNI, **(extra or {}))
    E(bus, cell_id, UNI)
    N(id, 'tr', id.replace('TR', 'TR '), kva=kva, u='20 kV / ' + u2, ucc='6 %' if id not in ('AEF2-TR1',) else '7 %',
      cooling=cooling, conf='confirme', src=UNI, board=loc_hta)
    E(cell_id, id, UNI, note='Câble 3x70 mm² Cu' if 'TR' in id[:2] else None)
    TR[id] = dict(lv=lv, dest=dest)

P55 = 'DISJ. SF1 400A 24 kV — TC 50-100/5-5A — S2036 (T14) : I>55A SIT 2 s à 10Is ; I>>500A DT 0,4 s ; Io=20A DT 0,4 s'
P70 = 'DISJ. SF1 400A 24 kV — TC 50-100/5-5A — S2036 (T14) : I>70A SIT 2 s à 10Is ; I>>500A DT 0,4 s ; Io=20A DT 0,4 s'
# SS1 gauche (ordre unifilaire de gauche à droite)
transfo('TR6A', '2000 kVA', '410 V', 'Sondes (sec probable)', 'SS1_BL', 'SS1_C6A', 'Cellule TR 6A (repère 010)', P70.replace('T14', 'T14 — ITH 25 kA'), lv='M32H1 STR58U', dest='TGBT 6', loc_hta='SS1_20', extra=dict(cell='Sch. 3298882'))
transfo('TR5A', '2000 kVA', '410 V', 'Sondes', 'SS1_BL', 'SS1_C5A', 'Cellule TR 5A (repère 010)', P55.replace('S2036', 'S2035'), lv='M32H1 STR38S', dest='TGBT 5', loc_hta='SS1_20')
transfo('TR4A', '2000 kVA', '410 V', 'Sondes', 'SS1_BL', 'SS1_C4A', 'Cellule TR 4A (repère 01)', P55, lv='M32H1 Micrologic 5.0A', dest='TGBT 4', loc_hta='SS1_20', extra=dict(cell='Sch. 3183407'))
transfo('TR3A', '2000 kVA', '410 V', 'Sondes', 'SS1_BL', 'SS1_C3A', 'Cellule TR 3A (repère 02)', P55, lv='Non indiqué sur unifilaire (MTZ2 40H1 selon plan TGBT3)', dest='TGBT 3', loc_hta='SS1_20', extra=dict(cell='Sch. 3183406'))
transfo('TR1A', '2000 kVA', '410 V', 'Sondes', 'SS1_BL', 'SS1_C1A', 'Cellule TR 1A (repère 01A)', P55, lv='NW32H1 Micrologic 5.0P', dest='TGBT 1A (unifilaire : « vers TGBT 2 »)', loc_hta='SS1_20', extra=dict(cell='Sch. 3275157'))
transfo('TR2A', '2000 kVA', '410 V', 'DGPT2 (immergé probable)', 'SS1_BL', 'SS1_C2A', 'Cellule TR 2A (repère 02A)', P55, lv='Non indiqué', dest='TGBT 2A (unifilaire : « vers TGBT 1 »)', loc_hta='SS1_20', extra=dict(cell='Sch. 3275158'))
# SS1 droite
transfo('TR1B', '2000 kVA', '410 V', 'DGPT2', 'SS1_BR', 'SS1_C1B', 'Cellule TR 1B (repère 01)', P55, lv='DA3200', dest='TGBT 1', loc_hta='SS1_20', extra=dict(cell='Sch. 3183027'))
transfo('TR2B', '2000 kVA', '410 V', 'DGPT2', 'SS1_BR', 'SS1_C2B', 'Cellule TR 2B (repère 02)', P55, lv='DA3200', dest='TGBT 2', loc_hta='SS1_20', extra=dict(cell='Sch. 3182851'))
transfo('TR3B', '2000 kVA', '410 V', 'DGPT2', 'SS1_BR', 'SS1_C3B', 'Cellule TR 3B (repère 03)', P55.replace('I>>500A', 'I>>300A'), lv='Non indiqué', dest='TGBT 3', loc_hta='SS1_20', extra=dict(cell='Sch. 3183086'))
transfo('TR4B', '2000 kVA', '410 V', 'DGPT2', 'SS1_BR', 'SS1_C4B', 'Cellule TR 4B (repère 04)', P55, lv='M32H1 Micrologic 5.0A', dest='TGBT 4', loc_hta='SS1_20', extra=dict(cell='Sch. 3183087'))
transfo('TR5B', '1600 kVA', '410 V', 'Sondes', 'SS1_BR', 'SS1_C5B', 'Cellule TR 5B (repère 020)', 'Interrupteur-fusible / disjoncteur STRN 400A (« 23-25B 400A ») — TCR3 — S2035 (T14) : I>70A SIT 2 s ; I>>500A DT 0,4 s ; Io=20A', lv='M32H1 STR38S', dest='TGBT 5', loc_hta='SS1_20', extra=dict(cell='Sch. E03933'))
transfo('TR6B', '2000 kVA', '410 V', 'Sondes', 'SS1_BR', 'SS1_C6B', 'Cellule TR 6B', 'Réglages : se reporter à l’unifilaire (bord droit, lecture à confirmer)', lv='Non lu', dest='TGBT 6', loc_hta='SS1_20', extra=dict(cell='Sch. 3298882'))

# SS2 20 kV gauche
transfo('TR-HYD', 'Non indiqué', 'Non indiqué', 'Non indiqué', 'SS2_BL', 'SS2_CHYD', 'Cellule TR Hydrogène (repères Sx / ELxxx non renseignés)', 'Réglages non renseignés sur l’unifilaire (Sxxxx/Mxx)', dest='TR Hydrogène', loc_hta='SS2_20')
transfo('AEF1-TRZ2', '900 kVA', '350 V', 'Non indiqué', 'SS2_BL', 'SS2_CZ2', 'Cellule AEF1-TRZ2 (B&B)', 'TC 100-200/5-5A — réglages non renseignés (I>xxA EIT)', dest='Électrodes zone 2', loc_hta='SS2_20')
transfo('AEF2-TR2', '3600/5000 kVA', '6000 V', 'Sondes', 'SS2_BL', 'SS2_CBT2', 'Cellule AEF2-TR2 Boosting T2', 'TC 100-200/5-5A — réglages non renseignés — câble 3x1x95² Al POPY N/G', dest='Tableau 6 kV Four 2 (AEF2-A2)', loc_hta='SS2_20')
transfo('TR9A', '2000/2500 kVA', '410 V', 'Sondes', 'SS2_BL', 'SS2_C9A', 'Cellule TR 9A (repère 01, S1)', 'DISJ. SF1 400A — S2036 (M15) : I>55A EIT 2 s à 10Is ; I>>300A DT 0,4 s ; Io=20A DT 0,4 s', lv='NW40H1 Micrologic 5.0A', dest='Nouveau TGBT 9', loc_hta='SS2_20', extra=dict(cell='Sch. 3182583'))
transfo('TR7A', '2000 kVA', '410 V', 'Sondes', 'SS2_BL', 'SS2_C7A', 'Cellule TR 7A (repère 02, S2)', 'DISJ. SF1 400A — S2036 (T14) : I>70A SIT 2 s à 10Is ; I>>500A DT 0,4 s ; Io=20A', lv='NW40H1 Micrologic 5.0A', dest='TGBT 7', loc_hta='SS2_20', extra=dict(cell='Sch. 3182586'))
transfo('TR8A', '3200 kVA', '480 V', 'Sondes', 'SS2_BL', 'SS2_CB1', 'Cellule BOOSTING 3200 kVA gauche (repère 03, S3)', 'DISJ. SF1 400A — S2036 (T15) : I>110A SIT 2 s à 10Is ; I>>500A DT 0,4 s ; Io=20A', dest='Boosting Four 1 (TGBT 8A probable)', loc_hta='SS2_20', extra=dict(cell='Sch. 3182584', alias='BOOSTING 3200 kVA (S3)'))
# SS2 20 kV droite
transfo('TR8B', '3200 kVA', '480 V', 'Sondes', 'SS2_BR', 'SS2_CB2', 'Cellule BOOSTING 3200 kVA droite (repère 012, S12)', 'DISJ. SF1 400A — S2036 (T15) : I>110A SIT 2 s à 10Is ; I>>500A DT 0,4 s ; Io=20A', dest='Boosting Four 1 (TGBT 8B probable)', loc_hta='SS2_20', extra=dict(cell='Sch. 3182750', alias='BOOSTING 3200 kVA (S12)'))
transfo('TR7B', '2000 kVA', '410 V', 'Sondes', 'SS2_BR', 'SS2_C7B', 'Cellule TR 7B (repère 01, S13)', 'DISJ. SF1 400A — S2036 (T14) : I>70A SIT 2 s à 10Is ; I>>500A DT 0,4 s ; Io=20A', dest='TGBT 7', loc_hta='SS2_20', extra=dict(cell='Sch. 3182752'))
transfo('TR9B', '2000/2500 kVA', '410 V', 'Sondes', 'SS2_BR', 'SS2_C9B', 'Cellule TR 9B', 'TC 50-100/5-5A — I>55A EIT 2 s ; I>>300A DT 0,4 s ; Io=20A (repères xx non renseignés)', lv='NW40H1 Micrologic 5.0A', dest='Nouveau TGBT 9', loc_hta='SS2_20')
transfo('AEF2-TR1', '3600/5000 kVA', '6000 V', 'Sondes', 'SS2_BR', 'SS2_CBT1', 'Cellule AEF2-TR1 Boosting T1', 'TC 100-200/5-5A — réglages non renseignés — câble 3x1x95² Al POPY N/G (002)', dest='Tableau 6 kV Four 2 (AEF2-A1)', loc_hta='SS2_20')
transfo('AEF1-TRZ1', '900 kVA', '350 V', 'Non indiqué', 'SS2_BR', 'SS2_CZ1', 'Cellule AEF1-TRZ1 (B&B)', 'TC 100-200/5-5A — réglages non renseignés', dest='Électrodes zone 1', loc_hta='SS2_20')

for z, tr in (('Z2', 'AEF1-TRZ2'), ('Z1', 'AEF1-TRZ1')):
    N(f'ELEC_{z}', 'load', f'Électrodes zone {z[1]} (B&B)', conf='confirme', src=UNI, board=None)
    E(tr, f'ELEC_{z}', UNI)
N('LOAD_HYD', 'load', 'TR Hydrogène — utilisation aval non documentée', conf='inconnu', src=UNI)
E('TR-HYD', 'LOAD_HYD', UNI, conf='inconnu')

# 6 kV Four 2
N('KV6_BL', 'bus', '6 kV Four 2 — demi-JdB gauche', board='KV6', conf='confirme', src=UNI)
N('KV6_BR', 'bus', '6 kV Four 2 — demi-JdB droit', board='KV6', conf='confirme', src=UNI)
cb_hta('KV6_A2', 'Arrivée AEF2-A2 (disj. SF1 400A 7,2 kV)', 'KV6', prot='TC 300-600/5-5A — réglages non renseignés (I>xxA EIT)', conf='confirme', src=UNI)
cb_hta('KV6_A1', 'Arrivée AEF2-A1 (disj. SF1 400A 7,2 kV)', 'KV6', prot='TC 300-600/5-5A — réglages non renseignés', conf='confirme', src=UNI)
N('KV6_C', 'cpl', 'Couplage AEF2-C (6 kV)', board='KV6', kind='HTA', cell='Interrupteur de couplage', conf='confirme', src=UNI)
E('AEF2-TR2', 'KV6_A2', UNI); E('KV6_A2', 'KV6_BL', UNI)
E('AEF2-TR1', 'KV6_A1', UNI); E('KV6_A1', 'KV6_BR', UNI)
E('KV6_BL', 'KV6_C', UNI); E('KV6_C', 'KV6_BR', UNI)
for d, bus in (('D6', 'KV6_BL'), ('D5', 'KV6_BL'), ('D4', 'KV6_BL'), ('D3', 'KV6_BR'), ('D2', 'KV6_BR'), ('D1', 'KV6_BR')):
    n = d[1]
    N(f'KV6_{d}', 'dep', f'AEF2-{d} → Armoire SPANG ligne {n}', board='KV6', half='G' if bus == 'KV6_BL' else 'D',
      model='Interrupteur-fusible 200 A', conf='confirme', src=UNI)
    E(bus, f'KV6_{d}', UNI)
    N(f'SPANG{n}', 'load', f'Armoire SPANG ligne {n} (Four 2)', conf='confirme', src=UNI)
    E(f'KV6_{d}', f'SPANG{n}', UNI)

# --------------------------------------------------------------------------- BT : TGBT
TGBT = {}
def tgbt(n, loc, loc_conf, style, coupler, cpl_rule=None, cpl_src=None, note=None, photos=(), docs=(), facade=None, sap=None, it=None):
    b = f'TGBT{n}'
    TGBT[n] = b
    boards[b] = dict(id=b, name=f'TGBT {n}', kind='TGBT', loc=loc, loc_conf=loc_conf, style=style,
                     halves=[dict(id=f'{b}A', label=f'TGBT {n}A'), dict(id=f'{b}B', label=f'TGBT {n}B')],
                     coupler=dict(status=coupler, rule=cpl_rule, src=cpl_src), note=note, photos=list(photos),
                     docs=list(docs), facade=facade, sap=sap, it=it)
    N(f'{b}A', 'bus', f'TGBT {n}A — jeu de barres A', board=b, half='A', conf='confirme', src=XL)
    N(f'{b}B', 'bus', f'TGBT {n}B — jeu de barres B', board=b, half='B', conf='confirme', src=XL)
    return b

def arrivals(b, n, qa_label, qb_label, tra, trb, conf_a='confirme', conf_b='confirme', src=None, qa_extra=None, qb_extra=None):
    N(f'{b}_QA', 'cb', qa_label, board=b, half='A', role='arrivee', conf=conf_a, src=src or UNI, **(qa_extra or {}))
    N(f'{b}_QB', 'cb', qb_label, board=b, half='B', role='arrivee', conf=conf_b, src=src or UNI, **(qb_extra or {}))
    E(tra, f'{b}_QA', UNI, conf=conf_a); E(f'{b}_QA', f'{b}A', src or UNI)
    E(trb, f'{b}_QB', UNI, conf=conf_b); E(f'{b}_QB', f'{b}B', src or UNI)

def coupler(b, label, conf, src, **kw):
    N(f'{b}_QC', 'cpl', label, board=b, role='couplage', conf=conf, src=src, **kw)
    E(f'{b}A', f'{b}_QC', src, conf=conf); E(f'{b}_QC', f'{b}B', src, conf=conf)

ROLL = 'Clés Ronis : « CHOIX DE SOURCE — PERMUTATION DES SOURCES À LA CHARGE DE L’EXPLOITANT ». Tableau de vérité QTR1 / QC / QTR2 : 1-0-1, 0-1-1, 1-1-0 (jamais 3 appareils fermés).'

# TGBT 1
b = tgbt(1, 'SS1', 'confirme', 'okken_beige', 'non_documente', note='Okken beige Merlin Gerin (photos). Neutre IT : 2 contrôleurs d’isolement IM400C + localisateurs IFL12 mis en service le 29/10/2024 (préalarme 30 kΩ, alarme 2 kΩ, inhibition partie droite si passage sur couplage).',
         photos=['Tgbt 1.pdf p1-p13'], docs=[T1RPT, 'p1.zip › TGBT1A.pdf (28 p., scanné)', 'p1.zip › TH11A-TGBT1B.pdf (65 p., scanné)'], sap='42922+42921 (lecture partielle photo p1)', it='IM400C + IFL12 (x2) — PAS600 RS485')
arrivals(b, 1, 'Arrivée TGBT 1A (TR 1A)', 'Arrivée TGBT 1B — DA3200 (TR 1B)', 'TR1A', 'TR1B', src='Exploitant : « chaque TGBT a des transfos qui portent leur nom A et B » ; Excel TR 1A & 1B')
coupler(b, 'Couplage TGBT 1A-1B (présent sur photos, repère non relevé)', 'probable', 'Photos Tgbt 1 + rapport WO-12101777 (« passage sur le couplage »)')
ISSUE('I-TR12', 'moyenne', 'Repères « VERS TGBT » inversés sur l’unifilaire (TR 1A / TR 2A)',
      'L’unifilaire 20 kV (R112529 rév. H) porte sous la cellule « TR 1A » la mention « VERS TGBT 2 » et sous « TR 2A » « VERS TGBT 1 ». '
      'Règle donnée par l’exploitant : chaque TGBT n est alimenté par les transformateurs TR nA et TR nB (cohérent avec l’Excel et le plan Schneider TGBT 2 « ARRIVÉE TRANSFO TR2A »). '
      'Le modèle applique TR 1A → TGBT 1A et TR 2A → TGBT 2A. Reste à vérifier que les cellules HTA repérées « TR 1A » / « TR 2A » sur le tableau 20 kV alimentent bien ces transformateurs (étiquettes de cellule).',
      [UNI, XL, T2DOC], ['TR1A', 'TR2A', 'TGBT1', 'TGBT2'])

# TGBT 2
b = tgbt(2, None, 'inconnu', 'okken_blanc', 'documente', cpl_rule='Couplage NW40HA 4P case 4-53 entre arrivées TR2A (3-28) et TR2B (5-28). Règle d’interverrouillage non lue dans le dossier (folios 060-069 couplage).',
         cpl_src=T2DOC, note='Okken blanc RAL 9001 (photos). Plan Schneider TH112001 mis à jour le 15/10/2024 (ajout départ Bâtiment Bronzini).',
         photos=['Tgbt 2.pdf p1-p11'], docs=[T2DOC], facade='TGBT2', sap='42930+42931 (photo p4)')
arrivals(b, 2, 'Arrivée TR2A — NW40H1 4P Micrologic 5.0P (case 3-28)', 'Arrivée TR2B — NW40H1 4P Micrologic 5.0P (case 5-28)', 'TR2A', 'TR2B',
         src=T2DOC, qa_extra=dict(case='3-28', model='NW40H1 4P 5.0P', ir='2887 A'), qb_extra=dict(case='5-28', model='NW40H1 4P 5.0P', ir='2887 A'))
coupler(b, 'Couplage TGBT 2 — NW40HA 4P (case 4-53)', 'confirme', T2DOC, case='4-53', model='NW40HA 4P')

# TGBT 3
b = tgbt(3, 'SS2', 'probable', 'okken_blanc_vert', 'documente', cpl_rule=ROLL, cpl_src=T3DOC,
         note='Okken (plan CX781001) — façade blanche à bandeau vert (photos). Cartouche du plan : « SOUS-STATION 2 » alors que TR3A/TR3B sont alimentés par le tableau 20 kV SS1. Pas d’onglet TR3 dans le classeur Excel.',
         photos=['Tgbt 3.pdf p1-p8', 'Tgbt 3 (2).pdf p1-p16'], docs=[T3DOC, T3LOCK, 'p1 - Copie.zip › Verrouillage DJ TR3B.pdf (scan transcrit)', 'TR2/TR3 Plan d’ensemble, essais individuels (p1 - Copie.zip)', 'Gaine à barres p46268'],
         facade='TGBT3', it='IM400 + IFL12MC (x2)')
arrivals(b, 3, 'Arrivée TR3A — QTR3A MTZ2 40H1 4P Micrologic 5.0X (case 3+28)', 'Arrivée TR3B — QTR3B MTZ2 40H1 4P (case 4+28)', 'TR3A', 'TR3B', src=T3DOC,
         qa_extra=dict(case='3+28', model='MTZ2 40H1 4P', ir='2887 A', keys='A3A (Ronis)'), qb_extra=dict(case='4+28', model='MTZ2 40H1 4P', ir='2887 A'))
coupler(b, 'Couplage QC — MTZ2 40HA 4P (case 3+53)', 'confirme', T3DOC, case='3+53', model='MTZ2 40HA 4P')
ISSUE('I-TGBT3-XL', 'moyenne', 'TGBT 3 absent du classeur Excel', 'Le classeur ne contient aucun onglet « TR 3A & 3B ». Les départs du TGBT 3 proviennent uniquement du dossier Schneider CX7810 (liste des consommateurs).', [XL, T3DOC], ['TGBT3'])
ISSUE('I-TR-KVA', 'basse', 'Puissance TR2/TR3 : 2000 ou 2500 kVA', 'Les plans Schneider TGBT 2 et 3 indiquent « 2000 kVA (2500 kVA) » et dimensionnent les arrivées pour 3520 A ; l’unifilaire indique 2000 kVA. Les documents « 149288_1466597/1466588 » (TR2, TR3) sont à consulter pour la plaque.', [UNI, T2DOC, T3DOC], ['TR2A', 'TR2B', 'TR3A', 'TR3B'])

# TGBT 4
b = tgbt(4, 'SS1', 'probable', 'okken_beige', 'documente', cpl_rule='Couplage « TR 4A - TR 4B » case 4-53 (étiquette rouge, photo Tgbt 4 p11). Règle d’interverrouillage non documentée.', cpl_src='Tgbt 4.pdf p9, p11',
         note='Merlin Gerin Okken beige. Plaque « TGBT N°4 — SAP : 42933+42934 ». Étiquettes « SST 1 » sur plusieurs départs → implantation SS1 probable. Contrôleurs d’isolement Vigilohm IM400 sur chaque demi-jeu de barres (lectures 100 kΩ et 21 kΩ au moment des photos).',
         photos=['Tgbt 4.pdf p1-p12'], facade='TGBT4', sap='42933+42934', it='Vigilohm IM400 (x2)')
arrivals(b, 4, '« PROVIENT DE TR 4A — ARRIVÉE TGBT 4A » case 3-28 (Masterpact NW)', '« PROVIENT DE TR 4B — ARRIVÉE TGBT 4B » case 6-28 (Masterpact NW)', 'TR4A', 'TR4B',
         src='Tgbt 4.pdf p11 / p9', qa_extra=dict(case='3-28', model='Masterpact NW (probable, Micrologic)'), qb_extra=dict(case='6-28', model='Masterpact NW (probable)'))
coupler(b, '« COUPLAGE TR 4A - TR 4B » case 4-53', 'confirme', 'Tgbt 4.pdf p9, p11', case='4-53', model='Masterpact NW (probable)')

# TGBT 5, 6, 7, 9 : Excel + photos ; TGBT 8 : boosting
b = tgbt(5, None, 'inconnu', 'okken_blanc', 'non_documente', note='Okken blanc (photos). Plaque « TGBT N°5 » visible (SAP partiellement lisible).', photos=['Tgbt 5.pdf p1-p18'])
arrivals(b, 5, 'Arrivée TGBT 5A (TR 5A — M32H1 STR38S)', 'Arrivée TGBT 5B (TR 5B 1600 kVA — M32H1 STR38S)', 'TR5A', 'TR5B')
coupler(b, 'Couplage TGBT 5 (symbole visible sur photos, non documenté)', 'probable', 'Tgbt 5.pdf p5-p6')
b = tgbt(6, None, 'inconnu', 'okken_blanc', 'non_documente', note='Okken blanc (photos).', photos=['Tgbt 6.pdf p1-p21'])
arrivals(b, 6, 'Arrivée TGBT 6A (TR 6A — M32H1 STR58U)', 'Arrivée TGBT 6B (TR 6B)', 'TR6A', 'TR6B')
coupler(b, 'Couplage TGBT 6 (symbole visible sur photos, non documenté)', 'probable', 'Tgbt 6.pdf p3-p7')
b = tgbt(7, 'SS2', 'probable', 'okken_blanc', 'non_documente', note='Onglet Excel « TR 7A & 7B » titré « Sous/station n°2 ». Photos « Tr7b.pdf » : étiquettes arc « TABLEAU TR7A TOUR BALTIMORE » et « TABLEAU TR7A AUXILIAIRES ».', photos=['Tr7b .pdf p1-p20', '24 V et 230 V tr7b.pdf'])
arrivals(b, 7, 'Arrivée TGBT 7A (TR 7A — NW40H1 Micrologic 5.0A)', 'Arrivée TGBT 7B (TR 7B)', 'TR7A', 'TR7B')
coupler(b, 'Couplage TGBT 7 (non documenté)', 'inconnu', 'aucun')
b = tgbt(8, 'SS2', 'probable', None, 'non_documente', note='Onglet « TR 8A & 8B » : « Boosting Four 1 Sous/Station 2 », départs ZONE 1 à 6. Rattachement aux 2 transformateurs BOOSTING 3200 kVA 480 V de l’unifilaire = probable (non nommés TR 8A/8B sur le schéma).', photos=[])
arrivals(b, 8, 'Arrivée TGBT 8A (Boosting 3200 kVA S3) — probable', 'Arrivée TGBT 8B (Boosting 3200 kVA S12) — probable', 'TR8A', 'TR8B', conf_a='probable', conf_b='probable')
coupler(b, 'Couplage TGBT 8 (non documenté)', 'inconnu', 'aucun')
b = tgbt(9, 'SS1', 'a_verifier', 'okken_blanc', 'non_documente', note='« Nouveau TGBT 9 » alimenté par TR 9A / TR 9B (2000/2500 kVA) depuis le tableau 20 kV SS2 (unifilaire). Implantation en SS1 selon indication utilisateur — à confirmer.', photos=['Tgbt 9.pdf p1-p24'])
arrivals(b, 9, 'Arrivée TGBT 9A (TR 9A — NW40H1 Micrologic 5.0A)', 'Arrivée TGBT 9B (TR 9B — NW40H1 Micrologic 5.0A)', 'TR9A', 'TR9B')
coupler(b, 'Couplage TGBT 9 (symbole visible sur photos, non documenté)', 'probable', 'Tgbt 9.pdf p5-p9')
ISSUE('I-LOC', 'moyenne', 'Implantation physique des TGBT', 'Le PowerPoint d’implantation n’a pas été transmis. Localisations retenues : TGBT 1 SS1 (rapport Schneider 2024), TGBT 4 SS1 (étiquettes « SST 1 », probable), TGBT 3 SS2 (cartouche plan), TGBT 7/8 SS2 (classeur), TGBT 9 SS1 (indication utilisateur, à confirmer). TGBT 2, 5, 6 : non localisés.', [], ['TGBT1', 'TGBT2', 'TGBT3', 'TGBT4', 'TGBT5', 'TGBT6', 'TGBT7', 'TGBT8', 'TGBT9'])

# --------------------------------------------------------------------------- départs
def dep(board, half, label, src, conf='confirme', case=None, model=None, ir=None, xl=None, rep=None, feeds=None, meter=None, plate=None, note=None, idx=[0]):
    idx[0] += 1
    id = f'D{idx[0]:04d}'
    bus = f'{board}{half}' if board in boards and half in ('A', 'B') else half
    N(id, 'dep', label, board=board, half=half, case=case, model=model, ir=ir, xl=xl, rep=rep, conf=conf, src=src, meter=meter, plate=plate, note=note)
    deps[id] = nodes[id]
    E(bus, id, src, conf=conf)
    if feeds:
        nodes[id]['feeds'] = feeds
    return id

def xlref(sheet, cell):
    return f'{XL} › onglet « {sheet} » › {cell}'

SHEETS = {s['sheet']: s for s in EX['sheets']}
XL_USED = set()

def xl_item(sheet, cell):
    s = SHEETS[sheet]
    for h in s['halves'].values():
        for it in h['items']:
            if it['cell'] == cell: return it['label']
    for bl in s['blocks']:
        if bl['cell'] == cell: return bl['header']
        for it in bl['items']:
            if it['cell'] == cell: return it['label']
    raise KeyError((sheet, cell))

# --- TGBT 2 : dossier Schneider (cases) + correspondances Excel
S2 = 'TR 2A & 2B'
T2 = [
 ('A', '1-28', 'DIV002 — RÉSERVE', 'NS800H 4P Micrologic 5.0A', '800 A', None),
 ('A', '1-53', 'DIV001 — TABLEAU ÉTUVE 7-8-9', 'NS1000H 4P 5.0A', 'Ir 450 A', 'H10'),
 ('A', '1-72', 'COND001 — BATTERIE CONDENSATEURS 350 kVAR', 'NS800H 3P 5.0A', 'Ir 758 A', 'H7'),
 ('A', '2-18', 'TD002 — TS44A AUXILIAIRES FOUR 01', 'NS1250H 4P 5.0A', 'Ir 1250 A', 'H9'),
 ('A', '2-36', 'TD001 — TS2A ÉTUVE S/STATION', 'NS1000H 4P 5.0A', 'Ir 800 A', 'H8'),
 ('A', '2-43', 'C_001 — SOUS-DISTRIBUTION DES AUXILIAIRES', 'NSX160H 4P Micrologic 2.2 160A', '160 A', 'H12'),
 ('A', '2-51', 'MULTICLIP 1 (200 A)', 'Multiclip 4P', None, None),
 ('A', '2-72', 'DIV003 — RÉSERVE', 'NSX630H 4P Micrologic 2.3', 'Ir 520 A', None),
 ('B', '6-18', 'TD001 — TS2B ÉTUVES S/STATION', 'NS1000H 4P 5.0A', 'Ir 800 A', 'L6'),
 ('B', '6-36', 'DIV001 — TS12 ROVING', 'NS1000H 4P 5.0A', 'Ir 900 A', 'L7'),
 ('B', '6-43', 'DIV007 — SOUS-DISTRIBUTION DES AUXILIAIRES', 'NSX160H 4P Micrologic 2.2 160A', '160 A', 'L10'),
 ('B', '6-51', 'MULTICLIP 2 (200 A)', 'Multiclip 4P', None, None),
 ('B', '6-72', 'DIV005 — RÉSERVE', 'NSX630H 4P Micrologic 2.3', 'Ir 520 A', None),
 ('B', '7-28', 'TD002 — TS44B AUXILIAIRES FOUR 01', 'NS1250H 4P 5.0A', 'Ir 1250 A', 'L9'),
 ('B', '7-53', 'DIV003 — BÂTIMENT BRONZINI', 'NS1250N 4P 5.0A', 'Ir 1250 A', None),
 ('B', '7-72', 'COND001 — BATTERIE CONDENSATEURS 350 kVAR', 'NS800H 3P 5.0A', 'Ir 758 A', 'L8'),
]
T2ID = {}
for half, case, label, model, ir, xc in T2:
    xl = None
    if xc:
        xl = dict(ref=xlref(S2, xc), label=xl_item(S2, xc)); XL_USED.add((S2, xc))
    T2ID[case] = dep('TGBT2', half, label, T2DOC + f' › liste consommateurs (case {case})', case=case, model=model, ir=ir, xl=xl,
                     conf='confirme' if xc or 'RÉSERVE' in label or 'MULTICLIP' in label or 'BRONZINI' in label else 'probable')
nodes[T2ID['6-36']]['conf'] = 'probable'
nodes[T2ID['6-36']]['note'] = 'Libellé plan « TS12 ROVING » ; Excel L7 « TS12 Emballage (Situé au travaux neuf) ». Le TS12 est aussi alimenté depuis le TGBT 3 (TS12A / TS12B) — voir incohérence.'
nodes[T2ID['6-43']]['conf'] = 'probable'
for xc in ('H6', 'H11', 'L11'):
    dep('TGBT2', 'A' if xc[0] == 'H' else 'B', xl_item(S2, xc), xlref(S2, xc), conf='a_verifier',
        xl=dict(ref=xlref(S2, xc), label=xl_item(S2, xc)), note='Départ du classeur non retrouvé dans la liste des consommateurs Schneider (case inconnue).')
    XL_USED.add((S2, xc))

# --- TGBT 3 : dossier CX7810
T3 = [
 ('A', '1+28', 'RÉSERVE', 'NS800H 4P Micrologic 5.0A', '800 A'),
 ('A', '1+53', 'FRIGO 7H217', 'NS1000H 4P 5.0A', '1000 A'),
 ('A', '1+72', 'COND001 — BATTERIE CONDENSATEURS 350 kVAR', 'NS800H 3P 5.0A', 'Ir 758 A'),
 ('A', '2+18', 'TS12A', 'NS1000H 4P 5.0A', '1000 A'),
 ('A', '2+36', 'RÉSERVE', 'NS1250H 4P 5.0A', '1250 A'),
 ('A', '2+43', 'C_001 — SOUS-DISTRIBUTION DES AUXILIAIRES', 'NSX160H 4P Micrologic 2.2 160A', '160 A'),
 ('A', '2+72', 'DIV003 — RÉSERVE', 'NSX630H 4P Micrologic 2.3', 'Ir 520 A'),
 ('B', '5+18', 'TS12B', 'NS1000H 4P 5.0A', 'Ir 800 A'),
 ('B', '5+36', 'RÉSERVE', 'NS1250H 4P 5.0A', '1250 A'),
 ('B', '5+43', 'DIV007 — SOUS-DISTRIBUTION DES AUXILIAIRES', 'NSX160H 4P Micrologic 2.2 160A', '160 A'),
 ('B', '5+72', 'DIV005 — RÉSERVE', 'NSX630H 4P Micrologic 2.3', 'Ir 520 A'),
 ('B', '6+28', 'FRIGO 7H214', 'NS1000H 4P 5.0A', '1000 A'),
 ('B', '6+53', 'RÉSERVE', 'NS1000H 4P 5.0A', '1000 A'),
 ('B', '6+72', 'COND001 — BATTERIE CONDENSATEURS 350 kVAR', 'NS800H 3P 5.0A', '800 A'),
]
T3ID = {}
for half, case, label, model, ir in T3:
    T3ID[case] = dep('TGBT3', half, label, T3DOC + f' › liste des consommateurs (case ={case})', case=case, model=model, ir=ir)
ISSUE('I-7H214', 'moyenne', 'FRIGO 7H214 : TGBT 1A ou TGBT 3B ?', 'Excel « TR 1A & 1B » H6 : « Frigo 7H214 » sur TGBT 1A. Plan Schneider TGBT 3 : « FRIGO 7H214 » case 6+28 (TGBT 3B). Probable transfert lors de la création du TGBT 3 — à vérifier.', [XL, T3DOC], [T3ID['6+28']])
ISSUE('I-TS12', 'haute', 'Alimentation du TS12', 'Trois sources documentaires : Excel L7 (TGBT 2B, « TS12 Emballage, situé aux travaux neufs ») ; plan TGBT 2 case 6-36 « TS12 ROVING » ; plan TGBT 3 cases 2+18 « TS12A » et 5+18 « TS12B ». Le modèle relie le TS12 aux départs du TGBT 3 ; le départ TGBT 2 6-36 est conservé sans liaison active.', [XL, T2DOC, T3DOC], ['TS12', T2ID['6-36']])

# --- TGBT 4 : relevé photos (étiquettes lisibles) + Excel
S4 = 'TR 4A & 4B'
T4 = [
 # half, case, label (étiquette exacte), plate, meter, xl cell, model
 ('A', '1-10', 'RÉSERVE', 'green', None, None, 'Derrière porte'),
 ('A', '1-23', 'TS8 — LOCAL FRIGO — CASE 1-23', 'green', '2x', 'H6', 'Derrière porte'),
 ('A', '1-32', 'AUXILIAIRE WUCS — PRÉPOSÉ BBG — CASE 1-32', 'green', '2x', 'H7', 'Derrière porte'),
 ('A', '1-41', 'RÉSERVE', 'green', None, None, 'Derrière porte'),
 ('A', '2-10', 'TS24A — FOUR 2 — CASE 2-10', 'green', '19', 'H8', 'Derrière porte'),
 ('A', '2-23', 'RÉSERVE', 'green', None, None, 'Derrière porte'),
 ('A', '2-35', 'ARMOIRE COFFRET CHANTIER F2 + ÉCLAIRAGE FOUR 2 — FILAGE F1 — CASE 2-35', 'green', '20', 'H9', 'Derrière porte'),
 ('A', '2-42', 'ÉTUVE 10 — HALL ÉTUVE — CASE 2-42', 'green', '21', 'H10', 'Derrière porte'),
 ('A', '2-52', 'AUXILIAIRE A — SST 1 — CASE 2-52', 'green', None, 'H11', 'Derrière porte'),
 ('A', '3-53', 'BATTERIE CONDENSATEUR 4A — SST 1 — CASE 3-53', 'green', None, 'H12', 'Masterpact NT (probable)'),
 ('B', '4-28', 'TS42 — FILIÈRE 4A02 À 4A09 — CASE 4-28', 'green', '18', 'L7', 'Masterpact NW sous capot transparent'),
 ('B', '5-28', 'TS43 — FILIÈRE 4A12 À 4A19 — CASE 5-28', 'green', '17', 'L12', 'Masterpact NW sous capot transparent'),
 ('B', '5-53', 'BATTERIE CONDENSATEUR 4B — SST 1 — CASE 5-53', 'green', None, 'L8', 'Masterpact NT (probable)'),
 ('B', '6-53', 'END BUSHING F1 — FILAGE F2 — CASE 6-53', 'green', '16', None, 'Masterpact NT (probable)'),
 ('B', '7-10', 'TS24B — FOUR 2 — CASE 7-10', 'green', '13', 'L9', 'Derrière porte'),
 ('B', '7-23', 'TSO — LABO ANALYSTE — CASE 7-23', 'green', '14', 'L13', 'Derrière porte'),
 ('B', '7-33', 'ÉCLAIRAGE SST 1 — CASE 7-33', 'green', '15', 'L14', 'Derrière porte'),
 ('B', '7-52', 'AUXILIAIRE B — SST 1 — CASE 7-52', 'green', None, 'L11', 'Derrière porte'),
]
T4ID = {}
for half, case, label, plate, meter, xc, model in T4:
    xl = None
    if xc:
        xl = dict(ref=xlref(S4, xc), label=xl_item(S4, xc)); XL_USED.add((S4, xc))
    conf = 'confirme'
    if case in ('4-28',): conf = 'probable'
    T4ID[case] = dep('TGBT4', half, label, f'Tgbt 4.pdf (étiquette case {case})', conf=conf, case=case, model=model, xl=xl, meter=meter, plate=plate)
nodes[T4ID['4-28']]['note'] = 'Colonne 4 = colonne du couplage : rattachement au demi-JdB B selon Excel (L7), à confirmer.'
nodes[T4ID['5-28']]['note'] = 'Étiquette « TS43 » ; Excel L12 « TS 42 Filières C4 4A12 à 4A19 ».'
ISSUE('I-TS43', 'basse', 'TS42 / TS43 (filières 4A12-4A19)', 'Étiquette TGBT 4 case 5-28 : « TS43 FILIÈRE 4A12 à 4A19 » ; Excel « TR 4A & 4B » L12 : « TS 42 Filières C4 4A12 à 4A19 ».', [XL, 'Tgbt 4.pdf p9'], [T4ID['5-28']])
for xc in ('L6', 'L10'):
    dep('TGBT4', 'B', xl_item(S4, xc), xlref(S4, xc), conf='a_verifier', xl=dict(ref=xlref(S4, xc), label=xl_item(S4, xc)),
        note='Présent dans le classeur, non identifié sur la façade photographiée.')
    XL_USED.add((S4, xc))

# --- autres TGBT : départs Excel (H / L)
for n, sheet in ((1, 'TR 1A & 1B'), (5, 'TR 5A & 5B'), (6, 'TR 6A & 6B'), (7, 'TR 7A & 7B'), (8, 'TR 8A & 8B'), (9, 'TR 9A & 9B')):
    s = SHEETS[sheet]
    for half, h in s['halves'].items():
        for it in h['items']:
            if (sheet, it['cell']) in XL_USED: continue
            dep(TGBT[n], half, it['label'], xlref(sheet, it['cell']), conf='confirme', xl=dict(ref=xlref(sheet, it['cell']), label=it['label']))
            XL_USED.add((sheet, it['cell']))

# --------------------------------------------------------------------------- tableaux secondaires
def sub(id, name, kind='TS', loc=None, loc_conf='inconnu', photos=(), note=None, halves=None, style=None, facade=None, docs=()):
    boards[id] = dict(id=id, name=name, kind=kind, loc=loc, loc_conf=loc_conf, photos=list(photos), note=note, style=style,
                      facade=facade, docs=list(docs), halves=halves or [dict(id=f'{id}_J', label=f'{name} — jeu de barres')],
                      coupler=dict(status='sans_objet' if not halves or len(halves) < 2 else 'non_documente'))
    for h in boards[id]['halves']:
        N(h['id'], 'bus', h['label'], board=id, conf='probable', src='Classeur / photos')
    return id

def find_dep(board, cell_sheet):
    sheet, cell = cell_sheet
    for d in deps.values():
        if d['board'] == board and d.get('xl') and d['xl']['ref'].endswith(f'› {cell}') and f'« {sheet} »' in d['xl']['ref']:
            return d['id']
    raise KeyError((board, cell_sheet))

def feed(dep_id, bus_id, conf='confirme', src=None, note=None):
    nodes[dep_id]['feeds'] = nodes[bus_id]['board']
    E(dep_id, bus_id, src or nodes[dep_id]['src'], conf=conf, note=note)

def fill_block(sheet, header_cell, board_bus, board, half='J', skip=()):
    s = SHEETS[sheet]
    bl = next(b for b in s['blocks'] if b['cell'] == header_cell)
    ids = []
    for it in bl['items']:
        if it['cell'] in skip: continue
        ids.append(dep(board, board_bus, it['label'], xlref(sheet, it['cell']), conf='confirme', xl=dict(ref=xlref(sheet, it['cell']), label=it['label'])))
        nodes[ids[-1]]['half'] = half
        XL_USED.add((sheet, it['cell']))
    return ids

# TS1 Ensimage (TGBT 1A H8)
sub('TS1', 'TS 1 — Ensimage')
feed(find_dep('TGBT1', ('TR 1A & 1B', 'H8')), 'TS1_J')
ts1 = fill_block('TR 1A & 1B', 'A13', 'TS1_J', 'TS1')
sub('ECL9M04', 'Éclairage Ensimage labo central 9M04', kind='Éclairage')
e9 = next(i for i in ts1 if nodes[i]['label'].startswith('Eclairage Ensimage labo central'))
feed(e9, 'ECL9M04_J')
fill_block('TR 1A & 1B', 'C16', 'ECL9M04_J', 'ECL9M04')
sub('COFAGIT', 'Coffret agitateur (cuves 14 à 17)', kind='Coffret', note='Bloc C50 du classeur sans tableau parent identifié (voisin de la liste TS 1).')
fill_block('TR 1A & 1B', 'C50', 'COFAGIT_J', 'COFAGIT')
ISSUE('I-AGIT', 'basse', 'Coffret agitateur sans parent', 'Bloc « Coffret agitateur » (C50-C54, onglet TR 1A & 1B) : aucun départ amont identifié.', [XL], ['COFAGIT'])
# TS7 (Four 1) A/B
sub('TS7', 'TS 7 — Four 1', loc='TERRAIN', note='À proximité du four (indication utilisateur). Photos : arrivées « TS7A s/station 1A », isolement JdB A, arrivée groupe électrogène (lecture partielle).',
    photos=['Ts 7.pdf p1-p11'], halves=[dict(id='TS7_A', label='TS 7A — Four 1'), dict(id='TS7_B', label='TS 7B — Four 1')], style='prisma_blanc')
feed(find_dep('TGBT1', ('TR 1A & 1B', 'H9')), 'TS7_A')
feed(find_dep('TGBT1', ('TR 1A & 1B', 'L9')), 'TS7_B')
fill_block('TR 1A & 1B', 'E13', 'TS7_A', 'TS7', half='A')
fill_block('TR 1A & 1B', 'O9', 'TS7_B', 'TS7', half='B')
# HVAC canal 3
sub('HVAC3', 'HVAC Canal 3', kind='Coffret')
feed(find_dep('TGBT1', ('TR 1A & 1B', 'H11')), 'HVAC3_J')
fill_block('TR 1A & 1B', 'J15', 'HVAC3_J', 'HVAC3')
# TS44 A/B (TGBT 2)
sub('TS44', 'TS 44 — Auxiliaires Four 1', loc='TERRAIN', note='En face des filières (indication utilisateur).', photos=['Ts 44.pdf p1-p12'],
    halves=[dict(id='TS44_A', label='TS 44A — Auxiliaires Four 1 (Heat wheel)'), dict(id='TS44_B', label='TS 44B — Auxiliaires Four 1')], style='okken_blanc')
feed(T2ID['2-18'], 'TS44_A'); feed(T2ID['7-28'], 'TS44_B')
fill_block('TR 2A & 2B', 'E12', 'TS44_A', 'TS44', half='A')
fill_block('TR 2A & 2B', 'O9', 'TS44_B', 'TS44', half='B')
# TS12
sub('TS12', 'TS 12 — Emballage / Roving', loc='TERRAIN', note='Au-dessus de la maintenance (indication utilisateur). Excel : « situé aux travaux neufs ». PrismaSeT à bandeau vert (photos).',
    photos=['Ts 12 .pdf p1-p22'], halves=[dict(id='TS12_A', label='TS 12A'), dict(id='TS12_B', label='TS 12B'), dict(id='TS12_J', label='TS 12 — départs (demi-JdB non attribué)')], style='prisma_vert')
feed(T3ID['2+18'], 'TS12_A', conf='confirme', src=T3DOC); feed(T3ID['5+18'], 'TS12_B', conf='confirme', src=T3DOC)
E('TS12_A', 'TS12_J', 'Hypothèse : répartition des départs non documentée', conf='a_verifier')
N('TS12_QC', 'cpl', 'Liaison / couplage TS 12A ↔ TS 12B (non documenté)', board='TS12', role='couplage', conf='inconnu', src='Hypothèse de modélisation : deux arrivées TS12A / TS12B (plan TGBT 3)')
E('TS12_J', 'TS12_QC', 'Hypothèse', conf='inconnu'); E('TS12_QC', 'TS12_B', 'Hypothèse', conf='inconnu')
nodes[T2ID['6-36']]['feeds'] = 'TS12'
fill_block('TR 2A & 2B', 'Q6', 'TS12_J', 'TS12', half='?')
# TS2 étuves
sub('TS2', 'TS 2 — Étuves', loc=None, note='TS2A / TS2B « Étuve(s) S/Station » (plan TGBT 2).', photos=['Ts2.pdf p1-p11'],
    halves=[dict(id='TS2_A', label='TS 2A — Étuves'), dict(id='TS2_B', label='TS 2B — Étuves')], style='okken_blanc')
feed(T2ID['2-36'], 'TS2_A'); feed(T2ID['6-18'], 'TS2_B')
sub('ETUVE789', 'Tableau Étuves 7-8-9', kind='TS')
feed(T2ID['1-53'], 'ETUVE789_J')
sub('BRONZINI', 'Bâtiment Bronzini', kind='Bâtiment', loc='TERRAIN', note='Zone Bronzini (indication utilisateur). Départ ajouté au TGBT 2 en 2024.', photos=['Bronzini .pdf p1-p3'])
feed(T2ID['7-53'], 'BRONZINI_J', src=T2DOC)
# TS8 / TS24 (TGBT 4)
sub('TS8', 'TS 8 — Groupe frigo (local frigo)')
feed(T4ID['1-23'], 'TS8_J')
fill_block('TR 4A & 4B', 'C7', 'TS8_J', 'TS8')
sub('TS24', 'TS 24 — Four 2', halves=[dict(id='TS24_A', label='TS 24A — Four 2'), dict(id='TS24_B', label='TS 24B — Four 2')])
feed(T4ID['2-10'], 'TS24_A'); feed(T4ID['7-10'], 'TS24_B')
fill_block('TR 4A & 4B', 'E9', 'TS24_A', 'TS24', half='A')
fill_block('TR 4A & 4B', 'O9', 'TS24_B', 'TS24', half='B')
for c in range(8, 13): XL_USED.add(('TR 6A & 6B', f'O{c}'))
ISSUE('I-TS24B', 'basse', 'Bloc TS 24B dupliqué', 'Le bloc « TS 24 B (Four 2) » apparaît à l’identique dans les onglets TR 4A & 4B (O9) et TR 6A & 6B (O7). Rattaché au TGBT 4B (L9) ; la copie de l’onglet TR 6 est ignorée.', [XL], ['TS24'])
sub('TS42', 'TS 42 — Filières 4A02 à 4A09'); feed(T4ID['4-28'], 'TS42_J', conf='probable')
sub('TS43', 'TS 43 — Filières 4A12 à 4A19'); feed(T4ID['5-28'], 'TS43_J', conf='probable')
sub('TSO', 'TSO — Labo analyste'); feed(T4ID['7-23'], 'TSO_J')
sub('ECLSST1', 'Armoire éclairage Sous-station 1', kind='Éclairage', photos=['Armoire éclairage .pdf p1'], note='Rapprochement photo « Armoire éclairage » ↔ départ « ÉCLAIRAGE SST 1 » : probable.')
feed(T4ID['7-33'], 'ECLSST1_J', conf='probable')
# TS28 (TGBT 6A)
sub('TS28', 'TS 28 — Clim Four 2 (face à l’ascenseur)')
feed(find_dep('TGBT6', ('TR 6A & 6B', 'H6')), 'TS28_J')
fill_block('TR 6A & 6B', 'C7', 'TS28_J', 'TS28')
# TS16 STEP (TGBT 7A)
sub('TS16', 'TS 16 — STEP')
feed(find_dep('TGBT7', ('TR 7A & 7B', 'H7')), 'TS16_J')
fill_block('TR 7A & 7B', 'C8', 'TS16_J', 'TS16')
# TS17 A/B chaufferie (TGBT 9)
sub('TS17', 'TS 17 — Chaufferie', photos=['Ts17A.pdf p1-p8', 'Ts17b.pdf p1-p13'],
    halves=[dict(id='TS17_A', label='TS 17A — Chaufferie'), dict(id='TS17_B', label='TS 17B — Chaufferie')], style='okken_beige')
feed(find_dep('TGBT9', ('TR 9A & 9B', 'H7')), 'TS17_A'); feed(find_dep('TGBT9', ('TR 9A & 9B', 'L7')), 'TS17_B')
ts17a = fill_block('TR 9A & 9B', 'C7', 'TS17_A', 'TS17', half='A')
ts17b = fill_block('TR 9A & 9B', 'P7', 'TS17_B', 'TS17', half='B')
sub('TS15', 'TS 15 — Batch'); feed(find_dep('TGBT9', ('TR 9A & 9B', 'L9')), 'TS15_J')
fill_block('TR 9A & 9B', 'N11', 'TS15_J', 'TS15')
ISSUE('I-TS17', 'haute', 'Origine du TS 17 / TS 9 : TGBT 9 ou TR 2B ?', 'Onglet « TR 9A & 9B » : TS 17A et TS 17B sur TGBT 9A / 9B. Mais la liste TS 17A contient « Arrivée 2A Normale » (C16) et les étiquettes arc du TS 9 indiquent « TABLEAU TR2B TS17B TS9 ». Hypothèse : étiquettes antérieures au « nouveau TGBT 9 ». À vérifier sur site.', [XL, 'Ts9.pdf p5, p7'], ['TS17', 'TS9'])
# Les "arrivées" listées dans TS17A sont des arrivées, pas des départs
for i in ts17a:
    if nodes[i]['label'].lower().startswith('arriv'):
        nodes[i]['t'] = 'cb'; nodes[i]['role'] = 'arrivee_ts'; nodes[i]['conf'] = 'a_verifier'
        nodes[i]['note'] = 'Ligne du classeur décrivant une arrivée du TS 17A (et non un départ). Origine non documentée.'

# TS9 chaufferie — façade relevée sur photos
sub('TS9', 'TS 9 — Chaufferie', loc='TERRAIN', photos=['Ts9.pdf p1-p7'], style='okken_beige', facade='TS9',
    note='Merlin Gerin, beige. 4 colonnes. Arrivées : TS17A (JdB A), secours groupe 1, « Arrivée B normale TS17B » ; couplage jeu de barres (col. 3). Automate de permutation de sources (« A ↔ forçage / A ↔ auto ») en colonne 1.',
    halves=[dict(id='TS9_A', label='TS 9 — JdB A'), dict(id='TS9_B', label='TS 9 — JdB B')])
N('TS9_QA', 'cb', 'ARRIVÉE TS17A (JdB A)', board='TS9', half='A', role='arrivee', conf='confirme', src='Ts9.pdf p1 (étiquette)')
N('TS9_QB', 'cb', 'ARRIVÉE B NORMALE TS17B', board='TS9', half='B', role='arrivee', conf='confirme', src='Ts9.pdf p7 (étiquette)')
N('TS9_QS', 'cb', 'ARRIVÉE SECOURS GROUPE 1', board='TS9', half='A', role='arrivee', conf='confirme', src='Ts9.pdf p1 (étiquette)', note='Jeu de barres raccordé : non documenté (JdB A supposé).')
N('TS9_ISA', 'sw', 'INTERRUPTEUR GÉNÉRAL ISOLEMENT JdB-A', board='TS9', half='A', conf='confirme', src='Ts9.pdf p1 (étiquette)')
N('TS9_QC', 'cpl', 'COUPLAGE JEU DE BARRES (TS 9)', board='TS9', role='couplage', conf='confirme', src='Ts9.pdf p5 (étiquette col. 3)')
N('GE1', 'src', 'Groupe électrogène n°1 (secours)', conf='probable', src='Ts9.pdf p1 « Arrivée secours groupe 1 » ; Excel TS17A C9 « Arrivée secours n°1 »', loc='TERRAIN')
alimA = next(i for i in ts17a if 'TS9' in nodes[i]['label'].replace(' ', ''))
alimB = next(i for i in ts17b if 'TS9' in nodes[i]['label'].replace(' ', ''))
nodes[alimA]['feeds'] = 'TS9'; nodes[alimB]['feeds'] = 'TS9'
E(alimA, 'TS9_QA', xlref('TR 9A & 9B', 'C15')); E('TS9_QA', 'TS9_ISA', 'Ts9.pdf p1', conf='probable'); E('TS9_ISA', 'TS9_A', 'Ts9.pdf p1', conf='probable')
E(alimB, 'TS9_QB', xlref('TR 9A & 9B', 'P17')); E('TS9_QB', 'TS9_B', 'Ts9.pdf p7', conf='probable')
E('GE1', 'TS9_QS', 'Ts9.pdf p1', conf='probable'); E('TS9_QS', 'TS9_A', 'Ts9.pdf p1', conf='a_verifier')
E('TS9_A', 'TS9_QC', 'Ts9.pdf p5'); E('TS9_QC', 'TS9_B', 'Ts9.pdf p5')
boards['TS9']['coupler'] = dict(status='documente', rule='« COUPLAGE JEU DE BARRES » (étiquette col. 3). Logique de la permutation automatique / forçage non documentée.', src='Ts9.pdf p2, p5')
T9 = [
 ('A', 'c1', '7PM26 — Transfert fuel domestique n°2', 'Tiroir : poignée rotative, marche/arrêt, compteur horaire, réarmement R', 'yellow'),
 ('A', 'c1', '7KM07 — Compresseur air instrum secours', 'Tiroir : poignée rotative, sélecteur', 'yellow'),
 ('A', 'c1', '7M21 — Coffret cde sirènes al. incendie', None, 'black'),
 ('A', 'c1', 'Alimentation commande C1 tours de refroidissement 1 et 2 Nord / 1 et 2 Sud', None, 'white'),
 ('A', 'c3', '7M08-7M09 — Alim. coffret chaudière 1 et 2', None, 'black'),
 ('A', 'c3', '7M13 — Armoire cde diesel pompe eau froide', None, 'black'),
 ('A', 'c3', 'Auxiliaires groupe 2', None, 'black'),
 ('A', 'c3', 'Auxiliaires groupe 1', None, 'black'),
 ('A', 'c3', '7PM043 — Chauffage diesel process', None, 'black'),
 ('A', 'c3', 'Prise PS chaufferie', None, 'black'),
 ('A', 'c3', 'PM05 — Volet chaufferie', None, 'black'),
 ('B', 'c4', 'AE7P025 (400 V)', 'Tiroir : poignée rotative, marche/arrêt, compteur horaire, réarmement R', 'red'),
 ('B', 'c4', 'Tiroir n°2 col. 4 — étiquette illisible (« … pompe … fuel domestique » ?)', 'Tiroir : poignée rotative, voyant', None),
 ('B', 'c4', 'Armoire silo kaolin', None, 'black'),
 ('B', 'c4', 'Sécheur 7K121', None, 'black'),
 ('B', 'c4', 'Sécheur 7K122', None, 'black'),
 ('B', 'c4', 'Départ réchauffeur 7,5 kW 7K121', None, 'black'),
 ('B', 'c4', 'Départ réchauffeur 7,5 kW 7K122', None, 'black'),
]
T9ID = []
for half, col, label, model, plate in T9:
    c = 'a_verifier' if 'illisible' in label else ('probable')
    T9ID.append(dep('TS9', f'TS9_{half}', label, f'Ts9.pdf (étiquette colonne {col[1]})', conf=c, model=model, plate=plate,
                    note='Demi-jeu de barres déduit de la position (colonne) — non documenté.'))
    nodes[T9ID[-1]]['half'] = half
ISSUE('I-TS9ARC', 'basse', 'Étiquette arc TS 9 col. 3', 'Relevé photo (Ts9.pdf p5) : 400 V ; Icc 1,62 kA ; 0,19 cal/cm² ; limite d’approche 14,91 cm. La maquette antérieure mentionnait 1,92 kA et 0,15 cal/cm² : relire la plaque.', ['Ts9.pdf p5'], ['TS9'])

# Pompes eau glacée (photos)
sub('PEG', 'Coffrets pompes eau glacée 7PM65 / 7PM03', kind='Coffret', loc='TERRAIN', photos=['Pompe eau glace 7pm 65 et 7Pm03.pdf p1-p3'],
    halves=[dict(id='PEG_65', label='Coffret 7PM65'), dict(id='PEG_03', label='Coffret 7PM03')])
for i in deps.values():
    l = i['label'].replace(' ', '').upper()
    if '7PM65' in l and i['board'] == 'TS44': feed(i['id'], 'PEG_65', conf='probable')
    if '7PM03' in l and i['board'] == 'TS44': feed(i['id'], 'PEG_03', conf='probable')

# --- Tableaux / équipements connus par photos seulement (inventaire)
PHOTO_ONLY = [
 ('TS46A', 'TS 46A', 'TS', 'TERRAIN', 'Entre Packman et l’emballage (indication utilisateur). Absent du classeur.', ['Ts46a .pdf p1-p3']),
 ('TS46B', 'TS 46B', 'TS', 'TERRAIN', 'Entre Packman et l’emballage (indication utilisateur). Absent du classeur.', ['Ts46b.pdf p1-p6']),
 ('OM27', 'Tableau OM 27', 'TS', None, 'Absent du classeur.', ['Tableau OM 27 .pdf p1']),
 ('ARM110', 'Armoire 110 V — instrument ampèremètre', 'Armoire 110 V', None, None, ['Armoire 110v instrument ampère mètre .pdf p1']),
 ('VENTIL', 'Coffret ventilation local Boosting F2', 'Coffret', None, 'Plaque lue sur Ventilation FOUR.pdf p3. Les pages 1, 2, 4, 5 et 6 montrent une autre armoire (Helipac).', ['Ventilation FOUR.pdf p3']),
 ('DECARBO', 'Décarbonatation', 'Coffret', None, 'Excel TS17A C29 « 7M10 Armoire commande decarbonatation » — rapprochement probable.', ['Decarbo .pdf p1-p2']),
 ('GORGE', 'Gorge Four 2', 'Armoires', None, 'Armoires grises à sectionneurs à poignée (photos). Excel TGBT 9A H6 « Normal secours gorge Four 2 » — rapprochement probable.', ['Gorge .pdf p1-p15']),
 ('GRADATHYR', 'Gradathyr (gradateurs à thyristors)', 'Armoires', 'SS1', 'Équipements de boosting cités en SS1 par l’utilisateur ; alimentation non documentée.', ['GRADATHYR.pdf p1-p5']),
 ('VARIVOLT', 'Varivolt 1 et 2', 'Armoires', None, 'Dossiers « schéma DM1 départ varivolt zone 1/2 » (p1 - Copie (2).zip). Rapprochement avec cellules AEF1-TRZ1/TRZ2 (électrodes zones 1/2) : probable.', ['Varivolt1 et 2 .pdf p1-p2']),
 ('OND1', 'Onduleur 1 (Sous-station 1)', 'Onduleur', 'SS1', 'Doc. 990-91407C (APC/Schneider). Départs « réseau 1 / réseau 2 onduleur » dans le classeur (TGBT 5A/5B, 6A/6B…).', ['Onduleur 1 .pdf p1-p2', 'Alim onduleur 1 .pdf p1-p3']),
 ('OND2', 'Onduleur 2 (Sous-station 2)', 'Onduleur', 'SS2', 'Plans R122618 « SS2 UPS distribution » (dwg).', ['Onduleur 2 .pdf p1', 'Alimentation onduleur 2.pdf p1-p4']),
 ('COND1', 'Batteries condensateurs TR1A / TR1B', 'Condensateurs', None, None, ['Batterie condensateur tr1a et 1b .pdf p1-p3']),
 ('COND2A', 'Batterie condensateurs TR2A', 'Condensateurs', None, None, ['Batterie condensateur tr2a .pdf p1-p2']),
 ('COND2B', 'Batterie condensateurs TR2B', 'Condensateurs', None, None, ['Condensateur tr2b .pdf p1']),
 ('COND3', 'Batteries condensateurs TGBT 3', 'Condensateurs', None, None, ['Condensateur tgbt 3.pdf p1-p2']),
 ('COND4', 'Batteries condensateurs TR4A / TR4B', 'Condensateurs', 'SS1', 'Étiquettes TGBT 4 « Batterie condensateur 4A/4B SST 1 ».', ['Condesanteur tr4b et 4 a .pdf p1-p2']),
 ('COND5A', 'Batterie condensateurs TR5A', 'Condensateurs', None, None, ['Condensateur tr 5a.pdf p1-p2']),
 ('COND5B', 'Batterie condensateurs 5B', 'Condensateurs', None, None, ['Condensateur 5b.pdf p1-p2']),
 ('COND6A', 'Batterie condensateurs 6A', 'Condensateurs', None, None, ['Condensateur 6a.pdf p1-p2']),
 ('COND6B', 'Batterie condensateurs 6B', 'Condensateurs', None, None, ['Condensateur 6b .pdf p1']),
 ('COND7', 'Batteries condensateurs TGBT 7A / 7B', 'Condensateurs', None, None, ['Batterie condensateur tgbt7a et 7b.pdf p1-p2']),
 ('COND9', 'Batteries condensateurs TGBT 9A / 9B', 'Condensateurs', None, None, ['Condensateur tgbt 9a et 9b .pdf p1-p4']),
 ('AUX7B', 'Coffret 24 V / 230 V TR7B', 'Coffret', None, None, ['24 V et 230 V tr7b.pdf p1']),
]
PAIRED = {'COND1', 'COND3', 'COND4', 'COND7', 'COND9'}   # deux batteries distinctes (A et B), une par demi-jeu de barres
for id, name, kind, loc, note, photos in PHOTO_ONLY:
    hv = [dict(id=f'{id}_A', label=f'{name} — batterie A'), dict(id=f'{id}_B', label=f'{name} — batterie B')] if id in PAIRED else None
    sub(id, name, kind=kind, loc=loc, loc_conf='probable' if loc else 'inconnu', photos=photos, note=note, halves=hv)
    if id in PAIRED: boards[id]['coupler'] = dict(status='sans_objet')
# Raccordement des batteries de condensateurs aux départs « condensateur » documentés (batterie A sur demi-JdB A, B sur B)
def link_cond(board_id, cond_board, conf='probable'):
    for d in deps.values():
        if d['board'] == board_id and 'CONDENS' in slug(d['label']):
            half = d.get('half') if d.get('half') in ('A', 'B') else 'A'
            E(d['id'], f'{cond_board}_{half}', d['src'], conf=conf); d['feeds'] = cond_board
link_cond('TGBT3', 'COND3'); link_cond('TGBT4', 'COND4', 'confirme'); link_cond('TGBT7', 'COND7'); link_cond('TGBT9', 'COND9')

# HTA boards
for id, name, loc, photos, facade in (
    ('PL20', 'Tableau 20 kV — Poste de livraison EDF / CNR', 'PL', ['Tableau 20kv edf cnr .pdf p1-p24', 'Départ 20kv edf cnr.pdf p1-p21'], 'PL20'),
    ('SS1_20', 'Tableau 20 kV — Sous-station 1', 'SS1', ['Tableau 20kv SS1.pdf p1-p16', 'Tableau 20kv   SS1.pdf p1-p10', 'Tableau 20kv     SS1.pdf p1-p24'], 'SS1_20'),
    ('SS2_20', 'Tableau 20 kV — Sous-station 2', 'SS2', [], 'SS2_20'),
    ('KV6', 'Tableau 6 kV — Four 2 (Sous-station 2)', 'SS2', ['Tableau 6kv.pdf p1-p13'], 'KV6')):
    boards[id] = dict(id=id, name=name, kind='HTA', loc=loc, loc_conf='confirme', photos=photos, style='sm6', facade=facade, docs=[UNI],
                      halves=[], coupler=dict(status='documente', rule='Couplage représenté sur l’unifilaire ; logique d’interverrouillage (clés) non décrite.', src=UNI),
                      note='Cellules Merlin Gerin / Schneider SM6 (repère « SM6 » sur l’unifilaire SS1 ; apparence confirmée par les photos). Ordre des cellules selon l’unifilaire.')
boards['PL20']['coupler'] = dict(status='sans_objet')
ISSUE('I-SS2PH', 'moyenne', 'Tableau 20 kV SS2 : photos', 'Aucun fichier photo explicitement nommé « SS2 ». Les fichiers « Tableau 20kv SS1 » (3 séries, 50 pages) peuvent contenir le tableau SS2 : tri à confirmer.', [], ['SS2_20'])

# --------------------------------------------------------------------------- Excel non utilisé (contrôle d'exhaustivité)
left = []
for s in EX['sheets']:
    for h in s['halves'].values():
        for it in h['items']:
            if (s['sheet'], it['cell']) not in XL_USED: left.append((s['sheet'], it['cell'], it['label']))
    for bl in s['blocks']:
        for it in bl['items']:
            if (s['sheet'], it['cell']) not in XL_USED: left.append((s['sheet'], it['cell'], it['label']))
print('Excel non rattaché :', len(left))
for l in left: print('   ', l)

# --------------------------------------------------------------------------- façades
F = {}
def okken_cols(spec):
    return spec

# TGBT 4 — relevé photo (cases et étiquettes exactes). Largeurs relatives : 650 / 250 (couloir câbles), proportions photo.
F['TGBT4'] = dict(style='okken_beige', title='TGBT N°4 — SAP : 42933+42934', brand='MERLIN GERIN', height=80,
  src='Tgbt 4.pdf p2, p5, p9, p11, p12', conf='Relevé photo (étiquettes lisibles) — proportions estimées sur photos non redressées',
  cols=[
   dict(n='1', w=650, units=[
     dict(y=8, h=9, k='doorcell', dep=T4ID['1-10'], voy=True, meter=True, label='RÉSERVE'),
     dict(y=21, h=9, k='doorcell', dep=T4ID['1-23'], voy=True, meter=True, label='TS8 / LOCAL FRIGO / CASE 1-23'),
     dict(y=31, h=9, k='doorcell', dep=T4ID['1-32'], voy=True, meter=True, label='AUXILIAIRE WUCS / PRÉPOSÉ BBG / CASE 1-32'),
     dict(y=41, h=9, k='doorcell', dep=T4ID['1-41'], voy=True, meter=True, label='RÉSERVE'),
   ], doors=[(0, 80)]),
   dict(n='2', w=650, units=[
     dict(y=9, h=8, k='doorcell', dep=T4ID['2-10'], voy=True, meter=True, num='19', label='TS24A / FOUR 2 / CASE 2-10'),
     dict(y=21, h=8, k='doorcell', dep=T4ID['2-23'], voy=True, meter=True, label='RÉSERVE'),
     dict(y=31, h=9, k='doorcell', dep=T4ID['2-35'], voy=True, meter=True, num='20', label='ARMOIRE COFFRET CHANTIER F2+ÉCLAIRAGE FOUR 2 / FILAGE F1 / CASE 2-35'),
     dict(y=42, h=8, k='doorcell', dep=T4ID['2-42'], voy=True, meter=True, num='21', label='ÉTUVE 10 / HALL ÉTUVE / CASE 2-42'),
     dict(y=52, h=5, k='doorcell', dep=T4ID['2-52'], voy=True, meter=False, label='AUXILIAIRE A / SST 1 / CASE 2-52'),
   ], doors=[(0, 80)]),
   dict(n='3', w=650, units=[
     dict(y=4, h=4, k='blank', label='PARAFOUDRE'),
     dict(y=24, h=17, k='nw', node='TGBT4_QA', plate='red', label='PROVIENT DE TR 4A / ARRIVÉE TGBT 4A / CASE 3-28', tr=True),
     dict(y=44, h=5, k='temp', label='Relais température (58 °C au relevé)'),
     dict(y=52, h=15, k='nt', dep=T4ID['3-53'], plate='green', label='BATTERIE CONDENSATEUR 4A / SST 1 / CASE 3-53'),
   ], doors=[(0, 12), (12, 43), (43, 49), (49, 68), (68, 80)]),
   dict(n='', w=250, units=[dict(y=26, h=3, k='voy'), dict(y=30, h=7, k='meter'), dict(y=39, h=6, k='mod2', label='Tension / Intensité'), dict(y=55, h=3, k='voy', label='Batterie condensateur 4A')], doors=[(0, 80)]),
   dict(n='4', w=650, units=[
     dict(y=8, h=8, k='imd', label='Vigilohm IM400 — TGBT 4A (100 kΩ au relevé)'),
     dict(y=22, h=19, k='nwc', dep=T4ID['4-28'], plate='green', label='TS42 / FILIÈRE 4A02 À 4A09 / CASE 4-28'),
     dict(y=50, h=17, k='nw', node='TGBT4_QC', plate='red', label='COUPLAGE / TR 4A-TR 4B / CASE 4-53'),
   ], doors=[(0, 18), (18, 44), (44, 49), (49, 70), (70, 80)]),
   dict(n='', w=250, units=[dict(y=26, h=3, k='voy'), dict(y=30, h=7, k='meter', num='18'), dict(y=57, h=3, k='voy2', label='Couplage')], doors=[(0, 80)]),
   dict(n='5', w=650, units=[
     dict(y=8, h=8, k='imd', label='Vigilohm IM400 — TGBT 4B (21 kΩ au relevé)'),
     dict(y=22, h=19, k='nwc', dep=T4ID['5-28'], plate='green', label='TS43 / FILIÈRE 4A12 À 4A19 / CASE 5-28'),
     dict(y=44, h=3, k='blank', label='Voyant / compteur'),
     dict(y=52, h=15, k='nt', dep=T4ID['5-53'], plate='green', label='BATTERIE CONDENSATEUR 4B / SST 1 / CASE 5-53'),
   ], doors=[(0, 18), (18, 44), (44, 49), (49, 70), (70, 80)]),
   dict(n='', w=250, units=[dict(y=26, h=3, k='voy'), dict(y=30, h=7, k='meter', num='17'), dict(y=55, h=3, k='voy', label='Batterie condensateur 4B')], doors=[(0, 80)]),
   dict(n='6', w=650, units=[
     dict(y=4, h=4, k='blank', label='PARAFOUDRE'),
     dict(y=24, h=17, k='nw', node='TGBT4_QB', plate='red', label='PROVIENT DE TR 4B / ARRIVÉE TGBT 4B / CASE 6-28', tr=True),
     dict(y=44, h=5, k='temp', label='Relais température'),
     dict(y=52, h=15, k='nt', dep=T4ID['6-53'], plate='green', label='END BUSHING F1 / FILAGE F2 / CASE 6-53'),
   ], doors=[(0, 12), (12, 43), (43, 49), (49, 68), (68, 80)]),
   dict(n='', w=250, units=[dict(y=26, h=3, k='voy'), dict(y=30, h=7, k='meter'), dict(y=39, h=6, k='mod2', label='Tension / Intensité'), dict(y=55, h=3, k='voy'), dict(y=59, h=6, k='meter', num='16')], doors=[(0, 80)]),
   dict(n='7', w=650, units=[
     dict(y=9, h=8, k='doorcell', dep=T4ID['7-10'], voy=True, meter=True, num='13', label='TS24B / FOUR 2 / CASE 7-10'),
     dict(y=21, h=8, k='doorcell', dep=T4ID['7-23'], voy=True, meter=True, num='14', label='TSO / LABO ANALYSTE / CASE 7-23'),
     dict(y=31, h=8, k='doorcell', dep=T4ID['7-33'], voy=True, meter=True, num='15', label='ÉCLAIRAGE SST1 / CASE 7-33'),
     dict(y=52, h=5, k='doorcell', dep=T4ID['7-52'], voy=True, meter=False, label='AUXILIAIRE B / SST 1 / CASE 7-52'),
   ], doors=[(0, 80)]),
  ])

def from_cases(rows, colw, half_of_col, node_of=None):
    """Façade Okken depuis les numéros de case du plan constructeur (y = case)."""
    cols = []
    for c, w in colw:
        units = []
        for (case, k, dep_id, node, plate, label, h) in rows.get(c, []):
            y = int(re.split(r'[-+]', case)[1])
            units.append(dict(y=y, h=h, k=k, dep=dep_id, node=node, plate=plate, label=label, case=case))
        cols.append(dict(n=str(c) if w >= 600 else '', w=w, units=units, doors=[(0, 80)] if w < 600 else None))
    return cols

R2 = {
 1: [('1-28', 'ns', T2ID['1-28'], None, 'green', 'RÉSERVE / CASE 1-28', 16), ('1-53', 'ns', T2ID['1-53'], None, 'green', 'TABLEAU ÉTUVE 7-8-9 / CASE 1-53', 16), ('1-72', 'ns', T2ID['1-72'], None, 'green', 'BATTERIE CONDENSATEURS / CASE 1-72', 7)],
 2: [('2-18', 'ns', T2ID['2-18'], None, 'green', 'TS44A AUXILIAIRES FOUR 01 / CASE 2-18', 15), ('2-36', 'ns', T2ID['2-36'], None, 'green', 'TS2A ÉTUVE S/STATION / CASE 2-36', 6), ('2-43', 'nsx', T2ID['2-43'], None, 'green', 'SOUS-DISTRIBUTION AUXILIAIRES / CASE 2-43', 7), ('2-51', 'window', T2ID['2-51'], None, None, 'MULTICLIP 1', 19), ('2-72', 'nsx', T2ID['2-72'], None, 'green', 'RÉSERVE / CASE 2-72', 7)],
 3: [('3-28', 'nw', None, 'TGBT2_QA', 'red', 'ARRIVÉE TRANSFO TR2A / CASE 3-28', 19)],
 4: [('4-53', 'nw', None, 'TGBT2_QC', 'red', 'COUPLAGE / CASE 4-53', 19)],
 5: [('5-28', 'nw', None, 'TGBT2_QB', 'red', 'ARRIVÉE TRANSFO TR2B / CASE 5-28', 19)],
 6: [('6-18', 'ns', T2ID['6-18'], None, 'green', 'TS2B ÉTUVES S/STATION / CASE 6-18', 15), ('6-36', 'ns', T2ID['6-36'], None, 'green', 'TS12 ROVING / CASE 6-36', 6), ('6-43', 'nsx', T2ID['6-43'], None, 'green', 'SOUS-DISTRIBUTION AUXILIAIRES / CASE 6-43', 7), ('6-51', 'window', T2ID['6-51'], None, None, 'MULTICLIP 2', 19), ('6-72', 'nsx', T2ID['6-72'], None, 'green', 'RÉSERVE / CASE 6-72', 7)],
 7: [('7-28', 'ns', T2ID['7-28'], None, 'green', 'TS44B AUXILIAIRES FOUR 01 / CASE 7-28', 16), ('7-53', 'ns', T2ID['7-53'], None, 'green', 'BÂTIMENT BRONZINI / CASE 7-53', 16), ('7-72', 'ns', T2ID['7-72'], None, 'green', 'BATTERIE CONDENSATEURS / CASE 7-72', 7)],
}
F['TGBT2'] = dict(style='okken_blanc', title='TGBT N°2 — SAP : 42930+42931', brand='Schneider Electric — Okken', height=80,
  src=T2DOC + ' (liste des consommateurs, colonnes 1 à 7) + Tgbt 2.pdf (apparence)', conf='Positions selon numéros de case du plan constructeur ; apparence d’après photos ; détails (voyants, centrales) génériques',
  cols=from_cases(R2, [(1, 650), (2, 650), (3, 650), (4, 650), (5, 650), (6, 650), (7, 650)], None))

R3 = {
 1: [('1+28', 'ns', T3ID['1+28'], None, 'green', 'RÉSERVE', 16), ('1+53', 'ns', T3ID['1+53'], None, 'green', 'FRIGO 7H217', 16), ('1+72', 'ns', T3ID['1+72'], None, 'green', 'BATTERIE CONDENSATEURS', 7)],
 2: [('2+18', 'ns', T3ID['2+18'], None, 'green', 'TS12A', 15), ('2+36', 'ns', T3ID['2+36'], None, 'green', 'RÉSERVE', 6), ('2+43', 'nsx', T3ID['2+43'], None, 'green', 'SOUS-DISTRIBUTION DES AUXILIAIRES', 8), ('2+51', 'window', None, None, None, 'MULTICLIP / AUXILIAIRES', 19), ('2+72', 'nsx', T3ID['2+72'], None, 'green', 'RÉSERVE', 7)],
 3: [('3+28', 'nw', None, 'TGBT3_QA', 'red', 'ARRIVÉE TRANSFO TR3A', 19), ('3+53', 'nw', None, 'TGBT3_QC', 'red', 'COUPLAGE', 19)],
 4: [('4+28', 'nw', None, 'TGBT3_QB', 'red', 'ARRIVÉE TRANSFO TR3B', 19)],
 5: [('5+18', 'ns', T3ID['5+18'], None, 'green', 'TS12B', 15), ('5+36', 'ns', T3ID['5+36'], None, 'green', 'RÉSERVE', 6), ('5+43', 'nsx', T3ID['5+43'], None, 'green', 'SOUS-DISTRIBUTION DES AUXILIAIRES', 8), ('5+51', 'window', None, None, None, 'MULTICLIP / AUXILIAIRES', 19), ('5+72', 'nsx', T3ID['5+72'], None, 'green', 'RÉSERVE', 7)],
 6: [('6+28', 'ns', T3ID['6+28'], None, 'green', 'FRIGO 7H214', 16), ('6+53', 'ns', T3ID['6+53'], None, 'green', 'RÉSERVE', 16), ('6+72', 'ns', T3ID['6+72'], None, 'green', 'BATTERIE CONDENSATEURS', 7)],
}
F['TGBT3'] = dict(style='okken_blanc_vert', title='TGBT N°3 — CX781001', brand='Schneider Electric — Okken', height=80,
  src=T3DOC + ' (face avant unifilaire p.26 : colonnes 650 mm, couloirs 250 mm en col. 2 et 5, longueur 4475 mm) + Tgbt 3.pdf / Tgbt 3 (2).pdf (apparence)',
  conf='Positions et largeurs selon plan constructeur ; apparence d’après photos ; détails génériques',
  cols=from_cases(R3, [(1, 650), (2, 650), ('2c', 250), (3, 650), (4, 650), (5, 650), ('5c', 250), (6, 650)], None))

# TS9 — relevé photos
F['TS9'] = dict(style='okken_beige', title='TS9', brand='MERLIN GERIN', height=80, src='Ts9.pdf p1, p2, p5, p7 ; IMG_4081-4092 (15/10/2026)',
  conf='Relevé photo : étiquettes noires partiellement lisibles, 15 étiquettes bleues lues sur les clichés du 15/10/2026, sans association validée aux protections (col. 2). Positions verticales estimées.',
  cols=[
   dict(n='1', w=500, units=[
     dict(y=10, h=10, k='drawer', dep=T9ID[0], plate='yellow', label='Transfert fuel domestique n°2 7PM26'),
     dict(y=20, h=10, k='drawer', dep=T9ID[1], plate='yellow', label='Compresseur air instrum secours 7KM07', counter=False),
     dict(y=34, h=3, k='plate', node='TS9_ISA', plate='black', label='INTERRUPTEUR GÉNÉRAL ISOLEMENT JdB-A'),
     dict(y=42, h=3, k='plate', node='TS9_QS', plate='black', label='ARRIVÉE SECOURS GROUPE 1'),
     dict(y=50, h=3, k='plate', node='TS9_QA', plate='black', label='ARRIVÉE TS17A'),
     dict(y=54, h=7, k='arc', label='ATTENTION Risque Classe 0'),
   ], doors=[(0, 10), (10, 20), (20, 30), (30, 80)]),
   dict(n='', w=400, units=[
     dict(y=13, h=6, k='meter', label='Centrale de mesure'),
     dict(y=36, h=8, k='paper', label='Consigne secours photographiée — manoeuvres à valider'),
     dict(y=46, h=8, k='ats', label='Automate permutation sources « A ↔ forçage / A ↔ auto »'),
     dict(y=43, h=3, k='plate', dep=T9ID[2], plate='black', x=0.72, label='7M21 COFFRET Cde SIRÈNES AL. INCENDIE'),
     dict(y=48, h=3, k='plate', dep=T9ID[3], plate='white', x=0.72, label='Alim. commande C1 tours de refroidissement'),
   ], doors=[(0, 80)]),
   dict(n='2', w=550, units=[dict(y=12, h=10, k='bluetags', label='Étiquettes bleues relevées le 15/10/2026 (rang supérieur)', tags=[
       'COFFRET ALIM BUTANE', 'CONTROLE DIESEL EAU FROIDE', 'PRIMAIRE TRANSFO 380 - 110',
       'ECL SECOURS CHAUFFERIE', 'DEPART COFFRET ALARME PORTAIL SNCF', 'ECLAIRAGE SECOURS GROUPES',
       'SECONDAIRE TRANSFO 380 - 110', 'SECHEUR AIR', 'INSTRUMENTATION CHAUFFERIE']), dict(y=28, h=8, k='bluetags', label='Étiquettes bleues relevées le 15/10/2026 (rang inférieur)', tags=[
       'ALIM VIGILHOM', '7 PM 20', 'RESERVE', 'ALIM 110 V', '7M15 CONTROLE DIESEL', 'ALARME CHAUFFERIE']), dict(y=34, h=2, k='blank')], doors=[(0, 12), (12, 80)]),
   dict(n='3', w=500, units=[
     dict(y=10, h=3, k='plate', dep=T9ID[4], plate='black', label='7M08-7M09. ALIM. COFFRET CHAUDIÈRE 1et2'),
     dict(y=10, h=8, k='arc', x=0.55, label='ATTENTION Risque Classe 0 — Tableau TR2B TS17B TS9 CHAUDIÈRE — 400 V — 1,62 kA — 0,19 cal/cm² — 14,91 cm'),
     dict(y=19, h=3, k='plate', dep=T9ID[5], plate='black', label='7M13. ARMOIRE Cde DIESEL POMPE EAU FROIDE'),
     dict(y=27, h=3, k='plate', dep=T9ID[6], plate='black', label='AUXILIAIRES GROUPE 2'),
     dict(y=35, h=3, k='plate', dep=T9ID[7], plate='black', label='AUXILIAIRES GROUPE 1'),
     dict(y=43, h=3, k='plate', dep=T9ID[8], plate='black', label='7PM043. CHAUFFAGE DIESEL PROCESS'),
     dict(y=51, h=3, k='plate', node='TS9_QC', plate='black', label='COUPLAGE JEU DE BARRES'),
     dict(y=63, h=3, k='plate', dep=T9ID[9], plate='black', label='PRISE PS CHAUFFERIE'),
     dict(y=69, h=3, k='plate', dep=T9ID[10], plate='black', label='PM05. VOLET CHAUFFERIE'),
   ], doors=[(0, 6), (6, 80)]),
   dict(n='4', w=550, units=[
     dict(y=14, h=11, k='drawer', dep=T9ID[11], plate='red', label='AE7P025 400V'),
     dict(y=25, h=11, k='drawer', dep=T9ID[12], label='Tiroir 2 (étiquette illisible)', counter=False),
     dict(y=38, h=3, k='plate', dep=T9ID[13], plate='black', label='ARMOIRE SILO KAOLIN'),
     dict(y=44, h=3, k='plate', dep=T9ID[14], plate='black', label='SÉCHEUR 7K121'),
     dict(y=49, h=3, k='plate', dep=T9ID[15], plate='black', label='SÉCHEUR 7K122'),
     dict(y=56, h=4, k='plate', dep=T9ID[16], plate='black', label='DÉPART RÉCHAUFFEUR 7.5KW 7K121'),
     dict(y=63, h=4, k='plate', dep=T9ID[17], plate='black', label='DÉPART RÉCHAUFFEUR 7.5KW 7K122'),
     dict(y=73, h=3, k='plate', node='TS9_QB', plate='black', label='ARRIVÉE B NORMALE TS17B'),
   ], doors=[(0, 14), (14, 25), (25, 36), (36, 80)]),
   dict(n='', w=330, units=[dict(y=16, h=6, k='meter', label='Centrale de mesure')], doors=[(0, 80)]),
  ])

# Tableaux SM6 (cellules depuis l'unifilaire)
def sm6(cells):
    return [dict(t=t, label=l, node=n, ref=r) for (t, l, n, r) in cells]
F['SS1_20'] = dict(style='sm6', title='TABLEAU 20 KV — SOUS-STATION 1', src=UNI, conf='Ordre et type des cellules selon l’unifilaire ; apparence SM6 type (photos Tableau 20kv SS1)',
  cells=sm6([('PF', 'Parafoudres', None, 'Varisil HD 24'), ('DM1', 'TR 6A', 'SS1_C6A', '010'), ('DM1', 'TR 5A', 'SS1_C5A', '010'), ('DM1', 'TR 4A', 'SS1_C4A', '01'),
   ('DM1', 'TR 3A', 'SS1_C3A', '02'), ('DM1', 'TR 1A', 'SS1_C1A', '01A'), ('DM1', 'TR 2A', 'SS1_C2A', '02A'), ('IM', 'Arrivée A1', 'SS1_A1', 'A1E'),
   ('CPL', 'Couplage V500', 'SS1_V500', 'V500'), ('CPL2', 'Couplage V500 (remontée)', 'SS1_V500', 'V500'), ('IM', 'Arrivée A2', 'SS1_A2', 'A2E'),
   ('DM1', 'TR 1B', 'SS1_C1B', '01'), ('DM1', 'TR 2B', 'SS1_C2B', '02'), ('DM1', 'TR 3B', 'SS1_C3B', '03'), ('DM1', 'TR 4B', 'SS1_C4B', '04'),
   ('QM', 'TR 5B', 'SS1_C5B', '020'), ('DM1', 'TR 6B', 'SS1_C6B', '—'), ('PF', 'Parafoudres', None, 'Varisil HD 24')]))
F['SS2_20'] = dict(style='sm6', title='TABLEAU 20 KV — SOUS-STATION 2', src=UNI, conf='Ordre et type des cellules selon l’unifilaire ; photos SS2 non identifiées',
  cells=sm6([('DM1', 'TR Hydrogène', 'SS2_CHYD', 'Sx'), ('DM1', 'AEF1-TRZ2 B&B', 'SS2_CZ2', 'Sx'), ('DM1', 'AEF2-TR2 Boosting T2', 'SS2_CBT2', '001'),
   ('DM1', 'TR 9A', 'SS2_C9A', '01'), ('DM1', 'TR 7A', 'SS2_C7A', '02'), ('DM1', 'Boosting 3200 kVA', 'SS2_CB1', '03'), ('CM', 'Mesure TT', None, 'Sch. 3182748'),
   ('PF', 'Parafoudres', None, ''), ('IM', 'Arrivée A3', 'SS2_A3', 'A3E'), ('CPL', 'Couplage', 'SS2_CPL', ''), ('CPL2', 'Couplage (remontée)', 'SS2_CPL', ''),
   ('IM', 'Arrivée A4', 'SS2_A4', 'A4E'), ('PF', 'Parafoudres', None, ''), ('CM', 'Mesure TT', None, 'Sch. 3182749'), ('DM1', 'Boosting 3200 kVA', 'SS2_CB2', '012'),
   ('DM1', 'TR 7B', 'SS2_C7B', '01'), ('DM1', 'TR 9B', 'SS2_C9B', 'xx'), ('DM1', 'AEF2-TR1 Boosting T1', 'SS2_CBT1', '002'), ('DM1', 'AEF1-TRZ1 B&B', 'SS2_CZ1', 'Sx')]))
F['PL20'] = dict(style='sm6', title='POSTE DE LIVRAISON 20 KV', src=UNI, conf='Ordre et type des cellules selon l’unifilaire',
  cells=sm6([('DM1', 'A — Secours EDF (04)', 'PL_A04', 'CS-400A'), ('CM', 'Mesure TT EDF', None, 'CS-50A'), ('IM', 'Interrupteur 400A', None, '400A-CIT'), ('PF', 'Parafoudres', None, '400A-CIT'),
   ('PF', 'Parafoudres', None, '400A-CIT'), ('IM', 'Interrupteur 400A', None, '400A-CIT'), ('CM', 'Mesure TT CNR', None, 'CS-50A'), ('DM1', 'B — Normal CNR (01)', 'PL_B01', 'CS-400A')]))
F['KV6'] = dict(style='sm6', title='TABLEAU 6 KV — FOUR N°2', src=UNI, conf='Ordre et type des cellules selon l’unifilaire ; apparence SM6 (photos Tableau 6kv)',
  cells=sm6([('QM', 'AEF2-D6 Spang L6', 'KV6_D6', '200A'), ('QM', 'AEF2-D5 Spang L5', 'KV6_D5', '200A'), ('QM', 'AEF2-D4 Spang L4', 'KV6_D4', '200A'), ('DM1', 'AEF2-A2 Arrivée', 'KV6_A2', ''),
   ('CPL', 'AEF2-C Couplage', 'KV6_C', ''), ('DM1', 'AEF2-A1 Arrivée', 'KV6_A1', ''), ('QM', 'AEF2-D3 Spang L3', 'KV6_D3', '200A'), ('QM', 'AEF2-D2 Spang L2', 'KV6_D2', '200A'), ('QM', 'AEF2-D1 Spang L1', 'KV6_D1', '200A')]))

# --------------------------------------------------------------------------- procédures documentées / entretien
PROCS = [
 dict(id='P-TR3A', title='Exploitation des verrouillages par serrures — Cellule DJ-TR3A', board='TGBT3', ents=['TGBT3_QA', 'SS1_C3A', 'TR3A'],
      status='Document constructeur (Schneider Electric) — validation de l’exploitant requise', src=T3LOCK,
      but=['INTERDIRE la fermeture du sectionneur de terre de la cellule « DJ-TR3A » tant que le circuit de commande du groupe n’est pas mis hors service.',
           'INTERDIRE l’accès au transformateur de puissance tant que le sectionneur de terre de la cellule disjoncteur n’est pas verrouillé dans la position FERMÉ.',
           'INTERDIRE la manœuvre en charge du sectionneur de ligne.',
           'INTERDIRE l’accès au disjoncteur et aux transformateurs de courant, sectionneur de ligne fermé.',
           'PERMETTRE la manœuvre à vide du disjoncteur, sectionneur de ligne ouvert.'],
      steps=['Ouvrir et verrouiller ouvert le disjoncteur BT QTR3A (la clé A3A est libre).',
             'Porter la clé A3A sur la serrure de condamnation du sectionneur de terre de la cellule « DJ-TR3A ».',
             'Ouvrir et verrouiller « ouvert » le disjoncteur de la cellule « DJ-TR3A » (récupérer la clé D3A libre).',
             'À l’aide de la clé D3A déverrouiller, ouvrir et verrouiller « ouvert » le sectionneur de ligne (la 1re clé D3A est prisonnière et la 2e clé D3A est libre).',
             'Possibilité de faire les essais à vide du disjoncteur à l’aide de la 2e clé D3A.',
             'À l’aide de la clé A3A déverrouiller et fermer le sectionneur de terre de la cellule « DJ-TR3A » (la clé A3A devient prisonnière).',
             'Enlever le panneau de la cellule « DJ-TR3A » (le sectionneur de terre peut être rouvert, la clé A3A reste prisonnière).',
             'Panneau de la cellule « DJ-TR3A » enlevé, prendre la clé T3A à l’intérieur.',
             'À l’aide de la clé T3A, déverrouiller l’un des volets de condamnation des bornes du transformateur (ces volets ôtés, la clé T3A reste prisonnière).'],
      warn='ATTENTION : les parties figurées en rouge sur le plan doivent être considérées comme restant sous tension après l’exécution des manœuvres énumérées. DÉFENSE D’OUVRIR TANT QUE LES CONDUCTEURS DE CE COMPARTIMENT N’ONT PAS ÉTÉ MIS HORS TENSION.'),
 dict(id='P-TR3B', title='Exploitation des verrouillages par serrures — Cellule DJ-TR3B', board='TGBT3', ents=['TGBT3_QB', 'SS1_C3B', 'TR3B'],
      status='Document constructeur (Schneider Electric, scan transcrit le 12/10/2026) — validation de l’exploitant requise',
      src='p1 - Copie.zip › 12_TGBT N°3 › Verrouillage DJ TR3B.pdf',
      but=['INTERDIRE la fermeture du sectionneur de terre de la cellule « DJ-TR3B » tant que le circuit de commande du groupe n’est pas mis hors service.',
           'INTERDIRE l’accès au transformateur de puissance tant que le sectionneur de terre de la cellule disjoncteur n’est pas verrouillé dans la position FERMÉ.',
           'INTERDIRE la manœuvre en charge du sectionneur de ligne.',
           'INTERDIRE l’accès au disjoncteur et aux transformateurs de courant, sectionneur de ligne fermé.',
           'PERMETTRE la manœuvre à vide du disjoncteur, sectionneur de ligne ouvert.'],
      steps=['Ouvrir et verrouiller ouvert le disjoncteur BT QTR3B (la clé A3B est libre).',
             'Porter la clé A3B sur la serrure de condamnation du sectionneur de terre de la cellule « DJ-TR3B ».',
             'Ouvrir et verrouiller « ouvert » le disjoncteur de la cellule « DJ-TR3B » (récupérer la clé D3B libre).',
             'À l’aide de la clé D3B déverrouiller, ouvrir et verrouiller « ouvert » le sectionneur de ligne (la 1re clé D3B est prisonnière et la 2e clé D3B est libre).',
             'Possibilité de faire les essais à vide du disjoncteur à l’aide de la 2e clé D3B.',
             'À l’aide de la clé A3B déverrouiller et fermer le sectionneur de terre de la cellule « DJ-TR3B » (la clé A3B devient prisonnière).',
             'Enlever le panneau de la cellule « DJ-TR3B » (le sectionneur de terre peut être rouvert, la clé A3B reste prisonnière).',
             'Panneau de la cellule « DJ-TR3B » enlevé, prendre la clé T3B à l’intérieur.',
             'À l’aide de la clé T3B, déverrouiller l’un des volets de condamnation des bornes du transformateur (ces volets ôtés, la clé T3B reste prisonnière).'],
      warn='ATTENTION : les parties figurées en rouge sur le plan doivent être considérées comme restant sous tension après l’exécution des manœuvres énumérées. DÉFENSE D’OUVRIR TANT QUE LES CONDUCTEURS DE CE COMPARTIMENT N’ONT PAS ÉTÉ MIS HORS TENSION.'),
 dict(id='P-TGBT3-SRC', title='TGBT 3 — Choix de source (clés Ronis)', board='TGBT3', ents=['TGBT3_QA', 'TGBT3_QB', 'TGBT3_QC'],
      status='Règle constructeur (plan CX781001 p.15) — aucune séquence fournie', src=T3DOC,
      but=['Permutation des sources à la charge de l’exploitant.', 'Combinaisons autorisées QTR3A / QC / QTR3B : 1-0-1, 0-1-1, 1-1-0 (jamais trois appareils fermés).'], steps=[], warn=None),
]
PROCS.append(dict(id='P-ATS', title='Poste de livraison — permutation automatique CNR (normal) → EDF (secours)', board='PL20', ents=['PL_A04', 'PL_B01', 'SRC_CNR', 'SRC_EDF'],
      status='Fonctionnement décrit par l’exploitant (10/10/2026) — cohérent avec l’unifilaire (disjoncteurs SF1 : « Décl. Manque 24VCC », « Fermeture 24VCC », « Armement 110VCC »)',
      src='Indication exploitant + ' + UNI,
      but=['Sur défaut (manque de tension) de l’alimentation principale CNR, la bobine à manque de tension provoque l’ouverture de l’arrivée CNR (cellule B, disj. 01).',
           'Le secours EDF (cellule A, disj. 04) prend alors le relais automatiquement et réalimente les tableaux 20 kV des deux sous-stations (arrivées A1/A3).',
           'À préciser par l’exploitant : temporisations, conditions de retour sur CNR (automatique ou manuel), interverrouillage empêchant la fermeture simultanée des deux arrivées, délestages éventuels.'],
      steps=[], warn=None))
nodes['PL_A04']['note'] = 'Secours EDF : fermeture automatique sur manque de tension CNR (permutation automatique, indication exploitant).'
nodes['PL_B01']['note'] = 'Arrivée normale CNR : ouverture par bobine à manque de tension sur défaut d’alimentation, bascule automatique vers EDF.'
for b in ('TGBT1', 'TGBT2', 'TGBT4', 'TGBT5', 'TGBT6', 'TGBT7', 'TGBT8', 'TGBT9', 'TS9', 'SS1_20', 'SS2_20', 'KV6', 'PL20'):
    PROCS.append(dict(id=f'P-{b}', title=f'{boards[b]["name"]} — procédure de changement de source / consignation', board=b, ents=[],
                      status='À FOURNIR — aucune procédure validée dans les documents transmis', src=None, but=[], steps=[], warn=None))

# --------------------------------------------------------------------------- façades relevées sur photos (module séparé)
import os as _os
exec(open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'facades_photo.py'), encoding='utf-8').read())
for d in deps.values(): d.pop('_fac', None)
exec(open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'unifilaire_detail.py'), encoding='utf-8').read())

# --------------------------------------------------------------------------- implantation (PowerPoint « PLAN IMPLANTATION 2 » + « site l ardoise »)
PPT = 'PLAN IMPLANTATION 2.pptx'
SITEP = 'site l ardoise.pptx'
LOC.clear()
LOC.update({
 'SITE': dict(name='Usine OCF — Laudun-l’Ardoise', parent=None, kind='site'),
 'PL': dict(name='Poste de livraison CNR / EDF', parent='SITE', kind='poste', bat=33),
 'SS1': dict(name='Sous-station 1', parent='SITE', kind='poste', bat=25, plan=['PLAN_SS1G', 'PLAN_SS1D'],
             note='Nom du plan d’implantation. Les documents électriques numérotent cette salle « S/STATION 2 » (unifilaire, classeur onglet TR 7) : voir incohérence de numérotation.'),
 'SS1G': dict(name='SS1 — côté gauche', parent='SS1', kind='salle', plan=['PLAN_SS1G']),
 'SS1D': dict(name='SS1 — côté droit', parent='SS1', kind='salle', plan=['PLAN_SS1D']),
 'SS2': dict(name='Sous-station 2', parent='SITE', kind='poste', bat=31, plan=['PLAN_SS2'],
             note='Nom du plan d’implantation. L’unifilaire nomme son tableau 20 kV « S/STATION 1 » et les étiquettes du TGBT 4 indiquent « SST 1 » : voir incohérence de numérotation.'),
 'CHAUF': dict(name='Local chaufferie', parent='SITE', kind='salle', bat=11, plan=['PLAN_CHAUF']),
 'STEP': dict(name='STEP', parent='SITE', kind='salle', bat=13, plan=['PLAN_STEP']),
 'TERRAIN': dict(name='Ateliers et bâtiments', parent='SITE', kind='zone'),
})
RELOC = {
 'PL20': ('PL', 'confirme'), 'SS1_20': ('SS2', 'confirme'), 'SS2_20': ('SS1G', 'confirme'), 'KV6': ('SS1D', 'confirme'), 'GORGE': ('SS1D', 'confirme'),
 'TGBT1': ('SS2', 'confirme'), 'TGBT2': ('SS2', 'confirme'), 'TGBT3': ('SS2', 'confirme'), 'TGBT4': ('SS2', 'confirme'), 'TGBT5': ('SS2', 'confirme'), 'TGBT6': ('SS2', 'confirme'),
 'TGBT7': ('SS1G', 'confirme'), 'TGBT9': ('SS1G', 'confirme'), 'TGBT8': ('SS1G', 'probable'),
 'GRADATHYR': ('SS1G', 'confirme'), 'VARIVOLT': ('SS1G', 'confirme'), 'COND7': ('SS1G', 'confirme'), 'COND9': ('SS1G', 'confirme'), 'VENTIL': ('SS1G', 'probable'), 'ARM110': ('SS1G', 'probable'),
 'TS2': ('SS2', 'confirme'), 'ECLSST1': ('SS2', 'confirme'), 'OND1': ('SS2', 'confirme'), 'OND2': ('SS2', 'confirme'),
 'COND1': ('SS2', 'confirme'), 'COND2A': ('SS2', 'confirme'), 'COND2B': ('SS2', 'confirme'), 'COND3': ('SS2', 'probable'), 'COND4': ('SS2', 'confirme'),
 'COND5A': ('SS2', 'confirme'), 'COND5B': ('SS2', 'confirme'), 'COND6A': ('SS2', 'confirme'), 'COND6B': ('SS2', 'confirme'),
 'TS9': ('CHAUF', 'confirme'), 'TS17': ('CHAUF', 'confirme'), 'DECARBO': ('CHAUF', 'confirme'), 'TS16': ('STEP', 'confirme'),
 'BRONZINI': ('TERRAIN', 'confirme'), 'TS12': ('TERRAIN', 'probable'), 'TS44': ('TERRAIN', 'probable'), 'TS7': ('TERRAIN', 'probable'),
 'TS46A': ('TERRAIN', 'probable'), 'TS46B': ('TERRAIN', 'probable'), 'PEG': ('TERRAIN', 'probable'),
}
for bid, (l, c) in RELOC.items():
    boards[bid]['loc'], boards[bid]['loc_conf'] = l, c
    boards[bid]['loc_src'] = PPT if l in ('SS1G', 'SS1D', 'SS2', 'CHAUF', 'STEP') else SITEP
boards['SS1_20'].update(name='Tableau 20 kV CNR / EDF — TR 1 à 6 (Sous-station 2)', alias='Unifilaire : « S/STATION 1 - 20KV » · plan : « TABLEAU ARRIVÉE 20 KV CNR EDF »',
                        photos=['Tableau 20kv edf cnr .pdf p1-p24'])
boards['SS2_20'].update(name='Tableau 20 kV — TR 7, TR 9, Boosting (Sous-station 1)', alias='Unifilaire : « S/STATION 2 - 20KV » · plan : « Tableau 20kv » (SS1 côté gauche)',
                        photos=['Tableau 20kv SS1.pdf p1-p16', 'Tableau 20kv   SS1.pdf p1-p10', 'Tableau 20kv     SS1.pdf p1-p24'])
boards['PL20'].update(name='Poste de livraison 20 kV CNR / EDF', photos=['Départ 20kv edf cnr.pdf p1-p21'])
boards['KV6']['name'] = 'Tableau 6 kV — Four 2 (Sous-station 1 côté droit)'
boards['ECLSST1']['name'] = 'Armoire éclairage sous-station'
boards['GORGE']['name'] = 'Tableau Gorge (Four 2)'
boards['TGBT7']['alias'] = 'Plan d’implantation : « Tr7 b »'
nodes['SS1_BL']['label'] = '20 kV TR 1-6 (SS2) — demi-JdB gauche'; nodes['SS1_BR']['label'] = '20 kV TR 1-6 (SS2) — demi-JdB droit'
nodes['SS2_BL']['label'] = '20 kV TR 7/9 (SS1) — demi-JdB gauche'; nodes['SS2_BR']['label'] = '20 kV TR 7/9 (SS1) — demi-JdB droit'
nodes['SS1_V500']['label'] = 'Couplage V500 — tableau 20 kV TR 1-6'
nodes['SS2_CPL']['label'] = 'Couplage — tableau 20 kV TR 7/9'
F['SS1_20']['title'] = 'TABLEAU 20 KV ARRIVÉE CNR / EDF — TR 1 À 6 (SOUS-STATION 2)'
F['SS2_20']['title'] = 'TABLEAU 20 KV — TR 7 / TR 9 / BOOSTING (SOUS-STATION 1)'
for i in issues:
    if i['id'] == 'I-LOC':
        i.update(sev='basse', title='Implantation physique des TGBT (résolue par le plan)',
                 text='Localisations reprises du plan d’implantation : TGBT 1 à 6, TS 2, tableau 20 kV arrivée CNR/EDF, condensateurs et onduleurs en Sous-station 2 ; TGBT 9, « Tr7 b » (TGBT 7), tableau 20 kV, gradathyr, varivolt, boosting en Sous-station 1 côté gauche ; tableau 6 kV, Gorge et Spang côté droit ; TS 9 / TS 17 en chaufferie ; TS 16 à la STEP.')
    if i['id'] == 'I-SS2PH':
        i.update(title='Photos des tableaux 20 kV', text='Les fichiers « Tableau 20kv SS1 » (3 séries) sont rattachés au tableau 20 kV de la Sous-station 1 du plan (TR 7/9) et « Tableau 20kv edf cnr » au tableau d’arrivée CNR/EDF de la Sous-station 2 : rattachement déduit des noms de fichiers, à confirmer.')
ISSUE('I-SSNUM', 'haute', 'Numérotation des sous-stations différente selon les documents',
      'Plan d’implantation (exploitant) : Sous-station 2 = TGBT 1 à 6 + tableau 20 kV CNR/EDF ; Sous-station 1 = TGBT 9, TGBT 7, boosting, 6 kV. '
      'Unifilaire : « S/STATION 1 - 20KV » = tableau des TR 1 à 6, « S/STATION 2 - 20KV » = tableau des TR 7/9/boosting/6 kV. Étiquettes TGBT 4 « SST 1 » et rapport Schneider TGBT 1 « Sous station N°1 » ; plan Schneider TGBT 3 « Sous-station 2 » ; classeur onglet TR 7 « Sous/station n°2 ». '
      'L’application utilise la numérotation du plan d’implantation et rappelle l’appellation de l’unifilaire dans chaque fiche. À harmoniser (risque d’erreur lors d’une consignation).',
      [PPT, UNI, XL, T1RPT, T3DOC], ['SS1_20', 'SS2_20', 'TGBT1', 'TGBT3', 'TGBT4'])

# --------------------------------------------------------------------------- tableaux HTA et TGBT 8 reconstruits sur photos (module séparé)
exec(open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'hta_photo.py'), encoding='utf-8').read())

# --------------------------------------------------------------------------- corrections et ajouts de l'audit du 11/10/2026 (relus sur les sources)
exec(open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'audit_2026_10_11.py'), encoding='utf-8').read())

# TS8 : nouvelle façade relevée sur terrain (aucune attribution de circuit par simple position).
exec(open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'ts8_photo.py'), encoding='utf-8').read())

# --------------------------------------------------------------------------- registre documentaire
INV = json.load(open(sys.argv[1].replace('excel.json', 'inv.json'), encoding='utf-8')) if False else None

data = dict(
  meta=dict(app='OCC ÉNERGIE', version='1.16', built='2026-10-12', data='Dossier Plan électrique relu le 12/10/2026 (classeur, unifilaire, photos, archives p1*.zip : verrouillage TR3B, PV France Transfo, schémas DM1 Varivolt)', unifilaire='Owens Corning R112529 — UNIFILAIRE HTA/BT — rév. H', site='Usine OCF à Laudun'),
  loc=LOC, nodes=list(nodes.values()), edges=edges, boards=list(boards.values()), facades=F, issues=issues, procs=PROCS,
  xl_left=[dict(sheet=s, cell=c, label=l) for s, c, l in left], **D_EXTRA)
json.dump(data, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('nœuds', len(nodes), 'arêtes', len(edges), 'tableaux', len(boards), 'départs', len(deps), 'incohérences', len(issues))
