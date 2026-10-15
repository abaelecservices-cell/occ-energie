"""Contrôles non destructifs du lot photographique 15/10/2026.
Usage : python tests/test_terrain_20261015.py (après build_data.py).
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent.parent
data = json.loads((ROOT / "build/data.json").read_text(encoding="utf-8"))
boards = {b["id"]: b for b in data["boards"]}
facades = data["facades"]
nodes = {n["id"]: n for n in data["nodes"]}
assert len(nodes) == len(data["nodes"]), "ID de noeud dupliqué"
assert len(boards) == len(data["boards"]), "ID de tableau dupliqué"

expected = {
    "TS15": ("Ts 15.zip", 25),
    "TS16": ("Ts 16(1).zip", 16),
    "TGBT2": ("Tgbt 2.zip", 11),
    "TGBT6": ("Tgbt 6(1).zip", 13),
    "TGBT9": ("Tgbt 9.zip", 30),
    "KV6": ("Tableau 6kv.zip", 22),
    "GORGE": ("Gorge.zip", 11),
    "BRONZINI": ("Bronzini.zip", 8),
    "VARIVOLT": ("Varivolt.zip", 13),
    "COND6A": ("Onduleur 6 a.zip", 4),
}
assert sum(n for _, n in expected.values()) == 153

for bid, pair in expected.items():
    board = boards[bid]
    photos = board.get("photo_terrain", [])
    assert any((p["archive"], p["nb"]) == pair for p in photos), (bid, "source manquante")
    assert any(not p["importe"] for p in photos), (bid, "import binaire annoncé sans preuve")

for bid in ["TS15", "TS16", "GORGE", "VARIVOLT"]:
    assert boards[bid].get("facade") == bid, (bid, "façade non enregistrée")
    assert facades[bid]["cols"], (bid, "façade vide")
    assert "15/10/2026" in facades[bid]["src"], (bid, "pas de traçabilité du relevé")

for bid in ["TS15", "TS16"]:
    for col in facades[bid]["cols"]:
        for u in col["units"]:
            if "dep" in u or "node" in u:
                nid = u.get("dep") or u.get("node")
                assert nid in nodes, (bid, "appareil inconnu", nid)
                assert nodes[nid].get("board") == bid, (bid, "mauvais tableau", nid)
assert "BATTERIE CONDENSATEUR 6A" in boards["COND6A"]["note"]
assert not any("Onduleur 6 a.zip" in (p.get("archive") or "")
               for b in data["boards"] if b["id"].startswith("OND")
               for p in b.get("photo_terrain", [])), "Erreur de classement des photos"

for edge in data["edges"]:
    assert edge["a"] in nodes and edge["b"] in nodes, ("liaison vers noeud absent", edge)
print("PASS : 153 photos cataloguées, 4 façades, références internes et graphe cohérents.")
