# Lot photographique OCC Énergie — 15 octobre 2026

## Réception et classification

153 photographies HEIC réparties en 10 archives transmises par l'exploitant le 15/10/2026. Inventaire manuel des planches visuelles. Le présent document **consigne la réception** : les fichiers binaires ne sont **pas encore importés dans ce dépôt**. Aucune validation topologique ne doit être déduite de ces seules photographies.

| Archive | Photos | Équipement associé | Traitement |
|---|---:|---|---|
| Ts 16(1).zip | 16 | TS16 — STEP | Façade et colonnes, photos nouvelles, reconstruction à reprendre |
| Ts 15.zip | 25 | TS15 — Batch | Façade et commandes, photos nouvelles, reconstruction à reprendre |
| Tgbt 9.zip | 30 | TGBT 9 | Photographies de façades, travées A/B et vues intérieures, confronter avec façade existante |
| Tgbt 6(1).zip | 13 | TGBT 6 | Photographies de façades et départs, confronter avec façade existante |
| Tgbt 2.zip | 11 | TGBT 2 | Photographies de façades, confronter avec façade existante |
| Tableau 6kv.zip | 22 | Tableau 6 kV — Four 2 | Façades des cellules, confronter avec schémas existants |
| Gorge.zip | 11 | Tableau Gorge (Four 2) | Façades d'armoires grises, documentation photographique |
| Bronzini.zip | 8 | Bâtiment Bronzini | Vues de façades et d'appareillages, documentation photographique |
| Varivolt.zip | 13 | Varivolt 1 et 2 | Deux ensembles distincts, zones 1 et 2, à documenter séparément |
| Onduleur 6 a.zip | 4 | **Batterie condensateur TR6A** | **Nom d'archive trompeur**, voir ci-dessous |

## Correction prioritaire d'identification

Sur **IMG_4267.heic** (lot « Onduleur 6 a.zip »), la façade porte **« PROVIENT DE TR 6A / BATTERIE CONDENSATEUR 6A »**. Ne pas associer ces photos à un onduleur 6A sur la seule base du nom du ZIP. Classer en **Batterie condensateur 6A — TR6A** sous réserve de la documentation électrique.

## Règles d'intégration dans l'application

1. Importer les photographies converties en JPG sous `assets/photos_terrain/2026-10-15/`, avec noms de lots et noms source préservés et un manifeste SHA-256.
2. Pour TS15 et TS16, mettre à jour la couverture photographique après import ; reconstruire les façades à partir des vues générales et inscriptions lisibles.
3. Pour TGBT2/TGBT6/TGBT9 et tableau 6 kV, confronter les départs et l'ordre des cellules avec les façades déjà vectorisées. Ne pas remplacer les schémas existants sans contrôle repère-à-repère.
4. Maintenir les **deux** tableaux Varivolt 1 et 2 distincts ; conserver le repérage des zones.
5. Ne pas inventer de liaison de distribution, de couplage ou de régime de consignation à partir de la proximité des armoires.
6. Mettre à jour `docs/5_AVANCEMENT.md` uniquement après l'import effectif des images et la vérification des associations.

## État de publication

- Rapport d'identification et classement : **consigné dans GitHub**.
- Images JPG et manifestes complets : préparés dans le lot de livraison de la conversation, **non encore publiés dans le dépôt**.
- Application OCC Énergie et arborescence électrique : **inchangées par cette opération**.
