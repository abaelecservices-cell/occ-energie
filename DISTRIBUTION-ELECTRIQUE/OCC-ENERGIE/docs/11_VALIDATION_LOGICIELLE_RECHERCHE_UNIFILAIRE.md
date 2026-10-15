# OCC Énergie — livraison logicielle du parcours « unifilaire d’abord »

## Comportement retenu pour la validation utilisateur

1. Recherche globale (départ, identifiant interne, libellé, repère, armoire, transformateur ou tableau).
2. Après le **clic sur un résultat**, la vue `Réseau HTA / BT` s’ouvre sur le schéma complet et cible l’alimentation du repère ; aucun onglet façade, carte ou dépannage ne doit s’ouvrir automatiquement.
3. Le conducteur réellement dessiné pour le chemin documentaire normal se distingue en jaune lumineux. Les liaisons incertaines sont pointillées en orange. Les bifurcations CNR/EDF ne sont allumées que du côté réellement retenu par le graphe.
4. Un panneau sous le schéma donne le parcours par repères, sa traçabilité, les incohérences documentaires, les clés renseignées et les actions **sur clic uniquement** : voir toute la liaison, voir la façade exacte (lorsqu’elle existe), voir l'implantation, voir le tableau.
5. Si le départ n'est **pas dessiné individuellement**, aucun faux câble n'est créé : le trajet amont réellement représenté est lumineux et l'absence de case sur le synoptique est signalée. Si aucune chaîne complète n'existe, un message le dit sans créer de halo artificiel.
6. Le retour depuis la façade et le plan conserve le repère sélectionné. Aucun clic sur « Ouvrir la façade » n'est simulé par la recherche.

## Validation logicielle, sans attendre le relevé terrain

- Vérifier dans le navigateur la recherche globale par identifiant exact, le choix sur résultats multiples, l'affichage initial du schéma et la surbrillance du conducteur.
- Vérifier l'absence d'ouverture automatique de façade, et son ouverture seulement par clic sur une commande explicite.
- Tester un départ du TGBT2 avec chemin, bâtiment, plan et façade déjà présents, puis le retour vers le réseau.
- Tester une recherche de tableau, un départ à case non documentée et les niveaux de zoom.
- Vérifier en CI la cohérence électrique **documentaire**, le HTML assemblé, la syntaxe et la génération du registre de terrain.
- Ne fusionner que si les contrôles qualité, navigateur, PDF et audit sont verts.

## Relevés physiques ultérieurs

Le dossier GitHub Actions **OCC Energie - Audit localisation et facades** produit les fichiers :

- `DEPARTS_A_COMPLETER.csv` : inventaire de tous les départs indexés.
- `FACADES_MANQUANTES_RELEVE_TERRAIN.csv` : un tableau par façade vectorielle absente, avec champs vides pour les observations à faire.
- `CASES_A_IDENTIFIER_TERRAIN.csv` : départs dépourvus de façade ou de case documentée.
- `CHECKLIST_TOUR_TERRAIN.md` : tournées par localisation et consignes photographiques.
- `SYNTHESE.md` : indicateurs de complétude (pas des preuves physiques).

Les champs relevés sont volontairement **vides** avant la visite. La mise à jour du modèle et l'affirmation « confirmé » attendront la vérification des repères et photos sur site.

**Sécurité :** cette application reste un outil d'aide documentaire. Elle n'observe pas en temps réel l'état des disjoncteurs ; les trajets ne sont pas des plans de cheminement de câble. Toute manœuvre exige habilitation et procédure validée.