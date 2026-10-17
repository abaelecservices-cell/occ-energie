"""Ajoute à build/data.json : plans d'implantation (géométrie PowerPoint) et vue aérienne (zones numérotées).

Usage : py -3 -I build_plans.py   (lit build/data.json, implantation.json, site.json, aerial.webp)
Chaque forme garde son texte d'origine ; le rattachement à un équipement est déclaré ici avec sa confiance.
"""
import os, json, re, base64, unicodedata
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B = lambda p: os.path.join(R, 'build', p)
D = json.load(open(B('data.json'), encoding='utf-8'))
IMP = json.load(open(B('implantation.json'), encoding='utf-8'))
SITE = json.load(open(B('site.json'), encoding='utf-8'))
NODE = {n['id']: n for n in D['nodes']}; BOARD = {b['id']: b for b in D['boards']}
PPT = 'PLAN IMPLANTATION 2.pptx'

def key(s):
    s = unicodedata.normalize('NFD', s or ''); s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^A-Z0-9]+', ' ', s.upper()).strip()

def dep_by(board, pat):
    for n in D['nodes']:
        if n['t'] == 'dep' and n['board'] == board and re.search(pat, n['label'], re.I): return n['id']
    raise KeyError((board, pat))

# texte normalisé de la forme -> (id équipement, confiance, remarque)
MAP = {
 # SS1 côté gauche
 'TRANSFO GRADATHYR 1': ('GRADATHYR', 'probable', 'Transformateur du gradathyr — non représenté sur l’unifilaire'),
 'TRANSFO GRADATHYR 2': ('GRADATHYR', 'probable', 'Transformateur du gradathyr — non représenté sur l’unifilaire'),
 'TRANSFO 1 TR7B': ('TR7A', 'probable', 'Plan : « TRANSFO 1 TR7B » — rattaché à TR 7A (règle : transfos A et B du TGBT)'),
 'TRANSFO 2 TR7B': ('TR7B', 'probable', 'Plan : « TRANSFO 2 TR7B » — rattaché à TR 7B'),
 'TRANSFO 1 TGBT 9': ('TR9A', 'probable', 'Plan : « Transfo 1 TGBT 9 » — rattaché à TR 9A'),
 'TRANSFO 2 TGBT 9': ('TR9B', 'probable', 'Plan : « Transfo 2 TGBT 9 » — rattaché à TR 9B'),
 'ARMOIRE GRADATHYR N3 1 CREUSET': ('GRADATHYR', 'confirme', None), 'ARMOIRE GRADATHYR': ('GRADATHYR', 'confirme', None),
 'TR7 B': ('TGBT7', 'confirme', 'Plan : « Tr7 b » = TGBT 7 (photos « Tr7b.pdf »)'), 'TGBT 9': ('TGBT9', 'confirme', None),
 'TABLEAU 20KV': ('SS2_20', 'confirme', 'Unifilaire « S/STATION 2 - 20KV »'),
 'BATTERIE CONDENSATEUR 7A ET 7B': ('COND7', 'confirme', None), 'BATTERIE CONDENSATEUR 9A ET 9B': ('COND9', 'confirme', None),
 'DTRIB 110V': ('ARM110', 'probable', 'Plan : « DTRIB 110V » ↔ photo « Armoire 110v instrument ampèremètre »'),
 'VARIVOLT': ('VARIVOLT', 'confirme', None),
 'BOOSTING CREUSET 1': ('TR8A', 'probable', 'Plan : « Boosting creuset 1 » ↔ transformateur BOOSTING 3200 kVA (S3) de l’unifilaire'),
 'BOOSTING CREUSET 2': ('TR8B', 'probable', 'Plan : « Boosting creuset 2 » ↔ transformateur BOOSTING 3200 kVA (S12)'),
 'COFFRET VENTILATION LOCAL BOOSTING 1': ('VENTIL', 'probable', None), 'COFFRET VENTILATITION LOCAL BOOSTING 1': ('VENTIL', 'probable', None),
 'COFFRET VENTILATION LOCAL BOSSTING 2': ('VENTIL', 'probable', None), 'ARMOIRE VENTILATEUR HELICOIDES HELIPAC': ('VENTIL', 'probable', None),
 # SS1 côté droit
 'TABLEA GORGE': ('GORGE', 'confirme', None), 'TABLEAU 6KV': ('KV6', 'confirme', None),
 'SPANG 2': ('SPANG2', 'confirme', None), 'SPANG 5': ('SPANG5', 'confirme', None), 'SPANG 6': ('SPANG6', 'confirme', None),
 # chaufferie
 'TS17A': ('TS17', 'confirme', None), 'TS17B': ('TS17', 'confirme', None), 'TS9': ('TS9', 'confirme', None),
 'GROUPE DIESEL 1': ('GE1', 'confirme', 'Groupe électrogène n°1 (arrivée secours TS 9)'),
 'DECARBO': ('DECARBO', 'confirme', None),
 'COMPRESSEUR 121': (dep_by('TGBT7', r'7K121'), 'probable', 'Compresseur 7K121 (TGBT 7A, classeur H6)'),
 'COMPRESSEUR 122': (dep_by('TGBT7', r'7K122'), 'probable', 'Compresseur 7K122 (TGBT 7A, classeur H9)'),
 'POMPE EAU FROIDE N 3': (dep_by('TS17', r'eau froide n.3'), 'probable', 'Ppe eau froide n°3 (TS 17B)'),
 # STEP
 'TS16': ('TS16', 'confirme', None),
 # SS2
 **{f'TRANSFO {n}{h}': (f'TR{n}{h}', 'confirme', None) for n in range(1, 7) for h in 'AB'},
 **{f'TGBT {n}': (f'TGBT{n}', 'confirme', None) for n in range(1, 7)},
 'TS2': ('TS2', 'confirme', None), 'ECLAIRAGE SOUS SATTION': ('ECLSST1', 'confirme', None),
 'TABLEAU ARRIVE 20 KV CNR EDF': ('SS1_20', 'confirme', 'Unifilaire « S/STATION 1 - 20KV »'),
 'CONDENSATEUR 2A': ('COND2A', 'confirme', None), 'CONDENCATEUR 1A ET 1 B': ('COND1', 'confirme', None), 'CONDENCATEUR 2A ET 2 B': ('COND2B', 'probable', None),
 'CONDENSATEUR 4A ET 4B': ('COND4', 'confirme', None), 'CONDENSAETEUR 5A': ('COND5A', 'confirme', None), 'CONDENSAETEUR 5B': ('COND5B', 'confirme', None),
 'CONDENSAETEUR 6A': ('COND6A', 'confirme', None), 'CONDENSAETEUR 6B': ('COND6B', 'confirme', None),
 'ONDULEUR 1': ('OND1', 'confirme', None), 'ONDULEUR 2': ('OND2', 'confirme', None),
 'ALIM ONDULEUR 1': ('ALIMOND1', 'confirme', 'Armoire « Alimentation ondulée onduleur 1 »'), 'ALIM ONDULEUR 2': ('ALIMOND2', 'confirme', 'Armoire « Alimentation ondulée onduleur 2 »'),
}

