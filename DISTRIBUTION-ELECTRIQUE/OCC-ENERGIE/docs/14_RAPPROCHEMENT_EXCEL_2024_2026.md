# Rapprochement du classeur « Distribution électrique 2024.xlsx » avec OCC Énergie — 15/10/2026

## Périmètre et sources

- **Source historique prioritaire pour ce contrôle** : `Distribution électrique 2024.xlsx`, transmis le 15/10/2026. Le classeur comprend 10 onglets : `Liste Etiquettes`, `Code couleur`, `TABLEAU 20 kV`, `TGBT N°1`, `TGBT N°2`, `TGBT N°4`, `TGBT N°5`, `TGBT N°6`, `Age equipement` et `INDEX`.
- **INDEX** : 36 lignes de départs, toutes marquées « Sous/station 1 » dans ce document : 13 pour TGBT 1, 10 pour TGBT 2, 13 pour TGBT 4 (lignes 5 à 40). Chaque ligne porte une localisation côté/colonne/case, parfois un TS et un lieu.
- **Age equipement** : 68 lignes d'appareils (lignes 2 à 69), années de mise en service parfois renseignées, aucune « dernière maintenance » exploitable visible dans ce registre.
- **Modèle actuel de l'application** : `build/excel.json` provient de **`Copie de Distribution.xlsm`**, non du fichier `Distribution électrique 2024.xlsx`; voir `README.md`, `build/excel.json`, `docs/5_AVANCEMENT.md` (503 départs indexés). Le classeur historique 2024 est un **complément**, pas un remplacement automatique des données courantes.
- **Autres sources dans le dépôt** : `docs/3_INCERTITUDES_ET_MANQUES.md`, photographies et plans techniques du répertoire `../Plan électrique/`. Les relevés terrain du 15/10/2026 peuvent arbitrer les écarts.

## Correspondances et écarts prioritaires

| Sujet | Constat dans le classeur 2024 | Constat dans le modèle/documentation OCC Énergie | Décision de rapprochement |
|---|---|---|---|
| Numérotation des sous-stations | `INDEX`, lignes 5–40 : TGBT 1, 2, 4 sous « Sous/station 1 ». | L'application utilise la nomenclature du plan d'implantation, TGBT 1–6 en « Sous-station 2 ». La divergence est **déjà documentée** dans `docs/3_INCERTITUDES_ET_MANQUES.md`. | **Ne pas déplacer les tableaux** sur la foi d'une appellation. Ajouter l'alias documentaire « SST 1 (archive/Schneider) » aux équipements concernés après validation des identifiants. |
| Départ 7H214 | `INDEX`, ligne 5 : TGBT 1A, colonne 1, case 53, « GROUPE 7 H214 » (LOCAL FRIGO). | `docs/3_INCERTITUDES_ET_MANQUES.md` mentionne « Frigo 7H214 » historique TGBT 1A, mais aussi sur un plan de TGBT 3B, et une étiquette actuelle « TS46A » en TGBT 1A case 1-53. | **Historique probablement dépassé** ; ne pas rétablir la liaison TGBT 1A → 7H214 sans confrontation photo, câbles et plans. |
| TS12 | `INDEX`, ligne 24 : TGBT 2B, colonne 6, case 36, TS12 (« TRAVAUX NEUF »). | `docs/3_INCERTITUDES_ET_MANQUES.md` : ancienne case 6-36 devenue « RÉSERVE » ; TS12 documenté alimenté par TGBT 3. | Classer TGBT 2B → TS12 comme **liaison historique**, et garder l'actuelle à vérifier sur site avant toute procédure. |
| TS8 | `INDEX`, ligne 28 : TGBT 4A, colonne 1, case 23, « TS8 » local frigo. | TS8 est inventorié dans `docs/5_AVANCEMENT.md` et documenté dans `docs/TS8_RELEVE_TERRAIN_2026-10-15.md`. | Rapprocher les repères TGBT4A / case1-23 et TS8 avec les photos ; ne pas confondre TS8 avec les deux armoires d'ensimage distinctes. |
| TS42 / TS43 | `INDEX`, lignes 34–35 : TGBT 4A case 4-28 → TS42 ; TGBT 4B case 5-28 → TS43. | TS42 et TS43 figurent dans l'inventaire ; une discordance TS42/TS43 existe dans l'ancienne source XLSM (`docs/3_INCERTITUDES_ET_MANQUES.md`). | La source 2024 renforce l'identification des repères ; la numérotation de départ doit être confirmée par étiquettes sur site. |
| TS24A / TS24B | `INDEX`, lignes 30 **et 38** : « TS24A » répété sur côtés A (2-10) et B (7-10) du TGBT4. | `docs/3_INCERTITUDES_ET_MANQUES.md` mentionne une duplication du bloc « TS24B » dans l'XLSM. | **Ne pas transformer la répétition en deux alimentations TS24A** ; vérifier si la seconde ligne est en réalité TS24B. |
| Années impossibles | `Age equipement`, lignes 65, 67 et 69 : **20023** pour « DJ HT 11A », « DJ HT 7B », « DJ BT 7B ». | Le modèle distingue les équipements TR11A / TR11B et des équipements TR7B. | Marquer **année invalide** ; ne pas convertir silencieusement en 2023. Les libellés 7B aux lignes 67/69 semblent également nécessiter un contrôle (possible 11B, non confirmé). |
| Couplages | `Age equipement` mentionne notamment « Couplage 1 », « Couplage 2 », « Couplage 5 », « Couplage 6 » avec des années. | `src/app.js` décrit une interdiction systématique de fermer simultanément les deux arrivées et le couplage comme « règle donnée par l'exploitant ». L'exploitant a corrigé cette attribution le 15/10/2026 : **pas de telle règle générale confirmée sur site** ; les demi-TGBT peuvent être couplés pour assurer la continuité pendant maintenance d'un transformateur. | **Corriger la documentation de l'hypothèse** ; distinguer fonction de couplage et permissifs/interverrouillages effectivement documentés. Ne jamais inférer que le parallélisme de deux transformateurs sous tension est autorisé : groupe vectoriel, rapport de tension, impédance, réglages et protections restent à vérifier. Toute logique de simulation ou procédure de manœuvre requiert revue technique. |

## Principes d'intégration

1. Conserver l'**original Excel 2024 intact**, avec colonnes et provenances précises (onglet, ligne, côté, colonne, case, désignation, lieu).
2. Utiliser l'XLSM et les photos actuelles pour la **configuration 2026**, et le XLSX 2024 pour les **repères historiques, localisations, années et écarts**.
3. Exposer explicitement le statut de chaque liaison : `confirmée 2026`, `documentée 2024 / historique`, `contradictoire`, `à vérifier`.
4. Éviter toute réaffectation automatique de sous-station, TS, transformateur ou couplage à partir d'un simple libellé ; conserver les alias documentaires.
5. Traiter en priorité les écarts à **impact de consignation ou de secours** : numérotation SS, TS12, 7H214, 24A/24B, logique de couplage.

**Statut du présent document** : premier croisement ciblé des onglets `INDEX` et `Age equipement` avec les données et rapports de l'application. **Il ne constitue ni un audit exhaustif de toutes les étiquettes de 2024, ni une validation de topologie ni une consigne de manœuvre.**
