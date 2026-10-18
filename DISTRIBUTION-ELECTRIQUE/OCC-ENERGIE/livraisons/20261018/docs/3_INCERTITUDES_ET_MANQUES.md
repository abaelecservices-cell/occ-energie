# Informations incertaines ou manquantes

Généré depuis le modèle de données de l’application OCC ÉNERGIE. Chaque point est consultable dans l’onglet **Registre**.

## Incohérences documentaires

### [HAUTE] Origine du TS 17 / TS 9 : TGBT 9 ou TR 2B ?

Onglet « TR 9A & 9B » : TS 17A et TS 17B sur TGBT 9A / 9B. Mais la liste TS 17A contient « Arrivée 2A Normale » (C16) et les étiquettes arc du TS 9 indiquent « TABLEAU TR2B TS17B TS9 ». Hypothèse : étiquettes antérieures au « nouveau TGBT 9 ». À vérifier sur site. Nouvel élément : plaque « TS17A — EAU DE REFROIDISSEMENT — CASE A2-18 » sur le TGBT 9 (Tgbt 9.pdf p19), cohérente avec le classeur (TS 17A sur TGBT 9A).

Documents : Copie de Distribution.xlsm; Ts9.pdf p5, p7

### [HAUTE] Numérotation des sous-stations différente selon les documents

Plan d’implantation (exploitant) : Sous-station 2 = TGBT 1 à 6 + tableau 20 kV CNR/EDF ; Sous-station 1 = TGBT 9, TGBT 7, boosting, 6 kV. Unifilaire : « S/STATION 1 - 20KV » = tableau des TR 1 à 6, « S/STATION 2 - 20KV » = tableau des TR 7/9/boosting/6 kV. Étiquettes TGBT 4 « SST 1 » et rapport Schneider TGBT 1 « Sous station N°1 » ; plan Schneider TGBT 3 « Sous-station 2 » ; classeur onglet TR 7 « Sous/station n°2 ». L’application utilise la numérotation du plan d’implantation et rappelle l’appellation de l’unifilaire dans chaque fiche. À harmoniser (risque d’erreur lors d’une consignation).

Documents : PLAN IMPLANTATION 2.pptx; schema unifilaire 20 KV derniere version.pdf; Copie de Distribution.xlsm; p1.zip › 10_TGBT N°1 › OnSite_TechRpt_WO-12101777.pdf; p1 - Copie.zip › 12_TGBT N°3 › CX7810_C TQC.PDF

### [HAUTE] TGBT 3 : clés Ronis dessinées mais « aucun verrouillage » écrit

Le même dossier Schneider (CX7810_C, 12/2024) dessine des clés Ronis de choix de source (p6) et précise en p5 qu’il n’y a aucun verrouillage entre les arrivées et le couplage, la permutation étant à la charge de l’exploitant. Une alarme « arrivées en parallèle » est câblée (p19-21). L’application applique la règle d’exploitation (jamais 3 appareils fermés) sans affirmer qu’un verrouillage physique existe. À trancher sur place (serrures présentes ? clés ?).

Documents : p1 - Copie.zip › 12_TGBT N°3 › CX7810_C TQC.PDF

### [MOYENNE] Repères « VERS TGBT » inversés sur l’unifilaire (TR 1A / TR 2A)

L’unifilaire 20 kV (R112529 rév. H) porte sous la cellule « TR 1A » la mention « VERS TGBT 2 » et sous « TR 2A » « VERS TGBT 1 ». Règle donnée par l’exploitant : chaque TGBT n est alimenté par les transformateurs TR nA et TR nB (cohérent avec l’Excel et le plan Schneider TGBT 2 « ARRIVÉE TRANSFO TR2A »). Le modèle applique TR 1A → TGBT 1A et TR 2A → TGBT 2A. Reste à vérifier que les cellules HTA repérées « TR 1A » / « TR 2A » sur le tableau 20 kV alimentent bien ces transformateurs (étiquettes de cellule). Lecture détaillée : le disjoncteur BT dessiné sous TR 1A est un NW32H1 Micrologic 5.0P (clé T1b EL42462) — c’est le modèle de l’arrivée du TGBT 1A (plan Schneider TGBT1A, case 2-28), alors que l’arrivée TR2A du TGBT 2 est un NW40H1. Avec l’étiquette « PROVIENT DE TR 1A » photographiée sur le TGBT 1, trois éléments indiquent TR 1A → TGBT 1 : les mentions « VERS TGBT 2 / VERS TGBT 1 » de l’unifilaire sont très probablement inversées. — Photos du tableau 20 kV (Sous-station 2) : les plaques gravées donnent, côté A, « TRANSFORMATEUR 2A » puis « TRANSFORMATEUR 1A » contre l’arrivée secours EDF, symétriquement au côté B (arrivée CNR, 1B, 2B…). L’unifilaire place TR 1A puis TR 2A : nouvel indice que l’unifilaire inverse 1A et 2A. À confirmer par le suivi des câbles.

