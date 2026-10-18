# Consignes pour Claude — intégration du fond aérien OCC

Intègre la vue aérienne de mon usine Owens Corning à L’Ardoise dans la vue Distribution de mon application OCC.

1. Lis `00_COMMENCER_ICI.md`, `LISEZ_MOI.md`, `metadata.json` et le code du composant. Repère ensuite la vue Distribution et les conventions du projet OCC auquel tu as accès.
2. Utilise les fichiers fournis : PNG transparent ou WebP sans perte pour l’image, et `occ_files` pour le chargement progressif au zoom. Préserve les pixels réels, la transparence et le cadrage. La résolution réelle est de 20 cm/pixel ; l’image fait 2 008 × 2 636 pixels.
3. Réutilise ou adapte `occ-orthophoto-viewer.js` à l’architecture existante. Conserve le zoom à la molette, le pincement tactile, le déplacement, la vue complète et l’affichage du détail natif. Charge les tuiles selon la zone visible et le niveau de zoom.
4. Place les ressources dans un dossier d’assets dédié. Adapte `tileRoot` au chemin réellement utilisé. L’aperçu autonome HTML sert à consulter le résultat ; privilégie les ressources séparées pour intégrer le composant.
5. Superpose les repères des équipements et les liaisons électriques dans une couche indépendante, synchronisée avec le zoom et le déplacement. Utilise les données existantes et les positions validées. Conserve les libellés lisibles. Stocke les positions en coordonnées d’image ou en coordonnées normalisées.
6. Préserve les fonctionnalités, les données et le thème vert OCC de l’application. Garde le module cohérent avec le code existant et évite les composants de navigation en doublon.
7. Conserve l’attribution : « Source : IGN — BD ORTHO® — prise de vue 2024 — Licence Ouverte Etalab 2.0 ». Le contour est indicatif et les coordonnées sont en Lambert-93, EPSG:2154.
8. Vérifie le chargement de toutes les tuiles, la transparence, les commandes de navigation, l’alignement des repères et le rendu sur ordinateur et écran tactile. Termine par la liste des fichiers modifiés et les vérifications effectuées.

Si le code OCC ou les positions des équipements manquent dans ton environnement, identifie les fichiers nécessaires pour poursuivre l’intégration.
