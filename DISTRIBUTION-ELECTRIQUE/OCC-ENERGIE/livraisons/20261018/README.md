# OCC Énergie — livraison vectorielle du 18 octobre 2026

Ouvrir **OCC_ENERGIE.html** dans ce dossier en conservant assets et docs à côté. Cette livraison correspond au HTML validé localement avec l’exploitant ; le manifeste permet de comparer les fichiers publiés à la livraison locale.

68 représentations SVG ; compléments intégrés à 39 fiches et à l’arborescence ; galeries de photos retirées des vues opérationnelles. Le fond aérien fourni par l’exploitant est conservé. Les raccordements non établis ne sont pas transformés en liaisons électriques.

Cette version est publiée dans un dossier distinct afin de conserver intégralement le modèle consolidé et les travaux SAP/Excel présents à la racine du projet. Elle ne remplace pas implicitement ce modèle ni ses variantes mobile et légère. Les deux modèles doivent être rapprochés avant toute substitution de la racine.

## Reconstruction

Python 3 : `python tools/build_app.py`. Le HTML utilise les données et correctifs JSON de build, les modules de src et validations.json. Aucun téléchargement requis pour reconstruire ou consulter l’application. Les scripts d’extraction des sources restent des outils de préparation et nécessitent les documents originaux.

## Contrôles reproductibles de cette publication

Node : exécuter les six scripts `tools/test_*.cjs` présents. Python : `python tools/test_project_compare.py`. Les contrôles portent sur l’arbre complet, le mapping, les façades PL20/TGBT8, le fond utilisateur et l’absence de photos dans les vues opérationnelles. Le rapport complet local atteste également les contrôles d’archives et des médias reçus ; ces archives volumineuses ne sont pas dupliquées dans cette livraison d’exécution.

Les photos d’armoires et PDF de travail restent dans le dossier local complet et les archives sources existantes du dépôt. Les liens vers ces photos sont absents des vues opérationnelles. L’ancien index photographique est conservé uniquement pour le classement reproductible par l’outil d’import ; ses médias ne sont pas inclus dans cette publication d’exécution. Aucune lecture exhaustive des petites plaques ni vérification interactive du navigateur n’est annoncée.

## Mise à disposition

Copier ce dossier complet ; ouvrir son HTML, ou servir son contenu en fichiers statiques. Aucun service réseau applicatif ajouté. Une publication sur GitHub ne déploie pas automatiquement un site web.
