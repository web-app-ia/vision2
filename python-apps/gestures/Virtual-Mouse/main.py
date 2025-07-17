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

import numpy as np
import time
import pyautogui
from mediapipe.python.solutions import hands as mp_hands
from mediapipe.python.solutions import drawing_utils as mp_drawing

class VirtualMouse:
    def __init__(self):
        self.hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)
        self.screen_width, self.screen_height = pyautogui.size()
        self.smoothening = 7
        self.prev_x, self.prev_y = 0, 0
        self.curr_x, self.curr_y = 0, 0

    def run(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Erreur: Impossible d'ouvrir la caméra.")
            return

        cap.set(3, 640)
        cap.set(4, 480)

        p_time = 0
        # Configuration de la fenêtre maximisée
        window_name = "Souris Virtuelle"
        setup_maximized_window(window_name)
        maximized_mode = True
        print("Mode fenêtre maximisée activé - Appuyez sur 'f' pour basculer")
        
        
        while True:
            success, img = cap.read()
            if not success:
                break

            img = cv2.flip(img, 1)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = self.hands.process(img_rgb)

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    self.process_hand(img, hand_landmarks)

            c_time = time.time()
            fps = 1 / (c_time - p_time)
            p_time = c_time
            cv2.putText(img, f'FPS: {int(fps)}', (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

            cv2.imshow("Souris Virtuelle", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    def process_hand(self, img, hand_landmarks):
        h, w, c = img.shape
        landmarks = hand_landmarks.landmark
        
        # Coordonnées du bout de l'index et du pouce
        x1, y1 = landmarks[8].x * w, landmarks[8].y * h  # Index
        x2, y2 = landmarks[4].x * w, landmarks[4].y * h  # Pouce

        # Mouvement du curseur
        x3 = np.interp(x1, (100, w - 100), (0, self.screen_width))
        y3 = np.interp(y1, (100, h - 100), (0, self.screen_height))
        
        self.curr_x = self.prev_x + (x3 - self.prev_x) / self.smoothening
        self.curr_y = self.prev_y + (y3 - self.prev_y) / self.smoothening

        pyautogui.moveTo(self.curr_x, self.curr_y)
        cv2.circle(img, (int(x1), int(y1)), 15, (255, 0, 255), cv2.FILLED)
        self.prev_x, self.prev_y = self.curr_x, self.curr_y

        # Détection du clic
        length = np.hypot(x2 - x1, y2 - y1)
        if length < 40:
            cv2.circle(img, (int(x1), int(y1)), 15, (0, 255, 0), cv2.FILLED)
            pyautogui.click()

        mp_drawing.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

if __name__ == "__main__":
    print("Lancement de la Souris Virtuelle...")
    print("Levez votre main et bougez l'index pour contrôler le curseur.")
    print("Pincez l'index et le pouce pour cliquer.")
    print("Appuyez sur 'q' dans la fenêtre de la caméra pour quitter.")
    virtual_mouse = VirtualMouse()
    virtual_mouse.run()