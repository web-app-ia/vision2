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
GRAVITE = 0.5
FORCE_SAUT = -10

# Couleurs
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
ROUGE = (255, 0, 0)
BLEU = (0, 0, 255)
VERT = (0, 255, 0)
JAUNE = (255, 255, 0)
ORANGE = (255, 165, 0)
MARRON = (139, 69, 19)
ROSE = (255, 192, 203)
VIOLET = (128, 0, 128)

class Oiseau:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vitesse_y = 0
        self.rayon = 20
        self.couleur = JAUNE
        self.angle = 0
        self.faim = 100
        self.energie = 100
        self.animation_saut = 0
        
    def update(self):
        # Gravité
        self.vitesse_y += GRAVITE
        self.y += self.vitesse_y
        
        # Angle basé sur la vitesse
        self.angle = max(-90, min(90, self.vitesse_y * 3))
        
        # Diminuer la faim et l'énergie
        self.faim = max(0, self.faim - 0.1)
        self.energie = max(0, self.energie - 0.05)
        
        # Animation de saut
        if self.animation_saut > 0:
            self.animation_saut -= 1
        
        # Vérifier les limites
        if self.y > HAUTEUR or self.y < 0:
            return False
        
        return True
    
    def sauter(self):
        self.vitesse_y = FORCE_SAUT
        self.animation_saut = 10
    
    def manger(self, type_nourriture):
        if type_nourriture == "graine":
            self.faim = min(100, self.faim + 20)
            self.energie = min(100, self.energie + 10)
        elif type_nourriture == "fruit":
            self.faim = min(100, self.faim + 30)
            self.energie = min(100, self.energie + 15)
        elif type_nourriture == "insecte":
            self.faim = min(100, self.faim + 15)
            self.energie = min(100, self.energie + 25)
        elif type_nourriture == "poison":
            self.faim = max(0, self.faim - 30)
            self.energie = max(0, self.energie - 20)
    
    def get_rect(self):
        return pygame.Rect(self.x - self.rayon, self.y - self.rayon, 
                          self.rayon * 2, self.rayon * 2)
    
    def dessiner(self, ecran):
        # Corps de l'oiseau
        couleur_corps = self.couleur
        if self.faim < 30:
            couleur_corps = ROUGE  # Rouge si affamé
        elif self.energie < 30:
            couleur_corps = ORANGE  # Orange si fatigué
        
        # Effet de saut
        rayon_effet = self.rayon
        if self.animation_saut > 0:
            rayon_effet += 2
        
        pygame.draw.circle(ecran, couleur_corps, (int(self.x), int(self.y)), rayon_effet)
        pygame.draw.circle(ecran, NOIR, (int(self.x), int(self.y)), rayon_effet, 2)
        
        # Yeux
        oeil1_x = self.x - 6
        oeil1_y = self.y - 6
        oeil2_x = self.x + 6
        oeil2_y = self.y - 6
        
        pygame.draw.circle(ecran, BLANC, (int(oeil1_x), int(oeil1_y)), 5)
        pygame.draw.circle(ecran, BLANC, (int(oeil2_x), int(oeil2_y)), 5)
        pygame.draw.circle(ecran, NOIR, (int(oeil1_x), int(oeil1_y)), 2)
        pygame.draw.circle(ecran, NOIR, (int(oeil2_x), int(oeil2_y)), 2)
        
        # Bec
        bec_points = [
            (self.x + 15, self.y),
            (self.x + 25, self.y - 3),
            (self.x + 25, self.y + 3)
        ]
        pygame.draw.polygon(ecran, ORANGE, bec_points)
        
        # Ailes (animation simple)
        if self.animation_saut > 5:
            aile_y = self.y - 5
        else:
            aile_y = self.y + 5
        
        # Aile gauche
        pygame.draw.ellipse(ecran, MARRON, (self.x - 25, aile_y - 8, 20, 16))
        # Aile droite
        pygame.draw.ellipse(ecran, MARRON, (self.x + 5, aile_y - 8, 20, 16))

