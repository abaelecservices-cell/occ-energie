"""Corrections et ajouts issus de l'audit du 11/10/2026 (« Liste des ajouts et corrections proposés pour OCC-ENERGIE »).

Chaque relevé ci-dessous a été RELU sur la photo ou le plan cité avant saisie (les lectures de l'audit non revérifiées ne sont pas saisies,
elles restent dans docs/4_PHOTOS_A_REPRENDRE.md). Règles appliquées :
- « lu sur une photo » ≠ « vérifié sur le terrain » : les relevés photo sont rangés dans `obs` (statut « photo ») ;
- aucune liaison électrique n'est créée à partir d'une étiquette seule ; les contradictions deviennent des écarts (issues) ;
- deux objets ne sont fusionnés que s'ils portent le même nom sur le même demi-jeu de barres du même tableau (conf « probable »).
Exécuté par build_data.py après hta_photo.py.
"""
AUD = 'audit 11/10/2026, relu sur la source'
T9 = 'Tgbt 9.pdf'
T7 = 'Tr7b .pdf'
T3A = 'p1 - Copie.zip › 12_TGBT N°3 › CX7810_C TQC.PDF'
T1B = 'p1.zip › 10_TGBT N°1 › TH11A-TGBT1B.pdf'

def OBS(target, t, src, kind='photo'):
    """Relevé documentaire rattaché à un équipement ou à un tableau (affiché comme tel, jamais comme un état réel)."""
    o = nodes.get(target) or boards.get(target)
    o.setdefault('obs', []).append(dict(t=t, src=src, kind=kind, d='2026-10-11'))

def merge_dep(old, new, label, case, src, note):
    """`old` = départ créé depuis une étiquette illisible ; `new` = ligne du classeur portant le même nom sur le même demi-jeu de barres."""
    for f in F.values():
        for c in f.get('cols', []) or []:
            for u in c.get('units', []) or []:
                if u.get('dep') == old: u['dep'] = new; u['label'] = label; u['plate'] = u.get('plate') or 'white'
    n = nodes[new]
    n['case'] = case
    n['label'] = f"{n['label']} — plaque « {label.replace(' / ', ' — ')} »"
    n['note'] = ((n.get('note') or '') + ' ' + note).strip()
    n['src'] = n['src'] + ' + ' + src
    del nodes[old]; deps.pop(old, None)
    edges[:] = [e for e in edges if e['a'] != old and e['b'] != old]
    for i in issues: i['ents'] = [new if x == old else x for x in i['ents']]

# ------------------------------------------------------------------ TGBT 1 : plaque SAP, case HVAC F2, ventilation TR 1B
boards['TGBT1']['sap'] = '98922+101152 (plaque, Tgbt 1.pdf p13)'
d = nodes['D0416']
d.update(case='3-63', label='HVAC F2 — LOCAL HVAC SUD — CASE 3-63', conf='probable',
         note='Plaque relue au zoom (Tgbt 1.pdf p13) : « HVAC F2 / LOCAL HVAC SUD / CASE 3-63 », cohérent avec le plan 2010 (« HVAC canal 3 », case 3-63). '
              'Ancienne valeur saisie : 3-40 (relevé précédent). Petite écriture : à confirmer sur place.')
for c in F['TGBT1']['cols']:
    for u in c['units']:
        if 'HVAC F2' in (u.get('label') or ''): u['label'] = 'HVAC F2 / LOCAL HVAC SUD / CASE 3-63'
N('TGBT1_VTR1B', 'dep', 'Ventilation transfo TR 1B', board='TGBT1', half='B', case='7-33', rep='Q7-33D', model='NG125L 2P 10 A (Multiclip 1)', aux='TR1B',
  conf='probable', src=f'{T1B} p59 — folio 312 (TH111001 rév. B du 13/05/2014)', note='Plan de 2014 : présence actuelle à vérifier sur place.')
E('TGBT1B', 'TGBT1_VTR1B', f'{T1B} p59', conf='probable')