TITLES = {'SOUS STATION 1 COTE GAUCHE', 'SOUS STATION 1 COTE DROIT', 'SOUS STATION N 2', 'LOCAL CHAUFFERIE', 'STEP'}
unmapped = []

def convert(slide_items, title, dx=0.0, dy=0.0, skip=lambda it: False):
    """Convertit les formes d'une diapositive en éléments de plan typés :
    wall (mur, trait noir/bleu), face (trait orange = côté où l'appareillage est visible), vis (double flèche = armoires en vis-à-vis),
    door (porte), box (armoire / équipement), title."""
    items, seen_spang3 = [], 0
    for it in slide_items:
        if skip(it): continue
        t = it['text']; k = key(t)
        e = dict(x=round(it['x'] + dx, 2), y=round(it['y'] + dy, 2), w=it['w'], h=it['h'], fh=it['fh'], fv=it['fv'], t=t)
        line = it['line'] or ''
        if it['kind'] == 'cxnSp':
            e['k'] = 'vis' if (it['head'] or it['tail']) else ('face' if 'accent2' in line else 'wall')
        elif it['kind'] == 'sp' and (it['w'] <= 8 or it['h'] <= 8) and not t:
            e['k'] = 'door'
        elif it['kind'] == 'sp' and not t:
            continue
        elif k in TITLES:
            e['k'] = 'title'
        elif k == 'ENTRE':
            e['k'] = 'entre'
        else:
            e['k'] = 'box'
            if k == 'SPANG 3':
                seen_spang3 += 1
                if seen_spang3 == 1: e.update(ref='SPANG3', conf='confirme')
                else: e.update(note='Deuxième boîte « Spang 3 » sur le plan : doublon ou autre ligne (1 ou 4 ?) — à confirmer', conf='a_verifier')
            elif k in MAP:
                ref, conf, note = MAP[k]
                assert ref in NODE or ref in BOARD, ref
                e.update(ref=ref, conf=conf)
                if note: e['note'] = note
            else:
                e['note'] = 'Équipement du plan non représenté dans les documents électriques transmis.'
                unmapped.append((title, t))
        items.append(e)
    return items

