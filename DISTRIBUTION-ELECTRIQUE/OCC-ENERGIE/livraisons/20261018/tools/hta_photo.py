"""Tableaux HTA reconstruits cellule par cellule à partir des photos (exécuté par build_data.py après unifilaire_detail.py).

Lecture faite le 11/10/2026 sur les photos à pleine résolution :
  « Tableau 20kv edf cnr .pdf » (24 p.) + « Départ 20kv edf cnr.pdf » (21 p.) = MÊME tableau : 20 kV CNR / EDF — TR 1 à 6 (Sous-station 2)
  « Tableau 20kv SS1.pdf » (16 p.), « Tableau 20kv   SS1.pdf » (10 p.), « Tableau 20kv     SS1.pdf » p12-p24 = tableau 20 kV TR 7 / 9 / boosting
  « Tableau 20kv     SS1.pdf » p1-p11 = tableau BT TR 8 (TGBT 8 — boosting, armoires Gradathyr zones creuset)
  « Tableau 6kv.pdf » (13 p.) = tableau 6 kV Four 2
  Aucune photo du poste de livraison CNR / EDF.

Description d'une cellule (dessin « sm6p ») :
  t      : type SM6 (DM1 disjoncteur, IM interrupteur, QM combiné fusibles, PF parafoudres, CM mesure, CPL couplage, CPL2 remontée)
  w      : largeur (375 ou 750 mm) ; plate / pc : texte de la plaque (« | » = retour à la ligne) et couleur (red / black / tag)
  band   : couleur du bandeau [gauche, droite] : white, cream, green (cellule Schneider récente, liseré vert)
  L, R   : contenu du bandeau gauche / droit : vN indicateurs de présence tension, lN voyants, bN boutons noirs
  top    : coffret BT haut (lv : relais Easergy, mid : coffret simple, cover : capot bas) ; mech : commande (dm1, im, pfm, cpl, blank, panel)
  brand  : MG (Merlin Gerin) ou SE (Schneider Electric) ; key : clé visible ; keybox : boîte à clés ; floor : coffret au sol devant la cellule
"""
T20 = 'Tableau 20kv edf cnr .pdf p1-p24 + Départ 20kv edf cnr.pdf p1-p21'
T79 = 'Tableau 20kv SS1.pdf p1-p16 · Tableau 20kv   SS1.pdf p1-p10 · Tableau 20kv     SS1.pdf p12-p24'
T6 = 'Tableau 6kv.pdf p1-p13'

def _dm1(node, plate, band, L='v3', R='v1 l4', **kw):
    return dict(t='DM1', w=750, node=node, plate=plate, pc=kw.pop('pc', 'red'), band=band, L=L, R=R, top='lv', mech='dm1', lock=True, floor=True, brand=kw.pop('brand', 'MG'), **kw)