Documents : schema unifilaire 20 KV derniere version.pdf; Copie de Distribution.xlsm; p1.zip › 11_TGBT N°2 › plan mise a jour TGBT N°2 (Bronzini).pdf; Tableau 20kv edf cnr .pdf p6, p9

### [MOYENNE] TGBT 3 absent du classeur Excel

Le classeur ne contient aucun onglet « TR 3A & 3B ». Les départs du TGBT 3 proviennent uniquement du dossier Schneider CX7810 (liste des consommateurs).

Documents : Copie de Distribution.xlsm; p1 - Copie.zip › 12_TGBT N°3 › CX7810_C TQC.PDF

### [MOYENNE] FRIGO 7H214 : TGBT 1A ou TGBT 3B ?

Excel « TR 1A & 1B » H6 : « Frigo 7H214 » sur TGBT 1A. Plan Schneider TGBT 3 : « FRIGO 7H214 » case 6+28 (TGBT 3B). Probable transfert lors de la création du TGBT 3 — à vérifier.

Documents : Copie de Distribution.xlsm; p1 - Copie.zip › 12_TGBT N°3 › CX7810_C TQC.PDF

### [MOYENNE] Plan TGBT 1B : « ARRIVÉE TR2B »

Le plan Schneider TH11A-TGBT1B (face avant unifilaire et liste colonne 5) indique « ARRIVÉE TRANSFO TR2B » en case 5-28, alors que l’étiquette sur le tableau porte « PROVIENT DE TR 1B — ARRIVÉE TGBT 1B — CASE 5-28 ». Le modèle suit l’étiquette (règle TR nA / TR nB).

Documents : TH11A-TGBT1B.pdf; Tgbt 1.pdf p6

### [MOYENNE] Groupe électrogène n°1 : deux tableaux secourus

Les photos montrent une « ARRIVÉE GROUPE ÉLECTROGÈNE N°1 » sur le TS 7 (Four 1) et une « ARRIVÉE SECOURS GROUPE 1 » sur le TS 9 (chaufferie). Le simulateur interdit de mettre le groupe en parallèle avec le réseau ; la logique réelle de permutation (automatique / manuelle) est à fournir.

Documents : Ts 7.pdf p8; Ts9.pdf p1

### [MOYENNE] By-pass total de l’onduleur 2 : TGBT 5A ou TGBT 6 ?

La plaque de l’armoire « Alimentation ondulée onduleur 2 » indique « PROVIENT DE TGBT 5A — BY-PASS TOTAL ONDULEUR 2 » (cohérent avec le classeur, TGBT 5A H7). Mais le TGBT 6 porte aussi une étiquette « ONDULEUR 2 - BY PASS — CASE 2A-12 ». Le modèle suit la plaque de l’armoire ondulée.

Documents : Alimentation onduleur 2.pdf p2; Tgbt 6.pdf p1; Copie de Distribution.xlsm

### [MOYENNE] Codes de clés identiques sur des appareils différents

Code EL13131 dessiné à la fois sur la cellule TR 2A (clé 02A) et sur la cellule TR 3B (clé 03, boîte T6g « 03 = EL13131 »). Code EL53511 dessiné à la fois pour S3 (TR 3B, « S3 = EL53511 ») et pour X1 (cellule TR 9A). Deux clés de même code ouvrent les mêmes serrures : à vérifier sur les serrures réelles (risque pour la consignation).

Documents : schema unifilaire 20 KV derniere version.pdf

### [MOYENNE] Cellules non renseignées sur l’unifilaire

Repères « xx / Sxxxx / ELxxxx » et réglages non renseignés pour : TR Hydrogène, AEF1-TRZ1, AEF1-TRZ2, AEF2-TR1, AEF2-TR2, TR 9B (tableau 20 kV TR 7/9) et les arrivées 6 kV AEF2-A1 / AEF2-A2. Les réglages réels sont à relever sur les relais.

Documents : schema unifilaire 20 KV derniere version.pdf

