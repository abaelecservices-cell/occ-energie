"""Contrôles de non-régression de la reconstruction photographique TS8."""
import json
from pathlib import Path

R = Path(__file__).resolve().parents[1]
d = json.loads((R / "build/data.json").read_text(encoding="utf-8"))
boards = {b["id"]: b for b in d["boards"]}
nodes = {n["id"]: n for n in d["nodes"]}
ts8 = boards["TS8"]
f = d["facades"]["TS8"]
assert ts8["facade"] == "TS8"
assert [x["n"] for x in f["cols"] if x["n"]] == ["1", "2", "3", "4"]
assert len([u for u in f["cols"][0]["units"] if u["k"] == "drawer"]) == 5
assert len([n for n in d["nodes"] if n.get("board") == "TS8" and n["t"] == "dep"]) == 20
labels = [n["label"].upper() for n in d["nodes"] if n.get("board") == "TS8"]
for label in ("7PM02", "4P062", "ES02", "ES05", "7PM01"):
    assert any(label in l for l in labels), label
assert "AMONT DU DISJONCTEUR PRINCIPAL" in ts8["safety_warning"]
assert any(i["id"] == "I-TS8-AMONT" and i["sev"] == "haute" for i in d["issues"])
# Le même départ documenté TGBT4 1-23 alimente le jeu de barres TS8.
up = [e["a"] for e in d["edges"] if e["b"] == "TS8_J"]
assert len(up) == 1, up
assert nodes[up[0]]["board"] == "TGBT4"
assert nodes[up[0]]["case"] == "1-23"
# Aucun disjoncteur de tête fictif qui rendrait tous les circuits hors tension.
assert "TS8_QMAIN" not in nodes
# Les étiquettes non liées ne doivent pas générer de départs.
assert not any(u.get("dep") for u in f["cols"][0]["units"] if "REPÈRE NON LU" in u.get("label", ""))
print("TS8 OK : façade, 20 départs préservés, alimentation et alerte vérifiées.")
