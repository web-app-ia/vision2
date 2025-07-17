#!/usr/bin/env python3
"""
Script pour appliquer le mode fenêtre maximisée à toutes les applications Python OpenCV
"""

import os
import re
import sys
from pathlib import Path

def add_fullscreen_support_to_file(file_path):
    """
    Ajoute le support du mode fenêtre maximisée à un fichier Python utilisant OpenCV
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier si le fichier utilise cv2.imshow
        if 'cv2.imshow' not in content:
            print(f"Aucun cv2.imshow trouvé dans {file_path}")
            return False
        
        # Vérifier si le support fenêtre maximisée est déjà présent
        if 'cv2.WINDOW_NORMAL' in content:
            print(f"Support fenêtre maximisée déjà présent dans {file_path}")
            return False
        
        # Rechercher la première occurrence de cv2.imshow
        imshow_pattern = r'cv2\.imshow\s*\(\s*[\'"]([^\'"]*)[\'"]'
        match = re.search(imshow_pattern, content)
        
        if not match:
            print(f"Impossible de trouver le pattern cv2.imshow dans {file_path}")
            return False
            
        window_name = match.group(1)
        
        # Ajouter le code pour le mode fenêtre maximisée après les imports
        import_pattern = r'(import cv2.*?\n)'
        fullscreen_code = f'''
# Configuration pour le mode fenêtre maximisée
def setup_maximized_window(window_name):
    """Configure une fenêtre pour occuper une grande partie de l'écran"""
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1200, 800)
    return True

def toggle_window_mode(window_name, is_maximized):
    """Bascule entre mode maximisé et fenêtre normale"""
    if is_maximized:
        cv2.resizeWindow(window_name, 800, 600)
        print("Mode fenêtre normale activé")
        return False
    else:
        cv2.resizeWindow(window_name, 1200, 800)
        print("Mode fenêtre maximisée activé")
        return True

'''
        
        # Rechercher où ajouter le code de configuration
        if 'while True:' in content or 'while ' in content:
            # Ajouter avant la boucle principale
            before_loop_pattern = r'(\s*)(while.*?:)'
            setup_code = f'''
        # Configuration de la fenêtre maximisée
        window_name = "{window_name}"
        setup_maximized_window(window_name)
        maximized_mode = True
        print("Mode fenêtre maximisée activé - Appuyez sur 'f' pour basculer")
        
        '''
            
            # Ajouter le code après les imports
            import_match = re.search(import_pattern, content)
            if import_match:
                content = content[:import_match.end()] + fullscreen_code + content[import_match.end():]
            
            # Ajouter avant la boucle
            content = re.sub(before_loop_pattern, setup_code + r'\1\2', content)
            
            # Ajouter la gestion des touches 'f' dans la boucle
            key_pattern = r'(key = cv2\.waitKey\(.*?\).*?\n)(.*?)(if key.*?:)'
            key_replacement = r'\1\2elif key == ord(\'f\'):\n                    maximized_mode = toggle_window_mode(window_name, maximized_mode)\n                \3'
            content = re.sub(key_pattern, key_replacement, content, flags=re.DOTALL)
            
            # Sauvegarder le fichier modifié
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"Mode fenêtre maximisée ajouté à {file_path}")
            return True
        else:
            print(f"Impossible de trouver la boucle principale dans {file_path}")
            return False
            
    except Exception as e:
        print(f"Erreur lors du traitement de {file_path}: {e}")
        return False

def process_directory(directory_path):
    """
    Traite tous les fichiers main.py dans le répertoire
    """
    processed_count = 0
    error_count = 0
    
    for root, dirs, files in os.walk(directory_path):
        if 'main.py' in files:
            main_py_path = os.path.join(root, 'main.py')
            print(f"\nTraitement de {main_py_path}...")
            
            try:
                if add_fullscreen_support_to_file(main_py_path):
                    processed_count += 1
                else:
                    error_count += 1
            except Exception as e:
                print(f"Erreur: {e}")
                error_count += 1
    
    return processed_count, error_count

def main():
    print("=== Script d'application du mode fenêtre maximisée ===")
    print("Ce script ajoute le support du mode fenêtre maximisée à toutes les applications Python OpenCV")
    
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
        print(f"\nLes applications modifiées supportent maintenant:")
        print("- Mode fenêtre maximisée par défaut au démarrage")
        print("- Touche 'f' pour basculer entre fenêtre maximisée et fenêtre normale")
        print("- Affichage des messages de confirmation")

if __name__ == "__main__":
    main()