# ------------------------------------------------------------------ TGBT 2 : plaque SAP, ventilation TR 2A / TR 2B
boards['TGBT2']['sap'] = '43930+42931 (plaque, Tgbt 2.pdf p4)'
for side, col, rep, cal, folio, pg in (('A', '2-51', 'Q2-51D', '10 A', '312', 77), ('B', '6-51', 'Q6-51D', '16 A', '322', 82)):
    N(f'TGBT2_VTR2{side}', 'dep', f'Ventilation transfo TR 2{side}', board='TGBT2', half=side, case=col, rep=rep, model=f'NG125L 2P {cal}', aux=f'TR2{side}',
      conf='confirme', src=f'{T2DOC} p{pg} — folio {folio}')
    E(f'TGBT2{side}', f'TGBT2_VTR2{side}', f'{T2DOC} p{pg}')
boards['TGBT2']['coupler']['lock'] = 'Plan TH112001 (p3, spécifications) : « … permutation est à la charge de l’exploitant ». Aucun verrouillage décrit.'

# ------------------------------------------------------------------ TGBT 3 : localisateurs de défaut, verrouillage / règle / alarme séparés
b3 = boards['TGBT3']['coupler']
b3['lock'] = ('Clés Ronis dessinées sur l’unifilaire du dossier (CX7810_C p6) : QTR1 / QC / QTR2 = 1-0-1, 0-1-1, 1-1-0. '
              'MAIS la page des spécifications (p5, folio 11) indique : « AUCUN VERROUILLAGE ENTRE LES ARRIVÉES ET LE COUPLAGE, LA PERMUTATION EST À LA CHARGE DE L’EXPLOITANT ». '
              'Présence réelle des serrures à vérifier sur place.')
b3['alarm'] = 'Alarme « ARRIVÉE EN … » (arrivées en parallèle) câblée sur les contacts de position QTR3A / QC / QTR3B (folios 40-42, p19-21).'
ISSUE('I-TGBT3-LOCK', 'haute', 'TGBT 3 : clés Ronis dessinées mais « aucun verrouillage » écrit',
      'Le même dossier Schneider (CX7810_C, 12/2024) dessine des clés Ronis de choix de source (p6) et précise en p5 qu’il n’y a aucun verrouillage entre les arrivées et le couplage, '
      'la permutation étant à la charge de l’exploitant. Une alarme « arrivées en parallèle » est câblée (p19-21). L’application applique la règle d’exploitation (jamais 3 appareils fermés) '
      'sans affirmer qu’un verrouillage physique existe. À trancher sur place (serrures présentes ? clés ?).', [T3A], ['TGBT3', 'TGBT3_QA', 'TGBT3_QB', 'TGBT3_QC'])
for p in PROCS:
    if p['id'] == 'P-TGBT3-SRC':
        p['status'] = 'Règle constructeur (CX7810_C p6, clés Ronis) — contredite p5 (« aucun verrouillage ») — aucune séquence fournie'

# règle d'exploitation (donnée par l'exploitant) : distincte du verrouillage physique et de l'alarme
OPRULE = 'Règle d’exploitation (exploitant, 11/10/2026) : chaque moitié sur son transformateur ; le couplage ne se ferme qu’après ouverture de l’arrivée qui alimentait la moitié à réalimenter ; jamais arrivée A, couplage et arrivée B fermés ensemble.'
for b in boards.values():
    if b.get('kind') == 'TGBT': b['coupler']['op'] = OPRULE

# ------------------------------------------------------------------ transformateurs : surveillance thermique et ventilation
_NT = 'Sec Trihal — sondes PT100 + relais NT935 AD : ventilateur 1 à 130 °C, alarme à 140 °C, déclenchement à 150 °C (schéma de câblage 106-267462 E, réglage dessiné — à confirmer sur le relais)'
nodes['TR3A']['cooling'] = _NT + ' ; CX7810_C p27'
nodes['TR3B']['cooling'] = _NT + ' ; CX7810_C p43'
ISSUE('I-TR3-COOL', 'basse', 'TR 3B : DGPT2 (unifilaire) ou sec Trihal (dossier 2025) ?',
      'L’unifilaire R112529 rév. H indique une protection DGPT2 (transformateur immergé) pour le TR 3B. Le dossier du TGBT 3 (12/2024) et le dossier constructeur 2025 décrivent des transformateurs secs Trihal '
      'avec sondes PT100 et relais NT935 (ventilateur 1 à 130 °C, alarme à 140 °C, déclenchement à 150 °C sur le schéma de câblage). Le transformateur a probablement été remplacé : la fiche suit le dossier récent. Ces seuils sont ceux du dessin, pas une relève sur le relais.',
      [UNI, T3A], ['TR3A', 'TR3B'])
