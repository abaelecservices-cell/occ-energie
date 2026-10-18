"""OCC Energie — statut de fidelite visuelle par facade, controle 18/10/2026.

Portee :
- 267 JPEG presents dans les 18 groupes du ZIP de phototheque corrigee ;
- 41 planches revues visuellement, dont les images sources TS1/TS8 en detail ;
- aucune certification de cote, position de protection, cable ou depart ;
- les photos des armoires A/B Ensimage sont melangees a d'autres panneaux ;
- les photographies des armoires aval des tours ne sont pas celles des
  facades des tableaux TS17A / TS17B.
N'ajoute/modifie AUCUN noeud, depart, arete ni regle de manoeuvre.
"""
PHOTO_SOURCES_1810 = {
  "TGBT2": ("Tgbt 2.zip", 11, "TGBT2 / cases et demi-travées à comparer au plan constructeur"),
  "TGBT6": ("Tgbt 6(1).zip", 13, "Arrivées, départs sous vitre et zones de mesure à recouper"),
  "TGBT7": ("Tgbt 7.zip", 30, "Photos de façade et compartiments intérieurs ; ordre des colonnes à confirmer"),
  "TGBT9": ("Tgbt 9.zip", 30, "Deux arrivées et couplage ; étiquettes des départs incomplètes"),
  "KV6": ("Tableau 6kv.zip", 22, "Cellules et ordre L1-L6 non certifiés"),
  "TS15": ("Ts 15.zip", 25, "Bande de tiroirs et portes vues ; dispositions fines à vérifier"),
  "TS16": ("Ts 16(1).zip", 16, "Trois zones visibles ; associations de commande à vérifier"),
  "TS9": ("Ts9.zip", 12, "Zones et rangées de commandes visibles ; associations de protection à vérifier"),
  "BRONZINI": ("Bronzini.zip", 8, "Deux armoires/panneaux Schneider et rangées d'appareils"),
  "GORGE": ("Gorge.zip", 11, "Trois modules gris côte à côte visibles"),
  "VARIVOLT": ("Varivolt.zip", 13, "Deux armoires distinctes, deux afficheurs chacune"),
  "COND6A": ("Onduleur 6 a.zip (nom trompeur)", 4, "Batterie condensateurs TR6A, PAS onduleur"),
  "TS17": ("Tour aéro.zip / Ts17A.zip et Ts17b.zip", 14,
           "Photos des QUATRE armoires AVAL des tours, non façades TS17A/B"),
  "TS1": ("Ts1.zip", 15,
          "IMG_3978-3992 : sept zones visibles, métallique bleu-gris"),
  "TS8": ("Ts8.zip", 12,
          "IMG_3966-3977 : beige, 4 travées, 5 tiroirs dans travée gauche"),
  "ENSIM_A": ("Dossier ensimage hétérogène", 18,
              "Ne permet PAS d'attribuer chaque cliché à cette armoire"),
  "ENSIM_B": ("Dossier ensimage hétérogène", 18,
              "Ne permet PAS d'attribuer chaque cliché à cette armoire"),
}

for _bid, _b in boards.items():
    if not _b.get("facade"):
        continue
    _src = PHOTO_SOURCES_1810.get(_bid)
    if _src:
        _archive, _count, _detail = _src
        _b["controle_photo"] = dict(
          statut="a_valider_visuellement",
          archive=_archive, photo_count=_count, constat=_detail,
          revision="18/10/2026",
          mention="Référence photographique contrôlée ; fidélité fine NON CERTIFIÉE")
    else:
        _b["controle_photo"] = dict(
          statut="source_photo_absente_du_lot_267",
          archive="anciens plans, PDF et archives à rapprocher",
          photo_count=0,
          constat="Façade non comparée de bout en bout aux sources originales",
          revision="18/10/2026",
          mention="Contrôle visuel incomplet ; ne pas présenter comme conforme.")
    _b["controle_photo"]["manoeuvre_autorisee"] = False
    _b["controle_photo"]["cote_certifiee"] = False

for _bid, _reason in (
    ("TS1", "Reconstruction antérieure ERRONÉE (beige, 5 tronçons). "
            "Correction source : dessin bleu-gris à 7 zones visuelles sur IMG_3990. "
            "Aucune case ni liaison de tiroir validée."),
    ("TS8", "Photo source antérieure mélangée avec TS1. "
            "Correspondance générale sur IMG_3966 et IMG_3974 ; 5 tiroirs et "
            "numérotation 1-4 observés, calibres et positions physiques non cotés."),
    ("ENSIM_A", "Lot photo Ensimage MELANGÉ (certaines vues représentent TS8). "
                "L'armoire A n'est pas reliée à un cliché unique."),
    ("ENSIM_B", "Lot photo Ensimage MELANGÉ (certaines vues représentent TS8). "
                "L'armoire B n'est pas reliée à un cliché unique."),
    ("TS17", "Les 14 JPG du lot TS17/tours montrent quatre armoires AVAL, "
             "pas la façade des TS17A et TS17B. Les PDF TS17 restent la source."),
):
    if _bid in boards and boards[_bid].get("controle_photo"):
        boards[_bid]["controle_photo"]["constat"] = _reason
        boards[_bid]["controle_photo"]["statut"] = (
            "reconstruction_corrigee_a_certifier" if _bid=="TS1"
            else "identification_source_non_validee" if _bid in ("ENSIM_A","ENSIM_B")
            else "correspondance_partielle_a_confirmer")

