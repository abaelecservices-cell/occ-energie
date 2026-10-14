"""Façades relevées sur les photographies (exécuté par build_data.py, accès à nodes, deps, boards, F, dep(), E(), ISSUE()).

Chaque unité de façade :
  y, h   : position verticale / hauteur en modules (0-80, 80 = 2200 mm ; pour Okken y = numéro de case)
  k      : type d'appareil dessiné (nw, ns, nsx, plate, meter, voy, imd, drawer, window, …)
  label  : texte exact de l'étiquette (séparateur « / » = retour à la ligne)
  m      : expression régulière pour retrouver un départ déjà connu (classeur, plan constructeur) du même tableau
  half   : demi-jeu de barres (A / B) quand la façade crée le départ
  node   : nœud existant (arrivée, couplage) représenté par l'unité
  feeds  : tableau alimenté (création de la liaison électrique)
"""
import re as _re

PHOTO_DEPS = []

def _find(board, pat, half=None):
    rx = _re.compile(pat, _re.I)
    for d in deps.values():
        if d['board'] == board and rx.search(d['label']) and (half is None or d.get('half') == half) and not d.get('_fac'):
            return d['id']
    return None

def _absorb(did, board, pat):
    """Fusionne un départ du classeur (doublon) dans le départ de la façade : la référence Excel est conservée, le doublon supprimé."""
    other = _find(board, pat)
    if not other or other == did: return
    o = nodes[other]
    if o.get('xl') and not nodes[did].get('xl'): nodes[did]['xl'] = o['xl']
    elif o.get('xl'): nodes[did]['xl2'] = o['xl']
    for e in [e for e in edges if e['a'] == other or e['b'] == other]:
        if e['b'] == other: edges.remove(e)
        elif e['a'] == other:
            e['a'] = did
            if o.get('feeds'): nodes[did]['feeds'] = o['feeds']
    nodes.pop(other); deps.pop(other, None)

def _by_case(board, case):
    for d in deps.values():
        if d['board'] == board and d.get('case') == case and not d.get('_fac'): return d['id']
    return None

def facade(fid, board, style, title, src, conf, cols, brand='MERLIN GERIN', note=None):
    out_cols = []
    for c in cols:
        units = []
        for u in c.get('units', []):
            u = dict(u)
            half = u.pop('half', None) or c.get('half')
            if 'node' in u:
                n = nodes[u['node']]
                for k in ('case', 'model', 'ir'):
                    if u.get(k): n[k] = u[k]
                if u.get('label'): n['plate'] = u['label']
                n['src'] = (n.get('src') or '') + f' ; façade : {src}'
            elif u.get('label') and u.get('k') not in ('blank', 'arc', 'paper', 'bluetags', 'meter', 'voy', 'voy2', 'mod2', 'imd', 'temp', 'ats', 'imd2', 'sel', 'win0', 'hmi', 'grille', 'estop', 'gauge', 'varlogic', 'handle') and not u.get('nodep'):
                did = u.pop('did', None) or (_by_case(board, u['mc']) if u.get('mc') else None)
                if not did and u.get('m'): did = _find(board, u['m'], half)
                lab = u['label'].replace(' / ', ' — ')
                if did and not u.get('est'):   # le libellé affiché devient celui de l'étiquette du tableau ; l'ancien libellé (classeur / plan) est conservé
                    nodes[did]['label_plan'] = nodes[did]['label']; nodes[did]['label'] = lab
                if did:
                    d = nodes[did]
                    d['photo_label'] = lab
                    d['src'] = f'{src} (étiquette « {lab} ») ; ' + d['src']
                    d['conf'] = 'confirme'
                else:
                    bus = f'{board}{half}' if board in boards and f'{board}{half}' in nodes else (half if half in nodes else None)
                    if bus is None:
                        hs = [h['id'] for h in boards[board]['halves'] if h['id'] in nodes]
                        bus = hs[0]
                    did = dep(board, bus, lab, f'{src} (étiquette)', conf=u.get('conf', 'confirme'), note=u.get('note'))
                    nodes[did]['half'] = half
                    PHOTO_DEPS.append(did)
                d = nodes[did]; d['_fac'] = True
                for k in ('case', 'model', 'ir', 'meter', 'plate'):
                    if u.get(k): d[k] = u[k]
                if u.get('note') and did not in PHOTO_DEPS: d['note'] = (d.get('note') + ' ' if d.get('note') else '') + u['note']
                if u.get('feeds'):
                    tgt = u['feeds']; tb = tgt if tgt in nodes else (boards[tgt]['halves'][0]['id'])
                    if not any(e['a'] == did and e['b'] == tb for e in edges):
                        E(did, tb, f'{src} (étiquette)', conf=u.get('conf', 'confirme'))
                    d['feeds'] = nodes[tb]['board'] if tb in nodes else tgt
                if u.get('absorb'):
                    for pat in (u['absorb'] if isinstance(u['absorb'], list) else [u['absorb']]): _absorb(did, board, pat)
                u['dep'] = did
            for k in ('m', 'mc', 'absorb', 'feeds', 'nodep', 'case', 'model', 'ir', 'conf', 'note'):
                u.pop(k, None)
            units.append(u)
        out_cols.append(dict(n=c.get('n', ''), w=c['w'], units=units, doors=c.get('doors')))
    F[fid] = dict(style=style, title=title, brand=brand, height=80, src=src, conf=conf, cols=out_cols, note=note)
    boards[board]['facade'] = fid

# =========================================================================================== TGBT 1
# Plan Schneider TGBT1A (Z0100804, face avant) + TH11A-TGBT1B (face avant unifilaire) + photos Tgbt 1.pdf p1, p2, p6, p9, p12.
T1 = 'Tgbt 1.pdf p1, p6, p9, p12 + plans TGBT1A Z0100804 / TH11A-TGBT1B 010'
facade('TGBT1', 'TGBT1', 'okken_beige', 'TGBT N°1 — SAP : 98922+101152', T1,
  'Colonnes et cases selon les plans Schneider ; étiquettes, appareils et centrales relevés sur les photos (2026).', brand='MERLIN GERIN — Okken', cols=[
  dict(n='1', w=650, half='A', units=[
    dict(y=4, h=3, k='blank', label='1A'),
    dict(y=49, h=4, k='meter', num='48'),
    dict(y=53, h=17, k='ns', label='TS 46A / CASE 1-53', case='1-53', model='Compact NS1000 4P débrochable (plan : NS1000 4P µ2.0)', plate='green', feeds='TS46A',
         note='Plan TGBT1A 2010 : « départ gr. froid 7H211 » ; étiquette actuelle : TS 46A.'),
    dict(y=72, h=7, k='ns', m=r'^Condensateur$', label='BATTERIE CONDENSATEUR 1A / SST 1 / CASE 1-72', case='1-72', model='Compact NS1000 3P débrochable', plate='green'),
  ], doors=[(4.5, 8), (8, 22), (22, 30), (30, 34), (34, 53), (53, 70), (70, 77)]),
  dict(n='2', w=650, half='A', units=[
    dict(y=26, h=19, k='nw', node='TGBT1_QA', label='PROVIENT DE TR 1A / ARRIVÉE TGBT 1A / CASE 2-28', plate='red', tr=True, case='2-28', model='Masterpact NW32H1 4P Micrologic 5.0P', ir='2816 A'),
    dict(y=55, h=4, k='plate', m=r'TS ?10', label='TS10 / ADMINISTRATIF / CASE 2-55', case='2-55', model='Compact NS630 4P (derrière porte)', plate='green'),
    dict(y=63, h=4, k='plate', m=r'TS ?7A', label='TS7A / FOUR 1 / CASE 2-63', case='2-63', model='Compact NS630 3P (derrière porte)', plate='green'),
    dict(y=70, h=4, k='plate', m=r'TS ?1 ', label='TS1 / ENSIMAGE / CASE 2-72', case='2-72', model='Compact NS630 4P (derrière porte)', plate='green'),
  ], doors=[(4.5, 10), (10, 25), (25, 45), (45, 50), (50, 77)]),
  dict(n='', w=350, half='A', units=[dict(y=14, h=4, k='meter'), dict(y=23, h=4, k='meter', num='43'), dict(y=31, h=4, k='meter', num='44'), dict(y=39, h=4, k='meter', num='45'),
    dict(y=46, h=4, k='meter', num='46'), dict(y=53, h=4, k='meter'), dict(y=58, h=2, k='voy'), dict(y=61, h=4, k='meter', num='47')], doors=[(4.5, 77)]),
  dict(n='3', w=650, half='A', units=[
    dict(y=14, h=6, k='blank', label='Tableau de repérage'),
    dict(y=22, h=6, k='imd2', label='Vigilohm IM400C + IFL12 — partie gauche'),
    dict(y=29, h=6, k='imd2', label='Vigilohm IM400C + IFL12 — partie droite'),
    dict(y=38, h=4, k='temp', label='Relais de température transfo (x2)'),
    dict(y=55, h=4, k='plate', label='COFFRET CHANTIER / SST 1 / CASE 3-35', case='3-35', model='Derrière porte', plate='green'),
    dict(y=61, h=4, k='plate', label='HVAC F2 / LOCAL HVAC SUD / CASE 3-40', case='3-40', model='Derrière porte', plate='green',
         note='Le classeur indique « HVAC Canal 3 » sur TGBT 1A et le plan 2010 « HVAC canal 3 » case 3-63 : étiquette actuelle différente.'),
    dict(y=68, h=4, k='plate', label='ATELIER AD 502 / CASE 3-72', case='3-72', model='Derrière porte', plate='green'),
  ], doors=[(4.5, 13), (13, 36), (36, 46), (46, 77)]),
  dict(n='', w=650, half='A', units=[dict(y=30, h=3, k='blank', label='PARAFOUDRE')], doors=[(4.5, 77)]),
  dict(n='4', w=650, half='B', units=[
    dict(y=26, h=19, k='nw', node='TGBT1_QC', label='COUPLAGE / TR 1A-TR 1B / CASE 4-28', plate='red', case='4-28', model='Masterpact NW32HA 4P'),
    dict(y=51, h=17, k='ns', m=r'end bushing', label='SECOURS END BUSHING F1 / FILAGE F2 / CASE 4-53', case='4-53', model='Compact NS1250N 4P', plate='green'),
    dict(y=70, h=8, k='ns', m=r'TS ?38', label='TS38 / FILIÈRE 2A12 À 2A19 / CASE 4-72', case='4-72', model='Compact NS1000N 3P', plate='green', meter='42'),
  ]),
  dict(n='5', w=650, half='B', units=[
    dict(y=11, h=6, k='mod2', label='Centrale PM + tension / intensité'),
    dict(y=26, h=19, k='nw', node='TGBT1_QB', label='PROVIENT DE TR 1B / ARRIVÉE TGBT 1B / CASE 5-28', plate='red', tr=True, case='5-28', model='Masterpact NW32H1 4P Micrologic 5.0P', ir='2816 A'),
    dict(y=51, h=17, k='ns', m=r'^Condensateur$', label='BATTERIE CONDENSATEUR 1B / SST 1 / CASE 5-53', case='5-53', model='Compact NS800N 3P', plate='green', meter='41'),
  ]),
  dict(n='6', w=650, half='B', units=[
    dict(y=26, h=17, k='ns', m=r'TS ?37', label='TS37 / FILIÈRE 2A02 À 2A09 / CASE 6-28', case='6-28', model='Compact NS1000N 3P', plate='green', meter='40'),
    dict(y=51, h=17, k='ns', label='TS 46B / CASE 6-53', case='6-53', model='ComPacT NS 4P (châssis réserve équipé)', plate='green', feeds='TS46B'),
  ]),
  dict(n='7', w=650, half='B', units=[
    dict(y=12, h=11, k='ns', label='RÉSERVE', case='7-18', model='Compact NS800N 4P Micrologic 5.0A', plate='green'),
    dict(y=25, h=50, k='window', m=r'TS ?7B', label='TS7B / FOUR 1 / CASE 7-72', case='7-72', model='Compact NSX630N 4P µ2.3 (derrière vitre, avec Multiclip 1 et sous-distribution des auxiliaires)'),
  ], doors=[(4.5, 11), (11, 24), (24, 77)]),
  dict(n='', w=250, half='B', units=[dict(y=12, h=4, k='blank', label='Condamnation'), dict(y=22, h=2, k='voy'), dict(y=26, h=4, k='meter'), dict(y=66, h=2, k='voy'), dict(y=69, h=4, k='meter', num='39')], doors=[(4.5, 77)]),
])
ISSUE('I-TGBT1B-TR2B', 'moyenne', 'Plan TGBT 1B : « ARRIVÉE TR2B »', 'Le plan Schneider TH11A-TGBT1B (face avant unifilaire et liste colonne 5) indique « ARRIVÉE TRANSFO TR2B » en case 5-28, alors que l’étiquette sur le tableau porte « PROVIENT DE TR 1B — ARRIVÉE TGBT 1B — CASE 5-28 ». Le modèle suit l’étiquette (règle TR nA / TR nB).', ['TH11A-TGBT1B.pdf', 'Tgbt 1.pdf p6'], ['TGBT1'])
ISSUE('I-TS46', 'basse', 'Origine des TS 46A / TS 46B retrouvée', 'Photos TGBT 1 : « TS 46A — CASE 1-53 » (demi-JdB A) et « TS 46B — CASE 6-53 » (demi-JdB B). Le plan TGBT1A 2010 indiquait en 1-53 « départ gr. froid 7H211 » (repris dans le classeur en « Frigo 7H214 », aujourd’hui sur le TGBT 3).', ['Tgbt 1.pdf p1, p9'], ['TS46A', 'TS46B', 'TGBT1'])

