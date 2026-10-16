# OCC Énergie — registre de réception vérifié (16 octobre 2026)

> **Document de référence pour éviter les demandes répétées.** Il complète, et prévaut pour la **réception des photos**, sur les anciennes listes `4_PHOTOS_A_REPRENDRE.md` (11/10), `12_TOUR_TERRAIN_FACADES_MANQUANTES.md` (état du modèle au 14/10) et les croix « Photos » de `5_AVANCEMENT.md`. « Photo non intégrée dans Git » ne signifie PAS « photo non transmise ». Les relations électriques non validées le restent.

## Méthode et sources contrôlées

- Examen des fichiers originaux de la **bibliothèque de cette conversation** : archives `Ts1.zip`, `Ts8.zip`, `Ts9.zip`, `Ts17A .zip`, `Ts17b.zip`; liste de réception des autres archives ; `OCC_ENERGIE_PHOTOS_TERRAIN_266_JPG.zip`, `OCC_ENERGIE_MANIFESTE_PHOTOS_20261015.json` et `OCC_ENERGIE_COMPLET_PHOTOS_15_10_2026.html`.
- `OCC_ENERGIE_PHOTOS_TERRAIN_266_JPG.zip` : **266 fichiers JPG dans 18 dossiers**, lecture ZIP et empreintes SHA-256 des 266 JPG validées contre son manifeste ; il ne s'agit pas de 266 armoires différentes.
- Les deux ZIP `Ts17A .zip` et `Ts17b.zip` : chacun 14 JPEG réels, **les mêmes 14 images et les mêmes empreintes** ; dédoublonnage impératif.
- GitHub (cette branche) : `sources/` contient seulement `photo_site_exploitant.jpg` et `referentiel_excel_2024.json` ; **pas** les archives photographiques ci-dessous. `assets/photos_terrain/` n'existe pas. Le catalogue GitHub de réception n'atteste donc pas la présence des binaires.
- L'HTML autonome avec photothèque (~77,8 Mo) en bibliothèque est un **livrable séparé** du `OCC_ENERGIE.html` de cette branche (~6,86 Mo). Leur code et leur base de données ne doivent pas être considérés identiques sans rapprochement fonctionnel.

## Sources DÉJÀ FOURNIES — ne jamais réclamer à nouveau la même série générique

| Ensemble | Fichier(s) fourni(s) / vérifiés | Couverture certaine |
| --- | --- | --- |
| TS17A et TS17B | `Ts17A.pdf`, `Ts17b.pdf` (façades historiques) ; `Ts17A .zip`, `Ts17b.zip` | Deux ZIP récents identiques : 14 photos des **quatre armoires aval des tours** ; les PDF documentent les TS17. Ne pas appeler ces 14 photos les façades TS17A/B. |
| TS8, local frigo | `Ts8.zip` (12 JPEG), relevé de 19 photos déjà exploité le 15/10 | Façade TS8 documentée et dessinée ; plusieurs correspondances protections/étiquettes restent incertaines |
| TS9, chaufferie | `Ts9.zip` (12 JPEG) et `Ts9.pdf` | 15 étiquettes bleues transcrites, mais pas toutes associées à une protection |
| TS1, ensimage | `Ts1.zip` (15 HEIC) et relevés d'ensimage | Façade TS1 dessinée ; **deux autres armoires ensimage** indépendantes déjà photographiées, origines amont inconnues |
| TS15, Batch | `Ts 15.zip` (25) | Façade documentaire dessinée |
| TS16, STEP | `Ts 16.zip` / `Ts 16(1).zip` (16) | Façade documentaire dessinée |
| TGBT2 | `Tgbt 2.zip` (11) | Photo et façade |
| TGBT6 | `Tgbt 6.zip` / `Tgbt 6(1).zip` (13) | Photo et façade |
| TGBT7 | `Tgbt 7.zip` (36 fichiers photo : 30 HEIC et 6 JPEG) | 30 JPG dans photothèque, ne pas compter les doubles formats comme 36 vues distinctes |
| TGBT9 | `Tgbt 9.zip` (30) | Photo et façade |
| Tableau 6 kV | `Tableau 6kv.zip` (22) | Photos reçues ; l'ordre Spang L1–L3 reste à fiabiliser |
| Gorge Four 2 | `Gorge.zip` (11) et relevé antérieur | Façade documentaire existante, origine électrique incertaine |
| Varivolt 1 et 2 | `Varivolt.zip` (13) et `Varivolt1 et 2 .pdf` | Deux ensembles, ne pas fusionner leurs origines |
| Bronzini | `Bronzini.zip` (8) et ancien PDF | Départs à recouper, certains libellés demeurent peu nets |
| Condensateurs TR6A | `Onduleur 6 a.zip` (4) | **Ce ne sont pas des photos d'onduleur** |
| Groupes 1 et 2 | `Groupe n1.zip` (4), `Groupe n2 .zip` (9) | Trois travées repérées, une travée couplage commune, raccordements électriques non démontrés |
| Tours aéroréfrigérantes / TS17 aval | `Tour aéro .zip` (14), autres dossiers de synthèse | Destinations et plaques A1/A2/C1/secours photographiées |
| Pompes eau glacée | `Pompe eau glace 7pm 65 et 7Pm03.pdf` et copie (1) | Document présent ; les étiquettes précises peuvent rester floues |

