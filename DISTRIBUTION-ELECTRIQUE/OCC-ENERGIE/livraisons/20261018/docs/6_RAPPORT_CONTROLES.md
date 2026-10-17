> Rapport historique : les chiffres et essais ci-dessous décrivent leur date initiale. État courant du 15/10/2026 : 51 façades (dont une vue partielle agitateur) sur 62 tableaux/coffrets. Pour la livraison actualisée, consulter 8_COMPARAISON_2026-10-15.md et les listes courantes 4_PHOTOS_A_REPRENDRE.md / 9_INFORMATIONS_RESTANTES.md.

# Rapport des contrôles — OCC ÉNERGIE v1.0.0 (10/10/2026)

## Passage 1 — Conformité aux fichiers sources

| Contrôle | Méthode | Résultat |
|---|---|---|
| Inventaire des fichiers | 50 PDF (476 pages photo, aucune page texte), 1 classeur .xlsm, 4 zip (plans Schneider, onduleurs, varivolt), unifilaire 20 kV (1 page vectorielle) | Fait — `2_REGISTRE_PHOTOS_SOURCES.csv` |
| Planches-contacts | 64 planches générées et examinées (TGBT 1-6, 9, TS 2/7/9/12/17B/44, HTA, Gorge, Gradathyr…) | Fait |
| Topologie HTA | Lecture zoomée de l’unifilaire R112529 rév. H : poste de livraison, SS1 (18 cellules), SS2 (19 cellules), 6 kV (9 cellules), réglages de protection lus cellule par cellule | Fait — croisement TR 1A/TR 2A signalé |
| Classeur Excel | Extraction cellule par cellule (onglet + référence) ; contrôle d’exhaustivité automatique | 0 ligne non rattachée |
| Dossiers Schneider | TGBT 2 (TH112001 rév. F, 88 p.) et TGBT 3 (CX781001, 94 p.) : listes des consommateurs, cases, appareils, réglages | Repris dans le modèle et les façades |
| Procédure TR3A | Texte constructeur repris mot pour mot dans l’application | Fait (TR3B scanné : à transcrire) |
| Façade TGBT 4 | Étiquettes relevées sur Tgbt 4.pdf p2, p5, p9, p11, p12 | 18 départs + arrivées + couplage lus |
| Façade TS 9 | Ts9.pdf p1, p2, p5, p7 | Étiquettes noires lues ; bleues illisibles (signalé) |

## Passage 2 — Cohérence implantation / schéma électrique

12 incohérences documentées et visibles dans l’application (onglet Registre, fiches concernées, rapport de dépannage) :
croisement TR 1A/2A ↔ TGBT 1/2 · alimentation du TS 12 (3 sources documentaires) · origine TS 17/TS 9 (TGBT 9 ou TR 2B) · FRIGO 7H214 (TGBT 1A ou 3B) ·
TGBT 3 absent du classeur · TGBT 3 « Sous-station 2 » mais alimenté depuis SS1 20 kV · puissance TR2/TR3 (2000/2500 kVA) · TS42/TS43 · bloc TS 24B dupliqué ·
coffret agitateur sans parent · étiquette arc TS 9 · photos du tableau 20 kV SS2 non identifiées · implantation physique des TGBT.

## Passage 3 — Contrôles fonctionnels (navigateur Chromium, bureau 758-1400 px et mobile 375×812, thèmes clair et sombre)