# =========================================================================================== TGBT 2
# Plan Schneider TH112001 rév. F (cases) + photos Tgbt 2.pdf p1, p3, p4, p7, p8 (étiquettes actuelles).
T2P = 'Tgbt 2.pdf p1, p3, p7, p8 + plan TH112001 rév. F'
facade('TGBT2', 'TGBT2', 'okken_blanc', 'TGBT N°2 — SAP : 43930+42931', T2P,
  'Cases et appareils selon le plan Schneider ; étiquettes, centrales et voyants relevés sur les photos.', brand='Schneider Electric — Okken', cols=[
  dict(n='1', w=650, half='A', units=[
    dict(y=26, h=17, k='ns', mc='1-28', label='SECOURS END BUSHING F2 / FILAGE F2 / CASE 1-28', absorb=r'end bushing 93\.02', plate='green', note='Plan 2014 : « DIV002 — réserve » ; étiquette actuelle : secours end bushing F2.'),
    dict(y=51, h=17, k='ns', mc='1-53', label='TS ÉTUVE 7 8 9 / HALL ÉTUVE / CASE 1-53', plate='green', meter='38'),
    dict(y=70, h=8, k='ns', mc='1-72', label='BATTERIE CONDENSATEUR 2A / SST 1 / CASE 1-72', plate='green'),
  ]),
  dict(n='2', w=650, half='A', units=[
    dict(y=16, h=17, k='ns', mc='2-18', label='TS 44 A / FILAGE F1 / CASE 2-18', plate='green'),
    dict(y=34, h=12, k='ns', mc='2-36', label='TS 2 A / SST 1 / CASE 2-36', plate='green'),
    dict(y=43, h=4, k='plate', mc='2-43', label='SOUS-DISTRIBUTION DES AUXILIAIRES', plate='green', absorb=r'^Sous distribution des auxiliaires$'),
    dict(y=49, h=20, k='window', mc='2-51', label='MULTICLIP 1'),
    dict(y=72, h=4, k='plate', mc='2-72', label='RÉSERVE', plate='green'),
  ], doors=[(4.5, 14), (14, 32), (32, 47), (47, 77)]),
  dict(n='', w=250, half='A', units=[dict(y=18, h=2, k='voy'), dict(y=21, h=4, k='meter', num='36'), dict(y=33, h=2, k='voy'), dict(y=36, h=4, k='meter', num='37')], doors=[(4.5, 77)]),
  dict(n='3', w=650, half='A', units=[
    dict(y=9, h=6, k='mod2', label='Centrale PM + tension / intensité'),
    dict(y=26, h=19, k='nw', node='TGBT2_QA', label='PROVIENT DE TR 2A / ARRIVÉE TGBT 2A / CASE 3-28', plate='red', tr=True),
  ]),
  dict(n='4', w=650, half='B', units=[
    dict(y=9, h=6, k='imd2', label='Vigilohm IM400 JdB A + JdB B'),
    dict(y=17, h=7, k='temp', label='Relais de température TR 2A / TR 2B (057 / 055 °C au relevé)'),
    dict(y=42, h=2, k='voy2'),
    dict(y=51, h=19, k='nw', node='TGBT2_QC', label='COUPLAGE / TR 2A-TR 2B / CASE 4-53', plate='red'),
  ]),
  dict(n='5', w=650, half='B', units=[
    dict(y=9, h=6, k='mod2', label='Centrale PM + tension / intensité'),
    dict(y=26, h=19, k='nw', node='TGBT2_QB', label='PROVIENT DE TR 2B / ARRIVÉE TGBT 2B / CASE 5-28', plate='red', tr=True),
  ]),
  dict(n='6', w=650, half='B', units=[
    dict(y=16, h=17, k='ns', mc='6-18', label='TS 2B / SST 1 / CASE 6-28', plate='green', note='Plan 2014 : case 6-18 ; étiquette : 6-28.'),
    dict(y=34, h=12, k='ns', mc='6-36', label='RÉSERVE', plate='green', note='Plan 2014 : « DIV001 — TS12 ROVING » ; étiquette d’origine retirée (traces de ruban adhésif), départ condamné (cadenas) au moment des photos.'),
    dict(y=43, h=4, k='plate', mc='6-43', label='SOUS-DISTRIBUTION DES AUXILIAIRES', plate='green', absorb=r'^Disj auxilliaires$'),
    dict(y=49, h=26, k='window', mc='6-51', label='COFFRET PC CHANTIER F1 / BOBINAGE F1', absorb=r'Coffret chantier Four 1', note='Plan 2014 : « Multiclip 2 » ; étiquette actuelle : coffret PC chantier F1 — bobinage F1 (le classeur L11 cite « coffret chantier Four 1 + armoire PC four 1 (secours) »).'),
    dict(y=72, h=4, k='plate', mc='6-72', label='RÉSERVE (6-72)', plate='green'),
  ], doors=[(4.5, 14), (14, 32), (32, 47), (47, 77)]),
  dict(n='', w=250, half='B', units=[dict(y=18, h=2, k='voy'), dict(y=21, h=4, k='meter', num='34'), dict(y=37, h=2, k='voy'), dict(y=40, h=4, k='meter'), dict(y=69, h=2, k='voy'), dict(y=72, h=4, k='meter', num='35')], doors=[(4.5, 77)]),
  dict(n='7', w=650, half='B', units=[
    dict(y=26, h=17, k='ns', mc='7-28', label='TS 44 B / FILAGE F1 / CASE 7-28', plate='green', meter='33'),
    dict(y=51, h=17, k='ns', mc='7-53', label='BÂTIMENT BRONZINI (CASE 7-53)', plate='green', note='Étiquette non lisible sur les photos (appareil neuf, condamné par cadenas) ; libellé selon le plan TH112001 rév. F (15/10/2024).', conf='probable'),
    dict(y=70, h=8, k='ns', mc='7-72', label='BATTERIE CONDENSATEUR 2B / SST 1 / CASE 7-72', plate='green'),
  ]),
])
_d = _by_case('TGBT2', '6-36') or next(d['id'] for d in deps.values() if d['board'] == 'TGBT2' and d.get('case') == '6-36')
nodes[_d].pop('feeds', None)
for i in issues:
    if i['id'] == 'I-TS12':
        i['text'] += ' Photos TGBT 2 : la case 6-36 porte aujourd’hui « RÉSERVE » (ancienne étiquette retirée, départ condamné) : le TS 12 n’est plus alimenté par le TGBT 2. Alimentation actuelle : TGBT 3 (TS12A case 2+18, TS12B case 5+18).'
        i['sev'] = 'basse'

# =========================================================================================== TGBT 3 (Okken neuf, MasterPacT MTZ2)
T3P = 'Tgbt 3.pdf p1 + Tgbt 3 (2).pdf p7, p12 + plan CX781001 (face avant p.22/26)'
facade('TGBT3', 'TGBT3', 'okken_blanc_vert', 'TGBT N°3 — CX781001', T3P,
  'Largeurs et cases selon le plan constructeur (colonnes 650 mm, couloirs 250 mm, longueur 4475 mm) ; appareils, centrales et étiquettes relevés sur les photos.', brand='Schneider Electric — Okken', cols=[
  dict(n='1', w=650, half='A', units=[
    dict(y=26, h=17, k='ns', mc='1+28', label='RÉSERVE', plate='green'),
    dict(y=51, h=17, k='ns', mc='1+53', label='FRIGO / 7H217', plate='green', meter='24'),
    dict(y=70, h=8, k='ns', mc='1+72', label='COND001 / BATTERIE CONDENSATEURS', plate='green'),
  ]),
  dict(n='2', w=650, half='A', units=[
    dict(y=9, h=5, k='imd2', label='Localisateur de défauts IFL12MC — JdB A'),
    dict(y=16, h=17, k='ns', mc='2+18', label='TS12A', plate='green'),
    dict(y=34, h=12, k='ns', mc='2+36', label='RÉSERVE (2+36)', plate='green'),
    dict(y=43, h=4, k='plate', mc='2+43', label='SOUS-DISTRIBUTION DES AUXILIAIRES', plate='green'),
    dict(y=49, h=24, k='window', label='MULTICLIP / AUXILIAIRES', nodep=True),
    dict(y=72, h=4, k='plate', mc='2+72', label='DIV003 — RÉSERVE', plate='green'),
  ], doors=[(6.5, 14), (14, 32), (32, 47), (47, 77)]),
  dict(n='', w=250, half='A', units=[dict(y=18, h=2, k='voy'), dict(y=21, h=4, k='meter', num='25'), dict(y=33, h=2, k='voy'), dict(y=36, h=4, k='meter'), dict(y=69, h=2, k='voy'), dict(y=72, h=4, k='meter')], doors=[(6.5, 77)]),
  dict(n='3', w=650, half='A', units=[
    dict(y=10, h=6, k='imd2', label='Vigilohm IM400 JdB A (330 kΩ) + PM + relais température TR3A'),
    dict(y=26, h=19, k='nw', node='TGBT3_QA', label='TR3A / ARRIVÉE / TRANSFO TR3A', plate='red', tr=True),
    dict(y=47, h=2, k='voy', label='Choix de source (clés Ronis) + voyants'),
    dict(y=51, h=19, k='nw', node='TGBT3_QC', label='COUPLAGE', plate='red'),
  ]),
  dict(n='4', w=650, half='B', units=[
    dict(y=10, h=6, k='imd2', label='Vigilohm IM400 JdB B (57 kΩ) + PM + relais température TR3B'),
    dict(y=26, h=19, k='nw', node='TGBT3_QB', label='TR3B / ARRIVÉE / TRANSFO TR3B', plate='red', tr=True),
    dict(y=47, h=2, k='voy'),
  ]),
  dict(n='5', w=650, half='B', units=[
    dict(y=9, h=5, k='imd2', label='Localisateur de défauts IFL12MC — JdB B'),
    dict(y=16, h=17, k='ns', mc='5+18', label='TS12B', plate='green'),
    dict(y=34, h=12, k='ns', mc='5+36', label='RÉSERVE (5+36)', plate='green'),
    dict(y=43, h=4, k='plate', mc='5+43', label='SOUS-DISTRIBUTION DES AUXILIAIRES', plate='green'),
    dict(y=49, h=24, k='window', label='MULTICLIP / AUXILIAIRES', nodep=True),
    dict(y=72, h=4, k='plate', mc='5+72', label='DIV005 — RÉSERVE', plate='green'),
  ], doors=[(6.5, 14), (14, 32), (32, 47), (47, 77)]),
  dict(n='', w=250, half='B', units=[dict(y=18, h=2, k='voy'), dict(y=21, h=4, k='meter'), dict(y=33, h=2, k='voy'), dict(y=36, h=4, k='meter'), dict(y=69, h=2, k='voy'), dict(y=72, h=4, k='meter')], doors=[(6.5, 77)]),
  dict(n='6', w=650, half='B', units=[
    dict(y=26, h=17, k='ns', mc='6+28', label='FRIGO / 7H214', plate='green'),
    dict(y=51, h=17, k='ns', mc='6+53', label='RÉSERVE (6+53)', plate='green'),
    dict(y=70, h=8, k='ns', mc='6+72', label='COND001 / BATTERIE CONDENSATEURS', plate='green'),
  ]),
])