S = IMP['slides']
# --- Sous-station 1 : côtés gauche et droit accolés, séparés par une cloison fine percée d'une ouverture d'environ 1 m
# Diapositive 1 : cloison droite x≈889-890 (deux segments, ouverture entre y≈255 et y≈303). Diapositive 2 : mur haut à y≈171,75.
DX, DY = 890.0, 130.5 - 171.75
left = convert(S[0]['items'], 'SS1', skip=lambda it: it['kind'] == 'cxnSp' and it['x'] >= 900 or key(it['text']) == 'SOUS STATION 1 COTE GAUCHE')
right = convert(S[1]['items'], 'SS1', DX, DY, skip=lambda it: (it['kind'] == 'cxnSp' and abs(it['y'] - 171.75) < 1 and not it['head']) or key(it['text']) == 'SOUS STATION 1 COTE DROIT')
RIGHT_END = DX + 819.0
for e in left:
    if e['k'] == 'wall' and e['h'] == 0 and e['w'] > 800: e['w'] = RIGHT_END - e['x']          # murs haut et bas prolongés
    if e['k'] == 'wall' and 888 < e['x'] < 892: e['partition'] = True                          # cloison fine
ss1 = left + right + [
    dict(k='wall', x=RIGHT_END, y=130.5, w=0, h=409.5, fh=False, fv=False, t=''),
    dict(k='title', x=60, y=60, w=600, h=40, fh=False, fv=False, t='SOUS-STATION 1'),
    dict(k='label', x=380, y=112, w=200, h=14, fh=False, fv=False, t='CÔTÉ GAUCHE'),
    dict(k='label', x=DX + 330, y=112, w=200, h=14, fh=False, fv=False, t='CÔTÉ DROIT'),
    dict(k='opening', x=889.5, y=255.0, w=0, h=48.0, fh=False, fv=False, t='Ouverture ≈ 1 m'),
]
plans = [
    dict(id='PLAN_SS1', title='Sous-station 1', loc='SS1', src=f'{PPT} — diapositives 1 (côté gauche) et 2 (côté droit), accolées', w=RIGHT_END + 40, h=IMP['h'], y0=40,
         note='Côtés gauche et droit séparés par une cloison fine percée d’une ouverture d’environ 1 m (indication exploitant). Échelle relative du PowerPoint, non cotée.', items=ss1),
    dict(id='PLAN_SS2', title='Sous-station 2', loc='SS2', src=f'{PPT} — diapositive 5', w=IMP['w'], h=IMP['h'], y0=40, items=convert(S[4]['items'], 'SS2')),
    dict(id='PLAN_CHAUF', title='Local chaufferie', loc='CHAUF', src=f'{PPT} — diapositive 3', w=IMP['w'], h=IMP['h'], y0=40, items=convert(S[2]['items'], 'CHAUF')),
    dict(id='PLAN_STEP', title='STEP', loc='STEP', src=f'{PPT} — diapositive 4', w=IMP['w'], h=IMP['h'], y0=40, items=convert(S[3]['items'], 'STEP')),
]
D['plans'] = plans
for l in D['loc'].values():
    if 'plan' in l: l['plan'] = ['PLAN_SS1' if p.startswith('PLAN_SS1') else p for p in l['plan']]

