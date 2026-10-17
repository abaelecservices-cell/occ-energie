"""Relevé détaillé de l'unifilaire 20 kV (R112529 rév. H), lu à 320 % tuile par tuile (11/10/2026).
Exécuté par build_data.py (accès à nodes, edges, boards, F, N, E, ISSUE, UNI).

Pour chaque cellule : n° de schéma Schneider (Sch.), repère, rapport de TC retenu (valeur soulignée / encadrée sur le plan), tenue ITH,
relais et réglages, câble, clés d'interverrouillage (nom, code, emplacement, état dessiné).
Pour chaque transformateur : couplage, neutre, surveillance, disjoncteur BT, clés BT, destination écrite sur le plan.

États de clés dessinés (convention Schneider, légende absente du plan) : « ● » clé prisonnière, « ○ » clé libre, « Ø » clé absente.
"""
K = lambda name, code, where, st: dict(name=name, code=code, where=where, st=st)
P = '●'; L = '○'; A = 'Ø'
SS1C = 'Unifilaire — tableau « S/STATION 1 - 20KV » (Sous-station 2 du plan d’implantation)'
SS2C = 'Unifilaire — tableau « S/STATION 2 - 20KV » (Sous-station 1 du plan d’implantation)'

CELLS = {
 # ----------------------------------------------------------- poste de livraison
 'PL_A04': dict(sch='3182344', rep='04', cell='CS-400A', tc='400/5-5A — 7,5 VA cl 0,1 / 5 VA 5P15 — 12,5 kA 1 s', relay='S2036 (S03)',
     settings='I> 440 A SIT 1,5 s à 10 Is · I>> 600 A DT 0,65 s · Io 30 A DT 0,65 s', device='Disjoncteur SF1 400 A 24 kV 12,5 kA — commande RI Sch. 889240 — armement 110 V CC — déclencheur à manque de tension 24 V CC — fermeture 24 V CC',
     keys=[K('A', '', 'boîte de clés en tête de la cellule A', P), K('04', '', 'interrupteur-sectionneur amont', P), K('04', '', 'disjoncteur (verrouillage ouvert)', A), K('A', '', 'sectionneur de terre amont', L), K('A1', '', 'sectionneur de terre aval / câble vers SS', L)],
     cable='Liaisons câbles (pointillés) vers les arrivées A1 (tableau TR 1-6) et A3 (tableau TR 7/9)'),
 'PL_B01': dict(sch='3182346', rep='01', cell='CS-400A', tc='400/5-5A — 7,5 VA cl 0,1 / 5 VA 5P15 — 12,5 kA 1 s', relay='S2036 (S03)',
     settings='I> 440 A SIT 1,5 s à 10 Is · I>> 600 A DT 0,65 s · Io 30 A DT 0,65 s', device='Disjoncteur SF1 400 A 24 kV 12,5 kA — commande RI Sch. 889240 — armement 110 V CC — déclencheur à manque de tension 24 V CC — fermeture 24 V CC',
     keys=[K('B', '', 'boîte de clés en tête de la cellule B', P), K('01', '', 'interrupteur-sectionneur amont', P), K('01', '', 'disjoncteur (verrouillage ouvert)', A), K('B', '', 'sectionneur de terre amont', L)],
     cable='Liaisons câbles vers les arrivées A2 (tableau TR 1-6) et A4 (tableau TR 7/9)'),
 # ----------------------------------------------------------- tableau 20 kV TR 1 à 6
 'SS1_C6A': dict(sch='3298882', rep='010', tc='50-100/5-5A (calibre non marqué) — 7,5 VA cl 0,5 / 5 VA 5P15 — ITH 25 kA 1 s', relay='S2036 (T14)', settings='I> 70 A SIT 2 s à 10 Is · I>> 500 A DT 0,4 s · Io 20 A DT 0,4 s',
     device='Disjoncteur SF1 400 A 24 kV 12,5 kA — CDE RI Sch. 888461F — décl. fermeture / ouverture 110 V CC — motoréducteur 110 V CC', cable='E00.107 — 3 × 70 mm² Cu',
     keys=[K('010', '618670', 'interrupteur-sectionneur', P), K('010', '618670', 'disjoncteur', A), K('010', '618670', 'sectionneur de terre', L), K('01', '619559', 'sectionneur de terre aval', L)]),
 'SS1_C5A': dict(sch='(non indiqué)', rep='010', tc='50-100/5-5A (calibre non marqué) — ITH 25 kA 1 s', relay='S2035 (T14)', settings='I> 55 A SIT 2 s à 10 Is · I>> 500 A DT 0,4 s · Io 20 A DT 0,4 s',
     device='Disjoncteur SF1 400 A 24 kV — CDE RI Sch. 888461F', cable='E00.107 — 3 × 70 mm² Cu',
     keys=[K('010', '263570', 'interrupteur-sectionneur', P), K('010', '263570', 'disjoncteur', A), K('010', '263570', 'sectionneur de terre', L), K('01', '246366', 'sectionneur de terre aval', L)]),
 'SS1_C4A': dict(sch='3183407', rep='01', tc='50/5-5A retenu (50-100) — ITH 21 kA 1 s', relay='S2036 (T14)', settings='I> 55 A SIT 2 s à 10 Is · I>> 500 A DT 0,4 s · Io 20 A DT 0,4 s',
     device='Disjoncteur SF1 400 A — CDE RI Sch. 889240', cable='E00.107 — 3 × 70 mm² Cu',
     keys=[K('T7d', '', 'boîte cellule', P), K('01', '', 'interrupteur-sectionneur', P), K('01', '', 'disjoncteur', A), K('01', '', 'sectionneur de terre', L), K('T7b', '', 'sectionneur de terre aval', L)]),
 'SS1_C3A': dict(sch='3183406', rep='02', tc='50/5-5A retenu (50-100) — ITH 21 kA 1 s', relay='S2036 (T14)', settings='I> 55 A SIT 2 s à 10 Is · I>> 500 A DT 0,4 s · Io 20 A DT 0,4 s',
     device='Disjoncteur SF1 400 A — CDE RI Sch. 889240', cable='E00.105 — 3 × 70 mm² Cu',
     keys=[K('T5d', '', 'boîte cellule', P), K('02', '', 'interrupteur-sectionneur', P), K('3A', '', 'interrupteur-sectionneur', L), K('02', '', 'sectionneur de terre', L), K('T5b', '', 'sectionneur de terre aval', L),
           K('T5g', '5EL2636', 'boîte de transfert T5g / 02 / 3A', A), K('02', 'EL24426', 'boîte de transfert', A), K('3A', '', 'boîte de transfert', P)]),
 'SS1_C1A': dict(sch='3275157', rep='01A', tc='100/5-5A retenu (50-100) — ITH 21 kA 1 s', relay='S2036 (T14)', settings='I> 55 A SIT 2 s à 10 Is · I>> 500 A DT 0,4 s · Io 20 A DT 0,4 s',
     device='Disjoncteur SF1 400 A — CDE RI Sch. 889240', cable='E00.103 — 3 × 70 mm² Cu',
     keys=[K('T1d', 'EL35351', 'boîte cellule', P), K('01A', 'EL11533', 'interrupteur-sectionneur', P), K('01A', 'EL11533', 'disjoncteur', A), K('01A', 'EL11533', 'sectionneur de terre', L), K('T1b', 'EL42462', 'sectionneur de terre aval', L)]),
 'SS1_C2A': dict(sch='3275158', rep='02A', tc='100/5-5A retenu (50-100) — ITH 21 kA 1 s', relay='S2036 (T14)', settings='I> 55 A SIT 2 s à 10 Is · I>> 500 A DT 0,4 s · Io 20 A DT 0,4 s',
     device='Disjoncteur SF1 400 A — CDE RI Sch. 889240', cable='E00.101 — 3 × 70 mm² Cu',
     keys=[K('T3d', 'EL31515', 'boîte cellule', P), K('02A', 'EL13131', 'interrupteur-sectionneur', P), K('02A', 'EL13131', 'disjoncteur', A), K('02A', 'EL13131', 'sectionneur de terre', L), K('T3b', 'EL24624', 'sectionneur de terre aval', L)]),
 'SS1_A1': dict(cell='Interrupteur-sectionneur d’arrivée (câble depuis le disjoncteur EDF 04)', keys=[K('A1E', '', 'interrupteur-sectionneur', A), K('A1C', '', 'sectionneur de terre', L)]),
 'SS1_V500': dict(cell='Couplage V500 : cellule disjoncteur de couplage (avec TC, relais non indiqué) + cellule de remontée de barres à interrupteur-sectionneur'),
 'SS1_A2': dict(cell='Interrupteur-sectionneur d’arrivée (câble depuis le disjoncteur CNR 01)', keys=[K('A2E', '', 'interrupteur-sectionneur', A), K('A2C', '', 'sectionneur de terre', L)]),
 'SS1_C1B': dict(sch='3183027', rep='01', tc='50/5-5A retenu (50-100) — ITH 21 kA 1 s', relay='S2036 (T14)', settings='I> 55 A SIT 2 s à 10 Is · I>> 500 A DT 0,4 s · Io 20 A DT 0,4 s',
     device='Disjoncteur SF1 400 A — CDE RI Sch. 889240', cable='E00.102 — 3 × 70 mm² Cu',
     keys=[K('T2d+S1', 'S1 = 5EL2256', 'boîte cellule', P), K('01', 'EL15335', 'interrupteur-sectionneur', P), K('01', 'EL15335', 'disjoncteur', A), K('01', 'EL15335', 'sectionneur de terre', L), K('T2b+X1', 'X1 = 1EL4432', 'sectionneur de terre aval', L)]),
 'SS1_C2B': dict(sch='3182851', rep='02', tc='50/5-5A retenu (50-100) — ITH 21 kA 1 s', relay='S2036 (T14)', settings='I> 55 A SIT 2 s à 10 Is · I>> 500 A DT 0,4 s · Io 20 A DT 0,4 s',
     device='Disjoncteur SF1 400 A — CDE RI Sch. 889240', cable='E00.104 — 3 × 70 mm² Cu',
     keys=[K('T4d+S2', 'S2 = EL53355', 'boîte cellule', P), K('02', 'EL13133', 'interrupteur-sectionneur', P), K('02', 'EL13133', 'disjoncteur', A), K('02', 'EL13133', 'sectionneur de terre', L), K('T4b+X2', 'X2 = EL55153', 'sectionneur de terre aval', L)]),
 'SS1_C3B': dict(sch='3183086', rep='03', tc='50/5-5A retenu (50-100) — ITH 21 kA 1 s', relay='S2036 (T14)', settings='I> 55 A EIT 2 s à 10 Is · I>> 300 A DT 0,4 s · Io 20 A DT 0,4 s',
     device='Disjoncteur SF1 400 A — CDE RI Sch. 889240', cable='E00.106 — 3 × 70 mm² Cu',
     keys=[K('T6d+S3', 'S3 = EL53511', 'boîte cellule', P), K('03', 'EL13131', 'interrupteur-sectionneur', P), K('3B', '', 'interrupteur-sectionneur', L), K('03', 'EL13131', 'sectionneur de terre', L), K('T6b+X3', 'X3 = EL51551', 'sectionneur de terre aval', L),
           K('T6g', '3EL2636', 'boîte de transfert T6g / 03 / 3B', A), K('03', 'EL13131', 'boîte de transfert', A), K('3B', '', 'boîte de transfert', P)]),
 'SS1_C4B': dict(sch='3183087', rep='04', tc='50/5-5A retenu (50-100) — ITH 21 kA 1 s', relay='S2036 (T14)', settings='I> 55 A SIT 2 s à 10 Is · I>> 500 A DT 0,4 s · Io 20 A DT 0,4 s',
     device='Disjoncteur SF1 400 A — CDE RI Sch. 889240', cable='E00.108 — 3 × 70 mm² Cu',
     keys=[K('T8d+S4', 'S4 = EL31113', 'boîte cellule', P), K('04', 'EL64462', 'interrupteur-sectionneur', P), K('04', 'EL64462', 'disjoncteur', A), K('04', 'EL64462', 'sectionneur de terre', L), K('T8b+X4', 'X4 = EL15115', 'sectionneur de terre aval', L)]),
 'SS1_C5B': dict(sch='E03933', rep='020', tc='TCR3 15 VA cl 0,5 KS = 3 (tore)', relay='S2035 (T14)', settings='I> 70 A SIT 2 s à 10 Is · I>> 500 A DT 0,4 s · Io 20 A DT 0,4 s',
     device='Interrupteur STRN 400 A + disjoncteur « 23-25B 400 A »', cable='E00.108 — 3 × 70 mm² Cu',
     keys=[K('020', '', 'interrupteur-sectionneur', P), K('020', '', 'disjoncteur', A), K('020', '', 'sectionneur de terre', L), K('02', '246364', 'sectionneur de terre aval', A)]),
 'SS1_C6B': dict(sch='3298882', rep='020', tc='75/5-5A retenu (75-150) — 7,5 VA cl 0,5 / 5 VA 5P15 — ITH 25 kA 1 s', relay='S2036 (T14)', settings='I> 70 A SIT 2 s à 10 Is · I>> 500 A DT 0,4 s · Io 20 A DT 0,4 s',
     device='Disjoncteur SF1 400 A 24 kV 12,5 kA — CDE RI Sch. 888461F', cable='E00.108 — 3 × 70 mm² Cu',
     keys=[K('020', '', 'interrupteur-sectionneur', P), K('020', '', 'disjoncteur', A), K('020', '', 'sectionneur de terre', L), K('02', '619561', 'sectionneur de terre aval', A)]),
 # ----------------------------------------------------------- tableau 20 kV TR 7 / TR 9 / boosting
 'SS2_CHYD': dict(sch='xxxxx (non renseigné)', rep='xx', tc='100-200/5-5A (100 retenu) — 30 VA cl 0,5 / 5 VA 5P15 / 7,5 VA 5P10 — ITH 14,5 kA 1 s', relay='Sxxxx (non renseigné)', settings='Non renseignés sur le plan',
     device='Interrupteur + disjoncteur SF1 400 A (lecture tuile)', keys=[K('Sx', 'ELxxx', 'boîte cellule', P), K('Xx', 'ELxxxx', 'sectionneur de terre aval', A)]),
 'SS2_CZ2': dict(sch='xxxxx (non renseigné)', rep='xx', tc='100-200/5-5A (100 retenu) — ITH 14,5 kA 1 s', relay='Sxxx / Mxx (non renseigné)', settings='I> xx A EIT 2 s à 10 Is · I>> xxx A DT 0,4 s · Io 20 A DT 0,4 s (valeurs non renseignées)',
     device='Disjoncteur SF1 400 A 24 kV 12,5 kA — Cde RI Sch. 889240', cable='3 × 1 × 50 mm² Al POPY N/G',
     keys=[K('Sx', 'ELxxx', 'boîte cellule', P), K('xx', 'ELxxxx', 'interrupteur-sectionneur', P), K('Xx', 'ELxxxx', 'sectionneur de terre aval', A)]),
 'SS2_CBT2': dict(sch='xxxxx (non renseigné)', rep='xx', tc='100-200/5-5A (100 retenu) — ITH 14,5 kA 1 s', relay='Sxxxx (non renseigné)', settings='I> xx A EIT 2 s · I>> xxx A DT 0,4 s · Io 20 A DT 0,4 s (valeurs non renseignées)',
     device='Disjoncteur SF1 400 A 24 kV 12,5 kA — Cde RI Sch. 889240', cable='Câble 001 — 3 × 1 × 95 mm² Al POPY N/G',
     keys=[K('Sx', 'ELxxx', 'boîte cellule', P), K('Xx', 'ELxxxx', 'sectionneur de terre aval', A)]),
 'SS2_C9A': dict(sch='3182583', rep='01', tc='50/5-5A retenu (50-100) — 30 VA cl 0,5 / 5 VA 5P15 / 7,5 VA 5P10 — ITH 14,5 kA 1 s', relay='S2036 (M15)', settings='I> 55 A EIT 2 s à 10 Is · I>> 300 A DT 0,4 s · Io 20 A DT 0,4 s',
     device='Disjoncteur SF1 400 A 24 kV 12,5 kA — Cde RI Sch. 889240', keys=[K('S1', 'EL33153', 'boîte cellule', P), K('01', 'EL62244', 'interrupteur-sectionneur', P), K('01', 'EL62244', 'disjoncteur', L), K('X1', 'EL53511', 'sectionneur de terre aval', A)]),
 'SS2_C7A': dict(sch='3182586', rep='02', tc='50/5-5A retenu (50-100) — ITH 14,5 kA 1 s', relay='S2036 (T14)', settings='I> 70 A SIT 2 s à 10 Is · I>> 500 A DT 0,4 s · Io 20 A DT 0,4 s',
     device='Disjoncteur SF1 400 A 24 kV 12,5 kA — Cde RI Sch. 889240', keys=[K('S2', '', 'boîte cellule', P), K('02', '', 'interrupteur-sectionneur', P), K('02', '', 'disjoncteur', L), K('X2', '', 'sectionneur de terre aval', A)]),
 'SS2_CB1': dict(sch='3182584', rep='03', tc='100/5-5A retenu (50-100) — ITH 14,5 kA 1 s', relay='S2036 (T15)', settings='I> 110 A SIT 2 s à 10 Is · I>> 500 A DT 0,4 s · Io 20 A DT 0,4 s',
     device='Disjoncteur SF1 400 A 24 kV 12,5 kA — Cde RI Sch. 889240', keys=[K('S3', 'EL35553', 'boîte cellule', P), K('03', 'EL64624', 'interrupteur-sectionneur', P), K('03', 'EL64624', 'disjoncteur', L), K('X3', 'EL31133', 'sectionneur de terre aval', A)]),
 'SS2_A3': dict(cell='Interrupteur-sectionneur d’arrivée (câble depuis le disjoncteur EDF 04)', keys=[K('A3E', '', 'interrupteur-sectionneur', A), K('A3C', '', 'sectionneur de terre', L)]),
 'SS2_CPL': dict(cell='Couplage par interrupteur-sectionneur + cellule de remontée de barres (pas de disjoncteur de couplage dessiné, contrairement au V500)'),
 'SS2_A4': dict(cell='Interrupteur-sectionneur d’arrivée (câble depuis le disjoncteur CNR 01)', keys=[K('A4E', '', 'interrupteur-sectionneur', A), K('A4C', '', 'sectionneur de terre', L)]),
 'SS2_CB2': dict(sch='3182750', rep='012', tc='50/5-5A retenu (50-100) — ITH 14,5 kA 1 s', relay='S2036 (T15)', settings='I> 110 A SIT 2 s à 10 Is · I>> 500 A DT 0,4 s · Io 20 A DT 0,4 s',
     device='Disjoncteur SF1 400 A 24 kV 12,5 kA — Cde RI Sch. 889240', keys=[K('S12', 'EL24264', 'boîte cellule', P), K('012', 'EL46662', 'interrupteur-sectionneur', P), K('012', 'EL46662', 'disjoncteur', L), K('X12', 'EL15313', 'sectionneur de terre aval', A)]),
 'SS2_C7B': dict(sch='3182752', rep='01', tc='50/5-5A retenu (50-100) — ITH 14,5 kA 1 s', relay='S2036 (T14)', settings='I> 70 A SIT 2 s à 10 Is · I>> 500 A DT 0,4 s · Io 20 A DT 0,4 s',
     device='Disjoncteur SF1 400 A 24 kV 12,5 kA — Cde RI Sch. 889240', keys=[K('S13', '', 'boîte cellule', P), K('01', '', 'interrupteur-sectionneur', P), K('01', '', 'disjoncteur', L), K('X13', '', 'sectionneur de terre aval', A)]),
 'SS2_C9B': dict(sch='xxxxxxxx (non renseigné)', rep='xx', tc='50/5-5A retenu (50-100) — ITH 14,5 kA 1 s', relay='Sxxxx (Txx) — non renseigné', settings='I> 55 A EIT 2 s à 10 Is · I>> 300 A DT 0,4 s · Io 20 A DT 0,4 s',
     device='Disjoncteur SF1 400 A', keys=[K('Sx', 'ELxxxxx', 'boîte cellule', P), K('Xx', 'ELxxxxx', 'sectionneur de terre aval', A)]),
 'SS2_CBT1': dict(sch='xxxxxxx (non renseigné)', rep='xx', tc='100-200/5-5A (100 retenu) — ITH 14,5 kA 1 s', relay='Sxxxx (non renseigné)', settings='Non renseignés', device='Disjoncteur SF1 400 A',
     cable='Câble 002 — 3 × 1 × 95 mm² Al POPY N/G', keys=[K('Sx', 'ELxxxxx', 'boîte cellule', P), K('Xx', 'ELxxxxx', 'sectionneur de terre aval', A)]),
 'SS2_CZ1': dict(sch='xxxxx (non renseigné)', rep='xx', tc='100-200/5-5A (100 retenu) — ITH 14,5 kA 1 s', relay='Sxxxx (non renseigné)', settings='Non renseignés', device='Disjoncteur SF1 400 A',
     cable='3 × 1 × 50 mm² Al POPY N/G', keys=[K('Sx', 'ELxxx', 'boîte cellule', P), K('Xx', 'ELxxxx', 'sectionneur de terre aval', A)]),
 # ----------------------------------------------------------- 6 kV four 2
 'KV6_A2': dict(rep='AEF2-A2', tc='300-600/5-5A (600 retenu) — 30 VA cl 0,5 / 5 VA 5P15 / 7,5 VA 5P10 — ITH 14,5 kA 1 s', relay='Sxxxx (Txx) — non renseigné', settings='I> xx A EIT 2 s · I>> xxx A DT 0,4 s · Io 20 A DT 0,4 s (non renseignés)',
     device='Disjoncteur SF1 400 A 7,2 kV 12,5 kA — Cde RI Sch. 889240', cable='Câble 003 — POPY N/G 3 × 2 × 1 × 150 mm² Al (depuis AEF2-TR2)', keys=[K('Sx', 'ELxxxxx', 'boîte cellule', P), K('xx', 'ELxxxxx', 'interrupteur-sectionneur', P), K('Xx', 'ELxxxxx', 'sectionneur de terre aval', A)]),
 'KV6_A1': dict(rep='AEF2-A1', tc='300-600/5-5A (600 retenu) — ITH 14,5 kA 1 s', relay='Sxxxx (Txx) — non renseigné', settings='Non renseignés',
     device='Disjoncteur SF1 400 A 7,2 kV 12,5 kA — Cde RI Sch. 889240', cable='Câble 004 — POPY N/G 3 × 2 × 1 × 150 mm² Al (depuis AEF2-TR1)', keys=[K('Sx', 'ELxxxxx', 'boîte cellule', P), K('Xx', 'ELxxxxx', 'sectionneur de terre aval', A)]),
 'KV6_C': dict(rep='AEF2-C', cell='Couplage par interrupteur-sectionneur + remontée de barres (« FOUR N°2 »)'),
}
for d in range(1, 7):
    CELLS[f'KV6_D{d}'] = dict(rep=f'AEF2-D{d}', device='Interrupteur-sectionneur + fusibles 200 A (combiné)', keys=[K('AxE', '', 'interrupteur-sectionneur', A), K('AxC', '', 'sectionneur de terre', L), K('AxC', '', 'serrure à l’armoire SPANG', A)])