| Scénario | Attendu | Résultat |
|---|---|---|
| Recherche « Étuve 2 » | Onglet TR 6A & 6B, cellule H9, TGBT 6A | ✓ 1er résultat, fiche avec réf. Excel H9 |
| « étuv » | Résultats dès les premiers caractères | ✓ TS 2 Étuves, Étuves 7-8-9, Étuve 2, Étuve 1… |
| « 7K121 » (scénario G) | Tableau, colonne, case, 2 transfos, couplage, même alimentation | ✓ Sécheur 7K121 (TS 9 JdB B) + Compresseur 7K121 (TGBT 7A) ; 9 chemins amont |
| « silo kaolin » | Départ TS 9 | ✓ |
| « couplage TS9 » | Couplage jeu de barres TS 9 | ✓ |
| « TR 6A », « TGBT 2 », « tgbt2 » | Transformateur / tableau en tête | ✓ |
| Tolérance accents/espaces/casse | « tgbt2 », « Etuve », « ups » (synonyme onduleur) | ✓ |
| Voir sur la façade | Ouverture de la façade, zoom et surbrillance du compartiment | ✓ (TGBT 4 case 4-28) |
| Scénario H — choix de source | A seul / B seul / couplage sur A / sur B / normal | ✓ TGBT 2, 3, 4, 9 : demi-JdB coupé = départs en rouge |
| Interverrouillage | 3 appareils fermés sur TGBT 3 | ✓ « Configuration INTERDITE (clés Ronis) » |
| Perte source CNR (EDF ouverte) | Tout le site hors tension | ✓ 0 départ alimenté ; fermeture EDF → 413 alimentés |
| Retour par sous-tableau | Le TS 12 alimenté des deux côtés ne doit pas réalimenter l’autre demi-JdB | ✗ puis corrigé (propagation orientée amont→aval) ✓ |
| Scénario E — « Perte alimentation TGBT 2 » | Chemin amont, transfos, protections, incertitudes, distinction théorique/procédure | ✓ 8 sections + bandeau d’incohérence TR 1A/2A |
| Bandeau de simulation | Présent sur Réseau, Tableau, Dépannage | ✓ |
| Console JavaScript | Aucune erreur | ✓ |
| Fichier autonome | Aucune ressource externe (pas de CDN, polices système) | ✓ 418 Ko, un seul fichier |

## Non testé

- Ouverture réelle sur iPhone (Safari iOS / app Fichiers) : test émulé uniquement (375×812). À faire par l’utilisateur ; points d’attention : ouverture depuis l’app Fichiers, stockage local du journal d’entretien.
- Liens « Ouvrir la source (PC) » : fonctionnent uniquement sur le PC où le dossier `DISTRIBUTION-ELECTRIQUE` est sur le Bureau.

## Version 1.1 — reprise (plans d’implantation, vue aérienne, façades photos, interverrouillages)

| Contrôle | Résultat |
|---|---|
| Vue aérienne | Détourée à la première délimitation rouge ; repère 19 (tente de stockage) retiré ; repères 2 fusionnés ; étiquettes affichées seulement pour SS1, SS2 et PDL |
| Sous-station 1 | Côtés gauche et droit accolés, cloison fine avec ouverture ≈ 1 m ; traits orange = face avant visible ; doubles flèches = vis-à-vis (cliquables) |
| Interverrouillage sources | Fermeture EDF avec CNR fermée : **refusée** ; perte CNR → bascule automatique EDF (440/444 départs réalimentés, les 4 restants = coffret agitateur sans amont documenté) |
| Interverrouillage 2 sur 3 | Couplage TGBT / TS 2 / TS 44 avec les deux arrivées fermées : **refusé** ; changements de mode de source sans passer par l’état interdit |
| Façades | 18 façades : TGBT 1 à 7 et 9, TS 2, 7, 9, 12, 17, 44, tableaux 20 kV (×3) et 6 kV |
| Fiches | 641 éléments + 37 bâtiments ouverts sans erreur JavaScript |
| Fichier | OCC_ENERGIE.html — 801 Ko, autonome |

## Version 1.2 — 11/10/2026

| Contrôle | Résultat |
|---|---|
| Relecture à pleine résolution | TS 44 colonne 1 (6 tiroirs confirmés) ; TGBT 9 (A1-28, A1-53, AB-53) ; TS 46B (plaque constructeur) ; alimentations ondulées 1 et 2 (toutes les plaques vertes) ; Gradathyr zones 1 et 2 ; batteries condensateurs TR1A / TR1B |
| Audit automatique des photos | 476 photos notées (netteté, surexposition, sous-exposition) : `7_AUDIT_QUALITE_PHOTOS.csv` |
| Nouvelles façades | 24 façades ajoutées, soit 42 au total |
| Nouvelles liaisons | TGBT 5 / TGBT 6 → onduleurs → alimentations ondulées ; by-pass total depuis le TGBT 5A ; batteries de condensateurs reliées aux TGBT 1, 2, 5, 6 |
| Interverrouillage by-pass onduleur | Fermeture du by-pass avec l’arrivée onduleur fermée : **refusée** ; après ouverture de l’arrivée : acceptée |
| Fiches / vues | 674 éléments, 60 tableaux × 5 onglets, 4 plans, 37 bâtiments : 0 erreur |