# --------------------------------------------------------------------------- vue aérienne
s2 = SITE['slides'][1]['items']
pic = next(i for i in s2 if i['kind'] == 'pic')
cx, cy = pic['x'] + pic['w'] / 2, pic['y'] + pic['h'] / 2
bw, bh = pic['h'], pic['w']            # rotation 270° : largeur et hauteur affichées permutées
bx0, by0 = cx - bw / 2, cy - bh / 2
CROP = json.load(open(B('aerial_crop.json')))
cw, ch = CROP['x1'] - CROP['x0'], CROP['y1'] - CROP['y0']
LEG = {}
for t in (i['text'] for i in SITE['slides'][2]['items']):
    # un repère = nombre précédé d'un espace (ou en début) et suivi d'une lettre ; « sous station 1 », « tente stockage 1 », « R1 » ne sont pas des repères
    ms = list(re.finditer(r'(?:^|(?<=\s))(\d{1,2})\s*(?=[^\d\s])', t))
    for k, m in enumerate(ms):
        LEG[int(m.group(1))] = t[m.end():ms[k + 1].start() if k + 1 < len(ms) else len(t)].strip()
ZB = {  # bâtiment -> tableaux / équipements (confiance, source)
 33: (['PL20'], 'confirme', 'Légende « PDL CNR EDF »'),
 25: (['SS2_20', 'TGBT9', 'TGBT7', 'KV6', 'GRADATHYR', 'GORGE'], 'confirme', 'Légende « sous station 1 » + plan d’implantation'),
 31: (['SS1_20', 'TGBT1', 'TGBT2', 'TGBT3', 'TGBT4', 'TGBT5', 'TGBT6', 'TS2'], 'confirme', 'Légende « sous station 2 » + plan d’implantation'),
 11: (['TS9', 'TS17'], 'confirme', 'Légende « local chaufferie » + plan'),
 13: (['TS16'], 'confirme', 'Légende « step » + plan'),
 12: (['BRONZINI'], 'confirme', 'Légende « bronzini »'),
 37: (['DECARBO'], 'probable', 'Légende « decarbo » (le plan place aussi une armoire Décarbo en chaufferie)'),
 1: (['TS12'], 'probable', 'Indication : TS 12 au-dessus de la maintenance'),
 3: (['TS46A', 'TS46B'], 'probable', 'Indication : TS 46A/46B entre Packman et l’emballage'),
 5: (['TS46A', 'TS46B'], 'probable', 'Indication : TS 46A/46B entre Packman et l’emballage'),
 36: (['TS7'], 'probable', 'Indication : TS 7 à proximité du four'),
 30: (['TS44'], 'probable', 'Indication : TS 44 en face des filières'),
 26: (['ETUVE789'], 'probable', 'Légende « hall étuves »'),
 29: (['TS1'], 'probable', 'Légende « atelier ensimage » ↔ TS 1 Ensimage'),
 8: (['TS15'], 'probable', 'Légende « batch » ↔ TS 15 Batch'),
}
SALLES = {25: 'Sous-station 1', 31: 'Sous-station 2', 33: 'PDL CNR / EDF'}   # seules étiquettes affichées
raw = []
for i in s2:
    if i['kind'] != 'sp' or not re.fullmatch(r'\d+', i['text'] or ''): continue
    fx, fy = (i['x'] - bx0) / bw, (i['y'] - by0) / bh
    raw.append(dict(n=int(i['text']), x=(fx - CROP['x0']) / cw, y=(fy - CROP['y0']) / ch, w=i['w'] / bw / cw, h=i['h'] / bh / ch))
# repère 19 en bas à droite : tente de stockage, pas le vestiaire (indication exploitant) -> supprimé
nineteen = sorted([r for r in raw if r['n'] == 19], key=lambda r: r['w'] * r['h'])
raw = [r for r in raw if not (r['n'] == 19 and r is nineteen[-1])]
LEG[20] = 'piscine'   # indication exploitant (absent de la légende du PowerPoint)
zones = []
for n in sorted({r['n'] for r in raw}):
    parts = [r for r in raw if r['n'] == n]
    nm_ = LEG.get(n, 'Bâtiment non légendé')
    z = dict(n=n, name=nm_[:1].upper() + nm_[1:], parts=[[round(p[k], 4) for k in ('x', 'y', 'w', 'h')] for p in parts])
    big = max(parts, key=lambda p: p['w'] * p['h'])
    z['cx'], z['cy'] = round(big['x'] + big['w'] / 2, 4), round(big['y'] + big['h'] / 2, 4)
    if n in SALLES: z['label'] = SALLES[n]
    if n in ZB: z.update(refs=ZB[n][0], conf=ZB[n][1], src=ZB[n][2])
    zones.append(z)
