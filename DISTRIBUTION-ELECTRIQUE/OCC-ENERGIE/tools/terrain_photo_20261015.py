"""Façades et références de terrain — lot du 15/10/2026.

Travail documentaire : aucune nouvelle arête, source d'alimentation, procédure
de manoeuvre ou correspondance de couplage n'est déduite des photographies.
Les noms de départs cliquables sont résolus exclusivement depuis les noeuds du
classeur déjà intégrés au graphe. Les tiroirs sans correspondance restent inertes.
Le lot binaire de 153 photos est livré séparément, pas hébergé par ce script.
"""
TERRAIN_1510 = "Relevé terrain OCF du 15/10/2026 — 153 photos, 10 archives (lot livré séparément)"

LOTS_1510 = {
    'TS15': ('Ts 15.zip', 25), 'TS16': ('Ts 16(1).zip', 16),
    'TGBT2': ('Tgbt 2.zip', 11), 'TGBT6': ('Tgbt 6(1).zip', 13),
    'TGBT9': ('Tgbt 9.zip', 30), 'KV6': ('Tableau 6kv.zip', 22),
    'GORGE': ('Gorge.zip', 11), 'BRONZINI': ('Bronzini.zip', 8),
    'VARIVOLT': ('Varivolt.zip', 13), 'COND6A': ('Onduleur 6 a.zip', 4),
}
for bid, (zipname, count) in LOTS_1510.items():
    if bid in boards:
        boards[bid].setdefault('docs', []).append(
            f'{TERRAIN_1510} — {zipname} ({count} vues HEIC, fichiers image non embarqués)')
        boards[bid].setdefault('photo_terrain', []).append(
            {'date': '2026-10-15', 'archive': zipname, 'nb': count, 'importe': False,
             'statut': 'photos terrain reçues, non hébergées dans le dépôt GitHub'})

# Identification vérifiée sur IMG_4267 : l'archive a un nom trompeur.
boards['COND6A']['note'] = (
    (boards['COND6A'].get('note') or '') +
    ' Relevé 15/10/2026 IMG_4267 : « PROVIENT DE TR 6A — BATTERIE CONDENSATEUR 6A ». '
    'Le ZIP source est nommé « Onduleur 6 a.zip » PAR ERREUR. '
    'Ce lot ne doit pas être rattaché à un onduleur. Origine électrique '
    'à recouper avec le plan de distribution.'
)
ISSUE('I-PHOTO-TR6A', 'moyenne', 'Archive Onduleur 6A : identification erronée',
      'IMG_4267 affiche « PROVIENT DE TR 6A — BATTERIE CONDENSATEUR 6A ». '
      'Les 4 clichés de « Onduleur 6 a.zip » documentent la batterie COND6A '
      'et non un onduleur. Nulle nouvelle liaison électrique créée.',
      [TERRAIN_1510, 'IMG_4267.heic'], ['COND6A'])

def _photo_item(board, pattern, label, y, h=8, kind='drawer'):
    """Associer à un départ EXISTANT seulement, sinon simple forme non interactive."""
    did = _find(board, pattern)
    item = dict(y=y, h=h, k=kind, label=label, plate='black')
    if did:
        item['node'] = did
    else:
        item['nodep'] = True
    return item

