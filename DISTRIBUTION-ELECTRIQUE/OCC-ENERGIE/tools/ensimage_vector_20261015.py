"""Ensimage : façades vectorielles sans photographie dans l'application.
Sources : relevé TS1 (IMG_3967 à 3977) et relevé deux armoires distinctes (15/10/2026).
Aucun appareil, câble, départ, alimentation ni jonction n'est inféré des images.
Exécuté après facades_photo.py et les modules de relevés terrain.
"""

SOURCE_TS1 = "Relevé terrain TS1 15/10/2026 — IMG_3967 à IMG_3977"
SOURCE_ENSIM = "Relevé terrain Ensimage 15/10/2026 — deux armoires distinctes, identification à reprendre"

# TS1 photographié : ensemble beige, bandeau ventilé en tête, plusieurs portes,
# commande modulaire sur un tronçon et instrumentations sur un autre.
# Nombre exact de travées, cotes et positions des 34 départs : NON CERTIFIÉS.
boards["TS1"]["note"] = ((boards["TS1"].get("note") or "") +
    " Relevé 15/10/2026 : vue générale de rangées de portes claires,"
    " bandeau ventilé, une zone commandes avec voyants et instruments."
    " La façade vectorielle est volontairement schématique ; aucune"
    " des 34 destinations Excel n'est localisée physiquement par déduction.")
facade("TS1", "TS1", "okken_beige", "TS1 — ENSIMAGE", SOURCE_TS1,
    "Tronçons apparents vectorisés : disposition indicative, largeurs, nombre exact de colonnes et positions des départs non validés. Aucun tiroir affecté par simple proximité.",
    brand="Ensemble beige — constructeur non confirmé", cols=[
        dict(n="Commandes observées", w=660, units=[
            dict(y=13, h=7, k="meter", label="Indications de commande observées"),
            dict(y=25, h=6, k="voy2", label="Voyants observés"),
            dict(y=38, h=5, k="sel", label="Sélecteur observé"),
            dict(y=54, h=5, k="plate", label="REPÈRES À RELEVER", nodep=True),
        ], doors=[(7, 74)]),
        dict(n="Panneaux visibles — groupe 1", w=740, units=[
            dict(y=36, h=7, k="plate", label="DÉPARTS NON POSITIONNÉS", nodep=True),
        ], doors=[(6, 75)]),
        dict(n="Panneaux visibles — groupe 2", w=740, units=[], doors=[(6, 75)]),
        dict(n="Panneaux visibles — groupe 3", w=740, units=[], doors=[(6, 75)]),
        dict(n="Mesures et sectionnement observés", w=740, units=[
            dict(y=22, h=9, k="meter", label="Centrale de mesure visible"),
            dict(y=42, h=7, k="plate", label="AFFICHAGES / FONCTIONS À RELEVER", nodep=True),
        ], doors=[(6, 75)]),
    ], note="Schéma de façade documentaire, non coté ; la liste des départs demeure dans Départs et Arborescence.")

# Les deux ensembles d'ensimage vus sur photos doivent rester DEUX tableaux.
# Attribution des photographies, séries de tiroirs, variateurs et circuits aux
# armoires A ou B non établie ; ne jamais associer par défaut au TS8.
for suffix in ("A", "B"):
    bid = "ENSIM_" + suffix
    sub(bid, "Ensimage — armoire distincte " + suffix + " (repère à confirmer)",
        kind="Armoires", loc=None, loc_conf="inconnu",
        note="Armoire ensimage distincte ; origine, tableau source, câbles, nom réel,"
             " répartition des photos et fonctions des variateurs à vérifier."
             " Sans raccordement électrique inventé.")
    facade(bid, bid, "armoire_grise",
        "ENSIMAGE — ARMOIRE " + suffix + " / IDENTIFICATION PROVISOIRE",
        SOURCE_ENSIM,
        "Gabarit de représentation uniquement : dessins des tiroirs moteurs et variateurs à attribuer à la bonne armoire avant implantation. Aucun dispositif représenté comme certifié.",
        brand="Identification constructeur à relever", cols=[
            dict(n="Panneau documentaire (non coté)", w=860, units=[
                dict(y=8, h=6, k="plate", label="ARMOIRE " + suffix + " — À IDENTIFIER", nodep=True),
                dict(y=40, h=6, k="plate", label="POSITIONS DES TIROIRS INCONNUES", nodep=True),
            ], doors=[(6, 75)]),
        ], note="Gabarit vectoriel sans départs attribués ni liaison amont ; aucune photographie affichée.")
    boards[bid]["safety_warning"] = (
        "Tableau et départs amont non identifiés ; aucune position ou manœuvre"
        " n'est validée à partir des seules photographies.")
