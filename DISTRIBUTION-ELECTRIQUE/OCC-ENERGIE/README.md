# OCC ÉNERGIE — Cartographie du réseau électrique

Application autonome (un seul fichier) de cartographie, de dépannage, d’entretien et d’aide à la compréhension des manœuvres de la distribution électrique de l’usine.
Indépendante de l’application OCC Bobinage (aucun code ni donnée partagés). *Designed by Labidi El Fahli.*

## Utilisation

Ouvrir **`OCC_ENERGIE.html`** (double-clic sur PC ; sur iPhone : app Fichiers → ouvrir). Fonctionne hors ligne.

| Onglet | Rôle |
|---|---|
| Accueil | Vue aérienne IGN, accès aux postes et sous-stations |
| Dépannage | Parcours en 3 touches : équipement (tableau, départ, machine, transformateur, cellule 20 kV) → symptôme observé → fiche. Raccourcis « Où il se trouve », « Ce qu’il alimente », « Fiche détaillée ». Diagnostic documentaire : `#/depannage/<repère>` |
| Plans | Plans d’implantation : poste de livraison CNR / EDF, sous-stations 1 et 2 (chaîne 20 kV → transfos → TGBT) |
| Tableaux | Arborescence CNR / EDF → TGBT → TS ; façades vectorielles, départs, alimentation, photos, écarts |
| Réseau | Schéma 20 kV → transfos → TGBT ; mode simulation |
| Entretien | Gammes indicatives par type d’équipement + journal local exportable (CSV) |
| Registre (icône en haut) | Écarts actifs / résolus, avancement par tableau, clés, procédures, informations à fournir, dossier des photos sur ce poste |

La barre de recherche (raccourci `/`) est toujours visible.

**Sécurité** : application consultative. Chaque fiche affiche son statut AVANT ses étapes :
- *Fiche de contrôle* (tableau coupé, cellule HTA, défaut d’isolement, température transformateur, commande impossible) : aucune ouverture ni fermeture rédigée ;
- *Projet non validé* (départ déclenché, couplage, retour à la normale) : rédigé d’après la topologie documentée et la règle d’exploitation donnée par l’exploitant, à faire valider ;
- *Validée* : seulement si inscrite dans `validations.json` pour cet équipement ET cette version (champ `empreinte` imprimé sur la fiche) ; une fiche modifiée après validation s’affiche « validation caduque ».

La simulation est une hypothèse de travail : elle est signalée sur toutes les vues (avec son heure) tant qu’elle diffère de la configuration normale ; les fiches de dépannage n’en dépendent pas et le « test dans le simulateur » travaille sur une copie.

Les liens photo ouvrent les PDF du dossier `Plan électrique` placé à côté du dossier de l’application (`../Plan électrique/`) ; un autre emplacement peut être réglé dans le Registre (enregistré sur le poste).

## Arborescence

```
OCC_ENERGIE.html        application (à diffuser)
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
```
```bash
py -3 -I tools/build_docs.py
```

Les façades sont décrites par des données (`F[...]` dans `tools/build_data.py` : colonnes, largeurs en mm, cases, appareils) et dessinées en SVG par l’application. Les salles disposent d’un repère en mm prêt à recevoir les cotes.

## Confidentialité

Documents sensibles : ne pas publier ce dossier sur un dépôt public ni sur un service en ligne. Aucune connexion au réseau industriel, aucune commande à distance.

## Relevé TS8 du 15 octobre 2026 — livraison intermédiaire

- **`OCC_ENERGIE_TS8.html`** : version reconstituée du parcours OCC Énergie contenant la façade SVG TS8 (4 travées, 5 tiroirs, 10 repères cliquables sur les 20 départs existants). Les départs sans correspondance photographique restent dans l'inventaire, sans placement inventé. Attention : la plaque rouge indique une **alimentation prise en amont du disjoncteur principal** ; l'application ne certifie jamais une consignation.
- Le fichier utilise **25 tuiles WebP graphiques externes** dans `assets/ts8_site_tiles/` et conserve les 9 autres tuiles directement intégrées. Pour préserver l'affichage de la carte satellite, lancer cette version avec le dossier complet du dépôt, de préférence depuis un serveur local ; **ce n'est pas la version portable mono-fichier**.
- **`OCC_ENERGIE.html`** demeure la version autonome antérieure, conservée sans modification. Pour régénérer la version mono-fichier intégrant le TS8 et les autres relevés du 15/10/2026, utiliser `tools/build_data.py` suivi de `tools/build_app.py` puis des tests depuis une copie locale complète (ou lorsque les runners GitHub Actions refonctionneront).
- Sources intégrées : `tools/ts8_photo.py`, `src/app.js` et `docs/TS8_RELEVE_TERRAIN_2026-10-15.md`. La reconstruction vectorielle ne contient aucune photographie de façade. Les 20 départs Excel de TS8 sont conservés ; aucune arête électrique nouvelle n'a été ajoutée.
- Contrôle du 15/10/2026 : extraction/parse JSON embarqué, unicité des 10 repères, 20 départs, ordre des 4 travées, 5 tiroirs, présence de l'alerte, absence d'arête orpheline : **conforme**. **Test visuel de navigateur et tests Python non exécutés** en raison des runners GitHub indisponibles.