TRANS = {
 'TR6A': dict(coupl='Dyn (triangle HTA / étoile BT)', neutre='Non indiqué', surv='Sondes', bt='M32H1 — STR58U', btkeys='01 — 619559', dest='VERS TGBT 6', fix='« VISSE » (raccordement HTA vissé)'),
 'TR5A': dict(coupl='Dyn', surv='Sondes', bt='M32H1 — STR38S', btkeys='01 — 246366', dest='VERS TGBT 5'),
 'TR4A': dict(coupl='Dyn', surv='Sondes', bt='M32H1 — Micrologic 5.0A', btkeys='T7b', dest='VERS TGBT 4', tkeys='T7d (porte transformateur)'),
 'TR3A': dict(coupl='Dyn', surv='Sondes', bt='(modèle non indiqué)', btkeys='(clé sans repère)', dest='VERS TGBT 3', tkeys='T5d / T5e (porte transformateur)'),
 'TR1A': dict(coupl='Dyn', surv='Sondes', bt='NW32H1 — Micrologic 5.0P', btkeys='T1b — EL42462', dest='VERS TGBT 2', tkeys='T1d — EL35351 (porte transformateur)'),
 'TR2A': dict(coupl='Dyn', surv='DGPT2 (transformateur immergé)', bt='(modèle non indiqué)', btkeys='T3b — EL24624', dest='VERS TGBT 1', tkeys='T3d — EL31515'),
 'TR1B': dict(coupl='Dyn', surv='DGPT2', bt='DA3200', btkeys='T2b+X1 — X1 = 1EL4432', dest='VERS TGBT 1', tkeys='T2d+S1'),
 'TR2B': dict(coupl='Dyn', surv='DGPT2', bt='DA3200', btkeys='T4b+X2 — X2 = EL55153', dest='VERS TGBT 2', tkeys='T4d+S2'),
 'TR3B': dict(coupl='Dyn', surv='DGPT2', bt='(modèle non indiqué)', btkeys='(clé sans repère)', dest='VERS TGBT 3', tkeys='T6d+X3 / T6e'),
 'TR4B': dict(coupl='Dyn', surv='DGPT2', bt='M32H1 — Micrologic 5.0A', btkeys='T8b+X4 — X4 = EL15115', dest='VERS TGBT 4', tkeys='T8d+S4'),
 'TR5B': dict(coupl='Dyn', surv='Sondes', bt='M32H1 — STR38S', btkeys='02 — 246364', dest='VERS TGBT 5', fix='« VISSE »'),
 'TR6B': dict(coupl='Dyn', surv='Sondes', bt='M32H1 — STR58U', btkeys='02 — 619561', dest='VERS TGBT 6', fix='« VISSE »'),
 'TR9A': dict(coupl='Dyn, neutre BT à la terre', surv='Sondes', bt='NW40H1 — Micrologic 5.0A', btkeys='X1', dest='VERS NOUVEAU TGBT9', tkeys='S1 — EL33153'),
 'TR7A': dict(coupl='Dyn, neutre BT à la terre', surv='Sondes', bt='NW40H1 — Micrologic 5.0A', btkeys='X2', dest='VERS TGBT 7', tkeys='S2'),
 'TR8A': dict(coupl='YNd (étoile HTA à la terre / triangle BT)', surv='Sondes', bt='Disjoncteur (modèle non indiqué)', btkeys='X3 — EL31133', dest='(aucune destination écrite — boosting)', tkeys='S3 — EL35553'),
 'TR8B': dict(coupl='YNd (étoile HTA à la terre / triangle BT)', surv='Sondes', bt='Disjoncteur (modèle non indiqué)', btkeys='X12 — EL15313', dest='(aucune destination écrite — boosting)', tkeys='S12 — EL24264'),
 'TR7B': dict(coupl='Dyn, neutre BT à la terre', surv='Sondes', bt='(modèle non indiqué)', btkeys='X13', dest='VERS TGBT 7', tkeys='S13'),
 'TR9B': dict(coupl='Dyn, neutre BT à la terre', surv='Sondes', bt='NW40H1 — Micrologic 5.0A', btkeys='Xx (non renseigné)', dest='VERS NOUVEAU TGBT9', tkeys='Sx (non renseigné)'),
 'AEF2-TR2': dict(coupl='Dyn — neutre 6 kV à la terre par résistance (avec tore)', ucc='x % (non renseigné)', surv='Sondes', bt='— (sortie 6 kV : câble 003 vers AEF2-A2)', dest='Tableau 6 kV four n°2'),
 'AEF2-TR1': dict(coupl='Dyn — neutre 6 kV à la terre par résistance (avec tore)', ucc='7 %', surv='Sondes', bt='— (sortie 6 kV : câble 004 vers AEF2-A1)', dest='Tableau 6 kV four n°2'),
 'AEF1-TRZ2': dict(coupl='Dyn', ucc='non indiqué', surv='—', bt='—', dest='VERS ÉLECTRODES ZONE 2'),
 'AEF1-TRZ1': dict(coupl='Dyn', ucc='non indiqué', surv='—', bt='—', dest='VERS ÉLECTRODES ZONE 1'),
 'TR-HYD': dict(coupl='Dyn', ucc='non indiqué', surv='—', bt='—', dest='TR HYDROGÈNE (aucune autre donnée)'),
}
for nid, info in CELLS.items():
    if nid not in nodes: print('  cellule absente du modèle', nid); continue
    nodes[nid]['uni'] = info
    if info.get('relay') and info.get('settings'):
        nodes[nid]['prot'] = f"{info.get('device', '')} — TC {info.get('tc', '')} — relais {info['relay']} : {info['settings']}".strip(' —')
    if info.get('rep'): nodes[nid]['cell'] = (f"Sch. {info['sch']} — " if info.get('sch') else '') + f"repère {info['rep']}"
    nodes[nid]['src'] = UNI + ' (lecture détaillée à 320 %, 11/10/2026)'
