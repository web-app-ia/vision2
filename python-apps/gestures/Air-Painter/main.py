import cv2

# Configuration pour le mode fenêtre maximisée
def setup_maximized_window(window_name):
    """Configure une fenêtre pour occuper une grande partie de l'écran"""
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1200, 800)
    return True

def toggle_window_mode(window_name, is_maximized):
    """Bascule entre mode maximisé et fenêtre normale"""
    if is_maximized:
        cv2.resizeWindow(window_name, 800, 600)
        print("Mode fenêtre normale activé")
        return False
    else:
        cv2.resizeWindow(window_name, 1200, 800)
        print("Mode fenêtre maximisée activé")
        return True

import mediapipe as mp
import numpy as np

# Initialisation MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

class AirPainter:
    def __init__(self):
        self.hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        
        # Canvas pour dessiner
        self.canvas = None
        self.colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]
        self.current_color = 0
        self.drawing = False
        self.prev_x, self.prev_y = 0, 0
        
    def get_finger_tip_position(self, landmarks, width, height):
        """Obtient la position du bout de l'index"""
        index_tip = landmarks.landmark[8]
        x = int(index_tip.x * width)
        y = int(index_tip.y * height)
        return x, y
    
    def is_finger_up(self, landmarks):
        """Détecte si l'index est levé"""
        # Position de l'index (bout et articulation)
        index_tip = landmarks.landmark[8]
        index_pip = landmarks.landmark[6]
        
        # L'index est levé si le bout est plus haut que l'articulation
        return index_tip.y < index_pip.y
    
    def is_thumb_up(self, landmarks):
        """Détecte si le pouce est levé"""
        thumb_tip = landmarks.landmark[4]
        thumb_ip = landmarks.landmark[3]
        
        return thumb_tip.x > thumb_ip.x
    
    def run(self):
        cap = cv2.VideoCapture(0)
        
        print("🎨 Air Painter - Peinture Aérienne")
        print("Instructions:")
        print("- Levez l'index pour dessiner")
        print("- Fermez le poing pour arrêter")
        print("- Levez le pouce pour changer de couleur")
        print("- Appuyez sur 'c' pour effacer")
        print("- Appuyez sur 'q' pour quitter")
        print("\nDémarrage...")
        # Configuration de la fenêtre maximisée
        window_name = "Air Painter"
        setup_maximized_window(window_name)
        maximized_mode = True
        print("Mode fenêtre maximisée activé - Appuyez sur 'f' pour basculer")
        
        
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            # Miroir de l'image
            frame = cv2.flip(frame, 1)
            height, width, _ = frame.shape
            
            # Initialiser le canvas si nécessaire
            if self.canvas is None:
                self.canvas = np.zeros((height, width, 3), np.uint8)
            
            # Conversion RGB pour MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Dessiner les points de la main
                    mp_drawing.draw_landmarks(
                        frame, hand_landmarks, mp_hands.HAND_CONNECTIONS
                    )
                    
                    # Obtenir la position du bout de l'index
                    x, y = self.get_finger_tip_position(hand_landmarks, width, height)
                    
                    # Vérifier les gestes
                    if self.is_finger_up(hand_landmarks) and not self.is_thumb_up(hand_landmarks):
                        # Mode dessin
                        cv2.circle(frame, (x, y), 10, self.colors[self.current_color], -1)
                        
                        if self.drawing:
                            # Dessiner une ligne sur le canvas
                            cv2.line(self.canvas, (self.prev_x, self.prev_y), (x, y), 
                                   self.colors[self.current_color], 5)
                        
                        self.drawing = True
                        self.prev_x, self.prev_y = x, y
                        
                    elif self.is_thumb_up(hand_landmarks):
                        # Changer de couleur
                        self.current_color = (self.current_color + 1) % len(self.colors)
                        cv2.putText(frame, "Couleur changée!", (10, 100), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        self.drawing = False
                        
                    else:
                        # Arrêter le dessin
                        self.drawing = False
            
            # Combiner le frame avec le canvas
            combined = cv2.addWeighted(frame, 0.7, self.canvas, 0.3, 0)
            
            # Afficher les informations
            cv2.putText(combined, f"Couleur: {self.current_color + 1}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, self.colors[self.current_color], 2)
            cv2.putText(combined, "Index: Dessiner | Pouce: Couleur | 'c': Effacer", 
                       (10, height - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            cv2.imshow('Air Painter', combined)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                break
            elif key == ord('f'):
                maximized_mode = toggle_window_mode(window_name, maximized_mode)
            elif key == ord('c'):
                # Effacer le canvas
                self.canvas = np.zeros((height, width, 3), np.uint8)
                print("Canvas effacé!")
        
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    painter = AirPainter()
    painter.run()