# ---- TS15 : 7 tiroirs dans la travée technique (photos IMG_4168-4171).
# Ordre ci-dessous issu des plaques lues ; aucun autre départ du classeur n'est positionné.
boards['TS15']['note'] = (
    (boards['TS15'].get('note') or '') +
    ' Relevé 15/10/2026 : batterie de tiroirs moteurs en façade, '
    'plusieurs portes pleines, colonne de commandes et section distribution centralisée BATCH. '
    'Positions des autres départs du classeur non relevées. '
    'Façade indicative, NON utilisable pour une consignation.'
)
facade('TS15', 'TS15', 'okken_beige', 'TS15 — BATCH', TERRAIN_1510 + ' / Ts 15.zip / IMG_4168 à 4171, 4177, 4189',
    'Façade reconstruite sur photos : travée de tiroirs et portes relevées ; '
    'six départs rapprochés par leurs repères photographiés et leur libellé Excel. '
    'Autres départs : positions inconnues, accessibles depuis « Départs ». '
    'Schéma documentaire non utilisable pour les manoeuvres.',
    brand='MERLIN GERIN / gamme à confirmer', cols=[
      dict(n='TS15 — porte gauche', w=640, units=[
          dict(y=6, h=5, k='plate', label='TS15 / BATCH', node='TS15_J'),
          dict(y=22, h=4, k='plate', label='RÉSERVE (étiquette visible)', nodep=True),
      ], doors=[(4,76)]),
      dict(n='Tiroirs moteurs', w=850, units=[
          _photo_item('TS15', r'2AM01', '2AM01 / VENTILATEUR HVAC / SALLE DE PESAGE', 10),
          _photo_item('TS15', r'2M06.?1', '2M06.1 / BATTERIE CHAUFFE HVAC / SALLE DE PESAGE', 19),
          _photo_item('TS15', r'2M06.?2', '2M06.2 / BATTERIE CHAUFFE HVAC / SALLE DE PESAGE', 28),
          _photo_item('TS15', r'2M06.?3', '2M06.3 / BATTERIE CHAUFFE HVAC / SALLE DE PESAGE', 37),
          _photo_item('TS15', r'2SM01', '2SM01 / MÉLANGEUR', 46),
          _photo_item('TS15', r'2SM02', '2SM02 / MÉLANGEUR', 55),
          dict(y=64, h=8, k='drawer', label='7e TIROIR — REPÈRE NON IDENTIFIÉ', nodep=True),
      ], doors=[(5,74)]),
      dict(n='Commandes', w=420, units=[
          dict(y=18, h=7, k='meter', label='Module indicateur'),
          dict(y=29, h=5, k='voy2', label='Voyants commande'),
          dict(y=40, h=5, k='estop', label='Arrêt / commande — fonction à confirmer'),
      ], doors=[(5,74)]),
      dict(n='Distribution BATCH', w=840, units=[
          dict(y=9, h=6, k='plate', label='DISTRIBUTION CENTRALISÉE / BATCH', nodep=True),
          dict(y=19, h=5, k='paper', label='Schéma affiché en façade'),
          dict(y=42, h=6, k='plate', label='AUTRES DÉPARTS : / VOIR ONGLET « DÉPARTS »', nodep=True),
      ], doors=[(4,75)]),
  ], note='Correspondances électriques conservées depuis le classeur. Localisation exacte des autres départs non établie.')

# ---- TS16 : panneau à deux commandes de pompes, vu de face IMG_4152-4157.
boards['TS16']['note'] = (
    (boards['TS16'].get('note') or '') +
    ' Relevé STEP 15/10/2026 : panneau deux pompes 7P10 et 7P11, '
    'voyants, sélecteurs manuel/auto, reprise égoutture et prises. '
    'Instruction manuscrite : en fonctionnement normal, UNE seule pompe '
    'eau de rivière doit être en automatique. À vérifier par l’exploitant '
    'avant exploitation ; ceci ne constitue pas une procédure de manoeuvre.'
)
facade('TS16', 'TS16', 'okken_beige', 'TS16 — STEP / EAUX USÉES', TERRAIN_1510 + ' / Ts 16(1).zip / IMG_4149 à 4164',
    'Vue générale : trois zones de portes dont deux commandes pompes superposées. '
    '7P10/7P11 identifiés sur étiquettes et rapprochés du classeur. '
    'Position précise des autres départs non connue, sans valeur de consignation.',
    brand='MERLIN GERIN / gamme à confirmer', cols=[
      dict(n='Armoire commande', w=780, units=[
          dict(y=7, h=5, k='plate', label='TS16 — STEP', node='TS16_J'),
          dict(y=19, h=6, k='plate', label='ALIMENTATION COMPTEUR / ZONE DÉCHETS', nodep=True),
          dict(y=43, h=5, k='plate', label='ARMOIRE COMMANDE / EAUX USÉES', nodep=True),
      ], doors=[(4,75)]),
      dict(n='Pompes de rivière', w=850, units=[
          _photo_item('TS16', r'7P10', 'PPE ER 7P10 / POMPE EAU DE RIVIÈRE', 12, 14, 'drawer'),
          _photo_item('TS16', r'7P11', 'PPE ER 7P11 / POMPE EAU DE RIVIÈRE', 29, 14, 'drawer'),
          dict(y=48, h=7, k='plate', label='REPRISE ÉGOUTTURE', m=r'Reprise egoutture', plate='black'),
          dict(y=64, h=5, k='plate', label='PRISE PS 63 A / EAUX USÉES', nodep=True),
      ], doors=[(4,75)]),
      dict(n='Commandes / mesure', w=400, units=[
          dict(y=13, h=8, k='meter', label='Contrôle pompe 7P10'),
          dict(y=30, h=8, k='meter', label='Contrôle pompe 7P11'),
          dict(y=49, h=5, k='voy', label='Voyant reprise égoutture'),
      ], doors=[(4,75)]),
  ], note='Annotation manuscrite sur site concernant les pompes : constat visuel seulement, aucune manoeuvre prescrite.')