for tid, info in TRANS.items():
    if tid not in nodes: print('  transfo absent', tid); continue
    nodes[tid]['uni'] = info
    if info.get('ucc'): nodes[tid]['ucc'] = info['ucc']
    nodes[tid]['cooling'] = info['surv']
nodes['SS1_V500']['label'] = 'Couplage V500 (disjoncteur) — tableau 20 kV TR 1-6'
nodes['SS2_CPL']['label'] = 'Couplage par interrupteur — tableau 20 kV TR 7/9'
nodes['SS1_C6B']['prot'] = CELLS['SS1_C6B']['device'] + ' — TC ' + CELLS['SS1_C6B']['tc'] + ' — relais S2036 (T14) : ' + CELLS['SS1_C6B']['settings']

# ----------------------------------------------------------- poste de livraison : cellules d'arrivée réseau (400A-CIT) et mesure (CS-50A)
for side, srcn, cut, cb, pf_first in (('A', 'SRC_EDF', 'EDF', 'PL_A04', False), ('B', 'SRC_CNR', 'CNR', 'PL_B01', True)):
    N(f'PL_{side}_ARR', 'sw', f'Arrivée réseau {cut} — interrupteur-sectionneur 400 A (cellule 400A-CIT, câble)', board='PL20', kind='HTA', conf='confirme', src=UNI,
      uni=dict(cell='400A-CIT — interrupteur-sectionneur + sectionneur de terre, arrivée câble réseau', keys=[]))
    N(f'PL_{side}_PF', 'sw', f'Interrupteur-sectionneur 400 A + 3 parafoudres Varisil HD 24 ({cut}, cellule 400A-CIT)', board='PL20', kind='HTA', conf='confirme', src=UNI,
      uni=dict(cell='400A-CIT — interrupteur-sectionneur, 3 parafoudres type VARISIL HD 24 (B89959014 + ZHSD3), indicateur de défaut'))
    N(f'PL_{side}_TT', 'load', f'Cellule mesure {cut} (CS-50A) — TT 20 kV/√3 / 100 V/√3, fusibles Solefuse 6,3 A', board='PL20', conf='confirme', src=UNI,
      uni=dict(sch='3296311' if side == 'A' else '3296314', cell='CS-50A — 3 CC Solefuse 6,3 A sans percuteur — 3 VRQN/S2 20 kV/√3 / 100 V/√3 30 VA cl 0,1 + 100 V/√3 30 VA cl 0,5'))
    # chaînage : source → arrivée câble → jeu de barres du poste → disjoncteur
    for e in edges:
        if e['a'] == srcn and e['b'] == cb: e['b'] = f'PL_{side}_ARR'
    N(f'PL_{side}_J', 'bus', f'Poste de livraison — jeu de barres {cut}', board='PL20', conf='confirme', src=UNI)
    E(f'PL_{side}_ARR', f'PL_{side}_J', UNI); E(f'PL_{side}_J', cb, UNI); E(f'PL_{side}_J', f'PL_{side}_PF', UNI); E(f'PL_{side}_J', f'PL_{side}_TT', UNI)
