# Jeux et Loisirs - Collection de Jeux Python

Cette collection contient 6 jeux développés en Python avec la librairie Pygame, inspirés de jeux populaires.

## Installation

1. **Installer Python** (version 3.7 ou supérieure)
2. **Installer les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```

## Jeux Disponibles

### 1. Super Mario (`super_mario.py`)
Un jeu de plateforme inspiré du célèbre Mario Bros.

**Contrôles :**
- Flèches directionnelles ou WASD : Déplacement
- Espace ou Flèche Haut : Sauter
- Échap : Quitter

**Objectif :** Collecter les pièces, éviter les ennemis et survivre le plus longtemps possible.

### 2. Snake (`snake.py`)
Le jeu classique du serpent avec des améliorations.

**Contrôles :**
- Flèches directionnelles : Déplacement
- R : Redémarrer
- Échap : Quitter

**Objectif :** Manger la nourriture pour grandir, éviter les murs et votre propre corps.

**Bonus :**
- Nourriture rouge : +10 points
- Nourriture jaune : +20 points + augmentation de vitesse
- Nourriture bleue : -5 points + réduction de taille

### 3. Basket Shoots (`basket_shoots.py`)
Un jeu de tir au panier avec physique réaliste.

**Contrôles :**
- Flèches ou A/D : Déplacer le joueur
- Clic souris : Tirer (direction et force selon la position du clic)
- R : Redémarrer
- Échap : Quitter

**Objectif :** Marquer le maximum de paniers en 60 secondes.

**Fonctionnalités :**
- Physique réaliste avec gravité
- Effet du vent
- Trajectoire prévisionnelle
- Statistiques de précision

### 4. Car Race (`car_race.py`)
Un jeu de course avec obstacles et powerups.

**Contrôles :**
- Flèches directionnelles ou WASD : Conduire
- Échap : Quitter

**Objectif :** Éviter les obstacles et collecter les bonus.

**Fonctionnalités :**
- Physique de conduite réaliste
- Powerups (vitesse, bouclier, points)
- Obstacles variés (normaux, bonus, malus)
- Système de vies et d'invincibilité

### 5. Hungry Birds (`hungry_birds.py`)
Un jeu inspiré de Flappy Bird avec un système de faim et d'énergie.

**Contrôles :**
- Espace ou Clic souris : Voler
- R : Redémarrer
- Échap : Quitter

**Objectif :** Naviguer entre les obstacles tout en maintenant la faim et l'énergie.

**Fonctionnalités :**
- Système de faim et d'énergie
- Différents types de nourriture
- Obstacles variés
- Barres de statut visuelles

### 6. Subway Surfers (`subway_surfers.py`)
Un jeu de course infinie avec changement de voies.

**Contrôles :**
- A/D ou Flèches Gauche/Droite : Changer de voie
- W ou Flèche Haut : Sauter
- S ou Flèche Bas : Glisser
- R : Redémarrer
- Échap : Quitter

**Objectif :** Collecter des pièces et éviter les obstacles sur 3 voies.

**Fonctionnalités :**
- 3 voies de course
- Obstacles variés (barrières, tunnels, trains)
- Powerups (invincibilité, boost, magnétisme)
- Système de score et de pièces

## Lancement des Jeux

Pour lancer un jeu, utilisez Python :

```bash
python super_mario.py
python snake.py
python basket_shoots.py
python car_race.py
python hungry_birds.py
python subway_surfers.py
```

## Fonctionnalités Communes

- **Interface utilisateur** : Scores, niveaux, instructions
- **Système de restart** : Touche R pour recommencer
- **Animations** : Effets visuels et animations fluides
- **Gestion des collisions** : Détection précise des collisions
- **Progression** : Augmentation progressive de la difficulté

## Développement

Ces jeux sont développés en Python avec :
- **Pygame** : Pour les graphiques et la gestion des événements
- **Maths** : Pour les calculs de physique et animations
- **Random** : Pour la génération aléatoire d'éléments

## Personnalisation

Vous pouvez facilement modifier :
- Les couleurs dans les constantes en haut de chaque fichier
- Les vitesses et difficultés
- Les tailles des éléments
- Les contrôles dans la gestion des événements

## Dépannage

**Problèmes courants :**
- Assurez-vous d'avoir installé pygame : `pip install pygame`
- Vérifiez que vous utilisez Python 3.7+
- Sur certains systèmes, utilisez `python3` au lieu de `python`

**Performance :**
- Les jeux sont optimisés pour tourner à 60 FPS
- Si vous avez des problèmes de performance, réduisez la constante FPS

## Améliorations Possibles

- Sons et musique
- Meilleurs graphiques avec des sprites
- Sauvegarde des scores
- Multijoueur
- Niveaux personnalisés

Amusez-vous bien avec ces jeux ! 🎮