# ---------------------------------------------------------------------------- 20 kV CNR / EDF — TR 1 à 6 (Sous-station 2)
SS1_CELLS = [
    dict(t='PF', w=375, plate='DÉPART 20kV|PARAFOUDRE CÔTÉ A', pc='red', band=['white'], L='', top='cover', mech='pfm', lock=True, brand='MG', label='Parafoudres côté A'),
    _dm1('SS1_C6A', 'DÉPART 20kV|TRANSFORMATEUR 6A', ['white', 'white'], L='v1', R='l4', sel=True, label='TR 6A'),
    _dm1('SS1_C5A', 'DÉPART 20kV|TRANSFORMATEUR 5A', ['white', 'white'], L='l4', R='v2', label='TR 5A'),
    _dm1('SS1_C4A', 'DÉPART 20kV|TRANSFORMATEUR 4A', ['cream', 'cream'], label='TR 4A'),
    _dm1('SS1_C3A', 'DÉPART 20kV|TRANSFORMATEUR 3A', ['white', 'cream'], label='TR 3A'),
    _dm1('SS1_C2A', 'DÉPART 20kV|TRANSFORMATEUR 2A', ['green', 'green'], R='l4 v1', brand='SE', label='TR 2A'),
    _dm1('SS1_C1A', 'DÉPART 20kV|TRANSFORMATEUR 1A', ['green', 'green'], R='l4 v1', brand='SE', label='TR 1A',
         note='Photo : cellule condamnée par un moraillon rouge et une étiquette de consignation le jour de la prise de vue.'),
    dict(t='IM', w=375, node='SS1_A1', plate='ARRIVÉE SECOURS EDF|PROVIENT DE|POSTE DE LIVRAISON', pc='red', band=['white'], L='l2 b2 l1', top='mid', mech='im', lock=True, brand='SE', label='Arrivée A1 (secours EDF)'),
    dict(t='CPL2', w=500, node='SS1_V500', plate='TABLEAU 20kV', pc='red', band=['white'], top='mid', mech='panel', brand='MG', label='Tableau 20 kV (remontée de barres)'),
    dict(t='CPL', w=750, node='SS1_V500', plate='COUPLAGE TABLEAU 20kV', pc='red', band=['white', 'white'], L='', R='', top='mid', mech='cpl', keybox='A2 · A1E · A3E / A1C · A3C · A1', brand='MG', label='Couplage V500'),
    dict(t='IM', w=375, node='SS1_A2', plate='ARRIVÉE NORMALE CNR|PROVIENT DE|POSTE DE LIVRAISON', pc='red', band=['white'], L='l2 b2 l1', top='mid', mech='im', lock=True, brand='MG', label='Arrivée A2 (normal CNR)'),
    _dm1('SS1_C1B', 'DÉPART 20kV|TRANSFORMATEUR 1B', ['white', 'cream'], label='TR 1B'),
    _dm1('SS1_C2B', 'DÉPART 20kV|TRANSFORMATEUR 2B', ['cream', 'cream'], label='TR 2B'),
    _dm1('SS1_C3B', 'DÉPART 20kV|TRANSFORMATEUR 3B', ['cream', 'cream'], label='TR 3B'),
    _dm1('SS1_C4B', 'DÉPART 20kV|TRANSFORMATEUR 4B', ['cream', 'cream'], label='TR 4B'),
    _dm1('SS1_C5B', 'DÉPART 20kV|TRANSFORMATEUR 5B', ['white', 'white'], L='l4', R='v2', label='TR 5B'),
    _dm1('SS1_C6B', 'DÉPART 20kV|TRANSFORMATEUR 6B', ['white', 'white'], L='v2', R='l3', sel=True, label='TR 6B'),
    dict(t='PF', w=375, plate='DÉPART 20kV|PARAFOUDRE CÔTÉ B', pc='red', band=['white'], L='', top='cover', mech='pfm', lock=True, brand='MG', label='Parafoudres côté B'),
]
F['SS1_20'].update(style='sm6p', cells=SS1_CELLS, src=T20,
    conf='Reconstruction cellule par cellule sur photos (18 cellules) : plaques rouges, bandeaux blancs / crème / liseré vert (cellules Schneider récentes TR 1A et TR 2A), relais Easergy, indicateurs de présence tension, voyants, cadenas jaunes, boîtes à clés. '
         'Côté A, les plaques donnent TR 2A puis TR 1A contre l’arrivée secours EDF (ordre symétrique du côté B : arrivée CNR, TR 1B, TR 2B…).')

