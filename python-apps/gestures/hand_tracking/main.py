import cv2

# Configuration pour le mode plein écran
def setup_fullscreen_window(window_name):
    """Configure une fenêtre pour le mode plein écran"""
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    return True

def toggle_fullscreen(window_name, is_fullscreen):
    """Bascule entre mode plein écran et fenêtre normale"""
    if is_fullscreen:
        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
        print("Mode fenêtre normale activé")
        return False
    else:
        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        print("Mode plein écran activé")
        return True

import mediapipe as mp
import numpy as np
import math
import time

class HandTrackingApp:
    def __init__(self):
        # Configuration MediaPipe
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Initialiser le détecteur de mains
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        
        # Variables pour le suivi
        self.prev_landmarks = None
        self.gesture_history = []
        self.fps_counter = 0
        self.fps_time = time.time()
        self.current_fps = 0
        
    def calculate_distance(self, point1, point2):
        """Calcule la distance entre deux points."""
        return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    
    def detect_gesture(self, landmarks):
        """Détecte des gestes simples basés sur les landmarks."""
        if not landmarks:
            return "Aucune main détectée"
        
        # Obtenir les coordonnées des doigts
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        middle_tip = landmarks[12]
        ring_tip = landmarks[16]
        pinky_tip = landmarks[20]
        
        # Obtenir les coordonnées des articulations
        thumb_ip = landmarks[3]
        index_pip = landmarks[6]
        middle_pip = landmarks[10]
        ring_pip = landmarks[14]
        pinky_pip = landmarks[18]
        
        # Compter les doigts levés
        fingers_up = 0
        
        # Pouce (logique spéciale car il se déplace horizontalement)
        if thumb_tip[0] > thumb_ip[0]:  # Pour la main droite
            fingers_up += 1
        
        # Autres doigts
        if index_tip[1] < index_pip[1]:
            fingers_up += 1
        if middle_tip[1] < middle_pip[1]:
            fingers_up += 1
        if ring_tip[1] < ring_pip[1]:
            fingers_up += 1
        if pinky_tip[1] < pinky_pip[1]:
            fingers_up += 1
        
        # Déterminer le geste
        if fingers_up == 0:
            return "Poing fermé"
        elif fingers_up == 1:
            return "Un doigt"
        elif fingers_up == 2:
            return "Deux doigts"
        elif fingers_up == 3:
            return "Trois doigts"
        elif fingers_up == 4:
            return "Quatre doigts"
        elif fingers_up == 5:
            return "Main ouverte"
        else:
            return f"{fingers_up} doigts levés"
    
    def calculate_hand_velocity(self, current_landmarks):
        """Calcule la vitesse de mouvement de la main."""
        if self.prev_landmarks is None:
            self.prev_landmarks = current_landmarks
            return 0
        
        # Utiliser le poignet comme point de référence
        wrist_current = current_landmarks[0]
        wrist_prev = self.prev_landmarks[0]
        
        velocity = self.calculate_distance(wrist_current, wrist_prev)
        self.prev_landmarks = current_landmarks
        
        return velocity
    
    def draw_info_panel(self, frame, gesture, velocity, hand_count):
        """Dessine un panneau d'information sur le frame."""
        panel_height = 120
        panel_width = 300
        
        # Créer un rectangle semi-transparent
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (panel_width, panel_height), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Ajouter le texte
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, f"Geste: {gesture}", (20, 40), font, 0.6, (0, 255, 0), 2)
        cv2.putText(frame, f"Mains detectees: {hand_count}", (20, 65), font, 0.6, (0, 255, 255), 2)
        cv2.putText(frame, f"Vitesse: {velocity:.1f}", (20, 90), font, 0.6, (255, 255, 0), 2)
        cv2.putText(frame, f"FPS: {self.current_fps:.1f}", (20, 115), font, 0.6, (255, 0, 255), 2)
    
    def update_fps(self):
        """Met à jour le compteur FPS."""
        self.fps_counter += 1
        current_time = time.time()
        
        if current_time - self.fps_time >= 1.0:
            self.current_fps = self.fps_counter
            self.fps_counter = 0
            self.fps_time = current_time
    
    def run(self):
        """Lance l'application de suivi des mains."""
        print("=== Application de Suivi des Mains ===")
        print("Initialisation de la caméra...")
        
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Erreur: Impossible d'ouvrir la caméra")
            return
        
        # Configurer la caméra
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        print("Caméra initialisée avec succès")
        print("Contrôles:")
        print("  - 'q' ou 'ESC' pour quitter")
        print("  - 'r' pour réinitialiser")
        print("  - 's' pour capturer une image")
        
        frame_count = 0
        
        try:
        # Configuration de la fenêtre plein écran
        window_name = "Suivi des Mains - Computer Vision App"
        setup_fullscreen_window(window_name)
        fullscreen_mode = True
        print("Mode plein écran activé - Appuyez sur 'f' pour basculer")
        
        
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Erreur lors de la lecture du frame")
                    break
                
                # Retourner horizontalement pour effet miroir
                frame = cv2.flip(frame, 1)
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Détecter les mains
                results = self.hands.process(frame_rgb)
                
                gesture = "Aucune main"
                velocity = 0
                hand_count = 0
                
                if results.multi_hand_landmarks:
                    hand_count = len(results.multi_hand_landmarks)
                    
                    for hand_landmarks in results.multi_hand_landmarks:
                        # Dessiner les landmarks
                        self.mp_drawing.draw_landmarks(
                            frame, 
                            hand_landmarks,
                            self.mp_hands.HAND_CONNECTIONS,
                            self.mp_drawing_styles.get_default_hand_landmarks_style(),
                            self.mp_drawing_styles.get_default_hand_connections_style()
                        )
                        
                        # Convertir les landmarks en coordonnées pixel
                        h, w, _ = frame.shape
                        landmarks_pixel = []
                        for lm in hand_landmarks.landmark:
                            landmarks_pixel.append([int(lm.x * w), int(lm.y * h)])
                        
                        # Détecter le geste
                        gesture = self.detect_gesture(landmarks_pixel)
                        
                        # Calculer la vitesse
                        velocity = self.calculate_hand_velocity(landmarks_pixel)
                        
                        # Dessiner le centre de la main
                        wrist = landmarks_pixel[0]
                        cv2.circle(frame, tuple(wrist), 10, (255, 0, 0), -1)
                        
                        # Dessiner une ligne entre les mains s'il y en a deux
                        if len(results.multi_hand_landmarks) == 2:
                            other_hand = results.multi_hand_landmarks[1 if results.multi_hand_landmarks[0] == hand_landmarks else 0]
                            other_wrist = [int(other_hand.landmark[0].x * w), int(other_hand.landmark[0].y * h)]
                            cv2.line(frame, tuple(wrist), tuple(other_wrist), (0, 255, 255), 2)
                
                # Mettre à jour le FPS
                self.update_fps()
                
                # Dessiner le panneau d'information
                self.draw_info_panel(frame, gesture, velocity, hand_count)
                
                # Ajouter des instructions
                cv2.putText(frame, "Appuyez sur 'q' pour quitter", (frame.shape[1] - 250, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                # Afficher le frame
                cv2.imshow('Suivi des Mains - Computer Vision App', frame)
                
                # Gestion des touches
                key = cv2.waitKey(1) & 0xFF
                
                elif key == ord(\'f\'):
                    fullscreen_mode = toggle_fullscreen(window_name, fullscreen_mode)
                if key == ord('q') or key == 27:  # 'q' ou ESC
                    print("Arrêt demandé par l'utilisateur")
                    break
                elif key == ord('r'):
                    print("Réinitialisation...")
                    self.prev_landmarks = None
                    self.gesture_history = []
                elif key == ord('s'):
                    filename = f"hand_capture_{int(time.time())}.jpg"
                    cv2.imwrite(filename, frame)
                    print(f"Image sauvegardée: {filename}")
                
                frame_count += 1
                
        except KeyboardInterrupt:
            print("Arrêt demandé par Ctrl+C")
        except Exception as e:
            print(f"Erreur: {e}")
        finally:
            print("Nettoyage des ressources...")
            cap.release()
            cv2.destroyAllWindows()
            print("Application terminée")

def main():
    print("Démarrage de l'application de suivi des mains...")
    app = HandTrackingApp()
    app.run()

if __name__ == "__main__":
    main()
