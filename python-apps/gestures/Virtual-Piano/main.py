import cv2
import mediapipe as mp
import numpy as np
import pygame
import math
import tkinter as tk
from tkinter import ttk
import threading
import time

class VirtualPiano:
    def __init__(self):
        # Configuration MediaPipe
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Configuration Pygame pour le son
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        # Configuration de la caméra
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        # Configuration du piano virtuel
        self.keys = {
            'C': {'pos': (100, 400), 'color': (255, 255, 255), 'freq': 261.63, 'pressed': False},
            'C#': {'pos': (150, 300), 'color': (50, 50, 50), 'freq': 277.18, 'pressed': False},
            'D': {'pos': (200, 400), 'color': (255, 255, 255), 'freq': 293.66, 'pressed': False},
            'D#': {'pos': (250, 300), 'color': (50, 50, 50), 'freq': 311.13, 'pressed': False},
            'E': {'pos': (300, 400), 'color': (255, 255, 255), 'freq': 329.63, 'pressed': False},
            'F': {'pos': (400, 400), 'color': (255, 255, 255), 'freq': 349.23, 'pressed': False},
            'F#': {'pos': (450, 300), 'color': (50, 50, 50), 'freq': 369.99, 'pressed': False},
            'G': {'pos': (500, 400), 'color': (255, 255, 255), 'freq': 392.00, 'pressed': False},
            'G#': {'pos': (550, 300), 'color': (50, 50, 50), 'freq': 415.30, 'pressed': False},
            'A': {'pos': (600, 400), 'color': (255, 255, 255), 'freq': 440.00, 'pressed': False},
            'A#': {'pos': (650, 300), 'color': (50, 50, 50), 'freq': 466.16, 'pressed': False},
            'B': {'pos': (700, 400), 'color': (255, 255, 255), 'freq': 493.88, 'pressed': False}
        }
        
        self.pressed_keys = set()
        self.last_press_time = {}
        self.recording = False
        self.recorded_notes = []
        self.playback_thread = None
        
        # Interface graphique
        self.setup_ui()
        
    def setup_ui(self):
        self.root = tk.Tk()
        self.root.title("Piano Virtuel - Contrôle Gestuel")
        self.root.geometry("300x200")
        
        # Style moderne
        style = ttk.Style()
        style.theme_use('clam')
        
        # Boutons de contrôle
        control_frame = ttk.Frame(self.root)
        control_frame.pack(pady=10)
        
        self.record_btn = ttk.Button(control_frame, text="🎵 Enregistrer", command=self.toggle_recording)
        self.record_btn.pack(side=tk.LEFT, padx=5)
        
        self.play_btn = ttk.Button(control_frame, text="▶️ Lecture", command=self.play_recording)
        self.play_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = ttk.Button(control_frame, text="🗑️ Effacer", command=self.clear_recording)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Indicateurs
        self.status_label = ttk.Label(self.root, text="Statut: Prêt", font=('Arial', 10))
        self.status_label.pack(pady=5)
        
        self.notes_label = ttk.Label(self.root, text="Notes enregistrées: 0", font=('Arial', 9))
        self.notes_label.pack(pady=2)
        
        # Instructions
        instructions = ttk.Label(self.root, text="Instructions:\n• Pointez du doigt pour jouer\n• Poing fermé pour silence\n• Enregistrez vos mélodies", 
                               font=('Arial', 9), justify=tk.LEFT)
        instructions.pack(pady=10)
        
    def generate_tone(self, frequency, duration=0.5, sample_rate=22050):
        """Génère un son de fréquence donnée"""
        frames = int(duration * sample_rate)
        arr = np.zeros(frames)
        
        for i in range(frames):
            arr[i] = np.sin(2 * np.pi * frequency * i / sample_rate)
        
        arr = (arr * 32767).astype(np.int16)
        stereo_arr = np.zeros((frames, 2), dtype=np.int16)
        stereo_arr[:, 0] = arr
        stereo_arr[:, 1] = arr
        
        return stereo_arr
    
    def play_note(self, note):
        """Joue une note"""
        if note in self.keys:
            freq = self.keys[note]['freq']
            tone = self.generate_tone(freq, 0.3)
            sound = pygame.sndarray.make_sound(tone)
            sound.play()
            
            if self.recording:
                self.recorded_notes.append((note, time.time()))
                self.notes_label.config(text=f"Notes enregistrées: {len(self.recorded_notes)}")
    
    def draw_piano(self, frame):
        """Dessine le piano virtuel"""
        # Dessiner les touches blanches
        for note, data in self.keys.items():
            if data['color'] == (255, 255, 255):  # Touches blanches
                x, y = data['pos']
                color = (100, 255, 100) if data['pressed'] else (255, 255, 255)
                cv2.rectangle(frame, (x-40, y-100), (x+40, y), color, -1)
                cv2.rectangle(frame, (x-40, y-100), (x+40, y), (0, 0, 0), 2)
                
                # Nom de la note
                cv2.putText(frame, note, (x-10, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        
        # Dessiner les touches noires
        for note, data in self.keys.items():
            if data['color'] == (50, 50, 50):  # Touches noires
                x, y = data['pos']
                color = (100, 255, 100) if data['pressed'] else (50, 50, 50)
                cv2.rectangle(frame, (x-25, y-80), (x+25, y-20), color, -1)
                cv2.rectangle(frame, (x-25, y-80), (x+25, y-20), (0, 0, 0), 2)
                
                # Nom de la note
                cv2.putText(frame, note, (x-15, y-40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    def detect_finger_position(self, landmarks, frame_width, frame_height):
        """Détecte la position du doigt pointé"""
        # Index finger tip
        index_tip = landmarks[8]
        x = int(index_tip.x * frame_width)
        y = int(index_tip.y * frame_height)
        
        # Vérifier quelle touche est touchée
        for note, data in self.keys.items():
            key_x, key_y = data['pos']
            if data['color'] == (255, 255, 255):  # Touches blanches
                if (key_x-40 <= x <= key_x+40) and (key_y-100 <= y <= key_y):
                    return note, (x, y)
            else:  # Touches noires
                if (key_x-25 <= x <= key_x+25) and (key_y-80 <= y <= key_y-20):
                    return note, (x, y)
        
        return None, (x, y)
    
    def is_pointing_gesture(self, landmarks):
        """Vérifie si le geste est un pointage"""
        # Vérifier si l'index est étendu et les autres doigts pliés
        index_tip = landmarks[8]
        index_pip = landmarks[6]
        middle_tip = landmarks[12]
        middle_pip = landmarks[10]
        
        # Index étendu
        index_extended = index_tip.y < index_pip.y
        # Majeur plié
        middle_folded = middle_tip.y > middle_pip.y
        
        return index_extended and middle_folded
    
    def toggle_recording(self):
        """Active/désactive l'enregistrement"""
        self.recording = not self.recording
        if self.recording:
            self.record_btn.config(text="⏹️ Arrêter")
            self.status_label.config(text="Statut: Enregistrement...")
            self.recorded_notes = []
        else:
            self.record_btn.config(text="🎵 Enregistrer")
            self.status_label.config(text="Statut: Prêt")
    
    def play_recording(self):
        """Lit l'enregistrement"""
        if not self.recorded_notes:
            self.status_label.config(text="Statut: Aucun enregistrement")
            return
        
        def play_thread():
            self.status_label.config(text="Statut: Lecture...")
            start_time = self.recorded_notes[0][1]
            
            for note, timestamp in self.recorded_notes:
                delay = timestamp - start_time
                if delay > 0:
                    time.sleep(min(delay, 2.0))  # Limite le délai
                
                self.play_note(note)
                start_time = timestamp
            
            self.status_label.config(text="Statut: Lecture terminée")
        
        if self.playback_thread is None or not self.playback_thread.is_alive():
            self.playback_thread = threading.Thread(target=play_thread)
            self.playback_thread.daemon = True
            self.playback_thread.start()
    
    def clear_recording(self):
        """Efface l'enregistrement"""
        self.recorded_notes = []
        self.notes_label.config(text="Notes enregistrées: 0")
        self.status_label.config(text="Statut: Enregistrement effacé")
    
    def run(self):
        """Boucle principale"""
        def camera_loop():
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    break
                
                # Inverser horizontalement pour effet miroir
                frame = cv2.flip(frame, 1)
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Détection des mains
                results = self.hands.process(frame_rgb)
                
                # Réinitialiser l'état des touches
                for key in self.keys:
                    self.keys[key]['pressed'] = False
                
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        # Dessiner les points de la main
                        self.mp_drawing.draw_landmarks(
                            frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                        )
                        
                        # Vérifier le geste de pointage
                        if self.is_pointing_gesture(hand_landmarks.landmark):
                            note, finger_pos = self.detect_finger_position(
                                hand_landmarks.landmark, frame.shape[1], frame.shape[0]
                            )
                            
                            if note:
                                self.keys[note]['pressed'] = True
                                current_time = time.time()
                                
                                # Éviter les répétitions trop rapides
                                if (note not in self.last_press_time or 
                                    current_time - self.last_press_time[note] > 0.2):
                                    self.play_note(note)
                                    self.last_press_time[note] = current_time
                            
                            # Dessiner le point de contact
                            cv2.circle(frame, finger_pos, 10, (0, 255, 0), -1)
                
                # Dessiner le piano
                self.draw_piano(frame)
                
                # Afficher le statut
                status_text = "🎵 ENREGISTREMENT" if self.recording else "🎹 PIANO VIRTUEL"
                cv2.putText(frame, status_text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # Instructions
                cv2.putText(frame, "Pointez du doigt pour jouer", (50, 600), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(frame, "Poing ferme pour silence", (50, 630), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                cv2.imshow('Piano Virtuel - Contrôle Gestuel', frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            self.cap.release()
            cv2.destroyAllWindows()
        
        # Lancer la caméra dans un thread séparé
        camera_thread = threading.Thread(target=camera_loop)
        camera_thread.daemon = True
        camera_thread.start()
        
        # Lancer l'interface graphique
        self.root.mainloop()

if __name__ == "__main__":
    app = VirtualPiano()
    app.run()
