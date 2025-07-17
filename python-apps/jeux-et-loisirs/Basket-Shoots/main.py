import pygame
import sys
import math
import random

# Initialisation de pygame
pygame.init()

# Constantes
LARGEUR = 800
HAUTEUR = 600
FPS = 60
GRAVITE = 0.5

# Couleurs
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
ROUGE = (255, 0, 0)
BLEU = (0, 0, 255)
VERT = (0, 255, 0)
ORANGE = (255, 165, 0)
MARRON = (139, 69, 19)
JAUNE = (255, 255, 0)
GRIS = (128, 128, 128)

class Ballon:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rayon = 15
        self.vitesse_x = 0
        self.vitesse_y = 0
        self.lance = False
        self.rebond = 0.7
        
    def lancer(self, force_x, force_y):
        self.vitesse_x = force_x / 10
        self.vitesse_y = force_y / 10
        self.lance = True
        
    def update(self):
        if self.lance:
            # Mouvement
            self.x += self.vitesse_x
            self.y += self.vitesse_y
            
            # Gravité
            self.vitesse_y += GRAVITE
            
            # Collision avec les bords
            if self.x - self.rayon <= 0 or self.x + self.rayon >= LARGEUR:
                self.vitesse_x *= -self.rebond
                self.x = max(self.rayon, min(LARGEUR - self.rayon, self.x))
            
            if self.y + self.rayon >= HAUTEUR:
                self.vitesse_y *= -self.rebond
                self.y = HAUTEUR - self.rayon
                
                # Arrêter le ballon s'il ne bouge plus beaucoup
                if abs(self.vitesse_y) < 1 and abs(self.vitesse_x) < 1:
                    self.lance = False
                    self.vitesse_x = 0
                    self.vitesse_y = 0
    
    def dessiner(self, ecran):
        pygame.draw.circle(ecran, ORANGE, (int(self.x), int(self.y)), self.rayon)
        pygame.draw.circle(ecran, NOIR, (int(self.x), int(self.y)), self.rayon, 2)
        
        # Lignes du ballon
        pygame.draw.line(ecran, NOIR, 
                        (int(self.x - self.rayon), int(self.y)), 
                        (int(self.x + self.rayon), int(self.y)), 2)
        pygame.draw.line(ecran, NOIR, 
                        (int(self.x), int(self.y - self.rayon)), 
                        (int(self.x), int(self.y + self.rayon)), 2)

class Panier:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.largeur = 80
        self.hauteur = 10
        self.poteau_largeur = 5
        self.poteau_hauteur = 100
        self.filet_points = []
        
        # Points du filet
        for i in range(5):
            self.filet_points.append((x + i * (self.largeur / 4), y + 10 + i * 5))
    
    def verifier_score(self, ballon):
        # Vérifier si le ballon traverse le panier par le haut
        if (self.x < ballon.x < self.x + self.largeur and
            self.y - 5 < ballon.y < self.y + 5 and
            ballon.vitesse_y > 0):
            return True
        return False
    
    def dessiner(self, ecran):
        # Poteau
        pygame.draw.rect(ecran, MARRON, 
                        (self.x + self.largeur, self.y, self.poteau_largeur, self.poteau_hauteur))
        
        # Panier
        pygame.draw.rect(ecran, ROUGE, (self.x, self.y, self.largeur, self.hauteur))
        
        # Filet
        for i, point in enumerate(self.filet_points):
            if i < len(self.filet_points) - 1:
                pygame.draw.line(ecran, BLANC, point, self.filet_points[i + 1], 2)
        
        # Lignes verticales du filet
        for i in range(0, self.largeur, 20):
            pygame.draw.line(ecran, BLANC, 
                           (self.x + i, self.y + 10), 
                           (self.x + i, self.y + 30), 2)

