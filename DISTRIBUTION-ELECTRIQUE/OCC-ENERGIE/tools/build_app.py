"""Assemble le fichier HTML autonome : OCC_ENERGIE.html (CSS + données + JS inline)."""
import os, json, argparse
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--lite', action='store_true')
parser.add_argument('--compact', action='store_true', help='34 tuiles dont 22 WebP zoom 12 externes ; conserver assets/ à côté du HTML')
parser.add_argument('--output', choices=['OCC_ENERGIE_TS8.html', 'OCC_ENERGIE_VECTORIEL_MOBILE.html', 'OCC_ENERGIE_STANDALONE.html'])
args = parser.parse_args()
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rd = lambda p: open(os.path.join(R, p), encoding='utf-8').read()
html = rd('src/index.html')
lite = args.lite
if lite:
    html = html.replace('<title>OCC ÉNERGIE</title>', '<title>OCC ÉNERGIE — Mode léger 2024</title>')
data = json.loads(rd('build/data.json'))
if args.lite and args.compact: parser.error('--lite et --compact sont incompatibles')
# Index et historique Excel 2024 : couche documentaire distincte du graphe actif.
# Ne crée pas d'arête et ne modifie aucune règle de simulation électrique.
data['historique2024'] = json.loads(rd('sources/referentiel_excel_2024.json'))
# Référentiel SAP et compléments terrain : index consultatif, sans nœuds ni arêtes ajoutés.
data['referentielSAP'] = json.loads(rd('sources/referentiel_sap_2026.json'))
if args.compact:
    # Conservation du zoom maximum sans regonfler l'HTML : fichiers WebP déjà versionnés dans assets/.
    tiles = data.get('site', {}).get('tiles', {})
    for key, val in list(tiles.items()):
        if key.startswith('12/'):
            path = 'assets/ts8_site_tiles/' + key + '.webp'
            if not os.path.isfile(os.path.join(R, path)):
                raise FileNotFoundError('Tuile indispensable à la version compacte : ' + path)
            tiles[key] = path
if lite:
    # Les grandes tuiles Deep Zoom de niveau 12 sont omises seulement en mode léger.
    # Le fichier normal conserve toute la résolution satellite de l'usine.
    site = data.get('site', {})
    site['tiles'] = {k: v for k, v in site.get('tiles', {}).items() if int(k.split('/')[0]) <= 11}
# Mode de livraison GitHub : l'application complète conserve les 34 tuiles,
# mais les 22 tuiles de zoom 12 sont chargées depuis le dossier d'assets local.
# Cela permet de versionner sans perdre le zoom maximal malgré les limites de
# transport des gros blobs (> 6 Mo). La version --lite reste mono-fichier.
# Pour générer un seul gros HTML totalement autonome :
#   py -3 tools/build_app.py --output OCC_ENERGIE_STANDALONE.html
if not lite and args.output != 'OCC_ENERGIE_STANDALONE.html':
    site = data.get('site', {})
    tiles = site.get('tiles', {})
    site['tiles'] = {
        **{k: v for k, v in tiles.items() if int(k.split('/')[0]) <= 11},
        **{k: 'assets/ts8_site_tiles/' + k + '.webp' for k in tiles if int(k.split('/')[0]) == 12},
    }
# registre de validation des ordres de manœuvre (signés par le chargé d'exploitation) ; les clés « _… » sont des commentaires
vp = os.path.join(R, 'validations.json')
data['validations'] = {k: v for k, v in json.load(open(vp, encoding='utf-8')).items() if not k.startswith('_')} if os.path.exists(vp) else {}
nval = len(data['validations'])
# les numéros de bâtiment sont la légende du PowerPoint (repérage) : jamais affichés dans les textes (scrub)
import re as _re
def scrub(o):
    if isinstance(o, str): return _re.sub(r' ?\(b[âa]t\. ?\d+\)', '', o)
    if isinstance(o, list): return [scrub(x) for x in o]
    if isinstance(o, dict): return {k: (v if k in ('img', 'tiles') else scrub(v)) for k, v in o.items()}
    return o
data = scrub(data)
data = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
js = rd('src/app.js').replace('/*PLANS*/', rd('src/plans.js').replace('/*PLANSVG*/', rd('src/plansvg.js')) + '\n' + rd('src/net.js') + '\n' + rd('src/manoeuvres.js') + '\n' + rd('src/fiche.js') + '\n' + rd('src/courant.js') + '\n' + rd('src/arbre.js') + '\n' + rd('src/parcours.js') + '\n' + rd('src/historique2024.js') + '\n' + rd('src/complements.js'))
html = html.replace('/*CSS*/', rd('src/style.css')).replace('/*DATA*/', data).replace('/*JS*/', js)
out = os.path.join(R, args.output or ('OCC_ENERGIE_2024_LITE.html' if lite else 'OCC_ENERGIE_REVUE_PHOTO_20261018.html' if args.compact else 'OCC_ENERGIE.html'))
open(out, 'w', encoding='utf-8', newline='\n').write(html)
print(out, round(os.path.getsize(out) / 1024), 'Ko -', nval, 'ordre(s) de manoeuvre valide(s)')