# =========================================================================================== TGBT 5
T5P = 'Tgbt 5.pdf p2, p5, p7, p9'
facade('TGBT5', 'TGBT5', 'okken_blanc', 'TGBT N°5 — SAP : 42978+42979', T5P,
  'Relevé photo : repères de colonnes 2A · 1A · A1 · 00 · A2 · 1B · 2B, étiquettes lisibles ; proportions estimées (photos non redressées), pas de plan constructeur transmis.', brand='Merlin Gerin / Schneider Electric — Okken', cols=[
  dict(n='2A', w=650, half='A', units=[
    dict(y=12, h=3, k='plate', m=r'By-pass total onduleur 1', label='ONDULEUR 1 - BY PASS / SST 1 / CASE 2A-6', case='2A-6', model='Derrière vitre', plate='green'),
    dict(y=20, h=3, k='plate', label='LOCAL MOTEUR+REBUILT / CASE 2A-12', case='2A-12', model='Derrière vitre', plate='green', note='Le classeur place « Local moteur + local rebuilt » sur le TGBT 6A (H7) : étiquette relevée sur le TGBT 5A.'),
    dict(y=28, h=3, k='plate', m=r'Réseau 1 onduleur 1', label='ONDULEUR 1 - RÉSEAU 1 / SST 1 / CASE 2A-18', case='2A-18', model='Derrière vitre', plate='green'),
    dict(y=10, h=34, k='window', label='', nodep=True),
    dict(y=55, h=15, k='nt', m=r'^Condensateurs$', label='BATTERIE CONDENSATEUR 5A / SST 1 / CASE 2A-44', case='2A-44', model='Masterpact NT/NW Merlin Gerin (ancien)', plate='green'),
  ], doors=[(4.5, 46), (46, 77)]),
  dict(n='', w=250, half='A', units=[dict(y=13, h=5, k='imd2', label='Relais onduleur 1 by-pass'), dict(y=23, h=5, k='imd2', label='Relais local moteur + rebuilt'), dict(y=33, h=5, k='imd2', label='Relais onduleur 1 réseau 1')], doors=[(4.5, 77)]),
  dict(n='1A', w=650, half='A', units=[
    dict(y=12, h=13, k='rot', m=r'TS 34', label='TS34 / FILIÈRE 1A12 À 1A19 / CASE 1A-13', case='1A-13', model='Compact NS (commande rotative)', plate='green', meter='10'),
    dict(y=28, h=13, k='rot', m=r'TS 33', label='TS33 / FILIÈRE 1A02 À 1A09 / CASE 1A-26', case='1A-26', model='Compact NS (commande rotative)', plate='green', meter='11'),
    dict(y=45, h=12, k='rot', label='RÉSERVE (1A)', model='Châssis réserve', plate='green'),
  ]),
  dict(n='', w=250, half='A', units=[dict(y=20, h=4, k='meter', num='10'), dict(y=35, h=4, k='meter', num='11'), dict(y=52, h=4, k='meter')], doors=[(4.5, 77)]),
  dict(n='A1', w=650, half='A', units=[
    dict(y=12, h=18, k='nw', node='TGBT5_QA', label='PROVIENT DE TR 5A / ARRIVÉE TGBT 5A / CASE A1-16', plate='red', tr=True, case='A1-16', model='Masterpact NW (Micrologic)'),
    dict(y=34, h=5, k='imd2', label='Vigilohm IM400 JdB A (40 kΩ au relevé)'),
    dict(y=42, h=4, k='temp', label='Relais température TR 5A'),
  ]),
  dict(n='', w=250, half='A', units=[dict(y=12, h=6, k='imd2', label='Centrale de mesure'), dict(y=22, h=2, k='voy')], doors=[(4.5, 77)]),
  dict(n='00', w=650, half='B', units=[
    dict(y=12, h=18, k='nw', node='TGBT5_QC', label='COUPLAGE / TR 5A-TR 5B / CASE 00-16', plate='red', case='00-16', model='Masterpact NW'),
    dict(y=34, h=4, k='sel', label='Sélecteurs SA1 / SA2 / SA3'),
  ]),
  dict(n='A2', w=650, half='B', units=[
    dict(y=12, h=18, k='nw', node='TGBT5_QB', label='PROVIENT DE TR 5B / ARRIVÉE TGBT 5B / CASE A2-16', plate='red', tr=True, case='A2-16', model='Masterpact NW (Micrologic)'),
    dict(y=34, h=5, k='imd2', label='Vigilohm IM400 JdB B (41 kΩ au relevé)'),
    dict(y=42, h=4, k='temp', label='Relais température TR 5B (72 °C au relevé)'),
  ]),
  dict(n='', w=250, half='B', units=[dict(y=12, h=6, k='imd2', label='Centrale de mesure'), dict(y=22, h=2, k='voy')], doors=[(4.5, 77)]),
  dict(n='1B', w=650, half='B', units=[
    dict(y=12, h=13, k='rot', m=r'TS 36', label='TS36 / FILIÈRE 3A12 À 3A19 / CASE 1B-13', case='1B-13', model='Compact NS sous capot (poignée rouge cadenassable)', plate='green', meter='8'),
    dict(y=28, h=13, k='rot', m=r'TS 35', label='TS35 / FILIÈRE 3A02 À 3A09 / CASE 1B-26', case='1B-26', model='Compact NS sous capot (poignée rouge cadenassable)', plate='green', meter='9'),
    dict(y=45, h=12, k='rot', label='RÉSERVE (1B)', model='Châssis réserve', plate='green'),
  ]),
  dict(n='', w=250, half='B', units=[dict(y=20, h=4, k='meter', num='8'), dict(y=35, h=4, k='meter', num='9')], doors=[(4.5, 77)]),
  dict(n='2B', w=650, half='B', units=[
    dict(y=12, h=3, k='plate', label='RÉSERVE (2B)', plate='green', model='Derrière vitre'),
    dict(y=20, h=3, k='plate', m=r'Zone entreprise', label='ZONE ENTREPRISE / LOCAL SETTI / CASE 2B-12', case='2B-12', model='Derrière vitre', plate='green'),
    dict(y=28, h=3, k='plate', m=r'Réseau 2 onduleur 1', label='ONDULEUR 1 - RÉSEAU 2 / SST 1 / CASE 2B-18', case='2B-18', model='Derrière vitre', plate='green'),
    dict(y=10, h=34, k='window', label='', nodep=True),
    dict(y=55, h=15, k='nt', m=r'^Condensateur$', label='BATTERIE CONDENSATEUR 5B / SST 1 / CASE 2B-44', case='2B-44', model='Masterpact NT/NW Merlin Gerin (ancien)', plate='green'),
  ], doors=[(4.5, 46), (46, 77)]),
  dict(n='', w=250, half='B', units=[dict(y=10, h=4, k='meter'), dict(y=18, h=4, k='meter', num='7'), dict(y=27, h=5, k='imd2', label='Relais onduleur 1 réseau 2')], doors=[(4.5, 77)]),
])

# =========================================================================================== TGBT 6
T6P = 'Tgbt 6.pdf p1, p2, p4, p8, p10'
facade('TGBT6', 'TGBT6', 'okken_blanc', 'TGBT N°6 — SAP : 82034+82035', T6P,
  'Relevé photo : colonnes 2A · 1A · A1 · 00 · A2 · 1B · 2B, étiquettes lisibles ; proportions estimées, pas de plan constructeur transmis.', brand='Merlin Gerin — Okken', cols=[
  dict(n='2A', w=650, half='A', units=[
    dict(y=12, h=3, k='plate', m=r'TS 28', label='TS28 - UTILITÉS FOUR 2 / FILAGE FOUR 2 / CASE 2A-06', case='2A-06', model='Derrière vitre', plate='green', feeds='TS28'),
    dict(y=19, h=3, k='plate', label='ONDULEUR 2 - BY PASS / SST 1 / CASE 2A-12', case='2A-12', model='Derrière vitre', plate='green'),
    dict(y=26, h=3, k='plate', m=r'réseau 1 onduleur 2', label='ONDULEUR 2 - RÉSEAU 1 / SST 1 / CASE 2A-18', case='2A-18', model='Derrière vitre', plate='green'),
    dict(y=33, h=3, k='plate', m=r'^Etuve 2$', label='ÉTUVE 2 / HALL ÉTUVE / CASE 2A-24', case='2A-24', model='Derrière vitre', plate='green'),
    dict(y=10, h=34, k='window', label='', nodep=True),
    dict(y=55, h=15, k='nt', m=r'^Condensateurs$', label='BATTERIE CONDENSATEUR 6A / SST 1 / CASE 2A-44', case='2A-44', model='Masterpact NW Merlin Gerin (ancien)', plate='green'),
  ], doors=[(4.5, 46), (46, 77)]),
  dict(n='', w=250, half='A', units=[dict(y=12, h=4, k='meter', num='4'), dict(y=20, h=4, k='meter'), dict(y=28, h=4, k='meter'), dict(y=36, h=4, k='meter', num='5')], doors=[(4.5, 77)]),
  dict(n='1A', w=650, half='A', units=[
    dict(y=12, h=13, k='rot', label='RÉSERVE (1A haut)', model='Châssis réserve (cadenassé)', plate='green'),
    dict(y=28, h=13, k='rot', label='RÉSERVE (1A milieu)', model='Châssis réserve', plate='green'),
    dict(y=55, h=15, k='nt', label='END BUSHING F2 / FILAGE F2 / CASE 1A-44', case='1A-44', model='Masterpact NW Merlin Gerin', plate='green'),
  ]),
  dict(n='', w=250, half='A', units=[dict(y=12, h=4, k='meter'), dict(y=55, h=4, k='meter', num='3')], doors=[(4.5, 77)]),
  dict(n='A1', w=650, half='A', units=[
    dict(y=12, h=18, k='nw', node='TGBT6_QA', label='PROVIENT DE TR 6A / ARRIVÉE TGBT 6A / CASE A1-12', plate='red', tr=True, case='A1-12', model='Masterpact NW (Micrologic)'),
    dict(y=33, h=5, k='imd2', label='Vigilohm IM400 JdB A'),
    dict(y=42, h=4, k='temp', label='Relais température TR 6A (74 °C au relevé)'),
  ]),
  dict(n='', w=250, half='A', units=[dict(y=12, h=4, k='meter'), dict(y=21, h=4, k='mod2', label='Tension / intensité'), dict(y=27, h=2, k='voy')], doors=[(4.5, 77)]),
  dict(n='00', w=650, half='B', units=[
    dict(y=12, h=18, k='nw', node='TGBT6_QC', label='COUPLAGE / TR 6A-TR 6B / CASE 00-12', plate='red', case='00-12', model='Masterpact NW'),
    dict(y=33, h=4, k='sel', label='Sélecteurs de couplage + voyants'),
  ]),
  dict(n='A2', w=650, half='B', units=[
    dict(y=12, h=18, k='nw', node='TGBT6_QB', label='PROVIENT DE TR 6B / ARRIVÉE TGBT 6B / CASE A2-12', plate='red', tr=True, case='A2-12', model='Masterpact NW (Micrologic)'),
    dict(y=33, h=5, k='imd2', label='Vigilohm IM400 JdB B'),
    dict(y=42, h=4, k='temp', label='Relais température TR 6B (65 °C au relevé)'),
  ]),
  dict(n='', w=250, half='B', units=[dict(y=12, h=4, k='meter'), dict(y=21, h=4, k='mod2', label='Tension / intensité'), dict(y=27, h=2, k='voy')], doors=[(4.5, 77)]),
  dict(n='1B', w=650, half='B', units=[
    dict(y=12, h=13, k='rot', m=r'HVAC nord', label='HVAC F1 / LOCAL HVAC NORD / CASE 1B-13', case='1B-13', model='Compact NS (commande rotative)', plate='green', meter='2'),
    dict(y=28, h=13, k='rot', m=r'TS 40', label='TS40 / FILAGE / CASE 1B-26', case='1B-26', model='Compact NS (commande rotative)', plate='green'),
    dict(y=44, h=30, k='window', label='', nodep=True),
  ], doors=[(4.5, 26), (26, 42), (42, 77)]),
  dict(n='', w=250, half='B', units=[dict(y=12, h=4, k='meter', num='2'), dict(y=28, h=4, k='meter')], doors=[(4.5, 77)]),
  dict(n='2B', w=650, half='B', units=[
    dict(y=12, h=3, k='plate', label='(étiquette effacée, 2B haut)', model='Derrière vitre', plate='white', conf='a_verifier'),
    dict(y=26, h=3, k='plate', m=r'réseau 2 onduleur 2', label='ONDULEUR 2 - RÉSEAU 2 / SST 1 / CASE 2B-18', case='2B-18', model='Derrière vitre', plate='green'),
    dict(y=33, h=3, k='plate', m=r'^Etuve 1$', label='ÉTUVE 1 / HALL ÉTUVE / CASE 2B-24', case='2B-24', model='Derrière vitre', plate='green'),
    dict(y=10, h=34, k='window', label='', nodep=True),
    dict(y=55, h=15, k='nt', m=r'^Condensateurs$', label='BATTERIE CONDENSATEUR 6B / SST 1 / CASE 2B-44', case='2B-44', model='Masterpact NW Merlin Gerin (ancien)', plate='green'),
  ], doors=[(4.5, 46), (46, 77)]),
  dict(n='', w=250, half='B', units=[dict(y=12, h=4, k='meter'), dict(y=19, h=4, k='meter', label='Réserve'), dict(y=27, h=4, k='meter'), dict(y=35, h=4, k='meter', num='1')], doors=[(4.5, 77)]),
])

