"""Test navigateur reel de la recherche sur l'unifilaire OCC Energie."""
from pathlib import Path
import os
import shutil
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "OCC_ENERGIE.html"
ARTIFACTS = ROOT / "artifacts"
ARTIFACTS.mkdir(exist_ok=True)
CHROME = os.environ.get("OCC_CHROME") or next(
    (shutil.which(name) for name in ("google-chrome", "chromium", "chromium-browser")
     if shutil.which(name)), None)
if not CHROME:
    raise RuntimeError("Chrome/Chromium absent : test navigateur impossible")
if not APP.is_file():
    raise RuntimeError("Application non construite")

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(
        executable_path=CHROME,
        headless=True,
        args=["--no-sandbox", "--disable-dev-shm-usage",
              "--allow-file-access-from-files"])
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    errors = []
    page.on("pageerror", lambda err: errors.append(str(err)))
    page.goto(APP.as_uri() + "#/reseau", wait_until="load")
    page.locator("#net-find").wait_for(timeout=20000)
    page.locator("#net-find").fill("TR1A")
    page.locator('[data-net-id="TR1A"]').wait_for(timeout=15000)
    page.locator('[data-net-id="TR1A"]').click()
    assert "Localisation documentaire" in page.locator("#net-doc").inner_text()
    assert "Cles / reperes documentes" in page.locator("#net-doc").inner_text()
    assert page.locator("svg g.flash").count() > 0, "Pas de halo sur le schema complet"

    # Changement de vue : la selection doit rester focusable.
    page.locator("#v2").click()
    page.locator("#net-find").wait_for(timeout=15000)
    assert page.locator("#net-find").input_value() == "TR1A"
    page.wait_for_timeout(600)
    assert page.locator("svg g.flash").count() > 0, "Focus perdu en vue unifilaire"

    # Chaque resultat doit pouvoir ouvrir sa fiche sans erreur JS.
    page.locator('#net-doc .btn[data-open="TR1A"]').click()
    assert "open" in page.locator("#sheet").get_attribute("class")
    page.screenshot(path=str(ARTIFACTS / "unifilaire-recherche.png"), full_page=True)

    # Parcours de bout en bout sur un depart avec zone, plan et case de facade
    page.keyboard.press("Escape")
    cible = page.evaluate("""() => {
      const hit = D.nodes.find(n => n.t === 'dep' && n.board === 'TGBT2'
        && facadeFor(n.id) && bestPath(n.id)
        && parcoursContext(n.id).zone && parcoursContext(n.id).plan);
      return hit ? hit.id : null;
    }""")
    assert cible, "Aucun depart TGBT2 suffisamment documente pour le parcours"

    page.goto(APP.as_uri() + "#/reseau/" + cible, wait_until="load")
    page.locator('#net-path[data-path-target="' + cible + '"]').wait_for(timeout=15000)
    assert page.locator("#net-path .trace-step").count() >= 5, "Chemin amont incomplet"
    assert page.evaluate('NETVIEW') == 'full', 'La selection d un depart doit ouvrir le schema complet'
    assert page.locator('#hta svg .trace-wire').count() > 0, "Aucune liaison du schema mise en lumiere"

    page.locator('#net-doc [data-go="#/site/' + cible + '"]').click()
    page.locator("#site-map svg").wait_for(timeout=20000)
    page.locator("#site-map svg .zone.flash").wait_for(timeout=15000)
    assert "Bâtiment ciblé" in page.locator("#view").inner_text()

    page.locator("#site-continue-plan").click()
    page.locator("#plan-selected").wait_for(timeout=15000)
    assert cible in page.locator("#plan-to-facade").get_attribute("data-go")

    page.locator("#plan-to-facade").click()
    page.locator("#facade-target").wait_for(timeout=15000)
    page.locator("#fv svg g.flash").wait_for(timeout=15000)  # focus pose au prochain frame navigateur
    assert "Case" in page.locator("#facade-target").inner_text(), "Repere de case absent"
    page.screenshot(path=str(ARTIFACTS / "parcours-site-facade.png"), full_page=True)

    browser.close()

    if errors:
        raise AssertionError("Erreurs JavaScript : " + " | ".join(errors[:10]))
    print("OK : recherche TR1A, halo, navigation, localisation, cles, fiche")
