"""SAP/compléments : tests de non-régression documentaires.
Aucune preuve de liaison électrique n'est ajoutée par le SAP.
"""
import json
from pathlib import Path

R = Path(__file__).resolve().parents[1]
s = json.loads((R / "sources" / "referentiel_sap_2026.json").read_text(encoding="utf-8"))
hist = json.loads((R / "sources" / "referentiel_excel_2024.json").read_text(encoding="utf-8"))
model = json.loads((R / "build" / "data.json").read_text(encoding="utf-8"))
t = s["tableaux"]
ids = {e["sap"] for e in t}
assert len(t) == 28 and len(ids) == 28
assert all(e["source_page"] == "SAP captures pages 4–5" for e in t)
assert all(e["statut"] in {"nouveau_repere", "facade_a_qualifier", "alias_a_confirmer", "deja_documente"} for e in t)
assert len([e for e in t if e["statut"] == "nouveau_repere"]) == 13
assert len([e for e in t if e["statut"] == "facade_a_qualifier"]) == 4
assert len(s["complements"]) == 17 and len(s["facades_a_qualifier"]) == 11
assert {r["repere"] for r in t if r["statut"] == "facade_a_qualifier"} == {"TS24", "TS28", "TS42", "TS43"}
assert next(r for r in t if r["sap"] == "98951")["statut"] == "alias_a_confirmer"
assert next(r for r in t if r["sap"] == "42947")["statut"] == "alias_a_confirmer"
assert len(hist["departIndex2024"]) == 36
assert "referentielSAP" not in model and "historique2024" not in model
assert len(model["edges"]) == 735, "Les liaisons du graphe ne doivent pas etre modifiees par un catalogue SAP"
assert len(model["boards"]) == 66, "Ne pas creer de TGBT/TS fictif via SAP"
assert (R / "src" / "complements.js").is_file()
src = (R / "src" / "app.js").read_text(encoding="utf-8")
builder = (R / "tools" / "build_app.py").read_text(encoding="utf-8")
assert "complements: vComplements" in src
assert "r.kind === 'sap'" in src
assert "src/complements.js" in builder and "referentiel_sap_2026.json" in builder
for filename in ("OCC_ENERGIE.html", "OCC_ENERGIE_TS8.html", "OCC_ENERGIE_VECTORIEL_MOBILE.html",
                 "OCC_ENERGIE_2024_LITE.html"):
    rendered = (R / filename).read_text(encoding="utf-8")
    assert '"referentielSAP":' in rendered, filename + " non regenere depuis les sources"
    assert "function vComplements(" in rendered, filename + " module absent"
assert (R / "OCC_ENERGIE_SAP_20261017_LITE.html").read_bytes() == (R / "OCC_ENERGIE_2024_LITE.html").read_bytes(), "La version SAP livrée doit suivre la reconstruction du mode léger"
print("OK : 28 SAP, 17 points, 11 façades candidates intégrés ; 66 tableaux / 735 liaisons inchangés")