# =========================================================================================== TGBT 7
T7P = 'Tr7b .pdf p1, p3, p5, p7, p9'
facade('TGBT7', 'TGBT7', 'okken_blanc', 'TGBT 7 — TR 7A / TR 7B', T7P,
  'Relevé photo (forte surexposition) : colonnes A4 · A3 · A2 · A1 · couplage · B0 · B1 · B2 ; départs derrière vitre non lisibles, repérés par les étiquettes des voyants / centrales. À compléter.', brand='Merlin Gerin — Okken', cols=[
  dict(n='A4', w=650, half='A', units=[
    dict(y=10, h=60, k='window', label='Départs derrière vitre (étiquettes non lisibles)', nodep=True),
    dict(y=20, h=6, k='arc', label='ATTENTION Risque Classe 1 — Tableau TR7A TOUR BALTIMORE — 400 V — 10,46 kA — 1,8 cal/cm² — 58,85 cm'),
    dict(y=30, h=6, k='arc', label='ATTENTION Risque Classe 1 — Tableau TR7A AUXILIAIRES — 400 V — 19,66 kA — 2,2 cal/cm² — 66,56 cm'),
  ], doors=[(4.5, 77)]),
  dict(n='A3', w=250, half='A', units=[dict(y=12, h=2, k='voy', label='Ondulateur'), dict(y=21, h=2, k='voy'), dict(y=24, h=4, k='meter', num='49'), dict(y=31, h=2, k='voy'), dict(y=34, h=4, k='meter')], doors=[(4.5, 77)]),
  dict(n='A2', w=650, half='A', units=[
    dict(y=14, h=13, k='nt', m=r'7K122', label='AE / 7K122 / 400 V', plate='red', model='Masterpact NT (Micrologic)', note='Étiquette arc voisine : « TABLEAU TR7B 7K122 » (400 V, 13,43 kA, 3,0 cal/cm², 79,50 cm).'),
    dict(y=32, h=40, k='window', label='', nodep=True),
    dict(y=40, h=3, k='plate', m=r'Armoire éclairage Rez', label='ARMOIRE ÉCLAIRAGE FOUR 1 RDC', plate='blue', model='Derrière vitre (repère sur voyant)'),
    dict(y=48, h=3, k='plate', m=r'Tour de refroidissement', label='TOUR ERF', plate='blue', model='Derrière vitre (repère sur voyant)', meter='51'),
  ], doors=[(4.5, 29), (29, 77)]),
  dict(n='', w=250, half='A', units=[dict(y=28, h=2, k='voy', label='Compresseur 7K122'), dict(y=31, h=4, k='meter', num='50'), dict(y=38, h=2, k='voy'), dict(y=44, h=2, k='voy'), dict(y=47, h=4, k='meter', num='51')], doors=[(4.5, 77)]),
  dict(n='A1', w=650, half='A', units=[
    dict(y=4, h=6, k='arc', label='ATTENTION DANGER — JEU DE BARRE TR7A — 400 V — 18,33 kA — 101 cal/cm² — 12,42 m — INTERVENTION INTERDITE SOUS TENSION'),
    dict(y=12, h=5, k='mod2', label='PM + tension / intensité'),
    dict(y=21, h=19, k='nw', node='TGBT7_QA', label='TR 7A / ARRIVÉE TR7A', plate='black', tr=True, model='Masterpact NW (Micrologic)'),
  ]),
  dict(n='', w=650, half='B', units=[
    dict(y=21, h=12, k='temp', label='Relais de température TR7A (40 °C) / TR7B (27 °C) + Vigilohm (x2)'),
    dict(y=46, h=19, k='nw', node='TGBT7_QC', label='COUPLAGE', plate='white', model='Masterpact NW'),
  ]),
  dict(n='B0', w=650, half='B', units=[
    dict(y=4, h=6, k='arc', label='ATTENTION DANGER — JEU DE BARRE TR7B — 400 V — 18,30 kA — 101 cal/cm² — 12,42 m'),
    dict(y=12, h=5, k='mod2', label='PM + tension / intensité'),
    dict(y=21, h=19, k='nw', node='TGBT7_QB', label='TR 7B / ARRIVÉE TR7B', plate='black', tr=True, model='Masterpact NW (Micrologic)'),
  ]),
  dict(n='B1', w=650, half='B', units=[
    dict(y=14, h=13, k='nt', label='AE / 7K121 / 400 V', plate='red', model='Masterpact NT (Micrologic)', note='Le classeur place « Compresseur 7K121 » sur TGBT 7A (H6) : l’étiquette « AE 7K121 » est sur la colonne B1 (demi-JdB B). À vérifier.'),
    dict(y=32, h=40, k='window', label='', nodep=True),
    dict(y=40, h=6, k='arc', label='ATTENTION Risque Classe 1 — Tableau TR7B LAVEUR'),
    dict(y=55, h=6, k='arc', label='ATTENTION Risque Classe 1 — Tableau TR7B AUXILIAIRES'),
  ], doors=[(4.5, 29), (29, 77)]),
  dict(n='B2', w=250, half='B', units=[dict(y=18, h=2, k='voy'), dict(y=21, h=4, k='meter', num='52'), dict(y=28, h=2, k='voy'), dict(y=31, h=4, k='meter', num='53'), dict(y=38, h=4, k='meter'), dict(y=66, h=2, k='voy', label='7K123'), dict(y=69, h=4, k='meter', num='55')], doors=[(4.5, 77)]),
])
ISSUE('I-7K121', 'basse', 'Compresseurs 7K121 / 7K122 sur TGBT 7', 'Classeur « TR 7A & 7B » : compresseurs 7K121 (H6) et 7K122 (H9) sur le TGBT 7A. Photos : « AE 7K122 » en colonne A2 (demi-JdB A) mais « AE 7K121 » en colonne B1 (demi-JdB B), et l’étiquette arc de la colonne A2 mentionne « TABLEAU TR7B 7K122 ». Rattachement à vérifier.', ['Tr7b .pdf p3, p5, p9', XL], ['TGBT7'])

# =========================================================================================== TGBT 9
T9P = 'Tgbt 9.pdf p16, p18, p20, p23'
facade('TGBT9', 'TGBT9', 'okken_blanc', 'TGBT 9', T9P,
  'Relevé photo : colonnes A3 · A2 · A1 · AB · B1 · B2 · B3 ; étiquettes de départ blanches non lisibles sur les photos (seul « Groupe froid 7H215 » est lisible). Les départs du classeur restent listés dans l’onglet Départs sans position.', brand='Schneider Electric — Okken', cols=[
  dict(n='A3', w=650, half='A', units=[
    dict(y=10, h=44, k='window', label='Départs derrière vitre (étiquettes non lisibles)', nodep=True),
    dict(y=60, h=6, k='ats', label='Relais + centrale (bas de colonne A3)'),
  ], doors=[(4.5, 56), (56, 77)]),
  dict(n='A2', w=650, half='A', units=[
    dict(y=12, h=13, k='ns', label='Départ A2 haut (étiquette non lisible)', model='Compact NS débrochable', plate='white', conf='a_verifier'),
    dict(y=28, h=13, k='ns', label='Départ A2 milieu (étiquette non lisible)', model='Compact NS débrochable', plate='white', conf='a_verifier'),
    dict(y=46, h=28, k='window', label='', nodep=True),
  ], doors=[(4.5, 26), (26, 44), (44, 77)]),
  dict(n='', w=250, half='A', units=[dict(y=13, h=4, k='meter'), dict(y=20, h=2, k='voy'), dict(y=29, h=4, k='meter'), dict(y=36, h=2, k='voy')], doors=[(4.5, 77)]),
  dict(n='A1', w=650, half='A', units=[
    dict(y=10, h=2, k='voy', label='Arrivée TR9A'),
    dict(y=19, h=19, k='nw', node='TGBT9_QA', label='TR 9A / ARRIVÉE TR9A', plate='black', tr=True, model='Masterpact NW40 H1 (Micrologic)'),
    dict(y=41, h=4, k='meter', num='57'),
    dict(y=51, h=17, k='ns', label='GROUPE FROID 7H215', model='Compact NS débrochable', plate='white', note='Étiquette blanche manuscrite relevée sur la photo Tgbt 9.pdf p20.'),
  ]),
  dict(n='AB', w=650, half='B', units=[
    dict(y=19, h=12, k='temp', label='Vigilohm IM400 JdB A / JdB B + relais température TR9A (54 °C) / TR9B (68 °C)'),
    dict(y=40, h=2, k='voy2'),
    dict(y=46, h=19, k='nw', node='TGBT9_QC', label='COUPLAGE TGBT 9', plate='white', model='Masterpact NW'),
  ]),
  dict(n='B1', w=650, half='B', units=[
    dict(y=12, h=5, k='mod2', label='PM + tension / intensité'),
    dict(y=19, h=19, k='nw', node='TGBT9_QB', label='TR 9B / ARRIVÉE TR9B', plate='black', tr=True, model='Masterpact NW40 H1 (Micrologic)'),
  ]),
  dict(n='B2', w=650, half='B', units=[
    dict(y=18, h=13, k='ns', label='Départ B2 haut (étiquette non lisible)', model='Compact NS débrochable', plate='white', conf='a_verifier'),
    dict(y=38, h=13, k='ns', label='Départ B2 bas (étiquette non lisible)', model='Compact NS débrochable', plate='white', conf='a_verifier'),
  ]),
  dict(n='B3', w=650, half='B', units=[
    dict(y=12, h=10, k='ns', label='Départ B3 haut (étiquette non lisible)', model='Compact NS', plate='white', conf='a_verifier'),
    dict(y=28, h=44, k='window', label='', nodep=True),
  ], doors=[(4.5, 25), (25, 77)]),
])

# =========================================================================================== couplages et plaques relevés sur photos
CPL_PHOTO = {
 'TGBT1': ('« COUPLAGE TR 1A-TR 1B — CASE 4-28 » (Masterpact NW32HA 4P, plan TH11A-TGBT1B)', 'Tgbt 1.pdf p6, p12', '98922+101152'),
 'TGBT5': ('« COUPLAGE TR 5A-TR 5B — CASE 00-16 » (Masterpact NW, sélecteurs SA1 / SA2 / SA3)', 'Tgbt 5.pdf p5', '42978+42979'),
 'TGBT6': ('« COUPLAGE TR 6A-TR 6B — CASE 00-12 » (Masterpact NW, sélecteurs)', 'Tgbt 6.pdf p4', '82034+82035'),
 'TGBT7': ('« COUPLAGE » (Masterpact NW, colonne entre arrivées TR7A et TR7B)', 'Tr7b .pdf p5', None),
 'TGBT9': ('Couplage Masterpact NW (colonne AB, entre arrivées TR9A et TR9B)', 'Tgbt 9.pdf p20', None),
}
for b, (txt, src, sap) in CPL_PHOTO.items():
    boards[b]['coupler'] = dict(status='documente', src=src,
        rule=f'Couplage relevé sur photo : {txt}. Règle d’interverrouillage non transmise : le simulateur applique « jamais 2 transformateurs en parallèle » (2 appareils fermés sur 3).')
    nodes[f'{b}_QC']['conf'] = 'confirme'
    nodes[f'{b}_QC']['label'] = f'Couplage {boards[b]["name"]} — ' + txt.split('»')[0].replace('«', '').strip().split(' — ')[0].title() if '«' in txt else f'Couplage {boards[b]["name"]}'
    if sap: boards[b]['sap'] = sap
