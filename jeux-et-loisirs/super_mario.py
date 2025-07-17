import pygame
import sys
import os

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
MARRON = (139, 69, 19)
JAUNE = (255, 255, 0)

class Mario:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.largeur = 30
        self.hauteur = 40
        self.vitesse = 5
        self.vitesse_saut = 0
        self.gravite = 0.5
        self.au_sol = False
        self.direction = 1  # 1 pour droite, -1 pour gauche
        
    def update(self, plateformes):
        # Mouvement horizontal
        touches = pygame.key.get_pressed()
        if touches[pygame.K_LEFT] or touches[pygame.K_a]:
            self.x -= self.vitesse
            self.direction = -1
        if touches[pygame.K_RIGHT] or touches[pygame.K_d]:
            self.x += self.vitesse
            self.direction = 1
        
        # Saut
        if (touches[pygame.K_SPACE] or touches[pygame.K_UP]) and self.au_sol:
            self.vitesse_saut = -12
            self.au_sol = False
        
        # Gravité
        self.vitesse_saut += self.gravite
        self.y += self.vitesse_saut
        
        # Collision avec les plateformes
        self.au_sol = False
        mario_rect = pygame.Rect(self.x, self.y, self.largeur, self.hauteur)
        
        for plateforme in plateformes:
            if mario_rect.colliderect(plateforme):
                if self.vitesse_saut > 0:  # Tombant
                    self.y = plateforme.top - self.hauteur
                    self.vitesse_saut = 0
                    self.au_sol = True
                elif self.vitesse_saut < 0:  # Montant
                    self.y = plateforme.bottom
                    self.vitesse_saut = 0
        
        # Limites de l'écran
        if self.x < 0:
            self.x = 0
        elif self.x > LARGEUR - self.largeur:
            self.x = LARGEUR - self.largeur
        
        # Chute dans le vide
        if self.y > HAUTEUR:
            self.__init__(50, HAUTEUR - 200)
    
    def dessiner(self, ecran):
        # Dessiner Mario (simplifié)
        pygame.draw.rect(ecran, ROUGE, (self.x, self.y, self.largeur, self.hauteur))
        # Chapeau
        pygame.draw.rect(ecran, MARRON, (self.x, self.y - 10, self.largeur, 10))
        # Yeux
        pygame.draw.circle(ecran, BLANC, (self.x + 8, self.y + 8), 3)
        pygame.draw.circle(ecran, BLANC, (self.x + 22, self.y + 8), 3)
        # Moustache
        pygame.draw.rect(ecran, NOIR, (self.x + 10, self.y + 15, 10, 3))

class Ennemi:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.largeur = 25
        self.hauteur = 25
        self.vitesse = 2
        self.direction = 1
        
    def update(self, plateformes):
        self.x += self.vitesse * self.direction
        
        # Collision avec les bords ou obstacles
        if self.x <= 0 or self.x >= LARGEUR - self.largeur:
            self.direction *= -1
        
        # Vérification des plateformes
        ennemi_rect = pygame.Rect(self.x, self.y, self.largeur, self.hauteur)
        for plateforme in plateformes:
            if ennemi_rect.colliderect(plateforme):
                self.direction *= -1
    
    def dessiner(self, ecran):
        pygame.draw.rect(ecran, VERT, (self.x, self.y, self.largeur, self.hauteur))
        # Yeux
        pygame.draw.circle(ecran, ROUGE, (self.x + 6, self.y + 6), 2)
        pygame.draw.circle(ecran, ROUGE, (self.x + 19, self.y + 6), 2)

class Piece:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rayon = 10
        self.collectee = False
        
    def dessiner(self, ecran):
        if not self.collectee:
            pygame.draw.circle(ecran, JAUNE, (self.x, self.y), self.rayon)
            pygame.draw.circle(ecran, NOIR, (self.x, self.y), self.rayon, 2)

def main():
    ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
    pygame.display.set_caption("Super Mario - Jeu Python")
    horloge = pygame.time.Clock()
    
    # Objets du jeu
    mario = Mario(50, HAUTEUR - 200)
    
    # Plateformes
    plateformes = [
        pygame.Rect(0, HAUTEUR - 50, LARGEUR, 50),  # Sol
        pygame.Rect(200, HAUTEUR - 150, 200, 20),
        pygame.Rect(500, HAUTEUR - 250, 150, 20),
        pygame.Rect(100, HAUTEUR - 350, 100, 20),
        pygame.Rect(600, HAUTEUR - 400, 150, 20)
    ]
    
    # Ennemis
    ennemis = [
        Ennemi(300, HAUTEUR - 130),
        Ennemi(550, HAUTEUR - 230),
        Ennemi(650, HAUTEUR - 380)
    ]
    
    # Pièces
    pieces = [
        Piece(250, HAUTEUR - 180),
        Piece(575, HAUTEUR - 280),
        Piece(150, HAUTEUR - 380),
        Piece(675, HAUTEUR - 430)
    ]
    
    score = 0
    font = pygame.font.Font(None, 36)
    
    # Boucle principale
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Mise à jour
        mario.update(plateformes)
        
        for ennemi in ennemis:
            ennemi.update(plateformes)
        
        # Collision Mario-Ennemis
        mario_rect = pygame.Rect(mario.x, mario.y, mario.largeur, mario.hauteur)
        for ennemi in ennemis:
            ennemi_rect = pygame.Rect(ennemi.x, ennemi.y, ennemi.largeur, ennemi.hauteur)
            if mario_rect.colliderect(ennemi_rect):
                # Restart du jeu
                mario = Mario(50, HAUTEUR - 200)
                score = max(0, score - 10)
        
        # Collision Mario-Pièces
        for piece in pieces:
            if not piece.collectee:
                piece_rect = pygame.Rect(piece.x - piece.rayon, piece.y - piece.rayon, 
                                       piece.rayon * 2, piece.rayon * 2)
                if mario_rect.colliderect(piece_rect):
                    piece.collectee = True
                    score += 10
        
        # Affichage
        ecran.fill(BLEU)  # Ciel
        
        # Dessiner les plateformes
        for plateforme in plateformes:
            pygame.draw.rect(ecran, MARRON, plateforme)
        
        # Dessiner les objets
        mario.dessiner(ecran)
        
        for ennemi in ennemis:
            ennemi.dessiner(ecran)
        
        for piece in pieces:
            piece.dessiner(ecran)
        
        # Afficher le score
        score_text = font.render(f"Score: {score}", True, BLANC)
        ecran.blit(score_text, (10, 10))
        
        # Instructions
        instructions = [
            "Flèches/WASD: Déplacer",
            "Espace/Haut: Sauter",
            "Échap: Quitter"
        ]
        
        for i, instruction in enumerate(instructions):
            text = pygame.font.Font(None, 24).render(instruction, True, BLANC)
            ecran.blit(text, (10, 50 + i * 25))
        
        pygame.display.flip()
        horloge.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
