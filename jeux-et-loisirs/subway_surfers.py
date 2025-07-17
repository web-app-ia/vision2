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
NOMBRE_VOIES = 3
LARGEUR_VOIE = LARGEUR // NOMBRE_VOIES
VITESSE_BASE = 8
GRAVITE = 0.8
FORCE_SAUT = -15

# Couleurs
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
ROUGE = (255, 0, 0)
BLEU = (0, 0, 255)
VERT = (0, 255, 0)
JAUNE = (255, 255, 0)
ORANGE = (255, 165, 0)
VIOLET = (128, 0, 128)
GRIS = (128, 128, 128)
MARRON = (139, 69, 19)
ROSE = (255, 192, 203)

class Joueur:
    def __init__(self):
        self.voie = 1  # 0, 1, 2 (gauche, centre, droite)
        self.x = LARGEUR // 2
        self.y = HAUTEUR - 150
        self.largeur = 40
        self.hauteur = 60
        self.vitesse_y = 0
        self.au_sol = True
        self.glisse = False
        self.temps_glisse = 0
        self.animation_course = 0
        self.invincible = False
        self.temps_invincible = 0
        self.vitesse_boost = False
        self.temps_boost = 0
        
    def update(self):
        # Animation de course
        self.animation_course += 1
        
        # Mouvement vertical (saut/chute)
        if not self.au_sol:
            self.vitesse_y += GRAVITE
            self.y += self.vitesse_y
            
            # Atterrissage
            if self.y >= HAUTEUR - 150:
                self.y = HAUTEUR - 150
                self.au_sol = True
                self.vitesse_y = 0
        
        # Glissade
        if self.glisse:
            self.temps_glisse -= 1
            if self.temps_glisse <= 0:
                self.glisse = False
        
        # Invincibilité
        if self.invincible:
            self.temps_invincible -= 1
            if self.temps_invincible <= 0:
                self.invincible = False
        
        # Boost de vitesse
        if self.vitesse_boost:
            self.temps_boost -= 1
            if self.temps_boost <= 0:
                self.vitesse_boost = False
        
        # Mettre à jour la position X
        self.x = self.voie * LARGEUR_VOIE + LARGEUR_VOIE // 2 - self.largeur // 2
    
    def changer_voie(self, direction):
        if direction == "gauche" and self.voie > 0:
            self.voie -= 1
        elif direction == "droite" and self.voie < NOMBRE_VOIES - 1:
            self.voie += 1
    
    def sauter(self):
        if self.au_sol:
            self.vitesse_y = FORCE_SAUT
            self.au_sol = False
    
    def glisser(self):
        if self.au_sol:
            self.glisse = True
            self.temps_glisse = 30
    
    def activer_invincibilite(self):
        self.invincible = True
        self.temps_invincible = 300  # 5 secondes
    
    def activer_boost(self):
        self.vitesse_boost = True
        self.temps_boost = 300  # 5 secondes
    
    def get_rect(self):
        hauteur_rect = self.hauteur if not self.glisse else self.hauteur // 2
        y_rect = self.y if not self.glisse else self.y + self.hauteur // 2
        return pygame.Rect(self.x, y_rect, self.largeur, hauteur_rect)
    
    def dessiner(self, ecran):
        # Couleur du joueur
        couleur = BLEU
        if self.invincible:
            couleur = JAUNE if self.temps_invincible % 10 < 5 else BLEU
        
        # Dessiner le joueur
        if self.glisse:
            # Position glissée
            pygame.draw.rect(ecran, couleur, (self.x, self.y + self.hauteur // 2, 
                                            self.largeur, self.hauteur // 2))
        else:
            # Position normale
            pygame.draw.rect(ecran, couleur, (self.x, self.y, self.largeur, self.hauteur))
        
        # Contour
        pygame.draw.rect(ecran, NOIR, (self.x, self.y, self.largeur, self.hauteur), 2)
        
        # Détails du personnage
        # Tête
        pygame.draw.circle(ecran, JAUNE, (self.x + self.largeur//2, self.y + 10), 8)
        
        # Yeux
        pygame.draw.circle(ecran, NOIR, (self.x + self.largeur//2 - 3, self.y + 8), 2)
        pygame.draw.circle(ecran, NOIR, (self.x + self.largeur//2 + 3, self.y + 8), 2)
        
        # Animation de course (jambes)
        if self.au_sol and not self.glisse:
            jambe_offset = 3 if (self.animation_course // 10) % 2 == 0 else -3
            pygame.draw.line(ecran, MARRON, 
                           (self.x + 10, self.y + self.hauteur), 
                           (self.x + 10 + jambe_offset, self.y + self.hauteur + 15), 3)
            pygame.draw.line(ecran, MARRON, 
                           (self.x + 30, self.y + self.hauteur), 
                           (self.x + 30 - jambe_offset, self.y + self.hauteur + 15), 3)

class Obstacle:
    def __init__(self, voie, type_obstacle):
        self.voie = voie
        self.x = voie * LARGEUR_VOIE + LARGEUR_VOIE // 2
        self.y = HAUTEUR - 100
        self.type = type_obstacle
        self.vitesse = VITESSE_BASE
        
        if type_obstacle == "barriere":
            self.largeur = 50
            self.hauteur = 80
            self.couleur = ROUGE
        elif type_obstacle == "tunnel":
            self.largeur = 60
            self.hauteur = 40
            self.couleur = GRIS
            self.y = HAUTEUR - 190  # Position haute
        elif type_obstacle == "train":
            self.largeur = 100
            self.hauteur = 120
            self.couleur = ORANGE
            self.y = HAUTEUR - 220
        
        self.x -= self.largeur // 2
    
    def update(self, vitesse_jeu):
        self.vitesse = VITESSE_BASE * vitesse_jeu
        self.y += self.vitesse
        return self.y < HAUTEUR + 100
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.largeur, self.hauteur)
    
    def dessiner(self, ecran):
        if self.type == "barriere":
            pygame.draw.rect(ecran, self.couleur, (self.x, self.y, self.largeur, self.hauteur))
            pygame.draw.rect(ecran, NOIR, (self.x, self.y, self.largeur, self.hauteur), 2)
            # Rayures
            for i in range(0, self.hauteur, 10):
                pygame.draw.line(ecran, JAUNE, (self.x, self.y + i), (self.x + self.largeur, self.y + i), 2)
        
        elif self.type == "tunnel":
            pygame.draw.rect(ecran, self.couleur, (self.x, self.y, self.largeur, self.hauteur))
            pygame.draw.rect(ecran, NOIR, (self.x, self.y, self.largeur, self.hauteur), 2)
            # Détails du tunnel
            pygame.draw.rect(ecran, NOIR, (self.x + 10, self.y + 10, self.largeur - 20, self.hauteur - 20))
        
        elif self.type == "train":
            pygame.draw.rect(ecran, self.couleur, (self.x, self.y, self.largeur, self.hauteur))
            pygame.draw.rect(ecran, NOIR, (self.x, self.y, self.largeur, self.hauteur), 2)
            # Fenêtres
            pygame.draw.rect(ecran, BLEU, (self.x + 10, self.y + 20, 20, 15))
            pygame.draw.rect(ecran, BLEU, (self.x + 40, self.y + 20, 20, 15))
            pygame.draw.rect(ecran, BLEU, (self.x + 70, self.y + 20, 20, 15))
            # Roues
            pygame.draw.circle(ecran, NOIR, (self.x + 20, self.y + self.hauteur - 10), 8)
            pygame.draw.circle(ecran, NOIR, (self.x + 80, self.y + self.hauteur - 10), 8)

class Piece:
    def __init__(self, voie, y_pos):
        self.voie = voie
        self.x = voie * LARGEUR_VOIE + LARGEUR_VOIE // 2
        self.y = y_pos
        self.rayon = 12
        self.vitesse = VITESSE_BASE
        self.collectee = False
        self.animation = 0
        
    def update(self, vitesse_jeu):
        self.vitesse = VITESSE_BASE * vitesse_jeu
        self.y += self.vitesse
        self.animation += 1
        return self.y < HAUTEUR + 50
    
    def get_rect(self):
        return pygame.Rect(self.x - self.rayon, self.y - self.rayon, 
                          self.rayon * 2, self.rayon * 2)
    
    def dessiner(self, ecran):
        if not self.collectee:
            # Effet de scintillement
            taille = self.rayon + math.sin(self.animation * 0.3) * 2
            pygame.draw.circle(ecran, JAUNE, (int(self.x), int(self.y)), int(taille))
            pygame.draw.circle(ecran, ORANGE, (int(self.x), int(self.y)), int(taille), 2)
            
            # Symbole dollar
            pygame.draw.line(ecran, VERT, (self.x - 4, self.y - 6), (self.x + 4, self.y + 6), 2)
            pygame.draw.line(ecran, VERT, (self.x - 4, self.y + 6), (self.x + 4, self.y - 6), 2)

class Powerup:
    def __init__(self, voie, type_powerup):
        self.voie = voie
        self.x = voie * LARGEUR_VOIE + LARGEUR_VOIE // 2
        self.y = random.randint(-300, -100)
        self.type = type_powerup
        self.largeur = 30
        self.hauteur = 30
        self.vitesse = VITESSE_BASE
        self.animation = 0
        
        if type_powerup == "invincible":
            self.couleur = JAUNE
        elif type_powerup == "boost":
            self.couleur = ROUGE
        elif type_powerup == "magnetisme":
            self.couleur = VIOLET
        
        self.x -= self.largeur // 2
    
    def update(self, vitesse_jeu):
        self.vitesse = VITESSE_BASE * vitesse_jeu
        self.y += self.vitesse
        self.animation += 1
        return self.y < HAUTEUR + 50
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.largeur, self.hauteur)
    
    def dessiner(self, ecran):
        # Effet de rotation
        angle = self.animation * 5
        
        # Dessiner un losange rotatif
        centre_x = self.x + self.largeur // 2
        centre_y = self.y + self.hauteur // 2
        
        points = []
        for i in range(4):
            angle_rad = math.radians(angle + i * 90)
            x = centre_x + 15 * math.cos(angle_rad)
            y = centre_y + 15 * math.sin(angle_rad)
            points.append((x, y))
        
        pygame.draw.polygon(ecran, self.couleur, points)
        pygame.draw.polygon(ecran, NOIR, points, 2)
        
        # Lettres indicatrices
        font = pygame.font.Font(None, 24)
        if self.type == "invincible":
            text = font.render("I", True, NOIR)
        elif self.type == "boost":
            text = font.render("B", True, NOIR)
        elif self.type == "magnetisme":
            text = font.render("M", True, NOIR)
        
        text_rect = text.get_rect(center=(centre_x, centre_y))
        ecran.blit(text, text_rect)

class Jeu:
    def __init__(self):
        self.joueur = Joueur()
        self.obstacles = []
        self.pieces = []
        self.powerups = []
        self.score = 0
        self.pieces_collectees = 0
        self.distance = 0
        self.vitesse_jeu = 1
        self.niveau = 1
        self.temps_niveau = 0
        self.game_over = False
        self.temps_obstacle = 0
        self.temps_piece = 0
        self.temps_powerup = 0
        self.magnetisme_actif = False
        self.temps_magnetisme = 0
        self.multiplicateur_score = 1
        
    def update(self):
        if self.game_over:
            return
        
        # Mettre à jour le joueur
        self.joueur.update()
        
        # Augmenter la distance
        self.distance += self.vitesse_jeu
        
        # Augmenter le niveau et la vitesse
        self.temps_niveau += 1
        if self.temps_niveau >= 300:  # 5 secondes
            self.niveau += 1
            self.temps_niveau = 0
            self.vitesse_jeu = min(self.vitesse_jeu + 0.1, 3)
        
        # Gérer le magnétisme
        if self.magnetisme_actif:
            self.temps_magnetisme -= 1
            if self.temps_magnetisme <= 0:
                self.magnetisme_actif = False
        
        # Générer des obstacles
        self.temps_obstacle += 1
        if self.temps_obstacle > max(60, 120 - self.niveau * 5):
            self.temps_obstacle = 0
            voie = random.randint(0, NOMBRE_VOIES - 1)
            type_obstacle = random.choice(["barriere", "tunnel", "train"])
            self.obstacles.append(Obstacle(voie, type_obstacle))
        
        # Générer des pièces
        self.temps_piece += 1
        if self.temps_piece > 30:
            self.temps_piece = 0
            voie = random.randint(0, NOMBRE_VOIES - 1)
            y_pos = random.randint(-200, -50)
            self.pieces.append(Piece(voie, y_pos))
        
        # Générer des powerups
        self.temps_powerup += 1
        if self.temps_powerup > 600:  # 10 secondes
            self.temps_powerup = 0
            voie = random.randint(0, NOMBRE_VOIES - 1)
            type_powerup = random.choice(["invincible", "boost", "magnetisme"])
            self.powerups.append(Powerup(voie, type_powerup))
        
        # Mettre à jour les obstacles
        self.obstacles = [obs for obs in self.obstacles if obs.update(self.vitesse_jeu)]
        
        # Mettre à jour les pièces
        self.pieces = [piece for piece in self.pieces if piece.update(self.vitesse_jeu)]
        
        # Mettre à jour les powerups
        self.powerups = [powerup for powerup in self.powerups if powerup.update(self.vitesse_jeu)]
        
        # Vérifier les collisions
        self.verifier_collisions()
        
        # Augmenter le score
        self.score += int(self.vitesse_jeu * self.multiplicateur_score)
    
    def verifier_collisions(self):
        joueur_rect = self.joueur.get_rect()
        
        # Collision avec les obstacles
        for obstacle in self.obstacles:
            if joueur_rect.colliderect(obstacle.get_rect()):
                if obstacle.type == "barriere" and not self.joueur.invincible:
                    self.game_over = True
                elif obstacle.type == "tunnel" and not self.joueur.glisse and not self.joueur.invincible:
                    self.game_over = True
                elif obstacle.type == "train" and not self.joueur.invincible:
                    self.game_over = True
        
        # Collision avec les pièces
        for piece in self.pieces:
            if not piece.collectee and joueur_rect.colliderect(piece.get_rect()):
                piece.collectee = True
                self.pieces_collectees += 1
                self.score += 10 * self.multiplicateur_score
        
        # Effet magnétisme
        if self.magnetisme_actif:
            for piece in self.pieces:
                if not piece.collectee and abs(piece.voie - self.joueur.voie) <= 1:
                    # Attirer la pièce vers le joueur
                    if piece.x < self.joueur.x:
                        piece.x += 5
                    elif piece.x > self.joueur.x:
                        piece.x -= 5
                    
                    if piece.y < self.joueur.y:
                        piece.y += 5
                    elif piece.y > self.joueur.y:
                        piece.y -= 5
        
        # Collision avec les powerups
        for powerup in self.powerups[:]:
            if joueur_rect.colliderect(powerup.get_rect()):
                if powerup.type == "invincible":
                    self.joueur.activer_invincibilite()
                elif powerup.type == "boost":
                    self.joueur.activer_boost()
                    self.multiplicateur_score = 2
                elif powerup.type == "magnetisme":
                    self.magnetisme_actif = True
                    self.temps_magnetisme = 300
                
                self.powerups.remove(powerup)
        
        # Réinitialiser le multiplicateur si le boost expire
        if not self.joueur.vitesse_boost:
            self.multiplicateur_score = 1
    
    def dessiner_fond(self, ecran):
        # Fond dégradé
        for y in range(HAUTEUR):
            couleur = int(50 + (100 - 50) * (y / HAUTEUR))
            pygame.draw.line(ecran, (couleur, couleur, couleur + 50), (0, y), (LARGEUR, y))
        
        # Lignes de voies
        for i in range(1, NOMBRE_VOIES):
            x = i * LARGEUR_VOIE
            pygame.draw.line(ecran, BLANC, (x, 0), (x, HAUTEUR), 2)
        
        # Lignes de route défilantes
        for i in range(-1, HAUTEUR // 50 + 1):
            y = (i * 50 + (self.distance // 2) % 50)
            pygame.draw.line(ecran, JAUNE, (0, y), (LARGEUR, y), 1)
    
    def dessiner_interface(self, ecran):
        font = pygame.font.Font(None, 36)
        
        # Score
        score_text = font.render(f"Score: {self.score}", True, BLANC)
        ecran.blit(score_text, (10, 10))
        
        # Pièces
        pieces_text = font.render(f"Pièces: {self.pieces_collectees}", True, BLANC)
        ecran.blit(pieces_text, (10, 50))
        
        # Niveau
        niveau_text = font.render(f"Niveau: {self.niveau}", True, BLANC)
        ecran.blit(niveau_text, (10, 90))
        
        # Vitesse
        vitesse_text = font.render(f"Vitesse: {self.vitesse_jeu:.1f}x", True, BLANC)
        ecran.blit(vitesse_text, (10, 130))
        
        # Powerups actifs
        y_offset = 170
        if self.joueur.invincible:
            invincible_text = font.render("INVINCIBLE", True, JAUNE)
            ecran.blit(invincible_text, (10, y_offset))
            y_offset += 30
        
        if self.joueur.vitesse_boost:
            boost_text = font.render("BOOST x2", True, ROUGE)
            ecran.blit(boost_text, (10, y_offset))
            y_offset += 30
        
        if self.magnetisme_actif:
            mag_text = font.render("MAGNÉTISME", True, VIOLET)
            ecran.blit(mag_text, (10, y_offset))
        
        # Instructions
        instructions = [
            "A/D ou Flèches: Changer de voie",
            "W/Haut: Sauter",
            "S/Bas: Glisser",
            "Échap: Quitter"
        ]
        
        for i, instruction in enumerate(instructions):
            text = pygame.font.Font(None, 24).render(instruction, True, BLANC)
            ecran.blit(text, (LARGEUR - 250, 10 + i * 25))

def afficher_game_over(ecran, score, pieces):
    font_large = pygame.font.Font(None, 72)
    font_medium = pygame.font.Font(None, 36)
    
    # Fond semi-transparent
    overlay = pygame.Surface((LARGEUR, HAUTEUR))
    overlay.set_alpha(128)
    overlay.fill(NOIR)
    ecran.blit(overlay, (0, 0))
    
    # Texte Game Over
    game_over_text = font_large.render("GAME OVER", True, ROUGE)
    game_over_rect = game_over_text.get_rect(center=(LARGEUR//2, HAUTEUR//2 - 100))
    ecran.blit(game_over_text, game_over_rect)
    
    # Score final
    score_text = font_medium.render(f"Score final: {score}", True, BLANC)
    score_rect = score_text.get_rect(center=(LARGEUR//2, HAUTEUR//2 - 50))
    ecran.blit(score_text, score_rect)
    
    # Pièces collectées
    pieces_text = font_medium.render(f"Pièces collectées: {pieces}", True, JAUNE)
    pieces_rect = pieces_text.get_rect(center=(LARGEUR//2, HAUTEUR//2 - 10))
    ecran.blit(pieces_text, pieces_rect)
    
    # Instructions
    restart_text = font_medium.render("Appuyez sur R pour recommencer", True, BLANC)
    restart_rect = restart_text.get_rect(center=(LARGEUR//2, HAUTEUR//2 + 30))
    ecran.blit(restart_text, restart_rect)

def main():
    ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
    pygame.display.set_caption("Subway Surfers - Jeu Python")
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
                elif not jeu.game_over:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        jeu.joueur.changer_voie("gauche")
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        jeu.joueur.changer_voie("droite")
                    elif event.key == pygame.K_UP or event.key == pygame.K_w:
                        jeu.joueur.sauter()
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        jeu.joueur.glisser()
        
        # Mise à jour du jeu
        jeu.update()
        
        # Affichage
        jeu.dessiner_fond(ecran)
        
        # Dessiner les objets
        for obstacle in jeu.obstacles:
            obstacle.dessiner(ecran)
        
        for piece in jeu.pieces:
            piece.dessiner(ecran)
        
        for powerup in jeu.powerups:
            powerup.dessiner(ecran)
        
        jeu.joueur.dessiner(ecran)
        jeu.dessiner_interface(ecran)
        
        # Afficher game over si nécessaire
        if jeu.game_over:
            afficher_game_over(ecran, jeu.score, jeu.pieces_collectees)
        
        pygame.display.flip()
        horloge.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
