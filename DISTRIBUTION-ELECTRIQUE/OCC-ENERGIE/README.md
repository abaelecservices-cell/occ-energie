# OCC ÉNERGIE — Cartographie du réseau électrique

> **Contrôle des photos déjà transmises (16/10/2026) :** consulter en priorité [le registre de réception vérifié](docs/16_REGISTRE_SOURCES_VERIFIEES_20261016.md) avant toute demande de nouveau relevé. Les anciennes listes de « photos manquantes » décrivent parfois seulement l'absence des originaux dans GitHub, **pas l'absence d'envoi par l'exploitant**. Corriger l'inversion vérifiée des séries TS1 / TS8 dans les livrables de photothèque avant toute qualification visuelle.

Application autonome (un seul fichier) de cartographie, de dépannage, d’entretien et d’aide à la compréhension des manœuvres de la distribution électrique de l’usine.
Indépendante de l’application OCC Bobinage (aucun code ni donnée partagés). *Designed by Labidi El Fahli.*

## Utilisation

Ouvrir **`OCC_ENERGIE.html`** (double-clic sur PC ; sur iPhone : app Fichiers → ouvrir). Fonctionne hors ligne.

**Version légère immédiatement disponible sur la branche de rapprochement** : `OCC_ENERGIE_2024_LITE.html`. Elle embarque le modèle complet (équipements, liaisons, façades, navigation et historique Excel 2024), mais omet les tuiles satellites du plus haut niveau de zoom afin de réduire la taille du fichier. La version normale reste `OCC_ENERGIE.html` et doit être régénérée avant fusion dans `main`.

| Onglet | Rôle |
|---|---|
| Accueil | Vue aérienne IGN, accès aux postes et sous-stations |
| Dépannage | Parcours en 3 touches : équipement (tableau, départ, machine, transformateur, cellule 20 kV) → symptôme observé → fiche. Raccourcis « Où il se trouve », « Ce qu’il alimente », « Fiche détaillée ». Diagnostic documentaire : `#/depannage/<repère>` |
| Plans | Plans d’implantation : poste de livraison CNR / EDF, sous-stations 1 et 2 (chaîne 20 kV → transfos → TGBT) |
| Tableaux | Arborescence CNR / EDF → cellules 20 kV → transformateurs → TGBT → TS → départs ; façades **uniquement vectorielles**, alimentation, sources documentaires et écarts |
| Réseau | Schéma 20 kV → transfos → TGBT ; mode simulation |
| Entretien | Gammes indicatives par type d’équipement + journal local exportable (CSV) |
| Excel 2024 (dans Tableaux) | Référence historisée : 36 départs (TGBT 1/2/4), 68 lignes d'âge des équipements. Recherche, filtre par TGBT et rapprochement visuel des repères de cases avec le modèle actuel. **N'ajoute pas de liaison dans le graphe**. URL interne : `#/historique2024`. |
| Registre (icône en haut) | Écarts actifs / résolus, avancement par tableau, clés, procédures, informations à fournir, dossier des photos sur ce poste |

La barre de recherche (raccourci `/`) est toujours visible.

**Sécurité** : application consultative. Chaque fiche affiche son statut AVANT ses étapes :
- *Fiche de contrôle* (tableau coupé, cellule HTA, défaut d’isolement, température transformateur, commande impossible) : aucune ouverture ni fermeture rédigée ;
- *Projet non validé* (départ déclenché, couplage, retour à la normale) : rédigé d’après une topologie documentaire incomplètement validée, à faire contrôler par les personnes habilitées ; aucune règle générale d’interdiction du couplage n’a été confirmée par l’exploitant le 15/10/2026 ;
- *Validée* : seulement si inscrite dans `validations.json` pour cet équipement ET cette version (champ `empreinte` imprimé sur la fiche) ; une fiche modifiée après validation s’affiche « validation caduque ».

La simulation est une hypothèse de travail : elle est signalée sur toutes les vues (avec son heure) tant qu’elle diffère de la configuration normale ; les fiches de dépannage n’en dépendent pas et le « test dans le simulateur » travaille sur une copie.

**Présentation des armoires : vectorielle uniquement.** Les photos sont conservées hors interface pour reconstruire et vérifier les façades. Aucun onglet photo, aucune visionneuse de photographie d'armoire, aucun lien d'ouverture de clichés. Les tableaux sans géométrie vérifiée affichent un gabarit vectoriel **non coté et non utilisable pour la consignation**. Les départs restent consultables dans l’arborescence sans inventer leur emplacement physique.

## Arborescence

