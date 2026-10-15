"""Fonctions historiques, simulation, thèmes et journal local sur contexte jetable."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=os.environ['OCC_CHROME'], headless=True)
    page = browser.new_page(accept_downloads=True)
    errors = []
    page.on('pageerror', lambda err: errors.append(str(err)))
    for name in ('OCC_ENERGIE.html', 'OCC_ENERGIE_2024_LITE.html',
                 'OCC_ENERGIE_TS8.html', 'OCC_ENERGIE_VECTORIEL_MOBILE.html'):
        page.goto((ROOT / name).as_uri() + '#/historique2024')
        assert page.locator('.hx24entry').count() == 36
        page.locator('#hx24-query').fill('TS42')
        assert 0 < page.locator('.hx24entry:visible').count() < 36
        page.locator('#hx24-query').fill('')
        page.locator('#hx24-ages').click()
        assert page.locator('.hx24entry').count() == 68
        page.locator('#themebtn').click()
        theme = page.locator('html').get_attribute('data-theme')
        page.locator('#themebtn').click()
        assert page.locator('html').get_attribute('data-theme') != theme
    page.goto((ROOT / 'OCC_ENERGIE.html').as_uri() + '#/reseau')
    assert page.evaluate('''() => {
      SANDBOX = true; resetSim();
      const before = JSON.stringify(SIM);
      if (setSw('TGBT2_QC', true)) throw Error('Couplage non qualifié accepté');
      if (JSON.stringify(SIM) !== before) throw Error('Refus non atomique');
      if (!LAST_CONFLICT.some(c => c.kind === 'cpl')) throw Error('Alerte absente');
      closeSheet(); resetSim();
      if (!setSw('SRC_CNR', false) || !atsActive() || !isClosed('PL_A04') ||
          isClosed('PL_B01')) throw Error('Permutation de secours incorrecte');
      if (!simNotice()) throw Error('Simulation non signalée');
      resetSim(); SANDBOX = false; return true;
    }''')
    page.evaluate('location.hash="#/entretien"; route(false)')
    page.locator('#le').fill('TEST CONSOLIDATION')
    page.locator('#li').fill('Test automatisé')
    page.locator('#lo').fill('Observation de test ; sans intervention réelle')
    page.locator('#ladd').click()
    assert page.evaluate('getLog()[0].e') == 'TEST CONSOLIDATION'
    page.reload()
    assert page.evaluate('getLog()[0].e') == 'TEST CONSOLIDATION'
    with page.expect_download() as download:
        page.locator('#lexp').click()
    downloaded = download.value
    assert 'TEST CONSOLIDATION' in Path(downloaded.path()).read_text(encoding='utf-8-sig')
    page.locator('[data-del="0"]').click()
    assert page.evaluate('getLog().length') == 0
    page.keyboard.press('/')
    assert page.locator('#search').evaluate('(el) => el === document.activeElement')
    assert not errors, errors
    print('OK fonctions : 4 HTML, référentiel, thèmes, simulation, journal/CSV, clavier')
    browser.close()
