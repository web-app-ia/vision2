# Configuration des Applications Computer Vision

Ce dossier contient les fichiers de configuration pour personnaliser l'affichage et les détails des applications dans l'interface.

## Structure des fichiers

### 1. `app_details.json`
Contient les détails complets de chaque application :

```json
{
  "nom_application": {
    "name": "Nom affiché",
    "description": "Description complète de l'application",
    "features": [
      "Fonctionnalité 1",
      "Fonctionnalité 2",
      "Fonctionnalité 3"
    ],
    "requirements": [
      "Prérequis 1",
      "Prérequis 2",
      "Prérequis 3"
    ],
    "usage": "Instructions d'utilisation détaillées"
  }
}
```

### 2. `categories.json`
Définit les catégories d'applications avec leurs icônes et couleurs :

```json
{
  "categories": {
    "nom_categorie": {
      "name": "🔥 Nom affiché",
      "description": "Description de la catégorie",
      "icon": "🔥",
      "color": "#ff6b6b"
    }
  }
}
```

## Comment modifier les configurations

### Ajouter une nouvelle application

1. **Ajoutez l'entrée dans `app_details.json`** :
```json
{
  "mon_nouvelle_app": {
    "name": "Mon Application",
    "description": "Une application fantastique qui fait des choses incroyables",
    "features": [
      "Fonctionnalité innovante",
      "Interface intuitive",
      "Performance optimisée"
    ],
    "requirements": [
      "Camera/webcam",
      "Python 3.8+",
      "Bibliothèque spécifique"
    ],
    "usage": "Lancez l'application et suivez les instructions à l'écran."
  }
}
```

2. **Créez le dossier de l'application** :
```
python-apps/
  └── categorie/
      └── mon_nouvelle_app/
          ├── main.py
          └── launch.bat (optionnel)
```

### Ajouter une nouvelle catégorie

1. **Ajoutez la catégorie dans `categories.json`** :
```json
{
  "ma_nouvelle_categorie": {
    "name": "🚀 Ma Catégorie",
    "description": "Applications de ma nouvelle catégorie",
    "icon": "🚀",
    "color": "#4CAF50"
  }
}
```

2. **Créez le dossier de la catégorie** :
```
python-apps/
  └── ma_nouvelle_categorie/
```

### Modifier les détails d'une application existante

1. **Trouvez l'application dans `app_details.json`**
2. **Modifiez les champs souhaités** :
   - `name` : Le nom affiché dans l'interface
   - `description` : Description complète
   - `features` : Liste des fonctionnalités
   - `requirements` : Liste des prérequis
   - `usage` : Instructions d'utilisation

### Personnaliser une catégorie

1. **Trouvez la catégorie dans `categories.json`**
2. **Modifiez les propriétés** :
   - `name` : Nom affiché (avec émoji)
   - `description` : Description de la catégorie
   - `icon` : Émoji représentant la catégorie
   - `color` : Couleur hexadécimale pour l'affichage

## Couleurs recommandées (charte graphique bleu foncé et blanc)

- Bleu foncé principal : `#1e3c72`
- Bleu moyen : `#2a5298`
- Blanc : `#ffffff`
- Gris clair : `#f8f9fa`
- Vert succès : `#28a745`
- Rouge erreur : `#dc3545`
- Orange attention : `#ffc107`

## Émojis recommandés

- 🎯 Suivi/tracking
- 👋 Gestes
- 🔍 Détection
- 🧠 Intelligence/reconnaissance
- ✨ Effets
- 📊 Analyse
- 🥽 Réalité augmentée
- 🎨 Créatif
- 🔧 Outils
- 🚀 Performance

## Exemple complet

Voici un exemple complet pour ajouter une application de réalité augmentée :

1. **Dans `app_details.json`** :
```json
{
  "ar_face_filter": {
    "name": "Filtres AR Visage",
    "description": "Application de réalité augmentée pour appliquer des filtres en temps réel sur le visage",
    "features": [
      "Détection faciale en temps réel",
      "Filtres 3D interactifs",
      "Suivi précis des expressions",
      "Sauvegarde photo/vidéo"
    ],
    "requirements": [
      "Camera/webcam HD",
      "Python 3.8+",
      "OpenCV",
      "MediaPipe",
      "Processeur performant"
    ],
    "usage": "Regardez la caméra et sélectionnez un filtre dans le menu. Utilisez les gestes pour interagir avec les éléments 3D."
  }
}
```

2. **Structure du dossier** :
```
python-apps/
  └── realite-augmentee/
      └── ar_face_filter/
          ├── main.py
          ├── launch.bat
          └── assets/
              ├── models/
              └── textures/
```

## Redémarrage nécessaire

Après avoir modifié les fichiers de configuration, redémarrez l'application pour voir les changements.

## Dépannage

- **Les modifications n'apparaissent pas** : Vérifiez la syntaxe JSON avec un validateur
- **Erreur de chargement** : Assurez-vous que les fichiers sont bien encodés en UTF-8
- **Application non détectée** : Vérifiez que le fichier `main.py` existe dans le dossier de l'application
