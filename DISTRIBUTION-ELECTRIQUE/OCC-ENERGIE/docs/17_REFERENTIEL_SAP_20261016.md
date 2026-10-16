# OCC Énergie — rapprochement de l'arborescence SAP (16 octobre 2026)

**Source :** document fourni par l'exploitant `arborescence sap distribtuion elec.docx`, **7 pages de captures d'écran SAP**. Transcription documentaire ciblée, à confirmer par extraction SAP structurée si le référentiel devient maître. Cette pièce constitue une **nomenclature de maintenance / localisation fonctionnelle**, et non un schéma électrique, ni une preuve de connexion entre un TGBT et un TS. Ne jamais convertir une relation parent/enfant SAP en câble ou en arrivée confirmée.

## 1. Conséquence immédiate pour les relevés photographiques

**NE PAS redemander** les photographies générales déjà transmises (voir `16_REGISTRE_SOURCES_VERIFIEES_20261016.md`). Cette pièce SAP fournit surtout des **identifiants de recherche et des candidats de recoupement**.

Parmi les façades à rechercher dans les anciens documents puis à photographier **seulement si réellement absentes** :
- TS24 : **100586** (« Tableau Elec. F2 »)
- TS28 : **101488** (« Tableau Elec. Climat. F2 »)
- TS42 : **101490** (« Tableau Filières Canal 4 Ext »)
- TS43 : **101491** (« Tableau Filières Canal 4 Int »).

La source SAP ne contient pas le repère « TSO Labo analyste » dans la capture des tableaux secondaires : **absence de l'extrait affiché**, pas preuve d'absence de SAP.

## 2. Liste des 28 entrées SAP « Tableaux Secondaires (400V) », pages 4 et 5

| N° SAP | Libellé à l'écran SAP | Rattachement nominal pour rapprochement seulement |
|---:|---|---|
| 42947 | Ts02 Tableau Elec. Station | TS02 ; **ne pas assimiler automatiquement** à TS2 « Étuves » du modèle OCC |
| 42948 | Ts32 Tableau Elec. | TS32 — libellé fonctionnel non précisé |
| 43817 | Ts30 Tableau Heat Wheel | TS30 |
| 44102 | Ts18 Tableau Elec. clim Four 1 | TS18 |
| 44118 | Ts33 Tableau Filières Canal1 Ext | TS33 |
| 44119 | Ts34 Tableau Filières Canal1 Int | TS34 |
| 44120 | Ts35 Tableau Filières Canal3 Ext | TS35 |
| 44121 | Ts36 Tableau Filières Canal3 Int | TS36 |
| 44131 | Ts12A/B Tableau Elec. roving | TS12 A/B |
| 44284 | Ts01 Tableau Elec. Ensimage | TS1 |
| 44878 | Ts27 Tableau Elec. Généralités F2 | TS27 |
| 64628 | Ts31 Tableau Elec. Atelier Elec. | TS31 |
| 91885 | Ts37 Tableau Filières Canal2 Ext | TS37 |
| 91886 | Ts38 Tableau Filières Canal2 Int | TS38 |
| 98333 | Ts07 Tableau Elec. Four 1 | TS7 |
| 98950 | Ts16 Tableau Elec. Step | TS16 |
| 98951 | Ts08 Tableau Elec. Généralités F1 | TS8 — **écart de libellé** avec OCC « Groupe frigo (local frigo) » |
| 98952 | Ts09 Tableau Elec. Chaufferie | TS9 |
| 98953 | Ts17 Tableau Chaufferie (Refroidissement) | TS17 |
| 98954 | Ts15 Tableau Elec. Batch | TS15 |
| 100586 | Ts24 Tableau Elec. F2 | TS24 |
| 101488 | Ts28 Tableau Elec. Climat. F2 | TS28 |
| 101489 | Ts40 Tableau Elec. | TS40 — libellé fonctionnel non précisé |
| 101490 | Ts42 Tableau Filières Canal4 Ext | TS42 ; rapprocher de « filières 4A02 à 4A09 » sans affirmer l'équivalence |
| 101491 | Ts43 Tableau Filières Canal4 Int | TS43 ; rapprocher de « filières 4A12 à 4A19 » sans affirmer l'équivalence |
| 101492 | Ts10 Tableau Bureaux Administratifs | TS10 |
| 674405 | Ts46B Tableau Elec. Packman | TS46B |
| 674406 | Ts46A Tableau Elec. Packman | TS46A |

