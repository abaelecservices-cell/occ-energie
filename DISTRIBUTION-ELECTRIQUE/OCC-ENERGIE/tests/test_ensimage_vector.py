"""Vérifie que le relevé ensimage n'invente pas de raccordement.
Lancer après outils/build_data.py.
"""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
d = json.loads((root / "build/data.json").read_text(encoding="utf-8"))
boards = {b["id"]: b for b in d["boards"]}
nodes = {n["id"]: n for n in d["nodes"]}

assert boards["TS1"]["facade"] == "TS1"
assert d["facades"]["TS1"]["cols"]
for bid in ("ENSIM_A", "ENSIM_B"):
    assert bid in boards
    assert boards[bid]["facade"] == bid
    assert d["facades"][bid]["cols"]
    assert "Gabarit" in d["facades"][bid]["conf"]
    assert boards[bid]["loc_conf"] == "inconnu"
    assert not any(x["a"] == bid + "_J" or x["b"] == bid + "_J" for x in d["edges"])
    assert not any(n.get("board") == bid and n["t"] == "dep" for n in d["nodes"])
    assert nodes[bid + "_J"]["t"] == "bus"
assert boards["TS8"]["facade"] == "TS8"
print("PASS : TS1 vectoriel et deux armoires ensimage sans arêtes inventées.")