### [MOYENNE] Poste de livraison CNR / EDF : aucune photo

Le fichier « Départ 20kv edf cnr.pdf », d’abord rattaché au poste de livraison, montre le tableau 20 kV TR 1 à 6 de la Sous-station 2. La façade du poste de livraison reste dessinée d’après l’unifilaire seul.

Documents : Départ 20kv edf cnr.pdf

### [BASSE] TR 3A / 3B : 2000 kVA confirmé par les plaques ; type de surveillance à vérifier

Les documents France Transfo du dossier TGBT 3 (n° 1466597 et 1466588, essais de janvier 2025) donnent 2000 kVA, Trihal sec enrobé, surveillance par sondes de température. L’unifilaire indique « DGPT2 » (protection des transformateurs immergés) pour TR 3B : si TR 3B est l’un de ces Trihal, la protection est par sondes, pas par DGPT2. Les plans Schneider TGBT 2 et 3 indiquent toujours « 2000 kVA (2500 kVA) » avec des arrivées 3520 A (réserve de puissance). Plaques de TR 2A / 2B non fournies.

Documents : schema unifilaire 20 KV derniere version.pdf; p1.zip › 11_TGBT N°2 › plan mise a jour TGBT N°2 (Bronzini).pdf; p1 - Copie.zip › 12_TGBT N°3 › CX7810_C TQC.PDF; p1 - Copie.zip › 12_TGBT N°3 › TRANSFORMATEUR › TR2 / TR3 (France Transfo : plan d’ensemble, procès-verbaux d’essais n° 1466597 et 1466588 du 28-29/01/2025, schémas de câblage)

### [BASSE] Implantation physique des TGBT (résolue par le plan)

Localisations reprises du plan d’implantation : TGBT 1 à 6, TS 2, tableau 20 kV arrivée CNR/EDF, condensateurs et onduleurs en Sous-station 2 ; TGBT 9, « Tr7 b » (TGBT 7), tableau 20 kV, gradathyr, varivolt, boosting en Sous-station 1 côté gauche ; tableau 6 kV, Gorge et Spang côté droit ; TS 9 / TS 17 en chaufferie ; TS 16 à la STEP.

Documents : —

### [BASSE] Alimentation du TS12

Trois sources documentaires : Excel L7 (TGBT 2B, « TS12 Emballage, situé aux travaux neufs ») ; plan TGBT 2 case 6-36 « TS12 ROVING » ; plan TGBT 3 cases 2+18 « TS12A » et 5+18 « TS12B ». Le modèle relie le TS12 aux départs du TGBT 3 ; le départ TGBT 2 6-36 est conservé sans liaison active. Photos TGBT 2 : la case 6-36 porte aujourd’hui « RÉSERVE » (ancienne étiquette retirée, départ condamné) : le TS 12 n’est plus alimenté par le TGBT 2. Alimentation actuelle : TGBT 3 (TS12A case 2+18, TS12B case 5+18).

Documents : Copie de Distribution.xlsm; p1.zip › 11_TGBT N°2 › plan mise a jour TGBT N°2 (Bronzini).pdf; p1 - Copie.zip › 12_TGBT N°3 › CX7810_C TQC.PDF

### [BASSE] TS42 / TS43 (filières 4A12-4A19)

Étiquette TGBT 4 case 5-28 : « TS43 FILIÈRE 4A12 à 4A19 » ; Excel « TR 4A & 4B » L12 : « TS 42 Filières C4 4A12 à 4A19 ».

Documents : Copie de Distribution.xlsm; Tgbt 4.pdf p9

### [BASSE] Coffret agitateur sans parent

Bloc « Coffret agitateur » (C50-C54, onglet TR 1A & 1B) : aucun départ amont identifié.

Documents : Copie de Distribution.xlsm

### [BASSE] Bloc TS 24B dupliqué

Le bloc « TS 24 B (Four 2) » apparaît à l’identique dans les onglets TR 4A & 4B (O9) et TR 6A & 6B (O7). Rattaché au TGBT 4B (L9) ; la copie de l’onglet TR 6 est ignorée.

Documents : Copie de Distribution.xlsm

### [BASSE] Étiquette arc TS 9 col. 3

Relevé photo (Ts9.pdf p5) : 400 V ; Icc 1,62 kA ; 0,19 cal/cm² ; limite d’approche 14,91 cm. La maquette antérieure mentionnait 1,92 kA et 0,15 cal/cm² : relire la plaque.