class Obstacle:
    def __init__(self, x, hauteur_haut, hauteur_bas):
        self.x = x
        self.hauteur_haut = hauteur_haut
        self.hauteur_bas = hauteur_bas
        self.largeur = 60
        self.vitesse = 3
        self.passe = False
        self.couleur = VERT
        
    def update(self):
        self.x -= self.vitesse
        return self.x > -self.largeur
    
    def get_rects(self):
        rect_haut = pygame.Rect(self.x, 0, self.largeur, self.hauteur_haut)
        rect_bas = pygame.Rect(self.x, HAUTEUR - self.hauteur_bas, self.largeur, self.hauteur_bas)
        return rect_haut, rect_bas
    
    def dessiner(self, ecran):
        # Obstacle du haut
        pygame.draw.rect(ecran, self.couleur, (self.x, 0, self.largeur, self.hauteur_haut))
        pygame.draw.rect(ecran, NOIR, (self.x, 0, self.largeur, self.hauteur_haut), 2)
        
        # Obstacle du bas
        pygame.draw.rect(ecran, self.couleur, (self.x, HAUTEUR - self.hauteur_bas, self.largeur, self.hauteur_bas))
        pygame.draw.rect(ecran, NOIR, (self.x, HAUTEUR - self.hauteur_bas, self.largeur, self.hauteur_bas), 2)
        
        # Détails des tuyaux
        pygame.draw.rect(ecran, VERT, (self.x - 5, self.hauteur_haut - 20, self.largeur + 10, 20))
        pygame.draw.rect(ecran, VERT, (self.x - 5, HAUTEUR - self.hauteur_bas, self.largeur + 10, 20))

class Nourriture:
    def __init__(self, x, y, type_nourriture):
        self.x = x
        self.y = y
        self.type = type_nourriture
        self.vitesse = 3
        self.collectee = False
        self.animation = 0
        
        if type_nourriture == "graine":
            self.couleur = MARRON
            self.rayon = 5
            self.points = 10
        elif type_nourriture == "fruit":
            self.couleur = ROUGE
            self.rayon = 8
            self.points = 20
        elif type_nourriture == "insecte":
            self.couleur = NOIR
            self.rayon = 6
            self.points = 15
        elif type_nourriture == "poison":
            self.couleur = VIOLET
            self.rayon = 7
            self.points = -50
        
    def update(self):
        self.x -= self.vitesse
        self.animation += 1
        return self.x > -self.rayon * 2
    
    def get_rect(self):
        return pygame.Rect(self.x - self.rayon, self.y - self.rayon, 
                          self.rayon * 2, self.rayon * 2)
    
    def dessiner(self, ecran):
        if self.collectee:
            return
        
        # Effet de scintillement
        rayon_effet = self.rayon + math.sin(self.animation * 0.2) * 2
        
        if self.type == "graine":
            pygame.draw.circle(ecran, self.couleur, (int(self.x), int(self.y)), int(rayon_effet))
            pygame.draw.circle(ecran, NOIR, (int(self.x), int(self.y)), int(rayon_effet), 1)
        elif self.type == "fruit":
            pygame.draw.circle(ecran, self.couleur, (int(self.x), int(self.y)), int(rayon_effet))
            # Feuille
            pygame.draw.circle(ecran, VERT, (int(self.x - 3), int(self.y - 5)), 3)
        elif self.type == "insecte":
            pygame.draw.ellipse(ecran, self.couleur, (self.x - rayon_effet, self.y - rayon_effet/2, 
                                                     rayon_effet * 2, rayon_effet))
            # Antennes
            pygame.draw.line(ecran, NOIR, (self.x - 3, self.y - 5), (self.x - 5, self.y - 8), 2)
            pygame.draw.line(ecran, NOIR, (self.x + 3, self.y - 5), (self.x + 5, self.y - 8), 2)
        elif self.type == "poison":
            pygame.draw.circle(ecran, self.couleur, (int(self.x), int(self.y)), int(rayon_effet))
            # Symbole de poison
            pygame.draw.line(ecran, BLANC, (self.x - 3, self.y - 3), (self.x + 3, self.y + 3), 2)
            pygame.draw.line(ecran, BLANC, (self.x - 3, self.y + 3), (self.x + 3, self.y - 3), 2)