**Le lot de 10 archives du 15/10 contient 153 photos** (TS15, TS16, TGBT2/6/9, 6 kV, Gorge, Varivolt, Bronzini, condensateurs TR6A). Il a été recensé dans GitHub mais ses binaires n'ont pas été importés. Des regroupements et livrables de photos existent déjà en bibliothèque ; leur absence de GitHub n'est PAS un motif pour redemander les originaux à l'exploitant.

## ERREUR AVÉRÉE : inversion des séries TS1 / TS8 dans la photothèque

**Les archives originales et les 266 JPG ont été comparés :**

- `Ts1.zip` contient **IMG_3978 à IMG_3992 (15 HEIC)** ; la photothèque classe ces 15 photos sous **TS8 — Groupe frigo**, au lieu de **TS1 — Ensimage**.
- `Ts8.zip` contient **IMG_3966 à IMG_3977 (12 JPEG)** ; la photothèque en classe 11 sous **TS1 — Ensimage** (IMG_3967 à 3977, dont deux suffixés « (1) »), au lieu de **TS8 — Groupe frigo**.
- **IMG_3966.jpeg** de l'archive TS8 originale n'a pas d'entrée correspondante dans la photothèque de 266 JPG.
- Comparaison de pixels après réduction pour IMG_3967, IMG_3970 et IMG_3972 : corrélation **1,000**, confirmant que les clichés placés sous TS1 proviennent matériellement de `Ts8.zip`.
- Le même mauvais classement `g` / `b` est présent dans les données photographiques de `OCC_ENERGIE_COMPLET_PHOTOS_15_10_2026.html`.

**À faire, par le projet logiciel et NON par le technicien :** corriger les métadonnées, réintégrer IMG_3966, refaire la photothèque et comparer les façades TS1/TS8 sur les photos sources. Ne pas échanger aveuglément les liaisons amont ni les positions de départs existantes : la correction de classification photo et la validation électrique sont deux opérations différentes.

## État GitHub et liste des vrais travaux internes

- Modèle consolidé du 15/10 : **66 tableaux, 23 transformateurs, 503 départs, 735 liens, 730 fiches, 33 écarts**. **21 départs sans chaîne amont complète**.
- Les listes « sans photo » du 11/10 ou du 14/10 sont **historiques**. Le registre `5_AVANCEMENT.md` signale parfois « Photos ✗ » pour TS1, TS8, TS15, TS16 et ensimage **parce que les originaux ne sont pas dans GitHub**, alors que les séries ont été reçues.
- Préalable logiciel : **rassembler les photos déjà fournies**, corriger le classement TS1/TS8, intégrer les sources binaires et références, contrôler les façades/documentations, régénérer les quatre HTML, vérifier l'arborescence et les scénarios de perte de source.
- `PR #16` (consolidation) reste en brouillon, non fusionnée dans `main`. Tests locaux consignés comme réussis, GitHub Actions bloqués avant première étape (message de compte/plafond de dépenses) ; aucune fusion validée.

