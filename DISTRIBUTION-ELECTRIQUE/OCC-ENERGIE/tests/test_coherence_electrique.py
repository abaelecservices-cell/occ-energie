
"""Tests de coherence documentaire OCC Energie.

Ce test verifie le modele de donnees.
Il ne certifie pas les connexions physiques de l'usine.
"""

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "build" / "data.json"

errors = []


def erreur(message):
    errors.append(message)


def indexer(elements, nom):
    ids = [x.get("id") for x in elements]
    doublons = [
        ident for ident, nombre in Counter(ids).items()
        if nombre > 1
    ]
    for ident in doublons:
        erreur(f"{nom} duplique : {ident}")
    return {x["id"]: x for x in elements if x.get("id")}


def liaison_existe(a, b, edges):
    return any(
        e.get("a") == a and e.get("b") == b
        for e in edges
    )


def tester():
    if not DATA.is_file():
        raise SystemExit("ERREUR : build/data.json absent")

    data = json.loads(DATA.read_text(encoding="utf-8"))

    for cle in ("nodes", "edges", "boards", "issues"):
        if not isinstance(data.get(cle), list):
            raise SystemExit(f"Structure invalide : {cle}")

    nodes = indexer(data["nodes"], "Equipement")
    boards = indexer(data["boards"], "Tableau")
    edges = data["edges"]

    confiance = {
        "confirme", "probable", "a_verifier", "inconnu"
    }

    # Integrite des equipements
    for ident, node in nodes.items():
        board = node.get("board")
        if board and board not in boards:
            erreur(f"{ident} : tableau inexistant {board}")

        conf = node.get("conf")
        if conf is not None and conf not in confiance:
            erreur(f"{ident} : confiance invalide {conf}")

    # Integrite des liaisons du graphe
    for i, edge in enumerate(edges):
        a, b = edge.get("a"), edge.get("b")

        if a not in nodes:
            erreur(f"Liaison {i} : origine inconnue {a}")
        if b not in nodes:
            erreur(f"Liaison {i} : destination inconnue {b}")

        conf = edge.get("conf")
        if conf is not None and conf not in confiance:
            erreur(f"Liaison {i} : confiance invalide {conf}")

    # Coherence du modele TR1 / TR2
    correspondances = {
        "TR1A": "TGBT1_QA",
        "TR1B": "TGBT1_QB",
        "TR2A": "TGBT2_QA",
        "TR2B": "TGBT2_QB",
    }

    for transfo, arrivee in correspondances.items():
        if transfo not in nodes:
            erreur(f"Transformateur absent : {transfo}")
        elif nodes[transfo].get("t") != "tr":
            erreur(f"Type incorrect : {transfo}")

        if arrivee not in nodes:
            erreur(f"Arrivee absente : {arrivee}")
        elif not liaison_existe(transfo, arrivee, edges):
            erreur(f"Liaison manquante : {transfo} -> {arrivee}")

    # Detecter une inversion dans le modele
    inversions = [
        ("TR1A", "TGBT2_QA"),
        ("TR2A", "TGBT1_QA"),
    ]

    for a, b in inversions:
        if liaison_existe(a, b, edges):
            erreur(f"Inversion potentielle : {a} -> {b}")

    # Anomalies documentaires connues
    alertes = {
        "I-TR12": "Destinations TR1A / TR2A a confirmer",
        "I-SSNUM": "Numerotation des sous-stations",
        "I-TGBT3-LOCK": "Verrouillages TGBT3 a verifier",
        "I-TS17": "Origine TS17 / TS9 a confirmer",
    }

    ids_issues = {
        issue.get("id") for issue in data["issues"]
    }

    for ident, message in alertes.items():
        if ident in ids_issues:
            print(f"DOCUMENTATION A VERIFIER : {message}")

    print(f"Equipements : {len(nodes)}")
    print(f"Tableaux : {len(boards)}")
    print(f"Liaisons : {len(edges)}")
    print(f"Anomalies documentaires : {len(data['issues'])}")

    if errors:
        for message in errors:
            print("ERREUR :", message)
        raise SystemExit(
            f"Echec : {len(errors)} incoherence(s) detectee(s)"
        )

    print("OK : coherence structurelle du modele")


if __name__ == "__main__":
    tester()
