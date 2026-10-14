"""Exporte le schema source vectoriel R112529 rev. H en planches A3 et A2.
Les decoupes sont des vues du document d'origine : elles ne corrigent pas ses ecarts.
"""
from io import BytesIO
from pathlib import Path
import fitz
from pypdf import PdfReader, PdfWriter

SITE = Path(__file__).resolve().parents[2]  # DISTRIBUTION-ELECTRIQUE
SOURCE = SITE / "Plan électrique" / "schema unifilaire 20 KV derniere version.pdf"
DEST = SITE / "OCC-ENERGIE" / "artifacts" / "unifilaire"
DEST.mkdir(parents=True, exist_ok=True)

# Coordonnees de la page A0 remise en paysage ; conserver les objets vectoriels.
REGIONS = [
    ("VUE GENERALE", "Poste de livraison, tableaux 20 kV, transformateurs, distribution 6 kV", (90,0,3110,2375)),
    ("POSTE DE LIVRAISON", "Arrivees EDF secours et CNR normale ; reperage documentaire", (1080,0,2310,420)),
    ("20 KV - S/STATION 1 - GAUCHE", "Troncons, cellules et transformateurs - vue gauche", (390,382,1750,1070)),
    ("20 KV - S/STATION 1 - DROITE", "Troncons, cellules et transformateurs - vue droite", (1640,382,3000,1070)),
    ("20 KV - S/STATION 2 - GAUCHE", "Cellules HTA et destinations - vue gauche", (390,1100,1700,1680)),
    ("20 KV - S/STATION 2 - DROITE", "Cellules HTA et destinations - vue droite", (1690,1100,2990,1680)),
    ("6 KV - FOUR 2", "Distribution 6 kV vers les armoires SPANG", (1140,1725,2395,2200)),
    ("CARTOUCHE ET REVISIONS", "Cartouche et identification du document original", (310,2190,3060,2380)),
]

def source_normalisee():
    reader = PdfReader(str(SOURCE))
    assert len(reader.pages) == 1, "Schema source attendu sur une page"
    page = reader.pages[0]
    page.transfer_rotation_to_content()
    writer = PdfWriter()
    writer.add_page(page)
    buffer = BytesIO()
    writer.write(buffer)
    return fitz.open(stream=buffer.getvalue(), filetype="pdf")

def exporter(fmt, src):
    width, height = fitz.paper_size(fmt.lower() + "-l")
    output = fitz.open()
    for number, (title, subtitle, area) in enumerate(REGIONS, 1):
        page = output.new_page(width=width, height=height)
        green = (.04, .58, .32)
        page.draw_rect(fitz.Rect(0, 0, width, 8), color=green, fill=green)
        page.insert_text((24, 37), "OCC ENERGIE / " + title, fontsize=16 if fmt == "A3" else 22, color=(.08,.22,.15))
        page.insert_text((24, 56), subtitle, fontsize=9.5 if fmt == "A3" else 12, color=(.3,.37,.33))
        page.show_pdf_page(fitz.Rect(24,71,width-24,height-42), src, 0,
                           clip=fitz.Rect(area), keep_proportion=True)
        page.draw_line((24,height-31),(width-24,height-31),color=(.7,.77,.72),width=.8)
        warning = "Source R112529 rev. H | Copie documentaire : verifier les connexions sur site"
        page.insert_text((24,height-17),warning,fontsize=8 if fmt == "A3" else 10)
        page.insert_text((width-90,height-17),f"{fmt} | {number}/{len(REGIONS)}",fontsize=8 if fmt == "A3" else 10)
    target=DEST / f"OCC_Energie_R112529_RevH_{fmt}_planches.pdf"
    output.set_metadata({"title":f"OCC Energie - Unifilaire {fmt} - R112529 rev H",
                         "subject":"Planches vectorielles de lecture"})
    output.save(str(target), garbage=4, deflate=True)
    check=fitz.open(str(target))
    assert len(check)==len(REGIONS), "Nombre de planches incorrect"
    assert all(int(p.rect.width)==int(width) for p in check), "Format papier incorrect"
    print(f"{target} : {len(check)} pages, {target.stat().st_size} octets")
    check.close()

def main():
    assert SOURCE.is_file(), f"Schema source absent : {SOURCE}"
    src=source_normalisee()
    assert src[0].rect.width > src[0].rect.height, "Source non normalisee"
    for fmt in ("A3","A2"):
        exporter(fmt,src)

if __name__=="__main__":
    main()