boards['TGBT1']['note'] = 'Merlin Gerin Okken beige, 7 colonnes + couloirs (plans Schneider TGBT1A / TH11A-TGBT1B ; photos). Neutre IT : 2 contrôleurs IM400C + localisateurs IFL12 mis en service le 29/10/2024 (préalarme 30 kΩ, alarme 2 kΩ, inhibition partie droite si passage sur couplage).'
for n in ('TGBT1_QA', 'TGBT1_QB'):
    nodes[n]['conf'] = 'confirme'

# =========================================================================================== tableaux secondaires : arrivées et couplages relevés sur photos
def add_arrivals(board, specs, coupler_label=None, coupler_src=None):
    """specs : {half_bus_id: (id_arrivee, libellé, src)} — insère l'appareil d'arrivée entre le départ amont et le jeu de barres."""
    for bus, (aid, lab, src) in specs.items():
        N(aid, 'cb', lab, board=board, half=bus[-1], role='arrivee', conf='confirme', src=src)
        for e in edges:
            if e['b'] == bus and nodes[e['a']]['t'] == 'dep' and nodes[e['a']]['board'] != board:
                e['b'] = aid
        E(aid, bus, src)
    if coupler_label:
        hs = list(specs.keys())
        N(f'{board}_QC', 'cpl', coupler_label, board=board, role='couplage', conf='confirme', src=coupler_src)
        E(hs[0], f'{board}_QC', coupler_src); E(f'{board}_QC', hs[1], coupler_src)
        boards[board]['coupler'] = dict(status='documente', src=coupler_src,
            rule='Couplage relevé sur photo. Règle d’interverrouillage non transmise : le simulateur applique « jamais 2 transformateurs en parallèle ».')

# TS 2 (Okken neuf, traits noirs) — Ts2.pdf p1, p4, p10
add_arrivals('TS2', {'TS2_A': ('TS2_QA', 'ARRIVÉE 2A — ALIM. VENANT DU TGBT N°2A', 'Ts2.pdf p4 (étiquette)'),
                     'TS2_B': ('TS2_QB', 'ARRIVÉE 2B — ALIM. VENANT DU TGBT N°2B', 'Ts2.pdf p4 (étiquette)')},
             'INTER DE COUPLAGE (TS 2)', 'Ts2.pdf p4 (étiquette)')
boards['TS2']['note'] = 'Okken Schneider (plaque « TS2 »), façade blanche à traits noirs. Arrivées 2A / 2B depuis le TGBT 2 et inter de couplage (photos). Départs moteurs en tiroirs (extracteurs et soufflage toiture étuves).'
drw = lambda y, n, lab: dict(y=y, h=5, k='drawer', label=lab, half='B', plate='white', model='Tiroir départ moteur (GV + sectionneur rotatif, marche / arrêt / défaut, réarmement)',
                             conf='probable', note='Étiquette du tiroir partiellement lisible sur Ts2.pdf p10.')
facade('TS2', 'TS2', 'okken_blanc_noir', 'TS2 — TABLEAU ÉTUVES', 'Ts2.pdf p1, p4, p10',
  'Relevé photo : colonnes 1 à 6 ; arrivées, couplage et centrales lisibles ; étiquettes de tiroirs partiellement lisibles.', brand='Schneider Electric — Okken', cols=[
  dict(n='1', w=650, half='A', units=[dict(y=6, h=40, k='window', label='Tiroirs départs moteurs (colonne 1, non relevés)', nodep=True)]),
  dict(n='2', w=650, half='A', units=[dict(y=10, h=60, k='window', label='Départs derrière vitre (non relevés)', nodep=True)]),
  dict(n='3', w=650, half='A', units=[
    dict(y=16, h=17, k='nsx', node='TS2_QA', label='ARRIVÉE 2A / ALIM. VENANT DU TGBT N°2A', plate='white', model='ComPacT NS / NSX débrochable'),
    dict(y=44, h=17, k='nsx', node='TS2_QC', label='INTER DE COUPLAGE', plate='white', model='ComPacT NS (interrupteur)'),
  ]),
  dict(n='4', w=650, half='B', units=[
    dict(y=16, h=17, k='nsx', node='TS2_QB', label='ARRIVÉE 2B / ALIM. VENANT DU TGBT N°2B', plate='white', model='ComPacT NS / NSX débrochable'),
  ]),
  dict(n='5', w=650, half='B', units=[dict(y=10, h=60, k='window', label='Départs derrière vitre', nodep=True), dict(y=50, h=4, k='meter', num='29', label='Alim étuve 5'), dict(y=56, h=4, k='meter', num='30', label='Alim étuve 6')]),
  dict(n='6', w=650, half='B', units=[
    drw(10, 1, 'EXTRACTEUR 3 TOITURE ÉTUVES / CASE 6-10'), drw(16, 2, 'EXTRACTEUR 4 TOITURE ÉTUVES / CASE 6-13'), drw(22, 3, 'SOUFFLAGE ÉTUVES / CASE 6-16'),
    drw(28, 4, 'EXTRACTEUR 5 / CASE 6-24'), drw(34, 5, 'EXTRACTEUR 6 / CASE 6-30'), drw(40, 6, 'VENTILATEUR JONCTION / CASE 6-36'), drw(46, 7, 'CHAUFFAGE / CASE 6-42'),
  ]),
])

# =========================================================================================== tableaux à tiroirs : structure relevée, départs du classeur placés dans l'ordre (positions estimées)
def bus_deps(bus):
    return [e['b'] for e in edges if e['a'] == bus and nodes[e['b']]['t'] == 'dep']
def stack(ids, y0, h=5, k='drawer', start=0, n=None, plate='black'):
    out = []
    for i, did in enumerate(ids[start:start + n if n else None]):
        out.append(dict(y=y0 + i * h, h=h, k=k, did=did, est=True, label=nodes[did]['label'][:46], plate=plate))
    return out
EST = 'Structure (colonnes, arrivées, couplage) relevée sur photos ; étiquettes des tiroirs non lisibles : les départs du classeur sont placés dans l’ordre du classeur (positions estimées, contour pointillé) — à confirmer sur site.'

# TS 44 — Okken neuf traits noirs, plaque « TS44 depuis SST1 TGBT N°2 » (Ts 44.pdf p1, p5, p11)
add_arrivals('TS44', {'TS44_A': ('TS44_QA', 'ARRIVÉE TS44 A', 'Ts 44.pdf p5 (étiquette)'), 'TS44_B': ('TS44_QB', 'ARRIVÉE TS44 B', 'Ts 44.pdf p5 (étiquette)')},
             'COUPLAGE (TS 44)', 'Ts 44.pdf p5 (étiquette)')
A44, B44 = bus_deps('TS44_A'), bus_deps('TS44_B')
facade('TS44', 'TS44', 'okken_blanc_noir', 'TS44 — DEPUIS SST1 TGBT N°2', 'Ts 44.pdf p1, p5, p11', EST, brand='Schneider Electric — Okken', cols=[
  dict(n='1', w=650, half='A', units=stack(A44, 8, 4.4, n=15)),
  dict(n='2', w=650, half='A', units=[dict(y=10, h=60, k='window', label='', nodep=True)]),
  dict(n='3', w=650, half='A', units=[dict(y=16, h=17, k='nsx', node='TS44_QA', label='ARRIVÉE TS44 A', plate='black', model='ComPacT NS débrochable'),
                                      dict(y=36, h=4, k='mod2', label='PM + voyants'), dict(y=44, h=17, k='nsx', node='TS44_QC', label='COUPLAGE', plate='black', model='ComPacT NS')]),
  dict(n='4', w=650, half='B', units=[dict(y=16, h=17, k='nsx', node='TS44_QB', label='ARRIVÉE TS44 B', plate='black', model='ComPacT NS débrochable'), dict(y=36, h=4, k='mod2', label='PM + voyants')]),
  dict(n='5', w=650, half='B', units=[dict(y=10, h=60, k='window', label='', nodep=True)]),
  dict(n='6', w=650, half='B', units=stack(B44, 8, 4.4, n=15)),
  dict(n='7', w=650, half='B', units=stack(B44, 8, 4.4, start=15, n=15)),
])
# TS 12 — Okken neuf bandeau vert (Ts 12 .pdf), deux arrivées TS12A / TS12B depuis TGBT 3
add_arrivals('TS12', {'TS12_A': ('TS12_QA', 'ARRIVÉE TS12A (depuis TGBT 3, case 2+18)', 'Ts 12 .pdf + plan CX781001'),
                      'TS12_B': ('TS12_QB', 'ARRIVÉE TS12B (depuis TGBT 3, case 5+18)', 'Ts 12 .pdf + plan CX781001')})
J12 = bus_deps('TS12_J')
facade('TS12', 'TS12', 'okken_blanc_vert', 'TS12 — EMBALLAGE / ROVING', 'Ts 12 .pdf p1-p22', EST, brand='Schneider Electric — Okken', cols=[
  dict(n='1', w=650, half='A', units=[dict(y=10, h=60, k='window', label='', nodep=True)]),
  dict(n='2', w=650, half='A', units=stack(J12, 8, 4.4, n=14)),
  dict(n='3', w=650, half='A', units=[dict(y=16, h=17, k='nw', node='TS12_QA', label='ARRIVÉE TS12A', plate='white', model='MasterPacT MTZ / ComPacT'), dict(y=36, h=4, k='mod2', label='PM + voyants'),
                                      dict(y=44, h=17, k='nw', node='TS12_QC', label='COUPLAGE', plate='white', model='MasterPacT')]),
  dict(n='4', w=650, half='B', units=[dict(y=16, h=17, k='nw', node='TS12_QB', label='ARRIVÉE TS12B', plate='white', model='MasterPacT MTZ / ComPacT'), dict(y=36, h=4, k='mod2', label='PM + voyants')]),
  dict(n='5', w=650, half='B', units=stack(J12, 8, 4.4, start=14, n=14)),
  dict(n='6', w=650, half='B', units=[dict(y=10, h=60, k='window', label='', nodep=True)]),
])
nodes['TS12_QC'].update(label='COUPLAGE TS12 (présent sur photos)', conf='probable', src='Ts 12 .pdf (appareil de couplage entre les deux arrivées)')
# TS 7 — Okken blanc traits noirs (Ts 7.pdf p8-p11) : arrivée TS7A s/station 1A, arrivée groupe électrogène n°1, isolement JdB A
A7, B7 = bus_deps('TS7_A'), bus_deps('TS7_B')
add_arrivals('TS7', {'TS7_A': ('TS7_QA', 'ARRIVÉE TS7A — S/STATION 1A', 'Ts 7.pdf p8, p11 (étiquette rouge)'), 'TS7_B': ('TS7_QB', 'ARRIVÉE TS7B', 'Classeur TR 1A & 1B O9')})
N('TS7_QG', 'cb', 'ARRIVÉE GROUPE ÉLECTROGÈNE N°1 (TS 7)', board='TS7', half='A', role='arrivee', conf='probable', src='Ts 7.pdf p8, p11 (étiquette rouge, lecture partielle)')
E('GE1', 'TS7_QG', 'Ts 7.pdf p8', conf='probable'); E('TS7_QG', 'TS7_A', 'Ts 7.pdf p8', conf='a_verifier')
facade('TS7', 'TS7', 'okken_blanc_noir', 'TS7 — FOUR 1', 'Ts 7.pdf p4-p11', EST, brand='Merlin Gerin — Okken', cols=[
  dict(n='1', w=650, half='A', units=[dict(y=10, h=60, k='window', label='', nodep=True)]),
  dict(n='2', w=650, half='A', units=stack(A7, 8, 4.4, n=13)),
  dict(n='3', w=650, half='A', units=[dict(y=12, h=6, k='plate', node='TS7_QA', label='ARRIVÉE TS7A / S/STATION 1A', plate='red'),
                                      dict(y=30, h=6, k='plate', label='ISOLEMENT JEU DE BARRES A', plate='red', nodep=True),
                                      dict(y=50, h=17, k='ns', node='TS7_QG', label='ARRIVÉE GROUPE ÉLECTROGÈNE N°1', plate='red', model='Compact NS (fond beige)')]),
  dict(n='4', w=650, half='B', units=[dict(y=12, h=6, k='plate', node='TS7_QB', label='ARRIVÉE TS7B', plate='red')] + stack(B7, 22, 4.4, n=9)),
])
ISSUE('I-GE1', 'moyenne', 'Groupe électrogène n°1 : deux tableaux secourus', 'Les photos montrent une « ARRIVÉE GROUPE ÉLECTROGÈNE N°1 » sur le TS 7 (Four 1) et une « ARRIVÉE SECOURS GROUPE 1 » sur le TS 9 (chaufferie). Le simulateur interdit de mettre le groupe en parallèle avec le réseau ; la logique réelle de permutation (automatique / manuelle) est à fournir.', ['Ts 7.pdf p8', 'Ts9.pdf p1'], ['TS7', 'TS9'])
# TS 17 A / B — Merlin Gerin Prisma beige à tiroirs (Ts17A.pdf, Ts17b.pdf)
A17, B17 = bus_deps('TS17_A'), bus_deps('TS17_B')
facade('TS17', 'TS17', 'prisma_beige', 'TS17A / TS17B — CHAUFFERIE', 'Ts17A.pdf p1-p8, Ts17b.pdf p1-p13', EST, brand='Merlin Gerin — Prisma', cols=[
  dict(n='17A-1', w=650, half='A', units=stack(A17, 8, 5, k='rot2', n=13)),
  dict(n='17A-2', w=650, half='A', units=stack(A17, 8, 5, k='rot2', start=13, n=13)),
  dict(n='', w=300, half='A', units=[dict(y=8, h=4, k='meter'), dict(y=16, h=4, k='meter')]),
  dict(n='17B-1', w=650, half='B', units=stack(B17, 8, 5, k='rot2', n=13)),
  dict(n='17B-2', w=650, half='B', units=stack(B17, 8, 5, k='rot2', start=13, n=13)),
])

