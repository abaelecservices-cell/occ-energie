@echo off
setlocal EnableExtensions
chcp 65001 >nul
cd /d "%~dp0"
title OCC ENERGIE - Reconstruction des livrables

echo ===========================================================
echo OCC ENERGIE - Reconstruire les HTML depuis les sources Git
echo ===========================================================
echo.

if not exist "tools\rebuild.py" (
  echo ERREUR : lancer ce fichier depuis le dossier OCC-ENERGIE.
  pause
  exit /b 1
)

where py >nul 2>nul
if not errorlevel 1 (
  py -3 tools\rebuild.py
) else (
  where python >nul 2>nul
  if errorlevel 1 (
    echo ERREUR : Python 3 est introuvable sur ce poste.
    echo Installer Python 3 avec les autorisations du poste.
    pause
    exit /b 1
  )
  python tools\rebuild.py
)

if errorlevel 1 (
  echo.
  echo ECHEC : aucune livraison ne doit etre publiee avant correction.
  echo Consulter l'erreur affichée ci-dessus.
  pause
  exit /b 1
)

echo.
echo Creation facultative d'un HTML COMPLET ET AUTONOME (zoom 12 inclus)...
where py >nul 2>nul
if not errorlevel 1 (
  py -3 tools\build_app.py --output OCC_ENERGIE_STANDALONE.html
) else (
  python tools\build_app.py --output OCC_ENERGIE_STANDALONE.html
)
if errorlevel 1 (
  echo ECHEC : variante autonome non creee. Versions GitHub conservees.
  pause
  exit /b 1
)

echo.
echo RECONSTRUCTION ET TESTS DOCUMENTAIRES TERMINES.
echo - OCC_ENERGIE.html : version complete avec tuiles satellites locales
echo - OCC_ENERGIE_2024_LITE.html : version autonome legere
echo - OCC_ENERGIE_SAP_20261017_LITE.html : copie du mode leger
echo - OCC_ENERGIE_TS8.html : version reconstruite
echo - OCC_ENERGIE_VECTORIEL_MOBILE.html : version reconstruite
echo - OCC_ENERGIE_STANDALONE.html : un seul HTML complet, 34 tuiles integrees
echo.
echo Ces fichiers sont locaux : la publication GitHub n'est pas automatique.
echo Verifier les parcours et la coherence documentaire avant la fusion.
echo.
pause
exit /b 0