Documents : Ts9.pdf p5

### [BASSE] Photos des tableaux 20 kV (tri effectué)

Tri fait sur les photos : « Tableau 20kv edf cnr » et « Départ 20kv edf cnr » = tableau 20 kV TR 1 à 6 (Sous-station 2) ; « Tableau 20kv SS1 » (3 séries) = tableau 20 kV TR 7 / 9 / boosting, sauf « Tableau 20kv     SS1 » p1-p11 = TGBT 8 (boosting). Aucune photo du poste de livraison.

Documents : —

### [BASSE] Origine des TS 46A / TS 46B retrouvée

Photos TGBT 1 : « TS 46A — CASE 1-53 » (demi-JdB A) et « TS 46B — CASE 6-53 » (demi-JdB B). Le plan TGBT1A 2010 indiquait en 1-53 « départ gr. froid 7H211 » (repris dans le classeur en « Frigo 7H214 », aujourd’hui sur le TGBT 3).

Documents : Tgbt 1.pdf p1, p9

### [BASSE] Compresseurs 7K121 / 7K122 sur TGBT 7

Classeur « TR 7A & 7B » : compresseurs 7K121 (H6) et 7K122 (H9) sur le TGBT 7A. Photos : « AE 7K122 » en colonne A2 (demi-JdB A) mais « AE 7K121 » en colonne B1 (demi-JdB B), et l’étiquette arc de la colonne A2 mentionne « TABLEAU TR7B 7K122 ». Rattachement à vérifier.

Documents : Tr7b .pdf p3, p5, p9; Copie de Distribution.xlsm

### [BASSE] Boosting : réglages identiques avec des rapports de TC différents

Les deux cellules BOOSTING 3200 kVA ont le même réglage I> 110 A SIT, mais le TC retenu est 100/5 A pour S3 (Sch. 3182584) et 50/5 A pour S12 (Sch. 3182750) : vérifier le paramétrage réel des relais S2036.

Documents : schema unifilaire 20 KV derniere version.pdf

### [BASSE] Tableau 6 kV : ordre des groupes Spang

Photos : à droite de l’arrivée transfo boosting B, les plaques donnent L6, L5 puis L4 en bout de tableau ; l’unifilaire dessine L4 contre l’arrivée et L6 en bout. Plaques des groupes côté A illisibles (positions L1 à L3 estimées). Correspondance des arrivées A / B avec les cellules 20 kV « boosting » à vérifier sur place.

Documents : Tableau 6kv.pdf p1-p13; schema unifilaire 20 KV derniere version.pdf

### [BASSE] TR 3B : DGPT2 (unifilaire) ou sec Trihal (dossier 2025) ?

L’unifilaire R112529 rév. H indique une protection DGPT2 (transformateur immergé) pour le TR 3B. Le dossier du TGBT 3 (12/2024) et le dossier constructeur 2025 décrivent des transformateurs secs Trihal avec sondes et relais de température (alarme, déclenchement, ventilateurs). Le transformateur a probablement été remplacé : la fiche suit le dossier récent. Seuils d’un dessin ≠ réglages actuels.

Documents : schema unifilaire 20 KV derniere version.pdf; p1 - Copie.zip › 12_TGBT N°3 › CX7810_C TQC.PDF

### [BASSE] TGBT 9 : contrôleur d’isolement à identifier

Les contrôleurs photographiés (Tgbt 9.pdf p22) sont des Vigilohm XML3xx (16 voies), pas des IM400. Référence exacte et notice à associer avant d’utiliser les seuils. Les seuils du TGBT 1 (rapport Schneider 2024) ne s’appliquent pas au TGBT 9.

Documents : Tgbt 9.pdf p22

### [BASSE] Onduleur 2 : 100 ou 120 kVA ?

La plaque QF1 de l’armoire ondulée se lit « GALAXY PW 120 KVA » (premier chiffre peu net, photo p2). L’application indiquait 100 kVA. Relever la plaque de l’onduleur.

Documents : Alimentation onduleur 2.pdf p2

### [BASSE] Varivolt : 901 kVA monophasé (plaque) / 900 kVA (unifilaire)

La plaque constructeur (série 26013-1) indique 901 kVA monophasé, secondaire variable 50-350 V. L’unifilaire porte 900 kVA / 350 V pour AEF1-TRZ1 et TRZ2. L’unité à laquelle appartient la plaque n’est pas établie (les repères 26013-3 / 26013-4 des armoires de commande ne suffisent pas) : valeurs de l’unifilaire conservées.

