"""Contrôles de non-régression : façade vectorielle uniquement et arborescence complète.
Usage : python tests/test_vector_only.py
"""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
app = (root / "src/app.js").read_text(encoding="utf-8")
tree = (root / "src/arbre.js").read_text(encoding="utf-8")

for forbidden in ("Voir la photo", "id=\"phbtn\"", "PHOTO_BASE",
                  "photoLinks(", "['p', 'Photos']", "BTAB === 'p'"):
    assert forbidden not in app, f"Accès photographique encore visible : {forbidden}"

for expected in ("b.vector_placeholder = true", "Gabarit vectoriel NON COTÉ",
                 "Façade vectorielle", "['o', 'Documents']",
                 "Géométrie inconnue"):
    assert expected in app, f"Affichage vectoriel incomplet : {expected}"

assert "function arbreDepLeaves(" in tree
assert "arbreDepLeaves(bid, null)" in tree
assert "arbreDepLeaves(b.id, null)" in tree
assert "arbreDepLeaves(bid, h === 'A'" in tree
assert "arbreDepLeaves(bid, h === 'B'" not in tree  # regroupement A/B dans expression unique
print("PASS : photothèque masquée, gabarits prudents, départs présents dans l'arbre.")