F['PL20']['cells'] = [dict(t='DM1', label='A — Secours EDF (disj. 04)', node='PL_A04', ref='CS-400A'), dict(t='CM', label='Mesure TT EDF', node='PL_A_TT', ref='CS-50A'),
                      dict(t='IM', label='Arrivée réseau EDF', node='PL_A_ARR', ref='400A-CIT'), dict(t='PF', label='Interr. + parafoudres EDF', node='PL_A_PF', ref='400A-CIT'),
                      dict(t='PF', label='Interr. + parafoudres CNR', node='PL_B_PF', ref='400A-CIT'), dict(t='IM', label='Arrivée réseau CNR', node='PL_B_ARR', ref='400A-CIT'),
                      dict(t='CM', label='Mesure TT CNR', node='PL_B_TT', ref='CS-50A'), dict(t='DM1', label='B — Normal CNR (disj. 01)', node='PL_B01', ref='CS-400A')]
F['PL20']['conf'] = 'Ordre et type des cellules selon l’unifilaire (lecture détaillée) : CS-400A · CS-50A · 400A-CIT · 400A-CIT (EDF) | 400A-CIT · 400A-CIT · CS-50A · CS-400A (CNR).'
for c in F['SS2_20']['cells']:
    if c['t'] == 'CPL': c['label'] = 'Couplage (interrupteur)'
    if c['t'] == 'CPL2': c['label'] = 'Remontée de barres'

