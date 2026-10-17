"""Contrôle anti-régression des tuiles haute résolution de OCC Energie.

Le HTML complet est un livrable offline avec le dossier assets adjacent ;
la version Lite est un monofichier sans niveau 12.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def html_data(name):
    source = (ROOT / name).read_text(encoding="utf-8")
    match = re.search(r'<script>window\.OCC_DATA=(.*?);</script>', source, re.DOTALL)
    assert match, f"Données embarquées introuvables : {name}"
    return json.loads(match.group(1)), source


for filename in ("OCC_ENERGIE.html", "OCC_ENERGIE_TS8.html", "OCC_ENERGIE_VECTORIEL_MOBILE.html"):
    data, html = html_data(filename)
    assert len(data["boards"]) == 66 and len(data["edges"]) == 735
    assert len(data["referentielSAP"]["tableaux"]) == 28
    assert "function vComplements(" in html
    deep = {k: v for k, v in data["site"]["tiles"].items() if k.startswith("12/")}
    assert len(deep) == 22, f"22 tuiles attendues dans {filename}"
    for key, image_path in deep.items():
        assert image_path == f"assets/ts8_site_tiles/{key}.webp", (filename, key, image_path)
        photo = ROOT / image_path
        assert photo.is_file(), f"Tuile introuvable : {photo}"
        with photo.open("rb") as file:
            header = file.read(12)
        assert header[:4] == b"RIFF" and header[8:12] == b"WEBP", photo

for filename in ("OCC_ENERGIE_2024_LITE.html", "OCC_ENERGIE_SAP_20261017_LITE.html"):
    data, html = html_data(filename)
    assert len(data["boards"]) == 66 and len(data["edges"]) == 735
    assert len(data["referentielSAP"]["tableaux"]) == 28
    assert "function vComplements(" in html
    assert not any(k.startswith("12/") for k in data["site"]["tiles"])

print("OK : 22 tuiles WEBP locales pour les HTML complets, monofichier lite et SAP conservés")