# ---------------------------------------------------------------------------- 20 kV TR 7 / TR 9 / boosting (Sous-station 1)
BK = dict(pc='black')
SS2_CELLS = [
    _dm1('SS2_CHYD', 'Départ hydrogène', ['green', 'green'], L='', R='l3 v3', pc='tag', brand='SE', label='TR Hydrogène', note='Plaque manuscrite jaune (cellule Schneider récente).'),
    _dm1('SS2_CZ2', 'VARIVOLT ZONE 2 FOUR 03-01', ['green', 'green'], L='', R='l3 v3', brand='SE', label='AEF1-TRZ2 (Varivolt zone 2)', **BK),
    _dm1('SS2_CBT2', 'PROTECTION TRANSFO|BOOSTING 10A FOUR 02', ['white', 'white'], L='l4', R='v2', label='AEF2-TR2 boosting', conf='a_verifier', note='Plaque lue partiellement.', **BK),
    _dm1('SS2_C9A', 'PROTECTION TRANSFO TR9 A', ['cream', 'cream'], L='', R='v3 l4', label='TR 9A', **BK),
    _dm1('SS2_C7A', 'DÉPART TR7 A', ['white', 'white'], L='v3 l4 b3', R='v1', label='TR 7A', **BK),
    _dm1('SS2_CB1', 'DÉPART BOOSTING|TR 8 A', ['cream', 'cream'], L='v3', R='v1 l4', label='Boosting TR 8A', **BK),
    dict(t='CM', w=375, plate='RÉFÉRENCE TENSION|JDB A SECOURS', pc='black', band=['white'], L='box', top='mid', mech='blank', brand='MG', label='Mesure TT A'),
    dict(t='PF', w=375, plate='CELLULE PARAFOUDRE|JDB A SECOURS', pc='black', band=['cream'], L='', top='mid', mech='pfm', lock=True, brand='MG', label='Parafoudres A'),
    dict(t='IM', w=375, node='SS2_A3', plate='ARRIVÉE SECOURS A|POSTE DE LIVRAISON', pc='black', band=['cream'], L='l2 l1', top='mid', mech='im', lock=True, brand='MG', label='Arrivée A3 (secours)'),
    dict(t='CPL', w=375, node='SS2_CPL', plate='COUPLAGE', pc='black', band=['white'], L='arc', top='mid', mech='cpl', brand='MG', label='Couplage', note='Étiquette « ATTENTION Risque Classe 4 » (risque d’arc).'),
    dict(t='CPL2', w=375, node='SS2_CPL', plate='COUPLAGE|TABLEAU 20 KV', pc='black', band=['white'], top='mid', mech='panel', brand='MG', label='Remontée de barres'),
    dict(t='IM', w=375, node='SS2_A4', plate='ARRIVÉE NORMALE B|POSTE DE LIVRAISON', pc='black', band=['cream'], L='l2 l1', top='mid', mech='im', lock=True, key='A4C', brand='MG', label='Arrivée A4 (normal)'),
    dict(t='PF', w=375, plate='CELLULE PARAFOUDRE|JDB B NORMAL', pc='black', band=['cream'], L='', top='mid', mech='pfm', lock=True, brand='MG', label='Parafoudres B'),
    dict(t='CM', w=375, plate='RÉFÉRENCE TENSION|JDB B NORMAL', pc='black', band=['white'], L='box', top='mid', mech='blank', brand='MG', label='Mesure TT B'),
    _dm1('SS2_CB2', 'DÉPART BOOSTING|TR 8 B', ['cream', 'cream'], L='v3', R='v1 l4', label='Boosting TR 8B', **BK),
    _dm1('SS2_C7B', 'DÉPART TR7 B', ['white', 'white'], L='v3 l4 b3', R='v1', label='TR 7B', **BK),
    _dm1('SS2_C9B', 'PROTECTION TRANSFO TR9 B', ['white', 'white'], L='l4', R='v2', label='TR 9B', **BK),
    _dm1('SS2_CBT1', 'PROTECTION TRANSFO|BOOSTING (côté B)', ['white', 'white'], L='l4', R='v2', label='AEF2-TR1 boosting', conf='a_verifier', note='Plaque peu lisible sur les photos.', **BK),
    _dm1('SS2_CZ1', 'VARIVOLT ZONE 1 FOUR 03-01', ['green', 'green'], L='', R='l3 v3', brand='SE', label='AEF1-TRZ1 (Varivolt zone 1)', **BK),
]
F['SS2_20'].update(style='sm6p', cells=SS2_CELLS, src=T79,
    conf='Reconstruction cellule par cellule sur photos (19 cellules), dans l’ordre de l’unifilaire (confirmé par les plaques) : plaques noires gravées, bandeaux blancs / crème / liseré vert (cellules Schneider récentes : hydrogène, Varivolt zones 1 et 2).')

