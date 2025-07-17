@echo off
echo ====================================
echo   Application Détection de Visage
echo ====================================
echo.

REM Vérifier et demander les privilèges administrateur
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Demande des privilèges administrateur pour accéder à la caméra...
    powershell -Command "Start-Process '%~f0' -Verb runAs"
    exit /b
)

echo Exécution avec les privilèges administrateur
echo.

REM Changer vers le répertoire de l'application
cd /d "%~dp0"

REM Vérifier si Python est installé
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERREUR: Python n'est pas installé ou n'est pas dans le PATH
    echo Veuillez installer Python depuis https://python.org
    pause
    exit /b 1
)

echo Installation/Mise à jour des dépendances...
pip install opencv-python numpy

echo.
echo Lancement de l'application...
echo.

REM Lancer l'application Python
echo Démarrage de l'application de détection de visage...
echo Tentative d'accès à la caméra...
python main.py

REM Si problème d'accès à la caméra, proposer le mode démonstration
echo.
echo Souhaitez-vous lancer le mode démonstration ? (o/n)
set /p choice=Votre choix: 

if /i "%choice%"=="o" (
    echo Lancement du mode démonstration...
    python demo_mode.py
) else if /i "%choice%"=="oui" (
    echo Lancement du mode démonstration...
    python demo_mode.py
) else (
    echo Mode démonstration ignoré
)

echo.
echo Application terminée
pause
