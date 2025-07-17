# Changelog

## [1.0.4] - 2025-01-17

### ✨ Améliorations
- **Correction du mode plein écran** : Les applications Python utilisent maintenant des fenêtres redimensionnables au lieu du mode plein écran système
- **Meilleure expérience utilisateur** : Les fenêtres peuvent être redimensionnées, déplacées et minimisées
- **Flexibilité d'affichage** : Les applications s'ouvrent en mode fenêtre maximisée (1200x800) par défaut

### 🔧 Corrections techniques
- Remplacement de `cv2.WINDOW_FULLSCREEN` par `cv2.WINDOW_NORMAL` avec redimensionnement automatique
- Mise à jour des fonctions `setup_fullscreen_window()` vers `setup_maximized_window()`
- Correction des fonctions `toggle_fullscreen()` vers `toggle_window_mode()`
- Ajout de `cv2.resizeWindow()` pour un contrôle précis des dimensions

### 📱 Applications concernées
- **13 applications** ont été mises à jour avec les nouvelles fonctionnalités de fenêtrage
- **Toutes les catégories** sont affectées : gestures, tracking, detection, etc.

### 🎮 Contrôles mis à jour
- **Touche 'f'** : Bascule entre mode maximisé (1200x800) et mode normal (800x600)
- **Touche 'q'** : Quitte l'application
- **Touche 'ESC'** : Redimensionne la fenêtre

### 🚀 Performances
- **Temps de lancement** amélioré des applications Python
- **Stabilité** accrue lors du redimensionnement des fenêtres
- **Compatibilité** renforcée avec différentes résolutions d'écran

### 📋 Fichiers modifiés
- `python-apps/apply_fullscreen_mode.py` → Renommé en mode fenêtre maximisée
- `python-apps/fix_fullscreen_mode.py` → Nouveau script de correction
- **13 applications Python** avec corrections appliquées
- Interface Electron mise à jour pour gérer les nouvelles dimensions

---

## [1.0.3] - Version précédente
- Fonctionnalités de base de l'application
- Interface Electron
- Applications Python avec mode plein écran système

---

### 🔗 Liens utiles
- [Repository GitHub](https://github.com/web-app-ia/vision2)
- [Documentation](./README.md)
- [Guide d'installation](./DEPLOYMENT.md)
