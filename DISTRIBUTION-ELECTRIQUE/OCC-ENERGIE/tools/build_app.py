"""Assemble le fichier HTML autonome : OCC_ENERGIE.html (CSS + données + JS inline)."""
import os, json, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rd = lambda p: open(os.path.join(R, p), encoding='utf-8').read()
html = rd('src/index.html')
lite = '--lite' in sys.argv
if lite:
    html = html.replace('<title>OCC ÉNERGIE</title>', '<title>OCC ÉNERGIE — Mode léger 2024</title>')
data = json.loads(rd('build/data.json'))
# Index et historique Excel 2024 : couche documentaire distincte du graphe actif.
# Ne crée pas d'arête et ne modifie aucune règle de simulation électrique.
data['historique2024'] = json.loads(rd('sources/referentiel_excel_2024.json'))
if lite:
    # Les grandes tuiles Deep Zoom de niveau 12 sont omises seulement en mode léger.
    # Le fichier normal conserve toute la résolution satellite de l'usine.
    site = data.get('site', {})
    site['tiles'] = {k: v for k, v in site.get('tiles', {}).items() if int(k.split('/')[0]) <= 11}
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
js = rd('src/app.js').replace('/*PLANS*/', rd('src/plans.js').replace('/*PLANSVG*/', rd('src/plansvg.js')) + '\n' + rd('src/net.js') + '\n' + rd('src/manoeuvres.js') + '\n' + rd('src/fiche.js') + '\n' + rd('src/courant.js') + '\n' + rd('src/arbre.js') + '\n' + rd('src/parcours.js') + '\n' + rd('src/historique2024.js'))
html = html.replace('/*CSS*/', rd('src/style.css')).replace('/*DATA*/', data).replace('/*JS*/', js)
out = os.path.join(R, 'OCC_ENERGIE_2024_LITE.html' if lite else 'OCC_ENERGIE.html')
open(out, 'w', encoding='utf-8').write(html)
print(out, round(os.path.getsize(out) / 1024), 'Ko -', nval, 'ordre(s) de manoeuvre valide(s)')
