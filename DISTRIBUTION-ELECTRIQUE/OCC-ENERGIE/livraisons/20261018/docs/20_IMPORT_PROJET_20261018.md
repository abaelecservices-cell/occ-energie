# Récupération du projet transmis — affichage vectoriel uniquement

Correction demandée le 18 octobre : les photographies et images de pages restent des sources archivées. Elles ne sont plus proposées dans les vues opérationnelles. Les armoires sont affichées en SVG uniquement. Le fond aérien choisi par l’utilisateur est conservé.

Source : OCC_ENERGIE_COMPLET_PHOTOS_CORRIGE_20261017 2.html ; SHA-256 ff777fc12bb0abe513ae8ba41b4bd036410ca5f5077b651fd8be6318a0260707. Original archivé dans sources/projects/20261018 avec la version de l’application avant import. Le code du fichier reçu n’est pas exécuté : seules les données JSON et les images embarquées sont extraites.

## Résultat du recoupement

438 références de cellules : 436 correspondent aux données existantes sans différence de transcription ; deux intitulés supplémentaires sont conservés dans les fiches TGBT7 et TGBT8 : TR 7A & 7B / H1, « Sous/satation n°2 » ; TR 8A & 8B / G1, « Boosting Four 1 Sous/Station 2 ». Ce sont des mentions de classeur : elles ne remplacent pas la localisation actuelle et ne créent aucun départ.

267 entrées photographiques récupérées ; 266 existaient dans la photothèque précédente. Photo supplémentaire : IMG_3966.jpeg, TS8, repère TS8 lisible sur la vue. Huit classements corrigés de l’application actuelle sont préservés au lieu de reprendre les affectations du fichier source.

35 galeries et leurs 256 images de pages sont conservées comme sources de travail hors des vues opérationnelles ; ces images ne constituent pas 256 nouveaux documents PDF. Les 76 PDF originaux déjà livrés restent intacts. Cinq images d’implantation et leurs 88 objets relatifs sont conservés, ainsi que le schéma unifilaire et son texte, les dix indications de proximité, les cinq relations narratives et cinq mentions de documents complémentaires. L’ancien fond de site et ses 40 zones sont conservés dans le catalogue de provenance ; le fond utilisateur actif reste inchangé.

39 fiches disposent du panneau « Repères et informations complémentaires ». L’onglet « Repères et sources » présente les références du relevé, sans ouvrir les photos. La recherche générale prend en compte les données importées rattachées aux fiches ; le catalogue vectoriel propose également son filtre. Les informations sans correspondance sûre sont accessibles dans la rubrique SANS-AFFECTATION, dont Tableau 20kv 3:2, armoire 110 V distribution et coffrets ondulés étuves 1 et 2. Les cinq mentions de PDF complémentaires conservent leur statut de simple référence.

## Validation et limites

Douze scripts Node passent, ainsi que trois tests unitaires Python. Les 267 photos, 256 pages, cinq images de plans, unifilaire et ancien fond sont contrôlés par empreinte SHA-256. Les nœuds, liaisons, procédures, façades, écarts, validations et fond usine sont comparés à la sauvegarde et restent identiques. Les anciennes références photographiques sont conservées. Contrôle des liens locaux et vérification complète du ZIP effectués à la livraison. Navigation interactive du HTML dans le navigateur non vérifiée dans cet environnement ; aucune mesure Lighthouse annoncée. Lecture intégrale des petites plaques des 267 photos non réalisée pendant cet import.

## Reconstruction et livraison

Depuis le dossier OCC-ENERGIE :

- python tools/import_project.py "chemin du projet HTML reçu" pour réextraire les sources ; conserver la sauvegarde initiale avant tout nouvel import.
- python tools/build_app.py pour reconstruire le HTML ; aucune dépendance réseau au fonctionnement.
- node tools/test_project_import.cjs et python tools/test_project_compare.py pour les contrôles ciblés.
- Ouvrir OCC_ENERGIE.html à côté des dossiers assets, docs, build et sources ; conserver le dossier livré pour les médias hors ligne. Ctrl + F5 après remplacement des fichiers.

Publication : copier ensemble l’application et ses ressources sur l’hébergement existant. Aucun push GitHub ni déploiement distant effectué par cet import. Les anciens scripts métier JavaScript sont conservés ; aucune migration TypeScript globale ni promesse de budget Lighthouse ne fait partie de cette récupération de données.

## Présentation vectorielle et arborescence

Les 68 SVG existants restent zoomables ; leur présence ne certifie pas toutes les petites plaques. La photo TS8 supplémentaire confirme une vue déjà citée dans le relevé TS8 ; elle ne justifie pas de nouveau départ inventé. Les 438 mentions de classeur, les notes et les deux intitulés complémentaires sont consultables directement dans les branches de l’arbre et les fiches détaillées. Le filtre de l’arborescence indexe aussi les compléments. Les anciennes galeries et PDF sont archivés pour préserver la provenance, sans lien d’ouverture depuis les vues opérationnelles. La configuration du dossier photo a été retirée de l’interface. Aucun nouveau dessin d’armoire n’est annoncé comme certifié par ce changement de présentation.
