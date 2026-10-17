"""Catalogue vectoriel et documentaire : aucune photographie affichée."""
import html

def write_page(root, catalog):
    esc = lambda value: html.escape(str(value), quote=True)
    sections = []
    for key, board in catalog['boards'].items():
        notes = ''.join(f'<p>{esc(n["text"])}<br><small>{esc(n["source"])}</small></p>' for n in board['notes'])
        rows = ''.join(f'<tr><td>{esc(x["sheet"])} · {esc(x["cell"])}</td><td>{esc(x["text"])}</td><td>{esc(x["status"])}</td></tr>' for x in board['distribution'])
        table = f'<details><summary>Repères du classeur ({len(board["distribution"])})</summary><p>Références documentaires ; une cellule ne prouve pas une liaison physique.</p><table><thead><tr><th>Référence</th><th>Texte</th><th>Comparaison</th></tr></thead><tbody>{rows}</tbody></table></details>' if rows else ''
        docs = ''.join(f'<li>{esc(d["source"])} · {len(d["pages"])} pages de référence</li>' for d in board['documents'])
        if key != 'SANS-AFFECTATION':
            vector = f'<object type="image/svg+xml" data="facades-vectors/{esc(key)}.svg" aria-label="Armoire vectorielle {esc(key)}"><a href="facades-vectors/{esc(key)}.svg">Ouvrir le SVG</a></object>'
            back = f'<a href="../OCC_ENERGIE.html#/b/{esc(key)}">Fiche interactive {esc(key)}</a>'
        else:
            vector = ''
            back = '<p>Références sans correspondance certaine : aucune armoire ni alimentation déduite.</p>'
        sections.append(f'<section id="{esc(key)}"><h2>{esc(key)}</h2>{back}{vector}{notes}{table}<ul>{docs}</ul></section>')
    rooms = []
    for room in catalog['rooms']:
        units = ''.join(f'<g><title>{esc(u["name"])}</title><rect x="{u["x"]}" y="{u["y"]}" width="{u["w"]}" height="{u["h"]}"/><text x="{u["x"]}" y="{u["y"]+2}">{esc(u["name"])}</text></g>' for u in room['units'])
        labels = ''.join(f'<li>{esc(u["name"])}</li>' for u in room['units'])
        rooms.append(f'<details><summary>{esc(room["name"])} · {len(room["units"])} repères</summary><p>{esc(room["source"])} · {esc(room["geometry"])}</p><svg viewBox="0 0 100 100" role="img" aria-label="{esc(room["name"])}">{units}</svg><ul>{labels}</ul></details>')
    unif = catalog['unif']
    content = f'''<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Armoires vectorielles et repères</title><link rel="stylesheet" href="project-catalog.css"><main><a href="../OCC_ENERGIE.html#/registre">Retour à OCC Énergie</a><h1>Armoires vectorielles et repères complémentaires</h1><p>68 représentations SVG, cinq implantations relatives et informations du projet reçu. Les photographies restent des sources de travail archivées ; aucune photographie d’armoire n’est affichée ici.</p><label for="find">Filtrer les armoires et références</label><input id="find" type="search" autocomplete="off"><p id="count" role="status"></p>{''.join(sections)}<section id="implantations"><h2>Implantations vectorielles documentaires</h2><p>Positions relatives, sans cotes métriques.</p>{''.join(rooms)}</section><section id="unifilaire"><h2>Références du schéma unifilaire</h2><p>{esc(unif['source'])}</p><details><summary>Transcription documentaire à recouper</summary><pre>{esc(unif['text'])}</pre></details></section></main><script src="project-catalog.js"></script></html>'''
    (root / 'docs/COMPLEMENTS-20261018.html').write_text(content, encoding='utf-8')