ISSUE('I-VARIVOLT-TC', 'basse', 'Varivolt : TC câblé en 200/5 (schéma 2023) ou en 100/5 (unifilaire) ?',
      'Les schémas Schneider des cellules DM1-A départ Varivolt (S000119797, dessins 697408-000 zone 1 et 697409-000 zone 2, 27/03/2023) portent « câblé sur grand rapport » sur les TC 3 × ARM3/N2F 200-100/5 A : le grand rapport est 200/5. '
      'L’unifilaire R112529 retient 100/5 (valeur soulignée). Le relais et ses réglages I> ne figurent pas sur ces schémas. À relever sur le relais.',
      ['p1 - Copie (2).zip › schema DM1 départ varivolt zone 1.pdf', 'p1 - Copie (2).zip › schema DM1 départ varivolt zone 2.pdf', UNI],
      ['SS2_CZ1', 'SS2_CZ2', 'AEF1-TRZ1', 'AEF1-TRZ2'])
nodes['TR7A']['cooling'] = 'Sondes + relais T935 : « ventilation et déclenchement température par relais T 935 » (étiquette, Tr7b .pdf p5)'

# ------------------------------------------------------------------ TGBT 9 : plaques relues, contrôleur d'isolement, Gorge Four 2
merge_dep('D0430', 'D0107', 'TS17A / EAU DE REFROIDISSEMENT / CASE A2-18', 'A2-18', f'{T9} p19 (plaque)',
          'Plaque « TS17A — EAU DE REFROIDISSEMENT — CASE A2-18 » (Tgbt 9.pdf p19) : même nom que la ligne du classeur sur le même demi-jeu de barres → rapprochement probable. '
          'Localisateur d’isolement JdB A, voie 3 = A2-18.')
nodes['D0107']['conf'] = 'probable'
merge_dep('D0431', 'D0109', 'BATTERIE DE CONDENSATEURS / JDB A / CASE A2-36', 'A2-36', f'{T9} p19 (plaque)',
          'Plaque « BATTERIE DE CONDENSATEURS — JDB A — CASE A2-36 » (Tgbt 9.pdf p19) : rapprochement probable avec la ligne « Condensateurs » du classeur (JdB A). Localisateur JdB A, voie 4 = A2-36.')
nodes['D0109']['conf'] = 'probable'
d = nodes['D0435']
d.update(label='RÉSERVE 800 A — CASE B3-18 (étiquette « Groupe froid 7H216 »)', case='B3-18', conf='a_verifier',
         note='Plaque gravée « RÉSERVE 800A — CASE B3-18 » et étiquette imprimée ajoutée « Groupe froid 7H216 » (Tgbt 9.pdf p3). Les deux coexistent : alimentation du groupe froid NON confirmée.')
for c in F['TGBT9']['cols']:
    for u in c['units']:
        if u.get('dep') == 'D0435': u['label'] = 'RÉSERVE 800A / CASE B3-18 + « Groupe froid 7H216 »'
d = nodes['D0106']
d.update(case='A3-72', note=((d.get('note') or '') + ' Plaques (Tgbt 9.pdf p17) : « NORMAL ALIM. ARMOIRE GORGE FOUR 2 — CASE A3-72N », « SECOURS ALIM. ARMOIRE GORGE FOUR 2 — CASE A3-72S » '
                 'et commutateur à clé « N/S ALIM ARMOIRE GORGE FOUR 2 — CASE A3-72 ». Source du secours et logique de permutation non documentées.').strip())
