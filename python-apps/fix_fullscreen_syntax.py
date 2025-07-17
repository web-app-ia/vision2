#!/usr/bin/env python3
"""
Script pour réparer les erreurs de syntaxe dans les applications modifiées
"""

import os
import re
import sys
from pathlib import Path

def fix_syntax_errors_in_file(file_path):
    """
    Répare les erreurs de syntaxe dans un fichier Python
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier si le fichier contient des erreurs typiques
        if 'elif key == ord(\\'f\\'):' in content:
            # Corriger l'erreur de syntaxe avec les guillemets
            content = content.replace('elif key == ord(\\'f\\'):', 'elif key == ord(\'f\'):')
            
            # Corriger l'indentation si nécessaire
            lines = content.split('\n')
            fixed_lines = []
            i = 0
            
            while i < len(lines):
                line = lines[i]
                
                # Rechercher la ligne avec elif key == ord('f'):
                if 'elif key == ord(\'f\'):' in line:
                    # Assurer la bonne indentation
                    indent = len(line) - len(line.lstrip())
                    
                    # Ajouter la ligne corrigée
                    fixed_lines.append(line)
                    
                    # Ajouter la ligne suivante avec la bonne indentation
                    if i + 1 < len(lines):
                        next_line = lines[i + 1]
                        if 'fullscreen_mode = toggle_fullscreen' in next_line:
                            # Assurer la bonne indentation pour la ligne suivante
                            fixed_lines.append(' ' * (indent + 4) + 'fullscreen_mode = toggle_fullscreen(window_name, fullscreen_mode)')
                            i += 1  # Passer la ligne suivante
                        else:
                            fixed_lines.append(' ' * (indent + 4) + 'fullscreen_mode = toggle_fullscreen(window_name, fullscreen_mode)')
                    else:
                        fixed_lines.append(' ' * (indent + 4) + 'fullscreen_mode = toggle_fullscreen(window_name, fullscreen_mode)')
                    
                    i += 1
                    continue
                
                # Corriger les problèmes d'indentation autour des conditions if/elif
                if 'if key == ord(' in line and 'elif key == ord(' in lines[i-1] if i > 0 else False:
                    # Cette ligne devrait être elif, pas if
                    line = line.replace('if key == ord(', 'elif key == ord(')
                
                fixed_lines.append(line)
                i += 1
            
            content = '\n'.join(fixed_lines)
            
            # Sauvegarder le fichier corrigé
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"Erreurs de syntaxe corrigées dans {file_path}")
            return True
        
        return False
        
    except Exception as e:
        print(f"Erreur lors de la correction de {file_path}: {e}")
        return False

def process_directory(directory_path):
    """
    Traite tous les fichiers main.py dans le répertoire
    """
    processed_count = 0
    
    for root, dirs, files in os.walk(directory_path):
        if 'main.py' in files:
            main_py_path = os.path.join(root, 'main.py')
            
            try:
                if fix_syntax_errors_in_file(main_py_path):
                    processed_count += 1
            except Exception as e:
                print(f"Erreur: {e}")
    
    return processed_count

def main():
    print("=== Script de réparation des erreurs de syntaxe ===")
    
    # Obtenir le répertoire des applications Python
    script_dir = Path(__file__).parent
    python_apps_dir = script_dir
    
    if not python_apps_dir.exists():
        print(f"Erreur: Le répertoire {python_apps_dir} n'existe pas")
        sys.exit(1)
    
    print(f"Répertoire de traitement: {python_apps_dir}")
    
    # Traiter tous les fichiers
    processed = process_directory(python_apps_dir)
    
    print(f"\n=== Résultats ===")
    print(f"Fichiers corrigés: {processed}")

if __name__ == "__main__":
    main()