Les **13 repères SAP TS10, TS18, TS27, TS30, TS31, TS32, TS33, TS34, TS35, TS36, TS37, TS38, TS40** ne sont pas détaillés comme tableaux individuels dans `docs/5_AVANCEMENT.md` (branche d'intégration). Cela **ne prouve pas** qu'aucune information à leur sujet n'existe déjà ailleurs dans le modèle. Avant de demander des photos, chercher dans les exports, classeurs, documents et listes d'équipements.

## 3. Distribution / HTA, pages 1 à 3

| Regroupement SAP | Objets visibles | Précaution |
|---|---|---|
| Distribution 4 (`...00404`) | Cellules TR4A/TR4B 97717/97725 ; transformateurs 98925/99084 ; TGBT4A/4B 42934/42933 ; condensateurs 603828/603829 | Rapprocher les numéros d'équipement sans inférer un raccordement nouveau |
| Distribution 5 (`...00405`) | Cellules TR5A/TR5B 97718/97719 ; transformateurs 121059/42977 ; TGBT5A/5B 42978/42979 ; condensateurs 91887/91888 | Idem |
| Distribution 6 (`...00406`) | Cellules TR6A/TR6B 97720/97721 ; transformateurs 82031/82032 ; TGBT6A/6B 82034/82035 ; condensateurs 82041/82042 | Idem |
| Distribution 7 (`...00507`) | Cellules TR7A/TR7B 603830/603831 ; TR7A/TR7B 89770/89771 ; TGBT7A/7B 101117/101121 ; condensateurs 603832/603833 | Le parent SAP affiche « Sous-Station 2 », tandis que le plan d'implantation utilisé par OCC situe le TGBT7 dans la sous-station dite 1 ; **numérotations à distinguer** |
| Distribution 8 (`...00508`) | Cellules TR8A/TR8B 607059/607060 ; TR8A/TR8B 89772/89773 ; BOOSTING Four 1, zones 1 à 6 et Gorge | Le terme « Distribution 8 » SAP n'autorise pas à inventorier un TGBT8A/8B physique sans contrôle |
| Distribution 9 (`...00509`) | Cellules TR9A/TR9B 660788/660789 ; TR9A/TR9B 660790/660791 ; TGBT9A/9B 660792/660793 | Idem |
| Distribution 10 (`...00510`) | Cellules TR10A/TR10B 635220/635221 ; TR10A/TR10B 635222/635223 ; BOOSTING Four 2, Gorge et **SPANG 6 kV zones 2–6** | Ne pas inventer de TGBT10 ni de « zone 1 absente » sur base de l'extrait |
| Distribution 11 (`...00511`) | Cellules TR11A/TR11B 660808/660810 (aucun tableau aval visible sur la capture) | Ne pas conclure à une topologie manquante à partir de la section réduite / non développée |

## 4. Autres catégories à intégrer dans la recherche de l'application

- **Onduleurs (page 6)** : Four 1–4, étuves 7/8/9, incendie/accueil, décarbonatation, STEP, bureaux administratifs, onduleurs 1/2 sous-station, onduleurs 110 V 1/2, tours aéroréfrigérantes, 24 VDC poste de livraison. `Onduleur Étuvés 7,8,9` (SAP **75163**) **n'est pas nécessairement** le tableau électrique étuves 7/8/9.
- **Armoires éclairage (page 6)** : notamment `Armoire Eclairage Ensimage` (**44283**), Batch, Forming F1/F2, locaux TS12, labo central, etc. Ne pas assimiler automatiquement `Armoire Eclairage Ensimage` à `Éclairage Ensimage labo central 9M04` sans repère de départ.
- **Climatisation / extraction (page 7)** : ventilation des sous-stations, soufflage Boosting, transformateurs 5A/5B/6A/6B/7A/7B/8A/8B, etc. Ces identifiants SAP améliorent la recherche d'auxiliaires mais **ne certifient pas** leur alimentation amont.

## 5. Écarts à traiter avant de changer les liaisons de puissance

1. **TS02** : SAP « Station » vs OCC « Étuves ».
2. **TS08** : SAP « Généralités F1 » vs OCC « Groupe frigo / local frigo ».
3. **TS42 / TS43** : SAP « Filières Canal 4 Ext / Int » vs désignations OCC par positions 4A ; vérifier si désignations équivalentes.
4. **Numérotation des sous-stations** : SAP « Sous-Station 2 » avec Distribution 7–11 vs convention du plan d'implantation retenue par OCC. Conserver les deux noms et leurs provenances.
5. **Spang 6 kV** : la catégorie Distribution 10 contient des équipements repérés SPANG, sans démontrer l'ordre physique des cellules ni leur chaîne de puissance.

## 6. Actions de développement, sans nouvelle demande terrain à ce stade

1. Ajouter un **index de recherche SAP** `id_sap → libellé_sap → candidat_equipment_id_OCC → source (page) → statut de correspondance`. Séparer relations `confirmé`, `à rapprocher`, `contradictoire`.
2. Rapprocher chaque ligne SAP des noms existants et conserver les alias sans écraser les repères validés sur site.
3. Ajouter les TS secondaires candidats absents de `5_AVANCEMENT.md` à une file de qualification documentaire, **sans créer de nouvelles façades fictives ni de liaisons électriques**.
4. Ne demander ensuite **qu'une photo de repère, d'armoire ou de départ précise** après épuisement des archives déjà reçues, et expliquer à quel diagnostic elle servira.
5. Le document SAP ne renseigne ni les cases, ni les câbles, ni les états d'appareils, ni les manœuvres. L'application reste **consultative**, sans validation de consignation.

**État :** dossier de rapprochement documentaire ajouté ; **aucune liaison, façade ou ID du modèle actif n'est modifié par ce document**.