class Joueur:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.largeur = 30
        self.hauteur = 60
        self.vitesse = 5
        
    def bouger(self, direction):
        if direction == "gauche" and self.x > 0:
            self.x -= self.vitesse
        elif direction == "droite" and self.x < LARGEUR - self.largeur:
            self.x += self.vitesse
    
    def dessiner(self, ecran):
        # Corps
        pygame.draw.rect(ecran, BLEU, (self.x, self.y, self.largeur, self.hauteur))
        
        # Tête
        pygame.draw.circle(ecran, JAUNE, (self.x + self.largeur//2, self.y - 15), 15)
        
        # Bras
        pygame.draw.line(ecran, BLEU, 
                        (self.x - 10, self.y + 20), 
                        (self.x + self.largeur + 10, self.y + 20), 5)
        
        # Jambes
        pygame.draw.line(ecran, BLEU, 
                        (self.x + 10, self.y + self.hauteur), 
                        (self.x + 5, self.y + self.hauteur + 20), 5)
        pygame.draw.line(ecran, BLEU, 
                        (self.x + 20, self.y + self.hauteur), 
                        (self.x + 25, self.y + self.hauteur + 20), 5)

class Jeu:
    def __init__(self):
        self.joueur = Joueur(50, HAUTEUR - 100)
        self.ballon = Ballon(self.joueur.x + 15, self.joueur.y - 20)
        self.panier = Panier(LARGEUR - 150, 100)
        self.score = 0
        self.tirs = 0
        self.temps_restant = 60  # 60 secondes
        self.ballon_avec_joueur = True
        self.niveau = 1
        self.vent = 0
        
    def update(self):
        # Mouvement du joueur
        touches = pygame.key.get_pressed()
        if touches[pygame.K_LEFT] or touches[pygame.K_a]:
            self.joueur.bouger("gauche")
            if self.ballon_avec_joueur:
                self.ballon.x = self.joueur.x + 15
        if touches[pygame.K_RIGHT] or touches[pygame.K_d]:
            self.joueur.bouger("droite")
            if self.ballon_avec_joueur:
                self.ballon.x = self.joueur.x + 15
        
        # Mise à jour du ballon
        if not self.ballon_avec_joueur:
            self.ballon.update()
            
            # Effet du vent
            if self.ballon.lance:
                self.ballon.vitesse_x += self.vent * 0.01
            
            # Vérifier le score
            if self.panier.verifier_score(self.ballon):
                self.score += 10
                self.remettre_ballon()
            
            # Remettre le ballon si il est arrêté
            if not self.ballon.lance:
                self.remettre_ballon()
        
        # Générer du vent aléatoire
        if random.randint(1, 120) == 1:  # Changement de vent toutes les 2 secondes environ
            self.vent = random.uniform(-2, 2)
        
        # Augmenter le niveau
        if self.score > 0 and self.score % 50 == 0:
            self.niveau = min(self.niveau + 1, 5)
            self.panier.x = random.randint(LARGEUR//2, LARGEUR - 150)
    
    def lancer_ballon(self, force_x, force_y):
        if self.ballon_avec_joueur:
            self.ballon.lancer(force_x, force_y)
            self.ballon_avec_joueur = False
            self.tirs += 1
    
    def remettre_ballon(self):
        self.ballon = Ballon(self.joueur.x + 15, self.joueur.y - 20)
        self.ballon_avec_joueur = True
    
    def dessiner_interface(self, ecran):
        font = pygame.font.Font(None, 36)
        
        # Score
        score_text = font.render(f"Score: {self.score}", True, NOIR)
        ecran.blit(score_text, (10, 10))
        
        # Tirs
        tirs_text = font.render(f"Tirs: {self.tirs}", True, NOIR)
        ecran.blit(tirs_text, (10, 50))
        
        # Temps
        temps_text = font.render(f"Temps: {self.temps_restant}", True, NOIR)
        ecran.blit(temps_text, (10, 90))
        
        # Niveau
        niveau_text = font.render(f"Niveau: {self.niveau}", True, NOIR)
        ecran.blit(niveau_text, (10, 130))
        
        # Vent
        vent_text = font.render(f"Vent: {self.vent:.1f}", True, NOIR)
        ecran.blit(vent_text, (10, 170))
        
        # Pourcentage de réussite
        if self.tirs > 0:
            pourcentage = (self.score // 10) / self.tirs * 100
            pourcentage_text = font.render(f"Précision: {pourcentage:.1f}%", True, NOIR)
            ecran.blit(pourcentage_text, (10, 210))
        
        # Instructions
        instructions = [
            "Flèches/AD: Bouger",
            "Clic: Tirer",
            "Plus le clic est loin,",
            "plus le tir est fort",
            "Échap: Quitter"
        ]
        
        for i, instruction in enumerate(instructions):
            text = pygame.font.Font(None, 24).render(instruction, True, NOIR)
            ecran.blit(text, (LARGEUR - 200, 10 + i * 25))
        
        # Indicateur de vent
        if self.vent != 0:
            vent_couleur = BLEU if self.vent < 0 else ROUGE
            pygame.draw.line(ecran, vent_couleur, 
                           (LARGEUR//2, 30), 
                           (LARGEUR//2 + self.vent * 20, 30), 5)
            pygame.draw.polygon(ecran, vent_couleur, [
                (LARGEUR//2 + self.vent * 20, 25),
                (LARGEUR//2 + self.vent * 20, 35),
                (LARGEUR//2 + self.vent * 20 + (5 if self.vent > 0 else -5), 30)
            ])

def dessiner_trajectoire(ecran, debut_x, debut_y, fin_x, fin_y):
    # Dessiner la trajectoire prévue
    points = []
    for i in range(10):
        t = i / 10
        x = debut_x + (fin_x - debut_x) * t
        y = debut_y + (fin_y - debut_y) * t + GRAVITE * t * t * 50
        points.append((int(x), int(y)))
    
    for i in range(len(points) - 1):
        pygame.draw.line(ecran, GRIS, points[i], points[i + 1], 2)

def main():
    ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
    pygame.display.set_caption("Basket Shoots - Jeu Python")
    horloge = pygame.time.Clock()
    
    jeu = Jeu()
    timer = 0
    clique = False
    debut_clic = (0, 0)
    
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
                    timer = 0
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Clic gauche
                    clique = True
                    debut_clic = event.pos
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and clique:
                    fin_clic = event.pos
                    force_x = fin_clic[0] - debut_clic[0]
                    force_y = fin_clic[1] - debut_clic[1]
                    jeu.lancer_ballon(force_x, force_y)
                    clique = False
        
        # Mise à jour du timer
        timer += 1
        if timer >= FPS:  # 1 seconde
            timer = 0
            jeu.temps_restant -= 1
            if jeu.temps_restant <= 0:
                jeu.temps_restant = 60
                jeu.score = 0
                jeu.tirs = 0
                jeu.niveau = 1
        
        # Mise à jour du jeu
        jeu.update()
        
        # Affichage
        ecran.fill(BLANC)
        
        # Dessiner le terrain
        pygame.draw.rect(ecran, VERT, (0, HAUTEUR - 50, LARGEUR, 50))
        
        # Dessiner les objets
        jeu.joueur.dessiner(ecran)
        jeu.ballon.dessiner(ecran)
        jeu.panier.dessiner(ecran)
        jeu.dessiner_interface(ecran)
        
        # Dessiner la trajectoire pendant le clic
        if clique:
            souris_pos = pygame.mouse.get_pos()
            dessiner_trajectoire(ecran, jeu.ballon.x, jeu.ballon.y, 
                               souris_pos[0], souris_pos[1])
        
        # Afficher game over si temps écoulé
        if jeu.temps_restant <= 0:
            font_large = pygame.font.Font(None, 72)
            game_over_text = font_large.render("TEMPS ÉCOULÉ!", True, ROUGE)
            game_over_rect = game_over_text.get_rect(center=(LARGEUR//2, HAUTEUR//2))
            ecran.blit(game_over_text, game_over_rect)
            
            restart_text = pygame.font.Font(None, 36).render("Appuyez sur R pour recommencer", True, NOIR)
            restart_rect = restart_text.get_rect(center=(LARGEUR//2, HAUTEUR//2 + 50))
            ecran.blit(restart_text, restart_rect)
        
        pygame.display.flip()
        horloge.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