## Version 1.3 — 11/10/2026 — lecture détaillée de l’unifilaire 20 kV

Méthode : extraction des 1 124 lignes de texte avec coordonnées + 21 tuiles agrandies à 320 % + zooms ciblés (couplages, câbles 6 kV).

| Élément relevé | Intégré |
|---|---|
| N° de schéma Schneider (Sch.) et repère de chaque cellule | 36 cellules |
| Rapport de TC retenu (valeur soulignée / encadrée), ITH, relais, réglages I> / I>> / Io | toutes les cellules renseignées |
| Clés d’interverrouillage (nom, code EL…, emplacement, état dessiné) | 4 boîtes de clés + clés de 30 cellules |
| Câbles (E00.101 à E00.108, 001 à 004, POPY Al) | oui |
| Transformateurs : couplage (Dyn / YNd), neutre (terre, résistance), surveillance (sondes / DGPT2), disjoncteur BT, clés BT, destination écrite | 23 transformateurs |
| Poste de livraison : 8 cellules (CS-400A, CS-50A, 2 × 400A-CIT par source) | modèle et façade mis à jour |
| Couplages : V500 = disjoncteur + remontée ; tableau TR 7/9 = interrupteur + remontée ; 6 kV AEF2-C = interrupteur + remontée | oui |
| Nouvelles incohérences | codes de clés en double (EL13131, EL53511) ; TC des deux boosting ; cellules non renseignées (xx) ; preuve supplémentaire de l’inversion TR 1A / TR 2A (disjoncteur NW32H1 5.0P = arrivée TGBT 1A) |
| Contrôle | 682 éléments, 60 tableaux, toutes les vues : 0 erreur ; aucun conflit d’interverrouillage à l’état initial ; perte CNR → bascule EDF |


## v1.4 — Fiches de dépendance (11/10/2026)

| Contrôle | Résultat |
|---|---|
| Fiche de dépendance pour chaque élément (départ, arrivée, jeu de barres, transformateur, cellule) et chaque tableau | 739 fiches générées, 0 erreur |
| Contenu | chaîne source → départ ; démarche du départ vers la source (étendue de la coupure, départ, jeu de barres / arrivée / couplage, tableaux amont, transformateur et cellule HTA, 20 kV et poste de livraison) ; secours documentés ; aval ; clés ; procédures |
| Règle de sécurité | aucune séquence de manœuvre générée ; configuration de secours par couplage affichée seulement si la règle d’interverrouillage est documentée (clés Ronis 1-1-0), sinon « aucune configuration proposée » |
| Chemin « normal » retenu | appareils fermés, sous tension en simulation, le moins de couplages possible (côté TR xA du 20 kV alimenté par l’arrivée CNR via le couplage V500, conforme au modèle) |
| Départs sans chaîne amont documentée | 7 (alimentations non documentées : voir 3_INCERTITUDES) |
| Accueil | cartes « Bâtiments équipés » expliquées (numéro = bâtiment de la vue aérienne, pastille = état simulé, « Emplacement probable ») ; noms des bâtiments corrigés (lecture de la légende de la vue aérienne) |


## v1.5 — Ordres de manœuvre (projets à valider) (11/10/2026)