# ---------------------------------------------------------------------------- 6 kV Four 2 (Sous-station 1 côté droit) — ordre vu de face sur les photos
KV_CELLS = [
    dict(t='QM', w=375, node='KV6_D1', plate='GROUPE SPANG|(plaque illisible)', pc='black', band=['white'], L='l4 v1', top='lv', mech='im', lock=True, brand='SE', est=True, label='Spang L1 (position estimée)'),
    dict(t='QM', w=375, node='KV6_D2', plate='GROUPE SPANG|(plaque illisible)', pc='black', band=['white'], L='l4 v1', top='lv', mech='im', lock=True, brand='SE', est=True, label='Spang L2 (position estimée)'),
    dict(t='QM', w=375, node='KV6_D3', plate='GROUPE SPANG|(plaque illisible)', pc='black', band=['white'], L='l4 v1', top='lv', mech='im', lock=True, brand='SE', est=True, label='Spang L3 (position estimée)'),
    _dm1('KV6_A1', 'ARRIVÉE TRANSFO BOOSTING|A FOUR 02', ['white', 'white'], L='l4 b3', R='v2', brand='SE', label='Arrivée A (AEF2-A1)', **BK),
    dict(t='CPL2', w=375, node='KV6_C', plate='TABLEAU 6 KV', pc='black', band=['white'], top='mid', mech='panel', brand='SE', label='Remontée de barres'),
    dict(t='CPL', w=375, node='KV6_C', plate='COUPLAGE BOOSTING A/B', pc='black', band=['white'], L='l4', top='lv', mech='cpl', brand='SE', label='Couplage AEF2-C'),
    _dm1('KV6_A2', 'ARRIVÉE TRANSFO BOOSTING|B FOUR 02', ['white', 'white'], L='l4 b3', R='v2', brand='SE', label='Arrivée B (AEF2-A2)', **BK),
    dict(t='QM', w=375, node='KV6_D6', plate='GROUPE SPANG L6', pc='black', band=['white'], L='l4 v1', top='lv', mech='im', lock=True, brand='SE', label='Spang L6'),
    dict(t='QM', w=375, node='KV6_D5', plate='GROUPE SPANG L5', pc='black', band=['white'], L='l4 v1', top='lv', mech='im', lock=True, brand='SE', label='Spang L5'),
    dict(t='QM', w=375, node='KV6_D4', plate='GROUPE SPANG L4', pc='black', band=['white'], L='l4 v1', top='lv', mech='im', lock=True, brand='SE', label='Spang L4'),
]
F['KV6'].update(style='sm6p', cells=KV_CELLS, src=T6,
    conf='Reconstruction sur photos (cellules Schneider SM6, plaques noires) dans l’ordre vu de face : groupes Spang, arrivée transfo boosting A, « TABLEAU 6 KV », couplage boosting A/B, arrivée transfo boosting B, groupes Spang L6, L5, L4. '
         'Plaques des groupes côté A illisibles (L1 à L3 placés selon l’unifilaire, positions estimées).')

# ---------------------------------------------------------------------------- poste de livraison : aucune photo
F['PL20']['conf'] = 'AUCUNE PHOTO du poste de livraison : cellules dessinées d’après l’unifilaire seulement (CS-400A · CS-50A · 400A-CIT · 400A-CIT EDF | CNR).'
F['PL20']['nophoto'] = True

# ---------------------------------------------------------------------------- rattachement des photos corrigé
boards['PL20']['photos'] = []
boards['PL20']['note'] = 'Aucune photo transmise du poste de livraison. Le fichier « Départ 20kv edf cnr.pdf » montre le tableau 20 kV CNR / EDF TR 1 à 6 de la Sous-station 2 (plaques « parafoudre côté B », « transformateur 5B / 6B »).'
boards['SS1_20']['photos'] = ['Tableau 20kv edf cnr .pdf p1-p24', 'Départ 20kv edf cnr.pdf p1-p21']
boards['SS2_20']['photos'] = ['Tableau 20kv SS1.pdf p1-p16', 'Tableau 20kv   SS1.pdf p1-p10', 'Tableau 20kv     SS1.pdf p12-p24']
boards['TGBT8']['photos'] = ['Tableau 20kv     SS1.pdf p1-p11']
boards['TGBT8']['it'] = 'localisateurs XL308 arrivées 1 et 2 (photo)'
boards['TGBT8']['note'] = (boards['TGBT8'].get('note') or '') + ' Photos : « Tableau 20kv     SS1.pdf » p1-p11 — armoires « ARRIVÉE 1 » (étiquette « TRANFO 8B », risque d’arc « JEU DE BARRE TR8B »), « ARRIVÉE 2 », « COUPLAGE », « CONTRÔLE », « ARMOIRE PUISSANCE NORMAL - SECOURS » et armoires « GRADATHYR ZONE N° … CREUSET ».'