if os.path.exists(B('ortho.webp')) and os.path.exists(B('ortho_affine.json')):
    # fond = orthophoto IGN 2024 (tools/ortho.py) ; repères du PowerPoint reportés par la transformation affine de tools/recale_ortho.py
    OA, OJ = json.load(open(B('ortho_affine.json'))), json.load(open(B('ortho.json'), encoding='utf-8'))
    (a, b_, c), (d, e, f) = OA['A']
    def to_o(x, y):  # fractions de l'ancienne image -> fractions de l'orthophoto
        X, Y = x * OA['oldW'], y * OA['oldH']
        return round((a * X + b_ * Y + c) / OJ['w'], 5), round((d * X + e * Y + f) / OJ['h'], 5)
    from PIL import Image as _Im, ImageDraw as _Dr
    def union_outline(polys, W, H):
        """Contour extérieur de la réunion de plusieurs quadrilatères (repères multi-parties d'un même bâtiment) :
        rastérisation pleine résolution, suivi des arêtes de bord, simplification (Ramer-Douglas-Peucker)."""
        P = [[(x * W, y * H) for x, y in p] for p in polys]
        x0 = int(min(x for p in P for x, _ in p)) - 2; y0 = int(min(y for p in P for _, y in p)) - 2
        x1 = int(max(x for p in P for x, _ in p)) + 3; y1 = int(max(y for p in P for _, y in p)) + 3
        m = _Im.new('1', (x1 - x0, y1 - y0), 0); d = _Dr.Draw(m)
        for p in P: d.polygon([(x - x0, y - y0) for x, y in p], fill=1)
        w, h = m.size; px = m.load(); f = lambda x, y: 0 <= x < w and 0 <= y < h and px[x, y]
        nxt = {}
        for y in range(h):
            for x in range(w):
                if not px[x, y]: continue
                if not f(x, y - 1): nxt.setdefault((x, y), []).append((x + 1, y))
                if not f(x + 1, y): nxt.setdefault((x + 1, y), []).append((x + 1, y + 1))
                if not f(x, y + 1): nxt.setdefault((x + 1, y + 1), []).append((x, y + 1))
                if not f(x - 1, y): nxt.setdefault((x, y + 1), []).append((x, y))
        loops = []
        while nxt:
            s = next(iter(nxt)); loop = [s]; cur = s
            while True:
                lst = nxt.get(cur)
                if not lst: break
                n = lst.pop()
                if not lst: del nxt[cur]
                if n == s: break
                loop.append(n); cur = n
            if len(loop) > 8: loops.append(loop)
        def rdp(pts, eps):
            if len(pts) < 3: return pts
            (ax, ay), (bx, by) = pts[0], pts[-1]; L = ((bx - ax) ** 2 + (by - ay) ** 2) ** .5 or 1e-9
            dmax, k = 0, 0
            for i in range(1, len(pts) - 1):
                dd = abs((bx - ax) * (ay - pts[i][1]) - (ax - pts[i][0]) * (by - ay)) / L
                if dd > dmax: dmax, k = dd, i
            return rdp(pts[:k + 1], eps)[:-1] + rdp(pts[k:], eps) if dmax > eps else [pts[0], pts[-1]]
        area = lambda l: sum(l[i][0] * l[i - 1][1] - l[i - 1][0] * l[i][1] for i in range(len(l))) / 2
        out = []
        for l in sorted(loops, key=lambda l: -abs(area(l))):
            if abs(area(l)) < 40: continue
            # contour fermé : coupé en deux au point le plus éloigné du départ, chaque moitié simplifiée séparément
            k = max(range(len(l)), key=lambda i: (l[i][0] - l[0][0]) ** 2 + (l[i][1] - l[0][1]) ** 2)
            s = rdp(l[:k + 1], 1.6)[:-1] + rdp(l[k:] + [l[0]], 1.6)[:-1]
            out.append([(round((x + x0) / W, 5), round((y + y0) / H, 5)) for x, y in s])
        return out   # parties jointives : un seul contour ; parties séparées : un contour chacune
    for z in zones:
        z['polys'] = [[to_o(x, y), to_o(x + w, y), to_o(x + w, y + h), to_o(x, y + h)] for x, y, w, h in z['parts']]
        z['cx'], z['cy'] = to_o(z['cx'], z['cy'])
        if len(z['polys']) > 1:   # repères multiples d'un même bâtiment (ex. n° 2) : un seul contour
            z['polys'] = union_outline(z['polys'], OJ['w'], OJ['h'])
        del z['parts']