Documents : 26013 nameplate.pdf; schema unifilaire 20 KV derniere version.pdf

## Éléments marqués « à vérifier » ou « non documenté »

| Élément | Tableau | Confiance | Motif |
|---|---|---|---|
| TR Hydrogène — utilisation aval non documentée |  | Non documenté | schema unifilaire 20 KV derniere version.pdf |
| Couplage TGBT 8 (non documenté) | TGBT 8 | Non documenté | aucun ; façade : Tableau 20kv     SS1.pdf p1-p11 |
| Alim platine vigilhom | TGBT 2 | À vérifier | Départ du classeur non retrouvé dans la liste des consommateurs Schneider (case inconnue). |
| Boosting Four 1 | TGBT 4 | À vérifier | Présent dans le classeur, non identifié sur la façade photographiée. |
| Disj auxilliaires | TGBT 4 | À vérifier | Présent dans le classeur, non identifié sur la façade photographiée. |
| Arrivée secours n°1 | TS 17 — Chaufferie | À vérifier | Ligne du classeur décrivant une arrivée du TS 17A (et non un départ). Origine non documentée. |
| Arrivée 2A Normale | TS 17 — Chaufferie | À vérifier | Ligne du classeur décrivant une arrivée du TS 17A (et non un départ). Origine non documentée. |
| Tiroir n°2 col. 4 — étiquette illisible (« … pompe … fuel domestique » ?) | TS 9 — Chaufferie | À vérifier | Demi-jeu de barres déduit de la position (colonne) — non documenté. |
| (étiquette effacée, 2B haut) | TGBT 6 | À vérifier | Tgbt 6.pdf p1, p2, p4, p8, p10 (étiquette) |
| Départ B2 haut (étiquette non lisible) | TGBT 9 | À vérifier | Tgbt 9.pdf p16, p18, p20, p23 (étiquette) |
| Départ B2 bas (étiquette non lisible) | TGBT 9 | À vérifier | Tgbt 9.pdf p16, p18, p20, p23 (étiquette) |
| RÉSERVE 800 A — CASE B3-18 (étiquette « Groupe froid 7H216 ») | TGBT 9 | À vérifier | Plaque gravée « RÉSERVE 800A — CASE B3-18 » et étiquette imprimée ajoutée « Groupe froid 7H216 » (Tgbt 9.pdf p3). Les deux coexistent : alimentation du groupe froid NON confirmée. |
| DÉPART (étiquette non lisible) | Alimentation ondulée — Onduleur 2 | À vérifier | Alimentation onduleur 2.pdf p2 (étiquette) |
| DÉPART NSX (étiquette non lisible) | Bâtiment Bronzini | À vérifier | Bronzini .pdf p1-p3 (étiquette) |
| DÉPART NSX — cadenassé (étiquette non lisible) | Bâtiment Bronzini | À vérifier | Bronzini .pdf p1-p3 (étiquette) |
| DISJONCTEUR NS à Micrologic (étiquette non lisible) | Bâtiment Bronzini | À vérifier | Bronzini .pdf p1-p3 (étiquette) |

## Couplages BT sans règle d’interverrouillage documentée

- TGBT 8 : couplage non documenté

## Documents attendus

1. PowerPoint d’implantation des sous-stations 1 et 2 (ordre des armoires, allées, vis-à-vis, sas SS1).
2. Captures Google Earth (vue aérienne et positions des tableaux secondaires).
3. Cotes des salles et des armoires (télémètre).
4. Procédures de changement de source et de consignation validées (TGBT 1, 2, 4 à 9, TS 9, couplages HTA V500 / SS2 / 6 kV).
5. Transcription du document « Verrouillage DJ TR3B » (scanné).
6. Confirmation de l’attribution TR 1A / TR 2A ↔ TGBT 1 / TGBT 2.
7. Confirmation de l’alimentation du TS 12 (TGBT 2 et/ou TGBT 3) et du TS 17 / TS 9 (TGBT 9 ou TR 2B).
8. Plaques signalétiques des transformateurs TR2/TR3 (2000 ou 2500 kVA).

### [MOYENNE] TS16 : annotation TGBT 6 / TR7A à clarifier

IMG_4149.heic montre le repère TS16 et une note manuscrite « Départ TGBT n°6 / TR7A ». Cette annotation ne suffit pas à établir le raccordement amont. Les liaisons du modèle restent inchangées.

Documents : Ts 16.zip / IMG_4149.heic
