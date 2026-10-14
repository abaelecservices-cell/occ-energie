"""Génère les livrables documentaires (docs/) à partir de build/data.json et build/inv_photos.json."""
import os, json, csv, re
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(os.path.join(R, 'build/data.json'), encoding='utf-8'))
INV = json.load(open(os.path.join(R, 'build/inv_photos.json'), encoding='utf-8'))
OUT = os.path.join(R, 'docs'); os.makedirs(OUT, exist_ok=True)
NODE = {n['id']: n for n in D['nodes']}; BOARD = {b['id']: b for b in D['boards']}
CONF = {'confirme': 'Confirmé', 'probable': 'Probable', 'a_verifier': 'À vérifier', 'inconnu': 'Non documenté'}
UP = {}
for e in D['edges']: UP.setdefault(e['b'], []).append(e['a'])

def w(name, text):
    open(os.path.join(OUT, name), 'w', encoding='utf-8').write(text); print(name)

# 1. Inventaire des équipements (CSV ; séparateur ; pour Excel FR)
with open(os.path.join(OUT, '1_INVENTAIRE_EQUIPEMENTS.csv'), 'w', encoding='utf-8-sig', newline='') as f:
    c = csv.writer(f, delimiter=';')
    c.writerow(['Identifiant', 'Type', 'Libellé', 'Tableau', 'Demi-JdB', 'Case', 'Appareil', 'Réglage', 'Alimente', 'Amont direct', 'Confiance', 'Source', 'Réf. classeur', 'Remarque'])
    T = {'src': 'Source', 'cb': 'Disjoncteur', 'sw': 'Interrupteur', 'cpl': 'Couplage', 'bus': 'Jeu de barres', 'tr': 'Transformateur', 'dep': 'Départ', 'load': 'Récepteur'}
    for n in D['nodes']:
        b = BOARD.get(n.get('board') or '')
        c.writerow([n['id'], T.get(n['t'], n['t']), n['label'], b['name'] if b else '', n.get('half') or '', n.get('case') or n.get('cell') or '',
                    n.get('model') or n.get('kva') or '', n.get('ir') or n.get('prot') or '', BOARD[n['feeds']]['name'] if n.get('feeds') in BOARD else '',
                    ' | '.join(NODE[u]['label'] for u in UP.get(n['id'], [])), CONF.get(n.get('conf'), ''), n.get('src') or '',
                    n['xl']['ref'] if n.get('xl') else '', n.get('note') or ''])
print('1_INVENTAIRE_EQUIPEMENTS.csv')

# 2. Registre photo / document -> tableau
used = {}
for b in D['boards']:
    for p in b.get('photos', []):
        f = re.match(r'^(.*?\.pdf)', p, re.I).group(1).strip()
        used.setdefault(f, []).append(b)
FAC_SRC = {fid: f.get('src', '') for fid, f in D['facades'].items()}
with open(os.path.join(OUT, '2_REGISTRE_PHOTOS_SOURCES.csv'), 'w', encoding='utf-8-sig', newline='') as f:
    c = csv.writer(f, delimiter=';')
    c.writerow(['Fichier', 'Pages (photos)', 'Tableau(x) associé(s)', 'Exploitation', 'Pages relevées pour la façade', 'Remarque'])
    for it in INV:
        fn = it['file'].strip()
        bs = used.get(fn, [])
        fac = [b for b in bs if b.get('facade')]
        pages = ''
        for b in fac:
            m = re.findall(r'p(\d+)', FAC_SRC.get(b['facade'], '').split(fn.split('.pdf')[0].strip())[-1][:40]) if fn.split('.pdf')[0].strip() in FAC_SRC.get(b['facade'], '') else []
            pages = ', '.join('p' + x for x in m)
        expl = 'Façade vectorielle reconstruite' if fac else ('Rattaché aux fiches (référence photo)' if bs else 'Non rattaché')
        c.writerow([fn, it['pages'], ', '.join(b['name'] for b in bs), expl, pages, ''])
print('2_REGISTRE_PHOTOS_SOURCES.csv')

# 3. Incertitudes et informations manquantes
txt = ['# Informations incertaines ou manquantes', '', 'Généré depuis le modèle de données de l’application OCC ÉNERGIE. Chaque point est consultable dans l’onglet **Registre**.', '',
       '## Incohérences documentaires', '']
for i in sorted(D['issues'], key=lambda x: {'haute': 0, 'moyenne': 1, 'basse': 2}[x['sev']]):
    txt += [f"### [{i['sev'].upper()}] {i['title']}", '', i['text'], '', 'Documents : ' + ('; '.join(i['refs']) or '—'), '']
txt += ['## Éléments marqués « à vérifier » ou « non documenté »', '', '| Élément | Tableau | Confiance | Motif |', '|---|---|---|---|']
for n in D['nodes']:
    if n.get('conf') in ('a_verifier', 'inconnu'):
        b = BOARD.get(n.get('board') or '')
        txt.append(f"| {n['label']} | {b['name'] if b else ''} | {CONF[n['conf']]} | {(n.get('note') or n.get('src') or '').replace('|', '/')} |")
txt += ['', '## Couplages BT sans règle d’interverrouillage documentée', '']
for b in D['boards']:
    if b['kind'] == 'TGBT' and not (b['coupler'].get('rule')):
        txt.append(f"- {b['name']} : couplage {'présent sur photos (repère non relevé)' if NODE.get(b['id'] + '_QC', {}).get('conf') == 'probable' else 'non documenté'}")
