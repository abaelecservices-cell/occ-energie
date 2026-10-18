@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title OCC ENERGIE - Reconstruction des 4 HTML

echo ============================================
echo OCC ENERGIE - Reconstruction hors ligne
echo ============================================
echo Cette operation travaille uniquement dans la copie locale.
echo Elle ne modifie ni les branches distantes ni les regles electriques.
echo.

where py >nul 2>nul
if errorlevel 1 (
  echo ERREUR : Lanceur Python "py" introuvable.
  echo Installer Python 3.12 ou plus recent puis relancer ce fichier.
  pause
  exit /b 1
)

echo [1/2] Reconstruction complete et execution des tests documentaires...
py -3 tools\rebuild.py
if errorlevel 1 (
  echo.
  echo ECHEC : reconstruction ou test non valide.
  echo Ne pas publier de livrable et consulter les messages ci-dessus.
  pause
  exit /b 1
)

echo.
echo [2/2] Controle des fichiers produits...
if not exist "OCC_ENERGIE.html" goto :missing
if not exist "OCC_ENERGIE_2024_LITE.html" goto :missing
if not exist "OCC_ENERGIE_TS8.html" goto :missing
if not exist "OCC_ENERGIE_VECTORIEL_MOBILE.html" goto :missing

echo.
echo SUCCES : les quatre HTML ont ete recrees avec tests documentaires.
echo Il reste a effectuer les tests navigateurs, puis a verifier
echo les modifications dans GitHub Desktop avant de publier.
echo.
where git >nul 2>nul
if not errorlevel 1 git status --short
pause
exit /b 0

:missing
echo ERREUR : un ou plusieurs HTML attendus sont absents.
pause
exit /b 1
