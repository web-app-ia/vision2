@echo off
echo ====================================
echo   Subway Surfers - Course Infinie
echo ====================================
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
pip install pygame numpy

echo.
echo Lancement de l'application...
echo.

REM Lancer l'application Python
echo Démarrage de Subway Surfers...
python main.py

echo Application terminée
pause
