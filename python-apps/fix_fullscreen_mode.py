#!/usr/bin/env python3
"""
Script pour corriger le mode fenêtre maximisée des applications Python OpenCV
Remplace WINDOW_FULLSCREEN par WINDOW_AUTOSIZE pour occuper seulement la frame
"""

import os
import re
import sys
from pathlib import Path

def fix_maximized_mode_in_file(file_path):
    """
    Corrige le mode fenêtre maximisée dans un fichier Python utilisant OpenCV
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier si le fichier contient du code de fenêtre maximisée à corriger
        if 'cv2.WINDOW_NORMAL' not in content and 'WND_PROP_FULLSCREEN' not in content:
            print(f"Aucun mode fenêtre maximisée à corriger dans {file_path}")
            return False
        
        original_content = content
        
        # 1. Remplacer cv2.WINDOW_NORMAL par cv2.WINDOW_NORMAL
        content = content.replace('cv2.WINDOW_NORMAL', 'cv2.WINDOW_NORMAL')
        
        # 2. Remplacer les setWindowProperty avec WND_PROP_FULLSCREEN
        content = re.sub(
            r'cv2\.setWindowProperty\(([^,]+),\s*cv2\.WND_PROP_FULLSCREEN,\s*cv2\.WINDOW_NORMAL\)',
            r'cv2.resizeWindow(\1, 1200, 800)',
            content
        )
        
        # 3. Remplacer les fonctions setup_fullscreen_window
        content = re.sub(
            r'def setup_fullscreen_window\(window_name\):.*?return True',
            '''def setup_maximized_window(window_name):
    """Configure une fenêtre pour occuper une grande partie de l'écran"""
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1200, 800)
    return True''',
            content,
            flags=re.DOTALL
        )
        
        # 4. Remplacer les fonctions toggle_fullscreen
        content = re.sub(
            r'def toggle_fullscreen\(window_name, is_fullscreen\):.*?return True',
            '''def toggle_window_mode(window_name, is_maximized):
    """Bascule entre mode maximisé et fenêtre normale"""
    if is_maximized:
        cv2.resizeWindow(window_name, 800, 600)
        print("Mode fenêtre normale activé")
        return False
    else:
        cv2.resizeWindow(window_name, 1200, 800)
        print("Mode fenêtre maximisée activé")
        return True''',
            content,
            flags=re.DOTALL
        )
        
        # 5. Remplacer les appels aux fonctions
        content = content.replace('setup_maximized_window(', 'setup_maximized_window(')
        content = content.replace('toggle_window_mode(', 'toggle_window_mode(')
        
        # 6. Remplacer les variables maximized_mode
        content = content.replace('maximized_mode', 'maximized_mode')
        
        # 7. Mettre à jour les messages
        content = re.sub(
            r'print\("Mode fenêtre maximisée activé[^"]*"\)',
            'print("Mode fenêtre maximisée activé - Appuyez sur \'f\' pour basculer")',
            content
        )
        
        # 8. Remplacer les commentaires
        content = content.replace('# Configuration pour le mode fenêtre maximisée', '# Configuration pour le mode fenêtre maximisée')
        content = content.replace('# Configuration de la fenêtre maximisée', '# Configuration de la fenêtre maximisée')
        
        # 9. Traiter les cas avec namedWindow et setWindowProperty sur des lignes séparées
        pattern = r'cv2\.namedWindow\(([^,]+),\s*cv2\.WINDOW_NORMAL\)\s*\n\s*cv2\.setWindowProperty\(\1,\s*cv2\.WND_PROP_FULLSCREEN,\s*cv2\.WINDOW_NORMAL\)'
        replacement = r'cv2.namedWindow(\1, cv2.WINDOW_NORMAL)\ncv2.resizeWindow(\1, 1200, 800)'
        content = re.sub(pattern, replacement, content)
        
        # 10. Corriger les instructions à l'écran
        content = content.replace('redimensionner la fenêtre', 'redimensionner la fenêtre')
        
        # 11. Corriger les commentaires en français
        content = content.replace('fenêtre maximisée', 'fenêtre maximisée')
        
        # Vérifier si des changements ont été effectués
        if content != original_content:
            # Sauvegarder le fichier modifié
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"Mode fenêtre maximisée corrigé dans {file_path}")
            return True
        else:
            print(f"Aucune modification nécessaire dans {file_path}")
            return False
            
    except Exception as e:
        print(f"Erreur lors du traitement de {file_path}: {e}")
        return False

def process_directory(directory_path):
    """
    Traite tous les fichiers .py dans le répertoire
    """
    processed_count = 0
    error_count = 0
    
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                print(f"\nTraitement de {file_path}...")
                
                try:
                    if fix_maximized_mode_in_file(file_path):
                        processed_count += 1
                    else:
                        error_count += 1
                except Exception as e:
                    print(f"Erreur: {e}")
                    error_count += 1
    
    return processed_count, error_count

def main():
    print("=== Script de correction du mode fenêtre maximisée ===")
    print("Ce script corrige le mode fenêtre maximisée pour qu'il occupe seulement la frame de la fenêtre")
    
    # Obtenir le répertoire des applications Python
    script_dir = Path(__file__).parent
    python_apps_dir = script_dir
    
    if not python_apps_dir.exists():
        print(f"Erreur: Le répertoire {python_apps_dir} n'existe pas")
        sys.exit(1)
    
    print(f"Répertoire de traitement: {python_apps_dir}")
    
    # Traiter tous les fichiers
    processed, errors = process_directory(python_apps_dir)
    
    print(f"\n=== Résultats ===")
    print(f"Fichiers traités avec succès: {processed}")
    print(f"Fichiers avec erreurs: {errors}")
    print(f"Total: {processed + errors}")
    
    if processed > 0:
        print(f"\nLes applications modifiées utilisent maintenant:")
        print("- Mode fenêtre maximisée au lieu du fenêtre maximisée système")
        print("- Possibilité de redimensionner et déplacer la fenêtre")
        print("- Touche 'f' pour basculer entre modes")
        print("- Pas de blocage en mode fenêtre maximisée système")

if __name__ == "__main__":
    main()
