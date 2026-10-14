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
    page.locator('#net-doc [data-open="TR1A"]').click()
    assert "open" in page.locator("#sheet").get_attribute("class")
    page.screenshot(path=str(ARTIFACTS / "unifilaire-recherche.png"), full_page=True)
    browser.close()

    if errors:
        raise AssertionError("Erreurs JavaScript : " + " | ".join(errors[:10]))
    print("OK : recherche TR1A, halo, navigation, localisation, cles, fiche")