# =========================================================================================== relevés à pleine résolution (11/10/2026)
# TS 44 colonne 1 : plaques gravées lues à 1:1 sur Ts 44.pdf p1 — l'ordre physique correspond à l'ordre du classeur (E13 à E18)
_c1 = F['TS44']['cols'][0]['units']
LUS44 = [('M002 — PPE EAU GLACÉE 7PM03 (AE7P003) / CASE 1-24', '1-24'), ('M001 — VENTILATEUR CHAMBRE LAVAGE N°1 4XM01 / CASE 1-30', '1-30'),
         ('M003 — POMPE CHAMBRE LAVAGE N°1 4PM01 / CASE 1-36', '1-36'), ('M006 — EXTRACTION FUMÉE HEAT WHEEL / CASE 1-42', '1-42'),
         ('M007 — EXTRACTION FUMÉE SECOURS HEAT WHEEL / CASE 1-48', '1-48'), ('M005 — ROTATION ÉCHANGEUR HEAT WHEEL N°1 / CASE 1-54', '1-54')]
for u, (lab, case) in zip(_c1, LUS44):
    u.pop('est', None); u['label'] = lab; u['plate'] = 'black'
    n = nodes[u['dep']]; n['case'] = case; n['photo_label'] = lab.replace(' / ', ' — '); n['conf'] = 'confirme'
    n['src'] = 'Ts 44.pdf p1 (plaque gravée lue à pleine résolution, lecture partielle recoupée avec le classeur) ; ' + n['src']
# TGBT 9 : plaques gravées lues à 1:1 sur Tgbt 9.pdf p20
nodes['TGBT9_QA'].update(case='A1-28', plate='ARRIVÉE TR9A — CASE A1-28')
nodes['TGBT9_QC'].update(case='AB-53', plate='COUPLAGE — CASE AB-53')
for c in F['TGBT9']['cols']:
    for u in c['units']:
        if u.get('node') == 'TGBT9_QA': u['label'] = 'ARRIVÉE TR9A / CASE A1-28'
        if u.get('node') == 'TGBT9_QC': u['label'] = 'COUPLAGE / CASE AB-53'
        if u.get('dep') and nodes[u['dep']]['label'].startswith('GROUPE FROID'):
            u['label'] = 'RÉSERVE 800 A / CASE A1-53 / (manuscrit : Groupe froid 7H215)'
            nodes[u['dep']].update(case='A1-53', model='Compact NS800 débrochable', note='Plaque gravée « RÉSERVE 800A — CASE A1-53 » ; étiquette manuscrite ajoutée « Groupe froid 7H215 ».')

# =========================================================================================== 15 armoires complémentaires (11/10/2026)
def dep_case(board, case):
    return next(d['id'] for d in deps.values() if d['board'] == board and d.get('case') == case)
def deco(y, h, k, label=None, x=None, **kw):
    u = dict(y=y, h=h, k=k, nodep=True); u.update(kw)
    if label: u['label'] = label
    if x is not None: u['x'] = x
    return u

# ---------- batteries de condensateurs (VarSet Schneider, plaques vertes « PROVIENT DE TR … ») — raccordement aux départs « condensateur » des TGBT
def link_caps(tgbt, mapping):
    for d in list(deps.values()):
        if d['board'] != tgbt or 'CONDENS' not in slug(d['label'] + ' ' + d.get('label_plan', '')): continue
        bus = busof = next((e['a'] for e in edges if e['b'] == d['id']), None)
        h = (busof or '')[-1]
        tgt = mapping.get(h)
        if tgt and not any(e['a'] == d['id'] and e['b'] == tgt for e in edges):
            E(d['id'], tgt, d['src'], conf='confirme'); d['feeds'] = nodes[tgt]['board']
link_caps('TGBT1', {'A': 'COND1_A', 'B': 'COND1_B'})
link_caps('TGBT2', {'A': 'COND2A_J', 'B': 'COND2B_J'})
link_caps('TGBT5', {'A': 'COND5A_J', 'B': 'COND5B_J'})
link_caps('TGBT6', {'A': 'COND6A_J', 'B': 'COND6B_J'})
boards['COND1']['halves'][0]['label'] = 'Batterie condensateur 1A'; boards['COND1']['halves'][1]['label'] = 'Batterie condensateur 1B'
def cab(bus, plate, n_grilles=3, w=800, reg='varlogic'):
    us = [dict(y=6, h=3, k='plate', node=bus, label=plate, plate='green', x=0.5), deco(17, 5, reg, 'Régulateur varmétrique VarLogic')]
    ys = [27, 43, 59][:n_grilles]
    us += [deco(y, 10, 'grille') for y in ys] + [deco(36, 6, 'handle')]
    return dict(n='', w=w, units=us, doors=[(3, 78)])
CAPS = [
 ('COND1', 'Batteries condensateurs TR 1A / TR 1B', [('COND1_A', 'PROVIENT DE TR 1A / BATTERIE CONDENSATEUR 1A'), ('COND1_B', 'PROVIENT DE TR 1B / BATTERIE CONDENSATEUR 1B')], 'Batterie condensateur tr1a et 1b .pdf p1-p3', 'Plaques lues à pleine résolution'),
 ('COND2A', 'Batterie condensateurs TR 2A', [('COND2A_J', 'PROVIENT DE TR 2A / BATTERIE CONDENSATEUR 2A')], 'Batterie condensateur tr2a .pdf p1-p2', 'Plaque verte, lecture partielle (photo peu nette)'),
 ('COND2B', 'Batterie condensateurs TR 2B', [('COND2B_J', 'PROVIENT DE TR 2B / BATTERIE CONDENSATEUR 2B')], 'Condensateur tr2b .pdf p1', 'Plaque verte, lecture partielle'),
 ('COND3', 'Batteries condensateurs TGBT 3', [('COND3_A', 'BATTERIE CONDENSATEUR TGBT 3 (A)'), ('COND3_B', 'BATTERIE CONDENSATEUR TGBT 3 (B)')], 'Condensateur tgbt 3.pdf p1-p2', 'Armoires VarSet sans plaque lisible'),
 ('COND4', 'Batteries condensateurs TR 4A / TR 4B', [('COND4_A', 'PROVIENT DE TR 4A / BATTERIE CONDENSATEUR 4A'), ('COND4_B', 'PROVIENT DE TR 4B / BATTERIE CONDENSATEUR 4B')], 'Condesanteur tr4b et 4 a .pdf p1-p2', 'Plaques vertes'),
 ('COND5A', 'Batterie condensateurs TR 5A', [('COND5A_J', 'PROVIENT DE TR 5A / BATTERIE CONDENSATEUR 5A')], 'Condensateur tr 5a.pdf p1-p2', 'Armoire ancienne à capot grillagé'),
 ('COND5B', 'Batterie condensateurs TR 5B', [('COND5B_J', 'PROVIENT DE TR 5B / BATTERIE CONDENSATEUR 5B')], 'Condensateur 5b.pdf p1-p2', 'Armoire ancienne à capot grillagé'),
 ('COND6A', 'Batterie condensateurs TR 6A', [('COND6A_J', 'PROVIENT DE TR 6A / BATTERIE CONDENSATEUR 6A')], 'Condensateur 6a.pdf p1-p2', 'Photos floues : plaque non vérifiable'),
 ('COND6B', 'Batterie condensateurs TR 6B', [('COND6B_J', 'PROVIENT DE TR 6B / BATTERIE CONDENSATEUR 6B')], 'Condensateur 6b .pdf p1', 'Plaque verte'),
 ('COND7', 'Batteries condensateurs TGBT 7A / 7B', [('COND7_A', 'BATTERIE CONDENSATEUR 7A'), ('COND7_B', 'BATTERIE CONDENSATEUR 7B')], 'Batterie condensateur tgbt7a et 7b.pdf p1-p2', 'Plaques non lisibles'),
 ('COND9', 'Batteries condensateurs TGBT 9A / 9B', [('COND9_A', 'BATTERIE CONDENSATEUR 9A'), ('COND9_B', 'BATTERIE CONDENSATEUR 9B')], 'Condensateur tgbt 9a et 9b .pdf p1-p4', 'Plaques blanches non lisibles'),
]
for bid, title, cabs, src, note in CAPS:
    old = bid in ('COND5A', 'COND5B')
    cols = [cab(bus, plate, n_grilles=1 if old else 3) for bus, plate in cabs]
    if old:
        for c in cols: c['units'] = [u for u in c['units'] if u['k'] != 'varlogic'] + [deco(2, 14, 'grille')]
    facade(bid, bid, 'enclosure_blanc', title.upper(), src, f'Relevé photo — armoires VarSet Schneider Electric ; {note}.', brand='Schneider Electric — VarSet', cols=cols)

# ---------- onduleurs et alimentations ondulées (Alim onduleur 1 .pdf p2, Alimentation onduleur 2.pdf p2)
AO = {}
for k, tg, c_r1, c_r2, bp in (('1', 'TGBT5', '2A-18', '2B-18', ('TGBT5', '2A-6')), ('2', 'TGBT6', '2A-18', '2B-18', None)):
    ob = f'OND{k}'; ab = f'ALIMOND{k}'
    N(f'OND{k}_UPS', 'sw', f'Onduleur {k} — Galaxy PW 2nd Gen (redresseur / onduleur)', board=ob, conf='confirme', src=f'Onduleur {k} .pdf (façade « Galaxy PW 2nd Gen — ONDULEUR {k} »)')
    E(dep_case(tg, c_r1), f'OND{k}_UPS', f'{tg} étiquette « ONDULEUR {k} - RÉSEAU 1 »'); E(f'OND{k}_UPS', f'OND{k}_J', 'Sortie onduleur')
    nodes[dep_case(tg, c_r1)]['feeds'] = ob
    N(f'OND{k}_R2', 'load', f'Onduleur {k} — entrée réseau 2 (by-pass statique)', board=ob, conf='probable', src=f'{tg} étiquette « ONDULEUR {k} - RÉSEAU 2 »',
      note='Entrée secours interne de l’onduleur : non modélisée comme source de la sortie (l’onduleur isole les deux réseaux).')
    E(dep_case(tg, c_r2), f'OND{k}_R2', f'{tg} étiquette « ONDULEUR {k} - RÉSEAU 2 »'); nodes[dep_case(tg, c_r2)]['feeds'] = ob
    sub(ab, f'Alimentation ondulée — Onduleur {k}', kind='TS', loc='SS2', loc_conf='confirme', style='prisma_beige',
        photos=[f'Alim onduleur 1 .pdf p1-p3' if k == '1' else 'Alimentation onduleur 2.pdf p1-p4'],
        note=f'Armoire Merlin Gerin Prisma beige « ALIMENTATION ONDULÉE ONDULEUR {k} ». Arrivée générale depuis l’onduleur {k}, by-pass total depuis le TGBT 5A (plaques).')
    AO[k] = ab
