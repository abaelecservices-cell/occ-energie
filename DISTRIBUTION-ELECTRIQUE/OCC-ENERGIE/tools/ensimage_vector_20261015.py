"""OCC Energie : facades Ensimage rectifiees sur les PHOTOS ORIGINALES.
TS1 : Ts1.zip (IMG_3978-3992), 15 photographies, reunion des panneaux bleu-gris.
TS8 : Ts8.zip (IMG_3966-3977) : NE PAS attribuer a TS1.
La photo d'ensemble IMG_3990 montre SEPT zones verticales discernables.
Le nombre de tiroirs, leur ordre, les inscriptions de reserve sont visuels ;
aucun cable, depart ni protection n'est affecte sur cette seule base.
"""

SOURCE_TS1 = ("Ts1.zip — IMG_3978 à IMG_3992 (15 vues originales) ; "
              "vue générale IMG_3990, vues détaillées IMG_3979 à IMG_3988")
SOURCE_ENSIM = ("Lot distinct Ensimage 15/10/2026 : ensemble de photographies "
                "hétérogène contenant aussi des vues de TS8 et de commandes ; "
                "répartition entre les armoires A/B non validée.")

boards["TS1"]["note"] = (
    (boards["TS1"].get("note") or "") +
    " Rectification photographique du 18/10/2026 : TS1 est une armoire "
    "BLEU-GRIS à tiroirs, pas une armoire beige. La vue générale IMG_3990 "
    "montre sept zones verticales visibles de gauche à droite : compartiment "
    "sans tiroirs, groupe N°6, groupe N°1, panneaux N°2/N°3/N°5, puis "
    "trois zones de tiroirs et commandes. Le plan est sans cotes ni attribution "
    "de départs ; les dimensions et repères restent à confirmer.")
boards["TS1"]["photo_fidelity"] = "corrigee_partielle_non_certifiee"
boards["TS1"]["safety_warning"] = (
    "Façade TS1 corrigée à partir de IMG_3978-3992, encore NON CERTIFIÉE "
    "tiroir par tiroir. Aucun raccordement ou repère de départ n'a été déduit "
    "de la position visuelle. Ne pas utiliser pour une manœuvre ou une consignation.")

def _tiroirs_ts1(count, y0, dy, prefix):
    """Tiroirs visibles, sans attribution de charge ni dimensions inventees."""
    return [dict(y=y0+i*dy, h=max(5,dy-1), k="drawer",
                 label=f"{prefix} — tiroir visuel {i+1}, repère à valider",
                 nodep=True) for i in range(count)]

facade("TS1", "TS1", "ensimage_bleu_gris", "TS1 — ENSIMAGE / FAÇADE BLEU-GRIS",
       SOURCE_TS1,
       "Reconstruction REVUE d'après les 15 photographies correctement classées. "
       "Sept zones visuelles, trames de tiroirs et couleur ajustées ; "
       "aucune cotation ni correspondance départ-tiroir certifiée.",
       brand="Façade métallique ancienne — fabricant non établi",
       cols=[
         dict(n="Ensemble de gauche", w=700, units=[
           dict(y=6, h=5, k="plate", label="ENSIMAGE — DISTRIBUTION", nodep=True,
                plate="black"),
           dict(y=23, h=8, k="arc", label="Avertissements photographiés"),
           dict(y=67, h=5, k="plate", label="RÉSERVE (panneau observé)",
                nodep=True, plate="yellow")
         ], doors=[(5,26),(26,54),(54,76)]),
         dict(n="N°6 (marquage manuscrit)", w=830,
              units=_tiroirs_ts1(6, 8, 10.5, "N°6"),
              doors=[(5,76)]),
         dict(n="N°1 (marquage manuscrit)", w=830,
              units=_tiroirs_ts1(6, 8, 10.5, "N°1"),
              doors=[(5,76)]),
         dict(n="N°2 / N°3 / N°5", w=830, units=[
           dict(y=11,h=18,k="drawer", label="N°2 — repère photo",
                nodep=True),
           dict(y=31,h=18,k="drawer", label="N°3 — repère photo",
                nodep=True),
           dict(y=51,h=18,k="drawer", label="N°5 — repère photo",
                nodep=True),
         ],doors=[(5,76)]),
         dict(n="Tiroirs centraux droits", w=740,
              units=_tiroirs_ts1(7, 8, 9, "Zone droite 1"),
              doors=[(5,76)]),
         dict(n="Tiroirs droits", w=740,
              units=_tiroirs_ts1(7, 8, 9, "Zone droite 2"),
              doors=[(5,76)]),
         dict(n="Commandes / tiroirs de droite", w=730,units=[
           dict(y=10,h=10,k="drawer",label="Commande 1 observée",nodep=True),
           dict(y=23,h=10,k="drawer",label="Commande 2 observée",nodep=True),
           dict(y=36,h=10,k="drawer",label="Commande 3 observée",nodep=True),
           dict(y=50,h=9,k="drawer",label="Commandes inférieures",nodep=True),
           dict(y=65,h=8,k="plate",label="REPÈRES NON ATTRIBUÉS",nodep=True)
         ],doors=[(5,76)]),
       ], note=("Source photographique corrigée (Ts1.zip IMG_3978-3992). "
                "Géométrie indicative par tronçon ; tiroirs sans destinations affectées."))

# Deux armoires Ensimage observees séparément mais leur attribution précise
# à chaque cliché reste non démontrée : pas de positionnements fictifs.
for suffix in ("A", "B"):
    bid = "ENSIM_" + suffix
    sub(bid, "Ensimage — armoire distincte " + suffix + " (repère à confirmer)",
        kind="Armoires", loc=None, loc_conf="inconnu",
        note="Armoire Ensimage distincte ; origine, nom réel, répartition des photos "
             "et fonctions des variateurs à vérifier. Le lot de photos transmis "
             "est MIXTE et comprend aussi des prises de vue TS8.")
    facade(bid, bid, "armoire_grise",
        "ENSIMAGE — ARMOIRE " + suffix + " / ATTRIBUTION NON VALIDÉE",
        SOURCE_ENSIM,
        "Gabarit non coté : impossibilité d'affecter de façon sûre les photos "
        "à l'armoire A ou B. Aucun tiroir ou branchement inventé.",
        brand="Identification terrain non établie", cols=[
            dict(n="Gabarit documentaire", w=860, units=[
                dict(y=8,h=6,k="plate",label="ARMOIRE " + suffix + " — À IDENTIFIER",
                     nodep=True),
                dict(y=42,h=6,k="plate",label="PHOTOS À RÉPARTIR / TIROIRS INCONNUS",
                     nodep=True)
            ],doors=[(6,75)])
        ],note="Façade provisoire non validée : sans départ assigné.")
    boards[bid]["photo_fidelity"] = "attribution_photo_non_resolue"
    boards[bid]["safety_warning"] = (
        "Armoire distincte, photographie exacte non associée : façade générique "
        "non validée, aucune connexion amont ni manœuvre autorisée.")