OBS('D0106', 'Deux appareils repérés A3-72N (normal) et A3-72S (secours) + commutateur à clé N/S (case A3-72). Ne pas en déduire une possibilité de secours.', f'{T9} p17')
boards['TGBT9']['it'] = 'Vigilohm XML3xx ×2 (16 voies affichées — XML316 probable ; référence exacte à relever) + relais de température NT935 ×2'
OBS('TGBT9', 'Contrôleurs d’isolement Vigilohm XML3xx (ancienne génération, 16 voies) avec tables « LOCALISATION DÉFAUT » — différents des IM400 du TGBT 1.', f'{T9} p22')
ISSUE('I-TGBT9-IMD', 'basse', 'TGBT 9 : contrôleur d’isolement à identifier',
      'Les contrôleurs photographiés (Tgbt 9.pdf p22) sont des Vigilohm XML3xx (16 voies), pas des IM400. Référence exacte et notice à associer avant d’utiliser les seuils. '
      'Les seuils du TGBT 1 (rapport Schneider 2024) ne s’appliquent pas au TGBT 9.', [f'{T9} p22'], ['TGBT9'])
ti = [i for i in issues if i['id'] == 'I-TS17']
if ti: ti[0]['text'] += ' Nouvel élément : plaque « TS17A — EAU DE REFROIDISSEMENT — CASE A2-18 » sur le TGBT 9 (Tgbt 9.pdf p19), cohérente avec le classeur (TS 17A sur TGBT 9A).'

# ------------------------------------------------------------------ TGBT 7 : cases relues au zoom
nodes['D0092'].update(case='A3-18', note='Plaque « STEP » complétée à la main « TS16 » — CASE A3-18 (Tr7b .pdf p3).')
nodes['D0094'].update(case='A2-1?', note=(nodes['D0094'].get('note') or '') + ' Plaque « COMPRESSEUR 7K122 CHAUFFERIE — CASE A2-1? » : dernier chiffre retouché à la main (16 ou 18), Tr7b .pdf p5.')
nodes['D0097'].update(case='B2-23', note='Plaque « AUXILIAIRE GE — CASE B2-23 » (Tr7b .pdf p12, p15 ; dernier chiffre peu net).')
nodes['D0098'].update(case='B2-33', label='Forming Nord / Laveur n°6', note='Étiquette « FORMING NORD — LAVEUR N°6 », case « B2-33 » écrite à la main (Tr7b .pdf p12, p15).')
OBS('D0091', 'Plaque « COMPRESSEUR AIR » avec « B2 18 » manuscrit près du disjoncteur repéré « AE 7K121 » : rapprochement avec ce départ à vérifier (plaques du disjoncteur et du compteur différentes).', f'{T7} p12')
OBS('TGBT7', 'Repère « 7K123 » avec voyants et centrale n°55 (Tr7b .pdf p12, p15) : aucun départ correspondant dans le modèle — identification à faire, aucune liaison supposée.', f'{T7} p12, p15')

# ------------------------------------------------------------------ TS 17 : coffrets variateurs
OBS('TS17', 'Coffret variateur « ALIM DEPUIS TS17B — Q34 — POMPE EAU FROIDE N°3 - 7PM41 » (Ts17b.pdf p11).', 'Ts17b.pdf p11')
OBS('TS17', 'Coffret variateur « ALIM DEPUIS TS17B — Q36 — POMPE EP 7PM 06 » (Ts17b.pdf p13).', 'Ts17b.pdf p13')
for i in ('D0372', 'D0374'):
    nodes[i]['note'] = ((nodes[i].get('note') or '') + ' Coffret de la pompe : « ALIM DEPUIS TS17B — Q34 » (Ts17b.pdf p11). Deux lignes du classeur portent 7PM41 : identité à vérifier avant fusion.').strip()
for i in ('D0368', 'D0375'):
    nodes[i]['note'] = ((nodes[i].get('note') or '') + ' Coffret « ALIM DEPUIS TS17B — Q36 — POMPE EP 7PM 06 » (Ts17b.pdf p13). Deux lignes 7PM06 dans le classeur : identité à vérifier.').strip()