# by-pass totaux : plaques « PROVIENT DE TGBT 5A BY-PASS TOTAL ONDULEUR 1 / 2 »
bp1 = dep_case('TGBT5', '2A-6')
bp2 = next(d['id'] for d in deps.values() if d['board'] == 'TGBT5' and 'onduleur 2' in d['label'].lower() and 'pass' in d['label'].lower())
for k, src_dep in (('1', bp1), ('2', bp2)):
    ab = AO[k]
    N(f'{ab}_QA', 'cb', f'PROVIENT DE ONDULEUR {k} — ARRIVÉE GÉNÉRALE (QF1, Galaxy PW 100 kVA)', board=ab, half='J', role='arrivee', conf='confirme', src='plaque verte (photo)', model='Interrupteur-sectionneur à commande rotative')
    E(f'OND{k}_J', f'{ab}_QA', 'plaque verte'); E(f'{ab}_QA', f'{ab}_J', 'plaque verte')
    N(f'{ab}_QBP', 'cb', f'PROVIENT DE TGBT 5A — BY-PASS TOTAL ONDULEUR {k}', board=ab, half='J', role='arrivee', conf='confirme', src='plaque verte (photo)',
      model='Interrupteur-sectionneur à commande rotative (clé de condamnation)', open0=True, excl=f'{ab}_QA',
      note='Normalement ouvert. Interverrouillé par clé avec l’arrivée générale onduleur : jamais les deux fermés (règle appliquée par le simulateur).')
    E(src_dep, f'{ab}_QBP', 'plaque verte « PROVIENT DE TGBT 5A »'); E(f'{ab}_QBP', f'{ab}_J', 'plaque verte')
    nodes[src_dep]['feeds'] = ab
ISSUE('I-BP2', 'moyenne', 'By-pass total de l’onduleur 2 : TGBT 5A ou TGBT 6 ?', 'La plaque de l’armoire « Alimentation ondulée onduleur 2 » indique « PROVIENT DE TGBT 5A — BY-PASS TOTAL ONDULEUR 2 » (cohérent avec le classeur, TGBT 5A H7). Mais le TGBT 6 porte aussi une étiquette « ONDULEUR 2 - BY PASS — CASE 2A-12 ». Le modèle suit la plaque de l’armoire ondulée.', ['Alimentation onduleur 2.pdf p2', 'Tgbt 6.pdf p1', XL], ['ALIMOND2', 'TGBT6'])
nodes[dep_case('TGBT6', '2A-12')]['note'] = 'Étiquette « ONDULEUR 2 - BY PASS » : voir incohérence I-BP2 (l’armoire ondulée indique un by-pass depuis le TGBT 5A).'
OUT1 = [('BOBINEUSES CANAL 1 / QF1 DÉPART CANAL 1 FIBRAGE', 28), ('BOBINEUSES CANAL 2 / QF1 DÉPART CANAL 2 FIBRAGE', 36),
        ('220 V ONDULÉ / FILIÈRES CANAL 1 ET CANAL 2', 44), ('COFFRET ONDULÉ ÉTUVES 1, 2, 3, 4, 5, 6 / GÉNÉRATEUR 1, 3 ET BAIE INFORMATIQUE HALL ÉTUVE', 52)]
OUT2 = [('BOBINEUSES CANAL 3', 28), ('DÉPART (étiquette non lisible)', 36),
        ('220 V ONDULÉ / FILIÈRES CANAL 3 ET CANAL 4', 44), ('COFFRET ONDULÉ ÉTUVES 7, 8, 9, 10 / GÉNÉRATEUR 2 ET BAIE INFORMATIQUE TRAVAUX NEUFS', 52)]
for k, outs, src in (('1', OUT1, 'Alim onduleur 1 .pdf p2'), ('2', OUT2, 'Alimentation onduleur 2.pdf p2')):
    ab = AO[k]
    us = [dict(y=4, h=3, k='plate', node=f'{ab}_J', label=f'ALIMENTATION ONDULÉE / ONDULEUR {k}', plate='green', x=0.5), deco(9, 3, 'blank', 'Bornier / fusibles'),
          dict(y=12, h=7, k='rot', node=f'{ab}_QA', label=f'PROVIENT DE ONDULEUR {k} / ARRIVÉE GÉNÉRALE', plate='green'),
          dict(y=20, h=7, k='rot', node=f'{ab}_QBP', label=f'PROVIENT DE TGBT 5A / BY-PASS TOTAL ONDULEUR {k}', plate='green')]
    us += [dict(y=y, h=7, k='rot', label=lab, plate='green' if 'non lisible' not in lab else 'white', model='Interrupteur-sectionneur rotatif',
                conf='a_verifier' if 'non lisible' in lab else 'confirme') for lab, y in outs]
    facade(ab, ab, 'prisma_beige', f'ALIMENTATION ONDULÉE — ONDULEUR {k}', src, 'Relevé photo à pleine résolution : plaques vertes lues ; disposition verticale estimée.',
           brand='Merlin Gerin — Prisma', cols=[dict(n='', w=800, units=us), dict(n='', w=300, units=[deco(30, 4, 'meter', num='6' if k == '2' else None), deco(38, 4, 'meter'), deco(46, 6, 'handle')], doors=[(3, 78)])])
for k in ('1', '2'):
    facade(f'OND{k}', f'OND{k}', 'enclosure_blanc', f'ONDULEUR {k} — GALAXY PW 2nd GEN', f'Onduleur {k} .pdf', 'Relevé photo : armoire Schneider Electric Galaxy PW 2nd Gen (bandeau vert, écran, grilles basses).', brand='Schneider Electric — Galaxy PW',
           cols=[dict(n='', w=900, units=[dict(y=4, h=3, k='plate', node=f'OND{k}_UPS', label=f'ONDULEUR {k}', plate='blue', x=0.8), deco(10, 8, 'paper', 'Consignes d’exploitation'), deco(36, 6, 'handle'), deco(60, 14, 'grille')], doors=[(2, 78)]),
                 dict(n='', w=900, units=[deco(8, 6, 'hmi', 'Écran de supervision Galaxy', x=0.7), deco(36, 6, 'handle'), deco(60, 14, 'grille')], doors=[(2, 78)])])

# ---------- TS 46A / TS 46B (Okken Schneider neufs) — alimentés par le TGBT 1 (cases 1-53 et 6-53)
add_arrivals('TS46A', {'TS46A_J': ('TS46A_QA', 'ARRIVÉE TS46A (depuis TGBT 1, case 1-53)', 'Ts46a .pdf p1 + étiquette TGBT 1 « TS 46A — CASE 1-53 »')})
add_arrivals('TS46B', {'TS46B_J': ('TS46B_QA', 'ARRIVÉE TS46B (depuis TGBT 1, case 6-53)', 'Ts46b.pdf p1 + étiquette TGBT 1 « TS 46B — CASE 6-53 »')})
nodes['TS46A_QA']['conf'] = nodes['TS46B_QA']['conf'] = 'probable'
boards['TS46A']['note'] = 'Okken Schneider Electric, plaque « TS46A — TGBT TS46 ». Alimenté par le TGBT 1A (case 1-53, étiquette « TS 46A »). Entre Packman et l’emballage.'
boards['TS46B']['note'] = 'Okken Schneider Electric, plaque constructeur « TGBT TS46B » — 400 V — régime IT 3P+N — 50 kA / 1 s — fabrication 12/2025. Alimenté par le TGBT 1B (case 6-53, étiquette « TS 46B »).'
facade('TS46A', 'TS46A', 'okken_blanc_noir', 'TS46A — TGBT TS46', 'Ts46a .pdf p1, p2', 'Relevé photo : 3 colonnes, départs derrière vitre (étiquettes non visibles), voyants et arrêt d’urgence en colonne 2.', brand='Schneider Electric — Okken', cols=[
  dict(n='1', w=650, units=[deco(10, 62, 'window', 'Départs derrière vitre')]),
  dict(n='1', w=400, units=[dict(y=24, h=3, k='voy2', node='TS46A_QA'), deco(24, 4, 'estop', x=0.75)]),
  dict(n='2', w=650, units=[deco(26, 46, 'window', ''), deco(22, 2, 'voy2', x=0.8)]),
])
facade('TS46B', 'TS46B', 'okken_blanc_vert', 'TGBT TS46B', 'Ts46b.pdf p1, p2, p6', 'Relevé photo : plaque constructeur lue (Okken, 400 V, IT 3P+N, 50 kA), départs derrière vitre, voyants ouvert / fermé / défaut et arrêt d’urgence.', brand='Schneider Electric — Okken', cols=[
  dict(n='1', w=650, units=[deco(9, 5, 'paper', 'Plaque constructeur : TGBT TS46B — Okken — 400 V — IT 3P+N — 50 kA/1 s — 12/2025'), deco(16, 60, 'window', 'Départs derrière vitre')]),
  dict(n='2', w=650, units=[dict(y=15, h=3, k='voy', node='TS46B_QA', label='Ouvert / Fermé / Défaut'), deco(15, 4, 'estop', x=0.3)]),
])

# ---------- Bâtiment Bronzini (PrismaSeT) — Bronzini .pdf p1, p3
add_arrivals('BRONZINI', {'BRONZINI_J': ('BRONZINI_QA', 'INTERRUPTEUR GÉNÉRAL (Bronzini)', 'Bronzini .pdf p1 (plaque, lecture partielle)')})
facade('BRONZINI', 'BRONZINI', 'okken_blanc_vert', 'TABLEAU BÂTIMENT BRONZINI', 'Bronzini .pdf p1-p3', 'Relevé photo à pleine résolution : PrismaSeT Schneider (bandeau vert), ComPacT NS / NSX et rangées modulaires ; une partie des petites étiquettes est illisible.', brand='Schneider Electric — PrismaSeT', cols=[
  dict(n='1', w=650, units=[
    dict(y=16, h=13, k='nsx', node='BRONZINI_QA', label='INTERRUPTEUR GÉNÉRAL', plate='white', model='ComPacT NS (interrupteur)'),
    dict(y=31, h=6, k='nsx', label='DÉPART NSX (étiquette non lisible)', plate='white', model='ComPacT NSX', conf='a_verifier'),
    dict(y=38, h=6, k='nsx', label='DÉPART NSX — cadenassé (étiquette non lisible)', plate='white', model='ComPacT NSX', conf='a_verifier'),
    dict(y=46, h=13, k='nsx', label='DISJONCTEUR NS à Micrologic (étiquette non lisible)', plate='white', model='ComPacT NS', conf='a_verifier'),
  ], doors=[(5, 14), (14, 30), (30, 37), (37, 45), (45, 77)]),
  dict(n='', w=250, units=[deco(12, 3, 'voy', 'Présence tension'), deco(28, 4, 'estop'), deco(33, 4, 'handle')], doors=[(5, 77)]),
  dict(n='2', w=750, units=[
    dict(y=9, h=4, k='modrow', label='ÉCLAIRAGE ZONE 1 · ÉCLAIRAGE ZONE 2 · DÉPART · DÉPART · ÉCLAIRAGE EXTÉRIEUR'),
    dict(y=20, h=4, k='modrow', label='ARRÊT D’URGENCE · COMMANDE · HORLOGE'),
    dict(y=31, h=4, k='modrow', label='COFFRET PJ1 · COFFRET PJ2 · PORTE 1 · PORTE 2'),
    dict(y=42, h=4, k='modrow', label='PALAN 1 · CHARGEUR BATTERIE TRANSPALETTE · COFFRET · POMPE'),
    dict(y=53, h=4, k='modrow', label='ALIM LABO « BRONZINI » · PC · PC · PC'),
  ], doors=[(5, 77)]),
])

# ---------- Gradathyr (tableau Gorge OM 221) — GRADATHYR.pdf p1-p5
for z in ('1', '2', '3'):
    pass