class Nuage:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vitesse = random.uniform(0.5, 2)
        self.taille = random.randint(30, 60)
        
    def update(self):
        self.x -= self.vitesse
        if self.x < -self.taille:
            self.x = LARGEUR + self.taille
            self.y = random.randint(50, 200)
    
    def dessiner(self, ecran):
        pygame.draw.circle(ecran, BLANC, (int(self.x), int(self.y)), self.taille)
        pygame.draw.circle(ecran, BLANC, (int(self.x + 20), int(self.y - 10)), self.taille // 2)
        pygame.draw.circle(ecran, BLANC, (int(self.x - 20), int(self.y - 10)), self.taille // 2)

class Jeu:
    def __init__(self):
        self.oiseau = Oiseau(100, HAUTEUR // 2)
        self.obstacles = []
        self.nourritures = []
        self.nuages = []
        self.score = 0
        self.meilleur_score = 0
        self.temps_obstacle = 0
        self.temps_nourriture = 0
        self.game_over = False
        self.niveau = 1
        self.vitesse_jeu = 1
        
        # Créer des nuages de fond
        for i in range(3):
            x = random.randint(0, LARGEUR)
            y = random.randint(50, 200)
            self.nuages.append(Nuage(x, y))
    
    def update(self):
        if self.game_over:
            return
        
        # Mettre à jour l'oiseau
        if not self.oiseau.update():
            self.game_over = True
            return
        
        # Vérifier si l'oiseau meurt de faim ou de fatigue
        if self.oiseau.faim <= 0 or self.oiseau.energie <= 0:
            self.game_over = True
            return
        
        # Mettre à jour les nuages
        for nuage in self.nuages:
            nuage.update()
        
        # Générer des obstacles
        self.temps_obstacle += 1
        if self.temps_obstacle > 120:  # Tous les 2 secondes
            self.temps_obstacle = 0
            hauteur_ouverture = 150
            hauteur_haut = random.randint(50, HAUTEUR - hauteur_ouverture - 50)
            hauteur_bas = HAUTEUR - hauteur_haut - hauteur_ouverture
            self.obstacles.append(Obstacle(LARGEUR, hauteur_haut, hauteur_bas))
        
        # Générer de la nourriture
        self.temps_nourriture += 1
        if self.temps_nourriture > 90:  # Tous les 1.5 secondes
            self.temps_nourriture = 0
            x = LARGEUR + 50
            y = random.randint(50, HAUTEUR - 50)
            types_nourriture = ["graine", "fruit", "insecte", "poison"]
            probabilites = [0.4, 0.3, 0.2, 0.1]  # Probabilités
            type_nourriture = random.choices(types_nourriture, probabilites)[0]
            self.nourritures.append(Nourriture(x, y, type_nourriture))
        
        # Mettre à jour les obstacles
        self.obstacles = [obs for obs in self.obstacles if obs.update()]
        
        # Mettre à jour la nourriture
        self.nourritures = [nour for nour in self.nourritures if nour.update()]
        
        # Vérifier les collisions
        self.verifier_collisions()
        
        # Augmenter le niveau
        if self.score > 0 and self.score % 50 == 0:
            self.niveau = min(self.niveau + 1, 10)
            self.vitesse_jeu = 1 + (self.niveau - 1) * 0.2
    
    def verifier_collisions(self):
        oiseau_rect = self.oiseau.get_rect()
        
        # Collision avec les obstacles
        for obstacle in self.obstacles:
            rect_haut, rect_bas = obstacle.get_rects()
            if oiseau_rect.colliderect(rect_haut) or oiseau_rect.colliderect(rect_bas):
                self.game_over = True
                return
            
            # Compter les points pour passer les obstacles
            if not obstacle.passe and obstacle.x + obstacle.largeur < self.oiseau.x:
                obstacle.passe = True
                self.score += 10
        
        # Collision avec la nourriture
        for nourriture in self.nourritures:
            if not nourriture.collectee and oiseau_rect.colliderect(nourriture.get_rect()):
                nourriture.collectee = True
                self.oiseau.manger(nourriture.type)
                self.score += nourriture.points
                self.score = max(0, self.score)  # Empêcher le score négatif
    
    def sauter(self):
        if not self.game_over:
            self.oiseau.sauter()
    
    def redemarrer(self):
        self.meilleur_score = max(self.meilleur_score, self.score)
        self.__init__()
    
    def dessiner_fond(self, ecran):
        # Dégradé de couleur pour le ciel
        for y in range(HAUTEUR):
            couleur_r = int(135 + (206 - 135) * (y / HAUTEUR))
            couleur_g = int(206 + (250 - 206) * (y / HAUTEUR))
            couleur_b = int(235 + (250 - 235) * (y / HAUTEUR))
            pygame.draw.line(ecran, (couleur_r, couleur_g, couleur_b), (0, y), (LARGEUR, y))
        
        # Dessiner les nuages
        for nuage in self.nuages:
            nuage.dessiner(ecran)
        
        # Sol
        pygame.draw.rect(ecran, VERT, (0, HAUTEUR - 20, LARGEUR, 20))
    
    def dessiner_interface(self, ecran):
        font = pygame.font.Font(None, 36)
        
        # Score
        score_text = font.render(f"Score: {self.score}", True, NOIR)
        ecran.blit(score_text, (10, 10))
        
        # Niveau
        niveau_text = font.render(f"Niveau: {self.niveau}", True, NOIR)
        ecran.blit(niveau_text, (10, 50))
        
        # Barres de faim et d'énergie
        barre_largeur = 200
        barre_hauteur = 20
        
        # Barre de faim
        pygame.draw.rect(ecran, ROUGE, (10, 90, barre_largeur, barre_hauteur))
        pygame.draw.rect(ecran, VERT, (10, 90, int(barre_largeur * (self.oiseau.faim / 100)), barre_hauteur))
        pygame.draw.rect(ecran, NOIR, (10, 90, barre_largeur, barre_hauteur), 2)
        
        faim_text = pygame.font.Font(None, 24).render("Faim", True, NOIR)
        ecran.blit(faim_text, (220, 95))
        
        # Barre d'énergie
        pygame.draw.rect(ecran, ROUGE, (10, 120, barre_largeur, barre_hauteur))
        pygame.draw.rect(ecran, BLEU, (10, 120, int(barre_largeur * (self.oiseau.energie / 100)), barre_hauteur))
        pygame.draw.rect(ecran, NOIR, (10, 120, barre_largeur, barre_hauteur), 2)
        
        energie_text = pygame.font.Font(None, 24).render("Énergie", True, NOIR)
        ecran.blit(energie_text, (220, 125))
        
        # Instructions
        instructions = [
            "Espace/Clic: Voler",
            "Collectez la nourriture",
            "Évitez les obstacles",
            "Échap: Quitter"
        ]
        
        for i, instruction in enumerate(instructions):
            text = pygame.font.Font(None, 24).render(instruction, True, NOIR)
            ecran.blit(text, (LARGEUR - 200, 10 + i * 25))
        
        # Légende des nourritures
        legende = [
            ("Graine: +10 pts", MARRON),
            ("Fruit: +20 pts", ROUGE),
            ("Insecte: +15 pts", NOIR),
            ("Poison: -50 pts", VIOLET)
        ]
        
        for i, (text, couleur) in enumerate(legende):
            text_surface = pygame.font.Font(None, 20).render(text, True, couleur)
            ecran.blit(text_surface, (10, HAUTEUR - 120 + i * 25))

def afficher_game_over(ecran, score, meilleur_score):
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
    
    # Score
    score_text = font_medium.render(f"Score: {score}", True, BLANC)
    score_rect = score_text.get_rect(center=(LARGEUR//2, HAUTEUR//2 - 50))
    ecran.blit(score_text, score_rect)
    
    # Meilleur score
    best_text = font_medium.render(f"Meilleur: {meilleur_score}", True, JAUNE)
    best_rect = best_text.get_rect(center=(LARGEUR//2, HAUTEUR//2 - 10))
    ecran.blit(best_text, best_rect)
    
    # Instructions
    restart_text = font_medium.render("Appuyez sur R pour recommencer", True, BLANC)
    restart_rect = restart_text.get_rect(center=(LARGEUR//2, HAUTEUR//2 + 30))
    ecran.blit(restart_text, restart_rect)

def main():
    ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
    pygame.display.set_caption("Hungry Birds - Jeu Python")
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
                elif event.key == pygame.K_SPACE:
                    jeu.sauter()
                elif event.key == pygame.K_r:
                    jeu.redemarrer()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Clic gauche
                    jeu.sauter()
        
        # Mise à jour du jeu
        jeu.update()
        
        # Affichage
        jeu.dessiner_fond(ecran)
        
        # Dessiner les objets
        for obstacle in jeu.obstacles:
            obstacle.dessiner(ecran)
        
        for nourriture in jeu.nourritures:
            nourriture.dessiner(ecran)
        
        jeu.oiseau.dessiner(ecran)
        jeu.dessiner_interface(ecran)
        
        # Afficher game over si nécessaire
        if jeu.game_over:
            afficher_game_over(ecran, jeu.score, jeu.meilleur_score)
        
        pygame.display.flip()
        horloge.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
