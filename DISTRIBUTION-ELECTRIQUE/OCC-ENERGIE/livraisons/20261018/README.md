# OCC Énergie — reprise photographique du 18 octobre 2026

Ouvrir **OCC_ENERGIE.html** avec les dossiers assets et docs conservés à côté.

## Avancement réel

La relecture exhaustive est **en cours**. 93 entrées photographiques sur 637 ont été examinées individuellement dans cette reprise. 21 pages PDF sur 868 sont consignées comme lues. Les encodages multiples peuvent représenter une même prise de vue : ces nombres ne sont pas un compte de prises de vue uniques.

Façades reprises : TS16, TS9, TS15, coffrets pompes eau glacée, TS40, Bronzini, TS28 et TGBT6. La géométrie est issue des vues disponibles et reste en proportions relatives, sans cotes mesurées. La présence d'un SVG et les tests structurels ne certifient pas sa fidélité exhaustive.

Les relevés photo par photo et leurs limites sont disponibles dans build/relecture-photos.json et build/relecture-pdf-pages.json. Les nouveaux repères, contradictions et demandes ciblées figurent dans build/photo-readings.json. Aucune liaison électrique n'est créée par déduction depuis une simple ressemblance de libellé. Les rapprochements photographiques TGBT6/TS28 et TGBT6/TS40 sont présentés avec leurs preuves et leurs limites.

Les vues opérationnelles montrent les armoires en SVG. Le fond aérien utilisateur reste conservé. Les archives photographiques et PDF complètes restent dans la livraison locale ; cette publication d'exécution ne les duplique pas.

## Reconstruction et contrôles

Python 3 : `python tools/build_app.py`.

Contrôles ciblés de cette reprise : `node tools/test_physical_readings.cjs` et `node tools/test_equipment_audit.cjs`. Ils contrôlent les cibles, profils physiques, mentions documentaires et l'absence de liaison déduite. Ils ne constituent pas un contrôle terrain ni une validation visuelle par l'exploitant. Les anciens tests d'égalité intégrale des données antérieures restent à adapter aux ajouts documentaires explicitement sourcés ; aucune réussite globale de la suite n'est annoncée.

## Publication

Cette version reste dans livraisons/20261018 afin de préserver le modèle consolidé et les travaux SAP/Excel de la racine. Copier le dossier complet ou le servir en fichiers statiques. La publication GitHub n'est pas un déploiement de site.