# ------------------------------------------------------------------ Gradathyr zone 3
d = nodes['D0461']
d.update(label='GRADATHYR — ZONE N°3 - GORGE', conf='confirme', note='Plaque « GRADATHYR / ZONE N°3 - GORGE » lue au zoom (GRADATHYR.pdf p4). Alimentation amont non documentée ; ne pas l’associer aux armoires Gorge sur la seule proximité des noms.')
for c in F['GRADATHYR']['cols']:
    for u in c['units']:
        if u.get('dep') == 'D0461': u['label'] = 'GRADATHYR / ZONE N°3 - GORGE'

# ------------------------------------------------------------------ Onduleur 2 : repères QF et puissance de plaque
nodes['ALIMOND2_QA']['label'] = 'PROVIENT DE ONDULEUR 2 — ARRIVÉE GÉNÉRALE (QF1, plaque « Galaxy PW 1?0 kVA »)'
nodes['ALIMOND2_QA']['note'] = 'Plaque QF1 « ARRIVÉE GÉNÉRALE GALAXY PW 120 KVA » probable (Alimentation onduleur 2.pdf p2) — premier chiffre peu net ; la valeur 100 kVA reprise jusqu’ici n’est pas confirmée.'
nodes['ALIMOND2_QBP']['label'] = 'PROVIENT DE TGBT 5A — BY-PASS TOTAL ONDULEUR 2 (QF2)'
ISSUE('I-OND2-KVA', 'basse', 'Onduleur 2 : 100 ou 120 kVA ?', 'La plaque QF1 de l’armoire ondulée se lit « GALAXY PW 120 KVA » (premier chiffre peu net, photo p2). L’application indiquait 100 kVA. Relever la plaque de l’onduleur.',
      ['Alimentation onduleur 2.pdf p2'], ['ALIMOND2', 'OND2'])

# ------------------------------------------------------------------ Varivolt : plaque constructeur (document indépendant)
boards['VARIVOLT'].setdefault('docs', []).append('p1 - Copie (2).zip › 20_VARIVOLT › 26013 nameplate.pdf (Bernard & Bonnefond, plan N°144532 du 20/02/2007)')
OBS('VARIVOLT', 'Plaque constructeur « VARIVOLT TRANSFORMER » Bernard & Bonnefond : monophasé, 901 kVA, 50 Hz, Ucc 6,2 %, OFAF, primaire 20 000 V ±10 % / 45 A, '
    'secondaire 50 à 273 V (3 300 A) et 273 à 350 V, série N°26013-1 (« N°26384 → 901 kVA »), MAN2007.', '26013 nameplate.pdf', kind='document')
ISSUE('I-VARIVOLT-PLATE', 'basse', 'Varivolt : 901 kVA monophasé (plaque) / 900 kVA (unifilaire)',
      'La plaque constructeur (série 26013-1) indique 901 kVA monophasé, secondaire variable 50-350 V. L’unifilaire porte 900 kVA / 350 V pour AEF1-TRZ1 et TRZ2. '
      'L’unité à laquelle appartient la plaque n’est pas établie (les repères 26013-3 / 26013-4 des armoires de commande ne suffisent pas) : valeurs de l’unifilaire conservées.',
      ['26013 nameplate.pdf', UNI], ['VARIVOLT', 'AEF1-TRZ1', 'AEF1-TRZ2'])

# ------------------------------------------------------------------ localisation des défauts d'isolement (canal → départ → case)
def _case_node(bid, case):
    k = case.replace(' ', '')
    for n in nodes.values():
        if n.get('board') == bid and (n.get('case') or '').replace(' ', '') == k: return n['id']
    return None
def _rows(bid, items):
    out = []
    for ch, txt, case in items:
        out.append(dict(ch=str(ch), txt=txt, case=case, node=_case_node(bid, case) if case and '?' not in case else None))
    return out
