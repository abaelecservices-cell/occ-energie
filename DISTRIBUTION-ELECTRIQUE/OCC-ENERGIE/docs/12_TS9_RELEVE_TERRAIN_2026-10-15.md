# OCC ÉNERGIE — TS9, relevé terrain du 15 octobre 2026

## Périmètre et source

Archive reçue : **Ts9.zip**, 12 photographies JPG : IMG_4081 à IMG_4092. Les fichiers originaux demeurent dans la pièce jointe de la conversation ; ils ne sont **pas archivés en binaire sur GitHub**. Le présent relevé complète les observations déjà issues de **Ts9.pdf** dans le modèle OCC Énergie.

Tableau **TS9 — Chaufferie**, appareillage de façade **Merlin Gerin** beige, quatre travées principales numérotées 1 à 4 et panneaux supplémentaires de mesure/commande. Le modèle existant TS9 représente déjà deux demi-jeux de barres, leurs arrivées et un couplage. Cette mise à jour améliore la lecture de la travée 2 ; elle ne crée aucun lien électrique supplémentaire.

## Repères photographiés : travée 2 (étiquettes bleues)

Le cliché **IMG_4091** et le détail **IMG_4092** permettent de transcrire **15 étiquettes** précédemment qualifiées d'illisibles. Ce sont des **marquages de façade observés** ; leur alignement n'établit pas leur correspondance unitaire avec des protections internes.

| Rang supérieur | Rang inférieur |
| --- | --- |
| COFFRET ALIM BUTANE | ALIM VIGILHOM |
| CONTROLE DIESEL EAU FROIDE | 7 PM 20 |
| PRIMAIRE TRANSFO 380 - 110 | RESERVE |
| ECL SECOURS CHAUFFERIE | ALIM 110 V |
| DEPART COFFRET ALARME PORTAIL SNCF | 7M15 CONTROLE DIESEL |
| ECLAIRAGE SECOURS GROUPES | ALARME CHAUFFERIE |
| SECONDAIRE TRANSFO 380 - 110 | |
| SECHEUR AIR | |
| INSTRUMENTATION CHAUFFERIE | |

Les expressions ci-dessus suivent au plus près les étiquettes photographiées. **VIGILHOM** est conservé tel que visible, sans correction implicite en « Vigilohm ». Les accents sont normalisés uniquement pour la présentation dans les vues où cela n'altère pas le repère.

## Autres zones visibles

- **Travée 1, IMG_4081/4082** : départ repéré **7PM26 — pré-transfert de fuel domestique n° 2** (libellé manuscrit) ; **7KM07 — compresseur d'air d'instrumentation de secours** (repère conservé du modèle antérieur, lecture photographique de la terminaison à corroborer) ; **interrupteur général isolement JdB-A**, **arrivée secours groupe 1**, **armoire TS17A**.
- **Panneaux adjacents, IMG_4083/4084/4085** : centrale de mesure ; dispositif de permutation des sources (commande « R = forçage » / « A = auto ») ; consigne locale indiquant l'existence d'une séquence de secours, du jeu de barres secours, de **TS9A** et de **TS9B**. Les instructions affichées constituent une source documentaire non validée, pas une procédure de manœuvre à exécuter.
- **Travée 3, IMG_4086/4090** : coffret chaudière 1 et 2 (7M08 / 7M09), commande diesel pompe eau froide (7M13), auxiliaires groupe 1 et 2, chauffage diesel process (7PM43 selon lecture de la plaquette ; modèle antérieur 7PM043), couplage jeu de barres, prise PS chaufferie et volet chaufferie.
- **Travée 4, IMG_4087/4088/4089** : tiroir repéré AE7P025 (400 V), second tiroir sans identification fiable, armoire silo kaolin, sécheurs 7K121 et 7K122, départs réchauffeurs 7,5 kW correspondants, arrivée B normale TS17B.
- **Plaques de risque**, en particulier IMG_4086/4090 : risque classe 0 ; valeurs de l'étiquette col. 3 visibles **400 V, Icc 1,62 kA, énergie incidente 0,19 cal/cm², limite d'approche 14,91 cm**. Reprendre la plaque sur site avant tout usage de sécurité ; ne pas déduire de ces valeurs une autorisation de manœuvre.

## Intégration au modèle et à la façade

Le modèle possédait déjà les noeuds **TS9_A, TS9_B, TS9_QA, TS9_QB, TS9_QS, TS9_QC** et les départs photographiés antérieurement. Cette révision :

1. Remplace les deux groupes d'étiquettes bleues sans texte par des étiquettes **lisibles et consultables** sur la façade SVG.
2. Conserve les 15 marquages bleus comme **annotations visuelles**, et non comme départs de distribution raccordés à un demi-jeu de barres par hypothèse.
3. Maintient les distinctions TS9A/TS9B et l'existence documentaire du groupe de secours et du couplage ; aucune position réelle ni logique de permutation n'est déduite de la photo.
4. Maintient les incertitudes préexistantes et les références croisées au classeur de distribution électrique.

## Contrôles restant nécessaires

- Correspondance exacte des **15 repères bleus** avec les disjoncteurs, borniers et circuits internes de la travée 2.
- Identification du **deuxième tiroir de la travée 4** et lecture de ses caractéristiques.
- Vérification **7KM07 / 7PM07** sur le départ compresseur, et **7PM43 / 7PM043** sur le chauffage diesel process (différences de lecture selon sources).
- Confirmation des connexions des deux demi-jeux de barres, du point de raccordement groupe électrogène et des verrouillages de couplage par le schéma à jour.
- Confirmation des arrivées amont TS17A/TS17B, des repères et de l'état normal des sources.
- Conservation des 12 photographies originales dans la base de sources du projet si les droits et la capacité de stockage le permettent.

**Statut** : relevé visuel intégré au modèle logiciel, **non validé électriquement**. OCC Énergie reste un outil documentaire ; aucune manœuvre ne doit être fondée uniquement sur sa simulation ou sa façade reconstruite.
