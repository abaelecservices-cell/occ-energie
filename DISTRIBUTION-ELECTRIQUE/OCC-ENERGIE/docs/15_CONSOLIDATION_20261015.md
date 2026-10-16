# Consolidation OCC Énergie — 15 octobre 2026

Dépôt privé : `abaelecservices-cell/occ-energie`.
Branche : `integration/consolidation-securisee-20261015`.
Sauvegarde conservée : `backup/main-before-consolidation-20261015` (`4a11b68`).

## Historique et résolution

- La PR #13 était fusionnée par `efcef59`, jusqu'au commit `9527617`.
- Les ajouts ultérieurs de cette branche, jusqu'à `bcc676e`, sont intégrés : TS1 et
  deux armoires ensimage indépendantes, sans liaison amont supposée.
- PR #14 : conserver les libellés du simulateur issus de #13 et réunir les entrées CI.
  L'archive 2024 reste distincte du graphe actif : 36 départs et 68 historiques.
- PR #15 : conserver le retour au schéma complet et ajouter la route historique.
- `main` (`3b92414`) est inclus : tuiles WebP préservées ; livraisons TS8/mobile
  manuelles archivées exactement dans `archives/20261015-main-3b92414/`.
- La branche `codex/unifilaire-localisation-2026-10-14` est déjà incluse.
- `transfert/iphone-html-2026-10-15` ajoute seulement un workflow temporaire de
  transfert ; conservée sans intégration de ce workflow à la chaîne de référence.
- Aucun force push ni suppression de branche.

## Reconstruction et corrections

`tools/rebuild.py` recompose modèle, plans, quatre HTML, documentation et lance
tous les tests documentaires. Les livrables TS8/mobile sont synchronisés avec
l'application complète ; la version légère conserve les fonctions et réduit la carte.

Les workflows incluent désormais l'intégration et ses PR, exécutent tous les tests
documentaires et les trois parcours navigateur. La reconstruction CI est en lecture
seule côté Git : contrôle de synchronisation et artefacts, sans push automatique.

Le test ensimage accepte les nœuds sans tableau. Le test réseau attend le routage
effectif avant de vérifier la localisation ; ses assertions métier sont conservées.
Le compteur de départs du build inclut aussi les départs HTA hors dictionnaire Excel.

## Validation locale

- 9 suites `test_*.py` réussies : complétude, cohérence, couplage, ensimage, 2024,
  intégrité des façades, terrain, TS8 et présentation vectorielle.
- Chrome et Edge : trois suites navigateur réussies dans chaque navigateur.
- Catalogue : 13 routes, 66 tableaux, 291 onglets, 730 fiches ; 503 départs dans l'arbre.
- Parcours : recherche, halo, réseau, usine, plan, façade et retour au réseau.
- Fonctions : quatre HTML, filtres 2024, thèmes, journal persistant, CSV,
  raccourci clavier de recherche, refus de couplage non qualifié et secours CNR/EDF.
- Largeurs 390, 768, 1440 pixels ; captures et absence d'appel réseau vérifiées.
- Syntaxes Python, JavaScript source/embarqué, YAML et marqueurs HTML contrôlés.
- PDF unifilaires A3/A2 : deux fichiers produits, 8 pages chacun.

Chrome et Edge partagent Chromium : Safari/Firefox et l'app Fichiers iPhone restent
non testés. Aucune certification de 60 fps, Lighthouse ou couverture 80 % n'est revendiquée.

## Conservation et limites

Le modèle contient 730 nœuds, 735 liaisons, 66 tableaux, 23 transformateurs,
503 départs et 33 écarts documentaires. Aucun nœud ou tableau de la sauvegarde
n'est supprimé. Toutes ses liaisons sont préservées, sans ajout ni modification.

Les PDF/photos/archives présents dans Git sont conservés. Les 153 photos HEIC du
lot du 15/10 sont cataloguées, mais leurs binaires n'étaient pas importés dans le dépôt
source ; leur présence complète ne peut pas être certifiée (voir document 13).

L'audit relève 21 départs sans chaîne amont, 264 sans bâtiment, 270 sans plan local,
190 sans position de façade et 379 sans numéro de case. Ces lacunes restent visibles.
19 formes du plan ne sont pas rattachées à un équipement ; aucun rattachement inventé.

Les Actions examinées sont refusées avant toute étape : GitHub cite des paiements
récents échoués ou un plafond de dépenses à revoir. Ce message ne distingue pas les
deux causes et ne prouve pas une dette. Aucun réglage de facturation n'est modifié.
La validation distante et l'intégration finale à `main` restent conditionnées à la
résolution de ce blocage et au succès des contrôles sur le commit final.