facade('GRADATHYR', 'GRADATHYR', 'armoire_grise', 'O M 221 — TABLEAU GORGE — GRADATHYR', 'GRADATHYR.pdf p1-p5',
  'Relevé photo à pleine résolution : armoires « GRADATHYR ZONE N°1 - GORGE » et « ZONE N°2 - GORGE » lues ; troisième armoire (p5, sombre) non lue.', brand='Gradateurs à thyristors', cols=[
  dict(n='', w=850, units=[deco(3, 3, 'plate', 'O M 221 / TABLEAU GORGE', plate='black', x=0.3),
    dict(y=8, h=3, k='plate', label='GRADATHYR / ZONE N°1 - GORGE', plate='black', x=0.5, model='Gradateur à thyristors, écran Power Electronics', conf='confirme'),
    deco(36, 6, 'hmi', 'Écran Power Electronics', x=0.5), deco(46, 3, 'voy', 'Zone en marche · Défaut général · Défaut thyristor', x=0.25),
    deco(52, 3, 'voy2', 'Réarmement défaut · Test lampes', x=0.5), deco(48, 8, 'handle', x=0.9), deco(68, 8, 'grille')], doors=[(3, 78)]),
  dict(n='', w=850, units=[dict(y=8, h=3, k='plate', label='GRADATHYR / ZONE N°2 - GORGE', plate='black', x=0.5, conf='confirme'),
    deco(36, 6, 'hmi', 'Écran Power Electronics', x=0.5), deco(46, 3, 'voy', 'Zone en marche · Défaut général · Défaut thyristor', x=0.25),
    deco(52, 3, 'voy2', '', x=0.5), deco(48, 8, 'handle', x=0.9), deco(68, 8, 'grille')], doors=[(3, 78)]),
  dict(n='', w=850, units=[dict(y=8, h=3, k='plate', label='GRADATHYR / ZONE N°3 (plaque non lue)', plate='black', x=0.5, conf='a_verifier'),
    deco(36, 6, 'hmi', 'Écran', x=0.5), deco(46, 3, 'voy', '', x=0.25), deco(48, 8, 'handle', x=0.9), deco(68, 8, 'grille')], doors=[(3, 78)]),
])
boards['GRADATHYR']['name'] = 'Gradathyr — Tableau Gorge (OM 221)'
boards['GRADATHYR']['note'] = 'Armoires de gradateurs à thyristors « GRADATHYR ZONE N°1 / N°2 - GORGE », plaque supérieure « O M 221 — TABLEAU GORGE ». Alimentation amont non documentée.'

# ---------- armoires simples
facade('ARM110', 'ARM110', 'armoire_grise', 'ARMOIRE 110 V DISTRIBUTION', 'Armoire 110v instrument ampère mètre .pdf p1', 'Relevé photo : plaque jaune et 4 appareils de mesure analogiques.', brand='', cols=[
  dict(n='', w=900, units=[dict(y=8, h=4, k='plate', node='ARM110_J', label='ARMOIRE / 110V DISTRIBUTION', plate='yellow', x=0.5),
    deco(22, 7, 'gauge', 'TENSION 1', x=0.22), deco(22, 7, 'gauge', 'TENSION 2', x=0.78), deco(44, 7, 'gauge', 'INTENSITÉ 1', x=0.22), deco(44, 7, 'gauge', 'INTENSITÉ 2', x=0.78)], doors=[(3, 78)])])
facade('ECLSST1', 'ECLSST1', 'armoire_grise', 'ARMOIRE ÉCLAIRAGE SOUS-STATION', 'Armoire éclairage .pdf p1', 'Relevé photo : armoire 2 portes fermées, étiquettes de risque d’arc ; appareillage non visible.', brand='', cols=[
  dict(n='', w=700, units=[dict(y=6, h=3, k='plate', node='ECLSST1_J', label='ARMOIRE ÉCLAIRAGE SOUS-STATION', plate='green', x=0.5), deco(12, 7, 'arc', 'ATTENTION Risque Classe 1 — étiquette d’arc', x=0.5), deco(40, 6, 'handle', x=0.9)], doors=[(3, 78)]),
  dict(n='', w=700, units=[deco(40, 6, 'handle', x=0.1)], doors=[(3, 78)])])
facade('OM27', 'OM27', 'armoire_grise', 'TABLEAU OM 27', 'Tableau OM 27 .pdf p1', 'Relevé photo : armoire 2 portes fermées sans appareil en façade (photo peu nette) ; appareillage intérieur à photographier porte ouverte (hors tension / par personnel habilité).', brand='', cols=[
  dict(n='', w=600, units=[dict(y=6, h=3, k='plate', node='OM27_J', label='TABLEAU OM 27', plate='black', x=0.5), deco(40, 6, 'handle', x=0.9)], doors=[(3, 78)]),
  dict(n='', w=600, units=[deco(40, 6, 'handle', x=0.1)], doors=[(3, 78)])])
facade('DECARBO', 'DECARBO', 'armoire_grise', 'DÉCARBONATATION — ARMOIRE DE COMMANDE', 'Decarbo .pdf p1, p2', 'Relevé photo : armoire de commande avec écran tactile, sélecteurs et voyants ; p1 = gros plan d’une armoire plus ancienne (centrale de mesure, 2 sectionneurs rouge / jaune).', brand='', cols=[
  dict(n='', w=800, units=[dict(y=5, h=3, k='plate', node='DECARBO_J', label='DÉCARBONATATION (7M10)', plate='white', x=0.5),
    deco(12, 7, 'hmi', 'Écran tactile', x=0.5), deco(23, 3, 'voy', 'Voyants', x=0.5), deco(28, 3, 'voy', '', x=0.5), deco(34, 3, 'voy2', '', x=0.5), deco(42, 6, 'handle', x=0.1)], doors=[(3, 78)]),
  dict(n='', w=700, units=[deco(8, 6, 'meter', x=0.5), deco(22, 6, 'rotsec', 'Sectionneur 1', x=0.3), deco(22, 6, 'rotsec', 'Sectionneur 2', x=0.7), deco(34, 3, 'voy2', '', x=0.3), deco(34, 3, 'voy2', '', x=0.7)], doors=[(3, 78)])])
facade('AUX7B', 'AUX7B', 'enclosure_blanc', 'COFFRET 24 V / 230 V TR7B', '24 V et 230 V tr7b.pdf p1', 'Relevé photo : coffret mural blanc, arrêt d’urgence en façade.', brand='', cols=[
  dict(n='', w=700, units=[dict(y=10, h=3, k='plate', node='AUX7B_J', label='24 V ET 230 V TR7B', plate='white', x=0.5), deco(18, 4, 'estop', x=0.6), deco(30, 6, 'handle', x=0.1)], doors=[(6, 48)])])
for b in ('ARM110', 'ECLSST1', 'OM27', 'DECARBO', 'AUX7B', 'GRADATHYR'): boards[b]['style'] = 'armoire_grise' if b != 'AUX7B' else 'enclosure_blanc'

# ---------- ventilation du four (Ventilation FOUR.pdf, relu le 12/10/2026 : les pages ne sont pas inexploitables)
VP = 'Ventilation FOUR.pdf'
# p3, coffret de gauche, plaque nette
boards['VENTIL'].update(
    name='Coffret ventilation local Boosting F2',
    photos=[VP + ' p3'],
    style='enclosure_blanc',
    note='Plaque : « Coffret ventilation local Boosting F2 — Pris dans TGBT 9A case A2 52E ». Marque Ventifield Industries, étiquette 3×400 V. Quatre tourelles (voyant marche, voyant défaut, commutateur auto/manu) et arrêt d’urgence. Le départ n’a pas été relu sur la façade du TGBT 9 (étiquettes de la colonne A2 illisibles).')
_vf2 = dep('TGBT9', 'A', 'COFFRET VENTILATION LOCAL BOOSTING F2 — CASE A2 52E', VP + ' p3 (plaque du coffret)',
           case='A2-52E', conf='probable',
           note='Lu sur le coffret, pas sur le TGBT 9. La colonne A2 du TGBT 9 a des départs dont l’étiquette de façade n’a pas été lue.')
feed(_vf2, 'VENTIL_J', conf='probable', src=VP + ' p3 (plaque du coffret)')
facade('VENTIL', 'VENTIL', 'enclosure_blanc', 'COFFRET VENTILATION LOCAL BOOSTING F2', VP + ' p3',
       'Plaque blanche lue en gros plan. Tourelles 1 à 4 de gauche à droite.', brand='Ventifield Industries', cols=[
    dict(n='', w=800, units=[
        dict(y=4, h=5, k='plate', node='VENTIL_J', label='BOOSTING F2 / PRIS DANS TGBT 9A / CASE A2 52E / 3×400 V', plate='white'),
        dict(y=14, h=8, k='plate', label='TOURELLE 1', plate='white'),
        dict(y=24, h=8, k='plate', label='TOURELLE 2', plate='white'),
        dict(y=34, h=8, k='plate', label='TOURELLE 3', plate='white'),
        dict(y=44, h=8, k='plate', label='TOURELLE 4', plate='white'),
        deco(58, 5, 'estop', 'ARRÊT D’URGENCE', x=0.5),
    ], doors=[(3, 72)])])

# p3, coffret de droite : même famille, plaque trop petite pour un numéro de case
sub('VENTF1', 'Coffret ventilation local Boosting 1', kind='Coffret', loc='SS1G', loc_conf='probable',
    photos=[VP + ' p3'],
    note='Second coffret mural, à droite du Boosting F2 sur la même photo. Quatre tourelles (marche / défaut / auto-manu) et arrêt d’urgence. Deux petites plaques en haut : l’une se lit comme le pendant « Boosting » du coffret F2, l’autre comme une alimentation depuis le TGBT 9A ; le numéro de départ n’est pas assez net pour être saisi. Le plan d’implantation appelle cet emplacement « coffret ventilation local boosting 1 ».')
boards['VENTF1']['loc_src'] = 'PLAN IMPLANTATION 2.pptx'
facade('VENTF1', 'VENTF1', 'enclosure_blanc', 'COFFRET VENTILATION — TOURELLES (BOOSTING 1)', VP + ' p3',
       'Même photo que le coffret F2, armoire de droite. Tourelles 1 à 4 lisibles ; plaques du haut trop petites pour un repère de case.', brand='', cols=[
    dict(n='', w=800, units=[
        dict(y=4, h=5, k='plate', node='VENTF1_J', label='TOURELLES / COFFRET DE DROITE / ALIMENTATION TGBT 9A (CASE NON LUE)', plate='white'),
        dict(y=14, h=8, k='plate', label='TOURELLE 1', plate='white'),
        dict(y=24, h=8, k='plate', label='TOURELLE 2', plate='white'),
        dict(y=34, h=8, k='plate', label='TOURELLE 3', plate='white'),
        dict(y=44, h=8, k='plate', label='TOURELLE 4', plate='white'),
        deco(58, 5, 'estop', 'ARRÊT D’URGENCE', x=0.5),
    ], doors=[(3, 72)])])

# p1, p4, p5 : armoire au sol, porte nette (p2 et p6 sont les mêmes portes, plus sombres)
sub('HELIPAC', 'Armoire ventilateurs hélicoïdes Helipac', kind='Armoire', loc='SS1G', loc_conf='confirme',
    photos=[VP + ' p1', VP + ' p4', VP + ' p5'],
    note='Plaque « ARMOIRE VENTILATEUR HELICOIDES HELIPAC ». Dix ventilateurs en deux rangées (1 à 5 en haut, 6 à 10 en bas) : voyant de présence, marche, arrêt. Arrêt d’urgence, sélecteur manu/auto, lampe « présence tension ». Aucune plaque d’alimentation sur la porte.')
boards['HELIPAC']['loc_src'] = 'PLAN IMPLANTATION 2.pptx'
facade('HELIPAC', 'HELIPAC', 'armoire_grise', 'ARMOIRE VENTILATEUR HELICOIDES HELIPAC', VP + ' p1, p4, p5',
       'Porte lue sur les pages 1 et 4 (nettes). Pages 2 et 6 : même armoire, local plus sombre.', brand='', cols=[
    dict(n='1 à 5', w=500, units=[dict(y=4, h=6, k='plate', node='HELIPAC_J', label='ARMOIRE VENTILATEUR / HELICOIDES HELIPAC', plate='white')] + [
        dict(y=12 + i * 8, h=7, k='plate', label=f'VENTILATEUR {i+1}', plate='white') for i in range(5)] + [
        deco(56, 5, 'estop', 'ARRÊT D’URGENCE', x=0.5), deco(64, 4, 'voy', 'PRÉSENCE TENSION', x=0.5)], doors=[(3, 76)]),
    dict(n='6 à 10', w=500, units=[
        dict(y=12 + i * 8, h=7, k='plate', label=f'VENTILATEUR {i+6}', plate='white') for i in range(5)], doors=[(3, 76)]),
])
# tableau 20 kV CNR / EDF : ordre des premières cellules confirmé par photo
F['SS1_20']['conf'] = 'Ordre des cellules selon l’unifilaire, confirmé sur photo pour les premières cellules (PFM parafoudres, DM1 TR 6A repère 010, DM1 TR 5A repère 01, TR 4A, TR 3A — plaques rouges « DÉPART 20 kV TRANSFORMATEUR … ») ; cellules SM6 Schneider.'
F['SS1_20']['src'] = UNI + ' + Tableau 20kv edf cnr .pdf p1, p3'