# ---------------------------------------------------------------------------- TGBT 8 (boosting) — façade sur photos
T8 = 'Tableau 20kv     SS1.pdf p1-p11'
def _grad(n, zone, m=None, est=False, nodep=False):
    u = [dict(y=4, h=3, k='plate', label=f'GRADATHYR / ZONE N°{zone} - CREUSET', plate='black', x=.5, **({'m': m} if m else {}), **({'nodep': True} if nodep else {}), **({'est': True} if est else {})),
         dict(y=20, h=11, k='hmi'), dict(y=34, h=6, k='voy'), dict(y=42, h=4, k='sel'), dict(y=52, h=10, k='handle'), dict(y=66, h=10, k='grille')]
    return dict(n=n, w=800, units=u)
facade('TGBT8', 'TGBT8', 'armoire_grise', 'TGBT N°8 — BOOSTING / GRADATHYR CREUSET', T8,
  'Armoires relevées sur photos : arrivées, couplage et contrôle lisibles ; ordre des armoires Gradathyr en partie estimé (vues de biais). '
  'Arrivée 1 = transformateur 8B (étiquette), arrivée 2 = 8A (déduit). Zones rattachées aux départs « ZONE 1 à 6 » du classeur.', brand='MERLIN GERIN', cols=[
  _grad('G1', '3.1', m=r'^ZONE 3$'),
  _grad('G2', '4.1', m=r'^ZONE 4$'),
  _grad('G3', '4.2', nodep=True),
  dict(n='1', w=800, units=[
    dict(y=3, h=3, k='plate', label='ARRIVÉE 1', plate='black', x=.5, nodep=True),
    dict(y=7, h=6, k='arc', label='ATTENTION Risque Classe 4 — Tableau JEU DE BARRE TR8B', x=.5),
    dict(y=14, h=14, k='nw', node='TGBT8_QB', label='TRANFO 8B', plate='blue', model='Masterpact NW (Micrologic)'),
    dict(y=31, h=5, k='voy'),
    dict(y=40, h=3, k='plate', label='CONTRÔLE', plate='black', x=.5, nodep=True),
    dict(y=45, h=6, k='gauge', label='TENSION ARR. 1'),
    dict(y=55, h=4, k='sel'),
    dict(y=63, h=6, k='imd2', label='XL308 arrivée 1 · XL308 arrivée 2'),
  ], doors=[(2, 38), (38, 77)]),
  dict(n='2', w=800, units=[
    dict(y=3, h=3, k='plate', label='ARRIVÉE 2', plate='black', x=.5, nodep=True),
    dict(y=7, h=6, k='arc', label='ATTENTION Risque Classe 4', x=.5),
    dict(y=14, h=14, k='nw', node='TGBT8_QA', label='ARRIVÉE 2 (TR 8A)', plate='black', model='Masterpact NW (Micrologic)'),
    dict(y=31, h=5, k='voy'),
    dict(y=40, h=3, k='plate', label='COUPLAGE', plate='black', x=.5, nodep=True),
    dict(y=45, h=14, k='nw', node='TGBT8_QC', label='COUPLAGE', plate='black', model='Masterpact NW'),
  ], doors=[(2, 38), (38, 77)]),
  dict(n='S', w=800, units=[
    dict(y=4, h=3, k='plate', label='ARMOIRE PUISSANCE / NORMAL - SECOURS', plate='black', x=.5, nodep=True),
    dict(y=22, h=8, k='mod2'), dict(y=34, h=6, k='voy'), dict(y=42, h=4, k='sel'),
  ], doors=[(2, 77)]),
  _grad('G4', '5', m=r'^ZONE 5$', est=True),
  _grad('G5', '6', m=r'^ZONE 6$', est=True),
  _grad('G6', '1 / 2 (non lue)', m=r'^ZONE 1$', est=True),
])
for z in ('ZONE 2',):
    pass  # zone 2 : armoire non identifiée sur les photos — départ conservé sans position de façade

