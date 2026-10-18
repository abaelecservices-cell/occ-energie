"""Vérification documentaire OCC Energie du 17/10/2026.

Aucun test ne certifie la connexion physique ni les manœuvres.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
meta = json.loads((ROOT / "sources" / "corrections_documentaires_20261017.json").read_text(encoding="utf-8"))
hist = json.loads((ROOT / "sources" / "referentiel_excel_2024.json").read_text(encoding="utf-8"))
rows = {r["ligneExcel"]: r for r in hist["departIndex2024"]}

assert meta["do_not_update_graph"] is True
assert len(rows) == 36
assert rows[23]["tgbt"] == 2 and rows[23]["colonne"] == 6 and rows[23]["case"] == "18" and rows[23]["ts"] == "TS2B"
assert rows[30]["tgbt"] == 4 and rows[30]["colonne"] == 2 and rows[30]["case"] == "10" and rows[30]["ts"] == "TS24A"
assert rows[38]["tgbt"] == 4 and rows[38]["colonne"] == 7 and rows[38]["case"] == "10" and rows[38]["ts"] == "TS24A"
assert sum(x["count"] for x in meta["reclassifications"]) == 26
assert sorted((x["original_label"], x["correct_board"]) for x in meta["reclassifications"]) == [("TS1", "TS8"), ("TS8", "TS1")]
assert meta["missing_image_recovered_locally"]["filename"] == "IMG_3966.jpeg"
assert meta["missing_image_recovered_locally"]["not_yet_in_git"] is True
assert meta["corrections_excel2024"]["TS42_TS43_cases"]["status"] == "concordance_documentaire_de_position"
print("OK : anomalies historiques et reclassement photos tracés, sans modifier le graphe actif")
