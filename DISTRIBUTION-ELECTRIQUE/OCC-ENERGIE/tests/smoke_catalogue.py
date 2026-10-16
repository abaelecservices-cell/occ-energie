"""Parcours de tous les tableaux, fiches et routes dans Chrome/Edge, hors ligne."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'artifacts'
ART.mkdir(exist_ok=True)
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=os.environ['OCC_CHROME'], headless=True)
    page = browser.new_page(viewport={'width': 1440, 'height': 900})
    errors, requests = [], []
    page.on('pageerror', lambda err: errors.append(str(err)))
    page.on('request', lambda req: requests.append(req.url) if req.url.startswith('http') else None)
    page.goto((ROOT / 'OCC_ENERGIE.html').as_uri())
    result = page.evaluate('''() => {
      const checked = {routes: 0, boards: 0, tabs: 0, sheets: 0};
      const visit = hash => { location.hash = hash; route(false);
        if (!VIEW().textContent.trim()) throw Error('Vue vide : ' + hash); };
      for (const r of ['', 'site', 'plans', 'reseau', 'tableaux', 'depannage',
                       'entretien', 'registre', 'historique2024', 'courant/TR1A',
                       'fiche/TR1A', 'fiches/TR1A', 'details/TR1A']) {
        visit('#/' + r); checked.routes++;
      }
      for (const b of D.boards) {
        visit('#/b/' + b.id); checked.boards++;
        for (const button of document.querySelectorAll('#btabs button')) {
          button.click(); checked.tabs++;
          if (!document.querySelector('#bbody').textContent.trim())
            throw Error('Onglet vide : ' + b.id + '/' + button.dataset.t);
        }
      }
      for (const n of D.nodes) { openEntity(n.id); closeSheet(); checked.sheets++; }
      visit('#/tableaux');
      document.querySelector('#topen').click();
      for (const b of D.boards)
        if (!VIEW().querySelector('[data-go="#/b/' + b.id + '"]'))
          throw Error('Tableau absent de l’arbre : ' + b.id);
      for (const n of D.nodes.filter(n => n.t === 'dep'))
        if (!VIEW().querySelector('[data-open="' + n.id + '"]'))
          throw Error('Départ absent de l’arbre : ' + n.id);
      return checked;
    }''')
    assert not errors, errors
    assert not requests, 'Appels réseau imprévus : ' + str(requests)
    for width in (390, 768, 1440):
        page.set_viewport_size({'width': width, 'height': 900})
        for route in ('', 'tableaux', 'historique2024', 'b/TS8', 'b/ENSIM_A'):
            page.evaluate('(r) => {location.hash="#/"+r; route(false)}', route)
            assert page.locator('#view').is_visible()
        page.screenshot(path=str(ART / f'catalogue-{width}.png'), full_page=True)
    assert not errors, errors
    print('OK catalogue :', result, '; largeurs 390/768/1440 ; aucun appel réseau')
    browser.close()
