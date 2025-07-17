import cv2
import numpy as np
import time
import os

class FaceDetectionApp:
    def __init__(self):
        # Initialiser les classificateurs
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        self.smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')
        
        # Variables de suivi
        self.face_count = 0
        self.total_faces_detected = 0
        self.fps_counter = 0
        self.fps_time = time.time()
        self.current_fps = 0
        self.detection_history = []
        
        # Paramètres de détection
        self.scale_factor = 1.1
        self.min_neighbors = 5
        self.min_size = (30, 30)
        
        # Couleurs
        self.colors = {
            'face': (255, 0, 0),      # Bleu pour les visages
            'eye': (0, 255, 0),       # Vert pour les yeux
            'smile': (0, 255, 255),   # Jaune pour les sourires
            'text': (255, 255, 255),  # Blanc pour le texte
            'panel': (0, 0, 0)        # Noir pour le panneau
        }
    
    def detect_faces(self, frame):
        """Détecte les visages, yeux et sourires dans le frame."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Détecter les visages
        faces = self.face_cascade.detectMultiScale(
            gray, 
            scaleFactor=self.scale_factor,
            minNeighbors=self.min_neighbors,
            minSize=self.min_size
        )
        
        face_data = []
        
        for (x, y, w, h) in faces:
            # Région d'intérêt pour le visage
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = frame[y:y+h, x:x+w]
            
            # Détecter les yeux dans le visage
            eyes = self.eye_cascade.detectMultiScale(
                roi_gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(10, 10)
            )
            
            # Détecter les sourires dans le visage
            smiles = self.smile_cascade.detectMultiScale(
                roi_gray,
                scaleFactor=1.8,
                minNeighbors=20,
                minSize=(25, 25)
            )
            
            face_info = {
                'rect': (x, y, w, h),
                'eyes': eyes,
                'smiles': smiles,
                'center': (x + w//2, y + h//2),
                'area': w * h
            }
            
            face_data.append(face_info)
        
        return face_data
    
    def draw_detections(self, frame, face_data):
        """Dessine les détections sur le frame."""
        for face_info in face_data:
            x, y, w, h = face_info['rect']
            
            # Dessiner le rectangle du visage
            cv2.rectangle(frame, (x, y), (x+w, y+h), self.colors['face'], 2)
            
            # Ajouter un label pour le visage
            cv2.putText(frame, 'Visage', (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.colors['face'], 2)
            
            # Dessiner les yeux
            for (ex, ey, ew, eh) in face_info['eyes']:
                cv2.rectangle(frame, (x+ex, y+ey), (x+ex+ew, y+ey+eh), self.colors['eye'], 2)
                cv2.putText(frame, 'Oeil', (x+ex, y+ey-5), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, self.colors['eye'], 1)
            
            # Dessiner les sourires
            for (sx, sy, sw, sh) in face_info['smiles']:
                cv2.rectangle(frame, (x+sx, y+sy), (x+sx+sw, y+sy+sh), self.colors['smile'], 2)
                cv2.putText(frame, 'Sourire', (x+sx, y+sy-5), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, self.colors['smile'], 1)
            
            # Dessiner le centre du visage
            center = face_info['center']
            cv2.circle(frame, center, 5, self.colors['face'], -1)
            
            # Afficher les informations du visage
            info_text = f"Yeux: {len(face_info['eyes'])} | Sourires: {len(face_info['smiles'])}"
            cv2.putText(frame, info_text, (x, y+h+20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.colors['text'], 1)
    
    def draw_info_panel(self, frame, face_data):
        """Dessine un panneau d'information sur le frame."""
        panel_height = 140
        panel_width = 350
        
        # Créer un rectangle semi-transparent
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (panel_width, panel_height), self.colors['panel'], -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Ajouter les informations
        font = cv2.FONT_HERSHEY_SIMPLEX
        y_offset = 35
        
        cv2.putText(frame, f"Visages detectes: {len(face_data)}", (20, y_offset), 
                   font, 0.6, self.colors['text'], 2)
        y_offset += 25
        
        cv2.putText(frame, f"Total detecte: {self.total_faces_detected}", (20, y_offset), 
                   font, 0.6, self.colors['text'], 2)
        y_offset += 25
        
        cv2.putText(frame, f"FPS: {self.current_fps:.1f}", (20, y_offset), 
                   font, 0.6, self.colors['text'], 2)
        y_offset += 25
        
        # Afficher les détails des visages
        if face_data:
            largest_face = max(face_data, key=lambda f: f['area'])
            eyes_count = len(largest_face['eyes'])
            smiles_count = len(largest_face['smiles'])
            
            cv2.putText(frame, f"Plus grand visage - Yeux: {eyes_count}, Sourires: {smiles_count}", 
                       (20, y_offset), font, 0.5, self.colors['text'], 1)
            y_offset += 20
            
            cv2.putText(frame, f"Taille: {largest_face['rect'][2]}x{largest_face['rect'][3]}", 
                       (20, y_offset), font, 0.5, self.colors['text'], 1)
    
    def update_fps(self):
        """Met à jour le compteur FPS."""
        self.fps_counter += 1
        current_time = time.time()
        
        if current_time - self.fps_time >= 1.0:
            self.current_fps = self.fps_counter
            self.fps_counter = 0
            self.fps_time = current_time
    
    def save_detection(self, frame, face_data):
        """Sauvegarde une capture avec les détections."""
        timestamp = int(time.time())
        filename = f"face_detection_{timestamp}.jpg"
        
        # Créer un dossier pour les captures si nécessaire
        if not os.path.exists("captures"):
            os.makedirs("captures")
        
        filepath = os.path.join("captures", filename)
        cv2.imwrite(filepath, frame)
        
        print(f"Capture sauvegardée: {filepath}")
        print(f"Visages détectés: {len(face_data)}")
        
        return filepath
    
    def run(self):
        """Lance l'application de détection de visage."""
        print("=== Application de Détection de Visage ===")
        print("Initialisation de la caméra...")
        
        # Essayer différents backends et indices de caméra
        cap = self.initialize_camera()
        
        if cap is None:
            print("Erreur: Impossible d'ouvrir la caméra avec tous les backends testés")
            print("Vérifiez que:")
            print("- Une caméra est connectée et allumée")
            print("- Les pilotes de caméra sont installés")
            print("- Aucune autre application n'utilise la caméra")
            print("- Les permissions d'accès à la caméra sont accordées")
            return
        
        # Configurer la caméra
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        print("Caméra initialisée avec succès")
        print("Contrôles:")
        print("  - 'q' ou 'ESC' pour quitter")
        print("  - 's' pour sauvegarder une capture")
        print("  - 'r' pour réinitialiser les compteurs")
        print("  - '+' pour augmenter la sensibilité")
        print("  - '-' pour diminuer la sensibilité")
        print("  - 'f' pour basculer en mode fenêtre maximisée")
        
        # Créer la fenêtre et la configurer pour le fenêtre maximisée
        window_name = 'Detection de Visage - Computer Vision App'
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 1200, 800)
        
        maximized_mode = True
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Erreur lors de la lecture du frame")
                    break
                
                # Retourner horizontalement pour effet miroir
                frame = cv2.flip(frame, 1)
                
                # Détecter les visages
                face_data = self.detect_faces(frame)
                
                # Mettre à jour les statistiques
                if face_data:
                    self.total_faces_detected += len(face_data)
                    self.detection_history.append(len(face_data))
                    
                    # Garder seulement les 100 dernières détections
                    if len(self.detection_history) > 100:
                        self.detection_history.pop(0)
                
                # Dessiner les détections
                self.draw_detections(frame, face_data)
                
                # Mettre à jour le FPS
                self.update_fps()
                
                # Dessiner le panneau d'information
                self.draw_info_panel(frame, face_data)
                
                # Ajouter des instructions
                cv2.putText(frame, "Appuyez sur 'q' pour quitter", (frame.shape[1] - 250, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.colors['text'], 1)
                
                # Afficher le frame
                cv2.imshow('Detection de Visage - Computer Vision App', frame)
                
                # Gestion des touches
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q') or key == 27:  # 'q' ou ESC
                    print("Arrêt demandé par l'utilisateur")
                    break
                elif key == ord('s'):
                    self.save_detection(frame, face_data)
                elif key == ord('r'):
                    print("Réinitialisation des compteurs...")
                    self.total_faces_detected = 0
                    self.detection_history = []
                elif key == ord('+'):
                    self.min_neighbors = max(1, self.min_neighbors - 1)
                    print(f"Sensibilité augmentée (min_neighbors: {self.min_neighbors})")
                elif key == ord('-'):
                    self.min_neighbors = min(10, self.min_neighbors + 1)
                    print(f"Sensibilité diminuée (min_neighbors: {self.min_neighbors})")
                elif key == ord('f'):
                    # Basculer le mode fenêtre maximisée
                    maximized_mode = not maximized_mode
                    if maximized_mode:
                        cv2.resizeWindow(window_name, 1200, 800)
                        print("Mode fenêtre maximisée activé - Appuyez sur 'f' pour basculer")
                    else:
                        cv2.resizeWindow(window_name, 1200, 800)
                        print("Mode fenêtre normal activé")
                
        except KeyboardInterrupt:
            print("Arrêt demandé par Ctrl+C")
        except Exception as e:
            print(f"Erreur: {e}")
        finally:
            print("Nettoyage des ressources...")
            cap.release()
            cv2.destroyAllWindows()
            print("Application terminée")
            
            # Afficher les statistiques finales
            if self.detection_history:
                avg_faces = sum(self.detection_history) / len(self.detection_history)
                max_faces = max(self.detection_history)
                print(f"Statistiques finales:")
                print(f"  - Moyenne de visages par frame: {avg_faces:.2f}")
                print(f"  - Maximum de visages détectés: {max_faces}")
                print(f"  - Total de détections: {self.total_faces_detected}")

    def initialize_camera(self):
        """Essayer d'initialiser la caméra avec différents backends et indices."""
        print("Essai des différents backends et indices de caméra...")
        backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_V4L2, cv2.CAP_ANY]
        for backend in backends:
            for index in range(4):
                cap = cv2.VideoCapture(index, backend)
                if cap.isOpened():
                    ret, _ = cap.read()
                    if ret:
                        print(f"Caméra {index} ouverte avec succès avec backend {backend}")
                        return cap
                    cap.release()
                print(f"Caméra {index} échouée avec backend {backend}")
        
        return None

def main():
    print("Démarrage de l'application de détection de visage...")
    app = FaceDetectionApp()
    app.run()

if __name__ == "__main__":
    main()