| Contrôle | Résultat |
|---|---|
| Ordres rédigés dans chaque fiche | « départ déclenché » (tous les départs) ; « demi-jeu de barres hors tension → réalimentation par le couplage » et « retour à la normale » pour les 11 tableaux dont le couplage relie directement deux demi-jeux de barres (TGBT 1 à 9, TS 2, TS 44) |
| Contenu de chaque ordre | habilitation ; conditions préalables ; cas d'arrêt (STOP : ne pas coupler si l'arrivée a déclenché sur défaut) ; puissance disponible (In du transformateur restant) ; interverrouillage (clés Ronis TGBT 3 / règle 2 sur 3) ; étapes numérotées à cocher ; bloc de signature à l'impression |
| Rejeu automatique des 44 ordres (22 secours + 22 retours) dans le simulateur | 44/44 : aucune manœuvre refusée, demi-jeu de barres réalimenté, aucun conflit, retour exact à l'état initial |
| Non rédigés (documents insuffisants) | TS 12 (départs non attribués aux demi-jeux de barres) ; TS 9 (arrivée secours groupe, logique non documentée) ; toutes les séquences HTA 20 kV / 6 kV (logique des clés non décrite sur l'unifilaire) |
| Statut | tous les ordres sont des PROJETS ; ils passent « Validé » uniquement via le registre validations.json (signature du chargé d'exploitation) |


## v1.6 — Application recentrée sur « remettre le courant » + orthophoto IGN (11/10/2026)

| Élément | Résultat |
|---|---|
| Parcours « ⚡ Remettre le courant » (onglet Courant, bouton d'accueil, bouton de chaque fiche) | 3 touches : quoi est coupé → que constatez-vous → fiche de manœuvre ; 1 913 fiches générées sans erreur |
| Fiche de manœuvre | titre, emplacement, STOP en rouge, « avant de commencer » (4 lignes max), étapes numérotées à cocher avec appareil + case ; statut « projet non validé » sur une ligne ; détails techniques repliés |
| Situations | départ seul ; demi-TGBT coupé (couplage) ; TGBT entièrement coupé (contrôles 20 kV) ; retour à la normale ; tableau secondaire coupé (départ d'alimentation) ; transformateur hors service ; tableau 20 kV coupé (contrôles) |
| Rejeu des 44 ordres couplage / retour | 44/44 sans interverrouillage refusé |
| Allègement | accueil (bouton, 3 salles, carte) ; fiche appareil (essentiel + « Plus d'informations » replié) ; page tableau (simulation et notes repliées) ; plans (liste d'équipements repliée) |
| Orthophoto IGN 2024 (20 cm/px) | extraite du fichier OCC_usine_vue_zoomable.html (tools/ortho.py), 400 Ko ; repères des 37 bâtiments reportés par recalage automatique (tools/recale_ortho.py) et contrôlés visuellement ; liaisons 20 kV PDL → sous-stations |
| Plans | vue unique « Liaisons 20 kV → transfos → TGBT » : 20 kV en violet, BT en vert, arrivée du poste de livraison sur chaque tableau 20 kV |
| Sans fiche possible (alimentation non documentée) | COFAGIT, OM27, ARM110, VENTIL, DECARBO, GORGE, GRADATHYR, VARIVOLT, AUX7B |


## v1.7 — Couplage TGBT et carte sans halo (11/10/2026)

| Élément | Résultat |
|---|---|
| Règle exploitant : chaque TGBT est scindé en deux, chaque moitié sur son transformateur ; le couplage ne se ferme qu'après ouverture de l'arrivée qui alimentait la moitié | appliquée par le simulateur sur la position des appareils (avant : seulement si les deux transformateurs étaient sous tension — un couplage avec l'arrivée du transformateur perdu encore fermée était accepté, corrigé) |
| Tests | couplage refusé tant que l'arrivée est fermée ; accepté après ouverture, demi-TGBT réalimenté ; refermeture de l'arrivée refusée tant que le couplage est fermé ; 44/44 ordres sans refus |
| Fiches de manœuvre couplage / retour | règle écrite en tête ; schéma « maintenant → après » (TR A, arrivée A, ½ A, couplage, ½ B, arrivée B, TR B) ; schéma normal sur l'écran « Que constatez-vous ? » |
| Plans | TGBT dessinés en deux demi-tableaux (A ▢ B) avec le couplage ; chaque transformateur relié à sa moitié ; plus de halo vert (rouge seulement si coupé en simulation) |
| Carte du site | plus de remplissage ni d'étiquette permanente : contour + nom au survol, fiche au toucher |


## v1.8 — Tableaux HTA et TGBT 8 reconstruits sur photos (11/10/2026)

| Élément | Résultat |
|---|---|
| Tableau 20 kV CNR / EDF TR 1 à 6 | 18 cellules relevées sur 45 pages de photos (deux fichiers : « Tableau 20kv edf cnr » et « Départ 20kv edf cnr ») : plaques, bandeaux, relais, voyants, cadenas, boîtes à clés |
| Tableau 20 kV TR 7 / 9 / boosting | 19 cellules ; ordre de l’unifilaire confirmé plaque par plaque (hydrogène, Varivolt zones 1 et 2, boosting, TR 7, TR 9, arrivées, couplage) |
| Tableau 6 kV | 10 cellules dans l’ordre vu de face ; remontée « TABLEAU 6 KV » ajoutée ; 3 plaques Spang illisibles (positions estimées) |
| TGBT 8 (boosting) | façade faite (photos rangées dans « Tableau 20kv     SS1.pdf » p1-p11) : arrivée 1 = TR 8B, arrivée 2, couplage, contrôle (localisateurs XL308 : neutre IT), armoires Gradathyr creuset reliées aux départs ZONE du classeur |
| Corrections | « Départ 20kv edf cnr.pdf » n’est pas le poste de livraison (aucune photo du poste) ; nouvel indice d’inversion TR 1A / TR 2A sur l’unifilaire (plaques) ; ordre des groupes Spang L4-L6 différent de l’unifilaire ; cellules « Varivolt zone 1 / 2 » = alimentation probable des Varivolt |
| Contrôle | 60 tableaux × 5 onglets, toutes les fiches et vues : 0 erreur ; 43 façades sur 60 |
| Liste des photos manquantes | 4_PHOTOS_A_REPRENDRE.md (14 sans photo, 4 à refaire sans façade, 6 à refaire partielles, gros plans) |


## v1.9 — Archives ZIP exploitées + arborescence du réseau (11/10/2026)

| Élément | Résultat |
|---|---|
| Archives | p1.zip (10_TGBT N°1, 11_TGBT N°2), p1 - Copie.zip (12_TGBT N°3), p1 - Copie (2).zip (20_VARIVOLT, 22_Onduleurs), p1 - Copie (3).zip vide. Dossiers 13 à 19 et 21 absents. |
| Transformateurs TGBT 3 | Trihal 2000 kVA 20 kV / 410 V Dyn11 Ucc 6 %, secs enrobés, sondes + relais NT935, n° 1466597 / 1466588 (essais 01/2025) ; gaine à barres Canalis KTA 3200 A ; incohérence I-TR-KVA mise à jour (DGPT2 de TR 3B à vérifier) |
| Varivolt | cellules DM1-A 400 A (SF1, TC ARM3 200-100/5, VPIS, CSH120), clés X0101/S0101/O0101 et X0201/S0201/O0201 ; procédures constructeur P-VARIVOLT1 / P-VARIVOLT2 (buts des verrouillages) |
| Coffrets ondulés étuves | 2 coffrets ajoutés (plans du 01/12/2024) : étuves 1 à 10, générateurs 1, 2, 3, baies informatiques ; arrivée 4 × 63 A + MX arrêt d’urgence |
| Arborescence | onglet Tableaux : CNR / EDF → poste de livraison → sous-station → tableau 20 kV → transformateurs → TGBT (½ A / ½ B, couplage) → TS → coffrets ; 53 tableaux sur 62 (9 sans alimentation documentée) ; recherche et repli |
| Correction | la vue « Par localisation » oubliait les tableaux situés en SS1 côté gauche / droit, chaufferie et STEP : 62 tableaux affichés |
| Contrôle | toutes les vues, fiches et ordres : 0 erreur ; 44/44 ordres de couplage / retour sans refus |


## v1.10 — Carte du site épurée (11/10/2026)

| Demande | Fait |
|---|---|
| Fusionner les parties du bâtiment n° 2 | les 3 repères « 2 » du PowerPoint forment un seul contour (réunion calculée, 10 sommets) ; règle appliquée à tout bâtiment à plusieurs repères |
| N° 20 = piscine | nommé « Piscine » |
| Les numéros (« bât. 31 »…) sont une légende de repérage | retirés de tous les textes affichés (noms de salles, tableaux, fiches, plans, schéma réseau, tuiles d’accueil, fiche bâtiment) ; garde-fou dans build_app.py |
| Annotations inutiles | ligne de sources sous la carte, pastille « Bâtiment n », lignes « Rattachement » / « Source » de la fiche bâtiment retirées ; seule la mention légale « © IGN BD ORTHO® 2024 » est conservée |
| Contrôle | toutes les vues : 0 erreur ; aucune mention « bât. NN » dans l’application |


## v1.11 — Vue « Plans » : PDL puis sous-stations, armoires rattachées à leur source (11/10/2026)

| Demande | Fait |
|---|---|
| Seulement le PDL CNR / EDF puis les sous-stations | 3 onglets : PDL CNR / EDF · Sous-station 1 · Sous-station 2 (les onglets « Local chaufferie » et « STEP » sont retirés) |
| PDL | schéma de principe d’après l’unifilaire (aucun plan ni photo) : arrivées CNR / EDF, 8 cellules, départs normal / secours vers les deux sous-stations, état simulé ; cellules et sous-stations cliquables |
| Chaufferie, STEP et autres armoires rattachées à leur source | sous chaque plan de sous-station : « Armoires alimentées depuis la sous-station », regroupées par tableau source, arborescence repliable ; 📍 ouvre le plan du local (chaufferie : Sous-station 1 › TGBT 9 › TS 17 ; STEP : Sous-station 1 › TGBT 7 › TS 16) |
| Contrôle | 5 plans, focus de chaque tableau, toutes les vues : 0 erreur |


## v1.12 — Vue du site recadrée et tournée (11/10/2026)

| Demande | Fait |
|---|---|
| Partir de la photo fournie, tourner de 90° sens antihoraire | appliqué à l’orthophoto IGN (même cadrage, bien plus nette que la capture 370 × 487 px) : nord à gauche, comme la vue du PowerPoint |
| Supprimer le « rectangle vert » autour | découpe juste à l’intérieur de la bande de pelouse qui entoure l’usine (côté ouest, deux décrochés au sud des tentes et de la cour, bande le long du champ et de la voie ferrée) : champ, bois et bâtiments au sud retirés ; usine, STEP, poste de livraison, château d’eau, piscine conservés |
| Bâtiments | 37 / 37 conservés et reportés par la même transformation ; flèche du nord orientée à gauche ; image 2 372 × 1 744 px (≈ 220 Ko) |


## v1.13 — Vue du site = photo de l’exploitant, non retouchée (11/10/2026)

| Demande | Fait |
|---|---|
| Garder la photo sans la retoucher | la capture fournie (sources/photo_site_exploitant.jpg) est affichée entière, sans découpe ni retouche, seulement tournée de 90° sens antihoraire (nord à gauche) ; la découpe de la bande de pelouse (v1.12) est abandonnée |
| Supprimer le fond vert foncé / le rectangle autour | plus de fond ni de cadre : la vue a exactement les proportions de la photo (1,316) |
| Bâtiments | 37 repères reportés sur la photo par recalage automatique sur l’orthophoto IGN (tools/recale_photo.py, contrôle par superposition) ; survol / clic vérifiés |
| Remarque | photo de 487 × 370 px : floue au zoom fort ; une capture plus grande peut la remplacer (même nom de fichier dans OCC-ENERGIE\sources, puis relancer recale_photo.py et la génération) |


## v1.14 — Vue aérienne : dossier OCC_DOSSIER_CLAUDE intégré (11/10/2026)

| Consigne du dossier | Fait |
|---|---|
| Image : PNG / WebP sans perte, pixels réels, transparence, cadrage | maître `assets/vue_aerienne/OCC_usine_IGN_2024_20cm.png` (SHA-256 be7da77c… conforme à metadata.json) ; pixels identiques à l’orthophoto déjà utilisée (écart RVB nul) ; tournée de 90° sens antihoraire à la demande de l’exploitant (transposition exacte, aucun pixel recalculé) ; transparence conservée hors contour |
| Chargement progressif des tuiles | pyramide Deep Zoom régénérée sur l’image tournée (tools/site_tiles.py : 34 tuiles 512 px, recouvrement 1 px, niveaux 6 à 12, WebP sans perte, 4,3 Mo) embarquée dans le fichier unique ; seules les tuiles visibles du niveau adapté au zoom sont chargées |
| Composant de navigation | visionneuse existante réutilisée (pas de doublon) : molette, pincement, glisser, vue complète ; bouton « 1:1 » (détail natif) ajouté |
| Repères et liaisons | couche vectorielle indépendante dans le même repère (coordonnées normalisées) : 37 bâtiments, liaisons 20 kV, nom au survol |
| Thème, fonctions, données | inchangés ; plus de fond vert foncé ni de cadre autour de la vue |
| Attribution | « Source : IGN — BD ORTHO® — prise de vue 2024 — Licence Ouverte Etalab 2.0 » sous la vue |
| Vérifications | 34/34 tuiles décodées aux dimensions attendues ; transparence (alpha 0 hors contour) ; zoom ±, molette, glisser (souris réelle), vue complète, 1:1 ; changement de niveau 10 → 11 → 12 et chargement des seules tuiles visibles ; alignement des 37 bâtiments contrôlé sur l’image maître tournée ; écran tactile 375 px (mode mobile) : pas de débordement, toucher d’un bâtiment → fiche ; non-régression : toutes les vues, 0 erreur, 44/44 ordres |


## v1.15 — Intégration de l’audit « Ajouts et corrections proposés » (11/10/2026)

Principe : seuls les points pertinents ont été repris ; chaque relevé a été **relu sur la photo ou le plan cité** avant saisie (module `tools/audit_2026_10_11.py`). Aucune séquence de manœuvre nouvelle n’a été déduite de l’audit.

| Point de l’audit | Fait |
|---|---|
| 1. Choisir un transformateur ou une cellule | la recherche du Dépannage accepte tableaux, départs, machines, transformateurs, cellules, couplages ; repère exact en premier ; plusieurs correspondances → « choisissez le bon » ; le diagnostic documentaire demande lequel au lieu de prendre le premier, et « autres correspondances » change réellement l’équipement (`#/depannage/<id>`) |
| 2. Un seul chemin | onglet renommé « Dépannage » ; sur chaque équipement : « Où il se trouve », « Ce qu’il alimente », « Fiche détaillée » |
| 3. Partir du symptôme | nouveaux symptômes : défaut d’isolement, alarme température transformateur, cellule HTA ouverte, commande impossible ; « tableau entièrement coupé » présente la cause amont comme une hypothèse et commence par lire l’état des arrivées (déclenchées = défaut BT) |
| 4. Une cellule ≠ tout le tableau HTA | fiche « cellule ouverte ou déclenchée » : transformateur, demi-TGBT concerné, lien vers la fiche couplage ; « tout le tableau coupé » reste une option séparée |
| 5. Validité avant les étapes | bandeau de statut en tête (contrôle / projet non validé / validée / validation caduque) avec référence, empreinte, version des données ; validation propre à l’équipement (S1:<départ>) ET à la version (empreinte) ; section « procédures validées » renommée |
| 7. Isolement par localisateur et canal | tables voie → départ : TGBT 3 (CX7810_C p53-54, 24 voies, texte du plan) et TGBT 9 (photo p22, cases illisibles laissées « ? ») ; seuils du TGBT 1 limités au TGBT 1 |
| 8. Observation ≠ simulation | bandeau « simulation en cours » sur toutes les vues avec heure et retour à la normale ; fiches et fiche détaillée calculées sur la configuration normale ; « tester dans le simulateur » sur une copie, arrêt au premier refus |
| 9-10. TGBT 9 | TS17A eau de refroidissement A2-18 et condensateurs JdB A A2-36 (plaques p19) rapprochés des lignes du classeur ; réserve 800 A B3-18 + étiquette « Groupe froid 7H216 » (non confirmé) ; Gorge Four 2 : A3-72N / A3-72S + commutateur N/S (relevé, aucune liaison ajoutée) ; contrôleurs Vigilohm XML3xx (écart I-TGBT9-IMD) |
| 11. TGBT 7 | STEP TS16 A3-18, compresseur 7K122 A2-1? (chiffre retouché), auxiliaire GE B2-23, Forming Nord / laveur 6 B2-33 ; 7K123 / centrale 55 et plaque « compresseur air B2 18 » en relevés à identifier ; TR 7A : relais T935 (ventilation et déclenchement) |
| 13. Ventilation des transformateurs | TR 2A Q2-51D 10 A (case 2-51) et TR 2B Q6-51D 16 A (6-51) — plan TGBT 2 2024 ; TR 1B Q7-33D 10 A (7-33) — plan TGBT 1B 2014 (probable) ; affichés sur la fiche du transformateur et dans la fiche « alarme température » |
| 19. Gradathyr | plaque « ZONE N°3 - GORGE » lue (p4) |
| 22. TS 17 | coffrets « ALIM DEPUIS TS17B Q34 — 7PM41 » et « Q36 — 7PM06 » en relevés ; doublons du classeur conservés (identité à vérifier) |
| 24. Onduleur 2 | QF1 / QF2 repérés ; plaque « Galaxy PW 1?0 kVA » (120 probable) : écart I-OND2-KVA |
| 26-27. Plaques | HVAC F2 case 3-63 (ancienne valeur 3-40 notée) ; SAP TGBT 1 98922+101152 ; SAP TGBT 2 43930+42931 |
| 31. Verrouillage TGBT 3 | trois champs séparés : règle d’exploitation, verrouillage physique (clés Ronis dessinées p6 / « aucun verrouillage » p5), alarme (p19-21) ; écart I-TGBT3-LOCK ; le simulateur applique la règle d’exploitation |
| 32. Transformateurs secs | TR 3A / 3B : Trihal, sondes et relais de température (CX7810_C p27 / p43) ; écart I-TR3-COOL avec le DGPT2 de l’unifilaire |
| 34. Plaque Varivolt | 901 kVA monophasé, 20 kV ±10 %, 50-350 V, OFAF, Ucc 6,2 % : document ajouté, unité non affectée (écart I-VARIVOLT-PLATE) |
| 36. Liens photo | anciens noms corrigés (Tgbt n1 → Tgbt 1.pdf, Tgbt n3 → Tgbt 3 (2).pdf…) ; noms accentués retrouvés dans leur forme exacte ; lien relatif « ../Plan électrique/ » + réglage par poste dans le Registre |
| 37. Historique | statut explicite actif / résolu des écarts ; version des données 1.15 du 11/10/2026 |

Non repris (à relever avant saisie, voir 4_PHOTOS_A_REPRENDRE.md) : façades TS 7 / TS 12 / TS 17A, pompes 7PM65 / 7PM03, Ventilation Four, Varivolt (zones, alarmes), Gorge (zones), Bronzini, relais HTA T60, étiquettes arc, table TGBT 4. Points 38-42 : documents à fournir (liste dans le Registre).

Vérifications : 2 686 fiches générées sans erreur (dont 98 « isolement », 46 « cellule », 23 « température ») ; 44/44 fiches couplage / retour acceptées par le simulateur ; test d’arrêt au premier refus ; état simulé inchangé après les tests ; toutes les vues, toutes les fiches d’appareil et d’écart : 0 erreur ; recherche « TR 6A », « cellule TR 6A », « 7K121 » contrôlée.

Complément : TS8 retrouvé dans la conversation Documentation TS8 (12 photos, ZIP original conservé dans sources/Ts8.zip). Premier coffret Ensimage identifié par l’utilisateur comme coffret agitateur : vue partielle intégrée sans affectation arbitraire des cuves.
