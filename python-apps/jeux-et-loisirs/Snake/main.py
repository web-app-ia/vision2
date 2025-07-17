import pygame
import sys
import random

# Initialisation de pygame
pygame.init()

# Constantes
LARGEUR = 600
HAUTEUR = 600
TAILLE_CELLULE = 20
FPS = 10

# Couleurs
NOIR = (0, 0, 0)
BLANC = (255, 255, 255)
VERT = (0, 255, 0)
ROUGE = (255, 0, 0)
BLEU = (0, 0, 255)
JAUNE = (255, 255, 0)

# Directions
HAUT = (0, -1)
BAS = (0, 1)
GAUCHE = (-1, 0)
DROITE = (1, 0)

class Snake:
    def __init__(self):
        self.corps = [(LARGEUR // 2 // TAILLE_CELLULE, HAUTEUR // 2 // TAILLE_CELLULE)]
        self.direction = DROITE
        self.grandir = False
        
    def bouger(self):
        tete = self.corps[0]
        nouvelle_tete = (tete[0] + self.direction[0], tete[1] + self.direction[1])
        
        # Vérifier les collisions avec les murs
        if (nouvelle_tete[0] < 0 or nouvelle_tete[0] >= LARGEUR // TAILLE_CELLULE or
            nouvelle_tete[1] < 0 or nouvelle_tete[1] >= HAUTEUR // TAILLE_CELLULE):
            return False
        
        # Vérifier les collisions avec le corps
        if nouvelle_tete in self.corps:
            return False
        
        self.corps.insert(0, nouvelle_tete)
        
        if not self.grandir:
            self.corps.pop()
        else:
            self.grandir = False
        
        return True
    
    def changer_direction(self, nouvelle_direction):
        # Empêcher de faire demi-tour
        if (self.direction[0] * -1, self.direction[1] * -1) != nouvelle_direction:
            self.direction = nouvelle_direction
    
    def manger(self):
        self.grandir = True
    
    def dessiner(self, ecran):
        for i, segment in enumerate(self.corps):
            x = segment[0] * TAILLE_CELLULE
            y = segment[1] * TAILLE_CELLULE
            
            if i == 0:  # Tête
                pygame.draw.rect(ecran, VERT, (x, y, TAILLE_CELLULE, TAILLE_CELLULE))
                pygame.draw.rect(ecran, NOIR, (x, y, TAILLE_CELLULE, TAILLE_CELLULE), 2)
                # Yeux
                pygame.draw.circle(ecran, NOIR, (x + 5, y + 5), 2)
                pygame.draw.circle(ecran, NOIR, (x + 15, y + 5), 2)
            else:  # Corps
                pygame.draw.rect(ecran, VERT, (x, y, TAILLE_CELLULE, TAILLE_CELLULE))
                pygame.draw.rect(ecran, NOIR, (x, y, TAILLE_CELLULE, TAILLE_CELLULE), 1)

class Nourriture:
    def __init__(self):
        self.position = self.generer_position()
        self.type = random.choice(['normale', 'bonus', 'malus'])
        
    def generer_position(self):
        x = random.randint(0, (LARGEUR // TAILLE_CELLULE) - 1)
        y = random.randint(0, (HAUTEUR // TAILLE_CELLULE) - 1)
        return (x, y)
    
    def dessiner(self, ecran):
        x = self.position[0] * TAILLE_CELLULE
        y = self.position[1] * TAILLE_CELLULE
        
        if self.type == 'normale':
            pygame.draw.rect(ecran, ROUGE, (x, y, TAILLE_CELLULE, TAILLE_CELLULE))
        elif self.type == 'bonus':
            pygame.draw.rect(ecran, JAUNE, (x, y, TAILLE_CELLULE, TAILLE_CELLULE))
        else:  # malus
            pygame.draw.rect(ecran, BLEU, (x, y, TAILLE_CELLULE, TAILLE_CELLULE))
        
        pygame.draw.rect(ecran, NOIR, (x, y, TAILLE_CELLULE, TAILLE_CELLULE), 2)

class Jeu:
    def __init__(self):
        self.snake = Snake()
        self.nourriture = Nourriture()
        self.score = 0
        self.niveau = 1
        self.fps = FPS
        
    def verifier_collision_nourriture(self):
        if self.snake.corps[0] == self.nourriture.position:
            if self.nourriture.type == 'normale':
                self.score += 10
                self.snake.manger()
            elif self.nourriture.type == 'bonus':
                self.score += 20
                self.snake.manger()
                self.fps = min(self.fps + 1, 15)  # Augmenter la vitesse
            else:  # malus
                self.score = max(0, self.score - 5)
                # Réduire le snake
                if len(self.snake.corps) > 1:
                    self.snake.corps.pop()
            
            # Générer nouvelle nourriture
            self.nouvelle_nourriture()
            
            # Augmenter le niveau
            if self.score > 0 and self.score % 100 == 0:
                self.niveau += 1
                self.fps = min(self.fps + 1, 20)
        
    def nouvelle_nourriture(self):
        while True:
            self.nourriture = Nourriture()
            if self.nourriture.position not in self.snake.corps:
                break
    
    def dessiner_interface(self, ecran):
        font = pygame.font.Font(None, 36)
        
        # Score
        score_text = font.render(f"Score: {self.score}", True, BLANC)
        ecran.blit(score_text, (10, 10))
        
        # Niveau
        niveau_text = font.render(f"Niveau: {self.niveau}", True, BLANC)
        ecran.blit(niveau_text, (10, 50))
        
        # Instructions
        instructions = [
            "Flèches: Déplacer",
            "R: Redémarrer",
            "Échap: Quitter"
        ]
        
        for i, instruction in enumerate(instructions):
            text = pygame.font.Font(None, 24).render(instruction, True, BLANC)
            ecran.blit(text, (LARGEUR - 150, 10 + i * 25))
        
        # Légende des couleurs
        legende = [
            ("Rouge: +10 pts", ROUGE),
            ("Jaune: +20 pts", JAUNE),
            ("Bleu: -5 pts", BLEU)
        ]
        
        for i, (text, couleur) in enumerate(legende):
            text_surface = pygame.font.Font(None, 20).render(text, True, couleur)
            ecran.blit(text_surface, (10, HAUTEUR - 80 + i * 25))

def afficher_game_over(ecran, score):
    font_large = pygame.font.Font(None, 72)
    font_medium = pygame.font.Font(None, 36)
    
    # Fond semi-transparent
    overlay = pygame.Surface((LARGEUR, HAUTEUR))
    overlay.set_alpha(128)
    overlay.fill(NOIR)
    ecran.blit(overlay, (0, 0))
    
    # Texte Game Over
    game_over_text = font_large.render("GAME OVER", True, ROUGE)
    game_over_rect = game_over_text.get_rect(center=(LARGEUR//2, HAUTEUR//2 - 50))
    ecran.blit(game_over_text, game_over_rect)
    
    # Score final
    score_text = font_medium.render(f"Score final: {score}", True, BLANC)
    score_rect = score_text.get_rect(center=(LARGEUR//2, HAUTEUR//2 + 10))
    ecran.blit(score_text, score_rect)
    
    # Instructions
    restart_text = font_medium.render("Appuyez sur R pour recommencer", True, BLANC)
    restart_rect = restart_text.get_rect(center=(LARGEUR//2, HAUTEUR//2 + 50))
    ecran.blit(restart_text, restart_rect)

def main():
    ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
    pygame.display.set_caption("Snake - Jeu Python")
    horloge = pygame.time.Clock()
    
    jeu = Jeu()
    game_over = False
    
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
                    game_over = False
                elif not game_over:
                    if event.key == pygame.K_UP:
                        jeu.snake.changer_direction(HAUT)
                    elif event.key == pygame.K_DOWN:
                        jeu.snake.changer_direction(BAS)
                    elif event.key == pygame.K_LEFT:
                        jeu.snake.changer_direction(GAUCHE)
                    elif event.key == pygame.K_RIGHT:
                        jeu.snake.changer_direction(DROITE)
        
        if not game_over:
            # Mise à jour du jeu
            if not jeu.snake.bouger():
                game_over = True
            
            jeu.verifier_collision_nourriture()
        
        # Affichage
        ecran.fill(NOIR)
        
        # Grille
        for x in range(0, LARGEUR, TAILLE_CELLULE):
            pygame.draw.line(ecran, (20, 20, 20), (x, 0), (x, HAUTEUR))
        for y in range(0, HAUTEUR, TAILLE_CELLULE):
            pygame.draw.line(ecran, (20, 20, 20), (0, y), (LARGEUR, y))
        
        # Dessiner les objets du jeu
        jeu.snake.dessiner(ecran)
        jeu.nourriture.dessiner(ecran)
        jeu.dessiner_interface(ecran)
        
        if game_over:
            afficher_game_over(ecran, jeu.score)
        
        pygame.display.flip()
        horloge.tick(jeu.fps)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
