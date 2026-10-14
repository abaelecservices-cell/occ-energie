# OCC Énergie — contrôle documentaire autonome

L'application conserve le repère du départ depuis l'unifilaire jusqu'à la façade.
Depuis une façade ciblée, le bandeau de navigation permet maintenant de revenir au
**schéma électrique amont** sans ressaisie. Le contexte est conservé également
lorsqu'on change d'onglet entre façade, départs, alimentation et photos.

## Inventaire des éléments à relever

Le workflow GitHub Actions **OCC Energie - Audit localisation et facades**
produit un artefact nommé **occ-energie-departs-a-completer**, contenant :

- DEPARTS_A_COMPLETER.csv : registre par départ (Excel FR : UTF-8, séparateur ;).
- SYNTHESE.md : chiffres de complétude documentaire et limites.

Ce rapport est régénéré à chaque modification de la branche contrôlée ou de
main. Les informations sont issues exclusivement du modèle build/data.json.
Un chemin amont calculé n'est pas une mesure de tension. Un plan ou une façade
n'est renseigné que si l'identifiant du départ/tableau figure explicitement
dans les objets de données. Le rapport signale les manques et ne **corrige jamais
automatiquement** les localisations, façades, sources ou liaisons.

## Protocole de validation terrain

Pour chaque ligne à compléter : relever l'étiquette du départ, son tableau, la
case, la colonne, la salle, le bâtiment, et la référence/photo source. Contrôler
le trajet de l'alimentation par les schémas et par les professionnels habilités,
puis qualifier séparément l'indice documentaire, l'observation terrain et sa
date. Les contradictions existantes (dont TR1A/TR2A, les dénominations de
sous-stations et les départs TS9/TS17) restent **à confirmer**.

Aucune fonctionnalité ici ne constitue une procédure de consignation ou un
constat des positions réelles de disjoncteurs.