T3L2 = [(1, 'QD1', '1+28'), (2, 'QD1', '1+28'), (3, 'QD2', '1+53'), (4, 'QD2', '1+53'), (5, 'QD4', '1+72'), (6, 'QD2', '2+18'), (7, 'QD2', '2+18'), (8, 'QD3', '2+36'),
        (9, 'QD3', '2+36'), (10, 'QDM', '2+43'), (11, 'QD5', '2+72'), (12, 'QTR3A (arrivée)', '3+28')]
T3L5 = [(1, 'QD2', '5+18'), (2, 'QD2', '5+18'), (3, 'QD3', '5+36'), (4, 'QD3', '5+36'), (5, 'QDM', '5+43'), (6, 'QD5', '5+72'), (7, 'QD2', '6+28'), (8, 'QD2', '6+28'),
        (9, 'QD2', '6+53'), (10, 'QD2', '6+53'), (11, 'QD4', '6+72'), (12, 'QTR3B (arrivée)', '4+28')]
T9A = [(1, 'Cardew (limiteur de surtension)', ''), (2, 'case A1-53', 'A1-53'), (3, 'case A2-18', 'A2-18'), (4, 'case A2-36', 'A2-36'), (5, 'case A2-43', 'A2-43'), (6, 'case A3-72', 'A3-72')]
T9B = [(1, 'Cardew (limiteur de surtension)', ''), (2, 'case B2-28 (lecture probable)', 'B2-28?'), (3, 'case B2-53 (lecture probable)', 'B2-53?'), (4, 'case B3-18', 'B3-18'),
       (5, 'case B3-2? (illisible)', 'B3-2?'), (6, 'case B3-43 (lecture probable)', 'B3-43?'), (7, 'case B3-?? (illisible)', 'B3-??'), (8, 'case B3-5? (illisible)', 'B3-5?')]
INSUL = {
 'TGBT3': dict(device='Localisateurs IFL12MC + contrôleurs IM400 (dossier CX7810_C, 12/2024)', src=f'{T3A} p53 (folio 91) et p54 (folio 92)', conf='confirme',
               note='Plusieurs voies désignent les deux tores d’un même départ. Table propre au TGBT 3 : ne pas la recopier sur un autre tableau.',
               groups=[dict(name='Localisateur colonne 2 (Modbus @54) — demi-tableau A', rows=_rows('TGBT3', [(c, f'{r} — case {k}', k) for c, r, k in T3L2])),
                       dict(name='Localisateur colonne 5 (Modbus @55) — demi-tableau B', rows=_rows('TGBT3', [(c, f'{r} — case {k}', k) for c, r, k in T3L5]))]),
 'TGBT9': dict(device='Vigilohm XML3xx ×2 (référence exacte à relever)', src=f'{T9} p22 (tables « LOCALISATION DÉFAUT », photo)', conf='probable',
               note='Tables lues sur photo : les cases marquées « ? » ne sont pas complétées par supposition. Voies 9 à 16 vides.',
               groups=[dict(name='Contrôleur JdB A', rows=_rows('TGBT9', T9A)), dict(name='Contrôleur JdB B', rows=_rows('TGBT9', T9B))]),
}
INSUL['TGBT1'] = dict(device='Vigilohm IM400C + IFL12 ×2 (mis en service le 29/10/2024)', src=T1RPT, conf='confirme',
                      note='Seuils relevés par Schneider en 2024 : préalarme 30 kΩ, alarme 2 kΩ ; inhibition de la partie droite si passage sur le couplage. Table voie → départ non fournie.', groups=[])
D_EXTRA['insul'] = INSUL

# ------------------------------------------------------------------ statut explicite des écarts (actif / résolu / partiel)
for i in issues:
    i.setdefault('status', 'resolu' if 'résolu' in i['title'].lower() else 'actif')

# ------------------------------------------------------------------ fichiers photo : forme Unicode réelle des noms (é composé / décomposé)
import unicodedata as _ud
_PH = _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', '..', 'Plan électrique'))
PHOTOFILES = {}
if _os.path.isdir(_PH):
    for f in _os.listdir(_PH):
        PHOTOFILES[_ud.normalize('NFC', f).strip()] = f
D_EXTRA['photofiles'] = PHOTOFILES
