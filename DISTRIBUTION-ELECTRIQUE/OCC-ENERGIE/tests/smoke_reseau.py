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
    page.wait_for_function("document.querySelector('#net-doc').textContent.includes('Localisation documentaire')")
    assert "Localisation documentaire" in page.locator("#net-doc").inner_text()
    assert "Cles / reperes documentes" in page.locator("#net-doc").inner_text()
    page.locator("svg g.flash").first.wait_for()
    assert page.locator("svg g.flash").count() > 0, "Pas de halo sur le schema complet"

    # Changement de vue : la selection doit rester focusable.
    page.locator("#v2").click()
    page.locator("#net-find").wait_for(timeout=15000)
    assert page.evaluate("NETVIEW") == "uni", "Le bouton HTA doit rester utilisable"
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

    # La recherche globale doit d'abord montrer le conducteur sur le schema.
    # Aucune ouverture automatique de facade / carte ne doit intervenir.
    page.goto(APP.as_uri() + "#/", wait_until="load")
    page.locator("#search").fill(cible)
    page.locator("#results .res").first.wait_for(timeout=15000)
    result_index = page.evaluate("(id) => RES.findIndex(r => r.id === id)", cible)
    assert result_index >= 0, "Le depart exact est absent des resultats globaux"
    page.locator("#results .res").nth(result_index).click()
    page.wait_for_function("CUR.route === 'reseau'", timeout=15000)
    assert page.evaluate("NETVIEW") == "full", "Recherche globale : pas de schema complet"
    assert page.evaluate("NET_FINDER.selected") == cible, "Repere perdu lors de la recherche"
    assert page.locator("#hta svg .trace-wire").count() > 0, "Conducteur non illumine apres recherche"
    assert page.locator("#facade-target").count() == 0, "Facade ouverte sans clic"
    assert page.locator("#net-focus-status").is_visible(), "Bandeau de selection absent"
    assert page.locator("#net-trace-visibility").is_visible(), "Retour d'etat du conducteur absent"
    assert page.evaluate("""() => document.querySelector('#hta').compareDocumentPosition(
      document.querySelector('#net-doc')) & Node.DOCUMENT_POSITION_FOLLOWING"""), "Fiche placee avant le schema"
    page.locator("#net-fit-path").click()
    assert page.locator("#hta svg .trace-wire").count() > 0

    # La recherche ambiguë ne doit pas choisir silencieusement le premier depart.
    page.locator("#net-find").fill("TR")
    page.locator("#net-find").press("Enter")
    assert "Plusieurs équipements" in page.locator("#net-doc").inner_text()
    assert page.evaluate("NET_FINDER.selected") == cible

    # Recherche tableau dans la barre generale : meme premier ecran unifilaire.
    page.locator("#search").fill("TGBT 2")
    board_index = page.evaluate("() => RES.findIndex(r => r.kind === 'board' && r.id === 'TGBT2')")
    assert board_index >= 0, "Le tableau TGBT2 est absent de la recherche"
    page.locator("#results .res").nth(board_index).click()
    page.wait_for_function("CUR.route === 'reseau'", timeout=10000)
    page.wait_for_function("CUR.args[0] === 'TGBT2'")
    assert page.evaluate("NET_FINDER.selected") == "TGBT2"
    assert page.locator("#hta svg").count() == 1

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
    page.wait_for_function("CUR.route === 'b'", timeout=15000)
    page.locator("#facade-target").wait_for(timeout=15000)
    page.locator("#fv svg g.flash").wait_for(timeout=15000)  # focus pose au prochain frame navigateur
    assert "Case" in page.locator("#facade-target").inner_text(), "Repere de case absent"
    page.screenshot(path=str(ARTIFACTS / "parcours-site-facade.png"), full_page=True)

    # Trajet inverse : case ciblée -> onglet des départs -> réseau -> trajet amont
    page.locator('#btabs [data-t="d"]').click()
    page.locator("#facade-return").wait_for(timeout=10000)
    assert cible in page.locator("#facade-to-reseau").get_attribute("data-go")
    page.locator("#facade-to-reseau").click()
    page.locator('#net-path[data-path-target="' + cible + '"]').wait_for(timeout=15000)
    assert page.evaluate("NETVIEW") == "full"
    assert page.locator("#hta svg .trace-wire").count() > 0
    page.locator('#net-doc [data-go="#/site/' + cible + '"]').wait_for(timeout=10000)

    browser.close()

    if errors:
        raise AssertionError("Erreurs JavaScript : " + " | ".join(errors[:10]))
    print("OK : recherche TR1A, halo, navigation, localisation, cles, fiche")