# ---- Gorge : trois modules gris clairement visibles (IMG_4234-4244).
# Photo de deux appareils voisins ne prouve ni liaison ni capacité de couplage.
boards['GORGE']['note'] = (
    (boards['GORGE'].get('note') or '') +
    ' Relevé 15/10/2026 : série de modules gris avec ventilation haute/basse, '
    'afficheur, poignée de sectionnement ; alimentation amont non identifiée. '
    'Les modules ne sont ni des cellules 6 kV ni des départs reliés automatiquement.'
)
facade('GORGE', 'GORGE', 'armoire_grise', 'GORGE — FOUR 2', TERRAIN_1510 + ' / Gorge.zip / IMG_4234 à 4244',
    'Relevé visuel des modules gris ; trois unités apparentes sur IMG_4241/4242. '
    'Aucun numéro individuel ni schéma de câblage vérifié. Vue indicative ; aucun départ créé.',
    brand='Constructeur / tension à confirmer', cols=[
      dict(n=f'Module apparent {i+1}', w=720, units=[
          dict(y=13, h=11, k='grille', label='Ventilation haute'),
          dict(y=28, h=8, k='hmi', label='Afficheur GORGE'),
          dict(y=44, h=8, k='handle', label='Poignée de sectionnement'),
          dict(y=57, h=13, k='grille', label='Ventilation basse'),
      ], doors=[(4,76)]) for i in range(3)
  ], note='Les trois modules sont représentés d’après la perspective ; leur identité électrique est à relever.')

# ---- Varivolt 1 et 2 : deux armoires distinctes, aucun couplage déduit.
boards['VARIVOLT']['note'] = (
    (boards['VARIVOLT'].get('note') or '') +
    ' Lot 15/10/2026 : deux armoires séparées Varivolt 1 (zone 1) et '
    'Varivolt 2 (zone 2). Cellules HTA amont/TC et correspondances '
    'électrodes à vérifier sur schémas DM1 ; ne pas confondre avec un tableau commun.'
)
facade('VARIVOLT', 'VARIVOLT', 'armoire_grise', 'VARIVOLT 1 ET 2 — ZONES DISTINCTES',
    TERRAIN_1510 + ' / Varivolt.zip / 13 images',
    'Deux ensembles photographiés distincts. Organisation schématique en deux '
    'colonnes pour différencier les armoires, sans déduction de liaison ou couplage.',
    brand='VARIVOLT — marque et modèle à confirmer', cols=[
      dict(n='VARIVOLT 1 / ZONE 1', w=820, units=[
          dict(y=8, h=6, k='plate', label='VARIVOLT 1 / ZONE 1', nodep=True),
          dict(y=23, h=12, k='hmi', label='Commandes et afficheurs visibles'),
          dict(y=42, h=12, k='handle', label='Appareil de coupure (repère à relever)'),
          dict(y=61, h=6, k='plate', label='SOURCE AMONT NON VÉRIFIÉE', nodep=True),
      ], doors=[(4,75)]),
      dict(n='VARIVOLT 2 / ZONE 2', w=820, units=[
          dict(y=8, h=6, k='plate', label='VARIVOLT 2 / ZONE 2', nodep=True),
          dict(y=23, h=12, k='hmi', label='Commandes et afficheurs visibles'),
          dict(y=42, h=12, k='handle', label='Appareil de coupure (repère à relever)'),
          dict(y=61, h=6, k='plate', label='SOURCE AMONT NON VÉRIFIÉE', nodep=True),
      ], doors=[(4,75)]),
  ], note='Deux armoires physiques. La séparation graphique ne représente pas un jeu de barres ni un couplage.')

# ---- Relevés apportant de la matière aux façades déjà existantes.
for bid in ('TGBT2', 'TGBT6', 'TGBT9', 'KV6', 'BRONZINI', 'COND6A'):
    f = boards[bid].get('facade')
    if f and f in F:
        F[f]['note'] = (
            (F[f].get('note') or '') +
            ' Photos complémentaires reçues le 15/10/2026 ; comparaison repère par repère '
            'en attente. Le dessin antérieur reste inchangé jusqu’à validation des étiquettes.')
ISSUE('I-LOT-1510-CONTROLES', 'moyenne', 'Façades existantes : nouveaux clichés à recouper',
      'Nouveaux relevés TGBT2 (11), TGBT6 (13), TGBT9 (30), tableau 6kV (22), '
      'Bronzini (8) et condensateur TR6A (4). '
      'Aucun changement de départ/couplage ou position des cellules '
      'n’est autorisé sans confrontation des repères aux schémas. '
      'Images JPG livrées hors dépôt ; plaques partiellement illisibles.',
      [TERRAIN_1510],
      ['TGBT2', 'TGBT6', 'TGBT9', 'KV6', 'BRONZINI', 'COND6A'])