PHOTO = os.path.join(os.path.dirname(B('x')), '..', 'sources', 'photo_site_exploitant.jpg')
MASTER = os.path.join(R, 'assets', 'vue_aerienne', 'OCC_usine_IGN_2024_20cm.png')
if os.path.exists(B('ortho_affine.json')) and os.path.exists(MASTER) and os.path.exists(B('site_tiles.json')):
    # Vue du site = dossier « OCC_DOSSIER_CLAUDE » fourni par l'exploitant : orthophoto IGN BD ORTHO 2024, 20 cm/pixel, pixels d'origine,
    # transparente hors contour, tournée de 90° sens antihoraire (nord à gauche, demande exploitant) ; pyramide de tuiles (tools/site_tiles.py)
    # chargée selon la zone visible et le zoom. Repères des bâtiments en couche vectorielle indépendante (coordonnées normalisées).
    ST = json.load(open(B('site_tiles.json')))
    META = json.load(open(os.path.join(R, 'assets', 'vue_aerienne', 'metadata.json'), encoding='utf-8'))
    def trt(fx, fy):  # fractions de l'orthophoto (nord en haut) -> fractions de l'image tournée de 90° antihoraire
        return (round(fy, 5), round(1 - fx, 5)) if ST['rotation'] == 90 else (fx, fy)
    for z in zones:
        z['polys'] = [[trt(x, y) for x, y in p] for p in z['polys']]
        z['cx'], z['cy'] = trt(z['cx'], z['cy'])
    D['site'] = dict(img=None, tiles=ST['tiles'], w=ST['width'], h=ST['height'], tileSize=ST['tileSize'], overlap=ST['overlap'], maxLevel=ST['maxLevel'],
                     ratio=round(ST['width'] / ST['height'], 4), zones=zones, poly=None, north='left' if ST['rotation'] == 90 else True, res=META['source_resolution_m_per_pixel'],
                     attribution=META['attribution'], src=META['attribution'] + ' — contour indicatif — tournée de 90° (nord à gauche)')
    print('carte : orthophoto IGN en tuiles', (ST['width'], ST['height']), len(ST['tiles']), 'tuiles — bâtiments', len(zones))
elif os.path.exists(B('ortho_affine.json')) and os.path.exists(PHOTO) and os.path.exists(B('photo_affine.json')):
    # Vue du site = photo fournie par l'exploitant, NON retouchée (ni découpe ni retouche), seulement tournée de 90° dans le sens antihoraire
    # (nord à gauche). Les repères des bâtiments (orthophoto) sont reportés par le recalage de tools/recale_photo.py.
    PA = json.load(open(B('photo_affine.json')))
    (pa, pb, pc), (pd, pe, pf) = PA['ortho_to_photo']
    ph = _Im.open(PHOTO).convert('RGB'); pw_, ph_ = ph.size
    rot = ph.rotate(90, expand=True)
    rot.save(B('site_photo.jpg'), 'JPEG', quality=95, subsampling=0)
    def trp(fx, fy):  # fractions de l'orthophoto -> fractions de la photo tournée (x' = y, y' = largeur - x)
        X, Y = fx * OJ['w'], fy * OJ['h']
        x, y = pa * X + pb * Y + pc, pd * X + pe * Y + pf
        return round(y / ph_, 5), round((pw_ - x) / pw_, 5)
    for z in zones:
        z['polys'] = [[trp(x, y) for x, y in p] for p in z['polys']]
        z['cx'], z['cy'] = trp(z['cx'], z['cy'])
    img = base64.b64encode(open(B('site_photo.jpg'), 'rb').read()).decode()
    D['site'] = dict(img='data:image/jpeg;base64,' + img, ratio=round(rot.width / rot.height, 4), zones=zones, poly=None, north='left', photo=True,
                     src='Photo aérienne fournie par l’exploitant (non retouchée, tournée de 90°) — repères des bâtiments reportés par recalage sur l’orthophoto IGN')
    print('carte : photo exploitant', rot.size, '— bâtiments', len(zones))
