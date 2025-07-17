import pygame
import sys
import random
import math

# Initialisation de pygame
pygame.init()

# Constantes
LARGEUR = 800
HAUTEUR = 600
FPS = 60

# Couleurs
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
ROUGE = (255, 0, 0)
BLEU = (0, 0, 255)
VERT = (0, 255, 0)
JAUNE = (255, 255, 0)
GRIS = (128, 128, 128)
ORANGE = (255, 165, 0)
VIOLET = (128, 0, 128)

class Voiture:
    def __init__(self, x, y, couleur=BLEU):
        self.x = x
        self.y = y
        self.largeur = 30
        self.hauteur = 60
        self.vitesse = 0
        self.vitesse_max = 8
        self.acceleration = 0.3
        self.freinage = 0.5
        self.couleur = couleur
        self.angle = 0
        self.vitesse_rotation = 5
        
    def update(self):
        touches = pygame.key.get_pressed()
        
        # Accélération et freinage
        if touches[pygame.K_UP] or touches[pygame.K_w]:
            self.vitesse = min(self.vitesse + self.acceleration, self.vitesse_max)
        elif touches[pygame.K_DOWN] or touches[pygame.K_s]:
            self.vitesse = max(self.vitesse - self.freinage, -self.vitesse_max // 2)
        else:
            # Décélération naturelle
            if self.vitesse > 0:
                self.vitesse = max(0, self.vitesse - 0.1)
            elif self.vitesse < 0:
                self.vitesse = min(0, self.vitesse + 0.1)
        
        # Rotation
        if touches[pygame.K_LEFT] or touches[pygame.K_a]:
            if self.vitesse != 0:
                self.angle -= self.vitesse_rotation * (self.vitesse / self.vitesse_max)
        if touches[pygame.K_RIGHT] or touches[pygame.K_d]:
            if self.vitesse != 0:
                self.angle += self.vitesse_rotation * (self.vitesse / self.vitesse_max)
        
        # Mouvement
        self.x += self.vitesse * math.cos(math.radians(self.angle))
        self.y += self.vitesse * math.sin(math.radians(self.angle))
        
        # Limites de l'écran
        self.x = max(0, min(LARGEUR - self.largeur, self.x))
        self.y = max(0, min(HAUTEUR - self.hauteur, self.y))
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.largeur, self.hauteur)
    
    def dessiner(self, ecran):
        # Calculer les coins de la voiture
        centre_x = self.x + self.largeur // 2
        centre_y = self.y + self.hauteur // 2
        
        # Points de la voiture (rectangle)
        points = [
            (-self.largeur//2, -self.hauteur//2),
            (self.largeur//2, -self.hauteur//2),
            (self.largeur//2, self.hauteur//2),
            (-self.largeur//2, self.hauteur//2)
        ]
        
        # Rotation des points
        angle_rad = math.radians(self.angle)
        points_rotated = []
        for px, py in points:
            rotated_x = px * math.cos(angle_rad) - py * math.sin(angle_rad)
            rotated_y = px * math.sin(angle_rad) + py * math.cos(angle_rad)
            points_rotated.append((centre_x + rotated_x, centre_y + rotated_y))
        
        # Dessiner la voiture
        pygame.draw.polygon(ecran, self.couleur, points_rotated)
        pygame.draw.polygon(ecran, NOIR, points_rotated, 2)
        
        # Dessiner les phares
        phare1_x = centre_x + (self.largeur//2 - 5) * math.cos(angle_rad)
        phare1_y = centre_y + (self.largeur//2 - 5) * math.sin(angle_rad)
        pygame.draw.circle(ecran, JAUNE, (int(phare1_x), int(phare1_y)), 3)

class VoitureIA:
    def __init__(self, x, y, couleur=ROUGE):
        self.x = x
        self.y = y
        self.largeur = 30
        self.hauteur = 60
        self.vitesse = random.uniform(2, 5)
        self.couleur = couleur
        self.direction = random.choice([-1, 1])
        self.temps_changement = 0
        
    def update(self):
        # Mouvement vertical
        self.y += self.vitesse
        
        # Mouvement horizontal aléatoire
        self.temps_changement += 1
        if self.temps_changement > 60:  # Changer de direction toutes les secondes
            self.direction = random.choice([-1, 0, 1])
            self.temps_changement = 0
        
        self.x += self.direction * 2
        
        # Limites horizontales
        if self.x <= 0 or self.x >= LARGEUR - self.largeur:
            self.direction *= -1
        
        # Réapparaître en haut si sort de l'écran
        if self.y > HAUTEUR:
            self.y = -self.hauteur
            self.x = random.randint(0, LARGEUR - self.largeur)
            self.vitesse = random.uniform(2, 5)
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.largeur, self.hauteur)
    
    def dessiner(self, ecran):
        pygame.draw.rect(ecran, self.couleur, (self.x, self.y, self.largeur, self.hauteur))
        pygame.draw.rect(ecran, NOIR, (self.x, self.y, self.largeur, self.hauteur), 2)
        
        # Phares
        pygame.draw.circle(ecran, JAUNE, (int(self.x + 5), int(self.y)), 3)
        pygame.draw.circle(ecran, JAUNE, (int(self.x + 25), int(self.y)), 3)

class Obstacle:
    def __init__(self, x, y, type_obstacle="normal"):
        self.x = x
        self.y = y
        self.type = type_obstacle
        self.vitesse = random.uniform(3, 6)
        
        if type_obstacle == "normal":
            self.largeur = 40
            self.hauteur = 40
            self.couleur = GRIS
        elif type_obstacle == "bonus":
            self.largeur = 25
            self.hauteur = 25
            self.couleur = VERT
        elif type_obstacle == "malus":
            self.largeur = 35
            self.hauteur = 35
            self.couleur = ORANGE
        
    def update(self):
        self.y += self.vitesse
        
        # Réapparaître en haut si sort de l'écran
        if self.y > HAUTEUR:
            self.y = -self.hauteur
            self.x = random.randint(0, LARGEUR - self.largeur)
            self.vitesse = random.uniform(3, 6)
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.largeur, self.hauteur)
    
    def dessiner(self, ecran):
        if self.type == "normal":
            pygame.draw.rect(ecran, self.couleur, (self.x, self.y, self.largeur, self.hauteur))
        elif self.type == "bonus":
            pygame.draw.circle(ecran, self.couleur, 
                             (int(self.x + self.largeur//2), int(self.y + self.hauteur//2)), 
                             self.largeur//2)
        elif self.type == "malus":
            # Dessiner un triangle
            points = [
                (self.x + self.largeur//2, self.y),
                (self.x, self.y + self.hauteur),
                (self.x + self.largeur, self.y + self.hauteur)
            ]
            pygame.draw.polygon(ecran, self.couleur, points)
        
        pygame.draw.rect(ecran, NOIR, (self.x, self.y, self.largeur, self.hauteur), 2)

class Powerup:
    def __init__(self, x, y, type_powerup):
        self.x = x
        self.y = y
        self.type = type_powerup
        self.largeur = 30
        self.hauteur = 30
        self.vitesse = 4
        self.temps_vie = 300  # 5 secondes
        
        if type_powerup == "speed":
            self.couleur = JAUNE
        elif type_powerup == "shield":
            self.couleur = BLEU
        elif type_powerup == "points":
            self.couleur = VIOLET
    
    def update(self):
        self.y += self.vitesse
        self.temps_vie -= 1
        
        if self.y > HAUTEUR or self.temps_vie <= 0:
            return False
        return True
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.largeur, self.hauteur)
    
    def dessiner(self, ecran):
        # Dessiner une étoile
        centre_x = self.x + self.largeur // 2
        centre_y = self.y + self.hauteur // 2
        
        points = []
        for i in range(10):
            angle = i * 36
            if i % 2 == 0:
                rayon = 15
            else:
                rayon = 7
            
            x = centre_x + rayon * math.cos(math.radians(angle - 90))
            y = centre_y + rayon * math.sin(math.radians(angle - 90))
            points.append((x, y))
        
        pygame.draw.polygon(ecran, self.couleur, points)
        pygame.draw.polygon(ecran, NOIR, points, 2)

class Jeu:
    def __init__(self):
        self.voiture_joueur = Voiture(LARGEUR // 2, HAUTEUR - 100)
        self.voitures_ia = []
        self.obstacles = []
        self.powerups = []
        self.score = 0
        self.niveau = 1
        self.temps_niveau = 0
        self.vitesse_jeu = 1
        self.vies = 3
        self.invincible = False
        self.temps_invincible = 0
        self.shield_actif = False
        self.temps_shield = 0
        self.speed_boost = False
        self.temps_speed_boost = 0
        
        # Créer des voitures IA initiales
        for i in range(3):
            x = random.randint(0, LARGEUR - 30)
            y = random.randint(-300, -60)
            self.voitures_ia.append(VoitureIA(x, y, random.choice([ROUGE, ORANGE, VIOLET])))
        
        # Créer des obstacles initiaux
        for i in range(2):
            x = random.randint(0, LARGEUR - 40)
            y = random.randint(-200, -40)
            type_obs = random.choice(["normal", "bonus", "malus"])
            self.obstacles.append(Obstacle(x, y, type_obs))
    
    def update(self):
        # Mettre à jour le joueur
        vitesse_originale = self.voiture_joueur.vitesse_max
        if self.speed_boost:
            self.voiture_joueur.vitesse_max = 12
            self.temps_speed_boost -= 1
            if self.temps_speed_boost <= 0:
                self.speed_boost = False
                self.voiture_joueur.vitesse_max = vitesse_originale
        
        self.voiture_joueur.update()
        
        # Gérer l'invincibilité
        if self.invincible:
            self.temps_invincible -= 1
            if self.temps_invincible <= 0:
                self.invincible = False
        
        # Gérer le shield
        if self.shield_actif:
            self.temps_shield -= 1
            if self.temps_shield <= 0:
                self.shield_actif = False
        
        # Mettre à jour les voitures IA
        for voiture in self.voitures_ia:
            voiture.update()
        
        # Mettre à jour les obstacles
        for obstacle in self.obstacles:
            obstacle.update()
        
        # Mettre à jour les powerups
        self.powerups = [p for p in self.powerups if p.update()]
        
        # Vérifier les collisions
        self.verifier_collisions()
        
        # Augmenter le score
        self.score += 1
        
        # Gestion des niveaux
        self.temps_niveau += 1
        if self.temps_niveau >= 1800:  # 30 secondes
            self.niveau += 1
            self.temps_niveau = 0
            self.vitesse_jeu += 0.2
            
            # Ajouter plus de voitures et obstacles
            if len(self.voitures_ia) < 6:
                x = random.randint(0, LARGEUR - 30)
                y = random.randint(-300, -60)
                self.voitures_ia.append(VoitureIA(x, y, random.choice([ROUGE, ORANGE, VIOLET])))
            
            if len(self.obstacles) < 4:
                x = random.randint(0, LARGEUR - 40)
                y = random.randint(-200, -40)
                type_obs = random.choice(["normal", "bonus", "malus"])
                self.obstacles.append(Obstacle(x, y, type_obs))
        
        # Générer des powerups aléatoirement
        if random.randint(1, 600) == 1:  # 1 chance sur 600 par frame
            x = random.randint(0, LARGEUR - 30)
            y = -30
            type_powerup = random.choice(["speed", "shield", "points"])
            self.powerups.append(Powerup(x, y, type_powerup))
    
    def verifier_collisions(self):
        joueur_rect = self.voiture_joueur.get_rect()
        
        # Collision avec les voitures IA
        for voiture in self.voitures_ia:
            if joueur_rect.colliderect(voiture.get_rect()) and not self.invincible and not self.shield_actif:
                self.vies -= 1
                self.invincible = True
                self.temps_invincible = 120  # 2 secondes d'invincibilité
                if self.vies <= 0:
                    self.game_over()
        
        # Collision avec les obstacles
        for obstacle in self.obstacles:
            if joueur_rect.colliderect(obstacle.get_rect()):
                if obstacle.type == "normal" and not self.invincible and not self.shield_actif:
                    self.vies -= 1
                    self.invincible = True
                    self.temps_invincible = 120
                    if self.vies <= 0:
                        self.game_over()
                elif obstacle.type == "bonus":
                    self.score += 50
                    obstacle.y = -obstacle.hauteur
                    obstacle.x = random.randint(0, LARGEUR - obstacle.largeur)
                elif obstacle.type == "malus" and not self.shield_actif:
                    self.score = max(0, self.score - 20)
                    obstacle.y = -obstacle.hauteur
                    obstacle.x = random.randint(0, LARGEUR - obstacle.largeur)
        
        # Collision avec les powerups
        for powerup in self.powerups[:]:
            if joueur_rect.colliderect(powerup.get_rect()):
                if powerup.type == "speed":
                    self.speed_boost = True
                    self.temps_speed_boost = 300  # 5 secondes
                elif powerup.type == "shield":
                    self.shield_actif = True
                    self.temps_shield = 300  # 5 secondes
                elif powerup.type == "points":
                    self.score += 100
                
                self.powerups.remove(powerup)
    
    def game_over(self):
        # Réinitialiser le jeu
        self.__init__()
    
    def dessiner_route(self, ecran):
        # Dessiner la route
        pygame.draw.rect(ecran, GRIS, (0, 0, LARGEUR, HAUTEUR))
        
        # Lignes de la route
        for i in range(-1, HAUTEUR // 40 + 1):
            y = (i * 40 + (self.score // 5) % 40)
            pygame.draw.rect(ecran, JAUNE, (LARGEUR // 2 - 5, y, 10, 20))
        
        # Bords de la route
        pygame.draw.rect(ecran, BLANC, (0, 0, 20, HAUTEUR))
        pygame.draw.rect(ecran, BLANC, (LARGEUR - 20, 0, 20, HAUTEUR))
    
    def dessiner_interface(self, ecran):
        font = pygame.font.Font(None, 36)
        
        # Score
        score_text = font.render(f"Score: {self.score}", True, NOIR)
        ecran.blit(score_text, (10, 10))
        
        # Vies
        vies_text = font.render(f"Vies: {self.vies}", True, NOIR)
        ecran.blit(vies_text, (10, 50))
        
        # Niveau
        niveau_text = font.render(f"Niveau: {self.niveau}", True, NOIR)
        ecran.blit(niveau_text, (10, 90))
        
        # Vitesse
        vitesse_text = font.render(f"Vitesse: {int(self.voiture_joueur.vitesse)}", True, NOIR)
        ecran.blit(vitesse_text, (10, 130))
        
        # Powerups actifs
        y_offset = 170
        if self.shield_actif:
            shield_text = font.render("SHIELD ACTIF", True, BLEU)
            ecran.blit(shield_text, (10, y_offset))
            y_offset += 30
        
        if self.speed_boost:
            speed_text = font.render("SPEED BOOST", True, JAUNE)
            ecran.blit(speed_text, (10, y_offset))
            y_offset += 30
        
        if self.invincible:
            invincible_text = font.render("INVINCIBLE", True, ROUGE)
            ecran.blit(invincible_text, (10, y_offset))
        
        # Instructions
        instructions = [
            "Flèches/WASD: Conduire",
            "Évitez les obstacles",
            "Collectez les bonus",
            "Échap: Quitter"
        ]
        
        for i, instruction in enumerate(instructions):
            text = pygame.font.Font(None, 24).render(instruction, True, NOIR)
            ecran.blit(text, (LARGEUR - 200, 10 + i * 25))

def main():
    ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
    pygame.display.set_caption("Car Race - Jeu Python")
    horloge = pygame.time.Clock()
    
    jeu = Jeu()
    
    # Boucle principale
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    jeu = Jeu()
        
        # Mise à jour du jeu
        jeu.update()
        
        # Affichage
        ecran.fill(BLANC)
        
        # Dessiner la route
        jeu.dessiner_route(ecran)
        
        # Dessiner les objets
        jeu.voiture_joueur.dessiner(ecran)
        
        for voiture in jeu.voitures_ia:
            voiture.dessiner(ecran)
        
        for obstacle in jeu.obstacles:
            obstacle.dessiner(ecran)
        
        for powerup in jeu.powerups:
            powerup.dessiner(ecran)
        
        # Dessiner l'interface
        jeu.dessiner_interface(ecran)
        
        # Effet de clignotement si invincible
        if jeu.invincible and jeu.temps_invincible % 10 < 5:
            overlay = pygame.Surface((LARGEUR, HAUTEUR))
            overlay.set_alpha(50)
            overlay.fill(ROUGE)
            ecran.blit(overlay, (0, 0))
        
        pygame.display.flip()
        horloge.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