# ----------------------------------------------------------- boîtes de clés d'arrivée (interverrouillage des liaisons EDF / CNR)
KEYBOXES = [
 dict(id='A', title='Boîte de clés A — liaison SECOURS EDF (disjoncteur 04)', where='Poste de livraison, cellule A', keys=[('A', P), ('04', L), ('A2', A)]),
 dict(id='B', title='Boîte de clés B — liaison NORMAL CNR (disjoncteur 01)', where='Poste de livraison, cellule B', keys=[('B', P), ('01', L), ('B2', A)]),
 dict(id='A1', title='Boîte de clés côté arrivées EDF (A1 / A3)', where='Tableau 20 kV TR 1-6 (en-tête gauche)', keys=[('A2', L), ('A1E', L), ('A3E', L), ('A1C', P), ('A3C', P), ('A1', P)]),
 dict(id='B1', title='Boîte de clés côté arrivées CNR (A2 / A4)', where='Tableau 20 kV TR 1-6 (en-tête droit)', keys=[('B2', L), ('A4E', L), ('A2E', L), ('A4C', P), ('A2C', P), ('B1', P)]),
]
D_EXTRA = dict(keyboxes=KEYBOXES, keylegend='Convention Schneider (légende absente du plan) : ● clé prisonnière · ○ clé libre · Ø clé absente. Les états sont ceux dessinés sur le plan, pas l’état réel.',
               keyseries='Clés transformateurs : T1 = TR 1A · T2 = TR 1B · T3 = TR 2A · T4 = TR 2B · T5 = TR 3A · T6 = TR 3B · T7 = TR 4A · T8 = TR 4B (suffixe d = cellule / porte transformateur, b = disjoncteur BT, e / g = boîtes de transfert). Côté tableau TR 7/9 : S = cellule HTA, X = disjoncteur BT.')

