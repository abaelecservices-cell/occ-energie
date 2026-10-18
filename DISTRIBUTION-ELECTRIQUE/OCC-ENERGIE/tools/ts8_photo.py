"""TS8 — relevé extérieur du 15/10/2026.

Ce module ne déduit AUCUN câblage ni ordre de départ d'après la simple disposition.
Les départs existants du classeur TR 4A & 4B, C8:C27 sont réutilisés via 'm'.
Les cases non identifiées restent non cliquables (nodep=True).
Sources photographiques ORIGINALES corrigées : Ts8.zip / IMG_3966 à IMG_3977 (12 vues).\nLe lot 19 clichés du relevé précédent ne sert plus de preuve de cette façade.
"""
TS8_PH = 'Archive TS8 authentifiée — Ts8.zip, IMG_3966 à IMG_3977 (12 vues) ; vue générale IMG_3974 et vue des 5 tiroirs IMG_3966'
boards['TS8']['style'] = 'okken_beige'
boards['TS8']['photo_fidelity'] = 'apparence_generale_recoupee_reperes_non_certifies'
boards['TS8']['note'] = (
    'Tableau TS8 BEIGE à 4 travées numérotées 1 à 4 (photo IMG_3974). '
    'Travée 1 : cinq ensembles extractibles / commandes rotatives confirmés VISUELLEMENT sur IMG_3966 ; la correspondance individuelle '
    'n’est lisible que pour 7PM02 et le surpresseur 4P062. '
    'Travée 4 : disjoncteur principal et afficheur, caractéristiques non lues. '
    'L’alimentation amont TGBT4 case 1-23 est documentaire (source : relevé TGBT4 / classeur), '
    'et non confirmée par une photographie de câble TS8. '
    'Les autres départs du classeur ne sont PAS placés artificiellement sur un tiroir.'
)
boards['TS8']['safety_warning'] = (
    'TS8 — ATTENTION : la façade porte « ALIMENTATION PRISE EN AMONT DU DISJONCTEUR PRINCIPAL ». '
    'L’ouverture de ce disjoncteur ne garantit pas la mise hors tension de tous les circuits. '
    'Les prises et dérivations concernées ne sont pas identifiées ; ne pas utiliser cette '
    'reconstruction comme procédure de consignation. Appliquer la procédure du site '
    'et vérifier l’absence de tension selon les règles applicables.'
)

