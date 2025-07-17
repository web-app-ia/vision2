# Computer Vision Applications

Une application Electron qui sert de répertoire pour des applications Python de Computer Vision.

## Fonctionnalités

- **Interface moderne** : Interface Electron avec design glassmorphism
- **Gestion des applications** : Lancement et arrêt des applications Python
- **Catégorisation** : Applications organisées par catégories
- **Suivi en temps réel** : Voir les applications en cours d'exécution
- **Recherche** : Recherche d'applications par nom ou catégorie

## Applications incluses

### 👋 Gestes
- **hand_tracking** : Suivi des mains en temps réel avec MediaPipe
  - Détection des gestes (doigts levés)
  - Calcul de la vitesse de mouvement
  - Suivi de 2 mains simultanément

### 🔍 Détection
- **face_detection** : Détection de visages avec OpenCV
  - Détection des visages, yeux et sourires
  - Statistiques en temps réel
  - Sauvegarde des captures

### 🎯 Suivi
- **pose_estimation** : Estimation de la pose corporelle avec MediaPipe
  - Suivi des 33 points du corps
  - Squelette en temps réel
  - Segmentation corporelle

## Installation

1. Clonez ou téléchargez le projet
2. Installez les dépendances Node.js :
   ```bash
   npm install
   ```

## Utilisation

### Lancer l'application Electron
```bash
npm start
```

### Développement
```bash
npm run dev
```

### Construire l'application
```bash
npm run build
```

## Prérequis

- Node.js et npm
- Python 3.7+ avec pip
- Webcam connectée

## Dépendances Python

Les dépendances sont automatiquement installées lors du premier lancement :
- opencv-python
- mediapipe
- numpy

## Contrôles des applications

### Hand Tracking
- `q` ou `ESC` : Quitter
- `r` : Réinitialiser
- `s` : Capturer une image

### Face Detection
- `q` ou `ESC` : Quitter
- `s` : Sauvegarder une capture
- `r` : Réinitialiser les compteurs
- `+` : Augmenter la sensibilité
- `-` : Diminuer la sensibilité

### Pose Estimation
- `q` : Quitter

## Structure du projet

```
computer-vision-app/
├── src/
│   ├── main.js          # Processus principal Electron
│   ├── preload.js       # Script de préchargement
│   ├── index.html       # Interface utilisateur
│   ├── styles.css       # Styles CSS
│   └── renderer.js      # Logique frontend
├── python-apps/
│   ├── gestures/
│   │   └── hand_tracking/
│   ├── detection/
│   │   └── face_detection/
│   └── tracking/
│       └── pose_estimation/
└── assets/
    └── (icônes et ressources)
```

## Développement

Pour ajouter une nouvelle application Python :

1. Créez un dossier dans la catégorie appropriée
2. Ajoutez un fichier `main.py` avec votre application
3. Créez un fichier `launch.bat` pour le lancement
4. Redémarrez l'application Electron

## Licence

MIT License
