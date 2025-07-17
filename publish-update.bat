@echo off
echo ====================================
echo   Publication de mise à jour
echo ====================================
echo.

if "%1"=="" (
    echo Usage: publish-update.bat [VERSION]
    echo Exemple: publish-update.bat 1.0.4
    pause
    exit /b 1
)

set VERSION=%1

echo Étape 1: Mise à jour de la version dans package.json...
powershell -Command "(Get-Content package.json) -replace '\"version\": \".*\"', '\"version\": \"%VERSION%\"' | Set-Content package.json"

echo.
echo Étape 2: Build de l'application...
call npm run build-win

echo.
echo Étape 3: Commit des modifications...
git add .
git commit -m "Version %VERSION% - Mise à jour avec système de mise à jour universel"

echo.
echo Étape 4: Création du tag de version...
git tag v%VERSION%

echo.
echo Étape 5: Push vers GitHub...
git push origin main
git push origin v%VERSION%

echo.
echo Étape 6: Publication automatique sur GitHub...
call npm run publish

echo.
echo ====================================
echo   Mise à jour %VERSION% publiée !
echo ====================================
echo.
echo Les utilisateurs recevront automatiquement la notification de mise à jour :
echo - Installeur NSIS : Mise à jour automatique
echo - Version portable : Notification + téléchargement manuel
echo - Version directe : Notification + téléchargement manuel
echo.
pause