txt += ['', '## Documents attendus', '',
        '1. PowerPoint d’implantation des sous-stations 1 et 2 (ordre des armoires, allées, vis-à-vis, sas SS1).',
        '2. Captures Google Earth (vue aérienne et positions des tableaux secondaires).',
        '3. Cotes des salles et des armoires (télémètre).',
        '4. Procédures de changement de source et de consignation validées (TGBT 1, 2, 4 à 9, TS 9, couplages HTA V500 / SS2 / 6 kV).',
        '5. Réglages des relais des cellules encore marquées « xx » sur l’unifilaire (TR Hydrogène, Varivolt, boosting 6 kV, TR 9B) : les schémas DM1 Varivolt de 2023 décrivent la cellule, pas les seuils du relais.',
        '6. Confirmation de l’attribution TR 1A / TR 2A ↔ TGBT 1 / TGBT 2.',
        '7. Confirmation de l’alimentation du TS 12 (TGBT 2 et/ou TGBT 3) et du TS 17 / TS 9 (TGBT 9 ou TR 2B).',
        '8. Plaques de TR 2A et TR 2B, et correspondance des n° de série France Transfo 1466597 / 1466588 avec TR 3A / TR 3B (les deux PV de janvier 2025 confirment des Trihal 2000 kVA, pas l’identité de chaque cuve).']
w('3_INCERTITUDES_ET_MANQUES.md', '\n'.join(txt))

# 4. Photos à reprendre
rep = ['# Photographies à reprendre', '', 'Motifs relevés lors de l’audit des 476 pages photo (planches-contacts + relevés détaillés).', '',
 '| Fichier | Tableau | Motif | Prise de vue souhaitée |', '|---|---|---|---|',
 '| Ts9.pdf p2 | TS 9 col. 2 | Étiquettes bleues collées illisibles (texte trop petit, reflets) | Gros plan perpendiculaire de la porte col. 2 |',
 '| Ts9.pdf p7 | TS 9 col. 4 | Étiquette du 2e tiroir illisible | Gros plan du tiroir |',
 '| Ts9.pdf p1-p2 | TS 9 col. 1 | Consigne affichée illisible ; automate de permutation non identifié | Gros plan consigne + plaque de l’automate |',
 '| Tgbt 1.pdf | TGBT 1 | Vues en perspective : étiquettes vertes non lisibles à distance | Vue de face redressée colonne par colonne + gros plans des étiquettes |',
 '| Tgbt 5.pdf / Tgbt 6.pdf | TGBT 5, 6 | Idem : perspective forte | Vue de face colonne par colonne |',
 '| Tgbt 9.pdf | TGBT 9 | Surexposition (fond blanc), étiquettes délavées | Photo sans contre-jour, flash désactivé |',
 '| Tr7b .pdf | TGBT 7 | Étiquettes de départs non lues ; seules les étiquettes arc sont lisibles | Gros plans étiquettes de départ |',
 '| Ts 7.pdf | TS 7 | Étiquettes rouges d’arrivée (TS7A / groupe électrogène) en lecture partielle | Gros plans des arrivées et du couplage |',
 '| Ts 12 .pdf, Ts 44.pdf, Ts2.pdf, Ts46a/b | TS 12, 44, 2, 46 | Pas de lecture des étiquettes à l’échelle des photos d’ensemble | Une vue d’ensemble + un gros plan par départ |',
 '| Tableau 20kv SS1 (3 fichiers) | SS1 / SS2 20 kV | Impossible de distinguer les séries SS1 et SS2 ; plaques rouges de cellules non lues | Une photo par cellule avec sa plaque, nommage par tableau |',
 '| Gorge .pdf | Gorge Four 2 | Photos sombres, plaques illisibles | Photo éclairée de chaque armoire |',
 '| Tous | — | Aucune photo de plaque signalétique de transformateur | Plaques TR 1A à TR 9B |',
 '', 'Recommandation : photographier chaque colonne de face (appareil perpendiculaire, à hauteur du milieu de colonne), puis un gros plan par étiquette.']
# 4_PHOTOS_A_REPRENDRE.md est rédigé à la main (contrôle à pleine résolution + 7_AUDIT_QUALITE_PHOTOS.csv) : ne pas l'écraser

# 5. Avancement par tableau
deps = {}
for n in D['nodes']:
    if n['t'] == 'dep': deps.setdefault(n['board'], []).append(n)
av = ['# État d’avancement réel par sous-station et par tableau', '', 'Critères vérifiables (pas de pourcentage global). ✓ fait · ~ partiel/probable · ✗ manquant.', '',
      '| Localisation | Tableau | Topologie amont | Départs | Façade | Couplage | Localisation | Photos |', '|---|---|---|---|---|---|---|---|']
LOC = D['loc']
for b in sorted(D['boards'], key=lambda b: (b.get('loc') or 'ZZ', b['name'])):
    has_up = b['kind'] == 'HTA' or any(h['id'] in UP for h in b.get('halves', []))
    cp = b['coupler']['status']
    av.append(f"| {LOC[b['loc']]['name'] if b.get('loc') else 'Non localisé'} | {b['name']} | {'✓' if has_up else '✗'} | {len(deps.get(b['id'], [])) or '✗'} | {'✓' if b.get('facade') else '✗'} | "
              f"{'✓' if cp == 'documente' else '—' if cp == 'sans_objet' else '~' if cp == 'non_documente' and NODE.get(b['id'] + '_QC', {}).get('conf') == 'probable' else '✗'} | "
              f"{'✓' if b.get('loc') and b.get('loc_conf') == 'confirme' else '~' if b.get('loc') else '✗'} | {'✓' if b.get('photos') else '✗'} |")
av += ['', f"Façades vectorielles reconstruites : {', '.join(BOARD.get(k, {'name': k})['name'] if k in BOARD else k for k in D['facades'])}.",
       f"Départs indexés : {sum(len(v) for v in deps.values())} · Lignes Excel non rattachées : {len(D['xl_left'])}."]
w('5_AVANCEMENT.md', '\n'.join(av))
