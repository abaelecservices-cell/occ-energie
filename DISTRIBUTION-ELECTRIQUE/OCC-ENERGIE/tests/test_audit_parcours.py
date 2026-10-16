"""Regression pour l'inventaire documentaire des depart : pas d'inference de positions."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from audit_parcours import audit, get_model, write_report  # noqa: E402


def fixture():
    return {
        "boards": [
            {"id": "T1", "name": "Tableau 1", "loc": "S1", "loc_conf": "confirme"},
            {"id": "T2", "name": "Tableau 2", "loc_conf": "inconnu"},
        ],
        "nodes": [
            {"id": "SRC", "t": "src", "label": "Source"},
            {"id": "D1", "t": "dep", "board": "T1", "label": "Depart A",
             "case": "2-13", "conf": "confirme", "src": "photo"},
            {"id": "D2", "t": "dep", "board": "T2", "label": "Depart B",
             "conf": "inconnu"},
        ],
        "edges": [{"a": "SRC", "b": "D1"}],
        "facades": {"F1": {"cells": [{"node": "D1"}], "cols": []}},
        "loc": {"S1": {"name": "Salle", "parent": None, "bat": 42}},
        "plans": [{"id": "P1", "items": [{"ref": "T1"}]},
                  {"id": "PLAN_PDL", "items": [{"ref": "T2"}]}],
        "site": {"zones": [{"n": 42, "label": "Bâtiment A"}]},
    }


def main():
    rows = audit(fixture())
    assert len(rows) == 2
    d1, d2 = rows
    assert d1["Batiment"] == "42" and d1["Facade"] == "F1"
    assert d1["Plan local"] == "P1" and d1["Chaine amont dirigee"] == "oui"
    assert not d1["Donnees manquantes"]
    assert d2["Batiment"] == "" and d2["Facade"] == ""
    assert d2["Plan local"] == ""  # plan de principe != plan de local
    assert d2["Chaine amont dirigee"] == "non"
    # Sur les donnees reelles aucune valeur de position ne doit etre fabriquee.
    data = get_model()
    real = audit(data)
    assert len(real) == sum(n["t"] == "dep" for n in data["nodes"])
    assert all(row["Confiance localisation"] in (
        "confirme", "probable", "a_verifier", "inconnu") for row in real)
    assert all(row["Priorite"] in ("P1", "P2", "P3", "Aucune") for row in real)
    # Les formulaires terrain pre-remplissent seulement les reperes deja documentes.
    from tempfile import TemporaryDirectory
    import csv
    with TemporaryDirectory() as d:
        from audit_parcours import write_report
        write_report(fixture(), d)
        out = Path(d)
        names = ["FACADES_MANQUANTES_RELEVE_TERRAIN.csv",
                 "CASES_A_IDENTIFIER_TERRAIN.csv",
                 "CHECKLIST_TOUR_TERRAIN.md"]
        assert all((out / name).exists() for name in names)
        with (out / names[0]).open(encoding="utf-8-sig", newline="") as h:
            boards_to_visit = list(csv.DictReader(h, delimiter=";"))
        assert len(boards_to_visit) == 2, "Les deux tableaux sans facade sont attendus"
        assert all(not r["Batiment a relever"] for r in boards_to_visit)
        assert all(r["Statut de verification"] == "A RELEVER" for r in boards_to_visit)
        with (out / names[1]).open(encoding="utf-8-sig", newline="") as h:
            cases_to_visit = list(csv.DictReader(h, delimiter=";"))
        assert len(cases_to_visit) == 1, "Seul D2 manque de facade et de case"
        assert all(not r["Case relevee"] and not r["Etiquette lue exactement"]
                   for r in cases_to_visit)

    print(f"Tests complétude OK : {len(real)} départs")


if __name__ == "__main__":
    main()