# ---------------------------------------------------------------------------- incohérences et compléments
for i in issues:
    if i['id'] == 'I-TR12':
        i['text'] += (' — Photos du tableau 20 kV (Sous-station 2) : les plaques gravées donnent, côté A, « TRANSFORMATEUR 2A » puis « TRANSFORMATEUR 1A » contre l’arrivée secours EDF, '
                      'symétriquement au côté B (arrivée CNR, 1B, 2B…). L’unifilaire place TR 1A puis TR 2A : nouvel indice que l’unifilaire inverse 1A et 2A. À confirmer par le suivi des câbles.')
        if 'Tableau 20kv edf cnr .pdf' not in i['refs']: i['refs'].append('Tableau 20kv edf cnr .pdf p6, p9')
    if i['id'] == 'I-SS2PH':
        i.update(sev='basse', title='Photos des tableaux 20 kV (tri effectué)',
                 text='Tri fait sur les photos : « Tableau 20kv edf cnr » et « Départ 20kv edf cnr » = tableau 20 kV TR 1 à 6 (Sous-station 2) ; « Tableau 20kv SS1 » (3 séries) = tableau 20 kV TR 7 / 9 / boosting, sauf « Tableau 20kv     SS1 » p1-p11 = TGBT 8 (boosting). Aucune photo du poste de livraison.')
ISSUE('I-PDLPH', 'moyenne', 'Poste de livraison CNR / EDF : aucune photo',
      'Le fichier « Départ 20kv edf cnr.pdf », d’abord rattaché au poste de livraison, montre le tableau 20 kV TR 1 à 6 de la Sous-station 2. La façade du poste de livraison reste dessinée d’après l’unifilaire seul.',
      ['Départ 20kv edf cnr.pdf'], ['PL20'])
ISSUE('I-KV6ORD', 'basse', 'Tableau 6 kV : ordre des groupes Spang',
      'Photos : à droite de l’arrivée transfo boosting B, les plaques donnent L6, L5 puis L4 en bout de tableau ; l’unifilaire dessine L4 contre l’arrivée et L6 en bout. Plaques des groupes côté A illisibles (positions L1 à L3 estimées). '
      'Correspondance des arrivées A / B avec les cellules 20 kV « boosting » à vérifier sur place.', [T6, UNI], ['KV6', 'KV6_D4', 'KV6_D6', 'KV6_A1', 'KV6_A2'])
boards['VARIVOLT']['note'] = (boards['VARIVOLT'].get('note') or '') + ' Le tableau 20 kV TR 7/9 porte deux cellules « VARIVOLT ZONE 1 FOUR 03-01 » et « VARIVOLT ZONE 2 FOUR 03-01 » (unifilaire : AEF1-TRZ1 / TRZ2) : alimentation probable des Varivolt, à confirmer.'

# =============================================================================== documents des archives ZIP (dossiers 10, 11, 12, 20, 22)
# --- TGBT 3 : transformateurs et gaine à barres (p1 - Copie.zip › 12_TGBT N°3 › 1 - Plan de réalisation TQC)
ZTR = 'p1 - Copie.zip › 12_TGBT N°3 › TRANSFORMATEUR › TR2 / TR3 (France Transfo : plan d’ensemble, procès-verbaux d’essais n° 1466597 et 1466588 du 28-29/01/2025, schémas de câblage)'
ZGB = 'p1 - Copie.zip › 12_TGBT N°3 › GAINE A BARRES › P46268 00B / 01B / 02B (Schneider Canalis)'
for t in ('TR3A', 'TR3B'):
    n = nodes[t]
    n['maker'] = 'France Transfo — Trihal (sec enrobé)'
    n['note'] = ((n.get('note') + ' ') if n.get('note') else '') + (
        'Dossier TGBT 3 : deux transformateurs Trihal 2000 kVA, 20 000 V / 410 V, Dyn11, Ucc 6 %, secs enrobés classe F, refroidissement AN, 4 410 kg, 2 336 × 1 280 × 2 725 mm, IP31, '
        'surveillance de température par sondes et relais NT935 ; n° de série 1466597 (« TR2 » du fournisseur) et 1466588 (« TR3 ») — correspondance avec TR 3A / TR 3B à confirmer. '
        'Liaison BT vers le TGBT 3 : gaine à barres Canalis KTA 3200 A 3P+N+PE IP55 (2 liaisons, plans P46268).')
    n['src'] = (n.get('src') or '') + ' ; ' + ZTR