# ----------------------------------------------------------- incohérences complémentaires
for i in issues:
    if i['id'] == 'I-TR12':
        i['text'] += (' Lecture détaillée : le disjoncteur BT dessiné sous TR 1A est un NW32H1 Micrologic 5.0P (clé T1b EL42462) — c’est le modèle de l’arrivée du TGBT 1A '
                      '(plan Schneider TGBT1A, case 2-28), alors que l’arrivée TR2A du TGBT 2 est un NW40H1. Avec l’étiquette « PROVIENT DE TR 1A » photographiée sur le TGBT 1, '
                      'trois éléments indiquent TR 1A → TGBT 1 : les mentions « VERS TGBT 2 / VERS TGBT 1 » de l’unifilaire sont très probablement inversées.')
        i['sev'] = 'moyenne'
ISSUE('I-KEYDUP', 'moyenne', 'Codes de clés identiques sur des appareils différents', 'Code EL13131 dessiné à la fois sur la cellule TR 2A (clé 02A) et sur la cellule TR 3B (clé 03, boîte T6g « 03 = EL13131 »). Code EL53511 dessiné à la fois pour S3 (TR 3B, « S3 = EL53511 ») et pour X1 (cellule TR 9A). Deux clés de même code ouvrent les mêmes serrures : à vérifier sur les serrures réelles (risque pour la consignation).', [UNI], ['SS1_C2A', 'SS1_C3B', 'SS2_C9A'])
ISSUE('I-BOOSTTC', 'basse', 'Boosting : réglages identiques avec des rapports de TC différents', 'Les deux cellules BOOSTING 3200 kVA ont le même réglage I> 110 A SIT, mais le TC retenu est 100/5 A pour S3 (Sch. 3182584) et 50/5 A pour S12 (Sch. 3182750) : vérifier le paramétrage réel des relais S2036.', [UNI], ['SS2_CB1', 'SS2_CB2'])
ISSUE('I-UNIXX', 'moyenne', 'Cellules non renseignées sur l’unifilaire', 'Repères « xx / Sxxxx / ELxxxx » et réglages non renseignés pour : TR Hydrogène, AEF1-TRZ1, AEF1-TRZ2, AEF2-TR1, AEF2-TR2, TR 9B (tableau 20 kV TR 7/9) et les arrivées 6 kV AEF2-A1 / AEF2-A2. Les réglages réels sont à relever sur les relais.', [UNI], ['SS2_CHYD', 'SS2_CZ1', 'SS2_CZ2', 'SS2_CBT1', 'SS2_CBT2', 'SS2_C9B', 'KV6_A1', 'KV6_A2'])
