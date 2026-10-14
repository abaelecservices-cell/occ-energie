# Reprise de l'unifilaire OCC Energie - 14 octobre 2026

## Portee

Cette livraison reprend la branche stable d'OCC Energie, sans recuperer les fichiers
non publies de la session interrompue. La branche historique
\`codex/unifilaire-localisation-2026-10-14\` n'a pas ete modifiee.

Source officielle des planches : \`Plan électrique/schema unifilaire 20 KV derniere version.pdf\`,
R112529, revision H. Aucune liaison nouvelle n'est inventee par cette mise a jour.

## Navigation ajoutee

Dans **Reseau**, la recherche contextuelle permet de saisir un repere (ex. TR1A),
de centrer l'element correspondant et de le mettre en surbrillance, sur la vue de
principe ou, si l'element y est dessine, dans l'ordre des cellules HTA.

Le volet de resultat donne acces a la fiche, a la localisation documentaire,
aux cles/reperes disponibles et aux incoherences documentaires associees.
Un equipement non dessine est signale, et son chemin amont peut etre utilise
pour l'orientation dans le graphe. La recherche generale preexistante reste inchangee.

## Documents imprimables

La commande reproductible est :

\`\`\`bash
python -m pip install 'pymupdf==1.26.5' 'pypdf==5.9.0'
python DISTRIBUTION-ELECTRIQUE/OCC-ENERGIE/tools/generer_planches.py
\`\`\`

Les dossiers A3 et A2 comportent chacun huit planches vectorielles :
vue generale, poste de livraison, sous-station 1 gauche/droite,
sous-station 2 gauche/droite, tableau 6 kV Four 2, cartouche.

Un workflow \`OCC Energie - Planches unifilaires A3/A2\` publie aussi les PDF
dans les artefacts telechargeables GitHub Actions.

## Verifications

- \`controle-occ.yml\` : syntaxe Python/JavaScript, presence des fichiers,
  reconstruction de l'HTML et cohérence informatique du graphe.
- \`occ-reseau-ui.yml\` : parcours navigateur Chrome (recherche TR1A,
  zoom/surbrillance, passage de vue, affichage de localisation et fiche).
- \`occ-unifilaire-pdf.yml\` : generation, controle du format et publication des PDF.

## Vigilances et limites

- Les inscriptions de destination TR1A/TR2A sur R112529 sont contradictoires
  avec d'autres sources. Le modele suit actuellement TR1A/TR1B vers TGBT1,
  TR2A/TR2B vers TGBT2 ; **les etiquettes physiques restent a confirmer**.
- Les denominations des sous-stations divergent entre documents.
- Les etiquettes de cles, serrures et protections sont documentaires :
  aucune sequence de manoeuvre HTA n'est certifiee par cette mise a jour.
- Les PDF sont des decoupes de l'original, et non un schema "as-built" corrige.
- Les chaines completes jusqu'aux armoires machines restent tributaires de
  documents secondaires et de confirmations physiques.
- Une relecture technique par l'exploitant habilite est requise avant toute
  utilisation pour consignation.