for q in ('TGBT3_QA', 'TGBT3_QB'):
    nodes[q]['note'] = ((nodes[q].get('note') + ' ') if nodes[q].get('note') else '') + 'Raccordement au transformateur par gaine à barres Canalis KTA 3200 A 3P+N+PE IP55 (plans P46268).'
boards['TGBT3']['docs'] += [ZTR, ZGB]
for i in issues:
    if i['id'] == 'I-TR-KVA':
        i.update(sev='basse', title='TR 3A / 3B : 2000 kVA confirmé par les plaques ; type de surveillance à vérifier',
                 text='Les documents France Transfo du dossier TGBT 3 (n° 1466597 et 1466588, essais de janvier 2025) donnent 2000 kVA, Trihal sec enrobé, surveillance par sondes de température. '
                      'L’unifilaire indique « DGPT2 » (protection des transformateurs immergés) pour TR 3B : si TR 3B est l’un de ces Trihal, la protection est par sondes, pas par DGPT2. '
                      'Les plans Schneider TGBT 2 et 3 indiquent toujours « 2000 kVA (2500 kVA) » avec des arrivées 3520 A (réserve de puissance). Plaques de TR 2A / 2B non fournies.')
        i['refs'].append(ZTR)

# --- Varivolt : cellules DM1-A (p1 - Copie (2).zip › 20_VARIVOLT)
for nid, z in (('SS2_CZ1', '1'), ('SS2_CZ2', '2')):
    n = nodes[nid]; zs = f'p1 - Copie (2).zip › 20_VARIVOLT › schema DM1 départ varivolt zone {z}.pdf (Schneider S000119797, 2023, 42 folios)'
    n['model'] = 'SM6 24 kV DM1-A 400 A — sectionneur CS 400 A + disjoncteur SF1 type 1 RI 400 A'
    n['keys'] = f'X0{z}01 · S0{z}01 · O0{z}01 (clés tubulaires, verrouillages type 50 + « protection transfo BT » C4-D)'
    n['note'] = ((n.get('note') + ' ') if n.get('note') else '') + (
        f'Dossier constructeur : cellule repère client 0{z}101, extension par la {"droite" if z == "1" else "gauche"} du tableau ; TC 3 × ARM3/N2F 200-100/5 A (cl. 0,5s et 5P15), '
        'VPIS V2, tore CSH120, câble 3 × (1 × 240 mm²) maxi, auxiliaires 110 V CC ; réseau 20 kV, 12,5 kA, neutre impédant.')
    n['src'] = (n.get('src') or '') + ' ; ' + zs
    PROCS.append(dict(id=f'P-VARIVOLT{z}', title=f'Verrouillages par serrures — cellule DM1-A « départ Varivolt zone {z} »', board='SS2_20', ents=[nid],
        status='Document constructeur (Schneider Electric, 2023) — validation de l’exploitant requise', src=zs + ' folios 9-10',
        but=['Interdire la manœuvre en charge du sectionneur de ligne.',
             'Interdire l’accès au disjoncteur et aux transformateurs de courant si le sectionneur de ligne n’est pas « OUVERT ».',
             'Permettre la manœuvre à vide du disjoncteur, sectionneur de ligne ouvert.',
             'Interdire la fermeture du sectionneur de terre et l’accès au disjoncteur et aux têtes de câbles tant que le disjoncteur BT n’est pas verrouillé « OUVERT » ou « DÉBROCHÉ ».',
             'Interdire l’accès au transformateur si le sectionneur de terre de la cellule n’a pas été fermé au préalable.'],
        steps=[], warn=f'Clés X0{z}01, S0{z}01, O0{z}01. L’ordre détaillé des manœuvres est sur les folios 9 et 10 du document constructeur (non retranscrit ici pour éviter une erreur d’ordre).'))
