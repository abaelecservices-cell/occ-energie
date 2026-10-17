"""Régression JavaScript — les listes DOM doivent employer $$ (querySelectorAll).

Évite les TypeError dans les écrans plans, courants, arborescence et historique.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
required = {
    "src/plans.js": ["$$('.tile[data-zone]').forEach"],
    "src/plansvg.js": ["$$('[data-p]').forEach"],
    "src/courant.js": ["$$('[data-mosim]').forEach"],
    "src/arbre.js": [
        "$$('.tnode', host)",
        "$$('.tnode', n).some",
        "$$('.tnode', n).forEach",
        "$$('details.tnode', host).forEach",
    ],
    "src/historique2024.js": ["$$('.hx24entry', $('#hx24-list')).forEach"],
}
for filename, good_patterns in required.items():
    src = (ROOT / filename).read_text(encoding="utf-8")
    for good in good_patterns:
        assert good in src, f"{filename}: sélecteur multiple absent: {good}"
        bad = good.replace("$$(", "$(", 1)
        assert bad not in src, f"{filename}: querySelector au lieu de querySelectorAll: {bad}"
print("OK : sélecteurs DOM de collection (plans, simulation, arbre, historique)")
