import cv2
import numpy as np
import time
import os

class FaceDetectionDemo:
    def __init__(self):
        # Initialiser les classificateurs
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        self.smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')
        
        # Variables de suivi
        self.total_faces_detected = 0
        self.current_fps = 30
        
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
    
    def create_demo_image(self, width=640, height=480):
        """Crée une image de démonstration avec des formes géométriques."""
        # Créer une image avec un dégradé
        image = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Dégradé bleu
        for y in range(height):
            color_value = int(255 * (y / height))
            image[y, :] = [color_value, color_value // 2, 100]
        
        # Ajouter du texte
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(image, "MODE DEMONSTRATION", (width//2 - 150, 50), 
                   font, 1, (255, 255, 255), 2)
        
        cv2.putText(image, "Pas de camera detectee", (width//2 - 120, 100), 
                   font, 0.7, (255, 255, 0), 2)
        
        cv2.putText(image, "Simulation de detection de visage", (width//2 - 180, 150), 
                   font, 0.6, (255, 255, 255), 1)
        
        # Ajouter des "visages" simulés (rectangles)
        face_positions = [(150, 200, 120, 150), (400, 250, 100, 130)]
        
        for (x, y, w, h) in face_positions:
            # Dessiner un rectangle pour simuler un visage
            cv2.rectangle(image, (x, y), (x+w, y+h), self.colors['face'], 2)
            cv2.putText(image, 'Visage Simule', (x, y-10), 
                       font, 0.5, self.colors['face'], 1)
            
            # Ajouter des "yeux" simulés
            eye_y = y + h//3
            cv2.rectangle(image, (x+w//4, eye_y), (x+w//4+20, eye_y+15), self.colors['eye'], 2)
            cv2.rectangle(image, (x+3*w//4-20, eye_y), (x+3*w//4, eye_y+15), self.colors['eye'], 2)
            
            # Ajouter un "sourire" simulé
            smile_y = y + 2*h//3
            cv2.rectangle(image, (x+w//3, smile_y), (x+2*w//3, smile_y+15), self.colors['smile'], 2)
        
        return image, len(face_positions)
    
    def draw_info_panel(self, frame, face_count):
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
        
        cv2.putText(frame, f"Visages detectes: {face_count}", (20, y_offset), 
                   font, 0.6, self.colors['text'], 2)
        y_offset += 25
        
        cv2.putText(frame, f"Total detecte: {self.total_faces_detected}", (20, y_offset), 
                   font, 0.6, self.colors['text'], 2)
        y_offset += 25
        
        cv2.putText(frame, f"FPS: {self.current_fps:.1f}", (20, y_offset), 
                   font, 0.6, self.colors['text'], 2)
        y_offset += 25
        
        cv2.putText(frame, "MODE DEMO - Pas de camera", (20, y_offset), 
                   font, 0.5, (0, 255, 255), 1)
    
    def run_demo(self):
        """Lance la démonstration."""
        print("=== MODE DEMONSTRATION - Détection de Visage ===")
        print("Aucune caméra détectée, lancement du mode démonstration")
        print("Contrôles:")
        print("  - 'q' ou 'ESC' pour quitter")
        print("  - 'r' pour réinitialiser les compteurs")
        print("  - ESPACE pour changer l'image de démonstration")
        
        demo_mode = 0
        
        try:
            while True:
                # Créer l'image de démonstration
                if demo_mode == 0:
                    frame, face_count = self.create_demo_image()
                else:
                    # Mode alternatif avec différentes positions
                    frame, face_count = self.create_demo_image()
                    # Modifier légèrement l'image pour simuler le mouvement
                    frame = cv2.flip(frame, 1)
                
                # Mettre à jour les statistiques
                self.total_faces_detected += face_count
                
                # Dessiner le panneau d'information
                self.draw_info_panel(frame, face_count)
                
                # Ajouter des instructions
                cv2.putText(frame, "Appuyez sur 'q' pour quitter | ESPACE pour changer", 
                           (frame.shape[1] - 400, frame.shape[0] - 20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, self.colors['text'], 1)
                
                # Afficher le frame
                cv2.imshow('Detection de Visage - MODE DEMO', frame)
                
                # Gestion des touches
                key = cv2.waitKey(100) & 0xFF  # Ralenti pour la démonstration
                
                if key == ord('q') or key == 27:  # 'q' ou ESC
                    print("Arrêt demandé par l'utilisateur")
                    break
                elif key == ord('r'):
                    print("Réinitialisation des compteurs...")
                    self.total_faces_detected = 0
                elif key == ord(' '):  # ESPACE
                    demo_mode = 1 - demo_mode
                    print(f"Changement vers le mode de démonstration {demo_mode + 1}")
                
        except KeyboardInterrupt:
            print("Arrêt demandé par Ctrl+C")
        except Exception as e:
            print(f"Erreur: {e}")
        finally:
            print("Nettoyage des ressources...")
            cv2.destroyAllWindows()
            print("Démonstration terminée")
            
            # Afficher les statistiques finales
            print(f"Statistiques de la démonstration:")
            print(f"  - Total de détections simulées: {self.total_faces_detected}")

def main():
    print("Démarrage de la démonstration de détection de visage...")
    demo = FaceDetectionDemo()
    demo.run_demo()

if __name__ == "__main__":
    main()
