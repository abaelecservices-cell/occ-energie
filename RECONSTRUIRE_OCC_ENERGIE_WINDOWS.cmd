@echo off
setlocal EnableExtensions
chcp 65001 >nul
cd /d "%~dp0"
if not exist "DISTRIBUTION-ELECTRIQUE\OCC-ENERGIE\tools\build_data.py" (
  echo ERREUR : placer ce fichier a la racine du depot occ-energie.
  pause
  exit /b 2
)
where git >nul 2>&1 || (echo Git introuvable. & pause & exit /b 2)
where py >nul 2>&1 || (echo Python 3 introuvable. & pause & exit /b 2)
git diff --quiet || (echo Modifications locales non enregistrees. & pause & exit /b 3)
git diff --cached --quiet || (echo Modifications indexees non enregistrees. & pause & exit /b 3)
git pull --ff-only || (echo Echec git pull. & pause & exit /b 3)
cd /d "DISTRIBUTION-ELECTRIQUE\OCC-ENERGIE"
py -3 tools\rebuild.py || goto :fail
echo.
echo RECONSTRUCTION OK : les quatre livrables OCC_ENERGIE*.html
cd /d "%~dp0"
git status --short
set /p PUSH="Publier la reconstruction sur GitHub ? (oui/N) : "
if /i not "%PUSH%"=="oui" goto :success
git add DISTRIBUTION-ELECTRIQUE/OCC-ENERGIE/build/data.json DISTRIBUTION-ELECTRIQUE/OCC-ENERGIE/OCC_ENERGIE*.html DISTRIBUTION-ELECTRIQUE/OCC-ENERGIE/docs
git diff --cached --quiet && goto :success
git commit -m "build(occ-energie): regenerer facades terrain et HTML" || goto :fail
git push || goto :fail
:success
echo Termine. HTML utilisable depuis le dossier OCC-ENERGIE.
pause
exit /b 0
:fail
echo Echec de reconstruction ou des tests. Aucun push automatique.
pause
exit /b 1
