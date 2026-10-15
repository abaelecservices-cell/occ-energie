# OCC Énergie — Armoires « Groupe n°1 » et « Groupe n°2 » — relevé photographique (15/10/2026)

## Provenance
- Archive `Groupe n1.zip` : **4 photographies** `IMG_4093.jpeg`, `IMG_4094.jpeg`, `IMG_4096.jpeg`, `IMG_4098.jpeg`.
- Archive `Groupe n2 .zip` : **9 photographies** `IMG_4106.jpeg` à `IMG_4114.jpeg`.
- Les 13 originaux ont été examinés dans la conversation. **Les fichiers JPEG eux-mêmes ne sont pas archivés dans ce dépôt**.
- Statut : **relevé visuel**, sans contrôle des câbles, ni schéma constructeur, ni mesure de tension.

## Constat matériel (lecture photo)
Deux travées explicitement marquées sur étiquettes jaunes :
- **GROUPE N°1** (Merlin Gerin, enveloppe beige) : **trois commandes de départ superposées**, un gros appareil à commande rotative en partie basse. Marquages QF6 / QF7 / QF8 visibles ou probables ; les lignes de destination doivent être relues sur les originaux / terrain avant validation.
- **GROUPE N°2** (Merlin Gerin, enveloppe beige) : **deux commandes de départ superposées**, un appareil inférieur à commande rotative. Gros plan `IMG_4110.jpeg` : **QF9 / TS24A**, **QF10 / TS7B**, et appareil bas **QF5 / RÉSERVE** (lecture de photographie, à confirmer sur plaque pour le raccordement).
- **Travée d'instrumentation / « COUPLAGE »** : photos `IMG_4096.jpeg`, `IMG_4098.jpeg`, `IMG_4106.jpeg`, `IMG_4107.jpeg`, `IMG_4113.jpeg` montrent un ensemble de mesure, appareil électronique Merlin Gerin, deux petits appareillages et commande générale basse. Une étiquette **« COUPLAGE »** est présente au-dessus de l'appareil inférieur (repère préfixe à relire). Les photos des deux archives semblent montrer **la même travée** : ne pas créer deux couplages indépendants.
- Disposition physique suggérée par les cadrages : **Groupe 1 — travée couplage / mesure — Groupe 2**. À confirmer par une photo panoramique unique de l'alignement.

## Rattachements au modèle existant
- `tools/build_data.py` contient déjà un nœud **`GE1`**, « Groupe électrogène n°1 (secours) », relié *probablement* à l'arrivée secours `TS9_QS`, sur la base des plaques TS9 et du classeur.
- Les étiquettes photographiées sur les armoires « Groupe n°1 / n°2 » sont **compatibles avec un ensemble de distribution de secours**, mais **ne prouvent pas**, à elles seules, l'identité électrique avec `GE1`, ni l'origine exacte de TS7, TS9, TS24 ou de leurs demi-jeux de barres.
- Ne pas fusionner les deux groupes, ne pas ajouter de liaison `GE1/GE2 → TS7/TS9/TS24`, ne pas décrire de manœuvre / synchronisation et ne pas utiliser le couplage comme une liaison garantie sans schémas et repérage des câbles.
- Aucun paramètre de protection, intensité nominale, mode auto / manuel ou capacité des générateurs ne peut être confirmé.

## Exploitation logicielle
- Les façades peuvent être reconstruites en **trois travées visuelles** et exploitées comme **inventaire documentaire à vérifier**.
- Les repères visibles doivent rester associés à leurs **sources photo individuelles**.
- Ne pas déclarer les départs dans le graphe exploitable ni les fiches de manœuvre comme `confirme` sans relevé des conducteurs et correspondance schéma.
- Préserver le statut `a_verifier` pour toute relation électrique nouvelle.

## Contrôles terrain restant à mener
1. Une photo large d'**ensemble** montrant les travées Groupe 1, Couplage et Groupe 2 simultanément.
2. Un gros plan net de **toutes** les étiquettes QF5 à QF10 et de l'appareil marqué « Couplage ».
3. La plaque signalétique / l'armoire d'automatisme de **chaque groupe électrogène** et ses données nominales, s'il s'agit bien de groupes électrogènes.
4. Les plans de puissance et de commande des deux groupes et du couplage, ainsi que leur logique de transfert réseau/secours.
5. Confirmation du chemin des départs vers TS7, TS9 et TS24 : départ physique, repère de câble, arrivée, jeu de barres et mode d'interverrouillage.

**Conclusion : documentation photographique intégrable, topologie non validée.**