"""Non-régression : le simulateur ne doit plus attribuer à l'exploitant une interdiction générale de couplage.
Les garde-fous de simulation restent conservés jusqu'à qualification terrain.
Exécution : python tests/test_couplage_documentaire.py
"""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
app = (root / "src/app.js").read_text(encoding="utf-8")
readme = (root / "README.md").read_text(encoding="utf-8")

assert "règle exploitant) : jamais" not in app
assert "règle d'exploitation « jamais arrivée" not in app
assert "simulation bloquée par prudence" in app
assert "Conditions de parallélisme non validées" in app
assert "configuration avec deux arrivées et couplage fermés non qualifiée" in app
assert "aucune règle générale d’interdiction du couplage" in readme
assert "isClosed(qa.id) && isClosed(qb.id) && isClosed(qc.id)" in app
print("PASS: provenance corrigée et garde-fous de simulation préservés")