## Chaînes électriques à valider — uniquement les données décisives pour le dépannage

1. Tours : l'étiquette de l'armoire A1 indique **TS17B** et A2 **TS17A**, contrairement à deux lignes du classeur. Il reste à rattacher, par schéma à jour ou repère de câble, départ TS17A C11 / TS17B P21 vers leur arrivée réelle.
2. TS9 / TS17 : lever le conflit **TGBT9 vs ancien TR2B**, préciser le départ TS9 de l'armoire de commande C1, l'alimentation secours et la permutation groupe.
3. TS8 : identifier exactement **quels circuits restent alimentés en amont du disjoncteur principal** et quels dispositifs les protègent ; ne pas interpréter l'ouverture de ce disjoncteur comme une mise hors tension intégrale.
4. Ensimage : identifier les départs amont des **deux armoires distinctes** et du coffret agitateur. Les photographies reçues ne prouvent pas les liaisons.
5. Réseau principal : vérifier l'identité réelle des cellules **TR1A/TR2A** face aux mentions inversées de l'ancien unifilaire. Préserver la règle d'exploitation fournie **TR1A/B→TGBT1, TR2A/B→TGBT2**.
6. Sécurités/couplages : TGBT3 Ronis contradictoire entre plan et texte ; tableau TGBT8, groupes 1/2, source normale/secours. Toute manœuvre reste réservée à une procédure validée.
7. Onduleur 2 : alimentation du by-pass **TGBT5A vs TGBT6** ; autres écarts documentés : groupe froid 7H214, TS42/TS43, TGBT7 7K121/7K122, ordre Spang 6 kV.
8. Localisation : compléter les **correspondances repère → bâtiment/salle/tableau/colonne/case**, sans demander de plaque constructeur ni de cotes inutiles.

## Équipements dont la couverture photographique exploitable n'a PAS été établie dans les séries rapprochées

**Ce n'est pas une injonction de rephotographier avant épuisement des anciens PDF et classeurs.** D'après `5_AVANCEMENT.md`, il reste à rechercher la preuve dans les documents déjà disponibles pour : poste de livraison 20 kV (façade dessinée d'après unifilaire, pas de photos certifiées), TS24, TS28, TS42, TS43, TSO, HVAC canal 3, tableau étuves 7-8-9, éclairage ensimage 9M04, coffrets ondulés étuves 1–6 / 7–10 et coffret agitateur. Les coffrets des pompes 7PM65 / 7PM03 ont déjà un PDF.

**Protocole de demande future :** avant chaque demande, consulter ce registre, `5_AVANCEMENT.md`, les photos et PDF d'origine et le dossier d'écarts. Si une pièce précise manque vraiment, demander uniquement **le repère de départ, la case, l'arrivée, la protection, le schéma de liaison ou le lieu concerné**, en indiquant quelle source existante a été exploitée et pourquoi elle ne suffit pas. Jamais une série générale déjà fournie. Éviter les plaques signalétiques non utiles au diagnostic et à la topologie.

## Limites

Cette vérification valide la **réception, l'identité et le classement de fichiers**, pas les câbles sur site ni les règles de manœuvre. Les fichiers du dépôt et ceux de la bibliothèque restent séparés tant qu'une importation explicite et vérifiée n'est pas exécutée. Le fichier `OCC_ENERGIE_COMPLET_PHOTOS_15_10_2026.html` doit être corrigé lui aussi avant de le présenter comme une référence définitive.