```
OCC_ENERGIE.html        application complète (reconstruction en attente sur la PR)
OCC_ENERGIE_2024_LITE.html  application légère (zoom satellite limité)
docs/                   livrables : inventaire, registre photos, incertitudes, photos à reprendre, avancement, contrôles
src/                    sources : app.js, manoeuvres.js (fiches), courant.js (parcours), fiche.js, plans.js, plansvg.js, arbre.js, net.js, style.css, index.html
tools/                  parse_excel.py, parse_pptx.py, aerial.py, ortho.py + recale_ortho.py + site_tiles.py (orthophoto IGN : assets/vue_aerienne, tuiles embarquées) → build_data.py (+ facades_photo.py, unifilaire_detail.py, hta_photo.py, audit_2026_10_11.py) → build_plans.py → build_app.py → build_docs.py
validations.json        registre des fiches validées (clé = référence imprimée, ex. « S2:TGBT6:A », avec « empreinte »)
build/                  données intermédiaires (excel.json, data.json, inv_photos.json)
```

## Reconstruire après mise à jour des données

```bash
py -3 -I tools/parse_excel.py "../Plan électrique/Copie de Distribution.xlsm" build/excel.json
```
```bash
py -3 -I tools/build_data.py build/excel.json build/data.json
```
```bash
py -3 -I tools/build_plans.py
```
```bash
py -3 -I tools/build_app.py
py -3 -I tools/build_app.py --lite
```
```bash
py -3 -I tools/build_docs.py
```

Le croisement des 36 départs de l'index historique 2024 est documenté dans `docs/14_RAPPROCHEMENT_INDEX_EXCEL_2024.md`. Une case concordante n'est pas une validation de la destination alimentée.

Les façades sont décrites par des données (`F[...]` dans `tools/build_data.py` : colonnes, largeurs en mm, cases, appareils) et dessinées en SVG par l’application. Les salles disposent d’un repère en mm prêt à recevoir les cotes.

## Confidentialité

Documents sensibles : ne pas publier ce dossier sur un dépôt public ni sur un service en ligne. Aucune connexion au réseau industriel, aucune commande à distance.

## Consolidation du 15 octobre 2026

La branche `integration/consolidation-securisee-20261015` réunit le référentiel Excel 2024,
la navigation par halo et les façades TS8, TS1 et ensimage. La sauvegarde
`backup/main-before-consolidation-20261015` reste la référence avant consolidation.

- `OCC_ENERGIE.html` : application autonome complète, carte et données embarquées.
- `OCC_ENERGIE_2024_LITE.html` : mêmes fonctions, tuiles de niveau 12 omises.
- `OCC_ENERGIE_TS8.html` et `OCC_ENERGIE_VECTORIEL_MOBILE.html` : noms de livraison
  conservés, reconstruits avec le même contenu complet que `OCC_ENERGIE.html`.
- Les photographies/PDF sources restent dans le dépôt, hors interface vectorielle.
  Un catalogue de photos ne prouve pas la présence des fichiers photographiques originaux.

### Reconstruction et tests

Python 3.12 et Node.js 22 ou plus sont utilisés en CI. Depuis ce dossier :

```powershell
py -3 tools/rebuild.py
```

Cette commande reconstruit modèle, plans, quatre HTML et documentation, puis lance
chaque `tests/test_*.py`. Elle ne contacte aucun service et ne modifie pas Git.
Les entrées `build/excel.json`, `implantation.json`, les tuiles et le référentiel 2024
sont versionnées. Pour renouveler l'extraction du classeur, employer `tools/parse_excel.py`.

Pour les tests navigateur, installer les dépendances de test puis indiquer Chrome :

```powershell
py -3 -m pip install playwright==1.56.0
$env:OCC_CHROME = 'C:\Program Files\Google\Chrome\Application\chrome.exe'
py -3 tests/smoke_reseau.py
py -3 tests/smoke_catalogue.py
py -3 tests/smoke_features.py
```

`smoke_reseau.py` contrôle le parcours recherche, conducteur, usine, plan, façade et retour.
`smoke_catalogue.py` ouvre chaque tableau, ses onglets et les fiches de tous les nœuds,
puis vérifie l'inventaire dans l'arbre et plusieurs largeurs d'écran.
`smoke_features.py` contrôle les quatre HTML, le référentiel, les thèmes, le journal/CSV,
la navigation clavier de recherche et des scénarios conservatoires de simulation.

### Livraison privée

Ouvrir `OCC_ENERGIE.html` par double-clic ; aucun serveur ni dossier d'assets requis.
Les quatre HTML sont reproductibles depuis les sources. Les workflows reconstruisent
et vérifient les fichiers versionnés, sans commit automatique ni push concurrent.
Ne fusionner vers `main` qu'après réussite des contrôles bloquants sur la version finale.
La publication signifie ici mise à disposition dans le dépôt privé ; aucun hébergement
public ni accès au réseau industriel n'est créé.

La consolidation préserve le JavaScript et les fonctions existants. Elle ne constitue
pas une migration TypeScript, une certification électrique, une mesure Lighthouse,
ni une preuve de couverture unitaire à 80 %. Les connexions physiques et les procédures
de manœuvre restent soumises aux sources et validations du site.

Les livraisons manuelles de `main` à `3b92414` sont conservées exactement dans
`archives/20261015-main-3b92414/`. Leurs tuiles WebP TS8 sont également conservées.
Les HTML de référence sont reconstruits à partir des sources et des relevés détaillés.