elif os.path.exists(B('ortho.webp')) and os.path.exists(B('ortho_affine.json')):
    # Cadrage demandé par l'exploitant (photo de référence du 11/10/2026) : découpe juste à l'intérieur de la bande de pelouse qui entoure
    # l'usine (le « rectangle vert » : côté ouest, deux décrochés au sud des tentes et de la cour, bande le long du champ et de la voie ferrée),
    # puis rotation de 90° dans le sens antihoraire (le nord passe à gauche, comme la vue du PowerPoint « site l ardoise »).
    CUT = [(258, 40), (515, 20), (1859, 10), (1944, 95), (1977, 898), (2002, 2248), (1944, 2323), (1800, 2382), (1720, 2250), (1680, 2050),
           (1660, 1800), (1655, 1460), (1600, 1410), (1105, 1410), (1105, 1148), (258, 1148)]
    def inside(px, py, poly=CUT):
        c = False
        for i in range(len(poly)):
            (x1, y1), (x2, y2) = poly[i], poly[i - 1]
            if (y1 > py) != (y2 > py) and px < (x2 - x1) * (py - y1) / (y2 - y1) + x1: c = not c
        return c
    full = _Im.open(B('ortho_full.png')).convert('RGBA')
    bx0, by0 = min(x for x, _ in CUT), min(y for _, y in CUT); bx1, by1 = max(x for x, _ in CUT), max(y for _, y in CUT)
    cw_, ch_ = bx1 - bx0, by1 - by0
    msk = _Im.new('L', full.size, 0); _Dr.Draw(msk).polygon(CUT, fill=255)
    alpha = _Im.composite(full.getchannel('A'), _Im.new('L', full.size, 0), msk)
    full.putalpha(alpha)
    rot = full.crop((bx0, by0, bx1, by1)).rotate(90, expand=True)          # PIL : angle positif = sens antihoraire
    rot.save(B('site_rot.webp'), 'WEBP', quality=80, method=6)
    def tr(fx, fy):  # fractions de l'orthophoto -> fractions de l'image découpée et tournée (x' = y, y' = largeur - x)
        X, Y = fx * OJ['w'] - bx0, fy * OJ['h'] - by0
        return round(Y / ch_, 5), round((cw_ - X) / cw_, 5)
    kept = []
    for z in zones:
        if not inside(z['cx'] * OJ['w'], z['cy'] * OJ['h']) and not z.get('refs'): continue   # bâtiments hors de la bande (champ, sud) retirés
        z['polys'] = [[tr(x, y) for x, y in p] for p in z['polys']]
        z['cx'], z['cy'] = tr(z['cx'], z['cy'])
        kept.append(z)
    print('carte : bâtiments conservés', len(kept), '/', len(zones), '— retirés :', [z['name'] for z in zones if z not in kept])
    zones = kept
    img = base64.b64encode(open(B('site_rot.webp'), 'rb').read()).decode()
    D['site'] = dict(img='data:image/webp;base64,' + img, ratio=round(rot.width / rot.height, 4), zones=zones,
                     poly=[tr(x / OJ['w'], y / OJ['h']) for x, y in CUT], north='left',
                     src=OJ['src'] + ' — cadrage à l’intérieur de la bande de pelouse, tourné de 90° (nord à gauche)')
else:
    img = base64.b64encode(open(B('aerial.webp'), 'rb').read()).decode()
    D['site'] = dict(img='data:image/webp;base64,' + img, ratio=round((bw * cw) / (bh * ch), 4), zones=zones, poly=CROP['poly'],
                     src='site l ardoise.pptx — diapositives 1 à 3 (image et repérage des bâtiments) ; image détourée au périmètre du site ; repère 19 (tente de stockage) retiré ; repères 2 fusionnés')
json.dump(D, open(B('data.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('plans', len(plans), 'zones', len(zones), 'légende', len(LEG), 'formes non rattachées', len(unmapped))
for u in unmapped: print('   ', u)
