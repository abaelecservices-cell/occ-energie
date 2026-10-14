"""Rapport des donnees manquantes : sortie CSV/Markdown, sans validation terrain."""
import csv
import json
from collections import defaultdict, Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "build" / "data.json"
DEST = ROOT / "artifacts" / "audit-parcours"

def get_model():
    data = json.loads(MODEL.read_text(encoding="utf-8"))
    assert all(k in data for k in ("boards", "nodes", "edges", "facades", "plans", "loc", "site"))
    return data

def facade_ids(data):
    result = defaultdict(set)
    for fid, f in data["facades"].items():
        for cell in f.get("cells", []):
            if cell.get("node"):
                result[cell["node"]].add(fid)
        for col in f.get("cols", []):
            for u in col.get("units", []):
                dep = u.get("dep") or u.get("node")
                if dep:
                    result[dep].add(fid)
    return result

def building(data, board):
    cursor, visited = board.get("loc"), set()
    while cursor and cursor in data["loc"] and cursor not in visited:
        visited.add(cursor)
        loc = data["loc"][cursor]
        if loc.get("bat") is not None:
            for z in data["site"].get("zones", []):
                if str(z.get("n")) == str(loc["bat"]):
                    return str(loc["bat"])
        cursor = loc.get("parent")
    return ""

def directed_from_sources(data):
    # Existence theorique du chemin dans le graphe dirige, pas mesure de tension.
    reverse = defaultdict(set)
    for e in data["edges"]:
        reverse[e["b"]].add(e["a"])
    connected = {n["id"] for n in data["nodes"] if n["t"] == "src"}
    previous = None
    while previous != len(connected):
        previous = len(connected)
        connected |= {nid for nid, ups in reverse.items() if ups & connected}
    return connected

def audit(data):
    boards = {b["id"]: b for b in data["boards"]}
    faces = facade_ids(data)
    reachable = directed_from_sources(data)
    plans = defaultdict(set)
    for p in data["plans"]:
        # PLAN_PDL est un schema de principe, pas un plan de salle.
        if p["id"] != "PLAN_PDL":
            for item in p.get("items", []):
                if item.get("ref"):
                    plans[item["ref"]].add(p["id"])
    rows = []
    for n in data["nodes"]:
        if n["t"] != "dep":
            continue
        b = boards.get(n.get("board")) or {}
        zone = building(data, b)
        facade = sorted(faces.get(n["id"], set()))
        plan = sorted(plans.get(b.get("id"), set()))
        loc_conf = b.get("loc_conf") or "inconnu"
        actions = []
        if n["id"] not in reachable:
            actions.append("Documenter la chaine amont")
        if loc_conf != "confirme":
            actions.append("Confirmer la localisation du tableau")
        if not zone:
            actions.append("Relever le batiment")
        if not plan:
            actions.append("Fournir le plan de local")
        if not facade:
            actions.append("Identifier la case sur la facade")
        if facade and not n.get("case"):
            actions.append("Confirmer le numero de case")
        if n.get("conf") != "confirme":
            actions.append("Verifier le repere et la source du depart")
        priority = "P1" if n["id"] not in reachable else "P2" if any(
            not x for x in (zone, plan, facade)) or loc_conf != "confirme" else "P3" if actions else "Aucune"
        rows.append({
            "Identifiant depart": n["id"], "Libelle": n.get("label", ""),
            "Identifiant tableau": b.get("id") or n.get("board") or "",
            "Tableau": b.get("name", ""), "Confiance depart": n.get("conf") or "inconnu",
            "Confiance localisation": loc_conf, "Batiment": zone,
            "Plan local": " | ".join(plan), "Facade": " | ".join(facade),
            "Case": str(n.get("case") or ""),
            "Chaine amont dirigee": "oui" if n["id"] in reachable else "non",
            "Priorite": priority, "Donnees manquantes": " | ".join(actions),
            "Source documentaire": n.get("src") or "",
        })
    assert rows, "Aucun depart present"
    assert len({row["Identifiant depart"] for row in rows}) == len(rows), "Doublon de depart"
    return rows

def write_report(data, dest=DEST):
    rows = audit(data)
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    with (dest / "DEPARTS_A_COMPLETER.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter=";")
        writer.writeheader()
        writer.writerows(rows)
    missing = {
        "Chaine amont non rattachee": lambda r: r["Chaine amont dirigee"] == "non",
        "Batiment non repere": lambda r: not r["Batiment"],
        "Plan de local non associe": lambda r: not r["Plan local"],
        "Depart non positionne en facade": lambda r: not r["Facade"],
        "Numero de case non renseigne": lambda r: not r["Case"],
        "Localisation non confirmee": lambda r: r["Confiance localisation"] != "confirme",
    }
    lines = ["# OCC Energie : lacunes documentaires de localisation et de tracage",
             "", "Source exclusive : build/data.json. Ce rapport ne certifie pas l'installation reelle.",
             "", f"Nombre de departs indexes : **{len(rows)}**.", "",
             "| Categorie | Departs |", "|---|---:|"]
    for label, predicate in missing.items():
        lines.append(f"| {label} | {sum(bool(predicate(row)) for row in rows)} |")
    lines += ["", "Le CSV contient le detail par depart, le tableau et la source documentaire.",
              "Batiment : seulement quand une zone du plan existe pour la localisation.",
              "Plan : uniquement lorsque le tableau est explicitement reference dans le plan local.",
              "Facade : uniquement quand un objet de facade pointe vers l'identifiant du depart.",
              "Amont : seulement les aretes orientees du modele ; couplages et etat reels non verifies.",
              "Les identifiants probables ou inconnus restent a confirmer avant intervention.",
              "Ces nombres signalent des besoins documentaires, et ne mesurent pas la fiabilite physique."]
    (dest / "SYNTHESE.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("Rapport de completude :", len(rows), "departs ; fichier", str(dest))
    return rows

if __name__ == "__main__":
    write_report(get_model())
