"""Assemble le fichier HTML autonome : OCC_ENERGIE.html (CSS + données + JS inline)."""
import os, json
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rd = lambda p: open(os.path.join(R, p), encoding='utf-8').read()
html = rd('src/index.html')
data = json.loads(rd('build/data.json'))
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
js = rd('src/app.js').replace('/*PLANS*/', rd('src/plans.js').replace('/*PLANSVG*/', rd('src/plansvg.js')) + '\n' + rd('src/net.js') + '\n' + rd('src/manoeuvres.js') + '\n' + rd('src/fiche.js') + '\n' + rd('src/courant.js') + '\n' + rd('src/arbre.js') + '\n' + rd('src/parcours.js'))
html = html.replace('/*CSS*/', rd('src/style.css')).replace('/*DATA*/', data).replace('/*JS*/', js)
out = os.path.join(R, 'OCC_ENERGIE.html')
open(out, 'w', encoding='utf-8').write(html)
print(out, round(os.path.getsize(out) / 1024), 'Ko -', nval, 'ordre(s) de manoeuvre valide(s)')
