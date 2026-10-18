# OCC Énergie — rapprochement documentaire du 17 octobre 2026

Objet : fiabiliser l'index historique, la réception des photos TS1/TS8 et la correspondance des façades **sans créer de liaison électrique**.

## Contrôles réalisés
- 36 positions de `Distribution électrique 2024.xlsx` (INDEX lignes 5–40) croisées avec `Liste Etiquettes` : 35 positions retrouvées à la même case (dont une discordance d'identité), une position sans étiquette à la même case.
- INDEX ligne 23 : TGBT2 / TS2B case **6-18** ; liste d'étiquettes ligne 38 : TS2B case **6-28**. Statut : contradiction, ne pas décider du raccordement.
- INDEX lignes 30 et 38 : TS24A cases **2-10** et **7-10** ; étiquettes lignes 91 et 109 : **TS24A 2-10 / TS24B 7-10**. Ne pas fusionner les deux départs.
- TS42 **4-28** et TS43 **5-28** concordent dans ces deux sources pour les repères/cases ; l'incertitude de côté du TGBT et d'alias SAP reste distincte.
- TS2A : INDEX côté B, 2-36 ; modèle consolidé côté A (à qualifier).
- TS12 6-36 : ancien INDEX « TS12 », modèle plus récent « réserve » (à qualifier).
- Référence 7H214 : ancien INDEX TGBT1A 1-53 ; schéma TGBT3B 6+28 (origine actuelle à établir).

## Photothèque d'origine
- Archives `Ts8.zip` : 12 JPEG **IMG_3966 à IMG_3977**, dont 11 classés à tort TS1 dans l'ancien manifeste.
- Archive `Ts1.zip` : 15 HEIC **IMG_3978 à IMG_3992**, classés à tort TS8 dans l'ancien manifeste.
- Une copie corrigée de la photothèque (267 images) a été produite hors dépôt : conservation octet pour octet des 266 JPEG, reclassement des 26 vues et restauration d'IMG_3966.jpeg depuis l'archive TS8.
- Les deux HTML **historiques** avec module photographique ont été corrigés hors dépôt. Ils ne doivent pas remplacer `OCC_ENERGIE.html` reconstruit depuis les sources de la branche d'intégration. Les images binaires réparées restent à importer séparément ; ce document ne prétend pas les avoir poussées dans Git.

## Façades
L'ancien `OCC_ENERGIE_COMPLET_PHOTOS_15_10_2026.html` contient trois élévations SVG explicites : TGBT2 (6 modules), TGBT3 (6), TGBT4 (7), non cotées et simplifiées. Leur présence ne certifie pas la position de chaque protection. Il faut comparer les élévations de la **branche courante** avec les originaux, travée, arrivée, couplage et case par case.

## Suite et sécurité
1. Conserver `sources/referentiel_excel_2024.json` comme archive et documenter les écarts, pas comme schéma de câblage.
2. Intégrer la correction TS1/TS8 dans la chaîne de photo-sources, vérifier chaque binaire, régénérer les 4 HTML par `tools/rebuild.py`.
3. Revoir les 21 départs sans chaîne amont complète et les 33 écarts documentaires déjà recensés, avec preuves identifiées.
4. Tests locaux et GitHub Actions sur le dernier commit avant toute fusion. Le blocage des runners de la PR #16 n'est pas résolu par ce travail.
5. Aucune manœuvre, consigne de consignation, fermeture de couplage ou position de disjoncteur ne peut être déduite de ces rapprochements.

Sources : `Distribution électrique 2024.xlsx` (INDEX et étiquettes) ; `arborescence sap distribtuion elec.docx` ; archives Ts1.zip, Ts8.zip ; `docs/14_RAPPROCHEMENT_INDEX_EXCEL_2024.md`, `docs/16_REGISTRE_SOURCES_VERIFIEES_20261016.md`, `docs/17_REFERENTIEL_SAP_20261016.md`.
