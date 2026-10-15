# TS17A / TS17B — Tours de refroidissement (relevé du 15/10/2026)

## Sources
Deux archives transmises, `Ts17A .zip` et `Ts17b.zip`, contenant chacune les **mêmes 14 JPEG**, de IMG_4038 à IMG_4051. Identité binaire des 14 JPEG vérifiée par SHA-256. Les deux archives ne sont pas deux relevés indépendants. Les images ne sont pas importées dans ce dépôt.

Les photos représentent **des armoires en aval de TS17A / TS17B**, et **non des façades des tableaux TS17 eux-mêmes**. Conserver les façades documentaires TS17 existantes jusqu'à un relevé de ces tableaux.

## Identification des quatre armoires distinctes

| Armoire | Plaque / fonction | Origine inscrite sur façade | Photos |
| --- | --- | --- | --- |
| Puissance **A1** | TOUR 1 NORD / TOUR 1 SUD | **ALIMENTATION DEPUIS TS17B** | IMG_4038–4043 |
| Puissance **A2** | TOUR 2 NORD / TOUR 2 SUD | **ALIMENTATION DEPUIS TS17A** | IMG_4038–4045, IMG_4051 |
| Contrôle **C1** | TOURS REFROIDISSEMENT ; pupitre Schneider Electric **Magelis** | **ALIMENTATION DEPUIS TS09** | IMG_4039–4040, IMG_4046, IMG_4050 |
| Tours de refroidissement **SECOURS** | Commandes 1 Nord, 2 Nord, 1 Centre, 2 Centre, 1 Sud, 2 Sud | Plaque rouge **« S/S N°2 TR7A »** ; annotation manuscrite jaune **« Départ TGBT n°6 TR7A »** | IMG_4047–4049 |

A1 : deux commandes de tour, avec arrêt d'urgence, réarmement et sélecteur AUTO/MAIN ; mesure PowerLogic, repère jaune **68**. A2 : configuration analogue pour tour 2, mesure PowerLogic, repère **69**. C1 : supervision Magelis, voyant SOUS TENSION et sélecteur de régulation. Le secours comporte six positions visibles. Ces marquages ne démontrent ni l'état électrique instantané ni le schéma détaillé des contacts.

## Écart critique avec le classeur utilisé par l'application

Le classeur `TR 9A & 9B`, importé dans `build/excel.json`, indique :
- **TS17A C11 : « Tour de refroidissement n°1 »** ; la façade de puissance **A1** de la tour 1 porte au contraire **« depuis TS17B »**.
- **TS17B P21 : « Tour de refroidissement n°2 »** ; la façade de puissance **A2** de la tour 2 porte au contraire **« depuis TS17A »**.

**Inversion entre classeur et étiquettes de terrain : PRIORITÉ HAUTE.** Ne pas choisir arbitrairement l'une des sources et ne pas changer les liaisons du graphe avant le contrôle **départ amont → câble → arrivée A1/A2** avec schéma actualisé.

## Autres précautions
- **C1** : alimentée d'après la plaque par **TS09** ; rapprocher le départ de commande C1 actuellement documenté sur TS9. Ne pas rattacher C1 à TS17A ou TS17B par simple proximité physique.
- **Secours** : lire et vérifier les deux indications **TR7A** et **TGBT n°6**. Le graphe actuel décrit le TGBT6 par TR6A/TR6B ; **ne créer aucun chemin de secours spéculatif**. Vérifier le libellé de la plaque, le départ amont et d'éventuelles modifications historiques.
- Le graphe logiciel décrit actuellement les deux TS17 sur **TGBT9**, avec l'incertitude préexistante `I-TS17` (ancienne mention TR2B). Le présent relevé n'apporte pas la preuve permettant de clore cette incertitude.
- L'association des commandes 1/2 Nord/Sud aux **moteurs et protections** ne peut pas être déduite de la seule façade.

## Relevés nécessaires
1. Photos des **départs TS17A C11 et TS17B P21** et repères de câbles/arrivées **A1, A2**, plus schémas de leurs départs.
2. Départ exact du **TS9** alimentant C1, identifié par repère et case.
3. Départ exact et chaîne d'alimentation de l'armoire de secours (**TR7A**, **TGBT6** à clarifier).
4. Références protections des quatre armoires, implantation sur plan, repères et équipements aval (moteurs, variateurs, pompes).

**Statut : pré-inventaire photographique ; topologie aval non validée électriquement. L'application reste consultative, non utilisable pour une consignation.**