facade('TS8', 'TS8', 'okken_beige', 'TS8 — GROUPE FRIGO', TS8_PH,
  'Reconstruction schématique d’après IMG_3966-3977 : couleur beige, cinq tiroirs de la travée 1, bandeau de commandes, portes centrales et disjoncteur principal à droite observés ; '
  'implantation fine des circuits inconnus, proportions non cotées et calibres non relevés. La fidélité tiroir-par-tiroir n’est PAS certifiée ; sans valeur de consignation.',
  brand='MERLIN GERIN / SCHNEIDER ELECTRIC (gamme non confirmée)',
  cols=[
    # Travée 1 : 5 tiroirs alignés verticalement ; seuls les rangs 2 et 4 ont un libellé certain.
    dict(n='1', w=850, units=[
      dict(y=9, h=8, k='drawer', label='TIROIR 1 / REPÈRE NON LU', nodep=True, counter=False),
      dict(y=18, h=8, k='drawer', label='7PM02 / POMPE EAU GLACÉE N°2', m=r'7PM02', plate='black', counter=False),
      dict(y=27, h=8, k='drawer', label='TIROIR 3 / REPÈRE NON LU', nodep=True, counter=False),
      dict(y=36, h=8, k='drawer', label='SURPRESSEUR 4P062 / NETTOYAGE FORMING',
           m=r'4P062', plate='white', counter=False),
      dict(y=45, h=8, k='drawer', label='TIROIR 5 / REPÈRE NON LU', nodep=True, counter=False),
      dict(y=56, h=3, k='plate', label='ES02 / VOLET OUEST LOCAL MACHINES FRIGO',
           m=r'Volet ouest local machines frigo', plate='black'),
      dict(y=62, h=3, k='plate', label='ES05 / VOLET EST LOCAL MACHINES FRIGO',
           m=r'Volet est local machines frigo', plate='black'),
      dict(y=68, h=3, k='plate', label='PRISE PS 63A / ÉTIQUETTE SUR PORTE',
           plate='black', nodep=True),
    ], doors=[(4.5, 55), (55, 76.5)]),
    # Colonne de commande attenante ; aucune correspondance électrique prouvée.
    dict(n='', w=310, units=[
      dict(y=16, h=2, k='voy2'),
      dict(y=23, h=4, k='meter', label='Module de contrôle'),
      dict(y=32, h=3, k='plate', label='AVERTISSEUR SONORE', nodep=True, plate='white'),
      dict(y=40, h=3, k='plate', label='ARRÊT KLAXON', nodep=True, plate='black'),
      dict(y=48, h=3, k='plate', label='RÉARMEMENT EV 7220', m=r'Réarmement EV 7220', plate='blue'),
    ], doors=[(4.5, 76.5)]),
    # Travée 2 : porte pleine, étiquettes de circuits de prises et liaison.
    dict(n='2', w=670, units=[
      dict(y=12, h=3, k='plate', label='PRISE PC 63A FOUR 1', m=r'Prise PC 63A Four 1', plate='black'),
      dict(y=61, h=4, k='plate', label='CONVOYEUR DE LIAISON / FORMING-ROVING',
           m=r'Convoyeur de liaison', plate='black'),
    ], doors=[(4.5, 76.5)]),
    # Travée 3 : étiquettes réelles de service ; la seule carte de prise PC 63 A
    # est ambiguë (plusieurs départs possibles dans le classeur), donc pas liée.
    dict(n='3', w=710, units=[
      dict(y=12, h=3, k='plate', label='POMPE EAU GLACÉE / 7PM01',
           m=r'7PM01', plate='black',
           note='Le repère 7PM01 figure sur une annotation jaune manuscrite ; étiquette gravée générique.'),
      dict(y=18, h=3, k='plate', label='GÉNÉRATEUR AIR CHAUD',
           m=r'Générateur air chaud n°3', plate='black',
           note='Numéro 3 présent au classeur mais non lisible sur l’étiquette.'),
      dict(y=36, h=3, k='plate', label='PC 63A / DESTINATION À VÉRIFIER', nodep=True, plate='black'),
      dict(y=44, h=3, k='plate', label='PC VENTILO COULÉE DE VERRE',
           m=r'PC ventilo coulée de verre', plate='white'),
      dict(y=50, h=3, k='plate', label='ARMOIRE GÉNÉRATEUR AIR CHAUD', nodep=True, plate='white'),
      dict(y=62, h=3, k='plate', label='ALIM. POMPE EAU DÉMINÉRALISÉE', nodep=True, plate='black'),
      dict(y=16, h=6, k='arc', label='ATTENTION Risque Classe 1'),
    ], doors=[(4.5, 76.5)]),
    # Cloison intermédiaire visible entre travées 3 et 4.
    dict(n='', w=320, units=[], doors=[(4.5, 76.5)]),
    # Travée 4 : porte du disjoncteur principal. L’avertissement "prise en amont"
    # interdit de l’insérer dans un graphe coupant arbitrairement tous les départs.
    dict(n='4', w=740, units=[
      dict(y=13, h=6, k='arc', label='ATTENTION Risque Classe 1'),
      dict(y=27, h=17, k='ns', label='DISJONCTEUR PRINCIPAL / RÉFÉRENCE NON LUE',
           nodep=True, plate='white'),
      dict(y=52, h=8, k='plate', label='ALIMENTATION PRISE EN AMONT / DU DISJONCTEUR PRINCIPAL',
           nodep=True, plate='red'),
    ], doors=[(4.5, 22), (22, 46), (46, 76.5)]),
    dict(n='', w=300, units=[dict(y=22, h=5, k='hmi', label='Afficheur de mesure')], doors=[(4.5, 76.5)]),
  ])
# La ligne Excel C11 attribue ES02 aux volets EST et OUEST, alors que la façade
# du volet EST porte ES05 : correction par le lien au nœud existant, sans création.
ISSUE('I-TS8-AMONT', 'haute', 'TS8 — circuits alimentés en amont du disjoncteur principal',
      'Plaque rouge sur travée 4 : « ALIMENTATION PRISE EN AMONT DU DISJONCTEUR PRINCIPAL ». '
      'Dérivations et protections concernées non identifiées. '
      'NE PAS déduire une mise hors tension intégrale de l’ouverture du disjoncteur principal. '
      'Pas de topologie de disjoncteur ajoutée sans schéma.',
      [TS8_PH], ['TS8'])
ISSUE('I-TS8-PLACEMENT', 'moyenne', 'TS8 — 3 tiroirs et plusieurs étiquettes non associés',
      'Travée 1 : les tiroirs 1, 3 et 5 ne disposent pas de repère lisible. '
      'Les étiquettes PC 63A, armoire générateur air chaud et pompe eau déminéralisée '
      'ne permettent pas une association sûre au disjoncteur sous-jacent ; '
      'les vingt départs Excel restent consultables dans la liste sans placement inventé.',
      [TS8_PH, 'Copie de Distribution.xlsm › TR 4A & 4B › C8:C27'], ['TS8'])