boards['VARIVOLT']['docs'] = (boards['VARIVOLT'].get('docs') or []) + ['p1 - Copie (2).zip › 20_VARIVOLT (schémas DM1 zones 1 et 2, plaque 26013)']

# --- coffrets ondulés étuves (p1 - Copie (2).zip › 22_Onduleurs › plan coffret ondulé étuve…)
ZCO = 'p1 - Copie (2).zip › 22_Onduleurs › Coffret ondulée étuve {k}.pdf (plan du 01/12/2024, folios 03-04, nomenclature)'
for k, feeder, rows in (
    ('1', 'D0446', [('Q03.05', 'ÉTUVE 1'), ('Q03.06', 'ÉTUVE 2'), ('Q03.07', 'ÉTUVE 3'), ('Q03.08', 'ÉTUVE 4'), ('Q03.09', 'ÉTUVE 5'), ('Q03.10', 'ÉTUVE 6'),
                    ('Q04.01', 'GÉNÉRATEUR 1'), ('Q04.02', 'GÉNÉRATEUR 3'), ('Q04.03', 'BAIE INFORMATIQUE'), ('Q04.04', 'RÉSERVE')]),
    ('2', 'D0450', [('Q03.05', 'ÉTUVE 7'), ('Q03.06', 'ÉTUVE 8'), ('Q03.07', 'ÉTUVE 9'), ('Q03.08', 'ÉTUVE 10'), ('Q03.09', 'GÉNÉRATEUR 2'), ('Q03.10', 'RÉSERVE'),
                    ('Q04.01', 'RÉSERVE'), ('Q04.02', 'RÉSERVE'), ('Q04.03', 'BAIE INFORMATIQUE'), ('Q04.04', 'RÉSERVE')])):
    if feeder not in nodes: continue
    bid, src = f'COFOND{k}', ZCO.format(k=k)
    sub(bid, f'Coffret ondulé étuves {"1 à 6" if k == "1" else "7 à 10"}', kind='Coffret', loc='TERRAIN', loc_conf='probable', docs=[src],
        note='Arrivée : interrupteur-sectionneur Q03.01 4 × 63 A (Legrand) puis disjoncteur Q03.02 iC60N 4 × 63 A avec bobine MX commandée par l’arrêt d’urgence du coffret ; '
             'voyant « sous tension ». Départs iC60N courbe C. Alimenté par ' + nodes[feeder]['label'] + '.')
    N(f'{bid}_Q', 'cb', 'Arrivée Q03.02 iC60N 4 × 63 A + MX (arrêt d’urgence)', board=bid, role='arrivee_ts', case='Q03.02', model='iC60N 4P 63 A courbe C + MX', conf='confirme', src=src,
      note='Un appui sur l’arrêt d’urgence du coffret ouvre ce disjoncteur (bobine MX) : le réarmer après déverrouillage de l’arrêt d’urgence.')
    E(feeder, f'{bid}_Q', src); E(f'{bid}_Q', f'{bid}_J', src)
    nodes[feeder]['feeds'] = bid
    for case, lab in rows:
        dep(bid, f'{bid}_J', lab, src, case=case, model='iC60N 2P ' + ('20 A' if case == 'Q04.03' or (k == '1' and case == 'Q04.04') or (k == '2' and case == 'Q04.04') else '16 A') + ' courbe C')
for b in ('OND1', 'OND2'):
    boards[b]['docs'] = (boards[b].get('docs') or []) + ['p1 - Copie (2).zip › 22_Onduleurs › Master UPS › procédure IPSOS « RAZ Riello Multi Dialog MDM-MDT » (onduleur concerné à confirmer)']
