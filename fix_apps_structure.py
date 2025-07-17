#!/usr/bin/env python3
"""
Script pour corriger la structure des applications computer-vision-app
Crée les fichiers launch.bat manquants pour toutes les applications
"""

import os
import sys
from pathlib import Path

def create_launch_bat(app_path, app_name):
    """Crée un fichier launch.bat pour une application"""
    launch_content = f"""@echo off
echo ====================================
echo   {app_name}
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
pip install opencv-python mediapipe numpy

echo.
echo Lancement de l'application...
echo.

REM Lancer l'application Python
echo Démarrage de {app_name}...
python main.py

echo Application terminée
pause
"""
    
    launch_path = app_path / "launch.bat"
    with open(launch_path, 'w', encoding='utf-8') as f:
        f.write(launch_content)
    
    print(f"✓ Créé launch.bat pour {app_name}")

def get_app_display_name(app_folder_name):
    """Convertit le nom de dossier en nom d'affichage"""
    name_mapping = {
        'Air-Painter': 'Peinture Aérienne',
        'Fruit-Slicer': 'Coupeur de Fruits',
        'Music-Conductor': 'Chef d\'Orchestre Musical',
        'Presentation-Controller': 'Contrôleur de Présentation',
        'Sign-Language-Translator': 'Traducteur de Langue des Signes',
        'Smart-Home-Control': 'Contrôle Domotique',
        'Virtual-Mouse': 'Souris Virtuelle',
        'Virtual-Piano': 'Piano Virtuel',
        'Audience-Engagement-Monitor': 'Moniteur d\'Engagement de l\'Audience',
        'Driver-Drowsiness-Detection': 'Détecteur de Somnolence au Volant',
        'face_detection': 'Détection de Visage',
        'Face-Controlled-Maze': 'Labyrinthe Contrôlé par Visage',
        'Focus-Mode-Enforcer': 'Mode Focus Forcé',
        'Virtual-Try-On': 'Essayage Virtuel',
        'Dance-Tutor': 'Professeur de Danse',
        'Fall-Detection-System': 'Système de Détection de Chute',
        'Pose-Invaders': 'Envahisseurs de Pose',
        'Posture-Coach': 'Coach de Posture',
        'Virtual-Fitness-Trainer': 'Entraîneur Fitness Virtuel',
        'Yoga-Pose-Analyzer': 'Analyseur de Poses de Yoga'
    }
    
    return name_mapping.get(app_folder_name, app_folder_name.replace('-', ' '))

def main():
    base_path = Path("C:/Users/USER/computer-vision-app - Copie/python-apps")
    
    if not base_path.exists():
        print(f"❌ Erreur: Le chemin {base_path} n'existe pas")
        return
    
    print("🔧 Correction de la structure des applications...")
    print("=" * 50)
    
    # Parcourir tous les dossiers d'applications
    for category_dir in base_path.iterdir():
        if category_dir.is_dir():
            print(f"\n📁 Catégorie: {category_dir.name}")
            
            for app_dir in category_dir.iterdir():
                if app_dir.is_dir():
                    app_name = app_dir.name
                    launch_bat_path = app_dir / "launch.bat"
                    main_py_path = app_dir / "main.py"
                    
                    # Vérifier si launch.bat existe
                    if not launch_bat_path.exists():
                        # Créer launch.bat
                        display_name = get_app_display_name(app_name)
                        create_launch_bat(app_dir, display_name)
                    else:
                        print(f"  ✓ {app_name} - launch.bat existe déjà")
                    
                    # Vérifier si main.py existe et n'est pas vide
                    if main_py_path.exists():
                        content = main_py_path.read_text(encoding='utf-8')
                        if content.strip().startswith('# Placeholder'):
                            print(f"  ⚠️  {app_name} - main.py est un placeholder")
                        else:
                            print(f"  ✓ {app_name} - main.py semble fonctionnel")
                    else:
                        print(f"  ❌ {app_name} - main.py manquant")
    
    print("\n" + "=" * 50)
    print("🎉 Correction terminée!")
    print("\nLes applications ont maintenant la structure correcte:")
    print("- main.py (code principal)")
    print("- launch.bat (fichier de lancement)")

if __name__ == "__main__":
    main()
