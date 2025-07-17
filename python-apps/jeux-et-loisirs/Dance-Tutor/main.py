import cv2
import mediapipe as mp
import numpy as np
import pygame
import sys
import math
import time
import json
from datetime import datetime

# Initialisation de pygame
pygame.init()
pygame.mixer.init()

# Constantes
WIDTH = 1200
HEIGHT = 800
FPS = 30

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
BLUE = (0, 100, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
PINK = (255, 192, 203)

# Initialisation de MediaPipe
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# Poses de danse prédéfinies
DANCE_POSES = {
    "Victory": {
        "description": "Bras levés en V",
        "keypoints": {
            "left_wrist": (0.3, 0.2),
            "right_wrist": (0.7, 0.2),
            "left_elbow": (0.4, 0.3),
            "right_elbow": (0.6, 0.3)
        },
        "tolerance": 0.15
    },
    "T-Pose": {
        "description": "Bras étendus horizontalement",
        "keypoints": {
            "left_wrist": (0.1, 0.5),
            "right_wrist": (0.9, 0.5),
            "left_elbow": (0.2, 0.5),
            "right_elbow": (0.8, 0.5)
        },
        "tolerance": 0.1
    },
    "Hands Up": {
        "description": "Mains en l'air",
        "keypoints": {
            "left_wrist": (0.4, 0.1),
            "right_wrist": (0.6, 0.1),
            "left_elbow": (0.4, 0.2),
            "right_elbow": (0.6, 0.2)
        },
        "tolerance": 0.12
    },
    "Disco": {
        "description": "Bras diagonaux",
        "keypoints": {
            "left_wrist": (0.2, 0.3),
            "right_wrist": (0.8, 0.7),
            "left_elbow": (0.3, 0.4),
            "right_elbow": (0.7, 0.6)
        },
        "tolerance": 0.15
    },
    "Salute": {
        "description": "Salut militaire",
        "keypoints": {
            "right_wrist": (0.65, 0.25),
            "right_elbow": (0.6, 0.35),
            "left_wrist": (0.35, 0.6),
            "left_elbow": (0.4, 0.5)
        },
        "tolerance": 0.1
    }
}

class DanceTutor:
    def __init__(self):
        self.pose = mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        self.current_pose = None
        self.target_pose = list(DANCE_POSES.keys())[0]
        self.pose_index = 0
        self.score = 0
        self.total_poses = 0
        self.pose_held_time = 0
        self.required_hold_time = 2.0  # seconds
        self.feedback_message = "Préparez-vous à danser!"
        self.feedback_color = WHITE
        
        # Système de séquence
        self.dance_sequence = list(DANCE_POSES.keys())
        self.sequence_mode = False
        self.sequence_index = 0
        self.sequence_score = 0
        
        # Historique des performances
        self.performance_history = []
        self.best_score = 0
        
        # Interface
        self.show_skeleton = True
        self.show_target_pose = True
        self.difficulty = "Normal"
        
        # Chronomètre
        self.start_time = time.time()
        self.session_time = 0
        
        # Effets visuels
        self.particles = []
        self.success_animation = 0
        
    def calculate_distance(self, point1, point2):
        """Calcule la distance entre deux points"""
        return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    
    def extract_pose_keypoints(self, landmarks):
        """Extrait les points clés de la pose"""
        if not landmarks:
            return None
            
        keypoints = {}
        
        # Mapping des indices MediaPipe
        mp_keypoints = {
            "left_wrist": mp_pose.PoseLandmark.LEFT_WRIST,
            "right_wrist": mp_pose.PoseLandmark.RIGHT_WRIST,
            "left_elbow": mp_pose.PoseLandmark.LEFT_ELBOW,
            "right_elbow": mp_pose.PoseLandmark.RIGHT_ELBOW,
            "left_shoulder": mp_pose.PoseLandmark.LEFT_SHOULDER,
            "right_shoulder": mp_pose.PoseLandmark.RIGHT_SHOULDER,
            "left_hip": mp_pose.PoseLandmark.LEFT_HIP,
            "right_hip": mp_pose.PoseLandmark.RIGHT_HIP
        }
        
        for name, landmark_idx in mp_keypoints.items():
            landmark = landmarks.landmark[landmark_idx]
            keypoints[name] = (landmark.x, landmark.y)
            
        return keypoints
    
    def compare_poses(self, current_keypoints, target_pose_name):
        """Compare la pose actuelle avec la pose cible"""
        if not current_keypoints:
            return False, 0.0
            
        target_pose = DANCE_POSES[target_pose_name]
        target_keypoints = target_pose["keypoints"]
        tolerance = target_pose["tolerance"]
        
        total_distance = 0.0
        valid_points = 0
        
        for keypoint_name, target_pos in target_keypoints.items():
            if keypoint_name in current_keypoints:
                current_pos = current_keypoints[keypoint_name]
                distance = self.calculate_distance(current_pos, target_pos)
                total_distance += distance
                valid_points += 1
        
        if valid_points == 0:
            return False, 0.0
            
        avg_distance = total_distance / valid_points
        accuracy = max(0, 1 - (avg_distance / tolerance))
        
        is_match = avg_distance <= tolerance
        return is_match, accuracy
    
    def create_particle(self, x, y, color):
        """Crée une particule d'effet visuel"""
        particle = {
            "x": x,
            "y": y,
            "vx": np.random.uniform(-5, 5),
            "vy": np.random.uniform(-8, -3),
            "color": color,
            "life": 1.0,
            "size": np.random.uniform(3, 8)
        }
        self.particles.append(particle)
    
    def update_particles(self):
        """Met à jour les particules"""
        for particle in self.particles[:]:
            particle["x"] += particle["vx"]
            particle["y"] += particle["vy"]
            particle["vy"] += 0.3  # Gravité
            particle["life"] -= 0.02
            
            if particle["life"] <= 0:
                self.particles.remove(particle)
    
    def draw_particles(self, screen):
        """Dessine les particules"""
        for particle in self.particles:
            alpha = int(particle["life"] * 255)
            color = (*particle["color"], alpha)
            size = int(particle["size"] * particle["life"])
            
            if size > 0:
                pygame.draw.circle(screen, particle["color"], 
                                 (int(particle["x"]), int(particle["y"])), size)
    
    def draw_target_pose_guide(self, screen):
        """Dessine le guide de la pose cible"""
        if not self.show_target_pose:
            return
            
        target_pose = DANCE_POSES[self.target_pose]
        keypoints = target_pose["keypoints"]
        
        # Zone de guide
        guide_rect = pygame.Rect(WIDTH - 300, 50, 250, 200)
        pygame.draw.rect(screen, (0, 0, 0, 100), guide_rect)
        pygame.draw.rect(screen, WHITE, guide_rect, 2)
        
        # Titre
        font = pygame.font.Font(None, 24)
        title_text = font.render(f"Pose: {self.target_pose}", True, WHITE)
        screen.blit(title_text, (guide_rect.x + 10, guide_rect.y + 10))
        
        # Description
        desc_text = font.render(target_pose["description"], True, LIGHT_GRAY)
        screen.blit(desc_text, (guide_rect.x + 10, guide_rect.y + 35))
        
        # Dessiner les points de la pose cible
        for keypoint_name, (x, y) in keypoints.items():
            screen_x = guide_rect.x + 50 + int(x * 150)
            screen_y = guide_rect.y + 80 + int(y * 100)
            
            color = GREEN if "wrist" in keypoint_name else BLUE
            pygame.draw.circle(screen, color, (screen_x, screen_y), 8)
            
            # Nom du point
            text = pygame.font.Font(None, 16).render(keypoint_name.replace("_", " "), True, WHITE)
            screen.blit(text, (screen_x - 20, screen_y + 12))
    
    def draw_pose_skeleton(self, screen, landmarks, accuracy=0.0):
        """Dessine le squelette de la pose"""
        if not landmarks or not self.show_skeleton:
            return
            
        # Connexions du squelette
        connections = [
            (mp_pose.PoseLandmark.LEFT_SHOULDER, mp_pose.PoseLandmark.RIGHT_SHOULDER),
            (mp_pose.PoseLandmark.LEFT_SHOULDER, mp_pose.PoseLandmark.LEFT_ELBOW),
            (mp_pose.PoseLandmark.LEFT_ELBOW, mp_pose.PoseLandmark.LEFT_WRIST),
            (mp_pose.PoseLandmark.RIGHT_SHOULDER, mp_pose.PoseLandmark.RIGHT_ELBOW),
            (mp_pose.PoseLandmark.RIGHT_ELBOW, mp_pose.PoseLandmark.RIGHT_WRIST),
            (mp_pose.PoseLandmark.LEFT_HIP, mp_pose.PoseLandmark.RIGHT_HIP),
            (mp_pose.PoseLandmark.LEFT_SHOULDER, mp_pose.PoseLandmark.LEFT_HIP),
            (mp_pose.PoseLandmark.RIGHT_SHOULDER, mp_pose.PoseLandmark.RIGHT_HIP)
        ]
        
        # Couleur basée sur la précision
        if accuracy > 0.8:
            color = GREEN
        elif accuracy > 0.5:
            color = YELLOW
        else:
            color = RED
        
        # Dessiner les connexions
        for connection in connections:
            start_landmark = landmarks.landmark[connection[0]]
            end_landmark = landmarks.landmark[connection[1]]
            
            start_pos = (int(start_landmark.x * 640), int(start_landmark.y * 480))
            end_pos = (int(end_landmark.x * 640), int(end_landmark.y * 480))
            
            pygame.draw.line(screen, color, start_pos, end_pos, 3)
        
        # Dessiner les points clés
        for landmark in landmarks.landmark:
            if landmark.visibility > 0.5:
                pos = (int(landmark.x * 640), int(landmark.y * 480))
                pygame.draw.circle(screen, color, pos, 5)
    
    def draw_interface(self, screen):
        """Dessine l'interface utilisateur"""
        # Titre
        font_large = pygame.font.Font(None, 48)
        title = font_large.render("Professeur de Danse", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 10))
        
        # Score et statistiques
        font = pygame.font.Font(None, 32)
        score_text = font.render(f"Score: {self.score}/{self.total_poses}", True, WHITE)
        screen.blit(score_text, (10, 80))
        
        accuracy = (self.score / max(1, self.total_poses)) * 100
        accuracy_text = font.render(f"Précision: {accuracy:.1f}%", True, WHITE)
        screen.blit(accuracy_text, (10, 120))
        
        # Temps de session
        self.session_time = time.time() - self.start_time
        time_text = font.render(f"Temps: {self.session_time:.1f}s", True, WHITE)
        screen.blit(time_text, (10, 160))
        
        # Pose actuelle
        pose_text = font.render(f"Pose cible: {self.target_pose}", True, WHITE)
        screen.blit(pose_text, (10, 200))
        
        # Temps de maintien
        hold_text = font.render(f"Maintenir: {self.pose_held_time:.1f}/{self.required_hold_time}s", True, WHITE)
        screen.blit(hold_text, (10, 240))
        
        # Feedback
        feedback_font = pygame.font.Font(None, 36)
        feedback_text = feedback_font.render(self.feedback_message, True, self.feedback_color)
        screen.blit(feedback_text, (WIDTH // 2 - feedback_text.get_width() // 2, HEIGHT - 100))
        
        # Barre de progression
        progress_width = 300
        progress_height = 20
        progress_x = WIDTH // 2 - progress_width // 2
        progress_y = HEIGHT - 150
        
        pygame.draw.rect(screen, GRAY, (progress_x, progress_y, progress_width, progress_height))
        
        if self.required_hold_time > 0:
            progress = min(1.0, self.pose_held_time / self.required_hold_time)
            pygame.draw.rect(screen, GREEN, (progress_x, progress_y, int(progress_width * progress), progress_height))
        
        pygame.draw.rect(screen, WHITE, (progress_x, progress_y, progress_width, progress_height), 2)
        
        # Contrôles
        controls = [
            "Espace: Pose suivante",
            "S: Activer/désactiver squelette",
            "G: Activer/désactiver guide",
            "R: Réinitialiser",
            "Échap: Quitter"
        ]
        
        for i, control in enumerate(controls):
            text = pygame.font.Font(None, 20).render(control, True, LIGHT_GRAY)
            screen.blit(text, (10, HEIGHT - 150 + i * 25))
        
        # Mode séquence
        if self.sequence_mode:
            seq_text = font.render(f"Mode Séquence: {self.sequence_index + 1}/{len(self.dance_sequence)}", True, YELLOW)
            screen.blit(seq_text, (WIDTH - 300, HEIGHT - 50))
    
    def process_frame(self, frame):
        """Traite une frame de la caméra"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb_frame)
        
        if results.pose_landmarks:
            keypoints = self.extract_pose_keypoints(results.pose_landmarks)
            is_match, accuracy = self.compare_poses(keypoints, self.target_pose)
            
            if is_match:
                self.pose_held_time += 1/FPS
                self.feedback_message = f"Excellent! Maintenez la pose... {self.pose_held_time:.1f}s"
                self.feedback_color = GREEN
                
                if self.pose_held_time >= self.required_hold_time:
                    self.score += 1
                    self.total_poses += 1
                    self.pose_held_time = 0
                    
                    # Effets visuels
                    for _ in range(10):
                        self.create_particle(WIDTH // 2, HEIGHT // 2, 
                                           (np.random.randint(0, 255), np.random.randint(0, 255), np.random.randint(0, 255)))
                    
                    self.success_animation = 30
                    self.feedback_message = "Parfait! Pose réussie!"
                    self.next_pose()
            else:
                self.pose_held_time = 0
                if accuracy > 0.7:
                    self.feedback_message = "Presque! Ajustez votre position"
                    self.feedback_color = YELLOW
                elif accuracy > 0.4:
                    self.feedback_message = "Continuez, vous y êtes presque"
                    self.feedback_color = ORANGE
                else:
                    self.feedback_message = "Regardez le guide et positionnez-vous"
                    self.feedback_color = RED
            
            return results.pose_landmarks, accuracy
        else:
            self.pose_held_time = 0
            self.feedback_message = "Positionnez-vous face à la caméra"
            self.feedback_color = WHITE
            return None, 0.0
    
    def next_pose(self):
        """Passe à la pose suivante"""
        if self.sequence_mode:
            self.sequence_index += 1
            if self.sequence_index >= len(self.dance_sequence):
                self.sequence_index = 0
                self.feedback_message = "Séquence terminée! Recommençons"
            self.target_pose = self.dance_sequence[self.sequence_index]
        else:
            self.pose_index = (self.pose_index + 1) % len(DANCE_POSES)
            self.target_pose = list(DANCE_POSES.keys())[self.pose_index]
    
    def reset_session(self):
        """Réinitialise la session"""
        self.score = 0
        self.total_poses = 0
        self.pose_held_time = 0
        self.start_time = time.time()
        self.feedback_message = "Session réinitialisée!"
        self.feedback_color = WHITE
        self.particles = []
        self.success_animation = 0
    
    def run(self):
        """Boucle principale de l'application"""
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Professeur de Danse")
        clock = pygame.time.Clock()
        
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        self.next_pose()
                    elif event.key == pygame.K_s:
                        self.show_skeleton = not self.show_skeleton
                    elif event.key == pygame.K_g:
                        self.show_target_pose = not self.show_target_pose
                    elif event.key == pygame.K_r:
                        self.reset_session()
                    elif event.key == pygame.K_m:
                        self.sequence_mode = not self.sequence_mode
                        self.feedback_message = f"Mode séquence: {'ON' if self.sequence_mode else 'OFF'}"
            
            # Capturer frame de la caméra
            ret, frame = self.cap.read()
            if ret:
                # Miroir horizontal
                frame = cv2.flip(frame, 1)
                
                # Traiter la frame
                landmarks, accuracy = self.process_frame(frame)
                
                # Convertir frame OpenCV en surface pygame
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_surface = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))
                
                # Dessiner
                screen.fill(BLACK)
                screen.blit(frame_surface, (0, 0))
                
                # Dessiner le squelette
                self.draw_pose_skeleton(screen, landmarks, accuracy)
                
                # Dessiner le guide de pose
                self.draw_target_pose_guide(screen)
                
                # Mettre à jour et dessiner les particules
                self.update_particles()
                self.draw_particles(screen)
                
                # Dessiner l'interface
                self.draw_interface(screen)
                
                # Animation de succès
                if self.success_animation > 0:
                    self.success_animation -= 1
                    overlay = pygame.Surface((WIDTH, HEIGHT))
                    overlay.set_alpha(self.success_animation * 5)
                    overlay.fill(GREEN)
                    screen.blit(overlay, (0, 0))
            
            pygame.display.flip()
            clock.tick(FPS)
        
        self.cap.release()
        pygame.quit()
        sys.exit()

def main():
    try:
        tutor = DanceTutor()
        tutor.run()
    except Exception as e:
        print(f"Erreur: {e}")
        print("Assurez-vous que votre caméra est connectée et que les dépendances sont installées.")
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()
